import argparse
import csv
import os
from pathlib import Path

from dotenv import load_dotenv

from graphql_client.graphql_client import Auth
from program_helpers.program_client import (
    ProgramClient,
    ProgramWithError,
)


def _write_error_data(data: list[ProgramWithError]) -> None:
    output_dir = Path(__file__).resolve().parents[2] / "tmpdata"
    output_path = output_dir / "failed.csv"

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["program_id", "input"])
        writer.writeheader()
        writer.writerows(
            {"program_id": item.program_id, "input": item.input} for item in data
        )

    print(f"Wrote invite error data to {output_path}")


def send_program_helper_invites():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-d",
        help="if set, do a dry run: don't actually send any invites",
        action="store_true",
    )
    args = arg_parser.parse_args()

    is_dry_run = args.d

    load_dotenv()
    event_slug = os.environ["EVENT_SLUG"]
    url = os.environ["KOMPASSI_GRAPHQUL_URL"]
    auth = Auth(os.environ["CSRF_TOKEN"], os.environ["SESSION_ID"])
    form_slug = os.environ["INVITE_FORM_SLUG"]

    program_client = ProgramClient(url, auth, event_slug)
    print("Read in data from Kompassi...")
    invite_data = program_client.get_program_needing_invites()

    if len(invite_data.failed) > 0:
        _write_error_data(invite_data.failed)

    for program in invite_data.to_invite:
        for email_address in program.emails:
            print(f"Sending invite to {email_address} for program {program.program_id}")
            program_client.send_program_invite(
                form_slug,
                program.program_id,
                email_address,
                program.language_code,
                is_dry_run,
            )

    print("Done!")


if __name__ == "__main__":
    send_program_helper_invites()
