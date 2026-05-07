import pandas as pd
import numpy as np
import os

rng = np.random.default_rng(42)

REGIONS = ["North America", "Europe", "Asia Pacific", "LAC", "MEA"]
CLIENT_TYPES = ["Bank", "Fintech", "Merchant", "Enabler"]
MONTHS = pd.date_range("2024-01-01", "2025-12-01", freq="MS")

# ── Dataset 1: market_landscape.csv ──────────────────────────────────────────
# Adoption index and USDC volume by region/client_type/month

BASE_ADOPTION = {
    "North America": 62, "Europe": 54, "Asia Pacific": 48, "LAC": 35, "MEA": 28
}
BASE_VOLUME = {
    "North America": 18.4, "Europe": 12.1, "Asia Pacific": 9.7, "LAC": 4.2, "MEA": 2.8
}
CLIENT_MULTIPLIER = {"Bank": 1.3, "Fintech": 1.5, "Merchant": 0.9, "Enabler": 1.1}

rows = []
for month in MONTHS:
    t = (month.year - 2024) * 12 + month.month - 1
    growth = 1 + t * 0.008
    for region in REGIONS:
        for client_type in CLIENT_TYPES:
            adoption = min(
                100,
                BASE_ADOPTION[region] * CLIENT_MULTIPLIER[client_type] * growth
                + rng.normal(0, 2),
            )
            volume = (
                BASE_VOLUME[region] * CLIENT_MULTIPLIER[client_type] * growth
                + rng.normal(0, 0.3)
            )
            rows.append(
                {
                    "month": month.strftime("%Y-%m-%d"),
                    "region": region,
                    "client_type": client_type,
                    "adoption_index": round(float(adoption), 1),
                    "usdc_volume_bn": round(float(max(0.1, volume)), 2),
                    "live_partners": max(
                        1,
                        int(
                            BASE_ADOPTION[region] / 10 * CLIENT_MULTIPLIER[client_type]
                            + t * 0.15
                            + rng.integers(-1, 2)
                        ),
                    ),
                    "yoy_growth_pct": round(float(rng.uniform(8, 35)), 1),
                }
            )

market_df = pd.DataFrame(rows)

# ── Dataset 2: client_profiles.csv ───────────────────────────────────────────
# One row per synthetic client — used for readiness assessment

BANK_NAMES = [
    "First National Bank", "Pacific Commerce Bank", "Summit Financial",
    "Atlas Bank", "Meridian Trust", "Apex Bank", "Harbor Financial",
    "Crestview Bank", "Pinnacle National", "Sterling Bank",
    "Nova Bank", "Cascade Financial", "Ironclad Bank", "Solaris Trust",
    "Keystone Bank", "Glacier Bank", "Horizon National", "Cobalt Financial",
    "Ember Bank", "Prism Trust",
]
FINTECH_NAMES = [
    "PaySwift", "NovaPay", "FluxFinance", "ArcPay", "ZenithWallet",
    "ClearStream", "Orbit Payments", "Nexus Pay", "Pulse Finance", "Axiom Pay",
    "Luminary Payments", "Catalyst Finance", "Vertex Pay", "Echo Payments",
    "Quantum Wallet", "Beacon Finance", "Prism Pay", "Stellar Payments",
    "Forge Finance", "Summit Pay",
]
MERCHANT_NAMES = [
    "NovaMart", "Apex Digital", "TechDirect", "GlobalShop", "SwiftRetail",
    "PrimeCommerce", "EclipseStore", "Horizon Retail", "Solaris Shop",
    "Crestview Commerce", "Nexus Retail", "Atlas Store", "Luminary Market",
    "Cascade Commerce", "Ironclad Retail", "Zenith Market", "Forge Store",
    "Cobalt Commerce", "Ember Retail", "Beacon Market",
]
ENABLER_NAMES = [
    "ChainBridge", "RailForge", "SettleCore", "ConnectRails", "NexusGateway",
    "PrismBridge", "OrbitalSettlement", "ClearRails", "VertexGateway",
    "ApexBridge", "LuminaryRails", "CatalystGateway", "ForgeConnect",
    "ZenithBridge", "BeaconRails", "EchoGateway", "SolarisConnect",
    "IroncladBridge", "CascadeRails", "HorizonGateway",
]

NAMES = {
    "Bank": BANK_NAMES, "Fintech": FINTECH_NAMES,
    "Merchant": MERCHANT_NAMES, "Enabler": ENABLER_NAMES,
}

SETTLEMENT_METHODS = ["Traditional", "Partial Crypto", "Exploring"]
COMPLEXITY = ["Low", "Medium", "High"]

TECH_BASE = {"Bank": 55, "Fintech": 78, "Merchant": 48, "Enabler": 70}
COMPLIANCE_BASE = {"Bank": 72, "Fintech": 58, "Merchant": 50, "Enabler": 60}
VOLUME_BASE = {
    "Bank": (5, 80), "Fintech": (0.5, 15),
    "Merchant": (1, 40), "Enabler": (2, 25),
}

client_rows = []
for client_type, names in NAMES.items():
    for name in names:
        region = rng.choice(REGIONS)
        tech = min(100, max(10, TECH_BASE[client_type] + rng.normal(0, 12)))
        compliance = min(100, max(10, COMPLIANCE_BASE[client_type] + rng.normal(0, 10)))
        vol_min, vol_max = VOLUME_BASE[client_type]
        volume = round(float(rng.uniform(vol_min, vol_max)), 1)
        complexity = rng.choice(COMPLEXITY, p=[0.3, 0.45, 0.25])
        settlement = rng.choice(SETTLEMENT_METHODS, p=[0.5, 0.3, 0.2])
        ttl = int(rng.integers(3, 24))
        client_rows.append(
            {
                "client_name": name,
                "client_type": client_type,
                "region": region,
                "current_settlement": settlement,
                "annual_volume_bn": volume,
                "tech_readiness": round(float(tech), 1),
                "compliance_readiness": round(float(compliance), 1),
                "integration_complexity": complexity,
                "time_to_live_months": ttl,
            }
        )

client_df = pd.DataFrame(client_rows)

# ── Write ─────────────────────────────────────────────────────────────────────
out_dir = os.path.join(os.path.dirname(__file__), "data")
market_df.to_csv(os.path.join(out_dir, "market_landscape.csv"), index=False)
client_df.to_csv(os.path.join(out_dir, "client_profiles.csv"), index=False)
print(f"market_landscape.csv  : {len(market_df)} rows")
print(f"client_profiles.csv   : {len(client_df)} rows")
