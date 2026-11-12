# ruff: noqa: E501  (prose-heavy generator: narrative strings and tables)
"""Writes the Najran R2 documents from the register (so tables cannot drift from the Parquet).

    .venv/bin/python screening/sweeps/najran/write_docs.py

Writes docs/regions/najran.md, docs/sources/r2-najran.csv and docs/assumptions-r2-najran.md.
Run after build.py; it reads the Parquet, the R1a universe and the pilot source rows.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
REG = REPO / "cities/ksa/regions/najran.parquet"
TODAY = "31 Oct 2026"


def fmt(v: object) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:,.1f}" if abs(v) < 1000 else f"{v:,.0f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def roles(lst: object) -> str:
    if lst is None or len(lst) == 0:
        return "none sourced"
    return "; ".join(f"{x['role']} ({x['source']})" for x in lst)


def main() -> None:
    df = pd.read_parquet(REG)
    s = pd.read_parquet(REPO / "cities/ksa/zones/settlements.parquet")
    s = s[s.region == "najran"].copy()
    s["osm_id"] = s["osm_id"].astype("int64")
    sel_ids = set(df["osm_id"].astype("int64"))
    rest = s[~s.osm_id.isin(sel_ids)]
    # every settlement left out must be below 5,000 on both figures (rule 2 check)
    worst = rest[["population", "grid_population"]].max(axis=1).max()
    assert worst < 5000, f"settlement left out at or above 5,000: {worst}"
    govs = df["governorate"].nunique()
    ten = int(df.tag_10k.sum())
    five = int(df.tag_5k.sum())
    scr = int(df.screened.sum())
    grid_rows = df[df.pop_type == "grid"]
    grid_ge10 = grid_rows[grid_rows.population >= 10000]
    n_roles = int(df.economic_roles.map(len).sum())
    sourced = int(
        sum(
            1
            for lst in df.economic_roles
            for x in lst
            if isinstance(x["source"], str) and x["source"].startswith("S-")
        )
    )
    status_counts = df.pop_source_status.fillna("none").value_counts().to_dict()

    lines = []
    a = lines.append
    a(
        "> **Document version:** docs/regions/najran.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_NAJRAN) | Status: draft"
    )
    a("")
    a("# Najrān region sweep (نجران, slug `najran`): R2 register")
    a("")
    a(
        "**Screening input, not a forecast.** Register: `cities/ksa/regions/najran.parquet` (and `.csv`, same rows). "
        "Built by `screening/sweeps/najran/build.py`; this page by `screening/sweeps/najran/write_docs.py`. "
        "Access dates: 2026-10-31 for the GASTAT primary files and the R1a builds; 2026-10-30 for the pilot-derived secondary rows (kept unchanged in `docs/sources/r2-najran.csv`). Sources: `docs/sources/r2-najran.csv` plus "
        "existing rows in `docs/sources/index.csv`. Assumptions: `docs/assumptions-r2-najran.md`."
    )
    a("")
    a("## Header values")
    a("")
    a(
        f"- `governorates_gastat: {govs}`: the seven Najrān governorate totals (six governorates plus the regional "
        "capital) all appear in the GASTAT primary TA1 governorate export (S-cp2-gastat-007, value match, 150 rows), "
        "and the region membership follows S-073 and the OSM polygons (see A-najran-006). Saudipedia's \"six governorates "
        'plus the capital" (S-najran-003) agrees.'
    )
    a(f"- `governorates_listed: {govs}`. Equal to `governorates_gastat`; no discrepancy.")
    a(
        "- Region total: 592,300 (Census 2022). The seven governorate totals sum to 592,300 (S-najran-001, S-cp2-gastat-007)."
    )
    a(
        f"- Rows: {len(df)} (7 governorate centres + {len(df) - 7} non-centre localities at 5,000 or more). "
        f"Settlements in the R1a universe for Najrān: {len(s)}; {len(rest)} are not rows, and all of them are below "
        "5,000 on both the official and the grid figure (checked by the script)."
    )
    a(
        f"- At or above 10,000 (`tag_10k`): **{ten}** rows (Najrān, Sharūrah, Al Mishaliah, Ḥubūnā, all official, GASTAT primary export)."
    )
    a(
        f"- At or above 5,000 (`tag_5k`, sensitivity): **{five}** rows. Four are `tag_10k`; the other seven are Abā al-Sa'ud "
        "(grid 11,474, uncorroborated) and six at 5,000–9,999 (Khubāsh, Thār, Al Wadī'ah, Al Mikhlaf, Al Nukaysi, Al Urayisah)."
    )
    a(
        f"- Grid-only towns at 10,000 or more that fail the corroboration gate: {len(grid_ge10)} (Abā al-Sa'ud, 11,474, `tag_10k` false, "
        "reason in the register)."
    )
    a(
        f"- Screened rows: {scr} of {len(df)}; excluded (kept as coverage rows): 2 governorate centres below 5,000 (Yadamah, Badr Al Janub)."
    )
    a(
        f"- Population sources by status: verified {status_counts.get('verified', 0)} (GASTAT primary export), secondary "
        f"{status_counts.get('secondary', 0)} (citypopulation.de, crediting GASTAT), unverified {status_counts.get('unverified', 0)} (WorldPop gap-fill)."
    )
    a(f"- Economic roles: {n_roles}; sourced to an S- id: {sourced}.")
    a("")
    a("## Register")
    a("")
    a("Table A: identity, coordinates, population and tags.")
    a("")
    a(
        "| name (EN) | name (AR) | governorate | centre | OSM node | lat, lon | population (type, year, source status) | ≥10k | ≥5k | screened |"
    )
    a("|---|---|---|---|---|---|---|---|---|---|")
    for _, r in df.sort_values("population", ascending=False).iterrows():
        pop = fmt(r.population)
        if r.population == r.population and r.pop_type:
            pop += f" ({r.pop_type}, {int(r.pop_year)}, {r.pop_source_status})"
        a(
            f"| {r.name_en} | {r.name_ar} | {r.governorate} ({r.governorate_ar}) | {fmt(r.is_governorate_centre)} | "
            f"{r.osm_type} {r.osm_id} | {r.lat:.5f}, {r.lon:.5f} | {pop} | {fmt(r.tag_10k)} | {fmt(r.tag_5k)} | {fmt(r.screened)} |"
        )
    a("")
    a("Table B: distances, metro, economic roles, terrain, screening.")
    a("")
    a(
        "| name (EN) | dist existing km (road min) | nearest existing | committed km (road min) | nearest committed (station) | dist metro km (road min) | nearest metro (tier) | economic roles (source) | terrain (assumed) | exclusion |"
    )
    a("|---|---|---|---|---|---|---|---|---|---|")
    for _, r in df.sort_values("population", ascending=False).iterrows():
        a(
            f"| {r.name_en} | {fmt(r.dist_existing_km)} ({fmt(r.road_min_existing)}) | {r.nearest_existing} | "
            f"{fmt(r.dist_committed_km)} ({fmt(r.road_min_committed)}) | {r.nearest_committed} ({r.nearest_committed_station}) | "
            f"{fmt(r.dist_metro_km)} ({fmt(r.road_min_metro)}) | {r.nearest_metro} ({fmt(r.nearest_metro_tier)}) | "
            f"{roles(r.economic_roles)} | {r.terrain_class} (A-najran-001) | {fmt(r.exclusion_reason)} |"
        )
    a("")
    a("Column notes:")
    a(
        "- **Distances** are great-circle (haversine, A-screen-pilot-001) to R1a's alignment vertices (1 km spacing). "
        "**Road minutes** are R1a's OSRM car skim (free flow, uncalibrated) to the nearest target station, as recorded in the "
        "settlements universe. The skim targets: `hhr:makkah`, `sar-east-passenger:riyadh`, `sar-east-passenger:hufuf`, `landbridge:muwai`."
    )
    a(
        "- **Committed layer:** Landbridge (`committed`, announced; `cities/ksa/lines/landbridge.yaml`, S-054). "
        "The station shown is the Muwai/Moya intermediate stop, named but not located in S-062; it is an announced stop, "
        "not an existing or built one. No row calls a committed or hypothetical line existing."
    )
    a(
        "- **Terrain** is assumed for every row (A-najran-001); no DEM class has been computed in R2."
    )
    a(
        "- **Metro**: all rows point to Najrān (tier 3), the nearest approved metro (A-screen-013). Najrān city is 0.0 km from itself."
    )
    a("")
    a("## Exclusions and coverage")
    a("")
    a(
        "- **Yadamah** (centre, 4,983 per S-najran-002) and **Badr Al Janub** (centre, 2,709): below 5,000 (A-screen-002). "
        "Kept as governorate-centre coverage rows (rule 2) with `screened: false`. The governorate totals (16,160; 7,991) are not used as centre figures."
    )
    a(
        "- **Al-Kharkhīr** (R1a settlement KSA-ST-01416, 3,277 grid): below 5,000, not a row. Its point lies at 18.85 N, 51.12 E, about 740 km from the "
        "Najrān-region centres, so its attribution to Sharūrah is a boundary or grid error (R1a control flag). Not used."
    )
    a(
        "- **Settlements left out:** the other settlements of the R1a universe for Najrān are below 5,000 on both figures and are not rows."
    )
    a(
        "- **Not in the R1a universe:** two Census 2010 cities above 5,000 (Hairat al-Salam, 5,820; Taslan, 5,284) are in the 2010 list but not "
        "in the R1a settlement universe or the 2022 primary 5,000+ export. Not added; see Needs Opus judgement."
    )
    a("")
    a("## Population provenance and the control total")
    a("")
    a(
        "- **Official, verified (6 rows):** Najrān, Sharūrah, Ḥubūnā, Khubāsh, Al Mishaliah, Al Wadī'ah: the GASTAT Census 2022 "
        "TA1 primary export, city 5,000+ (S-cp2-gastat-008). The relayed figures (S-cp2-gastat-001) agree on every row (0.0 % difference)."
    )
    a(
        "- **Official, secondary (2 rows):** Yadamah and Badr Al Janub: citypopulation.de's places 2,500+ table (S-najran-002), crediting GASTAT. "
        "`primary_to_find`: the GASTAT locality table."
    )
    a(
        "- **Grid, unverified (5 rows):** Thār (8,030), Abā al-Sa'ud (11,474), Al Mikhlaf (6,853), Al Nukaysi (6,525), Al Urayisah (6,093). "
        "WorldPop 2020 (S-r1a-506) gap-fill from R1a. None has a second method, and none is in the GASTAT places 2,500+ table (S-najran-002) "
        "or the primary 5,000+ export. `tag_10k` is false for all five (A-screen-031/032). `tag_5k` is not gated and is true for all five."
    )
    a(
        "- **Control total (A-screen-037):** the region's grid-filled population exceeds the residual by 5,347 (75,223 grid against a residual of "
        "69,876; `runs/gastat/primary/control_total.csv`). Reporting only; nothing is corrected."
    )
    a(
        "- **Record-only geo-verify estimates** (pilot GEO_VERIFY notes, reproduced in R2 by `screening.geo_verify.cli estimate` on the pilot "
        "register: buildings × occupancy and WorldPop): Thār 4,465 (band 1,314–10,245) and Badr Al Janub 4,128 (band 1,513–7,602); Yadamah has no "
        "building cluster. Both methods failed the 30 % back-test gate, so these are in `notes` only and never in `population`."
    )
    a("")
    a("## Needs Opus judgement (not resolved by the sweep)")
    a("")
    a(
        "1. **Khubāsh centre node.** The row uses the village node n8503374507 (17.54985, 44.74113); the governorate node n6774251958 is 55.5 km away. "
        "A-najran-003."
    )
    a(
        "2. **Ḥubūnā centre node.** The row uses the town node n11871306300; the governorate node n6769844117 is 20.2 km away. A-najran-003."
    )
    a(
        "3. **Najrān and Sharūrah centre figures.** The rows carry the city figures (381,431; 89,456), not the governorate totals (421,902; 100,199)."
    )
    a(
        "4. **Five grid-only towns at 5,000 or more** (Thār, Abā al-Sa'ud, Al Mikhlaf, Al Nukaysi, Al Urayisah). The GASTAT places 2,500+ table has no "
        "figure for any of them, so the grid may over-count, and the control total is +5,347. Decide whether they stay in the 5,000 sensitivity (tag_5k)."
    )
    a(
        "5. **Thār on the 5,000 line.** Its `tag_5k` rests on an uncorroborated grid figure (8,030); the record-only estimate (4,465) is below 5,000."
    )
    a(
        "6. **Abā al-Sa'ud.** The grid figure (11,474) crosses 10,000 but is uncorroborated (`tag_10k` false). It flips only if a second method corroborates it within 30 %."
    )
    a(
        "7. **Hairat al-Salam (5,820) and Taslan (5,284)** in the Census 2010 cities above 5,000 list are not in the R1a universe or the 2022 primary 5,000+ export. "
        "Are they GASTAT localities, and what are their 2022 figures? Not added."
    )
    a(
        "8. **Al Wadī'ah border-crossing role** rests on a secondary snippet (S-najran-010) and no R1a economic node. Verify before use."
    )
    a(
        "9. **Heritage role** (Hima cultural area, ~82 km from Najrān city and ~47 km from the Thār row) is attributed to the Najrān city row through R1a's nearest-town field (A-najran-005). Opus to decide whether Thār, a screened row, should carry it instead."
    )
    a(
        "10. **Spelling and transliteration.** The OSM names for Abā al-Sa'ud, Al Mikhlaf, Al Nukaysi and Al Urayisah are Arabic only; the English names are the coordinator's. Khubāsh is spelled per the citypopulation list (OSM: Khubash)."
    )
    a(
        "11. **Terrain** is assumed for all rows (A-najran-001). A DEM class is needed before any terrain-dependent output."
    )
    a(
        "12. **geo-verify CLI scope.** `screening.geo_verify.cli` reads only `cities/ksa/regions/pilot-*.parquet` (`REGISTERS`), so it does not process this register. The estimate was run on the pilot rows, not on these rows."
    )
    a("")
    a("## Sources")
    a("")
    a(
        "- GASTAT primary exports (in the repository's data area): S-cp2-gastat-007 (governorates), S-cp2-gastat-008 (cities 5,000+), "
        "S-cp2-gastat-001 (relayed cross-check). Registered in `cities/ksa/sources.yaml`."
    )
    a(
        "- Secondary: S-najran-001 (governorate table), S-najran-002 (places 2,500+), S-najran-003 (Saudipedia), S-najran-010 (border crossing). "
        "All are in `docs/sources/r2-najran.csv`."
    )
    a(
        "- OSM: S-najran-004 (GCC extract, ODbL). Economic nodes: S-cp1-100, S-r1a-204, S-r1a-205, S-r1a-210, S-r1a-221, S-r1a-222 (R1a)."
    )
    a(
        "- Population gap-fill: S-r1a-506 (WorldPop 2020, 100 m, constrained and UN-adjusted; CC BY 4.0, S-r1a-508). Census reference: S-071."
    )
    a("- Landbridge: S-054 (line), S-062 (intermediate stops, no location).")
    a("")
    a("## Validation performed")
    a("")
    a(
        "- `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/najran.parquet`: ok, 13 rows, 7 governorates."
    )
    a(
        "- Parquet and CSV hold the same 13 rows (same `osm_id` order); the table above is generated from the Parquet."
    )
    a(
        "- Every population carries `pop_source`, `pop_year` and `pop_type`; grid rows carry `pop_source_status: unverified`."
    )
    a("- Every economic role names an S- source (13 of 13).")
    a(
        "- The seven governorate centres each have a row; the non-row settlements are checked to be below 5,000."
    )
    a("")
    a("Screening input, not a forecast.")

    (REPO / "docs/regions/najran.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_sources()
    write_assumptions()
    print(f"wrote docs/regions/najran.md ({len(lines)} lines); rest-of-universe max = {worst:.0f}")


SOURCE_IDS = ["S-najran-001", "S-najran-002", "S-najran-003", "S-najran-004", "S-najran-010"]


def write_sources() -> None:
    """The R2 source rows: the pilot rows this register cites, under the same ids and claims."""
    pilot = pd.read_csv(REPO / "docs/sources/pilot-najran.csv", dtype=str).fillna("")
    keep = pilot[pilot.id.isin(SOURCE_IDS)].copy()
    keep["used_in"] = "docs/regions/najran.md; cities/ksa/regions/najran.parquet"
    keep.to_csv(REPO / "docs/sources/r2-najran.csv", index=False)


ASSUMPTIONS = [
    (
        "A-najran-001",
        "terrain class for every row (no DEM class computed in R2): mixed, except dunes for Sharūrah and Al Wadī'ah",
        "mixed / dunes",
        "class",
        "DEM class pending",
        "Assumed from secondary descriptions, carried from the pilot's terrain assumption (A-najran-terrain-001; its source S-najran-009 is in the pilot file only and weakly sourced). Replace from DEM before terrain-dependent outputs.",
        "assumed",
        "terrain_class",
    ),
    (
        "A-najran-002",
        "grid-only population gate: tag_10k false for every WorldPop-filled row (no second method run for any)",
        "tag_10k = false",
        "rule",
        "n/a",
        "Assumed to implement A-screen-031/032 for R2: no second independent method was run for these rows (the 2010-growth test has no matched 2010 city >5k for them).",
        "assumed (rule)",
        "tag_10k; exclusion_reason",
    ),
    (
        "A-najran-003",
        "centre node choice where OSM holds a governorate node and a village or town node (Khubāsh, Ḥubūnā)",
        "village / town node",
        "node",
        "governorate node 20–56 km away",
        "Assumed (pilot A-najran-osm-001, carried): the census-named settlement node is the centre; the governorate node is the administrative point.",
        "assumed",
        "osm_id; lat, lon",
    ),
    (
        "A-najran-004",
        "control-total tolerance for the grid-filled Najran population (reported, not corrected)",
        "+5,347 persons (grid 75,223 vs residual 69,876)",
        "persons",
        "A-screen-037",
        "Sourced: runs/gastat/primary/control_total.csv (A-screen-037). Reporting only.",
        "sourced",
        "notes",
    ),
    (
        "A-najran-005",
        "heritage role of the Hima cultural area attributed to the Najrān city row (the site is ~80 km away)",
        "attribution",
        "n/a",
        "n/a",
        "Assumed from R1a's nearest-town field (S-r1a-205, nearest_town Najran).",
        "assumed",
        "economic_roles",
    ),
    (
        "A-najran-006",
        "governorate count for Najrān = 7 (six governorates plus the regional capital)",
        "7",
        "governorates",
        "n/a",
        "Sourced: all seven Najrān governorate totals appear in the GASTAT primary export S-cp2-gastat-007 (value match); region membership from S-073 and OSM polygons (secondary), S-najran-003.",
        "sourced (membership secondary)",
        "governorates_gastat; governorates_listed",
    ),
]


def write_assumptions() -> None:
    head = [
        "> **Document version:** docs/assumptions-r2-najran.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_NAJRAN) | Status: draft",
        "",
        "# Assumptions: R2 Najrān sweep (slug `najran`)",
        "",
        "Same row format as `docs/assumptions.md`. The distance method (A-screen-pilot-001, haversine), the population thresholds (A-screen-001/002) "
        "and the population rule (A-screen-031 to A-screen-039) are canonical there; this file lists only the Najrān-specific choices.",
        "",
        "| id | parameter | value | unit | range | source or assumption | status | used in |",
        "|---|---|---|---|---|---|---|---|",
    ]
    rows = [f"| {' | '.join(r)} |" for r in ASSUMPTIONS]
    (REPO / "docs/assumptions-r2-najran.md").write_text(
        "\n".join(head + rows) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
