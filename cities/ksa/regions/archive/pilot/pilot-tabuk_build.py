"""Build the Tabuk pilot register (`pilot-tabuk.parquet` / `.csv`) from cited inputs.

Inputs:
- census figures and governorate list: transcribed from S-tabuk-001 (governorates) and
  S-tabuk-002 (settlements), both citypopulation.de crediting GASTAT Census 2022,
  accessed 2026-10-30;
- coordinates, OSM node ids, existing and historic rail: the local GCC extract
  `data/osm/gcc-states-latest.osm.pbf` (manifest id `osm-gcc-2026-10-14`, ODbL),
  read with the osmium CLI;
- metro coordinates: OSM place nodes of the approved metro set (A-screen-013).

Distances: great-circle (haversine) from the settlement node to the nearest rail vertex,
after densifying each OSM way to 0.5 km steps (assumption A-screen-pilot-001).
Road minutes stay null (R1a skims).

Run: uv run python cities/ksa/regions/pilot-tabuk_build.py
"""

from __future__ import annotations

import json
import math
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common import REPO_ROOT
from common.schemas import RegionRow

OSM_PBF = REPO_ROOT / "data" / "osm" / "gcc-states-latest.osm.pbf"
OUT_DIR = REPO_ROOT / "cities" / "ksa" / "regions"
EARTH_KM = 6371.0088
STEP_KM = 0.5
REGION = "tabuk"

# S-tabuk ids (docs/sources/pilot-tabuk.csv)
S_GOV, S_PLACES, S_OSM = "S-tabuk-001", "S-tabuk-002", "S-tabuk-006"
TERRAIN_ASSUMED = "A-screen-pilot-terrain-001"

