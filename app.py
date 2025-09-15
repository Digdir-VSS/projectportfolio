from nicegui import ui

from msal import ConfidentialClientApplication
from cachetools import TTLCache
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv
from pages.digdir_bidrag import digdir_bidrag_page
from pages.main import main_display

load_dotenv()
background="#f4f5f6"
stronger_background="#e9eaec"   
module="#b3d0ea"
primary='#0062ba'
secondary='#fff4b4'
accent='#f05f63'
felles_design = "#65707d"
warning='#C10015'
text_on_white="#1E2B3C"


azure_tenant_id = os.getenv("AZURE_TENANT_ID")
azure_client_id = os.getenv("AZURE_CLIENT_ID")
azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")

server = os.getenv("SERVER")
database = os.getenv("DATABASE")

driver = "ODBC Driver 18 for SQL Server"
connection_string = (f"mssql+pyodbc://{azure_client_id}:{azure_client_secret}@{server}:1433/{database}"
 f"?driver={driver}"
 "&authentication=ActiveDirectoryServicePrincipal"
 "&timeout=120"
 "&Encrypt=yes"
 "&TrustServerCertificate=no"
) 

engine2 = create_engine(connection_string, connect_args={'timeout': 120})
query = "select * from prosjekt_vurdering"
df = pd.read_sql_query(query, engine2)
print(df)

AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('TENANT_NAME')}"
REDIRECT_PATH = "/.auth/login/aad/callback"

# URL to log the user out in Entra
ENTRA_LOGOUT_ENDPOINT = f"https://login.microsoftonline.com/{os.environ.get('TENANT_NAME')}/oauth2/v2.0/logout"

# MSAL app instance
msal_app = ConfidentialClientApplication(
    azure_client_id,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

# Cache for in-progress authorisation flows. Give the user 5 minutes to complete the flow
AUTH_FLOW_STATES: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 5)

# Cache authenticated users for a maximum of 10 hours. TTL is in seconds
USER_DATA: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 60 * 10)

def require_login() -> dict[str, Any] | None:
    browser_id = app.storage.browser["id"]
    user = USER_DATA.get(browser_id)
    if not user:
        ui.navigate.to("/login")
        return None
    return user

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
        app.storage.user["user"] = user
        ui.navigate.to("/home")

def layout(active_step: str, title='Portfolio oversikt'):
    # HEADER
    with ui.header(elevated=True).style(f'background-color:{module}'):
        ui.label(title).classes('text-h3').style(f'color:{background}')

    # LEFT DRAWER
    with ui.left_drawer(elevated=True, value=True).style(f'background-color:{stronger_background}'):
        # Build steps first
        with ui.stepper().props('vertical header-nav color=primary active-color=primary done-color=secondary') \
                 .style(f'--q-primary: {module}; --q-secondary: {felles_design}').classes('w-full') as stepper:
            ui.step('Oversikt over dine prosjekter').props('name=oversikt clickable') \
                .on('click', lambda: ui.navigate.to('/'))
            ui.step('Overordnet info').props('name=overordnet clickable') \
                .on('click', lambda: ui.navigate.to('/overordnet'))
            ui.step('Digdirs bidrag').props('name=bidrag clickable') \
                .on('click', lambda: ui.navigate.to('/digdir_bidrag'))
            ui.step('Digdirs leveranse').props('name=leveranse clickable') \
                .on('click', lambda: ui.navigate.to('/leveranse'))
        stepper.value = active_step

@ui.page('/')
def main_page():
    layout(active_step='oversikt', title='Oversikt over dine prosjekter')
    main_display()
    ui.label('This is the home page.')

@ui.page('/digdir_bidrag')
def digdir():
    layout(active_step='bidrag', title='Digdirs bidrag')
    digdir_bidrag_page()
    ui.label('This is the Digdir page.')

# you can define other pages the same way
@ui.page('/overordnet')
def overordnet():
    layout(active_step='overordnet', title='Overordnet info')
    ui.label('This is the Overordnet page.')

@ui.page('/leveranse')
def leveranse():
    layout(active_step='leveranse', title='Digdirs leveranse')
    ui.label('This is the Leveranse page.')

ui.run(title='Internasjonale Aktiviteter')