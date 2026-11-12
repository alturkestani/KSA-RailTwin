#!/bin/zsh
# Run one track's milestone labels sequentially in its worktree (or in the main checkout for "main").
#   ./run_track.sh <track> <LABEL> [LABEL ...]
#   MODEL=claude-haiku-5-5 ./run_track.sh r2-riyadh REGION_RIYADH        # model override for bulk tracks
#   WT=0 ./run_track.sh main R0                                            # run in the main checkout, no worktree
# Labels map to prompts/<LABEL>.md. The run ends when docs/status/<track>.md contains "<LABEL>: done"
# or "<LABEL>: blocked - ...". Rate limits sleep 15 minutes and retry (4 tries). Every run appends a
# row to docs/cost-log.md via common.cost_log (list-price USD from the stream-json result).
# v1.4 (31 Oct 2026, CP4 G2a): per-run runaway guard line USD 60 list (was 25) -> logs/orch/PAUSE.
# v1.2 (31 Oct 2026): retries only on a rate-limit error; a run that ends without a status line stops (rc 3). RESUME=1 relaunches with the resume notice.
# Adapted from TrafficTwin/run_track.sh (Apache-2.0).
set -u; setopt null_glob
cd "$(dirname "$0")"; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
LOG=$ROOT/logs/orch; mkdir -p "$LOG" "$ROOT/docs/status"
MODEL=${MODEL:-claude-opus-5-5}
WT=${WT:-1}
note(){ echo "$(date '+%F %T') $*" | tee -a "$LOG/orchestrator.log"; }

setup_wt(){ # track -> ensures .worktrees/<track> exists on branch <track>, with data symlinks and a synced venv
  local t=$1 wt=$ROOT/.worktrees/$1
  if [[ ! -d $wt ]]; then
    git -C "$ROOT" show-ref --quiet "refs/heads/$t" || git -C "$ROOT" branch "$t" main
    git -C "$ROOT" worktree add "$wt" "$t" >> "$LOG/orchestrator.log" 2>&1 || { note "worktree $t failed"; return 1; }
  fi
  mkdir -p "$wt/logs" "$wt/runs" "$wt/docs/status" "$wt/data"
  for d in osm jeddah traffictwin ksa; do
    [[ -e $ROOT/data/$d && ! -e $wt/data/$d ]] && ln -s "$ROOT/data/$d" "$wt/data/$d"
  done
  (cd "$wt" && uv sync -q >> "$LOG/orchestrator.log" 2>&1) || note "uv sync in $t reported an error (continuing)"
  note "worktree $t ready"
}

run_prompt(){ # dir track label promptfile
  local dir=$1 track=$2 label=$3 pf=$4 tries=0 rc body out t0 t1
  [[ -f $pf ]] || { note "$track $label: prompt file $pf missing"; return 1; }
  while (( tries < 4 )); do tries=$((tries+1))
    if (( tries == 1 )) && [[ ${RESUME:-0} != 1 ]] && ! grep -qE "^[\`*_ ]*${label}:" "$dir/docs/status/$track.md" 2>/dev/null; then
      body="$(cat "$ROOT/prompts/_common.md"; echo; echo "Your track is \`$track\`; your milestone label is \`$label\`."; echo; cat "$pf")"
    else
      body="$(cat "$ROOT/prompts/_common.md"; echo; sed "s/M<n>/$label/g; s/<track>/$track/g" "$ROOT/prompts/_resume.md"; echo; echo "Your track is \`$track\`; your milestone label is \`$label\`."; echo; cat "$pf")"
    fi
    out="$LOG/$track-$label-try$tries.jsonl"; t0=$(date +%s)
    note "$track $label try $tries start (model $MODEL)"
    (cd "$dir" && claude -p "$body" --model "$MODEL" --dangerously-skip-permissions --verbose --output-format stream-json < /dev/null > "$out" 2>&1); rc=$?
    t1=$(date +%s); note "$track $label try $tries end rc=$rc ($(( (t1-t0)/60 )) min)"
    (cd "$ROOT" && uv run python -m common.cost_log add "$out" --track "$track" --label "$label" --try "$tries" --status-file "$dir/docs/status/$track.md" >> "$LOG/orchestrator.log" 2>&1) || note "cost log failed for $out"
    # Runaway guard (CP3, Tariq 31 Oct 2026): a single run above USD 25 list pauses the orchestrator (logs/orch/PAUSE) and is reported.
    usd=$(cd "$ROOT" && uv run python - "$out" <<'PY'
import json,sys
u=0.0
for line in open(sys.argv[1],encoding="utf-8",errors="ignore"):
    if '"type":"result"' in line or '"type": "result"' in line:
        try: u=float(json.loads(line).get("total_cost_usd") or 0)
        except Exception: pass
print(f"{u:.2f}")
PY
)
    if (( $(echo "${usd:-0} > ${RUN_GUARD_USD:-60}" | bc -l) )); then note "RUNAWAY GUARD: $track $label try $tries cost USD $usd > ${RUN_GUARD_USD:-60}; PAUSE flag set"; echo "$(date '+%F %T') $track $label USD $usd" >> "$LOG/PAUSE"; fi
    grep -qE "^[\`*_ ]*${label}: done" "$dir/docs/status/$track.md" 2>/dev/null && { note "$track $label DONE"; return 0; }
    grep -qE "^[\`*_ ]*${label}: blocked" "$dir/docs/status/$track.md" 2>/dev/null && { note "$track $label BLOCKED"; return 2; }
    if tail -c 30000 "$out" | grep -qiE '"is_error":\s*true' && tail -c 30000 "$out" | grep -qiE '"result":"[^"]*(rate.?limit|overloaded|usage limit|too many requests)'; then note "rate-limited; sleeping 15 min"; sleep 900; continue; fi
    # CP2 condition (Tariq, 31 Oct 2026): a run that ends without a status line is NOT retried blindly.
    note "$track $label ENDED WITHOUT STATUS LINE (rc=$rc, try $tries): stopped for the coordinator; resume manually with RESUME=1"
    return 3
  done; note "$track $label FAILED after $tries tries"; return 1; }

track=$1; shift
if [[ $track == main || $WT == 0 ]]; then dir=$ROOT; else setup_wt "$track" || exit 1; dir=$ROOT/.worktrees/$track; fi
for label in "$@"; do
  run_prompt "$dir" "$track" "$label" "$ROOT/prompts/$label.md"; rc=$?
  (( rc == 0 )) || { note "$track stops at $label (rc=$rc)"; exit $rc; }
done
note "$track finished"
