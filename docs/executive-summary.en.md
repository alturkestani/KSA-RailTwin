> **Document version:** docs/executive-summary.en.md v0.7 | 12 Nov 2026 | Author: PUBLISH_PREP (v0.7: public-use banner, native Arabic review pending, CP7 item 6); R9 (v0.6: banner: the Arabic summary reviewed on Tariq's request and signed off for internal use; CP6 draft note dropped; body unchanged); report-writer (v0.2: phase vs construction years, verify-R8); FIX_R8 (v0.3: unit on the spur figure, R8-checkpoint review item 3; v0.4: spur figure as a layout difference, five-metro reach qualifier, item 9); R8_L6_PANEL (v0.5: S6-L6 comparison sentence) | Status: reviewed

# KSA Rail Twin: executive summary

An independent, non-partisan feasibility study of additions to the Saudi rail network: a simulation on synthetic, uncalibrated demand, not a government plan. Reviewed on Tariq's request on 7 Nov 2026 together with the Arabic summary, and prepared for public release with the repository on 12 Nov 2026; a native Saudi review of the Arabic text is still pending, and where the two texts differ in meaning, the English text and the registers govern. The Arabic summary (`docs/executive-summary.ar.md`) has the same structure and the same figures.

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

**Reading the figures.** Every result is "in the model": a comparison of scenarios on synthetic, uncalibrated demand, not a forecast. Money is SAR million at 2025 prices, discounted to 2026 on the Green Book 2026 schedule[^S-cp1-060] over 60 years (A-cba-001, A-cba-004). Programme figures come from the frozen appraisal model, judge v3 (`d9fef643…`, `docs/r6/judge-hashes.md`), seed 1, 10,000 draws, as P10 / P50 / P90 ranges. "Robust NPV" is the NPV at median cost in the worst of three population cases.

## 1. The question

The committed programme (S1: the Landbridge and its Riyadh section, and the Saudi section of the GCC Railway, all announced/planned or under procurement[^S-054][^S-r1a-055][^S-029]) is the baseline. The question is which additions to it hold up once cost overruns, weak demand and different appraisal values are allowed for, and who carries the fiscal exposure. In the model S1 itself has an NPV of −337,555 / −60,103 / 11,607 SAR m (P10 / P50 / P90) against today's network (medium population; `runs/cba/CBA-S1-committed-programme`).

After screening every region and governorate and searching the combinations of the 71 searchable corridors (`runs/r6/library/`), three options are put forward, each against S1. None is a recommendation to build.

## 2. Three options against the committed programme

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

| option (judge v3, seed 1; `runs/r6/top5/top5.csv`) | capex P10 / P50 / P90, SAR m | robust NPV | NPV at P90 cost, low / medium / high | BCR P10 / P50 / P90, medium |
|---|---|---|---|---|
| S6-L2, central case | 801 / 1,423 / 5,286 | 6,792 | 3,986 / 4,771 / 5,589 | 1.52 / 5.96 / 22.23 |
| S6-L1, upside case (carries the spur's P90 cost risk: NPV at P90 cost −2,958 / −724 / +1,631) | 6,233 / 11,194 / 41,304 | 11,023 | −2,958 / −724 / +1,631 | 0.60 / 2.33 / 9.33 |
| S6-L3, reach alternative | 10,684 / 19,630 / 73,799 | 2,427 | −21,745 / −19,225 / −16,624 | 0.32 / 1.12 / 3.48 |

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

Source: `runs/r6/top5/top5.csv`. S6-L1 carries the Al-Kharj spur's P90 cost risk: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv. Figures: `report/figures/fig05-programme-npv-ranges.svg`, `report/figures/fig06-l1-p90-cost-risk.svg`.

- **S6-L2, the central case:** three new stations, Al Jubayl and Dhahran (2030) and Duruma (2050), on lines that exist or are committed; 2030 and 2050 are phase (opening) years, with construction from 2027 and 2047 (A-r6-002). In the model it is the only top layout that stays positive with every cost at its P90 in every population case.
- **S6-L1, the upside case, which carries the Al-Kharj spur's P90 cost risk:** S6-L2 plus the Al-Kharj spur (2050). It has the highest robust NPV found (the difference between S6-L1 and the same layout without the spur is SAR 4,231 m of robust NPV; that layout is S6-L2), but at P90 cost it turns negative in two of three population cases (NPV at P90 cost −2,958 / −724 / +1,631 SAR m, low / medium / high; `runs/r6/top5/top5.csv`).
- **S6-L3, the reach alternative:** the two 2030 stations, the spur and a Riyadh commuter belt. It brings 4.25 M people within 120 minutes door to door from the five metros (S6-L1, which carries the spur's P90 cost risk: 3.56 M) at the price of a lower robust NPV, and it is negative at P90 cost in every population case.

Layouts S6-L4 and S6-L5 appear only as illustrations of the reach trade-off, with no recommendation (`report/figures/fig08-reach-tradeoff.svg`).

Layout S6-L6 is a comparison layout, not the recommended programme: the smallest-capex set of library corridors that joins the network into one connected rail system (16 options, capex P50 SAR 227,213 m). In the model it adds the most rail trips and the widest national reach (reported only, not a score) of the six layouts but the least reach from the five metros, for a robust NPV of −191,660 SAR m (`runs/r6/l6/score/S6-L6.csv`; `report/figures/fig16-l6-connected-map.svg`).

## 3. Who pays

In the model no option pays for itself: fares cover only part of operating and renewal costs, so the state pays under every delivery model. Fully public delivery is cheaper in expected present value than an availability PPP for every option and across every registered parameter range (value for money of the PPP: −894, −5,124 and −8,779 SAR m for S6-L2, S6-L1 and S6-L3; `runs/r7/vfm/vfm.json`). S6-L1 carries the Al-Kharj spur's P90 cost risk here too (NPV at P90 cost −2,958 / −724 / +1,631 SAR m; `runs/r6/top5/top5.csv`). The 60-year net fiscal cost under public delivery is 695 / 1,283 / 4,088 SAR m for S6-L2 and 4,676 / 8,441 / 23,615 SAR m for S6-L1 (low population case; `runs/r7/fiscal/fiscal.json`). Under a PPP the state keeps the cost tail above the private cushion as a contingent liability. The finance premium in this test rests on a UK reference class[^S-fund-r7-001].

## 4. The three biggest uncertainties

1. **Capital cost.** The Al-Kharj spur (`runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json`) switches to a benefit–cost ratio below 1 at 9 % above the median of its uplifted cost (capex multiplier 1.09); the Dhahran and Al Jubayl stations tolerate multiples of theirs.
2. **Demand.** Demand is synthetic; the spur needs 66 % of the modelled demand and Duruma 52 %, while the committed programme needs 163 %.
3. **Appraisal values.** No Saudi value-of-time study was found in the sources read; the spur needs at least 0.85 times the central value of time and a real discount rate below 3.03 %.

Switching values: `runs/cba/<case>/switching_values.json` (standalone appraisal, medium population, 60 years). Figure: `report/figures/fig14-tornado-switching.svg`.

## 5. Open questions and limits

Of 16 legal and institutional items reviewed (`cities/ksa/funding/recommendations.yaml`), 13 remain unclear, among them who sets passenger fares, how rail debt and PPP commitments are reported, the role of PIF, and whether a station can be added within a host line's procurement. Each is kept as an open question, with no legal position inferred; all 13 are listed in `docs/policy-brief.md` §7 and `docs/delivery-models.md`.

Alignments are indicative sketches; wider economic impacts, freight and foreign visitors are outside the rankings. Stage gates before each construction start (`report/figures/fig09-stage-gates.svg`) mark where the choice can be revisited with a fielded survey and observed demand.

[^S-cp1-060]: HM Treasury, The Green Book (2026); verified, accessed 2026-10-31 (`docs/sources/index.csv`).
[^S-054]: MEED, "Saudi Landbridge rail scheme to be delivered by 2034", 2026-01-21; secondary, accessed 2026-10-30.
[^S-r1a-055]: MEED, "Contract award nears for Saudi Landbridge Riyadh section", 2026-08-31; secondary, accessed 2026-10-31.
[^S-029]: MEED, "Saudi Arabia tenders GCC rail link from Kuwait to UAE border", 2026-05-12; secondary, accessed 2026-10-30.
[^S-fund-r7-001]: National Audit Office (UK), PFI and PF2, HC 718, 2018-01-18; verified, accessed 2026-11-04.
