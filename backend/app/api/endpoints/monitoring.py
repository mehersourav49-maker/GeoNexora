from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models import Sensor, Telemetry
from ...models.sensor import TRANSMISSION_MODES
from ...schemas.telemetry import SensorOut, TelemetryIn, TelemetryOut
from ...services.data_fusion import fuse_risk
from ...services.lead_time_engine import calculate_lead_time

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])
v1_router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring v1"])

@router.get("/sensors", response_model=list[SensorOut])
def sensors(db: Session = Depends(get_db)):
    rows = db.scalars(select(Sensor).order_by(Sensor.id)).all()
    out=[]
    for s in rows:
        latest=db.scalar(select(Telemetry).where(Telemetry.sensor_id==s.id).order_by(Telemetry.timestamp.desc()).limit(1))
        out.append(SensorOut.model_validate({**{c.name:getattr(s,c.name) for c in Sensor.__table__.columns}, "latest": latest}))
    return out

@router.post("/telemetry", response_model=TelemetryOut)
def ingest(payload: TelemetryIn, db: Session = Depends(get_db)):
    if not db.get(Sensor, payload.sensor_id): raise HTTPException(404,"Sensor not found")
    row=Telemetry(**payload.model_dump(exclude_none=True))
    db.add(row); db.commit(); db.refresh(row); return row

@router.get("/sensors/{sensor_id}/risk")
def sensor_risk(sensor_id:int, db:Session=Depends(get_db)):
    s=db.get(Sensor,sensor_id)
    if not s: raise HTTPException(404,"Sensor not found")
    t=db.scalar(select(Telemetry).where(Telemetry.sensor_id==sensor_id).order_by(Telemetry.timestamp.desc()).limit(1))
    if not t: raise HTTPException(404,"No telemetry")
    fusion=fuse_risk(t.rainfall_mm_h,t.soil_saturation_pct,t.river_level_m,t.river_flow_m3s,t.slope_incline_deg)
    lead=calculate_lead_time(t.river_flow_m3s,t.rainfall_mm_h,t.api_mm,10, current_stage_m=t.river_level_m)
    return {"sensor_id":sensor_id,"fusion":fusion,"lead_time":lead.as_dict()}

@v1_router.post("/simulate-backhaul-failure")
def simulate_backhaul_failure(failed: bool = True, db: Session = Depends(get_db)):
    """Simulation only: changes persisted channel status; it cannot sever real networks."""
    sensors = db.scalars(select(Sensor).order_by(Sensor.id)).all()
    changed = 0
    for sensor in sensors:
        if failed and sensor.transmission_mode == "CELLULAR_4G":
            sensor.transmission_mode = "LORA_MESH_865MHZ"
            changed += 1
        elif not failed and sensor.transmission_mode == "LORA_MESH_865MHZ":
            sensor.transmission_mode = "CELLULAR_4G"
            changed += 1
    db.commit()
    return {"simulation": True, "cellular_4g_failed": failed, "changed_sensors": changed,
            "fallback_mode": "LORA_MESH_865MHZ" if failed else "CELLULAR_4G",
            "telemetry_interval_seconds": 60 if failed else 5,
            "message": "Simulated channel state only; no physical network was controlled."}

@v1_router.get("/transmission-modes")
def transmission_modes(db: Session = Depends(get_db)):
    rows = db.scalars(select(Sensor).order_by(Sensor.id)).all()
    return {"supported_modes": list(TRANSMISSION_MODES), "sensors": [{"id": s.id, "name": s.name,
            "transmission_mode": s.transmission_mode, "active": s.active,
            "interval_seconds": 60 if s.transmission_mode in ("LORA_MESH_865MHZ", "OFFLINE_BUFFER") else 5} for s in rows]}
