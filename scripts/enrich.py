"""
enrich.py — Step 2 of 3 in the data pipeline
Joins ABS 2021 Census G36 (dwelling structure) and G37 (tenure type) onto
the master postcode table produced by process.py, creating master_postcode_enriched.csv.

Run AFTER process.py. Requires the ABS census data in data/raw/abs_census_poa/
(see README for download instructions).

Usage:
    python scripts/enrich.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA = Path("data/raw")
OUT  = Path("data/output")

# ── Load base master ────────────────────────────────────────────────────────
print("Loading master_postcode.csv...")
master = pd.read_csv(OUT / "master_postcode.csv", dtype={"postcode": str})
master["postcode"] = master["postcode"].str.zfill(4)
print(f"  {len(master):,} postcodes")

# ── STEP A: ABS G36 — Dwelling Structure ────────────────────────────────────
# Table G36: Occupied private dwellings by structure (separate house, semi, flat/apt)
print("\nSTEP A: ABS G36 — dwelling structure")
g36_path = list(DATA.glob("abs_census_poa/**/*G36*POA.csv"))[0]
g36 = pd.read_csv(g36_path)
g36["postcode"] = g36["POA_CODE_2021"].str.replace("POA", "").str.zfill(4)

dwelling = pd.DataFrame()
dwelling["postcode"]        = g36["postcode"]
dwelling["separate_house"]  = pd.to_numeric(g36["OPDs_Separate_house_Dwellings"],  errors="coerce").fillna(0)
dwelling["semi_detached"]   = pd.to_numeric(g36["OPDs_SD_r_t_h_th_Tot_Dwgs"],     errors="coerce").fillna(0)
dwelling["flat_apartment"]  = pd.to_numeric(g36["OPDs_Flt_apart_Tot_Dwgs"],        errors="coerce").fillna(0)
# NOTE: use Total_PDs_Dwellings (all private dwellings including unoccupied) as denominator,
# NOT OPDs_Tot_OPDs_Dwellings (occupied only). Using occupied-only inflates percentages in
# postcodes with high vacancy rates (e.g. holiday areas, remote communities).
dwelling["total_dwellings"] = pd.to_numeric(g36["Total_PDs_Dwellings"],            errors="coerce").fillna(0)

# Percentages (0–100 scale)
dwelling["pct_house"]     = np.where(
    dwelling["total_dwellings"] > 0,
    dwelling["separate_house"] / dwelling["total_dwellings"] * 100,
    np.nan
)
dwelling["pct_apartment"] = np.where(
    dwelling["total_dwellings"] > 0,
    dwelling["flat_apartment"] / dwelling["total_dwellings"] * 100,
    np.nan
)
print(f"  {len(dwelling):,} postcodes | pct_house range: {dwelling['pct_house'].min():.1f}–{dwelling['pct_house'].max():.1f}%")

# ── STEP B: ABS G37 — Tenure Type ───────────────────────────────────────────
# Table G37: Occupied private dwellings by tenure type × dwelling structure
# Key column mapping:
#   O_OR_Total    = owned outright (total)
#   O_MTG_Total   = owned with mortgage (total)
#   R_Tot_Total   = renting total (all landlord types combined)
#   Total_Total   = all tenures total
#   R_Tot_DS_Sep_house       = renters in separate houses specifically
#   O_OR_DS_Sep_house        = owned outright, separate house
#   O_MTG_DS_Sep_house       = owned with mortgage, separate house
print("\nSTEP B: ABS G37 — tenure type")
g37_path = list(DATA.glob("abs_census_poa/**/*G37*POA.csv"))[0]
g37 = pd.read_csv(g37_path)
g37["postcode"] = g37["POA_CODE_2021"].str.replace("POA", "").str.zfill(4)

tenure = pd.DataFrame()
tenure["postcode"]       = g37["postcode"]
tenure["owned_outright"] = pd.to_numeric(g37["O_OR_Total"],          errors="coerce").fillna(0)
tenure["owned_mortgage"] = pd.to_numeric(g37["O_MTG_Total"],         errors="coerce").fillna(0)
tenure["renting_total"]  = pd.to_numeric(g37["R_Tot_Total"],         errors="coerce").fillna(0)
tenure["total_tenure"]   = pd.to_numeric(g37["Total_Total"],         errors="coerce").fillna(0)

# Renters and owners specifically in separate houses (for solar access modelling)
# Renter-occupied separate houses = the population that COULD get solar if landlord installs
tenure["renter_house"]   = pd.to_numeric(g37["R_Tot_DS_Sep_house"],  errors="coerce").fillna(0)
# Owner-occupied separate houses = baseline solar-eligible population
tenure["owner_house"]    = (
    pd.to_numeric(g37["O_OR_DS_Sep_house"],  errors="coerce").fillna(0)
    + pd.to_numeric(g37["O_MTG_DS_Sep_house"], errors="coerce").fillna(0)
)

# Percentages (0–100 scale)
tenure["pct_owner"]  = np.where(
    tenure["total_tenure"] > 0,
    (tenure["owned_outright"] + tenure["owned_mortgage"]) / tenure["total_tenure"] * 100,
    np.nan
)
tenure["pct_renter"] = np.where(
    tenure["total_tenure"] > 0,
    tenure["renting_total"] / tenure["total_tenure"] * 100,
    np.nan
)
print(f"  {len(tenure):,} postcodes | pct_renter range: {tenure['pct_renter'].dropna().min():.1f}–{tenure['pct_renter'].dropna().max():.1f}%")
print(f"  total renter_house (sep. houses): {tenure['renter_house'].sum():,.0f}")

# ── STEP C: Join all onto master ────────────────────────────────────────────
print("\nSTEP C: Merging onto master...")
enriched = (master
    .merge(dwelling[["postcode","separate_house","semi_detached","flat_apartment",
                      "total_dwellings","pct_house","pct_apartment"]],
           on="postcode", how="left")
    .merge(tenure[["postcode","owned_outright","owned_mortgage","renting_total",
                   "total_tenure","pct_owner","pct_renter","renter_house","owner_house"]],
           on="postcode", how="left")
)

print(f"  {len(enriched):,} postcodes in enriched master")
print(f"  {enriched['pct_renter'].notna().sum():,} with tenure data")
print(f"  {enriched['pct_house'].notna().sum():,} with dwelling structure data")

enriched.to_csv(OUT / "master_postcode_enriched.csv", index=False)
print(f"\n✓ Saved data/output/master_postcode_enriched.csv")

# ── STEP D: State-level renter gap summary ──────────────────────────────────
# States derived from postcode ranges (standard Australian convention)
print("\nSTEP D: State renter gap summary")

def postcode_to_state(pc):
    pc = int(pc)
    if 1000 <= pc <= 2599 or 2619 <= pc <= 2899 or 2921 <= pc <= 2999: return "NSW"
    if 2600 <= pc <= 2618 or 2900 <= pc <= 2920:                        return "ACT"
    if 3000 <= pc <= 3999 or 8000 <= pc <= 8999:                        return "VIC"
    if 4000 <= pc <= 4999 or 9000 <= pc <= 9999:                        return "QLD"
    if 5000 <= pc <= 5799 or 5800 <= pc <= 5999:                        return "SA"
    if 6000 <= pc <= 6797 or 6800 <= pc <= 6999:                        return "WA"
    if 7000 <= pc <= 7799 or 7800 <= pc <= 7999:                        return "TAS"
    if 800  <= pc <= 899  or 900  <= pc <= 999:                         return "NT"
    return "OTHER"

enriched["state"] = enriched["postcode"].apply(postcode_to_state)

# Renter gap: compare solar penetration in low-renter vs high-renter postcodes by state
# Filter to: has tenure data, enough houses, not inf/nan
valid = enriched[
    enriched["pct_renter"].notna() &
    enriched["apvi_pct"].notna() &
    (enriched["estimated_houses"] >= 100) &
    (enriched["pct_renter"] < 100) &   # exclude bad data
    (enriched["pct_house"] <= 100) &   # exclude bad data
    enriched["state"].isin(["NSW","VIC","QLD","SA","WA","TAS","ACT","NT"])
].copy()

# Median split within each state
def state_gap(df):
    median_renter = df["pct_renter"].median()
    low  = df[df["pct_renter"] <= median_renter]
    high = df[df["pct_renter"] >  median_renter]

    def wavg_solar(g):
        return np.average(g["apvi_pct"], weights=g["estimated_houses"])

    return pd.Series({
        "low_renter_solar":  round(wavg_solar(low),  1),
        "high_renter_solar": round(wavg_solar(high), 1),
        "gap_pp":            round(wavg_solar(low) - wavg_solar(high), 1),
        "n_postcodes":       len(df),
        "median_pct_renter": round(median_renter, 1),
        "est_missing_solar": int(
            (wavg_solar(low) - wavg_solar(high)) / 100
            * high["renter_house"].sum()
        )
    })

gap_table = valid.groupby("state").apply(state_gap).reset_index()
gap_table["relative_gap_pct"] = (gap_table["gap_pp"] / gap_table["low_renter_solar"] * 100).round(0).astype(int)
gap_table = gap_table.sort_values("gap_pp", ascending=False)

print("\nState renter solar gap:")
print(gap_table[["state","low_renter_solar","high_renter_solar","gap_pp","relative_gap_pct","est_missing_solar"]].to_string(index=False))

gap_table.to_csv(OUT / "state_renter_gap.csv", index=False)
print("\n✓ Saved data/output/state_renter_gap.csv")
print("\n✓ All done.")
