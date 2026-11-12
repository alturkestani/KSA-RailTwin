"""Screening funnel, first version (W2; `screening-funnel` skill stages 2 and 3).

Stage 2, long list (transparent filters, `cities/ksa/assumptions/screening_weights.yaml`):
governorate centres always pass (rule 2); other rows pass if `screened` and population >=
threshold (A-screen-001; sensitivity A-screen-002) or >= 1 sourced economic role (A-screen-003),
not counting `administrative` (A-screen-009; centres pass by rule 2 anyway).
Rows within `served_km` of an existing or committed station (A-screen-004) go to the "served"
bucket (station additions), not to the score.

Stage 3, short list: weighted multi-criteria score over the long list (rail gap on a capped log
scale, A-screen-021; `--gap-measure linear` gives the old min-max measure as a sensitivity), with a
+/- sweep of each
weight one at a time (renormalised), rank stability and per-candidate stability. Ties are broken
by a seeded permutation, so the same seed gives identical ranks (rule 10).

Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

uv run python -m screening.funnel long-list --in cities/ksa/candidates-pilot.parquet \
    --threshold 10000 --sensitivity 5000 --seed 1
uv run python -m screening.funnel score --weights cities/ksa/assumptions/screening_weights.yaml \
    --sweep 0.25 --seed 1 [--gap-measure linear --run-dir runs/screening-pilot/score-linear-gap]
uv run python -m screening.funnel sensitivity-grid --ratio 0.64 --seed 1   (CP2 P1a, report only)

Population basis (CP2 P1a, Tariq 31 Oct 2026): precedence official > derived corroborated > grid
(A-screen-031); a grid-only population counts for the >= 10k test only if a second independent
method (A-screen-033) agrees within 30 % (A-screen-032). No correction is applied to the base case.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.runmeta import rng, write_meta
from common.schemas import CORROBORATION_BAND, GRID_UNCORROBORATED, TAG_10K, corroborates

LABEL = "pilot, proposed criteria pending CP1; screening input, not a forecast"
LABEL_R2 = "screening input, not a forecast; criteria approved at CP1 (D6a-D10a, 31 Oct 2026)"
CRITERIA = ("population", "rail_gap", "commute", "economic_roles", "terrain")
DEFAULT_WEIGHTS = Path("cities/ksa/assumptions/screening_weights.yaml")
DEFAULT_RUN = Path("runs/screening-pilot")
EARTH_R_KM = 6371.0088  # IUGG mean Earth radius (haversine); a geometry constant, not a KSA fact

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


def load_config(path: Path) -> dict[str, Any]:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    w = sum(cfg["criteria"][c]["weight"]["value"] for c in CRITERIA)
    if not math.isclose(w, 1.0, abs_tol=1e-9):
        raise ValueError(f"weights sum to {w}, not 1")
    return cfg


def file_sha256(path: Path) -> str:
    """Content hash of an input file, so config_hash does not depend on the run directory."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def val(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def haversine_km(lat1: Any, lon1: Any, lat2: float, lon2: float) -> np.ndarray:
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi, dlmb = p2 - p1, np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * EARTH_R_KM * np.arcsin(np.sqrt(a))


def scored_roles(roles: Any, cfg: dict) -> set[str]:
    """Distinct sourced role names that count (A-screen-009 drops `administrative`)."""
    drop = set(val(cfg["criteria"]["economic_roles"].get("exclude_from_score", {"value": []})))
    return {r["role"] for r in roles if r["role"] not in drop}


def gap_measure(dist_km: pd.Series, how: str, cap_km: float) -> pd.Series:
    """Rail-gap criterion in [0, 1] (NaN stays NaN): capped log (A-screen-021) or min-max linear."""
    d = dist_km.astype(float)
    if how == "log_capped":
        return np.log10(1 + d.clip(lower=0, upper=cap_km)) / math.log10(1 + cap_km)
    if how == "linear":
        return _minmax(d)
    raise ValueError(f"unknown rail-gap measure {how!r}")


def rail_distance(df: pd.DataFrame, use_committed: bool = True) -> pd.Series:
    """Distance to the nearest line of the layers in use (A-screen-030 for the pilot)."""
    cols = ["dist_existing_km", "dist_committed_km"] if use_committed else ["dist_existing_km"]
    return df[cols].astype(float).min(axis=1, skipna=True)


