"""Coefficient sweep (TrafficTwin pattern: one at a time at each range end, plus joint corners) with
monotonicity checks, rank stability and a sensitivity band.

Variants
- `base`: every prior at its central value, R3 settings at base.
- `oat:<key>:low|high`: one utility coefficient at an end of its registered prior range.
- `joint:all_low|all_high|rail_favourable|rail_unfavourable`: every coefficient moved together.
- `set:<name>`: non-coefficient R3 settings (summer season, occupancy ends, purpose method).

The band over variants is a min / median / max over sweep corners, not a probability distribution.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from modechoice.coefficients import (
    MODES,
    UTILITY_KEYS,
    Coefficients,
    Corner,
    Param,
    corner,
    r3_value,
)
from modechoice.mnl import Settings, attribute_matrix, shares


@dataclass(frozen=True)
class Variant:
    id: str
    kind: str
    coefs: Coefficients
    settings: Settings
    description: str


# direction that favours rail for the joint rail corners ("high" = numerically high end)
_RAIL_FAVOURABLE: dict[str, Corner] = {
    "asc.rail": "high",
    "asc.air": "low",
    "asc.bus": "low",
    "ivt.car": "low",
    "ivt.rail": "high",
    "ivt.air": "low",
    "ivt.bus": "low",
    "access_egress": "high",
    "headway": "high",
    "on_time": "high",
}


def _opp(c: Corner) -> Corner:
    return {"low": "high", "high": "low", "base": "base"}[c]


def variants(priors: dict[str, Param], r3: dict[str, Any], settings: Settings) -> list[Variant]:
    base = corner(priors, {})
    out = [Variant("base", "base", base, settings, "all priors central")]
    for k in UTILITY_KEYS:
        for end in ("low", "high"):
            p = priors[k]
            out.append(
                Variant(
                    f"oat:{k}:{end}",
                    "oat",
                    corner(priors, {k: end}),
                    settings,
                    f"{k} = {p.at(end)} ({p.assumption})",
                )
            )
    out.append(
        Variant(
            "joint:all_low",
            "joint",
            corner(priors, dict.fromkeys(UTILITY_KEYS, "low")),
            settings,
            "every coefficient at its numerically low end",
        )
    )
    out.append(
        Variant(
            "joint:all_high",
            "joint",
            corner(priors, dict.fromkeys(UTILITY_KEYS, "high")),
            settings,
            "every coefficient at its numerically high end",
        )
    )
    out.append(
        Variant(
            "joint:rail_favourable",
            "joint",
            corner(priors, _RAIL_FAVOURABLE),
            settings,
            "every coefficient at the end that favours rail (cost at base)",
        )
    )
    out.append(
        Variant(
            "joint:rail_unfavourable",
            "joint",
            corner(priors, {k: _opp(v) for k, v in _RAIL_FAVOURABLE.items()}),
            settings,
            "every coefficient at the end that disfavours rail (cost at base)",
        )
    )
    occ = r3["car"]["occupancy"]["range"]
    mult_hi = r3_value(r3, "summer_penalty", "multiplier", which="high")
    sets = [
        ("set:summer", replace(settings, season="summer"), "summer season, multiplier central"),
        (
            "set:summer_high",
            replace(settings, season="summer", summer_multiplier=mult_hi),
            f"summer season, multiplier {mult_hi}",
        ),
        (
            "set:occupancy_low",
            replace(settings, car_occupancy=float(min(occ))),
            f"car occupancy {min(occ)}",
        ),
        (
            "set:occupancy_high",
            replace(settings, car_occupancy=float(max(occ))),
            f"car occupancy {max(occ)}",
        ),
        ("set:purpose_none", replace(settings, purpose_method="none"), "no purpose scaling"),
        (
            "set:purpose_ivt",
            replace(settings, purpose_method="ivt_scaling"),
            "purpose VoT ratio applied to time coefficients",
        ),
    ]
    out += [Variant(i, "setting", base, s, dsc) for i, s, dsc in sets]
    return out


def run_sweep(pairs: pd.DataFrame, vs: list[Variant]) -> pd.DataFrame:
    keep = ["pair_id", "pair_name", "o", "d", "purpose", "scenario"]
    if "input_variant" in pairs.columns:
        keep.append("input_variant")
    frames = []
    for v in vs:
        r = shares(pairs, v.coefs, v.settings)
        f = r[keep + [f"share_{m}" for m in MODES] + ["logsum", "b_cost_eff", "avail_rail"]].copy()
        f.insert(0, "variant", v.id)
        f.insert(1, "kind", v.kind)
        frames.append(f)
    return pd.concat(frames, ignore_index=True)


def monotonicity(pairs: pd.DataFrame, priors: dict[str, Param], settings: Settings) -> pd.DataFrame:
    """For each coefficient, rail share at its high vs low end on rows where rail is available.

    Theory: dP_r/db = P_r (x_r - xbar(b)) and dxbar/db = Var_P(x) >= 0, so P_r is increasing
    then decreasing in b (one turning point at most). If the derivative signs at both ends agree,
    the share is monotone over the range and the observed change must have that sign
    (pass / FAIL); otherwise the range spans the turning point ("turning point in range",
    not tested)."""
    rows = []
    mask = pairs["avail_rail"].fillna(False).to_numpy(dtype=bool)
    sub = pairs[mask].reset_index(drop=True)
    if "pair_id" not in sub.columns:
        sub["pair_id"] = sub["o"].astype(str) + "-" + sub["d"].astype(str)
    if "scenario" not in sub.columns:
        sub["scenario"] = "input"
    if "purpose" not in sub.columns:
        sub["purpose"] = "all"
    k = MODES.index("rail")
    for key in UTILITY_KEYS:
        lo, hi = corner(priors, {key: "low"}), corner(priors, {key: "high"})
        p_lo = shares(sub, lo, settings)["share_rail"].to_numpy()
        p_hi = shares(sub, hi, settings)["share_rail"].to_numpy()
        x = attribute_matrix(sub, key, settings)

        def dsign(c: Coefficients, x: np.ndarray = x) -> np.ndarray:
            r = shares(sub, c, settings)
            p = r[[f"share_{m}" for m in MODES]].to_numpy()
            return np.sign(np.round(p[:, k] * (x[:, k] - (p * x).sum(axis=1)), 12))

        s_lo, s_hi = dsign(lo), dsign(hi)
        for i in range(len(sub)):
            delta = p_hi[i] - p_lo[i]
            if s_lo[i] == s_hi[i]:
                expected = int(s_lo[i])
                observed = int(np.sign(np.round(delta, 12)))
                status = "pass" if observed == expected else "FAIL"
            else:
                expected, status = 0, "turning point in range"
            rows.append(
                {
                    "coefficient": key,
                    "pair_id": sub.at[i, "pair_id"],
                    "scenario": sub.at[i, "scenario"],
                    "purpose": sub.at[i, "purpose"],
                    "rail_share_low_end": p_lo[i],
                    "rail_share_high_end": p_hi[i],
                    "expected_sign": expected,
                    "status": status,
                }
            )
    return pd.DataFrame(rows)


def rank_stability(long: pd.DataFrame, rail_only: bool = True) -> pd.DataFrame:
    """Per scenario and purpose: Spearman rho of the pair ordering by rail share, base vs variant,
    and whether the ordering is identical. Input-variant rows (same OD, other input) excluded."""
    d = long[long["avail_rail"].fillna(False)] if rail_only else long
    if "input_variant" in d.columns:
        d = d[~d["input_variant"].fillna(False).astype(bool)]
    rows = []
    for (scn, pur), g in d.groupby(["scenario", "purpose"]):
        base = g[g["variant"] == "base"].set_index("pair_id")["share_rail"]
        for vid, gv in g.groupby("variant"):
            s = gv.set_index("pair_id")["share_rail"].reindex(base.index)
            rho = (
                float(spearmanr(base.to_numpy(), s.to_numpy()).statistic) if len(base) > 2 else 1.0
            )
            same = list(base.sort_values().index) == list(s.sort_values().index)
            rows.append(
                {
                    "scenario": scn,
                    "purpose": pur,
                    "variant": vid,
                    "spearman_rho": rho,
                    "same_order": same,
                    "n_pairs": len(base),
                }
            )
    return pd.DataFrame(rows)


def band(long: pd.DataFrame) -> pd.DataFrame:
    """Rail (and other) share range over sweep variants per pair, scenario and purpose."""
    keys = ["pair_id", "scenario", "purpose"]
    base = long[long["variant"] == "base"].set_index(keys)
    out = []
    for m in MODES:
        g = long.groupby(keys)[f"share_{m}"]
        b = pd.DataFrame(
            {
                f"{m}_base": base[f"share_{m}"],
                f"{m}_min": g.min(),
                f"{m}_median": g.median(),
                f"{m}_max": g.max(),
            }
        )
        out.append(b)
    return pd.concat(out, axis=1).reset_index()


def scenario_effect(long: pd.DataFrame, scenario: str = "S1", baseline: str = "S0") -> pd.DataFrame:
    """Rail-share change scenario minus matched baseline (same pair, purpose, variant)."""
    keys = ["variant", "pair_id", "purpose"]
    a = long[long["scenario"] == scenario].set_index(keys)["share_rail"]
    b = long[long["scenario"] == baseline].set_index(keys)["share_rail"]
    d = (a - b).rename("delta_rail_share").reset_index()
    return d


INPUT_KEYS: tuple[str, ...] = (
    "rail_ivt",
    "rail_fare",
    "rail_headway",
    "rail_speed",
    "fuel_price",
    "fuel_economy",
    "parking",
    "air_block",
    "air_fare",
    "air_headway",
    "bus_ivt",
    "bus_fare",
    "bus_headway",
)


def run_input_sweep(
    r3: dict[str, Any],
    skims: pd.DataFrame,
    points: dict[str, tuple[float, float]],
    coefs: Coefficients,
    settings: Settings,
) -> pd.DataFrame:
    """Base coefficients; each R3 input at the low / high end of its registered range, one at a
    time. 'rail_ivt' etc. use each pair's own range; 'rail_speed' moves the Landbridge ratio."""
    from modechoice.pairs import representative_pairs

    frames = []
    for key in INPUT_KEYS:
        for end in ("low", "high"):
            t = representative_pairs(r3, skims, points, inputs={key: end})
            vid = f"in:{key}:{end}"
            frames.append(run_sweep(t, [Variant(vid, "input", coefs, settings, vid)]))
    return pd.concat(frames, ignore_index=True)
