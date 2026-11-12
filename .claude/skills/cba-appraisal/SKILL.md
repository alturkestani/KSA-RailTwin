---
name: cba-appraisal
description: The W4 appraisal method: named standards (HMT Green Book, DfT TAG incl. A2.4 wider impacts, EU CBA Guide 2014, World Bank, any Saudi guidance), 30/40/60-year horizons with residual value, social, commercial and declining discount rates, the benefit list with the no-double-counting rule, NPV/BCR/EIRR/FIRR/payback/fiscal cost, Monte Carlo P10/P50/P90, tornado charts and switching values, and the CBA case YAML schema. Use for every corridor family and programme appraisal.
---
> **Document version:** skills/cba-appraisal/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Cost-benefit appraisal

Rule 6: every scenario is appraised against a matched baseline on the same zones, seed and parameters, following a named standard and stating every departure.

## Standards (cite the edition read, `S-xxx`)
HM Treasury Green Book (current edition) and its discounting annex; DfT Transport Analysis Guidance (TAG) units A1 (cost-benefit), A2.4 (wider economic impacts), A3 (environmental), A4 (social and distributional); EU Guide to Cost-Benefit Analysis of Investment Projects 2014; World Bank transport appraisal guidance; Saudi guidance (SAR, MEP, GAMEP/NCEC, Vision 2030 programme documents) if any is published — else write "none found, <date>". `docs/cba.md` opens with a "departures from the standard" table.

## Case schema (`CbaCase` in `common/schemas.py`; fixture `tests/fixtures/cba_case.yaml`)
```yaml
id: CBA-S3-asir-spur
scenario: S3            # scenario-yaml id
baseline: S1            # matched baseline
horizon_years: [30, 40, 60]
residual_value: {method: straight_line_remaining_life, asset_lives: {civil: 100, track: 40, systems: 20, rolling_stock: 30}, source: S-052}
price_year: 2024
currency: SAR
discount_rates:
  social: {rate: 0.035, declining: [[0, 30, 0.035], [31, 75, 0.03]], source: S-050, assumption_id: A-cba-001}
  commercial: {rate: 0.06, source: S-051, assumption_id: A-cba-002}
  sensitivity: [0.02, 0.05, 0.08]
costs: {capex_ref: runs/costs/S3-asir-spur/rcf/, opex_ref: ..., renewals_ref: ..., financing_ref: ...}
benefits:                # each with an assumption/source id and a method key
  travel_time_savings: {by_purpose: true, vot_ref: A-cba-010, rule_of_half: true}
  reliability: {method: tag_a1_3, ref: A-cba-011}
  safety: {method: crashes_avoided_vkt, ref: A-cba-012}
  emissions_air_quality: {method: carbon_values_and_pollutants, ref: A-cba-013}
  decongestion: {jeddah: traffictwin_coupling, elsewhere: vkt_based, ref: A-cba-014}
  freight_shift: {ref: A-cba-015}
  wider_economic_impacts: {agglomeration: tag_a2_4, report_separately: true, ref: A-cba-016}
  land_value_uplift: {capture_only_if_not_counted_in_time_savings: true, ref: A-cba-017}
  tourism_hajj_umrah_capacity: {ref: A-cba-018}
  regional_development_vision2030: {monetised: false, scorecard: docs/cba-scorecard.md}
monte_carlo: {draws: 10000, seed: 1, inputs: [capex, opex, demand, vot, discount_rate, construction_years]}
```

## No double counting
Travel-time savings and land value uplift measure the same welfare through different channels: report land value only as a capture potential, not as an added benefit. Agglomeration and other wider impacts are reported separately: BCR "without WEIs" and "with WEIs". Decongestion is counted once (Jeddah via TrafficTwin matched-control runs, elsewhere VKT-based; never both for one trip). Freight benefits exclude passenger time savings. The verifier checks the benefit matrix in `docs/cba.md` where every benefit names the channel it uses and the ones it excludes.

## Commands and outputs
`uv run python -m economics.cba run --case cities/ksa/cba/<id>.yaml --seed 1 --out runs/cba/<id>/` writes `results.json` (NPV, BCR with and without WEIs, EIRR, FIRR, payback year, fiscal cost to the state, all as P10/P50/P90 per horizon and discount rate), `tornado.csv/.png`, `switching_values.json` ("demand must be X % of forecast for BCR = 1"; capex, VoT, discount-rate switching values), `draws.parquet`, `meta.json`. `uv run python -m economics.cba report --run runs/cba/<id>/` renders the Markdown section for `docs/cba.md`.

## Rules that bite
- Ranges only; no single-point NPV anywhere. Label every table "synthetic demand, uncalibrated: scenario comparison, not a forecast".
- Value of time for KSA is an assumption (A-cba-010) with the range and the literature used; say so in the report.
- Declining long-term rates follow the Green Book schedule; cite it.
- Capex enters uplifted (`reference-class-forecasting`), never as the base estimate.
