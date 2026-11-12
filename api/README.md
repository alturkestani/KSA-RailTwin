> **Document version:** api/README.md v1.2 | 6 Nov 2026 | Author: viz-engineer (v1.0: R0 builder); R8_L6_PANEL (v1.2: S6-L6 comparison layout) | Status: draft

# `api/`: decision-dashboard API (R8), contract v1.0

FastAPI, file-backed and read-only (GET only), after TrafficTwin Jeddah's `api/` pattern (Apache-2.0, see `NOTICE`). It reads registers under `cities/ksa/`, scenarios under `scenarios/` and run outputs under `runs/`, and computes nothing beyond selection, reshaping and the difference against S1. No API keys, no external calls. The built web app (`web/dist`) is served at `/`.

```bash
make dashboard                                   # build web/ and serve http://127.0.0.1:8765
uv run uvicorn api.main:app --port 8765          # API only (+ web/dist if built)
uv run python -m api.cli serve --data-root tests/fixtures/api --runs-root tests/fixtures/api/run_outputs
uv run pytest -q tests/test_api_*.py             # smoke tests on the fixtures (seconds)
```

Environment (read at request time): `RAILTWIN_DATA_ROOT` (default the repo root), `RAILTWIN_RUNS_ROOT` (default `<data root>/runs`; the fixtures keep theirs in `tests/fixtures/api/run_outputs` because `runs/` is gitignored at every depth), `RAILTWIN_WEB_DIST` (default `web/dist`), `RAILTWIN_CORS_ORIGINS` (default the Vite dev server). Relative paths resolve against the repo root.

## Labels (rule 3, R7-checkpoint answer 5)

Every response that carries modelled numbers starts with `label` = `common.labels.LABEL` and `alignment_limitation` = `common.labels.ALIGNMENT_LIMITATION` (imported, never retyped; `api/contract.py: envelope`). Screening responses (`/api/register`, `/api/funnel`) carry the screening label "screening input, not a forecast". `/api/meta` also returns judge v3 (`v3-variants`, SHA-256 `d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee`, `docs/r6/judge-hashes.md`), seed 1, the OSM credit, the layer names, the baseline S1 (`runs/cba/CBA-S1-committed-programme`) and the central appraisal row (UN WPP medium, 60 years, Green Book 2026; `docs/cba.md` ranking basis). Ranges are objects `{p10, p50, p90}` with P10 ≤ P50 ≤ P90; a missing value is `null` (non-finite values in the runs, such as an infinite payback, become `null`).

## Endpoints

| endpoint | reads | returns |
|---|---|---|
| `GET /health` | | status and label |
| `GET /api/meta` | `common.labels`, `api/contract.py` | labels, judge, seed, layers, framing, central row, trade-off caption |
| `GET /api/layers`, `/api/layers/{layer}` | `cities/ksa/lines/geojson/{existing,committed,historical}.geojson`; `cities/ksa/alignments/<id>.geojson` (routed feature) or the corridor sketch; `cities/ksa/corridors/*/*.yaml` (station additions as points) | GeoJSON per layer; every feature carries `layer` and `layer_name` (`existing`, `committed/under procurement`, `hypothetical (ours)`, `historical`) |
| `GET /api/stations` | `cities/ksa/lines/stations.geojson` | station points with `layer` |
| `GET /api/regions` | `cities/ksa/zones/regions.geojson` | 13 region outlines (OSM, ODbL) |
| `GET /api/register?region=&stage=&min_population=` | `cities/ksa/candidates.parquet`, `runs/r2/long-list/longlist.parquet`, `runs/r2/score/scores.parquet` | register rows with `stage` ∈ `not_long_listed`, `served`, `long_list`, `short_list`, score and rank |
| `GET /api/funnel` | `runs/r2/long-list/counts.json`, scores, corridor YAMLs, `runs/cba/` | stage counts (settlements → long list → served → short list → corridors → appraised → layouts) and per-region counts |
| `GET /api/scenarios` | `scenarios/S0..S5.yaml`, `scenarios/S6-L1..L6.yaml` | id, title, baseline, layers, candidates, `role`, `trade_off_only`, `caption` |
| `GET /api/cba?population=&horizon=&rate_case=&family=`, `/api/cba/{case}` | `runs/cba/CBA-*/results.json` | per case: NPV, BCR, PVB, PVC, NPV and BCR with wider impacts, fiscal cost, PV capex as ranges |
| `GET /api/programmes?population=`, `/api/programmes/{layout}` | `runs/r6/top5/top5.csv`, `runs/r6/top5/L*/score.json`, `L*.layout.yaml`; S6-L6 only from `runs/r6/l6/score/S6-L6.csv`, `runs/r6/l6/score/score.json`, `runs/r6/l6/L6.layout.yaml` | S6-L1..L6 (`source` names the files read): framing, phases, NPV/BCR/PVC ranges (central row), capex range, NPV at P50 and P90 cost per population case; S6-L1 adds `p90_cost_note` |
| `GET /api/pareto` | `runs/r6/pareto_front.csv`, `top5.csv`, `runs/r6/l6/score/S6-L6.csv` | front points (robust NPV with low/medium/high band, reach, capex), the five search layouts (`kind` `search`; L4/L5 flagged `trade_off_only`) and S6-L6 appended (`kind` `comparison`, `comparison_only`, caption `caption_comparison`); S6-L6 is not a front point |
| `GET /api/fiscal` | `runs/r7/fiscal/fiscal.json` | net fiscal cost (30 and 60 years) and upfront public capex per delivery model, programmes and corridors; S1 baseline |
| `GET /api/vfm` | `runs/r7/vfm/vfm.json` | PSC, PPP, VfM low/central/high (envelope of the registered one-at-a-time driver sweeps; expected values, not P10/P50/P90) |
| `GET /api/difference?scenario=&population=` | layout `score.json`, `top5.csv`, or a CBA case | scenario minus S1: 2050 rail trips and passenger-km, per-line passengers, population within 60/120 min (reported only), and the appraisal ranges, which are increments over S1 by construction. 409 for S0, S1, S6-L4, S6-L5, S6-L6 and the S1-vs-S0 case |

## Framing (R7-checkpoint answer 1, binding)

S6-L2 = central case; S6-L1 = upside case that carries the Al-Kharj spur's P90 cost risk (its `p90_cost_note` is generated from `top5.csv` columns `npv_p90cost_{low,medium,high}`); S6-L3 = reach alternative; all against S1. S6-L4 and S6-L5 are flagged `trade_off_only` with the caption "trade-off illustration only: no recommendation"; the web app shows them only in the Pareto view, and difference mode refuses them. S6-L6 (R8_L6_PANEL, Tariq 6 Nov 2026) is a connectivity comparison from the connecting-set search, not a search result and not a reach trade-off: `FRAMING` gives it the role "comparison layout, not the recommended programme" with `trade_off_only` true, every response carries that caption (`api.contract.caption`), and `/api/meta` lists it under `comparison_layouts`. It is read only from `runs/r6/l6/` (never from `runs/r6/top5/` or `top5.csv`); it is not in the web switcher, it is shown only in the Pareto view (off-scale in the default y range and labelled there), difference mode refuses it (409), and the funnel's "optimised layouts (S6)" count stays the five search layouts of `top5.csv`.
