"""Scenario rail graph from line YAMLs.

uv run python -m network.graph build --scenario scenarios/S0.yaml --out runs/graph/S0/ --seed 1
uv run python -m network.graph check --scenario scenarios/S1.yaml        (validate only)

Loads `scenarios/<S>.yaml` (common.schemas.Scenario) and each id in `lines.include` from
`<lines-dir>/<id>.yaml` (common.schemas.LineSpec). A line whose `layer` is not in the scenario's
`layers` is an error (rule 5); S0 may contain no committed line.

Graph (NetworkX MultiGraph, undirected: every line runs both ways):
- nodes `<line_id>:<station_id>` with name_en, name_ar, lat, lon, layer, line, class, km_post;
- `line` edges between consecutive stations in list order (branches are separate lines or follow
  list order), km = km_post difference (great-circle fallback if not positive, flagged),
  `run_min` = pure-kinematics stop-to-stop minutes (accelerate, cruise, brake; see
  `segment_minutes`), `dwell_min` = the dwell at the arriving station, `min` = run_min + dwell_min;
- `interchange` edges between stations of different lines within `walk_max_km` (A-r1a-030) or with
  the same normalised name within `same_name_max_km` (A-r1a-032); walk minutes at A-r1a-031.
Running-time parameters come from the line's `running_time_model` (cruise_kmh, accel_ms2,
decel_ms2, dwell_s), cruise falls back to `design_speed_kmh`, the rest to graph_params.yaml
defaults (A-r1a-033..035). The source of each parameter is recorded on the edge.

Outputs: graph.json (node-link), nodes.parquet, edges.parquet, summary.json, meta.json.
"""

from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta
from common.schemas import LineSpec, Scenario
from network.geo import KNearest, haversine_km

PARAMS_YAML = Path(__file__).with_name("graph_params.yaml")
LINES_DIR = REPO_ROOT / "cities" / "ksa" / "lines"
ALIASES = {
    "cruise_kmh": ("cruise_kmh", "v_max_kmh", "max_speed_kmh", "cruise"),
    "accel_ms2": ("accel_ms2", "accel", "acceleration_ms2"),
    "decel_ms2": ("decel_ms2", "decel", "deceleration_ms2"),
    "dwell_s": ("dwell_s", "dwell", "dwell_sec"),
}
app = typer.Typer(add_completion=False, help="Scenario rail graphs from line YAMLs.")


class LayerError(ValueError):
    """A scenario includes a line from a layer it does not allow."""


def load_params(path: Path = PARAMS_YAML) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def load_scenario(path: Path) -> Scenario:
    return Scenario.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def load_line(lines_dir: Path, line_id: str) -> LineSpec:
    p = Path(lines_dir) / f"{line_id}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"line {line_id}: {p} not found")
    spec = LineSpec.model_validate(yaml.safe_load(p.read_text(encoding="utf-8")))
    if spec.id != line_id:
        raise ValueError(f"{p}: id {spec.id!r} does not match the file name {line_id!r}")
    return spec


def expand_ids(include: list[str], lines_dir: Path) -> tuple[list[str], dict[str, list[str]]]:
    """Resolve scenario line ids: an exact `<id>.yaml` wins; otherwise the group `<id>-*.yaml`
    (sorted) is used, e.g. `riyadh-metro` -> riyadh-metro-l1 ... -l6. Returns (ids, expansions)."""
    ids: list[str] = []
    expansions: dict[str, list[str]] = {}
    for i in include:
        if (Path(lines_dir) / f"{i}.yaml").exists():
            ids.append(i)
            continue
        group = sorted(p.stem for p in Path(lines_dir).glob(f"{i}-*.yaml"))
        if not group:
            raise FileNotFoundError(f"line {i}: no {i}.yaml and no {i}-*.yaml in {lines_dir}")
        expansions[i] = group
        ids.extend(group)
    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        raise ValueError(f"line ids included twice after expansion: {dup}")
    return ids, expansions


def scenario_lines(scn: Scenario, lines_dir: Path) -> list[LineSpec]:
    ids, _ = expand_ids(scn.lines.include, lines_dir)
    lines = [load_line(lines_dir, i) for i in ids]
    for ln in lines:
        if ln.layer not in scn.layers:
            raise LayerError(
                f"scenario {scn.id} allows layers {scn.layers} but line {ln.id} is {ln.layer!r}"
            )
        if scn.id == "S0" and ln.layer == "committed":
            raise LayerError(f"S0 may not contain committed line {ln.id}")
    return lines


# --------------------------------------------------------------------------- kinematics
def segment_minutes(km: float, cruise_kmh: float, accel_ms2: float, decel_ms2: float) -> float:
    """Stop-to-stop minutes: accelerate at `accel` to cruise, cruise, brake at `decel`.

    If the segment is too short to reach cruise, the train peaks at
    v_p = sqrt(2 L a b / (a + b)) and t = v_p / a + v_p / b. Dwell is not included.
    """
    if km <= 0:
        return 0.0
    if not (cruise_kmh > 0 and accel_ms2 > 0 and decel_ms2 > 0):
        return math.nan
    length, v, a, b = km * 1000.0, cruise_kmh / 3.6, accel_ms2, decel_ms2
    d_ab = v * v / (2 * a) + v * v / (2 * b)
    if length >= d_ab:
        t = v / a + v / b + (length - d_ab) / v
    else:
        vp = math.sqrt(2 * length * a * b / (a + b))
        t = vp / a + vp / b
    return t / 60.0


