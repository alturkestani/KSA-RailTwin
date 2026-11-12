> **Document version:** docs/regions/pilot-madinah.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_MADINAH) | Status: draft

# Pilot sweep: Al-Madinah al-Munawwarah (المدينة المنورة), slug `madinah`

Screening input, not a forecast. This is a coarse pilot to test the register schema (`PILOT_REGION_MADINAH`), not the full Madinah register (`REGION_MADINAH` in R2). Population is Census 2022 from a secondary aggregator that credits GASTAT (S-madinah-001), so every population row is `pop_type: secondary`. Coordinates and OSM IDs come from OpenStreetMap (ODbL; © OpenStreetMap contributors). Distances are great-circle (A-screen-pilot-001); road minutes are pending R1a. Files: `cities/ksa/regions/pilot-madinah.parquet` and `.csv` (same 9 rows).

## 1. Governorate count (GASTAT vs listed)

| item | value | source |
|---|---|---|
| `governorates_gastat` | **unverified**. The GASTAT primary list was not reached (portal DNS failure). Secondary reading: 9 governorate rows, i.e. 8 governorates plus the capital row. | S-madinah-001, S-madinah-002, S-madinah-003 |
| `governorates_listed` | **8 of 9**. Rows exist for 8 governorate centres. Wādī al-Fara' has no row because its centre is unidentified (section 6). | this register |

Discrepancy flagged (not resolved): the citypopulation.de region row gives 2,389,452 for Al-Madinah region, but its own governorate rows sum to **2,137,983**, which matches DataSaudi, Saudipedia and GLMM (S-madinah-003, S-madinah-004, S-079). The sum was re-computed for this document (see section 3, check 2).

The governorate rows (census 2022, S-madinah-001):

| governorate | governorate row (persons) | centre row in register |
|---|---|---|
| Al-Madinah al-Munawwarah (capital row) | 1,477,047 | Al-Madinah al-Munawwarah |
| Yanbu' al-Baḥr | 359,631 | Yanbu' al-Baḥr (place 331,916; includes Yanbu Industrial City) |
| Al-'Ulā | 60,103 | Al-Ula |
| Badr | 58,259 | Badr |
| Khaybar | 45,532 | Khaybar |
| Mahd adh-Dhahab | 48,590 | Mahd adh-Dhahab |
| Al-Ḥinākīyah | 43,256 | Al-Henakiyah |
| Al-'Aīṣ | 22,445 | Al-'Aīṣ |
| Wādī al-Fara' | 23,120 | **none** (centre not identified; section 6) |

## 2. Register rows (9)

Metro: primary tier (A-screen-013). All values are as written in the Parquet. `tag_10k` = population ≥ 10,000 (A-screen-001); `tag_5k` = ≥ 5,000 (A-screen-002). `dist_existing_km` is to the nearest of four located HHR stations (A-screen-pilot-004).

| name_en | name_ar | governorate | centre | population (2022) | tag_10k | tag_5k | threshold_50k | pilot_sample | osm_id (type) | lat, lon | dist_existing_km (nearest located station) | dist_metro_km (to Madinah) | terrain (assumed) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Al-Madinah al-Munawwarah | المدينة المنورة | Al-Madinah al-Munawwarah | yes | 1,411,599 | yes | yes | yes | no | 4571693347 (place=city) | 24.47115, 39.61112 | 8.96 (HHR Madinah) | 0.00 | mixed |
| Yanbu' al-Bahr | ينبع البحر | Yanbu' al-Baḥr | yes | 331,916 | yes | yes | yes | no | 3148037089 (place=city) | 24.08902, 38.06871 | 170.71 (HHR Madinah) | 162.01 | coastal |
| Al-Ula | العلا | Al-'Ulā | yes | 40,760 | yes | yes | no | yes | 7700293159 (place=town) | 26.55890, 37.95965 | 290.37 (HHR Madinah) | 285.22 | escarpment_mountain |
| Badr | بدر | Badr | yes | 30,494 | yes | yes | no | yes | 87175609 (way; place=village) | 23.78000, 38.79074 | 120.14 (HHR Madinah) | 113.30 | mixed |
| Khaybar | خيبر | Khaybar | yes | 15,888 | yes | yes | no | yes | 546640970 (place=town) | 25.70254, 39.29330 | 142.79 (HHR Madinah) | 140.62 | mixed |
| Mahd adh-Dhahab | مهد الذهب | Mahd adh-Dhahab | yes | 20,272 | yes | yes | no | yes | 1237964803 (place=town) | 23.49959, 40.87916 | 161.43 (HHR Madinah) | 168.13 | mixed |
| Al-Henakiyah | الحناكية | Al-Ḥinākīyah | yes | 24,880 | yes | yes | no | no | 1236695024 (place=town) | 24.87972, 40.51528 | 94.05 (HHR Madinah) | 102.03 | mixed |
| Al-'Aīṣ | العيص | Al-'Aīṣ | yes | 8,760 | no | yes | no | no | 5813392174 (place=town) | 25.06357, 38.10854 | 173.58 (HHR Madinah) | 165.39 | mixed |
| Ath-Thamad | الثمد | Khaybar | no | 8,385 | no | yes | no | yes | 7653649386 (place=town) | 25.52796, 39.33947 | 122.87 (HHR Madinah) | 120.66 | mixed |

