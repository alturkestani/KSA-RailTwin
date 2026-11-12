> **Document version:** docs/r6-topology.md v1.5 | 5 Nov 2026 | Author: FIX_R8 (v1.4: spur figure as a layout difference, R8-checkpoint review item 9b; v1.5: the same at §0 'why each one' and the five-metro reach qualifier on the layout table, VERIFY_FIX_R8 pass 1); INTEGRATE_R8 (§ outputs: coding-assistant mention reworded to "the builder", R8 review item 2b); INTEGRATE_R6_V3 (register pointer); R6 builder (optimizer); R6_V3 builder (judge v3: §0 scope, §0.1 national reach, §0.2, §3, §6, §7) | Status: reviewed

# R6 — national network topology optimisation (W9)

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Everything below is "in the model": a scenario comparison on a modelled demand base. Costs and benefits are P10/P50/P90 ranges from 10,000 Monte Carlo draws (seed 1); money is SAR million at 2025 prices, present values at 2026 (A-cba-301). Write "in the model, X changes by", never "will".


## 0. Results in brief (in the model; robust NPV = the worst of the three population cases)

**R6_V3 (judge v3, CP7-3): no variant improves S6-L1, S6-L2 or S6-L3; the CP7 layout set is unchanged (§0.2).**

**Scope (v1.1):** inclusion, phasing and, since R6_V3, the variants: line type, electrification and dropped intermediate stations on every searchable line corridor (judge v3, `judge/v3-variants`, SHA-256 `d9fef643…`, which reproduces v2 exactly: 8,763 of 8,763 figures, `docs/r6/judge-v3-backtest.md`). Single track was scored once and pruned because the frozen model has no track term (A-r6-102). Station relocation and new links stay out (CP7-6: no agent-proposed links). Figures in §0–§5 are the R6 (v2) results; v3 reproduces every one of them, and §0.2 adds what the variants change.

- **The search space is thin on value.** Of the 71 searchable corridors only six have a positive robust NPV at their best phase when scored alone (library `runs/r6/library/`): the Al Jubayl, Dhahran and Duruma station additions, the Al-Kharj spur (positive at every phase, robust NPV 2,254 at 2030 rising to 4,309 at 2050) and the two retired Jubail variants. Every S2 trunk gap, every S4 belt and every other S3 spur loses money in every population case at every phase; for every loss-making corridor, deferral to 2050 cuts the loss (lower PV of capex).
- **The robust-NPV optimum is small and the budget does not bind.** The exact MILP (fast mode) gives the same 4-corridor layout at B1, B2 and B3 (`runs/r6/milp/`), and all 20 GA runs (5 seeds × 3 budgets + seeded and holdout rounds) reach it: **S6-L1** = Al Jubayl + Dhahran stations (2030), Duruma station + Al-Kharj spur (2050). Full judge: robust NPV **SAR 11.0 bn**, capex P50 SAR 11.2 bn (P10 6.2 / P90 41.3).
- **Robustness to cost risk favours the stations-only layout.** On the held-out P90-cost test every flagged layout contains the Al-Kharj spur: they drop 7–13 places and L1 turns negative (S6-L1: −SAR 3.0 bn low case at P90 cost), while **S6-L2** (the three stations only, capex P50 SAR 1.4 bn) stays positive in every case (P90 cost +SAR 4.0 to 5.6 bn; NPV P10 of the draws +SAR 1.1 bn, medium). Flagged layouts: `runs/r6/holdout.csv`.
- **Reach costs money.** Door-to-door accessibility at 60 minutes never changes (no rail journey reaches any new zone within 60 door-to-door minutes of the five metros, as R5 found at 90 minutes, H9a), so the trade-off runs on the 120-minute band. Going from L1 (3.56 M people) to the B1 maximum (S6-L5, 5.30 M, 12 corridors) costs SAR 123.6 bn of robust NPV on SAR 98.2 bn capex; the front ends at about SAR 240 bn capex (5.39 M), so **B3 (SAR 500 bn) never binds**.
- **Which engine found what.** Every top-5 layout is on every GA front; the MILP proves the fast optimum; the agent loop (17 edits after the seed) reached L1–L4 by its own edits but found no layout outside the GA front. Its value was in the full-judge interactions the fast mode cannot see: Duruma turns negative next to the Riyadh belt 225 (−SAR 1.3 bn), and the Dammam belt 315 adds only 5.8k reach next to the Dhahran station for SAR 9.2 bn of NPV.
- **Fast vs full:** Spearman rank correlation **1.0** over 14 re-scored front layouts; the fast mode overstates robust NPV by 1–17 % of capex (corridors compete for the same trips); capex and reach are exact.

