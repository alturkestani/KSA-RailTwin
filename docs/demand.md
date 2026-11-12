> **Document version:** docs/demand.md v0.6 | 3 Nov 2026 | Author: INTEGRATE_R5 (register pointer repointed); R3 builder (demand-modeler); INTEGRATE_R3 (CP4-1a approvals in §8, register pointers); R5 (§12 H2a, H3a, H5) | Status: draft

# National demand model (W8, milestone R3)

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** The one exception is the single total marked `calibrated` in §8, and it holds only at the 2025 calibration point. Mode-choice coefficients are **literature-based until survey results exist**. Every figure below comes from a `runs/` output (the run id is given), a register row (`A-…`) or a source (`S-…`). This document uses "in the model, X …" throughout and never "X will …".

Contents: §1 what R3 delivers; §2 the CP3 pre-tasks (DEM terrain, skims for created rows, Badr's rank); §3 zones; §4 population inputs; §5 level of service; §6 gravity; §7 mode choice; §8 calibration; §9 outputs with run ids; §10 how to reproduce; §11 limits and items for R4/CP4.

## 1. What R3 delivers
| item | file / run | state |
|---|---|---|
| Zones | `cities/ksa/zones/zones.geojson`; `runs/zones/` | 423 zones: 136 governorate zones plus 287 hex zones inside 13 metro governorates (§3) |
| Population scenarios to 2060 | `cities/ksa/population/scenarios/*.yaml`; `docs/population-scenarios.md` | 9 scenario files plus the giga add-on file |
| Gravity by purpose plus mode split | `demand/gravity.py`; `runs/demand/<id>/od_<purpose>.parquet` | 5 purposes; freight: no open freight OD found (`freight.json`) |
| Mode choice (MNL car/rail/air/bus) | `modechoice/`; `docs/mode-choice.md` | coefficients from `mode_choice_priors.yaml`; sweep reported there |
| Calibration | `demand/calibrate.py`; `runs/demand/calibration-s1/` | 1 total calibrated (SAR East + North rail); air and bus `uncalibrated` (§8) |
| CP3 pre-tasks | `demand/terrain.py`, `demand/register_skims.py`, `demand/register_update.py`, `demand/badr.py` | done (§2) |

## 2. CP3 pre-tasks (Tariq's CP3 decision 8)
These three come first because they change the register the demand model reads.

### 2.1 Terrain from an open DEM
- **Data.** Copernicus DEM GLO-30, public COGs on AWS Open Data. Only windowed reads were made, 1,224 windows totalling 591,108,389 bytes, with no sign-up (S-r3-dem-001…006; licence row "Copernicus DEM GLO-30 [r3]"). Free disk was 50 GiB before and 49 GiB after; the gate is 15 GiB.
- **Classification rule.** The rule is in `cities/ksa/assumptions/demand_terrain.yaml`, A-geo-011…022, and is applied in order, first match wins (A-geo-021):
  1. escarpment_mountain;
  2. sabkha;
  3. coastal, using OSM `natural=coastline`;
  4. dunes;
  5. mixed;
  6. flat_desert.
- **What was measured.** Slope, relief and roughness inside a disc around each register point. The disc radius is 0.02 × √population km, clamped to 5–15 km (A-geo-011/012). The known weaknesses are listed in `docs/assumptions.md`:
  - the DEM is a surface model, so buildings add relief;
  - dunes and sabkha are signatures only (all 9 dune and 13 sabkha rows are flagged);
  - big cities are sensitive to the disc radius.
- **Coverage.** The DEM class replaced `terrain_class` on every register row (`uv run python -m demand.register_update apply`): 294 empty classes filled, 311 changed, 619 unchanged (`runs/r3/register_update/summary.json`, `terrain_changes.csv`).
- **Long-list count.** The long list holds 104 rows without a terrain class, not the 95 the CP3 note gave. The 95 came from an earlier long list (`runs/r3/terrain/summary_longlist-missing.json`).
- **Reproducibility.** A re-run from committed code (`runs/r3/terrain-rerun/`) gives an identical sidecar.

Effect on the short list. Compare `runs/r3/funnel-before/` with `runs/r3/funnel-after/`; both use seed 1 and the same weights.

- **Rank changes.** 192 of the 198 long-list ranks change, by at most 63 places. The short-list size stays at 60, and the top 30 overlap is 24 of 30.
- **Cause.** The terrain change explains every short-list move. Re-scoring with only the skims fill changes 0 ranks: the funnel scores on straight-line distances.
- **12 towns leave the short list.** Most are escarpment towns that had been median-filled as flat:
  - Asir: An-Nimas, Al Majaridah, Muhayil, Bahr Abu Sukaynah, Zahran al-Janub, Sarat Abidah, Tanumah;
  - Makkah: Al Jumum, Al Kamil;
  - Eastern: Ra's Tannurah, Al Khafji (both now sabkha);
  - Riyadh: Al Hariq.
- **12 towns enter.** Fir'ah Tarib, Al Jarn, Al Jishshah, Dhahran, Alkalabiuh, Samitah, Yanbu Industrial City, Sharurah, Rafha, Al Bada'i, Haql, Tayma. Rafha, Sharurah and Tayma enter because the DEM finds flat ground where the regional defaults had said dunes or mixed.
- **CP4 decision.** The ordering "sabkha before coastal" (A-geo-021) moves 13 low coastal towns from penalty 0 to −0.5.

### 2.2 Road skims for the created rows
All 28 register rows without road fields now have them; no road NaN is left (`runs/r3/skims_created/`, `uv run python -m demand.register_skims run`). They are 23 rows created at the merges, one more `pending skims` row, Yanbu Industrial City, Al Harth, Al Qara and Wadi al-Fara'.

- Three of the rows (Al Qara, Wadi al-Fara', makkah:relation:12429530) are polygon points, not located town centres, so their values are indicative only.
- Check against existing values: 3 rows that already had skims were recomputed, and all 9 road times match to 0.0 min.
- Re-run from committed code (`runs/r3/skims_created-rerun/`): identical.

### 2.3 Badr's rank (#3 in the R2 short list)
Run `runs/r3/badr/explain.json` (`uv run python -m demand.badr explain --seed 1`); the base ranks match the funnel runs exactly. Badr Hunayn (بدر, Badr governorate, Madinah region; row `madinah:node:1237968680`):

**Criterion values and weighted contributions (base weights).**

| criterion (weight) | value | contribution | long-list median | driver |
|---|---|---|---|---|
| population (0.30) | 0.7275 | 0.2182 | 0.6913 | 30,494 persons (S-cp2-gastat-008), close to the median |
| rail gap (0.20) | 0.8405 | 0.1681 | 0.9015 | 120.1 km from HHR Madinah station; below the median |
| commute (0.20) | 0.899 | 0.1798 | 0.0 | Madinah (tier 1) is 113.3 km away by straight line, inside the 40–120 km band (A-screen-005), so it scores tier factor 1.0 × log(Madinah pop) / log(Riyadh pop). Only 36.9 % of the long list scores above 0 here; Badr is 28th on this criterion. By road it is 115.4 min to Madinah |
| economic roles (0.20) | 0.6667 | 0.1333 | 0.0 | heritage and tourism (S-madinah-010) |
| terrain (0.10) | before DEM: 1.0 (median fill, no class); after DEM: 0.0 (escarpment_mountain) | 0.1 → 0.0 | 1.0 | DEM: steepest-10 % slope 21.5°, relief 205 m (`cities/ksa/zones/terrain_dem.parquet`); escarpment at every disc radius from 2 to 6 km |

**Rank across the sweep and sensitivities.**

| case | before DEM (R2 register) | after DEM (R3 register) |
|---|---|---|
| base rank | 3 | 14 |
| 10 sweep corners (A-screen-029): range | 3–5 | 10–18 |
| 5k threshold sensitivity | 3 (range 3–5) | 15 (10–19) |
| linear rail gap sensitivity | 5 (4–7) | 22 (15–29) |
| committed-layer sensitivity | 3 (3–5) | 14 (10–18) |
| commute tier factors (A-screen-026) ×0.75: tier 1 / tier 2 / tier 3 / all | 5 / 3 / 3 / 5 | 19 / 14 / 14 / 18 |
| commute tier factors ×1.25: tier 1 / tier 2 / tier 3 / all | 3 / 3 / 3 / 3 | 10 / 15 / 14 / 11 |
| band 40–120 km shifted ×0.75 (30–90 km) | 38 | 82 |
| band shifted ×1.25 (50–150 km) | 7 | 19 |
| band widened (30–150 km) | 7 | 20 |
| band narrowed (50–90 km) | 35 | 70 |
| commute criterion removed (weight 0, others renormalised) | 22 | 53 |

**Answer.** Badr's #3 rank came from the commute criterion's design, plus a data gap, and not from a strong position in the data.

- **The data gap.** Badr had no terrain class, so the median fill scored it as flat (terrain 1.0). The DEM reads escarpment (0.0), and that alone drops it from #3 to #14.
- **The criterion design.** Badr sits 113 km straight-line from Madinah, inside the upper edge of the 40–120 km band. In the real geography that is about 115 min by road, far from a 30-minute commute. Two tests show how much rests on this:
  - with the band at 30–90 km or 50–90 km, Badr scores 0 on commute and falls to #70–82;
  - without the commute criterion at all, it ranks #53.
- **What holds up.** Badr is a mid-sized town (30,494) with two sourced roles and a moderate rail gap.
- **Under the stated tests.** It stays on the short list (top 60) under every sweep corner and every tier-factor variant tested. It drops off only when the band's upper edge falls below 113 km.
- **Recommendation for CP4.** Measure the commute criterion on road or rail time rather than straight-line distance; this is the R4 isochrone work.

## 3. Zones (`uv run python -m demand.zones build --seed 1 --out runs/zones/`)
- **National.** One zone per OSM governorate polygon: 149 polygons, with GASTAT's Al Amoah merged into Tathlith (A-pop-007). Population is the GASTAT Census 2022 TA1 governorate table (S-cp2-gastat-007; `cities/ksa/population/base_2022_governorates.csv`). The zone point is the governorate's most populous settlement (A-demand-041).
- **Metros (CP1 list, A-screen-013).** The 13 governorates that hold a metro anchor row (11 metros, 14 anchor rows) are replaced by 10 km hexagons (A-demand-001):
  - Riyadh;
  - Jeddah;
  - Makkah;
  - Al Madinah;
  - Dammam and Khobar;
  - Taif;
  - Buraydah;
  - Tabuk;
  - Abha and Khamis Mushayt;
  - Jazan;
  - Najran.
- **Hex population.** The census governorate total is split by WorldPop 2020 constrained 100 m grid shares. Only shares are used, because WorldPop under-counts against the census (median 0.637, `docs/network.md`). Hexes under 3,000 grid persons merge into the nearest kept hex (A-demand-042). Each hex's point is the population-weighted pixel centroid (A-demand-043).
- **Result.** 423 zones, of which 287 are hexes. Zone populations sum to 32,175,224, exactly the census total (`runs/zones/summary.json`). Hex counts per metro range from 4 (Jazan) to 45 (Abha–Khamis Mushait).
- **Jobs proxy.** GASTAT administrative records, 2025 Q4 (social-insurance participants plus civil servants; 14,836,997 jobs; S-r3-cal-050, grade B), distributed by population within each region (A-demand-003). This is a flagged proxy: Riyadh holds 49.2 % of these jobs but 26.7 % of the population, and head-office registration may explain part of that (`cities/ksa/assumptions/demand_jobs.yaml`).
- **Economic nodes.** 136 located nodes are attached to zones: the zone that contains them, or the nearest zone for 10 offshore or border points (A-demand-044). Counts per role are stored per zone.
- **Licences.** The zone geometry is a derived database of OpenStreetMap, (c) OpenStreetMap contributors, ODbL 1.0. Hex shares come from WorldPop (CC BY 4.0).

## 4. Population inputs
The full method and every figure are in `docs/population-scenarios.md`. The model runs use:
- `baseline` (Census 2022, no growth);
- `un_wpp_medium_gastat2024` (the calibration point, 2025; A-pop-003);
- UN WPP 2024 `un_wpp_low` / `medium` / `high` for 2040, 2050 and 2060 (S-r3-pop-001, census-anchored, A-pop-001);
- `vision2030_policy` for 2030, a labelled policy scenario rather than a forecast;
- the giga-project add-on on WPP Medium 2050 at delivered shares P10/P50/P90 and at the announced figures (A-demand-030, reallocate mode A-pop-013).

Governorate totals are projected by `demand.population.project` with census shares held (A-pop-005). Hexes keep their 2022 within-governorate shares.

## 5. Level of service (`uv run python -m demand.supply skims --seed 1 --out runs/skims/r3-zones/`)
**Road skims.** OSRM /table with the national MLD files, car profile, free flow (OSRM v26.10.0). It covers 423 × 423 zone pairs (178,929 pairs, 0 unreachable), plus zone ↔ 20 stations and zone ↔ 27 airports. The run takes about 5 s (4.8–5.1 s over the runs, `runs/skims/r3-zones/summary.json`). The largest zone-to-road snap is 9.7 km, from a desert or island point. Road times are uncongested and not calibrated.

**Car and bus.** Taken from `mode_choice_r3.yaml` (fuel cost, occupancy; bus at 1.15 × road minutes, SAR 0.20 per km, 240 min headway, available from 50 km).

**Rail (S0: HHR, SAR East, SAR North; S1 adds the Landbridge, committed and announced/planned).**
- Access is to the nearest station of each line within 90 min by road (A-demand-045), plus 10 min terminal time per side (A-demand-046).
- In-vehicle time is km-post span divided by the line's average speed, taken from its longest published pair (A-demand-047).
- Fares are per km (A-demand-048), headways per line (A-mode-041, A-demand-049), on-time from S-014 and S-r3-mode-001.
- No transfers: each OD pair uses its best single line. R4's running-time model replaces this.

**Air.**
- Access is to the nearest airport within 150 min (A-demand-050).
- Routes are those listed in `mode_choice_r3.yaml` plus every airport to RUH, JED and DMM (A-demand-051). Unlisted hub routes get a 480 min headway (A-demand-052).
- Block time and fare follow A-mode-029/030, processing time per side follows A-mode-028.

## 6. Gravity (`uv run python -m demand.gravity run --scenario S0 --population baseline --seed 1 --out runs/demand/S0-baseline-s1/`)
**Generation.** Productions are trip rate × zone population. The one-way intercity trips per resident per year are (`demand_generation.yaml`):

| purpose | rate | range | assumption |
|---|---|---|---|
| commute | 0.5 | 0.1–2.0 | A-demand-015 |
| business | 0.977 | 0.571–1.586 | A-demand-014 |
| leisure/VFR | 2.564 | 1.692–4.625 | A-demand-013 |
| tourism | 2.403 | 1.802–3.468 | A-demand-012 |

These rates are anchored on Ministry of Tourism domestic overnight trips (S-soc-032, secondary) and expanded by registered day-trip multipliers.

**Pilgrimage.** Fixed external totals by origin region for 2025:
- internal Umrah: 25,055,083 (S-soc-029);
- Madinah religious visits: 7,840,577 (S-r3-cal-041…044);
- internal Hajj: 166,654 (S-soc-028).

Each total is split to zones by population within the region and sent to the zone that holds Masjid al-Haram or Al-Masjid an-Nabawi, out and back (A-demand-006, -016…-019). Origins in the destination governorate are dropped. Other years scale with population (A-demand-057).

**Distribution.**
- An intercity trip needs at least 40 road km between zones (A-demand-005); commute is restricted to 40–120 road km (A-demand-055).
- Business, leisure/VFR and tourism are doubly constrained and Furness-balanced to a relative error below 1e-4. Run S0-baseline-s1 needed 14, 23 and 15 iterations, with a maximum error of 9.7e-5.
- **Commute is origin-constrained (A-demand-058), a stated departure from the skill.** With the band, the doubly-constrained problem has no solution: Furness reached a maximum relative error of 1.0 after 500 iterations. In S0-baseline-s1, commute productions of 968,797 trips a year have no zone in band and are reported as lost.
- Attractions: jobs for commute and business; population for leisure/VFR; for tourism, population × (1 + 0.25 × the count of tourism, heritage, Hajj/Umrah and giga nodes in the zone) (A-demand-054).

**Impedance.** The cost is composite generalised minutes, −logsum / |b_ivt_car| of the purpose's MNL (A-demand-056). It takes an exponential form for commute (β 0.05 per min, S-r3-cal-032) and power forms for business, leisure/VFR and tourism (γ 1.5, 1.9 and 1.5; S-r3-cal-035; A-demand-021…025). Impedances are computed in log space with per-row scaling, which leaves the solution unchanged.

**PA to OD.** OD = ½ (PA + PAᵀ) for the four distributed purposes (A-demand-060). This keeps the totals and makes station and airport counts directional.

**Freight.** No open freight OD was found. `freight.json` lists what exists: GASTAT rail freight totals by line, and port throughput totals without an inland OD.

**Determinism.** Re-running the same command into `runs/r3/determinism/S0-baseline-s1-rerun/` gives byte-identical `od_*.parquet` for all five purposes (SHA-256 in `totals.json`: commute `29ab5cf5…`, business `db205f1c…`, leisure/VFR `26e4cea0…`, tourism `3b20ae7d…`, pilgrimage `b3376c14…`). The run also gives the same config hash (`e58ff5e8f804…`) and data hash (`b611a722fc22…`, the manifest after this track's last register edit; all runs re-made from code version `r2-int-13-ga245981`). On `main`, INTEGRATE_R3 (1 Nov 2026) re-ran `./demand/run_r3.sh 1` from the merged tree: the five OD SHA-256 values above, the calibration and the run summary are unchanged; the `meta.json` files now record data hash `773494feadc0…` (the manifest after the integration edits) and code version `r2-int-20-g0427c91`. `runs/r3/determinism/` was not re-run. Every `meta.json` records seed, config hash, manifest hash, code version and the run identity.

## 7. Mode choice
The MNL over car, rail, air and bus is in `modechoice/`, with car as the reference. Its coefficients come from `cities/ksa/assumptions/mode_choice_priors.yaml` (A-mode-001…012, each with its source). Purpose enters by scaling the cost coefficient with value-of-time ratios (A-mode-021). The summer first/last-mile penalty is a variant (A-mode-026/027). The full specification, the coefficient table and the coefficient sweep (59 variants × 80 rows; no monotonicity failures) are in `docs/mode-choice.md` (runs `runs/r3/modechoice/`).

## 8. Calibration (`uv run python -m demand.calibrate run --seed 1 --out runs/demand/calibration-s1/`)
**Calibration point.** 2025, S0 line set, population `un_wpp_medium_gastat2024` (35,927,621 persons), because the trip rates were set per resident of the GASTAT 2024 estimate.

**What may be adjusted.** Only the registered calibration parameters asc.rail, asc.air and asc.bus (`mode_choice_r3.yaml` calibration_hook), inside the priors' ranges (A-mode-010…012). The fit is least squares on log(modelled / observed) over three national targets; the optimiser stopped on its ftol condition after 8 evaluations. Every evaluation is logged in `adjustments_log.csv`.

**Pass rule.** A target passes when |modelled / observed − 1| ≤ its tolerance (A-demand-036). The tolerances are:
- ±15 % for grade A totals (TAG M3.2 Table 4, A-demand-032);
- ±25 % for stations and airports (A-demand-033; trip ends under 100,000 a year are reported, not failed);
- ±5 % for mean trip length (A-demand-034);
- ±25 % for grade B (A-demand-035).

GEH is reported on daily flows and is never the pass test. **Only a fitted target that passes is `calibrated`.** A target within tolerance that was not fitted is "within tolerance (validation, not fitted)".

**Rail scope (A-demand-059).** The HHR total includes international visitors (foreign Umrah performers arriving by air), whom this resident-demand model does not generate. GASTAT gives no split by nationality or residence. The rail constant is therefore fitted to SAR East + SAR North passengers only, and HHR is reported, not fitted.

| fit target (2025) | observed | source | before (prior constants) | after | tolerance | status |
|---|---|---|---|---|---|---|
| SAR East + SAR North rail passengers | 2,409,259 | S-r3-cal-001 (A) | +69.8 % | 2,461,593 (**+2.2 %**) | ±15 % | **calibrated** (approved: Tariq, 31 Oct 2026, CP4-1a) |
| domestic air departures | 32,031,852 | S-r3-cal-010 (A) | −60.3 % | 21,659,266 (−32.4 %) | ±15 % | uncalibrated (kept into R4 for recalibration, CP4-1a) |
| intercity bus Q2–Q4 | 2,747,000 | S-r3-cal-020…022 (B) | +687 % | 9,297,555 (+238.5 %; annual × 0.75, A-demand-053) | ±25 % | uncalibrated (kept into R4 for recalibration, CP4-1a) |

**Adjustments** (`calibration.json`):
- asc.rail: −0.20 → **−0.798**, inside the range [−1.0, 0.5];
- asc.air: −0.20 → **+0.50**, at its upper bound;
- asc.bus: −0.60 → **−1.50**, at its lower bound.

**Why air and bus stay uncalibrated.** Their constants would have to leave their registered ranges. A diagnostic fit without the ranges, which is not adopted, needs asc.air +1.18 and asc.bus −2.71 to match both totals.

Possible reasons the model misses (not tested here):
- the hub-only air network (A-demand-051);
- the generous bus availability rule, every pair over 50 km at a 240 min headway;
- the TGA bus count's scope, which may leave out non-scheduled and Umrah coach operators (TGA bulletins not read, S-r3-cal-020).

**Validation (not fitted), after calibration** (`targets_table.csv`, 105 rows):
- **Rail lines.**
  - SAR East: +46.8 % passengers, +25.9 % passenger-km, −14.2 % mean trip length.
  - SAR North: −69.2 % passengers, −62.8 % passenger-km, +20.8 % mean trip length. One rail constant cannot split East from North, and the North line's 540 min headway lies outside the literature range of the headway coefficient (`docs/mode-choice.md`).
  - HHR: −24.2 % passengers, −71.0 % passenger-km, −61.8 % mean trip length. In the model HHR carries mostly short Makkah–Jeddah trips, while observed HHR use is dominated by Madinah (station departures −84.2 %), which fits the scope note above.
- **Stations.** 3 of the 30 station figures (15 stations × departures and arrivals) are within tolerance: Makkah departures and arrivals, and Jeddah Airport arrivals. 10 trip-end figures are low-flow exempt; the rest are outside.
- **Airports.** 10 of the airport figures are within tolerance (MED, TUU, AJF, RAE, YNB departures and arrivals). The large airports are all under: RUH departures −34.4 %, JED −39.6 %, DMM −29.9 %, AHB −72.1 %.
- **Available but unverified, never fitted.** TGA/Argaam rail 2025 (11.7 M), the total rail including intracity (156.4 M) and the domestic air total including general aviation.

**What is calibrated: exactly one total,** SAR East + SAR North rail passengers in 2025. Nothing else is calibrated: not air, not bus, not HHR, and not any per-line, per-station or per-airport figure. All outputs keep the label **"synthetic demand, uncalibrated: scenario comparison, not a forecast"**.

## 9. Outputs with run ids (seed 1; `runs/demand/summary-s1/summary.csv`, `pairs.csv`)
Annual one-way person trips, millions. Runs other than S0-baseline-s1 use the fitted constants from `runs/demand/calibration-s1/calibration.json`.

| run id | population (M) | commute | business | leisure/VFR | tourism | pilgrimage | car | rail | air | bus |
|---|---|---|---|---|---|---|---|---|---|---|
| S0-baseline-s1 (Census 2022, prior constants) | 32.18 | 15.12 | 31.44 | 82.50 | 77.32 | 53.08 | 209.05 | 13.18 | 11.40 | 25.82 |
| S0-un_wpp_medium_gastat2024-2025-base-s1 (calibration point) | 35.93 | 16.88 | 35.10 | 92.12 | 86.33 | 59.27 | 246.72 | 8.93 | 21.66 | 12.40 |
| S0-…-2025-low-s1 (trip rates at range low ends) | 35.93 | 3.38 | 20.51 | 60.79 | 64.74 | 59.27 | 176.92 | 6.42 | 16.34 | 9.01 |
| S0-…-2025-high-s1 (range high ends) | 35.93 | 67.53 | 56.98 | 166.17 | 124.60 | 59.27 | 408.86 | 14.70 | 31.14 | 19.85 |
| S0-un_wpp_low-2050-base-s1 | 44.31 | 20.82 | 43.30 | 113.62 | 106.49 | 73.10 | 304.31 | 11.01 | 26.72 | 15.29 |
| S0-un_wpp_medium-2050-base-s1 | 47.69 | 22.41 | 46.60 | 122.29 | 114.61 | 78.68 | 327.52 | 11.85 | 28.75 | 16.46 |
| S0-un_wpp_high-2050-base-s1 | 51.09 | 24.01 | 49.92 | 131.00 | 122.77 | 84.28 | 350.86 | 12.70 | 30.80 | 17.63 |
| S0-un_wpp_medium-2060-base-s1 | 52.68 | 24.75 | 51.47 | 135.07 | 126.59 | 86.90 | 361.75 | 13.09 | 31.76 | 18.18 |
| S0-vision2030_policy-2030-base-s1 (policy scenario) | 50.00 | 23.65 | 48.85 | 128.20 | 120.15 | 82.48 | 341.70 | 11.79 | 33.37 | 16.48 |
| S0-un_wpp_medium-2050-giga_p50-s1 | 47.69 | 22.36 | 46.60 | 122.29 | 114.61 | 78.69 | 327.79 | 11.75 | 28.50 | 16.50 |
| S0-un_wpp_medium-2050-giga_announced-s1 | 47.69 | 18.16 | 46.60 | 122.29 | 114.61 | 78.71 | 313.47 | 8.57 | 41.27 | 17.05 |

`summary.csv` holds the 2040 and 2060 rows, the giga P10/P90 rows and every S1 run.

**Reading the table.**
- **Trip-rate band.** At the 2025 calibration point, moving every trip rate to its range ends gives a band of 6.42–14.70 M rail trips around the central 8.93 M. That is the generation uncertainty, which the calibration does not narrow: car has no observed target, so generation and the mode constants cannot be told apart (`demand_generation.yaml` calibration note).
- **Giga add-on.** At P50 delivered shares the add-on moves few people (A-demand-030). At the announced figures it moves 9.7 M residents into the host zones, taken pro rata from everyone else, so commute and rail fall and air rises. This is a scenario comparison, not an expectation.

**Matched pairs, S1 − S0** (Landbridge, committed; same zones, seed, population, rates and constants; rule 6; `pairs.csv`, 17 pairs).
- At the 2025 point: rail +2.69 M (8.93 → 11.62 M; the Landbridge carries 4.40 M), car −1.87 M, air −0.71 M, bus −0.11 M.
- HHR falls by 1.70 M in the model. Of the 4.40 M Landbridge trips, 1.71 M are Jeddah ↔ Al-Jumum hops that the best-single-line rule takes from HHR, with Al-Jumum an unlocated proxy station. Riyadh ↔ Al-Jumum is 1.57 M; Riyadh ↔ Jeddah is 0.45 M.
- This is an R3 artifact to fix in R4, when there is a rail graph with transfers and located stations. **Do not read it as a Landbridge result.**

## 10. Reproduce
`./demand/run_r3.sh 1` runs the whole chain in about 2.6–2.7 min (last full run on the track 31 Oct 2026, code version `r2-int-13-ga245981`; re-run on `main` by INTEGRATE_R3 on 1 Nov 2026, code version `r2-int-20-g0427c91`, about 3 min): zones, skims, the baseline gravity run, calibration, the 34 scenario runs and the summary. Before it, run `./demand/run_register_r3.sh 1 before|after` and `uv run python -m demand.badr explain --seed 1` (§2). Tests: `uv run pytest tests/test_demand_*.py tests/test_modechoice_*.py` gives 80 tests in 1.9 s, including on the 6-zone fixture:
- gravity row and column sums;
- bit-for-bit determinism;
- MNL shares summing to 1;
- monotonic responses;
- the calibration pass rule.

## 11. Limits and items carried forward
- **R4 network items.**
  - Rail is single-line with no transfers and fixed average speeds. This produces the Landbridge/HHR artifact in §9 and the East/North split error in §8.
  - Rail station access is a road-time cap.
  - Air uses a hub-only network.
  - Commute should be measured on road or rail time rather than straight-line distance (§2.3).
  - The two S5 Jubail station additions remain open.
- **International visitors (HHR, Makkah/Madinah airports)** are not modelled. An external visitor segment needs foreign Umrah arrivals by port of entry, and no such table is in the repo (A-demand-059).
- **Air and bus constants** are outside their ranges at calibration (CP4 decision).
- **Jobs proxy.** Riyadh's job share is probably inflated by head-office registration (CP4: the population-share or 50/50 sensitivity; `demand_jobs.yaml`).
- **Created rows.** 24 created register rows still carry no sourced economic roles (INTEGRATE_R2 open issue).
- **Freight.** No open freight OD was found.
- **Corridor YAMLs.** These were not regenerated with the DEM terrain. Corridor terrain shares still use the A-corr-013 proxy from register rows; the register rows are now DEM classes, but `screening.corridors generate` was not re-run (screening owns it; R4 hand-off).

## 12. R5 recalibration (CP5 decisions H2a, H3a, H5; 3 Nov 2026)

**Synthetic demand, uncalibrated: scenario comparison, not a forecast** — except the totals marked `calibrated` below, at the 2025 calibration point only.

Run: `uv run python -m demand.calibrate run --network r4 --seed 1 --out runs/r5/demand/calibration-r5-s1/` (R4 rail graph, air pairs and bus nodes; population un_wpp_medium_gastat2024, 2025), then `uv run python -m demand.intl_fit fit --seed 1 --out runs/r5/demand/intl-fit-s1/`.

**H2a, domestic air.** A-mode-011 (ASC air) range widened from [−1.0, 0.5] to [−1.0, 1.5] on 3 Nov 2026, decision H2a (Tariq), reason "KSA air constants not transferable from the literature prior" (`cities/ksa/assumptions/mode_choice_priors.yaml` v0.2; register update in `docs/assumptions.md`). Re-fit (`runs/r5/demand/calibration-r5-s1/calibration.json`):

| constant | R4 fit (range) | R5 fit (range) | at bound? |
|---|---|---|---|
| asc.rail (A-mode-010) | −0.826 ([−1.0, 0.5]) | −0.775 ([−1.0, 0.5]) | no |
| asc.air (A-mode-011) | +0.500 ([−1.0, 0.5], at bound) | **+1.192** ([−1.0, 1.5]) | no |
| asc.bus (A-mode-012) | −1.495 ([−1.5, 0.0]) | −1.415 ([−1.5, 0.0]) | no |

| fitted target (observed) | R4 deviation | R5 deviation | R5 status |
|---|---|---|---|
| SAR East + SAR North passengers 2025 (2,409,259) | −1.4 % | 0.0 % | calibrated |
| domestic air departures 2025 (32,031,852) | −29.9 % | **0.0 %** | **calibrated** (inside the widened range) |
| intercity bus Q2–Q4 2025 (2,747,000) | −0.7 % | 0.0 % | calibrated |

The unbounded diagnostic of R4 (+1.19) now lies inside the range, so the bounded and unbounded fits coincide. Air stays "coefficients literature-based until survey results exist" for everything except this constant.

**H3a, international rail share fitted.** The international segment (`demand.intl`, A-intl-003) puts a share s of every foreign-visitor leg with a rail path on rail. HHR riders are resident trips plus s × the international legs on HHR, linear in s, so the exact fit is s* = (observed − resident) / (legs at s = 1) (`demand/intl_fit.py`, test `tests/test_demand_intl_fit_r5.py`):

| quantity | value |
|---|---|
| HHR 2025 observed (rail-hhr-pax-2025, grade A) | 8,529,112 |
| HHR resident trips, R5 calibration run (S0) | 6,992,226 (−18.0 % without the segment) |
| international HHR legs at s = 1 | 53,721,366 |
| **fitted share s\*** (`calibrated`) | **0.0286** (prior central 0.176, range 0.026–0.470: inside the range) |
| HHR with the segment | 8,529,112 (0.0 %, by construction) |

**The HHR 2025 total is now a calibration target, not independent validation.** `cities/ksa/population/intl_segment.yaml` v1.1 carries the fitted value (`status: calibrated`). The replacement validation check, which the fit does not use, is the **HHR Ramadan month profile** (A-intl-008): the modelled HHR Ramadan factor (Ramadan month ÷ mean month) against the GASTAT 2025 monthly HHR series (March 2025 = Ramadan 1446; `data/ksa/calibration/gastat_rail_tables_2025/railway_tables_2025_en.xlsx` sheet 1-2), tolerance ±15 % (A-intl-009, by analogy with A-demand-032):

| check | observed | modelled | deviation | result |
|---|---|---|---|---|
| HHR Ramadan factor, 2025 | 1.486 | 1.128 | −24.0 % | **FAIL** (outside ±15 %) |

Reason: resident demand carries no monthly profile in this model (every resident purpose is an annual average), so the modelled Ramadan peak comes from the international segment alone, which carries 18 % of HHR riders after the fit. Domestic Umrah and Ramadan travel by residents are therefore under-represented in the peak; the annual total is unaffected. The R4 central share (0.176) gave a Ramadan factor of 1.42 but overshot the annual total by +89.9 %. Other checks of the same run: intercity rail 2025 total (validation, not fitted) −14.1 % without the segment; KAIA station departures −41.7 % (international scope, A-demand-059).

**H5, Q2 2025 Umrah release.** The most recent official dated release is `Umrah Statistics Q2 2025 EN.pdf` (GASTAT, PDF created 9 Aug 2026, upload stamp t=1786339722854; workbook Table 1.10 modified 6 Aug 2026): 1,405,116 external performers (S-r5-h5-001). The earlier file `Umrah Statistics for Q2 - 2025 - EN.pdf` (created 19 Nov 2025) gives 1,324,418 (S-r5-h5-002, sensitivity only). The dates are unambiguous, so the later file is the revision and C-r4-intl-002 is closed (`docs/sources/conflicts.md`). The value of record was already 1,405,116 in R4, so no R4 output changes.
