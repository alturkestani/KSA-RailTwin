# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/alb/build.py (last modified 2026-10-30 22:03 +03, pilot run PILOT_REGION_AL_BAHA).
# Role: built the region register.
# Outputs named in the code: {REPO}/cities/ksa/regions/pilot-al_baha.csv, {REPO}/cities/ksa/regions/pilot-al_baha.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Build the Al-Baha pilot register (Parquet + CSV) from the sourced values in docs/regions/pilot-al_baha.md."""

import json
import math
import sys

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO = "./"
sys.path.insert(0, REPO)
from common.schemas import RegionRow  # noqa: E402

ACCESS = "2026-10-30"
S_ADMIN, S_PLACE, S_BALJ, S_WIKI_BALJ, S_WIKI_PROV = (
    "S-al_baha-001",
    "S-al_baha-002",
    "S-al_baha-003",
    "S-al_baha-004",
    "S-al_baha-005",
)
S_OSM_PLACE, S_OSM_RAIL, S_HHR, S_SARAWAT, S_AQIQ, S_AJEL, S_SAUDIPEDIA = (
    "S-al_baha-006",
    "S-al_baha-007",
    "S-al_baha-008",
    "S-al_baha-009",
    "S-al_baha-010",
    "S-al_baha-011",
    "S-al_baha-012",
)
S_GASTAT_REGIONS = "S-070"
S_GASTAT_GOV_UNVERIFIED = "S-072"
S_GASTAT_PORTAL = "S-090"


def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return round(2 * R * math.asin(math.sqrt(d)), 1)


MAKKAH_STN = (21.4176557, 39.7885323)  # OSM node 10956967098, Haramain station Makkah (in service)
TAIF = (21.2702801, 40.4158308)  # OSM node 1236468526, place=city (secondary metro)
ABHA = (18.2164282, 42.5043596)  # OSM node 295924875, place=city (Abha, secondary metro)
TERRAIN = "escarpment_mountain"
EXIST_NAME = "Haramain HSR, Makkah Central station (Rusaifah), OSM node 10956967098; in service since 11 Oct 2018"
ROAD_NOTE = "pending R1a skims"
STD_ROLE_ADMIN = {"role": "administrative", "source": S_ADMIN}

rows = []


def add(**kw):
    rows.append(kw)


def base(
    name_en,
    name_ar,
    gov_en,
    gov_ar,
    osm,
    lat,
    lon,
    pop,
    pop_src,
    tag10,
    tag5,
    roles,
    screened,
    excl,
    sources,
    notes,
    pilot=False,
    reason="",
    thr50=False,
    primary_to_find="",
):
    d_ex = hav((lat, lon), MAKKAH_STN) if not math.isnan(lat) else None
    d_taif = hav((lat, lon), TAIF) if not math.isnan(lat) else None
    d_abha = hav((lat, lon), ABHA) if not math.isnan(lat) else None
    if d_taif is None:
        metro, mkm, tier = None, None, None
    elif d_taif <= d_abha:
        metro, mkm, tier = "Taif (place=city, OSM 1236468526)", d_taif, 2
    else:
        metro, mkm, tier = "Abha (place=city, OSM 295924875)", d_abha, 2
    add(
        name_ar=name_ar,
        name_en=name_en,
        region="al_baha",
        governorate=gov_en,
        governorate_ar=gov_ar,
        is_governorate_centre=True,
        osm_id=osm,
        lat=lat,
        lon=lon,
        population=pop,
        pop_source=pop_src if pop is not None else None,
        pop_year=2022 if pop is not None else None,
        pop_type="secondary" if pop is not None else None,
        tag_10k=bool(pop is not None and pop >= 10000),
        tag_5k=bool(pop is not None and pop >= 5000),
        threshold_50k=bool(pop is not None and pop >= 50000),
        dist_existing_km=d_ex,
        road_min_existing=None,
        nearest_existing=EXIST_NAME if d_ex is not None else None,
        dist_committed_km=None,
        road_min_committed=None,
        nearest_committed=None,
        nearest_committed_station=None,
        dist_metro_km=mkm,
        road_min_metro=None,
        nearest_metro=metro,
        nearest_metro_tier=tier,
        economic_roles=roles,
        terrain_class=TERRAIN,
        road_min_method=ROAD_NOTE,
        screened=screened,
        exclusion_reason=excl,
        sources=sources,
        fixture=False,
        pilot_sample=pilot,
        sample_reason=reason,
        notes=notes,
        primary_to_find=primary_to_find,
    )


ADMIN = [STD_ROLE_ADMIN]
SRC_BASE = [S_ADMIN, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT]
SRC_PLACE = [S_PLACE] + SRC_BASE
NaN = float("nan")

