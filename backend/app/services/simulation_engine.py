import numpy as np
from .data_fusion import fuse_risk

def run_simulation(catchment_area_km2: float, rainfall_mm_h: float, soil_saturation_pct: float,
                   slope_incline_deg: float, bedrock_runoff_factor: float, vulnerable_population: int):
    t = np.linspace(0, 180, 25)
    saturation_factor = 0.55 + 0.45 * soil_saturation_pct / 100
    runoff_coeff = min(0.95, max(0.12, (rainfall_mm_h/150)*0.45 + saturation_factor*0.35)) * bedrock_runoff_factor
    pulse = np.exp(-((t-55)/45)**2) * (0.45 + rainfall_mm_h/150)
    runoff = (rainfall_mm_h/1000/3600) * catchment_area_km2 * 1_000_000 * runoff_coeff * (1 + pulse)
    peak = float(np.max(runoff))
    # Infinite-slope approximation; effective cohesion/friction are normalized scenario parameters.
    cohesion_kpa = 28.0 * (1 - 0.45*soil_saturation_pct/100)
    friction_deg = max(12.0, 34.0 - 12.0*soil_saturation_pct/100)
    gamma = 19.0
    z = 2.0
    pore_pressure_ratio = 0.15 + 0.55*soil_saturation_pct/100
    import math
    fs = (cohesion_kpa/(gamma*z*math.sin(math.radians(slope_incline_deg))*math.cos(math.radians(slope_incline_deg))) +
          (math.tan(math.radians(friction_deg))*(1-pore_pressure_ratio))/max(math.tan(math.radians(slope_incline_deg)),0.05))
    fs = float(max(0.35, min(3.5, fs)))
    flow_velocity = max(1.5, 2.5 + peak/250)
    time_to_inundation = max(0.35, 3.5 - rainfall_mm_h/70 - soil_saturation_pct/250 + slope_incline_deg/180) * (1.0 + 0.15*100/max(100,flow_velocity*20))
    cone = max(0.5, catchment_area_km2 * (0.08 + rainfall_mm_h/2000) * bedrock_runoff_factor)
    fused = fuse_risk(rainfall_mm_h, soil_saturation_pct, 2.0 + peak/300, peak, slope_incline_deg)
    slope_risk = "High" if fs < 1.0 else "Moderate" if fs < 1.3 else "Low"
    notes = ["Simulation is in-memory and does not create an alert.", "Factor of Safety is an engineering screening estimate, not a site certification."]
    if slope_risk == "High": notes.append("High slope-failure susceptibility under the selected saturation and incline assumptions.")
    hydro = [{"minutes":float(round(x,1)),"runoff_m3s":float(round(y,2)),"inundation_depth_m":float(round(max(0,y/peak*2.2),2))} for x,y in zip(t,runoff)]
    return {"threat_level": fused["threat_level"], "peak_runoff_m3s":round(peak,2), "factor_of_safety":round(fs,2),
            "slope_failure_risk":slope_risk, "time_to_inundation_hours":round(time_to_inundation,2),
            "vulnerable_population":int(vulnerable_population), "projected_flood_cone_km2":round(cone,2), "hydrograph":hydro, "notes":notes}
