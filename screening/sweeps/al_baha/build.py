"""Build the R2 region register for Al-Baha (الباحة), slug `al_baha` (region-sweep skill).

Inputs are read-only and already registered upstream: the R1a settlement universe
(`cities/ksa/zones/settlements.parquet`, with the CP2 GASTAT primary figures and the R1a distance
fields applied), the R1a economic nodes (`cities/ksa/zones/economic_nodes.parquet`), the OSM
governorate polygons (`cities/ksa/zones/governorates.geojson`) and the GASTAT Census 2022 TA1
primary Excel exports (S-cp2-gastat-007/008). Nothing is downloaded here.

Rows: the 10 governorate centres (one per governorate; Al-Qara has no OSM place node, see
`CENTRE`), every settlement with population >= 5,000 (tag_5k), and every OSM place=city|town in the
region. The rest of the universe (about 200 villages and hamlets below 5,000) stays in
`settlements.parquet`; it is not in this register.

Run: `uv run python -m screening.sweeps.al_baha.build --seed 1`
"""

from __future__ import annotations

import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

from common.runmeta import rng
from common.schemas import GRID_UNCORROBORATED, TAG_5K, TAG_10K, corroborates

ROOT = Path(__file__).resolve().parents[3]
REGION = "al_baha"
UNIVERSE = ROOT / "cities/ksa/zones/settlements.parquet"
ECON = ROOT / "cities/ksa/zones/economic_nodes.parquet"
GOV_GEO = ROOT / "cities/ksa/zones/governorates.geojson"
GOV_PRIMARY = ROOT / "data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx"
CITY_PRIMARY = ROOT / "data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx"
OUT = ROOT / "cities/ksa/regions/al_baha.parquet"

# GASTAT region total for Al-Bahah (S-r1a-502; citypopulation region table S-al_baha-001).
REGION_TOTAL_2022 = 339_174
GOVERNORATES_GASTAT = 10  # the 10 governorate names below; their sum equals REGION_TOTAL_2022

# Governorate centre rows, checked by hand: settlement_id -> the governorate (gov_id) it must belong
# to in the universe (asserted below). Al-Qara (G006) has no OSM place node in the universe: its row
# uses the governorate polygon's representative point, flagged in notes (A-al_baha-002).
CENTRE: dict[str, str | None] = {
    "G001": "KSA-ST-01855",  # Al-Aqiq: OSM town (Al `Aqiq); GASTAT Alaqiq 19,269
    "G002": "KSA-ST-00013",  # Al-Bahah: OSM city; GASTAT Albahah 90,515
    "G003": "KSA-ST-00581",  # Al-Hajrah: OSM village (الحجرة); grid figure only
    "G004": "KSA-ST-01336",  # Al-Mandaq: OSM town (Al Mindak); GASTAT Almandaq 8,674
    "G005": "KSA-ST-00575",  # Al-Mukhwah: OSM town (Al Makhwah); GASTAT Almukhwah 26,248
    "G006": None,  # Al-Qara: no place node in the universe
    "G007": "KSA-ST-01515",  # Bani Hasan: OSM town (بني حسن); GASTAT Bani Hasan 6,344
    "G008": "KSA-ST-00566",  # Biljurashi: OSM town (Baljurashi); GASTAT Biljurashi 35,985
    "G009": "KSA-ST-01891",  # Farat Ghamid Az Zinad: OSM town (Ghamid Az Zinad); grid figure only
    "G010": "KSA-ST-03122",  # Qilwah: OSM town; GASTAT Qilwah 13,069
}

# English names where the universe carries only the Arabic name or an OSM spelling we rewrite.
NAME_EN: dict[str, str] = {
    "KSA-ST-01855": "Al-'Aqiq",
    "KSA-ST-01336": "Al-Mindak",
    "KSA-ST-00581": "Al-Hajrah",
    "KSA-ST-01515": "Bani Hasan",
    "KSA-ST-07026": "Sayal",
}

