# Add a program dimension to Kompassi with values. The input file should follow this format:

# first-value-slug;English title for first value;Finnish title for first value
# second-value-slug;English title for second value;Finnish title for second value
# ...
#
# The dimension definition should be in a JSON file, see the data folder for an example.

import argparse
import csv
import json
import os
from dotenv import load_dotenv

from dimensions.dimension_client import (
    Auth,
    DimensionClient,
    DimensionValue,
    AddDimensionValueError,
)


def add_dimension():
    # Parse command-line arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("dimension_slug", help="slug of dimension to create")
    arg_parser.add_argument(
        "path_to_definition_file",
        help="absolute path to file with dimension definitions",
    )
    arg_parser.add_argument(
        "path_to_values_file",
        help="absolute path to semicolon-separated dimension value CSV file",
    )
    args = arg_parser.parse_args()

    slug = args.dimension_slug
    path_to_definition_file = args.path_to_definition_file
    path_to_values_file = args.path_to_values_file

    with open(path_to_definition_file) as f:
        definition = json.load(f)

    with open(path_to_values_file) as f:
        reader = csv.DictReader(
            f, fieldnames=["slug", "title_finnish", "title_english"], delimiter=";"
        )
        values = [row for row in reader]

    # Get environment file
    load_dotenv()
    url = os.environ["KOMPASSI_GRAPHQUL_URL"]
    event_slug = os.environ["EVENT_SLUG"]
    auth = Auth(os.environ["CSRF_TOKEN"], os.environ["SESSION_ID"])

    client = DimensionClient(url, auth)

    # Create dimension
    print(f"Creating dimension {slug}")
    print(f"Writing to {url} for event {event_slug}")

    res = client.create_dimension(event_slug, "program", slug, definition)
    print(f"Got the following result from creation: {res}")

    print(f"Adding {len(values)} dimension values")

    failed_slugs = []
    for value in values:
        try:
            print(f'Adding dimension {value["slug"]}')
            dimension_value = DimensionValue(
                value["title_english"], value["title_finnish"]
            )

            client.add_dimension_value(
                event_slug, "program", slug, value["slug"], dimension_value
            )
            print("Added successfully")
        except AddDimensionValueError as e:
            print(f"Error adding dimension {value['slug']}: {e}")
            failed_slugs.append(value["slug"])

    if len(failed_slugs) > 0:
        print(
            f"Failed to add {len(failed_slugs)} dimension values: {', '.join(failed_slugs)}"
        )


if __name__ == "__main__":
    add_dimension()
