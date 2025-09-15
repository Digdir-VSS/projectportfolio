from nicegui import ui

from .utils import spacer

def main_display():
    box = spacer()
    
    with ui.element('div').classes('max-w-5xl px-4 md:px-12 py-12'):

        ui.label('Embedding an external website:')

        # Embed an iframe using ui.html
        ui.html('<iframe  title="internasjonale_aktiviteter_digdir" src="https://app.powerbi.com/reportEmbed?reportId=ef9f91a2-6c31-4b46-8351-6542efde0fd5&autoAuth=true&ctid=008e560f-08af-4cec-a056-b35447503991" width="1800" height="900" frameborder="0" allowFullScreen="true"></iframe>')
        ui.label('Content below the iframe.')
