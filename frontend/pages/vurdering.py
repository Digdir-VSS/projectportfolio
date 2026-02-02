from nicegui import ui, run
from datetime import datetime, date
import ast, asyncio
from dataclasses import asdict, is_dataclass

from sqlalchemy import table
from models.validators import to_json, to_list, sort_selected_values    
from models.ui_models import VurderingDataUI
from frontend.utils.backend_client import api_update_vurdering
grouppe = ["eID","KI", "Tjenesteutvikling", "Intern styring", "Økonomi", "Kunnskap og innsikt"]
def vurdering_overview(vurderinger):

    if not vurderinger:
        ui.label("Ingen vurderinger funnet.")
        return
    rows = [
        {**v.dict(), "prosjekt_id": str(v.prosjekt_id)}
        for v in vurderinger  # vurderinger = db_connector.get_all_vurderinger()
    ]
    visible_keys = [
        "navn",
        "avdeling",
        "oppstart",
        "planlagt_ferdig",
        "fase",
        "estimert_budsjet_behov",
        "vedtatt_tildeling",
        "tiltakseier",
        "kontaktpersoner",
        "gruppe",
        "mscw",
        "pulje",
        "kommentar",
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
    table = ui.table(
        columns=columns,
        rows=rows,
        row_key="prosjekt_id",
        column_defaults={
            "align": "left",
            "headerClasses": "uppercase text-primary",
            "sortable": True,
        },
    ).classes("w-full")


# Header
    with table.add_slot('top-left'):
        def toggle() -> None:
            table.toggle_fullscreen()
            button.props('icon=fullscreen_exit' if table.is_fullscreen else 'icon=fullscreen')
        button = ui.button('Toggle fullscreen', icon='fullscreen', on_click=toggle).props('flat')

    table.add_slot(
        "header",
        r"""
        <q-tr :props="props">
            <q-th auto-width />
            <q-th v-for="col in props.cols" :key="col.name" :props="props">
                {{ col.label }}
            </q-th>
        </q-tr>
        """,
    )

    # Body
    table.add_slot(
        "body",
        r"""
        <q-tr :props="props">
            <q-td auto-width>
                <a :href="'/vurdering/' + props.row.prosjekt_id"><q-btn size="sm" color="primary" round dense
                    @click="location.href = '/vurdering/' + props.row.prosjekt_id"

                    icon="edit" /></a>
            </q-td>
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
                {{ props.row[col.field] }}
            </q-td>
        </q-tr>
        """,
    )


def vurdering_page(vurdering_prosjekt, brukere_list, email):
    print(vurdering_prosjekt)
    ui.markdown(
        f"## *Vurdering for:* **{vurdering_prosjekt.portfolioproject.navn}**"
    ).classes('text-xl font-bold mb-4')

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-6 rounded-lg"):
        ui.label("1. Prosjektinfo").classes(
            'col-span-5 col-start-1 row-start-1 text-lg font-bold underline mt-4'
        )
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-2'):
            ui.label("Navn på tiltak").classes('text-lg font-bold')
            ui.input(value=vurdering_prosjekt.portfolioproject.navn).classes('w-full bg-white rounded-lg').bind_value(vurdering_prosjekt.portfolioproject, "navn")


        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-2'):
            ui.label("Tiltakseier").classes('text-lg font-bold')
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
                vurdering_prosjekt.portfolioproject,
                "kontaktpersoner",
                forward=to_json,
                backward=to_list
            )
        with ui.element("div").classes('col-span-3 row-span-1 col-start-1 row-start-3'):
            ui.label("Kontaktperson").classes('text-lg font-bold')
            ui.select(list(brukere_list.keys()), with_input=True, multiple=True, on_change=sort_selected_values).props(
                    "clearable options-dense color=primary").classes("w-full bg-white rounded-lg").props('use-chips').bind_value(vurdering_prosjekt.portfolioproject, "kontaktpersoner", forward=to_json, backward=to_list)
        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-3'):
            ui.label("Avdeling").classes('text-lg font-bold')
            ui.input(value=vurdering_prosjekt.portfolioproject.avdeling).classes('w-full bg-white rounded-lg').bind_value(vurdering_prosjekt.portfolioproject, "avdeling")
    
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-6 rounded-lg"):
        ui.label("2. Vurdering").classes(
            'col-span-5 col-start-1 row-start-1 text-lg font-bold underline mt-4'
        )
        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-2'):
            ui.label("Gruppe").classes('text-lg font-bold')
            ui.select(options=grouppe, with_input=True, new_value_mode=not None, clearable=True).classes('w-full bg-white rounded-lg').bind_value(vurdering_prosjekt.vurdering, "gruppe")
        with ui.element("div").classes('col-span-1 row-span-1 col-start-3 row-start-2'):
            ui.label("MSCW").classes('text-lg font-bold')
            ui.select(
                ['M', 'S', 'C', 'W']
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                vurdering_prosjekt.vurdering, "mscw"
            )
        with ui.element("div").classes('col-span-2 row-span-1 col-start-4 row-start-2'):
            ui.label("Pulje").classes('text-lg font-bold')
            ui.input(value=vurdering_prosjekt.vurdering.pulje).classes('w-full bg-white rounded-lg').bind_value(vurdering_prosjekt.vurdering, "pulje")
        with ui.element("div").classes('col-span-2 row-span-1 col-start-1 row-start-3'):
            ui.label("Risikovurdering").classes('text-lg font-bold')
            ui.textarea(value=vurdering_prosjekt.vurdering.risiko_vurdering).classes('w-full bg-white rounded-lg').bind_value(vurdering_prosjekt.vurdering, "risiko_vurdering")
        with ui.element("div").classes('col-span-3 row-span-3 col-start-3 row-start-3'):
            ui.label("Kommentar").classes('text-lg font-bold')
            ui.textarea(value=vurdering_prosjekt.vurdering.risiko_vurdering).classes('w-full bg-white rounded-lg').bind_value(vurdering_prosjekt.vurdering, "risiko_vurdering")
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-6 rounded-lg"):

        ui.label("3. Finansiering").classes(
            'col-span-5 col-start-1 row-start-1 text-lg font-bold underline mt-4'
        )
        with ui.element("div").classes('col-span-3 row-span-3 col-start-3 row-start-3'):
            ui.label("Kommentar").classes('text-lg font-bold')
            ui.textarea(value=vurdering_prosjekt.vurdering.risiko_vurdering).classes('w-full bg-white rounded-lg').bind_value(vurdering_prosjekt.vurdering, "risiko_vurdering")
    with ui.grid(columns=4).classes('gap-4 w-full'):
        ui.label('Navn')
        ui.label('Gruppe')
        ui.label('Pulje')
        ui.label('Tildeling')

    async def save_object() -> "VurderingData":
     
        with ui.dialog() as dialog:
            ui.label("💾 Lagrer endringer... Vennligst vent ⏳")
            ui.spinner(size="lg", color="primary")
        try:
            dialog.open()
            await asyncio.sleep(0.1)  # Allow UI to render spinner
            await api_update_vurdering(vurdering_prosjekt, vurdering_prosjekt.portfolioproject.prosjekt_id, email)

            ui.notify("✅ Endringer lagret i databasen!", type="positive", position="top")

            await asyncio.sleep(1)
            ui.navigate.to(f"/vurdering/{prosjekt_id}")
        finally:
            dialog.close()
    async def check_or_update():
        await save_object()

    ui.button("💾 Lagre", on_click=check_or_update).classes("mt-4")
        # ui.label("2. Status og fase").classes(
        #     'col-span-5 text-lg font-bold underline mt-4'
        # )

        # with ui.element("div").classes('col-span-2'):
        #     ui.label("MSCW").classes('font-bold')
        #     ui.select(
        #         ['M', 'S', 'C', 'W']
        #     ).classes(
        #         'w-full bg-white rounded-lg'
        #     ).bind_value(
        #         vurdering_prosjekt.vurdering, "mscw"
        #     )

    #     with ui.element("div").classes('col-span-3'):
    #         ui.label("Fremskritt").classes('font-bold')
    #         ui.select(
    #             FREMSKRITT_STATUS
    #         ).classes(
    #             'w-full bg-white rounded-lg'
    #         ).bind_value(
    #             rapportering.fremskritt, "fremskritt"
    #         )

    #     ui.label("4. Fremskritt – detaljer").classes(
    #         'col-span-5 text-lg font-bold underline mt-4'
    #     )

    #     ui.label("4. Viktige endringer").classes(
    #         'col-span-5 text-lg font-bold underline mt-4'
    #     )

    #     with ui.element("div").classes('col-span-2'):
    #         ui.label("Har det vært viktige endringer?").classes('font-bold')
    #         ui.input().classes(
    #             "w-full bg-white rounded-lg"
    #         ).bind_value(
    #             rapportering.rapportering, "viktige_endringer"
    #         )

    #     with ui.element("div").classes('col-span-3'):
    #         ui.label("Kommentar til endringer").classes('font-bold')
    #         ui.input().classes(
    #             "w-full bg-white rounded-lg"
    #         ).bind_value(
    #             rapportering.rapportering, "viktige_endringer_kommentar"
    #         )

    #     ui.label("5. Risiko").classes(
    #         'col-span-5 text-lg font-bold underline mt-4'
    #     )

    #     with ui.element("div").classes('col-span-2'):
    #         ui.label("Gjennomføringsrisiko").classes('font-bold')
    #         ui.input().classes(
    #             "w-full bg-white rounded-lg"
    #         ).bind_value(
    #             rapportering.delivery_risk, "risiko_rapportert"
    #         )

    #     with ui.element("div").classes('col-span-3'):
    #         ui.label("Begrunnelse for risiko").classes('font-bold')
    #         ui.input().classes(
    #             "w-full bg-white rounded-lg"
    #         ).bind_value(
    #             rapportering.delivery_risk, "risiko_rapportert_begrunnet"
    #         )



