"""Distributional analysis per case (W4/W7, R5; method docs/social.md Part B, DfT TAG A4.2).

Who gains: user benefits (rule-of-a-half generalised-cost savings, valued at the purpose VoT)
are allocated half to the origin and half to the destination zone of each OD (docs/social.md B1
step 3a), summed by region, and compared with each region's population share (TAG A4.2 share of
benefits vs share of population). The regional shares come from the medium population scenario at
2050 (A-cba-310); the P10/P50/P90 apply the shares to the Monte Carlo PV of user benefits.
Income bands: no income-by-zone source exists (docs/social.md B4), so the band table uses the
proxy named there: regions grouped into terciles of the Saudi unemployment rate (GASTAT LFS
Q4 2025, S-soc-015/016; A-cba-311), a regional labour-market proxy, not household income.
Who pays: the fiscal cost to the state (PV, fully public delivery, A-cba-312) and the fares paid
by users (PV of fare revenue); fare-to-income ratios are not available (no income data).
Who is left out: towns of 10,000+ in the regions the case serves with no station within the
access distance (A-cba-313) after the case; freight-only route-km.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from common import REPO_ROOT
from economics import benefits, demandruns

GROUP = "un_wpp_medium-2050"
REGIONS = (
    "riyadh",
    "makkah",
    "madinah",
    "qassim",
    "eastern",
    "asir",
    "tabuk",
    "hail",
    "northern_borders",
    "jazan",
    "najran",
    "al_baha",
    "al_jouf",
)


def haversine_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def regional_shares(case_id: str, vot: dict[str, float], root: Path = REPO_ROOT) -> pd.DataFrame:
    z = demandruns.load_zone_inputs(case_id, GROUP, root)
    val = sum(z[f"user_min_{k}"] * vot[k] / 60.0 for k in benefits.PURPOSES)
    z = z.assign(ub=val)
    g = z.groupby("region").agg(ub=("ub", "sum"), population=("population", "sum"))
    g = g.reindex(list(REGIONS)).fillna(0.0)
    tot_ub = g.ub.sum()
    g["benefit_share"] = g.ub / tot_ub if tot_ub != 0 else 0.0
    g["population_share"] = g.population / g.population.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        g["benefit_to_population"] = g.benefit_share / g.population_share
    return g.reset_index()


def unemployment_bands(p: Any) -> dict[str, str]:
    raw = p.raw.get("lfs_q4_2025_saudi_unemployment_pct", {}) or {}
    vals = {k: float(v) for k, v in (raw.get("by_region") or {}).items()}
    if not vals:
        return {}
    s = pd.Series(vals).sort_values()
    terc = pd.qcut(s.rank(method="first"), 3, labels=["low", "middle", "high"])
    return {k: f"{v} unemployment tercile" for k, v in terc.items()}


def stations_of(lines: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for ln in lines:
        for s in ln.get("stations", []):
            if s.get("lat") is not None and s.get("lon") is not None:
                rows.append({"line": ln["id"], "lat": float(s["lat"]), "lon": float(s["lon"])})
    return pd.DataFrame(rows)


def left_out(case: Any, p: Any, root: Path = REPO_ROOT) -> tuple[pd.DataFrame, list[str]]:
    """Towns of 10,000+ in the served regions without a station within the access distance."""
    from access import railgraph

    cfg = yaml.safe_load((root / "cities/ksa/assumptions/access_network.yaml").read_text())
    base = "S1" if case.candidate else "S0"
    lines = railgraph.scenario_lines(
        case.scenario if not case.candidate else "S1",
        cfg,
        root,
        Path(case.candidate) if case.candidate else None,
    )
    st = stations_of(lines)
    reg = pd.read_parquet(root / "cities/ksa/candidates.parquet")
    pop_col = "population" if "population" in reg.columns else "pop"
    reg = reg[reg[pop_col].fillna(0) >= 10_000].copy()
    lat = "lat" if "lat" in reg.columns else "point_lat"
    lon = "lon" if "lon" in reg.columns else "point_lon"
    if case.candidate:
        c = yaml.safe_load((root / case.candidate).read_text(encoding="utf-8"))
        cst = stations_of([c])
    else:
        cst = st
    # served regions: regions of the towns nearest to each case station
    served: set[str] = set()
    for r in cst.itertuples():
        d = haversine_km(r.lat, r.lon, reg[lat].to_numpy(), reg[lon].to_numpy())
        if len(d):
            served.add(str(reg.region.iloc[int(np.argmin(d))]))
    del base
    dmin = np.full(len(reg), np.inf)
    for r in st.itertuples():
        dmin = np.minimum(
            dmin, haversine_km(r.lat, r.lon, reg[lat].to_numpy(), reg[lon].to_numpy())
        )
    reg["nearest_station_km"] = dmin
    thr = p["access_distance_km"].value
    lo = reg[(reg.nearest_station_km > thr) & reg.region.isin(served)]
    name = "name_en" if "name_en" in reg.columns else reg.columns[0]
    g = lo.groupby("region").agg(towns=(name, "count"), population=(pop_col, "sum")).reset_index()
    return g, sorted(served)


def table(
    case: Any, p: Any, draws: pd.DataFrame, pop: str = "un_wpp_medium", root: Path = REPO_ROOT
) -> dict[str, Any]:
    vot = {k: p[f"vot_{k}"].value for k in benefits.PURPOSES}
    sh = regional_shares(case.id, vot, root)
    col = f"pv_user_time_cost|{pop}"
    ub = draws[col].to_numpy() if col in draws else np.zeros(1)
    q = np.percentile(ub, [10, 50, 90])
    sh["user_benefit_pv_p10"] = sh.benefit_share * q[0]
    sh["user_benefit_pv_p50"] = sh.benefit_share * q[1]
    sh["user_benefit_pv_p90"] = sh.benefit_share * q[2]
    bands = unemployment_bands(p)
    sh["proxy_band"] = sh.region.map(bands).fillna("unknown")
    band = (
        sh.groupby("proxy_band")[["benefit_share", "population_share"]].sum().reset_index()
        if bands
        else pd.DataFrame()
    )
    lo, served = left_out(case, p, root)
    return {"regions": sh, "bands": band, "left_out": lo, "served_regions": served}


def fmt(x: float, d: int = 1) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n/a"
    return f"{x:,.{d}f}"
