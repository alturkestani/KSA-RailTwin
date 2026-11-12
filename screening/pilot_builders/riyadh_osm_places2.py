# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/rs/osm_places2.py (last modified 2026-10-30 21:14 +03, pilot run PILOT_REGION_RIYADH).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, time, urllib.parse, urllib.request

UA = "KSA-RailTwin-pilot/0.1 (non-commercial research; screening pilot)"
qs = [
    "Al Kharj",
    "Al Zulfi",
    "Afif",
    "Shaqra",
    "Layla Al Aflaj",
    "Al Quwayiyah",
    "As Sulayyil",
    "Huraymila",
    "Hawtat Bani Tamim",
    "Marat",
    "Wadi ad Dawasir",
    "Ad Diriyah",
    "Dawadmi Riyadh",
]
for q in qs:
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"format": "jsonv2", "limit": 8, "countrycodes": "sa", "q": q + ", Riyadh Region"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    hits = [d for d in data if d["category"] == "place"]
    print("==", q, "place hits:", len(hits))
    for d in hits[:3]:
        print(
            "  ",
            d["osm_type"],
            d["osm_id"],
            d["lat"],
            d["lon"],
            d["type"],
            d.get("name"),
            "|",
            d["display_name"][:60],
        )
    time.sleep(1.1)
