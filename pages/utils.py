from nicegui import ui

def spacer(width: int | None = None, height: int | None = None):
    box = ui.element('div').classes('shrink-0')
    if width:
        box.style(f'width:{width}px;')
    if height:
        box.style(f'height:{height}px;')
    return box