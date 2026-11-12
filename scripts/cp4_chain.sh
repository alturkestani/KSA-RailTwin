#!/bin/zsh
# CP4 chain (Tariq, 31 Oct 2026): INTEGRATE_R3 -> verifier PASS -> tag r3 -> R4 phase (R4 + INTEGRATE_R4). Run under caffeinate.
set -u; cd "$(dirname "$0")/.."; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
note(){ echo "$(date '+%F %T') $*" | tee -a "$ROOT/logs/orch/orchestrator.log"; }
note "=== CP4 chain start ==="
rm -f logs/orch/PAUSE
WT=0 MODEL=claude-opus-5-5 ./run_track.sh main INTEGRATE_R3; rc=$?
(( rc == 0 )) || { note "CP4 chain: INTEGRATE_R3 rc=$rc; stopping for the coordinator"; exit $rc; }
if grep -qE "^VERDICT: PASS" docs/status/verify-INTEGRATE_R3.md 2>/dev/null; then
  git add -A docs/cost-log.md docs/cost-log.csv >/dev/null 2>&1; git commit -q -m "docs(cost-log): INTEGRATE_R3 row" >/dev/null 2>&1
  git tag -a r3 -m "R3 demand and population scenarios integrated (INTEGRATE_R3, red-team PASS). CP4 decisions recorded." && note "tagged r3"
else
  note "CP4 chain: verify-INTEGRATE_R3 is not PASS; stopping for the coordinator"; exit 6
fi
[[ -f logs/orch/PAUSE ]] && { note "CP4 chain: PAUSE flag present; not starting R4"; exit 7; }
./orchestrate.sh r4
note "=== CP4 chain end ==="
