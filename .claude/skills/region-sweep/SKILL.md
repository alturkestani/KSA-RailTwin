---
name: region-sweep
description: Schema and procedure for one region-scout sweep: every GASTAT governorate of the region and every town at or above the population threshold, with sourced population, distances to existing, committed and metro rail, economic roles and terrain, written to cities/ksa/regions/<region>.parquet and docs/regions/<region>.md. Use for W2 region registers and the national pilot.
---
> **Document version:** skills/region-sweep/SKILL.md v1.6 | 31 Oct 2026 | Author: coordinator; merged schema by CP1_PREP; geo-verify step aligned to the CLI by GEO_VERIFY; population rule and GASTAT addendum by CP2_PREP | Status: active

# Region sweep

Rule 2: no silent omissions. Every governorate of the region appears, screened or excluded with a reason. Rule 1: every population and distance has a source id.

## The 13 regions (slug, English, Arabic)
`riyadh` Riyadh الرياض · `makkah` Makkah مكة المكرمة · `madinah` Madinah المدينة المنورة · `eastern` Eastern Province المنطقة الشرقية · `qassim` Qassim القصيم · `asir` Asir عسير · `tabuk` Tabuk تبوك · `hail` Hail حائل · `northern_borders` Northern Borders الحدود الشمالية · `jazan` Jazan جازان · `najran` Najran نجران · `al_baha` Al-Baha الباحة · `al_jouf` Al-Jouf الجوف

## Governorate list requirement
Take the official GASTAT list of governorates (محافظات) for the region as published by GASTAT (Census 2022 tables or the administrative-divisions list; record the URL and access date as `S-xxx`). Every governorate becomes at least one row (its centre). The file header records `governorates_gastat: <n>` and `governorates_listed: <n>`; they must be equal or the sweep is incomplete. If GASTAT and another source disagree on the count, write both and flag it.

## Register schema (one row per settlement; Parquet, pydantic model `RegionRow` in `common/schemas.py`)
| field | type | rule |
|---|---|---|
| name_ar, name_en | str | official spelling; transliteration as used by GASTAT/OSM |
| region, governorate | str | slugs as above; governorate in English and Arabic (`governorate_ar`) |
| is_governorate_centre | bool | |
| osm_id, osm_type | int or null; `node` / `way` / `relation` | `place=*` element; the type is required with the id (ids overlap across types) |
| lat, lon | float | WGS84 |
| population | int or null | |
| pop_source | `S-xxx` | required when population is set |
| pop_year | int | |
| pop_type | `official` / `derived` / `grid` | GASTAT = official; GASTAT share applied = derived; GHSL/WorldPop = grid. Never `secondary`. Precedence (A-screen-031): official > derived > grid; a grid figure only where no official or derived figure exists, and then `pop_source_status: unverified` (the schema rejects anything else) |
| pop_source_status, primary_to_find | `verified` / `secondary` / `unverified`; str | read on GASTAT = verified; a GASTAT figure relayed by an aggregator (citypopulation.de) = `official` + `secondary` + `primary_to_find` naming the GASTAT table; settlement (place) figure, never the governorate total |
| tag_10k, tag_5k | bool | population ≥ 10,000; ≥ 5,000 (sensitivity). Never `threshold_5k`. **Grid rows:** `tag_10k = true` only if `pop_corroboration` agrees within 30 % (abs(grid − value) / grid ≤ 0.30, A-screen-032); otherwise `tag_10k = false` and `exclusion_reason` contains "grid-only population, uncorroborated" (the row stays `screened`). `tag_5k` is not gated |
| pop_corroboration, pop_corroboration_value | `buildings_x_occupancy` / `ghs_pop_sum` / `viirs_calibrated` / `gastat2010_city_growth`; float | grid rows only; the second independent method and its value (A-screen-033). Leave both null when no second method has been run: never invent one. WorldPop never corroborates itself |
| threshold_50k, pilot_sample | bool or null | **pilot only** (null in R2 registers); `pilot_sample = true` needs the reason in `notes` |
| dist_existing_km, road_min_existing | float or null | to the nearest existing line station or alignment; name in `nearest_existing` |
| dist_committed_km, road_min_committed, nearest_committed, nearest_committed_station | | committed/under-procurement lines and their planned stations |
| dist_metro_km, road_min_metro, nearest_metro | | nearest metro in the approved set (A-screen-013): primary Riyadh, Jeddah, Makkah, Madinah, Dammam–Khobar–Dhahran; secondary Taif, Buraidah, Tabuk, Abha–Khamis Mushait; tertiary Jazan, Najran; record `nearest_metro_tier` (1/2/3) too |
| road_min_method, dist_method, notes | str | e.g. `pending R1a skims`, `haversine` |
| economic_roles | list of `{role, source}` | roles: port, industrial_city, mining, tourism, heritage, hajj_umrah, airport, university, giga_project, agriculture, border_crossing, military, administrative, energy (refineries, oil/gas processing, export terminals). The source must tie the role to that town. `administrative` is kept in the data but does not enter the screening score (A-screen-009) |
| terrain_class | `flat_desert` / `dunes` / `sabkha` / `escarpment_mountain` / `coastal` / `mixed` | these words only (not `sand_dunes`, `coastal_plain`); from DEM; source id or assumption id |
| screened | bool | false only with `exclusion_reason` |
| exclusion_reason | str or null | e.g. "below 5k and no economic role", "inside metro area, handled by commuter belt" |
| sources | list of `S-xxx` | |

