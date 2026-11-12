> **Document version:** docs/regions/najran.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_NAJRAN) | Status: draft

# Najrān region sweep (نجران, slug `najran`): R2 register

**Screening input, not a forecast.** Register: `cities/ksa/regions/najran.parquet` (and `.csv`, same rows). Built by `screening/sweeps/najran/build.py`; this page by `screening/sweeps/najran/write_docs.py`. Access dates: 2026-10-31 for the GASTAT primary files and the R1a builds; 2026-10-30 for the pilot-derived secondary rows (kept unchanged in `docs/sources/r2-najran.csv`). Sources: `docs/sources/r2-najran.csv` plus existing rows in `docs/sources/index.csv`. Assumptions: `docs/assumptions.md` (merged at R2).

## Header values

- `governorates_gastat: 7`: the seven Najrān governorate totals (six governorates plus the regional capital) all appear in the GASTAT primary TA1 governorate export (S-cp2-gastat-007, value match, 150 rows), and the region membership follows S-073 and the OSM polygons (see A-najran-006). Saudipedia's "six governorates plus the capital" (S-najran-003) agrees.
- `governorates_listed: 7`. Equal to `governorates_gastat`; no discrepancy.
- Region total: 592,300 (Census 2022). The seven governorate totals sum to 592,300 (S-najran-001, S-cp2-gastat-007).
- Rows: 13 (7 governorate centres + 6 non-centre localities at 5,000 or more). Settlements in the R1a universe for Najrān: 187; 174 are not rows, and all of them are below 5,000 on both the official and the grid figure (checked by the script).
- At or above 10,000 (`tag_10k`): **4** rows (Najrān, Sharūrah, Al Mishaliah, Ḥubūnā, all official, GASTAT primary export).
- At or above 5,000 (`tag_5k`, sensitivity): **11** rows. Four are `tag_10k`; the other seven are Abā al-Sa'ud (grid 11,474, uncorroborated) and six at 5,000–9,999 (Khubāsh, Thār, Al Wadī'ah, Al Mikhlaf, Al Nukaysi, Al Urayisah).
- Grid-only towns at 10,000 or more that fail the corroboration gate: 1 (Abā al-Sa'ud, 11,474, `tag_10k` false, reason in the register).
- Screened rows: 11 of 13; excluded (kept as coverage rows): 2 governorate centres below 5,000 (Yadamah, Badr Al Janub).
- Population sources by status: verified 6 (GASTAT primary export), secondary 2 (citypopulation.de, crediting GASTAT), unverified 5 (WorldPop gap-fill).
- Economic roles: 13; sourced to an S- id: 13.

## Register

Table A: identity, coordinates, population and tags.

| name (EN) | name (AR) | governorate | centre | OSM node | lat, lon | population (type, year, source status) | ≥10k | ≥5k | screened |
|---|---|---|---|---|---|---|---|---|---|
| Najran | نجران | Najran (نجران) | yes | node 982548735 | 17.54398, 44.22468 | 381,431 (official, 2022, verified) | yes | yes | yes |
| Sharurah | شرورة | Sharurah (شرورة) | yes | node 1013646681 | 17.49123, 47.11261 | 89,456 (official, 2022, verified) | yes | yes | yes |
| Al Mishaliah | المشعلية | Najran (نجران) | no | node 4213220389 | 17.75783, 44.46435 | 23,252 (official, 2022, verified) | yes | yes | yes |
| Hubuna | حبونا | Hubuna (حبونا) | yes | node 11871306300 | 17.85185, 44.02316 | 12,738 (official, 2022, verified) | yes | yes | yes |
| Aba Al Saud | ابا السعود | Najran (نجران) | no | node 6774270978 | 17.45652, 44.11210 | 11,474 (grid, 2020, unverified) | no | yes | yes |
| Al Wadiah | الوديعة | Sharurah (شرورة) | no | node 1236473531 | 17.05751, 47.08815 | 8,365 (official, 2022, verified) | no | yes | yes |
| Thar | ثار | Thar (ثار) | yes | node 6774275597 | 17.97488, 44.11082 | 8,030 (grid, 2020, unverified) | no | yes | yes |
| Khubash | خباش | Khubash (خباش) | yes | node 8503374507 | 17.54985, 44.74113 | 7,182 (official, 2022, verified) | no | yes | yes |
| Al Mikhlaf | المخلاف | Najran (نجران) | no | node 11871306808 | 17.48607, 44.10313 | 6,853 (grid, 2020, unverified) | no | yes | yes |
| Al Nukaysi | النكاسي | Najran (نجران) | no | node 6774270081 | 17.56620, 44.32752 | 6,525 (grid, 2020, unverified) | no | yes | yes |
| Al Urayisah | العريسة | Najran (نجران) | no | node 6774292689 | 17.55907, 44.30769 | 6,093 (grid, 2020, unverified) | no | yes | yes |
| Yadamah | يدمة | Yadamah (يدمة) | yes | node 6774224946 | 18.52917, 44.20306 | 4,983 (official, 2022, secondary) | no | no | no |
| Badr Al Janub | بدر الجنوب | Badr Al Janub (بدر الجنوب) | yes | node 9327906415 | 17.88137, 43.71636 | 2,709 (official, 2022, secondary) | no | no | no |

Table B: distances, metro, economic roles, terrain, screening.

| name (EN) | dist existing km (road min) | nearest existing | committed km (road min) | nearest committed (station) | dist metro km (road min) | nearest metro (tier) | economic roles (source) | terrain (assumed) | exclusion |
|---|---|---|---|---|---|---|---|---|---|
| Najran | 633.8 (645.9) | hhr (road target hhr:makkah) | 601.8 (648.2) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 0.0 (0.0) | Najran (tier 3) (3) | administrative (S-najran-001); airport (S-cp1-100;S-r1a-210); university (S-r1a-221;S-r1a-222;S-r1a-210); industrial_city (S-r1a-204;S-r1a-210); heritage (S-r1a-205) | mixed (A-najran-001) | — |
| Sharurah | 787.1 (797.9) | sar-east-passenger (road target sar-east-passenger:riyadh) | 779.9 (779.5) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 306.3 (237.3) | Najran (tier 3) (3) | administrative (S-najran-001); airport (S-cp1-100;S-r1a-210) | dunes (A-najran-001) | — |
| Al Mishaliah | 636.8 (641.6) | hhr (road target sar-east-passenger:riyadh) | 591.8 (623.2) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 34.8 (45.8) | Najran (tier 3) (3) | none sourced | mixed (A-najran-001) | — |
| Hubuna | 594.8 (658.1) | hhr (road target hhr:makkah) | 561.8 (665.5) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 40.3 (73.9) | Najran (tier 3) (3) | administrative (S-najran-001) | mixed (A-najran-001) | — |
| Aba Al Saud | 632.0 (653.2) | hhr (road target hhr:makkah) | 605.8 (660.6) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 15.4 (21.5) | Najran (tier 3) (3) | none sourced | mixed (A-najran-001) | grid-only population, uncorroborated |
| Al Wadiah | 835.3 (831.6) | sar-east-passenger (road target sar-east-passenger:riyadh) | 815.9 (813.3) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 308.8 (271.1) | Najran (tier 3) (3) | border_crossing (S-najran-010) | dunes (A-najran-001) | — |
| Thar | 592.6 (681.9) | hhr (road target sar-east-passenger:riyadh) | 553.3 (663.5) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 49.4 (70.8) | Najran (tier 3) (3) | administrative (S-najran-001) | mixed (A-najran-001) | — |
| Khubash | 674.1 (687.8) | hhr (road target sar-east-passenger:riyadh) | 626.2 (669.4) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 54.8 (52.4) | Najran (tier 3) (3) | administrative (S-najran-001) | mixed (A-najran-001) | — |
| Al Mikhlaf | 629.0 (642.9) | hhr (road target hhr:makkah) | 602.4 (650.3) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 14.4 (22.4) | Najran (tier 3) (3) | none sourced | mixed (A-najran-001) | — |
| Al Nukaysi | 640.1 (657.9) | hhr (road target hhr:makkah) | 604.2 (639.6) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 11.2 (12.8) | Najran (tier 3) (3) | none sourced | mixed (A-najran-001) | — |
| Al Urayisah | 639.1 (652.6) | hhr (road target hhr:makkah) | 604.0 (647.5) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 9.0 (7.5) | Najran (tier 3) (3) | none sourced | mixed (A-najran-001) | — |
| Yadamah | 562.1 (696.5) | hhr (road target sar-east-passenger:riyadh) | 503.4 (595.9) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 109.6 (141.6) | Najran (tier 3) (3) | administrative (S-najran-001) | mixed (A-najran-001) | Centre population 4,983 is below 5,000 (A-screen-002). Kept as the governorate-centre coverage row (rule 2); the governorate total is not used as the centre figure. |
| Badr Al Janub | 569.0 (592.8) | hhr (road target hhr:makkah) | 546.0 (600.1) | landbridge (landbridge:muwai, Muwai/Moya, announced stop (S-062)) | 65.6 (117.4) | Najran (tier 3) (3) | administrative (S-najran-001) | mixed (A-najran-001) | Centre population 2,709 is below 5,000 (A-screen-002). Kept as the governorate-centre coverage row (rule 2); the governorate total is not used as the centre figure. |

Column notes:
- **Distances** are great-circle (haversine, A-screen-pilot-001) to R1a's alignment vertices (1 km spacing). **Road minutes** are R1a's OSRM car skim (free flow, uncalibrated) to the nearest target station, as recorded in the settlements universe. The skim targets: `hhr:makkah`, `sar-east-passenger:riyadh`, `sar-east-passenger:hufuf`, `landbridge:muwai`.
- **Committed layer:** Landbridge (`committed`, announced; `cities/ksa/lines/landbridge.yaml`, S-054). The station shown is the Muwai/Moya intermediate stop, named but not located in S-062; it is an announced stop, not an existing or built one. No row calls a committed or hypothetical line existing.
- **Terrain** is assumed for every row (A-najran-001); no DEM class has been computed in R2.
- **Metro**: all rows point to Najrān (tier 3), the nearest approved metro (A-screen-013). Najrān city is 0.0 km from itself.

## Exclusions and coverage

- **Yadamah** (centre, 4,983 per S-najran-002) and **Badr Al Janub** (centre, 2,709): below 5,000 (A-screen-002). Kept as governorate-centre coverage rows (rule 2) with `screened: false`. The governorate totals (16,160; 7,991) are not used as centre figures.
- **Al-Kharkhīr** (R1a settlement KSA-ST-01416, 3,277 grid): below 5,000, not a row. Its point lies at 18.85 N, 51.12 E, about 740 km from the Najrān-region centres, so its attribution to Sharūrah is a boundary or grid error (R1a control flag). Not used.
- **Settlements left out:** the other settlements of the R1a universe for Najrān are below 5,000 on both figures and are not rows.
- **Not in the R1a universe:** two Census 2010 cities above 5,000 (Hairat al-Salam, 5,820; Taslan, 5,284) are in the 2010 list but not in the R1a settlement universe or the 2022 primary 5,000+ export. Not added; see Needs judgement.

## Population provenance and the control total

- **Official, verified (6 rows):** Najrān, Sharūrah, Ḥubūnā, Khubāsh, Al Mishaliah, Al Wadī'ah: the GASTAT Census 2022 TA1 primary export, city 5,000+ (S-cp2-gastat-008). The relayed figures (S-cp2-gastat-001) agree on every row (0.0 % difference).
- **Official, secondary (2 rows):** Yadamah and Badr Al Janub: citypopulation.de's places 2,500+ table (S-najran-002), crediting GASTAT. `primary_to_find`: the GASTAT locality table.
- **Grid, unverified (5 rows):** Thār (8,030), Abā al-Sa'ud (11,474), Al Mikhlaf (6,853), Al Nukaysi (6,525), Al Urayisah (6,093). WorldPop 2020 (S-r1a-506) gap-fill from R1a. None has a second method, and none is in the GASTAT places 2,500+ table (S-najran-002) or the primary 5,000+ export. `tag_10k` is false for all five (A-screen-031/032). `tag_5k` is not gated and is true for all five.
- **Control total (A-screen-037):** the region's grid-filled population exceeds the residual by 5,347 (75,223 grid against a residual of 69,876; `runs/gastat/primary/control_total.csv`). Reporting only; nothing is corrected.
- **Record-only geo-verify estimates** (pilot GEO_VERIFY notes, reproduced in R2 by `screening.geo_verify.cli estimate` on the pilot register: buildings × occupancy and WorldPop): Thār 4,465 (band 1,314–10,245) and Badr Al Janub 4,128 (band 1,513–7,602); Yadamah has no building cluster. Both methods failed the 30 % back-test gate, so these are in `notes` only and never in `population`.

## Needs judgement (not resolved by the sweep)

1. **Khubāsh centre node.** The row uses the village node n8503374507 (17.54985, 44.74113); the governorate node n6774251958 is 55.5 km away. A-najran-003.
2. **Ḥubūnā centre node.** The row uses the town node n11871306300; the governorate node n6769844117 is 20.2 km away. A-najran-003.
3. **Najrān and Sharūrah centre figures.** The rows carry the city figures (381,431; 89,456), not the governorate totals (421,902; 100,199).
4. **Five grid-only towns at 5,000 or more** (Thār, Abā al-Sa'ud, Al Mikhlaf, Al Nukaysi, Al Urayisah). The GASTAT places 2,500+ table has no figure for any of them, so the grid may over-count, and the control total is +5,347. Decide whether they stay in the 5,000 sensitivity (tag_5k).
5. **Thār on the 5,000 line.** Its `tag_5k` rests on an uncorroborated grid figure (8,030); the record-only estimate (4,465) is below 5,000.
6. **Abā al-Sa'ud.** The grid figure (11,474) crosses 10,000 but is uncorroborated (`tag_10k` false). It flips only if a second method corroborates it within 30 %.
7. **Hairat al-Salam (5,820) and Taslan (5,284)** in the Census 2010 cities above 5,000 list are not in the R1a universe or the 2022 primary 5,000+ export. Are they GASTAT localities, and what are their 2022 figures? Not added.
8. **Al Wadī'ah border-crossing role** rests on a secondary snippet (S-najran-010) and no R1a economic node. Verify before use.
9. **Heritage role** (Hima cultural area, ~82 km from Najrān city and ~47 km from the Thār row) is attributed to the Najrān city row through R1a's nearest-town field (A-najran-005). merge-stage to decide whether Thār, a screened row, should carry it instead.
10. **Spelling and transliteration.** The OSM names for Abā al-Sa'ud, Al Mikhlaf, Al Nukaysi and Al Urayisah are Arabic only; the English names are the coordinator's. Khubāsh is spelled per the citypopulation list (OSM: Khubash).
11. **Terrain** is assumed for all rows (A-najran-001). A DEM class is needed before any terrain-dependent output.
12. **geo-verify CLI scope.** `screening.geo_verify.cli` reads only `cities/ksa/regions/pilot-*.parquet` (`REGISTERS`), so it does not process this register. The estimate was run on the pilot rows, not on these rows.

## Sources

- GASTAT primary exports (in the repository's data area): S-cp2-gastat-007 (governorates), S-cp2-gastat-008 (cities 5,000+), S-cp2-gastat-001 (relayed cross-check). Registered in `cities/ksa/sources.yaml`.
- Secondary: S-najran-001 (governorate table), S-najran-002 (places 2,500+), S-najran-003 (Saudipedia), S-najran-010 (border crossing). All are in `docs/sources/r2-najran.csv`.
- OSM: S-najran-004 (GCC extract, ODbL). Economic nodes: S-cp1-100, S-r1a-204, S-r1a-205, S-r1a-210, S-r1a-221, S-r1a-222 (R1a).
- Population gap-fill: S-r1a-506 (WorldPop 2020, 100 m, constrained and UN-adjusted; CC BY 4.0, S-r1a-508). Census reference: S-071.
- Landbridge: S-054 (line), S-062 (intermediate stops, no location).

## Validation performed

- `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/najran.parquet`: ok, 13 rows, 7 governorates.
- Parquet and CSV hold the same 13 rows (same `osm_id` order); the table above is generated from the Parquet.
- Every population carries `pop_source`, `pop_year` and `pop_type`; grid rows carry `pop_source_status: unverified`.
- Every economic role names an S- source (13 of 13).
- The seven governorate centres each have a row; the non-row settlements are checked to be below 5,000.

Screening input, not a forecast.
