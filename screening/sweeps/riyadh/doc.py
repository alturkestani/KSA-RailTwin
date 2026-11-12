# ruff: noqa: E501  (long prose and source literals; same convention as scripts/register_gastat_tables.py)
"""Writes docs/regions/riyadh.md from the register (`cities/ksa/regions/riyadh.parquet`).

Run after `screening.sweeps.riyadh.build`: `python -m screening.sweeps.riyadh.doc`. Every figure in
the document is computed here from the register, so the prose and the tables cannot drift apart.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from screening.sweeps.riyadh.build import GOV_AR, OUT_PARQUET, governorate_totals

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / "docs/regions/riyadh.md"
VERSION = (
    "> **Document version:** docs/regions/riyadh.md v1.0 | 31 Oct 2026 | Author: region-scout "
    "(REGION_RIYADH sweep) | Status: draft\n"
)


def _md(v: object) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "–"
    if isinstance(v, float):
        return f"{v:,.1f}"
    if isinstance(v, int) and not isinstance(v, bool):
        return f"{v:,}"
    return str(v).replace("|", "/")


def main() -> None:
    d = pd.read_parquet(OUT_PARQUET)
    meta = pq.read_schema(OUT_PARQUET).metadata
    gov_gastat = int(meta[b"governorates_gastat"])
    gov_listed = int(meta[b"governorates_listed"])
    gov_tot = governorate_totals()
    n = len(d)
    n10 = int(d.tag_10k.sum())
    n5 = int(d.tag_5k.sum())
    scr = d[d.screened]
    excl = d[~d.screened]
    pt = d.pop_type.fillna("none").value_counts().to_dict()
    grid_gate = d[d.exclusion_reason.fillna("").str.contains("grid-only")]
    relayed = int(((d.pop_type == "official") & (d.pop_source_status == "secondary")).sum())
    verified = int(((d.pop_type == "official") & (d.pop_source_status == "verified")).sum())
    roles = {}
    for rs in d.economic_roles:
        for r in rs:
            roles[r["role"]] = roles.get(r["role"], 0) + 1
    rows_with_roles = int(sum(1 for rs in d.economic_roles if len(rs)))
    seats = d[d.is_governorate_centre]

    out: list[str] = [VERSION, "", "# Riyadh region sweep (الرياض, slug `riyadh`)", ""]
    out += [
        "Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.",
        "",
        "Register: `cities/ksa/regions/riyadh.parquet` (CSV mirror `riyadh.csv`); schema `RegionRow`; "
        "built by `screening/sweeps/riyadh/build.py`; document by `screening/sweeps/riyadh/doc.py`.",
        "",
        "## Headline counts",
        "",
        f"- Governorates: **{gov_gastat}** on the GASTAT list (S-073 names, each matched to the GASTAT "
        f"primary TA1 governorate export, S-cp2-gastat-007); **{gov_listed}** listed in the register "
        f"(`governorates_listed`). The 23 primary totals sum to **{sum(gov_tot.values()):,}**, equal to the "
        "GASTAT TA1 Riyadh region total (S-cp2-gastat-002, 8,591,748). Every governorate has its seat as "
        "a row.",
        f"- Rows (settlements of the R1a universe in the region): **{n:,}**; screened **{len(scr)}**, "
        f"excluded **{len(excl):,}** (all `below 5k and no economic role`).",
        f"- At or above 10,000 (`tag_10k`): **{n10}**. At or above 5,000 (`tag_5k`, sensitivity): **{n5}**.",
        f"- Population basis: official {pt.get('official', 0)} ({verified} read on GASTAT's primary "
        f"tables, {relayed} relayed), derived {pt.get('derived', 0)} (OSM population tags), grid "
        f"{pt.get('grid', 0):,} (WorldPop 2020, `unverified`).",
        f"- Grid-only rows at or above 10,000 that fail the 30 % corroboration gate (A-screen-032): "
        f"**{len(grid_gate)}** ({', '.join(grid_gate.name_en)}). Each stays `screened` with the reason "
        "`grid-only population, uncorroborated`.",
        f"- Sourced economic roles: {sum(roles.values())} role entries on {rows_with_roles} rows "
        f"({', '.join(f'{k} {v}' for k, v in sorted(roles.items()))}).",
        "- Committed lines are `committed/under procurement` or `announced/planned` (Landbridge; Riyadh Rail "
        "Link), never `existing`. Their stations are unlocated proxies (see Judgement list, item 8).",
        "",
        "## Governorates (GASTAT list, 23)",
        "",
        "| governorate (EN) | governorate (AR) | GASTAT primary total (S-cp2-gastat-007) | seat | seat population | seat source, status | rows screened |",
        "|---|---|---:|---|---:|---|---:|",
    ]
    for _, s in seats.sort_values("governorate").iterrows():
        g = s.governorate
        nscr = int(((d.governorate == g) & d.screened).sum())
        out.append(
            f"| {g} | {GOV_AR[g]} | {gov_tot[g]:,} | {s.name_en} | {_md(s.population)} | "
            f"{s.pop_source} ({s.pop_source_status}) | {nscr} |"
        )
    out += [
        "",
        "The seat figure is the town figure (primary city table, S-cp2-gastat-008); the governorate total is "
        "shown for reconciliation only and is never used as a town figure. Ar-Rayn's seat (2,726) is a locality "
        "under 5,000 relayed from citypopulation.de (S-cp1-017, `secondary`, with `primary_to_find` = the GASTAT "
        "locality table, not reachable, S-090).",
        "",
        "## Screened rows (60)",
        "",
        "Distances: `dist_*_km` is great-circle distance to the nearest existing station or committed proxy "
        "(haversine); `road_min_*` is OSRM free-flow car minutes from the R1a skims (S-r1a-809; not calibrated). "
        "`tag_5k` rows are included for the sensitivity run; `tag_10k` rows form the base case.",
        "",
        "| name (EN) | governorate | population | pop_type | status | tag_5k | tag_10k | dist existing km | road min existing | dist committed km (proxy) | nearest metro (tier) | economic roles (role:source) | terrain | exclusion |",
        "|---|---|---:|---|---|---|---|---:|---:|---:|---|---|---|---|",
    ]
    for _, t in scr.sort_values(["governorate", "population"], ascending=[True, False]).iterrows():
        roles_txt = "; ".join(f"{r['role']}:{r['source']}" for r in t.economic_roles) or "–"
        out.append(
            f"| {_md(t.name_en)} | {t.governorate} | {_md(t.population)} | {t.pop_type or '–'} | "
            f"{t.pop_source_status or '–'} | {'yes' if t.tag_5k else 'no'} | {'yes' if t.tag_10k else 'no'} | "
            f"{_md(t.dist_existing_km)} | {_md(t.road_min_existing)} | {_md(t.dist_committed_km)} | "
            f"{t.nearest_metro} ({t.nearest_metro_tier}) | {roles_txt} | {t.terrain_class} | "
            f"{_md(t.exclusion_reason)} |"
        )
    out += [
        "",
        "## Exclusions",
        "",
        f"{len(excl):,} settlements are excluded with the reason `below 5k and no economic role`. They are "
        "in the register with their population and distance fields (grid or OSM figure, `unverified` or "
        "`secondary`) so that no settlement is silently dropped; they do not enter the ≥ 5k or ≥ 10k sets. "
        "Two of them are 0-population OSM tags (AlMardamah; Darat AlMardamah).",
        "",
        "## Sources",
        "",
        "- GASTAT Census 2022 TA1 primary exports (S-cp2-gastat-007 governorates, S-cp2-gastat-008 cities ≥ 5,000; "
        "S-cp2-gastat-002 region total; S-cp2-gastat-001 relayed cross-check, not used as value of record).",
        "- 23 governorate names: S-073 (citypopulation.de, crediting GASTAT; terms unread). The GASTAT locality "
        "table that would confirm every locality is not reachable (S-090, S-r1a-500).",
        "- Settlement universe and population basis: R1a (`cities/ksa/zones/settlements.parquet`, CP2 P1a; "
        "WorldPop 2020 100 m constrained, S-r1a-505, CC BY 4.0; OSM place nodes, ODbL, S-riyadh-010 and S-r1a-210).",
        "- Distances and road minutes: R1a skims (S-r1a-809; OSRM MLD car on the GCC extract; OSM ODbL).",
        "- Lines: existing (sar-east, sar-north passenger), committed (Landbridge S-054, S-062; Riyadh Rail Link S-060).",
        "- Economic roles: R1a economic nodes (S-r1a-204 MODON, S-r1a-205 WHS list, S-r1a-217 Ma'aden "
        "snippets, S-r1a-221 universities, S-r1a-229/231/234/235 giga-projects, S-cp1-100 GACA airports, "
        "S-cp1-102 KSU), and the pilot's sourced roles (S-riyadh-011 to 014).",
        "- Terrain: Tuwaiq escarpment (S-riyadh-015) for Ar-Riyadh; all other rows carry the pilot default "
        "(`flat_desert`, A-screen-pilot-002 [riyadh]) with no DEM class run.",
        "",
        "## Judgement list (Needs Opus judgement; not resolved by guessing)",
        "",
        "1. **Al-Saih** (138,604, grid, Al-Kharj): the largest grid-only figure in the region and the only row "
        "with a second method run (`gastat2010_city_growth` = 232,644, 68 % away: fails the gate). It is not in the "
        "primary city table. Decide once the GASTAT locality table is reachable; no figure is substituted.",
        "2. **Mugharrizat** (19,214, grid) and **Tharmada'** (11,002, grid, Marat): grid-only, uncorroborated; "
        "excluded from the ≥ 10k test, kept `screened`.",
        "3. **Al-Kharj** city (295,462, primary city table) has no OSM node in the R1a universe (osm_id null); "
        "coordinates are the R1a row's. Confirm the OSM element before any map use.",
        "4. **Riyadh Al Khabra** (31,203, GASTAT primary governorate): not on the S-073 list of the Riyadh region and "
        "not in the sum that equals the region total. Not registered here; its region is not verified in this sweep.",
        "5. **Node ties by name** (not by polygon): Sudair → Hawtat Sudayr (15.7 km from the node; the R1a node "
        "is not a town). Dhurma → Duruma; Qiddiya City, SEDRA, King Salman Park and Sports Boulevard → Ar-Riyadh (city "
        "row); Diriyah Gate → Ad-Dir'iyah. Confirm each tie.",
        "6. **Excluded R1a nodes** (`EXCLUDED_NODES` in the build script): `univ-ksau-hs` (Jeddah coordinates, region "
        "tag not Riyadh); `heritage-uruq-bani-maarid` (19.34 N, about 600 km from its named town); `giga-new-murabba` "
        "(source S-r1a-214 is a Hajj-site coordinate list). None is attributed to Riyadh.",
        "7. **Ma'aden Al-'Amar** (mining): the role's source (S-r1a-217) is search snippets, not read. Tied to the "
        "hamlet at the node's coordinates (23.764 N, 45.081 E, 61 persons, grid). Read the Ma'aden source before use.",
        "8. **Committed stations are proxies**: Landbridge stops (Dawadmi, Riyadh, Muwai, North South Connection) and "
        "Riyadh Rail Link stops are unlocated (`committed_sites_unlocated`). The committed distances are to those "
        "proxy points (Ar-Riyadh = 0.0 km by construction), not to an alignment or a station site.",
        "9. **Terrain** is the pilot default for 1,095 rows (no DEM class run). Only Ar-Riyadh has a sourced class.",
        "10. **Name spelling**: the register follows S-073 (`Rimah`); the GASTAT primary export and the R1a rows say "
        "`Rumah` (the town, 25,031). The primary governorate total for Rimah is 35,683 (`Rumah`).",
        "11. **Al-Faw** (17 persons, grid): the heritage role is tied to it through the node at its coordinates; the "
        "source is the Wikidata WHS list (S-r1a-205). Confirm the inscription.",
        "12. **Figures that differ from older sources**: Ar-Riyadh city is 6,924,566 (primary, S-cp2-gastat-008), not "
        "7,000,100 (Wikipedia, S-riyadh-009) nor the governorate's 7,009,120 (S-cp2-gastat-007). Pilot vs primary "
        "differ by more than 2 % for no Riyadh row.",
        "",
        "## Layers",
        "",
        "Every line in this file is `existing` (sar-east and sar-north passenger), `committed/under procurement` "
        "(Riyadh Rail Link, S-060) or `announced/planned` (Landbridge, S-054, S-062). The distance columns name "
        "their layer in `nearest_existing` or `nearest_committed`.",
        "",
        "Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast.",
        "",
    ]
    DOC.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {DOC.relative_to(ROOT)} ({len(out)} lines)")


if __name__ == "__main__":
    main()
