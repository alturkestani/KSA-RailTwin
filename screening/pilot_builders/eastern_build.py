# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/pilot-eastern-src/build.py (last modified 2026-10-30 21:13 +03, pilot run PILOT_REGION_EASTERN).
# Role: built the region register.
# Outputs named in the code: pilot-eastern.csv, pilot-eastern.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Builds the PILOT_REGION_EASTERN register (pilot-only builder; not committed)."""

import json, math, sys
from pathlib import Path
import pyarrow as pa, pyarrow.parquet as pq
from common.schemas import RegionRow

ROOT = Path(".").resolve()
REG = ROOT / "cities/ksa/regions"
REG.mkdir(parents=True, exist_ok=True)
CITY = "S-eastern-001"  # citypopulation.de Eastern Region (Census 2022-05-10 values)
OSM = "S-eastern-004"  # OpenStreetMap node/way via Nominatim (ODbL)


def roles(*pairs):
    return [{"role": r, "source": s} for r, s in pairs]


# Existing line stations (East line, SAR published list S-025; coords from OSM railway nodes)
EXISTING = {
    "Riyadh station": (24.6505, 46.7407, "node 492520789"),
    "Hofuf station": (25.3866, 49.5686, "way 95533900"),
    "Abqaiq station": (25.9319, 49.6647, "node 2011671784"),
    "Dammam station": (26.4097, 50.1263, "node 492547630"),
}
# Metro reference points: Dammam-Khobar-Dhahran (primary tier) and Riyadh (primary tier), A-screen-pilot-003
METRO = {
    "Dammam–Khobar–Dhahran (Dammam node)": (26.4368, 50.1040),
    "Dammam–Khobar–Dhahran (Khobar node)": (26.3040, 50.1960),
    "Dammam–Khobar–Dhahran (Dhahran node)": (26.2967, 50.1202),
    "Riyadh (city node)": (24.6389, 46.7160),
}


def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(h))


def near(pt, pts):
    name, d = min(((n, hav(pt, c)) for n, c in pts.items()), key=lambda x: x[1])
    return round(d, 2), name


# (name_en, name_ar, gov_en, gov_ar, centre, osm_id, lat, lon, pop, pop_src_extra, roles, screened, excl, pilot, extra_sources, note)
R = []


def add(
    name_en,
    name_ar,
    gov,
    gov_ar,
    centre,
    osm,
    lat,
    lon,
    pop,
    roles_=(),
    screened=True,
    excl=None,
    pilot=False,
    srcs=(),
    note="",
):
    R.append(
        dict(
            name_en=name_en,
            name_ar=name_ar,
            gov=gov,
            gov_ar=gov_ar,
            centre=centre,
            osm=osm,
            lat=lat,
            lon=lon,
            pop=pop,
            roles=roles(*roles_),
            screened=screened,
            excl=excl,
            pilot=pilot,
            srcs=list(srcs) + [s for _, s in roles_],
            note=note,
        )
    )


