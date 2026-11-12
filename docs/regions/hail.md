> **Document version:** docs/regions/hail.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_HAIL, track r2-hail) | Status: draft

# Region sweep: Ḥā'il (حائل), slug `hail` (REGION_HAIL, R2)

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.

Register: `cities/ksa/regions/hail.parquet` and `.csv` (17 rows). Validated with `uv run python -m screening.region_sweep validate --strict`, header `governorates_gastat: 9`, `governorates_listed: 9`. Access date for every source: 2026-10-31 (Asia/Riyadh) unless the source table says otherwise. The built script is `screening/sweeps/hail/build_register.py`; this document is written by `screening/sweeps/hail/write_doc.py` from the register.

## 1. Governorate count

- **GASTAT governorates in Ḥā'il: 9, reconciled.** The primary GASTAT Census 2022 TA1 governorate export (S-cp2-gastat-007) carries the nine names of the working list (S-073): Ḥā'il 498,575; Al-Ḥā'īṭ (Al Hait) 74,596; Baq'ā' (Baqa) 56,362; Ash-Shamlī 20,946; Simīrā' 19,563; As-Sulaymī 17,343; Mawqaq 16,835; Al-Ghazalah 12,767; Ash-Shanān (Ash Shinan) 29,419. The sum is **746,406**, equal to the Ḥā'il region total in S-hail-001, so the set is complete (S-hail-009, derived). The primary export has no region column, so the membership of each name in Ḥā'il is S-073 (secondary) checked by that sum.
- Every governorate has its centre as a row: Al-Ghazalah, Al-Ḥā'īṭ, As-Sulaymī, Ash-Shamlī, Ash-Shanān, Baq'ā', Mawqaq, Simīrā', Ḥā'il.
- Nationally, the primary table has 150 governorate rows; the working list has 152 (150 plus two flagged rows, Abanat and Al-Bayda, in Qassim and the Eastern Province). That discrepancy is for the coverage audit, not this sweep.
- The primary table also lists a governorate named Turubah (41,769) that is not one of the nine. The Ḥā'il Turubah is a town in the Baq'ā' governorate (see section 6).

## 2. Counts

