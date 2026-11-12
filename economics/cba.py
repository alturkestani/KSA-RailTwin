"""Cost-benefit appraisal of one case against its matched baseline (W4, R5; `cba-appraisal` skill).

    uv run python -m economics.cba run --case cities/ksa/cba/<id>.yaml --seed 1 --out runs/cba/<id>/
    uv run python -m economics.cba report

Time axis: calendar years from the present-value year (A-cba-301, year 0) on. Construction starts
in the A-cba-301 start year and lasts the drawn uplifted duration (R1c); capex is spread evenly over
it (A-cba-303). Operation runs from opening for the horizon (30/40/60 years, A-cba-004); demand
quantities are interpolated between the modelled years (2025 calibration point; 2040/2050/2060 per
population scenario) and held flat after 2060 (A-cba-306), with a ramp-up in the first three years
(A-cba-110..112). Values of time grow with real GDP per head x the income elasticity
(A-cba-106/107). Every money flow is SAR million at 2025 prices.

Outputs per population scenario x horizon x discount-rate case, each as P10/P50/P90 over the
Monte Carlo draws: PVB, PVC, NPV and BCR without and with wider impacts, EIRR, FIRR, payback year,
fiscal cost to the state, and the PV of every stream.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from common.schemas import CbaCase
from economics import benefits, demandruns, discounting, montecarlo
from economics import params as prm

RATE_CASES = ("greenbook_2026", "tag_declining", "flat_5", "flat_7", "drawn")
CENTRAL_RATE = "greenbook_2026"
OUTPUTS = (
    "pvb",
    "pvc",
    "npv",
    "npv_wei",
    "bcr",
    "bcr_wei",
    "eirr",
    "firr",
    "payback_years",
    "fiscal_cost",
)
STREAMS = (
    "user_time_cost",
    "vehicle_operating_cost_nonfuel",
    "reliability",
    "safety",
    "carbon",
    "air_quality",
    "decongestion_interurban",
    "decongestion_jeddah",
    "freight_shift",
    "wei_agglomeration",
    "wei_imperfect_competition",
    "fare_revenue",
)
CLASS_OF = {
    "civil_track": "track",
    "structure": "civil",
    "terrain_premium": "civil",
    "utilities": "civil",
    "land": "civil",
    "design_pm": "civil",
    "station": "buildings",
    "depot": "buildings",
    "signalling": "systems",
    "telecom": "systems",
    "electrification_ocs": "systems",
    "power_substations": "systems",
    "rolling_stock": "rolling_stock",
}

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """CBA per case: run, report."""


def load_case(path: Path) -> CbaCase:
    return CbaCase.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


# --------------------------------------------------------------------------- case context
@dataclass
class Context:
    case: CbaCase
    p: prm.Params
    scalars: pd.DataFrame  # demand inputs per population x year
    cost: dict[str, Any]  # cost run base.yaml
    class_share: dict[str, float]
    train_km_yr: float
    electric: bool
    line_type: str


def class_shares(cost_run: Path, root: Path = REPO_ROOT) -> dict[str, float]:
    """Capex shares by asset class from the cost run's trace (P50 per component)."""
    tr = pd.read_csv(root / cost_run / "trace.csv")
    tr["base"] = tr.component.str.replace(r"\[.*\]", "", regex=True)
    tr = tr[tr.base.isin(CLASS_OF)]
    if tr.empty:
        return {"civil": 1.0}
    tr = tr.assign(cls=tr.base.map(CLASS_OF), P50=pd.to_numeric(tr.P50, errors="coerce"))
    s = tr.groupby("cls").P50.sum()
    return (s / s.sum()).to_dict()


def residual_fraction(h: int, shares: dict[str, float], lives: dict[str, int]) -> float:
    """Straight-line remaining life at the end of year h of operation (A-cba-305): renewable
    classes were renewed every L years (renewals are costed), so their age is ((h-1) mod L) + 1;
    civil works are never renewed inside the horizon."""
    f = 0.0
    for c, s in shares.items():
        life = int(lives.get(c, lives.get("civil", 100)))
        age = h if c in ("civil", "station_unrenewed") else ((h - 1) % life) + 1
        f += s * max(0.0, 1.0 - age / life)
    return f


