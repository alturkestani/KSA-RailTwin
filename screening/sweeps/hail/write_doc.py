# ruff: noqa: E501
# Long prose and source strings, as in screening/pilot_builders.
"""Write docs/regions/hail.md from the Hail register (REGION_HAIL).

The table, the counts and the exclusion tallies are computed from `cities/ksa/regions/hail.parquet` and
the R1a universe, so the document cannot drift from the register. The narrative is fixed text.

Run: uv run python -m screening.sweeps.hail.write_doc
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from screening.sweeps.hail import build_register

ROOT = Path(__file__).resolve().parents[3]
REG = ROOT / "cities/ksa/regions/hail.parquet"
SETTLEMENTS = ROOT / "cities/ksa/zones/settlements.parquet"
OUT = ROOT / "docs/regions/hail.md"

HEADER = (
    "> **Document version:** docs/regions/hail.md v1.0 | 31 Oct 2026 | Author: region-scout "
    "(REGION_HAIL, track r2-hail) | Status: draft\n"
)


def _pop_label(r: pd.Series) -> str:
    return f"{int(r['population']):,} ({r['pop_type']}, {r['pop_source_status']})"


def _table(df: pd.DataFrame) -> str:
    lines = [
        "| # | name (AR) | name (EN) | governorate | centre | population (type, status) | pop source | tag 10k | tag 5k | nearest existing | road min | nearest metro (tier) | road min to metro | economic roles |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        roles = (
            "; ".join(f"{x['role']} ({x['source']})" for x in r["economic_roles"]) or "none sourced"
        )
        lines.append(
            "| {i} | {ar} | {en} | {gov} | {c} | {pop} | {src} | {t10} | {t5} | {ex} | {rmin} | {met} ({tier}) | {rmm} | {roles} |".format(
                i=i,
                ar=r["name_ar"],
                en=r["name_en"],
                gov=r["governorate"],
                c="Y" if r["is_governorate_centre"] else "N",
                pop=_pop_label(r),
                src=r["pop_source"],
                t10="Y" if r["tag_10k"] else "N",
                t5="Y" if r["tag_5k"] else "N",
                ex=r["nearest_existing"],
                rmin=f"{r['road_min_existing']:.1f}",
                met=r["nearest_metro"],
                tier=int(r["nearest_metro_tier"]),
                rmm=f"{r['road_min_metro']:.1f}",
                roles=roles,
            )
        )
    return "\n".join(lines)


def _not_written(reg_ids: set[str]) -> tuple[pd.DataFrame, dict[str, int], int, list[str]]:
    """Universe rows not in the register, on the resolved figures (relayed precedence applied).

    Returns (excluded rows, place tally, largest resolved excluded population, names of the excluded
    towns whose grid or OSM figure is >= 5,000 but whose relayed GASTAT figure is below it).
    """
    s = pd.read_parquet(SETTLEMENTS)
    h = s[s["region"] == "hail"]
    resolved, overridden = build_register._apply_relayed_precedence(h)
    excluded = resolved[~resolved["settlement_id"].isin(reg_ids)]
    big = excluded.loc[excluded["population"] >= 5000, "name_en"].tolist()
    assert not big, f"unexpected excluded rows at or above 5,000 on the resolved figure: {big}"
    tally = excluded["place"].value_counts().to_dict()
    overridden_names = [r["name_en"] for _, r in h.iterrows() if r["settlement_id"] in overridden]
    largest = int(excluded["population"].max())
    return excluded, tally, largest, overridden_names


def build() -> str:
    df = pd.read_parquet(REG).sort_values("population", ascending=False)
    n_rows = len(df)
    n_centre = int(df["is_governorate_centre"].sum())
    n_10k = int(df["tag_10k"].sum())
    n_5k = int(df["tag_5k"].sum())
    n_grid = int((df["pop_type"] == "grid").sum())
    n_grid_10k = int(((df["pop_type"] == "grid") & (df["population"] >= 10_000)).sum())
    n_primary = int((df["pop_source_status"] == "verified").sum())
    n_secondary = int((df["pop_source_status"] == "secondary").sum())
    n_unverified = int((df["pop_source_status"] == "unverified").sum())
    n_roles = int(df["economic_roles"].apply(len).sum())
    universe = int(len(pd.read_parquet(SETTLEMENTS).query("region == 'hail'")))
    reg_ids = set(build_register.CENTRES) | build_register.NON_CENTRE_5K
    _, below, largest_excluded, overridden_names = _not_written(reg_ids)
    not_written = universe - n_rows
    below_text = ", ".join(f"{k} {v}" for k, v in sorted(below.items(), key=lambda kv: -kv[1]))
    gov_list = ", ".join(sorted(df.loc[df["is_governorate_centre"], "governorate"].unique()))
    overridden_text = ", ".join(overridden_names)
    n_overridden = len(overridden_names)
    return f"""{HEADER}
