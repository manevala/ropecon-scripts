import json
from dataclasses import dataclass
import email.utils

from gql import gql

from graphql_client.graphql_client import Auth, get_client

PROGRAM_HELPERS_FIELD = "program_helpers"


@dataclass
class ProgramWithEmails:
    program_id: str
    language_code: str
    emails: list[str]


@dataclass
class ProgramWithError:
    program_id: str
    input: str


@dataclass
class ToInviteResponse:
    to_invite: list[ProgramWithEmails]
    failed: list[ProgramWithError]


class ProgramClient:
    def __init__(self, endpoint: str, auth: Auth, event_slug: str):
        self.client = get_client(endpoint, auth)
        self.event_slug = event_slug

    def get_program_needing_invites(self) -> ToInviteResponse:
        query = gql("""
          query GetProgramsNeedingInvites($event: String!) {
            event(slug: $event) {
              program {
                programs {
                  slug
                  isCancelled
                  invitations {
                    id
                  }
                  programOffer {
                    formData
                    language
                  }
                }
              }
            }
          }      
        """)

        variables = {"event": self.event_slug}

        result = self.client.execute(query, variable_values=variables)

        program_data = result["event"]["program"]["programs"]

        needs_invite = []
        entries_with_errors = []
        for program in program_data:
            program_id = program["slug"]

            if len(program["invitations"]) != 0:
                print(f"Program {program_id} already has invites, ignoring")
                continue
            if program["isCancelled"]:
                print(f"Program {program_id} has been cancelled, ignoring")
                continue

            program_offer = program.get("programOffer")
            if program_offer is None:
                print(f"No offer found for program {program_id}, ignoring")
                continue

            emails_maybe = self._parse_emails_from_form_data(
                program_offer["formData"], program_id
            )
            if emails_maybe[0] is None:
                print(
                    f"Malformed emails field for program {program_id}, adding to errors list"
                )
                entries_with_errors.append(
                    ProgramWithError(program_id, str(emails_maybe[1]))
                )
            elif len(emails_maybe[0]) == 0:
                print(f"No helper emails found for program {program_id}, ignoring")
            else:
                print(f"Found emails for program {program_id} adding to send list")
                needs_invite.append(
                    ProgramWithEmails(
                        program_id, program_offer["language"], emails_maybe[0]
                    )
                )

        print(
            f"Found {len(program_data)} programs, invites to send to {len(needs_invite)} programs, erroneous input for {len(entries_with_errors)} programs"
        )

        return ToInviteResponse(needs_invite, entries_with_errors)

    def send_program_invite(
        self,
        survey_slug: str,
        program_id: str,
        email_address: str,
        language_code: str,
        is_dry_run: bool,
    ):
        mutation = gql("""
          mutation MyMutation($input: InviteProgramHostInput!) {
            inviteProgramHost(input: $input) {
              invitation {
                id
              }
            }
          }
        """)

        variables = {
            "input": {
                "eventSlug": self.event_slug,
                "programSlug": program_id,
                "formData": {
                    "email": email_address,
                    "surveySlug": survey_slug,
                    "language": language_code,
                },
            }
        }

        if is_dry_run:
            print(f"Dry run, not sending invite for {program_id}")
        else:
            try:
                self.client.execute(mutation, variable_values=variables)
            except Exception as e:
                print(
                    f"ERROR: Failed to send invite for program {program_id}, error: {e}"
                )

    @staticmethod
    def _is_more_or_less_valid_email(address_maybe: str) -> bool:
        return "@" in email.utils.parseaddr(address_maybe)[1]

    def _parse_emails_from_form_data(
        self, form_data: str, program_id: str
    ) -> tuple[list[str] | None, str | None]:
        data = json.loads(form_data)
        helpers_input = data.get(PROGRAM_HELPERS_FIELD)
        if helpers_input is None:
            print(
                f"No input field with program helpers found in offer for program {program_id}"
            )
            return [], None
        helpers = [h.strip() for h in helpers_input.split(",") if h]
        if all([self._is_more_or_less_valid_email(h) for h in helpers]):
            return helpers, None
        else:
            return None, helpers_input
