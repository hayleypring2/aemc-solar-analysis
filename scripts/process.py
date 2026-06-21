import pandas as pd
import numpy as np
import geopandas as gpd
import json, os
from pathlib import Path

DATA = Path("data")
OUT  = Path("output")
OUT.mkdir(exist_ok=True)

# ── STEP 1: CER solar → annual cumulative by postcode ──────────────────────
print("STEP 1: CER solar → annual")
solar_raw = pd.read_csv(DATA/"cer_solar_installations.csv", dtype={"Small Unit Installation Postcode":str})
solar_raw.rename(columns={"Small Unit Installation Postcode":"postcode"}, inplace=True)
solar_raw["postcode"] = solar_raw["postcode"].str.zfill(4)

monthly_cols = [c for c in solar_raw.columns if "Installation Quantity" in c
                and c not in ["Historic Total Installation Quantity (2001 - 2010)","Total Installation Quantity"]]

# melt to long, coerce installs to int immediately
solar_long = solar_raw[["postcode"]+monthly_cols].melt(id_vars="postcode", var_name="month_col", value_name="installs")
solar_long["installs"] = pd.to_numeric(solar_long["installs"], errors="coerce").fillna(0).astype(int)
solar_long["year"] = solar_long["month_col"].str.extract(r"(\d{4})").astype(int)
solar_annual = solar_long.groupby(["postcode","year"])["installs"].sum().reset_index()

# add pre-2011 historic lump
hist = solar_raw[["postcode","Historic Total Installation Quantity (2001 - 2010)"]].copy()
hist["installs"] = pd.to_numeric(hist["Historic Total Installation Quantity (2001 - 2010)"], errors="coerce").fillna(0).astype(int)
hist["year"] = 2010
solar_annual = pd.concat([hist[["postcode","year","installs"]], solar_annual], ignore_index=True)
solar_annual = solar_annual.sort_values(["postcode","year"]).reset_index(drop=True)
solar_annual["cumulative_solar"] = solar_annual.groupby("postcode")["installs"].cumsum()
print(f"  {len(solar_annual):,} rows | years {solar_annual.year.min()}–{solar_annual.year.max()}")

# ── STEP 2: Battery ────────────────────────────────────────────────────────
print("STEP 2: Battery")
bat = pd.read_csv(DATA/"cer_battery_installations.csv", dtype={"Small unit postcode":str})
bat.rename(columns={"Small unit postcode":"postcode"}, inplace=True)
bat["postcode"] = bat["postcode"].str.zfill(4)
bat["total_battery_installs"] = pd.to_numeric(bat["Total Installation Quantity"], errors="coerce").fillna(0).astype(int)
bat = bat[["postcode","total_battery_installs"]]
print(f"  {len(bat):,} postcodes | {bat.total_battery_installs.sum():,} total batteries")

# ── STEP 3: ABS income ─────────────────────────────────────────────────────
print("STEP 3: ABS income")
g02 = list(DATA.glob("abs_census_poa/**/*G02*POA.csv"))[0]
inc = pd.read_csv(g02)
inc["postcode"] = inc["POA_CODE_2021"].str.replace("POA","").str.zfill(4)
inc["median_hhd_income_weekly"]  = pd.to_numeric(inc["Median_tot_hhd_inc_weekly"], errors="coerce")
inc["median_hhd_income_annual"]  = inc["median_hhd_income_weekly"] * 52
inc = inc[["postcode","median_hhd_income_weekly","median_hhd_income_annual"]]
print(f"  {len(inc):,} postcodes | income ${inc.median_hhd_income_weekly.min():.0f}–${inc.median_hhd_income_weekly.max():.0f}/wk")

# ── STEP 4: APVI snapshot ──────────────────────────────────────────────────
print("STEP 4: APVI")
apvi = pd.read_csv(DATA/"apvi_postcodes.csv", dtype={"postcode":str})
apvi["postcode"] = apvi["postcode"].str.zfill(4)
apvi["estimated_houses"] = pd.to_numeric(apvi["estimated_houses"], errors="coerce")
apvi["apvi_pct"] = pd.to_numeric(apvi["density"], errors="coerce")   # % of houses with solar
apvi["apvi_res_installs"] = pd.to_numeric(apvi["installs_Residential"], errors="coerce")
apvi["apvi_res_capacity_kw"] = pd.to_numeric(apvi["capacity_Residential"], errors="coerce")
apvi = apvi[["postcode","estimated_houses","apvi_pct","apvi_res_installs","apvi_res_capacity_kw"]]
print(f"  {len(apvi):,} postcodes | {apvi.apvi_pct.notna().sum():,} with penetration rate")

# ── STEP 5: Master postcode table ──────────────────────────────────────────
print("STEP 5: Master join")
cer_tot = solar_raw[["postcode","Total Installation Quantity"]].copy()
cer_tot["cer_total_solar"] = pd.to_numeric(cer_tot["Total Installation Quantity"], errors="coerce").fillna(0).astype(int)
cer_tot = cer_tot[["postcode","cer_total_solar"]]

master = (apvi
    .merge(inc,     on="postcode", how="left")
    .merge(cer_tot, on="postcode", how="left")
    .merge(bat,     on="postcode", how="left")
)
master["total_battery_installs"] = master["total_battery_installs"].fillna(0).astype(int)
master["cer_total_solar"]        = master["cer_total_solar"].fillna(0).astype(int)