# >= 50,000 (Census 2022 place rows, S-eastern-001; corroborated by S-eastern-002 where listed)
add(
    "Dammam",
    "الدمام",
    "Ad-Dammām",
    "الدمام",
    True,
    287865393,
    26.4368,
    50.1040,
    1386166,
    [("port", "S-eastern-007"), ("airport", "S-eastern-012")],
    srcs=[CITY, "S-eastern-002"],
    note="Governorate seat. Governorate row (Ad-Dammām, 1,532,326) is larger than the place row: not summed.",
)
add(
    "Hofuf (Al-Hufuf–Al-Mubarraz)",
    "الهفوف والمبرز",
    "Al-Ahsa",
    "الأحساء",
    True,
    208501048,
    25.3697,
    49.5865,
    729606,
    [("heritage", "S-eastern-006"), ("agriculture", "S-eastern-006")],
    srcs=[CITY, "S-eastern-002", "S-eastern-006"],
    note="Census place row merges Al-Hufuf and Al-Mubarraz (citypopulation.de). Governorate centre: Hofuf. Merge kept as published (A-screen-pilot-005).",
)
add(
    "Jubail",
    "الجبيل",
    "Al-Jubaīl",
    "الجبيل",
    True,
    38903292,
    27.0007,
    49.6532,
    474679,
    [("industrial_city", "S-eastern-008")],
    srcs=[CITY, "S-eastern-002", "S-eastern-008"],
    note="Census place row includes Jubail Industrial City (citypopulation.de note).",
)
add(
    "Khobar",
    "الخبر",
    "Al-Khubar",
    "الخبر",
    True,
    32441763,
    26.3040,
    50.1960,
    409549,
    srcs=[CITY, "S-eastern-002"],
)
add(
    "Hafar al-Batin",
    "حفر الباطن",
    "Ḥafar al-Bāṭin",
    "حفر الباطن",
    True,
    983083568,
    28.4328,
    45.9628,
    387096,
    srcs=[CITY],
)
add(
    "Ath-Thuqbah",
    "الثقبة",
    "Al-Khubar",
    "الخبر",
    False,
    19120268,
    26.2730,
    50.1928,
    248888,
    srcs=[CITY],
    note="OSM object is a boundary relation tagged neighbourhood (not a town node). Inside the Dammam–Khobar–Dhahran metro area.",
)
add(
    "Dhahran",
    "الظهران",
    "Ad-Dammām",
    "الدمام",
    False,
    447805356,
    26.2967,
    50.1202,
    143936,
    [("university", "S-eastern-009"), ("military", "S-eastern-009")],
    srcs=[CITY, "S-eastern-002", "S-eastern-009"],
    note="Inside the Dammam–Khobar–Dhahran metro area. The KFUPM campus adjoins Dhahran Air Base (S-eastern-009).",
)
add(
    "Tarout",
    "تاروت",
    "Al-Qaṭīf",
    "القطيف",
    False,
    1237806675,
    26.5764,
    50.0555,
    117646,
    srcs=[CITY],
)
add(
    "Qatif",
    "القطيف",
    "Al-Qaṭīf",
    "القطيف",
    True,
    1237806905,
    26.5586,
    50.0087,
    87332,
    srcs=[CITY, "S-eastern-002"],
)
add(
    "Saihat",
    "سيهات",
    "Al-Qaṭīf",
    "القطيف",
    False,
    1013645811,
    26.4750,
    50.0416,
    84818,
    srcs=[CITY, "S-eastern-002"],
    note="OSM name 'Sayhat'.",
)
add(
    "Khafji",
    "الخفجي",
    "Al-Khafjī",
    "الخفجي",
    True,
    983083571,
    28.4225,
    48.4928,
    78691,
    [("border_crossing", "S-eastern-005")],
    srcs=[CITY, "S-eastern-002", "S-eastern-005"],
    note="Governorate centre. Announced GCC railway route passes Al-Khafji (S-032), alignment not located.",
)
add(
    "Rahimah",
    "رحيمة",
    "R'ās Tanūrah",
    "رأس تنورة",
    False,
    975188254,
    26.7117,
    50.0646,
    57030,
    srcs=[CITY],
    screened=True,
    note="OSM object is an amenity inside Ras Tanura town (Al Fayha district): probable overlap with the Ras Tanura row. Not summed; Needs Opus judgement.",
)
# Governorate centres below 50,000 (screened because they are centres)
add(
    "Abqaiq (Buqayq)",
    "بقيق",
    "Abqaīq",
    "بقيق",
    True,
    348286415,
    25.9356,
    49.6683,
    45032,
    srcs=[CITY, "S-eastern-010"],
    pilot=True,
    note="Pilot sample. Governorate centre with a population smaller than a non-centre town (Raḥīmah, 57,030) in the same region. Oil processing (Aramco) has no enum role; see Needs Opus judgement.",
)
add(
    "An-Nu'ayriyah",
    "النعيرية",
    "An-Na'īryah",
    "النعيرية",
    True,
    1236770860,
    27.4742,
    48.4789,
    40023,
    srcs=[CITY],
)
add(
    "Qaryat al-'Ulyā",
    "قرية العليا",
    "Qaryat al-'Ulyā",
    "قرية العليا",
    True,
    1041975797,
    27.5514,
    47.6957,
    10961,
    srcs=[CITY],
    note="OSM way tagged village. Governorate-level row (21,788) is not used as the town figure.",
)
add(
    "Ras Tanura",
    "رأس تنورة",
    "R'ās Tanūrah",
    "رأس تنورة",
    True,
    1237805652,
    26.7074,
    50.0674,
    None,
    [("port", "S-eastern-011")],
    srcs=["S-eastern-011", OSM],
    note="Town population not published in the sources consulted: the governorate row (62,314) is not used. Refinery (Aramco) has no enum role. Needs Opus judgement.",
)
add(
    "Al-Udayd",
    "العديد",
    "Al-'Udayd",
    "العديد",
    True,
    11871306304,
    24.6132,
    51.4110,
    None,
    srcs=[OSM, CITY],
    note="No town-level population (governorate row 8,635 not used). OSM locality is at 24.61 N, 51.41 E, near the Qatar border: location unverified. Needs Opus judgement.",
)
add(
    "Al-Bayda",
    "البيضاء",
    "Al-Bayḍā",
    "البيضاء",
    False,
    1236739581,
    25.9756,
    49.6425,
    None,
    srcs=[OSM],
    screened=False,
    excl="Governorate status conflicting (Eastern Province list: 13 with Al-Bayda in Saudipedia Arabic and Wikipedia Arabic; 12 in citypopulation.de, S-eastern-001). Centre not located: OSM candidate is by name only (several 'Al Bayda' nodes). Population unverified.",
    note="Candidate centre by name only. Needs Opus judgement.",
)
# Pilot sample: 5,000-50,000, non-centre, stratified (near/far x role/no role; edge cases)
add(
    "Al-Oyun",
    "العيون",
    "Al-'Aḥsā'",
    "الأحساء",
    False,
    10775657799,
    25.6076,
    49.5649,
    35226,
    srcs=[CITY, OSM],
    pilot=True,
    note="Pilot sample: NEAR (24.6 km to Hofuf station) with no sourced economic role.",
)
add(
    "Al-Jubail (Al-Ahsa governorate)",
    "الجبيل",
    "Al-'Aḥsā'",
    "الأحساء",
    False,
    695579475,
    25.4080,
    49.6616,
    9994,
    srcs=[CITY, OSM],
    pilot=True,
    note="Pilot sample: same name as the Jubail governorate centre (split across governorates). OSM tags it place=neighbourhood (unmapped town type). NEAR Hofuf, no sourced role.",
)
add(
    "Al-Qaisumah",
    "القيصومة",
    "Ḥafar al-Bāṭin",
    "حفر الباطن",
    False,
    957479209,
    28.3097,
    46.1275,
    27307,
    srcs=[CITY, OSM],
    pilot=True,
    note="Pilot sample: FAR from the existing line (over 100 km) with no sourced role.",
)
add(
    "King Khalid Military City",
    "مدينة الملك خالد العسكرية",
    "Ḥafar al-Bāṭin",
    "حفر الباطن",
    False,
    348108482,
    27.9822,
    45.5450,
    25356,
    [("military", "S-eastern-001")],
    srcs=[CITY, OSM],
    pilot=True,
    note="Pilot sample: FAR with a sourced role. Census row is a 'Military Institution', not a civil town: schema edge.",
)

