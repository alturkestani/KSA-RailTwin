# ruff: noqa: E501, SIM102  (R2 merge: sweep script kept as written by the Jazan sweep)
"""REGION_JAZAN sweep builder (R2, `region-sweep` skill): writes cities/ksa/regions/jazan.parquet + .csv.

Inputs (read-only): cities/ksa/zones/settlements.parquet (R1a universe, GASTAT primary matches and
WorldPop gap-fill), cities/ksa/zones/economic_nodes.parquet, the GASTAT primary exports under
data/ksa/tables/gastat/ (city >= 5,000 and governorate), and the Jazan source rows in
docs/sources/index.csv. Every source id written to a row is checked against the index.

Run (no uv sync needed; the project venv):
  PYTHONPATH=. .venv/bin/python screening/sweeps/jazan/build_register.py
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common.schemas import RegionRow

REPO = Path(__file__).resolve().parents[3]
SETTLEMENTS = REPO / "cities/ksa/zones/settlements.parquet"
ECON = REPO / "cities/ksa/zones/economic_nodes.parquet"
CITY5K = REPO / "data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx"
GOV_PRIMARY = REPO / "data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx"
INDEX = REPO / "docs/sources/index.csv"
SOURCES_OWN = REPO / "docs/sources/r2-jazan.csv"
OUT_PARQUET = REPO / "cities/ksa/regions/jazan.parquet"
OUT_CSV = REPO / "cities/ksa/regions/jazan.csv"
REGION = "jazan"
LISTED = 17  # the working list of 17 governorates (docs/gastat-regions.md; S-jazan-001)
JAZAN_REGION_TOTAL = 1_404_997  # GASTAT Census 2022 region total (S-cp2-gastat-001)
HHR_MAKKAH = (21.4176557, 39.7885323)  # OSM node 10956967098 (S-jazan-008)
LANDBRIDGE_STATIONS = {  # cities/ksa/lines/landbridge.yaml (S-062 coordinates; class planned)
    "landbridge:al-jumum": ("Al-Jumum (Jumoum / Jamuma)", 21.621168, 39.698979),
    "landbridge:muwai": ("Muwai (Moya)", 22.436566, 41.761935),
}

# (EN governorate, AR governorate, centre OSM node id or None, extra note)
GOVERNORATES: list[tuple[str, str, int | None, str]] = [
    ("Jazan", "جيزان", 288992209, ""),
    ("Sabya", "صبيا", 1237961155, ""),
    ("Abu Arish", "أبو عريش", 8506762133, ""),
    ("Samtah", "صامطة", 1237961376, ""),
    ("Baysh", "بيش", 6391743774, ""),
    ("Damad", "ضمد", 1237961144, ""),
    ("Ahad al Masarihah", "أحد المسارحة", 7699743951, ""),
    ("Ad Dair", "الدائر", 4941110005, "centre named Alddayer in R1a"),
    ("Al Aridah", "العارضة", 1237961156, ""),
    ("Al Aydabi", "العيدابي", 1237961253, ""),
    ("Farasan", "فرسان", 1013176773, "island governorate"),
    ("Ad Darb", "الدرب", 1237960408, ""),
    ("At Tuwal", "الطوال", 1237961475, "centre below 5,000 in GASTAT (Other)"),
    ("Al Harth", "الحرث", None, "no OSM place node: placeholder centre (S-jazan-006)"),
    ("Ar Rayth", "الريث", 1237961077, "centre below 5,000 (grid)"),
    ("Harub", "هروب", 1237961726, "centre not tabulated by GASTAT (grid)"),
    ("Fayfa", "فيفاء", 1237961319, "centre with no grid population (R1a = 0)"),
]
GOV_CANON = {
    "Abu Arish Governorate": "Abu Arish",
    "Damad Governorate": "Damad",
    "Harub Governorate": "Harub",
    "Al Tuwal Governorate": "At Tuwal",
    "Faifa Governorate": "Fayfa",
    "Alddayer": "Ad Dair",
    "Ahad Al Masarihah": "Ahad al Masarihah",
}
GOV_AR = {en: ar for en, ar, _, _ in GOVERNORATES}

# Economic roles tied to a town (R1a economic_nodes first; pilot and new sources where R1a is silent).
ROLES: dict[int, list[tuple[str, str]]] = {
    288992209: [  # Jizan
        ("airport", "S-cp1-100;S-r1a-210"),
        ("port", "S-r1a-208"),
        ("industrial_city", "S-r1a-200;S-r1a-204;S-r1a-210"),
        ("university", "S-r1a-210;S-r1a-221;S-r1a-222"),
        ("energy", "S-jazan-016"),
    ],
    1013176773: [  # Farasan
        ("tourism", "S-r1a-210;S-r1a-244;S-jazan-010"),
        ("heritage", "S-jazan-011"),
    ],
    1237961376: [  # Samtah
        ("agriculture", "S-jazan-012"),
    ],
}

NOTE_BY_OSM: dict[int, str] = {
    288992209: (
        "JCPDI location conflict (S-jazan-009: 60 km north vs 60 km south-east): the RCJY node is used "
        "as R1a has it. Energy role: Jazan refinery 400,000 bpd operating (S-jazan-016, search snippet of "
        "Saudipedia and MEES; the town tie to Jizan city is not read in the page: confirm). Jazan Port "
        "(S-r1a-208) is unlocated (no coordinates)."
    ),
    1237961376: (
        "Agriculture role rests on a market description in a Saudipedia search snippet (S-jazan-012): not "
        "a production statistic and the page is not read: Needs Opus judgement."
    ),
    1013176773: (
        "Farasan is an island town: R1a road times (OSRM car, no ferry) are not meaningful for the "
        "island. Road minutes are reported as R1a has them."
    ),
    10989383620: (
        "GASTAT primary export lists 'Alkhadra'' at 5,861 (S-cp2-gastat-008). R1a carried a WorldPop 7,055 "
        "for this village and had no match; the primary figure takes precedence (A-screen-038): "
        "conflict log: grid 7,055 vs official 5,861 (+20.4 % grid over official)."
    ),
    4946646307: (
        "Al Jawah: WorldPop grid 21,104 for a village-tagged place that GASTAT does not tabulate; the "
        "grid figure is not corroborated (no second method; A-screen-031..033), so tag_10k is false."
    ),
    4941110005: "Centre of Ad Dair (name Alddayer in R1a and GASTAT's city list).",
    7699743950: (
        "Non-centre town larger than its governorate centre Ad Darb (9,940 vs 5,216): a schema edge, "
        "kept as the sweep rule (every town at or above 5k)."
    ),
    1237961253: "GASTAT city-list spelling: Alaydabi; R1a: Al 'Aydabi.",
}
SOURCE_OVERRIDE_NOTE = {
    1237961475: (
        "Not tabulated by GASTAT city list (under 5,000, 'Other'); the figure is citypopulation.de's "
        "relayed value (S-jazan-002, secondary); primary_to_find: GASTAT locality table (S-090 "
        "unreachable)."
    ),
}


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    r = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(h))


def terrain(lat: float, lon: float, osm: int | None) -> str:
    """Rule-based, not DEM (A-jazan-002). Escarpment for the Fayfa highlands centre."""
    if osm == 1237961319:
        return "escarpment_mountain"
    return "coastal" if lon < 42.75 else "mixed"


def index_ids() -> set[str]:
    """Global index plus this track's own source table (docs/sources/r2-jazan.csv)."""
    ids: set[str] = set()
    for path in (INDEX, SOURCES_OWN):
        with path.open(encoding="utf-8-sig") as fh:
            ids |= {row["id"] for row in csv.DictReader(fh)}
    return ids


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    st = pd.read_parquet(SETTLEMENTS)
    st = st[st.region == REGION].copy()
    econ = pd.read_parquet(ECON)
    econ = econ[econ.region == REGION]
    c5k = pd.read_excel(CITY5K)
    gov = pd.read_excel(GOV_PRIMARY)
    wanted = {g[0].lower() for g in GOVERNORATES}
    gov = gov[gov.Governorate.astype(str).str.lower().isin(wanted)]
    gov_total = int(gov.Total.sum())
    if gov_total != JAZAN_REGION_TOTAL:
        fail(f"sum of 17 governorate totals {gov_total} != region total {JAZAN_REGION_TOTAL}")
    if len(gov) != LISTED:
        fail(f"primary governorate table matched {len(gov)} of {LISTED} names")

    centre_ids = {g[2] for g in GOVERNORATES if g[2] is not None}
    sel = st[
        (st.population >= 5000) | (st.grid_population >= 5000) | (st.osm_id.isin(centre_ids))
    ].copy()
    # Al Harth centre: no place node in the R1a universe, so it is added from its placeholder point
    # (Nominatim bbox centre, S-jazan-006). Distance to the existing station by haversine (A-jazan-001).
    al_harth = {c: float("nan") for c in sel.columns}
    al_harth.update(
        region=REGION,
        name_en="Al Harth",
        name_ar="الحرث",
        governorate="Al Harth",
        lat=16.7842,
        lon=43.1529,
        dist_existing_km=haversine_km((16.7842, 43.1529), HHR_MAKKAH),
        _synthetic=True,
    )
    sel["_synthetic"] = False
    sel = pd.concat([sel, pd.DataFrame([al_harth])], ignore_index=True)

    primary_values = set(c5k.Total.astype("Int64").dropna().tolist())
    known_ids = index_ids()
    rows: list[dict[str, Any]] = []

    for _, r in sel.iterrows():
        osm = None if pd.isna(r.osm_id) else int(r.osm_id)
        is_centre = osm in centre_ids or bool(r["_synthetic"])
        gov_raw = str(r.governorate)
        gov_en = GOV_CANON.get(gov_raw, gov_raw)
        if gov_en not in GOV_AR:
            fail(f"unmapped governorate {gov_raw!r} for {r.name_en} ({osm})")
        pop = None if pd.isna(r.population) else int(r.population)
        pop_type = None if pd.isna(r.pop_type) else str(r.pop_type)
        status = None if pd.isna(r.pop_source_status) else str(r.pop_source_status)
        pop_src = None if pd.isna(r.pop_source) else str(r.pop_source)
        if pop_src == "gastat-census2022-ta1-city5k-xlsx":  # R1a label for the primary city export
            pop_src = "S-cp2-gastat-008"
        pop_year = None if pd.isna(r.pop_year) else int(r.pop_year)
        primary_to_find = None

        if osm == 10989383620:  # Alkhadra': primary GASTAT over WorldPop (A-screen-038)
            pop, pop_type, status = 5861, "official", "verified"
            pop_src, pop_year = "S-cp2-gastat-008", 2022
        if pop_src == "S-cp2-gastat-008":
            if pop not in primary_values:
                fail(f"official value {pop} for {r.name_en} not in GASTAT city >= 5,000 export")
        if osm == 1237961475:  # Al Tuwal: only the relayed value exists
            primary_to_find = "GASTAT Census 2022 locality table (S-090 unreachable)"
        if osm == 1237961319:  # Fayfa centre: R1a grid = 0 (no cells): no sourced figure
            pop, pop_type, status, pop_src, pop_year = None, None, None, None, None
        if pop_type == "grid" and pop == 0:
            pop, pop_type, status, pop_src, pop_year = None, None, None, None, None
        if osm is None and pop is None:  # Al Harth centre (no place node)
            pop_type = status = pop_src = pop_year = None

        if pop_type == "derived" and status == "secondary":
            pop_src = "S-r1a-210"  # OSM GCC extract population tag (contributor value)
        if pop_type == "grid":
            pop_src = "S-r1a-505"  # WorldPop 2020 100 m constrained, not UN-adjusted (A-r1a-004)
            pop_year = 2020
            status = "unverified"
        if pop_type == "official" and pop_src == "S-jazan-002":
            primary_to_find = (
                primary_to_find or "GASTAT Census 2022 locality table (S-090 unreachable)"
            )

        lat, lon = float(r.lat), float(r.lon)
        name_en = str(r.name_en) if not pd.isna(r.name_en) else f"unnamed WorldPop cluster {osm}"
        name_ar = str(r.name_ar) if not pd.isna(r.name_ar) else ""
        if osm is None:  # Al Harth centre: Nominatim bbox centre (S-jazan-006)
            lat, lon = 16.7842, 43.1529
            name_en, name_ar = "Al Harth", "الحرث"

        tag_5k = pop is not None and pop >= 5000
        is_grid = pop_type == "grid"
        tag_10k = (
            pop is not None and pop >= 10000 and not is_grid
        )  # grid: corroboration gate (none run)
        excl = None
        if is_grid and pop is not None and pop >= 10000:
            excl = "grid-only population, uncorroborated"

        sources = ["S-jazan-005" if osm else "S-jazan-006", "S-jazan-001"]
        if pop_src:
            sources.append(pop_src)
        if not pd.isna(r.dist_existing_km):
            sources += ["S-jazan-008"] + (["S-r1a-809"] if osm is not None else [])
        if not pd.isna(r.dist_committed_km):
            sources += ["S-054", "S-r1a-809"]
        if primary_to_find and "S-jazan-002" in (pop_src or ""):
            sources.append("S-jazan-002")

        roles: list[dict[str, str]] = []
        if is_centre:
            roles.append({"role": "administrative", "source": "S-jazan-001"})
        for role, src in ROLES.get(osm, []):
            roles.append({"role": role, "source": src})
            sources += [s for s in src.split(";")]

        notes: list[str] = []
        if is_centre:
            notes.append(f"Governorate centre of {gov_en}.")
        if osm in NOTE_BY_OSM:
            notes.append(NOTE_BY_OSM[osm])
        if osm in SOURCE_OVERRIDE_NOTE:
            notes.append(SOURCE_OVERRIDE_NOTE[osm])
        if is_grid:
            notes.append(
                "Population: WorldPop 2020 grid gap-fill (R1a, A-r1a-004); no official figure; "
                "pop_corroboration not run (A-screen-033); tag_10k false."
            )
        if pop_type == "derived" and status == "secondary":
            notes.append(f"Population: OSM population tag (contributor value, {pop_year}).")
        if pop is None and not is_grid:
            notes.append("No sourced population for this centre; left null (not guessed).")
        if osm is None:
            notes.append(
                "Placeholder point: no R1a node, so committed and metro distances and road minutes "
                "are not computed (null); existing distance is haversine."
            )

        dist_ex = None if pd.isna(r.dist_existing_km) else float(r.dist_existing_km)
        dist_ex_check = haversine_km((lat, lon), HHR_MAKKAH)
        if dist_ex is not None and abs(dist_ex - dist_ex_check) > 0.5:
            fail(f"existing distance for {name_en}: R1a {dist_ex} vs haversine {dist_ex_check:.2f}")
        cs = None if pd.isna(r.nearest_committed) else str(r.nearest_committed)
        cstation = None
        dist_com = None if pd.isna(r.dist_committed_km) else float(r.dist_committed_km)
        if cs in LANDBRIDGE_STATIONS:
            cstation, slat, slon = LANDBRIDGE_STATIONS[cs]
            chk = haversine_km((lat, lon), (slat, slon))
            if dist_com is not None and abs(dist_com - chk) > 0.5:
                fail(f"committed distance for {name_en}: R1a {dist_com} vs haversine {chk:.2f}")

        metro = None if pd.isna(r.nearest_metro_city) else str(r.nearest_metro_city)
        tier = None if pd.isna(r.nearest_metro_tier) else int(r.nearest_metro_tier)

        row: dict[str, Any] = {
            "name_ar": name_ar,
            "name_en": name_en,
            "region": REGION,
            "governorate": gov_en,
            "governorate_ar": GOV_AR[gov_en],
            "is_governorate_centre": bool(is_centre),
            "osm_id": osm,
            "osm_type": None if osm is None else str(r.osm_type),
            "lat": lat,
            "lon": lon,
            "population": pop,
            "pop_source": pop_src,
            "pop_year": pop_year,
            "pop_type": pop_type,
            "pop_source_status": status,
            "primary_to_find": primary_to_find,
            "pop_corroboration": None,
            "pop_corroboration_value": None,
            "tag_10k": tag_10k,
            "tag_5k": tag_5k,
            "dist_existing_km": dist_ex,
            "road_min_existing": None
            if pd.isna(r.road_min_existing)
            else float(r.road_min_existing),
            "nearest_existing": "Haramain HSR, Makkah station (existing)",
            "dist_committed_km": dist_com,
            "road_min_committed": None
            if pd.isna(r.road_min_committed)
            else float(r.road_min_committed),
            "nearest_committed": "Saudi Landbridge, Riyadh-Jeddah (committed layer; status announced)"
            if cs
            else None,
            "nearest_committed_station": cstation,
            "dist_metro_km": None if pd.isna(r.dist_metro_city_km) else float(r.dist_metro_city_km),
            "road_min_metro": None
            if pd.isna(r.road_min_metro_city)
            else float(r.road_min_metro_city),
            "nearest_metro": None if metro is None else metro.replace(" (tier", " (tier"),
            "nearest_metro_tier": tier,
            "economic_roles": roles,
            "terrain_class": terrain(lat, lon, osm),
            "screened": True,
            "exclusion_reason": excl,
            "sources": sorted(set(sources), key=sources.index),
            "fixture": False,
            "threshold_50k": None,
            "pilot_sample": None,
            "road_min_method": "osrm_table_mld_car: R1a skims, free-flow car, uncalibrated (S-r1a-809)",
            "dist_method": "haversine (A-jazan-001); checked against R1a distance fields",
            "notes": " | ".join(notes) if notes else None,
        }
        if row["dist_committed_km"] is None:
            row["nearest_committed"] = None
        rows.append(row)

    df = pd.DataFrame(rows)
    # GEO_VERIFY estimates (screening/sweeps/jazan/geo_estimates.py; record only, notes only).
    est_path = REPO / "runs/geo_verify/estimate-r2-jazan/estimates-r2.csv"
    if est_path.exists():
        for e in pd.read_csv(est_path).itertuples():
            if e.n_buildings == 0:
                msg = f"GEO_VERIFY 31 Oct 2026 (R2): no building cluster in the window, no estimate [{e.method_log_id}]"
            else:
                msg = (
                    f"GEO_VERIFY 31 Oct 2026 (R2; record only, back-test gate failed): derived estimate "
                    f"central {e.est_central:,.0f} (band {e.est_low:,.0f}-{e.est_high:,.0f}; WorldPop grid "
                    f"{e.grid:,.0f}, buildings x occupancy {e.buildings:,.0f}) [{e.method_log_id}]"
                )
            prior = df.at[e.row_in_file, "notes"]
            df.at[e.row_in_file, "notes"] = msg if pd.isna(prior) else f"{prior} | {msg}"
    missing_ids = sorted({s for r in rows for s in r["sources"] if s not in known_ids})
    if missing_ids:
        fail(f"source ids not in docs/sources/index.csv: {missing_ids}")
    # Every centre must appear exactly once.
    cen = df[df.is_governorate_centre]
    if len(cen) != LISTED or cen.governorate.nunique() != LISTED:
        fail(f"governorate centres {len(cen)} / governorates {cen.governorate.nunique()}")
    dup = df.dropna(subset=["osm_id"]).duplicated(subset=["osm_type", "osm_id"]).sum()
    if dup:
        fail(f"{dup} duplicate OSM ids")

    # Strict row validation against RegionRow.
    for i, rec in enumerate(df.to_dict(orient="records")):
        clean = {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in rec.items()}
        clean["economic_roles"] = list(clean["economic_roles"])
        try:
            RegionRow.model_validate(clean)
        except ValueError as e:
            fail(f"row {i} {rec['name_en']}: {str(e).splitlines()[0]}")

    df["economic_roles_csv"] = df["economic_roles"].map(
        lambda rs: ";".join(f"{x['role']}:{x['source']}" for x in rs) if rs else ""
    )
    df["sources_csv"] = df["sources"].map(";".join)

    table = pa.Table.from_pandas(
        df.drop(columns=["economic_roles_csv", "sources_csv"]).assign(
            osm_id=lambda d: d["osm_id"].astype("Int64"),
            population=lambda d: d["population"].astype("Int64"),
            pop_year=lambda d: d["pop_year"].astype("Int64"),
            nearest_metro_tier=lambda d: d["nearest_metro_tier"].astype("Int64"),
        ),
        preserve_index=False,
    )
    table = table.replace_schema_metadata(
        {
            "governorates_gastat": str(LISTED),
            "governorates_listed": str(LISTED),
        }
    )
    pq.write_table(table, OUT_PARQUET)

    csv_df = df.drop(columns=["economic_roles", "sources"]).rename(
        columns={"economic_roles_csv": "economic_roles", "sources_csv": "sources"}
    )
    csv_df.to_csv(OUT_CSV, index=False)

    n10 = int(df.tag_10k.sum())
    n5 = int(df.tag_5k.sum())
    print(f"rows={len(df)} centres={len(cen)} tag_10k={n10} tag_5k={n5}")
    print(
        "pop_type:",
        df.pop_type.value_counts(dropna=False).to_dict(),
        "| status:",
        df.pop_source_status.value_counts(dropna=False).to_dict(),
    )
    print(f"gov total check: {gov_total} == {JAZAN_REGION_TOTAL}")
    universe_n = len(st)
    universe_10k = int((st.population >= 10000).sum())
    write_md(df, universe_n, universe_10k)


