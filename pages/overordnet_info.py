from nicegui import ui, app
from .utils import input_field, input_field_date, select_field, text_area_field
from models.cache_model import CacheModel


def digdir_overordnet_info_page(page_name, store):
    overordnet_cache = store

    # page container (centered)
    with ui.element("div").classes("w-full max-w-5xl px-4 md:px-12 py-12"):
        ui.label("Overordent info").classes(
            "text-2xl md:text-3xl font-semibold text-[#1E2B3C] mb-4"
        )

        # form card
        with ui.card().classes(
            "block w-full p-6 md:p-8 rounded-2xl shadow-lg bg-white form-card"
        ):
            # responsive grid: 1 col on mobile, 2 cols from md
            with ui.element("div").classes("flex flex-col gap-7"):

                with ui.element("div").classes("grid grid-cols-2 gap-5 w-full"):

                    input_field(
                        cache_model=overordnet_cache,
                        field_name="initiativ_navn",
                        label="1. Hva heter det overordnete initiativet som Digdirs aktivitet tar utgangspunkt i?",
                    )
                    input_field(
                        cache_model=overordnet_cache,
                        field_name="e-post-adresse-kontakt-person",
                        label="6. Hva er epostadressen til kontaktpunkt hos den overordnete organisasjonen?",
                    )
                    input_field(
                        cache_model=overordnet_cache,
                        field_name="url-initiativ-nettside",
                        label="2. Hva er URL-en til nettside om initiativet?",
                    )

                    text_area_field(
                        cache_model=overordnet_cache,
                        field_name="hovedmålet_initiativet",
                        label="7. Hva er hovedmålet for initiativet?",
                    )
                    select_field(
                        cache_model=overordnet_cache,
                        field_name="initiative_type",
                        label="3. Hvilken type initiativ er det?",
                        categories=[
                            "Progam",
                            "Prosjekt",
                            "Undersøkelse",
                            "Konferanse",
                            "Ekspertgruppe",
                            "Nettverk",
                            "Annet",
                        ],
                    )

                    select_field(
                        cache_model=overordnet_cache,
                        field_name="geografiske_område",
                        label="8. Hvilket geografisk område dekker initiativet?",
                        categories=[
                            "Norden",
                            "Norden og Baltikum",
                            "Europa",
                            "Globalt",
                            "Annet",
                        ],
                    )
                    select_field(
                        cache_model=overordnet_cache,
                        field_name="organisasjon_ansvar",
                        label="4. Hvilken organisasjon har ansvar for det overordnete initiativet?",
                        categories=[
                            "EU-kommisjon",
                            "Nordisk ministerråd",
                            "OECD",
                            "Den norske regjeringen (bilateralt samarbeidsavrtale mellom Norge og utvalge land)",
                            "Annet",
                        ],
                    )

                    select_field(
                        cache_model=overordnet_cache,
                        field_name="fagområde_initiative",
                        label="9. Hvilke fagområder innen digitalisering gjelder initiativet?",
                        categories=[
                            "Cybersikkerhet",
                            "Digital tjenesteutvikling",
                            "KI",
                            "Digitaliseringsregelverk",
                            "Tilitstjenester (eID, eSignature, meldingsutveksling, ...)",
                            "Annet",
                        ],
                    )

                    input_field(
                        cache_model=overordnet_cache,
                        field_name="kontaktpunkt_overordnet_organisasjon",
                        label="5. Hvem er kontaktpunkt hos den overordnete organisasjonen?",
                    )

            # actions
            with ui.row().classes("justify-end gap-3 pt-12"):
                ui.button("Tilbake").on_click(lambda: ui.navigate.to("/")).props(
                    "flat color=primary"
                )
                ui.button("Neste").on_click(
                    lambda: ui.navigate.to("/digdir_aktivitet")
                ).props("color=primary")
