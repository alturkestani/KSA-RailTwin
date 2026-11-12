> **Document version:** docs/regions/northern_borders.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_NORTHERN_BORDERS, R2) | Status: draft

# Northern Borders (الحدود الشمالية): region sweep (R2)

Slug `northern_borders` · Register `cities/ksa/regions/northern_borders.parquet` (CSV mirror alongside) · Label: **screening input, not a forecast**. Access date for every source: 31 Oct 2026 (Asia/Riyadh) unless stated. Population is the settlement figure, never a governorate total.

## Governorate count

- `governorates_gastat: 4`: GASTAT Census 2022 TA1 primary export, 150 governorates (S-cp2-gastat-007). Arar 202,719; Rafha 84,536; Turayf 66,004; Al Uwayqilah 20,318.
- `governorates_listed: 4`: each has a row for its centre (4 centre rows).
- Cross-check: the four governorate totals sum to 373,577, equal to the TA1 region total of 373,577 (`runs/gastat/primary/control_total.csv`). The relayed list (S-northern_borders-002, -003) also gives four. No discrepancy.

## Counts

| item | count | note |
|---|---|---|
| register rows | 57 | every settlement in the R1a universe for this region; 8 screened, 49 excluded with a reason (table below) |
| tag_10k = true | 4 | Arar, Rafha, Turayf, Al-Uwayqilah: primary GASTAT city figures (S-cp2-gastat-008) |
| grid-only ≥ 10,000, not tagged | 2 | Linah (17,616) and Badanah (10,670): no corroborating method run (A-screen-032) |
| tag_5k = true (sensitivity) | 7 | the four above, Rawdat Habbas (5,620, primary), and Linah and Badanah (grid; tag_5k is not gated) |
| screened = true | 8 | the 4 centres, the ≥5,000 places, and Hazm al Jalamid (sourced mining role) |
| excluded (screened = false) | 49 | exclusion reason per row |
| rows with ≥ 1 sourced economic role | 5 | airports, university, border post, industrial city, mining; governorate seats (administrative) |
| populations: official / secondary / grid | 7 / 2 / 27 | official = 5 primary GASTAT figures + 2 relayed (`secondary`); grid rows unverified |

