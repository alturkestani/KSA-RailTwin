> **Document version:** docs/regions/eastern.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_EASTERN) | Status: draft

# Eastern Province (المنطقة الشرقية): region register R2 (slug `eastern`)

**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. No modelled output appears in this file.

Registers: `cities/ksa/regions/eastern.parquet` and `eastern.csv` (same rows, same order). Built by `screening/sweeps/eastern/build.py` from the R1a settlement universe (`cities/ksa/zones/settlements.parquet`), the R1a economic nodes and the primary GASTAT exports. Register values were not typed in by hand.

## 1. Governorate count

| item | value | source |
|---|---|---|
| `governorates_gastat` | **12** Eastern rows in the 150-row GASTAT primary list (Census 2022 TA1 governorate export) | S-cp2-gastat-007; S-073 (150 governorate rows) |
| `governorates_listed` | **12** (one centre row per GASTAT governorate; the register has 12 distinct governorates) | this register |
| count in Arabic secondary sources | 13 (Al-Bayda listed as a 13th) | S-eastern-003 (Saudipedia, Arabic) |

**Discrepancy, written both ways:** Al-Bayda (البيضاء) appears in the Arabic secondary list (S-eastern-003) but is not one of the 150 GASTAT governorate rows (S-cp2-gastat-007), so it is an excluded row (`screened = false`; A-eastern-004). Counts reconcile to GASTAT (12 = 12). The 12 GASTAT governorate totals sum to **5,125,254**, equal to the Eastern regional total of 5,125,254 (S-cp2-gastat-007; S-cp2-gastat-003). Open for merge-stage (item 1).

