"""Administrative zones and the settlement universe (PROJECT.md W1 "settlement universe").

- `regions` / `governorates`: OSM admin_level 4 (13 regions) and admin_level 6 (governorates)
  polygons inside Saudi Arabia from the GCC extract (ODbL), simplified, with the region key
  (ISO 3166-2 code of the containing region). Written to
  cities/ksa/zones/{regions,governorates}.geojson.
- `settlements`: every OSM `place=city|town|village|hamlet` node inside KSA, assigned to its
  governorate and region by point-in-polygon, plus the pilot-register rows (sourced populations)
  that match no OSM node. Population priority (A-r1a-001): pilot register (S-id, GASTAT via
  aggregator) > OSM `population` tag (ODbL; secondary) > population grid estimate (derived; licence
  in the row) > none (`pop_status: pending`). Written to cities/ksa/zones/settlements.parquet.

CLI:
  uv run python -m network.zones admin
  uv run python -m network.zones settlements [--grid data/ksa/grids/<file>.tif]
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import typer
import yaml
from shapely.geometry import Point, mapping, shape
from shapely.strtree import STRtree

from common import REPO_ROOT

OSM_CREDIT = "(c) OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright)"
ADMIN_SEQ = Path("data/ksa/osm/gcc-admin-areas.geojsonseq")
PLACES_SEQ = Path("data/ksa/osm/gcc-places.geojsonseq")
ZONES = Path("cities/ksa/zones")
PILOT = Path("cities/ksa/candidates-pilot.parquet")
PARAMS = Path("network/zones_params.yaml")
SETTLEMENT_PLACES = ("city", "town", "village", "hamlet")
ISO_REGION = {
    "SA-01": "riyadh",
    "SA-02": "makkah",
    "SA-03": "madinah",
    "SA-04": "eastern",
    "SA-05": "qassim",
    "SA-06": "hail",
    "SA-07": "tabuk",
    "SA-08": "northern_borders",
    "SA-09": "jazan",
    "SA-10": "najran",
    "SA-11": "al_baha",
    "SA-12": "al_jouf",
    "SA-14": "asir",
}

app = typer.Typer(add_completion=False, help="Regions, governorates and the settlement universe.")


def _seq(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip().lstrip("\x1e")
            if line:
                yield json.loads(line)


def load_params(root: Path = REPO_ROOT) -> dict:
    return yaml.safe_load((root / PARAMS).read_text(encoding="utf-8"))


def ksa_polygon(root: Path = REPO_ROOT):
    fc = json.loads((root / ZONES / "ksa.geojson").read_text(encoding="utf-8"))
    return shape(fc["features"][0]["geometry"])


def admin_frames(root: Path = REPO_ROOT) -> tuple[list[dict], list[dict]]:
    """Regions (level 4) and governorates (level 6) inside KSA as lists of dicts with geometry."""
    ksa = ksa_polygon(root)
    regions, govs = [], []
    for f in _seq(root / ADMIN_SEQ):
        p = f["properties"]
        lvl = p.get("admin_level")
        if lvl not in ("4", "6") or p.get("@type") != "relation":
            continue
        geom = shape(f["geometry"])
        if not ksa.contains(geom.representative_point()):
            continue
        row = {
            "osm_id": p["@id"],
            "name_en": p.get("name:en") or p.get("name"),
            "name_ar": p.get("name:ar") or p.get("name"),
            "wikidata": p.get("wikidata"),
            "geometry": geom,
        }
        if lvl == "4":
            row["iso3166_2"] = p.get("ISO3166-2")
            row["region"] = ISO_REGION.get(p.get("ISO3166-2"))
            regions.append(row)
        else:
            govs.append(row)
    for g in govs:
        pt = g["geometry"].representative_point()
        hits = [r for r in regions if r["geometry"].contains(pt)]
        g["region"] = hits[0]["region"] if hits else None
    return regions, govs


def _write_fc(path: Path, rows: list[dict], name: str, tol: float) -> None:
    feats = []
    for r in rows:
        props = {k: v for k, v in r.items() if k != "geometry"}
        geom = r["geometry"].simplify(tol, preserve_topology=True)
        feats.append({"type": "Feature", "properties": props, "geometry": mapping(geom)})
    fc = {
        "type": "FeatureCollection",
        "name": name,
        "attribution": OSM_CREDIT,
        "licence": "ODbL-1.0 (derived database of OpenStreetMap)",
        "source": "osm-gcc-2026-10-14",
        "simplify_deg": tol,
        "features": feats,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n", "utf-8")


@app.command()
def admin(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Write regions.geojson and governorates.geojson (OSM admin polygons, ODbL)."""
    params = load_params(root)
    tol = params["simplify_deg"]["value"]
    regions, govs = admin_frames(root)
    regions.sort(key=lambda r: r["iso3166_2"] or "")
    govs.sort(key=lambda g: (g["region"] or "", g["name_en"] or ""))
    for i, g in enumerate(govs, 1):
        g["gov_id"] = g["zone_id"] = f"G{i:03d}"  # zone_id: national skim zones (network.skims)
    _write_fc(root / ZONES / "regions.geojson", regions, "regions", tol)
    _write_fc(root / ZONES / "governorates.geojson", govs, "governorates", tol)
    counts = pd.Series([g["region"] for g in govs]).value_counts().sort_index()
    typer.echo(f"regions {len(regions)}; governorates {len(govs)}")
    typer.echo(counts.to_string())