# --------------------------------------------------------------- population basis (CP2 P1a)
BASES = ("official", "derived_corroborated", "derived_uncorroborated", "grid_corroborated")
BASES = (*BASES, "grid_unverified", "none")
DEFAULT_UNIVERSE = Path("cities/ksa/zones/settlements.parquet")


def _col(df: pd.DataFrame, name: str) -> pd.Series:
    return df[name] if name in df else pd.Series([None] * len(df), index=df.index, dtype=object)


def population_basis(
    df: pd.DataFrame, band: float = CORROBORATION_BAND, ratio: float = 1.0
) -> pd.DataFrame:
    """Resolve each row's population basis (A-screen-031..033). Returns, per row:

    - `population_basis`: official | derived_corroborated | derived_uncorroborated |
      grid_corroborated | grid_unverified | none (precedence official > derived > grid; a row
      carries one `pop_type`, so the precedence decides which figure a row may hold, and
      corroboration decides whether a grid figure may count for the >= 10k test);
    - `population_eval`: the population used for the test (grid-only figures divided by `ratio`;
      `ratio = 1` is the base case, no correction);
    - `corroboration_rel_diff`: abs(grid - other) / grid for grid rows with a second method;
    - `pop10k_eligible`: True where the population may count for a >= 10k threshold.

    Derived rows are classed corroborated/uncorroborated against the WorldPop grid where the
    table carries `grid_population` (reporting only; Tariq's rule gates grid-only rows, so a
    derived figure keeps counting: A-screen-031, open for CP3).
    """
    ptype = _col(df, "pop_type")
    pop = pd.to_numeric(_col(df, "population"), errors="coerce").astype(float)
    other = pd.to_numeric(_col(df, "pop_corroboration_value"), errors="coerce").astype(float)
    grid_ref = pd.to_numeric(_col(df, "grid_population"), errors="coerce").astype(float)
    is_grid = (ptype == "grid").fillna(False).astype(bool)
    pop_eval = pop.where(~is_grid, pop / ratio)
    rel = pd.Series(np.nan, index=df.index)
    corr = pd.Series(False, index=df.index)
    for i in df.index[is_grid]:
        g, o = pop_eval[i], other[i]
        if not (pd.isna(g) or pd.isna(o)) and g > 0:
            rel[i] = abs(g - o) / g
        corr[i] = corroborates(None if pd.isna(g) else g, None if pd.isna(o) else o, band)
    d_corr = pd.Series(False, index=df.index)
    for i in df.index[(ptype == "derived").fillna(False).astype(bool)]:
        g, d = grid_ref[i], pop[i]
        d_corr[i] = corroborates(None if pd.isna(g) else g, None if pd.isna(d) else d, band)
    basis = np.select(
        [
            pop.isna() | ptype.isna(),
            ptype == "official",
            (ptype == "derived") & d_corr,
            ptype == "derived",
            is_grid & corr,
            is_grid,
        ],
        ["none", "official", "derived_corroborated", "derived_uncorroborated"]
        + ["grid_corroborated", "grid_unverified"],
        default="none",
    )
    out = pd.DataFrame(index=df.index)
    out["population_basis"] = basis
    out["population_eval"] = pop_eval
    out["corroboration_rel_diff"] = rel
    out["pop10k_eligible"] = (pop_eval.notna() & (~is_grid | corr)).astype(bool)
    return out


def tag_10k_rule(
    df: pd.DataFrame, band: float = CORROBORATION_BAND, ratio: float = 1.0
) -> pd.Series:
    """The >= 10k tag under P1a: population >= 10k and (not grid-only, or corroborated)."""
    pb = population_basis(df, band, ratio)
    return ((pb["population_eval"] >= TAG_10K) & pb["pop10k_eligible"]).fillna(False).astype(bool)


