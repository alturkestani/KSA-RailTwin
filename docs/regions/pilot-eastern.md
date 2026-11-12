> **Document version:** docs/regions/pilot-eastern.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_EASTERN) | Status: draft

# Eastern Province (المنطقة الشرقية): pilot register (slug `eastern`)

**Screening input, not a forecast.** Coarse pilot sweep of the Eastern Province to test the `RegionRow` schema. Not the full register (`REGION_EASTERN`, milestone R2). Registers: `cities/ksa/regions/pilot-eastern.parquet` and `.csv` (22 rows; same rows, same order). Raw extracts are stored under `data/ksa/regions-pilot/` (gitignored) and registered in `cities/ksa/sources.yaml`.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. No modelled output appears in this file.

## 1. Governorate count (governorates_gastat vs governorates_listed)

| item | value | source |
|---|---|---|
| `governorates_gastat` | **null: not verified.** GASTAT's governorate list was not reached: portal.saudicensus.sa did not resolve on 30 Oct 2026. | S-072, S-090 (existing) |
| `governorates_listed` | **13** rows (12 census governorates and the flagged Al-Bayda row, E18) | this register |
| Count in secondary sources | 13 including Al-Bayda (Saudipedia Arabic: 12 named plus the Dammam seat); 12 (citypopulation.de census table, which lists the same 12 without Al-Bayda) | S-eastern-003; S-eastern-001 |

**Discrepancy, flagged with both sources:** Al-Bayda is in the Arabic sources (S-eastern-003, and the Arabic Wikipedia list in docs/gastat-regions.md) but absent from the census governorate table (S-eastern-001). Evidence for 12 census units: the 12 census governorate rows sum exactly to the regional total of 5,125,254 (S-eastern-001), so there is no room for a 13th census governorate. Not decided. See Needs judgement, item 1.

## 2. Census 2022 governorate rows (regional context; not register rows)

| governorate (EN / AR) | population 2022 (S-eastern-001) | note |
|---|---|---|
| Ad-Dammām / الدمام | 1,532,326 | seat |
| Al-'Aḥsā' / الأحساء | 1,104,267 | includes Hofuf (E02) |
| Al-Khubar / الخبر | 658,550 | |
| Al-Qaṭīf / القطيف | 552,442 | |
| Al-Jubaīl / الجبيل | 505,162 | |
| Ḥafar al-Bāṭin / حفر الباطن | 467,007 | |
| Abqaīq / بقيق | 64,632 | |
| An-Na'īryah / النعيرية | 63,815 | |
| R'ās Tanūrah / رأس تنورة | 62,314 | |
| Al-Khafjī / الخفجي | 84,316 | |
| Qaryat al-'Ulyā / قرية العليا | 21,788 | |
| Al-'Udayd / العديد | 8,635 | |
| Al-Bayḍā / البيضاء | not in the census table | see §1 |
| **Sum of the 12 rows** | **5,125,254** | equals the regional total (S-eastern-001) |

## 3. Register (22 rows)

ID = row order (`RegionRow` has no id field). `pop_type` is `official` because the schema allows only official, derived or grid; the value is GASTAT Census 2022 as republished by citypopulation.de, and the source row S-eastern-001 is marked secondary (Needs judgement, item 2). Distances are great-circle (haversine) to station points, not alignments (§7). Roles are only the schema's enumerated roles; anything else is in §8.

