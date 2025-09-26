from nicegui import ui, app, Client
from typing import Any
from cachetools import TTLCache
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication
from sqlalchemy.orm import Session

from utils.db_functions import diff_projects, apply_changes
from utils.project_loader import get_project_data, ProjectData  # your Pydantic model
from pages.login_page import register_login_pages
from pages.utils import layout, validate_token
import uuid
load_dotenv()

# Client ID and secret correspond to your Entra Application registration
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url=os.getenv("KEY_VAULT_URL"), credential=credential
)
CLIENT_SECRET = client.get_secret(os.getenv("CLIENT_SECRET")).value
CLIENT_ID = os.environ.get("CLIENT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('TENANT_NAME')}"

SCOPE = ["User.Read"]

# Redirect path where the user will be directed to after logging in. This needs to configured in the Entra Application
# Registration -> Manage -> Authentication -> Web Redirect URIs, prepended with the possible values for
# BASE_APPLICATION_URL, e.g.:
# - `http://localhost:8080/.auth/login/aad/callback`
# - `https://<your_app_name>.azurewebsites.net/.auth/login/aad/callback`
REDIRECT_PATH = "/.auth/login/aad/callback"

# URL to log the user out in Entra
ENTRA_LOGOUT_ENDPOINT = f"https://login.microsoftonline.com/{os.environ.get('TENANT_NAME')}/oauth2/v2.0/logout"

# MSAL app instance
msal_app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)
# Cache for in-progress authorisation flows. Give the user 5 minutes to complete the flow
AUTH_FLOW_STATES: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 5)

# Cache authenticated users for a maximum of 10 hours. TTL is in seconds
USER_DATA: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 60 * 10)
register_login_pages(
    msal_app=msal_app,
    AUTH_FLOW_STATES=AUTH_FLOW_STATES,
    USER_DATA=USER_DATA,
    ENTRA_LOGOUT_ENDPOINT=ENTRA_LOGOUT_ENDPOINT,
    SCOPE=SCOPE,
    REDIRECT_PATH=REDIRECT_PATH,
)

def require_login() -> dict[str, Any] | None:
    browser_id = app.storage.browser["id"]
    user = USER_DATA.get(browser_id)
    if not user:
        ui.navigate.to("/login")
        return None
    return user



# keep a global cache of loaded projects for comparison
ORIGINAL_PROJECTS: dict[str, list[ProjectData]] = {}
@ui.page("/")
def index(client: Client):
    """
    This home page serves to check whether a user is logged in or not. If not, a login button will be presented. If yes,
    the user will be directed to the portal app.
    """

    # Obtain the browser ID and use it to determine whether the user is logged in or not
    browser_id = app.storage.browser["id"]
    user = USER_DATA.get(browser_id, None)

    # if "user" was not initialised
    if not user:
        # Display log in components
        with ui.column().classes("w-full items-center"):
            ui.markdown(f"## NiceGUI Entra authentication app\n Welcome to this app. \n Please log in").style(
                "white-space: pre-wrap"
            ).classes('text-l')

            ui.button("Login with Microsoft", on_click=lambda: ui.navigate.to("/login"))
    else:
        # If the user is logged in, store their information and redirect them to the actual app
        app.storage.user["user"] = user.get("claims")

        ui.navigate.to("/home")



@ui.page('/home')
def main_page():
    require_login()
    layout(active_step='oversikt', title='Oversikt over dine prosjekter')
    ui.label('This is the home page.')



@ui.page('/overordnet')
def overordnet():
    user = require_login()
    if not user:
        return 
    layout(active_step='overordnet', title='Overordnet info')
    # digdir_overordnet_info_page('overordnet')
    ui.label('This is the Overordnet page.')

@ui.page("/digdir_aktivitet")
def digdir():
    user = require_login()
    if not user:
        return 
    layout(active_step='aktivitet',  title='Om Digdirs aktivitet')
    # digdir_aktivitet_page('aktivitet')
    ui.label('This is the Digdir page.')


@ui.page("/leveranse")
def leveranse():
    user = require_login()
    if not user:
        return 
    layout(active_step='leveranse', title='Om Digdirs leveranse')
    # digdir_leveranse("leveranse")




@ui.page('/projects')
def projects_page():
    user = require_login()
    if not user:
        return
    
    email = user["claims"].get("preferred_username") or user["claims"].get("emails", [None])[0]
    if not email:
        ui.notify('No email claim found in login!')
        return
    
    layout(active_step='oversikt', title='Prosjekter')
    ui.label(f'Prosjekter for {email}')
    
    with Session(engine) as session:
        projects = get_project_data(session, email)
    
    # store original copy for later diff
    ORIGINAL_PROJECTS[email] = [p.model_copy(deep=True) for p in projects]
    
    # create a table with editable fields
    table = ui.table(
        columns=[{'name': f, 'label': f, 'field': f, 'editable': True} for f in projects[0].model_fields.keys()],
        rows=[p.dict() for p in projects],
        row_key='prosjekt_id'
    ).classes('w-full')
    
    def save_changes():
        # get edited rows back from table
        edited = [ProjectData(**row) for row in table.rows]
        diffs = diff_projects(ORIGINAL_PROJECTS[email], edited)
        
        if not diffs:
            ui.notify('No changes detected')
            return
        
        with Session(engine) as session:
            apply_changes(session, diffs)
            ui.notify('Changes saved to database!')
    
    ui.button('Save changes', on_click=save_changes)


if __name__ in {"__main__", "__mp_main__"}:
    
    ui.run(
        title='Internasjonale Aktiviteter',
        port=8080,
        storage_secret=str(uuid.uuid4()),
    )