> **Document version:** docs/regions/riyadh.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_RIYADH sweep) | Status: draft


# Riyadh region sweep (الرياض, slug `riyadh`)

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.

Register: `cities/ksa/regions/riyadh.parquet` (CSV mirror `riyadh.csv`); schema `RegionRow`; built by `screening/sweeps/riyadh/build.py`; document by `screening/sweeps/riyadh/doc.py`.

## Headline counts

- Governorates: **23** on the GASTAT list (S-073 names, each matched to the GASTAT primary TA1 governorate export, S-cp2-gastat-007); **23** listed in the register (`governorates_listed`). The 23 primary totals sum to **8,591,748**, equal to the GASTAT TA1 Riyadh region total (S-cp2-gastat-002, 8,591,748). Every governorate has its seat as a row.
- Rows (settlements of the R1a universe in the region): **1,096**; screened **60**, excluded **1,036** (all `below 5k and no economic role`).
- At or above 10,000 (`tag_10k`): **22**. At or above 5,000 (`tag_5k`, sensitivity): **57**.
- Population basis: official 37 (36 read on GASTAT's primary tables, 1 relayed), derived 10 (OSM population tags), grid 1,049 (WorldPop 2020, `unverified`).
- Grid-only rows at or above 10,000 that fail the 30 % corroboration gate (A-screen-032): **3** (Al-Saih, Mugharrizat, Tharmada'). Each stays `screened` with the reason `grid-only population, uncorroborated`.
- Sourced economic roles: 30 role entries on 14 rows (airport 3, giga_project 6, heritage 3, industrial_city 6, military 1, mining 1, university 10).
- Committed lines are `committed/under procurement` or `announced/planned` (Landbridge; Riyadh Rail Link), never `existing`. Their stations are unlocated proxies (see Judgement list, item 8).

## Governorates (GASTAT list, 23)

| governorate (EN) | governorate (AR) | GASTAT primary total (S-cp2-gastat-007) | seat | seat population | seat source, status | rows screened |
|---|---|---:|---|---:|---|---:|
| 'Afif | عفيف | 71,616 | Afif | 47,340 | S-cp2-gastat-008 (verified) | 1 |
| Ad-Dawadmi | الدوادمي | 200,620 | Ad Dawadimi | 86,861 | S-cp2-gastat-008 (verified) | 4 |
| Ad-Dilam | الدلم | 54,822 | Ad Dilam | 39,267 | S-cp2-gastat-008 (verified) | 4 |
| Ad-Dir'iyah | الدرعية | 95,834 | Ad Dir`iyah | 61,609 | S-cp2-gastat-008 (verified) | 4 |
| Al-Aflaj | الأفلاج | 54,544 | Layla | 29,698 | S-cp2-gastat-008 (verified) | 5 |
| Al-Ghat | الغاط | 10,799 | Al Ghat | 8,683 | S-cp2-gastat-008 (verified) | 1 |
| Al-Hariq | الحريق | 10,864 | Al Hariq | 6,895 | S-cp2-gastat-008 (verified) | 1 |
| Al-Kharj | الخرج | 373,177 | Al-Kharj | 295,462 | S-cp2-gastat-008 (verified) | 5 |
| Al-Majma'ah | المجمعة | 151,877 | Al Majma'ah | 70,243 | S-cp2-gastat-008 (verified) | 6 |
| Al-Muzahimiyah | المزاحمية | 62,760 | Al Muzahimiyah | 55,604 | S-cp2-gastat-008 (verified) | 1 |
| Al-Quwayiyah | القويعية | 71,410 | Al Quway`iyah | 28,589 | S-cp2-gastat-008 (verified) | 4 |
| Ar-Rayn | الرين | 28,243 | Ar Rayn | 2,726 | S-cp1-017 (secondary) | 1 |
| Ar-Riyadh | الرياض | 7,009,120 | Riyadh | 6,924,566 | S-cp2-gastat-008 (verified) | 4 |
| As-Sulayyil | السليل | 35,271 | As Sulayyil | 25,136 | S-cp2-gastat-008 (verified) | 1 |
| Az-Zulfi | الزلفي | 74,903 | Az Zulfi | 68,317 | S-cp2-gastat-008 (verified) | 1 |
| Durma | ضرما | 26,299 | Duruma | 16,344 | S-cp2-gastat-008 (verified) | 1 |
| Hawtat Bani Tamim | حوطة بني تميم | 41,854 | Hotat Bani Tamim | 30,720 | S-cp2-gastat-008 (verified) | 2 |
| Huraymila | حريملاء | 21,758 | Huraymila' | 9,842 | S-cp2-gastat-008 (verified) | 2 |
| Marat | مرات | 9,846 | Marat | 6,574 | S-cp2-gastat-008 (verified) | 2 |
| Rimah | رماح | 35,683 | Rumah | 25,031 | S-cp2-gastat-008 (verified) | 2 |
| Shaqra | شقراء | 46,403 | Shaqra' | 32,215 | S-cp2-gastat-008 (verified) | 3 |
| Thadiq | ثادق | 12,510 | Thadig | 7,433 | S-cp2-gastat-008 (verified) | 2 |
| Wadi ad-Dawasir | وادي الدواسر | 91,535 | Wadi Ad Dawasir | 77,433 | S-cp2-gastat-008 (verified) | 3 |

The seat figure is the town figure (primary city table, S-cp2-gastat-008); the governorate total is shown for reconciliation only and is never used as a town figure. Ar-Rayn's seat (2,726) is a locality under 5,000 relayed from citypopulation.de (S-cp1-017, `secondary`, with `primary_to_find` = the GASTAT locality table, not reachable, S-090).

## Screened rows (60)

Distances: `dist_*_km` is great-circle distance to the nearest existing station or committed proxy (haversine); `road_min_*` is OSRM free-flow car minutes from the R1a skims (S-r1a-809; not calibrated). `tag_5k` rows are included for the sensitivity run; `tag_10k` rows form the base case.

| name (EN) | governorate | population | pop_type | status | tag_5k | tag_10k | dist existing km | road min existing | dist committed km (proxy) | nearest metro (tier) | economic roles (role:source) | terrain | exclusion |
|---|---|---:|---|---|---|---|---:|---:|---:|---|---|---|---|
| Afif | 'Afif | 47,340 | official | verified | yes | yes | 311.4 | 275.4 | 162.8 | Buraidah (2) | – | flat_desert | – |
| Ad Dawadimi | Ad-Dawadmi | 86,861 | official | verified | yes | yes | 189.9 | 164.5 | 0.0 | Buraidah (2) | airport:S-cp1-100 | flat_desert | – |
| Sajir | Ad-Dawadmi | 14,858 | official | verified | yes | yes | 116.4 | 125.4 | 79.4 | Buraidah (2) | – | flat_desert | – |
| Albijadiyah | Ad-Dawadmi | 8,560 | official | verified | yes | no | 246.7 | 212.9 | 68.6 | Buraidah (2) | – | flat_desert | – |
| Arjaa | Ad-Dawadmi | 5,163 | derived | secondary | yes | no | 175.0 | 190.3 | 27.1 | Buraidah (2) | – | flat_desert | – |
| Ad Dilam | Ad-Dilam | 39,267 | official | verified | yes | yes | 84.4 | 85.8 | 84.4 | Riyadh (1) | – | flat_desert | – |
| Sahna | Ad-Dilam | 8,257 | grid | unverified | yes | no | 83.6 | 91.1 | 83.6 | Riyadh (1) | – | flat_desert | – |
| Ad Dubay`ah | Ad-Dilam | 5,487 | derived | secondary | yes | no | 75.4 | 77.3 | 75.4 | Riyadh (1) | – | flat_desert | – |
| Na`jan | Ad-Dilam | 5,125 | derived | secondary | yes | no | 76.9 | 79.8 | 76.9 | Riyadh (1) | – | flat_desert | – |
| Ad Dir`iyah | Ad-Dir'iyah | 61,609 | official | verified | yes | yes | 20.2 | 22.9 | 19.0 | Riyadh (1) | heritage:S-riyadh-012; giga_project:S-riyadh-013; heritage:S-r1a-205; giga_project:S-r1a-230 | flat_desert | – |
| Al `Uyaynah | Ad-Dir'iyah | 8,649 | official | verified | yes | no | 37.9 | 54.9 | 37.9 | Riyadh (1) | – | flat_desert | – |
| Al Jubaylah | Ad-Dir'iyah | 8,005 | official | verified | yes | no | 32.7 | 48.9 | 32.8 | Riyadh (1) | – | flat_desert | – |
| `Awdah | Ad-Dir'iyah | 6,327 | grid | unverified | yes | no | 22.8 | 31.5 | 21.5 | Riyadh (1) | – | flat_desert | – |
| Layla | Al-Aflaj | 29,698 | official | verified | yes | yes | 262.2 | 210.2 | 260.9 | Riyadh (1) | – | flat_desert | – |
| Al Hamar | Al-Aflaj | 6,158 | grid | unverified | yes | no | 252.5 | 283.8 | 250.7 | Riyadh (1) | – | flat_desert | – |
| Al Badi` | Al-Aflaj | 5,417 | official | verified | yes | no | 292.7 | 233.7 | 291.3 | Riyadh (1) | – | flat_desert | – |
| Ghasibah | Al-Aflaj | 5,348 | grid | unverified | yes | no | 263.4 | 210.7 | 262.1 | Riyadh (1) | – | flat_desert | – |
| Al Haddar | Al-Aflaj | 5,067 | grid | unverified | yes | no | 307.1 | 314.2 | 305.2 | Riyadh (1) | – | flat_desert | – |
| Al Ghat | Al-Ghat | 8,683 | official | verified | yes | no | 48.4 | 43.5 | 179.9 | Buraidah (2) | university:S-riyadh-011 | flat_desert | – |
| Al Hariq | Al-Hariq | 6,895 | official | verified | yes | no | 115.4 | 146.3 | 113.7 | Riyadh (1) | – | flat_desert | – |
| Al-Kharj | Al-Kharj | 295,462 | official | verified | yes | yes | 132.2 | 195.9 | 132.2 | Riyadh (1) | military:S-riyadh-014; industrial_city:S-r1a-204; university:S-r1a-221 | flat_desert | – |
| Al-Saih | Al-Kharj | 138,604 | grid | unverified | yes | no | 80.0 | 75.0 | 80.0 | Riyadh (1) | – | flat_desert | grid-only population, uncorroborated |
| Al Hayathim | Al-Kharj | 13,893 | official | verified | yes | yes | 73.8 | 75.3 | 73.8 | Riyadh (1) | – | flat_desert | – |
| Al Manifiyah | Al-Kharj | 5,731 | grid | unverified | yes | no | 77.2 | 72.8 | 77.2 | Riyadh (1) | – | flat_desert | – |
| Ar Rafi`ah | Al-Kharj | 5,623 | grid | unverified | yes | no | 73.9 | 71.6 | 73.9 | Riyadh (1) | – | flat_desert | – |
| Al Majma'ah | Al-Majma'ah | 70,243 | official | verified | yes | yes | 7.7 | 16.5 | 184.1 | Buraidah (2) | university:S-riyadh-011; university:S-r1a-221 | flat_desert | – |
| Hawtat Sudayr | Al-Majma'ah | 14,813 | official | verified | yes | yes | 41.1 | 45.4 | 141.7 | Riyadh (1) | university:S-riyadh-011; industrial_city:S-r1a-204 | flat_desert | – |
| Tumayr | Al-Majma'ah | 11,217 | official | verified | yes | yes | 50.9 | 53.4 | 130.5 | Riyadh (1) | – | flat_desert | – |
| Al Artawiyah | Al-Majma'ah | 8,684 | official | verified | yes | no | 65.4 | 63.0 | 231.6 | Buraidah (2) | – | flat_desert | – |
| Harmah | Al-Majma'ah | 7,775 | official | verified | yes | no | 8.8 | 18.1 | 185.5 | Buraidah (2) | – | flat_desert | – |
| روضة سدير | Al-Majma'ah | 5,304 | official | verified | yes | no | 36.8 | 43.4 | 147.3 | Riyadh (1) | – | flat_desert | – |
| Al Muzahimiyah | Al-Muzahimiyah | 55,604 | official | verified | yes | yes | 51.5 | 48.5 | 48.7 | Riyadh (1) | – | flat_desert | – |
| Al Quway`iyah | Al-Quwayiyah | 28,589 | official | verified | yes | yes | 161.2 | 122.3 | 103.0 | Riyadh (1) | – | flat_desert | – |
| Ar Ruwaydah | Al-Quwayiyah | 7,916 | official | verified | yes | no | 224.0 | 166.5 | 89.9 | Riyadh (1) | – | flat_desert | – |
| Al Jilh | Al-Quwayiyah | 7,180 | grid | unverified | yes | no | 100.8 | 84.4 | 98.0 | Riyadh (1) | – | flat_desert | – |
| Al `Amar | Al-Quwayiyah | 61 | grid | unverified | no | no | 195.0 | 172.3 | 107.8 | Riyadh (1) | mining:S-r1a-217 | flat_desert | – |
| Ar Rayn | Ar-Rayn | 2,726 | official | secondary | no | no | 175.5 | 146.6 | 156.1 | Riyadh (1) | – | flat_desert | – |
| Riyadh | Ar-Riyadh | 6,924,566 | official | verified | yes | yes | 2.8 | 7.0 | 0.0 | Riyadh (1) | airport:S-cp1-100; industrial_city:S-r1a-204; university:S-cp1-102; giga_project:S-r1a-229; giga_project:S-r1a-231; giga_project:S-r1a-234; giga_project:S-r1a-235; university:S-r1a-221 | escarpment_mountain | – |
| Mugharrizat | Ar-Riyadh | 19,214 | grid | unverified | yes | no | 15.3 | 21.2 | 15.3 | Riyadh (1) | – | flat_desert | grid-only population, uncorroborated |
| Al Hair | Ar-Riyadh | 13,951 | official | verified | yes | yes | 29.3 | 41.5 | 29.0 | Riyadh (1) | – | flat_desert | – |
| (no English name: KSA-ST-01419) | Ar-Riyadh | 5,347 | grid | unverified | yes | no | 23.4 | 54.0 | 23.4 | Riyadh (1) | – | flat_desert | – |
| As Sulayyil | As-Sulayyil | 25,136 | official | verified | yes | yes | 481.1 | 381.7 | 451.6 | Najran (3) | – | flat_desert | – |
| Az Zulfi | Az-Zulfi | 68,317 | official | verified | yes | yes | 73.6 | 68.3 | 205.4 | Buraidah (2) | university:S-riyadh-011; industrial_city:S-r1a-204 | flat_desert | – |
| Duruma | Durma | 16,344 | official | verified | yes | yes | 61.6 | 56.9 | 59.1 | Riyadh (1) | industrial_city:S-r1a-204 | flat_desert | – |
| Hotat Bani Tamim | Hawtat Bani Tamim | 30,720 | official | verified | yes | yes | 130.1 | 110.0 | 129.1 | Riyadh (1) | – | flat_desert | – |
| Al Hulwah | Hawtat Bani Tamim | 6,374 | derived | secondary | yes | no | 133.5 | 119.5 | 132.3 | Riyadh (1) | – | flat_desert | – |
| Huraymila' | Huraymila | 9,842 | official | verified | yes | no | 71.2 | 68.1 | 71.3 | Riyadh (1) | – | flat_desert | – |
| mulham | Huraymila | 8,932 | official | verified | yes | no | 55.5 | 61.3 | 55.6 | Riyadh (1) | – | flat_desert | – |
| Tharmada' | Marat | 11,002 | grid | unverified | yes | no | 89.5 | 101.5 | 131.5 | Riyadh (1) | – | flat_desert | grid-only population, uncorroborated |
| Marat | Marat | 6,574 | official | verified | yes | no | 94.5 | 105.3 | 126.0 | Riyadh (1) | – | flat_desert | – |
| Rumah | Rimah | 25,031 | official | verified | yes | yes | 88.7 | 87.0 | 88.8 | Riyadh (1) | university:S-riyadh-011 | flat_desert | – |
| Saad | Rimah | 6,824 | grid | unverified | yes | no | 85.7 | 89.7 | 85.7 | Riyadh (1) | – | flat_desert | – |
| Shaqra' | Shaqra | 32,215 | official | verified | yes | yes | 76.7 | 78.2 | 121.3 | Riyadh (1) | industrial_city:S-r1a-204; university:S-r1a-221 | flat_desert | – |
| Al Hurayyiq | Shaqra | 8,473 | derived | secondary | yes | no | 52.7 | 72.1 | 147.5 | Riyadh (1) | – | flat_desert | – |
| Al Qasab | Shaqra | 6,348 | grid | unverified | yes | no | 70.3 | 93.4 | 134.1 | Riyadh (1) | – | flat_desert | – |
| Old Thadiq | Thadiq | 7,438 | derived | secondary | yes | no | 82.8 | 73.4 | 102.5 | Riyadh (1) | – | flat_desert | – |
| Thadig | Thadiq | 7,433 | official | verified | yes | no | 83.9 | 73.5 | 102.3 | Riyadh (1) | – | flat_desert | – |
| Wadi Ad Dawasir | Wadi ad-Dawasir | 77,433 | official | verified | yes | yes | 506.8 | 441.6 | 383.6 | Khamis Mushait (2) | airport:S-cp1-100 | flat_desert | – |
| Alhazem | Wadi ad-Dawasir | 7,520 | grid | unverified | yes | no | 507.3 | 445.1 | 380.5 | Khamis Mushait (2) | – | flat_desert | – |
| Al Faw | Wadi ad-Dawasir | 17 | grid | unverified | no | no | 565.7 | 459.2 | 458.1 | Najran (3) | heritage:S-r1a-205 | flat_desert | – |

## Exclusions

1,036 settlements are excluded with the reason `below 5k and no economic role`. They are in the register with their population and distance fields (grid or OSM figure, `unverified` or `secondary`) so that no settlement is silently dropped; they do not enter the ≥ 5k or ≥ 10k sets. Two of them are 0-population OSM tags (AlMardamah; Darat AlMardamah).

## Sources

- GASTAT Census 2022 TA1 primary exports (S-cp2-gastat-007 governorates, S-cp2-gastat-008 cities ≥ 5,000; S-cp2-gastat-002 region total; S-cp2-gastat-001 relayed cross-check, not used as value of record).
- 23 governorate names: S-073 (citypopulation.de, crediting GASTAT; terms unread). The GASTAT locality table that would confirm every locality is not reachable (S-090, S-r1a-500).
- Settlement universe and population basis: R1a (`cities/ksa/zones/settlements.parquet`, CP2 P1a; WorldPop 2020 100 m constrained, S-r1a-505, CC BY 4.0; OSM place nodes, ODbL, S-riyadh-010 and S-r1a-210).
- Distances and road minutes: R1a skims (S-r1a-809; OSRM MLD car on the GCC extract; OSM ODbL).
- Lines: existing (sar-east, sar-north passenger), committed (Landbridge S-054, S-062; Riyadh Rail Link S-060).
- Economic roles: R1a economic nodes (S-r1a-204 MODON, S-r1a-205 WHS list, S-r1a-217 Ma'aden snippets, S-r1a-221 universities, S-r1a-229/231/234/235 giga-projects, S-cp1-100 GACA airports, S-cp1-102 KSU), and the pilot's sourced roles (S-riyadh-011 to 014).
- Terrain: Tuwaiq escarpment (S-riyadh-015) for Ar-Riyadh; all other rows carry the pilot default (`flat_desert`, A-screen-pilot-002 [riyadh]) with no DEM class run.

## Judgement list (Needs judgement; not resolved by guessing)

1. **Al-Saih** (138,604, grid, Al-Kharj): the largest grid-only figure in the region and the only row with a second method run (`gastat2010_city_growth` = 232,644, 68 % away: fails the gate). It is not in the primary city table. Decide once the GASTAT locality table is reachable; no figure is substituted.
2. **Mugharrizat** (19,214, grid) and **Tharmada'** (11,002, grid, Marat): grid-only, uncorroborated; excluded from the ≥ 10k test, kept `screened`.
3. **Al-Kharj** city (295,462, primary city table) has no OSM node in the R1a universe (osm_id null); coordinates are the R1a row's. Confirm the OSM element before any map use.
4. **Riyadh Al Khabra** (31,203, GASTAT primary governorate): not on the S-073 list of the Riyadh region and not in the sum that equals the region total. Not registered here; its region is not verified in this sweep.
5. **Node ties by name** (not by polygon): Sudair → Hawtat Sudayr (15.7 km from the node; the R1a node is not a town). Dhurma → Duruma; Qiddiya City, SEDRA, King Salman Park and Sports Boulevard → Ar-Riyadh (city row); Diriyah Gate → Ad-Dir'iyah. Confirm each tie.
6. **Excluded R1a nodes** (`EXCLUDED_NODES` in the build script): `univ-ksau-hs` (Jeddah coordinates, region tag not Riyadh); `heritage-uruq-bani-maarid` (19.34 N, about 600 km from its named town); `giga-new-murabba` (source S-r1a-214 is a Hajj-site coordinate list). None is attributed to Riyadh.
7. **Ma'aden Al-'Amar** (mining): the role's source (S-r1a-217) is search snippets, not read. Tied to the hamlet at the node's coordinates (23.764 N, 45.081 E, 61 persons, grid). Read the Ma'aden source before use.
8. **Committed stations are proxies**: Landbridge stops (Dawadmi, Riyadh, Muwai, North South Connection) and Riyadh Rail Link stops are unlocated (`committed_sites_unlocated`). The committed distances are to those proxy points (Ar-Riyadh = 0.0 km by construction), not to an alignment or a station site.
9. **Terrain** is the pilot default for 1,095 rows (no DEM class run). Only Ar-Riyadh has a sourced class.
10. **Name spelling**: the register follows S-073 (`Rimah`); the GASTAT primary export and the R1a rows say `Rumah` (the town, 25,031). The primary governorate total for Rimah is 35,683 (`Rumah`).
11. **Al-Faw** (17 persons, grid): the heritage role is tied to it through the node at its coordinates; the source is the Wikidata WHS list (S-r1a-205). Confirm the inscription.
12. **Figures that differ from older sources**: Ar-Riyadh city is 6,924,566 (primary, S-cp2-gastat-008), not 7,000,100 (Wikipedia, S-riyadh-009) nor the governorate's 7,009,120 (S-cp2-gastat-007). Pilot vs primary differ by more than 2 % for no Riyadh row.

## Layers

Every line in this file is `existing` (sar-east and sar-north passenger), `committed/under procurement` (Riyadh Rail Link, S-060) or `announced/planned` (Landbridge, S-054, S-062). The distance columns name their layer in `nearest_existing` or `nearest_committed`.

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.