| ID | name (EN / AR) | governorate | centre | population (2022) | ≥50k | pilot sample | dist. to existing station (km), nearest | dist. to metro (km), nearest | economic roles (source) | screened / exclusion |
|---|---|---|---|---|---|---|---|---|---|---|
| E01 | Dammam / الدمام | Ad-Dammām | yes | 1,386,166 (official, S-eastern-001) | yes | no | 3.7 (Dammam station) | 0.0 (Dammam–Khobar–Dhahran (Dammam node)) | port (S-eastern-007); airport (S-eastern-012) | yes |
| E02 | Hofuf (Al-Hufuf–Al-Mubarraz) / الهفوف والمبرز | Al-Ahsa | yes | 729,606 (official, S-eastern-001) | yes | no | 2.6 (Hofuf station) | 116.1 (Dammam–Khobar–Dhahran (Dhahran node)) | heritage (S-eastern-006); agriculture (S-eastern-006) | yes |
| E03 | Jubail / الجبيل | Al-Jubaīl | yes | 474,679 (official, S-eastern-001) | yes | no | 80.8 (Dammam station) | 77.0 (Dammam–Khobar–Dhahran (Dammam node)) | industrial_city (S-eastern-008) | yes |
| E04 | Khobar / الخبر | Al-Khubar | yes | 409,549 (official, S-eastern-001) | yes | no | 13.7 (Dammam station) | 0.0 (Dammam–Khobar–Dhahran (Khobar node)) | — | yes |
| E05 | Hafar al-Batin / حفر الباطن | Ḥafar al-Bāṭin | yes | 387,096 (official, S-eastern-001) | yes | no | 427.6 (Riyadh station) | 428.5 (Riyadh (city node)) | — | yes |
| E06 | Ath-Thuqbah / الثقبة | Al-Khubar | no | 248,888 (official, S-eastern-001) | yes | no | 16.6 (Dammam station) | 3.5 (Dammam–Khobar–Dhahran (Khobar node)) | — | yes |
| E07 | Dhahran / الظهران | Ad-Dammām | no | 143,936 (official, S-eastern-001) | yes | no | 12.6 (Dammam station) | 0.0 (Dammam–Khobar–Dhahran (Dhahran node)) | university (S-eastern-009); military (S-eastern-009) | yes |
| E08 | Tarout / تاروت | Al-Qaṭīf | no | 117,646 (official, S-eastern-001) | yes | no | 19.8 (Dammam station) | 16.3 (Dammam–Khobar–Dhahran (Dammam node)) | — | yes |
| E09 | Qatif / القطيف | Al-Qaṭīf | yes | 87,332 (official, S-eastern-001) | yes | no | 20.3 (Dammam station) | 16.5 (Dammam–Khobar–Dhahran (Dammam node)) | — | yes |
| E10 | Saihat / سيهات | Al-Qaṭīf | no | 84,818 (official, S-eastern-001) | yes | no | 11.1 (Dammam station) | 7.5 (Dammam–Khobar–Dhahran (Dammam node)) | — | yes |
| E11 | Khafji / الخفجي | Al-Khafjī | yes | 78,691 (official, S-eastern-001) | yes | no | 275.8 (Dammam station) | 272.1 (Dammam–Khobar–Dhahran (Dammam node)) | border_crossing (S-eastern-005) | yes |
| E12 | Rahimah / رحيمة | R'ās Tanūrah | no | 57,030 (official, S-eastern-001) | yes | no | 34.1 (Dammam station) | 30.8 (Dammam–Khobar–Dhahran (Dammam node)) | — | yes |
| E13 | Abqaiq (Buqayq) / بقيق | Abqaīq | yes | 45,032 (official, S-eastern-001) | no | yes | 0.6 (Abqaiq station) | 60.4 (Dammam–Khobar–Dhahran (Dhahran node)) | — | yes |
| E14 | An-Nu'ayriyah / النعيرية | An-Na'īryah | yes | 40,023 (official, S-eastern-001) | no | no | 201.7 (Dammam station) | 198.1 (Dammam–Khobar–Dhahran (Dammam node)) | — | yes |
| E15 | Qaryat al-'Ulyā / قرية العليا | Qaryat al-'Ulyā | yes | 10,961 (official, S-eastern-001) | no | no | 265.8 (Abqaiq station) | 268.9 (Dammam–Khobar–Dhahran (Dammam node)) | — | yes |
| E16 | Ras Tanura / رأس تنورة | R'ās Tanūrah | yes | — | no | no | 33.6 (Dammam station) | 30.3 (Dammam–Khobar–Dhahran (Dammam node)) | port (S-eastern-011) | yes |
| E17 | Al-Udayd / العديد | Al-'Udayd | yes | — | no | no | 204.6 (Hofuf station) | 224.1 (Dammam–Khobar–Dhahran (Khobar node)) | — | yes |
| E18 | Al-Bayda / البيضاء | Al-Bayḍā | no | — | no | no | 5.3 (Abqaiq station) | 59.6 (Dammam–Khobar–Dhahran (Dhahran node)) | — | no: Governorate status conflicting (Eastern Province list: 13 with Al-Bayda in Saudipedia Arabic and Wikipedia Arabic; 12 in citypopulation.de, S-eastern-001). Centre not located: OSM candidate is by name only (several 'Al Bayda' nodes). Population unverified. |
| E19 | Al-Oyun / العيون | Al-'Aḥsā' | no | 35,226 (official, S-eastern-001) | no | yes | 24.6 (Hofuf station) | 94.6 (Dammam–Khobar–Dhahran (Dhahran node)) | — | yes |
| E20 | Al-Jubail (Al-Ahsa governorate) / الجبيل | Al-'Aḥsā' | no | 9,994 (official, S-eastern-001) | no | yes | 9.6 (Hofuf station) | 109.0 (Dammam–Khobar–Dhahran (Dhahran node)) | — | yes |
| E21 | Al-Qaisumah / القيصومة | Ḥafar al-Bāṭin | no | 27,307 (official, S-eastern-001) | no | yes | 411.4 (Riyadh station) | 412.4 (Riyadh (city node)) | — | yes |
| E22 | King Khalid Military City / مدينة الملك خالد العسكرية | Ḥafar al-Bāṭin | no | 25,356 (official, S-eastern-001) | no | yes | 389.2 (Riyadh station) | 389.6 (Riyadh (city node)) | military (S-eastern-001) | yes |

