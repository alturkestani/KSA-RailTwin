"""Rail running-time model (W8, R4 task 1; skill isochrone-commute).

Per stop-to-stop segment the train follows a speed profile on a 25 m grid:
- a forward pass accelerates at a(v) = a0 below the power knee and a0 x v_knee / v above it
  (constant-power residual acceleration), capped by the line speed and any speed restriction;
- a backward pass brakes at the service deceleration b into every stop and restriction;
- time = sum of dx / mean speed. Dwell per intermediate stop (by station class) and a UIC 451-1
  style recovery margin (pct x running time + min per 100 km) are added on top.
Every real-world parameter comes from `cities/ksa/assumptions/running_time_classes.yaml`
(rolling-stock classes) and `running_time_lines.yaml` (per-line operating speed, restrictions,
patterns, validation pairs), each with a source id or an assumption id (docs/assumptions.md).

Outputs per run (`runs/access/running_time/<line>-<pattern>-s<seed>/`):
- `pairs.csv`: in-vehicle minutes for every station pair of the pattern (running, dwell, recovery);
- `stops.csv`: the explicit minute cost of every intermediate stop (stop vs pass at line speed,
  plus dwell; the through-passenger penalty used by optimisation);
- `validation.json` for lines with published times (model vs published, error %, ±10 % gate).

  uv run python -m access.running_time --line cities/ksa/lines/hhr.yaml --pattern all-stop --seed 1

Running times are a timetable model, not a forecast.
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

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta

CLASSES = Path("cities/ksa/assumptions/running_time_classes.yaml")
LINES = Path("cities/ksa/assumptions/running_time_lines.yaml")
DX_M = 25.0

app = typer.Typer(add_completion=False, help=__doc__)


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def load_yaml(path: Path, root: Path = REPO_ROOT) -> dict[str, Any]:
    p = path if path.is_absolute() else root / path
    return yaml.safe_load(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- parameters
@dataclass(frozen=True)
class Stock:
    """Rolling-stock class: kinematics, dwell by station class, recovery margin."""

    name: str
    vmax_kmh: float
    accel_ms2: float
    knee_kmh: float
    decel_ms2: float
    dwell_s: dict[str, float]
    recovery_pct: float
    recovery_min_per_100km: float

    @classmethod
    def from_yaml(cls, name: str, d: dict[str, Any], scale: str = "value") -> Stock:
        def pick(node: Any) -> float:
            if isinstance(node, dict) and scale in ("low", "high") and "range" in node:
                lo, hi = node["range"]
                return float(lo if scale == "low" else hi)
            return float(_v(node))

        return cls(
            name=name,
            vmax_kmh=pick(d["vmax_kmh"]),
            accel_ms2=pick(d["accel_ms2"]),
            knee_kmh=pick(d["power_knee_kmh"]),
            decel_ms2=pick(d["decel_ms2"]),
            dwell_s={k: pick(v) for k, v in d["dwell_s"].items()},
            recovery_pct=pick(d["recovery"]["pct"]),
            recovery_min_per_100km=pick(d["recovery"]["min_per_100km"]),
        )

    def dwell(self, station_class: str) -> float:
        return float(self.dwell_s.get(station_class, self.dwell_s["default"]))


@dataclass
class LineRun:
    """One line (or corridor) with stations, km-posts, operating speed and restrictions."""

    line_id: str
    stations: pd.DataFrame  # id, km_post, class (sorted by km_post)
    stock: Stock
    line_speed_kmh: float
    restrictions: list[tuple[float, float, float]] = field(default_factory=list)  # (from, to, kmh)
    route_factor: float = 1.0

    @property
    def vcap_kmh(self) -> float:
        return min(self.line_speed_kmh, self.stock.vmax_kmh)


# --------------------------------------------------------------------------- kinematics
def segment_profile(
    km: float,
    vcap_kmh: float,
    stock: Stock,
    limits: list[tuple[float, float, float]] | None = None,
    v_start_kmh: float = 0.0,
    v_end_kmh: float = 0.0,
    dx_m: float = DX_M,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Minutes for one segment from v_start to v_end; limits are (from_km, to_km, kmh) relative to
    the segment start. Returns (minutes, x_m, v_ms)."""
    if km <= 0:
        return 0.0, np.zeros(1), np.zeros(1)
    n = max(int(math.ceil(km * 1000.0 / dx_m)), 2)
    x = np.linspace(0.0, km * 1000.0, n + 1)
    vlim = np.full(n + 1, vcap_kmh / 3.6)
    for a, b, s in limits or []:
        m = (x >= a * 1000.0) & (x <= b * 1000.0)
        vlim[m] = np.minimum(vlim[m], s / 3.6)
    dx = x[1] - x[0]
    a0, vk, dec = stock.accel_ms2, stock.knee_kmh / 3.6, stock.decel_ms2
    v = np.empty(n + 1)
    v[0] = min(v_start_kmh / 3.6, vlim[0])
    for i in range(n):  # forward: traction, constant power above the knee
        acc = a0 if v[i] <= vk else a0 * vk / max(v[i], 1e-6)
        v[i + 1] = min(vlim[i + 1], math.sqrt(v[i] * v[i] + 2.0 * acc * dx))
    v[n] = min(v[n], v_end_kmh / 3.6)
    for i in range(n - 1, -1, -1):  # backward: service braking
        v[i] = min(v[i], math.sqrt(v[i + 1] * v[i + 1] + 2.0 * dec * dx))
    vm = 0.5 * (v[1:] + v[:-1])
    t = float(np.sum(dx / np.maximum(vm, 1e-3)))
    return t / 60.0, x, v


