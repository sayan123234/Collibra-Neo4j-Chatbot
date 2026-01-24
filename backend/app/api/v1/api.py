from fastapi import APIRouter
from backend.app.api.v1.endpoints import chat, lineage, admin

api_router = APIRouter()
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(lineage.router, tags=["lineage"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
