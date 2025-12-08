from fastapi.testclient import TestClient
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import uuid
from unittest.mock import patch
import uuid

from backend.innlevering_router import router

load_dotenv()

API_KEY = os.getenv("INNLEVERING_API_KEY")

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_new_innnleverings_prosjekt():
    payload = {"email": "test@example.com", "prosjekt_id": str(uuid.uuid4())}
    response = client.post(
        "/api/innlevering/ny_prosjekt", headers={"x-api-key": API_KEY}, json=payload
    )
    assert response.status_code == 200
    output_data = response.json()
    assert output_data["portfolioproject"]["epost_kontakt"] == payload["email"]
    for name, dataclass in output_data.items():
        """Remove after ressurbruk refactor"""
        if name != "ressursbruk":
            assert dataclass["prosjekt_id"] == payload["prosjekt_id"]
    response = client.post(
        "/api/innlevering/ny_prosjekt", headers={"x-api-key": "abc"}, json=payload
    )
    assert response.status_code == 401


def test_get_innnleverings_prosjekter():
    parameter = {
        "email": "test@example.com",
    }
    response = client.get(
        "/api/innlevering/prosjekter", headers={"x-api-key": API_KEY}, params=parameter
    )
    assert response.status_code == 200
    assert response.json() == []

    response = client.get(
        "/api/innlevering/prosjekter",
        headers={"x-api-key": "API_KEY"},
        params=parameter,
    )
    assert response.status_code == 401


def test_get_innnleverings_prosjekter_with_results():
    fake_projects = [
        {
            "prosjekt_id": "ABC123",
            "navn": "Testprosjekt 1",
            "epost_kontakt": "test@example.com",
        },
        {
            "prosjekt_id": "XYZ999",
            "navn": "Testprosjekt 2",
            "epost_kontakt": "test@example.com",
        },
    ]

    with patch(
        "backend.innlevering_router.db_connector.get_projects",
        return_value=fake_projects,
    ):
        response = client.get(
            "/api/innlevering/prosjekter",
            headers={"x-api-key": API_KEY},
            params={"email": "test@example.com"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data == fake_projects


def test_get_prosjekt():
    prosjekt_id = str(uuid.uuid4())

    fake_project = {
        "fremskritt": {
            "fremskritt_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "fremskritt": "",
            "fase": "",
            "planlagt_ferdig": None,
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": None,
        },
        "samarabeid": {
            "samarbeid_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "samarbeid_intern": "",
            "samarbeid_eksternt": "",
            "avhengigheter_andre": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "portfolioproject": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "navn": "Testprosjekt",
            "oppstart": None,
            "avdeling": "",
            "tiltakseier": "",
            "kontaktpersoner": "",
            "epost_kontakt": "test@example.com",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "problemstilling": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
        },
        "tiltak": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
        },
        "risikovurdering": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
        },
        "malbilde": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
        },
        "resursbehov": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
        },
        "digitaliseringstrategi": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
        },
        "ressursbruk": {},
    }

    with patch("backend.innlevering_router.db_connector") as mock_db:
        mock_db.get_single_project.return_value = fake_project

        response = client.get(
            f"/api/innlevering/prosjekt/{prosjekt_id}",
            headers={"x-api-key": API_KEY},
        )

    assert response.status_code == 200
    data = response.json()

    assert data["portfolioproject"]["epost_kontakt"] == "test@example.com"
    for section in data.values():
        if isinstance(section, dict) and "prosjekt_id" in section:
            assert section["prosjekt_id"] == prosjekt_id


def test_update_prosjekt():
    prosjekt_id = str(uuid.uuid4())
    e_mail = "test@example.com"

    fake_project = {
        "fremskritt": {
            "fremskritt_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "fremskritt": "",
            "fase": "",
            "planlagt_ferdig": None,
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": None,
        },
        "samarabeid": {
            "samarbeid_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "samarbeid_intern": "",
            "samarbeid_eksternt": "",
            "avhengigheter_andre": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "portfolioproject": {
            "prosjekt_sk_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "navn": "Testprosjekt",
            "oppstart": None,
            "avdeling": "",
            "tiltakseier": "",
            "kontaktpersoner": "",
            "epost_kontakt": e_mail,
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
       
        "problemstilling": {
            "problem_stilling_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "problem": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "tiltak": {
            "tiltak_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "tiltak_beskrivelse": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "risikovurdering": {
            "risiko_vurdering_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "vurdering": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "malbilde": {
            "malbilde_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "malbilde_1_beskrivelse": "",
            "malbilde_1_vurdering": "",
            "malbilde_2_beskrivelse": "",
            "malbilde_2_vurdering": "",
            "malbilde_3_beskrivelse": "",
            "malbilde_3_vurdering": "",
            "malbilde_4_beskrivelse": "",
            "malbilde_4_vurdering": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "resursbehov": {
            "ressursbehov_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "estimert_budsjet_forklaring": "",
            "estimert_budsjet_behov": None,
            "antall_mandsverk_intern": None,
            "antall_mandsverk_ekstern": None,
            "antall_mandsverk_ekstern_betalt": None,
            "risiko_av_estimat": "",
            "risiko_av_estimat_tall": None,
            "kompetanse_som_trengs": "",
            "kompetanse_tilgjengelig": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "digitaliseringstrategi": {
            "digitalisering_strategi_id": str(uuid.uuid4()),
            "prosjekt_id": prosjekt_id,
            "sammenheng_digital_strategi": "",
            "digital_strategi_kommentar": "",
            "sist_endret": None,
            "endret_av": "",
            "er_gjeldende": True,
        },
        "ressursbruk": {},
    }

    with patch("backend.innlevering_router.db_connector") as mock_db:
        mock_db.update_project.return_value = {"status": "ok"}

        response = client.post(
            "/api/innlevering/update_prosjekt",
            headers={"x-api-key": API_KEY},
            params={"prosjekt_id": prosjekt_id, "e_mail": e_mail},
            json=fake_project,
        )

        called_project, called_prosjekt_id, called_email = mock_db.update_project.call_args[0]
        assert called_email == e_mail
        assert str(called_prosjekt_id) == prosjekt_id

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}