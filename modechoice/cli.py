"""CLI for `modechoice` (W8 intercity MNL: car, rail, air, bus).

uv run python -m modechoice.cli version
uv run python -m modechoice.cli pairs --seed 1 --out runs/r3/modechoice/pairs-s1/
uv run python -m modechoice.cli shares --od runs/r3/modechoice/pairs-s1/pairs.parquet --seed 1 \
    --out runs/r3/modechoice/shares-pairs-s1/
uv run python -m modechoice.cli sweep --seed 1 --out runs/r3/modechoice/sweep/

Every output carries "synthetic demand, uncalibrated: scenario comparison, not a forecast" and
"coefficients literature-based until survey results exist".
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import typer

from common import REPO_ROOT
from common.cli import make_app
from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from modechoice import pairs as pairs_mod
from modechoice.coefficients import (
    COEF_LABEL,
    PRIORS_PATH,
    R3_PATH,
    UTILITY_KEYS,
    base_coefficients,
    load_priors,
    load_r3,
)
from modechoice.mnl import MODES, Settings, shares
from modechoice.sweep import (
    band,
    monotonicity,
    rank_stability,
    run_input_sweep,
    run_sweep,
    scenario_effect,
    variants,
)

app = make_app("modechoice", "Multinomial logit mode choice over car, rail, air and bus.")


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def _label(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["label"] = LABEL
    df["coef_label"] = COEF_LABEL
    return df


def _assumption_ids(priors: dict, r3: dict) -> list[str]:
    ids = {p.assumption for p in priors.values() if p.assumption}
    text = json.dumps(r3) + PRIORS_PATH.read_text(encoding="utf-8")
    ids |= set(re.findall(r"A-[a-z0-9_]+-\d{3}", text))
    return sorted(ids)


def _config(priors: dict, r3: dict, extra: dict | None = None) -> dict:
    return {
        "priors": {k: [p.value, p.low, p.high] for k, p in priors.items()},
        "r3": r3,
        **(extra or {}),
    }


def _settings(r3: dict, priors: dict, season: str | None) -> Settings:
    s = Settings.from_r3(r3, priors)
    if season:
        s = Settings(**{**s.__dict__, "season": season})
    return s


@app.command("pairs")
def pairs_cmd(
    out: Path = typer.Option(..., "--out", help="run directory"),
    seed: int = seed_option(),
    skims: Path = typer.Option(pairs_mod.SKIMS_PATH, "--skims"),
) -> None:
    """Build the representative OD table (pairs x S0/S1 x purposes) with every attribute."""
    priors, r3 = load_priors(), load_r3()
    t = pairs_mod.representative_pairs(r3, pairs_mod.load_skims(skims), pairs_mod.load_points())
    out.mkdir(parents=True, exist_ok=True)
    _label(t).to_parquet(out / "pairs.parquet", index=False)
    write_meta(
        out,
        seed,
        _config(priors, r3),
        {
            "run_id": out.name,
            "coef_label": COEF_LABEL,
            "inputs": {"skims": _rel(skims), "priors": _rel(PRIORS_PATH), "r3": _rel(R3_PATH)},
            "assumptions": _assumption_ids(priors, r3),
            "n_rows": len(t),
        },
    )
    typer.echo(f"{len(t)} rows -> {out / 'pairs.parquet'}")


@app.command("shares")
def shares_cmd(
    od: Path = typer.Option(..., "--od", help="OD parquet with o, d, purpose and mode attributes"),
    out: Path = typer.Option(..., "--out", help="run directory"),
    seed: int = seed_option(),
    season: str = typer.Option("", "--season", help="other | summer (default from the R3 YAML)"),
    with_band: bool = typer.Option(True, "--band/--no-band", help="also write the sweep band"),
) -> None:
    """Mode shares and logsums per OD row at the prior central values (+ sweep band)."""
    priors, r3 = load_priors(), load_r3()
    settings = _settings(r3, priors, season or None)
    table = pd.read_parquet(od)
    res = shares(table, base_coefficients(priors), settings)
    out.mkdir(parents=True, exist_ok=True)
    _label(res).to_parquet(out / "shares.parquet", index=False)
    extra = {}
    if with_band:
        t = table.copy()
        if "pair_id" not in t.columns:
            t["pair_id"] = t["o"].astype(str) + "-" + t["d"].astype(str)
        if "scenario" not in t.columns:
            t["scenario"] = "input"
        if "pair_name" not in t.columns:
            t["pair_name"] = t["pair_id"]
        long = run_sweep(t, variants(priors, r3, settings))
        _label(band(long)).to_parquet(out / "shares_band.parquet", index=False)
        extra["band"] = (
            "shares_band.parquet: min/median/max over sweep variants (not a distribution)"
        )
    write_meta(
        out,
        seed,
        _config(priors, r3, {"season": settings.season}),
        {
            "run_id": out.name,
            "coef_label": COEF_LABEL,
            "inputs": {"od": _rel(od), "priors": _rel(PRIORS_PATH), "r3": _rel(R3_PATH)},
            "assumptions": _assumption_ids(priors, r3),
            "n_rows": len(res),
            **extra,
        },
    )
    typer.echo(f"{len(res)} rows -> {out / 'shares.parquet'}")


@app.command("sweep")
def sweep_cmd(
    out: Path = typer.Option(..., "--out", help="run directory"),
    seed: int = seed_option(),
    skims: Path = typer.Option(pairs_mod.SKIMS_PATH, "--skims"),
) -> None:
    """Coefficient sweep on the representative pairs: one at a time, joint corners, settings."""
    priors, r3 = load_priors(), load_r3()
    settings = Settings.from_r3(r3, priors)
    sk, pts = pairs_mod.load_skims(skims), pairs_mod.load_points()
    t = pairs_mod.representative_pairs(r3, sk, pts)
    vs = variants(priors, r3, settings)
    coef_long = run_sweep(t, vs)
    input_long = run_input_sweep(r3, sk, pts, base_coefficients(priors), settings)
    long = pd.concat([coef_long, input_long], ignore_index=True)
    mono = monotonicity(t, priors, settings)
    ranks = rank_stability(long)
    bnd = band(long)
    eff = scenario_effect(long)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in [
        ("pairs", t),
        ("sweep_long", long),
        ("monotonicity", mono),
        ("rank_stability", ranks),
        ("band", bnd),
        ("scenario_effect_S1_vs_S0", eff),
    ]:
        _label(df).to_parquet(out / f"{name}.parquet", index=False)
    # small human-readable table for docs/mode-choice.md: rail share, leisure_vfr, every variant
    piv = (
        long[long["purpose"] == "leisure_vfr"]
        .pivot_table(index="variant", columns=["scenario", "pair_id"], values="share_rail")
        .reindex([v.id for v in vs] + sorted(input_long["variant"].unique()))
    )
    piv.columns = [f"{s}:{p}" for s, p in piv.columns]
    piv.round(4).to_csv(out / "rail_share_leisure_vfr.csv")
    counts = mono["status"].value_counts().to_dict()
    write_meta(
        out,
        seed,
        _config(priors, r3),
        {
            "run_id": out.name,
            "coef_label": COEF_LABEL,
            "inputs": {"skims": _rel(skims), "priors": _rel(PRIORS_PATH), "r3": _rel(R3_PATH)},
            "assumptions": _assumption_ids(priors, r3),
            "n_variants": len(vs) + int(input_long["variant"].nunique()),
            "n_coefficient_variants": len(vs),
            "n_input_variants": int(input_long["variant"].nunique()),
            "variants": {v.id: v.description for v in vs},
            "coefficients_swept": list(UTILITY_KEYS),
            "modes": list(MODES),
            "monotonicity": counts,
            "rank_stability_min_rho": float(ranks["spearman_rho"].min()),
            "band_note": "min/median/max over sweep variants, not a probability distribution",
        },
    )
    typer.echo(
        f"{len(vs)} coefficient + {input_long['variant'].nunique()} input variants, "
        f"{len(long)} rows; monotonicity {counts} -> {out}"
    )


if __name__ == "__main__":
    app()