### 0.1 Top 5 layouts (full judge, 10,000 draws, seed 1; `runs/r6/top5/<L>/score.json`, scenario files `scenarios/S6-L1..L5.yaml`, maps `runs/r6/top5/<L>-map.png`, table `runs/r6/top5/top5.csv`)

| | S6-L1 | S6-L2 | S6-L3 | S6-L4 | S6-L5 |
|---|---|---|---|---|---|
| Corridors (phase) | Al Jubayl, Dhahran (2030); Duruma, Al-Kharj spur (2050) | Al Jubayl, Dhahran (2030); Duruma (2050) | Al Jubayl, Dhahran (2030); Al-Kharj spur, Riyadh belt 225 (2050) | L3 + Makkah belt 045 (2050) | Al Jubayl, Dhahran (2030); Riyadh belts 000/090/225/270, Jeddah 000/315, Makkah 045/090/315, Madinah 045 (2050) |
| Robust NPV (P50 PVB − P50 PVC, worst case) | 11,023 | 6,792 | 2,427 | −7,934 | −112,565 |
| NPV at P50 cost, low / medium / high | 11,023 / 13,255 / 15,556 | 6,792 / 7,572 / 8,384 | 2,427 / 4,890 / 7,428 | −7,934 / −4,864 / −1,617 | −112,565 / −110,365 / −108,017 |
| NPV at P90 cost, low / medium / high (held out) | −2,958 / −724 / 1,631 | 3,986 / 4,771 / 5,589 | −21,745 / −19,225 / −16,624 | −54,553 / −51,470 / −48,184 | −229,925 / −227,697 / −225,401 |
| NPV draws P10 / P50 / P90 (medium) | −5,243 / 11,301 / 40,819 | 1,051 / 7,053 / 18,604 | −20,113 / 2,215 / 34,873 | −48,564 / −8,477 / 32,796 | −222,390 / −109,484 / −67,710 |
| BCR P10 / P50 / P90 (medium, without WEIs) | 0.60 / 2.33 / 9.33 | 1.52 / 5.96 / 22.23 | 0.32 / 1.12 / 3.48 | 0.21 / 0.75 / 2.22 | 0.03 / 0.14 / 0.37 |
| Capex P10 / P50 / P90 (uplifted, undiscounted) | 6,233 / 11,194 / 41,304 | 801 / 1,423 / 5,286 | 10,684 / 19,630 / 73,799 | 19,031 / 36,726 / 143,343 | 52,401 / 98,170 / 374,892 |
| Added rail trips 2050, medium (vs S1) | 4.29 M | 1.78 M | 4.85 M | 6.62 M | 5.51 M |
| Added rail passenger-km 2050 (m) | 669 | 17 | 790 | 936 | 418 |
| New route-km; added trips per route-km | 139; 30,828 | 0; n/a | 218; 22,218 | 313; 21,135 | 989; 5,569 |
| Reach gain, 60 / 120 min door-to-door (2025 population, five metros) | 0 / 3.56 M | 0 / 3.56 M | 0 / 4.25 M | 0 / 4.67 M | 0 / 5.30 M |
| PV of carbon benefit P50 (medium) | 7,126 | 3,202 | 7,684 | 9,365 | 6,490 |
| HHR / Landbridge passengers 2050 (S1: 11.27 M / 4.76 M) | 11.28 M / 5.60 M | 11.27 M / 5.27 M | 11.28 M / 5.11 M | 10.77 M / 4.94 M | 10.35 M / 4.55 M |
| National reach, 2025 population within 60 / 120 door-to-station minutes of any station of S1 + layout (S1 alone: 22.35 M / 26.10 M of 35.93 M); **reported column only, not in the score** (CP7-5, A-r6-104) | 23.36 M / 26.67 M | 22.94 M / 26.25 M | 23.40 M / 26.67 M | 24.38 M / 26.89 M | 24.21 M / 26.63 M |
| National reach gain vs S1, 60 / 120 min (reported only) | +1.01 M / +0.57 M | +0.59 M / +0.15 M | +1.05 M / +0.57 M | +2.04 M / +0.79 M | +1.87 M / +0.54 M |
| WEIs, PV P50 (indicative only, CP6 P4a; not in the score) | 142,741 | 114,628 | 267,682 | 310,951 | 370,715 |
| Rate/horizon sensitivity, medium, NPV at P50 cost: GB2026 30 y / 40 y; TAG; flat 5 %; flat 7 % | 6,227 / 8,020; 9,866; 3,503; 946 | 4,035 / 5,307; 6,155; 3,225; 1,535 | −46 / 367; 2,799; −716; −1,433 | −7,833 / −8,870; −5,769; −6,684; −5,126 | −82,021 / −99,727; −91,563; −52,563; −28,688 |

