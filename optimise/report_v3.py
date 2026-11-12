"""R6_V3 reporting: the CP7 layouts with variant edits, the final top 5 with the national reach
column (reported only), maps and scorecards.

  uv run python -m optimise.report_v3 cp7                # runs/r6/v3/cp7/cp7.csv
  uv run python -m optimise.report_v3 top5 --final L1=<yaml>:<score dir>,...   # runs/r6/top5/

`top5` moves the v2 top 5 (`runs/r6/top5/`) to `runs/r6/top5-v2/` once (never deletes it), then
writes `runs/r6/top5/<L>/` from the v3 full-judge runs, adds the national reach (optimise/reach.py,
A-r6-104) to each `score.json` under the key `national_reach_reported_only` (the judge's robust
NPV and every other figure are untouched; the pristine judge output stays in its v3 run dir),
re-draws the maps and rebuilds `top5.csv` with the reach columns.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from optimise import report
from optimise import search as se

POPS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R6_V3 reporting."""


def summary(s: dict) -> dict:
    return {
        "robust_npv": s["robust_npv"],
        "capex_p50": s["capex_sar_m"]["capex_p50"],
        "capex_p90": s["capex_sar_m"]["capex_p90"],
        **{f"npv_p50cost_{p.split('_')[-1]}": s["npv_at_p50_cost"][p] for p in POPS},
        **{f"npv_p90cost_{p.split('_')[-1]}": s["npv_at_p90_cost"][p] for p in POPS},
        "robust_npv_p90cost": min(s["npv_at_p90_cost"].values()),
        "access_gain_120": s.get("access_gain_120"),
    }


@app.command("cp7")
def cp7_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """L1 and L3 (CP7-1) with every applicable variant edit vs the v2 layout (A-r6-105)."""
    rows = []
    for k in ("L1", "L2", "L3"):
        s = json.loads((root / "runs/r6/v3/backtest" / k / "score.json").read_text())
        rows.append({"layout": f"S6-{k}", "edit": "v2 layout (v3 judge)", **summary(s)})
    for p in sorted((root / "runs/r6/v3/cp7").glob("*/score.json")):
        s = json.loads(p.read_text())
        k = p.parent.name.split("-")[1]
        rows.append({"layout": f"S6-{k}", "edit": p.parent.name, **summary(s)})
    df = pd.DataFrame(rows)
    base = df[df.edit.str.startswith("v2")].set_index("layout")
    df["d_robust_npv"] = df.robust_npv - df.layout.map(base.robust_npv)
    df["d_capex_p50"] = df.capex_p50 - df.layout.map(base.capex_p50)
    sign0 = df.layout.map(base.robust_npv_p90cost) > 0
    df["p90cost_sign_kept"] = (df.robust_npv_p90cost > 0) == sign0
    df["adoptable_A_r6_105"] = (df.d_robust_npv > 0) & df.p90cost_sign_kept
    df["label"] = LABEL
    out = root / "runs/r6/v3/cp7/cp7.csv"
    df.to_csv(out, index=False)
    typer.echo(df.drop(columns="label").round(1).to_string())


def reach(layouts: list[Path], out: Path, root: Path) -> dict:
    env = dict(os.environ, R6_JUDGE_ROOT=str(root / "judge" / se.JUDGE))
    env.pop("PYTHONPATH", None)
    subprocess.run(
        [
            str(root / ".venv/bin/python"),
            str(root / "optimise/reach.py"),
            "--layouts",
            ",".join(str(p) for p in layouts),
            "--out",
            str(out),
        ],
        cwd=root / "judge" / se.JUDGE,
        env=env,
        check=True,
    )
    return json.loads(out.read_text())


@app.command("top5")
def top5_cmd(
    final: str = typer.Option(..., help="L1=<layout yaml>:<v3 score dir>,... for L1..L5"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    t5, t2 = root / "runs/r6/top5", root / "runs/r6/top5-v2"
    if t5.exists() and not t2.exists():
        t5.rename(t2)
    t5.mkdir(parents=True, exist_ok=True)
    picks = {}
    for item in final.split(","):
        k, rest = item.split("=")
        lay, sdir = rest.split(":")
        picks[k] = (root / lay, root / sdir)
    lays = []
    for k, (lay, sdir) in sorted(picks.items()):
        d = t5 / k
        if d.exists():
            shutil.rmtree(d)
        subprocess.run(["cp", "-cR", str(sdir), str(d)], check=True)
        shutil.copy(lay, t5 / f"{k}.layout.yaml")
        (d / "layout-source.txt").write_text(
            f"{lay.relative_to(root)}\nscored in {sdir.relative_to(root)}\n"
        )
        lays.append(t5 / f"{k}.layout.yaml")
    r = reach(lays, root / "runs/r6/v3/national_reach.json", root)
    for k in picks:
        sp = t5 / k / "score.json"
        s = json.loads(sp.read_text())
        nr = r["layouts"][str(t5 / f"{k}.layout.yaml")]
        s["national_reach_reported_only"] = {
            "note": "reported column only, never in the score (CP7-5, A-r6-104); "
            "added by optimise.report_v3 after the judge run",
            "population_2025_within_min": {b: nr["layout"][b] for b in ("60", "120")},
            "S1_population_2025_within_min": {b: r["S1"][b] for b in ("60", "120")},
            "gain_vs_S1": nr["gain"],
            "within_120_with_access_cap": nr["layout"]["120_within_access_cap"],
            "population_total_2025": r["population_total_2025"],
        }
        sp.write_text(json.dumps(s, indent=1, default=float) + "\n")
        lay = yaml.safe_load((t5 / f"{k}.layout.yaml").read_text())
        report.layout_map(
            lay,
            t5 / f"{k}-map.png",
            f"S6-{k} ({lay.get('id', '')}): existing + committed + hypothetical layout",
            root,
        )
    report.scorecards_cmd(root)
    df = pd.read_csv(t5 / "top5.csv")
    for k in picks:
        nr = json.loads((t5 / k / "score.json").read_text())["national_reach_reported_only"]
        i = df.index[df.layout == f"S6-{k}"]
        df.loc[i, "national_reach_60_reported_only"] = nr["population_2025_within_min"]["60"]
        df.loc[i, "national_reach_120_reported_only"] = nr["population_2025_within_min"]["120"]
        df.loc[i, "national_reach_gain_120_reported_only"] = nr["gain_vs_S1"]["120"]
        df.loc[i, "national_reach_gain_60_reported_only"] = nr["gain_vs_S1"]["60"]
        df.loc[i, "variants"] = json.dumps(
            [
                c
                for c in yaml.safe_load((t5 / f"{k}.layout.yaml").read_text())["corridors"]
                if set(c) - {"id", "phase"}
            ]
        )
    df.to_csv(t5 / "top5.csv", index=False)
    typer.echo(df.T.to_string())


if __name__ == "__main__":
    app()
