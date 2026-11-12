# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/najran_work/dist.py (last modified 2026-10-30 21:58 +03, pilot run PILOT_REGION_NAJRAN).
# Role: distance calculations (printed, copied into the register).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, math, re

R = 6371.0088


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(d))


places = {}
for line in open("/tmp/najran_places.geojsonseq", encoding="utf-8"):
    line = line.strip().lstrip("\x1e")
    if not line:
        continue
    f = json.loads(line)
    p = f["properties"]
    lon, lat = f["geometry"]["coordinates"]
    places[f["id"]] = (
        p.get("place"),
        p.get("name"),
        p.get("name:en"),
        lat,
        lon,
        p.get("population"),
    )
# metro centres: pick the largest 'city'/'town' node by name (OSM)
names = {
    "Riyadh": "الرياض",
    "Jeddah": "جدة",
    "Makkah": "مكة المكرمة",
    "Madinah": "المدينة المنورة",
    "Dammam": "الدمام",
    "Khobar": "الخبر",
    "Dhahran": "الظهران",
    "Taif": "الطائف",
    "Buraidah": "بريدة",
    "Tabuk": "تبوك",
    "Abha": "أبها",
    "Khamis Mushait": "خميس مشيط",
    "Jazan": "جازان",
    "Najran": "نجران",
}
print("metro candidates:")
for en, ar in names.items():
    c = [(k, v) for k, v in places.items() if v[1] == ar and v[0] in ("city", "town")]
    print(en, [(k, v[0], round(v[3], 4), round(v[4], 4)) for k, v in c])
