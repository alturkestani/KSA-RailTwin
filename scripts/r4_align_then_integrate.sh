#!/bin/zsh
# After R4: run R4_ALIGN in the r4 worktree, then clear the coordinator hold and run INTEGRATE_R4 (guard rules unchanged).
set -u; cd "$(dirname "$0")/.."; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
note(){ echo "$(date '+%F %T') $*" | tee -a "$ROOT/logs/orch/orchestrator.log"; }
while ! grep -qE "^[\`*_ ]*R4: (done|blocked)" .worktrees/r4/docs/status/r4.md 2>/dev/null; do sleep 60; done
grep -qE "^[\`*_ ]*R4: blocked" .worktrees/r4/docs/status/r4.md && { note "R4 blocked; R4_ALIGN not started"; exit 2; }
sleep 90   # let the r4 phase script log its end and hit the hold
note "=== R4_ALIGN start (inserted step) ==="
MODEL=claude-opus-5-5 ./run_track.sh r4 R4_ALIGN; rc=$?
(( rc == 0 )) || { note "R4_ALIGN rc=$rc; stopping for the coordinator"; exit $rc; }
# clear only the coordinator HOLD; a real guard line must stay
if grep -q "COORDINATOR HOLD" logs/orch/PAUSE 2>/dev/null; then
  grep -v "COORDINATOR HOLD" logs/orch/PAUSE > logs/orch/PAUSE.tmp; mv logs/orch/PAUSE.tmp logs/orch/PAUSE; [[ -s logs/orch/PAUSE ]] || rm -f logs/orch/PAUSE
fi
[[ -f logs/orch/PAUSE ]] && { note "runaway guard line present; INTEGRATE_R4 not launched"; exit 7; }
WT=0 MODEL=claude-opus-5-5 ./run_track.sh main INTEGRATE_R4
note "=== R4_ALIGN chain end ==="
