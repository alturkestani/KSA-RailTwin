> **Document version:** docs/report/sections/00-front-matter.md v1.2 | 12 Nov 2026 | Author: report-writer; FIX_R8 (v1.1: neutral framing of the study question, R8-checkpoint review item 7); PUBLISH_PREP (v1.2: public-release banner, CP7 item 6) | Status: reviewed

# 0. Front matter

**KSA Rail Twin: a national, investment-grade economic feasibility study of a Saudi rail network.** Milestone R8 deliverable, reviewed by the author at checkpoint CP6 and prepared for public release at checkpoint CP7. It is an independent simulation on synthetic, uncalibrated demand: not a government plan, and not endorsed by any agency, operator or company. The author decides when it is published.

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

## 0.1 Scope

The study compares options for extending Saudi Arabia's rail network: which corridors, in what order, at what cost, with what long-term benefit, funded and owned by whom, and with what effect on people. It covers all 13 regions and all 150 GASTAT governorates (coverage audit `docs/coverage.md`, GASTAT Census 2022[^S-cp2-gastat-007]), the committed programme (S1: the Landbridge, the Riyadh Rail Link and the Saudi GCC section, each "announced/planned" with its source) and every generated corridor family (S2 trunk gaps, S3 branches and spurs, S4 commuter belts, S5 station additions), appraised against the matched baseline (runs/cba/CBA-S1-committed-programme for S1 against S0; S1 for everything else).

The simulation is the tool; the decision case is the product. The report gives options and evidence. It does not advocate for any entity, body, firm or programme, and Vision 2030 alignment appears only as a qualitative scorecard (`docs/cba-scorecard.md`), not as an argument.

## 0.2 The three rail layers

Every map, table and figure keeps three layers apart: **existing** (lines in service, from OpenStreetMap and published operator facts), **committed / under procurement** (announced or planned lines, never shown as existing; each with a source and date) and **hypothetical (ours)** (every corridor this study generated). Maps carry the OpenStreetMap credit (ODbL) and the layer legend.

## 0.3 How to read the figures

- **Labels.** Every modelled output carries the two labels printed above. The first says the demand is synthetic and uncalibrated beyond three 2025 totals, so results compare scenarios and are not forecasts. The second says the routed alignments are indicative sketches; lengths, costs and running times built on them inherit that uncertainty (`docs/alignments.md` §0).
- **Model language.** The report writes "in the model, X is reduced by …", never as a prediction of what a line does in reality.
- **Ranges.** Costs and benefits are P10 / P50 / P90 ranges over 10,000 Monte Carlo draws (seed 1), never single points (runs/r6/top5/top5.csv; runs/cba/summary.parquet). P10 is the value that 10 % of the draws fall below, P50 the median, P90 the value 90 % of draws fall below. A wide range is a finding, not a defect.
- **Robust NPV.** The score used to rank layouts is the worst of the three UN WPP population cases (low, medium, high) of P50 benefits minus P50 costs, 60 years, Green Book 2026 declining rate (A-r6-001, A-cba-001). "NPV at P90 cost" replaces P50 costs by P90 costs: the held-out cost-risk test.
- **Phase years.** 2030, 2035, 2040 and 2050 are the optimiser's phase years; construction starts three years earlier (2027, 2032, 2037, 2047; A-r6-002) and the opening year is drawn from the reference-class schedule distribution. A stage-gate falls before construction, so the gate for a 2050 phase is in 2047.
- **Money.** SAR million at 2025 prices, present value at 2026, unless a table says otherwise (A-cost-001, A-cba-301). Rounding: whole SAR million in tables; BCRs to two decimals; every figure is rounded half away from zero from the run file (so 2,426.50 prints as 2,427), and no rounding changes a sign or a ranking.
- **Provenance.** Every number carries a source footnote `[^S-…]` (resolved in the source notes and in Annex S), an assumption id `A-…` (Annex A) or a run path `runs/…` with its `meta.json` (seed, config hash, data hash, code version). Every R6/R7 figure comes from the frozen judge v3 (`v3-variants`, SHA-256 `d9fef643…`, `docs/r6/judge-hashes.md`), seed 1, with the frozen alignment weights v1 (`align_weights.yaml`, hash `2b718ecb…`).

## 0.4 Decision framing used throughout

- **S6-L2** (the three station additions) is the **central case**.
- **S6-L1** (S6-L2 plus the Al-Kharj spur in phase 2050, construction from 2047 by A-r6-002) is the **upside case that carries the Al-Kharj spur's P90 cost risk**: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
- **S6-L3** is the **reach alternative**.
- All three are presented **against S1**, the committed programme (runs/cba/CBA-S1-committed-programme).
- Two further layouts from the optimisation appear only as trade-off illustrations on the Pareto and reach figures (§4.6); they carry no recommendation, delivery model or stage-gate.

## 0.5 Independence

This is a personal, open-source, non-partisan study. It uses only public, licence-compatible data and open-source tools (licence and openness register `docs/licences.md`). Naming a public body (for example the state rail company, the Transport General Authority, the National Center for Privatization or the Ministry of Finance) states a legal or institutional fact with its source; it is not an endorsement. Delivery-model findings are the analyst's judgement of the best fit given the evidence, set out side by side with the alternatives.
