"""STUDY_EXTRA_TRAVEL: the frozen judge v1-r5 (the code behind the published S1-vs-S0 CBA,
runs/cba/CBA-S1-committed-programme) run on the study path. Run with the judge's files first on the
import path, as `study/rj_judge.py` is run (this file is harness; the judge's functions are called
unchanged and nothing under judge/ is written):

  R6_JUDGE_ROOT=judge/v1-r5 .venv/bin/python study/extra_travel_judge.py <command> --out <dir>

Commands (all outputs under the --out directory, which the study CLI sets under
runs/study/extra-travel/):
- `baseline`: the Riyadh-Jeddah pair under S1 (and S0), 2050 UN WPP medium, by mode and purpose;
- `induced`: the induced-demand sensitivity. In-process wrappers only: `demand.gravity.run_model`
  is memoised (S0 and S1 are run once per group) and `economics.benefits.extract` receives the
  scenario OD tables of tourism, leisure_vfr and business scaled by (C1/C0)**e against the
  baseline's composite cost; then the judge's own `demandruns.run_group` writes the CBA inputs of
  each elasticity case. e = 0 must reproduce the published scalars exactly;
- `cba`: the judge's own `economics.cba.run_case` on one case directory (S1 vs S0 case file with
  `demand_runs` pointed at the study inputs);
- `land`: rail paths from the land-entry border zones to the holy-city zones under S0 and S1.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Not the official
ranking.
"""

from __future__ import annotations

import os
import sys

_J = os.path.abspath(os.environ["R6_JUDGE_ROOT"])
if _J not in sys.path:
    sys.path.insert(0, _J)

import argparse  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("extra_travel_core", _HERE / "extra_travel_core.py")
core = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(core)

CONFIG = _HERE.parent / "cities/ksa/assumptions/extra_travel_study.yaml"
CASE = "CBA-S1-committed-programme"


def cfg() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def _root() -> Path:
    from common import REPO_ROOT

    assert Path(REPO_ROOT).resolve() == Path(_J).resolve(), "judge root not first on the path"
    return Path(REPO_ROOT)


def _run(scenario: str, pop: str, year: int):
    from demand import gravity
    from economics import demandruns as dr

    root = _root()
    ov = dr.overrides(root)
    c = gravity.RunConfig(scenario, pop, year, ov, {}, root, network="r4")
    return gravity.run_model(c)


