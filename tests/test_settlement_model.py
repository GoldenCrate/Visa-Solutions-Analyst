import pytest
from streamlit_app.utils.settlement_model import compute_settlement_economics


def _econ(volume=10.0, region="North America", complexity="Low"):
    return compute_settlement_economics(volume, region, complexity)


def test_savings_positive():
    result = _econ()
    assert result["annual_savings_usd"] > 0


def test_mea_highest_savings_bps():
    na = compute_settlement_economics(10, "North America", "Low")
    mea = compute_settlement_economics(10, "MEA", "Low")
    assert mea["savings_bps"] > na["savings_bps"]


def test_larger_volume_larger_savings():
    small = _econ(volume=1.0)
    large = _econ(volume=50.0)
    assert large["annual_savings_usd"] > small["annual_savings_usd"]


def test_high_complexity_higher_impl_cost():
    low = _econ(complexity="Low")
    high = _econ(complexity="High")
    assert high["implementation_cost_usd"] > low["implementation_cost_usd"]


def test_five_year_schedule_length():
    result = _econ()
    assert len(result["five_year_schedule"]) == 5


def test_five_year_schedule_increasing():
    result = _econ()
    sched = [r["cumulative_savings_usd"] for r in result["five_year_schedule"]]
    assert all(sched[i] < sched[i + 1] for i in range(len(sched) - 1))


def test_payback_shorter_with_larger_volume():
    small = _econ(volume=1.0)
    large = _econ(volume=100.0)
    assert large["payback_months"] < small["payback_months"]


def test_invalid_volume_raises():
    with pytest.raises(ValueError):
        compute_settlement_economics(-1, "North America", "Low")


def test_invalid_region_raises():
    with pytest.raises(ValueError):
        compute_settlement_economics(10, "Antarctica", "Low")


def test_invalid_complexity_raises():
    with pytest.raises(ValueError):
        compute_settlement_economics(10, "Europe", "Very Low")


def test_output_keys_present():
    result = _econ()
    expected = {"traditional_cost_bps", "usdc_cost_bps", "savings_bps",
                "annual_savings_usd", "implementation_cost_usd", "payback_months", "five_year_schedule"}
    assert expected.issubset(result.keys())
