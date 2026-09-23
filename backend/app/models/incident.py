from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    location: Mapped[str] = mapped_column(String(160))
    date: Mapped[datetime] = mapped_column(DateTime)
    severity: Mapped[str] = mapped_column(String(20))
    fatalities: Mapped[int] = mapped_column(Integer, default=0)
    rainfall_mm: Mapped[float] = mapped_column(Float, default=0)
    description: Mapped[str] = mapped_column(Text)

class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    targets: Mapped[str] = mapped_column(Text)
    channels: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    dispatched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(30), default="dispatched")
