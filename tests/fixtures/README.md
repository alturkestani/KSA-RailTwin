> **Document version:** tests/fixtures/README.md v1.3 | 7 Nov 2026 | Author: R9 (demo_inputs.yaml row); R0 builder; R1a and GEO_VERIFY rows added by INTEGRATE_R1; R8 builder (exception for `api/`) | Status: draft

# Test fixtures

Tiny files for unit tests (they run in seconds). **Every value here is invented for testing and describes no real place, line, cost or appraisal**: names are "Fixture ...", every file or row carries `fixture: true` or `source: fixture`, and nothing here may be cited in a document or used as an input to a real run.

**Exception (R8):** `tests/fixtures/api/` holds trimmed copies of real registers and run outputs (not invented values) so the dashboard API tests exercise the real schemas; see `tests/fixtures/api/README.md`. They are never cited and never used as run inputs either.

| file | schema (`common/schemas.py`) | content |
|---|---|---|
| `corridor.yaml` | `LineSpec` (`line-yaml` skill) | 1 hypothetical corridor, 3 stations |
| `zones.geojson` | `ZoneProps` (feature properties) | 6 square zones with made-up populations |
| `region_register.parquet` | `RegionRow` (`region-sweep` skill) | mini-region register, 5 towns; rebuilt by `make_region_register.py` |
| `cost_register.yaml` | `CostItem` (`cost-register` skill) | 4 items, all `status: assumed`, `source: fixture` |
| `cba_case.yaml` | `CbaCase` (`cba-appraisal` skill) | 1 CBA case |
| `stream-json-sample.jsonl` | Claude Code stream-json | 3 events ending in a `result` event, for `common.cost_log` |
| `benchmarks_metrics.csv` | `rail.benchmarks` metric table (`docs/benchmarks/METHOD.md`) | 3 rows (cost/km A, ridership B, cost/km D), `source: S-fixture-*` |
| `rail_fixture.opl` | OSM OPL text (`rail.osm_lines`) | invented rail ways and stations ("Fixture Alpha" …) at made-up coordinates; `tests/test_rail_osm_lines.py` (R1a) |
| `roads_fixture.osm` | OSM XML (`network.skims`, `network.access`) | invented road network: nodes 1–6 at the centroids of `zones.geojson`, 7–8 a disconnected island; class, `maxspeed`, oneway and `access=private` cases; `tests/test_network_*.py` (R1a) |
| `zones_jeddah_fixture.geojson` | `ZoneProps` | invented squares with made-up populations ("Fixture Jeddah Zone …"), placed inside the TrafficTwin Jeddah clip box only so the road-skim demo has a network; no real zones (R1a) |
| `geo_verify/backtest_table.csv` | `screening.geo_verify` back-test table | 3 rows with letters for names (`a`, `b`, `c`) and made-up census/grid/building values; `tests/test_geo_verify.py` (GEO_VERIFY) |
| `geo_verify/station.geojson` | station-site point (`screening.geo_verify` stations) | 1 point, `station_uid: fixture:jeddah`, at an OSM way position (way 485762503) used only as a test geometry; not cited anywhere (GEO_VERIFY) |
| `demo_inputs.yaml` | `common.demo` inputs | invented screening distances, CBA benefit quantities and cost draws, and the dashboard fixture roots for `make demo` (R9); `fixture: true` |
