"""S6-L6: one connected rail system, a comparison layout (not the recommended programme).

  uv run python -m optimise.connect components --out runs/r6/l6 --seed 1
  uv run python -m optimise.connect search --out runs/r6/l6 --seed 1
  uv run python -m optimise.connect scenario --out runs/r6/l6
  uv run python -m optimise.connect map --out runs/r6/l6
  uv run python -m optimise.connect score --out runs/r6/l6/score   # after `optimise.search full`

- components: the rail graph of S1 and of S6-L1..L5 under the CURRENT interchange rules
  (`network.graph.build_graph`: walk 0.4 km A-r1a-030, same name 3.0 km A-r1a-032; nothing is
  widened, no station moves), each layout's corridors added as the judge adds them (lines appended,
  station additions inserted into their host line, `optimise.layout.materialise` for variants);
  component count, lines and stations per component, and the measured gaps between components.
- search: the smallest connecting set over the R6_V3 library options (A-r6-130..134,
  `cities/ksa/assumptions/r6_l6.yaml`): one component and every required city on the graph;
  exact MILP (scipy/HiGHS) with a single-commodity flow on the "item graph" (S1 components and
  library options as nodes, an arc wherever two items have stations that meet the interchange
  rules); min capex P50 first, corridor count second; the next two sets must each drop at least
  one corridor of every earlier set. Every set is re-checked on the real graph.
- the building blocks are the library's single-corridor scores (fast mode, A-r6-006): "fast mode,
  not a full-judge score; corridor interaction not included". Nothing here runs the judge.
- score (S6_L6_SCORE): reads the full-judge v3 output of S6-L6 (run by `optimise.search full
  --all-cases`, never edited) and writes the scorecard row in the `runs/r6/top5/top5.csv` columns,
  the reported-only national reach (A-r6-104), the layout hash and the map; nothing under
  `runs/r6/top5/` is written.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import functools
import json
import time
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import typer
import yaml

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL
from common.runmeta import seed_option, write_meta
from common.schemas import LineSpec, Scenario
from network import graph as ng
from network.geo import haversine_km

PARAMS = Path("cities/ksa/assumptions/r6_l6.yaml")
CORRIDORS = Path("cities/ksa/corridors")
FAST_LABEL = (
    "fast mode, not a full-judge score; corridor interaction not included; the full judge "
    "overstated/understated fast mode by 1–17 % of capex in R6"
)
LAYOUTS = ("S6-L1", "S6-L2", "S6-L3", "S6-L4", "S6-L5")
app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


def params(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / PARAMS).read_text(encoding="utf-8"))


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


# --------------------------------------------------------------------------- graph
def s1_lines(root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    scn = ng.load_scenario(root / "scenarios/S1.yaml")
    return [
        ln.model_dump(by_alias=True, mode="json", exclude_none=True)
        for ln in ng.scenario_lines(scn, root / "cities/ksa/lines")
    ]


def materialise(item: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    from optimise import layout as lay

    return lay.materialise(item, root)


def layout_lines(items: list[dict[str, Any]], root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """S1 lines + the layout items, exactly as the judge composes a layout (lines appended,
    station additions inserted into the host line at their km-post)."""
    from access.railgraph import insert_station

    lines = s1_lines(root)
    for it in items:
        c = materialise(it, root)
        if c.get("family") == "station_addition":
            lines = insert_station(lines, c)
        else:
            lines.append(c)
    return lines


def to_spec(d: dict[str, Any]) -> LineSpec:
    keys = set(LineSpec.model_fields) | {f.alias for f in LineSpec.model_fields.values() if f.alias}
    return LineSpec.model_validate({k: v for k, v in d.items() if k in keys})


def rail_graph(items: list[dict[str, Any]], root: Path = REPO_ROOT) -> nx.MultiGraph:
    """The scenario rail graph of S1 + items under the current interchange rules."""
    return ng.build_graph([to_spec(d) for d in layout_lines(items, root)], ng.load_params())


def components(g: nx.MultiGraph) -> list[set[str]]:
    """Connected components, largest first (ties by first node id)."""
    return sorted(nx.connected_components(g), key=lambda c: (-len(c), min(c)))


def _xy(g: nx.MultiGraph, nodes: list[str]) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.array([g.nodes[n]["lat"] for n in nodes]),
        np.array([g.nodes[n]["lon"] for n in nodes]),
    )


def gap(g: nx.MultiGraph, a: set[str], b: set[str]) -> dict[str, Any]:
    """Nearest station pair between two components (great-circle km, network.geo)."""
    na, nb = sorted(a), sorted(b)
    la, oa = _xy(g, na)
    lb, ob = _xy(g, nb)
    d = haversine_km(la[:, None], oa[:, None], lb[None, :], ob[None, :])
    i, j = np.unravel_index(int(np.argmin(d)), d.shape)
    return {
        "a": na[i],
        "a_name": g.nodes[na[i]]["name_en"],
        "b": nb[j],
        "b_name": g.nodes[nb[j]]["name_en"],
        "km": round(float(d[i, j]), 2),
    }


def summary(g: nx.MultiGraph) -> dict[str, Any]:
    cc = components(g)
    comps = []
    for k, c in enumerate(cc):
        lines = sorted({g.nodes[n]["line"] for n in c})
        comps.append(
            {
                "component": k,
                "lines": lines,
                "n_stations": len(c),
                "stations": sorted(c) if len(c) <= 12 else None,
            }
        )
    gaps = [
        {"from": i, "to": j, **gap(g, cc[i], cc[j])}
        for i in range(len(cc))
        for j in range(i + 1, len(cc))
    ]
    return {"n_components": len(cc), "components": comps, "gaps": gaps}


def scenario_items(sid: str, root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    d = yaml.safe_load((root / "scenarios" / f"{sid}.yaml").read_text(encoding="utf-8"))
    return list((d.get("layout") or {}).get("corridors") or [])


# --------------------------------------------------------------------------- cities
def city_refs(root: Path = REPO_ROOT) -> dict[str, dict[str, Any]]:
    """Reference point per city: the station the corridor families use for it (A-r6-131)."""
    return json.loads(json.dumps(_city_refs(Path(root))))


@functools.lru_cache(maxsize=4)
def _city_refs(root: Path) -> dict[str, dict[str, Any]]:
    p = params(root)
    out = {}
    for row in p["required"] + p["reported"]:
        fams = [row["anchor_family"]] if row.get("anchor_family") else None
        hit = None
        for f in sorted((root / CORRIDORS).glob("*/*.yaml")):
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
            if fams and d["family"] not in fams:
                continue
            for s in d["stations"]:
                src = str(s.get("source", ""))
                ok = src.startswith("register") or src.startswith("A-screen-013")
                if s["id"] == row["ref"] and ok:
                    hit = {
                        "lat": float(s["lat"]),
                        "lon": float(s["lon"]),
                        "name_en": s["name_en"],
                        "ref_source": src,
                        "ref_file": str(f.relative_to(root)),
                    }
                    break
            if hit:
                break
        if hit is None:
            raise KeyError(f"no reference point for {row['city']} ({row['ref']})")
        out[row["city"]] = {**row, **hit, "required": row in p["required"]}
    return out


def on_graph(g: nx.MultiGraph, nodes: set[str] | None, ref: dict[str, Any]) -> dict[str, Any]:
    """T1 interchange rules, else T2 served distance (A-r6-131); nearest station reported."""
    gp = ng.load_params()["interchange"]
    walk, same = float(gp["walk_max_km"]["value"]), float(gp["same_name_max_km"]["value"])
    p = params()["on_graph"]
    served = float(_v(p["served_metro_km" if ref["kind"] == "metro" else "served_town_km"]))
    ns = sorted(nodes if nodes is not None else g.nodes)
    la, lo = _xy(g, ns)
    d = haversine_km(la, lo, ref["lat"], ref["lon"])
    k = int(np.argmin(d))
    same_name = [
        n
        for n, x in zip(ns, d, strict=True)
        if x <= same and ng._norm(g.nodes[n]["name_en"]) == ng._norm(ref["name_en"])
    ]
    if d[k] <= walk:
        test = "T1 walk"
    elif same_name:
        test = "T1 same name"
    elif d[k] <= served:
        test = f"T2 served {served:g} km"
    else:
        test = None
    return {
        "nearest": ns[k],
        "nearest_name": g.nodes[ns[k]]["name_en"],
        "km": round(float(d[k]), 2),
        "test": test,
        "on_graph": test is not None,
    }


# --------------------------------------------------------------------------- items
def _linked(a: list[dict], b: list[dict], walk: float, same: float) -> bool:
    if not a or not b:
        return False
    la = np.array([s["lat"] for s in a])[:, None]
    oa = np.array([s["lon"] for s in a])[:, None]
    lb = np.array([s["lat"] for s in b])[None, :]
    ob = np.array([s["lon"] for s in b])[None, :]
    d = haversine_km(la, oa, lb, ob)
    if (d <= walk).any():
        return True
    na = [ng._norm(s["name_en"]) for s in a]
    nb = [ng._norm(s["name_en"]) for s in b]
    return any(na[i] == nb[j] for i, j in zip(*np.nonzero(d <= same), strict=True))


def item_model(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Nodes = S1 components + library options; arcs = interchange-rule links (exact: every
    item is internally connected and inter-item links are the graph's interchange edges)."""
    from optimise import variants as va

    fast = va.FastV(root)
    g1 = rail_graph([], root)
    cc = components(g1)
    gp = ng.load_params()["interchange"]
    walk, same = float(gp["walk_max_km"]["value"]), float(gp["same_name_max_km"]["value"])
    nodes: list[dict[str, Any]] = []
    for k, c in enumerate(cc):
        sts = [
            {
                "lat": g1.nodes[n]["lat"],
                "lon": g1.nodes[n]["lon"],
                "name_en": g1.nodes[n]["name_en"],
            }
            for n in sorted(c)
        ]
        nodes.append(
            {
                "kind": "s1",
                "name": f"S1-c{k}",
                "lines": sorted({g1.nodes[n]["line"] for n in c}),
                "stations": sts,
                "host": None,
            }
        )
    line_comp = {ln: k for k, nd in enumerate(nodes) for ln in nd["lines"]}
    for o, (cid, var, lib) in enumerate(fast.opts):
        c = materialise({"id": cid, **var}, root)
        if c.get("family") == "station_addition":
            sts = [s for s in c["stations"] if s.get("class") == "planned"]
            host = next(
                str(s["source"]).split()[1].split(":")[0]
                for s in c["stations"]
                if str(s.get("source", "")).startswith("stations.geojson ")
            )
            hk = line_comp[host]
        else:
            sts, hk = list(c["stations"]), None
        nodes.append(
            {
                "kind": "opt",
                "name": lib,
                "id": cid,
                "variant": var,
                "opt": o,
                "stations": sts,
                "host": hk,
            }
        )
    n = len(nodes)
    adj = set()
    for i in range(n):
        if nodes[i]["host"] is not None:
            adj.add((i, nodes[i]["host"]))
        for j in range(i + 1, n):
            a, b = nodes[i], nodes[j]
            if a["kind"] == "opt" and b["kind"] == "opt" and a["id"] == b["id"]:
                continue  # options of one corridor are exclusive
            if _linked(a["stations"], b["stations"], walk, same):
                adj.add((i, j))
    return {"fast": fast, "nodes": nodes, "edges": sorted(adj), "n_s1": len(cc)}


