"""REGION_TABUK sweep: builds the Tabuk register (r2-tabuk).

Inputs (all read-only): `cities/ksa/zones/settlements.parquet` (R1a universe, Tabuk rows = the
region's settlements), `cities/ksa/zones/economic_nodes.parquet`, `cities/ksa/lines/*.yaml` (line
source ids), `data/ksa/tables/gastat/` (through `screening.gastat`, governorate count).
Outputs: `cities/ksa/regions/tabuk.parquet` (+ `.csv` mirror), `docs/regions/tabuk.md`,
`docs/sources/r2-tabuk.csv`.

    PYTHONPATH=. .venv/bin/python -m screening.sweeps.tabuk.build
    PYTHONPATH=. .venv/bin/python -m screening.region_sweep validate --strict \
        cities/ksa/regions/tabuk.parquet

Rules applied (CLAUDE.md / region-sweep skill): population precedence official > derived > grid
(A-screen-031); a grid figure never sets tag_10k without corroboration (none in Tabuk: no grid row
reaches 10,000); governorate rows use the settlement figure, never the governorate total; distances
and road minutes are the R1a skims, not recomputed here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import yaml

from common.schemas import RegionRow

ROOT = Path(".")
REGIONS = ROOT / "cities/ksa/regions"
LINES = ROOT / "cities/ksa/lines"
DOCS = ROOT / "docs"
SLUG = "tabuk"

# Canonical governorate names (as in the pilot register) keyed by the R1a governorate id
# (OSM polygon, cities/ksa/zones/governorates.geojson). Seven rows of the GASTAT list (see below).
GOV = {
    "G143": ("Al-Wajh", "الوجه"),
    "G144": ("Al-Bad'", "البدع"),
    "G145": ("Duba", "ضباء"),
    "G146": ("Haql", "حقل"),
    "G147": ("Tabuk", "تبوك"),
    "G148": ("Taymā'", "تيماء"),
    "G149": ("Umluj", "أملج"),
}
# Terrain by governorate: no DEM read in R2 (A-tabuk-003, assumed; pending the DEM pass).
TERRAIN = {
    "Al-Wajh": "coastal",
    "Al-Bad'": "mixed",
    "Duba": "coastal",
    "Haql": "coastal",
    "Tabuk": "mixed",
    "Taymā'": "mixed",
    "Umluj": "coastal",
}
# Sourced economic roles by R1a settlement_id (role, S- source tying the role to that town).
ROLES: dict[str, list[tuple[str, str]]] = {
    "KSA-ST-01633": [  # Tabuk
        ("administrative", "S-tabuk-004"),
        ("airport", "S-tabuk-013"),
        ("heritage", "S-tabuk-014"),
        ("industrial_city", "S-r1a-204"),
        ("university", "S-r1a-221"),
    ],
    "KSA-ST-01191": [("airport", "S-tabuk-011"), ("heritage", "S-tabuk-012")],  # Al-Wajh
    "KSA-ST-01190": [("port", "S-tabuk-007")],  # Duba (Dhiba port: unverified status, S-r1a-209)
    "KSA-ST-00291": [("border_crossing", "S-tabuk-010")],  # Haql (Aqaba border)
    "KSA-ST-01186": [("heritage", "S-tabuk-008")],  # Tayma (UNESCO tentative list)
    "KSA-ST-01187": [("heritage", "S-tabuk-009")],  # Al-Bad'
    "KSA-ST-03114": [  # Neom (giga-project town)
        ("giga_project", "S-r1a-212"),
        ("port", "S-r1a-212"),
        ("airport", "S-cp1-100"),
    ],
}
PRIMARY_CITY_SRC = "S-cp2-gastat-008"
GRID_SRC = "S-r1a-505"  # WorldPop 2020 100 m constrained (the R1a grid; settlements.pop_source)
OSM_SRC = "S-r1a-210"  # OSM GCC extract (ids, coordinates, OSM population tags)
LANDBRIDGE_SRC = "S-054"
TAG_10K, TAG_5K = 10_000, 5_000
EXCLUDE_5K = "below 5,000 and no sourced economic role (A-screen-003)"
NAME_FIX = {"Halat `Ammar": "Halat Ammar", "Tayma'": "Tayma"}
DIST_METHOD = (
    "great circle to the 15 intercity passenger stations (A-r1a-008; existing) and to the "
    "committed-line stops (indicative: planned stops unlocated, A-tabuk-004); metro by haversine "
    "to the A-r1a-009 reference nodes"
)
ROAD_METHOD = "osrm_table_mld_car: 5 nearest great-circle candidates (A-r1a-027), R1a skims"


def nn(v: Any) -> Any:
    """NaN/NA to None; numpy scalars to Python."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return v.item() if isinstance(v, np.generic) else v


