from fastapi import Depends, HTTPException, status, Header, APIRouter
from fastapi.responses import JSONResponse
import os
from typing import Any
from dotenv import load_dotenv
from uuid import UUID
from pydantic import BaseModel
from backend.database.db import db_connector
from backend.database.db_connection import ProjectData
from models.sql_models import Overview

load_dotenv()

router = APIRouter(prefix="/api/innlevering")

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


@router.get("/prosjekt/{prosjekt_id}")
async def get_innnleverings_prosjekt(prosjekt_id: str, access_key: str = Depends(verify_api_key)) -> ProjectData:
    return db_connector.get_single_project(prosjekt_id)

@router.post("/ny_prosjekt")
async def create_new_innnleverings_prosjekt(ny_prosjekt: NyProsjekt, access_key: str = Depends(verify_api_key)):
    return db_connector.create_empty_project(ny_prosjekt.email, ny_prosjekt.prosjekt_id)


@router.get("/prosjekter")
async def get_innnleverings_prosjekt(email: str | None = None, access_key: str = Depends(verify_api_key)) -> list[dict[str, Any]]:
    """ Remember that email needs to be passed as search query parameter in request"""
    return db_connector.get_projects(email)

@router.post("/update_prosjekt")
async def update_innnleverings_prosjekt(project: ProjectData, prosjekt_id: UUID, e_mail: str, access_key: str = Depends(verify_api_key)):
    return db_connector.update_project(project, prosjekt_id, e_mail)

@router.get("/get_overview", response_model=list[Overview])
async def get_overview(access_key: str = Depends(verify_api_key)):
    return db_connector.get_overview()