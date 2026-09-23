import csv, io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models import Incident
router=APIRouter(prefix="/api/analytics",tags=["Analytics"])
@router.get("/incidents")
def incidents(db:Session=Depends(get_db)): return db.scalars(select(Incident).order_by(Incident.date.desc())).all()
@router.get("/incidents.csv")
def csv_export(db:Session=Depends(get_db)):
    rows=db.scalars(select(Incident).order_by(Incident.date.desc())).all(); out=io.StringIO(); w=csv.writer(out); w.writerow(["id","title","location","date","severity","fatalities","rainfall_mm","description"])
    for x in rows: w.writerow([x.id,x.title,x.location,x.date.isoformat(),x.severity,x.fatalities,x.rainfall_mm,x.description])
    return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=geonexora_incidents.csv"})
