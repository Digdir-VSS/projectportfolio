import httpx
import os 
from enum import StrEnum

from models.ui_models import ProjectData, RapporteringData, RapporteringUI, FremskrittUI, DeliveryRiskUI
from models.ui_models import OverviewUI

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
API_KEY = os.getenv("INNLEVERING_API_KEY")  # or whatever you use


class EndpointConfig(StrEnum):
    INNLEVERING = "innlevering"
    VURDERING = "vurdering"
    STATUS_RAPPORTERING = "status_rapportering"
    FINANSERING = "finansering"


async def api_get_projects(email: str | None):
    print(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekter")
    headers = {"x-api-key": API_KEY}
    params = {}
    if email is not None:
        params["email"] = email

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekter", params=params, headers=headers)
        r.raise_for_status()
        return r.json()


async def api_get_project(prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekt/{prosjekt_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        return ProjectData(**data)


async def api_update_project(project: ProjectData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = project.model_dump(mode="json")
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/update_prosjekt",
            params=params,
            json=payload,
            headers=headers,
        )
        return r.json()

async def api_create_new_project(email: str, prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    payload = {"email": email, "prosjekt_id": prosjekt_id}

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/ny_prosjekt",
            json=payload,
            headers=headers,
        )
        r.raise_for_status()
        data = r.json()
        return ProjectData(**data)
    
async def api_get_overview():
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/get_overview", headers=headers)
        response.raise_for_status()
        return [OverviewUI(**prosjekt) for prosjekt in response.json()]

async def api_get_rapporterings_data(email: str, prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    payload = {"email": email, "prosjekt_id": prosjekt_id}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekt/{prosjekt_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        return RapporteringData(
            rapportering=RapporteringUI(),
            portfolioproject=data["portfolioproject"], 
            fremskritt=data["fremskritt"], 
            delivery_risk=DeliveryRiskUI()
        )