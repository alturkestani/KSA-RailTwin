# ruff: noqa: E501
# Long prose and source strings, as in screening/pilot_builders.
"""REGION_HAIL: build the R2 Hail register (`region-sweep` skill, schema `RegionRow`).

Inputs, all registered: the R1a settlement universe (`cities/ksa/zones/settlements.parquet`, OSM place
nodes with the R1a population basis, OSRM road minutes, S-r1a-809), the R1a economic nodes
(`cities/ksa/zones/economic_nodes.parquet`), the GASTAT primary Census 2022 TA1 exports
(`data/ksa/tables/gastat/`, S-cp2-gastat-007 and -008) and the working governorate list
(`docs/gastat-regions.md`, S-073). Output: `cities/ksa/regions/hail.parquet` and `.csv`.

Population precedence: a GASTAT-relayed figure (S-hail-001, matched by Arabic name and governorate)
replaces a grid or OSM figure; the GASTAT primary figure and the R1a universe basis are used otherwise.

Selection (A-hail-001): every governorate centre of the region, plus every settlement with a resolved
population of at least 5,000. Rows below 5,000 that are not governorate centres are not written.

Run: uv run python -m screening.sweeps.hail.build_register
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

from common.schemas import RegionRow

ROOT = Path(__file__).resolve().parents[3]
SETTLEMENTS = ROOT / "cities/ksa/zones/settlements.parquet"
GOV_PRIMARY = ROOT / "data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx"
CITY_PRIMARY = ROOT / "data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx"
LINES = ROOT / "cities/ksa/lines"
OUT = ROOT / "cities/ksa/regions/hail.parquet"
RELAYED_HAIL = ROOT / "data/ksa/hail/citypop_hail_census2022.csv"  # S-hail-001
REGION = "hail"
THRESHOLD_5K = 5_000
REGION_TOTAL_S_HAIL_001 = 746_406  # S-hail-001 (relayed; region total by governorate sum)

# Governorate centres: settlement id in the R1a universe, EN spelling of docs/gastat-regions.md (S-073),
# GASTAT primary governorate-table name (S-cp2-gastat-007).
CENTRES: dict[str, tuple[str, str]] = {
    "KSA-ST-00041": ("Ḥā'il", "Hail"),
    "KSA-ST-03117": ("Al-Ghazalah", "Al Ghazalah"),
    "KSA-ST-00295": ("Al-Ḥā'īṭ", "Al Hait"),
    "KSA-ST-01668": ("Ash-Shamlī", "Ash Shamli"),
    "KSA-ST-00998": ("Ash-Shanān", "Ash Shinan"),
    "KSA-ST-00296": ("As-Sulaymī", "As Sulaymi"),
    "KSA-ST-00963": ("Baq'ā'", "Baqa"),
    "KSA-ST-01160": ("Mawqaq", "Mawqaq"),
    "KSA-ST-02596": ("Simīrā'", "Simira"),
}
# Expected non-centre rows at >= 5,000 (asserted, so a change in the universe is caught).
NON_CENTRE_5K = {
    "KSA-ST-00937",  # Turubah (Turba) Baqa'a governorate, primary 8,590 (not the Makkah Turubah 28,279)
    "KSA-ST-00991",  # Al Ajfar (Alajfir, primary 7,518; crosswalk KSA-ST-00991)
    "KSA-ST-01158",  # Jubbah, primary 5,622
    "KSA-ST-05133",  # Ayal Obaid, grid
    "KSA-ST-01669",  # Asbatr, grid
    "KSA-ST-03874",  # Dhurayghit, grid
    "KSA-ST-07060",  # Al Malwi, OSM tag (dated 1950 in the universe)
    "KSA-ST-01159",  # Al Wudayy, grid
}
# OSM gives these places an Arabic name only (no name:en); the English form is our transliteration (noted).
NAME_EN_TRANSLIT: dict[str, str] = {
    "KSA-ST-07060": "Al-Malwi",
    "KSA-ST-01668": "Ash-Shamlī",
    "KSA-ST-01669": "Asbatr",
    "KSA-ST-03874": "Dhurayghit",
    "KSA-ST-05133": "Ayal Obaid",
}
# Rows whose figure was replaced by the relayed S-hail-001 figure (precedence), kept for the notes.
OVERRIDE_NOTE_CONTEXT: dict[str, str] = {}
# GEO_VERIFY estimates of the pilot run (31 Oct 2026), carried as record-only values: the back-test is above
# the 30 % gate, so none of them enters `population` (docs/geo-verify.md). Not re-run in this track.
GEO_VERIFY_PILOT: dict[str, str] = {
    "KSA-ST-00998": "GEO_VERIFY pilot 31 Oct 2026 (record-only): central 9,424 (band 3,383–17,730), id geo-est-1468d75f",
    "KSA-ST-01160": "GEO_VERIFY pilot 31 Oct 2026 (record-only): central 5,316 (band 1,856–9,305), id geo-est-be17cfdb",
    "KSA-ST-02596": "GEO_VERIFY pilot 31 Oct 2026 (record-only): central 2,589 (band 557–6,382), id geo-est-12342d15",
}
# Economic roles tied to a town in this register, each with the source that ties it (R1a nodes or pilot).
ROLES: dict[str, list[dict[str, str]]] = {
    "KSA-ST-00041": [
        {"role": "administrative", "source": "S-hail-006"},
        {"role": "airport", "source": "S-hail-006"},
        {"role": "industrial_city", "source": "S-r1a-204"},
        {"role": "university", "source": "S-hail-007"},
    ],
    "KSA-ST-01158": [{"role": "heritage", "source": "S-hail-005"}],
}
# Primary-table matches (crosswalk) are verified; the rest of the figures carry their own status.
PRIMARY_CITY_SOURCE = "gastat-census2022-ta1-city5k-xlsx"
WORLDPOP_SOURCE = "worldpop-sau-2020-100m-unadj-constrained"
SECONDARY_SOURCE = "S-hail-001"
PRIMARY_TO_FIND_LOCALITY = (
    "GASTAT Census 2022 locality table (localities under 5,000 are only in the 'Other (< 5,000)' "
    "row of S-cp2-gastat-008)"
)
GRID_SOURCE = "S-r1a-506"
OSM_SOURCE = "S-hail-003"
GOV_SOURCE = "S-cp2-gastat-007"
CITY_SOURCE = "S-cp2-gastat-008"
SKIM_SOURCE = "S-r1a-809"
ROAD_METHOD = "osrm_table_mld_car (S-r1a-809; free flow, uncalibrated)"
DIST_METHOD = (
    "haversine (R1a settlements.parquet; great-circle to the station the road skim targets)"
)
TERRAIN_NOTE = "terrain not classified (no DEM in the R2 sweep; A-hail-001)"


def _primary_governorates() -> dict[str, int]:
    """Governorate totals of the primary GASTAT table (S-cp2-gastat-007), keyed by primary name."""
    df = pd.read_excel(GOV_PRIMARY, header=None, skiprows=1, usecols=[0, 1])
    df.columns = ["name", "total"]
    return {str(r["name"]).strip(): int(r["total"]) for _, r in df.iterrows()}


def _primary_cities() -> pd.DataFrame:
    """Primary city rows of 5,000 or more (S-cp2-gastat-008)."""
    df = pd.read_excel(CITY_PRIMARY, header=None, skiprows=1, usecols=[0, 1])
    df.columns = ["name", "total"]
    return df


def _check_governorate_sum() -> dict[str, int]:
    """The nine Hail governorate rows must sum to the region total (S-hail-001)."""
    primary = _primary_governorates()
    names = [v[1] for v in CENTRES.values()]
    missing = [n for n in names if n not in primary]
    if missing:
        raise SystemExit(f"governorate names not in the primary table: {missing}")
    total = sum(primary[n] for n in names)
    if total != REGION_TOTAL_S_HAIL_001:
        raise SystemExit(
            f"Hail governorates sum {total:,} != region total {REGION_TOTAL_S_HAIL_001:,}"
        )
    return {n: primary[n] for n in names}


def _pop_fields(rec: dict[str, Any]) -> dict[str, Any]:
    """Population provenance fields for one universe row (population basis of the R1a universe)."""
    pop = int(rec["population"])
    src = rec["pop_source"]
    if src == PRIMARY_CITY_SOURCE:
        return {
            "pop_source": CITY_SOURCE,
            "pop_year": 2022,
            "pop_type": "official",
            "pop_source_status": "verified",
            "primary_to_find": None,
            "population": pop,
        }
    if src == SECONDARY_SOURCE:
        return {
            "pop_source": SECONDARY_SOURCE,
            "pop_year": 2022,
            "pop_type": "official",
            "pop_source_status": "secondary",
            "primary_to_find": PRIMARY_TO_FIND_LOCALITY,
            "population": pop,
        }
    if src == WORLDPOP_SOURCE:
        return {
            "pop_source": GRID_SOURCE,
            "pop_year": 2020,
            "pop_type": "grid",
            "pop_source_status": "unverified",
            "primary_to_find": PRIMARY_TO_FIND_LOCALITY,
            "population": pop,
        }
    if str(src).startswith("osm-gcc"):
        year = rec["osm_population_year"]
        return {
            "pop_source": OSM_SOURCE,
            "pop_year": int(year) if pd.notna(year) else 2026,
            "pop_type": "derived",
            "pop_source_status": "secondary",
            "primary_to_find": PRIMARY_TO_FIND_LOCALITY,
            "population": pop,
        }
    raise SystemExit(f"unhandled population source {src!r} for {rec['name_en']}")


def _line_source(nearest: str | None) -> str | None:
    """Source id of the line a station id belongs to (line YAML `source:`)."""
    if not nearest:
        return None
    line_id = nearest.split(":")[0]
    path = LINES / f"{line_id}.yaml"
    if not path.exists():
        return None
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.startswith("source:"):
            return ln.split(":", 1)[1].strip()
    return None


def _metro(name: str | None) -> tuple[str | None, int | None]:
    """'Buraidah (tier 2)' -> ('Buraidah', 2)."""
    if not name:
        return None, None
    base, _, tier = name.partition(" (tier ")
    return base.strip(), int(tier.rstrip(")")) if tier else None


def _ar_key(name: object) -> str:
    """Arabic name key: tatweel (ـ) removed, spaces trimmed (the relayed table prints some with it)."""
    return str(name).replace("\u0640", "").strip()


def _gov_key(name: object) -> str:
    """Arabic governorate key: the universe prints 'محافظة <name>'; the relayed table prints <name>."""
    key = _ar_key(name)
    return key[len("محافظة ") :].strip() if key.startswith("محافظة ") else key


def _relayed_places() -> dict[tuple[str, str], int]:
    """Place rows of the relayed Ḥā'il table (S-hail-001), keyed by (Arabic name, Arabic governorate).

    A duplicate key is an error: a name alone is not a place (two Ḥā'il places share a name).
    """
    out: dict[tuple[str, str], int] = {}
    lines = RELAYED_HAIL.read_text(encoding="utf-8").splitlines()[1:]
    for line in lines:
        # eight fields; the last one (source note) may hold stray commas
        parts = line.split(",", 7)
        if len(parts) == 8 and parts[0] == "place":
            key = (_ar_key(parts[2]), _gov_key(parts[4]))
            if key in out:
                raise SystemExit(f"duplicate relayed place {key}")
            out[key] = int(parts[5])
    return out


def _apply_relayed_precedence(h: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """A GASTAT-relayed figure beats a grid or OSM figure (precedence: official > derived > grid).

    The relayed table (S-hail-001) is matched by (Arabic name, governorate) to every grid or OSM row. Returns the
    frame with the relayed figure in place, and the replaced figures keyed by settlement id.
    """
    relayed = _relayed_places()
    h = h.copy()
    seen: set[tuple[str, str]] = set()
    overridden: dict[str, int] = {}
    for i, r in h.iterrows():
        key = (_ar_key(r["name_ar"]), _gov_key(r["governorate_ar"]))
        if key[0] in ("", "nan"):  # no Arabic name: cannot be matched to the relayed table
            continue
        if key in seen and key in relayed:  # an ambiguous relayed match is an error
            raise SystemExit(f"two universe rows share {key}, which the relayed table matches")
        seen.add(key)
        if r["pop_source"] in (PRIMARY_CITY_SOURCE, SECONDARY_SOURCE):
            continue
        if key in relayed:
            overridden[r["settlement_id"]] = int(r["population"])
            h.at[i, "population"] = relayed[key]
            h.at[i, "pop_source"] = SECONDARY_SOURCE
    return h, overridden


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    settlements = pd.read_parquet(SETTLEMENTS)
    h = settlements[settlements["region"] == REGION].copy()
    gov_totals = _check_governorate_sum()
    h, overridden = _apply_relayed_precedence(h)
    selected = h[(h["population"] >= THRESHOLD_5K) | h["settlement_id"].isin(CENTRES)]
    ids = set(selected["settlement_id"])
    expected = set(CENTRES) | NON_CENTRE_5K
    if ids != expected:
        raise SystemExit(f"selection differs: extra {ids - expected}, missing {expected - ids}")
    rows: list[dict[str, Any]] = []
    checks = {"road_target_mismatch": 0}
    for _, u in selected.iterrows():
        rec = u.to_dict()
        is_centre = rec["settlement_id"] in CENTRES
        gov_en = CENTRES[rec["settlement_id"]][0] if is_centre else _gov_en(rec["governorate"])
        pop = _pop_fields(rec)
        tag_10k = pop["population"] >= 10_000 and pop["pop_type"] != "grid"  # A-screen-031 gate
        tag_5k = pop["population"] >= THRESHOLD_5K
        existing = rec["nearest_existing"]
        committed = rec["nearest_committed"]
        metro, tier = _metro(rec["nearest_metro_city"])
        screened = not (is_centre and pop["population"] < THRESHOLD_5K)
        notes = _notes(rec, is_centre, gov_totals)
        if rec["road_target_existing"] != existing:
            notes.append(
                f"road minutes to {rec['road_target_existing']} (existing), straight-line nearest {existing}"
            )
        if rec["road_target_committed"] != committed:
            checks["road_target_mismatch"] += 1
            notes.append(
                f"road minutes to {rec['road_target_committed']} (committed, unlocated), "
                f"straight-line nearest {committed}"
            )
        roles = ROLES.get(rec["settlement_id"], [])
        if not roles:
            notes.append(
                "economic roles assessed against the R1a nodes: none sourced for this town"
            )
        if rec["settlement_id"] in NAME_EN_TRANSLIT:
            notes.append(
                f"name_en '{NAME_EN_TRANSLIT[rec['settlement_id']]}' is our transliteration (OSM has no name:en)"
            )
        row = {
            "name_ar": rec["name_ar"],
            "name_en": NAME_EN_TRANSLIT.get(rec["settlement_id"], rec["name_en"]),
            "region": REGION,
            "governorate": gov_en,
            "governorate_ar": rec["governorate_ar"],
            "is_governorate_centre": is_centre,
            "osm_id": int(rec["osm_id"]),
            "osm_type": rec["osm_type"],
            "lat": float(rec["lat"]),
            "lon": float(rec["lon"]),
            "population": pop["population"],
            "pop_source": pop["pop_source"],
            "pop_year": pop["pop_year"],
            "pop_type": pop["pop_type"],
            "pop_source_status": pop["pop_source_status"],
            "primary_to_find": pop["primary_to_find"],
            "pop_corroboration": None,
            "pop_corroboration_value": None,
            "tag_10k": tag_10k,
            "tag_5k": tag_5k,
            "dist_existing_km": _f(rec["dist_existing_km"]),
            "road_min_existing": _f(rec["road_min_existing"]),
            "nearest_existing": existing,
            "dist_committed_km": _f(rec["dist_committed_km"]),
            "road_min_committed": _f(rec["road_min_committed"]),
            "nearest_committed": committed.split(":")[0] if committed else None,
            "nearest_committed_station": committed,
            "dist_metro_km": _f(rec["dist_metro_city_km"]),
            "road_min_metro": _f(rec["road_min_metro_city"]),
            "nearest_metro": metro,
            "nearest_metro_tier": tier,
            "economic_roles": roles,
            "terrain_class": None,
            "screened": screened,
            "exclusion_reason": None
            if screened
            else "below 5k and no sourced economic role (governorate centre kept so the governorate is covered)",
            "sources": _sources(rec, is_centre, pop, existing, committed, metro, roles),
            "fixture": False,
            "threshold_50k": None,
            "pilot_sample": None,
            "road_min_method": ROAD_METHOD,
            "dist_method": DIST_METHOD,
            "notes": " | ".join(notes),
        }
        RegionRow.model_validate(row)  # schema check at build time
        rows.append(row)
    rows.sort(key=lambda r: -(r["population"] or 0))
    meta = {
        "governorates_gastat": "9",
        "governorates_listed": str(len({r["governorate"] for r in rows})),
        **{k: str(v) for k, v in checks.items()},
    }
    return rows, meta


def _f(v: Any) -> float | None:
    return None if v is None or pd.isna(v) else round(float(v), 2)


def _gov_en(universe_name: str) -> str:
    for en, prim in CENTRES.values():
        if prim == universe_name:
            return en
    raise SystemExit(f"governorate {universe_name!r} is not one of the nine Hail governorates")


def _notes(rec: dict[str, Any], is_centre: bool, gov_totals: dict[str, int]) -> list[str]:
    out: list[str] = []
    src = rec["pop_source"]
    if src == PRIMARY_CITY_SOURCE:
        out.append(
            "population: GASTAT Census 2022 TA1 city table (S-cp2-gastat-008) matched by value and name to the R1a place node"
        )
    elif src == SECONDARY_SOURCE:
        out.append(
            "population: Census 2022 relayed (S-hail-001, secondary); not in S-cp2-gastat-008"
        )
    elif src == WORLDPOP_SOURCE:
        out.append(
            "population: WorldPop 2020 grid (R1a, pop_type grid, unverified); no GASTAT or OSM figure; below 10k so no corroboration is needed (A-screen-031)"
        )
    else:
        out.append(
            f"population: OSM population tag {rec['osm_population']:.0f} (node {rec['osm_id']}, tag year {int(rec['osm_population_year'])}); not in the GASTAT tables"
        )
    if is_centre:
        gov_name = _gov_en_centre(rec["settlement_id"])
        out.append(
            f"governorate total {gov_totals[gov_name]:,} (S-cp2-gastat-007) is not a settlement figure"
        )
    if rec["settlement_id"] == "KSA-ST-00998":
        out.append(
            "CONFLICT: primary city table has Alshazalah 11,560 (S-cp2-gastat-008), which the crosswalk leaves unmatched (screening/gastat_crosswalk.yaml); Ash-Shanān kept on S-hail-001 until a match is decided (Opus judgement)"
        )
    if rec["settlement_id"] == "KSA-ST-00937":
        out.append(
            "name collision: Turubah (Makkah) 28,279 is a different place in S-cp2-gastat-008; OSM population tag 5,134 conflicts with the census figure, census used"
        )
    if rec["settlement_id"] == "KSA-ST-07060":
        out.append(
            "DOUBTFUL: OSM village tag 15,000 dated 1950 in the R1a universe; it alone passes 10k; governorate membership from OSM polygons at 25.3 N (Opus judgement, A-hail-002)"
        )
    if rec["settlement_id"] == "KSA-ST-00295":
        out.append("OSM spells the node 'Al Hayit' (الحايط); matched by coordinates and name")
    if rec["settlement_id"] == "KSA-ST-00296":
        out.append(
            "centre population is not in the primary table (below 5,000 there, 'Other' row); the R1a grid figure is used (grid, pop_type grid)"
        )
    if rec["settlement_id"] in ("KSA-ST-01160", "KSA-ST-02596"):
        out.append(
            "governorate centre below 5,000: screened false, kept for coverage of the governorate"
        )
    if rec["settlement_id"] in OVERRIDE_NOTE_CONTEXT:
        out.append(OVERRIDE_NOTE_CONTEXT[rec["settlement_id"]])
    if rec["settlement_id"] in GEO_VERIFY_PILOT:
        out.append(GEO_VERIFY_PILOT[rec["settlement_id"]])
    out.append(TERRAIN_NOTE)
    if rec["settlement_id"] == "KSA-ST-00041":
        out.append(
            "regional description S-hail-008 (Aja and Salma ranges; Nafud sand sea) recorded, not a DEM class"
        )
    if rec["settlement_id"] == "KSA-ST-01158":
        out.append(
            "heritage role: UNESCO rock-art component at Jabal Umm Sinman (S-hail-005); Wikidata position of the economic node is region-level, placed at this town"
        )
    return out


def _gov_en_centre(settlement_id: str) -> str:
    return CENTRES[settlement_id][1]


def _sources(
    rec: dict[str, Any], is_centre: bool, pop: dict[str, Any], existing, committed, metro, roles
) -> list[str]:
    out: list[str] = [pop["pop_source"], OSM_SOURCE, SKIM_SOURCE]
    if is_centre:
        out.append(GOV_SOURCE)
    line_existing = _line_source(existing)
    if line_existing:
        out.append(line_existing)
    if committed and committed.startswith("landbridge"):
        out.append("S-054")
    for r in roles:
        out.append(r["source"])
    if rec["settlement_id"] in ("KSA-ST-00937", "KSA-ST-00998"):
        out.append(CITY_SOURCE)
    seen: list[str] = []
    for s in out:
        if s not in seen:
            seen.append(s)
    return seen


def write(rows: list[dict[str, Any]], meta: dict[str, str]) -> None:
    df = pd.DataFrame(rows)
    table = pa.Table.from_pandas(df, preserve_index=False)
    table = table.replace_schema_metadata(
        {
            **(table.schema.metadata or {}),
            **{k.encode(): v.encode() for k, v in meta.items() if not k.startswith("_")},
        }
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT)
    flat = df.copy()
    flat["economic_roles"] = flat["economic_roles"].apply(
        lambda rs: ";".join(f"{r['role']}:{r['source']}" for r in rs)
    )
    flat["sources"] = flat["sources"].apply(lambda s: ";".join(s))
    flat.to_csv(OUT.with_suffix(".csv"), index=False)


app = typer.Typer(add_completion=False, help=__doc__)


@app.command()
def main(
    dry_run: bool = typer.Option(False, "--dry-run", help="print the summary, write nothing"),
) -> None:
    rows, meta = build_rows()
    n_10k = sum(1 for r in rows if r["tag_10k"])
    n_5k = sum(1 for r in rows if r["tag_5k"])
    n_centre = sum(1 for r in rows if r["is_governorate_centre"])
    typer.echo(
        f"rows {len(rows)}; centres {n_centre}; tag_10k {n_10k}; tag_5k {n_5k}; header {meta}"
    )
    if not dry_run:
        write(rows, meta)
        typer.echo(f"wrote {OUT} and {OUT.with_suffix('.csv')}")


if __name__ == "__main__":
    app()