SAR million, 2025 prices, PV 2026 unless stated. Since R6_V3 the files are the v3 scores (`runs/r6/top5/<L>/score.json`, copied from `runs/r6/v3/backtest/<L>/`, identical to v2 in every figure; the v2 copies are in `runs/r6/top5-v2/`); the national reach is added to each `score.json` under `national_reach_reported_only` and to `top5.csv` (`runs/r6/v3/national_reach.json`, `optimise/reach.py`). National reach counts every zone within 120 door-to-station minutes (road minutes from the R4 station skims + 10 terminal minutes, × summer factor 1.15) of any station, so it also counts the trunk-gap and regional towns the five-metro band ignores; the 90-minute station access cap of the demand model is not applied (with it, L1 120-min = 26.47 M). The Dhahran station carries 3.04 M of the 120-minute reach gain on its own (library); Al Jubayl 0.42 M; Duruma 0.10 M.

**Why each one is on the list.** L1: the highest robust NPV found by every engine, but its value hangs on the Al-Kharj spur (the difference between S6-L1 and the same layout without the spur, L2, is SAR 4,231 m of robust NPV) and it goes negative at P90 cost. L2: the cost-robust choice: positive at P90 cost in every case, BCR P10 1.52, about one-eighth of L1's capex; it gives up the Al-Kharj spur's 2.5 M added trips. L3: the cheapest step up the reach front (+0.68 M people within 120 min for SAR 8.6 bn more robust NPV loss than L1); its NPV is near zero at P50 and negative at 30 years or flat rates. L4: reach in a second metro (Makkah), already negative at P50. L5: what the B1 budget buys at the reach end: 1.7 M more people within 120 min than L1 for a robust NPV of −SAR 112.6 bn; dominated on NPV by every other layout.

### 0.2 Judge v3: what changed (R6_V3, CP7-3; 3–4 Nov 2026)

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Files: `runs/r6/v3/` (library, MILP, GA, re-score, CP7 edits, back-test); `runs/r6/v3/results.tsv` (47,108 rows, one per evaluation with its hypothesis); registers A-r6-101…107 (`docs/assumptions.md`, A-r6-101…107; folded from the r6v3 fragment at INTEGRATE_R6_V3).

