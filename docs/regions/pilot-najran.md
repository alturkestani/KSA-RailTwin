> **Document version:** docs/regions/pilot-najran.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_NAJRAN) | Status: draft

# Najran region: pilot sweep (coarse, high cut-off)

**Screening input, not a forecast.** This is the pilot register for slug `najran` (نجران). It tests the region-sweep schema. It is not the full `REGION_NAJRAN` register (R2). Access date for every source: 2026-10-30 (Asia/Riyadh). Register: `cities/ksa/regions/pilot-najran.parquet` (and `.csv`, same rows). Sources: `docs/sources/pilot-najran.csv` (S-najran-001 to 010) plus existing rows in `docs/sources/index.csv`. Assumptions: `docs/assumptions-pilot-najran.md`.

## Header values

- `governorates_gastat: 7 (unverified)`. The GASTAT primary list could not be reached: portal.saudicensus.sa does not resolve (S-090), and stats.gov.sa has no region or governorate tables (checked 30 Oct 2026). The 7 comes from secondary sources only (S-najran-001, S-073).
- `governorates_listed: 7`: six governorates plus the regional capital Najrān, which citypopulation.de lists as its own governorate row (S-najran-001). Saudipedia describes the region as "six governorates" plus the capital (S-najran-003). The two secondary sources agree, so no discrepancy is flagged, but neither is the primary check.
- Region total: 592,300 (Census 2022, S-najran-001). The seven governorate rows sum exactly to this total (7,991 + 24,823 + 7,834 + 421,902 + 100,199 + 13,391 + 16,160 = 592,300). DataSaudi also quotes 592,300 (secondary; not registered as a source row).
- Towns ≥ 50,000: **2** (Najrān city 381,431; Sharūrah town 89,456; both S-najran-002).
- Pilot sample (5,000–50,000, `pilot_sample: true`): **4**. This is the complete set of sourced 5k–50k localities in the region (see the sample rationale).
- Rows: **9** (7 governorate centres + 2 non-centre localities).
- Population type: **every population is `secondary`** (citypopulation.de crediting GASTAT). The schema enum does not contain `secondary` (see Schema gaps). `primary_to_find`: GASTAT Census 2022 locality table for Najran (not reachable).

## Register (generated from the Parquet)

Table A: identity, coordinates, population and tags.

| name (EN) | name (AR) | governorate | centre | OSM id (type) | lat, lon | population (pop_type, year, source) | ≥50k | ≥10k | ≥5k | pilot sample |
|---|---|---|---|---|---|---|---|---|---|---|
| Najrān | نجران | Najrān (نجران) | yes | n982548735 (city) | 17.54398, 44.22468 | 381,431 (secondary, 2022, S-najran-002) | yes | yes | yes | no |
| Sharūrah | شرورة | Sharūrah (شرورة) | yes | n1013646681 (city) | 17.49123, 47.11261 | 89,456 (secondary, 2022, S-najran-002) | yes | yes | yes | no |
| Al-Mish'alīah | المشعلية | Najrān (نجران) | no | n4213220389 (village) | 17.75783, 44.46435 | 23,252 (secondary, 2022, S-najran-002) | no | yes | yes | yes |
| Ḥubūnā | حبونا | Ḥubūnā (حبونا) | yes | n11871306300 (town) | 17.85185, 44.02316 | 12,738 (secondary, 2022, S-najran-002) | no | yes | yes | yes |
| Khubāsh | خباش | Khubāsh (خباش) | yes | n8503374507 (village) | 17.54985, 44.74113 | 7,182 (secondary, 2022, S-najran-002) | no | no | yes | yes |
| Al-Wadī'ah | الوديعه | Sharūrah (شرورة) | no | n1236473531 (village) | 17.05751, 47.08815 | 8,365 (secondary, 2022, S-najran-002) | no | no | yes | yes |
| Yadamah | يدمة | Yadamah (يدمة) | yes | n6774224946 (village) | 18.52917, 44.20306 | 4,983 (secondary, 2022, S-najran-002) | no | no | no | no |
| Badr al-Janūb | بدر الجنوب | Badr al-Janūb (بدر الجنوب) | yes | n9327906415 (town) | 17.88137, 43.71636 | 2,709 (secondary, 2022, S-najran-002) | no | no | no | no |
| Thār | ثار | Thār (ثار) | yes | n6774275597 (town) | 17.97488, 44.11082 | — (not sourced) | no | no | no | no |