# Region sweep: Ḥā'il (حائل), slug `hail` (REGION_HAIL, R2)

Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.

Register: `cities/ksa/regions/hail.parquet` and `.csv` ({n_rows} rows). Validated with `uv run python -m screening.region_sweep validate --strict`, header `governorates_gastat: 9`, `governorates_listed: 9`. Access date for every source: 2026-10-31 (Asia/Riyadh) unless the source table says otherwise. The built script is `screening/sweeps/hail/build_register.py`; this document is written by `screening/sweeps/hail/write_doc.py` from the register.

## 1. Governorate count

- **GASTAT governorates in Ḥā'il: 9, reconciled.** The primary GASTAT Census 2022 TA1 governorate export (S-cp2-gastat-007) carries the nine names of the working list (S-073): Ḥā'il 498,575; Al-Ḥā'īṭ (Al Hait) 74,596; Baq'ā' (Baqa) 56,362; Ash-Shamlī 20,946; Simīrā' 19,563; As-Sulaymī 17,343; Mawqaq 16,835; Al-Ghazalah 12,767; Ash-Shanān (Ash Shinan) 29,419. The sum is **746,406**, equal to the Ḥā'il region total in S-hail-001, so the set is complete (S-hail-009, derived). The primary export has no region column, so the membership of each name in Ḥā'il is S-073 (secondary) checked by that sum.
- Every governorate has its centre as a row: {gov_list}.
- Nationally, the primary table has 150 governorate rows; the working list has 152 (150 plus two flagged rows, Abanat and Al-Bayda, in Qassim and the Eastern Province). That discrepancy is for the coverage audit, not this sweep.
- The primary table also lists a governorate named Turubah (41,769) that is not one of the nine. The Ḥā'il Turubah is a town in the Baq'ā' governorate (see section 6).

## 2. Counts

