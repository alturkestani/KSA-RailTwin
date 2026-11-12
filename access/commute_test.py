# ruff: noqa: E501
"""The 30-minute test (R4 task 3; skill isochrone-commute).

For every metro of the CP1 list and every register town 40-120 km BY ROAD from it (A-screen-005;
road km from the OSRM table in cities/ksa/zones/commute_minutes_r4.parquet), per scenario (S0, S1,
each S2-S5 candidate):
- in-vehicle minutes from the town's stations (within the local catchment, A-r4-acc-006) to the
  metro's boarding stations (`access.isochrones.origin_stations`), best pair, with the running-time
  band (timetable factor low/high, A-r4-rt-011); `yes` when the central value is <= 30 min;
- door-to-door minutes (road access + terminal, wait, rides and transfers, egress; summer factor);
- car AM-peak minutes (free-flow skim x A-access-012);
- the modelled car-trip change for the town <-> metro commute pair: 1 - car share (scenario) /
  car share (S0), from the calibrated R4 multinomial logit (commute purpose, same zones, seed and
  coefficients: a matched baseline), band = running-time band. "In the model, car trips fell by
  X-Y %" -- never a forecast.

  uv run python -m access.commute_test run --seed 1
writes runs/access/commute-test-s1/{commute_test.parquet, by_metro.csv, meta.json}.
Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer

from access import isochrones as iso
from access import railgraph
from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

MINUTES = Path("cities/ksa/zones/commute_minutes_r4.parquet")
CALIBRATION = Path("runs/r4/demand/calibration-r4-s1/calibration.json")
CASES = ("value", "low", "high")
COLUMNS = [
    "scenario",
    "family",
    "candidate",
    "metro",
    "tier",
    "row_key",
    "town",
    "town_ar",
    "region",
    "population",
    "road_km",
    "car_peak_min",
    "town_station",
    "ivt_min",
    "ivt_min_low",
    "ivt_min_high",
    "d2d_min",
    "d2d_min_low",
    "d2d_min_high",
    "within_30_ivt",
    "within_90_d2d",
    "within_120_d2d",
    "car_trip_change_pct",
    "car_trip_change_pct_lo",
    "car_trip_change_pct_hi",
]

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """The 30-minute test."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def towns(root: Path = REPO_ROOT) -> pd.DataFrame:
    """Town x metro pairs 40-120 road km (A-screen-005) with the town's zone."""
    import geopandas as gpd

    t = pd.read_parquet(root / MINUTES)
    t = t[(t.road_km >= 40) & (t.road_km <= 120)].copy()
    reg = pd.read_parquet(root / "cities/ksa/candidates.parquet")[
        ["row_key", "name_en", "name_ar", "region", "population", "lat", "lon"]
    ]
    t = t.merge(reg, on="row_key")
    zg = gpd.read_file(root / iso.ZONES_GEOJSON)[["zone_id", "geometry"]]
    pts = gpd.GeoDataFrame(
        t[["row_key"]].drop_duplicates(),
        geometry=gpd.points_from_xy(
            t.drop_duplicates("row_key").lon, t.drop_duplicates("row_key").lat
        ),
        crs=4326,
    )
    j = gpd.sjoin(pts, zg, predicate="within")[["row_key", "zone_id"]]
    return t.merge(j, on="row_key", how="left").rename(columns={"zone_id": "town_zone"})


def rail_times(ctx: iso.Context, tz: str, az: str, local: float) -> tuple[float, float, str | None]:
    """(in-vehicle min, door-to-door min, town station) from the town zone's stations (local
    catchment) to the metro's boarding stations (`isochrones.origin_stations`), best pair."""
    mb = iso.origin_stations(ctx, az, local)
    st = ctx.zst[(ctx.zst.zone_id == tz) & (ctx.zst.to_min <= local)]
    if mb.empty or st.empty:
        return np.nan, np.nan, None
    uid_ix = {u: k for k, u in enumerate(ctx.g_min.nodes.uid)}
    best_ivt, best_d2d, best_st = np.inf, np.inf, None
    for r in st.itertuples(index=False):
        a = uid_ix[r.uid]
        for m in mb.itertuples(index=False):
            b = uid_ix[m.uid]
            if a == b:
                continue
            ivt = float(ctx.g_ivt.gen[a, b])
            d2d = (
                (float(r.to_min) + ctx.term) * ctx.summer
                + float(ctx.g_min.gen[a, b])
                + (float(m.from_min) + ctx.term) * ctx.summer
            )
            # in-vehicle and door-to-door are minimised separately (they may use different pairs)
            if np.isfinite(ivt) and ivt < best_ivt:
                best_ivt, best_st = ivt, r.uid
            if np.isfinite(d2d):
                best_d2d = min(best_d2d, d2d)
    if not np.isfinite(best_ivt):
        return np.nan, np.nan, None
    return best_ivt, (best_d2d if np.isfinite(best_d2d) else np.nan), best_st


