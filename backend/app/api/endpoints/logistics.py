from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from ...core.database import get_db
from ...models import Shelter, AgencyContact, BroadcastLog
from ...schemas.shelter import ShelterOut, BroadcastRequest, BroadcastOut
router=APIRouter(prefix="/api/logistics",tags=["Logistics"])
@router.get("/shelters",response_model=list[ShelterOut])
def shelters(db:Session=Depends(get_db)): return db.scalars(select(Shelter).order_by(Shelter.id)).all()
@router.get("/agencies")
def agencies(db:Session=Depends(get_db)): return db.scalars(select(AgencyContact).where(AgencyContact.active==True)).all()
@router.post("/broadcast",response_model=BroadcastOut)
def broadcast(payload:BroadcastRequest,db:Session=Depends(get_db)):
    now=datetime.utcnow(); row=BroadcastLog(targets=",".join(payload.targets),channels=",".join(payload.channels),message=payload.message,dispatched_at=now)
    db.add(row); db.commit(); db.refresh(row)
    return {**payload.model_dump(),"id":row.id,"status":row.status,"dispatched_at":now.isoformat()}
