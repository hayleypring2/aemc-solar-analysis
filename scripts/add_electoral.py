import geopandas as gpd
import pandas as pd
import numpy as np
import json, warnings
from pathlib import Path

OUT = Path('/sessions/determined-kind-newton/mnt/outputs/solar_project/output')

master = pd.read_csv(OUT / 'master_postcode.csv')
master['postcode'] = master['postcode'].astype(str).str.zfill(4)

# Use APVI snapshot % as solar penetration (covers more postcodes than CER totals)
# apvi_pct is already % of houses with solar
master['solar_pct_frac'] = master['apvi_pct'].fillna(0) / 100.0

pca_geo = gpd.read_file(OUT / 'postcode_geo.geojson')
pca_geo['postcode'] = pca_geo['postcode'].astype(str).str.zfill(4)

electorates = gpd.read_file('/sessions/determined-kind-newton/mnt/AUS-March-2025-esri/AUS_ELB_region.shp')
electorates = electorates.to_crs('EPSG:4326')

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    pca_centroids = pca_geo[['postcode','geometry']].copy()
    pca_centroids['geometry'] = pca_centroids.geometry.centroid

joined = gpd.sjoin(pca_centroids, electorates[['Elect_div','geometry']], 
                   how='left', predicate='within')
postcode_electorate = joined[['postcode','Elect_div']].rename(columns={'Elect_div':'electorate'})
master2 = master.merge(postcode_electorate, on='postcode', how='left')

def wagg(g):
    g = g[g['estimated_houses'].fillna(0) > 0]
    if len(g) == 0:
        return pd.Series()
    houses = g['estimated_houses']
    total_h = houses.sum()
    sol_frac = g['solar_pct_frac']  # APVI-based
    bat = g['total_battery_installs'].fillna(0)
    inc = g['median_hhd_income_weekly']
    dec = g['income_decile']
    # weighted average solar penetration
    sol_pen = sol_frac.mul(houses).sum() / total_h
    bat_pen = (bat / houses).mul(houses).sum() / total_h
    return pd.Series({
        'total_houses': int(total_h),
        'solar_penetration': float(sol_pen),
        'battery_penetration': float(bat_pen),
        'median_income_weekly': float(np.average(inc.fillna(0), weights=houses)) if inc.notna().any() else None,
        'avg_decile': float(np.average(dec.fillna(5), weights=houses)),
        'n_postcodes': int(len(g)),
    })

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    elec_agg = master2.dropna(subset=['electorate']).groupby('electorate').apply(wagg).reset_index()

elec_agg = elec_agg.dropna(subset=['total_houses'])
elec_agg['solar_pct'] = (elec_agg['solar_penetration'] * 100).round(1)
elec_agg['battery_pct'] = (elec_agg['battery_penetration'] * 100).round(2)
elec_agg['income_annual'] = (elec_agg['median_income_weekly'].fillna(0) * 52).round(0).astype(int)
elec_agg = elec_agg.sort_values('solar_pct', ascending=False)

print(f"{len(elec_agg)} electorates\n")
print("TOP 20 by solar penetration:")
print(elec_agg[['electorate','solar_pct','battery_pct','income_annual','avg_decile']].head(20).to_string(index=False))
print("\nBOTTOM 10:")
print(elec_agg[['electorate','solar_pct','battery_pct','income_annual','avg_decile']].tail(10).to_string(index=False))

# Check any still-zero
zeros = elec_agg[elec_agg['solar_pct'] == 0]
print(f"\nZero-solar electorates: {len(zeros)}")

out_records = elec_agg[['electorate','total_houses','solar_pct','battery_pct',
                          'income_annual','avg_decile','n_postcodes']].to_dict(orient='records')
with open(OUT / 'electorate_summary.json', 'w') as f:
    json.dump(out_records, f, indent=2)
print(f"\nSaved {len(out_records)} electorates to electorate_summary.json")