Facts status: 5 rows verified (GASTAT primary, S-cp2-gastat-008); 2 secondary (citypopulation.de, S-northern_borders-001: At Timyat, Ash Shu'bah); 27 grid gap-fills unverified (S-r1a-506). Grid rows carry no corroboration in this sweep: no second method was run, and the 2010-growth check has no 2010 entry for Linah or Badanah.

## Register

Distances per R1a: `dist_existing_km` is great circle to the 15 intercity passenger stations (A-r1a-008) with OSRM car road minutes over the 5 nearest (A-r1a-027, S-r1a-809); committed distances use alignment vertices at 1 km (A-r1a-007). Metro: nearest metro in the A-screen-013 set. Terrain assumed (A-northern_borders-001).

| name (EN) | name (AR) | governorate | centre | population | pop_type | status | 10k | 5k | dist existing km (road min) | nearest metro (tier, km) | economic roles | terrain | screened | exclusion |
|---|---|---|---|---:|---|---|---|---|---:|---|---|---|---|---|
| Arar | عرعر | Arar | yes | 199,247 | official | verified | Y | Y | 186.5 (162) | Tabuk (T2, 517) | airport (S-cp1-100;S-r1a-210); industrial_city (S-r1a-204); university (S-r1a-221;S-r1a-222;S-r1a-210); border_crossing (S-r1a-210); administrative (S-northern_borders-003;S-northern_borders-002) | flat_desert | Y |  |
| Rafha | رفحاء | Rafha | yes | 63,929 | official | verified | Y | Y | 276.7 (337) | Buraidah (T2, 370) | airport (S-cp1-100;S-r1a-210); administrative (S-northern_borders-003;S-northern_borders-002) | dunes | Y |  |
| Turayf | طريف | Turayf | yes | 61,395 | official | verified | Y | Y | 133.0 (107) | Tabuk (T2, 416) | airport (S-cp1-100;S-r1a-210); administrative (S-northern_borders-003;S-northern_borders-002) | flat_desert | Y |  |
| Linah | لينة | Rafha |  | 17,616 | grid | unverified |  | Y | 228.3 (265) | Buraidah (T2, 271) | none sourced | dunes | Y | grid-only population, uncorroborated |
| Al-Uwayqilah | العويقيلة | Al Uwayqilah | yes | 17,055 | official | verified | Y | Y | 244.5 (247) | Buraidah (T2, 479) | administrative (S-northern_borders-003;S-northern_borders-002) | flat_desert | Y |  |
| Badanah | بدنة | Arar |  | 10,670 | grid | unverified |  | Y | 185.7 (164) | Tabuk (T2, 515) | none sourced | flat_desert | Y | grid-only population, uncorroborated |
| Rawdat Habbas | روضة هباس | Rafha |  | 5,620 | official | verified |  | Y | 296.3 (330) | Buraidah (T2, 315) | none sourced | dunes | Y |  |
| At Timyat | طلعة التمياط | Rafha |  | 3,770 | official | secondary |  |  | 276.8 (312) | Buraidah (T2, 400) | none sourced | dunes | N | below 5,000 (secondary figure); no sourced economic role |
| Ibn Suayyid | إبن سعيد | Arar |  | 3,712 | grid | unverified |  |  | 182.3 (178) | Tabuk (T2, 504) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| Ash Shu‘bah | شعبة نصاب | Rafha |  | 3,430 | official | secondary |  |  | 273.4 (298) | Buraidah (T2, 294) | none sourced | dunes | N | below 5,000 (secondary figure); no sourced economic role |
| Al Khushaybi | الخشيبي | Rafha |  | 2,387 | grid | unverified |  |  | 286.1 (352) | Buraidah (T2, 330) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| As Sulaymaniyah | السليمانية | Arar |  | 1,108 | grid | unverified |  |  | 161.4 (218) | Tabuk (T2, 504) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| unnamed OSM node 2848030337 |  | Arar |  | 843 | grid | unverified |  |  | 184.3 (168) | Tabuk (T2, 512) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| Ibn Shuraym | إبن شريم | Rafha |  | 813 | grid | unverified |  |  | 296.6 (349) | Buraidah (T2, 406) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| ebn thunayyan | ابن ثنيان | Al Uwayqilah |  | 805 | grid | unverified |  |  | 227.7 (234) | Buraidah (T2, 497) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| Al Markuz | المركوز | Al Uwayqilah |  | 804 | grid | unverified |  |  | 274.8 (274) | Buraidah (T2, 443) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| نعيجان | نعيجان | Al Uwayqilah |  | 667 | grid | unverified |  |  | 209.2 (266) | Buraidah (T2, 402) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| Daydeeb | الديدب | Arar |  | 617 | grid | unverified |  |  | 190.7 (180) | Tabuk (T2, 529) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| الجبهان | الجبهان | Rafha |  | 609 | grid | unverified |  |  | 278.8 (344) | Buraidah (T2, 362) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| Zibala | زبالا | Rafha |  | 352 | grid | unverified |  |  | 259.0 (326) | Buraidah (T2, 343) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| Hazm al Jalamid | حزم الجلاميد | Arar |  | 187 | grid | unverified |  |  | 183.3 (208) | Tabuk (T2, 468) | mining (S-r1a-211;S-r1a-210) | flat_desert | Y |  |
| اعيوج لينة | اعيوج لينة | Rafha |  | 119 | grid | unverified |  |  | 256.6 (301) | Buraidah (T2, 276) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| unnamed OSM node 348243528 |  | Rafha |  | 94 | grid | unverified |  |  | 275.4 (329) | Buraidah (T2, 377) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| Qaysumat Fayhan | قيصومة فيحان | Rafha |  | 81 | grid | unverified |  |  | 203.9 (277) | Buraidah (T2, 332) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| Ibn Bakr | هجرة ابن بكر | Arar |  | 54 | grid | unverified |  |  | 180.8 (190) | Tabuk (T2, 495) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| Nisab | نصاب | Rafha |  | 44 | grid | unverified |  |  | 306.4 (352) | Buraidah (T2, 326) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| الهبكة | الهبكة | Al Uwayqilah |  | 33 | grid | unverified |  |  | 238.1 (315) | Buraidah (T2, 422) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| Al Kasib | الكاسب | Al Uwayqilah |  | 28 | grid | unverified |  |  | 223.1 (225) | Buraidah (T2, 505) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| Lawqah | لوقة | Rafha |  | 17 | grid | unverified |  |  | 256.8 (341) | Buraidah (T2, 407) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| اليدية | اليدية | Rafha |  | 14 | grid | unverified |  |  | 182.4 (283) | Buraidah (T2, 371) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| مغطية | مغطية | Rafha |  | 13 | grid | unverified |  |  | 222.8 (252) | Buraidah (T2, 243) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| Al Musandaq | المصندق | Rafha |  | 9 | grid | unverified |  |  | 272.4 (375) | Buraidah (T2, 331) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| السلمانية | السلمانية | Al Uwayqilah |  | 9 | grid | unverified |  |  | 212.9 (278) | Buraidah (T2, 393) | none sourced | flat_desert | N | below 5,000 (grid estimate only); no sourced economic role |
| unnamed OSM node 11204976241 |  | Rafha |  | 6 | grid | unverified |  |  | 244.7 (258) | Buraidah (T2, 264) | none sourced | dunes | N | below 5,000 (grid estimate only); no sourced economic role |
| Abu Sawr | ابو صور | Rafha |  |  |  |  |  |  | 284.3 (325) | Buraidah (T2, 304) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| Ad Duwayd | الدويد | Al Uwayqilah |  |  |  |  |  |  | 246.1 (263) | Buraidah (T2, 463) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| Al Hadaqah | الحدقة | Rafha |  |  |  |  |  |  | 220.2 (242) | Buraidah (T2, 239) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| Al Judayyidah | الجديّدة | Arar |  |  |  |  |  |  | 241.9 (202) | Tabuk (T2, 572) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| Al Lumayma' | اللميماء | Al Uwayqilah |  |  |  |  |  |  | 273.8 (290) | Buraidah (T2, 491) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| Al `Ajrumiyah | العجرمية | Rafha |  |  |  |  |  |  | 283.9 (317) | Buraidah (T2, 412) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| As Saddah | السادَّة | Al Uwayqilah |  |  |  |  |  |  | 208.7 (261) | Buraidah (T2, 401) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| Ibn Suqi | إبن سوقي | Rafha |  |  |  |  |  |  | 274.1 (319) | Buraidah (T2, 388) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| Umm Khunsur | أم خنصر | Arar |  |  |  |  |  |  | 205.4 (206) | Buraidah (T2, 538) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| Umm Radamah | أم رضمة | Rafha |  |  |  |  |  |  | 250.3 (275) | Buraidah (T2, 271) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| Umm ad Diyan | أم الضيان | Arar |  |  |  |  |  |  | 251.2 (273) | Buraidah (T2, 549) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| Zahwah | زهوة | Al Uwayqilah |  |  |  |  |  |  | 219.1 (281) | Buraidah (T2, 416) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| jdedt arar | جديدة عرعر | Arar |  |  |  |  |  |  | 233.0 (196) | Tabuk (T2, 565) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| ragwah | رغوه | Rafha |  |  |  |  |  |  | 235.6 (269) | Buraidah (T2, 254) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| ابن بشيت | ابن بشيت | Rafha |  |  |  |  |  |  | 237.8 (255) | Buraidah (T2, 258) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| ابن عجل | ابن عجل | Rafha |  |  |  |  |  |  | 272.3 (331) | Buraidah (T2, 382) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| اللميماء | اللميماء | Al Uwayqilah |  |  |  |  |  |  | 274.7 (290) | Buraidah (T2, 491) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| حدق الجندة | حدق الجندة | Rafha |  |  |  |  |  |  | 232.5 (314) | Buraidah (T2, 328) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| قليب غنيم | قليب غنيم | Rafha |  |  |  |  |  |  | 227.1 (264) | Buraidah (T2, 246) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| مركز الصحن | مركز الصحن | Al Uwayqilah |  |  |  |  |  |  | 263.5 (261) | Buraidah (T2, 458) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |
| نواظر | نواظر | Rafha |  |  |  |  |  |  | 255.3 (338) | Buraidah (T2, 376) | none sourced | dunes | N | no sourced or grid population; no sourced economic role |
| هجرة ابن بكر | هجرة ابن بكر | Arar |  |  |  |  |  |  | 190.4 (198) | Tabuk (T2, 502) | none sourced | flat_desert | N | duplicate of KSA-ST-00857 (Ibn Bakr): Arabic-only record of the same place |
| هجرة ابن عايش | هجرة ابن عايش | Al Uwayqilah |  |  |  |  |  |  | 253.1 (254) | Buraidah (T2, 470) | none sourced | flat_desert | N | no sourced or grid population; no sourced economic role |

## Notes by row

- **Arar** (عرعر): Governorate centre (Arar). Population is the Census 2022 locality figure 199,247, not the governorate total 202,719 (S-cp2-gastat-007). Universe name '`Ar`ar' corrected to Arar. Arar Domestic Airport (S-cp1-100); Northern Borders University (S-r1a-221, S-r1a-222); Arar-Iraq border post (S-r1a-210; the brief names Jadidat Arar, see Needs judgement); MODON Arar Industrial City (S-r1a-204; no position sourced).
- **Rafha** (رفحاء): Governorate centre (Rafha). Locality 63,929, not the governorate total 84,536 (S-cp2-gastat-007). Rafha Domestic Airport (S-cp1-100). Terrain 'dunes' assumed (A-northern_borders-001).
- **Turayf** (طريف): Governorate centre (Turayf; GASTAT spelling Turayf, OSM Turayf). Locality 61,395, not the governorate total 66,004 (S-cp2-gastat-007). Turaif Domestic Airport, TUI (S-cp1-100). Not the Iraq-Jordan crossing Turaibil.
- **Linah** (لينة): Grid-only population 17,616 (WorldPop, S-r1a-506). Not in the GASTAT city list of 5,000 or more (S-cp2-gastat-008) under any spelling tried (Linah, Lina, Lin), which points to a population below 5,000 and to a grid over-count (region grid exceeds the residual: control_total_flag). tag_5k kept true because tag_5k is not gated. tag_10k false: no second method run (A-screen-032). Needs judgement. Pilot: OSM lists Linah twice (town node 1236407820 and a village way); one row kept.
- **Al-Uwayqilah** (العويقيلة): Governorate centre (Al-Uwayqilah). Primary city name 'Aluwayqilah' (S-cp2-gastat-008; identical to the relayed figure); locality 17,055, not the governorate total 20,318.
- **Badanah** (بدنة): Grid-only population 10,670 (WorldPop, S-r1a-506). OSM 'hamlet' (universe) with a grid figure above 10,000. Not in the GASTAT city list of 5,000 or more under the name Badanah. Unmatched primary name 'Albadie Walqarfi' (8,623; no OSM settlement by name) may be a variant; not resolved. tag_10k false (uncorroborated). Needs judgement.
- **Rawdat Habbas** (روضة هباس): Primary city name 'Rawdat Hibas' (S-cp2-gastat-008); OSM 'Rawdat Habbas'. The relayed figure 5,620 (S-cp2-gastat-001) matches the primary. The OSM place tag 5,532 is a 2010 value and is not used. Tagged 5k only.
- **At Timyat** (طلعة التمياط): Place below 5,000: not in the TA1 city export (cities of 5,000 or more), so the citypopulation.de figure (S-northern_borders-001) stays secondary. Name match to the GASTAT locality 'At Timyat' not confirmed. OSM 'village'.
- **Ibn Suayyid** (إبن سعيد): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Ash Shu‘bah** (شعبة نصاب): Place below 5,000 (secondary 3,430, S-northern_borders-001); not in the TA1 city export. The universe grid figure is 7,536 (2.2 times the secondary figure): a grid over-count flag, not used. OSM 'town' on a 3,430 place (tag/size mismatch, pilot).
- **Al Khushaybi** (الخشيبي): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **As Sulaymaniyah** (السليمانية): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **unnamed OSM node 2848030337** (): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Ibn Shuraym** (إبن شريم): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **ebn thunayyan** (ابن ثنيان): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Al Markuz** (المركوز): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **نعيجان** (نعيجان): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Daydeeb** (الديدب): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **الجبهان** (الجبهان): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Zibala** (زبالا): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Hazm al Jalamid** (حزم الجلاميد): Ma'aden Al-Jalamid phosphate mine and beneficiation plant (S-r1a-211, S-r1a-210). The mine polygon (31.507 N, 39.930 E) is about 30 km from the OSM village node used for the row (31.280 N, 40.104 E): R1a conflict, see Needs judgement. dist_existing_km is to the passenger stations (R1a, A-r1a-008); the nearest existing rail by alignment is the SAR North freight line (S-019) at 14.2 km (any-line column, A-r1a-007), which is the pilot's 14.2 km. Population: WorldPop grid only (187), unverified; no threshold depends on it.
- **اعيوج لينة** (اعيوج لينة): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **unnamed OSM node 348243528** (): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Qaysumat Fayhan** (قيصومة فيحان): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Ibn Bakr** (هجرة ابن بكر): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Nisab** (نصاب): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **الهبكة** (الهبكة): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Al Kasib** (الكاسب): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Lawqah** (لوقة): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **اليدية** (اليدية): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **مغطية** (مغطية): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Al Musandaq** (المصندق): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **السلمانية** (السلمانية): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **unnamed OSM node 11204976241** (): WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000.
- **Abu Sawr** (ابو صور): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Ad Duwayd** (الدويد): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Al Hadaqah** (الحدقة): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Al Judayyidah** (الجديّدة): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Al Lumayma'** (اللميماء): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Al `Ajrumiyah** (العجرمية): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **As Saddah** (السادَّة): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Ibn Suqi** (إبن سوقي): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Umm Khunsur** (أم خنصر): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Umm Radamah** (أم رضمة): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Umm ad Diyan** (أم الضيان): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **Zahwah** (زهوة): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **jdedt arar** (جديدة عرعر): 2010 city of 5,125 (runs/gastat/apply/cities2010_growth.csv) but not in the 2022 city list of 5,000 or more. WorldPop cells sum to 0, so the 2010-growth estimate (5,438; A-screen-035) cannot be tested against a grid figure and is not used. Needs judgement: merged into Arar or below 5,000 in 2022?
- **ragwah** (رغوه): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **ابن بشيت** (ابن بشيت): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **ابن عجل** (ابن عجل): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **اللميماء** (اللميماء): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **حدق الجندة** (حدق الجندة): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **قليب غنيم** (قليب غنيم): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **مركز الصحن** (مركز الصحن): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **نواظر** (نواظر): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).
- **هجرة ابن بكر** (هجرة ابن بكر): Arabic-only record of Ibn Bakr (KSA-ST-00857); excluded to avoid double counting.
- **هجرة ابن عايش** (هجرة ابن عايش): No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed).