- **The judge.** v3 = v2 + the one-line variant-id fix (`<corridor-id>-v<8-hex>`, accepted by the LineSpec pattern). Back-test: S0, the S1 programme and S6-L1…L5 re-scored through v3, **8,763 / 8,763 figures identical** (`docs/r6/judge-v3-backtest.md`); the 73 base corridors of the library too (26,457 / 26,457, `runs/r6/v3/backtest/library-v3-vs-v2.json`).
- **Variant library** (`runs/r6/v3/library/`, 217 single-corridor runs, every one at all four phases): the 73 base corridors, 65 line-type, 62 electrification and 16 station-drop variants, 1 single-track demonstration. Not scored: single track on the other 61 line corridors (no track term in the model: the demonstration is identical to the base, A-r6-102); the 9 station additions (no variant field applies); stage-2 combinations (A-r6-103: none qualified, because no electrification variant improves any corridor). 15 of 65 line-type and 8 of 16 station-drop variants improve their corridor at its best phase; **0 of 62 non-electrified variants do** (traction energy and carbon cost more than the electrification capex saved, −78 to −6,716). The largest gains are on corridors that stay deeply negative: Riyadh–Jeddah trunk as conventional instead of HSR +19,758 (still −47,603; capex P50 −56,456 at 2030), Riyadh–Dammam conventional +2,903 (still −14,097), Riyadh–Jeddah without the Al-Quway'iyah stop +1,607. **No variant turns a corridor positive.** Wall time 18:43–20:25 UTC (6 runs in parallel, about 1.7 h; the enumeration estimate was 1.4 h, so no pruning rule beyond A-r6-102 was needed).
- **MILP** (exact, fast mode, 214 options × 4 phases): the same layout as R6 at B1, B2 and B3, with no variant option: S6-L1 (fast robust NPV 12,135; `runs/r6/v3/milp/`; the run without variants gives the same).
- **NSGA-II** (5 seeds × B1/B2/B3, R6 settings): every run stopped on the 30-restart cap with the front still moving (A-r6-106; fronts of 2,036–3,985 points, because variants add many near-equal capex/NPV trade-offs); the combined fronts hold 2,964 (B1), 5,542 (B2) and 5,638 (B3) points, 97–99 % of them with at least one variant. The maximum robust NPV on every front is S6-L1 without variants; variants extend the reach end: B1's largest 120-min reach is 5.33 M (v2: 5.30 M) and the overall front ends at 5.42 M (v2: 5.39 M) at about SAR 214–235 bn capex.
- **Full-judge re-score** (A-r6-107: 29 layouts: the R6 spread plus the best variant point per budget (21), and the MILP layout and the 9 R6 agent-kept layouts, of which 8 are new (the MILP layout and one kept layout are S6-L1, a front point)): fast vs full Spearman **0.992**; the fast mode overstates robust NPV on 27 of the 28 non-empty layouts (by up to SAR 48.5 bn at the reach end, and by 72.7 % of capex on L2, whose capex is only 1,423) and understates it on one (by 93); capex and reach are exact; judge SHA-256 identical at start and end (`runs/r6/v3/rescore/`). Best full-judge layout with a variant: L1 with the Al-Kharj spur non-electrified, 10,648 (below L1). The reach-end variant layouts cost more NPV per person reached than the v2 L5: e.g. 5.33 M people within 120 min for −145,699 robust NPV at capex 97,847 (v2 L5: 5.30 M, −112,565, 98,170).
- **Agent round:** not run. Variant points are non-dominated on the GA front (so a round was allowed), but they sit at the reach end below −SAR 70 bn; the variant edits that matter for the CP7 set were scored directly on L1–L3 (below, 10 full-judge runs). CP7-6: no new links.

**The CP7 layout set (CP7-1) before and after** (full judge, 10,000 draws, seed 1, 60 years, Green Book 2026; SAR m; `runs/r6/v3/cp7/cp7.csv`; adoption rule A-r6-105: robust NPV up **and** the P90-cost sign kept):

