import argparse
import os

from dotenv import load_dotenv

from graphql_client.graphql_client import Auth
from perks import involvement_client
from perks.handle_involvements import filter_involvements, perk_to_form_data
from perks.read_excel import read_excel


def set_perks():
    load_dotenv()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("path_to_perk_file", help="Absolute path to perk file")
    args = arg_parser.parse_args()
    path_to_file = args.path_to_perk_file

    client = involvement_client.InvolvementClient(
        os.environ["KOMPASSI_GRAPHQL_URL"],
        Auth(os.environ["CSRF_TOKEN"], os.environ["SESSION_ID"]),
        os.environ["EVENT_SLUG"],
    )

    perk_list = read_excel(path_to_file)
    all_involvements = client.get_all_involvements()

    filtered_involvements = filter_involvements(all_involvements, perk_list)
    perks_to_set = perk_to_form_data(filtered_involvements)

    for perk in perks_to_set:
        client.update_involvement(perk.involvement_id, perk.form_data)


if __name__ == "__main__":
    set_perks()
