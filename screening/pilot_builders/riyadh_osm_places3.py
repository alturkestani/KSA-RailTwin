# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/rs/osm_places3.py (last modified 2026-10-30 21:16 +03, pilot run PILOT_REGION_RIYADH).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, time, urllib.parse, urllib.request

UA = "KSA-RailTwin-pilot/0.1 (non-commercial research; screening pilot)"
qs = [
    ("Al Kharj", "city"),
    ("Al-Kharj", "town"),
    ("Az Zulfi", "town"),
    ("Zulfi", "city"),
    ("Shaqra", "town"),
    ("Quwayiyah", "town"),
    ("As Sulayyil", "town"),
    ("Hautat Bani Tamim", "town"),
    ("Wadi ad Dawasir", "city"),
    ("Ad Dilam", "town"),
    ("Huraymila", "town"),
    ("Huraymila", "town"),
]
for q, ft in qs:
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"format": "jsonv2", "limit": 5, "countrycodes": "sa", "q": q, "featuretype": ft}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    print("==", q, ft, len(data))
    for d in data[:2]:
        print(
            "  ",
            d["osm_type"],
            d["osm_id"],
            d["lat"],
            d["lon"],
            d.get("type"),
            d.get("name"),
            "|",
            d["display_name"][:60],
        )
    time.sleep(1.1)
