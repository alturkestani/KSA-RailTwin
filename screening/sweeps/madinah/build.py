"""Region sweep for Al-Madinah (slug `madinah`), R2 input (REGION_MADINAH, 31 Oct 2026).

Builds `cities/ksa/regions/madinah.parquet` (+ `.csv`) from the R1a settlement universe
(`cities/ksa/zones/settlements.parquet`, which already carries the GASTAT primary TA1 city figures,
the WorldPop grid gap-fill, the R1a OSRM road skims and the nearest existing / committed / metro
distances) and the R1a economic nodes. Rows: the governorate centres (one per GASTAT governorate of
the region) and every settlement at or above 5,000 (`tag_5k`, the sensitivity set). Settlements
below 5,000 stay in the universe and are counted, not written (see docs/regions/madinah.md).

Run from the worktree root:

    .venv/bin/python -m screening.sweeps.madinah.build --seed 1

Deterministic: no sampling; `--seed` is recorded for rule 10.
"""
# ruff: noqa: E501  (source and reason strings are kept whole for the register)

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

from common.runmeta import rng
from common.schemas import TAG_5K, TAG_10K, RegionRow

app = typer.Typer(add_completion=False, help="Madinah region sweep (R2).")

REGION = "madinah"
UNIVERSE = Path("cities/ksa/zones/settlements.parquet")
ECON = Path("cities/ksa/zones/economic_nodes.parquet")
GOVS = Path("cities/ksa/zones/governorates.geojson")
OUT = Path("cities/ksa/regions")
GOVERNORATES_GASTAT = 9  # S-073: 9 governorate rows for Al-Madinah (capital row included)

# Population sources (main index ids). The R1a universe pop_source strings map onto these.
SRC_PRIMARY = "S-cp2-gastat-008"  # GASTAT Census 2022 TA1 primary, cities 5,000+
SRC_GRID = "S-r1a-506"  # WorldPop 2020 100 m constrained, UN-adjusted
SRC_OSM_TAG = "S-madinah-016"  # OSM place=* population tag (this sweep; ODbL)
SRC_OSM_PLACE = "S-madinah-005"  # OSM place nodes, ids and coordinates (pilot)

# Governorate centres: settlement_id in the R1a universe, chosen by name, node and population
CENTRES = {
    "KSA-ST-01532": "Madinah",  # node 4571693347 (Medina city)
    "KSA-ST-01439": "Yanbu",  # node 3148037089
    "KSA-ST-02693": "Al Ula",  # node 7700293159
    "KSA-ST-01387": "Badr",  # node 1237968680 (Badr Hunayn); pilot alternative: way 87175609
    "KSA-ST-00055": "Khaybar",  # node 546640970
    "KSA-ST-00605": "Al Hinakiyah",  # node 1236695024
    "KSA-ST-01365": "Al Mahd",  # node 1237964803 (Mahd adh Dhahab)
    "KSA-ST-01683": "Al Is",  # node 5813392174 (Al-'Aīṣ)
}

# Economic roles tied to a register row: (role, source). R1a economic nodes first; the pilot
# sources S-madinah-010/011 for Badr and Khaybar, which R1a does not carry.
ROLES: dict[str, list[tuple[str, str]]] = {
    "KSA-ST-01532": [
        ("airport", "S-cp1-100"),
        ("hajj_umrah", "S-r1a-214"),
        ("industrial_city", "S-r1a-204"),
        ("university", "S-r1a-221"),
    ],
    "KSA-ST-01439": [
        ("port", "S-r1a-208"),
        ("industrial_city", "S-r1a-202"),
        ("energy", "S-cp1-105"),
        ("airport", "S-cp1-100"),
        ("university", "S-r1a-221"),
    ],
    "KSA-ST-02693": [
        ("airport", "S-cp1-100"),
        ("giga_project", "S-r1a-227"),
        ("heritage", "S-r1a-205"),
    ],
    "KSA-ST-01387": [("heritage", "S-madinah-010"), ("tourism", "S-madinah-010")],
    "KSA-ST-00055": [
        ("heritage", "S-madinah-011"),
        ("tourism", "S-madinah-011"),
        ("agriculture", "S-madinah-011"),
    ],
    "KSA-ST-01365": [("mining", "S-r1a-237")],
}

