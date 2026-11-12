# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/asir-scripts/build_pilot.py (last modified 2026-10-30 21:27 +03, pilot run PILOT_REGION_ASIR).
# Role: built the region register.
# Outputs named in the code: {REPO}/cities/ksa/regions/pilot-asir.csv, {REPO}/cities/ksa/regions/pilot-asir.parquet, {REPO}/docs/regions/pilot-asir.md.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Builder for the Asir pilot register (run with the repo's .venv). Not part of the repo."""

import json
import math
import sys

REPO = "./"
sys.path.insert(0, REPO)

import pandas as pd  # noqa: E402

from common.schemas import RegionRow, load_region_register  # noqa: E402

OUT_PQ = f"{REPO}/cities/ksa/regions/pilot-asir.parquet"
OUT_CSV = f"{REPO}/cities/ksa/regions/pilot-asir.csv"
OUT_MD = f"{REPO}/docs/regions/pilot-asir.md"
SRC_CITYPOP = "S-asir-001"
SRC_OSM_PLACE = "S-asir-003"
SRC_OSM_STATION = "S-asir-004"
SRC_HHR = "S-asir-005"
SRC_LB = "S-asir-006"
SRC_TERRAIN = "S-asir-007"
SRC_ROLE_AIR = "S-asir-008"
SRC_ROLE_MINE = "S-asir-009"
SRC_ROLE_HERITAGE = "S-asir-010"
SRC_GASTAT_FAIL = ["S-072", "S-090"]

# Existing rail (Haramain stations; OSM station nodes = S-asir-004, list = S-asir-005).
EXISTING = {
    "Haramain - King Abdulaziz Intl Airport (Jeddah)": (21.6605, 39.1738, 7227897402),
    "Haramain - King Abdullah Economic City": (22.4218, 39.1917, 2147398509),
    "Haramain - Makkah": (21.4177, 39.7885, 10956967098),
    "Haramain - Madinah": (24.4723, 39.6996, 10957110707),
    "HHR - Riyadh Railway Station": (24.6505, 46.7407, 492520789),
}
# Committed / under procurement (Landbridge intermediate stations; names conflict across sources).
COMMITTED = {
    "Landbridge (committed) - Al Jumum": (21.621168, 39.6989787, 1236466181),
    "Landbridge (committed) - Al Muwayh": (22.4365659, 41.761935, 1236449504),
    "Landbridge (committed) - Ad Dawadimi": (24.494167, 44.383333, 1236695687),
}
# Metro tiers (A-screen-013). Coordinates from OSM place nodes (S-asir-003).
METROS = [
    ("Riyadh", 1, 24.638916, 46.7160104, 315358390),
    ("Jeddah", 1, 21.5504432, 39.1742363, 1933393717),
    ("Makkah", 1, 21.420847, 39.826869, 0),
    ("Madinah", 1, 24.471153, 39.6111216, 4571693347),
    ("Dammam", 1, 26.4367824, 50.1039991, 287865393),
    ("Khobar", 1, 26.3039999, 50.1960237, 32441763),
    ("Taif", 2, 21.2702801, 40.4158308, 1236468526),
    ("Buraidah", 2, 26.331667, 43.971667, 1236365110),
    ("Tabuk", 2, 28.4012536, 36.567049, 5418190413),
    ("Abha-Khamis Mushait", 2, 18.2164282, 42.5043596, 295924875),
    ("Abha-Khamis Mushait", 2, 18.3, 42.733333, 983083570),
    ("Jazan", 3, 16.894719, 42.5579758, 288992209),
    ("Najran", 3, 17.5439809, 44.2246817, 982548735),
]

