#!/usr/bin/env bash
# R4 register refresh (CP4 requirement 3 and CP4-5a): the funnel after the 24 created rows get their
# roles (CP1 weights, straight-line band) and with the commute criterion in minutes
# (screening_weights_r4.yaml). Outputs under runs/r4/funnel-<tag>/. Label: screening input, not a forecast.
# Order after a register rebuild: screening/run_r2.sh -> demand.register_update apply ->
# screening.commute_r4 roles -> screening.commute_r4 minutes -> screening.commute_r4 weights -> this script.
#   ./screening/run_r4.sh [seed]
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-1}
C=cities/ksa/candidates.parquet
F="uv run python -m screening.funnel --national"
for TAG in roles minutes; do
  W=cities/ksa/assumptions/screening_weights.yaml
  [ "$TAG" = minutes ] && W=cities/ksa/assumptions/screening_weights_r4.yaml
  R=runs/r4/funnel-$TAG
  $F long-list --in $C --threshold 10000 --sensitivity 5000 --seed "$SEED" --run-dir $R/long-list
  $F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list/longlist.parquet --register $C --run-dir $R/score
done
