from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

class Sensor(Base):
    __tablename__ = "sensors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    sensor_type: Mapped[str] = mapped_column(String(60))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    elevation_m: Mapped[float] = mapped_column(Float, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    telemetries: Mapped[list["Telemetry"]] = relationship(back_populates="sensor", cascade="all, delete-orphan")

class Telemetry(Base):
    __tablename__ = "telemetry"
    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    rainfall_mm_h: Mapped[float] = mapped_column(Float, default=0)
    river_flow_m3s: Mapped[float] = mapped_column(Float, default=0)
    river_level_m: Mapped[float] = mapped_column(Float, default=0)
    soil_saturation_pct: Mapped[float] = mapped_column(Float, default=0)
    slope_incline_deg: Mapped[float] = mapped_column(Float, default=25)
    api_mm: Mapped[float] = mapped_column(Float, default=0)
    sensor: Mapped[Sensor] = relationship(back_populates="telemetries")
