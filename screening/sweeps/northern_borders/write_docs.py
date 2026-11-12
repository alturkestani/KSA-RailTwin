"""Writes docs/regions/northern_borders.md from the register, so the two agree.  # noqa: E501

uv run python -m screening.sweeps.northern_borders.write_docs   (repo root, venv python)
"""

from __future__ import annotations

import pandas as pd

from screening.sweeps.northern_borders.build import OUT_PQ, PILOT, REGION, ROOT, UNIVERSE

OUT_MD = ROOT / "docs/regions/northern_borders.md"
GOV_PRIMARY = {"Arar": 202_719, "Rafha": 84_536, "Turayf": 66_004, "Al Uwayqilah": 20_318}


def _n(x: object) -> str:
    return "" if pd.isna(x) else f"{int(x):,}"


def _roles(rs: object) -> str:
    rs = list(rs) if rs is not None else []  # Parquet returns numpy arrays for list columns
    return "; ".join(f"{x['role']} ({x['source']})" for x in rs) if rs else "none sourced"


def main() -> None:
    df = pd.read_parquet(OUT_PQ)
    pilot = pd.read_parquet(PILOT)
    u = pd.read_parquet(UNIVERSE)
    u = u[u.region == REGION]

    n_tag10 = int(df.tag_10k.sum())
    n_tag5 = int(df.tag_5k.sum())
    n_grid10 = int(((df.pop_type == "grid") & (df.population >= 10_000)).sum())
    n_grid = int(((df.pop_type == "grid") & df.population.notna()).sum())
    n_off = int((df.pop_type == "official").sum())
    n_sec = int((df.pop_source_status == "secondary").sum())
    n_ver = int((df.pop_source_status == "verified").sum())
    n_scr = int(df.screened.sum())
    n_excl = int((~df.screened).sum())
    n_roles = int((df.economic_roles.map(lambda x: len(x)) > 0).sum())
    n_centres = int(df.is_governorate_centre.sum())
    gov_sum = sum(GOV_PRIMARY.values())

    # the pilot register has no osm_type, so pilot rows join on osm_id alone (ids checked unique)
    align = u[["osm_id", "dist_existing_any_line_km", "nearest_existing_any_line"]]
    pm = pilot[["osm_id", "name_en", "dist_existing_km", "dist_metro_km"]].dropna(subset=["osm_id"])
    pm = pm.merge(align.drop_duplicates("osm_id"), on="osm_id", how="inner")
    pm = pm.merge(df[["osm_id", "dist_metro_km"]].drop_duplicates("osm_id"), on="osm_id",
                  how="left", suffixes=("_pilot", "_r2"))  # fmt: skip

    L: list[str] = []
    a = L.append
    a("> **Document version:** docs/regions/northern_borders.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_NORTHERN_BORDERS, R2) | Status: draft")  # fmt: skip  # noqa: E501
    a("")
    a("# Northern Borders (الحدود الشمالية): region sweep (R2)")
    a("")
    a("Slug `northern_borders` · Register `cities/ksa/regions/northern_borders.parquet` (CSV mirror alongside) · Label: **screening input, not a forecast**. Access date for every source: 31 Oct 2026 (Asia/Riyadh) unless stated. Population is the settlement figure, never a governorate total.")  # fmt: skip  # noqa: E501
    a("")
    a("## Governorate count")
    a("")
    a("- `governorates_gastat: 4`: GASTAT Census 2022 TA1 primary export, 150 governorates (S-cp2-gastat-007). Arar 202,719; Rafha 84,536; Turayf 66,004; Al Uwayqilah 20,318.")  # fmt: skip  # noqa: E501
    a(f"- `governorates_listed: 4`: each has a row for its centre ({n_centres} centre rows).")
    a(f"- Cross-check: the four governorate totals sum to {gov_sum:,}, equal to the TA1 region total of 373,577 (`runs/gastat/primary/control_total.csv`). The relayed list (S-northern_borders-002, -003) also gives four. No discrepancy.")  # fmt: skip  # noqa: E501
    a("")
    a("## Counts")
    a("")
    a("| item | count | note |")
    a("|---|---|---|")
    a(f"| register rows | {len(df)} | every settlement in the R1a universe for this region; {n_scr} screened, {n_excl} excluded with a reason (table below) |")  # fmt: skip  # noqa: E501
    a(f"| tag_10k = true | {n_tag10} | Arar, Rafha, Turayf, Al-Uwayqilah: primary GASTAT city figures (S-cp2-gastat-008) |")  # fmt: skip  # noqa: E501
    a(f"| grid-only ≥ 10,000, not tagged | {n_grid10} | Linah (17,616) and Badanah (10,670): no corroborating method run (A-screen-032) |")  # fmt: skip  # noqa: E501
    a(f"| tag_5k = true (sensitivity) | {n_tag5} | the four above, Rawdat Habbas (5,620, primary), and Linah and Badanah (grid; tag_5k is not gated) |")  # fmt: skip  # noqa: E501
    a(f"| screened = true | {n_scr} | the 4 centres, the ≥5,000 places, and Hazm al Jalamid (sourced mining role) |")  # fmt: skip  # noqa: E501
    a(f"| excluded (screened = false) | {n_excl} | exclusion reason per row |")
    a(f"| rows with ≥ 1 sourced economic role | {n_roles} | airports, university, border post, industrial city, mining; governorate seats (administrative) |")  # fmt: skip  # noqa: E501
    a(f"| populations: official / secondary / grid | {n_off} / {n_sec} / {n_grid} | official = {n_ver} primary GASTAT figures + {n_sec} relayed (`secondary`); grid rows unverified |")  # fmt: skip  # noqa: E501
    a("")
    a(f"Facts status: {n_ver} rows verified (GASTAT primary, S-cp2-gastat-008); {n_sec} secondary (citypopulation.de, S-northern_borders-001: At Timyat, Ash Shu'bah); {n_grid} grid gap-fills unverified (S-r1a-506). Grid rows carry no corroboration in this sweep: no second method was run, and the 2010-growth check has no 2010 entry for Linah or Badanah.")  # fmt: skip  # noqa: E501
    a("")
    a("## Register")
    a("")
    a("Distances per R1a: `dist_existing_km` is great circle to the 15 intercity passenger stations (A-r1a-008) with OSRM car road minutes over the 5 nearest (A-r1a-027, S-r1a-809); committed distances use alignment vertices at 1 km (A-r1a-007). Metro: nearest metro in the A-screen-013 set. Terrain assumed (A-northern_borders-001).")  # fmt: skip  # noqa: E501
    a("")
    a("| name (EN) | name (AR) | governorate | centre | population | pop_type | status | 10k | 5k | dist existing km (road min) | nearest metro (tier, km) | economic roles | terrain | screened | exclusion |")  # fmt: skip  # noqa: E501
    a("|---|---|---|---|---:|---|---|---|---|---:|---|---|---|---|---|")
    for _, r in df.iterrows():
        dist = f"{r.dist_existing_km:.1f} ({r.road_min_existing:.0f})"
        metro = f"{r.nearest_metro} (T{int(r.nearest_metro_tier)}, {r.dist_metro_km:.0f})"
        status = "" if pd.isna(r.pop_source_status) else str(r.pop_source_status)
        ptype = "" if pd.isna(r.pop_type) else str(r.pop_type)
        excl = "" if pd.isna(r.exclusion_reason) else str(r.exclusion_reason)
        a(f"| {r.name_en} | {r.name_ar} | {r.governorate} | {'yes' if r.is_governorate_centre else ''} | {_n(r.population)} | {ptype} | {status} | {'Y' if r.tag_10k else ''} | {'Y' if r.tag_5k else ''} | {dist} | {metro} | {_roles(r.economic_roles)} | {r.terrain_class} | {'Y' if r.screened else 'N'} | {excl} |")  # fmt: skip  # noqa: E501
    a("")
    a("## Notes by row")
    a("")
    for _, r in df[df.notes.fillna("") != ""].iterrows():
        a(f"- **{r.name_en}** ({r.name_ar}): {r.notes}")
    a("")
    a("## Changes from the pilot (`pilot-northern_borders`)")
    a("")
    a("The pilot measured great-circle distance to the OSM line geometry. The R1a alignment distance over all existing lines (`dist_existing_any_line_km`, A-r1a-007; includes the SAR North freight line S-019) is the same kind of measure, so it is the comparison here. The register's `dist_existing_km` is R1a's passenger-station distance, which is not comparable with the pilot's line distance. Population values for the pilot's rows are the same GASTAT primary figures (identical), now sourced to S-cp2-gastat-008.")  # fmt: skip  # noqa: E501
    a("")
    a("| name | pilot dist to existing line km | R2 alignment, any existing line km | nearest existing line (R2 alignment) | pilot dist metro km | R2 dist metro km |")  # fmt: skip  # noqa: E501
    a("|---|---:|---:|---|---:|---:|")
    for _, r in pm.iterrows():
        a(f"| {r.name_en} | {r.dist_existing_km:.1f} | {r.dist_existing_any_line_km:.1f} | {r.nearest_existing_any_line} | {r.dist_metro_km_pilot:.1f} | {r.dist_metro_km_r2:.1f} |")  # fmt: skip  # noqa: E501
    a("")
    a("## Exclusions (rule 2: none silent)")
    a("")
    a("Every settlement in the R1a universe for this region appears in the register. Excluded rows and their reasons are in the table above. Groups:")  # fmt: skip  # noqa: E501
    a("")
    for reason, k in df[~df.screened].exclusion_reason.fillna("").value_counts().items():
        a(f"- {k} × {reason}")
    a("")
    a("## Sources")
    a("")
    a("Population: S-cp2-gastat-007 (governorate totals, not used as populations), S-cp2-gastat-008 (primary city figures for places of 5,000 or more), S-cp2-gastat-001 (relayed DataPulse table, cross-check only: identical for the five primary cities), S-northern_borders-001 (citypopulation.de, secondary: At Timyat, Ash Shu'bah), S-r1a-506 (WorldPop 2020, 100 m, constrained, UN-adjusted; grid gap-fills).")  # fmt: skip  # noqa: E501
    a("")
    a("Geometry, distances and roles: S-r1a-210 (OSM element ids and coordinates), S-r1a-809 (OSRM car skims), S-cp1-100 (airports: GACA report), S-r1a-204 (MODON), S-r1a-211 (Ma'aden Al-Jalamid), S-r1a-221 and S-r1a-222 (universities), S-northern_borders-002 and -003 (governorate seats), S-northern_borders-010 (Nafud erg; terrain assumption). Lines: S-017 (SAR North passenger), S-019 (SAR North freight), S-029 (GCC railway), S-054 (Landbridge).")  # fmt: skip  # noqa: E501
    a("")
    a("Assumptions: `docs/assumptions-r2-northern_borders.md` (A-northern_borders-001…005). Population gate: A-screen-031…033; 2010 growth check A-screen-035; control total A-screen-037; roles A-screen-009.")  # fmt: skip  # noqa: E501
    a("")
    a("## Needs Opus judgement (not resolved by guessing)")
    a("")
    a("1. **Linah (KSA-ST-00393)**: grid 17,616, but absent from the GASTAT list of cities of 5,000 or more under any spelling tried. Which is right, the grid (an over-count, as the control total suggests) or the list? Sets tag_5k.")  # fmt: skip  # noqa: E501
    a("2. **Badanah (KSA-ST-00884)**: grid 10,670, absent from the ≥ 5,000 list. Is the unmatched primary name 'Albadie Walqarfi' (8,623; no OSM settlement by name) the same place? Sets tag_5k, and tag_10k only if a figure is confirmed.")  # fmt: skip  # noqa: E501
    a("3. **Jadidat Arar (KSA-ST-01533)**: a 2010 city of 5,125 (`runs/gastat/apply/cities2010_growth.csv`), absent from the 2022 list; WorldPop cells sum to 0. Merged into Arar, or below 5,000 in 2022? Population left null.")  # fmt: skip  # noqa: E501
    a("4. **Ash Shu'bah (KSA-ST-00391)**: secondary 3,430 vs grid 7,536. The sourced figure is used; a GASTAT locality table is needed to confirm it.")  # fmt: skip  # noqa: E501
    a("5. **Hazm al Jalamid (KSA-ST-00856)**: the R1a mining node sits on the mine polygon (31.507 N, 39.930 E), about 30 km from the OSM village node used as the row (R1a conflict, `docs/sources`). Which point is the town? The distance to the freight line differs by that choice.")  # fmt: skip  # noqa: E501
    a("6. **Waad Al-Shamal MODON industrial city** (R1a node `modon-waad-al-shamal`; S-r1a-204; position from the OSM phosphate feature): not a settlement in the R1a universe, so it has no row. Add a row, or keep it as a node only?")  # fmt: skip  # noqa: E501
    a("7. **Al-Haditha border post (Jordan)** (R1a node `border-haditha-jordan`): no town in this region is tied to it in the sources read; left unassigned.")  # fmt: skip  # noqa: E501
    a("8. **Arar border post**: the brief names Jadidat Arar; the OSM names do not say which post is meant (R1a node `border-arar-iraq`, which asks for escalation).")  # fmt: skip  # noqa: E501
    a("9. **SAR North passenger, layer `existing`** (`cities/ksa/lines/sar-north-passenger.yaml`, S-017): the R2 sweep does not re-verify the opening status of the passenger service. The `dist_existing_km` values depend on the passenger stations it lists.")  # fmt: skip  # noqa: E501
    a("10. **Unmatched primary cities with no region in the export** (69 in total). NB-plausible names: Albadie Walqarfi (8,623) and Aleuruq Alshamalia (5,783), both without an OSM settlement. The export has no region column, so they cannot be placed in this region from the export alone.")  # fmt: skip  # noqa: E501
    a(
        "11. **Terrain** is assumed for every row (A-northern_borders-001): no DEM run in this sweep."  # noqa: E501
    )
    a("")
    a("Label: screening input, not a forecast.")
    a("")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT_MD} ({len(L)} lines)")


if __name__ == "__main__":
    main()
