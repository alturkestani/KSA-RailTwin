---
name: scenario-yaml
description: Schema and conventions for scenario files scenarios/S0..S6*.yaml in TrafficTwin policy-yaml style (identity, layer set, lines included, population scenario, cost and benefit references, matched baseline, seed, sensitivity band) and their validation. Use when creating, validating or running any scenario.
---
> **Document version:** skills/scenario-yaml/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Scenario YAML

All files validate against `Scenario` in `common/schemas.py`: `uv run python -m common.scenarios validate scenarios/` must pass. Rule 6: every scenario names its matched baseline and is run on the same zones, seed and parameters; every result carries a sensitivity band.

## Fixed scenarios (PROJECT.md section 6)
| id | kind | content |
|---|---|---|
| S0 | baseline_today | existing lines incl. the Riyadh Metro |
| S1 | baseline_committed | S0 + Landbridge (with its planned stations) + Riyadh Rail Link + the Saudi GCC section |
| S2 | family_trunk_gaps | generated (e.g. Jeddah–Riyadh HSR vs the S1 mixed line) |
| S3 | family_branches_spurs | generated |
| S4 | family_commuter_belts | generated, one per metro |
| S5 | family_station_additions | generated |
| S6-<envelope>-<model> | optimised_programme | from `optimise.pareto`, one per budget envelope and delivery model |
Generated families hold many candidates: `scenarios/S3.yaml` lists `candidates:` with one entry per corridor file (`corridor-generator`), and the runner evaluates each against the baseline.

## Schema
```yaml
id: S3
kind: family_branches_spurs          # baseline_today | baseline_committed | family_* | optimised_programme | sensitivity
title: "Branches and spurs to economic nodes"
layers: [existing, committed, hypothetical]   # which line layers are active
baseline: S1                           # matched baseline id (S0 for S1; null only for S0)
lines:                                 # fixed lines by id (line-yaml); families add candidates
  include: [sar-north, sar-east, hhr-haramain, riyadh-metro, landbridge, riyadh-rail-link, gcc-saudi]
candidates:                            # families only
  - cities/ksa/corridors/branch_spur/S3-asir-abha-khamis-spur.yaml
population_scenario: cities/ksa/population/un_wpp_medium.yaml   # also run against low/high and the giga-project add-on
gigaproject_addon: cities/ksa/population/gigaprojects_delivered_50pct.yaml   # or null
demand_params: cities/ksa/assumptions/gravity.yaml
mode_choice_params: cities/ksa/assumptions/mode_choice_priors.yaml
costs: {register: cities/ksa/costs/cost_register.yaml, uplifts: cities/ksa/costs/uplifts.yaml}
appraisal: cities/ksa/cba/template.yaml   # cba-appraisal case template
seed: 1
sensitivity:
  seeds: [1, 2, 3]                     # seed band
  sweep: {vot: [-0.25, 0.25], capex: [-0.2, 0.5], demand: [-0.4, 0.2]}
  population_scenarios: [un_wpp_low, un_wpp_medium, un_wpp_high]
labels: ["synthetic demand, uncalibrated: scenario comparison, not a forecast"]
source: "PROJECT.md section 6; generated candidates from screening.corridors <hash>"
```

## Runner
`uv run python -m common.scenarios run S3 --seed 1 --out runs/scenarios/S3-s1/` (R4 onwards) orchestrates skims → demand → mode choice → access → costs → CBA for each candidate against the baseline and writes `summary.parquet` (one row per candidate × population scenario × seed with every KPI as P10/P50/P90), `diff/` (candidate minus baseline on the shared zones), `meta.json` (seed, config hash, manifest hash, code version).

## Rules
- A scenario never edits a line file; it references them. A scenario never carries a number that belongs in a register.
- Layer discipline: a committed line may not appear in `S0`; a hypothetical line may not appear in `S0` or `S1`.
- Difference mode in the dashboard reads `diff/`, so every candidate must be run against the matched baseline with identical zones and seed.
- Sensitivity bands are mandatory in every table derived from a scenario run.
