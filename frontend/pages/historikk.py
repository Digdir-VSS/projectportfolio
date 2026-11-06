from datetime import date, datetime, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

import httpx
import pandas as pd
from nicegui import ui
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from frontend.pages.overview import OVERVIEW_TABLE_CSS
from frontend.utils.backend_client import api_get_historikk
from models.ui_models import HistorikkData
from models.validators import to_list

OSLO = ZoneInfo("Europe/Oslo")

# The columns in the Excel file, in order: (section in HistorikkData, field, column name).
# The names follow the forms. Budget years are added after BUDGET_COLUMNS_AFTER.
HISTORIKK_FELTER = [
    # Project page
    ("portfolioproject", "navn", "Navn på tiltak"),
    ("portfolioproject", "tiltakseier", "Tiltakseier (linjeleder)"),
    ("fremskritt", "fase", "Fase"),
    ("portfolioproject", "kontaktpersoner", "Kontaktperson"),
    ("portfolioproject", "oppstart", "Start"),
    ("fremskritt", "planlagt_ferdig", "Planlagt ferdig"),
    ("portfolioproject", "avdeling", "Ansvarlig enhet"),
    ("samarabeid", "samarbeid_intern", "Samarbeid internt"),
    ("samarabeid", "samarbeid_eksternt", "Samarbeid eksternt"),
    ("samarabeid", "avhengigheter_andre", "Avhengigheter andre oppgaver"),
    ("problemstilling", "problem", "Problemstilling"),
    ("tiltak", "tiltak_beskrivelse", "Beskrivelse av tiltaket og hovedleveranser for denne fasen"),
    ("risikovurdering", "vurdering", "Risiko hvis tiltaket ikke gjennomføres"),
    ("malbilde", "malbilde_1_beskrivelse", "1 Vi fremmer samordning og prioritering for en mer effektiv offentlig sektor"),
    ("malbilde", "malbilde_2_beskrivelse", "2 Vi leder an i ansvarlig og innovativ bruk av data og kunstig intelligens"),
    ("malbilde", "malbilde_3_beskrivelse", "3 Vi sikrer trygg tilgang til digitale tjenester for alle"),
    ("malbilde", "malbilde_4_beskrivelse", "4 Vi løser komplekse utfordringer sammen og tilpasser oss en verden i rask endring"),
    ("digitaliseringstrategi", "sammenheng_digital_strategi", "Tilknyttet tiltak i Digitaliseringsstrategien"),
    ("digitaliseringstrategi", "digital_strategi_kommentar", "Eventuell beskrivelse av kobling til Digitaliseringsstrategien"),
    ("resursbehov", "kompetanse_som_trengs", "Hvilke kompetanser trenges for tiltaket?"),
    ("resursbehov", "kompetanse_tilgjengelig", "Er kompetanser tilgjengelige internt"),
    ("resursbehov", "antall_mandsverk_intern", "Månedsverk interne"),
    ("resursbehov", "antall_mandsverk_ekstern", "Månedsverk eksterne"),
    ("resursbehov", "estimert_budsjet_behov", "Estimert budsjettbehov i kr"),
    ("resursbehov", "risiko_av_estimat", "Hvor sikkert er estimatet"),
    ("resursbehov", "estimert_budsjet_forklaring", "Forklaring estimat"),
    # Vurdering
    ("vurdering", "beslutningsstatus", "Beslutningsstatus"),
    ("vurdering", "mscw", "MSCW"),
    ("vurdering", "vurdert_risiko", "Vurdert risiko"),
    ("vurdering", "gruppe", "Gruppe"),
    ("vurdering", "pulje", "Pulje"),
    ("finansiering", "tildelte_midler", "Tildeling"),
    ("finansiering", "tildelte_midler_dekker", "Tildelingen dekker"),
    ("finansiering", "prosjekt_nummer", "Prosjektnummer i økonomisystemet"),
    ("samfunnseffekt", "effekt", "Samfunnseffekt"),
    ("vurdering", "begrunnelse", "Begrunnelse for anbefaling"),
    # Rapportering
    ("fremskritt", "fremskritt", "Status fremdrift"),
    ("delivery_risk", "risiko_rapportert", "Risiko fra rapportering"),
    ("delivery_risk", "risiko_rapportert_begrunnet", "Begrunnelse for risiko"),
    ("rapportering", "viktige_endringer", "Har det vært vesentlige endringer i forutsetninger og rammebetingelser siden siste rapportering?"),
    ("rapportering", "viktige_endringer_kommentar", "Er det endringer i hva tiltaket skal levere og når leveransene skal skje?"),
    ("avhengigheter", "avhengigheter", "Er det noen avhengigheter som er spesielt viktig for tiltaket?"),
]
BUDGET_COLUMNS_AFTER = "Estimert budsjettbehov i kr"

# These are stored as JSON lists
LIST_FIELDS = {"kontaktpersoner", "samarbeid_intern", "sammenheng_digital_strategi"}


def local_date(timestamp: datetime | None) -> date | None:
    """The Norwegian date of a sist_endret, which is stored as naive UTC."""
    if timestamp is None:
        return None
    return timestamp.replace(tzinfo=timezone.utc).astimezone(OSLO).date()


def date_text(value: date | None) -> str:
    return value.strftime("%d.%m.%Y") if value else ""


