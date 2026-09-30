
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .core.config import settings
from .core.database import Base, engine
from .api.endpoints import (
    alerts,
    analytics,
    logistics,
    monitoring,
    simulation,
)
from .models import *

# Database initialization
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Hyper-local flash flood early warning "
        "and incident command system"
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register existing API routers
app.include_router(monitoring.router)
app.include_router(simulation.router)
app.include_router(logistics.router)
app.include_router(alerts.router)
app.include_router(analytics.router)

# The Dockerfile copies the Vite build to backend/static/
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"


@app.get("/api/dashboard/summary")
def summary():
    return {
        "service": "GeoNexora",
        "status": "online",
        "message": "Multi-source flash-flood command system",
    }


@app.get("/", include_in_schema=False)
def root():
    if not INDEX_FILE.is_file():
        raise HTTPException(
            status_code=503,
            detail="Frontend build not found",
        )
    return FileResponse(INDEX_FILE)


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    # Unknown API routes should remain API errors.
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    if not INDEX_FILE.is_file():
        raise HTTPException(
            status_code=503,
            detail="Frontend build not found",
        )

    # Serve existing frontend files, such as JS, CSS and icons.
    requested_file = (STATIC_DIR / full_path).resolve()

    if (
        requested_file.is_relative_to(STATIC_DIR.resolve())
        and requested_file.is_file()
    ):
        return FileResponse(requested_file)

    # Fall back to index.html for frontend routes.
    return FileResponse(INDEX_FILE)
