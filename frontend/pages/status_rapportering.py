from typing import List
from nicegui import ui

from models.ui_models import RapporteringData
from models.validators import to_json, to_list, to_date_str, convert_to_int, sort_selected_values
from frontend.static_variables import FREMSKRITT_STATUS
  

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
    print(rapportering.fremskritt.fase)
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
                ['Konsept', 'Planlegging', 'Gjennomføring', 'Problem/ide']
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                rapportering.fremskritt, "fase"
            )

        with ui.element("div").classes('col-span-3'):
            ui.label("Fremskritt").classes('font-bold')
            ui.select(
                FREMSKRITT_STATUS
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                rapportering.fremskritt, "fremskritt"
            )

        ui.label("4. Fremskritt – detaljer").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        with ui.element("div").classes('col-span-5'):
            ui.label("Kommentar til fremskritt").classes('font-bold')
            ui.input(
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                rapportering.fremskritt, "fremskritt_kommentar"
            )

        ui.label("5. Viktige endringer").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        with ui.element("div").classes('col-span-2'):
            ui.label("Har det vært viktige endringer?").classes('font-bold')
            ui.input().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.rapportering, "viktige_endringer"
            )

        with ui.element("div").classes('col-span-3'):
            ui.label("Kommentar til endringer").classes('font-bold')
            ui.input().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.rapportering, "viktige_endringer_kommentar"
            )

        ui.label("6. Risiko").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        with ui.element("div").classes('col-span-2'):
            ui.label("Gjennomføringsrisiko").classes('font-bold')
            ui.input().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.delivery_risk, "risiko_rapportert"
            )

        with ui.element("div").classes('col-span-3'):
            ui.label("Begrunnelse for risiko").classes('font-bold')
            ui.input().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                rapportering.delivery_risk, "risiko_rapportert_begrunnet"
            )
    ui.button("💾 Lagre").classes("mt-6")

