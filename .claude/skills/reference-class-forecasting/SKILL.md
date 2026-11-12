---
name: reference-class-forecasting
description: Applying reference-class forecasting and optimism-bias uplifts (Flyvbjerg reference-class literature, UK Green Book supplementary guidance) to rail capex, schedule and ridership, reporting P50 and P80 budgets and overrun distributions, and where the uplift tables live. Use whenever a cost, schedule or demand figure leaves the register and enters an estimate, a CBA or a report.
---
> **Document version:** skills/reference-class-forecasting/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Reference-class forecasting

Every base estimate is optimistic until proven otherwise. The method: place the project in a reference class of comparable completed projects, take the empirical distribution of outcome/estimate ratios, and read the uplift needed for the chosen confidence level.

## Sources to read and cite (verify, then record `S-xxx`)
- Flyvbjerg, Holm and Buhl, "Underestimating Costs in Public Works Projects", JAPA 2002; Flyvbjerg, "From Nobel Prize to Project Management: Getting Risks Right", 2006; Flyvbjerg et al. on rail ridership forecasts (inaccuracy in traffic forecasts, 2005). Record the exact figures the papers give for rail (cost escalation mean and sd; ridership shortfall), never from memory.
- HM Treasury Green Book, supplementary guidance on optimism bias (the Mott MacDonald study and the uplift tables by project type and appraisal stage, with the percentages for rail at outline business case).
- Any later reference-class datasets found (e.g. Flyvbjerg's database papers, ITF/OECD reviews, EU Court of Auditors HSR report). Grade evidence per `benchmark-dossier`.

## Uplift table `cities/ksa/costs/uplifts.yaml`
```yaml
- id: U-capex-hsr-obc
  applies_to: capex
  line_type: hsr
  stage: outline_business_case       # strategic | outline_business_case | full_business_case
  distribution: lognormal             # lognormal | empirical | triangular
  params: {median_ratio: 1.00, p80_ratio: 1.45}   # outcome / base estimate
  source: S-040
  status: sourced
  assumption_id: A-rcf-001
- id: U-ridership-hsr
  applies_to: ridership
  distribution: empirical
  samples_source: S-041               # table of outcome/forecast ratios
```
Every uplift is a registered assumption (`A-rcf-nnn`); choosing a stage is itself an assumption.

## Procedure
1. `uv run python -m costs.rcf apply --estimate runs/costs/<corridor>/base.yaml --uplifts cities/ksa/costs/uplifts.yaml --seed 1 --draws 10000 --out runs/costs/<corridor>/rcf/` draws capex, schedule and ridership multipliers and writes P10/P50/P80/P90 plus the full distribution (Parquet).
2. Report **P50** (median budget) and **P80** (budget with 80 % confidence) for capex; schedule overrun distribution in months; ridership as a shortfall distribution applied to the W8 demand.
3. Combine in the CBA Monte Carlo (`cba-appraisal`) — the same draws, so cost and demand uncertainty are not double-applied.
4. In every table: "base estimate", "P50 (uplifted)", "P80 (uplifted)", with the uplift id.

## Rules that bite
- Never present the base estimate alone; never present a single point.
- KSA-specific evidence (Haramain cost history, Riyadh Metro, SAR lines) is used to check whether the global reference class fits; if the KSA outcomes differ, say so and keep both.
- Ridership uplifts are negative (shortfall); document that the demand model's output is itself "synthetic, uncalibrated".
