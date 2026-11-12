# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/hail-scratch/build.py (last modified 2026-10-30 21:28 +03, pilot run PILOT_REGION_HAIL).
# Role: built the region register.
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Build cities/ksa/regions/pilot-hail.{parquet,csv} from OSM coordinates and citypopulation.de figures (secondary)."""

import json, math, sys
from pathlib import Path
import pandas as pd

OUT = Path(sys.argv[1])


def walk(p):
    for line in open(p, encoding="utf-8"):
        line = line.strip().lstrip("\x1e")
        if line:
            yield json.loads(line)


def hav(a, b):
    R = 6371.0088
    la1, lo1 = map(math.radians, (a[1], a[0]))
    la2, lo2 = map(math.radians, (b[1], b[0]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(h))


# OSM place nodes (ids + coords) from the Hail bbox extract
places = []
for f in walk("/tmp/hail-scratch/places2.geojsonseq"):
    if f["geometry"]["type"] == "Point":
        places.append((f["id"], f["properties"], tuple(f["geometry"]["coordinates"])))


def osm_at(lon, lat):
    best = min(places, key=lambda t: (t[2][0] - lon) ** 2 + (t[2][1] - lat) ** 2)
    d = math.hypot(best[2][0] - lon, best[2][1] - lat)
    assert d < 0.005, (lon, lat, d)
    return int(best[0][1:]), best[1]


# existing: North line passenger stations (OSM stops; service confirmed S-hail-004)
EXISTING = {
    "Hail station": (41.7554194, 27.6835926),
    "Al-Qassim station": (44.0915573, 26.4922762),
    "Majmaah station": (45.4197342, 25.9207722),
    "Al-Jawf station": (39.8376771, 29.6485411),
}
# metro set (A-screen-013) with tiers; coordinates = OSM place=city nodes
METRO = [
    ("Riyadh", 1, (46.716010, 24.638916)),
    ("Jeddah", 1, (39.174236, 21.550443)),
    ("Makkah", 1, (39.826869, 21.420847)),
    ("Madinah", 1, (39.611122, 24.471153)),
    ("Dammam", 1, (50.103999, 26.436782)),
    ("Al Khobar", 1, (50.196024, 26.304000)),
    ("Taif", 2, (40.415831, 21.270280)),
    ("Buraidah", 2, (43.971667, 26.331667)),
    ("Tabuk", 2, (36.567049, 28.401254)),
    ("Abha", 2, (42.504360, 18.216428)),
    ("Khamis Mushait", 2, (42.733333, 18.300000)),
    ("Jazan", 3, (42.557976, 16.894719)),
    ("Najran", 3, (44.224682, 17.543981)),
]

# name, pop (citypop Census 2022 places table; None = not published), governorate, is_centre, coords (OSM), role list, sample, terrain basis
ROWS = [
    (
        "Ḥā'il",
        "حائل",
        448623,
        "Ḥā'il",
        "حائل",
        True,
        (41.6986, 27.5209),
        ["administrative", "airport", "university"],
        False,
        "Ḥā'il city (governorate centre)",
    ),
    (
        "Al-Ghazālah",
        "الغزالة",
        5592,
        "Al-Ghazalah",
        "الغزالة",
        True,
        (41.315707, 26.787481),
        [],
        True,
        None,
    ),
    ("Al-Ḥā'īṭ", "الحائط", 8289, "Al-Ḥā'īṭ", "الحائط", True, (40.4720, 25.9860), [], True, None),
    (
        "Ash-Shamlī",
        "الشملي",
        9163,
        "Ash-Shamlī",
        "الشملي",
        True,
        (40.3239, 26.8629),
        [],
        True,
        None,
    ),
    (
        "Ash-Shanān",
        "الشنان",
        11560,
        "Ash-Shanān",
        "الشنان",
        True,
        (42.4439, 27.1750),
        [],
        False,
        None,
    ),
    (
        "As-Sulaymī",
        "السليمي",
        None,
        "As-Sulaymī",
        "السليمي",
        True,
        (41.3596, 26.2903),
        [],
        False,
        None,
    ),
    ("Baq'ā'", "بقعاء", 19659, "Baq'ā'", "بقعاء", True, (42.3899, 27.9103), [], False, None),
    ("Mawqaq", "موقق", 3148, "Mawqaq", "موقق", True, (41.1756, 27.3858), [], False, None),
    ("Simīrā'", "سميراء", 3105, "Simīrā'", "سميراء", True, (42.1249, 26.4942), [], False, None),
    ("Jubbah", "جبة", 5622, "Ḥā'il", "حائل", False, (40.9530, 28.0169), ["heritage"], True, None),
    ("Turubah", "تربة", 8590, "Baq'ā'", "بقعاء", False, (42.9204, 28.2596), [], True, None),
]
ROLE_SRC = {
    "administrative": "S-hail-006",
    "airport": "S-hail-006",
    "university": "S-hail-007",
    "heritage": "S-hail-005",
}
SAMPLE_REASON = {
    "Al-Ghazālah": "far (>100 km) from an existing station, no sourced role; governorate centre of Al-Ghazalah, 5,592 is smaller than the non-centre town Jubbah (5,622) in the same region (schema edge)",
    "Jubbah": "non-centre town with a sourced economic role (heritage: UNESCO rock-art serial site, Jabal Umm Sinman); 87 km from Hail station; larger than the Al-Ghazalah centre (schema edge)",
    "Turubah": "far (>100 km) from an existing station, no sourced role; non-centre town in Baq'a' governorate; OSM population tag (5,134) conflicts with citypopulation (8,590), census figure used",
    "Ash-Shamlī": "far (>100 km) from an existing station, no sourced role; governorate centre; OSM place node has Arabic name only (name:en absent)",
    "Al-Ḥā'īṭ": "far (>100 km) from an existing station, no sourced role; OSM spells the node 'Al Hayit' (الحايط): spelling-variant edge, matched by coordinates and name",
}
EXCL = {
    "As-Sulaymī": "centre population not in the Census 2022 places table (2,500+); not estimated. governorate total 17,343 is not a settlement figure. Needs Opus judgement",
    "Mawqaq": "below 5k and no sourced economic role (governorate centre kept so the governorate is covered)",
    "Simīrā'": "below 5k and no sourced economic role (governorate centre kept so the governorate is covered)",
}
TERRAIN_SRC = {"Ḥā'il": "S-hail-008"}

rows = []
for nen, nar, pop, gov, gov_ar, centre, (lon, lat), roles, sample, _ in ROWS:
    osm_id, tags = osm_at(lon, lat)
    d_exist = {k: hav((lon, lat), c) for k, c in EXISTING.items()}
    near = min(d_exist, key=d_exist.get)
    metro_d = {m: (hav((lon, lat), c), tier) for m, tier, c in METRO}
    mname = min(metro_d, key=lambda m: metro_d[m][0])
    tier = metro_d[mname][1]
    if pop is None:
        pop_src = pop_year = pop_type = None
    else:
        pop_src, pop_year, pop_type = "S-hail-001", 2022, "secondary"
    sourced_roles = [{"role": r, "source": ROLE_SRC[r]} for r in roles]
    excl = EXCL.get(nen)
    screened = excl is None
    if pop is not None and pop < 5000 and not roles and excl is None:
        raise SystemExit("unexpected")
    if nen == "Ḥā'il":
        terr, tbasis, aid = (
            "mixed",
            "sourced: S-hail-008 (Aja and Salma ranges W and SE, Nafud sand sea N and E)",
            "none",
        )
    else:
        terr, tbasis, aid = (
            "mixed",
            "assumed: regional description S-hail-008; row not classified",
            "A-screen-pilot-002",
        )
    srcs = sorted(
        {"S-hail-001", "S-hail-003", "S-hail-004"}
        | set(ROLE_SRC[r] for r in roles)
        | ({"S-hail-008"} if nen == "Ḥā'il" else set())
    )
    rows.append(
        dict(
            name_ar=nar,
            name_en=nen,
            region="hail",
            governorate=gov,
            governorate_ar=gov_ar,
            is_governorate_centre=centre,
            osm_id=osm_id,
            lat=lat,
            lon=lon,
            population=pop,
            pop_source=pop_src,
            pop_year=pop_year,
            pop_type=pop_type,
            tag_10k=bool(pop is not None and pop >= 10000),
            tag_5k=bool(pop is not None and pop >= 5000),
            dist_existing_km=round(d_exist[near], 1),
            road_min_existing=None,
            nearest_existing=f"{near} (North line, passenger; S-hail-004)",
            dist_committed_km=None,
            road_min_committed=None,
            nearest_committed=None,
            nearest_committed_station=None,
            dist_metro_km=round(metro_d[mname][0], 1),
            road_min_metro=None,
            nearest_metro=mname,
            economic_roles=sourced_roles,
            terrain_class=terr,
            screened=screened,
            exclusion_reason=excl,
            sources=srcs,
            fixture=False,
            threshold_50k=bool(pop is not None and pop >= 50000),
            pilot_sample=sample,
            sample_reason=SAMPLE_REASON.get(nen),
            nearest_metro_tier=tier,
            primary_to_find="GASTAT Census 2022 locality table (portal.saudicensus.sa: DNS failure 30 Oct 2026)"
            if pop
            else None,
            terrain_basis=tbasis,
            assumption_id=aid,
            road_min_method="pending R1a skims",
            dist_method="haversine, A-screen-pilot-001",
            notes=None,
        )
    )
df = pd.DataFrame(rows)
for c in ("population", "pop_year", "osm_id"):
    df[c] = df[c].astype("Int64")
df = df.astype(object).where(pd.notna(df), None)
df.attrs["governorates_gastat"] = 9
df.attrs["governorates_listed"] = int(df[df["is_governorate_centre"]]["governorate"].nunique())
OUT.parent.mkdir(parents=True, exist_ok=True)
import pyarrow as pa, pyarrow.parquet as pq

tbl = pa.Table.from_pandas(df, preserve_index=False).replace_schema_metadata(
    {
        b"governorates_gastat": b"9",
        b"governorates_listed": str(df.attrs["governorates_listed"]).encode(),
        b"governorates_gastat_status": b"secondary: GASTAT primary unreachable 30 Oct 2026; citypopulation.de list of 9 governorates for Hail (S-073, S-hail-001)",
    }
)
pq.write_table(tbl, OUT.with_suffix(".parquet"))
df.to_csv(OUT.with_suffix(".csv"), index=False)
print(
    df[
        [
            "name_en",
            "osm_id",
            "lat",
            "lon",
            "population",
            "screened",
            "tag_5k",
            "tag_10k",
            "dist_existing_km",
            "nearest_metro",
            "nearest_metro_tier",
            "pilot_sample",
        ]
    ].to_string()
)
