from nicegui import ui
from models.ui_models import ProsjektListUI

def show_vedtak_overview(prosjekter: list[ProsjektListUI]):

    ui.markdown("## Tiltak – velg prosjekt").classes("text-2xl font-bold underline mb-6")

    with ui.element("div").classes("w-full flex flex-col gap-3"):
        for p in prosjekter:
            prosjekt_id = p.prosjekt
            navn = p.prosjekt_beskrivelse or prosjekt_id

            with ui.card().classes(
                "w-full cursor-pointer hover:bg-gray-100 transition-colors rounded-lg border border-gray-200 px-6 py-4"
            ).on("click", lambda pid=prosjekt_id: ui.navigate.to(f"/vedtak/{pid}")):

                with ui.element("div").classes("flex items-center justify-between w-full"):
                    with ui.element("div").classes("flex flex-col"):
                        ui.label(navn).classes("text-lg font-bold text-gray-800")
                        ui.label(prosjekt_id).classes("text-sm text-gray-400")

                    ui.icon("chevron_right").classes("text-gray-400 text-2xl")