def _limits_between(run: LineRun, k0: float, k1: float) -> list[tuple[float, float, float]]:
    out = []
    for a, b, s in run.restrictions:
        lo, hi = max(a, k0), min(b, k1)
        if hi > lo:
            out.append((lo - k0, hi - k0, s))
    return out


def run_minutes(run: LineRun, stops: list[str]) -> pd.DataFrame:
    """Cumulative timetable along the stop list (in km order): running, dwell and recovery minutes
    to every stop from the first; dwell counted at intermediate stops only."""
    st = run.stations.set_index("id")
    ks = [float(st.at[s, "km_post"]) for s in stops]
    rows = [{"station": stops[0], "km": ks[0], "run_min": 0.0, "dwell_min": 0.0, "rec_min": 0.0}]
    run_c = dwell_c = rec_c = 0.0
    for i in range(1, len(stops)):
        k0, k1 = ks[i - 1], ks[i]
        lo, hi = min(k0, k1), max(k0, k1)
        km = (hi - lo) * run.route_factor
        lim = _limits_between(run, lo, hi)
        if run.route_factor != 1.0:
            lim = [(a * run.route_factor, b * run.route_factor, s) for a, b, s in lim]
        m, _, _ = segment_profile(km, run.vcap_kmh, run.stock, lim)
        run_c += m
        rec_c += run.stock.recovery_pct * m + run.stock.recovery_min_per_100km * km / 100.0
        if i > 1:
            dwell_c += run.stock.dwell(str(st.at[stops[i - 1], "class"])) / 60.0
        rows.append(
            {
                "station": stops[i],
                "km": k1,
                "run_min": run_c,
                "dwell_min": dwell_c,
                "rec_min": rec_c,
            }
        )
    return pd.DataFrame(rows)


def pair_table(run: LineRun, stops: list[str]) -> pd.DataFrame:
    """In-vehicle minutes between every ordered pair of the stop list (same train)."""
    tt = run_minutes(run, stops)
    tt["ivt_min"] = tt.run_min + tt.dwell_min + tt.rec_min
    out = []
    for i in range(len(tt)):
        for j in range(i + 1, len(tt)):
            a, b = tt.iloc[i], tt.iloc[j]
            # dwell at stop i belongs to the train before departure: exclude it for a boarder at i
            st_cls = run.stations.set_index("id").at[a.station, "class"]
            dwell_i = run.stock.dwell(str(st_cls)) / 60.0 if i > 0 else 0.0
            out.append(
                {
                    "from": a.station,
                    "to": b.station,
                    "km": abs(b.km - a.km) * run.route_factor,
                    "run_min": b.run_min - a.run_min,
                    "dwell_min": b.dwell_min - a.dwell_min - dwell_i,
                    "rec_min": b.rec_min - a.rec_min,
                }
            )
    df = pd.DataFrame(out)
    df["ivt_min"] = df.run_min + df.dwell_min + df.rec_min
    return df


