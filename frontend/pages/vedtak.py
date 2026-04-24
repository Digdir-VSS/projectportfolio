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


def show_vedtak(prosjekt_id: str, vedtak_data: VedtakData, vurdering: VurderingData, email: str):

    with ui.element("div").classes("w-full p-6 flex flex-col gap-6"):

        # ── Header: title + dato ──────────────────────────────────────────────
        with ui.element("div").classes("flex items-center gap-6"):
            ui.markdown("## Porteføljestyrets vedtak").classes(
                "text-2xl font-bold underline m-0"
            )
            ui.label('Dato for vedtak').classes('text-lg font-bold')
            ui.input().bind_value(vedtak_data.vedtak, "vedtak_dato", backward=to_date_str, forward=to_datetime).props("outlined dense type=date clearable color=primary").classes("w-full")

        # ── Tildeling ─────────────────────────────────────────────────────────
        with ui.element("div").classes("flex flex-col gap-1 mt-4"):
            ui.label("Tildeling").classes("font-bold text-base")

            with ui.element("div").classes("flex border border-gray-300 rounded w-fit"):
                ui.label("2026").style(
                    "font-weight: bold; padding: 6px 24px; border-right: 1px solid #d1d5db;"
                )
                ui.label(
                    f"{vedtak_data.finansering.tildelte_midler:,} NOK"
                    if vedtak_data.finansering and vedtak_data.finansering.tildelte_midler
                    else "—"
                ).style("font-weight: bold; padding: 6px 24px;")

        # ── Vedtak ────────────────────────────────────────────────────────────
        with ui.element("div").classes("flex flex-col gap-2 mt-4"):
            ui.label("Vedtak").classes("font-bold text-xl")
            ui.textarea(
                placeholder="Eksempel: Tildeles midler for konseptfase. Tiltaket kommer tilbake for ny behandling høsten 2026. Tidsplan koordineres med tiltak xx."
            ).classes(
                "w-full rounded-lg border border-gray-300 bg-white min-h-[220px] p-4"
            ).bind_value(vedtak_data.vedtak, "vedtak_beskrivelse")

    # ── Save ──────────────────────────────────────────────────────────────────
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

    ui.button("💾 Lagre vedtak", on_click=save_object).classes(
        "mt-4 border border-gray-300 font-bold"
    )