# Sources: docs/sources/r2-al_baha.csv (S-al_baha-1xx; cross-referenced to the shared ids).
S_GOV = "S-al_baha-101"  # S-cp2-gastat-007
S_CITY = "S-al_baha-102"  # S-cp2-gastat-008
S_UNIV = "S-al_baha-103"  # R1a settlement universe (OSM ODbL; CP2 apply)
S_GRID = "S-al_baha-104"  # S-r1a-505 WorldPop 2020 100 m constrained, not UN-adjusted
S_ADMIN = "S-al_baha-105"  # OSM governorate polygons (Geofabrik GCC extract, ODbL)
S_ROAD = "S-al_baha-106"  # S-r1a-809 OSRM road distances and times
S_ECON = "S-al_baha-107"  # R1a economic nodes (S-r1a-204/210/221 and the GACA source S-cp1-100)
S_AIRPORT = "S-al_baha-108"  # Wikipedia, Al-Aqiq (airport located in Al-Aqiq)
S_TERRAIN = "S-al_baha-109"  # Wikipedia, Sarawat Mountains (region-level escarpment)
S_UNIV_LIST = "S-al_baha-110"  # Wikipedia list of universities by province (S-r1a-221)
S_MODON = "S-al_baha-111"  # MODON industrial cities (S-r1a-204)
S_CITYPOP = (
    "S-al_baha-112"  # citypopulation.de region table, cross-check only (pilot S-al_baha-001)
)
S_SAUDIPEDIA = "S-al_baha-113"  # Saudipedia, Bani Hasan governorate (pilot S-al_baha-012)

DIST_METHOD = "haversine to station (R1a distances.py); committed stations are unlocated proxies"
AIRPORT = (20.29681, 41.63983)  # R1a economic node airport-abt-al-baha (OSM aerodrome)
BAHAH_CITY = (20.013794, 41.465638)  # universe KSA-ST-00013
ASSUMPTION_TERRAIN = "A-al_baha-001"
ASSUMPTION_CENTRE = "A-al_baha-002"
ASSUMPTION_AIRPORT = "A-al_baha-003"
ASSUMPTION_COMMITTED = "A-al_baha-004"

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


def primary_city(path: Path = CITY_PRIMARY) -> dict[str, int]:
    """Census 2022 TA1 city (>= 5,000) primary figures, Al-Bahah names only (read from the xlsx)."""
    d = pd.read_excel(path, dtype={0: str})
    d.columns = ["city", "total", "saudi", "nonsaudi"]
    return dict(zip(d.city, d.total.astype(int), strict=True))


def primary_governorates(path: Path = GOV_PRIMARY) -> pd.DataFrame:
    d = pd.read_excel(path, dtype={0: str})
    d.columns = ["governorate", "total", "saudi", "nonsaudi"]
    return d


