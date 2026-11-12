> **Document version:** docs/regions/pilot-makkah.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_MAKKAH) | Status: draft

# Makkah region: pilot sweep (coarse)

**Screening input, not a forecast.** This is a coarse pilot to test the region-sweep schema. It is not the full Makkah register (that is `REGION_MAKKAH` in R2). Nothing here is a modelled output.

Register header: `governorates_gastat: not found (null)`; `governorates_listed: 17`.

## 1. Governorate count

- GASTAT's own governorate count for Makkah region: **not found.** The census portal (portal.saudicensus.sa) did not resolve on 30 Oct 2026 (S-072, S-090). A search for GASTAT's governorate table on 30 Oct 2026 also found no primary table.
- Listed here: **17**, from the 17 governorate rows of the citypopulation.de Makkah page, which credits GASTAT's Census 2022 (S-makkah-001). The national list (S-073) also has 17 Makkah rows.
- Status: **flagged, not reconciled.** Both sources agree on 17, but neither is GASTAT's own table.
- Coverage in this register: **16 of 17 governorates** have a row. Al-Ardiyat (العرضيات) is withheld: no coordinates were found in OSM (Nominatim, 30 Oct 2026), and `RegionRow` requires lat/lon (section 5).

## 2. Rows (Parquet and CSV, 18 rows)

Parquet: `cities/ksa/regions/pilot-makkah.parquet` (validates with `common.schemas.load_region_register`). CSV: `cities/ksa/regions/pilot-makkah.csv` (same 18 `osm_id` keys, plus the secondary population and tag columns the Parquet cannot carry, section 6).

Populations in this table are **secondary** (citypopulation.de, credits GASTAT, S-makkah-001). They are not in the Parquet's `population` field (section 6). Distances are great-circle (A-screen-pilot-001); road minutes are not computed (R1a skims). Terrain is not assessed (section 6).

