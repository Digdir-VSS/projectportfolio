import httpx
import os 
from backend.database.db_connection import ProjectData

BACKEND_BASE = "http://localhost:8080/api/innlevering"
API_KEY = os.getenv("INNLEVERING_API_KEY")  # or whatever you use

async def api_get_projects(email: str | None):
    headers = {"x-api-key": API_KEY}
    params = {}
    if email is not None:
        params["email"] = email

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BACKEND_BASE}/prosjekter", params=params, headers=headers)
        r.raise_for_status()
        return r.json()


async def api_get_project(prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BACKEND_BASE}/prosjekt/{prosjekt_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        return ProjectData(**data)


async def api_update_project(project: ProjectData, prosjekt_id: str, email: str):
    headers = {"x-api-key": API_KEY}
    params = {"prosjekt_id": prosjekt_id, "e_mail": email}
    payload = project.model_dump(mode="json")
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_BASE}/update_prosjekt",
            params=params,
            json=payload,
            headers=headers,
        )
        print("UPDATE ERROR STATUS:", r.status_code)
        print("UPDATE ERROR BODY:", r.text)  # 👈 this shows FastAPI’s validation errors
        return r.json()

async def api_create_new_project(email: str, prosjekt_id: str):
    headers = {"x-api-key": API_KEY}
    payload = {"email": email, "prosjekt_id": prosjekt_id}

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_BASE}/ny_prosjekt",
            json=payload,
            headers=headers,
        )
        r.raise_for_status()
        return r.json()