# ----------------------------------------------------------------------------- grids
def read_geotiff(path: Path) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    """Single-band north-up GeoTIFF via Pillow: returns (array, (x0, y0, dx, dy)), no rasterio."""
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(path)
    tie = im.tag_v2[33922]  # ModelTiepointTag (i, j, k, x, y, z)
    scale = im.tag_v2[33550]  # ModelPixelScaleTag (dx, dy, dz)
    arr = np.array(im, dtype="float32")
    nodata = im.tag_v2.get(42113)
    if nodata is not None:
        arr[arr == float(nodata)] = np.nan
    arr[arr < 0] = np.nan
    return arr, (tie[3] - tie[0] * scale[0], tie[4] + tie[1] * scale[1], scale[0], scale[1])


def grid_sum_within(arr, transform, lat: float, lon: float, radius_km: float) -> float:
    """Sum of grid cells whose centre lies within radius_km of (lat, lon)."""
    x0, y0, dx, dy = transform
    km_per_deg = 111.32
    rlat = radius_km / km_per_deg
    rlon = radius_km / (km_per_deg * max(math.cos(math.radians(lat)), 1e-6))
    c0, c1 = int((lon - rlon - x0) / dx), int((lon + rlon - x0) / dx) + 1
    r0, r1 = int((y0 - (lat + rlat)) / dy), int((y0 - (lat - rlat)) / dy) + 1
    c0, r0 = max(c0, 0), max(r0, 0)
    c1, r1 = min(c1, arr.shape[1]), min(r1, arr.shape[0])
    if c0 >= c1 or r0 >= r1:
        return float("nan")
    sub = arr[r0:r1, c0:c1]
    cols = x0 + (np.arange(c0, c1) + 0.5) * dx
    rows = y0 - (np.arange(r0, r1) + 0.5) * dy
    lon_g, lat_g = np.meshgrid(cols, rows)
    dkm = np.hypot(
        (lat_g - lat) * km_per_deg, (lon_g - lon) * km_per_deg * math.cos(math.radians(lat))
    )
    return float(np.nansum(np.where(dkm <= radius_km, sub, 0.0)))


def grid_allocate_nearest(arr, transform, lats, lons, radii_km) -> np.ndarray:
    """Allocate every populated grid cell to its nearest settlement if the cell centre lies within
    that settlement's radius; returns the population per settlement (no double counting)."""
    from scipy.spatial import cKDTree

    x0, y0, dx, dy = transform
    rows, cols = np.nonzero(np.nan_to_num(arr) > 0)
    vals = arr[rows, cols].astype("float64")
    clat = y0 - (rows + 0.5) * dy
    clon = x0 + (cols + 0.5) * dx

    def xyz(lat, lon):
        la, lo = np.radians(lat), np.radians(lon)
        return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]

    tree = cKDTree(xyz(np.asarray(lats), np.asarray(lons)))
    d, j = tree.query(xyz(clat, clon))
    km = d * 6371.0088
    ok = km <= np.asarray(radii_km)[j]
    out = np.zeros(len(lats))
    np.add.at(out, j[ok], vals[ok])
    return out


