from nicegui import ui, app, Client
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
import os
from msal import ConfidentialClientApplication
from cachetools import TTLCache
from sqlalchemy import create_engine
import pandas as pd
import uuid 
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import text

from pages.login_page import register_login_pages
from pages.utils import layout, validate_token
from database_connection.create_connection import build_engine
from database_connection.sql_models import PageAktivitetUI, PageLeveranseUI, PageOverordnetInfoUI

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

# resource_url = "https://database.windows.net/.default"
# system_assigned_credentials = DefaultAzureCredential()
# token_object = system_assigned_credentials.get_token(resource_url)
# connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={os.getenv('SQL_ENDPOINT')},1433;Database={os.getenv('DATABASE')};Encrypt=Yes;TrustServerCertificate=No"
# db_engine = build_engine(connection_string, token_object)

# Cache for in-progress authorisation flows. Give the user 5 minutes to complete the flow
AUTH_FLOW_STATES: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 5)

# Cache authenticated users for a maximum of 10 hours. TTL is in seconds
USER_DATA: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=256, ttl=60 * 60 * 10)


azure_client_id = os.getenv("AZURE_CLIENT_ID")
azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")
server = os.getenv("SERVER")
database = os.getenv("DATABASE")
driver="ODBC Driver 18 for SQL Server"
connection_string = (f"mssql+pyodbc://{azure_client_id}:{azure_client_secret}@{server}:1433/{database}"
f"?driver={driver}"
"&authentication=ActiveDirectoryServicePrincipal"
"&timeout=120"
"&Encrypt=yes"
"&TrustServerCertificate=no"
)


engine2 = create_engine(connection_string, connect_args={'timeout': 120})
# Session = scoped_session(sessionmaker(bind=engine2))

# s = Session()
# result = s.execute("INSERT INTO [dbo].[new_table] (age, name) VALUES (25, 'Test User')")
with engine2.connect() as connection:
    result = connection.execute(text("INSERT INTO [dbo].[new_table] (age, name) VALUES (25, 'Test User')"))
    print(result.all())
# query = "INSERT INTO [dbo].[new_table] (age, name) VALUES (25, 'Test User')"
# df = pd.read_sql_query(query, engine2)
# print(df)

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


if __name__ in {"__main__", "__mp_main__"}:
    
    ui.run(
        title='Internasjonale Aktiviteter',
        port=8080,
        storage_secret=str(uuid.uuid4()),
    )
