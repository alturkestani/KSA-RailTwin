"""STUDY_EXTRA_TRAVEL (Tariq, 7 Nov 2026; prompts/STUDY_EXTRA_TRAVEL.md): extra domestic trips and
visitor / land-entry effects. A research sensitivity beside the main programme, like STUDY_RJ: not
a new official ranking, not a GDP study, not R10.

Engine: the frozen judge v1-r5 (tag r5; the code behind the published S1-vs-S0 CBA
runs/cba/CBA-S1-committed-programme), run through the study entry `study/extra_travel_judge.py`.
Nothing under judge/, runs/cba/, runs/r6/ or runs/r7/ is written; every output is under
runs/study/extra-travel/.

  uv run python -m study.extra_travel baseline --seed 1
  uv run python -m study.extra_travel induced --seed 1
  uv run python -m study.extra_travel land --seed 1
  uv run python -m study.extra_travel summary

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Not the official
ranking.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta
from study import extra_travel_core as core

LABEL = core.LABEL
NOT_OFFICIAL = core.NOT_OFFICIAL
JUDGE = "v1-r5"
OUT = Path("runs/study/extra-travel")
CONFIG = Path("cities/ksa/assumptions/extra_travel_study.yaml")
PUBLISHED = Path("runs/cba/CBA-S1-committed-programme")
PUBLISHED_INPUTS = Path("runs/cba/inputs")
CASE = "CBA-S1-committed-programme"
POPS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
CENTRAL_RATE = "greenbook_2026"
HORIZON = 60
ZERO = "zero"

app = typer.Typer(add_completion=False, help="STUDY_EXTRA_TRAVEL (study path only).")


def cfg(root: Path = REPO_ROOT) -> dict[str, Any]:
    return yaml.safe_load((root / CONFIG).read_text(encoding="utf-8"))


def elasticity_cases(root: Path = REPO_ROOT) -> dict[str, float]:
    """The zero case (must reproduce the published inputs) plus the configured cases."""
    return {ZERO: 0.0, **{k: float(v) for k, v in cfg(root)["induced"]["elasticity_cases"].items()}}


def judge_python(root: Path = REPO_ROOT) -> str:
    return str(root / ".venv/bin/python")


def judge_env(root: Path = REPO_ROOT) -> dict[str, str]:
    from optimise import judge as jd

    env = dict(os.environ, R6_JUDGE_ROOT=str(jd.judge_root(JUDGE, root)))
    for k in ("PYTHONPATH", "STUDY_RJ_MARKER"):
        env.pop(k, None)
    return env


def _entry(args: list[str], root: Path, log: Path) -> str:
    from optimise import judge as jd

    jd.check_fingerprint(JUDGE, root)
    r = subprocess.run(
        [judge_python(root), str(root / "study/extra_travel_judge.py"), *args],
        cwd=jd.judge_root(JUDGE, root),
        env=judge_env(root),
        capture_output=True,
        text=True,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(r.stdout + "\n" + r.stderr[-20000:], encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr[-2000:])
    jd.check_fingerprint(JUDGE, root)
    return r.stdout


def _meta(out: Path, seed: int, config: Any, root: Path, **extra: Any) -> None:
    from optimise import judge as jd

    rec = jd.load_record(JUDGE, root)
    write_meta(
        out,
        seed,
        config,
        extra={
            "label": LABEL,
            "study": "STUDY_EXTRA_TRAVEL",
            "official_ranking": False,
            "not_official": NOT_OFFICIAL,
            "judge": JUDGE,
            "judge_sha256": rec["sha256"],
            "judge_commit": rec.get("commit"),
            "judge_fingerprint_checked": True,
            "entry": "study/extra_travel_judge.py",
            **extra,
        },
    )


# --------------------------------------------------------------------------- commands
@app.command("baseline")
def baseline_cmd(seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)):
    """Item 2: the Riyadh-Jeddah pair under S1 and S0 (2050 medium) from the frozen model."""
    out = root / OUT / "baseline"
    typer.echo(_entry(["baseline", "--out", str(out.resolve())], root, out / "judge.log"))
    _meta(out, seed, cfg(root)["rj_pair"], root)


@app.command("induced")
def induced_cmd(seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)):
    """Item 3: induced-demand CBA inputs for every elasticity case, then the frozen CBA on each."""
    out = root / OUT / "induced"
    cases = elasticity_cases(root)
    arg = ",".join(f"{k}={v}" for k, v in cases.items())
    typer.echo(
        _entry(
            ["induced", "--out", str(out.resolve()), "--cases", arg], root, out / "judge-inputs.log"
        )
    )
    for name in cases:
        d = out / name
        typer.echo(
            _entry(
                ["cba", "--out", str(d.resolve()), "--seed", str(seed)], root, d / "judge-cba.log"
            )
        )
        _meta(
            d,
            seed,
            {"induced": cfg(root)["induced"], "case": name, "elasticity": cases[name]},
            root,
            elasticity=cases[name],
            baseline="S0",
            scenario="S1",
        )
    chk = reproduction_check(root)
    (out / "reproduction_check.json").write_text(json.dumps(chk, indent=1) + "\n")
    if not chk["inputs_identical"] or not chk["results_identical"]:
        raise RuntimeError(f"zero case does not reproduce the published S1 vs S0: {chk}")


@app.command("land")
def land_cmd(seed: int = seed_option(), root: Path = typer.Option(REPO_ROOT, hidden=True)):
    """Item 4: land-entry ports, rail paths and the labelled visitor scenarios."""
    out = root / OUT / "land"
    typer.echo(_entry(["land", "--out", str(out.resolve())], root, out / "judge.log"))
    sc = land_scenarios(root)
    (out / "land_scenarios.json").write_text(json.dumps(sc, indent=1) + "\n", encoding="utf-8")
    pd.DataFrame(sc["rows"]).to_csv(out / "land_scenarios.csv", index=False)
    _meta(out, seed, cfg(root)["land_ports"], root)


@app.command("summary")
def summary_cmd(root: Path = typer.Option(REPO_ROOT, hidden=True)):
    """Sensitivity tables (both labels + not the official ranking) from the stored study runs."""
    s = induced_summary(root)
    out = root / OUT
    (out / "induced_summary.json").write_text(json.dumps(s, indent=1) + "\n", encoding="utf-8")
    pd.DataFrame(s["rows"]).to_csv(out / "induced_summary.csv", index=False)
    typer.echo(json.dumps({r["case"]: r["npv_p50_medium"] for r in s["rows"]}))


# --------------------------------------------------------------------------- checks
def reproduction_check(root: Path = REPO_ROOT) -> dict[str, Any]:
    """The zero case's CBA inputs and results must equal the published S1-vs-S0 ones."""
    zd = root / OUT / "induced" / ZERO
    worst = 0.0
    for g in sorted((root / PUBLISHED_INPUTS).glob("*/scalars.parquet")):
        pub = pd.read_parquet(g)
        pub = pub[pub.case == CASE].reset_index(drop=True)
        st = pd.read_parquet(zd / "inputs" / g.parent.name / "scalars.parquet")
        num = [c for c in pub.columns if c not in ("case", "population", "year")]
        a, b = pub[num].to_numpy(float), st[num].to_numpy(float)
        rel = np.abs(a - b) / np.maximum(np.abs(a), 1.0)
        worst = max(worst, float(rel.max()))
    pr = json.loads((root / PUBLISHED / "results.json").read_text())["results"]
    zr = json.loads((zd / "cba" / "results.json").read_text())["results"]
    same = json.dumps(pr, sort_keys=True) == json.dumps(zr, sort_keys=True)
    return {
        "inputs_identical": worst == 0.0,
        "inputs_max_relative_difference": worst,
        "results_identical": same,
        "published": str(PUBLISHED),
    }


