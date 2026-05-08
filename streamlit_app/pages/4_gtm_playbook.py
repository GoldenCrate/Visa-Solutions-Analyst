import streamlit as st
import altair as alt
import pandas as pd
from utils.data_loader import load_clients
from utils.readiness_score import compute_readiness_score
from utils.settlement_model import compute_settlement_economics
from utils.gtm_pitch import generate_gtm_pitch, answer_followup

COLORS = {
    "navy":  "#1e3a5f",
    "blue":  "#2563eb",
    "grey":  "#9ca3af",
    "red":   "#dc2626",
    "amber": "#d97706",
    "green": "#16a34a",
}

st.set_page_config(page_title="GTM Playbook", layout="wide")
st.title("GTM Playbook & AI Pitch Generator")
st.caption("Generate a client-tailored pre-sales pitch with Claude AI, then explore the full client prioritization matrix below.")

clients_df = load_clients()

# ── Score all clients ─────────────────────────────────────────────────────────
scored = []
for _, row in clients_df.iterrows():
    r = compute_readiness_score(
        row["tech_readiness"], row["compliance_readiness"],
        row["integration_complexity"], row["current_settlement"],
    )
    econ = compute_settlement_economics(
        row["annual_volume_bn"], row["region"], row["integration_complexity"]
    )
    scored.append({
        "Client": row["client_name"],
        "Type": row["client_type"],
        "Region": row["region"],
        "Readiness_Score": r["score"],
        "Tier": r["tier"],
        "Volume_B": row["annual_volume_bn"],
        "Savings_M": round(econ["annual_savings_usd"] / 1_000_000, 2),
        "Payback_Months": econ["payback_months"],
        "_gaps": r["gaps"],
        "_complexity": row["integration_complexity"],
        "_econ": econ,
    })

scored_df = pd.DataFrame(scored)

# ── AI Pitch Generator ────────────────────────────────────────────────────────
st.subheader("AI Pitch Generator")
st.markdown("Select a client to generate a Claude-powered, tailored pre-sales pitch and objection handler.")

top_clients = scored_df.sort_values("Readiness_Score", ascending=False).head(20)
client_choice = st.selectbox(
    "Select a client",
    options=top_clients["Client"].tolist(),
    format_func=lambda c: (
        f"{c} — "
        f"{top_clients.loc[top_clients['Client']==c, 'Tier'].values[0]} "
        f"({top_clients.loc[top_clients['Client']==c, 'Readiness_Score'].values[0]:.0f}/100)"
    )
)

selected = scored_df[scored_df["Client"] == client_choice].iloc[0]
client_row = clients_df[clients_df["client_name"] == client_choice].iloc[0]

with st.expander("Client snapshot", expanded=True):
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Readiness Score", f"{selected['Readiness_Score']:.1f}/100")
    d2.metric("Tier", selected["Tier"])
    d3.metric("Annual Volume", f"${selected['Volume_B']:.1f}B")
    d4.metric("Est. Annual Savings", f"${selected['Savings_M']:.2f}M")

    st.markdown("**Identified Gaps:**")
    for gap in selected["_gaps"]:
        st.write(f"- {gap}")

# Reset chat when client changes
if "last_client" not in st.session_state or st.session_state["last_client"] != client_choice:
    st.session_state["last_client"] = client_choice
    st.session_state["pitch_generated"] = False
    st.session_state["pitch_context"] = ""
    st.session_state["chat_history"] = []
    st.session_state["pitch_bullets"] = []
    st.session_state["top_objection"] = ""

if st.button("Generate GTM Pitch", type="primary"):
    with st.spinner("Generating pitch with Claude AI..."):
        try:
            pitch = generate_gtm_pitch(
                client_name=client_choice,
                client_type=selected["Type"],
                region=selected["Region"],
                readiness_tier=selected["Tier"],
                readiness_score=selected["Readiness_Score"],
                gaps=selected["_gaps"],
                annual_savings_usd=selected["_econ"]["annual_savings_usd"],
                payback_months=selected["_econ"]["payback_months"],
            )
            st.session_state["pitch_generated"] = True
            st.session_state["pitch_bullets"] = pitch["pitch_bullets"]
            st.session_state["top_objection"] = pitch["top_objection"]
            st.session_state["chat_history"] = []
            gaps_text = "\n".join(f"- {g}" for g in selected["_gaps"])
            st.session_state["pitch_context"] = f"""You are a Visa Crypto Solutions analyst who just prepared a pre-sales pitch for {client_choice} ({selected['Type']}, {selected['Region']}).

Client profile:
- Readiness tier: {selected['Tier']} (score: {selected['Readiness_Score']:.1f}/100)
- Annual settlement volume: ${selected['Volume_B']:.1f}B
- Estimated annual savings on USDC rails: ${selected['_econ']['annual_savings_usd']:,.0f}
- Payback period: {selected['_econ']['payback_months']:.1f} months
- Identified gaps:
{gaps_text}

Pitch you generated:
{chr(10).join(f'- {b}' for b in pitch['pitch_bullets'])}

Top objection flagged: {pitch['top_objection']}

Answer any follow-up questions the account executive has about this client or pitch. Be concise and practical — this is a pre-meeting prep tool, not a research report."""

        except Exception as e:
            st.error(f"API call failed: {e}. Ensure ANTHROPIC_API_KEY is set in your Streamlit secrets.")

