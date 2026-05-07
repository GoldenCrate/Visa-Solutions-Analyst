"""
Settlement economics model: USDC rails vs traditional correspondent banking.

Traditional correspondent banking costs: 25-40 bps on cross-border,
8-15 bps on domestic. USDC settlement: ~5-8 bps flat regardless of corridor.
"""

from __future__ import annotations

TRADITIONAL_COST_BPS = {
    "North America": 10.0,
    "Europe": 14.0,
    "Asia Pacific": 22.0,
    "LAC": 32.0,
    "MEA": 38.0,
}

USDC_COST_BPS = {
    "North America": 6.0,
    "Europe": 6.5,
    "Asia Pacific": 7.0,
    "LAC": 7.5,
    "MEA": 8.0,
}

IMPLEMENTATION_COST_USD = {
    "Low": 150_000,
    "Medium": 400_000,
    "High": 900_000,
}


def compute_settlement_economics(
    annual_volume_bn: float,
    region: str,
    integration_complexity: str,
) -> dict:
    """
    Returns annual savings, implementation cost, payback period, and
    year-by-year cumulative savings over 5 years.
    """
    if annual_volume_bn <= 0:
        raise ValueError("annual_volume_bn must be positive")
    if region not in TRADITIONAL_COST_BPS:
        raise ValueError(f"region must be one of {list(TRADITIONAL_COST_BPS)}")
    if integration_complexity not in IMPLEMENTATION_COST_USD:
        raise ValueError(f"integration_complexity must be one of {list(IMPLEMENTATION_COST_USD)}")

    trad_bps = TRADITIONAL_COST_BPS[region]
    usdc_bps = USDC_COST_BPS[region]
    savings_bps = trad_bps - usdc_bps

    volume_usd = annual_volume_bn * 1_000_000_000
    annual_savings = volume_usd * (savings_bps / 10_000)
    impl_cost = IMPLEMENTATION_COST_USD[integration_complexity]

    payback_months = (impl_cost / annual_savings * 12) if annual_savings > 0 else float("inf")

    yearly = []
    cumulative = -impl_cost
    for yr in range(1, 6):
        cumulative += annual_savings
        yearly.append({"year": yr, "cumulative_savings_usd": round(cumulative, 0)})

    return {
        "traditional_cost_bps": trad_bps,
        "usdc_cost_bps": usdc_bps,
        "savings_bps": round(savings_bps, 1),
        "annual_savings_usd": round(annual_savings, 0),
        "implementation_cost_usd": impl_cost,
        "payback_months": round(payback_months, 1),
        "five_year_schedule": yearly,
    }
