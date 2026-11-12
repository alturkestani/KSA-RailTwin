> **Document version:** docs/network.md v0.11 | 6 Nov 2026 | Author: S6_L6_CONNECTED (validation-offsets row: `osm_line` returns every part); FIX_HHR_REROUTE (§HHR geometry follow-up paragraph); FIX_HHR_JEDDAH (§HHR geometry; corridor-bonus row and line citations after the verifier, passes 1–3); R1a builder (with gis-network-engineer); CP2_PREP builder (§Population basis rewritten for GASTAT addenda 1 and 2: primary TA1 tables, control total) | Status: draft

# National data build and network (W1, milestone R1a)

What R1a built, how to rebuild it, and the counts measured on 31 Oct 2026. Maps and tables derived from these files carry **"(c) OpenStreetMap contributors (ODbL 1.0)"** and the three-layer legend (`existing`, `committed/under procurement`, `hypothetical (ours)`; plus `historical` for the Hejaz Railway). Road and rail times are free-flow or kinematic model values: **synthetic demand, uncalibrated: scenario comparison, not a forecast**. Source ids: `docs/sources/index.csv`; conflicts `C-r1a-*`: `docs/sources/conflicts.md`; assumptions `A-r1a-*`: `docs/assumptions.md`.

## 1. Rebuild (all local, about 5 minutes after the OSRM preparation)

```
uv run python -m rail.osm extract                         # 8 s: rail/admin/place extracts, layer GeoJSONs, routes.json
uv run python -m rail.lines build                         # 15 line YAMLs, alignments, stations.geojson, layer files
uv run python -m rail.lines validate cities/ksa/lines/    # 15 line files, 0 errors
uv run python -m network.zones admin                      # 13 regions, 149 governorates
uv run python -m network.zones settlements --grid data/ksa/grids/sau_ppp_2020_UNadj_constrained.tif \
    --grid-manifest-id worldpop-sau-2020-100m-unadj-constrained
uv run python -m network.osrm prepare --pbf data/osm/gcc-states-latest.osm.pbf     # 187.7 s, 2.4 GB
uv run python -m network.distances main --backend osrm --osrm-dir data/ksa/osrm/gcc-states-latest --seed 1   # 24 s
uv run python -m screening.gastat apply --seed 1   # CP2 P1a addendum: relayed Census 2022 city figures, A-screen-035, P1a gate on tag_10k (after zones + distances)
uv run python -m network.zones gov-points
uv run python -m network.skims --backend osrm --pbf data/osm/gcc-states-latest.osm.pbf \
    --zones cities/ksa/zones/governorate_points.geojson --seed 1 --out runs/skims/national-governorates/
uv run python -m network.graph build --scenario scenarios/S0.yaml --out runs/graph/S0/ --seed 1
uv run python -m network.graph build --scenario scenarios/S1.yaml --out runs/graph/S1/ --seed 1
uv run python -m network.econ                            # economic_nodes.parquet from the CSV
```
Demo skim (README command, Jeddah clip): `uv run python -m network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones.geojson --seed 1 --out runs/skims/demo/`. The fixture zones lie outside the Jeddah clip, so all 6 snaps are flagged (max 104.3 km); `tests/fixtures/zones_jeddah_fixture.geojson` is the in-clip variant. The `osmnx` backend is an OSMnx-equivalent osmium + NetworkX drivable graph (OSMnx itself is not installed; `pyproject.toml` is not owned by this track). Details: `docs/status/r1a-network-notes.md`.

Tools: osmium-tool 1.19.1 (`/opt/homebrew/bin/osmium`), osrm-backend 26.10.0 (Homebrew, `/opt/homebrew/bin/osrm-*`, car profile `/opt/homebrew/share/osrm-backend/profiles/car.lua`).

## 2. Rail layers (`cities/ksa/lines/`)

One spec per line in `rail/specs/<id>.yaml` holds the published facts with their source ids; `rail.lines build` adds OSM station positions and km-posts (cumulative shortest path along OSM track between consecutive stations; OSM gaps ≤ 0.3 km joined, A-r1a-005; branch stations hang off the previous main-line station). Committed lines have no published alignment: their polyline joins town-centroid or existing-station proxies, every site is flagged `unlocated:*`, km-posts are a great-circle chain, and `uncertainty_km` is set (A-r1a-006).

| line id | layer | status | line_type | stations | last km-post (km) | published length (km) | line source |
|---|---|---|---|---|---|---|---|
| hhr | existing | in_service | hsr | 5 | 448.54 | 453 (S-002, secondary) | S-001 |
| sar-north-passenger | existing | in_service | conventional_passenger | 6 | 1,242.67 | 1,250 (S-017) | S-017 |
| sar-east-passenger | existing | in_service | conventional_passenger | 4 | 449.09 | not set (733 km "double track", C-r1a-15) | S-024 |
| sar-north-freight | existing | in_service | freight (P4a, S-cp2-401…403) | 5 | 1,374.55 | 1,550 (S-019; C-r1a-17) | S-019 |
| sar-east-freight-legacy | existing | in_service | freight (P4a, S-cp2-401…403) | 6 | 560.76 | 566 (S-026) | S-026 |
| riyadh-metro-l1 … l6 | existing | in_service | metro | 25 / 15 / 22 / 9 / 12 / 10 | 36.70 / 24.21 / 39.76 / 29.04 / 12.55 / 29.11 | 38 / 25.3 / 40.7 / 29.6 / 12.9 / 29.9 (S-r1a-045…050, secondary) | S-r1a-045…050 |
| landbridge | committed | announced | mixed | 5 (all unlocated) | 874.3 (great circle) | 900 (S-054) | S-054 (MEED, 21 Jan 2026) |
| riyadh-rail-link | committed | procurement | mixed | 2 (proxies) | 22.9 (great circle) | 35 (S-060) | S-r1a-055 (MEED, 31 Aug 2026) |
| gcc-railway-ksa | committed | design | mixed | 3 (proxies) | 580.6 (great circle) | 672 (S-029) | S-029 (MEED, 12 May 2026) |
| hejaz-railway | historical | abandoned | conventional_passenger | 24 | 694.01 | Saudi section not stated (C-r1a-12) | S-r1a-066 |

Totals: **existing** 11 line files, 119 station rows, 4,247.0 km of km-posts (passenger, freight and metro); **committed** 3 lines, 10 station rows (all unlocated), 1,477.8 km (great circle, indicative); **historical** 1 line, 24 stations, 694.0 km. Station locations (`cities/ksa/lines/stations.geojson`, field `location_method`): 137 `osm:*`, 16 `unlocated:*` (10 committed, 6 existing freight terminals placed on the track node nearest to their OSM place proxy). GEO_VERIFY locates the 16. Al-Jumum (Landbridge "Jamuma", MEED Projects pid=114639, S-lb-018) remains a town-centroid proxy: the site is not published.