# --------------------------------------------------------------------------- baseline (item 2)
def baseline(out: Path) -> dict:
    from demand import gravity

    root = _root()
    c = cfg()["rj_pair"]
    pop, year = c["population"], int(c["year"])
    zones = gravity.zone_population(year, pop, root)
    ra = set(zones.loc[zones.metro.eq(c["metros"][0]), "zone_id"])
    je = set(zones.loc[zones.metro.eq(c["metros"][1]), "zone_id"])
    res = {}
    for s in ("S0", "S1"):
        r = _run(s, pop, year)
        ex = core.pair_extract(r["od"], ra, je)
        los = core.pair_rows(r["los"], ra, je)
        rail = pd.concat([core.pair_rows(d, ra, je) for d in r["od"].values()])
        rail = rail[rail.trips_rail > 0].merge(
            los[["o", "d", "cost_sar_rail"]], on=["o", "d"], how="left"
        )
        w = rail.trips_rail
        ex["rail_fare_sar_trip_weighted"] = (
            float((w * rail.cost_sar_rail).sum() / w.sum()) if w.sum() > 0 else None
        )
        # level of service on the pair, weighted by each mode's own trips (frozen LOS inputs)
        allp = pd.concat([core.pair_rows(d, ra, je) for d in r["od"].values()])
        allp = allp[["o", "d", "trips_rail", "trips_air"]].merge(
            los.drop(columns=[c for c in ("trips_rail", "trips_air") if c in los]),
            on=["o", "d"],
            how="left",
        )
        lv = {}
        for m in ("rail", "air"):
            wm = allp[f"trips_{m}"]
            if wm.sum() <= 0:
                continue
            for col in ("cost_sar", "ivt_min", "access_min", "egress_min", "headway_min"):
                lv[f"{col}_{m}"] = float((wm * allp[f"{col}_{m}"]).sum() / wm.sum())
        ex["los_trip_weighted"] = lv
        ex["national_trips_total"] = float(sum(d.trips.sum() for d in r["od"].values()))
        ex["los_columns"] = sorted(r["los"].columns)
        res[s] = ex
    # the induced sensitivity restricted to this pair (S1 vs S0; same rule as `induced`)
    b0, b1 = _run("S0", pop, year), _run("S1", pop, year)
    ic = cfg()["induced"]
    induced_pair = {}
    for name, eps in ic["elasticity_cases"].items():
        alloc = "rail_only" if name.endswith("_rail_only") else "proportional"
        od = {
            pu: core.induce_od(b0["od"][pu], b1["od"][pu], float(eps), alloc)
            if pu in ic["purposes"]
            else b1["od"][pu]
            for pu in b1["od"]
        }
        ex = core.pair_extract(od, ra, je)
        induced_pair[name] = {
            "elasticity": float(eps),
            "allocation": alloc,
            "extra": core.diff_extract(res["S1"]["total"], ex["total"]),
        }
    doc = {
        "label": core.LABEL,
        "official_ranking": False,
        "induced_on_pair": induced_pair,
        "pair": f"every {c['metros'][0]}-metro zone x every {c['metros'][1]}-metro zone, "
        "both directions, all five purposes (A-xt-001)",
        "zones": {c["metros"][0]: sorted(ra), c["metros"][1]: sorted(je)},
        "population": pop,
        "year": year,
        "judge": "v1-r5",
        "runs": res,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "rj_baseline.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    return doc


# --------------------------------------------------------------------------- induced (item 3)
DIAG: dict[str, dict] = {}
_STATE: dict[str, object] = {"eps": 0.0, "group": "", "alloc": "proportional"}


def install_induced(purposes: list[str]) -> None:
    from demand import gravity
    from economics import benefits

    cache: dict[tuple, dict] = {}
    orig_run = gravity.run_model

    def run_model(c, los=None):
        if los is not None:
            return orig_run(c, los)
        k = (c.scenario, c.population, c.year, c.candidate, tuple(sorted(c.rate_scale.items())))
        if k not in cache:
            cache[k] = orig_run(c)
        return cache[k]

    gravity.run_model = run_model
    orig_extract = benefits.extract

    def extract(base, scen, zones, p, jz, b_ivt_car=0.010, asc=None):
        eps = float(_STATE["eps"])
        od = dict(scen["od"])
        diag = {}
        for pu in purposes:
            new = core.induce_od(base["od"][pu], scen["od"][pu], eps, str(_STATE["alloc"]))
            diag[pu] = core.diff_extract(
                core.trips_pkm_by_mode(scen["od"][pu]), core.trips_pkm_by_mode(new)
            )
            od[pu] = new
        allp = pd.concat(list(scen["od"].values()), ignore_index=True)
        diag["_scenario_all_purposes"] = core.trips_pkm_by_mode(allp)
        diag["_baseline_all_purposes"] = core.trips_pkm_by_mode(
            pd.concat(list(base["od"].values()), ignore_index=True)
        )
        DIAG[str(_STATE["group"])] = diag
        s2 = {**scen, "od": od}
        return orig_extract(base, s2, zones, p, jz, b_ivt_car, asc)

    benefits.extract = extract


def induced(out: Path, cases: dict[str, float]) -> dict:
    from economics import demandruns as dr

    root = _root()
    c = cfg()["induced"]
    install_induced(list(c["purposes"]))
    summary: dict[str, dict] = {}
    for name, eps in cases.items():
        d = out / name
        DIAG.clear()
        _STATE["alloc"] = "rail_only" if name.endswith("_rail_only") else "proportional"
        for pop, year in dr.groups():
            _STATE["eps"], _STATE["group"] = eps, dr.group_id(pop, year)
            case = [{"id": CASE, "baseline": "S0", "scenario_lines": "S1"}]
            dr.run_group(pop, year, case, root, (d / "inputs").resolve())
        (d / "induced_diag.json").write_text(
            json.dumps({"elasticity": eps, "allocation": _STATE["alloc"], "groups": DIAG}, indent=1)
            + "\n",
            encoding="utf-8",
        )
        summary[name] = {"elasticity": eps, "groups": sorted(DIAG)}
    return summary


def cba(case_dir: Path, seed: int) -> dict:
    from economics import cba as cb

    root = _root()
    case = yaml.safe_load((root / "cities/ksa/cba" / f"{CASE}.yaml").read_text(encoding="utf-8"))
    case["demand_runs"] = str((case_dir / "inputs").resolve())
    cp = case_dir / "case.yaml"
    cp.write_text(yaml.safe_dump(case, sort_keys=False), encoding="utf-8")
    res = cb.run_case(cp.resolve(), seed, (case_dir / "cba").resolve(), root)
    return {"case": res["case"], "rows": len(res["results"])}


# --------------------------------------------------------------------------- land (item 4)
def land(out: Path) -> dict:
    from access import railgraph
    from demand import intl

    root = _root()
    lp = cfg()["land_ports"]
    rows = []
    for y in lp["bulletins_ah"]:
        t = intl.port_table(y, root)
        t = t[t.port.str.lower() != "total"].assign(year_ah=y)
        rows.append(t)
    t = pd.concat(rows, ignore_index=True)
    seg = yaml.safe_load((root / intl.SEGMENT).read_text(encoding="utf-8"))
    p2a = seg["port_to_airport"]

    def is_land(p: str) -> bool:
        low = p.lower()
        return p2a.get(p) is None and not any(
            s in low for s in ("islamic port", "commercial port", "airport", "air base")
        )

    land_rows = t[t.port.map(is_land)]
    groups = lp["groups"]
    mix = core.port_mix(land_rows[["port", "total"]], groups)
    zone_of = {p: z for spec in groups.values() for p, z in spec["ports"].items()}
    by_zone: dict[str, float] = {}
    for r in land_rows.itertuples(index=False):
        by_zone[zone_of[r.port]] = by_zone.get(zone_of[r.port], 0.0) + float(r.total)
    hz = intl.holy_zones(root)
    pairs = pd.DataFrame(
        [{"o": z, "d": hz[c]} for z in sorted(by_zone) for c in ("makkah", "madinah")]
    )
    from demand import gravity

    road = pd.read_parquet(root / gravity.SKIMS / "road.parquet")
    road = pairs.merge(road.rename(columns={"km": "road_km"})[["o", "d", "road_km"]], how="left")
    road_km = {f"{r.o}|{r.d}": float(r.road_km) for r in road.itertuples(index=False)}
    paths = {}
    for s in ("S0", "S1"):
        los = railgraph.rail_los(pairs, s, root)
        paths[s] = [
            {
                "o": r.o,
                "d": r.d,
                "avail_rail": bool(r.avail_rail) if pd.notna(r.avail_rail) else False,
                "rail_path": r.rail_path if isinstance(r.rail_path, str) else None,
                "rail_km": float(r.rail_km) if "rail_km" in los and pd.notna(r.rail_km) else None,
            }
            for r in los.itertuples(index=False)
        ]
    um = intl.umrah_2025(root)
    hj = intl.hajj_2025(root)
    sp = intl.airport_split(2025, root)
    doc = {
        "label": core.LABEL,
        "official_ranking": False,
        "judge": "v1-r5",
        "bulletins_ah": lp["bulletins_ah"],
        "land_ports": land_rows[["year_ah", "port", "total"]].to_dict(orient="records"),
        "port_mix": mix,
        "persons_by_zone": by_zone,
        "holy_zones": hz,
        "road_km": road_km,
        "rail_paths": paths,
        "umrah_2025_total": float(um["total"]),
        "hajj_2025_by_mode": hj["by_mode"],
        "frozen_split_shares": sp["shares"],
        "frozen_split_range": sp["range"],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "land_inputs.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    return {k: doc[k] for k in ("port_mix", "persons_by_zone", "holy_zones")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["baseline", "induced", "cba", "land"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases", default="")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    out = Path(a.out)
    if a.command == "baseline":
        r = baseline(out)
        print(json.dumps({s: r["runs"][s]["total"] for s in r["runs"]}))
    elif a.command == "induced":
        cases = {k: float(v) for k, v in (x.split("=") for x in a.cases.split(",") if x)}
        print(json.dumps(induced(out, cases)))
    elif a.command == "cba":
        print(json.dumps(cba(out, a.seed)))
    else:
        print(json.dumps(land(out)))


if __name__ == "__main__":
    main()
