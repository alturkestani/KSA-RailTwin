> **Document version:** docs/report/sections/03-methods.md v1.0 | 4 Nov 2026 | Author: report-writer | Status: draft

# 3. Methods, standards and departures

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

Each step names the standard it follows and states where it departs. The full method notes are the workstream documents named in each subsection; this section summarises them and does not add figures of its own.

## 3.1 Data

- **Rail layers** from OpenStreetMap (ODbL) and published operator facts, with committed lines digitised as "announced/planned" with source and date (`docs/data-sources.md`, `docs/network.md`; for example the Haramain line facts[^S-002]).
- **Settlements and population:** GASTAT Census 2022 governorate totals and the table of cities of 5,000 or more (primary exports[^S-cp2-gastat-007][^S-cp2-gastat-008]); open population grids for towns GASTAT does not tabulate (WorldPop[^S-r1a-505], GHSL[^S-r1a-509]), scaled to the governorate control totals (A-screen-040).
- **Population to 2060:** UN World Population Prospects 2024 low / medium / high[^S-r3-pop-001] (`docs/population-scenarios.md`).
- **Terrain:** Copernicus GLO-30, routed at about 90 m (`docs/alignments.md` §2; licence register `docs/licences.md`).
- **Every dataset** is a row of the manifest `cities/ksa/sources.yaml` with its SHA-256; every run records the manifest hash in its `meta.json`. No Google, TomTom or HERE traffic and no imagery crops are used.

**Departure.** No open national household travel survey, origin–destination matrix, freight OD or road count series was found, so demand is synthetic (§3.3) and freight is not monetised (A-cba-309).

## 3.2 Screening (W2)

The funnel follows the `screening-funnel` method with criteria, weights and thresholds approved at CP1: population at or above 10,000 or a sourced economic role, governorate centres always in (A-screen-001, A-screen-003); towns within 10 km of an existing station go to a served bucket for station additions (A-screen-004); the short list is the top 60 by a weighted score with a ±25 % one-at-a-time weight sweep (A-screen-006, A-screen-029). Corridor families are generated from the short list by rule, never from a hand-picked list (`docs/candidates.md` §4).

<!-- gen:screening -->
| region | GASTAT governorates | register settlements | long list | short list |
|---|---|---|---|---|
| Riyadh | 23 | 705 | 30 | 14 |
| Makkah | 17 | 77 | 20 | 9 |
| Madinah | 9 | 22 | 10 | 5 |
| Qassim | 13 | 37 | 15 | 2 |
| Eastern Province | 12 | 75 | 36 | 8 |
| Asir | 18 | 37 | 20 | 10 |
| Tabuk | 7 | 55 | 8 | 4 |
| Hail | 9 | 17 | 11 | 1 |
| Northern Borders | 4 | 57 | 5 | 1 |
| Jazan | 17 | 51 | 19 | 4 |
| Najran | 7 | 13 | 9 | 1 |
| Al-Baha | 10 | 16 | 10 | 0 |
| Al-Jouf | 4 | 62 | 5 | 1 |
| **total** | **150** | **1,224** | **198** | **60** |
Runs: runs/r2/long-list/longlist.parquet, runs/r2/score/ranks.parquet (short list = the top 60 by base score, A-screen-006; seed 1); register cities/ksa/candidates.parquet; governorates from docs/coverage.md (GASTAT Census 2022[^S-cp2-gastat-007]).
<!-- /gen:screening -->

Rank stability: 23 of the top 30 stay in the top 30 at every sweep corner; Kendall's tau between the base ranking and the corners is at least 0.93 (runs/r2/score/summary.json). **Departure:** the score ranks towns for further study; it is not demand, cost or benefit.