# Labels for R1a ids (the register names the station or corridor, not the id alone)
EXISTING_LABEL = {
    "hhr:madinah": "Haramain HSR, Madinah station (R1a id hhr:madinah)",
    "hhr:kaec": "Haramain HSR, KAEC station (R1a id hhr:kaec)",
}
COMMITTED_PREFIX = "Saudi Landbridge, committed layer (R1a id {})"
METRO_LABEL = {
    "Madinah (tier 1)": "Madinah (tier 1, A-screen-013)",
    "Makkah (tier 1)": "Makkah (tier 1, A-screen-013)",
    "Tabuk (tier 2)": "Tabuk (tier 2, A-screen-013)",
    "Taif (tier 2)": "Taif (tier 2, A-screen-013)",
}
YANBU_NOTE = (
    "Pilot census place 331,916 (S-madinah-001) = this city 258,777 + Yanbu Industrial City "
    "73,139 (row 'Yanbaa As-Senayah' below): the primary table splits the two; no error"
)
STATIONS = Path("cities/ksa/lines/stations.geojson")
INDUSTRIAL_CITY = "Yanbaa As-Senayah"  # GASTAT primary 2022 name for Yanbu Industrial City


def _clean(s: object) -> str | None:
    """Backtick transliteration marks to apostrophes; missing -> None."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return None
    return str(s).replace("`", "'")


def _num(x: object) -> float | None:
    return None if x is None or pd.isna(x) else float(x)


def _pop_fields(r: pd.Series) -> dict[str, Any]:
    """Population fields by precedence official > derived > grid (A-screen-031)."""
    empty: dict[str, Any] = {
        "population": None,
        "pop_source": None,
        "pop_year": None,
        "pop_type": None,
        "pop_source_status": None,
        "primary_to_find": None,
    }
    if pd.isna(r.population):
        return empty
    src = str(r.pop_source)
    pop = int(r.population)
    if src.startswith("gastat-census2022-ta1-city5k"):
        return empty | {
            "population": pop,
            "pop_source": SRC_PRIMARY,
            "pop_year": 2022,
            "pop_type": "official",
            "pop_source_status": "verified",
        }
    gap = "GASTAT Census 2022 locality table (settlement not in the primary 5,000+ city file)"
    if src.startswith("worldpop"):
        return empty | {
            "population": pop,
            "pop_source": SRC_GRID,
            "pop_year": 2020,
            "pop_type": "grid",
            "pop_source_status": "unverified",
            "primary_to_find": gap,
        }
    if src.startswith("osm-"):  # the tag's own year (Al Mohaffar: 2010), not the extract date
        return empty | {
            "population": pop,
            "pop_source": SRC_OSM_TAG,
            "pop_year": int(r.osm_population_year),
            "pop_type": "derived",
            "pop_source_status": "unverified",
            "primary_to_find": gap,
        }
    raise ValueError(f"unknown population source {src!r} for {r.settlement_id}")


def _row(r: pd.Series, centre: bool, roles: list[tuple[str, str]], note: str | None) -> dict:
    pop = _pop_fields(r)
    population = pop["population"]
    tag_10k = population is not None and population >= TAG_10K
    exclusion = None
    if tag_10k and pop["pop_type"] == "grid":  # A-screen-031/032: no second method run
        tag_10k = False
        exclusion = "grid-only population, uncorroborated"
    parts = [f"R1a universe {r.settlement_id} ({r.place})"]
    if pop["pop_type"] == "grid":
        parts.append(
            f"WorldPop grid {int(r.grid_population)} (S-r1a-506); no second method run "
            "(pop_corroboration null)"
        )
    if pop["pop_type"] == "derived":
        parts.append(
            "population from an OSM place tag, not GASTAT; the universe label "
            "'derived_corroborated' is not used because no corroboration is recorded"
        )
    if note:
        parts.append(note)
    name_en, name_ar = _clean(r.name_en), _clean(r.name_ar)
    if name_en is None and name_ar is None:  # unnamed in OSM: label by node, never invent a name
        name_en = name_ar = f"(unnamed OSM {r.osm_type} {int(r.osm_id)})"
        parts.append("unnamed in OSM and in the R1a universe; labelled by OSM id")
    if not roles:
        parts.append("economic roles not assessed beyond the R1a economic nodes")
    sources = {SRC_OSM_PLACE, pop["pop_source"], *(s for _, s in roles)} - {None}
    return {
        "name_ar": name_ar,
        "name_en": name_en,
        "region": REGION,
        "governorate": r.governorate,
        "governorate_ar": r.governorate_ar,
        "is_governorate_centre": centre,
        "osm_id": int(r.osm_id),
        "osm_type": r.osm_type,
        "lat": float(r.lat),
        "lon": float(r.lon),
        **pop,
        "tag_10k": tag_10k,
        "tag_5k": population is not None and population >= TAG_5K,
        "dist_existing_km": _num(r.dist_existing_km),
        "road_min_existing": _num(r.road_min_existing),
        "nearest_existing": EXISTING_LABEL.get(r.nearest_existing, r.nearest_existing),
        "dist_committed_km": _num(r.dist_committed_km),
        "road_min_committed": _num(r.road_min_committed),
        "nearest_committed": COMMITTED_PREFIX.format(r.nearest_committed),
        "nearest_committed_station": None,
        "dist_metro_km": _num(r.dist_metro_city_km),
        "road_min_metro": _num(r.road_min_metro_city),
        "nearest_metro": METRO_LABEL.get(r.nearest_metro_city, r.nearest_metro_city),
        "nearest_metro_tier": int(r.nearest_metro_tier),
        "economic_roles": [{"role": a, "source": b} for a, b in roles],
        "terrain_class": None,
        "screened": True,
        "exclusion_reason": exclusion,
        "sources": sorted(sources),
        "threshold_50k": None,
        "pilot_sample": None,
        "road_min_method": "osrm_table_mld_car (R1a skims)",
        "dist_method": "haversine",
        "notes": ". ".join(parts),
    }


def _gov_centroid(name: str) -> tuple[float, float]:
    """Mean vertex of the OSM governorate polygon `name` (outer rings; WGS84). Not a settlement."""
    g = json.loads(GOVS.read_text(encoding="utf-8"))
    feats = [f for f in g["features"] if f["properties"].get("name_en") == name]
    if len(feats) != 1:
        raise ValueError(f"governorate polygon {name!r}: {len(feats)} matches on name_en")
    geom = feats[0]["geometry"]
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    pts = [tuple(p) for poly in polys for p in poly[0]]
    lon = sum(p[0] for p in pts) / len(pts)
    lat = sum(p[1] for p in pts) / len(pts)
    return round(lat, 6), round(lon, 6)


def _fara_row(gov_ar: str) -> dict:
    lat, lon = _gov_centroid("Wadi Al Fara")
    return {
        "name_ar": "وادي الفرع",
        "name_en": "Wadi al-Fara' (governorate seat not identified)",
        "region": REGION,
        "governorate": "Wadi Al Fara",
        "governorate_ar": gov_ar,
        "is_governorate_centre": True,
        "osm_id": None,
        "osm_type": None,
        "lat": lat,
        "lon": lon,
        "population": None,
        "pop_source": None,
        "pop_year": None,
        "pop_type": None,
        "pop_source_status": None,
        "primary_to_find": "governorate seat name and its GASTAT locality population",
        "tag_10k": False,
        "tag_5k": False,
        "dist_existing_km": None,
        "road_min_existing": None,
        "nearest_existing": None,
        "dist_committed_km": None,
        "road_min_committed": None,
        "nearest_committed": None,
        "nearest_committed_station": None,
        "dist_metro_km": None,
        "road_min_metro": None,
        "nearest_metro": None,
        "nearest_metro_tier": None,
        "economic_roles": [],
        "terrain_class": None,
        "screened": False,
        "exclusion_reason": (
            "governorate seat not identified in the sources reached (S-madinah-015); no "
            "population and no distances; lat/lon = governorate polygon centroid, not a settlement"
        ),
        "sources": ["S-073", "S-madinah-015"],
        "threshold_50k": None,
        "pilot_sample": None,
        "road_min_method": None,
        "dist_method": None,
        "notes": (
            "Seven subdivision centres are named in S-madinah-015 (Al-Akhal, Abu Dhaba', "
            "Al-Hamnah, Al-Hindiyah, Umm al-Burak, Suri, Mughaysil); none is identified as the "
            "seat, so none is chosen here"
        ),
    }


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance, R = 6371.0088 km (A-r1a-001 / pilot A-screen-pilot-001)."""
    import math

    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * 6371.0088 * math.asin(math.sqrt(a)), 2)