def best_phase(fast: Any, o: int) -> int:
    """Phase index with the highest robust NPV (A-r6-001) of option o alone (A-r6-134)."""
    rob = (fast.pvb[o] - fast.pvc[o]).min(axis=1)
    return int(np.argmax(rob))


def covers(model: dict[str, Any], refs: dict[str, dict[str, Any]]) -> dict[str, list[int]]:
    """Per required city: the item nodes whose stations put it on the graph (T1 or T2)."""
    gp = ng.load_params()["interchange"]
    walk, same = float(gp["walk_max_km"]["value"]), float(gp["same_name_max_km"]["value"])
    p = params()["on_graph"]
    out = {}
    for city, r in refs.items():
        served = float(_v(p["served_metro_km" if r["kind"] == "metro" else "served_town_km"]))
        ref = [{"lat": r["lat"], "lon": r["lon"], "name_en": r["name_en"]}]
        hit = []
        for k, nd in enumerate(model["nodes"]):
            sts = nd["stations"]
            if not sts:
                continue
            if _linked(ref, sts, walk, same):
                hit.append(k)
                continue
            d = haversine_km(
                np.array([s["lat"] for s in sts]),
                np.array([s["lon"] for s in sts]),
                r["lat"],
                r["lon"],
            )
            if (d <= served).any():
                hit.append(k)
        out[city] = hit
    return out


