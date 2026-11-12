#!/usr/bin/env bash
# R4 chain (prompts/R4.md): running-time factors and the HHR gate, station skims, the R4 calibration,
# matched S0/S1 demand runs, the international segment, isochrones, the 30-minute test, corridor costs,
# the per-candidate summaries, the HHR validation and the Jeddah coupling policy YAMLs. Outputs under
# runs/ (gitignored). Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
#   ./access/run_r4.sh [seed]          REGISTER=1 also re-runs the register updates (roles, commute
#                                      minutes, R4 weights, funnel), which rewrite tracked files
#   The TrafficTwin run itself: `uv run python -m coupling.jeddah command --policy r4_hhr_jeddah_kaia`
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-1}
uv run python -m access.running_time run --line cities/ksa/lines/hhr.yaml --pattern all-stop --seed "$SEED"
uv run python -m access.running_time factors --seed "$SEED" --out runs/access/running_time/factors-s"$SEED"
uv run python -m access.railgraph skims --seed "$SEED"
if [ "${REGISTER:-0}" = "1" ]; then
  uv run python -m screening.commute_r4 roles --seed "$SEED"
  uv run python -m screening.commute_r4 minutes --seed "$SEED"
  uv run python -m screening.commute_r4 weights
  ./screening/run_r4.sh "$SEED"
fi
uv run python -m demand.calibrate run --network r4 --seed "$SEED" --out runs/r4/demand/calibration-r4-s"$SEED"/
CAL=runs/r4/demand/calibration-r4-s$SEED/calibration.json
for S in S0 S1; do
  uv run python -m demand.gravity run --scenario $S --population un_wpp_medium_gastat2024 --year 2025 \
    --calibration "$CAL" --network r4 --seed "$SEED" --out runs/r4/demand/$S-r4-2025-base-s"$SEED"/
done
uv run python -m demand.intl split --seed "$SEED"
for S in S0 S1; do uv run python -m demand.intl run --scenario $S --seed "$SEED" --out runs/intl/$S-s"$SEED"/; done
uv run python -m access.isochrones all --seed "$SEED"
uv run python -m access.commute_test run --seed "$SEED"
uv run python -m network.evaluate costs --seed "$SEED"
uv run python -m network.evaluate summary --seed "$SEED"
uv run python -m network.evaluate hhr --seed "$SEED"
uv run python -m coupling.jeddah policies --seed "$SEED"
uv run python scripts/r4_doc_tables.py
