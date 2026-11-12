#!/usr/bin/env bash
# R3 demand chain (prompts/R3.md tasks 1-5): zones, skims, the baseline gravity run, calibration,
# then the scenario set with matched baselines (same zones, seed and parameters) and the trip-rate
# band. Outputs under runs/ (gitignored). Label: synthetic demand, uncalibrated: scenario
# comparison, not a forecast.
#   ./demand/run_r3.sh [seed]          (SKIP_PREP=1 reuses runs/zones and runs/skims/r3-zones)
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=${1:-1}
G="uv run python -m demand.gravity run --seed $SEED"
if [ "${SKIP_PREP:-0}" != "1" ]; then
  uv run python -m demand.zones build --seed "$SEED" --out runs/zones/
  uv run python -m demand.supply skims --seed "$SEED" --out runs/skims/r3-zones/
fi
# 1. the prompt's command: S0, Census 2022 baseline, prior constants (uncalibrated)
$G --scenario S0 --population baseline --year 2022 --out runs/demand/S0-baseline-s$SEED/
# 2. calibration at 2025 (demand_gravity.yaml calibration block)
uv run python -m demand.calibrate run --seed "$SEED" --out runs/demand/calibration-s$SEED/
CAL=runs/demand/calibration-s$SEED/calibration.json
P=un_wpp_medium_gastat2024
# 3. matched pair S0 / S1 at 2025 with the trip-rate band (low | base | high)
for S in S0 S1; do for R in low base high; do
  $G --scenario $S --population $P --year 2025 --calibration $CAL --rates $R \
     --out runs/demand/$S-$P-2025-$R-s$SEED/
done; done
# 4. population scenarios (S0 and S1, base rates)
for S in S0 S1; do
  for PS in un_wpp_low un_wpp_medium un_wpp_high; do for Y in 2040 2050 2060; do
    $G --scenario $S --population $PS --year $Y --calibration $CAL --out runs/demand/$S-$PS-$Y-base-s$SEED/
  done; done
  $G --scenario $S --population vision2030_policy --year 2030 --calibration $CAL \
     --out runs/demand/$S-vision2030_policy-2030-base-s$SEED/
  # 5. giga-project add-ons on WPP Medium 2050 (announced vs delivered shares, A-demand-030)
  for Q in p10 p50 p90 announced; do
    $G --scenario $S --population un_wpp_medium --year 2050 --calibration $CAL --giga $Q \
       --out runs/demand/$S-un_wpp_medium-2050-giga_$Q-s$SEED/
  done
done
uv run python -m demand.report summary --seed "$SEED" --out runs/demand/summary-s$SEED/
