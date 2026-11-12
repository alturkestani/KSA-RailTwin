# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/aljouf_osm/calc.py (last modified 2026-10-30 22:05 +03, pilot run PILOT_REGION_AL_JOUF).
# Role: distance calculations (printed, copied into the register).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import json, math

R = 6371.0088


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(d))


g = json.load(open("rail_geom.json"))
verts = []
ways = 0
for e in g["elements"]:
    if e.get("tags", {}).get("railway") != "rail":
        continue
    ways += 1
    for p in e.get("geometry", []):
        verts.append((p["lat"], p["lon"], e["id"]))
print("ways", ways, "vertices", len(verts))
stations = {
    "Al-Jawf (SAR North, OSM node 5920530139)": (29.6485, 39.8377),
    "Al Qurayyat (SAR North, OSM node 7987566890)": (31.4203, 37.289),
}
towns = {
    "Sakaka": (29.9784008, 40.2048, "city node 1236740006"),
    "Al Qurayyat": (31.3333, 37.3419, "city node 1236744823"),
    "Tubarjal": (30.5007, 38.2165, "city node 1236745024"),
    "Dumat al-Jandal": (29.8059, 39.8667, "city node 1236739971"),
    "Suwayr": (30.1173, 40.3888, "town node 1236739864"),
    "Abu Ajram": (29.8899, 39.3058, "village node 5910483362"),
    "An Nabk Abu Qasr": (30.2942, 38.7014, "village node 1236739661"),
    "Al Fayad": (30.6053, 38.0999, "town node 1236744782"),
    "Miqua (unconfirmed)": (29.8210, 38.9234, "village node 5889647646"),
    "Ghata (ambiguous)": (31.2665, 37.5275, "village node 1236744649 (غطي)"),
}
metros = {
    "Tabuk": (28.4012536, 36.5670490),
    "Buraidah": (26.3316670, 43.9716670),
    "Madinah": (24.4711530, 39.6111216),
    "Riyadh": (24.6389160, 46.7160104),
}
for name, (la, lo, src) in towns.items():
    best = min(verts, key=lambda v: hav((la, lo), (v[0], v[1])))
    d_rail = hav((la, lo), (best[0], best[1]))
    st = min(stations.items(), key=lambda s: hav((la, lo), s[1]))
    d_st = hav((la, lo), st[1])
    m = {k: round(hav((la, lo), v), 1) for k, v in metros.items()}
    print(
        f"{name:22s} rail {d_rail:7.2f} km | nearest station {st[0][:12]} {d_st:7.2f} km | metros {m}"
    )