base(
    "Al-Bāḥah",
    "الباحة",
    "Al-Bāḥah",
    "محافظة الباحة",
    295921642,
    20.0137941,
    41.4656378,
    90515,
    S_PLACE,
    True,
    True,
    ADMIN,
    True,
    None,
    SRC_PLACE + [S_AQIQ] * 0,
    "Region capital and governorate seat. Population 90,515 is the citypopulation place row (same figure as the governorate row). Only pilot town at or above 50k (threshold_50k). OSM node is place=city. Roles limited to administrative; region-level tourism and honey claims (S-al_baha-011) are in docs/regions/pilot-al_baha.md, not attached to this town.",
    thr50=True,
    primary_to_find="GASTAT locality table for Al-Baha city (census 2022)",
)

base(
    "Al-'Aqīq",
    "العقيق",
    "Al-'Aqīq",
    "محافظة العقيق",
    6767957154,
    20.2836432,
    41.6560108,
    19269,
    S_PLACE,
    True,
    True,
    ADMIN + [{"role": "airport", "source": S_AQIQ}],
    True,
    None,
    [S_ADMIN, S_PLACE, S_AQIQ, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate centre (town). King Saud Domestic Airport (IATA ABT) is described as located in Al-Aqiq, domestic flights only (Wikipedia, S-al_baha-010). The airport role is the only sourced role in the pilot sample; no distance from the town to the airport was sourced.",
    pilot=True,
    reason="With economic role (airport). Far from existing rail (231 km).",
    primary_to_find="GASTAT locality table; GACA airport facts",
)

base(
    "Al-Ḥajrah",
    "الحجرة",
    "Al-Ḥajrah",
    "محافظة الحجرة",
    1236690663,
    20.1997012,
    41.0720687,
    None,
    None,
    False,
    False,
    ADMIN,
    True,
    None,
    [S_ADMIN, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate seat is OSM place=village (node 1236690663), smaller than several non-centre towns elsewhere; the schema edge case the brief asks for. No place-level census figure sourced: the governorate row (12,136, S-al_baha-001) is the governorate total and is not used as the centre population. Population null, so no tag.",
    primary_to_find="GASTAT locality population for al-Ḥajrah centre",
)

base(
    "Al-Makhwāh",
    "المخواة",
    "Al-Makhwāh",
    "محافظة المخواة",
    1236690590,
    19.7794440,
    41.4355560,
    26248,
    S_PLACE,
    True,
    True,
    ADMIN,
    True,
    None,
    [S_ADMIN, S_PLACE, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate centre (town, OSM place=town). Governorate total 48,333 (S-al_baha-001) is below 50k; the town figure 26,248 is the place row. Sample: far from rail, no sourced role.",
    pilot=True,
    reason="Without sourced role. Far from rail (250 km). Mid band (26,248).",
    primary_to_find="GASTAT locality table",
)

base(
    "Al-Mandaq",
    "المندق",
    "Al-Mandaq",
    "محافظة المندق",
    1237964146,
    20.1105064,
    41.2828451,
    8674,
    S_PLACE,
    False,
    True,
    ADMIN,
    True,
    None,
    [S_ADMIN, S_PLACE, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate centre (town). Place row 8,674 (S-al_baha-002); governorate total 20,010. Tag_5k only. Sample: lower band, no sourced role, far from rail (213 km).",
    pilot=True,
    reason="Without sourced role. Lower band (8,674). Far from rail (213 km).",
    primary_to_find="GASTAT locality table",
)

base(
    "Al-Qarā",
    "القرى",
    "Al-Qarā",
    "محافظة القرى",
    None,
    NaN,
    NaN,
    None,
    None,
    False,
    False,
    ADMIN,
    False,
    "centre not located: no OSM place node found in the Nominatim search and no coordinate source for the governorate centre; the governorate total (19,586, S-al_baha-001) is not a centre population",
    [S_ADMIN, S_OSM_PLACE, S_OSM_RAIL],
    "Row kept so that every governorate has a row (rule 2). lat/lon left as NaN because no sourced coordinate exists; RegionRow requires coordinates, so this row fails validation until the centre is located. The Wikipedia 'Al-Qura' article describes a different governorate (29.9 N, 40.2 E) and was discarded.",
    primary_to_find="OSM node or GASTAT coordinates for the al-Qarā centre",
)

base(
    "Baljurashī",
    "بلجرشي",
    "Baljurashī",
    "محافظة بلجرشي",
    None,
    19.8612090,
    41.5609769,
    35985,
    S_BALJ,
    True,
    True,
    ADMIN,
    True,
    None,
    [S_ADMIN, S_BALJ, S_WIKI_BALJ, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate centre (town). Unmapped OSM place: no place=* node found by Nominatim (only the governorate boundary relation 12429798), so osm_id null. Coordinates from Wikipedia (secondary). Governorate total 51,787 is at or above 50k but the town (35,985) is below 50k: the threshold applies to settlements, so threshold_50k is false (Needs Opus judgement).",
    pilot=True,
    reason="Unmapped OSM place (no place node). Governorate total 51,787 vs town 35,985 tests the settlement-vs-governorate rule. Far from rail (253 km).",
    primary_to_find="GASTAT locality table; OSM place node",
)

base(
    "Banī Ḥasan",
    "بني حسن",
    "Banī Ḥasan",
    "محافظة بني حسن",
    3734863966,
    20.0534990,
    41.3736650,
    6344,
    S_PLACE,
    False,
    True,
    ADMIN,
    True,
    None,
    [S_ADMIN, S_PLACE, S_SAUDIPEDIA, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate centre conflict: OSM town node 'Bani Hasan' versus Saudipedia, which lists Bidan (Category A) and Wadi Al-Sadr (Category B) as centres (S-al_baha-012). Place row 6,344 (S-al_baha-002) vs governorate total 15,496 (S-al_baha-001 and S-al_baha-012 agree). Wikipedia's 35,082 for this governorate disagrees with both and is not used.",
    pilot=True,
    reason="Centre conflict (OSM town vs Saudipedia). Smallest sampled town (6,344). Without sourced role. Far from rail (224 km).",
    primary_to_find="GASTAT centre designation for Bani Hasan",
)

base(
    "Ghāmid az-Zinād",
    "غامد الزناد",
    "Far'at Ghāmid az-Zinād",
    "محافظة فرعة غامد الزناد",
    6770793665,
    19.5944390,
    41.5201123,
    None,
    None,
    False,
    False,
    ADMIN,
    True,
    None,
    [S_ADMIN, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate centre (town, OSM place=town). No place-level census figure sourced: the governorate total 12,506 (S-al_baha-001) is not the centre population. Population null, so no tag. Nearest metro is Abha, not Taif.",
    primary_to_find="GASTAT locality population for Ghāmid az-Zinād centre",
)

base(
    "Qilwah",
    "قلوة",
    "Qilwah",
    "محافظة قلوة",
    8506335688,
    19.9401107,
    41.2513010,
    13069,
    S_PLACE,
    True,
    True,
    ADMIN,
    True,
    None,
    [S_ADMIN, S_PLACE, S_OSM_PLACE, S_HHR, S_OSM_RAIL, S_SARAWAT],
    "Governorate centre (town, OSM node 8506335688). A second OSM node, 6768458212, is tagged place=governorate at 20.0000 N, 41.0833 E; kept as a conflict, the town node is used. Governorate total 31,197 (S-al_baha-001) vs town 13,069 (S-al_baha-002).",
    pilot=True,
    reason="Two OSM candidates for the centre (town vs governorate node). Without sourced role. Far from rail (224 km).",
    primary_to_find="GASTAT centre designation for Qilwah",
)

# Distances are recomputed here from the exact OSM coordinates above, so the register is reproducible.
df = pd.DataFrame(rows)
assert len(df) == 10, len(df)


def roles_out(v):
    return [dict(r) for r in v]


df["economic_roles"] = df["economic_roles"].map(roles_out)

# Schema-facing copy for validation (drop brief-only extras).
SCHEMA_FIELDS = set(RegionRow.model_fields)
EXTRAS = [
    "threshold_50k",
    "pilot_sample",
    "sample_reason",
    "nearest_metro_tier",
    "road_min_method",
    "notes",
    "primary_to_find",
]
val_errors = {}
for i, r in df.iterrows():
    rec = {
        k: (None if (isinstance(v, float) and math.isnan(v)) else v)
        for k, v in r.items()
        if k in SCHEMA_FIELDS
    }
    rec["pop_type"] = rec.get("pop_type")
    if rec.get("population") is not None and rec.get("pop_type") == "secondary":
        rec["pop_type"] = "official"  # validation-only substitute; see the report
    try:
        RegionRow.model_validate(rec)
    except Exception as e:
        val_errors[r["name_en"]] = str(e).splitlines()[1:4]

print("validation errors (after validation-only substitution of secondary->official):")
for k, v in val_errors.items():
    print(" ", k, "->", v)

meta = {
    b"region": b"al_baha",
    b"governorates_gastat": b"unknown (portal unreachable, S-090; S-072 unverified)",
    b"governorates_listed": b"10 rows (9 governorates + Al-Bahah row; S-al_baha-001 citypopulation; 9 per S-al_baha-005)",
}

out = df.copy()
out.insert(0, "row_id", [f"AB-{i + 1:02d}" for i in range(len(out))])
for c in ["osm_id", "population", "pop_year"]:
    out[c] = out[c].astype("Int64")
out["sources"] = out["sources"].map(lambda x: list(dict.fromkeys(x)))
table = pa.Table.from_pandas(out, preserve_index=False)
table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
pq.write_table(table, f"{REPO}/cities/ksa/regions/pilot-al_baha.parquet")

csv = out.copy()
csv["economic_roles"] = csv["economic_roles"].map(lambda x: json.dumps(x, ensure_ascii=False))
csv["sources"] = csv["sources"].map(lambda x: ";".join(x))
csv.to_csv(f"{REPO}/cities/ksa/regions/pilot-al_baha.csv", index=False, encoding="utf-8")
print("rows", len(out), "columns", len(out.columns))
print(
    out[
        [
            "name_en",
            "osm_id",
            "lat",
            "lon",
            "population",
            "dist_existing_km",
            "dist_metro_km",
            "nearest_metro_tier",
            "pilot_sample",
            "threshold_50k",
            "screened",
        ]
    ].to_string()
)
