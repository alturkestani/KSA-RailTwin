"""Zone-to-zone level of service per mode for the national demand run (W8, R3).

`skims`: OSRM /table (national MLD files, car profile, free flow) for zone x zone, zone x station
and zone x airport, from the zone points of demand.zones. `attributes()`: vectorised MNL input
columns (modechoice.mnl conventions) for every admissible OD pair and one scenario's line set:
- car: road minutes (+ terminal), fuel cost per vehicle (mode_choice_r3.yaml car block);
- rail: per line, the nearest station by road time within A-demand-045; IVT = km-post span / line
  speed (A-demand-047), fare per km (A-demand-048), headway, on-time; no transfers (R4);
- air: nearest airport within A-demand-050; route if listed or hub-to-spoke (A-demand-051);
  block time and fare by the mode_choice_r3.yaml formulas; processing time per side;
- bus: mode_choice_r3.yaml bus block.

uv run python -m demand.supply skims --seed 1 --out runs/skims/r3-zones/

Free-flow road times; no rail or air timetables beyond the published pairs. Label: synthetic demand,
uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml
from pyproj import Geod

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from modechoice.coefficients import load_r3, r3_value

SUPPLY = Path("cities/ksa/assumptions/demand_supply.yaml")
STATIONS = Path("cities/ksa/lines/stations.geojson")
NODES = Path("cities/ksa/zones/economic_nodes.parquet")
ZONE_POINTS = Path("runs/zones/points.geojson")
OSRM_DIR = Path("data/ksa/osrm/gcc-states-latest")
_GEOD = Geod(ellps="WGS84")

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Level of service for the demand model."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def load_supply(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / SUPPLY).read_text(encoding="utf-8"))


def zone_points(root: Path = REPO_ROOT, path: Path = ZONE_POINTS) -> pd.DataFrame:
    g = json.loads((root / path).read_text(encoding="utf-8"))
    rows = [
        {
            "zone_id": f["properties"]["zone_id"],
            "lon": f["geometry"]["coordinates"][0],
            "lat": f["geometry"]["coordinates"][1],
        }
        for f in g["features"]
    ]
    return pd.DataFrame(rows).sort_values("zone_id").reset_index(drop=True)


def stations(root: Path = REPO_ROOT, lines: list[str] | None = None) -> pd.DataFrame:
    g = json.loads((root / STATIONS).read_text(encoding="utf-8"))
    rows = []
    for f in g["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"][:2]
        rows.append(
            {
                "station_uid": p["station_uid"],
                "line_id": p["line_id"],
                "km_post": float(p["km_post"]),
                "lon": lon,
                "lat": lat,
            }
        )
    df = pd.DataFrame(rows)
    if lines is not None:
        df = df[df.line_id.isin(lines)]
    return df.sort_values(["line_id", "km_post"]).reset_index(drop=True)


def airports(root: Path = REPO_ROOT) -> pd.DataFrame:
    e = pd.read_parquet(root / NODES)
    a = e[(e.role == "airport") & e.located.fillna(False).astype(bool)].copy()
    a["iata"] = a.subtype.map(lambda s: re.search(r"IATA ([A-Z]{3})", s).group(1))
    return a[["node_id", "iata", "lon", "lat"]].sort_values("iata").reset_index(drop=True)


def all_lines(sup: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for ls in sup["rail"]["lines_by_scenario"].values():
        out += [x for x in ls if x not in out]
    return out


# --------------------------------------------------------------------------- skims
def run_skims(root: Path, osrm_dir: Path, out: Path) -> dict[str, Any]:
    from network import osrm as osrm_mod

    sup = load_supply(root)
    z = zone_points(root)
    st = stations(root, all_lines(sup))
    ap = airports(root)
    zl = z[["lon", "lat"]].to_numpy()
    t0 = time.time()
    with osrm_mod.server(root / osrm_dir, max_table=1000) as url:
        zz = osrm_mod.table(url, zl, zl, batch=100)
        zs = osrm_mod.table(url, zl, st[["lon", "lat"]].to_numpy(), batch=100)
        za = osrm_mod.table(url, zl, ap[["lon", "lat"]].to_numpy(), batch=100)
        sz = osrm_mod.table(url, st[["lon", "lat"]].to_numpy(), zl, batch=100)
        az = osrm_mod.table(url, ap[["lon", "lat"]].to_numpy(), zl, batch=100)
    secs = round(time.time() - t0, 1)
    ids = z.zone_id.to_numpy()
    n = len(ids)
    road = pd.DataFrame(
        {
            "o": np.repeat(ids, n),
            "d": np.tile(ids, n),
            "km": (zz["distance_m"] / 1000).ravel().round(3),
            "min": (zz["duration_s"] / 60).ravel().round(2),
        }
    )
    road["intrazonal"] = road.o == road.d
    road.loc[road.intrazonal, ["km", "min"]] = 0.0

    def _long(mat_to, mat_from, targets, key):
        m = len(targets)
        return pd.DataFrame(
            {
                "zone_id": np.repeat(ids, m),
                key: np.tile(targets[key].to_numpy(), n),
                "to_min": (mat_to["duration_s"] / 60).ravel().round(2),
                "to_km": (mat_to["distance_m"] / 1000).ravel().round(3),
                "from_min": (mat_from["duration_s"].T / 60).ravel().round(2),
                "from_km": (mat_from["distance_m"].T / 1000).ravel().round(3),
            }
        )

    zst = _long(zs, sz, st, "station_uid").merge(
        st[["station_uid", "line_id", "km_post"]], on="station_uid"
    )
    zap = _long(za, az, ap, "iata")
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    road.to_parquet(run / "road.parquet", index=False)
    zst.to_parquet(run / "zone_station.parquet", index=False)
    zap.to_parquet(run / "zone_airport.parquet", index=False)
    return {
        "zones": n,
        "pairs": int(len(road)),
        "stations": int(len(st)),
        "airports": int(len(ap)),
        "unreachable_pairs": int(road["min"].isna().sum()),
        "zone_snap_m_max": float(np.nanmax(zz["src_snap_m"])),
        "seconds": secs,
        "osrm_version": osrm_mod.osrm_version(),
    }


@app.command("skims")
def skims_cmd(
    out: Path = typer.Option(Path("runs/skims/r3-zones")),
    osrm_dir: Path = typer.Option(OSRM_DIR),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Road skims zone x zone, zone <-> station and zone <-> airport (OSRM, free flow)."""
    summary = run_skims(root, osrm_dir, out)
    (root / out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    write_meta(
        root / out,
        seed,
        {"supply": load_supply(root), "zones": str(ZONE_POINTS)},
        extra={
            "summary": summary,
            "method": "osrm_table_mld_car (free flow, uncalibrated)",
            "label": LABEL,
        },
    )
    typer.echo(json.dumps(summary, indent=1))


# --------------------------------------------------------------------------- level of service
def _nearest(df: pd.DataFrame, key: str, max_min: float, minutes: str = "to_min") -> pd.DataFrame:
    """Per zone (and line, for stations) the nearest target by road minutes within max_min."""
    ok = df[df[minutes].notna() & (df[minutes] <= max_min)]
    idx = ok.groupby(key)[minutes].idxmin()
    return ok.loc[idx]


def _gc_km(lon1, lat1, lon2, lat2) -> np.ndarray:
    _, _, m = _GEOD.inv(lon1, lat1, lon2, lat2)
    return np.asarray(m) / 1000.0


def attributes(
    od: pd.DataFrame,
    skim_dir: Path,
    scenario: str,
    root: Path = REPO_ROOT,
    sup: dict[str, Any] | None = None,
    r3: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Per-mode MNL columns for an OD table with o, d (zone ids) and road_km, road_min."""
    sup = sup or load_supply(root)
    r3 = r3 or load_r3()
    out = od.copy()
    n = len(out)
    # car
    fuel = r3_value(r3, "car", "fuel_price_sar_per_l")
    econ = r3_value(r3, "car", "fuel_economy_km_per_l")
    parking = r3_value(r3, "car", "parking_toll_sar_per_trip")
    out["avail_car"] = np.isfinite(out.road_min.to_numpy())
    out["ivt_min_car"] = out.road_min + r3_value(r3, "car", "terminal_min")
    out["access_min_car"] = 0.0
    out["egress_min_car"] = 0.0
    out["headway_min_car"] = 0.0
    out["cost_sar_car"] = out.road_km * fuel / econ + parking
    # bus
    bus_ok = out.road_km.to_numpy() >= r3_value(r3, "bus", "availability_min_road_km")
    out["avail_bus"] = bus_ok
    out["ivt_min_bus"] = np.where(
        bus_ok, out.road_min * r3_value(r3, "bus", "ivt_factor_on_road"), np.nan
    )
    out["access_min_bus"] = float(r3["access_egress"]["bus"]["access_min"])
    out["egress_min_bus"] = float(r3["access_egress"]["bus"]["egress_min"])
    out["headway_min_bus"] = r3_value(r3, "bus", "headway_min")
    out["cost_sar_bus"] = np.where(
        bus_ok, out.road_km * r3_value(r3, "bus", "fare_per_km_sar"), np.nan
    )
    # rail: best line per pair
    zst = pd.read_parquet(root / skim_dir / "zone_station.parquet")
    lines = sup["rail"]["lines_by_scenario"][scenario]
    term = float(_v(sup["rail"]["terminal_min"]))
    max_acc = float(_v(sup["rail"]["station_access"]["max_road_min"]))
    best_gt = np.full(n, np.inf)
    cols = {k: np.full(n, np.nan) for k in ("ivt", "acc", "egr", "fare", "hw", "ontime", "km")}
    line_of = np.full(n, None, dtype=object)
    so = np.full(n, None, dtype=object)
    sd = np.full(n, None, dtype=object)
    for line in lines:
        lp = sup["rail"]["lines"][line]
        acc = _nearest(zst[zst.line_id == line], "zone_id", max_acc, "to_min").set_index("zone_id")
        egr = _nearest(zst[zst.line_id == line], "zone_id", max_acc, "from_min").set_index(
            "zone_id"
        )
        a = out.o.map(acc["station_uid"]).to_numpy()
        b = out.d.map(egr["station_uid"]).to_numpy()
        ka = out.o.map(acc["km_post"]).to_numpy(dtype=float)
        kb = out.d.map(egr["km_post"]).to_numpy(dtype=float)
        ta = out.o.map(acc["to_min"]).to_numpy(dtype=float) + term
        tb = out.d.map(egr["from_min"]).to_numpy(dtype=float) + term
        ok = pd.notna(a) & pd.notna(b) & (a != b)
        km = np.abs(ka - kb)
        ivt = km / float(_v(lp["speed_kmh"])) * 60.0
        gt = np.where(ok, ivt + ta + tb, np.inf)
        better = gt < best_gt
        best_gt = np.where(better, gt, best_gt)
        on = r3["on_time"]["rail_by_line"][line]["value"]
        for k, v in (
            ("ivt", ivt),
            ("acc", ta),
            ("egr", tb),
            ("km", km),
            ("fare", km * float(_v(lp["fare_per_km_sar"]))),
            ("hw", np.full(n, float(_v(lp["headway_min"])))),
            ("ontime", np.full(n, float(on))),
        ):
            cols[k] = np.where(better, v, cols[k])
        line_of = np.where(better, line, line_of)
        so = np.where(better, a, so)
        sd = np.where(better, b, sd)
    rail_ok = np.isfinite(best_gt)
    out["avail_rail"] = rail_ok
    out["ivt_min_rail"] = cols["ivt"]
    out["access_min_rail"] = cols["acc"]
    out["egress_min_rail"] = cols["egr"]
    out["headway_min_rail"] = cols["hw"]
    out["cost_sar_rail"] = cols["fare"]
    out["ontime_rail"] = cols["ontime"]
    out["rail_line"] = line_of
    out["rail_station_o"] = so
    out["rail_station_d"] = sd
    out["rail_km"] = cols["km"]
    # air
    zap = pd.read_parquet(root / skim_dir / "zone_airport.parquet")
    ap = airports(root).set_index("iata")
    max_air = float(_v(sup["air"]["airport_access"]["max_road_min"]))
    acc = _nearest(zap, "zone_id", max_air, "to_min").set_index("zone_id")
    egr = _nearest(zap, "zone_id", max_air, "from_min").set_index("zone_id")
    ia = out.o.map(acc["iata"]).to_numpy()
    ib = out.d.map(egr["iata"]).to_numpy()
    listed = {frozenset(r["pair"]): r for r in r3["air"]["routes"]}
    hubs = set(sup["air"]["network_rule"]["hubs"])
    hw_unlisted = float(_v(sup["air"]["headway_unlisted_min"]))
    route = np.zeros(n, dtype=bool)
    hw = np.full(n, np.nan)
    for i, (x, y) in enumerate(zip(ia, ib, strict=True)):
        if pd.isna(x) or pd.isna(y) or x == y:
            continue
        r = listed.get(frozenset((x, y)))
        if r is not None:
            route[i], hw[i] = True, float(r["headway_min"])
        elif x in hubs or y in hubs:
            route[i], hw[i] = True, hw_unlisted
    g = np.full(n, np.nan)
    if route.any():
        g[route] = _gc_km(
            ap.loc[ia[route], "lon"].to_numpy(),
            ap.loc[ia[route], "lat"].to_numpy(),
            ap.loc[ib[route], "lon"].to_numpy(),
            ap.loc[ib[route], "lat"].to_numpy(),
        )
    blk_fixed = r3_value(r3, "air", "block_time", "fixed_min")
    blk_speed = r3_value(r3, "air", "block_time", "speed_km_per_min")
    out["avail_air"] = route
    out["ivt_min_air"] = np.where(route, blk_fixed + g / blk_speed, np.nan)
    out["access_min_air"] = np.where(
        route,
        out.o.map(acc["to_min"]).to_numpy(dtype=float)
        + float(r3["access_egress"]["air"]["access_min"]),
        np.nan,
    )
    out["egress_min_air"] = np.where(
        route,
        out.d.map(egr["from_min"]).to_numpy(dtype=float)
        + float(r3["access_egress"]["air"]["egress_min"]),
        np.nan,
    )
    out["headway_min_air"] = hw
    out["cost_sar_air"] = np.where(
        route,
        r3_value(r3, "air", "fare", "fixed_sar") + r3_value(r3, "air", "fare", "per_km_sar") * g,
        np.nan,
    )
    out["ontime_air"] = np.where(route, r3_value(r3, "on_time", "air"), np.nan)
    out["air_o"] = np.where(route, ia, None)
    out["air_d"] = np.where(route, ib, None)
    out["air_gc_km"] = g
    out["scenario"] = scenario
    return out


if __name__ == "__main__":
    app()
