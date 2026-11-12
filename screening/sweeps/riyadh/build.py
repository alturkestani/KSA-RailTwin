# ruff: noqa: E501  (long prose and source literals; same convention as scripts/register_gastat_tables.py)
"""Riyadh region sweep (REGION_RIYADH, W2): one row per settlement of the Riyadh region.

Inputs (read only): `cities/ksa/zones/settlements.parquet` (R1a universe with the CP2 population
basis and the R1a OSRM skims), `cities/ksa/zones/economic_nodes.parquet`, the pilot register
`cities/ksa/regions/pilot-riyadh.csv` (sourced university, heritage, giga-project and military roles),
and the GASTAT primary TA1 governorate export (governorate count and total check only).

Outputs: `cities/ksa/regions/riyadh.parquet` (governorate counts in the key-value header) and the
CSV mirror. The prose in `docs/regions/riyadh.md` is written by hand from the figures this script
prints (`uv run python -m screening.sweeps.riyadh.build`).

Every settlement of the region is in the register: screened rows, and rows excluded with a reason
(rule 2). Population rule (CP2 P1a, A-screen-031…039): the primary GASTAT city table first, then
the relayed seat figure, then the OSM tag, then the WorldPop grid (gated).
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common.schemas import GRID_UNCORROBORATED, TAG_5K, TAG_10K, RegionRow, corroborates

ROOT = Path(__file__).resolve().parents[3]
SETTLEMENTS = ROOT / "cities/ksa/zones/settlements.parquet"
ECON = ROOT / "cities/ksa/zones/economic_nodes.parquet"
PILOT = ROOT / "cities/ksa/regions/archive/pilot/pilot-riyadh.csv"
GOV_PRIMARY = ROOT / "data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx"
OUT_PARQUET = ROOT / "cities/ksa/regions/riyadh.parquet"
OUT_CSV = ROOT / "cities/ksa/regions/riyadh.csv"
WORK = ROOT / "data/ksa/riyadh/work"  # gitignored working files

REGION = "riyadh"
GOVERNORATES_GASTAT = (
    23  # S-073 list of Riyadh-region governorates (citypopulation.de, GASTAT list)
)
REGION_TOTAL_TA1 = 8_591_748  # S-cp2-gastat-002, GASTAT TA1 Riyadh region total

# Settlement-universe governorate label (R1a polygon name) -> register governorate (S-073 spelling).
GOV_MAP = {
    "Riyadh governorate": "Ar-Riyadh",
    "Ad Duwadimi": "Ad-Dawadmi",
    "Ad Dilam": "Ad-Dilam",
    "Ad Diriyah": "Ad-Dir'iyah",
    "Afif": "'Afif",
    "Al Aflaj": "Al-Aflaj",
    "Al Ghat": "Al-Ghat",
    "Al Hariq": "Al-Hariq",
    "Al Kharj": "Al-Kharj",
    "Al Majmaah": "Al-Majma'ah",
    "Al Muzahimiyah": "Al-Muzahimiyah",
    "Al Quwayiyah": "Al-Quwayiyah",
    "Ar Rayn": "Ar-Rayn",
    "As Sulayyil": "As-Sulayyil",
    "Az Zulfi": "Az-Zulfi",
    "Duruma": "Durma",
    "Hawtat Bani Tamim": "Hawtat Bani Tamim",
    "Huraymila": "Huraymila",
    "Marat": "Marat",
    "Rumah": "Rimah",
    "Shaqra": "Shaqra",
    "Thadiq": "Thadiq",
    "Wadi Ad Dawasir": "Wadi ad-Dawasir",
}
# Register governorate -> name in the GASTAT primary governorate export (S-cp2-gastat-007)
PRIMARY_NAME = {
    "Ar-Riyadh": "Ar Riyadh",
    "Ad-Dawadmi": "Ad Duwadimi",
    "Ad-Dilam": "Ad Dilam",
    "Ad-Dir'iyah": "Ad Diriyah",
    "'Afif": "Afif",
    "Al-Aflaj": "Al Aflaj",
    "Al-Ghat": "Al Ghat",
    "Al-Hariq": "Al Hariq",
    "Al-Kharj": "Al Kharj",
    "Al-Majma'ah": "Al Majmaah",
    "Al-Muzahimiyah": "Al Muzahimiyah",
    "Al-Quwayiyah": "Al Quwayiyah",
    "Ar-Rayn": "Ar Rayn",
    "As-Sulayyil": "As Sulayyil",
    "Az-Zulfi": "Az Zulfi",
    "Durma": "Duruma",
    "Hawtat Bani Tamim": "Hawtat Bani Tamim",
    "Huraymila": "Huraymila",
    "Marat": "Marat",
    "Rimah": "Rumah",
    "Shaqra": "Shaqra",
    "Thadiq": "Thadiq",
    "Wadi ad-Dawasir": "Wadi Ad Dawasir",
}
# Arabic governorate names (docs/gastat-regions.md, S-073 table; transliteration match)
GOV_AR = {
    "Ar-Riyadh": "الرياض",
    "Ad-Dawadmi": "الدوادمي",
    "Ad-Dilam": "الدلم",
    "Ad-Dir'iyah": "الدرعية",
    "'Afif": "عفيف",
    "Al-Aflaj": "الأفلاج",
    "Al-Ghat": "الغاط",
    "Al-Hariq": "الحريق",
    "Al-Kharj": "الخرج",
    "Al-Majma'ah": "المجمعة",
    "Al-Muzahimiyah": "المزاحمية",
    "Al-Quwayiyah": "القويعية",
    "Ar-Rayn": "الرين",
    "As-Sulayyil": "السليل",
    "Az-Zulfi": "الزلفي",
    "Durma": "ضرما",
    "Hawtat Bani Tamim": "حوطة بني تميم",
    "Huraymila": "حريملاء",
    "Marat": "مرات",
    "Rimah": "رماح",
    "Shaqra": "شقراء",
    "Thadiq": "ثادق",
    "Wadi ad-Dawasir": "وادي الدواسر",
}
# Governorate seat -> settlement_id (the seat row of the R1a universe; the Al-Kharj seat is the
# primary city table row, which has no OSM node)
SEAT_ID = {
    "Ar-Riyadh": "KSA-ST-00035",
    "Ad-Dawadmi": "KSA-ST-00609",
    "Ad-Dilam": "KSA-ST-00749",
    "Ad-Dir'iyah": "KSA-ST-00710",
    "'Afif": "KSA-ST-00048",
    "Al-Aflaj": "KSA-ST-00821",  # Layla, the seat (as in the pilot)
    "Al-Ghat": "KSA-ST-01141",
    "Al-Hariq": "KSA-ST-00801",
    "Al-Kharj": "KSA-ST-07371",
    "Al-Majma'ah": "KSA-ST-00388",
    "Al-Muzahimiyah": "KSA-ST-00280",
    "Al-Quwayiyah": "KSA-ST-00409",
    "Ar-Rayn": "KSA-ST-00410",
    "As-Sulayyil": "KSA-ST-00282",
    "Az-Zulfi": "KSA-ST-00300",
    "Durma": "KSA-ST-00741",
    "Hawtat Bani Tamim": "KSA-ST-00276",
    "Huraymila": "KSA-ST-00701",
    "Marat": "KSA-ST-00037",
    "Rimah": "KSA-ST-00709",
    "Shaqra": "KSA-ST-00670",
    "Thadiq": "KSA-ST-00283",
    "Wadi ad-Dawasir": "KSA-ST-01425",
}
# Sources
PRIMARY_CITY_SRC = "S-cp2-gastat-008"  # GASTAT TA1 primary city >= 5,000 table
PRIMARY_GOV_SRC = "S-cp2-gastat-007"  # GASTAT TA1 primary governorate table
REGION_TOTAL_SRC = "S-cp2-gastat-002"
GOV_LIST_SRC = "S-073"  # 23 Riyadh governorates (citypopulation.de, crediting GASTAT)
RELAYED_SEAT_SRC = "S-cp1-017"  # Ar-Rayn seat (relayed; locality under 5,000)
OSM_POP_SRC = "S-r1a-210"  # OSM GCC extract: population tags and element ids
WORLDPOP_SRC = (
    "S-r1a-505"  # WorldPop 2020 100 m constrained, not UN-adjusted (settlements pop_source)
)
ROAD_SRC = "S-r1a-809"  # OSRM MLD car free-flow minutes (R1a skims)
OSM_PLACE_SRC = "S-riyadh-010"  # OSM place nodes read for the pilot (ids and coordinates)
TUWAIQ_SRC = "S-riyadh-015"  # Tuwaiq escarpment (Riyadh city terrain)
TERRAIN_DEFAULT = "A-screen-pilot-002 [riyadh]"  # default flat_desert, no DEM class (A-riyadh-003)

COMMITTED = {
    "landbridge": ("Saudi Landbridge Riyadh-Jeddah rail (announced/planned)", ["S-054", "S-062"]),
    "riyadh-rail-link": (
        "Riyadh Rail Link, Landbridge Riyadh section (committed/under procurement)",
        ["S-060"],
    ),
}
# Nearest-town labels of the R1a economic nodes -> register settlement (name match; the distance
# between node and settlement is recorded in notes where it is not zero)
NODE_TOWN = {
    "Riyadh": "KSA-ST-00035",
    "Riyadh (Qiddiya City)": "KSA-ST-00035",
    "Ad-Dawadmi": "KSA-ST-00609",
    "Wadi ad-Dawasir": "KSA-ST-01425",
    "Diriyah": "KSA-ST-00710",
    "Sudair": "KSA-ST-00691",  # Hawtat Sudayr (name match; judgement, see notes)
    "Zulfi": "KSA-ST-00300",
    "Shaqra": "KSA-ST-00670",
    "Al-Kharj": "KSA-ST-07371",
    "Dhurma": "KSA-ST-00741",
    "Majmaah": "KSA-ST-00388",
    "Al Amar": "KSA-ST-05632",
    "Al-Faw": "KSA-ST-01853",
}
# R1a nodes not tied to a Riyadh town (judgement list in docs/regions/riyadh.md)
EXCLUDED_NODES = {
    "univ-ksau-hs": "R1a node at Jeddah coordinates (21.42 N, 39.36 E); the region tag is not a "
    "Riyadh location and the main campus is unverified",
    "heritage-uruq-bani-maarid": "node at 19.34 N, 45.90 E, about 600 km from its nearest_town "
    "Shaqra (25.18 N); the town tie does not hold",
    "giga-new-murabba": "source S-r1a-214 is a Wikidata list of Hajj and Umrah coordinates and "
    "does not tie New Murabba to a town",
}
# Pilot-sourced roles not carried by the R1a node table (S-riyadh-011 is the Majmaah University
# branch-campus list; the seat, Ad-Dir'iyah and Al-Kharj roles come from the pilot)
PILOT_ROLES = [
    ("KSA-ST-00710", "heritage", "S-riyadh-012"),  # At-Turaif, Ad-Dir'iyah
    ("KSA-ST-00710", "giga_project", "S-riyadh-013"),  # Diriyah Gate
    ("KSA-ST-07371", "military", "S-riyadh-014"),  # Prince Sultan Air Base, Al-Kharj
    ("KSA-ST-00388", "university", "S-riyadh-011"),  # Majmaah University, Al-Majma'ah
    ("KSA-ST-00300", "university", "S-riyadh-011"),  # branch campus, Az-Zulfi
    ("KSA-ST-01141", "university", "S-riyadh-011"),  # branch campus, Al-Ghat
    ("KSA-ST-00709", "university", "S-riyadh-011"),  # branch campus, Rumah
    ("KSA-ST-00691", "university", "S-riyadh-011"),  # branch campus, Hotat Sudair
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km (the registered haversine method; A-r1a-009 family)."""
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _s(v: Any) -> str | None:
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return None
    return str(v)


