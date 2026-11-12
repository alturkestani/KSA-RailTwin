> **Document version:** docs/regions/asir.md v1.0 | 31 Oct 2026 | Author: region-scout (r2-asir, REGION_ASIR) | Status: draft

# Region sweep: Asir (عسير), slug `asir`

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast. Built by `screening/sweeps/asir/build_register.py` (seed 1; deterministic) from the R1a settlement universe and the primary GASTAT Census 2022 TA1 exports. Assumptions: `docs/assumptions.md` (merged at R2). Sources: `docs/sources/r2-asir.csv` and `docs/sources/index.csv`.

## Counts

| item | value | source |
|---|---|---|
| governorates per GASTAT (primary TA1 governorate table, Asir rows) | 18 | S-cp2-gastat-007 |
| governorates listed in the register (one centre row each) | 18 | this register |
| rows (all, incl. one screened out) | 37 | this register |
| governorate centres | 18 | this register |
| rows with `tag_10k` (population ≥ 10,000) | 13 | A-screen-001 |
| rows with `tag_5k` (population ≥ 5,000, sensitivity) | 32 | A-screen-002 |
| grid-only rows ≥ 10,000 held out of `tag_10k` (no corroborating method run) | 3 | A-screen-032, A-screen-033 |
| rows screened out | 1 | exclusion reason per row |
| populations by type: official / derived / grid / null | 16 / 3 / 18 / 0 | A-screen-031 |
| populations by status: verified / secondary / unverified | 14 / 5 / 18 | source-citation |
| sourced economic roles (rows with at least one) | 9 roles on 4 towns | S- id per role |
| rows with terrain assessed | 1 of 37 | see Terrain below |

GASTAT's Asir governorate total: the 18 primary governorate rows sum to 2,024,285, the same as the region total in S-soc-339 and the citypopulation figure in S-asir-001. OSM has 17 Asir governorate polygons (G015 to G031, `cities/ksa/zones/governorates.geojson`); the 18th, Al Amoah, has no polygon (C-r1a-20). Secondary lists differ (17 in Wikipedia, 18 in Saudipedia, per docs/status/pilot-asir.md; secondary, not checked here). This register follows the primary GASTAT table's 18.

Governorate name mapping (GASTAT primary → OSM name used in the register): An Namas → An Nimas; Zahran Al Janub → Dhahran Al Janub; Rijal Al Ma → Rijal Almaa. Other names match.

## Table

Columns: town (EN), town (AR), governorate (OSM name), centre, population, type / status, ≥10k, ≥5k, distance to existing station (km) / road minutes (OSRM, free flow), nearest committed planned station (Landbridge), nearest metro (tier), economic roles (sourced), terrain, flags, screened.