## 4. Towns at or above 50,000 (threshold_50k, derived here)

`RegionRow` has `tag_10k` and `tag_5k` only, so the 50,000 tag lives in this document. Twelve rows meet it: E01 Dammam (1,386,166), E02 Hofuf (729,606), E03 Jubail (474,679), E04 Khobar (409,549), E05 Hafar al-Batin (387,096), E06 Ath-Thuqbah (248,888), E07 Dhahran (143,936), E08 Tarout (117,646), E09 Qatif (87,332), E10 Saihat (84,818), E11 Khafji (78,691), E12 Raḥīmah (57,030). Raḥīmah is probably part of the Ras Tanura urban area (Needs judgement, item 3). Ras Tanura's own population is not published in the sources consulted, so it cannot be tested against the 50,000 threshold.

## 5. Pilot sample (5,000 to 50,000; `pilot_sample: true`; 5 rows)

Stratified across distance to the existing East line (near: under 25 km; far: over 100 km) and a sourced economic role. Quadrants covered: near, no role (E19); edge case near, no role (E20); far, no role (E21); far, with a sourced role (E22); plus the centre edge case E13. Near with a sourced enum role: **not represented** in this pilot. Abqaiq (E13) is near but its role (oil processing) has no enum value.

- **E13 Abqaiq (governorate centre, 45,032): edge case.** The centre is smaller than the non-centre town Raḥīmah (57,030) in the same region, and it is 0.6 km from the East line station. Tests the centre-vs-town rule.
- **E19 Al-Oyun (35,226): near (24.6 km to Hofuf station), no sourced role.**
- **E20 Al-Jubail, Al-Ahsa governorate (9,994): edge case.** It has the same name as the Jubail centre (E03) but sits in another governorate, and OSM tags it `place=neighbourhood`, not a town. Near Hofuf (9.6 km), no sourced role.
- **E21 Al-Qaisumah (27,307): far (411 km to Riyadh station, the nearest existing station), no sourced role.** Hafar al-Batin governorate.
- **E22 King Khalid Military City (25,356): far (389 km to Riyadh station), role military (S-eastern-001 census row, "Military Institution").** Edge case: a military settlement, not a civil town (Needs judgement, item 9).

## 6. Exclusions and screening status

