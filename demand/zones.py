"""Demand zones (W8, R3 task 1): governorate zones Kingdom-wide and hexagon sub-zones inside the
metro governorates (CP1 metro list, A-screen-013).

- National: one zone per OSM governorate polygon (149; GASTAT's 150th, Al Amoah, is merged into
  Tathlith, A-pop-007), Census 2022 population (S-cp2-gastat-007), point = the governorate's most
  populous settlement (A-demand-041).
- Metros: each governorate holding a metro anchor row is replaced by hexagons (A-demand-001)
  clipped to it; the census total is split by WorldPop 2020 grid shares (only shares are used);
  hexes below a minimum grid population merge into the nearest kept hex (A-demand-042); the point
  is the population-weighted pixel centroid (A-demand-043).
- Jobs proxy: region formal jobs (S-r3-cal-050) x zone population share of the region
  (A-demand-003); economic nodes counted per zone by role (A-demand-044).

Every zone keeps `parent_gov` (G-id) and `share_in_gov`, so population scenarios projected on the
governorate base (demand.population.project) split to sub-zones with fixed shares.

uv run python -m demand.zones build --seed 1 --out runs/zones/
writes cities/ksa/zones/zones.geojson (polygons), runs/zones/zones.parquet and points.geojson
(one point per zone, for network.skims) and meta.json.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rasterio.mask
import typer
import yaml
from pyproj import Transformer
from shapely.geometry import Point, Polygon, mapping

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from demand import population as popmod

GOVS = Path("cities/ksa/zones/governorates.geojson")
GOV_POINTS = Path("cities/ksa/zones/governorate_points.geojson")
REGISTER = Path("cities/ksa/candidates.parquet")
PILOT = Path("cities/ksa/candidates-pilot.parquet")
WEIGHTS = Path("cities/ksa/assumptions/screening_weights.yaml")
PARAMS = Path("cities/ksa/assumptions/demand_zones.yaml")
JOBS = Path("cities/ksa/assumptions/demand_jobs.yaml")
NODES = Path("cities/ksa/zones/economic_nodes.parquet")
GRID = Path("data/ksa/grids/sau_ppp_2020_UNadj_constrained.tif")
OUT_GEOJSON = Path("cities/ksa/zones/zones.geojson")
ROLES = (
    "airport",
    "port",
    "industrial_city",
    "university",
    "hajj_umrah",
    "giga_project",
    "heritage",
    "tourism",
    "mining",
    "energy",
    "border_crossing",
)

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Demand zones."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def load_params(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / PARAMS).read_text(encoding="utf-8"))


def metro_governorates(root: Path = REPO_ROOT) -> pd.DataFrame:
    """zone_id, metro, tier for every governorate that holds a metro anchor row (A-screen-013)."""
    from screening.funnel import resolve_anchor

    reg = pd.read_parquet(root / REGISTER)
    pilot = pd.read_parquet(root / PILOT) if (root / PILOT).exists() else None
    cfg = yaml.safe_load((root / WEIGHTS).read_text(encoding="utf-8"))
    rows = []
    by = reg.set_index("row_key")
    for m in cfg["metros"]:
        for a in m["anchors"]:
            r = by.loc[resolve_anchor(reg, a, pilot)]
            rows.append({"metro": m["name"], "tier": int(m["tier"]), "lat": r.lat, "lon": r.lon})
    pts = pd.DataFrame(rows)
    g = gpd.read_file(root / GOVS)[["zone_id", "geometry"]]
    p = gpd.GeoDataFrame(pts, geometry=gpd.points_from_xy(pts.lon, pts.lat), crs=4326)
    j = gpd.sjoin(p, g, how="left", predicate="within")
    if j.zone_id.isna().any():
        raise ValueError("a metro anchor lies outside every governorate polygon")
    return (
        j.groupby("zone_id")
        .agg(metro=("metro", "first"), tier=("tier", "min"))
        .reset_index()
        .sort_values("zone_id")
    )


def hex_grid(poly_utm: Polygon, flat_km: float) -> list[Polygon]:
    """Pointy-top hexagons (flat-to-flat = flat_km) covering a polygon in metric coordinates."""
    r = flat_km * 1000 / math.sqrt(3)  # circumradius
    w, h = flat_km * 1000, 1.5 * r
    minx, miny, maxx, maxy = poly_utm.bounds
    cells = []
    row = 0
    y = miny - h
    while y <= maxy + h:
        x0 = minx - w + (w / 2 if row % 2 else 0.0)
        x = x0
        while x <= maxx + w:
            ang = [math.radians(30 + 60 * k) for k in range(6)]
            hx = Polygon([(x + r * math.cos(a), y + r * math.sin(a)) for a in ang])
            if hx.intersects(poly_utm):
                cells.append(hx.intersection(poly_utm))
            x += w
        y += h
        row += 1
    return [c for c in cells if not c.is_empty and c.area > 0]


def grid_in(
    geom_wgs84: Any, src: rasterio.DatasetReader
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(lon, lat, value) of the grid pixels inside a WGS84 geometry (no-data and <= 0 dropped)."""
    arr, tr = rasterio.mask.mask(src, [mapping(geom_wgs84)], crop=True, filled=True)
    a = arr[0].astype("float64")
    nod = src.nodata
    ok = np.isfinite(a) & (a > 0)
    if nod is not None:
        ok &= a != nod
    rows, cols = np.nonzero(ok)
    xs, ys = rasterio.transform.xy(tr, rows, cols, offset="center")
    return np.asarray(xs), np.asarray(ys), a[rows, cols]


