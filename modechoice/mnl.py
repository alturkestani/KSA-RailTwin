"""Multinomial logit mode choice over car, rail, air and bus (W8), generalised from TrafficTwin's
binary car-vs-Loop logit (docs/loop-mode-choice.md there, read-only).

Utility per traveller and mode m (car = reference, ASC 0):

    V_m = ASC_m
        + b_ivt[m]  * IVT_m                 in-vehicle minutes
        + b_access  * AE_m                  access + egress minutes, summer-penalised (below)
        + b_headway * headway_m             minutes between departures: the prior is a headway
                                            multiplier on the headway itself (S-soc-302) and the
                                            SP design shows "a train every ..."; NOT headway/2
        + b_cost/s_p * cost_m               SAR per traveller; car = per-vehicle cost / occupancy
        + b_ontime  * (on_time_m - ref)     rail and air only; NaN = no term

AE_m = (access + egress) x (1 + outdoor_share_m x (multiplier - 1)) in the summer season, else
(access + egress). s_p is the purpose VoT ratio (A-mode-021, method `cost_scaling`); with
`ivt_scaling` the time coefficients are multiplied by s_p instead; with `none` s_p = 1.

Input OD table columns: o, d, purpose, and per mode m: ivt_min_m, access_min_m, egress_min_m,
headway_min_m, cost_sar_m, ontime_m, avail_m (bool). Missing optional columns default to 0 (times,
cost), NaN (on-time) or False (availability for non-car; car defaults to True).

Output: share_<m> (sum to 1 where any mode is available, 0 where unavailable), logsum (ln sum exp
V, NaN where nothing is available), b_cost_eff (the cost coefficient used on the row, for turning
a logsum change into SAR: dCS = d logsum / -b_cost_eff), any_avail.

"synthetic demand, uncalibrated: scenario comparison, not a forecast";
"coefficients literature-based until survey results exist".
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from modechoice.coefficients import (
    MODES,
    Coefficients,
    Param,
    load_priors,
    load_r3,
    vot_ratios,
)

PURPOSES: tuple[str, ...] = ("commute", "business", "leisure_vfr", "pilgrimage", "tourism")


@dataclass(frozen=True)
class Settings:
    """Non-coefficient model settings (every value from mode_choice_r3.yaml, A-mode-021...041)."""

    season: str = "other"
    summer_multiplier: float = 1.5
    outdoor_share: dict[str, float] = field(
        default_factory=lambda: {"car": 0.0, "rail": 0.3, "air": 0.1, "bus": 0.4}
    )
    ontime_reference: float = 87.5
    car_occupancy: float = 2.0
    purpose_method: str = "cost_scaling"
    vot_ratio: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_r3(cls, r3: dict | None = None, priors: dict[str, Param] | None = None, **kw):
        r3 = r3 or load_r3()
        priors = priors or load_priors()
        sp = r3["summer_penalty"]
        base = cls(
            season=str(sp["default_season"]["value"]),
            summer_multiplier=float(sp["multiplier"]["value"]),
            outdoor_share={"car": 0.0, **{m: float(sp["outdoor_share"][m]) for m in MODES[1:]}},
            ontime_reference=float(r3["on_time"]["reference_pp"]["value"]),
            car_occupancy=float(r3["car"]["occupancy"]["value"]),
            purpose_method=str(r3["purpose"]["method"]["value"]),
            vot_ratio=vot_ratios(r3, priors),
        )
        return cls(**{**base.__dict__, **kw})


def _col(od: pd.DataFrame, name: str, default: float) -> np.ndarray:
    if name in od.columns:
        return od[name].to_numpy(dtype=float)
    return np.full(len(od), default, dtype=float)


def _purpose_scale(od: pd.DataFrame, settings: Settings) -> np.ndarray:
    if settings.purpose_method == "none" or "purpose" not in od.columns:
        return np.ones(len(od))
    if settings.purpose_method not in ("cost_scaling", "ivt_scaling"):
        raise ValueError(f"unknown purpose method {settings.purpose_method}")
    purposes = od["purpose"].astype(str)
    unknown = sorted(set(purposes) - set(settings.vot_ratio))
    if unknown:
        raise ValueError(f"purposes without a VoT ratio: {unknown}")
    return purposes.map(settings.vot_ratio).to_numpy(dtype=float)


def availability(od: pd.DataFrame) -> np.ndarray:
    cols = []
    for m in MODES:
        name = f"avail_{m}"
        if name in od.columns:
            cols.append(od[name].fillna(False).to_numpy(dtype=bool))
        else:
            cols.append(np.full(len(od), m == "car", dtype=bool))
    return np.column_stack(cols)


def utilities(
    od: pd.DataFrame, coefs: Coefficients, settings: Settings
) -> tuple[np.ndarray, np.ndarray]:
    """(V, b_cost_eff): V is (n, 4) in MODES order with -inf where a mode is unavailable."""
    n = len(od)
    s = _purpose_scale(od, settings)
    time_scale = s if settings.purpose_method == "ivt_scaling" else np.ones(n)
    b_cost = coefs.cost / s if settings.purpose_method == "cost_scaling" else np.full(n, coefs.cost)
    summer = settings.season == "summer"
    v = np.empty((n, len(MODES)), dtype=float)
    for j, m in enumerate(MODES):
        ivt = _col(od, f"ivt_min_{m}", 0.0)
        ae = _col(od, f"access_min_{m}", 0.0) + _col(od, f"egress_min_{m}", 0.0)
        if summer:
            ae = ae * (
                1.0 + settings.outdoor_share.get(m, 0.0) * (settings.summer_multiplier - 1.0)
            )
        headway = np.nan_to_num(_col(od, f"headway_min_{m}", 0.0), nan=0.0)
        cost = np.nan_to_num(_col(od, f"cost_sar_{m}", 0.0), nan=0.0)
        if m == "car":
            cost = cost / settings.car_occupancy
        ontime = _col(od, f"ontime_{m}", np.nan)
        ontime_term = np.where(
            np.isnan(ontime), 0.0, coefs.on_time * (ontime - settings.ontime_reference)
        )
        v[:, j] = (
            coefs.asc.get(m, 0.0)
            + time_scale * coefs.ivt[m] * ivt
            + time_scale * coefs.access_egress * ae
            + time_scale * coefs.headway * headway
            + b_cost * cost
            + ontime_term
        )
    avail = availability(od)
    bad = avail & ~np.isfinite(v)
    if bad.any():
        raise ValueError(f"non-finite utility for an available mode in {int(bad.sum())} cells")
    v = np.where(avail, v, -np.inf)
    return v, b_cost


def shares(od: pd.DataFrame, coefs: Coefficients, settings: Settings | None = None) -> pd.DataFrame:
    """Copy of `od` with share_<mode>, logsum, b_cost_eff and any_avail (numerically stable)."""
    settings = settings or Settings.from_r3()
    v, b_cost = utilities(od, coefs, settings)
    any_avail = np.isfinite(v).any(axis=1)
    vmax = np.where(any_avail, np.max(v, axis=1), 0.0)
    ex = np.exp(v - vmax[:, None])  # exp(-inf) = 0 for unavailable modes
    denom = ex.sum(axis=1)
    safe = np.where(any_avail, denom, 1.0)
    p = np.where(any_avail[:, None], ex / safe[:, None], 0.0)
    out = od.copy()
    for j, m in enumerate(MODES):
        out[f"share_{m}"] = p[:, j]
    out["logsum"] = np.where(any_avail, vmax + np.log(safe), np.nan)
    out["b_cost_eff"] = b_cost
    out["any_avail"] = any_avail
    return out


def consumer_surplus_change_sar(
    logsum_base: np.ndarray, logsum_scenario: np.ndarray, b_cost_eff: np.ndarray
) -> np.ndarray:
    """Logsum user benefit per traveller in SAR (W4): (LS_scn - LS_base) / -b_cost. Use this OR the
    rule-of-a-half on generalised cost for the same OD and purpose, never both (no double count)."""
    return (np.asarray(logsum_scenario) - np.asarray(logsum_base)) / -np.asarray(b_cost_eff)


def share_derivative_sign(
    od: pd.DataFrame, coefs: Coefficients, settings: Settings, key: str, mode: str = "rail"
) -> np.ndarray:
    """Analytic sign of d share_mode / d coefficient: P_m (x_m - sum_j P_j x_j) for the attribute
    the coefficient multiplies (ASC of `mode` itself: +1)."""
    res = shares(od, coefs, settings)
    p = res[[f"share_{m}" for m in MODES]].to_numpy()
    k = MODES.index(mode)
    x = attribute_matrix(od, key, settings)
    xbar = (p * x).sum(axis=1)
    d = p[:, k] * (x[:, k] - xbar)
    return np.sign(np.round(d, 12))


def attribute_matrix(od: pd.DataFrame, key: str, settings: Settings) -> np.ndarray:
    """(n, 4) attribute that coefficient `key` multiplies (purpose scaling folded in)."""
    n = len(od)
    s = _purpose_scale(od, settings)
    ts = s if settings.purpose_method == "ivt_scaling" else np.ones(n)
    x = np.zeros((n, len(MODES)))
    for j, m in enumerate(MODES):
        if key == f"asc.{m}":
            x[:, j] = 1.0
        elif key == f"ivt.{m}":
            x[:, j] = ts * _col(od, f"ivt_min_{m}", 0.0)
        elif key == "access_egress":
            ae = _col(od, f"access_min_{m}", 0.0) + _col(od, f"egress_min_{m}", 0.0)
            if settings.season == "summer":
                ae = ae * (
                    1 + settings.outdoor_share.get(m, 0.0) * (settings.summer_multiplier - 1)
                )
            x[:, j] = ts * ae
        elif key == "headway":
            x[:, j] = ts * np.nan_to_num(_col(od, f"headway_min_{m}", 0.0))
        elif key == "cost":
            c = np.nan_to_num(_col(od, f"cost_sar_{m}", 0.0))
            if m == "car":
                c = c / settings.car_occupancy
            x[:, j] = c / s if settings.purpose_method == "cost_scaling" else c
        elif key == "on_time":
            ot = _col(od, f"ontime_{m}", np.nan)
            x[:, j] = np.where(np.isnan(ot), 0.0, ot - settings.ontime_reference)
    # unavailable modes carry NaN attributes but zero probability: neutralise them
    return np.where(availability(od), np.nan_to_num(x, nan=0.0), 0.0)
