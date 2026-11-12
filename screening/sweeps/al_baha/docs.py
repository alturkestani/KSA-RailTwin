# ruff: noqa: E501 (the generated Markdown is prose with long lines)
"""Write docs/regions/al_baha.md from cities/ksa/regions/al_baha.parquet (REGION_AL_BAHA).

The table is generated from the register so the Markdown, the Parquet and the CSV cannot drift.
Run after `screening.sweeps.al_baha.build build`:
    uv run python -m screening.sweeps.al_baha.docs
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from common.schemas import TAG_5K, TAG_10K
from screening.sweeps.al_baha.build import AIRPORT, BAHAH_CITY, _km

ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "cities/ksa/regions/al_baha.parquet"
UNIVERSE = ROOT / "cities/ksa/zones/settlements.parquet"
OUT = ROOT / "docs/regions/al_baha.md"

app = typer.Typer(add_completion=False, help=__doc__)

HEADER = (
    "> **Document version:** docs/regions/al_baha.md v1.0 | 31 Oct 2026 | Author: region-scout "
    "(REGION_AL_BAHA) | Status: draft\n"
)


def _cell(v: object) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NA:
        return "–"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:,.1f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v).replace("|", "/")


def _roles(rs: object) -> str:
    if rs is None or len(rs) == 0:
        return "none sourced"
    return "; ".join(f"{r['role']} ({r['source']})" for r in rs)


def table(df: pd.DataFrame) -> str:
    cols = [
        ("Name (EN)", lambda r: r.name_en),
        ("Name (AR)", lambda r: r.name_ar),
        ("Governorate", lambda r: r.governorate),
        ("Centre", lambda r: r.is_governorate_centre),
        ("OSM id (type)", lambda r: f"{_cell(r.osm_id)} ({_cell(r.osm_type)})"),
        ("Lat, lon", lambda r: f"{r.lat:.4f}, {r.lon:.4f}"),
        ("Population", lambda r: _cell(r.population)),
        ("Pop type / status", lambda r: f"{_cell(r.pop_type)} / {_cell(r.pop_source_status)}"),
        ("Pop source", lambda r: _cell(r.pop_source)),
        ("10k / 5k", lambda r: f"{_cell(r.tag_10k)} / {_cell(r.tag_5k)}"),
        (
            "Existing: station, km, road min",
            lambda r: (
                f"{_cell(r.nearest_existing)}, "
                f"{_cell(r.dist_existing_km)} km, {_cell(r.road_min_existing)} min"
            ),
        ),
        (
            "Committed: line, km (proxy), road min",
            lambda r: (
                f"{_cell(r.nearest_committed)}, "
                f"{_cell(r.dist_committed_km)} km, {_cell(r.road_min_committed)} min"
            ),
        ),
        (
            "Metro: city, tier, km, road min",
            lambda r: (
                f"{_cell(r.nearest_metro)}, "
                f"{_cell(r.nearest_metro_tier)}, {_cell(r.dist_metro_km)} km, {_cell(r.road_min_metro)} min"
            ),
        ),
        ("Economic roles (source)", lambda r: _roles(r.economic_roles)),
        ("Terrain", lambda r: _cell(r.terrain_class)),
        ("Screened", lambda r: _cell(r.screened)),
    ]
    head = "| " + " | ".join(c for c, _ in cols) + " |"
    sep = "|" + "---|" * len(cols)
    body = ["| " + " | ".join(_cell(f(r)) for _, f in cols) + " |" for r in df.itertuples()]
    return "\n".join([head, sep, *body])


def notes_block(df: pd.DataFrame) -> str:
    lines = []
    for r in df.itertuples():
        if r.notes:
            lines.append(f"- **{r.name_en}**: {r.notes}")
    return "\n".join(lines)


@app.command()
def main() -> None:
    """Regenerate docs/regions/al_baha.md."""
    df = pd.read_parquet(REGISTER)
    univ = pd.read_parquet(UNIVERSE)
    univ = univ[univ.region == "al_baha"]
    n_univ = len(univ)
    carried = univ.osm_id.isin(df.osm_id.dropna().astype("int64"))
    n_univ_in = int(carried.sum())
    left = univ[~carried]
    left_max = int(left.population.max())
    n_gov = int(df.governorate.nunique())
    n_10k = int(df.tag_10k.sum())
    n_5k = int(df.tag_5k.sum())
    n_centre = int(df.is_governorate_centre.sum())
    n_grid = int((df.pop_type == "grid").sum())
    n_official = int((df.pop_type == "official").sum())
    assert TAG_10K == 10_000 and TAG_5K == 5_000 and left_max < TAG_5K
    aqiq = df[df.name_en.str.startswith("Al-'Aqiq")].iloc[0]
    ap_aqiq = _km(*AIRPORT, aqiq.lat, aqiq.lon)
    ap_bahah = _km(*AIRPORT, *BAHAH_CITY)
    md = f"""{HEADER}
