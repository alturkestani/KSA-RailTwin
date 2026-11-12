#!/usr/bin/env bash
# R3 register refresh (CP3 decision 8): funnel on the register before and after the DEM terrain
# and created-row skims sidecars, with the R2 sensitivities. Outputs under runs/r3/funnel-*/.
# Label: screening input, not a forecast.
#   ./demand/run_register_r3.sh [seed] [tag]     (tag: before | after)
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-1}
TAG=${2:-after}
R=runs/r3/funnel-$TAG
W=cities/ksa/assumptions/screening_weights.yaml
C=cities/ksa/candidates.parquet
F="uv run python -m screening.funnel --national"
$F long-list --in $C --threshold 10000 --sensitivity 5000 --seed "$SEED" --run-dir $R/long-list
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list/longlist.parquet --register $C --run-dir $R/score
$F long-list --in $C --threshold 5000 --sensitivity 5000 --seed "$SEED" --run-dir $R/long-list-5k
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list-5k/longlist.parquet --register $C --run-dir $R/score-5k
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list/longlist.parquet --register $C \
  --gap-measure linear --run-dir $R/score-linear-gap
$F long-list --in $C --threshold 10000 --sensitivity 5000 --seed "$SEED" --use-committed --run-dir $R/long-list-committed
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list-committed/longlist.parquet --register $C --run-dir $R/score-committed