def running_params(line: LineSpec, params: dict[str, Any]) -> dict[str, tuple[float, str]]:
    """{name: (value, provenance)} for cruise_kmh, accel_ms2, decel_ms2, dwell_s."""
    rtm = line.running_time_model or {}
    out: dict[str, tuple[float, str]] = {}
    for name, keys in ALIASES.items():
        for k in keys:
            if k in rtm and rtm[k].value is not None:
                out[name] = (float(rtm[k].value), f"line:running_time_model.{k}")
                break
    if "cruise_kmh" not in out and line.design_speed_kmh:
        out["cruise_kmh"] = (float(line.design_speed_kmh), "line:design_speed_kmh")
    if "cruise_kmh" not in out:
        out["cruise_kmh"] = (math.nan, "missing")
    for name, d in params["running_time_defaults"].items():
        if name not in out:
            out[name] = (float(d["value"]), f"default:{d['assumption_id']}")
    return out


# --------------------------------------------------------------------------- build
def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def build_graph(lines: list[LineSpec], params: dict[str, Any] | None = None) -> nx.MultiGraph:
    params = params or load_params()
    g = nx.MultiGraph()
    for ln in lines:
        rp = running_params(ln, params)
        prev = None
        for st in ln.stations:
            nid = f"{ln.id}:{st.id}"
            if nid in g:
                raise ValueError(f"duplicate node {nid}")
            g.add_node(
                nid,
                kind="station",
                line=ln.id,
                station=st.id,
                layer=ln.layer,
                name_en=st.name_en,
                name_ar=st.name_ar,
                lat=st.lat,
                lon=st.lon,
                station_class=st.class_,
                km_post=st.km_post,
            )
            if prev is not None:
                gc = float(haversine_km(prev.lat, prev.lon, st.lat, st.lon))
                km = st.km_post - prev.km_post
                km_method = "km_post"
                if km <= 0:
                    km, km_method = gc, "great_circle_fallback"
                run = segment_minutes(
                    km, rp["cruise_kmh"][0], rp["accel_ms2"][0], rp["decel_ms2"][0]
                )
                dwell = rp["dwell_s"][0] / 60.0
                g.add_edge(
                    f"{ln.id}:{prev.id}",
                    nid,
                    kind="line",
                    line=ln.id,
                    layer=ln.layer,
                    km=float(km),
                    km_method=km_method,
                    gc_km=gc,
                    run_min=run,
                    dwell_min=dwell,
                    min=run + dwell,
                    cruise_kmh=rp["cruise_kmh"][0],
                    accel_ms2=rp["accel_ms2"][0],
                    decel_ms2=rp["decel_ms2"][0],
                    dwell_s=rp["dwell_s"][0],
                    params_source=json.dumps({k: v[1] for k, v in rp.items()}, sort_keys=True),
                )
            prev = st
    add_interchanges(g, params)
    return g


def add_interchanges(g: nx.MultiGraph, params: dict[str, Any]) -> int:
    ic = params["interchange"]
    walk_km = float(ic["walk_max_km"]["value"])
    same_km = float(ic["same_name_max_km"]["value"])
    speed = float(ic["walk_speed_kmh"]["value"])
    nodes = [n for n, d in g.nodes(data=True) if d.get("kind") == "station"]
    if len(nodes) < 2:
        return 0
    lat = np.array([g.nodes[n]["lat"] for n in nodes])
    lon = np.array([g.nodes[n]["lon"] for n in nodes])
    kn = KNearest(lat, lon)
    pairs: dict[tuple[int, int], str] = {}
    radius = max(walk_km, same_km)
    from network.geo import EARTH_RADIUS_KM

    chord = 2 * math.sin(radius / (2 * EARTH_RADIUS_KM))
    for i, j in kn.tree.query_pairs(chord):
        a, b = nodes[i], nodes[j]
        if g.nodes[a]["line"] == g.nodes[b]["line"]:
            continue
        d = float(haversine_km(lat[i], lon[i], lat[j], lon[j]))
        same = _norm(g.nodes[a]["name_en"]) == _norm(g.nodes[b]["name_en"])
        if d <= walk_km:
            pairs[(i, j)] = "walk_distance"
        elif same and d <= same_km:
            pairs[(i, j)] = "same_name"
    for (i, j), why in sorted(pairs.items()):
        d = float(haversine_km(lat[i], lon[i], lat[j], lon[j]))
        a, b = nodes[i], nodes[j]
        g.add_edge(
            a,
            b,
            kind="interchange",
            line=None,
            layer=f"{g.nodes[a]['layer']}|{g.nodes[b]['layer']}",
            km=d,
            km_method="great_circle",
            gc_km=d,
            run_min=d / speed * 60.0,
            dwell_min=0.0,
            min=d / speed * 60.0,
            reason=why,
        )
    return len(pairs)