Table B: distances, metro, economic roles, terrain, screening.

| name (EN) | dist existing km (method: haversine) | nearest existing | committed km | dist metro km | nearest metro (tier) | economic roles (source) | terrain (assumed) | screened | exclusion reason |
|---|---|---|---|---|---|---|---|---|---|
| Najrān | 633.8 | Haramain high-speed rail (OSM segment near Makkah) | not computed (no committed geometry) | 0.0 | Najrān (tertiary) | administrative (S-najran-001); university (S-najran-005); airport (S-najran-006) | mixed (A-najran-terrain-001) | yes | — |
| Sharūrah | 750.6 | Riyadh–Dammam line (OSM, named 'قطار الدمام - الخط الثاني') | not computed (no committed geometry) | 306.3 | Najrān (tertiary) | administrative (S-najran-001); airport (S-najran-007) | dunes (A-najran-terrain-001) | yes | — |
| Al-Mish'alīah | 636.7 | Haramain high-speed rail (OSM segment near Makkah) | not computed (no committed geometry) | 34.8 | Najrān (tertiary) | — | mixed (A-najran-terrain-001) | yes | — |
| Ḥubūnā | 594.8 | Haramain high-speed rail (OSM segment near Makkah) | not computed (no committed geometry) | 40.3 | Najrān (tertiary) | administrative (S-najran-001) | mixed (A-najran-terrain-001) | yes | — |
| Khubāsh | 674.1 | Haramain high-speed rail (OSM segment near Makkah) | not computed (no committed geometry) | 54.8 | Najrān (tertiary) | administrative (S-najran-001) | mixed (A-najran-terrain-001) | yes | — |
| Al-Wadī'ah | 798.9 | Riyadh–Dammam line (OSM, named 'قطار الدمام - الخط الثاني') | not computed (no committed geometry) | 308.8 | Najrān (tertiary) | border_crossing (S-najran-010) | dunes (A-najran-terrain-001) | yes | — |
| Yadamah | 562.1 | Haramain high-speed rail (OSM segment near Makkah) | not computed (no committed geometry) | 109.6 | Najrān (tertiary) | administrative (S-najran-001) | mixed (A-najran-terrain-001) | no | Centre population 4,983 is below the 5,000 sensitivity threshold (A-screen-002). Kept as the governorate-centre coverage row (rule 2). Governorate total 16,160 (S-najran-001) is not used as the centre figure. |
| Badr al-Janūb | 569.0 | Haramain high-speed rail (OSM segment near Makkah) | not computed (no committed geometry) | 65.6 | Najrān (tertiary) | administrative (S-najran-001) | mixed (A-najran-terrain-001) | no | Centre population 2,709 is below 5,000 (A-screen-002). Kept as the governorate-centre coverage row (rule 2). Governorate total 7,991 (S-najran-001). |
| Thār | 592.6 | Haramain high-speed rail (OSM segment near Makkah) | not computed (no committed geometry) | 49.4 | Najrān (tertiary) | administrative (S-najran-001) | mixed (A-najran-terrain-001) | no | No sourced centre population: Thār is not in the census locality table (places ≥2,500, S-najran-002), so the centre figure is null (not guessed). Governorate total 13,391 (S-najran-001) is not used. Kept as coverage row (rule 2). |

