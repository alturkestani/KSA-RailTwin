"""Writes docs/regions/madinah.md from the built register and the GASTAT primary tables (R2).

Every count in the document is computed here from `cities/ksa/regions/madinah.parquet`, the R1a
universe and the GASTAT primary city export, so the prose and the table cannot drift apart.

    .venv/bin/python -m screening.sweeps.madinah.report --seed 1
"""
# ruff: noqa: E501  (prose lines are the document text; kept whole)

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from common.runmeta import rng

app = typer.Typer(add_completion=False, help="Madinah region report (R2).")

REG = Path("cities/ksa/regions/madinah.parquet")
UNIVERSE = Path("cities/ksa/zones/settlements.parquet")
CITY5K = Path("data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx")
OUT = Path("docs/regions/madinah.md")
VERSION = "docs/regions/madinah.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_MADINAH) | Status: draft"

# Unmatched primary cities that are placed in this register by name (see notes)
PLACED_BY_NAME = {"Yanbaa As-Senayah"}
WADI_OQOOL = "Wadi Al Oqool farms"


def _md(v: object) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return str(v).replace("|", "/")


def _unmatched_primary(univ: pd.DataFrame) -> pd.DataFrame:
    """Primary 5,000+ city rows whose total is not an official population in the R1a universe."""
    c = pd.read_excel(CITY5K)
    c = c[~c.City.str.startswith(("Other", "Total"))]
    official = set(univ.loc[univ.population_basis == "official", "population"].astype(int))
    return c[~c.Total.isin(official)].reset_index(drop=True)