<!-- gen:fig-fig02-screening-funnel -->
![Figure 2. Screening funnel: settlement universe to CP7 programme layouts](figures/fig02-screening-funnel.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 2.* Log-scale bars of the count at each stage: settlement universe, candidate register, long list, short list, corridor candidates by family, corridor CBA cases and the three CP7 layouts.
Source: cities/ksa/zones/settlements.parquet; cities/ksa/candidates.parquet; runs/r2/score/summary.json; cities/ksa/corridors; runs/cba; runs/r6/top5/top5.csv. Provenance: R2 screening runs/r2 (code r2-6-g811202e) · seed 1 · registers cities/ksa (lines, zones, corridors) · R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1 · judge v3 d9fef643… · seed 1.
<!-- /gen:fig-fig02-screening-funnel -->

<!-- gen:fig-fig03-coverage-by-region -->
![Figure 3. Coverage: every region screened](figures/fig03-coverage-by-region.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 3.* For each of the 13 regions: register rows screened, long list and short list (symmetric log scale), with the number of governorates in the label.
Source: runs/r2/long-list/counts.json; runs/r2/score/scores.parquet; docs/coverage.md; cities/ksa/zones/regions.geojson. Provenance: R2 screening runs/r2 (code r2-6-g811202e) · seed 1 · registers cities/ksa (lines, zones, corridors).
<!-- /gen:fig-fig03-coverage-by-region -->

## 3.3 Demand and mode choice (W8)

- **Zones:** 423 zones, governorate zones plus hexagons inside the metro governorates (runs/zones/; `docs/demand.md` §3).
- **Trip distribution:** a doubly constrained gravity model by purpose (commute, business, leisure and visiting friends and relatives, pilgrimage, tourism), `docs/demand.md` §6.
- **Mode choice:** a multinomial logit across car, rail, air and bus with literature coefficients (`docs/mode-choice.md`), the summer first/last-mile factor (A-access-011) and car peak factor (A-access-012). Coefficients are "literature-based until survey results exist".
- **Calibration:** three 2025 totals only: SAR East plus North rail passengers, domestic air departures and intercity bus, each fitted to 0.0 % deviation by the alternative-specific constants (runs/r5/demand/calibration-r5-s1/calibration.json). International visitors carry a fixed fitted rail share and no user benefits (A-intl-003, A-cba-310).

**Standard and departure.** DfT TAG expects a calibrated and validated demand model; this one is calibrated on three totals and is not validated against any observed origin–destination matrix. That is why every result carries the synthetic-demand label and why the reference-class ridership ratio (median 0.69 of forecast in the draws, runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json; class A-rcf-029[^S-cost-rcf-013]) is drawn in every Monte Carlo draw. The stated-preference survey that would replace the literature coefficients is designed (`docs/survey/`) and has not been fielded.

## 3.4 Network, running times and alignments (W1, W8)

- **Running times** come from a kinematic model (acceleration, cruise, braking, dwell per stop) with a timetable factor fitted leave-one-out on published Haramain and SAR East times (A-r4-rt-011; Haramain 2018 timetable[^S-cp2-503], current Makkah–Madinah time[^S-r4-rt-003]); every intermediate stop has an explicit minute cost (`docs/network-evaluation.md` §1).
- **Alignments** are least-cost paths on the 30 m terrain under the frozen weights v1 (`cities/ksa/assumptions/align_weights.yaml`, hash `2b718ecb…`; A-align-080 for the route factor). On three operating reference lines the routed paths drifted 3–10 km on average from the real lines, while lengths stayed within ±5 % (`docs/alignments.md` §4). Station additions on existing or committed track are not routed.
- **Commute sheds** at 30 / 45 / 60 minutes and the 30-minute test use the R4 rail graph and OSRM road skims (runs/access/commute-test-s1/; summer factor A-access-011).

**Departure.** The alignments are not engineering designs; the alternative weights v2 are a sensitivity only (§6.4).

## 3.5 Costs (W3)

- **Register:** 207 items with low / central / high values, unit, currency, price year, source and status, normalised to 2025 SAR through one documented price and exchange-rate index (A-cost-001, A-cost-002; `cities/ksa/costs/cost_register.yaml`, `docs/costs.md`).
- **Bottom-up capex** per km by line type and terrain class (flat desert, dunes, sabkha, escarpment), with tunnels and viaducts from the routed alignment, stations by class, systems, rolling stock, land, design and contingency; reconciled against Saudi and international top-down data points (`docs/costs.md` §4–§5).
- **Opex and renewals** over the appraisal period, including an assumed sand-maintenance uplift on dune km (A-cost-302) and assumed renewal shares (A-cost-016); Saudisation share as a parameter (A-cost-300).
- **Reference-class forecasting** (UK Green Book supplementary guidance on optimism bias[^S-cost-rcf-001] and DfT TAG A1.2[^S-cost-rcf-005]): capex is uplifted with the Oxford Global Projects 2020 rail class at strategic stage, P50 1.19, P80 2.21, P90 3.69 (A-rcf-001, A-rcf-031[^S-cost-rcf-008]); schedule with the matching class; the Saudi schedule record (Haramain, Riyadh Metro) sits at or beyond P80–P90 of the global curve, so schedules are reported at P80 and P90 as well (A-rcf-039).

**Departure.** No published cost exists for desert sand mitigation on railways, so that uplift is an assumption with a wide range; terrain-specific benchmark costs were not found (`docs/benchmarks/synthesis.md` §1).

## 3.6 Cost–benefit analysis (W4)

- **Named standard:** HM Treasury Green Book 2026[^S-cp1-088] and DfT TAG (A1.1[^S-cp1-062], A1.3[^S-r5-cba-029], A2.4[^S-r5-cba-011]), with the EC Guide 2014[^S-cp1-067] and World Bank discounting guidance[^S-cp1-069] as cross-checks. No published Saudi appraisal method was found[^S-r5-cba-028].
- **Rates and horizons:** Green Book 2026 declining social rate 3.00 / 2.50 / 2.25 % (A-cba-001[^S-cp1-060]); sensitivities TAG declining, flat 5 % and 7 % (A-cba-002); 30, 40 and 60 years with residual value (A-cba-004).
- **Benefits:** user time and cost savings by the rule of a half on the logit composite cost, non-fuel vehicle operating costs, safety, carbon, air quality and inter-urban decongestion, with a generated no-double-counting matrix (`docs/cba.md` §5). Wider economic impacts are computed by TAG A2.4 but are **indicative only and excluded from every score** (CP6 P4a). Land value uplift is a capture potential, not a benefit.
- **Uncertainty:** 10,000 Monte Carlo draws per case (seed 1) over capex and schedule (the reference-class draws), opex, ridership ratio, value of time, carbon, crash and congestion values and the discount rate (A-cba-302); tornado charts and switching values (`docs/cba.md` §6).

**Departures** (full table in `docs/cba.md` §3): the value of time is transferred from UK TAG values by income (A-cba-010, A-cba-101…106) because no Saudi value-of-time study exists, and the appraisal and behavioural values differ by about 1.9–2.0× (stated, not resolved); reliability is not monetised in the central case (A-cba-109); freight is zero (A-cba-309); the marginal cost of public funds is 1 (A-cba-123); Jeddah decongestion is zero because no candidate is representable in TrafficTwin (a lower bound); every case starts construction in 2027 and is discounted to 2026 (A-cba-301).

## 3.7 Optimisation and phasing (W9)

- **The judge:** a frozen, read-only copy of the demand model and appraisal (judge v3 `v3-variants`, SHA-256 `d9fef643…`, back-tested to reproduce its predecessor on every figure; `docs/r6/judge-hashes.md`, `docs/r6/judge-v3-backtest.md`).
- **Score:** robust NPV, the worst population case of P50 benefits minus P50 costs, 60 years, Green Book 2026, without wider impacts (A-r6-001); reach as the 2025 population within 120 door-to-door minutes of the five metros (A-r6-007), with national reach as a reported column only (A-r6-104).
- **Search:** an exact MILP (HiGHS) on the fast mode, an NSGA-II over robust NPV, capex and reach (A-r6-013), and an agent loop that edits one layout at a time; every kept or front layout is re-scored by the full judge (A-r6-006, A-r6-107). Budget levels B1 / B2 / B3 = SAR 100 / 250 / 500 bn capex P50 (A-r6-003); each phase must be deliverable alone (A-r6-005); each corridor has a phase year of 2030, 2035, 2040 or 2050, with construction starting three years earlier (A-r6-002).
- **Variants:** line type, electrification and dropped intermediate stations on every searchable line corridor; single track is not searched because the frozen model has no track term (A-r6-102).

**Departure.** Phasing is a construction-start choice, not a real-options model with observed-demand triggers; §7 turns the result into stage-gates by hand, with the conditions stated. The v3 genetic search stopped on its restart cap with the reach end still moving (A-r6-106); the robust-NPV maximum is proven by the MILP.

## 3.8 Delivery models and fiscal exposure (W6)

- **Options** (`docs/funding.md`): fully public, public with private O&M, DBFOM availability PPP, DBFOM demand-risk PPP, a hybrid with station-area land value capture, and station-area value capture alone; each with a risk-allocation matrix (`cities/ksa/funding/risk_matrix_*.yaml`).
- **Metrics:** upfront public capex, net fiscal cost over 30 / 40 / 60 years, peak share of total state expenditure (MoF budget line[^S-fund-026], grown by A-fund-005), contingent liabilities and a termination memorandum item (A-fund-102, A-fund-104, A-fund-006), timing profile (A-fund-106).
- **Value for money:** public sector comparator against an availability PPP following Green Book logic[^S-fund-024] (no NCP method was found[^S-fund-056]); private finance at the sovereign real rate (A-fund-101) plus a premium (A-fund-008[^S-fund-r7-001]); PSP Law term of 30 years (A-fund-010[^S-fund-002]).
- **Approximations:** the judge stores P10 / P50 / P90 summaries, not the draws, so the capex tail is a lognormal through P50 and P90 (A-fund-108), PV components known at P50 are scaled with the capex quantile (A-fund-107) and annual flows are level equivalents (A-fund-109). The P10 / P50 / P90 of the engine series are the sorted values of the three runs at capex P10, P50 and P90 (A-fund-107), a cost range rather than quantiles of a simulated distribution.

**Departure.** No Saudi PPP has a published payment schedule, cost of capital, minimum revenue guarantee or termination record for rail; those parameters are registered assumptions with ranges and the value-for-money test reports their switching values (`docs/fiscal-exposure.md`).
