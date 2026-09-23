from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models import Alert
router=APIRouter(prefix="/api/alerts",tags=["Alerts"])
@router.get("")
def alerts(db:Session=Depends(get_db)): return db.scalars(select(Alert).order_by(Alert.created_at.desc())).all()
@router.patch("/{alert_id}/acknowledge")
def acknowledge(alert_id:int,db:Session=Depends(get_db)):
    a=db.get(Alert,alert_id); a.acknowledged=True; db.commit(); return {"id":a.id,"acknowledged":True}
