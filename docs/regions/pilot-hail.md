> **Document version:** docs/regions/pilot-hail.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, track pilot-hail) | Status: draft

# Pilot region sweep: Ḥā'il (حائل), slug `hail`

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.

This is the coarse pilot sweep that tests the region-sweep schema (PILOT_REGION_HAIL). It is not the full register (that is `REGION_HAIL` in R2). Register: `cities/ksa/regions/pilot-hail.parquet` and `.csv` (11 rows, same ids). Access date for every source: 2026-10-30 (Asia/Riyadh).

## 1. Governorate count

- `governorates_gastat: 9`, `governorates_listed: 9`. **Both figures are secondary.** The GASTAT census portal did not resolve (`portal.saudicensus.sa`, DNS failure, S-hail-002), so the GASTAT primary list was not read. The 9 comes from the citypopulation.de Hail page (S-hail-001), which credits GASTAT, and matches the Arabic Wikipedia table in `docs/gastat-regions.md` (S-073, 9 rows for Ḥā'il). Nothing conflicts, but no primary source confirms it. `docs/coverage.md` must still reconcile this to the GASTAT primary.
- Governorates (9): Al-Ghazalah · Al-Ḥā'īṭ · Ash-Shamlī · Ash-Shanān · As-Sulaymī · Baq'ā' · Ḥā'il · Mawqaq · Simīrā'. Every governorate has at least one row (its centre). The 9 centres are the rows marked centre = Y.
- Census 2022 check: the nine governorate totals sum to 746,406, which equals the region total on the same page.

## 2. Register rows

| # | name (EN / AR) | governorate | centre | osm_id | lat, lon | population (year, type, source) | 5k / 10k / 50k | dist to existing station (km) | nearest metro (tier, km) | economic roles (source) | terrain | screened | pilot_sample |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Ḥā'il / حائل | Ḥā'il | Y | 346801397 | 27.5209, 41.6986 | 448,623 (2022, secondary, S-hail-001) | Y/Y/Y | 18.9 | Buraidah (T2, 261.3) | administrative (S-hail-006), airport (S-hail-006), university (S-hail-007) | mixed | Y | N |
| 2 | Al-Ghazālah / الغزالة | Al-Ghazalah | Y | 8495477458 | 26.7875, 41.3157 | 5,592 (2022, secondary, S-hail-001) | Y/N/N | 108.7 | Buraidah (T2, 269.0) | none sourced | mixed | Y | Y |
| 3 | Al-Ḥā'īṭ / الحائط | Al-Ḥā'īṭ | Y | 1236337588 | 25.9860, 40.4720 | 8,289 (2022, secondary, S-hail-001) | Y/N/N | 227.7 | Madinah (T1, 189.4) | none sourced | mixed | Y | Y |
| 4 | Ash-Shamlī / الشملي | Ash-Shamlī | Y | 5809637428 | 26.8629, 40.3239 | 9,163 (2022, secondary, S-hail-001) | Y/N/N | 168.4 | Madinah (T1, 275.4) | none sourced | mixed | Y | Y |
| 5 | Ash-Shanān / الشنان | Ash-Shanān | Y | 1237555018 | 27.1750, 42.4439 | 11,560 (2022, secondary, S-hail-001) | Y/Y/N | 88.4 | Buraidah (T2, 178.3) | none sourced | mixed | Y | N |
| 6 | As-Sulaymī / السليمي | As-Sulaymī | Y | 1236337734 | 26.2903, 41.3596 | not published | N/N/N | 159.8 | Buraidah (T2, 260.4) | none sourced | mixed | N | N |
| 7 | Baq'ā' / بقعاء | Baq'ā' | Y | 1237538431 | 27.9103, 42.3899 | 19,659 (2022, secondary, S-hail-001) | Y/Y/N | 67.3 | Buraidah (T2, 235.2) | none sourced | mixed | Y | N |
| 8 | Mawqaq / موقق | Mawqaq | Y | 1237937493 | 27.3858, 41.1756 | 3,148 (2022, secondary, S-hail-001) | N/N/N | 66.1 | Buraidah (T2, 301.1) | none sourced | mixed | N | N |
| 9 | Simīrā' / سميراء | Simīrā' | Y | 7684860021 | 26.4942, 42.1249 | 3,105 (2022, secondary, S-hail-001) | N/N/N | 137.2 | Buraidah (T2, 184.8) | none sourced | mixed | N | N |
| 10 | Jubbah / جبة | Ḥā'il | N | 1237937470 | 28.0169, 40.9530 | 5,622 (2022, secondary, S-hail-001) | Y/N/N | 87.2 | Buraidah (T2, 352.5) | heritage (S-hail-005) | mixed | Y | Y |
| 11 | Turubah / تربة | Baq'ā' | N | 1237534271 | 28.2596, 42.9204 | 8,590 (2022, secondary, S-hail-001) | Y/N/N | 131.1 | Buraidah (T2, 238.2) | none sourced | mixed | Y | Y |

Population column: "year, type, source". All population figures are `pop_type: secondary` (see section 8 on the schema). Distances are great-circle (haversine) from OSM coordinates to the nearest **existing station point** on the North line (`A-screen-pilot-001`, `A-screen-pilot-006`). Road minutes are pending R1a skims. Committed distances are not computed (section 5).

## 3. Threshold and sample

- **Towns ≥ 50,000:** one settlement, **Ḥā'il (448,623)** (`threshold_50k = Y`). The governorate totals Al-Ḥā'īṭ (74,596) and Baq'ā' (56,362) are above 50,000, but these are governorate totals, not settlement figures. Their centres are 8,289 and 19,659. The threshold is applied at settlement level (`A-screen-pilot-003`). See section 7.
- **Stratified sample (5 towns, 5,000–50,000; `pilot_sample = Y`).** Each row's reason is in the register's `sample_reason` column.
  - Al-Ghazālah (5,592, centre). Far: 108.7 km from Ḥā'il station. No sourced economic role. Schema edge: the centre is smaller than the non-centre town Jubbah (5,622).
  - Jubbah (5,622, non-centre, Ḥā'il governorate). 87.2 km from the station. **Sourced economic role: heritage** (UNESCO rock-art site, Jabal Umm Sinman, S-hail-005). This is the one sample row with a role.
  - Turubah (8,590, non-centre, Baq'ā' governorate). Far: 131.1 km. No sourced role. OSM's population tag (5,134) conflicts with the census figure. The census figure is used.
  - Ash-Shamlī (9,163, centre). Far: 168.4 km. No sourced role. The OSM node has an Arabic name only.
  - Al-Ḥā'īṭ (8,289, centre). Far: 227.7 km. No sourced role. OSM spells the node "Al Hayit" (الحايط), so this row tests a spelling-variant match (matched by name and coordinates).
- **Schema edges in the sample:** Al-Ghazālah (centre) and Jubbah (non-centre) show a governorate centre smaller than a non-centre town. The Al-Ḥā'īṭ row tests an OSM name variant. A town split across governorates was not found in this pilot.
- **Gap, not closed:** no 5,000–50,000 town lies within 25 km of an existing station in Ḥā'il. The "near" test (<25 km) is therefore **not met** and the sample is far-biased (see section 7).

## 4. Excluded and not registered

Excluded rows (`screened = N`, with reason):
- As-Sulaymī (centre): centre population is not in the Census 2022 places table (2,500+). Not estimated; the governorate total (17,343) is not used as a settlement figure. Needs judgement.
- Mawqaq (3,148, centre) and Simīrā' (3,105, centre): below 5,000 and no sourced economic role. Kept as rows only so each governorate is covered.

Places from the citypopulation.de 2,500+ table that are **not registered** (18 places in the table; 10 registered, 8 not):
- Al-Ajfir (7,518, Baq'ā' governorate): no OSM place node found in the pilot extract. Coordinates are required by the schema, so it is not registered. **Needs judgement:** this is a 5,000–50,000 town and should be placed in R2.
- Al-Ḥafīr (3,243), Al-Ḥalīfah as-Suflā (4,151), Al-Khuṭah (3,355), Al-Qā'id (2,913), An-Nayṣīh (4,597), Ar-Rarwḍah (2,906), Munīfat al-Qā'id (4,688): below 5,000, not sampled (pilot scope). Full sweep in R2.

## 5. Distances and layers

- **Existing (North line, passenger).** In operation: the Northern Network carried 258,600 passengers in Q3 2026 and its route includes Hail and Al-Jouf (Asharq Al-Awsat, 21 Oct 2026, S-hail-004; route also in S-018). Stations used: Ḥā'il, Al-Qassim, Al-Majmaah and Al-Jawf (OSM `railway=station|stop` nodes). The distance is to the nearest **station point**, not to the alignment (`A-screen-pilot-006`).
- **Committed (under procurement).** Not computed. The Landbridge, GCC railway and Riyadh Rail Link alignments and station coordinates are not published with coordinates in the repository (S-061 and S-062 unverified). Every row's committed fields are null, with no value guessed.
- **Metro.** Nearest metro from the approved set (`A-screen-013`) by haversine. Most rows fall to Buraidah (tier 2). Ash-Shamlī and Al-Ḥā'īṭ fall to Madinah (tier 1) because it is closer. Tiers are recorded in the Parquet (`nearest_metro_tier`).

## 6. Economic roles and terrain

- **Ḥā'il (city):** administrative (regional capital: GACA snippet, S-hail-006); airport (Hail Airport, HAS/OEHL, serves Ḥā'il; S-hail-006); university (جامعة حائل, official site uoh.edu.sa, S-hail-007).
- **Jubbah:** heritage (UNESCO World Heritage serial site, Jabal Umm Sinman at Jubbah; secondary, S-hail-005; the UNESCO page itself returned HTTP 403).
- **All others:** no role sourced in this pilot, so `economic_roles` is empty.
- **Terrain:** Ḥā'il city is `mixed`, sourced to the regional description (Aja to the west, Salma to the south-east, An Nafud sand sea to the north and east; S-hail-008, secondary). Every other row is `mixed` as an **assumption** (`A-screen-pilot-002`): the regional description is sourced, but no DEM classification was done for the row. The DEM step is R1a/R2 work.

## 7. Needs judgement

1. **As-Sulaymī centre population** is absent from the 2,500+ table. Not estimated; needs a primary (GASTAT locality table).
2. **Al-Ajfir (7,518)** is not registered: no OSM node in the pilot extract. Needs a coordinate and an osm_id.
3. **The 50,000 threshold is applied at settlement level.** Al-Ḥā'īṭ (74,596) and Baq'ā' (56,362) pass as governorate totals but not as settlements. Confirm this reading.
4. **The "near" sample test (<25 km from an existing station) is unmet.** No 5,000–50,000 town in Ḥā'il is within 25 km of a station. The sample is far-biased; say so if the R2 test is strict.
5. **Terrain** is `mixed` by assumption for every row except Ḥā'il city. Decide whether R1a should run a DEM classification.
6. **Population sources conflict with OSM tags** (not used): Ḥā'il city node 310,897 vs census 448,623; Baq'ā' 13,382 vs 19,659; Ash-Shanān 7,157 vs 11,560; Turubah 5,134 vs 8,590; Jubbah 5,493 vs 5,622; Al-Qā'id 5,523 vs 2,913. The census figure is used throughout, but the OSM tags are old and the discrepancy should be explained.
7. **Economic-role sources are partly weak:** the GACA airport page was read as a search snippet only (direct fetch not completed; S-hail-006), and the UNESCO page returned 403 (S-hail-005, secondary via worldheritagesite.org).

## 8. Schema deviations (flagged, not fixed in `common/`)

- `common/schemas.py:RegionRow` has `pop_type` as `official | derived | grid`. The pilot brief and `source-citation` require `secondary` for aggregator figures. The register writes `secondary`, and validation used a local subclass that adds `secondary` (`common/` untouched, per the additive-only rule). **Needs judgement** on the schema change.
- `RegionRow` has no `threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `primary_to_find`, `terrain_basis`, `assumption_id`, `road_min_method`, `dist_method` or `notes`. These are extra pilot columns in the Parquet and CSV. The validator drops them before checking the `RegionRow` fields.
- `screening.region_sweep` (the `validate` command) does not exist yet in this worktree. Validation was done with pydantic against `RegionRow` (11/11 rows pass; Parquet and CSV agree on row count and ids).
- Parquet schema metadata holds `governorates_gastat: 9` and `governorates_listed: 9`.

## 9. Sources

| id | what it supports | status |
|---|---|---|
| S-hail-001 | populations (governorates and places 2,500+), region total 746,406; census date 10 May 2022 | secondary (citypopulation.de; GASTAT credited) |
| S-hail-002 | GASTAT primary portal (not reached) | unverified |
| S-hail-003 | OSM node ids and coordinates; metro city nodes (ODbL) | verified (manifest osm-gcc-2026-10-14) |
| S-hail-004 | North Line in passenger service; Q3 2026 passengers | secondary (press) |
| S-hail-005 | Jubbah: UNESCO rock-art serial site (inscribed 2015) | secondary |
| S-hail-006 | Hail Airport; serves Ḥā'il, capital of the province | secondary (snippet) |
| S-hail-007 | University of Ha'il (Arabic name on official site) | verified |
| S-hail-008 | Ḥā'il city elevation and surrounding ranges and sand sea | secondary |
| S-018 | SAR North Line route (Riyadh–Majmaah–Qassim–Hail–Jouf–Qurayyat) | verified (existing register) |
| S-071, S-070 | Census 2022 date and 13 regions | existing register |
| S-073 | governorate row count (150 total; Hail 9) | secondary (existing register) |

Licence and attribution: OSM © OpenStreetMap contributors (ODbL). citypopulation.de terms not checked; the transcription is gitignored (`data/ksa/hail/`) and not committed. Register rows in `docs/licences-pilot-hail.csv`.
