from nicegui import ui, app
from .utils import (
    select_field,
    input_field,
    text_area_field,
    input_field_date,
    check_box,
)
from models.cache_model import CacheModel
from static_variables import COUNTRIES, AKTIVITY_ROLES


def digdir_aktivitet_page(page_name, store):
    aktivitet_cache = store#CacheModel(page_name, store)

    # page container (centered)
    with ui.element("div").classes("w-full max-w-5xl px-4 md:px-12 py-12"):
        ui.label("Om Digdirs aktivitet").classes(
            "text-2xl md:text-3xl font-semibold text-[#1E2B3C] mb-4"
        )

        # form card
        with ui.card().classes(
            "block w-full p-6 md:p-8 rounded-2xl shadow-lg bg-white form-card"
        ):
            # responsive grid: 1 col on mobile, 2 cols from md
            with ui.element("div").classes("flex flex-col gap-5"):

                with ui.element("div").classes("grid grid-cols-2 gap-5 w-full"):

                    input_field(
                        cache_model=aktivitet_cache,
                        field_name="aktivitet_navn",
                        label="10. Hva heter aktiviteten som Digdir deltar i?",
                    )
                    select_field(
                        cache_model=aktivitet_cache,
                        field_name="samarbeids_land",
                        label="13. Hvilket land samarbeider Digdir med ifm. aktiviteten?",
                        categories=COUNTRIES,
                    )
                    select_field(
                        cache_model=aktivitet_cache,
                        field_name="type_aktivitet",
                        label="11. Hvilke type aktivitet er det?",
                        categories=[],
                    )
                    with ui.element("div").classes("grid grid-cols-2 gap-5 w-full"):
                        input_field(
                            cache_model=aktivitet_cache,
                            field_name="tidsbruk_for_digdir_bidrag",
                            label="14. Hva er anslått tidsbruk for Digdirs bidrag, i dagsverk?",
                            validation={
                                "Må være et tall": lambda value: (value is None)
                                or (str(value).isdigit())
                            },
                        )
                    check_box(
                        cache_model=aktivitet_cache,
                        field_name="strategiske_føringer",
                        label="12a. Hvilke strategiske føringer gir forankring for Digdirs deltakelse?",
                        boxes=[
                            "Hovedinstruks",
                            "Tildelingsbrev",
                            "Digdirs målbilde",
                            "Digitaliseringsrundskriv",
                            "Annet",
                        ],
                    )
                    with ui.element("div").classes("grid grid-cols-2 gap-5 w-full"):
                        input_field(
                            cache_model=aktivitet_cache,
                            field_name="budsjettbehov_for_digdir_bidrag",
                            label="15. Hva er anslått budsjettbehov for Digdirs bidrag, i kroner?",
                            validation={
                                "Må være et tall": lambda value: (value is None)
                                or (str(value).isdigit())
                            },
                        )
                        ui.html(
                            "<br><br><br><br>F.eks kostnader knyttet til ev. reiser, møtevirksomhet, innkjøp av varer/tjenester ++"
                        ).classes("text-xs text-gray-500").style("font-size: 10px;")
                    text_area_field(
                        cache_model=aktivitet_cache,
                        field_name="kapittelreferanse_føring",
                        label="12b. Oppgi kapittelreferanse eller formuleringen fra gjeldende føring",
                        rows=6,
                        h_size=40,
                    )
                    input_field(
                        cache_model=aktivitet_cache,
                        field_name="andre_norske_samarbeidspartner",
                        label="16. Hvilke andre norske aktører er samarbeidspartnere/ koblet til aktiviteten",
                    )
                    select_field(
                        cache_model=aktivitet_cache,
                        field_name="digdirs_rolle_i_aktivitet",
                        label="13. Hvilken rolle har Digdir i aktiviteten?",
                        categories=AKTIVITY_ROLES,
                    )
                    with ui.element("div").classes("grid grid-cols-2 gap-5 w-full"):
                        input_field_date(
                            cache_model=aktivitet_cache,
                            field_name="aktivitet_tid_fra",
                            label="17. Aktivitet varer fra",
                        )
                        input_field_date(
                            cache_model=aktivitet_cache,
                            field_name="aktivitet_tid_til",
                            label="17. Aktivitet varer til",
                        )
            with ui.row().classes("justify-end gap-3 pt-12"):
                ui.button("Tilbake").on_click(
                    lambda: ui.navigate.to("/overordnet")
                ).props("flat color=primary")
                ui.button("Neste").on_click(lambda: ui.navigate.to("/leveranse")).props(
                    "color=primary"
                )
