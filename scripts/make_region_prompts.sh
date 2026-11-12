#!/usr/bin/env bash
# Generate the per-region, integrate and verify prompts from their templates. Idempotent: re-running
# overwrites the generated files (they are derived; edit the templates, not the outputs).
#   ./scripts/make_region_prompts.sh            (from the repo root; also `make region-prompts`)
# Placeholders: {{REGION}} English name, {{REGION_AR}} Arabic name, {{SLUG}} region-sweep slug
# (lower-case, underscores, as in .claude/skills/region-sweep/SKILL.md), {{UPPER}} the label suffix used
# by orchestrate.sh (RIYADH ... AL_JOUF), {{PHASE}} / {{LABEL}} for integrate and verify prompts.
set -euo pipefail
cd "$(dirname "$0")/.."
P=prompts

# UPPER|slug|English|Arabic  (order = orchestrate.sh)
REGIONS=(
  "RIYADH|riyadh|Riyadh|الرياض"
  "MAKKAH|makkah|Makkah|مكة المكرمة"
  "MADINAH|madinah|Madinah|المدينة المنورة"
  "EASTERN|eastern|Eastern Province|المنطقة الشرقية"
  "QASSIM|qassim|Qassim|القصيم"
  "ASIR|asir|Asir|عسير"
  "TABUK|tabuk|Tabuk|تبوك"
  "HAIL|hail|Hail|حائل"
  "NORTHERN_BORDERS|northern_borders|Northern Borders|الحدود الشمالية"
  "JAZAN|jazan|Jazan|جازان"
  "NAJRAN|najran|Najran|نجران"
  "AL_BAHA|al_baha|Al-Baha|الباحة"
  "AL_JOUF|al_jouf|Al-Jouf|الجوف"
)

render() { # template out  key=value ...
  local tpl=$1 out=$2; shift 2
  local text; text=$(<"$tpl")
  for kv in "$@"; do
    local k=${kv%%=*} v=${kv#*=}
    text=${text//\{\{$k\}\}/$v}
  done
  printf '%s\n' "$text" > "$out"
}

n=0
for r in "${REGIONS[@]}"; do
  IFS='|' read -r UP SLUG EN AR <<< "$r"
  render "$P/REGION_TEMPLATE.md"       "$P/REGION_$UP.md"       "UPPER=$UP" "SLUG=$SLUG" "REGION=$EN" "REGION_AR=$AR"
  render "$P/PILOT_REGION_TEMPLATE.md" "$P/PILOT_REGION_$UP.md" "UPPER=$UP" "SLUG=$SLUG" "REGION=$EN" "REGION_AR=$AR"
  n=$((n+2))
done
for ph in R1 R2 R3 R4 R5 R6 R7 R8 R9; do
  render "$P/INTEGRATE_TEMPLATE.md" "$P/INTEGRATE_$ph.md" "PHASE=$ph"; n=$((n+1))
done
for lb in R0 R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 PILOT_MERGE DATASCOUT_1H; do
  render "$P/VERIFY_TEMPLATE.md" "$P/VERIFY_$lb.md" "LABEL=$lb"; n=$((n+1))
done
echo "generated $n prompt files under $P/"
