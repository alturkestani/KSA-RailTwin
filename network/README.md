> **Document version:** network/README.md v1.1 | 31 Oct 2026 | Author: gis-network-engineer (R1a) | Status: draft

# `network/` (W1, R1a)

Geospatial network build (W1): road skims, distance fields, scenario rail graphs. Owner: `gis-network-engineer`. Settlement and zone geometry (`zones.py`) is the coordinator's module.

| module | CLI | what it does |
|---|---|---|
| `roadgraph.py` | (library) | OSMnx-equivalent drivable graph: `osmium tags-filter` + `add-locations-to-ways` (OPL) into a NetworkX MultiDiGraph / SciPy CSR; oneway, geodesic lengths, free-flow speeds from `road_speeds.yaml` |
| `skims.py` | `uv run python -m network.skims --backend osmnx\|osrm --pbf <pbf> --zones <geojson> --seed N --out <dir>` | zone-to-zone road km/min (`skims.parquet`, `zones_snapped.parquet`, `meta.json`) |
| `osrm.py` | `uv run python -m network.osrm prepare\|estimate\|calibrate ...` | OSRM MLD preparation under `data/ksa/osrm/<stem>/`, dry-run estimate (`osrm_scale.yaml`), local server, batched /table |
| `access.py` | `uv run python -m network.access --points <p> --targets <t> --backend great_circle\|osrm\|graph --out <parquet>` | nearest station/line vertex per settlement, great-circle and road (K candidates) |
| `graph.py` | `uv run python -m network.graph build --scenario scenarios/S0.yaml --out runs/graph/S0/ --seed 1` | scenario rail graph from line YAMLs, layer checks, kinematic run times, interchanges |
| `geo.py` | (library) | haversine, cKDTree nearest on unit vectors |

Parameters live in YAML with assumption ids (`road_speeds.yaml` A-r1a-010..026, `access_params.yaml` A-r1a-027, `osrm_scale.yaml` A-r1a-028, `graph_params.yaml` A-r1a-030..035). Road times are free-flow and uncalibrated. Maps or tables derived from OSM carry "(c) OpenStreetMap contributors (ODbL 1.0)". Tests: `uv run pytest -q tests/test_network_*.py` (fixtures only; no national run in pytest). Details and measurements: `docs/status/r1a-network-notes.md`.

## Demo (R1a README command)
```
uv run python -m network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones.geojson --seed 1 --out runs/skims/demo/
```
Runs in about 1.5 s; the fixture zones lie outside the Jeddah clip, so all 6 snaps are flagged (max 104.27 km). National: `uv run python -m network.skims --backend osrm --pbf data/osm/gcc-states-latest.osm.pbf --zones cities/ksa/zones/governorate_points.geojson --seed 1 --out runs/skims/national-governorates/` (after `uv run python -m network.osrm prepare --pbf data/osm/gcc-states-latest.osm.pbf`). The root `README.md` is a coordinator file; INTEGRATE_R1 should copy this command there.
