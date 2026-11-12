---
name: screening-funnel
description: The W2 screening funnel from all settlements to a long list (transparent filters) to a short list (weighted multi-criteria score with explicit weights, a ±25 % sweep and rank stability), the default criteria to be approved at CP1, the structure of docs/screening.md and the one-row-per-governorate coverage table docs/coverage.md. Use when merging region registers, scoring candidates or writing the coverage audit.
---
> **Document version:** skills/screening-funnel/SKILL.md v1.5 | 31 Oct 2026 | Author: coordinator; CP1_PREP criteria; population rule and GASTAT addendum by CP2_PREP | Status: active

# Screening funnel

Inputs: the 13 region registers (`region-sweep`), merged by `uv run python -m screening.merge --out cities/ksa/candidates.parquet` (schema = `RegionRow` plus `funnel_stage` and score fields). Output: `docs/candidates.md`, `docs/screening.md`, `docs/coverage.md`, and the short list that feeds `corridor-generator`.

## Stages
1. **All settlements**: every row of every region register (count reported per region).
2. **Long list**: transparent filters, each a registered assumption with its id printed in the doc:
   - `population >= 10,000` (A-screen-001; sensitivity run at 5,000, A-screen-002), OR at least one sourced economic role other than `administrative` (A-screen-003, A-screen-009);
   - not already within 10 km of an existing or committed station (A-screen-004; such towns go to the "station additions / served" bucket, not out of the study);
   - governorate centres always pass to the long list regardless of population (rule 2).
   - population basis (A-screen-031…033, 035): a grid-only population (`pop_type: grid`) counts for the ≥ 10k test only if corroborated within 30 % by a second method (`pop_corroboration`); otherwise the row fails the population test with the reason "grid-only population, uncorroborated" (it can still pass as a centre or by a sourced role). The 5k sensitivity is not gated. `screening.funnel.population_basis` resolves `official` / `derived_corroborated` / `derived_uncorroborated` / `grid_corroborated` / `grid_unverified`; `docs/screening.md` reports the counts by basis.
3. **Short list**: weighted multi-criteria score, `uv run python -m screening.funnel score --weights cities/ksa/assumptions/screening_weights.yaml --sweep 0.25 --seed 1`. Whole pilot chain with the sensitivities (5k, linear gap, committed layer): `./screening/run_pilot_funnel.sh 1`.

4. **Grid sensitivity (report only)**: Tariq, CP2, 31 Oct 2026: "GASTAT-relayed figures win where they exist; WorldPop fills gaps only, every gap row flagged `pop_type: grid`, `pop_source_status: unverified`. A grid-only settlement may pass the ≥ 10k test only if a second independent method (building footprints × occupancy, GHSL, or VIIRS-calibrated) corroborates it within 30 %. Sensitivity to report: WorldPop ÷ 0.64 (the back-test median ratio), with the list of settlements whose ≥ 10k status flips; the correction is **not** applied to the base case." GASTAT addenda (Tariq, 31 Oct 2026): the **primary** Census 2022 TA1 exports `data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx` (150 governorates, S-cp2-gastat-007) and `census2022_TA1_city5k_primary.xlsx` (271 cities of 5,000 or more plus "Other (< 5,000)" = 3,683,816, S-cp2-gastat-008) "supersede the relayed file at governorate and city level" (addendum 2, 15:25): a settlement matched to a primary city gets that figure as `pop_type: official`, `pop_source_status: verified`, and "the ≥ 10k test for those rows uses the primary figure only (no corroboration needed)" (matching tiers and guards A-screen-038; crosswalk `screening/gastat_crosswalk.yaml`); the DataPulse relayed table (S-cp2-gastat-001) is a cross-check only, "never the value of record where a primary row exists"; keep citypopulation.de only for localities neither table covers; log a conflict where figures differ by more than 2 %. Grid-filled populations outside the matched cities are checked against each region's residual (control total A-screen-037; `control_total_flag`, reporting only). Below city level keep the WorldPop gap-fill under the gate, with "a third method: the 2010 cities > 5k list grown at the governorate's 2010→2022 ratio" (`pop_corroboration: gastat2010_city_growth`, value = pop_2010 × gov_2022 / gov_2010, A-screen-035), which "counts as one of the independent corroboration methods". The sensitivity uses the back-test median against the primary cities: ÷ 0.71 (A-screen-039; earlier ÷ 0.48, A-screen-036, and ÷ 0.64, A-screen-034). Lookups and the 2010 estimates: `screening.gastat` (`tables`, `apply`, then `primary`; `runs/gastat/apply/cities2010_growth.csv`). Run `uv run python -m screening.funnel sensitivity-grid --ratio 0.71 --seed 1 --run-dir runs/screening-pilot/sens-grid-071` (A-screen-039; state the earlier 0.48 and 0.64 too) → `flips.csv` (both directions: `flip_rule` under the gate, `flip_raw` arithmetic), `counts.json`, `meta.json`; print the table in `docs/screening.md`. Show the base case unchanged.

