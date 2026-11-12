#!/usr/bin/env bash
# R4_ALIGN chain (prompts/R4_ALIGN.md): data -> frozen-weight validation -> route every S2-S4 corridor
# and the trunk alternatives -> sidecars -> corridor generation on routed lengths (same inputs as R2:
# candidates d31ec39b4d9a, scores 7b98bec42055) -> running times, isochrones, 30-minute test, costs,
# summaries -> funnel re-run -> before/after tables -> maps. Outputs under runs/ (gitignored) except the
# sidecars (cities/ksa/alignments/) and the regenerated corridor YAMLs and scenarios, which are tracked.
# Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
#   ./network/run_r4a.sh [seed]       DATA=1 also rebuilds the OSM layers and the tile cache
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-1}
if [ "${DATA:-0}" = "1" ]; then
  ./network/align_osm.sh
  uv run python -m network.align_data tiles
  uv run python -m network.align_data dem --workers 8
  uv run python -m network.align_data worldcover --workers 4
  uv run python -m network.align_data flags
  uv run python -m network.align_data index
fi
uv run python -m network.align validate --seed "$SEED"
# the trunk pairs not generated in R2 (dominated or not a speed gap), as corridor YAMLs
mkdir -p runs/r4a/inputs runs/r4a/regen0/scenarios
git show c52439b^:cities/ksa/candidates.parquet > runs/r4a/inputs/candidates.parquet
uv run python -m screening.corridors generate --candidates runs/r4a/inputs/candidates.parquet \
  --scores runs/r2/score/scores.parquet --out runs/r4a/regen0/corridors \
  --scenarios runs/r4a/regen0/scenarios --run-dir runs/r4a/regen0/run \
  --alternatives-out runs/r4a/alternatives --seed "$SEED"
uv run python -m network.align route-all --seed "$SEED" --workers 3
uv run python -m network.align route-all --seed "$SEED" --workers 3 --corridors-dir runs/r4a/alternatives --tag alternatives
uv run python -m network.align apply --seed "$SEED"
uv run python -m network.align apply --seed "$SEED" --corridors-dir runs/r4a/alternatives --tag alternatives --sub alternatives
uv run python -m screening.corridors generate --candidates runs/r4a/inputs/candidates.parquet \
  --scores runs/r2/score/scores.parquet --alignments cities/ksa/alignments \
  --run-dir runs/r4a/corridors --seed "$SEED"
uv run python -m screening.corridors validate
uv run python -m access.isochrones all --seed "$SEED"
uv run python -m access.commute_test run --seed "$SEED"
uv run python -m network.evaluate costs --seed "$SEED"
uv run python -m network.evaluate summary --seed "$SEED"
./screening/run_r4.sh "$SEED"
uv run python -m network.align compare --seed "$SEED"
uv run python -m network.align maps --seed "$SEED"
uv run python -m network.align reproduce --n 10 --seed "$SEED"
uv run python scripts/r4a_doc_tables.py --seed "$SEED"
