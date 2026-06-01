import json
from dataclasses import dataclass
from typing import Any

from gql import gql

from graphql_client.graphql_client import get_client, Auth

GROUPING_VALUES = ["grouping.dreams", "grouping.lgbt", "grouping.beginners"]


@dataclass(frozen=True)
class ProgramToEdit:
    program_id: str
    values_to_set: list[str]
    existing_dimensions: list[Any]


class ProgramClient:
    def __init__(self, endpoint: str, auth: Auth, event_slug: str):
        self.client = get_client(endpoint, auth)
        self.event_slug = event_slug

    def get_programs_to_edit(self) -> list[ProgramToEdit]:
        query = gql("""
                  query GetProgramsNeedingInvites($event: String!) {
                    event(slug: $event) {
                      program {
                        programs(publicOnly: false) {
                          slug
                          programOffer {
                            formData
                          }
                          dimensions {
                            dimension {
                              slug
                              isMultiValue
                            }
                            value {
                              slug
                            }
                          }
                        }
                      }
                    }
                  }      
                """)

        variables = {"event": self.event_slug}

        result = self.client.execute(query, variable_values=variables)

        programs_to_edit = []
        for program in result["event"]["program"]["programs"]:
            if program.get("programOffer") is not None:
                form_data = json.loads(program["programOffer"]["formData"])
                grouping_values = [
                    key for key in GROUPING_VALUES if form_data.get(key) is not None
                ]
                if grouping_values:
                    programs_to_edit.append(
                        ProgramToEdit(
                            program["slug"],
                            grouping_values,
                            program.get("dimensions") or [],
                        )
                    )

        return programs_to_edit

    def set_correct_dimension_value(self, program_to_edit: ProgramToEdit) -> None:
        mutation = gql("""
            mutation SetGroupingDimensionValue($input: UpdateProgramDimensionsInput!) {
                updateProgramDimensions(input: $input) {
                    program {
                        slug
                    }
                }
            }
        """)

        dimensions_to_set = dict([(key, "on") for key in program_to_edit.values_to_set])

        for dimension in program_to_edit.existing_dimensions:
            if dimension["dimension"]["isMultiValue"] is True:
                dimensions_to_set[
                    f"{dimension['dimension']['slug']}.{dimension['value']['slug']}"
                ] = "on"
            else:
                dimensions_to_set[f"{dimension['dimension']['slug']}"] = dimension[
                    "value"
                ]["slug"]

        variables = {
            "input": {
                "eventSlug": self.event_slug,
                "programSlug": program_to_edit.program_id,
                "formData": dimensions_to_set,
            }
        }

        result = self.client.execute(mutation, variable_values=variables)

        if result.get("errors"):
            print(
                f"Error for program item {program_to_edit.program_id}: ${result['errors'][0]['message']}"
            )
