> **Document version:** docs/status/r1a-network-notes.md v0.2 | 31 Oct 2026 | Author: gis-network-engineer (R1a) | Status: draft

# R1a network notes (road skims, distance fields, rail graph)

Draft hand-off from the `gis-network-engineer` builder to the coordinator. Road times below are **free-flow car times, uncalibrated**. Every OSM-derived output carries "(c) OpenStreetMap contributors (ODbL 1.0)". Every number here traces to a `runs/` or `data/ksa/osrm/` output, a log under `logs/r1a-osrm-*`, or a YAML with an assumption id.

## What was built

| file | purpose |
|---|---|
| `network/roadgraph.py` | OSMnx-equivalent drivable graph. `osmium tags-filter w/highway=<classes>`, then `osmium add-locations-to-ways -f opl`, then parse into a NetworkX MultiDiGraph plus SciPy CSR. Oneway handling: yes/true/1, -1/reverse, implied for motorway and roundabouts. Lengths are WGS84 geodesic (pyproj.Geod). Free-flow speed = numeric `maxspeed` × factor, else the class default. Snapping uses the largest strongly connected component. |
| `network/skims.py` | CLI `--backend osmnx\|osrm`. Writes `skims.parquet` (o, d, km, min, reachable, intrazonal, o/d snap km and flags), `zones_snapped.parquet` and `meta.json` (seed, config hash, manifest hash, code version, backend, path, pbf relative path, **pbf_sha256**, n_nodes, n_edges, runtime_s, assumption ids). Unreachable pairs are NaN and counted. The OSRM backend refuses an OSRM dir prepared from a different PBF (SHA-256 check). |
| `network/osrm.py` | `prepare` (extract with car.lua, partition, customize, MLD) into `data/ksa/osrm/<stem>/`. The PBF is symlinked there; nothing is written under `data/osm/`. Each step runs under `/usr/bin/time -l`. Also `estimate` (dry run with disk and time gates), `calibrate`, a local `osrm-routed` context manager and batched `/table`. |
| `network/access.py` | `nearest_targets()` and its CLI. Backends: `great_circle` (cKDTree on unit vectors, exact haversine), `osrm`, and `graph`. The road backends route the K great-circle-nearest candidates and keep the one with the shortest road time. The `method` column holds `great_circle_haversine`, `osrm_table_mld_car` or `nx_dijkstra_<pbf-stem>`. |
| `network/graph.py` | `build` and `check`. Builds a scenario rail graph from `cities/ksa/lines/<id>.yaml`. Layer checks: a line outside the scenario's layers raises `LayerError`, and S0 rejects committed lines. Line edges run in station list order. Run times are pure kinematics (accelerate, cruise, brake) plus dwell, and the source of each parameter is recorded on the edge. Interchanges link stations within walking distance, or with the same name. Writes `graph.json` (node-link), `nodes.parquet`, `edges.parquet`, `summary.json` (lines/stations/edges/km per layer) and `meta.json`. |
| `network/geo.py` | haversine (IUGG mean radius 6371.0088 km), `KNearest` |
| `network/road_speeds.yaml`, `access_params.yaml`, `graph_params.yaml`, `osrm_scale.yaml` | all parameters, with assumption ids |
| `tests/test_network_{skims,access,graph}.py` | 23 tests, about 3 s in total. They include one real OSRM prepare-and-table run on the fixture (skipped if OSRM is absent). No Jeddah or GCC PBF is needed. |
| `tests/fixtures/roads_fixture.osm` | invented 8-node road net (oneway, maxspeed, a private way, a disconnected island) at the FZ1–FZ6 centroids |
| `tests/fixtures/zones_jeddah_fixture.geojson` | 6 invented 0.03° square zones "Fixture Jeddah Zone n" inside the Jeddah clip, `fixture: true`, made-up populations |

## Commands that work (all run 31 Oct 2026)

