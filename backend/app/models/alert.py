from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    severity: Mapped[str] = mapped_column(String(20))
    threat_level: Mapped[str] = mapped_column(String(20))
    village: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(Text)
    lead_time_min_h: Mapped[float] = mapped_column(Float)
    lead_time_max_h: Mapped[float] = mapped_column(Float)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
