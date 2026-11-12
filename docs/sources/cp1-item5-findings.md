> **Document version:** docs/sources/cp1-item5-findings.md v1.0 | 31 Oct 2026 | Author: rail-data-scout (CP1_PREP) | Status: draft

pilot, proposed criteria pending CP1; screening input, not a forecast

# CP1_PREP item 5: Al-Qarā centre and Riyadh seat populations, with GASTAT reachability

Access date for every row: 2026-10-31 (Asia/Riyadh). Citation rows: `docs/sources/cp1-item5.csv` (S-cp1-001 to S-cp1-028, same header as `docs/sources/index.csv`). Nothing in `docs/sources/index.csv`, `docs/regions/` or the pilot registers was edited. No sign-up, post, email or agency contact. Every number below carries an S-cp1 id. Synthetic demand, uncalibrated: scenario comparison, not a forecast (no model output is used here).

## Summary

- Al-Qarā: the governorate centre is OSM node 4975708122 (place=governorate). The OSM admin_centre (seat) is Al Tawilah (الأطاولة), node 9327998071 (place=town), 1.1 km away. Two second-source coordinates (Wikidata, Wikipedia) point to Al-Jawf, about 1,077 km away: a conflict, not used. The settlement population for Al-Qarā is **not tabulated** on citypopulation.de; the governorate total 19,586 is not used as a settlement figure.
- Riyadh seats: **14 of 14 have a seat-town population, all secondary** (citypopulation.de crediting GASTAT). **0 verified** on GASTAT: the GASTAT portal did not connect, and the GASTAT and open.data.gov.sa pages reached did not expose a locality table.
- Downloads (task C): none. No GASTAT or open-data census table was reachable as a file, so `data/ksa/tables/` was not created and no manifest row was added. `uv run python -m common.manifest verify` returned OK (16 rows) after this session; no manifest row was added.
- Conflicts flagged, not averaged: Al-Qarā 2010 population (citypopulation 31,186 vs OSM and Wikidata 31,480); Al-Qarā coordinates (Wikidata and Wikipedia vs OSM).

## 1. Al-Qarā (القرى), governorate centre in Al-Bahah

### 1a. Candidate points (OSM)

| role | osm_id | osm_type | place tag | lat | lon | name:ar | name:en | S-ids |
|---|---|---|---|---|---|---|---|---|
| governorate centre (use for the centre point) | 4975708122 | node | governorate | 20.2507795 | 41.3503986 | القرى | ALQARA | S-cp1-002, S-cp1-001 (label member), S-cp1-004 |
| administrative centre, seat town (candidate for the settlement point) | 9327998071 | node | town, capital=6 | 20.2475218 | 41.3607144 | الأطاولة | Al Tawilah | S-cp1-003, S-cp1-001 (admin_centre member), S-cp1-004 |
| governorate boundary (area, not a point) | 12429803 | relation | boundary=administrative, admin_level=6, place=province | 20.2507795 (Nominatim centroid) | 41.3503986 | محافظة القرى | Al Qara | S-cp1-001 |

Containment: Nominatim places both nodes in "Al Qara, Al-Bahah Province" (S-cp1-004). Nominatim search for "Al Qara" did not return node 4975708122 itself; it was read through the OSM API. Overpass mirrors were not usable: overpass-api.de returned HTTP 000; overpass.osm.ch returned empty element lists both for an id query on node 4975708122 and for a place bounding-box query that contains it. The OSM API 0.6 was used instead.

### 1b. Second-source cross-check and distances (haversine, R = 6371.0088 km)

| pair | second source | S-id | distance km |
|---|---|---|---|
| OSM governorate node vs citypopulation.de page coordinate (20.394, 41.328) | citypopulation.de Al-Qarā page (meta latitude/longitude; basis not stated) | S-cp1-005 | 16.1 |
| OSM admin centre (Al Tawilah) vs citypopulation.de page coordinate | same | S-cp1-005, S-cp1-003 | 16.6 |
| OSM governorate node vs OSM admin centre | internal OSM check | S-cp1-002, S-cp1-003 | 1.14 |
| OSM governorate node vs Wikidata Q65040833 P625 (29.8833, 40.2167) | Wikidata | S-cp1-006 | 1077.1 |
| OSM governorate node vs Wikipedia (en) Al-Qura (29.883, 40.217) | Wikipedia | S-cp1-007 | 1077.1 |
| Wikidata point vs citypopulation point | Wikidata vs citypopulation | S-cp1-006, S-cp1-005 | 1061.1 |
| Wikipedia point vs Al-Jawf Qara village node 1236739557 (29.876944, 40.226944) | OSM node in Sakaka, Al Jawf | S-cp1-010, S-cp1-007 | 1.2 |