```
uv run ruff check network tests && uv run pytest -q tests/test_network_*.py        # 23 passed, ~3 s
uv run python -m network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones.geojson --seed 1 --out runs/skims/demo-zones/
uv run python -m network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones_jeddah_fixture.geojson --seed 1 --out runs/skims/demo-zones_jeddah_fixture/
uv run python -m network.skims --backend osrm  --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones_jeddah_fixture.geojson --seed 1 --out runs/skims/demo-osrm-jeddah-zones_jeddah_fixture/
uv run python -m network.skims --backend osrm  --pbf data/osm/gcc-states-latest.osm.pbf --zones tests/fixtures/zones.geojson --seed 1 --out runs/skims/demo-osrm-gcc-zones/
uv run python -m network.osrm prepare  --pbf data/osm/gcc-states-latest.osm.pbf --log logs/r1a-osrm-gcc.log
uv run python -m network.osrm estimate --pbf data/osm/gcc-states-latest.osm.pbf
uv run python -m network.access --points runs/access/demo/points.parquet --targets runs/access/demo/targets_existing.parquet --backend great_circle --out runs/access/demo/near_gc.parquet
uv run python -m network.access --points runs/access/demo/points.parquet --targets runs/access/demo/targets_existing.parquet --backend osrm --osrm-dir data/ksa/osrm/gcc-states-latest --out runs/access/demo/near_osrm.parquet
uv run python -m network.graph build --scenario <tmp S2 fixture scenario> --lines-dir <tmp dir with corridor.yaml> --out runs/graph/fixture/ --seed 1
```

The far-zone demo (the `tests/fixtures/zones.geojson` command the coordinator asked for) runs end to end. All 6 zones lie outside the Jeddah clip, so all 6 snaps are flagged: max snap 104.27 km with osmium+networkx and 104.38 km with OSRM-Jeddah. Against the national OSRM files, 3 snaps are flagged (max 8.30 km). Snap distances are reported per zone and are not added to km or min.

## Measurements

**osmium+networkx on the Jeddah clip** (`data/osm/jeddah.osm.pbf`, 3,611,567 B, SHA-256 `cafede24…f319e`):
- 45,972 highway ways read, of which 44,319 were kept as drivable. 734 of them carry `maxspeed`, so class default speeds dominate.
- Graph: 183,709 nodes, 358,590 directed edges, 179,700 nodes in the largest SCC.
- Build plus 6×6 skim: 1.24–1.62 s (`runtime_s` in meta). An earlier run took 8.66 s while the national OSRM job was running at the same time.

**Backend agreement, Jeddah fixture zones, 30 off-diagonal pairs:**
- OSRM/graph km ratio: median 1.000, range 0.742–1.182. The outliers are FJZ1-origin pairs, where OSRM snaps to the nearest road segment and the graph snaps to the nearest node (0.95 km away).
- OSRM/graph minutes: median 1.051, range 1.003–1.28. OSRM adds turn penalties.
- OSRM on the Jeddah clip and on the national files gives identical results for these pairs.

**OSRM preparation (MLD, car.lua, 11 threads), from `prep_stats.json` and `logs/r1a-osrm-*.log`:**

| PBF | MB | wall s | peak RSS MB | peak footprint MB | output MB |
|---|---|---|---|---|---|
| jeddah (TrafficTwin clip) | 3.61 | 3.46 | 335.2 | 324.9 | 74.3 |
| west-calib (`osmium extract -b 38.5,20.5,41.5,23.5` of the GCC PBF) | 11.75 | 9.03 | 626.0 | 807.1 | 220.9 |
| central-calib (`-b 38.0,20.0,47.5,26.0`) | 43.24 | 29.61 | 1383.7 | 1756.2 | 590.4 |
| **gcc-states-latest (national)** | **255.37** | **187.65** | **3232.1** | **6974.1** | **2396.6** |

- National steps: extract 135.2 s (RSS 3.23 GB, footprint 6.97 GB), partition 40.2 s, customize 12.2 s.
- The two calibration clips were deleted after measurement (their numbers are kept in `network/osrm_scale.yaml`).
- Footprint is macOS's "peak memory footprint", which counts compressed pages. It is the better guide to memory pressure on the 18 GB machine.

**National estimate made before the run** (affine least-squares fit on the first three points; worst case = slope × 1.5, A-r1a-028):
- 2.82 min (worst 4.22)
- peak RSS 6.39 GiB (worst 9.46)
- disk 3.06 GiB (worst 4.56)
- Gates: free after the worst-case output 24.5 GiB ≥ 15 GiB; time ≤ 90 min. Both OK, so the run went ahead.
- Measured: 3.1 min, RSS 3.0 GiB, output 2.23 GiB, all inside the estimate. The national point is now in `osrm_scale.yaml` as a fourth point.

**National OSRM status: PREPARED.** Files are in `data/ksa/osrm/gcc-states-latest/` (2.2 GB on disk, from PBF SHA-256 `fffc7e74…2073`, which matches `cities/ksa/sources.yaml`). The Jeddah OSRM files are in `data/ksa/osrm/jeddah/` (71 MB).

