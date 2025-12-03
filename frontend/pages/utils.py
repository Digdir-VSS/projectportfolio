from nicegui import ui
import ast

from models.ui_models import ProjectData
from models.validators import validate_budget_distribution

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
        if validate_budget_distribution(project.resursbehov.estimert_budsjet_behov, project.ressursbruk[2026].predicted_resources,project.ressursbruk[2027].predicted_resources,project.ressursbruk[2028].predicted_resources):
            return  False, "❌ Summen av ressursbehov for 2026–2028 stemmer ikke med totalbudsjettet."
    else:
        return True, ""

def layout(active_step: str, title: str, steps: dict[str, str]):
    ui.add_head_html('''
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@digdir/designsystemet-theme/brand/digdir.css">
    ''')
    # HEADER
    with ui.header(elevated=True).style('background-color: var(--ds-color-accent-base-default)'):
        ui.label(title).classes('text-h3').style('color: var(--ds-color-accent-base-contrast-default)')

    # LEFT DRAWER
    with ui.left_drawer(elevated=True, value=True).style('background-color: var(--ds-color-neutral-surface-tinted)'):
        with ui.stepper().props(
            'vertical header-nav'
        ).style('''
            --q-primary: var(--ds-color-accent-base-default);
            --q-secondary: var(--ds-color-success-base-default);
            --q-stepper-color: var(--ds-color-neutral-border-default);
        ''').classes('w-full') as stepper:
            for route, label in steps.items():
                ui.step(label).props(f'name={route} clickable') \
                    .on('click', lambda _, r=route: ui.navigate.to(f'/{r}'))
        
        # set active step
        stepper.value = active_step