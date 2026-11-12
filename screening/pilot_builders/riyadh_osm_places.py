# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/rs/osm_places.py (last modified 2026-10-30 21:11 +03, pilot run PILOT_REGION_RIYADH).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, sys, time, urllib.parse, urllib.request

UA = "KSA-RailTwin-pilot/0.1 (non-commercial research; screening pilot)"
names = {
    "riyadh": "الرياض",
    "al_kharj": "الخرج",
    "majmaah": "المجمعة",
    "dawadmi": "الدوادمي",
    "zulfi": "الزلفي",
    "diriyah": "الدرعية",
    "muzahimiyah": "المزاحمية",
    "afif": "عفيف",
    "rimah": "رماح",
    "uyaynah": "العيينة",
    "jubaylah": "الجبيلة",
    "shaqra": "شقراء",
    "aflaj": "الأفلاج",
    "quwayiyah": "القويعية",
    "dilam": "الدلم",
    "sulayyil": "السليل",
    "rayn": "الرين",
    "durma": "ضرما",
    "huraymila": "حريملاء",
    "hawtah": "حوطة بني تميم",
    "thadiq": "ثادق",
    "ghat": "الغاط",
    "marat": "مرات",
    "wadi_dawasir": "وادي الدواسر",
    "harik": "الحريق",
    "mazari_malqa": "مزارع الملقى",
}
for key, ar in names.items():
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"format": "jsonv2", "limit": 8, "countrycodes": "sa", "q": ar + " منطقة الرياض"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    hits = [d for d in data if d["osm_type"] == "node" and d["category"] == "place"]
    print("==", key, ar, "node hits:", len(hits))
    for d in hits[:3]:
        print(
            "  ",
            d["osm_id"],
            d["lat"],
            d["lon"],
            d["type"],
            d.get("name"),
            "|",
            d["display_name"][:70],
        )
    time.sleep(1.1)