def basis_counts(df: pd.DataFrame, ratio: float = 1.0) -> dict[str, Any]:
    """Rows by basis, and grid-only rows >= 10k without and with the ratio correction."""
    pb = population_basis(df)
    grid = (_col(df, "pop_type") == "grid").fillna(False).astype(bool)
    pop = pd.to_numeric(_col(df, "population"), errors="coerce").astype(float)
    return {
        "rows": int(len(df)),
        "by_basis": {b: int((pb["population_basis"] == b).sum()) for b in BASES},
        "grid_only_rows": int(grid.sum()),
        "grid_with_second_method_value": int(
            (
                grid & pd.to_numeric(_col(df, "pop_corroboration_value"), errors="coerce").notna()
            ).sum()
        ),
        "grid_ge_10k_raw": int((grid & (pop >= TAG_10K)).sum()),
        f"grid_ge_10k_raw_div_{ratio:g}": int((grid & (pop / ratio >= TAG_10K)).sum()),
        "tag_10k_rule": int(tag_10k_rule(df).sum()),
        f"tag_10k_rule_div_{ratio:g}": int(tag_10k_rule(df, ratio=ratio).sum()),
    }


def grid_flips(df: pd.DataFrame, ratio: float, key: str) -> pd.DataFrame:
    """Rows whose >= 10k status changes when grid-only populations are divided by `ratio`.

    Two readings, both reported: `rule` (the P1a gate, corroboration re-checked on the corrected
    figure, so flips go both ways) and `raw` (population >= 10k only, flips up only).
    """
    grid = (_col(df, "pop_type") == "grid").fillna(False).astype(bool)
    pop = pd.to_numeric(_col(df, "population"), errors="coerce").astype(float)
    base_rule, sens_rule = tag_10k_rule(df), tag_10k_rule(df, ratio=ratio)
    base_raw = (pop >= TAG_10K).fillna(False)
    sens_raw = (pop.where(~grid, pop / ratio) >= TAG_10K).fillna(False)
    pb0, pb1 = population_basis(df), population_basis(df, ratio=ratio)
    keep = (base_rule != sens_rule) | (base_raw != sens_raw)
    cols = [c for c in (key, "name_en", "name_ar", "region", "pop_type") if c in df]
    out = df.loc[keep, cols].copy()
    out["population_base"] = pop[keep]
    out["population_sens"] = pb1.loc[keep, "population_eval"].round(1)
    out["pop_corroboration"] = _col(df, "pop_corroboration")[keep]
    out["pop_corroboration_value"] = _col(df, "pop_corroboration_value")[keep]
    out["rel_diff_base"] = pb0.loc[keep, "corroboration_rel_diff"].round(4)
    out["rel_diff_sens"] = pb1.loc[keep, "corroboration_rel_diff"].round(4)
    out["tag_10k_rule_base"], out["tag_10k_rule_sens"] = base_rule[keep], sens_rule[keep]
    out["tag_10k_raw_base"], out["tag_10k_raw_sens"] = base_raw[keep], sens_raw[keep]

    def _dir(b: pd.Series, t: pd.Series) -> pd.Series:
        return pd.Series(np.select([~b & t, b & ~t], ["up", "down"], default=""), index=b.index)

    out["flip_rule"] = _dir(base_rule, sens_rule)[keep]
    out["flip_raw"] = _dir(base_raw, sens_raw)[keep]
    return out