# (name_en, name_ar, governorate, governorate_ar, centre?, osm node, lat, lon,
#  census population (S-tabuk-002) or None, roles [(role, source)], terrain, sample?, notes)
ROWS: list[dict] = [
    dict(
        name_en="Tabuk",
        name_ar="تبوك",
        governorate="Tabuk",
        governorate_ar="تبوك",
        centre=True,
        osm="n5418190413",
        lat=28.40125,
        lon=36.56705,
        pop=594350,
        roles=[
            ("administrative", "S-tabuk-004"),
            ("airport", "S-tabuk-013"),
            ("heritage", "S-tabuk-014"),
        ],
        terrain="mixed",
        sample=False,
        notes="Seat of the region (S-tabuk-004). Governorate population 623,665 (S-tabuk-001) "
        "is not used for the row. Hejaz Railway station is a restored museum site (S-tabuk-014); "
        "the historic line is layer historical and is not counted as existing.",
    ),
    dict(
        name_en="Umluj",
        name_ar="أملج",
        governorate="Umluj",
        governorate_ar="أملج",
        centre=True,
        osm="n973472834",
        lat=25.03028,
        lon=37.26223,
        pop=46229,
        roles=[],
        terrain="coastal",
        sample=True,
        notes="Sample: no sourced economic role (the Wikipedia role statements are unreferenced, "
        "S-tabuk-011). Governorate population 69,656 (S-tabuk-001), town 46,229 (S-tabuk-002): "
        "the row uses the town. Nearest metro is Madinah (tier 1, 245 km), not Tabuk: schema edge "
        "(A-screen-013 is nearest-metro by distance). No airport in the governorate (S-tabuk-011).",
    ),
    dict(
        name_en="Duba",
        name_ar="ضباء",
        governorate="Duba",
        governorate_ar="ضباء",
        centre=True,
        osm="n1237957881",
        lat=27.35208,
        lon=35.69207,
        pop=39543,
        roles=[("port", "S-tabuk-007")],
        terrain="coastal",
        sample=True,
        notes="Sample: far from existing rail, sourced port role (ferry to Egypt, S-tabuk-007). "
        "Governorate population 54,917 (S-tabuk-001), town 39,543 (S-tabuk-002). A traveller "
        "account (not used) places a NEOM port about 38 km north of Duba.",
    ),
    dict(
        name_en="Al-Wajh",
        name_ar="الوجه",
        governorate="Al-Wajh",
        governorate_ar="الوجه",
        centre=True,
        osm="n1237957986",
        lat=26.24442,
        lon=36.45328,
        pop=33868,
        roles=[("heritage", "S-tabuk-012"), ("airport", "S-tabuk-011")],
        terrain="coastal",
        sample=False,
        notes="Not sampled (the stratum is covered by Duba and Haql). Governorate population "
        "49,948 (S-tabuk-001), town 33,868 (S-tabuk-002). Domestic airport and Nabataean port "
        "history from travel and Wikipedia pages (S-tabuk-011, S-tabuk-012); port activity ended "
        "late 1990s per one secondary account (unverified).",
    ),
    dict(
        name_en="Tayma",
        name_ar="تيماء",
        governorate="Taymā'",
        governorate_ar="تيماء",
        centre=True,
        osm="n1237942492",
        lat=27.62260,
        lon=38.53926,
        pop=37579,
        roles=[("heritage", "S-tabuk-008")],
        terrain="mixed",
        sample=True,
        notes="Sample: heritage role (UNESCO Tentative List serial entry, not inscribed; "
        "S-tabuk-008); "
        "closest existing line of the sample (SAR North line, 212 km). Governorate population "
        "42,165 (S-tabuk-001), town 37,579 (S-tabuk-002).",
    ),
    dict(
        name_en="Haql",
        name_ar="حقل",
        governorate="Haql",
        governorate_ar="حقل",
        centre=True,
        osm="n1236312441",
        lat=29.28642,
        lon=34.94691,
        pop=25652,
        roles=[("border_crossing", "S-tabuk-010")],
        terrain="coastal",
        sample=True,
        notes="Sample: sourced border adjacency to Aqaba, Jordan (S-tabuk-010); crossing name not "
        "stated there (the Durra crossing is named in a search snippet only, unverified). Far from "
        "existing rail (325 km). Governorate population 27,712 (S-tabuk-001), "
        "town 25,652 (S-tabuk-002).",
    ),
    dict(
        name_en="Al-Bad'",
        name_ar="البدع",
        governorate="Al-Bad'",
        governorate_ar="البدع",
        centre=True,
        osm="n1237951657",
        lat=28.48416,
        lon=35.01411,
        pop=16583,
        roles=[("heritage", "S-tabuk-009")],
        terrain="mixed",
        sample=True,
        notes="Sample: heritage role from Wikipedia (Nabataean rock-cut tombs, petroglyphs; "
        "S-tabuk-009). Far from existing rail (393 km). Two population levels: town 16,583 "
        "(S-tabuk-002) and governorate 17,973 (S-tabuk-001). Air travel via Tabuk city "
        "(S-tabuk-009).",
    ),
    dict(
        name_en="Bi'r Ibn Hirmas",
        name_ar="بئر ابن هرماس",
        governorate="Tabuk",
        governorate_ar="تبوك",
        centre=False,
        osm="n1237958577",
        lat=28.87000,
        lon=36.25774,
        pop=4964,
        roles=[],
        terrain="mixed",
        sample=False,
        screened=False,
        exclusion="below 5,000 (A-screen-002 sensitivity threshold); kept as the 5k-edge check. "
        "Census population 4,964 (S-tabuk-002); the OSM tag (5,975) is not used.",
        notes="Not a governorate centre. Sits 0.4 km from the historic Hejaz line "
        "(layer historical).",
    ),
    dict(
        name_en="Hala Ammar",
        name_ar="حالة عمار",
        governorate="unresolved",
        governorate_ar="غير محدد",
        centre=False,
        osm="n1237958860",
        lat=29.16194,
        lon=36.07583,
        pop=None,
        roles=[],
        terrain="mixed",
        sample=False,
        screened=False,
        exclusion="governorate status unresolved: a centre in the Tabuk municipality "
        "listing (search snippet only; S-tabuk-005 returned 404) and a governorate in the "
        "Al-Ma'rifa list (S-tabuk-021, snippet only); no census population in S-tabuk-002. "
        "The OSM tag (5,293) is not used.",
        notes="Governorate count conflict: see docs/regions/pilot-tabuk.md section 1.",
    ),
]

# Approved metros (A-screen-013), nearest-metro by great-circle distance.
# (name, OSM node id of the city node in the extract, tier). Pinned by id: OSM `name` tags are
# mostly Arabic and the English forms sit in `alt_name`, so name matching is unreliable.
METROS = [
    ("Riyadh", "n315358390", 1),
    ("Jeddah", "n1933393717", 1),
    ("Makkah", "n4308338842", 1),
    ("Madinah", "n4571693347", 1),
    ("Dammam", "n287865393", 1),
    ("Khobar", "n32441763", 1),
    ("Dhahran", "n447805356", 1),
    ("Taif", "n1236468526", 2),
    ("Buraidah", "n1236365110", 2),
    ("Tabuk", "n5418190413", 2),
    ("Abha", "n295924875", 2),
    ("Khamis Mushait", "n983083570", 2),
    ("Jazan", "n288992209", 3),
    ("Najran", "n982548735", 3),
]

