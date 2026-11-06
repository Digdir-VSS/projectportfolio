import asyncio
from msgraph import GraphServiceClient
from dotenv import load_dotenv

from models.azure_auth import GRAPH_SCOPE, get_azure_credential

load_dotenv()

async def _fetch_all_users() -> dict:
    client = GraphServiceClient(credentials=get_azure_credential(), scopes=[GRAPH_SCOPE])

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