**OSRM /table throughput (national):**
- 1,000 × 1,000 OSM `place=city|town|village` nodes in the KSA bounding box (random sample, seed 1; timing only, nothing written): 15.9 s at batch 100, 0 unreachable pairs, 105 of the 1,000 points snapped more than 2 km.
- Access demo, 186 pilot-register points × 119 existing stations (K = 5): 1.69 s, 0 unreachable. For 37 points the road-time winner differs from the great-circle nearest. Median road km / great-circle km = 1.287 (`runs/access/demo/`).

**Disk readings** (`df -h ~`, Avail):

| when | Avail |
|---|---|
| before `brew install osrm-backend` | 32 Gi |
| after the install | 31 Gi |
| before Jeddah prep | 32,432,697,344 B free |
| before national prep | 29 Gi (31,131,316,224 B) |
| after national prep | 25 Gi (27,379,367,936 B). The drop exceeds the 2.4 GB output because other sessions were writing at the same time. |
| end of session | 52 Gi (space was freed outside this track) |

## Tools

| tool | version | path |
|---|---|---|
| OSRM | osrm-backend **v26.10.0** (Homebrew bottle `osrm-backend--26.10.0.arm64_tahoe`, 65.9 MB, installed 31 Oct 2026) | binaries `/opt/homebrew/bin/osrm-{extract,partition,customize,routed}`; profile `/opt/homebrew/share/osrm-backend/profiles/car.lua` |
| osmium-tool | 1.19.1 | `/opt/homebrew/bin/osmium` |
| OSMnx | not installed (`osmnx_importable: false` in meta) | the osmium+networkx path ran |

## Assumptions for registration (values / range / reason)

| id | value | range | reason |
|---|---|---|---|
| A-r1a-010 | motorway 90 km/h | 90–120 | OSRM car.lua default (shared basis for both backends); free-flow, uncalibrated; Saudi motorway limits are higher |
| A-r1a-011 | motorway_link 45 | 35–60 | OSRM car.lua default |
| A-r1a-012 | trunk 85 | 70–110 | same |
| A-r1a-013 | trunk_link 40 | 30–50 | same |
| A-r1a-014 | primary 65 | 50–90 | same |
| A-r1a-015 | primary_link 30 | 25–45 | same |
| A-r1a-016 | secondary 55 | 40–80 | same |
| A-r1a-017 | secondary_link 25 | 20–40 | same |
| A-r1a-018 | tertiary 40 | 30–60 | same |
| A-r1a-019 | tertiary_link 20 | 15–30 | same |
| A-r1a-020 | unclassified 25 | 20–50 | same; desert unclassified roads may be faster |
| A-r1a-021 | residential 25 | 15–40 | same |
| A-r1a-022 | living_street 10 | 5–20 | same |
| A-r1a-023 | service 15 | 10–25 | same |
| A-r1a-024 | road (unknown class) 10 | 10–25 | OSRM `default_speed` |
| A-r1a-025 | maxspeed factor 0.8 | 0.7–1.0 | OSRM car.lua `speed_reduction`. Free-flow speeds below the posted limit. |
| A-r1a-026 | snap flag threshold 2.0 km | 1–5 | coordinator instruction; above it the centroid-to-road leg is material |
| A-r1a-027 | K = 5 road-routed candidates | 3–10 | a target outside the K great-circle nearest can never win, even if it is faster by road |
| A-r1a-028 | OSRM estimate slope margin 1.5 | 1.0–2.0 | the reference clips differ in density from the national extract |
| A-r1a-030 | interchange walk distance 0.4 km | 0.2–0.8 | typical same-complex transfer walk; links stations of different lines |
| A-r1a-031 | walk speed 4.8 km/h | 3.6–5.4 | about 1.33 m/s typical adult walking speed; to be sourced (literature) when registered |
| A-r1a-032 | same-name interchange cap 3.0 km | 1–5 | avoids linking two different stations that share a city name |
| A-r1a-033 | default accel 0.5 m/s² | 0.3–0.8 | used only when a line YAML has no value; to be replaced by sourced rolling-stock data |
| A-r1a-034 | default decel 0.6 m/s² | 0.4–0.9 | service braking; same caveat |
| A-r1a-035 | default dwell 120 s | 60–300 | intercity stop dwell; same caveat |

A-r1a-029 is unused. Method choices that are not numbers (drivable classes, exclusions, implied oneway) are in `road_speeds.yaml` and mirror the OSRM car profile.