def split_governorate(
    gov_geom: Any, gid: str, total: int, src: rasterio.DatasetReader, flat_km: float, min_pop: float
) -> gpd.GeoDataFrame:
    """Hex sub-zones of one governorate with census population split by grid shares."""
    g = gpd.GeoSeries([gov_geom], crs=4326)
    utm = g.estimate_utm_crs()
    poly = g.to_crs(utm).iloc[0]
    cells = hex_grid(poly, flat_km)
    lon, lat, val = grid_in(gov_geom, src)
    to_utm = Transformer.from_crs(4326, utm, always_xy=True)
    px, py = to_utm.transform(lon, lat)
    cg = gpd.GeoDataFrame({"cell": range(len(cells))}, geometry=cells, crs=utm)
    pts = gpd.GeoDataFrame(
        {"v": val, "lon": lon, "lat": lat}, geometry=gpd.points_from_xy(px, py), crs=utm
    )
    j = gpd.sjoin(pts, cg, how="inner", predicate="within")
    agg = j.groupby("cell").agg(v=("v", "sum"))
    cg["grid_pop"] = cg["cell"].map(agg["v"]).fillna(0.0)
    keep = cg[cg.grid_pop >= min_pop].copy()
    if keep.empty:  # tiny governorate: one zone
        keep = cg.nlargest(1, "grid_pop").copy()
    drop = cg[~cg.cell.isin(keep.cell)]
    # merge dropped cells into the nearest kept cell (centroid distance), grid population included
    kc = np.c_[keep.geometry.centroid.x, keep.geometry.centroid.y]
    target = {}
    for c, geom in zip(drop.cell, drop.geometry, strict=True):
        d = np.hypot(kc[:, 0] - geom.centroid.x, kc[:, 1] - geom.centroid.y)
        target[c] = int(keep.cell.iloc[int(np.argmin(d))])
    cg["owner"] = cg.cell.map(lambda c: target.get(c, c))
    j["owner"] = j["cell"].map(lambda c: target.get(c, c))
    merged = cg.dissolve(by="owner", aggfunc={"grid_pop": "sum"}).reset_index()
    # weighted pixel centroid per owner (WGS84)
    w = j.groupby("owner").apply(
        lambda d: pd.Series(
            {"lon": np.average(d.lon, weights=d.v), "lat": np.average(d.lat, weights=d.v)}
        ),
        include_groups=False,
    )
    merged = merged.join(w, on="owner")
    merged = merged.sort_values(["grid_pop", "owner"], ascending=[False, True]).reset_index(
        drop=True
    )
    merged["zone_id"] = [f"{gid}-H{i + 1:03d}" for i in range(len(merged))]
    shares = merged.grid_pop / merged.grid_pop.sum()
    merged["share_in_gov"] = shares.round(10)
    merged["population_2022"] = popmod.largest_remainder(shares, int(total)).to_numpy()
    out = merged.to_crs(4326)
    # fall back to the polygon's representative point if a cell had no pixel
    rp = out.geometry.representative_point()
    out["point_lon"] = out["lon"].fillna(rp.x)
    out["point_lat"] = out["lat"].fillna(rp.y)
    return out.drop(columns=["owner", "lon", "lat", "cell"], errors="ignore")