def _yanbu_industrial_row(univ: pd.DataFrame, econ: pd.DataFrame) -> dict:
    """Yanbu Industrial City: a GASTAT primary city (73,139) that the R1a universe does not hold.
    Position = the R1a economic node `rcjy-yanbu-industrial` (located); no place node, so no
    osm_id. Distances are straight-line to the nearest existing station (HHR) and to the Madinah
    metro node; no committed distance and no road skim (not computed for this point)."""
    node = econ.loc[econ.node_id == "rcjy-yanbu-industrial"].iloc[0]
    lat, lon = float(node.lat), float(node.lon)
    st = json.loads(STATIONS.read_text(encoding="utf-8"))
    existing = []
    for f in st["features"]:
        pr = f["properties"]
        if pr.get("layer") != "existing" or f["geometry"] is None:
            continue
        slon, slat = f["geometry"]["coordinates"][:2]
        existing.append((_haversine_km(lat, lon, slat, slon), pr["station_uid"]))
    d_ex, uid = min(existing)
    med = univ.loc[univ.settlement_id == "KSA-ST-01532"].iloc[0]
    d_metro = _haversine_km(lat, lon, float(med.lat), float(med.lon))
    return {
        "name_ar": node.name_ar,
        "name_en": "Yanbu' al-Sina'iyah (Yanbu Industrial City)",
        "region": REGION,
        "governorate": "Yanbu",
        "governorate_ar": "ينبع",
        "is_governorate_centre": False,
        "osm_id": None,
        "osm_type": None,
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "population": 73139,
        "pop_source": SRC_PRIMARY,
        "pop_year": 2022,
        "pop_type": "official",
        "pop_source_status": "verified",
        "primary_to_find": None,
        "tag_10k": True,
        "tag_5k": True,
        "dist_existing_km": d_ex,
        "road_min_existing": None,
        "nearest_existing": EXISTING_LABEL.get(uid, uid),
        "dist_committed_km": None,
        "road_min_committed": None,
        "nearest_committed": None,
        "nearest_committed_station": None,
        "dist_metro_km": d_metro,
        "road_min_metro": None,
        "nearest_metro": METRO_LABEL["Madinah (tier 1)"],
        "nearest_metro_tier": 1,
        "economic_roles": [{"role": "industrial_city", "source": "S-r1a-202"}],
        "terrain_class": None,
        "screened": True,
        "exclusion_reason": None,
        "sources": sorted({SRC_PRIMARY, "S-r1a-202", SRC_OSM_PLACE}),
        "threshold_50k": None,
        "pilot_sample": None,
        "road_min_method": "not computed (point not in the R1a universe; no skim)",
        "dist_method": "haversine",
        "notes": (
            "Not in the R1a universe (unmatched in the CP2 primary match): added from the GASTAT "
            "primary table 'Yanbaa As-Senayah' 73,139 (S-cp2-gastat-008). Coordinates = R1a "
            "economic node rcjy-yanbu-industrial (S-r1a-202; located, node not a place). "
            "Committed distance not computed. " + YANBU_NOTE
        ),
    }