## Default criteria and weights (proposal for CP1; all `assumed`, `approval: pending CP1`)
The canonical values are `cities/ksa/assumptions/screening_weights.yaml` (v0.2, 31 Oct 2026) and `docs/plan.md` §1; this table summarises them.
| criterion | measure | default weight |
|---|---|---|
| population | log10(population), min-max scaled | 0.30 |
| rail gap | log10(1 + min(d, 300)) / log10(301), d = distance (km) to the nearest line of the layers in use (A-screen-030); farther = higher, saturates at the cap (A-screen-021, cap range 200–500 km); `--gap-measure linear` = the old min-max measure, run as a sensitivity | 0.20 |
| commute potential | 1 if 40–120 km road distance from a metro (A-screen-005), scaled by metro size and tier (A-screen-013: primary Riyadh, Jeddah, Makkah, Madinah, Dammam–Khobar–Dhahran; secondary Taif, Buraidah, Tabuk, Abha–Khamis Mushait; tertiary Jazan, Najran) | 0.20 |
| economic roles | count of distinct sourced roles, `administrative` excluded (A-screen-009), capped at 3 (A-screen-008); role list incl. `energy` (A-screen-007, -010); one source per role tied to the town or its governorate (A-screen-011) | 0.20 |
| terrain | penalty: escarpment_mountain -1, dunes/sabkha -0.5, mixed -0.5 (A-screen-025), flat/coastal 0 | 0.10 |
Weights sum to 1; each is swept ±25 % (one at a time, renormalised) and the doc reports, per candidate, the share of sweep draws in which it stays in the short list (rank stability). Short-list cut: top N where N is an assumption (A-screen-006, default 60) plus every candidate stable in ≥ 80 % of draws.

## docs/screening.md structure
Version header; label "screening input, synthetic, not a forecast"; funnel counts per region (all → long → short) as a table; the filters with assumption ids; the weight table and sweep results; the short list with scores and stability; the dominated or excluded candidates with reasons; the sensitivity (5k threshold) differences; sources and open questions.

## Coverage table docs/coverage.md
One row per GASTAT governorate, 13 regions, in GASTAT order: `region | governorate_ar | governorate_en | centre | population (S-xxx) | rows in register | long list | short list | served by existing/committed station (name) | status: screened / excluded (reason)`. Footer: `governorates in table = <n>; GASTAT count = <n> (S-xxx)`; the two must match or the milestone is blocked. `uv run python -m screening.coverage --out docs/coverage.md` builds it from the merged register and the GASTAT list; the `red-team-verifier` reconciles it.

## Rules that bite
- Corridor families are generated from the short list, never from a hand-coded town list (W2.4).
- Thresholds and weights are Tariq's to approve at CP1; until then every doc says "proposed".
- Any town the brief names as illustrative (Al-Jumum, Taif, Tabuk, ...) is treated like every other row; no special pleading.
