"""
Client stablecoin readiness scoring model.

Inputs are all observable during a pre-sales discovery call.
Returns a composite score (0-100), a tier label, and a list of gaps.
"""

from __future__ import annotations

COMPLEXITY_PENALTY = {"Low": 0, "Medium": -8, "High": -18}
SETTLEMENT_BONUS = {"Traditional": 0, "Partial Crypto": 10, "Exploring": 5}

WEIGHTS = {"tech": 0.40, "compliance": 0.35, "complexity": 0.15, "settlement": 0.10}


def compute_readiness_score(
    tech_readiness: float,
    compliance_readiness: float,
    integration_complexity: str,
    current_settlement: str,
) -> dict:
    """
    Returns:
        score       : float 0-100
        tier        : "Ready" | "Developing" | "Early Stage"
        gaps        : list of human-readable gap strings
        subscores   : dict with component breakdown
    """
    if not (0 <= tech_readiness <= 100):
        raise ValueError("tech_readiness must be 0-100")
    if not (0 <= compliance_readiness <= 100):
        raise ValueError("compliance_readiness must be 0-100")
    if integration_complexity not in COMPLEXITY_PENALTY:
        raise ValueError(f"integration_complexity must be one of {list(COMPLEXITY_PENALTY)}")
    if current_settlement not in SETTLEMENT_BONUS:
        raise ValueError(f"current_settlement must be one of {list(SETTLEMENT_BONUS)}")

    complexity_score = 100 + COMPLEXITY_PENALTY[integration_complexity]
    settlement_score = SETTLEMENT_BONUS[current_settlement] * 10

    raw = (
        WEIGHTS["tech"] * tech_readiness
        + WEIGHTS["compliance"] * compliance_readiness
        + WEIGHTS["complexity"] * complexity_score
        + WEIGHTS["settlement"] * settlement_score
    )
    score = round(min(100.0, max(0.0, raw)), 1)

    if score >= 70:
        tier = "Ready"
    elif score >= 45:
        tier = "Developing"
    else:
        tier = "Early Stage"

    gaps: list[str] = []
    if tech_readiness < 60:
        gaps.append("Technology infrastructure below threshold — API gateway and tokenization layer needed")
    if compliance_readiness < 65:
        gaps.append("Compliance framework gaps — AML/KYC policies for stablecoin flows require review")
    if integration_complexity == "High":
        gaps.append("High integration complexity — legacy core banking system migration required")
    if current_settlement == "Traditional":
        gaps.append("No crypto settlement experience — phased pilot recommended before full USDC migration")
    if not gaps:
        gaps.append("No critical gaps identified — client is ready to move to contract stage")

    return {
        "score": score,
        "tier": tier,
        "gaps": gaps,
        "subscores": {
            "Technology": round(tech_readiness, 1),
            "Compliance": round(compliance_readiness, 1),
            "Integration": round(complexity_score, 1),
            "Settlement Experience": round(float(settlement_score), 1),
        },
    }
