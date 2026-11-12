"""Region sweep for Northern Borders (R2 REGION_NORTHERN_BORDERS; `region-sweep` skill).

Builds cities/ksa/regions/northern_borders.parquet (+ CSV mirror) from the R1a settlement universe
(cities/ksa/zones/settlements.parquet, region == northern_borders) and the R1a economic nodes.

Population follows the CP2 and addendum rule: the GASTAT primary TA1 city export (S-cp2-gastat-008)
first; then a secondary GASTAT figure relayed by citypopulation.de (S-northern_borders-001, flagged
secondary); then the WorldPop grid (S-r1a-506) as a gap-fill only, gated by A-screen-031/032.
Nothing is estimated here: a grid cell sum of zero is recorded as no population.

uv run python -m screening.sweeps.northern_borders.build   (repo root, venv python)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
UNIVERSE = ROOT / "cities/ksa/zones/settlements.parquet"
ECON = ROOT / "cities/ksa/zones/economic_nodes.csv"
PILOT = ROOT / "cities/ksa/regions/archive/pilot/pilot-northern_borders.parquet"
OUT_PQ = ROOT / "cities/ksa/regions/northern_borders.parquet"
OUT_CSV = ROOT / "cities/ksa/regions/northern_borders.csv"

REGION = "northern_borders"
GOV_GASTAT = 4  # S-cp2-gastat-007: Arar, Rafha, Turayf, Al Uwayqilah (150 governorates in total)
GOV_LISTED = 4
TAG_10K, TAG_5K = 10_000, 5_000
S_PRIMARY_CITY = "S-cp2-gastat-008"
S_PRIMARY_GOV = "S-cp2-gastat-007"
S_SECONDARY = "S-northern_borders-001"
S_GRID = "S-r1a-506"
S_OSM = "S-r1a-210"
S_ROAD = "S-r1a-809"
S_TERRAIN = "S-northern_borders-010"
S_ADMIN_A = "S-northern_borders-002"
S_ADMIN_B = "S-northern_borders-003"

# Governorate centres: universe settlement_id of the seat -> GASTAT governorate (English)
CENTRES = {
    "KSA-ST-00883": "Arar",
    "KSA-ST-00277": "Rafha",
    "KSA-ST-00872": "Turayf",
    "KSA-ST-00873": "Al Uwayqilah",
}
GOV_TOTAL = {  # S-cp2-gastat-007 governorate totals (not used as a population)
    "Arar": 202_719,
    "Rafha": 84_536,
    "Turayf": 66_004,
    "Al Uwayqilah": 20_318,
}
# Universe rows holding an Arabic-only record of a place already present (excluded, no double count)
DUPLICATES = {"KSA-ST-03247": ("KSA-ST-00857", "Ibn Bakr")}
# Stray characters in universe English names (corrected here; the notes say so)
NAME_FIX = {"KSA-ST-00883": "Arar", "KSA-ST-00873": "Al-Uwayqilah"}
# R1a economic_nodes node_id -> (settlement_id, role, sources); the town tie is by nearest_town_en
ECON_ROLE_MAP = {
    "airport-rae-arar": ("KSA-ST-00883", "airport", "S-cp1-100;S-r1a-210"),
    "airport-rah-rafha": ("KSA-ST-00277", "airport", "S-cp1-100;S-r1a-210"),
    "airport-tui-turaif": ("KSA-ST-00872", "airport", "S-cp1-100;S-r1a-210"),
    "modon-arar": ("KSA-ST-00883", "industrial_city", "S-r1a-204"),
    "univ-northern-borders": ("KSA-ST-00883", "university", "S-r1a-221;S-r1a-222;S-r1a-210"),
    "border-arar-iraq": ("KSA-ST-00883", "border_crossing", "S-r1a-210"),
    "maaden-al-jalamid-phosphate": ("KSA-ST-00856", "mining", "S-r1a-211;S-r1a-210"),
}  # fmt: skip
# Governorate seats: an administrative role (kept in the data; outside the screening score)
ADMIN_SEATS = {sid: g for sid, g in CENTRES.items()}
# Terrain: assumed (A-northern_borders-001), not DEM-verified
TERRAIN_BY_GOV = {"Rafha": "dunes"}
DEFAULT_TERRAIN = "flat_desert"
LINE_SOURCE = {"sar-north-passenger": "S-017", "gcc-railway-ksa": "S-029", "landbridge": "S-054"}

# Row notes for the rows that need one (keyed by universe settlement_id)
NOTES = {
    "KSA-ST-00883": (
        "Governorate centre (Arar). Population is the Census 2022 locality figure 199,247, not the "
        "governorate total 202,719 (S-cp2-gastat-007). Universe name '`Ar`ar' corrected to Arar. "
        "Arar Domestic Airport (S-cp1-100); Northern Borders University (S-r1a-221, S-r1a-222); "
        "Arar-Iraq border post (S-r1a-210; the brief names Jadidat Arar, see Needs Opus judgement); "  # noqa: E501
        "MODON Arar Industrial City (S-r1a-204; no position sourced)."
    ),
    "KSA-ST-00277": (
        "Governorate centre (Rafha). Locality 63,929, not the governorate total 84,536 "
        "(S-cp2-gastat-007). Rafha Domestic Airport (S-cp1-100). Terrain 'dunes' assumed "
        "(A-northern_borders-001)."
    ),
    "KSA-ST-00872": (
        "Governorate centre (Turayf; GASTAT spelling Turayf, OSM Turayf). Locality 61,395, not the "
        "governorate total 66,004 (S-cp2-gastat-007). Turaif Domestic Airport, TUI (S-cp1-100). "
        "Not the Iraq-Jordan crossing Turaibil."
    ),
    "KSA-ST-00873": (
        "Governorate centre (Al-Uwayqilah). Primary city name 'Aluwayqilah' (S-cp2-gastat-008; "
        "identical to the relayed figure); locality 17,055, not the governorate total 20,318."
    ),
    "KSA-ST-00981": (
        "Primary city name 'Rawdat Hibas' (S-cp2-gastat-008); OSM 'Rawdat Habbas'. The relayed "
        "figure 5,620 (S-cp2-gastat-001) matches the primary. The OSM place tag 5,532 is a 2010 "
        "value and is not used. Tagged 5k only."
    ),
    "KSA-ST-00989": (
        "Place below 5,000: not in the TA1 city export (cities of 5,000 or more), so the "
        "citypopulation.de figure (S-northern_borders-001) stays secondary. Name match to the "
        "GASTAT locality 'At Timyat' not confirmed. OSM 'village'."
    ),
    "KSA-ST-00391": (
        "Place below 5,000 (secondary 3,430, S-northern_borders-001); not in the TA1 city export. "
        "The universe grid figure is 7,536 (2.2 times the secondary figure): a grid over-count "
        "flag, not used. OSM 'town' on a 3,430 place (tag/size mismatch, pilot)."
    ),
    "KSA-ST-00393": (
        "Grid-only population 17,616 (WorldPop, S-r1a-506). Not in the GASTAT city list of 5,000 "
        "or more (S-cp2-gastat-008) under any spelling tried (Linah, Lina, Lin), which points to a "
        "population below 5,000 and to a grid over-count (region grid exceeds the residual: "
        "control_total_flag). tag_5k kept true because tag_5k is not gated. tag_10k false: no "
        "second method run (A-screen-032). Needs Opus judgement. Pilot: OSM lists Linah twice (town "  # noqa: E501
        "node 1236407820 and a village way); one row kept."
    ),
    "KSA-ST-00884": (
        "Grid-only population 10,670 (WorldPop, S-r1a-506). OSM 'hamlet' (universe) with a "
        "grid figure above 10,000. Not in the GASTAT city list of 5,000 or more under the name "
        "Badanah. Unmatched primary name 'Albadie Walqarfi' (8,623; no OSM settlement by name) may "
        "be a variant; not resolved. tag_10k false (uncorroborated). Needs Opus judgement."
    ),
    "KSA-ST-00856": (
        "Ma'aden Al-Jalamid phosphate mine and beneficiation plant (S-r1a-211, S-r1a-210). The "
        "mine polygon (31.507 N, 39.930 E) is about 30 km from the OSM village node used for the "
        "row (31.280 N, 40.104 E): R1a conflict, see Needs Opus judgement. dist_existing_km is to "
        "the passenger stations (R1a, A-r1a-008); the nearest existing rail by alignment is the "
        "SAR North freight line (S-019) at 14.2 km (any-line column, A-r1a-007), which is the pilot's "  # noqa: E501
        "14.2 km. Population: WorldPop grid only (187), unverified; no threshold depends on it."
    ),
    "KSA-ST-01533": (
        "2010 city of 5,125 (runs/gastat/apply/cities2010_growth.csv) but not in the 2022 city "
        "list of 5,000 or more. WorldPop cells sum to 0, so the 2010-growth estimate (5,438; "
        "A-screen-035) cannot be tested against a grid figure and is not used. Needs Opus judgement: "  # noqa: E501
        "merged into Arar or below 5,000 in 2022?"
    ),
    "KSA-ST-03247": "Arabic-only record of Ibn Bakr (KSA-ST-00857); excluded to avoid double counting.",  # noqa: E501
}
# Extra sources for a row (the SAR North freight line, nearest existing rail by alignment)
EXTRA_SOURCES = {"KSA-ST-00856": ["S-019"]}
GRID_BELOW_5K = "WorldPop gap-fill only (S-r1a-506); no official figure; below 5,000."
NO_POP = "No population: no GASTAT figure and WorldPop cells sum to 0 (not guessed)."


def _name_en(r: pd.Series) -> str:
    if r.settlement_id in NAME_FIX:
        return NAME_FIX[r.settlement_id]
    if isinstance(r.name_en, str) and r.name_en.strip():
        return r.name_en.strip()
    return f"unnamed OSM {r.osm_type} {int(r.osm_id)}"


def _pop(r: pd.Series) -> dict:
    """Population by the CP2 rule: primary > secondary > grid gap-fill (A-screen-031…033)."""
    out = dict(population=None, pop_source=None, pop_year=None, pop_type=None,
               pop_source_status=None, primary_to_find=None)  # fmt: skip
    if r.settlement_id in DUPLICATES:
        return out
    if r.pop_type == "official" and str(r.pop_source).startswith("gastat-census2022-ta1-city5k"):
        out.update(population=int(r.population), pop_source=S_PRIMARY_CITY, pop_year=2022,
                   pop_type="official", pop_source_status="verified")  # fmt: skip
    elif r.pop_type == "official" and r.pop_source == S_SECONDARY:
        out.update(population=int(r.population), pop_source=S_SECONDARY, pop_year=2022,
                   pop_type="official", pop_source_status="secondary",
                   primary_to_find="GASTAT Census 2022 locality table (place below 5,000; the TA1 city export lists cities of 5,000 or more only)")  # fmt: skip  # noqa: E501
    elif r.pop_type == "grid" and pd.notna(r.population) and r.population > 0:
        out.update(population=int(r.population), pop_source=S_GRID, pop_year=2020,
                   pop_type="grid", pop_source_status="unverified")  # fmt: skip
    return out


def _roles(econ: pd.DataFrame) -> dict[str, list[dict]]:
    roles: dict[str, list[dict]] = {}
    for node_id, (sid, role, src) in ECON_ROLE_MAP.items():
        if node_id not in set(econ.node_id):
            raise ValueError(f"economic node missing from R1a: {node_id}")
        roles.setdefault(sid, []).append({"role": role, "source": src})
    for sid in ADMIN_SEATS:
        roles.setdefault(sid, []).append(
            {"role": "administrative", "source": f"{S_ADMIN_B};{S_ADMIN_A}"}
        )
    return roles


def _sources(sid: str, p: dict, centre: bool, econ_roles: list[dict], line: str, comm: str) -> list:
    src = [S_OSM, S_ROAD, S_TERRAIN]
    if p["pop_source"]:
        src.append(p["pop_source"])
    if centre:
        src.append(S_PRIMARY_GOV)
    if sid in ADMIN_SEATS:
        src += [S_ADMIN_A, S_ADMIN_B]
    for x in econ_roles:
        src += [s for s in x["source"].split(";") if s]
    src += EXTRA_SOURCES.get(sid, [])
    if line:
        src.append(LINE_SOURCE.get(line, "S-017"))
    if comm:
        src.append(LINE_SOURCE.get(comm, S_OSM))
    return list(dict.fromkeys(src))


def build() -> pd.DataFrame:
    u = pd.read_parquet(UNIVERSE)
    n = u[u.region == REGION].copy()
    econ = pd.read_csv(ECON)
    econ = econ[econ.region == REGION]
    roles = _roles(econ)
    rows = []
    for _, r in n.iterrows():
        sid = r.settlement_id
        p = _pop(r)
        pop = p["population"]
        centre = sid in CENTRES
        gov = r.governorate
        econ_roles = roles.get(sid, [])
        tag_5k = pop is not None and pop >= TAG_5K
        gated_10k = pop is not None and pop >= TAG_10K
        tag_10k = gated_10k and p["pop_type"] != "grid"  # grid rows need corroboration (none run)
        line = r.nearest_existing_line if isinstance(r.nearest_existing_line, str) else None
        comm = r.nearest_committed_line if isinstance(r.nearest_committed_line, str) else None
        exclusion = None
        if sid in DUPLICATES:
            other, other_name = DUPLICATES[sid]
            exclusion = f"duplicate of {other} ({other_name}): Arabic-only record of the same place"
            screened = False
        elif p["pop_type"] == "grid" and gated_10k:
            exclusion = "grid-only population, uncorroborated"
            screened = True
        elif centre or tag_5k or econ_roles:
            screened = True
        else:
            screened = False
            if pop is None:
                exclusion = "no sourced or grid population; no sourced economic role"
            elif p["pop_type"] == "grid":
                exclusion = "below 5,000 (grid estimate only); no sourced economic role"
            else:
                exclusion = "below 5,000 (secondary figure); no sourced economic role"
        notes = NOTES.get(sid)
        if notes is None:
            if pop is None:
                notes = NO_POP
            elif p["pop_type"] == "grid":
                notes = GRID_BELOW_5K
            else:
                notes = ""
        if centre and gov in GOV_TOTAL and sid not in NOTES:
            notes = f"Governorate centre ({gov})."
        rows.append(
            dict(
                name_ar=r.name_ar if isinstance(r.name_ar, str) else "",
                name_en=_name_en(r),
                region=REGION,
                governorate=gov,
                governorate_ar=r.governorate_ar,
                is_governorate_centre=centre,
                osm_id=int(r.osm_id) if pd.notna(r.osm_id) else None,
                osm_type=r.osm_type if isinstance(r.osm_type, str) else None,
                lat=float(r.lat),
                lon=float(r.lon),
                population=pop,
                pop_source=p["pop_source"],
                pop_year=p["pop_year"],
                pop_type=p["pop_type"],
                pop_source_status=p["pop_source_status"],
                primary_to_find=p["primary_to_find"],
                pop_corroboration=None,
                pop_corroboration_value=None,
                tag_10k=bool(tag_10k),
                tag_5k=bool(tag_5k),
                dist_existing_km=round(float(r.dist_existing_km), 2),
                road_min_existing=round(float(r.road_min_existing), 1),
                nearest_existing=line,
                dist_committed_km=round(float(r.dist_committed_km), 2),
                road_min_committed=round(float(r.road_min_committed), 1),
                nearest_committed=comm,
                nearest_committed_station=None,
                dist_metro_km=round(float(r.dist_metro_city_km), 2),
                road_min_metro=round(float(r.road_min_metro_city), 1),
                nearest_metro=r.nearest_metro_city.rsplit(" (", 1)[0],
                nearest_metro_tier=int(r.nearest_metro_tier),
                economic_roles=econ_roles,
                terrain_class=TERRAIN_BY_GOV.get(gov, DEFAULT_TERRAIN),
                screened=bool(screened),
                exclusion_reason=exclusion,
                sources=_sources(sid, p, centre, econ_roles, line, comm),
                fixture=False,
                threshold_50k=None,
                pilot_sample=None,
                road_min_method="R1a OSRM car skim (osrm_table_mld_car; free flow, uncalibrated; S-r1a-809)",  # noqa: E501
                dist_method="dist_existing_km: great circle to the 15 intercity passenger stations (R1a, A-r1a-008); committed: alignment vertices at 1 km (A-r1a-007); road: OSRM car (A-northern_borders-002)",  # fmt: skip  # noqa: E501
                notes=notes,
                _sid=sid,
            )
        )
    df = pd.DataFrame(rows)
    # Rows with an official population first, then by population, then name (stable order)
    df = df.assign(_k=df.population.fillna(-1)).sort_values(
        ["_k", "name_en"], ascending=[False, True]
    )
    return df.drop(columns=["_k"]).reset_index(drop=True)


def pilot_distances() -> pd.DataFrame:
    """Pilot haversine distances keyed by osm_id, for the changes table in the region note."""
    p = pd.read_parquet(PILOT)
    return p[["osm_id", "name_en", "dist_existing_km", "dist_metro_km"]]


def write(df: pd.DataFrame) -> None:
    out = df.drop(columns=["_sid"])
    cols = list(out.columns)
    table = pa.Table.from_pandas(out[cols], preserve_index=False)
    meta = {
        b"governorates_gastat": str(GOV_GASTAT).encode(),
        b"governorates_listed": str(GOV_LISTED).encode(),
    }
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
    OUT_PQ.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT_PQ)
    csv = out.copy()
    csv["economic_roles"] = csv.economic_roles.map(
        lambda rs: ";".join(f"{x['role']}:{x['source']}" for x in rs)
    )
    csv["sources"] = csv.sources.map(lambda s: ";".join(s))
    csv["osm_id"] = csv.osm_id.astype("Int64")
    csv["population"] = csv.population.astype("Int64")
    csv["pop_year"] = csv.pop_year.astype("Int64")
    csv.to_csv(OUT_CSV, index=False)


if __name__ == "__main__":
    df = build()
    write(df)
    print(df[["name_en", "population", "pop_type", "tag_10k", "tag_5k", "screened"]].to_string())
    print("rows", len(df))
