"""REGION_MAKKAH sweep builder (R2, `region-sweep` skill): the Makkah region register.

Inputs (read only):
- `cities/ksa/zones/settlements.parquet`: the R1a settlement universe with the GASTAT primary and
  relayed joins, the WorldPop gap-fill, OSM population tags and the OSRM road minutes (S-r1a-809);
- `runs/gastat/` (gitignored): `screening.gastat` outputs (`region_check.csv`,
  `primary/city_matches.csv`);
- `data/ksa/makkah/raw/nominatim-ardhiyat-2026-10-31.json` (registered in
  `cities/ksa/sources.yaml`);
- `cities/ksa/lines/stations.geojson` (located stations; used only for the Al-Ardiyat centroid row).

Outputs: `cities/ksa/regions/makkah.parquet` and `.csv` (header `governorates_gastat` and
`governorates_listed`), and `docs/regions/makkah.md` (table generated from the register).

Every override is listed in `OVERRIDES` below and in `docs/assumptions-r2-makkah.md`.

uv run python -m screening.sweeps.makkah.build --seed 1
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
import typer

from common.schemas import RegionRow

ROOT = Path(__file__).resolve().parents[3]
SETTLEMENTS = ROOT / "cities/ksa/zones/settlements.parquet"
STATIONS = ROOT / "cities/ksa/lines/stations.geojson"
GASTAT_RUNS = ROOT / "runs/gastat"
NOMINATIM = ROOT / "data/ksa/makkah/raw/nominatim-ardhiyat-2026-10-31.json"
OUT_PARQUET = ROOT / "cities/ksa/regions/makkah.parquet"
OUT_CSV = ROOT / "cities/ksa/regions/makkah.csv"
OUT_MD = ROOT / "docs/regions/makkah.md"
EARTH_R_KM = 6371.0088  # A-screen-pilot-001 (haversine, Earth radius)
GRID_NEAR_MAKKAH_KM = 25.0  # A-makkah-007
GOVERNORATES_GASTAT = 17  # S-cp2-gastat-007 joined to S-073 names (runs/gastat/region_check.csv)

# S-073 names (docs/gastat-regions.md) for the 17 Makkah governorates, keyed by the
# settlements.parquet `governorate` value.
GOVERNORATES: dict[str, tuple[str, str]] = {
    "Adam": ("Adam", "أضم"),
    "Al Ardhiyat": ("Al-Ardiyat", "العرضيات"),
    "Al Jumum": ("Al-Jumum", "الجموم"),
    "Al Kamil": ("Al-Kamil", "الكامل"),
    "Al Khurmah": ("Al-Khurmah", "الخرمة"),
    "Al Lith": ("Al-Lith", "الليث"),
    "Al Muwayh": ("Al-Muwayh", "المويه"),
    "Al Qunfudhah": ("Al-Qunfudhah", "القنفذة"),
    "Al Taif": ("At-Ta'if", "الطائف"),
    "Bahrah": ("Bahrah", "بحرة"),
    "Governorate of Jeddah": ("Jiddah", "جدة"),
    "Khulays": ("Khulays", "خليص"),
    "Makkah Al Mukarramah": ("Makkah al-Mukarramah", "مكة المكرمة"),
    "Missan": ("Maysan", "ميسان"),
    "Rabigh": ("Rabigh", "رابغ"),
    "Ranyah": ("Ranyah", "رنية"),
    "Turubah": ("Turubah", "تربة"),
}

# Governorate centre = the settlement of that name (settlement_id in settlements.parquet).
# Al-Ardiyat has
# no settlement row in the universe: it gets the OSM boundary centroid row below (A-makkah-004).
CENTRES: dict[str, str] = {
    "Adam": "KSA-ST-01876",
    "Al Jumum": "KSA-ST-00508",
    "Al Kamil": "KSA-ST-01356",
    "Al Khurmah": "KSA-ST-00499",
    "Al Lith": "KSA-ST-01349",
    "Al Muwayh": "KSA-ST-00488",
    "Al Qunfudhah": "KSA-ST-00270",
    "Al Taif": "KSA-ST-00520",
    "Bahrah": "KSA-ST-01322",
    "Governorate of Jeddah": "KSA-ST-01411",
    "Khulays": "KSA-ST-00059",
    "Makkah Al Mukarramah": "KSA-ST-01525",
    "Missan": "KSA-ST-00009",
    "Rabigh": "KSA-ST-00263",
    "Ranyah": "KSA-ST-01763",
    "Turubah": "KSA-ST-07369",
}

# OVERRIDES (each one is also an assumption row, A-makkah-00x):
# - Adham (KSA-ST-01876): the relayed 2022 figure 9,022 (S-makkah-001) is attributed here
#   through the
#   Census 2010 bridge (screening/gastat_crosswalk.yaml, city_primary "Adham": no name match). The
#   universe's OSM tag (10,484, 2010) is superseded because official beats derived (A-screen-031).
# - KSA-ST-03308 (village, Al-Mahd node): the universe carries the same 9,022 by a pilot join; the
#   crosswalk leaves that figure unmatched, so the village is dropped (not a register row).
# - KSA-ST-00497 (Turabah node) is the same town as Turubah (relation 12429522, GASTAT
#   28,279): kept as
#   an excluded duplicate with no population.
OVERRIDE_POP: dict[str, dict[str, Any]] = {
    "KSA-ST-01876": {
        "population": 9022,
        "pop_source": "S-makkah-001",
        "pop_type": "official",
        "pop_source_status": "secondary",
        "pop_year": 2022,
        "primary_to_find": "S-cp2-gastat-008 row 'Adham' (no settlement "
        "matched by name; identity to confirm)",
    },
}
DROP = {
    "KSA-ST-03308": "universe carries Adham's figure on this village node (pilot join); dropped"
}
DUPLICATE_OF = {"KSA-ST-00497": "KSA-ST-07369"}
# Unmatched primary TA1 cities whose name matches a register row
# (`runs/gastat/primary/city_matches.csv`).
# Identity is open (no region in the export): the note records the candidate; no value is changed.
CANDIDATE_NOTES: dict[str, str] = {
    "KSA-ST-01313": "primary TA1 'Alqawz' 22,374 (unmatched; same Arabic name القوز; "
    "identity open): "
    "if confirmed, the official figure replaces the OSM tag 23,391; tag_10k stays true",
    "KSA-ST-00586": "primary TA1 'Eshyrh' 9,517 (unmatched, ambiguous name; identity open)",
    "KSA-ST-01838": "primary TA1 'Ghuran' 6,803 (unmatched, ambiguous name; identity open)",
    "KSA-ST-06814": "primary TA1 'Alsayl' 6,064 (unmatched, ambiguous name; identity open)",
    "KSA-ST-05598": 'primary TA1 "Aleurafa\'" 5,432 (unmatched, ambiguous name; identity open)',
}

# Al-Ardiyat governorate: OSM boundary relation 12429530, centroid from Nominatim (S-makkah-008).
ARDIYAT_CENTROID = {
    "name_en": "Al-Ardiyat",
    "name_ar": "العرضيات",
    "osm_type": "relation",
    "osm_id": 12429530,
    "lat": 19.4348098,
    "lon": 41.7020734,
}

# Economic roles tied to a settlement: (settlement_id, role, source id, note). Taken from
# economic_nodes.csv (R1a, S-r1a-*) and docs/sources/cp1-item1-roles.csv (S-cp1-*), plus the
# pilot's KAUST snippet (S-makkah-003). Nodes with no town-level tie are NOT listed (see the md).
ROLES: list[tuple[str, str, str, str]] = [
    (
        "KSA-ST-01411",
        "airport",
        "S-cp1-100",
        "King Abdulaziz International Airport (GACA Feb 2025)",
    ),
    ("KSA-ST-01411", "port", "S-cp1-111", "Jeddah Islamic Port (Mawani; operator per S-cp1-112)"),
    ("KSA-ST-01411", "industrial_city", "S-r1a-204", "MODON Jeddah industrial cities 1-3"),
    ("KSA-ST-01411", "heritage", "S-r1a-205", "Historic Jeddah (UNESCO, Wikidata)"),
    ("KSA-ST-01411", "hajj_umrah", "S-cp1-110", "Hajj terminal at KAIA (2017 capacity figure)"),
    ("KSA-ST-01411", "university", "S-r1a-221", "King Abdulaziz University; University of Jeddah"),
    ("KSA-ST-01411", "tourism", "S-r1a-239", "Jeddah Corniche (Wikipedia infobox)"),
    ("KSA-ST-01525", "hajj_umrah", "S-cp1-109", "Makkah: Hajj and Umrah destination"),
    (
        "KSA-ST-01525",
        "hajj_umrah",
        "S-r1a-214",
        "Masjid al-Haram; Mina, Muzdalifah, Arafat (Wikidata)",
    ),
    ("KSA-ST-01525", "industrial_city", "S-r1a-204", "MODON Makkah industrial cities 1-2"),
    ("KSA-ST-01525", "university", "S-r1a-221", "Umm Al-Qura University"),
    ("KSA-ST-00520", "airport", "S-cp1-100", "Ta'if International Airport (GACA Feb 2025)"),
    (
        "KSA-ST-00520",
        "industrial_city",
        "S-r1a-204",
        "Taif Industrial City (MODON; site unlocated)",
    ),
    ("KSA-ST-00520", "tourism", "S-r1a-241", "Taif highland tourism (Wikipedia infobox)"),
    ("KSA-ST-00520", "university", "S-r1a-221", "Taif University"),
    (
        "KSA-ST-00263",
        "energy",
        "S-cp1-104",
        "Petro Rabigh refinery (governorate-level tie, secondary)",
    ),
    ("KSA-ST-00263", "hajj_umrah", "S-r1a-225", "Miqat Al-Juhfah (site unlocated; secondary list)"),
    ("KSA-ST-01349", "hajj_umrah", "S-r1a-225", "Miqat Yalamlam (site unlocated; secondary list)"),
    (
        "KSA-ST-00583",
        "hajj_umrah",
        "S-r1a-225",
        "Miqat Qarn al-Manazil and Dhat Irq (site unlocated)",
    ),
    (
        "KSA-ST-00052",
        "university",
        "S-makkah-003",
        "KAUST campus in Thuwal (search snippet, not fetched)",
    ),
]

ROW_FIELDS = [
    "name_ar",
    "name_en",
    "region",
    "governorate",
    "governorate_ar",
    "is_governorate_centre",
    "osm_id",
    "osm_type",
    "lat",
    "lon",
    "population",
    "pop_source",
    "pop_year",
    "pop_type",
    "pop_source_status",
    "primary_to_find",
    "pop_corroboration",
    "pop_corroboration_value",
    "tag_10k",
    "tag_5k",
    "dist_existing_km",
    "road_min_existing",
    "nearest_existing",
    "dist_committed_km",
    "road_min_committed",
    "nearest_committed",
    "nearest_committed_station",
    "dist_metro_km",
    "road_min_metro",
    "nearest_metro",
    "nearest_metro_tier",
    "road_min_method",
    "dist_method",
    "economic_roles",
    "terrain_class",
    "screened",
    "exclusion_reason",
    "sources",
    "threshold_50k",
    "pilot_sample",
    "notes",
]
ROLE_TYPE = pa.list_(pa.struct([("role", pa.string()), ("source", pa.string())]))

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance; a and b are (lat, lon)."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * EARTH_R_KM * math.asin(math.sqrt(h))


def clean(v: Any) -> Any:
    """NaN and pandas NA become None; numpy scalars become Python scalars."""
    if v is None or v is pd.NA or (isinstance(v, float) and math.isnan(v)):
        return None
    return v.item() if hasattr(v, "item") else v


def strip_tier(name: str | None) -> str | None:
    return re.sub(r"\s*\(tier \d\)$", "", name) if isinstance(name, str) else None


def centroid_distances(
    stations: list[dict[str, Any]], metros: list[tuple[str, int, tuple[float, float]]]
) -> dict[str, Any]:
    """Distances from the Al-Ardiyat centroid to the nearest located existing and committed station,
    and the nearest approved metro among Makkah, Jeddah and Taif (approximate; no road minutes)."""
    here = (ARDIYAT_CENTROID["lat"], ARDIYAT_CENTROID["lon"])
    out: dict[str, Any] = {}
    for layer, prefix in (("existing", "dist_existing"), ("committed", "dist_committed")):
        cand = [s for s in stations if s["layer"] == layer and s["located"]]
        key = f"nearest_{layer}"
        if not cand:  # committed stations are unlocated (A-stn): no distance is invented
            out[f"{prefix}_km"], out[key] = None, None
            continue
        best = min(cand, key=lambda s: haversine_km(here, s["ll"]))
        out[f"{prefix}_km"] = round(haversine_km(here, best["ll"]), 2)
        out[key] = best["name"]
    name, tier, ll = min(metros, key=lambda m: haversine_km(here, m[2]))
    out["dist_metro_km"] = round(haversine_km(here, ll), 2)
    out["nearest_metro"] = name
    out["nearest_metro_tier"] = tier
    return out


def load_stations() -> list[dict[str, Any]]:
    feats = json.loads(STATIONS.read_text())["features"]
    rows = []
    for f in feats:
        p = f["properties"]
        if p.get("layer") not in ("existing", "committed") or not f.get("geometry"):
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        rows.append(
            {
                "layer": p["layer"],
                "located": bool(p.get("located")),
                "ll": (lat, lon),
                "name": f"{p.get('line_id')}:{p.get('station_id')}",
            }
        )
    return rows


def population_fields(r: pd.Series) -> dict[str, Any]:
    """Map a universe population (source string) to the RegionRow provenance fields."""
    src = str(r["pop_source"])
    if src == "gastat-census2022-ta1-city5k-xlsx":
        return {
            "pop_source": "S-cp2-gastat-008",
            "pop_type": "official",
            "pop_source_status": "verified",
            "primary_to_find": None,
        }
    if src == "S-makkah-001":
        return {
            "pop_source": "S-makkah-001",
            "pop_type": "official",
            "pop_source_status": "secondary",
            "primary_to_find": "S-cp2-gastat-008 row (if ≥ 5,000) or "
            "the GASTAT Census 2022 locality table",
        }
    if src.startswith("osm-gcc"):
        return {
            "pop_source": "S-makkah-009",
            "pop_type": "derived",
            "pop_source_status": "secondary",
            "primary_to_find": "GASTAT Census 2022 table for this locality",
        }
    if src.startswith("worldpop"):
        return {
            "pop_source": "S-r1a-505",
            "pop_type": "grid",
            "pop_source_status": "unverified",
            "primary_to_find": "GASTAT Census 2022 table for this locality",
        }
    raise ValueError(f"unmapped population source {src!r} for {r['settlement_id']}")


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    s = pd.read_parquet(SETTLEMENTS)
    m = s[s["region"] == "makkah"].copy()
    stations = load_stations()
    metros = []
    for sid, tier in (("KSA-ST-01525", 1), ("KSA-ST-01411", 1), ("KSA-ST-00520", 2)):
        r = m[m["settlement_id"] == sid].iloc[0]
        metros.append(
            (strip_tier(r["nearest_metro_city"]) or r["name_en"], tier, (r["lat"], r["lon"]))
        )
    mecca = m[m["settlement_id"] == "KSA-ST-01525"].iloc[0]
    mecca_ll = (mecca["lat"], mecca["lon"])
    ardiyat = centroid_distances(stations, metros)
    ard_nom = json.loads(NOMINATIM.read_text())
    assert ard_nom and int(ard_nom[0]["osm_id"]) == ARDIYAT_CENTROID["osm_id"], (
        "Nominatim raw mismatch"
    )

    selected = []
    for _, r in m.iterrows():
        sid = r["settlement_id"]
        if sid in DROP:
            continue
        pop = clean(r["population"])
        is_centre = sid in CENTRES.values()
        if sid in DUPLICATE_OF:
            selected.append(("dup", r))
        elif is_centre or (pop is not None and pop >= 5000):
            selected.append(("row", r))
        elif r["place"] in ("city", "town") and pop is not None:
            selected.append(("below5k", r))

    rows: list[dict[str, Any]] = []
    for kind, r in selected:
        sid = r["settlement_id"]
        gov_en, gov_ar = GOVERNORATES[r["governorate"]]
        centre_of = [g for g, c in CENTRES.items() if c == sid]
        unnamed = f"unnamed OSM {r['osm_type']} {int(r['osm_id'])}"  # no name in OSM: not invented
        base = {
            "name_en": clean(r["name_en"]) or clean(r["name_ar"]) or unnamed,
            "name_ar": clean(r["name_ar"]) or clean(r["name_en"]) or unnamed,
            "region": "makkah",
            "governorate": gov_en,
            "governorate_ar": gov_ar,
            "is_governorate_centre": bool(centre_of),
            "osm_id": int(r["osm_id"]),
            "osm_type": r["osm_type"],
            "lat": float(r["lat"]),
            "lon": float(r["lon"]),
            "terrain_class": None,
            "threshold_50k": None,
            "pilot_sample": None,
        }
        pop = clean(r["population"])
        pop_type = None
        nodate_note = None
        pop_fields = {"pop_source": None, "pop_source_status": None, "primary_to_find": None}
        if sid in OVERRIDE_POP:
            ov = OVERRIDE_POP[sid]
            pop = ov["population"]
            pop_fields = {k: ov[k] for k in ("pop_source", "pop_source_status", "primary_to_find")}
            pop_type = ov["pop_type"]
            pop_year = ov["pop_year"]
        elif kind != "dup" and pop is not None and clean(r["pop_year"]) is None:
            nodate_note = (
                f"population tag {int(pop)} carries no year; not used (the schema needs pop_year)"
            )
            pop, pop_year = None, None
        elif kind != "dup" and pop is not None:
            pf = population_fields(r)
            pop_fields = {k: pf[k] for k in ("pop_source", "pop_source_status", "primary_to_find")}
            pop_type = pf["pop_type"]
            pop_year = int(clean(r["pop_year"]))
        else:
            pop_year = None
        if kind == "dup":
            pop = None
            pop_year = None
        pop_int = int(pop) if pop is not None else None
        tag_10k = bool(pop_int is not None and pop_int >= 10000 and pop_type != "grid")
        tag_5k = bool(pop_int is not None and pop_int >= 5000)
        if pop_type == "grid" and pop_int is not None and pop_int >= 10000:
            tag_10k = (
                False  # A-screen-031/032: no second method run for this row (no corroboration)
            )
        notes: list[str] = []
        exclusion = None
        screened = True
        if kind == "dup":
            exclusion = f"duplicate of {DUPLICATE_OF[sid]} (Turubah, relation 12429522): same town"
            screened = False
            notes.append(
                "Turabah node: same town as the Turubah relation row; "
                "excluded to avoid double counting"
            )
        elif kind == "below5k":
            exclusion = f"below 5,000 (population {pop_int}, {pop_type})"
            screened = False
        if pop_type == "grid" and pop_int is not None and pop_int >= 10000 and not tag_10k:
            exclusion = "grid-only population, uncorroborated"
        if pop_type == "grid":
            notes.append(
                "WorldPop 2020 gap-fill (1.5 km allocation); unverified; no second method run"
            )
            if haversine_km(mecca_ll, (r["lat"], r["lon"])) <= GRID_NEAR_MAKKAH_KM:
                notes.append(
                    "within 25 km of Makkah city: may overlap the official "
                    "Makkah city figure (open)"
                )
        if pop_type == "derived" and kind != "dup":
            notes.append("OSM population tag, not a GASTAT figure")
            if pop_year == 1882:
                notes.append("tag year 1882 is implausible; value unverified")
        if sid in OVERRIDE_POP:
            notes.append(
                "relayed 2022 figure 9,022 attributed here via the Census "
                "2010 bridge (A-makkah-003); "
                "OSM tag 10,484 (2010) differs by -14 %"
            )
        if nodate_note:
            notes.append(nodate_note)
            if pop_int is None and not centre_of:
                exclusion, screened = "no sourced population: OSM tag without a year", False
        if sid in CANDIDATE_NOTES:
            notes.append(CANDIDATE_NOTES[sid])
        if sid == "KSA-ST-07369":
            notes.append(
                "primary GASTAT 28,279 on the relation; Turabah node "
                "KSA-ST-00497 excluded as duplicate"
            )
        if sid == "KSA-ST-01356":
            notes.append(
                "governorate seat; relayed figure below the 5,000 city "
                "export, locality table not read"
            )
        if sid == "KSA-ST-00009":
            notes.append("governorate seat (Maysan); OSM population tag with year 2010 (as tagged)")
        if centre_of and sid == "KSA-ST-01876":
            notes.append("governorate seat (Adam)")

        road = {
            "road_min_existing": clean(r["road_min_existing"]),
            "road_min_committed": clean(r["road_min_committed"]),
            "road_min_metro": clean(r["road_min_metro_city"]),
        }
        roles = [(x[1], x[2], x[3]) for x in ROLES if x[0] == sid]
        row = {
            **base,
            "population": pop_int,
            "pop_year": pop_year,
            "pop_type": pop_type,
            **pop_fields,
            "pop_corroboration": None,
            "pop_corroboration_value": None,
            "tag_10k": tag_10k,
            "tag_5k": tag_5k,
            "dist_existing_km": round(float(r["dist_existing_km"]), 2)
            if clean(r["dist_existing_km"]) is not None
            else None,
            "road_min_existing": round(float(road["road_min_existing"]), 1)
            if road["road_min_existing"] is not None
            else None,
            "nearest_existing": clean(r["nearest_existing"]),
            "dist_committed_km": round(float(r["dist_committed_km"]), 2)
            if clean(r["dist_committed_km"]) is not None
            else None,
            "road_min_committed": round(float(road["road_min_committed"]), 1)
            if road["road_min_committed"] is not None
            else None,
            "nearest_committed": clean(r["nearest_committed"]),
            "nearest_committed_station": _committed_station(r),
            "dist_metro_km": round(float(r["dist_metro_city_km"]), 2)
            if clean(r["dist_metro_city_km"]) is not None
            else None,
            "road_min_metro": round(float(road["road_min_metro"]), 1)
            if road["road_min_metro"] is not None
            else None,
            "nearest_metro": strip_tier(clean(r["nearest_metro_city"])),
            "nearest_metro_tier": int(r["nearest_metro_tier"]),
            "road_min_method": "osrm_table_mld_car (R1a skims; free flow, uncalibrated; S-r1a-809)"
            if road["road_min_existing"] is not None
            else "pending skims",
            "dist_method": "haversine (R1a settlements.parquet; A-makkah-001)",
            "economic_roles": [{"role": ro, "source": so} for ro, so, _ in roles],
            "screened": screened,
            "exclusion_reason": exclusion,
            "sources": _sources(pop_fields.get("pop_source"), roles, road, r),
            "notes": "; ".join(notes + [n for _, _, n in roles if n]) or None,
        }
        if centre_of:
            row["notes"] = "; ".join(
                ["governorate centre (" + centre_of[0] + ")"]
                + ([row["notes"]] if row["notes"] else [])
            )
        rows.append(row)

    # Al-Ardiyat governorate centroid row (no settlement in the universe; A-makkah-004).
    ard = {
        "name_en": ARDIYAT_CENTROID["name_en"],
        "name_ar": ARDIYAT_CENTROID["name_ar"],
        "region": "makkah",
        "governorate": "Al-Ardiyat",
        "governorate_ar": "العرضيات",
        "is_governorate_centre": True,
        "osm_id": ARDIYAT_CENTROID["osm_id"],
        "osm_type": ARDIYAT_CENTROID["osm_type"],
        "lat": ARDIYAT_CENTROID["lat"],
        "lon": ARDIYAT_CENTROID["lon"],
        "population": None,
        "pop_source": None,
        "pop_year": None,
        "pop_type": None,
        "pop_source_status": None,
        "primary_to_find": "GASTAT locality table: seat town of Al-Ardiyat (not located)",
        "pop_corroboration": None,
        "pop_corroboration_value": None,
        "tag_10k": False,
        "tag_5k": False,
        "dist_existing_km": ardiyat["dist_existing_km"],
        "road_min_existing": None,
        "nearest_existing": ardiyat["nearest_existing"],
        "dist_committed_km": ardiyat["dist_committed_km"],
        "road_min_committed": None,
        "nearest_committed": ardiyat["nearest_committed"],
        "nearest_committed_station": None,
        "dist_metro_km": ardiyat["dist_metro_km"],
        "road_min_metro": None,
        "nearest_metro": ardiyat["nearest_metro"],
        "nearest_metro_tier": ardiyat["nearest_metro_tier"],
        "road_min_method": "pending skims",
        "dist_method": "haversine (centroid to nearest located station; A-makkah-001)",
        "economic_roles": [],
        "terrain_class": None,
        "screened": False,
        "exclusion_reason": "governorate centre: seat town not located and no sourced population",
        "sources": ["S-makkah-008", "S-makkah-002"],
        "notes": "centroid of OSM boundary relation 12429530 (Nominatim, "
        "S-makkah-008), not a settlement; "
        "distances to the located stations in stations.geojson, not to the alignment",
        "threshold_50k": None,
        "pilot_sample": None,
    }
    rows.append(ard)
    return rows, {"mecca_ll": mecca_ll}


def _committed_station(r: pd.Series) -> str | None:
    t = clean(r["road_target_committed"])
    if not isinstance(t, str) or ":" not in t:
        return None
    return f"{t.split(':', 1)[1].title()} (site unlocated; approximate, R1a)"


def _sources(
    pop_source: str | None, roles: list[tuple[str, str, str]], road: dict[str, Any], r: pd.Series
) -> list[str]:
    out: list[str] = []
    if pop_source:
        out.append(pop_source)
    out.append("S-makkah-002")  # OSM ids and coordinates
    if road["road_min_existing"] is not None:
        out.append("S-r1a-809")
    out.extend(so for _, so, _ in roles)
    return sorted(set(out))


def to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    gov_order = {g: i for i, g in enumerate(sorted({r["governorate"] for r in rows}))}
    df["_g"] = df["governorate"].map(gov_order)
    df["_c"] = ~df["is_governorate_centre"]
    df["_p"] = df["population"].fillna(-1)
    df = df.sort_values(["_g", "_c", "_p"], ascending=[True, True, False]).drop(
        columns=["_g", "_c", "_p"]
    )
    return df.reset_index(drop=True)


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errs = []
    for i, rec in enumerate(rows):
        body = {k: v for k, v in rec.items() if k in ROW_FIELDS}
        try:
            RegionRow.model_validate(body)
        except ValueError as e:
            errs.append(f"row {i} {rec.get('name_en')}: {str(e).splitlines()[0:3]}")
    return errs


def write_outputs(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = to_frame(rows)
    keep = [c for c in ROW_FIELDS if c in df.columns]
    flat = df[[c for c in keep if c not in ("economic_roles", "sources")]].copy()
    table = pa.Table.from_pandas(flat, preserve_index=False)
    roles = [[{"role": x["role"], "source": x["source"]} for x in r] for r in df["economic_roles"]]
    table = table.append_column("economic_roles", pa.array(roles, type=ROLE_TYPE))
    table = table.append_column(
        "sources", pa.array([list(x) for x in df["sources"]], type=pa.list_(pa.string()))
    )
    meta = dict(table.schema.metadata or {})
    meta[b"governorates_gastat"] = str(GOVERNORATES_GASTAT).encode()
    meta[b"governorates_listed"] = str(len(set(df["governorate"]))).encode()
    table = table.replace_schema_metadata(meta)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT_PARQUET)
    csv = df[keep].copy()
    csv["economic_roles"] = csv["economic_roles"].map(lambda x: json.dumps(x, ensure_ascii=False))
    csv["sources"] = csv["sources"].map(lambda x: ";".join(x))
    csv.to_csv(OUT_CSV, index=False)
    return df


def cell(x: Any) -> str:
    """Markdown table cell: empty for None or NaN."""
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else str(x)


def write_markdown(df: pd.DataFrame, unmatched: pd.DataFrame) -> None:
    n10 = int(df["tag_10k"].sum())
    n5 = int(df["tag_5k"].sum())
    centres = int(df["is_governorate_centre"].sum())
    grid10_out = df[(df["pop_type"] == "grid") & (df["population"] >= 10000)]
    lines = [
        "> **Document version:** docs/regions/makkah.md v1.0 | 31 Oct "
        "2026 | Author: region-scout (REGION_MAKKAH) | Status: draft",
        "",
        "# Region register: Makkah (مكة المكرمة), R2 sweep",
        "",
        "Screening input, not a forecast. Label: synthetic demand, uncalibrated: "
        "scenario comparison, not a forecast.",
        "",
        "## 1. Counts",
        "",
        f"- Governorates: `governorates_gastat` = {GOVERNORATES_GASTAT} "
        f"(S-cp2-gastat-007 joined to the S-073 names; "
        f"sum 8,021,463 = S-soc-339). `governorates_listed` = {df['governorate'].nunique()}. "
        f"They match.",
        f"- Rows: {len(df)}; governorate centres: {centres} (all 17 "
        f"governorates have a row; Al-Ardiyat's centre is a centroid; its distances are to located "
        f"stations, not to the alignment).",
        f"- Rows with `tag_10k` true: {n10}. Rows with `tag_5k` true: {n5}.",
        f"- Grid-only rows at 10,000 or more held out of `tag_10k` (uncorroborated, "
        f"A-screen-031/032): {len(grid10_out)}.",
        "- Economic roles: sourced for the towns listed in section 4; "
        "roles not assessed for the rest (empty list means not sourced).",
        "- Terrain: not assessed (no DEM class in the R1a settlement "
        "universe); `terrain_class` is null everywhere.",
        "- Road minutes: OSRM free-flow skims from R1a (S-r1a-809, uncalibrated) "
        "where the universe has them.",
        "",
        "## 2. Register",
        "",
        "| name (EN) | name (AR) | governorate | pop | pop type | status "
        "| 10k | 5k | dist exist km | road min exist | dist metro km "
        "(tier) | screened | exclusion |",
        "|---|---|---|---:|---|---|---|---|---:|---:|---|---|---|",
    ]
    for _, r in df.iterrows():
        pop = "" if pd.isna(r["population"]) else f"{int(r['population']):,}"
        metro = (
            ""
            if pd.isna(r["dist_metro_km"])
            else f"{r['dist_metro_km']:.1f} ({r['nearest_metro']}, T{int(r['nearest_metro_tier'])})"
        )
        dist = "" if pd.isna(r["dist_existing_km"]) else f"{r['dist_existing_km']:.1f}"
        road = "" if pd.isna(r["road_min_existing"]) else f"{r['road_min_existing']:.0f}"
        lines.append(
            "| "
            + " | ".join(
                [
                    cell(r["name_en"]),
                    cell(r["name_ar"]),
                    cell(r["governorate"]),
                    pop,
                    cell(r["pop_type"]),
                    cell(r["pop_source_status"]),
                    "y" if r["tag_10k"] else "n",
                    "y" if r["tag_5k"] else "n",
                    dist,
                    road,
                    metro,
                    "y" if r["screened"] else "n",
                    cell(r["exclusion_reason"]),
                ]
            )
            + " |"
        )
    lines += [
        "",
        "## 3. Unmatched primary TA1 cities (name candidates are in the notes)",
        "",
        "All 69 primary TA1 cities (≥ 5,000) that matched no settlement, across all 13 regions",
        "(the export has no region column). They cannot be placed in Makkah without a region",
        "(`runs/gastat/primary/city_matches.csv`); they are listed so that none is dropped",
        "silently. Makkah membership is open (section 6).",
        "",
        "| city (export) | total 2022 | reason |",
        "|---|---:|---|",
    ]
    for _, u in unmatched.iterrows():
        lines.append(f"| {u['city']} | {int(u['total']):,} | {u['reason']} |")
    lines += [
        "",
        "## 4. Economic roles (sourced; town-level ties only)",
        "",
    ]
    for _, r in df[df["economic_roles"].map(len) > 0].iterrows():
        roles = ", ".join(f"{x['role']} ({x['source']})" for x in r["economic_roles"])
        lines.append(f"- {r['name_en']}: {roles}")
    lines += [
        "",
        "Not placed (no town-level tie or unlocated): Rabigh port (King "
        "Abdullah Port, governorate-level tie only, S-cp1-104); "
        "the Al-Qunfudhah port (negative result S-makkah-007); the Ad "
        "Duwayhi mine (region not assigned, unlocated); "
        "the giga-project role for KAEC (no PIF source tying Rabigh, "
        "S-cp1-104); the Modon Taif and Jeddah Oasis sites (no position).",
        "",
        "## 5. Sources",
        "",
        "Ids are in `docs/sources/r2-makkah.csv` and `docs/sources/index.csv`. "
        "Key: S-cp2-gastat-007 (governorate table), "
        "S-cp2-gastat-008 (city ≥ 5,000 table), S-makkah-001 (citypopulation.de "
        "relay), S-makkah-002 (OSM), S-makkah-008 "
        "(Nominatim boundary), S-makkah-009 (OSM population tags), S-r1a-505 "
        "(WorldPop 2020 100 m constrained), S-r1a-809 (OSRM).",
        "",
        "## 6. Needs Opus judgement (not resolved by guessing)",
        "",
        "1. Adham (أضم): the 9,022 figure is attributed by the Census "
        "2010 bridge, not a name match (A-makkah-003). Confirm against "
        "the primary table row.",
        "2. Al-Ardiyat seat: the centre is the boundary centroid; the "
        "seat town is not located (A-makkah-004).",
        "3. Grid rows within 25 km of Makkah city (for example Ash Sharai, "
        "Juranah, Shara'i al-Mujahidin) may sit inside the official "
        "Makkah city figure (A-makkah-007). Possible double count, not resolved.",
        "4. Unmatched primary cities (section 3): region and Makkah membership unknown. "
        "Name candidates are noted on the rows (Al Quoz: Alqawz 22,374; Ushayrah: Eshyrh 9,517; "
        "Ghran: Ghuran 6,803; Assel: Alsayl 6,064; Al 'Arfa': Aleurafa' 5,432). "
        "Malkan 5,196, Al Shoudayda 5,156 and Alshaqiraa 6,069 have no candidate row. "
        "Not changed without identity.",
        "5. Thuwal's governorate is Jiddah (S-makkah-004, snippet); "
        "Al-Hawiyah is in At-Ta'if (OSM). Both from snippets, not fetched pages.",
        "6. KAEC giga-project role and the Rabigh port role: governorate-level "
        "ties only (S-cp1-104); not placed.",
        "7. Missan/Maysan, Governorate of Jeddah naming: universe spellings "
        "mapped to S-073 names (A-makkah-006).",
        "8. Universe defect: `settlements.parquet` carries Adham's 9,022 "
        "on the Al-Mahd village node (KSA-ST-03308); the register drops "
        "that node, but the universe still needs fixing (coordinator).",
        "9. Terrain class for every row: not assessed.",
        "",
        "Screening input, not a forecast.",
        "",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines))


def unmatched_cities() -> pd.DataFrame:
    u = pd.read_csv(GASTAT_RUNS / "primary/city_matches.csv")
    return u[u["settlement_id"].isna()][["city", "total", "reason"]].sort_values(
        "total", ascending=False
    )


@app.callback()
def main() -> None:
    """Makkah region sweep builder (REGION_MAKKAH)."""


@app.command()
def build(
    seed: int = typer.Option(
        1, help="recorded for determinism (rule 10); the build has no randomness"
    ),
) -> None:
    """Build the register, validate every row against RegionRow and "
    "write Parquet, CSV and Markdown."""
    rows, _ = build_rows()
    errs = validate_rows(rows)
    if errs:
        for e in errs:
            typer.echo(f"FAIL {e}")
        raise typer.Exit(1)
    df = write_outputs(rows)
    write_markdown(df, unmatched_cities())
    typer.echo(
        f"ok   {OUT_PARQUET.name}: {len(df)} rows, {df['governorate'].nunique()} "
        f"governorates (seed {seed})"
    )


if __name__ == "__main__":
    app()
