> **Document version:** docs/regions/pilot-al_jouf.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_AL_JOUF) | Status: draft

# Region register, pilot: Al-Jouf (الجوف), slug `al_jouf`

**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

Coarse pilot sweep (high cut-off) to test the `RegionRow` schema. The full register is `REGION_AL_JOUF` (R2). Access date for every source: **30 Oct 2026** (Asia/Riyadh). Files: `cities/ksa/regions/pilot-al_jouf.parquet` and `.csv` (same 8 rows, same ids, cross-checked); sources `docs/sources/pilot-al_jouf.csv` (S-al_jouf-001 to -009, plus S-018 from the index); assumptions `docs/assumptions-pilot-al_jouf.md`.

## Header: governorate count

- `governorates_gastat`: **4** (status: secondary; the GASTAT primary was not reached)
- `governorates_listed`: **4** (Sakaka, Al-Qurayyat, Tubarjal, Dumat al-Jandal)
- **Discrepancy, flagged with both sources.** citypopulation.de (S-al_jouf-001, -002; credits GASTAT Census 2022) lists 4 governorates, and its region total 595,822 equals the sum of the four governorate totals. Saudipedia's Tabarjal Governorate page also says four (S-al_jouf-004). Wikipedia's Al-Jouf Province page and Saudipedia's Emirate of Al-Jawf page say **three** (S-al_jouf-003, -004). The official GASTAT list was not reached: `portal.saudicensus.sa` gave no connection (S-al_jouf-005). Until GASTAT's list is read, the count is 4 with this conflict open.
- Every governorate has at least one row (its centre). Region total 595,822 (Census 2022, S-al_jouf-001), of which 4 governorates sum to that total.

## Register (8 rows)

The table below is generated from the Parquet file. `pilot_sample` is not a `RegionRow` field: the flag is carried here and in the sample rationale (see "Schema gaps").

| name (EN) | name (AR) | governorate | governorate centre | population (Census 2022) | pop_source / pop_year / pop_type | osm_id | lat | lon | tag_10k | tag_5k | dist_existing_km | dist_metro_km (Tabuk) | economic_roles | pilot_sample |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sakaka | سكاكا | Sakaka | yes | 204,174 | S-al_jouf-001 / 2022 / official | 1236740006 | 29.9784 | 40.2048 | true | true | 40.73 | 394.2 | administrative (S-al_jouf-001), airport (S-al_jouf-008) | false |
| Al-Qurayyat | القريات | Al-Qurayyat | yes | 167,080 | S-al_jouf-001 / 2022 / official | 1236744823 | 31.3333 | 37.3419 | true | true | 6.13 | 334.5 | administrative (S-al_jouf-001) | false |
| Tubarjal | طبرجل | Tubarjal | yes | 78,354 | S-al_jouf-001 / 2022 / official | 1236745024 | 30.5007 | 38.2165 | true | true | 28.87 | 282.8 | administrative (S-al_jouf-001) | false |
| Dumat al-Jandal | دومة الجندل | Dumat al-Jandal | yes | 42,362 | S-al_jouf-001 / 2022 / official | 1236739971 | 29.8059 | 39.8667 | true | true | 10.19 | 356.6 | administrative (S-al_jouf-001), heritage (S-al_jouf-009), tourism (S-al_jouf-009) | true |
| Ṣuwayr | صوير | Sakaka | no | 12,430 | S-al_jouf-001 / 2022 / official | 1236739864 | 30.1173 | 40.3888 | true | true | 53.28 | 416.9 | — | true |
| Abu 'Ajram | أبو عجرم | Dumat al-Jandal | no | 5,610 | S-al_jouf-001 / 2022 / official | 5910483362 | 29.8899 | 39.3058 | false | true | 15.73 | 313.3 | — | true |
| An-Nabak Abū Qaṣr | النبك أبو قصر | Tubarjal | no | 5,374 | S-al_jouf-001 / 2022 / official | 1236739661 | 30.2942 | 38.7014 | false | true | 18.46 | 295.1 | — | true |
| Al-Fayāḍ | الفياض | Tubarjal | no | 5,532 | S-al_jouf-001 / 2022 / official | 1236744782 | 30.6053 | 38.0999 | false | true | 27.56 | 286.5 | — | true |

## Sample rationale (stratified, 5 rows with `pilot_sample = true`)

Al-Jouf does not offer every stratum the brief names. The sample uses the schema edges the pilot is meant to test, and the gaps are reported rather than forced.

