import enum
import json
import uuid
from dataclasses import dataclass

from gql import gql

from graphql_client.graphql_client import get_client, Auth

PROGRAM_OFFERER_ROLE = "OFFERER"

SPECIAL_DIET_OPTIONS = {
    "special_diet.glutenfree": "glutenfree",
    "special_diet.milkfree": "milkfree",
    "special_diet.lactosefree": "lactosefree",
    "special_diet.vegan": "vegan",
    "special_diet.vegetarian": "vegetarian",
}


@dataclass(frozen=True)
class SpecialDiet:
    host_id: str
    diet_type: str
    diet_description: str


class ProgramHostClient:
    def __init__(self, endpoint: str, auth: Auth, event_slug: str):
        self.client = get_client(endpoint, auth)
        self.event_slug = event_slug

    @staticmethod
    def _get_special_diet_from_form_data(form_data: dict[str, str]) -> str:
        # The special diet selection can have two different forms
        diets = []

        if form_data.get("special_diet") is not None:
            diets.append(form_data.get("special_diet"))

        for diet in SPECIAL_DIET_OPTIONS.keys():
            if form_data.get(diet) is not None:
                diets.append(SPECIAL_DIET_OPTIONS[diet])

        return ", ".join(diets)

    def get_program_offerer_diets(self) -> list[SpecialDiet]:
        query = gql("""
            query GetProgramsWithHosts($event: String!) {
              event(slug: $event) {
                program {
                  programs {
                    slug
                    programOffer {
                      formData
                    }
                    programHosts {
                      programHostRole
                      person {
                        id
                      }
                    }
                  }
                }
              }
            }
        """)

        response = self.client.execute(
            query, variable_values={"event": self.event_slug}
        )

        print(f"Found {len(response['event']['program']['programs'])} programs")

        offerer_diets = []
        for program in response["event"]["program"]["programs"]:
            if program["programOffer"] is not None:
                form_data = json.loads(program["programOffer"]["formData"])
                special_diet = self._get_special_diet_from_form_data(form_data)
                other_special_diet = form_data.get("other_special_diet") or ""
                program_offerer_id = next(
                    (
                        host["person"]["id"]
                        for host in program.get("programHosts") or []
                        if host.get("programHostRole") == PROGRAM_OFFERER_ROLE
                        and host.get("person") is not None
                    ),
                    str(uuid.uuid4()),  # If no offerer is found, just use a random id
                )

                offerer_diets.append(
                    SpecialDiet(program_offerer_id, special_diet, other_special_diet)
                )

        return offerer_diets

    def get_program_helper_diets(self, survey_slug: str) -> list[SpecialDiet]:
        query = gql("""
          query ProgramHostInviteResponse($eventSlug: String!, $surveySlug: String!) {
            event(slug: $eventSlug) {
              forms {
                survey(slug: $surveySlug, app: PROGRAM_V2, purpose: INVITE) {
                  responses {
                    id
                    values
                    originalCreatedBy {
                      id
                      displayName
                    }
                  }
                }
              }
            }
          }
        """)

        variables = {
            "eventSlug": self.event_slug,
            "surveySlug": survey_slug,
        }

        response = self.client.execute(query, variable_values=variables)
        responses = response["event"]["forms"]["survey"]["responses"]
        print(f"Found {len(responses)} responses for survey {survey_slug}")

        helper_diets = []
        for survey_response in responses:
            values = survey_response["values"]
            if isinstance(values, str):
                values = json.loads(values)

            special_diet = values.get("special_diet") or [""]
            other_special_diet = values.get("other_special_diet") or ""
            helper_diets.append(
                SpecialDiet(
                    survey_response["originalCreatedBy"]["id"],
                    ", ".join(special_diet),
                    other_special_diet,
                )
            )

        return helper_diets
