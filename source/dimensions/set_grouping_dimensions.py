import argparse
import os

from dotenv import load_dotenv

from dimensions.program_client import ProgramClient
from graphql_client.graphql_client import Auth


def set_grouping_dimensions():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-l",
        "--limit",
        help="set dimensions only for the first LIMIT programs found. Use to test that all works as expected",
        type=int,
    )
    args = arg_parser.parse_args()
    limit = args.limit

    load_dotenv()
    client = ProgramClient(
        os.environ["KOMPASSI_GRAPHQL_URL"],
        Auth(os.environ["CSRF_TOKEN"], os.environ["SESSION_ID"]),
        os.environ["EVENT_SLUG"],
    )
    programs_to_edit = client.get_programs_to_edit_grouping()

    print(f"Found {len(programs_to_edit)} programs to edit.")

    if limit is not None:
        programs_to_edit = programs_to_edit[:limit]
        print(f"NOTE: editing only {limit} programs")

    print("Starting set_grouping_dimensions...")
    for program in programs_to_edit:
        print(f"Setting dimensions for program {program.program_id}")
        client.set_correct_grouping_dimension_value(program)
    print("Done!")


if __name__ == "__main__":
    set_grouping_dimensions()