| measure | count |
|---|---|
| rows in the register | 17 |
| governorate centres | 9 (2 of them below 5,000: Mawqaq, Simīrā', `screened: false`, kept for coverage) |
| rows with population ≥ 10,000 (`tag_10k`) | 4 (Ḥā'il; Baq'ā'; Ash-Shanān on a secondary figure; Al Malwi on a doubtful OSM tag) |
| rows with population ≥ 5,000 (`tag_5k`) | 15 |
| population type `grid` (WorldPop, unverified) | 5; of these ≥ 10,000: 0 (no grid row passes the 10k test, so no corroboration was needed; A-screen-031) |
| population source verified (GASTAT read) | 8 |
| population source secondary (relayed or OSM tag) | 4 |
| population source unverified (grid) | 5 |
| economic roles, each with a source | 5 (see section 5) |
| R1a settlement universe rows in the region | 650 |

## 3. Register table

Sorted by population. `pop source`: `S-cp2-gastat-008` = GASTAT Census 2022 primary city table; `S-hail-001` = citypopulation.de relayed (secondary); `S-r1a-506` = WorldPop 2020 grid (unverified); `S-hail-003` = OSM population tag. Road minutes: OSRM car profile, free flow, uncalibrated (S-r1a-809). Distances are straight-line (haversine) in the register (`dist_*_km`).

| # | name (AR) | name (EN) | governorate | centre | population (type, status) | pop source | tag 10k | tag 5k | nearest existing | road min | nearest metro (tier) | road min to metro | economic roles |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | حائل | Ha'il | Ḥā'il | Y | 448,623 (official, verified) | S-cp2-gastat-008 | Y | Y | sar-north-passenger:hail | 20.7 | Buraidah (2) | 161.6 | administrative (S-hail-006); airport (S-hail-006); industrial_city (S-r1a-204); university (S-hail-007) |
| 2 | بقعاء | Baqa | Baq'ā' | Y | 19,659 (official, verified) | S-cp2-gastat-008 | Y | Y | sar-north-passenger:hail | 74.3 | Buraidah (2) | 210.7 | none sourced |
| 3 | الملوي | Al-Malwi | Al-Ḥā'īṭ | N | 15,000 (derived, secondary) | S-hail-003 | Y | Y | hhr:madinah | 103.6 | Madinah (1) | 109.6 | none sourced |
| 4 | الشنان | Ash Shinan | Ash-Shanān | Y | 11,560 (official, secondary) | S-hail-001 | Y | Y | sar-north-passenger:hail | 60.2 | Buraidah (2) | 107.6 | none sourced |
| 5 | الشملي | Ash-Shamlī | Ash-Shamlī | Y | 9,163 (official, verified) | S-cp2-gastat-008 | N | Y | sar-north-passenger:hail | 149.7 | Madinah (1) | 259.9 | none sourced |
| 6 | تربة | Turubah | Baq'ā' | N | 8,590 (official, verified) | S-cp2-gastat-008 | N | Y | sar-north-passenger:hail | 159.2 | Buraidah (2) | 264.1 | none sourced |
| 7 | الحايط | Al Hayit | Al-Ḥā'īṭ | Y | 8,289 (official, verified) | S-cp2-gastat-008 | N | Y | hhr:madinah | 147.9 | Madinah (1) | 154.0 | none sourced |
| 8 | الأجفر | Al Ajfar | Baq'ā' | N | 7,518 (official, verified) | S-cp2-gastat-008 | N | Y | sar-north-passenger:hail | 131.1 | Buraidah (2) | 156.4 | none sourced |
| 9 | السليمي | As Sulaymi | As-Sulaymī | Y | 6,775 (grid, unverified) | S-r1a-506 | N | Y | sar-north-passenger:hail | 144.8 | Buraidah (2) | 231.4 | none sourced |
| 10 | عيال عبيد | Ayal Obaid | Al-Ḥā'īṭ | N | 6,561 (grid, unverified) | S-r1a-506 | N | Y | hhr:madinah | 152.9 | Madinah (1) | 159.0 | none sourced |
| 11 | أسبطر | Asbatr | Ash-Shamlī | N | 6,344 (grid, unverified) | S-r1a-506 | N | Y | sar-north-passenger:hail | 139.5 | Madinah (1) | 275.7 | none sourced |
| 12 | ضريغط | Dhurayghit | Al-Ḥā'īṭ | N | 5,809 (grid, unverified) | S-r1a-506 | N | Y | sar-north-passenger:hail | 161.9 | Madinah (1) | 215.3 | none sourced |
| 13 | جبة | Jubbah | Ḥā'il | N | 5,622 (official, verified) | S-cp2-gastat-008 | N | Y | sar-north-passenger:hail | 77.3 | Buraidah (2) | 217.8 | heritage (S-hail-005) |
| 14 | الغزالة | Al Ghazalah | Al-Ghazalah | Y | 5,592 (official, verified) | S-cp2-gastat-008 | N | Y | sar-north-passenger:hail | 86.3 | Buraidah (2) | 215.1 | none sourced |
| 15 | الودي | Al Wudayy | Ḥā'il | N | 5,323 (grid, unverified) | S-r1a-506 | N | Y | sar-north-passenger:hail | 34.7 | Buraidah (2) | 171.6 | none sourced |
| 16 | موقق | Mawqaq | Mawqaq | Y | 3,148 (official, secondary) | S-hail-001 | N | N | sar-north-passenger:hail | 76.5 | Buraidah (2) | 213.4 | none sourced |
| 17 | سميراء | Simira' | Simīrā' | Y | 3,105 (official, secondary) | S-hail-001 | N | N | sar-north-passenger:hail | 157.1 | Buraidah (2) | 202.6 | none sourced |

## 4. Exclusions

- **Screened false (kept for coverage):** Mawqaq (3,148, secondary) and Simīrā' (3,105, secondary): governorate centres below 5,000 with no sourced economic role.
- **Not written (below 5,000 and not a governorate centre):** 633 of the 650 universe rows for the region are not in the register: hamlet 422, village 209, town 2. They are below the 5,000 sensitivity threshold (A-screen-002), so they are not tagged. The largest excluded resolved population is 4,688. 6 R1a universe rows carry a grid or OSM figure that the relayed GASTAT table (S-hail-001) replaces by name and governorate (Al Hulayfah Assofla, Al Ruwda, Al Qa`id, Munifat al Qa`id, An Nisiyah, Al Khuttah); the relayed figure takes precedence (official > derived > grid), and those below 5,000 are not written. No other excluded row has a grid or OSM figure at or above 5,000 (checked in the builder). None has a sourced economic role.
- No duplicate was removed. Ash-Shanān's census figure is the S-hail-001 figure; its universe row is kept once.

## 5. Economic roles

Roles were assessed against the 168 R1a economic nodes (`cities/ksa/zones/economic_nodes.parquet`), five of which are located in Ḥā'il: the Ḥā'il Regional Airport (GACA, S-cp1-100), the Ḥā'il Industrial City (MODON, S-r1a-204), the Rock Art in the Hail Region (UNESCO, S-hail-005 and S-r1a-205, Wikidata position at region level), the University of Ḥā'il (S-hail-007, S-r1a-221), and the Az Zabirah bauxite mine (Ma'aden; the region is unverified, so no row is assigned; S-r1a-236). The roles in the register are the ones tied to a town: Ḥā'il city (administrative, airport, industrial city, university) and Jubbah (heritage, placed at Jabal Umm Sinman; S-hail-005). Every other town has no sourced role, and its row says so in `notes`.

## 6. Conflicts and decisions

- **Ash-Shanān 11,560 vs Alshazalah 11,560.** The primary city table has `Alshazalah` at 11,560 (S-cp2-gastat-008), which may be the same place; the crosswalk (`screening/gastat_crosswalk.yaml`) leaves it unmatched and logs the conflict. The row stays on S-hail-001 (secondary), so its ≥ 10k status depends on a secondary figure until the match is decided.
- **Relayed figures beat grid and OSM figures.** Al-Khuṭah (3,355), Al-Ḥalīfah as-Suflā (4,151) and Al-Qā'id (2,913) are in the relayed S-hail-001 table (checked live on the page, 31 Oct 2026). The earlier register used their grid or OSM figures (9,636, 8,990, 5,523) and tagged them at 5k; that was a precedence error, now fixed. They are not written.
- **Turubah.** The Makkah Turubah (28,279, S-cp2-gastat-008) is a different place. The Ḥā'il Turubah row takes `Turba` (8,590, primary); the OSM tag (5,134) conflicts with the census figure, and the census figure is used.
- **Al Ajfar.** Matched by the crosswalk to `Alajfir` (7,518, primary; KSA-ST-00991).
- **Al-Ḥā'īṭ.** OSM spells the node `Al Hayit` (الحايط); matched by coordinates and name, primary 8,289.
- **Population type of the R1a universe.** The 634 grid rows in the universe are `unverified`; the register keeps the grid figure only for towns that have no tabulated or relayed figure, and tags it `grid`. No grid figure is treated as a census figure.
- **Geo-verify.** The pilot GEO_VERIFY estimates for Ash-Shanān, Mawqaq and Simīrā' are carried in `notes` as record-only values (their back-test is above the 30 % gate). They were not re-run in this track: the WorldPop raster and footprint tiles are not in the worktree, and the prompt's disk gate rules out the downloads. Al Malwi and Al Qa'id (OSM tags) have no estimate.

## 7. Needs judgement

1. **Al Malwi (الملوي), 15,000, OSM village tag dated 1950, governorate Al-Ḥā'īṭ at 25.3 N.** It alone passes 10k among the non-centre rows. The tag is doubtful and the position is at the southern edge of the region; decide whether the row stays `tag_10k: true` (A-hail-002), and whether its governorate membership is right.
2. **Ash-Shanān 11,560: match Alshazalah (primary) or keep the secondary figure.** The crosswalk says unmatched; the value coincides.
3. **Grid-only towns and the R1a grid figure for As-Sulaymī.** Ayal Obaid (6,561), Asbatr (6,344), Dhurayghit (5,809), Al Wudayy (5,323) and As-Sulaymī (6,775, the centre; the census places table does not tabulate it) have no GASTAT figure; their figures are the R1a WorldPop grid, not census figures, and they sit only in the 5k sensitivity. Al Malwi (item 1) is the only ≥ 10k row on an OSM tag.
4. **Terrain class** is not measured (A-hail-001); the regional description (S-hail-008) is not a row class.
5. **Membership at the region edge (A-hail-003).** OSM polygons place Al Hulayfah Assofla at 25.99 N, 40.8 E and Al Hayit at 25.99 N, 40.5 E in the Ḥā'il region. The locations are plausible for Al-Ḥā'īṭ but need a check against GASTAT's boundary list.

## 8. Sources

Governorate and population: S-cp2-gastat-007, S-cp2-gastat-008, S-hail-001 (secondary), S-hail-009 (derived sum), S-073 (working list), S-cp2-gastat-001 (cross-check, not used as the value of record). Grid: S-r1a-506 (WorldPop 2020). OSM positions and place tags: S-hail-003, S-r1a-210. Road skims: S-r1a-809. Rail: S-017 (SAR North, existing), S-001 (HHR, existing), S-054 (Landbridge, announced; committed layer, stations unlocated). Economic roles: S-hail-005, S-hail-006, S-hail-007, S-hail-008, S-cp1-100, S-r1a-204, S-r1a-205, S-r1a-221, S-r1a-236. The source index is `docs/sources/index.csv`; the new row is `docs/sources/r2-hail.csv`.

## 9. Layers

Rail layers: the existing lines (SAR North passenger, HHR) are existing; the Landbridge stops are committed (announced/planned, unlocated), and no committed line is called existing. The roads and the distances are straight-line or free-flow estimates, not timetables.
