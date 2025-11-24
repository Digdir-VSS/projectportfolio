from nicegui import ui

# from .utils import spacer

def dashboard():
    # box = spacer()
    
    with ui.element('div').classes('max-w-5xl px-0 md:px-2 py-2'):

        # ui.label('Embedding an external website:')
        ui.element("div").classes('text-lg font-bold mb-2')
        # Embed an iframe using ui.html
        # ui.html('<iframe title="Porteføljeoversikt" width="1767" height="774.25" src="https://app.powerbi.com/reportEmbed?reportId=499bd08d-2515-45e9-81be-c4b243dc6695&autoAuth=true&ctid=008e560f-08af-4cec-a056-b35447503991" frameborder="0" allowFullScreen="true"></iframe>')
        # ui.label('Content below the iframe.')
