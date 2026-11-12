> **Document version:** docs/regions/al_baha.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_AL_BAHA) | Status: draft

# Al-Baha (الباحة) region sweep, slug `al_baha` (REGION_AL_BAHA, R2 input)

**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Access dates: 31 Oct 2026 for the R2 sources, 30 Oct 2026 for the pilot-derived ones (Asia/Riyadh). Register: `cities/ksa/regions/al_baha.parquet` (CSV mirror `.csv`); validated with `screening.region_sweep validate --strict` (ok, 16 rows, 10 governorates). Builder: `screening/sweeps/al_baha/build.py`; this page: `screening/sweeps/al_baha/docs.py`.

## Governorate count (reconciled)

| source | count | status |
|---|---|---|
| GASTAT Census 2022 TA1 primary export, governorate split (`S-al_baha-101`, S-cp2-gastat-007): ten Al-Bahah governorates, read by name against the OSM polygons | **10** | verified (primary export) |
| Their sum: 90,515 + 37,608 + 51,787 + 48,333 + 31,197 + 15,496 + 20,010 + 19,586 + 12,506 + 12,136 = 339,174, equal to the Al-Bahah region total (`S-r1a-502`, 339,174; `S-al_baha-112`) | 339,174 | checked in `build.py` (assertion) |
| OSM governorate polygons, Al-Bahah (`S-al_baha-105`) | 10 | derived |
| citypopulation.de Al-Bahah region table (`S-al_baha-112`, secondary, credits GASTAT) | 10 rows + region total; all 11 values equal the primary export to the person | cross-check, 0 conflicts over 2 % |
| Wikipedia, Al-Bahah Province (pilot `S-al_baha-005`): nine governorates plus the Al-Bahah capital | 9 + capital = 10 | secondary; consistent |

`governorates_gastat: 10` · `governorates_listed: 10`. The two counts are equal and the header records both.

**Not in this region:** `Al Harjah` (18,503) appears in the primary export. It is not one of the ten polygons, and adding it would break the region-total check (the ten sum exactly to 339,174). Its region is for the coverage audit to settle (`docs/coverage.md`); it is not in this register.

## Coverage of the register

- Rows: **16**; governorate centres: **10** (one per governorate; all 10 governorates have a row).
- Towns at or above 10,000 (`tag_10k`): **5**. All five official GASTAT towns in the region at or above 10,000 are in the register: Al-Bahah, Al-Makhwah (Al Mukhwah), Baljurashi, Al-'Aqiq, Qilwah.
- At or above 5,000 (`tag_5k`, sensitivity): **12** rows.
- Population provenance: 7 official rows (GASTAT Census 2022 TA1 city ≥ 5,000 primary export, `verified`, `S-al_baha-102`); 8 grid rows (WorldPop 2020 100 m constrained not UN-adjusted, `S-al_baha-104`, `unverified`). No row carries a derived figure, and no secondary aggregator figure is used.
- Grid rows at or above 10,000: none. The gate (A-screen-031/032) therefore did not bind. No second method was run, so no `pop_corroboration` value is stored.
- Excluded rows: none. Every row is `screened: true`.
- Settlements not in the register: 233 of the 248 Al-Bahah settlements in `cities/ksa/zones/settlements.parquet` are not carried here (the register holds 15 of them, plus the Al-Qara centre, which has no universe row). None is a town or city in OSM, and the largest of them is 4,322 (grid), below 5,000, so they fail the 5k test. They stay in the R1a universe for the coverage audit and the sensitivity runs.

## Register table

Distances are great-circle (haversine) to the station the R1a universe holds (`dist_method`); road minutes are OSRM free-flow, uncalibrated (`S-al_baha-106`). Committed distances go to **unlocated proxy stations** (`A-al_baha-004`); read them as indicative. Layers: `hhr:makkah` is the existing Haramain HSR station at Makkah Central (`cities/ksa/lines/hhr.yaml`, layer existing); `landbridge` is committed-layer in its YAML (`layer: committed`) and is announced/planned, so it is never labelled existing.

