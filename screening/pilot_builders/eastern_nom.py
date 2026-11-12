# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/pilot-eastern-src/nom.py (last modified 2026-10-30 21:08 +03, pilot run PILOT_REGION_EASTERN).
# Role: lookup helper (OSM/Nominatim or census-table extraction).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, sys, time, urllib.parse, urllib.request

UA = "KSA-RailTwin-pilot/0.1 (personal open-source research)"
QUERIES = [
    ("dammam", "الدمام، المنطقة الشرقية"),
    ("hofuf", "الهفوف، المنطقة الشرقية"),
    ("jubail", "الجبيل، المنطقة الشرقية"),
    ("khobar", "الخبر، المنطقة الشرقية"),
    ("hafar", "حفر الباطن، المنطقة الشرقية"),
    ("dhahran", "الظهران، المنطقة الشرقية"),
    ("thuqbah", "الثقبة، المنطقة الشرقية"),
    ("tarout", "تاروت، المنطقة الشرقية"),
    ("qatif", "القطيف، المنطقة الشرقية"),
    ("saihat", "سيهات، المنطقة الشرقية"),
    ("khafji", "الخفجي، المنطقة الشرقية"),
    ("abqaiq", "بقيق، المنطقة الشرقية"),
    ("nariyah", "النعيرية، المنطقة الشرقية"),
    ("qaryat_ulya", "قرية العليا، المنطقة الشرقية"),
    ("ras_tanura", "رأس تنورة، المنطقة الشرقية"),
    ("udayd", "العديد، المنطقة الشرقية"),
    ("bayda", "البيضاء، المنطقة الشرقية"),
    ("rahimah", "رحيمة، المنطقة الشرقية"),
    ("oyun", "العيون، المنطقة الشرقية"),
    ("qaisumah", "القيصومة، حفر الباطن"),
    ("jafr", "الجفر، المنطقة الشرقية"),
    ("safwa", "صفوى، المنطقة الشرقية"),
    ("st_hofuf", "محطة قطار الهفوف"),
    ("st_abqaiq", "محطة قطار بقيق"),
    ("st_dammam", "محطة قطار الدمام"),
]
out = {}
for key, q in QUERIES:
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {
            "q": q,
            "format": "jsonv2",
            "limit": 4,
            "countrycodes": "sa",
            "accept-language": "en",
            "addressdetails": 1,
        }
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    out[key] = [
        {
            "osm_type": d["osm_type"],
            "osm_id": int(d["osm_id"]),
            "lat": float(d["lat"]),
            "lon": float(d["lon"]),
            "class": d.get("category", d.get("class")),
            "type": d.get("addresstype", d.get("type")),
            "name": d.get("name"),
            "display": d["display_name"][:110],
        }
        for d in data
    ]
    time.sleep(1.1)
json.dump(out, open("nominatim.json", "w"), ensure_ascii=False, indent=1)
for k, v in out.items():
    print("==", k)
    for d in v[:3]:
        print(
            "   ",
            d["osm_type"],
            d["osm_id"],
            round(d["lat"], 4),
            round(d["lon"], 4),
            d["class"],
            d["type"],
            "|",
            d["display"],
        )
