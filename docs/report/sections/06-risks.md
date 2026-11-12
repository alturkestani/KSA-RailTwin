> **Document version:** docs/report/sections/06-risks.md v1.0 | 4 Nov 2026 | Author: report-writer | Status: draft

# 6. Risks, sensitivities and open questions

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

## 6.1 Cost overruns

The capex ranges are reference-class ranges with a heavy upper tail: capex P90 is about 3.7 × P50 for each CP7 layout (S6-L2 5,286 against 1,423; S6-L1 41,304 against 11,194; S6-L3 73,799 against 19,630; runs/r6/top5/top5.csv), because the published rail class at strategic stage has P90 3.69 (A-rcf-001[^S-cost-rcf-008]). The held-out P90-cost test is the study's main cost-risk check: on it every flagged layout among the top 25 contains the Al-Kharj spur (runs/r6/holdout.csv). S6-L2 stays positive at P90 cost in every population case; S6-L1 does not: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv. S6-L3 is negative at P90 cost in every case (runs/r6/top5/top5.csv).

Switching values and the largest one-at-a-time drivers of the five CP7 corridors:

<!-- gen:switching -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| corridor (R5 CBA case, construction start 2027) | central BCR | demand for BCR = 1 (share of the modelled forecast) | capex × for BCR = 1 | value-of-time × for BCR = 1 | constant real rate at NPV = 0 | largest three tornado swings (NPV swing, SAR m) | run |
|---|---|---|---|---|---|---|---|
| Al Jubayl station (GCC Railway) | 129.59 | 6 % | 15.29 | n/a | 18.69 % | ridership actual/forecast (P10/P90) (10,212); discount rate (TAG 3.5 % declining / flat 7 %) (3,377); carbon value (low/high) (2,845) | `runs/cba/CBA-S5-station_addition-al-jubayl` |
| Dhahran station (SAR East line) | 3.84 | 17 % | 5.43 | n/a | 10.37 % | ridership actual/forecast (P10/P90) (3,806); carbon value (low/high) (1,345); capex (uplifted, P10/P90) (1,294) | `runs/cba/CBA-S5-station_addition-dhahran` |
| Duruma station (Landbridge) | 1.24 | 52 % | 1.46 | 0.72 | 4.02 % | capex (uplifted, P10/P90) (1,294); ridership actual/forecast (P10/P90) (1,228); value of time (low/high) (919) | `runs/cba/CBA-S5-station_addition-duruma` |
| Al-Kharj spur | 1.06 | 66 % | 1.09 | 0.85 | 3.03 % | ridership actual/forecast (P10/P90) (24,528); capex (uplifted, P10/P90) (24,264); value of time (low/high) (6,400) | `runs/cba/CBA-S3-branch_spur-al-kharj` |
| Riyadh commuter belt 225 (Al Muzahimiyah, Duruma) | 0.14 | 422 % | n/a | 11.51 | n/a | capex (uplifted, P10/P90) (23,673); discount rate (TAG 3.5 % declining / flat 7 %) (5,059); ridership actual/forecast (P10/P90) (4,937) | `runs/cba/CBA-S4-commuter_belt-riyadh-225` |
Runs: runs/cba/CBA-<id>/switching_values.json and tornado.csv (R5 CBA, seed 1, medium population, 60 years, Green Book 2026; the R5 model before the CP6 zone split, so the levels differ from the judge v3 figures in the other tables; the ordering of the drivers is what this table shows).
<!-- /gen:switching -->

