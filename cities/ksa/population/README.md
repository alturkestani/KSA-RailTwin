> **Document version:** cities/ksa/population/README.md v0.1 | 31 Oct 2026 | Author: demand-modeler (R3) | Status: draft

# cities/ksa/population: population scenarios to 2060 (W8)

Every figure produced from these files is **synthetic demand, uncalibrated: scenario comparison, not a forecast**. Method and results are in `docs/population-scenarios.md`. Assumptions are in `docs/assumptions.md`, sources in `docs/sources/r3-pop.csv` and licences in `docs/licences.csv`.

Rebuild (needs the raw UN files under `data/ksa/population/`, manifest ids `un-wpp2024-totalpop-csv`, `un-wup2025-national-definitions-csv` and `un-wup2025-degurba-level1-csv`):

    uv run python -m demand.population build --seed 1      # tables + generated YAMLs (deterministic)
    uv run python -m demand.population validate            # every number has a source or assumption id
    uv run python -m demand.population show --scenario un_wpp_medium --year 2040 [--downscaling regional_trend] [--giga p50] [--out runs/population/<id>/]

## Files

| file | written by | content | licence |
|---|---|---|---|
| `inputs.yaml` | hand | every real-world constant the code reads (census and GASTAT totals, Vision 2030 statements, downscaling weight, giga parameters), each with `source:` or `assumption:` | facts with citations |
| `base_2022_governorates.csv` | `build` | 150 GASTAT governorates (Census 2022 TA1 primary export), region, Arabic name, zone id (OSM polygon G001-G149; Al Amoah merged into G031, A-pop-007), total/Saudi/non-Saudi | derived from GASTAT Census 2022 (GASTAT use policy: acknowledge GASTAT; **modified**, not official statistics) |
| `wpp2024_sau_total_population.csv` | `build` | UN WPP 2024 Saudi Arabia rows, all variants, 2010-2060, thousands as printed | CC BY 3.0 IGO: "United Nations, DESA, Population Division (2024). World Population Prospects 2024, Online Edition" (extract) |
| `wup2025_sau_urban_share.csv` | `build` | UN WUP 2025 Saudi urban share (national definitions; Degree of Urbanisation cities and cities + towns), 2010-2050 | CC BY 3.0 IGO: "United Nations, DESA, Population Division (2025). World Urbanization Prospects 2025" (extract) |
| `downscaling.yaml` | `build` | constant-shares and regional-trend parameters, GASTAT TA9 region totals 2010 and 2022 | derived from GASTAT (as above) |
| `scenarios/*.yaml` | `build`, except `gigaprojects.yaml` (hand) | the scenario files (schema below) | as their sources |

## Scenario schema

Every file starts with a comment version header (`# > **Document version:** ...`) and carries:

```yaml
id: un_wpp_medium              # file stem
kind: projection_un_wpp        # baseline_census | projection_un_wpp | sensitivity | policy_vision2030 | urbanisation_trend | addon_gigaprojects
title: "..."
label: "synthetic demand, uncalibrated: scenario comparison, not a forecast"
base: baseline                 # the census base the totals are anchored to
zones: cities/ksa/population/base_2022_governorates.csv
downscaling: {default: constant_shares, alternatives: [regional_trend], assumptions: [A-pop-005, A-pop-006]}
national_totals:
  unit: persons
  source: S-r3-pop-001         # or a list
  assumptions: [A-pop-001, ...]
  values: {2022: 32175224, 2023: ..., 2060: ...}   # annual, persons
  no_growth: true              # baseline only: the 2022 total applies to every year
prediction_intervals: {...}    # un_wpp_medium only: lower_95, lower_80, median, upper_80, upper_95 by 5-year step
zone_overrides:                # vision2030_policy only: zone -> {values: {year: persons}, source, assumptions}
  G138: {...}
tourism: {...}                 # vision2030_policy only: visits targets (tourism purpose, never population)
```

`gigaprojects.yaml` (`kind: addon_gigaprojects`) holds `projects:`, each `{id, name, zone, zone_method, residents_announced, residents_basis (increment | total_area), jobs_announced, visitors_announced, visitors_unit, target_year, delivered_share {p10, p50, p90, assumption}, status, status_date, sources, assumptions, notes}` plus optional `residents_observed_capacity`, `homes_announced`, `hotel_rooms_announced`, `jobs_target_year` and `supersedes_when_larger`.

Rules enforced by `validate` (and `tests/test_demand_population.py`): header line, label and kind present; every numeric leaf has a `source`/`sources`/`assumption`/`assumptions`/`derived_from` key on its own mapping or an ancestor (a file-wide key at the top level does not count); every `S-` id resolves in `docs/sources/index.csv` or `docs/sources/r3-pop.csv`, and every `A-` id in `docs/assumptions.md` or `docs/assumptions.md`.

## Library contract

`demand.population.project(base_by_zone, scenario, year) -> pd.Series`: integer zone populations whose sum equals the scenario's national total for that year exactly (largest-remainder rounding). Optional `method="regional_trend"` and `weight=`. `giga_increments(...)` and `apply_giga(pop, inc, "reallocate" | "additive")` add the giga-project quantities; `reallocate` keeps the national total.