def context(case: CbaCase, root: Path = REPO_ROOT, p: prm.Params | None = None) -> Context:
    p = p or prm.load(root)
    sc = demandruns.load_inputs(case.id, root, Path(case.demand_runs or demandruns.INPUTS))
    runs = montecarlo.split_runs(case.cost_run)
    specs = montecarlo.split_runs(case.cost_spec)
    costs = [yaml.safe_load((root / r / "base.yaml").read_text(encoding="utf-8")) for r in runs]
    sp = [yaml.safe_load((root / s).read_text(encoding="utf-8")) for s in specs]
    tkm = sum(float((c.get("operations") or {}).get("train_km_yr") or 0.0) for c in costs)
    # capex-weighted class shares over the runs
    w = [float(c["capex_base_sar_m"]["P50"]) for c in costs]
    shares: dict[str, float] = {}
    for r, wi in zip(runs, w, strict=True):
        for k, v in class_shares(r, root).items():
            shares[k] = shares.get(k, 0.0) + v * wi / sum(w)
    if case.family == "station_addition":
        shares = {"station_unrenewed": 1.0}
        tkm = 0.0  # no added train-km: through trains stop (the stop time is in the demand runs)
    return Context(
        case=case,
        p=p,
        scalars=sc,
        cost=costs[0],
        class_share=shares,
        train_km_yr=tkm,
        electric=all(bool(x.get("electrified", True)) for x in sp),
        line_type=str(sp[0].get("line_type", costs[0].get("line_type"))),
    )


# --------------------------------------------------------------------------- annual series
def annual_quantities(ctx: Context, pop: str, years: np.ndarray) -> dict[str, np.ndarray]:
    """Demand-side physical quantities per calendar year (before ramp-up and ridership ratio)."""
    cols = [c for c in ctx.scalars.columns if c not in ("case", "population", "year")]
    out = {}
    for c in cols:
        ys, vs = demandruns.series_for(ctx.scalars, pop, c)
        out[c] = benefits.interpolate(ys, vs, years)
    return out


def carbon_value(p: prm.Params, years: np.ndarray) -> np.ndarray:
    """SAR per tCO2e (2025 prices) by year: schedule if given, else 2025 value x real growth."""
    sched = p.raw.get("carbon_value_schedule")
    if isinstance(sched, dict) and sched:
        pts = sorted(
            (int(k), float(v["value"] if isinstance(v, dict) else v))
            for k, v in sched.items()
            if str(k).isdigit()
        )
        if pts:
            ys, vs = zip(*pts, strict=True)
            return np.interp(years, ys, vs)
    v0 = p["carbon_value_2025"].value
    g = p.get("carbon_value_growth_real", 0.0) or 0.0
    return v0 * (1.0 + g) ** (years - 2025)


def grid_factor(p: prm.Params, years: np.ndarray) -> np.ndarray:
    sched = p.raw.get("ksa_grid_kgco2e_per_kwh_schedule")
    if isinstance(sched, dict) and sched:
        pts = sorted(
            (int(k), float(v["value"] if isinstance(v, dict) else v))
            for k, v in sched.items()
            if str(k).isdigit()
        )
        if pts:
            ys, vs = zip(*pts, strict=True)
            return np.interp(years, ys, vs)
    return np.full(len(years), p["ksa_grid_kgco2e_per_kwh"].value)


def vot_by_purpose(p: prm.Params) -> dict[str, float]:
    return {k: p[f"vot_{k}"].value for k in benefits.PURPOSES}


def rail_energy_kwh_per_train_km(p: prm.Params, line_type: str) -> float:
    key = {
        "hsr": "ef_rail_electric_kwh_per_train_km_hsr",
        "commuter": "ef_rail_electric_kwh_per_train_km_commuter",
    }.get(line_type, "ef_rail_electric_kwh_per_train_km_conventional")
    return p[key].value


