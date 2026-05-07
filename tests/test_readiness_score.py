import pytest
from streamlit_app.utils.readiness_score import compute_readiness_score


def _score(tech=70, compliance=70, complexity="Low", settlement="Traditional"):
    return compute_readiness_score(tech, compliance, complexity, settlement)


def test_ready_tier():
    result = _score(tech=90, compliance=88, complexity="Low", settlement="Partial Crypto")
    assert result["tier"] == "Ready"
    assert result["score"] >= 70


def test_developing_tier():
    result = _score(tech=55, compliance=58, complexity="Medium", settlement="Traditional")
    assert result["tier"] == "Developing"
    assert 45 <= result["score"] < 70


def test_early_stage_tier():
    result = _score(tech=20, compliance=25, complexity="High", settlement="Traditional")
    assert result["tier"] == "Early Stage"
    assert result["score"] < 45


def test_score_bounded_0_to_100():
    result = _score(tech=100, compliance=100, complexity="Low", settlement="Partial Crypto")
    assert 0 <= result["score"] <= 100
    result2 = _score(tech=0, compliance=0, complexity="High", settlement="Traditional")
    assert 0 <= result2["score"] <= 100


def test_no_gaps_when_ready():
    result = _score(tech=95, compliance=92, complexity="Low", settlement="Partial Crypto")
    assert any("No critical gaps" in g for g in result["gaps"])


def test_tech_gap_flagged():
    result = _score(tech=30, compliance=80, complexity="Low", settlement="Traditional")
    assert any("Technology" in g for g in result["gaps"])


def test_compliance_gap_flagged():
    result = _score(tech=80, compliance=40, complexity="Low", settlement="Traditional")
    assert any("Compliance" in g for g in result["gaps"])


def test_high_complexity_gap_flagged():
    result = _score(tech=80, compliance=80, complexity="High", settlement="Traditional")
    assert any("integration complexity" in g.lower() for g in result["gaps"])


def test_invalid_tech_readiness_raises():
    with pytest.raises(ValueError):
        compute_readiness_score(110, 70, "Low", "Traditional")


def test_invalid_complexity_raises():
    with pytest.raises(ValueError):
        compute_readiness_score(70, 70, "Very High", "Traditional")


def test_invalid_settlement_raises():
    with pytest.raises(ValueError):
        compute_readiness_score(70, 70, "Low", "Blockchain")


def test_subscores_keys_present():
    result = _score()
    assert set(result["subscores"].keys()) == {"Technology", "Compliance", "Integration", "Settlement Experience"}