| # | name (EN / AR) | governorate | centre | osm (type, id) | lat, lon | coords method | pop, secondary (S-makkah-001) | dist to nearest existing HHR station (km) | nearest existing | dist to nearest metro (km) | nearest metro | ≥50k | pilot sample | screened / exclusion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 'Āḍam / أضم | 'Āḍam | yes | relation, 12429531 | 20.4196, 40.8442 | boundary centroid (Nominatim relation; no place node found) | 9,022 | 156.0 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 104.5 | Taif (tier 2) | no | no | yes |
| 2 | Al-Jumūm / الجموم | Al-Jumūm | yes | node, 1236466181 | 21.6212, 39.6990 | OSM place node | 41,089 | 24.5 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 25.9 | Makkah (tier 1) | no | yes | yes |
| 3 | Al-Kāmil / الكامل | Al-Kāmil | yes | node, 1237964645 | 22.2640, 39.7982 | OSM place node | 3,151 | 64.8 | HHR King Abdullah Economic City station, OSM node 2147398509 | 93.8 | Makkah (tier 1) | no | no | no: governorate centre kept for coverage (rule 2); secondary population 3,151 is below 5,000 |
| 4 | Khulaīṣ / خليص | Khulaīṣ | yes | node, 724120971 | 22.1551, 39.3202 | OSM place node | 20,139 | 32.5 | HHR King Abdullah Economic City station, OSM node 2147398509 | 68.9 | Jeddah (tier 1) | no | yes | yes |
| 5 | Al-Līth / الليث | Al-Līth | yes | relation, 12429525 | 20.1451, 40.2701 | boundary centroid (Nominatim relation; no place node found) | 20,811 | 150.1 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 126.0 | Taif (tier 2) | no | no | yes |
| 6 | Al-Muwayh / المويه | Al-Muwayh | yes | node, 1236449504 | 22.4366, 41.7619 | OSM place node | 7,278 | 233.0 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 190.0 | Taif (tier 2) | no | no | yes |
| 7 | Al-Qunfudhah / القنفذة | Al-Qunfudhah | yes | relation, 12429518 | 19.1264, 41.0789 | boundary centroid (Nominatim relation; no place node found) | 42,447 | 288.1 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 248.2 | Taif (tier 2) | no | yes | yes |
| 8 | Ranyah / رنية | Ranyah | yes | node, 5924471509 | 21.2572, 42.8502 | OSM place node | 28,681 | 317.6 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 252.3 | Taif (tier 2) | no | no | yes |
| 9 | Al-Khurmah / الخرمة | Al-Khurmah | yes | node, 1236454949 | 21.9081, 42.0318 | OSM place node | 28,491 | 238.1 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 181.5 | Taif (tier 2) | no | yes | yes |
| 10 | Turubah / تربة | Turubah | yes | relation, 12429522 | 21.2173, 41.5875 | boundary centroid (Nominatim relation; no place node found) | 28,279 | 187.7 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 121.6 | Taif (tier 2) | no | no | yes |
| 11 | Maysān / ميسان | Maysān | yes | node, 295919318 | 20.7372, 40.8387 | OSM place node (no census place row: unmapped) | not set (secondary only) | 132.7 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 73.8 | Taif (tier 2) | no | no | yes |
| 12 | Makkah al-Mukarramah / مكة المكرمة | Makkah al-Mukarramah | yes | relation, 12429517 | 21.4208, 39.8269 | boundary centroid (Nominatim relation; no place node found) | 2,385,509 | 4.0 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 0.0 | Makkah (tier 1) | yes | no | yes |
| 13 | Jiddah / جدة | Jiddah | yes | node, 1933393717 | 21.5504, 39.1742 | OSM place node | 3,712,917 | 12.2 | HHR KAIA airport station (Jeddah central station not located: distance overstated) | 0.0 | Jeddah (tier 1) | yes | no | yes |
| 14 | Aṭ-Ṭa'if / الطائف | Aṭ-Ṭa'if | yes | node, 1236468526 | 21.2703, 40.4158 | OSM place node | 563,282 | 67.0 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 0.0 | Taif (tier 2) | yes | no | yes |
| 15 | Rābigh / رابغ | Rābigh | yes | relation, 12429524 | 22.7990, 39.0336 | boundary centroid (Nominatim relation; no place node found) | 72,928 | 45.0 | HHR King Abdullah Economic City station, OSM node 2147398509 | 139.6 | Jeddah (tier 1) | yes | no | yes |
| 16 | Baḥrah / بحرة | Baḥrah | yes | node, 1237963667 | 21.4013, 39.4500 | OSM place node | 70,118 | 35.1 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 33.0 | Jeddah (tier 1) | yes | no | yes |
| 17 | Al-Ḥawiyah / الحوية | Aṭ-Ṭa'if | no | node, 295933353 | 21.4449, 40.5030 | OSM place node | 171,610 | 74.0 | HHR Makkah station (قطار الحرمين السريع - مكة), OSM node 10956967098 | 21.4 | Taif (tier 2) | yes | no | yes |
| 18 | Thuwal / ثول | Jiddah | no | node, 443345673 | 22.2833, 39.1128 | OSM place node | 26,957 | 17.4 | HHR King Abdullah Economic City station, OSM node 2147398509 | 81.7 | Jeddah (tier 1) | no | yes | yes |

## 3. Towns at or above 50,000 (secondary populations)

Six settlements: Makkah (2,385,509), Jiddah (3,712,917), Aṭ-Ṭa'if (563,282), Al-Ḥawiyah (171,610), Rābigh (72,928), Baḥrah (70,118). The `threshold_50k: true` tag is in the CSV only.

Note: Al-Ḥawiyah is a non-centre place in OSM under Taif governorate; check it against GASTAT's governorate assignment.

## 4. Stratified sample of smaller towns (5 to 50,000)

Five rows, `pilot_sample: true` in the CSV. The sample is not representative; it tests schema edges.

