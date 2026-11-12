"""Discounting (W4, R5): constant and declining (stepped) social discount rates, NPV, IRR, payback.

Declining schedule (HM Treasury Green Book, Oct 2026, para 6.54; A-cba-001): the rate r_k applies
to the years in band k, so the discount factor is the running product
DF(t) = prod_{s=1..t} 1 / (1 + r(s)). Year 0 is the price-base / appraisal year (DF = 1).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

# (first year, last year, rate), years counted from the appraisal year (year 1 = the next year)
Schedule = Sequence[tuple[int, int, float]]

SCHEDULES: dict[str, Schedule] = {
    # A-cba-001 central (CP1 D1a): Green Book 2026 / supplementary guidance (S-cp1-060, S-cp1-061)
    "greenbook_2026": [(1, 30, 0.03), (31, 75, 0.025), (76, 125, 0.0225)],
    # A-cba-001 sensitivity: DfT TAG A1.1 / Data Book table A 1.1.1 (S-cp1-062, S-cp1-063)
    "tag_declining": [(1, 30, 0.035), (31, 75, 0.03), (76, 125, 0.025)],
    # A-cba-002 sensitivities (EC Guide 2014 cohesion 5 %; World Bank 2016 range, 7 %)
    "flat_5": [(1, 125, 0.05)],
    "flat_7": [(1, 125, 0.07)],
}


def rate_by_year(schedule: Schedule, n_years: int) -> np.ndarray:
    """Rate applying in each year 1..n_years (index 0 = year 1)."""
    r = np.full(n_years, np.nan)
    for a, b, x in schedule:
        lo, hi = max(a, 1) - 1, min(b, n_years)
        if hi > lo:
            r[lo:hi] = x
    if np.isnan(r).any():
        last = schedule[-1][2]
        r = np.where(np.isnan(r), last, r)
    return r


def factors(schedule: Schedule, n_years: int) -> np.ndarray:
    """Discount factors for years 0..n_years-1 (DF[0] = 1)."""
    r = rate_by_year(schedule, max(n_years - 1, 0))
    df = np.ones(n_years)
    if n_years > 1:
        df[1:] = np.cumprod(1.0 / (1.0 + r))
    return df


def constant(rate: float) -> Schedule:
    return [(1, 10_000, float(rate))]


def shifted(schedule: Schedule, delta: float) -> Schedule:
    """The schedule with every band moved by `delta` (rate perturbation for Monte Carlo)."""
    return [(a, b, x + delta) for a, b, x in schedule]


def npv(flows: np.ndarray, df: np.ndarray) -> np.ndarray:
    """NPV along the last axis: flows (..., T), df (T,)."""
    return np.asarray(flows) @ np.asarray(df)[: np.asarray(flows).shape[-1]]


def irr(flows: np.ndarray, lo: float = -0.5, hi: float = 1.0, tol: float = 1e-7) -> float:
    """Internal rate of return of one stream (year 0 first) by bisection on NPV(r) = 0.
    Returns NaN when NPV does not change sign on [lo, hi] (no IRR in the bracket)."""
    f = np.asarray(flows, dtype=float)
    t = np.arange(len(f))

    def g(r: float) -> float:
        return float(np.sum(f / (1.0 + r) ** t))

    a, b = lo, hi
    ga, gb = g(a), g(b)
    if not (np.isfinite(ga) and np.isfinite(gb)) or ga * gb > 0:
        return float("nan")
    for _ in range(200):
        m = 0.5 * (a + b)
        gm = g(m)
        if abs(gm) < tol or (b - a) < tol:
            return m
        if ga * gm <= 0:
            b, gb = m, gm
        else:
            a, ga = m, gm
    return 0.5 * (a + b)


def irr_many(flows: np.ndarray, lo: float = -0.5, hi: float = 1.0) -> np.ndarray:
    """Vectorised bisection IRR over rows of `flows` (draws, T); NaN where no sign change."""
    f = np.asarray(flows, dtype=float)
    t = np.arange(f.shape[1])

    def g(r: np.ndarray) -> np.ndarray:
        return np.sum(f / (1.0 + r[:, None]) ** t[None, :], axis=1)

    a = np.full(f.shape[0], lo)
    b = np.full(f.shape[0], hi)
    ga, gb = g(a), g(b)
    ok = np.isfinite(ga) & np.isfinite(gb) & (ga * gb <= 0)
    for _ in range(80):
        m = 0.5 * (a + b)
        gm = g(m)
        left = ga * gm <= 0
        b = np.where(left, m, b)
        a = np.where(left, a, m)
        ga = np.where(left, ga, gm)
    out = 0.5 * (a + b)
    return np.where(ok, out, np.nan)


def payback_year(flows: np.ndarray, df: np.ndarray, opening_index: int) -> float:
    """Years after opening until the cumulative discounted net flow turns non-negative and stays
    so at the horizon end; inf if never within the horizon."""
    c = np.cumsum(np.asarray(flows) * np.asarray(df)[: len(flows)])
    if c[-1] < 0:
        return float("inf")
    neg = np.where(c < 0)[0]
    first = 0 if len(neg) == 0 else int(neg[-1]) + 1
    return float(max(first - opening_index, 0))
