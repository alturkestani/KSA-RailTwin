#!/bin/zsh
# First-session chain (brief section 10.3–10.4): data-scout verification pass, then the Landbridge
# reconciliation (Fable) in parallel with the national pilot. Run under caffeinate:
#   caffeinate -dimsu ./scripts/first_session.sh
set -u; cd "$(dirname "$0")/.."; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
note(){ echo "$(date '+%F %T') $*" | tee -a "$ROOT/logs/orch/orchestrator.log"; }
note "=== first session chain start ==="
WT=0 MODEL=claude-opus-5-5 ./run_track.sh main DATASCOUT_1H
WT=0 MODEL=claude-fable-5-1 ./run_track.sh main LANDBRIDGE_RECONCILE & pLB=$!
./orchestrate.sh pilot
wait $pLB
note "=== first session chain end ==="