# Al-Baha (الباحة) region sweep, slug `al_baha` (REGION_AL_BAHA, R2 input)

**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Access dates: 31 Oct 2026 for the R2 sources, 30 Oct 2026 for the pilot-derived ones (Asia/Riyadh). Register: `cities/ksa/regions/al_baha.parquet` (CSV mirror `.csv`); validated with `screening.region_sweep validate --strict` (ok, 16 rows, 10 governorates). Builder: `screening/sweeps/al_baha/build.py`; this page: `screening/sweeps/al_baha/docs.py`.

## Governorate count (reconciled)

| source | count | status |
|---|---|---|
| GASTAT Census 2022 TA1 primary export, governorate split (`S-al_baha-101`, S-cp2-gastat-007): ten Al-Bahah governorates, read by name against the OSM polygons | **10** | verified (primary export) |
| Their sum: 90,515 + 37,608 + 51,787 + 48,333 + 31,197 + 15,496 + 20,010 + 19,586 + 12,506 + 12,136 = 339,174, equal to the Al-Bahah region total (`S-r1a-502`, 339,174; `S-al_baha-112`) | 339,174 | checked in `build.py` (assertion) |
| OSM governorate polygons, Al-Bahah (`S-al_baha-105`) | 10 | derived |
| citypopulation.de Al-Bahah region table (`S-al_baha-112`, secondary, credits GASTAT) | 10 rows + region total; all 11 values equal the primary export to the person | cross-check, 0 conflicts over 2 % |
| Wikipedia, Al-Bahah Province (pilot `S-al_baha-005`): nine governorates plus the Al-Bahah capital | 9 + capital = 10 | secondary; consistent |

`governorates_gastat: 10` · `governorates_listed: {n_gov}`. The two counts are equal and the header records both.

**Not in this region:** `Al Harjah` (18,503) appears in the primary export. It is not one of the ten polygons, and adding it would break the region-total check (the ten sum exactly to 339,174). Its region is for the coverage audit to settle (`docs/coverage.md`); it is not in this register.

## Coverage of the register

- Rows: **{len(df)}**; governorate centres: **{n_centre}** (one per governorate; all 10 governorates have a row).
- Towns at or above 10,000 (`tag_10k`): **{n_10k}**. All five official GASTAT towns in the region at or above 10,000 are in the register: Al-Bahah, Al-Makhwah (Al Mukhwah), Baljurashi, Al-'Aqiq, Qilwah.
- At or above 5,000 (`tag_5k`, sensitivity): **{n_5k}** rows.
- Population provenance: {n_official} official rows (GASTAT Census 2022 TA1 city ≥ 5,000 primary export, `verified`, `S-al_baha-102`); {n_grid} grid rows (WorldPop 2020 100 m constrained not UN-adjusted, `S-al_baha-104`, `unverified`). No row carries a derived figure, and no secondary aggregator figure is used.
- Grid rows at or above 10,000: none. The gate (A-screen-031/032) therefore did not bind. No second method was run, so no `pop_corroboration` value is stored.
- Excluded rows: none. Every row is `screened: true`.
- Settlements not in the register: {len(left)} of the {n_univ} Al-Bahah settlements in `cities/ksa/zones/settlements.parquet` are not carried here (the register holds {n_univ_in} of them, plus the Al-Qara centre, which has no universe row). None is a town or city in OSM, and the largest of them is {left_max:,} (grid), below 5,000, so they fail the 5k test. They stay in the R1a universe for the coverage audit and the sensitivity runs.

## Register table

Distances are great-circle (haversine) to the station the R1a universe holds (`dist_method`); road minutes are OSRM free-flow, uncalibrated (`S-al_baha-106`). Committed distances go to **unlocated proxy stations** (`A-al_baha-004`); read them as indicative. Layers: `hhr:makkah` is the existing Haramain HSR station at Makkah Central (`cities/ksa/lines/hhr.yaml`, layer existing); `landbridge` is committed-layer in its YAML (`layer: committed`) and is announced/planned, so it is never labelled existing.

{table(df)}

Notes per row (from `notes`):

{notes_block(df)}

## Economic roles (sourced; A-screen-011)