def solve(
    model: dict[str, Any],
    need: dict[str, list[int]],
    exclude_ids: set[str] = frozenset(),
    forbid: list[set[str]] | None = None,
    capex_cap: float | None = None,
    count_obj: bool = False,
) -> set[int] | None:
    """Exact MILP (scipy/HiGHS): min capex (or the corridor count under a capex cap) s.t. one
    option per corridor at most, every required city covered, and the S1 components plus the
    chosen options connected in the item graph. Connectivity by lazy node-separator cuts: for a
    selected component C without the root, y_v <= sum of y over the neighbours of C (exact: any
    path from v to the root leaves C through a neighbour of C); re-solved until connected."""
    from scipy.optimize import Bounds, LinearConstraint, milp

    nodes, fast = model["nodes"], model["fast"]
    n = len(nodes)
    s1 = [k for k in range(n) if nodes[k]["kind"] == "s1"]
    opt = [k for k in range(n) if nodes[k]["kind"] == "opt"]
    nbr: dict[int, set[int]] = {k: set() for k in range(n)}
    for i, j in model["edges"]:
        nbr[i].add(j)
        nbr[j].add(i)
    cap = np.zeros(n)
    for k in opt:
        cap[k] = fast.capex[nodes[k]["opt"], 0]
    c = np.zeros(n)
    if count_obj:
        c[opt] = 1.0
    else:
        c[:] = cap
    lb, ub = np.zeros(n), np.ones(n)
    lb[s1] = 1.0
    for k in opt:
        if nodes[k]["id"] in exclude_ids:
            ub[k] = 0.0
    A: list[np.ndarray] = []
    lo: list[float] = []
    hi: list[float] = []

    def add(r: np.ndarray, a: float, b: float) -> None:
        A.append(r)
        lo.append(a)
        hi.append(b)

    by_id: dict[str, list[int]] = {}
    for k in opt:
        by_id.setdefault(nodes[k]["id"], []).append(k)
    for ks in by_id.values():
        r = np.zeros(n)
        r[ks] = 1.0
        add(r, -np.inf, 1.0)
    for _city, ks in need.items():
        if any(k in s1 for k in ks):
            continue
        r = np.zeros(n)
        r[ks] = 1.0
        add(r, 1.0, np.inf)
    for fs in forbid or []:  # drop at least one corridor of an earlier set
        r = np.zeros(n)
        for k in opt:
            if nodes[k]["id"] in fs:
                r[k] = 1.0
        add(r, -np.inf, float(len(fs) - 1))
    if capex_cap is not None:
        add(cap.copy(), -np.inf, capex_cap)
    root = s1[0]
    # options of one corridor with the same stations are one topology group (variants that
    # change only line type or electrification): cuts are written on group sums, which removes
    # the symmetry between such variants
    gkey = {
        k: (nodes[k]["id"], tuple(s.get("id", "") for s in nodes[k]["stations"]))
        if nodes[k]["kind"] == "opt"
        else ("s1", k)
        for k in range(n)
    }
    groups: dict[tuple, list[int]] = {}
    for k in range(n):
        groups.setdefault(gkey[k], []).append(k)

    def expand(ks: set[int]) -> set[int]:
        return set().union(*(groups[gkey[k]] for k in ks)) if ks else set()

    def cut(cc: set[int]) -> None:
        cc = expand(cc)
        ring = sorted(expand(set().union(*(nbr[v] for v in cc)) - cc) - cc)
        for key in sorted({gkey[v] for v in cc}):
            r = np.zeros(n)
            r[ring] = 1.0
            r[groups[key]] -= 1.0
            add(r, 0.0, np.inf)

    for _key, ks in groups.items():  # singleton-group cuts up front
        if root not in ks and nbr[ks[0]]:
            cut(set(ks))
    for _ in range(2000):
        res = milp(
            c,
            constraints=LinearConstraint(np.array(A), lo, hi),
            integrality=np.ones(n),
            bounds=Bounds(lb, ub),
        )
        if not res.success:
            return None
        sel = {k for k in range(n) if res.x[k] > 0.5}
        h = nx.Graph()
        h.add_nodes_from(sel)
        h.add_edges_from((i, j) for i, j in model["edges"] if i in sel and j in sel)
        comps = [cc for cc in nx.connected_components(h) if root not in cc]
        if not comps:
            return sel - set(s1)
        for cc in comps:
            cut(cc)
    raise RuntimeError("connectivity cuts did not converge in 2000 rounds")


def lexi(model: dict[str, Any], need: dict[str, list[int]], **kw: Any) -> set[int] | None:
    """Capex first, then corridor count at that capex (A-r6-133)."""
    tol = float(_v(params()["search"]["tie_tol_sar_m"]))
    s = solve(model, need, **kw)
    if s is None:
        return None
    cap = sum(model["fast"].capex[model["nodes"][k]["opt"], 0] for k in s)
    s2 = solve(model, need, capex_cap=cap + tol, count_obj=True, **kw)
    return s2 if s2 is not None else s


def items_of(model: dict[str, Any], sel: set[int]) -> list[dict[str, Any]]:
    from optimise import search as se

    fast = model["fast"]
    out = []
    for k in sorted(sel, key=lambda k: model["nodes"][k]["name"]):
        nd = model["nodes"][k]
        out.append(
            {"id": nd["id"], "phase": se.PHASES[best_phase(fast, nd["opt"])], **nd["variant"]}
        )
    return out