| Layout and edit | Robust NPV (Δ) | Capex P50 (Δ) | Capex P90 | NPV at P90 cost, low / medium / high | Verdict |
|---|---|---|---|---|---|
| **S6-L1** as in R6 (v3 judge) | **11,023** | 11,194 | 41,304 | −2,958 / −724 / 1,631 | kept |
| L1, Al-Kharj spur non-electrified | 10,648 (−375) | 10,156 (−1,039) | 37,172 | −2,008 / 230 / 2,571 | found, not adopted: robust NPV falls (A-r6-105); it does narrow the P90-cost loss (low case −2,958 → −2,008) |
| L1, Al-Kharj spur as commuter line | 5,224 (−5,799) | 11,209 (+15) | 41,153 | −8,213 / −5,689 / −3,055 | found, not adopted |
| L1, Al-Kharj spur commuter + non-electrified | 1,867 (−9,156) | 10,171 (−1,024) | 37,020 | −10,187 / −7,635 / −4,996 | found, not adopted |
| **S6-L2** as in R6 | **6,792** | 1,423 | 5,286 | 3,986 / 4,771 / 5,589 | kept: no variant surface (three station additions: no line type, track, electrification or intermediate station); positive at P90 cost in every case |
| **S6-L3** as in R6 | **2,427** | 19,630 | 73,799 | −21,745 / −19,225 / −16,624 | kept |
| L3, Riyadh belt 225 without Al-Muzahimiyah | 1,742 (−684) | 19,479 (−151) | 73,262 | −22,256 / −19,847 / −17,343 | found, not adopted |
| L3, belt 225 non-electrified | −380 (−2,807) | 19,005 (−626) | 71,309 | −23,742 / −21,183 / −18,645 | found, not adopted |
| L3, belt 225 non-electrified and without Al-Muzahimiyah | −1,040 (−3,466) | 18,854 (−776) | 70,773 | −24,242 / −21,777 / −19,347 | found, not adopted |
| L3, Al-Kharj non-electrified | −144 (−2,571) | 18,591 (−1,039) | 69,666 | −22,944 / −20,429 / −17,863 | found, not adopted |
| L3, Al-Kharj non-electrified, belt 225 without Al-Muzahimiyah | −806 (−3,233) | 18,441 (−1,190) | 69,129 | −23,442 / −21,037 / −18,568 | found, not adopted |
| L3, both non-electrified | 215 (−2,212) | 17,966 (−1,664) | 67,177 | −21,754 / −19,272 / −16,747 | found, not adopted |
| L3, both non-electrified, belt 225 without Al-Muzahimiyah | −447 (−2,873) | 17,815 (−1,815) | 66,640 | −22,247 / −19,864 / −17,451 | found, not adopted |

The 8 L3 edits that put the Al-Kharj spur on the commuter class were not scored: on L1 the commuter class already costs SAR 5.8 bn of robust NPV (decision recorded in `docs/status/r6v3.md`).

**Final layout set for R7 (unchanged; `scenarios/S6-L1..L3.yaml` not edited):**
- **S6-L2** (cost-robust): Al Jubayl, Dhahran (2030); Duruma (2050). Robust NPV 6,792; positive at P90 cost in every case (3,986 / 4,771 / 5,589).
- **S6-L1** (highest robust NPV): L2 + the Al-Kharj spur (2050). Robust NPV 11,023. **The Al-Kharj spur's P90 cost risk, explicitly:** L1's capex P90 is 41,304 against L2's 5,286 (the spur adds about SAR 36 bn at P90 against about SAR 9.8 bn at P50, layout differences), and at P90 cost L1 turns negative in the low and medium cases (−2,958 / −724; high +1,631) while L2 stays positive (+3,986 / +4,771 / +5,589). The difference between S6-L1 and the same layout without the spur (L2) is SAR 4,231 m of robust NPV (L1 − L2): a difference between layouts, not an additive share (the spur alone over S1 scores 4,309, `runs/r7/corridors/S3-branch_spur-al-kharj@2050/score.json`). Non-electrification of the spur reduces the P90 loss (low −2,008) but lowers the robust NPV, so it is not adopted; it is a design option for R7 to keep in view.
- **S6-L3** (reach alternative): robust NPV 2,427, negative at P90 cost in every case and at 30 years or flat 5 %/7 % (§0.1).

## 1. Method

