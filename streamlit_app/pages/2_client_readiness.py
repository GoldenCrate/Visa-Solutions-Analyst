import streamlit as st
import altair as alt
import pandas as pd
from utils.data_loader import load_clients
from utils.readiness_score import compute_readiness_score

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

TIER_COLOR = {
    "Ready":       COLORS["green"],
    "Developing":  COLORS["amber"],
    "Early Stage": COLORS["red"],
}

st.set_page_config(page_title="Client Readiness Assessment", layout="wide")
st.title("Client Readiness Assessment")
st.caption("Score a client's readiness to adopt Visa USDC settlement rails — the pre-sales solutioning tool a solutions analyst uses before every client meeting.")

clients_df = load_clients()

mode = st.radio("Assessment mode", ["Browse existing clients", "Assess a new client"], horizontal=True)
st.divider()

if mode == "Browse existing clients":
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        type_filter = st.multiselect("Client Type", options=sorted(clients_df["client_type"].unique()),
                                     default=sorted(clients_df["client_type"].unique()))
    with col_f2:
        region_filter = st.multiselect("Region", options=sorted(clients_df["region"].unique()),
                                       default=sorted(clients_df["region"].unique()))

    filtered = clients_df[
        clients_df["client_type"].isin(type_filter) &
        clients_df["region"].isin(region_filter)
    ].copy()

    results = []
    for _, row in filtered.iterrows():
        r = compute_readiness_score(
            row["tech_readiness"], row["compliance_readiness"],
            row["integration_complexity"], row["current_settlement"],
        )
        results.append({
            "Client": row["client_name"],
            "Type": row["client_type"],
            "Region": row["region"],
            "Score": r["score"],
            "Tier": r["tier"],
            "Volume_B": row["annual_volume_bn"],
        })

    result_df = pd.DataFrame(results).sort_values("Score", ascending=False)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Clients Assessed", len(result_df))
    k2.metric("Ready", len(result_df[result_df["Tier"] == "Ready"]))
    k3.metric("Developing", len(result_df[result_df["Tier"] == "Developing"]))
    k4.metric("Early Stage", len(result_df[result_df["Tier"] == "Early Stage"]))

    st.markdown("### Only 28% of Clients Are Ready — Banks Lead on Compliance, Fintechs Lead on Technology")
    st.caption("The Developing clients represent the near-term pipeline — prioritise those closest to score 70.")

    st.subheader("Client Readiness Scorecard")

    def color_tier(val):
        return f"color: {TIER_COLOR.get(val, 'black')}; font-weight: bold"

    styled = result_df.style.map(color_tier, subset=["Tier"]).format(
        {"Score": "{:.1f}", "Volume_B": "${:.1f}B"}
    )
    st.dataframe(styled, use_container_width=True, height=380)

    # ── Score distribution ─────────────────────────────────────────────────────
    st.markdown("### Ready Clients (Blue) Cluster at the Top — Fintechs and Banks Lead")
    st.caption("Grey points = Developing or Early Stage — the pipeline to build toward readiness.")
    scatter = (
        alt.Chart(result_df)
        .mark_circle(size=90)
        .encode(
            x=alt.X("Type:N", title="Client Type", axis=alt.Axis(grid=False)),
            y=alt.Y("Score:Q", title="Readiness Score", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(grid=False)),
            color=alt.condition(
                alt.datum.Tier == "Ready",
                alt.value(COLORS["blue"]),
                alt.value(COLORS["grey"])
            ),
            tooltip=["Client:N", "Type:N", "Region:N",
                     alt.Tooltip("Score:Q", format=".1f"), "Tier:N",
                     alt.Tooltip("Volume_B:Q", title="Volume ($B)", format="$.1f")],
        )
        .properties(height=300)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(scatter, use_container_width=True)

else:
    st.markdown("### Score Any Client in Real Time — Adjust Discovery Call Inputs")
    st.caption("Move tech readiness or compliance sliders to see the biggest impact on overall score.")
    st.info("Enter discovery-call details below to generate a readiness score in real time.")

    c1, c2 = st.columns(2)
    with c1:
        client_name = st.text_input("Client Name", value="Acme Bank")
        client_type = st.selectbox("Client Type", ["Bank", "Fintech", "Merchant", "Enabler"])
        region = st.selectbox("Region", ["North America", "Europe", "Asia Pacific", "LAC", "MEA"])
    with c2:
        tech = st.slider("Technology Readiness (0-100)", 0, 100, 55,
                         help="API infrastructure, tokenization capability, cloud maturity")
        compliance = st.slider("Compliance Readiness (0-100)", 0, 100, 60,
                               help="AML/KYC policies, regulatory approvals, audit readiness")
        complexity = st.selectbox("Integration Complexity", ["Low", "Medium", "High"])
        settlement = st.selectbox("Current Settlement Experience",
                                  ["Traditional", "Partial Crypto", "Exploring"])

    result = compute_readiness_score(tech, compliance, complexity, settlement)
    score, tier, gaps, subscores = result["score"], result["tier"], result["gaps"], result["subscores"]

    color = TIER_COLOR[tier]

    st.divider()
    st.markdown(f"### {client_name} — <span style='color:{color}'>{tier}</span> ({score}/100)", unsafe_allow_html=True)

    sub_df = pd.DataFrame(
        [{"Component": k, "Score": v, "Weight": w}
         for (k, v), w in zip(subscores.items(), ["40%", "35%", "15%", "10%"])]
    )
    bar = (
        alt.Chart(sub_df)
        .mark_bar()
        .encode(
            x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(grid=False)),
            y=alt.Y("Component:N", sort="-x", axis=alt.Axis(grid=False)),
            color=alt.condition(
                alt.datum.Score >= 65,
                alt.value(COLORS["green"]),
                alt.value(COLORS["red"]),
            ),
            tooltip=["Component:N", "Score:Q", "Weight:N"],
        )
        .properties(height=180)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(bar, use_container_width=True)

    st.markdown("### Identified Gaps — Address These Before Pitching USDC Rails")
    for gap in gaps:
        st.warning(gap) if "No critical" not in gap else st.success(gap)
