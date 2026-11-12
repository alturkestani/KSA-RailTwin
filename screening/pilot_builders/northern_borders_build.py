# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/nbpilot/build_register.py (last modified 2026-10-30 21:43 +03, pilot run PILOT_REGION_NORTHERN_BORDERS).
# Role: built the region register.
# Outputs named in the code: cities/ksa/regions/pilot-northern_borders.csv, cities/ksa/regions/pilot-northern_borders.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Pilot build for northern_borders (scratch script, not committed; see docs/status for the R2 plan)."""

import csv, datetime as dt, hashlib, json, math
from pathlib import Path
from typing import Literal
import pandas as pd
from pydantic import ConfigDict
from common.schemas import RegionRow

REPO = Path("./")
R = 6371.0088


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(d))


rail = json.load(open("/tmp/nb_rail.json"))["elements"]
places_osm = json.load(open("/tmp/nb_places.json"))["elements"]
named, unnamed = [], []
kind = {}
for e in rail:
    t = e.get("tags", {})
    g = e.get("geometry", [])
    if not g:
        continue
    pts = [(p["lat"], p["lon"]) for p in g]
    if "قطار الشمال" in t.get("name", "") and t.get("service") in (None, "spur"):
        named.append((e["id"], pts))
        kind[e["id"]] = t.get("usage", "unspecified")
    elif (
        not t.get("name")
        and t.get("railway") == "rail"
        and t.get("usage") == "branch"
        and t.get("service") is None
    ):
        unnamed.append((e["id"], pts))


def nearest(pt, ways):
    best = (1e9, None)
    for wid, pts in ways:
        for p in pts:
            d = hav(pt, p)
            if d < best[0]:
                best = (d, wid)
    return best


