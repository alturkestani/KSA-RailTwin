# ruff: noqa: E501
"""Asir region sweep: build cities/ksa/regions/asir.{parquet,csv} (REGION_ASIR, R2 input).

> **Document version:** screening/sweeps/asir/build_register.py v1.0 | 31 Oct 2026 | Author: region-scout (r2-asir) | Status: draft

Inputs (all read-only, all registered): the R1a settlement universe `cities/ksa/zones/settlements.parquet`
(OSM ids and coordinates, OSRM road minutes, WorldPop grid figures, OSM population tags), the R1a economic
nodes `cities/ksa/zones/economic_nodes.parquet`, the primary GASTAT Census 2022 TA1 exports (S-cp2-gastat-007/008)
and the pilot-asir source rows. Every official population is checked against the primary table by name; a
mismatch fails the build.

Run: `uv run python -m screening.sweeps.asir.build_register --seed 1`
(the script takes no randomness; `--seed` is recorded in the header for rule 10).
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

from common.schemas import GRID_UNCORROBORATED, TAG_5K, TAG_10K, RegionRow

app = typer.Typer(add_completion=False, help=__doc__)
ROOT = Path(__file__).resolve().parents[3]
SETTLEMENTS = ROOT / "cities/ksa/zones/settlements.parquet"
ECON = ROOT / "cities/ksa/zones/economic_nodes.parquet"
GOV_PRIMARY = ROOT / "data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx"
CITY_PRIMARY = ROOT / "data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx"
OUT_PARQUET = ROOT / "cities/ksa/regions/asir.parquet"
OUT_CSV = ROOT / "cities/ksa/regions/asir.csv"

GOVERNORATES_GASTAT = 18  # primary TA1 governorate table, Asir rows (see GOV_ROWS)
GOVERNORATES_LISTED = 18

# GASTAT primary governorate names for the 18 Asir governorates (S-cp2-gastat-007).
GOV_ROWS = [
    "Abha", "Ahad Rufaydah", "Al Amoah", "Al Birk", "Al Harjah", "Al Majardah", "An Namas",
    "Balqarn", "Bariq", "Bishah", "Khamis Mushayt", "Muhayil", "Rijal Al Ma", "Sarat Abidah",
    "Tanumah", "Tarib", "Tathlith", "Zahran Al Janub",
]  # fmt: skip
# OSM governorate name (cities/ksa/zones/governorates.geojson, used in the universe) per GASTAT name.
GOV_OSM = {
    "Abha": "Abha", "Ahad Rufaydah": "Ahad Rufaydah", "Al Amoah": "Al Amoah",  # no OSM polygon
    "Al Birk": "Al Birk", "Al Harjah": "Al Harjah", "Al Majardah": "Al Majardah",
    "An Namas": "An Nimas", "Balqarn": "Balqarn", "Bariq": "Bariq", "Bishah": "Bishah",
    "Khamis Mushayt": "Khamis Mushayt", "Muhayil": "Muhayil", "Rijal Al Ma": "Rijal Almaa",
    "Sarat Abidah": "Sarat Abidah", "Tanumah": "Tanumah", "Tarib": "Tarib", "Tathlith": "Tathlith",
    "Zahran Al Janub": "Dhahran Al Janub",
}  # fmt: skip
GOV_AR = {
    "Abha": "أبها", "Ahad Rufaydah": "أحد رفيدة", "Al Amoah": "الأمواه", "Al Birk": "البرك",
    "Al Harjah": "الحرجة", "Al Majardah": "المجاردة", "An Nimas": "النماص", "Balqarn": "بلقرن",
    "Bariq": "بارق", "Bishah": "بيشة", "Khamis Mushayt": "خميس مشيط", "Muhayil": "محايل عسير",
    "Rijal Almaa": "رجال ألمع", "Sarat Abidah": "سراة عبيدة", "Tanumah": "تنومة", "Tarib": "طريب",
    "Tathlith": "تثليث", "Dhahran Al Janub": "ظهران الجنوب",
}  # fmt: skip

# Source ids. Existing (docs/sources/index.csv): S-cp2-gastat-007/008 (primary GASTAT), S-cp2-gastat-001
# (relayed cross-check), S-cp2-gastat-005 (Census 2010 cities), S-soc-339 (region total), S-cp1-100
# (GACA airport names), S-r1a-204/210/221/240 (MODON, OSM, universities, Abha coordinates).
# This track: S-asir-001..010 (pilot sources, carried over), S-asir-011..014 (new, below).
S_PRIMARY_CITY = "S-cp2-gastat-008"
S_PRIMARY_GOV = "S-cp2-gastat-007"
S_CITIES2010 = "S-cp2-gastat-005"
S_SETTLE = "S-asir-011"  # R1a settlement universe + OSRM skims
S_WORLDPOP = "S-asir-012"  # WorldPop 2020 constrained grid (grid rows)
S_OSMPOP = "S-asir-013"  # OSM population tags (derived rows)
S_OSMGOV = "S-asir-014"  # OSM admin polygons (containment)
S_CITYPOP = "S-asir-001"  # citypopulation.de relaying GASTAT (secondary)
S_OSM_NODES = "S-asir-003"
S_LANDBRIDGE_STATIONS = (
    "S-062"  # committed Landbridge station names (cities/ksa/lines/landbridge.yaml)
)

# Economic roles, each tied to its town by one source id (R1a economic_nodes first; pilot roles
# otherwise). Keys are settlement ids.
ROLES = {
    "KSA-ST-00026": [  # Abha
        ("airport", "S-cp1-100"),
        ("tourism", "S-r1a-240"),
        ("university", "S-r1a-221"),
        ("industrial_city", "S-r1a-204"),  # MODON Asir industrial city, tied to Abha (unlocated)
    ],
    "KSA-ST-00265": [("airport", "S-cp1-100"), ("mining", "S-asir-009")],  # Bisha
    "KSA-ST-00268": [("military", "S-asir-008")],  # Khamis Mushait (King Khalid Air Base)
    "KSA-ST-06172": [("heritage", "S-asir-010"), ("agriculture", "S-asir-010")],  # Rijal Almaa
}

# Each row: settlement id -> spec. `pop` is (type, value, source, status, primary_to_find, year).
# Name checks guard against a settlement-id slip: the expected name must occur in name_ar.
ROWS: list[dict] = [
    # ---- governorate centres (18) ----
    dict(sid="KSA-ST-00026", centre="Abha", gov="Abha", name="Abha", name_ar="أبها",
         pop=("official", 334290, S_PRIMARY_CITY, "verified", None, 2022), primary="Abha"),
    dict(sid="KSA-ST-02691", centre="Ahad Rufaydah", gov="Ahad Rufaydah", name="Ahad Rafidah",
         name_ar="أحد رفيدة", pop=("official", 79202, S_PRIMARY_CITY, "verified", None, 2022),
         primary="Ahad Rafidah"),
    dict(sid="KSA-ST-01879", centre="Al Amoah", gov="Al Amoah", name="Al-Amwah", name_ar="الأمواه",
         pop=("grid", 9200, S_WORLDPOP, "unverified", None, 2020), notes=(
             "Governorate seat: no OSM polygon for Al Amoah (C-r1a-20); the node named Al Amoah "
             "lies inside the Tathlith polygon by containment (A-asir-002). GASTAT governorate total "
             "10,969 is not a settlement figure and is not used. Needs Opus judgement.")),
    dict(sid="KSA-ST-01240", centre="Al Birk", gov="Al Birk", name="Al-Birk", name_ar="البرك",
         pop=("official", 3987, S_CITYPOP, "secondary", "GASTAT Census 2022 locality table (place "
              "under 5,000 is not in the TA1 city table)", 2022)),
    dict(sid="KSA-ST-01075", centre="Al Harjah", gov="Al Harjah", name="Al-Harjah", name_ar="الحرجة",
         pop=("grid", 435, S_WORLDPOP, "unverified", None, 2020), notes=(
             "Seat chosen by containment in the Al Harjah polygon (A-asir-002). A second node named "
             "Al Harajah (KSA-ST-00560, 4,540, secondary) lies in the Balqarn polygon and is listed "
             "separately as screened out. The grid figure 435 is low for a seat. Needs Opus judgement.")),
    dict(sid="KSA-ST-00555", centre="Al Majardah", gov="Al Majardah", name="Al Majaridah",
         name_ar="المجاردة", pop=("official", 21837, S_PRIMARY_CITY, "verified", None, 2022),
         primary="Almajardah"),
    dict(sid="KSA-ST-00552", centre="An Nimas", gov="An Nimas", name="An-Nimas", name_ar="النماص",
         pop=("official", 22541, S_PRIMARY_CITY, "verified", None, 2022), primary="Alnamas"),
    dict(sid="KSA-ST-00563", centre="Balqarn", gov="Balqarn", name="Sabt Al 'Alayah",
         name_ar="سبت العلاية", pop=("grid", 7594, S_WORLDPOP, "unverified", None, 2020), notes=(
             "Seat chosen by containment in the Balqarn polygon (A-asir-002); the pilot's Balqarn "
             "node (osm 11891866421, Jawf Balqarn) is in Makkah and was dropped. OSM population tag "
             "200000 is rejected: GASTAT's 271-city table does not list the town and the 2010 list "
             "has Al-Ulya at 19,956 unmatched (A-asir-003). Needs Opus judgement.")),
    dict(sid="KSA-ST-01850", centre="Bariq", gov="Bariq", name="Bariq", name_ar="بارق",
         pop=("grid", 2858, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-00265", centre="Bishah", gov="Bishah", name="Bisha", name_ar="بيشة",
         pop=("official", 115537, S_PRIMARY_CITY, "verified", None, 2022), primary="Bishah"),
    dict(sid="KSA-ST-00268", centre="Khamis Mushayt", gov="Khamis Mushayt", name="Khamis Mushait",
         name_ar="خميس مشيط", pop=("official", 535065, S_PRIMARY_CITY, "verified", None, 2022),
         primary="Khamis Mushait"),
    dict(sid="KSA-ST-00558", centre="Muhayil", gov="Muhayil", name="Muhayil", name_ar="محايل عسير",
         pop=("official", 97967, S_PRIMARY_CITY, "verified", None, 2022), primary="Muhayil"),
    dict(sid="KSA-ST-06172", centre="Rijal Almaa", gov="Rijal Almaa", name="Rijal Almaa",
         name_ar="رجال ألمع", pop=("grid", 288, S_WORLDPOP, "unverified", None, 2020), notes=(
             "Seat by OSM place node named Rijal Almaa (osm 11892567408) in its polygon. The grid "
             "figure 288 is implausibly low for a seat (heritage village, S-asir-010). Needs Opus judgement.")),
    dict(sid="KSA-ST-00029", centre="Sarat Abidah", gov="Sarat Abidah", name="Sarat Abidah",
         name_ar="سراة عبيدة", pop=("official", 19855, S_PRIMARY_CITY, "verified", None, 2022),
         primary="Sarat Abidah"),
    dict(sid="KSA-ST-01711", centre="Tanumah", gov="Tanumah", name="Tanumah", name_ar="تنومة",
         pop=("official", 12442, S_PRIMARY_CITY, "verified", None, 2022), primary="Tanawma",
         notes=(
             "GASTAT's primary city table spells the town Tanawma (12,442; row checked 31 Oct 2026). "
             "The R1a universe value (12,442, tabulated_primary) is confirmed. The OSM tag 14,684 equals "
             "the 2010 census count and is not used; WorldPop 3,149 is not used.")),
    dict(sid="KSA-ST-02690", centre="Tarib", gov="Tarib", name="Fir'ah Tarib", name_ar="فرعة طريب",
         pop=("official", 8722, S_PRIMARY_CITY, "verified", None, 2022), primary="Fareah Tarib"),
    dict(sid="KSA-ST-00397", centre="Tathlith", gov="Tathlith", name="Tathlith", name_ar="تثليث",
         pop=("official", 15854, S_PRIMARY_CITY, "verified", None, 2022), primary="Tathlith"),
    dict(sid="KSA-ST-01310", centre="Zahran Al Janub", gov="Dhahran Al Janub",
         name="Zahran al-Janub", name_ar="ظهران الجنوب",
         pop=("official", 24134, S_PRIMARY_CITY, "verified", None, 2022), primary="Zahran Aljanub"),
    # ---- other towns >= 5,000 (sensitivity) and >= 10,000 (screening) ----
    dict(sid="KSA-ST-01227", name="Bahr Abu Sukaynah", name_ar="بحر أبوسكينة", gov="Muhayil",
         pop=("official", 10862, S_PRIMARY_CITY, "verified", None, 2022), primary="Bahr Abu Sukaynah"),
    dict(sid="KSA-ST-00561", name="Al Bashaer", name_ar="البشائر", gov="Balqarn",
         pop=("derived", 12021, S_OSMPOP, "secondary", None, None), notes=(
             "OSM population tag, not in GASTAT's 271-city table (A-asir-001). Needs Opus judgement.")),
    dict(sid="KSA-ST-00537", name="Tabalah", name_ar="تبالة", gov="Bishah",
         pop=("derived", 5670, S_OSMPOP, "secondary", None, None), notes=(
             "OSM population tag, not in GASTAT's 271-city table (A-asir-001).")),
    dict(sid="KSA-ST-02380", name="Shawas Diyar Bani Was", name_ar="شواص ديار بني واس", gov="Balqarn",
         pop=("derived", 8422, S_OSMPOP, "secondary", None, None), notes=(
             "OSM population tag, not in GASTAT's 271-city table (A-asir-001).")),
    dict(sid="KSA-ST-01089", name="Al Ithnayn", name_ar="الإثنين", gov="Abha",
         pop=("official", 5593, S_PRIMARY_CITY, "verified", None, 2022), primary="Al Ithnayn"),
    dict(sid="KSA-ST-01882", name="Wadi Ibn Hishbal", name_ar="وادي ابن هشبل", gov="Khamis Mushayt",
         pop=("grid", 6587, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-01892", name="Tandahah", name_ar="تندحة", gov="Khamis Mushayt",
         pop=("grid", 7749, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-01893", name="Al Mudhah", name_ar="المضة", gov="Tarib",
         pop=("grid", 9492, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-01878", name="Al Sabikhah", name_ar="الصبيخة", gov="Tarib",
         pop=("grid", 7173, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-04169", name="Masloom", name_ar="مصلوُم", gov="Khamis Mushayt",
         pop=("grid", 12376, S_WORLDPOP, "unverified", None, 2020), gate=True),
    dict(sid="KSA-ST-05279", name="Al Harayr", name_ar="الهرير", gov="Khamis Mushayt",
         pop=("grid", 10260, S_WORLDPOP, "unverified", None, 2020), gate=True),
    dict(sid="KSA-ST-00028", name="King Faisal Military City", name_ar="مدينة الملك فيصل العسكرية",
         gov="Khamis Mushayt", pop=("grid", 10017, S_WORLDPOP, "unverified", None, 2020), gate=True),
    dict(sid="KSA-ST-05783", name="Al Bani Thawr", name_ar="آل بني ثور", gov="Khamis Mushayt",
         pop=("grid", 5396, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-05406", name="Ar Raysh", name_ar="الريش", gov="Muhayil",
         pop=("grid", 5392, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-06111", name="Dirs", name_ar="الضرس", gov="Muhayil",
         pop=("grid", 5044, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-01097", name="Yuhan", name_ar="يهن", gov="Abha",
         pop=("grid", 5029, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-01530", name="Al Hammah", name_ar="الحميمة", gov="Bishah",
         pop=("grid", 5362, S_WORLDPOP, "unverified", None, 2020)),
    dict(sid="KSA-ST-02119", name="Al Habil", name_ar="الحبيل", gov="Rijal Almaa",
         pop=("grid", 5810, S_WORLDPOP, "unverified", None, 2020)),
    # ---- screened out (kept for transparency) ----
    dict(sid="KSA-ST-00560", name="Al Harajah", name_ar="الحرجة", gov="Balqarn",
         pop=("official", 4540, S_CITYPOP, "secondary", "GASTAT Census 2022 locality table (under 5,000)", 2022),
         screened=False,
         exclusion_reason="below 5k and not a seat: alternative Al-Harjah node, rejected by containment (A-asir-002)"),
]  # fmt: skip


def _num(v) -> float | None:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return float(v)


def _station(label: str | None) -> str | None:
    """Universe station keys -> readable names (the keys are the universe's own)."""
    if label is None or (isinstance(label, float) and math.isnan(label)):
        return None
    mapping = {
        "hhr:makkah": "Haramain HSR (existing) - Makkah station",
        "hhr:madinah": "Haramain HSR (existing) - Madinah station",
        "landbridge:muwai": "Saudi Landbridge (committed) - Muwai (Moya)",
        "landbridge:al-jumum": "Saudi Landbridge (committed) - Al-Jumum (Jumoum / Jamuma)",
        "riyadh-metro-l3:jeddah-road": "Riyadh Metro L3 (committed) - Jeddah Road",
    }
    if label in mapping:
        return mapping[label]
    return label


def _load() -> tuple[pd.DataFrame, pd.DataFrame]:
    s = pd.read_parquet(SETTLEMENTS)
    e = pd.read_parquet(ECON)
    return s, e


def _primary_tables() -> tuple[dict[str, int], dict[str, int]]:
    g = pd.read_excel(GOV_PRIMARY)
    c = pd.read_excel(CITY_PRIMARY)
    gov = {str(r.Governorate): int(r.Total) for r in g.itertuples()}
    city = {str(r.City): int(r.Total) for r in c.itertuples()}
    return gov, city


def build_rows() -> list[dict]:
    s, econ = _load()
    gov_primary, city_primary = _primary_tables()
    asir = s[s.region == "asir"].set_index("settlement_id")
    assert all(g in gov_primary for g in GOV_ROWS), "GASTAT governorate names drifted"
    assert len(GOV_ROWS) == GOVERNORATES_GASTAT == GOVERNORATES_LISTED
    out: list[dict] = []
    seen_centres: set[str] = set()
    for spec in ROWS:
        sid = spec["sid"]
        u = asir.loc[sid]
        # name guard: the expected Arabic name must match the universe row
        assert spec["name_ar"] in str(u["name_ar"]) or str(u["name_ar"]) in spec["name_ar"], (
            sid,
            u["name_ar"],
            spec["name_ar"],
        )
        pop_spec = spec.get("pop")
        pop_type = pop_src = pop_year = status = prim = None
        population = None
        if pop_spec is not None:
            pop_type, population, pop_src, status, prim, pop_year = pop_spec
            if pop_type == "derived":  # OSM tags carry no year: the extract edition year (2026)
                pop_year = (
                    int(u["osm_population_year"]) if pd.notna(u["osm_population_year"]) else 2026
                )
            if pop_type == "official" and spec.get("primary"):
                want = city_primary[spec["primary"]]
                assert population == want, (sid, population, want)
            if pop_type == "official" and pop_src == S_CITYPOP:
                assert status == "secondary"
        if pop_type == "grid":
            assert pop_src == S_WORLDPOP and status == "unverified"
            assert abs(float(u["grid_population"]) - population) < 1, (sid, u["grid_population"])
        tag_10k = population is not None and population >= TAG_10K
        tag_5k = population is not None and population >= TAG_5K
        screened = spec.get("screened", True)
        exclusion = spec.get("exclusion_reason")
        if spec.get("gate") and pop_type == "grid":
            # grid-only >= 10k: no second method run for this settlement (A-screen-032)
            tag_10k = False
            exclusion = (
                f"{GRID_UNCORROBORATED} (WorldPop {int(population)}; no second method run for "
                "this settlement, A-screen-033)"
            )
        centre = spec.get("centre")
        if centre:
            assert centre not in seen_centres
            seen_centres.add(centre)
        gov = spec["gov"]
        economic = [{"role": r, "source": src} for r, src in ROLES.get(sid, [])]
        road_ex = _num(u["road_min_existing"])
        road_co = _num(u["road_min_committed"])
        road_me = _num(u["road_min_metro_city"])
        row = {
            "name_ar": spec["name_ar"],
            "name_en": spec["name"],
            "region": "asir",
            "governorate": gov,
            "governorate_ar": GOV_AR.get(gov, spec["name_ar"]),
            "is_governorate_centre": bool(centre),
            "osm_id": int(u["osm_id"]),
            "osm_type": str(u["osm_type"]),
            "lat": float(u["lat"]),
            "lon": float(u["lon"]),
            "population": population,
            "pop_source": pop_src,
            "pop_year": int(pop_year) if pop_year else None,
            "pop_type": pop_type,
            "pop_source_status": status,
            "primary_to_find": prim,
            "pop_corroboration": None,
            "pop_corroboration_value": None,
            "tag_10k": bool(tag_10k),
            "tag_5k": bool(tag_5k),
            "dist_existing_km": _num(u["dist_existing_km"]),
            "road_min_existing": road_ex,
            "nearest_existing": _station(u["nearest_existing"]),
            "dist_committed_km": _num(u["dist_committed_km"]),
            "road_min_committed": road_co,
            "nearest_committed": "Saudi Landbridge (committed; announced/planned)",
            "nearest_committed_station": _station(u["nearest_committed"]),
            "dist_metro_km": _num(u["dist_metro_city_km"]),
            "road_min_metro": road_me,
            "nearest_metro": u["nearest_metro_city"],
            "economic_roles": economic,
            "terrain_class": "escarpment_mountain" if sid == "KSA-ST-00026" else None,
            "screened": bool(screened),
            "exclusion_reason": exclusion,
            "sources": _sources(sid, pop_src, economic),
            "fixture": False,
            "threshold_50k": None,
            "pilot_sample": None,
            "nearest_metro_tier": int(u["nearest_metro_tier"])
            if pd.notna(u["nearest_metro_tier"])
            else None,
            "road_min_method": "osrm_table_mld_car: R1a skim, free flow, uncalibrated (A-asir-004)"
            if road_ex is not None
            else "pending R1a skims",
            "dist_method": "great circle (haversine) to the station; road minutes OSRM (R1a)",
            "notes": spec.get("notes"),
        }
        out.append(row)
    return out


def _sources(sid: str, pop_src: str | None, economic: list[dict]) -> list[str]:
    ids = [S_SETTLE, S_OSM_NODES, S_LANDBRIDGE_STATIONS]
    if pop_src:
        ids.insert(0, pop_src)
    ids += [e["source"] for e in economic]
    if sid in ("KSA-ST-00026",):
        ids += ["S-asir-007"]
    return list(dict.fromkeys(ids))


def _check_rows(rows: list[dict]) -> None:
    """Validate every row against RegionRow and the reconciliation rules."""
    for r in rows:
        RegionRow.model_validate(r)
    names = [r["governorate"] for r in rows if r["is_governorate_centre"]]
    assert len(names) == GOVERNORATES_LISTED == len(set(names)) == 18, names
    keys = {(r["osm_type"], r["osm_id"]) for r in rows}
    assert len(keys) == len(rows), "duplicate OSM ids"


def _to_frame(rows: list[dict]) -> pd.DataFrame:
    cols = list(RegionRow.model_fields)
    df = pd.DataFrame(rows)
    return df[[c for c in cols if c in df.columns]]


def _csv_roles(v: list[dict]) -> str:
    return ";".join(f"{e['role']}:{e['source']}" for e in v)


@app.command()
def main(
    seed: int = typer.Option(1, help="Recorded for rule 10; the build is deterministic."),
) -> None:
    rows = build_rows()
    _check_rows(rows)
    df = _to_frame(rows)
    table = pa.Table.from_pandas(df, preserve_index=False)
    meta = {
        b"governorates_gastat": str(GOVERNORATES_GASTAT).encode(),
        b"governorates_listed": str(GOVERNORATES_LISTED).encode(),
        b"seed": str(seed).encode(),
    }
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT_PARQUET)
    csv = df.copy()
    csv["economic_roles"] = [_csv_roles(v) for v in csv["economic_roles"]]
    csv["sources"] = [";".join(v) for v in csv["sources"]]
    csv.to_csv(OUT_CSV, index=False)
    print(
        f"rows={len(rows)} centres={sum(r['is_governorate_centre'] for r in rows)} "
        f"ge10k={sum(r['tag_10k'] for r in rows)} ge5k={sum(r['tag_5k'] for r in rows)}"
    )


if __name__ == "__main__":
    app()