# --------------------------------------------------------------------------- evaluation
def evaluate(
    ctx: Context,
    draws: pd.DataFrame,
    pop: str,
    horizons: list[int],
    rate_cases: list[str],
    detail: bool = False,
    include_reliability: bool = False,
) -> dict[tuple[int, str], dict[str, np.ndarray]]:
    """Per-draw outputs for one population scenario: {(horizon, rate_case): {output: (D,)}}."""
    p = ctx.p
    prog = p
    y0 = int(prog["pv_year"].value)
    start = int(prog["construction_start_year"].value)
    n_c = np.maximum(1, np.rint(draws.construction_years.to_numpy())).astype(int)
    d = len(draws)
    t_len = (start - y0) + int(n_c.max()) + max(horizons) + 1
    years = y0 + np.arange(t_len)
    yy = years[None, :]
    opening = start + n_c[:, None]
    age = yy - opening  # years since opening (0 = opening year)
    operating = age >= 0
    ramp = np.ones((d, t_len))
    for k, key in enumerate(("ramp_up_year1", "ramp_up_year2", "ramp_up_year3")):
        ramp = np.where(age == k, p[key].value, ramp)
    q = annual_quantities(ctx, pop, years.astype(float))
    ratio = draws.ridership_ratio.to_numpy()[:, None]
    dem = ramp * operating * ratio  # demand-driven scaling (D, T)
    # agglomeration: GC-driven, not ridership-driven (A-cba-307); TAG A2.4 para 4.2.2 ramp
    a1 = p["agglomeration_ramp_year1"].value
    an = max(p["agglomeration_ramp_years"].value, 1.0)
    agg = np.clip(a1 + (1.0 - a1) * age / an, 0.0, 1.0) * operating
    g = p["real_gdp_per_capita_growth"].value / 100.0  # percent in the YAML (A-cba-108)
    e = p["vot_income_elasticity"].value
    vgrow = (1.0 + g) ** (e * (years - 2025))
    vm = draws.vot_mult.to_numpy()[:, None]
    vot = vot_by_purpose(p)
    sar = 1e-6  # SAR -> SAR million
    s: dict[str, np.ndarray] = {}
    ub = np.zeros(t_len)
    ub_bus = np.zeros(t_len)
    for k in benefits.PURPOSES:
        v = q[f"user_min_{k}"] / 60.0 * vot[k] * vgrow
        ub = ub + v
        if k == "business":
            ub_bus = v
    s["user_time_cost"] = ub[None, :] * dem * vm * sar
    vot_avg = vot["leisure_vfr"]
    rel = (
        0.5
        * q["car_pkm_diverted_min"]
        / 60.0
        * p["rail_reliability_sd_share"].value
        * p["reliability_ratio"].value
        * vot_avg
        * vgrow
    )
    # A-cba-109/112: no KSA journey-time variability data, so reliability is a sensitivity only
    # (include_reliability=True); the central case carries zero
    s["reliability"] = rel[None, :] * dem * vm * sar * (1.0 if include_reliability else 0.0)
    dcar = q["car_vkm_interurban"] + q["car_vkm_jeddah_urban"]
    dbus = q["bus_vkm"]
    dair = q["air_pkm"]
    tk = ctx.train_km_yr * operating  # train-km from opening (service is not demand-driven)
    crash = p["road_crash_cost_sar_per_car_vkm"].value
    crash_bus = p.get("road_crash_cost_sar_per_bus_vkm", crash) or crash
    crash_rail = p.get("rail_crash_cost_sar_per_train_km", 0.0) or 0.0
    cm = draws.crash_mult.to_numpy()[:, None]
    s["safety"] = (
        -(dcar * crash + dbus * crash_bus)[None, :] * dem * cm - tk * crash_rail * cm
    ) * sar
    cv = carbon_value(p, years.astype(float))
    if ctx.electric:
        rail_t = (
            tk
            * rail_energy_kwh_per_train_km(p, ctx.line_type)
            * grid_factor(p, years.astype(float))[None, :]
            / 1000.0
        )
    else:
        rail_t = tk * p["ef_rail_diesel_kgco2e_per_train_km"].value / 1000.0
    road_t = (
        dcar * p["ef_car_kgco2e_per_vkm"].value
        + dbus * p["ef_bus_kgco2e_per_vkm"].value
        + dair * p["ef_air_kgco2e_per_pkm_domestic"].value
    ) / 1000.0
    kmult = draws.carbon_mult.to_numpy()[:, None]
    s["carbon"] = -(road_t[None, :] * dem + rail_t) * cv[None, :] * kmult * sar
    am = draws.aq_mult.to_numpy()[:, None]
    aq_rail = 0.0 if ctx.electric else (p.get("air_quality_cost_sar_per_train_km_diesel") or 0.0)
    s["air_quality"] = (
        -(
            dcar * p["air_quality_cost_sar_per_car_vkm"].value
            + dbus * (p.get("air_quality_cost_sar_per_bus_vkm") or 0.0)
        )[None, :]
        * dem
        * am
        - tk * aq_rail * am
    ) * sar
    mm = draws.mec_mult.to_numpy()[:, None]
    mec = p["marginal_external_congestion_cost_sar_per_car_vkm_intercity"].value
    s["decongestion_interurban"] = -q["car_vkm_interurban"][None, :] * mec * dem * mm * sar
    # Jeddah urban legs: TrafficTwin only (R4 runs; A-cba-308); no candidate is representable,
    # so the stream is zero and never VKT-valued instead
    s["decongestion_jeddah"] = np.zeros((d, t_len))
    s["freight_shift"] = np.zeros((d, t_len))  # A-cba-309: no open freight OD
    gdpw = p["gdp_per_worker_sar"].value * (1.0 + g) ** (years - 2025)
    wm = draws.wei_mult.to_numpy()[:, None]
    el = p["agglomeration_elasticity"].value
    s["wei_agglomeration"] = (q["wei_job_weighted_dlnED"] * gdpw * el)[None, :] * agg * wm * sar
    s["wei_imperfect_competition"] = (
        ub_bus[None, :] * dem * vm * p["imperfect_competition_uplift"].value * sar
    )
    s["fare_revenue"] = q["revenue_sar"][None, :] * dem * sar
    # non-fuel car operating costs are not in the perceived car cost of the logsum (fuel only,
    # A-mode-023), so the resource saving on removed car-km is its own stream (A-cba-222)
    s["vehicle_operating_cost_nonfuel"] = (
        -dcar[None, :] * p["car_voc_nonfuel_sar_per_vkm"].value * dem * sar
    )
    capex = draws.capex.to_numpy()[:, None]
    build = (yy >= start) & (yy < opening)
    capex_flow = np.where(build, capex / n_c[:, None], 0.0)
    opex = draws.opex.to_numpy()[:, None]
    lives = ctx.case.residual_value.asset_lives
    core = [k for k in STREAMS if benefits.MATRIX[k]["in"] == "core"]
    wei = [k for k in STREAMS if benefits.MATRIX[k]["in"] == "wei"]
    out: dict[tuple[int, str], dict[str, np.ndarray]] = {}
    for h in horizons:
        hm = operating & (age < h)
        ren_col = f"renewals_{h}y" if f"renewals_{h}y" in draws else "renewals_60y"
        ren = draws[ren_col].to_numpy()[:, None] / h
        rvf = residual_fraction(h, ctx.class_share, lives)
        rv = np.where(age == h - 1, capex * rvf, 0.0)
        cost_flow = capex_flow + np.where(hm, opex + ren, 0.0)
        ben_core = sum(np.where(hm, s[k], 0.0) for k in core)
        ben_wei = sum(np.where(hm, s[k], 0.0) for k in wei)
        rev = np.where(hm, s["fare_revenue"], 0.0)
        econ = ben_core + rev - cost_flow + rv
        fin = rev - cost_flow
        eirr = discounting.irr_many(econ)
        firr = discounting.irr_many(fin)
        for rc in rate_cases:
            df = rate_factors(rc, t_len, draws)
            pv = (
                (lambda m, df=df: np.sum(m * df, axis=1))
                if df.ndim == 2
                else (lambda m, df=df: m @ df)
            )
            pvb = pv(ben_core)
            pvw = pv(ben_wei)
            pvc = pv(cost_flow) - pv(rv) - pv(rev)
            fiscal = pv(cost_flow) - pv(rev)
            npv = pvb - pvc
            with np.errstate(divide="ignore", invalid="ignore"):
                bcr = np.where(pvc > 0, pvb / pvc, np.inf)
                bcr_w = np.where(pvc > 0, (pvb + pvw) / pvc, np.inf)
            dfr = df if df.ndim == 2 else np.broadcast_to(df, econ.shape)
            cum = np.cumsum(econ * dfr, axis=1)
            pay = np.full(d, np.inf)
            okp = cum[:, -1] >= 0
            neg_last = np.where(cum < 0, np.arange(t_len)[None, :], -1).max(axis=1)
            first = neg_last + 1
            pay = np.where(okp, np.maximum(first - (opening[:, 0] - y0), 0), np.inf)
            res = {
                "pvb": pvb,
                "pvc": pvc,
                "npv": npv,
                "npv_wei": npv + pvw,
                "bcr": bcr,
                "bcr_wei": bcr_w,
                "eirr": eirr,
                "firr": firr,
                "payback_years": pay.astype(float),
                "fiscal_cost": fiscal,
                "pv_capex": pv(capex_flow),
                "pv_opex_renewals": pv(cost_flow - capex_flow),
                "pv_residual": pv(rv),
                "opening_year": opening[:, 0].astype(float),
            }
            if detail:
                for k in STREAMS:
                    res[f"pv_{k}"] = pv(np.where(hm, s[k], 0.0))
            out[(h, rc)] = res
    return out