| town | population (secondary) | distance to nearest HHR station | role (sourced?) | why it is in the sample |
|---|---|---|---|---|
| Al-Jumūm (governorate centre) | 41,089 | 24.5 km to Makkah station (near) | none sourced | Near, no role. An announced Landbridge stop is claimed at "Jumoum" (S-062); the owner identifies it as Al-Jumum (S-063), with no published location. Kept out of `existing`. |
| Thuwal (non-centre) | 26,957 | 17.4 km to KAEC station (near) | university: KAUST (S-makkah-003, snippet) | Near, with a sourced role. Non-centre town larger than the governorate centre Khulaīṣ (20,139): a schema edge. Governorate ambiguous (Jiddah per OSM and Wikipedia snippet). |
| Khulaīṣ (governorate centre) | 20,139 | 32.5 km to KAEC (between 25 and 100 km) | none sourced | Neither near nor far. Tests the mid band, and a centre smaller than a non-centre town (Thuwal). |
| Al-Khurmah (governorate centre) | 28,491 | 238 km to Makkah station (far) | none sourced | Far, no role. OSM place node. The governorate total (38,744) is cross-checked against S-makkah-005; the centre town figure is from S-makkah-001 only. |
| Al-Qunfudhah (governorate centre) | 42,447 | 288 km to Makkah station (far) | none sourced (search found no port role, S-makkah-007) | Far, coastal, no sourced role. Centre coordinates are a boundary centroid (A-screen-pilot-003). |

So the sample has 5 rows (within 4 to 6): near with a role 1 (Thuwal), near without a role 1 (Al-Jumūm), mid band without a role 1 (Khulaīṣ), far without a role 2 (Al-Khurmah, Al-Qunfudhah). Not covered: far with a sourced role. No sourced role was found for any far town in this pilot.

## 5. Exclusions and withheld rows

| row | status | reason |
|---|---|---|
| Al-Ardiyat (العرضيات), governorate centre | **withheld** (not in Parquet or CSV) | no coordinates found in OSM via Nominatim (30 Oct 2026); `RegionRow` requires lat/lon. Needed: an OSM place node. The governorate total in the citypopulation list is 65,078 and its centre place row is absent. |
| Al-Kāmil, governorate centre | in register, `screened: false` | secondary population 3,151, below the 5,000 tag. Kept for coverage (rule 2). |
| Maysān, governorate centre | in register, population not set | OSM has the place (node 295919318, town) but the citypopulation place list has no row for it: "unmapped" census row. The governorate total is 28,765. |

## 6. Schema notes (what the pilot could and could not write)

The prompt's field list and `common/schemas.py:RegionRow` differ. The Parquet follows `RegionRow` (the code is authoritative). The mapping:

| prompt field | `RegionRow` field | note |
|---|---|---|
| `dist_km_existing` | `dist_existing_km` | |
| `road_min_existing` | `road_min_existing` | null (`road_min_method: pending R1a skims`; not a field in `RegionRow`) |
| `nearest_existing_line` | `nearest_existing` | a station name, not a line (the HHR alignment is not in the pilot) |
| `nearest_committed_station` | `nearest_committed_station` | |
| `economic_roles` | `economic_roles` | `{role, source}` |
| `terrain_class` | `terrain_class` | null: DEM not read; `RegionRow.terrain_class` has no `assumed` value (cannot carry an assumption id) |
| `source_ids` | `sources` | |
| `pop_type: secondary` | not in `RegionRow` | `pop_type` accepts only `official`, `derived`, `grid`. |
| `threshold_50k`, `pilot_sample`, `notes`, `primary_to_find` | not in `RegionRow` | CSV only (`extra="forbid"` rejects them) |

**Consequence:** the Parquet has `population` null for all 18 rows, so `tag_10k` and `tag_5k` are false and no row is tagged. The secondary populations are in the CSV (`population_secondary`) with their source id. The Parquet is valid, but it does not yet carry the thresholds. This is the main open decision (section 8, item 1).

## 7. Sources

