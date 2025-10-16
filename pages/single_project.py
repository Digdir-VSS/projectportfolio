from nicegui import ui, app, Client
from typing import Any
from utils.project_loader import diff_projects, ProjectData, engine, apply_changes, update_project_from_diffs, get_single_project_data, create_empty_project
from sqlmodel import Session
from uuid import UUID
from datetime import datetime
avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS']
def project_detail(prosjekt_id: str, email: str, new: bool = False):
    if new:
        project = create_empty_project(email, pid=prosjekt_id)
    else:
        with Session(engine) as session:
            prosjet_list = get_single_project_data(session, prosjekt_id)
            print(prosjet_list)
            if prosjet_list:
                project =  prosjet_list.model_copy(deep=True)

        if not prosjet_list:
            ui.label('Project not found or you do not have access to it.')
            return
    # get all data for this project
    # print(ORIGINAL_PROJECTS)
    # project = ORIGINAL_PROJECTS[email].get(prosjekt_id)

    # project = next((p for p in projects if str(p.prosjekt_id) == prosjekt_id), None)



    ui.markdown(f"## *{project.navn_tiltak or prosjekt_id}*")

    inputs: dict[str, Any] = {}
    # show all fields as key/value
    with ui.grid(columns=5).classes("w-full gap-5"):
        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-1'):
            ui.label("Navn prosjekt").classes('text-lg font-bold')
            inputs['navn_tiltak'] = ui.input(value=project.navn_tiltak).classes('w-full')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-2 row-start-1'):
            ui.label("Kontaktperson").classes('text-lg font-bold')
            inputs['kontaktperson'] = ui.input(value=project.kontaktperson).classes('w-full')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-1'):
            ui.label("Epost kontaktperson").classes('text-lg font-bold')
            inputs["eier_epost"] = ui.input(value=project.eier_epost).classes('w-full')

        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-2'):
            ui.label('Hovedavdeling').classes('text-lg font-bold')
            inputs['avdeling'] = ui.radio(
                avdelinger,  # <-- your real avdelinger
                value=project.avdeling
            ).props("inline")
        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-3'):
            ui.label('Samarbeid internt').classes('text-lg font-bold')
            inputs["samarbeid_internt"] = ui.select(avdelinger, multiple=True, value=project.samarbeid_intern.split(',') if project.samarbeid_intern else []).classes('w-full')
        
        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-3'):
            ui.label('Samarbeid eksternt').classes('text-lg font-bold')
            inputs["samarbeid_eksternt"] = ui.input(value=project.samarbeid_eksternt)
        
        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-1'):
            ui.label("Beskrivelse av prosjekt").classes('text-lg font-bold')
            inputs['beskrivelse'] = ui.textarea(value=project.beskrivelse)
        
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-4'):
            ui.label("Avhengigheter andre").classes('text-lg font-bold')
            inputs['avhengigheter_andre'] = ui.textarea(value=project.avhengigheter_andre).classes('w-full')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-5'):
            ui.label('Start').classes('text-lg font-bold')
            oppstart_date = str(project.oppstart_tid.date()) if project.oppstart_tid else None
            with ui.input(value=oppstart_date, placeholder='Velg dato') as oppstart_input:
                with oppstart_input.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: oppstart_menu.open()).classes('cursor-pointer')
                with ui.menu().props('no-parent-event') as oppstart_menu:
                    oppstart_date = ui.date(value=oppstart_date).props('mask=YYYY-MM-DD')
                    oppstart_date.bind_value(oppstart_input, 'value')
                    with ui.row().classes('justify-end'):
                        ui.button('Lukk', on_click=oppstart_menu.close).props('flat')

                inputs['oppstart_tid'] = oppstart_input

        with ui.element("div").classes('col-span-1 row-span-1 col-start-2 row-start-5'):
            ui.label("Planlagt ferdig").classes('text-lg font-bold')
            ferdig_date = str(project.ferdig_tid.date()) if project.ferdig_tid else None
            with ui.input(value=ferdig_date,  placeholder='Velg dato') as ferdig_input:
                with ferdig_input.add_slot('append'):
                    ui.icon('edit_calendar').on('click', lambda: ferdig_menu.open()).classes('cursor-pointer')
                with ui.menu().props('no-parent-event') as ferdig_menu:
                    ferdig_date = ui.date(value=ferdig_date).props('mask=YYYY-MM-DD')
                    ferdig_date.bind_value(ferdig_input, 'value')
                    with ui.row().classes('justify-end'):
                        ui.button('Lukk', on_click=ferdig_menu.close).props('flat')

            inputs['ferdig_tid'] = ferdig_input
            # with ui.input(ferdig_date) as date:
            #     with ui.menu().props('no-parent-event') as menu:
            #         with ui.date().bind_value(date) as d:
            #             with ui.row().classes('justify-end'):
            #                 ui.button('Close', on_click=menu.close).props('flat')

            #     with date.add_slot('append'):
            #         ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                # ferdig_tid = ui.date(value=ferdig_date).props('mask=YYYY-MM-DD')
                # inputs['ferdig_tid'] =date.label
 
        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-5'):
            ui.label("Fase tiltak").classes('text-lg font-bold')
            inputs['fase_tiltak'] = ui.select(
                ['Konsept', 'Planlegging', 'Gjennomføring','Problem/ide'],
                value=project.fase_tiltak
                )
        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-3'):
            ui.label('Problemstilling').classes('text-lg font-bold')
            inputs['problemstilling'] = ui.textarea(value=project.problemstilling).classes('w-full')
        
        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-6'):
            ui.label("Kompetansebehov").classes('text-lg font-bold')
            inputs['kompetanse_behov'] = ui.textarea(value=project.kompetanse_behov).classes('w-full')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-7'):
            ui.label("Kompetanse internt").classes('text-lg font-bold')
            kompetanse_internt_list = ["Ja","Ja, men det er ikke tilstrekkelig kapasitet","Delvis","Nei"]
            selected_kompetanse = project.kompetanse_internt if project.kompetanse_internt in kompetanse_internt_list else None
            inputs['kompetanse_internt'] = ui.select(kompetanse_internt_list, value=selected_kompetanse).classes('w-full')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-2 row-start-7'):
            ui.label("Månedsverk internt").classes('text-lg font-bold')
            manedsverk_intern = project.månedsverk_interne if type(project.månedsverk_interne) == int else None
            inputs['månedsverk_interne'] = ui.input(value=manedsverk_intern).props('type=number min=0').classes('w-full')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-7'):
            ui.label("Månedsverk eksternt").classes('text-lg font-bold')
            manedsverk_ekstern = project.månedsverk_eksterne if type(project.månedsverk_eksterne) == int else None
            inputs['månedsverk_eksterne'] = ui.input(value=manedsverk_ekstern).props('type=number min=0').classes('w-full')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-5'):
            ui.label('Risikovurdering').classes('text-lg font-bold')
            inputs['risiko'] = ui.textarea(value=project.risiko)


        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-8'):
            ui.label('Estimert budsjett behov').classes('text-lg font-bold')
            inputs['estimert_behov_utover_driftsrammen'] = ui.input(value=project.estimert_behov_utover_driftsrammen).props('type=number min=0').classes('w-full')
            # , validation=lambda value: "Må være et tall" if not isinstance(value, int) else None
        with ui.element("div").classes('col-span-2 row-span-1 col-start-2 row-start-8'):
            ui.label("Hvor sikkert er estimatet").classes('text-lg font-bold')
            estimat_liste = ["Relativt sikkert","Noe usikkert","Svært usikkert"]
            selected_estimat = project.hvor_sikkert_estimatene if project.hvor_sikkert_estimatene in estimat_liste else None
            inputs['hvor_sikkert_estimatene'] = ui.select(estimat_liste, value=selected_estimat).classes('w-full')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-7'):
            ui.label('Forklaring estimat').classes('text-lg font-bold')
            inputs['estimert_behov_forklaring'] = ui.textarea(value=project.estimert_behov_forklaring)


    ui.markdown(f"## *Tilknytning til andre strategier*")
    with ui.grid(columns=4).classes("w-full gap-5"):
        ui.label("Målbilde og strategi").classes('col-span-1 row-span-1 col-start-1 row-start-1 text-lg font-bold')
        ui.label("Vi fremmer samordning og prioritering for en mer effektiv offentlig sektor").classes('col-span-2 row-span-1 col-start-1 row-start-2 text-lg')
        inputs['malbilde_1_beskrivelse'] = ui.textarea(value=project.malbilde_1_beskrivelse).classes('col-span-2 row-span-2 col-start-1 row-start-3')
        ui.label("Vi leder an i ansvarlig og innovativ bruk av data og kunstig intelligens").classes('col-span-2 row-span-1 col-start-3 row-start-2 text-lg')
        inputs['malbilde_2_beskrivelse'] = ui.textarea(value=project.malbilde_2_beskrivelse).classes('col-span-2 row-span-2 col-start-3 row-start-3')
        ui.label("Vi sikrer trygg tilgang til digitale tjenester for alle").classes('col-span-2 row-span-1 col-start-1 row-start-5 text-lg')
        inputs['malbilde_3_beskrivelse'] = ui.textarea(value=project.malbilde_3_beskrivelse).classes('col-span-2 row-span-2 col-start-1 row-start-6')
        ui.label("Vi løser komplekse utfordringer sammen og tilpasser oss en verden i rask endring").classes('col-span-2 row-span-1 col-start-3 row-start-5 text-lg')
        inputs['malbilde_4_beskrivelse'] = ui.textarea(value=project.malbilde_3_beskrivelse).classes('col-span-2 row-span-2 col-start-3 row-start-6')
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
        with ui.element("div").classes('col-span-2 row-span-2 col-start-1 row-start-8'):
            ui.label('Sammenheng med Digitaliseringsstrategien').classes('text-lg font-bold')
            selected_keys = project.sammenheng_med_digitaliseringsstrategien_mm or []
            selected_labels = [digitaliserings_strategi_digdir[i] for i in selected_keys if i in digitaliserings_strategi_digdir]

            inputs['sammenheng_med_digitaliseringsstrategien_mm'] = ui.select(list(digitaliserings_strategi_digdir.values()), 
                                                                              multiple=True, 
                                                                              value=selected_labels).classes('w-full')
            # inputs['sammenheng_med_digitaliseringsstrategien_mm'] = ui.textarea(value=project.sammenheng_med_digitaliseringsstrategien_mm).classes('w-full')

    # def get_input_value(inp):
    #     # Try the most common attributes first
    #     for attr in ("value", "text", "label"):
    #         if hasattr(inp, attr):
    #             val = getattr(inp, attr)
    #             # Normalize strings: strip spaces and treat empty as None
    #             if isinstance(val, str):
    #                 val = val.strip()
    #                 if val == "":
    #                     val = None
    #             return val
    #     # Some UI elements might use 'checked' (checkboxes)
    #     if hasattr(inp, "checked"):
    #         return inp.checked
    #     # If no known value field, return None
    #     return None
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


    def update_data():
        updated_data = {field: get_input_value(inp) for field, inp in inputs.items()}
        # for field, inp in inputs.items():
        #     if inp.label:
        #         updated_data[field] = inp.label
        #     else:
        #         updated_data[field] = inp.value if inp.value != "" else None
        # {field: inp.label if inp.value == "" else inp.value for field, inp in inputs.items()}
        updated_data["prosjekt_id"] = UUID(prosjekt_id)
        # updated_data["eier_epost"] = project.eier_epost  # do not allow changing owner here
        # list_fields = [inp.label if inp.value == "" else inp.value for field, inp in inputs.items()]
        # edited_project = ProjectData(**updated_data)
        edited_project = project.model_copy(update=updated_data)

        if edited_project.oppstart_tid:
            edited_project.oppstart_tid = datetime.strptime(edited_project.oppstart_tid , "%Y-%m-%d")
        if edited_project.ferdig_tid:
            edited_project.ferdig_tid = datetime.strptime(edited_project.ferdig_tid , "%Y-%m-%d")
        if not edited_project.hvor_sikkert_estimatene:
            edited_project.hvor_sikkert_estimatene = ""
        if len(edited_project.sammenheng_med_digitaliseringsstrategien_mm) > 0 and isinstance(edited_project.sammenheng_med_digitaliseringsstrategien_mm[0], str):
            reverse_digdir = {v: k for k, v in digitaliserings_strategi_digdir.items()}
            edited_project.sammenheng_med_digitaliseringsstrategien_mm = [reverse_digdir[label] for label in edited_project.sammenheng_med_digitaliseringsstrategien_mm if label in reverse_digdir]
        # print([project], [edited_project])
        diffs = diff_projects([project],[edited_project])
        print(new)
        print(diffs)
        if not diffs:
            ui.notify('No changes made.')
            return
        with Session(engine) as session:
            if new:
                diffs[0]["changes"]["eier_epost"] = {"old": None, "new": updated_data["eier_epost"]}
                apply_changes(diffs, session, new=new)
                
                ui.navigate.to(f"/project/{prosjekt_id}")
            else:
                apply_changes(diffs, session)
                update_project_from_diffs(project=project, diffs=diffs)

            ui.notify('Changes saved to database!')
        # diff_projects(dict(project), updated_data)
        # print(diff_projects)
    ui.button("💾 Save", on_click=update_data).classes("mt-4")