OUT_MD = REPO / "docs/regions/jazan.md"


def write_md(df: pd.DataFrame, universe_n: int, universe_10k: int) -> None:
    """docs/regions/jazan.md: counts, table, exclusions, sources, open questions (from the register)."""
    n = len(df)
    pops = df.population.notna()
    by_type = df.pop_type.fillna("none").value_counts().to_dict()
    lines = [
        "> **Document version:** docs/regions/jazan.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_JAZAN, track r2-jazan) | Status: draft",
        "",
        "# Region register: Jazan (جازان), slug `jazan` (R2)",
        "",
        "Screening input, not a forecast. Built by `screening/sweeps/jazan/build_register.py` (register) and "
        "`screening/sweeps/jazan/geo_estimates.py` (GEO_VERIFY estimates, record only). Outputs: "
        "`cities/ksa/regions/jazan.parquet` and `.csv`. Validated with `screening.region_sweep validate --strict`.",
        "",
        "## Governorate count",
        "",
        "| item | value | source |",
        "|---|---|---|",
        f"| governorates_gastat | {LISTED} (derived: all 17 working-list names are in GASTAT's primary governorate export (S-cp2-gastat-007); their totals sum to the Jazan region total {JAZAN_REGION_TOTAL:,} (S-cp2-gastat-001); A-jazan-003) | S-cp2-gastat-007; S-cp2-gastat-001 |",
        f"| governorates_listed | {LISTED} (citypopulation.de, Census 2022 list) | S-jazan-001 |",
        "| Saudipedia count (emirate text) | 16 (conflict, not resolved) | S-jazan-003 |",
        "| GASTAT's own list | not read: portal.saudicensus.sa unreachable (S-jazan-015) | S-jazan-015 |",
        "",
        "## Counts",
        "",
        f"- Rows: {n} ({LISTED} governorate centres, {n - LISTED} other places at or above 5,000 on the figure used).",
        f"- Rows at or above 10,000 (`tag_10k`): {int(df.tag_10k.sum())}. Rows at or above 5,000 (`tag_5k`): {int(df.tag_5k.sum())}.",
        f"- Population types: official {by_type.get('official', 0)} (GASTAT primary city export {int((df.pop_source == 'S-cp2-gastat-008').sum())}; relayed {int((df.pop_source == 'S-jazan-002').sum())}); derived {by_type.get('derived', 0)} (OSM contributor tag, secondary); grid {by_type.get('grid', 0)} (WorldPop 2020 gap-fill, unverified); no figure {int((~pops).sum())}.",
        f"- R1a universe: {universe_n} places in region; {universe_10k} at or above 10,000 on R1a's figure. Not listed row by row: places below 5,000 on their figure (the register keeps every place at or above 5,000 and all 17 centres).",
        f"- Economic roles: {int(df.economic_roles.map(len).sum())} role entries on "
        f"{int((df.economic_roles.map(len) > 0).sum())} rows (each with an S- source; "
        f"administrative on the {LISTED} centres, the rest on Jizan, Farasan and Samtah).",
        "",
        "## Gates and checks",
        "",
        f"- Governorate totals sum to the region total: {JAZAN_REGION_TOTAL:,} = {JAZAN_REGION_TOTAL:,}.",
        "- Every official value appears in GASTAT's primary city >= 5,000 export (asserted in the builder).",
        "- Existing and committed distances agree with haversine to within 0.5 km (asserted; `dist_method: haversine`).",
        "- Grid-only populations: none corroborated (no second method run; A-screen-031..033). Al Jawah (21,104, grid) is the only grid row at or above 10,000; it is `tag_10k: false`.",
        "- Conflict logged: Alkhadra' (GASTAT 5,861 vs R1a WorldPop 7,055, +20.4 % grid over official). Official figure used (A-screen-038).",
        "- GEO_VERIFY (record only): 25 unsourced or relayed rows estimated; the back-test gate fails (median APE grid 0.667, buildings 0.595; `runs/geo_verify/backtest/summary.json`). Estimates are in `notes`, never in `population`.",
        "",
        "## Register",
        "",
        "| name | governorate | centre | population | type / status | 5k | 10k | km existing | road min existing | km committed | nearest metro (tier) | terrain | economic roles | exclusion |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in df.itertuples():
        pop = "" if pd.isna(r.population) else f"{int(r.population):,}"
        typ = "" if pd.isna(r.pop_type) else f"{r.pop_type} / {r.pop_source_status}"
        roles = ", ".join(x["role"] for x in r.economic_roles) if r.economic_roles else ""
        metro = "" if pd.isna(r.nearest_metro) else f"{r.nearest_metro}"
        dex = "" if pd.isna(r.dist_existing_km) else f"{r.dist_existing_km:.0f}"
        rmin = "" if pd.isna(r.road_min_existing) else f"{r.road_min_existing:.0f}"
        dcom = "" if pd.isna(r.dist_committed_km) else f"{r.dist_committed_km:.0f}"
        exc = "" if pd.isna(r.exclusion_reason) else r.exclusion_reason
        lines.append(
            f"| {r.name_en} / {r.name_ar} | {r.governorate} | {'yes' if r.is_governorate_centre else ''} | {pop} | {typ} | "
            f"{'Y' if r.tag_5k else ''} | {'Y' if r.tag_10k else ''} | {dex} | {rmin} | {dcom} | {metro} | "
            f"{r.terrain_class} | {roles} | {exc} |"
        )
    lines += [
        "",
        "## Exclusions",
        "",
        "- No row is screened out. One row is kept with `tag_10k: false` for an uncorroborated grid figure: Al Jawah (`grid-only population, uncorroborated`).",
        "- Al Harth centre: no OSM place node in R1a; placeholder point (S-jazan-006); population null.",
        "- Fayfa centre: R1a grid is 0 (no cells); population null.",
        "",
        "## Sources",
        "",
        "Population: S-cp2-gastat-008 (GASTAT primary city >= 5,000), S-cp2-gastat-007 and S-cp2-gastat-001 (governorate totals), S-jazan-002 (citypopulation.de, relayed; Al Tuwal only), S-r1a-210 (OSM population tag), S-r1a-505 (WorldPop 2020). Places and nodes: S-jazan-005 (OSM place nodes), S-jazan-006 (Al Harth placeholder), S-jazan-001 (governorate list). Distances: S-jazan-008 (Haramain station Makkah), S-054 and S-062 (Landbridge, committed layer, announced), S-r1a-809 (OSRM skims). Economic roles: S-r1a-200/204/208/210/221/222/244, S-cp1-100, S-jazan-009/010/011/012/016. Terrain: S-jazan-013 with A-jazan-002. Full rows: `docs/sources/r2-jazan.csv` and `docs/sources/index.csv`.",
        "",
        "## Needs Opus judgement (not resolved by guessing)",
        "",
        "1. Governorate count: 17 (derived from GASTAT's primary export) vs 16 (Saudipedia). GASTAT's own list was not read (S-jazan-015).",
        "2. Al Harth centre: placeholder coordinates from a Nominatim bbox centre; no OSM place node; population null.",
        "3. Jizan port and JCPDI location: two sources give 60 km north and 60 km south-east of Jizan (S-jazan-009). The RCJY node is used as R1a has it.",
        "4. Terrain classes are rule-based (A-jazan-002), not from Copernicus DEM. DEM classes are needed before use.",
        "5. Al Jawah (21,104, WorldPop only; village tag): is it a town? GASTAT does not tabulate it. Needs a second method or an official locality figure before any 10k use.",
        "6. Samtah agriculture role: from a Saudipedia market description in a search snippet (S-jazan-012); the page is not read.",
        "7. Jazan refinery (energy role on Jizan): operating at 400,000 bpd per MEES and Saudipedia (S-jazan-016, snippets); the town tie is to be confirmed on the page.",
        "8. Al Tuwal: no sourced border_crossing role; not assigned. Its population is citypopulation.de's relayed figure (secondary; GASTAT locality table not reachable).",
        "9. Farasan road times (OSRM car, no ferry) are not meaningful for an island town.",
        "10. Abu as Sadad (9,940) is larger than its governorate centre Ad Darb (5,216): a schema edge, kept.",
        "11. GEO_VERIFY estimates are record only: the back-test gate fails, and the estimator covers only the rows listed in the notes (25 of 50).",
        "",
        "Label: screening input, not a forecast.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
