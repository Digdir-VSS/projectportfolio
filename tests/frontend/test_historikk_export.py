from datetime import date, datetime
from io import BytesIO
from uuid import uuid4

import pandas as pd

from frontend.pages.historikk import HISTORIKK_FELTER, create_excel, latest_change, local_date, table_row
from models.ui_models import (
    AvhengigheterUI,
    DeliveryRiskUI,
    DigitaliseringStrategiUI,
    FinansieringUI,
    FremskrittUI,
    HistorikkData,
    MalbildeUI,
    PortfolioProjectUI,
    ProblemstillingUI,
    RapporteringUI,
    ResursbehovUI,
    RessursbrukUI,
    RisikovurderingUI,
    SamarabeidUI,
    SamfunnsEffektUI,
    TiltakUI,
    VurderingUI,
)


def project(**overrides) -> HistorikkData:
    sections = {
        "fremskritt": FremskrittUI(fase="Konsept", fremskritt="På plan", planlagt_ferdig=datetime(2026, 12, 1)),
        "samarabeid": SamarabeidUI(samarbeid_intern='["DSS", "KOM"]'),
        "portfolioproject": PortfolioProjectUI(navn="Prosjekt", avdeling="DSS", kontaktpersoner='["Ola", "Kari"]'),
        "problemstilling": ProblemstillingUI(),
        "tiltak": TiltakUI(),
        "risikovurdering": RisikovurderingUI(vurdering="Tekst"),
        "malbilde": MalbildeUI(),
        "resursbehov": ResursbehovUI(estimert_budsjet_behov=300),
        "digitaliseringstrategi": DigitaliseringStrategiUI(),
        "vurdering": VurderingUI(beslutningsstatus="Vedtatt", sist_endret=datetime(2026, 5, 1, 12, 0)),
        "finansiering": FinansieringUI(),
        "samfunnseffekt": SamfunnsEffektUI(),
        "rapportering": RapporteringUI(sist_endret=datetime(2026, 4, 1, 12, 0), endret_av="ola@digdir.no"),
        "delivery_risk": DeliveryRiskUI(risiko_rapportert="Høy"),
        "avhengigheter": AvhengigheterUI(),
        "ressursbruk": {2027: RessursbrukUI(year=2027, predicted_resources=100), 2026: RessursbrukUI(year=2026, predicted_resources=200)},
    }
    return HistorikkData(prosjekt_id=uuid4(), **{**sections, **overrides})


def read_excel(historikk) -> pd.DataFrame:
    return pd.read_excel(BytesIO(create_excel(historikk)))


def test_every_form_field_becomes_a_column():
    columns = list(read_excel([project()]).columns)

    assert [name for _, _, name in HISTORIKK_FELTER if name not in columns] == []


def test_budget_years_follow_the_total_in_year_order():
    columns = list(read_excel([project()]).columns)
    total = columns.index("Estimert budsjettbehov i kr")

    assert columns[total + 1:total + 3] == ["Budsjett 2026", "Budsjett 2027"]


def test_budget_years_are_collected_across_projects():
    without_budget = project(ressursbruk={})
    with_budget = project(ressursbruk={2029: RessursbrukUI(year=2029, predicted_resources=5)})

    assert "Budsjett 2029" in read_excel([without_budget, with_budget]).columns


def test_lists_are_written_as_readable_text():
    row = read_excel([project()]).iloc[0]

    assert row["Kontaktperson"] == "Ola; Kari"
    assert row["Samarbeid internt"] == "DSS; KOM"


def test_text_excel_cannot_store_does_not_break_the_file():
    pasted = project(risikovurdering=RisikovurderingUI(vurdering="Linje\x0bto"))

    assert read_excel([pasted]).iloc[0]["Risiko hvis tiltaket ikke gjennomføres"] == "Linjeto"


def test_text_starting_with_equals_stays_text():
    formula = project(risikovurdering=RisikovurderingUI(vurdering="=1+1 er to"))

    assert read_excel([formula]).iloc[0]["Risiko hvis tiltaket ikke gjennomføres"] == " =1+1 er to"


def test_latest_change_looks_across_sections():
    assert latest_change(project()) == (datetime(2026, 5, 1, 12, 0), None)


def test_saved_time_is_shown_as_norwegian_date():
    assert local_date(datetime(2026, 6, 30, 22, 30)) == date(2026, 7, 1)


def test_table_row_marks_deleted_projects():
    row = table_row(project(slettet=datetime(2026, 3, 1, 12, 0)), "2026-02-01")

    assert row["navn"] == "Prosjekt (slettet 01.03.2026)"
    assert row["dato"] == "2026-02-01"
