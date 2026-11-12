"""Distance fields: nearest target (station or line vertex) per point (settlement).

uv run python -m network.access --points <points.parquet: id,lat,lon> \
    --targets <targets.parquet|.geojson: id,lat,lon[,layer]> --backend great_circle \
    --out <out.parquet>
uv run python -m network.access ... --backend osrm --osrm-dir data/ksa/osrm/gcc-states-latest
uv run python -m network.access ... --backend graph --pbf data/osm/jeddah.osm.pbf

Method per row (`method` column):
- `great_circle_haversine`: nearest target by great-circle km (cKDTree on 3-D unit vectors, exact).
  Road km/min are NaN. No detour factor is applied here; any factor is the caller's registered
  assumption.
- `osrm_table_mld_car`: the K great-circle-nearest targets (K = A-r1a-027, access_params.yaml) are
  routed with OSRM /table; the fastest by road time wins.
- `nx_dijkstra_<pbf-stem>`: same K candidates on the osmium+networkx road graph (network.roadgraph).
If no candidate is reachable by road, the great-circle nearest is kept, road values are NaN and
`road_reachable` is False (never 0).

Output columns: id, gc_target_id, gc_km, target_id, target_layer, target_gc_km, road_km, road_min,
road_reachable, point_snap_km, target_snap_km, k, method. Free-flow road times, uncalibrated.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import typer
import yaml
from scipy.sparse.csgraph import dijkstra

from common.runmeta import seed_option, write_meta
from network import osrm as osrm_mod
from network.geo import KNearest
from network.roadgraph import RoadGraph, build_graph, load_speed_config
from network.skims import _lookup, path_km, rel, snap_to_graph

PARAMS_YAML = Path(__file__).with_name("access_params.yaml")
METHOD_GC = "great_circle_haversine"
METHOD_OSRM = "osrm_table_mld_car"
app = typer.Typer(add_completion=False, help="Nearest-target distance fields.")


def default_k(path: Path = PARAMS_YAML) -> int:
    return int(yaml.safe_load(path.read_text(encoding="utf-8"))["k_candidates"]["value"])


def read_points(path: Path) -> pd.DataFrame:
    """id, lat, lon (+ any extra columns) from Parquet, CSV or (Geo)JSON points."""
    path = Path(path)
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
    else:
        gdf = gpd.read_file(path)
        if "lat" not in gdf.columns or "lon" not in gdf.columns:
            pts = gdf.geometry.representative_point()
            gdf["lon"], gdf["lat"] = pts.x, pts.y
        df = pd.DataFrame(gdf.drop(columns="geometry"))
    missing = {"id", "lat", "lon"} - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    df["id"] = df["id"].astype(str)
    return df.reset_index(drop=True)


def _road_osrm(url: str, plon, plat, tlon, tlat, cand: np.ndarray, batch: int):
    """Durations/distances point x its own candidates (shape n x k), batched by points."""
    n, k = cand.shape
    dur, dist = np.full((n, k), np.nan), np.full((n, k), np.nan)
    psnap, tsnap = np.full(n, np.nan), np.full((n, k), np.nan)
    for i0 in range(0, n, batch):
        rows = np.arange(i0, min(n, i0 + batch))
        uniq, inv = np.unique(cand[rows], return_inverse=True)
        res = osrm_mod.table(
            url,
            np.column_stack([plon[rows], plat[rows]]),
            np.column_stack([tlon[uniq], tlat[uniq]]),
            batch=batch,
        )
        inv = inv.reshape(len(rows), k)
        r = np.arange(len(rows))[:, None]
        dur[rows] = res["duration_s"][r, inv]
        dist[rows] = res["distance_m"][r, inv]
        psnap[rows] = res["src_snap_m"]
        tsnap[rows] = res["dst_snap_m"][inv]
    return dur, dist, psnap / 1000.0, tsnap / 1000.0


def _road_graph(g: RoadGraph, plat, plon, tlat, tlon, cand: np.ndarray):
    """Same as _road_osrm on the NetworkX-equivalent graph: reverse Dijkstra from each target."""
    n, k = cand.shape
    pnode, psnap = snap_to_graph(g, plat, plon)
    used = np.unique(cand)
    tnode_u, tsnap_u = snap_to_graph(g, tlat[used], tlon[used])
    tpos = {int(t): i for i, t in enumerate(used)}
    t, m = g.csr()
    t_rev, look_rev = t.T.tocsr(), _lookup(m.T.tocsr())
    dur, dist = np.full((n, k), np.nan), np.full((n, k), np.nan)
    tsnap = np.full((n, k), np.nan)
    for ti, tn in zip(used, tnode_u, strict=True):
        d, pred = dijkstra(t_rev, directed=True, indices=int(tn), return_predecessors=True)
        rows, cols = np.nonzero(cand == ti)
        sec = d[pnode[rows]]
        met = path_km(pred, int(tn), pnode[rows], look_rev)
        sec[~np.isfinite(sec)] = np.nan
        met[np.isnan(sec)] = np.nan
        dur[rows, cols], dist[rows, cols] = sec, met
        tsnap[rows, cols] = tsnap_u[tpos[int(ti)]]
    return dur, dist, psnap, tsnap


def nearest_targets(
    points_df: pd.DataFrame,
    targets_df: pd.DataFrame,
    backend: str = "great_circle",
    k: int | None = None,
    osrm_dir: Path | None = None,
    osrm_url: str | None = None,
    graph: RoadGraph | None = None,
    pbf: Path | None = None,
    batch: int = 100,
) -> pd.DataFrame:
    """Nearest target per point. `backend`: great_circle | osrm | graph (see module doc).

    For `osrm`, pass a running server `osrm_url` or a prepared `osrm_dir` (a server is started
    and stopped). For `graph`, pass a `RoadGraph` or a `pbf` to build one.
    """
    k = k or default_k()
    p, tg = points_df.reset_index(drop=True), targets_df.reset_index(drop=True)
    plat, plon = p["lat"].to_numpy(float), p["lon"].to_numpy(float)
    tlat, tlon = tg["lat"].to_numpy(float), tg["lon"].to_numpy(float)
    tid = tg["id"].astype(str).to_numpy(dtype=object)
    tlayer = (tg["layer"] if "layer" in tg else pd.Series([None] * len(tg))).to_numpy(object)
    gc_km, cand = KNearest(tlat, tlon).query(plat, plon, k=k)
    kk = cand.shape[1]
    out = pd.DataFrame(
        {
            "id": p["id"].astype(str).to_numpy(),
            "gc_target_id": tid[cand[:, 0]],
            "gc_km": gc_km[:, 0],
        }
    )
    if backend == "great_circle":
        choice = np.zeros(len(p), int)
        dur = dist = np.full((len(p), kk), np.nan)
        psnap, tsnap = np.full(len(p), np.nan), np.full((len(p), kk), np.nan)
        method = METHOD_GC
    elif backend == "osrm":
        if osrm_url:
            dur, dist, psnap, tsnap = _road_osrm(osrm_url, plon, plat, tlon, tlat, cand, batch)
        else:
            if osrm_dir is None:
                raise ValueError("backend osrm needs osrm_url or osrm_dir")
            with osrm_mod.server(Path(osrm_dir), max_table=2 * batch + kk) as url:
                dur, dist, psnap, tsnap = _road_osrm(url, plon, plat, tlon, tlat, cand, batch)
        method = METHOD_OSRM
    elif backend == "graph":
        if graph is None:
            if pbf is None:
                raise ValueError("backend graph needs graph or pbf")
            graph = build_graph(Path(pbf), load_speed_config())
        dur, dist, psnap, tsnap = _road_graph(graph, plat, plon, tlat, tlon, cand)
        method = "nx_dijkstra_" + osrm_mod.pbf_stem(Path(graph.source or pbf or "graph"))
    else:
        raise ValueError("backend must be great_circle, osrm or graph")
    if backend != "great_circle":
        safe = np.where(np.isfinite(dur), dur, np.inf)
        choice = safe.argmin(axis=1)
        none = ~np.isfinite(safe).any(axis=1)
        choice[none] = 0
    r = np.arange(len(p))
    chosen = cand[r, choice]
    out["target_id"] = tid[chosen]
    out["target_layer"] = tlayer[chosen]
    out["target_gc_km"] = gc_km[r, choice]
    out["road_km"] = dist[r, choice] / 1000.0
    out["road_min"] = dur[r, choice] / 60.0
    out["road_reachable"] = np.isfinite(out["road_min"].to_numpy())
    out["point_snap_km"] = psnap
    out["target_snap_km"] = tsnap[r, choice]
    out["k"] = kk
    out["method"] = method
    return out


@app.command()
def main(
    points: Path = typer.Option(..., exists=True, help="Parquet/CSV/GeoJSON with id, lat, lon"),
    targets: Path = typer.Option(..., exists=True, help="Parquet/GeoJSON with id, lat, lon, layer"),
    out: Path = typer.Option(..., help="output Parquet"),
    backend: str = typer.Option("great_circle", help="great_circle | osrm | graph"),
    osrm_dir: Path = typer.Option(None, help="prepared OSRM dir (data/ksa/osrm/<stem>)"),
    pbf: Path = typer.Option(None, help="PBF for backend graph"),
    k: int = typer.Option(0, help="candidates routed by road (0 = A-r1a-027 default)"),
    batch: int = typer.Option(100, help="OSRM /table batch size"),
    seed: int = seed_option(),
) -> None:
    """Nearest target per point; writes <out> and <out-dir>/<out-stem>.meta/meta.json."""
    t0 = time.monotonic()
    p, tg = read_points(points), read_points(targets)
    res = nearest_targets(p, tg, backend, k or None, osrm_dir=osrm_dir, pbf=pbf, batch=batch)
    out.parent.mkdir(parents=True, exist_ok=True)
    res.to_parquet(out, index=False)
    extra: dict[str, Any] = {
        "points": rel(points),
        "targets": rel(targets),
        "backend": backend,
        "method": res["method"].iloc[0] if len(res) else None,
        "n_points": len(p),
        "n_targets": len(tg),
        "k": int(res["k"].iloc[0]) if len(res) else None,
        "n_road_unreachable": int((~res["road_reachable"]).sum())
        if backend != "great_circle"
        else None,
        "assumptions": ["A-r1a-027"] if backend != "great_circle" else [],
        "runtime_s": round(time.monotonic() - t0, 2),
    }
    if backend == "osrm":
        extra |= {"osrm_dir": rel(osrm_dir), "osrm_version": osrm_mod.osrm_version()}
    if backend == "graph":
        extra["pbf"] = rel(pbf)
    cfg = {"backend": backend, "points": extra["points"], "targets": extra["targets"], "k": k}
    write_meta(out.parent / f"{out.stem}.meta", seed, cfg, extra)
    typer.echo(f"{extra['method']}: {len(p)} points x {len(tg)} targets -> {out}")


if __name__ == "__main__":
    app()
