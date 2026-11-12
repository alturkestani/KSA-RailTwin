# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/hail-scratch/dist.py (last modified 2026-10-30 21:24 +03, pilot run PILOT_REGION_HAIL).
# Role: distance calculations (printed, copied into the register).
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


# search for Al-Ha'it (الحائط) more widely
for f in walk("places2.geojsonseq"):
    p = f["properties"]
    c = f["geometry"]["coordinates"]
    if f["geometry"]["type"] != "Point":
        continue
    s = json.dumps(p, ensure_ascii=False)
    if (
        "حائط" in s
        or "Ha'it" in s
        or "Haʼit" in s
        or "Hayt" in s
        or "Hait" in s
        or "Ha'yt" in s
        or "Ha'it" in s.lower()
        or "al hait" in s.lower()
        or "al hayt" in s.lower()
    ):
        print("HAIT?", f["id"], p.get("place"), p.get("name:en"), p.get("name:ar"), c)