EXISTING_EXCLUDED_SERVICES = {"siding", "yard", "spur", "crossover"}


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    la1, lo1 = map(math.radians, (a[1], a[0]))
    la2, lo2 = map(math.radians, (b[1], b[0]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * EARTH_KM * math.asin(math.sqrt(h))


def densify(coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for a, b in zip(coords, coords[1:], strict=False):
        n = max(1, int(haversine(a, b) / STEP_KM))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
    return out or coords


def export_geojsonseq(pbf: Path, out: Path) -> list[dict]:
    subprocess.run(
        [
            "osmium",
            "export",
            "-f",
            "geojsonseq",
            "--add-unique-id=type_id",
            "-o",
            str(out),
            "--overwrite",
            str(pbf),
        ],
        check=True,
    )
    feats = []
    for line in out.read_text(encoding="utf-8").splitlines():
        line = line.strip().lstrip("\x1e")
        if line:
            feats.append(json.loads(line))
    return feats


def load_osm(tmp: Path) -> tuple[dict[str, dict], list[tuple[str, dict, list]]]:
    """Return place nodes keyed by OSM node id, and rail ways with densified vertices."""
    places_pbf, rail_pbf = tmp / "places.pbf", tmp / "rail.pbf"
    subprocess.run(
        [
            "osmium",
            "tags-filter",
            "--overwrite",
            "-o",
            str(places_pbf),
            str(OSM_PBF),
            "n/place=city,town,village,hamlet,locality,suburb",
        ],
        check=True,
    )
    subprocess.run(
        [
            "osmium",
            "tags-filter",
            "--overwrite",
            "-o",
            str(rail_pbf),
            str(OSM_PBF),
            "w/railway=rail,construction,abandoned,disused",
        ],
        check=True,
    )
    nodes: dict[str, dict] = {}
    for f in export_geojsonseq(places_pbf, tmp / "places.geojsonseq"):
        nodes[f["id"]] = {
            "props": f.get("properties", {}),
            "coord": tuple(f["geometry"]["coordinates"]),
        }
    ways: list[tuple[str, dict, list]] = []
    for f in export_geojsonseq(rail_pbf, tmp / "rail.geojsonseq"):
        geom = f.get("geometry") or {}
        if geom.get("type") == "LineString":
            parts = [geom["coordinates"]]
        elif geom.get("type") == "MultiLineString":
            parts = geom["coordinates"]
        else:
            continue
        pts: list[tuple[float, float]] = []
        for part in parts:
            pts += densify([tuple(c) for c in part])
        ways.append((f["id"], f.get("properties", {}), pts))
    return nodes, ways


def nearest_way(pt: tuple[float, float], ways: list, keep) -> tuple[float, str, dict] | None:
    best: tuple[float, str, dict] | None = None
    for wid, props, pts in ways:
        if not keep(props):
            continue
        d = min(haversine(pt, c) for c in pts)
        if best is None or d < best[0]:
            best = (d, wid, props)
    return best


def is_existing(props: dict) -> bool:
    return props.get("railway") == "rail" and props.get("service") not in EXISTING_EXCLUDED_SERVICES


def describe_way(wid: str, props: dict) -> str:
    name = props.get("name")
    if name:
        return f"{name} (OSM {wid})"
    return f"unnamed OSM {props.get('usage') or 'rail'} way {wid}"


def metro_coords(nodes: dict[str, dict]) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for name, osm_id, _tier in METROS:
        if osm_id not in nodes:
            raise SystemExit(f"metro {name}: OSM node {osm_id} not in the extract")
        out[name] = nodes[osm_id]["coord"]
    return out


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="tabuk-osm-"))
    nodes, ways = load_osm(tmp)
    metros = metro_coords(nodes)
    tier = {n: t for n, _, t in METROS}

    records: list[dict] = []
    for r in ROWS:
        node = nodes.get(r["osm"])
        if node is None:
            raise SystemExit(f"{r['name_en']}: OSM node {r['osm']} not found in extract")
        pt = (r["lon"], r["lat"])
        if abs(node["coord"][0] - r["lon"]) > 0.002 or abs(node["coord"][1] - r["lat"]) > 0.002:
            raise SystemExit(f"{r['name_en']}: coordinates differ from OSM node {r['osm']}")
        ex = nearest_way(pt, ways, is_existing)
        hist = nearest_way(pt, ways, lambda p: p.get("railway") in ("abandoned", "disused"))
        metro_name, metro_km = min(
            ((n, haversine(pt, c)) for n, c in metros.items()), key=lambda kv: kv[1]
        )
        screened = r.get("screened", True)
        pop = r["pop"]
        pop_type = "secondary" if pop is not None else None
        rec = {
            "name_ar": r["name_ar"],
            "name_en": r["name_en"],
            "region": REGION,
            "governorate": r["governorate"],
            "governorate_ar": r["governorate_ar"],
            "is_governorate_centre": r["centre"],
            "osm_id": int(r["osm"][1:]),
            "lat": r["lat"],
            "lon": r["lon"],
            "population": pop,
            "pop_source": S_PLACES if pop is not None else None,
            "pop_year": 2022 if pop is not None else None,
            "pop_type": pop_type,
            "primary_to_find": (
                "GASTAT Census 2022 locality table (portal.saudicensus.sa; "
                "DNS failure 2026-10-30, S-072, S-090)"
            )
            if pop is not None
            else None,
            "tag_10k": pop is not None and pop >= 10_000,
            "tag_5k": pop is not None and pop >= 5_000,
            "threshold_50k": pop is not None and pop >= 50_000,
            "pilot_sample": r["sample"],
            "dist_existing_km": round(ex[0], 1) if ex else None,
            "road_min_existing": None,
            "nearest_existing": describe_way(ex[1], ex[2]) if ex else None,
            "dist_committed_km": None,
            "road_min_committed": None,
            "nearest_committed": None,
            "nearest_committed_station": None,
            "dist_metro_km": round(metro_km, 1),
            "road_min_metro": None,
            "nearest_metro": metro_name,
            "nearest_metro_tier": tier[metro_name],
            "distance_method": (
                f"haversine; OSM way densified to {STEP_KM} km steps; A-screen-pilot-001"
            ),
            "road_min_method": "pending R1a skims",
            "economic_roles": [{"role": ro, "source": so} for ro, so in r["roles"]],
            "terrain_class": r["terrain"],
            "terrain_source": f"assumed: {TERRAIN_ASSUMED}",
            "screened": screened,
            "exclusion_reason": r.get("exclusion"),
            "sources": sorted({S_OSM, S_PLACES, S_GOV, *[so for _, so in r["roles"]]}),
            "notes": r["notes"] + f" Historic (abandoned/disused) Hejaz line: {hist[0]:.1f} km."
            if hist
            else r["notes"],
            "fixture": False,
        }
        RegionRow.model_validate(rec)
        records.append(rec)

    # Governorate coverage (rule 2): every governorate of the citypopulation list has a row.
    gov_rows = {rec["governorate"] for rec in records}
    expected = {"Tabuk", "Umluj", "Duba", "Al-Wajh", "Taymā'", "Haql", "Al-Bad'"}
    missing = expected - gov_rows
    if missing:
        raise SystemExit(f"governorates without a row: {sorted(missing)}")

    df = pd.DataFrame(records)
    meta = {
        b"governorates_gastat": b"unverified (not found in GASTAT portal; S-072, S-090)",
        b"governorates_listed": (
            b"7 (6 governorates + Tabuk City seat; S-tabuk-001, S-tabuk-004, S-tabuk-003)"
        ),
        b"governorates_alt_count": (
            b"6 (Tabuk municipality, Saudipedia and Arab Countries Guide wording; "
            b"see docs/regions/pilot-tabuk.md)"
        ),
        b"region": REGION.encode(),
        b"method": b"haversine; screening input, not a forecast",
    }
    table = pa.Table.from_pandas(df, preserve_index=False).replace_schema_metadata(meta)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT_DIR / "pilot-tabuk.parquet")
    df_csv = df.copy()
    for col in ("economic_roles", "sources"):
        df_csv[col] = df_csv[col].apply(lambda v: json.dumps(v, ensure_ascii=False))
    df_csv.to_csv(OUT_DIR / "pilot-tabuk.csv", index=False, encoding="utf-8")
    print(
        f"rows={len(records)} pilot_sample={sum(r['pilot_sample'] for r in records)} "
        f"threshold_50k={sum(r['threshold_50k'] for r in records)} "
        f"screened={sum(r['screened'] for r in records)}"
    )


if __name__ == "__main__":
    main()
