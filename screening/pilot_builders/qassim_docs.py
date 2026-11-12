# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/qassim_build/docs.py (last modified 2026-10-30 21:33 +03, pilot run PILOT_REGION_QASSIM).
# Role: wrote the region documents.
# Outputs named in the code: docs/assumptions-pilot-qassim.md, docs/regions/pilot-qassim.md.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

table = open("/tmp/qassim_build/table.md", encoding="utf-8").read()
region = f"""> **Document version:** docs/regions/pilot-qassim.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_QASSIM) | Status: draft

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

{table}
Governorate centres in the table are the 13 governorate rows (row 14 is excluded). Rows 15–19 are the stratified pilot sample.

## 3. Towns at or above 50,000 (threshold_50k)

Three settlements: Buraydah (571,169), 'Unaīzah (183,319), Ar Rass (107,902). All three are governorate centres. Al-Badā'i'a (48,474) and Al-Bukayriyah (43,229) are just under 50k.

**Open point:** Buraydah governorate has 677,647 persons in total (S-qassim-001), of which Buraydah city proper is 571,169. The remaining 106,478 are not all placed in the citypopulation Qassim list. The GASTAT locality table is not reachable, so a settlement of 50k or more in that remainder cannot be ruled out. Needs Opus judgement (section 7).

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

## 7. Needs Opus judgement

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
"""
open("./docs/regions/pilot-qassim.md", "w", encoding="utf-8").write(region)

assump = """> **Document version:** docs/assumptions-pilot-qassim.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_QASSIM) | Status: draft

# Assumptions register: pilot Qassim

Same row format as `docs/assumptions.md`. Integration merges these rows into `docs/assumptions.md`.

| id | parameter | value | unit | range | source or assumption | status | used in |
|---|---|---|---|---|---|---|---|
| A-screen-pilot-001 | distance method for `dist_existing_km`, `dist_committed_km` and `dist_metro_km`: great-circle (haversine) from published or OSM coordinates; line distance is the minimum over 10 sampled points per OSM segment of the main-line geometry | haversine | method | error under 1% at pilot scale (sampled points); road minutes not computed (`road_min_method: pending R1a skims`) | assumption for the pilot (PROJECT.md W2 note; approved as registered by the prompt, pending CP1) | assumed | `cities/ksa/regions/pilot-qassim.parquet` (all distance fields) |
| A-qassim-terrain-001 | terrain class for all Qassim pilot rows | flat_desert | class | alternatives: dunes (Ad Dahna), mixed; elevation about 600-750 m (secondary, S-qassim-009) | assumption: no DEM read in the pilot; Najd-plateau description from search summary S-qassim-009 (unverified) | assumed | `terrain_class` column, all 19 rows |
"""
open("./docs/assumptions-pilot-qassim.md", "w", encoding="utf-8").write(assump)
print("written")
