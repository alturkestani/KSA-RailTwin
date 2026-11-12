"""REGION_AL_JOUF (R2): build the Al-Jouf region register from the R1a settlement universe.

Inputs (read only): `cities/ksa/zones/settlements.parquet` (R1a universe, GASTAT primary applied),
`cities/ksa/zones/economic_nodes.parquet`, `cities/ksa/regions/pilot-al_jouf.csv` (record-only
GEO_VERIFY notes). Outputs: `cities/ksa/regions/al_jouf.parquet` and `.csv`. No random draws.

uv run python -m screening.sweeps.al_jouf.build
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

ROOT = Path(__file__).resolve().parents[3]
UNIVERSE = ROOT / "cities/ksa/zones/settlements.parquet"
ECON = ROOT / "cities/ksa/zones/economic_nodes.parquet"
PILOT = ROOT / "cities/ksa/regions/archive/pilot/pilot-al_jouf.csv"
OUT_PQ = ROOT / "cities/ksa/regions/al_jouf.parquet"
OUT_CSV = ROOT / "cities/ksa/regions/al_jouf.csv"

REGION = "al_jouf"
GASTAT_COUNT = 4  # the four Al-Jouf governorates in the GASTAT primary export (S-cp2-gastat-007)
PRIMARY_CITY = (
    "S-cp2-gastat-008"  # GASTAT Census 2022 TA1 primary, cities of 5,000+ (official, verified)
)
WORLDPOP = "S-r1a-505"  # WorldPop 2020 100 m constrained (grid)
OSM = "S-r1a-210"  # OSM GCC extract element ids and coordinates
ROAD = "S-r1a-809"  # OSRM 26.10.0 MLD car skims (free flow)
LINE = "S-018"  # SAR North passenger line places
TAG_10K, TAG_5K = 10_000, 5_000
CORROB_PRIMARY_TO_FIND = (
    "GASTAT Census 2022 locality table (portal.saudicensus.sa unreachable; the primary city table "
    "S-cp2-gastat-008 lists only places of 5,000 or more)"
)
# English spellings from the GASTAT primary city table where R1a carries only the Arabic name
NAME_EN = {"ميقوع": "Meegowa", "أبو عجرم": "Abu Ajram"}
GOVERNORATE_CENTRES = {"KSA-ST-00854", "KSA-ST-00868", "KSA-ST-00871", "KSA-ST-00851"}

# Economic roles per settlement (role, source): R1a economic_nodes and the pilot sources.
ROLES: dict[str, list[tuple[str, str]]] = {
    "KSA-ST-00854": [  # Sakaka
        ("administrative", "S-al_jouf-008"),
        ("airport", "S-cp1-100;S-r1a-210"),
        ("university", "S-r1a-221;S-r1a-222;S-r1a-210"),
        ("industrial_city", "S-r1a-204"),
    ],
    "KSA-ST-00868": [("administrative", "S-al_jouf-002"), ("airport", "S-cp1-100;S-r1a-210")],
    "KSA-ST-00871": [("administrative", "S-al_jouf-002")],
    "KSA-ST-00851": [
        ("administrative", "S-al_jouf-002"),
        ("heritage", "S-al_jouf-009"),
        ("tourism", "S-al_jouf-009"),
    ],
}


def _none(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if v is pd.NA or v is pd.NaT:
        return None
    if isinstance(v, np.generic):
        return v.item()
    return v


def _f(v: Any) -> float | None:
    v = _none(v)
    return None if v is None else float(v)


def _pilot_geo() -> dict[int, str]:
    """Record-only GEO_VERIFY notes from the pilot register, keyed by OSM id (not applied)."""
    out: dict[int, str] = {}
    if not PILOT.exists():
        return out
    p = pd.read_csv(PILOT)
    for _, r in p.iterrows():
        note = str(r.get("notes", "") or "")
        m = re.search(r"derived estimate central ([\d,]+) \(band ([\d,]+)–([\d,]+)", note)
        g = re.search(r"\[(geo-est-[0-9a-f]+)\]", str(r.get("primary_to_find", "") or "") + note)
        if m and g and not pd.isna(r.get("osm_id")):
            out[int(r["osm_id"])] = (
                f"pilot GEO_VERIFY 31 Oct 2026, record-only: central {m.group(1)} "
                f"(band {m.group(2)}–{m.group(3)}) [{g.group(1)}]"
            )
    return out


def _population(r: pd.Series) -> dict[str, Any]:
    """Population fields under the CP2 rule: GASTAT primary first, then grid (gated)."""
    src = str(_none(r.pop_source) or "")
    notes: list[str] = []
    if src.startswith("gastat-census2022-ta1-city5k"):
        pop = int(r.population)
        out = dict(
            population=pop,
            pop_source=PRIMARY_CITY,
            pop_year=2022,
            pop_type="official",
            pop_source_status="verified",
            primary_to_find=None,
            pop_corroboration=None,
            pop_corroboration_value=None,
        )
        return out | {"tag_10k": pop >= TAG_10K, "tag_5k": pop >= TAG_5K, "notes": notes}
    # OSM place tags are not 2022 figures: the dated 2010 ones equal the Census 2010 list
    # (S-cp2-gastat-005); the undated ones cannot be checked. Neither is used (A-al_jouf-004).
    osm_pop = _none(r.osm_population)
    if osm_pop is not None:
        year = _none(r.osm_population_year)
        when = f"year {int(year)}" if year is not None else "year not recorded"
        notes.append(
            f"OSM population tag {int(osm_pop)} ({when}) not used as a 2022 figure (A-al_jouf-004)"
        )
    grid = _none(r.grid_population)
    pop = int(grid) if grid is not None else 0
    out = dict(
        population=pop,
        pop_source=WORLDPOP,
        pop_year=2020,
        pop_type="grid",
        pop_source_status="unverified",
        primary_to_find=CORROB_PRIMARY_TO_FIND,
        pop_corroboration=None,  # no second method was run for this row (A-screen-031/032)
        pop_corroboration_value=None,
        tag_10k=False,  # grid-only and uncorroborated: never passes the 10k test here
        tag_5k=pop >= TAG_5K,  # the 5k tag is not gated
    )
    notes.append(
        "not in the GASTAT 2022 city table (S-cp2-gastat-008, 5,000+): presumed 2022 below "
        "5,000 (A-al_jouf-003); grid figure shown, not a GASTAT value"
    )
    return out | {"notes": notes}


def _metro_name(v: Any) -> str:
    """R1a writes the metro as 'Tabuk (tier 2)'; the tier is stored in its own column."""
    return re.sub(r"\s*\(tier \d\)$", "", str(v))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def build_rows(univ: pd.DataFrame, econ: pd.DataFrame, geo: dict[int, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, r in univ.sort_values("population", ascending=False, na_position="last").iterrows():
        sid = r.settlement_id
        pop = _population(r)
        roles = [{"role": a, "source": b} for a, b in ROLES.get(sid, [])]
        notes: list[str] = list(pop.pop("notes"))
        if sid in GOVERNORATE_CENTRES:
            notes.insert(0, "governorate centre")
        if sid == "KSA-ST-00871":
            notes.append(
                "no economic role sourced (border_crossing not recorded: no source in the repo)"
            )
        if sid == "KSA-ST-01713":
            notes.append("GASTAT city table name 'Meegowa' (= Miqua'); OSM name is Arabic only")
        if sid == "KSA-ST-00869":
            notes.append(
                "OSM node 1236744849 'Al Hadithah'; census name Al-Hadithah al-Qadimah per "
                "S-al_jouf-002 (Needs Opus judgement: also the SAR North terminus 'Al Haditha' "
                "in S-018)"
            )
        if str(_none(r.control_total_flag) or "") and sid not in GOVERNORATE_CENTRES:
            notes.append(f"R1a control flag: {r.control_total_flag}")
        if str(_none(r.exclusion_reason) or "").startswith("inside a matched city"):
            notes.append("R1a flag: inside a matched city's radius (possible double counting)")
        if _none(r.osm_id) is not None and int(r.osm_id) in geo:
            notes.append(geo[int(r.osm_id)])
        notes.append("terrain not assessed (A-al_jouf-002)")
        # Screening: no sourced role and below 5,000 is excluded (row kept, reason given).
        # A grid-only row at or above 10,000 stays screened, with the uncorroborated reason.
        screened = True
        exclusion = None
        if not pop["tag_5k"] and not roles and sid not in GOVERNORATE_CENTRES:
            screened = False
            exclusion = "below 5,000 and no sourced economic role"
        elif pop["pop_type"] == "grid" and pop["population"] >= TAG_10K:
            exclusion = "grid-only population, uncorroborated"
        road_existing = _f(r.road_min_existing)
        road_committed = _f(r.road_min_committed)
        road_metro = _f(r.road_min_metro_city)
        sources = [PRIMARY_CITY if pop["pop_type"] == "official" else WORLDPOP, OSM, LINE, ROAD]
        sources += sorted({s for _, b in ROLES.get(sid, []) for s in b.split(";")}, key=str)
        row = dict(
            name_ar=str(r.name_ar),
            name_en=NAME_EN.get(str(r.name_en), str(r.name_en)),
            region=REGION,
            governorate=str(r.governorate),
            governorate_ar=str(_none(r.governorate_ar) or ""),
            is_governorate_centre=sid in GOVERNORATE_CENTRES,
            osm_id=int(r.osm_id) if _none(r.osm_id) is not None else None,
            osm_type=str(r.osm_type),
            lat=float(r.lat),
            lon=float(r.lon),
            population=pop["population"],
            pop_source=pop["pop_source"],
            pop_year=pop["pop_year"],
            pop_type=pop["pop_type"],
            pop_source_status=pop["pop_source_status"],
            primary_to_find=pop["primary_to_find"],
            pop_corroboration=pop["pop_corroboration"],
            pop_corroboration_value=pop["pop_corroboration_value"],
            tag_10k=bool(pop["tag_10k"]),
            tag_5k=bool(pop["tag_5k"]),
            dist_existing_km=_f(r.dist_existing_km),
            road_min_existing=road_existing,
            nearest_existing=str(_none(r.nearest_existing) or "") or None,
            dist_committed_km=_f(r.dist_committed_km),
            road_min_committed=road_committed,
            nearest_committed=str(_none(r.nearest_committed) or "") or None,
            nearest_committed_station=str(_none(r.road_target_committed) or "") or None,
            dist_metro_km=_f(r.dist_metro_city_km),
            road_min_metro=road_metro,
            nearest_metro=(
                f"{_metro_name(r.nearest_metro_city)} "
                f"(tier {int(r.nearest_metro_tier)}, A-screen-013)"
                if _none(r.nearest_metro_city)
                else None
            ),
            economic_roles=roles,
            terrain_class=None,
            screened=screened,
            exclusion_reason=exclusion,
            sources=sources,
            fixture=False,
            threshold_50k=None,
            pilot_sample=None,
            nearest_metro_tier=int(r.nearest_metro_tier) if _none(r.nearest_metro_tier) else None,
            road_min_method=(
                "osrm_table_mld_car (R1a skim, S-r1a-809; free flow, uncalibrated)"
                if road_existing is not None
                else "pending skims"
            ),
            dist_method="haversine to nearest existing station (R1a; checked: Sakaka 51.03 km)",
            notes=" | ".join(notes) if notes else None,
        )
        rows.append(row)
    return rows


SCHEMA = pa.schema(
    [
        ("name_ar", pa.string()),
        ("name_en", pa.string()),
        ("region", pa.string()),
        ("governorate", pa.string()),
        ("governorate_ar", pa.string()),
        ("is_governorate_centre", pa.bool_()),
        ("osm_id", pa.int64()),
        ("osm_type", pa.string()),
        ("lat", pa.float64()),
        ("lon", pa.float64()),
        ("population", pa.int64()),
        ("pop_source", pa.string()),
        ("pop_year", pa.int64()),
        ("pop_type", pa.string()),
        ("pop_source_status", pa.string()),
        ("primary_to_find", pa.string()),
        ("pop_corroboration", pa.string()),
        ("pop_corroboration_value", pa.float64()),
        ("tag_10k", pa.bool_()),
        ("tag_5k", pa.bool_()),
        ("dist_existing_km", pa.float64()),
        ("road_min_existing", pa.float64()),
        ("nearest_existing", pa.string()),
        ("dist_committed_km", pa.float64()),
        ("road_min_committed", pa.float64()),
        ("nearest_committed", pa.string()),
        ("nearest_committed_station", pa.string()),
        ("dist_metro_km", pa.float64()),
        ("road_min_metro", pa.float64()),
        ("nearest_metro", pa.string()),
        (
            "economic_roles",
            pa.list_(pa.struct([("role", pa.string()), ("source", pa.string())])),
        ),
        ("terrain_class", pa.string()),
        ("screened", pa.bool_()),
        ("exclusion_reason", pa.string()),
        ("sources", pa.list_(pa.string())),
        ("fixture", pa.bool_()),
        ("threshold_50k", pa.bool_()),
        ("pilot_sample", pa.bool_()),
        ("nearest_metro_tier", pa.int64()),
        ("road_min_method", pa.string()),
        ("dist_method", pa.string()),
        ("notes", pa.string()),
    ]
)


def write(rows: list[dict[str, Any]]) -> None:
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    table = table.replace_schema_metadata(
        {
            "governorates_gastat": str(GASTAT_COUNT),
            "governorates_listed": str(GASTAT_COUNT),
        }
    )
    OUT_PQ.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT_PQ)
    flat = pd.DataFrame(rows)
    flat["economic_roles"] = flat["economic_roles"].map(json.dumps)
    flat["sources"] = flat["sources"].map(lambda s: ";".join(s))
    flat.to_csv(OUT_CSV, index=False)


app = typer.Typer(add_completion=False, help=__doc__)


@app.callback()
def main() -> None:
    """Al-Jouf region register (REGION_AL_JOUF)."""


@app.command()
def build() -> None:
    """Write cities/ksa/regions/al_jouf.parquet and .csv from the R1a universe."""
    univ = pd.read_parquet(UNIVERSE)
    univ = univ[univ.region == REGION].copy()
    econ = pd.read_parquet(ECON)
    rows = build_rows(univ, econ, _pilot_geo())
    write(rows)
    n10 = sum(r["tag_10k"] for r in rows)
    n5 = sum(r["tag_5k"] for r in rows)
    centres = sum(r["is_governorate_centre"] for r in rows)
    typer.echo(f"rows={len(rows)} tag_10k={n10} tag_5k={n5} gov_centres={centres}")


if __name__ == "__main__":
    app()
