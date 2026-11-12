> **Document version:** docs/regions/jazan.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_JAZAN, track r2-jazan) | Status: draft

# Region register: Jazan (جازان), slug `jazan` (R2)

Screening input, not a forecast. Built by `screening/sweeps/jazan/build_register.py` (register) and `screening/sweeps/jazan/geo_estimates.py` (GEO_VERIFY estimates, record only). Outputs: `cities/ksa/regions/jazan.parquet` and `.csv`. Validated with `screening.region_sweep validate --strict`.

## Governorate count

| item | value | source |
|---|---|---|
| governorates_gastat | 17 (derived: all 17 working-list names are in GASTAT's primary governorate export (S-cp2-gastat-007); their totals sum to the Jazan region total 1,404,997 (S-cp2-gastat-001); A-jazan-003) | S-cp2-gastat-007; S-cp2-gastat-001 |
| governorates_listed | 17 (citypopulation.de, Census 2022 list) | S-jazan-001 |
| Saudipedia count (emirate text) | 16 (conflict, not resolved) | S-jazan-003 |
| GASTAT's own list | not read: portal.saudicensus.sa unreachable (S-jazan-015) | S-jazan-015 |

## Counts

- Rows: 50 (17 governorate centres, 33 other places at or above 5,000 on the figure used).
- Rows at or above 10,000 (`tag_10k`): 12. Rows at or above 5,000 (`tag_5k`): 46.
- Population types: official 26 (GASTAT primary city export 25; relayed 1); derived 2 (OSM contributor tag, secondary); grid 20 (WorldPop 2020 gap-fill, unverified); no figure 2.
- R1a universe: 1237 places in region; 13 at or above 10,000 on R1a's figure. Not listed row by row: places below 5,000 on their figure (the register keeps every place at or above 5,000 and all 17 centres).
- Economic roles: 25 role entries on 17 rows (each with an S- source; administrative on the 17 centres, the rest on Jizan, Farasan and Samtah).

## Gates and checks

- Governorate totals sum to the region total: 1,404,997 = 1,404,997.
- Every official value appears in GASTAT's primary city >= 5,000 export (asserted in the builder).
- Existing and committed distances agree with haversine to within 0.5 km (asserted; `dist_method: haversine`).
- Grid-only populations: none corroborated (no second method run; A-screen-031..033). Al Jawah (21,104, grid) is the only grid row at or above 10,000; it is `tag_10k: false`.
- Conflict logged: Alkhadra' (GASTAT 5,861 vs R1a WorldPop 7,055, +20.4 % grid over official). Official figure used (A-screen-038).
- GEO_VERIFY (record only): 25 unsourced or relayed rows estimated; the back-test gate fails (median APE grid 0.667, buildings 0.595; `runs/geo_verify/backtest/summary.json`). Estimates are in `notes`, never in `population`.

## Register

| name | governorate | centre | population | type / status | 5k | 10k | km existing | road min existing | km committed | nearest metro (tier) | terrain | economic roles | exclusion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jizan / جيزان | Jazan | yes | 173,919 | official / verified | Y | Y | 581 | 484 | 605 | Jazan (tier 3) | coastal | administrative, airport, port, industrial_city, university, energy |  |
| Farasan / فرسان | Farasan | yes | 10,118 | official / verified | Y | Y | 579 | 1052 | 603 | Jazan (tier 3) | coastal | administrative, tourism, heritage |  |
| Ad Darb / الدرب | Ad Darb | yes | 5,216 | official / verified | Y |  | 484 | 403 | 508 | Abha (tier 2) | coastal | administrative |  |
| Abu as Sala / أبو السلع | Sabya |  | 6,316 | official / verified | Y |  | 551 | 463 | 575 | Jazan (tier 3) | coastal |  |  |
| Al Madayah / المضايا | Ahad al Masarihah |  | 7,330 | official / verified | Y |  | 602 | 496 | 626 | Jazan (tier 3) | coastal |  |  |
| ALMata'an / المطعن | Baysh |  | 7,116 | official / verified | Y |  | 530 | 440 | 554 | Jazan (tier 3) | coastal |  |  |
| Al Kharadilah / الخرادلة | Jazan |  | 5,318 | official / verified | Y |  | 581 | 478 | 605 | Jazan (tier 3) | coastal |  |  |
| Al Usaylah / العسيلة | Abu Arish |  | 7,816 | grid / unverified | Y |  | 589 | 486 | 613 | Jazan (tier 3) | coastal |  |  |
| Misliyah / مسلية | Baysh |  | 5,559 | official / verified | Y |  | 527 | 441 | 551 | Jazan (tier 3) | coastal |  |  |
| Ar Rayth / الريث | Ar Rayth | yes | 2,321 | grid / unverified |  |  | 532 | 493 | 549 | Abha (tier 2) | mixed | administrative |  |
| Qanburah / قنبورة | Abu Arish |  | 5,410 | grid / unverified | Y |  | 589 | 492 | 613 | Jazan (tier 3) | mixed |  |  |
| Hakimah / حاكمة ابوعريش | Abu Arish |  | 6,991 | official / verified | Y |  | 585 | 486 | 609 | Jazan (tier 3) | mixed |  |  |
| Al Zabyah / الظبية | Sabya |  | 11,287 | official / verified | Y | Y | 566 | 469 | 590 | Jazan (tier 3) | coastal |  |  |
| Damad / ضمد | Damad | yes | 26,079 | official / verified | Y | Y | 573 | 482 | 597 | Jazan (tier 3) | mixed | administrative |  |
| Khudayrah / خضيرة | Damad |  | 5,235 | grid / unverified | Y |  | 574 | 476 | 598 | Jazan (tier 3) | mixed |  |  |
| Al Husayni / الحسيني | Sabya |  | 6,490 | official / verified | Y |  | 563 | 468 | 587 | Jazan (tier 3) | coastal |  |  |
| Sabya / صبيا | Sabya | yes | 72,086 | official / verified | Y | Y | 560 | 468 | 584 | Jazan (tier 3) | coastal | administrative |  |
| Al `Aridah / العارضة | Al Aridah | yes | 10,902 | official / verified | Y | Y | 597 | 508 | 616 | Jazan (tier 3) | mixed | administrative |  |
| Shuqayri / الشقيري | Damad |  | 7,238 | derived / secondary | Y |  | 573 | 488 | 597 | Jazan (tier 3) | mixed |  |  |
| Salhabah / صلهبة | Sabya |  | 9,421 | grid / unverified | Y |  | 560 | 462 | 584 | Jazan (tier 3) | coastal |  |  |
| Al `Aydabi / العيدابي | Al Aydabi | yes | 10,357 | official / verified | Y | Y | 571 | 489 | 591 | Jazan (tier 3) | mixed | administrative |  |
| Faifa / فيفا | Fayfa | yes |  |  |  |  | 578 | 514 | 592 | Jazan (tier 3) | escarpment_mountain | administrative |  |
| Al Laqyah / اللقية | Samtah |  | 5,096 | derived / secondary | Y |  | 630 | 516 | 654 | Jazan (tier 3) | mixed |  |  |
| Samitah / صامطة | Samtah | yes | 43,301 | official / verified | Y | Y | 630 | 515 | 654 | Jazan (tier 3) | mixed | administrative, agriculture |  |
| Ar Rukubah / الركوبة | Samtah |  | 6,191 | official / verified | Y |  | 629 | 513 | 653 | Jazan (tier 3) | mixed |  |  |
| Al Hadrur / الحضرور | Samtah |  | 6,199 | grid / unverified | Y |  | 631 | 520 | 655 | Jazan (tier 3) | mixed |  |  |
| Al Jaradiyah / الجرادية | Samtah |  | 7,092 | official / verified | Y |  | 630 | 515 | 654 | Jazan (tier 3) | mixed |  |  |
| Al Tuwal / الطوال | At Tuwal | yes | 4,671 | official / secondary |  |  | 638 | 527 | 662 | Jazan (tier 3) | mixed | administrative |  |
| Harub / هروب | Harub | yes | 9,394 | grid / unverified | Y |  | 549 | 497 | 568 | Jazan (tier 3) | mixed | administrative |  |
| Alddayer / الدائر | Ad Dair | yes | 15,752 | official / verified | Y | Y | 573 | 514 | 585 | Jazan (tier 3) | mixed | administrative |  |
| Al Jawah / الجوة | Fayfa |  | 21,104 | grid / unverified | Y |  | 579 | 525 | 591 | Jazan (tier 3) | mixed |  | grid-only population, uncorroborated |
| `Ayban / عيبان | Al Aydabi |  | 7,037 | grid / unverified | Y |  | 573 | 503 | 589 | Jazan (tier 3) | mixed |  |  |
| Baysh / بيش | Baysh | yes | 32,679 | official / verified | Y | Y | 534 | 444 | 558 | Jazan (tier 3) | coastal | administrative |  |
| Muqza` / مقزع | Ar Rayth |  | 6,883 | grid / unverified | Y |  | 534 | 483 | 555 | Jazan (tier 3) | mixed |  |  |
| Abu Alsadad / أبوالسداد | Ad Darb |  | 9,940 | official / verified | Y |  | 484 | 403 | 508 | Abha (tier 2) | coastal |  |  |
| Ahad al Musarihah / أحد المسارحة | Ahad al Masarihah | yes | 25,670 | official / verified | Y | Y | 620 | 503 | 644 | Jazan (tier 3) | mixed | administrative |  |
| Abu Arish / أبو عريش | Abu Arish | yes | 69,632 | official / verified | Y | Y | 589 | 487 | 614 | Jazan (tier 3) | mixed | administrative |  |
| alturashia / الطرشية | At Tuwal |  | 5,112 | grid / unverified | Y |  | 633 | 525 | 657 | Jazan (tier 3) | mixed |  |  |
| Qawz Al-Jaafra / قوز الجعافره | Sabya |  | 6,182 | grid / unverified | Y |  | 551 | 456 | 576 | Jazan (tier 3) | coastal |  |  |
| Al Kadarah / الكدرة | Ad Darb |  | 9,654 | grid / unverified | Y |  | 485 | 413 | 508 | Abha (tier 2) | coastal |  |  |
| Mizhirah / مزهرة | Ahad al Masarihah |  | 6,397 | official / verified | Y |  | 597 | 487 | 621 | Jazan (tier 3) | coastal |  |  |
| Alaliya / العالية | Sabya |  | 5,802 | grid / unverified | Y |  | 544 | 461 | 568 | Jazan (tier 3) | coastal |  |  |
| Alkhadra / الخضراء | Sabya |  | 5,861 | official / verified | Y |  | 543 | 461 | 567 | Jazan (tier 3) | coastal |  |  |
| الرخة / الرخة | Al Aridah |  | 7,392 | grid / unverified | Y |  | 595 | 502 | 616 | Jazan (tier 3) | mixed |  |  |
| unnamed WorldPop cluster 11047734768 /  | Al Aridah |  | 5,187 | grid / unverified | Y |  | 595 | 502 | 617 | Jazan (tier 3) | mixed |  |  |
| السودي / السودي | Samtah |  | 5,187 | grid / unverified | Y |  | 628 | 518 | 652 | Jazan (tier 3) | mixed |  |  |
| قائم العرب / قائم العرب | Al Aydabi |  | 5,404 | grid / unverified | Y |  | 570 | 488 | 592 | Jazan (tier 3) | mixed |  |  |
| جريبة / جريبة | Sabya |  | 6,220 | grid / unverified | Y |  | 560 | 462 | 584 | Jazan (tier 3) | coastal |  |  |
| Harajah / الحرجه | Damad |  | 6,541 | grid / unverified | Y |  | 575 | 486 | 599 | Jazan (tier 3) | mixed |  |  |
| Al Harth / الحرث | Al Harth | yes |  |  |  |  | 625 |  |  |  | mixed | administrative |  |

## Exclusions

- No row is screened out. One row is kept with `tag_10k: false` for an uncorroborated grid figure: Al Jawah (`grid-only population, uncorroborated`).
- Al Harth centre: no OSM place node in R1a; placeholder point (S-jazan-006); population null.
- Fayfa centre: R1a grid is 0 (no cells); population null.

## Sources

Population: S-cp2-gastat-008 (GASTAT primary city >= 5,000), S-cp2-gastat-007 and S-cp2-gastat-001 (governorate totals), S-jazan-002 (citypopulation.de, relayed; Al Tuwal only), S-r1a-210 (OSM population tag), S-r1a-505 (WorldPop 2020). Places and nodes: S-jazan-005 (OSM place nodes), S-jazan-006 (Al Harth placeholder), S-jazan-001 (governorate list). Distances: S-jazan-008 (Haramain station Makkah), S-054 and S-062 (Landbridge, committed layer, announced), S-r1a-809 (OSRM skims). Economic roles: S-r1a-200/204/208/210/221/222/244, S-cp1-100, S-jazan-009/010/011/012/016. Terrain: S-jazan-013 with A-jazan-002. Full rows: `docs/sources/r2-jazan.csv` and `docs/sources/index.csv`.

## Needs judgement (not resolved by guessing)

1. Governorate count: 17 (derived from GASTAT's primary export) vs 16 (Saudipedia). GASTAT's own list was not read (S-jazan-015).
2. Al Harth centre: placeholder coordinates from a Nominatim bbox centre; no OSM place node; population null.
3. Jizan port and JCPDI location: two sources give 60 km north and 60 km south-east of Jizan (S-jazan-009). The RCJY node is used as R1a has it.
4. Terrain classes are rule-based (A-jazan-002), not from Copernicus DEM. DEM classes are needed before use.
5. Al Jawah (21,104, WorldPop only; village tag): is it a town? GASTAT does not tabulate it. Needs a second method or an official locality figure before any 10k use.
6. Samtah agriculture role: from a Saudipedia market description in a search snippet (S-jazan-012); the page is not read.
7. Jazan refinery (energy role on Jizan): operating at 400,000 bpd per MEES and Saudipedia (S-jazan-016, snippets); the town tie is to be confirmed on the page.
8. Al Tuwal: no sourced border_crossing role; not assigned. Its population is citypopulation.de's relayed figure (secondary; GASTAT locality table not reachable).
9. Farasan road times (OSRM car, no ferry) are not meaningful for an island town.
10. Abu as Sadad (9,940) is larger than its governorate centre Ad Darb (5,216): a schema edge, kept.
11. GEO_VERIFY estimates are record only: the back-test gate fails, and the estimator covers only the rows listed in the notes (25 of 50).

Label: screening input, not a forecast.
