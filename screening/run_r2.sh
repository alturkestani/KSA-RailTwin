#!/usr/bin/env bash
# R2 national screening chain (prompts/R2.md): merge the 13 region registers, match the 271
# primary GASTAT cities (screening.primary_match), scale grid rows to the region residual
# (A-screen-040; CP3 5a drops zero-population grid rows), then the funnel with its sensitivities
# and the coverage table. Outputs under runs/r2/ (gitignored) and cities/ksa/candidates.parquet.
# Label: screening input, not a forecast.
#   ./screening/run_r2.sh [seed]        (DROP_ZERO=0 keeps the zero-population grid rows: R2 state)
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-1}
R=runs/r2
W=cities/ksa/assumptions/screening_weights.yaml
C=cities/ksa/candidates.parquet
DZ=""; [ "${DROP_ZERO:-1}" = "1" ] && DZ="--drop-zero-grid"

uv run python -m screening.merge --pattern "cities/ksa/regions/*.parquet" --exclude "pilot-*" \
  --out $C --run-dir $R/merge --seed "$SEED"
uv run python -m screening.primary_match --register $C --run-dir $R/primary_match --seed "$SEED"
uv run python -m screening.control_total --register $C --run-dir $R/control_total --seed "$SEED" $DZ
F="uv run python -m screening.funnel --national"
$F long-list --in $C --threshold 10000 --sensitivity 5000 --seed "$SEED" --run-dir $R/long-list
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list/longlist.parquet --register $C --run-dir $R/score
$F long-list --in $C --threshold 5000 --sensitivity 5000 --seed "$SEED" --run-dir $R/long-list-5k
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list-5k/longlist.parquet --register $C --run-dir $R/score-5k
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list/longlist.parquet --register $C \
  --gap-measure linear --run-dir $R/score-linear-gap
$F long-list --in $C --threshold 10000 --sensitivity 5000 --seed "$SEED" --use-committed --run-dir $R/long-list-committed
$F score --weights $W --sweep 0.25 --seed "$SEED" --in $R/long-list-committed/longlist.parquet --register $C --run-dir $R/score-committed
# grid sensitivity on the unscaled grid values (A-screen-039; report only)
uv run python -c "import pandas as pd; d=pd.read_parquet('$C'); g=d.pop_grid_raw.notna(); d.loc[g,'population']=d.loc[g,'pop_grid_raw']; d.to_parquet('$R/candidates-unscaled.parquet', index=False)"
$F sensitivity-grid --ratio 0.71 --seed "$SEED" --register $R/candidates-unscaled.parquet --run-dir $R/sens-grid-071
uv run python -m screening.corridors generate --candidates $C --scores $R/score/scores.parquet --seed "$SEED" --run-dir $R/corridors
uv run python -m screening.coverage national --register $C --run $R --out docs/coverage.md
uv run python -m screening.report_r2 --run $R