# Governorate centres. Fields: governorate EN, governorate AR, centre AR, centre EN, OSM id,
# lat, lon, centre population (GASTAT-derived place table, S-asir-001) or None,
# governorate population (S-asir-001), flags.
CENTRES = [
    ("Abha", "أبها", "أبها", "Abha", 295924875, 18.2164282, 42.5043596, 334290, 422243, {}),
    (
        "Ahad Rafidah",
        "أحد رفيدة",
        "أحد رفيدة",
        "Ahad Rafidah",
        7700248106,
        18.18141,
        42.84136,
        79202,
        107894,
        {},
    ),
    (
        "Al-Amwah",
        "الأمواه",
        "الأمواه",
        "Al-Amwah",
        6769849264,
        18.71395,
        43.66095,
        None,
        10969,
        {"note": "centre population not in S-asir-001 place table; OSM town name 'Al Amoah'"},
    ),
    ("Al-Birk", "البرك", "البرك", "Al-Birk", 1237961107, 18.21722, 41.53639, 3987, 22583, {}),
    (
        "Al-Harjah",
        "الحرجة",
        "الحرجة",
        "Al-Harjah",
        1236690496,
        19.57566,
        41.98454,
        4540,
        18503,
        {
            "opus": "three OSM 'الحرجة' candidates (19.58N 41.98E; 17.92N 43.37E; 21.86N 40.18E); centre not confirmed"
        },
    ),
    (
        "Al-Majaridah",
        "المجاردة",
        "المجاردة",
        "Al-Majaridah",
        1236688112,
        19.13022,
        41.92364,
        21837,
        48302,
        {"sample": "schema edge: centre 21,837 in a governorate of 48,302 (just under 50k)"},
    ),
    ("An-Nimas", "النماص", "النماص", "An-Nimas", 1236687970, 19.11667, 42.13333, 22541, 38409, {}),
    (
        "Balqarn",
        "بالقرن",
        "بالقرن",
        "Balqarn",
        11891866421,
        19.3221772,
        41.8597965,
        None,
        60012,
        {
            "opus": "no OSM node named Balqarn; provisional coordinates on village 'جوف بلقرن'; centre unresolved",
            "unresolved": True,
        },
    ),
    (
        "Bariq",
        "بارق",
        "بارق",
        "Bariq",
        6733316507,
        18.93803,
        41.9464,
        None,
        44880,
        {"note": "centre population not in S-asir-001 place table"},
    ),
    ("Bisha", "بيشة", "بيشة", "Bisha", 983083565, 20.0, 42.6, 115537, 202096, {}),
    (
        "Khamis Mushait",
        "خميس مشيط",
        "خميس مشيط",
        "Khamis Mushait",
        983083570,
        18.3,
        42.73333,
        535065,
        601305,
        {},
    ),
    (
        "Muhayil",
        "محايل",
        "محايل عسير",
        "Muhayil",
        1236688965,
        18.54639,
        42.04889,
        97967,
        230537,
        {},
    ),
    (
        "Rijal Alma",
        "رجال ألمع",
        "رجال ألمع",
        "Rijal Almaa",
        11892567408,
        18.21249,
        42.27334,
        None,
        50825,
        {
            "opus": "governorate total 50,825 is >= 50k but centre population not in S-asir-001 place table"
        },
    ),
    (
        "Sarat Abidah",
        "سراة عبيدة",
        "سراة عبيدة",
        "Sarat Abidah",
        295926005,
        18.0874,
        43.13264,
        19855,
        57123,
        {"sample": "schema edge: governorate total 57,123 (>= 50k) but centre 19,855 (< 50k)"},
    ),
    (
        "Tanumah",
        "تنومة",
        "تنومة",
        "Tanumah",
        5889480125,
        18.95353,
        42.17026,
        12442,
        17756,
        {"sample": "5k-50k band; far from rail; no sourced economic role found"},
    ),
    (
        "Tarib",
        "طريب",
        "فرعة طريب",
        "Fir'ah Tarib",
        7700248105,
        18.5649816,
        43.2038211,
        8722,
        22298,
        {
            "sample": "5k-10k band edge; centre name matched from OSM 'فرعة طريب' to S-asir-001 'فرعه طريب' (name match, not confirmed as the governorate seat)"
        },
    ),
    (
        "Tathlith",
        "تثليث",
        "تثليث",
        "Tathlith",
        1236412511,
        19.53333,
        43.5,
        15854,
        36451,
        {"sample": "5k-50k band; far from rail; no sourced economic role found"},
    ),
    (
        "Zahran al-Janub",
        "ظهران الجنوب",
        "ظهران الجنوب",
        "Zahran al-Janub",
        1237961702,
        17.6617883,
        43.5194305,
        24134,
        32099,
        {},
    ),
]

ROLES = {
    "Abha": [("airport", SRC_ROLE_AIR), ("administrative", SRC_ROLE_AIR)],
    "Khamis Mushait": [("military", SRC_ROLE_AIR)],
    "Bisha": [("mining", SRC_ROLE_MINE)],
    "Rijal Alma": [
        ("heritage", SRC_ROLE_HERITAGE),
        ("tourism", SRC_ROLE_HERITAGE),
        ("agriculture", SRC_ROLE_HERITAGE),
    ],
}
SAMPLE_ONLY = {"Tanumah", "Tathlith", "Sarat Abidah", "Al-Majaridah", "Tarib"}