master["solar_per_house"]   = np.where(master["estimated_houses"]>0, master["cer_total_solar"]/master["estimated_houses"], np.nan)
master["battery_per_house"] = np.where(master["estimated_houses"]>0, master["total_battery_installs"]/master["estimated_houses"], np.nan)
master["battery_per_solar"] = np.where(master["cer_total_solar"]>0,  master["total_battery_installs"]/master["cer_total_solar"], np.nan)

eligible = master["median_hhd_income_weekly"].notna() & (master["estimated_houses"]>100)
master.loc[eligible,"income_decile"] = pd.qcut(
    master.loc[eligible,"median_hhd_income_weekly"], q=10, labels=range(1,11)).astype(float)

print(f"  {len(master):,} postcodes | {master.income_decile.notna().sum():,} with decile")
master.to_csv(OUT/"master_postcode.csv", index=False)

# ── STEP 6: Annual series ──────────────────────────────────────────────────
print("STEP 6: Annual time series")
annual = solar_annual.merge(
    master[["postcode","estimated_houses","median_hhd_income_weekly","median_hhd_income_annual","income_decile"]],
    on="postcode", how="left"
)
annual["penetration"] = np.where(annual["estimated_houses"]>0, annual["cumulative_solar"]/annual["estimated_houses"], np.nan)
annual.to_csv(OUT/"annual_by_postcode.csv", index=False)
print(f"  {len(annual):,} rows saved")

# ── STEP 7: Income-decile trajectories ────────────────────────────────────
print("STEP 7: Decile trajectories")
va = annual[annual["income_decile"].notna() & (annual["estimated_houses"]>50) & annual["penetration"].notna()].copy()

def wavg(g):
    return pd.Series({
        "avg_penetration": np.average(g["penetration"], weights=g["estimated_houses"]),
        "total_installs":  int(g["installs"].sum()),
        "total_houses":    int(g["estimated_houses"].sum()),
        "n_postcodes":     len(g)
    })

dec_ts = va.groupby(["income_decile","year"]).apply(wavg).reset_index()

ts_json = {}
for dec in sorted(dec_ts["income_decile"].unique()):
    d = dec_ts[dec_ts["income_decile"]==dec].sort_values("year")
    ts_json[int(dec)] = {
        "years":       d["year"].tolist(),
        "penetration": [round(float(v),4) for v in d["avg_penetration"]],
        "total_installs": d["total_installs"].tolist()
    }
with open(OUT/"decile_time_series.json","w") as f:
    json.dump(ts_json, f)

# Battery vs solar by decile
def bat_wavg(g):
    return pd.Series({
        "solar_penetration":   float(np.average(g["solar_per_house"].fillna(0),   weights=g["estimated_houses"])),
        "battery_penetration": float(np.average(g["battery_per_house"].fillna(0), weights=g["estimated_houses"])),
        "battery_per_solar_pct": float(np.average(g["battery_per_solar"].fillna(0), weights=g["estimated_houses"]))*100,
        "n_postcodes":         int(len(g)),
        "total_houses":        int(g["estimated_houses"].sum()),
        "median_income_weekly":float(g["median_hhd_income_weekly"].median())
    })

bat_dec = master[master["income_decile"].notna() & (master["estimated_houses"]>50)].groupby("income_decile").apply(bat_wavg).reset_index()
print("\n  Battery vs Solar penetration by income decile:")
print(bat_dec[["income_decile","median_income_weekly","solar_penetration","battery_penetration","battery_per_solar_pct"]].to_string(index=False))

with open(OUT/"battery_by_decile.json","w") as f:
    json.dump(bat_dec.to_dict(orient="records"), f, default=float)
print("\n  Saved decile_time_series.json + battery_by_decile.json")

# ── STEP 8: GeoJSON for choropleth ────────────────────────────────────────
print("\nSTEP 8: Build GeoJSON")
poa = gpd.read_file(DATA/"abs_poa_shp").to_crs(epsg=4326)
poa["postcode"] = poa["POA_CODE21"].str.zfill(4)

geo = poa.merge(master[["postcode","estimated_houses","apvi_pct","solar_per_house","battery_per_house",
                         "battery_per_solar","median_hhd_income_weekly","income_decile",
                         "cer_total_solar","total_battery_installs"]], on="postcode", how="left")

print("  Simplifying geometries...")
geo["geometry"] = geo["geometry"].simplify(tolerance=0.005, preserve_topology=True)

gf = geo[geo["median_hhd_income_weekly"].notna()].copy()
for c in ["apvi_pct","solar_per_house","battery_per_house","battery_per_solar","median_hhd_income_weekly"]:
    gf[c] = gf[c].round(3)

gf[["postcode","estimated_houses","apvi_pct","solar_per_house","battery_per_house",
    "battery_per_solar","median_hhd_income_weekly","income_decile",
    "cer_total_solar","total_battery_installs","geometry"]].to_file(OUT/"postcode_geo.geojson", driver="GeoJSON")

sz = os.path.getsize(OUT/"postcode_geo.geojson")/1e6
print(f"  Saved postcode_geo.geojson ({sz:.1f} MB)")

print("\n✓ All done — outputs in ./output/")
