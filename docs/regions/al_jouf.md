> **Document version:** docs/regions/al_jouf.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_AL_JOUF) | Status: draft

# Region register: Al-Jouf (الجوف), slug `al_jouf` (REGION_AL_JOUF, R2)

**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

Full region sweep (R2) built from the R1a settlement universe with the GASTAT primary Census 2022 exports applied (CP2 P1a addendum 2). Access date for every source: **31 Oct 2026** (Asia/Riyadh). Files: `cities/ksa/regions/al_jouf.parquet` and `.csv` (same rows, same order; validated with `screening.region_sweep validate --strict`); sources `docs/sources/r2-al_jouf.csv`; assumptions `docs/assumptions.md` (merged at R2); build `screening/sweeps/al_jouf/build.py`; this table from `screening/sweeps/al_jouf/report.py`.

## Header: governorate count

- `governorates_gastat`: **4** (GASTAT Census 2022 TA1 primary governorate export, S-cp2-gastat-007: Sakaka 236,669; Al Qurayyat 195,016; Tubarjal 109,796; Dawamat Al Jandal 54,341 (governorate totals, not used for town rows). Region membership of the four names comes from citypopulation.de (S-al_jouf-002, secondary); GASTAT's own region-membership table was not reachable.)
- `governorates_listed`: **4**, the distinct governorates in the rows: Al Qurayyat, Dawamat Al Jandal, Sakaka, Tubarjal.
- Conflict, not resolved: Wikipedia and Saudipedia's Emirate page say **3** governorates (S-al_jouf-003, S-al_jouf-004, secondary, search summaries). The count of 4 matches the census list and the Tabarjal page; see Needs judgement.

## Counts

- Rows: **83** (every R1a settlement of the region, one row each; no OSM id duplicated).
- Governorate centres (each has a row): **4**.
- Towns at or above 10,000 (`tag_10k`): **5**, all GASTAT primary (official, verified). Grid-only rows at or above 10,000 that fail the corroboration gate: **3**, `tag_10k` false.
- Towns at or above 5,000 (`tag_5k`, sensitivity): **21** (official 9, grid 12). **Ghata (GASTAT 2022: 6,653) is missing; see Gaps.**
- Population basis: official (GASTAT primary, verified) 9 rows; grid (WorldPop 2020, unverified) 74 rows.
- Screened: 21 rows; excluded below 5,000 with no sourced economic role: 62 rows.

## Gaps (must close before R2 is done)

- **Ghata** (Al-Qurayyat governorate; GASTAT Census 2022 primary city table: **6,653**, S-cp2-gastat-008; membership S-al_jouf-002). It has no row because no coordinate source was found: the R1a name match gave the name to Al Ghat (Riyadh, KSA-ST-01141), the local OSM extract has no object named Ghata in Latin or الغطا spellings (S-al_jouf-011). Candidate, not confirmed: OSM village غطي / Ghutti, node 1236744649 (31.266538 N, 37.527451 E), in the box and in Al-Qurayyat; citypopulation.de writes Ghata as غطى. Nominatim (8 queries: 2 unbounded, 6 bounded to the Al-Jouf box), Wikidata and the 2010 list return nothing (S-al_jouf-010). A row needs a located source (GASTAT locality table or a located OSM/GeoNames entry). Until then the ≥ 5,000 count is one short.
- Terrain class: not assessed (no DEM read; disk gate; A-al_jouf-002). Column null on every row.
- Hajj/Umrah, border crossing (Tubarjal) and other roles: no source in the repository; not recorded.
- Geo-verify `estimate`: not run (it downloads building footprints and Sentinel-2 windows, outside the R2 disk gate). The pilot's record-only GEO_VERIFY notes are carried in the notes for the rows they cover.

## Population rule applied

1. GASTAT primary city table (S-cp2-gastat-008, 271 cities of 5,000+): official, verified, year 2022. The DataPulse relayed figures are identical for these rows (cross-check only).
2. OSM `place` population tags are not 2022 figures (A-al_jouf-004). The two dated 2010 equal the Census 2010 list (S-cp2-gastat-005); three undated tags are not used either.
3. Otherwise WorldPop 2020 (100 m, constrained; S-r1a-505): `pop_type: grid`, `pop_source_status: unverified`, `tag_10k` false (no second method run: `pop_corroboration` null; A-screen-031/032). A grid row at or above 5,000 is shown for the sensitivity and noted as presumed below 5,000 in 2022 (A-al_jouf-003). The grid is not a GASTAT value and is never corrected in `population`.

## Distances and roads

- Existing and metro straight-line distances (`dist_*_km`) are from the R1a universe: `dist_existing_km` is haversine to the nearest existing station on the SAR North passenger line (checked for Sakaka: 51.03 km to `sar-north-passenger:al-jawf`); `dist_metro_km` is haversine to the nearest metro city (tier from A-screen-013; Tabuk tier 2, Buraidah tier 2).
- Road minutes (`road_min_*`) are the R1a OSRM table, MLD car profile, free flow, uncalibrated (S-r1a-809).
- Committed distances: nearest committed station is the Landbridge stop `dawadmi` (planned, committed layer per `cities/ksa/lines/landbridge.yaml`) or the GCC railway's Kuwait border proxy, both with unlocated sites in R1a; the distances are to the alignment as R1a computed them. No committed line is called existing.

## Exclusions

- Below 5,000 with no sourced economic role: 62 rows, `screened: false`, reason given per row.
- Grid-only at or above 10,000, uncorroborated (`tag_10k` false, `screened` true): 3 rows (At Tuwayr, Al Hadithah, Al 'Isawiyah).
- No row was excluded as a duplicate or outside the region polygon.

## Sources (ids in `docs/sources/r2-al_jouf.csv` or `docs/sources/index.csv`)

- Population: S-cp2-gastat-008 (GASTAT Census 2022 TA1 primary, cities of 5,000+), S-cp2-gastat-007 (governorates), S-cp2-gastat-005 (Census 2010 cities), S-r1a-505 (WorldPop 2020 100 m constrained), S-cp2-gastat-001 (DataPulse, cross-check only).
- Coordinates and OSM ids: S-r1a-210 (OSM GCC extract, element ids), S-al_jouf-006 (pilot Overpass place nodes), S-al_jouf-011 (filtered copy used for the checks).
- Lines and roads: S-018 (SAR North places), S-r1a-809 (OSRM skims).
- Economic roles: S-cp1-100 and S-r1a-210 (airports, GACA report Feb 2025), S-r1a-221, S-r1a-222 (university), S-r1a-204 (MODON industrial city), S-al_jouf-008 (Sakaka capital), S-al_jouf-002 (governorate membership), S-al_jouf-009 (Dumat heritage and tourism, Arab News 2022, secondary).
- Counts and conflicts: S-al_jouf-003, S-al_jouf-004 (governorate count, secondary); S-al_jouf-005 (GASTAT portal, unverified).

## Needs judgement (not resolved by guessing)

1. Governorate count 3 or 4 (conflict above). The register uses 4, which the GASTAT primary names support.
2. Ghata: find a located source (GASTAT locality table or a located OSM/GeoNames entry), then add the row.
3. Al-Hadithah (OSM node 1236744849, grid 11,301): census name Al-Ḥadīthah al-Qadīmah per S-al_jouf-002 (not in the 5,000+ table, so presumed below 5,000). Also the SAR North terminus 'Al Haditha' (S-018). Which place is the terminus, and is the grid row a double count?
4. Al 'Isawiyah (grid 15,474 against an OSM 2010 tag of 5,629, grid ÷ 2010 = 2.7): presumed below 5,000 in 2022, grid unverified. Keep as a sensitivity row or set population to null?
5. Jouf station (`sar-north-passenger:al-jawf`, 29.648 N, 39.837 E): 17.8 km from Dawamat Al Jandal and 51 km from Sakaka, the nearest station for most rows. Confirm it is the region's main station.
6. Sakaka industrial city: the MODON Al-Jouf oasis is unlocated (S-r1a-204); its town link is the MODON table's nearest-town field (R1a). Keep the role or drop it?
7. Tubarjal border crossing and Al Qurayyat industry: searched, not sourced; not recorded.
8. Far (>100 km) stratum: the sample logic is out of scope for R2; no pilot sample flags are set.
9. Corroboration gate: the 2010-growth method (`gastat2010_city_growth`) applies only to matched towns; no Al-Jouf grid row is matched, so no grid row passes the 10,000 gate.

## Notes on the rows

- R1a's `control_total_flag` marks the region's grid sum above its residual (`runs/gastat/primary/control_total.csv`, al_jouf: grid 86,611 + tabulated unmatched 20,208 against a residual of 67,886). Reporting only; the flags are in the notes of the rows they cover.
- Terrain (`terrain_class`): null on every row (A-al_jouf-002).

Screening input, not a forecast. Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

## Table

Sorted by population (largest first; null last). `existing` and `metro` are km / road minutes (road minutes are free-flow OSRM).

| # | name (EN) | name (AR) | governorate | population | pop_type / status | tag_10k | tag_5k | screened | existing: km / road min | metro: km / road min | economic roles | exclusion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Sakaka | سكاكا | Sakaka | 204174 | official / verified | yes | yes | yes | 51.03 / 53.8 | 394.25 / 328.2 | administrative (S-al_jouf-008), airport (S-cp1-100;S-r1a-210), university (S-r1a-221;S-r1a-222;S-r1a-210), industrial_city (S-r1a-204) |  |
| 2 | Al Qurayyat | القريات | Al Qurayyat | 167080 | official / verified | yes | yes | yes | 10.93 / 16.4 | 334.48 / 439.0 | administrative (S-al_jouf-002), airport (S-cp1-100;S-r1a-210) |  |
| 3 | Tubarjal | طبرجل | Tubarjal | 78354 | official / verified | yes | yes | yes | 135.21 / 111.8 | 282.84 / 349.0 | administrative (S-al_jouf-002) |  |
| 4 | Dawmat al Jandal | دومة الجندل | Dawamat Al Jandal | 42362 | official / verified | yes | yes | yes | 17.75 / 29.6 | 356.58 / 291.9 | administrative (S-al_jouf-002), heritage (S-al_jouf-009), tourism (S-al_jouf-009) |  |
| 5 | Al `Isawiyah | العيساوية | Al Qurayyat | 15474 | grid / unverified | no | yes | yes | 102.32 / 84.3 | 291.44 / 371.0 |  | grid-only population, uncorroborated |
| 6 | Suwayr | صوير | Sakaka | 12430 | official / verified | yes | yes | yes | 74.47 / 77.5 | 416.93 / 352.0 |  |  |
| 7 | Al Hadithah | الحديثة | Al Qurayyat | 11301 | grid / unverified | no | yes | yes | 12.93 / 23.5 | 344.26 / 456.1 |  | grid-only population, uncorroborated |
| 8 | At Tuwayr | الطوير | Sakaka | 10083 | grid / unverified | no | yes | yes | 45.45 / 51.3 | 390.46 / 323.8 |  | grid-only population, uncorroborated |
| 9 | Hudayb | هديب | Sakaka | 8536 | grid / unverified | no | yes | yes | 71.39 / 80.6 | 415.15 / 355.1 |  |  |
| 10 | Qara | قارا | Sakaka | 7627 | grid / unverified | no | yes | yes | 45.39 / 48.2 | 391.47 / 320.8 |  |  |
| 11 | Meegowa | ميقوع | Tubarjal | 7020 | official / verified | no | yes | yes | 90.31 / 81.3 | 278.06 / 279.1 |  |  |
| 12 | Ar Radīfah | الرديفة | Dawamat Al Jandal | 6596 | grid / unverified | no | yes | yes | 22.6 / 39.4 | 341.07 / 283.4 |  |  |
| 13 | Al Faysaliyah | الفيصلية | Sakaka | 6488 | grid / unverified | no | yes | yes | 48.35 / 54.4 | 392.51 / 327.0 |  |  |
| 14 | An Nasifah | الناصفة | Al Qurayyat | 6193 | grid / unverified | no | yes | yes | 49.63 / 62.8 | 314.78 / 407.9 |  |  |
| 15 | Abu Ajram | أبو عجرم | Dawamat Al Jandal | 5610 | official / verified | no | yes | yes | 57.91 / 57.1 | 313.26 / 255.3 |  |  |
| 16 | Talat Ammar | طلعة عمار | Sakaka | 5562 | grid / unverified | no | yes | yes | 132.27 / 109.9 | 460.87 / 384.3 |  |  |
| 17 | Al Fiyad | الفياض | Tubarjal | 5532 | official / verified | no | yes | yes | 119.11 / 106.5 | 286.47 / 357.1 |  |  |
| 18 | أصفان | أصفان | Dawamat Al Jandal | 5430 | grid / unverified | no | yes | yes | 16.26 / 39.1 | 332.93 / 300.3 |  |  |
| 19 | An Nabk Abu Qasr | النبك أبو قصر | Tubarjal | 5374 | official / verified | no | yes | yes | 130.88 / 108.3 | 295.11 / 306.8 |  |  |
| 20 | الاضارع | الاضارع | Dawamat Al Jandal | 5200 | grid / unverified | no | yes | yes | 32.53 / 39.9 | 332.41 / 272.2 |  |  |
| 21 | قليب خضر | قليب خضر | Al Qurayyat | 5092 | grid / unverified | no | yes | yes | 85.34 / 72.8 | 298.23 / 383.7 |  |  |
| 22 | Al Laqayit | اللقايط | Sakaka | 4550 | grid / unverified | no | no | no | 54.4 / 60.8 | 397.98 / 334.7 |  | below 5,000 and no sourced economic role |
| 23 | الرفيعة | الرفيعة | Sakaka | 4318 | grid / unverified | no | no | no | 65.6 / 74.2 | 408.41 / 348.6 |  | below 5,000 and no sourced economic role |
| 24 | Mujamma` al Hadithah | مجمع الحديثة | Al Qurayyat | 3222 | grid / unverified | no | no | no | 19.55 / 28.4 | 349.9 / 461.0 |  | below 5,000 and no sourced economic role |
| 25 | Zallum | زلوم | Sakaka | 2680 | grid / unverified | no | no | no | 72.82 / 64.8 | 411.61 / 339.2 |  | below 5,000 and no sourced economic role |
| 26 | An Nazayim | النظايم | Sakaka | 2246 | grid / unverified | no | no | no | 71.72 / 68.5 | 412.05 / 342.9 |  | below 5,000 and no sourced economic role |
| 27 | Ghutti | غطي | Al Qurayyat | 2048 | grid / unverified | no | no | no | 28.38 / 34.2 | 331.79 / 443.3 |  | below 5,000 and no sourced economic role |
| 28 | Hadban | هدبان | Sakaka | 1775 | grid / unverified | no | no | no | 68.49 / 77.2 | 411.6 / 351.7 |  | below 5,000 and no sourced economic role |
| 29 | Al Laqayit | اللقايط | Sakaka | 1607 | grid / unverified | no | no | no | 57.23 / 65.5 | 400.8 / 339.5 |  | below 5,000 and no sourced economic role |
| 30 | النباج | النباج | Tubarjal | 1479 | grid / unverified | no | no | no | 152.9 / 119.3 | 286.8 / 344.0 |  | below 5,000 and no sourced economic role |
| 31 | Al Husayba` | الحصيباء | Dawamat Al Jandal | 1271 | grid / unverified | no | no | no | 15.43 / 29.4 | 355.22 / 293.5 |  | below 5,000 and no sourced economic role |
| 32 | Shaybani | شيباني | Al Qurayyat | 896 | grid / unverified | no | no | no | 19.57 / 25.2 | 333.5 / 437.7 |  | below 5,000 and no sourced economic role |
| 33 | Khaw`a' | خوعاء | Sakaka | 784 | grid / unverified | no | no | no | 60.97 / 74.3 | 407.52 / 346.9 |  | below 5,000 and no sourced economic role |
| 34 | Fiyad Mani` | فياض مانع | Sakaka | 724 | grid / unverified | no | no | no | 41.14 / 44.9 | 387.4 / 317.4 |  | below 5,000 and no sourced economic role |
| 35 | الشقيق | الشقيق المروت | Dawamat Al Jandal | 606 | grid / unverified | no | no | no | 39.48 / 47.1 | 341.68 / 325.8 |  | below 5,000 and no sourced economic role |
| 36 | Al Washwash | الوشوش | Al Qurayyat | 557 | grid / unverified | no | no | no | 32.05 / 26.8 | 347.27 / 466.8 |  | below 5,000 and no sourced economic role |
| 37 | الرافعية | الرافعية | Dawamat Al Jandal | 533 | grid / unverified | no | no | no | 23.55 / 30.9 | 339.61 / 279.3 |  | below 5,000 and no sourced economic role |
| 38 | Ithrah | إثرة | Al Qurayyat | 346 | grid / unverified | no | no | no | 31.99 / 27.0 | 347.15 / 467.0 |  | below 5,000 and no sourced economic role |
| 39 | Al Muzayrir | المزيرير | Sakaka | 317 | grid / unverified | no | no | no | 38.63 / 48.9 | 385.23 / 321.5 |  | below 5,000 and no sourced economic role |
| 40 | Ash Shuwayhitiyah | الشويحطية | Sakaka | 286 | grid / unverified | no | no | no | 81.3 / 82.7 | 410.78 / 357.2 |  | below 5,000 and no sourced economic role |
| 41 | Qur as Sumur | قور السمر | Sakaka | 214 | grid / unverified | no | no | no | 39.02 / 45.9 | 385.08 / 318.5 |  | below 5,000 and no sourced economic role |
| 42 | Al Qara | القرعاء | Sakaka | 187 | grid / unverified | no | no | no | 49.18 / 47.8 | 389.92 / 322.3 |  | below 5,000 and no sourced economic role |
| 43 | مركز الحماد | مركز الحماد | Al Qurayyat | 183 | grid / unverified | no | no | no | 66.09 / 71.6 | 362.94 / 511.5 |  | below 5,000 and no sourced economic role |
| 44 | Ar Ridifah | الرديفة | Al Qurayyat | 167 | grid / unverified | no | no | no | 62.02 / 52.5 | 307.06 / 398.2 |  | below 5,000 and no sourced economic role |
| 45 | Qa` al Gharis | قاع الغريس | Sakaka | 163 | grid / unverified | no | no | no | 54.08 / 63.4 | 399.13 / 335.9 |  | below 5,000 and no sourced economic role |
| 46 | عذفاء | عذفاء | Sakaka | 138 | grid / unverified | no | no | no | 161.65 / 183.5 | 409.19 / 456.0 |  | below 5,000 and no sourced economic role |
| 47 | Al Qunaytirah | القنيطرة | Sakaka | 125 | grid / unverified | no | no | no | 43.97 / 46.4 | 384.52 / 320.8 |  | below 5,000 and no sourced economic role |
| 48 | الحوي | الحوي | Tubarjal | 105 | grid / unverified | no | no | no | 166.5 / 150.4 | 182.18 / 153.0 |  | below 5,000 and no sourced economic role |
| 49 | Jimajim | جماجم | Al Qurayyat | 99 | grid / unverified | no | no | no | 59.1 / 50.5 | 308.89 / 433.5 |  | below 5,000 and no sourced economic role |
| 50 | الناصفة | الناصفة | Sakaka | 98 | grid / unverified | no | no | no | 73.89 / 69.1 | 414.02 / 343.5 |  | below 5,000 and no sourced economic role |
| 51 | Al Qal`ah | القلعة | Sakaka | 94 | grid / unverified | no | no | no | 57.77 / 60.9 | 399.55 / 335.3 |  | below 5,000 and no sourced economic role |
| 52 | Kaf | كاف | Al Qurayyat | 61 | grid / unverified | no | no | no | 20.29 / 28.1 | 344.82 / 468.0 |  | below 5,000 and no sourced economic role |
| 53 | Mazati al Kaysumah | مزارع الكيسومة | Sakaka | 52 | grid / unverified | no | no | no | 47.5 / 49.2 | 386.79 / 323.6 |  | below 5,000 and no sourced economic role |
| 54 | Al Bayda' | البيضاء | Sakaka | 47 | grid / unverified | no | no | no | 53.71 / 58.4 | 394.64 / 332.8 |  | below 5,000 and no sourced economic role |
| 55 | Umm Furs | أم فرس | Sakaka | 45 | grid / unverified | no | no | no | 42.22 / 50.5 | 383.76 / 324.9 |  | below 5,000 and no sourced economic role |
| 56 | المندسة | المندسة | Dawamat Al Jandal | 29 | grid / unverified | no | no | no | 29.65 / 54.2 | 352.93 / 304.2 |  | below 5,000 and no sourced economic role |
| 57 | Al Qarqar | القرقر | Al Qurayyat | 22 | grid / unverified | no | no | no | 28.63 / 27.7 | 343.59 / 463.9 |  | below 5,000 and no sourced economic role |
| 58 | Qiyal | قيال | Sakaka | 20 | grid / unverified | no | no | no | 53.4 / 59.2 | 389.95 / 333.6 |  | below 5,000 and no sourced economic role |
| 59 | Sidi` | صديع | Tubarjal | 19 | grid / unverified | no | no | no | 113.33 / 110.5 | 289.31 / 361.0 |  | below 5,000 and no sourced economic role |
| 60 | Ayn al Hawwasi | عين الحواسي | Al Qurayyat | 9 | grid / unverified | no | no | no | 30.03 / 23.6 | 345.11 / 463.5 |  | below 5,000 and no sourced economic role |
| 61 | Rawd al Mazari` | روض المزارع | Dawamat Al Jandal | 6 | grid / unverified | no | no | no | 27.78 / 46.8 | 357.73 / 300.4 |  | below 5,000 and no sourced economic role |
| 62 | Al Mughtabiyah | المغتبية | Dawamat Al Jandal | 5 | grid / unverified | no | no | no | 29.5 / 50.2 | 358.86 / 303.7 |  | below 5,000 and no sourced economic role |
| 63 | Al Badiyi` | البديّع | Al Qurayyat | 0 | grid / unverified | no | no | no | 65.12 / 71.5 | 309.74 / 417.1 |  | below 5,000 and no sourced economic role |
| 64 | Uwaysit | أويسط | Tubarjal | 0 | grid / unverified | no | no | no | 130.07 / 104.6 | 283.55 / 348.9 |  | below 5,000 and no sourced economic role |
| 65 | Subayhah | صبيحة | Tubarjal | 0 | grid / unverified | no | no | no | 105.19 / 84.0 | 286.41 / 282.5 |  | below 5,000 and no sourced economic role |
| 66 | رحيه | رحيه | Sakaka | 0 | grid / unverified | no | no | no | 101.49 / 105.0 | 448.22 / 377.6 |  | below 5,000 and no sourced economic role |
| 67 | الأرنبية | الأرنبية | Dawamat Al Jandal | 0 | grid / unverified | no | no | no | 134.81 / 226.1 | 397.19 / 512.8 |  | below 5,000 and no sourced economic role |
| 68 | أبو رواث | أبو رواث | Sakaka | 0 | grid / unverified | no | no | no | 133.64 / 156.1 | 467.75 / 428.7 |  | below 5,000 and no sourced economic role |
| 69 | Al Murir | المرير | Dawamat Al Jandal | 0 | grid / unverified | no | no | no | 30.06 / 51.4 | 359.34 / 304.9 |  | below 5,000 and no sourced economic role |
| 70 | Al `Uqaylah | العقيلة | Al Qurayyat | 0 | grid / unverified | no | no | no | 20.64 / 27.7 | 332.93 / 440.2 |  | below 5,000 and no sourced economic role |
| 71 | Ad Dab`iyah | الضبعيّة | Sakaka | 0 | grid / unverified | no | no | no | 50.28 / 53.9 | 388.45 / 328.3 |  | below 5,000 and no sourced economic role |
| 72 | Al Midarrah | المدرة | Sakaka | 0 | grid / unverified | no | no | no | 42.58 / 51.0 | 389.4 / 323.6 |  | below 5,000 and no sourced economic role |
| 73 | Minwa | منوى | Al Qurayyat | 0 | grid / unverified | no | no | no | 28.13 / 22.3 | 345.15 / 462.2 |  | below 5,000 and no sourced economic role |
| 74 | Al Qutb | القطب | Sakaka | 0 | grid / unverified | no | no | no | 54.92 / 54.0 | 393.38 / 328.4 |  | below 5,000 and no sourced economic role |
| 75 | Mughayra' | مغيراء | Sakaka | 0 | grid / unverified | no | no | no | 60.56 / 80.6 | 407.44 / 353.1 |  | below 5,000 and no sourced economic role |
| 76 | Ajrubah | أجربة | Dawamat Al Jandal | 0 | grid / unverified | no | no | no | 31.15 / 53.5 | 356.78 / 307.0 |  | below 5,000 and no sourced economic role |
| 77 | Al Murayr | المرير | Sakaka | 0 | grid / unverified | no | no | no | 45.37 / 71.6 | 373.09 / 346.1 |  | below 5,000 and no sourced economic role |
| 78 | طناب | طناب | Dawamat Al Jandal | 0 | grid / unverified | no | no | no | 82.1 / 62.8 | 373.63 / 341.6 |  | below 5,000 and no sourced economic role |
| 79 | هجرة عقلة هويدي | هجرة عقلة هويدي | Sakaka | 0 | grid / unverified | no | no | no | 170.0 / 212.8 | 515.88 / 487.3 |  | below 5,000 and no sourced economic role |
| 80 | Al Jarawi | الجراوي | Tubarjal | 0 | grid / unverified | no | no | no | 117.85 / 96.1 | 289.0 / 294.6 |  | below 5,000 and no sourced economic role |
| 81 | Muwaysin | مويسن | Dawamat Al Jandal | 0 | grid / unverified | no | no | no | 26.55 / 30.0 | 369.37 / 304.4 |  | below 5,000 and no sourced economic role |
| 82 | Shaghar | شغار | Tubarjal | 0 | grid / unverified | no | no | no | 109.84 / 86.6 | 288.45 / 285.2 |  | below 5,000 and no sourced economic role |
| 83 | هجرة مكيمن فهد الجلعود | هجرة مكيمن فهد الجلعود | Sakaka | 0 | grid / unverified | no | no | no | 169.32 / 190.8 | 400.48 / 463.3 |  | below 5,000 and no sourced economic role |
