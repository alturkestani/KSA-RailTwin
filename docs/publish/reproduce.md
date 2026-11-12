> **Document version:** docs/publish/reproduce.md v1.1 | 12 Nov 2026 | Author: PUBLISH_PREP (main); PUBLISH_EXPORT (v1.1: shipped figure inputs as level 2, Zenodo placeholder for the full run archive as level 3; Tariq's answer Q8) | Status: draft

# Reproducing the main figures

Every modelled output is **synthetic demand, uncalibrated: scenario comparison, not a forecast**.

The report and deck figures (`docs/report/figures/fig01…fig16`, `docs/deck-figures/`) are drawn by one deterministic command:

```bash
uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/
```

It reads gitignored run outputs under `runs/` plus committed registers under `cities/ksa/` and `docs/` (`common/figures.py`). The author's rebuild from the author's `runs/` is byte-identical (`docs/status/verify-R8.md`). A public clone has no `runs/`, but it ships the figure inputs (the part of `runs/` that the figures read), so there are four levels of reproduction.

## Level 1: the pipeline at fixture scale (minutes, no data)

`make setup && make test && make demo` runs screening, the cost-benefit engine and the dashboard API on the invented fixtures in `tests/fixtures/` (README, "Try it"). It shows the code paths, but **not** the study's numbers.

## Level 2: rebuild the published figures from the shipped figure inputs (exact, seconds)

The repository ships the 106 run-output files (21.6 MB) that the figures are drawn from (the 105 the build reads plus the L1 score file behind fig06's numbers), under [`figure-inputs/`](figure-inputs/README.md) with their SHA-256 sums (Tariq's answer Q8, 12 Nov 2026). Copy them into `runs/` and run the command above:

```bash
mkdir -p runs && cp -R docs/publish/figure-inputs/runs/. runs/
uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/
git status --short docs/report/figures docs/deck-figures    # expect: no output
```

On the author's machine, with only these files present in a fresh tree, every report and deck figure came out byte-identical to the committed ones (`figure-inputs/README.md`). This level rebuilds the figures only. The report text, the dashboard data and the run-scoped tests need level 3.

## Level 3: everything from the author's full run archive (exact)

The full `runs/` archive (about 5.0 GB) and the frozen appraisal-model copies (`judge/v3-variants`, SHA-256 `d9fef643…`, `docs/r6/judge-hashes.md`; about 870 MB) are to be deposited on Zenodo by the author: **Zenodo DOI: `10.5281/zenodo.[TO BE FILLED BY THE AUTHOR]`** (not deposited yet, 12 Nov 2026). Unpack it at the repository root and run the command above. The figure tests (`tests/test_report_figures.py`, `tests/test_report_build.py`) and the other run-scoped tests then run instead of skipping.

## Level 4: re-run the chain from public data (approximate)

The chain below is the one recorded in the repository, with seed 1 throughout. A fresh run gives **approximate, not identical** numbers, for two reasons. First, Geofabrik serves only the latest OSM extract, while the study used the 2026-10-14 edition. Second, two R6 steps have no recorded command (see the end of this list). Register every download as a new manifest row (`docs/versioning.md`).

| step | command (as recorded) | output | needs | recorded time |
|---|---|---|---|---|
| 0. data | download the Geofabrik GCC-states extract to `data/osm/gcc-states-latest.osm.pbf` (ODbL); `DATA=1 ./network/run_r4a.sh` fetches the DEM, WorldCover and tile index (`network/run_r4a.sh`); WorldPop SAU 2020 and UN WPP 2024 per `cities/ksa/sources.yaml` | `data/` | network, about 1 GB of disk | n/a |
| 1. road routing | `uv run python -m network.osrm prepare --pbf data/osm/gcc-states-latest.osm.pbf` (`docs/network.md`) | OSRM graph | osrm-backend, osmium-tool | 187.7 s, 2.4 GB |
| 2. screening (R2) | `./screening/run_r2.sh 1` (`docs/screening.md`) | `runs/r2` | committed region registers | about 12 s |
| 3. demand (R3) | `./demand/run_r3.sh 1` (`docs/demand.md`) | `runs/zones`, `runs/skims/r3-zones` | OSRM | about 2.6–3 min |
| 4. access (R4) | `./access/run_r4.sh 1`, then `./network/run_r4a.sh 1` (`docs/status/r4.md`) | `runs/access`, running-time factors, station skims | OSRM. The Jeddah coupling step only writes policy YAML; no figure needs SUMO or TrafficTwin | about 20 min |
| 5. CBA (R5) | the sequence in `docs/status/r5.md` (demand calibration, `network.evaluate costs`, `access.railgraph skims`, `access.isochrones all --seed 1`, `costs.estimate`), then `economics.cli cases && inputs --workers 4 && run-all --workers 4 && summary && economics.cba report` (`docs/cba.md`) | `runs/cba` | steps 1–4 | not recorded |
| 6. zone split and re-calibration (R6) | re-run `demand.calibrate run --network r4 --seed 1` after the `demand_zones.yaml` v0.2 split (`docs/r6/judge-backtest.md`) | `runs/r6/demand/…` | step 5 | not recorded |
| 7. freeze the appraisal model | `uv run python -m optimise.judge freeze --ref 0172345 --name v3-variants`, then `optimise.judge verify` (`judge/README.md`, `docs/r6/judge-hashes.md`) | `judge/v3-variants` | the recorded `runs/` inputs; the hash matches only if every input is byte-identical | n/a |
| 8. R6 front | `optimise.search library|milp|ga|try|full` with `R6_JUDGE=v2-p5b` (`optimise/search.py`) | `runs/r6/pareto_front.csv` | judge v2 | **the command that writes the CSV is not recorded**. Part of the search was interactive and cannot be replayed exactly |
| 9. layouts (R6_V3) | `optimise.variants enumerate | library | milp | ga | rescore | backtest`, then `optimise.report_v3 cp7 | top5 --final …` (`docs/r6-topology.md`, `optimise/report_v3.py`) | `runs/r6/top5` | judge v3 | library 1 h 42 min; **the `--final` arguments are not recorded** |
| 10. S6-L6 comparison | `optimise.connect components|search|scenario|map --out runs/r6/l6 --seed 1`; `optimise.search full … --engine l6-score`; `optimise.connect score` (`optimise/connect.py`, `docs/status/main.md`) | `runs/r6/l6` | judge v3 | about 2 min |
| 11. funding (R7) | `funding.inputs score-corridors`; `funding.fiscal build --seed 1`; `funding.vfm build --seed 1` (`docs/fiscal-exposure.md`) | `runs/r7` | judge v3 | about 3 min plus 14 s |
| 12. figures | the command at the top | `docs/report/figures/`, `docs/deck-figures/` | steps 2–11 | seconds |

The run metas record which `runs/` were built from uncommitted ("dirty") code (`meta.json` `code_version`). A public re-run builds from a clean commit, which is one more reason the numbers differ in detail.
