#!/usr/bin/env bash
# Rerun the pilot screening chain (CP1_PREP item 1.4): merge, long list, score, and the three
# sensitivities (5k threshold, linear rail gap, committed layer), then the coverage table.
# Outputs under runs/screening-pilot/ (gitignored). Label: pilot, proposed criteria pending CP1;
# screening input, not a forecast.   ./screening/run_pilot_funnel.sh [seed]
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-1}
R=runs/screening-pilot
W=cities/ksa/assumptions/screening_weights.yaml
F="uv run python -m screening.funnel"
uv run python -m screening.merge --pattern "cities/ksa/regions/archive/pilot/pilot-*.parquet" \
  --out cities/ksa/candidates-pilot.parquet --seed "$SEED"
$F long-list --threshold 10000 --sensitivity 5000 --seed "$SEED" --run-dir $R/long-list
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list/longlist.parquet --run-dir $R/score
$F long-list --threshold 5000 --sensitivity 5000 --seed "$SEED" --run-dir $R/long-list-5k
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list-5k/longlist.parquet --run-dir $R/score-5k
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list/longlist.parquet \
  --gap-measure linear --run-dir $R/score-linear-gap
$F long-list --threshold 10000 --sensitivity 5000 --seed "$SEED" --use-committed --run-dir $R/long-list-committed
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list-committed/longlist.parquet --run-dir $R/score-committed
uv run python -m screening.coverage pilot --out runs/screening-pilot/coverage-pilot.md
