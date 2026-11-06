from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.dml import Update
from sqlmodel import Session, SQLModel

from backend.database import db_connection
from backend.database.db_connection import HISTORIKK_SECTIONS, DBConnector
from backend.database.historikk import deleted_projects, end_of_day_utc, latest_versions
from models.sql_models import DeliveryRisk, Fremskritt, PortfolioProject, Ressursbruk, Tiltak, Vurdering, schema_name


def version(project, saved, current=False, year=None):
    return SimpleNamespace(prosjekt_id=project, sist_endret=saved, er_gjeldende=current, year=year)


def test_end_of_day_follows_norwegian_summer_time():
    assert end_of_day_utc(date(2026, 6, 30)) == datetime(2026, 6, 30, 22, 0)


def test_end_of_day_follows_norwegian_winter_time():
    assert end_of_day_utc(date(2026, 1, 31)) == datetime(2026, 1, 31, 23, 0)


def test_latest_version_is_kept_per_project():
    old = version("A", datetime(2026, 1, 1))
    new = version("A", datetime(2026, 2, 1))
    other = version("B", datetime(2026, 1, 15))

    result = latest_versions([new, other, old])

    assert result == {"a": new, "b": other}


def test_latest_version_can_be_kept_per_year():
    budget_2026 = version("A", datetime(2026, 1, 1), year=2026)
    budget_2027 = version("A", datetime(2026, 2, 1), year=2027)

    result = latest_versions([budget_2026, budget_2027], key=lambda row: row.year)

    assert result == {2026: budget_2026, 2027: budget_2027}


def test_project_without_current_row_is_deleted_at_its_newest_row():
    deleted_at = datetime(2026, 3, 1)
    versions = [version("A", datetime(2026, 1, 1)), version("A", deleted_at)]

    assert deleted_projects(versions) == {"a": deleted_at}


def test_project_with_current_row_is_not_deleted():
    versions = [version("A", datetime(2026, 1, 1)), version("A", datetime(2026, 2, 1), current=True)]

    assert deleted_projects(versions) == {}


def run_delete(monkeypatch, last_version):
    session = MagicMock()
    session.exec.return_value.first.return_value = last_version
    context = MagicMock()
    context.__enter__.return_value = session
    monkeypatch.setattr(db_connection, "Session", MagicMock(return_value=context))

    deleted_at = datetime(2026, 11, 5, 12, 0)
    db_connection.delete_prosjekt(MagicMock(), last_version.prosjekt_id, [PortfolioProject, Tiltak], deleted_at, "admin@digdir.no")
    return session, deleted_at


def test_delete_keeps_the_saved_time_of_each_version(monkeypatch):
    last_version = PortfolioProject(prosjekt_id=uuid4(), navn="Prosjekt", sist_endret=datetime(2026, 1, 1), er_gjeldende=True)

    session, _ = run_delete(monkeypatch, last_version)

    updates = [call.args[0] for call in session.exec.call_args_list if isinstance(call.args[0], Update)]
    assert len(updates) == 2
    for statement in updates:
        assert [column.key for column in statement._values] == ["er_gjeldende"]


def test_delete_records_when_the_project_was_deleted(monkeypatch):
    last_version = PortfolioProject(prosjekt_id=uuid4(), navn="Prosjekt", sist_endret=datetime(2026, 1, 1), er_gjeldende=True)

    session, deleted_at = run_delete(monkeypatch, last_version)

    deletion = session.add.call_args.args[0]
    assert deletion.navn == "Prosjekt"
    assert deletion.sist_endret == deleted_at
    assert deletion.endret_av == "admin@digdir.no"
    assert deletion.er_gjeldende is False
    assert deletion.prosjekt_sk_id != last_version.prosjekt_sk_id
    session.commit.assert_called_once()


# --- get_historikk against a real database ---------------------------------------

@compiles(UNIQUEIDENTIFIER, "sqlite")
def uniqueidentifier_on_sqlite(element, compiler, **kwargs):
    return "CHAR(36)"


@pytest.fixture
def connector():
    engine = create_engine("sqlite://").execution_options(schema_translate_map={schema_name: None})
    models = [model for model, _ in HISTORIKK_SECTIONS.values()] + [Ressursbruk]
    SQLModel.metadata.create_all(engine, tables=[model.__table__ for model in models])
    return DBConnector(engine, {})


def save(connector, *rows):
    with Session(connector.engine) as session:
        session.add_all(rows)
        session.commit()


def project_row(project, navn, saved, current=False):
    return PortfolioProject(prosjekt_id=project, navn=navn, sist_endret=saved, er_gjeldende=current)