**Station-site research (CP2_PREP item 6, 31 Oct 2026; `rail/station_research.yaml`, applied by `uv run python -m rail.lines apply-sites`).** After GEO_VERIFY placed 2 freight sites (`osm_spur_end`), 14 stations were `unlocated:*`. Outcome: **1 resolved** (Al-Ahsa freight stop = the OSM-tagged SAR Al Hufuf station, way/95533900, confidence medium, band 0.5 km, A-stn-004/007, S-cp2-606), **11 low-confidence** (8 committed Landbridge/GCC stops at their town centroid; King Abdulaziz Port at the Wikipedia port coordinate S-cp2-603 with a 4.4 km band to the OSM port node, A-stn-009; Riyadh dry port adjacent to the SAR Riyadh station, S-cp2-604, A-stn-005; Ras Al-Khair at the locality centroid, 18.4 km band), **2 unlocated** (the Riyadh Rail Link's North-South and Eastern connection points: not published, and an existing station is not a connection point, A-stn-008). Low-confidence points carry `confidence: low`, `located: false` and `uncertainty_km` from the built-up radius (A-stn-001; Muwai 15 km fallback, A-stn-002; max with named alternatives, A-stn-003), derived table `data/ksa/geo/stn-extent-radii-2026-10-31.json` (manifest `stn-extent-radii-2026-10-31`). No layer changed: committed stops stay announced/planned. Moves against the previous point: GCC railway Kuwait-border stop 13.1 km (Al Khafji customs proxy → Al Khafji town centroid; the spec proxy stays inside the band and the line's indicative polyline still uses it), King Abdulaziz Port 10.3 km, Ras Al-Khair 8.9 km, all others ≤ 0.9 km (`distance_from_current_km` in `runs/cp2_prep/item6/stations-research.yaml`). Freight-terminal km-posts stay at their track snap points; the site point is the facility. Counts now: 138 `osm:*` (incl. Al-Ahsa), 2 `osm_spur_end`, 9 `town_centroid`, 1 `published`, 1 `adjacent_to_facility`, 2 `unlocated:*`.

`rail.lines build` now **merges**: a station the rebuild would put back to `unlocated:*` keeps its previous geo- or research-located site and location fields (`rail.lines.preserve_located`; a station OSM places takes the OSM position; tests `tests/test_cp2_item6_stations.py`). A full rebuild after the research reproduced `stations.geojson` with 0 differing features (14 kept).

Served test re-run (`uv run --with rasterio python -m screening.geo_verify.cli served-rerun --seed 1`, pilot register 186 rows): served 8 → 8, long list 157 → 157, pass-5k-not-served 170 → 170; `dist_existing_km` unchanged on every row; `dist_committed_km` changed on 15 rows (median |Δ| 9.1 km, max 13.1 km: Khafji 13.1 → 0.0 km; Northern Borders rows +6 to +11 km), list in `runs/cp2_prep/item6/served-diff.csv`. The committed-layer distances stay indicative (pilot criterion A-screen-030).

OSM layer files (`cities/ksa/lines/geojson/`, ODbL): `existing_osm.geojson` 2,518 ways, 6,159.7 km of in-service track, of which main line (no `service` tag) rail 5,021.6 km, subway 344.4 km, light rail 21.1 km, monorail 9.1 km, and service track yard 483.5 / siding 153.1 / spur 120.2 / crossover 6.7 km; `historical_osm.geojson` 100 ways, 785.9 km (abandoned/disused); `osm_construction_proposed.geojson` 60 ways, 276.3 km tagged `layer: unassigned` (OSM is not an announcement, rule 5; not used by any scenario); `osm_stations.geojson` 171 station features. Rail found in OSM without a line file: the Al Mashaaer Al Mugaddassah metro (Makkah, relations 1273546/7734267, 9 stops) has no operator source yet, so no `existing` file was written; the Jubail–Dammam railway (relation 15925686) and the Riyadh–Az Zabirah link are in `existing_osm` only. Both are flagged for R2.

Schema notes: `LineSpec.line_type` gained `freight` at CP2 (P4a, additive). Of the 15 line files only the two SAR freight lines carry it, because only they have a cited freight-only source: SAR presents both as "Freight Train" services apart from the passenger trains (S-cp2-401), Wikipedia calls the North line "a dedicated freight corridor" (S-cp2-402) and says the original Dammam–Riyadh line is "used only by freight trains" (S-cp2-403; both secondary). The phosphate/bauxite branches and the Al-Ba'ithah and Hazm al-Jalamid points are stations of `sar-north-freight`, not separate files, so that change covers them. Landbridge, the GCC railway and the Riyadh Rail Link stay `mixed`; every other line is unchanged. No line except HHR has a sourced speed, so 95 of 99 S0 line edges have no running time (R4).

### Haramain running-time check
OSM track Makkah–Jeddah (Al-Sulimaniyah) = 78.25 km (brief: 77 km). Published journey time 43 min (S-005, Wikipedia, secondary; C-r1a-01 lists 21–105 min values from other sources). Implied average **109 km/h** on the OSM distance (107 km/h on 77 km). The pure-kinematic graph model at 300 km/h (S-003) with default acceleration, braking and dwell (A-r1a-033…035) gives **18.2 min** running time on the same segment, 2.4 times faster than the published time (C-r1a-22). Every 30-minute claim in later milestones must use the timetable-calibrated effective speed, not the line speed. The decomposition of the 43 min is in §HHR-check below (CP2_PREP).

### HHR-check: decomposition of the published Makkah–Jeddah time (C-r1a-22; CP2_PREP item 5, 31 Oct 2026)

Run: `uv run python -m network.hhr_check run --seed 1` (parameters in `network/hhr_check.yaml`; outputs `runs/cp2_prep/item5/hhr-check/` with `components.csv`, `envelope.csv`, `summary.json`, `meta.json`; tests `tests/test_cp2_item5_hhr.py`). The running time uses the graph's own kinematics (`network.graph.segment_minutes`), so the 18.2 min of the graph is reproduced exactly. This is a timetable check, not a forecast.

**Where the 43 min comes from.** S-005 (Wikipedia) cites HHR's "Train Schedule" page archived on 19 Oct 2018 (S-cp2-507). That page is the opening timetable (S-cp2-503): train 80 Makkah 08:00 → Jeddah 08:43, train 1100 10:00 → 10:43, train 170 17:00 → 17:43, and in the other direction Jeddah 10:22 → Makkah 11:05 (trains 81, 1131, 171 the same 43 min); no stop between Makkah and Jeddah. The same timetable ran Makkah–Madinah non-stop in 175 min (train 3130), an average of 154 km/h on 448.54 km. Pages read in 2026 give about 2 hours for that run (S-r1a-010, secondary), and Makkah–Jeddah 28 to 30 min (S-cp2-504 aggregator, S-r1a-006 travel guide; both secondary, no SAR timetable readable, S-r1a-003). The 43 min is therefore an **October 2018 opening-timetable value**. Analysis: the opening timetable ran well below line speed on the whole line, not only between Makkah and Jeddah.

