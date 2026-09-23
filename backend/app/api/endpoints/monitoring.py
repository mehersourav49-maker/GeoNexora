from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models import Sensor, Telemetry
from ...schemas.telemetry import SensorOut, TelemetryIn, TelemetryOut
from ...services.data_fusion import fuse_risk
from ...services.lead_time_engine import calculate_lead_time

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

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
    return {"sensor_id":sensor_id,"fusion":fusion,"lead_time":lead.__dict__}
