"""Which Azure identity the app uses for the database and Microsoft Graph.

AZURE_SQL_AUTH selects it, with the same name and values as in the ERP project:

  "token"  The service principal, from FABRIC_CLIENT_ID, FABRIC_SECRET and
           TENANT_ID. This is the default, so the container apps run as before
           without any new configuration.
  "cli"    Whoever is logged in with `az login`, for local development. No client
           secret is needed on the developer's machine.
"""
import os
import threading
import time

from azure.core.credentials import AccessToken, TokenCredential
from azure.identity import AzureCliCredential, ClientSecretCredential

SQL_SCOPE = "https://database.windows.net/.default"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"

# Refresh this long before expiry, so a connection never opens with a dying token
REFRESH_MARGIN_SECONDS = 300


def get_azure_credential() -> TokenCredential:
    auth_mode = os.getenv("AZURE_SQL_AUTH", "token").lower()
    if auth_mode == "cli":
        return AzureCliCredential()
    if auth_mode != "token":
        raise ValueError(f"AZURE_SQL_AUTH must be 'token' or 'cli', not '{auth_mode}'")

    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("FABRIC_CLIENT_ID")
    client_secret = os.getenv("FABRIC_SECRET")
    if not (tenant_id and client_id and client_secret):
        raise ValueError(
            "TENANT_ID, FABRIC_CLIENT_ID and FABRIC_SECRET must be set. "
            "For local development, run `az login` and set AZURE_SQL_AUTH=cli."
        )
    return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)


class CachedToken:
    """Reuses one token until it nears expiry.

    AzureCliCredential does not cache, so without this every new database
    connection would start an `az` process.
    """

    def __init__(self, credential: TokenCredential, scope: str):
        self._credential = credential
        self._scope = scope
        self._lock = threading.Lock()
        self._token: AccessToken | None = None

    def get(self) -> str:
        with self._lock:
            if self._token is None or time.time() >= self._token.expires_on - REFRESH_MARGIN_SECONDS:
                print("🔑 Requesting new Entra ID token...")
                self._token = self._credential.get_token(self._scope)
            return self._token.token