| component | minutes | km | source or assumption id |
|---|---|---|---|
| (a) line-speed running at 300 km/h | 13.10 | 65.52 | 300 km/h operational speed: S-cp2-501 (HHR portal), S-003. Segment 78.25 km: `cities/ksa/lines/hhr.yaml` km posts (OSM; HHR prints 77 km, S-cp2-502). Lower limits near the stations or anywhere else: **unknown**, none published or found (A-hhr-001: none assumed) |
| (b) acceleration 0 → 300 km/h at 0.5 m/s² | 2.78 | 6.94 | A-r1a-033 (assumed). Talgo 350 SRO: 8,000/8,400 kW, 8 × 1,000 kW motors (S-cp2-506, secondary); **no acceleration, braking or mass figure found**, so the inputs stay assumptions (grade: unsourced) |
| (b) braking 300 → 0 km/h at 0.6 m/s² | 2.31 | 5.79 | A-r1a-034 (assumed) |
| (b) of which time lost against running the same km at 300 km/h | 2.55 | | derived from the two rows above |
| (c) dwell at intermediate stops | 0.00 | | no intermediate stop (S-cp2-503; station order S-001, S-cp2-502); A-r1a-035 (120 s) does not apply |
| (d) recovery margin: 7 % of running time + 1 min/100 km | 2.06 | | UIC 451-1 as relayed by Schittenhelm 2011 (S-cp2-505); category choice A-hhr-002. HHR's own margin is not published |
| **total** | **20.25** | 78.25 | |
| envelope (A-r1a-033 0.3–0.8 m/s², A-r1a-034 0.4–0.9 m/s², A-hhr-002 5–7 % + 1.0–1.5 min/100 km; 36 combinations) | 18.94 – 22.25 | | `envelope.csv` |

Arithmetic (central): v = 300 / 3.6 = 83.33 m/s; acceleration 83.33 / 0.5 = 166.7 s over 83.33² / (2 × 0.5) = 6.94 km; braking 83.33 / 0.6 = 138.9 s over 5.79 km; cruise (78.25 − 6.94 − 5.79) = 65.52 km at 300 km/h = 13.10 min; running 18.20 min; margin 0.07 × 18.20 + 1.0 × 0.7825 = 2.06 min; total 20.25 min.

| published time | value (min) | residual = published − decomposition (min), central (envelope) | uniform line speed that would give the published time with the same acceleration, braking and margin |
|---|---|---|---|
| opening timetable 2018 (S-cp2-503 = S-005) | 43 | **22.7** (20.7 – 24.1) | 122 km/h |
| current, secondary (S-cp2-504, S-r1a-006) | 28 – 30 | 7.7 – 9.7 (5.7 – 11.1) | 198 – 182 km/h |

**Conclusion.** The four components sum to 20.3 min (18.9–22.3), not 43 ± 3 min (A-hhr-003): **C-r1a-22 stays open, residual 22.7 min** (20.7–24.1) against the 43 min. Even against the current secondary 28–30 min, 7.7–9.7 min remain unexplained, outside the ± 3 min band. No sourced input explains the residual: it would have to come from running below 300 km/h. The candidates are station-approach limits, the urban section in Jeddah, temporary speed restrictions, or a softer driving style or a larger timetable margin than UIC's. None is published or was found. What would resolve it: (1) a current SAR timetable (sar.hhr.sa journey search results for sample dates, S-r1a-003) to replace the 2018 value; (2) an HHR line-speed profile or speed-restriction list (SAR, the Al-Shoula consortium, Renfe or Adif technical papers); (3) Talgo 350 SRO tractive-effort and braking curves (Talgo, SAR). Until then R4 calibrates an effective speed to the timetable and labels it: 109 km/h on the 2018 timetable, or 157–168 km/h on 78.25 km at 28–30 min. It does not use the 300 km/h line speed for the 30-minute tests.

### HHR geometry (FIX_HHR_JEDDAH, 6 Nov 2026)

**Defect.** Tariq's map showed a straight line in west Jeddah from Al-Sulaimaniyah to KAIA. That line does not exist. `rail.lines build` drew each line as one LineString, and it appended the branch path (Al-Sulaimaniyah → junction → KAIA) to the main path before continuing the main line from Al-Sulaimaniyah. The result was a **stitch**: after vertex 376 (KAIA, 39.1737763, 21.660417), vertex 377 jumps **17.32 km** back to Al-Sulaimaniyah (39.2444797, 21.5192451). The line then retraces the Al-Sulaimaniyah–junction stretch a second time: vertices 266–320 and 377–431 are the same points (vertex 320 = vertex 431 = 39.215395, 21.6234465, the junction).

**Fix (method).** Branch stations (`branch: true` in `rail/specs/hhr.yaml`, only KAIA) now form their own part. The branch path from its main-line station is cut at its last vertex on the main part (the junction), because the main part already draws the shared stretch (`rail.lines.branch_parts`). A line with a branch is written as a **MultiLineString**, with properties `parts` `[main, branch]`, `part_to` `[null, kaia]` and `part_km`. Lines without a branch remain one LineString, byte for byte. The geometry is the OSM track (`data/ksa/osm/ksa-rail.opl` from the GCC extract in the manifest, the same graph as before). Nothing was drawn by hand. km-posts are computed exactly as before, so `cities/ksa/lines/hhr.yaml` and every station are unchanged. The rebuild changed only `hhr.geojson` and `existing.geojson` feature 0. In `stations.geojson`, only the `generated` date changed: all 153 stations are identical, and the 14 located stations were preserved by `preserve_located`. `rail.lines validate` passes (15 files, 0 errors); it already read MultiLineString through shapely, so `common/schemas.py` needed no change.

**Visual check of the junction and branch.** Sentinel-2 L2A scene S2B_37QED_20261027 (10 m), a 7.2 × 7.2 km window centred at 21.642 N, 39.195 E (manifest `sentinel-2-l2a-cogs-hhr_kaia_branch`, gitignored cache), checked on 6 Nov 2026. A track corridor leaves the main line south of the interchange at the junction, runs west beside the highway and turns north-west into the KAIA station. The OSM branch follows it. Nothing visible runs straight between Al-Sulaimaniyah and KAIA. This was a visual check only, and no geometry was traced from the imagery.

| | before (rev 0cc369e) | after |
|---|---|---|
| geometry | LineString, 1 part | MultiLineString, 2 parts (`main`, `branch`) |
| vertices | 1,100 | main 989; branch 57 |
| measured length (haversine over vertices) | 484.59 km | main **448.54 km**; branch **6.69 km**; total 455.23 km |
| repeated vertices | 55 (Al-Sulaimaniyah–junction drawn twice: 266–320 = 377–431) | 0 in either part |
| stitch (segment > 5 km re-entering a drawn stretch) | 1: index 376 → 377, 17.32 km, KAIA → Al-Sulaimaniyah | none |
| junction | (drawn through, not marked) | 39.215395, 21.6234465 (main way 629481003 meets branch way 868371679) |

