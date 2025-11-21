from fastapi.testclient import TestClient
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import uuid
from unittest.mock import patch

from backend.innlevering_router import router

load_dotenv()

API_KEY = os.getenv("INNLEVERING_API_KEY")

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_new_innnleverings_prosjekt():
    payload = {"email": "test@example.com", "prosjekt_id": "ABC123"}
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

    # Ensure the router returns our fake list of dicts
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
    # Exact match is fine if your API just passes through DB result
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

    # Assert core invariants
    assert data["portfolioproject"]["epost_kontakt"] == "test@example.com"
    for section in data.values():
        if isinstance(section, dict) and "prosjekt_id" in section:
            assert section["prosjekt_id"] == prosjekt_id
