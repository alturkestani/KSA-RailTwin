> **Document version:** docs/regions/pilot-asir.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, PILOT_REGION_ASIR) | Status: draft

# Asir (عسير) pilot region sweep, coarse

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.
Pilot scope: a coarse sweep to test the schema (PROJECT.md W2 full register is R2, `REGION_ASIR`). Research only; no downloads; no grids or PBF extracts beyond the local OSM symlink already in the manifest.

## Header

- `governorates_gastat`: **18** (secondary: citypopulation.de's census-2022 governorate table, which credits GASTAT; **S-asir-001**). The GASTAT primary table was not reached: `portal.saudicensus.sa` returned a DNS failure on 30 Oct 2026 (S-072, S-090).
- `governorates_listed`: **18** (rows in `cities/ksa/regions/pilot-asir.parquet`, one centre row each).
- **Discrepancy flagged, not resolved:** the English Wikipedia infobox and the Arabic Wikipedia table give 17 governorate rows for Asir, and Saudipedia gives 18 plus Abha (`docs/gastat-regions.md`, S-074 to S-076). The 18 used here include Abha as its own governorate row, as the census table does. Primary GASTAT confirmation is still needed before R2.
- Register: `cities/ksa/regions/pilot-asir.parquet` (18 rows, 36 columns) and `pilot-asir.csv` (same rows and ids). Both validate against `common.schemas.RegionRow`, which was extended additively for the pilot (see Schema changes below). `screening.region_sweep` does not exist in this worktree, so the validation is `common.schemas.load_region_register`.

## Coverage

Every governorate has one row (its centre). The table below holds the census governorate totals (S-asir-001). These are perimeter populations, not settlement sizes, so they are not used as the populations in the register.

| governorate (EN) | governorate (AR) | population 2022 (governorate) |
|---|---|---|
| Abha | أبها | 422,243 |
| Ahad Rafidah | أحد رفيدة | 107,894 |
| Al-Amwah | الأمواه | 10,969 |
| Al-Birk | البرك | 22,583 |
| Al-Harjah | الحرجة | 18,503 |
| Al-Majaridah | المجاردة | 48,302 |
| An-Nimas | النماص | 38,409 |
| Balqarn | بالقرن | 60,012 |
| Bariq | بارق | 44,880 |
| Bisha | بيشة | 202,096 |
| Khamis Mushait | خميس مشيط | 601,305 |
| Muhayil | محايل | 230,537 |
| Rijal Alma | رجال ألمع | 50,825 |
| Sarat Abidah | سراة عبيدة | 57,123 |
| Tanumah | تنومة | 17,756 |
| Tarib | طريب | 22,298 |
| Tathlith | تثليث | 36,451 |
| Zahran al-Janub | ظهران الجنوب | 32,099 |
| **Total (Asir region, census 2022)** | | **2,024,285** (matches the region total on S-asir-001) |

Centre populations are the census place-table values (places of at least 2,500 inhabitants, S-asir-001). Where a centre is not in that table, its population is `null` and it is not guessed.

## Register rows (generated from the Parquet)

| name (EN) | name (AR) | governorate | population (centre, 2022) | tags | dist. existing (km) | dist. committed (km) | dist. metro (km) | nearest metro (tier) | terrain | economic roles | pilot sample | screened |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Abha | أبها | Abha | 334,290 | 50k, 10k | 455.4 | 475.6 | 0.0 | Abha-Khamis Mushait (tier 2) | escarpment_mountain | airport; administrative |  | yes |
| Ahad Rafidah | أحد رفيدة | Ahad Rafidah | 79,202 | 50k, 10k | 481.1 | 486.3 | 17.4 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | yes |
| Al-Amwah | الأمواه | Al-Amwah | null | - | 503.9 | 458.7 | 108.1 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | yes |
| Al-Birk | البرك | Al-Birk | 3,987 | - | 400.1 | 424.4 | 102.2 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | yes |
| Al-Harjah | الحرجة | Al-Harjah | 4,540 | - | 307.0 | 319.0 | 160.7 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | yes |
| Al-Majaridah | المجاردة | Al-Majaridah | 21,837 | 10k | 338.1 | 361.2 | 118.6 | Abha-Khamis Mushait (tier 2) | mixed | none sourced | yes | yes |
| An-Nimas | النماص | An-Nimas | 22,541 | 10k | 353.9 | 371.2 | 107.5 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | yes |
| Balqarn | بالقرن | Balqarn | null | - | 317.7 | 340.6 | 140.4 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | no |
| Bariq | بارق | Bariq | null | - | 356.0 | 379.4 | 99.5 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | yes |
| Bisha | بيشة | Bisha | 115,537 | 50k, 10k | 332.2 | 284.5 | 189.5 | Abha-Khamis Mushait (tier 2) | mixed | mining |  | yes |
| Khamis Mushait | خميس مشيط | Khamis Mushait | 535,065 | 50k, 10k | 463.7 | 471.0 | 0.0 | Abha-Khamis Mushait (tier 2) | mixed | military |  | yes |
| Muhayil | محايل عسير | Muhayil | 97,967 | 50k, 10k | 397.1 | 420.8 | 60.5 | Abha-Khamis Mushait (tier 2) | mixed | none sourced |  | yes |
| Rijal Almaa | رجال ألمع | Rijal Alma | null | - | 441.1 | 464.8 | 24.4 | Abha-Khamis Mushait (tier 2) | mixed | heritage; tourism; agriculture |  | yes |
| Sarat Abidah | سراة عبيدة | Sarat Abidah | 19,855 | 10k | 509.5 | 504.3 | 48.4 | Abha-Khamis Mushait (tier 2) | mixed | none sourced | yes | yes |
| Tanumah | تنومة | Tanumah | 12,442 | 10k | 369.9 | 389.6 | 89.2 | Abha-Khamis Mushait (tier 2) | mixed | none sourced | yes | yes |
| Fir'ah Tarib | فرعة طريب | Tarib | 8,722 | 5k | 477.4 | 455.9 | 57.7 | Abha-Khamis Mushait (tier 2) | mixed | none sourced | yes | yes |
| Tathlith | تثليث | Tathlith | 15,854 | 10k | 439.7 | 369.8 | 159.1 | Abha-Khamis Mushait (tier 2) | mixed | none sourced | yes | yes |
| Zahran al-Janub | ظهران الجنوب | Zahran al-Janub | 24,134 | 10k | 572.0 | 561.8 | 75.9 | Najran (tier 3) | mixed | none sourced |  | yes |

Distances are straight-line (haversine) from OSM coordinates; road minutes are empty (`road_min_method: pending R1a skims`, A-screen-pilot-001). Abha and Khamis Mushait show 0.0 km to metro because they are the metro nodes themselves.

## Towns of 50,000 or more (threshold_50k)

Five centre rows reach 50,000 in the census place table: Abha (334,290), Ahad Rafidah (79,202), Bisha (115,537), Khamis Mushait (535,065) and Muhayil (97,967). The place table lists no non-centre settlement in Asir at 50,000 or more.

Two governorate totals are at or above 50,000 while their centre is not in the place table, or is below 50,000: Balqarn (60,012), Rijal Alma (50,825) and Sarat Abidah (57,123, centre 19,855). These are listed under "Needs judgement".

## Pilot sample of towns between 5,000 and 50,000

Five rows carry `pilot_sample: true`, each with a reason in the register:
- **Al-Majaridah** (21,837): schema edge: centre 21,837 in a governorate of 48,302 (just under 50k)
- **Sarat Abidah** (19,855): schema edge: governorate total 57,123 (>= 50k) but centre 19,855 (< 50k)
- **Tanumah** (12,442): 5k-50k band; far from rail; no sourced economic role found
- **Fir'ah Tarib** (8,722): 5k-10k band edge; centre name matched from OSM 'فرعة طريب' to S-asir-001 'فرعه طريب' (name match, not confirmed as the governorate seat)
- **Tathlith** (15,854): 5k-50k band; far from rail; no sourced economic role found

Stratification result, stated plainly:
- **Near rail (under 25 km of an existing or committed station):** no Asir centre qualifies. The nearest is 284 km to a committed station and 307 km to an existing one. The near stratum is empty and is not filled with a town from another region.
- **Far rail (over 100 km):** every row qualifies (all centres are over 280 km from any station used here).
- **With a sourced economic role:** no sampled town in the 5,000–50,000 band has a sourced role. The sourced roles (airport, military, mining exploration, heritage) sit with Abha, Khamis Mushait, Bisha and Rijal Alma, which are either outside the band or have no sourced population.

## Exclusions

- **Balqarn** (centre): `screened = false`. OSM has no node named بالقرن. The coordinates are provisional on the village جوف بلقرن, and the centre is not assigned. Reason recorded in the register.
- No other row is excluded.

## Needs judgement

1. **Balqarn centre.** Which settlement is the governorate seat? The candidates are جوف بلقرن, شعف بلقرن and نخال بلقرن (OSM villages). The row is excluded until this is decided.
2. **Al-Harjah centre.** Three OSM nodes are named الحرجة (19.58N 41.98E village; 17.92N 43.37E town; 21.86N 40.18E hamlet). The row uses the first, unconfirmed.
3. **Governorate totals at or above 50k with no matching centre** (Balqarn, Rijal Alma, Sarat Abidah): does the 50k tag apply to the governorate perimeter or only to settlements? The register tags settlements only.
4. **Tarib centre name.** The row is named "Fir'ah Tarib" from OSM فرعة طريب matched to the census place فرعه طريب. It is not confirmed as the governorate seat.
5. **Al-Amwah.** The Arabic name is from the aggregator. The centre population is `null`. Its OSM node is named "Al Amoah".
6. **Bariq, Rijal Alma.** Centre populations are `null` (not in the census place table). Rijal Alma is in a governorate of 50,825.
7. **Terrain for non-Abha centres** is `mixed` by assumption (A-screen-pilot-002); no DEM was used. Abha is classed `escarpment_mountain` from the Sarawat escarpment description (S-asir-007), not from elevation data.
8. **Mining role at Bisha** is exploration only (Muhaddad site, S-asir-009). No production data was found, so the role is recorded as exploration and not as an operating mine.

## Rail layers (kept apart)

- **Existing:** Haramain / HHR station nodes (Makkah, Madinah, KAEC, Jeddah airport, Riyadh; S-asir-004, S-asir-005). Jeddah Al-Sulaymaniyah has no coordinate in the sources used and is omitted (A-screen-pilot-005). No existing line serves Asir.
- **Committed / under procurement:** Saudi Landbridge (Riyadh–Jeddah leg), intermediate stations Al Jumum, Al Muwayh and Ad Dawadimi (S-asir-006). Layer `committed`, never existing. The intermediate station names conflict across sources (Jumoum/Jamuma; Muwai/Moya; Dawadmi/Al-Doadmi). The coordinates come from OSM places matched by name (A-screen-pilot-003). A 2026 report says contracts are not yet signed.
- **Not used:** the GCC railway and the Riyadh Rail Link, which do not serve Asir. Their station lists were not loaded for the pilot.

## Metro set

Tiers from A-screen-013 (primary Riyadh, Jeddah, Makkah, Madinah, Dammam–Khobar; secondary Taif, Buraidah, Tabuk, Abha–Khamis Mushait; tertiary Jazan, Najran). The nearest metro is chosen across all tiers. Metro coordinates are OSM city-node proxies (A-screen-pilot-004).

## Schema changes (additive; `common/schemas.py`)

- `pop_type` accepts `secondary` (aggregator figures, flagged).
- New optional fields: `threshold_50k` (population >= 50,000, validated), `pilot_sample` and `pilot_reason` (reason required when set), `distance_method`, `primary_to_find`.
- `TAG_50K` constant (pilot only, not a CP1 threshold).
- Existing rows and fixtures are unaffected (all new fields default to off or null).

## Licences and attribution

- Map data: © OpenStreetMap contributors, ODbL 1.0. Place and station coordinates come from the local GCC extract (`osm-gcc-2026-10-14`, already in `cities/ksa/sources.yaml`).
- Population figures: citypopulation.de (T. Brinkhoff), crediting GASTAT; terms not checked, used for facts with citation only, not copied (see `docs/data-sources.md`).

## Sources

See `docs/sources/pilot-asir.csv` (S-asir-001 to S-asir-010) and the existing S-072, S-074 to S-076 and S-090 in `docs/sources/index.csv`.