## Changes from the pilot (`pilot-northern_borders`)

The pilot measured great-circle distance to the OSM line geometry. The R1a alignment distance over all existing lines (`dist_existing_any_line_km`, A-r1a-007; includes the SAR North freight line S-019) is the same kind of measure, so it is the comparison here. The register's `dist_existing_km` is R1a's passenger-station distance, which is not comparable with the pilot's line distance. Population values for the pilot's rows are the same GASTAT primary figures (identical), now sourced to S-cp2-gastat-008.

| name | pilot dist to existing line km | R2 alignment, any existing line km | nearest existing line (R2 alignment) | pilot dist metro km | R2 dist metro km |
|---|---:|---:|---|---:|---:|
| Arar | 95.2 | 95.1 | sar-north-freight | 516.7 | 516.7 |
| Rafha | 276.2 | 205.0 | sar-north-freight | 369.7 | 369.7 |
| Turaif | 96.4 | 96.4 | sar-north-passenger | 415.9 | 415.9 |
| Al-Uwayqilah | 215.3 | 215.3 | sar-north-freight | 479.3 | 479.3 |
| Rawdat Habas | 302.2 | 145.4 | sar-north-freight | 315.2 | 315.2 |
| Talah at-Tamiat | 271.6 | 237.8 | sar-north-freight | 400.4 | 400.4 |
| Sha'bih Nasab | 326.6 | 116.9 | sar-north-freight | 293.7 | 293.7 |
| Hazm al-Jalamid | 14.2 | 14.2 | sar-north-freight | 467.8 | 467.8 |

