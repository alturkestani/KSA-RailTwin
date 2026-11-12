---
name: pareto-optimizer
description: The W9 multi-objective optimisation and phasing method: objectives, decision variables, NSGA-II (pymoo) versus epsilon-constraint (OR-Tools/HiGHS) and how to justify the choice, p-median station siting with a through-passenger time penalty, real-options stage-gates for sequencing, the robustness metric and the output format. Use for R6 and for any siting or programme-selection question.
---
> **Document version:** skills/pareto-optimizer/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Pareto optimisation and phasing

## Objectives (maximise unless stated; all from `runs/` outputs, never typed in)
`npv_p50` and `bcr_p50` (from `economics.cba`), `coverage_population` and `coverage_jobs` (people and jobs within the 60-minute isochrone of a station, from `access`), `regional_balance` (e.g. 1 − Gini of per-capita accessibility gain across the 13 regions), `emissions_reduction_tco2_yr`; minimise `fiscal_exposure_p80` (from `funding.exposure`) and `downside_risk` (P10 NPV shortfall).

## Decision variables
Binary build/no-build per corridor (from the S2–S5 families); alignment option index per corridor; technology per corridor (`hsr` / `conventional_passenger` / `upgrade` / `mixed`); station set per corridor (p-median choice among candidate station sites); service pattern (`express` / `skip_stop` / `all_stop`) and frequency level; fare level index; phase (build year bucket: 0–5, 6–10, 11–15, defer).

## Method choice (justify in `docs/optimisation.md`)
- **NSGA-II via `pymoo`** when the evaluation is a black box (CBA Monte Carlo per candidate programme) and the variable space is mixed-integer: population size, generations, seed, and evaluation count recorded; surrogate or cached evaluations allowed with the cache keyed by (variables, seed).
- **Epsilon-constraint with OR-Tools / HiGHS / CBC (MILP)** when objectives are linear in build decisions (coverage, capex) and constraints are budget envelopes; exact fronts for small problems.
- Use both where feasible and show that the fronts agree on the small problem; report the one used for the full problem and why.
- Budget envelopes: a set of capex caps (registered assumption `A-opt-001`) producing one Pareto set each.

## Station siting
p-median on the candidate station sites along an alignment: minimise population-weighted access time subject to a through-passenger penalty (minutes per stop from the running-time model, `isochrone-commute`) times through demand; the penalty is explicit in the objective and reported per added stop.

## Sequencing as real options
Stage-gates every 5 years: `build`, `expand`, `defer` triggered by observed demand and population thresholds (A-opt-002); evaluate the policy tree under the W8 population and giga-project scenarios and the W3/W4 Monte Carlo draws; value of waiting reported as the NPV difference between the committed programme and the staged programme.

## Robustness
For the recommended programme: the share of Monte Carlo draws (≥ 1,000) in which it stays within 5 % of the Pareto-optimal NPV at its budget envelope (A-opt-003 for the 5 %); regret relative to the best programme per draw (mean, P90).

## Commands and outputs
`uv run python -m optimise.pareto run --config cities/ksa/optimise/<name>.yaml --seed 1 --out runs/optimise/<name>/` writes `front.parquet` (one row per non-dominated programme with every objective and the variable vector), `front.png` per objective pair, `recommended.yaml` (programme, phases, robustness, regret), `dominated.md` (why each dominated option lost), `meta.json`. `uv run python -m optimise.siting --corridor <id> --p <n> --seed 1` writes the station set and the per-stop penalty table.

## Rules that bite
- Fronts, not a single answer: the report shows the trade-off charts; "recommended" always carries its budget envelope and robustness.
- Every evaluation uses the same seed set as the CBA so results are reproducible; `meta.json` records evaluation count and runtime.
- Expected runtime over 90 minutes needs the smaller-sample run first (CLAUDE.md).
