from pydantic import BaseModel, Field

class SimulationRequest(BaseModel):
    catchment_area_km2: float = Field(gt=0, le=5000)
    rainfall_mm_h: float = Field(ge=0, le=150, description="Rainfall intensity; multiplied by storm duration to get event depth")
    soil_saturation_pct: float = Field(ge=0, le=100)
    slope_incline_deg: float = Field(ge=0, le=70)
    bedrock_runoff_factor: float = Field(ge=0.5, le=2.0)
    vulnerable_population: int = Field(default=5000, ge=0)
    curve_number: float = Field(default=78.0, ge=30, le=98, description="AMC-II SCS Curve Number before moisture adjustment")
    storm_duration_hours: float = Field(default=1.0, gt=0, le=24)
    time_of_concentration_hours: float = Field(default=1.0, gt=0, le=48)
    timestep_hours: float = Field(default=0.1, gt=0, le=1)

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
    curve_number: float
    antecedent_moisture_condition: str
    storm_total_rainfall_mm: float
    potential_maximum_retention_mm: float
    initial_abstraction_mm: float
    direct_runoff_depth_mm: float
    time_to_peak_hours: float
    risk: dict
    hydrograph: list[HydroPoint]
    notes: list[str]
