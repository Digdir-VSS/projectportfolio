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
from utils.project_loader import get_project_data, ProjectData, engine  # your Pydantic model
from pages.login_page import register_login_pages
from pages.dashboard import dashboard
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

steps_dict = {
    "home": "Oversikt over dine prosjekter",
    "oppdater_prosjekt": "Ny/ endre prosjekt",
    "digdir_aktivitet": "Om Digdirs aktivitet",
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
    user = require_login()
    # if user is not None:
    #     print(user["preferred_username"])
    layout(active_step='home', title='Oversikt over dine prosjekter', steps=steps_dict)
    ui.label('This is the home page.')
    dashboard()



@ui.page('/oppdater_prosjekt')
def overordnet():
    user = require_login()
    if not user:
        return 
    # digdir_overordnet_info_page('overordnet')
        # load projects for this user
    email = user["preferred_username"]
    # email = "jonhakon.odd@digdir.no"  # for testing
    if not email:
        ui.notify('No email claim found in login!')
        return

    layout(active_step='oppdater_prosjekt', title='Rediger prosjekt', steps=steps_dict)
    ui.label(f'Prosjekter for {email}')
    if email in super_user:
        ui.label('You are a super user and can edit all projects.')

        with Session(engine) as session:
            projects = get_project_data(session, None)
    else:        
        with Session(engine) as session:
            projects = get_project_data(session, email)
        # print(projects)
    # store original copy for later diff

    
    # create a table with editable fields
    if not projects:
        ui.label('No projects found for this user.')
        return
    ORIGINAL_PROJECTS[email] = {
        str(p.prosjekt_id): p.model_copy(deep=True) for p in projects
    }
    # print(projects[0].model_fields.keys())
#     rows = [
#     {new_key: getattr(p, old_key) for old_key, new_key in field_mapping.items()}
#     for p in projects
# ]

    # define columns with new names
    columns = [
        {"name": new_key, "label": new_key, "field": new_key, "editable": True}
        for new_key in field_mapping.values()
    ]
    rows = [
        {
            "prosjekt_id": str(p.prosjekt_id),
            **{new_key: getattr(p, old_key) for old_key, new_key in field_mapping.items()}
        }
        for p in projects
    ]
    table = ui.table(
        columns=columns,
        rows=rows,
        row_key='prosjekt_id',  # or "Kontaktperson" if that's unique, or keep prosjekt_id hidden
        column_defaults={"align": "left", 'headerClasses': 'uppercase text-primary', "sortable": True, "filterable": True},
        selection="single",
    ).classes("w-full")

    selected = ui.label("No project selected")

    def on_row_select(e):
        if e.args:
            selected.set_text(f"Selected: {e.args["rows"][0]["Navn prosjekt"]}")

    table.on("selection", on_row_select)
    def open_details():
        selected_rows = table.selected
        if selected_rows:
            prosjekt_id = selected_rows[0]['prosjekt_id']
            ui.navigate.to(f"/project/{prosjekt_id}")

    ui.button("Open details", on_click=open_details)
    # def save_changes():
    #     # get edited rows back from table
    #     edited = [ProjectData(**row) for row in table.rows]
    #     diffs = diff_projects(ORIGINAL_PROJECTS[email], edited)
        
    #     if not diffs:
    #         ui.notify('No changes detected')
    #         return
        
    #     with Session(engine) as session:
    #         apply_changes(session, diffs)
    #         ui.notify('Changes saved to database!')
    
    # ui.button('Save changes', on_click=save_changes)
@ui.page('/project/{prosjekt_id}')
def project_detail(prosjekt_id: str):
    layout(active_step='oppdater_prosjekt', title='Prosjekt detaljer', steps=steps_dict)
    user = require_login()
    if not user:
        return 
    # digdir_overordnet_info_page('overordnet')
        # load projects for this user
    email = user["preferred_username"]
    # email = "jonhakon.odd@digdir.no"  # for testing
    if not email:
        ui.notify('No email claim found in login!')
        return

    # get all data for this project
    # print(ORIGINAL_PROJECTS)
    project = ORIGINAL_PROJECTS[email].get(prosjekt_id)

    # project = next((p for p in projects if str(p.prosjekt_id) == prosjekt_id), None)

    if not project:
        ui.label("Project not found")
        return

    ui.markdown(f"## *{project.navn_tiltak or prosjekt_id}*")

    inputs: dict[str, Any] = {}
    # show all fields as key/value
    with ui.grid(columns=3).classes("gap-4 w-full"):
        inputs['navn_tiltak'] = ui.input('Navn prosjekt', value=project.navn_tiltak)
        inputs['kontaktperson'] = ui.input('Kontaktperson', value=project.kontaktperson)
        inputs["eier_epost"] = ui.input('Epost kontaktperson', value=project.eier_epost)
    with ui.grid(columns=2).classes("gap-4 w-full"):
        with ui.column().classes('items-left'):
            ui.label('Hovedavdeling')
            inputs['avdeling'] = ui.radio(
                avdelinger,  # <-- your real avdelinger
                value=project.avdeling
            ).props("inline")
            ui.label('Samarbeid internt')
            inputs["samarbeid_internt"] = ui.select(avdelinger, multiple=True, label='Samarbeid internt', value=project.samarbeid_intern.split(',') if project.samarbeid_intern else []).classes('w-64')
            ui.label('Samarbeid eksternt')
            inputs["samarbeid_eksternt"] = ui.input('Samarbeid eksternt', value=project.samarbeid_eksternt)
        inputs['beskrivelse'] = ui.textarea('Beskrivelse av prosjekt', value=project.beskrivelse).classes('w-full')
        
        with ui.column().classes('items-left flex'):
            inputs['avhengigheter_andre'] = ui.textarea(
                'Avhengigheter andre', value=project.avhengigheter_andre).classes('w-full')
            with ui.row().classes('items-center grid-flow-row auto-rows-max'):
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label('Start')
                    with ui.input(str(project.oppstart_tid.date())) as date:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.date().bind_value(date):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with date.add_slot('append'):
                            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label("Planlagt ferdig")
                    with ui.input(str(project.ferdig_tid.date())) as date:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.date().bind_value(date):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with date.add_slot('append'):
                            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label("Fase tiltak")
                    inputs['fase_tiltak'] = ui.select(
                        ['Konsept', 'Planlegging', 'Gjennomføring','Problem/ide'],
                        value=project.fase_tiltak
                    )
        with ui.column().classes('items-left'):
            ui.label('Problemstilling')
            inputs['problemstilling'] = ui.textarea('Problemstilling', value=project.problemstilling).classes('w-full')
        
        with ui.column().classes('items-left'):
            ui.label("Kompetansebehov")
            inputs['kompetanse_behov'] = ui.textarea('Kompetansebehov', value=project.kompetanse_behov).classes('w-full')
            with ui.row().classes('items-center grid-flow-row auto-rows-max'):
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label("Kompetanse internt")
                    kompetanse_internt_list = ["Ja","Ja, men det er ikke tilstrekkelig kapasitet","Delvis","Nei"]
                    selected_kompetanse = project.kompetanse_internt if project.kompetanse_internt in kompetanse_internt_list else None

                    inputs['kompetanse_internt'] = ui.select(kompetanse_internt_list, value=selected_kompetanse).classes('w-64')
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label("Månedsverk internt")
                    inputs['månedsverk_interne'] = ui.input(value=int(project.månedsverk_interne) or 0).props('type=number min=0').classes('w-32')
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label("Månedsverk eksternt")
                    inputs['månedsverk_eksterne'] = ui.input(value=int(project.månedsverk_eksterne) or 0).props('type=number min=0').classes('w-32')

        inputs['risiko'] = ui.textarea('Risikovurdering', value=project.risiko).classes('w-full')

        with ui.column().classes('items-left'):
            with ui.row().classes('items-center grid-flow-row auto-rows-max'):
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label('Estimert budsjett behov')
                    inputs['estimert_behov_utover_driftsrammen'] = ui.input('Budsjettbehov', value=project.estimert_behov_utover_driftsrammen).props('type=number min=0').classes('w-full')
                    # , validation=lambda value: "Må være et tall" if not isinstance(value, int) else None
                with ui.column().classes('items-left w-64 flex-1'):
                    ui.label("Hvor sikkert er estimatet")
                    estimat_liste = ["Relativt sikkert","Noe usikkert","Svart usikkert"]
                    selected_estimat = project.hvor_sikkert_estimatene if project.hvor_sikkert_estimatene in estimat_liste else None
                    inputs['hvor_sikkert_estimatene'] = ui.select(estimat_liste, value=selected_estimat).classes('w-full')
        inputs['estimert_behov_forklaring'] = ui.textarea('Forklaring estimat', value=project.estimert_behov_forklaring).classes('w-full')



                    # (value=str(project.oppstart_tid), on_change=lambda e: date.set_value(e.value)).props('min-width=150px')

            # with date.add_slot('append'):
            #     ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
        # print(project.oppstart_tid.date())
        # inputs['oppstart_tid'] = ui.date('Oppstart', type='date', value=str(project.oppstart_tid or ''))
        # inputs['ferdig_tid'] = ui.date('Ferdig', type='date', value=str(project.ferdig_tid or ''))
        # ui.input(value=project.navn_tiltak).props('label="Navn prosjekt"')
        # ui.input(value=project.kontaktperson).props('label="Kontaktperson"')   
        # ui.input(value=project.avdeling).props('label="Hovedavdeling"')
        # ui.input(value=project.fase_tiltak).props('label="Fase"')
        # ui.input(value=project.date_modified).props('label="Sist endret"') 
        # ui.input(value=project.beskrivelse).props('label="Beskrivelse av prosjekt"').classes('w-full')
        # ui.input(value=project.problemstilling).props('label="Problemstilling"').classes('w-full')
    # for field, value in project.dict().items():
    #     print(field)
    #     with ui.row():
    #         ui.label(field).classes("font-bold w-48")
    #         ui.label(str(value))


@ui.page("/digdir_aktivitet")
def digdir():
    user = require_login()
    if not user:
        return 
    layout(active_step='digdir_aktivitet',  title='Om Digdirs aktivitet',steps=steps_dict)
    # digdir_aktivitet_page('aktivitet')
    ui.label('This is the Digdir page.')


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
        print(projects)
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
        title='Internasjonale Aktiviteter',
        port=8080,
        storage_secret=str(uuid.uuid4()),
    )