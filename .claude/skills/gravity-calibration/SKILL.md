---
name: gravity-calibration
description: The W8 demand method: zones, doubly-constrained gravity models by purpose with documented impedance functions, population and giga-project scenarios as inputs, calibration to observed rail, air and bus totals, and the labels every output must carry. Use when building or calibrating the national OD matrices in demand/.
---
> **Document version:** skills/gravity-calibration/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Gravity model and calibration

All outputs: **synthetic demand, uncalibrated: scenario comparison, not a forecast** until the calibration step below passes and the status in `docs/assumptions.md` changes to `calibrated` for the fitted parameters.

## Zones
`cities/ksa/zones/zones.geojson`: one zone per GASTAT governorate nationally; finer zones (OSM admin_level 10 districts or a hex grid, assumption `A-demand-001`) inside the five metro areas. Population per zone from GASTAT Census 2022 (official) with the scenario multipliers (`demand.population`); jobs from the Labour Force Survey regional totals distributed by OSM land use and POIs (derived, `A-demand-002`); special generators (ports, airports, universities, Hajj/Umrah sites, giga-projects) as attraction add-ons with sources.

## Purposes and generation
`commute`, `business`, `leisure_vfr`, `pilgrimage`, `tourism`, `freight` (where data allows). Trip rates per purpose and per capita are assumptions with ranges (`A-demand-01x`) sourced from any Saudi or GCC survey found, else international literature labelled as such. Pilgrimage demand uses Hajj/Umrah statistics (GASTAT, Ministry of Hajj) as fixed external totals by origin.

## Doubly-constrained gravity
`T_ij = A_i B_j O_i D_j f(c_ij)`, with Furness balancing to a tolerance of 1e-4 (recorded). Impedance `f(c)`: exponential `exp(-beta c)`, power `c^-gamma` or combined; `c_ij` is generalised cost by the best current mode from the skims (road time from OSRM/r5py, air pair time where flights exist, rail time where a line exists) plus fare terms from `modechoice`. The functional form and `beta`/`gamma` per purpose are registered assumptions until calibrated. Intrazonal cost = half the distance to the nearest zone centroid (A-demand-020).

Command: `uv run python -m demand.gravity run --zones cities/ksa/zones/zones.geojson --skims runs/skims/<id>/ --scenario cities/ksa/population/<scenario>.yaml --params cities/ksa/assumptions/gravity.yaml --seed 1 --out runs/demand/<id>/` writes `od_<purpose>.parquet`, `totals.json`, `meta.json`.

## Calibration targets (observed totals, each `S-xxx`)
GASTAT Railway Transport Statistics (annual rail passengers, intercity passenger-km; 2023: 30.3 M passengers, 2,618 M pkm, to re-verify), HHR ridership (primary source needed), GACA/GASTAT domestic air passengers by city pair, SAPTCO/TGA intercity bus passengers where published, road traffic counts if any exist (say so if none). Procedure: `uv run python -m demand.calibrate --run runs/demand/<id>/ --targets cities/ksa/population/targets.yaml --seed 1` fits `beta`/`gamma` and the mode constants to minimise the weighted squared log error of modelled vs observed totals by mode and, where available, by city pair; report the fit (GEH-like statistic per target, error table) in `docs/demand.md`. Only when every target with grade A/B evidence is within the tolerance stated in `targets.yaml` (an assumption) do the fitted parameters become `calibrated`.

## Rules that bite
- Never calibrate to a target that is itself unverified; list such targets as "available but unverified".
- Giga-project demand is an add-on scenario (announced vs delivered share, `A-demand-030`), never in the base.
- Every OD matrix carries the label, the scenario id, the seed and the manifest hash; the dashboard shows them.
- Population scenarios: GASTAT projections (if published), UN WPP latest revision low/medium/high, urbanisation trend, Vision 2030 targets — each a separate YAML under `cities/ksa/population/` with sources.
