> **Document version:** docs/regions/qassim.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_QASSIM) | Status: draft

# Qassim (القصيم) region sweep, slug `qassim`

**Screening input, not a forecast.** Synthetic demand, uncalibrated: scenario comparison, not a forecast.

Built by `screening/sweeps/qassim/build.py` from the R1a settlement universe (`cities/ksa/zones/settlements.parquet`), the GASTAT primary Census 2022 exports and the R1a economic nodes. Register: `cities/ksa/regions/qassim.parquet` (CSV mirror `qassim.csv`); validated with `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/qassim.parquet`. Source ids `S-cp2-gastat-*`, `S-r1a-*`, `S-cp1-*` are in `docs/sources/index.csv`; `S-qassim-*` are in `docs/sources/r2-qassim.csv`.

## 1. Governorate count (rule 2)

| source | count | status |
|---|---|---|
| GASTAT primary governorate export (S-cp2-gastat-007; 150 rows) | 13 Qassim governorates named in the table; their 2022 totals sum to 1,336,179 | verified (read from the export) |
| GASTAT TA9 region table, 2022 (S-cp2-gastat-003) | Al Qaseem 2022 = 1,336,179 | verified (read from the CSV) |
| DataPulse relayed governorate table (S-cp2-gastat-001) | same names and values on the 13 governorates (cross-check; not value of record) | secondary |

`governorates_gastat` = 13 and `governorates_listed` = 13. GASTAT's exports do not state a Qassim governorate count; the 13 is derived from the 13 names whose sum equals the TA9 region total exactly. Equal, with no discrepancy to record. The 13 are: Buraydah, Unayzah, Ar Rass, Al Bukayriyah, Al Midhnab, Al Badai, Riyadh Al Khabra, Al Asyah, Ash Shimasiyah, Uyun Al Jiwa, Uqlat As Suqur, Dariyah, An Nabhaniyah.

Abanat (R1a sub-locality rows, population 0 in the universe, in An Nabhaniyah) is not a governorate and is not a row: the 13 governorates reconcile to the region total without it.

## 2. Counts

| measure | value |
|---|---|
| rows in the register | 35 (13 governorate centres, 22 other rows) |
| screened rows / excluded rows | 34 / 1 |
| rows with tag_10k = true (≥ 10,000) | 10 (all GASTAT primary, official) |
| rows with tag_5k = true (≥ 5,000; sensitivity) | 28 (official 19, grid 9) |
| grid-only rows ≥ 10,000 gated out (`grid-only population, uncorroborated`) | 4 |
| rows with no 2022 population (not used; see §5) | 6 |
| economic roles, rows with ≥ 1 sourced role / total roles | 3 / 6 |
| population basis: official / grid / none | 19 / 10 / 6 |

Population provenance: an official figure is the GASTAT primary city export (S-cp2-gastat-008, read directly: `verified`); a grid figure is the WorldPop 2020 gap-fill (S-r1a-506, `unverified`, A-screen-031). No `secondary` figure is used. No corroboration method was run for any grid row (`pop_corroboration` null), so no grid row passes the 10,000 test.

## 3. Coverage

The R1a universe holds 575 Qassim settlements. The register holds the 13 governorate centres, every settlement at or above 5,000 in the universe (any population basis), and the rows listed in §5. The other 540 settlements are not rows: they are below the 5,000 sensitivity threshold (A-screen-002), and none is a governorate centre.

Completeness caveat: seven primary cities of 5,000 or more could not be placed in any region (table in §6). Any of them could be in Qassim, so the list of Qassim towns at or above 5,000 is complete only conditionally on that list.

## 4. Register table

Distances: `dist_existing_km` = great circle to the nearest intercity station (A-r1a-008; here SAR North passenger, al-Qassim); `road_min_existing` = OSRM car, MLD, 5 nearest (A-r1a-027). `dist_committed_km` = to the Landbridge proxy station Dawadmi (unlocated; committed layer as in R1a). `dist_metro_km` = to Buraidah (approved tier-2 metro). Population per row is in the register; roles are sourced in the register.