# --------------------------------------------------------------------------- stage 2
def long_list(df: pd.DataFrame, cfg: dict, threshold: int, sensitivity: int) -> pd.DataFrame:
    """Flag every row: passes at the threshold, at the sensitivity, served, and why."""
    ll = cfg["long_list"]
    out = df.copy()
    pop = out["population"].astype("Float64")
    has_role = out["economic_roles"].map(lambda r: len(scored_roles(r, cfg)) > 0)
    centre = out["is_governorate_centre"].astype(bool)
    screened = out["screened"].astype(bool)
    dist = rail_distance(out, bool(val(ll.get("use_committed", {"value": True}))))
    out["rail_dist_km"] = dist
    out["served"] = (dist <= val(ll["served_km"])).fillna(False).astype(bool)
    role_ok = has_role & bool(val(ll["role_passes"]))
    pb = population_basis(out)  # CP2 P1a: grid-only figures count for >= 10k only if corroborated
    out["population_basis"] = pb["population_basis"]
    gated = ~pb["pop10k_eligible"] & (pop >= TAG_10K).fillna(False).astype(bool)
    for tag, t in (("pass_threshold", threshold), ("pass_sensitivity", sensitivity)):
        by_pop = (pop >= t).fillna(False).astype(bool)
        if t >= TAG_10K:  # A-screen-031: the gate applies to the >= 10k test, not below it
            by_pop = by_pop & pb["pop10k_eligible"]
        out[tag] = (centre & bool(val(ll["centres_always_pass"]))) | (screened & (by_pop | role_ok))
    reasons = []
    for c, s, p, r, gt in zip(centre, screened, pop, role_ok, gated, strict=True):
        why = []
        if c:
            why.append("governorate centre")
        if s and p is not pd.NA and p >= threshold and not (gt and threshold >= TAG_10K):
            why.append(f"population >= {threshold}")
        if s and gt and threshold >= TAG_10K:
            why.append(GRID_UNCORROBORATED)
        if s and r:
            why.append("sourced role")
        if not s:
            why.append("sweep excluded (note kept)")
        reasons.append("; ".join(why) or "below threshold, no role")
    out["long_list_reason"] = reasons
    out["data_flag"] = np.where(~screened, out["exclusion_reason"].fillna(""), "")
    out["funnel_stage"] = np.select(
        [out["pass_threshold"] & out["served"], out["pass_threshold"]],
        ["served", "long"],
        default="all",
    )
    return out


# --------------------------------------------------------------------------- stage 3
def _minmax(s: pd.Series) -> pd.Series:
    lo, hi = s.min(), s.max()
    if pd.isna(lo):  # criterion missing on every row: neutral, flagged by the caller
        return pd.Series(0.5, index=s.index)
    if hi == lo:
        return s * 0 + 0.5
    return (s - lo) / (hi - lo)


def _fill(s: pd.Series, how: str) -> pd.Series:
    if how == "min":
        return s.fillna(s.min())
    if how == "median":
        return s.fillna(s.median())
    return s.fillna(0.0)


PILOT_REGISTER = Path("cities/ksa/candidates-pilot.parquet")


def resolve_anchor(register: pd.DataFrame, key: str, pilot: pd.DataFrame | None = None) -> str:
    """A-screen-013 anchors are pilot row keys. In the national register the same place may carry
    another key: the pilot wrote `osm` for the OSM type, and a sweep may have re-keyed a place
    (e.g. a relation to its place node). Resolve, in order: the key itself; the same region and
    OSM id; the row of the same region holding the pilot anchor's official figure (unique)."""
    if key in set(register.row_key):
        return key
    region, _, oid = key.split(":", 2)
    same = register[(register.region == region) & (register.osm_id.astype("Int64") == int(oid))]
    if len(same) == 1:
        return str(same.row_key.iloc[0])
    if pilot is not None and key in set(pilot.row_key):
        pop = pilot.set_index("row_key").at[key, "population"]
        hit = register[(register.region == region) & (register.population == pop)]
        if len(hit) == 1:
            return str(hit.row_key.iloc[0])
    raise KeyError(f"metro anchor {key} not found in the register")


def metro_table(register: pd.DataFrame, cfg: dict) -> list[dict[str, Any]]:
    by_key = register.set_index("row_key")
    pilot = pd.read_parquet(PILOT_REGISTER) if PILOT_REGISTER.exists() else None
    out = []
    for m in cfg["metros"]:
        rows = by_key.loc[[resolve_anchor(register, a, pilot) for a in m["anchors"]]]
        if rows["population"].isna().any():
            raise ValueError(f"metro {m['name']}: an anchor row has no population")
        out.append(
            {
                "name": m["name"],
                "tier": int(m["tier"]),
                "lat": rows["lat"].to_numpy(float),
                "lon": rows["lon"].to_numpy(float),
                "pop": float(rows["population"].sum()),
            }
        )
    return out


