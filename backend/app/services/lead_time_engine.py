from __future__ import annotations
from dataclasses import dataclass, asdict
from math import exp, sqrt

# Approximate corridor waypoints and segment parameters. Replace with surveyed channel
# geometry and gauge-derived hydraulic radius/slope before operational use.
CORRIDOR_SEGMENTS = [
    {"from": "Upper Alaknanda catchment", "to": "Joshimath", "length_km": 18.0, "slope": 0.035, "hydraulic_radius_m": 0.65, "manning_n": 0.045},
    {"from": "Joshimath", "to": "Pipalkoti", "length_km": 24.0, "slope": 0.018, "hydraulic_radius_m": 0.85, "manning_n": 0.040},
    {"from": "Pipalkoti", "to": "Chamoli", "length_km": 20.0, "slope": 0.012, "hydraulic_radius_m": 0.95, "manning_n": 0.040},
]

@dataclass(frozen=True)
class LeadTimeResult:
    lead_time_hours_min: float
    lead_time_hours_max: float
    threat_level: str
    recommended_evacuation_action: str
    milestones: tuple[dict, ...] = ()
    method: str = "Manning travel-time screening estimate"
    confidence: str = "low until calibrated with surveyed geometry and gauge data"

    def as_dict(self):
        return asdict(self)


def manning_velocity_mps(hydraulic_radius_m: float, slope: float, manning_n: float) -> float:
    if hydraulic_radius_m <= 0 or slope <= 0 or manning_n <= 0:
        raise ValueError("Hydraulic radius, channel slope and Manning roughness must be positive")
    return (1.0 / manning_n) * hydraulic_radius_m ** (2.0 / 3.0) * sqrt(slope)


def corridor_milestones(segments: list[dict] | None = None, velocity_multiplier: float = 1.0) -> list[dict]:
    if velocity_multiplier <= 0:
        raise ValueError("velocity_multiplier must be positive")
    elapsed_seconds = 0.0
    milestones = []
    for seg in segments or CORRIDOR_SEGMENTS:
        velocity = manning_velocity_mps(seg["hydraulic_radius_m"], seg["slope"], seg["manning_n"]) * velocity_multiplier
        elapsed_seconds += seg["length_km"] * 1000.0 / velocity
        milestones.append({"settlement": seg["to"], "segment_from": seg["from"], "segment_length_km": seg["length_km"],
                           "velocity_m_s": round(velocity, 2), "estimated_elapsed_minutes": round(elapsed_seconds / 60.0),
                           "confidence": "low: illustrative geometry/roughness; calibrate before operational use"})
    return milestones


def calculate_lead_time(flow_m3s: float, rainfall_mm_h: float, api_mm: float,
                        distance_km: float, critical_stage_m: float = 4.0,
                        current_stage_m: float = 2.5, basin_area_km2: float = 100.0) -> LeadTimeResult:
    flow = max(flow_m3s, 1.0)
    rain_factor = 1.0 + min(max(rainfall_mm_h, 0) / 120.0, 1.5)
    api_factor = 1.0 + min(max(api_mm, 0) / 150.0, 1.0)
    # Manning travel time is used as a physically interpretable screening term.
    velocity = manning_velocity_mps(0.8, 0.02, 0.04) * min(1.8, max(0.65, 0.8 + flow / 500.0))
    travel_h = max(distance_km, 0.1) * 1000.0 / velocity / 3600.0
    stage_gap = max(critical_stage_m - current_stage_m, 0.0)
    pressure = rain_factor * api_factor * (1 + flow / 250.0) * max(0.7, min(1.5, (max(basin_area_km2, 1.0) / 100.0) ** 0.15))
    surge_h = stage_gap * 0.35 / pressure
    min_h = max(0.0, travel_h + surge_h * 0.70)
    max_h = max(min_h + 0.05, travel_h + surge_h * 1.25)
    threat_score = min(1.0, pressure * (1.0 / (1.0 + exp(-(flow - 120) / 70))))
    if min_h < 1.0 or threat_score >= 0.85:
        level, action = "Critical", "Activate incident command; verify official gauges and initiate locally authorized evacuation procedures."
    elif min_h < 2.5 or threat_score >= 0.62:
        level, action = "High", "Alert village wardens, verify routes and shelter capacity, and increase telemetry review frequency."
    elif min_h < 6.0 or threat_score >= 0.38:
        level, action = "Moderate", "Increase monitoring and verify downstream communications and local conditions."
    else:
        level, action = "Low", "Continue routine monitoring and maintain readiness."
    velocity_multiplier = 1.0 + min(max(flow, 0.0) / 1000.0, 0.8) + min(max(rainfall_mm_h, 0.0) / 200.0, 0.3)
    return LeadTimeResult(round(min_h, 2), round(max_h, 2), level, action, tuple(corridor_milestones(velocity_multiplier=velocity_multiplier)))