Full list in `docs/sources/pilot-makkah.csv`. Reused from the national index (`docs/sources/index.csv`):

- S-072: GASTAT governorate count not found (census portal unresolved).
- S-073: Census 2022 administrative list (17 Makkah governorate rows; secondary).
- S-090: GASTAT census tables unreachable.
- S-062, S-063: Landbridge "Jumoum" stop named by a trade site; identity owner-stated.
- S-079: Makkah region total conflict (8,021,463 vs 7,769,994).

Pilot sources: S-makkah-001 (citypopulation Makkah page), S-makkah-002 (OSM via Nominatim), S-makkah-003 (KAUST, snippet), S-makkah-004 (Thuwal, snippet), S-makkah-005 (Urbistat cross-check), S-makkah-006 (Monshaat, conflict), S-makkah-007 (no Al-Qunfudhah port source found).

**Conflict (not used in any row):** the 17 governorate rows of S-makkah-001 sum to **8,021,463**, equal to GLMM and Monshaat (S-079). The citypopulation region row is 7,769,994. The citypopulation page is therefore internally inconsistent; the governorate rows are used, pending GASTAT.

Licence: OSM data is ODbL (credit: © OpenStreetMap contributors). citypopulation.de terms were not checked (flagged). These rows should go into the licence register (not written here: `docs/licences-pilot-makkah.*` is not in this track's ownership list).

## 8. Needs judgement

1. **Schema gap (main decision).** `RegionRow.pop_type` has no `secondary` value, so secondary populations cannot go in the Parquet. Options: (a) add `secondary` to the `pop_type` Literal in `common/schemas.py` (a one-line change to shared code, outside this track's additive-only rule); (b) wait for GASTAT's primary tables. Recommendation: (a), with the rule that `secondary` rows can never tag `threshold_*` as "official".
2. **GASTAT governorate count** is unverified; 17 is from secondary sources only. Needs GASTAT's own table (or the Law of Provinces) before R2.
3. **Al-Ardiyat** (governorate 17) has no coordinates; withheld. Needs an OSM place node or a GASTAT locality coordinate.
4. **Thuwal governorate**: Jiddah (OSM, Wikipedia snippet) versus the citypopulation list (not checked).
5. **Al-Ḥawiyah governorate**: Taif (OSM) versus GASTAT (not checked).
6. **Al-Jumūm**: the Landbridge "Jumoum" stop is an owner-identified name (S-063), not a published location. It is not in any layer (a `committed` line would need a source with coordinates). The rule that announced lines are never `existing` holds. `nearest_committed` is text only, with `dist_committed_km` null.
7. **Economic roles**: only Thuwal has a sourced role. No roles are sourced for Makkah (hajj/umrah), Jiddah (airport, port), Rābigh (industrial), or the others. An empty list means "not assessed", not "no role". R2 needs sources.
8. **Terrain**: not assessed in the pilot (no DEM read). `terrain_class` is null everywhere.
9. **Governorate centres without a place node**: Makkah, Adam, Al-Līth, Al-Qunfudhah, Turubah and Rābigh use the OSM boundary centroid (A-screen-pilot-003). Replace in R1a.
10. **Jiddah distance**: the Jeddah central HHR station (Al-Sulaymaniyah) is named in S-001 but was not located. The distance to KAIA (12.2 km) is overstated for the city.

## 9. Known limits

- OSM came from Nominatim search only. The Overpass API returned 502 (at capacity) on 30 Oct 2026, so there was no bulk query of `place=*` in the region. The local GCC extract (`data/osm/gcc-states-latest.osm.pbf`) was not read (the pilot does not need it; R1a should use it).
- Coverage is 16 of 17 governorates. The region list is from one secondary source (S-073 / S-makkah-001).
- The build script is in `/tmp/pilot_makkah/build.py` and is not committed (no pilot-owned location for it). The Parquet and CSV are the outputs.
- No road minutes, no committed-line distances, no terrain.