def criteria_scores(
    cand: pd.DataFrame, metros: list[dict], cfg: dict, gap_how: str | None = None
) -> pd.DataFrame:
    """Criterion scores in [0, 1] (higher = more attractive) and a missing-value flag."""
    cr = cfg["criteria"]
    out = pd.DataFrame(index=cand.index)
    miss = pd.DataFrame(index=cand.index)
    logpop = np.log10(cand["population"].astype(float))
    miss["population"] = logpop.isna()
    out["population"] = _fill(_minmax(logpop), val(cr["population"]["missing"]))
    gap = cand["rail_dist_km"].astype(float)
    miss["rail_gap"] = gap.isna()
    how = gap_how or val(cr["rail_gap"]["measure_kind"])
    gm = gap_measure(gap, how, float(val(cr["rail_gap"]["cap_km"])))
    out["rail_gap"] = _fill(gm, val(cr["rail_gap"]["missing"]))
    lo, hi = val(cr["commute"]["band_km"])
    tf = {int(k): val(v) for k, v in cr["commute"]["tier_factor"].items()}
    biggest = max(m["pop"] for m in metros)
    lat, lon = cand["lat"].to_numpy(float), cand["lon"].to_numpy(float)
    best = np.zeros(len(cand))
    nearest_name = np.array([""] * len(cand), dtype=object)
    nearest_km = np.full(len(cand), np.inf)
    # R4 (additive, CP4-5a): the band in minutes on min(road, rail in-vehicle) per metro
    minutes = val(cr["commute"].get("measure_kind", {"value": "km"})) == "minutes"
    if minutes:
        lo_m, hi_m = val(cr["commute"]["band_min"])
        mt = pd.read_parquet(REPO_ROOT / val(cr["commute"]["minutes_file"]))
        mt = mt.pivot(index="row_key", columns="metro", values="commute_min")
    for m in metros:
        d = np.min(
            [haversine_km(lat, lon, a, b) for a, b in zip(m["lat"], m["lon"], strict=True)], 0
        )
        val_m = tf[m["tier"]] * math.log10(m["pop"]) / math.log10(biggest)
        if minutes:
            t = cand["row_key"].map(mt[m["name"]]).to_numpy(float)
            inband = (t >= lo_m) & (t <= hi_m)
        else:
            inband = (d >= lo) & (d <= hi)
        best = np.where(inband, np.maximum(best, val_m), best)
        closer = d < nearest_km
        nearest_km = np.where(closer, d, nearest_km)
        nearest_name = np.where(closer, m["name"], nearest_name)
    out["commute"] = best
    miss["commute"] = False
    cap = val(cr["economic_roles"]["cap"])
    n_roles = cand["economic_roles"].map(lambda r: len(scored_roles(r, cfg)))
    out["economic_roles"] = n_roles.map(lambda n: min(n, cap) / cap)
    miss["economic_roles"] = n_roles == 0
    pen = {k: val(v) for k, v in cr["terrain"]["penalty"].items()}
    terr = cand["terrain_class"].map(lambda t: 1.0 + pen[t] if isinstance(t, str) else np.nan)
    miss["terrain"] = terr.isna()
    out["terrain"] = _fill(terr.astype(float), val(cr["terrain"]["missing"]))
    out.attrs["missing"] = miss
    out.attrs["nearest_metro"] = pd.Series(nearest_name, index=cand.index)
    out.attrs["nearest_metro_km"] = pd.Series(nearest_km, index=cand.index)
    return out


def base_weights(cfg: dict) -> dict[str, float]:
    return {c: float(val(cfg["criteria"][c]["weight"])) for c in CRITERIA}


def sweep_corners(weights: dict[str, float], frac: float) -> list[tuple[str, dict[str, float]]]:
    """One-at-a-time corners: each weight x (1 - frac) and x (1 + frac), renormalised to 1."""
    corners = []
    for c in CRITERIA:
        for sign, tag in ((-1, "-"), (1, "+")):
            w = dict(weights)
            w[c] *= 1 + sign * frac
            total = sum(w.values())
            corners.append((f"{c}{tag}{frac:g}", {k: v / total for k, v in w.items()}))
    return corners


