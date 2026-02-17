from nicegui import ui, Client
from nicegui import app
from typing import Any
from cachetools import TTLCache
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication
import copy

from frontend.utils.backend_client import api_get_projects, api_get_project, api_create_new_project, api_get_overview, api_get_rapporterings_data, api_get_vurderings_data
from frontend.pages.login_page import register_login_pages
from frontend.pages.dashboard import dashboard
from frontend.pages.overview import overview_page
from frontend.pages.single_project import project_detail as digdir_overordnet_info_page
from frontend.pages.status_rapportering import show_status_rapportering_overview, show_status_rapportering
from frontend.pages.vurdering import show_status_vurdering_overview, show_vurdering
from frontend.utils.azure_users import load_users
from frontend.pages.utils import layout, get_menu_items_for_user
import uuid
from frontend.static_variables import STEPS_DICT

#app.include_router(innleverings_router)

load_dotenv()

bruker_list = load_users()

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

super_user = os.getenv("SUPER_USER")
# keep a global cache of loaded projects for comparison
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
        ui.navigate.to("/oppdater_prosjekt")



@ui.page('/home')
def main_page():
    user = require_login()
    if not user:
        return 
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)

    layout(title='Hjemmeside', menu_items=menu, active_route="home")
    ui.label('Detter er hjemmesiden. Her vil vi publisere en oversikt med informasjon om prosjektene.')
    dashboard()

def new_project():
    # Create a blank ProjectData with default values
    new_id = str(uuid.uuid4())

    # Store it in the same place so project_detail() can load it
    ui.notify("New project created", type="positive")

    # Navigate to the same project page as "edit"
    ui.navigate.to(f"/project/new/{new_id}")

@ui.page('/vurdering')
async def oversikt():
    user = require_login()
    if not user:
        return 
    email = user["preferred_username"]
    if email not in super_user:
        ui.notify("Du har ikke tilgang til denne siden", type="negative")
        ui.navigate.to("/oversikt")
        return
    oversikt_data = await api_get_overview()
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)

    layout(title='Oversikt', menu_items=menu, active_route="oversikt"),
    overview_page(oversikt_data)

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
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)

    layout(title='Ny/ endre prosjekt', menu_items=menu, active_route="oppdater_prosjekt")
    ui.label(f'Prosjekter for {user_name}').classes('text-lg font-bold mb-2')
    if email in super_user:
        ui.label('Du er logget inn som admin og ser alle prosjekter').classes('text-sm italic mb-4')
        projects = await api_get_projects(None)
    else:        
        projects = await api_get_projects(email)
    
    # store original copy for later diff

    
    
    with ui.column().classes("w-full gap-2"):
        with ui.row().classes('gap-2'):
            ui.button("➕ New Project", on_click=lambda: new_project()).props("color=secondary")
        # create a table with editable fields
        if not projects:
            ui.label('No projects found for this user.')
            return
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
   


@ui.page('/project/{prosjekt_id}')
async def project_detail(prosjekt_id: str):
  
    user = require_login()
    if not user:
        return 
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)

    layout(title='Prosjekt detaljer', menu_items=menu, active_route="oppdater_prosjekt")
    user_name = user["name"]
    email = user["preferred_username"]
    if not email:
        ui.notify('No email claim found in login!')
        return
    project = await api_get_project(prosjekt_id=prosjekt_id)
    if not project:
        ui.label('Prosjektet ble ikke funnet, eller du har ikke tilgang til det.')
        return
    digdir_overordnet_info_page(prosjekt_id=prosjekt_id, email=email, project=project, brukere_list=bruker_list)

@ui.page('/project/new/{prosjekt_id}')
async def project_detail(prosjekt_id: str):
    
    user = require_login()
    if not user:
        return 
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)

    layout(title="Oppdater prosjekt", menu_items=menu, active_route="oppdater_prosjekt")

    email = user["preferred_username"]
    project = await api_create_new_project(email=email, prosjekt_id=prosjekt_id)
    if not email:
        ui.notify('No email claim found in login!')
        return
    digdir_overordnet_info_page(prosjekt_id=prosjekt_id, email=email, project=project, brukere_list=bruker_list)

@ui.page("/status_rapportering")
async def status_rapportering_overview():
    user = require_login()
    if not user:
        return 
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)
    layout(title='Rapportering av status',menu_items=menu, active_route="status_rapportering")
    email = user["preferred_username"]

    if not email:
        ui.notify('No email claim found in login!')
        return
    if email in super_user:
        ui.label('Du er logget inn som admin og ser alle prosjekter').classes('text-sm italic mb-4')
        prosjekter = await api_get_projects(None)
    else:        
        prosjekter = await api_get_projects(email)
    show_status_rapportering_overview(prosjekter=prosjekter)

@ui.page("/status_rapportering/{prosjekt_id}")
async def status_rapportering(prosjekt_id):
    user = require_login()
    if not user:
        return 
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)
    layout(title='Rapportering av status',menu_items=menu, active_route="status_rapportering")
    email = user["preferred_username"]
    rapportering = await api_get_rapporterings_data(email=email, prosjekt_id=prosjekt_id)
    #print(rapportering)
    if not email:
        ui.notify('No email claim found in login!')
        return
    show_status_rapportering(prosjekt_id=prosjekt_id, email=email, rapportering=rapportering, brukere_list=bruker_list)


@ui.page("/vurdering/{prosjekt_id}")
async def vurderingen(prosjekt_id):
    user = require_login()
    if not user:
        return 
    email = user["preferred_username"]
    if email not in super_user:
        ui.notify("Du har ikke tilgang til denne siden", type="negative")
        ui.navigate.to("/oversikt")
        return
    menu = get_menu_items_for_user(user=user, super_user=super_user, STEPS_DICT=STEPS_DICT)
    layout(title='Vurdering av tiltak',menu_items=menu, active_route="vurdering")
    email = user["preferred_username"]
    vurdering = await api_get_vurderings_data(prosjekt_id=prosjekt_id)
    if not email:
        ui.notify('No email claim found in login!')
        return
    show_vurdering(prosjekt_id=prosjekt_id, email=email, vurdering=vurdering)



if __name__ in {"__main__", "__mp_main__"}:
    
    ui.run(
        title='Projectportfolio',
        host="0.0.0.0",    
        port=8080,
        storage_secret=os.getenv("STORAGE_SECRET"),
        favicon='icon/Verktøykasse.png',
    )