def stop_costs(run: LineRun, stops: list[str]) -> pd.DataFrame:
    """Explicit minute cost per intermediate stop: (running with the stop - running without it) +
    dwell, on the two neighbouring segments (recovery included pro rata)."""
    st = run.stations.set_index("id")
    rows = []
    for i in range(1, len(stops) - 1):
        a, s, b = stops[i - 1], stops[i], stops[i + 1]
        with_stop = pair_table(run, [a, s, b])
        through = pair_table(run, [a, b])
        t_with = float(
            with_stop.loc[(with_stop["from"] == a) & (with_stop.to == b), "ivt_min"].iloc[0]
        )
        t_thru = float(through.ivt_min.iloc[0])
        rows.append(
            {
                "station": s,
                "class": str(st.at[s, "class"]),
                "km": float(st.at[s, "km_post"]),
                "stop_cost_min": t_with - t_thru,
                "dwell_min": run.stock.dwell(str(st.at[s, "class"])) / 60.0,
            }
        )
    return pd.DataFrame(rows, columns=["station", "class", "km", "stop_cost_min", "dwell_min"])


# --------------------------------------------------------------------------- line set-up
def line_stations(line: dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "id": s["id"],
                "km_post": float(s["km_post"]),
                "class": s.get("class", "intermediate"),
                "lat": s.get("lat"),
                "lon": s.get("lon"),
                "name_en": s.get("name_en", s["id"]),
            }
            for s in line["stations"]
        ]
    )
    return df.sort_values("km_post").reset_index(drop=True)


def stock_for(
    line: dict[str, Any], classes: dict[str, Any], lines_cfg: dict[str, Any], scale: str = "value"
) -> tuple[str, Stock]:
    cfg = lines_cfg.get("lines", {}).get(line["id"], {})
    cls = (
        cfg.get("stock") or classes["by_line_type"][line.get("line_type", "conventional_passenger")]
    )
    cls = _v(cls)
    return cls, Stock.from_yaml(cls, classes["classes"][cls], scale)


def build_run(
    line: dict[str, Any],
    root: Path = REPO_ROOT,
    scale: str = "value",
    classes: dict[str, Any] | None = None,
    lines_cfg: dict[str, Any] | None = None,
) -> LineRun:
    """LineRun from a line or corridor YAML dict and the two running-time YAMLs."""
    classes = classes or load_yaml(CLASSES, root)
    lines_cfg = lines_cfg or load_yaml(LINES, root)
    _, stock = stock_for(line, classes, lines_cfg, scale)
    cfg = lines_cfg.get("lines", {}).get(line["id"], {})
    if "line_speed_kmh" in cfg:
        node = cfg["line_speed_kmh"]
        if scale in ("low", "high") and isinstance(node, dict) and "range" in node:
            # slow end of the speed range = the "high" running-time case
            lo, hi = node["range"]
            speed = float(hi if scale == "low" else lo)
        else:
            speed = float(_v(node))
    else:
        design = line.get("design_speed_kmh")
        speed = float(design) if design else stock.vmax_kmh
    restr = [
        (float(r["from_km"]), float(r["to_km"]), float(_v(r["kmh"])))
        for r in cfg.get("restrictions", [])
    ]
    rf = line.get("route_factor")
    rf = 1.0 if rf is None else float(_v(rf))
    if cfg.get("km_is_route", line.get("layer") != "hypothetical"):
        rf = 1.0  # km-posts of existing lines are along the track already
    if "route_factor_override" in cfg:
        rf = float(_v(cfg["route_factor_override"]))
    routed = line.get("alignment_routed")
    if routed:
        # R4_ALIGN: km-posts are chainage along the routed alignment; curve speed limits apply
        rf = 1.0
        restr += [
            (float(r["from_km"]), float(r["to_km"]), float(r["kmh"]))
            for r in routed.get("speed_restrictions", [])
        ]
    return LineRun(line["id"], line_stations(line), stock, speed, restr, rf)


def pattern_stops(run: LineRun, pattern: str, line_cfg: dict[str, Any]) -> list[str]:
    ids = run.stations.id.tolist()
    if pattern == "all-stop":
        return ids
    if pattern == "express":
        return [ids[0], ids[-1]]
    pats = line_cfg.get("patterns", {})
    if pattern in pats:
        return [s for s in ids if s in set(pats[pattern]["stops"])]
    raise typer.BadParameter(f"unknown pattern {pattern}")


