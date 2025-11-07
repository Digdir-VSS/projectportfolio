from nicegui import ui, run
from datetime import datetime, date
import ast
import json
from utils.azure_users import load_users
from utils.db_connection import DBConnector
import ast, asyncio

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
            oppstart = getattr(project.portfolioproject, "oppstart", None)
            if isinstance(oppstart, (datetime, date)):
                setattr(project.portfolioproject, "oppstart", to_date_str(oppstart))
            ui.input().bind_value(project.portfolioproject, "oppstart").props("outlined dense type=date clearable color=primary").classes("w-full")
            
        with ui.element("div").classes('col-span-1 row-span-1 col-start-5 row-start-5'):
            ui.label("Planlagt ferdig").classes('text-lg font-bold')
            ferdig_date = getattr(project.fremskritt, "planlagt_ferdig", None)
            if isinstance(ferdig_date, (datetime, date)):
                setattr(project.fremskritt, "planlagt_ferdig", to_date_str(ferdig_date))
            ui.input().bind_value(project.fremskritt, "planlagt_ferdig").props("outlined dense type=date clearable color=primary").classes("w-full")
            
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("2. Begrunnelse").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-5 row-span-3 col-start-1 row-start-3'):
            ui.label('Problemstilling').classes('text-lg font-bold')
            ui.textarea(value=project.problemstilling.problem).classes('w-full bg-white rounded-lg').bind_value(project.problemstilling, "problem")

        with ui.element("div").classes('col-span-5 row-span-3 col-start-1 row-start-6'):
            ui.label("Beskrivelse av tiltak").classes('text-lg font-bold')
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
        with ui.element("div").classes('col-span-4 row-span-2 col-start-1 row-start-10'):
            ui.label('Tilknyttet tiltak i Digitaliseringsstrategien').classes('text-lg font-bold')
            ui.select(list(digitaliserings_strategi_digdir.values()), multiple=True).classes('w-full bg-white rounded-lg').bind_value(project.digitaliseringstrategi, "sammenheng_digital_strategi", forward=to_json, backward=to_list)
        with ui.element("div").classes('col-span-4 row-span-2 col-start-1 row-start-12'):
                ui.label('Eventuelt kommentar').classes('text-lg font-bold')
                ui.textarea(value=None).classes('w-full bg-white rounded-lg')

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("4. Ressursbehov").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-1 row-start-3'):
            ui.label("Hvilke kompetanser trenges for tiltaket?").classes('text-lg font-bold')
            ui.textarea().classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "kompetanse_som_trengs")

        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-3'):
            ui.label("Er kompetanser tilgjengelige internt").classes('text-lg font-bold')
            kompetanse_internt_list = ["Ja","Ja, men det er ikke tilstrekkelig kapasitet","Delvis","Nei"]
            #selected_kompetanse = project.resursbehov.kompetanse_tilgjengelig  if project.resursbehov.kompetanse_tilgjengelig in kompetanse_internt_list else None
            ui.select(kompetanse_internt_list).classes('w-full bg-white rounded-lg').bind_value( project.resursbehov, "kompetanse_tilgjengelig")
        
        ui.label("Estimert antall månedsverk for fasen").classes('text-lg font-bold col-span-3 row-span-1 col-start-1 row-start-5')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-6'):
            ui.label("Interne").classes('text-lg font-bold')
            if isinstance(project.resursbehov.antall_mandsverk_intern, float) or isinstance(project.resursbehov.antall_mandsverk_intern, str) or isinstance(project.resursbehov.antall_mandsverk_intern, int):
                try: 
                    project.resursbehov.antall_mandsverk_intern = int(project.resursbehov.antall_mandsverk_intern)
                except:
                    project.resursbehov.antall_mandsverk_intern = 0
            else:
                project.resursbehov.antall_mandsverk_intern = None
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "antall_mandsverk_intern")
        with ui.element("div").classes('col-span-1 row-span-1 col-start-2 row-start-6'):
            ui.label("Eksterne").classes('text-lg font-bold')
            if isinstance(project.resursbehov.antall_mandsverk_ekstern, float) or isinstance(project.resursbehov.antall_mandsverk_ekstern, str) or isinstance(project.resursbehov.antall_mandsverk_intern, int):
                try:
                    project.resursbehov.antall_mandsverk_ekstern = int(project.resursbehov.antall_mandsverk_ekstern)
                except:
                    project.resursbehov.antall_mandsverk_ekstern = 0
            else:
                project.resursbehov.antall_mandsverk_ekstern = None
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "antall_mandsverk_ekstern")

        
        ui.label("Estimert finansieringsbehov (eksl. interne ressurser)").classes('text-lg font-bold col-span-2 row-span-1 col-start-4 row-start-2')

        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-3'):
            ui.label('Estimert budsjett behov').classes('text-lg font-bold')
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "estimert_budsjet_behov")

        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-4'):
            ui.label("Hvor sikkert er estimatet").classes('text-lg font-bold')
            estimat_liste = ["Relativt sikkert","Noe usikkert","Svært usikkert"]

            ui.select(estimat_liste).classes('w-full bg-white rounded-lg').bind_value(project.resursbehov,"risiko_av_estimat")

        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-5'):
            ui.label('Forklaring estimat').classes('text-lg font-bold')
            ui.textarea(value=project.resursbehov.estimert_budsjet_forklaring).classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "estimert_budsjet_forklaring")
    
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



        await update_data()

    async def update_data():
        with ui.dialog() as dialog:
            ui.label("💾 Lagrer endringer... Vennligst vent ⏳")
            ui.spinner(size="lg", color="primary")

        dialog.open()
        await asyncio.sleep(0.1)  # Allow UI to render spinner

        try:
            # --- Data normalization ---
            if project.portfolioproject.oppstart:
                if isinstance(project.portfolioproject.oppstart, (datetime, date)):
                    project.portfolioproject.oppstart = project.portfolioproject.oppstart.strftime("%Y-%m-%d")
                else:
                    project.portfolioproject.oppstart = str(project.portfolioproject.oppstart)

            if project.fremskritt.planlagt_ferdig:
                if isinstance(project.fremskritt.planlagt_ferdig, (datetime, date)):
                    project.fremskritt.planlagt_ferdig = project.fremskritt.planlagt_ferdig.strftime("%Y-%m-%d")
                else:
                    project.fremskritt.planlagt_ferdig = str(project.fremskritt.planlagt_ferdig)

            if not project.resursbehov.risiko_av_estimat:
                project.resursbehov.risiko_av_estimat = ""

            # --- Handle epost and kontaktpersoner ---
            if project.portfolioproject.tiltakseier:
                project.portfolioproject.epost_kontakt = str([brukere[project.portfolioproject.tiltakseier]])

            if len(project.portfolioproject.kontaktpersoner) > 0 and isinstance(project.portfolioproject.kontaktpersoner[0], str):
                kontakt_epost = [brukere.get(i) for i in project.portfolioproject.kontaktpersoner]
                project.portfolioproject.kontaktpersoner = str(project.portfolioproject.kontaktpersoner)
                if project.portfolioproject.tiltakseier:
                    project.portfolioproject.epost_kontakt = str([brukere[project.portfolioproject.tiltakseier]])
                    epost_list = ast.literal_eval(project.portfolioproject.epost_kontakt)
                else:
                    epost_list = []
                if epost_list and epost_list[0] not in kontakt_epost:
                    epost_list.extend(kontakt_epost)
                else:
                    epost_list = kontakt_epost
                project.portfolioproject.epost_kontakt = str(epost_list)

            # --- Save project (run in background thread if heavy) ---
            await run.io_bound(db_connector.update_project, project, email)

            ui.notify("✅ Endringer lagret i databasen!", type="positive", position="top")

            # Slight pause to let the user see success message before redirect
            await asyncio.sleep(0.2)
            ui.navigate.to("/oppdater_prosjekt")

        except Exception as e:
            ui.notify(f"❌ Feil under lagring: {e}", type="negative", position="top")

        finally:
            dialog.close()

    ui.button("💾 Save", on_click=check_or_update).classes("mt-4")