def latest_change(data: HistorikkData) -> tuple[datetime | None, str | None]:
    """When the project last changed before the chosen date, and who changed it."""
    sections = [getattr(data, name) for name in type(data).model_fields]
    sections = [section for section in sections if hasattr(section, "sist_endret")]
    sections += list((data.ressursbruk or {}).values())
    saved = [section for section in sections if section.sist_endret]
    if not saved:
        return None, None
    newest = max(saved, key=lambda section: section.sist_endret)
    return newest.sist_endret, newest.endret_av


def excel_value(field: str, value):
    if field in LIST_FIELDS:
        items = to_list(value)
        value = "; ".join(items) if isinstance(items, list) and items else value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        # Pasted text can hold characters Excel files can't store, and a leading "=" would
        # make Excel read the text as a formula
        value = ILLEGAL_CHARACTERS_RE.sub("", value)
        return f" {value}" if value.startswith("=") else value
    return value


def excel_row(data: HistorikkData, budget_years: list[int]) -> dict:
    row = {}
    for section, field, column in HISTORIKK_FELTER:
        row[column] = excel_value(field, getattr(getattr(data, section), field, None))
        if column == BUDGET_COLUMNS_AFTER:
            for year in budget_years:
                budget = (data.ressursbruk or {}).get(year)
                row[f"Budsjett {year}"] = budget.predicted_resources if budget else None

    changed_at, changed_by = latest_change(data)
    row["Sist vurdert"] = local_date(data.vurdering.sist_endret)
    row["Sist rapportert"] = local_date(data.rapportering.sist_endret)
    row["Sist endret"] = local_date(changed_at)
    row["Endret av"] = changed_by
    row["Slettet"] = local_date(data.slettet)
    return row


def create_excel(historikk: list[HistorikkData]) -> bytes:
    budget_years = sorted({year for data in historikk for year in (data.ressursbruk or {})})
    rows = [excel_row(data, budget_years) for data in historikk]
    buffer = BytesIO()
    pd.DataFrame(rows).to_excel(buffer, index=False)
    return buffer.getvalue()


def table_row(data: HistorikkData, dato: str) -> dict:
    changed_at, changed_by = latest_change(data)
    navn = data.portfolioproject.navn or ""
    if data.slettet:
        navn = f"{navn} (slettet {date_text(local_date(data.slettet))})"
    return {
        "prosjekt_id": str(data.prosjekt_id),
        "dato": dato,
        "navn": navn,
        "avdeling": data.portfolioproject.avdeling,
        "fase": data.fremskritt.fase,
        "tiltakseier": data.portfolioproject.tiltakseier,
        "beslutningsstatus": data.vurdering.beslutningsstatus,
        "fremdrift": data.fremskritt.fremskritt,
        "risiko": data.delivery_risk.risiko_rapportert,
        "sist_endret": date_text(local_date(changed_at)),
        "endret_av": changed_by,
    }


TABLE_COLUMNS = [
    ("navn", "Navn"),
    ("avdeling", "Ansvarlig enhet"),
    ("fase", "Fase"),
    ("tiltakseier", "Tiltakseier"),
    ("beslutningsstatus", "Beslutningsstatus"),
    ("fremdrift", "Status fremdrift"),
    ("risiko", "Status risiko"),
    ("sist_endret", "Sist endret"),
    ("endret_av", "Endret av"),
]


async def historikk_page():
    ui.add_css(OVERVIEW_TABLE_CSS)
    today = datetime.now(OSLO).date().isoformat()
    historikk: list[HistorikkData] = []

    async def load():
        nonlocal historikk
        dato = date_input.value
        if not dato:
            return
        try:
            result = await api_get_historikk(dato)
        except httpx.HTTPError:
            ui.notify("Kunne ikke hente historikk", type="negative")
            return
        if dato != date_input.value:  # another date was chosen in the meantime
            return
        historikk = sorted(result, key=lambda data: (data.portfolioproject.navn or "").casefold())
        table.rows = [table_row(data, dato) for data in historikk]
        table.update()
        count.text = f"{len(historikk)} prosjekter"

    def download():
        if not historikk:
            ui.notify("Ingen prosjekter å laste ned for denne datoen", type="warning")
            return
        ui.download.content(create_excel(historikk), f"prosjekter_{date_input.value}.xlsx")

    ui.label("Velg en dato for å se hvordan prosjektene så ut ved slutten av den dagen.").classes("text-sm italic")
    with ui.row().classes("items-center gap-4"):
        date_input = ui.input("Dato", value=today, on_change=load).props(f"type=date outlined dense stack-label max={today}")
        ui.button("Last ned", icon="download", on_click=download).props("color=primary")
        count = ui.label("")

    columns = [{"name": "vis", "label": "", "field": "vis", "sortable": False, "align": "left"}]
    for field, label in TABLE_COLUMNS:
        column = {"name": field, "label": label, "field": field, "sortable": True, "align": "left", "classes": "whitespace-normal"}
        if field == "navn":
            column["style"] = "width: 30%; min-width: 200px"
        columns.append(column)

    table = ui.table(
        columns=columns,
        rows=[],
        row_key="prosjekt_id",
        column_defaults={"headerClasses": "uppercase text-primary whitespace-normal"},
    ).classes("w-full overview-table")
    table.add_slot(
        "body-cell-vis",
        r"""
        <q-td auto-width>
            <q-btn
                size="sm"
                color="primary"
                dense
                no-caps
                label="Vis prosjekt"
                class="q-px-sm"
                :href="'/historikk/' + props.row.prosjekt_id + '?dato=' + props.row.dato"
            />
        </q-td>
        """,
    )
    await load()
