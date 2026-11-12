# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/aljouf_osm/build.py (last modified 2026-10-30 22:06 +03, pilot run PILOT_REGION_AL_JOUF).
# Role: built the region register.
# Outputs named in the code: pilot-al_jouf.csv, pilot-al_jouf.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Build cities/ksa/regions/pilot-al_jouf.{parquet,csv} from RegionRow fields (pilot, 30 Oct 2026)."""

import math, json, sys
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

R = 6371.0088


def hav(a, b):
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(d))


GEOM = json.load(open("/tmp/aljouf_osm/rail_geom.json"))
VERTS = [
    (p["lat"], p["lon"])
    for e in GEOM["elements"]
    if e.get("tags", {}).get("railway") == "rail"
    for p in e.get("geometry", [])
]
METRO_TABUK = (28.4012536, 36.5670490)  # OSM node 5418190413 via Nominatim, tier 2 (A-screen-013)
EXISTING = "SAR North line (OSM railway=rail; passenger route per S-018)"
BASE_SRC = ["S-al_jouf-001", "S-al_jouf-002", "S-al_jouf-006", "S-al_jouf-007", "S-018"]

# (name_ar, name_en, governorate_en, governorate_ar, is_centre, osm_id, lat, lon, pop, roles, extra_src)
ROWS = [
    (
        "سكاكا",
        "Sakaka",
        "Sakaka",
        "سكاكا",
        True,
        1236740006,
        29.9784,
        40.2048,
        204174,
        [("administrative", "S-al_jouf-001"), ("airport", "S-al_jouf-008")],
        ["S-al_jouf-008"],
    ),
    (
        "القريات",
        "Al-Qurayyat",
        "Al-Qurayyat",
        "القريات",
        True,
        1236744823,
        31.3333,
        37.3419,
        167080,
        [("administrative", "S-al_jouf-001")],
        [],
    ),
    (
        "طبرجل",
        "Tubarjal",
        "Tubarjal",
        "طبرجل",
        True,
        1236745024,
        30.5007,
        38.2165,
        78354,
        [("administrative", "S-al_jouf-001")],
        [],
    ),
    (
        "دومة الجندل",
        "Dumat al-Jandal",
        "Dumat al-Jandal",
        "دومة الجندل",
        True,
        1236739971,
        29.8059,
        39.8667,
        42362,
        [
            ("administrative", "S-al_jouf-001"),
            ("heritage", "S-al_jouf-009"),
            ("tourism", "S-al_jouf-009"),
        ],
        ["S-al_jouf-009"],
    ),
    ("صوير", "Ṣuwayr", "Sakaka", "سكاكا", False, 1236739864, 30.1173, 40.3888, 12430, [], []),
    (
        "أبو عجرم",
        "Abu 'Ajram",
        "Dumat al-Jandal",
        "دومة الجندل",
        False,
        5910483362,
        29.8899,
        39.3058,
        5610,
        [],
        [],
    ),
    (
        "النبك أبو قصر",
        "An-Nabak Abū Qaṣr",
        "Tubarjal",
        "طبرجل",
        False,
        1236739661,
        30.2942,
        38.7014,
        5374,
        [],
        [],
    ),
    ("الفياض", "Al-Fayāḍ", "Tubarjal", "طبرجل", False, 1236744782, 30.6053, 38.0999, 5532, [], []),
]
SAMPLE = {"Ṣuwayr", "Abu 'Ajram", "An-Nabak Abū Qaṣr", "Al-Fayāḍ", "Dumat al-Jandal"}

recs = []
for name_ar, name_en, gov, gov_ar, centre, osm, la, lo, pop, roles, extra in ROWS:
    d_rail = min(hav((la, lo), v) for v in VERTS)
    srcs = sorted(set(BASE_SRC + extra + ["S-al_jouf-001"]))
    recs.append(
        {
            "name_ar": name_ar,
            "name_en": name_en,
            "region": "al_jouf",
            "governorate": gov,
            "governorate_ar": gov_ar,
            "is_governorate_centre": centre,
            "osm_id": osm,
            "lat": la,
            "lon": lo,
            "population": pop,
            "pop_source": "S-al_jouf-001",
            "pop_year": 2022,
            "pop_type": "official",
            "tag_10k": pop >= 10000,
            "tag_5k": pop >= 5000,
            "dist_existing_km": round(d_rail, 2),
            "road_min_existing": None,
            "nearest_existing": EXISTING,
            "dist_committed_km": None,
            "road_min_committed": None,
            "nearest_committed": None,
            "nearest_committed_station": None,
            "dist_metro_km": round(hav((la, lo), METRO_TABUK), 1),
            "road_min_metro": None,
            "nearest_metro": "Tabuk (tier 2, A-screen-013)",
            "economic_roles": [{"role": r, "source": s} for r, s in roles],
            "terrain_class": None,
            "screened": True,
            "exclusion_reason": None,
            "sources": srcs,
            "fixture": False,
        }
    )
df = pd.DataFrame(recs)
out_dir = Path("./cities/ksa/regions")
out_dir.mkdir(parents=True, exist_ok=True)
meta = {
    b"governorates_gastat": b"4",
    b"governorates_listed": b"4",
    b"governorate_count_note": b"citypopulation.de (S-al_jouf-001/002) lists 4; Wikipedia and Saudipedia Emirate page list 3 (S-al_jouf-003/004); GASTAT primary not reached (S-al_jouf-005)",
    b"screening_label": b"synthetic demand, uncalibrated: scenario comparison, not a forecast",
    b"build": b"pilot 30 Oct 2026; haversine (A-screen-pilot-001)",
}
table = pa.Table.from_pandas(df, preserve_index=False)
table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
pq.write_table(table, out_dir / "pilot-al_jouf.parquet")
flat = df.copy()
flat["economic_roles"] = flat["economic_roles"].apply(
    lambda r: "; ".join(f"{x['role']}:{x['source']}" for x in r)
)
flat["sources"] = flat["sources"].apply(lambda s: "; ".join(s))
flat.to_csv(out_dir / "pilot-al_jouf.csv", index=False, encoding="utf-8")
print(df[["name_en", "population", "dist_existing_km", "dist_metro_km", "osm_id"]].to_string())
print("rows", len(df), "sample", sum(1 for r in recs if r["name_en"] in SAMPLE))