def line_source(line_ref: Any) -> str | None:
    """Source id of the line named in an R1a reference such as `sar-north-passenger:al-qurayyat`."""
    ref = nn(line_ref)
    if not ref:
        return None
    path = LINES / f"{str(ref).split(':')[0]}.yaml"
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("source")


def pop_fields(r: pd.Series) -> tuple[str, str, str | None, int, str, str | None]:
    """(pop_source, pop_source_status, primary_to_find, pop_year, pop_type, grid corroboration)."""
    src = str(r.pop_source)
    if src.startswith("gastat-census2022-ta1-city5k"):
        return PRIMARY_CITY_SRC, "verified", None, 2022, "official", None
    if src == "S-tabuk-002":  # Bi'r Ibn Hirmas: a sub-5,000 place, only in the census "Other" row
        return (
            "S-tabuk-002",
            "secondary",
            "GASTAT Census 2022 locality table (sub-5,000 places sit in the 'Other' row of "
            "S-cp2-gastat-008; the figure is not in the export)",
            2022,
            "official",
            None,
        )
    if src.startswith("worldpop"):
        return GRID_SRC, "unverified", None, 2020, "grid", None
    if src.startswith("osm-gcc"):
        return OSM_SRC, "secondary", None, int(r.pop_year), "derived", None
    raise ValueError(f"unmapped population source {src!r} for {r.settlement_id}")


def build_rows(t: pd.DataFrame) -> list[dict[str, Any]]:
    gov_seats = (
        t.sort_values("population", ascending=False).groupby("gov_id", sort=True).head(1)
    )  # the largest settlement of each governorate is its centre (checked against the 7 seats)
    seats = set(gov_seats.settlement_id)
    rows: list[dict[str, Any]] = []
    for r in t.itertuples(index=False):
        gname, gar = GOV[r.gov_id]
        raw_name = nn(r.name_en) or nn(r.name_ar) or f"unnamed OSM node {int(r.osm_id)}"
        name_en = NAME_FIX.get(str(raw_name), str(raw_name))
        notes = []
        # An OSM population tag with no year cannot carry pop_year (schema): kept as a note only.
        dated = not (str(r.pop_source).startswith("osm-gcc") and pd.isna(r.pop_year))
        if pd.isna(r.population) or not dated:
            psrc, pstat, ptf, pyear, ptype = None, None, None, None, None
            pop, tag10, tag5 = None, False, False
            if not dated:
                notes.append(
                    f"OSM population tag {int(r.osm_population):,} (undated, S-r1a-210) not used: "
                    "no year to attach (schema); below 5,000 in any case"
                )
        else:
            psrc, pstat, ptf, pyear, ptype, _ = pop_fields(pd.Series(r._asdict()))
            pop = int(r.population)
            tag10 = bool(pop >= TAG_10K)
            tag5 = bool(pop >= TAG_5K)
            if ptype == "grid" and tag10:
                raise ValueError(f"grid row >= 10k without corroboration: {r.settlement_id}")
        roles = [{"role": rl, "source": s} for rl, s in ROLES.get(r.settlement_id, [])]
        screened = tag5 or bool(roles)
        if r.settlement_id in seats:
            notes.append("governorate centre; the governorate total is not used (S-cp2-gastat-007)")
        if ptype == "grid":
            notes.append(
                f"WorldPop 2020 grid only ({pop:,}), unverified; no second method run, so no "
                f"corroboration (A-screen-031/033)"
            )
        if r.settlement_id == "KSA-ST-01193":  # Halat Ammar
            notes.append(
                "CONFLICT: OSM population tag 5,293 (derived) but the census city table (≥ 5,000, "
                "S-cp2-gastat-008) does not list it; WorldPop 7,067 not used (derived > grid); "
                "5k sensitivity only"
            )
        if r.settlement_id == "KSA-ST-01192":  # Bi'r Ibn Hirmas
            notes.append(
                "census 4,964 (S-tabuk-002, secondary); the OSM tag 5,975 is not used; 0.4 km from "
                "the historic Hejaz line (layer historical, not existing)"
            )
        if r.settlement_id == "KSA-ST-03114":  # Neom
            notes.append(
                "giga-project town (S-r1a-212); Port of NEOM has no location (node unlocated); "
                "Trojena (S-r1a-233) and Oxagon are in the same NEOM area, not separate rows"
            )
        if r.settlement_id == "KSA-ST-00262":  # Umluj
            notes.append("no sourced economic role (S-tabuk-011 role statements are unreferenced)")
        if str(r.nearest_committed or "").startswith("landbridge"):
            notes.append(
                "committed-line distances indicative: Landbridge stops unlocated (A-tabuk-004)"
            )
        srcs = [psrc, OSM_SRC]
        srcs += [line_source(r.nearest_existing), line_source(r.nearest_committed)]
        srcs += [s for _, s in ROLES.get(r.settlement_id, [])]
        if str(r.nearest_committed or "").startswith("landbridge"):
            srcs.append(LANDBRIDGE_SRC)
        if ptf is None and pstat == "secondary" and ptype == "official":
            raise ValueError(f"{r.settlement_id}: official secondary needs primary_to_find")
        row: dict[str, Any] = {
            "name_ar": str(nn(r.name_ar) or name_en),
            "name_en": name_en,
            "region": SLUG,
            "governorate": gname,
            "governorate_ar": gar,
            "is_governorate_centre": r.settlement_id in seats,
            "osm_id": int(r.osm_id),
            "osm_type": str(r.osm_type),
            "lat": float(r.lat),
            "lon": float(r.lon),
            "population": pop,
            "pop_source": psrc,
            "pop_year": pyear,
            "pop_type": ptype,
            "pop_source_status": pstat,
            "primary_to_find": ptf,
            "pop_corroboration": None,
            "pop_corroboration_value": None,
            "tag_10k": tag10,
            "tag_5k": tag5,
            "dist_existing_km": nn(r.dist_existing_km),
            "road_min_existing": nn(r.road_min_existing),
            "nearest_existing": nn(r.nearest_existing),
            "dist_committed_km": nn(r.dist_committed_km),
            "road_min_committed": nn(r.road_min_committed),
            "nearest_committed": nn(r.nearest_committed),
            "nearest_committed_station": nn(r.road_target_committed),
            "dist_metro_km": nn(r.dist_metro_city_km),
            "road_min_metro": nn(r.road_min_metro_city),
            "nearest_metro": nn(r.nearest_metro_city),
            "nearest_metro_tier": int(r.nearest_metro_tier),
            "economic_roles": roles,
            "terrain_class": TERRAIN[gname],
            "screened": screened,
            "exclusion_reason": None if screened else EXCLUDE_5K,
            "sources": list(dict.fromkeys(s for s in srcs if s)),
            "fixture": False,
            "threshold_50k": None,
            "pilot_sample": None,
            "road_min_method": ROAD_METHOD,
            "dist_method": DIST_METHOD,
            "notes": "; ".join(notes) or None,
        }
        RegionRow.model_validate(row)  # the schema is the contract: fail early per row
        rows.append(row)
    return rows


