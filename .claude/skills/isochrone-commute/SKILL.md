---
name: isochrone-commute
description: Computing 30/45/60-minute commute-shed isochrones for every metro, in-vehicle versus door-to-door times, the 30-minute test for towns 40–120 km from a major city, the running-time model, and the Haramain reality check. Use for W8 network evaluation (R4), the 30-minute lens in every corridor assessment and the coverage objectives in optimisation.
---
> **Document version:** skills/isochrone-commute/SKILL.md v1.1 | 30 Oct 2026 | Author: coordinator | Status: active

# Isochrones and the 30-minute test

## Running-time model (`access.running_time`)
Per service: acceleration to cruise, cruise at min(design speed, line speed), braking, plus dwell per intermediate stop and a recovery margin; parameters from `line-yaml` or `cities/ksa/assumptions/running_time.yaml` (each with a source or assumption id). Output per station pair: in-vehicle minutes and the explicit minute cost of every stop (reported as a table; used by `pareto-optimizer` as the through-passenger penalty).

Reality check (mandatory in every doc that uses the model): Haramain Makkah–Jeddah, 77 km in about 43 minutes, average about 107 km/h on a 300 km/h line (S-xxx). The model run on the existing HHR line must reproduce the published timetable within ±10 % before any hypothetical line is evaluated; the error is reported in `docs/access.md`.

## Door-to-door
`door_to_door = access_time + wait (headway/2, capped by assumption A-access-010) + in_vehicle + transfer penalties + egress_time`. Access and egress from the road skims (OSRM/r5py on the OSM graph) between zone centroids and stations, with a summer-heat first/last-mile penalty as a registered assumption (A-access-011) that the W7 analysis informs. Both in-vehicle and door-to-door are always reported side by side.

## The 30-minute test
For every town in the candidate register 40–120 km by road from a metro centre (A-screen-005; metro set A-screen-013: primary Riyadh, Jeddah, Makkah, Madinah, Dammam–Khobar–Dhahran; secondary Taif, Buraidah, Tabuk, Abha–Khamis Mushait; tertiary Jazan, Najran; report by tier): can a service on an existing, committed or hypothetical line deliver ≤ 30 minutes in-vehicle to the metro's main station, and what is the door-to-door time? Report: yes/no in-vehicle, door-to-door minutes, the car time from the skim at the AM peak (Jeddah from TrafficTwin's baseline; elsewhere free-flow plus a peak factor A-access-012), and the car trips the mode-choice model shifts in the scenario ("in the model, X % of car trips shifted", never "will remove").

## Isochrones
`uv run python -m access.isochrones --metro <riyadh|jeddah|makkah|madinah|dammam|taif|buraidah|tabuk|abha_khamis|jazan|najran> --scenario S<n> --minutes 30,45,60 --mode door_to_door --seed 1 --out runs/access/<id>/` writes `isochrone_<min>.geojson`, `reached.parquet` (population and jobs reached per band from the zone table), `meta.json`. Routing on the multimodal graph (road skims + rail services) with r5py/OpenTripPlanner where installed, else a NetworkX time-expanded graph (record which; disk gate before any r5/OSRM build).

## Outputs for the report and dashboard
Per metro and scenario: population and jobs within 30/45/60 minutes (baseline vs scenario, same zones and seed), the 30-minute test table for every qualifying town, the per-stop minute cost table, and the Haramain check error. Label every figure.

## Rules that bite
- Never assume 30 minutes; compute it. Every "30-minute" claim in any document cites the run id.
- Speeds above the line's design speed or above what the benchmark dossiers show as achieved averages are flagged.
- Isochrones are drawn on the same zone system as the demand model, so coverage objectives and CBA use identical populations.