Column notes:
- **Existing distances** are great-circle (haversine, A-screen-pilot-001) from the OSM point to the nearest vertex of a Saudi existing rail way (`railway=rail`, excluding construction, proposed, yard, siding, crossover, spur and industrial). Najrān region has **no rail in OSM**, so every row is a long-range distance. Road minutes are empty (`road_min_method: pending R1a skims`).
- **Committed distances** are not computed. `cities/ksa/lines/` does not exist yet, and no committed line geometry (Landbridge, GCC railway, Riyadh Rail Link) is in the repo. OSM railway=construction ways are not the announced committed layer; for information only, the nearest such way is about 905 km to 1,020 km from the Najrān-region rows. This value is not registered.
- **Metro** distances use the approved set (A-screen-013) with OSM city-node coordinates (A-screen-pilot-002). Najrān is itself a tertiary metro, so the Najrān city row is 0.0 km from itself. The nearest metro for every other row is Najrān (tertiary tier); the next-nearest approved metros are Khamis Mushait and Abha (secondary).
- **Terrain** is assumed for every row (A-najran-terrain-001). Najrān valley and centres are `mixed`; Sharūrah and Al-Wadī'ah are `dunes` from desert descriptions. These are not DEM classes. R1a should replace them with Copernicus or SRTM classes.

## Sample rationale (Najrān)

The sourced pool of 5,000–50,000 localities in the region is exactly four (Al-Mish'alīah, Ḥubūnā, Khubāsh, Al-Wadī'ah). The stratified sample therefore takes the whole pool, which meets the 4–6 requirement. The strata were applied as follows:

- **Rail distance (near < 25 km, far > 100 km):** all four are far (≥ 560 km from existing rail). The "near" stratum is empty by construction, so the near/far split cannot be tested in Najrān. Recorded as a gap, not filled.
- **Economic role:** Al-Wadī'ah (border crossing, S-najran-010), Ḥubūnā and Khubāsh (governorate centres, S-najran-001), and Al-Mish'alīah (no sourced role).
- **Schema edges tested** (the reason for each row is also in its `notes` field in the Parquet):
  - Al-Mish'alīah: OSM tags it `village` but the census table lists a 23,252 place, the largest non-centre locality in Najrān governorate. It tests an OSM tag mismatch.
  - Ḥubūnā: a governorate centre (12,738) against the governorate total (24,823). It also has two OSM nodes (town and governorate); the town node is used.
  - Khubāsh: a governorate centre (7,182) against a governorate total of 7,834. Two OSM candidates exist (village and governorate nodes); see Needs judgement.
  - Al-Wadī'ah: a non-centre town at 8,365 with a sourced border-crossing role.
- **Not testable in this pilot:** "a governorate centre smaller than a non-centre town" within one governorate. The only sourced non-centre localities (Al-Mish'alīah in Najrān, Al-Wadī'ah in Sharūrah) each sit in a governorate whose centre is larger (381,431 and 89,456). "A town split across governorates": none found in the sourced table.
- **Near/far, role and threshold coverage** are therefore partial. The sample is a schema test, not a representative draw.

## Exclusions (with reasons)

- **Yadamah** (centre, 4,983): below the 5,000 sensitivity threshold (A-screen-002). Kept as the governorate-centre coverage row (rule 2), `screened: false`.
- **Badr al-Janūb** (centre, 2,709): below 5,000. Kept as a coverage row, `screened: false`.
- **Thār** (centre): the centre is not in the census locality table (places ≥ 2,500), so no population is sourced. Population is left null, not guessed. Kept as a coverage row, `screened: false`. The governorate total 13,391 is not used for the centre.
- No town of 5,000–50,000 is excluded. The region has no other sourced localities in that band.

Governorate-to-row check: each of the 7 governorates has one row (Najrān, Sharūrah, Ḥubūnā, Khubāsh, Yadamah, Badr al-Janūb, Thār). Najrān governorate's non-centre localities other than Al-Mish'alīah are not sourced, so Najrān governorate's total (421,902) exceeds the city row (381,431) by 40,471. That difference is not a row.

## Sources

