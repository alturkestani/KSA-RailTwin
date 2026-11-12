"""Why does Badr rank where it does? (CP3 decision 8, Tariq 31 Oct 2026; R3 prompt addendum.)

Re-scores the R2 long list with the screening funnel's own functions (screening.funnel,
read-only) and reports one candidate's criterion values, its rank in the base case, across the
10 one-at-a-time sweep corners (A-screen-029) and in the three R2 sensitivities (5k threshold,
linear rail gap, committed layer), and under the commute-criterion design variants Tariq asked
for: each tier factor (A-screen-026) and all of them together at x0.75 / x1.25, and the 40-120 km
band (A-screen-005) shifted and widened/narrowed by 25 %. Run on the register before and after
the R3 DEM terrain update, so the effect of the terrain fill is shown separately.

Label: screening input, not a forecast.

uv run python -m demand.badr explain --row-key madinah:node:1237968680 --seed 1 \
    --out runs/r3/badr/
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pandas as pd
import typer

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta
from screening.funnel import (
    CRITERIA,
    base_weights,
    criteria_scores,
    load_config,
    long_list,
    metro_table,
    rank,
    rng,
    score,
    sweep_corners,
)

WEIGHTS = Path("cities/ksa/assumptions/screening_weights.yaml")
BADR = "madinah:node:1237968680"
LABEL = "screening input, not a forecast"

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Rank explanation for one screening candidate."""