# Derived distances
rows = []
for r in R:
    pt = (r["lat"], r["lon"])
    d_ex, n_ex = near(pt, {k: (v[0], v[1]) for k, v in EXISTING.items()})
    d_me, n_me = near(pt, METRO)
    tier = 1  # all metro reference points are primary-tier (A-screen-013)
    rr = dict(
        name_ar=r["name_ar"],
        name_en=r["name_en"],
        region="eastern",
        governorate=r["gov"],
        governorate_ar=r["gov_ar"],
        is_governorate_centre=r["centre"],
        osm_id=r["osm"],
        lat=r["lat"],
        lon=r["lon"],
        population=r["pop"],
        pop_source=(CITY if r["pop"] is not None else None),
        pop_year=(2022 if r["pop"] is not None else None),
        pop_type=("official" if r["pop"] is not None else None),
        tag_10k=(r["pop"] or 0) >= 10000,
        tag_5k=(r["pop"] or 0) >= 5000,
        dist_existing_km=d_ex,
        road_min_existing=None,
        nearest_existing=f"East line: {n_ex}",
        dist_committed_km=None,
        road_min_committed=None,
        nearest_committed="GCC railway (announced route; alignment not located)",
        nearest_committed_station=(
            "Al-Khafji (route point, S-032; no station coordinates)"
            if r["gov"] == "Al-Khafji" and r["centre"]
            else None
        ),
        dist_metro_km=d_me,
        road_min_metro=None,
        nearest_metro=n_me,
        economic_roles=r["roles"],
        terrain_class=None,
        screened=r["screened"],
        exclusion_reason=r["excl"],
        sources=sorted(set(r["srcs"])),
        fixture=False,
    )
    rows.append((rr, r))

