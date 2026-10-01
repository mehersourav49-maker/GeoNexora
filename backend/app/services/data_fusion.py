from .geo_risk import explain_threat

def fuse_risk(rainfall_mm_h: float, soil_saturation_pct: float, river_level_m: float,
              river_flow_m3s: float, slope_incline_deg: float) -> dict:
    rainfall = min(max(rainfall_mm_h / 120.0, 0.0), 1.0)
    soil = min(max(soil_saturation_pct / 100.0, 0.0), 1.0)
    level = min(max(river_level_m / 5.0, 0.0), 1.0)
    flow = min(max(river_flow_m3s / 250.0, 0.0), 1.0)
    slope = min(max((slope_incline_deg - 15) / 40.0, 0.0), 1.0)
    # The published threat score uses the same deterministic feature weights as XAI.
    # River stage and flow remain visible as contextual drivers until calibrated
    # drainage-choke and basin-specific model inputs are available.
    explainability = explain_threat(rainfall_mm_h, soil_saturation_pct, slope_incline_deg, drainage_choke_pct=0.0)
    score = explainability["score"]
    threat = explainability["threat_level"]
    return {"score": round(score, 3), "threat_level": threat,
            "drivers": [{"name":"Rainfall intensity","contribution":round(.28*rainfall,3)},
                        {"name":"Soil saturation","contribution":round(.20*soil,3)},
                        {"name":"River stage","contribution":round(.25*level,3)},
                        {"name":"Upstream flow","contribution":round(.20*flow,3)},
                        {"name":"Slope susceptibility","contribution":round(.07*slope,3)}],
            "explainability": explainability}
