from fastapi import Depends, HTTPException, status, Header, APIRouter
import os
from uuid import UUID
from dotenv import load_dotenv

from backend.database.db import db_connector
from models.ui_models import VurderingDataUI, VurderingOverviewUI


load_dotenv()

router = APIRouter(prefix="/api/vurdering")

API_KEY = os.getenv("INNLEVERING_API_KEY")  # reuse or rename if you want

async def verify_api_key(x_api_key: str = Header(...)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
@router.get("/get_overview", response_model=list[VurderingOverviewUI])
async def get_overview(
    access_key: str = Depends(verify_api_key),
):
    return db_connector.get_all_vurderinger()

@router.get("/{prosjekt_id}", response_model=VurderingDataUI)
async def get_vurdering(
    prosjekt_id: str,
    access_key: str = Depends(verify_api_key),
):
    return db_connector.get_single_vurdering(prosjekt_id)

@router.post("/update")
async def update_vurdering(
    vurdering: VurderingDataUI,
    prosjekt_id: UUID,
    e_mail: str,
    access_key: str = Depends(verify_api_key),
):
    return db_connector.update_vurdering(vurdering, prosjekt_id, e_mail)