### 1.1 The judge (locked)
- `judge/v2-p5b` is a read-only copy of the R5 demand model and appraisal (commit 7606b43, SHA-256 `2bdee7f5…`), with the CP6 P5b zone split and the post-split calibration re-fit (`docs/r6/judge-backtest.md`). It was back-tested first: the R5 code reproduces S0, S1 and two single-corridor cases with **zero** difference (270/270 figures).
- A layout = S1 plus any set of the 71 searchable corridors (the 72 costed R5 corridors less the Jubail Industrial City station, CP6 P6a), each with a phase (2030/2035/2040/2050) and optional variant fields (line type, track, electrification, dropped intermediate stations). The adapter `optimise/layout.py` (frozen inside the judge) calls the R5 functions unchanged: one demand run per phase on the cumulative network, benefits of each phase against the network before it, and one `economics.cba.evaluate` per appraisal context; present values add draw by draw.
- Approved values used unchanged (CP6): VoT PPP central (P2a), the reference-class ridership ratio in every draw (P3a), WEIs indicative and excluded from the score (P4a), one shared Jubail station (P6a), the P9a assumed values, Green Book 2026 rates (D1a), 60-year horizon as the score horizon (A-cba-004 lists 30/40/60).
- **Score** (A-r6-001): robust NPV = min over the UN WPP low/medium/high population cases of P50(PVB) − P50(PVC), 60 years, Green Book 2026, without WEIs. Reported beside it: NPV P10/P50/P90 of the draws, BCR, capex P10/P50/P90 (uplifted, undiscounted), 2050 rail trips and passenger-km, ridership per route-km, accessibility gain (A-r6-007), CO2, and the HHR and Landbridge loads.
- **Hard constraints** (rejected, not penalised): capex P50 ≤ the budget level (A-r6-003: B1 100, B2 250, B3 500 SAR bn); Makkah and Madinah served (always true: HHR is existing); gradient and curve limits of the line type (A-r6-004; every R5 corridor is grade-feasible as routed; a line-type change that the routed alignment cannot carry is rejected); protected areas flagged (WDPA km from the alignment sidecars); each phase deliverable on its own (A-r6-005).

### 1.2 Two engines
- **Classical:** an exact MILP (scipy/HiGHS) maximises robust NPV on the fast model per budget level, and an NSGA-II (own implementation, 80 × 100 generations per restart, seeds 1–5, A-r6-013) finds the three-objective front (robust NPV, capex, accessibility gain at 60 min) per budget level, stopping when the front does not move over 2 restarts.
- **Autoresearch loop:** the builder edits `scenarios/candidate.yaml` one change at a time with a one-line hypothesis; `uv run python -m optimise.search try --hypothesis "..."` screens it in fast mode, then scores it with the full judge; it is kept (and committed) if robust NPV improves or the point is non-dominated among kept layouts, otherwise the file is reverted. Every attempt is a row of `runs/r6/results.tsv`. The GA's front seeds the loop; the loop's kept layouts seed a second GA round.
- **Fast mode** (A-r6-006): the sum of the single-corridor full-judge scores at each corridor's phase (library `runs/r6/library/`, 73 judge runs), accessibility as the union of single-corridor reach sets. Every kept or front layout is re-scored by the full judge before it counts; the fast-vs-full rank correlation is reported.

## 2. Comparison with S1–S5 (full judge, every corridor of the family at 2030; `runs/r6/compare/`)

| Layout (vs S1) | Corridors | Robust NPV | Capex P50 | Reach gain, 120 min door to door from the five metros |
|---|---|---|---|---|
| S1 committed programme vs S0 (R5, medium, NPV P50 of draws) | 3 lines | −60,103 (R5, `runs/cba/CBA-S1-committed-programme`) | ≈ 101,508 (P50 uplifted, sum of the three line runs) | — |
| S5 family (all station additions) | 9 | −1,174 | 6,745 | 3.60 M |
| S3 family (all spurs) | 19 | −308,853 | 248,441 | 0.41 M |
| S4 family (all belts) | 20 | −405,554 | 203,343 | 2.27 M |
| S2 family (all trunk gaps) | 23 | −957,580 | 761,974 | 0.36 M |
| **S6-L1** | 4 | **11,023** | 11,194 | 3.56 M |
| **S6-L2** | 3 | **6,792** | 1,423 | 3.56 M |

Whole families at 2030 are far below the optimised layouts; even the S5 family turns negative once the four Al-Ahsa stations, Az Zulfi and Thuwal are included at 2030.