- **E18 Al-Bayda: `screened = false`.** Governorate status conflicting (§1); centre not located. The OSM candidate (`place=locality`, Abqaiq governorate) was matched by name only; several OSM objects named "Al Bayda'" exist. Population unverified.
- No other row is excluded. Rows with `population = null` (E16 Ras Tanura, E17 Al-Udayd, E18 Al-Bayda) must not be treated as zero by the funnel.
- Towns inside the Dammam–Khobar–Dhahran metro (E04 Khobar, E06 Ath-Thuqbah, E07 Dhahran, E10 Saihat, and the Dammam row itself) stay `screened = true`. The commuter-belt decision belongs to R2, not to the pilot (the region-sweep skill's example exclusion "inside metro area" is not applied here).

## 7. Method and limits

- **Coordinates and osm_id:** OSM objects from Nominatim search results on 30 Oct 2026 (S-eastern-004; ODbL). Object types are mixed: most are `place=city|town|village` nodes; E06 is a boundary relation (tagged neighbourhood), E15 Qaryat al-'Ulyā is a way (village), E12 Raḥīmah is an amenity inside Ras Tanura, and E20 is a `place=neighbourhood` way. The `osm_id` is the object id; the object type is in this list. Overpass was not used (HTTP 502, server at capacity, 30 Oct 2026), and the GCC PBF was not parsed because no OSM reader is installed in this worktree (adding one would change `pyproject.toml`).
- **Distances (`dist_existing_km`):** haversine (R = 6,371.0088 km) from the row's coordinates to the nearest existing East line station point: Riyadh (node 492520789), Hofuf (way 95533900), Abqaiq (node 2011671784), Dammam (node 492547630). Station list from SAR's published East line (S-025). **To station points, not the alignment** (A-screen-pilot-002). Note: the OSM node for the Dammam station carries a Dhahran address (Needs judgement, item 13).
- **Distances (`dist_metro_km`):** haversine to the nearest reference node of the primary-tier metros in A-screen-013: Dammam (node 287865393), Khobar (node 32441763), Dhahran (node 447805356) for Dammam–Khobar–Dhahran, and Riyadh city (node 315358390). A-screen-pilot-003. The Riyadh reference is nearer than Dammam for Hafar al-Batin (E05), Al-Qaisumah (E21) and King Khalid Military City (E22).
- **Committed lines:** the GCC railway's announced route (S-029, S-032) passes Al-Khafji (route point) and Dammam (not confirmed). No alignment or station coordinates were found, so `dist_committed_km` is **null** for every row (not computed). No Landbridge or Riyadh Rail Link line enters the Eastern Province in the sources consulted (Landbridge is Riyadh–Jeddah, S-054 to S-058; the Riyadh Rail Link is Riyadh-only, S-033). Committed lines are never labelled existing.
- **Road minutes:** null everywhere (`road_min_method: pending R1a skims`).
- **Terrain:** `terrain_class` is null for every row. The DEM classification is pending R1a, and none of the geography sources consulted classifies these settlements. Not guessed.
- **Populations:** citypopulation.de (S-eastern-001) with Wikipedia corroboration (S-eastern-002). Where the two differ: Dammam 1,386,166 (census place row) against 1,386,671 (Wikipedia); Khafji uses the place row 78,691, not the governorate row 84,316 that Wikipedia shows. The register keeps the place rows. A GASTAT primary table would replace this and register as a new edition.
- **The nearest existing station for Hafar al-Batin, Al-Qaisumah and King Khalid Military City is Riyadh**, at about 390 to 430 km. No North line station was included (its coordinates were not sourced).

## 8. Economic roles the schema cannot express

Roles come only from the enumerated list in `common/schemas.py` (`EconomicRoleName`). Two sourced facts do not fit the list and are recorded here instead of forced into a role:

- Abqaiq (E13): oil processing (Aramco hub; S-eastern-010). No enum role.
- Ras Tanura (E16): refinery (Aramco; S-eastern-011), no enum role. Its port is recorded as `port`.

## 9. Sources

| id | publisher | status | used for |
|---|---|---|---|
| S-eastern-001 | citypopulation.de (credits GASTAT) | secondary | governorate and place populations (Census 2022-05-10); military row (E22) |
| S-eastern-002 | Wikipedia (CC BY-SA 4.0) | secondary | corroboration of town populations |
| S-eastern-003 | Saudipedia (Arabic) | secondary | Eastern Province governorate count (13 incl. seat) |
| S-eastern-004 | OpenStreetMap via Nominatim (ODbL) | verified (objects); types checked per row | coordinates, osm_id |
| S-eastern-005 | Gulf States Newsletter (search extract) | secondary | Khafji border crossing (Al-Nuwasib–Al-Khafji) |
| S-eastern-006 | UNESCO World Heritage Centre (search extract) | secondary | Al-Ahsa Oasis role (heritage, agriculture) |
| S-eastern-007 | Maritime Executive (search extract, Mawani figures) | secondary | Dammam port role |
| S-eastern-008 | Wikipedia on RCJY (search extract) | secondary | Jubail industrial city role |
| S-eastern-009 | Wikipedia on KFUPM; KFUPM staff page (search extract) | secondary | Dhahran university and air-base roles |
| S-eastern-010 | Saudipedia / Wikipedia on Abqaiq (search extract) | secondary | §8 (no enum role) |
| S-eastern-011 | Wikipedia on Ras Tanura; MarineLink (search extract) | secondary | Ras Tanura port role; §8 |
| S-eastern-012 | Wikipedia on King Fahd International Airport (search extract) | secondary | Dammam airport role |

Existing ids used (docs/data-sources.md): S-025 (East line stations), S-029 and S-032 (GCC railway route), S-033 (Riyadh Metro), S-054 to S-058 (Landbridge), S-070 (13 regions), S-071 (census reference date), S-072 and S-090 (GASTAT governorate count and portal, unverified).

## 10. Needs judgement

1. **Governorate count, 12 or 13.** Saudipedia (Arabic) and the Arabic Wikipedia list give 13 with Al-Bayda; the census table (S-eastern-001) gives 12 and sums exactly to the regional total. Decide the Eastern count and whether Al-Bayda is a governorate, a sub-unit or an error. Until then E18 is `screened = false`.
2. **`pop_type`.** The pilot brief asks for `secondary`; `RegionRow` allows only official, derived or grid. I used `official` (the value is GASTAT's census figure), with the source row S-eastern-001 marked secondary. Decide: add `secondary` to the schema, or require a GASTAT primary before populations are used.
3. **Raḥīmah (E12, 57,030) against Ras Tanura (E16).** The OSM object is an amenity in Ras Tanura's Al Fayha district. It may be the same urban area as Ras Tanura. Not summed. Decide which row, if either, is the town.
4. **Ras Tanura town population.** None in the sources consulted (the governorate figure 62,314 is not used). Find the census locality row.
5. **Al-Udayd (E17).** No town-level population (governorate 8,635 not used). The OSM locality is at 24.61 N, 51.41 E, near the Qatar border. Verify its location before any distance is computed.
6. **Al-Bayda (E18).** Centre not located. The candidate is by name only.
7. **Hofuf (E02).** The census place row merges Al-Hufuf and Al-Mubarraz (729,606). Keep merged, or split (no split source found).
8. **Jubail (E03).** The census place row includes Jubail Industrial City (S-eastern-001 note). Keep as the town figure, or report the industrial city separately.
9. **King Khalid Military City (E22).** A "Military Institution" in the census table and a `place=town` in OSM. Keep as a settlement row for screening, or treat as an institution.
10. **Economic-role enum.** Oil processing (E13 Abqaiq) and refinery (E16 Ras Tanura) have no enum value. Propose `energy` or a similar role.
11. **Schema gaps between the pilot brief and `RegionRow`.** Field names differ (brief: `dist_km_existing`, `nearest_existing_line`, `dist_km_committed`; schema: `dist_existing_km`, `nearest_existing`, `dist_committed_km`). Fields the brief asks for but `RegionRow` does not have: `threshold_50k`, `pilot_sample`, `notes`, `primary_to_find`, `road_min_method`, `nearest_metro_tier` (the region-sweep skill lists it too). `RegionRow` forbids extra fields, so these are kept in this document. The brief's terrain label `coastal_plain` is `coastal` in the schema. The schema also has no `id` field.
12. **Metro inclusion.** Whether towns inside the Dammam–Khobar–Dhahran metro go to the commuter-belt path, or are excluded, is an R2 decision.
13. **Dammam station.** OSM node 492547630 carries a Dhahran address. Confirm it is the East line's Dammam station (SAR published list, S-025).
14. **GCC railway alignment.** Coordinates are needed for committed-line distances. Not found.
15. **Terrain.** Pending the DEM classification in R1a.

## 11. Validation

- Every row was built as a `RegionRow` and validated before writing, and again after the Parquet was read back: 22 of 22 pass.
- `uv run python -m screening.region_sweep validate` was **not run**: the module does not exist in this worktree (`screening/` is still the R0 skeleton and is owned by the screening track). The validation above used `common/schemas.py:RegionRow` directly.
- Parquet and CSV have the same 22 rows in the same order and the same columns (`economic_roles` flattened to `role:source`; `sources` joined with `;`). The table in §3 is generated from the Parquet.