| Name (EN) | Name (AR) | Governorate | Centre | OSM id (type) | Lat, lon | Population | Pop type / status | Pop source | 10k / 5k | Existing: station, km, road min | Committed: line, km (proxy), road min | Metro: city, tier, km, road min | Economic roles (source) | Terrain | Screened |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Al Qara | القرى | Al Qara | yes | – (–) | 20.4768, 41.3334 | – | – / – | – | no / no | –, – km, – min | –, – km, – min | –, –, – km, – min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |
| Al-'Aqiq | العقيق | Al Aqiq | yes | 6767957154 (node) | 20.2836, 41.6560 | 19269 | official / verified | S-al_baha-102 | yes / yes | hhr:makkah, 231.4 km, 271.2 min | landbridge, 239.7 km, 285.7 min | Taif (tier 2), 2, 169.3 km, 196.8 min | administrative (S-al_baha-101;S-al_baha-105); airport (S-al_baha-108;S-al_baha-107) | escarpment_mountain | yes |
| Al Bahah | الباحة | Al Bahah | yes | 295921642 (node) | 20.0138, 41.4656 | 90515 | official / verified | S-al_baha-102 | yes / yes | hhr:makkah, 234.1 km, 221.5 min | landbridge, 256.2 km, 236.0 min | Taif (tier 2), 2, 177.3 km, 147.2 min | administrative (S-al_baha-101;S-al_baha-105); university (S-al_baha-110;S-al_baha-107); industrial_city (S-al_baha-111) | escarpment_mountain | yes |
| Rahwat al Barr | رهوة البر | Al Bahah | no | 1236690571 (node) | 20.0586, 41.4507 | 5035 | grid / unverified | S-al_baha-104 | no / yes | hhr:makkah, 229.6 km, 216.5 min | landbridge, 251.6 km, 231.1 min | Taif (tier 2), 2, 172.5 km, 142.2 min | none sourced | escarpment_mountain | yes |
| Al-Hajrah | الحجرة | Al Hajrah | yes | 1236690663 (node) | 20.1997, 41.0721 | 2812 | grid / unverified | S-al_baha-104 | no / no | hhr:makkah, 190.1 km, 238.8 min | landbridge, 212.9 km, 246.1 min | Taif (tier 2), 2, 137.2 km, 226.1 min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |
| Al-Mindak | المندق | Al Mandaq | yes | 1237964146 (node) | 20.1105, 41.2828 | 8674 | official / verified | S-al_baha-102 | no / yes | hhr:makkah, 212.8 km, 224.4 min | landbridge, 235.2 km, 238.9 min | Taif (tier 2), 2, 157.4 km, 150.1 min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |
| Musaylah | مسيلة | Al Mandaq | no | 1237964360 (node) | 20.1595, 41.2843 | 5590 | grid / unverified | S-al_baha-104 | no / yes | hhr:makkah, 209.2 km, 226.0 min | landbridge, 231.4 km, 240.5 min | Taif (tier 2), 2, 153.0 km, 151.6 min | none sourced | escarpment_mountain | yes |
| Awirah | عويرة | Al Mandaq | no | 4975921682 (node) | 20.1852, 41.2587 | 5342 | grid / unverified | S-al_baha-104 | no / yes | hhr:makkah, 205.3 km, 230.1 min | landbridge, 227.5 km, 244.7 min | Taif (tier 2), 2, 149.1 km, 155.8 min | none sourced | escarpment_mountain | yes |
| Al Makhwah | المخواة | Al Mukhwah | yes | 1236690590 (node) | 19.7794, 41.4356 | 26248 | official / verified | S-al_baha-102 | yes / yes | hhr:makkah, 250.1 km, 264.0 min | landbridge, 273.1 km, 274.7 min | Taif (tier 2), 2, 196.9 km, 189.6 min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |
| Al Marwa | المروة | Al Mukhwah | no | 11871768367 (node) | 19.8262, 41.4465 | 6521 | grid / unverified | S-al_baha-104 | no / yes | hhr:makkah, 247.2 km, 258.2 min | landbridge, 269.9 km, 272.7 min | Taif (tier 2), 2, 193.1 km, 183.9 min | none sourced | escarpment_mountain | yes |
| Sayal | سيال | Al Mukhwah | no | 13564183874 (node) | 19.7929, 41.4335 | 6106 | grid / unverified | S-al_baha-104 | no / yes | hhr:makkah, 248.9 km, 264.7 min | landbridge, 271.8 km, 277.1 min | Taif (tier 2), 2, 195.5 km, 190.4 min | none sourced | escarpment_mountain | yes |
| Al Tawilah | الأطاولة | Al Qara | no | 9327998071 (node) | 20.2475, 41.3607 | 2032 | grid / unverified | S-al_baha-104 | no / no | hhr:makkah, 208.9 km, 197.8 min | landbridge, 230.5 km, 212.3 min | Taif (tier 2), 2, 150.3 km, 123.4 min | none sourced | escarpment_mountain | yes |
| Bani Hasan | بني حسن | Bani Hasan | yes | 3734863966 (node) | 20.0535, 41.3737 | 6344 | official / verified | S-al_baha-102 | no / yes | hhr:makkah, 224.0 km, 230.7 min | landbridge, 246.3 km, 245.2 min | Taif (tier 2), 2, 168.0 km, 156.4 min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |
| Baljurashi | بلجرشي | Biljurashi | yes | 1236690533 (node) | 19.8594, 41.5572 | 35985 | official / verified | S-al_baha-102 | yes / yes | hhr:makkah, 252.8 km, 246.6 min | landbridge, 275.2 km, 261.1 min | Taif (tier 2), 2, 196.8 km, 172.3 min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |
| Ghamid Az Zinad | غامد الزناد | Farat Ghamid Az Zinad | yes | 6770793665 (node) | 19.5944, 41.5201 | 1528 | grid / unverified | S-al_baha-104 | no / no | hhr:makkah, 271.3 km, 302.3 min | landbridge, 294.5 km, 309.6 min | Abha (tier 2), 2, 184.9 km, 232.7 min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |
| Qilwah | قلوه | Qilwah | yes | 8506335688 (node) | 19.9401, 41.2513 | 13069 | official / verified | S-al_baha-102 | yes / yes | hhr:makkah, 223.9 km, 261.4 min | landbridge, 246.9 km, 275.9 min | Taif (tier 2), 2, 171.6 km, 187.1 min | administrative (S-al_baha-101;S-al_baha-105) | escarpment_mountain | yes |

