from app.services.data_fusion import fuse_risk
def test_fusion_escalates():
    assert fuse_risk(10,20,1,20,15)["threat_level"]=="Low"
    assert fuse_risk(140,100,5,300,45)["threat_level"]=="Critical"