def rate_factors(rc: str, t_len: int, draws: pd.DataFrame) -> np.ndarray:
    """Discount factors (T,) for a named schedule or a constant 'const:<r>'; (D, T) for `drawn`
    (the central schedule shifted by each draw's rate_shift, A-cba-304)."""
    if rc.startswith("const:"):
        return discounting.factors(discounting.constant(float(rc.split(":", 1)[1])), t_len)
    if rc == "drawn":
        base = np.array([discounting.rate_by_year(discounting.SCHEDULES[CENTRAL_RATE], t_len - 1)])
        r = base + draws.rate_shift.to_numpy()[:, None]
        df = np.ones((len(draws), t_len))
        df[:, 1:] = np.cumprod(1.0 / (1.0 + r), axis=1)
        return df
    return discounting.factors(discounting.SCHEDULES[rc], t_len)


def pct(x: np.ndarray, qs: tuple[int, ...] = (10, 50, 90)) -> dict[str, float | None]:
    """Percentiles; NaN (no IRR in the bracket) counts as the lowest value; inf stays inf."""
    a = np.asarray(x, dtype=float)
    a = np.where(np.isnan(a), -np.inf, a)
    out: dict[str, float | None] = {}
    for qq in qs:
        v = float(np.percentile(a, qq, method="nearest"))
        out[f"P{qq}"] = v if math.isfinite(v) else (None if v < 0 else float("inf"))
    return out


