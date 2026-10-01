import csv, io
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models import Incident
router=APIRouter(prefix="/api/analytics",tags=["Analytics"])
v1_router=APIRouter(prefix="/api/v1/analytics",tags=["Analytics v1"])

@router.get("/incidents")
def incidents(db:Session=Depends(get_db)): return db.scalars(select(Incident).order_by(Incident.date.desc())).all()

@router.get("/incidents.csv")
def csv_export(db:Session=Depends(get_db)):
    rows=db.scalars(select(Incident).order_by(Incident.date.desc())).all(); out=io.StringIO(); w=csv.writer(out); w.writerow(["id","title","location","date","severity","fatalities","rainfall_mm","description"])
    for x in rows: w.writerow([x.id,x.title,x.location,x.date.isoformat(),x.severity,x.fatalities,x.rainfall_mm,x.description])
    return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=geonexora_incidents.csv"})

@v1_router.get("/replay/chamoli-2021")
@router.get("/replay/chamoli-2021")
def chamoli_2021_replay():
    """Pedagogical reconstruction, not observed telemetry or a validated forecast."""
    times = [("T-180m", 8, 42, 0.3, 58), ("T-150m", 10, 44, 0.4, 59), ("T-120m", 12, 46, 0.5, 60),
             ("T-90m", 14, 48, 0.7, 62), ("T-60m", 18, 52, 1.0, 65), ("T-30m", 22, 58, 1.5, 69),
             ("T-10m", 38, 71, 2.4, 76), ("T+0m", 75, 88, 4.8, 88), ("T+15m", 96, 94, 7.2, 94), ("T+30m", 82, 96, 8.0, 96)]
    steps=[]
    for index,(label,flow,seismic,level,soil) in enumerate(times):
        score=min(1.0, .30*(flow/100)+.20*(seismic/100)+.25*(level/8)+.25*(soil/100))
        threat="Critical" if score>=.8 else "High" if score>=.6 else "Moderate" if score>=.35 else "Low"
        steps.append({"step":index,"time_label":label,"upstream_flow_rate":flow,"seismic_acoustic_trigger":seismic,
                      "river_level_spike":level,"soil_saturation":soil,"threat_score":round(score,3),"threat_level":threat,
                      "data_status":"RECONSTRUCTED DEMONSTRATION DATA"})
    return {"event":"Chamoli rock-ice avalanche and debris-flow disaster, 2021-02-07",
            "data_status":"reconstructed demonstration timeline; values are illustrative, not observed telemetry",
            "source_note":"Use verified scientific publications and official event records before treating any values as historical measurements.",
            "detection_lead_time_claim":None,"steps":steps}
