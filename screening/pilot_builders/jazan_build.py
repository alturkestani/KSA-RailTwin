# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/jz/build/build_pilot.py (last modified 2026-10-30 21:41 +03, pilot run PILOT_REGION_JAZAN).
# Role: built the region register.
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Build the Jazan pilot register (one-off; inputs are cited OSM and citypopulation.de values)."""

import json, math
from pathlib import Path
import pandas as pd

R_KM = 6371.0088  # A-screen-pilot-001: mean Earth radius, great-circle distance


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return round(2 * R_KM * math.asin(math.sqrt(h)), 1)


MAKKAH_STN = (21.4177, 39.7885)  # OSM node 10956967098, Haramain HSR Makkah station (existing)
JIZAN = (16.8947, 42.558)  # OSM node 288992209 (tertiary metro, A-screen-013)
APPROVED_NEAR = {  # other approved metros close enough to matter for Jazan
    "Abha-Khamis Mushait (tier 2)": [(18.2164, 42.5044), (18.3, 42.7333)],
    "Najran (tier 3)": [(17.5439809, 44.2246817)],
}

# (name_en, name_ar, gov_en, gov_ar, centre, osm_id, lat, lon, pop, roles, sample, reason, terrain_override)
POP = "S-jazan-002"
GOV = "S-jazan-001"
OSM = "S-jazan-005"
ROWS = [
    # --- governorate centres (17) ---
    dict(
        name_en="Jizan",
        name_ar="جيزان",
        gov="Jizan",
        gov_ar="جيزان",
        centre=True,
        osm=288992209,
        lat=16.8947,
        lon=42.558,
        pop=173919,
        roles=[
            ("port", "S-jazan-009"),
            ("industrial_city", "S-jazan-009"),
            ("administrative", GOV),
        ],
    ),
    dict(
        name_en="Sabya",
        name_ar="صبيا",
        gov="Sabya",
        gov_ar="صبيا",
        centre=True,
        osm=1237961155,
        lat=17.15023,
        lon=42.6215,
        pop=72086,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Abu Arish",
        name_ar="أبو عريش",
        gov="Abu Arish",
        gov_ar="أبو عريش",
        centre=True,
        osm=8506762133,
        lat=16.9661,
        lon=42.8381,
        pop=69632,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Samtah",
        name_ar="صامطة",
        gov="Samtah",
        gov_ar="صامطة",
        centre=True,
        osm=1237961376,
        lat=16.59722,
        lon=42.94389,
        pop=43301,
        roles=[("administrative", GOV), ("agriculture", "S-jazan-012")],
        sample=True,
        reason="with a sourced economic role (agriculture; secondary source); a governorate centre of 43,301, below 50k (threshold test)",
    ),
    dict(
        name_en="Bish",
        name_ar="بيش",
        gov="Bish",
        gov_ar="بيش",
        centre=True,
        osm=6391743774,
        lat=17.3756,
        lon=42.5372,
        pop=32679,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Ahad al Musarihah",
        name_ar="أحد المسارحة",
        gov="Ahad al Musarihah",
        gov_ar="أحد المسارحة",
        centre=True,
        osm=7699743951,
        lat=16.7107,
        lon=42.9531,
        pop=25670,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Damad",
        name_ar="ضمد",
        gov="Damad",
        gov_ar="ضمد",
        centre=True,
        osm=1237961144,
        lat=17.1051,
        lon=42.7795,
        pop=26079,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Ad Dayer",
        name_ar="الدائر",
        gov="Ad Dayer",
        gov_ar="الدائر",
        centre=True,
        osm=4941110005,
        lat=17.33848,
        lon=43.13289,
        pop=15752,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Al Aridah",
        name_ar="العارضة",
        gov="Al Aridah",
        gov_ar="العارضة",
        centre=True,
        osm=1237961156,
        lat=17.03952,
        lon=43.08371,
        pop=10902,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Al Aydabi",
        name_ar="العيدابي",
        gov="Al Aydabi",
        gov_ar="العيدابي",
        centre=True,
        osm=1237961253,
        lat=17.2352,
        lon=42.9404,
        pop=10357,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Farasan",
        name_ar="فرسان",
        gov="Farasan",
        gov_ar="فرسان",
        centre=True,
        osm=1013176773,
        lat=16.7022,
        lon=42.1183,
        pop=10118,
        roles=[("administrative", GOV), ("tourism", "S-jazan-010"), ("heritage", "S-jazan-011")],
        sample=True,
        reason="with sourced economic roles (island tourism and heritage); island governorate centre, coastal (tests an island settlement)",
        terrain="coastal",
    ),
    dict(
        name_en="Ad Darb",
        name_ar="الدرب",
        gov="Ad Darb",
        gov_ar="الدرب",
        centre=True,
        osm=1237960408,
        lat=17.7334,
        lon=42.2501,
        pop=5216,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Al Tuwal",
        name_ar="الطوال",
        gov="Al Tuwal",
        gov_ar="الطوال",
        centre=True,
        osm=1237961475,
        lat=16.53082,
        lon=42.96901,
        pop=4671,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Al Harth",
        name_ar="الحرث",
        gov="Al Harth",
        gov_ar="الحرث",
        centre=True,
        osm=None,
        lat=16.7842,
        lon=43.1529,
        pop=None,
        roles=[("administrative", GOV)],
        unmapped=True,
    ),
    dict(
        name_en="Ar Rayth",
        name_ar="الريث",
        gov="Ar Rayth",
        gov_ar="الريث",
        centre=True,
        osm=1237961077,
        lat=17.60394,
        lon=42.85668,
        pop=None,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Harub",
        name_ar="هروب",
        gov="Harub",
        gov_ar="هروب",
        centre=True,
        osm=1237961726,
        lat=17.43983,
        lon=42.89273,
        pop=None,
        roles=[("administrative", GOV)],
    ),
    dict(
        name_en="Fayfa",
        name_ar="فيفا",
        gov="Fayfa",
        gov_ar="فيفا",
        centre=True,
        osm=1237961319,
        lat=17.26329,
        lon=43.1067,
        pop=None,
        roles=[("administrative", GOV)],
        terrain="escarpment_mountain",
    ),
    # --- non-centre sample towns (5k-50k) ---
    dict(
        name_en="Abu as Sadad",
        name_ar="أبو السداد",
        gov="Ad Darb",
        gov_ar="الدرب",
        centre=False,
        osm=7699743950,
        lat=17.72522,
        lon=42.22878,
        pop=9940,
        roles=[],
        sample=True,
        reason="schema edge: non-centre town (9,940) larger than its governorate centre Ad Darb (5,216); no sourced economic role",
    ),
    dict(
        name_en="Al Zabyah",
        name_ar="الظبية",
        gov="Sabya",
        gov_ar="صبيا",
        centre=False,
        osm=1237961139,
        lat=17.11748,
        lon=42.66728,
        pop=11287,
        roles=[],
        sample=True,
        reason="without a sourced economic role; about 5 km from Sabya (72,086, a 50k town): tests a town in a large town's reach",
    ),
    dict(
        name_en="Misliyah",
        name_ar="مسلية",
        gov="Bish",
        gov_ar="بيش",
        centre=False,
        osm=1237961012,
        lat=17.45988,
        lon=42.5572,
        pop=5559,
        roles=[],
        sample=True,
        reason="without a sourced economic role; 5,000-10,000 band (tag_5k only): tests the 5k sensitivity tag and the tag_10k exclusion",
    ),
]


# terrain: A-screen-pilot-002 (assumed). Coastal Tihama plain for longitudes below 42.75; mixed foothills east of it;
# Fayfa Mountains overridden to escarpment_mountain (S-jazan-013).
def terrain(r):
    if r.get("terrain"):
        return r["terrain"], "override"
    return ("coastal" if r["lon"] < 42.75 else "mixed"), "assumed"


out = []
for r in ROWS:
    pop = r["pop"]
    d_exist = hav((r["lat"], r["lon"]), MAKKAH_STN)
    d_metro = hav((r["lat"], r["lon"]), JIZAN)
    # nearest approved metro across the checked set (Jizan, Abha-Khamis Mushait, Najran)
    best = ("Jazan (tertiary, A-screen-013)", 3, d_metro)
    for name, pts in APPROVED_NEAR.items():
        d = min(hav((r["lat"], r["lon"]), p) for p in pts)
        if d < best[2]:
            best = (name, int(name.split("tier ")[1][0]), d)
    terr, terr_basis = terrain(r)
    sources = [OSM, GOV if r["centre"] else None]
    if r.get("unmapped"):
        sources.append("S-jazan-006")
    else:
        sources.append(OSM)
    sources += [POP] if pop is not None else []
    sources += ["S-jazan-008"]
    sources = [s for s in dict.fromkeys(sources) if s]  # dedupe, keep order
    for role, src in r["roles"]:
        if src not in sources:
            sources.append(src)
    row = dict(
        name_en=r["name_en"],
        name_ar=r["name_ar"],
        region="jazan",
        governorate=r["gov"],
        governorate_ar=r["gov_ar"],
        is_governorate_centre=r["centre"],
        osm_id=r["osm"],
        lat=r["lat"],
        lon=r["lon"],
        population=pop,
        pop_source=POP if pop is not None else None,
        pop_year=2022 if pop is not None else None,
        pop_type="secondary" if pop is not None else None,
        tag_10k=bool(pop is not None and pop >= 10000),
        tag_5k=bool(pop is not None and pop >= 5000),
        threshold_50k=bool(pop is not None and pop >= 50000),
        dist_existing_km=d_exist,
        road_min_existing=None,
        nearest_existing="Haramain HSR, Makkah station (existing)",
        dist_committed_km=None,
        road_min_committed=None,
        nearest_committed=None,
        nearest_committed_station=None,
        dist_metro_km=best[2],
        road_min_metro=None,
        nearest_metro=best[0],
        nearest_metro_tier=best[1],
        economic_roles=[{"role": ro, "source": sr} for ro, sr in r["roles"]],
        terrain_class=terr,
        terrain_basis=(
            "S-jazan-013 + A-screen-pilot-002"
            if terr_basis == "assumed"
            else "S-jazan-013 (cited; override)"
        ),
        screened=True,
        exclusion_reason=None,
        sources=sources,
        fixture=False,
        pilot_sample=bool(r.get("sample", False)),
        sample_reason=r.get("reason", ""),
        primary_to_find=(
            "GASTAT Census 2022 locality table (S-090 unreachable)"
            if pop is not None
            else "GASTAT Census 2022 population and governorate membership (S-090)"
        ),
        road_min_method="pending R1a skims",
        dist_method="haversine (A-screen-pilot-001)",
    )
    out.append(row)

df = pd.DataFrame(out)
df["osm_id"] = df["osm_id"].astype("Int64")
df["population"] = df["population"].astype("Int64")
df["pop_year"] = df["pop_year"].astype("Int64")
Path("/tmp/jz/build/rows.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(
    df[
        [
            "name_en",
            "governorate",
            "is_governorate_centre",
            "population",
            "tag_5k",
            "tag_10k",
            "threshold_50k",
            "dist_existing_km",
            "dist_metro_km",
            "nearest_metro",
            "terrain_class",
            "pilot_sample",
        ]
    ].to_string()
)
print(
    "rows",
    len(df),
    "governorates",
    df.governorate.nunique(),
    "centres",
    int(df.is_governorate_centre.sum()),
)