- **Administrative** (governorate seat): all ten centres (`S-al_baha-101` governorate name; `S-al_baha-105` OSM polygon).
- **University**: Al-Bahah, Al Baha University (`S-al_baha-110`, Wikipedia list by province; location `S-al_baha-107` OSM node 7994033787, about 2.6 km from the Al-Bahah centre). The public status is derived by subtraction (`S-r1a-222`) and is not checked against the Ministry list.
- **Industrial city**: Al-Bahah, MODON Al-Baha Industrial City (`S-al_baha-111`). No position source exists, so the role is attached by name and the row is flagged.
- **Airport**: Al-Aqiq, King Saud bin Abdulaziz (ABT) domestic airport (`S-al_baha-108` Wikipedia: "located in Al-Aqiq"; location `S-al_baha-107`). The airport is {ap_aqiq:.1f} km from the Al-Aqiq centre and {ap_bahah:.1f} km from Al-Bahah, by great circle (see `A-al_baha-003`).
- **Region-level, not attached to a town (not in the register):** summer tourism and honey (AJEL, `S-al_baha-011` in the pilot file; no year). Heritage villages (a travel guide) and a pomegranate figure from a search snippet are not used. No port, mining, border-crossing, giga-project, Hajj/Umrah, military or energy node was found for Al-Baha in the sources read.
- **Not assessed:** roles for the other towns are empty ("none sourced"), not "none exist".

## Terrain

All sixteen rows: `escarpment_mountain`, a region-level class from the Sarawat escarpment (`S-al_baha-109`). The DEM was not sampled (disk gate; `A-al_baha-001`). This is not a per-town result, and R3 should replace it with DEM classes.

## Exclusions

None. The Al-Qara centre is kept, not excluded: its coordinates are a flagged polygon point (`A-al_baha-002`), not a located town.

## Needs Opus judgement (not resolved here)

1. **Al-Qara centre.** The OSM universe has no place node for the governorate seat (Al-Qara, 19,586 in the governorate total; no town figure). The row uses the polygon representative point (20.4768 N, 41.3334 E) with no distances and no population. A located centre (GASTAT locality list, which is not reachable, or OSM) is needed. The geo-verify step was **not run**: its estimator downloads Microsoft building-footprint tiles and imagery, which the R2 disk gate does not allow in this track (see the status block).
2. **Airport attachment.** R1a's economic node names Al-Bahah as nearest town. By great-circle distance the airport is nearer Al-Aqiq. Al-Aqiq is used, following the Wikipedia location. Confirm before the R2 roles are frozen.
3. **Al-Hajrah seat.** OSM tags the governorate seat `place=village` (grid 2,812). Governorate total 12,136. No town-level census figure is sourced.
4. **Ghamid Az Zinad seat.** OSM town, grid 1,528, governorate total 12,506. The seat's population is not sourced, and the grid figure is far below the governorate total.
5. **Bani Hasan centre.** OSM town node (6,344 official) versus Saudipedia's Bidan and Wadi Al-Sadr (`S-al_baha-113`). The OSM node is used; the Saudipedia conflict is not resolved.
6. **Qilwah.** Two OSM nodes (town 8506335688 used; governorate node 6768458212 not used). The official figure is for the town; the governorate total is 31,197.
7. **Committed distances.** Landbridge and GCC station sites are unlocated proxies (A-r1a-006). The road target for Al-Makhwah is Jeddah (a proxy), while its great-circle station is Al-Jumum; both are shown in the source fields.
8. **R1a control-total and double-counting flags** (grid rows Rahwat al Barr, Sayal). Not excluded. Two villages may double-count a matched city's extent (`A-r1a-004`). Settle in R2 review.
9. **Grid over-count flag** on the region's residual (`control_total_flag`): the grid sum over Al-Bahah exceeds the residual. Reported only (A-screen-037).
10. **Terrain** is region-level (A-al_baha-001).

## Sources

Full rows in `docs/sources/r2-al_baha.csv` (ids `S-al_baha-101` to `S-al_baha-113`). Cross-references to shared ids: `S-al_baha-101` = S-cp2-gastat-007; `S-al_baha-102` = S-cp2-gastat-008; `S-al_baha-104` = S-r1a-505; `S-al_baha-106` = S-r1a-809; `S-al_baha-107` = R1a economic nodes (S-r1a-204, S-r1a-210, S-r1a-221, S-r1a-222, S-cp1-100); `S-al_baha-110` = S-r1a-221; `S-al_baha-111` = S-r1a-204.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Screening input, not a forecast.
"""
    OUT.write_text(md, encoding="utf-8")
    typer.echo(f"wrote {OUT} ({len(md)} chars)")


if __name__ == "__main__":
    app()