def governorate_info() -> dict[str, dict[str, Any]]:
    """gov_id -> {name_en, name_ar, geometry} for Al-Bahah's polygons in the OSM admin file."""
    gj = json.loads(GOV_GEO.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for f in gj["features"]:
        p = f["properties"]
        if p.get("region") == REGION:
            out[p["gov_id"]] = {
                "name_en": p["name_en"],
                "name_ar": p["name_ar"],
                "geometry": f["geometry"],
            }
    return out


def centre_point(geom: dict[str, Any]) -> tuple[float, float]:
    """Representative point inside the polygon (shapely), used only for Al-Qara (A-al_baha-002)."""
    from shapely.geometry import shape

    pt = shape(geom).representative_point()
    return float(pt.y), float(pt.x)


def role_rows(sid: str | None, gov_id: str, is_centre: bool) -> list[dict[str, str]]:
    """Economic roles, each with an S- source that ties it to this town (A-screen-011)."""
    roles: list[dict[str, str]] = []
    if is_centre:
        roles.append({"role": "administrative", "source": f"{S_GOV};{S_ADMIN}"})
    if sid == "KSA-ST-00013":  # Al-Bahah
        roles.append({"role": "university", "source": f"{S_UNIV_LIST};{S_ECON}"})
        roles.append({"role": "industrial_city", "source": S_MODON})
    if sid == "KSA-ST-01855":  # Al-Aqiq: the domestic airport is located here (A-al_baha-003)
        roles.append({"role": "airport", "source": f"{S_AIRPORT};{S_ECON}"})
    return roles


def build_rows(univ: pd.DataFrame, govs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    centre_ids = {v for v in CENTRE.values() if v}
    keep = univ.population.fillna(0).ge(TAG_5K) | univ.place.isin(["city", "town"])
    keep |= univ.settlement_id.isin(centre_ids)
    sel = univ[keep].sort_values(["gov_id", "population"], ascending=[True, False])

    for gov_id, g in govs.items():
        sid = CENTRE[gov_id]
        if sid is None:  # Al-Qara: no universe row, polygon point
            lat, lon = centre_point(g["geometry"])
            rows.append(
                _row(
                    name_en=g["name_en"],
                    name_ar=g["name_ar"].replace("محافظة ", ""),
                    gov_id=gov_id,
                    g=g,
                    centre=True,
                    lat=lat,
                    lon=lon,
                    osm_id=None,
                    osm_type=None,
                    u=None,
                )
            )

    for _, u in sel.iterrows():
        gov_id = u.gov_id
        is_centre = u.settlement_id in centre_ids and CENTRE.get(gov_id) == u.settlement_id
        assert gov_id in govs, f"{u.settlement_id}: governorate {gov_id} not an Al-Bahah polygon"
        if u.settlement_id in centre_ids:
            assert CENTRE[gov_id] == u.settlement_id, (
                f"{u.settlement_id} is a centre of another gov"
            )
        rows.append(
            _row(
                name_en=NAME_EN.get(
                    u.settlement_id, u.name_en if isinstance(u.name_en, str) else u.name_ar
                ),
                name_ar=u.name_ar,
                gov_id=gov_id,
                g=govs[gov_id],
                centre=is_centre,
                lat=float(u.lat),
                lon=float(u.lon),
                osm_id=int(u.osm_id),
                osm_type=u.osm_type,
                u=u,
            )
        )
    return rows


def _row(
    *,
    name_en: str,
    name_ar: str,
    gov_id: str,
    g: dict[str, Any],
    centre: bool,
    lat: float,
    lon: float,
    osm_id: int | None,
    osm_type: str | None,
    u: pd.Series | None,
) -> dict[str, Any]:
    sid = None if u is None else u.settlement_id
    pop = None if u is None or pd.isna(u.population) else int(u.population)
    pop_type = pop_source = pop_year = pop_status = None
    sources = [S_UNIV, S_ADMIN, S_GOV, S_ROAD] if u is not None else [S_ADMIN]
    roles = role_rows(sid, gov_id, centre)
    sources += [s for r in roles for s in r["source"].split(";")]
    notes: list[str] = []
    corroboration = None
    corroboration_value = None
    exclusion = None
    if pop is not None:
        src = str(u.pop_source)
        if src.startswith("gastat-census2022-ta1-city5k"):
            pop_type, pop_source, pop_year, pop_status = "official", S_CITY, 2022, "verified"
            sources.append(S_CITY)
        elif src.startswith("worldpop"):
            pop_type, pop_source, pop_year, pop_status = (
                "grid",
                S_GRID,
                int(u.pop_year),
                "unverified",
            )
            sources.append(S_GRID)
        else:
            raise ValueError(f"{sid}: unexpected population source {src!r}")
    if u is not None and pd.notna(u.control_total_flag):
        notes.append(f"R1a control-total flag: {u.control_total_flag}")

    tag_10k = bool(pop is not None and pop >= TAG_10K)
    tag_5k = bool(pop is not None and pop >= TAG_5K)
    if pop_type == "grid" and tag_10k and not corroborates(pop, corroboration_value):
        # A-screen-031/032: a grid row passes the 10k test only with a second method (none run).
        tag_10k = False
        exclusion = GRID_UNCORROBORATED
        notes.append("grid figure >= 10,000 without a second method: tag_10k false (A-screen-031)")
    primary_checked = pop_type == "official"
    return {
        "name_ar": name_ar,
        "name_en": name_en,
        "region": REGION,
        "governorate": g["name_en"],
        "governorate_ar": g["name_ar"],
        "is_governorate_centre": centre,
        "osm_id": osm_id,
        "osm_type": osm_type,
        "lat": lat,
        "lon": lon,
        "population": pop,
        "pop_source": pop_source,
        "pop_year": pop_year,
        "pop_type": pop_type,
        "pop_source_status": pop_status,
        "primary_to_find": None,
        "pop_corroboration": corroboration,
        "pop_corroboration_value": corroboration_value,
        "tag_10k": tag_10k,
        "tag_5k": tag_5k,
        "dist_existing_km": None if u is None else _f(u.dist_existing_km),
        "road_min_existing": None if u is None else _f(u.road_min_existing),
        "nearest_existing": None if u is None else _s(u.nearest_existing),
        "dist_committed_km": None if u is None else _f(u.dist_committed_km),
        "road_min_committed": None if u is None else _f(u.road_min_committed),
        "nearest_committed": None if u is None else _s(u.nearest_committed).split(":")[0],
        "nearest_committed_station": None if u is None else _s(u.nearest_committed),
        "dist_metro_km": None if u is None else _f(u.dist_metro_city_km),
        "road_min_metro": None if u is None else _f(u.road_min_metro_city),
        "nearest_metro": None if u is None else _s(u.nearest_metro_city),
        "nearest_metro_tier": None if u is None else int(u.nearest_metro_tier),
        "economic_roles": roles,
        "terrain_class": "escarpment_mountain",
        "screened": True,
        "exclusion_reason": exclusion,
        "sources": sorted(set(sources + [S_TERRAIN])),
        "threshold_50k": None,
        "pilot_sample": None,
        "road_min_method": "osrm_table_mld_car (R1a skims, free flow, uncalibrated; S-al_baha-106)"
        if u is not None
        else "pending: centre not located",
        "dist_method": DIST_METHOD if u is not None else "pending: centre not located",
        "notes": _notes(notes, u, centre, primary_checked, name_en, sid),
        "fixture": False,
    }


def _km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km (haversine, R1a convention)."""
    r = 6371.0088
    p1, p2 = radians(lat1), radians(lat2)
    a = sin((p2 - p1) / 2) ** 2 + cos(p1) * cos(p2) * sin(radians(lon2 - lon1) / 2) ** 2
    return 2 * r * asin(sqrt(a))


def _f(v: Any) -> float | None:
    return None if v is None or pd.isna(v) else round(float(v), 2)


def _s(v: Any) -> str | None:
    return None if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)


def _notes(
    notes: list[str],
    u: pd.Series | None,
    centre: bool,
    primary_checked: bool,
    name_en: str,
    sid: str | None,
) -> str | None:
    out: list[str] = []
    if u is None:
        out.append(
            "governorate centre not located in the universe: lat/lon are the governorate polygon's "
            "representative point (A-al_baha-002, flagged); no population, no distances (pending)"
        )
    else:
        if centre:
            out.append("governorate centre (OSM seat, A-screen-011)")
        if primary_checked:
            out.append(f"population: GASTAT Census 2022 TA1 city>=5,000 primary export ({S_CITY})")
        if (
            pd.notna(u.population)
            and pd.notna(u.grid_population)
            and u.population != u.grid_population
        ):
            out.append(f"grid figure {int(u.grid_population)} not used (official figure governs)")
        if sid == "KSA-ST-01855":
            out.append(
                f"airport role (A-al_baha-003): King Saud bin Abdulaziz (ABT) is "
                f"{_km(*AIRPORT, u.lat, u.lon):.1f} km from this centre and "
                f"{_km(*AIRPORT, *BAHAH_CITY):.1f} km from Al-Bahah; "
                "R1a names Al-Bahah as nearest town"
            )
        if sid == "KSA-ST-00013":
            out.append(
                "MODON Al-Baha Industrial City: no position source; attached by name (unlocated)"
            )
        if sid == "KSA-ST-00581":
            out.append("OSM place=village as a governorate seat (kept as tagged)")
        if sid == "KSA-ST-01515":
            out.append(
                "centre conflict: OSM town vs Saudipedia Bidan / Wadi Al-Sadr (S-al_baha-113)"
            )
        if sid == "KSA-ST-03122":
            out.append("two OSM nodes; governorate node 6768458212 not used")
        if sid == "KSA-ST-07026":
            out.append(
                "OSM hamlet, grid only; English name is our transliteration (none in OSM or GASTAT)"
            )
        if pd.notna(u.population):
            out.append("committed distances go to unlocated proxy stations (A-al_baha-004)")
    out += notes
    return "; ".join(out) or None


def validate_dataframe(df: pd.DataFrame) -> None:
    from common.schemas import RegionRow, _plain

    for rec in df.to_dict(orient="records"):
        RegionRow.model_validate({k: _plain(v) for k, v in rec.items()})


def cross_check() -> dict[str, Any]:
    """Primary vs universe figures for Al-Bahah (conflict > 2 % logged; none expected)."""
    city = primary_city()
    checks = {
        "Albahah": ("KSA-ST-00013", 90515),
        "Alaqiq": ("KSA-ST-01855", 19269),
        "Almandaq": ("KSA-ST-01336", 8674),
        "Almukhwah": ("KSA-ST-00575", 26248),
        "Bani Hasan": ("KSA-ST-01515", 6344),
        "Biljurashi": ("KSA-ST-00566", 35985),
        "Qilwah": ("KSA-ST-03122", 13069),
    }
    out: dict[str, Any] = {}
    for name, (sid, pop) in checks.items():
        assert city[name] == pop, f"{name}: primary {city[name]} != expected {pop}"
        out[name] = {"settlement_id": sid, "primary": city[name]}
    gov = primary_governorates()
    gov_map = dict(zip(gov.governorate, gov.total.astype(int), strict=True))
    names = [
        "Al Aqiq",
        "Al Bahah",
        "Al Hajrah",
        "Al Mandaq",
        "Al Mukhwah",
        "Al Qara",
        "Bani Hasan",
        "Biljurashi",
        "Farat Ghamid Az Zinad",
        "Qilwah",
    ]
    gov_vals = {n: gov_map[n] for n in names}
    total = sum(gov_vals.values())
    assert total == REGION_TOTAL_2022, f"sum of 10 governorates {total} != {REGION_TOTAL_2022}"
    out["governorates_sum"] = total
    out["governorates"] = gov_vals
    return out


@app.callback()
def main() -> None:
    """Al-Baha R2 region register builder."""


@app.command()
def build(seed: int = typer.Option(1, "--seed", min=0)) -> None:
    """Write cities/ksa/regions/al_baha.parquet (+ CSV mirror) with the governorate-count header."""
    rng(seed)
    cc = cross_check()
    typer.echo(json.dumps({"primary_check": "ok", "governorates_sum": cc["governorates_sum"]}))
    univ = pd.read_parquet(UNIVERSE)
    univ = univ[univ.region == REGION].copy()
    govs = governorate_info()
    assert len(govs) == GOVERNORATES_GASTAT, f"{len(govs)} polygons, expected {GOVERNORATES_GASTAT}"
    rows = build_rows(univ, govs)
    df = pd.DataFrame(rows)
    # Pilot-only flags stay null in the R2 register (region-sweep skill).
    df["threshold_50k"] = None
    df["pilot_sample"] = None
    for col in ("osm_id", "population", "pop_year", "nearest_metro_tier"):
        df[col] = df[col].astype("Int64")
    validate_dataframe(df)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    meta = {
        b"governorates_gastat": str(GOVERNORATES_GASTAT).encode(),
        b"governorates_listed": str(df.governorate.nunique()).encode(),
    }
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
    pq.write_table(table, OUT)

    mirror = df.copy()
    mirror["economic_roles"] = mirror.economic_roles.map(
        lambda rs: "; ".join(f"{r['role']} [{r['source']}]" for r in rs)
    )
    mirror["sources"] = mirror.sources.map(lambda s: ";".join(s))
    mirror.to_csv(OUT.with_suffix(".csv"), index=False)
    typer.echo(
        json.dumps(
            {
                "rows": len(df),
                "governorates": int(df.governorate.nunique()),
                "centres": int(df.is_governorate_centre.sum()),
                "tag_10k": int(df.tag_10k.sum()),
                "tag_5k": int(df.tag_5k.sum()),
            }
        )
    )


if __name__ == "__main__":
    app()