# --------------------------------------------------------------------------- summaries
def _row(results: list[dict], pop: str, h: int = HORIZON, rc: str = CENTRAL_RATE) -> dict:
    return next(
        r for r in results if r["population"] == pop and r["horizon"] == h and r["rate_case"] == rc
    )


def _pct(x: np.ndarray) -> dict[str, float]:
    return {f"P{q}": float(np.percentile(x, q)) for q in (10, 50, 90)}


def induced_summary(root: Path = REPO_ROOT) -> dict[str, Any]:
    base = root / OUT / "induced"
    cases = elasticity_cases(root)
    z_draws = pd.read_parquet(base / ZERO / "cba" / "draws.parquet")
    z_sc = pd.read_parquet(base / ZERO / "inputs" / "un_wpp_medium-2050" / "scalars.parquet")
    rows = []
    for name, eps in cases.items():
        res = json.loads((base / name / "cba" / "results.json").read_text())["results"]
        med = _row(res, "un_wpp_medium")
        dr = pd.read_parquet(base / name / "cba" / "draws.parquet")
        sc = pd.read_parquet(base / name / "inputs" / "un_wpp_medium-2050" / "scalars.parquet")
        diag_doc = json.loads((base / name / "induced_diag.json").read_text())
        diag = diag_doc["groups"]
        g = diag["un_wpp_medium-2050"]
        extra = {
            "trips": {m: 0.0 for m in (*core.MODES, "total")},
            "pkm": {m: 0.0 for m in (*core.MODES, "total")},
        }
        for pu, d in g.items():
            if pu.startswith("_"):
                continue
            for k in ("trips", "pkm"):
                for m in extra[k]:
                    extra[k][m] += d[k][m]
        s1_rail = g["_scenario_all_purposes"]["trips"]["rail"]
        s1_vs_s0_rail = s1_rail - g["_baseline_all_purposes"]["trips"]["rail"]
        key = f"|un_wpp_medium|{CENTRAL_RATE}"
        d_npv = dr[f"npv{key}"].to_numpy() - z_draws[f"npv{key}"].to_numpy()
        d_pvb = dr[f"pvb{key}"].to_numpy() - z_draws[f"pvb{key}"].to_numpy()
        d_ut = (
            dr["pv_user_time_cost|un_wpp_medium"].to_numpy()
            - z_draws["pv_user_time_cost|un_wpp_medium"].to_numpy()
        )
        rows.append(
            {
                "case": name,
                "elasticity": eps,
                "allocation": diag_doc.get("allocation", "proportional"),
                "purposes": ",".join(cfg(root)["induced"]["purposes"]),
                "extra_trips_2050_medium": extra["trips"]["total"],
                "extra_trips_rail_2050_medium": extra["trips"]["rail"],
                "extra_trips_air_2050_medium": extra["trips"]["air"],
                "extra_trips_car_2050_medium": extra["trips"]["car"],
                "extra_trips_bus_2050_medium": extra["trips"]["bus"],
                "extra_pkm_m_2050_medium": extra["pkm"]["total"] / 1e6,
                "extra_pkm_rail_m_2050_medium": extra["pkm"]["rail"] / 1e6,
                "extra_pkm_air_m_2050_medium": extra["pkm"]["air"] / 1e6,
                "extra_pkm_car_m_2050_medium": extra["pkm"]["car"] / 1e6,
                "national_trips_s1_2050_medium": g["_scenario_all_purposes"]["trips"]["total"],
                "s1_rail_trips_2050_medium": s1_rail,
                "s1_vs_s0_rail_trips_2050_medium": s1_vs_s0_rail,
                "generated_share_of_s1_added_rail_trips": (
                    extra["trips"]["rail"] / (s1_vs_s0_rail + extra["trips"]["rail"])
                    if s1_vs_s0_rail + extra["trips"]["rail"] > 0
                    else 0.0
                ),
                "extra_fare_revenue_sar_m_2050_medium": float(
                    sc.revenue_sar.iloc[0] - z_sc.revenue_sar.iloc[0]
                )
                / 1e6,
                "extra_user_benefit_hours_m_2050_medium": float(
                    sum(
                        sc[c].iloc[0] - z_sc[c].iloc[0]
                        for c in sc.columns
                        if c.startswith("user_min_")
                    )
                )
                / 60e6,
                **{f"npv_{q.lower()}_medium": med["npv"][q] for q in ("P10", "P50", "P90")},
                **{f"bcr_{q.lower()}_medium": med["bcr"][q] for q in ("P10", "P50", "P90")},
                **{
                    f"pv_user_time_{q.lower()}_medium": med["pv_user_time_cost"][q]
                    for q in ("P10", "P50", "P90")
                },
                **{
                    f"pv_fare_{q.lower()}_medium": med["pv_fare_revenue"][q]
                    for q in ("P10", "P50", "P90")
                },
                **{f"npv_p50_{p}": _row(res, p)["npv"]["P50"] for p in POPS},
                **{f"extra_npv_{k.lower()}_medium": v for k, v in _pct(d_npv).items()},
                **{f"extra_pvb_{k.lower()}_medium": v for k, v in _pct(d_pvb).items()},
                **{f"extra_pv_user_time_{k.lower()}_medium": v for k, v in _pct(d_ut).items()},
                "extra_pv_fare_p50_difference_of_medians": med["pv_fare_revenue"]["P50"]
                - _row(
                    json.loads((base / ZERO / "cba" / "results.json").read_text())["results"],
                    "un_wpp_medium",
                )["pv_fare_revenue"]["P50"],
                "label": LABEL,
                "official_ranking": False,
                "not_official": NOT_OFFICIAL,
            }
        )
    return {
        "label": LABEL,
        "not_official": NOT_OFFICIAL,
        "official_ranking": False,
        "units": "SAR million, 2025 prices, PV 2026; 60 years; Green Book 2026 rate (A-cba-001); "
        "trips one-way per year",
        "comparison": "S1 vs S0 (published R5 CBA, judge v1-r5); zero case = published",
        "rows": rows,
    }