def test_history_shows_the_version_saved_before_the_date(connector):
    project = uuid4()
    save(connector,
         project_row(project, "Gammelt navn", datetime(2026, 1, 10, 9)),
         project_row(project, "Nytt navn", datetime(2026, 3, 10, 9), current=True))

    assert connector.get_historikk(date(2026, 2, 1))[0].portfolioproject.navn == "Gammelt navn"
    assert connector.get_historikk(date(2026, 4, 1))[0].portfolioproject.navn == "Nytt navn"


def test_a_change_late_in_the_evening_belongs_to_the_norwegian_date(connector):
    project = uuid4()
    save(connector,
         project_row(project, "Før", datetime(2026, 6, 1, 9)),
         project_row(project, "Etter", datetime(2026, 6, 30, 21, 30), current=True),
         )

    assert connector.get_historikk(date(2026, 6, 30))[0].portfolioproject.navn == "Etter"


def test_each_section_uses_its_own_latest_version(connector):
    project = uuid4()
    save(connector,
         project_row(project, "Navn", datetime(2026, 1, 1), current=True),
         Fremskritt(prosjekt_id=project, fase="Konsept", sist_endret=datetime(2026, 1, 1)),
         Fremskritt(prosjekt_id=project, fase="Planlegging", sist_endret=datetime(2026, 5, 1), er_gjeldende=True),
         Vurdering(prosjekt_id=project, beslutningsstatus="Vedtatt", sist_endret=datetime(2026, 2, 1), er_gjeldende=True),
         DeliveryRisk(prosjekt_id=project, risiko_rapportert="Høy", sist_endret=datetime(2026, 2, 15), er_gjeldende=True))

    result = connector.get_historikk(date(2026, 3, 1))[0]

    assert result.fremskritt.fase == "Konsept"
    assert result.vurdering.beslutningsstatus == "Vedtatt"
    assert result.delivery_risk.risiko_rapportert == "Høy"


def test_sections_saved_later_are_empty(connector):
    project = uuid4()
    save(connector,
         project_row(project, "Navn", datetime(2026, 1, 1), current=True),
         Vurdering(prosjekt_id=project, beslutningsstatus="Vedtatt", sist_endret=datetime(2026, 5, 1), er_gjeldende=True))

    assert connector.get_historikk(date(2026, 2, 1))[0].vurdering.beslutningsstatus is None


def test_budget_is_tracked_per_year(connector):
    project = uuid4()
    save(connector,
         project_row(project, "Navn", datetime(2026, 1, 1), current=True),
         Ressursbruk(prosjekt_id=project, year=2026, predicted_resources=100, sist_endret=datetime(2026, 1, 1)),
         Ressursbruk(prosjekt_id=project, year=2026, predicted_resources=150, sist_endret=datetime(2026, 5, 1), er_gjeldende=True),
         Ressursbruk(prosjekt_id=project, year=2027, predicted_resources=200, sist_endret=datetime(2026, 1, 1), er_gjeldende=True))

    budget = connector.get_historikk(date(2026, 2, 1))[0].ressursbruk

    assert {year: row.predicted_resources for year, row in budget.items()} == {2026: 100, 2027: 200}


def test_project_created_after_the_date_is_left_out(connector):
    save(connector, project_row(uuid4(), "Navn", datetime(2026, 5, 1), current=True))

    assert connector.get_historikk(date(2026, 2, 1)) == []


def test_deleted_project_only_appears_while_it_existed(connector):
    project = uuid4()
    deleted_at = datetime(2026, 5, 1, 9)
    save(connector,
         project_row(project, "Navn", datetime(2026, 1, 1)),
         project_row(project, "Navn", deleted_at))

    before = connector.get_historikk(date(2026, 2, 1))

    assert before[0].slettet == deleted_at
    assert connector.get_historikk(date(2026, 5, 1)) == []
    assert connector.get_historikk(date(2026, 6, 1)) == []


def test_one_project_can_be_requested(connector):
    wanted, other = uuid4(), uuid4()
    save(connector,
         project_row(wanted, "Denne", datetime(2026, 1, 1), current=True),
         project_row(other, "Andre", datetime(2026, 1, 1), current=True))

    result = connector.get_historikk(date(2026, 2, 1), str(wanted))

    assert [data.portfolioproject.navn for data in result] == ["Denne"]


def test_begrunnelse_is_saved_with_the_vurdering():
    from backend.database.db_connection import ui_to_sqlmodel
    from models.ui_models import VurderingUI

    row = ui_to_sqlmodel(VurderingUI(begrunnelse="Fordi"), Vurdering)

    assert row.begrunnelse == "Fordi"


def test_begrunnelse_appears_in_history(connector):
    project = uuid4()
    save(connector,
         project_row(project, "Navn", datetime(2026, 1, 1), current=True),
         Vurdering(prosjekt_id=project, begrunnelse="Fordi", sist_endret=datetime(2026, 1, 2), er_gjeldende=True))

    assert connector.get_historikk(date(2026, 2, 1))[0].vurdering.begrunnelse == "Fordi"
