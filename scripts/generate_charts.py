"""
generate_charts.py — Step 3 of 3 in the data pipeline
Produces all JSON chart data files used by index.html and solutions.html.

Run AFTER process.py and enrich.py. Reads master_postcode_enriched.csv
and electorate_summary.json from data/output/.

Usage:
    python scripts/generate_charts.py

Outputs (all to data/output/):
    dwelling_chart_data.json   — dwelling type × income decile chart
    state_breakdown.json       — state-level solar/battery/income summary
    solutions_data.json        — renter gap analysis (solar_gap, state_data, decile_data, national)
    marginal_seats.json        — marginal seat solar/income analysis
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

OUT = Path("data/output")

# ── Load enriched master ────────────────────────────────────────────────────
print("Loading master_postcode_enriched.csv...")
df = pd.read_csv(OUT / "master_postcode_enriched.csv", dtype={"postcode": str})
df["postcode"] = df["postcode"].str.zfill(4)

# State from postcode ranges
def to_state(pc):
    pc = int(pc)
    if 1000 <= pc <= 2599 or 2619 <= pc <= 2899 or 2921 <= pc <= 2999: return "NSW"
    if 2600 <= pc <= 2618 or 2900 <= pc <= 2920:                        return "ACT"
    if 3000 <= pc <= 3999 or 8000 <= pc <= 8999:                        return "VIC"
    if 4000 <= pc <= 4999 or 9000 <= pc <= 9999:                        return "QLD"
    if 5000 <= pc <= 5999:                                               return "SA"
    if 6000 <= pc <= 6999:                                               return "WA"
    if 7000 <= pc <= 7999:                                               return "TAS"
    if 800  <= pc <= 999:                                                return "NT"
    return "OTHER"

df["state"] = df["postcode"].apply(to_state)

# Common filter: valid data for income decile analysis
valid = df[
    df["income_decile"].notna() &
    df["pct_renter"].notna() &
    df["apvi_pct"].notna() &
    (df["estimated_houses"] >= 100) &
    (df["pct_renter"] < 100) &      # exclude data errors
    (df["pct_house"] <= 100) &      # exclude data errors
    (df["apvi_pct"] > 0)
].copy()
print(f"  {len(valid):,} valid postcodes for analysis")

def wavg(series, weights):
    """Weighted average."""
    return float(np.average(series, weights=weights))

# ── 1. dwelling_chart_data.json ─────────────────────────────────────────────
# Three series by income decile:
#   dwell_data:   weighted avg pct_house, pct_apartment, pct_renter
#   solar_full:   avg solar penetration (apvi_pct) — all postcodes
#   solar_house:  avg solar penetration — house-dominant postcodes (pct_house > 70)
#   solar_mixed:  avg solar penetration — mixed-dwelling postcodes (30 < pct_house <= 70)
print("\n1. dwelling_chart_data.json")

dwell_data, solar_full, solar_house, solar_mixed = [], {}, {}, {}

for dec in sorted(valid["income_decile"].unique()):
    sub  = valid[valid["income_decile"] == dec]
    d    = int(dec)
    w    = sub["estimated_houses"]

    dwell_data.append({
        "income_decile": d,
        "pct_house": round(wavg(sub["pct_house"],     w), 1),
        "pct_apt":   round(wavg(sub["pct_apartment"], w), 1),
        "pct_renter":round(wavg(sub["pct_renter"],    w), 1),
    })
    solar_full[str(d)] = round(wavg(sub["apvi_pct"], w), 1)

    # House-dominant postcodes: pct_house > 70
    h = sub[sub["pct_house"] > 70]
    solar_house[str(d)] = round(wavg(h["apvi_pct"], h["estimated_houses"]), 1) if len(h) >= 3 else None

    # Mixed-dwelling postcodes: 30 < pct_house <= 70
    m = sub[(sub["pct_house"] > 30) & (sub["pct_house"] <= 70)]
    solar_mixed[str(d)] = round(wavg(m["apvi_pct"], m["estimated_houses"]), 1) if len(m) >= 3 else None

out = {"dwell_data": dwell_data, "solar_full": solar_full,
       "solar_house": solar_house, "solar_mixed": solar_mixed}
with open(OUT / "dwelling_chart_data.json", "w") as f:
    json.dump(out, f)
print("  Saved dwelling_chart_data.json")

# ── 2. state_breakdown.json ─────────────────────────────────────────────────
# State-level weighted averages of solar and battery penetration, and median income
print("\n2. state_breakdown.json")

state_valid = df[
    df["apvi_pct"].notna() &
    df["battery_per_house"].notna() &
    df["median_hhd_income_annual"].notna() &
    (df["estimated_houses"] > 0) &
    (df["state"] != "OTHER")
].copy()

state_rows = []
for state in ["SA", "QLD", "WA", "ACT", "NSW", "VIC", "NT", "TAS"]:
    sub = state_valid[state_valid["state"] == state]
    if len(sub) == 0:
        continue
    state_rows.append({
        "state":         state,
        "solar_pct":     wavg(sub["apvi_pct"],          sub["estimated_houses"]),
        "battery_pct":   wavg(sub["battery_per_house"],  sub["estimated_houses"]) * 100,
        "median_income": float(sub["median_hhd_income_annual"].median()),
        "total_houses":  float(sub["estimated_houses"].sum()),
        "n_postcodes":   float(len(sub)),
    })

# Sort by solar_pct descending
state_rows.sort(key=lambda x: -x["solar_pct"])
with open(OUT / "state_breakdown.json", "w") as f:
    json.dump(state_rows, f, indent=2)
print("  Saved state_breakdown.json")

# ── 3. solutions_data.json ──────────────────────────────────────────────────
# Comprehensive dataset for solutions.html:
#   solar_gap:  owner-like vs renter-heavy solar penetration by income decile
#   state_data: per-state renter/owner house counts + solar
#   decile_data: per-decile dwelling/tenure/solar summary
#   national:   aggregate totals
print("\n3. solutions_data.json")

# 3a. solar_gap — within each income decile, house-heavy postcodes split by renter share:
#   owner_like   = pct_house > 60 AND pct_renter < 20
#   renter_heavy = pct_house > 60 AND pct_renter > 35
solar_gap = []
for dec in sorted(valid["income_decile"].unique()):
    sub   = valid[(valid["income_decile"] == dec) & (valid["pct_house"] > 60)]
    owner = sub[sub["pct_renter"] < 20]
    rente = sub[sub["pct_renter"] > 35]
    if len(owner) < 3 or len(rente) < 3:
        continue
    ol = round(wavg(owner["apvi_pct"], owner["estimated_houses"]), 1)
    rh = round(wavg(rente["apvi_pct"], rente["estimated_houses"]), 1)
    solar_gap.append({
        "decile":       int(dec),
        "owner_like":   ol,
        "renter_heavy": rh,
        "gap":          round(ol - rh, 1),
    })

# 3b. state_data — renter/owner house counts + solar + apartments
state_data = []
state_enrich = df[
    df["renter_house"].notna() &
    df["owner_house"].notna() &
    df["apvi_pct"].notna() &
    (df["state"] != "OTHER")
].copy()

for state in ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "ACT", "NT"]:
    sub = state_enrich[state_enrich["state"] == state]
    if len(sub) == 0:
        continue
    total_houses   = int(sub["estimated_houses"].sum())
    renter_houses  = int(sub["renter_house"].sum())
    owner_houses   = int(sub["owner_house"].sum())
    # Estimated solar houses: apvi_pct × estimated_houses
    solar_houses   = int((sub["apvi_pct"] / 100 * sub["estimated_houses"]).sum())
    apartments     = int(sub["flat_apartment"].sum()) if "flat_apartment" in sub.columns else 0
    total_renters  = int(sub["renting_total"].sum()) if "renting_total" in sub.columns else 0
    solar_pct      = round(wavg(sub["apvi_pct"], sub["estimated_houses"]), 1)

    state_data.append({
        "state":         state,
        "renter_houses": renter_houses,
        "owner_houses":  owner_houses,
        "solar_houses":  solar_houses,
        "total_houses":  total_houses,
        "apartments":    apartments,
        "total_renters": total_renters,
        "solar_pct":     solar_pct,
    })

# 3c. decile_data — per decile summary
decile_data = []
for dec in sorted(valid["income_decile"].unique()):
    sub = valid[valid["income_decile"] == dec]
    d   = int(dec)
    w   = sub["estimated_houses"]
    decile_data.append({
        "decile":          d,
        "income_annual":   int(sub["median_hhd_income_annual"].median()),
        "solar_pct":       round(wavg(sub["apvi_pct"],        w), 1),
        "pct_apartment":   round(wavg(sub["pct_apartment"],   w), 1),
        "pct_house":       round(wavg(sub["pct_house"],       w), 1),
        "pct_renter":      round(wavg(sub["pct_renter"],      w), 1),
        "renter_houses":   int(sub["renter_house"].sum()),
        "owner_houses":    int(sub["owner_house"].sum()),
        "apartments":      int(sub["flat_apartment"].sum()),
        "total_dwellings": int(sub["total_dwellings"].sum()),
    })

# 3d. national aggregates
nat_valid = df[df["estimated_houses"] > 0]
total_renter_houses  = int(df["renter_house"].sum())
total_solar_houses   = int((df["apvi_pct"].fillna(0) / 100 * df["estimated_houses"].fillna(0)).sum())
total_est_houses     = int(df["estimated_houses"].sum())
total_apartments     = int(df["flat_apartment"].fillna(0).sum())

national = {
    "total_renter_houses":    total_renter_houses,
    "total_solar_houses":     total_solar_houses,
    "total_estimated_houses": total_est_houses,
    "total_apartments":       total_apartments,
    "community_solar_30pct":  int(total_renter_houses * 0.30),
    "community_solar_50pct":  int(total_renter_houses * 0.50),
}

solutions_out = {
    "solar_gap":   solar_gap,
    "state_data":  state_data,
    "decile_data": decile_data,
    "national":    national,
}
with open(OUT / "solutions_data.json", "w") as f:
    json.dump(solutions_out, f, indent=2)
print("  Saved solutions_data.json")

# ── 4. marginal_seats.json ──────────────────────────────────────────────────
# Electoral margin data sourced from AEC 2025 election results.
# Solar/income data joined from electorate_summary.json.
# Seats with margin <= 6pp included.
print("\n4. marginal_seats.json")

ELECTORAL_DATA = {
    # ALP seats
    "Bennelong":  {"margin": 0.04,  "held_by": "ALP", "likely_change": False},
    "Gilmore":    {"margin": 0.17,  "held_by": "ALP", "likely_change": False},
    "Lyons":      {"margin": 0.92,  "held_by": "ALP", "likely_change": False},
    "Lingiari":   {"margin": 1.60,  "held_by": "ALP", "likely_change": False},
    "Robertson":  {"margin": 2.23,  "held_by": "ALP", "likely_change": False},
    "Paterson":   {"margin": 2.60,  "held_by": "ALP", "likely_change": False},
    "Tangney":    {"margin": 2.85,  "held_by": "ALP", "likely_change": False},
    "Boothby":    {"margin": 3.28,  "held_by": "ALP", "likely_change": False},
    "Chisholm":   {"margin": 3.33,  "held_by": "ALP", "likely_change": False},
    "Bullwinkel": {"margin": 3.35,  "held_by": "ALP", "likely_change": False},
    "Parramatta": {"margin": 3.72,  "held_by": "ALP", "likely_change": False},
    "McEwen":     {"margin": 3.82,  "held_by": "ALP", "likely_change": False},
    "Hunter":     {"margin": 4.78,  "held_by": "ALP", "likely_change": False},
    "Reid":       {"margin": 5.19,  "held_by": "ALP", "likely_change": False},
    "Blair":      {"margin": 5.23,  "held_by": "ALP", "likely_change": False},
    "Bruce":      {"margin": 5.31,  "held_by": "ALP", "likely_change": False},
    "Werriwa":    {"margin": 5.34,  "held_by": "ALP", "likely_change": False},
    # LIB seats
    "Menzies":    {"margin": 0.42,  "held_by": "LIB", "likely_change": True},
    "Deakin":     {"margin": 0.02,  "held_by": "LIB", "likely_change": True},
    "Sturt":      {"margin": 0.45,  "held_by": "LIB", "likely_change": True},
    "Moore":      {"margin": 0.91,  "held_by": "LIB", "likely_change": True},
    "Canning":    {"margin": 1.20,  "held_by": "LIB", "likely_change": False},
    "Casey":      {"margin": 1.43,  "held_by": "LIB", "likely_change": False},
    "Bass":       {"margin": 1.43,  "held_by": "LIB", "likely_change": True},
    "Aston":      {"margin": 2.61,  "held_by": "LIB", "likely_change": True},
    "Banks":      {"margin": 2.64,  "held_by": "LIB", "likely_change": True},
    "Monash":     {"margin": 2.90,  "held_by": "LIB", "likely_change": False},
    "Bradfield":  {"margin": 3.40,  "held_by": "LIB", "likely_change": True},
    "Hughes":     {"margin": 3.46,  "held_by": "LIB", "likely_change": True},
    "Wannon":     {"margin": 3.50,  "held_by": "LIB", "likely_change": False},
    "Forrest":    {"margin": 4.19,  "held_by": "LIB", "likely_change": False},
    "Durack":     {"margin": 4.66,  "held_by": "LIB", "likely_change": False},
    # LNP seats
    "Dickson":    {"margin": 1.70,  "held_by": "LNP", "likely_change": True},
    "Longman":    {"margin": 3.08,  "held_by": "LNP", "likely_change": True},
    "Bonner":     {"margin": 3.41,  "held_by": "LNP", "likely_change": True},
    "Leichhardt": {"margin": 3.44,  "held_by": "LNP", "likely_change": True},
    "Flynn":      {"margin": 3.82,  "held_by": "LNP", "likely_change": False},
    "Forde":      {"margin": 4.23,  "held_by": "LNP", "likely_change": True},
    "Petrie":     {"margin": 4.44,  "held_by": "LNP", "likely_change": True},
    "Bowman":     {"margin": 5.51,  "held_by": "LNP", "likely_change": False},
    # Other
    "Cowper":     {"margin": 2.40,  "held_by": "NAT", "likely_change": False},
    "Ryan":       {"margin": 2.65,  "held_by": "GRN", "likely_change": False},
    "Melbourne":  {"margin": 5.58,  "held_by": "GRN", "likely_change": True},
}

elec_summary = json.load(open(OUT / "electorate_summary.json"))
elec_lookup = {r["electorate"]: r for r in elec_summary}

marginal_seats = []
for electorate, elec_data in ELECTORAL_DATA.items():
    if electorate not in elec_lookup:
        print(f"  WARNING: {electorate} not in electorate_summary.json")
        continue
    summ = elec_lookup[electorate]
    marginal_seats.append({
        "electorate":   electorate,
        "margin":       elec_data["margin"],
        "held_by":      elec_data["held_by"],
        "likely_change":elec_data["likely_change"],
        "state":        summ.get("state", to_state(electorate)),
        "solar_pct":    summ["solar_pct"],
        "income_annual":summ["income_annual"],
        "avg_decile":   summ["avg_decile"],
    })

# Sort by margin
marginal_seats.sort(key=lambda x: x["margin"])

with open(OUT / "marginal_seats.json", "w") as f:
    json.dump(marginal_seats, f, indent=2)
print(f"  Saved marginal_seats.json ({len(marginal_seats)} seats)")

print("\n✓ All chart data generated.")