| measure | count |
|---|---|
| rows in the register | {n_rows} |
| governorate centres | {n_centre} (2 of them below 5,000: Mawqaq, Simīrā', `screened: false`, kept for coverage) |
| rows with population ≥ 10,000 (`tag_10k`) | {n_10k} (Ḥā'il; Baq'ā'; Ash-Shanān on a secondary figure; Al Malwi on a doubtful OSM tag) |
| rows with population ≥ 5,000 (`tag_5k`) | {n_5k} |
| population type `grid` (WorldPop, unverified) | {n_grid}; of these ≥ 10,000: {n_grid_10k} (no grid row passes the 10k test, so no corroboration was needed; A-screen-031) |
| population source verified (GASTAT read) | {n_primary} |
| population source secondary (relayed or OSM tag) | {n_secondary} |
| population source unverified (grid) | {n_unverified} |
| economic roles, each with a source | {n_roles} (see section 5) |
| R1a settlement universe rows in the region | {universe} |

## 3. Register table

Sorted by population. `pop source`: `S-cp2-gastat-008` = GASTAT Census 2022 primary city table; `S-hail-001` = citypopulation.de relayed (secondary); `S-r1a-506` = WorldPop 2020 grid (unverified); `S-hail-003` = OSM population tag. Road minutes: OSRM car profile, free flow, uncalibrated (S-r1a-809). Distances are straight-line (haversine) in the register (`dist_*_km`).

{_table(df)}

## 4. Exclusions

- **Screened false (kept for coverage):** Mawqaq (3,148, secondary) and Simīrā' (3,105, secondary): governorate centres below 5,000 with no sourced economic role.
- **Not written (below 5,000 and not a governorate centre):** {not_written} of the {universe} universe rows for the region are not in the register: {below_text}. They are below the 5,000 sensitivity threshold (A-screen-002), so they are not tagged. The largest excluded resolved population is {largest_excluded:,}. {n_overridden} R1a universe rows carry a grid or OSM figure that the relayed GASTAT table (S-hail-001) replaces by name and governorate ({overridden_text}); the relayed figure takes precedence (official > derived > grid), and those below 5,000 are not written. No other excluded row has a grid or OSM figure at or above 5,000 (checked in the builder). None has a sourced economic role.
- No duplicate was removed. Ash-Shanān's census figure is the S-hail-001 figure; its universe row is kept once.

## 5. Economic roles

Roles were assessed against the 168 R1a economic nodes (`cities/ksa/zones/economic_nodes.parquet`), five of which are located in Ḥā'il: the Ḥā'il Regional Airport (GACA, S-cp1-100), the Ḥā'il Industrial City (MODON, S-r1a-204), the Rock Art in the Hail Region (UNESCO, S-hail-005 and S-r1a-205, Wikidata position at region level), the University of Ḥā'il (S-hail-007, S-r1a-221), and the Az Zabirah bauxite mine (Ma'aden; the region is unverified, so no row is assigned; S-r1a-236). The roles in the register are the ones tied to a town: Ḥā'il city (administrative, airport, industrial city, university) and Jubbah (heritage, placed at Jabal Umm Sinman; S-hail-005). Every other town has no sourced role, and its row says so in `notes`.

## 6. Conflicts and decisions

- **Ash-Shanān 11,560 vs Alshazalah 11,560.** The primary city table has `Alshazalah` at 11,560 (S-cp2-gastat-008), which may be the same place; the crosswalk (`screening/gastat_crosswalk.yaml`) leaves it unmatched and logs the conflict. The row stays on S-hail-001 (secondary), so its ≥ 10k status depends on a secondary figure until the match is decided.
- **Relayed figures beat grid and OSM figures.** Al-Khuṭah (3,355), Al-Ḥalīfah as-Suflā (4,151) and Al-Qā'id (2,913) are in the relayed S-hail-001 table (checked live on the page, 31 Oct 2026). The earlier register used their grid or OSM figures (9,636, 8,990, 5,523) and tagged them at 5k; that was a precedence error, now fixed. They are not written.
- **Turubah.** The Makkah Turubah (28,279, S-cp2-gastat-008) is a different place. The Ḥā'il Turubah row takes `Turba` (8,590, primary); the OSM tag (5,134) conflicts with the census figure, and the census figure is used.
- **Al Ajfar.** Matched by the crosswalk to `Alajfir` (7,518, primary; KSA-ST-00991).
- **Al-Ḥā'īṭ.** OSM spells the node `Al Hayit` (الحايط); matched by coordinates and name, primary 8,289.
- **Population type of the R1a universe.** The 634 grid rows in the universe are `unverified`; the register keeps the grid figure only for towns that have no tabulated or relayed figure, and tags it `grid`. No grid figure is treated as a census figure.
- **Geo-verify.** The pilot GEO_VERIFY estimates for Ash-Shanān, Mawqaq and Simīrā' are carried in `notes` as record-only values (their back-test is above the 30 % gate). They were not re-run in this track: the WorldPop raster and footprint tiles are not in the worktree, and the prompt's disk gate rules out the downloads. Al Malwi and Al Qa'id (OSM tags) have no estimate.

## 7. Needs Opus judgement

1. **Al Malwi (الملوي), 15,000, OSM village tag dated 1950, governorate Al-Ḥā'īṭ at 25.3 N.** It alone passes 10k among the non-centre rows. The tag is doubtful and the position is at the southern edge of the region; decide whether the row stays `tag_10k: true` (A-hail-002), and whether its governorate membership is right.
2. **Ash-Shanān 11,560: match Alshazalah (primary) or keep the secondary figure.** The crosswalk says unmatched; the value coincides.
3. **Grid-only towns and the R1a grid figure for As-Sulaymī.** Ayal Obaid (6,561), Asbatr (6,344), Dhurayghit (5,809), Al Wudayy (5,323) and As-Sulaymī (6,775, the centre; the census places table does not tabulate it) have no GASTAT figure; their figures are the R1a WorldPop grid, not census figures, and they sit only in the 5k sensitivity. Al Malwi (item 1) is the only ≥ 10k row on an OSM tag.
4. **Terrain class** is not measured (A-hail-001); the regional description (S-hail-008) is not a row class.
5. **Membership at the region edge (A-hail-003).** OSM polygons place Al Hulayfah Assofla at 25.99 N, 40.8 E and Al Hayit at 25.99 N, 40.5 E in the Ḥā'il region. The locations are plausible for Al-Ḥā'īṭ but need a check against GASTAT's boundary list.

## 8. Sources

Governorate and population: S-cp2-gastat-007, S-cp2-gastat-008, S-hail-001 (secondary), S-hail-009 (derived sum), S-073 (working list), S-cp2-gastat-001 (cross-check, not used as the value of record). Grid: S-r1a-506 (WorldPop 2020). OSM positions and place tags: S-hail-003, S-r1a-210. Road skims: S-r1a-809. Rail: S-017 (SAR North, existing), S-001 (HHR, existing), S-054 (Landbridge, announced; committed layer, stations unlocated). Economic roles: S-hail-005, S-hail-006, S-hail-007, S-hail-008, S-cp1-100, S-r1a-204, S-r1a-205, S-r1a-221, S-r1a-236. The source index is `docs/sources/index.csv`; the new row is `docs/sources/r2-hail.csv`.

## 9. Layers

Rail layers: the existing lines (SAR North passenger, HHR) are existing; the Landbridge stops are committed (announced/planned, unlocated), and no committed line is called existing. The roads and the distances are straight-line or free-flow estimates, not timetables.
"""


app = typer.Typer(add_completion=False, help=__doc__)


@app.command()
def main(dry_run: bool = typer.Option(False, "--dry-run", help="print, write nothing")) -> None:
    text = build()
    if dry_run:
        typer.echo(text)
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    typer.echo(f"wrote {OUT}")


if __name__ == "__main__":
    app()
