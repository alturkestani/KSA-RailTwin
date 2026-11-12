> **Document version:** docs/regions/tabuk.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_TABUK) | Status: draft

# Tabuk sweep (تبوك, slug `tabuk`)

**Screening input, not a forecast.** Full R2 register for Tabuk: every GASTAT governorate, every settlement the R1a universe holds for the region (119), population from the primary GASTAT Census 2022 exports where they cover a town, WorldPop only as a flagged gap-fill, distances and road minutes from the R1a skims. Register: `cities/ksa/regions/tabuk.parquet` and `.csv`. Builders: `screening/sweeps/tabuk/`.

## 1. Governorate count

| Source | Count | Note |
|---|---|---|
| GASTAT primary, TA1 by governorate (S-cp2-gastat-007) | 150 governorates in the export; **7 in Tabuk** | Region membership of each governorate from the relayed S-073 list (`screening/gastat.py`, `governorates_2022`); the seven are Tabuk, Umluj, Duba, Al-Wajh, Taymā', Haql, Al-Bad' |
| Register: `governorates_gastat` header | **7** | |
| Register: `governorates_listed` header | **7** | the seven governorate centres, one row each |
| S-tabuk-004 (Wikipedia, Tabuk Province) | 6 + seat = 7 | agrees |
| S-tabuk-003 (Arabic Wikipedia) | 7 rows incl. the capital | agrees |
| S-tabuk-021 (Al-Ma'rifa) | counts Hala Ammar as the 7th | unverified; the primary export has no Hala/Halat entry, so not a governorate |

GASTAT and the register agree (7 = 7). Halat Ammar (حالة عمار) is not a governorate: its OSM polygon is Tabuk (G147), so it sits in the Tabuk governorate row.

## 2. Counts

- Rows: **119** (all settlements the R1a universe holds for `tabuk`; the 7 governorate centres are among them).
- At ≥ 10,000 (`tag_10k`): **7**, all seven governorate centres, all `pop_type: official` from the primary city export S-cp2-gastat-008. No grid row reaches 10,000, so the corroboration gate is not triggered.
- At ≥ 5,000 (`tag_5k`, sensitivity): **10** = the seven centres plus Halat Ammar (derived, OSM tag), Makna and Al Kor (WorldPop grid, unverified).
- Screened in (`screened: true`): **11** = the 10 at ≥ 5,000 plus Neom (2,122 grid; giga-project role).
- Excluded (`screened: false`, with reason): **108**, each with the reason `below 5,000 and no sourced economic role (A-screen-003)`; one of them (قرية الجديد, OSM tag 4,000) also has no dated population and so no population field.
- Rows with a population: **118**; without: **1** (the undated OSM tag above).
- Rows with a sourced economic role: **7** (14 role entries); every role names an S- source.
- WorldPop grid rows: **109**, all `pop_source_status: unverified`, none with `pop_corroboration` (no second method was run for these villages; the 2010 city-growth method covers only towns in the 2010 ≥ 5,000 list).

## 3. Population basis and conflicts

- Seven centres: GASTAT primary city export (S-cp2-gastat-008), settlement figures (Tabuk 594,350; Umluj 46,229; Duba 39,543; Al-Wajh 33,868; Tayma 37,579; Haql 25,652; Al-Bad' 16,583). The governorate totals (S-cp2-gastat-007: Tabuk 623,665, etc.) are not used for any row.
- Bi'r Ibn Hirmas: 4,964 from the relayed citypopulation.de table (S-tabuk-002, secondary). It is below 5,000, so the primary city export does not list it; the OSM tag 5,975 is not used.
- Halat Ammar: OSM population tag 5,293 (derived, S-r1a-210). **Conflict:** the census city table (≥ 5,000 list, S-cp2-gastat-008) does not list it, so it is either below 5,000 in the census or missing from the list. WorldPop gives 7,067, not used (derived > grid). Kept as a 5k sensitivity row only (A-tabuk-002).
- Makna (5,756) and Al Kor (5,353): WorldPop 2020 grid, unverified; `tag_5k` only (no 10k status possible without corroboration).
- Duba: the register keeps the GASTAT city figure (39,543). The R1a grid for the same town (25,568 OSM tag, 17,104 grid) is not used.
- Conflicting social-media figure for Tabuk city (S-tabuk-017, 448,000) and web figure (S-tabuk-019, 753,730): not used.

## 4. Distances and economic roles

- Distances: R1a skims. `dist_existing_km` = great circle to the 15 intercity passenger stations (A-r1a-008), road minutes OSRM car over the 5 nearest candidates (A-r1a-027). Tabuk's nearest existing stations are on the SAR North line (Al-Qurayyat, Al-Jawf) and the HHR (Madinah); the historic Hejaz line is `historical` and not counted.
- Committed: `nearest_committed` is Landbridge or GCC-railway stops; Landbridge stops are unlocated (`committed_sites_unlocated`), so committed distances are indicative (A-tabuk-004).
- Metro: `dist_metro_km` from the A-r1a-009 reference nodes, tier from A-screen-013. Tabuk is a tier-2 metro: 91 rows point to Tabuk (tier 2) and 28 (mostly Umluj and the northern coast) point to Madinah (tier 1) because Madinah is nearer by great circle (see §8).
- Roles: every role is sourced in the row (`economic_roles`, `source`); the sources are the pilot's S-tabuk-004/007–014 and the R1a economic nodes S-r1a-204, S-r1a-212, S-r1a-221, S-cp1-100. Umluj has no sourced role (S-tabuk-011's role statements are unreferenced).

## 5. Terrain

Terrain is **assumed by governorate** (A-tabuk-003): no DEM class exists for this region in the R1a outputs, so no DEM was read in R2. Coastal: Al-Wajh, Duba, Haql, Umluj. Mixed: Tabuk, Taymā', Al-Bad'. Replace with a DEM class before any terrain-dependent cost or alignment.

## 6. The table

| # | name_en | name_ar | governorate | osm_id | population | pop_type | status | tag 5k | tag 10k | screened | road min existing | nearest committed | metro (tier) | roles | exclusion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Tabuk | تبوك | Tabuk | 5418190413 | 594,350 | official | verified | yes | yes | yes | 303.1 | landbridge:jeddah | Tabuk (tier 2) | administrative, airport, heritage, industrial_city, university | seat (Tabuk) |
| 2 | Umluj | أملج | Umluj | 973472834 | 46,229 | official | verified | yes | yes | yes | 254.8 | landbridge:jeddah | Madinah (tier 1) | none sourced | seat (Umluj) |
| 3 | Duba | ضبا | Duba | 1237957881 | 39,543 | official | verified | yes | yes | yes | 438.5 | landbridge:jeddah | Tabuk (tier 2) | port | seat (Duba) |
| 4 | Tayma | تيماء | Taymā' | 1237942492 | 37,579 | official | verified | yes | yes | yes | 308.0 | landbridge:muwai | Tabuk (tier 2) | heritage | seat (Taymā') |
| 5 | Al Wajh | الوجه | Al-Wajh | 1237957986 | 33,868 | official | verified | yes | yes | yes | 376.2 | landbridge:jeddah | Tabuk (tier 2) | airport, heritage | seat (Al-Wajh) |
| 6 | Haql | حقل | Haql | 1236312441 | 25,652 | official | verified | yes | yes | yes | 486.5 | landbridge:jeddah | Tabuk (tier 2) | border_crossing | seat (Haql) |
| 7 | Al-Bad' | البدع | Al-Bad' | 1237951657 | 16,583 | official | verified | yes | yes | yes | 466.1 | landbridge:jeddah | Tabuk (tier 2) | heritage | seat (Al-Bad') |
| 8 | Makna | مقنا | Al-Bad' | 1236317831 | 5,756 | grid | unverified | yes | no | yes | 495.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | – |
| 9 | الكر | الكر | Al-Wajh | 13202274463 | 5,353 | grid | unverified | yes | no | yes | 441.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | – |
| 10 | Halat Ammar | حالة عمار | Tabuk | 1237958860 | 5,293 | derived | secondary | yes | no | yes | 373.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | – |
| 11 | Neom | نيوم | Duba | 8428377321 | 2,122 | grid | unverified | no | no | yes | 424.7 | landbridge:jeddah | Tabuk (tier 2) | airport, giga_project, port | – |
| 12 | Bi'r Ibn Hirmas | بئر ابن هرماس | Tabuk | 1237958577 | 4,964 | official | secondary | no | no | no | 344.8 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 13 | المنجور | المنجور | Al-Wajh | 5813392171 | 4,487 | grid | unverified | no | no | no | 330.1 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 14 | Sharma | شرما | Duba | 5796927641 | 4,431 | grid | unverified | no | no | no | 461.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 15 | Al Khuraybah | الخريبة | Duba | 1237953124 | 3,371 | grid | unverified | no | no | no | 427.9 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 16 | Al-Muweleh | المويلح | Duba | 5811549631 | 2,318 | grid | unverified | no | no | no | 448.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 17 | Beda | بدا | Al-Wajh | 5813392173 | 2,007 | grid | unverified | no | no | no | 420.1 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 18 | الشبحة | الشبحة | Umluj | 6768379773 | 1,676 | grid | unverified | no | no | no | 267.6 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 19 | شُطِيْن | شُطِيْن | Al-Wajh | 7976521844 | 1,526 | grid | unverified | no | no | no | 345.2 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 20 | شواق | شواق | Duba | 5796878010 | 1,488 | grid | unverified | no | no | no | 470.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 21 | الجهراء | الجهراء | Taymā' | 8850711928 | 962 | grid | unverified | no | no | no | 238.3 | landbridge:muwai | Madinah (tier 1) | none sourced | below 5k, no role |
| 22 | القليبه | القليبه | Tabuk | 5792766713 | 945 | grid | unverified | no | no | no | 230.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 23 | ابو القزاز | ابو القزاز | Al-Wajh | 13202274467 | 925 | grid | unverified | no | no | no | 448.2 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 24 | الرس | الرس | Al-Wajh | 7045263790 | 652 | grid | unverified | no | no | no | 428.2 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 25 | شغب | شغب | Duba | 5931432181 | 557 | grid | unverified | no | no | no | 480.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 26 | Al Assafiyah | العسافية | Taymā' | 1236758598 | 530 | grid | unverified | no | no | no | 322.3 | landbridge:dawadmi | Tabuk (tier 2) | none sourced | below 5k, no role |
| 27 | Al Disah | الديسه | Duba | 5809637427 | 428 | grid | unverified | no | no | no | 478.9 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 28 | الحواويط | الحواويط | Duba | 14128986575 | 416 | grid | unverified | no | no | no | 475.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 29 | Al Humaydah | الحميضة | Haql | 11871539261 | 412 | grid | unverified | no | no | no | 480.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 30 | Shaban | الشبعان | Umluj | 1237968244 | 384 | grid | unverified | no | no | no | 249.2 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 31 | unnamed OSM node 3358200251 | unnamed OSM node 3358200251 | Al-Wajh | 3358200251 | 376 | grid | unverified | no | no | no | 427.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 32 | Al Nashifuh | النشيفه | Al-Wajh | 5809625958 | 343 | grid | unverified | no | no | no | 422.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 33 | الفاجية | الفاجية | Umluj | 9279397920 | 322 | grid | unverified | no | no | no | 261.6 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 34 | المثلث | المثلث | Taymā' | 8850714102 | 297 | grid | unverified | no | no | no | 234.1 | landbridge:muwai | Madinah (tier 1) | none sourced | below 5k, no role |
| 35 | النابع | النابع | Al-Wajh | 9482630952 | 236 | grid | unverified | no | no | no | 409.7 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 36 | الشرف | الشرف | Al-Bad' | 5796977485 | 201 | grid | unverified | no | no | no | 446.2 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 37 | البديعه | البديعه | Tabuk | 7092592606 | 143 | grid | unverified | no | no | no | 370.3 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 38 | الدبيبات | الدبيبات | Umluj | 9279409245 | 142 | grid | unverified | no | no | no | 266.0 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 39 | Ash Sharmah | شرما | Duba | 1237953031 | 110 | grid | unverified | no | no | no | 454.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 40 | المشيريف | المشيريف | Umluj | 7677989124 | 109 | grid | unverified | no | no | no | 242.1 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 41 | ابو راكه | ابو راكه | Al-Wajh | 5809629987 | 92 | grid | unverified | no | no | no | 428.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 42 | الحسي | الحسي | Umluj | 7465351185 | 91 | grid | unverified | no | no | no | 230.0 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 43 | عين الأخضر | عين الأخضر | Tabuk | 5809629989 | 86 | grid | unverified | no | no | no | 411.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 44 | شقري | شقري | Tabuk | 5796856231 | 76 | grid | unverified | no | no | no | 364.1 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 45 | رأس الخريطه | رأس الخريطه | Tabuk | 5809740392 | 48 | grid | unverified | no | no | no | 402.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 46 | Al Fuqayyir | الفقيّر | Umluj | 11870220263 | 43 | grid | unverified | no | no | no | 267.1 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 47 | المعظم | المعظم | Tabuk | 5796924000 | 41 | grid | unverified | no | no | no | 385.3 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 48 | تولة | تولة | Umluj | 9307897264 | 34 | grid | unverified | no | no | no | 346.9 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 49 | Samnah | سمنة | Umluj | 11870737896 | 26 | grid | unverified | no | no | no | 271.0 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 50 | ابيط | ابيط | Taymā' | 5923859593 | 25 | grid | unverified | no | no | no | 372.5 | landbridge:dawadmi | Tabuk (tier 2) | none sourced | below 5k, no role |
| 51 | الظلفة | الظلفة | Tabuk | 5796915663 | 22 | grid | unverified | no | no | no | 435.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 52 | NEOM Community 1 | مجتمع نيوم 1 | Duba | 12390325533 | 16 | grid | unverified | no | no | no | 434.3 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 53 | احامر | احامر | Taymā' | 8850700244 | 9 | grid | unverified | no | no | no | 248.2 | landbridge:muwai | Madinah (tier 1) | none sourced | below 5k, no role |
| 54 | unnamed OSM node 5513837434 | unnamed OSM node 5513837434 | Tabuk | 5513837434 | 5 | grid | unverified | no | no | no | 467.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 55 | `Alaqan | علقان | Haql | 1236312468 | 0 | grid | unverified | no | no | no | 459.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 56 | Al Hudayrah | الهديرة | Tabuk | 1236320505 | 0 | grid | unverified | no | no | no | 363.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 57 | Al Hawja' | الهوج | Tabuk | 1236753456 | 0 | grid | unverified | no | no | no | 198.9 | landbridge:dawadmi | Tabuk (tier 2) | none sourced | below 5k, no role |
| 58 | Mughayra | مغيراء | Tabuk | 1236762595 | 0 | grid | unverified | no | no | no | 362.4 | landbridge:dawadmi | Tabuk (tier 2) | none sourced | below 5k, no role |
| 59 | unnamed OSM node 3358197802 | unnamed OSM node 3358197802 | Al-Wajh | 3358197802 | 0 | grid | unverified | no | no | no | 413.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 60 | unnamed OSM node 3358231400 | unnamed OSM node 3358231400 | Al-Wajh | 3358231400 | 0 | grid | unverified | no | no | no | 434.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 61 | الكتيب | الكتيب | Taymā' | 3731210955 | 0 | grid | unverified | no | no | no | 312.0 | landbridge:muwai | Tabuk (tier 2) | none sourced | below 5k, no role |
| 62 | الزراع | الزراع | Tabuk | 5796865934 | 0 | grid | unverified | no | no | no | 371.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 63 | رحيب | رحيب | Tabuk | 5796917273 | 0 | grid | unverified | no | no | no | 423.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 64 | السرو | السرو | Tabuk | 5809562348 | 0 | grid | unverified | no | no | no | 396.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 65 | شكاعه | شكاعه | Tabuk | 5809624027 | 0 | grid | unverified | no | no | no | 348.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 66 | الفارعه | الفارعه | Al-Wajh | 5809629988 | 0 | grid | unverified | no | no | no | 449.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 67 | حسمى | حسمى | Tabuk | 5809660573 | 0 | grid | unverified | no | no | no | 377.7 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 68 | الجو | الجو | Al-Wajh | 5810662573 | 0 | grid | unverified | no | no | no | 418.1 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 69 | بجده | بجده | Tabuk | 5810667905 | 0 | grid | unverified | no | no | no | 390.2 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 70 | Alsourah | الصورة | Duba | 5811552621 | 0 | grid | unverified | no | no | no | 464.9 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 71 | الزيته | الزيته | Haql | 5819241623 | 0 | grid | unverified | no | no | no | 416.8 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 72 | ضم | ضم | Tabuk | 5819241624 | 0 | grid | unverified | no | no | no | 377.7 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 73 | روى | روى | Tabuk | 5819291840 | 0 | grid | unverified | no | no | no | 373.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 74 | السنانيات | السنانيات | Taymā' | 6139976586 | 0 | grid | unverified | no | no | no | 294.1 | landbridge:muwai | Tabuk (tier 2) | none sourced | below 5k, no role |
| 75 | الشدخ | الشدخ | Umluj | 6768385362 | 0 | grid | unverified | no | no | no | 242.6 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 76 | فجر | فجر | Tabuk | 6768409870 | 0 | grid | unverified | no | no | no | 270.5 | landbridge:dawadmi | Tabuk (tier 2) | none sourced | below 5k, no role |
| 77 | قمراء بن قايم | قمراء بن قايم | Taymā' | 7023555018 | 0 | grid | unverified | no | no | no | 186.2 | landbridge:muwai | Madinah (tier 1) | none sourced | below 5k, no role |
| 78 | ثرف | ثرف | Haql | 7120399590 | 0 | grid | unverified | no | no | no | 442.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 79 | صروم | صروم | Umluj | 8721298626 | 0 | grid | unverified | no | no | no | 279.0 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 80 | المجمع | المجمع | Al-Wajh | 9250201292 | 0 | grid | unverified | no | no | no | 371.1 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 81 | العماير | العماير | Al-Wajh | 9255338629 | 0 | grid | unverified | no | no | no | 427.1 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 82 | السطيح | السطيح | Umluj | 9277814257 | 0 | grid | unverified | no | no | no | 215.7 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 83 | نُعظة | نُعظة | Umluj | 9279392144 | 0 | grid | unverified | no | no | no | 263.2 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 84 | الجريف | الجريف | Al-Wajh | 9286596427 | 0 | grid | unverified | no | no | no | 451.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 85 | الظبيبة | الظبيبة | Duba | 9299574398 | 0 | grid | unverified | no | no | no | 477.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 86 | المدقة | المدقة | Al-Wajh | 9307928497 | 0 | grid | unverified | no | no | no | 329.8 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 87 | Neom Construction Village | قرية نيوم الإنشائية | Duba | 9471511170 | 0 | grid | unverified | no | no | no | 411.9 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 88 | حديباء | حديباء | Al-Wajh | 9482631742 | 0 | grid | unverified | no | no | no | 422.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 89 | الحايل | الحايل | Umluj | 10595647316 | 0 | grid | unverified | no | no | no | 280.9 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 90 | نقبان | نقبان | Tabuk | 11060830552 | 0 | grid | unverified | no | no | no | 464.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 91 | أبو محيثلات | أبو محيثلات | Al-Wajh | 11118191152 | 0 | grid | unverified | no | no | no | 429.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 92 | الرقيطاء | الرقيطاء | Haql | 11494085765 | 0 | grid | unverified | no | no | no | 419.8 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 93 | Tawala | توله | Umluj | 11870738004 | 0 | grid | unverified | no | no | no | 310.0 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 94 | Tarim | تريم | Duba | 11871306953 | 0 | grid | unverified | no | no | no | 433.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 95 | Kulwah | كلوة | Tabuk | 11871636132 | 0 | grid | unverified | no | no | no | 362.4 | landbridge:dawadmi | Tabuk (tier 2) | none sourced | below 5k, no role |
| 96 | `Aynunah | عينونة | Duba | 11871651963 | 0 | grid | unverified | no | no | no | 431.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 97 | NEOM Construction Village 2 | NEOM Construction Village 2 | Duba | 12250497381 | 0 | grid | unverified | no | no | no | 471.7 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 98 | Trojena Pioneer Camp | Trojena Pioneer Camp | Tabuk | 12250556104 | 0 | grid | unverified | no | no | no | 445.8 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 99 | Neom Residential Camp 01 | Neom Residential Camp 01 | Al-Bad' | 12390254637 | 0 | grid | unverified | no | no | no | 470.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 100 | Neom Residential Camp 26 | Neom Residential Camp 26 | Duba | 12390325515 | 0 | grid | unverified | no | no | no | 436.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 101 | Neom Residential Camp 09 | Neom Residential Camp 09 | Al-Bad' | 12390325559 | 0 | grid | unverified | no | no | no | 449.3 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 102 | Neom Residential Camp 13 | Neom Residential Camp 13 | Duba | 12390325560 | 0 | grid | unverified | no | no | no | 447.4 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 103 | Neom Residential Camp 11 | Neom Residential Camp 11 | Duba | 12390325561 | 0 | grid | unverified | no | no | no | 447.8 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 104 | Neom Residential Camp 05 | Neom Residential Camp 05 | Al-Bad' | 12390340605 | 0 | grid | unverified | no | no | no | 455.5 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 105 | Turtle Bay Village | Turtle Bay Village | Umluj | 12400398910 | 0 | grid | unverified | no | no | no | 309.7 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 106 | NEOM Community 2 | 2 قرية نيوم | Duba | 12471383222 | 0 | grid | unverified | no | no | no | 413.8 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 107 | بئر عسيكر | بئر عسيكر | Umluj | 12477792819 | 0 | grid | unverified | no | no | no | 267.0 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 108 | المجالدة | المجالدة | Al-Wajh | 13020050818 | 0 | grid | unverified | no | no | no | 378.1 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 109 | السطيح | السطيح | Umluj | 13321902779 | 0 | grid | unverified | no | no | no | 258.2 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 110 | ابوطينة | ابوطينة | Al-Wajh | 13387175906 | 0 | grid | unverified | no | no | no | 458.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 111 | عمق | عمق | Umluj | 13681173788 | 0 | grid | unverified | no | no | no | 311.8 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 112 | راكان | راكان | Duba | 13965651314 | 0 | grid | unverified | no | no | no | 458.6 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 113 | العشيرة | العشيرة | Al-Wajh | 14003323939 | 0 | grid | unverified | no | no | no | 415.0 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 114 | الرمام | الرمام | Al-Wajh | 14003324078 | 0 | grid | unverified | no | no | no | 410.8 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 115 | الضبط | الضبط | Umluj | 14003595669 | 0 | grid | unverified | no | no | no | 309.4 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 116 | المسلق | المسلق | Al-Wajh | 14005179630 | 0 | grid | unverified | no | no | no | 438.3 | landbridge:jeddah | Tabuk (tier 2) | none sourced | below 5k, no role |
| 117 | ام الحيران | ام الحيران | Umluj | 14074085867 | 0 | grid | unverified | no | no | no | 241.7 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 118 | مسرورة | مسرورة | Umluj | 14074096068 | 0 | grid | unverified | no | no | no | 244.1 | landbridge:jeddah | Madinah (tier 1) | none sourced | below 5k, no role |
| 119 | قرية الجديد | قرية الجديد | Taymā' | 3360031773 | – | – | – | no | no | no | 251.5 | landbridge:muwai | Tabuk (tier 2) | none sourced | no dated population |

## 7. Exclusions

Every excluded row is in the table with its reason. In summary: the 107 below-5,000 settlements carry the reason `below 5,000 and no sourced economic role (A-screen-003)`, and the undated OSM tag (قرية الجديد) also has no population. Bi'r Ibn Hirmas (4,964) is the 5k boundary check: census figure below 5,000, OSM tag 5,975 not used.

## 8. Needs judgement (not resolved by guessing)

1. **Halat Ammar, census vs OSM.** Census ≥ 5,000 list omits it; OSM tag 5,293. Kept as a derived 5k row. Decide whether to drop it or get the census locality figure.
2. **Red Sea International Airport (Hanak) and Red Sea Global.** Their R1a nodes name Hanak and 'Red Sea coast', but neither is a settlement in the R1a universe, so the roles are not attached to any row. Decide whether to add Hanak as a settlement.
3. **NEOM.** The town figure (2,122) is a WorldPop grid value for a giga-project site under construction; the Port of NEOM has no location (node unlocated). The giga-project role is sourced (S-r1a-212), the population is not a settled figure.
4. **Terrain** is by governorate (A-tabuk-003), not a DEM class.
5. **Umluj's nearest metro** is Madinah (tier 1, 245 km), not Tabuk (tier 2). A-screen-013 nearest-by-distance; decide whether the Tabuk tier should cover Umluj.
6. **Committed distances** are indicative: Landbridge stops are unlocated proxies (A-tabuk-004).
7. **Umluj** has no sourced economic role.
8. **Dhiba port (Duba)**: the Mawani name is unverified (S-r1a-209 not read); the role rests on S-tabuk-007 and S-r1a-242.
9. **Haql spelling**: the S-073 list writes 'Haqil'; the register uses 'Haql' (the GASTAT primary spelling).

## 9. Sources

`docs/sources/r2-tabuk.csv` (21 rows): primary 2, secondary 13, unverified 6. The primary GASTAT exports are S-cp2-gastat-007 (governorates) and S-cp2-gastat-008 (cities of 5,000 or more); WorldPop is S-r1a-505; OSM ids and tags are S-r1a-210.

Label: screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.