| sample row | size (Census 2022) | distance to SAR North alignment | sourced economic role | reason it was picked |
|---|---|---|---|---|
| Dumat al-Jandal | 42,362 (governorate centre) | 10.19 km (near) | heritage, tourism (S-al_jouf-009) | **Schema edge:** a governorate centre below 50 000 (the 50k tag would be false); it is also the only sampled row with a sourced role. |
| Ṣuwayr (Sakaka) | 12,430 | 53.28 km (mid) | none sourced | Non-centre town above 10 000, so `tag_10k` is true on a non-centre row, at a mid distance. |
| Abu 'Ajram (Dumat al-Jandal) | 5,610 | 15.73 km (near) | none sourced | Smallest near-line sample. Its OSM node is typed `village`, although the census size is 5 610. Match is by Arabic name only. |
| An-Nabak Abū Qaṣr (Tubarjal) | 5,374 | 18.46 km (near) | none sourced | Just above the 5,000 threshold (`tag_5k` only); OSM `village`; Arabic name matches exactly. |
| Al-Fayāḍ (Tubarjal) | 5,532 | 27.56 km (mid) | none sourced | Mid distance, just above 5,000; OSM `town`; Arabic name matches (الفياض). |

**Strata not filled, and why.**
- **Far (>100 km from a rail line): not filled.** No Al-Jouf settlement in the census list is more than 100 km from the SAR North alignment (largest: Ṣuwayr at 53.28 km; Sakaka the centre at 40.73 km). The test is left unmet, not forced. Far towns exist in other regions.
- **Economic roles: only one sample row has a sourced role.** Tubarjal's border crossing with Jordan and Al-Qurayyat's industrial role were searched and not found (no source recorded), so they are not claimed. See "Needs judgement".
- **Near (<25 km):** three sample rows (Dumat, Abu 'Ajram, An-Nabak) plus Al-Qurayyat (centre, 6.13 km).

## Governorates and towns not in the register (exclusions)

Rule 2 (no silent omissions): every Census 2022 place at or above 2 500 in the four governorates is accounted for below. Coordinates are not in the register for the places listed as "not in pilot" because the pilot sample is capped at five.

| place (EN) | governorate | Census 2022 | reason for exclusion |
|---|---|---|---|
| Hadīb | Sakaka | 3 677 | below 5,000 (A-screen-002), not sampled |
| Zalūm | Sakaka | 4 368 | below 5,000 (A-screen-002), not sampled |
| Al-'Aqīlah | Al-Qurayyat | 3 170 | below 5,000 (A-screen-002), not sampled |
| Al-Ḥadīthah al-Qadīmah | Al-Qurayyat | 3 956 | below 5,000 (A-screen-002), not sampled. The SAR North passenger list names "Al Haditha" as a terminus (S-018); this place is not confirmed as that station (see Needs judgement) |
| Al-'Isāwīyah | Al-Qurayyat | 4 357 | below 5,000 (A-screen-002), not sampled |
| An-Nāṣfah | Al-Qurayyat | 2 991 | below 5,000 (A-screen-002), not sampled |
| Ghaṭā | Al-Qurayyat | 6 653 | 5,000–50,000 but not in the 5-row sample. The OSM candidate `غطي` (village, 31.2665, 37.5275) is a name that does not match the transliteration with confidence, so no coordinates were assigned. |
| Shu'īb al-Ghwaīl | Tubarjal | 3 546 | below 5,000 (A-screen-002), not sampled |
| Shu'īb Ṭalḥah Ṭabrijal | Tubarjal | 2 632 | below 5,000 (A-screen-002), not sampled |
| Mīqūa' | Tubarjal | 7 020 | 5,000–50,000 but not in the 5-row sample. An OSM `village` node (ميقوع, 29.8210, 38.9234) matches in Arabic, but the Census page's Arabic was not read, so the match is not confirmed. |
| Abu 'Ajram | Dumat al-Jandal | 5 610 | in the sample (see above) |

Places in the list at or above 50 000 with no exclusion: Sakaka (204,174), Al-Qurayyat (167,080), Tubarjal (78,354). **Towns ≥ 50 000: 3** (`threshold_50k` = true for these; the flag is not a `RegionRow` field). Dumat al-Jandal (42,362) is below 50 000.

## Distances and metro (method: A-screen-pilot-001)

- **Existing line.** `dist_existing_km` = great-circle distance from the town coordinates to the nearest OSM `railway=rail` vertex in the box 29.5–31.6 N, 37.0–40.4 E (130 ways, 2 109 vertices; S-al_jouf-006). The nearest point is the SAR North passenger line, which passes "Jouf" and "Qurayyat" and ends at "Al Haditha" (S-018). OSM station nodes: الجوف (Al-Jawf, 29.6485, 39.8377) and القريات (Al Qurayyat, 31.4203, 37.2890). Caution: vertices are not segments, so distances may be overstated by up to the spacing of OSM vertices. Road minutes are not computed (`road_min_existing` null, pending R1a skims).
- **Committed.** `dist_committed_km` null. No committed alignment geometry is in the repository for any line, and the sourced committed lines (Landbridge Riyadh–Jeddah, GCC Kuwait–UAE, Riyadh Rail Link) have no sourced Al-Jouf alignment in this pilot. Left unknown rather than estimated. Committed lines are "announced/planned", never existing (rule 5).
- **Metro.** `dist_metro_km` = distance to the Tabuk centre (OSM node 5418190413; S-al_jouf-007), **tier 2** (A-screen-013). Tabuk is the nearest of the four A-screen-013 metros geocoded in this pilot (register rows: Tabuk 282.8–416.9 km; Buraidah 548.0–851.9 km; Madinah 593.7–794.9 km; Riyadh 872.2–1,182.9 km). The other A-screen-013 metros (Taif, Makkah, Jeddah, Dammam–Khobar–Dhahran, Abha–Khamis Mushait, Jazan, Najran) were not geocoded in the pilot and are not compared. Check in R2 before use.

## Economic roles (every role has a source)

- Administrative: the four governorate centres, from the governorate list in S-al_jouf-001.
- Airport: Sakaka, "served by Al-Jawf Airport which has domestic flights" (S-al_jouf-008, Wikipedia; secondary).
- Heritage and tourism: Dumat al-Jandal (S-al_jouf-009, Arab News, 4 Sep 2022; secondary).
- **Not recorded** (searched, no source found): Tubarjal border crossing, Al-Qurayyat industrial city, mining, giga-project, university, port, Hajj/Umrah. The sample towns without a source have `economic_roles = []`. Empty is not "none": it means "not found in this pilot".

## Terrain

`terrain_class` is **null** on every row (assumption A-screen-pilot-004). No DEM was read and no cited class was found for these towns. Sakaka is "just to the north of the An Nafud desert" (S-al_jouf-008), a location, not a class. The USGS Al Jawf quadrangle geology (sheet 29D) was seen in search results but not read, so it is not used.

## Schema gaps (for the coordinator; the schema was not changed)

`common/schemas.py` is shared and the track rules allow additive changes only. The pilot brief names fields that `RegionRow` does not have (`RegionRow` uses `extra="forbid"`), so the Parquet and CSV carry only `RegionRow` fields:
1. `threshold_50k`: carried here as text ("3 towns ≥ 50k: Sakaka, Al-Qurayyat, Tubarjal").
2. `pilot_sample` and the sample reason: carried in the sample table above.
3. `notes`: not carried in the register; the reasons are in this document.
4. `road_min_method` (pending R1a skims): not carried; `road_min_*` are null.
5. `nearest_metro_tier`: carried inside the `nearest_metro` string ("Tabuk (tier 2, A-screen-013)").
6. `pop_type = secondary`: the schema's enum is `official | derived | grid`; see Needs judgement.
7. `screening.region_sweep` does not exist in this worktree, so the `validate` command is not available. The Parquet and CSV were checked against `common.schemas.RegionRow` with Python instead: 8 of 8 rows validate, and the Parquet and CSV agree on row count, `osm_id` and `population`.

## Needs judgement

1. **Governorate count: 3 or 4.** The GASTAT primary must settle it. Secondary sources conflict (S-al_jouf-001/002/004 say 4; S-al_jouf-003 and the Emirate page say 3). Current recording: `governorates_gastat = 4`, flagged.
2. **`pop_type`.** The Census 2022 values come from citypopulation.de (secondary, crediting GASTAT). The schema has no `secondary` value, so they are recorded as `official` (assumption A-screen-pilot-002). Decide: add `secondary` to the schema, or replace with the GASTAT locality table before use.
3. **Abu 'Ajram's OSM node** (5910483362) is matched by Arabic name only, and it lies about 50 km west of the Dumat centre. Confirm it is the census place.
4. **Al-Fayāḍ and Ṣuwayr OSM matches** are by name (الفياض; صوير). Confirm the Arabic on the census pages.
5. **Al-Ḥadīthah.** The SAR North passenger list names "Al Haditha" as a terminus (S-018). The census place Al-Ḥadīthah al-Qadīmah (3 956) is below 5 000 and is not confirmed as that station. Decide which governorate the terminus is in before R2.
6. **Jouf station.** The OSM station الجوف is 17.7 km from the Dumat centre and 51 km from Sakaka. It is not assigned to a governorate here. Decide whether SAR's "Jouf" stop is the Al-Jouf region's main station.
7. **Terrain** is null for all rows. A DEM classification (R1a) is needed.
8. **Economic roles** for Tubarjal (border) and Al-Qurayyat (industrial) were not found. If confirmed by a source, add them.
9. **Far stratum** is empty for Al-Jouf. Decide whether the sample rule should allow a region with no far town to report the stratum as unmet, as here.

## Sources

Full rows in `docs/sources/pilot-al_jouf.csv` (ids S-al_jouf-001 to -009). Also used: S-018 (SAR North passenger line places, verified; `docs/sources/index.csv`). Status counts (9 new rows plus S-018): **verified** 3 (S-al_jouf-006, -007 and S-018; OSM and SAR primary); **secondary** 6 (S-al_jouf-001, -002, -003, -004, -008, -009; -003 and -004 read from search summaries only); **unverified** 1 (S-al_jouf-005, GASTAT not reached).

Licences: OpenStreetMap data (ODbL 1.0; credit "© OpenStreetMap contributors"). Coordinates and `osm_id` are derived from OSM, so the ODbL share-alike and attribution rules apply to any derived database (licence register row to be added by the coordinator; `data/` is not written). The Overpass and Nominatim responses were used directly and not saved in the repository.
