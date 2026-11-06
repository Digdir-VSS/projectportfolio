import httpx
import os 
from dotenv import load_dotenv

from models.ui_models import HistorikkData, ProjectData, RapporteringData, VurderingData, ProsjektListUI, VedtakData
from models.ui_models import OverviewUI, OpenOverviewUI

load_dotenv()

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
API_KEY = os.getenv("API_KEY")  # or whatever you use

# httpx gives up after 5 seconds by default. A request that opens a new database
# connection can take longer, especially with AZURE_SQL_AUTH=cli, where `az` alone
# needs several seconds to fetch a token.
BACKEND_TIMEOUT = 60

def api_get_admins():
    headers = {"x-api-key": API_KEY}
    with httpx.Client(timeout=BACKEND_TIMEOUT) as client:
        r = client.get(f"{BACKEND_BASE_URL}/admins", headers=headers)
        r.raise_for_status()
        return r.json()

async def api_get_projects(email: str | None, assessed: bool = False):
    headers = {"x-api-key": API_KEY}
    params = {"assessed": assessed}
    if email is not None:
        params["email"] = email

    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.get(f"{BACKEND_BASE_URL}/prosjekter", params=params, headers=headers)
        r.raise_for_status()
        return r.json()


async def api_get_project(prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.get(f"{BACKEND_BASE_URL}/prosjekt/{prosjekt_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        return ProjectData(**data)


async def api_update_project(project: ProjectData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = project.model_dump(mode="json")
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/update_prosjekt",
            params=params,
            json=payload,
            headers=headers,
        )
        return r.json()

async def api_create_new_project(email: str, prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    payload = {"email": email, "prosjekt_id": prosjekt_id}

    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/ny_prosjekt",
            json=payload,
            headers=headers,
        )
        r.raise_for_status()
        data = r.json()
        return ProjectData(**data)
    
async def api_get_overview():
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        response = await client.get(f"{BACKEND_BASE_URL}/get_overview", headers=headers)
        response.raise_for_status()
        return [OverviewUI(**prosjekt) for prosjekt in response.json()]
    
async def api_get_vurderings_data(prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.get(f"{BACKEND_BASE_URL}/vurdering/{prosjekt_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        return VurderingData(**data)
    
async def api_get_rapporterings_data(email: str, prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.get(f"{BACKEND_BASE_URL}/status_rapport/{prosjekt_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        return RapporteringData(**data)

async def api_update_rapport(rapport: RapporteringData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = rapport.model_dump(mode="json")
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/update_status_rapport",
            params=params,
            json=payload,
            headers=headers,
        )
        return r.json()
    
async def api_update_rapport(rapport: RapporteringData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = rapport.model_dump(mode="json")
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/update_status_rapport",
            params=params,
            json=payload,
            headers=headers,
        )
        return r.json()
    

async def api_update_vurdering(rapport: VurderingData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = rapport.model_dump(mode="json")
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/update_vurdering",
            params=params,
            json=payload,
            headers=headers,
        )
        return r.json()
    
async def api_get_prosjekt_list():
    headers = {"x-api-key": API_KEY}

    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        response = await client.get(
            f"{BACKEND_BASE_URL}/get_prosjekt_list",
            headers=headers,
        )
        response.raise_for_status()
        return [ProsjektListUI(**prosjekt) for prosjekt in response.json()]
    
async def api_get_historikk(dato: str) -> list[HistorikkData]:
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        response = await client.get(f"{BACKEND_BASE_URL}/historikk", params={"dato": dato}, headers=headers)
        response.raise_for_status()
        return [HistorikkData(**prosjekt) for prosjekt in response.json()]

async def api_get_prosjekt_historikk(prosjekt_id: str, dato: str) -> HistorikkData | None:
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        response = await client.get(f"{BACKEND_BASE_URL}/historikk/{prosjekt_id}", params={"dato": dato}, headers=headers)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return HistorikkData(**response.json())

async def api_get_open_overview():
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        response = await client.get(f"{BACKEND_BASE_URL}/get_open_overview", headers=headers)
        response.raise_for_status()
        return [OpenOverviewUI(**prosjekt) for prosjekt in response.json()]
    

async def api_delete_prosjekt(prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/delete_prosjekt",
            params=params,
            headers=headers,
        )
        return r.json()

async def api_get_vedtak_data(prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.get(f"{BACKEND_BASE_URL}/vedtak/{prosjekt_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        return VedtakData(**data)
    
async def api_update_vedtak(vedtak: VedtakData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = vedtak.model_dump(mode="json")
    async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
        r = await client.post(
            f"{BACKEND_BASE_URL}/update_vedtak",
            params=params,
            json=payload,
            headers=headers,
        )
        return r.json()