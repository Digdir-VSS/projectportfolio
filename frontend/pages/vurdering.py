from nicegui import ui
import asyncio

from models.ui_models import VurderingData
from models.validators import to_json, to_list, sort_selected_values
from frontend.utils.backend_client import api_update_vurdering, api_get_prosjekt_list

from frontend.static_variables import FREMDRIFT_STATUS, RISIKO_CATEGORIES, MSCW, DIGITALISERINGS_STRATEGI, FASE

grouppe = ["eID","KI", "Tjenesteutvikling", "Intern styring", "Økonomi", "Kunnskap og innsikt"]

prosjekt_nummer_list = []
def show_status_vurdering_overview(prosjekter):
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
                    <a :href="'/vurdering/' + props.row.prosjekt_id"><q-btn size="sm" color="primary" round dense
                    @click="location.href = '/vurdering/' + props.row.prosjekt_id"

                    icon="edit" /></a>
                    
                </q-td>
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.value }}
                </q-td>
            </q-tr>
            '''
        )
   

  
def show_vurdering(prosjekt_id: str, email: str, vurdering: VurderingData, prosjekter=None):
    prosjekt_dict = {
    p.prosjekt:f"{p.prosjekt} – {p.prosjekt_beskrivelse}"
    for p in prosjekter
}
    # prosjekt_list = list(prosjekt_dict.keys())
    ui.markdown(
        f"## *Vurdering på:* **{vurdering.portfolioproject.navn}**"
    ).classes('text-xl font-bold mb-4')

    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-6 rounded-lg"):

        ui.label("1. Kontaktpersoner").classes(
            'col-span-5 text-lg font-bold underline mt-4'
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
                vurdering.fremskritt, "fase"
            )

        with ui.element("div").classes('col-span-2'):
            ui.label("Fremdrift").classes('font-bold')
            ui.select(
                FREMDRIFT_STATUS
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                vurdering.fremskritt, "fremskritt"
            )

        with ui.element("div").classes('col-span-1'):
            ui.label("Risiko").classes('font-bold')
            ui.select(
                RISIKO_CATEGORIES
            ).classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                vurdering.risiko, "vurdering"
            )

        ui.label("3. Tilknytning til strategier").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        ui.label("Beskriv hvordan tiltaket understøtter målbildet").classes(
            'col-span-5 font-bold mt-2'
        )

        with ui.element("div").classes('col-span-5'):
            ui.label("1. Vi fremmer samordning og prioritering for en mer effektiv offentlig sektor").classes('font-bold')
            ui.textarea().classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                vurdering.malbilde, "malbilde_1_beskrivelse"
            )

        with ui.element("div").classes('col-span-5'):
            ui.label("2. Vi leder an i ansvarlig og innovativ bruk av data og kunstig intelligens").classes('font-bold')
            ui.textarea().classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                vurdering.malbilde, "malbilde_2_beskrivelse"
            )

        with ui.element("div").classes('col-span-5'):
            ui.label("3. Vi sikrer trygg tilgang til digitale tjenester for alle").classes('font-bold')
            ui.textarea().classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                vurdering.malbilde, "malbilde_3_beskrivelse"
            )

        with ui.element("div").classes('col-span-5'):
            ui.label("4. Vi løser komplekse utfordringer sammen og tilpasser oss en verden i rask endring").classes('font-bold')
            ui.textarea().classes(
                'w-full bg-white rounded-lg'
            ).bind_value(
                vurdering.malbilde, "malbilde_4_beskrivelse"
            )

        with ui.element("div").classes('col-span-5'):
            ui.label('Tilknyttet tiltak i Digitaliseringsstrategien').classes('font-bold')
            ui.select(
                DIGITALISERINGS_STRATEGI,
                multiple=True,
                on_change=sort_selected_values
            ).classes(
                'w-full bg-white rounded-lg'
            ).props(
                'use-chips'
            ).bind_value(
                vurdering.digitaliseringstrategi,
                "sammenheng_digital_strategi",
                forward=to_json,
                backward=to_list
            )

        with ui.element("div").classes('col-span-5'):
            ui.label('Eventuell beskrivelse av kobling til Digitaliseringsstrategien').classes('font-bold')
            ui.textarea().bind_value(
                vurdering.digitaliseringstrategi,
                "digital_strategi_kommentar"
            ).classes(
                'w-full bg-white rounded-lg'
            )

        ui.label("4. Samfunnseffekt").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        with ui.element("div").classes('col-span-5'):
            ui.label("Hvor store bruker- og samfunnseffekter").classes('font-bold')
            ui.input().classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                vurdering.samfunnseffekt, "effekt"
            )

        ui.label("5. MSCW").classes(
            'col-span-5 text-lg font-bold underline mt-4'
        )

        with ui.element("div").classes('col-span-5'):
            ui.label("Vurdering").classes('font-bold')
            ui.select(MSCW).classes(
                "w-full bg-white rounded-lg"
            ).bind_value(
                vurdering.vurdering, "mscw"
            )
        ui.label("6. Finansiering").classes(
            'col-span-5 text-lg font-bold underline mt-4')
        with ui.element("div").classes('col-span-2'):
            ui.label("Gruppe").classes('text-lg font-bold')
            ui.select(options=grouppe, with_input=True, new_value_mode=not None, clearable=True).classes('w-full bg-white rounded-lg').bind_value(vurdering.vurdering, "gruppe")

        with ui.element("div").classes('col-span-5'):
            ui.label("Prosjekt nummer i økønomisystemet").classes('font-bold')
            ui.select(options=prosjekt_dict, with_input=True, new_value_mode=not None, clearable=True).classes('w-full bg-white rounded-lg').bind_value(
                vurdering.finansiering, "prosjekt_nummer"
            )

    async def save_object() -> "VurderingData":
        with ui.dialog() as dialog:
            ui.label("💾 Lagrer endringer... Vennligst vent ⏳")
            ui.spinner(size="lg", color="primary")
        try:
            dialog.open()
            await asyncio.sleep(0.1)
            await api_update_vurdering(vurdering, prosjekt_id, email)

            ui.notify("✅ Endringer lagret i databasen!", type="positive", position="top")

            await asyncio.sleep(1)
            ui.navigate.to(f"/vurdering/{prosjekt_id}")
        finally:
            dialog.close()

    async def check_or_update():
        await save_object()

    ui.button("💾 Lagre", on_click=check_or_update).classes("mt-4")