def validate(run: LineRun, line_cfg: dict[str, Any], tol: float) -> list[dict[str, Any]]:
    """Model vs published times for the line's validation pairs (non-stop or with listed stops)."""
    out = []
    for v in line_cfg.get("validation", []):
        stops = v["stops"]
        ids = run.stations.set_index("id").km_post
        order = sorted(stops, key=lambda s: float(ids[s]))
        tab = pair_table(run, order)
        m = float(tab.loc[(tab["from"] == order[0]) & (tab.to == order[-1]), "ivt_min"].iloc[0])
        pub = float(_v(v["published_min"]))
        err = m / pub - 1.0
        out.append(
            {
                "id": v["id"],
                "pair": f"{stops[0]}-{stops[-1]}",
                "stops": stops,
                "role": v.get("role", "validation"),
                "published_min": pub,
                "published_source": v["published_min"].get("source"),
                "model_min": round(m, 2),
                "error_pct": round(100 * err, 1),
                "tolerance_pct": round(100 * tol, 1),
                "pass": bool(abs(err) <= tol),
            }
        )
    return out


def fit_line_speed(
    line: dict[str, Any],
    target: dict[str, Any],
    root: Path = REPO_ROOT,
    lo: float = 80.0,
    hi: float = 350.0,
) -> float:
    """The uniform operating speed that reproduces one published time (bisection). Used only to
    derive the calibrated speed of a line from a pair that is NOT its validation gate pair."""
    classes, lines_cfg = load_yaml(CLASSES, root), load_yaml(LINES, root)
    pub = float(_v(target["published_min"]))
    stops = target["stops"]
    cfg = lines_cfg.get("lines", {}).get(line["id"], {})

    def minutes(speed: float) -> float:
        lc = {"lines": {line["id"]: {**cfg, "line_speed_kmh": speed}}}
        r = build_run(line, root, classes=classes, lines_cfg=lc)
        km = r.stations.set_index("id").km_post
        order = sorted(stops, key=lambda s: float(km[s]))
        t = pair_table(r, order)
        return float(t.loc[(t["from"] == order[0]) & (t.to == order[-1]), "ivt_min"].iloc[0])

    a, b = lo, hi
    if minutes(b) > pub:
        return b
    for _ in range(40):
        m = 0.5 * (a + b)
        a, b = (m, b) if minutes(m) > pub else (a, m)
    return round(0.5 * (a + b), 1)


def timetable_factors(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Published / modelled minutes on every validation pair (A-r4-rt-011). Per existing line: the
    median over its `era: current` pairs (else all its pairs). Generic factor for planned and
    hypothetical lines: median over all current pairs, range = min-max over all pairs."""
    lines_cfg = load_yaml(LINES, root)
    classes = load_yaml(CLASSES, root)
    tol = float(_v(lines_cfg["validation_tolerance"]))
    rows = []
    for lid, cfg in lines_cfg["lines"].items():
        if not cfg.get("validation"):
            continue
        ld = load_yaml(Path(f"cities/ksa/lines/{lid}.yaml"), root)
        r = build_run(ld, root, classes=classes, lines_cfg=lines_cfg)
        for v in validate(r, cfg, tol):
            era = next(x.get("era", "current") for x in cfg["validation"] if x["id"] == v["id"])
            rows.append(
                {**v, "line": lid, "era": era, "factor": v["published_min"] / v["model_min"]}
            )
    df = pd.DataFrame(rows)
    per_line = {}
    for lid, g in df.groupby("line"):
        cur = g[g.era == "current"]
        use = cur if len(cur) else g
        per_line[lid] = {
            "value": round(float(use.factor.median()), 3),
            "range": [round(float(g.factor.min()), 3), round(float(g.factor.max()), 3)],
            "pairs": use.id.tolist(),
        }
    cur = df[df.era == "current"]
    generic = {
        "value": round(float(cur.factor.median()), 3),
        "range": [round(float(df.factor.min()), 3), round(float(df.factor.max()), 3)],
        "pairs": cur.id.tolist(),
        "assumption": "A-r4-rt-011",
    }
    gate = []
    for g in df[df.role.astype(str).str.startswith("gate")].itertuples():
        # leave-one-out: the factor is fitted on every current pair except the gate pair itself
        others = cur[cur.id != g.id]
        f_loo = float(others.factor.median())
        pred = g.model_min * f_loo
        err = pred / g.published_min - 1.0
        gate.append(
            {
                "id": g.id,
                "published_min": g.published_min,
                "published_source": g.published_source,
                "kinematic_min": g.model_min,
                "kinematic_error_pct": g.error_pct,
                "loo_factor": round(f_loo, 3),
                "loo_pairs": others.id.tolist(),
                "predicted_min": round(pred, 2),
                "error_pct": round(100 * err, 1),
                "tolerance_pct": round(100 * tol, 1),
                "pass": bool(abs(err) <= tol),
            }
        )
    return {
        "per_line": per_line,
        "generic": generic,
        "gate": gate,
        "pairs": df.round(3).to_dict("records"),
    }


# --------------------------------------------------------------------------- CLI
@app.command("factors")
def factors_cmd(
    out: Path = typer.Option(Path("runs/access/running_time/factors-s1"), "--out"),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Timetable factors (published / modelled) for every validation pair; writes factors.json."""
    f = timetable_factors(root)
    run_dir = root / out
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "factors.json").write_text(json.dumps(f, indent=1, default=str) + "\n")
    write_meta(
        run_dir,
        seed,
        {"classes": load_yaml(CLASSES, root), "lines": load_yaml(LINES, root)},
        extra={"method": "published / modelled minutes (A-r4-rt-011)"},
    )
    typer.echo(json.dumps({k: f[k] for k in ("per_line", "generic", "gate")}, indent=1))