def blocks(model: dict[str, Any], sel: set[int], root: Path = REPO_ROOT) -> dict[str, Any]:
    """Library building blocks per option and the fast-mode sums (A-r6-006)."""
    from optimise import search as se

    fast = model["fast"]
    rows = []
    reach_any = np.zeros_like(fast.reach["120"][0], dtype=bool)
    for k in sorted(sel, key=lambda k: model["nodes"][k]["name"]):
        nd = model["nodes"][k]
        o = nd["opt"]
        j = best_phase(fast, o)
        sc = json.loads((root / se.LIB / nd["name"] / "score.json").read_text())
        cx = sc["capex_sar_m"]
        rob = (fast.pvb[o] - fast.pvc[o]).min(axis=1)
        reach_any |= fast.reach["120"][o]
        c = materialise({"id": nd["id"], **nd["variant"]}, root)
        rows.append(
            {
                "id": nd["id"],
                "option": nd["name"],
                "variant": nd["variant"],
                "family": c.get("family"),
                "best_phase": se.PHASES[j],
                "robust_npv_best_phase": round(float(rob[j]), 1),
                "robust_npv_2030": round(float(rob[0]), 1),
                "capex_p10": round(float(cx["capex_p10"]), 1),
                "capex_p50": round(float(cx["capex_p50"]), 1),
                "capex_p90": round(float(cx["capex_p90"]), 1),
                "reach_gain_120_alone": round(
                    float(fast.reach["120"][o].any(axis=0) @ fast.popv), 0
                ),
                "route_km": 0.0 if c.get("family") == "station_addition" else float(c["length_km"]),
            }
        )
    tot = {
        # A-r6-006: min over the population cases of the summed corridor NPVs (not the sum of
        # each corridor's own minimum, which is listed per row)
        "robust_npv_fast": round(
            fast.score(fast.genome_of({"corridors": items_of(model, sel)}))["robust_npv"], 1
        ),
        "robust_npv_sum_of_row_minima": round(sum(r["robust_npv_best_phase"] for r in rows), 1),
        "capex_p10_sum": round(sum(r["capex_p10"] for r in rows), 1),
        "capex_p50_sum": round(sum(r["capex_p50"] for r in rows), 1),
        "capex_p90_sum": round(sum(r["capex_p90"] for r in rows), 1),
        "reach_gain_120_union": round(float(reach_any.any(axis=0) @ fast.popv), 0),
        "n_corridors": len(rows),
        "route_km": round(sum(r["route_km"] for r in rows), 1),
        "label": FAST_LABEL,
    }
    return {"rows": rows, "totals": tot}


def check(items: list[dict[str, Any]], root: Path = REPO_ROOT) -> dict[str, Any]:
    """Re-check a layout on the real graph: components and the city tests."""
    g = rail_graph(items, root)
    cc = components(g)
    refs = city_refs(root)
    main = cc[0]
    cities = {c: on_graph(g, main, r) | {"required": r["required"]} for c, r in refs.items()}
    return {
        "n_components": len(cc),
        "cities": cities,
        "all_required_on_graph": all(v["on_graph"] for v in cities.values() if v["required"]),
    }