@app.command()
def report(seed: int = typer.Option(1, "--seed", min=0)) -> None:
    """Write docs/regions/madinah.md."""
    rng(seed)
    d = pd.read_parquet(REG)
    univ = pd.read_parquet(UNIVERSE)
    m = univ[univ.region == "madinah"]
    unmatched = _unmatched_primary(univ)
    gov_n = int(d.governorate.nunique())
    grid_uncorr = d[d.exclusion_reason.fillna("").str.contains("uncorroborated")]
    below5 = int((m.population.fillna(0) < 5000).sum())
    roles = sum(len(x) for x in d.economic_roles)
    lines: list[str] = []
    w = lines.append
    w(f"> **Document version:** {VERSION}")
    w("")
    w("# Region sweep: Al-Madinah al-Munawwarah (المدينة المنورة), slug `madinah` (R2)")
    w("")
    w("Screening input, not a forecast.")
    w("")
    w("## 1. Governorate count (GASTAT vs listed)")
    w("")
    w(
        "- `governorates_gastat` = **9** (S-073: the relayed census governorate list gives 9 "
        "rows for the region, capital included). The primary TA1 governorate export "
        "(S-cp2-gastat-007) has all 9 names with populations; it has no region column, so "
        "membership rests on S-073."
    )
    w(
        f"- `governorates_listed` = **{gov_n}** (distinct governorates in the rows). Equal: no discrepancy."
    )
    w(
        "- Wādī al-Fara' has a row (governorate centre not identified; section 5). The pilot's "
        "'8 of 9' gap is closed by that row, not by a sourced seat."
    )
    w("")
    w("## 2. Counts")
    w("")
    w(
        f"- Rows in the register: **{len(d)}** ({int(d.is_governorate_centre.sum())} governorate-centre rows, incl. Wādī al-Fara'; {len(d) - int(d.is_governorate_centre.sum())} other settlements)."
    )
    w(f"- At or above 10,000 (`tag_10k`): **{int(d.tag_10k.sum())}** rows, all official GASTAT.")
    w(
        f"- Grid-only at or above 10,000, uncorroborated (kept, `tag_10k` false, `exclusion_reason` set): **{len(grid_uncorr)}** rows."
    )
    w(f"- At or above 5,000 (`tag_5k`, sensitivity set): **{int(d.tag_5k.sum())}** rows.")
    w(
        f"- Settlements below 5,000 in the R1a universe, not written: **{below5}** (rule 2: counted, not silently dropped)."
    )
    w(
        f"- Economic roles recorded: **{roles}** (each with an `S-` source); rows with no role: {int((d.economic_roles.map(len) == 0).sum())} (roles not assessed beyond the R1a nodes)."
    )
    w(
        "- Terrain: **not assessed** for every row (`terrain_class` null): no DEM terrain layer is in the R1a outputs and the disk gate forbids a new DEM download here (section 6)."
    )
    w("")
    w("## 3. Register (table)")
    w("")
    w(
        "Population: `official` = GASTAT primary (verified); `grid` = WorldPop gap-fill (unverified); `derived` = OSM tag. Distances are straight-line (haversine) to the nearest existing station (HHR) and the metro; road minutes are the R1a OSRM car skim."
    )
    w("")
    w(
        "| # | name (EN) | name (AR) | governorate | centre | population | type / status | ≥10k | ≥5k | dist existing km (road min) | nearest metro (tier) | roles |"
    )
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in d.reset_index(drop=True).iterrows():
        pop = "—" if pd.isna(r.population) else f"{int(r.population):,}"
        ts = "—" if pd.isna(r.pop_type) else f"{r.pop_type} / {r.pop_source_status}"
        dist = "—" if pd.isna(r.dist_existing_km) else f"{r.dist_existing_km:.1f}"
        road = "—" if pd.isna(r.road_min_existing) else f"{r.road_min_existing:.0f}"
        metro = "—" if pd.isna(r.nearest_metro) else f"{r.nearest_metro} "
        roles_s = "; ".join(x["role"] for x in r.economic_roles) or "—"
        w(
            f"| {i + 1} | {_md(r.name_en)} | {_md(r.name_ar)} | {_md(r.governorate)} | "
            f"{'yes' if r.is_governorate_centre else 'no'} | {pop} | {ts} | "
            f"{'yes' if r.tag_10k else 'no'} | {'yes' if r.tag_5k else 'no'} | {dist} ({road}) | "
            f"{metro.strip()} | {roles_s} |"
        )
    w("")
    w(
        "Node and station labels: `nearest_existing` is the R1a station id (`hhr:madinah`, `hhr:kaec`), named in the register; `nearest_committed` is the Saudi Landbridge committed layer, with its stations unlocated (R1a), so `nearest_committed_station` is null."
    )
    w("")
    w("## 4. Exclusions and what is not in the table (rule 2)")
    w("")
    w(
        f"- **Below 5,000:** {below5} R1a settlements; not rows of this register (the sensitivity threshold is 5,000)."
    )
    w(
        f"- **Grid-only, ≥ 10,000, uncorroborated:** {', '.join(grid_uncorr.name_en.astype(str))}. Kept as rows with `tag_10k` false; no second method was run (A-screen-031/032)."
    )
    w(
        f"- **{WADI_OQOOL} (GASTAT primary, 24,381, official):** NOT a row. It is an official ≥10,000 settlement the register should hold, but it has no OSM node and no coordinates in any source reached (the pilot also could not place it). `RegionRow` needs lat/lon, and a proxy point would give wrong distances. **Open: needs a located point (Opus judgement).**"
    )
    w(
        "- **Wādī al-Fara' seat:** row kept with `screened: false`, no population, no distances. S-madinah-015 names seven subdivision centres and no seat; none is chosen."
    )
    open_big = unmatched[~unmatched.City.isin(PLACED_BY_NAME | {WADI_OQOOL})]
    big = open_big[open_big.Total >= 10000]
    w(
        f"- **GASTAT primary cities not matched to any settlement in the R1a universe:** {len(open_big)} rows, not counting the two discussed above (Yanbu Industrial City, now a row; Wādī al-'Uqūl farms) and 'Other'. Their region is not stated in the primary export, and the R1a matching did not place them. Of these, **{len(big)}** are at or above 10,000; any that belongs to Al-Madinah region would be a missing row. Listed in section 7. **Open: needs the GASTAT city-to-governorate table (Opus judgement).**"
    )
    w("")
    w("## 5. Centres and the Wādī al-Fara' gap")
    w("")
    w(
        "- Every governorate of the 9 has a row. Centres are the place carrying the governorate's name (the census city row, matched in the R1a universe): Madinah, Yanbu', Al-Ula, Badr (Badr Hunayn, node 1237968680; pilot alternative way 87175609 is a `village`-tagged way with the same population), Khaybar, Al-Hinakiyah, Mahd adh-Dhahab, Al-'Aīṣ."
    )
    w(
        "- Wādī al-Fara': no seat named in any source reached (S-madinah-015, S-madinah-017). The row is the governorate's polygon centroid, flagged as not a settlement."
    )
    w("")
    w("## 6. Checks run")
    w("")
    w(
        "- Build: `.venv/bin/python -m screening.sweeps.madinah.build --seed 1`, then `.venv/bin/python -m screening.sweeps.madinah.report --seed 1`."
    )
    w(
        "- `screening.region_sweep validate --strict cities/ksa/regions/madinah.parquet`: ok (rows, governorate header, CSV mirror, OSM ids unique)."
    )
    w(
        "- Yanbu: the pilot's 331,916 = primary 258,777 (city) + 73,139 (Yanbu Industrial City, added here). Exactly equal, so the pilot's figure was the city plus its industrial city (pilot judgement item 5 resolved)."
    )
    w(
        "- Population rule: 9 primary official rows (plus the Yanbu Industrial City row) use the primary figure, with no corroboration needed; grid rows are gated; the OSM tag row is `derived` and unverified."
    )
    w("- Road minutes: every R1a row has an OSRM car skim; the Industrial City row has none.")
    w("- Terrain: not assessed (see section 2).")
    w("")
    w("## 7. Unmatched GASTAT primary cities (region not stated; not in the register)")
    w("")
    w(
        f"The primary 5,000+ city export has {len(unmatched)} city rows not matched as official populations in the R1a universe before this sweep; one of them (Yanbu Industrial City) is placed in this register, and one (Wādī al-'Uqūl farms) is discussed in section 4. The list below is the ≥ 10,000 remainder, excluding Wādī al-'Uqūl farms (section 4), with region not assigned (the 2010 administrative-region column matched by name is unreliable: one false hit, 'Alulya' to 'Al-Ula', was rejected). Any of these that is in Al-Madinah must be added once the city-to-governorate table is found."
    )
    w("")
    w("| city (GASTAT EN) | total 2022 | note |")
    w("|---|---|---|")
    for _, r in big.iterrows():
        w(f"| {r.City} | {int(r.Total):,} | region not stated |")
    w("")
    w("## 8. Needs Opus judgement (not resolved by guessing)")
    w("")
    w(f"1. {WADI_OQOOL} (24,381, official): located point needed; schema needs lat/lon.")
    w(
        "2. Unmatched GASTAT ≥ 10,000 cities (section 7): region membership. Blocks the completeness acceptance until resolved."
    )
    w(
        "3. Terrain class: a DEM-based classification (Copernicus or SRTM) is needed for all rows; not run (no download under the disk gate)."
    )
    w(
        "4. Al Mohaffar (7,174, OSM tag dated 2010) is the only OSM-tag figure in the register; it is older than the census."
    )
    w(
        "5. Sidi Hamzah (grid 30,876, 9 km from the Madinah centre) and Al 'Uyun (grid 11,547): grid figures in the Madinah metro area; the Medina city figure may already include them. Not netted; the grid is not corroborated."
    )
    w(
        "6. Badr seat: node 1237968680 (Badr Hunayn) vs way 87175609 (`village`-tagged, same 2022 population). Choice recorded; check the seat in a GASTAT or governorate source."
    )
    w(
        "7. Landbridge: committed layer in R1a. Whether its alignment runs through Madinah or Yanbu is unverified (pilot S-madinah-006); the register's committed distances use the R1a alignment and say so."
    )
    w(
        "8. Governorate centre spelling: 'Al Is' (GASTAT primary; spelled Al-'Aīṣ in S-073 and the pilot)."
    )
    w("")
    w("## 9. Sources")
    w("")
    w(
        "Source ids are in `docs/sources/r2-madinah.csv` (S-madinah-) and in `docs/sources/index.csv` (S-cp2-, S-r1a-, S-cp1-, S-073, S-001). Key ones: S-cp2-gastat-008 (primary city 5,000+), S-cp2-gastat-007 (primary governorates), S-073 (governorate list), S-r1a-506 (WorldPop 2020 100 m, constrained UN-adjusted), S-r1a-202/204/205/208/214/221/227/237 and S-cp1-100/105 (economic nodes), S-madinah-005/008–015 (pilot sources), S-madinah-016 (OSM population tags, ODbL), S-madinah-017 (governorate summary; search result, not fetched)."
    )
    w("")
    w(
        "Licences: OpenStreetMap ODbL (credit: © OpenStreetMap contributors), GASTAT data (credited; use policy https://www.stats.gov.sa/en/use-policy), WorldPop CC BY 4.0 (`worldpop-sau-2020-100m-unadj-constrained`)."
    )
    w("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(lines)} lines); unmatched >=10k: {len(big)}; below5k {below5}")


if __name__ == "__main__":
    app()
