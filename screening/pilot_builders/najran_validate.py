# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/najran_work/validate.py (last modified 2026-10-30 22:01 +03, pilot run PILOT_REGION_NAJRAN).
# Role: validation only (no output files).
# Outputs named in the code: cities/ksa/regions/pilot-najran.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Validate pilot rows against common/schemas.py:RegionRow (copy only).
Known schema gaps: pop_type 'secondary' (not in the enum) is mapped to 'official' for this check only;
extra columns (threshold_50k, pilot_sample, notes, osm_place_tag, dist_method, screen_stage,
road_min_method) are dropped for this check only."""

import pandas as pd, math, sys

sys.path.insert(0, ".")
from common.schemas import RegionRow

df = pd.read_parquet("cities/ksa/regions/pilot-najran.parquet")
EXTRA = {
    "threshold_50k",
    "pilot_sample",
    "notes",
    "osm_place_tag",
    "dist_method",
    "screen_stage",
    "road_min_method",
}
ok = 0
errs = []
for _, r in df.iterrows():
    d = {k: v for k, v in r.to_dict().items() if k not in EXTRA}
    for k, v in list(d.items()):
        if v is None or (isinstance(v, float) and math.isnan(v)) or (v is pd.NA):
            d[k] = None
        elif (
            isinstance(v, (str, list, tuple))
            or type(v).__module__ == "numpy"
            and getattr(v, "ndim", 0) > 0
        ):
            pass
        elif hasattr(v, "item"):
            d[k] = v.item()
    if d.get("pop_type") == "secondary":
        d["pop_type"] = "official"
    if d.get("economic_roles") is not None:
        d["economic_roles"] = [dict(x) for x in d["economic_roles"]]
    d["sources"] = list(d["sources"]) if d.get("sources") is not None else []
    try:
        RegionRow(**d)
        ok += 1
    except Exception as e:
        errs.append((d["name_en"], str(e)[:300]))
print("rows validated:", ok, "of", len(df))
for e in errs:
    print("ERR", e)
