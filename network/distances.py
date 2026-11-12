"""Distance fields for every settlement (R1a task 5): great-circle and road km/min to the nearest
existing intercity station, existing line, committed line and its planned station, Riyadh Metro
station and metro city (A-screen-013 tiers). Writes the columns into
cities/ksa/zones/settlements.parquet and a run record under runs/distances/<run>/.

Methods (one `*_method` column per field):
- great-circle: haversine km to the nearest target (station point, or a vertex of the line
  alignment densified to `densify_km`, A-r1a-007);
- road: OSRM /table (MLD, car profile, free flow, uncalibrated) over the K great-circle-nearest
  stations (network.access, K = A-r1a-027); road values NaN when unreachable, never 0.
Committed stations are UNLOCATED proxies (town centroids, rail.lines): their distances are
indicative and flagged by `committed_sites_unlocated`.

CLI:
  uv run python -m network.distances main --backend osrm \
      --osrm-dir data/ksa/osrm/gcc-states-latest --seed 1
  uv run python -m network.distances main --backend great_circle --seed 1     # no road fields
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import typer
import yaml
from shapely.geometry import shape

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta
from network.access import nearest_targets
from network.geo import KNearest

SETTLEMENTS = Path("cities/ksa/zones/settlements.parquet")
STATIONS = Path("cities/ksa/lines/stations.geojson")
GEOJSON = Path("cities/ksa/lines/geojson")
PARAMS = Path("network/distances_params.yaml")

app = typer.Typer(add_completion=False, help="Settlement distance fields.")


def load_params(root: Path) -> dict:
    return yaml.safe_load((root / PARAMS).read_text(encoding="utf-8"))


def station_table(root: Path) -> pd.DataFrame:
    fc = json.loads((root / STATIONS).read_text(encoding="utf-8"))
    rows = []
    for f in fc["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        rows.append({"id": p["station_uid"], "lat": lat, "lon": lon, **p})
    return pd.DataFrame(rows)


def densify(coords: list, step_km: float) -> list[tuple[float, float]]:
    """(lon, lat) vertices with extra points so no gap exceeds step_km (great-circle-ish)."""
    out = []
    for (x0, y0), (x1, y1) in zip(coords, coords[1:], strict=False):
        dkm = np.hypot((y1 - y0) * 111.32, (x1 - x0) * 111.32 * np.cos(np.radians(y0)))
        n = max(int(np.ceil(dkm / step_km)), 1)
        for t in np.arange(n) / n:
            out.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
    out.append(tuple(coords[-1]))
    return out


def line_vertices(root: Path, line_ids: list[str], step_km: float) -> pd.DataFrame:
    rows = []
    for lid in line_ids:
        fc = json.loads((root / GEOJSON / f"{lid}.geojson").read_text(encoding="utf-8"))
        geom = shape(fc["features"][0]["geometry"])
        parts = [geom] if geom.geom_type == "LineString" else list(geom.geoms)
        for part in parts:
            for lon, lat in densify(list(part.coords), step_km):
                rows.append({"id": lid, "lat": lat, "lon": lon})
    return pd.DataFrame(rows)


def gc_nearest(points: pd.DataFrame, targets: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    km, idx = KNearest(targets.lat.to_numpy(float), targets.lon.to_numpy(float)).query(
        points.lat.to_numpy(float), points.lon.to_numpy(float), k=1
    )
    return km[:, 0], targets.id.astype(str).to_numpy(object)[idx[:, 0]]


def metro_cities(settlements: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Metro reference points: OSM place=city nodes named in A-screen-013 (tier per city)."""
    rows = []
    for name, spec in params["metro_cities"]["value"].items():
        hit = settlements[settlements.osm_id == spec["osm_node"]]
        if hit.empty:
            raise ValueError(f"metro city {name}: OSM node {spec['osm_node']} not in settlements")
        r = hit.iloc[0]
        rows.append(
            {
                "id": f"{name} (tier {spec['tier']})",
                "lat": r.lat,
                "lon": r.lon,
                "tier": spec["tier"],
            }
        )
    return pd.DataFrame(rows)


def add_fields(
    df: pd.DataFrame,
    prefix: str,
    points: pd.DataFrame,
    targets: pd.DataFrame,
    backend: str,
    osrm_url: str | None,
) -> dict:
    t0 = time.time()
    res = nearest_targets(points, targets, backend=backend, osrm_url=osrm_url)
    df[f"dist_{prefix}_km"] = res.gc_km.round(2).to_numpy()
    df[f"nearest_{prefix}"] = res.gc_target_id.to_numpy()
    df[f"road_target_{prefix}"] = res.target_id.to_numpy() if backend != "great_circle" else None
    df[f"road_km_{prefix}"] = res.road_km.round(2).to_numpy()
    df[f"road_min_{prefix}"] = res.road_min.round(1).to_numpy()
    df[f"{prefix}_method"] = res.method.iloc[0]
    return {
        "targets": len(targets),
        "method": res.method.iloc[0],
        "road_reachable": int(res.road_reachable.sum()) if backend != "great_circle" else 0,
        "seconds": round(time.time() - t0, 1),
    }


