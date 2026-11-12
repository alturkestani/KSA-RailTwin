> **Document version:** docs/regions/pilot-qassim.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_QASSIM) | Status: draft

# Qassim (القصيم) pilot sweep, slug `qassim`

**Screening input, not a forecast.** Synthetic demand, uncalibrated: scenario comparison, not a forecast. This is a coarse pilot sweep to test the region-sweep schema (`PILOT_REGION_QASSIM`). The full register is `REGION_QASSIM` in R2. Access date for every source: 30 Oct 2026. Source ids: `docs/sources/pilot-qassim.csv`.

## 1. Governorate count (rule 2)

| source | count | status |
|---|---|---|
| citypopulation.de admin page (S-qassim-001; credits GASTAT) | 13 governorates; their 2022 populations sum to the region total 1,336,179 | secondary |
| citypopulation.de Qassim page (S-qassim-002) | same 13 governorates | secondary |
| English Wikipedia, Al-Qassim Province (S-qassim-004) | 13 in the table; infobox says 12 (unreconciled) | secondary |
| Arabic Wikipedia list (S-075 family in `docs/sources/index.csv`) | 14: adds Abanat (C-010) | secondary; conflict |
| GASTAT's own table | not reached (`portal.saudicensus.sa` did not connect on the access date) | **unverified** |

Register header: `governorates_gastat: 13` (**secondary**, as credited to GASTAT by citypopulation.de; not read from GASTAT) and `governorates_listed: 13`. They are equal, but the GASTAT figure is not yet primary. The Abanat conflict is resolved as excluded (see section 5). The infobox's 12 is left unreconciled. The table and citypopulation both give 13 governorates, and the 13 populations sum exactly to the region total (1,336,179).

## 2. Settlement rows

Every row carries `pop_source`, `pop_year` and `pop_type` when a population is set. `pop_type = secondary` (see section 6 on the schema). Distances are great-circle (haversine, A-screen-pilot-001). Road minutes are empty (`road_min_method: pending R1a skims`). Line geometry is OSM (ODbL): SAR Riyadh–Qurayyat passenger line, Qassim bounding box. The line is classed **existing** because the Wikipedia infobox states "Operating" (S-qassim-005). No committed or under-procurement alignment passes Qassim in any source reached (the Landbridge route is unpublished; Riyadh Rail Link and the GCC Saudi section are outside Qassim), so `dist_committed_km` is null.