## Population rule (CP2 P1a)
Population rule (Tariq, CP2, 31 Oct 2026; A-screen-031…033): "GASTAT-relayed figures win where they exist; WorldPop fills gaps only, every gap row flagged `pop_type: grid`, `pop_source_status: unverified`. A grid-only settlement may pass the ≥ 10k test only if a second independent method (building footprints × occupancy, GHSL, or VIIRS-calibrated) corroborates it within 30 %. Sensitivity to report: WorldPop ÷ 0.64 (the back-test median ratio), with the list of settlements whose ≥ 10k status flips; the correction is **not** applied to the base case." In the sweep: take GASTAT first; use the R1a grid figure only for a settlement GASTAT does not tabulate; record a second method only if it was actually run (as of the GASTAT addendum, 31 Oct 2026, six grid-only rows carry a 2010-growth value and none is within 30 %; and the buildings estimator is record-only after failing its back-test, `docs/geo-verify.md` §3). The grid sensitivity is run by `screening.funnel sensitivity-grid`, not by the sweep; never store a corrected figure in `population`.

GASTAT addenda (Tariq, 31 Oct 2026): the **primary** Census 2022 TA1 exports `data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx` (150 governorates, S-cp2-gastat-007) and `census2022_TA1_city5k_primary.xlsx` (271 cities of 5,000 or more plus "Other (< 5,000)" = 3,683,816, S-cp2-gastat-008) "supersede the relayed file at governorate and city level" (addendum 2, 15:25): a settlement matched to a primary city gets that figure as `pop_type: official`, `pop_source_status: verified`, and "the ≥ 10k test for those rows uses the primary figure only (no corroboration needed)" (matching tiers and guards A-screen-038; crosswalk `screening/gastat_crosswalk.yaml`); the DataPulse relayed table (S-cp2-gastat-001) is a cross-check only, "never the value of record where a primary row exists"; keep citypopulation.de only for localities neither table covers; log a conflict where figures differ by more than 2 %. Grid-filled populations outside the matched cities are checked against each region's residual (control total A-screen-037; `control_total_flag`, reporting only). Below city level keep the WorldPop gap-fill under the gate, with "a third method: the 2010 cities > 5k list grown at the governorate's 2010→2022 ratio" (`pop_corroboration: gastat2010_city_growth`, value = pop_2010 × gov_2022 / gov_2010, A-screen-035), which "counts as one of the independent corroboration methods". The sensitivity uses the back-test median against the primary cities: ÷ 0.71 (A-screen-039; earlier ÷ 0.48, A-screen-036, and ÷ 0.64, A-screen-034). Lookups and the 2010 estimates: `screening.gastat` (`tables`, `apply`, then `primary`; `runs/gastat/apply/cities2010_growth.csv`).

## Procedure
1. Build the register with a script committed in the worktree under `screening/sweeps/<slug>/` (never `/tmp`): candidates from GASTAT tables (official), OSM `place=city|town|village` within the region polygon (ODbL) and GHSL/WorldPop grids for untabulated towns (licence checked first). Raw downloads go under `data/ksa/<slug>/raw/` (gitignored) and into `cities/ksa/sources.yaml` (`uv run python -m common.manifest add`) before anything is computed from them. Assumption ids are prefixed by the slug (`A-<slug>-001`).
2. Fill every distance field from the W1 network layers (`cities/ksa/lines/*.geojson`) and the road skims when available; until skims exist, straight-line distance with `road_min_* = null`, `dist_method: haversine` and a note.
3. Write the Parquet with the header keys `governorates_gastat` and `governorates_listed` (Parquet key-value metadata), the CSV mirror, and `docs/regions/<slug>.md`: version header; GASTAT governorate count vs listed; table of rows; exclusions with reasons; sources list; open questions. Label: "screening input, not a forecast".
4. Register every new parameter (thresholds, grid-population method) in the assumptions register; every dataset in the licence register and `cities/ksa/sources.yaml`.
5. Status block ends with the plain line `<LABEL>: done` or `<LABEL>: blocked - <reason>` at the start of a line (no backticks, bold, bullet or indentation).

## Acceptance
- `governorates_listed == governorates_gastat` for the region; every row with a population has `pop_source`.
- No row invented from memory: a town without a sourced population is kept with `population = null` and `pop_type = null`, not guessed.
- `uv run python -m screening.region_sweep validate cities/ksa/regions/<slug>.parquet` passes (rows against `RegionRow`, one region, no duplicate OSM ids, CSV mirror, header counts); `--strict` once GASTAT's count is readable (an unverified count is otherwise a warning).

## Geo-verify step (mandatory from 31 Oct 2026)
After the register is built, run `uv run --with rasterio python -m screening.geo_verify.cli estimate --which no-pop --region <slug> --seed 1` (and `--which secondary` for rows whose figure is only relayed) for every unlocated or unsourced row; for stations and planned stops, add the candidate site and its evidence to `screening/geo_verify/station_sites.yaml` and run `... stations --seed 1` (Sentinel-2 window, method log) before `--apply`. Follow `.claude/skills/geo-verify/SKILL.md` (two methods, back-test gate, bands, conflict rows, Google visual-only) and record the `A-geo-` parameters and method-log ids in `notes`. As of the GEO_VERIFY back-test (31 Oct 2026, `docs/geo-verify.md`) both estimators fail the 30 % gate, so their values go in `notes` only, never in `population`, until a re-test passes.
