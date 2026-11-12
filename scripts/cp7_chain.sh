#!/bin/zsh
# CP7 chain (Tariq, 3 Nov 2026): R6_V3 (judge v3, variants) -> INTEGRATE_R6_V3 -> verify PASS -> tag r6.1 -> r7 phase (R7 + INTEGRATE_R7). Run under caffeinate. Stops at the R7 checkpoint.
set -u; cd "$(dirname "$0")/.."; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
note(){ echo "$(date '+%F %T') $*" | tee -a "$ROOT/logs/orch/orchestrator.log"; }
note "=== CP7 chain start ==="
[[ -f logs/orch/PAUSE ]] && { note "CP7 chain: PAUSE flag present; not starting"; exit 7; }
./orchestrate.sh r6v3; rc=$?
(( rc == 0 )) || { note "CP7 chain: r6v3 phase rc=$rc; stopping for the coordinator"; exit $rc; }
grep -qE '^[`*_ ]*INTEGRATE_R6_V3: done' docs/status/main.md || { note "CP7 chain: INTEGRATE_R6_V3 not done; stopping"; exit 6; }
if grep -qE "^VERDICT: PASS" docs/status/verify-INTEGRATE_R6_V3.md 2>/dev/null; then
  git add -A docs/cost-log.md docs/cost-log.csv >/dev/null 2>&1; git commit -q -m "docs(cost-log): INTEGRATE_R6_V3 row" >/dev/null 2>&1
  git tag -a r6.1 -m "r6.1: judge v3 (variants searched, CP7-3) integrated (INTEGRATE_R6_V3, red-team PASS). CP7 decisions recorded; R7 approved by Tariq." && note "tagged r6.1"
else
  note "CP7 chain: verify-INTEGRATE_R6_V3 is not PASS; stopping for the coordinator"; exit 6
fi
[[ -f logs/orch/PAUSE ]] && { note "CP7 chain: PAUSE flag present; not starting R7"; exit 7; }
./orchestrate.sh r7
note "=== CP7 chain end (R7 checkpoint: coordinator reports to Tariq) ==="
