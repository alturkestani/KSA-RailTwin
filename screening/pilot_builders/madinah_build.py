# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/pilot_madinah/build.py (last modified 2026-10-30 21:10 +03, pilot run PILOT_REGION_MADINAH).
# Role: built the region register.
# Outputs named in the code: pilot-madinah.csv, pilot-madinah.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Build the pilot Madinah register (one-off, outside the repo). Run from the worktree with `uv run python -I`."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

WT = Path("./")
sys.path.insert(0, str(WT))
from common.schemas import RegionRow  # noqa: E402

ACCESS = "2026-10-30"
R_EARTH = 6371.0088


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, lo1 = map(math.radians, a)
    la2, lo2 = map(math.radians, b)
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R_EARTH * math.asin(math.sqrt(h))


# Existing passenger stations located in OSM (KAEC not located; see docs/status).
HHR = {
    "HHR Madinah station (OSM node 10957110707)": (24.4722969, 39.6996036),
    "HHR Makkah station (OSM node 10956967098)": (21.4176557, 39.7885323),
    "HHR Al-Sulaymaniyah Jeddah station (OSM way 485762503)": (21.5167190, 39.2462714),
    "HHR Jeddah airport station (OSM node 7227897402)": (21.6605044, 39.1738182),
}
MADINAH_METRO = (24.4711530, 39.6111216)  # OSM node 4571693347, place=city

S_CITYPOP = "S-madinah-001"
S_OSM = "S-madinah-005"
S_HHR = "S-001"

# name_en, name_ar, governorate_en, governorate_ar, is_centre, osm_id, lat, lon, pop, roles, terrain, extra
ROWS = [
    dict(
        name_en="Al-Madinah al-Munawwarah",
        name_ar="المدينة المنورة",
        gov="Al-Madinah al-Munawwarah",
        gov_ar="المدينة المنورة",
        centre=True,
        osm_id=4571693347,
        lat=24.4711530,
        lon=39.6111216,
        pop=1411599,
        roles=[("hajj_umrah", "S-madinah-013"), ("airport", "S-madinah-013")],
        terrain="mixed",
        t50=True,
        sample=False,
        notes="Metro set primary (A-screen-013). Governorate centre = same-named place (A-screen-pilot-003). Census place row, city proper (S-083 matches). Mapped by OSM as place=city. HHR Madinah station lies in Al-Hadra district (S-madinah-005).",
    ),
    dict(
        name_en="Yanbu' al-Bahr",
        name_ar="ينبع البحر",
        gov="Yanbu' al-Bahr",
        gov_ar="ينبع",
        centre=True,
        osm_id=3148037089,
        lat=24.0890190,
        lon=38.0687076,
        pop=331916,
        roles=[("port", "S-madinah-008"), ("industrial_city", "S-madinah-008")],
        terrain="coastal",
        t50=True,
        sample=False,
        notes="Census place 'Yanbu al-Bahr [Yanbu; incl. Yanbu Industrial City]' = 331,916 (S-madinah-001); governorate row 359,631. OSM place=city node 3148037089 used; suburb node 1237968846 (Yanbu al-Bahr) is the alternative match. Census place includes the industrial city, so the population is not the town alone (Needs Opus judgement).",
    ),
    dict(
        name_en="Al-Ula",
        name_ar="العلا",
        gov="Al-Ula",
        gov_ar="العلا",
        centre=True,
        osm_id=7700293159,
        lat=26.5588965,
        lon=37.9596519,
        pop=40760,
        roles=[
            ("giga_project", "S-madinah-012"),
            ("heritage", "S-madinah-012"),
            ("tourism", "S-madinah-012"),
        ],
        terrain="escarpment_mountain",
        t50=False,
        sample=True,
        notes="Pilot sample (far, sourced roles: giga-project and heritage). Stratum: >100 km from the nearest located station. Census place 40,760 (<50k). Terrain: sandstone valley setting, assumed (A-screen-pilot-002).",
    ),
    dict(
        name_en="Badr",
        name_ar="بدر",
        gov="Badr",
        gov_ar="بدر",
        centre=True,
        osm_id=87175609,
        lat=23.7800000,
        lon=38.7907409,
        pop=30494,
        roles=[("heritage", "S-madinah-010"), ("tourism", "S-madinah-010")],
        terrain="mixed",
        t50=False,
        sample=True,
        notes="Pilot sample (far, sourced roles: heritage). OSM way 87175609 is tagged place=village, but the census place is 30,494 (type mismatch, edge case). Coordinates are the way centroid from Nominatim. Distance from Madinah is about 120–150 km by search summary (S-madinah-010, unverified detail).",
    ),
    dict(
        name_en="Khaybar",
        name_ar="خيبر",
        gov="Khaybar",
        gov_ar="خيبر",
        centre=True,
        osm_id=546640970,
        lat=25.7025446,
        lon=39.2932974,
        pop=15888,
        roles=[
            ("heritage", "S-madinah-011"),
            ("tourism", "S-madinah-011"),
            ("agriculture", "S-madinah-011"),
        ],
        terrain="mixed",
        t50=False,
        sample=True,
        notes="Pilot sample (far, sourced roles: heritage, tourism, agriculture/dates). Harrat Khaybar lava field (S-madinah-014). Census place 15,888 is the centre row.",
    ),
    dict(
        name_en="Mahd adh-Dhahab",
        name_ar="مهد الذهب",
        gov="Mahd adh-Dhahab",
        gov_ar="مهد الذهب",
        centre=True,
        osm_id=1237964803,
        lat=23.4995868,
        lon=40.8791554,
        pop=20272,
        roles=[("mining", "S-madinah-009")],
        terrain="mixed",
        t50=False,
        sample=True,
        notes="Pilot sample (far, sourced role: mining, Ma'aden gold mine). Distance from Madinah is given as 167 km (most sources) and 380 km (one Ithra article, S-madinah-009): unresolved, not used in any field. Centre = same-named place (A-screen-pilot-003).",
    ),
    dict(
        name_en="Al-Henakiyah",
        name_ar="الحناكية",
        gov="Al-Henakiyah",
        gov_ar="الحناكية",
        centre=True,
        osm_id=1236695024,
        lat=24.8797220,
        lon=40.5152780,
        pop=24880,
        roles=[],
        terrain="mixed",
        t50=False,
        sample=False,
        notes="Governorate centre; census place 24,880 (S-madinah-001). Economic roles NOT searched in the pilot: empty means not recorded, not 'no role'. Arabic name variant 'الحناكيه' in OSM.",
    ),
    dict(
        name_en="Al-'Aīṣ",
        name_ar="العيص",
        gov="Al-'Aīṣ",
        gov_ar="العيص",
        centre=True,
        osm_id=5813392174,
        lat=25.0635722,
        lon=38.1085415,
        pop=8760,
        roles=[],
        terrain="mixed",
        t50=False,
        sample=False,
        notes="Governorate centre; census place 8,760 (S-madinah-001). Below 10k: tag_10k false, tag_5k true. Economic roles NOT searched. Governorate boundary relation 12429013 (OSM) confirms the name.",
    ),
    dict(
        name_en="Ath-Thamad",
        name_ar="الثمد",
        gov="Khaybar",
        gov_ar="خيبر",
        centre=False,
        osm_id=7653649386,
        lat=25.5279589,
        lon=39.3394661,
        pop=8385,
        roles=[],
        terrain="mixed",
        t50=False,
        sample=True,
        notes="Pilot sample (far, no economic role recorded: NOT searched, so 'without role' means 'none recorded'). Non-centre town of Khaybar governorate, below 10k (tag_5k only). OSM place=town node.",
    ),
]


