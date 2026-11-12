"""R4 level of service for the demand model (CP4 R4 requirements 1 and 2).

`attributes(od, scenario, ...)` starts from R3's `demand.supply.attributes` (car and bus blocks,
the R3 air formulas) and replaces:
- rail: the rail graph with located stations and transfers (`access.railgraph.rail_los`);
- air: a route exists only on the sourced spoke-to-spoke pairs of access_air_routes.yaml
  (A-r4-air-001, replacing the hub rule A-demand-051); listed R3 routes keep their headway, others
  A-demand-052; block time and fares as R3 (A-mode-029/030);
- bus: available only between zones within the access cap of two different bus nodes
  (access_bus.yaml, A-r4-bus-001/002), access and egress include the road minutes to the node.
  Variants: `named_and_capitals` (default), `named_only`, `r3_all_pairs` (R3 rule A-mode-040).

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from common import REPO_ROOT
from demand import supply

AIR = Path("cities/ksa/assumptions/access_air_routes.yaml")
BUS = Path("cities/ksa/assumptions/access_bus.yaml")
BUS_VARIANTS = ("named_and_capitals", "named_only", "r3_all_pairs")


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def _yaml(p: Path, root: Path) -> dict[str, Any]:
    return yaml.safe_load((root / p).read_text(encoding="utf-8"))


def base_scenario(scenario: str) -> str:
    """S0 stays S0; S1 and every S2-S5 candidate run on the S1 line set (+ the candidate)."""
    return "S0" if scenario == "S0" else "S1"


def air_block(out: pd.DataFrame, skim_dir: Path, root: Path) -> pd.DataFrame:
    from modechoice.coefficients import load_r3, r3_value

    r3 = load_r3()
    sup = supply.load_supply(root)
    air = _yaml(AIR, root)
    routes = {frozenset(r["pair"]) for r in air["routes"]}
    listed = {frozenset(r["pair"]): float(r["headway_min"]) for r in r3["air"]["routes"]}
    hw_un = float(_v(air["headway_unlisted_min"]))
    zap = pd.read_parquet(root / skim_dir / "zone_airport.parquet")
    ap = supply.airports(root).set_index("iata")
    cap = float(_v(sup["air"]["airport_access"]["max_road_min"]))
    acc = supply._nearest(zap, "zone_id", cap, "to_min").set_index("zone_id")
    egr = supply._nearest(zap, "zone_id", cap, "from_min").set_index("zone_id")
    ia = out.o.map(acc["iata"]).to_numpy()
    ib = out.d.map(egr["iata"]).to_numpy()
    n = len(out)
    route = np.zeros(n, dtype=bool)
    hw = np.full(n, np.nan)
    for i, (x, y) in enumerate(zip(ia, ib, strict=True)):
        if pd.isna(x) or pd.isna(y) or x == y:
            continue
        key = frozenset((x, y))
        if key in routes:
            route[i] = True
            hw[i] = listed.get(key, hw_un)
    g = np.full(n, np.nan)
    if route.any():
        g[route] = supply._gc_km(
            ap.loc[ia[route], "lon"].to_numpy(),
            ap.loc[ia[route], "lat"].to_numpy(),
            ap.loc[ib[route], "lon"].to_numpy(),
            ap.loc[ib[route], "lat"].to_numpy(),
        )
    out = out.copy()
    out["avail_air"] = route
    out["ivt_min_air"] = np.where(
        route,
        r3_value(r3, "air", "block_time", "fixed_min")
        + g / r3_value(r3, "air", "block_time", "speed_km_per_min"),
        np.nan,
    )
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
    return out


def bus_nodes_zone_times(root: Path, variant: str) -> pd.DataFrame:
    """zone_id x node: road minutes zone -> node zone point (R3 road skim between zone points)."""
    import geopandas as gpd

    bus = _yaml(BUS, root)
    nodes = pd.DataFrame(bus["nodes"])
    if variant == "named_only":
        nodes = nodes[nodes.tier == "named"]
    zg = gpd.read_file(root / "cities/ksa/zones/zones.geojson")[["zone_id", "geometry"]]
    pts = gpd.GeoDataFrame(nodes, geometry=gpd.points_from_xy(nodes.lon, nodes.lat), crs=4326)
    j = gpd.sjoin(pts, zg, predicate="within")[["city", "zone_id"]].rename(
        columns={"zone_id": "node_zone"}
    )
    road = pd.read_parquet(root / "runs/skims/r3-zones" / "road.parquet")
    t = road.merge(j, left_on="d", right_on="node_zone")[["o", "city", "min"]]
    return t.rename(columns={"o": "zone_id", "min": "to_node_min"})


def bus_block(out: pd.DataFrame, root: Path, variant: str) -> pd.DataFrame:
    if variant == "r3_all_pairs":
        return out
    bus = _yaml(BUS, root)
    cap = float(_v(bus["node_access_max_road_min"]))
    zn = bus_nodes_zone_times(root, variant)
    zn = zn[zn.to_node_min <= cap].sort_values("to_node_min").groupby("zone_id").head(1)
    node_of = zn.set_index("zone_id").city
    t_of = zn.set_index("zone_id").to_node_min
    no, nd = out.o.map(node_of), out.d.map(node_of)
    ok = no.notna().to_numpy() & nd.notna().to_numpy() & (no.to_numpy() != nd.to_numpy())
    ok &= out.avail_bus.fillna(False).to_numpy(dtype=bool)
    out = out.copy()
    out["avail_bus"] = ok
    out["access_min_bus"] = np.where(
        ok, out.access_min_bus + out.o.map(t_of).to_numpy(dtype=float), np.nan
    )
    out["egress_min_bus"] = np.where(
        ok, out.egress_min_bus + out.d.map(t_of).to_numpy(dtype=float), np.nan
    )
    for c in ("ivt_min_bus", "cost_sar_bus"):
        out[c] = np.where(ok, out[c], np.nan)
    return out


def attributes(
    od: pd.DataFrame,
    scenario: str,
    root: Path = REPO_ROOT,
    candidate: Path | None = None,
    bus_variant: str = "named_and_capitals",
    skim_dir: Path = Path("runs/skims/r3-zones"),
    factor_case: str = "value",
) -> pd.DataFrame:
    """MNL columns for an OD table (o, d, road_km, road_min) on the R4 network."""
    from access import railgraph

    if bus_variant not in BUS_VARIANTS:
        raise ValueError(f"bus_variant must be one of {BUS_VARIANTS}")
    base = base_scenario(scenario)
    out = supply.attributes(od, skim_dir, base, root)
    rl = railgraph.rail_los(
        out[["o", "d"]].reset_index(drop=True),
        base if candidate is None else "S1",
        root,
        candidate,
        factor_case=factor_case,
    )
    for c in rl.columns:
        if c not in ("o", "d"):
            out[c] = rl[c].to_numpy()
    out = air_block(out, skim_dir, root)
    out = bus_block(out, root, bus_variant)
    out["scenario"] = scenario
    return out
