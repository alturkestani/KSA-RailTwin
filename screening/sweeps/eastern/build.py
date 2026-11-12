# Document version: screening/sweeps/eastern/build.py v1.0 | 31 Oct 2026 | Author: region-scout (REGION_EASTERN) | Status: draft
# ruff: noqa: E501  (the Markdown writer carries long prose lines)
"""Build the R2 region register for the Eastern Province (slug `eastern`).

Inputs (all in this worktree, read-only):
- cities/ksa/zones/settlements.parquet  R1a settlement universe (primary GASTAT populations
  attached by screening.gastat; OSM tags; WorldPop 2020 grid; OSRM road minutes; metro tiers)
- cities/ksa/zones/economic_nodes.parquet  R1a economic nodes (sourced roles)
- cities/ksa/regions/pilot-eastern.parquet  pilot register (one row used: Al-Jubail, Al-Ahsa)
- data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx  (governorate control total)

Outputs: cities/ksa/regions/eastern.parquet, eastern.csv, docs/regions/eastern.md.
Run from the repository root:  PYTHONPATH=. python screening/sweeps/eastern/build.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common.schemas import GRID_UNCORROBORATED, TAG_5K, TAG_10K, RegionRow, corroborates

ROOT = Path(".")
SETTLEMENTS = ROOT / "cities/ksa/zones/settlements.parquet"
NODES = ROOT / "cities/ksa/zones/economic_nodes.parquet"
PILOT = ROOT / "cities/ksa/regions/archive/pilot/pilot-eastern.parquet"
GOV_XLSX = ROOT / "data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx"
OUT_PARQUET = ROOT / "cities/ksa/regions/eastern.parquet"
OUT_CSV = ROOT / "cities/ksa/regions/eastern.csv"
OUT_MD = ROOT / "docs/regions/eastern.md"

GOVERNORATES_GASTAT = 12  # S-cp2-gastat-007 (150-row list): 12 Eastern governorate rows
GOVERNORATES_LISTED = 12  # the 12 GASTAT rows below; Al-Bayda is an excluded row (see notes)

# GASTAT governorate (R1a gov_id) -> English name, Arabic name, centre settlement_id.
GOV = {
    "G032": ("Abqaiq", "بقيق", "KSA-ST-00047"),
    "G033": ("Al-Ahsa", "الأحساء", "KSA-ST-00003"),
    "G034": ("Al-Jubail", "الجبيل", "KSA-ST-00002"),
    "G035": ("Al-Khafji", "الخفجي", "KSA-ST-00269"),
    "G036": ("An-Nuayriyah", "النعيرية", "KSA-ST-00902"),
    "G037": ("Al-Udayd", "العديد", "KSA-ST-07367"),
    "G038": ("Ad-Dammam", "الدمام", "KSA-ST-00004"),
    "G039": ("Hafar Al-Batin", "حفر الباطن", "KSA-ST-00267"),
    "G040": ("Al-Khubar", "الخبر", "KSA-ST-00001"),
    "G041": ("Qaryat al-Ulya", "قرية العليا", "KSA-ST-00046"),
    "G042": ("Al-Qatif", "القطيف", "KSA-ST-01114"),
    "G043": ("Ras Tannurah", "رأس تنورة", "KSA-ST-01101"),
}
GOV_EN_TO_ID = {v[2]: k for k, v in GOV.items()}

# Settlement rows that are NOT register rows (excluded, reason recorded).
EXCLUDE = {
    "KSA-ST-07368": (
        "Al-Bayda: not one of the 12 GASTAT Eastern governorates (S-cp2-gastat-007); listed as a "
        "13th governorate in Arabic sources (S-eastern-003); R1a grid value (32 persons) not used; "
        "centre not located (A-eastern-004)"
    ),
    "KSA-ST-07366": (
        "duplicate of KSA-ST-01101 (Ra's Tannurah) on the same OSM node 1237805652; R1a grid value "
        "(6,445) not used"
    ),
    "KSA-ST-03116": (
        "duplicate of the Al-Hofuf / Al-Ahsa urban row KSA-ST-00003: the OSM 'Al Ahsa' node "
        "(3 km away) carries a contributor value of 903,597 that is an oasis-wide tag, not a town "
        "figure; the tag is not used (A-eastern-003)"
    ),
    "KSA-ST-00817": (
        "Al-Mubarraz village (grid, 32,327): the GASTAT city Al-Mubarraz (299,501) is carried on "
        "KSA-ST-00003 as part of the Al-Hofuf-Al-Mubarraz row (A-eastern-003); the grid figure is "
        "not used"
    ),
}

# R1a economic nodes (node_id) -> settlement_id that carries the role (sourced town).
NODE_TOWN = {
    "airport-dmm-king-fahd": ("KSA-ST-00004", "airport"),
    "airport-aqi-al-qaisumah": ("KSA-ST-00994", "airport"),
    "airport-hof-al-ahsa": ("KSA-ST-00003", "airport"),
    "port-king-abdulaziz-dammam": ("KSA-ST-00004", "port"),
    "port-jubail-commercial": ("KSA-ST-00002", "port"),
    "port-king-fahad-industrial-jubail": ("KSA-ST-00002", "port"),
    "port-ras-tanura": ("KSA-ST-01101", "port"),
    "modon-dammam-1": ("KSA-ST-00004", "industrial_city"),
    "modon-dammam-2": ("KSA-ST-00004", "industrial_city"),
    "modon-dammam-3": ("KSA-ST-00004", "industrial_city"),
    "modon-ahsa-1": ("KSA-ST-00003", "industrial_city"),
    "modon-ahsa-oasis": ("KSA-ST-00003", "industrial_city"),
    "modon-hafar-al-batin": ("KSA-ST-00267", "industrial_city"),
    "rcjy-jubail-industrial": ("KSA-ST-00002", "industrial_city"),
    "energy-ras-tanura-refinery": ("KSA-ST-01101", "energy"),
    "energy-abqaiq-processing": ("KSA-ST-00047", "energy"),
    "energy-satorp-jubail": ("KSA-ST-00002", "energy"),
    "heritage-al-ahsa-oasis": ("KSA-ST-00003", "heritage"),
    "border-king-fahd-causeway": ("KSA-ST-00001", "border_crossing"),
    "border-al-khafji-kuwait": ("KSA-ST-00269", "border_crossing"),
    "univ-kfupm": ("KSA-ST-00053", "university"),
    "univ-imam-abdulrahman": ("KSA-ST-00004", "university"),
    "univ-king-faisal": ("KSA-ST-00003", "university"),
    "univ-hafr-al-batin": ("KSA-ST-00267", "university"),
    "univ-jubail-college": ("KSA-ST-00002", "university"),
}
# Roles from the pilot's search-extract sources (secondary), kept for towns with no R1a node.
EXTRA_ROLES = {
    "KSA-ST-00042": [("military", "S-eastern-001")],  # King Khalid Military City (census row)
    "KSA-ST-00053": [("military", "S-eastern-009")],  # Dhahran (air base, search extract)
}

NOT_IN_UNIVERSE = {
    # Al-Jubail (Al-Ahsa), 9,994 in the primary export ('Aljabil', crosswalk: none); the pilot's
    # OSM neighbourhood object is used for the coordinates and osm_id only.
    "AL-JUBAIL-AHSA": "pilot",
}


def _clean(v):
    if v is None or v is pd.NA or v is pd.NaT:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "item"):
        return v.item()
    return v


def _road(v):
    v = _clean(v)
    return None if v is None else float(v)


def gastat_control_total() -> tuple[int, dict[str, int]]:
    """Sum of the 12 Eastern governorate rows in the primary GASTAT governorate export."""
    raw = pd.read_excel(GOV_XLSX, header=None)
    names = {
        "Ad Dammam": "G038",
        "Al Ahsa": "G033",
        "Al Jubayl": "G034",
        "Al Khafji": "G035",
        "Al Khubar": "G040",
        "Al Nuayriyah": "G036",
        "Al Qatif": "G042",
        "Al Udayd": "G037",
        "Buqayq": "G032",
        "Hafar Al Batin": "G039",
        "Qaryah Al Ulya": "G041",
        "Ras Tannurah": "G043",
    }
    found: dict[str, int] = {}
    for _, row in raw.iterrows():
        label = str(row[0]).strip()
        if label in names and names[label] not in found:
            found[names[label]] = int(row[1])
    if len(found) != GOVERNORATES_GASTAT:
        raise SystemExit(f"governorate export: found {len(found)} of 12 Eastern rows")
    return sum(found.values()), found


def population_fields(s: pd.Series) -> dict:
    """Population provenance per the CP2 population rule (A-screen-031 to 039)."""
    p = _clean(s.population)
    if p is None or p <= 0:
        return {}
    p = int(p)
    if s.pop_type == "official":
        return {
            "population": p,
            "pop_source": "S-cp2-gastat-008",
            "pop_year": 2022,
            "pop_type": "official",
            "pop_source_status": "verified",
        }
    if s.pop_type == "derived":  # OSM place population tag, not a GASTAT figure
        if _clean(s.pop_year) is None:  # undated tag: no year, so no figure (A-eastern-005)
            return {}
        return {
            "population": p,
            "pop_source": "S-r1a-210",
            "pop_year": int(s.pop_year),
            "pop_type": "derived",
            "pop_source_status": "secondary",
            "primary_to_find": "GASTAT Census 2022 locality table (not in the primary exports)",
        }
    if s.pop_type == "grid":
        corr = _clean(s.pop_corroboration)
        corr_v = _clean(s.pop_corroboration_value)
        return {
            "population": p,
            "pop_source": "S-r1a-505",
            "pop_year": 2020,
            "pop_type": "grid",
            "pop_source_status": "unverified",
            "pop_corroboration": corr,
            "pop_corroboration_value": None if corr_v is None else float(corr_v),
        }
    raise ValueError(f"unexpected pop_type {s.pop_type!r} for {s.name_en}")


def build_rows(s_east: pd.DataFrame, pilot: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    NODE_ROWS = pd.read_parquet(NODES)
    centre_ids = {v[2] for v in GOV.values()}
    by_id = {r.settlement_id: r for r in s_east.itertuples(index=False)}
    # Settlements that become register rows: governorate centres, everything >= 5,000, and the
    # Al-Bayda / Al-Udayd / duplicate exclusions (only the first two are kept as rows).
    keep = set(centre_ids) | set(EXCLUDE)
    for r in s_east.itertuples(index=False):
        p = _clean(r.population)
        if p is not None and p >= TAG_5K:
            keep.add(r.settlement_id)

    for sid in sorted(keep, key=lambda x: str(_clean(by_id[x].name_en) or "")):
        r = by_id[sid]
        gov_id = r.gov_id
        gov_en, gov_ar, _ = GOV[gov_id]
        pop = population_fields(r)
        osm_type = _clean(r.osm_type)
        # R1a leaves a few grid-only settlements unnamed: a labelled placeholder, never a guess
        unnamed = f"(unnamed {osm_type} {int(r.osm_id)})"
        row = {
            "name_ar": _clean(r.name_ar) or "",
            "name_en": _clean(r.name_en) or unnamed,
            "region": "eastern",
            "governorate": gov_en,
            "governorate_ar": gov_ar,
            "is_governorate_centre": sid in centre_ids,
            "osm_id": int(r.osm_id) if _clean(r.osm_id) is not None else None,
            "osm_type": osm_type,
            "lat": float(r.lat),
            "lon": float(r.lon),
            "dist_existing_km": _road(r.dist_existing_km),
            "nearest_existing": _clean(r.road_target_existing),
            "road_min_existing": _road(r.road_min_existing),
            "dist_committed_km": _road(r.dist_committed_km),
            "nearest_committed": _clean(r.nearest_committed_line),
            "nearest_committed_station": _clean(r.road_target_committed),
            "road_min_committed": _road(r.road_min_committed),
            "dist_metro_km": _road(r.dist_metro_city_km),
            "nearest_metro": _clean(r.nearest_metro_city),
            "road_min_metro": _road(r.road_min_metro_city),
            "nearest_metro_tier": int(r.nearest_metro_tier)
            if _clean(r.nearest_metro_tier) is not None
            else None,
            "road_min_method": "osrm_table_mld_car (R1a skims)"
            if _road(r.road_min_existing) is not None
            else "pending skims",
            "dist_method": "haversine to the nearest station (R1a)",
            "economic_roles": [],
            "terrain_class": None,
            "screened": True,
            "exclusion_reason": None,
            "sources": ["S-cp2-gastat-008", "S-r1a-210"],
            "fixture": False,
        }
        # population (no figure for a governorate centre with a zero grid value)
        if pop:
            row.update(pop)
        row["tag_5k"] = bool(row.get("population", 0) and row["population"] >= TAG_5K)
        row["tag_10k"] = bool(row.get("population", 0) and row["population"] >= TAG_10K)
        if row.get("pop_type") == "grid":
            if row["population"] >= TAG_10K and not corroborates(
                row["population"], row.get("pop_corroboration_value")
            ):
                row["tag_10k"] = False
                row["exclusion_reason"] = GRID_UNCORROBORATED + " (screened true; tag_5k not gated)"
            row["sources"] = ["S-r1a-505", "S-r1a-210"]
        if row.get("pop_type") == "derived":
            row["sources"] = ["S-r1a-210"]
        if sid in EXCLUDE:
            row["screened"] = False
            row["exclusion_reason"] = EXCLUDE[sid]
            row["tag_10k"] = False
            row["tag_5k"] = False
            row.pop("population", None)
            for k in (
                "pop_source",
                "pop_year",
                "pop_type",
                "pop_source_status",
                "pop_corroboration",
                "pop_corroboration_value",
            ):
                row.pop(k, None)
            row["sources"] = ["S-r1a-210"]
        # economic roles
        roles = []
        for node_id, (town_id, role) in NODE_TOWN.items():
            if town_id == sid:
                n = NODE_ROWS.loc[NODE_ROWS.node_id == node_id].iloc[0]
                src = str(n.source_id).split(";")[0]
                roles.append({"role": role, "source": src})
        for role, src in EXTRA_ROLES.get(sid, []):
            roles.append({"role": role, "source": src})
        row["economic_roles"] = roles
        row["sources"] = sorted(set(row["sources"]) | {x["source"] for x in roles})
        row["notes"] = _notes(sid, r, pop, row)
        rows.append(row)

    # Al-Jubail (Al-Ahsa): primary 9,994 with no R1a settlement (crosswalk: none)
    p = pilot.loc[pilot.name_en.str.startswith("Al-Jubail") & (pilot.governorate == "Al-'Aḥsā'")]
    if len(p) != 1:
        raise SystemExit("pilot Al-Jubail (Al-Ahsa) row not found")
    pr = p.iloc[0]
    rows.append(
        {
            "name_ar": "الجبيل",
            "name_en": "Al-Jubail (Al-Ahsa)",
            "region": "eastern",
            "governorate": "Al-Ahsa",
            "governorate_ar": "الأحساء",
            "is_governorate_centre": False,
            "osm_id": int(pr.osm_id),
            "osm_type": pr.osm_type,
            "lat": float(pr.lat),
            "lon": float(pr.lon),
            "population": 9994,
            "pop_source": "S-cp2-gastat-008",
            "pop_year": 2022,
            "pop_type": "official",
            "pop_source_status": "verified",
            "tag_10k": False,
            "tag_5k": True,
            "dist_existing_km": _road(pr.dist_existing_km),
            "nearest_existing": _clean(pr.nearest_existing),
            "road_min_existing": None,
            "dist_committed_km": None,
            "nearest_committed": None,
            "nearest_committed_station": None,
            "road_min_committed": None,
            "dist_metro_km": _road(pr.dist_metro_km),
            "nearest_metro": _clean(pr.nearest_metro),
            "road_min_metro": None,
            "nearest_metro_tier": 1,
            "road_min_method": "pending skims",
            "dist_method": "haversine to the station point (pilot, A-screen-pilot-002)",
            "economic_roles": [],
            "terrain_class": None,
            "screened": True,
            "exclusion_reason": None,
            "sources": ["S-cp2-gastat-008", "S-eastern-004"],
            "fixture": False,
            "notes": (
                "Primary export 'Aljabil' 9,994 (crosswalk: none, no R1a settlement). Coordinates "
                "and osm_id from the pilot register (OSM place=neighbourhood way, S-eastern-004); "
                "the name is shared with Al-Jubail (E03, Al-Jubayl governorate). Under 10k: no "
                "grid check needed. Distances are haversine to the pilot station point; committed "
                "distance not computed."
            ),
        }
    )
    return rows


def _notes(sid: str, r, pop: dict, row: dict) -> str | None:
    parts: list[str] = []
    if sid == "KSA-ST-00003":
        parts.append(
            "Combined row: Al-Hofuf 430,105 + Al-Mubarraz 299,501 (primary export, S-cp2-gastat-008; "
            "crosswalk combined_with). The governorate centre; the OSM node is 'Al-Hofuf'."
        )
    if sid == "KSA-ST-01101":
        parts.append(
            "Primary export labels this city 'Rahimah' (57,030); the crosswalk matches it to the "
            "Ra's Tannurah node. Opus judgement item 3 (governorate centre)."
        )
    if sid == "KSA-ST-07367":
        parts.append(
            "Governorate centre (Al-Udayd). R1a grid value 0: not used. The GASTAT governorate "
            "total (8,635) is not a town figure. Coordinates from R1a; population not sourced; "
            "geo-verify pending (see docs/regions/eastern.md §6)."
        )
    if row.get("pop_type") == "grid":
        parts.append(
            "Grid-only (WorldPop 2020 constrained, unverified): a value, not a GASTAT figure."
        )
    if row.get("pop_type") == "derived":
        parts.append(
            "Population from the OSM place population tag (year as tagged, 2010); not tabulated "
            "in the primary GASTAT export; included as derived per rule 2."
        )
    if _clean(r.pop_type) == "derived" and row.get("pop_type") is None:
        parts.append(
            f"OSM place population tag {int(r.population)} is undated (no year), so it is not "
            "used as a figure (A-eastern-005)."
        )
    return " ".join(parts) or None


def write(rows: list[dict], gov_total: int, gov_detail: dict[str, int]) -> pd.DataFrame:
    for row in rows:
        RegionRow.model_validate(row)  # raises on any schema breach
    df = pd.DataFrame(rows)
    df = df.sort_values(["is_governorate_centre", "name_en"], ascending=[False, True]).reset_index(
        drop=True
    )
    df["osm_id"] = df["osm_id"].astype("Int64")
    for c in ("population", "pop_year", "nearest_metro_tier"):
        df[c] = df[c].astype("Int64")
    meta = {
        b"governorates_gastat": str(GOVERNORATES_GASTAT).encode(),
        b"governorates_listed": str(GOVERNORATES_LISTED).encode(),
        b"gastat_governorate_sum_2022": str(gov_total).encode(),
    }
    table = pa.Table.from_pandas(df, preserve_index=False)
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT_PARQUET)
    csv = df.copy()
    for c in ("economic_roles", "sources"):
        csv[c] = csv[c].apply(lambda v: json.dumps(v, ensure_ascii=False))
    csv.to_csv(OUT_CSV, index=False)
    return df


def main() -> None:
    settlements = pd.read_parquet(SETTLEMENTS)
    east = settlements.loc[settlements.region == "eastern"].copy()
    pilot = pd.read_parquet(PILOT)
    gov_total, gov_detail = gastat_control_total()
    rows = build_rows(east, pilot)
    df = write(rows, gov_total, gov_detail)
    write_md(df, gov_total, gov_detail)
    print(f"rows={len(df)} centres={int(df.is_governorate_centre.sum())}")
    print(f"governorates_in_rows={df.governorate.nunique()} gov_sum_2022={gov_total}")
    print(
        f"tag_10k={int(df.tag_10k.sum())} tag_5k={int(df.tag_5k.sum())} "
        f"screened_false={int((~df.screened).sum())}"
    )


def _fmt(v, nd: int = 1) -> str:
    v = _clean(v)
    if v is None:
        return "—"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def _pop_cell(r) -> str:
    p = _clean(r.population)
    if p is None:
        return "— (no sourced figure)"
    return f"{int(p):,} ({r.pop_type}, {r.pop_source_status})"


def write_md(df: pd.DataFrame, gov_total: int, gov_detail: dict[str, int]) -> None:
    n = len(df)
    n10 = int(df.tag_10k.sum())
    n5 = int(df.tag_5k.sum())
    off10 = int(((df.pop_type == "official") & df.tag_10k).sum())
    der10 = int(((df.pop_type == "derived") & df.tag_10k).sum())
    grid_rows = df[df.pop_type == "grid"]
    grid_gated = grid_rows[grid_rows.exclusion_reason.fillna("").str.contains("uncorroborated")]
    excl = df[~df.screened]
    role_counts: dict[str, int] = {}
    for lst in df.economic_roles:
        for x in lst:
            role_counts[x["role"]] = role_counts.get(x["role"], 0) + 1
    gov_rows = df[df.is_governorate_centre].sort_values("governorate")
    lines: list[str] = []
    w = lines.append
    w(
        "> **Document version:** docs/regions/eastern.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_EASTERN) | Status: draft"
    )
    w("")
    w("# Eastern Province (المنطقة الشرقية): region register R2 (slug `eastern`)")
    w("")
    w(
        "**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. No modelled output appears in this file."
    )
    w("")
    w(
        "Registers: `cities/ksa/regions/eastern.parquet` and `eastern.csv` (same rows, same order). Built by `screening/sweeps/eastern/build.py` from the R1a settlement universe (`cities/ksa/zones/settlements.parquet`), the R1a economic nodes and the primary GASTAT exports. Register values were not typed in by hand."
    )
    w("")
    w("## 1. Governorate count")
    w("")
    w("| item | value | source |")
    w("|---|---|---|")
    w(
        f"| `governorates_gastat` | **{GOVERNORATES_GASTAT}** Eastern rows in the 150-row GASTAT primary list (Census 2022 TA1 governorate export) | S-cp2-gastat-007; S-073 (150 governorate rows) |"
    )
    w(
        f"| `governorates_listed` | **{GOVERNORATES_LISTED}** (one centre row per GASTAT governorate; the register has {df.governorate.nunique()} distinct governorates) | this register |"
    )
    w(
        "| count in Arabic secondary sources | 13 (Al-Bayda listed as a 13th) | S-eastern-003 (Saudipedia, Arabic) |"
    )
    w("")
    w(
        f"**Discrepancy, written both ways:** Al-Bayda (البيضاء) appears in the Arabic secondary list (S-eastern-003) but is not one of the 150 GASTAT governorate rows (S-cp2-gastat-007), so it is an excluded row (`screened = false`; A-eastern-004). Counts reconcile to GASTAT (12 = 12). The 12 GASTAT governorate totals sum to **{gov_total:,}**, equal to the Eastern regional total of 5,125,254 (S-cp2-gastat-007; S-cp2-gastat-003). Open for Opus (item 1)."
    )
    w("")
    w(
        "| governorate (EN) | governorate (AR) | GASTAT 2022 total | centre row (name) | centre population |"
    )
    w("|---|---|---|---|---|")
    for _, r in gov_rows.iterrows():
        key = r.governorate
        tot = next((v for k, v in gov_detail.items() if GOV[k][0] == key), None)
        w(f"| {key} | {r.governorate_ar} | {tot:,} | {r.name_en} | {_pop_cell(r)} |")
    w("")
    w("## 2. Counts")
    w("")
    w(
        f"- Rows: **{n}** ({len(gov_rows)} governorate centres; {n - len(gov_rows)} other rows: towns at or above 5,000 and {len(excl)} excluded rows)."
    )
    w(
        f"- Towns at or above 10,000 (`tag_10k`): **{n10}** = {off10} official (GASTAT primary, verified) + {der10} derived (OSM place tag, secondary) + 0 grid (no grid row passes the corroboration gate)."
    )
    w(f"- Towns at or above 5,000 (`tag_5k`, sensitivity): **{n5}**.")
    w(
        f"- Grid-only rows (WorldPop 2020, unverified): {len(grid_rows)}; of these {len(grid_gated)} are at or above 10,000 and uncorroborated, so `tag_10k = false` (exclusion_reason set, screened true). Only Udhailiyah has a second method (gastat2010_city_growth, 9,409 vs grid 14,071: 33 % apart, over the 30 % band), so it is not corroborated."
    )
    w(
        f"- Universe settlements in the region: {int(len(pd.read_parquet(SETTLEMENTS).query('region == "eastern"')))}; 56 are register rows (plus the pilot's Al-Jubail row, which has no universe settlement); the rest are below 5,000 (or undated) and are not register rows, counted here only."
    )
    w(f"- `screened = false`: {len(excl)} rows (section 4).")
    w("- `pilot_sample` and `threshold_50k`: null in this R2 register.")
    w("")
    w("## 3. Register table")
    w("")
    w(
        "Population cell: figure (pop_type, pop_source_status). Distances in km (haversine to the nearest station, R1a); road minutes are OSRM car (R1a skims). `—` = not available."
    )
    w("")
    w(
        "| # | name (EN) | name (AR) | governorate | centre | population | ≥10k | ≥5k | screened | existing: km / road min | metro: nearest, tier, km | committed: km / road min | roles (sourced) |"
    )
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(df.itertuples(index=False), 1):
        metro = f"{r.nearest_metro} / T{_fmt(r.nearest_metro_tier, 0)} / {_fmt(r.dist_metro_km)}"
        ex = f"{_fmt(r.dist_existing_km)} / {_fmt(r.road_min_existing)}"
        cm = f"{_fmt(r.dist_committed_km)} / {_fmt(r.road_min_committed)}"
        roles = ", ".join(x["role"] for x in r.economic_roles) or "none sourced"
        w(
            f"| {i} | {r.name_en} | {r.name_ar} | {r.governorate} | {'yes' if r.is_governorate_centre else 'no'} | {_pop_cell(r)} | {'yes' if r.tag_10k else 'no'} | {'yes' if r.tag_5k else 'no'} | {'yes' if r.screened else 'no'} | {ex} | {metro} | {cm} | {roles} |"
        )
    w("")
    w("## 4. Exclusions and rows not carried")
    w("")
    w("| name | governorate | reason |")
    w("|---|---|---|")
    for r in excl.itertuples(index=False):
        w(f"| {r.name_en} | {r.governorate} | {r.exclusion_reason} |")
    w("")
    w(
        "Not register rows (counted, not screened): the other universe settlements below 5,000 or without a sourced population. Rows with no sourced population stay `population = null`; the funnel must not read them as zero."
    )
    w("")
    w("## 5. Economic roles")
    w("")
    w(
        "Every role names the source that ties it to that town (R1a economic nodes, `source_id`; S-eastern-001 and S-eastern-009 for the two military roles). Counts: "
        + ", ".join(f"{k} {v}" for k, v in sorted(role_counts.items()))
        + "."
    )
    w("")
    w(
        "Not carried as roles: Ras Al-Khair port, mining and industrial city (no register row; R1a nodes located False or no town row); Al-Ruqi, Al-Salmi, Al-Batha and Salwa border posts (no town row; Salwa unverified in R1a). Settlement rows with no node get no role."
    )
    w("")
    w("## 6. Geo-verify step (record-only)")
    w("")
    w(
        "Run: `screening.geo_verify.cli estimate --which no-pop --region eastern --seed 1` (method log `geo-est-c172b6d4`, `geo-est-4166a87b`, `geo-est-2628554c`). **The CLI reads `cities/ksa/regions/pilot-*.parquet` only**, so it evaluated the three pilot rows, not this register (a CLI change is needed for R2; not made here, shared code). Results, mapped to the R2 rows by coordinate:"
    )
    w("")
    w(
        "- Ras Tanura (pilot row, same coordinates as the R2 centre Ra's Tannurah): estimate central 22,923 (range 7,013–39,756; 6,491 footprint buildings; buildings method 24,925). The point-window grid value there is 21,081, against 6,445 in the R1a allocation (A-r1a-004): the two grid methods disagree at this point. Record-only (the back-test gate fails both estimators, GEO_VERIFY); not used. The sourced figure stays 57,030 (primary export)."
    )
    w(
        "- Al-Udayd (centre): no footprint cluster (0 buildings). No estimate. Population stays null."
    )
    w("- Al-Bayda: no footprint cluster (0 buildings). No estimate. Row excluded.")
    w(
        "- Stations and planned stops: not in this step (no station candidates for the Eastern Province in `station_sites.yaml` yet)."
    )
    w("")
    w("## 7. Method and limits")
    w("")
    w(
        "- Populations: GASTAT Census 2022 TA1 primary exports (S-cp2-gastat-007 for governorates, S-cp2-gastat-008 for cities of 5,000 or more), matched by `screening/gastat_crosswalk.yaml` (A-screen-038). Derived: OSM place population tags (S-r1a-210), and only where dated (A-eastern-005). Grid: WorldPop 2020 constrained (S-r1a-505), unverified; grid rows ≥ 10k are gated (A-screen-031 to 033)."
    )
    w(
        "- Distances: haversine to the nearest station (R1a, `dist_existing_km` and `dist_committed_km`) and to the metro reference city node (`dist_metro_km`, A-r1a-009); road minutes OSRM car (`road_min_*`, R1a skims). The committed (GCC railway) station positions are unlocated (R1a flag), so committed distances are approximate and are labelled committed, never existing."
    )
    w(
        "- Terrain: `terrain_class` null for every row (no R1a DEM class for Eastern towns; not guessed)."
    )
    w(
        "- The Al-Jubail (Al-Ahsa) row takes its coordinates from the pilot register (OSM neighbourhood way, S-eastern-004) because the primary export's 'Aljabil' (9,994) has no R1a settlement."
    )
    w(
        "- The Al-Hofuf row is the combined Al-Hofuf 430,105 + Al-Mubarraz 299,501 (crosswalk, A-eastern-003)."
    )
    w("")
    w("## 8. Sources")
    w("")
    w(
        "S-cp2-gastat-007 (governorates, 150 rows), S-cp2-gastat-008 (cities ≥ 5,000, 271 rows + Other), S-cp2-gastat-003 (regional TA9 totals), S-073 (governorate row list), S-cp2-gastat-001 (relayed cross-check only), S-r1a-210 (OSM GCC extract: ids, coordinates, OSM population tags, ODbL), S-r1a-505 (WorldPop 2020 constrained, CC BY 4.0), R1a economic-node sources (S-r1a-*, S-cp1-*), S-eastern-001/003/009 (secondary; roles and military rows), S-eastern-004 (Nominatim object ids for the pilot Al-Jubail row). New ids in `docs/sources/r2-eastern.csv`."
    )
    w("")
    w("## 9. Needs Opus judgement (not resolved by guessing)")
    w("")
    w(
        "1. Governorate count: GASTAT 12 vs Saudipedia 13 (Al-Bayda). Al-Bayda is excluded here; a decision is needed on whether it is a governorate."
    )
    w(
        "2. Al-Hofuf: keep the combined 729,606 row (crosswalk) or split Al-Hofuf (430,105) and Al-Mubarraz (299,501) into two rows (the OSM nodes must then be found)."
    )
    w(
        "3. Ra's Tannurah: the primary export labels this city 'Rahimah' (57,030); matched to the Ra's Tannurah node (crosswalk). Confirm the name and governorate-centre choice."
    )
    w(
        "4. Al-Jubail (Al-Ahsa, 9,994): the primary export figure, the pilot's neighbourhood coordinates and the Al-Jubail (Al-Jubayl) name clash. Confirm the location and whether it is a town."
    )
    w(
        "5. OSM-tag towns (derived, secondary): AL THIYBIA (14,442, counted at 10k), As Saffaniyah, Bani M'en, Mulayjah, Al Marah, the Nuqayrah node: confirm they are not GASTAT-tabulated towns under other names; the 10k count depends on AL THIYBIA. AL THIYBIA (28.12 N, 45.67 E) is placed in the Hafar Al-Batin governorate by the R1a polygon; check the location and governorate before use."
    )
    w(
        "6. Grid rows ≥ 10k (Ar Rabi'iyah, Aziziyah, Sanabis, As Su'ayyirah, Darin and others): none passes the corroboration gate. The 2010-growth method (A-screen-035) was run only for Udhailiyah."
    )
    w(
        "7. Al-Khobar vs Ath-Thuqbah: Thuqbah is 248,888 (GASTAT city) inside the Dammam–Khobar–Dhahran metro. The commuter-belt decision (R2) decides whether it is a separate row."
    )
    w(
        "8. Military roles (King Khalid Military City; Dhahran air base): the first is a census row, the second a search extract (S-eastern-009). Confirm."
    )
    w("9. Terrain class (R1a DEM classification) is null for all Eastern rows.")
    w(
        "10. Governorate-centre rows: Al-Udayd (no sourced town figure; GASTAT governorate total 8,635 is not a town figure)."
    )
    w(
        "11. Schema: `energy` is in the role list; Abqaiq and Ras Tanura are recorded with energy roles where a node exists."
    )
    w("")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
