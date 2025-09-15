from nicegui import ui

from .utils import spacer

initiative_types = ['Program', 'Prosjekt', 'Strategi', 'Politikk', 'Annet']
org_options = ['Direktorat', 'Departement', 'Kommunal etat', 'Privat', 'Frivillig', 'Annet']
geo_options = ['Nasjonalt', 'Regionalt', 'Kommunalt', 'Internasjonalt', 'Annet']
domain_options = [
    'Arkitektur', 'Standardisering', 'Informasjonssikkerhet', 'Personvern',
    'Deling av data', 'Tjenesteutvikling', 'Annet'
]

def get_store() -> dict:
    return {}
    

def digdir_bidrag_page():
    store = get_store()

    # page container (centered)
    with ui.element('div').classes('max-w-5xl px-4 md:px-12 py-12'):
        ui.label('Om det overordnete initiativet som aktivteten hører innunder') \
            .classes('text-2xl md:text-3xl font-semibold text-[#1E2B3C] mb-4')

        # form card
        with ui.card().classes('block w-full p-6 md:p-8 rounded-2xl shadow-lg bg-white form-card'):
            # responsive grid: 1 col on mobile, 2 cols from md
            with ui.element('div').classes('flex flex-col gap-5'):

                ui.input('1. Hva heter ...', value=store.get('navn_initiativ', '')) \
                    .props('outlined dense clearable color=primary').classes('w-full')

                ui.input('2. Hva er URL-en ...', value=store.get('url', '')) \
                    .props('outlined dense type=url clearable color=primary').classes('col-span-full')

                q3 = ui.select(
                        initiative_types,
                        label='3. Hvilken type initiativ er det?',
                        value=store.get('type', 'Annet')
                    ).props('outlined dense clearable options-dense color=primary').classes('w-full')

                # spans both columns when shown
                ui.input('Spesifiser type (ved "Annet")', value=store.get('type_annet', '')) \
                    .props('outlined dense clearable color=primary') \
                    .classes('w-full') \
                    .bind_visibility_from(q3, 'value', lambda v: v == 'Annet')

                q4 = ui.select(
                        org_options,
                        label='4. Hvilken organisasjon har ansvar ...',
                        value=store.get('ansvarlig_org', 'Annet')
                    ).props('outlined dense clearable options-dense color=primary').classes('w-full')

                ui.input('Spesifiser organisasjon (ved "Annet")', value=store.get('ansvarlig_org_annet', '')) \
                    .props('outlined dense clearable color=primary') \
                    .classes('w-full') \
                    .bind_visibility_from(q4, 'value', lambda v: v == 'Annet')

                ui.input('5. Hvem er kontaktpunkt ...', value=store.get('kontaktpunkt', '')) \
                    .props('outlined dense clearable color=primary').classes('w-full')

                ui.input('6. Hva er epostadressen ...', value=store.get('kontakt_epost', '')) \
                    .props('outlined dense type=email clearable color=primary').classes('w-full')

                # textarea spans both columns
                ui.textarea('7. Hva er hovedmålet ...', value=store.get('hovedmal', '')) \
                    .props('outlined autogrow clearable color=primary') \
                    .classes('w-full')

                q8 = ui.select(
                        geo_options,
                        label='8. Hvilket geografisk område dekker initiativet?',
                        value=store.get('geografi', 'Annet')
                    ).props('outlined dense clearable options-dense color=primary').classes('w-full')

                ui.input('Spesifiser geografisk område (ved "Annet")', value=store.get('geografi_annet', '')) \
                    .props('outlined dense clearable color=primary') \
                    .classes('w-full') \
                    .bind_visibility_from(q8, 'value', lambda v: v == 'Annet')

                q9 = ui.select(
                        domain_options,
                        label='9. Hvilke fagområder ...',
                        value=store.get('fagomrade', 'Annet')
                    ).props('outlined dense clearable options-dense color=primary').classes('w-full')

                ui.input('Spesifiser fagområde (ved "Annet")', value=store.get('fagomrade_annet', '')) \
                    .props('outlined dense clearable color=primary') \
                    .classes('col-span-6') \
                    .bind_visibility_from(q9, 'value', lambda v: v == 'Annet')

            # actions bar
            with ui.row().classes('justify-end gap-3 pt-12'):
                ui.button('Tilbake').props('flat color=primary')
                ui.button('Neste').props('color=primary')