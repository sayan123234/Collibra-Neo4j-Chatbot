from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.v1.api import api_router
from backend.app.services.graph_service import graph_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        graph_service.connect()
    except Exception as e:
        print(f"Failed to connect to Graph Database: {e}")
    yield
    # Shutdown
    graph_service.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health")
def health_check():
    db_status = "connected" if graph_service.graph else "disconnected"
    return {"status": "ok", "app_name": settings.PROJECT_NAME, "database": db_status}


# Import and include routers here later

app.include_router(api_router, prefix=settings.API_V1_STR)
