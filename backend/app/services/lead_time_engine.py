from dataclasses import dataclass
from math import exp

@dataclass(frozen=True)
class LeadTimeResult:
    lead_time_hours_min: float
    lead_time_hours_max: float
    threat_level: str
    recommended_evacuation_action: str

def calculate_lead_time(flow_m3s: float, rainfall_mm_h: float, api_mm: float,
                        distance_km: float, critical_stage_m: float = 4.0,
                        current_stage_m: float = 2.5, basin_area_km2: float = 100.0) -> LeadTimeResult:
    flow = max(flow_m3s, 1.0)
    rain_factor = 1.0 + min(rainfall_mm_h / 120.0, 1.5)
    api_factor = 1.0 + min(api_mm / 150.0, 1.0)
    travel_h = max(distance_km, 0.5) / max(8.0 + 0.03 * flow, 2.0)
    stage_gap = max(critical_stage_m - current_stage_m, 0.25)
    catchment_factor = max(0.7, min(1.5, (basin_area_km2 / 100.0) ** 0.15))
    pressure = rain_factor * api_factor * (1 + flow / 250.0) * catchment_factor
    surge_h = stage_gap * 2.2 / pressure
    min_h = max(0.25, travel_h + surge_h * 0.70)
    max_h = max(min_h + 0.25, travel_h + surge_h * 1.25)
    threat_score = min(1.0, pressure * (1.0 / (1.0 + exp(-(flow - 120)/70))))
    if min_h < 1.0 or threat_score >= 0.85:
        level, action = "Critical", "Initiate evacuation of exposed clusters; open shelters and broadcast CAP/SMS/siren advisories."
    elif min_h < 2.5 or threat_score >= 0.62:
        level, action = "High", "Pre-position response teams, alert village wardens, verify evacuation routes and shelter capacity."
    elif min_h < 6.0 or threat_score >= 0.38:
        level, action = "Moderate", "Increase telemetry frequency, issue preparedness advisory and verify downstream communications."
    else:
        level, action = "Low", "Continue routine monitoring and maintain readiness."
    return LeadTimeResult(round(min_h,2), round(max_h,2), level, action)
