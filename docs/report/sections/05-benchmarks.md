> **Document version:** docs/report/sections/05-benchmarks.md v1.0 | 4 Nov 2026 | Author: report-writer | Status: draft

# 5. Benchmarks: what other countries did

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

The W5 dossiers (`docs/benchmarks/<country>.md`) cover every country the brief names: France, Japan, Spain, Germany, China, South Korea, Italy, Morocco, Turkey, the UAE and Egypt, plus a cautionary reference class (California high-speed rail, UK HS2 and others) and cross-cutting notes on small towns and population-growth peers. Each dossier lists what it found and, where nothing reliable was found, says so. Observed outcomes abroad are evidence about those countries, not forecasts for Saudi Arabia; this section summarises `docs/benchmarks/synthesis.md` and adds no new figure.

## 5.1 Cost per km

Cost per km varies by more than an order of magnitude across the audited lines, and within one country as much as between countries: France's own record runs from 6.0 to 28.3 M EUR (2023 prices) per km across ten lines[^S-bench-fr-098]. The sources name drivers (urban nodes, land, viaducts and tunnels in Germany[^S-bench-de-003]; standardised designs and a scale supply industry in China, with the World Bank cautioning that transfer "depends on their individual situations"[^S-bench-cn-081]) rather than measure them. No dossier decomposes cost by terrain class, so desert, dune and sabkha costs are not covered by the benchmarks; the cost register fills that gap with assumptions that carry wide ranges (A-cost-302).