| # | name (EN / AR) | governorate | centre | pop 2022 (S-qassim-002) | lat, lon (OSM) | osm | km to North line | km to Buraydah (metro) | roles | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Al-'Asyāḥ / الأسياح | Al-'Asyāḥ | yes | null | 26.7958, 44.2036 | node 11081595197 | 35.2 | 56.5 | none sourced | - |
| 2 | Al-Badā'i'a / البدائع | Al-Badā'i'a | yes | 48,474 | 25.9878, 43.7335 | node 6770266310 | 66.1 | 45.0 | none sourced | - |
| 3 | Al-Bukayriyah / البكيرية | Al-Bukayriyah | yes | 43,229 | 26.1499, 43.6654 | relation 12406850 | 52.4 | 36.6 | none sourced | - |
| 4 | Al-Midhnab / المذنب | Al-Midhnab | yes | 33,341 | 25.8596, 44.2209 | relation 12406843 | 64.0 | 58.1 | none sourced | - |
| 5 | An-Nabhāniyah / النبهانية | An-Nabhāniyah | yes | 5,221 | 25.8556, 43.0813 | way 302790288 | 101.5 | 103.5 | none sourced | - |
| 6 | Ar-Rass / الرس | Ar-Rass | yes | 107,902 | 25.8685, 43.5039 | node 346703530 | 87.4 | 69.5 | agriculture | threshold_50k |
| 7 | Ash-Shimāiyah / الشماسية | Ash-Shimāiyah | yes | 5,719 | 26.3183, 44.2631 | node 1236365190 | 12.8 | 29.1 | none sourced | - |
| 8 | Buraydah / بريدة | Buraydah | yes | 571,169 | 26.3317, 43.9717 | node 1236365110 | 21.3 | 0.0 | administrative | threshold_50k |
| 9 | Ḍariyah / ضرية | Ḍariyah | yes | 5,485 | 24.9309, 42.5833 | relation 12406851 | 214.4 | 208.9 | none sourced | COORD UNRESOLVED |
| 10 | Riyāḍ al-Khabrā' / رياض الخبراء | Riyāḍ al-Khabrā' | yes | 25,588 | 26.0548, 43.5581 | node 734945198 | 66.2 | 51.5 | none sourced | - |
| 11 | 'Unaīzah / عنيزة | 'Unaīzah | yes | 183,319 | 26.0909, 43.9864 | way 785290146 | 45.1 | 26.8 | tourism | threshold_50k |
| 12 | 'Uqalt aṣ-Ṣuqūr / عقلة الصقور | 'Uqalt aṣ-Ṣuqūr | yes | null | 25.8284, 42.1979 | node 747671382 | 144.5 | 185.8 | none sourced | - |
| 13 | 'Uyūn al-Jiwā' / عيون الجواء | 'Uyūn al-Jiwā' | yes | 15,619 | 26.4946, 43.6377 | node 1237556276 | 17.9 | 37.9 | none sourced | - |
| 14 | Abanat (sub-locality, not a governorate row) / أبانات | An-Nabhāniyah | no | null | 25.4445, 42.7037 | node 11350920607 | 156.5 | 160.7 | none sourced | excluded |
| 15 | Al-Quwārah / القوارة | Buraydah | no | 5,646 | 26.7819, 43.4669 | node 747671390 | 5.4 | 70.9 | none sourced | pilot_sample |
| 16 | Al-Malīdā' / المليداء | Buraydah | no | 6,967 | 26.3183, 43.7808 | node 1237555392 | 30.7 | 19.1 | none sourced | pilot_sample |
| 17 | Al-Khubarā' / الخبراء | Buraydah | no | 16,906 | 26.0700, 43.6245 | node 1237557434 | 62.1 | 45.2 | none sourced | pilot_sample |
| 18 | Qibah / قبة | Al-'Asyāḥ | no | 11,506 | 27.4025, 44.3241 | node 747671189 | 101.3 | 124.1 | none sourced | pilot_sample |
| 19 | Dakhnah / دخنة | Ar-Rass | no | 6,354 | 25.3610, 43.6140 | node 747667497 | 134.3 | 113.7 | none sourced | pilot_sample |

Governorate centres in the table are the 13 governorate rows (row 14 is excluded). Rows 15–19 are the stratified pilot sample.

## 3. Towns at or above 50,000 (threshold_50k)

Three settlements: Buraydah (571,169), 'Unaīzah (183,319), Ar Rass (107,902). All three are governorate centres. Al-Badā'i'a (48,474) and Al-Bukayriyah (43,229) are just under 50k.

**Open point:** Buraydah governorate has 677,647 persons in total (S-qassim-001), of which Buraydah city proper is 571,169. The remaining 106,478 are not all placed in the citypopulation Qassim list. The GASTAT locality table is not reachable, so a settlement of 50k or more in that remainder cannot be ruled out. Needs judgement (section 7).

## 4. Pilot sample (5 rows, `pilot_sample: true`)

The sample spans the distance arms (near <25 km, mid 25–100 km, far >100 km) and the non-centre/centre edges. None of the five has a sourced economic role, so the "with role" arm of the sample is empty (see section 7).