def jobs_proxy(z: pd.DataFrame, root: Path = REPO_ROOT) -> pd.Series:
    """A-demand-003: region formal jobs x zone population / region population."""
    j = yaml.safe_load((root / JOBS).read_text(encoding="utf-8"))
    reg_jobs = {k: float(v["jobs_formal"]) for k, v in j["regions"].items()}
    reg_pop = z.groupby("region")["population_2022"].sum()
    return z.apply(
        lambda r: reg_jobs[r.region] * r.population_2022 / reg_pop[r.region], axis=1
    ).round(1)


def attach_nodes(z: gpd.GeoDataFrame, root: Path = REPO_ROOT) -> pd.DataFrame:
    nodes = pd.read_parquet(root / NODES)
    nodes = nodes[nodes.located.fillna(False).astype(bool)]
    p = gpd.GeoDataFrame(nodes, geometry=gpd.points_from_xy(nodes.lon, nodes.lat), crs=4326)
    j = gpd.sjoin(p, z[["zone_id", "geometry"]], how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")]
    miss = j.zone_id.isna()
    unattached = sorted(j.loc[miss, "node_id"])
    if miss.any():  # offshore or border points outside the simplified polygons: nearest zone
        utm = z.estimate_utm_crs()
        zz = z[["zone_id", "geometry"]].to_crs(utm)
        near = gpd.sjoin_nearest(p.loc[miss[miss].index].to_crs(utm), zz, how="left")
        near = near[~near.index.duplicated(keep="first")]
        j.loc[miss, "zone_id"] = near["zone_id_right" if "zone_id_right" in near else "zone_id"]
    counts = pd.crosstab(j.zone_id, j.role).reindex(columns=list(ROLES), fill_value=0)
    ids = j.groupby("zone_id")["node_id"].agg(lambda s: ";".join(sorted(s)))
    out = pd.DataFrame(index=z.zone_id)
    for r in ROLES:
        out[f"n_{r}"] = counts[r].reindex(out.index).fillna(0).astype(int) if r in counts else 0
    out["economic_nodes"] = ids.reindex(out.index).fillna("")
    out.attrs["unattached"] = unattached
    return out.reset_index()


def build_zones(root: Path = REPO_ROOT) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    params = load_params(root)
    flat = float(_v(params["metro_subzones"]["hex_flat_to_flat_km"]))
    min_pop = float(_v(params["metro_subzones"]["min_hex_population"]))
    govs = gpd.read_file(root / GOVS)[["zone_id", "name_en", "name_ar", "region", "geometry"]]
    base = popmod.base_by_zone()
    if set(base.index) != set(govs.zone_id):
        raise ValueError("census base zones and governorate polygons differ")
    gpts = gpd.read_file(root / GOV_POINTS)[["zone_id", "geometry"]]
    gpts = gpts.set_index("zone_id").geometry
    metros = metro_governorates(root).set_index("zone_id")
    # R6 (CP6 P5b, A-r6-010): non-metro governorates split with the same hexagon method so that
    # station additions in them get their own catchment (Al-Ahsa G033, Al Jubayl G034)
    sp = params.get("split_governorates") or {}
    split_ids = set(_v(sp.get("zones", {"value": []})) or [])
    sflat = float(_v(sp["hex_flat_to_flat_km"])) if split_ids else flat
    parts = []
    with rasterio.open(root / GRID) as src:
        for g in govs.itertuples(index=False):
            tot = int(base[g.zone_id])
            if g.zone_id in metros.index:
                h = split_governorate(g.geometry, g.zone_id, tot, src, flat, min_pop)
                h["kind"] = "metro_hex"
                h["metro"] = metros.at[g.zone_id, "metro"]
                h["metro_tier"] = int(metros.at[g.zone_id, "tier"])
            elif g.zone_id in split_ids:
                h = split_governorate(g.geometry, g.zone_id, tot, src, sflat, min_pop)
                h["kind"] = "split_hex"
                h["metro"] = None
                h["metro_tier"] = pd.NA
            else:
                pt = gpts.get(g.zone_id, g.geometry.representative_point())
                h = gpd.GeoDataFrame(
                    {
                        "zone_id": [g.zone_id],
                        "share_in_gov": [1.0],
                        "population_2022": [tot],
                        "grid_pop": [np.nan],
                        "point_lon": [pt.x],
                        "point_lat": [pt.y],
                        "kind": ["governorate"],
                        "metro": [None],
                        "metro_tier": [pd.NA],
                    },
                    geometry=[g.geometry],
                    crs=4326,
                )
            h["parent_gov"] = g.zone_id
            h["gov_name_en"] = g.name_en
            h["gov_name_ar"] = g.name_ar
            h["region"] = g.region
            parts.append(h)
    z = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=4326)
    z["population_2022"] = z["population_2022"].astype("int64")
    z["pop_source"] = "S-cp2-gastat-007"
    z["pop_method"] = np.where(
        z.kind.isin(["metro_hex", "split_hex"]),
        "census governorate total x WorldPop 2020 share (A-demand-001)",
        "census",
    )
    z["jobs_proxy"] = jobs_proxy(z, root)
    z["jobs_source"] = "S-r3-cal-050 (region) x population share (A-demand-003)"
    nodes = attach_nodes(z, root)
    z = z.merge(nodes, on="zone_id", how="left")
    z["label"] = LABEL
    z = z.sort_values("zone_id").reset_index(drop=True)
    checks = {
        "zones": int(len(z)),
        "governorate_zones": int((z.kind == "governorate").sum()),
        "metro_hex_zones": int((z.kind == "metro_hex").sum()),
        "split_hex_zones": int((z.kind == "split_hex").sum()),
        "split_governorates": sorted(split_ids),
        "metro_governorates": metros.reset_index().to_dict("records"),
        "population_total": int(z.population_2022.sum()),
        "population_census_total": int(base.sum()),
        "jobs_total": round(float(z.jobs_proxy.sum()), 1),
        "economic_nodes_attached": int(z[[f"n_{r}" for r in ROLES]].to_numpy().sum()),
        "economic_nodes_outside_polygons_nearest_zone": nodes.attrs.get("unattached", []),
        "hex_flat_to_flat_km": flat,
        "min_hex_population": min_pop,
    }
    if checks["population_total"] != checks["population_census_total"]:
        raise AssertionError("zone populations do not sum to the census total")
    return z, checks


