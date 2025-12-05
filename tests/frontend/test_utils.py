# test_validators.py
from frontend.pages.utils import validate_budget_distribution, validate_kontaktpersoner, validate_project_navn, validate_tiltakseier, validate_send_schema
import ast
from types import SimpleNamespace
import pytest


# --- Helpers -----------------------------------------------------------------

def make_project(
    navn="Prosjekt X",
    kontaktpersoner_str="[{'navn': 'Ola Nordmann'}]",
    tiltakseier="Enhet A",
    predicted_2026=None,
    predicted_2027=None,
    predicted_2028=None,
    total_budget=100,
):
    """Create a minimal fake ProjectData object."""

    portfolioproject = SimpleNamespace(
        navn=navn,
        kontaktpersoner=kontaktpersoner_str,
        tiltakseier=tiltakseier,
    )

    ressursbruk = {
        2026: SimpleNamespace(predicted_resources=predicted_2026),
        2027: SimpleNamespace(predicted_resources=predicted_2027),
        2028: SimpleNamespace(predicted_resources=predicted_2028),
    }

    resursbehov = SimpleNamespace(
        estimert_budsjet_behov=total_budget
    )

    return SimpleNamespace(
        portfolioproject=portfolioproject,
        ressursbruk=ressursbruk,
        resursbehov=resursbehov,
    )


# --- validate_kontaktpersoner ------------------------------------------------

def test_validate_kontaktpersoner_missing():
    valid, msg = validate_kontaktpersoner(None, msg="❌ Du må fylle inn kontaktpersoner.")
    assert valid is False
    assert "kontaktperson" in msg


def test_validate_kontaktpersoner_empty_list_string():
    valid, msg = validate_kontaktpersoner("[]",  msg="❌ Du må fylle inn kontaktpersoner.")
    assert valid is False
    assert "kontaktperson" in msg


def test_validate_kontaktpersoner_ok():
    kontaktpersoner = str(["Ola", "Kari"])
    valid, msg = validate_kontaktpersoner(kontaktpersoner, msg="❌ Du må fylle inn kontaktpersoner.")
    # EXPECTED behaviour: this should be valid
    assert valid is True
    assert msg == ""


# --- validate_project_navn ---------------------------------------------------

def test_validate_project_navn_missing():
    valid, msg = validate_project_navn(None, msg="❌ Du må fylle inn tiltaksnavn.")
    assert valid is False
    assert "tiltaksnavn" in msg


def test_validate_project_navn_empty_string():
    valid, msg = validate_project_navn("   ", msg="❌ Du må fylle inn tiltaksnavn.")
    assert valid is False
    assert "tiltaksnavn" in msg


def test_validate_project_navn_ok():
    valid, msg = validate_project_navn("Prosjekt X", msg="Test")
    # EXPECTED behaviour: non-empty name is valid
    assert valid is True
    assert msg == ""


# --- validate_tiltakseier ----------------------------------------------------

def test_validate_tiltakseier_missing():
    valid, msg = validate_tiltakseier(None, msg="❌ Du må fylle inn tiltakseier.")
    assert valid is False
    assert "tiltakseier" in msg


def test_validate_tiltakseier_ok():
    valid, msg = validate_tiltakseier("Enhet A", msg="Test")
    # EXPECTED behaviour: non-empty owner is valid
    assert valid is True
    assert msg == ""


# --- validate_send_schema: field-level checks --------------------------------

def test_validate_send_schema_fails_on_missing_name_first():
    project = make_project(navn="", kontaktpersoner_str="[]", tiltakseier=None)

    valid, msg = validate_send_schema(project)

    assert valid is False
    # Should fail on name first (because it is validated first)
    assert "tiltaksnavn" in msg


def test_validate_send_schema_fails_on_missing_kontaktperson_second():
    project = make_project(
        navn="Prosjekt X",
        kontaktpersoner_str="[]",
        tiltakseier="Enhet A",
    )

    valid, msg = validate_send_schema(project)

    assert valid is False
    assert "kontaktperson" in msg