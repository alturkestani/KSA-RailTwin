# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/pilot-eastern-src/md.py (last modified 2026-10-30 21:13 +03, pilot run PILOT_REGION_EASTERN).
# Role: wrote the region documents.
# Outputs named in the code: cities/ksa/regions/pilot-eastern.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json
import pyarrow.parquet as pq

rows = pq.read_table("cities/ksa/regions/pilot-eastern.parquet").to_pylist()
side = json.load(open("/tmp/pilot-eastern-src/sidecar.json"))


def f(v, nd=1):
    return "—" if v is None else (f"{v:,.{nd}f}" if isinstance(v, float) else f"{v:,}")


def roles(rs):
    return "; ".join(f"{x['role']} ({x['source']})" for x in rs) or "—"


lines = []
lines.append(
    "| ID | name (EN / AR) | governorate | centre | population (2022) | ≥50k | pilot sample | dist. to existing station (km), nearest | dist. to metro (km), nearest | economic roles (source) | screened / exclusion |"
)
lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
for r, s in zip(rows, side):
    pop = "—" if r["population"] is None else f"{r['population']:,}"
    pop_cell = pop if r["population"] is None else f"{pop} ({r['pop_type']}, {r['pop_source']})"
    ex = f"{r['dist_existing_km']:.1f} ({r['nearest_existing'].replace('East line: ', '')})"
    me = f"{r['dist_metro_km']:.1f} ({r['nearest_metro']})"
    scr = "yes" if r["screened"] else f"no: {r['exclusion_reason']}"
    lines.append(
        f"| {s['id']} | {r['name_en']} / {r['name_ar']} | {r['governorate']} | {'yes' if r['is_governorate_centre'] else 'no'} | {pop_cell} | {'yes' if (r['population'] or 0) >= 50000 else 'no'} | {'yes' if s['pilot_sample'] else 'no'} | {ex} | {me} | {roles(r['economic_roles'])} | {scr} |"
    )
open("/tmp/pilot-eastern-src/table.md", "w").write("\n".join(lines) + "\n")
print(len(rows), "rows")
print("\n".join(lines[:3]))
