#!/bin/zsh
# CP6 chain (Tariq, 3 Nov 2026): clear pause -> INTEGRATE_R5 -> verify PASS -> tag r5 -> R6 phase (R6 + INTEGRATE_R6). Run under caffeinate.
set -u; cd "$(dirname "$0")/.."; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
note(){ echo "$(date '+%F %T') $*" | tee -a "$ROOT/logs/orch/orchestrator.log"; }
note "=== CP6 chain start ==="
rm -f logs/orch/PAUSE
WT=0 MODEL=claude-opus-5-5 ./run_track.sh main INTEGRATE_R5; rc=$?
(( rc == 0 )) || { note "CP6 chain: INTEGRATE_R5 rc=$rc; stopping for the coordinator"; exit $rc; }
if grep -qE "^VERDICT: PASS" docs/status/verify-INTEGRATE_R5.md 2>/dev/null; then
  git add -A docs/cost-log.md docs/cost-log.csv >/dev/null 2>&1; git commit -q -m "docs(cost-log): INTEGRATE_R5 row" >/dev/null 2>&1
  git tag -a r5 -m "R5 CBA integrated (INTEGRATE_R5, red-team PASS). CP6 decisions recorded; R6 released by Tariq." && note "tagged r5"
else
  note "CP6 chain: verify-INTEGRATE_R5 is not PASS; stopping for the coordinator"; exit 6
fi
[[ -f logs/orch/PAUSE ]] && { note "CP6 chain: PAUSE flag present; not starting R6"; exit 7; }
./orchestrate.sh r6
note "=== CP6 chain end ==="
