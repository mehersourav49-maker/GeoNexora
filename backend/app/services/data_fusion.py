def fuse_risk(rainfall_mm_h: float, soil_saturation_pct: float, river_level_m: float,
              river_flow_m3s: float, slope_incline_deg: float) -> dict:
    rainfall = min(rainfall_mm_h / 120.0, 1.0)
    soil = soil_saturation_pct / 100.0
    level = min(river_level_m / 5.0, 1.0)
    flow = min(river_flow_m3s / 250.0, 1.0)
    slope = min(max(slope_incline_deg - 15, 0) / 40.0, 1.0)
    score = 0.28*rainfall + 0.20*soil + 0.25*level + 0.20*flow + 0.07*slope
    if score >= .80: threat="Critical"
    elif score >= .60: threat="High"
    elif score >= .35: threat="Moderate"
    else: threat="Low"
    return {"score": round(score,3), "threat_level": threat,
            "drivers": [
                {"name":"Rainfall intensity","contribution":round(.28*rainfall,3)},
                {"name":"Soil saturation","contribution":round(.20*soil,3)},
                {"name":"River stage","contribution":round(.25*level,3)},
                {"name":"Upstream flow","contribution":round(.20*flow,3)},
                {"name":"Slope susceptibility","contribution":round(.07*slope,3)},
            ]}
