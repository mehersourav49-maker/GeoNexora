import math
from app.services.simulation_engine import curve_number_for_amc, run_simulation
from app.services.geo_risk import FEATURE_WEIGHTS, explain_threat


def test_scs_cn_retention_and_runoff_are_physical():
    result = run_simulation(100, 80, 80, 35, 1.0, 1000, curve_number=78, storm_duration_hours=1)
    expected_s = 25400 / result["curve_number"] - 254
    assert math.isclose(result["potential_maximum_retention_mm"], expected_s, abs_tol=0.01)
    assert result["direct_runoff_depth_mm"] > 0
    assert result["peak_runoff_m3s"] > 0


def test_no_runoff_below_initial_abstraction():
    result = run_simulation(10, 1, 40, 20, 1.0, 0, curve_number=60, storm_duration_hours=1)
    assert result["direct_runoff_depth_mm"] == 0
    assert result["peak_runoff_m3s"] == 0


def test_amc_and_xai_weights_are_deterministic():
    cn, amc = curve_number_for_amc(78, 90)
    assert amc == "AMC III" and cn >= 78
    assert math.isclose(sum(FEATURE_WEIGHTS.values()), 1.0)
    assert explain_threat(100, 90, 32)["threat_level"] in {"High", "Critical"}
