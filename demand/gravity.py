"""Doubly-constrained gravity by purpose with MNL mode split (W8, R3 task 3; skill
gravity-calibration).

For each purpose p (business, leisure_vfr, tourism doubly constrained; commute origin-constrained,
A-demand-058, because its 40-120 km band makes the doubly-constrained problem infeasible):
  O_i = rate_p x population_i (demand_generation.yaml trip_rates), D_j = attraction_p,j scaled to
  sum O; T_ij = A_i B_j O_i D_j f_p(c_ij) on admissible pairs (road km >= 40, A-demand-005;
  commute only in the 40-120 km band, A-demand-055), Furness-balanced to 1e-4.
  c_ij = composite generalised minutes from the MNL logsum (A-demand-056); f_p exponential or power
  (A-demand-021..025).
Pilgrimage: fixed external totals by origin region (Umrah, Madinah visits, Hajj; 2025), split to
zones by population, to the zones holding Masjid al-Haram / Al-Masjid an-Nabawi; out and back.
Mode split: modechoice.mnl.shares on demand.supply level of service (car, rail, air, bus).

uv run python -m demand.gravity run --scenario S0 --population baseline --seed 1 \
    --out runs/demand/S0-baseline-s1/
writes od_<purpose>.parquet (o, d, trips and trips_<mode>), totals.json, freight.json, meta.json.

Freight: no open freight OD found (freight.json says what exists).
Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from demand import population as popmod
from demand import supply
from modechoice.coefficients import Coefficients, apply_overrides, base_coefficients, load_r3
from modechoice.mnl import MODES, Settings, shares

GRAVITY = Path("cities/ksa/assumptions/demand_gravity.yaml")
ZONES = Path("runs/zones/zones.parquet")
SKIMS = Path("runs/skims/r3-zones")
NODES = Path("cities/ksa/zones/economic_nodes.parquet")
ZONES_GEOJSON = Path("cities/ksa/zones/zones.geojson")
MODE_LABEL = "coefficients literature-based until survey results exist"
DISTRIBUTED = ("commute", "business", "leisure_vfr", "tourism")
OD_COLS = [
    "o",
    "d",
    "road_km",
    "road_min",
    "rail_line",
    "rail_station_o",
    "rail_station_d",
    "rail_km",
    "air_o",
    "air_d",
    "air_gc_km",
]
R4_COLS = ["rail_path", "rail_boardings"]

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Gravity demand by purpose."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


@dataclass
class RunConfig:
    scenario: str = "S0"
    population: str = "baseline"
    year: int = 2022
    overrides: dict[str, float] = field(default_factory=dict)  # coefficient overrides (asc.*)
    rate_scale: dict[str, float] = field(default_factory=dict)  # trip-rate multipliers per purpose
    root: Path = REPO_ROOT
    unbounded: bool = False  # calibration diagnostic only
    giga: str | None = None  # giga-project add-on quantile (p10 | p50 | p90 | announced) or None
    # R4 (additive): network "r3" (R3 supply) or "r4" (rail graph, sourced air pairs, bus nodes)
    network: str = "r3"
    candidate: str | None = None  # R4: one S2-S5 corridor YAML on top of the S1 line set
    bus_variant: str = "named_and_capitals"  # R4 bus availability (demand.r4.BUS_VARIANTS)


# --------------------------------------------------------------------------- zones and inputs
def zone_population(
    year: int, population: str, root: Path = REPO_ROOT, giga: str | None = None
) -> pd.DataFrame:
    """Zone table with the scenario population for `year`: governorate totals from
    demand.population.project (plus the giga-project add-on at quantile `giga`, A-demand-030,
    in the inputs.yaml add-on mode, A-pop-013), split to metro hexes by their fixed grid shares."""
    z = pd.read_parquet(root / ZONES)
    if population == "baseline":
        gov = popmod.base_by_zone()
    else:
        gov = popmod.project(popmod.base_by_zone(), popmod.load_scenario(population), year)
    if giga:
        inp = popmod.inputs()
        inc = popmod.giga_increments(
            popmod.load_scenario("gigaprojects"), year, giga, popmod.base_by_zone(), inp=inp
        )
        gov = popmod.apply_giga(gov, inc, str(inp["gigaprojects"]["addon_mode"]["value"]))
    parts = []
    for gid, g in z.groupby("parent_gov", sort=True):
        w = pd.Series(g.share_in_gov.to_numpy(), index=g.zone_id.to_numpy())
        parts.append(popmod.largest_remainder(w, int(gov[gid])))
    pop = pd.concat(parts).reindex(z.zone_id)
    z = z.copy()
    z["population"] = pop.to_numpy().astype("int64")
    # jobs per resident held at the proxy's zone rate (A-demand-003)
    rate = z.jobs_proxy / z.population_2022.where(z.population_2022 > 0)
    z["jobs"] = (rate.fillna(0.0) * z.population).round(3)
    return z.sort_values("zone_id").reset_index(drop=True)


def od_frame(zones: pd.DataFrame, root: Path = REPO_ROOT) -> pd.DataFrame:
    """Every zone pair o != d with road km/min and the zone indices."""
    road = pd.read_parquet(root / SKIMS / "road.parquet")
    road = road.rename(columns={"km": "road_km", "min": "road_min"})
    idx = {z: i for i, z in enumerate(zones.zone_id)}
    road = road[road.o.isin(idx) & road.d.isin(idx) & (road.o != road.d)].copy()
    road["oi"] = road.o.map(idx).astype(int)
    road["di"] = road.d.map(idx).astype(int)
    return road.sort_values(["oi", "di"]).reset_index(drop=True)


def furness(
    o: np.ndarray, d: np.ndarray, f: np.ndarray, tol: float, max_iter: int
) -> tuple[np.ndarray, int, float]:
    """Doubly-constrained balancing of f to row totals o and column totals d (sum o == sum d)."""
    b = np.ones(len(d))
    err = np.inf
    t = f
    for it in range(1, max_iter + 1):
        fb = f @ b
        a = np.divide(o, fb, out=np.zeros_like(o), where=fb > 0)
        fa = f.T @ a
        b = np.divide(d, fa, out=np.zeros_like(d), where=fa > 0)
        t = a[:, None] * f * b[None, :]
        rs, cs = t.sum(1), t.sum(0)
        er = np.abs(rs - o)[o > 0] / o[o > 0]
        ec = np.abs(cs - d)[d > 0] / d[d > 0]
        err = float(max(er.max(initial=0.0), ec.max(initial=0.0)))
        if err < tol:
            return t, it, err
    return t, max_iter, err


def log_impedance(c: np.ndarray, purpose: str, gen: dict[str, Any]) -> np.ndarray:
    """ln f(c): exponential -beta c or power -gamma ln c (A-demand-021..025)."""
    ip = gen["impedance_priors"]
    form = ip["functional_form"]["value"][purpose]
    if form == "exponential":
        return -float(ip[purpose]["beta_per_min"]["value"]) * c
    if form == "power":
        return -float(ip[purpose]["gamma"]["value"]) * np.log(np.maximum(c, 1.0))
    raise ValueError(f"unknown impedance form {form!r}")


def impedance_matrix(n: int, oi: np.ndarray, di: np.ndarray, logf: np.ndarray) -> np.ndarray:
    """Dense f with zeros off the admissible pairs, each row scaled by exp(-max ln f) so the
    exponential form cannot underflow (a doubly-constrained solution is row-scale invariant)."""
    lf = np.full((n, n), -np.inf)
    lf[oi, di] = logf
    rmax = lf.max(axis=1, keepdims=True)
    rmax = np.where(np.isfinite(rmax), rmax, 0.0)
    return np.exp(lf - rmax)


def attraction(zones: pd.DataFrame, purpose: str, grav: dict[str, Any]) -> np.ndarray:
    if purpose in ("commute", "business"):
        return zones.jobs.to_numpy(dtype=float)
    if purpose == "leisure_vfr":
        return zones.population.to_numpy(dtype=float)
    if purpose == "tourism":
        w = float(_v(grav["attraction"]["tourism"]["w"]))
        n = zones[["n_tourism", "n_heritage", "n_hajj_umrah", "n_giga_project"]].sum(axis=1)
        return zones.population.to_numpy(dtype=float) * (1.0 + w * n.to_numpy(dtype=float))
    raise ValueError(purpose)


# --------------------------------------------------------------------------- pilgrimage
def destination_zone(node: str, root: Path = REPO_ROOT) -> tuple[str, str]:
    """(zone_id, parent_gov) of the zone polygon containing an economic node."""
    import geopandas as gpd

    nodes = pd.read_parquet(root / NODES).set_index("node_id")
    zg = gpd.read_file(root / ZONES_GEOJSON)[["zone_id", "parent_gov", "geometry"]]
    pt = gpd.points_from_xy([nodes.at[node, "lon"]], [nodes.at[node, "lat"]])
    j = gpd.sjoin(gpd.GeoDataFrame(geometry=pt, crs=4326), zg, predicate="within")
    return str(j.zone_id.iloc[0]), str(j.parent_gov.iloc[0])


def pilgrimage_od(
    zones: pd.DataFrame,
    gen: dict[str, Any],
    grav: dict[str, Any],
    pop_ratio: float,
    root: Path = REPO_ROOT,
) -> pd.DataFrame:
    """Fixed OD: origin-region totals x zone population share, to the destination node's zone,
    out and back (A-demand-006, -016..019, -057). Origins in the destination governorate dropped."""
    pg = gen["pilgrimage"]
    pcfg = grav["pilgrimage"]
    reg_pop = zones.groupby("region").population.sum()
    nat = float(zones.population.sum())
    tpp = float(_v(pcfg["trips_per_person"]))
    overlap = float(_v(pcfg["overlap_factor_madinah"]))
    hajj_total = float(pg["hajj_internal"]["y2025"]["value"])
    segments = {
        "umrah": (
            pg["umrah_internal_2025"]["by_origin_region"],
            pcfg["destinations"]["umrah"],
            1.0,
        ),
        "madinah_visit": (
            pg["madinah_visits_internal_2025"]["by_origin_region"],
            pcfg["destinations"]["madinah_visit"],
            overlap,
        ),
        "hajj": (
            {r: hajj_total * float(p) / nat for r, p in reg_pop.items()},
            pcfg["destinations"]["hajj"],
            1.0,
        ),
    }
    rows = []
    for seg, (by_region, node, factor) in segments.items():
        dz, dgov = destination_zone(node, root)
        for r in zones.itertuples(index=False):
            if r.parent_gov == dgov or r.population <= 0:
                continue
            persons = (
                float(by_region[r.region])
                * factor
                * pop_ratio
                * r.population
                / float(reg_pop[r.region])
            )
            half = persons * tpp / 2.0
            rows.append({"o": r.zone_id, "d": dz, "segment": seg, "trips": half})
            rows.append({"o": dz, "d": r.zone_id, "segment": seg, "trips": half})
    df = pd.DataFrame(rows)
    return df.groupby(["o", "d"], as_index=False, sort=True).trips.sum()


# --------------------------------------------------------------------------- model run
def coefficients(overrides: dict[str, float], unbounded: bool = False) -> Coefficients:
    """Base coefficients with overrides inside their registered ranges (apply_overrides refuses
    anything else). `unbounded` is for the calibration diagnostic only (never an adopted run):
    ASC overrides are set without the range check."""
    c = base_coefficients()
    if not overrides:
        return c
    if not unbounded:
        return apply_overrides(c, overrides)
    asc = dict(c.asc)
    for k, x in overrides.items():
        if not k.startswith("asc."):
            raise KeyError(f"unbounded overrides are limited to ASCs, not {k}")
        asc[k.split(".", 1)[1]] = float(x)
    return dataclasses.replace(c, asc=asc)


def los_for(cfg: RunConfig, od: pd.DataFrame) -> pd.DataFrame:
    """Level of service for an OD table: R3 supply, or the R4 network (demand.r4)."""
    if cfg.network == "r4":
        from demand import r4

        cand = Path(cfg.candidate) if cfg.candidate else None
        return r4.attributes(od, cfg.scenario, cfg.root, cand, cfg.bus_variant)
    return supply.attributes(od, SKIMS, cfg.scenario, cfg.root)


def mode_split(
    od: pd.DataFrame, purpose: str, coefs: Coefficients, settings: Settings
) -> pd.DataFrame:
    x = od.copy()
    x["purpose"] = purpose
    return shares(x, coefs, settings)


def _with_modes(
    ms: pd.DataFrame, keep: np.ndarray, trips: np.ndarray, c: np.ndarray
) -> pd.DataFrame:
    res = ms.loc[keep, [c for c in OD_COLS + R4_COLS if c in ms.columns]].copy()
    res["trips"] = trips
    res["cost_min"] = c
    for m in MODES:
        res[f"trips_{m}"] = res.trips * ms.loc[keep, f"share_{m}"].to_numpy()
    return res.reset_index(drop=True)


def run_model(cfg: RunConfig, los: pd.DataFrame | None = None) -> dict[str, Any]:
    """Run every purpose; return {'zones', 'od': {purpose: DataFrame}, 'diagnostics', 'los'}."""
    root = cfg.root
    grav = load_yaml(root / GRAVITY)
    gen = load_yaml(root / grav["generation_file"])
    zones = zone_population(cfg.year, cfg.population, root, cfg.giga)
    n = len(zones)
    if los is None:
        los = los_for(cfg, od_frame(zones, root))
    coefs = coefficients(cfg.overrides, cfg.unbounded)
    settings = Settings.from_r3()
    b_ivt_car = abs(float(coefs.ivt["car"]))
    tol = float(_v(grav["furness"]["tolerance"]))
    max_iter = int(_v(grav["furness"]["max_iter"]))
    min_km = float(_v(grav["admissible_pairs"]["min_road_km"]))
    lo_c, hi_c = _v(grav["admissible_pairs"]["commute_band_road_km"])
    out: dict[str, pd.DataFrame] = {}
    diag: dict[str, Any] = {}
    adm = (los.road_km >= min_km).to_numpy()
    pop = zones.population.to_numpy(dtype=float)
    oi, di = los.oi.to_numpy(), los.di.to_numpy()
    for p in DISTRIBUTED:
        ms = mode_split(los, p, coefs, settings)
        c = np.maximum(-ms.logsum.to_numpy() / b_ivt_car, 1.0)
        ok = adm & np.isfinite(c)
        if p == "commute":
            ok &= ((los.road_km >= lo_c) & (los.road_km <= hi_c)).to_numpy()
        f = impedance_matrix(n, oi[ok], di[ok], log_impedance(c[ok], p, gen))
        rate = float(gen["trip_rates"][p]["value"]) * float(cfg.rate_scale.get(p, 1.0))
        o = rate * pop
        feasible = f.sum(1) > 0
        lost = float(o[~feasible].sum())
        o = np.where(feasible, o, 0.0)
        d = attraction(zones, p, grav) * (f.sum(0) > 0)
        d = d * (o.sum() / d.sum()) if d.sum() > 0 else d
        constraint = str(_v(grav["constraint"][p]))
        if constraint == "doubly":
            t, iters, err = furness(o, d, f, tol, max_iter)
        else:  # origin-constrained (A-demand-058): commute band makes Furness infeasible
            w = f * d[None, :]
            ws = w.sum(1, keepdims=True)
            t = np.divide(w, ws, out=np.zeros_like(w), where=ws > 0) * o[:, None]
            iters, err = 0, float(np.max(np.abs(t.sum(1) - o)[o > 0] / o[o > 0], initial=0.0))
        # production-attraction -> origin-destination: half of each home-based trip end returns
        # (A-demand-060); totals unchanged, directional counts (stations, airports) symmetric
        t = 0.5 * (t + t.T)
        tv = t[oi, di]
        keep = tv > 0
        out[p] = _with_modes(ms, keep, tv[keep], c[keep])
        diag[p] = {
            "furness_iterations": iters,
            "furness_max_rel_error": err,
            "furness_tolerance": tol,
            "constraint": constraint,
            "generated": float(rate * pop.sum()),
            "lost_no_admissible_destination": lost,
            "rate": rate,
        }
    # pilgrimage: 2025 totals x population / 2025 calibration population (A-demand-057)
    calib = grav["calibration"]
    ref = popmod.national_total(
        popmod.load_scenario(_v(calib["population_scenario"])), int(_v(calib["year"]))
    )
    pop_ratio = float(zones.population.sum()) / float(ref)
    pod = pilgrimage_od(zones, gen, grav, pop_ratio, root)
    road = pd.read_parquet(root / SKIMS / "road.parquet")
    road = road.rename(columns={"km": "road_km", "min": "road_min"})
    pod = pod.merge(road[["o", "d", "road_km", "road_min"]], on=["o", "d"], how="left")
    pl = los_for(cfg, pod[["o", "d", "road_km", "road_min"]])
    ms = mode_split(pl, "pilgrimage", coefs, settings)
    c = np.maximum(-ms.logsum.to_numpy() / b_ivt_car, 1.0)
    out["pilgrimage"] = _with_modes(ms, np.ones(len(ms), bool), pod.trips.to_numpy(), c)
    diag["pilgrimage"] = {
        "population_ratio_to_2025_calibration": pop_ratio,
        "trips": float(pod.trips.sum()),
    }
    return {"zones": zones, "od": out, "diagnostics": diag, "los": los}


def _round(d: Any) -> dict[str, float]:
    return {str(k): round(float(v), 1) for k, v in dict(d).items()}


def totals(result: dict[str, Any]) -> dict[str, Any]:
    od = result["od"]
    allp = pd.concat([d.assign(purpose=p) for p, d in od.items()], ignore_index=True)
    t: dict[str, Any] = {"label": LABEL, "mode_choice_label": MODE_LABEL}
    t["by_purpose"] = _round({p: d.trips.sum() for p, d in od.items()})
    t["by_mode"] = _round({m: allp[f"trips_{m}"].sum() for m in MODES})
    t["by_purpose_mode"] = {
        p: _round({m: d[f"trips_{m}"].sum() for m in MODES}) for p, d in od.items()
    }
    rail = allp[allp.trips_rail > 0]
    if "rail_path" in rail.columns:
        t["rail_by_line"] = path_line_totals(rail)
        t["rail_by_main_line"] = _round(rail.groupby("rail_line").trips_rail.sum())
        t["rail_transfer_share"] = round(
            float((rail.trips_rail * (rail.rail_boardings > 1)).sum() / rail.trips_rail.sum()), 4
        )
    t["rail_by_line_r3_rule" if "rail_path" in rail.columns else "rail_by_line"] = {
        str(line): {
            "passengers": round(float(g.trips_rail.sum()), 1),
            "passenger_km_m": round(float((g.trips_rail * g.rail_km).sum()) / 1e6, 3),
            "mean_trip_km": round(float((g.trips_rail * g.rail_km).sum() / g.trips_rail.sum()), 2),
        }
        for line, g in rail.groupby("rail_line")
    }
    t["rail_station_departures"] = _round(rail.groupby("rail_station_o").trips_rail.sum())
    t["rail_station_arrivals"] = _round(rail.groupby("rail_station_d").trips_rail.sum())
    air = allp[allp.trips_air > 0]
    t["air_airport_departures"] = _round(air.groupby("air_o").trips_air.sum())
    t["air_airport_arrivals"] = _round(air.groupby("air_d").trips_air.sum())
    t["population"] = int(result["zones"].population.sum())
    t["diagnostics"] = result["diagnostics"]
    return t


def path_line_totals(rail: pd.DataFrame) -> dict[str, dict[str, float]]:
    """R4: per-line journeys (a trip boarding a line counts once on it) and passenger-km from
    rail_path ("line:km|line:km")."""
    acc: dict[str, list[float]] = {}
    for trips, path in zip(rail.trips_rail.to_numpy(), rail.rail_path.to_numpy(), strict=True):
        if not isinstance(path, str):
            continue
        for leg in path.split("|"):
            ln, km = leg.rsplit(":", 1)
            a = acc.setdefault(ln, [0.0, 0.0])
            a[0] += float(trips)
            a[1] += float(trips) * float(km)
    return {
        ln: {
            "passengers": round(p, 1),
            "passenger_km_m": round(pk / 1e6, 3),
            "mean_trip_km": round(pk / p, 2) if p else 0.0,
        }
        for ln, (p, pk) in sorted(acc.items())
    }


FREIGHT_NOTE = {
    "label": LABEL,
    "freight_od": "no open freight OD found",
    "searched": [
        "GASTAT Railway Transport Statistics 2025 (manifest gastat-rail-stats-2025-en): rail "
        "freight totals by line, no origin-destination table",
        "Mawani / Transport General Authority public pages: port throughput totals, no inland OD",
        "no open road freight survey or truck OD for Saudi Arabia was found (docs/data-sources.md)",
    ],
    "consequence": "freight stays out of the R3 OD matrices; R4/R5 treat freight by line totals "
    "with registered assumptions",
}


def write_run(result: dict[str, Any], cfg: RunConfig, out: Path, seed: int) -> dict[str, Any]:
    run = cfg.root / out
    run.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for p, d in result["od"].items():
        dd = d.copy()
        num = dd.select_dtypes("number").columns
        dd[num] = dd[num].round(6)
        path = run / f"od_{p}.parquet"
        dd.to_parquet(path, index=False)
        hashes[p] = hashlib.sha256(path.read_bytes()).hexdigest()
    tot = totals(result)
    tot["od_sha256"] = hashes
    (run / "totals.json").write_text(json.dumps(tot, indent=1, default=float) + "\n")
    (run / "freight.json").write_text(json.dumps(FREIGHT_NOTE, indent=1) + "\n")
    config = {
        "scenario": cfg.scenario,
        "population": cfg.population,
        "year": cfg.year,
        "overrides": cfg.overrides,
        "rate_scale": cfg.rate_scale,
        "giga": cfg.giga,
        "network": cfg.network,
        "candidate": cfg.candidate,
        "bus_variant": cfg.bus_variant,
        "gravity": load_yaml(cfg.root / GRAVITY),
        "supply": supply.load_supply(cfg.root),
        "mode_choice_r3": load_r3(),
    }
    write_meta(
        run,
        seed,
        config,
        extra={
            "label": LABEL,
            "mode_choice_label": MODE_LABEL,
            "run": {
                "scenario": cfg.scenario,
                "population": cfg.population,
                "year": cfg.year,
                "overrides": cfg.overrides,
                "rate_scale": cfg.rate_scale,
                "giga": cfg.giga,
            },
            "inputs": {"zones": str(ZONES), "skims": str(SKIMS)},
            "od_sha256": hashes,
            "assumptions": ["A-demand-005", "A-demand-021", "A-demand-055", "A-demand-056"],
        },
    )
    return tot


def rate_scales(which: str, root: Path = REPO_ROOT) -> dict[str, float]:
    """Trip-rate multipliers at the range ends of demand_generation.yaml (low | base | high)."""
    if which == "base":
        return {}
    gen = load_yaml(root / load_yaml(root / GRAVITY)["generation_file"])
    out = {}
    for p in DISTRIBUTED:
        r = gen["trip_rates"][p]
        lo, hi = sorted(float(x) for x in r["range"])
        out[p] = (lo if which == "low" else hi) / float(r["value"])
    return out


def calibrated_overrides(path: Path | None) -> dict[str, float]:
    """The fitted ASCs from a demand.calibrate run (calibration.json `adjustments`)."""
    if path is None:
        return {}
    cal = json.loads(Path(path).read_text(encoding="utf-8"))
    return {a["parameter"]: float(a["fitted"]) for a in cal["adjustments"]}


@app.command("run")
def run_cmd(
    scenario: str = typer.Option("S0", help="S0 | S1 (rail line set, demand_supply.yaml)"),
    population: str = typer.Option(
        "baseline", help="scenario id (cities/ksa/population/scenarios)"
    ),
    year: int = typer.Option(2022),
    overrides: str = typer.Option("", help='JSON coefficient overrides, e.g. {"asc.rail": -0.5}'),
    calibration: Path | None = typer.Option(None, help="calibration.json: use its fitted ASCs"),
    rates: str = typer.Option("base", help="trip rates: base | low | high (range ends)"),
    giga: str | None = typer.Option(None, help="giga add-on quantile: p10 | p50 | p90 | announced"),
    network: str = typer.Option(
        "r3", help="r3 (R3 supply) | r4 (rail graph, air pairs, bus nodes)"
    ),
    candidate: str | None = typer.Option(None, help="R4: S2-S5 corridor YAML added to S1"),
    bus_variant: str = typer.Option("named_and_capitals", help="R4 bus rule"),
    out: Path = typer.Option(Path("runs/demand/S0-baseline-s1")),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Gravity by purpose + mode split; writes OD Parquet per purpose, totals.json, meta.json."""
    ov = calibrated_overrides(calibration)
    ov.update(json.loads(overrides) if overrides else {})
    cfg = RunConfig(
        scenario,
        population,
        year,
        ov,
        rate_scales(rates, root),
        root,
        False,
        giga,
        network,
        candidate,
        bus_variant,
    )
    tot = write_run(run_model(cfg), cfg, out, seed)
    keys = ("by_purpose", "by_mode", "rail_by_line", "population")
    typer.echo(json.dumps({k: tot[k] for k in keys}, indent=1))


if __name__ == "__main__":
    app()