Every row: `pop_source` S-madinah-001, `pop_year` 2022, `pop_type` secondary; `sources` include S-001 (HHR station list) and S-madinah-005 (OSM coordinates). Economic roles (each with its source):
- Al-Madinah: hajj_umrah, airport (S-madinah-013).
- Yanbu': port, industrial_city (S-madinah-008).
- Al-Ula: giga_project, heritage, tourism (S-madinah-012).
- Badr: heritage, tourism (S-madinah-010).
- Khaybar: heritage, tourism, agriculture (S-madinah-011).
- Mahd adh-Dhahab: mining (S-madinah-009).
- Al-Henakiyah, Al-'Aīṣ, Ath-Thamad: **none recorded, not searched**. An empty list here means "not recorded", not "no role".

## 3. Checks run

1. Parquet and CSV hold the same 9 rows and ids (checked in the handoff).
2. Governorate rows sum to 1,477,047 + 359,631 + 60,103 + 58,259 + 45,532 + 48,590 + 43,256 + 22,445 + 23,120 = **2,137,983**. This equals the GLMM total and the DataSaudi figure, not the citypopulation region row (2,389,452).
3. Haversine check: Madinah city centre to the HHR Madinah station = 8.96 km. The station sits about 9 km east of the centre, in Al-Hadra district (S-madinah-005).
4. `RegionRow` validation: each of the 9 rows fails on **one** field, `pop_type = 'secondary'` (the model allows only `official`, `derived`, `grid`). All other fields pass, including the coordinate box, the tag rules and the population-source rule. The `screening.region_sweep validate` command does not exist in this worktree (the `screening` package has only the R0 `cli.py`), so this check was run with pydantic directly.

## 4. Sample of smaller towns (5–50k): rationale

Five rows carry `pilot_sample: true` (Al-Ula, Badr, Khaybar, Mahd adh-Dhahab, Ath-Thamad). Each has a reason in the Parquet `notes`.