Reading: the OSM governorate node and the citypopulation page coordinate agree to 16.1 km, which is within the uncertainty of an unstated centroid basis. The Wikidata and Wikipedia coordinates lie about 1 km from the Qara village in Sakaka (Al-Jawf), so the Al-Bahah entity appears to have inherited the wrong point. **Conflict, not used.** Other Al-Qara places excluded as different places: Al Qara' hamlet in Makkah Region (S-cp1-009); Al Qarah neighbourhood in Al-Ahsa (S-cp1-011).

### 1c. Census 2022 population

| item | value | S-id | status | note |
|---|---|---|---|---|
| settlement (place) population, Al-Qarā or Al Tawilah | **not tabulated** | S-cp1-005 | n/a | the citypopulation.de Al-Qarā page has 0 place rows; no Al Tawilah census figure in any source read |
| governorate population 2022 (context only; NOT a settlement figure) | 19,586 | S-cp1-005 | secondary (GASTAT primary to find) | same as S-al_baha-001 |
| governorate population 2010 | citypopulation 31,186 vs OSM and Wikidata 31,480 | S-cp1-005 vs S-cp1-001, S-cp1-008 | conflict | difference 294 persons (0.9 %); both shown, not averaged |
| governorate population 2004 | 29,162 | S-cp1-005 | secondary | citypopulation |

Note for the pilot register (not applied; no existing file was edited): row AB-06 (Al-Qarā) is marked "centre not located" in `docs/regions/pilot-al_baha.md`. The OSM governorate node (place=governorate) and the OSM seat (Al Tawilah, place=town) are both now sourced here, so the coordinator can decide which point the register should use. The population stays unavailable.

## 2. Riyadh region: governorate-seat populations (14 seats)

