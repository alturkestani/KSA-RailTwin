> **Document version:** docs/regions/makkah.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_MAKKAH) | Status: draft

# Region register: Makkah (مكة المكرمة), R2 sweep

Screening input, not a forecast. Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

## 1. Counts

- Governorates: `governorates_gastat` = 17 (S-cp2-gastat-007 joined to the S-073 names; sum 8,021,463 = S-soc-339). `governorates_listed` = 17. They match.
- Rows: 77; governorate centres: 17 (all 17 governorates have a row; Al-Ardiyat's centre is a centroid; its distances are to located stations, not to the alignment).
- Rows with `tag_10k` true: 16. Rows with `tag_5k` true: 68.
- Grid-only rows at 10,000 or more held out of `tag_10k` (uncorroborated, A-screen-031/032): 12.
- Economic roles: sourced for the towns listed in section 4; roles not assessed for the rest (empty list means not sourced).
- Terrain: not assessed (no DEM class in the R1a settlement universe); `terrain_class` is null everywhere.
- Road minutes: OSRM free-flow skims from R1a (S-r1a-809, uncalibrated) where the universe has them.

## 2. Register

| name (EN) | name (AR) | governorate | pop | pop type | status | 10k | 5k | dist exist km | road min exist | dist metro km (tier) | screened | exclusion |
|---|---|---|---:|---|---|---|---|---:|---:|---|---|---|
| Adham | أضم | Adam | 9,022 | official | secondary | n | y | 156.2 | 259 | 103.2 (Taif, T2) | y |  |
| Al-Ardiyat | العرضيات | Al-Ardiyat |  |  |  | n | n | 297.3 |  | 244.2 (Taif, T2) | n | governorate centre: seat town not located and no sourced population |
| Namerah | نمرة | Al-Ardiyat | 9,283 | official | verified | n | y | 282.7 | 293 | 175.6 (Abha, T2) | y |  |
| Thurayban | ثريبان | Al-Ardiyat | 2,416 | grid | unverified | n | n | 305.8 | 328 | 153.8 (Abha, T2) | n | below 5,000 (population 2416, grid) |
| Al Jumum | الجموم | Al-Jumum | 41,089 | official | verified | y | y | 24.4 | 30 | 25.9 (Makkah, T1) | y |  |
| `Usfan | عسفان | Al-Jumum | 5,761 | grid | unverified | n | y | 34.5 | 48 | 45.3 (Jeddah, T1) | y |  |
| Al Kamil | الكامل | Al-Kamil | 3,151 | official | secondary | n | n | 64.8 | 106 | 93.8 (Makkah, T1) | y |  |
| Al Khurmah | الخرمة | Al-Khurmah | 28,491 | official | verified | y | y | 238.2 | 227 | 181.5 (Taif, T2) | y |  |
| Al Lith | الليث | Al-Lith | 20,811 | official | verified | y | y | 150.1 | 147 | 126.0 (Taif, T2) | y |  |
| غميقة | غميقة | Al-Lith | 12,869 | grid | unverified | n | y | 142.2 | 169 | 107.7 (Taif, T2) | y | grid-only population, uncorroborated |
| Al Wasqah | الوسقة | Al-Lith | 10,438 | grid | unverified | n | y | 178.8 | 168 | 144.0 (Taif, T2) | y | grid-only population, uncorroborated |
| سلم الزواهر | سلم الزواهر | Al-Lith |  |  |  | n | n | 203.0 | 210 | 164.3 (Taif, T2) | n | no sourced population: OSM tag without a year |
| Al Muwayh | المويه | Al-Muwayh | 7,278 | official | verified | n | y | 233.0 | 198 | 190.0 (Taif, T2) | y |  |
| Almargab | المرقب | Al-Muwayh | 6,019 | grid | unverified | n | y | 207.5 | 221 | 176.6 (Taif, T2) | y |  |
| Diri | ضري | Al-Muwayh | 5,382 | grid | unverified | n | y | 208.8 | 220 | 177.5 (Taif, T2) | y |  |
| Umm al Dawm | أم الدوم | Al-Muwayh | 5,274 | official | verified | n | y | 210.1 | 223 | 179.3 (Taif, T2) | y |  |
| Zalim | ظلم | Al-Muwayh | 5,090 | derived | secondary | n | y | 285.0 | 229 | 242.4 (Taif, T2) | y |  |
| Al Qunfudhah | القنفذة | Al-Qunfudhah | 42,447 | official | verified | y | y | 288.1 | 247 | 181.1 (Abha, T2) | y |  |
| Al Quoz | القوز | Al-Qunfudhah | 23,391 | derived | secondary | y | y | 314.9 | 266 | 151.2 (Abha, T2) | y |  |
| Al Mozailef | المظيلف | Al-Qunfudhah | 9,769 | official | verified | n | y | 247.0 | 215 | 203.7 (Taif, T2) | y |  |
| عنيكر | عنيكر | Al-Qunfudhah | 6,720 | grid | unverified | n | y | 320.2 | 285 | 151.1 (Abha, T2) | y |  |
| البيضين | البيضين | Al-Qunfudhah | 5,644 | grid | unverified | n | y | 344.7 | 292 | 130.9 (Abha, T2) | y |  |
| unnamed OSM node 8117392315 | unnamed OSM node 8117392315 | Al-Qunfudhah | 2,781 | grid | unverified | n | n | 308.9 | 300 | 147.5 (Abha, T2) | n | below 5,000 (population 2781, grid) |
| At Ta'if | الطائف | At-Ta'if | 563,282 | official | verified | y | y | 67.0 | 76 | 0.0 (Taif, T2) | y |  |
| Al Hawiyah | الحوية | At-Ta'if | 171,610 | official | verified | y | y | 74.0 | 81 | 21.4 (Taif, T2) | y |  |
| As Sayl as Saghir | السيل الصغير | At-Ta'if | 13,850 | official | verified | y | y | 72.5 | 79 | 27.1 (Taif, T2) | y |  |
| Shaqsan | شقصان | At-Ta'if | 11,688 | grid | unverified | n | y | 113.8 | 111 | 46.9 (Taif, T2) | y | grid-only population, uncorroborated |
| As Sayl al Kabir | السيل الكبير | At-Ta'if | 9,663 | grid | unverified | n | y | 68.9 | 66 | 39.6 (Taif, T2) | y |  |
| Qiya | قيا | At-Ta'if | 9,262 | official | verified | n | y | 132.0 | 127 | 65.2 (Taif, T2) | y |  |
| رحاب | رحاب | At-Ta'if | 9,205 | grid | unverified | n | y | 65.9 | 87 | 21.2 (Taif, T2) | y |  |
| Al `Arfa' | العرفاء | At-Ta'if | 9,168 | grid | unverified | n | y | 86.9 | 92 | 36.0 (Taif, T2) | y |  |
| Ushayrah | عشيرة | At-Ta'if | 8,425 | derived | secondary | n | y | 96.9 | 119 | 59.5 (Taif, T2) | y |  |
| As Sudayrah | سديرة | At-Ta'if | 7,261 | grid | unverified | n | y | 110.0 | 132 | 46.0 (Taif, T2) | y |  |
| Assel | السيل | At-Ta'if | 7,157 | grid | unverified | n | y | 69.9 | 65 | 39.4 (Taif, T2) | y |  |
| ريع الذياب | ريع الذياب | At-Ta'if | 6,898 | grid | unverified | n | y | 72.1 | 79 | 26.4 (Taif, T2) | y |  |
| غزايل | غزايل | At-Ta'if | 5,847 | grid | unverified | n | y | 141.8 | 134 | 75.6 (Taif, T2) | y |  |
| Al Qasr | القصر | At-Ta'if | 5,794 | grid | unverified | n | y | 128.3 | 190 | 135.4 (Makkah, T1) | y |  |
| Al Hada | الهدا | At-Ta'if | 5,639 | official | verified | n | y | 51.7 | 62 | 17.4 (Taif, T2) | y |  |
| Ash Shafa | الشفا | At-Ta'if | 2,151 | grid | unverified | n | n | 66.7 | 102 | 24.8 (Taif, T2) | n | below 5,000 (population 2151, grid) |
| Bahrah | بحرة | Bahrah | 70,118 | official | verified | y | y | 24.8 | 25 | 33.0 (Jeddah, T1) | y |  |
| Bahrat al Qadimah | بحرة القديمة | Bahrah | 19,929 | grid | unverified | n | y | 28.0 | 30 | 34.6 (Makkah, T1) | y | grid-only population, uncorroborated |
| Hadda | حداء | Bahrah | 13,273 | grid | unverified | n | y | 24.2 | 29 | 28.1 (Makkah, T1) | y | grid-only population, uncorroborated |
| Shu`aybah | الشعيبة | Bahrah | 5,286 | official | verified | n | y | 85.1 | 86 | 86.8 (Makkah, T1) | y |  |
| Jeddah | جدة | Jiddah | 3,712,917 | official | verified | y | y | 8.2 | 16 | 0.0 (Jeddah, T1) | y |  |
| Thuwal | ثول | Jiddah | 26,957 | official | verified | y | y | 17.4 | 18 | 81.7 (Jeddah, T1) | y |  |
| Dhahban | ذهبان | Jiddah | 9,436 | official | verified | n | y | 30.6 | 36 | 42.7 (Jeddah, T1) | y |  |
| Khulays | خليص | Khulays | 20,139 | official | verified | y | y | 32.5 | 35 | 68.9 (Jeddah, T1) | y |  |
| Ghran | غران | Khulays | 6,400 | derived | secondary | n | y | 39.6 | 48 | 50.5 (Jeddah, T1) | y |  |
| Mecca | مكة | Makkah al-Mukarramah | 2,385,509 | official | verified | y | y | 4.0 | 8 | 0.0 (Makkah, T1) | y |  |
| Ash Sharai | الشرائع | Makkah al-Mukarramah | 114,461 | grid | unverified | n | y | 17.4 | 23 | 13.5 (Makkah, T1) | y | grid-only population, uncorroborated |
| Al Juranah | الجعرانة | Makkah al-Mukarramah | 38,060 | grid | unverified | n | y | 23.5 | 32 | 20.5 (Makkah, T1) | y | grid-only population, uncorroborated |
| Shara'i` al Mujahidin | شرائع المجاهدين | Makkah al-Mukarramah | 17,285 | grid | unverified | n | y | 19.4 | 22 | 15.7 (Makkah, T1) | y | grid-only population, uncorroborated |
| As Sifyani | السفياني | Makkah al-Mukarramah | 15,670 | grid | unverified | n | y | 8.2 | 16 | 6.1 (Makkah, T1) | y | grid-only population, uncorroborated |
| Al Hamra | الحمراء | Makkah al-Mukarramah | 14,572 | grid | unverified | n | y | 1.9 | 9 | 5.5 (Makkah, T1) | y | grid-only population, uncorroborated |
| ريع وصيق وفقاسة نعمان | ريع وصيق وفقاسة نعمان | Makkah al-Mukarramah | 11,076 | grid | unverified | n | y | 28.1 | 29 | 24.5 (Makkah, T1) | y | grid-only population, uncorroborated |
| Murshidiyah | المرشدية | Makkah al-Mukarramah | 11,037 | grid | unverified | n | y | 8.0 | 15 | 8.8 (Makkah, T1) | y | grid-only population, uncorroborated |
| At Tanim | التنعيم | Makkah al-Mukarramah | 9,149 | grid | unverified | n | y | 7.4 | 16 | 7.2 (Makkah, T1) | y |  |
| AshShu`bah | الشعبة | Makkah al-Mukarramah | 8,507 | grid | unverified | n | y | 22.8 | 34 | 18.9 (Makkah, T1) | y |  |
| Al Nawariyah | النوارية | Makkah al-Mukarramah | 7,458 | grid | unverified | n | y | 15.8 | 21 | 16.5 (Makkah, T1) | y |  |
| Ren | رين | Makkah al-Mukarramah | 7,225 | grid | unverified | n | y | 37.0 | 39 | 30.2 (Taif, T2) | y |  |
| `AbidalQurashi | عابد القرشي | Makkah al-Mukarramah | 6,542 | grid | unverified | n | y | 24.7 | 33 | 20.9 (Makkah, T1) | y |  |
| Bashm | بشم | Makkah al-Mukarramah | 6,517 | grid | unverified | n | y | 7.9 | 13 | 6.8 (Makkah, T1) | y |  |
| Wadi Ashara | وادي الشراء | Makkah al-Mukarramah | 6,487 | grid | unverified | n | y | 39.1 | 39 | 28.4 (Taif, T2) | y |  |
| شرائع النخل | شرائع النخل | Makkah al-Mukarramah | 5,610 | grid | unverified | n | y | 30.4 | 51 | 26.6 (Makkah, T1) | y |  |
| Missan | ميسان | Maysan | 5,227 | derived | secondary | n | y | 132.7 | 166 | 73.8 (Taif, T2) | y |  |
| بني سعد | بني سعد | Maysan | 6,482 | grid | unverified | n | y | 118.1 | 136 | 54.4 (Taif, T2) | y |  |
| unnamed OSM node 295919137 | unnamed OSM node 295919137 | Maysan | 6,007 | grid | unverified | n | y | 109.5 | 126 | 45.5 (Taif, T2) | y |  |
| حداد بني مالك | حداد بني مالك | Maysan | 3,528 | grid | unverified | n | n | 159.6 | 182 | 99.7 (Taif, T2) | n | below 5,000 (population 3528, grid) |
| القريع | القريع | Maysan | 1,874 | grid | unverified | n | n | 170.1 | 199 | 112.4 (Taif, T2) | n | below 5,000 (population 1874, grid) |
| Rabigh | رابغ | Rabigh | 72,928 | official | verified | y | y | 45.0 | 36 | 139.6 (Jeddah, T1) | y |  |
| Saabar | صعبر | Rabigh | 6,237 | derived | secondary | n | y | 3.1 | 6 | 100.0 (Jeddah, T1) | y |  |
| Masturah | مستورة | Rabigh | 6,220 | official | verified | n | y | 85.0 | 68 | 169.9 (Madinah, T1) | y |  |
| حجر | حجر | Rabigh | 5,579 | grid | unverified | n | y | 86.0 | 128 | 162.5 (Madinah, T1) | y |  |
| King Abdullah Economic City | مدينة الملك عبد الله الاقتصادية | Rabigh | 5,126 | official | verified | n | y | 11.6 | 21 | 95.2 (Jeddah, T1) | y |  |
| Ranyah | رنية | Ranyah | 28,681 | official | verified | y | y | 317.6 | 318 | 252.3 (Taif, T2) | y |  |
| Turubah | تربة | Turubah | 28,279 | official | verified | y | y | 187.7 | 178 | 121.6 (Taif, T2) | y |  |
| Turabah | تربة | Turubah |  |  |  | n | n | 192.4 | 177 | 126.3 (Taif, T2) | n | duplicate of KSA-ST-07369 (Turubah, relation 12429522): same town |

## 3. Unmatched primary TA1 cities (name candidates are in the notes)

All 69 primary TA1 cities (≥ 5,000) that matched no settlement, across all 13 regions
(the export has no region column). They cannot be placed in Makkah without a region
(`runs/gastat/primary/city_matches.csv`); they are listed so that none is dropped
silently. Makkah membership is open (section 6).

| city (export) | total 2022 | reason |
|---|---:|---|
| Jubail Industrial City | 172,233 | crosswalk: no settlement (see screening/gastat_crosswalk.yaml) |
| Yanbaa As-Senayah | 73,139 | crosswalk: no settlement (see screening/gastat_crosswalk.yaml) |
| Arqa | 42,179 | ambiguous name: 0 exact / 11 spelling-variant candidates and no region in the export to choose between them |
| Altaraf | 29,588 | ambiguous name: 0 exact / 10 spelling-variant candidates and no region in the export to choose between them |
| Wadi Al Oqool farms | 24,381 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Aleumran | 22,781 | ambiguous name: 0 exact / 5 spelling-variant candidates and no region in the export to choose between them |
| Alqawz | 22,374 | universe (name): KSA-ST-06114 fails the plausibility guard (A-screen-038) |
| Alkalabiuh | 21,992 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Almunayzilh | 21,346 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Aljurn | 20,329 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Alulya | 20,250 | universe (name): KSA-ST-00680 fails the plausibility guard (A-screen-038) |
| Thebea | 17,502 | ambiguous name: 0 exact / 5 spelling-variant candidates and no region in the export to choose between them |
| Albitaliuh | 15,146 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Alhasma | 13,028 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Iiskan Alkalabiuh | 12,817 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alhaliluh | 12,337 | ambiguous name: 0 exact / 8 spelling-variant candidates and no region in the export to choose between them |
| Alshazalah | 11,560 | crosswalk: no settlement (see screening/gastat_crosswalk.yaml) |
| Aljushuh | 11,482 | ambiguous name: 0 exact / 6 spelling-variant candidates and no region in the export to choose between them |
| Benban | 10,793 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Aljabil | 9,994 | crosswalk: no settlement (see screening/gastat_crosswalk.yaml) |
| Alramiluh | 9,741 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Altwaythir | 9,700 | ambiguous name: 0 exact / 7 spelling-variant candidates and no region in the export to choose between them |
| Eshyrh | 9,517 | ambiguous name: 0 exact / 33 spelling-variant candidates and no region in the export to choose between them |
| Alealiuh Walkhudira' | 9,147 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Adham | 9,022 | crosswalk: no settlement (see screening/gastat_crosswalk.yaml) |
| Alqaruh | 8,656 | ambiguous name: 0 exact / 28 spelling-variant candidates and no region in the export to choose between them |
| Khabat Alkharish Wamuzaraea | 8,629 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Albadie Walqarfi | 8,623 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Ramadah | 8,607 | universe (name): KSA-ST-05700 fails the plausibility guard (A-screen-038) |
| Centers | 8,392 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Al Amajya | 8,156 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Al Tafih Farms | 7,716 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Almansuruh | 7,622 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Aleasiluh | 7,552 | ambiguous name: 0 exact / 23 spelling-variant candidates and no region in the export to choose between them |
| Prince Sultan Base | 7,530 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| An Naifiyah | 7,456 | ambiguous name: 0 exact / 3 spelling-variant candidates and no region in the export to choose between them |
| Alqarin | 7,339 | ambiguous name: 0 exact / 12 spelling-variant candidates and no region in the export to choose between them |
| King Abdul Aziz Military Academy | 7,154 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Al-Wadyin Station | 6,869 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Ghuran | 6,803 | ambiguous name: 0 exact / 4 spelling-variant candidates and no region in the export to choose between them |
| Alhutuh | 6,786 | ambiguous name: 0 exact / 10 spelling-variant candidates and no region in the export to choose between them |
| Aljafr | 6,772 | ambiguous name: 0 exact / 5 spelling-variant candidates and no region in the export to choose between them |
| Ghata | 6,653 | settlement KSA-ST-01141 also claimed by: Alghat, Ghata |
| Desalination Plant | 6,632 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Marikh | 6,349 | ambiguous name: 0 exact / 4 spelling-variant candidates and no region in the export to choose between them |
| Alshaqiraa | 6,069 | ambiguous name: 0 exact / 8 spelling-variant candidates and no region in the export to choose between them |
| Alsayl | 6,064 | ambiguous name: 0 exact / 23 spelling-variant candidates and no region in the export to choose between them |
| Al Rihan | 6,048 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Harad (Nadek) project and the adjacent areas | 5,951 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alkhadra' | 5,861 | ambiguous name: 5 exact / 17 spelling-variant candidates and no region in the export to choose between them |
| Aleuruq Alshamalia | 5,783 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Muhalih | 5,773 | 2010 bridge (skeleton): KSA-ST-00558 fails the plausibility guard (A-screen-038) |
| Shuab Makkah village | 5,673 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Qasirabin Eaqil | 5,617 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Umm Alawqb | 5,615 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Al Junfour | 5,589 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alramiduh | 5,581 | ambiguous name: 0 exact / 3 spelling-variant candidates and no region in the export to choose between them |
| Alshawajiruh | 5,537 | 2010 bridge (skeleton): KSA-ST-00644 fails the plausibility guard (A-screen-038) |
| Alshaquh Aleulya | 5,449 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Aleurafa' | 5,432 | ambiguous name: 0 exact / 15 spelling-variant candidates and no region in the export to choose between them |
| Alfudul | 5,374 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Aghnam farm and surrounding farms | 5,211 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Malkan | 5,196 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Al Shoudayda | 5,156 | ambiguous name: 0 exact / 24 spelling-variant candidates and no region in the export to choose between them |
| Alghawibuh | 5,139 | ambiguous name: 0 exact / 3 spelling-variant candidates and no region in the export to choose between them |
| Alhalalih | 5,120 | ambiguous name: 0 exact / 8 spelling-variant candidates and no region in the export to choose between them |
| San'abrah | 5,094 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alshaqiq | 5,092 | ambiguous name: 0 exact / 17 spelling-variant candidates and no region in the export to choose between them |
| Alsafuh | 5,050 | 2010 bridge (skeleton): KSA-ST-05170 fails the plausibility guard (A-screen-038) |

## 4. Economic roles (sourced; town-level ties only)

- Al Lith: hajj_umrah (S-r1a-225)
- At Ta'if: airport (S-cp1-100), industrial_city (S-r1a-204), tourism (S-r1a-241), university (S-r1a-221)
- As Sayl al Kabir: hajj_umrah (S-r1a-225)
- Jeddah: airport (S-cp1-100), port (S-cp1-111), industrial_city (S-r1a-204), heritage (S-r1a-205), hajj_umrah (S-cp1-110), university (S-r1a-221), tourism (S-r1a-239)
- Thuwal: university (S-makkah-003)
- Mecca: hajj_umrah (S-cp1-109), hajj_umrah (S-r1a-214), industrial_city (S-r1a-204), university (S-r1a-221)
- Rabigh: energy (S-cp1-104), hajj_umrah (S-r1a-225)

Not placed (no town-level tie or unlocated): Rabigh port (King Abdullah Port, governorate-level tie only, S-cp1-104); the Al-Qunfudhah port (negative result S-makkah-007); the Ad Duwayhi mine (region not assigned, unlocated); the giga-project role for KAEC (no PIF source tying Rabigh, S-cp1-104); the Modon Taif and Jeddah Oasis sites (no position).

## 5. Sources

Ids are in `docs/sources/r2-makkah.csv` and `docs/sources/index.csv`. Key: S-cp2-gastat-007 (governorate table), S-cp2-gastat-008 (city ≥ 5,000 table), S-makkah-001 (citypopulation.de relay), S-makkah-002 (OSM), S-makkah-008 (Nominatim boundary), S-makkah-009 (OSM population tags), S-r1a-505 (WorldPop 2020 100 m constrained), S-r1a-809 (OSRM).

## 6. Needs judgement (not resolved by guessing)

1. Adham (أضم): the 9,022 figure is attributed by the Census 2010 bridge, not a name match (A-makkah-003). Confirm against the primary table row.
2. Al-Ardiyat seat: the centre is the boundary centroid; the seat town is not located (A-makkah-004).
3. Grid rows within 25 km of Makkah city (for example Ash Sharai, Juranah, Shara'i al-Mujahidin) may sit inside the official Makkah city figure (A-makkah-007). Possible double count, not resolved.
4. Unmatched primary cities (section 3): region and Makkah membership unknown. Name candidates are noted on the rows (Al Quoz: Alqawz 22,374; Ushayrah: Eshyrh 9,517; Ghran: Ghuran 6,803; Assel: Alsayl 6,064; Al 'Arfa': Aleurafa' 5,432). Malkan 5,196, Al Shoudayda 5,156 and Alshaqiraa 6,069 have no candidate row. Not changed without identity.
5. Thuwal's governorate is Jiddah (S-makkah-004, snippet); Al-Hawiyah is in At-Ta'if (OSM). Both from snippets, not fetched pages.
6. KAEC giga-project role and the Rabigh port role: governorate-level ties only (S-cp1-104); not placed.
7. Missan/Maysan, Governorate of Jeddah naming: universe spellings mapped to S-073 names (A-makkah-006).
8. Universe defect: `settlements.parquet` carries Adham's 9,022 on the Al-Mahd village node (KSA-ST-03308); the register drops that node, but the universe still needs fixing (coordinator).
9. Terrain class for every row: not assessed.

Screening input, not a forecast.
