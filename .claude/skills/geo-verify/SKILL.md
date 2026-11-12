---
name: geo-verify
description: Standing method for geospatial verification and estimation: using open satellite imagery, built-up and building layers, population grids and night-lights as a second, independent line of evidence to verify locations (stations, seats, Landbridge stops) and to estimate missing or secondary quantities (population, built-up area, distances) with two methods, an uncertainty band, a back-test gate and a strict Google Maps visual-only rule. Use in every region sweep, whenever a primary figure is missing or conflicting, and before any location enters a register.
---
> **Document version:** skills/geo-verify/SKILL.md v1.2 | 31 Oct 2026 | Author: coordinator, from Tariq's standing method of 31 Oct 2026; footprint licence corrected by INTEGRATE_R1; §3 UTM rule by CP2_PREP | Status: active

# Geospatial verification and estimation (`screening/geo_verify/`)

**Goal.** Use satellite imagery and geometry to verify locations and to estimate missing quantities (population, built-up area, station sites, distances) wherever primary data is missing or conflicting, as a **second, independent line of evidence**. It never replaces an official figure; it sits beside it.

## 1. Sources (open first; log every one in the licence register and the manifest)
- **Imagery:** Copernicus Sentinel-2 (10 m, Copernicus free licence with attribution), Landsat (USGS, public domain), and ESRI/Maxar basemaps only where their terms allow the use (read the terms; record the row; default: not used).
- **Built-up and buildings:** GHSL GHS-BUILT-S and GHS-POP (JRC, CC BY 4.0), Microsoft Global ML Building Footprints (CDLA-Permissive-2.0, corrected at INTEGRATE_R1 after the GEO_VERIFY verifier F1), OSM buildings (ODbL).
- **Population grids:** WorldPop (CC BY 4.0), GHS-POP (CC BY 4.0), Meta HRSL where it covers KSA (CC BY 4.0; check coverage first).
- **Activity:** VIIRS night-lights (NOAA/EOG, public domain with citation).
- **Google Maps / Google Earth: VISUAL spot checks only.** Never scrape, download tiles, trace, or store any data derived from it. Cite it as "visual check, Google Maps, <date>" in `notes`, nothing else.

## 2. Use cases, in priority order
a. **Q14 — locate unlocated stations.** Jeddah's Al-Sulaymaniyah HHR station first, then every other unlocated station and Landbridge stop: OSM (`railway=station`, `public_transport=station`, name matching in Arabic and English) plus imagery confirmation of the platform/roof footprint; write `cities/ksa/lines/stations.geojson` rows with `location_method`, `confidence` and sources; then **rerun the served test** (`screening.funnel`) and report what moved.
b. **Al-Qarā and Al-Khamasin.** Confirm the settlement footprint and the seat town; resolve the Wikidata conflict geometrically: distance from the candidate point to the governorate polygon (inside / outside, km to the boundary); write a conflict row if sources disagree.
c. **Every settlement with no population, or only a secondary one:** estimate it with **at least two independent methods**: (1) gridded population (WorldPop and/or GHS-POP) summed over the settlement polygon; (2) building count (Microsoft footprints or OSM) × occupancy, with household size from Census 2022 (GASTAT, cited). Report the central value and the range (min–max of the methods, widened by each method's back-test error).
d. **The 40 Qassim geocodes not in the manifest:** validate point-in-polygon against the governorate polygons, add the files to `cities/ksa/sources.yaml` with SHA-256, and flag any point outside its governorate.

## 3. Maths and geometry rules
- Compute in a **metric CRS**: the WGS84 UTM north zone of the feature's longitude, zone = floor((lon + 180) / 6) + 1, EPSG 326<zone> (the EPSG definition; a longitude on a boundary belongs to the zone east of it): zone 36N (EPSG:32636) west of 36° E, 37N (32637) 36–42° E, 38N (32638) 42–48° E, 39N (32639) 48–54° E, 40N (32640) 54–60° E (`screening/geo_verify/geom.py`, boundary tests in `tests/test_cp2_item3_utm.py`); EPSG:3857 **only** for display.
- **Geodesic** distances (pyproj `Geod.inv`, WGS84) for every straight-line km in a register.
- **Settlement extents** come from built-up clusters: DBSCAN on building centroids or a morphological close on GHS-BUILT-S; every parameter (eps, min_samples, kernel size, threshold) is an `A-geo-xxx` assumption with value, range and reason.
- Every derived number carries its **method, inputs (manifest ids), parameters (A-geo ids) and an uncertainty band**, and enters the register as `pop_type: derived` (or `grid`), `pop_source_status: secondary`, `primary_to_find: true` (the GASTAT table).
- **Never overwrite an official or GASTAT figure.** Where an estimate differs from it by more than 25 %, log a conflict row (`docs/sources/conflicts.md`) and keep both.
- **Back-test gate:** before using any estimator, run it on **10 settlements with known Census 2022 populations** (stratified by size) and report the **median absolute % error**. Above 30 %: the method is not used for ranking; its values are recorded only (`notes`, `method_log`), never in `population`.

## 4. Package
`screening/geo_verify/`: `cli.py` (typer; `--seed`; commands `stations`, `seat`, `estimate`, `backtest`, `validate-geocodes`, `served-rerun`), `extents.py`, `estimators.py`, `imagery.py` (COG streaming via `rasterio` windowed reads), `geom.py` (CRS choice, geodesic), `method_log.py` (append-only JSONL per derived value: id, method, inputs, parameters, value, band, run id). Tests on fixtures (one synthetic settlement, one station, one back-test table). `docs/geo-verify.md` documents methods, back-test results and the licence rows. New `A-geo-xxx` ids per parameter. The `rail-data-scout` agent and the `region-sweep` skill call this method for every unlocated or unsourced row.

## 5. Limits
- **Stream** cloud-optimised GeoTIFFs clipped to settlement windows (bbox + 2 km). **No national mosaics.**
- Geo caches (`data/ksa/geo/`) ≤ 5 GB; **stop if disk drops below 15 GiB free** (`df -h ~`); record size before every download in the status file.
- Budget for the method: **USD 40 list** (about 75 minutes of an Opus run at the rates observed; the coordinator checks `docs/cost-log.md` and alerts Tariq if exceeded). Time-box accordingly and write what is done and what is not.

## 6. Verification
The `red-team-verifier` spot-checks **10 derived values** against the imagery window and the method log (inputs, parameters, back-test error, band) before PASS, and checks that no Google-derived data exists in the repo.