| governorate (EN) | governorate (AR) | GASTAT 2022 total | centre row (name) | centre population |
|---|---|---|---|---|
| Abqaiq | بقيق | 64,632 | Abqaiq | 45,032 (official, verified) |
| Ad-Dammam | الدمام | 1,532,326 | Dammam | 1,386,166 (official, verified) |
| Al-Ahsa | الأحساء | 1,104,267 | Al-Hofuf | 729,606 (official, verified) |
| Al-Jubail | الجبيل | 505,162 | Al Jubayl | 302,446 (official, verified) |
| Al-Khafji | الخفجي | 84,316 | Al Khafji | 78,691 (official, verified) |
| Al-Khubar | الخبر | 658,550 | Al Khobar | 409,549 (official, verified) |
| Al-Qatif | القطيف | 552,442 | Qatif | 87,332 (official, verified) |
| Al-Udayd | العديد | 8,635 | Al-Udayd | — (no sourced figure) |
| An-Nuayriyah | النعيرية | 63,815 | Nuayriyah | 40,023 (official, verified) |
| Hafar Al-Batin | حفر الباطن | 467,007 | Hafar Al-Batin | 387,096 (official, verified) |
| Qaryat al-Ulya | قرية العليا | 21,788 | Qaryah al `Ulya | 10,961 (official, verified) |
| Ras Tannurah | رأس تنورة | 62,314 | Ra's Tannurah | 57,030 (official, verified) |

## 2. Counts

- Rows: **57** (12 governorate centres; 45 other rows: towns at or above 5,000 and 4 excluded rows).
- Towns at or above 10,000 (`tag_10k`): **29** = 28 official (GASTAT primary, verified) + 1 derived (OSM place tag, secondary) + 0 grid (no grid row passes the corroboration gate).
- Towns at or above 5,000 (`tag_5k`, sensitivity): **51**.
- Grid-only rows (WorldPop 2020, unverified): 12; of these 6 are at or above 10,000 and uncorroborated, so `tag_10k = false` (exclusion_reason set, screened true). Only Udhailiyah has a second method (gastat2010_city_growth, 9,409 vs grid 14,071: 33 % apart, over the 30 % band), so it is not corroborated.
- Universe settlements in the region: 215; 56 are register rows (plus the pilot's Al-Jubail row, which has no universe settlement); the rest are below 5,000 (or undated) and are not register rows, counted here only.
- `screened = false`: 4 rows (section 4).
- `pilot_sample` and `threshold_50k`: null in this R2 register.

## 3. Register table

Population cell: figure (pop_type, pop_source_status). Distances in km (haversine to the nearest station, R1a); road minutes are OSRM car (R1a skims). `—` = not available.

| # | name (EN) | name (AR) | governorate | centre | population | ≥10k | ≥5k | screened | existing: km / road min | metro: nearest, tier, km | committed: km / road min | roles (sourced) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Abqaiq | بقيق | Abqaiq | yes | 45,032 (official, verified) | yes | yes | yes | 0.5 / 2.9 | Dhahran (tier 1) / T1 / 60.4 | 70.7 / 60.6 | energy |
| 2 | Al Jubayl | الجبيل | Al-Jubail | yes | 302,446 (official, verified) | yes | yes | yes | 80.8 / 64.5 | Dammam (tier 1) / T1 / 77.0 | 77.0 / 61.0 | port, port, industrial_city, energy, university |
| 3 | Al Khafji | الخفجي | Al-Khafji | yes | 78,691 (official, verified) | yes | yes | yes | 275.8 / 200.6 | Dammam (tier 1) / T1 / 272.1 | 13.1 / 15.9 | border_crossing |
| 4 | Al Khobar | الخبر | Al-Khubar | yes | 409,549 (official, verified) | yes | yes | yes | 13.7 / 15.7 | Al Khobar (tier 1) / T1 / 0.0 | 17.4 / 17.1 | border_crossing |
| 5 | Al-Hofuf | الهفوف | Al-Ahsa | yes | 729,606 (official, verified) | yes | yes | yes | 2.6 / 7.1 | Dhahran (tier 1) / T1 / 116.1 | 129.5 / 108.6 | airport, industrial_city, industrial_city, heritage, university |
| 6 | Al-Udayd | العديد | Al-Udayd | yes | — (no sourced figure) | no | no | yes | 204.6 / 277.0 | Al Khobar (tier 1) / T1 / 224.1 | 55.7 / 165.5 | none sourced |
| 7 | Dammam | الدمام | Ad-Dammam | yes | 1,386,166 (official, verified) | yes | yes | yes | 3.7 / 6.3 | Dammam (tier 1) / T1 / 0.0 | 0.0 / 0.0 | airport, port, industrial_city, industrial_city, industrial_city, university |
| 8 | Hafar Al-Batin | حفر الباطن | Hafar Al-Batin | yes | 387,096 (official, verified) | yes | yes | yes | 283.9 / 228.1 | Buraidah (tier 2) / T2 / 305.3 | 239.8 / 230.8 | industrial_city, university |
| 9 | Nuayriyah | النعيرية | An-Nuayriyah | yes | 40,023 (official, verified) | yes | yes | yes | 201.7 / 145.9 | Dammam (tier 1) / T1 / 198.1 | 116.3 / 93.9 | none sourced |
| 10 | Qaryah al `Ulya | قرية العليا | Qaryat al-Ulya | yes | 10,961 (official, verified) | yes | yes | yes | 265.9 / 212.1 | Dammam (tier 1) / T1 / 268.7 | 127.6 / 145.4 | none sourced |
| 11 | Qatif | القطيف | Al-Qatif | yes | 87,332 (official, verified) | yes | yes | yes | 20.3 / 24.3 | Dammam (tier 1) / T1 / 16.5 | 16.5 / 20.2 | none sourced |
| 12 | Ra's Tannurah | رأس تنورة | Ras Tannurah | yes | 57,030 (official, verified) | yes | yes | yes | 33.6 / 43.7 | Dammam (tier 1) / T1 / 30.3 | 30.3 / 40.2 | port, energy |
| 13 | (unnamed node 3154057250) |  | Al-Ahsa | no | 7,839 (grid, unverified) | no | yes | yes | 154.7 / 137.7 | Riyadh (tier 1) / T1 / 239.2 | 237.2 / 197.0 | none sourced |
| 14 | AL THIYBIA | الذيبية | Hafar Al-Batin | no | 14,442 (derived, secondary) | yes | yes | yes | 238.9 / 199.7 | Buraidah (tier 2) / T2 / 260.2 | 272.5 / 277.9 | none sourced |
| 15 | Al Ahsa | الأحساء | Al-Ahsa | no | — (no sourced figure) | no | no | no | 0.6 / 4.4 | Dhahran (tier 1) / T1 / 115.4 | 128.6 / 105.9 | none sourced |
| 16 | Al Awjam | الأوجام | Al-Qatif | no | 16,147 (official, verified) | yes | yes | yes | 24.9 / 25.3 | Dammam (tier 1) / T1 / 21.2 | 21.2 / 21.8 | none sourced |
| 17 | Al Badrani | البدراني | Al-Qatif | no | 8,041 (grid, unverified) | no | yes | yes | 20.1 / 19.6 | Dammam (tier 1) / T1 / 16.5 | 16.5 / 16.1 | none sourced |
| 18 | Al Ghuwaybah | الغويبة | Al-Ahsa | no | 8,880 (grid, unverified) | no | yes | yes | 18.8 / 23.1 | Dhahran (tier 1) / T1 / 123.4 | 137.6 / 125.2 | none sourced |
| 19 | Al Jish | الجش | Al-Qatif | no | 22,343 (official, verified) | yes | yes | yes | 16.5 / 22.0 | Dammam (tier 1) / T1 / 12.9 | 12.9 / 17.8 | none sourced |
| 20 | Al Khuwaildiyah | الخويلدية | Al-Qatif | no | 6,578 (official, verified) | no | yes | yes | 20.8 / 24.9 | Dammam (tier 1) / T1 / 17.0 | 17.0 / 20.8 | none sourced |
| 21 | Al Marah | المراح | Al-Ahsa | no | 5,633 (derived, secondary) | no | yes | yes | 23.0 / 22.8 | Dhahran (tier 1) / T1 / 94.9 | 107.3 / 93.6 | none sourced |
| 22 | Al Mubarraz | المبرز | Al-Ahsa | no | — (no sourced figure) | no | no | no | 3.2 / 7.1 | Dhahran (tier 1) / T1 / 112.2 | 125.4 / 105.8 | none sourced |
| 23 | Al Oyun | العيون | Al-Ahsa | no | 35,226 (official, verified) | yes | yes | yes | 24.6 / 22.2 | Dhahran (tier 1) / T1 / 94.6 | 106.8 / 89.4 | none sourced |
| 24 | Al Qudayh | القديح | Al-Qatif | no | 22,492 (official, verified) | yes | yes | yes | 22.3 / 26.8 | Dammam (tier 1) / T1 / 18.6 | 18.6 / 22.6 | none sourced |
| 25 | Al `Awwamiyah | العوامية | Al-Qatif | no | 26,276 (official, verified) | yes | yes | yes | 24.4 / 29.7 | Dammam (tier 1) / T1 / 20.6 | 20.6 / 25.5 | none sourced |
| 26 | Al `Aziziyah | العزيزية | Al-Khubar | no | 14,977 (grid, unverified) | no | yes | yes | 26.4 / 29.0 | Al Khobar (tier 1) / T1 / 13.7 | 29.9 / 30.9 | none sourced |
| 27 | Al-Bayda | البيضاء | Abqaiq | no | — (no sourced figure) | no | no | no | 5.3 / 43.4 | Dhahran (tier 1) / T1 / 59.6 | 68.9 / 76.2 | none sourced |
| 28 | Al-Jubail (Al-Ahsa) | الجبيل | Al-Ahsa | no | 9,994 (official, verified) | no | yes | yes | 9.6 / — | Dammam–Khobar–Dhahran (Dhahran node) / T1 / 109.0 | — / — | none sourced |
| 29 | An Nabiyah | النابية | Al-Qatif | no | 13,018 (official, verified) | yes | yes | yes | 14.0 / 16.8 | Dammam (tier 1) / T1 / 10.6 | 10.6 / 13.3 | none sourced |
| 30 | Ar Rabi`iyah | الربيعية | Al-Qatif | no | 14,660 (grid, unverified) | no | yes | yes | 18.6 / 28.8 | Dammam (tier 1) / T1 / 15.1 | 15.1 / 24.6 | none sourced |
| 31 | As Sabat | السباط | Al-Ahsa | no | 12,938 (grid, unverified) | no | yes | yes | 14.9 / 21.5 | Dhahran (tier 1) / T1 / 109.3 | 123.4 / 123.1 | none sourced |
| 32 | As Saffaniyah | السفانية | Al-Khafji | no | 6,259 (derived, secondary) | no | yes | yes | 223.3 / 167.4 | Dammam (tier 1) / T1 / 219.6 | 68.9 / 50.5 | none sourced |
| 33 | As Su`ayyirah | السعيرة | Hafar Al-Batin | no | 11,144 (grid, unverified) | no | yes | yes | 296.3 / 213.3 | Dammam (tier 1) / T1 / 299.2 | 117.5 / 148.0 | none sourced |
| 34 | Ash Shaharin | الشهارين | Al-Ahsa | no | 5,518 (official, verified) | no | yes | yes | 8.8 / 15.3 | Dhahran (tier 1) / T1 / 110.9 | 124.6 / 116.9 | none sourced |
| 35 | At Tubi | التوبي | Al-Qatif | no | 8,801 (official, verified) | no | yes | yes | 21.2 / 25.6 | Dammam (tier 1) / T1 / 17.5 | 17.5 / 21.4 | none sourced |
| 36 | Ath-Thuqbah | الثقبة | Al-Khubar | no | 248,888 (official, verified) | yes | yes | yes | 16.6 / 18.1 | Al Khobar (tier 1) / T1 / 3.5 | 20.2 / 20.2 | none sourced |
| 37 | Bani M`en | أبو معن | Al-Qatif | no | 6,093 (derived, secondary) | no | yes | yes | 42.2 / 39.8 | Dammam (tier 1) / T1 / 38.6 | 38.6 / 35.4 | none sourced |
| 38 | Darin | دارين | Al-Qatif | no | 7,090 (grid, unverified) | no | yes | yes | 16.4 / 28.9 | Dammam (tier 1) / T1 / 12.9 | 12.9 / 24.8 | none sourced |
| 39 | Dhahran | الظهران | Ad-Dammam | no | 143,936 (official, verified) | yes | yes | yes | 12.6 / 18.7 | Dhahran (tier 1) / T1 / 0.0 | 15.7 / 20.8 | university, military |
| 40 | Hillat Muhaish | حلة محيش | Al-Qatif | no | 7,287 (official, verified) | no | yes | yes | 19.2 / 23.9 | Dammam (tier 1) / T1 / 15.5 | 15.5 / 19.7 | none sourced |
| 41 | Imhaish | محيش | Al-Qatif | no | 5,813 (grid, unverified) | no | yes | yes | 19.4 / 24.4 | Dammam (tier 1) / T1 / 15.7 | 15.7 / 20.2 | none sourced |
| 42 | Jarudiyah | الجارودية | Al-Qatif | no | 20,986 (official, verified) | yes | yes | yes | 20.3 / 25.8 | Dammam (tier 1) / T1 / 16.6 | 16.6 / 21.6 | none sourced |
| 43 | King Khālid Military City | مدينة الملك خالد العسكرية | Hafar Al-Batin | no | 25,356 (official, verified) | yes | yes | yes | 219.3 / 226.7 | Buraidah (tier 2) / T2 / 240.7 | 287.3 / 304.8 | military |
| 44 | Mallahah | الملاحة | Al-Qatif | no | 5,544 (official, verified) | no | yes | yes | 17.1 / 23.1 | Dammam (tier 1) / T1 / 13.5 | 13.5 / 18.9 | none sourced |
| 45 | Mulayjah | مليجة | An-Nuayriyah | no | 5,925 (derived, secondary) | no | yes | yes | 193.4 / 161.3 | Dammam (tier 1) / T1 / 190.7 | 138.5 / 109.3 | none sourced |
| 46 | Qaisumah | القيصومة | Hafar Al-Batin | no | 27,307 (official, verified) | yes | yes | yes | 274.7 / 236.8 | Buraidah (tier 2) / T2 / 306.1 | 224.9 / 241.5 | airport |
| 47 | Ras Tanura | رأس تنورة | Ras Tannurah | no | — (no sourced figure) | no | no | no | 33.6 / 43.7 | Dammam (tier 1) / T1 / 30.3 | 30.3 / 40.2 | none sourced |
| 48 | Safwa | صفوى | Al-Qatif | no | 45,676 (official, verified) | yes | yes | yes | 32.0 / 35.6 | Dammam (tier 1) / T1 / 28.3 | 28.3 / 32.1 | none sourced |
| 49 | Salwa | سلوى | Al-Udayd | no | 5,566 (grid, unverified) | no | yes | yes | 139.7 / 103.7 | Al Khobar (tier 1) / T1 / 182.7 | 106.2 / 81.7 | none sourced |
| 50 | Sanabis | سنابس | Al-Qatif | no | 14,243 (grid, unverified) | no | yes | yes | 19.1 / 30.4 | Dammam (tier 1) / T1 / 15.7 | 15.7 / 26.3 | none sourced |
| 51 | Sayhat | سيهات | Al-Qatif | no | 84,818 (official, verified) | yes | yes | yes | 11.1 / 16.6 | Dammam (tier 1) / T1 / 7.5 | 7.5 / 12.4 | none sourced |
| 52 | Tarout | تاروت | Al-Qatif | no | 117,646 (official, verified) | yes | yes | yes | 19.8 / 30.9 | Dammam (tier 1) / T1 / 16.3 | 16.3 / 26.7 | none sourced |
| 53 | Udhailiyah | العضيلية | Al-Ahsa | no | 14,071 (grid, unverified) | no | yes | yes | 38.5 / 43.2 | Dhahran (tier 1) / T1 / 152.6 | 165.1 / 130.8 | none sourced |
| 54 | Umm Al Hamam | أم الحمام | Al-Qatif | no | 12,818 (official, verified) | yes | yes | yes | 17.8 / 22.9 | Dammam (tier 1) / T1 / 14.1 | 14.1 / 18.7 | none sourced |
| 55 | Umm as Sahik | أم الساهك | Al-Qatif | no | 15,378 (official, verified) | yes | yes | yes | 34.3 / 32.6 | Dammam (tier 1) / T1 / 30.6 | 30.6 / 29.1 | none sourced |
| 56 | `Inak | عنك | Al-Qatif | no | 20,038 (official, verified) | yes | yes | yes | 15.7 / 19.8 | Dammam (tier 1) / T1 / 12.0 | 12.0 / 15.6 | none sourced |
| 57 | النقيرة | النقيرة | An-Nuayriyah | no | — (no sourced figure) | no | no | yes | 246.0 / 204.6 | Dammam (tier 1) / T1 / 242.4 | 73.6 / 91.6 | none sourced |

