import streamlit as st
import altair as alt
import pandas as pd
from utils.settlement_model import compute_settlement_economics, TRADITIONAL_COST_BPS, USDC_COST_BPS

st.set_page_config(page_title="Settlement Economics", layout="wide")
st.title("Settlement Economics Model")
st.caption("Quantify the business case for USDC rails vs traditional correspondent banking — the cost model a solutions analyst uses to justify the investment to a CFO.")

# ── Inputs ────────────────────────────────────────────────────────────────────
st.subheader("Deal Parameters")
c1, c2, c3 = st.columns(3)
with c1:
    volume = st.number_input("Annual Settlement Volume ($B)", min_value=0.1, max_value=500.0,
                              value=10.0, step=0.5)
with c2:
    region = st.selectbox("Region / Settlement Corridor",
                          ["North America", "Europe", "Asia Pacific", "LAC", "MEA"])
with c3:
    complexity = st.selectbox("Integration Complexity", ["Low", "Medium", "High"])

result = compute_settlement_economics(volume, region, complexity)

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Traditional Cost", f"{result['traditional_cost_bps']} bps")
k2.metric("USDC Cost", f"{result['usdc_cost_bps']} bps")
k3.metric("Annual Savings", f"${result['annual_savings_usd']:,.0f}")
k4.metric("Payback Period",
          f"{result['payback_months']:.1f} months" if result['payback_months'] < 120 else ">10 years")

st.divider()

left, right = st.columns(2)

# ── Cost comparison bar ───────────────────────────────────────────────────────
with left:
    st.subheader("Cost Comparison (bps)")
    cost_df = pd.DataFrame([
        {"Rail": "Traditional", "Cost (bps)": result["traditional_cost_bps"]},
        {"Rail": "USDC", "Cost (bps)": result["usdc_cost_bps"]},
    ])
    bar = (
        alt.Chart(cost_df)
        .mark_bar()
        .encode(
            y=alt.Y("Rail:N", title=None, sort=["Traditional", "USDC"]),
            x=alt.X("Cost (bps):Q", title="Settlement Cost (bps)"),
            color=alt.Color("Rail:N", scale=alt.Scale(
                domain=["Traditional", "USDC"], range=["#c0392b", "#1a7a4a"]
            ), legend=None),
            tooltip=["Rail:N", alt.Tooltip("Cost (bps):Q", format=".1f")],
        )
        .properties(height=160)
    )
    st.altair_chart(bar, use_container_width=True)

# ── 5-year cumulative savings ─────────────────────────────────────────────────
with right:
    st.subheader("5-Year Cumulative Net Savings")
    schedule_df = pd.DataFrame(result["five_year_schedule"])
    line = (
        alt.Chart(schedule_df)
        .mark_line(point=True, color="#1a7a4a")
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("cumulative_savings_usd:Q", title="Cumulative Net Savings ($)",
                    axis=alt.Axis(format="$,.0f")),
            tooltip=["year:O", alt.Tooltip("cumulative_savings_usd:Q", format="$,.0f", title="Net Savings")],
        )
        .properties(height=280)
    )
    zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(strokeDash=[4, 4], color="gray").encode(y="y:Q")
    st.altair_chart(line + zero_line, use_container_width=True)

# ── Regional benchmarks ───────────────────────────────────────────────────────
st.subheader("Settlement Cost Benchmarks Across Regions")
bench_df = pd.DataFrame([
    {"Region": r, "Rail": "Traditional", "Cost (bps)": TRADITIONAL_COST_BPS[r]}
    for r in TRADITIONAL_COST_BPS
] + [
    {"Region": r, "Rail": "USDC", "Cost (bps)": USDC_COST_BPS[r]}
    for r in USDC_COST_BPS
])

bench_chart = (
    alt.Chart(bench_df)
    .mark_bar()
    .encode(
        y=alt.Y("Region:N", title="Region", sort=["North America", "Europe", "Asia Pacific", "LAC", "MEA"]),
        x=alt.X("Cost (bps):Q", title="Settlement Cost (bps)"),
        color=alt.Color("Rail:N", scale=alt.Scale(
            domain=["Traditional", "USDC"], range=["#c0392b", "#1a7a4a"]
        )),
        yOffset="Rail:N",
        tooltip=["Region:N", "Rail:N", alt.Tooltip("Cost (bps):Q", format=".1f")],
    )
    .properties(height=300)
)
st.altair_chart(bench_chart, use_container_width=True)
st.caption("Traditional costs: correspondent banking averages. USDC costs: on-chain settlement estimates. Implementation costs: Low=$150K, Medium=$400K, High=$900K.")
