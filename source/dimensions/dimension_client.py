from dataclasses import dataclass

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from graphql_client.graphql_client import Auth, get_client


@dataclass(frozen=True)
class DimensionData:
    can_add_values: bool
    can_remove: bool
    is_key_dimension: bool
    is_list_filter: bool
    is_multi_value: bool
    is_negative_selection: bool
    is_public: bool
    is_shown_in_detail: bool
    is_shown_to_subject: bool
    is_technical: bool
    title_en: str
    title_fi: str
    # Possible values: MANUAL,TITLE,SLUG
    value_ordering: str


@dataclass(frozen=True)
class DimensionValue:
    title_en: str
    title_fi: str


class AddDimensionValueError(Exception):
    pass


class DimensionClient:
    def __init__(
        self,
        endpoint: str,
        auth: Auth,
    ):
        self.client = get_client(endpoint, auth)

    def create_dimension(
        self,
        scope: str,
        universe: str,
        dimension_slug: str,
        dimension_data: DimensionData,
    ) -> str:
        mutation = gql("""
            mutation AddDimension($input: PutDimensionInput!) {
                putDimension(input: $input) {
                    dimension {
                        slug
                    }
                }
            }
        """)

        variables = {
            "input": {
                "scopeSlug": scope,
                "dimensionSlug": dimension_slug,
                "universeSlug": universe,
                "formData": dimension_data,
            }
        }

        result = self.client.execute(mutation, variable_values=variables)

        if result.get("errors"):
            first_error = result["errors"][0]["message"]
            return f"Error: {first_error}"
        else:
            return "OK"

    def add_dimension_value(
        self,
        scope: str,
        universe: str,
        dimension_slug: str,
        value_slug: str,
        value_data: DimensionValue,
    ) -> None:
        mutation = gql("""
            mutation AddDimensionValue($input: PutDimensionValueInput!) {
                putDimensionValue(input: $input) {
                    value {
                        slug
                    }
                }
            }
        """)

        variables = {
            "input": {
                "scopeSlug": scope,
                "dimensionSlug": dimension_slug,
                "universeSlug": universe,
                "valueSlug": value_slug,
                "formData": {
                    "title_en": value_data.title_en,
                    "title_fi": value_data.title_fi,
                },
            }
        }

        result = self.client.execute(mutation, variable_values=variables)

        if result.get("errors"):
            raise AddDimensionValueError(result["errors"][0]["message"])