| name (EN) | name (AR) | governorate | centre | population | basis | ≥10k | ≥5k | existing km (road min) | committed km (road min) | metro km (road min) | roles | screened / exclusion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Buraydah | بريدة | Buraydah | yes | 571,169 | official / verified | true | true | 21.5 (21) | 208 (188) | 0.0 (0) | airport (S-cp1-100); industrial_city (S-r1a-204); university (S-r1a-221); administrative (S-qassim-004) | yes |
| Unaizah | عنيزة | Unayzah | yes | 183,319 | official / verified | true | true | 45.9 (44) | 182 (165) | 26.8 (24) | tourism (S-qassim-009) | yes |
| Ar Rass | الرس | Ar Rass | yes | 107,902 | official / verified | true | true | 90.9 (83) | 177 (172) | 69.5 (66) | agriculture (S-qassim-009) | yes |
| Al Bada'i` | البدائع | Al Badai | yes | 48,474 | official / verified | true | true | 66.5 (64) | 178 (187) | 45.0 (47) | none sourced | yes |
| Albukayriyah | البكيرية | Al Bukayriyah | yes | 43,229 | official / verified | true | true | 57.1 (46) | 198 (198) | 36.6 (31) | none sourced | yes |
| Al Mithnab | المذنب | Al Midhnab | yes | 33,341 | official / verified | true | true | 71.6 (63) | 153 (140) | 58.1 (49) | none sourced | yes |
| Riyad Al Khabra | رياض الخبراء | Riyadh Al Khabra | yes | 25,588 | official / verified | true | true | 72.1 (60) | 192 (197) | 51.5 (45) | none sourced | yes |
| Al Jiwa | عيون الجواء | Uyun Al Jiwa | yes | 15,619 | official / verified | true | true | 45.2 (46) | 235 (210) | 37.9 (30) | none sourced | yes |
| Uglat Asugour | عقلة الصقور | Uqlat As Suqur | yes | 9,717 | official / verified | false | true | 202.9 (152) | 265 (279) | 185.8 (137) | none sourced | yes |
| Ash Shimasiyah | الشماسية | Ash Shimasiyah | yes | 5,719 | official / verified | false | true | 25.8 (42) | 203 (192) | 29.1 (32) | none sourced | yes |
| Dariyah | ضرية | Dariyah | yes | 5,485 | official / verified | false | true | 229.4 (186) | 149 (156) | 208.0 (171) | none sourced | yes |
| An Nabhaniyah | النبهانية | An Nabhaniyah | yes | 5,221 | official / verified | false | true | 124.1 (94) | 202 (208) | 104.5 (79) | none sourced | yes |
| Al Asyah | الأسياح | Al Asyah | yes | 2,318 | grid / unverified | false | false | 35.5 (37) | 257 (231) | 56.5 (50) | none sourced | yes |
| القبعيه | القبعيه | Al Badai |  | 29,927 | grid / unverified | false | true | 69.6 (69) | 171 (180) | 48.3 (52) | none sourced | yes (kept; grid-only population, uncorroborated) |
| Ash Shihiyah | الشيحية | Al Bukayriyah |  | 25,648 | grid / unverified | false | true | 55.0 (59) | 210 (215) | 37.2 (44) | none sourced | yes (kept; grid-only population, uncorroborated) |
| Dulay` Rashid | ضليع رشيد | An Nabhaniyah |  | 17,933 | grid / unverified | false | true | 166.1 (162) | 191 (238) | 145.4 (147) | none sourced | yes (kept; grid-only population, uncorroborated) |
| Al Khabra | الخبراء | Buraydah |  | 16,906 | official / verified | true | true | 66.2 (56) | 191 (200) | 45.2 (41) | none sourced | yes |
| Qibah | قبة | Al Asyah |  | 11,506 | official / verified | true | true | 103.8 (104) | 323 (298) | 124.1 (117) | none sourced | yes |
| Al Badai al Ulya | البدائع العليا | Al Badai |  | 10,710 | grid / unverified | false | true | 70.8 (65) | 177 (186) | 49.2 (48) | none sourced | yes (kept; grid-only population, uncorroborated) |
| Nab'ah | نبعة | Al Midhnab |  | 9,981 | grid / unverified | false | true | 74.2 (71) | 150 (142) | 60.2 (57) | none sourced | yes |
| Al Bosor | البصر | Buraydah |  | 7,345 | grid / unverified | false | true | 32.2 (30) | 206 (190) | 11.7 (15) | none sourced | yes |
| Al Mulayda | المليداء | Buraydah |  | 6,967 | official / verified | false | true | 36.5 (39) | 212 (200) | 19.1 (23) | none sourced | yes |
| Al Hamjah | الهمجة | An Nabhaniyah |  | 6,874 | grid / unverified | false | true | 150.8 (136) | 173 (214) | 129.6 (121) | none sourced | yes |
| Ayn Ibn Fuhayd | عين ابن فهيد | Al Asyah |  | 6,548 | official / verified | false | true | 33.5 (34) | 254 (228) | 54.7 (47) | none sourced | yes |
| Dukhnah | دخنة | Ar Rass |  | 6,354 | official / verified | false | true | 134.6 (118) | 124 (117) | 113.7 (101) | none sourced | yes |
| Al Quwarah | القوارة | Buraydah |  | 5,646 | official / verified | false | true | 69.9 (81) | 270 (246) | 70.9 (65) | none sourced | yes |
| قصر بن عقيل | قصر بن عقيل | Buraydah |  | 5,617 | official / verified | false | true | 102.3 (92) | 181 (181) | 81.3 (76) | none sourced | yes |
| الروغاني | الروغاني | Unayzah |  | 5,507 | grid / unverified | false | true | 41.3 (42) | 187 (170) | 21.9 (22) | none sourced | yes |
| Diras | ضراس | Buraydah |  | 5,055 | grid / unverified | false | true | 28.3 (26) | 209 (187) | 8.9 (10) | none sourced | yes |
| Ad Dilaymiyah | الدليمية | Buraydah |  | null | none | false | false | 96.5 (77) | 204 (204) | 77.3 (62) | none sourced | yes |
| Adh Dhibiyah | الذيبية | Buraydah |  | null | none | false | false | 106.4 (92) | 211 (219) | 87.9 (76) | none sourced | yes |
| Al Fuwayliq | الفويلق | Al Bukayriyah |  | null | none | false | false | 83.6 (99) | 245 (263) | 72.6 (83) | none sourced | yes |
| KHUSAIBAH | خصيبة | Al Asyah |  | null | none | false | false | 43.6 (48) | 266 (242) | 63.7 (61) | none sourced | yes |
| Wadi Al nakhil | وادي النخيل | An Nabhaniyah |  | null | none | false | false | 173.3 (172) | 188 (247) | 152.4 (156) | none sourced | yes |
| Ḍariyah | ضرية | Dariyah |  | null | none | false | false | 230.2 (216) | 188 (209) | 208.9 (201) | none sourced | no: duplicate of the Dariyah governorate centre (KSA-ST-00478): boundary-relation centroid, not a settlement point; the official 5,485 is carried by the place node (A-qassim-004) |

## 5. Exclusions and rows without a 2022 population

- Dariyah boundary centroid (KSA-ST-07370, OSM relation 12406851): excluded as a duplicate of the Dariyah centre place node (KSA-ST-00478), which carries the official 5,485 (A-qassim-004).
- Five OSM-tagged towns with no 2022 figure (A-qassim-003): Khusaibah, Wadi al Nakhil, Ad Dilaymiyah, Al Fuwayliq, Adh Dhibiyah. Kept with population null; the stale OSM values are recorded in the notes, with the record-only GEO_VERIFY estimates (below).
- Four grid-only towns of 10,000 or more are kept (screened) with tag_10k false and `grid-only population, uncorroborated`.

GEO_VERIFY no-pop step (31 Oct 2026, `screening/sweeps/qassim/geo_nopop.py`, seed 1): record-only, not used in `population`; the buildings and grid estimators are above the 30 % back-test gate (`docs/geo-verify.md`). Values are in each row's notes.

## 6. Unplaced primary cities (completeness)

Primary cities of 5,000 or more with no R1a settlement and no region in the export (the R1a matcher left them ambiguous; they are not in this register). Any of them could be a Qassim town; see merge-stage item 5.

| primary city name (as exported) | 2022 total |
|---|---|
| Alqaruh | 8,656 |
| Albadie Walqarfi | 8,623 |
| Almansuruh | 7,622 |
| Alqarin | 7,339 |
| Alshaquh Aleulya | 5,449 |
| Aleurafa' | 5,432 |
| Alkhadra' | 5,861 |

Hand joins made in this sweep (not the R1a matcher): Qasirabin Eaqil (5,617) to KSA-ST-01645; Dariyah (5,485) to the place node KSA-ST-00478.

## 7. Sources

- GASTAT Census 2022 primary TA1 exports: governorates (S-cp2-gastat-007), cities of 5,000 or more (S-cp2-gastat-008), TA9 region table (S-cp2-gastat-003); relayed DataPulse cross-check (S-cp2-gastat-001).
- OpenStreetMap, ODbL (S-r1a-210): element ids and coordinates; WorldPop 2020 100 m constrained, UN-adjusted, CC BY 4.0 (S-r1a-506, S-r1a-508).
- R1a settlement universe, road skims and line distances (S-qassim-010); SAR North passenger line status (S-qassim-005, S-qassim-007); Landbridge (S-054).
- Economic roles: GACA airports (S-cp1-100), MODON industrial cities (S-r1a-204), Qassim University (S-r1a-221); administrative seat from the Wikipedia article (S-qassim-004, secondary); tourism and agriculture from unopened search summaries (S-qassim-009, unverified).
- Access date for the local GASTAT files: 31 Oct 2026 (`data/ksa/tables/gastat/README.md`); hashes in `cities/ksa/sources.yaml`.

## 8. Facts: verification status

- Verified (read from the GASTAT export or the R1a output): the 13 governorate totals and the region total; the 19 official rows (17 matched by value by R1a, Dariyah re-pointed from the boundary relation to its place node, and Qasr Bin Aqil hand-joined: see merge-stage items 1 and 2).
- Secondary: governorate names as relayed; the administrative seat (Wikipedia); OSM ids and coordinates (ODbL, extract 14 Oct 2026).
- Unverified: WorldPop grid figures (all grid rows); economic roles for Unayzah and Ar Rass (S-qassim-009); terrain (assumed).

## 9. Needs judgement (not resolved by guessing)

1. Dariyah centre (A-qassim-004): the official 5,485 is carried by place node KSA-ST-00478 (lat 24.72), not by the boundary centroid KSA-ST-07370 (24.93 N, 42.58 E); the two are 42 km apart. Confirm the place and its coordinates.
2. Qasr Bin Aqil (A-qassim-002): primary 'Qasirabin Eaqil' (5,617) is joined by hand to OSM village KSA-ST-01645 (WorldPop 16,608); confirm the identity. Tag_10k is false either way.
3. Stale OSM population tags (A-qassim-003): Khusaibah (10,000, no date), Wadi al Nakhil (8,000, no date), Ad Dilaymiyah (5,862), Al Fuwayliq (5,620) and Adh Dhibiyah (5,068) equal Census 2010 values or have no date, and none is in the GASTAT 2022 table of cities of 5,000 or more. Kept with population null; decide whether to treat them as below 5,000 in 2022.
4. Grid-only towns of 10,000 or more (four rows, uncorroborated, tag_10k false): Al-Qabaah 29,927, Ash Shihiyah 25,648, Dulay` Rashid 17,933, Al Badai al Ulya 10,710. No second method was run (no 2010 match in the Census 2010 list). Decide whether to run a corroboration method for them.
5. Unplaced primary cities (no R1a settlement; the export has no region, and the matcher found no unique name): Alqaruh 8,656; Albadie Walqarfi 8,623; Almansuruh 7,622; Alqarin 7,339; Alshaquh Aleulya 5,449; Aleurafa' 5,432; Alkhadra' 5,861. Any of them could be in Qassim: the completeness claim is conditional on this list.
6. Landbridge layer (A-qassim-005): R1a labels it committed (the nearest committed line for every Qassim row), while cities/ksa/lines/landbridge.yaml has status announced. Rule 5 says planned lines are announced/planned. Confirm the layer before any commitment-based screening.
7. Unverified economic roles (A-qassim-006): tourism for Unayzah and agriculture for Ar Rass come from an unopened search summary (S-qassim-009). Verify at source or drop before screening.
8. Terrain (A-qassim-001): every row is flat_desert by assumption. The Ad Dahna dunes and the escarpment edge may apply; a DEM read is pending.
9. Economic roles not assigned: Qassim MODON Second Industrial City and the Qassim MODON Oasis (unlocated), Ba'itha bauxite mine (no settlement row in the register). Confirm the host towns.
