import argparse
import os

from dotenv import load_dotenv

from graphql_client.graphql_client import Auth
from special_diets.program_host_client import ProgramHostClient, SpecialDiet
from special_diets.write_excel import write_excel


def list_special_diets() -> list[SpecialDiet]:
    client = ProgramHostClient(
        os.environ["KOMPASSI_GRAPHQL_URL"],
        Auth(os.environ["CSRF_TOKEN"], os.environ["SESSION_ID"]),
        os.environ["EVENT_SLUG"],
    )
    offerer_diets = client.get_program_offerer_diets()
    helper_diets = client.get_program_helper_diets(os.environ["INVITE_FORM_SLUG"])

    print(
        f"Found {len(offerer_diets)} offerer diets and {len(helper_diets)} helper diets"
    )
    unique_ids = set([host.host_id for host in offerer_diets + helper_diets])
    print(f"Unique ids: {len(set(unique_ids))}")

    special_diets_by_host_id = {}

    for special_diet in offerer_diets + helper_diets:
        special_diets_by_host_id.setdefault(special_diet.host_id, special_diet)

    return list(special_diets_by_host_id.values())


def main() -> None:
    load_dotenv()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("excel_path", help="path to the output Excel file")
    args = arg_parser.parse_args()

    write_excel(list_special_diets(), args.excel_path)


if __name__ == "__main__":
    main()
