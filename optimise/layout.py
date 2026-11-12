"""R6 layout adapter: scores a whole national layout (several corridors, variants, phases) with
the frozen R5 demand model and appraisal, calling their functions unchanged (R6 design B).

Run it with the judge's own files first on the import path (never this checkout's modules):

  .venv/bin/python judge/<name>/optimise/layout.py evaluate --judge judge/<name> \
      --layout scenarios/candidate.yaml --out runs/r6/eval/<id> --draws 10000 --seed 1

What it adds to R5 (and nothing else):
- line sets: `access.railgraph.scenario_lines` is wrapped so a layout marker file
  (`{r6_layout: [...]}`) stands for S1 plus every corridor of the layout (station additions are
  inserted into their host line, lines appended), exactly as R5 adds one candidate;
- variants: a corridor may change `line_type` (running times, headway, fare and costing follow the
  R5 class tables), `track`, `electrified` (costing only) or drop intermediate stations; a variant
  is costed by the frozen `network.evaluate.costing_input` + `costs.estimate`;
- phases: the layout is appraised as tranches (corridors of one phase), tranche k = layout up to
  phase k against the layout up to phase k-1 (S1 for k = 1), with construction starting
  `phase - 3` (A-r6-002; phase 2030 = the R5 start year 2027, A-cba-301); every tranche is a
  `economics.cba.evaluate` call and present values add draw by draw (same Monte Carlo seed);
- lines and station additions in one tranche are two appraisal contexts (R5 treats a station
  addition as its own family: station-only capex, no added train-km); the demand change is booked
  once, on the lines context (or on the first station context if the tranche has no line).

Score (A-r6-001): robust NPV = min over the low/medium/high population cases of
P50(PVB) - P50(PVC), 60 years, Green Book 2026 rates, without wider impacts (CP6 P4a).

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import os
import sys

_J = os.environ.get("R6_JUDGE_ROOT")
if _J:
    _J = os.path.abspath(_J)
    if _J not in sys.path:
        sys.path.insert(0, _J)

import dataclasses  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

LABEL = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
POPS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
PHASES = (2030, 2035, 2040, 2050)
START_LAG = 3  # A-r6-002: construction start = phase year - 3 (phase 2030 -> 2027 = A-cba-301)
FAMILY_DIRS = {
    "S2": "trunk_gap",
    "S3": "branch_spur",
    "S4": "commuter_belt",
    "S5": "station_addition",
}
ACCESS_METROS = ("Riyadh", "Jeddah", "Makkah", "Madinah", "Dammam–Khobar–Dhahran")
ACCESS_BANDS = (60, 120)
LOAD_LINES = ("hhr", "landbridge", "riyadh-rail-link")
LINE_TYPES = ("hsr", "mixed", "conventional_passenger", "commuter")


def jroot() -> Path:
    if not _J:
        raise SystemExit("R6_JUDGE_ROOT is not set: run through optimise.search or set it")
    return Path(_J)


# --------------------------------------------------------------------------- layout file
def load_layout(path: Path) -> dict[str, Any]:
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    d.setdefault("corridors", [])
    for c in d["corridors"]:
        c.setdefault("phase", 2030)
        if int(c["phase"]) not in PHASES:
            raise ValueError(f"{c['id']}: phase {c['phase']} not in {PHASES}")
    return d


def corridor_path(cid: str, root: Path) -> Path:
    fam = FAMILY_DIRS[cid.split("-")[0]]
    if "jubail-two-stations" in cid:
        return Path("cities/ksa/cba/variants") / f"{cid}.yaml"
    return Path("cities/ksa/corridors") / fam / f"{cid}.yaml"


def variant_key(item: dict[str, Any]) -> dict[str, Any]:
    return {k: item[k] for k in ("line_type", "track", "electrified", "drop_stations") if k in item}


def variant_id(item: dict[str, Any]) -> str:
    v = variant_key(item)
    if not v:
        return item["id"]
    h = hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()[:8]
    return f"{item['id']}-v{h}"


def materialise(item: dict[str, Any], root: Path) -> dict[str, Any]:
    """Corridor dict of one layout item with its variant fields applied."""
    c = yaml.safe_load((root / corridor_path(item["id"], root)).read_text(encoding="utf-8"))
    v = variant_key(item)
    if not v:
        return c
    c = dict(c)
    c["id"] = variant_id(item)
    if "line_type" in v:
        c["line_type"] = v["line_type"]
    if v.get("drop_stations"):
        drop = set(v["drop_stations"])
        keep = [s for s in c["stations"] if s["id"] not in drop or s.get("class") == "terminal"]
        if len(keep) != len(c["stations"]) - len(drop):
            raise ValueError(f"{item['id']}: only intermediate stations can be dropped")
        c["stations"] = keep
    c["r6_variant"] = v
    return c


def feasibility(item: dict[str, Any], root: Path) -> list[str]:
    """Hard checks of one item (gradient/curve limits of its class, A-r6-004)."""
    errs = []
    if "line_type" in item:
        if item["line_type"] not in LINE_TYPES:
            errs.append(f"{item['id']}: line_type {item['line_type']} not allowed")
            return errs
        c = yaml.safe_load((root / corridor_path(item["id"], root)).read_text(encoding="utf-8"))
        if c.get("family") == "station_addition":
            errs.append(f"{item['id']}: a station addition has no line type")
            return errs
        side = root / "cities/ksa/alignments" / f"{item['id']}.json"
        a = json.loads(side.read_text(encoding="utf-8"))
        cls = yaml.safe_load(
            (root / "cities/ksa/assumptions/running_time_classes.yaml").read_text(encoding="utf-8")
        )
        vmax = float(cls["classes"][cls["by_line_type"][item["line_type"]]]["vmax_kmh"]["value"])
        cap = 0.0125 if item["line_type"] == "mixed" else 0.025  # R4_ALIGN caps (A-align-020)
        if float(a.get("formation_max_grade") or 0.0) > cap + 1e-4:
            errs.append(
                f"{item['id']}: formation grade {a['formation_max_grade']:.4f} > {cap} for "
                f"{item['line_type']} (needs re-routing)"
            )
        if float(a.get("min_curve_kmh") or 0.0) + 1e-6 < vmax and vmax > float(
            a.get("design_kmh") or 0.0
        ):
            errs.append(
                f"{item['id']}: alignment routed for {a.get('design_kmh')} km/h, curves limit "
                f"{a.get('min_curve_kmh')} km/h < {vmax} ({item['line_type']}; needs re-routing)"
            )
    return errs


def protected_km(cid: str, root: Path) -> float:
    side = root / "cities/ksa/alignments" / f"{cid}.json"
    if not side.exists():
        return 0.0
    a = json.loads(side.read_text(encoding="utf-8"))
    return float((a.get("area_km") or {}).get("protected") or 0.0)


# --------------------------------------------------------------------------- line-set wrapper
_PATCHED = False


def patch_railgraph() -> None:
    """Wrap access.railgraph.scenario_lines: a marker file {r6_layout: [items]} = S1 + items."""
    global _PATCHED
    if _PATCHED:
        return
    from access import railgraph

    orig = railgraph.scenario_lines

    def scenario_lines(scenario, cfg, root=railgraph.REPO_ROOT, candidate=None):
        if candidate is not None:
            p = Path(candidate)
            p = p if p.is_absolute() else Path(root) / p
            d = yaml.safe_load(p.read_text(encoding="utf-8"))
            if isinstance(d, dict) and "r6_layout" in d:
                lines = orig(scenario, cfg, root, None)
                for item in d["r6_layout"]:
                    c = materialise(item, Path(root))
                    if c.get("family") == "station_addition":
                        lines = railgraph.insert_station(lines, c)
                    else:
                        lines.append(c)
                return lines
        return orig(scenario, cfg, root, candidate)

    railgraph.scenario_lines = scenario_lines
    _PATCHED = True


def write_marker(items: list[dict[str, Any]], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({"r6_layout": items, "label": LABEL}, sort_keys=False), encoding="utf-8"
    )
    return path


# --------------------------------------------------------------------------- costs of variants
def cost_refs_for(item: dict[str, Any], root: Path, out: Path, seed: int) -> dict[str, str]:
    """(cost_run, cost_spec, cost_costing) of one item: R5 runs, or a variant costed now."""
    cid = item["id"]
    if not variant_key(item):
        if "jubail-two-stations" in cid:
            base = "S5-station_addition-al-jubayl"
            return {
                "cost_run": f"runs/costs/{base}",
                "cost_spec": f"runs/network-eval/costing/{base}.yaml",
                "cost_costing": f"runs/network-eval/costing/{base}.costing.yaml",
            }
        return {
            "cost_run": f"runs/costs/{cid}",
            "cost_spec": f"runs/network-eval/costing/{cid}.yaml",
            "cost_costing": f"runs/network-eval/costing/{cid}.costing.yaml",
        }
    import subprocess

    from network import evaluate as nev

    vid = variant_id(item)
    vdir = (out / "variants" / vid).resolve()
    done = vdir / "cost" / "rcf" / "distribution.parquet"
    if not done.exists():
        c = materialise(item, root)
        spec, costing = nev.costing_input(c, root)
        if "track" in item:
            spec["track"] = item["track"]
        if "electrified" in item:
            spec["electrified"] = bool(item["electrified"])
        vdir.mkdir(parents=True, exist_ok=True)
        (vdir / "spec.yaml").write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True))
        (vdir / "costing.yaml").write_text(yaml.safe_dump(costing, sort_keys=False))
        env = dict(os.environ, PYTHONPATH=str(root))
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "costs.estimate",
                "--corridor",
                str(vdir / "spec.yaml"),
                "--costing",
                str(vdir / "costing.yaml"),
                "--seed",
                str(seed),
                "--draws",
                "10000",
                "--out",
                str(vdir / "cost"),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            env=env,
        )
        if r.returncode:
            raise RuntimeError(f"variant costing failed for {vid}: {r.stderr[-600:]}")
    return {
        "cost_run": str(vdir / "cost"),
        "cost_spec": str(vdir / "spec.yaml"),
        "cost_costing": str(vdir / "costing.yaml"),
    }


# --------------------------------------------------------------------------- demand
def _demand_group(args: tuple) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """One (population, year) group: S1 and the cumulative layout of every phase; scalars of
    every tranche against the previous cumulative network (demandruns.run_group logic)."""
    pop, year, markers, tranche_ids, root_s = args
    root = Path(root_s)
    patch_railgraph()
    from demand import gravity
    from economics import benefits, demandruns
    from economics import params as prm

    ov = demandruns.overrides(root)
    p = prm.load(root)
    zones = gravity.zone_population(year, pop, root)
    jz = demandruns.jeddah_zones(zones)
    coefs = gravity.coefficients(ov)
    b_car = abs(float(coefs.ivt["car"]))
    asc = {m: float(coefs.asc.get(m, 0.0)) for m in ("car", "rail", "air", "bus")}

    def run(candidate: str | None) -> dict[str, Any]:
        cfg = gravity.RunConfig("S1", pop, year, ov, {}, root, network="r4", candidate=candidate)
        return gravity.run_model(cfg)

    prev = run(None)
    rows = []
    loads: dict[str, Any] = {"S1": line_loads(prev)}
    jobs = zones.jobs.fillna(0.0).to_numpy(dtype=float)
    for m, tid in zip(markers, tranche_ids, strict=True):
        cur = run(m)
        ph = benefits.extract(prev, cur, zones, p, jz, b_car, asc)
        d = dataclasses.asdict(ph)
        um = d.pop("user_min")
        d.pop("user_min_zone")
        wei = d.pop("wei_dlnED")
        d["wei_job_weighted_dlnED"] = float(np.nansum(jobs * wei))
        rows.append(
            {
                "case": tid,
                "population": pop,
                "year": year,
                **{f"user_min_{q}": v for q, v in um.items()},
                **d,
            }
        )
        prev = cur
    loads |= line_loads(prev)
    return demandruns.group_id(pop, year), rows, loads


def line_loads(res: dict[str, Any]) -> dict[str, Any]:
    from demand import gravity

    od = res["od"]
    allp = pd.concat([d.assign(purpose=q) for q, d in od.items()], ignore_index=True)
    rail = allp[allp.trips_rail > 0]
    out = {
        "rail_trips": float(allp.trips_rail.sum()),
        "rail_pkm_m": float((rail.trips_rail * rail.rail_km).sum() / 1e6),
    }
    if "rail_path" in rail.columns:
        out["by_line"] = gravity.path_line_totals(rail)
    return out


# --------------------------------------------------------------------------- appraisal
def _params_with_start(p: Any, start: int) -> Any:
    from economics import params as prm

    q = p["construction_start_year"]
    num = dict(p.numeric)
    num["construction_start_year"] = dataclasses.replace(
        q, value=float(start), low=float(start), high=float(start)
    )
    return prm.Params(num, p.raw)


def _case(cid: str, family: str, cand: str | None, refs: dict[str, str], inputs: Path, n: int):
    from common.schemas import CbaCase
    from economics import cli as ecli

    d = ecli.base_case(cid, "S6", "S1")
    d["id"] = cid
    d |= {"family": family, "candidate": cand, **refs, "demand_runs": str(inputs)}
    d["costs"] = ecli.cost_refs(refs["cost_run"].split(","))
    d["monte_carlo"]["draws"] = n
    return CbaCase.model_validate(d)


def appraise(
    contexts: list[dict[str, Any]],
    root: Path,
    seed: int,
    n: int,
    horizons: list[int],
    rate_cases: list[str],
) -> dict[str, Any]:
    """Sum of per-draw present values over every appraisal context of the layout."""
    from economics import cba, montecarlo
    from economics import params as prm

    p0 = prm.load(root)
    acc: dict[tuple[str, int, str], dict[str, np.ndarray]] = {}
    capex = np.zeros(n)
    capex_base = np.zeros(n)
    for cx in contexts:
        p = _params_with_start(p0, cx["start"])
        case = _case(cx["id"], cx["family"], cx["candidate"], cx["refs"], cx["inputs"], n)
        ctx = cba.context(case, root, p)
        draws = montecarlo.draw_inputs(
            str(case.cost_run),
            str(case.cost_spec),
            case.cost_costing,
            p,
            seed,
            n,
            root,
            (p["rate_shift"].low, p["rate_shift"].high),
            station_addition=cba.n_planned(case, root),
        )
        capex += draws.capex.to_numpy()
        capex_base += draws.capex_base.to_numpy()
        for pop in POPS:
            ev = cba.evaluate(ctx, draws, pop, horizons, rate_cases, detail=True)
            for (h, rc), r in ev.items():
                a = acc.setdefault((pop, h, rc), {})
                for k, v in r.items():
                    if k in ("pvb", "pvc", "fiscal_cost") or k.startswith("pv_"):
                        a[k] = a.get(k, 0.0) + v
                a["pv_wei"] = a.get("pv_wei", 0.0) + (r["npv_wei"] - r["npv"])
    return {"acc": acc, "capex": capex, "capex_base": capex_base}


def q(x: np.ndarray, v: float) -> float:
    """Percentile as economics.cba.pct: method "nearest", NaN counts as the lowest value."""
    a = np.asarray(x, dtype=float)
    return float(np.percentile(np.where(np.isnan(a), -np.inf, a), v, method="nearest"))


def summarise(ap: dict[str, Any]) -> dict[str, Any]:
    acc = ap["acc"]
    rows = []
    for (pop, h, rc), a in sorted(acc.items()):
        pvb, pvc = a["pvb"], a["pvc"]
        npv = pvb - pvc
        with np.errstate(divide="ignore", invalid="ignore"):
            bcr = np.where(pvc > 0, pvb / pvc, np.inf)
        rows.append(
            {
                "population": pop,
                "horizon": h,
                "rate_case": rc,
                "pvb_p50": q(pvb, 50),
                "pvc_p10": q(pvc, 10),
                "pvc_p50": q(pvc, 50),
                "pvc_p90": q(pvc, 90),
                "npv_p10": q(npv, 10),
                "npv_p50": q(npv, 50),
                "npv_p90": q(npv, 90),
                "npv_at_p50_cost": q(pvb, 50) - q(pvc, 50),
                "npv_at_p90_cost": q(pvb, 50) - q(pvc, 90),
                "bcr_p10": q(bcr, 10),
                "bcr_p50": q(bcr, 50),
                "bcr_p90": q(bcr, 90),
                "pv_wei_p50": q(a["pv_wei"], 50),
                "fiscal_cost_p50": q(a["fiscal_cost"], 50),
                **{f"{k}_p50": q(v, 50) for k, v in a.items() if k.startswith("pv_")},
            }
        )
    return {
        "rows": rows,
        "capex_p10": q(ap["capex"], 10),
        "capex_p50": q(ap["capex"], 50),
        "capex_p90": q(ap["capex"], 90),
        "capex_base_p50": q(ap["capex_base"], 50),
    }


# --------------------------------------------------------------------------- accessibility
def accessibility(marker: Path | None, root: Path) -> dict[str, Any]:
    """Population (2025, WPP medium GASTAT-anchored: the R4 isochrone base) within 60/120
    door-to-door minutes of the five named metros, S1 and the layout."""
    patch_railgraph()
    from access import isochrones as iso

    ms = [m for m in iso.metros(root) if m["name"] in ACCESS_METROS]
    zones = iso.zones_table(root)
    road = pd.read_parquet(root / "runs/skims/r3-zones/road.parquet")
    out: dict[str, Any] = {}
    zsets: dict[str, Any] = {}
    for tag, cand in (("S1", None), ("layout", marker)):
        ctx = iso.context("S1", cand, root, zones=zones, road=road)
        res, zs = {}, {}
        for m in ms:
            tab, zz = iso.reached(ctx, m, iso.anchor_zone(m, root))
            t = tab[tab["mode"].eq("door_to_door") & tab.band_min.isin(ACCESS_BANDS)]
            res[m["name"]] = {int(r.band_min): float(r.population) for r in t.itertuples()}
            zs[m["name"]] = {
                str(b): sorted(zz.loc[zz.d2d_min <= b, "zone_id"].astype(str)) for b in ACCESS_BANDS
            }
        out[tag] = res
        zsets[tag] = zs
    gain = {b: sum(out["layout"][m][b] - out["S1"][m][b] for m in out["S1"]) for b in ACCESS_BANDS}
    return {
        "by_metro": out,
        "gain_sum_over_metros": {str(b): v for b, v in gain.items()},
        "population_base": "2025, un_wpp_medium_gastat2024 (access.isochrones.POP)",
        "zones_reached": zsets,
    }


# --------------------------------------------------------------------------- evaluate
def tranches(layout: dict[str, Any]) -> list[tuple[int, list[dict[str, Any]]]]:
    by: dict[int, list[dict[str, Any]]] = {}
    for c in layout["corridors"]:
        by.setdefault(int(c["phase"]), []).append(c)
    return sorted(by.items())


def constraints(layout: dict[str, Any], root: Path, capex_p50: float | None) -> dict[str, Any]:
    errs, flags = [], []
    seen = set()
    for c in layout["corridors"]:
        if c["id"] in seen:
            errs.append(f"{c['id']}: listed twice")
        seen.add(c["id"])
        if not (root / corridor_path(c["id"], root)).exists():
            errs.append(f"{c['id']}: unknown corridor")
            continue
        if (root / "runs/costs" / c["id"] / "SKIPPED.json").exists():
            errs.append(f"{c['id']}: not costed in R5 (grade-infeasible)")
        errs += feasibility(c, root)
        pk = protected_km(c["id"], root)
        if pk > 0:
            flags.append(f"{c['id']}: {pk:.1f} km through protected areas (WDPA; flagged)")
    ceiling = layout.get("capex_ceiling_sar_m")
    if ceiling is not None and capex_p50 is not None and capex_p50 > float(ceiling):
        errs.append(f"capex P50 {capex_p50:,.0f} > ceiling {float(ceiling):,.0f} SAR m")
    return {"errors": errs, "flags": flags}


def connected_phases(layout: dict[str, Any], root: Path) -> tuple[list[str], list[str]]:
    """Each phase deliverable on its own (A-r6-005): a line corridor whose terminals touch neither
    the S1 network nor any other layout corridor is an island (flagged, allowed: R2 generated it
    that way); one that touches only layout corridors needs one of them in the same or an earlier
    phase (station additions sit on S1 lines)."""
    from access import railgraph

    cfg = railgraph.load_cfg(root)
    net = []
    for ld in railgraph.scenario_lines("S1", cfg, root, None):
        net += [(float(s["lat"]), float(s["lon"])) for s in ld["stations"]]
    net_a = np.array(net)
    mats = {c["id"]: (int(c["phase"]), materialise(c, root)) for c in layout["corridors"]}
    lines = {k: v for k, v in mats.items() if v[1].get("family") != "station_addition"}
    pts = {
        k: np.array([(float(s["lat"]), float(s["lon"])) for s in v[1]["stations"]])
        for k, v in lines.items()
    }

    def near(a: np.ndarray, b: np.ndarray) -> bool:
        if not len(a) or not len(b):
            return False
        g = np.broadcast_arrays(a[:, None, 1], a[:, None, 0], b[None, :, 1], b[None, :, 0])
        d = railgraph.km_between(*(x.ravel() for x in g))
        return bool((d <= 1.0).any())

    errs, flags = [], []
    for k, (ph, _c) in lines.items():
        ends = pts[k][[0, -1]]
        if near(ends, net_a):
            continue
        others = [(o, lines[o][0]) for o in lines if o != k and near(ends, pts[o])]
        if not others:
            flags.append(f"{k}: island (touches neither S1 nor another layout corridor)")
        elif min(p for _, p in others) > ph:
            errs.append(
                f"phase {ph}: {k} connects only to later-phase corridors "
                f"{sorted(o for o, _ in others)}"
            )
    return errs, flags


def evaluate(
    layout_path: Path,
    out: Path,
    seed: int = 1,
    draws: int = 10000,
    workers: int = 4,
    with_access: bool = True,
    horizons: tuple[int, ...] = (60,),
    rate_cases: tuple[str, ...] = ("greenbook_2026",),
    phase_sweep: bool = False,
) -> dict[str, Any]:
    root = jroot()
    t0 = time.monotonic()
    layout = load_layout(layout_path)
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    cons = constraints(layout, root, None)
    if not cons["errors"]:
        ce, cf = connected_phases(layout, root)
        cons["errors"] += ce
        cons["flags"] += cf
    if cons["errors"]:
        res = {"label": LABEL, "feasible": False, **cons}
        (out / "score.json").write_text(json.dumps(res, indent=1) + "\n")
        return res
    tr = tranches(layout)
    if not tr:  # S1 itself: zero by construction
        res = {
            "label": LABEL,
            "feasible": True,
            **cons,
            "corridors": [],
            "n_corridors": 0,
            "robust_npv": 0.0,
            "npv_at_p50_cost": dict.fromkeys(POPS, 0.0),
            "capex_sar_m": {"capex_p50": 0.0},
            "access_gain_60": 0.0,
            "access_gain_120": 0.0,
        }
        (out / "score.json").write_text(json.dumps(res, indent=1) + "\n")
        return res
    markers, tids, cum = [], [], []
    for k, (ph, items) in enumerate(tr):
        cum = cum + [dict(c) for c in items]
        markers.append(str(write_marker(cum, out / f"layout-phase{k + 1}.yaml")))
        tids.append(f"CBA-R6-T{k + 1}-{ph}")
    from economics import demandruns

    jobs = [(pop, y, markers, tids, str(root)) for pop, y in demandruns.groups()]
    if workers <= 1:
        res_g = [_demand_group(j) for j in jobs]
    else:
        import multiprocessing as mp

        with mp.get_context("spawn").Pool(workers) as pool:
            res_g = pool.map(_demand_group, jobs)
    inputs = out / "inputs"
    loads = {}
    for gid, rows, ld in res_g:
        gd = inputs / gid
        gd.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(rows)
        zero = []
        for k, (_ph, items) in enumerate(tr):
            for c in items:
                zr = {
                    col: (0.0 if col not in ("case", "population", "year") else None)
                    for col in df.columns
                }
                zr |= {
                    "case": f"{tids[k]}-st-{c['id']}",
                    "population": rows[0]["population"],
                    "year": rows[0]["year"],
                }
                zero.append(zr)
        pd.concat([df, pd.DataFrame(zero)], ignore_index=True).to_parquet(
            gd / "scalars.parquet", index=False
        )
        loads[gid] = ld
    contexts = []
    for k, (ph, items) in enumerate(tr):
        tid = tids[k]
        lines = [c for c in items if not c["id"].startswith("S5-")]
        stations = [c for c in items if c["id"].startswith("S5-")]
        start = ph - START_LAG
        if lines:
            refs = [cost_refs_for(c, root, out, seed) for c in lines]
            fam = FAMILY_DIRS[lines[0]["id"].split("-")[0]]
            contexts.append(
                {
                    "id": tid,
                    "family": fam,
                    "candidate": None,
                    "refs": {key: ",".join(r[key] for r in refs) for key in refs[0]},
                    "inputs": inputs,
                    "start": start,
                }
            )
        for j, c in enumerate(stations):
            own_demand = not lines and j == 0
            contexts.append(
                {
                    "id": tid if own_demand else f"{tid}-st-{c['id']}",
                    "family": "station_addition",
                    "candidate": str(corridor_path(c["id"], root)),
                    "refs": cost_refs_for(c, root, out, seed),
                    "inputs": inputs,
                    "start": start,
                }
            )
    ap = appraise(contexts, root, seed, draws, list(horizons), list(rate_cases))
    sm = summarise(ap)
    sweep = {}
    if phase_sweep and len(tr) == 1:  # fast-mode library: the same tranche started per phase
        for ph in PHASES:
            cs = [dict(cx, start=ph - START_LAG) for cx in contexts]
            sp = summarise(appraise(cs, root, seed, draws, [60], ["greenbook_2026"]))
            sweep[str(ph)] = {
                "capex_p50": sp["capex_p50"],
                **{
                    f"{k}|{r['population']}": r[k]
                    for r in sp["rows"]
                    for k in ("pvb_p50", "pvc_p50", "pvc_p90", "npv_at_p50_cost", "npv_p50")
                },
            }
    cons2 = constraints(layout, root, sm["capex_p50"])
    cons["errors"] += [e for e in cons2["errors"] if e.startswith("capex")]
    central = [r for r in sm["rows"] if r["horizon"] == 60 and r["rate_case"] == "greenbook_2026"]
    npv_c = {r["population"]: r["npv_at_p50_cost"] for r in central}
    res: dict[str, Any] = {
        "label": LABEL,
        "feasible": not cons["errors"],
        **cons,
        "layout": layout_path.name,
        "corridors": [c["id"] for c in layout["corridors"]],
        "n_corridors": len(layout["corridors"]),
        "phases": {str(ph): [c["id"] for c in items] for ph, items in tr},
        "draws": draws,
        "seed": seed,
        "robust_npv": min(npv_c.values()),
        "robust_case": min(npv_c, key=npv_c.get),
        "npv_at_p50_cost": npv_c,
        "npv_at_p90_cost": {r["population"]: r["npv_at_p90_cost"] for r in central},
        "npv_p50": {r["population"]: r["npv_p50"] for r in central},
        "npv_p10": {r["population"]: r["npv_p10"] for r in central},
        "npv_p90": {r["population"]: r["npv_p90"] for r in central},
        "bcr_p50": {r["population"]: r["bcr_p50"] for r in central},
        "bcr_p10": {r["population"]: r["bcr_p10"] for r in central},
        "bcr_p90": {r["population"]: r["bcr_p90"] for r in central},
        "pvb_p50": {r["population"]: r["pvb_p50"] for r in central},
        "pvc_p50": {r["population"]: r["pvc_p50"] for r in central},
        "pvc_p90": {r["population"]: r["pvc_p90"] for r in central},
        "phase_sweep": sweep,
        "pv_wei_p50_indicative": {r["population"]: r["pv_wei_p50"] for r in central},
        "capex_sar_m": {
            k: sm[k] for k in ("capex_p10", "capex_p50", "capex_p90", "capex_base_p50")
        },
        "appraisal_rows": sm["rows"],
        "units": "SAR million, 2025 prices; PV at 2026 (A-cba-301); capex undiscounted, uplifted",
    }
    res |= demand_metrics(loads, root)
    if with_access:
        marker = Path(markers[-1]) if markers else None
        res["accessibility"] = accessibility(marker, root)
        res["access_gain_60"] = res["accessibility"]["gain_sum_over_metros"]["60"]
        res["access_gain_120"] = res["accessibility"]["gain_sum_over_metros"]["120"]
    res["seconds"] = round(time.monotonic() - t0, 1)
    (out / "score.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    return res


def demand_metrics(loads: dict[str, Any], root: Path) -> dict[str, Any]:
    """2050 medium: rail trips, passenger-km, ridership per route-km, HHR/Landbridge loads; CO2."""
    g = loads.get("un_wpp_medium-2050") or {}
    s1 = g.get("S1", {})
    by = g.get("by_line", {})
    s1by = s1.get("by_line", {})
    out = {
        "rail_trips_2050_medium": g.get("rail_trips"),
        "rail_pkm_m_2050_medium": g.get("rail_pkm_m"),
        "rail_trips_2050_medium_S1": s1.get("rail_trips"),
        "rail_pkm_m_2050_medium_S1": s1.get("rail_pkm_m"),
        "loads_2050_medium": {ln: by.get(ln) for ln in LOAD_LINES},
        "loads_2050_medium_S1": {ln: s1by.get(ln) for ln in LOAD_LINES},
        "by_line_2050_medium": by,
    }
    return out


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="R6 layout judge (run with R6_JUDGE_ROOT set)")
    ap.add_argument("cmd", choices=["evaluate", "zonepop"])
    ap.add_argument("--layout", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-access", action="store_true")
    ap.add_argument("--all-cases", action="store_true", help="3 horizons x 5 rate cases")
    ap.add_argument("--phase-sweep", action="store_true", help="single tranche at every phase")
    a = ap.parse_args()
    if a.cmd == "zonepop":  # zone populations behind the accessibility metric (fast mode union)
        from access import isochrones as iso

        a.out.mkdir(parents=True, exist_ok=True)
        iso.zones_table(jroot()).to_parquet(a.out / "zones_pop.parquet", index=False)
        return
    hz = (30, 40, 60) if a.all_cases else (60,)
    rc = (
        ("greenbook_2026", "tag_declining", "flat_5", "flat_7", "drawn")
        if a.all_cases
        else ("greenbook_2026",)
    )
    r = evaluate(
        a.layout, a.out, a.seed, a.draws, a.workers, not a.no_access, hz, rc, a.phase_sweep
    )
    print(
        json.dumps(
            {k: r.get(k) for k in ("feasible", "robust_npv", "capex_sar_m", "errors")},
            default=float,
        )
    )


if __name__ == "__main__":
    main()
