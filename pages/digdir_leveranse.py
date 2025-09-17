from nicegui import ui, app
from models.cache_model import CacheModel
from .utils import input_field, select_field, check_box, text_area_field, radio_box
from static_variables import LEVERANSEOMRÅDER, AVDELINGER, AKTØRER


def digdir_leveranse(page_name, store):
    leveranse_cache = store

    # page container (centered)
    # page container (centered)
    with ui.element("div").classes("w-full max-w-5xl px-4 md:px-12 py-12"):
        ui.label("Om Digirs leveranse").classes(
            "text-2xl md:text-3xl font-semibold text-[#1E2B3C] mb-4"
        )

        # form card
        with ui.card().classes(
            "block w-full p-6 md:p-8 rounded-2xl shadow-lg bg-white form-card"
        ):
            # responsive grid: 1 col on mobile, 2 cols from md
            with ui.element("div").classes("flex flex-col gap-5"):

                with ui.element("div").classes("grid grid-cols-2 gap-5 w-full"):
                    select_field(
                        cache_model=leveranse_cache,
                        field_name="leveranseområde",
                        label="18. Hvilke leveranseområder treffer aktiviteten?",
                        categories=LEVERANSEOMRÅDER,
                    )

                    input_field(
                        cache_model=leveranse_cache,
                        field_name="kontaktperson_for_aktivitet_in_digdir",
                        label="22. Hvem er kontaktperson for aktiviteten hos Digdir?",
                    )

                    radio_box(
                        cache_model=leveranse_cache,
                        field_name="avdeling_hovedansvar",
                        label="20. Hvilken avdeling har hovedansvar for Digdirs deltakelse?",
                        boxes=AVDELINGER,
                    )
                    check_box(
                        cache_model=leveranse_cache,
                        field_name="andre_avdeling_ansvar",
                        label="23. Hvilke andre avdelinger i Digdir bidrar/ vil bidra i aktiviteten?",
                        boxes=AVDELINGER,
                    )

                    check_box(
                        cache_model=leveranse_cache,
                        field_name="aktører_som_er_interessenter",
                        label="21. Hvilke aktører er aktuelle interessenter for aktiviteten?",
                        boxes=AKTØRER,
                        rows=3,
                    )

                    with ui.element("div").classes("flex flex-col gap-1"):
                        ui.html(
                            "24. Gjelder Digdirs bidrag i aktiviteten forhold til land som hører til risiko/høyrisikoområder?"
                        )
                        høyrisikoområder = (
                            ui.radio(["ja", "nei"])
                            .props("color=primary inline")
                            .bind_value(leveranse_cache, "høyrisikoområder")
                        )

                        # 24. Sikkerhetsvurdering (conditional)
                        ui.label(
                            "25. Hvis ja, er det gjennomført en sikkerhetsmessig vurdering sammen med VIS-VSB?"
                        ).bind_visibility_from(
                            høyrisikoområder, "value", lambda v: v == "ja"
                        )
                        ui.radio(["ja", "nei"]).props(
                            "color=primary inline"
                        ).bind_visibility_from(
                            høyrisikoområder, "value", lambda v: v == "ja"
                        ).bind_value(
                            leveranse_cache, "sikkerhetsmessig_vurdering"
                        )

                        text_area_field(
                            cache_model=leveranse_cache,
                            field_name="relevant_budskap",
                            label="26. Hvilket budskap anses som relevant å kommunisere om Digdirs bidrag til de ulike aktuelle interessenter?",
                        )

            # actions
            with ui.row().classes("justify-end gap-3 pt-12"):
                ui.button("Tilbake").on_click(
                    lambda: ui.navigate.to("/digdir_aktivitet")
                ).props("flat color=primary")
                ui.button("Neste").props("color=primary")
