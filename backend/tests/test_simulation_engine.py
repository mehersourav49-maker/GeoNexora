from app.services.simulation_engine import run_simulation
def test_simulation_returns_hydrograph_and_fs():
    r=run_simulation(100,80,80,35,1.1,5000)
    assert r["peak_runoff_m3s"]>0
    assert 0.35 <= r["factor_of_safety"] <= 3.5
    assert len(r["hydrograph"])>10
