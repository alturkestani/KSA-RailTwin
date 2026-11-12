# ruff: noqa: E501
"""Render docs/regions/asir.md from cities/ksa/regions/asir.parquet (REGION_ASIR).

> **Document version:** screening/sweeps/asir/render_doc.py v1.0 | 31 Oct 2026 | Author: region-scout (r2-asir) | Status: draft

Every count in the document is computed from the register here; the prose is fixed text.
Run after build_register: `.venv/bin/python -m screening.sweeps.asir.render_doc`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import typer

ROOT = Path(__file__).resolve().parents[3]
REG = ROOT / "cities/ksa/regions/asir.parquet"
OUT = ROOT / "docs/regions/asir.md"
app = typer.Typer(add_completion=False, help=__doc__)


def _fmt(v, nd=0) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "null"
    return f"{v:,.{nd}f}"


def _roles(v) -> str:
    return ", ".join(f"{e['role']} ({e['source']})" for e in v) if len(v) else "none sourced"


def _flags(r) -> str:
    f = []
    if r["notes"] and "Needs Opus" in str(r["notes"]):
        f.append("Opus")
    if r["exclusion_reason"] and "grid-only" in str(r["exclusion_reason"]):
        f.append("grid gate")
    if r["pop_type"] == "derived":
        f.append("OSM tag")
    if r["pop_source_status"] == "secondary":
        f.append("secondary")
    if r["population"] is None or pd.isna(r["population"]):
        f.append("no pop")
    return "; ".join(f) or "-"


@app.command()
def main() -> None:
    df = pd.read_parquet(REG)
    head = pq.read_schema(REG).metadata
    g_gastat = head[b"governorates_gastat"].decode()
    g_listed = head[b"governorates_listed"].decode()
    centres = df[df.is_governorate_centre]
    ge10 = df[df.tag_10k]
    ge5 = df[df.tag_5k]
    grid_gate = df[df.exclusion_reason.fillna("").str.contains("grid-only")]
    screened_out = df[~df.screened]
    off = df[df.pop_type == "official"]
    der = df[df.pop_type == "derived"]
    grd = df[df.pop_type == "grid"]
    sec = df[df.pop_source_status == "secondary"]
    unv = df[df.pop_source_status == "unverified"]
    ver = df[df.pop_source_status == "verified"]
    roles_rows = df[df.economic_roles.apply(len) > 0]
    n_roles = int(df.economic_roles.apply(len).sum())
    terr = df[df.terrain_class.notna()]

    rows = []
    for _, r in df.sort_values(
        ["is_governorate_centre", "population"], ascending=[False, False], na_position="last"
    ).iterrows():
        pop = _fmt(r["population"]) if pd.notna(r["population"]) else "null"
        ptype = r["pop_type"] if pd.notna(r["pop_type"]) else "null"
        road = _fmt(r["road_min_existing"], 0) if pd.notna(r["road_min_existing"]) else "pending"
        metro = (
            f"{r['nearest_metro']} / tier {int(r['nearest_metro_tier'])}"
            if pd.notna(r["nearest_metro_tier"])
            else "null"
        )
        terrain = r["terrain_class"] if pd.notna(r["terrain_class"]) else "not assessed"
        rows.append(
            f"| {r['name_en']} | {r['name_ar']} | {r['governorate']} | {'yes' if r['is_governorate_centre'] else 'no'} | "
            f"{pop} | {ptype} / {r['pop_source_status'] if pd.notna(r['pop_source_status']) else 'null'} | "
            f"{'Y' if r['tag_10k'] else 'N'} | {'Y' if r['tag_5k'] else 'N'} | "
            f"{_fmt(r['dist_existing_km'], 1)} / {road} | {r['nearest_committed_station']} | {metro} | "
            f"{_roles(r['economic_roles'])} | {terrain} | {_flags(r)} | {'Y' if r['screened'] else 'N'} |"
        )
    table = "\n".join(rows)

    out = f"""> **Document version:** docs/regions/asir.md v1.0 | 31 Oct 2026 | Author: region-scout (r2-asir, REGION_ASIR) | Status: draft