# ── Show pitch + chat if generated ───────────────────────────────────────────
if st.session_state.get("pitch_generated"):
    st.subheader("Pre-Sales Pitch")
    for bullet in st.session_state["pitch_bullets"]:
        st.markdown(f"- {bullet}")

    st.subheader("Top Objection to Anticipate")
    st.info(st.session_state["top_objection"])

    st.divider()
    st.subheader("Ask a Follow-Up Question")
    st.caption("Ask Claude anything about this client or pitch — how to handle objections, what to emphasise, competitive angles, next steps.")

    with st.form("followup_form", clear_on_submit=True):
        user_q = st.text_input(
            "Your question",
            placeholder="e.g. How should I handle it if they say they're already working with a competitor?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Ask", type="primary")

    if submitted and user_q.strip():
        st.session_state["chat_history"].append({"role": "user", "content": user_q})
        try:
            answer = answer_followup(
                system_context=st.session_state["pitch_context"],
                chat_history=st.session_state["chat_history"][:-1],
                user_question=user_q,
            )
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"API call failed: {e}")

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.caption("Powered by Claude Haiku via the Anthropic API. Each generation uses ~500 tokens (~$0.0001).")

st.divider()

# ── Segment prioritization matrix ─────────────────────────────────────────────
st.markdown("### Ready Fintechs in North America Are the Highest-Priority Targets — Shortest Path to Commercial Close")
st.caption("Top-right quadrant = act now. Bottom-left = nurture. Do not pursue Early Stage clients this quarter.")

st.markdown("### Navy Clients Are Immediate Priorities — High Readiness and Large Settlement Volumes")
st.caption("Navy = act now (top-right quadrant). Grey = developing pipeline. Amber lines = priority thresholds.")

median_vol = scored_df["Volume_B"].median()
priority_matrix = (
    alt.Chart(scored_df)
    .mark_circle()
    .encode(
        x=alt.X("Readiness_Score:Q", scale=alt.Scale(domain=[0, 100]), title="Readiness Score", axis=alt.Axis(grid=False)),
        y=alt.Y("Volume_B:Q", title="Annual Settlement Volume ($B)", axis=alt.Axis(grid=False)),
        size=alt.Size("Savings_M:Q", legend=None, scale=alt.Scale(range=[40, 600])),
        color=alt.condition(
            (alt.datum.Readiness_Score >= 70) & (alt.datum.Volume_B >= median_vol),
            alt.value(COLORS["navy"]),
            alt.value(COLORS["grey"])
        ),
        shape=alt.Shape("Type:N"),
        tooltip=[
            "Client:N", "Type:N", "Region:N",
            alt.Tooltip("Readiness_Score:Q", title="Readiness Score", format=".1f"),
            alt.Tooltip("Volume_B:Q", title="Volume ($B)", format="$.1f"),
            alt.Tooltip("Savings_M:Q", title="Annual Savings ($M)", format="$.2f"),
            alt.Tooltip("Payback_Months:Q", title="Payback (months)", format=".1f"),
            "Tier:N",
        ],
    )
    .properties(height=400)
    .interactive()
)
vline = alt.Chart(pd.DataFrame({"x": [70]})).mark_rule(strokeDash=[6, 3], color=COLORS["amber"]).encode(x="x:Q")
hline = alt.Chart(pd.DataFrame({"y": [median_vol]})).mark_rule(strokeDash=[6, 3], color=COLORS["amber"]).encode(y="y:Q")
priority_chart = (priority_matrix + vline + hline).configure_view(strokeWidth=0)
st.altair_chart(priority_chart, use_container_width=True)

st.divider()

# ── Recommended approach by tier ──────────────────────────────────────────────
st.subheader("GTM Approach by Readiness Tier")
tier_cols = st.columns(3)
with tier_cols[0]:
    st.markdown("**Ready (score 70+)**")
    st.success("Move directly to commercial terms. Lead with settlement cost savings and speed to live. Target 90-day close.")
with tier_cols[1]:
    st.markdown("**Developing (45-69)**")
    st.warning("Run a 60-day technical pilot. Pair with a Visa implementation specialist. Close after pilot success metrics.")
with tier_cols[2]:
    st.markdown("**Early Stage (<45)**")
    st.error("Do not pursue a deal now. Add to a 6-month nurture track. Assign to regional enablement team for infrastructure support.")