| row | why it was sampled |
|---|---|
| Al-Ula (40,760) | far (290 km); sourced giga-project and heritage roles. |
| Badr (30,494) | far (120 km); heritage role; **tests an OSM tagging mismatch** (way tagged `place=village` with a census population of 30,494). |
| Khaybar (15,888) | far (143 km); heritage, tourism and agriculture roles. |
| Mahd adh-Dhahab (20,272) | far (161 km); mining role (Ma'aden gold mine). Distance from Madinah is disputed (167 km vs 380 km, S-madinah-009); not used. |
| Ath-Thamad (8,385) | far (123 km); **without** a recorded role (not searched); non-centre town below 10k. |

Stratum coverage: **near (< 25 km) is empty** for this region. The only located station in Al-Madinah is the HHR Madinah station, and among the located settlements only the city itself lies within 25 km of it (a centre row, not a sample). Unlocated places such as Mazārī' Wādī al-'Uqūl could change this (section 5). Two sample-design edges could not be tested:
- A governorate centre smaller than a non-centre town: no such case in the ≥5k set (Ath-Thamad, 8,385, is smaller than every centre in its region).
- A town split across governorates: no case found.

## 5. Exclusions (rule 2: nothing silently omitted)

| place | census population | governorate | reason |
|---|---|---|---|
| Mazārī' Wādī al-'Uqūl | 24,381 | Al-Madinah al-Munawwarah | **no OSM node found** (Nominatim search, Arabic name, no result). No coordinates, so no row. Needs judgement (section 6). |
| 12 places of 2,500 to 4,999 (Ad-Duwayf'ah 2,638; Al-Wāsṭah 2,621; Al-Qubaybah 2,593; Al-Miḥfar 2,772; Al-Faqīr 3,349; Al-'Adhīb 3,382; Mughayrā' 3,422; Al-Yutmah 3,561; Al-Ghizlānī 3,706; Ar-Rāyis 3,849; Aṣ-Ṣuwaydrah 4,235; Aṣ-Ṣalṣalah 4,455) | 2,593–4,455 | various | below the 5,000 sensitivity threshold (A-screen-002). Not in the register. |

The census locality list used (places ≥ 2,500) comes from S-madinah-001, so places under 2,500 are not listed at all. That is a source limit, not a screening decision.

## 6. Needs judgement

1. **Schema: `pop_type = 'secondary'`.** The pilot prompt needs `secondary` for aggregators; `RegionRow` allows only `official`, `derived`, `grid`. All 9 rows are `secondary`. Options: add `secondary` to the literal in `common/schemas.py` (a change to an existing line, so not additive under the `common/` rule), or treat citypopulation as GASTAT-derived. I did not change the schema or relabel the rows.
2. **Schema: extra pilot columns.** `RegionRow` uses `extra="forbid"`. The pilot columns `threshold_50k`, `pilot_sample`, `nearest_metro_tier`, `primary_to_find`, `road_min_method`, `dist_method` and `notes` are in the Parquet and CSV but fail the model. Decide whether these belong in the schema or in a sidecar.
3. **Terrain vocabulary.** The prompt lists `sand_dunes` and `coastal_plain`. The schema has `dunes`, `coastal`, `mixed`, `escarpment_mountain`, `flat_desert`, `sabkha`. I used the schema values.
4. **Wādī al-Fara' centre.** Its governorate row exists (23,120), but the centre is not named in the sources: Saudipedia lists seven or eight subdivision centres (Al-Akhal, Abu Dhaba', Al-Hamnah, Al-Hindiyah, Umm al-Burak, Suri, Mughaysil) and none as the capital (S-madinah-015). No row was written. Needs the GASTAT or Ministry of Interior centre.
5. **Mazārī' Wādī al-'Uqūl (24,381).** No OSM node was found, so it cannot be placed. Either an OSM mapping task or the GASTAT locality coordinate is needed.
6. **Yanbu' population.** The census place (331,916) includes Yanbu Industrial City. The town alone may be far smaller. The governorate-level figure is 359,631. Used as-is (A-screen-pilot-005).
7. **Badr type mismatch.** OSM tags the Badr way as `place=village`, against a census population of 30,494. The OSM tag is not used to decide anything; the coordinate is the way centroid.
8. **Governorate count.** GASTAT primary not reached. Secondary sources say 8 governorates plus the capital, which is 9 rows. The register has 8 rows of 9 (section 1).
9. **Committed layer.** No committed line through Al-Madinah is sourced. The Landbridge Wikipedia page returned HTTP 404. A search summary mentions a 172 km King Abdullah Port to Yanbu Industrial City line; it is unverified and not used (S-madinah-006). The register uses `dist_committed_km = null`.
10. **Existing layer.** KAEC station coordinates were not found in OSM (two Nominatim queries, Arabic and English, no results). `dist_existing_km` uses the four located stations. For Yanbu', Badr and Mahd the nearest located station is Madinah. For Yanbu' that is guaranteed by latitude alone if KAEC lies south of about 22.5° N (KAEC's position is not sourced); for Badr and Mahd it is not proven. Recheck once KAEC is located.
11. **Economic roles not searched.** Al-Henakiyah, Al-'Aīṣ and Ath-Thamad have no role searched. Their empty lists are not evidence of no role.

## 7. Sources

Pilot source rows are in `docs/sources/pilot-madinah.csv` (S-madinah-001 to S-madinah-015; S-madinah-007 is not used). Existing index rows used: S-001 (HHR station list, verified), S-070 (13 regions), S-072 and S-090 (GASTAT not reached), S-079 (region-total conflict), S-083 (Madinah city, citypopulation).

OpenStreetMap: © OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright). Share-alike applies to derived databases (licence register). Coordinates were read from Nominatim; they are not checked against GASTAT locality coordinates.

Screening input, not a forecast. No figure here is a demand or ridership estimate.