# Region sweep: Asir (عسير), slug `asir`

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast. Built by `screening/sweeps/asir/build_register.py` (seed 1; deterministic) from the R1a settlement universe and the primary GASTAT Census 2022 TA1 exports. Assumptions: `docs/assumptions-r2-asir.md`. Sources: `docs/sources/r2-asir.csv` and `docs/sources/index.csv`.

## Counts

| item | value | source |
|---|---|---|
| governorates per GASTAT (primary TA1 governorate table, Asir rows) | {g_gastat} | S-cp2-gastat-007 |
| governorates listed in the register (one centre row each) | {g_listed} | this register |
| rows (all, incl. one screened out) | {len(df)} | this register |
| governorate centres | {len(centres)} | this register |
| rows with `tag_10k` (population ≥ 10,000) | {len(ge10)} | A-screen-001 |
| rows with `tag_5k` (population ≥ 5,000, sensitivity) | {len(ge5)} | A-screen-002 |
| grid-only rows ≥ 10,000 held out of `tag_10k` (no corroborating method run) | {len(grid_gate)} | A-screen-032, A-screen-033 |
| rows screened out | {len(screened_out)} | exclusion reason per row |
| populations by type: official / derived / grid / null | {len(off)} / {len(der)} / {len(grd)} / {int(df.population.isna().sum())} | A-screen-031 |
| populations by status: verified / secondary / unverified | {len(ver)} / {len(sec)} / {len(unv)} | source-citation |
| sourced economic roles (rows with at least one) | {n_roles} roles on {len(roles_rows)} towns | S- id per role |
| rows with terrain assessed | {len(terr)} of {len(df)} | see Terrain below |

GASTAT's Asir governorate total: the 18 primary governorate rows sum to 2,024,285, the same as the region total in S-soc-339 and the citypopulation figure in S-asir-001. OSM has 17 Asir governorate polygons (G015 to G031, `cities/ksa/zones/governorates.geojson`); the 18th, Al Amoah, has no polygon (C-r1a-20). Secondary lists differ (17 in Wikipedia, 18 in Saudipedia, per docs/status/pilot-asir.md; secondary, not checked here). This register follows the primary GASTAT table's 18.

Governorate name mapping (GASTAT primary → OSM name used in the register): An Namas → An Nimas; Zahran Al Janub → Dhahran Al Janub; Rijal Al Ma → Rijal Almaa. Other names match.

## Table

Columns: town (EN), town (AR), governorate (OSM name), centre, population, type / status, ≥10k, ≥5k, distance to existing station (km) / road minutes (OSRM, free flow), nearest committed planned station (Landbridge), nearest metro (tier), economic roles (sourced), terrain, flags, screened.

| town | town (AR) | governorate | centre | population | type / status | ≥10k | ≥5k | existing km / road min | committed station | nearest metro (tier) | economic roles | terrain | flags | screened |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
{table}

Distances: `dist_existing_km` is the great-circle distance to the nearest existing station in the R1a set. In this set the only existing stations are on the Haramain line, so every Asir row points to Makkah (A-asir-004 covers the road minutes). `dist_committed_km` is to the Landbridge stations; the names are from `cities/ksa/lines/landbridge.yaml` (S-062). The two names used for Al-Jumum and Muwai are the same planned stops as S-asir-006 (names differ across sources). `dist_metro_km` is to the nearest metro reference node (A-screen-013 tiers); Abha and Khamis Mushait are each a reference node and are in the same metro group.

## Exclusions and screened-out rows

- **Al Harajah** (KSA-ST-00560, 4,540, secondary): screened out. It is the second node named Al Harajah, which containment places in Balqarn, and it is below 5,000. The Al-Harjah seat is KSA-ST-01075 (see the Needs Opus list).
- **Three grid-only towns ≥ 10,000 are held out of `tag_10k`** (`exclusion_reason` "grid-only population, uncorroborated"; they stay screened and `tag_5k` is true): Masloom 12,376, Al Harayr 10,260, King Faisal Military City 10,017. No second method has been run for them, and the 2010-growth method only applies to the matched 2010 cities of more than 5,000.
- No governorate is excluded. The pilot's Balqarn exclusion is resolved: the seat is now Sabt Al 'Alayah (see below).

