import streamlit as st
import altair as alt
from utils.data_loader import load_market

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

st.set_page_config(page_title="Stablecoin Market Landscape", layout="wide")
st.title("Stablecoin Market Landscape")
st.caption("Global USDC adoption trends across client segments and regions — the market context a solutions analyst brings into every client conversation.")

df = load_market()

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    client_filter = st.multiselect(
        "Client Type", options=sorted(df["client_type"].unique()),
        default=sorted(df["client_type"].unique())
    )
with col2:
    region_filter = st.multiselect(
        "Region", options=sorted(df["region"].unique()),
        default=sorted(df["region"].unique())
    )

filtered = df[df["client_type"].isin(client_filter) & df["region"].isin(region_filter)]

# ── KPI cards ─────────────────────────────────────────────────────────────────
latest = filtered[filtered["month"] == filtered["month"].max()]
prior  = filtered[filtered["month"] == filtered["month"].sort_values().unique()[-13]] \
    if len(filtered["month"].unique()) >= 13 else latest

k1, k2, k3, k4 = st.columns(4)
avg_adoption   = latest["adoption_index"].mean()
prior_adoption = prior["adoption_index"].mean()
total_volume   = latest["usdc_volume_bn"].sum()
prior_volume   = prior["usdc_volume_bn"].sum()
total_partners = latest["live_partners"].sum()
avg_growth     = latest["yoy_growth_pct"].mean()

k1.metric("Avg Adoption Index", f"{avg_adoption:.1f}", f"{avg_adoption - prior_adoption:+.1f} YoY")
k2.metric("USDC Volume (bn)", f"${total_volume:.1f}B", f"{(total_volume - prior_volume) / prior_volume * 100:+.1f}%")
k3.metric("Live Partners", f"{total_partners:,}")
k4.metric("Avg YoY Growth", f"{avg_growth:.1f}%")

st.divider()

st.markdown("### North America Leads USDC Volume but MEA Shows the Fastest Year-on-Year Growth")
st.caption("Two different GTM stories: defend the North America lead, invest early in MEA infrastructure.")

# ── Adoption index trend by region ────────────────────────────────────────────
st.markdown("### MEA and North America Show the Strongest Adoption Index Growth Across All Regions")
st.caption("Blue lines = priority regions (North America + MEA). Grey = monitor. Use filters to isolate.")
trend = filtered.groupby(["month", "region"])["adoption_index"].mean().reset_index()
chart = (
    alt.Chart(trend)
    .mark_line(point=True)
    .encode(
        x=alt.X("month:T", title="Month", axis=alt.Axis(grid=False)),
        y=alt.Y("adoption_index:Q", title="Adoption Index (0-100)", scale=alt.Scale(zero=False), axis=alt.Axis(grid=False)),
        color=alt.condition(
            (alt.datum.region == "North America") | (alt.datum.region == "MEA"),
            alt.value(COLORS["blue"]),
            alt.value(COLORS["grey"])
        ),
        tooltip=["month:T", "region:N", alt.Tooltip("adoption_index:Q", format=".1f")],
    )
    .properties(height=320)
    .interactive()
    .configure_view(strokeWidth=0)
)
st.altair_chart(chart, use_container_width=True)

# ── USDC volume heatmap ───────────────────────────────────────────────────────
st.markdown("### Banks and Central Banks Generate the Most USDC Volume — North America Dominates")
st.caption("Heatmap intensity = transaction volume ($B). Darker blue = more volume in that segment-region pair.")
heat_data = latest.groupby(["client_type", "region"])["usdc_volume_bn"].sum().reset_index()
heatmap = (
    alt.Chart(heat_data)
    .mark_rect()
    .encode(
        x=alt.X("region:N", title=None, axis=alt.Axis(grid=False)),
        y=alt.Y("client_type:N", title=None, axis=alt.Axis(grid=False)),
        color=alt.Color("usdc_volume_bn:Q", scale=alt.Scale(scheme="blues"), legend=alt.Legend(title="Volume ($B)")),
        tooltip=["client_type:N", "region:N", alt.Tooltip("usdc_volume_bn:Q", format="$.2f", title="Volume ($B)")],
    )
    .properties(height=220)
    .configure_view(strokeWidth=0)
)
st.altair_chart(heatmap, use_container_width=True)

# ── Growth by client type ─────────────────────────────────────────────────────
st.markdown("### All Client Types Are Growing Double-Digits — Fintechs Lead YoY Expansion")
st.caption("YoY growth across all segments confirms market momentum — prioritise highest-growth segments for outreach.")
growth_data = latest.groupby("client_type")["yoy_growth_pct"].mean().reset_index()
growth_bar = (
    alt.Chart(growth_data)
    .mark_bar(color=COLORS["navy"])
    .encode(
        x=alt.X("client_type:N", title="Client Type", sort="-y", axis=alt.Axis(grid=False)),
        y=alt.Y("yoy_growth_pct:Q", title="Avg YoY Growth (%)", axis=alt.Axis(grid=False)),
        tooltip=["client_type:N", alt.Tooltip("yoy_growth_pct:Q", format=".1f", title="Growth (%)")],
    )
    .properties(height=240)
)
growth_labels = growth_bar.mark_text(dy=-6, fontSize=11).encode(
    text=alt.Text("yoy_growth_pct:Q", format=".1f"),
    color=alt.value(COLORS["navy"])
)
growth_bar = (growth_bar + growth_labels).configure_view(strokeWidth=0)
st.altair_chart(growth_bar, use_container_width=True)

st.caption("Data: Synthetic dataset modelling global stablecoin adoption patterns. Generated for portfolio demonstration.")
