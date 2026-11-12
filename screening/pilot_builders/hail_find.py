# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/hail-scratch/find.py (last modified 2026-10-30 21:24 +03, pilot run PILOT_REGION_HAIL).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, math


def walk(p):
    for line in open(p, encoding="utf-8"):
        line = line.strip().lstrip("\x1e")
        if line:
            yield json.loads(line)


def hav(a, b):
    R = 6371.0088
    la1, lo1 = map(math.radians, (a[1], a[0]))
    la2, lo2 = map(math.radians, (b[1], b[0]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(h))


rows = []
for f in walk("places2.geojsonseq"):
    p = f["properties"]
    c = f["geometry"]["coordinates"]
    if f["geometry"]["type"] != "Point":
        continue
    if not (25.0 <= c[1] <= 29.5 and 38.5 <= c[0] <= 44.5):
        continue
    nm = (p.get("name:en") or "") + " | " + (p.get("name:ar") or p.get("name") or "")
    if (
        any(
            k in nm.lower()
            for k in [
                "hait",
                "hayt",
                "ha'it",
                "ha'i",
                "hait",
                "ha'il",
                "hail",
                "shamly",
                "shamli",
                "shaml",
                "sulaym",
                "sulaymi",
                "qa'id",
                "qaid",
                "qa`id",
                "ghazal",
                "ghazaal",
                "khutt",
                "hufayr",
                "jubb",
                "jubah",
                "turub",
                "ajfir",
                "ajfer",
                "baqa",
                "baq`a",
                "baq'a",
                "shanan",
                "shanān",
                "mawqaq",
                "simira",
                "sumayra",
                "sumaira",
                "halifah",
                "hulay",
                "nisiy",
                "nasiy",
                "munifa",
                "rawd",
                "hafir",
                "hufay",
                "khutta",
                "ghazal",
                "الحائط",
                "الشملي",
                "شملي",
                "سميراء",
                "بقعاء",
                "الشنان",
                "تربة",
                "جبة",
                "الاجفر",
                "الغزالة",
                "موقق",
                "السليمي",
            ]
        )
        or p.get("name") is None
        and p.get("name:ar") is None
    ):
        rows.append(
            (
                f["id"],
                p.get("place"),
                p.get("name:en"),
                p.get("name:ar"),
                p.get("population"),
                round(c[0], 4),
                round(c[1], 4),
            )
        )
for r in rows:
    if r[1] in ("city", "town", "village", "hamlet", "locality", "isolated_dwelling"):
        print(r)
