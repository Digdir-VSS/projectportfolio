import httpx
import os 
<<<<<<< HEAD
<<<<<<< HEAD
from enum import StrEnum

from backend.database.db_connection import ProjectData

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
API_KEY = os.getenv("INNLEVERING_API_KEY")  # or whatever you use


class EndpointConfig(StrEnum):
    INNLEVERING = "innlevering"
    VURDERING = "vurdering"
    STATUS_RAPPORTERING = "status_rapportering"
    FINANSERING = "finansering"


async def api_get_projects(email: str | None):
    print(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekter")
=======
=======
from enum import StrEnum

>>>>>>> bd7afd7 (add Enum Config)
from backend.database.db_connection import ProjectData

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
API_KEY = os.getenv("INNLEVERING_API_KEY")  # or whatever you use


class EndpointConfig(StrEnum):
    INNLEVERING = "innlevering"
    VURDERING = "vurdering"
    STATUS_RAPPORTERING = "status_rapportering"
    FINANSERING = "finansering"


async def api_get_projects(email: str | None):
<<<<<<< HEAD
>>>>>>> 0411402 (add client to backend fast api)
=======
    print(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekter")
>>>>>>> bd7afd7 (add Enum Config)
    headers = {"x-api-key": API_KEY}
    params = {}
    if email is not None:
        params["email"] = email

    async with httpx.AsyncClient() as client:
<<<<<<< HEAD
<<<<<<< HEAD
        r = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekter", params=params, headers=headers)
=======
        r = await client.get(f"{BACKEND_BASE}/prosjekter", params=params, headers=headers)
>>>>>>> 0411402 (add client to backend fast api)
=======
        r = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekter", params=params, headers=headers)
>>>>>>> bd7afd7 (add Enum Config)
        r.raise_for_status()
        return r.json()


async def api_get_project(prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient() as client:
<<<<<<< HEAD
<<<<<<< HEAD
        r = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekt/{prosjekt_id}", headers=headers)
=======
        r = await client.get(f"{BACKEND_BASE}/prosjekt/{prosjekt_id}", headers=headers)
>>>>>>> 0411402 (add client to backend fast api)
=======
        r = await client.get(f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/prosjekt/{prosjekt_id}", headers=headers)
>>>>>>> bd7afd7 (add Enum Config)
        r.raise_for_status()
        data = r.json()
        return ProjectData(**data)


async def api_update_project(project: ProjectData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = project.model_dump(mode="json")
    async with httpx.AsyncClient() as client:
        r = await client.post(
<<<<<<< HEAD
<<<<<<< HEAD
            f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/update_prosjekt",
=======
            f"{BACKEND_BASE}/update_prosjekt",
>>>>>>> 0411402 (add client to backend fast api)
=======
            f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/update_prosjekt",
>>>>>>> bd7afd7 (add Enum Config)
            params=params,
            json=payload,
            headers=headers,
        )
<<<<<<< HEAD
<<<<<<< HEAD
=======
        print("UPDATE ERROR STATUS:", r.status_code)
        print("UPDATE ERROR BODY:", r.text)  # 👈 this shows FastAPI’s validation errors
>>>>>>> 0411402 (add client to backend fast api)
=======
>>>>>>> bd7afd7 (add Enum Config)
        return r.json()

async def api_create_new_project(email: str, prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    payload = {"email": email, "prosjekt_id": prosjekt_id}

    async with httpx.AsyncClient() as client:
        r = await client.post(
<<<<<<< HEAD
<<<<<<< HEAD
            f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/ny_prosjekt",
=======
            f"{BACKEND_BASE}/ny_prosjekt",
>>>>>>> 0411402 (add client to backend fast api)
=======
            f"{BACKEND_BASE_URL}/{EndpointConfig.INNLEVERING}/ny_prosjekt",
>>>>>>> bd7afd7 (add Enum Config)
            json=payload,
            headers=headers,
        )
        r.raise_for_status()
        return r.json()