# ----------------------------------------------------------------------------- settlements
def _osm_population(p: dict) -> tuple[int | None, int | None]:
    raw = (p.get("population") or "").replace(",", "").replace(" ", "")
    if not raw.isdigit():
        return None, None
    year = None
    for k in ("population:date", "source:population:date", "census:population"):
        v = p.get(k) or ""
        if v[:4].isdigit():
            year = int(v[:4])
            break
    return int(raw), year


def osm_places(root: Path, ksa) -> pd.DataFrame:
    rows = []
    for f in _seq(root / PLACES_SEQ):
        p = f["properties"]
        if p.get("place") not in SETTLEMENT_PLACES or p.get("@type") != "node":
            continue
        lon, lat = f["geometry"]["coordinates"]
        if not ksa.contains(Point(lon, lat)):
            continue
        pop, year = _osm_population(p)
        rows.append(
            {
                "osm_type": "node",
                "osm_id": int(p["@id"]),
                "place": p["place"],
                "name_en": p.get("name:en") or p.get("int_name") or p.get("name"),
                "name_ar": p.get("name:ar") or p.get("name"),
                "lat": lat,
                "lon": lon,
                "osm_population": pop,
                "osm_population_year": year,
                "wikidata": p.get("wikidata"),
            }
        )
    return pd.DataFrame(rows)


def assign_admin(df: pd.DataFrame, govs: list[dict], regions: list[dict]) -> pd.DataFrame:
    gtree = STRtree([g["geometry"] for g in govs])
    rtree = STRtree([r["geometry"] for r in regions])
    pts = [Point(xy) for xy in zip(df.lon, df.lat, strict=True)]
    gi = gtree.query(pts, predicate="within")
    ri = rtree.query(pts, predicate="within")
    gmap = dict(zip(gi[0], gi[1], strict=True))
    rmap = dict(zip(ri[0], ri[1], strict=True))
    df = df.copy()
    df["gov_id"] = [govs[gmap[i]]["gov_id"] if i in gmap else None for i in range(len(df))]
    df["governorate"] = [govs[gmap[i]]["name_en"] if i in gmap else None for i in range(len(df))]
    df["governorate_ar"] = [govs[gmap[i]]["name_ar"] if i in gmap else None for i in range(len(df))]
    df["region"] = [regions[rmap[i]]["region"] if i in rmap else None for i in range(len(df))]
    df["admin_method"] = ["point_in_polygon" if i in gmap else None for i in range(len(df))]
    for i in [i for i in range(len(df)) if i not in gmap]:  # coast/islands: nearest polygon
        k = int(gtree.nearest(pts[i]))
        g = govs[k]
        df.loc[df.index[i], ["gov_id", "governorate", "governorate_ar", "region"]] = [
            g["gov_id"],
            g["name_en"],
            g["name_ar"],
            g["region"],
        ]
        km = g["geometry"].distance(pts[i]) * 111.32
        df.loc[df.index[i], "admin_method"] = f"nearest_polygon ({km:.1f} km outside)"
    return df


def load_govs(root: Path) -> tuple[list[dict], list[dict]]:
    out = []
    for name in ("governorates", "regions"):
        fc = json.loads((root / ZONES / f"{name}.geojson").read_text(encoding="utf-8"))
        out.append([{**f["properties"], "geometry": shape(f["geometry"])} for f in fc["features"]])
    return out[0], out[1]


