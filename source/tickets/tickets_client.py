from dataclasses import dataclass

from gql import gql

from graphql_client.graphql_client import Auth, get_client
from tickets.read_excel import TicketOrder


@dataclass(frozen=True)
class CreatedOrder:
    id: str
    number: str


class TicketsClient:
    def __init__(self, endpoint: str, auth: Auth, event_slug: str):
        self.client = get_client(endpoint, auth)
        self.event_slug = event_slug

    def send_order(self, order: TicketOrder) -> CreatedOrder | None:
        """Send a ticket order, return id of the created order"""
        mutation = gql("""
            mutation CreateOrder($input: CreateOrderInput!) {
                createOrder(input: $input) {
                    order {
                        id
                        orderNumber
                    }
                }
            }
        """)

        variables = {
            "input": {
                "eventSlug": self.event_slug,
                "customer": {
                    "firstName": order.first_name,
                    "lastName": order.last_name,
                    "email": order.email,
                },
                "language": order.language_code,
                "products": [
                    {
                        "productId": order.ticket_product_id,
                        "quantity": order.number_of_tickets,
                    }
                ],
            }
        }

        try:
            result = self.client.execute(mutation, variable_values=variables)
        except Exception as e:
            print(f"Failed for email: {order.email}, error: {e}")
            return None

        if result.get("errors"):
            first_error = result["errors"][0]["message"]
            print(f"Failed for email: {order.email}, error: {first_error}")
            return None
        else:
            return CreatedOrder(
                result["createOrder"]["order"]["id"],
                result["createOrder"]["order"]["orderNumber"],
            )

    def mark_order_paid(self, order_id: str) -> None:
        mutation = gql("""
            mutation MarkOrderAsPaid($input: MarkOrderAsPaidInput!) {
                markOrderAsPaid(input: $input) {
                    order {
                        id
                    }
                }
            }
        """)

        variables = {
            "input": {
                "eventSlug": self.event_slug,
                "orderId": order_id,
            }
        }

        result = self.client.execute(mutation, variable_values=variables)

        if result.get("errors"):
            first_error = result["errors"][0]["message"]
            print(f"Failed marking paid for order: {order_id}, error: {first_error}")
        else:
            print(f"Marked order paid for order: {order_id}")