def _f(v: Any) -> float | None:
    if v is None or pd.isna(v):
        return None
    return float(v)


def roles_by_settlement(
    econ: pd.DataFrame,
) -> tuple[dict[str, list[dict[str, str]]], list[str], dict[str, list[tuple]]]:
    """settlement_id -> [{role, source}]; the nodes that could not be tied to a register row; and
    per settlement the node ties that need a note (unlocated node, or node more than 5 km away)."""
    out: dict[str, list[dict[str, str]]] = {}
    unresolved: list[str] = []
    ties: dict[str, list[tuple[str, str, float | None, float | None]]] = {}

    def add(sid: str, role: str, source: str) -> None:
        lst = out.setdefault(sid, [])
        if not any(x["role"] == role and x["source"] == source for x in lst):
            lst.append({"role": role, "source": source})

    for sid, role, src in PILOT_ROLES:  # pilot sources first: one entry per role and town
        add(sid, role, src)
    for n in econ.itertuples():
        if n.node_id in EXCLUDED_NODES:
            unresolved.append(f"{n.node_id}: {EXCLUDED_NODES[n.node_id]}")
            continue
        sid = NODE_TOWN.get(str(n.nearest_town_en))
        if sid is None:
            unresolved.append(
                f"{n.node_id}: nearest_town {n.nearest_town_en!r} has no register row"
            )
            continue
        src = (
            "S-cp1-100"
            if n.role == "airport"
            else next(x for x in str(n.source_id).split(";") if x.startswith("S-"))
        )
        if n.role == "mining":  # the Ma'aden site is in S-r1a-217 search snippets (not read)
            src = "S-r1a-217"
        add(sid, str(n.role), src)
        ties.setdefault(sid, []).append((n.role, n.node_id, _f(n.lat), _f(n.lon)))
    return out, unresolved, ties