METROS = {  # tier per A-screen-013; coordinates from OSM city nodes (Nominatim, S-northern_borders-004)
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
SRC = dict(
    CP="S-northern_borders-001",
    SP="S-northern_borders-002",
    WP="S-northern_borders-003",
    NOM="S-northern_borders-004",
    OVP="S-northern_borders-005",
    ARW="S-northern_borders-006",
    AJ="S-northern_borders-007",
    JAL="S-northern_borders-008",
    MEED_MR="S-northern_borders-009",
    NAF="S-northern_borders-010",
    GCC="S-northern_borders-011",
    ARAB="S-northern_borders-012",
)
SAR = ["S-017", "S-018", "S-022"]
# (key, name_en, name_ar, gov_en, gov_ar, centre?, osm_id, osm_type, lat, lon, pop, pop_key, roles, terrain, screened, reason, sample, sample_reason, notes)
P = [
    (
        "Arar",
        "Arar",
        "عرعر",
        "Arar",
        "عرعر",
        True,
        1236747164,
        "node",
        30.9815531,
        41.0164788,
        199247,
        ["CP", "SP", "WP"],
        [
            ("administrative", SRC["WP"]),
            ("border_crossing", SRC["ARW"]),
            ("border_crossing", SRC["AJ"]),
        ],
        "flat_desert",
        True,
        "",
        False,
        "",
        "Governorate centre and regional seat. Population is the Arar locality figure (199,247), not the governorate total (202,719). Border crossing with Iraq (An Nukhayb) per the sources cited. OSM place tag population 167,057 is a 2010 value and is not used.",
    ),
    (
        "Rafha",
        "Rafha",
        "رفحاء",
        "Rafha",
        "رفحاء",
        True,
        1013645991,
        "node",
        29.6324189,
        43.5178685,
        63929,
        ["CP", "SP", "WP"],
        [("administrative", SRC["WP"]), ("airport", SRC["NOM"])],
        "dunes",
        True,
        "",
        False,
        "",
        "Governorate centre. Locality 63,929; governorate total 84,536. Airport from the OSM aerodrome relation 11881620. Terrain 'dunes' is assumed from the Nafud erg description (S-northern_borders-010), not verified at town level. OSM population tag 52,712 is a 2010 value and is not used.",
    ),
    (
        "Turaif",
        "Turaif",
        "طريف",
        "Turaif",
        "طريف",
        True,
        1236745370,
        "node",
        31.6725877,
        38.6615532,
        61395,
        ["CP", "SP", "WP"],
        [("administrative", SRC["WP"])],
        "flat_desert",
        True,
        "",
        False,
        "",
        "Governorate centre. Locality 61,395 (≥50k); governorate total 66,004. OSM name 'Turayf'; GASTAT spelling 'Ṭuraīf'. Not the Iraq–Jordan crossing Turaibil (not Saudi; not used).",
    ),
    (
        "Al-Uwayqilah",
        "Al-Uwayqilah",
        "العويقيلة",
        "Al-Uwayqilah",
        "العويقيلة",
        True,
        1236745582,
        "node",
        30.3632535,
        42.2382351,
        17055,
        ["CP", "SP", "WP"],
        [("administrative", SRC["WP"])],
        "flat_desert",
        True,
        "",
        True,
        "5–50k band (in band, governorate centre); >100 km from the existing line; administrative role only (economic role: governorate seat)",
        "Governorate centre in the 5–50k band. Locality 17,055; governorate total 20,318. Saudipedia lists it as Category B (S-northern_borders-002). The smallest governorate in the region.",
    ),
    (
        "Rawdat Habas",
        "Rawdat Habas",
        "روضة هباس",
        "Rafha",
        "رفحاء",
        False,
        1237548502,
        "node",
        29.1503987,
        44.3114119,
        5620,
        ["CP"],
        [],
        "flat_desert",
        True,
        "",
        True,
        "5–50k band (in band, non-centre); >100 km from the existing line; no sourced economic role",
        "Non-centre town in the 5–50k band (Rafha governorate). Locality 5,620; tag_5k only. OSM place tag population 5,532 matches the 2010 census value and is not used.",
    ),
    (
        "Talah at-Tamiat",
        "Talah at-Tamiat",
        "طلعة التمياط",
        "Rafha",
        "رفحاء",
        False,
        1237552255,
        "node",
        29.8569440,
        43.1402780,
        3770,
        ["CP"],
        [],
        "flat_desert",
        False,
        "below 5,000 and no sourced economic role",
        True,
        "control below 5k: far (>100 km) from the existing line; OSM tags it 'village' while the GASTAT-listed locality is a larger place; OSM name 'At Timyat' is a probable name match (not confirmed)",
        "Below the 5k sensitivity threshold; kept as a pilot control. The OSM name ('At Timyat') is a probable match to the GASTAT locality (name match not verified).",
    ),
    (
        "Sha'bih Nasab",
        "Sha'bih Nasab",
        "شعبة نصاب",
        "Rafha",
        "رفحاء",
        False,
        1236406905,
        "node",
        28.8836507,
        44.7397731,
        3430,
        ["CP"],
        [],
        "flat_desert",
        False,
        "below 5,000 and no sourced economic role",
        True,
        "control below 5k: far (>100 km) from the existing line; OSM tags it 'town' on a 3,430 place (tag/size mismatch)",
        "Below the 5k sensitivity threshold. Tagged 'town' in OSM at 3,430 people: a tag/size mismatch kept as a schema test.",
    ),
    (
        "Hazm al-Jalamid",
        "Hazm al-Jalamid",
        "حزم الجلاميد",
        "Arar",
        "عرعر",
        False,
        1236741000,
        "node",
        31.280278,
        40.104167,
        None,
        [],
        [("mining", SRC["JAL"]), ("mining", SRC["MEED_MR"])],
        "flat_desert",
        False,
        "no sourced population (not in the ≥2,500 secondary list); held for the R2 GASTAT locality check",
        True,
        "near (<25 km) the existing line; sourced mining role (Ma'aden phosphate); population unsourced: tests the null-population path",
        "Ma'aden phosphate mine town near the Iraqi border; OSM 'village'. The population is unsourced and left null (no guess). Lies about 14 km from the SAR North branch (named way) and about 19 km from unnamed OSM branch segments.",
    ),
]
ROWS = []
for (
    key,
    en,
    ar,
    gov,
    gov_ar,
    centre,
    osm_id,
    osm_type,
    lat,
    lon,
    pop,
    pops,
    roles,
    terrain,
    screened,
    reason,
    sample,
    sample_reason,
    notes,
) in P:
    d_ex, wid = nearest((lat, lon), named)
    d_un, wid_u = nearest((lat, lon), unnamed)
    mets = sorted((hav((lat, lon), (la, lo)), m, tier) for m, (tier, la, lo) in METROS.items())
    src_ids = list(pops) if pops else []
    src_ids = [SRC[k] for k in src_ids]
    if pop is not None or key in ("Hazm al-Jalamid",):
        pass
    if pop is not None:
        src_ids = [SRC["CP"], SRC["SP"], SRC["WP"]] if "SP" in pops else [SRC["CP"]]
        src_ids += [SRC["NOM"]]
    else:
        src_ids = []
    src_ids = sorted(set(src_ids + [SRC["NOM"], SRC["OVP"]] + SAR[:2]))
    if key == "Hazm al-Jalamid":
        src_ids = sorted(set(src_ids + [SRC["JAL"], SRC["MEED_MR"]]))
    if key == "Arar":
        src_ids = sorted(set(src_ids + [SRC["ARW"], SRC["AJ"]]))
    if key in ("Rafha",):
        src_ids = sorted(set(src_ids + [SRC["NAF"]]))
    if key in ("Turaif", "Arar", "Rafha", "Al-Uwayqilah"):
        src_ids = sorted(set(src_ids + [SRC["WP"]]))
    ROWS.append(
        dict(
            name_ar=ar,
            name_en=en,
            region="northern_borders",
            governorate=gov,
            governorate_ar=gov_ar,
            is_governorate_centre=centre,
            osm_id=osm_id,
            lat=lat,
            lon=lon,
            population=pop,
            pop_source=SRC["CP"] if pop is not None else None,
            pop_year=2022 if pop is not None else None,
            pop_type="secondary" if pop is not None else None,
            tag_10k=bool(pop is not None and pop >= 10000),
            tag_5k=bool(pop is not None and pop >= 5000),
            threshold_50k=bool(pop is not None and pop >= 50000),
            dist_existing_km=round(d_ex, 1),
            road_min_existing=None,
            nearest_existing=f"SAR North {kind[wid]} line (OSM way {wid})",
            dist_committed_km=None,
            road_min_committed=None,
            nearest_committed=None,
            nearest_committed_station=None,
            dist_metro_km=round(mets[0][0], 1),
            road_min_metro=None,
            nearest_metro=mets[0][1],
            nearest_metro_tier=mets[0][2],
            road_min_method="pending R1a skims",
            economic_roles=[{"role": r, "source": s} for r, s in roles],
            terrain_class=terrain,
            screened=screened,
            exclusion_reason=reason or None,
            pilot_sample=sample,
            sample_reason=sample_reason or None,
            notes=notes,
            sources=src_ids,
            fixture=False,
            _d_unnamed=round(d_un, 1),
            _unnamed_way=wid_u,
            _metro2=f"{mets[1][1]} {round(mets[1][0], 1)} km",
        )
    )


class PilotRow(RegionRow):
    model_config = ConfigDict(extra="allow")
    pop_type: Literal["official", "derived", "grid", "secondary"] | None = None


def clean(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


for r in ROWS:
    # validation via the subclass (extra fields allowed; pop_type gains 'secondary'); base schema untouched
    vals = {
        k: v
        for k, v in clean(r).items()
        if k
        not in (
            "pilot_sample",
            "sample_reason",
            "threshold_50k",
            "nearest_metro_tier",
            "road_min_method",
            "notes",
        )
    }
    PilotRow.model_validate(vals)

cols = list(clean(ROWS[0]).keys())
df = pd.DataFrame([clean(r) for r in ROWS], columns=cols)
df["population"] = df["population"].astype("Int64")
df["pop_year"] = df["pop_year"].astype("Int64")
df["osm_id"] = df["osm_id"].astype("Int64")
out_parq = REPO / "cities/ksa/regions/pilot-northern_borders.parquet"
out_csv = REPO / "cities/ksa/regions/pilot-northern_borders.csv"
out_parq.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(out_parq, index=False)
df_csv = df.copy()
for c in ("economic_roles", "sources"):
    df_csv[c] = df_csv[c].apply(
        lambda v: (
            "|".join(f"{x['role']}:{x['source']}" for x in v)
            if c == "economic_roles"
            else "|".join(v)
        )
    )
df_csv.to_csv(out_csv, index=False)
back = pd.read_parquet(out_parq)
assert len(back) == len(pd.read_csv(out_csv)) == len(ROWS)
print("rows", len(ROWS), "parquet+csv ok")
for r in ROWS:
    print(
        r["name_en"],
        r["population"],
        r["dist_existing_km"],
        r["nearest_existing"],
        r["dist_metro_km"],
        r["nearest_metro"],
        r["nearest_metro_tier"],
        r["_d_unnamed"],
        r["_unnamed_way"],
        r["_metro2"],
        r["sources"],
    )
json.dump(ROWS, open("/tmp/nbpilot/rows.json", "w"), ensure_ascii=False, indent=1, default=str)