def match_pilot(places: pd.DataFrame, pilot: pd.DataFrame, max_km: float) -> pd.DataFrame:
    """Attach pilot rows (sourced populations) to OSM place nodes by node id, else nearest node
    within max_km; unmatched pilot rows are returned as extra rows."""
    from scipy.spatial import cKDTree

    def xyz(lat, lon):
        la, lo = np.radians(lat), np.radians(lon)
        return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]

    tree = cKDTree(xyz(places.lat.to_numpy(), places.lon.to_numpy()))
    idx_by_id = {int(i): k for k, i in enumerate(places.osm_id)}
    places = places.copy()
    for col in ("pilot_row_key", "pilot_population", "pilot_pop_source", "pilot_pop_type"):
        places[col] = None
    for col in ("pilot_pop_year", "pilot_pop_status", "pilot_is_seat", "pilot_match"):
        places[col] = None
    extra = []
    taken: set[int] = set()
    for _, r in pilot.iterrows():
        k = None
        how = None
        if r.osm_type == "node" and pd.notna(r.osm_id) and int(r.osm_id) in idx_by_id:
            k, how = idx_by_id[int(r.osm_id)], "osm_node_id"
        else:
            d, j = tree.query(xyz(np.array([r.lat]), np.array([r.lon]))[0])
            km = d * 6371.0088
            if km <= max_km and j not in taken:
                k, how = int(j), f"nearest_node_{km:.2f}km"
        if k is None or k in taken:
            extra.append(r)
            continue
        taken.add(k)
        places.loc[places.index[k], "pilot_row_key"] = r.row_key
        if pd.notna(r.population):
            places.loc[places.index[k], "pilot_population"] = int(r.population)
            places.loc[places.index[k], "pilot_pop_source"] = r.pop_source
            places.loc[places.index[k], "pilot_pop_type"] = r.pop_type
            places.loc[places.index[k], "pilot_pop_year"] = int(r.pop_year)
            places.loc[places.index[k], "pilot_pop_status"] = r.pop_source_status
        places.loc[places.index[k], "pilot_is_seat"] = bool(r.is_governorate_centre)
        places.loc[places.index[k], "pilot_match"] = how
    ex = pd.DataFrame(extra)
    if len(ex):
        ex = pd.DataFrame(
            {
                "osm_type": ex.osm_type,
                "osm_id": ex.osm_id,
                "place": None,
                "name_en": ex.name_en,
                "name_ar": ex.name_ar,
                "lat": ex.lat,
                "lon": ex.lon,
                "osm_population": None,
                "osm_population_year": None,
                "wikidata": None,
                "pilot_row_key": ex.row_key,
                "pilot_population": ex.population.astype("Int64"),
                "pilot_pop_source": ex.pop_source,
                "pilot_pop_type": ex.pop_type,
                "pilot_pop_year": ex.pop_year.astype("Int64"),
                "pilot_pop_status": ex.pop_source_status,
                "pilot_is_seat": ex.is_governorate_centre,
                "pilot_match": "pilot_only (no OSM place node within the match radius)",
            }
        )
        places = pd.concat([places, ex], ignore_index=True)
    return places


def choose_population(df: pd.DataFrame, grid, params: dict, grid_meta: dict | None) -> pd.DataFrame:
    """Population per row by priority: pilot register > OSM tag > grid allocation > pending."""
    df = df.copy()
    radius = params["grid_radius_km"]["value"]
    radii = [radius.get(p, radius["default"]) for p in df.place]
    gridpop = None
    if grid is not None:
        gridpop = grid_allocate_nearest(grid[0], grid[1], df.lat, df.lon, radii)
    df["grid_population"] = None if gridpop is None else np.round(gridpop).astype("int64")
    pop, year, ptype, src, status, method, lic = [], [], [], [], [], [], []
    aid = params["grid_radius_km"]["assumption_id"]
    for k, r in enumerate(df.itertuples(index=False)):
        if pd.notna(r.pilot_population):
            pop.append(int(r.pilot_population))
            year.append(int(r.pilot_pop_year))
            ptype.append(r.pilot_pop_type)
            src.append(r.pilot_pop_source)
            status.append(r.pilot_pop_status or "secondary")
            method.append("pilot register (cities/ksa/candidates-pilot.parquet)")
            lic.append("facts cited (see source row)")
        elif pd.notna(r.osm_population):
            pop.append(int(r.osm_population))
            year.append(int(r.osm_population_year) if pd.notna(r.osm_population_year) else None)
            ptype.append("derived")
            src.append(f"osm-gcc-2026-10-14 node/{int(r.osm_id)} population tag")
            status.append("secondary")
            method.append("OSM population tag (contributor value; year from population:date)")
            lic.append("ODbL-1.0")
        elif gridpop is not None:
            pop.append(int(round(gridpop[k])))
            year.append(grid_meta["year"])
            ptype.append("grid")
            src.append(grid_meta["manifest_id"])
            status.append("unverified")
            method.append(
                f"grid cells allocated to the nearest settlement within {radii[k]} km ({aid})"
            )
            lic.append(grid_meta["licence"])
        else:
            pop.append(None)
            year.append(None)
            ptype.append(None)
            src.append(None)
            status.append(None)
            method.append("pending: no tabulated population; grid not available")
            lic.append(None)
    df["population"] = pd.array(pop, dtype="Int64")
    df["pop_year"] = pd.array(year, dtype="Int64")
    df["pop_type"] = ptype
    df["pop_source"] = src
    df["pop_source_status"] = status
    df["pop_method"] = method
    df["pop_licence"] = lic
    quality = np.select(
        [
            df.pop_type.isin(["official"]),
            df.pop_method.str.startswith("OSM"),
            df.pop_type.eq("grid") & df.population.fillna(0).gt(0),
            df.pop_type.eq("grid"),
        ],
        ["tabulated_secondary", "osm_tag", "grid_estimate", "grid_zero"],
        default="pending",
    )
    df["pop_quality"] = quality
    return df


