from __future__ import annotations

FEATURE_WEIGHTS = {"rainfall_intensity": 0.40, "soil_saturation": 0.35, "slope_instability": 0.15, "drainage_choke": 0.10}


def classify(score: float) -> str:
    return "Critical" if score >= .8 else "High" if score >= .6 else "Moderate" if score >= .35 else "Low"


def polygon_from_center(lat: float, lon: float, d: float = .025):
    return [[lon-d,lat-d],[lon+d,lat-d],[lon+d,lat+d],[lon-d,lat+d],[lon-d,lat-d]]


def explain_threat(rainfall_mm_h: float, soil_saturation_pct: float, slope_deg: float,
                   drainage_choke_pct: float = 0.0, curve_number: float = 78.0,
                   estimated_arrival_minutes: int | None = None) -> dict:
    """Deterministic weighted attribution. Inputs are normalized to documented ranges."""
    features = {
        "rainfall_intensity": min(1.0, max(0.0, rainfall_mm_h / 120.0)),
        "soil_saturation": min(1.0, max(0.0, soil_saturation_pct / 100.0)),
        "slope_instability": min(1.0, max(0.0, (slope_deg - 10.0) / 35.0)),
        "drainage_choke": min(1.0, max(0.0, drainage_choke_pct / 100.0)),
    }
    contributions = {k: round(v * FEATURE_WEIGHTS[k], 4) for k, v in features.items()}
    score = min(1.0, sum(contributions.values()))
    threat = classify(score)
    retention = 25400.0 / min(99.0, max(30.0, curve_number)) - 254.0
    amc = "AMC III" if soil_saturation_pct >= 75 else "AMC II" if soil_saturation_pct >= 35 else "AMC I"
    arrival = f" Peak surge arrival estimate: {estimated_arrival_minutes} minutes; treat as model-derived, not a guaranteed warning window." if estimated_arrival_minutes is not None else " No validated wave-arrival estimate is available."
    advisory = (f"{threat} Flash Flood Threat: rainfall {rainfall_mm_h:.1f} mm/h; soil saturation {amc} ({soil_saturation_pct:.0f}%) "
                f"and slope {slope_deg:.1f}°; estimated SCS retention S={retention:.1f} mm. Review gauges and local conditions before issuing an official warning." + arrival)
    return {"score": round(score, 3), "threat_level": threat, "weights": FEATURE_WEIGHTS.copy(),
            "normalized_features": {k: round(v, 3) for k, v in features.items()},
            "contributions": contributions, "antecedent_moisture_condition": amc,
            "potential_maximum_retention_mm": round(retention, 2), "commander_advisory": advisory}