def score(crit: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    return sum(crit[c] * weights[c] for c in CRITERIA)


def rank(scores: pd.Series, tiebreak: pd.Series) -> pd.Series:
    """Rank 1 = best; equal scores ordered by the seeded tiebreak (deterministic for a seed)."""
    order = pd.DataFrame({"s": scores.round(12), "t": tiebreak}).sort_values(
        ["s", "t"], ascending=[False, True]
    )
    return pd.Series(np.arange(1, len(order) + 1), index=order.index).reindex(scores.index)


def run_score(
    ll: pd.DataFrame,
    register: pd.DataFrame,
    cfg: dict,
    frac: float,
    seed: int,
    gap_how: str | None = None,
) -> dict[str, Any]:
    cand = ll[(ll["funnel_stage"] == "long")].copy()
    metros = metro_table(register, cfg)
    crit = criteria_scores(cand, metros, cfg, gap_how)
    w0 = base_weights(cfg)
    gen = rng(seed)
    tiebreak = pd.Series(gen.permutation(len(cand)), index=cand.index)
    base = score(crit, w0)
    ranks = {"base": rank(base, tiebreak)}
    scores = {"base": base}
    for label, w in sweep_corners(w0, frac):
        scores[label] = score(crit, w)
        ranks[label] = rank(scores[label], tiebreak)
    top_n = int(val(cfg["short_list"]["top_n"]))
    report_top = int(val(cfg["short_list"]["report_top"]))
    stable_share = float(val(cfg["short_list"]["stable_share"]))
    corners = [k for k in ranks if k != "base"]
    rk = pd.DataFrame(ranks)
    in_top_n = (rk[corners] <= top_n).mean(axis=1)
    in_top_r = (rk[corners] <= report_top).mean(axis=1)
    short = (rk["base"] <= top_n) | (in_top_n >= stable_share)
    base_top = set(rk.index[rk["base"] <= report_top])
    kept_all = {i for i in base_top if all(rk.loc[i, c] <= report_top for c in corners)}
    per_corner_overlap = {c: len(base_top & set(rk.index[rk[c] <= report_top])) for c in corners}
    contrib = pd.DataFrame({c: crit[c] * w0[c] for c in CRITERIA})
    top_idx = rk.index[rk["base"] <= report_top]

    def _clean(d: dict[str, float]) -> dict[str, float | None]:
        return {k: (None if pd.isna(v) else round(float(v), 4)) for k, v in d.items()}

    def _spearman(c: str) -> float | None:
        # undefined (None) when a criterion is constant over the long list
        return None if crit[c].nunique() < 2 else float(crit[c].corr(base, method="spearman"))

    # Kendall tau between every pair of rankings (base + corners), over the whole long list
    names = list(rk.columns)
    taus = [
        float(rk[a].corr(rk[b], method="kendall"))
        for i, a in enumerate(names)
        for b in names[i + 1 :]
    ]
    tau_base = {c: round(float(rk["base"].corr(rk[c], method="kendall")), 4) for c in corners}
    drivers = {
        "mean_share_of_score_top": _clean(contrib.loc[top_idx].div(base[top_idx], axis=0).mean()),
        "mean_share_of_score_all": _clean(contrib.div(base.replace(0, np.nan), axis=0).mean()),
        "spearman_with_score": _clean({c: _spearman(c) for c in CRITERIA}),
    }
    miss = crit.attrs["missing"]
    table = cand[
        ["row_key", "region", "name_en", "name_ar", "governorate", "population", "pop_source"]
    ].copy()
    table = table.join(crit.add_prefix("c_"))
    table["missing"] = miss.apply(lambda r: ",".join(c for c in CRITERIA if r[c]), axis=1)
    table["nearest_metro_calc"] = crit.attrs["nearest_metro"]
    table["nearest_metro_km_calc"] = crit.attrs["nearest_metro_km"].round(1)
    table["score"] = base.round(4)
    table["rank"] = rk["base"]
    table["rank_min"] = rk.min(axis=1)
    table["rank_max"] = rk.max(axis=1)
    table["share_corners_top_n"] = in_top_n.round(3)
    table["share_corners_top_report"] = in_top_r.round(3)
    table["short_list"] = short
    table["data_flag"] = cand["data_flag"]
    table = table.sort_values("rank")
    summary = {
        "label": LABEL,
        "seed": seed,
        "sweep_fraction": frac,
        "weights": w0,
        "rail_gap_measure": gap_how or val(cfg["criteria"]["rail_gap"]["measure_kind"]),
        "rail_gap_cap_km": val(cfg["criteria"]["rail_gap"]["cap_km"]),
        "roles_excluded_from_score": list(
            val(cfg["criteria"]["economic_roles"].get("exclude_from_score", {"value": []}))
        ),
        "corners": corners,
        "n_long": int(len(cand)),
        "n_short": int(short.sum()),
        "top_n": top_n,
        "report_top": report_top,
        "top_report_stable_all_corners": len(kept_all),
        "top_report_stability": round(len(kept_all) / report_top, 4) if report_top else None,
        "per_corner_overlap_top_report": per_corner_overlap,
        "per_corner_overlap_top_n": {
            c: len(set(rk.index[rk["base"] <= top_n]) & set(rk.index[rk[c] <= top_n]))
            for c in corners
        },
        "kendall_tau_base_vs_corner": tau_base,
        "kendall_tau_pairs": {
            "n_pairs": len(taus),
            "min": round(min(taus), 4) if taus else None,
            "median": round(float(np.median(taus)), 4) if taus else None,
        },
        "drivers": drivers,
        "missing_counts": {c: int(miss[c].sum()) for c in CRITERIA},
        "metros": [
            {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in m.items()}
            for m in metros
        ],
    }
    sweep = pd.DataFrame({k: v.round(6) for k, v in scores.items()})
    sweep.insert(0, "row_key", cand["row_key"])
    return {"table": table, "summary": summary, "sweep": sweep, "ranks": rk}


# --------------------------------------------------------------------------- CLI
@app.callback()
def _main(
    national: bool = typer.Option(False, "--national", help="R2 label (criteria approved at CP1)"),
) -> None:
    global LABEL
    if national:
        LABEL = LABEL_R2


@app.command("long-list")
def long_list_cmd(
    inp: Path = typer.Option(Path("cities/ksa/candidates-pilot.parquet"), "--in"),
    threshold: int = typer.Option(..., "--threshold", help="A-screen-001"),
    sensitivity: int = typer.Option(..., "--sensitivity", help="A-screen-002"),
    weights: Path = typer.Option(DEFAULT_WEIGHTS, "--weights"),
    run_dir: Path = typer.Option(DEFAULT_RUN / "long-list", "--run-dir"),
    seed: int = typer.Option(1, "--seed", min=0),
    use_committed: bool | None = typer.Option(
        None, "--use-committed/--existing-only", help="override A-screen-030 (sensitivity)"
    ),
) -> None:
    """Apply the long-list filters; write longlist.parquet and meta.json."""
    cfg = load_config(weights)
    if use_committed is not None:
        uc = {"value": use_committed, "assumption_id": "A-screen-030"}
        cfg["long_list"]["use_committed"] = uc
    df = pd.read_parquet(inp)
    out = long_list(df, cfg, threshold, sensitivity)
    run_dir.mkdir(parents=True, exist_ok=True)
    out.to_parquet(run_dir / "longlist.parquet", index=False)
    counts = {
        "all": out.groupby("region").size().to_dict(),
        "long_threshold": out[out.funnel_stage == "long"].groupby("region").size().to_dict(),
        "served": out[out.funnel_stage == "served"].groupby("region").size().to_dict(),
        "pass_sensitivity_not_served": out[out.pass_sensitivity & ~out.served]
        .groupby("region")
        .size()
        .to_dict(),
    }
    cfg_ids = {
        "threshold": val(cfg["long_list"]["threshold"]),
        "sensitivity": val(cfg["long_list"]["sensitivity"]),
    }
    write_meta(
        run_dir,
        seed,
        {
            "weights": cfg,
            "threshold": threshold,
            "sensitivity": sensitivity,
            "input": file_sha256(inp),
        },
        {
            "step": "screening.funnel long-list",
            "label": LABEL,
            "counts": counts,
            "yaml_values": cfg_ids,
        },
    )
    (run_dir / "counts.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    typer.echo(json.dumps({k: sum(v.values()) for k, v in counts.items()}))


@app.command("score")
def score_cmd(
    weights: Path = typer.Option(DEFAULT_WEIGHTS, "--weights"),
    sweep: float = typer.Option(..., "--sweep", help="A-screen-029"),
    inp: Path = typer.Option(DEFAULT_RUN / "long-list" / "longlist.parquet", "--in"),
    register: Path = typer.Option(Path("cities/ksa/candidates-pilot.parquet"), "--register"),
    run_dir: Path = typer.Option(DEFAULT_RUN / "score", "--run-dir"),
    seed: int = typer.Option(1, "--seed", min=0),
    gap_measure_opt: str | None = typer.Option(
        None, "--gap-measure", help="log_capped (A-screen-021 default) | linear (sensitivity)"
    ),
) -> None:
    """Score the long list, sweep the weights, write scores, sweep and summary."""
    cfg = load_config(weights)
    res = run_score(
        pd.read_parquet(inp), pd.read_parquet(register), cfg, sweep, seed, gap_measure_opt
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    res["table"].to_parquet(run_dir / "scores.parquet", index=False)
    res["sweep"].to_parquet(run_dir / "sweep.parquet", index=False)
    res["ranks"].assign(row_key=res["sweep"]["row_key"]).to_parquet(
        run_dir / "ranks.parquet", index=False
    )
    (run_dir / "summary.json").write_text(
        json.dumps(res["summary"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_meta(
        run_dir,
        seed,
        {
            "weights": cfg,
            "sweep": sweep,
            "gap_measure": gap_measure_opt,
            "input": file_sha256(inp),
            "register": file_sha256(register),
        },
        {"step": "screening.funnel score", "label": LABEL},
    )
    s = res["summary"]
    typer.echo(
        json.dumps(
            {
                k: s[k]
                for k in (
                    "n_long",
                    "n_short",
                    "top_report_stable_all_corners",
                    "top_report_stability",
                )
            }
        )
    )


@app.command("sensitivity-grid")
def sensitivity_grid_cmd(
    ratio: float = typer.Option(..., "--ratio", help="grid / tabulated median (A-r1a-004)"),
    seed: int = typer.Option(1, "--seed", min=0),
    register: Path = typer.Option(Path("cities/ksa/candidates-pilot.parquet"), "--register"),
    universe: Path = typer.Option(DEFAULT_UNIVERSE, "--universe"),
    run_dir: Path = typer.Option(DEFAULT_RUN / "sens-grid-064", "--run-dir"),
) -> None:
    """Report-only sensitivity (CP2 P1a): divide every grid-only population by --ratio, re-run the
    >= 10k test on the register and the settlement universe, write flips.csv (both directions),
    counts.json and meta.json. The base case is not changed."""
    if ratio <= 0:
        raise typer.BadParameter("ratio must be > 0")
    rng(seed)  # nothing is random here; seeded for rule 10 uniformity
    tables = {"register": (register, "row_key"), "universe": (universe, "settlement_id")}
    flips, counts = [], {}
    for name, (path, key) in tables.items():
        df = pd.read_parquet(path)
        counts[name] = basis_counts(df, ratio)
        f = grid_flips(df, ratio, key).rename(columns={key: "row_id"})
        f.insert(0, "table", name)
        flips.append(f)
    flip_df = pd.concat(flips, ignore_index=True)
    for col in ("flip_rule", "flip_raw"):
        for name in tables:
            sub = flip_df[flip_df.table == name][col]
            counts[name][f"{col}_up"] = int((sub == "up").sum())
            counts[name][f"{col}_down"] = int((sub == "down").sum())
    run_dir.mkdir(parents=True, exist_ok=True)
    flip_df.to_csv(run_dir / "flips.csv", index=False)
    (run_dir / "counts.json").write_text(
        json.dumps(counts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_meta(
        run_dir,
        seed,
        {
            "ratio": ratio,
            "band": CORROBORATION_BAND,
            "register": file_sha256(register),
            "universe": file_sha256(universe),
        },
        {
            "step": "screening.funnel sensitivity-grid",
            "label": LABEL,
            "report_only": True,
            "assumptions": ["A-screen-031", "A-screen-032", "A-screen-033", "A-r1a-004"],
            "counts": counts,
        },
    )
    typer.echo(json.dumps(counts))


if __name__ == "__main__":
    app()