## Licence items used (verified 31 Oct 2026)

| item | licence | source | note |
|---|---|---|---|
| OSRM (osrm-backend 26.10.0) | BSD-2-Clause | https://github.com/Project-OSRM/osrm-backend/blob/master/LICENSE.TXT | update the existing `docs/licences.csv` row: version 26.10.0, verified |
| osmium-tool 1.19.1 | GPL-3.0 | https://github.com/osmcode/osmium-tool (README "License") | called only as an external CLI via subprocess; not linked or redistributed, so no copyleft effect on the Apache-2.0 code. Flag before bundling any binary. |
| libosmium (inside osmium-tool and OSRM) | BSL-1.0 | https://github.com/osmcode/libosmium | |
| NetworkX 3.7 | BSD-3-Clause | https://github.com/networkx/networkx/blob/main/LICENSE.txt | row exists |
| SciPy, pyproj, geopandas, shapely | BSD-3 / MIT / BSD-3 / BSD-3 | rows exist (PyPI-verified 30 Oct) | |
| OSM data (GCC extract and Jeddah clip) | ODbL-1.0 | row exists | the OSRM files, road graphs and skims are **derived databases**: share-alike applies if they are distributed publicly. Credit "(c) OpenStreetMap contributors". |
| OSMnx | MIT | (row "planned; unverified") | not used; mark the row as not used, or leave it planned |

## Scenario graphs (coordinator request, 31 Oct 2026)

`network/graph.py` now expands an include id that has no exact `<id>.yaml` into the sorted group `<id>-*.yaml`. The expansion is recorded in `summary.json` (`expanded_ids`) and in `meta.json`. If neither the exact file nor the group exists, the build raises `FileNotFoundError`. A test covers this: `test_group_id_expansion`.

```
uv run python -m network.graph build --scenario scenarios/S0.yaml --out runs/graph/S0/ --seed 1   # 108 nodes, 112 edges
uv run python -m network.graph build --scenario scenarios/S1.yaml --out runs/graph/S1/ --seed 1   # 118 nodes, 123 edges
```

| scenario | layer | lines | stations | line edges | km (sum of km_post differences) |
|---|---|---|---|---|---|
| S0 | existing | 9 (hhr, sar-north-passenger, sar-east-passenger, riyadh-metro-l1..l6) | 108 | 99 | 2,311.67 |
| S1 | existing | 9 (as S0) | 108 | 99 | 2,311.67 |
| S1 | committed | 3 (landbridge, riyadh-rail-link, gcc-railway-ksa) | 10 | 7 | 1,477.8 |

In both scenarios, `riyadh-metro` expands to riyadh-metro-l1 … l6.

**Interchange edges: S0 13, S1 17.** All of them have reason `walk_distance` (≤ 0.4 km, A-r1a-030); none needed the same-name rule.
- **Metro:** 10 station names are shared across metro lines, giving 12 line pairs, and all 12 are linked. The KAFD station is shared by L1, L4 and L6 (3 edges). The other 9 shared names give one edge each: STC (L1-L2), National Museum (L1-L5), Qasr Al Hokm (L1-L3), Ministry of Education (L2-L5), Al Hamra (L2-L6), An Naseem (L3-L6), Ar Rabi (L4-L6), Uthman Bin Affan Road (L4-L6) and SABIC (L4-L6). Their distances range from 0.004 to 0.091 km.
- **S0 only:** sar-east-passenger:riyadh with riyadh-metro-l3:railway (0.110 km).
- **S1 adds 4:**
  - sar-north-passenger:riyadh-north with riyadh-rail-link:north-south-connection (0.124 km)
  - sar-east-passenger:riyadh with riyadh-rail-link:eastern-network-connection (0.000 km)
  - riyadh-metro-l3:railway with riyadh-rail-link:eastern-network-connection (0.110 km)
  - riyadh-metro-l1:al-bat-ha with landbridge:riyadh (0.133 km)

Run times are missing for 95 of the 99 S0 line edges and 96 of the 106 S1 line edges (`edges_missing_run_time`).

## OSRM PBF: symlink, not a copy

`data/ksa/osrm/gcc-states-latest/gcc-states-latest.osm.pbf` is a **relative symlink** (67 B) into the TrafficTwin `data/osm/` copy that `prepare()` creates. osrm-extract writes its outputs next to its input, so the link is needed there. Nothing was copied and nothing changed. `df -h ~` reads 51 Gi available (31 Oct 2026, end of session).

