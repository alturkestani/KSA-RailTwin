# ruff: noqa: E501  (prose-heavy generator: narrative strings and tables)
"""Najran region sweep (R2, slug `najran`): builds the register rows.

Inputs (all read locally, nothing downloaded):
- `cities/ksa/zones/settlements.parquet` (R1a universe; population, grid gap-fill, skims, committed distances)
- `cities/ksa/zones/economic_nodes.parquet` (R1a economic nodes, one source id per node)
- `data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx` and `..._city5k_primary.xlsx`
  (GASTAT primary exports, S-cp2-gastat-007 / -008; checked, not re-keyed)
- `cities/ksa/regions/pilot-najran.parquet` (pilot notes; GEO_VERIFY record-only strings are carried into `notes`)

Output: `cities/ksa/regions/najran.parquet` and `.csv`, validated by `screening.region_sweep validate --strict`.

    uv run python screening/sweeps/najran/build.py
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[3]
REGION = "najran"
GOV_COUNT = (
    7  # six governorates + the regional capital (S-najran-003; primary values checked below)
)
TAG_10K = 10_000
TAG_5K = 5_000
GRID_SOURCE = "S-r1a-506"  # WorldPop 2020, 100 m, constrained and UN-adjusted (R1a gap-fill)
GRID_YEAR = 2020
HAV = "haversine (A-screen-pilot-001)"
ROAD = "osrm_table_mld_car (R1a skims; free flow, uncalibrated)"
EXCL_GRID = "grid-only population, uncorroborated"
GOV_PRIMARY = REPO / "data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx"
CITY_PRIMARY = REPO / "data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx"
OUT = REPO / "cities/ksa/regions"

# osm_id -> (name_en, governorate_en, governorate_ar, centre?, name_note)
# name_en follows the GASTAT primary export spelling where one exists; grid-only names are
# transliterated by the coordinator from the Arabic OSM name (no GASTAT spelling exists for them).
ROWS = {
    982548735: ("Najran", "Najran", "نجران", True),
    1013646681: ("Sharurah", "Sharurah", "شرورة", True),
    11871306300: ("Hubuna", "Hubuna", "حبونا", True),
    8503374507: ("Khubash", "Khubash", "خباش", True),
    6774224946: ("Yadamah", "Yadamah", "يدمة", True),
    9327906415: ("Badr Al Janub", "Badr Al Janub", "بدر الجنوب", True),
    6774275597: ("Thar", "Thar", "ثار", True),
    4213220389: ("Al Mishaliah", "Najran", "نجران", False),
    1236473531: ("Al Wadiah", "Sharurah", "شرورة", False),
    6774270978: ("Aba Al Saud", "Najran", "نجران", False),
    11871306808: ("Al Mikhlaf", "Najran", "نجران", False),
    6774270081: ("Al Nukaysi", "Najran", "نجران", False),
    6774292689: ("Al Urayisah", "Najran", "نجران", False),
}

# Economic roles: osm_id -> list of (role, source). Every role names the source that ties it to
# the town. Sources: S-najran-001 (governorate table, secondary), S-cp1-100 (GACA airport names),
# S-r1a-210 (OSM positions), S-r1a-204 (MODON), S-r1a-205 (Wikidata), S-r1a-221/222 (university),
# S-najran-010 (border crossing, secondary snippet).
ROLES = {
    982548735: [
        ("administrative", "S-najran-001"),
        ("airport", "S-cp1-100;S-r1a-210"),
        ("university", "S-r1a-221;S-r1a-222;S-r1a-210"),
        ("industrial_city", "S-r1a-204;S-r1a-210"),
        ("heritage", "S-r1a-205"),
    ],
    1013646681: [("administrative", "S-najran-001"), ("airport", "S-cp1-100;S-r1a-210")],
    11871306300: [("administrative", "S-najran-001")],
    8503374507: [("administrative", "S-najran-001")],
    6774224946: [("administrative", "S-najran-001")],
    9327906415: [("administrative", "S-najran-001")],
    6774275597: [("administrative", "S-najran-001")],
    1236473531: [("border_crossing", "S-najran-010")],
}

# Terrain: assumed for every row (A-najran-001) until a DEM class is computed (no DEM run in R2).
TERRAIN = {1013646681: "dunes", 1236473531: "dunes"}

# Pilot assumptions for the Najran centre nodes (A-najran-003) and the record-only GEO_VERIFY notes.
PILOT = Path("cities/ksa/regions/archive/pilot/pilot-najran.parquet")


ROLE_IDS: dict[int, set[str]] = {
    osm: {src for _, s in roles for src in s.split(";")} for osm, roles in ROLES.items()
}


def _sources(osm: int, pop_source: str | None, centre: bool) -> list[str]:
    """Only the ids this row actually uses: OSM position, population, centre listing, roles."""
    ids = {"S-najran-004"} | ROLE_IDS.get(osm, set())
    if pop_source:
        ids.add(pop_source)
    if pop_source == "S-cp2-gastat-008":
        ids.add("S-cp2-gastat-001")  # relayed cross-check (0.0 % difference)
    if centre:
        ids.add("S-najran-001")
    return sorted(ids)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def gastat_check() -> int:
    """Confirm the seven Najran governorate populations appear in the GASTAT primary export."""
    gov = pd.read_excel(GOV_PRIMARY, header=None)
    values = set(pd.to_numeric(gov.iloc[:, 1], errors="coerce").dropna().astype(int))
    # the seven governorate totals of the region (S-073 rows, identical on the primary export)
    najran_govs = {421902, 100199, 24823, 16160, 13391, 7991, 7834}
    missing = sorted(v for v in najran_govs if v not in values)
    if missing or sum(najran_govs) != 592300:
        raise SystemExit(f"GASTAT primary check failed; missing {missing}")
    city = pd.read_excel(CITY_PRIMARY, header=None)
    names = (
        city.astype(str)
        .apply(
            lambda c: c.str.contains("Najran|Sharurah|Hubuna|Khubash|Mishaliah|Wadiah", regex=True)
        )
        .any(axis=1)
    )
    if int(names.sum()) < 6:
        raise SystemExit("GASTAT primary city export: fewer than six Najran city rows")
    return GOV_COUNT


def build() -> pd.DataFrame:
    gov_count = gastat_check()
    s = pd.read_parquet(REPO / "cities/ksa/zones/settlements.parquet")
    s = s[s.region == REGION].copy()
    econ = pd.read_parquet(REPO / "cities/ksa/zones/economic_nodes.parquet")
    hima = econ[econ.node_id == "heritage-bir-hima-hima-cultural-area"].iloc[0]
    pilot = pd.read_parquet(REPO / PILOT).set_index("osm_id")
    s["osm_id"] = s["osm_id"].astype("int64")

    out = []
    for osm, (name_en, gov_en, gov_ar, centre) in ROWS.items():
        r = s[s.osm_id == osm]
        if len(r) != 1:
            raise SystemExit(f"osm {osm}: expected one R1a row, found {len(r)}")
        r = r.iloc[0]
        grid_only = r.pop_type == "grid" if isinstance(r.pop_type, str) else False
        # population: GASTAT first (primary export, or relayed where the primary has no row);
        # WorldPop gap-fill only where neither exists (population rule, A-screen-031)
        pop = None if pd.isna(r.population) else int(r.population)
        if r.pop_type == "official" and r.pop_source == "gastat-census2022-ta1-city5k-xlsx":
            pop_source, pop_year, pop_type, status, prim = (
                "S-cp2-gastat-008",
                2022,
                "official",
                "verified",
                None,
            )
        elif r.pop_type == "official":  # S-najran-002 (citypopulation.de, credits GASTAT)
            pop_source, pop_year, pop_type, status = "S-najran-002", 2022, "official", "secondary"
            prim = "GASTAT Census 2022 locality table (places 2,500+ and the TA1 export is 5,000+ only; primary not reached for this row)"
        elif grid_only:
            pop_source, pop_year, pop_type, status = GRID_SOURCE, GRID_YEAR, "grid", "unverified"
            prim = "GASTAT Census 2022 locality table (not in the places 2,500+ table S-najran-002 nor the TA1 5,000+ export)"
        else:
            pop_source = pop_year = pop_type = status = prim = None

        corr = None
        if pop_type == "grid":
            corr = None  # no second independent method run for these rows (A-screen-033)
        tag_10k = bool(pop is not None and pop >= TAG_10K and pop_type != "grid")
        tag_5k = bool(pop is not None and pop >= TAG_5K)

        screened = True
        excl = None
        if pop_type == "grid" and pop is not None and pop >= TAG_10K:
            excl = EXCL_GRID
        if centre and pop is not None and pop < TAG_5K:
            screened, excl = (
                False,
                (
                    f"Centre population {pop:,} is below 5,000 (A-screen-002). Kept as the governorate-centre "
                    "coverage row (rule 2); the governorate total is not used as the centre figure."
                ),
            )

        lat, lon = float(r.lat), float(r.lon)
        dist_existing = (
            None if pd.isna(r.dist_existing_line_km) else round(float(r.dist_existing_line_km), 1)
        )
        dist_comm = (
            None if pd.isna(r.dist_committed_line_km) else round(float(r.dist_committed_line_km), 1)
        )
        dist_metro = (
            None if pd.isna(r.dist_metro_city_km) else round(float(r.dist_metro_city_km), 1)
        )

        notes = [
            f"R1a settlement {r.settlement_id}; OSM place={r.place} (node {osm}).",
            "Governorate centre (GASTAT list S-073 via S-najran-001; primary value checked on S-cp2-gastat-007)."
            if centre
            else "Non-centre locality.",
        ]
        if pop_type == "grid":
            notes.append(
                "Population is a WorldPop 2020 gap-fill (R1a; A-r1a-004), not a census figure; no second method "
                "run, so tag_10k is false (A-screen-031/032). Not in the GASTAT 2,500+ locality list (S-najran-002) "
                "nor the 5,000+ primary export: the grid figure may over-count (see Needs Opus judgement)."
            )
            if isinstance(r.control_total_flag, str):
                notes.append(f"R1a control flag: {r.control_total_flag}.")
        if pop_source == "S-cp2-gastat-008":
            notes.append(
                "Population = GASTAT Census 2022 TA1 primary export, city 5,000+ (S-cp2-gastat-008); the relayed figure "
                "agrees (S-cp2-gastat-001)."
            )
        if osm in pilot.index:
            geo = [seg for seg in str(pilot.loc[osm, "notes"]).split(" | ") if "GEO_VERIFY" in seg]
            notes += [f"Pilot record only ({'; '.join(geo)})."] if geo else []
        if osm == 6774224946 or osm == 9327906415:
            notes.append(
                "GASTAT figure relayed (S-najran-002), below 5,000; a primary locality figure is still to be read."
            )
        if osm == 8503374507 or osm == 11871306300:
            notes.append(
                "OSM holds a second candidate for this centre (governorate node); the town/village node is used (A-najran-003)."
            )
        if osm == 6774275597:
            notes.append(
                "Conflict on the 5,000 line: R1a WorldPop allocation 8,030 (3.0 km) against the pilot grid 6,144 (1 km) and "
                "the record-only buildings estimate 4,465 (band 1,314-10,245; back-test above the 30 % gate). tag_5k rests on "
                "the uncorroborated grid figure; the sensitivity is for the funnel."
            )
        if osm == 4213220389:
            notes.append(
                "OSM place=village against a census figure of 23,252 (largest non-centre locality in the governorate); census figure used."
            )
        if osm == 1236473531:
            notes.append(
                "Border-crossing role rests on a secondary snippet (S-najran-010); verify before use."
            )
        if osm == 982548735:
            notes.append(
                f"Heritage: Hima cultural area (S-r1a-205) is {haversine_km(lat, lon, float(hima.lat), float(hima.lon)):.0f} km "
                "from this row; tied to this town through R1a's nearest-town field (A-najran-005)."
            )
        if osm in (6774270978, 11871306808, 6774270081, 6774292689):
            notes.append(
                "name_en transliterated by the coordinator from the Arabic OSM name (no GASTAT spelling)."
            )
        if osm == 1013646681:
            notes.append(
                "Airport role verified by location: OSM aerodrome node (R1a economic node airport-shw-sharurah)."
            )

        out.append(
            {
                "name_ar": r.name_ar,
                "name_en": name_en,
                "region": REGION,
                "governorate": gov_en,
                "governorate_ar": gov_ar,
                "is_governorate_centre": centre,
                "osm_id": osm,
                "osm_type": "node",
                "lat": lat,
                "lon": lon,
                "population": pop,
                "pop_source": pop_source,
                "pop_year": pop_year,
                "pop_type": pop_type,
                "pop_source_status": status,
                "primary_to_find": prim,
                "pop_corroboration": corr,
                "pop_corroboration_value": None,
                "tag_10k": tag_10k,
                "tag_5k": tag_5k,
                "dist_existing_km": dist_existing,
                "road_min_existing": None
                if pd.isna(r.road_min_existing)
                else round(float(r.road_min_existing), 1),
                "nearest_existing": f"{r.nearest_existing_line} (road target {r.road_target_existing})",
                "dist_committed_km": dist_comm,
                "road_min_committed": None
                if pd.isna(r.road_min_committed)
                else round(float(r.road_min_committed), 1),
                "nearest_committed": r.nearest_committed_line,
                "nearest_committed_station": (
                    "landbridge:muwai, Muwai/Moya, announced stop (S-062)"
                    if r.nearest_committed_line == "landbridge"
                    else r.road_target_committed
                ),
                "dist_metro_km": dist_metro,
                "road_min_metro": None
                if pd.isna(r.road_min_metro_city)
                else round(float(r.road_min_metro_city), 1),
                "nearest_metro": r.nearest_metro_city,
                "nearest_metro_tier": int(r.nearest_metro_tier),
                "economic_roles": [{"role": ro, "source": so} for ro, so in ROLES.get(osm, [])],
                "terrain_class": TERRAIN.get(osm, "mixed"),
                "screened": screened,
                "exclusion_reason": excl,
                "sources": _sources(osm, pop_source, centre),
                "threshold_50k": None,
                "pilot_sample": None,
                "road_min_method": ROAD,
                "dist_method": HAV,
                "notes": " | ".join(notes),
            }
        )

    df = pd.DataFrame(out)
    df.attrs["governorates_gastat"] = gov_count
    return df


def write(df: pd.DataFrame) -> None:
    """Parquet with the GASTAT header counts (region-sweep skill), and the CSV mirror."""
    for col in ("osm_id", "population", "pop_year", "nearest_metro_tier"):
        df[col] = df[col].astype("Int64")
    listed = df["governorate"].nunique()
    meta = {
        b"governorates_gastat": str(df.attrs["governorates_gastat"]).encode(),
        b"governorates_listed": str(listed).encode(),
    }
    table = pa.Table.from_pandas(df, preserve_index=False)
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
    pq.write_table(table, OUT / "najran.parquet")
    csv = df.copy()
    csv["economic_roles"] = csv["economic_roles"].map(
        lambda r: ";".join(f"{x['role']}:{x['source']}" for x in r)
    )
    csv["sources"] = csv["sources"].map(";".join)
    csv.to_csv(OUT / "najran.csv", index=False)


if __name__ == "__main__":
    register = build()
    write(register)
    print(
        register[["name_en", "population", "pop_type", "tag_5k", "tag_10k", "screened"]].to_string()
    )