def land_scenarios(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Labelled land-entry scenarios on the stored land inputs (study path; Hajj held fixed)."""
    c = cfg(root)["land_ports"]
    d = json.loads((root / OUT / "land" / "land_inputs.json").read_text())
    tot_land = sum(d["persons_by_zone"].values())
    zone_share = {z: v / tot_land for z, v in d["persons_by_zone"].items()}
    zone_group = {z: g for g, spec in c["groups"].items() for z in spec["ports"].values()}
    hz = d["holy_zones"]["makkah"]
    rows = []
    for net in ("S0", "S1"):
        path = {r["o"]: r["avail_rail"] for r in d["rail_paths"][net] if r["d"] == hz}
        rkm = {r["o"]: (r["rail_km"] or 0.0) for r in d["rail_paths"][net] if r["d"] == hz}
        for ls_name, ls in c["land_share_variants"].items():
            for rs_name, rs in c["rail_share_variants"].items():
                for xv in c["extra_land_volume"]:
                    r = core.land_scenario(d["umrah_2025_total"], ls, zone_share, path, rs, xv)
                    fare = {
                        k: sum(
                            r["rail_trips_by_group"][z] * rkm.get(z, 0.0) * v
                            for z in r["rail_trips_by_group"]
                        )
                        / 1e6
                        for k, v in c["fare_per_km_if_counted"].items()
                    }
                    by_g: dict[str, float] = {}
                    for z, v in r["rail_trips_by_group"].items():
                        by_g[zone_group[z]] = by_g.get(zone_group[z], 0.0) + v
                    rows.append(
                        {
                            "network": net,
                            "land_share": ls_name,
                            "land_share_value": ls,
                            "rail_share": rs_name,
                            "rail_share_value": rs,
                            "extra_land_volume": xv,
                            "land_entrants": r["entrants"],
                            "extra_entrants": r["extra_entrants"],
                            "rail_trips_entry_exit": r["rail_trips"],
                            **{f"fare_if_counted_sar_m_{k}": v for k, v in fare.items()},
                            **{f"rail_trips_{g}": v for g, v in sorted(by_g.items())},
                            "hajj_land_held_fixed": d["hajj_2025_by_mode"]["land"],
                            "label": LABEL,
                            "official_ranking": False,
                            "not_official": NOT_OFFICIAL,
                        }
                    )
    return {
        "label": LABEL,
        "not_official": NOT_OFFICIAL,
        "official_ranking": False,
        "year": "2025 arrivals (frozen intl segment year); no growth applied",
        "hajj_held_fixed": d["hajj_2025_by_mode"],
        "zone_share": zone_share,
        "rows": rows,
    }


if __name__ == "__main__":
    app()
