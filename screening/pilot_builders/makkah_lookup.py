# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/pilot_makkah/lookup.py (last modified 2026-10-30 21:07 +03, pilot run PILOT_REGION_MAKKAH).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, time, urllib.parse, urllib.request, sys

UA = "KSA-RailTwin-pilot/1.0 (non-commercial research; contact via repository owner)"
names = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
for n in names:
    q = urllib.parse.quote(n + ", Saudi Arabia")
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=3&countrycodes=sa"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        res = [{"error": str(e)}]
    print("##", n)
    for r in res[:3]:
        print(
            "  ",
            r.get("osm_type"),
            r.get("osm_id"),
            r.get("class"),
            r.get("type"),
            r.get("lat"),
            r.get("lon"),
            (r.get("display_name") or r.get("error"))[:100],
        )
    time.sleep(1.1)
