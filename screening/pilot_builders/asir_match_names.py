# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/asir-scripts/match_names.py (last modified 2026-10-30 21:24 +03, pilot run PILOT_REGION_ASIR).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, sys

NAMES = [
    "أبها",
    "أحد رفيدة",
    "الأمواه",
    "البرك",
    "الحرجة",
    "المجاردة",
    "النماص",
    "بالقرن",
    "بلقرن",
    "بارق",
    "بيشة",
    "خميس مشيط",
    "محايل",
    "محايل عسير",
    "رجال ألمع",
    "سراة عبيدة",
    "تنومة",
    "طريب",
    "تثليث",
    "ظهران الجنوب",
    "العلاية",
    "سبت العلاية",
    "الواديين",
    "الحريضه",
    "بني كبير",
    "القحمه",
    "الباحة",
    "بالقرن",
    "الاثنين",
]
LAT = (17.9, 20.6)
LON = (41.3, 43.9)
seen = []
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.strip().lstrip("\x1e")
    if not line:
        continue
    f = json.loads(line)
    g = f.get("geometry") or {}
    if g.get("type") != "Point":
        continue
    lon, lat = g["coordinates"]
    p = f.get("properties", {})
    if not (LAT[0] <= lat <= LAT[1] and LON[0] <= lon <= LON[1]):
        continue
    if p.get("place") not in (
        "city",
        "town",
        "village",
        "hamlet",
        "suburb",
        "neighbourhood",
        "locality",
        "quarter",
    ):
        continue
    name = p.get("name") or ""
    if name in NAMES or (p.get("name:en") or "").lower().startswith(
        (
            "abha",
            "bish",
            "khamis",
            "muhayil",
            "sarat",
            "tanum",
            "tathlith",
            "zahran",
            "rijal",
            "bariq",
            "balqarn",
            "ahad",
            "al birk",
            "al harj",
            "majarid",
            "an nimas",
            "tarib",
            "amwah",
            "al amwah",
            "sabt",
            "al 'ulay",
            "al alayah",
            "al ulayah",
        )
    ):
        seen.append(
            (
                p.get("place"),
                f.get("id"),
                name,
                p.get("name:en"),
                p.get("population"),
                round(lat, 5),
                round(lon, 5),
            )
        )
for s in sorted(seen, key=lambda x: x[2] or ""):
    print(s)
