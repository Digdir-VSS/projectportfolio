from nicegui import ui
import ast

from models.ui_models import ProjectData
from models.validators import validate_budget_distribution
import copy

def validate_kontaktpersoner(kontaktpersoner: str | None, msg: str) -> tuple[bool, str]:
    if kontaktpersoner is None:
        return  False, msg
    kontaktpersoner_list = ast.literal_eval(kontaktpersoner) if kontaktpersoner else []
    if not kontaktpersoner_list:
        return  False, msg
    return True, ""

def validate_project_navn(project_navn: str | None, msg: str) -> tuple[bool, str]:
    if not project_navn:
        return  False, msg
    if project_navn.strip() == "":
        return  False, msg
    return True, ""

def validate_tiltakseier(tiltakseier: str | None, msg: str) -> tuple[bool, str]:
    if tiltakseier is None:
        return False, msg
    if not tiltakseier:
        return False, msg
    else:
        return True, ""
    
def validate_send_schema(project: ProjectData) -> tuple[bool, str]:
    validation_navn, message_navn = validate_project_navn(project.portfolioproject.navn, msg="❌ Du må fylle inn tiltaksnavn.")
    if not validation_navn:
        return validation_navn, message_navn

    validation_kontaktperson, message_kontaktperson = validate_kontaktpersoner(project.portfolioproject.kontaktpersoner, msg="❌ Du må fylle inn kontaktperson.")
    if not validation_kontaktperson:
        return validation_kontaktperson, message_kontaktperson
    
    validation_tiltakseier, message_tiltakseier = validate_tiltakseier(project.portfolioproject.tiltakseier, msg="❌ Du må fylle inn tiltakseier.")
    if not validation_tiltakseier:
        return validation_tiltakseier, message_tiltakseier

    if project.ressursbruk[2026].predicted_resources or project.ressursbruk[2027].predicted_resources or project.ressursbruk[2028].predicted_resources:
        is_invaid = validate_budget_distribution(project.resursbehov.estimert_budsjet_behov, project.ressursbruk[2026].predicted_resources,project.ressursbruk[2027].predicted_resources,project.ressursbruk[2028].predicted_resources)
        if is_invaid:   
            return  False, "❌ Summen av ressursbehov for 2026–2028 stemmer ikke med totalbudsjettet."
    return True, ""


def layout(title: str, menu_items: dict[str, dict], active_route: str):
    ui.timer(interval=30, callback=lambda: ui.run_javascript('0'), once=False)
    ui.add_head_html('''
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@digdir/designsystemet-theme/brand/digdir.css">
    ''')

    dark_blue = '#0D2B5B'
    active_color = 'grey-6'
    with ui.header(elevated=True).classes('bg-primary text-white'):
        with ui.row().classes('items-center no-wrap w-full'):

            # placeholder, assigned after drawer is created
            menu_button = ui.button(icon='menu').props('flat dense round')

            ui.label(title).classes('text-h6 q-ml-md')

    # ---- LEFT DRAWER ----
    with ui.left_drawer(elevated=True, value=True,
    fixed=True).style('background-color: var(--ds-color-neutral-surface-tinted)') as drawer:

        with ui.list().props('dense padding'):
            for route, item in menu_items.items():
                is_active = route == active_route
                with ui.item(
                    on_click=lambda _, r=route: (
                        drawer.set_value(True),
                        ui.navigate.to(f'/{r}')
                    ),
                ).classes(
                    '' if is_active else 'text-grey-6'  # inactive items grey
                ):
                    if icon := item.get('icon'):
                        with ui.item_section().props('avatar'):
                            ui.icon(icon).style(
                                f'color: {dark_blue if is_active else "var(--q-grey-6)"}'
                            )

                    with ui.item_section():
                     ui.label(item['label']).style(
                            f'color: {dark_blue if is_active else "var(--q-grey-6)"}'
                        )

    # ---- wire button AFTER drawer exists ----
    menu_button.on(
        'click',
        lambda: drawer.set_value(not drawer.value)
    )
def get_menu_items_for_user(user: dict, super_user: list, STEPS_DICT: dict) -> dict:
    email = user.get("preferred_username")

    # start with a copy so we don’t mutate the original
    menu = copy.deepcopy(STEPS_DICT)

    # hide "vurdering" for non-super users
    if email not in super_user:
        menu.pop("vurdering", None)

    return menu