def _ranks(
    register: pd.DataFrame,
    cfg: dict,
    seed: int,
    threshold: int = 10000,
    gap_how: str | None = None,
    use_committed: bool | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Base and corner ranks over the long list (same tiebreak as screening.funnel.run_score)."""
    cfg = copy.deepcopy(cfg)
    if use_committed is not None:
        cfg["long_list"]["use_committed"] = {"value": use_committed}
    ll = long_list(register, cfg, threshold, 5000)
    cand = ll[ll["funnel_stage"] == "long"].copy()
    crit = criteria_scores(cand, metro_table(register, cfg), cfg, gap_how)
    w0 = base_weights(cfg)
    tiebreak = pd.Series(rng(seed).permutation(len(cand)), index=cand.index)
    rk = {"base": rank(score(crit, w0), tiebreak)}
    for label, w in sweep_corners(w0, float(cfg["sweep"]["fraction"]["value"])):
        rk[label] = rank(score(crit, w), tiebreak)
    rk = pd.DataFrame(rk)
    rk.index = cand["row_key"].to_numpy()
    crit.index = cand["row_key"].to_numpy()
    return rk, crit


def _commute_variants(cfg: dict) -> dict[str, dict]:
    """A-screen-026 tier factors and the A-screen-005 band, each varied by 25 %."""
    out: dict[str, dict] = {}
    tiers = cfg["criteria"]["commute"]["tier_factor"]
    for f, tag in ((0.75, "x0.75"), (1.25, "x1.25")):
        for t in tiers:
            c = copy.deepcopy(cfg)
            c["criteria"]["commute"]["tier_factor"][t]["value"] *= f
            out[f"tier{t}_{tag}"] = c
        c = copy.deepcopy(cfg)
        for t in tiers:
            c["criteria"]["commute"]["tier_factor"][t]["value"] *= f
        out[f"all_tiers_{tag}"] = c
    lo, hi = cfg["criteria"]["commute"]["band_km"]["value"]
    bands = {
        "band_shift_x0.75": (lo * 0.75, hi * 0.75),
        "band_shift_x1.25": (lo * 1.25, hi * 1.25),
        "band_wide": (lo * 0.75, hi * 1.25),
        "band_narrow": (lo * 1.25, hi * 0.75),
    }
    for name, (a, b) in bands.items():
        c = copy.deepcopy(cfg)
        c["criteria"]["commute"]["band_km"]["value"] = [a, b]
        out[name] = c
    return out


def explain(register: pd.DataFrame, cfg: dict, key: str, seed: int) -> dict[str, Any]:
    rk, crit = _ranks(register, cfg, seed)
    if key not in rk.index:
        return {"row_key": key, "in_long_list": False}
    w0 = base_weights(cfg)
    row = crit.loc[key]
    n = len(rk)
    res: dict[str, Any] = {
        "row_key": key,
        "in_long_list": True,
        "n_long": n,
        "criteria": {c: round(float(row[c]), 4) for c in CRITERIA},
        "weighted_contribution": {c: round(float(row[c] * w0[c]), 4) for c in CRITERIA},
        "score": round(float(score(crit, w0)[key]), 4),
        "rank_base": int(rk.at[key, "base"]),
        "rank_corners": {c: int(rk.at[key, c]) for c in rk.columns if c != "base"},
        "rank_corner_range": [int(rk.loc[key].min()), int(rk.loc[key].max())],
        "long_list_criterion_median": {c: round(float(crit[c].median()), 4) for c in CRITERIA},
        "share_of_long_list_with_commute_gt_0": round(float((crit["commute"] > 0).mean()), 4),
        "commute_rank_among_long_list": int((crit["commute"] > row["commute"]).sum()) + 1,
    }
    sens = {}
    for name, kw in {
        "threshold_5k": {"threshold": 5000},
        "linear_gap": {"gap_how": "linear"},
        "committed_layer": {"use_committed": True},
    }.items():
        r, _ = _ranks(register, cfg, seed, **kw)
        sens[name] = (
            {
                "rank": int(r.at[key, "base"]),
                "n_long": len(r),
                "range": [int(r.loc[key].min()), int(r.loc[key].max())],
            }
            if key in r.index
            else {"rank": None, "n_long": len(r)}
        )
    res["sensitivities"] = sens
    var = {}
    for name, c in _commute_variants(cfg).items():
        r, cr = _ranks(register, c, seed)
        var[name] = {
            "commute": round(float(cr.at[key, "commute"]), 4),
            "rank": int(r.at[key, "base"]),
            "range": [int(r.loc[key].min()), int(r.loc[key].max())],
        }
    res["commute_design_variants"] = var
    # counterfactual: no commute criterion at all (weight 0, others renormalised)
    w = {k: (0.0 if k == "commute" else v) for k, v in w0.items()}
    t = sum(w.values())
    w = {k: v / t for k, v in w.items()}
    tb = pd.Series(rng(seed).permutation(n), index=crit.index)
    res["rank_without_commute_criterion"] = int(rank(score(crit, w), tb)[key])
    res["short_list_top_n"] = int(cfg["short_list"]["top_n"]["value"])
    return res


@app.command("explain")
def explain_cmd(
    row_key: str = typer.Option(BADR, "--row-key"),
    register: Path = typer.Option(Path("cities/ksa/candidates.parquet")),
    before: Path = typer.Option(Path("runs/r3/register_update/candidates_before.parquet")),
    weights: Path = typer.Option(WEIGHTS),
    out: Path = typer.Option(Path("runs/r3/badr")),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Explain one candidate's rank before and after the DEM terrain update; write JSON."""
    cfg = load_config(root / weights)
    res = {"label": LABEL, "seed": seed}
    for tag, path in (("before_dem", before), ("after_dem", register)):
        reg = pd.read_parquet(root / path)
        r = explain(reg, cfg, row_key, seed)
        r["terrain_class_in_register"] = reg.set_index("row_key").at[row_key, "terrain_class"]
        res[tag] = r
    (root / out).mkdir(parents=True, exist_ok=True)
    (root / out / "explain.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    write_meta(
        root / out,
        seed,
        {"row_key": row_key, "register": str(register), "before": str(before)},
        extra={"assumptions": ["A-screen-005", "A-screen-026", "A-screen-029", "A-geo-021"]},
    )
    typer.echo(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    app()
