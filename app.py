from nicegui import ui, app, Client, run
from typing import Any
from cachetools import TTLCache
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication

from utils.db_connection import DBConnector, ProjectData
from pages.login_page import register_login_pages
from pages.dashboard import dashboard
from pages.single_project import project_detail as digdir_overordnet_info_page
from pages.utils import layout
import uuid

load_dotenv()

# Client ID and secret correspond to your Entra Application registration
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url=os.getenv("KEY_VAULT_URL"), credential=credential
)
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.environ.get("CLIENT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('TENANT_NAME')}"

SCOPE = ["User.Read"]
REDIRECT_PATH = "/.auth/login/aad/callback"

# URL to log the user out in Entra
ENTRA_LOGOUT_ENDPOINT = f"https://login.microsoftonline.com/{os.environ.get('TENANT_NAME')}/oauth2/v2.0/logout"

# MSAL app instance
msal_app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

db_connector = DBConnector.create_engine(driver_name = "{ODBC Driver 18 for SQL Server}", server_name = os.getenv("SERVER"), database_name = os.getenv("DATABASE"), fabric_client_id = os.getenv("FABRIC_CLIENT_ID"), fabric_tenant_id  = os.getenv("TENANT_ID"), fabric_client_secret = os.getenv("FABRIC_SECRET"))
# Cache for in-progress authorisation flows. Give the user 5 minutes to complete the flow
AUTH_FLOW_STATES: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 5)

register_login_pages(
    msal_app=msal_app,
    AUTH_FLOW_STATES=AUTH_FLOW_STATES,
    ENTRA_LOGOUT_ENDPOINT=ENTRA_LOGOUT_ENDPOINT,
    SCOPE=SCOPE,
    REDIRECT_PATH=REDIRECT_PATH,
)

def require_login() -> dict[str, Any] | None:
    claims = app.storage.user.get("claims")
    if not claims:
        ui.navigate.to("/login")
        return None
    return claims

steps_dict = {
    "home": "Oversikt over dine prosjekter",
    "oppdater_prosjekt": "Ny/ endre prosjekt",
    "status_rapportering": "Rapportering av status",
    "leveranse": "Om Digdirs leveranse"
}
field_mapping = {
    "navn_tiltak": "Navn prosjekt",
    "kontaktperson": "Kontaktperson",
    "tiltakseier":"Tiltakseier",
    "avdeling": "Hovedavdeling",
    "fase_tiltak": "Fase",
    "date_modified": "Sist endret",
}
avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS']  # <-- your real avdelinger
super_user = os.getenv("SUPER_USER")
# keep a global cache of loaded projects for comparison
ORIGINAL_PROJECTS: dict[str, list[ProjectData]] = {}
@ui.page("/")
def index(client: Client):
    """
    This home page serves to check whether a user is logged in or not. If not, a login button will be presented. If yes,
    the user will be directed to the portal app.
    """

    # Obtain the browser ID and use it to determine whether the user is logged in or not
    claims = app.storage.user.get("claims")
    # if "user" was not initialised
    if not claims:
        # Display log in components
        with ui.column().classes("w-full items-center"):
            ui.markdown(f"## Prosjekt portalen autentisering \n Welcome to this app. \n Please log in").style(
                "white-space: pre-wrap"
            ).classes('text-l')

            ui.button("Login with Microsoft", on_click=lambda: ui.navigate.to("/login"))
    else:
        # If the user is logged in, store their information and redirect them to the actual app
        ui.navigate.to("/home")



@ui.page('/home')
def main_page():
    user = require_login()
    if not user:
        return 

    layout(active_step='home', title='Oversikt over dine prosjekter', steps=steps_dict)
    ui.label('This is the home page.')
    dashboard()



@ui.page('/oppdater_prosjekt')
async def overordnet():
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
        projects = await run.io_bound(db_connector.get_projects, None)
    else:        
        projects = await run.io_bound(db_connector.get_projects, email)
    
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
    user_name = user["name"]
    print(user_name)
    email = user["preferred_username"]
    if not email:
        ui.notify('No email claim found in login!')
        return
    digdir_overordnet_info_page(db_connector=db_connector, prosjekt_id=prosjekt_id, email=email, user_name=user_name)
@ui.page('/project/new/{prosjekt_id}')
def project_detail(prosjekt_id: str):
    
    user = require_login()
    if not user:
        return 
    layout(active_step='oppdater_prosjekt', title='Prosjekt detaljer', steps=steps_dict)

    email = user["preferred_username"]
    user_name = user["name"]
    print(user_name)
    if not email:
        ui.notify('No email claim found in login!')
        return
    digdir_overordnet_info_page(db_connector=db_connector, prosjekt_id=prosjekt_id, email=email, user_name=user_name, new=True)
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


if __name__ in {"__main__", "__mp_main__"}:
    
    ui.run(
        title='Projectportfolio',
        host="0.0.0.0",    
        port=8080,
        storage_secret=os.getenv("STORAGE_SECRET"),
        favicon='icon/Verktøykasse.png'
    )