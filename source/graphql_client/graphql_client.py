from dataclasses import dataclass

from gql import Client
from gql.transport.requests import RequestsHTTPTransport


@dataclass(frozen=True)
class Auth:
    csrf_token: str
    session_id: str


def get_client(endpoint: str, auth: Auth) -> Client:
    transport = RequestsHTTPTransport(
        url=endpoint,
        headers={
            "Cookie": f"csrftoken={auth.csrf_token};sessionid={auth.session_id}",
        },
        verify=True,
    )
    return Client(transport=transport, fetch_schema_from_transport=False)
