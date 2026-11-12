# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/najran_work/md.py (last modified 2026-10-30 22:02 +03, pilot run PILOT_REGION_NAJRAN).
# Role: wrote the region documents.
# Outputs named in the code: cities/ksa/regions/pilot-najran.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import pandas as pd, math

df = pd.read_parquet("cities/ksa/regions/pilot-najran.parquet")


def f(v, nd=1):
    if v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NA:
        return "—"
    return f"{v:,.{nd}f}" if isinstance(v, float) else str(v)


def pop(r):
    if r["population"] is None or pd.isna(r["population"]):
        return "— (not sourced)"
    return f"{int(r['population']):,} ({r['pop_type']}, {int(r['pop_year'])}, {r['pop_source']})"


def roles(r):
    rs = r["economic_roles"]
    if rs is None or len(rs) == 0:
        return "—"
    return "; ".join(f"{x['role']} ({x['source']})" for x in rs)


def yn(b):
    return "yes" if b else "no"


A = [
    "| name (EN) | name (AR) | governorate | centre | OSM id (type) | lat, lon | population (pop_type, year, source) | ≥50k | ≥10k | ≥5k | pilot sample |",
    "|---|---|---|---|---|---|---|---|---|---|---|",
]
for _, r in df.iterrows():
    A.append(
        f"| {r['name_en']} | {r['name_ar']} | {r['governorate']} ({r['governorate_ar']}) | {yn(r['is_governorate_centre'])} | n{int(r['osm_id'])} ({r['osm_place_tag'] or '—'}) | {r['lat']:.5f}, {r['lon']:.5f} | {pop(r)} | {yn(r['threshold_50k'])} | {yn(r['tag_10k'])} | {yn(r['tag_5k'])} | {yn(r['pilot_sample'])} |"
    )
B = [
    "| name (EN) | dist existing km (method: haversine) | nearest existing | committed km | dist metro km | nearest metro (tier) | economic roles (source) | terrain (assumed) | screened | exclusion reason |",
    "|---|---|---|---|---|---|---|---|---|---|",
]
for _, r in df.iterrows():
    terr = f"{r['terrain_class']} (A-najran-terrain-001)"
    B.append(
        f"| {r['name_en']} | {f(r['dist_existing_km'])} | {r['nearest_existing']} | not computed (no committed geometry) | {f(r['dist_metro_km'])} | {r['nearest_metro']} | {roles(r)} | {terr} | {yn(r['screened'])} | {('—' if r['exclusion_reason'] is None or pd.isna(r['exclusion_reason']) else r['exclusion_reason'])} |"
    )
open("/tmp/najran_work/tableA.md", "w", encoding="utf-8").write("\n".join(A) + "\n")
open("/tmp/najran_work/tableB.md", "w", encoding="utf-8").write("\n".join(B) + "\n")
print("\n".join(A))
print()
print("\n".join(B))
