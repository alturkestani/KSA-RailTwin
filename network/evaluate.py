# ruff: noqa: E501
"""R4 network evaluation: corridor costs, the per-candidate summary and the HHR validation table.

`costs`: for every S2-S5 candidate, a LineSpec costing input (runs/network-eval/costing/<id>.yaml:
the corridor's stations, line type and length, a hypothetical all-stop service, the running-time
class kinematics) and a `costing:` sidecar with the corridor's own terrain and structure shares
(the 'unknown' terrain share falls back to the R1c default flat desert, A-cost-010, flagged), then
`costs.estimate` (R1c register ids, reference-class uplifts) into runs/costs/<id>/. A station
addition is costed as its one new station only (the station item of the same run).
`summary`: runs/network-eval/<scenario>/summary.parquet, one row per candidate: km, stations,
running time (central and band), isochrone population reached (change vs S1), 30-minute towns,
capex and opex P10/P50/P90, uplifted P50/P80, run ids. Ranges only, never points.
`hhr`: the HHR 2025 validation with and without the international segment against +/-15 %
(A-demand-032; status validation, not fitted) and the Ramadan check.

  uv run python -m network.evaluate costs --seed 1
  uv run python -m network.evaluate summary --seed 1
  uv run python -m network.evaluate hhr --seed 1

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.runmeta import seed_option, write_meta

COSTING = Path("runs/network-eval/costing")
ACCESS = Path("cities/ksa/assumptions/access_network.yaml")
CLASSES = Path("cities/ksa/assumptions/running_time_classes.yaml")
COST_ASSUMPTIONS = {
    "track": {"value": "double", "assumption_id": "A-r4-cost-001"},
    "electrified": {"value": True, "assumption_id": "A-r4-cost-002"},
    "span": {"value": "06:00-23:00", "assumption_id": "A-r4-cost-003"},
    "unknown_terrain": {"value": "flat_desert", "assumption_id": "A-cost-010"},
}

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Network evaluation."""


def _v(node: Any) -> Any:
    return node["value"] if isinstance(node, dict) and "value" in node else node


def _shares(terr: dict[str, float], tot: float) -> dict[str, float]:
    """Shares rounded to 6 decimals; the rounding residual goes to the largest share so they sum
    to 1 within the estimator's 1e-6 check."""
    sh = {k: round(v / tot, 6) for k, v in terr.items() if v > 0}
    big = max(sh, key=sh.get)
    sh[big] = round(sh[big] + 1.0 - sum(sh.values()), 6)
    return sh