# Validation against the canonical schema (Pydantic, extra=forbid)
for rr, _ in rows:
    RegionRow.model_validate(rr)

ids = [f"E{i:02d}" for i in range(1, len(rows) + 1)]
out_rows = [rr for rr, _ in rows]
meta = {
    "governorates_gastat": "null (not verified: S-072, S-090)",
    "governorates_listed": "13 (incl. Al-Bayda; 12 per S-073)",
}
tbl = pa.Table.from_pylist(out_rows)
tbl = tbl.replace_schema_metadata({k.encode(): v.encode() for k, v in meta.items()})
pq.write_table(tbl, REG / "pilot-eastern.parquet")
back = pq.read_table(REG / "pilot-eastern.parquet").to_pylist()
assert len(back) == len(out_rows)
for b in back:
    RegionRow.model_validate(b)

import csv

with open(REG / "pilot-eastern.csv", "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    cols = list(out_rows[0].keys())
    w.writerow(cols)
    for rr in out_rows:
        row = []
        for c in cols:
            v = rr[c]
            if c == "economic_roles":
                v = " | ".join(f"{x['role']}:{x['source']}" for x in v)
            elif c == "sources":
                v = ";".join(v)
            elif isinstance(v, bool):
                v = "true" if v else "false"
            row.append("" if v is None else v)
        w.writerow(row)

# Sidecar for the Markdown only (pilot-only fields are not in the schema)
json.dump(
    [
        {
            "id": ids[i],
            "pilot_sample": r["pilot"],
            "note": r["note"],
            "name_en": rr["name_en"],
            "gov": rr["governorate"],
            "dist_ex": rr["nearest_existing"],
            "metro": rr["nearest_metro"],
        }
        for i, (rr, r) in enumerate(rows)
    ],
    open("/tmp/pilot-eastern-src/sidecar.json", "w"),
    ensure_ascii=False,
    indent=1,
)
print(
    "rows",
    len(out_rows),
    "pilot_sample",
    sum(r["pilot"] for _, r in rows),
    ">=50k",
    sum(1 for rr, _ in rows if (rr["population"] or 0) >= 50000),
)
for rr, r in rows:
    print(
        f"{rr['name_en'][:30]:30} pop={rr['population']} ex={rr['dist_existing_km']} {rr['nearest_existing']} metro={rr['dist_metro_km']} {rr['nearest_metro']} centre={rr['is_governorate_centre']} screened={rr['screened']} pilot={r['pilot']}"
    )
