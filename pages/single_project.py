from nicegui import ui, run
from typing import Any
from utils.project_loader import diff_projects, ProjectData, get_engine, apply_changes, update_project_from_diffs, get_single_project_data, create_empty_project
from uuid import UUID
from datetime import datetime
import ast
import json
from utils.azure_users import load_users
from utils.db_connection import DBConnector


brukere = load_users()
brukere_list = list(brukere.keys())
avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS']
def project_detail(db_connector: DBConnector, prosjekt_id: str, email: str, user_name: str, new: bool = False):
    if new:
        project = create_empty_project(email,user_name=user_name, pid=prosjekt_id)
    else:
        prosjet_list = db_connector.get_single_project(prosjekt_id)
        if not prosjet_list:
            ui.label('Project not found or you do not have access to it.')
            return
        project =  prosjet_list.model_copy(deep=True)



    ui.markdown(f"## *Porteføljeinitiativ: {project.navn_tiltak}*").classes('text-xl font-bold')
    inputs: dict[str, Any] = {}
    # show all fields as key/value
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("1. Grunninformasjon").classes('col-span-1 row-span-1 col-start-1 row-start-3 text-lg font-bold underline mt-4 mb-2')
        with ui.element("div").classes('col-span-2 row-span-1 col-start-2 row-start-3'):
            ui.label("Navn på tiltak").classes('text-lg font-bold')
            inputs['navn_tiltak'] = ui.input(value=project.navn_tiltak).classes('w-full bg-white rounded-lg')
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-4'):
            ui.label("Tiltakseier").classes('text-lg font-bold')
            inputs['tiltakseier'] = ui.select(brukere_list, with_input=True, multiple=False,value=project.tiltakseier, validation= lambda value: "Du må velge en tiltakseier" if value == None else None).props(
                    "outlined dense clearable options-dense color=primary").classes(
                        "w-full bg-white rounded-lg").props('use-chips')
 
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-5'):
            ui.label("Kontaktpersoner").classes('text-lg font-bold')
            kontakt_person = ast.literal_eval(project.kontaktperson) if "[" in project.kontaktperson else None
            inputs['kontaktperson'] = ui.select(brukere_list, with_input=True, multiple=True,value=kontakt_person).props(
                    "clearable options-dense color=primary").classes("w-full bg-white rounded-lg").props('use-chips')


        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-6'):
            ui.label('Hovedavdeling').classes('text-lg font-bold')
            inputs['avdeling'] = ui.radio(
                avdelinger,  # <-- your real avdelinger
                value=project.avdeling
            ).props("inline")
        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-7'):
            ui.label('Samarbeid internt').classes('text-lg font-bold')
            try:
                samarbeid_intern_list = json.loads(project.samarbeid_intern)
            except (TypeError, json.JSONDecodeError):
                samarbeid_intern_list = []

            inputs["samarbeid_intern"] = ui.select(
                avdelinger,
                multiple=True,
                value=samarbeid_intern_list
            ).props("use-chips").classes("w-full bg-white rounded-lg")

        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-7'):
            ui.label('Samarbeid eksternt').classes('text-lg font-bold')
            inputs["samarbeid_eksternt"] = ui.input(value=project.samarbeid_eksternt).classes('w-full bg-white rounded-lg')

        with ui.element("div").classes('col-span-3 row-span-2 col-start-4 row-start-6'):
            ui.label("Avhengigheter andre").classes('text-lg font-bold')
            inputs['avhengigheter_andre'] = ui.textarea(value=project.avhengigheter_andre).classes('w-full bg-white rounded-lg')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-4'):
            ui.label("Hvilken fase skal startes").classes('text-lg font-bold')
            inputs['fase_tiltak'] = ui.select(
                ['Konsept', 'Planlegging', 'Gjennomføring','Problem/ide'],
                value=project.fase_tiltak
                ).classes('w-full bg-white rounded-lg')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-5'):
            ui.label('Start').classes('text-lg font-bold')
            oppstart_date = str(project.oppstart_tid.date()) if project.oppstart_tid else None
            with ui.input(value=oppstart_date, placeholder='Velg dato').classes('bg-white rounded-lg') as oppstart_input:
                with oppstart_input.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: oppstart_menu.open()).classes('cursor-pointer')
                with ui.menu().props('no-parent-event') as oppstart_menu:
                    oppstart_date = ui.date(value=oppstart_date).props('mask=YYYY-MM-DD')
                    oppstart_date.bind_value(oppstart_input, 'value')
                    with ui.row().classes('justify-end'):
                        ui.button('Lukk', on_click=oppstart_menu.close).props('flat')

                inputs['oppstart_tid'] = oppstart_input
            
        with ui.element("div").classes('col-span-1 row-span-1 col-start-5 row-start-5'):
            ui.label("Planlagt ferdig").classes('text-lg font-bold')
            ferdig_date = str(project.ferdig_tid.date()) if project.ferdig_tid else None
            with ui.input(value=ferdig_date,  placeholder='Velg dato').classes('bg-white rounded-lg') as ferdig_input:
                with ferdig_input.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: ferdig_menu.open()).classes('cursor-pointer')
                with ui.menu().props('no-parent-event') as ferdig_menu:
                    ferdig_date = ui.date(value=ferdig_date).props('mask=YYYY-MM-DD')
                    ferdig_date.bind_value(ferdig_input, 'value')
                    with ui.row().classes('justify-end'):
                        ui.button('Lukk', on_click=ferdig_menu.close).props('flat')

            inputs['ferdig_tid'] = ferdig_input

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("2. Begrunnelse").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-5 row-span-2 col-start-1 row-start-3'):
            ui.label('Problemstilling').classes('text-lg font-bold')
            inputs['problemstilling'] = ui.textarea(value=project.problemstilling).classes('w-full bg-white rounded-lg')

        with ui.element("div").classes('col-span-5 row-span-2 col-start-1 row-start-5'):
            ui.label("Beskrivelse av prosjekt").classes('text-lg font-bold')
            inputs['beskrivelse'] = ui.textarea(value=project.beskrivelse).classes('w-full bg-white rounded-lg')

        with ui.element("div").classes('col-span-5 row-span-2 col-start-1 row-start-7'):
            ui.label('Risiko hvis tiltaket ikke gjennomføres').classes('text-lg font-bold')
            inputs['risiko'] = ui.textarea(value=project.risiko).classes('w-full bg-white rounded-lg')

 

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("3. Resursbehov").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-1 row-start-3'):
            ui.label("Hvilke kompetanser trenges for tiltaket?").classes('text-lg font-bold')
            inputs['kompetanse_behov'] = ui.textarea(value=project.kompetanse_behov).classes('w-full bg-white rounded-lg')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-3'):
            ui.label("Kompetanse internt").classes('text-lg font-bold')
            kompetanse_internt_list = ["Ja","Ja, men det er ikke tilstrekkelig kapasitet","Delvis","Nei"]
            selected_kompetanse = project.kompetanse_internt if project.kompetanse_internt in kompetanse_internt_list else None
            inputs['kompetanse_internt'] = ui.select(kompetanse_internt_list, value=selected_kompetanse).classes('w-full bg-white rounded-lg')
        
        ui.label("Estimert antall månedsverk for fasen").classes('text-lg font-bold col-span-1 row-span-1 col-start-1 row-start-5')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-6'):
            ui.label("Interne").classes('text-lg font-bold')
            manedsverk_intern = project.månedsverk_interne if type(project.månedsverk_interne) == int else None
            inputs['månedsverk_interne'] = ui.input(value=manedsverk_intern).props('type=number min=0').classes('w-full bg-white rounded-lg')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-2 row-start-6'):
            ui.label("Eksterne").classes('text-lg font-bold')
            manedsverk_ekstern = project.månedsverk_eksterne if type(project.månedsverk_eksterne) == int else None
            inputs['månedsverk_eksterne'] = ui.input(value=manedsverk_ekstern).props('type=number min=0').classes('w-full bg-white rounded-lg')

        
        ui.label("Estimert finansieringsbehov (eksl. interne ressurser)").classes('text-lg font-bold col-span-1 row-span-1 col-start-4 row-start-2')

        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-3'):
            ui.label('Estimert budsjett behov').classes('text-lg font-bold')
            inputs['estimert_behov_utover_driftsrammen'] = ui.input(value=project.estimert_behov_utover_driftsrammen).props('type=number min=0').classes('w-full bg-white rounded-lg')
            # , validation=lambda value: "Må være et tall" if not isinstance(value, int) else None
        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-4'):
            ui.label("Hvor sikkert er estimatet").classes('text-lg font-bold')
            estimat_liste = ["Relativt sikkert","Noe usikkert","Svært usikkert"]
            selected_estimat = project.hvor_sikkert_estimatene if project.hvor_sikkert_estimatene in estimat_liste else None
            inputs['hvor_sikkert_estimatene'] = ui.select(estimat_liste, value=selected_estimat).classes('w-full bg-white rounded-lg')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-5'):
            ui.label('Forklaring estimat').classes('text-lg font-bold')
            inputs['estimert_behov_forklaring'] = ui.textarea(value=project.estimert_behov_forklaring).classes('w-full bg-white rounded-lg')

    with ui.grid(columns=4).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("4. Tilknytning til andre strategier").classes('col-span-1 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        ui.label("Målbilde").classes('col-span-1 row-span-1 col-start-1 row-start-3 text-lg font-bold')
        ui.label("1 Vi fremmer samordning og prioritering for en mer effektiv offentlig sektor").classes('col-span-2 row-span-1 col-start-1 row-start-4 text-lg')
        inputs['malbilde_1_beskrivelse'] = ui.textarea(value=project.malbilde_1_beskrivelse).classes('col-span-2 row-span-2 col-start-1 row-start-5 bg-white rounded-lg')
        ui.label("2 Vi leder an i ansvarlig og innovativ bruk av data og kunstig intelligens").classes('col-span-2 row-span-1 col-start-3 row-start-4 text-lg')
        inputs['malbilde_2_beskrivelse'] = ui.textarea(value=project.malbilde_2_beskrivelse).classes('col-span-2 row-span-2 col-start-3 row-start-5 bg-white rounded-lg')
        ui.label("3 Vi sikrer trygg tilgang til digitale tjenester for alle").classes('col-span-2 row-span-1 col-start-1 row-start-7 text-lg')
        inputs['malbilde_3_beskrivelse'] = ui.textarea(value=project.malbilde_3_beskrivelse).classes('col-span-2 row-span-2 col-start-1 row-start-8 bg-white rounded-lg')
        ui.label("4 Vi løser komplekse utfordringer sammen og tilpasser oss en verden i rask endring").classes('col-span-2 row-span-1 col-start-3 row-start-7 text-lg')
        inputs['malbilde_4_beskrivelse'] = ui.textarea(value=project.malbilde_4_beskrivelse).classes('col-span-2 row-span-2 col-start-3 row-start-8 bg-white rounded-lg')
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
            try:
                selected_keys = ast.literal_eval(project.sammenheng_med_digitaliseringsstrategien_mm)
            except (ValueError, SyntaxError):
                selected_keys = project.sammenheng_med_digitaliseringsstrategien_mm = []
            # selected_keys = project.sammenheng_med_digitaliseringsstrategien_mm or []
            selected_labels = [digitaliserings_strategi_digdir[i] for i in selected_keys if i in digitaliserings_strategi_digdir]
            inputs['sammenheng_med_digitaliseringsstrategien_mm'] = ui.select(list(digitaliserings_strategi_digdir.values()), 
                                                                              multiple=True, 
                                                                              value=selected_labels).classes('w-full bg-white rounded-lg')
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
        updated_data = {field: get_input_value(inp) for field, inp in inputs.items()}

        updated_data["prosjekt_id"] = UUID(prosjekt_id)
        edited_project = project.model_copy(update=updated_data)
        if edited_project.samarbeid_intern:
            edited_project.samarbeid_intern = json.dumps(edited_project.samarbeid_intern)
        if edited_project.oppstart_tid:
            edited_project.oppstart_tid = datetime.strptime(edited_project.oppstart_tid , "%Y-%m-%d")
        if edited_project.ferdig_tid:
            edited_project.ferdig_tid = datetime.strptime(edited_project.ferdig_tid , "%Y-%m-%d")
        if not edited_project.hvor_sikkert_estimatene:
            edited_project.hvor_sikkert_estimatene = ""
        if len(edited_project.sammenheng_med_digitaliseringsstrategien_mm) > 0 and isinstance(edited_project.sammenheng_med_digitaliseringsstrategien_mm[0], str):
            # reverse_digdir = {v: k for k, v in digitaliserings_strategi_digdir.items()}
            edited_project.sammenheng_med_digitaliseringsstrategien_mm = str([reverse_digdir[label] for label in edited_project.sammenheng_med_digitaliseringsstrategien_mm if label in reverse_digdir])
        if not edited_project.tiltakseier or edited_project.tiltakseier.strip() == "":
            ui.notify("❌ Du må fylle inn tiltakseier.", type="warning", position="top", close_button="OK")
            return
        edited_project.eier_epost = str([brukere[edited_project.tiltakseier]])
        if not edited_project.navn_tiltak or edited_project.navn_tiltak.strip() == "":
            ui.notify("❌ Du må fylle inn tiltaksnavn.", type="warning", position="top", close_button="OK")
            return
        if len(edited_project.kontaktperson) > 0 and isinstance(edited_project.kontaktperson[0], str):
            kontakt_epost = [brukere.get(i) for i in edited_project.kontaktperson]
            edited_project.kontaktperson = str(edited_project.kontaktperson)
            epost_list = ast.literal_eval(edited_project.eier_epost)
            if epost_list[0] not in kontakt_epost:
                epost_list.extend(kontakt_epost)
                edited_project.eier_epost = str(epost_list)
            else:
                edited_project.eier_epost = str(kontakt_epost)
        edited_project.endret_av = user_name

        diffs = diff_projects([project],[edited_project])
        if not diffs:
            ui.notify('No changes made.')
            return
        await run.io_bound(db_connector.update_project, new, diffs, user_name) 
        ui.navigate.to(f"/oppdater_prosjekt")
        ui.notify('Changes saved to database!')

    ui.button("💾 Save", on_click=update_data).classes("mt-4")
