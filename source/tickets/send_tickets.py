import argparse
import os

from dotenv import load_dotenv

from graphql_client.graphql_client import Auth
from tickets.read_excel import read_excel
from tickets.tickets_client import TicketsClient


def send_tickets():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("excel_path", help="absolute path to excel file")
    arg_parser.add_argument(
        "-n",
        "--not-paid",
        action="store_true",
        help="if set, don't mark orders as paid",
    )
    args = arg_parser.parse_args()
    excel_path = args.excel_path
    set_not_paid = args.not_paid

    load_dotenv()
    event_slug = os.environ["EVENT_SLUG"]
    url = os.environ["KOMPASSI_GRAPHQL_URL"]
    auth = Auth(os.environ["CSRF_TOKEN"], os.environ["SESSION_ID"])

    print("Opening ticket order file")
    to_send = read_excel(excel_path)
    print(f"Found {len(to_send)} tickets to send")

    tickets_client = TicketsClient(url, auth, event_slug)
    print("Sending orders")
    order_ids = []
    for order in to_send:
        created_order = tickets_client.send_order(order)
        if created_order is not None:
            print(
                f"Sent order {created_order.id}, order number {created_order.number} to email {order.email}"
            )
            order_ids.append(created_order.id)

    print(f"Sent {len(order_ids)} orders")

    if set_not_paid:
        print("Not setting orders paid, done")
        return
    else:
        print("Next setting orders paid")
        for order_id in order_ids:
            tickets_client.mark_order_paid(order_id)
            print(f"Marked order {order_id} as paid")


if __name__ == "__main__":
    send_tickets()
