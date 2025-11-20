from nicegui import APIRouter
from fastapi import Depends, HTTPException, status, Header
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from .database.db import db_connector
from .database.db_connection import ProjectData

load_dotenv()

router = APIRouter(prefix="/api/innlevering/")

API_KEY = os.getenv("INNLEVERING_API_KEY")

class NyProsjekt(BaseModel):
    prosjekt_id: str
    email: str


async def verify_api_key(x_api_key: str = Header(...)):
    if API_KEY:
        if x_api_key != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )
    else:
        HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )


@router.get("prosjekt/{prosjekt_id}")
async def get_innnleverings_prosjekt(prosjekt_id: str, access_key: str = Depends(verify_api_key)) -> ProjectData:
    return db_connector.get_single_project(prosjekt_id)

@router.post("/ny_prosjekt")
async def get_innnleverings_prosjekt(ny_prosjekt: NyProsjekt, access_key: str = Depends(verify_api_key)):
    return db_connector.create_empty_project(ny_prosjekt.email, ny_prosjekt.prosjekt_id)


@router.post("/projects")
async def get_innnleverings_prosjekt(email: str | None, access_key: str = Depends(verify_api_key)) -> List[str, str]:
    """ Remember that email needs to be passed as search query parameter in request"""
    return db_connector.get_projects(email)
