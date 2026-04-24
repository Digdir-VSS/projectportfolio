from nicegui import ui
import asyncio

from models.ui_models import ProjectData, VurderingData,VedtakData
from frontend.utils.backend_client import api_update_vedtak
from models.validators import to_date_str, add_thousand_split, convert_to_int_from_thousand_sign, to_datetime


def show_vedtak_overview(prosjekter: list[ProjectData]):

    ui.markdown("## Tiltak – velg prosjekt").classes("text-2xl font-bold underline mb-6")

    with ui.element("div").classes("w-full flex flex-col gap-3"):
        for p in prosjekter:
            prosjekt_id = p["prosjekt_id"]
            navn = p["navn"]

            with ui.card().classes(
                "w-full cursor-pointer hover:bg-gray-100 transition-colors rounded-lg border border-gray-200 px-6 py-4"
            ).on("click", lambda pid=prosjekt_id: ui.navigate.to(f"/vedtak/{pid}")):

                with ui.element("div").classes("flex items-center justify-between w-full"):
                    with ui.element("div").classes("flex flex-col"):
                        ui.label(navn).classes("text-lg font-bold text-gray-800")

                    ui.icon("chevron_right").classes("text-gray-400 text-2xl")


def show_vedtak(prosjekt_id: str, vedtak_data: VedtakData, vurdering: VurderingData, email: str, access_allowance: bool = True):

    def lock(element):
        if not access_allowance:
            element.props('disable')
        return element

    with ui.element("div").classes("w-full p-6 flex flex-col gap-4"):

        # ── Header card ───────────────────────────────────────────────────────
        with ui.element("div").classes("flex items-center gap-6 bg-white border border-gray-200 rounded-xl p-5"):
            ui.label("Porteføljestyrets vedtak").classes("text-xl font-bold")
            with ui.element("div").classes("ml-auto flex items-center gap-3"):
                ui.label("Dato for vedtak").classes("text-sm text-gray-500 whitespace-nowrap")
                lock(
                    ui.input()
                    .bind_value(vedtak_data.vedtak, "vedtak_dato", backward=to_date_str, forward=to_datetime)
                    .props("outlined dense type=date clearable color=primary")
                )

        # ── Main card ─────────────────────────────────────────────────────────
        with ui.element("div").classes("bg-white border border-gray-200 rounded-xl p-5 flex flex-col gap-5"):

            # Tildeling
            with ui.element("div"):
                ui.label("TILDELING").classes("text-xs font-medium text-gray-400 tracking-widest mb-2")
                with ui.element("div").classes("inline-flex border border-gray-200 rounded-lg overflow-hidden"):
                    ui.label("2026").classes("text-sm font-medium px-4 py-1.5 bg-gray-50 border-r border-gray-200 text-gray-500")
                    ui.label(
                        f"{vedtak_data.finansering.tildelte_midler:,} NOK"
                        if vedtak_data.finansering and vedtak_data.finansering.tildelte_midler
                        else "—"
                    ).classes("text-sm font-medium px-4 py-1.5")

            ui.separator()

            # Vedtak text
            with ui.element("div"):
                ui.label("VEDTAK").classes("text-xs font-medium text-gray-400 tracking-widest mb-2")
                lock(
                    ui.textarea(
                        placeholder="Eksempel: Tildeles midler for konseptfase. Tiltaket kommer tilbake for ny behandling høsten 2026. Tidsplan koordineres med tiltak xx."
                    )
                    .classes("w-full bg-white rounded-lg")
                    .props("outlined rows=7")
                    .bind_value(vedtak_data.vedtak, "vedtak_beskrivelse")
                )

        # ── Save ──────────────────────────────────────────────────────────────
        async def save_object():
            with ui.dialog() as dialog:
                ui.label("💾 Lagrer vedtak... Vennligst vent ⏳")
                ui.spinner(size="lg", color="primary")
            try:
                dialog.open()
                await asyncio.sleep(0.1)
                await api_update_vedtak(vedtak_data, prosjekt_id, email)
                ui.notify("✅ Vedtak lagret!", type="positive", position="top")
                await asyncio.sleep(1)
                ui.navigate.to(f"/vedtak/{prosjekt_id}")
            finally:
                dialog.close()

        if access_allowance:
            ui.button("💾 Lagre vedtak", on_click=save_object).classes("self-end mt-2")