def car_shares(
    pairs: pd.DataFrame, scenario: str, candidate: Path | None, case: str, root: Path
) -> pd.Series:
    """Commute car share per (o, d) on the R4 network with the calibrated constants."""
    from demand import r4
    from demand.gravity import calibrated_overrides, coefficients
    from modechoice.mnl import Settings, shares

    road = pd.read_parquet(root / "runs/skims/r3-zones/road.parquet").rename(
        columns={"km": "road_km", "min": "road_min"}
    )
    od = pairs.merge(road[["o", "d", "road_km", "road_min"]], on=["o", "d"], how="left")
    los = r4.attributes(od, scenario, root, candidate, factor_case=case)
    los["purpose"] = "commute"
    coefs = coefficients(calibrated_overrides(root / CALIBRATION))
    sh = shares(los, coefs, Settings.from_r3())
    return pd.Series(sh.share_car.to_numpy(), index=pd.MultiIndex.from_frame(od[["o", "d"]]))


def run_test(root: Path = REPO_ROOT) -> pd.DataFrame:
    tw = towns(root)
    ms = {m["name"]: m for m in iso.metros(root)}
    azs = {n: iso.anchor_zone(m, root) for n, m in ms.items()}
    tw["metro_zone"] = tw.metro.map(azs)
    tw = tw[tw.town_zone.notna() & (tw.town_zone != tw.metro_zone)].reset_index(drop=True)
    local = float(_v(railgraph.load_cfg(root)["station_catchment_road_min"]))
    peak = float(_v(railgraph.load_cfg(root)["car_peak_factor"]))
    pairs = (
        pd.concat(
            [
                tw[["town_zone", "metro_zone"]].rename(
                    columns={"town_zone": "o", "metro_zone": "d"}
                ),
                tw[["town_zone", "metro_zone"]].rename(
                    columns={"town_zone": "d", "metro_zone": "o"}
                ),
            ]
        )
        .drop_duplicates()
        .reset_index(drop=True)
    )
    zones = iso.zones_table(root)
    road = pd.read_parquet(root / "runs/skims/r3-zones/road.parquet")
    base_share = car_shares(pairs, "S0", None, "value", root)
    rows = []
    scen = [("S0", None, "S0"), ("S1", None, "S1")] + [
        (f, c, f) for f, c in iso.candidate_list(root)
    ]
    for scenario, cand, fam in scen:
        ctxs = {
            c: iso.context(scenario, cand, root, factor_case=c, zones=zones, road=road)
            for c in CASES
        }
        shares = {c: car_shares(pairs, scenario, cand, c, root) for c in CASES}
        sid = ctxs["value"].sid
        for r in tw.itertuples(index=False):
            t = {c: rail_times(ctxs[c], r.town_zone, r.metro_zone, local) for c in CASES}
            out_in = [(r.town_zone, r.metro_zone), (r.metro_zone, r.town_zone)]
            base = np.mean([base_share[k] for k in out_in])
            red = {c: 1.0 - np.mean([shares[c][k] for k in out_in]) / base for c in CASES}
            rows.append(
                {
                    "scenario": sid,
                    "family": fam,
                    "candidate": str(cand) if cand else None,
                    "metro": r.metro,
                    "tier": r.tier,
                    "row_key": r.row_key,
                    "town": r.name_en,
                    "town_ar": r.name_ar,
                    "region": r.region,
                    "population": r.population,
                    "road_km": r.road_km,
                    "car_peak_min": r.road_min * peak,
                    "town_station": t["value"][2],
                    "ivt_min": t["value"][0],
                    "ivt_min_low": t["low"][0],
                    "ivt_min_high": t["high"][0],
                    "d2d_min": t["value"][1],
                    "d2d_min_low": t["low"][1],
                    "d2d_min_high": t["high"][1],
                    "within_30_ivt": bool(t["value"][0] <= 30.0)
                    if np.isfinite(t["value"][0])
                    else False,
                    # door-to-door 90/120-minute bands (R5, CP5 decision H9a)
                    "within_90_d2d": bool(np.isfinite(t["value"][1]) and t["value"][1] <= 90.0),
                    "within_120_d2d": bool(np.isfinite(t["value"][1]) and t["value"][1] <= 120.0),
                    "car_trip_change_pct": -100 * red["value"],
                    "car_trip_change_pct_lo": -100 * max(red["low"], red["high"], red["value"]),
                    "car_trip_change_pct_hi": -100 * min(red["low"], red["high"], red["value"]),
                }
            )
    return pd.DataFrame(rows, columns=COLUMNS)


@app.command("run")
def run_cmd(
    seed: int = seed_option(),
    out: Path = typer.Option(Path("runs/access/commute-test-s1")),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """The 30-minute test for every metro, town and scenario."""
    df = run_test(root)
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    df.to_parquet(run / "commute_test.parquet", index=False)
    by = (
        df.groupby(["scenario", "metro"])
        .agg(
            towns=("row_key", "nunique"),
            towns_within_30=("within_30_ivt", "sum"),
            towns_within_90_d2d=("within_90_d2d", "sum"),
            towns_within_120_d2d=("within_120_d2d", "sum"),
        )
        .reset_index()
    )
    by.to_csv(run / "by_metro.csv", index=False)
    write_meta(
        run,
        seed,
        {"minutes": str(MINUTES), "calibration": str(CALIBRATION)},
        extra={
            "label": LABEL,
            "towns": int(df.row_key.nunique()),
            "pairs": int(df[["metro", "row_key"]].drop_duplicates().shape[0]),
        },
    )
    s = by[by.scenario.isin(["S0", "S1"])]
    typer.echo(json.dumps(s.to_dict("records"), indent=0, default=float))


if __name__ == "__main__":
    app()
