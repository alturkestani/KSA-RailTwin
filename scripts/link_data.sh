#!/usr/bin/env bash
# Create the read-only data symlinks into the TrafficTwin checkout (no copies, no downloads).
#   ./scripts/link_data.sh            (also `make data-links`)
# TRAFFICTWIN overrides the checkout location. Idempotent: existing links are left alone.
set -euo pipefail
cd "$(dirname "$0")/.."
TT=${TRAFFICTWIN:-"$HOME/Documents/Projects/TrafficTwin"}
[[ -d $TT ]] || { echo "TrafficTwin checkout not found at $TT (set TRAFFICTWIN=...)" >&2; exit 1; }
mkdir -p data
link(){ # name target
  if [[ -L data/$1 ]]; then echo "data/$1 -> $(readlink "data/$1") (kept)";
  elif [[ -e data/$1 ]]; then echo "data/$1 exists and is not a symlink; not touching it" >&2; exit 1;
  else ln -s "$2" "data/$1"; echo "data/$1 -> $2"; fi
}
link osm "$TT/data/osm"
link jeddah "$TT/data/jeddah"
link traffictwin "$TT"
