"""Reference-class forecasting: draw capex, schedule and ridership multipliers from
`cities/ksa/costs/uplifts.yaml` (`reference-class-forecasting` skill) and apply them to a base
estimate. Seeded; writes P10/P50/P80/P90 and the full distribution.

Distributions (ratios = outcome / base, or actual / forecast for ridership):
- `empirical`: the percentiles printed by the source; linear interpolation of the inverse CDF
  between them; outside the printed range, lognormal tails whose sigma is fitted to the printed
  points (least squares of ln ratio on the normal score), anchored at the end points.
  A source's printed percentiles are reproduced exactly.
- `lognormal`: `median_ratio` with `p80_ratio` (or `sigma`).
- `normal`: `mean_ratio`, `sd`, truncated below at `floor` (resampled), e.g. Flyvbjerg mean and sd.
- `triangular`: `low`, `mode`, `high`.

CLI:
  uv run python -m costs.rcf apply --estimate runs/costs/<id>/base.yaml \
      --uplifts cities/ksa/costs/uplifts.yaml --seed 1 --draws 10000 --out runs/costs/<id>/rcf/
  uv run python -m costs.rcf show --uplifts cities/ksa/costs/uplifts.yaml
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml
from scipy import stats

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import rng as make_rng
from common.runmeta import seed_option, write_meta
from common.schemas import UpliftSpec, load_uplifts

UPLIFTS = REPO_ROOT / "cities" / "ksa" / "costs" / "uplifts.yaml"
REPORT_P = (10, 50, 80, 90)

app = typer.Typer(add_completion=False, help="Reference-class uplifts (P50/P80 budgets).")


# --------------------------------------------------------------------------- distributions
def pert(
    rng: np.random.Generator,
    low: float,
    mode: float,
    high: float,
    n: int,
    u: np.ndarray | None = None,
) -> np.ndarray:
    """PERT (beta) draws on [low, high] with the given mode (A-cost-004: low/central/high =
    min/mode/max). With `u` (uniforms in (0,1)) the draws are the PERT quantiles of `u`, which lets
    the caller correlate several items (comonotonic, A-cost-003)."""
    if high <= low:
        return np.full(n, float(mode))
    a = 1 + 4 * (mode - low) / (high - low)
    b = 1 + 4 * (high - mode) / (high - low)
    if u is None:
        return low + (high - low) * rng.beta(a, b, n)
    return low + (high - low) * stats.beta.ppf(u, a, b)


def _lognormal_fit(pct: dict[float, float]) -> tuple[float, float]:
    """Least-squares fit of ln(ratio) = mu + sigma * z(p) through printed percentiles."""
    ps = np.array(sorted(pct), dtype=float)
    z = stats.norm.ppf(ps / 100.0)
    y = np.log(np.array([pct[p] for p in sorted(pct)], dtype=float))
    if len(ps) == 1 or np.allclose(z, z[0]):
        return float(y.mean()), 0.0
    sigma, mu = np.polyfit(z, y, 1)
    return float(mu), float(max(sigma, 0.0))


def empirical_ppf(pct: dict[Any, float], u: np.ndarray) -> np.ndarray:
    pts = {float(k): float(v) for k, v in pct.items()}
    ps = np.array(sorted(pts))
    vals = np.array([pts[p] for p in ps])
    if np.any(np.diff(vals) < 0):
        raise ValueError("empirical percentiles must be non-decreasing")
    q = u * 100.0
    out = np.interp(q, ps, vals)
    _, sigma = _lognormal_fit(pts)
    z = stats.norm.ppf(u)
    z0, z1 = stats.norm.ppf(ps[0] / 100.0), stats.norm.ppf(ps[-1] / 100.0)
    lo, hi = q < ps[0], q > ps[-1]
    # tails: lognormal shape (fitted sigma) anchored at the printed end points, so continuous
    out[lo] = vals[0] * np.exp(sigma * (z[lo] - z0))
    out[hi] = vals[-1] * np.exp(sigma * (z[hi] - z1))
    return out


def draw(spec: UpliftSpec, rng: np.random.Generator, n: int) -> np.ndarray:
    p = spec.params
    if spec.distribution == "empirical":
        return empirical_ppf(p["percentiles"], rng.uniform(1e-6, 1 - 1e-6, n))
    if spec.distribution == "lognormal":
        mu = math.log(float(p["median_ratio"]))
        sigma = (
            float(p["sigma"])
            if "sigma" in p
            else (math.log(float(p["p80_ratio"])) - mu) / stats.norm.ppf(0.8)
        )
        return np.exp(mu + sigma * rng.standard_normal(n))
    if spec.distribution == "normal":
        mean, sd, floor = float(p["mean_ratio"]), float(p["sd"]), float(p["floor"])
        x = mean + sd * rng.standard_normal(n)
        bad = x < floor
        while bad.any():  # truncated normal by resampling
            x[bad] = mean + sd * rng.standard_normal(int(bad.sum()))
            bad = x < floor
        return x
    lo, mode, hi = float(p["low"]), float(p["mode"]), float(p["high"])
    return rng.triangular(lo, mode, hi, n) if hi > lo else np.full(n, mode)


def select(
    uplifts: list[UpliftSpec], applies_to: str, line_type: str, stage: str, uplift_id: str = ""
) -> UpliftSpec:
    """Pick the uplift: an explicit id (any role), else a `role: default` entry with the most
    specific line type (exact > rail > all) and stage (exact > n/a > the class's only stage)."""
    if uplift_id:
        for u in uplifts:
            if u.id == uplift_id:
                return u
        raise KeyError(uplift_id)
    pool = [u for u in uplifts if u.applies_to == applies_to and u.role == "default"]
    order = (line_type, "rail", "all")
    for lt in order:
        for st in (stage, "n/a"):
            for u in pool:
                if u.line_type == lt and u.stage == st:
                    return u
    for lt in order:  # the reference class exists at one stage only (e.g. ridership)
        cands = [u for u in pool if u.line_type == lt]
        if len(cands) == 1:
            return cands[0]
    raise KeyError(f"no {applies_to} uplift for line_type={line_type} stage={stage}")


def percentiles(x: np.ndarray, ps: tuple[int, ...] = REPORT_P) -> dict[str, float]:
    return {f"P{p}": float(np.percentile(x, p)) for p in ps}


# --------------------------------------------------------------------------- apply
def apply(
    base: dict[str, Any],
    uplifts: list[UpliftSpec],
    seed: int,
    draws: int,
    base_draws: np.ndarray | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Multiply base draws by uplift draws. `base` needs `line_type`, `stage` and `capex` (low,
    central, high; or `base_draws`). Optional `schedule_years` (low, central, high) and
    `ridership_base` (any positive number, e.g. 1.0 for a ratio)."""
    rng = make_rng(seed)
    lt, st = base["line_type"], base["stage"]
    out: dict[str, Any] = {"label": LABEL, "seed": seed, "draws": draws, "uplifts_used": {}}
    cols: dict[str, np.ndarray] = {}
    c = base["capex"]
    cap = (
        base_draws
        if base_draws is not None
        else pert(rng, float(c["low"]), float(c["central"]), float(c["high"]), draws)
    )
    u_cap = select(uplifts, "capex", lt, st, base.get("uplift_capex", ""))
    m_cap = draw(u_cap, rng, draws)
    cols |= {"capex_base": cap, "capex_multiplier": m_cap, "capex_uplifted": cap * m_cap}
    out["uplifts_used"]["capex"] = {
        "id": u_cap.id,
        "source": u_cap.source,
        "assumption_id": u_cap.assumption_id,
    }
    out["capex"] = {
        "unit": c.get("unit", "SAR_m"),
        "base_estimate": percentiles(cap, (10, 50, 90)),
        "multiplier": percentiles(m_cap),
        "uplifted": percentiles(cap * m_cap),
    }
    if "schedule_years" in base:
        s = base["schedule_years"]
        sch = pert(rng, float(s["low"]), float(s["central"]), float(s["high"]), draws)
        u_s = select(uplifts, "schedule", lt, st, base.get("uplift_schedule", ""))
        m_s = draw(u_s, rng, draws)
        cols |= {"schedule_base_years": sch, "schedule_multiplier": m_s}
        cols["schedule_uplifted_years"] = sch * m_s
        overrun_months = (sch * m_s - sch) * 12.0
        cols["schedule_overrun_months"] = overrun_months
        out["uplifts_used"]["schedule"] = {
            "id": u_s.id,
            "source": u_s.source,
            "assumption_id": u_s.assumption_id,
        }
        out["schedule"] = {
            "base_years": percentiles(sch, (10, 50, 90)),
            "multiplier": percentiles(m_s),
            "uplifted_years": percentiles(sch * m_s),
            "overrun_months": percentiles(overrun_months),
        }
    if "ridership_base" in base:
        u_r = select(uplifts, "ridership", lt, st, base.get("uplift_ridership", ""))
        m_r = draw(u_r, rng, draws)
        cols["ridership_ratio"] = m_r
        cols["ridership_uplifted"] = float(base["ridership_base"]) * m_r
        out["uplifts_used"]["ridership"] = {
            "id": u_r.id,
            "source": u_r.source,
            "assumption_id": u_r.assumption_id,
        }
        out["ridership"] = {
            "note": "actual/forecast ratio applied to a synthetic, uncalibrated demand output",
            "ratio": percentiles(m_r),
            "uplifted": percentiles(float(base["ridership_base"]) * m_r),
        }
    df = pd.DataFrame(cols)
    df.insert(0, "draw", np.arange(draws))
    return out, df


@app.command("apply")
def apply_cmd(
    estimate: Path = typer.Option(..., "--estimate", help="base.yaml written by costs.estimate"),
    uplifts: Path = typer.Option(UPLIFTS, "--uplifts"),
    seed: int = seed_option(),
    draws: int = typer.Option(10_000, "--draws", min=100),
    out: Path = typer.Option(..., "--out"),
) -> None:
    """Draw multipliers and write summary.yaml, distribution.parquet and meta.json."""
    base = yaml.safe_load(estimate.read_text(encoding="utf-8"))
    ups = load_uplifts(uplifts)
    summary, df = apply(base, ups, seed, draws)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.yaml").write_text(yaml.safe_dump(summary, sort_keys=False), "utf-8")
    df.to_parquet(out / "distribution.parquet", index=False)
    write_meta(
        out,
        seed,
        {"base": base, "uplifts": [u.model_dump() for u in ups], "draws": draws},
        {"assumptions": sorted({v["assumption_id"] for v in summary["uplifts_used"].values()})},
    )
    cu = summary["capex"]["uplifted"]
    typer.echo(f"capex uplifted P50 {cu['P50']:,.0f} / P80 {cu['P80']:,.0f} ({LABEL})")


@app.command()
def show(uplifts: Path = typer.Option(UPLIFTS, "--uplifts"), draws: int = 20_000) -> None:
    """Print each uplift's P10/P50/P80/P90 multiplier (seed 1)."""
    for u in load_uplifts(uplifts):
        q = percentiles(draw(u, make_rng(1), draws))
        typer.echo(
            f"{u.id:40s} {u.applies_to:9s} "
            + " ".join(f"{k} {v:.3f}" for k, v in q.items())
            + f"  ({u.source}, {u.assumption_id})"
        )


if __name__ == "__main__":
    app()
