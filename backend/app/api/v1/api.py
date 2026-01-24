from fastapi import APIRouter
from backend.app.api.v1.endpoints import chat, lineage

api_router = APIRouter()
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(lineage.router, tags=["lineage"])