@app.command("run")
def main(
    line: Path = typer.Option(..., "--line", help="line or corridor YAML"),
    pattern: str = typer.Option("all-stop", "--pattern", help="all-stop | express | <named>"),
    out: Path | None = typer.Option(None, "--out"),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Pair times, per-stop minute costs and (where published) the validation gate."""
    ld = load_yaml(line, root)
    lines_cfg = load_yaml(LINES, root)
    lcfg = lines_cfg.get("lines", {}).get(ld["id"], {})
    tol = float(_v(lines_cfg["validation_tolerance"]))
    out = out or Path(f"runs/access/running_time/{ld['id']}-{pattern}-s{seed}")
    run_dir = root / out
    run_dir.mkdir(parents=True, exist_ok=True)
    res: dict[str, Any] = {}
    for scale in ("value", "low", "high"):
        r = build_run(ld, root, scale, lines_cfg=lines_cfg)
        stops = pattern_stops(r, pattern, lcfg)
        res[scale] = (r, stops, pair_table(r, stops), stop_costs(r, stops))
    r, stops, pairs, sc = res["value"]
    for scale in ("low", "high"):
        pairs[f"ivt_min_{scale}"] = res[scale][2].ivt_min.to_numpy()
    pairs.round(3).to_csv(run_dir / "pairs.csv", index=False)
    sc.round(3).to_csv(run_dir / "stops.csv", index=False)
    val = validate(r, lcfg, tol)
    summary = {
        "line": ld["id"],
        "pattern": pattern,
        "stock": r.stock.name,
        "line_speed_kmh": r.line_speed_kmh,
        "vcap_kmh": r.vcap_kmh,
        "stops": stops,
        "end_to_end_min": round(float(pairs.ivt_min.iloc[len(stops) - 2]), 2),
        "validation": val,
        "note": "timetable model, not a forecast",
    }
    (run_dir / "validation.json").write_text(json.dumps(summary, indent=1) + "\n")
    write_meta(
        run_dir,
        seed,
        {"line": ld, "classes": load_yaml(CLASSES, root), "lines": lines_cfg, "pattern": pattern},
        extra={"summary": summary, "method": "speed-profile simulation, 25 m grid"},
    )
    typer.echo(json.dumps(summary, indent=1))


@app.callback(invoke_without_command=True)
def _default(
    ctx: typer.Context,
    line: Path | None = typer.Option(None, "--line", help="line or corridor YAML (brief form)"),
    pattern: str = typer.Option("all-stop", "--pattern"),
    out: Path | None = typer.Option(None, "--out"),
    seed: int = seed_option(),
) -> None:
    """The brief's form `python -m access.running_time --line ... --seed 1` = `run`."""
    if ctx.invoked_subcommand is None:
        if line is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        main(line=line, pattern=pattern, out=out, seed=seed, root=REPO_ROOT)


if __name__ == "__main__":
    app()
