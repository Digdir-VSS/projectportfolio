from nicegui import ui, run
from typing import Any
from utils.project_loader import diff_projects
from uuid import UUID
from datetime import datetime
import ast
import json
from utils.azure_users import load_users
from utils.db_connection import DBConnector

def to_list(value: str | None):
    """Convert stored JSON string to Python list for the UI."""
    try:
        return json.loads(value) if value else []
    except json.JSONDecodeError:
        return []

def to_json(value: list[str] | None):
    """Convert UI list back to JSON string for the dataclass."""
    return json.dumps(value or [])


brukere = load_users()
brukere_list = list(brukere.keys())
avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS']
def project_detail(db_connector: DBConnector, prosjekt_id: str, email: str, user_name: str, new: bool = False):
    if new:
        project = db_connector.create_empty_project(email=email,user_name=user_name, prosjekt_id=prosjekt_id)
    else:
        project = db_connector.get_single_project(prosjekt_id)
        if not project:
            ui.label('Project not found or you do not have access to it.')
            return
    print(project)
    ui.markdown(f"## *Porteføljeinitiativ: {project.portfolioproject.navn}*").classes('text-xl font-bold')
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("1. Grunninformasjon").classes('col-span-1 row-span-1 col-start-1 row-start-3 text-lg font-bold underline mt-4 mb-2')
        with ui.element("div").classes('col-span-2 row-span-1 col-start-2 row-start-3'):
            ui.label("Navn på tiltak").classes('text-lg font-bold')
            project.portfolioproject.navn = ui.input(value=project.portfolioproject.navn).classes('w-full bg-white rounded-lg')
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-4'):
            ui.label("Tiltakseier").classes('text-lg font-bold')
            ui.select(brukere_list, with_input=True, multiple=False, validation= lambda value: "Du må velge en tiltakseier" if value == None else None).props(
                    "outlined dense clearable options-dense color=primary").classes(
                        "w-full bg-white rounded-lg").props('use-chips').bind_value(project.portfolioproject, "navn")
 
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-5'):
            ui.label("Kontaktpersoner").classes('text-lg font-bold')
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
            ui.label("Avhengigheter andre").classes('text-lg font-bold')
            ui.textarea().classes('w-full bg-white rounded-lg').bind_value(project.samarabeid, "avhengigheter_andre")

        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-4'):
            ui.label("Hvilken fase skal startes").classes('text-lg font-bold')
            ui.select(
                ['Konsept', 'Planlegging', 'Gjennomføring','Problem/ide'],
                ).classes('w-full bg-white rounded-lg').bind_value(project.fremskritt, "fase")
        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-5'):
            ui.label('Start').classes('text-lg font-bold')
            oppstart_date = str(project.portfolioproject.oppstart.date()) if project.portfolioproject.oppstart else None
            with ui.input(value=oppstart_date, placeholder='Velg dato').classes('bg-white rounded-lg') as oppstart_input:
                with oppstart_input.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: oppstart_menu.open()).classes('cursor-pointer')
                with ui.menu().props('no-parent-event') as oppstart_menu:
                    oppstart_date = ui.date(value=oppstart_date).props('mask=YYYY-MM-DD')
                    oppstart_date.bind_value(oppstart_input, 'value')
                    with ui.row().classes('justify-end'):
                        ui.button('Lukk', on_click=oppstart_menu.close).props('flat')

                project.portfolioproject.oppstart  = oppstart_input
            
        with ui.element("div").classes('col-span-1 row-span-1 col-start-5 row-start-5'):
            ui.label("Planlagt ferdig").classes('text-lg font-bold')
            ferdig_date = str(project.fremskritt.planlagt_ferdig.date()) if project.fremskritt.planlagt_ferdig else None
            with ui.input(value=ferdig_date,  placeholder='Velg dato').classes('bg-white rounded-lg') as ferdig_input:
                with ferdig_input.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: ferdig_menu.open()).classes('cursor-pointer')
                with ui.menu().props('no-parent-event') as ferdig_menu:
                    ferdig_date = ui.date(value=ferdig_date).props('mask=YYYY-MM-DD')
                    ferdig_date.bind_value(ferdig_input, 'value')
                    with ui.row().classes('justify-end'):
                        ui.button('Lukk', on_click=ferdig_menu.close).props('flat')

            project.fremskritt.planlagt_ferdig = ferdig_input

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("2. Begrunnelse").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-5 row-span-2 col-start-1 row-start-3'):
            ui.label('Problemstilling').classes('text-lg font-bold')
            ui.textarea(value=project.problemstilling.problem).classes('w-full bg-white rounded-lg').bind_value(project.problemstilling, "problem")

        with ui.element("div").classes('col-span-5 row-span-2 col-start-1 row-start-5'):
            ui.label("Beskrivelse av prosjekt").classes('text-lg font-bold')
            ui.textarea(value=project.tiltak.tiltak_beskrivelse).classes('w-full bg-white rounded-lg').bind_value(project.tiltak, "tiltak_beskrivelse")

        with ui.element("div").classes('col-span-5 row-span-2 col-start-1 row-start-7'):
            ui.label('Risiko hvis tiltaket ikke gjennomføres').classes('text-lg font-bold')
            ui.textarea(value=project.risikovurdering.vurdering).classes('w-full bg-white rounded-lg').bind_value(project.risikovurdering, "vurdering")

 

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("3. Resursbehov").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-1 row-start-3'):
            ui.label("Hvilke kompetanser trenges for tiltaket?").classes('text-lg font-bold')
            ui.textarea().classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "kompetanse_som_trengs")

        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-3'):
            ui.label("Kompetanse internt").classes('text-lg font-bold')
            kompetanse_internt_list = ["Ja","Ja, men det er ikke tilstrekkelig kapasitet","Delvis","Nei"]
            selected_kompetanse = project.resursbehov.kompetanse_tilgjengelig  if project.resursbehov.kompetanse_tilgjengelig in kompetanse_internt_list else None
            project.resursbehov.kompetanse_tilgjengelig = ui.select(kompetanse_internt_list, value=selected_kompetanse).classes('w-full bg-white rounded-lg')
        
        ui.label("Estimert antall månedsverk for fasen").classes('text-lg font-bold col-span-1 row-span-1 col-start-1 row-start-5')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-6'):
            ui.label("Interne").classes('text-lg font-bold')
            if isinstance(project.resursbehov.antall_mandsverk_intern, float) or isinstance(project.resursbehov.antall_mandsverk_intern, str) or isinstance(project.resursbehov.antall_mandsverk_intern, int):
                antall_mandsverk_intern = int(project.resursbehov.antall_mandsverk_intern)
            else:
                antall_mandsverk_intern = None
            project.resursbehov.antall_mandsverk_intern = ui.input(value=antall_mandsverk_intern).props('type=number min=0').classes('w-full bg-white rounded-lg')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-2 row-start-6'):
            ui.label("Eksterne").classes('text-lg font-bold')
            if isinstance(project.resursbehov.antall_mandsverk_ekstern, float) or isinstance(project.resursbehov.antall_mandsverk_ekstern, str) or isinstance(project.resursbehov.antall_mandsverk_intern, int):
                antall_mandsverk_ekstern = int(project.resursbehov.antall_mandsverk_ekstern)
            else:
                antall_mandsverk_ekstern = None
            project.resursbehov.antall_mandsverk_ekstern = ui.input(value=antall_mandsverk_ekstern).props('type=number min=0').classes('w-full bg-white rounded-lg')

        
        ui.label("Estimert finansieringsbehov (eksl. interne ressurser)").classes('text-lg font-bold col-span-1 row-span-1 col-start-4 row-start-2')

        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-3'):
            ui.label('Estimert budsjett behov').classes('text-lg font-bold')
            project.resursbehov.estimert_budsjet_behov = ui.input(value=project.resursbehov.estimert_budsjet_behov).props('type=number min=0').classes('w-full bg-white rounded-lg')
            # , validation=lambda value: "Må være et tall" if not isinstance(value, int) else None
        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-4'):
            ui.label("Hvor sikkert er estimatet").classes('text-lg font-bold')
            estimat_liste = ["Relativt sikkert","Noe usikkert","Svært usikkert"]
            selected_estimat = project.resursbehov.risiko_av_estimat if project.resursbehov.risiko_av_estimat in estimat_liste else None
            project.resursbehov.risiko_av_estimat = ui.select(estimat_liste, value=selected_estimat).classes('w-full bg-white rounded-lg')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-5'):
            ui.label('Forklaring estimat').classes('text-lg font-bold')
            ui.textarea(value=project.resursbehov.estimert_budsjet_forklaring).classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "estimert_budsjet_forklaring")

    with ui.grid(columns=4).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("4. Tilknytning til andre strategier").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        ui.label("Målbilde").classes('col-span-1 row-span-1 col-start-1 row-start-3 text-lg font-bold')
        ui.label("1 Vi fremmer samordning og prioritering for en mer effektiv offentlig sektor").classes('col-span-2 row-span-1 col-start-1 row-start-4 text-lg')
        project.malbilde.malbilde_1_beskrivelse = ui.textarea(value=project.malbilde.malbilde_1_beskrivelse).classes('col-span-2 row-span-2 col-start-1 row-start-5 bg-white rounded-lg')
        ui.label("2 Vi leder an i ansvarlig og innovativ bruk av data og kunstig intelligens").classes('col-span-2 row-span-1 col-start-3 row-start-4 text-lg')
        project.malbilde.malbilde_2_beskrivelse = ui.textarea(value=project.malbilde.malbilde_2_beskrivelse).classes('col-span-2 row-span-2 col-start-3 row-start-5 bg-white rounded-lg')
        ui.label("3 Vi sikrer trygg tilgang til digitale tjenester for alle").classes('col-span-2 row-span-1 col-start-1 row-start-7 text-lg')
        project.malbilde.malbilde_3_beskrivelse = ui.textarea(value=project.malbilde.malbilde_3_beskrivelse).classes('col-span-2 row-span-2 col-start-1 row-start-8 bg-white rounded-lg')
        ui.label("4 Vi løser komplekse utfordringer sammen og tilpasser oss en verden i rask endring").classes('col-span-2 row-span-1 col-start-3 row-start-7 text-lg')
        project.malbilde.malbilde_4_beskrivelse = ui.textarea(value=project.malbilde.malbilde_4_beskrivelse).classes('col-span-2 row-span-2 col-start-3 row-start-8 bg-white rounded-lg')
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
            "114": "114: følge opp Handlingsplan for auka inkludering i eit digitalt samfunn",
            "115": "115: styrke innsatsen for å øke den digitale kompetansen hos seniorer",
            "116": "116: styrke arbeidet med brukskvalitet, klarspråk og universell utforming i offentlige digitale tjenester",
            "118": "118: sikre økt brukerinvolvering ved utvikling av digitale tjenester"
        }
        reverse_digdir = {v: k for k, v in digitaliserings_strategi_digdir.items()}
        with ui.element("div").classes('col-span-4 row-span-2 col-start-1 row-start-10'):
            ui.label('Sammenheng med Digitaliseringsstrategien').classes('text-lg font-bold')
            ui.select(list(digitaliserings_strategi_digdir.values()), multiple=True).classes('w-full bg-white rounded-lg').bind_value(project.digitaliseringstrategi, "sammenheng_digital_strategi", forward=to_json, backward=to_list)


    def get_input_value(inp):
        """
        Extracts the value from various NiceGUI UI elements.
        Handles text, select, checkbox, and date inputs.
        """
        # Handle Select
        if hasattr(inp, "value"):
            # Normal text, select, or textarea input
            val = inp.value
            if val is not None:
                return val.strip() if isinstance(val, str) else val

        # Handle text-only label-based inputs (some types expose .label instead)
        if hasattr(inp, "label") and not hasattr(inp, "value"):
            val = inp.label
            if val is not None:
                return val.strip() if isinstance(val, str) else val

        # Handle nested Date input inside an Input
        if hasattr(inp, "default_slot_children"):
            for child in inp.default_slot_children:
                # The nested date picker lives inside this slot
                if hasattr(child, "value") and hasattr(child, "mask") and "YYYY" in getattr(child, "mask", ""):
                    return child.value  # Return actual selected date

        # Handle checkbox (returns bool)
        if hasattr(inp, "checked"):
            return inp.checked

        return None


    async def update_data():
        print(project.samarabeid)
        project.samarabeid = {field: get_input_value(inp) for field, inp in project.samarabeid.to_dict().items()}

        if project.samarabeid.samarbeid_intern:
            project.samarabeid.samarbeid_intern = json.dumps(project.samarabeid.samarbeid_intern)
        if project.portfolioproject.oppstart:
            project.portfolioproject.oppstart = datetime.strptime(project.portfolioproject.oppstart, "%Y-%m-%d")
        if project.fremskritt.planlagt_ferdig:
            project.fremskritt.planlagt_ferdig = datetime.strptime(project.fremskritt.planlagt_ferdig , "%Y-%m-%d")
        if not project.resursbehov.risiko_av_estimat:
            project.resursbehov.risiko_av_estimat = ""
        if len(project.digitaliseringstrategi.sammenheng_digital_strategi) > 0 and isinstance(project.digitaliseringstrategi.sammenheng_digital_strategi[0], str):
            # reverse_digdir = {v: k for k, v in digitaliserings_strategi_digdir.items()}
            project.digitaliseringstrategi.sammenheng_digital_strategi = str([reverse_digdir[label] for label in project.digitaliseringstrategi.sammenheng_digital_strategi if label in reverse_digdir])
        if not project.portfolioproject.tiltakseier or project.portfolioproject.tiltakseier.strip() == "":
            ui.notify("❌ Du må fylle inn tiltakseier.", type="warning", position="top", close_button="OK")
            return
        project.portfolioproject.epost_kontakt = str([brukere[project.portfolioproject.tiltakseier]])
        if not project.portfolioproject.navn or project.portfolioproject.nav.strip() == "":
            ui.notify("❌ Du må fylle inn tiltaksnavn.", type="warning", position="top", close_button="OK")
            return
        if len(project.portfolioproject.kontaktpersoner) > 0 and isinstance(project.portfolioproject.kontaktpersoner[0], str):
            kontakt_epost = [brukere.get(i) for i in project.portfolioproject.kontaktpersoner]
            project.portfolioproject.kontaktpersoner = str(project.portfolioproject.kontaktpersoner)
            epost_list = ast.literal_eval(project.portfolioproject.epost_kontakt)
            if epost_list[0] not in kontakt_epost:
                epost_list.extend(kontakt_epost)
                project.portfolioproject.epost_kontakt = str(epost_list)
            else:
                project.portfolioproject.epost_kontakt = str(kontakt_epost)

        await run.io_bound(db_connector.update_project, new, diffs, user_name) 
        ui.navigate.to(f"/oppdater_prosjekt")
        ui.notify('Changes saved to database!')

    ui.button("💾 Save", on_click=update_data).classes("mt-4")