| town | town (AR) | governorate | centre | population | type / status | ≥10k | ≥5k | existing km / road min | committed station | nearest metro (tier) | economic roles | terrain | flags | screened |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Khamis Mushait | خميس مشيط | Khamis Mushayt | yes | 535,065 | official / verified | Y | Y | 463.7 / 483 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | military (S-asir-008) | not assessed | - | Y |
| Abha | أبها | Abha | yes | 334,290 | official / verified | Y | Y | 455.4 / 465 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | airport (S-cp1-100), tourism (S-r1a-240), university (S-r1a-221), industrial_city (S-r1a-204) | escarpment_mountain | - | Y |
| Bisha | بيشة | Bishah | yes | 115,537 | official / verified | Y | Y | 332.2 / 376 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | airport (S-cp1-100), mining (S-asir-009) | not assessed | - | Y |
| Muhayil | محايل عسير | Muhayil | yes | 97,967 | official / verified | Y | Y | 397.1 / 410 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Ahad Rafidah | أحد رفيدة | Ahad Rufaydah | yes | 79,202 | official / verified | Y | Y | 481.1 / 491 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Zahran al-Janub | ظهران الجنوب | Dhahran Al Janub | yes | 24,134 | official / verified | Y | Y | 572.0 / 568 | Saudi Landbridge (committed) - Muwai (Moya) | Najran (tier 3) / tier 3 | none sourced | not assessed | - | Y |
| An-Nimas | النماص | An Nimas | yes | 22,541 | official / verified | Y | Y | 353.9 / 361 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al Majaridah | المجاردة | Al Majardah | yes | 21,837 | official / verified | Y | Y | 338.1 / 357 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Sarat Abidah | سراة عبيدة | Sarat Abidah | yes | 19,855 | official / verified | Y | Y | 509.5 / 513 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Tathlith | تثليث | Tathlith | yes | 15,854 | official / verified | Y | Y | 439.7 / 512 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Tanumah | تنومة | Tanumah | yes | 12,442 | official / verified | Y | Y | 369.9 / 384 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al-Amwah | الأمواه | Al Amoah | yes | 9,200 | grid / unverified | N | Y | 503.9 / 595 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | judgement | Y |
| Fir'ah Tarib | فرعة طريب | Tarib | yes | 8,722 | official / verified | N | Y | 477.4 / 528 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Sabt Al 'Alayah | سبت العلاية | Balqarn | yes | 7,594 | grid / unverified | N | Y | 305.9 / 309 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | none sourced | not assessed | judgement | Y |
| Al-Birk | البرك | Al Birk | yes | 3,987 | official / secondary | N | N | 400.1 / 328 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | secondary | Y |
| Bariq | بارق | Bariq | yes | 2,858 | grid / unverified | N | N | 356.0 / 368 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al-Harjah | الحرجة | Al Harjah | yes | 435 | grid / unverified | N | N | 539.9 / 540 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | judgement | Y |
| Rijal Almaa | رجال ألمع | Rijal Almaa | yes | 288 | grid / unverified | N | N | 441.1 / 459 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | heritage (S-asir-010), agriculture (S-asir-010) | not assessed | judgement | Y |
| Masloom | مصلوُم | Khamis Mushayt | no | 12,376 | grid / unverified | N | Y | 459.3 / 484 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | grid gate | Y |
| Al Bashaer | البشائر | Balqarn | no | 12,021 | derived / secondary | Y | Y | 289.8 / 292 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | none sourced | not assessed | judgement; OSM tag; secondary | Y |
| Bahr Abu Sukaynah | بحر أبوسكينة | Muhayil | no | 10,862 | official / verified | Y | Y | 408.2 / 426 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al Harayr | الهرير | Khamis Mushayt | no | 10,260 | grid / unverified | N | Y | 471.5 / 490 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | grid gate | Y |
| King Faisal Military City | مدينة الملك فيصل العسكرية | Khamis Mushayt | no | 10,017 | grid / unverified | N | Y | 477.1 / 490 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | grid gate | Y |
| Al Mudhah | المضة | Tarib | no | 9,492 | grid / unverified | N | Y | 460.9 / 528 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Shawas Diyar Bani Was | شواص ديار بني واس | Balqarn | no | 8,422 | derived / secondary | N | Y | 281.9 / 293 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | none sourced | not assessed | OSM tag; secondary | Y |
| Tandahah | تندحة | Khamis Mushayt | no | 7,749 | grid / unverified | N | Y | 467.8 / 494 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al Sabikhah | الصبيخة | Tarib | no | 7,173 | grid / unverified | N | Y | 448.7 / 552 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Wadi Ibn Hishbal | وادي ابن هشبل | Khamis Mushayt | no | 6,587 | grid / unverified | N | Y | 437.1 / 479 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al Habil | الحبيل | Rijal Almaa | no | 5,810 | grid / unverified | N | Y | 449.5 / 452 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Tabalah | تبالة | Bishah | no | 5,670 | derived / secondary | N | Y | 296.9 / 349 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | OSM tag; secondary | Y |
| Al Ithnayn | الإثنين | Abha | no | 5,593 | official / verified | N | Y | 486.7 / 492 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al Bani Thawr | آل بني ثور | Khamis Mushayt | no | 5,396 | grid / unverified | N | Y | 466.4 / 491 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Ar Raysh | الريش | Muhayil | no | 5,392 | grid / unverified | N | Y | 393.0 / 418 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al Hammah | الحميمة | Bishah | no | 5,362 | grid / unverified | N | Y | 331.4 / 374 | Saudi Landbridge (committed) - Muwai (Moya) | Khamis Mushait (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Dirs | الضرس | Muhayil | no | 5,044 | grid / unverified | N | Y | 399.6 / 416 | Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Yuhan | يهن | Abha | no | 5,029 | grid / unverified | N | Y | 455.9 / 466 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | none sourced | not assessed | - | Y |
| Al Harajah | الحرجة | Balqarn | no | 4,540 | official / secondary | N | N | 307.0 / 316 | Saudi Landbridge (committed) - Muwai (Moya) | Abha (tier 2) / tier 2 | none sourced | not assessed | secondary | N |

Distances: `dist_existing_km` is the great-circle distance to the nearest existing station in the R1a set. In this set the only existing stations are on the Haramain line, so every Asir row points to Makkah (A-asir-004 covers the road minutes). `dist_committed_km` is to the Landbridge stations; the names are from `cities/ksa/lines/landbridge.yaml` (S-062). The two names used for Al-Jumum and Muwai are the same planned stops as S-asir-006 (names differ across sources). `dist_metro_km` is to the nearest metro reference node (A-screen-013 tiers); Abha and Khamis Mushait are each a reference node and are in the same metro group.

## Exclusions and screened-out rows

- **Al Harajah** (KSA-ST-00560, 4,540, secondary): screened out. It is the second node named Al Harajah, which containment places in Balqarn, and it is below 5,000. The Al-Harjah seat is KSA-ST-01075 (see the Needs merge-stage list).
- **Three grid-only towns ≥ 10,000 are held out of `tag_10k`** (`exclusion_reason` "grid-only population, uncorroborated"; they stay screened and `tag_5k` is true): Masloom 12,376, Al Harayr 10,260, King Faisal Military City 10,017. No second method has been run for them, and the 2010-growth method only applies to the matched 2010 cities of more than 5,000.
- No governorate is excluded. The pilot's Balqarn exclusion is resolved: the seat is now Sabt Al 'Alayah (see below).

## Needs judgement (not resolved here)

1. **Al-Harjah seat**: two candidate nodes. KSA-ST-01075 (containment: Al Harjah polygon, grid 435) is used; KSA-ST-00560 (Balqarn polygon, secondary 4,540) is screened out. A-asir-002.
2. **Al Amoah seat**: no OSM polygon (C-r1a-20); the node named Al Amoah lies in the Tathlith polygon. Used as the seat, grid 9,200 (unverified). The GASTAT governorate total 10,969 is not a settlement figure and is not used.
3. **Balqarn seat (Sabt Al 'Alayah)**: the OSM tag 200,000 is rejected (A-asir-003); WorldPop 7,594 used (unverified). The 2010 list has Al-Ulya at 19,956 with no 2022 match in the register, and GASTAT's 2022 ≥ 5,000 table does not list the town. The seat needs a GASTAT locality figure.
4. **Rijal Almaa seat**: grid 288 is implausibly low for a seat (heritage village, S-asir-010). Unverified; needs the GASTAT locality figure.
5. **OSM-tag towns not in GASTAT's ≥ 5,000 table**: Al Bashaer 12,021 (in `tag_10k`), Tabalah 5,670 and Shawas Diyar Bani Was 8,422. Derived (A-asir-001), not GASTAT figures, and their status is secondary. If GASTAT's locality data puts them below 5,000, they drop out of `tag_5k`.
6. **Bisha mining**: the role is exploration only (S-asir-009, a shortlist of exploration sites, secondary). It is not a producing mine and should not be treated as a mining economy.
7. **Khamis Mushait military role**: King Khalid Air Base is cited from secondary sources (S-asir-008). Not verified against a primary source.
8. **Terrain**: only Abha is classed (`escarpment_mountain`, S-asir-007, secondary). The rest are null because no DEM extract was run (disk gate); the pilot's `mixed` default for the other centres was not carried over as an assumption.
9. **Economic roles not sourced**: MODON Asir (industrial city, unlocated; tied to Abha by R1a, S-r1a-204), and the 2010 Al-Ulya town. No port, border, energy or giga-project node lies in Asir in the R1a set.

## Facts and conflicts to carry

- Population conflicts: none left open for an official figure. The R1a universe agrees with the primary table on every official row; the build asserts this for each row with a primary name. Tanumah (Tanawma in the primary table) is 12,442 in both.
- Relayed vs primary: citypopulation.de (S-asir-001) gives the same governorate sum (2,024,285) as the primary table. The DataPulse relayed table (S-cp2-gastat-001) is a cross-check only.
- Pilot (docs/status/pilot-asir.md) corrections: the Balqarn centre (osm 11891866421, Jawf Balqarn, Makkah) is dropped; the pilot's Al-Harjah node (1236690496) is the Balqarn-polygon node and is screened out; the pilot's Tanumah row had no population; it now carries the primary figure 12,442 (Tanawma).

## Sources

See `docs/sources/r2-asir.csv` (S-asir-001 to S-asir-014) and the shared index (`docs/sources/index.csv`) for S-cp2-gastat-001, -005, -007, -008, S-soc-339, S-cp1-100, S-r1a-204, S-r1a-210, S-r1a-221, S-r1a-240, S-062.

Population sources: S-cp2-gastat-008 (primary GASTAT city table; verified, value of record); S-cp2-gastat-007 (primary governorate table; governorate totals not used as town figures); S-asir-001 (citypopulation, GASTAT relayed, secondary); S-asir-012 (WorldPop 2020 grid, unverified); S-asir-013 (OSM tags, secondary).

Facts with no figure: the GASTAT governorate list is verified from the primary table (S-cp2-gastat-007). The GASTAT locality (place under 5,000) figures are not in the primary tables; that gap is the main open item.

Licences: OpenStreetMap contributors (ODbL 1.0) on every OSM-derived row; WorldPop (CC BY 4.0, doi:10.5258/SOTON/WP00684); GASTAT data (use policy; attribution). No new dataset was downloaded for this sweep (every input is registered in `cities/ksa/sources.yaml`).