@app.command()
def settlements(
    grid: Path | None = typer.Option(None, help="population GeoTIFF (WorldPop/GHSL) or none"),
    grid_manifest_id: str = typer.Option("", help="manifest id of the grid file"),
    grid_year: int = typer.Option(2020),
    grid_licence: str = typer.Option("CC-BY-4.0"),
    out: Path = typer.Option(ZONES / "settlements.parquet"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Build the settlement universe (no distance fields; `network.distances` adds them)."""
    params = load_params(root)
    ksa = ksa_polygon(root)
    govs, regions = load_govs(root)
    places = osm_places(root, ksa)
    pilot = pd.read_parquet(root / PILOT)
    df = match_pilot(places, pilot, params["pilot_match_km"]["value"])
    df = assign_admin(df, govs, regions)
    g = None
    meta = None
    if grid is not None:
        g = read_geotiff(grid if grid.is_absolute() else root / grid)
        meta = {"year": grid_year, "manifest_id": grid_manifest_id, "licence": grid_licence}
    df = choose_population(df, g, params, meta)
    df.insert(0, "settlement_id", [f"KSA-ST-{i:05d}" for i in range(1, len(df) + 1)])
    df["osm_id"] = df["osm_id"].astype("Int64")
    df["tag_10k"] = df.population.fillna(0) >= 10_000  # A-screen-001
    df["tag_5k"] = df.population.fillna(0) >= 5_000  # A-screen-002
    df["attribution"] = OSM_CREDIT
    df.to_parquet(root / out, index=False)
    typer.echo(f"settlements {len(df)}; with population {int(df.population.notna().sum())}")
    typer.echo(df.pop_type.value_counts(dropna=False).to_string())


@app.command("gov-points")
def gov_points(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """One zone point per governorate: its most populous settlement (A-r1a-006b), for skims."""
    df = pd.read_parquet(root / ZONES / "settlements.parquet")
    df = df[df.population.notna()].sort_values("population", ascending=False)
    top = df.groupby("gov_id", as_index=False).first()
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r.lon, r.lat]},
            "properties": {
                "zone_id": r.gov_id,
                "governorate": r.governorate,
                "region": r.region,
                "settlement_id": r.settlement_id,
                "name_en": r.name_en,
                "population": int(r.population),
                "pop_type": r.pop_type,
                "pop_source": r.pop_source,
                "method": "most populous settlement of the governorate (A-r1a-001 priority)",
            },
        }
        for r in top.itertuples(index=False)
    ]
    fc = {
        "type": "FeatureCollection",
        "name": "governorate_points",
        "attribution": OSM_CREDIT,
        "features": feats,
    }
    (root / ZONES / "governorate_points.geojson").write_text(
        json.dumps(fc, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )
    typer.echo(f"governorate points {len(feats)}")


if __name__ == "__main__":
    app()
