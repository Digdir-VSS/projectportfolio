from fastapi import FastAPI
from backend.router import router

api_app = FastAPI(title="Project Portfolio API")

api_app.include_router(router)
