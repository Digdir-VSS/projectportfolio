from nicegui import ui, run
from datetime import datetime, date
import ast
import json
from utils.azure_users import load_users
from utils.db_connection import DBConnector, ProjectData
from utils.data_models import RessursbrukUI
import ast, asyncio
import copy
from pydantic import BaseModel

def to_list(value):
    """Safely parse a JSON list or return [] if invalid."""
    if value is None:
        return []
    if isinstance(value, list):  # Already deserialized
        return value
    value = str(value).strip()
    if not value or value.lower() in ("null", "none"):
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []

def to_json(value: list[str] | None):
    """Convert UI list back to JSON string for the dataclass."""
    return json.dumps(value or [],  ensure_ascii=False)

def to_date_str(value):
    """Convert datetime/date to ISO date string (YYYY-MM-DD) for NiceGUI."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)

def to_datetime(value):
    if isinstance(value, str):
        return datetime.strptime(value,"%Y-%m-%d")
    else:
        return value
    
brukere = load_users()

brukere_list = list(brukere.keys())
avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS', 'KI Norge']
def project_detail(db_connector: DBConnector, prosjekt_id: str, email: str, user_name: str, new: bool = False):
    if new:
        project = db_connector.create_empty_project(email=email, prosjekt_id=prosjekt_id)
    else:
        project = db_connector.get_single_project(prosjekt_id)
        if not project:
            ui.label('Project not found or you do not have access to it.')
            return
    original_project = copy.deepcopy(project)
    ui.markdown(f"## *Porteføljeinitiativ:* **{project.portfolioproject.navn}**").classes('text-xl font-bold')
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("1. Grunninformasjon").classes('col-span-1 row-span-1 col-start-1 row-start-3 text-lg font-bold underline mt-4 mb-2')
        with ui.element("div").classes('col-span-2 row-span-1 col-start-2 row-start-3'):
            ui.label("Navn på tiltak").classes('text-lg font-bold')
            ui.input(value=project.portfolioproject.navn).classes('w-full bg-white rounded-lg').bind_value(project.portfolioproject, "navn")
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-4'):
            ui.label("Tiltakseier (linjeleder)").classes('text-lg font-bold')
            ui.select(brukere_list, with_input=True, multiple=False, validation= lambda value: "Du må velge en tiltakseier" if value == None else None).props(
                    "outlined dense clearable options-dense color=primary").classes(
                        "w-full bg-white rounded-lg").props('use-chips').bind_value(project.portfolioproject, "tiltakseier")
 
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-5'):
            ui.label("Kontaktperson").classes('text-lg font-bold')
            ui.select(brukere_list, with_input=True, multiple=True).props(
                    "clearable options-dense color=primary").classes("w-full bg-white rounded-lg").props('use-chips').bind_value(project.portfolioproject, "kontaktpersoner", forward=to_json, backward=to_list)

        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-6'):
            ui.label('Hovedavdeling').classes('text-lg font-bold')
            ui.radio(
                avdelinger,  # <-- your real avdelinger
            ).props("inline").bind_value(project.portfolioproject, "avdeling")
        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-7'):
            ui.label('Samarbeid internt').classes('text-lg font-bold')

            ui.select(
                avdelinger,
                multiple=True,
            ).props("use-chips").classes("w-full bg-white rounded-lg").bind_value(project.samarabeid, "samarbeid_intern", forward=to_json, backward=to_list)

        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-7'):
            ui.label('Samarbeid eksternt').classes('text-lg font-bold')
            ui.input().classes('w-full bg-white rounded-lg').bind_value(project.samarabeid, "samarbeid_eksternt")

        with ui.element("div").classes('col-span-3 row-span-2 col-start-4 row-start-6'):
            ui.label("Avhengigheter andre oppgaver").classes('text-lg font-bold')
            ui.textarea().classes('w-full bg-white rounded-lg').bind_value(project.samarabeid, "avhengigheter_andre")

        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-4'):
            ui.label("Hvilken fase skal startes").classes('text-lg font-bold')
            ui.select(
                ['Konsept', 'Planlegging', 'Gjennomføring','Problem/ide'],
                ).classes('w-full bg-white rounded-lg').bind_value(project.fremskritt, "fase")
        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-5'):
            ui.label('Start').classes('text-lg font-bold')
            ui.date().bind_value(project.portfolioproject, "oppstart").props("outlined dense clearable color=primary").classes("w-full")
            
        with ui.element("div").classes('col-span-1 row-span-1 col-start-5 row-start-5'):
            ui.label("Planlagt ferdig").classes('text-lg font-bold')
            ui.date().bind_value(project.fremskritt, "planlagt_ferdig").props("outlined dense clearable color=primary").classes("w-full")
            
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("2. Begrunnelse").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-5 row-span-3 col-start-1 row-start-3'):
            ui.label('Problemstilling').classes('text-lg font-bold')
            ui.textarea(value=project.problemstilling.problem).classes('w-full bg-white rounded-lg').bind_value(project.problemstilling, "problem")

        with ui.element("div").classes('col-span-5 row-span-3 col-start-1 row-start-6'):
            ui.label("Beskrivelse av tiltaket og hovedleveranser for denne fasen").classes('text-lg font-bold')
            ui.textarea(value=project.tiltak.tiltak_beskrivelse).classes('w-full bg-white rounded-lg').bind_value(project.tiltak, "tiltak_beskrivelse")

        with ui.element("div").classes('col-span-5 row-span-2 col-start-1 row-start-9'):
            ui.label('Risiko hvis tiltaket ikke gjennomføres').classes('text-lg font-bold')
            ui.textarea(value=project.risikovurdering.vurdering).classes('w-full bg-white rounded-lg').bind_value(project.risikovurdering, "vurdering")
  
    with ui.grid(columns=4).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("3. Tilknytning til strategier").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        ui.label("Beskriv hvordan tiltaket understøtter målbildet").classes('col-span-4 row-span-1 col-start-1 row-start-3 text-lg font-bold')
        ui.label("1 Vi fremmer samordning og prioritering for en mer effektiv offentlig sektor").classes('col-span-2 row-span-1 col-start-1 row-start-4 text-lg')
        ui.textarea().classes('col-span-2 row-span-2 col-start-1 row-start-5 bg-white rounded-lg').bind_value(project.malbilde, "malbilde_1_beskrivelse")
        ui.label("2 Vi leder an i ansvarlig og innovativ bruk av data og kunstig intelligens").classes('col-span-2 row-span-1 col-start-3 row-start-4 text-lg')
        ui.textarea().classes('col-span-2 row-span-2 col-start-3 row-start-5 bg-white rounded-lg').bind_value(project.malbilde, "malbilde_2_beskrivelse")
        ui.label("3 Vi sikrer trygg tilgang til digitale tjenester for alle").classes('col-span-2 row-span-1 col-start-1 row-start-7 text-lg')
        ui.textarea().classes('col-span-2 row-span-2 col-start-1 row-start-8 bg-white rounded-lg').bind_value(project.malbilde, "malbilde_3_beskrivelse")
        ui.label("4 Vi løser komplekse utfordringer sammen og tilpasser oss en verden i rask endring").classes('col-span-2 row-span-1 col-start-3 row-start-7 text-lg')
        ui.textarea().classes('col-span-2 row-span-2 col-start-3 row-start-8 bg-white rounded-lg').bind_value(project.malbilde, "malbilde_4_beskrivelse")
        digitaliserings_strategi_digdir = {
            "6": "6: få på plass veiledning om regelverksutvikling innen digitalisering, KI og datadeling",
            "11a": "11a: forsterke arbeidet med sammenhengende tjenester, i samarbeid med KS",
            "11g": "11g: videreføre arbeidet med livshendelser - Dødsfall og arv",
            "12": "12: utrede en felles digital inngang til innbyggere og andre brukere til informasjon og til digitale offentlige tjenester",
            "13": "13: etablere en utprøvingsarena for utforsking av regulatoriske og teknologiske utfordringer i arbeidet med sammenhengende tjenester",
            "15": "15: videreutvikle virkemidler for digitalisering og innovasjon i offentlig sektor",
            "41": "41: etablere en nasjonal arkitektur for et felles digitalt økosystem, i samarbeid med KS",
            "42": "42: tilby alle en digital lommebok med eID på høyt nivå",
            "43": "43: utvikle løsninger for digital representasjon, herunder for vergemål",
            "51": "51: samordne råd- og veiledningsressurser innenfor digital sikkerhet bedre",
            "74": "74: samordne og styrke veiledningen om deling og bruk av data, og arbeidet med orden i eget hus",
            "75": "75: prioritere arbeidet med å gjøre tilgjengelig nasjonale datasett som er viktige for offentlig sektor og samfunnet",
            "76": "76: legge til rette for sektorovergripende samarbeid om standarder og formater for datautveksling for digitalisering av hele verdikjeder",
            "87": "87: styrke veiledningsarbeidet for ansvarlig utvikling og bruk av KI, blant annet gjennom regulatoriske sandkasser",
            "88": "88: sikre ansvarlig utvikling og bruk av KI i offentlig sektor",
            "114": "114: følge opp Handlingsplan for auka inkludering i eit digitalt samfunn",
            "115": "115: styrke innsatsen for å øke den digitale kompetansen hos seniorer",
            "116": "116: styrke arbeidet med brukskvalitet, klarspråk og universell utforming i offentlige digitale tjenester",
            "118": "118: sikre økt brukerinvolvering ved utvikling av digitale tjenester"
        }
        reverse_digdir = {v: k for k, v in digitaliserings_strategi_digdir.items()}
        with ui.element("div").classes('col-span-4 row-span-3 col-start-1 row-start-10'):
            ui.label('Tilknyttet tiltak i Digitaliseringsstrategien').classes('text-lg font-bold')
            ui.select(list(digitaliserings_strategi_digdir.values()), multiple=True).classes('w-full bg-white rounded-lg').bind_value(project.digitaliseringstrategi, "sammenheng_digital_strategi", forward=to_json, backward=to_list)
        with ui.element("div").classes('col-span-4 row-span-2 col-start-1 row-start-13'):
                ui.label('Eventuell beskrivelse av kobling til Digitaliseringsstrategien').classes('text-lg font-bold')
                ui.textarea().bind_value(project.digitaliseringstrategi, "digital_strategi_kommentar").classes('w-full bg-white rounded-lg')

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("4. Ressursbehov").classes('col-span-5 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-1 row-start-3'):
            ui.label("Hvilke kompetanser trenges for tiltaket?").classes('text-lg font-bold')
            ui.textarea().classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "kompetanse_som_trengs")

        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-3'):
            ui.label("Er kompetanser tilgjengelige internt").classes('text-lg font-bold')
            kompetanse_internt_list = ["Ja","Ja, men det er ikke tilstrekkelig kapasitet","Delvis","Nei"]
            #selected_kompetanse = project.resursbehov.kompetanse_tilgjengelig  if project.resursbehov.kompetanse_tilgjengelig in kompetanse_internt_list else None
            ui.select(kompetanse_internt_list).classes('w-full bg-white rounded-lg').bind_value( project.resursbehov, "kompetanse_tilgjengelig")
        

        ui.label("Estimert antall månedsverk for fasen").classes('text-lg font-bold col-span-2 row-span-2 col-start-4 row-start-2')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-3'):
            ui.label("Interne").classes('text-lg font-bold')
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "antall_mandsverk_intern",forward=lambda x: int(x) if x not in (None,"") else None)
        with ui.element("div").classes('col-span-1 row-span-1 col-start-5 row-start-3'):
            ui.label("Eksterne").classes('text-lg font-bold')
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "antall_mandsverk_ekstern",forward=lambda x: int(x) if x not in (None,"") else None)

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("5. Finansieringsbehov (ekskl. interne ressurser)​").classes('col-span-5 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-3'):
            ui.label('Estimert budsjettbehov i kr').classes('text-lg font-bold')
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "estimert_budsjet_behov",forward=lambda x: int(x) if x not in (None,"") else None)

        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-4'):
            ui.label("Hvor sikkert er estimatet").classes('text-lg font-bold')
            estimat_liste = ["Relativt sikkert","Noe usikkert","Svært usikkert"]

            ui.select(estimat_liste).classes('w-full bg-white rounded-lg').bind_value(project.resursbehov,"risiko_av_estimat")

        with ui.element("div").classes('col-span-4 row-span-2 col-start-2 row-start-4'):
            ui.label('Forklaring estimat').classes('text-lg font-bold')
            ui.textarea(value=project.resursbehov.estimert_budsjet_forklaring).classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "estimert_budsjet_forklaring")
        
        with ui.element("div").classes('col-span-3 row-span-2 col-start-3 row-start-3'):
            ui.label('Fordeling av budsjett pr år').classes('text-lg font-bold')
            
            # Horizontal container for the year inputs
            with ui.element("div").classes("flex flex-wrap space-x-8 mt-2"):
                for year in [2026, 2027, 2028]:
                    # Ensure the dict always has a RessursbrukUI object for this year
                    if year not in project.ressursbruk:
                        project.ressursbruk[year] = RessursbrukUI(year=year, predicted_resources=None)
                    
                    # Container for each year (vertical inside horizontal)
                    with ui.element("div").classes("flex flex-row items-center"):
                        ui.label(f"{year}").classes('font-medium')
                        ui.input().props('type=number min=0 step=1 input-style="text-align: right;"') \
                        .classes('w-24 bg-white rounded-lg') \
                        .bind_value(project.ressursbruk[year], 'predicted_resources',forward=lambda x: int(x) if x not in (None,"") else None)

    async def prune_unchanged_fields() -> ProjectData:
        """Compare original and modified ProjectData, and remove unchanged submodels."""
        IGNORED_FIELDS = {
            "sist_endret",
            "endret_av",
            "er_gjeldende",
            "prosjekt_id",
            "ressursbruk_id",
        }

        def clean_dict(d):
            """Convert dataclass to dict and remove ignored fields."""
            if isinstance(d, BaseModel):
                d = d.model_dump()
            return {k: v for k, v in d.items() if k not in IGNORED_FIELDS}

        # Iterate through each submodel (e.g. fremskritt, tiltak, etc.)
        for field_name, original_value in original_project.__dict__.items():
            modified_value = getattr(project, field_name, None)

            # Skip if the modified field doesn't exist
            if modified_value is None:
                continue

            # Handle ressursbruk separately (it's a dict of year → RessursbrukUI)
            if field_name == "ressursbruk":
                new_dict = {}
                original_ressurs = getattr(original_project, field_name, {}) or {}

                for year, modified_year_obj in modified_value.items():
                    original_year_obj = original_ressurs.get(year)


                    if original_year_obj is None:
                        new_dict[year] = modified_year_obj
                        continue
                    
                    orig_clean = clean_dict(original_year_obj)
                    mod_clean = clean_dict(modified_year_obj)
                    if orig_clean != mod_clean:
                        new_dict[year] = modified_year_obj
                # If nothing changed for any year, clear the entire dict
                if not new_dict:
                    setattr(project, field_name, None)
                else:
                    setattr(project, field_name, new_dict)
                continue

            # Compare regular dataclass models
            if isinstance(modified_value, BaseModel) and isinstance(original_value, BaseModel):
                if clean_dict(original_value) == clean_dict(modified_value):
                    setattr(project, field_name, None)

        if project.portfolioproject:
            kontakt_list = ast.literal_eval(project.portfolioproject.kontaktpersoner)

            if project.portfolioproject.tiltakseier:
                if project.portfolioproject.tiltakseier not in kontakt_list:
                    kontakt_list.append(project.portfolioproject.tiltakseier)
            kontakt_epost = [brukere.get(i) for i in kontakt_list]
            project.portfolioproject.epost_kontakt = str(kontakt_epost)

        with ui.dialog() as dialog:
            ui.label("💾 Lagrer endringer... Vennligst vent ⏳")
            ui.spinner(size="lg", color="primary")
        try:
            dialog.open()
            await asyncio.sleep(0.1)  # Allow UI to render spinner
            await run.io_bound(db_connector.update_project, project, prosjekt_id, email)

            ui.notify("✅ Endringer lagret i databasen!", type="positive", position="top")

            await asyncio.sleep(1)
            ui.navigate.to(f"/project/{prosjekt_id}")
        finally:
            dialog.close()
    async def check_or_update():
        kontaktpersoner = project.portfolioproject.kontaktpersoner
        navn = project.portfolioproject.navn
        if isinstance(kontaktpersoner, str):
            try:
                parsed = ast.literal_eval(kontaktpersoner)
                if isinstance(parsed, list):
                    kontaktpersoner = parsed
                else:
                    kontaktpersoner = []
            except Exception:
                kontaktpersoner = []
        # Check navn_tiltak — handles None or empty string
        if not navn or navn.strip() == "":
            ui.notify("❌ Du må fylle inn tiltaksnavn.", type="warning", position="top", close_button="OK")
            return
        if not kontaktpersoner or (isinstance(kontaktpersoner, list) and len(kontaktpersoner) == 0) \
        or (isinstance(kontaktpersoner, str) and kontaktpersoner.strip() == ""):
            ui.notify("❌ Du må fylle inn kontaktperson.", type="warning", position="top", close_button="OK")
            return

        await prune_unchanged_fields()

    ui.button("💾 Save", on_click=check_or_update).classes("mt-4")