def costing_input(
    c: dict[str, Any], root: Path = REPO_ROOT
) -> tuple[dict[str, Any], dict[str, Any]]:
    """(LineSpec dict, costing sidecar) for one corridor YAML dict."""
    acc = yaml.safe_load((root / ACCESS).read_text(encoding="utf-8"))
    cls = yaml.safe_load((root / CLASSES).read_text(encoding="utf-8"))
    lt = c["line_type"]
    stock = cls["classes"][cls["by_line_type"][lt]]
    hw = acc["hypothetical_service"]["headway_min"]
    headway = float(_v(hw.get(lt, hw["default"])))
    stations = []
    planned = c.get("family") == "station_addition"
    for s in c["stations"]:
        cl = s.get("class", "intermediate")
        if planned:
            cl = "intermediate" if cl == "planned" else "terminal"
        stations.append(
            {k: s[k] for k in ("id", "name_en", "name_ar", "km_post", "lat", "lon", "source")}
            | {"class": cl}
        )
    spec = {
        "id": c["id"],
        "name_en": c["name_en"],
        "name_ar": c["name_ar"],
        "layer": "hypothetical",
        "operator": None,
        "status": "generated",
        "source": str(c.get("source", "screening.corridors")),
        "source_date": str(c.get("source_date")),
        "accessed": str(c.get("accessed")),
        "line_type": lt,
        "design_speed_kmh": float(_v(stock["vmax_kmh"])),
        "track": _v(COST_ASSUMPTIONS["track"]),
        "electrified": _v(COST_ASSUMPTIONS["electrified"]),
        "length_km": float(c["length_km"]),
        "alignment": c.get("alignment"),
        "generated_from": str(c.get("generated_from")),
        "rules_hash": str(c.get("rules_hash")),
        "stations": stations,
        "services": [
            {
                "id": "all_stop",
                "stops": "all",
                "headway_min": headway,
                "span": _v(COST_ASSUMPTIONS["span"]),
                "sampled": "2026-11-01",
                "source": "A-r4-acc-003 / A-demand-049 (hypothetical service)",
            }
        ],
        "running_time_model": {
            "accel_ms2": {
                "value": float(_v(stock["accel_ms2"])),
                "assumption": "A-r4-rt-001..008 (class)",
            },
            "decel_ms2": {"value": float(_v(stock["decel_ms2"])), "assumption": "A-r1a-034"},
            "cruise_kmh": {
                "value": float(_v(stock["vmax_kmh"])),
                "assumption": "running_time_classes.yaml",
            },
            "dwell_s": {"value": float(_v(stock["dwell_s"]["default"])), "assumption": "A-r1a-035"},
        },
        "notes": f"R4 costing input generated by network.evaluate from {c['id']}; {LABEL}",
    }
    terr = dict(c.get("terrain_shares") or {"unknown": 1.0})
    routed = bool((c.get("alignment_routed") or {}).get("status") == "routed")
    t_id = "A-align-060" if routed else "A-corr-013"
    s_ids = {"tunnel": "A-align-042", "viaduct": "A-align-041"} if routed else {}
    unk = float(terr.pop("unknown", 0.0))
    terr["flat_desert"] = terr.get("flat_desert", 0.0) + unk
    tot = sum(terr.values())
    costing = {
        "costing": {
            "terrain_shares": {
                k: {"value": v, "assumption_id": t_id} for k, v in _shares(terr, tot).items()
            },
            "structure_shares": {
                k: {"value": float(v), "assumption_id": s_ids.get(k, "A-corr-014")}
                for k, v in (c.get("structures_share") or {}).items()
            },
        },
        "unknown_terrain_share_filled_flat_desert": round(unk / tot, 4) if tot else None,
        "unknown_terrain_assumption": "A-cost-010",
        "alignment": "routed (R4_ALIGN, measured shares)"
        if routed
        else "straight sketch (proxy shares)",
    }
    return spec, costing