def joins(model: dict[str, Any], sel: set[int], root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """For each S1 island (component 1..): the interchange edges from its lines (stations
    inserted by station additions included) to a chosen corridor, with distance and rule."""
    g = rail_graph(items_of(model, sel), root)
    g1 = rail_graph([], root)
    out = []
    for k, c in enumerate(components(g1)):
        if k == 0:
            continue
        lines = {g1.nodes[n]["line"] for n in c}
        for u, v, d in g.edges(data=True):
            if d.get("kind") != "interchange":
                continue
            for a, b in ((u, v), (v, u)):
                if g.nodes[a]["line"] in lines and g.nodes[b]["line"] not in lines:
                    out.append(
                        {
                            "island": k,
                            "island_lines": sorted(lines),
                            "island_station": a,
                            "inserted_by_station_addition": a not in c,
                            "joined_by": b,
                            "joined_line": g.nodes[b]["line"],
                            "km": round(float(d["km"]), 3),
                            "rule": d["reason"],
                        }
                    )
    return out


def ties(
    model: dict[str, Any], sel: set[int], need: dict[str, list[int]], tol: float, root: Path
) -> list[dict[str, Any]]:
    """Equal-capex swaps of one chosen option for an unchosen one (within tol) that keep the
    set feasible on the real graph: recorded as ties (A-r6-133), not as alternatives."""
    fast, nodes = model["fast"], model["nodes"]
    cap = {
        k: float(fast.capex[nodes[k]["opt"], 0])
        for k, nd in enumerate(nodes)
        if nd["kind"] == "opt"
    }
    ids = {nodes[k]["id"] for k in sel}
    out = []
    for s in sorted(sel, key=lambda k: nodes[k]["name"]):
        subs = []
        for t, ct in sorted(cap.items(), key=lambda kv: nodes[kv[0]]["name"]):
            if nodes[t]["id"] in ids or abs(ct - cap[s]) > tol or nodes[t]["variant"]:
                continue
            alt = (sel - {s}) | {t}
            ch = check(items_of(model, alt), root)
            if ch["n_components"] == 1 and ch["all_required_on_graph"]:
                subs.append(nodes[t]["name"])
        if subs:
            out.append(
                {
                    "chosen": nodes[s]["name"],
                    "capex_p50": round(cap[s], 1),
                    "equal_capex_substitutes": subs,
                }
            )
    return out


# --------------------------------------------------------------------------- CLI
@app.command("components")
def components_cmd(out: Path = typer.Option(Path("runs/r6/l6")), seed: int = seed_option()) -> None:
    """Component count and gaps of S1 and S6-L1..L5 (current rules)."""
    t0 = time.monotonic()
    out.mkdir(parents=True, exist_ok=True)
    res = {"label": LABEL, "S1": summary(rail_graph([]))}
    for sid in LAYOUTS:
        res[sid] = summary(rail_graph(scenario_items(sid)))
    (out / "components.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    for k, v in res.items():
        if k != "label":
            typer.echo(f"{k}: {v['n_components']} components")
    write_meta(out, seed, {"cmd": "components"}, {"seconds": round(time.monotonic() - t0, 1)})


@app.command("search")
def search_cmd(out: Path = typer.Option(Path("runs/r6/l6")), seed: int = seed_option()) -> None:
    """Smallest connecting set + the next two sets; with and without the chord-band corridors."""
    t0 = time.monotonic()
    out.mkdir(parents=True, exist_ok=True)
    p = params()
    model = item_model()
    refs = city_refs()
    req = {c: r for c, r in refs.items() if r["required"]}
    need = covers(model, req)
    chord = set(p["search"]["chord_band"])
    res: dict[str, Any] = {"label": LABEL, "fast_label": FAST_LABEL, "refs": refs, "runs": {}}
    for tag, excl in (("all", set()), ("no_chord_band", chord), ("base_only", None)):
        if excl is None:  # base corridors only (no v3 variant), chord band excluded
            ex = chord
            model_b = {**model}
            keep = [
                k for k, nd in enumerate(model["nodes"]) if nd["kind"] == "s1" or not nd["variant"]
            ]
            remap = {k: i for i, k in enumerate(keep)}
            model_b["nodes"] = [model["nodes"][k] for k in keep]
            model_b["edges"] = [
                (remap[i], remap[j]) for i, j in model["edges"] if i in remap and j in remap
            ]
            need_b = {c: [remap[k] for k in ks if k in remap] for c, ks in need.items()}
            mdl, nd_ = model_b, need_b
        else:
            ex, mdl, nd_ = excl, model, need
        sets, forbid = [], []
        tol = float(_v(p["search"]["tie_tol_sar_m"]))
        for _ in range(1 + int(_v(p["search"]["alternatives"]))):
            s = lexi(mdl, nd_, exclude_ids=ex, forbid=forbid)
            if s is None:
                break
            ids = {mdl["nodes"][k]["id"] for k in s}
            its = items_of(mdl, s)
            sets.append(
                {
                    "items": its,
                    "blocks": blocks(mdl, s),
                    "check": check(its),
                    "joins": joins(mdl, s),
                    "ties": ties(mdl, s, nd_, tol, REPO_ROOT),
                    "uses_chord_band": sorted(ids & chord),
                }
            )
            # the next set drops at least one LINE corridor of every earlier set (station
            # additions of equal capex are ties, recorded above)
            forbid.append({i for i in ids if not i.startswith("S5-")})
        res["runs"][tag] = sets
        for k, s in enumerate(sets):
            t = s["blocks"]["totals"]
            typer.echo(
                f"{tag} #{k}: {t['n_corridors']} corridors, capex P50 {t['capex_p50_sum']:,.0f}, "
                f"fast robust NPV {t['robust_npv_fast']:,.0f}, components "
                f"{s['check']['n_components']}, cities ok {s['check']['all_required_on_graph']}"
            )
    # sensitivity: Ha'il and Ar Rass required too (reported cities), chord band excluded
    need_r = covers(model, refs)
    s = lexi(model, need_r, exclude_ids=chord)
    if s is not None:
        its = items_of(model, s)
        res["runs"]["with_reported_cities"] = [
            {
                "items": its,
                "blocks": blocks(model, s),
                "check": check(its),
                "joins": joins(model, s),
                "ties": [],
                "uses_chord_band": [],
            }
        ]
        t = res["runs"]["with_reported_cities"][0]["blocks"]["totals"]
        typer.echo(
            f"with_reported_cities: {t['n_corridors']} corridors, "
            f"capex P50 {t['capex_p50_sum']:,.0f}"
        )
    (out / "search.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    write_meta(
        out, seed, {"cmd": "search", "params": p}, {"seconds": round(time.monotonic() - t0, 1)}
    )


SCENARIO = Path("scenarios/S6-L6.yaml")
# display only: label offsets (points) where two city labels would overlap
LABEL_OFFSETS = {"Jeddah": (-5, 2, "right"), "Makkah": (4, -9, "left")}
MAP = Path("docs/report/figures/s6-l6-connected-map.png")


def chosen(res: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """L6 = the minimum set without the FIX_HHR chord-band corridors (item 4)."""
    sets = res["runs"].get("no_chord_band") or []
    if not sets:
        raise RuntimeError("no connecting set without the chord-band corridors (blocked)")
    return "no_chord_band", sets[0]


def corridor_file(cid: str) -> str:
    fam = {"S2": "trunk_gap", "S3": "branch_spur", "S4": "commuter_belt", "S5": "station_addition"}
    return str(CORRIDORS / fam[cid[:2]] / f"{cid}.yaml")


def scenario_doc(items: list[dict[str, Any]], totals: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "S6-L6",
        "kind": "comparison_layout",
        "title": (
            "S6-L6 (S6_L6_CONNECTED, hypothetical): one connected rail system: the smallest "
            "set of library corridors that joins S1's three components and puts the required "
            "cities on the graph (comparison layout, not the recommended programme)"
        ),
        "label": "comparison layout, not the recommended programme",
        "layer": "hypothetical (ours)",
        "layers": ["existing", "committed", "hypothetical"],
        "baseline": "S1",
        "lines": {
            "include": [
                "hhr",
                "sar-north-passenger",
                "sar-east-passenger",
                "riyadh-metro",
                "landbridge",
                "riyadh-rail-link",
                "gcc-railway-ksa",
            ]
        },
        "candidates": [corridor_file(c["id"]) for c in items],
        "layout": {
            "corridors": items,
            "phase_rule": "construction starts phase - 3 (A-r6-002)",
            "phase_choice": (
                "each option's best single-corridor library phase (highest robust NPV, "
                "runs/r6/v3/library; A-r6-134), not optimised as a layout"
            ),
            "variant_fields": (
                "electrified: false = the costed R6_V3 non-electrified variant (A-r6-101 (b)); "
                "chosen because it has the lowest capex P50 (A-r6-133)"
            ),
        },
        "connectivity": {
            "components": 1,
            "rules": (
                "network.graph interchange rules unchanged: walk 0.4 km (A-r1a-030), same name "
                "3.0 km (A-r1a-032); A-r6-130"
            ),
        },
        "fast_mode_totals": {k: v for k, v in totals.items() if k != "label"},
        "fast_mode_label": FAST_LABEL,
        "population_scenario": "un_wpp_low / un_wpp_medium / un_wpp_high (robust = minimum)",
        "gigaproject_addon": "none",
        "seed": 1,
        "sensitivity": {"band": "P10/P50/P90", "draws": 10000},
        "labels": [LABEL],
        "source": (
            "S6_L6_CONNECTED search (optimise/connect.py; runs/r6/l6/search.json); building "
            "blocks = R6_V3 single-corridor library (judge v3-variants); NOT scored by the judge"
        ),
        "demand_params": "cities/ksa/assumptions/demand.yaml",
        "mode_choice_params": "cities/ksa/assumptions/modechoice.yaml",
        "costs": "cities/ksa/costs/cost_register.yaml",
        "appraisal": "cities/ksa/assumptions/appraisal.yaml",
    }


def join_paths(items: list[dict[str, Any]], root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Per S1 island: the shortest station path (fewest graph edges) on the L6 graph from the
    island to the S1 main component, and the layout corridors and inserted stations on it."""
    g = rail_graph(items, root)
    g1 = rail_graph([], root)
    s1_lines = {g1.nodes[m]["line"] for m in g1}
    cc = components(g1)
    out = []
    for k, c in enumerate(cc[1:], 1):
        h = nx.Graph(g)
        h.add_edges_from(("_src", n) for n in c)
        h.add_edges_from((n, "_dst") for n in cc[0])
        path = nx.shortest_path(h, "_src", "_dst")[1:-1]
        via: list[str] = []
        for n in path:
            ln = g.nodes[n]["line"]
            if ln in s1_lines and n not in g1:
                via.append(f"inserted station {n}")
            elif ln not in s1_lines and ln not in via:
                via.append(ln)
        out.append(
            {
                "island": k,
                "island_lines": sorted({g1.nodes[n]["line"] for n in c}),
                "path": path,
                "via": via,
            }
        )
    return out


def attachments(items: list[dict[str, Any]], root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Every interchange edge between an S1 line (any component; inserted station-addition
    stations included) and a layout line, with the S1 component it belongs to."""
    g = rail_graph(items, root)
    g1 = rail_graph([], root)
    comp = {g1.nodes[n]["line"]: k for k, c in enumerate(components(g1)) for n in c}
    out = []
    for u, v, d in g.edges(data=True):
        if d.get("kind") != "interchange":
            continue
        for a, b in ((u, v), (v, u)):
            la, lb = g.nodes[a]["line"], g.nodes[b]["line"]
            if la in comp and lb not in comp:
                out.append(
                    {
                        "s1_component": comp[la],
                        "s1_station": a,
                        "s1_station_name": g.nodes[a]["name_en"],
                        "layout_station": b,
                        "km": round(float(d["km"]), 3),
                        "rule": d["reason"],
                    }
                )
    return sorted(out, key=lambda r: (r["s1_component"], r["s1_station"], r["layout_station"]))


@app.command("scenario")
def scenario_cmd(out: Path = typer.Option(Path("runs/r6/l6"))) -> None:
    """Write scenarios/S6-L6.yaml (and runs/r6/l6/L6.layout.yaml) from the search result."""
    res = json.loads((out / "search.json").read_text())
    _, best = chosen(res)
    doc = scenario_doc(best["items"], best["blocks"]["totals"])
    Scenario.model_validate(doc)
    head = (
        "# Scenario S6-L6 - one connected rail system (hypothetical layer; corridors are ours, "
        "not announced). COMPARISON LAYOUT, NOT THE RECOMMENDED PROGRAMME. Schema: "
        ".claude/skills/scenario-yaml/SKILL.md.\n# Label: " + LABEL + ".\n"
    )
    (REPO_ROOT / SCENARIO).write_text(
        head + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100)
    )
    lay = {"id": "S6-L6", "layer": "hypothetical", "base": "S1", "label": LABEL}
    lay["corridors"] = best["items"]
    (out / "L6.layout.yaml").write_text(yaml.safe_dump(lay, sort_keys=False))
    att = {
        "label": LABEL,
        "attachments": attachments(best["items"]),
        "join_paths": join_paths(best["items"]),
    }
    (out / "attachments.json").write_text(json.dumps(att, indent=1, ensure_ascii=False) + "\n")
    typer.echo(str(SCENARIO))


def _route_km(items: list[dict[str, Any]]) -> float:
    km = 0.0
    for it in items:
        c = materialise(it)
        if c.get("family") != "station_addition":
            km += float(c["length_km"])
    return round(km, 1)


@app.command("compare")
def compare_cmd(out: Path = typer.Option(Path("runs/r6/l6")), seed: int = seed_option()) -> None:
    """L6 vs S6-L1..L5: fast-mode robust NPV, capex P50 vs B1/B2/B3, 120-min reach (union of
    library reach sets), components, corridor count, new route-km; national reach (reported
    only) through optimise/reach.py on the judge v3 files (no scoring)."""
    import subprocess

    import pandas as pd

    from optimise import search as se
    from optimise import variants as va

    t0 = time.monotonic()
    res = json.loads((out / "search.json").read_text())
    comp = json.loads((out / "components.json").read_text())
    _, best = chosen(res)
    fast = va.FastV()
    top5 = pd.read_csv(REPO_ROOT / "runs/r6/top5/top5.csv").set_index("layout")
    budgets = se.budgets()
    rows = []
    l6_items = best["items"]
    for sid in (*LAYOUTS, "S6-L6"):
        items = scenario_items(sid) if sid != "S6-L6" else l6_items
        sc = fast.score(fast.genome_of({"corridors": items}))
        row = {
            "layout": sid,
            "robust_npv_fast": round(sc["robust_npv"], 0),
            "capex_p50": round(sc["capex_p50"], 0),
            "reach_gain_120_union": round(sc["access_gain_120"], 0),
            "n_corridors": len(items),
            "new_route_km": _route_km(items),
            "components": 1 if sid == "S6-L6" else comp[sid]["n_components"],
        }
        for b, v in budgets.items():
            row[f"within_{b}"] = sc["capex_p50"] <= v
        key = sid
        if key in top5.index:
            row["robust_npv_full_judge_published"] = float(top5.loc[key, "robust_npv"])
            row["national_reach_120_published"] = float(
                top5.loc[key, "national_reach_120_reported_only"]
            )
            row["national_reach_gain_120_published"] = float(
                top5.loc[key, "national_reach_gain_120_reported_only"]
            )
        rows.append(row)
    # national reach for L6: the R6_V3 harness (reported only, never a score; A-r6-104)
    reach_json = out / "national_reach.json"
    judge = REPO_ROOT / "judge" / se.JUDGE
    subprocess.run(
        [
            str(REPO_ROOT / ".venv/bin/python"),
            str(REPO_ROOT / "optimise/reach.py"),
            "--layouts",
            str((out / "L6.layout.yaml").resolve()),
            "--out",
            str(reach_json.resolve()),
        ],
        cwd=REPO_ROOT,
        env={**__import__("os").environ, "R6_JUDGE_ROOT": str(judge)},
        check=True,
    )
    nr = json.loads(reach_json.read_text())
    lay = next(iter(nr["layouts"].values()))
    rows[-1]["national_reach_120"] = lay["layout"]["120"]
    rows[-1]["national_reach_gain_120"] = lay["gain"]["120"]
    rows[-1]["national_reach_60"] = lay["layout"]["60"]
    rows[-1]["national_reach_gain_60"] = lay["gain"]["60"]
    doc = {"label": LABEL, "fast_label": FAST_LABEL, "budgets": budgets, "rows": rows}
    (out / "compare.json").write_text(json.dumps(doc, indent=1) + "\n")
    pd.DataFrame(rows).to_csv(out / "compare.csv", index=False)
    typer.echo(pd.DataFrame(rows).to_string(index=False))
    write_meta(out, seed, {"cmd": "compare"}, {"seconds": round(time.monotonic() - t0, 1)})


@app.command("map")
def map_cmd(
    out: Path = typer.Option(Path("runs/r6/l6")), dest: Path = typer.Option(REPO_ROOT / MAP)
) -> None:
    """The one component (fig01 map family, common.figures): S1 layers, the L6 corridors in one
    colour, the joining corridors highlighted, the required cities annotated; OSM credit."""
    import geopandas as gpd
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    from common import figures as cf

    res = json.loads((out / "search.json").read_text())
    _, best = chosen(res)
    items = best["items"]
    jp = json.loads((out / "attachments.json").read_text())["join_paths"]
    via = [v for p in jp for v in p["via"]]
    join_ids = {v.rsplit("-v", 1)[0] for v in via if v.startswith("S")}
    join_sa = {v.split()[-1].split(":")[1] for v in via if v.startswith("inserted station")}
    cf.register_fonts()
    fig, ax = plt.subplots(figsize=(10, 9.4), dpi=110)
    comp_col, join_col = "#1a7f64", "#e07b00"
    # one colour under everything in the component (S1 existing + committed and the layout)
    for layer in ("existing", "committed"):
        g = gpd.read_file(REPO_ROOT / cf.LINES / f"{layer}.geojson")
        g.plot(ax=ax, color=comp_col, lw=6, alpha=0.22, zorder=2)
    handles = cf._base_layers(ax)
    for it in items:
        if it["id"].startswith("S5-"):
            continue
        al = gpd.read_file(REPO_ROOT / cf.ALIGNMENTS / f"{it['id']}.geojson")
        if "kind" in al.columns:
            al = al[al["kind"] == "routed"]
        al.plot(ax=ax, color=comp_col, lw=6, alpha=0.22, zorder=2)
        hl = it["id"] in join_ids
        al.plot(ax=ax, color=join_col if hl else comp_col, lw=3.0 if hl else 2.0, zorder=5)
    sa = []
    for it in items:
        if it["id"].startswith("S5-"):
            d = yaml.safe_load((REPO_ROOT / corridor_file(it["id"])).read_text())
            sa += [(s, s["id"] in join_sa) for s in d["stations"] if s.get("class") == "planned"]
    for s, hl in sa:
        ax.scatter(
            s["lon"],
            s["lat"],
            marker="*",
            s=150,
            color=join_col if hl else comp_col,
            edgecolor="white",
            lw=0.5,
            zorder=8,
        )
    chk = best["check"]["cities"]
    refs = city_refs()
    for city, r in refs.items():
        ok = chk[city]["on_graph"]
        ax.scatter(r["lon"], r["lat"], s=18, color="black" if ok else "#b00020", zorder=9)
        lab = city + ("" if r["required"] else " (reported)") + ("" if ok else ": not on graph")
        ax.annotate(
            lab,
            (r["lon"], r["lat"]),
            xytext=LABEL_OFFSETS.get(city, (4, 3, "left"))[:2],
            ha=LABEL_OFFSETS.get(city, (4, 3, "left"))[2],
            textcoords="offset points",
            fontsize=6.8,
            zorder=10,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.7, "pad": 0.6},
        )
    cf._aspect(ax, 24.0)
    ax.set_axis_off()
    cf._osm(ax)
    handles += [
        Line2D(
            [],
            [],
            color=comp_col,
            lw=2.0,
            label=cf.LAYER_NAME["hypothetical"] + ": S6-L6 corridors",
        ),
        Line2D(
            [],
            [],
            color=join_col,
            lw=3.0,
            label="hypothetical (ours): corridors joining an S1 island",
        ),
        Line2D(
            [],
            [],
            color=join_col,
            marker="*",
            ls="",
            markersize=10,
            label="hypothetical (ours): station addition joining an island",
        ),
        Line2D(
            [],
            [],
            color=comp_col,
            marker="*",
            ls="",
            markersize=10,
            label="hypothetical (ours): station addition",
        ),
        Line2D([], [], color=comp_col, lw=6, alpha=0.22, label="the one connected component"),
        Line2D(
            [],
            [],
            color="black",
            marker="o",
            ls="",
            markersize=4,
            label="city reference point (on the graph)",
        ),
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        fontsize=7,
        title="rail layers (never mixed)",
        title_fontsize=7.5,
        framealpha=0.9,
    )
    t = best["blocks"]["totals"]
    ax.set_title(
        "S6-L6: one connected rail system (comparison layout, not the recommended programme)",
        fontsize=10,
    )
    fig.text(
        0.01,
        0.01,
        f"{LABEL}. {t['n_corridors']} library corridors; components: 1 (S1: 3). "
        "Interchange rules unchanged (walk 0.4 km, same name 3.0 km).\n"
        f"Alignment limitation: {ALIGNMENT_LIMITATION}.",
        fontsize=6.3,
        va="bottom",
        wrap=True,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=110, metadata={"Software": None})
    plt.close(fig)
    typer.echo(f"{dest} {dest.stat().st_size / 1024:.0f} KB")


SCORE_PATHS = ("score.json", "meta.json")


def score_row(
    s: dict[str, Any],
    name: str,
    nr: dict[str, Any],
    layout: dict[str, Any],
    root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """One row in the runs/r6/top5/top5.csv columns (optimise.report scorecards + report_v3 top5)
    from a full-judge all-case score.json and the reported-only national reach."""
    import pandas as pd

    pops = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
    ar = pd.DataFrame(s["appraisal_rows"])
    med = ar[ar.population == "un_wpp_medium"]
    sens = {
        f"{r.rate_case}/{r.horizon}y": r.npv_at_p50_cost
        for r in med.itertuples()
        if r.horizon == 60 or r.rate_case == "greenbook_2026"
    }
    loads = s.get("loads_2050_medium") or {}
    loads1 = s.get("loads_2050_medium_S1") or {}
    rk = sum(
        float(json.loads((root / "cities/ksa/alignments" / f"{c}.json").read_text())["length_km"])
        for c in s["corridors"]
        if not c.startswith("S5-") and (root / "cities/ksa/alignments" / f"{c}.json").exists()
    )
    dtrips = (s["rail_trips_2050_medium"] or 0) - (s["rail_trips_2050_medium_S1"] or 0)
    return {
        "layout": name,
        "corridors": len(s["corridors"]),
        "robust_npv": s["robust_npv"],
        **{f"npv_p50cost_{p.split('_')[-1]}": s["npv_at_p50_cost"][p] for p in pops},
        **{f"npv_p90cost_{p.split('_')[-1]}": s["npv_at_p90_cost"][p] for p in pops},
        "npv_draws_p10_medium": s["npv_p10"]["un_wpp_medium"],
        "npv_draws_p50_medium": s["npv_p50"]["un_wpp_medium"],
        "npv_draws_p90_medium": s["npv_p90"]["un_wpp_medium"],
        "bcr_p10_medium": s["bcr_p10"]["un_wpp_medium"],
        "bcr_p50_medium": s["bcr_p50"]["un_wpp_medium"],
        "bcr_p90_medium": s["bcr_p90"]["un_wpp_medium"],
        "pv_wei_indicative_medium": s["pv_wei_p50_indicative"]["un_wpp_medium"],
        **dict(s["capex_sar_m"].items()),
        "rail_trips_2050_medium": s["rail_trips_2050_medium"],
        "added_rail_trips_2050_medium": dtrips,
        "added_rail_pkm_m_2050_medium": (s["rail_pkm_m_2050_medium"] or 0)
        - (s["rail_pkm_m_2050_medium_S1"] or 0),
        "new_route_km": rk,
        "added_trips_per_new_route_km": dtrips / rk if rk else None,
        "access_gain_60": s.get("access_gain_60"),
        "access_gain_120": s.get("access_gain_120"),
        "co2_pv_p50_medium": float(
            med[(med.horizon == 60) & (med.rate_case == "greenbook_2026")].pv_carbon_p50.iloc[0]
        ),
        "hhr_pax_2050": (loads.get("hhr") or {}).get("passengers"),
        "hhr_pax_2050_S1": (loads1.get("hhr") or {}).get("passengers"),
        "landbridge_pax_2050": (loads.get("landbridge") or {}).get("passengers"),
        "landbridge_pax_2050_S1": (loads1.get("landbridge") or {}).get("passengers"),
        "flags": "; ".join(s.get("flags", [])),
        "phases": json.dumps(s["phases"]),
        **{f"sens_{k}": v for k, v in sens.items()},
        "national_reach_60_reported_only": nr["population_2025_within_min"]["60"],
        "national_reach_120_reported_only": nr["population_2025_within_min"]["120"],
        "national_reach_gain_120_reported_only": nr["gain_vs_S1"]["120"],
        "national_reach_gain_60_reported_only": nr["gain_vs_S1"]["60"],
        "variants": json.dumps([c for c in layout["corridors"] if set(c) - {"id", "phase"}]),
    }


@app.command("score")
def score_cmd(
    out: Path = typer.Option(Path("runs/r6/l6/score")),
    reach_file: Path = typer.Option(Path("runs/r6/l6/national_reach.json")),
    layout: Path = typer.Option(Path("runs/r6/l6/L6.layout.yaml")),
) -> None:
    """Post-judge bookkeeping for the S6-L6 full-judge score (S6_L6_SCORE): the national reach
    (reported only, A-r6-104) added to score.json as report_v3 did for L1-L5 (the judge's own
    file is kept as score.judge.json), the layout hash in meta.json, the scorecard row
    S6-L6.csv and the map S6-L6-map.png. Never runs the judge; never writes runs/r6/top5/."""
    import pandas as pd

    from optimise import report
    from optimise import search as se

    out, reach_file, layout = (REPO_ROOT / p for p in (out, reach_file, layout))
    if "top5" in out.parts:
        raise typer.BadParameter("S6-L6 is not a top-5 layout: never write runs/r6/top5/")
    sp, raw = out / "score.json", out / "score.judge.json"
    if not raw.exists():
        raw.write_bytes(sp.read_bytes())
    s = json.loads(raw.read_text())
    r = json.loads(reach_file.read_text())
    lr = next(v for k, v in r["layouts"].items() if Path(k).name == layout.name)
    s["national_reach_reported_only"] = {
        "note": "reported column only, never in the score (CP7-5, A-r6-104); "
        "added by optimise.connect score after the judge run",
        "population_2025_within_min": {b: lr["layout"][b] for b in ("60", "120")},
        "S1_population_2025_within_min": {b: r["S1"][b] for b in ("60", "120")},
        "gain_vs_S1": lr["gain"],
        "within_120_with_access_cap": lr["layout"]["120_within_access_cap"],
        "population_total_2025": r["population_total_2025"],
    }
    sp.write_text(json.dumps(s, indent=1, default=float) + "\n")
    lay = yaml.safe_load(layout.read_text())
    mp = out / "meta.json"
    m = json.loads(mp.read_text())
    m["layout_hash"] = se.layout_hash(lay)
    m["layout_file"] = str(layout.relative_to(REPO_ROOT))
    mp.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    row = score_row(s, "S6-L6", s["national_reach_reported_only"], lay)
    pd.DataFrame([row]).to_csv(out / "S6-L6.csv", index=False)
    report.layout_map(
        lay,
        out / "S6-L6-map.png",
        f"S6-L6 (comparison layout, not the recommended programme): robust NPV "
        f"{s['robust_npv']:,.0f}, capex P50 {s['capex_sar_m']['capex_p50']:,.0f} SAR m",
        note=f"Full judge v3, seed 1. Alignment limitation: {ALIGNMENT_LIMITATION}.",
    )
    typer.echo(json.dumps({k: row[k] for k in ("robust_npv", "capex_p50", "access_gain_120")}))


if __name__ == "__main__":
    app()
