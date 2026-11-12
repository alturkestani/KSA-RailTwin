"""Switching values and tornado charts (W4, R5).

Both use the deterministic central row (cost and duration at their draw medians, multipliers at
1, ridership ratio at its median) with the medium population scenario, the 60-year horizon and the
central social rate (Green Book 2026, A-cba-001), unless stated.

Switching values (Green Book 2026, sensitivity and switching values): the value of one input at
which BCR (without WEIs) = 1, the others held central:
- demand: the share of the MODEL forecast (ridership ratio, 1.0 = as modelled) giving BCR = 1;
- capex: the multiplier on central uplifted capex giving BCR = 1;
- value of time: the multiplier on every purpose's VoT giving BCR = 1;
- discount rate: the constant real rate at which NPV = 0.
Roots by bisection; when no root lies in the search bracket the bound is reported ("> x" / "< x").

Tornado: one-at-a-time swings of each input to its P10 and P90 (draw percentiles, or a
parameter's low/high), NPV and BCR without WEIs at the central settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from economics import cba

POP = "un_wpp_medium"
HORIZON = 60


def _npv_bcr(ctx: Any, row: pd.DataFrame, pop: str = POP, rc: str = cba.CENTRAL_RATE):
    r = cba.evaluate(ctx, row, pop, [HORIZON], [rc])[(HORIZON, rc)]
    return float(r["npv"][0]), float(r["bcr"][0])


def bisect(f, lo: float, hi: float, n: int = 60) -> float | None:
    """Root of f on [lo, hi] (f continuous); None if no sign change."""
    a, b = lo, hi
    fa, fb = f(a), f(b)
    if not (np.isfinite(fa) and np.isfinite(fb)) or fa * fb > 0:
        return None
    for _ in range(n):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def switching_values(ctx: Any, central: pd.DataFrame) -> dict[str, Any]:
    pop = POP if any(ctx.scalars.population == POP) else ctx.scalars.population.iloc[-1]

    def bcr_minus_1(col: str, scale: bool):
        def f(k: float) -> float:
            r = central.copy()
            r[col] = (central[col] * k) if scale else k
            b = _npv_bcr(ctx, r, pop)[1]
            return (b if np.isfinite(b) else 1e6) - 1.0

        return f

    npv0, bcr0 = _npv_bcr(ctx, central, pop)
    out: dict[str, Any] = {
        "label": cba.LABEL,
        "basis": {
            "population": pop,
            "horizon_years": HORIZON,
            "rate_case": cba.CENTRAL_RATE,
            "central_npv_sar_m": npv0,
            "central_bcr": bcr0,
            "central_ridership_ratio": float(central.ridership_ratio.iloc[0]),
        },
    }
    specs = {
        "demand_share_of_model_forecast": ("ridership_ratio", False, 0.0, 20.0),
        "capex_multiplier": ("capex", True, 0.01, 20.0),
        "vot_multiplier": ("vot_mult", True, 0.0, 20.0),
    }
    for name, (col, scale, lo, hi) in specs.items():
        k = bisect(bcr_minus_1(col, scale), lo, hi)
        if k is None:
            f_lo = bcr_minus_1(col, scale)(lo)
            out[name] = {
                "value": None,
                "bound": (f"< {lo}" if f_lo > 0 else f"> {hi}"),
                "note": "BCR = 1 not reached inside the bracket",
            }
        else:
            out[name] = {"value": k}
    out["demand_share_of_model_forecast"]["statement"] = (
        "in the model, demand must be "
        + (
            f"{100 * out['demand_share_of_model_forecast']['value']:.0f} %"
            if out["demand_share_of_model_forecast"]["value"] is not None
            else out["demand_share_of_model_forecast"]["bound"]
        )
        + " of the modelled forecast for BCR = 1"
    )

    def npv_at(r: float) -> float:
        return _npv_bcr(ctx, central, pop, f"const:{r}")[0]

    k = bisect(npv_at, -0.05, 0.5)
    out["discount_rate_npv_zero"] = (
        {"value": k}
        if k is not None
        else {"value": None, "bound": "> 0.5" if npv_at(0.5) > 0 else "< -0.05"}
    )
    return out


def tornado(ctx: Any, draws: pd.DataFrame, central: pd.DataFrame) -> pd.DataFrame:
    p = ctx.p
    pop = POP if any(ctx.scalars.population == POP) else ctx.scalars.population.iloc[-1]
    rows = []

    def add(name: str, col: str | None, lo: float, hi: float, pop_case=None, rc=None):
        res = {}
        for tag, v in (("low", lo), ("high", hi)):
            r = central.copy()
            if col is not None:
                r[col] = v
            pp = pop_case[tag] if pop_case else pop
            npv, bcr = _npv_bcr(ctx, r, pp, rc[tag] if rc else cba.CENTRAL_RATE)
            res[tag] = (npv, bcr)
        rows.append(
            {
                "input": name,
                "low_value": lo,
                "high_value": hi,
                "npv_low": res["low"][0],
                "npv_high": res["high"][0],
                "bcr_low": res["low"][1],
                "bcr_high": res["high"][1],
                "swing_npv": abs(res["high"][0] - res["low"][0]),
            }
        )

    for col, name in (
        ("capex", "capex (uplifted, P10/P90)"),
        ("construction_years", "construction duration (P10/P90)"),
        ("opex", "opex (P10/P90)"),
        ("ridership_ratio", "ridership actual/forecast (P10/P90)"),
    ):
        lo, hi = np.percentile(draws[col], [10, 90])
        add(name, col, float(lo), float(hi))
    v = p["vot_leisure_vfr"]
    add("value of time (low/high)", "vot_mult", v.low / v.value, v.high / v.value)
    for col, key, name in (
        ("carbon_mult", "carbon_value_2025", "carbon value (low/high)"),
        ("crash_mult", "road_crash_cost_sar_per_car_vkm", "crash cost (low/high)"),
        (
            "mec_mult",
            "marginal_external_congestion_cost_sar_per_car_vkm_intercity",
            "congestion cost (low/high)",
        ),
    ):
        q = p[key]
        add(name, col, q.low / q.value, q.high / q.value)
    pops = set(ctx.scalars.population)
    if {"un_wpp_low", "un_wpp_high"} <= pops:
        add(
            "population scenario (UN WPP low/high)",
            None,
            0,
            0,
            pop_case={"low": "un_wpp_low", "high": "un_wpp_high"},
        )
    add(
        "discount rate (TAG 3.5 % declining / flat 7 %)",
        None,
        0,
        0,
        rc={"low": "tag_declining", "high": "flat_7"},
    )
    return pd.DataFrame(rows).sort_values("swing_npv", ascending=False).reset_index(drop=True)


def tornado_png(t: pd.DataFrame, path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 0.45 * len(t) + 1.6))
    base = None
    if len(t):
        base = 0.5 * (t.npv_low.iloc[0] + t.npv_high.iloc[0])
    y = np.arange(len(t))[::-1]
    lo = np.minimum(t.npv_low, t.npv_high) / 1000.0
    hi = np.maximum(t.npv_low, t.npv_high) / 1000.0
    ax.barh(y, hi - lo, left=lo, color="#4C78A8")
    ax.set_yticks(y, t.input)
    ax.set_xlabel("NPV without wider impacts, SAR bn (2025 prices)")
    if base is not None:
        ax.axvline(0, color="#444", lw=0.8)
    ax.set_title(
        f"{title}\nsynthetic demand, uncalibrated: scenario comparison, not a forecast", fontsize=9
    )
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
