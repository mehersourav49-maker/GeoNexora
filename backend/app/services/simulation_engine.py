"""Event-based runoff screening using the SCS Curve Number method.

Inputs are scenario assumptions, not a calibrated operational forecast. Rainfall
is treated as total storm depth = intensity * duration.
"""
from __future__ import annotations
import math
import numpy as np
from .data_fusion import fuse_risk


def curve_number_for_amc(cn_ii: float, soil_saturation_pct: float) -> tuple[float, str]:
    """Convert AMC-II CN to AMC-I/II/III using standard empirical conversions."""
    cn_ii = min(98.0, max(30.0, float(cn_ii)))
    saturation = min(100.0, max(0.0, float(soil_saturation_pct)))
    if saturation < 35:
        cn = cn_ii / (2.281 - 0.01281 * cn_ii)
        return min(98.0, max(30.0, cn)), "AMC I"
    if saturation >= 75:
        cn = cn_ii / (0.427 + 0.00573 * cn_ii)
        return min(99.0, max(cn_ii, cn)), "AMC III"
    return cn_ii, "AMC II"


def run_simulation(catchment_area_km2: float, rainfall_mm_h: float, soil_saturation_pct: float,
                   slope_incline_deg: float, bedrock_runoff_factor: float, vulnerable_population: int,
                   curve_number: float = 78.0, storm_duration_hours: float = 1.0,
                   time_of_concentration_hours: float = 1.0, timestep_hours: float = 0.1):
    """Run an SCS-CN event runoff and SCS unit-hydrograph screening scenario."""
    if catchment_area_km2 <= 0 or storm_duration_hours <= 0 or time_of_concentration_hours <= 0 or timestep_hours <= 0:
        raise ValueError("Area, storm duration, concentration time and timestep must be positive")
    if rainfall_mm_h < 0 or not 0 <= soil_saturation_pct <= 100 or not 0 <= slope_incline_deg <= 90:
        raise ValueError("Rainfall, saturation or slope is outside its physical range")
    area = float(catchment_area_km2)
    p = float(rainfall_mm_h) * float(storm_duration_hours)
    cn, amc = curve_number_for_amc(curve_number, soil_saturation_pct)
    retention_mm = 25400.0 / cn - 254.0
    initial_abstraction_mm = 0.2 * retention_mm
    runoff_depth_mm = ((p - initial_abstraction_mm) ** 2 / (p - initial_abstraction_mm + retention_mm)) if p > initial_abstraction_mm else 0.0
    tp_hours = 0.6 * float(time_of_concentration_hours) + timestep_hours / 2.0
    peak_discharge_m3s = 0.208 * area * runoff_depth_mm / max(tp_hours, 1e-6)

    # A triangular unit-hydrograph-shaped screening curve; peak is physics-derived above.
    base_time_h = max(2.67 * tp_hours, tp_hours + timestep_hours)
    times = np.arange(0.0, base_time_h + timestep_hours / 2, timestep_hours)
    shape = np.where(times <= tp_hours, times / tp_hours, np.maximum(0.0, (base_time_h - times) / (base_time_h - tp_hours)))
    hydrograph = [{"minutes": round(float(t * 60), 1), "runoff_m3s": round(float(peak_discharge_m3s * max(0.0, q)), 3),
                   "inundation_depth_m": round(float(2.2 * max(0.0, q)), 3)} for t, q in zip(times, shape)]

    # Existing slope stability output is retained as a screening estimate, not certification.
    cohesion_kpa = 28.0 * (1 - 0.45 * soil_saturation_pct / 100)
    friction_deg = max(12.0, 34.0 - 12.0 * soil_saturation_pct / 100)
    gamma, z = 19.0, 2.0
    pore_pressure_ratio = 0.15 + 0.55 * soil_saturation_pct / 100
    denominator = gamma * z * max(math.sin(math.radians(slope_incline_deg)) * math.cos(math.radians(slope_incline_deg)), 0.05)
    fs = cohesion_kpa / denominator + math.tan(math.radians(friction_deg)) * (1 - pore_pressure_ratio) / max(math.tan(math.radians(slope_incline_deg)), 0.05)
    fs = float(max(0.35, min(3.5, fs)))
    fused = fuse_risk(rainfall_mm_h, soil_saturation_pct, 2.0 + peak_discharge_m3s / 300, peak_discharge_m3s, slope_incline_deg)
    slope_risk = "High" if fs < 1.0 else "Moderate" if fs < 1.3 else "Low"
    notes = ["SCS-CN runoff depth uses storm total rainfall (intensity × duration).", "AMC conversion is an empirical screening approximation; validate CN and AMC thresholds for the basin.", "SCS peak discharge and triangular hydrograph are screening estimates, not a calibrated operational forecast.", "Factor of Safety is an engineering screening estimate, not a site certification."]
    return {"threat_level": fused["threat_level"], "risk": fused, "curve_number": round(cn, 2), "antecedent_moisture_condition": amc,
            "storm_total_rainfall_mm": round(p, 2), "potential_maximum_retention_mm": round(retention_mm, 2),
            "initial_abstraction_mm": round(initial_abstraction_mm, 2), "direct_runoff_depth_mm": round(runoff_depth_mm, 2),
            "time_to_peak_hours": round(tp_hours, 3), "peak_runoff_m3s": round(peak_discharge_m3s, 3),
            "factor_of_safety": round(fs, 2), "slope_failure_risk": slope_risk,
            "time_to_inundation_hours": round(tp_hours, 2), "vulnerable_population": int(vulnerable_population),
            "projected_flood_cone_km2": round(max(0.0, area * min(1.0, runoff_depth_mm / 100.0) * max(0.1, bedrock_runoff_factor)), 2),
            "hydrograph": hydrograph, "notes": notes}