@app.command()
def main(
    backend: str = typer.Option("osrm", help="osrm | great_circle"),
    osrm_dir: Path = typer.Option(Path("data/ksa/osrm/gcc-states-latest")),
    out_run: Path = typer.Option(Path("runs/distances/settlements")),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Compute the distance fields and write them into settlements.parquet."""
    params = load_params(root)
    step = params["densify_km"]["value"]
    df = pd.read_parquet(root / SETTLEMENTS)
    df = df[[c for c in df.columns if not c.startswith(("dist_", "nearest_", "road_"))]]
    df = df[[c for c in df.columns if not c.endswith("_method") or c in ("pop_method",)]]
    df = df.drop(columns=[c for c in ("committed_sites_unlocated",) if c in df], errors="ignore")
    pts = pd.DataFrame({"id": df.settlement_id, "lat": df.lat, "lon": df.lon})
    st = station_table(root)
    intercity = st[(st.layer == "existing") & st.line_id.isin(params["intercity_lines"]["value"])]
    committed = st[st.layer == "committed"]
    metro = st[st.line_id.str.startswith("riyadh-metro")]
    sets = {
        "existing": intercity,
        "committed": committed,
        "metro_station": metro,
        "metro_city": metro_cities(df, params),
    }
    summary: dict = {}
    url_ctx = None
    if backend == "osrm":
        from network import osrm as osrm_mod

        url_ctx = osrm_mod.server(root / osrm_dir, max_table=1000)
        url = url_ctx.__enter__()
    else:
        url = None
    try:
        for prefix, targets in sets.items():
            summary[prefix] = add_fields(df, prefix, pts, targets, backend, url)
    finally:
        if url_ctx is not None:
            url_ctx.__exit__(None, None, None)
    for prefix, ids in (
        ("existing_line", params["intercity_lines"]["value"]),
        ("existing_any_line", params["existing_all_lines"]["value"]),
        ("committed_line", list(committed.line_id.unique())),
    ):
        km, nid = gc_nearest(pts, line_vertices(root, ids, step))
        df[f"dist_{prefix}_km"] = np.round(km, 2)
        df[f"nearest_{prefix}"] = nid
        df[f"{prefix}_method"] = f"great_circle_haversine to alignment vertices every {step} km"
    df["nearest_metro_tier"] = (
        df.nearest_metro_city.str.extract(r"tier (\d)")[0].astype("Int64").to_numpy()
    )
    df["committed_sites_unlocated"] = True
    df.to_parquet(root / SETTLEMENTS, index=False)
    config = {"backend": backend, "params": params, "sets": {k: len(v) for k, v in sets.items()}}
    write_meta(root / out_run, seed, config, extra={"summary": summary, "rows": len(df)})
    typer.echo(json.dumps(summary, indent=1))


@app.command("register")
def register_cmd(
    inp: Path = typer.Option(Path("cities/ksa/candidates-pilot.parquet"), "--in"),
    out: Path = typer.Option(Path("cities/ksa/zones/candidates-pilot-r1a.parquet")),
    backend: str = typer.Option("osrm", help="osrm | great_circle"),
    osrm_dir: Path = typer.Option(Path("data/ksa/osrm/gcc-states-latest")),
    out_run: Path = typer.Option(Path("runs/distances/register")),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Recompute a region register's distance columns from cities/ksa/lines/stations.geojson
    (RegionRow fields), writing a NEW file so `screening.funnel long-list --in <out>` re-runs."""
    params = load_params(root)
    reg = pd.read_parquet(root / inp)
    pts = pd.DataFrame({"id": reg.index.astype(str), "lat": reg.lat, "lon": reg.lon})
    st = station_table(root)
    sets = {
        "existing": st[
            (st.layer == "existing") & st.line_id.isin(params["intercity_lines"]["value"])
        ],
        "committed": st[st.layer == "committed"],
        "metro": metro_cities(pd.read_parquet(root / SETTLEMENTS), params),
    }
    ctx = None
    url = None
    if backend == "osrm":
        from network import osrm as osrm_mod

        ctx = osrm_mod.server(root / osrm_dir, max_table=1000)
        url = ctx.__enter__()
    try:
        res = {k: nearest_targets(pts, t, backend=backend, osrm_url=url) for k, t in sets.items()}
    finally:
        if ctx is not None:
            ctx.__exit__(None, None, None)
    reg = reg.copy()
    for k in ("existing", "committed", "metro"):
        r = res[k]
        reg[f"dist_{k}_km"] = r.gc_km.round(2).to_numpy()
        reg[f"road_min_{k}"] = r.road_min.round(1).to_numpy()
    reg["nearest_existing"] = res["existing"].gc_target_id.to_numpy()
    reg["nearest_committed_station"] = res["committed"].gc_target_id.to_numpy()
    reg["nearest_committed"] = res["committed"].gc_target_id.str.split(":").str[0].to_numpy()
    reg["nearest_metro"] = res["metro"].gc_target_id.to_numpy()
    reg["nearest_metro_tier"] = (
        res["metro"].gc_target_id.str.extract(r"tier (\d)")[0].astype(int).to_numpy()
    )
    reg["dist_method"] = (
        "great_circle_haversine to cities/ksa/lines/stations.geojson (R1a); committed sites "
        "are unlocated proxies"
    )
    reg["road_min_method"] = res["existing"].method.iloc[0] + " (free flow, uncalibrated)"
    reg.to_parquet(root / out, index=False)
    write_meta(root / out_run, seed, {"in": str(inp), "backend": backend}, extra={"rows": len(reg)})
    typer.echo(f"{len(reg)} register rows -> {out}")


if __name__ == "__main__":
    app()
