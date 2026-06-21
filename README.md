# Grattan Institute — AEMC Electricity Pricing Review
## Distributional analysis of rooftop solar and the renter gap

Analysis and interactive visualisations supporting Grattan Institute's submission to the AEMC Electricity Pricing Review (June 2026).

**Core argument:** The AEMC's distributional premise — that solar owners are wealthy and subsidised by poorer non-solar households — is not supported by postcode-level data. The access gap is a tenure gap, not an income gap.

---

## Files

| File | Description |
|------|-------------|
| `index.html` | Interactive postcode map (6.9MB, all data embedded) |
| `solutions.html` | Policy solutions document with evidence |
| `AEMC_claims_audit.md` | Fact-check of all claims and figures |
| `postcode_geo.geojson` | Postcode boundaries with solar data (7.8MB) |
| `data/output/master_postcode_enriched.csv` | Key derived dataset — all analysis starts here |
| `data/output/*.json` | Pre-computed chart data embedded in HTML files |
| `scripts/process.py` | Main data processing pipeline |
| `scripts/add_electoral.py` | Adds federal electorate to postcode data |

---

## Data sources

### Included in this repo
- **APVI postcode solar data** (`data/raw/apvi_postcodes.csv`) — cumulative installations by postcode, downloaded from [pvmap.apvi.org.au](https://pvmap.apvi.org.au)
- **CER solar installations** (`data/raw/cer_solar_installations.csv`) — Clean Energy Regulator small-scale technology certificates
- **CER battery installations** (`data/raw/cer_battery_installations.csv`) — Clean Energy Regulator

### Download separately (too large for GitHub)

**ABS 2021 Census — General Community Profile (GCP), Postal Area geography**
1. Go to [abs.gov.au/census/find-census-data/datapacks](https://www.abs.gov.au/census/find-census-data/datapacks)
2. Select: 2021 Census GCP | Geography: POA | Download all tables
3. Unzip to `data/raw/abs_census_poa/`
4. Key tables used: G02 (income), G36 (dwelling structure), G37 (tenure type)

**AEC electorate boundaries** (for `add_electoral.py`)
- Download from [aec.gov.au/Electorates/gis/gis_datadownload.htm](https://www.aec.gov.au/Electorates/gis/gis_datadownload.htm)
- Place `AUS_ELB_region.*` files in the repo root

---

## Replication

```bash
# Install dependencies
pip install pandas geopandas shapely

# Run main pipeline (requires ABS data downloaded as above)
python scripts/process.py

# Add electorate data (requires AEC shapefile downloaded as above)
python scripts/add_electoral.py
```

Outputs are written to `data/output/`. The HTML files embed the JSON outputs directly — copy the relevant JSON into the `<script>` blocks in `index.html` and `solutions.html` to update.

---

## Key findings

- **Tenure gap, not income gap:** Solar penetration is 20–28pp lower in high-renter postcodes than low-renter postcodes, *controlling for income*. High-income renter postcodes have lower solar uptake than low-income owner-occupier postcodes.
- **National scale:** ~1.42 million renter-occupied houses in Australia lack access to rooftop solar. 
- **Voluntary programs don't scale:** Solar Victoria's rental rebate has reached 1.4% of renter houses after 6 years; owner-occupier penetration exceeds 35% in the same period.
- **State variation:** Queensland has the largest absolute renter solar gap (18.2pp), affecting ~94,000 households.

---

## Contact

Grattan Institute Energy Program  
[grattan.edu.au](https://grattan.edu.au)