## Exclusions (rule 2: none silent)

Every settlement in the R1a universe for this region appears in the register. Excluded rows and their reasons are in the table above. Groups:

- 24 × below 5,000 (grid estimate only); no sourced economic role
- 22 × no sourced or grid population; no sourced economic role
- 2 × below 5,000 (secondary figure); no sourced economic role
- 1 × duplicate of KSA-ST-00857 (Ibn Bakr): Arabic-only record of the same place

## Sources

Population: S-cp2-gastat-007 (governorate totals, not used as populations), S-cp2-gastat-008 (primary city figures for places of 5,000 or more), S-cp2-gastat-001 (relayed DataPulse table, cross-check only: identical for the five primary cities), S-northern_borders-001 (citypopulation.de, secondary: At Timyat, Ash Shu'bah), S-r1a-506 (WorldPop 2020, 100 m, constrained, UN-adjusted; grid gap-fills).

Geometry, distances and roles: S-r1a-210 (OSM element ids and coordinates), S-r1a-809 (OSRM car skims), S-cp1-100 (airports: GACA report), S-r1a-204 (MODON), S-r1a-211 (Ma'aden Al-Jalamid), S-r1a-221 and S-r1a-222 (universities), S-northern_borders-002 and -003 (governorate seats), S-northern_borders-010 (Nafud erg; terrain assumption). Lines: S-017 (SAR North passenger), S-019 (SAR North freight), S-029 (GCC railway), S-054 (Landbridge).

Assumptions: `docs/assumptions.md` (merged at R2) (A-northern_borders-001…005). Population gate: A-screen-031…033; 2010 growth check A-screen-035; control total A-screen-037; roles A-screen-009.

## Needs judgement (not resolved by guessing)

1. **Linah (KSA-ST-00393)**: grid 17,616, but absent from the GASTAT list of cities of 5,000 or more under any spelling tried. Which is right, the grid (an over-count, as the control total suggests) or the list? Sets tag_5k.
2. **Badanah (KSA-ST-00884)**: grid 10,670, absent from the ≥ 5,000 list. Is the unmatched primary name 'Albadie Walqarfi' (8,623; no OSM settlement by name) the same place? Sets tag_5k, and tag_10k only if a figure is confirmed.
3. **Jadidat Arar (KSA-ST-01533)**: a 2010 city of 5,125 (`runs/gastat/apply/cities2010_growth.csv`), absent from the 2022 list; WorldPop cells sum to 0. Merged into Arar, or below 5,000 in 2022? Population left null.
4. **Ash Shu'bah (KSA-ST-00391)**: secondary 3,430 vs grid 7,536. The sourced figure is used; a GASTAT locality table is needed to confirm it.
5. **Hazm al Jalamid (KSA-ST-00856)**: the R1a mining node sits on the mine polygon (31.507 N, 39.930 E), about 30 km from the OSM village node used as the row (R1a conflict, `docs/sources`). Which point is the town? The distance to the freight line differs by that choice.
6. **Waad Al-Shamal MODON industrial city** (R1a node `modon-waad-al-shamal`; S-r1a-204; position from the OSM phosphate feature): not a settlement in the R1a universe, so it has no row. Add a row, or keep it as a node only?
7. **Al-Haditha border post (Jordan)** (R1a node `border-haditha-jordan`): no town in this region is tied to it in the sources read; left unassigned.
8. **Arar border post**: the brief names Jadidat Arar; the OSM names do not say which post is meant (R1a node `border-arar-iraq`, which asks for escalation).
9. **SAR North passenger, layer `existing`** (`cities/ksa/lines/sar-north-passenger.yaml`, S-017): the R2 sweep does not re-verify the opening status of the passenger service. The `dist_existing_km` values depend on the passenger stations it lists.
10. **Unmatched primary cities with no region in the export** (69 in total). NB-plausible names: Albadie Walqarfi (8,623) and Aleuruq Alshamalia (5,783), both without an OSM settlement. The export has no region column, so they cannot be placed in this region from the export alone.
11. **Terrain** is assumed for every row (A-northern_borders-001): no DEM run in this sweep.

Label: screening input, not a forecast.
