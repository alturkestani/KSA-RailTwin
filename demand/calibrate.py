"""Calibration of the national demand model against observed totals (W8, R3 task 5).

Runs demand.gravity at the calibration point (2025, population scenario and line set from
demand_gravity.yaml `calibration`), compares modelled with observed totals from
demand_calibration.yaml, and fits ONLY the registered calibration parameters (asc.rail, asc.air,
asc.bus; mode_choice_r3.yaml calibration_hook) inside their stated ranges (A-mode-010..012) by
least squares on log(modelled / observed) over the fit targets. Every adjustment is logged.

Pass rule (A-demand-036): a target passes when |modelled / observed - 1| <= its tolerance
(A-demand-032..035); GEH on daily flows is reported, never used as the pass test. The status flips
to `calibrated` per total, never globally; targets with grade C/D or `usable: false` are listed as
"available but unverified" and never fitted.

Scope decision (A-demand-059): the HHR line total includes international visitors (foreign Umrah
performers arriving by air), whom this resident-demand model does not generate; the rail constant
is fitted to SAR East + SAR North passengers and HHR is reported, not fitted.

uv run python -m demand.calibrate run --seed 1 --out runs/demand/calibration-s1/

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast (except the totals the
table marks `calibrated`, at the 2025 calibration point only).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml
from scipy.optimize import least_squares

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta
from demand import gravity, supply
from modechoice.coefficients import load_priors

TARGETS = Path("cities/ksa/assumptions/demand_calibration.yaml")
LINE_OF = {"hhr": "hhr", "sar_east": "sar-east-passenger", "sar_north": "sar-north-passenger"}
STATION_OF = {
    "rail-hhr-stn-makkah-2025": "hhr:makkah",
    "rail-hhr-stn-al-sulimaniyah-jeddah-2025": "hhr:jeddah",
    "rail-hhr-stn-airport-jeddah-2025": "hhr:kaia",
    "rail-hhr-stn-kaec-2025": "hhr:kaec",
    "rail-hhr-stn-madinah-2025": "hhr:madinah",
    "rail-sar_east-stn-riyadh-2025": "sar-east-passenger:riyadh",
    "rail-sar_east-stn-hufuf-2025": "sar-east-passenger:hufuf",
    "rail-sar_east-stn-abqaiq-2025": "sar-east-passenger:abqaiq",
    "rail-sar_east-stn-dammam-2025": "sar-east-passenger:dammam",
    "rail-sar_north-stn-riyadh-north-2025": "sar-north-passenger:riyadh-north",
    "rail-sar_north-stn-majmaah-2025": "sar-north-passenger:majmaah",
    "rail-sar_north-stn-qassim-2025": "sar-north-passenger:al-qassim",
    "rail-sar_north-stn-hail-2025": "sar-north-passenger:hail",
    "rail-sar_north-stn-jouf-2025": "sar-north-passenger:al-jawf",
    "rail-sar_north-stn-qurayyat-2025": "sar-north-passenger:al-qurayyat",
}
DERIVED_RAIL_FIT = "rail-sar-east-north-pax-2025"  # SAR East + SAR North, A-demand-059
PARAMS = ("asc.rail", "asc.air", "asc.bus")

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Calibration of the demand model."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def load_targets(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / TARGETS).read_text(encoding="utf-8"))


def geh(m: float, c: float) -> float:
    """GEH on average daily flows (annual / 365), descriptive only (demand_calibration.yaml)."""
    md, cd = m / 365.0, c / 365.0
    return math.sqrt(2 * (md - cd) ** 2 / (md + cd)) if md + cd > 0 else 0.0


def modelled(tot: dict[str, Any], bus_q_share: float) -> dict[str, float]:
    """Modelled value per target id (and the derived rail fit target)."""
    rl = tot["rail_by_line"]
    m: dict[str, float] = {}

    def line(k: str, f: str) -> float:
        return float(rl.get(LINE_OF[k], {}).get(f, 0.0))

    m["rail-intercity-pax-2025"] = sum(line(k, "passengers") for k in LINE_OF)
    m["rail-intercity-pkm-2025"] = sum(line(k, "passenger_km_m") for k in LINE_OF)
    for k in LINE_OF:
        m[f"rail-{k}-pax-2025"] = line(k, "passengers")
        m[f"rail-{k}-pkm-2025"] = line(k, "passenger_km_m")
        m[f"rail-{k}-triplen-2025"] = line(k, "mean_trip_km")
    m[DERIVED_RAIL_FIT] = line("sar_east", "passengers") + line("sar_north", "passengers")
    dep, arr = tot["rail_station_departures"], tot["rail_station_arrivals"]
    for tid, uid in STATION_OF.items():
        m[f"{tid}:departures"] = float(dep.get(uid, 0.0))
        m[f"{tid}:arrivals"] = float(arr.get(uid, 0.0))
    m["air-domestic-departures-2025"] = float(tot["by_mode"]["air"])
    m["_air_dep"] = tot["air_airport_departures"]  # type: ignore[assignment]
    m["_air_arr"] = tot["air_airport_arrivals"]  # type: ignore[assignment]
    bus = float(tot["by_mode"]["bus"])
    m["bus-intercity-pax-2025q2q4"] = bus * bus_q_share
    for q in ("q2", "q3", "q4"):
        m[f"bus-intercity-pax-2025{q}"] = bus / 4.0
    return m


def target_rows(cal: dict[str, Any], m: dict[str, float], airports: pd.DataFrame) -> pd.DataFrame:
    """One row per comparable observed value (station/airport targets give two rows)."""
    tol = cal["tolerances"]
    iata_of = dict(zip(airports.node_id, airports.iata, strict=True))
    rows = []
    for t in cal["targets"]:
        if t.get("year") != 2025:
            continue
        usable = bool(t.get("usable")) and t.get("evidence_grade") in ("A", "B")
        rel = (t.get("tolerance") or {}).get("rel")
        base = {
            "id": t["id"],
            "mode": t["mode"],
            "measure": t["measure"],
            "scope": t["scope"],
            "grade": t.get("evidence_grade"),
            "source_id": t.get("source_id"),
            "usable": usable,
            "tolerance": rel,
            "tolerance_id": (t.get("tolerance") or {}).get("assumption"),
        }
        if isinstance(t["value"], dict):
            if t["mode"] == "rail":
                pairs = [(f"{t['id']}:{k}", k, v) for k, v in t["value"].items()]
            else:
                node = t["scope"].split("economic node ")[-1].rstrip(")")
                iata = iata_of.get(node)
                pairs = [(f"{t['id']}:{k}", k, v) for k, v in t["value"].items()]
                for key, k, _ in pairs:
                    src = m["_air_dep"] if k == "departures" else m["_air_arr"]
                    m[key] = float(src.get(iata, 0.0)) if iata else float("nan")
            for key, _k, v in pairs:
                exempt = float(v) < float(
                    tol["A_station"]["low_flow_exempt_below_departures_per_year"]
                )
                rows.append(
                    {
                        **base,
                        "id": key,
                        "observed": float(v),
                        "modelled": m.get(key, np.nan),
                        "low_flow_exempt": exempt,
                    }
                )
        elif isinstance(t["value"], (int, float)):
            rows.append(
                {
                    **base,
                    "observed": float(t["value"]),
                    "modelled": m.get(t["id"], np.nan),
                    "low_flow_exempt": False,
                }
            )
    df = pd.DataFrame(rows)
    df["ratio"] = df.modelled / df.observed
    df["deviation_pct"] = (df.ratio - 1.0) * 100.0
    df["geh_daily"] = [
        geh(a, b) if np.isfinite(a) and t not in ("mean_trip_length_km", "passenger_km") else np.nan
        for a, b, t in zip(df.modelled, df.observed, df.measure, strict=True)
    ]
    within = (df.deviation_pct.abs() / 100.0) <= df.tolerance.fillna(-1)
    df["pass"] = np.where(df.usable & df.tolerance.notna() & ~df.low_flow_exempt, within, None)
    df["status"] = np.select(
        [~df.usable, df.modelled.isna(), df.low_flow_exempt, df["pass"].eq(True)],
        [
            "available but unverified (not fitted)",
            "reported (no comparable model output)",
            "reported (low-flow exempt)",
            "within tolerance (validation, not fitted)",
        ],
        default="outside tolerance",
    )
    return df


def run_calibration(
    root: Path, seed: int, network: str = "r3", bus_variant: str = "named_and_capitals"
) -> dict[str, Any]:
    """R3 calibration; R4 (additive): `network="r4"` runs it on the R4 rail graph, air pairs and bus
    nodes (demand.r4)."""
    grav = gravity.load_yaml(root / gravity.GRAVITY)
    cc = grav["calibration"]
    cal = load_targets(root)
    year = int(_v(cc["year"]))
    pop = str(_v(cc["population_scenario"]))
    bus_q = float(_v(cc["bus_quarter_share"]))
    cfg = gravity.RunConfig("S0", pop, year, {}, {}, root, network=network, bus_variant=bus_variant)
    zones = gravity.zone_population(year, pop, root)
    los = gravity.los_for(cfg, gravity.od_frame(zones, root))
    priors = load_priors()
    lo = np.array([priors[p].low for p in PARAMS])
    hi = np.array([priors[p].high for p in PARAMS])
    x0 = np.array([priors[p].value for p in PARAMS])
    obs = {
        t["id"]: float(t["value"]) for t in cal["targets"] if isinstance(t["value"], (int, float))
    }
    obs[DERIVED_RAIL_FIT] = obs["rail-sar_east-pax-2025"] + obs["rail-sar_north-pax-2025"]
    fit = [DERIVED_RAIL_FIT, "air-domestic-departures-2025", "bus-intercity-pax-2025q2q4"]
    log: list[dict[str, Any]] = []

    def evaluate(x: np.ndarray, unbounded: bool = False) -> tuple[dict[str, Any], dict[str, float]]:
        ov = dict(zip(PARAMS, map(float, x), strict=True))
        c = gravity.RunConfig(
            "S0", pop, year, ov, {}, root, unbounded, network=network, bus_variant=bus_variant
        )
        res = gravity.run_model(c, los=los)
        tot = gravity.totals(res)
        return res, modelled(tot, bus_q)

    def resid(x: np.ndarray) -> np.ndarray:
        _, m = evaluate(x)
        r = np.array([math.log(m[k] / obs[k]) for k in fit])
        log.append(
            {
                "eval": len(log) + 1,
                **dict(zip(PARAMS, map(float, x), strict=True)),
                **{f"log_ratio:{k}": float(v) for k, v in zip(fit, r, strict=True)},
                "sse": float((r**2).sum()),
            }
        )
        return r

    _, m0 = evaluate(x0)
    sol = least_squares(resid, x0, bounds=(lo, hi), x_scale=1.0, diff_step=1e-3, max_nfev=60)
    xs = sol.x
    res, m1 = evaluate(xs)
    airports = supply.airports(root)
    table0 = target_rows(cal, dict(m0), airports)
    table = target_rows(cal, dict(m1), airports)
    der = {
        "id": DERIVED_RAIL_FIT,
        "mode": "rail",
        "measure": "passengers",
        "scope": "SAR East + SAR North (derived from two grade A targets; A-demand-059)",
        "grade": "A",
        "source_id": "S-r3-cal-001",
        "usable": True,
        "tolerance": 0.15,
        "tolerance_id": "A-demand-032",
        "observed": obs[DERIVED_RAIL_FIT],
        "modelled": m1[DERIVED_RAIL_FIT],
        "low_flow_exempt": False,
    }
    der["ratio"] = der["modelled"] / der["observed"]
    der["deviation_pct"] = (der["ratio"] - 1) * 100
    der["geh_daily"] = geh(der["modelled"], der["observed"])
    der["pass"] = abs(der["ratio"] - 1) <= 0.15
    der["status"] = "outside tolerance" if not der["pass"] else "within tolerance"
    table = pd.concat([pd.DataFrame([der]), table], ignore_index=True)
    table["fitted"] = table.id.isin(fit)
    table["deviation_before_pct"] = table.id.map(
        dict(zip(table0.id, table0.deviation_pct, strict=True))
        | {DERIVED_RAIL_FIT: (m0[DERIVED_RAIL_FIT] / obs[DERIVED_RAIL_FIT] - 1) * 100}
    )
    # status per total (never global): only a FITTED target inside its tolerance is calibrated
    table.loc[table.fitted, "status"] = np.where(
        table.loc[table.fitted, "pass"].eq(True), "calibrated", "uncalibrated"
    )
    hhr_note = (
        table.id.str.startswith("rail-hhr")
        | table.id.eq("rail-intercity-pax-2025")
        | table.id.eq("rail-intercity-pkm-2025")
    )
    table.loc[hhr_note & table.status.eq("outside tolerance"), "status"] = (
        "outside tolerance (scope: includes international visitors, A-demand-059)"
    )
    # diagnostic only (not adopted): the constants the fit targets would need without the ranges
    wide = (np.full(3, -6.0), np.full(3, 6.0))
    sol_u = least_squares(
        lambda x: np.array([math.log(evaluate(x, True)[1][k] / obs[k]) for k in fit]),
        xs,
        bounds=wide,
        diff_step=1e-3,
        max_nfev=40,
    )
    _, mu = evaluate(sol_u.x, True)
    unbounded = {
        "note": "diagnostic only, NOT adopted: the registered ranges (A-mode-010..012) bind",
        "x": dict(zip(PARAMS, map(float, sol_u.x), strict=True)),
        "deviation_pct": {k: (mu[k] / obs[k] - 1) * 100 for k in fit},
        "nfev": int(sol_u.nfev),
    }
    adjustments = [
        {
            "parameter": p,
            "prior": float(a),
            "fitted": float(b),
            "range": [float(l_), float(h_)],
            "at_bound": bool(np.isclose(b, l_) or np.isclose(b, h_)),
            "assumption": priors[p].assumption,
        }
        for p, a, b, l_, h_ in zip(PARAMS, x0, xs, lo, hi, strict=True)
    ]
    return {
        "result": res,
        "table": table,
        "adjustments": adjustments,
        "unbounded_diagnostic": unbounded,
        "log": log,
        "optimizer": {
            "status": int(sol.status),
            "message": str(sol.message),
            "nfev": int(sol.nfev),
            "cost": float(sol.cost),
        },
        "config": {
            "year": year,
            "population": pop,
            "scenario": "S0",
            "fit_targets": fit,
            "bus_quarter_share": bus_q,
            "network": network,
            "bus_variant": bus_variant,
        },
        "run_config": cfg,
    }


@app.command("run")
def run_cmd(
    out: Path = typer.Option(Path("runs/demand/calibration-s1")),
    seed: int = seed_option(),
    network: str = typer.Option("r3", help="r3 | r4 (rail graph, air pairs, bus nodes)"),
    bus_variant: str = typer.Option("named_and_capitals", help="R4 bus rule"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Fit the ASCs inside their ranges, write the calibration table and the calibrated run."""
    r = run_calibration(root, seed, network, bus_variant)
    run = root / out
    run.mkdir(parents=True, exist_ok=True)
    tab = r["table"]
    tab.to_csv(run / "targets_table.csv", index=False)
    pd.DataFrame(r["log"]).to_csv(run / "adjustments_log.csv", index=False)
    cfg = r["run_config"]
    cfg.overrides = {a["parameter"]: a["fitted"] for a in r["adjustments"]}
    od_dir = out / "od"
    tot = gravity.write_run(r["result"], cfg, od_dir, seed)
    summary = {
        "label": LABEL,
        "config": r["config"],
        "adjustments": r["adjustments"],
        "optimizer": r["optimizer"],
        "unbounded_diagnostic": r["unbounded_diagnostic"],
        "status_counts": tab.status.value_counts().to_dict(),
        "calibrated_totals": tab.loc[tab.status == "calibrated", "id"].tolist(),
        "fit_targets": tab.loc[
            tab.fitted, ["id", "observed", "modelled", "deviation_pct", "status"]
        ]
        .round(3)
        .to_dict("records"),
        "by_mode": tot["by_mode"],
        "by_purpose": tot["by_purpose"],
    }
    (run / "calibration.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    write_meta(
        run,
        seed,
        {"targets": load_targets(root), "gravity": gravity.load_yaml(root / gravity.GRAVITY)},
        extra={
            "summary": summary,
            "assumptions": [
                "A-demand-032",
                "A-demand-033",
                "A-demand-034",
                "A-demand-035",
                "A-demand-036",
                "A-demand-053",
                "A-demand-059",
                "A-mode-010",
                "A-mode-011",
                "A-mode-012",
            ],
        },
    )
    typer.echo(
        json.dumps(
            {
                k: summary[k]
                for k in ("adjustments", "unbounded_diagnostic", "fit_targets", "status_counts")
            },
            indent=1,
            default=str,
        )
    )


if __name__ == "__main__":
    app()
