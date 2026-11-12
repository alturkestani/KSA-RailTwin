# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: cities/ksa/regions/build_pilot_riyadh.py (tracked in the repo until CP1_PREP) (last modified 2026-10-30 22:11 +03, pilot run PILOT_REGION_RIYADH).
# Role: built the region register.
# Outputs named in the code: pilot-riyadh.csv, pilot-riyadh.parquet.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

"""Builds the Riyadh pilot register (cities/ksa/regions/pilot-riyadh.{parquet,csv}).

One source of truth: the ROWS below. Every field comes from a source id in
docs/sources/pilot-riyadh.csv (or an existing S-nnn in docs/sources/index.csv) or an
assumption id in docs/assumptions-pilot-riyadh.md.
Run: PYTHONPATH=. uv run python cities/ksa/regions/build_pilot_riyadh.py
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from common.schemas import LABEL_TEXT, RegionRow, load_region_register

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT_PARQUET = HERE / "pilot-riyadh.parquet"
OUT_CSV = HERE / "pilot-riyadh.csv"
OUT_MD = REPO / "docs" / "regions" / "pilot-riyadh.md"

EARTH_R_KM = 6371.0088  # mean radius; assumption A-screen-pilot-001 (haversine)

# Existing passenger rail, proxied by published station places (S-018 North, S-025 East).
# Station coordinates = place centres (A-screen-pilot-004); line geometry is pending R1a.
EXISTING = {
    "SAR North passenger: Riyadh station (proxy)": (24.6389160, 46.7160104),
    "SAR North passenger: Al-Majma'ah (proxy)": (25.9038890, 45.3455560),
}
# Committed: Landbridge Riyadh-Jeddah, intermediate station Dawadimi (S-062; no location in source).
COMMITTED = {"Landbridge Riyadh-Jeddah, Dawadimi intermediate (proxy)": (24.4941670, 44.3833330)}
METRO_RIYADH = (24.6389160, 46.7160104)  # Riyadh Metro (existing since Dec 2024; S-037); tier 1

SRC_GOV_LIST = "S-073"  # governorate rows (secondary; GASTAT count unverified, S-072)
PRIMARY_TO_FIND = (
    "GASTAT Census 2022 locality table (portal.saudicensus.sa unreachable 30 Oct 2026; S-090)"
)
TERRAIN_DEFAULT = "A-screen-pilot-002"


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * EARTH_R_KM * math.asin(math.sqrt(h))


def row(
    name_en: str,
    name_ar: str,
    gov_en: str,
    gov_ar: str,
    centre: bool,
    lat: float,
    lon: float,
    *,
    osm: tuple[str, int] | None = None,
    pop: int | None = None,
    pop_source: str | None = None,
    pop_year: int | None = None,
    roles: list[tuple[str, str]] = (),
    terrain: tuple[str, str] = ("flat_desert", TERRAIN_DEFAULT),
    sample: bool = False,
    notes: str = "",
    excl: str | None = None,
) -> dict:
    """One register row. `osm` = (type, id) of a place node; None when the coordinate is a proxy."""
    pop_type = "secondary" if pop is not None else None
    sources = [SRC_GOV_LIST, "S-018", "S-025", "S-037", "S-062", "S-riyadh-010"]
    sources += [pop_source] if pop_source else []
    sources += [r[1] for r in roles]
    if terrain[1].startswith("S-") and terrain[1] not in sources:
        sources.append(terrain[1])
    dist_existing = min(haversine_km((lat, lon), p) for p in EXISTING.values())
    near_name = min(EXISTING, key=lambda k: haversine_km((lat, lon), EXISTING[k]))
    dist_com = min(haversine_km((lat, lon), p) for p in COMMITTED.values())
    dist_metro = haversine_km((lat, lon), METRO_RIYADH)
    rec = {
        "name_ar": name_ar,
        "name_en": name_en,
        "region": "riyadh",
        "governorate": gov_en,
        "governorate_ar": gov_ar,
        "is_governorate_centre": centre,
        "osm_id": osm[1] if osm else None,
        "osm_type": osm[0] if osm else None,
        "lat": lat,
        "lon": lon,
        "population": pop,
        "pop_source": pop_source,
        "pop_year": pop_year if pop is not None else None,
        "pop_type": pop_type,
        "primary_to_find": PRIMARY_TO_FIND if pop is not None else None,
        "tag_10k": pop is not None and pop >= 10_000,
        "tag_5k": pop is not None and pop >= 5_000,
        "threshold_50k": pop is not None and pop >= 50_000,
        "dist_existing_km": round(dist_existing, 1),
        "road_min_existing": None,
        "nearest_existing": near_name,
        "dist_committed_km": round(dist_com, 1),
        "road_min_committed": None,
        "nearest_committed": "Landbridge Riyadh-Jeddah (announced/planned; S-054, S-062)",
        "nearest_committed_station": next(iter(COMMITTED)),
        "dist_metro_km": round(dist_metro, 1),
        "road_min_metro": None,
        "nearest_metro": "Riyadh",
        "nearest_metro_tier": 1,
        "distance_method": (
            "haversine (A-screen-pilot-001); lat/lon as listed in osm_type/osm_id or proxy (notes)"
        ),
        "road_min_method": "pending R1a skims",
        "economic_roles": [{"role": r, "source": s} for r, s in roles],
        "terrain_class": terrain[0],
        "terrain_source": terrain[1],
        "screened": excl is None,
        "exclusion_reason": excl,
        "sources": sources,
        "pilot_sample": sample,
        "notes": notes,
        "fixture": False,
    }
    RegionRow.model_validate(rec)  # fail early on any schema breach
    return rec


NO_POP = "population not sourced in pilot (governorate total only; S-073/S-riyadh-001)"
PROXY_REL = (
    "coordinate = OSM governorate boundary centroid (not the town; town node not found in "
    "Nominatim)"
)
UNI = "S-riyadh-011"

ROWS = [
    row(
        "Riyadh",
        "الرياض",
        "Ar-Riyadh",
        "الرياض",
        True,
        24.6389160,
        46.7160104,
        osm=("node", 315358390),
        pop=6_924_566,
        pop_source="S-080",
        pop_year=2022,
        roles=[],
        terrain=("escarpment_mountain", "S-riyadh-015"),
        notes="Region and national capital (GASTAT list S-073). City-proper 6,924,566 (S-080) vs "
        "7,000,100 "
        "(Wikipedia, S-riyadh-009) vs 7,009,120 (governorate, S-riyadh-001): unresolved, flagged. "
        "Riyadh Rail Link (35 km, committed, S-060): no station coordinates, distance not "
        "computed.",
    ),
    row(
        "Ad-Dawadmi",
        "الدوادمي",
        "Ad-Dawadmi",
        "الدوادمي",
        True,
        24.4941670,
        44.3833330,
        osm=("node", 1236695687),
        pop=86_861,
        pop_source="S-riyadh-009",
        pop_year=2022,
        notes="Landbridge intermediate station named in S-062 (no location in source; this town "
        "centre "
        "is the proxy). "
        "Governorate total 200,620 (S-riyadh-001) is not the town figure. Secondary (Wikipedia).",
    ),
    row(
        "Ad-Dilam",
        "الدلم",
        "Ad-Dilam",
        "الدلم",
        True,
        23.9969440,
        47.1650000,
        osm=None,
        excl=NO_POP,
        notes=PROXY_REL + " (OSM relation 12423665). Governorate total 54,822 (S-riyadh-001). "
        "Centre town node not found; pilot does not screen it.",
    ),
    row(
        "Ad-Dir'iyah",
        "الدرعية",
        "Ad-Dir'iyah",
        "الدرعية",
        True,
        24.7483029,
        46.5717678,
        osm=("node", 1236703790),
        pop=61_609,
        pop_source="S-riyadh-003",
        pop_year=2022,
        roles=[("heritage", "S-riyadh-012"), ("giga_project", "S-riyadh-013")],
        terrain=("flat_desert", TERRAIN_DEFAULT),
        notes="At-Turaif District inscribed 2010 (UNESCO 1329, S-riyadh-012). Diriyah Gate "
        "giga-project (S-riyadh-013). "
        "Sits on Wadi Hanifa near the Tuwaiq escarpment (S-riyadh-015), but the class is "
        "assumed, not sourced. "
        "Town 61,609 (S-riyadh-003); governorate total 95,834 (S-riyadh-001).",
    ),
    row(
        "'Afif",
        "عفيف",
        "'Afif",
        "عفيف",
        True,
        23.9023697,
        42.9150847,
        osm=None,
        pop=47_340,
        pop_source="S-riyadh-005",
        pop_year=2022,
        sample=True,
        notes="Unmapped OSM place: no place node found in Nominatim (Arabic and English queries). "
        "Coordinate is the "
        "governorate boundary relation centroid (OSM 12423683), a proxy, not the town. Pilot "
        "sample: far from "
        "existing rail (>100 km by proxy), no sourced economic role, schema edge (osm_id null).",
    ),
    row(
        "Layla",
        "ليلى",
        "Al-Aflaj",
        "الأفلاج",
        True,
        22.2929472,
        46.7171558,
        osm=("node", 1236714296),
        pop=None,
        excl=NO_POP,
        notes="Presumed centre: OSM place=city node 'Layla' inside the Al Aflaj governorate. The "
        "centre identity and the "
        "Arabic name are unverified against GASTAT (open item for R2). Governorate total 54,544 "
        "(S-riyadh-001).",
    ),
    row(
        "Al-Ghat",
        "الغاط",
        "Al-Ghat",
        "الغاط",
        True,
        26.0286110,
        44.9508330,
        osm=("node", 1237933651),
        pop=None,
        excl=NO_POP,
        roles=[("university", UNI)],
        notes="Branch campus of Majmaah University (S-riyadh-011). Governorate total 10,799 "
        "(S-riyadh-001); town figure not sourced.",
    ),
    row(
        "Al-Hariq",
        "الحريق",
        "Al-Hariq",
        "الحريق",
        True,
        23.6336110,
        46.5138890,
        osm=("node", 1236708740),
        pop=None,
        excl=NO_POP,
        notes="Governorate total 10,864 (S-riyadh-001); town figure not sourced. Arabic "
        "governorate "
        "name from S-073 list.",
    ),
    row(
        "Al-Kharj",
        "الخرج",
        "Al-Kharj",
        "الخرج",
        True,
        23.8304401,
        47.6840134,
        osm=None,
        pop=295_462,
        pop_source="S-riyadh-007",
        pop_year=2022,
        roles=[("military", "S-riyadh-014")],
        notes="Coordinate is the OSM governorate boundary centroid (relation 12423676), a proxy: "
        "the "
        "town node was not found, "
        "and the centroid may be tens of km from the town. Town 295,462 (S-riyadh-007) vs "
        "governorate 373,177 (S-riyadh-001). "
        "Prince Sultan Air Base (S-riyadh-014) ~80-100 km SE of Riyadh (sources disagree). "
        "Freight line incl. Al-Kharj (S-026) is not a passenger line, not used as existing.",
    ),
    row(
        "Al-Majma'ah",
        "المجمعة",
        "Al-Majma'ah",
        "المجمعة",
        True,
        25.9038890,
        45.3455560,
        osm=("node", 1236400187),
        pop=70_243,
        pop_source="S-riyadh-008",
        pop_year=2022,
        roles=[("university", UNI)],
        notes="Main campus of Majmaah University (S-riyadh-011). Lies on SAR North (S-018), so it "
        "is "
        "the existing-rail proxy itself. "
        "Governorate total 151,877 (S-riyadh-001); town 70,243 (S-riyadh-008) also in "
        "S-riyadh-009.",
    ),
    row(
        "Al-Muzahimiyah",
        "المزاحمية",
        "Al-Muzahimiyah",
        "المزاحمية",
        True,
        24.4727747,
        46.2705605,
        osm=("node", 1013646924),
        pop=55_604,
        pop_source="S-riyadh-004",
        pop_year=2022,
        notes="Town figure 55,604 (S-riyadh-004); the page labels it 'Place'. Governorate total "
        "62,760 "
        "(S-riyadh-001) is not the town figure.",
    ),
    row(
        "Al-Quwayiyah",
        "القويعية",
        "Al-Quwayiyah",
        "القويعية",
        True,
        24.0650560,
        45.2843810,
        osm=None,
        excl=NO_POP,
        notes=PROXY_REL + " (OSM relation 12423672). Governorate total 71,410 (S-riyadh-001).",
    ),
    row(
        "Ar-Rayn",
        "الرين",
        "Ar-Rayn",
        "الرين",
        True,
        23.5406188,
        45.5108048,
        osm=("node", 1236421402),
        pop=None,
        excl=NO_POP,
        notes="Governorate total 28,243 (S-riyadh-001); town figure not sourced.",
    ),
    row(
        "As-Sulayyil",
        "السليل",
        "As-Sulayyil",
        "السليل",
        True,
        20.4597220,
        45.5744440,
        osm=None,
        excl=NO_POP,
        notes=PROXY_REL
        + " (OSM relation 12423668). Governorate total 35,271 (S-riyadh-001); town figure not "
        "sourced.",
    ),
    row(
        "Az-Zulfi",
        "الزلفي",
        "Az-Zulfi",
        "الزلفي",
        True,
        26.2995806,
        44.8151967,
        osm=None,
        pop=68_317,
        pop_source="S-riyadh-009",
        pop_year=2022,
        roles=[("university", UNI)],
        notes="Coordinate is the OSM governorate boundary centroid (relation 12423674), a proxy. "
        "Branch campus of Majmaah University "
        "(S-riyadh-011). Town 68,317 (S-riyadh-009, secondary); governorate total 74,903 "
        "(S-riyadh-001).",
    ),
    row(
        "Durma",
        "ضرما",
        "Durma",
        "ضرما",
        True,
        24.5955100,
        46.1337430,
        osm=("node", 1236704884),
        pop=None,
        excl=NO_POP,
        notes="Governorate total 26,299 (S-riyadh-001); town figure not sourced.",
    ),
    row(
        "Hawtat Bani Tamim",
        "حوطة بني تميم",
        "Hawtat Bani Tamim",
        "حوطة بني تميم",
        True,
        23.4874984,
        46.8787064,
        osm=None,
        excl=NO_POP,
        notes=PROXY_REL
        + " (OSM relation 12423669). Governorate total 41,854 (S-riyadh-001); town figure not "
        "sourced. "
        "'Hotat Sudair' branch campus (S-riyadh-011) is not mapped to this row: the naming match "
        "is unconfirmed.",
    ),
    row(
        "Huraymila",
        "حريملاء",
        "Huraymila",
        "حريملاء",
        True,
        25.1266670,
        46.1225000,
        osm=None,
        excl=NO_POP,
        notes=PROXY_REL
        + " (OSM relation 12423671). Governorate total 21,758 (S-riyadh-001); town figure not "
        "sourced.",
    ),
    row(
        "Marat",
        "مرات",
        "Marat",
        "مرات",
        True,
        25.0716670,
        45.4572220,
        osm=("way", 31154343),
        pop=None,
        excl=NO_POP,
        notes="Way-mapped town (OSM place=town). Governorate total 9,846 (S-riyadh-001); town "
        "figure "
        "not sourced.",
    ),
    row(
        "Rimah",
        "رماح",
        "Rimah",
        "رماح",
        True,
        25.5697220,
        47.1566670,
        osm=("node", 1236703436),
        pop=25_031,
        pop_source="S-riyadh-006",
        pop_year=2022,
        sample=True,
        roles=[("university", UNI)],
        terrain=("flat_desert", TERRAIN_DEFAULT),
        notes="Pilot sample (far, with a role): ~110 km from Riyadh and ~180 km from Majmaah by "
        "proxy. "
        "Branch campus of Majmaah University "
        "(S-riyadh-011). Governorate total 35,683 (S-riyadh-001) is not the town figure.",
    ),
    row(
        "Shaqra",
        "شقراء",
        "Shaqra",
        "شقراء",
        True,
        25.2483330,
        45.2527780,
        osm=None,
        excl=NO_POP,
        notes=PROXY_REL
        + " (OSM relation 12423677). Governorate total 46,403 (S-riyadh-001); town figure not "
        "sourced. "
        "Town vs governorate figures diverge across aggregators (city-facts.com, unreliable).",
    ),
    row(
        "Thadiq",
        "ثادق",
        "Thadiq",
        "ثادق",
        True,
        25.2810000,
        45.8630000,
        osm=("node", 1014940192),
        pop=None,
        excl=NO_POP,
        notes="Governorate total 12,510 (S-riyadh-001); town figure not sourced.",
    ),
    row(
        "Wadi ad-Dawasir",
        "وادي الدواسر",
        "Wadi ad-Dawasir",
        "وادي الدواسر",
        True,
        20.4602516,
        44.7995530,
        osm=None,
        excl=NO_POP,
        notes=PROXY_REL
        + " (OSM relation 12423662). Governorate total 91,535 (S-riyadh-001); the town figure "
        "is unresolved: Needs Opus judgement (a governorate total is not the centre figure).",
    ),
    # non-centre samples (5k-50k, Ad-Dir'iyah governorate)
    row(
        "Al-Uyaynah",
        "العيينة",
        "Ad-Dir'iyah",
        "الدرعية",
        False,
        24.9052780,
        46.3913890,
        osm=("node", 1014940282),
        pop=8_649,
        pop_source="S-riyadh-003",
        pop_year=2022,
        sample=True,
        notes="Pilot sample (mid-distance, no sourced role, non-centre town): ~44 km from Riyadh "
        "station proxy. "
        "Town 8,649 (S-riyadh-003). Heritage role not sourced, so none recorded.",
    ),
    row(
        "Al-Jubaylah",
        "الجبيلة",
        "Ad-Dir'iyah",
        "الدرعية",
        False,
        24.9138234,
        46.4448418,
        osm=("node", 1236702040),
        pop=8_005,
        pop_source="S-riyadh-003",
        pop_year=2022,
        sample=True,
        notes="Pilot sample (mid-distance, no sourced role, non-centre town): ~40 km from Riyadh "
        "station proxy. "
        "Town 8,005 (S-riyadh-003). Diriyah Gate boundary relation to this town not verified.",
    ),
]


def build() -> pd.DataFrame:
    df = pd.DataFrame(ROWS)
    df.to_parquet(
        OUT_PARQUET,
        index=False,
        engine="pyarrow",
    )
    df.to_csv(OUT_CSV, index=False)
    return df


if __name__ == "__main__":
    df = build()
    register = load_region_register(OUT_PARQUET)
    print(f"rows={len(df)} validated={len(register)} governorates={df['governorate'].nunique()}")
    n50, nsample = int(df["threshold_50k"].sum()), int(df["pilot_sample"].sum())
    print(f"threshold_50k={n50} pilot_sample={nsample}")
    print(LABEL_TEXT)
