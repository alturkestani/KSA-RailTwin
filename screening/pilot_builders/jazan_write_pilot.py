# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/jz/build/write_pilot.py (last modified 2026-10-30 21:41 +03, pilot run PILOT_REGION_JAZAN).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: and pilot-jazan.csv, cities/ksa/regions/pilot-jazan.csv, cities/ksa/regions/pilot-jazan.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json
from typing import Literal
from pathlib import Path
import pandas as pd
from common.schemas import RegionRow

REPO = Path("./")
rows = json.loads(Path("/tmp/jz/build/rows.json").read_text(encoding="utf-8"))
for r in rows:
    r["sources"] = list(r["sources"])
    r["fixture"] = False
REG_FIELDS = list(RegionRow.model_fields)


# validation only: the schema has no "secondary" pop_type yet (see status block)
class PilotRow(RegionRow):
    pop_type: Literal["official", "derived", "grid", "secondary"] | None = None


errors = []
for i, r in enumerate(rows):
    base = {k: r[k] for k in REG_FIELDS if k in r}
    try:
        PilotRow(**base)
    except Exception as e:  # noqa: BLE001
        errors.append((r["name_en"], str(e)))
print("RegionRow validation errors:", errors or "none")
assert not errors

df = pd.DataFrame(rows)
for c in ("osm_id", "population", "pop_year"):
    df[c] = df[c].astype("Int64")
ordered = REG_FIELDS + [c for c in df.columns if c not in REG_FIELDS]
df = df[ordered]
out_pq = REPO / "cities/ksa/regions/pilot-jazan.parquet"
df.to_parquet(out_pq, index=False)

csv = df.copy()
csv["economic_roles"] = csv["economic_roles"].apply(lambda v: json.dumps(v, ensure_ascii=False))
csv["sources"] = csv["sources"].apply(lambda v: ";".join(v))
csv.to_csv(REPO / "cities/ksa/regions/pilot-jazan.csv", index=False, encoding="utf-8")
print("wrote", len(df), "rows;", out_pq.name, "and pilot-jazan.csv")
