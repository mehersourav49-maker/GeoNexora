from datetime import datetime
from pydantic import BaseModel, Field

class TelemetryIn(BaseModel):
    sensor_id: int
    rainfall_mm_h: float = Field(ge=0)
    river_flow_m3s: float = Field(ge=0)
    river_level_m: float = Field(ge=0)
    soil_saturation_pct: float = Field(ge=0, le=100)
    slope_incline_deg: float = Field(ge=0, le=90)
    api_mm: float = Field(ge=0)
    timestamp: datetime | None = None

class TelemetryOut(TelemetryIn):
    id: int
    timestamp: datetime
    model_config = {"from_attributes": True}

class SensorOut(BaseModel):
    id: int
    name: str
    sensor_type: str
    latitude: float
    longitude: float
    elevation_m: float
    active: bool
    transmission_mode: str = "CELLULAR_4G"
    latest: TelemetryOut | None = None
    model_config = {"from_attributes": True}
