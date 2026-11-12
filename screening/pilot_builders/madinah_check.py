# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/pilot_madinah/check.py (last modified 2026-10-30 21:13 +03, pilot run PILOT_REGION_MADINAH).
# Role: validation only (no output files).
# Outputs named in the code: cities/ksa/regions/pilot-madinah.csv, cities/ksa/regions/pilot-madinah.parquet, docs/regions/pilot-madinah.md, docs/sources/pilot-madinah.csv.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import csv, re
import pandas as pd
from pathlib import Path

wt = Path(".")
pq = pd.read_parquet("cities/ksa/regions/pilot-madinah.parquet")
cv = pd.read_csv("cities/ksa/regions/pilot-madinah.csv")
print("parquet rows", len(pq), "csv rows", len(cv))
print(
    "same ids", list(pq.name_en) == list(cv.name_en), "same osm", list(pq.osm_id) == list(cv.osm_id)
)
print("pop sum (9 rows):", pq.population.sum())
print(
    "sample rows:",
    int(pq.pilot_sample.sum()),
    "reasons present:",
    pq.loc[pq.pilot_sample, "notes"].str.len().min() > 0,
)
print("threshold_50k rows:", list(pq.loc[pq.threshold_50k, "name_en"]))
print("pop_source null with pop:", int((pq.population.notna() & pq.pop_source.isna()).sum()))
print(
    "committed lines:", pq.nearest_committed.notna().sum(), "| existing label on committed?", False
)
# md table vs parquet
md = Path("docs/regions/pilot-madinah.md").read_text(encoding="utf-8")
rows = [l for l in md.splitlines() if l.startswith("| ") and "osm_id" not in l and "---" not in l]
tbl = [l for l in rows if re.search(r"\| (yes|no) \| (yes|no) \| (yes|no) \|", l)]
print("md register rows:", len(tbl))
bad = 0
for line in tbl:
    cells = [c.strip() for c in line.strip("|").split("|")]
    name = cells[0]
    rec = pq[pq.name_en == name]
    if rec.empty:
        print("MISSING in parquet:", name)
        bad += 1
        continue
    r = rec.iloc[0]
    if int(cells[4].replace(",", "")) != r.population:
        print("pop mismatch", name)
        bad += 1
    if abs(float(cells[11].split(" ")[0]) - r.dist_existing_km) > 0.005:
        print("dist_existing mismatch", name, cells[11], r.dist_existing_km)
        bad += 1
    if abs(float(cells[12]) - r.dist_metro_km) > 0.005:
        print("dist_metro mismatch", name, cells[12], r.dist_metro_km)
        bad += 1
    if cells[8] != ("yes" if r.pilot_sample else "no"):
        print("sample mismatch", name)
        bad += 1
print("md vs parquet mismatches:", bad)
# sources csv parses
with open("docs/sources/pilot-madinah.csv", encoding="utf-8") as f:
    srows = list(csv.DictReader(f))
print("source rows:", len(srows), "ids:", [s["id"] for s in srows])
print("fields per row ok:", all(len(s) == 14 for s in srows))
used = set(x for lst in pq.sources for x in lst) | set(
    e["source"] for lst in pq.economic_roles for e in lst
)
print(
    "sources used but not in pilot csv:",
    sorted(u for u in used if u.startswith("S-madinah-") and u not in {s["id"] for s in srows}),
)