@app.command("costs")
def costs_cmd(
    seed: int = seed_option(),
    draws: int = typer.Option(10_000),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """costs.estimate for every S2-S5 candidate (runs/costs/<id>/)."""
    from access.isochrones import candidate_list

    (root / COSTING).mkdir(parents=True, exist_ok=True)
    done = []
    for fam, path in candidate_list(root):
        c = yaml.safe_load((root / path).read_text(encoding="utf-8"))
        skip = root / "runs/costs" / c["id"] / "SKIPPED.json"
        reason = infeasible_reason(c)
        if reason:
            # R4_ALIGN A-align-091: an impossible profile is not priced; a stale run is never read
            if skip.parent.exists():
                import shutil

                shutil.rmtree(skip.parent)  # no stale estimate beside the marker
            skip.parent.mkdir(parents=True, exist_ok=True)
            skip.write_text(json.dumps({"id": c["id"], "reason": reason}, indent=1) + "\n")
            done.append({"id": c["id"], "family": fam, "ok": False, "skipped": reason})
            typer.echo(f"{c['id']}: not costed ({reason})")
            continue
        if skip.exists():
            skip.unlink()
        spec, costing = costing_input(c, root)
        sp = root / COSTING / f"{c['id']}.yaml"
        cp = root / COSTING / f"{c['id']}.costing.yaml"
        sp.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
        cp.write_text(yaml.safe_dump(costing, sort_keys=False), encoding="utf-8")
        out = Path("runs/costs") / c["id"]
        r = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "costs.estimate",
                "--corridor",
                str(sp),
                "--costing",
                str(cp),
                "--seed",
                str(seed),
                "--draws",
                str(draws),
                "--out",
                str(out),
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        done.append(
            {
                "id": c["id"],
                "family": fam,
                "ok": r.returncode == 0,
                "stderr": r.stderr[-400:] if r.returncode else "",
            }
        )
        typer.echo(f"{c['id']}: {'ok' if r.returncode == 0 else 'FAILED'}")
    run = root / "runs/network-eval" / f"costs-s{seed}"
    run.mkdir(parents=True, exist_ok=True)
    (run / "costs.json").write_text(json.dumps(done, indent=1) + "\n")
    write_meta(run, seed, {"assumptions": COST_ASSUMPTIONS}, extra={"label": LABEL, "runs": done})


def infeasible_reason(c: dict[str, Any]) -> str | None:
    """Why a routed corridor is not costed (R4_ALIGN A-align-091), or None."""
    r = c.get("alignment_routed") or {}
    if r.get("status") != "routed" or r.get("profile_feasible", True):
        return None
    legs = "; ".join(
        f"{x['from']}-{x['to']}: {x['height_difference_m']:.0f} m in {x['routed_km']:.1f} km "
        f"(at least {x['min_km_at_cap']:.1f} km at the {100 * r['max_grade_cap']:.2f} % cap)"
        for x in r.get("infeasible_legs", [])
    )
    return f"grade-infeasible at the class cap: {legs or 'formation cap check failed'}"


def cost_row(cid: str, family: str, root: Path) -> dict[str, Any]:
    run = root / "runs/costs" / cid
    if (run / "SKIPPED.json").exists():
        why = json.loads((run / "SKIPPED.json").read_text())["reason"]
        nan = float("nan")
        return {
            "capex_basis": f"not costed: {why}",
            **{
                k: nan
                for k in (
                    "capex_p10",
                    "capex_p50",
                    "capex_p90",
                    "capex_uplifted_p10",
                    "capex_uplifted_p50",
                    "capex_uplifted_p80",
                    "capex_uplifted_p90",
                    "opex_p10",
                    "opex_p50",
                    "opex_p90",
                )
            },
            "opex_note": f"not costed: {why}",
            "cost_register_ids": "",
            "cost_run": None,
        }
    b = yaml.safe_load((run / "base.yaml").read_text(encoding="utf-8"))
    tr = pd.read_csv(run / "trace.csv")
    reg_ids = sorted({x.strip() for s in tr.register_id.dropna() for x in str(s).split(",")})
    if family == "S5":
        st = tr[tr.component == "station[intermediate]"].iloc[0]
        # the register station item has zero spread (an R1c default); the reference-class uplift
        # draws of the same run (rcf/distribution.parquet, capex_multiplier) give the range
        mult = pd.read_parquet(run / "rcf/distribution.parquet").capex_multiplier.to_numpy()
        up = float(st.P50) * mult
        q = {
            k: float(np.percentile(up, v))
            for k, v in (("p10", 10), ("p50", 50), ("p80", 80), ("p90", 90))
        }
        return {
            "capex_basis": "new station only: register station item (zero-spread R1c default, no release use until "
            "cleared) x the reference-class capex multiplier draws of the same run",
            "capex_p10": float(st.P10),
            "capex_p50": float(st.P50),
            "capex_p90": float(st.P90),
            "capex_uplifted_p10": q["p10"],
            "capex_uplifted_p50": q["p50"],
            "capex_uplifted_p80": q["p80"],
            "capex_uplifted_p90": q["p90"],
            "opex_p10": None,
            "opex_p50": None,
            "opex_p90": None,
            "opex_note": "unknown: the R1c register has no per-station operating item and an added stop adds no "
            "train-km (the register's opex units)",
            "cost_register_ids": f"{st.register_id}; uplifts as in {run.relative_to(root)}/rcf/summary.yaml",
            "cost_run": str(run.relative_to(root)),
        }
    cb, cu, op = b["capex_base_sar_m"], b["capex_uplifted_sar_m"], b["opex_sar_m_per_year"]
    return {
        "capex_basis": "whole corridor (base P10/P50/P90; uplifted by the reference-class uplift)",
        "capex_p10": cb["P10"],
        "capex_p50": cb["P50"],
        "capex_p90": cb["P90"],
        "capex_uplifted_p50": cu["P50"],
        "capex_uplifted_p80": cu["P80"],
        "opex_p10": op["P10"],
        "opex_p50": op["P50"],
        "opex_p90": op["P90"],
        "cost_register_ids": ";".join(reg_ids),
        "cost_run": str(run.relative_to(root)),
    }


@app.command("summary")
def summary_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """runs/network-eval/<S2..S5>/summary.parquet (one row per candidate)."""
    from access import running_time as rt
    from access.isochrones import candidate_list

    iso = pd.read_parquet(root / f"runs/access/isochrones-summary-s{seed}/reached_all.parquet")
    ct = pd.read_parquet(root / f"runs/access/commute-test-s{seed}/commute_test.parquet")
    s1 = iso[iso.scenario == "S1"]
    key = ["metro", "mode", "band_min"]
    s1_30 = set(
        ct[(ct.scenario == "S1") & ct.within_30_ivt].apply(lambda r: (r.metro, r.row_key), axis=1)
    )
    rows = []
    for fam, path in candidate_list(root):
        c = yaml.safe_load((root / path).read_text(encoding="utf-8"))
        cid = c["id"]
        res = {}
        for case in ("value", "low", "high"):
            run = rt.build_run(c, root, case)
            if c.get("family") == "station_addition":
                # minutes the new stop adds to a through train on the host segment (per-stop cost)
                sc = rt.stop_costs(run, run.stations.id.tolist())
                new_ids = {x["id"] for x in c["stations"] if x.get("class") == "planned"}
                res[case] = float(sc[sc.station.isin(new_ids)].stop_cost_min.sum())
                continue
            tab = rt.pair_table(run, run.stations.id.tolist())
            res[case] = float(tab.ivt_min.iloc[len(run.stations) - 2])
        fac = json.loads((root / "runs/access/running_time/factors-s1/factors.json").read_text())[
            "generic"
        ]
        it = iso[iso.scenario == cid].merge(s1[key + ["population"]], on=key, suffixes=("", "_s1"))
        it["delta"] = it.population - it.population_s1
        dd = {
            f"pop_{m}_{b}_delta_vs_s1": float(
                it[(it["mode"] == m) & (it.band_min == b)].delta.sum()
            )
            for m in ("in_vehicle", "door_to_door")
            for b in (30, 60)
        }
        c30 = ct[(ct.scenario == cid) & ct.within_30_ivt]
        new30 = sorted(
            {f"{r.town} ({r.metro})" for r in c30.itertuples() if (r.metro, r.row_key) not in s1_30}
        )
        row = {
            "scenario": fam,
            "candidate": cid,
            "family": c.get("family"),
            "line_type": c["line_type"],
            "km": float(c["length_km"]),
            "stations": len(c["stations"]),
            "run_min_basis": "added minutes per through train (stop cost of the new station)"
            if c.get("family") == "station_addition"
            else "end-to-end all-stop",
            "run_min_kinematic": res["value"],
            "run_min_p10": res["value"] * fac["range"][0],
            "run_min_p50": res["value"] * fac["value"],
            "run_min_p90": res["value"] * fac["range"][1],
            **dd,
            "towns_within_30_ivt": int(c30.row_key.nunique()),
            "towns_within_30_new_vs_s1": len(new30),
            "towns_within_30_new_list": "; ".join(new30),
            **cost_row(cid, fam, root),
            "isochrone_run": f"runs/access/{cid}",
            "commute_test_run": f"runs/access/commute-test-s{seed}",
            "label": LABEL,
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    for fam, g in df.groupby("scenario"):
        out = root / "runs/network-eval" / fam
        out.mkdir(parents=True, exist_ok=True)
        g.to_parquet(out / "summary.parquet", index=False)
        write_meta(
            out,
            seed,
            {"scenario": fam, "candidates": g.candidate.tolist()},
            extra={
                "label": LABEL,
                "note": "ranges only: P10/P50/P90; run_min band = timetable factor range",
            },
        )
    typer.echo(
        df.groupby("scenario")
        .agg(n=("candidate", "size"), capex_p50_sum=("capex_p50", "sum"))
        .to_string()
    )


@app.command("hhr")
def hhr_cmd(
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """HHR 2025 with and without the international segment vs +/-15 % (validation, not fitted)."""
    import warnings

    cal = yaml.safe_load((root / "cities/ksa/assumptions/demand_calibration.yaml").read_text())
    obs = next(t["value"] for t in cal["targets"] if t["id"] == "rail-hhr-pax-2025")
    tol = 0.15
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = pd.read_excel(
            root / "data/ksa/calibration/gastat_rail_tables_2025/railway_tables_2025_en.xlsx",
            sheet_name="1-2",
            header=None,
        ).fillna("")
    hhr_m = next(
        [float(x) for x in [str(v).strip() for v in r if str(v).strip()][2:14]]
        for r in m.values
        if str(r[0]).strip() == "Haramain High Speed Railway"
    )
    ram_obs = hhr_m[2] / (sum(hhr_m) / 12.0)  # March 2025 = Ramadan 1446
    rows = []
    for s in ("S0", "S1"):
        res = json.loads((root / f"runs/r4/demand/{s}-r4-2025-base-s1/totals.json").read_text())
        intl = json.loads((root / f"runs/intl/{s}-s1/totals.json").read_text())
        resident = float(res["rail_by_line"]["hhr"]["passengers"])
        ih = intl["rail_by_line"].get("hhr", {"value": 0, "low": 0, "high": 0})
        pk = intl["peaks"].get("hhr", {})
        for case in ("value", "low", "high"):
            tot = resident + float(ih[case])
            rows.append(
                {
                    "scenario": s,
                    "rail_share_case": case,
                    "observed_2025": obs,
                    "resident": resident,
                    "international": float(ih[case]),
                    "total": tot,
                    "deviation_without_pct": 100 * (resident / obs - 1),
                    "deviation_with_pct": 100 * (tot / obs - 1),
                    "within_tolerance_without": abs(resident / obs - 1) <= tol,
                    "within_tolerance_with": abs(tot / obs - 1) <= tol,
                    "status": "validation, not fitted",
                }
            )
        if s == "S0":
            legs = float(ih["value"]) / 0.176 if ih["value"] else float("nan")
            implied = (obs - resident) / legs if legs else float("nan")
            ram_model = (resident / 12 + pk.get("ramadan_month", 0)) / (
                (resident + ih["value"]) / 12
            )
    out = root / f"runs/network-eval/hhr-validation-s{seed}"
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out / "hhr_validation.csv", index=False)
    extra = {
        "tolerance": {"rel": tol, "assumption": "A-demand-032"},
        "implied_rail_share_for_exact_fit_S0": implied,
        "ramadan_factor_observed_march_2025": ram_obs,
        "ramadan_factor_model_central_S0": ram_model,
        "label": LABEL,
    }
    (out / "hhr_validation.json").write_text(
        json.dumps({"rows": rows, **extra}, indent=1, default=float) + "\n"
    )
    write_meta(out, seed, {"observed": obs}, extra=extra)
    typer.echo(df.round(1).to_string(index=False))
    typer.echo(
        json.dumps(
            {k: (round(v, 4) if isinstance(v, float) else v) for k, v in extra.items()}, default=str
        )
    )


if __name__ == "__main__":
    app()
