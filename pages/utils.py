from typing import Any, Callable

from nicegui import ui
import requests
import jwt
from jwt.algorithms import RSAAlgorithm
import os 
from dotenv import load_dotenv

load_dotenv()

def _get_tenant_public_key_for_key_id(key_id, tenant_name):
    """
    Obtain the public key used by Azure AD to sign tokens.

    Note that this method obtains all public keys on every call. This could be optimised by caching these keys and/or by
    only obtaining keys that are not yet present in the cache.
    """
    jwks_url = f"https://login.microsoftonline.com/{tenant_name}/discovery/v2.0/keys"
    response = requests.get(jwks_url)
    jwks = response.json()

    # Find the correct key from the available keys
    key = next((key for key in jwks["keys"] if key["kid"] == key_id), None)

    # Attempt to extract the actual public key
    if key:
        public_key = RSAAlgorithm.from_jwk(key)
    else:
        raise Exception("Public key not found")

    return public_key


def validate_token(jwt_token, tenant_name):
    """Validate the JWT token using the public key from Azure AD."""

    # Obtain relevant specifications from the JWT token
    header = jwt.get_unverified_header(jwt_token)
    algorithm = header["alg"]
    key_id = header["kid"]

    # Obtain the Azure public key corresponding to our tenant and the given `key_id` that was included in the JWT token.
    tenant_public_key = _get_tenant_public_key_for_key_id(key_id, tenant_name)

    try:
        # Decode the token, verifying the signature and claims
        decoded_token = jwt.decode(jwt_token, tenant_public_key, algorithms=[algorithm], audience=os.getenv("CLIENT_ID"))
        return decoded_token
    except jwt.PyJWTError as e:
        print(f"Token validation error: {e}")
        return None



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

        #     ui.step('Oversikt over dine prosjekter').props('name=oversikt clickable') \
        #         .on('click', lambda: ui.navigate.to('/'))
        #     ui.step('Overordnet info').props('name=overordnet clickable') \
        #         .on('click', lambda: ui.navigate.to('/overordnet'))
        #     ui.step('Om Digdirs aktivitet').props('name=aktivitet clickable') \
        #         .on('click', lambda: ui.navigate.to('/digdir_aktivitet'))
        #     ui.step('Om Digdirs leveranse').props('name=leveranse clickable') \
        #         .on('click', lambda: ui.navigate.to('/leveranse'))
        # stepper.value = active_step


def input_field(
    cache_model: Any,
    field_name: str,
    label: str,
    validation: Callable[[str], str | None] | None = None,
) -> None:
    """Render an input field bound to a cache_model attribute."""
    with ui.element("div").classes("flex flex-col gap-1"):
        ui.html(label)
        ui.input(validation=validation).bind_value(cache_model, field_name).props(
            "outlined dense clearable color=primary"
        ).classes("w-full")


def input_field_date(cache_model: Any, field_name: str, label: str) -> None:
    """Render a date input field bound to a cache_model attribute."""
    with ui.element("div").classes("flex flex-col gap-1"):
        ui.html(label)
        ui.input().bind_value(cache_model, field_name).props(
            "outlined dense type=date clearable color=primary"
        ).classes("w-full")


def select_field(
    cache_model: Any, field_name: str, label: str, categories: list[str]
) -> None:
    """Render a select dropdown with optional 'Annet' input field."""
    with ui.element("div").classes("flex flex-col gap-1"):
        ui.html(label)
        select = (
            ui.select(categories)
            .bind_value(cache_model, field_name)
            .props("outlined dense clearable options-dense color=primary")
            .classes("w-full")
        )

        ui.input("Spesifiser annet...").bind_visibility_from(
            select, "value", lambda v: v == "Annet"
        ).bind_value(cache_model, f"{field_name}_annet").props(
            "outlined dense clearable color=primary"
        ).classes(
            "w-full"
        )


def text_area_field(
    cache_model: Any, field_name: str, label: str, rows: int = 6, h_size: int = 40
) -> None:
    """Render a textarea field."""
    with ui.element("div").classes("flex flex-col gap-1"):
        ui.html(label)
        ui.textarea().bind_value(cache_model, field_name).props(
            f"outlined clearable color=primary rows={rows}"
        ).classes(f"w-full h-{h_size}")


def check_box(
    cache_model: Any, field_name: str, label: str, boxes: list[str], rows: int = 2
) -> None:
    """Render a group of checkboxes, including optional 'Annet' input."""
    with ui.element("div").classes("flex flex-col gap-1"):
        ui.html(label)

        number_of_cols = int(len(boxes) / rows) or 1

        with ui.element("div").classes(f"grid grid-cols-{number_of_cols} gap-5 w-full"):
            for box_name in boxes:
                box_name = box_name.replace(" ", "_")
                key = f"{field_name}_{box_name}"

                # Ensure default is False instead of None
                if getattr(cache_model, key, None) is None:
                    setattr(cache_model, key, False)

                checkbox = ui.checkbox(box_name).bind_value(cache_model, key)

                if box_name.lower() == "annet":
                    ui.input("Spesifiser annet...").bind_visibility_from(
                        checkbox, "value"
                    ).bind_value(cache_model, f"{field_name}_Annet").props(
                        "outlined dense clearable color=primary"
                    ).classes(
                        f"w-full col-span-{number_of_cols}"
                    )


def radio_box(
    cache_model: Any, field_name: str, label: str, boxes: list[str], rows: int = 2
) -> None:
    """Render a radio group with optional 'Annet' input."""
    with ui.element("div").classes("flex flex-col gap-1"):
        ui.html(label)
        with ui.element("div").classes(f"grid grid-cols-1 gap-1 w-full"):
            radio = ui.radio(boxes).bind_value(cache_model, field_name).props("inline")

            ui.input("Spesifiser annet...").bind_visibility_from(
                radio, "value", lambda v: v == "Annet"
            ).bind_value(cache_model, f"{field_name}_annet").props(
                "outlined dense clearable color=primary"
            ).classes(
                "w-full"
            )
