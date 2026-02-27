from typing import List
from nicegui import ui
import asyncio, ast

from models.ui_models import RapporteringData
from models.validators import to_json, to_list, to_date_str, convert_to_int, sort_selected_values
from frontend.static_variables import FREMDRIFT_STATUS, RISIKO_CATEGORIES, FASE
from frontend.utils.backend_client import api_update_rapport
  

def show_status_rapportering_overview(prosjekter):
    with ui.column().classes("w-full gap-2"):
        if not prosjekter:
            ui.label('Ingen prosjekter funnet for denne brukeren.')
            return
        visible_keys = [
            key for key in prosjekter[0].keys()
            if key not in ["prosjekt_id", "epost_kontakt"]
        ]

        columns = [
            {
                "name": key,
                "label": key.replace("_", " ").title(),
                "field": key,
                "sortable": True,
                "align": "left",
            }
            for key in visible_keys
        ]


        rows = [
            {**p, "prosjekt_id": str(p["prosjekt_id"])}
            for p in prosjekter
        ]

        table =  ui.table(columns=columns,
                    rows=rows,
                    row_key="prosjekt_id",
                    column_defaults={
                        "align": "left",
                        "headerClasses": "uppercase text-primary",
                        "sortable": True,
                        "filterable": True,
                    },).classes("w-full")

        table.add_slot(
            'header',
            r'''
            <q-tr :props="props">
                <q-th auto-width />
                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.label }}
                </q-th>
            </q-tr>
            '''
        )

        table.add_slot(
            'body',
            r'''
            <q-tr :props="props">
                <q-td auto-width>
                    <a :href="'/status_rapportering/' + props.row.prosjekt_id"><q-btn size="sm" color="primary" round dense
                    @click="location.href = '/status_rapportering/' + props.row.prosjekt_id"

                    icon="edit" /></a>
                    
                </q-td>
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.value }}
                </q-td>
            </q-tr>
            '''
        )
   

  
def show_status_rapportering(prosjekt_id: str, email: str, rapportering: RapporteringData, brukere_list):
    ui.markdown(
        f"## *Rapportering på:* **{rapportering.portfolioproject.navn}**"
    ).classes('text-xl font-bold mb-4')

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-6 rounded-lg"):

        ui.label("1. Kontaktpersoner").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        with ui.element("div").classes('col-span-5'):
            ui.select(
                list(brukere_list.keys()),
                with_input=True,
                multiple=True,
                on_change=sort_selected_values
            ).props(
                "clearable options-dense color=primary use-chips"
            ).classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.portfolioproject,
                "kontaktpersoner",
                forward=to_json,
                backward=to_list
            )

        ui.label("2. Status og fase").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        with ui.element("div").classes('col-span-2'):
            ui.label("Prosjektfase").classes('font-bold')
            ui.select(
                FASE
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                rapportering.fremskritt, "fase"
            )



        ui.label("3. Vesentlige endringer").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        # Row for labels
        with ui.element("div").classes('col-span-2'):
            ui.label("Har det vært vesentlige endringer i forutsetninger og rammebetingelser siden siste rapportering?").classes('font-bold')

        with ui.element("div").classes('col-span-3'):
            ui.label("Er det endringer i hva tiltaket skal levere og når leveransene skal skje?").classes('font-bold')

        # Row for inputs (aligned)
        with ui.element("div").classes('col-span-2'):
            ui.textarea().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.rapportering, "viktige_endringer"
            )

        with ui.element("div").classes('col-span-3'):
            ui.textarea().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.rapportering, "viktige_endringer_kommentar"
            )
        
        ui.label("4. Avhengigheter").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )
        with ui.element("div").classes('col-span-5'):
            ui.label("Er det noen avhengigheter som er spesielt viktig for tiltaket?").classes('font-bold')
            ui.textarea().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.avhengigheter, "avhengigheter"
            )
        ui.label("5. Fremdrift").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )
        with ui.element("div").classes('col-span-3'):
            ui.label("Fremdrift").classes('font-bold')
            ui.select(
                FREMDRIFT_STATUS
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                rapportering.fremskritt, "fremskritt"
            )
        ui.label("6. Risiko").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )
        # Row for labels
        with ui.element("div").classes('col-span-2'):
            ui.label(" Risiko for at tiltaket ikke oppnå planlagte resultater innen avtalt tid, kostnad og kvalitet ").classes('font-bold')


        with ui.element("div").classes('col-span-3'):
            ui.label("Begrunnelse for risiko").classes('font-bold')

 
        with ui.element("div").classes('col-span-2'):
            ui.select(RISIKO_CATEGORIES).classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.delivery_risk, "risiko_rapportert"
            )

        with ui.element("div").classes('col-span-3'):
            ui.textarea().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.delivery_risk, "risiko_rapportert_begrunnet"
            )
    async def save_object() -> "RapporteringData":
     
        with ui.dialog() as dialog:
            ui.label("💾 Lagrer endringer... Vennligst vent ⏳")
            ui.spinner(size="lg", color="primary")
        try:
            dialog.open()
            await asyncio.sleep(0.1)  # Allow UI to render spinner
            await api_update_rapport(rapportering, prosjekt_id, email)

            ui.notify("✅ Endringer lagret i databasen!", type="positive", position="top")

            await asyncio.sleep(1)
            ui.navigate.to(f"/status_rapportering/{prosjekt_id}")
        finally:
            dialog.close()
    async def check_or_update():
        await save_object()


    ui.button("💾 Lagre", on_click=check_or_update).classes("mt-4")

