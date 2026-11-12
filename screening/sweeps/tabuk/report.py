# ruff: noqa: E501  (prose-heavy Markdown and source notes; one sentence per string)
"""REGION_TABUK: writes docs/regions/tabuk.md, the source list and the summary counts (r2-tabuk).

Reads `cities/ksa/regions/tabuk.parquet` (written by `screening.sweeps.tabuk.build`) and the pilot
source list (`docs/sources/pilot-tabuk.csv`), so every number in the Markdown comes from the
register.

    PYTHONPATH=. .venv/bin/python -m screening.sweeps.tabuk.report
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(".")
REG = ROOT / "cities/ksa/regions/tabuk.parquet"
MD = ROOT / "docs/regions/tabuk.md"
SRC_IN = ROOT / "docs/sources/pilot-tabuk.csv"
SRC_OUT = ROOT / "docs/sources/r2-tabuk.csv"

# Source status overrides for R2 (the primary GASTAT exports supersede the pilot's relays).
SRC_STATUS = {
    "S-tabuk-001": (
        "secondary; governorate values cross-checked against the primary export S-cp2-gastat-007 "
        "(150 governorates; Tabuk region 886,036 = pilot check): the primary figures are used"
    ),
    "S-tabuk-002": (
        "secondary; used only for Bi'r Ibn Hirmas (4,964, below 5,000, not in the primary city "
        "table). Town values for the seven seats and the other towns come from S-cp2-gastat-008"
    ),
    "S-tabuk-006": (
        "primary (OSM); same GCC extract as S-r1a-210, which carries the register's OSM ids and "
        "tags"
    ),
}
SRC_NOTE = {
    "S-tabuk-017": "conflicting social-media figure: not used (C-tabuk-001)",
    "S-tabuk-019": "conflicting web figure: not used",
    "S-tabuk-021": (
        "unverified count: the GASTAT primary export (150 governorates) has no Hala/Halat entry, so "
        "Halat Ammar is not a governorate in R2"
    ),
    "S-tabuk-005": "404 (2026-10-30): not used",
}


def status_class(s: str) -> str:
    s = s.lower()
    if s.startswith("primary"):
        return "primary"
    if s.startswith("secondary"):
        return "secondary"
    return "unverified"


def write_sources() -> Counter:
    src = pd.read_csv(SRC_IN)
    for sid, text in SRC_STATUS.items():
        src.loc[src.id == sid, "status"] = text
    for sid, text in SRC_NOTE.items():
        src.loc[src.id == sid, "status"] = (
            src.loc[src.id == sid, "status"].astype(str) + "; " + text
        )
    src.to_csv(SRC_OUT, index=False)
    return Counter(status_class(str(s)) for s in src.status)


def short_roles(roles) -> str:
    return ", ".join(sorted({r["role"] for r in roles})) if len(roles) else "none sourced"


def fmt(v, nd: int | None = None) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "–"
    if isinstance(v, float) and nd is not None:
        return f"{v:,.{nd}f}"
    if isinstance(v, (int,)) and not isinstance(v, bool):
        return f"{v:,}"
    return str(v)


def main() -> None:
    df = pd.read_parquet(REG)
    counts = {
        "rows": len(df),
        "gov": df.governorate.nunique(),
        "ge10k": int(df.tag_10k.sum()),
        "ge5k": int(df.tag_5k.sum()),
        "screened": int(df.screened.sum()),
        "excluded": int((~df.screened).sum()),
        "no_pop": int(df.population.isna().sum()),
        "pop_type": df.pop_type.value_counts(dropna=False).to_dict(),
        "roles_rows": int((df.economic_roles.map(len) > 0).sum()),
        "roles_total": int(df.economic_roles.map(len).sum()),
        "grid_rows": int((df.pop_type == "grid").sum()),
    }
    src_counts = write_sources()
    lines: list[str] = []
    w = lines.append
    w(
        "> **Document version:** docs/regions/tabuk.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_TABUK) | Status: draft"
    )
    w("")
    w("# Tabuk sweep (تبوك, slug `tabuk`)")
    w("")
    w(
        "**Screening input, not a forecast.** Full R2 register for Tabuk: every GASTAT governorate, every "
        "settlement the R1a universe holds for the region (119), population from the primary GASTAT Census 2022 "
        "exports where they cover a town, WorldPop only as a flagged gap-fill, distances and road minutes from the R1a skims. "
        "Register: `cities/ksa/regions/tabuk.parquet` and `.csv`. Builders: `screening/sweeps/tabuk/`."
    )
    w("")
    w("## 1. Governorate count")
    w("")
    w("| Source | Count | Note |")
    w("|---|---|---|")
    w(
        "| GASTAT primary, TA1 by governorate (S-cp2-gastat-007) | 150 governorates in the export; **7 in Tabuk** | Region membership of each governorate from the relayed S-073 list (`screening/gastat.py`, `governorates_2022`); the seven are Tabuk, Umluj, Duba, Al-Wajh, Taymā', Haql, Al-Bad' |"
    )
    w("| Register: `governorates_gastat` header | **7** | |")
    w(
        "| Register: `governorates_listed` header | **7** | the seven governorate centres, one row each |"
    )
    w("| S-tabuk-004 (Wikipedia, Tabuk Province) | 6 + seat = 7 | agrees |")
    w("| S-tabuk-003 (Arabic Wikipedia) | 7 rows incl. the capital | agrees |")
    w(
        "| S-tabuk-021 (Al-Ma'rifa) | counts Hala Ammar as the 7th | unverified; the primary export has no Hala/Halat entry, so not a governorate |"
    )
    w("")
    w(
        "GASTAT and the register agree (7 = 7). Halat Ammar (حالة عمار) is not a governorate: its OSM polygon is Tabuk (G147), so it sits in the Tabuk governorate row."
    )
    w("")
    w("## 2. Counts")
    w("")
    w(
        f"- Rows: **{counts['rows']}** (all settlements the R1a universe holds for `tabuk`; the 7 governorate centres are among them)."
    )
    w(
        f"- At ≥ 10,000 (`tag_10k`): **{counts['ge10k']}**, all seven governorate centres, all `pop_type: official` from the primary city export S-cp2-gastat-008. No grid row reaches 10,000, so the corroboration gate is not triggered."
    )
    w(
        f"- At ≥ 5,000 (`tag_5k`, sensitivity): **{counts['ge5k']}** = the seven centres plus Halat Ammar (derived, OSM tag), Makna and Al Kor (WorldPop grid, unverified)."
    )
    w(
        f"- Screened in (`screened: true`): **{counts['screened']}** = the 10 at ≥ 5,000 plus Neom (2,122 grid; giga-project role)."
    )
    w(
        f"- Excluded (`screened: false`, with reason): **{counts['excluded']}**, each with the reason `below 5,000 and no sourced economic role (A-screen-003)`; one of them (قرية الجديد, OSM tag 4,000) also has no dated population and so no population field."
    )
    w(
        f"- Rows with a population: **{counts['rows'] - counts['no_pop']}**; without: **{counts['no_pop']}** (the undated OSM tag above)."
    )
    w(
        f"- Rows with a sourced economic role: **{counts['roles_rows']}** ({counts['roles_total']} role entries); every role names an S- source."
    )
    w(
        f"- WorldPop grid rows: **{counts['grid_rows']}**, all `pop_source_status: unverified`, none with `pop_corroboration` (no second method was run for these villages; the 2010 city-growth method covers only towns in the 2010 ≥ 5,000 list)."
    )
    w("")
    w("## 3. Population basis and conflicts")
    w("")
    w(
        "- Seven centres: GASTAT primary city export (S-cp2-gastat-008), settlement figures (Tabuk 594,350; Umluj 46,229; Duba 39,543; Al-Wajh 33,868; Tayma 37,579; Haql 25,652; Al-Bad' 16,583). The governorate totals (S-cp2-gastat-007: Tabuk 623,665, etc.) are not used for any row."
    )
    w(
        "- Bi'r Ibn Hirmas: 4,964 from the relayed citypopulation.de table (S-tabuk-002, secondary). It is below 5,000, so the primary city export does not list it; the OSM tag 5,975 is not used."
    )
    w(
        "- Halat Ammar: OSM population tag 5,293 (derived, S-r1a-210). **Conflict:** the census city table (≥ 5,000 list, S-cp2-gastat-008) does not list it, so it is either below 5,000 in the census or missing from the list. WorldPop gives 7,067, not used (derived > grid). Kept as a 5k sensitivity row only (A-tabuk-002)."
    )
    w(
        "- Makna (5,756) and Al Kor (5,353): WorldPop 2020 grid, unverified; `tag_5k` only (no 10k status possible without corroboration)."
    )
    w(
        "- Duba: the register keeps the GASTAT city figure (39,543). The R1a grid for the same town (25,568 OSM tag, 17,104 grid) is not used."
    )
    w(
        "- Conflicting social-media figure for Tabuk city (S-tabuk-017, 448,000) and web figure (S-tabuk-019, 753,730): not used."
    )
    w("")
    w("## 4. Distances and economic roles")
    w("")
    w(
        "- Distances: R1a skims. `dist_existing_km` = great circle to the 15 intercity passenger stations (A-r1a-008), road minutes OSRM car over the 5 nearest candidates (A-r1a-027). Tabuk's nearest existing stations are on the SAR North line (Al-Qurayyat, Al-Jawf) and the HHR (Madinah); the historic Hejaz line is `historical` and not counted."
    )
    w(
        "- Committed: `nearest_committed` is Landbridge or GCC-railway stops; Landbridge stops are unlocated (`committed_sites_unlocated`), so committed distances are indicative (A-tabuk-004)."
    )
    w(
        "- Metro: `dist_metro_km` from the A-r1a-009 reference nodes, tier from A-screen-013. Tabuk is a tier-2 metro: 91 rows point to Tabuk (tier 2) and 28 (mostly Umluj and the northern coast) point to Madinah (tier 1) because Madinah is nearer by great circle (see §8)."
    )
    w(
        "- Roles: every role is sourced in the row (`economic_roles`, `source`); the sources are the pilot's S-tabuk-004/007–014 and the R1a economic nodes S-r1a-204, S-r1a-212, S-r1a-221, S-cp1-100. Umluj has no sourced role (S-tabuk-011's role statements are unreferenced)."
    )
    w("")
    w("## 5. Terrain")
    w("")
    w(
        "Terrain is **assumed by governorate** (A-tabuk-003): no DEM class exists for this region in the R1a outputs, so no DEM was read in R2. Coastal: Al-Wajh, Duba, Haql, Umluj. Mixed: Tabuk, Taymā', Al-Bad'. Replace with a DEM class before any terrain-dependent cost or alignment."
    )
    w("")
    w("## 6. The table")
    w("")
    w(
        "| # | name_en | name_ar | governorate | osm_id | population | pop_type | status | tag 5k | tag 10k | screened | road min existing | nearest committed | metro (tier) | roles | exclusion |"
    )
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(
        df.sort_values(
            ["screened", "population"], ascending=[False, False], na_position="last"
        ).itertuples(index=False),
        1,
    ):
        excl = (
            "–"
            if r.screened
            else ("no dated population" if pd.isna(r.population) else "below 5k, no role")
        )
        if r.is_governorate_centre:
            excl = "seat (" + r.governorate + ")"
        status = "–" if pd.isna(r.pop_source_status) else str(r.pop_source_status)
        w(
            f"| {i} | {r.name_en} | {r.name_ar} | {r.governorate} | {r.osm_id} | {fmt(None if pd.isna(r.population) else int(r.population))} | "
            f"{fmt(r.pop_type)} | {status} | {'yes' if r.tag_5k else 'no'} | {'yes' if r.tag_10k else 'no'} | "
            f"{'yes' if r.screened else 'no'} | {fmt(r.road_min_existing, 1)} | {fmt(r.nearest_committed)} | "
            f"{fmt(r.nearest_metro)} | {short_roles(r.economic_roles)} | {excl} |"
        )
    w("")
    w("## 7. Exclusions")
    w("")
    w(
        "Every excluded row is in the table with its reason. In summary: the 107 below-5,000 settlements carry the reason `below 5,000 and no sourced economic role (A-screen-003)`, and the undated OSM tag (قرية الجديد) also has no population. Bi'r Ibn Hirmas (4,964) is the 5k boundary check: census figure below 5,000, OSM tag 5,975 not used."
    )
    w("")
    w("## 8. Needs Opus judgement (not resolved by guessing)")
    w("")
    w(
        "1. **Halat Ammar, census vs OSM.** Census ≥ 5,000 list omits it; OSM tag 5,293. Kept as a derived 5k row. Decide whether to drop it or get the census locality figure."
    )
    w(
        "2. **Red Sea International Airport (Hanak) and Red Sea Global.** Their R1a nodes name Hanak and 'Red Sea coast', but neither is a settlement in the R1a universe, so the roles are not attached to any row. Decide whether to add Hanak as a settlement."
    )
    w(
        "3. **NEOM.** The town figure (2,122) is a WorldPop grid value for a giga-project site under construction; the Port of NEOM has no location (node unlocated). The giga-project role is sourced (S-r1a-212), the population is not a settled figure."
    )
    w("4. **Terrain** is by governorate (A-tabuk-003), not a DEM class.")
    w(
        "5. **Umluj's nearest metro** is Madinah (tier 1, 245 km), not Tabuk (tier 2). A-screen-013 nearest-by-distance; decide whether the Tabuk tier should cover Umluj."
    )
    w(
        "6. **Committed distances** are indicative: Landbridge stops are unlocated proxies (A-tabuk-004)."
    )
    w("7. **Umluj** has no sourced economic role.")
    w(
        "8. **Dhiba port (Duba)**: the Mawani name is unverified (S-r1a-209 not read); the role rests on S-tabuk-007 and S-r1a-242."
    )
    w(
        "9. **Haql spelling**: the S-073 list writes 'Haqil'; the register uses 'Haql' (the GASTAT primary spelling)."
    )
    w("")
    w("## 9. Sources")
    w("")
    w(
        f"`docs/sources/r2-tabuk.csv` ({sum(src_counts.values())} rows): primary {src_counts.get('primary', 0)}, secondary {src_counts.get('secondary', 0)}, unverified {src_counts.get('unverified', 0)}. The primary GASTAT exports are S-cp2-gastat-007 (governorates) and S-cp2-gastat-008 (cities of 5,000 or more); WorldPop is S-r1a-505; OSM ids and tags are S-r1a-210."
    )
    w("")
    w(
        "Label: screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast."
    )
    w("")
    MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(counts)


if __name__ == "__main__":
    main()
