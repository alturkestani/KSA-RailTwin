> **Document version:** docs/report/sections/01-executive-summary.md v1.1 | 5 Nov 2026 | Author: report-writer; FIX_R8 (v1.1: spur figure as a layout difference, five-metro reach qualifier, item 9) | Status: draft

# 1. Executive summary

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

Every figure below is "in the model": a scenario comparison on synthetic, uncalibrated demand, SAR million at 2025 prices, PV 2026, P10 / P50 / P90 over 10,000 draws, judge v3 (`d9fef643…`), seed 1 (runs/r6/top5/top5.csv). The answers are options with their evidence, not advice to any entity.

## 1.1 What was screened

- Every one of the 150 GASTAT governorates in all 13 regions is in the coverage table, screened or excluded with a reason; 1,224 register settlements went through the funnel to a long list of 198 and a short list of 60 (runs/r2/long-list/longlist.parquet, runs/r2/score/summary.json; GASTAT Census 2022[^S-cp2-gastat-007]).
- The short list generated 71 searchable corridors in four families: 23 trunk gaps, 19 branches and spurs, 20 commuter belts and 9 station additions, each costed bottom-up with reference-class uplifts and appraised against S1 (runs/r6/v3/library/library.json; uplift class A-rcf-031).

## 1.2 What the model finds

- **The committed programme itself does not pass in the model.** S1 against S0, medium population: BCR P10 / P50 / P90 0.07 / 0.31 / 1.26 and NPV P50 −60,103 SAR m (runs/cba/CBA-S1-committed-programme). S1 is committed, so the study treats it as the baseline and asks what to add to it.
- **Value is thin and concentrated in small additions.** Of the 71 searchable corridors, four have a positive robust NPV at their best phase (2030, 2035, 2040 or 2050; construction three years earlier, A-r6-002) when scored alone: the Al Jubayl, Dhahran and Duruma station additions and the Al-Kharj spur; no trunk gap, no commuter belt and no other spur does at any phase (runs/r6/v3/library/). Whole families built at 2030 lose between −1,174 (all station additions) and −957,580 SAR m (all trunk gaps) of robust NPV (runs/r6/compare/).
- **Central case, S6-L2** (Al Jubayl and Dhahran stations in phase 2030, construction from 2027; Duruma station in phase 2050, construction from 2047; A-r6-002): robust NPV 6,792; NPV at P90 cost 3,986 / 4,771 / 5,589 (low / medium / high), positive in every population case; capex P10 / P50 / P90 801 / 1,423 / 5,286; BCR P10 / P50 / P90 1.52 / 5.96 / 22.23 (medium) (runs/r6/top5/top5.csv).
- **Upside case, S6-L1** (S6-L2 plus the Al-Kharj spur in phase 2050, construction from 2047): robust NPV 11,023 on capex P10 / P50 / P90 6,233 / 11,194 / 41,304. It carries the Al-Kharj spur's P90 cost risk: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv. The difference between S6-L1 and the same layout without the spur is SAR 4,231 m of robust NPV (S6-L1 − S6-L2, runs/r6/top5/top5.csv).
- **Reach alternative, S6-L3** (Al Jubayl, Dhahran, the Al-Kharj spur and the Riyadh commuter belt 225): it raises the population within 120 door-to-door minutes of the five metros from 3.56 M to 4.25 M, for a robust NPV of 2,427 that turns negative at P90 cost in every case (−21,745 / −19,225 / −16,624) and at 30 years or flat 5 % / 7 % rates (runs/r6/top5/top5.csv).
- **Reach costs money.** Moving along the reach front to the largest reach the B1 budget buys (5.30 M people within 120 door-to-door minutes of the five metros) costs SAR 123.6 bn of robust NPV against S6-L1 (runs/r6/top5/top5.csv; budget levels A-r6-003). No layout brings any new zone within 60 door-to-door minutes of a metro (runs/r6/top5/top5.csv, `access_gain_60` = 0).

## 1.3 Who pays

- No option is self-financing in the model: in the robust (low) population case fares cover less than half of operating and renewal costs on every CP7 programme (PV fares ÷ PV opex and renewals 0.46 for S6-L2, 0.41 for S6-L1, 0.19 for S6-L3; runs/r7/fiscal/fiscal.json), before any capex.
- Net fiscal cost to the state over 60 years, fully public delivery, P10 / P50 / P90: S6-L2 695 / 1,283 / 4,088; S6-L1 4,676 / 8,441 / 23,615; S6-L3 12,696 / 18,962 / 45,343 SAR m, all incremental to S1 (runs/r7/fiscal/fiscal.json).
- An availability PPP is more expensive in expected present value than public delivery for every corridor and programme, and the sign holds across every registered parameter range (value for money S6-L2 −894, S6-L1 −5,124, S6-L3 −8,779 SAR m; runs/r7/vfm/vfm.json). S6-L1 remains the upside case with the spur's cost risk: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv. The decisive driver, the private-finance premium, comes from a UK reference class and is unclear for Saudi Arabia[^S-fund-r7-001] (A-fund-008).
- Thirteen legal and institutional questions stay open (§6.5), among them who sets passenger fares, whether a station can be added inside a committed host line's procurement and how state rail capex is reported; no legal position is inferred (cities/ksa/funding/recommendations.yaml).

## 1.4 What would change the answer

- **Demand.** The demand is synthetic; the reference-class ridership ratio (median 0.69 of forecast in the draws, central ridership ratio 0.693 in runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json; class A-rcf-029[^S-cost-rcf-013]) is already applied in every draw. A calibrated survey-based demand model is the single largest open item (§6.2).
- **Cost tails.** Capex P90 is about 3.7 × P50 for every CP7 layout (runs/r6/top5/top5.csv), following the published reference class for rail at strategic stage (A-rcf-001[^S-cost-rcf-008]). A design-stage estimate that narrowed the Al-Kharj spur's tail is the condition for S6-L1 to pass its stage-gate (§7).
- **Alignments.** Under the alternative alignment weights v2 (a sensitivity only, not adopted) S6-L1's robust NPV moves 11,023 → 11,297 and S6-L3's 2,427 → 3,180; no sign changes (runs/r7-v2/sensitivity.json, §6.4). Under the base weights v1, S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.

## 1.5 Evidence from other countries

Overruns are the common case in the audited record (every high-speed line audited by the European Court of Auditors overran by more than 25 %[^S-bench-fr-086]); measured ridership is mostly below forecast where it was measured[^S-bench-kr-009][^S-bench-fr-043]; and the effects of intermediate stations on small towns are mixed to negative (no clear regeneration at 15 of 18 audited EU stations[^S-bench-st-014]). §5 has the detail.

<!-- gen:fig-fig05-programme-npv-ranges -->
![Figure 5. Programme NPV ranges: S1, and the CP7 layouts against S1](figures/fig05-programme-npv-ranges.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 5.* Left: NPV of the S1 committed programme against S0, P10/P50/P90 (R5 CBA). Right: incremental NPV over S1 of S6-L2 (central), S6-L1 (upside, carries the Al-Kharj spur's P90 cost risk) and S6-L3 (reach), P10–P90 of the judge v3 draws with P50 and the robust NPV; UN WPP medium, 60 years, Green Book 2026.
Source: runs/cba/CBA-S1-committed-programme/results.json; runs/r6/top5/top5.csv. Provenance: R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1 · judge v3 d9fef643… · seed 1. S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:fig-fig05-programme-npv-ranges -->