## Needs Opus judgement (not resolved here)

1. **Al-Harjah seat**: two candidate nodes. KSA-ST-01075 (containment: Al Harjah polygon, grid 435) is used; KSA-ST-00560 (Balqarn polygon, secondary 4,540) is screened out. A-asir-002.
2. **Al Amoah seat**: no OSM polygon (C-r1a-20); the node named Al Amoah lies in the Tathlith polygon. Used as the seat, grid 9,200 (unverified). The GASTAT governorate total 10,969 is not a settlement figure and is not used.
3. **Balqarn seat (Sabt Al 'Alayah)**: the OSM tag 200,000 is rejected (A-asir-003); WorldPop 7,594 used (unverified). The 2010 list has Al-Ulya at 19,956 with no 2022 match in the register, and GASTAT's 2022 ≥ 5,000 table does not list the town. The seat needs a GASTAT locality figure.
4. **Rijal Almaa seat**: grid 288 is implausibly low for a seat (heritage village, S-asir-010). Unverified; needs the GASTAT locality figure.
5. **OSM-tag towns not in GASTAT's ≥ 5,000 table**: Al Bashaer 12,021 (in `tag_10k`), Tabalah 5,670 and Shawas Diyar Bani Was 8,422. Derived (A-asir-001), not GASTAT figures, and their status is secondary. If GASTAT's locality data puts them below 5,000, they drop out of `tag_5k`.
6. **Bisha mining**: the role is exploration only (S-asir-009, a shortlist of exploration sites, secondary). It is not a producing mine and should not be treated as a mining economy.
7. **Khamis Mushait military role**: King Khalid Air Base is cited from secondary sources (S-asir-008). Not verified against a primary source.
8. **Terrain**: only Abha is classed (`escarpment_mountain`, S-asir-007, secondary). The rest are null because no DEM extract was run (disk gate); the pilot's `mixed` default for the other centres was not carried over as an assumption.
9. **Economic roles not sourced**: MODON Asir (industrial city, unlocated; tied to Abha by R1a, S-r1a-204), and the 2010 Al-Ulya town. No port, border, energy or giga-project node lies in Asir in the R1a set.

## Facts and conflicts to carry

- Population conflicts: none left open for an official figure. The R1a universe agrees with the primary table on every official row; the build asserts this for each row with a primary name. Tanumah (Tanawma in the primary table) is 12,442 in both.
- Relayed vs primary: citypopulation.de (S-asir-001) gives the same governorate sum (2,024,285) as the primary table. The DataPulse relayed table (S-cp2-gastat-001) is a cross-check only.
- Pilot (docs/status/pilot-asir.md) corrections: the Balqarn centre (osm 11891866421, Jawf Balqarn, Makkah) is dropped; the pilot's Al-Harjah node (1236690496) is the Balqarn-polygon node and is screened out; the pilot's Tanumah row had no population; it now carries the primary figure 12,442 (Tanawma).

## Sources

See `docs/sources/r2-asir.csv` (S-asir-001 to S-asir-014) and the shared index (`docs/sources/index.csv`) for S-cp2-gastat-001, -005, -007, -008, S-soc-339, S-cp1-100, S-r1a-204, S-r1a-210, S-r1a-221, S-r1a-240, S-062.

Population sources: S-cp2-gastat-008 (primary GASTAT city table; verified, value of record); S-cp2-gastat-007 (primary governorate table; governorate totals not used as town figures); S-asir-001 (citypopulation, GASTAT relayed, secondary); S-asir-012 (WorldPop 2020 grid, unverified); S-asir-013 (OSM tags, secondary).

Facts with no figure: the GASTAT governorate list is verified from the primary table (S-cp2-gastat-007). The GASTAT locality (place under 5,000) figures are not in the primary tables; that gap is the main open item.

Licences: OpenStreetMap contributors (ODbL 1.0) on every OSM-derived row; WorldPop (CC BY 4.0, doi:10.5258/SOTON/WP00684); GASTAT data (use policy; attribution). No new dataset was downloaded for this sweep (every input is registered in `cities/ksa/sources.yaml`).
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote {OUT} ({len(df)} rows)")


if __name__ == "__main__":
    app()
