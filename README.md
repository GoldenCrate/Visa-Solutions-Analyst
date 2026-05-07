# Visa Stablecoin Solutions Analyst

This project models the analytical and client-facing work performed by a Solutions Analyst on Visa's Crypto Solutions team. It synthesises 560 rows of synthetic data across 80 client profiles and 480 market observations to surface stablecoin adoption trends, client readiness scores, settlement economics, and AI-generated pre-sales pitches. **The centrepiece is a Claude-powered GTM Pitch Generator — the kind of tool a solutions analyst uses before walking into a client meeting with a bank, fintech, or merchant.** Rather than a generic output, **Claude reads each client's actual data — their readiness score, identified gaps, annual settlement volume, and estimated savings — and generates a custom-tailored 3-bullet pre-sales pitch and objection handler specific to that client's situation.**

## Live Dashboard

**URL:** https://visa-solutions-analyst-nqkzmmsdmgor2awze5bn9m.streamlit.app/

## Job Posting

- **Role:** Analyst, Solutions Management
- **Company:** Visa Inc. — Crypto Solutions
- **Ref:** REF081443W

This project directly demonstrates the role's core responsibilities: client stablecoin solutioning, pre-sales preparation, Go-To-Market strategy, and AI tooling for research and prototyping.

## Tech Stack

| Layer | Tool |
|---|---|
| Data | Synthesized CSVs — Python generator script |
| Data Processing | Pandas |
| Scoring Models | Python pure functions (`compute_readiness_score`, `compute_settlement_economics`) |
| AI Pitch Generator | Anthropic Claude API (claude-haiku-4-5) |
| Visualisation | Altair |
| Dashboard | Streamlit (four-page multipage app) |
| Testing | pytest (23 unit tests) |
| Deployment | Streamlit Community Cloud |

## Dashboard Pages

**Page 1 — Market Landscape:** Global USDC adoption trends by region and client type. KPI cards, 24-month adoption index trend, volume heatmap, and YoY growth by segment — the market context a solutions analyst brings into every client conversation.

**Page 2 — Client Readiness Assessment:** Pre-sales solutioning tool. Browse 80 synthetic client profiles (banks, fintechs, merchants, enablers) scored on technology readiness, compliance readiness, and integration complexity — or manually assess a new client from discovery-call inputs. Outputs a readiness score (0–100), tier (Ready / Developing / Early Stage), and a list of specific gaps to address.

**Page 3 — Settlement Economics:** The CFO business case. Models USDC rail costs vs traditional correspondent banking across 5 global regions. Inputs: annual settlement volume, region, integration complexity. Outputs: annual savings, implementation cost, payback period, and a 5-year cumulative savings schedule.

**Page 4 — GTM Playbook & AI Pitch Generator:** The standout feature. Select any client and Claude AI generates a tailored 3-bullet pre-sales pitch based on their readiness tier, identified gaps, and savings potential — plus the top objection to anticipate. Below the pitch generator: a full client prioritization matrix (readiness vs. volume) with quadrant reference lines to identify highest-priority targets, and a tier-based GTM approach guide.

## JD Alignment

| Job Description Requirement | Project Feature |
|---|---|
| Work with clients on stablecoin strategy | Page 2 — Client Readiness Assessment |
| Support pre-sales preparation and sales materials | Page 4 — AI Pitch Generator |
| Help shape Go-To-Market strategy globally | Page 4 — Prioritization matrix + tier playbook |
| Subject matter expertise in stablecoins/blockchain | Pages 1 & 3 — USDC adoption data + settlement rail economics |
| Acumen with AI tooling for research and prototyping | Page 4 — Live Claude API integration |

## Key Insights

**Market:** Fintechs lead stablecoin adoption index globally (avg 85+) while MEA lags all regions at 28 — pointing to infrastructure gaps rather than product-market fit issues. North America leads USDC volume at $18.4B/month.

**Readiness:** Of 80 clients assessed, 22 are Ready (score 70+), 54 are Developing, and 4 are Early Stage. Banks score highest on compliance readiness; fintechs lead on technology readiness.

**Settlement economics:** MEA clients have the highest savings potential (30 bps spread vs traditional rails) but also the longest payback periods due to high integration complexity. North America clients break even fastest — ideal for early pilot programs.

**GTM priority:** Target Ready fintechs in North America and Europe first — highest readiness scores combined with large settlement volumes and shortest implementation timelines. MEA requires infrastructure investment before commercial engagement.

## Setup & Reproduction

**Requirements:** Python 3.10+

```bash
pip install streamlit altair pandas numpy anthropic pytest

# Generate datasets
cd streamlit_app
python generate_data.py

# Run the dashboard
streamlit run 1_market_landscape.py

# Run tests (from project root)
pytest
```

**API Key:** The GTM Pitch Generator requires an Anthropic API key. For local use, create `streamlit_app/.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

## Repository Structure

    .
    ├── streamlit_app/
    │   ├── 1_market_landscape.py          # Page 1: Market Landscape
    │   ├── pages/
    │   │   ├── 2_client_readiness.py      # Page 2: Client Readiness Assessment
    │   │   ├── 3_settlement_economics.py  # Page 3: Settlement Economics Model
    │   │   └── 4_gtm_playbook.py          # Page 4: GTM Playbook + AI Pitch Generator
    │   ├── utils/
    │   │   ├── data_loader.py             # Cached CSV loaders
    │   │   ├── readiness_score.py         # compute_readiness_score() pure function
    │   │   ├── settlement_model.py        # compute_settlement_economics() pure function
    │   │   └── gtm_pitch.py              # generate_gtm_pitch() — Claude API call
    │   ├── data/
    │   │   ├── market_landscape.csv       # 480 rows — monthly adoption by region/client type
    │   │   └── client_profiles.csv        # 80 rows — synthetic client profiles
    │   └── generate_data.py               # Synthetic data generator
    ├── tests/
    │   ├── test_readiness_score.py        # 12 unit tests
    │   └── test_settlement_model.py       # 11 unit tests
    ├── requirements.txt
    ├── pytest.ini
    └── README.md
