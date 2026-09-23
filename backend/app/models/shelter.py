from sqlalchemy import String, Float, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base

class Shelter(Base):
    __tablename__ = "shelters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(140))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    max_capacity: Mapped[int] = mapped_column(Integer)
    occupied_beds: Mapped[int] = mapped_column(Integer)
    food_days: Mapped[float] = mapped_column(Float)
    medical_staff: Mapped[int] = mapped_column(Integer)
    generator_online: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(30), default="operational")

class AgencyContact(Base):
    __tablename__ = "agency_contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    agency: Mapped[str] = mapped_column(String(80))
    hotline: Mapped[str] = mapped_column(String(40))
    coverage: Mapped[str] = mapped_column(String(160))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
