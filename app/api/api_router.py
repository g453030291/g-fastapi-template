from fastapi import APIRouter

from app.api import test_api

api_router = APIRouter(prefix="/api", tags=["API"])

api_router.include_router(test_api.router, prefix="/test", tags=["Test"])