def governorate_totals() -> dict[str, int]:
    """GASTAT primary governorate totals for the register governorates (S-cp2-gastat-007)."""
    g = pd.read_excel(GOV_PRIMARY)
    primary = {str(k): int(v) for k, v in zip(g["Governorate"], g["Total"], strict=True)}
    return {reg: primary[PRIMARY_NAME[reg]] for reg in GOV_AR}


def build_records() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    s = pd.read_parquet(SETTLEMENTS)
    r = s[s.region == REGION].copy()
    econ = pd.read_parquet(ECON)
    econ = econ[econ.region == REGION].copy()
    pilot = pd.read_csv(PILOT)
    pilot_pop = {
        int(p.osm_id): float(p.population) for p in pilot.itertuples() if pd.notna(p.osm_id)
    }
    roles, unresolved, ties = roles_by_settlement(econ)
    gov_totals = governorate_totals()
    seat_of = {v: k for k, v in SEAT_ID.items()}
    conflicts: list[str] = []
    records: list[dict[str, Any]] = []

    for t in r.itertuples():
        sid = t.settlement_id
        gov = GOV_MAP[t.governorate]
        seat = seat_of.get(sid) if seat_of.get(sid) == gov else None
        is_seat = seat is not None
        roles_here = roles.get(sid, [])
        notes: list[str] = []
        sources: list[str] = []

        name_en = _s(t.name_en) or ""
        name_ar = _s(t.name_ar) or (GOV_AR[gov] if is_seat else "")
        if not name_en:  # placeholder keeps the CSV mirror readable (an empty cell reads as NaN)
            name_en = f"(no English name: {sid})"
            notes.append("English name not in OSM (R1a); Arabic name only")
        if sid == "KSA-ST-07371":
            name_en = "Al-Kharj"
            notes.append(
                "primary city table row with no OSM node matched (osm_id null); coordinates "
                "from the R1a universe"
            )
        osm_id = None if pd.isna(t.osm_id) else int(t.osm_id)

        # ---- population (CP2 P1a)
        pb = t.population_basis
        pop = None if pd.isna(t.population) else int(t.population)
        pop_type = pop_src = pop_status = pop_year = primary_to_find = None
        corr = corr_val = None
        if pop is not None:
            if pb == "official" and t.pop_source == "gastat-census2022-ta1-city5k-xlsx":
                pop_type, pop_src, pop_status, pop_year = (
                    "official",
                    PRIMARY_CITY_SRC,
                    "verified",
                    2022,
                )
                sources.append(PRIMARY_CITY_SRC)
            elif pb == "official":
                pop_type, pop_src, pop_status, pop_year = (
                    "official",
                    RELAYED_SEAT_SRC,
                    "secondary",
                    2022,
                )
                primary_to_find = (
                    "GASTAT Census 2022 locality table (not reachable; S-090, S-r1a-500)"
                )
                sources.append(RELAYED_SEAT_SRC)
            elif pb.startswith("derived"):
                pop_type, pop_src, pop_status = "derived", OSM_POP_SRC, "secondary"
                pop_year = int(t.pop_year) if not pd.isna(t.pop_year) else 2010
                sources.append(OSM_POP_SRC)
                notes.append("OSM population tag (not a GASTAT figure)")
            elif pb == "grid_unverified":
                pop_type, pop_src, pop_status, pop_year = "grid", WORLDPOP_SRC, "unverified", 2020
                sources.append(WORLDPOP_SRC)
                if pop >= TAG_5K:
                    primary_to_find = (
                        "GASTAT Census 2022 locality table (not reachable; S-090, S-r1a-500)"
                    )
                if not pd.isna(t.pop_corroboration):
                    corr = str(t.pop_corroboration)
                    corr_val = float(t.pop_corroboration_value)
                    notes.append(
                        f"second method {corr} = {corr_val:,.0f} (pop_2010 x gov_2022 / gov_2010, A-screen-035)"
                    )
            else:
                raise ValueError(f"unknown population basis {pb!r} for {sid}")

        tag_10k = pop is not None and pop >= TAG_10K
        tag_5k = pop is not None and pop >= TAG_5K
        exclusion = None
        if pop_type == "grid" and tag_10k and (corr_val is None or not corroborates(pop, corr_val)):
            tag_10k = False
            exclusion = GRID_UNCORROBORATED
            notes.append("grid-only figure at or above 10,000 fails the 30 % corroboration gate")

        screened = bool(is_seat or roles_here or tag_5k)
        if not screened:
            exclusion = "below 5k and no economic role"

        # ---- sources, roles, committed and metro
        if is_seat:
            sources.extend([GOV_LIST_SRC, PRIMARY_GOV_SRC])
            notes.append(
                f"governorate total {gov_totals[gov]:,} (S-cp2-gastat-007; governorate, not the town figure)"
            )
        for item in roles_here:
            sources.append(item["source"])
        for role, node_id, nlat, nlon in ties.get(sid, []):
            if nlat is None:
                notes.append(f"economic node: {role} node {node_id} unlocated; tied by name")
            else:
                km = _haversine_km(nlat, nlon, float(t.lat), float(t.lon))
                notes.append(f"economic node: {role} node {node_id}, {km:.1f} km from the row")
        committed_name = committed_station = None
        ccl = _s(t.nearest_committed_line)
        if ccl:
            committed_name, csrcs = COMMITTED[ccl]
            sources.extend(csrcs)
            station = str(t.nearest_committed).split(":", 1)[1].replace("-", " ").title()
            committed_station = f"{station} (unlocated proxy)"
        sources.extend([ROAD_SRC, OSM_PLACE_SRC])

        if sid == "KSA-ST-00035":
            terrain = "escarpment_mountain"
            sources.append(TUWAIQ_SRC)
            notes.append("terrain escarpment_mountain: Tuwaiq escarpment (S-riyadh-015)")
        else:
            terrain = "flat_desert"
            notes.append(
                f"terrain flat_desert is the pilot default ({TERRAIN_DEFAULT}); no DEM class run"
            )
        if (
            osm_id is not None
            and pop is not None
            and osm_id in pilot_pop
            and pop_type == "official"
        ):
            pv = pilot_pop[osm_id]
            if abs(pv - pop) / pop > 0.02:
                conflicts.append(f"{name_en}: pilot {pv:,.0f} vs primary {pop:,} (> 2 %)")
        if _s(t.control_total_flag):
            notes.append(f"control total flag (reporting only): {t.control_total_flag}")
        if sid in {"KSA-ST-00691"} and not is_seat:
            notes.append("Hotat Sudair branch campus of Majmaah University (S-riyadh-011)")

        records.append(
            {
                "name_ar": name_ar,
                "name_en": name_en,
                "region": REGION,
                "governorate": gov,
                "governorate_ar": GOV_AR[gov],
                "is_governorate_centre": is_seat,
                "osm_id": osm_id,
                "osm_type": _s(t.osm_type),
                "lat": float(t.lat),
                "lon": float(t.lon),
                "population": pop,
                "pop_source": pop_src,
                "pop_year": pop_year,
                "pop_type": pop_type,
                "pop_source_status": pop_status,
                "primary_to_find": primary_to_find,
                "pop_corroboration": corr,
                "pop_corroboration_value": corr_val,
                "tag_10k": tag_10k,
                "tag_5k": tag_5k,
                "dist_existing_km": _f(t.dist_existing_km),
                "road_min_existing": _f(t.road_min_existing),
                "nearest_existing": _s(t.nearest_existing),
                "dist_committed_km": _f(t.dist_committed_km),
                "road_min_committed": _f(t.road_min_committed),
                "nearest_committed": committed_name,
                "nearest_committed_station": committed_station,
                "dist_metro_km": _f(t.dist_metro_city_km),
                "road_min_metro": _f(t.road_min_metro_city),
                "nearest_metro": re.sub(r"\s*\(tier \d\)", "", str(t.nearest_metro_city)),
                "nearest_metro_tier": int(t.nearest_metro_tier),
                "economic_roles": roles_here,
                "terrain_class": terrain,
                "screened": screened,
                "exclusion_reason": exclusion,
                "sources": sorted(set(sources)),
                "fixture": False,
                "threshold_50k": None,
                "pilot_sample": None,
                "road_min_method": "osrm_table_mld_car free flow (R1a skims, S-r1a-809)",
                "dist_method": "haversine",
                "notes": " | ".join(notes) if notes else None,
            }
        )
    records.sort(key=lambda x: (x["governorate"], -(x["population"] or 0), x["name_en"]))
    return records, {
        "unresolved_nodes": unresolved,
        "conflicts": conflicts,
        "gov_totals": gov_totals,
    }


