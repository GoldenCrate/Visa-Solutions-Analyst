import streamlit as st
import altair as alt
import pandas as pd
from utils.settlement_model import compute_settlement_economics, TRADITIONAL_COST_BPS, USDC_COST_BPS

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

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

st.markdown("### MEA Clients Save the Most on USDC Rails — But Take the Longest to Break Even")
st.caption("North America offers fastest payback — ideal for early pilots. MEA is the long-term strategic prize.")

left, right = st.columns(2)

# ── Cost comparison bar ───────────────────────────────────────────────────────
with left:
    st.markdown("### USDC Rails Cost 40–75% Less Than Traditional Correspondent Banking")
    st.caption("Grey = traditional cost. Navy = USDC cost. Gap = annual savings potential.")
    cost_df = pd.DataFrame([
        {"Rail": "Traditional", "Cost (bps)": result["traditional_cost_bps"]},
        {"Rail": "USDC", "Cost (bps)": result["usdc_cost_bps"]},
    ])
    bar = (
        alt.Chart(cost_df)
        .mark_bar()
        .encode(
            y=alt.Y("Rail:N", title=None, sort=["Traditional", "USDC"], axis=alt.Axis(grid=False)),
            x=alt.X("Cost (bps):Q", title="Settlement Cost (bps)", axis=alt.Axis(grid=False)),
            color=alt.condition(
                alt.datum.Rail == "USDC",
                alt.value(COLORS["navy"]),
                alt.value(COLORS["grey"])
            ),
            tooltip=["Rail:N", alt.Tooltip("Cost (bps):Q", format=".1f")],
        )
        .properties(height=160)
    )
    cost_labels = bar.mark_text(align='left', dx=4, fontSize=11).encode(
        text=alt.Text("Cost (bps):Q", format=".1f"),
        color=alt.value(COLORS["navy"])
    )
    bar = (bar + cost_labels).configure_view(strokeWidth=0)
    st.altair_chart(bar, use_container_width=True)

# ── 5-year cumulative savings ─────────────────────────────────────────────────
with right:
    st.markdown("### Break-Even Typically Reached in Year 2 — Pure Savings Thereafter")
    st.caption("Blue dot = break-even point. Implementation cost recovered, then savings compound annually.")
    schedule_df = pd.DataFrame(result["five_year_schedule"])

    breakeven_df = schedule_df[schedule_df["cumulative_savings_usd"] >= 0]
    breakeven_year = breakeven_df["year"].iloc[0] if len(breakeven_df) > 0 else None

    line = (
        alt.Chart(schedule_df)
        .mark_line(point=True, color=COLORS["navy"])
        .encode(
            x=alt.X("year:O", title="Year", axis=alt.Axis(grid=False)),
            y=alt.Y("cumulative_savings_usd:Q", title="Cumulative Net Savings ($)",
                    axis=alt.Axis(format="$,.0f", grid=False)),
            tooltip=["year:O", alt.Tooltip("cumulative_savings_usd:Q", format="$,.0f", title="Net Savings")],
        )
        .properties(height=280)
    )
    zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(strokeDash=[4, 4], color=COLORS["grey"]).encode(y="y:Q")
    layers = [line, zero_line]
    if breakeven_year:
        be_point = alt.Chart(schedule_df[schedule_df["year"] == breakeven_year]).mark_point(
            color=COLORS["blue"], size=150, filled=True
        ).encode(x="year:O", y="cumulative_savings_usd:Q")
        be_label = alt.Chart(schedule_df[schedule_df["year"] == breakeven_year]).mark_text(
            align='left', dx=8, fontSize=11, color=COLORS["blue"], text="Break-even"
        ).encode(x="year:O", y="cumulative_savings_usd:Q")
        layers += [be_point, be_label]
    savings_chart = alt.layer(*layers).properties(height=280).configure_view(strokeWidth=0)
    st.altair_chart(savings_chart, use_container_width=True)

# ── Regional benchmarks ───────────────────────────────────────────────────────
st.markdown("### USDC Costs Are Consistently Lower Across Every Region — MEA Gap Is Largest")
st.caption("Navy = USDC cost. Grey = traditional cost. Wider gap = greater savings potential.")
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
        y=alt.Y("Region:N", title="Region", sort=["North America", "Europe", "Asia Pacific", "LAC", "MEA"], axis=alt.Axis(grid=False)),
        x=alt.X("Cost (bps):Q", title="Settlement Cost (bps)", axis=alt.Axis(grid=False)),
        color=alt.condition(
            alt.datum.Rail == "USDC",
            alt.value(COLORS["navy"]),
            alt.value(COLORS["grey"])
        ),
        yOffset="Rail:N",
        tooltip=["Region:N", "Rail:N", alt.Tooltip("Cost (bps):Q", format=".1f")],
    )
    .properties(height=300)
    .configure_view(strokeWidth=0)
)
st.altair_chart(bench_chart, use_container_width=True)
st.caption("Traditional costs: correspondent banking averages. USDC costs: on-chain settlement estimates. Implementation costs: Low=$150K, Medium=$400K, High=$900K.")