def hav(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest(lat, lon, table):
    name, d = min(((n, hav(lat, lon, v[0], v[1])) for n, v in table.items()), key=lambda x: x[1])
    return name, d


def build_rows():
    rows = []
    for gov, gov_ar, c_ar, c_en, osm, lat, lon, pop, gov_pop, flags in CENTRES:
        ex_name, ex_d = nearest(lat, lon, EXISTING)
        cm_name, cm_d = nearest(lat, lon, COMMITTED)
        me = min(((hav(lat, lon, m[2], m[3]), m) for m in METROS), key=lambda x: x[0])
        d_me, m = me
        tag_10k = pop is not None and pop >= 10_000
        tag_5k = pop is not None and pop >= 5_000
        tag_50k = pop is not None and pop >= 50_000
        # Terrain: Abha is described as on the Sarawat escarpment (S-asir-007); the rest are assumed (A-screen-pilot-002).
        terrain = "escarpment_mountain" if c_en == "Abha" else "mixed"
        roles = [{"role": r, "source": s} for r, s in ROLES.get(gov, [])]
        sources = [SRC_CITYPOP, SRC_OSM_PLACE, SRC_OSM_STATION, SRC_HHR, SRC_LB, *SRC_GASTAT_FAIL]
        if terrain == "escarpment_mountain":
            sources.append(SRC_TERRAIN)
        else:
            sources.append("A-screen-pilot-002")
        sources += [s for _, s in ROLES.get(gov, [])]
        unresolved = flags.get("unresolved", False)
        pilot = gov in SAMPLE_ONLY
        rows.append(
            dict(
                name_ar=c_ar,
                name_en=c_en,
                region="asir",
                governorate=gov,
                governorate_ar=gov_ar,
                is_governorate_centre=True,
                osm_id=osm,
                lat=lat,
                lon=lon,
                population=pop,
                pop_source=SRC_CITYPOP if pop is not None else None,
                pop_year=2022 if pop is not None else None,
                pop_type="secondary" if pop is not None else None,
                tag_10k=tag_10k,
                tag_5k=tag_5k,
                threshold_50k=tag_50k,
                dist_existing_km=round(ex_d, 1),
                road_min_existing=None,
                nearest_existing=ex_name,
                dist_committed_km=round(cm_d, 1),
                road_min_committed=None,
                nearest_committed=cm_name.split(" - ")[0],
                nearest_committed_station=cm_name,
                dist_metro_km=round(d_me, 1),
                road_min_metro=None,
                nearest_metro=f"{m[0]} (tier {m[1]})",
                economic_roles=roles,
                terrain_class=terrain,
                screened=not unresolved,
                exclusion_reason=(
                    "governorate centre unresolved (OSM has no Balqarn centre node); coordinates provisional, needs Opus judgement"
                    if unresolved
                    else None
                ),
                sources=sources,
                fixture=False,
                pilot_sample=pilot,
                pilot_reason=(flags.get("sample") if pilot else None),
                distance_method=(
                    "haversine (great-circle) from OSM coordinates; road_min pending R1a skims; "
                    "A-screen-pilot-001"
                ),
                primary_to_find=(
                    "GASTAT Census 2022 locality/governorate table (portal.saudicensus.sa: DNS failure 2026-10-30, S-090)"
                    if pop is not None or True
                    else None
                ),
            )
        )
        rows[-1]["_flags"] = flags
        rows[-1]["_gov_pop"] = gov_pop
    return rows


def main():
    rows = build_rows()
    for r in rows:
        r.pop("_flags")
        r.pop("_gov_pop")
    # Validate every row against the schema.
    validated = [RegionRow.model_validate(r) for r in rows]
    df = pd.DataFrame(rows)
    df.to_parquet(OUT_PQ, index=False)
    flat = df.copy()
    flat["economic_roles"] = flat["economic_roles"].apply(
        lambda rs: ";".join(f"{x['role']}:{x['source']}" for x in rs)
    )
    flat["sources"] = flat["sources"].apply(lambda s: ";".join(s))
    flat.to_csv(OUT_CSV, index=False)
    reread = load_region_register(__import__("pathlib").Path(OUT_PQ))
    assert len(reread) == len(validated) == 18
    gov_sum = sum(c[8] for c in CENTRES)
    pop_50 = [r.name_en for r in validated if r.threshold_50k]
    print("rows", len(validated), "governorates", len({r.governorate for r in validated}))
    print("gov pop sum (S-asir-001 governorate rows):", gov_sum)
    print("threshold_50k:", pop_50)
    print("pilot sample:", [r.name_en for r in validated if r.pilot_sample])
    print("screened false:", [r.name_en for r in validated if not r.screened])
    print(
        "tag_5k:", sum(r.tag_5k for r in validated), "tag_10k:", sum(r.tag_10k for r in validated)
    )
    print("null population:", [r.name_en for r in validated if r.population is None])
    for r in validated:
        print(
            r.name_en,
            r.population,
            r.dist_existing_km,
            r.nearest_existing,
            r.dist_committed_km,
            r.nearest_committed_station,
            r.dist_metro_km,
            r.nearest_metro,
            r.terrain_class,
        )


if __name__ == "__main__":
    main()