@app.command("build")
def build_cmd(
    out: Path = typer.Option(Path("runs/zones")),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Build the zone system; write zones.geojson (tracked) and the run files."""
    z, checks = build_zones(root)
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    geo = z.copy()
    utm = geo.estimate_utm_crs()
    geo["geometry"] = geo.to_crs(utm).geometry.simplify(200).to_crs(4326)  # ~200 m, as A-r1a-003
    geo["area_km2"] = (z.to_crs(utm).area / 1e6).round(2)
    geo.to_file(root / OUT_GEOJSON, driver="GeoJSON")
    pd.DataFrame(geo.drop(columns="geometry")).to_parquet(run / "zones.parquet", index=False)
    pts = gpd.GeoDataFrame(
        geo[["zone_id", "parent_gov", "kind"]],
        geometry=[Point(x, y) for x, y in zip(geo.point_lon, geo.point_lat, strict=True)],
        crs=4326,
    )
    pts.to_file(run / "points.geojson", driver="GeoJSON")
    (run / "summary.json").write_text(json.dumps(checks, indent=1, default=str) + "\n")
    write_meta(
        run,
        seed,
        {"params": load_params(root), "grid": str(GRID)},
        extra={
            "summary": checks,
            "assumptions": ["A-demand-001", "A-demand-003", "A-demand-041", "A-demand-042"]
            + ["A-demand-043", "A-demand-044", "A-pop-007"],
            "label": LABEL,
        },
    )
    typer.echo(json.dumps({k: v for k, v in checks.items() if k != "metro_governorates"}, indent=1))


if __name__ == "__main__":
    app()