Notes per row (from `notes`):

- **Al Qara**: governorate centre not located in the universe: lat/lon are the governorate polygon's representative point (A-al_baha-002, flagged); no population, no distances (pending)
- **Al-'Aqiq**: governorate centre (OSM seat, A-screen-011); population: GASTAT Census 2022 TA1 city>=5,000 primary export (S-al_baha-102); grid figure 10270 not used (official figure governs); airport role (A-al_baha-003): King Saud bin Abdulaziz (ABT) is 2.2 km from this centre and 36.3 km from Al-Bahah; R1a names Al-Bahah as nearest town; committed distances go to unlocated proxy stations (A-al_baha-004)
- **Al Bahah**: governorate centre (OSM seat, A-screen-011); population: GASTAT Census 2022 TA1 city>=5,000 primary export (S-al_baha-102); grid figure 7887 not used (official figure governs); MODON Al-Baha Industrial City: no position source; attached by name (unlocated); committed distances go to unlocated proxy stations (A-al_baha-004)
- **Rahwat al Barr**: committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: inside a matched city's A-r1a-004 radius: possible double counting with the city extent
- **Al-Hajrah**: governorate centre (OSM seat, A-screen-011); OSM place=village as a governorate seat (kept as tagged); committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: grid over-count or boundary mismatch (region grid sum exceeds the residual)
- **Al-Mindak**: governorate centre (OSM seat, A-screen-011); population: GASTAT Census 2022 TA1 city>=5,000 primary export (S-al_baha-102); grid figure 1040 not used (official figure governs); committed distances go to unlocated proxy stations (A-al_baha-004)
- **Musaylah**: committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: grid over-count or boundary mismatch (region grid sum exceeds the residual)
- **Awirah**: committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: grid over-count or boundary mismatch (region grid sum exceeds the residual)
- **Al Makhwah**: governorate centre (OSM seat, A-screen-011); population: GASTAT Census 2022 TA1 city>=5,000 primary export (S-al_baha-102); grid figure 7954 not used (official figure governs); committed distances go to unlocated proxy stations (A-al_baha-004)
- **Al Marwa**: committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: grid over-count or boundary mismatch (region grid sum exceeds the residual)
- **Sayal**: OSM hamlet, grid only; English name is our transliteration (none in OSM or GASTAT); committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: inside a matched city's A-r1a-004 radius: possible double counting with the city extent
- **Al Tawilah**: committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: grid over-count or boundary mismatch (region grid sum exceeds the residual)
- **Bani Hasan**: governorate centre (OSM seat, A-screen-011); population: GASTAT Census 2022 TA1 city>=5,000 primary export (S-al_baha-102); grid figure 378 not used (official figure governs); centre conflict: OSM town vs Saudipedia Bidan / Wadi Al-Sadr (S-al_baha-113); committed distances go to unlocated proxy stations (A-al_baha-004)
- **Baljurashi**: governorate centre (OSM seat, A-screen-011); population: GASTAT Census 2022 TA1 city>=5,000 primary export (S-al_baha-102); grid figure 2988 not used (official figure governs); committed distances go to unlocated proxy stations (A-al_baha-004)
- **Ghamid Az Zinad**: governorate centre (OSM seat, A-screen-011); committed distances go to unlocated proxy stations (A-al_baha-004); R1a control-total flag: grid over-count or boundary mismatch (region grid sum exceeds the residual)
- **Qilwah**: governorate centre (OSM seat, A-screen-011); population: GASTAT Census 2022 TA1 city>=5,000 primary export (S-al_baha-102); grid figure 23422 not used (official figure governs); two OSM nodes; governorate node 6768458212 not used; committed distances go to unlocated proxy stations (A-al_baha-004)

