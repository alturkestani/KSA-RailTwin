# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/najran_work/calc.py (last modified 2026-10-30 21:59 +03, pilot run PILOT_REGION_NAJRAN).
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


EXIST_SERVICE_EXCL = {"yard", "siding", "crossover", "spur"}
exist = []
constr = []
for line in open("/tmp/najran_rail.geojsonseq", encoding="utf-8"):
    line = line.strip().lstrip("\x1e")
    if not line:
        continue
    f = json.loads(line)
    g = f["geometry"]
    p = f["properties"]
    if g["type"] != "LineString":
        continue
    if p.get("railway") == "construction" or p.get("construction"):
        constr.append(
            (
                f.get("id"),
                p.get("name", ""),
                p.get("railway"),
                p.get("construction", ""),
                g["coordinates"],
            )
        )
        continue
    if (
        p.get("railway") == "rail"
        and p.get("service") not in EXIST_SERVICE_EXCL
        and p.get("usage") != "industrial"
        and max(x for x, y in g["coordinates"]) <= 51.5
    ):
        exist.append((f.get("id"), p.get("name", ""), p.get("usage", ""), g["coordinates"]))


def nearest(pt, lines):
    best = (1e9, None, None, None)
    for item in lines:
        lid, name, coords = item[0], item[1], item[-1]
        for x, y in coords:
            d = hav(pt, (y, x))
            if d < best[0]:
                best = (d, lid, (name or "(unnamed)"), (y, x))
    return best


targets = {
    "Najran city": (17.54398, 44.22468),
    "Sharurah": (17.49123, 47.11261),
    "Al-Mish alia": (17.75783, 44.46435),
    "Hubuna": (17.85185, 44.02316),
    "Khubash (village node)": (17.54985, 44.74113),
    "Khubash (governorate node)": (17.66667, 45.25),
    "Al-Wadiah": (17.05751, 47.08815),
    "Yadamah": (18.52917, 44.20306),
    "Badr al-Janub": (17.88137, 43.71636),
    "Thar": (17.97488, 44.11082),
}
print("dropped as outside KSA (lon>51.5 vertex):", "see count below")
print("existing rail lines considered:", len(exist), " construction-tagged:", len(constr))
for k, pt in targets.items():
    d, lid, name, where = nearest(pt, exist)
    dc, cid, cname, cw = nearest(pt, constr) if constr else (None, None, None, None)
    print(
        f"{k:28s} existing {d:8.1f} km  {lid} {name[:30]}  @{where[0]:.3f},{where[1]:.3f} | constr {dc if dc is None else round(dc, 1)} {cid} {cname[:20] if cname else ''} {cw and (round(cw[0], 3), round(cw[1], 3))}"
    )
metros = {
    "Riyadh": (24.6389, 46.716),
    "Jeddah": (21.5504, 39.1742),
    "Makkah": (21.42085, 39.82687),
    "Madinah": (24.4712, 39.6111),
    "Dammam": (26.4368, 50.104),
    "Khobar": (26.304, 50.196),
    "Dhahran": (26.2967, 50.1202),
    "Taif": (21.2703, 40.4158),
    "Buraidah": (26.3317, 43.9717),
    "Tabuk": (28.4013, 36.567),
    "Abha": (18.2164, 42.5044),
    "Khamis Mushait": (18.3, 42.7333),
    "Jazan": (16.89472, 42.55798),
    "Najran": (17.54398, 44.22468),
}
tier = {
    "Riyadh": 1,
    "Jeddah": 1,
    "Makkah": 1,
    "Madinah": 1,
    "Dammam": 1,
    "Khobar": 1,
    "Dhahran": 1,
    "Taif": 2,
    "Buraidah": 2,
    "Tabuk": 2,
    "Abha": 2,
    "Khamis Mushait": 2,
    "Jazan": 3,
    "Najran": 3,
}
print("nearest metro (approved set, A-screen-013):")
for k, pt in targets.items():
    ds = sorted((hav(pt, v), m) for m, v in metros.items())[:3]
    print(f"{k:28s}", [(m, round(d, 1), tier[m]) for d, m in ds])
