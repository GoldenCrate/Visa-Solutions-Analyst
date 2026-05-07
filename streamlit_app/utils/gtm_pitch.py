"""
GTM pitch generator — calls Claude API to produce a client-tailored
pre-sales recommendation based on readiness assessment outputs.
"""

from __future__ import annotations
import anthropic
import os
import streamlit as st


def _get_api_key() -> str:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY", "")


def generate_gtm_pitch(
    client_name: str,
    client_type: str,
    region: str,
    readiness_tier: str,
    readiness_score: float,
    gaps: list[str],
    annual_savings_usd: float,
    payback_months: float,
) -> dict:
    """
    Returns:
        pitch_bullets : list of 3 strings — the GTM pitch points
        top_objection : string — the most likely objection + how to handle it
    """
    gaps_text = "\n".join(f"- {g}" for g in gaps)
    savings_fmt = f"${annual_savings_usd:,.0f}"
    payback_fmt = f"{payback_months:.1f} months"

    prompt = f"""You are a Visa Crypto Solutions analyst preparing a pre-sales briefing for an account executive.

Client context:
- Client: {client_name} ({client_type}, {region})
- Stablecoin Readiness Tier: {readiness_tier} (score: {readiness_score}/100)
- Identified gaps:
{gaps_text}
- Estimated annual savings on USDC rails vs traditional settlement: {savings_fmt}
- Estimated payback period on implementation: {payback_fmt}

Write exactly 3 concise bullet points (each under 25 words) that the account executive should lead with in the opening pitch to this client. Focus on value, urgency, and fit — not product features.

Then write 1 sentence identifying the most likely objection this client will raise and how to handle it.

Format your response exactly as:
PITCH:
- [bullet 1]
- [bullet 2]
- [bullet 3]

OBJECTION: [objection and response]"""

    client = anthropic.Anthropic(api_key=_get_api_key())
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    pitch_bullets: list[str] = []
    top_objection = ""

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("- "):
            pitch_bullets.append(line[2:])
        elif line.startswith("OBJECTION:"):
            top_objection = line.replace("OBJECTION:", "").strip()

    return {"pitch_bullets": pitch_bullets[:3], "top_objection": top_objection}
