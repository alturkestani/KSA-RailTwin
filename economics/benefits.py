"""Benefit streams of a scenario against its matched baseline (W4, R5; `cba-appraisal` skill).

`extract()` reads one baseline and one scenario demand result (demand.gravity, same zones, seed,
population scenario, year and coefficients: rule 6) and returns the physical changes every stream
is valued from. `value_year()` turns them into SAR for one year. Each stream names the channel it
uses and the channels it excludes (`MATRIX`); `check_no_double_counting()` fails when two streams
count the same channel. Matrix and check are what docs/cba.md prints and the tests run.

User benefits: rule of a half on the composite generalised cost of the mode-choice logsum,
cost_min = -logsum / |b_ivt,car| (car in-vehicle minutes, demand.gravity), per OD and purpose:
    dCS_od = 1/2 (T0 + T1) (C0 - C1)              [generalised minutes]
valued at the appraisal value of time of the purpose (A-cba-101..105). The composite cost already
contains fares and car operating costs, so neither is added again; fare revenue is a transfer to
the operator and enters the cost side (TAG broad transport budget). Vehicle operating costs of
diverted car users are inside dCS (channel `generalised_cost`), never a separate stream.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

PURPOSES = ("commute", "business", "leisure_vfr", "tourism", "pilgrimage")

# stream -> channel it counts; channels it must exclude; whether it is in the core BCR.
# Core streams are added; WEIs are reported separately (BCR with and without); land value uplift
# and the scorecard items are never added (capture potential / qualitative).
MATRIX: dict[str, dict[str, Any]] = {
    "user_time_cost": {
        "channel": "generalised_cost",
        "excludes": [
            "fare_revenue",
            "vehicle_operating_cost_nonfuel",
            "land_value",
            "agglomeration",
        ],
        "contains": ["fare_paid", "vehicle_operating_cost_fuel", "rail_air_on_time"],
        "in": "core",
        "method": "rule of a half on the logsum composite cost per OD and purpose (TAG A1.3); "
        "contains fares and the car FUEL cost (perceived, A-mode-023)",
    },
    "vehicle_operating_cost_nonfuel": {
        "channel": "vehicle_operating_cost_nonfuel",
        "excludes": ["generalised_cost"],
        "in": "core",
        "method": "non-fuel car VOC (resource cost) x change in car vkm; the logsum's car cost is "
        "fuel only, so this channel is not in generalised_cost (TAG A1.3 non-fuel VOC)",
    },
    "reliability": {
        "channel": "travel_time_variability",
        "excludes": ["generalised_cost"],
        "in": "core",
        "method": "SENSITIVITY ONLY (zero in the central case, A-cba-109/112): car journey-time "
        "SD x reliability ratio x VoT, rule of a half, on car trips diverted to rail "
        "(TAG A1.3 sec. 6); the logsum carries an on-time term for rail and air only, so the car "
        "variability channel is not in generalised_cost",
    },
    "fare_revenue": {
        "channel": "fare_revenue",
        "excludes": ["generalised_cost"],
        "in": "cost_side",
        "method": "rail trips x model fare (cost_sar_rail); a transfer from users to the operator, "
        "netted from PVC (TAG A1.1 broad transport budget)",
    },
    "safety": {
        "channel": "road_crashes",
        "excludes": ["generalised_cost"],
        "in": "core",
        "method": "crash cost per car / bus vehicle-km x change in vehicle-km, rail train-km added",
    },
    "carbon": {
        "channel": "ghg_emissions",
        "excludes": ["air_quality"],
        "in": "core",
        "method": "emission factors x change in car / bus vkm, air pkm and rail train-km x "
        "carbon value",
    },
    "air_quality": {
        "channel": "local_pollutants",
        "excludes": ["ghg_emissions"],
        "in": "core",
        "method": "damage cost per vehicle-km (TAG A3 / EU Handbook, transferred)",
    },
    "decongestion_interurban": {
        "channel": "congestion_interurban_vkm",
        "excludes": ["congestion_jeddah_traffictwin", "generalised_cost"],
        "in": "core",
        "method": "marginal external congestion cost x car vkm change outside the Jeddah metro "
        "urban legs (VKT-based)",
    },
    "decongestion_jeddah": {
        "channel": "congestion_jeddah_traffictwin",
        "excludes": ["congestion_interurban_vkm"],
        "in": "core",
        "method": "TrafficTwin matched-control runs (R4 run ids) for the Jeddah urban legs only; "
        "never VKT-valued as well",
    },
    "freight_shift": {
        "channel": "freight_road_to_rail",
        "excludes": ["generalised_cost", "road_crashes", "ghg_emissions"],
        "in": "core",
        "method": "NOT MONETISED (zero, A-cba-309): no open freight OD exists (demand freight.json)"
        "; method if a corridor freight volume is sourced: tkm diverted x (road - rail cost + "
        "truck externalities, cba_freight.yaml); passenger time savings excluded",
    },
    "wei_agglomeration": {
        "channel": "agglomeration",
        "excludes": ["generalised_cost", "land_value"],
        "in": "wei",
        "method": "TAG A2.4 effective density x elasticity x GDP per zone (reported separately)",
    },
    "wei_imperfect_competition": {
        "channel": "output_imperfect_competition",
        "excludes": ["generalised_cost"],
        "in": "wei",
        "method": "uplift on business user benefits (TAG A2.4, reported separately)",
    },
    "land_value_uplift": {
        "channel": "land_value",
        "excludes": ["generalised_cost", "agglomeration"],
        "in": "capture_only",
        "method": "capture potential only, not added (it capitalises the time savings)",
    },
    "tourism_hajj_umrah_capacity": {
        "channel": "visitor_capacity",
        "excludes": ["generalised_cost"],
        "in": "scorecard",
        "method": "international visitors carry no generalised-cost model (demand.intl fixed "
        "share); capacity value not monetised unless sourced (none found): scorecard only",
    },
    "regional_development_vision2030": {
        "channel": "regional_development",
        "excludes": ["agglomeration", "generalised_cost"],
        "in": "scorecard",
        "method": "qualitative scorecard (docs/cba-scorecard.md), not monetised",
    },
}

ADDED = ("core", "wei")  # the only `in` classes whose SAR enter a benefit total


def check_no_double_counting(matrix: dict[str, dict[str, Any]] = MATRIX) -> None:
    """Fail on any double counting among the ADDED streams (core + WEI):
    1. two streams count the same channel;
    2. a stream counts a channel that another stream already contains (e.g. a fuel-cost stream
       next to user benefits, whose composite cost contains fuel);
    3. a stream counts a channel it declares excluded from itself."""
    added = {k: v for k, v in matrix.items() if v["in"] in ADDED}
    seen: dict[str, str] = {}
    for name, s in added.items():
        ch = s["channel"]
        if ch in seen:
            raise ValueError(f"double counting: {name} and {seen[ch]} both count {ch}")
        seen[ch] = name
        if ch in s.get("excludes", []):
            raise ValueError(f"{name} counts {ch}, which it excludes")
    for name, s in added.items():
        for other, t in added.items():
            if other != name and s["channel"] in t.get("contains", []):
                raise ValueError(f"double counting: {name} counts {s['channel']}, inside {other}")


@dataclass
class Physical:
    """Physical changes scenario - baseline for one modelled year (annual)."""

    user_min: dict[str, float] = field(default_factory=dict)  # generalised minutes saved
    user_min_zone: dict[str, np.ndarray] = field(default_factory=dict)  # per zone, 50/50 o/d
    car_trips_diverted: float = 0.0  # car trips (persons) leaving car, all purposes
    car_vkm_interurban: float = 0.0  # change (scenario - baseline), vehicle-km
    car_vkm_jeddah_urban: float = 0.0
    car_pkm_diverted_min: float = 0.0  # baseline car minutes of diverted person trips
    bus_vkm: float = 0.0
    air_pkm: float = 0.0
    rail_pkm: float = 0.0
    rail_trips: float = 0.0
    revenue_sar: float = 0.0  # change in rail fare revenue
    trips_total: float = 0.0
    trips_cost_up: float = 0.0  # diagnostic: baseline trips on pairs whose composite cost rose
    wei_dlnED: np.ndarray | None = None  # per zone: ED1/ED0 - 1 (business/commute GC)

    def scaled(self, k: float) -> Physical:
        """All demand-driven quantities times k (ridership ratio)."""
        return Physical(
            user_min={p: v * k for p, v in self.user_min.items()},
            user_min_zone={p: v * k for p, v in self.user_min_zone.items()},
            car_trips_diverted=self.car_trips_diverted * k,
            car_vkm_interurban=self.car_vkm_interurban * k,
            car_vkm_jeddah_urban=self.car_vkm_jeddah_urban * k,
            car_pkm_diverted_min=self.car_pkm_diverted_min * k,
            bus_vkm=self.bus_vkm * k,
            air_pkm=self.air_pkm * k,
            rail_pkm=self.rail_pkm * k,
            rail_trips=self.rail_trips * k,
            revenue_sar=self.revenue_sar * k,
            trips_total=self.trips_total,
            trips_cost_up=self.trips_cost_up,
            wei_dlnED=None if self.wei_dlnED is None else self.wei_dlnED * k,
        )


def _join(b: pd.DataFrame, s: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    keep = ["o", "d", "trips", "cost_min", *[c for c in cols if c in b.columns]]
    j = b[keep].merge(
        s[[c for c in keep if c in s.columns]], on=["o", "d"], how="outer", suffixes=("_0", "_1")
    )
    for c in ("trips_0", "trips_1"):
        j[c] = j[c].fillna(0.0)
    # an OD present in one run only: no cost there means no admissible trips (gravity drops them);
    # its composite cost is taken from the other run (no change counted on that pair)
    j["cost_min_0"] = j["cost_min_0"].fillna(j["cost_min_1"])
    j["cost_min_1"] = j["cost_min_1"].fillna(j["cost_min_0"])
    return j


def rule_of_half(t0: np.ndarray, t1: np.ndarray, c0: np.ndarray, c1: np.ndarray) -> np.ndarray:
    """Consumer-surplus change per OD (units of c): 1/2 (T0 + T1) (C0 - C1)."""
    return 0.5 * (np.asarray(t0) + np.asarray(t1)) * (np.asarray(c0) - np.asarray(c1))


def effective_density_change(
    gc0: pd.DataFrame,
    gc1: pd.DataFrame,
    zones: pd.DataFrame,
    alpha: float,
    intrazonal_min: np.ndarray,
    cutoff_min: float | None = None,
) -> np.ndarray:
    """TAG A2.4 effective density per zone i, ED_i = sum_j E_j / GC_ij^alpha (own zone with its
    intrazonal cost), with GC in generalised minutes; returns ED1/ED0 - 1 per zone."""
    zid = zones.zone_id.tolist()
    idx = {z: i for i, z in enumerate(zid)}
    n = len(zid)
    col = "jobs" if "jobs" in zones.columns else "jobs_proxy"
    jobs = zones[col].fillna(0.0).to_numpy(dtype=float)

    def ed(gc: pd.DataFrame) -> np.ndarray:
        e = jobs / np.maximum(intrazonal_min, 1.0) ** alpha
        oi = gc.o.map(idx).to_numpy()
        di = gc.d.map(idx).to_numpy()
        c = np.maximum(gc.gc.to_numpy(dtype=float), 1.0)
        ok = ~(np.isnan(oi.astype(float)) | np.isnan(di.astype(float)))
        if cutoff_min:  # 0 or None = no cut-off (TAG A2.4 sets none, A-cba-133)
            ok &= c <= cutoff_min
        oi, di, c = oi[ok].astype(int), di[ok].astype(int), c[ok]
        np.add.at(e, oi, jobs[di] / c**alpha)
        return e

    e0, e1 = ed(gc0), ed(gc1)
    out = np.zeros(n)
    m = e0 > 0
    out[m] = e1[m] / e0[m] - 1.0
    return out


def extract(
    base: dict[str, Any],
    scen: dict[str, Any],
    zones: pd.DataFrame,
    p: Any,
    jeddah_zones: set[str],
    b_ivt_car: float = 0.010,
    asc: dict[str, float] | None = None,
) -> Physical:
    """Physical changes from two demand.gravity results (dicts with 'od' and 'los')."""
    zid = zones.zone_id.tolist()
    idx = {z: i for i, z in enumerate(zid)}
    n = len(zid)
    occ_car = p["car_occupancy_intercity"].value
    occ_bus = p["bus_occupancy_intercity"].value
    l_urban = p["jeddah_urban_leg_km"].value
    out = Physical()
    fare = {}
    for tag, res in (("0", base), ("1", scen)):
        los = res["los"]
        fare[tag] = los.set_index(["o", "d"])["cost_sar_rail"]
    gc_parts: dict[str, list[pd.DataFrame]] = {"0": [], "1": []}
    for purpose in PURPOSES:
        b = base["od"][purpose]
        s = scen["od"][purpose]
        cols = ["trips_car", "trips_rail", "trips_air", "trips_bus", "road_km", "road_min"]
        cols += ["rail_km", "air_gc_km"]
        j = _join(b, s, cols)
        for m in ("car", "rail", "air", "bus"):
            for t in ("0", "1"):
                c = f"trips_{m}_{t}"
                j[c] = j[c].fillna(0.0) if c in j else 0.0
        for c in ("road_km", "road_min", "rail_km", "air_gc_km"):
            j[c] = j[f"{c}_1"].fillna(j[f"{c}_0"]).fillna(0.0)
        cs = rule_of_half(j.trips_0, j.trips_1, j.cost_min_0, j.cost_min_1)
        out.user_min[purpose] = float(np.nansum(cs))
        z = np.zeros(n)
        oi = j.o.map(idx)
        di = j.d.map(idx)
        okz = oi.notna() & di.notna()
        csv = np.nan_to_num(np.asarray(cs, dtype=float))
        np.add.at(z, oi[okz].astype(int).to_numpy(), 0.5 * csv[okz.to_numpy()])
        np.add.at(z, di[okz].astype(int).to_numpy(), 0.5 * csv[okz.to_numpy()])
        out.user_min_zone[purpose] = z
        d_car = j.trips_car_1 - j.trips_car_0
        ends_j = j.o.isin(jeddah_zones).astype(int) + j.d.isin(jeddah_zones).astype(int)
        urban = np.minimum(j.road_km, l_urban * ends_j)
        out.car_vkm_jeddah_urban += float((d_car * urban).sum() / occ_car)
        out.car_vkm_interurban += float((d_car * (j.road_km - urban)).sum() / occ_car)
        div = np.maximum(-d_car, 0.0)
        out.car_trips_diverted += float(div.sum())
        out.car_pkm_diverted_min += float((div * j.road_min).sum())
        out.bus_vkm += float(((j.trips_bus_1 - j.trips_bus_0) * j.road_km).sum() / occ_bus)
        out.air_pkm += float(((j.trips_air_1 - j.trips_air_0) * j.air_gc_km).sum())
        # rail passenger-km on each run's own rail distance
        rk0 = j["rail_km_0"].fillna(0.0) if "rail_km_0" in j else 0.0
        rk1 = j["rail_km_1"].fillna(0.0) if "rail_km_1" in j else 0.0
        out.rail_pkm += float((j.trips_rail_1 * rk1 - j.trips_rail_0 * rk0).sum())
        out.rail_trips += float((j.trips_rail_1 - j.trips_rail_0).sum())
        f0 = fare["0"].reindex(pd.MultiIndex.from_frame(j[["o", "d"]])).to_numpy()
        f1 = fare["1"].reindex(pd.MultiIndex.from_frame(j[["o", "d"]])).to_numpy()
        out.revenue_sar += float(
            np.nansum(j.trips_rail_1.to_numpy() * np.nan_to_num(f1))
            - np.nansum(j.trips_rail_0.to_numpy() * np.nan_to_num(f0))
        )
        out.trips_total += float(j.trips_1.sum())
        up = (j.cost_min_1 - j.cost_min_0).to_numpy() > 1e-6
        out.trips_cost_up += float(j.trips_0.to_numpy()[up].sum())
        if purpose in ("business", "commute"):
            # GC_ij = the logsum composite cost (car in-vehicle minutes), the same measure as
            # the user benefits; TAG A2.4 uses the trip-weighted average over modes (departure,
            # docs/cba.md: the average without mode constants falls when logit users switch for
            # taste reasons). Purposes weighted by the BASELINE trips in both runs (A-cba-307).
            for t in ("0", "1"):
                gc_parts[t].append(
                    pd.DataFrame({"o": j.o, "d": j.d, "gc": j[f"cost_min_{t}"], "w": j.trips_0})
                )
    # WEI: trip-weighted business + commute generalised cost per pair (pairs in both runs)
    gcs = {}
    for t in ("0", "1"):
        g = pd.concat(gc_parts[t], ignore_index=True)
        g = g[g.o != g.d]
        g["wgc"] = g.gc * g.w
        a = g.groupby(["o", "d"], as_index=False)[["wgc", "w"]].sum()
        a = a[a.w > 0]
        a["gc"] = a.wgc / a.w
        gcs[t] = a[["o", "d", "gc"]]
    m = gcs["0"].merge(gcs["1"], on=["o", "d"], suffixes=("_0", "_1"))
    radius_km = np.sqrt(zones.area_km2.fillna(1.0).to_numpy(dtype=float) / np.pi)
    # own-zone cost: TAG A2.4 mean distance in a disc, capped at an urban trip because jobs sit
    # in the towns of a governorate-sized zone, not across its area (A-cba-307)
    intrazonal = np.minimum(
        (2.0 / 3.0) * radius_km / p["intrazonal_speed_kmh"].value * 60.0,
        p["intrazonal_gc_cap_min"].value,
    )
    cut = p.get("effective_density_cutoff_min")
    out.wei_dlnED = effective_density_change(
        m.rename(columns={"gc_0": "gc"})[["o", "d", "gc"]],
        m.rename(columns={"gc_1": "gc"})[["o", "d", "gc"]],
        zones,
        p["agglomeration_decay_alpha"].value,
        intrazonal,
        cut,
    )
    return out


def interpolate(years: list[int], values: list[float], t: np.ndarray) -> np.ndarray:
    """Linear between modelled years; flat after the last one (A-cba-306) and before the first."""
    return np.interp(t, np.asarray(years, float), np.asarray(values, float))