Pilot-specific (`docs/sources/pilot-najran.csv`):
- S-najran-001: citypopulation.de, Najrān Region governorate table (census 2022; source line credits GASTAT). Secondary.
- S-najran-002: citypopulation.de, Najrān Region places ≥ 2,500 (census 2022). Secondary.
- S-najran-003: Saudipedia, Najran Province (search snippet). Secondary.
- S-najran-004: OpenStreetMap GCC extract (manifest `osm-gcc-2026-10-14`, ODbL 1.0; SHA-256 `fffc7e74…6ad2073`). Verified (local file).
- S-najran-005: Najran University location (portal snippet). Secondary.
- S-najran-006: Najran airport (Times Aerospace news, snippet). Secondary.
- S-najran-007: en.wikipedia, Al-Wadiah (search summary). Secondary.
- S-najran-008: Saudipedia, Sarawat Mountains (snippet). Secondary.
- S-najran-009: Saudipedia, Sharurah Governorate (search summary). Unverified; the dune claim is weakly sourced.
- S-najran-010: Governor of Najran and Al-Wadeeah crossing (ajel.sa snippet). Secondary.

Existing rows used:
- S-073: citypopulation.de admin list (150 rows; GASTAT-credited). Secondary.
- S-071: census reference date, 9 May 2022.
- S-090: GASTAT portal unreachable (primary not reached).

## Needs judgement

1. **Khubāsh centre node.** The census places Khubāsh at 7,182 but OSM has two candidates: village node n8503374507 at 17.54985, 44.74113 (used) and governorate node n6774251958 at 17.66667, 45.25 (708 km from existing rail, 110 km from Najrān). Which node is the centre needs a decision.
2. **Ḥubūnā centre node.** Town node n11871306300 (used) vs governorate node n6769844117 (17.78333, 44.2). Same question.
3. **Najrān centre population.** The row uses the city figure 381,431 (place). The governorate figure is 421,902. Decide which one the centre row carries under the GASTAT list once it is found.
4. **Sharūrah centre population.** The row uses the town figure 89,456; the governorate figure 100,199 includes Al-Khirkhīr. Same question.
5. **Al-Mish'alīah.** OSM place=village vs census "Place" 23,252. Keep the census population, and decide whether to correct the OSM tag (outside this register).
6. **Sharūrah airport role.** Rests on the airport name in S-najran-007, not on a sourced location. Verify before any use of the role.
7. **Thār centre population.** Null. Needs the GASTAT locality table.
8. **Terrain.** All terrain classes are assumed (A-najran-terrain-001). Replace from DEM in R1a. The dune call for Sharūrah and Al-Wadī'ah rests on weakly sourced text (S-najran-009).
9. **Spelling.** "Khubāsh" (citypopulation) vs "Khubash" (OSM and secondary snippets). The register uses the citypopulation spelling.

## Schema gaps (for merge-stage; the register is not changed)

- `pop_type` enum is `official | derived | grid`. The prompt's `secondary` value is not in `common/schemas.py:RegionRow`. Rows are written as `secondary`; the validation run maps it to `official` for the check only.
- `RegionRow` has no `threshold_50k`, `pilot_sample`, `notes`, `osm_place_tag`, `dist_method` or `screen_stage` columns, and no `nearest_metro_tier` (the tier is in the `nearest_metro` string). These extra columns are in the Parquet and CSV.
- `terrain_class` enum is `flat_desert | dunes | sabkha | escarpment_mountain | coastal | mixed`. The prompt lists `sand_dunes` and `coastal_plain`, which do not exist in the schema. The schema values are used.
- `screening.region_sweep` does not exist (`screening/cli.py` is the R0 skeleton). `uv run python -m screening.region_sweep validate` cannot run. Validation was done by a copy of the rows against `RegionRow` with the two shims above (9 of 9 pass).
- `cities/ksa/lines/` does not exist, so committed distances cannot be computed.
- The `region-sweep` skill's `is_governorate_centre` and `tag_*` rules are satisfied.

## Validation performed

- `RegionRow` copy-validation: 9 of 9 rows pass (with the two shims above).
- Parquet and CSV: 9 rows each, same `osm_id` and `name_en` order.
- Population arithmetic: governorate rows sum to the region total (592,300).
- Every population carries `pop_source`, `pop_year` and `pop_type`. Thār, with no population, has all three null.
- Every distance carries a method (haversine, A-screen-pilot-001).
- No planned or committed line is labelled existing. Najrān has no committed rows.
- Every economic role names a source id.
- Four rows carry `pilot_sample: true`, each with a reason in `notes`.