# --------------------------------------------------------------------------- run
def central_row(draws: pd.DataFrame) -> pd.DataFrame:
    """One deterministic row: cost and duration at their draw medians, multipliers at 1."""
    row = {c: float(np.median(draws[c])) for c in draws.columns if c != "draw"}
    for c in ("vot_mult", "carbon_mult", "crash_mult", "aq_mult", "mec_mult", "wei_mult"):
        row[c] = 1.0
    row["rate_shift"] = 0.0
    row["draw"] = -1
    return pd.DataFrame([row])


def n_planned(case: CbaCase, root: Path = REPO_ROOT) -> int:
    """Number of new stations of a station-addition case (0 for every other family)."""
    if case.family != "station_addition" or not case.candidate:
        return 0
    c = yaml.safe_load((root / case.candidate).read_text(encoding="utf-8"))
    return sum(1 for s in c["stations"] if s.get("class") == "planned")


def run_case(case_path: Path, seed: int, out: Path, root: Path = REPO_ROOT) -> dict[str, Any]:
    from economics import switching

    case = load_case(root / case_path if not Path(case_path).is_absolute() else case_path)
    p = prm.load(root)
    ctx = context(case, root, p)
    n = int(case.monte_carlo.draws)
    draws = montecarlo.draw_inputs(
        str(case.cost_run),
        str(case.cost_spec),
        case.cost_costing,
        p,
        seed,
        n,
        root,
        (p["rate_shift"].low, p["rate_shift"].high),
        station_addition=n_planned(case, root),
    )
    pops = case.population_scenarios or list(demandruns.POPULATIONS)
    rates = case.rate_cases or list(RATE_CASES)
    hz = list(case.horizon_years)
    results: list[dict[str, Any]] = []
    keep: dict[str, np.ndarray] = {}
    for pop in pops:
        ev = evaluate(ctx, draws, pop, hz, rates, detail=True)
        for (h, rc), r in ev.items():
            row = {"population": pop, "horizon": h, "rate_case": rc}
            for k, v in r.items():
                row[k] = pct(v)
            results.append(row)
            if h == max(hz):
                for k in ("npv", "npv_wei", "bcr", "bcr_wei", "pvb", "pvc"):
                    keep[f"{k}|{pop}|{rc}"] = r[k]
                if rc == CENTRAL_RATE:
                    keep[f"eirr|{pop}"] = r["eirr"]
                    keep[f"firr|{pop}"] = r["firr"]
                    keep[f"pv_user_time_cost|{pop}"] = r["pv_user_time_cost"]
    out.mkdir(parents=True, exist_ok=True)
    dr = pd.concat([draws, pd.DataFrame(keep)], axis=1)
    dr.to_parquet(out / "draws.parquet", index=False)
    central = central_row(draws)
    tor = switching.tornado(ctx, draws, central)
    tor.to_csv(out / "tornado.csv", index=False)
    switching.tornado_png(tor, out / "tornado.png", case.id)
    sv = switching.switching_values(ctx, central)
    (out / "switching_values.json").write_text(json.dumps(sv, indent=1) + "\n", encoding="utf-8")
    res = {
        "label": LABEL,
        "case": case.id,
        "family": case.family,
        "scenario": case.scenario,
        "baseline": case.baseline,
        "candidate": case.candidate,
        "cost_run": case.cost_run,
        "demand_runs": case.demand_runs,
        "units": "SAR million, 2025 prices, PV at the A-cba-301 year; rates and IRRs as shares",
        "draws": n,
        "seed": seed,
        "central_rate_case": CENTRAL_RATE,
        "results": results,
    }
    (out / "results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    write_meta(
        out,
        seed,
        {"case": case.model_dump(), "params_files": list(prm.FILES)},
        extra={
            "label": LABEL,
            "assumptions": sorted({i for q in p.numeric.values() for i in q.ids}),
        },
    )
    return res


@app.command("run")
def run_cmd(
    case: Path = typer.Option(..., "--case"),
    seed: int = seed_option(),
    out: Path = typer.Option(..., "--out"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Appraise one case: results.json, draws.parquet, tornado.csv/.png, switching_values.json."""
    r = run_case(case, seed, out, root)
    c = (
        next(
            x
            for x in r["results"]
            if x["population"] == "un_wpp_medium"
            and x["horizon"] == 60
            and x["rate_case"] == CENTRAL_RATE
        )
        if any(x["population"] == "un_wpp_medium" for x in r["results"])
        else r["results"][0]
    )
    typer.echo(f"{r['case']}: BCR {c['bcr']} NPV {c['npv']} ({LABEL})")


@app.command("report")
def report_cmd(
    summary: Path = typer.Option(Path("runs/cba/summary.parquet"), "--summary"),
    doc: Path = typer.Option(Path("docs/cba.md"), "--doc"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Render the generated results section of docs/cba.md from summary.parquet."""
    from economics import report

    report.write_all(root / summary, root / doc, root)
    typer.echo(f"wrote the results section of {doc}")


if __name__ == "__main__":
    app()
