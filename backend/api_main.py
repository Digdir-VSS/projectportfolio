from fastapi import FastAPI
from backend.innlevering_router import router as innleverings_router

api_app = FastAPI(title="Project Portfolio API")

api_app.include_router(innleverings_router)