Reconciliation of the old length: 484.59 = main 448.54 + duplicated Al-Sulaimaniyah–junction stretch 12.04 + branch 6.69 + stitch 17.32 (Makkah→Jeddah 78.29 + Jeddah→KAIA 18.73 + stitch 17.32 + Jeddah→Madinah 370.25). The main part equals the km-post span Makkah–Madinah (448.54 km; S-002's 449.2 km, secondary, is 0.15 % away; `length_km` 453 = 449.2 + 3.75 is the secondary total). The branch measures 6.69 km on OSM against S-002's 3.75 km: conflict **C-fixhhr-001** (`docs/sources/conflicts.md`, open). The old note in `docs/alignments.md` §7 item 2, that the 484.6 km of HHR geometry "includes yards and approach tracks", was wrong. The excess was the stitch, the duplicated stretch and the branch.

Long straight segments remain elsewhere (36 segments over 2 km on the main part; the longest is 17.2 km at index 588, north of KAEC). They are single straight OSM way segments, not stitches: none re-enters a drawn stretch, and all 402 segments over 2 km in `existing.geojson` (every line) join two consecutive nodes of one OSM way (checked against `data/ksa/osm/ksa-rail.opl`, 6 Nov 2026). The acceptance test therefore checks for **stitches** (no segment over 2 km that ends on an already drawn vertex, and no repeated vertices), not for every segment over 2 km.

Reproduce: `uv run python -m rail.lines build` (alignments) and `uv run python -m rail.hhr_check --before-rev 0cc369e` (this table and the dependency table; output `runs/fix-hhr/check.json`). Maps: `docs/report/figures/hhr-jeddah-before.png` and `hhr-jeddah-after.png` (`uv run python -m common.figures jeddah-hhr --geojson <file> --out <png>`).

**Length dependency.** Every consumer of the HHR geometry or its length, and which length it used: (a) the stitched LineString (484.59 km), (b) the km-posts or the 453 km figure, (c) the OSM track length clipped between the end stations.

| consumer | reads | used | moves with the fix? | evidence |
|---|---|---|---|---|
| `rail/lines.py` km-posts | OSM track graph, shortest path per station pair | (b) km-posts (448.54 km span; KAIA 97.02 via the branch) | no: `hhr.yaml` byte-identical | `git diff` of the rebuild: only `hhr.geojson`, `existing.geojson`, `stations.geojson` `generated` |
| `hhr.yaml` `length_km` 453 | spec (S-002) | (b) | no | spec unchanged |
| R1a/R3/R4 rail graph, skims, transfers (`network/graph.py`, `access/railgraph.py`) | line YAML stations and `km_post` | (b) | no | `km_post` grep; no geojson read |
| HHR running-time gate H1a −12.2 % (`access/running_time.py`) | `km_post` | (b) | no | same |
| R5–R8 CBA, R6 topology, report, brief, summaries | graph and running-time outputs; routed corridor lengths from R4_ALIGN | (b) for existing lines | not directly; yes through the routed hypothetical alignments (corridor-bonus row and A-align-070 row below) | no geojson read in `economics/`, `optimise/` (maps only), `coupling/` |
| R4_ALIGN validation length "HHR 426.6 vs 448.5 km", length error −4.9 % | routed length vs km-post span | (b) | no | `network/align.py` `compare(ref_km=km-post span)` |
| **R4_ALIGN validation offsets** (`runs/align/validation-s1`; `docs/alignments.md` §4, `docs/alignments-tables.md` §1) | `hhr.geojson` feature 0, clipped between the routed end points | **(a)** stitched | **yes**: mean offset 3.317 → 3.399 km (main + branch) or 3.432 km (main only; what `osm_line` returned until S6_L6_CONNECTED item 7, 6 Nov 2026; it now returns every part, so `compare` gives 3.399); p90 7.664 → 7.757 / 7.774; Hausdorff 14.328 → 14.330 / 14.329; `osm_km_clipped` 483.331 → 454.070 / 447.391; `osm_alignment_km` 484.59 → 455.23 | `rail.hhr_check` reproduces the published row exactly from the before geometry |
| R4_ALIGN OSM structures (bridge 44.1 km, tunnel 9.3 km within 50 m) | whole stitched line | (a) | totals no, if the branch is kept: 44.122 / 9.311 km with main + branch; main only 42.225 / 2.184 (KAIA's tunnel is on the branch). The shares divide by `osm_km_clipped`, so they move: bridge 9.13 % → 9.72 %, tunnel 1.93 % → 2.05 % | same |
| **R4_ALIGN corridor bonus** (`network/align.py` `_rail_geoms` → `rail_mask` → `penalty_surface`, 1 km dilation, bonus 0.25 v1 / 0.1 v2; `docs/alignments.md` §2) | every existing non-metro line geometry, rasterised as a preferred band when routing **every hypothetical corridor** | **(a)** stitched | **yes, directly** (found by the verifier, VERIFY_FIX_HHR_JEDDAH): the chord and the duplicated stretch were a cost-bonus band across west Jeddah. Routed alignments with vertices within 1.5 km of the chord and more than 1.5 km from the true HHR: `S4-commuter_belt-jeddah-315` (6), `S4-commuter_belt-jeddah-000` (5), `S4-commuter_belt-jeddah-045` (1), `S2-trunk_gap-riyadh-jeddah` (1); none in `cities/ksa/alignments-v2`. Belts 000 and 315 are in S6-L5, and CBA cases `CBA-S4-commuter_belt-jeddah-000`, `-315` and `CBA-S2-trunk_gap-riyadh-jeddah` exist. Effect size unknown until re-routed (not done) | `network/align.py` `_rail_geoms` l. 254, `rail_mask` l. 287, `penalty_surface` l. 346, `build_graph` l. 377; `penalty_surface(…, rail_mask(…))` called at both resolutions, l. 550 and 607, `build_graph` called l. 554 and 611; scan of `cities/ksa/alignments/*.geojson` |
| **A-align-070 tuning objective** (weights v1, frozen; 7.446 km) | mean of the three validation mean offsets | (a) | **yes**: at the frozen weights 7.446 → about 7.473 (with branch) or 7.484 (main only). Whether the coordinate descent would pick different weights is **unknown without re-tuning**. The weights feed every routed corridor, hence the R4–R8 lengths, costs and CBA | arithmetic: (3.399 − 3.317) / 3 = +0.027 |
| FIX_R7 weights v2 (in-sample 4.842; held-out HHR 5.79 km; `docs/alignments.md` §4b, annex A-align-100) | same | (a) | **yes**: v2 in-sample HHR 4.517 → 4.641 / 4.686; held-out HHR 5.791 → 5.957 / 6.012 | `runs/align/validation-v2-s1`, `validation-v2-loo-s1/hhr` |
| FIX_R7 offset diagnosis (`network/align_diag.py`; HHR 3.32 km split urban 1.82 / approaches 1.22) | same | (a) | probably (it decomposes the same mean offset); not recomputed | code reads `osm_line` |
| `docs/alignments.md` §7 item 2 ("HHR 484.6 km of geometry … yards and approach tracks") | measured length | (a) | **yes (text wrong)** | above |
| settlement distance fields `dist_existing_line_km`, `dist_existing_any_line_km` (`network/distances.py`, committed `settlements.parquet`) | line vertices densified to 1 km | (a) | 1 of 7,371 rows if re-run: Jeddah (OSM node 1933393717) 5.14 → 6.11 km; nearest line still `hhr`. Not re-run | `rail.hhr_check`: published = before on 7,371 rows |
| S5 station-addition test (A-corr-011, 15 km; `screening/corridors.py`) | per-line geojson parts | (a) | outcome no: Jeddah 5.12 → 6.11 km, stays ≤ 15 km and is skipped anyway (an existing station is within 10 km) | same |
| fig01, fig12 (report and deck) | `existing.geojson` | (a) drawn | drawn geometry only, rebuilt; no number printed from it | `figures-index.csv` unchanged |
| dashboard API `/api/layers/existing` | `existing.geojson` | (a) | serves the MultiLineString; `alignment_km` property 484.59 → 455.23 (in `web/src/types.ts`, not displayed by any component) | `dashboard-map.png` re-captured byte-identical |

**Verdict: published figures depend on the stitched geometry.** These were computed against it: the R4_ALIGN HHR validation offsets and the OSM structure shares, the tuning objective of the frozen weights v1, the FIX_R7 v2 numbers, the §7 sentence, and the routing of every hypothetical corridor through the corridor-bonus band. The Jeddah belts 000, 045 and 315 and Riyadh–Jeddah have routed vertices in the chord's band. Lengths, running times, skims and km-posts of the existing lines did not use the stitched length. The routed lengths of those four corridors, and through them their running times, costs and CBA cases (incl. S6-L5), can move directly on a re-route. All routed corridors can move further if a re-tune picks different v1 weights. Both are R4_ALIGN re-runs and Tariq's decision. Nothing was re-run.

**Follow-up (FIX_HHR_REROUTE, 6 Nov 2026; Tariq's decisions; `docs/alignments.md` §4d).**
- The corridor-bonus band is built from every part of the MultiLineString: the main line and the KAIA branch, with no chord.
- The four corridors were re-routed under the frozen v1 weights. All four are byte-identical to before, because every cell under the old chord also lies within 1 km of an OSM highway, so the corridor flag did not change on any path. Nothing downstream moved.
- The HHR offset and structure figures are now published on the corrected geometry, main + branch: mean 3.399 km; bridge 9.72 %, tunnel 2.05 %.
- The §7 sentence in `docs/alignments.md` is corrected.
- The v1 weights stay frozen (objective about 7.473 km). The v2 figures would read 4.641 / 5.957 km if recomputed; v2 is not adopted.
- C-fixhhr-001 stays open.

## 3. Scenario graphs (`runs/graph/S0`, `runs/graph/S1`)
| scenario | layer | lines | stations | line edges | km | interchange edges |
|---|---|---|---|---|---|---|
| S0 | existing | 9 (the metro id `riyadh-metro` expands to l1–l6) | 108 | 99 | 2,311.67 | 13 |
| S1 | existing + committed | 9 + 3 | 108 + 10 | 99 + 7 | 2,311.67 + 1,477.8 | 17 |
S0 contains no committed line (checked by `network.graph`, `LayerError`). Interchanges by walking distance ≤ 0.4 km (A-r1a-030); S1's links to the committed Riyadh proxies are artefacts of the proxy sites and must not be read as planned interchanges.

## 4. Settlement universe (`cities/ksa/zones/`)
- `regions.geojson` 13 regions; `governorates.geojson` 149 OSM governorate polygons (per region: Riyadh 23, Asir 17, Jazan 17, Makkah 17, Qassim 13, Eastern 12, Al-Baha 10, Hail 9, Madinah 9, Najran 7, Tabuk 7, Al-Jouf 4, Northern Borders 4) against the 150-row working list (C-r1a-20).
- `settlements.parquet`: **7,371 rows**, 7,364 OSM place nodes (55 city, 221 town, 3,603 village, 3,485 hamlet) plus 7 pilot rows that match no node. Every row has a population with type, source, status, method and licence (A-r1a-001): 164 tabulated (pilot register, GASTAT via aggregators, `secondary`), 118 OSM `population` tags (`derived`, `secondary`, ODbL), 7,089 WorldPop 2020 grid allocations (`grid`, `unverified`, CC BY 4.0), of which 2,541 receive 0 (no constrained-grid population within the radius: `pop_quality = grid_zero`). Tag counts: 181 rows ≥ 10,000 and 383 rows ≥ 5,000 (A-screen-001/002). These counts are as built by `network.zones`; after `screening.gastat apply` and `screening.gastat primary` (CP2 P1a addenda 1 and 2) the table holds 215 official (201 `verified` primary) / 80 derived / 7,076 grid rows and `tag_10k` is 143 under the P1a gate (§Population basis).
- Grid back-test on the 164 tabulated rows: grid / tabulated median 0.637 (IQR 0.332–1.104). The grid method under-counts, most of all for cities larger than the 10 km radius (Riyadh 1.85 M against 6.92 M). Grid values are a fallback for towns GASTAT does not tabulate, never a replacement (A-r1a-004).
- Region / governorate assignment: point in polygon for 7,368 rows; 3 coastal points take the nearest polygon (≤ 2.3 km outside).
- GASTAT's Census 2022 portal was not reachable on 31 Oct 2026 (docs/sources/r1a-data-inventory.md); the primary TA1 governorate and city ≥ 5,000 tables were exported by Tariq from the Tableau dashboard the same day (addendum 2), and 201 settlements are now `verified` (§Population basis).

### Population basis (CP2 P1a, 31 Oct 2026; A-screen-031…039; GASTAT addenda 1 and 2 applied)

Rule (Tariq, CP2, 31 Oct 2026): GASTAT figures win where they exist; WorldPop fills gaps only, every gap row `pop_type: grid`, `pop_source_status: unverified`; a grid-only settlement may pass the ≥ 10k test only if a second independent method (building footprints × occupancy, GHS-POP, VIIRS-calibrated, or the Census 2010 city grown at its governorate's 2010→2022 ratio, A-screen-035) corroborates it within 30 % (abs(grid − other) / grid ≤ 0.30). Resolver `screening.funnel.population_basis`. **From CP2 on, the population basis is the primary GASTAT Census 2022 TA1 governorate and city ≥ 5,000 tables** (S-cp2-gastat-007/008), exported by Tariq from the TA1 Tableau dashboard on 31 Oct 2026 (addendum 2); the DataPulse relayed file (S-cp2-gastat-001) is a cross-check only.

**Primary vs relayed cross-check** (`uv run python -m screening.gastat primary --seed 1` → `runs/gastat/primary/crosscheck_{governorates,cities}.csv`). The two exports have no region column and no Arabic names, so the join is on an English name key, then on the identical total for spellings that differ.

| level | primary rows | relayed rows | joined by name | joined by identical total | unmatched names | differences (total, Saudi, non-Saudi) |
|---|---|---|---|---|---|---|
| governorate | 150 (sum 32,175,224) | 150 | 150 | 0 | 0 / 0 | **0** on all 150 rows |
| city | 271 + Other 3,683,816 (sum 32,175,224) | 60 | 20 | 40 (e.g. Bariduh = Buraidah, Jayzan = Jazan, Alzahran = Al-Dahran) | 0 relayed cities without a primary row | **0** on all 60 rows |

The relayed file is a faithful copy of the primary table at both levels (conflict C-gastat-001: none found). Region totals: every region's governorate sum equals the primary TA1 and TA9 region totals (S-cp2-gastat-002/003; `docs/coverage.md`). The 2024 national estimate is 35,300,280 (S-cp2-gastat-006; no regional split), the base for the R3 population scenarios. Not available: Census 2022 localities and villages below 5,000, and 2023–25 regional estimates.

**Settlement universe: primary cities of 5,000 or more** (same command; `city_matches.csv`, `changes.csv`). 202 of the 271 primary cities are matched to 201 settlements (Alhufuf + Almubriz stay one combined row, KSA-ST-00003, 729,606, as in the pilot register); they hold 27,576,260 of the 28,491,408 people in cities of 5,000 or more. Each matched row gets the primary figure with `pop_type: official`, `pop_source_status: verified`, `pop_source: gastat-census2022-ta1-city5k-xlsx` (manifest id), `pop_quality: tabulated_primary`, no corroboration value, and is tested at ≥ 10k on that figure alone. The 151 pilot register rows of these settlements get the same figure (`S-cp2-gastat-008`, `verified`, `primary_to_find` cleared). Matching tiers and guards (A-screen-038; crosswalk `screening/gastat_crosswalk.yaml` `city_primary`, checked by hand against the OSM node's Arabic name):

| tier (A-screen-038) | cities | Census 2022 persons |
|---|---|---|
| crosswalk | 17 | 842,926 |
| relayed figure | 58 | 24,124,833 |
| identical figure | 102 | 2,398,345 |
| 2010 bridge (name) | 12 | 120,471 |
| universe (name) | 7 | 48,279 |
| 2010 bridge (skeleton) | 6 | 41,406 |
| **matched** | **202** (to 201 settlements) | **27,576,260** |
| unmatched | 69 | 915,148 |

38 rows change by more than 2 % (37 universe rows that were derived OSM tags or grid allocations, and one register row): table in `docs/sources/conflicts.md` C-gastat-005. One register correction: the eastern pilot row on the OSM node Ash Shaharin (KSA-ST-05310) carried 9,994, which the primary table gives to the Al-Ahsa town Aljabil; it now holds Alshaharin's own 5,518 (C-gastat-002). Two pilot figures sit on differently named nodes and are left unmatched for R2 review: Adham 9,022 on المهد (Makkah) and Alshazalah 11,560 on Ash Shinan (Hail) (C-gastat-003/004); 14 official rows keep a relayed (`secondary`) citypopulation.de figure that the primary city table does not list (governorate seats or localities under 5,000).

Unmatched primary cities (69; reason per city; their people stay in the region residual below):

| primary city (export spelling) | Census 2022 | reason |
|---|---|---|
| Jubail Industrial City | 172,233 | crosswalk: no settlement |
| Yanbaa As-Senayah | 73,139 | crosswalk: no settlement |
| Arqa | 42,179 | ambiguous name: 0 exact / 11 spelling-variant candidates and no region in the export to choose between them |
| Altaraf | 29,588 | ambiguous name: 0 exact / 10 spelling-variant candidates and no region in the export to choose between them |
| Wadi Al Oqool farms | 24,381 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Aleumran | 22,781 | ambiguous name: 0 exact / 5 spelling-variant candidates and no region in the export to choose between them |
| Alqawz | 22,374 | universe (name): KSA-ST-06114 fails the plausibility guard (A-screen-038) |
| Alkalabiuh | 21,992 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Almunayzilh | 21,346 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Aljurn | 20,329 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Alulya | 20,250 | universe (name): KSA-ST-00680 fails the plausibility guard (A-screen-038) |
| Thebea | 17,502 | ambiguous name: 0 exact / 5 spelling-variant candidates and no region in the export to choose between them |
| Albitaliuh | 15,146 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Alhasma | 13,028 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Iiskan Alkalabiuh | 12,817 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alhaliluh | 12,337 | ambiguous name: 0 exact / 8 spelling-variant candidates and no region in the export to choose between them |
| Alshazalah | 11,560 | crosswalk: no settlement |
| Aljushuh | 11,482 | ambiguous name: 0 exact / 6 spelling-variant candidates and no region in the export to choose between them |
| Benban | 10,793 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Aljabil | 9,994 | crosswalk: no settlement |
| Alramiluh | 9,741 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Altwaythir | 9,700 | ambiguous name: 0 exact / 7 spelling-variant candidates and no region in the export to choose between them |
| Eshyrh | 9,517 | ambiguous name: 0 exact / 33 spelling-variant candidates and no region in the export to choose between them |
| Alealiuh Walkhudira' | 9,147 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Adham | 9,022 | crosswalk: no settlement |
| Alqaruh | 8,656 | ambiguous name: 0 exact / 28 spelling-variant candidates and no region in the export to choose between them |
| Khabat Alkharish Wamuzaraea | 8,629 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Albadie Walqarfi | 8,623 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Ramadah | 8,607 | universe (name): KSA-ST-05700 fails the plausibility guard (A-screen-038) |
| Centers | 8,392 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Al Amajya | 8,156 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Al Tafih Farms | 7,716 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Almansuruh | 7,622 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Aleasiluh | 7,552 | ambiguous name: 0 exact / 23 spelling-variant candidates and no region in the export to choose between them |
| Prince Sultan Base | 7,530 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| An Naifiyah | 7,456 | ambiguous name: 0 exact / 3 spelling-variant candidates and no region in the export to choose between them |
| Alqarin | 7,339 | ambiguous name: 0 exact / 12 spelling-variant candidates and no region in the export to choose between them |
| King Abdul Aziz Military Academy | 7,154 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Al-Wadyin Station | 6,869 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Ghuran | 6,803 | ambiguous name: 0 exact / 4 spelling-variant candidates and no region in the export to choose between them |
| Alhutuh | 6,786 | ambiguous name: 0 exact / 10 spelling-variant candidates and no region in the export to choose between them |
| Aljafr | 6,772 | ambiguous name: 0 exact / 5 spelling-variant candidates and no region in the export to choose between them |
| Ghata | 6,653 | settlement KSA-ST-01141 also claimed by: Alghat, Ghata |
| Desalination Plant | 6,632 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Marikh | 6,349 | ambiguous name: 0 exact / 4 spelling-variant candidates and no region in the export to choose between them |
| Alshaqiraa | 6,069 | ambiguous name: 0 exact / 8 spelling-variant candidates and no region in the export to choose between them |
| Alsayl | 6,064 | ambiguous name: 0 exact / 23 spelling-variant candidates and no region in the export to choose between them |
| Al Rihan | 6,048 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Harad (Nadek) project and the adjacent areas | 5,951 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alkhadra' | 5,861 | ambiguous name: 5 exact / 17 spelling-variant candidates and no region in the export to choose between them |
| Aleuruq Alshamalia | 5,783 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Muhalih | 5,773 | 2010 bridge (skeleton): KSA-ST-00558 fails the plausibility guard (A-screen-038) |
| Shuab Makkah village | 5,673 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Qasirabin Eaqil | 5,617 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Umm Alawqb | 5,615 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Al Junfour | 5,589 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alramiduh | 5,581 | ambiguous name: 0 exact / 3 spelling-variant candidates and no region in the export to choose between them |
| Alshawajiruh | 5,537 | 2010 bridge (skeleton): KSA-ST-00644 fails the plausibility guard (A-screen-038) |
| Alshaquh Aleulya | 5,449 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Aleurafa' | 5,432 | ambiguous name: 0 exact / 15 spelling-variant candidates and no region in the export to choose between them |
| Alfudul | 5,374 | ambiguous name: 0 exact / 2 spelling-variant candidates and no region in the export to choose between them |
| Aghnam farm and surrounding farms | 5,211 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Malkan | 5,196 | ambiguous name: 0 exact / 1 spelling-variant candidates and no region in the export to choose between them |
| Al Shoudayda | 5,156 | ambiguous name: 0 exact / 24 spelling-variant candidates and no region in the export to choose between them |
| Alghawibuh | 5,139 | ambiguous name: 0 exact / 3 spelling-variant candidates and no region in the export to choose between them |
| Alhalalih | 5,120 | ambiguous name: 0 exact / 8 spelling-variant candidates and no region in the export to choose between them |
| San'abrah | 5,094 | no OSM settlement with this name (name variant, facility, camp or merged place) |
| Alshaqiq | 5,092 | ambiguous name: 0 exact / 17 spelling-variant candidates and no region in the export to choose between them |
| Alsafuh | 5,050 | 2010 bridge (skeleton): KSA-ST-05170 fails the plausibility guard (A-screen-038) |

**Control total (A-screen-037; reporting only).** The primary "Other (Less than 5000 inhabitants)" row is 3,683,816. The WorldPop-filled (grid) populations of the 7,076 settlements not matched to a primary city sum to **4,557,403**, which exceeds it by 873,587. Explanation: the per-region residual (TA1 region total − matched cities) also contains the 915,148 people of the 69 unmatched primary cities, whose grid cells are allocated to nearby grid settlements; against the residual (4,598,964) the national grid sum is 41,561 lower. The 1,517,574 people on unmatched tabulated rows (OSM `population` tags and 14 relayed figures; 952,849 of them in the Eastern Province, of which 903,597 is one OSM node "Al Ahsa" (`derived`) carrying a governorate-scale tag that double counts Alhufuf + Almubriz: open issue for R2 in `docs/STATUS.md`) come on top and are not part of this test.

| region | TA1 total | matched cities (n) | residual | grid, unmatched (rows) | grid − residual | tabulated, unmatched | flagged rows |
|---|---|---|---|---|---|---|---|
| riyadh | 8,591,748 | 8,091,836 (36) | 499,912 | 710,057 (1049) | +210,145 | 43,786 | 656 |
| makkah | 8,021,463 | 7,299,681 (25) | 721,782 | 934,520 (1118) | +212,738 | 111,714 | 727 |
| madinah | 2,137,983 | 1,819,815 (9) | 318,168 | 280,587 (782) | -37,581 | 7,474 | 0 |
| qassim | 1,336,179 | 1,108,710 (18) | 227,469 | 366,159 (547) | +138,690 | 41,875 | 282 |
| eastern | 5,125,254 | 4,466,009 (33) | 659,245 | 277,756 (172) | -381,489 | 952,849 | 0 |
| asir | 2,024,285 | 1,303,901 (14) | 720,384 | 549,408 (926) | -170,976 | 241,790 | 0 |
| tabuk | 886,036 | 793,804 (7) | 92,232 | 43,639 (109) | -48,593 | 14,257 | 0 |
| hail | 746,406 | 513,056 (8) | 233,350 | 202,210 (634) | -31,140 | 38,796 | 0 |
| northern_borders | 373,577 | 347,246 (5) | 26,331 | 41,725 (50) | +15,394 | 7,200 | 28 |
| jazan | 1,404,997 | 581,738 (24) | 823,259 | 788,487 (1200) | -34,772 | 29,933 | 0 |
| najran | 592,300 | 522,424 (6) | 69,876 | 75,223 (179) | +5,347 | 7,692 | 114 |
| al_baha | 339,174 | 200,104 (7) | 139,070 | 201,021 (241) | +61,951 | 0 | 193 |
| al_jouf | 595,822 | 527,936 (9) | 67,886 | 86,611 (69) | +18,725 | 20,208 | 48 |
| **KSA** | **32,175,224** | **27,576,260 (201)** | **4,598,964** | **4,557,403 (7076)** | **-41,561** | **1,517,574** | **2048** |

Seven regions exceed their residual (Riyadh, Makkah, Qassim, Northern Borders, Najran, Al-Baha, Al-Jouf). In those regions every grid row with a population gets `control_total_flag`: **172 rows** (403,830 persons) lie inside a matched city's A-r1a-004 allocation radius (possible double counting with the city extent: the census city includes districts that OSM maps as separate nodes); **1,876 rows** (2,011,486 persons) are grid over-count or boundary mismatch (the UN-adjusted 2020 grid totals 34.7 M against 32.2 M in the census, §WorldPop back-test). List: `runs/gastat/primary/control_flags.csv`. No population is changed by the flag.

| basis (after addendum 2) | rows | rows ≥ 10,000 | `tag_10k` |
|---|---|---|---|
| official, primary GASTAT city ≥ 5,000 (`verified`) | 201 | 133 | 133 |
| official, relayed via citypopulation.de, not in the primary city table (`secondary`) | 14 | 1 | 1 |
| derived, corroborated by the WorldPop grid within 30 % (reporting only) | 24 | 3 | 3 |
| derived, not corroborated (still counts: derived rows are not gated, A-screen-031 (b)) | 56 | 6 | 6 |
| grid, corroborated (A-screen-033/035 method within A-screen-032) | 0 | 0 | 0 |
| grid, unverified (4 have a 2010-growth value, none within 30 %) | 7,076 | 37 | 0 (all gated) |
| **total** | **7,371** | **180** | **143** |

`tag_5k` 390 (not gated). Before addendum 2 the table held 165 official (all `secondary`) / 117 derived / 7,089 grid rows and `tag_10k` 141 (addendum 1, below).

**Addendum 1 (superseded at city level).** `uv run python -m screening.gastat apply --seed 1` (→ `runs/gastat/apply/`) first wrote the 60 relayed city figures (S-cp2-gastat-001) into the pilot registers (58 rows) and this table (59 rows; three conflicts > 2 %: Al-Jubail 474,679 → 302,446, Yanbu' 331,916 → 258,777, Safwa 50,447 (OSM tag) → 45,676; C-cp2-601…603 in `docs/sources/conflicts.md`); `primary` re-sources all of them to the primary table with identical values. The Census 2010 cities > 5,000 list (245 cities, S-cp2-gastat-005) matched 202 settlements by Arabic or English name within the region; grown at the governorate ratio (S-cp2-gastat-004; region ratio from TA9 for the 33 governorates created after 2010, A-screen-035) it lands within 30 % of the official 2022 figure for 96 of 138 official cities (median absolute error 16.9 %). It is the bridge that gives the primary city names a region (A-screen-038).

**WorldPop back-test against the primary cities (report only; never applied to the base case).** The WorldPop 2020 settlement allocation (A-r1a-004 radius, nearest settlement; raster `worldpop-sau-2020-100m-unadj-constrained`) against the 201 settlements matched to primary cities: grid / census median **0.710** (IQR 0.370–1.157), median absolute error 49.6 %, 61 of 201 within 30 % (`runs/gastat/primary/backtest_cities.csv`). Earlier: **0.480** against the 60 relayed cities (IQR 0.307–0.727) and **0.637** on the 164 tabulated rows (IQR 0.332–1.104). The governorate-polygon sum (addendum 1) gives 1.280 (IQR 1.018–1.682; the grid totals 34.7 M against 32.2 M), which does not apply to settlement allocations. The item 1.2 sensitivity therefore uses **÷ 0.71** (A-screen-039); ÷ 0.48 (A-screen-036) and ÷ 0.64 (A-screen-034) are kept for comparison. Detail: `docs/geo-verify.md` §12.

Grid-only rows ≥ 10,000: **37** in the base case, **70** at ÷ 0.71, **92** at ÷ 0.64 and **164** at ÷ 0.48 (plain arithmetic: 33, 55 and 127 rows lifted over 10k; `runs/screening-pilot/sens-grid-{071,064,048}/flips.csv`). Under the rule, **one row flips up at every ratio: Al-Saih (Riyadh)**, grid 138,604 vs a 2010-growth estimate of 232,644 (68 % apart in the base case; 19 % at ÷ 0.71). Nothing flips down. Derived figures are OSM contributor tags (CP3: whether to gate derived rows too).

## 5. Distance fields (in `settlements.parquet`; run `runs/distances/settlements`, seed 1)
| field | method | targets | median | max |
|---|---|---|---|---|
| `dist_existing_km` / `road_km_existing` / `road_min_existing` | great circle; OSRM car MLD over the 5 nearest (A-r1a-027) | 15 intercity passenger stations (A-r1a-008) | 211.8 km / 282.3 km / 223.0 min | 845.1 km / 2,062.6 km / 1,374.0 min |
| `dist_existing_line_km` | great circle to alignment vertices every 1 km (A-r1a-007) | hhr, SAR North and East passenger | 203.8 km | 835.3 km |
| `dist_existing_any_line_km` | same | all 11 existing line files | 199.1 km | 798.9 km |
| `dist_committed_km` / `nearest_committed` / road fields | as above | 10 committed stations (**unlocated proxies**, `committed_sites_unlocated = true`) | 314.8 km (gc) / 428.0 km (road) | 1,056.9 / 1,785.5 km |
| `dist_committed_line_km` | alignment vertices | committed polylines (indicative) | 306.9 km | 1,056.9 km |
| `dist_metro_station_km` + road | as above | 93 Riyadh Metro stops | 725.2 km | 1,256.5 km |
| `dist_metro_city_km` + road, `nearest_metro_tier` | as above | 14 metro reference nodes, A-screen-013 tiers (A-r1a-009) | 114.7 km / 128.3 min | 828.6 km / 1,420.8 min |
All 7,371 rows are reachable by road in every set. Median road km / great-circle km to the nearest existing station: 1.313. 32 settlements lie within 10 km (great circle) of an existing intercity station; 133 within 30 min free-flow road time. Al-Jumum (C-r1a-19): 25.9 km great circle / 34.0 km road to Makkah, 54.8 / 75.4 km to Jeddah.

## 6. Road skims
- **National skim: run.** `runs/skims/national-governorates/` (OSRM 26.10.0, MLD, car, free flow): 149 governorate points (most populous settlement each, A-r1a-006b), 22,201 OD pairs, 0 unreachable, 1 snap > 2 km (max 9.73 km, median 0.02 km), 1.64 s run time (`runtime_s` in the clean rerun of 31 Oct 2026); `meta.json` records seed 1, config hash, manifest hash, code version and the PBF SHA-256. National OSRM preparation: estimate 2.82 min (worst 4.22), measured 3.1 min (187.7 s), peak RSS 3.2 GB, 2.4 GB of files under `data/ksa/osrm/gcc-states-latest/` (the PBF is a symlink there, not a copy).
- **Disk** (`df -h ~`, Avail): 32 GiB at the start of R1a; 29 GiB before the national OSRM preparation; 26 GiB after the grid downloads (59.5 MB of grids, so the rest of that drop came from elsewhere on the machine, not traced); 51 GiB at 09:5x after space was freed outside this track (not traced). Gate ≥ 15 GiB held throughout.
- Not done: TrafficTwin Jeddah peak-time skims (R4 coupling); r5py (not needed, OSRM covers the national case).

## 7. Screening re-run on the new station file (for GEO_VERIFY and R2)
`uv run python -m network.distances register --seed 1` recomputes the RegionRow distance columns of `cities/ksa/candidates-pilot.parquet` (186 rows, read-only here) from `cities/ksa/lines/stations.geojson` and writes a new file `cities/ksa/zones/candidates-pilot-r1a.parquet` (the merged register itself is not modified). Then:
```
uv run python -m screening.funnel long-list --in cities/ksa/zones/candidates-pilot-r1a.parquet --threshold 10000 --sensitivity 5000 --seed 1 --run-dir runs/screening-r1a/long-list
uv run python -m screening.funnel score --weights cities/ksa/assumptions/screening_weights.yaml --sweep 0.25 --seed 1 --in runs/screening-r1a/long-list/longlist.parquet --run-dir runs/screening-r1a/score
```
Result (31 Oct 2026, seed 1): long list 157 at 10k, served 8, short list 60, top-30 stable in all sweep corners for 22 candidates (stability 0.733), against 157 / 60 / 21 in the CP1_PREP pilot run. GEO_VERIFY reruns this after locating the 16 unlocated stations.

## 8. Economic nodes (`cities/ksa/zones/economic_nodes.parquet`)
168 rows, each with at least one S- source id (`network.econ` rejects unsourced rows), 136 located and 32 left `unlocated` (never guessed): airport 27 (27 located), border crossing 12 (10), energy 5 (4), giga-project 11 (10; status announced / under_construction / partly_open with a date), Hajj/Umrah 10 (5), heritage 8 (8), industrial city 40 (26), mining 10 (7), port 12 (7), tourism 4 (4), university 29 (28). Location methods: OSM element, Wikidata, Wikipedia coordinates (secondary) or host-city centroid (flagged). Gaps and conflicts: `docs/sources/r1a-econ.md` (Mawani and Ma'aden primary lists unreadable; several giga-project sites returned 403; MoE university list not read; Umm Wu'al not written).
