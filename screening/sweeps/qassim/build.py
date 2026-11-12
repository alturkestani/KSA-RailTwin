# Document version: screening/sweeps/qassim/build.py v1.0 | 31 Oct 2026 | Author: region-scout (REGION_QASSIM) | Status: draft
# ruff: noqa: E501 (report prose and Markdown table rows are long lines)
"""REGION_QASSIM (R2): build the Qassim region register and its Markdown report.

Inputs (all read-only):
- `cities/ksa/zones/settlements.parquet` (R1a universe): OSM ids and coordinates, WorldPop 2020
  grid figures, GASTAT primary matches (`population_basis`), road skims and metro/line distances;
- `data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx` and `..._governorate_primary.xlsx`
  (S-cp2-gastat-008 and -007): the value of record for cities of 5,000 or more and governorates;
- `data/ksa/tables/gastat/TA9-...csv` (S-cp2-gastat-003): region total 1,336,179 for the check;
- `cities/ksa/zones/economic_nodes.parquet` (R1a economic nodes; sources in each node).

Outputs: `cities/ksa/regions/qassim.parquet` (header keys `governorates_gastat`,
`governorates_listed`), `cities/ksa/regions/qassim.csv`, `docs/regions/qassim.md`.

Run: `uv run python -m screening.sweeps.qassim.build`

Overrides are explicit below (each one carries its assumption id). Nothing is estimated here: the
WorldPop figures are the R1a gap-fill and stay `grid`, `unverified` (A-screen-031).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common.schemas import (
    TAG_5K,
    TAG_10K,
    RegionRow,
    _plain,
    corroborates,
)

ROOT = Path(__file__).resolve().parents[3]
UNIVERSE = ROOT / "cities/ksa/zones/settlements.parquet"
ECON = ROOT / "cities/ksa/zones/economic_nodes.parquet"
GASTAT = ROOT / "data/ksa/tables/gastat"
CITY_PRIMARY = GASTAT / "census2022_TA1_city5k_primary.xlsx"
GOV_PRIMARY = GASTAT / "census2022_TA1_governorate_primary.xlsx"
TA9 = GASTAT / (
    "TA9-Population2010-2022byRegionNationalityandGender_"
    "Population2010-2022byRegionNationalityandGender.csv"
)
OUT_PARQUET = ROOT / "cities/ksa/regions/qassim.parquet"
OUT_CSV = ROOT / "cities/ksa/regions/qassim.csv"
OUT_MD = ROOT / "docs/regions/qassim.md"
OUT_JSON = ROOT / "screening/sweeps/qassim/counts.json"
GEO_NOPOP = ROOT / "runs/geo_verify/estimate/no-pop/estimates-no-pop.csv"

REGION = "qassim"
S_GOV_PRIMARY = "S-cp2-gastat-007"
S_CITY_PRIMARY = "S-cp2-gastat-008"
S_TA9 = "S-cp2-gastat-003"
S_RELAYED = "S-cp2-gastat-001"
S_OSM = "S-r1a-210"
S_WORLDPOP = "S-r1a-506"
S_UNIVERSE = "S-qassim-010"
S_RAIL = "S-qassim-005"
S_RAIL_OSM = "S-qassim-007"
S_LANDBRIDGE = "S-054"
S_ADMIN = "S-qassim-004"
S_ROLE_UNVERIFIED = "S-qassim-009"
S_GACA = "S-cp1-100"
S_MODON = "S-r1a-204"
S_UNIV = "S-r1a-221"
S_CITYPOP_LIST = "S-qassim-001"

# The 13 governorates of Qassim (GASTAT primary governorate table names), with the R1a settlement
# that is the governorate centre (OSM place node; A-qassim-004 for Dariyah).
CENTRES = {
    "Buraydah": "KSA-ST-00303",
    "Unayzah": "KSA-ST-00266",
    "Ar Rass": "KSA-ST-00040",
    "Al Bukayriyah": "KSA-ST-01013",
    "Al Midhnab": "KSA-ST-00313",
    "Al Badai": "KSA-ST-01886",
    "Riyadh Al Khabra": "KSA-ST-00060",
    "Al Asyah": "KSA-ST-04781",
    "Ash Shimasiyah": "KSA-ST-00307",
    "Uyun Al Jiwa": "KSA-ST-01027",
    "Uqlat As Suqur": "KSA-ST-00197",
    "Dariyah": "KSA-ST-00478",
    "An Nabhaniyah": "KSA-ST-01068",
}
# Settlement on the relation centroid that duplicates the Dariyah centre (A-qassim-004).
DUPLICATE_EXCLUDED = {"KSA-ST-07370": "KSA-ST-00478"}

# Official figure set by name match to the primary city table (A-qassim-002, A-qassim-004).
OFFICIAL_BY_NAME = {
    "KSA-ST-01645": ("Qasirabin Eaqil", 5617),  # قصر بن عقيل: hand-matched, see notes
    "KSA-ST-00478": ("Dariyah", 5485),  # centre place node; the primary row is the relation
}
# OSM population tags with no year, or a 2010 year: not used as 2022 figures (A-qassim-003).
STALE_OSM_TAG = {
    "KSA-ST-00146": "Khusaibah (OSM tag 10,000, no population:date)",
    "KSA-ST-02908": "Wadi al Nakhil (OSM tag 8,000, no population:date)",
    "KSA-ST-01055": "Ad Dilaymiyah (OSM tag 5,862 = Census 2010 value)",
    "KSA-ST-00340": "Al Fuwayliq (OSM tag 5,620 = Census 2010 value)",
    "KSA-ST-02406": "Adh Dhibiyah (OSM tag 5,068 = Census 2010 value)",
}
# Sourced economic roles, each tied to the town (source ids as in the R1a node or the pilot).
ROLES = {
    "KSA-ST-00303": [
        ("airport", S_GACA),
        ("industrial_city", S_MODON),
        ("university", S_UNIV),
        ("administrative", S_ADMIN),
    ],
    "KSA-ST-00266": [("tourism", S_ROLE_UNVERIFIED)],
    "KSA-ST-00040": [("agriculture", S_ROLE_UNVERIFIED)],
}
GRID_NOTE_TEXT = "WorldPop 2020 grid (R1a gap-fill, A-r1a-004); no second method run (A-screen-033)"
GRID_GATE_TEXT = "grid-only population, uncorroborated"
TERRAIN = "flat_desert"  # A-qassim-001 (assumed; no DEM read)
TERRAIN_NOTE = "terrain assumed flat_desert (A-qassim-001); DEM read pending"


def geo_notes() -> dict[str, str]:
    """GEO_VERIFY no-pop records (record-only; never a population value), keyed by name_en."""
    if not GEO_NOPOP.exists():
        return {}
    g = pd.read_csv(GEO_NOPOP)
    out = {}
    for r in g.itertuples():
        if pd.isna(r.est_central):
            text = "no estimate (no building cluster within the snap radius, A-geo-003)"
        else:
            text = (
                f"estimate {r.est_central:,.0f} (band {r.est_low:,.0f}-{r.est_high:,.0f}; "
                f"grid {r.grid:,.0f}; buildings x occupancy {r.buildings:,.0f})"
            )
        out[r.name_en] = (
            "GEO_VERIFY 31 Oct 2026 (no-pop, record-only; back-test above the 30 % gate): "
            f"{text} [{r.method_log_id}]"
        )
    return out


def _nan(v):
    return None if v is None or (isinstance(v, float) and v != v) or pd.isna(v) else v


def primary_city_values() -> dict[str, int]:
    """Primary city table: name -> total, read from the export (S-cp2-gastat-008)."""
    c = pd.read_excel(CITY_PRIMARY)
    return {str(n): int(t) for n, t in zip(c.iloc[:, 0], c.iloc[:, 1], strict=True)}


def governorate_totals() -> dict[str, int]:
    g = pd.read_excel(GOV_PRIMARY)
    return {str(n): int(t) for n, t in zip(g.iloc[:, 0], g.iloc[:, 1], strict=True)}


def region_total() -> int:
    t = pd.read_csv(TA9, dtype=str)
    row = t[(t.iloc[:, 0] == "Al Qaseem") & (t.iloc[:, 1] == "2022")]
    return int(str(row.iloc[0, 2]).replace(",", ""))


def build_rows(u: pd.DataFrame, econ: pd.DataFrame, city: dict[str, int]) -> list[dict]:
    centre_ids = set(CENTRES.values())
    assert set(CENTRES) <= set(governorate_totals()), "centre names must be GASTAT governorates"
    # every centre id is a Qassim settlement in its own governorate
    for gov, sid in CENTRES.items():
        r = u[u.settlement_id == sid].iloc[0]
        assert r.governorate == gov, (sid, r.governorate, gov)

    # rows: centres; every settlement >= 5,000 (any population type, incl. the 2010-era OSM tags);
    # the duplicate boundary-centroid row (excluded)
    tagged = u[(u.population.fillna(0) >= TAG_5K) | u.settlement_id.isin(STALE_OSM_TAG)]
    ids = sorted(set(tagged.settlement_id) | centre_ids | set(DUPLICATE_EXCLUDED))
    sub = u[u.settlement_id.isin(ids)].copy()
    econ_q = econ[econ.region == REGION]  # kept for the audit count
    assert len(econ_q) > 0

    geo = geo_notes()
    rows = []
    for _, r in sub.iterrows():
        sid = r.settlement_id
        is_centre = sid in centre_ids
        gov = r.governorate
        pop = _nan(r.population)
        pop_type = _nan(r.pop_type)
        pop_source = pop_year = pop_status = prim = corr = corr_v = None
        excl = None
        screened = True
        notes = []
        if sid in DUPLICATE_EXCLUDED:
            screened = False
            excl = (
                "duplicate of the Dariyah governorate centre (" + DUPLICATE_EXCLUDED[sid] + "): "
                "boundary-relation centroid, not a settlement point; the official 5,485 is carried "
                "by the place node (A-qassim-004)"
            )
            pop = None
            notes.append("relation centroid 24.93 N 42.58 E: coordinates not a town position")
        elif sid in STALE_OSM_TAG:
            pop = None
            notes.append(
                "no 2022 figure: "
                + STALE_OSM_TAG[sid]
                + "; absent from the GASTAT Census 2022 table of cities of 5,000 or more, so not "
                "used (A-qassim-003; Opus to confirm)"
            )
        elif sid in OFFICIAL_BY_NAME:
            name, value = OFFICIAL_BY_NAME[sid]
            pop = value
            pop_type, pop_source, pop_year, pop_status = (
                "official",
                S_CITY_PRIMARY,
                2022,
                "verified",
            )
            if sid == "KSA-ST-01645":
                notes.append(
                    "primary export name 'Qasirabin Eaqil' (5,617) joined by hand to this OSM "
                    "village (قصر بن عقيل, Buraydah); the R1a matcher had no OSM name for it; "
                    "the WorldPop 16,608 is superseded (A-qassim-002; Opus to confirm)"
                )
            else:
                notes.append(
                    "primary Census 2022 figure for 'Ḍariyah' (5,485) carried by this place node, "
                    "not by the boundary relation (A-qassim-004); the WorldPop 5,798 is superseded"
                )
        elif pop is not None and pop_type == "official":
            pop_source, pop_year, pop_status = S_CITY_PRIMARY, 2022, "verified"
            pop_type = "official"
        elif pop is not None and pop_type == "grid":
            pop_type = "grid"
            pop_source, pop_year, pop_status = S_WORLDPOP, 2020, "unverified"
            notes.append(GRID_NOTE_TEXT)
        elif pop is not None:
            raise ValueError(f"unexpected population basis for {sid}: {pop_type}")
        # grid-only figures >= 10k are gated: no second method was run, so tag_10k stays false
        if (
            pop_type == "grid"
            and pop is not None
            and pop >= TAG_10K
            and not corroborates(pop, corr_v)
        ):
            excl = GRID_GATE_TEXT
        pop_int = int(pop) if pop is not None else None
        tag_10k = bool(pop_int is not None and pop_int >= TAG_10K and excl != GRID_GATE_TEXT)
        tag_5k = bool(pop_int is not None and pop_int >= TAG_5K)

        roles = [{"role": role, "source": src} for role, src in ROLES.get(sid, [])]
        if any(x["source"] == S_ROLE_UNVERIFIED for x in roles):
            notes.append(
                "role from an unverified search summary (S-qassim-009), not checked at source "
                "(A-qassim-006; Opus to confirm)"
            )
        if r.name_en in geo and pop_int is None:
            notes.append(geo[r.name_en])
        if _nan(r.name_en) is None:
            notes.append(
                "name_en is the Arabic name (no Latin name in the R1a universe; transliteration pending)"
            )
        notes.append(TERRAIN_NOTE)
        notes.append(f"R1a settlement_id {sid}")
        sources = [S_OSM, S_UNIVERSE, S_RAIL, S_RAIL_OSM, S_LANDBRIDGE]
        if pop_source:
            sources.insert(0, pop_source)
        if pop_type == "grid" and S_WORLDPOP not in sources:
            sources.insert(1, S_WORLDPOP)
        for src in [x["source"] for x in roles] + ([S_ADMIN] if sid == "KSA-ST-00303" else []):
            if src not in sources:
                sources.append(src)

        rec = {
            "name_ar": r.name_ar,
            "name_en": _nan(r.name_en) or r.name_ar,
            "region": REGION,
            "governorate": gov,
            "governorate_ar": r.governorate_ar,
            "is_governorate_centre": is_centre,
            "osm_id": int(r.osm_id),
            "osm_type": r.osm_type,
            "lat": float(r.lat),
            "lon": float(r.lon),
            "population": pop_int,
            "pop_source": pop_source if pop_int is not None else None,
            "pop_year": pop_year if pop_int is not None else None,
            "pop_type": pop_type if pop_int is not None else None,
            "pop_source_status": pop_status if pop_int is not None else None,
            "primary_to_find": prim,
            "pop_corroboration": corr,
            "pop_corroboration_value": corr_v,
            "tag_10k": tag_10k,
            "tag_5k": tag_5k,
            "dist_existing_km": round(float(r.dist_existing_km), 2),
            "road_min_existing": round(float(r.road_min_existing), 1),
            "nearest_existing": "SAR North passenger line, station al-Qassim (R1a: "
            + str(r.nearest_existing)
            + ")",
            "dist_committed_km": round(float(r.dist_committed_km), 2),
            "road_min_committed": round(float(r.road_min_committed), 1),
            "nearest_committed": "Landbridge (R1a layer: committed; YAML status: announced)",
            "nearest_committed_station": "Dawadmi (unlocated proxy, R1a)",
            "dist_metro_km": round(float(r.dist_metro_city_km), 2),
            "road_min_metro": round(float(r.road_min_metro_city), 1),
            "nearest_metro": "Buraidah",
            "nearest_metro_tier": int(r.nearest_metro_tier),
            "road_min_method": "OSRM car MLD, 5 nearest candidates (A-r1a-027); R1a skim",
            "dist_method": (
                "great circle to the nearest intercity station (A-r1a-008); committed to "
                "unlocated proxy stations (A-r1a-007)"
            ),
            "economic_roles": roles,
            "terrain_class": TERRAIN,
            "screened": screened,
            "exclusion_reason": excl,
            "sources": sources,
            "fixture": False,
            "threshold_50k": None,
            "pilot_sample": None,
            "notes": " | ".join(notes),
        }
        rows.append(rec)
    return rows


def validate_rows(rows: list[dict]) -> None:
    for rec in rows:
        RegionRow.model_validate({k: _plain(v) for k, v in rec.items()})


def write(rows: list[dict], gov_count: int) -> None:
    rows = sorted(
        rows,
        key=lambda r: (
            not r["is_governorate_centre"],
            -(r["population"] or 0),
            r["name_en"],
        ),
    )
    table = pa.Table.from_pylist(rows)
    meta = {
        b"governorates_gastat": str(gov_count).encode(),
        b"governorates_listed": str(gov_count).encode(),
    }
    table = table.replace_schema_metadata(meta)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT_PARQUET)
    csv_rows = []
    for r in rows:
        c = dict(r)
        c["economic_roles"] = ";".join(f"{x['role']}:{x['source']}" for x in r["economic_roles"])
        c["sources"] = ";".join(r["sources"])
        csv_rows.append(c)
    pd.DataFrame(csv_rows).to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(counts(rows), indent=2, ensure_ascii=False) + "\n")


def counts(rows: list[dict]) -> dict:
    pops = [r["population"] for r in rows if r["population"] is not None]
    return {
        "rows": len(rows),
        "centres": sum(r["is_governorate_centre"] for r in rows),
        "screened": sum(r["screened"] for r in rows),
        "excluded": sum(not r["screened"] for r in rows),
        "tag_10k": sum(r["tag_10k"] for r in rows),
        "tag_5k": sum(r["tag_5k"] for r in rows),
        "pop_official": sum(r["pop_type"] == "official" for r in rows),
        "pop_grid": sum(r["pop_type"] == "grid" for r in rows),
        "pop_null": sum(r["population"] is None for r in rows),
        "grid_gate_excluded": sum(r["exclusion_reason"] == GRID_GATE_TEXT for r in rows),
        "roles_rows": sum(bool(r["economic_roles"]) for r in rows),
        "roles_total": sum(len(r["economic_roles"]) for r in rows),
        "population_sum_rows": sum(pops),
    }


UNPLACED = [
    # primary city names with no R1a settlement and no region in the export (matcher: ambiguous)
    ("Alqaruh", 8656),
    ("Albadie Walqarfi", 8623),
    ("Almansuruh", 7622),
    ("Alqarin", 7339),
    ("Alshaquh Aleulya", 5449),
    ("Aleurafa'", 5432),
    ("Alkhadra'", 5861),
]
OPUS = [
    "Dariyah centre (A-qassim-004): the official 5,485 is carried by place node KSA-ST-00478 (lat 24.72), not by the boundary centroid KSA-ST-07370 (24.93 N, 42.58 E); the two are 42 km apart. Confirm the place and its coordinates.",
    "Qasr Bin Aqil (A-qassim-002): primary 'Qasirabin Eaqil' (5,617) is joined by hand to OSM village KSA-ST-01645 (WorldPop 16,608); confirm the identity. Tag_10k is false either way.",
    "Stale OSM population tags (A-qassim-003): Khusaibah (10,000, no date), Wadi al Nakhil (8,000, no date), Ad Dilaymiyah (5,862), Al Fuwayliq (5,620) and Adh Dhibiyah (5,068) equal Census 2010 values or have no date, and none is in the GASTAT 2022 table of cities of 5,000 or more. Kept with population null; decide whether to treat them as below 5,000 in 2022.",
    "Grid-only towns of 10,000 or more (four rows, uncorroborated, tag_10k false): Al-Qabaah 29,927, Ash Shihiyah 25,648, Dulay` Rashid 17,933, Al Badai al Ulya 10,710. No second method was run (no 2010 match in the Census 2010 list). Decide whether to run a corroboration method for them.",
    "Unplaced primary cities (no R1a settlement; the export has no region, and the matcher found no unique name): Alqaruh 8,656; Albadie Walqarfi 8,623; Almansuruh 7,622; Alqarin 7,339; Alshaquh Aleulya 5,449; Aleurafa' 5,432; Alkhadra' 5,861. Any of them could be in Qassim: the completeness claim is conditional on this list.",
    "Landbridge layer (A-qassim-005): R1a labels it committed (the nearest committed line for every Qassim row), while cities/ksa/lines/landbridge.yaml has status announced. Rule 5 says planned lines are announced/planned. Confirm the layer before any commitment-based screening.",
    "Unverified economic roles (A-qassim-006): tourism for Unayzah and agriculture for Ar Rass come from an unopened search summary (S-qassim-009). Verify at source or drop before screening.",
    "Terrain (A-qassim-001): every row is flat_desert by assumption. The Ad Dahna dunes and the escarpment edge may apply; a DEM read is pending.",
    "Economic roles not assigned: Qassim MODON Second Industrial City and the Qassim MODON Oasis (unlocated), Ba'itha bauxite mine (no settlement row in the register). Confirm the host towns.",
]


def render_md(rows: list[dict], c: dict) -> str:
    rs = sorted(
        rows, key=lambda r: (not r["is_governorate_centre"], -(r["population"] or 0), r["name_en"])
    )
    lines = [
        "> **Document version:** docs/regions/qassim.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_QASSIM) | Status: draft",
        "",
        "# Qassim (القصيم) region sweep, slug `qassim`",
        "",
        "**Screening input, not a forecast.** Synthetic demand, uncalibrated: scenario comparison, not a forecast.",
        "",
        "Built by `screening/sweeps/qassim/build.py` from the R1a settlement universe (`cities/ksa/zones/settlements.parquet`), the GASTAT primary Census 2022 exports and the R1a economic nodes. Register: `cities/ksa/regions/qassim.parquet` (CSV mirror `qassim.csv`); validated with `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/qassim.parquet`. Source ids `S-cp2-gastat-*`, `S-r1a-*`, `S-cp1-*` are in `docs/sources/index.csv`; `S-qassim-*` are in `docs/sources/r2-qassim.csv`.",
        "",
        "## 1. Governorate count (rule 2)",
        "",
        "| source | count | status |",
        "|---|---|---|",
        "| GASTAT primary governorate export (S-cp2-gastat-007; 150 rows) | 13 Qassim governorates named in the table; their 2022 totals sum to 1,336,179 | verified (read from the export) |",
        "| GASTAT TA9 region table, 2022 (S-cp2-gastat-003) | Al Qaseem 2022 = 1,336,179 | verified (read from the CSV) |",
        "| DataPulse relayed governorate table (S-cp2-gastat-001) | same names and values on the 13 governorates (cross-check; not value of record) | secondary |",
        "",
        f"`governorates_gastat` = {c['governorates']} and `governorates_listed` = {c['governorates']}. GASTAT's exports do not state a Qassim governorate count; the 13 is derived from the 13 names whose sum equals the TA9 region total exactly. Equal, with no discrepancy to record. The 13 are: Buraydah, Unayzah, Ar Rass, Al Bukayriyah, Al Midhnab, Al Badai, Riyadh Al Khabra, Al Asyah, Ash Shimasiyah, Uyun Al Jiwa, Uqlat As Suqur, Dariyah, An Nabhaniyah.",
        "",
        "Abanat (R1a sub-locality rows, population 0 in the universe, in An Nabhaniyah) is not a governorate and is not a row: the 13 governorates reconcile to the region total without it.",
        "",
        "## 2. Counts",
        "",
        "| measure | value |",
        "|---|---|",
        f"| rows in the register | {c['rows']} (13 governorate centres, {c['rows'] - c['centres']} other rows) |",
        f"| screened rows / excluded rows | {c['screened']} / {c['excluded']} |",
        f"| rows with tag_10k = true (≥ 10,000) | {c['tag_10k']} (all GASTAT primary, official) |",
        f"| rows with tag_5k = true (≥ 5,000; sensitivity) | {c['tag_5k']} (official {c['tag5k_official']}, grid {c['tag5k_grid']}) |",
        f"| grid-only rows ≥ 10,000 gated out (`grid-only population, uncorroborated`) | {c['grid_gate_excluded']} |",
        f"| rows with no 2022 population (not used; see §5) | {c['pop_null']} |",
        f"| economic roles, rows with ≥ 1 sourced role / total roles | {c['roles_rows']} / {c['roles_total']} |",
        f"| population basis: official / grid / none | {c['pop_official']} / {c['pop_grid']} / {c['pop_null']} |",
        "",
        "Population provenance: an official figure is the GASTAT primary city export (S-cp2-gastat-008, read directly: `verified`); a grid figure is the WorldPop 2020 gap-fill (S-r1a-506, `unverified`, A-screen-031). No `secondary` figure is used. No corroboration method was run for any grid row (`pop_corroboration` null), so no grid row passes the 10,000 test.",
        "",
        "## 3. Coverage",
        "",
        f"The R1a universe holds {c['universe_rows']} Qassim settlements. The register holds the 13 governorate centres, every settlement at or above 5,000 in the universe (any population basis), and the rows listed in §5. The other {c['below5k']} settlements are not rows: they are below the 5,000 sensitivity threshold (A-screen-002), and none is a governorate centre.",
        "",
        "Completeness caveat: seven primary cities of 5,000 or more could not be placed in any region (table in §6). Any of them could be in Qassim, so the list of Qassim towns at or above 5,000 is complete only conditionally on that list.",
        "",
        "## 4. Register table",
        "",
        "Distances: `dist_existing_km` = great circle to the nearest intercity station (A-r1a-008; here SAR North passenger, al-Qassim); `road_min_existing` = OSRM car, MLD, 5 nearest (A-r1a-027). `dist_committed_km` = to the Landbridge proxy station Dawadmi (unlocated; committed layer as in R1a). `dist_metro_km` = to Buraidah (approved tier-2 metro). Population per row is in the register; roles are sourced in the register.",
        "",
        "| name (EN) | name (AR) | governorate | centre | population | basis | ≥10k | ≥5k | existing km (road min) | committed km (road min) | metro km (road min) | roles | screened / exclusion |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rs:
        pop = f"{r['population']:,}" if r["population"] is not None else "null"
        basis = f"{r['pop_type']} / {r['pop_source_status']}" if r["pop_type"] else "none"
        roles = (
            "; ".join(f"{x['role']} ({x['source']})" for x in r["economic_roles"]) or "none sourced"
        )
        excl = "yes" if r["screened"] else f"no: {r['exclusion_reason']}"
        if r["screened"] and r["exclusion_reason"]:
            excl = f"yes (kept; {r['exclusion_reason']})"
        lines.append(
            f"| {r['name_en']} | {r['name_ar']} | {r['governorate']} | {'yes' if r['is_governorate_centre'] else ''} | {pop} | {basis} | {'true' if r['tag_10k'] else 'false'} | {'true' if r['tag_5k'] else 'false'} | {r['dist_existing_km']:.1f} ({r['road_min_existing']:.0f}) | {r['dist_committed_km']:.0f} ({r['road_min_committed']:.0f}) | {r['dist_metro_km']:.1f} ({r['road_min_metro']:.0f}) | {roles} | {excl} |"
        )
    lines += [
        "",
        "## 5. Exclusions and rows without a 2022 population",
        "",
        "- Dariyah boundary centroid (KSA-ST-07370, OSM relation 12406851): excluded as a duplicate of the Dariyah centre place node (KSA-ST-00478), which carries the official 5,485 (A-qassim-004).",
        "- Five OSM-tagged towns with no 2022 figure (A-qassim-003): Khusaibah, Wadi al Nakhil, Ad Dilaymiyah, Al Fuwayliq, Adh Dhibiyah. Kept with population null; the stale OSM values are recorded in the notes, with the record-only GEO_VERIFY estimates (below).",
        "- Four grid-only towns of 10,000 or more are kept (screened) with tag_10k false and `grid-only population, uncorroborated`.",
        "",
        "GEO_VERIFY no-pop step (31 Oct 2026, `screening/sweeps/qassim/geo_nopop.py`, seed 1): record-only, not used in `population`; the buildings and grid estimators are above the 30 % back-test gate (`docs/geo-verify.md`). Values are in each row's notes.",
        "",
        "## 6. Unplaced primary cities (completeness)",
        "",
        "Primary cities of 5,000 or more with no R1a settlement and no region in the export (the R1a matcher left them ambiguous; they are not in this register). Any of them could be a Qassim town; see Opus item 5.",
        "",
        "| primary city name (as exported) | 2022 total |",
        "|---|---|",
    ]
    for n, v in UNPLACED:
        lines.append(f"| {n} | {v:,} |")
    lines += [
        "",
        "Hand joins made in this sweep (not the R1a matcher): Qasirabin Eaqil (5,617) to KSA-ST-01645; Dariyah (5,485) to the place node KSA-ST-00478.",
        "",
        "## 7. Sources",
        "",
        "- GASTAT Census 2022 primary TA1 exports: governorates (S-cp2-gastat-007), cities of 5,000 or more (S-cp2-gastat-008), TA9 region table (S-cp2-gastat-003); relayed DataPulse cross-check (S-cp2-gastat-001).",
        "- OpenStreetMap, ODbL (S-r1a-210): element ids and coordinates; WorldPop 2020 100 m constrained, UN-adjusted, CC BY 4.0 (S-r1a-506, S-r1a-508).",
        "- R1a settlement universe, road skims and line distances (S-qassim-010); SAR North passenger line status (S-qassim-005, S-qassim-007); Landbridge (S-054).",
        "- Economic roles: GACA airports (S-cp1-100), MODON industrial cities (S-r1a-204), Qassim University (S-r1a-221); administrative seat from the Wikipedia article (S-qassim-004, secondary); tourism and agriculture from unopened search summaries (S-qassim-009, unverified).",
        "- Access date for the local GASTAT files: 31 Oct 2026 (`data/ksa/tables/gastat/README.md`); hashes in `cities/ksa/sources.yaml`.",
        "",
        "## 8. Facts: verification status",
        "",
        "- Verified (read from the GASTAT export or the R1a output): the 13 governorate totals and the region total; the 19 official rows (17 matched by value by R1a, Dariyah re-pointed from the boundary relation to its place node, and Qasr Bin Aqil hand-joined: see Opus items 1 and 2).",
        "- Secondary: governorate names as relayed; the administrative seat (Wikipedia); OSM ids and coordinates (ODbL, extract 14 Oct 2026).",
        "- Unverified: WorldPop grid figures (all grid rows); economic roles for Unayzah and Ar Rass (S-qassim-009); terrain (assumed).",
        "",
        "## 9. Needs Opus judgement (not resolved by guessing)",
        "",
    ]
    for i, t in enumerate(OPUS, 1):
        lines.append(f"{i}. {t}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    u = pd.read_parquet(UNIVERSE)
    u = u[u.region == REGION].copy()
    econ = pd.read_parquet(ECON)
    city = primary_city_values()
    gov = governorate_totals()
    qassim_gov = [g for g in gov if g in CENTRES]
    assert len(qassim_gov) == 13
    gsum = sum(gov[g] for g in CENTRES)
    assert gsum == region_total() == 1336179, (gsum, region_total())
    # the Qassim governorate rows, verified against the primary table (value of record)
    for name, total in OFFICIAL_BY_NAME.values():
        assert city[name] == total, (name, city.get(name), total)
    rows = build_rows(u, econ, city)
    validate_rows(rows)
    write(rows, gov_count=len(CENTRES))
    selected = set(
        u[(u.population.fillna(0) >= TAG_5K) | u.settlement_id.isin(STALE_OSM_TAG)].settlement_id
    )
    selected |= set(CENTRES.values()) | set(DUPLICATE_EXCLUDED)
    c = counts(rows)
    c.update(
        governorates=len(CENTRES),
        universe_rows=len(u),
        below5k=len(u) - len(selected),
        tag5k_official=sum(r["tag_5k"] and r["pop_type"] == "official" for r in rows),
        tag5k_grid=sum(r["tag_5k"] and r["pop_type"] == "grid" for r in rows),
    )
    OUT_JSON.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(rows, c), encoding="utf-8")
    print(json.dumps(c, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