def main() -> None:
    records, stats = build_records()
    gov_total = sum(stats["gov_totals"].values())
    print(
        f"primary governorate sum over {len(stats['gov_totals'])} governorates = {gov_total:,} "
        f"(TA1 region total {REGION_TOTAL_TA1:,}; equal: {gov_total == REGION_TOTAL_TA1})"
    )
    for rec in records:
        RegionRow.model_validate(rec)
    listed = len({x["governorate"] for x in records})
    if listed != GOVERNORATES_GASTAT:
        raise SystemExit(f"governorates listed {listed} != {GOVERNORATES_GASTAT}")
    n10 = sum(x["tag_10k"] for x in records)
    n5 = sum(x["tag_5k"] for x in records)
    nscr = sum(x["screened"] for x in records)
    print(
        f"rows {len(records)}; governorates listed {listed}; tag_10k {n10}; tag_5k {n5}; "
        f"screened {nscr}; excluded {len(records) - nscr}"
    )
    print(f"unresolved nodes: {stats['unresolved_nodes']}")
    print(f"pilot vs primary conflicts over 2 %: {stats['conflicts']}")

    meta = {
        b"governorates_gastat": str(GOVERNORATES_GASTAT).encode(),
        b"governorates_listed": str(listed).encode(),
    }
    table = pa.Table.from_pylist(records).replace_schema_metadata(meta)
    pq.write_table(table, OUT_PARQUET)

    csv = pd.DataFrame(records, dtype=object)
    csv["economic_roles"] = [
        ";".join(f"{x['role']}:{x['source']}" for x in rs) for rs in csv["economic_roles"]
    ]
    csv["sources"] = [";".join(ss) for ss in csv["sources"]]
    csv.to_csv(OUT_CSV, index=False)
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "build_stats.json").write_text(
        json.dumps(
            {"rows": len(records), "tag_10k": n10, "tag_5k": n5, "screened": nscr, **stats},
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
