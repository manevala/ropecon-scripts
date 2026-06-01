import os

from dotenv import load_dotenv

from dimensions import program_client
from dimensions.program_client import ProgramClient
from graphql_client.graphql_client import Auth


def set_grouping_dimensions():
    load_dotenv()
    client = ProgramClient(
        os.environ["KOMPASSI_GRAPHQUL_URL"],
        Auth(os.environ["CSRF_TOKEN"], os.environ["SESSION_ID"]),
        os.environ["EVENT_SLUG"],
    )
    programs_to_edit = client.get_programs_to_edit()

    print(f"Found {len(programs_to_edit)} programs to edit.")

    print("Starting set_grouping_dimensions...")
    for program in programs_to_edit:
        client.set_correct_dimension_value(program)
    print("Done!")


if __name__ == "__main__":
    set_grouping_dimensions()
