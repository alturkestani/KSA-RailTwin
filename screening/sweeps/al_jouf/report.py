"""Writes docs/regions/al_jouf.md from cities/ksa/regions/al_jouf.parquet (REGION_AL_JOUF, R2).

The table is generated from the register so the Markdown cannot drift from the Parquet.

uv run python -m screening.sweeps.al_jouf.report
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import typer

ROOT = Path(__file__).resolve().parents[3]
REG = ROOT / "cities/ksa/regions/al_jouf.parquet"
OUT = ROOT / "docs/regions/al_jouf.md"
VERSION = (
    "> **Document version:** docs/regions/al_jouf.md v1.0 | 31 Oct 2026 | Author: region-scout "
    "(REGION_AL_JOUF) | Status: draft\n"
)


def _cell(v: object) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).replace("|", "/")


def _roles(v: object) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    items = list(v)
    return ", ".join(f"{x['role']} ({x['source']})" for x in items)


def table(df: pd.DataFrame) -> str:
    head = (
        "| # | name (EN) | name (AR) | governorate | population | pop_type / status | tag_10k | "
        "tag_5k "
        "| screened | existing: km / road min | metro: km / road min | economic roles "
        "| exclusion |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    lines = []
    for i, r in enumerate(df.itertuples(index=False), start=1):
        existing = f"{_cell(r.dist_existing_km)} / {_cell(r.road_min_existing)}"
        metro = f"{_cell(r.dist_metro_km)} / {_cell(r.road_min_metro)}"
        status = f"{r.pop_type} / {r.pop_source_status}"
        lines.append(
            f"| {i} | {_cell(r.name_en)} | {_cell(r.name_ar)} | {_cell(r.governorate)} "
            f"| {_cell(r.population)} | {status} | {'yes' if r.tag_10k else 'no'} "
            f"| {'yes' if r.tag_5k else 'no'} | {'yes' if r.screened else 'no'} "
            f"| {existing} | {metro} | {_roles(r.economic_roles)} | {_cell(r.exclusion_reason)} |"
        )
    return head + "\n".join(lines) + "\n"


def main_text(df: pd.DataFrame, meta: dict[str, str]) -> str:
    n = len(df)
    n10 = int(df.tag_10k.sum())
    n5 = int(df.tag_5k.sum())
    official = int((df.pop_type == "official").sum())
    grid = int((df.pop_type == "grid").sum())
    centres = int(df.is_governorate_centre.sum())
    n5_official = int(((df.pop_type == "official") & df.tag_5k).sum())
    n5_grid = int(((df.pop_type == "grid") & df.tag_5k).sum())
    grid_10k = int(((df.pop_type == "grid") & (df.population >= 10_000)).sum())
    screened = int(df.screened.sum())
    below5 = int((~df.screened).sum())
    gov_names = sorted(df.governorate.unique())
    parts = [
        VERSION,
        "# Region register: Al-Jouf (الجوف), slug `al_jouf` (REGION_AL_JOUF, R2)\n",
        "**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario "
        "comparison, "
        "not a forecast.\n",
        "Full region sweep (R2) built from the R1a settlement universe with the GASTAT primary "
        "Census 2022 "
        "exports applied (CP2 P1a addendum 2). Access date for every source: **31 Oct 2026** "
        "(Asia/Riyadh). "
        "Files: `cities/ksa/regions/al_jouf.parquet` and `.csv` (same rows, same order; "
        "validated with "
        "`screening.region_sweep validate --strict`); sources `docs/sources/r2-al_jouf.csv`; "
        "assumptions "
        "`docs/assumptions-r2-al_jouf.md`; build `screening/sweeps/al_jouf/build.py`; this table "
        "from "
        "`screening/sweeps/al_jouf/report.py`.\n",
        "## Header: governorate count\n",
        "- `governorates_gastat`: **4** (GASTAT Census 2022 TA1 primary governorate export, "
        "S-cp2-gastat-007: "
        "Sakaka 236,669; Al Qurayyat 195,016; Tubarjal 109,796; Dawamat Al Jandal 54,341 "
        "(governorate totals, "
        "not used for town rows). Region membership of the four names comes from citypopulation.de "
        "(S-al_jouf-002, secondary); GASTAT's own region-membership table was not reachable.)",
        "- `governorates_listed`: **4**, the distinct governorates in the rows: "
        + ", ".join(gov_names)
        + ".",
        "- Conflict, not resolved: Wikipedia and Saudipedia's Emirate page say **3** governorates "
        "(S-al_jouf-003, S-al_jouf-004, secondary, search summaries). The count of 4 matches the "
        "census list "
        "and the Tabarjal page; see Needs Opus judgement.\n",
        "## Counts\n",
        f"- Rows: **{n}** (every R1a settlement of the region, one row each; no OSM id "
        "duplicated).",
        f"- Governorate centres (each has a row): **{centres}**.",
        f"- Towns at or above 10,000 (`tag_10k`): **{n10}**, all GASTAT primary (official, "
        "verified). "
        f"Grid-only rows at or above 10,000 that fail the corroboration gate: **{grid_10k}**, "
        "`tag_10k` false.",
        f"- Towns at or above 5,000 (`tag_5k`, sensitivity): **{n5}** (official {n5_official}, "
        f"grid {n5_grid}). **Ghata (GASTAT 2022: 6,653) is missing; see Gaps.**",
        f"- Population basis: official (GASTAT primary, verified) {official} rows; grid "
        f"(WorldPop 2020, unverified) {grid} rows.",
        f"- Screened: {screened} rows; excluded below 5,000 with no sourced economic role: "
        f"{below5} rows.\n",
        "## Gaps (must close before R2 is done)\n",
        "- **Ghata** (Al-Qurayyat governorate; GASTAT Census 2022 primary city "
        "table: **6,653**, "
        "S-cp2-gastat-008; membership S-al_jouf-002). It has no row because no coordinate source "
        "was found: "
        "the R1a name match gave the name to Al Ghat (Riyadh, KSA-ST-01141), the local OSM "
        "extract has no object "
        "named Ghata in Latin or الغطا spellings (S-al_jouf-011). Candidate, not confirmed: "
        "OSM village "
        "غطي / Ghutti, node 1236744649 (31.266538 N, 37.527451 E), in the box and in Al-Qurayyat; "
        "citypopulation.de writes Ghata as غطى. Nominatim (8 queries: 2 unbounded, 6 bounded "
        "to the Al-Jouf box), Wikidata and the 2010 list "
        "return nothing (S-al_jouf-010). A row needs a located source (GASTAT locality table or "
        "a located OSM/"
        "GeoNames entry). Until then the ≥ 5,000 count is one short.",
        "- Terrain class: not assessed (no DEM read; disk gate; A-al_jouf-002). Column null on "
        "every row.",
        "- Hajj/Umrah, border crossing (Tubarjal) and other roles: no source in the repository; "
        "not recorded.",
        "- Geo-verify `estimate`: not run (it downloads building footprints and Sentinel-2 "
        "windows, outside the "
        "R2 disk gate). The pilot's record-only GEO_VERIFY notes are carried in the notes for the "
        "rows they cover.\n",
        "## Population rule applied\n",
        "1. GASTAT primary city table (S-cp2-gastat-008, 271 cities of 5,000+): official, "
        "verified, year 2022. "
        "The DataPulse relayed figures are identical for these rows (cross-check only).",
        "2. OSM `place` population tags are not 2022 figures (A-al_jouf-004). The two dated 2010 "
        "equal the "
        "Census 2010 list (S-cp2-gastat-005); three undated tags are not used either.",
        "3. Otherwise WorldPop 2020 (100 m, constrained; S-r1a-505): `pop_type: grid`, "
        "`pop_source_status: "
        "unverified`, `tag_10k` false (no second method run: `pop_corroboration` null; "
        "A-screen-031/032). "
        "A grid row at or above 5,000 is shown for the sensitivity and noted as presumed below "
        "5,000 in 2022 "
        "(A-al_jouf-003). The grid is not a GASTAT value and is never corrected in `population`.\n",
        "## Distances and roads\n",
        "- Existing and metro straight-line distances (`dist_*_km`) are from the R1a universe: "
        "`dist_existing_km` "
        "is haversine to the nearest existing station on the SAR North passenger line (checked "
        "for Sakaka: 51.03 "
        "km to `sar-north-passenger:al-jawf`); `dist_metro_km` is haversine to the nearest metro "
        "city (tier from "
        "A-screen-013; Tabuk tier 2, Buraidah tier 2).",
        "- Road minutes (`road_min_*`) are the R1a OSRM table, MLD car profile, free flow, "
        "uncalibrated (S-r1a-809).",
        "- Committed distances: nearest committed station is the Landbridge stop `dawadmi` "
        "(planned, "
        "committed layer per `cities/ksa/lines/landbridge.yaml`) or the GCC railway's Kuwait "
        "border proxy, both "
        "with unlocated sites in R1a; the distances are to the alignment as R1a computed them. "
        "No committed line "
        "is called existing.\n",
        "## Exclusions\n",
        "- Below 5,000 with no sourced economic role: " + str(below5) + " rows, `screened: "
        "false`, reason given per row.",
        "- Grid-only at or above 10,000, uncorroborated (`tag_10k` false, `screened` true): "
        f"{grid_10k} rows (At Tuwayr, Al Hadithah, Al 'Isawiyah).",
        "- No row was excluded as a duplicate or outside the region polygon.\n",
        "## Sources (ids in `docs/sources/r2-al_jouf.csv` or `docs/sources/index.csv`)\n",
        "- Population: S-cp2-gastat-008 (GASTAT Census 2022 TA1 primary, cities of 5,000+), "
        "S-cp2-gastat-007 "
        "(governorates), S-cp2-gastat-005 (Census 2010 cities), S-r1a-505 (WorldPop 2020 100 m "
        "constrained), "
        "S-cp2-gastat-001 (DataPulse, cross-check only).",
        "- Coordinates and OSM ids: S-r1a-210 (OSM GCC extract, element ids), S-al_jouf-006 "
        "(pilot Overpass "
        "place nodes), S-al_jouf-011 (filtered copy used for the checks).",
        "- Lines and roads: S-018 (SAR North places), S-r1a-809 (OSRM skims).",
        "- Economic roles: S-cp1-100 and S-r1a-210 (airports, GACA report Feb 2025), S-r1a-221, "
        "S-r1a-222 "
        "(university), S-r1a-204 (MODON industrial city), S-al_jouf-008 (Sakaka capital), "
        "S-al_jouf-002 "
        "(governorate membership), S-al_jouf-009 (Dumat heritage and tourism, Arab News 2022, "
        "secondary).",
        "- Counts and conflicts: S-al_jouf-003, S-al_jouf-004 (governorate count, secondary); "
        "S-al_jouf-005 "
        "(GASTAT portal, unverified).\n",
        "## Needs Opus judgement (not resolved by guessing)\n",
        "1. Governorate count 3 or 4 (conflict above). The register uses 4, which the GASTAT "
        "primary names support.",
        "2. Ghata: find a located source (GASTAT locality table or a located OSM/GeoNames "
        "entry), then add the row.",
        "3. Al-Hadithah (OSM node 1236744849, grid 11,301): census name Al-Ḥadīthah al-Qadīmah "
        "per S-al_jouf-002 "
        "(not in the 5,000+ table, so presumed below 5,000). Also the SAR North terminus 'Al "
        "Haditha' (S-018). "
        "Which place is the terminus, and is the grid row a double count?",
        "4. Al 'Isawiyah (grid 15,474 against an OSM 2010 tag of 5,629, grid ÷ 2010 = 2.7): "
        "presumed below 5,000 in "
        "2022, grid unverified. Keep as a sensitivity row or set population to null?",
        "5. Jouf station (`sar-north-passenger:al-jawf`, 29.648 N, 39.837 E): 17.8 km from "
        "Dawamat Al Jandal and "
        "51 km from Sakaka, the nearest station for most rows. Confirm it is the region's main "
        "station.",
        "6. Sakaka industrial city: the MODON Al-Jouf oasis is unlocated (S-r1a-204); its town "
        "link is the MODON "
        "table's nearest-town field (R1a). Keep the role or drop it?",
        "7. Tubarjal border crossing and Al Qurayyat industry: searched, not sourced; not "
        "recorded.",
        "8. Far (>100 km) stratum: the sample logic is out of scope for R2; no pilot sample "
        "flags are set.",
        "9. Corroboration gate: the 2010-growth method (`gastat2010_city_growth`) applies only "
        "to matched towns; "
        "no Al-Jouf grid row is matched, so no grid row passes the 10,000 gate.\n",
        "## Notes on the rows\n",
        "- R1a's `control_total_flag` marks the region's grid sum above its residual "
        "(`runs/gastat/primary/"
        "control_total.csv`, al_jouf: grid 86,611 + tabulated unmatched 20,208 against a "
        "residual of 67,886). "
        "Reporting only; the flags are in the notes of the rows they cover.",
        "- Terrain (`terrain_class`): null on every row (A-al_jouf-002).\n",
        "Screening input, not a forecast. Label: synthetic demand, uncalibrated: scenario "
        "comparison, not a forecast.\n",
        "## Table\n",
        "Sorted by population (largest first; null last). `existing` and `metro` are km / road "
        "minutes "
        "(road minutes are free-flow OSRM).\n",
        table(df),
    ]
    return "\n".join(parts)


app = typer.Typer(add_completion=False, help=__doc__)


@app.callback()
def main() -> None:
    """Markdown report for the Al-Jouf register."""


@app.command()
def report() -> None:
    """Write docs/regions/al_jouf.md."""
    df = pd.read_parquet(REG)
    df = df.sort_values("population", ascending=False, na_position="last").reset_index(drop=True)
    meta = {k.decode(): v.decode() for k, v in (pq.read_schema(REG).metadata or {}).items()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(main_text(df, meta), encoding="utf-8")
    typer.echo(f"wrote {OUT.relative_to(ROOT)}: {len(df)} rows")


if __name__ == "__main__":
    app()
