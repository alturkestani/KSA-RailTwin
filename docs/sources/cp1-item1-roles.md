> **Document version:** docs/sources/cp1-item1-roles.md v1.0 | 31 Oct 2026 | Author: rail-data-scout (CP1_PREP) | Status: draft

# CP1 item 1.3: economic roles for the pilot candidate register

Scope: the `economic_roles` gaps listed in the CP1_PREP brief, plus a sweep of the airport and port towns in the register. Access date for every row: 2026-10-31.

Outputs (no existing file was edited; the coordinator merges the role lines into `cities/ksa/candidates-pilot.parquet`):
- `docs/sources/cp1-item1-roles-sources.csv`: 20 source rows, S-cp1-100 to S-cp1-119 (same header as `docs/sources/index.csv`).
- `docs/sources/cp1-item1-roles.csv`: 30 role lines to ADD, plus 4 `(none found)` lines.

## Totals

30 roles added, across 10 regions:

| Region | Roles added | Towns |
|---|---|---|
| makkah | 7 | Makkah (hajj_umrah); Jiddah (port, airport, hajj_umrah); Rābigh (energy, port); Aṭ-Ṭa'if (airport) |
| eastern | 8 | Jubail (port, energy); Ras Tanura (energy); Abqaiq (energy); Hofuf (airport); Al-Qaisumah (airport); Hafar al-Batin (airport); Khobar (tourism) |
| riyadh | 5 | Riyadh (airport, university, giga_project); Ad-Dawadmi (airport); Wadi ad-Dawasir (airport) |
| madinah | 3 | Yanbu' al-Bahr (energy, airport); Al-Ula (airport) |
| northern_borders | 2 | Arar (airport); Turaif (airport) |
| tabuk | 1 | Tabuk (giga_project, province-level; flagged) |
| jazan | 1 | Jizan (airport) |
| asir | 1 | Bisha (airport) |
| qassim | 1 | Buraydah (airport) |
| al_baha | 1 | Al-Bāḥah (airport) |

Verified (primary): 15 roles, of which 12 are GACA airport lines tied to the town through the airport name, plus the KSU and TotalEnergies lines and the Riyadh GACA release. Secondary: 15 roles.

## Not found (none-found lines in the CSV)

- Rābigh, giga_project: no PIF giga-project source ties Rabigh. King Abdullah Economic City is administered by the Royal Commission for Jubail and Yanbu and developed by Emaar (search summaries). Pages read: saudipedia.com/en/rabigh-governorate.
- Khobar, port / airport / energy: not added. King Fahd Causeway is a road link, not a port, and King Fahd International Airport is 54 km away in Dammam (saudipedia.com/en/article/1187, read). Khobar tourism is added.
- Umluj, airport: not added. Red Sea International Airport is located in Hanak, Tabuk Province (en.wikipedia.org/wiki/Red_Sea_International_Airport, read). Search summaries that say "Umluj area" are unsourced. Conflict for escalation.
- Al-Qurayyat, airport: none in the GACA February 2025 report (all three pages read).

## Requested rows: outcome

| Row | Outcome |
|---|---|
| makkah:relation:12429517 Makkah | hajj_umrah added (secondary: Saudipedia search extract; Ministry of Hajj and Umrah statement still to find) |
| madinah:osm:4571693347 Al-Madinah | existing hajj_umrah (S-madinah-013, secondary) and airport kept. GACA February 2025 names "Prince Mohammed bin Abdulaziz International Airport" (5-15M band), so the airport name is verified. Hajj role remains secondary. Nothing added. |
| makkah:node:1933393717 Jiddah | port, airport, hajj_umrah added (see CSV) |
| makkah:relation:12429524 Rābigh | energy added (Petro Rabigh, secondary). port added at governorate level (King Abdullah Port inside KAEC, which is inside Rabigh governorate). giga_project not added (none-found line). |
| madinah:osm:3148037089 Yanbu' al-Bahr | energy added (YASREF, secondary). SAMREF and Luberef not separately sourced: samref.com.sa plant page returned 404, and the homepage had no location text. airport added (GACA verified). |
| eastern:osm:38903292 Jubail | port added (Mawani via Arab News, secondary); energy added (SATORP, TotalEnergies page, verified) |
| eastern:osm:287865393 Dammam | existing port (S-eastern-007) and airport (S-eastern-012) kept as adequate secondary sources. Primary (Mawani, GACA or DACO) still to find. Nothing added. |
| eastern:osm:1237805652 Ras Tanura | energy added (secondary). The same portfolio-pplus page gives a location sentence ("near the industrial port city of Jubail") that conflicts with the town; not used. |
| eastern:osm:348286415 Abqaiq | energy added (Saudipedia, secondary; Eastern Province, processing role). Aramco page not reached. |
| tabuk:osm:5418190413 Tabuk | giga_project added at province level only (NEOM is in Tabuk Province per Wikipedia summary). The Tabuk city row is not named as NEOM's location. Flagged. |
| madinah:osm:7700293159 Al-Ula | airport added (GACA verified; Saudipedia secondary). Existing giga_project, heritage and tourism (S-madinah-012) not re-verified; see the flags below. |
| eastern:osm:208501048 Hofuf | heritage: existing (S-eastern-006). Airport added (Al-Ahsa International Airport, HOF, serves Hofuf; secondary search summary). |
| riyadh:node:315358390 Riyadh | airport (GACA release, 23 Jul 2025, verified); university (KSU, verified); giga_project (Diriyah Gate, borderline; secondary) |
| eastern:osm:32441763 Khobar | tourism added (Saudipedia, secondary). Port, airport and energy: none found (see above). |
| riyadh:node:1236703790 Ad-Dir'iyah | heritage (S-riyadh-012: UNESCO 1329 list, snippet read) and giga_project (S-riyadh-013: PIF portfolio, snippet read) kept. UNESCO page returned 403 to WebFetch and curl on the access date. Nothing added. |

