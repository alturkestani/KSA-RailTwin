"""Summary table of the R3 demand runs (one row per run directory under runs/demand/).

uv run python -m demand.report summary --seed 1 --out runs/demand/summary-s1/
writes summary.csv (run id, scenario, population, year, rates, giga, totals by purpose and mode,
rail by line), pairs.csv (S1 minus its matched S0 run on the same population, year, rates and
seed) and meta.json.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import typer

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

RUNS = Path("runs/demand")

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Demand run summaries."""


def row(run: Path) -> dict[str, Any] | None:
    meta = run / "meta.json"
    tot = run / "totals.json"
    if not (meta.exists() and tot.exists()):
        return None
    m = json.loads(meta.read_text(encoding="utf-8"))
    t = json.loads(tot.read_text(encoding="utf-8"))
    cfg = m.get("run", {})
    rs = cfg.get("rate_scale") or {}
    r: dict[str, Any] = {
        "run_id": str(run.relative_to(REPO_ROOT / RUNS)) if run.is_absolute() else run.name,
        "scenario": cfg.get("scenario"),
        "population": cfg.get("population"),
        "year": cfg.get("year"),
        "rates": "base" if not rs else ("low" if min(rs.values()) < 1 else "high"),
        "giga": cfg.get("giga"),
        "calibrated_ascs": bool(cfg.get("overrides")),
        "population_total": t["population"],
        "seed": m.get("seed"),
        "code_version": m.get("code_version"),
    }
    for p, v in t["by_purpose"].items():
        r[f"trips_{p}"] = v
    for k, v in t["by_mode"].items():
        r[f"trips_{k}"] = v
    for line, v in t["rail_by_line"].items():
        r[f"rail_{line}"] = v["passengers"]
        r[f"rail_pkm_m_{line}"] = v["passenger_km_m"]
    return r


def collect(root: Path = REPO_ROOT) -> pd.DataFrame:
    rows = []
    for d in sorted((root / RUNS).rglob("totals.json")):
        r = row(d.parent)
        if r is not None:
            r["run_id"] = str(d.parent.relative_to(root / RUNS))
            rows.append(r)
    return pd.DataFrame(rows)


def matched_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """S1 minus S0 on the same population, year, rates, giga, constants and seed (rule 6)."""
    key = ["population", "year", "rates", "giga", "calibrated_ascs", "seed"]
    df = df.assign(giga=df.giga.fillna("none"))
    df = df[~df.run_id.str.startswith("calibration")]  # the calibration's own OD run is not a pair
    s0 = df[df.scenario == "S0"].set_index(key)
    s1 = df[df.scenario == "S1"].set_index(key)
    common = s0.index.intersection(s1.index)
    cols = [c for c in df.columns if c.startswith(("trips_", "rail_"))]
    out = (s1.loc[common, cols].fillna(0) - s0.loc[common, cols].fillna(0)).reset_index()
    out.insert(0, "s1_run", s1.loc[common, "run_id"].to_numpy())
    out.insert(0, "s0_run", s0.loc[common, "run_id"].to_numpy())
    return out


@app.command("summary")
def summary_cmd(
    out: Path = typer.Option(Path("runs/demand/summary-s1")),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Collect every run's totals into one table and the S1 - S0 matched differences."""
    df = collect(root)
    df = df[~df.run_id.str.startswith("summary")]
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    df.to_csv(run / "summary.csv", index=False)
    pairs = matched_pairs(df)
    pairs.to_csv(run / "pairs.csv", index=False)
    write_meta(run, seed, {"runs": df.run_id.tolist()}, extra={"label": LABEL, "rows": len(df)})
    typer.echo(f"{len(df)} runs, {len(pairs)} matched S1-S0 pairs -> {out}")


if __name__ == "__main__":
    app()
