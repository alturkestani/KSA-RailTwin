# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/hail-scratch/match.py (last modified 2026-10-30 21:24 +03, pilot run PILOT_REGION_HAIL).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, sys

names_ar = [
    "الغزالة",
    "الغزالة",
    "الحائط",
    "الشملي",
    "الشملى",
    "الشنان",
    "السليمي",
    "بقعاء",
    "حائل",
    "موقق",
    "سميراء",
    "الاجفر",
    "الحفير",
    "الحليفة",
    "الخطة",
    "القاعد",
    "النيصية",
    "الروضة",
    "جبة",
    "منيفة",
    "تربة",
    "الروضه",
    "الحفيرة",
    "عقلة",
    "الغزالة",
]


def walk(path):
    for line in open(path, encoding="utf-8"):
        line = line.strip().lstrip("\x1e")
        if not line:
            continue
        yield json.loads(line)


print("== place nodes matching Hail names")
for f in walk("places.geojsonseq"):
    p = f["properties"]
    ar = p.get("name:ar") or p.get("name") or ""
    if any(n in ar for n in names_ar) and p.get("place") in (
        "city",
        "town",
        "village",
        "hamlet",
        "isolated_dwelling",
        "suburb",
        "neighbourhood",
        "locality",
    ):
        print(
            f.get("id"),
            p.get("place"),
            "|",
            p.get("name:ar"),
            "|",
            p.get("name:en") or p.get("name"),
            "|",
            p.get("population"),
            "|",
            f["geometry"]["coordinates"],
        )
print("== rail stations in bbox")
for f in walk("rail_stations.geojsonseq"):
    p = f["properties"]
    print(
        f.get("id"),
        p.get("railway"),
        "|",
        p.get("name:ar"),
        "|",
        p.get("name:en") or p.get("name"),
        "|",
        p.get("operator"),
        "|",
        f["geometry"]["coordinates"],
    )
