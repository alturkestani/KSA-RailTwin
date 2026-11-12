> **Document version:** docs/status/pilot-jazan.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, track pilot-jazan) | Status: draft

# Track `pilot-jazan` — status

## PILOT_REGION_JAZAN: coarse pilot sweep of Jazan (جازان), slug `jazan` — 30 Oct 2026

Label: screening input, not a forecast.

**Rows written:** 20 (17 governorate centres + 3 non-centre sample towns). Files: `cities/ksa/regions/pilot-jazan.parquet` and `.csv` (same 20 ids, same values; checked by row count, `osm_id` and `name_en`), `docs/regions/pilot-jazan.md` (table generated from the Parquet), `docs/sources/pilot-jazan.csv` (14 `S-jazan-*` rows), `docs/assumptions-pilot-jazan.md` (6 rows), `docs/licences-pilot-jazan.md` and `.csv` (6 rows).

**Governorates:** GASTAT official count **not read** (portal.saudicensus.sa did not connect; S-jazan-015). `governorates_listed` = **17** (citypopulation.de, Census 2022 list; S-jazan-001). Saudipedia says **16** (S-jazan-003). **Discrepancy flagged, not resolved** (Needs Opus 1). Header key in the Parquet: `governorates_gastat: unverified`, `governorates_listed: 17`.

**Towns ≥ 50,000 (Census 2022, secondary):** 3 — Jizan 173,919; Sabya 72,086; Abu Arish 69,632.

**Sample (`pilot_sample: true`):** 5 rows, each with a reason in `sample_reason`: Abu as Sadad (schema edge: non-centre larger than its governorate centre), Farasan (roles: tourism, heritage), Samtah (role: agriculture), Al Zabyah (no role, near a 50k town), Misliyah (no role, 5k band). Near (<25 km) rail case: **none exists in Jazan** (no existing or committed line in the region); all 20 rows are > 480 km from the nearest existing station.

**Facts (14 sources):** verified 4 (OSM nodes; Makkah HHR station), secondary 9 (citypopulation.de, Saudipedia, Arab News, Gulf Industry, CruiseMapper, Wikipedia), unverified 1 (GASTAT portal).

**Elapsed:** about 12 minutes, 21:33 to 21:43 (Asia/Riyadh, from file timestamps; no run-time measurement).

**Checks run:**
- `RegionRow` validation (`common/schemas.py`) on all 20 rows: **passes**, with one deliberate relaxation (below). `uv run python -m screening.region_sweep validate` does **not** exist yet (`screening/cli.py` is the R0 skeleton), so the brief's command could not run.
- Acceptance: governorates flagged (both sources cited), every row with `pop_source`/`pop_year`/`pop_type` when a population is set, every distance has a method (`haversine`), no committed line labelled existing, every economic role has a source, 5 sample rows with reasons, Parquet and CSV agree.

**Deviations from the brief (for the coordinator):**
1. **`pop_type: secondary`** is not in `RegionRow` (its Literal is official / derived / grid). Validation used a local subclass (in `/tmp`, not committed) that widens that one Literal; nothing else changed. Decision needed: add `secondary` to `RegionRow.pop_type` (and `primary_to_find`) before R2.
2. **Extra fields** not in `RegionRow` (strict, `extra=forbid`) are written as Parquet/CSV columns, not validated: `threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `terrain_basis`, `primary_to_find`, `road_min_method`, `dist_method`. Same decision as 1.
3. **No `screening/region_sweep` module**, so the register was written with pandas against `RegionRow`, as the brief allowed.
4. **`common/` untouched** (the brief allows additive changes only; none were needed).

**Data and gates:** no download over 50 MB (the Overpass and Nominatim responses were a few KB to 6.7k nodes). No GHSL/WorldPop grid, no PBF, no DEM. Disk was checked in the R0 record (26 GiB free) and not changed by this run.

**Needs Opus judgement (not guessed into values):**
1. Governorate count 16 (Saudipedia) vs 17 (citypopulation). GASTAT's own table is needed.
2. Al Harth centre: no `place=*` node in the OSM box query. Coordinates are a Nominatim boundary bbox centre (A-screen-pilot-004), a placeholder. Population null.
3. Jizan port (JCPDI) location: 60 km north vs 60 km south-east of Jizan in two sources (S-jazan-009). The port and industrial zone roles are on the Jizan row without coordinates for the zone.
4. Terrain classes are rule-based (A-screen-pilot-002: 42.75° E cut-off; Fayfa escarpment). Copernicus DEM classes needed in R2.
5. Population null for Ar Rayth, Harub, Fayfa and Al Harth (their governorate totals are in the list, but no centre figure is in the 2022 places table).
6. Al Tuwal (Yemen border): no sourced `border_crossing` role; not assigned.
7. Samtah agriculture role rests on a search snippet of the Saudipedia page; read the page before use.
8. Aṭ-Ṭuwāl, Fayfā and Harūb carry a previous-parent marker on citypopulation (Ṣāmiṭah, Jīzān, Al-'Aydābī); membership of their settlements to check in the GASTAT admin table.
9. Economic roles left empty where none is sourced (Sabya and Abu Arish, both 50k+; Abu as Sadad, Al Zabyah, Misliyah). Not guessed.

**Outcome:** the pilot schema works on a real region. Two schema gaps need a coordinator decision (deviations 1–2) before R2.

PILOT_REGION_JAZAN: done
