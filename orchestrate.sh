#!/bin/zsh
# v1.5 (3 Nov 2026, CP6 P11a): r6 single-run guard USD 100.
# v1.4 (31 Oct 2026, CP3): no hard phase caps; runaway guard (run > USD 25, phase > 150 % of estimate) pauses via logs/orch/PAUSE.
# v1.3 (31 Oct 2026): parallel cap counts run_track.sh processes with pgrep (zsh's jobs table is empty inside a command substitution, which let all 13 R2 sweeps start at once).
# KSA Rail Twin orchestrator: runs a named phase of parallel tracks in git worktrees, then integration.
#   caffeinate -dimsu ./orchestrate.sh r1        # R1a..R1d in parallel (four research/data tracks), then INTEGRATE_R1
#   caffeinate -dimsu ./orchestrate.sh r2        # 13 region-scouts in batches of 4 (Haiku), then screening (Opus)
#   caffeinate -dimsu ./orchestrate.sh pilot     # the national pilot of the first session (section 10.4)
# Keep the Mac plugged in, lid open. Logs: logs/orch/. Costs: docs/cost-log.md.
# The coordinator (Cowork) launches this; nothing here pushes, publishes or contacts anyone (rule 7).
set -u; setopt null_glob
cd "$(dirname "$0")"; ROOT=$PWD
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
mkdir -p logs/orch .worktrees docs/status
LOG=$ROOT/logs/orch
note(){ echo "$(date '+%F %T') $*" | tee -a "$LOG/orchestrator.log"; }
OPUS=claude-opus-5-5; HANKO=claude-haiku-5-5; FABLE=claude-fable-5-1
MAX_PARALLEL=${MAX_PARALLEL:-4}   # 18 GB Mac: research tracks are light; compute tracks run alone

# CP3 (Tariq, 31 Oct 2026): no hard phase caps. Runaway guard only: a single run > USD 25 (run_track.sh) or a phase > 150 % of its
# estimate pauses the orchestrator (logs/orch/PAUSE) and the coordinator reports to Tariq. Estimates (USD list) from docs/plan.md section 5.
typeset -A PHASE_EST; PHASE_EST=(r1 150 r2 80 r3 45 r4 90 r5 80 r6 95 r6v3 40 r7 25 r8 75 r9 15 r10 120)   # r4 raised 45 -> 90 by Tariq, 31 Oct 2026 23:55 (phase guard 135); r5 raised 40 -> 80 by Tariq, 3 Nov 2026 (phase guard 120); r6 = 95, the builder's justified estimate per the R6 spec guardrail D (first status line, 3 Nov 2026), recorded by the coordinator
phase_cost(){ # label-prefix...  -> USD sum of matching cost-log rows
  uv run python - "$@" <<'PY'
import csv,sys
pref=sys.argv[1:]; s=0.0
for r in csv.DictReader(open("docs/cost-log.csv",encoding="utf-8")):
    lab=r.get("label","")
    if any(lab==p or lab.startswith(p) for p in pref):
        try: s+=float(r.get("usd_list") or 0)
        except ValueError: pass
print(f"{s:.2f}")
PY
}
guard(){ # phase labels... : stop if PAUSE flag exists or the phase is > 150 % of its estimate
  local ph=$1; shift
  if [[ -f $LOG/PAUSE ]]; then note "PAUSED by the runaway guard ($(tail -1 $LOG/PAUSE)); not launching more runs"; return 1; fi
  local c=$(phase_cost "$@") est=${PHASE_EST[$ph]:-50}
  if (( $(echo "$c > 1.5 * $est" | bc -l) )); then note "RUNAWAY GUARD: phase $ph at USD $c > 150 % of estimate USD $est; PAUSE flag set"; echo "$(date '+%F %T') phase $ph USD $c est $est" >> "$LOG/PAUSE"; return 1; fi
  return 0
}