## Economic roles (sourced; A-screen-011)

- **Administrative** (governorate seat): all ten centres (`S-al_baha-101` governorate name; `S-al_baha-105` OSM polygon).
- **University**: Al-Bahah, Al Baha University (`S-al_baha-110`, Wikipedia list by province; location `S-al_baha-107` OSM node 7994033787, about 2.6 km from the Al-Bahah centre). The public status is derived by subtraction (`S-r1a-222`) and is not checked against the Ministry list.
- **Industrial city**: Al-Bahah, MODON Al-Baha Industrial City (`S-al_baha-111`). No position source exists, so the role is attached by name and the row is flagged.
- **Airport**: Al-Aqiq, King Saud bin Abdulaziz (ABT) domestic airport (`S-al_baha-108` Wikipedia: "located in Al-Aqiq"; location `S-al_baha-107`). The airport is 2.2 km from the Al-Aqiq centre and 36.3 km from Al-Bahah, by great circle (see `A-al_baha-003`).
- **Region-level, not attached to a town (not in the register):** summer tourism and honey (AJEL, `S-al_baha-011` in the pilot file; no year). Heritage villages (a travel guide) and a pomegranate figure from a search snippet are not used. No port, mining, border-crossing, giga-project, Hajj/Umrah, military or energy node was found for Al-Baha in the sources read.
- **Not assessed:** roles for the other towns are empty ("none sourced"), not "none exist".

## Terrain

All sixteen rows: `escarpment_mountain`, a region-level class from the Sarawat escarpment (`S-al_baha-109`). The DEM was not sampled (disk gate; `A-al_baha-001`). This is not a per-town result, and R3 should replace it with DEM classes.

## Exclusions

None. The Al-Qara centre is kept, not excluded: its coordinates are a flagged polygon point (`A-al_baha-002`), not a located town.

## Needs judgement (not resolved here)

1. **Al-Qara centre.** The OSM universe has no place node for the governorate seat (Al-Qara, 19,586 in the governorate total; no town figure). The row uses the polygon representative point (20.4768 N, 41.3334 E) with no distances and no population. A located centre (GASTAT locality list, which is not reachable, or OSM) is needed. The geo-verify step was **not run**: its estimator downloads Microsoft building-footprint tiles and imagery, which the R2 disk gate does not allow in this track (see the status block).
2. **Airport attachment.** R1a's economic node names Al-Bahah as nearest town. By great-circle distance the airport is nearer Al-Aqiq. Al-Aqiq is used, following the Wikipedia location. Confirm before the R2 roles are frozen.
3. **Al-Hajrah seat.** OSM tags the governorate seat `place=village` (grid 2,812). Governorate total 12,136. No town-level census figure is sourced.
4. **Ghamid Az Zinad seat.** OSM town, grid 1,528, governorate total 12,506. The seat's population is not sourced, and the grid figure is far below the governorate total.
5. **Bani Hasan centre.** OSM town node (6,344 official) versus Saudipedia's Bidan and Wadi Al-Sadr (`S-al_baha-113`). The OSM node is used; the Saudipedia conflict is not resolved.
6. **Qilwah.** Two OSM nodes (town 8506335688 used; governorate node 6768458212 not used). The official figure is for the town; the governorate total is 31,197.
7. **Committed distances.** Landbridge and GCC station sites are unlocated proxies (A-r1a-006). The road target for Al-Makhwah is Jeddah (a proxy), while its great-circle station is Al-Jumum; both are shown in the source fields.
8. **R1a control-total and double-counting flags** (grid rows Rahwat al Barr, Sayal). Not excluded. Two villages may double-count a matched city's extent (`A-r1a-004`). Settle in R2 review.
9. **Grid over-count flag** on the region's residual (`control_total_flag`): the grid sum over Al-Bahah exceeds the residual. Reported only (A-screen-037).
10. **Terrain** is region-level (A-al_baha-001).

## Sources

Full rows in `docs/sources/r2-al_baha.csv` (ids `S-al_baha-101` to `S-al_baha-113`). Cross-references to shared ids: `S-al_baha-101` = S-cp2-gastat-007; `S-al_baha-102` = S-cp2-gastat-008; `S-al_baha-104` = S-r1a-505; `S-al_baha-106` = S-r1a-809; `S-al_baha-107` = R1a economic nodes (S-r1a-204, S-r1a-210, S-r1a-221, S-r1a-222, S-cp1-100); `S-al_baha-110` = S-r1a-221; `S-al_baha-111` = S-r1a-204.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Screening input, not a forecast.