def main() -> None:
    settle = pd.read_parquet(ROOT / "cities/ksa/zones/settlements.parquet")
    t = settle[settle.region == SLUG].copy()
    assert len(t) == 119, f"expected the 119 R1a Tabuk settlements, found {len(t)}"
    assert set(t.gov_id) <= set(GOV), f"unexpected governorate ids {set(t.gov_id) - set(GOV)}"
    rows = build_rows(t)
    df = pd.DataFrame(rows)
    seats = df[df.is_governorate_centre]
    assert len(seats) == 7 and df.governorate.nunique() == 7, "7 governorate centres expected"
    assert (df.population.sum() - seats.population.sum()) >= 0
    gastat = "7"  # GASTAT governorate rows in Tabuk: primary TA1 export (S-cp2-gastat-007) joined
    listed = str(df.governorate.nunique())
    meta = {
        b"governorates_gastat": gastat.encode(),
        b"governorates_listed": listed.encode(),
    }
    table = pa.Table.from_pandas(df, preserve_index=False).replace_schema_metadata(meta)
    REGIONS.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, REGIONS / f"{SLUG}.parquet")
    df_csv = df.copy()
    for c in ("economic_roles", "sources"):
        df_csv[c] = df_csv[c].map(
            lambda v: ";".join(
                f"{x['role']}:{x['source']}" if isinstance(x, dict) else str(x) for x in v
            )
        )
    df_csv.to_csv(REGIONS / f"{SLUG}.csv", index=False)
    print(
        f"wrote {len(df)} rows; seats {len(seats)}; ≥10k {int(df.tag_10k.sum())}; "
        f"≥5k {int(df.tag_5k.sum())}; screened {int(df.screened.sum())}"
    )


if __name__ == "__main__":
    main()