def tables(g: nx.MultiGraph) -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = pd.DataFrame([{"node_id": n, **d} for n, d in g.nodes(data=True)])
    edges = pd.DataFrame([{"u": u, "v": v, **d} for u, v, d in g.edges(data=True)])
    return nodes, edges


def summarise(
    scn: Scenario,
    lines: list[LineSpec],
    g: nx.MultiGraph,
    expansions: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    nodes, edges = tables(g)
    le = edges[edges["kind"] == "line"] if len(edges) else edges
    per_layer: dict[str, Any] = {}
    for layer in scn.layers:
        ids = [ln.id for ln in lines if ln.layer == layer]
        e = le[le["layer"] == layer] if len(le) else le
        per_layer[layer] = {
            "lines": len(ids),
            "line_ids": ids,
            "stations": int((nodes["layer"] == layer).sum()) if len(nodes) else 0,
            "edges": len(e),
            "km": round(float(e["km"].sum()), 3) if len(e) else 0.0,
        }
    n_ic = int((edges["kind"] == "interchange").sum()) if len(edges) else 0
    ic = edges[edges["kind"] == "interchange"] if len(edges) else edges
    return {
        "scenario": scn.id,
        "include": list(scn.lines.include),
        "expanded_ids": expansions or {},
        "layers": per_layer,
        "interchange_by_reason": ic["reason"].value_counts().to_dict() if len(ic) else {},
        "interchange_edges": n_ic,
        "n_nodes": g.number_of_nodes(),
        "n_edges": g.number_of_edges(),
        "edges_missing_run_time": int(le["run_min"].isna().sum()) if len(le) else 0,
        "edges_km_fallback": int((le["km_method"] != "km_post").sum()) if len(le) else 0,
    }


def _rel(p: Path) -> str:
    rp, root = Path(p).resolve(), REPO_ROOT.resolve()
    return str(rp.relative_to(root)) if rp.is_relative_to(root) else rp.name


def build(
    scenario: Path, out: Path, seed: int, lines_dir: Path = LINES_DIR, params: Path = PARAMS_YAML
) -> dict[str, Any]:
    t0 = time.monotonic()
    scn = load_scenario(scenario)
    prm = load_params(params)
    lines = scenario_lines(scn, lines_dir)
    g = build_graph(lines, prm)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(g, edges="edges")
    (out / "graph.json").write_text(
        json.dumps(data, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    nodes, edges = tables(g)
    nodes.to_parquet(out / "nodes.parquet", index=False)
    edges.to_parquet(out / "edges.parquet", index=False)
    summary = summarise(scn, lines, g, expand_ids(scn.lines.include, lines_dir)[1])
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    used = sorted(
        {d["assumption_id"] for d in prm["interchange"].values()}
        | {
            s.split(":", 1)[1]
            for _, _, d in g.edges(data=True)
            if d.get("kind") == "line"
            for s in json.loads(d["params_source"]).values()
            if s.startswith("default:")
        }
    )
    extra = {
        "scenario": scn.id,
        "scenario_file": _rel(scenario),
        "lines_dir": _rel(lines_dir),
        "expanded_ids": summary["expanded_ids"],
        "line_files": {ln.id: _rel(Path(lines_dir) / f"{ln.id}.yaml") for ln in lines},
        "n_nodes": summary["n_nodes"],
        "n_edges": summary["n_edges"],
        "assumptions": used,
        "runtime_s": round(time.monotonic() - t0, 3),
    }
    config = {
        "scenario": scn.model_dump(mode="json"),
        "lines": [ln.model_dump(mode="json", by_alias=True) for ln in lines],
        "params": prm,
    }
    write_meta(out, seed, config, extra)
    return summary


@app.command("build")
def build_cmd(
    scenario: Path = typer.Option(..., exists=True),
    out: Path = typer.Option(...),
    seed: int = seed_option(),
    lines_dir: Path = typer.Option(LINES_DIR, help="dir of <line_id>.yaml"),
    params: Path = typer.Option(PARAMS_YAML),
) -> None:
    """Build the scenario graph: graph.json, nodes/edges.parquet, summary.json, meta.json."""
    summary = build(scenario, out, seed, lines_dir, params)
    typer.echo(json.dumps(summary["layers"], ensure_ascii=False))
    typer.echo(f"{summary['n_nodes']} nodes, {summary['n_edges']} edges -> {out}")


@app.command("check")
def check_cmd(
    scenario: Path = typer.Option(..., exists=True),
    lines_dir: Path = typer.Option(LINES_DIR),
) -> None:
    """Validate the scenario and its line YAMLs (layers, schema) without writing anything."""
    scn = load_scenario(scenario)
    lines = scenario_lines(scn, lines_dir)
    typer.echo(f"{scn.id}: {len(lines)} lines OK ({', '.join(ln.id for ln in lines)})")


if __name__ == "__main__":
    app()
