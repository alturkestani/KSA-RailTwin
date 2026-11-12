# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/qassim_build/validate.py (last modified 2026-10-30 21:32 +03, pilot run PILOT_REGION_QASSIM).
# Role: validation only (no output files).
# Outputs named in the code: cities/ksa/regions/pilot-qassim.csv, cities/ksa/regions/pilot-qassim.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import sys, math, json

sys.path.insert(0, "./")
import pandas as pd
from typing import Literal
from pydantic import ConfigDict, Field
from common.schemas import RegionRow

df = pd.read_parquet("./cities/ksa/regions/pilot-qassim.parquet")
known = set(RegionRow.model_fields)


def clean(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "tolist"):
        return v.tolist()
    return v


rows = [{k: clean(v) for k, v in r.items()} for r in df.to_dict(orient="records")]
# 1 canonical
canon_fail = []
for r in rows:
    sub = {k: v for k, v in r.items() if k in known}
    sub["economic_roles"] = [dict(x) for x in (sub.get("economic_roles") or [])]
    sub["sources"] = list(sub.get("sources") or [])
    try:
        RegionRow.model_validate(sub)
    except Exception as e:
        canon_fail.append((r["name_en"], str(e).splitlines()[0][:160]))
print("CANONICAL RegionRow: fail", len(canon_fail), "of", len(rows))
for f in canon_fail[:3]:
    print("  ", f)


# 2 pilot extension: pop_type secondary + extra columns allowed
class PilotRow(RegionRow):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    pop_type: Literal["official", "derived", "grid", "secondary"] | None = None


ok = 0
errs = []
for r in rows:
    sub = {k: v for k, v in r.items() if k in known or k not in ()}
    sub["economic_roles"] = [dict(x) for x in (sub.get("economic_roles") or [])]
    sub["sources"] = list(sub.get("sources") or [])
    try:
        PilotRow.model_validate(sub)
        ok += 1
    except Exception as e:
        errs.append((r["name_en"], str(e).splitlines()[:3]))
print("PILOT extension (secondary + extras): pass", ok, "of", len(rows), errs[:3])
# 3 parquet vs csv agreement
csv = pd.read_csv("./cities/ksa/regions/pilot-qassim.csv")
print(
    "parquet rows", len(df), "csv rows", len(csv), "same ids", list(df.name_en) == list(csv.name_en)
)
