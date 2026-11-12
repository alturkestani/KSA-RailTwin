"""Zone-to-zone road skims (free-flow car time and distance) with pluggable backends.

uv run python -m network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf \
    --zones tests/fixtures/zones_jeddah_fixture.geojson --seed 1 --out runs/skims/demo-jeddah/
uv run python -m network.skims --backend osrm --pbf data/osm/jeddah.osm.pbf \
    --zones tests/fixtures/zones_jeddah_fixture.geojson --seed 1 --out runs/skims/demo-osrm/

Backends
- `osmnx`: OSMnx-equivalent drivable graph built with osmium + NetworkX (`network.roadgraph`;
  OSMnx itself is not installed, and meta.json records which path ran). Zone centroids snap to the
  nearest node of the largest strongly connected component; times are Dijkstra on free-flow
  seconds, km is the length of that fastest path.
- `osrm`: osrm-backend MLD files under `data/ksa/osrm/<pbf-stem>/` (prepared on demand), a local
  `osrm-routed`, the /table service in batches, then the server stops.

Outputs in `--out`: skims.parquet (long: o, d, km, min, reachable, intrazonal, o/d snap km and
flags), zones_snapped.parquet, meta.json. Unreachable pairs are NaN and counted, never 0. Snap
distances (centroid to network) are NOT added to km/min; they are reported per zone, and zones
snapped farther than `snap_flag_km` (A-r1a-026) are flagged. Intrazonal pairs (o == d) are 0 by
construction and marked `intrazonal`; they are not a measured intrazonal time.

Free-flow, uncongested road times; not calibrated against observed traffic.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import typer
from scipy.sparse.csgraph import dijkstra

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta
from network import osrm as osrm_mod
from network.geo import KNearest
from network.roadgraph import (
    SPEEDS_YAML,
    RoadGraph,
    build_graph,
    load_speed_config,
    osmium_version,
    osmnx_available,
)

DIJKSTRA_BATCH = 64  # sources per Dijkstra call (memory: batch x n_nodes float64)
app = typer.Typer(add_completion=False, help="Road skims between zone centroids.")


def rel(p: Path) -> str:
    p = Path(p)
    try:
        return os.path.relpath(p.resolve(), REPO_ROOT.resolve())
    except ValueError:  # pragma: no cover - other drive
        return p.name


def zone_centroids(zones_path: Path) -> pd.DataFrame:
    """zone_id, lat, lon of each zone centroid (computed in a local UTM CRS)."""
    gdf = gpd.read_file(zones_path)
    if "zone_id" not in gdf.columns:
        raise ValueError("zones GeoJSON needs a `zone_id` property")
    if gdf["zone_id"].duplicated().any():
        raise ValueError("duplicate zone_id")
    gdf = gdf.set_crs(4326) if gdf.crs is None else gdf.to_crs(4326)
    utm = gdf.estimate_utm_crs()
    c = gdf.to_crs(utm).geometry.centroid.to_crs(4326)
    return pd.DataFrame({"zone_id": gdf["zone_id"].astype(str), "lat": c.y, "lon": c.x})


# --------------------------------------------------------------------------- graph backend
def snap_to_graph(g: RoadGraph, lat, lon) -> tuple[np.ndarray, np.ndarray]:
    """(graph node index, snap km) to the nearest node of the largest SCC."""
    mask = g.largest_scc()
    cand = np.flatnonzero(mask)
    km, j = KNearest(g.lat[cand], g.lon[cand]).query(lat, lon, k=1)
    return cand[j[:, 0]], km[:, 0]


def path_km(pred: np.ndarray, src: int, dst: np.ndarray, m_lookup) -> np.ndarray:
    """Metres along the predecessor tree from `src` to each `dst` (NaN if unreachable)."""
    out = np.zeros(len(dst))
    cur = dst.astype(np.int64).copy()
    alive = cur != src
    bad = alive & (pred[cur] < 0)
    out[bad] = np.nan
    alive &= ~bad
    while alive.any():
        p = pred[cur[alive]]
        out[alive] += m_lookup(p, cur[alive])
        cur[alive] = p
        alive = (cur != src) & ~bad
    return out


def _lookup(csr_m):
    csr_m = csr_m.tocsr()

    def f(rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
        return np.asarray(csr_m[rows, cols]).ravel()

    return f


def graph_od(g: RoadGraph, src_nodes: np.ndarray, dst_nodes: np.ndarray) -> dict[str, np.ndarray]:
    """Fastest-path seconds and the metres of that path, sources x destinations."""
    t, m = g.csr()
    look = _lookup(m)
    ns, nd = len(src_nodes), len(dst_nodes)
    dur = np.full((ns, nd), np.nan)
    dist = np.full((ns, nd), np.nan)
    for i0 in range(0, ns, DIJKSTRA_BATCH):
        block = src_nodes[i0 : i0 + DIJKSTRA_BATCH]
        uniq, inv = np.unique(block, return_inverse=True)
        d, pred = dijkstra(t, directed=True, indices=uniq, return_predecessors=True)
        d, pred = np.atleast_2d(d), np.atleast_2d(pred)
        for r, s in enumerate(uniq):
            row_t = d[r, dst_nodes]
            row_m = path_km(pred[r], int(s), dst_nodes, look)
            row_t[~np.isfinite(row_t)] = np.nan
            row_m[np.isnan(row_t)] = np.nan
            for i in np.flatnonzero(inv == r):
                dur[i0 + i] = row_t
                dist[i0 + i] = row_m
    return {"duration_s": dur, "distance_m": dist}


# --------------------------------------------------------------------------- assemble
def long_skims(
    zone_ids: list[str],
    duration_s: np.ndarray,
    distance_m: np.ndarray,
    snap_km: np.ndarray,
    snap_flag_km: float,
) -> pd.DataFrame:
    n = len(zone_ids)
    oi, di = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    oi, di = oi.ravel(), di.ravel()
    ids = np.asarray(zone_ids, dtype=object)
    km = distance_m.ravel() / 1000.0
    mins = duration_s.ravel() / 60.0
    intra = oi == di
    km[intra], mins[intra] = 0.0, 0.0
    reach = np.isfinite(mins)
    return pd.DataFrame(
        {
            "o": ids[oi],
            "d": ids[di],
            "km": km,
            "min": mins,
            "reachable": reach,
            "intrazonal": intra,
            "o_snap_km": snap_km[oi],
            "d_snap_km": snap_km[di],
            "o_snap_flag": snap_km[oi] > snap_flag_km,
            "d_snap_flag": snap_km[di] > snap_flag_km,
        }
    )


def run_skims(
    backend: str,
    pbf: Path,
    zones: Path,
    out: Path,
    seed: int,
    speeds: Path = SPEEDS_YAML,
    osrm_root: Path = osrm_mod.OSRM_ROOT,
    batch: int = 100,
) -> dict[str, Any]:
    t0 = time.monotonic()
    cfg = load_speed_config(speeds)
    flag_km = float(cfg["snap_flag_km"]["value"])
    zc = zone_centroids(zones)
    extra: dict[str, Any] = {
        "backend": backend,
        "pbf": rel(pbf),
        "pbf_bytes": Path(pbf).resolve().stat().st_size,
        "pbf_sha256": osrm_mod.sha256_file(pbf),
        "zones": rel(zones),
        "n_zones": len(zc),
    }
    if backend == "osmnx":
        g = build_graph(pbf, cfg)
        node, snap_km = snap_to_graph(g, zc["lat"].to_numpy(), zc["lon"].to_numpy())
        od = graph_od(g, node, node)
        zc["snap_node_osmid"] = g.node_ids[node]
        zc["snap_lat"], zc["snap_lon"] = g.lat[node], g.lon[node]
        extra |= {
            "path": "osmium+networkx",
            "osmnx_importable": osmnx_available(),
            "osmium_version": osmium_version(),
            "n_nodes": g.n_nodes,
            "n_edges": g.n_edges,
            "n_nodes_largest_scc": int(g.largest_scc().sum()),
            "graph_stats": g.stats,
            "speeds_config": rel(speeds),
            "method": "nx_dijkstra_" + osrm_mod.pbf_stem(pbf),
            "assumptions": sorted(
                {v["assumption_id"] for v in cfg["default_speed_kmh"].values()}
                | {cfg["maxspeed_factor"]["assumption_id"], cfg["snap_flag_km"]["assumption_id"]}
            ),
        }
    elif backend == "osrm":
        odir = osrm_mod.osrm_dir_for(pbf, osrm_root)
        if not osrm_mod.is_prepared(odir):
            osrm_mod.prepare(pbf, osrm_root)
        prep = odir / "prep_stats.json"
        prep_sha = json.loads(prep.read_text())["pbf_sha256"] if prep.exists() else None
        if prep_sha and prep_sha != extra["pbf_sha256"]:
            raise RuntimeError(f"{odir} was prepared from a different PBF (SHA-256 mismatch)")
        lonlat = zc[["lon", "lat"]].to_numpy()
        with osrm_mod.server(odir, max_table=2 * batch) as url:
            res = osrm_mod.table(url, lonlat, lonlat, batch=batch)
        od = {"duration_s": res["duration_s"], "distance_m": res["distance_m"]}
        snap_km = res["src_snap_m"] / 1000.0
        extra |= {
            "path": "osrm",
            "osrm_version": osrm_mod.osrm_version(),
            "osrm_dir": rel(odir),
            "osrm_prep_pbf_sha256": prep_sha,
            "profile": "car.lua",
            "algorithm": "mld",
            "method": "osrm_table_mld_car",
            "assumptions": [cfg["snap_flag_km"]["assumption_id"]],
            "notes": "speeds from the OSRM car profile; OSRM durations include turn penalties",
        }
    else:
        raise typer.BadParameter("backend must be osmnx or osrm")
    zc["snap_km"] = snap_km
    zc["snap_flag"] = snap_km > flag_km
    sk = long_skims(list(zc["zone_id"]), od["duration_s"], od["distance_m"], snap_km, flag_km)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    sk.to_parquet(out / "skims.parquet", index=False)
    zc.to_parquet(out / "zones_snapped.parquet", index=False)
    inter = sk[~sk["intrazonal"]]
    extra |= {
        "n_pairs": int(len(sk)),
        "n_unreachable": int((~inter["reachable"]).sum()),
        "n_snap_flagged": int(zc["snap_flag"].sum()),
        "max_snap_km": float(np.nanmax(snap_km)) if len(zc) else None,
        "snap_flag_km": flag_km,
        "runtime_s": round(time.monotonic() - t0, 2),
    }
    config = {"backend": backend, "pbf": extra["pbf"], "zones": extra["zones"], "speeds": cfg}
    write_meta(out, seed, config, extra)
    return extra


@app.command()
def main(
    backend: str = typer.Option("osmnx", help="osmnx (osmium+networkx) or osrm"),
    pbf: Path = typer.Option(..., exists=True, help="OSM PBF (e.g. data/osm/jeddah.osm.pbf)"),
    zones: Path = typer.Option(..., exists=True, help="zones GeoJSON with zone_id"),
    out: Path = typer.Option(..., help="output dir under runs/"),
    seed: int = seed_option(),
    speeds: Path = typer.Option(SPEEDS_YAML, help="road speed / snap config YAML"),
    osrm_root: Path = typer.Option(osrm_mod.OSRM_ROOT, help="OSRM file root (data/ksa/osrm)"),
    batch: int = typer.Option(100, help="OSRM /table batch size (sources and destinations)"),
) -> None:
    """Compute zone-to-zone skims and write skims.parquet, zones_snapped.parquet, meta.json."""
    extra = run_skims(backend, pbf, zones, out, seed, speeds, osrm_root, batch)
    typer.echo(
        f"{extra['method']}: {extra['n_zones']} zones, {extra['n_pairs']} pairs, "
        f"{extra['n_unreachable']} unreachable, {extra['n_snap_flagged']} snaps > "
        f"{extra['snap_flag_km']} km (max {extra['max_snap_km']:.2f} km), "
        f"{extra['runtime_s']} s -> {out}"
    )


if __name__ == "__main__":
    app()
