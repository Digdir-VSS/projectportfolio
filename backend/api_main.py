from fastapi import FastAPI
from backend.innlevering_router import router as innleverings_router
from backend.vurdering_router import router as vurdering_router

api_app = FastAPI(title="Project Portfolio API")

api_app.include_router(innleverings_router)
api_app.include_router(vurdering_router)
