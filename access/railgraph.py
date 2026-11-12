"""National rail graph with located stations and transfers (R4, CP4 requirement 1; W8).

Replaces R3's best-single-line rule (`demand.supply.attributes`, A-mode-040), which ignored the wait
and let a 120-min-headway Landbridge hop beat HHR for Jeddah <-> Makkah trips. Here:
- every line in the scenario is one all-stop service; in-vehicle minutes between its stations come
  from `access.running_time` x the timetable factor (A-r4-rt-011: the line's own factor if it has
  published times, else the generic factor);
- stations of different services within the walk-transfer distance are linked (A-r4-acc-001), and
  a corridor's `connects_to` stations are linked as interchanges;
- path choice minimises generalised minutes in rail-IVT units with the mode-choice priors'
  own ratios
  (headway x b_headway/b_ivt at every boarding, walk x b_access/b_ivt, a transfer penalty
  A-r4-acc-002 at every boarding after the first; since R5, fares x b_cost/b_ivt on every ride,
  and the reported walk is the walk the search costed: explicit interchanges are 0 km);
- zone access: for every zone the nearest station of each service within the access cap
  (A-demand-045) by road (OSRM skims `runs/skims/r4-stations/`), plus the terminal minutes.

The level of service handed to the MNL (`attributes`) keeps R3's columns; transfer walk goes to
access minutes, transfer waits and penalties to in-vehicle-equivalent minutes; `rail_path` lists
the lines with km. Running times are a timetable model; demand outputs keep the label
"synthetic demand, uncalibrated: scenario comparison, not a forecast".

  uv run python -m access.railgraph skims --seed 1          (OSRM, zone x station, all stations)
  uv run python -m access.railgraph check --scenario S1 --seed 1
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml
from pyproj import Geod
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

from access import running_time as rt
from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

ACCESS_CFG = Path("cities/ksa/assumptions/access_network.yaml")
SUPPLY = Path("cities/ksa/assumptions/demand_supply.yaml")
LINES_DIR = Path("cities/ksa/lines")
CORRIDORS = Path("cities/ksa/corridors")
STATION_SKIMS = Path("runs/skims/r4-stations")
FACTORS = Path("runs/access/running_time/factors-s1/factors.json")
ZONE_POINTS = Path("runs/zones/points.geojson")
OSRM_DIR = Path("data/ksa/osrm/gcc-states-latest")
_GEOD = Geod(ellps="WGS84")

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Rail graph with transfers."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def load_cfg(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / ACCESS_CFG).read_text(encoding="utf-8"))


def km_between(lon1, lat1, lon2, lat2) -> np.ndarray:
    _, _, m = _GEOD.inv(lon1, lat1, lon2, lat2)
    return np.asarray(m) / 1000.0


# --------------------------------------------------------------------------- scenario line sets
def load_line(line_id: str, root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / LINES_DIR / f"{line_id}.yaml").read_text(encoding="utf-8"))


def load_corridor(path: Path, root: Path = REPO_ROOT) -> dict[str, Any]:
    p = path if path.is_absolute() else root / path
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def all_corridors(root: Path = REPO_ROOT) -> list[Path]:
    return sorted((root / CORRIDORS).glob("*/*.yaml"))


def scenario_lines(
    scenario: str, cfg: dict[str, Any], root: Path = REPO_ROOT, candidate: Path | None = None
) -> list[dict[str, Any]]:
    """Intercity passenger line dicts for S0 / S1 (access_network.yaml line_sets), plus one
    hypothetical corridor (a station addition is inserted into its host line instead)."""
    ids = cfg["line_sets"][scenario]["lines"]
    lines = [load_line(i, root) for i in ids]
    lines = [apply_site_overrides(ld, cfg) for ld in lines]
    if candidate is not None:
        c = load_corridor(candidate, root)
        if c.get("family") == "station_addition":
            lines = insert_station(lines, c)
        else:
            lines.append(c)
    return lines


def apply_site_overrides(line: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """Relocate unpublished station sites per access_network.yaml station_sites (A-r4-acc-004)."""
    ov = cfg.get("station_sites", {}).get(line["id"])
    if not ov:
        return line
    line = {**line, "stations": [dict(s) for s in line["stations"]]}
    for s in line["stations"]:
        o = ov.get(s["id"])
        if o:
            s["lat"], s["lon"] = float(o["lat"]), float(o["lon"])
            s["site_override"] = o.get("assumption")
    return line


def insert_station(lines: list[dict[str, Any]], c: dict[str, Any]) -> list[dict[str, Any]]:
    """Station addition: the corridor's `planned` station joins its host line at its km-post
    position (host from the `stations.geojson <line>:<station>` sources of its neighbours)."""
    host = None
    for s in c["stations"]:
        src = str(s.get("source", ""))
        if src.startswith("stations.geojson "):
            host = src.split()[1].split(":")[0]
            break
    new = [s for s in c["stations"] if s.get("class") == "planned"]
    out = []
    for ld in lines:
        if ld["id"] != host:
            out.append(ld)
            continue
        ld = {**ld, "stations": [dict(s) for s in ld["stations"]]}
        nbr = {s["id"]: s for s in c["stations"] if s.get("class") != "planned"}
        first = sorted(nbr.values(), key=lambda s: float(s["km_post"]))[0]
        host_km = {s["id"]: float(s["km_post"]) for s in ld["stations"]}
        offset = host_km.get(first["id"], 0.0) - float(first["km_post"])
        for s in new:
            ld["stations"].append(
                {**s, "km_post": float(s["km_post"]) + offset, "class": "intermediate"}
            )
        ld["stations"].sort(key=lambda s: float(s["km_post"]))
        ld["candidate"] = c["id"]
        out.append(ld)
    if host is None or not any(ld.get("candidate") == c["id"] for ld in out):
        raise ValueError(f"{c['id']}: host line of the station addition not in the scenario")
    return out


# --------------------------------------------------------------------------- services
@dataclass
class Service:
    line_id: str
    layer: str
    stations: pd.DataFrame  # uid, id, km_post, lat, lon, class
    ivt: np.ndarray  # (n, n) in-vehicle minutes, factor applied
    km: np.ndarray  # (n, n) route km
    headway_min: float
    fare_per_km: float
    ontime: float
    factor: float


def factors(root: Path = REPO_ROOT) -> dict[str, Any]:
    p = root / FACTORS
    if not p.exists():
        f = rt.timetable_factors(root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(f, indent=1, default=str) + "\n")
    return json.loads(p.read_text(encoding="utf-8"))


def service_params(line: dict[str, Any], cfg: dict[str, Any], sup: dict[str, Any]) -> dict:
    lid = line["id"]
    if lid in sup["rail"]["lines"]:
        lp = sup["rail"]["lines"][lid]
        return {
            "headway": float(_v(lp["headway_min"])),
            "fare": float(_v(lp["fare_per_km_sar"])),
        }
    d = cfg["hypothetical_service"]
    lt = line.get("line_type", "conventional_passenger")
    return {
        "headway": float(
            _v(d["headway_min"][lt] if lt in d["headway_min"] else d["headway_min"]["default"])
        ),
        "fare": float(
            _v(
                d["fare_per_km_sar"][lt]
                if lt in d["fare_per_km_sar"]
                else d["fare_per_km_sar"]["default"]
            )
        ),
    }


def build_service(
    line: dict[str, Any],
    cfg: dict[str, Any],
    sup: dict[str, Any],
    fac: dict[str, Any],
    ontime_by_line: dict[str, float],
    root: Path = REPO_ROOT,
    rt_scale: str = "value",
    factor_case: str = "value",
) -> Service:
    run = rt.build_run(line, root, rt_scale)
    stops = run.stations.id.tolist()
    tab = rt.pair_table(run, stops)
    n = len(stops)
    idx = {s: i for i, s in enumerate(stops)}
    ivt = np.zeros((n, n))
    km = np.zeros((n, n))
    for r in tab.itertuples(index=False):
        i, j = idx[r[0]], idx[r[1]]
        ivt[i, j] = ivt[j, i] = r.ivt_min
        km[i, j] = km[j, i] = r.km
    f = fac["per_line"].get(line["id"], fac["generic"])
    factor = (
        float(f["value"])
        if factor_case == "value"
        else float(f["range"][0] if factor_case == "low" else f["range"][1])
    )
    st = run.stations.copy()
    st["uid"] = line["id"] + ":" + st.id
    p = service_params(line, cfg, sup)
    on = ontime_by_line.get(line["id"], float(_v(cfg["hypothetical_service"]["ontime_pp"])))
    return Service(
        line["id"],
        line.get("layer", "hypothetical"),
        st,
        ivt * factor,
        km,
        p["headway"],
        p["fare"],
        on,
        factor,
    )


# --------------------------------------------------------------------------- graph
@dataclass
class Graph:
    services: list[Service]
    nodes: pd.DataFrame  # hub nodes: uid, line_id, svc, i, lat, lon
    gen: np.ndarray  # (H, H) generalised minutes hub->hub (first boarding without penalty)
    pred: np.ndarray  # predecessors on the expanded graph
    n_hub: int
    w: dict[str, float]
    # R5 fix: walk minutes of every walk/interchange link as the search costed it, so trace()
    # reports the same walk the path choice used (explicit interchanges are 0 km by definition)
    walk_min: dict[tuple[int, int], float] = field(default_factory=dict)


def weights(cfg: dict[str, Any]) -> dict[str, float]:
    from modechoice.coefficients import base_coefficients

    c = base_coefficients()
    b_ivt = abs(float(c.ivt["rail"]))
    return {
        "headway": abs(float(c.headway)) / b_ivt,
        "access": abs(float(c.access_egress)) / b_ivt,
        # R5 fix: fares in the path choice (minutes per SAR, b_cost / b_ivt,rail), so the chosen
        # path is the one the MNL values most; without it a new faster-but-dearer path could
        # replace a cheaper one and lower the rail utility of an existing pair
        "fare": abs(float(c.cost)) / b_ivt,
        "transfer_penalty": float(_v(cfg["transfer"]["penalty_ivt_min"])),
        "walk_kmh": float(_v(cfg["transfer"]["walk_kmh"])),
        "walk_fixed_min": float(_v(cfg["transfer"]["walk_fixed_min"])),
        "max_walk_km": float(_v(cfg["transfer"]["max_walk_km"])),
    }


def board_cost(sv: Service, w: dict[str, float], mode: str, wait_cap: float) -> float:
    """Cost of one boarding: generalised (headway x b_headway/b_ivt), minutes (expected wait
    headway/2 capped, A-access-010) or in-vehicle (0)."""
    if mode == "generalised":
        return w["headway"] * sv.headway_min
    if mode == "minutes":
        return min(sv.headway_min / 2.0, wait_cap)
    return 0.0


def build_graph(
    services: list[Service],
    lines: list[dict[str, Any]],
    cfg: dict[str, Any],
    mode: str = "generalised",
) -> Graph:
    """mode: generalised (path choice for the MNL), minutes (door-to-door clock minutes: waits,
    walks, rides; no penalty) or ivt (rides only)."""
    w = weights(cfg)
    wait_cap = float(_v(cfg.get("wait_cap_min", {"value": 30})))
    if mode != "generalised":
        w = {
            **w,
            "transfer_penalty": 0.0,
            "access": 1.0 if mode == "minutes" else 0.0,
            "fare": 0.0,
        }
    hubs = []
    for s, sv in enumerate(services):
        for i, r in enumerate(sv.stations.itertuples(index=False)):
            hubs.append(
                {
                    "uid": r.uid,
                    "line_id": sv.line_id,
                    "svc": s,
                    "i": i,
                    "lat": float(r.lat),
                    "lon": float(r.lon),
                }
            )
    nodes = pd.DataFrame(hubs)
    h = len(nodes)
    # expanded graph: hub k = k, platform (boarded) k = h + k, arrival (on board, about to
    # alight) k = 2h + k. Rides go platform -> arrival only, so two rides cannot chain without
    # alighting and re-boarding (which would skip the intermediate dwell).
    rows, cols, vals = [], [], []
    base = 0
    for sv in services:
        n = len(sv.stations)
        for i in range(n):
            hk = base + i
            rows += [hk, 2 * h + hk]
            cols += [h + hk, hk]
            vals += [board_cost(sv, w, mode, wait_cap) + w["transfer_penalty"] + 1e-9, 1e-9]
            for j in range(n):
                if i != j:
                    rows.append(h + hk)
                    cols.append(2 * h + base + j)
                    vals.append(max(sv.ivt[i, j] + w["fare"] * sv.km[i, j] * sv.fare_per_km, 1e-6))
        base += n
    # walk transfers between hubs of different services
    lat, lon = nodes.lat.to_numpy(), nodes.lon.to_numpy()
    links = set()
    for a in range(h):
        d = km_between(np.full(h, lon[a]), np.full(h, lat[a]), lon, lat)
        for b in np.where((d <= w["max_walk_km"]) & (nodes.svc.to_numpy() != nodes.svc.iat[a]))[0]:
            links.add((a, int(b), float(d[b])))
    # explicit interchanges: corridor connects_to (line:station) and access_network.yaml
    uid_ix = {u: k for k, u in enumerate(nodes.uid)}
    pairs = list(cfg.get("interchanges", []))
    for ld in lines:
        for c in ld.get("connects_to") or []:
            for s in ld["stations"]:
                pairs.append(
                    {"a": f"{ld['id']}:{s['id']}", "b": c["station"], "nearest_only": True}
                )
    for p in pairs:
        if p["a"] not in uid_ix or p["b"] not in uid_ix:
            continue
        a, b = uid_ix[p["a"]], uid_ix[p["b"]]
        if p.get("nearest_only"):
            # only the corridor station nearest to the connection point is the interchange
            cand = [k for k, u in enumerate(nodes.uid) if u.split(":")[0] == p["a"].split(":")[0]]
            dd = km_between(
                lon[cand], lat[cand], np.full(len(cand), lon[b]), np.full(len(cand), lat[b])
            )
            a = cand[int(np.argmin(dd))]
        links.add((a, b, 0.0))
        links.add((b, a, 0.0))
    walk_min: dict[tuple[int, int], float] = {}
    for a, b, d in links:
        rows.append(a)
        cols.append(b)
        wm = w["walk_fixed_min"] + 60.0 * d / w["walk_kmh"]
        # duplicate (a, b) links are summed by coo_matrix -> keep the summed walk too
        walk_min[(a, b)] = walk_min.get((a, b), 0.0) + wm
        vals.append(w["access"] * wm)
    m = coo_matrix((vals, (rows, cols)), shape=(3 * h, 3 * h)).tocsr()
    # every path starts by boarding at its own hub (the zone access chose that station), so the
    # search runs from the boarded platforms: no walk-only "rail" path between co-located stations
    dist, pred = dijkstra(m, directed=True, indices=h + np.arange(h), return_predecessors=True)
    board = np.array([board_cost(services[int(sv)], w, mode, wait_cap) for sv in nodes.svc])
    gen = board[:, None] + dist[:, :h]
    np.fill_diagonal(gen, np.inf)
    return Graph(services, nodes, gen, pred, h, w, walk_min)


def trace(g: Graph, a: int, b: int) -> dict[str, Any]:
    """Path attributes hub a -> hub b: IVT, km, fare, legs, boardings, walk minutes."""
    path = [b]
    start = g.n_hub + a  # the search ran from the boarded platform of hub a
    while path[-1] != start:
        p = int(g.pred[a, path[-1]])
        if p < 0:
            return {}
        path.append(p)
    path = [a] + path[::-1]
    h = g.n_hub
    ivt = km = fare = walk = wait_eq = 0.0
    legs: list[tuple[str, float]] = []
    boardings = 0
    first_hw = math.nan
    for u, v in zip(path[:-1], path[1:], strict=True):
        if h <= u < 2 * h and v >= 2 * h:  # ride
            su, sv_ = g.nodes.iloc[u - h], g.nodes.iloc[v - 2 * h]
            svc = g.services[int(su.svc)]
            t = svc.ivt[int(su.i), int(sv_.i)]
            k = svc.km[int(su.i), int(sv_.i)]
            ivt += t
            km += k
            fare += k * svc.fare_per_km
            if legs and legs[-1][0] == svc.line_id:
                legs[-1] = (svc.line_id, legs[-1][1] + k)
            else:
                legs.append((svc.line_id, k))
        elif u < h and v == u + h:  # board
            svc = g.services[int(g.nodes.svc.iat[u])]
            boardings += 1
            if boardings == 1:
                first_hw = svc.headway_min
            else:
                wait_eq += g.w["headway"] * svc.headway_min + g.w["transfer_penalty"]
        elif u < h and v < h:  # walk
            if (u, v) in g.walk_min:  # R5: the link cost the search used
                walk += g.walk_min[(u, v)]
                continue
            d = km_between(
                g.nodes.lon.iat[u], g.nodes.lat.iat[u], g.nodes.lon.iat[v], g.nodes.lat.iat[v]
            )
            walk += g.w["walk_fixed_min"] + 60.0 * float(d) / g.w["walk_kmh"]
    main = max(legs, key=lambda x: x[1])[0] if legs else None
    return {
        "ivt": ivt,
        "km": km,
        "fare": fare,
        "walk": walk,
        "xfer_eq": wait_eq,
        "boardings": boardings,
        "headway": first_hw,
        "main": main,
        "path": "|".join(f"{ln}:{k:.1f}" for ln, k in legs),
    }


# --------------------------------------------------------------------------- level of service
def station_table(services: list[Service]) -> pd.DataFrame:
    rows = []
    for sv in services:
        for r in sv.stations.itertuples(index=False):
            rows.append(
                {"uid": r.uid, "line_id": sv.line_id, "lat": float(r.lat), "lon": float(r.lon)}
            )
    return pd.DataFrame(rows)


def zone_station_times(services: list[Service], root: Path = REPO_ROOT) -> pd.DataFrame:
    """zone_id, uid, to_min, from_min from the R4 station skims (matched by coordinates)."""
    zs = pd.read_parquet(root / STATION_SKIMS / "zone_station.parquet")
    st = station_table(services)
    st["key"] = st.lat.round(5).astype(str) + "," + st.lon.round(5).astype(str)
    missing = set(st.key) - set(zs.key)
    if missing:
        raise KeyError(
            f"{len(missing)} stations have no skim; run `access.railgraph skims`: "
            f"{sorted(missing)[:5]}"
        )
    return st[["uid", "line_id", "key"]].merge(zs, on="key")


def rail_los(
    od: pd.DataFrame,
    scenario: str,
    root: Path = REPO_ROOT,
    candidate: Path | None = None,
    rt_scale: str = "value",
    factor_case: str = "value",
) -> pd.DataFrame:
    """Rail columns for an OD table (o, d): the MNL inputs plus rail_line (main line), rail_path,
    rail_station_o/d, rail_km, rail_boardings. `factor_case` low/high = timetable factor range ends
    (the running-time band)."""
    from modechoice.coefficients import load_r3

    cfg = load_cfg(root)
    sup = yaml.safe_load((root / SUPPLY).read_text(encoding="utf-8"))
    r3 = load_r3()
    ontime = {k: float(v["value"]) for k, v in r3["on_time"]["rail_by_line"].items()}
    fac = factors(root)
    lines = scenario_lines(scenario, cfg, root, candidate)
    services = [
        build_service(ld, cfg, sup, fac, ontime, root, rt_scale, factor_case) for ld in lines
    ]
    g = build_graph(services, lines, cfg)
    zst = zone_station_times(services, root)
    term = float(_v(sup["rail"]["terminal_min"]))
    cap = float(_v(sup["rail"]["station_access"]["max_road_min"]))
    uid_ix = {u: k for k, u in enumerate(g.nodes.uid)}
    zst = zst[zst.to_min.notna()]
    # per zone: nearest station of each service within the cap (both directions)
    acc = zst[zst.to_min <= cap].sort_values("to_min").groupby(["zone_id", "line_id"]).head(1)
    egr = zst[zst.from_min <= cap].sort_values("from_min").groupby(["zone_id", "line_id"]).head(1)
    acc_by = {
        z: list(zip(gr.uid.map(uid_ix), gr.to_min + term, strict=True))
        for z, gr in acc.groupby("zone_id")
    }
    egr_by = {
        z: list(zip(gr.uid.map(uid_ix), gr.from_min + term, strict=True))
        for z, gr in egr.groupby("zone_id")
    }
    wa = g.w["access"]
    n = len(od)
    best = np.full(n, np.inf)
    bo = np.full(n, -1)
    bd = np.full(n, -1)
    ba = np.full(n, np.nan)
    be = np.full(n, np.nan)
    o_arr, d_arr = od.o.to_numpy(), od.d.to_numpy()
    cache: dict[tuple[str, str], tuple[float, int, int, float, float]] = {}
    for k in range(n):
        key = (o_arr[k], d_arr[k])
        if key not in cache:
            res = (np.inf, -1, -1, np.nan, np.nan)
            for a, ta in acc_by.get(key[0], []):
                for b, tb in egr_by.get(key[1], []):
                    if a == b:
                        continue
                    gc = wa * (ta + tb) + g.gen[a, b]
                    if gc < res[0]:
                        res = (gc, a, b, ta, tb)
            cache[key] = res
        best[k], bo[k], bd[k], ba[k], be[k] = cache[key]
    ok = np.isfinite(best)
    tr_cache: dict[tuple[int, int], dict[str, Any]] = {}
    cols: dict[str, list] = {
        c: []
        for c in ("ivt", "km", "fare", "walk", "xfer_eq", "boardings", "headway", "main", "path")
    }
    for k in range(n):
        if not ok[k]:
            for c in cols:
                cols[c].append(None)
            continue
        key2 = (int(bo[k]), int(bd[k]))
        if key2 not in tr_cache:
            tr_cache[key2] = trace(g, *key2)
        t = tr_cache[key2]
        for c in cols:
            cols[c].append(t.get(c))
    out = od[["o", "d"]].copy()
    f = lambda c: np.array([np.nan if x is None else x for x in cols[c]], dtype=float)  # noqa: E731
    # a path must ride at least one line that is not a connector (A-r4-acc-005)
    conn = set(_v(cfg.get("connector_lines", {"value": []})))
    real = np.array(
        [
            isinstance(pth, str) and any(leg.split(":")[0] not in conn for leg in pth.split("|"))
            for pth in cols["path"]
        ]
    )
    ok = ok & (np.nan_to_num(f("boardings")) >= 1) & real
    for c in cols:
        cols[c] = [x if keep else None for x, keep in zip(cols[c], ok, strict=True)]
    ba = np.where(ok, ba, np.nan)
    be = np.where(ok, be, np.nan)
    out["avail_rail"] = ok
    out["ivt_min_rail"] = f("ivt") + f("xfer_eq")
    out["access_min_rail"] = ba + f("walk")
    out["egress_min_rail"] = be
    out["headway_min_rail"] = f("headway")
    out["cost_sar_rail"] = f("fare")
    out["rail_line"] = np.array(cols["main"], dtype=object)
    out["ontime_rail"] = [
        ontime.get(x, float(_v(cfg["hypothetical_service"]["ontime_pp"]))) if x else np.nan
        for x in cols["main"]
    ]
    out["rail_path"] = np.array(cols["path"], dtype=object)
    out["rail_station_o"] = np.where(ok, g.nodes.uid.to_numpy()[np.maximum(bo, 0)], None)
    out["rail_station_d"] = np.where(ok, g.nodes.uid.to_numpy()[np.maximum(bd, 0)], None)
    out["rail_km"] = f("km")
    out["rail_boardings"] = f("boardings")
    return out


# --------------------------------------------------------------------------- skims
def all_station_points(root: Path = REPO_ROOT) -> pd.DataFrame:
    """Every station of every intercity line set and every corridor, with site overrides."""
    cfg = load_cfg(root)
    pts = []
    ids = sorted({i for v in cfg["line_sets"].values() for i in v["lines"]})
    for lid in ids:
        ld = apply_site_overrides(load_line(lid, root), cfg)
        pts += [(s["lat"], s["lon"]) for s in ld["stations"]]
    for p in all_corridors(root):
        c = load_corridor(p, root)
        pts += [(s["lat"], s["lon"]) for s in c["stations"]]
    df = pd.DataFrame(pts, columns=["lat", "lon"]).astype(float)
    df["key"] = df.lat.round(5).astype(str) + "," + df.lon.round(5).astype(str)
    return df.drop_duplicates("key").reset_index(drop=True)


@app.command("skims")
def skims_cmd(
    out: Path = typer.Option(STATION_SKIMS),
    osrm_dir: Path = typer.Option(OSRM_DIR),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """OSRM road minutes zone -> station and station -> zone for every station (free flow)."""
    from demand.supply import zone_points
    from network import osrm as osrm_mod

    z = zone_points(root)
    st = all_station_points(root)
    zl, sl = z[["lon", "lat"]].to_numpy(), st[["lon", "lat"]].to_numpy()
    with osrm_mod.server(root / osrm_dir, max_table=1000) as url:
        zs = osrm_mod.table(url, zl, sl, batch=100)
        sz = osrm_mod.table(url, sl, zl, batch=100)
    n, m = len(z), len(st)
    df = pd.DataFrame(
        {
            "zone_id": np.repeat(z.zone_id.to_numpy(), m),
            "key": np.tile(st.key.to_numpy(), n),
            "to_min": (zs["duration_s"] / 60).ravel().round(2),
            "to_km": (zs["distance_m"] / 1000).ravel().round(3),
            "from_min": (sz["duration_s"].T / 60).ravel().round(2),
            "from_km": (sz["distance_m"].T / 1000).ravel().round(3),
        }
    )
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    df.to_parquet(run / "zone_station.parquet", index=False)
    st.to_parquet(run / "stations.parquet", index=False)
    summary = {
        "zones": n,
        "stations": m,
        "unreachable": int(df.to_min.isna().sum()),
        "osrm_version": osrm_mod.osrm_version(),
    }
    write_meta(
        run,
        seed,
        {"stations": st.key.tolist()},
        extra={"summary": summary, "method": "osrm_table_mld_car (free flow)", "label": LABEL},
    )
    typer.echo(json.dumps(summary, indent=1))


@app.command("check")
def check_cmd(
    scenario: str = typer.Option("S1"),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Print the generalised minutes and path between the main station pairs (debugging aid)."""
    cfg = load_cfg(root)
    sup = yaml.safe_load((root / SUPPLY).read_text(encoding="utf-8"))
    fac = factors(root)
    lines = scenario_lines(scenario, cfg, root)
    from modechoice.coefficients import load_r3

    ontime = {k: float(v["value"]) for k, v in load_r3()["on_time"]["rail_by_line"].items()}
    svcs = [build_service(ld, cfg, sup, fac, ontime, root) for ld in lines]
    g = build_graph(svcs, lines, cfg)
    for a, b in cfg.get("check_pairs", []):
        ia, ib = list(g.nodes.uid).index(a), list(g.nodes.uid).index(b)
        typer.echo(f"{a} -> {b}: gen {g.gen[ia, ib]:.1f} | {trace(g, ia, ib)}")


if __name__ == "__main__":
    app()