def build() -> pd.DataFrame:
    recs = []
    for r in ROWS:
        loc = (r["lat"], r["lon"])
        dists = {k: haversine(loc, v) for k, v in HHR.items()}
        near = min(dists, key=dists.get)
        d_ex = round(dists[near], 2)
        d_met = round(haversine(loc, MADINAH_METRO), 2)
        srcs = [S_CITYPOP, S_OSM, S_HHR]
        srcs += sorted({s for _, s in r["roles"]})
        srcs = sorted(set(srcs))
        pop = r["pop"]
        recs.append(
            {
                "name_ar": r["name_ar"],
                "name_en": r["name_en"],
                "region": "madinah",
                "governorate": r["gov"],
                "governorate_ar": r["gov_ar"],
                "is_governorate_centre": r["centre"],
                "osm_id": r["osm_id"],
                "lat": r["lat"],
                "lon": r["lon"],
                "population": pop,
                "pop_source": S_CITYPOP,
                "pop_year": 2022,
                "pop_type": "secondary",
                "tag_10k": pop >= 10_000,
                "tag_5k": pop >= 5_000,
                "dist_existing_km": d_ex,
                "road_min_existing": None,
                "nearest_existing": near,
                "dist_committed_km": None,
                "road_min_committed": None,
                "nearest_committed": None,
                "nearest_committed_station": None,
                "dist_metro_km": d_met,
                "road_min_metro": None,
                "nearest_metro": "Madinah (tier 1, A-screen-013)",
                "economic_roles": [{"role": ro, "source": s} for ro, s in r["roles"]],
                "terrain_class": r["terrain"],
                "screened": True,
                "exclusion_reason": None,
                "sources": srcs,
                "fixture": False,
                # pilot annotations (not in RegionRow; see docs/status/pilot-madinah.md)
                "threshold_50k": bool(r["t50"]),
                "pilot_sample": bool(r["sample"]),
                "nearest_metro_tier": 1,
                "primary_to_find": "GASTAT Census 2022 locality table (portal.saudicensus.sa; DNS failed on 2026-10-30)",
                "road_min_method": "pending R1a skims",
                "dist_method": "haversine",
                "notes": r["notes"],
            }
        )
    return pd.DataFrame(recs)


def validate(df: pd.DataFrame) -> list[str]:
    core = [c for c in RegionRow.model_fields]
    problems = []
    for i, rec in enumerate(df.to_dict(orient="records")):
        clean = {
            k: (None if (isinstance(v, float) and v != v) else v)
            for k, v in rec.items()
            if k in core
        }
        try:
            RegionRow.model_validate(clean)
        except Exception as e:  # noqa: BLE001
            problems.append(f"row {i} {rec['name_en']}: {str(e).splitlines()[0:3]}")
    return problems


if __name__ == "__main__":
    out = WT / "cities/ksa/regions"
    df = build()
    df_csv = df.copy()
    df_csv["economic_roles"] = df["economic_roles"].apply(
        lambda v: json.dumps(v, ensure_ascii=False)
    )
    df_csv["sources"] = df["sources"].apply(lambda v: ";".join(v))
    df_csv.to_csv(out / "pilot-madinah.csv", index=False)
    df.to_parquet(out / "pilot-madinah.parquet", index=False)
    print(
        df[
            [
                "name_en",
                "population",
                "is_governorate_centre",
                "tag_10k",
                "tag_5k",
                "dist_existing_km",
                "dist_metro_km",
                "pilot_sample",
                "threshold_50k",
            ]
        ].to_string()
    )
    print("rows:", len(df))
    print("validation problems:")
    for p in validate(df):
        print("  ", p)
    print(
        "sum of 9 governorate rows Madinah (citypop, incl. capital):",
        sum([22445, 43256, 1477047, 60103, 58259, 45532, 48590, 23120, 359631]),
    )
