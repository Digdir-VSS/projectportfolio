from nicegui import ui
import asyncio

from models.ui_models import VurderingData, ProjectData
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
   

def show_vurdering(
    prosjekt_id: str,
    email: str,
    vurdering: VurderingData,
    project_data: ProjectData = None,  # pass the full project data for the read-only section
):
    # ── Section 1: Fakta om tiltaket (read-only) ─────────────────────────────
    with ui.grid(columns=5).classes("w-full gap-5 bg-white border border-gray-200 p-6 rounded-lg mb-6"):

        # Title row
        with ui.element("div").classes("col-span-3"):
            ui.markdown(f"## Fakta om {vurdering.portfolioproject.navn}").classes("text-xl font-bold underline m-0")

        # Start + Planlagt ferdig + Fase (top right)
        with ui.element("div").classes("col-span-2 flex flex-col gap-2"):
            with ui.element("div").classes("flex gap-4"):
                with ui.element("div"):
                    ui.label("Start").classes("text-sm text-gray-500 font-bold")
                    ui.input(
                        value=vurdering.portfolioproject.oppstart.strftime("%d.%m.%Y")
                        if vurdering.portfolioproject.oppstart else "—"
                    ).classes("bg-gray-100 text-gray-600 rounded w-full").props("readonly")

                with ui.element("div"):
                    ui.label("Planlagt ferdig").classes("text-sm text-gray-500 font-bold")
                    ui.input(
                        value=vurdering.fremskritt.planlagt_ferdig.strftime("%d.%m.%Y")
                        if vurdering.fremskritt and vurdering.fremskritt.planlagt_ferdig else "—"
                    ).classes("bg-gray-100 text-gray-600 rounded w-full").props("readonly")

            with ui.element("div").classes("flex items-center gap-2"):
                ui.label("Fase:").classes("font-bold text-gray-600")
                ui.input(
                    value=vurdering.fremskritt.fase if vurdering.fremskritt and vurdering.fremskritt.fase else "—"
                ).classes("bg-gray-100 text-gray-600 rounded flex-1").props("readonly")

        # Tiltakseier + Kontaktperson
        with ui.element("div").classes("col-span-2"):
            ui.label("Tiltakseier").classes("font-bold text-gray-600")
            ui.input(
                value=vurdering.portfolioproject.tiltakseier or "—"
            ).classes("bg-gray-100 text-gray-600 rounded w-full").props("readonly")

        with ui.element("div").classes("col-span-2"):
            ui.label("Kontaktperson").classes("font-bold text-gray-600")
            ui.input(
                value=", ".join(to_list(vurdering.portfolioproject.kontaktpersoner)) or "—"
            ).classes("bg-gray-100 text-gray-600 rounded w-full").props("readonly").props('use-chips')

        # Spacer to keep layout aligned (col 5 is taken by dates above)
        ui.element("div").classes("col-span-1")

        # Problemstilling + Hovedleveranser (side by side, tall)
        with ui.element("div").classes("col-span-2"):
            ui.label("Problemstilling").classes("font-bold text-gray-600")
            ui.textarea(
                value=project_data.problemstilling.problem if project_data and project_data.problemstilling else "—"
            ).classes("bg-gray-100 text-gray-600 rounded w-full min-h-[160px]").props("readonly")

        with ui.element("div").classes("col-span-3"):
            ui.label("Hovedleveranser").classes("font-bold text-gray-600")
            ui.textarea(
                value=project_data.tiltak.tiltak_beskrivelse if project_data and project_data.tiltak else "—"
            ).classes("bg-gray-100 text-gray-600 rounded w-full min-h-[160px]").props("readonly")

        # Ressurs- og finansieringsbehov table + Risiko side by side
        with ui.element("div").classes("col-span-2"):
            ui.label("Ressurs- og finansieringsbehov").classes("font-bold text-gray-600 mb-2")
            columns = [
                {"name": "year",      "label": "",                   "field": "year",      "align": "left"},
                {"name": "intern",    "label": "Mnd.v. Interne",     "field": "intern",    "align": "left"},
                {"name": "ekstern",   "label": "mnd.v. Eksterne",    "field": "ekstern",   "align": "left"},
                {"name": "budsjett",  "label": "Finansieringsbehov", "field": "budsjett",  "align": "left"},
            ]
            rows = []
            if project_data and project_data.ressursbruk:
                for year, rb in sorted(project_data.ressursbruk.items()):
                    rows.append({
                        "year":     str(year),
                        "intern":   str(project_data.resursbehov.antall_mandsverk_intern or "")
                                    if project_data.resursbehov else "",
                        "ekstern":  str(project_data.resursbehov.antall_mandsverk_ekstern or "")
                                    if project_data.resursbehov else "",
                        "budsjett": str(rb.predicted_resources or "") if rb else "",
                    })
            else:
                rows = [
                    {"year": "2026", "intern": "", "ekstern": "", "budsjett": ""},
                    {"year": "2027", "intern": "", "ekstern": "", "budsjett": ""},
                    {"year": "2028", "intern": "", "ekstern": "", "budsjett": ""},
                ]
            ui.table(columns=columns, rows=rows).classes(
                "w-full text-sm border border-gray-200 rounded"
            ).props("dense flat")

        with ui.element("div").classes("col-span-3"):
            ui.label("Risiko hvis tiltaket ikke gjennomføres").classes("font-bold text-gray-600")
            ui.textarea(
                value=project_data.risikovurdering.vurdering
                      if project_data and project_data.risikovurdering else "—"
            ).classes("bg-gray-100 text-gray-600 rounded w-full min-h-[160px]").props("readonly")

    # ── Section 2: Porteføljekontorets anbefaling (editable) ─────────────────
    with ui.grid(columns=5).classes("w-full gap-5 bg-[#f9f9f9] p-6 rounded-lg"):

        with ui.element("div").classes("col-span-5"):
            ui.markdown(
                f"## *Porteføljekontorets anbefaling på:* **{vurdering.portfolioproject.navn}**"
            ).classes("text-xl font-bold")

        ui.label("MSCW").classes("col-span-5 text-lg font-bold underline mt-4")
        with ui.element("div").classes("col-span-5"):
            ui.label("Vurdering").classes("font-bold")
            ui.select(MSCW).classes(
                "w-full bg-white rounded-lg border-2 border-green-600"
            ).bind_value(vurdering.vurdering, "mscw")

        ui.label("Finansiering").classes("col-span-5 text-lg font-bold underline mt-4")

        with ui.element("div").classes("col-span-2"):
            ui.label("Tildeling").classes("font-bold")
            ui.number(
                label="NOK",
                min=0,
                format="%.0f",
            ).classes(
                "w-full bg-white rounded-lg border-2 border-green-600"
            ).bind_value(vurdering.finansiering, "tildelte_midler")

        with ui.element("div").classes("col-span-3"):
            ui.label("Tildelingen dekker").classes("font-bold")
            ui.textarea(placeholder="Beskriv hva tildelingen dekker...").classes(
                "w-full bg-white rounded-lg border-2 border-green-600"
            ).bind_value(vurdering.finansiering, "tildelte_midler_dekker")

        with ui.element("div").classes("col-span-5"):
            ui.label("Begrunnelse for anbefaling").classes("font-bold")
            ui.textarea(placeholder="Skriv begrunnelsen her...").classes(
                "w-full bg-white rounded-lg border-2 border-green-600 min-h-[200px]"
            ).bind_value(vurdering.vurdering, "begrunnelse")

    # ── Save ──────────────────────────────────────────────────────────────────
    async def save_object():
        with ui.dialog() as dialog:
            ui.label("💾 Lagrer endringer... Vennligst vent ⏳")
            ui.spinner(size="lg", color="primary")
        try:
            dialog.open()
            await asyncio.sleep(0.1)
            await api_update_vurdering(vurdering, prosjekt_id, email)
            ui.notify("✅ Endringer lagret!", type="positive", position="top")
            await asyncio.sleep(1)
            ui.navigate.to(f"/vurdering/{prosjekt_id}")
        finally:
            dialog.close()

    ui.button("💾 Lagre", on_click=save_object).classes("mt-4")