## Sweep of other port and airport towns

Added, from the GACA February 2025 operational report (verified by name) and secondary tie-ins: Jizan (airport), Arar (airport), Taif (airport), Bisha (airport), Al-Qaisumah (airport), Buraydah (airport; Wikipedia airport list gives the town tie), Hafar al-Batin (airport; Wikipedia list covers both towns), Wadi ad-Dawasir (airport), Al-Bāḥah (airport), Ad-Dawadmi (airport), Turaif (airport), Al-Ula (airport), Yanbu' al-Bahr (airport).

Not added: Abha, Najran, Hail, Sakaka (Al-Jouf), Sharurah, Rafha, Tabuk, Duba, Al-Wajh and Dammam already carry the airport or port role in the register. Duba's port is now the Port of NEOM (management moved to NEOM in 2022 per search summaries); the existing port role is kept.

## Flags and conflicts (for the coordinator)

1. Ras Tanura location text conflicts (portfolio-pplus: "near the industrial port city of Jubail"). Role kept; location not taken from this page.
2. Abqaiq distance to Dhahran: 48 km (Saudipedia, read) vs about 60 km (search summary). Not used in the role.
3. Red Sea International Airport: Hanak, Tabuk Province (Wikipedia, read) vs "Umluj area" (aggregators). Not added to Umluj. Escalate.
4. Tabuk giga_project (NEOM): province-level tie only. The brief allows this; confirm or drop.
5. Rābigh port: King Abdullah Port is inside KAEC, which is inside Rabigh governorate. Governorate-level tie; coordinator to confirm the town-level tie.
6. Riyadh giga_project (Diriyah Gate): on the north-west edge of Riyadh per search summaries; Diriyah is a separate governorate that keeps its own rows. Borderline.
7. Al-Ula giga_project (existing S-madinah-012): sourced to a Vision 2030 project page (search summary). The Royal Commission for AlUla is not a PIF giga-project in the sources read. Label to be confirmed. Hegra UNESCO (whc.unesco.org/en/list/1292) returned 403 on the access date.
8. Hofuf airport: tie comes from a search summary of the Wikipedia article and the GACA airport page (redirected, not read). Name verified in the GACA report.
9. Buraydah and Hafar al-Batin airports: the GACA report carries region or regional names (Al-Qassim; Al-Qaisumah), so the town tie rests on Wikipedia's airport list (secondary).
10. Makkah hajj_umrah: secondary search extract (Saudipedia). The Arab News article dated 14 Jan 2025 was not used because the two fetches of the same URL returned inconsistent text.
11. Jeddah hajj_umrah: the Hajj terminal capacity figure is from 2017. A current GACA or KAIA source is needed before any use in a figure.
12. Khobar tourism: Saudipedia only; weak. Ministry of Tourism or Eastern Region source to find.

## Primary sources not reached on the access date (keep as secondary)

- Mawani: mawani.gov.sa root loaded with no port text; Jeddah and Jubail port pages returned 404 or no text.
- Saudi Aramco: aramco.com news redirect path and the Abqaiq item returned 404 on the redirected path.
- SAMREF: samref.com.sa plant page returned 404; homepage had no location sentence.
- Petro Rabigh: petrorabigh.com/en read; home page has no location sentence.
- UNESCO World Heritage List pages (1563, 1329, 1292): 403 to WebFetch and curl.
- Royal Commission for Makkah City and Holy Sites (rcmc.gov.sa): no Hajj/Umrah role sentence on the page.
- Matarat (matarat.sa): DNS failure on the access date.

## Verified sources used

- GACA, Operational Performance Standards Monthly Report, February 2025 (PDF; S-cp1-100). Read as rendered pages.
- GACA news, 23 Jul 2025, King Khalid International Airport in Riyadh (S-cp1-101).
- King Saud University, campus location page (S-cp1-102).
- TotalEnergies, SATORP project page (S-cp1-103).

## Licence

Public web pages and a GACA public report. Factual role statements only; no dataset is stored. No row needs a licence-register entry beyond the sources themselves (GACA and KSU public pages; the Wikipedia and Saudipedia pages are cited as secondary). No real-world action taken.
