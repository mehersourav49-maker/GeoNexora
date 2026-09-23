from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import Base, engine
from .api.endpoints import alerts, analytics, logistics, monitoring, simulation
from .models import *
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name,version="1.0.0",description="Hyper-local flash flood early warning and incident command system")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(monitoring.router); app.include_router(simulation.router); app.include_router(logistics.router); app.include_router(alerts.router); app.include_router(analytics.router)
@app.get("/")
def root(): return {"service":"GeoNexora","status":"online"}
@app.get("/api/dashboard/summary")
def summary(): return {"service":"GeoNexora","status":"online","message":"Multi-source flash-flood command system"}
