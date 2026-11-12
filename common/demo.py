"""Fixture-scale demo (`make demo`, R9): screening -> CBA -> dashboard API, on invented fixtures.

Every input is a test fixture (`tests/fixtures/region_register.parquet`, `cba_case.yaml`,
`demo_inputs.yaml`, `tests/fixtures/api/`); nothing national is read, downloaded or contacted.
The dashboard step starts the read-only API on 127.0.0.1 (a free port), queries a few endpoints,
saves the responses and stops it; `--serve` keeps it running instead. Outputs go to
`runs/demo/` (gitignored). Label: synthetic demand, uncalibrated: scenario comparison, not a
forecast. The fixture numbers describe no real place, line, cost or appraisal.

CLI:
  uv run python -m common.demo run [--out runs/demo] [--seed 1] [--serve] [--port 0]
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import rng, write_meta

# The dashboard API labels screening responses with this text instead of LABEL (api/README.md).
SCREENING_LABEL = "screening input, not a forecast"

FIX = REPO_ROOT / "tests" / "fixtures"
INPUTS = FIX / "demo_inputs.yaml"
WEIGHTS = REPO_ROOT / "cities" / "ksa" / "assumptions" / "screening_weights.yaml"

app = typer.Typer(add_completion=False, help="Fixture-scale demo: screening, CBA, dashboard API.")


@app.callback()
def _group() -> None:
    """Fixture-scale demo (R9)."""


def load_inputs(path: Path = INPUTS) -> dict[str, Any]:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not cfg.get("fixture"):
        raise ValueError(f"{path} is not marked fixture: true")
    return cfg


def screening_step(inp: dict[str, Any], out: Path, seed: int) -> dict[str, Any]:
    """Merge the mini-region register, apply the long-list filters, score and sweep the weights."""
    from screening import funnel
    from screening.merge import merge_frames

    s = inp["screening"]
    merged, _ = merge_frames([FIX / "region_register.parquet"])
    merged["dist_existing_km"] = s["dist_existing_km"]
    cfg = funnel.load_config(WEIGHTS)
    anchor = merged.loc[merged["name_en"] == s["metro_anchor_name_en"], "row_key"].item()
    cfg["metros"] = [{"name": "Fixture metro", "tier": 1, "anchors": [anchor]}]
    threshold = int(funnel.val(cfg["long_list"]["threshold"]))
    sensitivity = int(funnel.val(cfg["long_list"]["sensitivity"]))
    ll = funnel.long_list(merged, cfg, threshold, sensitivity)
    res = funnel.run_score(ll, merged, cfg, float(s["sweep_fraction"]), seed)
    out.mkdir(parents=True, exist_ok=True)
    ll.to_parquet(out / "longlist.parquet", index=False)
    res["table"].to_csv(out / "scores.csv", index=False)
    res["sweep"].to_csv(out / "sweep.csv", index=False)
    summary = {
        "label": "screening input, not a forecast (fixture data)",
        "settlements": int(len(ll)),
        "long_list": int((ll["funnel_stage"] == "long").sum()),
        "short_list": res["summary"]["n_short"],
        "weight_sweep_corners": len(res["summary"]["corners"]),
        "top_report_stability": res["summary"]["top_report_stability"],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_meta(out, seed, {"inputs": s, "weights": str(WEIGHTS.relative_to(REPO_ROOT))})
    return summary


def _draws(c: dict[str, Any], n: int, seed: int) -> pd.DataFrame:
    g = rng(seed)
    capex = g.uniform(c["capex_low"], c["capex_high"], n)
    d = pd.DataFrame(
        {
            "draw": np.arange(n),
            "capex": capex,
            "capex_base": np.full(n, c["capex_base"]),
            "capex_multiplier": capex / c["capex_base"],
            "construction_years": np.full(n, c["construction_years"]),
            "opex": np.full(n, c["opex"]),
            "renewals_30y": np.full(n, c["renewals_30y"]),
            "renewals_40y": np.full(n, c["renewals_40y"]),
            "renewals_60y": np.full(n, c["renewals_60y"]),
            "ridership_ratio": g.uniform(c["ridership_low"], c["ridership_high"], n),
        }
    )
    for m in ("vot_mult", "carbon_mult", "crash_mult", "aq_mult", "mec_mult", "wei_mult"):
        d[m] = 1.0
    d["rate_shift"] = 0.0
    return d


def cba_step(inp: dict[str, Any], out: Path, seed: int) -> dict[str, Any]:
    """Appraise the fixture CBA case with the real engine and the registered parameters."""
    from economics import cba
    from economics import params as prm

    c = inp["cba"]
    case = cba.load_case(FIX / "cba_case.yaml")
    q = c["quantities"]
    rows = [
        {"case": case.id, "population": c["base_year_population"], "year": c["base_year"]} | q,
        {"case": case.id, "population": c["population"], "year": c["forecast_year"]}
        | {k: c["forecast_growth"] * v for k, v in q.items()},
    ]
    ctx = cba.Context(
        case=case,
        p=prm.load(),
        scalars=pd.DataFrame(rows),
        cost={},
        class_share=c["class_share"],
        train_km_yr=c["train_km_yr"],
        electric=c["electric"],
        line_type=c["line_type"],
    )
    n = int(case.monte_carlo.draws)
    draws = _draws(c, n, seed)
    horizons = [int(h) for h in case.horizon_years]
    res = cba.evaluate(ctx, draws, c["population"], horizons, [c["rate_case"]])
    table = {
        f"{h}y": {k: cba.pct(res[(h, c["rate_case"])][k]) for k in ("pvb", "pvc", "npv", "bcr")}
        for h in horizons
    }
    summary = {
        "label": LABEL,
        "fixture": True,
        "case": case.id,
        "draws": n,
        "rate_case": c["rate_case"],
        "units": "SAR million, invented fixture values (P10/P50/P90)",
        "results": table,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_meta(out, seed, {"inputs": c, "case": "tests/fixtures/cba_case.yaml"})
    return summary


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _get(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=10) as r:  # noqa: S310 (127.0.0.1 only)
        return json.loads(r.read().decode("utf-8"))


def dashboard_step(
    inp: dict[str, Any], out: Path, port: int = 0, serve: bool = False
) -> dict[str, Any]:
    """Start the read-only API on the fixture data, save a few responses, stop it."""
    d = inp["dashboard"]
    port = port or _free_port()
    env = os.environ | {
        "RAILTWIN_DATA_ROOT": str(REPO_ROOT / d["data_root"]),
        "RAILTWIN_RUNS_ROOT": str(REPO_ROOT / d["runs_root"]),
    }
    cmd = [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1"]
    cmd += ["--port", str(port), "--log-level", "warning"]
    proc = subprocess.Popen(cmd, cwd=REPO_ROOT, env=env)
    base = f"http://127.0.0.1:{port}"
    try:
        t0 = time.monotonic()
        while True:
            try:
                _get(base + "/health")
                break
            except OSError:
                if proc.poll() is not None or time.monotonic() - t0 > d["startup_timeout_s"]:
                    raise RuntimeError("dashboard API did not start") from None
                time.sleep(0.3)
        out.mkdir(parents=True, exist_ok=True)
        got: dict[str, Any] = {}
        for ep in d["endpoints"]:
            body = _get(base + ep)
            name = ep.strip("/").replace("/", "_") or "root"
            (out / f"{name}.json").write_text(
                json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            text = json.dumps(body, ensure_ascii=False)
            got[ep] = isinstance(body, dict) and (LABEL in text or SCREENING_LABEL in text)
        summary = {"url": base, "endpoints": got, "web_dist_served": _has_web()}
        (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        if serve:
            typer.echo(f"dashboard on fixture data: {base}/ (Ctrl-C to stop)")
            proc.wait()
        return summary
    except KeyboardInterrupt:
        return {"url": base, "stopped": "interrupted"}
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


def _has_web() -> bool:
    return (REPO_ROOT / "web" / "dist" / "index.html").exists()


@app.command("run")
def run_cmd(
    out: Path = typer.Option(REPO_ROOT / "runs" / "demo", "--out"),
    seed: int = typer.Option(1, "--seed", min=0),
    port: int = typer.Option(0, "--port", help="0 = a free port"),
    serve: bool = typer.Option(False, "--serve", help="keep the dashboard API running"),
) -> None:
    """Run the three demo steps on fixtures and print a short summary."""
    inp = load_inputs()
    timings: dict[str, float] = {}
    t = time.monotonic()
    scr = screening_step(inp, out / "screening", seed)
    timings["screening_s"] = round(time.monotonic() - t, 2)
    t = time.monotonic()
    cb = cba_step(inp, out / "cba", seed)
    timings["cba_s"] = round(time.monotonic() - t, 2)
    t = time.monotonic()
    dash = dashboard_step(inp, out / "dashboard", port, serve)
    timings["dashboard_s"] = round(time.monotonic() - t, 2)
    (out / "timings.json").write_text(json.dumps(timings, indent=2) + "\n", encoding="utf-8")
    h = max(cb["results"], key=lambda k: int(k.rstrip("y")))
    npv = cb["results"][h]["npv"]
    typer.echo(f"Label: {LABEL} (fixture data; invented values)")
    typer.echo(
        f"screening: {scr['settlements']} settlements -> {scr['long_list']} long list -> "
        f"{scr['short_list']} short list; {scr['weight_sweep_corners']} weight-sweep corners"
    )
    typer.echo(
        f"cba: {cb['case']}, {cb['draws']} draws, {h} NPV P10/P50/P90 = "
        f"{npv['P10']:,.0f} / {npv['P50']:,.0f} / {npv['P90']:,.0f} SAR million (fixture)"
    )
    ok = sum(bool(v) for v in dash.get("endpoints", {}).values())
    web = "served at /" if dash.get("web_dist_served") else "not built (make demo-serve builds it)"
    typer.echo(
        f"dashboard API: {len(dash.get('endpoints', {}))} endpoints answered "
        f"({ok} carry a label); web app {web}"
    )
    shown = out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out
    typer.echo(f"outputs: {shown} ; timings {timings}")
    missing = [ep for ep, v in dash.get("endpoints", {}).items() if not v and ep != "/health"]
    if missing:
        typer.echo(f"WARNING: endpoints without the label: {missing}")


if __name__ == "__main__":
    app()
