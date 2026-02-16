from nicegui import ui, run
import ast
from frontend.utils.backend_client import api_update_project
from models.ui_models import ProjectData, RessursbrukUI
import ast, asyncio

from frontend.pages.utils import validate_send_schema
from models.validators import to_json, to_list, to_date_str, convert_to_int, add_thousand_split, convert_to_int_from_thousand_sign, sort_selected_values, to_datetime
from frontend.static_variables import DIGITALISERINGS_STRATEGI, ESTIMAT_LISTE, FASE
    
avdelinger = ['BOD','DSS' ,'KOM','FEL','STL' ,'TUU', 'VIS', 'KI Norge']
def project_detail(prosjekt_id: str, email: str, project: ProjectData, brukere_list):
    ui.markdown(f"## *Porteføljeinitiativ:* **{project.portfolioproject.navn}**").classes('text-xl font-bold')
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("1. Grunninformasjon").classes('col-span-1 row-span-1 col-start-1 row-start-3 text-lg font-bold underline mt-4 mb-2')
        with ui.element("div").classes('col-span-2 row-span-1 col-start-2 row-start-3'):
            ui.label("Navn på tiltak").classes('text-lg font-bold')
            ui.input(value=project.portfolioproject.navn).classes('w-full bg-white rounded-lg').bind_value(project.portfolioproject, "navn")
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-4'):
            ui.label("Tiltakseier (linjeleder)").classes('text-lg font-bold')
            ui.select(list(brukere_list.keys()), with_input=True, multiple=False, validation= lambda value: "Du må velge en tiltakseier" if value == None else None).props(
                    "outlined dense clearable options-dense color=primary").classes(
                        "w-full bg-white rounded-lg").props('use-chips').bind_value(project.portfolioproject, "tiltakseier")
        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-4'):
            ui.label("Hvilken fase skal startes").classes('text-lg font-bold')
            ui.select(
                FASE,value=None
                ).classes('w-full bg-white rounded-lg').bind_value(project.fremskritt, "fase")
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-5'):
            ui.label("Kontaktperson").classes('text-lg font-bold')
            ui.select(list(brukere_list.keys()), with_input=True, multiple=True, on_change=sort_selected_values).props(
                    "clearable options-dense color=primary").classes("w-full bg-white rounded-lg").props('use-chips').bind_value(project.portfolioproject, "kontaktpersoner", forward=to_json, backward=to_list)
        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-5'):
            ui.label('Start').classes('text-lg font-bold')
            ui.input().bind_value(project.portfolioproject, "oppstart", backward=to_date_str, forward=to_datetime).props("outlined dense type=date clearable color=primary").classes("w-full")
            
        with ui.element("div").classes('col-span-1 row-span-1 col-start-5 row-start-5'):
            ui.label("Planlagt ferdig").classes('text-lg font-bold')
            ui.input().bind_value(project.fremskritt, "planlagt_ferdig",backward=to_date_str, forward=to_datetime).props("outlined dense type=date clearable color=primary").classes("w-full")
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
                on_change=sort_selected_values
            ).props("use-chips").classes("w-full bg-white rounded-lg").bind_value(project.samarabeid, "samarbeid_intern", forward=to_json, backward=to_list)

        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-7'):
            ui.label('Samarbeid eksternt').classes('text-lg font-bold')
            ui.input().classes('w-full bg-white rounded-lg').bind_value(project.samarabeid, "samarbeid_eksternt")

        with ui.element("div").classes('col-span-3 row-span-2 col-start-4 row-start-6'):
            ui.label("Avhengigheter andre oppgaver").classes('text-lg font-bold')
            ui.textarea().classes('w-full bg-white rounded-lg').bind_value(project.samarabeid, "avhengigheter_andre")
        
            
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

        with ui.element("div").classes('col-span-4 row-span-5 col-start-1 row-start-10'):
            ui.label('Tilknyttet tiltak i Digitaliseringsstrategien').classes('text-lg font-bold')
            ui.select(DIGITALISERINGS_STRATEGI, multiple=True, on_change=sort_selected_values).classes('w-full bg-white rounded-lg').props('use-chips').bind_value(project.digitaliseringstrategi, "sammenheng_digital_strategi", forward=to_json, backward=to_list)
        with ui.element("div").classes('col-span-4 row-span-2 col-start-1 row-start-15'):
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
            ui.select(kompetanse_internt_list, value=None).classes('w-full bg-white rounded-lg').bind_value( project.resursbehov, "kompetanse_tilgjengelig")
        

        ui.label("Estimert antall månedsverk for fasen").classes('text-lg font-bold col-span-2 row-span-2 col-start-4 row-start-2')

        with ui.element("div").classes('col-span-1 row-span-1 col-start-4 row-start-3'):
            ui.label("Interne").classes('text-lg font-bold')
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "antall_mandsverk_intern", forward=convert_to_int)
        with ui.element("div").classes('col-span-1 row-span-1 col-start-5 row-start-3'):
            ui.label("Eksterne").classes('text-lg font-bold')
            ui.input().props('type=number min=0').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "antall_mandsverk_ekstern", forward=convert_to_int)

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-4 rounded-lg"):
        ui.label("5. Finansieringsbehov (ekskl. interne ressurser)​").classes('col-span-5 row-span-1 col-start-1 row-start-2 text-lg font-bold underline mt-4 mb-2')

        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-3'):
            ui.label('Estimert budsjettbehov i kr').classes('text-lg font-bold')
            ui.input().props('inputmode=numeric').classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "estimert_budsjet_behov", backward=add_thousand_split, forward=convert_to_int_from_thousand_sign)

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
                        ui.input().props('inputmode=numeric min=0 step=1 input-style="text-align: right;"') \
                        .classes('w-24 bg-white rounded-lg') \
                        .bind_value(project.ressursbruk[year], 'predicted_resources', backward=add_thousand_split, forward=convert_to_int_from_thousand_sign)

        with ui.element("div").classes('col-span-1 row-span-1 col-start-1 row-start-4'):
            ui.label("Hvor sikkert er estimatet").classes('text-lg font-bold')
            

            ui.select(ESTIMAT_LISTE, value = None).classes('w-full bg-white rounded-lg').bind_value(project.resursbehov,"risiko_av_estimat")

        with ui.element("div").classes('col-span-4 row-span-2 col-start-2 row-start-4'):
            ui.label('Forklaring estimat').classes('text-lg font-bold')
            ui.textarea(value=project.resursbehov.estimert_budsjet_forklaring).classes('w-full bg-white rounded-lg').bind_value(project.resursbehov, "estimert_budsjet_forklaring")
        
        

    async def save_object() -> "ProjectData":
     
        with ui.dialog() as dialog:
            ui.label("💾 Lagrer endringer... Vennligst vent ⏳")
            ui.spinner(size="lg", color="primary")
        try:
            dialog.open()
            await asyncio.sleep(0.1)  # Allow UI to render spinner
            await api_update_project(project, prosjekt_id, email)

            ui.notify("✅ Endringer lagret i databasen!", type="positive", position="top")

            await asyncio.sleep(1)
            ui.navigate.to(f"/project/{prosjekt_id}")
        finally:
            dialog.close()
    async def check_or_update():
    
        is_valid, message = validate_send_schema(project)
        if is_valid:
            kontakt_list = ast.literal_eval(project.portfolioproject.kontaktpersoner)
            kontakt_list.append(project.portfolioproject.tiltakseier)
            kontakt_set = list(set(kontakt_list))
            project.portfolioproject.epost_kontakt = str([brukere_list[i] for i in kontakt_set])
            await save_object()
        else: 
            ui.notify(message, type="warning", position="top", close_button="OK")
            return 



    ui.button("💾 Lagre", on_click=check_or_update).classes("mt-4")