| town | why it is in the sample |
|---|---|
| Al-Quwārah (5,646; 5.4 km) | near arm; tests the smallest near town |
| Al-Malīdā' (6,967; 30.7 km) | mid arm; small town in Buraydah governorate, close to the metro |
| Al-Khubarā' (16,906; 62.1 km) | mid arm; largest non-centre sample town |
| Qibah (11,506; 101.3 km) | far arm; non-centre town larger than the Ash-Shimāiyah centre (5,719); its governorate centre (Al-'Asyāḥ) has a null population |
| Dakhnah (6,354; 134.3 km) | far arm; second far town, in the Ar-Rass governorate |

The stratified sample was meant to cover the economic-role arms too. In this pass no sourced role was found for any sample town, so that arm is untested here.

## 5. Exclusions and omissions (rule 2)

- **Abanat** (row 14, `screened = false`): an Arabic-Wikipedia 14th governorate that is absent from every other list. OSM places it as village nodes inside the An-Nabhāniyah boundary. Excluded pending GASTAT confirmation.
- **Hijrat 'Uqlat aṣ-Ṣuqūr** (9,717 in 2022, S-qassim-002): no OSM place node found (Arabic query). Not placed, so it has no coordinates and no row. Listed here so the omission is not silent.
- **Other localities ≥ 5,000 not sampled** (sample quota of 4–6 reached; not geocoded in this pass): 'Aīn Bin Fuhaīd (6,548, Al-'Asyāḥ), Ash-Shaqah al-'Aliyā (5,449, Buraydah), Qaṣrābin 'Aqīl (5,617, Buraydah). Two of them (Ash-Shaqah, Qaṣrābin) returned no OSM result for their Arabic names; 'Aīn Bin Fuhaīd was not queried.
- **Below 5,000 (not sampled, excluded from tags):** all other Place rows in S-qassim-002 (for example Ad-Dulaymiyah 4,763, Al-Fuwayliq 4,861, Al-Qarīn 3,466, Kahṣībah 4,529, Ash-Shīḥiyah 2,708, Abā al-Wurūd 3,142, Qaṣībā' al-Jadīdah 2,691, Ad-Dhībiyah 2,623). Listed in S-qassim-002; not registered.
- **Ḍariyah** (row 9) is kept, not excluded, but its coordinates are unresolved (flagged `COORD UNRESOLVED`). Its distances are invalid.

## 6. Schema notes (for the coordinator, not changed here)

1. `RegionRow.pop_type` allows only `official`, `derived` and `grid`. The pilot writes `secondary`, as the prompt requires. The canonical `RegionRow` rejects those 16 populated rows on that field alone (checked: all errors are `pop_type`). A local extension that adds `secondary` passes all 19 rows. The canonical schema therefore has no pass for this register. Needs a decision (section 7).
2. `RegionRow` has no fields for `threshold_50k`, `pilot_sample`, `notes`, `road_min_method`, `dist_method`, `terrain_status`, `nearest_metro_tier` or the coordinate flag. They are written as extra Parquet and CSV columns, and the validator checks them only through the extension.
3. `common/schemas.py` was not changed (not in this track's ownership).

## 7. Needs judgement

1. **Schema:** add `secondary` to `pop_type` and the pilot fields to `RegionRow`, or keep `secondary` and map it to `grid`/`derived` in R2. This decides whether `validate` can pass canonically.
2. **Governorate count:** GASTAT's own list is needed to make `governorates_gastat` primary. The 13 vs 12 vs 14 conflict is recorded in section 1.
3. **Buraydah governorate remainder (106,478):** whether a 50k+ settlement sits outside the Buraydah city proper. Needs the GASTAT locality table.
4. **Ḍariyah coordinates:** the only Qassim candidate is a boundary centroid at 24.93N, 42.58E, which looks wrong. Place node and distances to be replaced.
5. **Centre populations:** Al-'Asyāḥ and 'Uqalt aṣ-Ṣuqūr have no centre place row in the source. Null, not guessed.
6. **Bukayriyah and Midhnab coordinates:** boundary-relation centroids, not place nodes. Replace in R2.
7. **Economic roles:** Buraydah (administrative) is from Wikipedia. 'Unaīzah (tourism) and Ar Rass (agriculture) come from search summaries (S-qassim-009, unverified). No sample town has a sourced role.
8. **Terrain:** every row is `flat_desert` (A-qassim-terrain-001, assumed). Ad Dahna dune fields may apply to parts of the region. A DEM read is needed in R2.
9. **Nearest metro:** Buraydah (tier 2) is recorded as nearest for every row, checked by distance to Buraydah only. The other approved metros (Riyadh, Madinah and so on) were not computed in this pilot.

## 8. Sources

See `docs/sources/pilot-qassim.csv` (S-qassim-001 to 007 and 009; S-qassim-008 is unused, its material is folded into 009). Raw pages and JSON are archived under `data/ksa/pilot-qassim/raw/` (gitignored; SHA-256 in the source register). OSM data: © OpenStreetMap contributors, ODbL 1.0.

## 9. Labels

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast. No planned or committed line is labelled existing: the North line is labelled existing on the strength of the Wikipedia infobox (S-qassim-005).