<!-- gen:fig-fig13-benchmark-cost-per-km -->
![Figure 13. Benchmark cost per route-km, converted to SAR 2025](figures/fig13-benchmark-cost-per-km.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 13.* Cost per route-km of the grade A–C benchmark rows (SAR m per km, 2025 prices, central conversion, log scale) by country with the country median, beside capex P10/P50/P90 ÷ routed length of the two routed CP7 lines (Al-Kharj spur, Riyadh belt 225).
Source: cities/ksa/corridors/branch_spur/S3-branch_spur-al-kharj.yaml; cities/ksa/corridors/commuter_belt/S4-commuter_belt-riyadh-225.yaml; cities/ksa/benchmarks/metrics.csv; cities/ksa/costs/index.yaml; cities/ksa/benchmarks/cost_levels.yaml; runs/r7/fiscal/fiscal.json; docs/benchmarks/README.md. Provenance: benchmark register cities/ksa/benchmarks (R1b) · R7 funding engine runs/r7 on judge v3 d9fef643… scores · seed 1.
<!-- /gen:fig-fig13-benchmark-cost-per-km -->

## 5.2 Overruns

Cost and schedule overruns are the common case in the audited record. The European Court of Auditors found that "all audited high-speed lines had cost overruns of more than 25 %"[^S-bench-fr-086]; Spain's audited lines and the Madrid–Barcelona contracts overran at line and contract level[^S-bench-es-001][^S-bench-es-003]; the UK National Audit Office reports that HS2 costs doubled since 2020[^S-bench-caut-062]; Korea's audit board projected Gyeongbu costs 25.86 % above the 1997 plan[^S-bench-kr-022]. Opening dates moved by years in Egypt[^S-bench-eg-018], Turkey[^S-bench-tr-013] and Japan[^S-bench-jp-010][^S-bench-jp-003]. The record is not uniform: Morocco's completed-cost figure equals the plan figure in the audit court report, so its overrun cannot be settled from the sources read, and China's single recorded observation came in below its estimate (`docs/benchmarks/morocco.md`, `docs/benchmarks/china.md`).

The study's capex ranges already carry this evidence through the reference-class uplift (P90 3.69 × the base for rail at strategic stage, A-rcf-001[^S-cost-rcf-008]). The two Saudi data points (Haramain and the Riyadh Metro) sit at or beyond P80–P90 of the global schedule curve (A-rcf-039).

## 5.3 Ridership against forecast

Ex-post comparisons exist for few lines; where they exist most early-year outturns were below forecast. Korea's first-year ratios sit near one half of the forecast in the abstracts read[^S-bench-kr-009][^S-bench-kr-011]; the Channel Tunnel forecasts "largely and systematically overestimated" the market[^S-bench-caut-043]; Brightline's ridership growth was below its rating case[^S-bench-caut-036]; France's LGV SEA traffic was 4 to 10 % below the public-inquiry forecasts[^S-bench-fr-043]. There are exceptions: LGV Est phase 1 came in 4 % above its expectation[^S-bench-fr-055], and Morocco's Al Boraq rose from 0.43 of its opening forecast in year 3 to 0.93 in year 7 (press-reported operator figures)[^S-bench-ma-026][^S-bench-ma-012]. The study applies the reference-class ridership ratio (median 0.69 of forecast in the draws, runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json; class A-rcf-029[^S-cost-rcf-013]) in every draw.

## 5.4 Farebox recovery

Line-level operating ratios are rarely public. They were found for Turkey only (ticket revenue covering 73–79 % of cost in 2017–2018, with public service payments)[^S-bench-tr-003]; Spain's operators ran operating losses in 2023–2024 on the regulator's totals[^S-bench-es-005]; China's weaker 200–250 km/h lines are linked by the World Bank to fixed, low fares[^S-bench-cn-084]. In the model, PV fares cover 0.19–0.46 of PV operating and renewal costs on the CP7 programmes in the robust case (runs/r7/fiscal/fiscal.json): no comparator suggests that a Saudi line would be self-financing.

## 5.5 The 200–800 km band

The band has partial support. In Japan rail carried the largest share in the 300–700 km bands in 2000, with air dominant beyond about 700 km[^S-bench-jp-001]; in Spain rail's share was high on 365–621 km corridors and fell sharply beyond about 180 minutes[^S-bench-es-005][^S-bench-es-004]; French evidence puts air dominance at about three to four hours of rail journey[^S-bench-fr-045]. The evidence points to travel time, frequency and price, not distance, as the operative variable; on Berlin–Munich air was faster door-to-door[^S-bench-de-019]. No Gulf or desert-climate evidence exists in the dossiers. In this study's model no generated trunk gap in or near the band has a positive robust NPV (runs/r6/v3/library/).

## 5.6 Small towns and intermediate stations

The clearest audit and peer-reviewed results on in-between and peripheral places are negative or null: no clear regeneration at 15 of 18 audited EU stations[^S-bench-st-014], a sizable employment decrease in in-between Shinkansen municipalities[^S-bench-st-001], and GDP falls in peripheral Chinese counties on upgraded lines[^S-bench-st-032]. Positive results exist but are narrower (GDP, prices or migration at specific stations; `docs/benchmarks/small-towns.md`). No study read gives a planning number for a small town's population, jobs or land value against a matched control. This bears on the station additions that make up S6-L2: their benefits in the model are user time savings, not local regeneration, and no regeneration benefit is added (`docs/cba.md` §5).

## 5.7 Delivery models observed

State-led construction and operation (China, Spain's ADIF and Renfe, Turkey, Morocco, Egypt with an export-credit-financed contractor consortium), concession (France's LGV SEA), private (Brightline), open-access competition on public infrastructure (Italy) and a state developer with an operating joint venture (UAE). The dossiers record what each model allocated, for example that the SEA concession shifted construction-cost risk away from the public budget but did not reduce its cost per km, which "a atteint un niveau record"[^S-bench-fr-032], but they contain no like-for-like comparison of outcomes by model. The Haramain line was delivered through public design-build packages and an EPC plus O&M contract, about six years late, with 2023 ridership about an eighth of the design projection (secondary)[^S-fund-261][^S-fund-265].

## 5.8 Gaps carried forward

Line-level farebox and operating ratios; ex-post ridership against forecast; terrain-specific costs; any Gulf outcome data; and primary audit documents not reached (Cour des comptes 2014, Korea's audit board, Morocco's audit court on the final Al Boraq cost, the California High-Speed Rail Authority plans). The per-dossier "no reliable data found" lists and the gaps table in `docs/benchmarks/README.md` are the full record.