## 3. Engines and search record
- `runs/r6/results.tsv` (5,252 rows): MILP 9 (6 + 3 holdout), GA fronts 5,183 rows (20 runs: B1/B2/B3 × seeds 1–5, B1/B2 seed 6 seeded with the agent's kept layouts, B1/B2/B3 seed 1 holdout), 14 GA re-scores, 4 family and 5 top-5 full scores, and the agent loop: 18 attempts (seed + 17 edits): 9 kept, 6 reverted by the full judge, 2 reverted by the fast screen, 1 judge error (variant, see limits). Per-evaluation cost: judge runs are local compute (USD 0); agent edits are in-session turns of the builder (the optimiser track; "in-session", included in the run total of `docs/cost-log.md`).
- GA fronts: B1 198 points in every seed; B2/B3 289–293. The seeded round (seed 6) added no non-dominated point (front unchanged), so the GA stop rule was met. The agent loop stopped after 17 edits on the phase budget guard (cost of the run near the USD 95 phase estimate by the builder's judgement; the measured total is the run row the orchestrator appends to `docs/cost-log.md`); its last two edits were kept as non-dominated points without improving the best robust NPV, and the 20-non-improving rule was not reached (the GA front had already stopped moving).
- Judge integrity: fingerprint checked before every judge call; full SHA-256 identical at the start and end of the library, every GA run and the re-score (`runs/r6/library/library.json`, `runs/r6/ga/*/info.json`, `runs/r6/rescore/rescore.json`): `2bdee7f5…`.
- **R6_V3 search record (judge v3, `runs/r6/v3/results.tsv`, 47,108 rows):** 5 back-test re-scores; 144 stage-1 variant library rows (the 73 base re-runs are recorded in `runs/r6/v3/library/library.json`); MILP 6 (3 with variants, 3 without); NSGA-II fronts 46,914 rows (15 runs, B1/B2/B3 × seeds 1–5, all stopped on the 30-restart cap, A-r6-106); 29 full-judge re-scores (21 front points and 8 R6 agent-kept layouts; the MILP layout and the ninth agent-kept layout are both S6-L1, already a B1 front point); 10 CP7 variant edits on L1 and L3. Every v3 judge run meta records `judge v3-variants @ 017234562c sha256 d9fef643…`; full SHA-256 identical at the start and end of the library (`runs/r6/v3/library/library.json`, `variants-stage1.json`, `variants-stage2.json`), the MILP (`runs/r6/v3/milp/info.json`), every GA run (`runs/r6/v3/ga/*/info.json`) and the re-score (`runs/r6/v3/rescore/rescore.json`). Commands: `uv run python -m optimise.variants enumerate | library --stage 1|2 | milp | ga --budget <B> --seed <s> | rescore | backtest`; `uv run python -m optimise.report_v3 cp7 | top5`; shell drivers in `logs/r6v3/*.sh` (gitignored).

## 4. CP6 P5b: the affected S5 cases before and after the zone split (medium, 60 y, GB2026; NPV P10 / P50 / P90 of the draws)

| Case | R5 (one Al-Ahsa zone, one Jubail zone) | R6 judge v2 (split zones, re-fitted constants) | R6 robust NPV |
|---|---|---|---|
| Al-Jarn | −2,447 / −1,237 / −706 | −2,241 / −1,097 / −651 | −1,050 |
| Al-Oyun | −2,447 / −1,237 / −706 | −2,380 / −1,189 / −688 | −1,133 |
| Al-Qarah | −2,447 / −1,237 / −706 | −1,609 / −521 / −269 | −541 |
| Al-Umran | −2,447 / −1,237 / −706 | −1,664 / −565 / −329 | −585 |
| Al Jubayl | 1,601 / 5,999 / 14,439 | 1,359 / 5,369 / 12,984 | 4,982 |
| Jubail Industrial City | 952 / 4,210 / 10,353 | 1,269 / 5,105 / 12,372 | 4,735 |
| Both Jubail stations | 712 / 5,196 / 13,641 | 523 / 4,689 / 12,439 | 4,502 |

With their own zones the four Al-Ahsa stations are no longer identical, but all four stay negative at every phase. One shared Jubail station (Al Jubayl) still beats two stations (P6a holds).

## 5. Sensitivities and overfitting
- Population: the robust case is always UN WPP low; on the held-out high case two of the top-25 holdout layouts drop more than 5 places (the single Al Jubayl station, 7 places, and the empty layout, 6), both overtaken by multi-station layouts; nothing else moves more than 5.
- Cost: the held-out P90-cost test flags 7 of the top-25 holdout layouts (rank drop 7–13 places, `runs/r6/holdout.csv`), every one containing the Al-Kharj spur (with the Riyadh belt 225, the Dammam belt 315 or Thuwal in five of them); the station-only layouts move up (9 of 25 flagged in total with the two above). Read with care: the fast-mode P90 sums corridor P90s (comonotonic draws), a cautious bound; the full-judge P90-cost figures for the top 5 are in §0.1.
- Rates and horizons (§0.1 last row): L1 and L2 stay positive under every rate case and horizon; L3 is negative at 30 years and at flat 5 %/7 %.

## 6. Limits (scenario comparison on a modelled demand base, not a forecast)
- Synthetic demand, uncalibrated beyond the three 2025 totals; resident trips only (international visitors carry no user benefits, CP6 P8a); not monetised: freight, reliability, Jeddah decongestion (P8a).
- ~~Variants were not searched~~ (R6 v1.0): closed by R6_V3 (CP7-3): judge v3 fixes the variant id and the variants are searched (§0.2). What stays limited: **track** has no term in the frozen cost or demand model (costs per double-track-equivalent km; headways from the line type), so single track scores the same as double and was not searched (A-r6-102): a single-track saving or capacity limit needs a model change, not a search; line types are limited to the classes the routed alignment can carry (A-r6-004: no corridor can take HSR as routed, and no commuter belt can move up a class); stations are only dropped one at a time; electrification is a cost-and-energy switch only (no running-time difference between electric and diesel stock in the model).
- **The v3 GA did not converge by the R6 rule:** every run stopped on the 30-restart cap with the front still moving (A-r6-106); its maximum (S6-L1) is proven by the MILP, and the reach end is where the front still moves. The full-judge re-score covers a selection (A-r6-107), not every front point.
- Sub-run metas (`A-cba/meta.json` of the back-test part A and `variants/*/cost/meta.json` of the variant costings) record the worktree's `git describe`, because the judge copy sits inside the worktree; the code that ran is the frozen judge's, recorded by the enclosing run meta (`judge v3-variants @ 017234562c`).
- Agent-proposed new links were not attempted (they need routing on the DEM through `network.align` and new station skims before the judge can score them).
- The fast mode ignores corridor interactions (competing lines): it overstates NPV by up to 17 % of capex, but never changed a rank among the re-scored layouts.
- Phasing is a construction-start convention (A-r6-002) with a drawn construction duration; it is not a real-options stage-gate model (W9 sequencing under observed demand is for R7/R8 if wanted).
- Accessibility counts 2025 residents within 120 door-to-door minutes of five metro stations; it says nothing about other cities (e.g. trunk gaps between regional cities score zero on it). Since R6_V3 the **national reach** (any station, door-to-station; A-r6-104) is reported beside it as a column only (CP7-5); it measures access to the network, not where people can travel to within the time.
- CO2 is reported as the PV of the carbon benefit stream (SAR m), not in tonnes.

## 7. Checkpoint decisions (R6 checkpoint, closed at CP7 by Tariq, 3 Nov 2026; `docs/STATUS.md` "CP7 decisions")
1. **Layouts to R7 (CP7-1):** S6-L2 (cost-robust) and S6-L1 (highest robust NPV, with the Al-Kharj spur's P90 cost risk carried explicitly), S6-L3 as the reach alternative; L4/L5 trade-off only. After judge v3: unchanged (§0.2).
2. **Budget levels (CP7-2):** B1/B2/B3 = SAR 100/250/500 bn approved (A-r6-003 → approved).
3. **Judge v3 (CP7-3):** approved and done in R6_V3: variant-id fix, new hash `d9fef643…`, library and top layouts re-run, variants searched; no layout change (§0.2).
4. **Re-fit and international share (CP7-4):** the post-split re-fit (A-r6-011 → accepted) and the international share below its range (D-r6-04) accepted; H3a carried to R8 reporting.
5. **Accessibility metric (CP7-5):** the five-metro 120-min band stays the score (A-r6-007); the national reach is a reported column only (A-r6-104; §0.1).
6. **New links (CP7-6):** no agent-proposed new links for now.
