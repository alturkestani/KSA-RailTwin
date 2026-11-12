# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/asir-scripts/extract_places.py (last modified 2026-10-30 21:24 +03, pilot run PILOT_REGION_ASIR).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, sys

LAT = (17.0, 21.0)
LON = (41.0, 44.6)
out = []
with open(sys.argv[1], encoding="utf-8") as f:
    for line in f:
        line = line.strip().lstrip("\x1e")
        if not line:
            continue
        feat = json.loads(line)
        g = feat.get("geometry") or {}
        if g.get("type") != "Point":
            continue
        lon, lat = g["coordinates"]
        if not (LAT[0] <= lat <= LAT[1] and LON[0] <= lon <= LON[1]):
            continue
        p = feat.get("properties", {})
        out.append(
            dict(
                osm_id=int(feat["id"][1:]) if isinstance(feat.get("id"), str) else feat.get("id"),
                place=p.get("place"),
                name=p.get("name"),
                name_en=p.get("name:en"),
                name_ar=p.get("name:ar"),
                population=p.get("population"),
                lat=lat,
                lon=lon,
            )
        )
out.sort(key=lambda d: (d["place"] or "", d["name"] or ""))
for d in out:
    print(json.dumps(d, ensure_ascii=False))
