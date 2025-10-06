from nicegui import ui, app, Client
from typing import Any
from utils.project_loader import diff_projects

avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS']
def project_detail(prosjekt_id: str, ORIGINAL_PROJECTS:dict, email:str):


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
            with ui.input(oppstart_date) as date:
                with ui.menu().props('no-parent-event') as menu:
                    with ui.date().bind_value(date):
                        with ui.row().classes('justify-end'):
                            ui.button('Close', on_click=menu.close).props('flat')
                with date.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-2 row-start-5'):
            ui.label("Planlagt ferdig").classes('text-lg font-bold')
            ferdig_date = str(project.ferdig_tid.date()) if project.ferdig_tid else None
            with ui.input(ferdig_date) as date:
                with ui.menu().props('no-parent-event') as menu:
                    with ui.date().bind_value(date):
                        with ui.row().classes('justify-end'):
                            ui.button('Close', on_click=menu.close).props('flat')
                with date.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
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
            manedsverk_intern = project.månedsverk_interne if type(project.månedsverk_interne) == int else 0
            inputs['månedsverk_interne'] = ui.input(value=manedsverk_intern).props('type=number min=0').classes('w-full')
        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-7'):
            ui.label("Månedsverk eksternt").classes('text-lg font-bold')
            manedsverk_ekstern = project.månedsverk_eksterne if type(project.månedsverk_eksterne) == int else 0
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
            estimat_liste = ["Relativt sikkert","Noe usikkert","Svart usikkert"]
            selected_estimat = project.hvor_sikkert_estimatene if project.hvor_sikkert_estimatene in estimat_liste else None
            inputs['hvor_sikkert_estimatene'] = ui.select(estimat_liste, value=selected_estimat).classes('w-full')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-7'):
            ui.label('Forklaring estimat').classes('text-lg font-bold')
            inputs['estimert_behov_forklaring'] = ui.textarea(value=project.estimert_behov_forklaring)


    ui.markdown(f"## *Tilknytning til andre strategier*")
    with ui.grid(columns=5).classes("w-full gap-5"):
        mal_kategorier = ["Lite relevant","Noe bidrag til mål","Viktigste mål"]
        ui.label("Mål for digitalisering").classes('col-span-1 row-span-1 col-start-1 row-start-1 text-lg font-bold')
        ui.label("Mål 1: Digitalisering i offentlig sektor er samordnet og samfinnsnyttig").classes('col-span-1 row-span-1 col-start-1 row-start-2')
        inputs['mål_1_tildelingsbrevet'] = ui.select(mal_kategorier, value=project.mål_1_tildelingsbrevet).classes('col-span-2 row-span-1 col-start-2 row-start-2')
        ui.label("Mål 2: Digdirs fellesløsninger er samfunnsnyttige, sikre og enkle å tå i bruk").classes('col-span-1 row-span-1 col-start-1 row-start-3')
        inputs['mål_2_tildelingsbrevet'] = ui.select(mal_kategorier, value=project.mål_2_tildelingsbrevet).classes('col-span-2 row-span-1 col-start-2 row-start-3')
        ui.label("Mål 3: Digitale tjenester er tilgjengelig for alle").classes('col-span-1 row-span-1 col-start-1 row-start-4')
        inputs['mål_3_tildelingsbrevet'] = ui.select(mal_kategorier, value=project.mål_3_tildelingsbrevet).classes('col-span-2 row-span-1 col-start-2 row-start-4')

        with ui.element("div").classes('col-span-2 row-span-2 col-start-4 row-start-2'):
            ui.label('Sammenheng med Digitaliseringsstrategien').classes('text-lg font-bold')
            inputs['sammenheng_med_digitaliseringsstrategien_mm'] = ui.textarea(value=project.sammenheng_med_digitaliseringsstrategien_mm).classes('w-full')
    print(inputs,project)