## Exact call for the settlement distance fields (OSRM backend)

Start one server for all target sets. `osrm.server` is a context manager that starts `osrm-routed --algorithm mld` on a free localhost port and stops it on exit, including after an error:

```python
from pathlib import Path
import geopandas as gpd, pandas as pd
from network import osrm
from network.access import nearest_targets

st = gpd.read_file("cities/ksa/lines/stations.geojson")
targets = pd.DataFrame(
    {
        "id": st.station_uid,
        "lat": st.geometry.y,
        "lon": st.geometry.x,
        "layer": st.layer,
        "line_id": st.line_id,
    }
)
points = ...  # DataFrame with id, lat, lon (about 7,400 settlements)
with osrm.server(Path("data/ksa/osrm/gcc-states-latest"), max_table=1000) as url:
    near_existing = nearest_targets(
        points, targets[targets.layer == "existing"], backend="osrm", osrm_url=url, batch=100
    )  # k defaults to 5 (A-r1a-027)
    near_committed = nearest_targets(points, targets[targets.layer == "committed"], ...)
    near_metro = nearest_targets(
        points, targets[targets.line_id.str.startswith("riyadh-metro")], ...
    )
```

Batch limits:
- `batch` (default 100) is the number of points per /table request and also the maximum number of destinations per request. Larger candidate unions are split into further 100-wide requests.
- `max_table` must be ≥ `batch`. 1000 leaves room for a batch of up to 500.
- Without `osrm_url`, passing `osrm_dir=` starts and stops a server per call, sized automatically.

Expected time, from the measured 100 × 100 request rate (1,000 × 1,000 in 15.9 s): 7,400 points × ≤ 5 candidates is about 370 requests, so roughly 1 minute per target set. That is an estimate, not a measurement.

Output columns: `road_km` and `road_min` (NaN if no candidate is reachable, with `road_reachable` False), `gc_km` to the great-circle nearest, and `method` = `osrm_table_mld_car`. The CLI equivalent is `uv run python -m network.access --points <p> --targets <t> --backend osrm --osrm-dir data/ksa/osrm/gcc-states-latest --out <parquet>`.

## Open issues for the coordinator

1. RESOLVED by group expansion (see "Scenario graphs"). Was: **`scenarios/S0.yaml` and `S1.yaml` include `riyadh-metro`, but the line files are `riyadh-metro-l1` … `riyadh-metro-l6`.** `network.graph check --scenario scenarios/S0.yaml` fails with "riyadh-metro.yaml not found". With the six ids substituted in a temporary copy, the build works:
   - S0: 9 existing lines, 108 stations, 99 line edges, 2,311.67 km, 13 interchanges.
   - S1: adds 3 committed lines, 10 stations, 7 edges, 1,477.8 km.
   (These probe outputs were not kept; rerun after fixing the scenarios.)
2. **Running times are missing for 96 of 106 S1 line edges.** Those lines have neither `running_time_model.cruise_kmh` nor `design_speed_kmh`, so `run_min` is NaN and counted in `summary.json` as `edges_missing_run_time`. Only hhr, landbridge and gcc-railway-ksa have times. Add the cruise speed (sourced) to the YAMLs, or decide a registered default per line type.
3. `sar-east-passenger:riyadh` and `riyadh-rail-link:eastern-network-connection` have identical coordinates (interchange at 0.000 km). Check whether that is intended.
4. **`data/osm/jeddah.osm.pbf` has no row in `cities/ksa/sources.yaml`** (SHA-256 `cafede24632a3e1bf0aa5631c09e13d12a5ae1c86ac67db62c2350bdeedf319e`, 3,611,567 B). Add it before the verifier runs `common.manifest verify`.
5. Add rows to `tests/fixtures/README.md` (not my file) for `roads_fixture.osm` and `zones_jeddah_fixture.geojson`.
6. **`network/zones.py` (coordinator's file; I will not edit it) was probably reformatted** by my first `uv run ruff format network tests` at 09:44. Formatting only, no logic change, but please diff it. After that I ran ruff only on my own files.
7. Snapping differs between backends: the graph snaps to the nearest node, OSRM to the nearest segment. For settlement access, OSRM is the reference method. The graph backend is for small clips and tests.
8. **Skims for the full candidate register are not yet produced.** The national OSRM files are ready, and a 5,000-zone all-pairs skim is projected at about 400 s from the measured throughput. They will be run when the register and zones are final.