def _validate_and_write(df: pd.DataFrame) -> None:
    for rec in df.to_dict(orient="records"):
        RegionRow.model_validate({k: _plain(v) for k, v in rec.items()})  # raises on violation
    n_gov = int(df.governorate.nunique())
    print(f"rows {len(df)}; governorates in rows {n_gov}; tag_10k {int(df.tag_10k.sum())}; "
          f"tag_5k {int(df.tag_5k.sum())}")  # fmt: skip
    OUT.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    meta = dict(table.schema.metadata or {})
    meta[b"governorates_gastat"] = str(GOVERNORATES_GASTAT).encode()
    meta[b"governorates_listed"] = str(n_gov).encode()
    pq.write_table(table.replace_schema_metadata(meta), OUT / f"{REGION}.parquet")
    csv = df.copy()
    for c in ("economic_roles", "sources"):
        csv[c] = csv[c].apply(lambda v: ";".join(
            f"{x['role']}:{x['source']}" if isinstance(x, dict) else str(x) for x in v
        ))  # fmt: skip
    csv.to_csv(OUT / f"{REGION}.csv", index=False)


def _plain(v: Any) -> Any:
    """numpy scalars and NaN to Python values the pydantic model accepts."""
    if isinstance(v, float) and pd.isna(v):
        return None
    if hasattr(v, "item") and not isinstance(v, (list, dict, str)):
        return v.item()
    return v


@app.command()
def build(seed: int = typer.Option(1, "--seed", min=0)) -> None:
    """Write the Madinah register (Parquet + CSV), validated against RegionRow."""
    rng(seed)
    univ = pd.read_parquet(UNIVERSE)
    m = univ[univ.region == REGION]
    econ = pd.read_parquet(ECON)
    print(f"universe rows {len(m)}; economic nodes {int((econ.region == REGION).sum())}")
    chosen = m[m.settlement_id.isin(CENTRES) | m.population.ge(TAG_5K)]
    rows = []
    for _, r in chosen.iterrows():
        note = YANBU_NOTE if r.settlement_id == "KSA-ST-01439" else None
        rows.append(_row(r, r.settlement_id in CENTRES, ROLES.get(r.settlement_id, []), note))
    rows.append(_yanbu_industrial_row(m, econ))
    gov_ar = m.loc[m.governorate == "Wadi Al Fara", "governorate_ar"].dropna()
    rows.append(_fara_row(gov_ar.iloc[0] if len(gov_ar) else "وادي الفرع"))
    _validate_and_write(pd.DataFrame(rows))


if __name__ == "__main__":
    app()
