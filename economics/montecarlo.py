"""Monte Carlo draws for the CBA (W4, R5).

Joint draws per case (10,000 by default, seeded):
- capex (uplifted) and construction duration: the R1c reference-class draws of the case's cost run
  (runs/costs/<id>/rcf/distribution.parquet, A-rcf-001/-020), SHARED with costs.rcf: the same seed
  gives the same multipliers. `ridership_ratio` comes from the same call to costs.rcf.apply with
  `ridership_base: 1`, appended after the capex and schedule streams so those stay identical
  (test: tests/test_economics_montecarlo.py);
- opex per year and renewals: the costs.estimate draws of the same run (draw-aligned);
- value-of-time multiplier: lognormal with the A-cba-101..105 low/high as its P10/P90 (one
  multiplier for every purpose: perfectly correlated, A-cba-302);
- discount-rate shift for the `drawn` rate case: uniform on the A-cba-304 band;
- externality multipliers (carbon, crash, air quality, congestion) and the WEI elasticity:
  lognormal from their low/high (P10/P90), independent of each other (A-cba-302).
Correlations (A-cba-302): capex and duration as drawn by R1c (independent multipliers on a joint
base draw); ridership independent of costs; VoT independent of demand.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from common import REPO_ROOT

Z90 = 1.2815515655446004  # standard normal P90


def lognormal_from_p10_p90(
    rng: np.random.Generator, value: float, low: float, high: float, n: int
) -> np.ndarray:
    """Multiplier draws (median 1) whose P10/P90 are low/value and high/value."""
    if value <= 0 or low <= 0 or high <= 0 or low == high:
        return np.ones(n)
    lo, hi = np.log(low / value), np.log(high / value)
    sigma = max((hi - lo) / (2 * Z90), 1e-9)
    mu = 0.5 * (hi + lo)
    return np.exp(mu + sigma * rng.standard_normal(n))


def cost_draws(cost_run: Path, root: Path = REPO_ROOT) -> pd.DataFrame:
    """Draw-aligned capex/schedule (rcf) and opex/renewals (estimate) of one cost run."""
    rcf = pd.read_parquet(root / cost_run / "rcf" / "distribution.parquet")
    est = pd.read_parquet(root / cost_run / "distribution.parquet")
    df = rcf.merge(est.drop(columns=["capex_base"]), on="draw", how="left")
    return df


def rcf_base(spec: Path, costing: Path | None, root: Path = REPO_ROOT) -> dict[str, Any]:
    """The costs.rcf base the cost run used (line type, stage, construction-year triple), rebuilt
    from the corridor spec and costing sidecar exactly as costs.estimate builds it."""
    from common.schemas import LineSpec
    from costs.estimate import PROFILES, load_profile

    line = LineSpec.model_validate(yaml.safe_load((root / spec).read_text(encoding="utf-8")))
    prof = load_profile(line, PROFILES, (root / costing) if costing else None)
    st = prof.get("appraisal_stage", "strategic")
    stage = st.get("value", "strategic") if isinstance(st, dict) else st
    return {
        "line_type": line.line_type,
        "stage": stage,
        "capex": {"unit": "SAR_m (2025)"},
        "schedule_years": {
            k: float(prof["construction_years"][k]) for k in ("low", "central", "high")
        },
    }


def ridership_draws(
    cost_run: Path,
    spec: Path,
    costing: Path | None,
    seed: int,
    draws: int,
    root: Path = REPO_ROOT,
) -> pd.DataFrame:
    """costs.rcf.apply on the cost run's own base and base draws (same seed) plus
    `ridership_base: 1`: the capex and schedule multipliers equal the cost run's (the ridership
    stream is drawn last), and `ridership_ratio` is the Flyvbjerg actual/forecast ratio."""
    from common.schemas import load_uplifts
    from costs import rcf

    est = pd.read_parquet(root / cost_run / "distribution.parquet")
    base = rcf_base(spec, costing, root) | {"ridership_base": 1.0}
    ups = load_uplifts(rcf.UPLIFTS)
    _, df = rcf.apply(base, ups, seed, len(est), base_draws=est["capex_base"].to_numpy())
    return df.iloc[:draws].reset_index(drop=True)


def split_runs(value: str | None) -> list[Path]:
    """`cost_run` / `cost_spec` / `cost_costing` may list several runs (comma-separated) for a
    programme case (S1 = Landbridge + Riyadh Rail Link + GCC section)."""
    return [Path(x.strip()) for x in str(value or "").split(",") if x.strip()]


def _one_run(
    cost_run: Path, spec: Path, costing: Path | None, seed: int, draws: int, root: Path
) -> pd.DataFrame:
    cd = cost_draws(cost_run, root).iloc[:draws].reset_index(drop=True)
    rr = ridership_draws(cost_run, spec, costing, seed, draws, root)
    same = np.allclose(rr["capex_multiplier"], cd["capex_multiplier"]) and np.allclose(
        rr["schedule_multiplier"], cd["schedule_multiplier"]
    )
    if not same:
        raise RuntimeError(f"{cost_run}: shared draws differ from the cost run (seed {seed})")
    cd["ridership_ratio"] = rr["ridership_ratio"].to_numpy()
    return cd


def station_only(cd: pd.DataFrame, cost_run: Path, n_stations: int, p: Any, root: Path):
    """S5 station additions: the cost run prices its host segment, but only the new station(s)
    are the case's capex. Base draws follow the trace's station P10/P50/P90 (lognormal through
    P10/P90 around P50, comonotonic with the run's base draws); the R1c multiplier draws are the
    run's own (shared). Opex = A-cba-314 share of station base capex a year; no renewal inside
    the horizon (residual value class `station_unrenewed`, A-cba-305)."""
    from scipy.stats import norm

    tr = pd.read_csv(root / cost_run / "trace.csv")
    st = tr[tr.component == "station[intermediate]"].iloc[0]
    p10, p50, p90 = float(st.P10), float(st.P50), float(st.P90)
    sig = max(np.log(p90 / p10) / (2 * Z90), 1e-9) if p10 > 0 and p90 > p10 else 0.0
    u = (cd["capex_base"].rank(method="first").to_numpy() - 0.5) / len(cd)
    base = n_stations * p50 * np.exp(sig * norm.ppf(u))
    cd = cd.copy()
    cd["capex_base"] = base
    cd["capex_uplifted"] = base * cd["capex_multiplier"].to_numpy()
    cd["opex_per_year"] = base * p["station_opex_share_of_capex"].value
    for h in (30, 40, 60):
        cd[f"renewals_{h}y"] = 0.0
    return cd


def draw_inputs(
    cost_run: Path | str,
    spec: Path | str,
    costing: Path | str | None,
    p: Any,
    seed: int,
    draws: int,
    root: Path = REPO_ROOT,
    rate_band: tuple[float, float] = (-0.005, 0.01),
    station_addition: int = 0,
) -> pd.DataFrame:
    """All Monte Carlo inputs of one case, one row per draw. Several cost runs are summed
    draw by draw (capex, opex, renewals); the construction duration is the longest; the ridership
    ratio is the first run's (one programme-level shortfall, A-cba-302)."""
    runs = split_runs(str(cost_run))
    specs = split_runs(str(spec))
    costs = split_runs(str(costing)) if costing else [None] * len(runs)
    parts = [
        _one_run(r, s, c, seed, draws, root) for r, s, c in zip(runs, specs, costs, strict=True)
    ]
    if station_addition:
        parts = [station_only(parts[0], runs[0], station_addition, p, root)]
    cd = parts[0].copy()
    for col in ("capex_uplifted", "capex_base", "opex_per_year"):
        cd[col] = sum(x[col] for x in parts)
    for h in (30, 40, 60):
        cd[f"renewals_{h}y"] = sum(x[f"renewals_{h}y"] for x in parts)
    cd["schedule_uplifted_years"] = np.max(
        np.vstack([x["schedule_uplifted_years"].to_numpy() for x in parts]), axis=0
    )
    cd["capex_multiplier"] = cd["capex_uplifted"] / cd["capex_base"]
    rng = np.random.default_rng([seed, 5])  # separate stream: never disturbs costs.rcf draws
    out = pd.DataFrame(
        {
            "draw": np.arange(draws),
            "capex": cd["capex_uplifted"].to_numpy(),
            "capex_base": cd["capex_base"].to_numpy(),
            "capex_multiplier": cd["capex_multiplier"].to_numpy(),
            "construction_years": cd["schedule_uplifted_years"].to_numpy(),
            "opex": cd["opex_per_year"].to_numpy(),
            "renewals_30y": cd["renewals_30y"].to_numpy(),
            "renewals_40y": cd["renewals_40y"].to_numpy(),
            "renewals_60y": cd["renewals_60y"].to_numpy(),
            "ridership_ratio": cd["ridership_ratio"].to_numpy(),
        }
    )
    vot = p["vot_leisure_vfr"]
    out["vot_mult"] = lognormal_from_p10_p90(rng, vot.value, vot.low, vot.high, draws)
    out["rate_shift"] = rng.uniform(rate_band[0], rate_band[1], draws)
    for k, key in (
        ("carbon_mult", "carbon_value_2025"),
        ("crash_mult", "road_crash_cost_sar_per_car_vkm"),
        ("aq_mult", "air_quality_cost_sar_per_car_vkm"),
        ("mec_mult", "marginal_external_congestion_cost_sar_per_car_vkm_intercity"),
        ("wei_mult", "agglomeration_elasticity"),
    ):
        q = p[key]
        out[k] = lognormal_from_p10_p90(rng, q.value, q.low, q.high, draws)
    return out
