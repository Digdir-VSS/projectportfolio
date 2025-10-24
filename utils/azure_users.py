import asyncio
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv
load_dotenv()

async def _fetch_all_users() -> dict:
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url=os.getenv("KEY_VAULT_URL"), credential=credential
    )
    # async def list_gr
    CLIENT_SECRET = os.environ.get("FABRIC_SECRET")
    CLIENT_ID = os.environ.get("FABRIC_CLIENT_ID")
    TENANT_ID = os.environ.get("TENANT_ID")
    credentials = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    scopes = ['https://graph.microsoft.com/.default']
    client = GraphServiceClient(credentials=credentials, scopes=scopes)

    users = []
    page = await client.users.get()
    brukere = {}
    while page:
        if page.value:
            users.extend(page.value)

            for user in page.value:
                if user.job_title and user.job_title != "Eksterne":
                    brukere[user.display_name] = user.mail

        if page.odata_next_link:
            page = await client.users.with_url(page.odata_next_link).get()
        else:
            break
    return brukere

def load_users() -> dict:
    """Synchronous wrapper to get all Azure AD users as a dictionary."""
    return asyncio.run(_fetch_all_users())

