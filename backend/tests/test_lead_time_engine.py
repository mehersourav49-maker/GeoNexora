from app.services.lead_time_engine import calculate_lead_time
def test_lead_time_decreases_with_hazard():
    low=calculate_lead_time(40,20,20,10,current_stage_m=1.0)
    high=calculate_lead_time(220,120,140,10,current_stage_m=3.8)
    assert high.lead_time_hours_min < low.lead_time_hours_min
    assert high.threat_level in {"High","Critical"}
