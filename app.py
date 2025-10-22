from nicegui import ui, app, Client
from typing import Any
from cachetools import TTLCache
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication
from sqlmodel import Session

from utils.db_functions import diff_projects, apply_changes
from utils.project_loader import get_project_data, ProjectData, engine, get_projects  # your Pydantic model
from pages.login_page import register_login_pages
from pages.dashboard import dashboard
from pages.single_project import project_detail as digdir_overordnet_info_page
from pages.utils import layout, validate_token
import uuid
import json
import datetime
load_dotenv()

# Client ID and secret correspond to your Entra Application registration
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url=os.getenv("KEY_VAULT_URL"), credential=credential
)
CLIENT_SECRET = client.get_secret(os.getenv("CLIENT_SECRET_NAME")).value
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

steps_dict = {
    "home": "Oversikt over dine prosjekter",
    "oppdater_prosjekt": "Ny/ endre prosjekt",
    "status_rapportering": "Rapportering av status",
    "leveranse": "Om Digdirs leveranse",
    "projects": "Prosjekter"
}
field_mapping = {
    "navn_tiltak": "Navn prosjekt",
    "kontaktperson": "Kontaktperson",
    "avdeling": "Hovedavdeling",
    "fase_tiltak": "Fase",
    "date_modified": "Sist endret",
}
avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS']  # <-- your real avdelinger
super_user = json.loads(open('.hidden_config/config.json').read())[0]['super_user']
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
            ui.markdown(f"## Prosjekt portalen autentisering \n Welcome to this app. \n Please log in").style(
                "white-space: pre-wrap"
            ).classes('text-l')

            ui.button("Login with Microsoft", on_click=lambda: ui.navigate.to("/login"))
    else:
        # If the user is logged in, store their information and redirect them to the actual app
        app.storage.user["user"] = user.get("claims")

        ui.navigate.to("/home")



@ui.page('/home')
def main_page():
    user = require_login()

    layout(active_step='home', title='Oversikt over dine prosjekter', steps=steps_dict)
    ui.label('This is the home page.')
    dashboard()



@ui.page('/oppdater_prosjekt')
def overordnet():
    user = require_login()
    if not user:
        return 

    email = user["preferred_username"]
    user_name = user["name"]
    if not email:
        ui.notify('No email claim found in login!')
        return

    layout(active_step='oppdater_prosjekt', title='Rediger prosjekt', steps=steps_dict)
    ui.label(f'Prosjekter for {user_name}').classes('text-lg font-bold mb-2')
    if email in super_user:
        ui.label('You are a super user and can edit all projects.')

        with Session(engine) as session:
            projects = get_projects(session, None)
    else:        
        with Session(engine) as session:
            projects = get_projects(session, email)
    
    # store original copy for later diff

    
    # create a table with editable fields
    if not projects:
        ui.label('No projects found for this user.')
        return
    ORIGINAL_PROJECTS[email] = [p for p in projects]
    with ui.column().classes("w-full gap-2"):
        with ui.row().classes('gap-2'):
            ui.button("➕ New Project", on_click=lambda: new_project()).props("color=secondary")

        visible_keys = [
            key for key in projects[0].keys()
            if key not in ["prosjekt_id", "epost_kontakt"]
        ]

        columns = [
            {
                "name": key,
                "label": key.replace("_", " ").title(),
                "field": key,
                "sortable": True,
                "align": "left",
            }
            for key in visible_keys
        ]


        rows = [
            {**p, "prosjekt_id": str(p["prosjekt_id"])}  # ensure UUID is a string
            for p in projects
        ]

        table =  ui.table(columns=columns,
                    rows=rows,
                    row_key="prosjekt_id",
                    column_defaults={
                        "align": "left",
                        "headerClasses": "uppercase text-primary",
                        "sortable": True,
                        "filterable": True,
                    },).classes("w-full")

        table.add_slot(
            'header',
            r'''
            <q-tr :props="props">
                <q-th auto-width />
                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.label }}
                </q-th>
            </q-tr>
            '''
        )

        table.add_slot(
            'body',
            r'''
            <q-tr :props="props">
                <q-td auto-width>
                    <a :href="'/project/' + props.row.prosjekt_id"><q-btn size="sm" color="primary" round dense
                    @click="location.href = '/project/' + props.row.prosjekt_id"

                    icon="edit" /></a>
                    
                </q-td>
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.value }}
                </q-td>
            </q-tr>
            '''
        )
   
    def new_project():
        # Create a blank ProjectData with default values
        new_id = str(uuid.uuid4())

        # Store it in the same place so project_detail() can load it
        ui.notify("New project created", type="positive")

        # Navigate to the same project page as "edit"
        ui.navigate.to(f"/project/new/{new_id}")

@ui.page('/project/{prosjekt_id}')
def project_detail(prosjekt_id: str):
  
    user = require_login()
    if not user:
        return 
    layout(active_step='oppdater_prosjekt', title='Prosjekt detaljer', steps=steps_dict)

    email = user["preferred_username"]
    if not email:
        ui.notify('No email claim found in login!')
        return
    digdir_overordnet_info_page(prosjekt_id, email)
@ui.page('/project/new/{prosjekt_id}')
def project_detail(prosjekt_id: str):
    
    user = require_login()
    if not user:
        return 
    layout(active_step='oppdater_prosjekt', title='Prosjekt detaljer', steps=steps_dict)

    email = user["preferred_username"]
    if not email:
        ui.notify('No email claim found in login!')
        return
    digdir_overordnet_info_page(prosjekt_id, email, new=True)
@ui.page("/status_rapportering")
def digdir():
    user = require_login()
    if not user:
        return 
    layout(active_step='status_rapportering',  title='Rapportering av status',steps=steps_dict)
    # digdir_aktivitet_page('aktivitet')
    email = user["preferred_username"]
    user_name = user["name"]
    if not email:
        ui.notify('No email claim found in login!')
        return


@ui.page("/leveranse")
def leveranse():
    user = require_login()
    if not user:
        return 
    layout(active_step='leveranse', title='Om Digdirs leveranse',steps=steps_dict)
    # digdir_leveranse("leveranse")




@ui.page('/projects')
def projects_page():
    user = require_login()
    if not user:
        return
    # load projects for this user
    email = user["preferred_username"]
    # email = "jonhakon.odd@digdir.no"  # for testing
    if not email:
        ui.notify('No email claim found in login!')
        return
    
    layout(active_step='oversikt', title='Prosjekter', steps=steps_dict)
    ui.label(f'Prosjekter for {email}')
    
    with Session(engine) as session:
        projects = get_project_data(session, email)
    # store original copy for later diff
    ORIGINAL_PROJECTS[email] = [p.model_copy(deep=True) for p in projects]
    
    # create a table with editable fields
    if not projects:
        ui.label('No projects found for this user.')
        return
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
        title='Projectportfolio',
        port=8080,
        storage_secret=os.getenv("uuid_run"),
        favicon='icon/Verktøykasse.png'
    )