from typing import Any

from gql import gql

from graphql_client.graphql_client import Auth, get_client


class InvolvementClient:
    def __init__(self, endpoint: str, auth: Auth, event_slug: str):
        self.client = get_client(endpoint, auth)
        self.event_slug = event_slug

    def get_all_involvements(self) -> dict[str, Any]:
        query = gql("""
            query GetInvolvements {
              event(slug: "ropecon2026") {
                involvement {
                  id
                  people {
                    email
                    id
                    involvements {
                      id
                      type
                      cachedDimensions
                      cachedAnnotations
                    }
                  }
                }
              }
            }
       """)

        result = self.client.execute(query)
        return result["event"]["involvement"]["people"]

    def update_involvement(self, involvement_id: int, form_data: dict[str, Any]):
        mutation = gql("""
         mutation
           UpdateInvolvementPerks($input: UpdateInvolvementPerksInput!) {
             updateInvolvementPerks(input: $input) {
              involvement
           {
              id
            }
          }
        }
       """)

        variables = {
            "input": {
                "eventSlug": self.event_slug,
                "involvementId": involvement_id,
                "formData": form_data,
            }
        }

        result = self.client.execute(mutation, variable_values=variables)

        if result.get("errors"):
            print(
                f"Error for involvement {involvement_id}: ${result['errors'][0]['message']}"
            )
