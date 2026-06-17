import copy
import json
from dataclasses import dataclass
from typing import Any

from gql import gql

from graphql_client.graphql_client import get_client, Auth

GROUPING_VALUES = ["grouping.dreams", "grouping.lgbt", "grouping.beginners"]
REGISTRATION_KEY = "registration"
# Form fields use underscore in Ropecon 2026, but the dimension slugs use hyphen.
REGISTRATION_VALUES = [
    "experience_point",
    "gamepoint",
    "konsti",
    "other",
    "not_required",
    "ropelarp",
]


@dataclass(frozen=True)
class ProgramToEdit:
    program_id: str
    values_to_set: list[str]
    existing_dimensions: list[Any]


class ProgramClient:
    def __init__(self, endpoint: str, auth: Auth, event_slug: str):
        self.client = get_client(endpoint, auth)
        self.event_slug = event_slug

    def _get_programs(self) -> dict[str, Any]:
        query = gql("""
                   query GetPrograms($event: String!) {
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
        return self.client.execute(query, variable_values=variables)

    def get_programs_to_edit_grouping(self) -> list[ProgramToEdit]:
        result = self._get_programs()

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

    def get_programs_to_edit_registration(self) -> list[ProgramToEdit]:
        result = self._get_programs()

        programs_to_edit = []
        for program in result["event"]["program"]["programs"]:
            if program.get("programOffer") is not None:
                form_data = json.loads(program["programOffer"]["formData"])
                registration_value = form_data.get(REGISTRATION_KEY)
                if registration_value is not None:
                    programs_to_edit.append(
                        ProgramToEdit(
                            program["slug"],
                            [registration_value],
                            program.get("dimensions") or [],
                        )
                    )

        return programs_to_edit

    def _set_dimension_values(
        self, program_to_edit: ProgramToEdit, base_dimension: dict[str, str]
    ) -> None:
        dimensions_to_set = copy.deepcopy(base_dimension)

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

        mutation = gql("""
                          mutation SetDimensionValue($input: UpdateProgramDimensionsInput!) {
                              updateProgramDimensions(input: $input) {
                                  program {
                                      slug
                                  }
                              }
                          }
                      """)

        result = self.client.execute(mutation, variable_values=variables)

        if result.get("errors"):
            print(
                f"Error for program item {program_to_edit.program_id}: ${result['errors'][0]['message']}"
            )

    def set_correct_grouping_dimension_value(
        self, program_to_edit: ProgramToEdit
    ) -> None:
        dimension = dict([(key, "on") for key in program_to_edit.values_to_set])
        self._set_dimension_values(program_to_edit, dimension)

    def set_correct_registration_dimension_value(
        self, program_to_edit: ProgramToEdit
    ) -> None:
        dimensions = {
            REGISTRATION_KEY: program_to_edit.values_to_set[0].replace("_", "-")
        }
        self._set_dimension_values(program_to_edit, dimensions)