## 4. Exclusions and rows not carried

| name | governorate | reason |
|---|---|---|
| Al Ahsa | Al-Ahsa | duplicate of the Al-Hofuf / Al-Ahsa urban row KSA-ST-00003: the OSM 'Al Ahsa' node (3 km away) carries a contributor value of 903,597 that is an oasis-wide tag, not a town figure; the tag is not used (A-eastern-003) |
| Al Mubarraz | Al-Ahsa | Al-Mubarraz village (grid, 32,327): the GASTAT city Al-Mubarraz (299,501) is carried on KSA-ST-00003 as part of the Al-Hofuf-Al-Mubarraz row (A-eastern-003); the grid figure is not used |
| Al-Bayda | Abqaiq | Al-Bayda: not one of the 12 GASTAT Eastern governorates (S-cp2-gastat-007); listed as a 13th governorate in Arabic sources (S-eastern-003); R1a grid value (32 persons) not used; centre not located (A-eastern-004) |
| Ras Tanura | Ras Tannurah | duplicate of KSA-ST-01101 (Ra's Tannurah) on the same OSM node 1237805652; R1a grid value (6,445) not used |

Not register rows (counted, not screened): the other universe settlements below 5,000 or without a sourced population. Rows with no sourced population stay `population = null`; the funnel must not read them as zero.

## 5. Economic roles

Every role names the source that ties it to that town (R1a economic nodes, `source_id`; S-eastern-001 and S-eastern-009 for the two military roles). Counts: airport 3, border_crossing 2, energy 3, heritage 1, industrial_city 7, military 2, port 4, university 5.

Not carried as roles: Ras Al-Khair port, mining and industrial city (no register row; R1a nodes located False or no town row); Al-Ruqi, Al-Salmi, Al-Batha and Salwa border posts (no town row; Salwa unverified in R1a). Settlement rows with no node get no role.

## 6. Geo-verify step (record-only)

Run: `screening.geo_verify.cli estimate --which no-pop --region eastern --seed 1` (method log `geo-est-c172b6d4`, `geo-est-4166a87b`, `geo-est-2628554c`). **The CLI reads `cities/ksa/regions/pilot-*.parquet` only**, so it evaluated the three pilot rows, not this register (a CLI change is needed for R2; not made here, shared code). Results, mapped to the R2 rows by coordinate:

- Ras Tanura (pilot row, same coordinates as the R2 centre Ra's Tannurah): estimate central 22,923 (range 7,013–39,756; 6,491 footprint buildings; buildings method 24,925). The point-window grid value there is 21,081, against 6,445 in the R1a allocation (A-r1a-004): the two grid methods disagree at this point. Record-only (the back-test gate fails both estimators, GEO_VERIFY); not used. The sourced figure stays 57,030 (primary export).
- Al-Udayd (centre): no footprint cluster (0 buildings). No estimate. Population stays null.
- Al-Bayda: no footprint cluster (0 buildings). No estimate. Row excluded.
- Stations and planned stops: not in this step (no station candidates for the Eastern Province in `station_sites.yaml` yet).

## 7. Method and limits

- Populations: GASTAT Census 2022 TA1 primary exports (S-cp2-gastat-007 for governorates, S-cp2-gastat-008 for cities of 5,000 or more), matched by `screening/gastat_crosswalk.yaml` (A-screen-038). Derived: OSM place population tags (S-r1a-210), and only where dated (A-eastern-005). Grid: WorldPop 2020 constrained (S-r1a-505), unverified; grid rows ≥ 10k are gated (A-screen-031 to 033).
- Distances: haversine to the nearest station (R1a, `dist_existing_km` and `dist_committed_km`) and to the metro reference city node (`dist_metro_km`, A-r1a-009); road minutes OSRM car (`road_min_*`, R1a skims). The committed (GCC railway) station positions are unlocated (R1a flag), so committed distances are approximate and are labelled committed, never existing.
- Terrain: `terrain_class` null for every row (no R1a DEM class for Eastern towns; not guessed).
- The Al-Jubail (Al-Ahsa) row takes its coordinates from the pilot register (OSM neighbourhood way, S-eastern-004) because the primary export's 'Aljabil' (9,994) has no R1a settlement.
- The Al-Hofuf row is the combined Al-Hofuf 430,105 + Al-Mubarraz 299,501 (crosswalk, A-eastern-003).

## 8. Sources

S-cp2-gastat-007 (governorates, 150 rows), S-cp2-gastat-008 (cities ≥ 5,000, 271 rows + Other), S-cp2-gastat-003 (regional TA9 totals), S-073 (governorate row list), S-cp2-gastat-001 (relayed cross-check only), S-r1a-210 (OSM GCC extract: ids, coordinates, OSM population tags, ODbL), S-r1a-505 (WorldPop 2020 constrained, CC BY 4.0), R1a economic-node sources (S-r1a-*, S-cp1-*), S-eastern-001/003/009 (secondary; roles and military rows), S-eastern-004 (Nominatim object ids for the pilot Al-Jubail row). New ids in `docs/sources/r2-eastern.csv`.

## 9. Needs judgement (not resolved by guessing)

1. Governorate count: GASTAT 12 vs Saudipedia 13 (Al-Bayda). Al-Bayda is excluded here; a decision is needed on whether it is a governorate.
2. Al-Hofuf: keep the combined 729,606 row (crosswalk) or split Al-Hofuf (430,105) and Al-Mubarraz (299,501) into two rows (the OSM nodes must then be found).
3. Ra's Tannurah: the primary export labels this city 'Rahimah' (57,030); matched to the Ra's Tannurah node (crosswalk). Confirm the name and governorate-centre choice.
4. Al-Jubail (Al-Ahsa, 9,994): the primary export figure, the pilot's neighbourhood coordinates and the Al-Jubail (Al-Jubayl) name clash. Confirm the location and whether it is a town.
5. OSM-tag towns (derived, secondary): AL THIYBIA (14,442, counted at 10k), As Saffaniyah, Bani M'en, Mulayjah, Al Marah, the Nuqayrah node: confirm they are not GASTAT-tabulated towns under other names; the 10k count depends on AL THIYBIA. AL THIYBIA (28.12 N, 45.67 E) is placed in the Hafar Al-Batin governorate by the R1a polygon; check the location and governorate before use.
6. Grid rows ≥ 10k (Ar Rabi'iyah, Aziziyah, Sanabis, As Su'ayyirah, Darin and others): none passes the corroboration gate. The 2010-growth method (A-screen-035) was run only for Udhailiyah.
7. Al-Khobar vs Ath-Thuqbah: Thuqbah is 248,888 (GASTAT city) inside the Dammam–Khobar–Dhahran metro. The commuter-belt decision (R2) decides whether it is a separate row.
8. Military roles (King Khalid Military City; Dhahran air base): the first is a census row, the second a search extract (S-eastern-009). Confirm.
9. Terrain class (R1a DEM classification) is null for all Eastern rows.
10. Governorate-centre rows: Al-Udayd (no sourced town figure; GASTAT governorate total 8,635 is not a town figure).
11. Schema: `energy` is in the role list; Abqaiq and Ras Tanura are recorded with energy roles where a node exists.

