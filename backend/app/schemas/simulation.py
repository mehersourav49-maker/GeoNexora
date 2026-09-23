from pydantic import BaseModel, Field

class SimulationRequest(BaseModel):
    catchment_area_km2: float = Field(gt=0, le=5000)
    rainfall_mm_h: float = Field(ge=0, le=150)
    soil_saturation_pct: float = Field(ge=0, le=100)
    slope_incline_deg: float = Field(ge=0, le=70)
    bedrock_runoff_factor: float = Field(ge=0.5, le=2.0)
    vulnerable_population: int = Field(default=5000, ge=0)

class HydroPoint(BaseModel):
    minutes: float
    runoff_m3s: float
    inundation_depth_m: float

class SimulationResult(BaseModel):
    threat_level: str
    peak_runoff_m3s: float
    factor_of_safety: float
    slope_failure_risk: str
    time_to_inundation_hours: float
    vulnerable_population: int
    projected_flood_cone_km2: float
    hydrograph: list[HydroPoint]
    notes: list[str]