run_batch(){ # "track:LABEL:MODEL" ... (keeps at most MAX_PARALLEL running; a free slot is refilled at once, no head-of-line blocking)
  local spec t l m
  for spec in "$@"; do
    t=${spec%%:*}; l=${${spec#*:}%%:*}; m=${spec##*:}
    while (( $(pgrep -f "run_track.sh" | wc -l) >= MAX_PARALLEL )); do sleep 20; done
    MODEL=$m ./run_track.sh "$t" "$l" &
    sleep 3
  done
  wait
}

phase=${1:-}
case $phase in
  pilot)
    note "=== pilot: coarse national sweep (13 regions, Hanko bulk) + scoping note ==="
    specs=()
    for r in RIYADH MAKKAH MADINAH EASTERN QASSIM ASIR TABUK HAIL NORTHERN_BORDERS JAZAN NAJRAN AL_BAHA AL_JOUF; do
      specs+=("pilot-${(L)r}:PILOT_REGION_${r}:$HANKO")
    done
    run_batch $specs
    WT=0 MODEL=$OPUS ./run_track.sh main PILOT_MERGE
    ;;
  r1)
    note "=== R1: four foundations tracks in parallel ==="
    # r1a runs two labels in sequence (R1a, then GEO_VERIFY in the same worktree); the others one each
    MODEL=$OPUS ./run_track.sh r1a R1a GEO_VERIFY &
    sleep 3
    run_batch "r1b:R1b:$OPUS" "r1c:R1c:$OPUS" "r1d:R1d:$OPUS"
    wait
    WT=0 MODEL=$OPUS ./run_track.sh main INTEGRATE_R1
    ;;
  r2)
    note "=== R2: 13 region sweeps (Haiku), then the screening analyst, then integration (no phase cap; runaway guard only) ==="
    for r in RIYADH MAKKAH MADINAH EASTERN QASSIM ASIR TABUK HAIL NORTHERN_BORDERS JAZAN NAJRAN AL_BAHA AL_JOUF; do
      guard r2 REGION_ R2 INTEGRATE_R2 || break
      while (( $(pgrep -f "run_track.sh" | wc -l) >= MAX_PARALLEL )); do sleep 20; done
      MODEL=$HANKO ./run_track.sh "r2-${(L)r}" "REGION_${r}" &
      sleep 3
    done
    wait
    guard r2 REGION_ R2 INTEGRATE_R2 && WT=0 MODEL=$OPUS ./run_track.sh main R2
    guard r2 REGION_ R2 INTEGRATE_R2 && WT=0 MODEL=$OPUS ./run_track.sh main INTEGRATE_R2
    ;;
  r6v3)
    note "=== R6_V3: judge v3 (variants) re-run, CP7-3 ==="
    guard r6v3 R6_V3 INTEGRATE_R6_V3 || exit 5
    RUN_GUARD_USD=100 MODEL=$OPUS ./run_track.sh r6v3 R6_V3
    rc=$?; (( rc == 0 )) || { note "R6_V3 ended rc=$rc: INTEGRATE_R6_V3 not launched"; exit 3; }
    guard r6v3 R6_V3 INTEGRATE_R6_V3 || exit 5
    WT=0 MODEL=$OPUS ./run_track.sh main INTEGRATE_R6_V3
    ;;
  r3|r4|r5|r6|r7|r8|r9)
    label=${(U)phase}
    note "=== $label: single compute/analysis track ==="
    guard "$phase" "$label" "INTEGRATE_$label" || exit 5
    if [[ $phase == r6 ]]; then RUN_GUARD_USD=100 MODEL=$OPUS ./run_track.sh "$phase" "$label"; else MODEL=$OPUS ./run_track.sh "$phase" "$label"; fi
    rc=$?; (( rc == 0 )) || { note "$label ended rc=$rc (no status line, blocked, or killed): INTEGRATE_$label not launched; coordinator decides"; exit 3; }
    guard "$phase" "$label" "INTEGRATE_$label" || exit 5
    WT=0 MODEL=$OPUS ./run_track.sh main "INTEGRATE_$label"
    ;;
  verify)
    # Independent red-team pass on the main checkout; label VERIFY_<milestone>, e.g. ./orchestrate.sh verify R0
    WT=0 MODEL=$FABLE ./run_track.sh main "VERIFY_${2:?milestone label}"
    ;;
  *) echo "usage: $0 {pilot|r1|r2|r3..r9|r6v3|verify <LABEL>}"; exit 2 ;;
esac
note "=== orchestrator end ($phase) ==="
