# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/nbpilot/build_inputs.py (last modified 2026-10-30 21:40 +03, pilot run PILOT_REGION_NORTHERN_BORDERS).
# Role: built the region register.
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, math

R = 6371.0088


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(d))


rail = json.load(open("/tmp/nb_rail.json"))["elements"]
north_named, north_unnamed_branch = [], []
for e in rail:
    t = e.get("tags", {})
    g = e.get("geometry", [])
    if not g:
        continue
    pts = [(p["lat"], p["lon"]) for p in g]
    name = t.get("name", "")
    svc = t.get("service")
    if "قطار الشمال" in name and svc in (None, "spur"):
        north_named.append((e["id"], name, pts))
    elif not name and t.get("railway") == "rail" and t.get("usage") == "branch" and svc is None:
        north_unnamed_branch.append((e["id"], pts))


# only ways that lie inside the Northern Borders box (lat 29-32.5, lon 37.5-41.5) for the Hazm check
def nearest(pt, ways):
    best = (1e9, None, None)
    for wid, *rest in ways:
        pts = rest[-1]
        for p in pts:
            d = hav(pt, p)
            if d < best[0]:
                best = (d, wid, p)
    return best


places = {
    "Arar": (30.9815531, 41.0164788),
    "Rafha": (29.6324189, 43.5178685),
    "Turaif": (31.6725877, 38.6615532),
    "Al-Uwayqilah": (30.3632535, 42.2382351),
    "Rawdat Habas": (29.1503987, 44.3114119),
    "Talah at-Tamiat": (29.8569440, 43.1402780),
    "Sha'bih Nasab": (28.8836507, 44.7397731),
    "Hazm al-Jalamid": (31.280278, 40.104167),
}
metros = {  # name, tier, lat, lon, osm
    "Riyadh": (1, 24.6389160, 46.7160104),
    "Jeddah": (1, 21.5504432, 39.1742363),
    "Makkah": (1, 21.4208470, 39.8268690),
    "Madinah": (1, 24.4711530, 39.6111216),
    "Dammam": (1, 26.4367824, 50.1039991),
    "Taif": (2, 21.2702801, 40.4158308),
    "Buraidah": (2, 26.3316670, 43.9716670),
    "Tabuk": (2, 28.4012536, 36.5670490),
    "Abha": (2, 18.2164282, 42.5043596),
    "Khamis Mushait": (2, 18.3000000, 42.7333330),
    "Jazan": (3, 16.8947190, 42.5579758),
    "Najran": (3, 17.5439809, 44.2246817),
}
out = {}
for n, pt in places.items():
    d_named, wid, vp = nearest(pt, [(w, nm, p) for w, nm, p in north_named])
    d_unn, wid2, vp2 = nearest(pt, [(w, p) for w, p in north_unnamed_branch])
    mets = sorted(((hav(pt, (la, lo)), m, tier) for m, (tier, la, lo) in metros.items()))
    out[n] = dict(
        dist_existing_named_km=round(d_named, 1),
        way=wid,
        vertex=vp,
        dist_unnamed_branch_km=round(d_unn, 1),
        unnamed_way=wid2,
        nearest_metro=mets[0][1],
        metro_km=round(mets[0][0], 1),
        tier=mets[0][2],
        metro_2nd=mets[1][1],
        metro_2nd_km=round(mets[1][0], 1),
    )
print(json.dumps(out, ensure_ascii=False, indent=1))
print("named ways used:", len(north_named), "unnamed branch ways:", len(north_unnamed_branch))
