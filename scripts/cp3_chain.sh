#!/bin/zsh
# CP3 chain (Tariq, 31 Oct 2026): INTEGRATE_R2 -> verifier PASS check -> tag r2-int -> R3 phase (R3 + INTEGRATE_R3). Run under caffeinate.
set -u; cd "$(dirname "$0")/.."; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
note(){ echo "$(date '+%F %T') $*" | tee -a "$ROOT/logs/orch/orchestrator.log"; }
note "=== CP3 chain start ==="
WT=0 MODEL=claude-opus-5-5 ./run_track.sh main INTEGRATE_R2; rc=$?
if (( rc != 0 )); then note "CP3 chain: INTEGRATE_R2 rc=$rc; stopping for the coordinator"; exit $rc; fi
if grep -qE "^VERDICT: PASS" docs/status/verify-INTEGRATE_R2.md 2>/dev/null; then
  git add -A docs/cost-log.md docs/cost-log.csv >/dev/null 2>&1; git commit -q -m "docs(cost-log): INTEGRATE_R2 row" >/dev/null 2>&1
  git tag -a r2-int -m "R2 integrated (INTEGRATE_R2, red-team PASS): item-4 fix (Jubail Industrial City placed, 12 unmatched >=10k cities resolved or listed), 478 zero-pop grid rows dropped, housekeeping. CP3 decisions recorded." && note "tagged r2-int"
else
  note "CP3 chain: verify-INTEGRATE_R2 is not PASS; stopping for the coordinator"; exit 6
fi
[[ -f logs/orch/PAUSE ]] && { note "CP3 chain: PAUSE flag present; not starting R3"; exit 7; }
./orchestrate.sh r3
note "=== CP3 chain end ==="
