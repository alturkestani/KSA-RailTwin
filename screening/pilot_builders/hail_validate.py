# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/hail-scratch/validate.py (last modified 2026-10-30 21:27 +03, pilot run PILOT_REGION_HAIL).
# Role: validation only (no output files).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Validate pilot-hail register against RegionRow (pilot pop_type 'secondary' allowed locally; common/ untouched)."""

import sys
from typing import Literal
from pathlib import Path
import pandas as pd

sys.path.insert(0, "./")
from common.schemas import RegionRow, _plain
from pydantic import Field

PILOT_EXTRA = {
    "threshold_50k",
    "pilot_sample",
    "sample_reason",
    "nearest_metro_tier",
    "primary_to_find",
    "terrain_basis",
    "assumption_id",
    "road_min_method",
    "dist_method",
    "notes",
}


class PilotRegionRow(RegionRow):
    pop_type: Literal["official", "derived", "grid", "secondary"] | None = None


path = Path(sys.argv[1])
df = pd.read_parquet(path)
print("rows", len(df), "columns", len(df.columns))
ok = 0
for rec in df.to_dict(orient="records"):
    base = {k: _plain(v) for k, v in rec.items() if k not in PILOT_EXTRA}
    PilotRegionRow.model_validate(base)
    ok += 1
print("RegionRow (pilot pop_type) validated:", ok)
csv = pd.read_csv(path.with_suffix(".csv"))
assert len(csv) == len(df) and list(csv["name_en"]) == list(df["name_en"]), (
    "parquet and csv disagree"
)
print("parquet/csv agree: rows", len(csv), "ids", "match")
print(
    "governorates_listed (centres):",
    int(df[df["is_governorate_centre"]]["governorate"].nunique()),
    "attr:",
    df.attrs,
)
