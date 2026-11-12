"""STUDY_EXTRA_TRAVEL: pure functions (numpy/pandas only) shared by the study CLI
(`study.extra_travel`) and the frozen-judge entry (`study/extra_travel_judge.py`, which loads this
file by path because it runs with the judge's files first on the import path).

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Not the official
ranking.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

LABEL = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
NOT_OFFICIAL = "not the official ranking"
MODES = ("car", "rail", "air", "bus")
# passenger-km distance column per mode in the frozen OD tables (demand.gravity._with_modes)
PKM_COL = {"car": "road_km", "rail": "rail_km", "air": "air_gc_km", "bus": "road_km"}


def induced_factor(c0: np.ndarray, c1: np.ndarray, eps: float) -> np.ndarray:
    """Trip factor (C1 / C0) ** eps per pair; 1 where either cost is missing or not positive."""
    c0 = np.asarray(c0, dtype=float)
    c1 = np.asarray(c1, dtype=float)
    ok = np.isfinite(c0) & np.isfinite(c1) & (c0 > 0) & (c1 > 0)
    f = np.ones_like(c1)
    f[ok] = (c1[ok] / c0[ok]) ** float(eps)
    return f


ALLOCATIONS = ("proportional", "rail_only")


def induce_od(
    base: pd.DataFrame, scen: pd.DataFrame, eps: float, allocation: str = "proportional"
) -> pd.DataFrame:
    """Scenario OD table of one purpose with trips scaled by the induced factor against the
    baseline's composite cost on the same pair; pairs absent from the baseline keep factor 1.
    eps = 0 returns an identical table.

    allocation "proportional": the pair's mode shares are kept (generated trips split like the
    pair's existing trips). "rail_only" (a rail-favourable bound): on pairs with rail trips and a
    factor above 1, every generated trip is a rail trip; elsewhere proportional."""
    if allocation not in ALLOCATIONS:
        raise ValueError(f"allocation {allocation!r} not in {ALLOCATIONS}")
    b = base[["o", "d", "cost_min"]].rename(columns={"cost_min": "_c0"})
    m = scen.merge(b, on=["o", "d"], how="left")
    f = induced_factor(m["_c0"].to_numpy(), m["cost_min"].to_numpy(), eps)
    t = scen["trips"].to_numpy(dtype=float)
    out = scen.copy()
    out["trips"] = t * f
    rail_only = np.zeros(len(t), dtype=bool)
    if allocation == "rail_only" and "trips_rail" in scen:
        rail_only = (scen["trips_rail"].to_numpy(dtype=float) > 0) & (f > 1.0)
    for mode in MODES:
        c = f"trips_{mode}"
        if c not in out:
            continue
        v = scen[c].to_numpy(dtype=float)
        prop = v * f
        if mode == "rail":
            out[c] = np.where(rail_only, v + t * (f - 1.0), prop)
        else:
            out[c] = np.where(rail_only, v, prop)
    return out


def trips_pkm_by_mode(od: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Trips and passenger-km by mode of one OD table (pkm on each mode's own distance)."""
    out: dict[str, dict[str, float]] = {"trips": {}, "pkm": {}}
    for m in MODES:
        t = od[f"trips_{m}"].to_numpy(dtype=float)
        k = od[PKM_COL[m]].fillna(0.0).to_numpy(dtype=float) if PKM_COL[m] in od else 0.0
        out["trips"][m] = float(t.sum())
        out["pkm"][m] = float((t * k).sum())
    out["trips"]["total"] = float(sum(out["trips"][m] for m in MODES))
    out["pkm"]["total"] = float(sum(out["pkm"][m] for m in MODES))
    return out


def pair_rows(od: pd.DataFrame, a: set[str], b: set[str]) -> pd.DataFrame:
    """Rows of an OD table between zone sets a and b, both directions."""
    return od[(od.o.isin(a) & od.d.isin(b)) | (od.o.isin(b) & od.d.isin(a))]


def pair_extract(od: dict[str, pd.DataFrame], a: set[str], b: set[str]) -> dict[str, Any]:
    """Trips and passenger-km by mode and purpose between two zone sets (both directions)."""
    by_purpose = {p: trips_pkm_by_mode(pair_rows(d, a, b)) for p, d in od.items()}
    allp = pd.concat([pair_rows(d, a, b) for d in od.values()], ignore_index=True)
    tot = trips_pkm_by_mode(allp)
    rail = allp[allp.trips_rail > 0]
    mean_rail_km = (
        float((rail.trips_rail * rail.rail_km).sum() / rail.trips_rail.sum()) if len(rail) else 0.0
    )
    return {"total": tot, "by_purpose": by_purpose, "mean_rail_km": mean_rail_km}


def diff_extract(base: dict[str, Any], scen: dict[str, Any]) -> dict[str, dict[str, float]]:
    """scen - base for the trips/pkm dicts of trips_pkm_by_mode."""
    return {k: {m: scen[k][m] - base[k][m] for m in scen[k]} for k in ("trips", "pkm")}


def port_mix(rows: pd.DataFrame, groups: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Land-entry persons by port group from Table 3 rows (columns port, total) of the chosen
    bulletins; every port must belong to exactly one group (no silent omission)."""
    lookup = {p: g for g, spec in groups.items() for p in spec["ports"]}
    missing = sorted(set(rows.port) - set(lookup))
    if missing:
        raise ValueError(f"land ports without a group: {missing}")
    tot = float(rows.total.sum())
    persons = {g: float(rows[rows.port.map(lookup) == g].total.sum()) for g in groups}
    return {
        "persons": persons,
        "total": tot,
        "shares": {g: (v / tot if tot else 0.0) for g, v in persons.items()},
    }


def land_scenario(
    umrah_total: float,
    land_share: float,
    group_shares: dict[str, float],
    rail_path: dict[str, bool],
    rail_share: float,
    extra_volume: float = 0.0,
    legs_per_person: int = 2,
) -> dict[str, Any]:
    """Foreign Umrah land entrants and their onward rail trips (entry and exit legs between the
    border zone and the first holy city) where the scenario's rail graph has a path. Hajj is not an
    input: Hajj totals are permit-constrained and held fixed."""
    entrants = umrah_total * land_share * (1.0 + extra_volume)
    by_group = {g: entrants * s for g, s in group_shares.items()}
    rail = {
        g: (n * legs_per_person * rail_share if rail_path.get(g, False) else 0.0)
        for g, n in by_group.items()
    }
    return {
        "entrants": entrants,
        "extra_entrants": umrah_total * land_share * extra_volume,
        "by_group": by_group,
        "rail_trips_by_group": rail,
        "rail_trips": float(sum(rail.values())),
    }