<!-- gen:fig-fig14-tornado-switching -->
![Figure 14. Tornado and switching values: S1 and the Al-Kharj spur](figures/fig14-tornado-switching.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 14.* One-at-a-time NPV tornado (each input at its low/P10 and high/P90 value) and the switching values for the S1 committed programme against S0 and the Al-Kharj spur against S1 (R5 CBA, docs/cba.md §6).
Source: runs/cba/CBA-S1-committed-programme/tornado.csv; runs/cba/CBA-S1-committed-programme/switching_values.json; runs/cba/CBA-S3-branch_spur-al-kharj/tornado.csv; runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json. Provenance: R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1.
<!-- /gen:fig-fig14-tornado-switching -->

Reading the table: for the Al-Kharj spur, in the model, capex 9 % above its central uplifted value or demand below 66 % of the modelled forecast takes its BCR to 1, and the ridership ratio and capex give the two largest NPV swings (runs/cba/CBA-S3-branch_spur-al-kharj). The two 2030 stations keep a BCR above 1 down to a small share of the modelled demand; Duruma needs about half of it (runs/cba/CBA-S5-station_addition-duruma). The Riyadh belt 225 needs more than four times the modelled demand (runs/cba/CBA-S4-commuter_belt-riyadh-225).

## 6.2 Demand shortfall

- The demand is synthetic: calibrated on three 2025 totals and validated against no observed origin–destination matrix (runs/r5/demand/calibration-r5-s1/calibration.json). This is the largest single uncertainty in the study.
- The reference-class ridership ratio (actual ÷ forecast: median 0.69 in the draws, runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json; class P10 0.25, P90 1.35, A-rcf-029[^S-cost-rcf-013]) is drawn in every draw, so the ranges already include a typical shortfall; it is a correction from the international record, not a Saudi measurement (A-rcf-035).
- The mode-choice coefficients are literature-based until the designed stated-preference survey is fielded by people, not by this project (`docs/survey/`); the behavioural and appraisal values of time differ by about 1.9–2.0× (A-cba-106).
- International pilgrims and tourists carry no user benefits (A-cba-310) and freight is not monetised (A-cba-309): both make the benefit side a lower bound for lines that would carry them.
- Population: the robust case is always UN WPP low; on the held-out high case only two of the top 25 holdout layouts move more than five places (runs/r6/holdout.csv).

## 6.3 Fiscal exposure and delivery risk

- **Contingent liabilities.** Under an availability PPP the overrun above the private cushion stays with the state: for S6-L1, 4,859 expected and 14,611 at P90 capex (PV, SAR m); for the Al-Kharj spur alone 3,963 and 11,921 (runs/r7/fiscal/fiscal.json; A-fund-102). For S6-L1 these arise in the cases where its economic case fails: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
- **Termination** at opening is a memorandum item, not added to the net fiscal cost; the PSP Law allows compensation that may include lost revenues (A-fund-006[^S-fund-008]).
- **Budget share.** The peak share of total state expenditure at P90 capex is 0.091 % (S6-L2, 2027), 0.662 % (S6-L1, 2047) and 1.230 % (S6-L3, 2047) under fully public delivery (runs/r7/fiscal/fiscal.json); beyond 2028 the denominator is a projection (A-fund-005[^S-fund-026]), and no rail or transport budget line was found.
- **Evenhanded reading.** For a PPP: a fixed-price contract can protect the budget from overruns up to the private cushion and has delivered on time elsewhere[^S-fund-047], and the National Center for Privatization targets value for money from PPPs[^S-fund-030]. For public delivery: the corridors are small or interface-bound, their fares do not carry the costs, the tail beyond any cushion stays with the state under every model, and public finance avoids the premium[^S-fund-r7-001]. Public delivery has its own schedule and demand risks, which the state carries in full (Haramain[^S-fund-265]). The value-for-money sign would change only if Saudi bids priced risk far below the reference class (switching values in runs/r7/vfm/vfm.json; A-fund-007, A-fund-008).

## 6.4 Alignment weights v2 (sensitivity only; not in any headline)

The frozen weights v1 are the base for every figure in this report. A second weight set, v2, was routed for the two CP7 line corridors (the Al-Kharj spur and the Riyadh belt 225), re-costed and re-scored with the same frozen judge, and is reported here only (`docs/alignments.md` §4c). Geometry, v1 → v2: the Al-Kharj spur 139.2 → 138.5 km, tunnel plus viaduct 2.0 → 0.6 km, earthworks 4.8 → 12.3 km; the Riyadh belt 225 79.0 → 69.5 km, tunnel plus viaduct 8.0 → 13.7 km (runs/align/corridors-v2-s1/; A-align-100). Every figure that moved:

<!-- gen:alignment-v2 -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| entity (weights v1 → v2) | robust NPV (SAR m) | capex P50 (SAR m) | capex P90 (SAR m) | net fiscal cost 60 y P50, fully public (SAR m) | VfM (% of PSC) |
|---|---|---|---|---|---|
| `S3-branch_spur-al-kharj` | 4,309 → 4,577 | 9,771 → 9,272 | 36,018 → 33,868 | 7,523 → 7,247 | −4,230 → −4,013 (−38.5 % → −38.3 %) |
| `S4-commuter_belt-riyadh-225` | −8,293 → −7,778 | 8,910 → 10,227 | 34,256 → 40,520 | 11,320 → 11,194 | −3,860 → −4,432 (−26.2 % → −28.9 %) |
| `S5-station_addition-al-jubayl` | 4,982 → 4,982 | 474 → 474 | 1,762 → 1,762 | 168 → 168 | −344 → −344 (−72.3 % → −72.3 %) |
| `S5-station_addition-dhahran` | 2,362 → 2,362 | 474 → 474 | 1,762 → 1,762 | 682 → 682 | −344 → −344 (−34.8 % → −34.8 %) |
| `S5-station_addition-duruma` | 481 → 481 | 474 → 474 | 1,762 → 1,762 | 483 → 483 | −205 → −205 (−31.4 % → −31.4 %) |
| `S6-L2` | 6,792 → 6,792 | 1,423 → 1,423 | 5,286 → 5,286 | 1,283 → 1,283 | −894 → −894 (−41.2 % → −41.2 %) |
| `S6-L1` | 11,023 → 11,297 | 11,194 → 10,695 | 41,304 → 39,154 | 8,441 → 8,197 | −5,124 → −4,907 (−38.9 % → −38.8 %) |
| `S6-L3` | 2,427 → 3,180 | 19,630 → 20,448 | 73,799 → 77,912 | 18,962 → 18,478 | −8,779 → −9,135 (−32.2 % → −33.4 %) |
Run: runs/r7-v2/sensitivity.json (weights v2, not adopted; docs/alignments.md §4c; d9fef643… judge v3, seed 1). The three station additions and S6-L2 are not routed and do not change. S6-L1 under the base weights v1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:alignment-v2 -->

In the model, no sign changes under v2: the S6-L1 robust NPV rises by 274 and S6-L3's by 754, the value-for-money sign is unchanged everywhere, and S6-L2 does not move because station additions are not routed (runs/r7-v2/sensitivity.json). S6-L1 under v1, the base: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv. Adopting v2 would mean re-running R6 and R7 for every corridor, not only these two.

## 6.5 Open legal and institutional questions

Thirteen of the sixteen legal and institutional items reviewed are unclear on the sources read. Each is kept as an open question; no legal position is inferred from any of them, and none is resolved in this report.

<!-- gen:legal -->
| # | item | open question (no legal position is inferred) | sources |
|---|---|---|---|
| 1 | `sar_ownership_form` | Who are SAR's shareholders per its commercial registration or articles, and what is its legal form? | [^S-fund-034][^S-fund-035] |
| 2 | `fiscal_reporting` | Are SAR's capex and debt consolidated in general-government statistics or the budget, and would PPP payment commitments or guarantees be disclosed? (fully public via budget, PIF or SAR differ in reporting, not in the risk the state carries) | [^S-fund-029][^S-fund-026] |
| 3 | `pif_role` | Does PIF currently finance SAR's capex (equity, loans or guarantees), and what do Arts. 3-4 of the official PIF Law text say on domestic infrastructure and guarantees? | [^S-lb-012][^S-lb-009][^S-fund-036][^S-fund-037] |
| 4 | `fare_setting_authority` | Who sets and approves passenger fares on intercity and commuter rail (the state rail company, TGA, a ministry or a concession contract)? Railway Law Art. 18 covers usage (access) fees under use agreements, not passenger fares; no source read settles it. | [^S-fund-016][^S-fund-012] |
| 5 | `railway_law_regulation` | Which cases of the Railway Law Implementing Regulation allow transfer of existing assets to a concessionaire, and has TGA published a usage-fee policy? | [^S-fund-054][^S-fund-055] |
| 6 | `psp_regulations_thresholds` | What do the amended (2023/2024) Implementing Regulations say on the SAR 200 m PPP threshold (reported by secondary sources), procurement methods, the VfM study and MoF fiscal approval? | [^S-fund-041][^S-fund-053][^S-fund-042] |
| 7 | `psp_relevant_agency` | For an intercity or commuter rail PPP, which body is the relevant and the executive agency (Art. 2 governing rules), and is SAR a contracting authority under Art. 4? | [^S-fund-010] |
| 8 | `psp_railway_interaction` | Does a rail concession tendered under Railway Law Art. 32 also follow PSP Law procedures (NCP study, MoF approval)? | [^S-fund-013][^S-fund-003] |
| 9 | `ncp_vfm_method` | Has NCP published a VfM or PSC method (the R7 test follows the Green Book logic as a named reference)? | [^S-fund-030][^S-fund-056][^S-fund-024] |
| 10 | `om_contract_status` | Is a 5-year-plus O&M-only rail contract (as on Haramain) a PPP under PSP Law Art. 1, with NCP and MoF steps, or ordinary government procurement? | [^S-fund-001][^S-fund-039] |
| 11 | `host_line_procurement` | Can a station on a committed host line (GCC Railway in design; the Landbridge in phased delivery after the PPP talks ended) be added within the host line's procurement, and under what procurement model are the Landbridge phases being let? | [^S-029][^S-059][^S-lb-001][^S-060] |
| 12 | `lvc_instruments` | Which Saudi instruments (development rights on railway land under Railway Law Art. 33, municipal fees, the white-land fee) could legally be earmarked for rail? | [^S-fund-014] |
| 13 | `land_expropriation` | What expropriation procedure and timetable apply to a new rail alignment (not reviewed in R1d or R7)? | [^S-fund-014][^S-fund-006] |
Register: cities/ksa/funding/recommendations.yaml `legal_items` (13 items with status unclear; docs/delivery-models.md, All legal and institutional items).
<!-- /gen:legal -->

The three items found clear (the state rail company's mandate, the Railway Law concession articles and the PSP Law steps) are in `docs/delivery-models.md` with their sources.

## 6.6 Other limits

- **Rates and horizons.** S6-L1 and S6-L2 stay positive at 30 and 40 years and at flat 5 % and 7 % at P50 cost (S6-L1 at P90 cost: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv); S6-L3 is negative at 30 years and at flat 5 % and 7 % (runs/r6/top5/top5.csv; A-cba-002, A-cba-004).
- **Wider economic impacts** are indicative only and excluded from every score: under TAG's own definition the effective density fell in a development test, so the agglomeration estimate is not reliable on governorate-sized zones (`docs/cba.md` §7; A-cba-130).
- **The fast search mode** overstates robust NPV against the full judge (by 72.7 % of capex on S6-L2), so every reported layout is a full-judge score (runs/r6/v3/rescore/rescore.json; A-r6-006).
- **Phasing** is a construction-start convention with a drawn construction duration (A-r6-002), not a real-options model; §7 adds the gates by hand.
- **Track** has no term in the frozen model, so single track was not searched (A-r6-102).
