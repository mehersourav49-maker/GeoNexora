from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

TRANSMISSION_MODES = ("CELLULAR_4G", "LORA_MESH_865MHZ", "ESP32_CAPTIVE_HOTSPOT", "OFFLINE_BUFFER")

class Sensor(Base):
    __tablename__ = "sensors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    sensor_type: Mapped[str] = mapped_column(String(60))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    elevation_m: Mapped[float] = mapped_column(Float, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Safe migration in main.py adds this column to existing PostgreSQL/SQLite databases.
    transmission_mode: Mapped[str] = mapped_column(String(40), default="CELLULAR_4G", nullable=False, server_default="CELLULAR_4G")
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