Source for every row: citypopulation.de Ar-Riyad Region page (https://www.citypopulation.de/en/saudiarabia/riyad/), Places table, column "Population Census 2022-05-10", which credits GASTAT. Status = secondary for all 14 (GASTAT primary not reached). Census reference date 2022-05-10. Seat basis: "name = governorate" means the citypopulation Governorate column equals the place name; that is an inference, not a seat statement read from a source. The governorate total is shown for context only.

| # | seat (EN) | name (AR) | seat town population 2022 | S-id | seat basis | governorate total 2022 (context, not the seat) | found | status | primary to find |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Ad-Dilam | الدلم | 39,267 | S-cp1-012 | name = governorate (inferred) | 54,822 (S-cp1-012) | yes | secondary | GASTAT Census 2022 locality table |
| 2 | Layla | ليلى | 29,698 | S-cp1-013 | pilot register: OSM place Layla in Al-Aflaj (name differs; inferred) | 54,544 (S-cp1-013) | yes | secondary | GASTAT Census 2022 locality table |
| 3 | Al-Ghat | الغاط | 8,683 | S-cp1-014 | name = governorate (inferred) | 10,799 (S-cp1-014) | yes | secondary | GASTAT Census 2022 locality table |
| 4 | Al-Hariq | الحريق | 6,895 | S-cp1-015 | name = governorate (inferred) | 10,864 (S-cp1-015) | yes | secondary | GASTAT Census 2022 locality table |
| 5 | Al-Quwayiyah | القويعية | 28,589 | S-cp1-016 | name = governorate (inferred) | 71,410 (S-cp1-016) | yes | secondary | GASTAT Census 2022 locality table |
| 6 | Ar-Rayn | الرين | 2,726 | S-cp1-017 | name = governorate (inferred) | 28,243 (S-cp1-017) | yes | secondary | GASTAT Census 2022 locality table |
| 7 | As-Sulayyil | السليل | 25,136 | S-cp1-018 | name = governorate (inferred) | 35,271 (S-cp1-018) | yes | secondary | GASTAT Census 2022 locality table |
| 8 | Durma | ضرما | 16,344 | S-cp1-019 | name = governorate (inferred) | 26,299 (S-cp1-019) | yes | secondary | GASTAT Census 2022 locality table |
| 9 | Hawtat Bani Tamim | حوطة بني تميم | 30,720 | S-cp1-020 | name = governorate (inferred) | 41,854 (S-cp1-020) | yes | secondary | GASTAT Census 2022 locality table |
| 10 | Huraymila | حريملاء | 9,842 | S-cp1-021 | name = governorate (inferred) | 21,758 (S-cp1-021) | yes | secondary | GASTAT Census 2022 locality table |
| 11 | Marat | مرات | 6,574 | S-cp1-022 | name = governorate (inferred) | 9,846 (S-cp1-022) | yes | secondary | GASTAT Census 2022 locality table |
| 12 | Shaqra | شقراء | 32,215 | S-cp1-023 | name = governorate (inferred) | 46,403 (S-cp1-023) | yes | secondary | GASTAT Census 2022 locality table |
| 13 | Thadiq | ثادق | 7,433 | S-cp1-024 | name = governorate (inferred) | 12,510 (S-cp1-024) | yes | secondary | GASTAT Census 2022 locality table |
| 14 | Wadi ad-Dawasir | وادي الدواسر | 77,433 | S-cp1-025 | name = governorate (inferred) | 91,535 (S-cp1-025) | yes | secondary | GASTAT Census 2022 locality table |

**Count: 14 of 14 have a seat-town population (all secondary, 0 verified on GASTAT).**

Notes on the Riyadh rows:
- Wadi ad-Dawasir: the pilot register said the centre was unresolved. This page has a place row "Wādī ad-Dawāsir" in Wādī ad-Dawāsir (77,433, S-cp1-025). This resolves the centre figure only at secondary level; the governorate total is 91,535.
- Layla: the Al-Aflaj governorate row is 54,544; the Layla place row is 29,698 (S-cp1-013). The seat is inferred from the pilot register (OSM place Layla), not from a GASTAT statement.
- Al-Khamasin (the town sometimes given as the Wadi ad-Dawasir seat, per the brief): no row with that name appears on the citypopulation Riyadh places table, and no other source was read for it. Left unresolved.
- Ad-Dilam: the governorate row is labelled "Ad-Dilam [ ← Al-Kharj ]" (formerly part of Al-Kharj); the seat is the Ad-Dilam place row (39,267).
- Coverage vs the pilot register: the pilot listed 13 unscreened seats with no sourced population, plus Wadi ad-Dawasir. Every one now has a secondary value here, so the coordinator can decide whether to update `docs/regions/pilot-riyadh.md`. Not applied.

### 2a. Places URLs tried (for any seat not found)

No seat was missed, so there are no "not found" entries. For completeness, the GASTAT and open-data URLs tried for the locality tables are listed in section 3.

## 3. GASTAT and open-data reachability log (2026-10-31)

| URL | result | S-id |
|---|---|---|
| https://portal.saudicensus.sa/ | curl HTTP 000 (no connection) | S-cp1-028 |
| https://portal.saudicensus.sa/portal/public/1/15?type=TABLE | curl HTTP 000 (no connection) | S-cp1-028 |
| https://www.stats.gov.sa/en/statistics | HTTP 200 (site reachable) | none (navigation) |
| https://www.stats.gov.sa/en/statistics?index=119025&subindex=127380 | HTTP 200; "Saudi Census Statistics 2022" section; no locality or governorate table download link in static HTML | S-cp1-026 |
| https://www.stats.gov.sa/en/w/census-2022 and https://www.stats.gov.sa/en/census | HTTP 404 (guessed paths) | none |
| https://open.data.gov.sa/ | HTTP 200 (Open Data Platform home) | none |
| https://open.data.gov.sa/en/datasets?q=census | HTTP 200; no result list in static HTML | S-cp1-027 |
| https://open.data.gov.sa/api/3/action/package_search?q=census%202022&rows=50 | HTTP 200 with body "Request Rejected" (WAF support ID); not a dataset list | S-cp1-027 |
| web search: GASTAT Census 2022 locality or Riyadh governorate table as a file | no GASTAT locality file in results (UNESCWA deck and unrelated census files only) | none |
| https://citypopulation.de/en/saudiarabia/riyadh/ (region slug guessed) | redirect to homepage; the working slug is /riyad/ | none |

Census 2022 locality tables were therefore not reached on any GASTAT primary URL. The Riyadh and Al-Qarā numbers are secondary (citypopulation.de) and must be replaced when `portal.saudicensus.sa` or a GASTAT file becomes reachable (rule 1).

## 4. Downloaded tables (task C)

None. Nothing was downloaded, so there are no manifest rows from this item and no `data/ksa/tables/README.md`. Reasons: the GASTAT portal did not connect (HTTP 000); stats.gov.sa has no census table file link in the pages read; open.data.gov.sa rejected the search API with a WAF page and its HTML search showed no census dataset. Disk at the time of the check: 24 GiB free (`df -h ~`). `uv run python -m common.manifest verify` returned "manifest OK: 16 rows".

## 5. Open items and escalations

- Al-Qarā settlement population: not tabulated anywhere read. Needs a GASTAT locality table (the citypopulation Al-Qarā page is empty). Escalate if the register must carry a settlement figure.
- Al-Qarā centre point choice: governorate node (place=governorate, 20.2508, 41.3504) vs seat Al Tawilah (place=town, 20.2475, 41.3607). Both are OSM; the coordinator must decide which one the register uses. Only 1.1 km apart, so the choice barely changes distances.
- Al-Qarā 2010 population conflict: 31,186 (citypopulation) vs 31,480 (OSM tag and Wikidata with a GASTAT reference). Unresolved; GASTAT 2010 table needed.
- Wikidata Q65040833 and Wikipedia Al-Qura coordinates are wrong for Al-Bahah. Suggest the coordinator or a later run flags them to the Wikidata and Wikipedia editors; no edit was made here (no real-world action).
- Riyadh seat identities are inferred from name matches (13 of 14); Layla is from the pilot register. Needs a seat statement from GASTAT or the Riyadh region profile.

Sources: `docs/sources/cp1-item5.csv` (S-cp1-001 to S-cp1-028). Access date 2026-10-31 on every row.
