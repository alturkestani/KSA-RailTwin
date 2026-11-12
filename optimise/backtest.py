"""R6 precondition 3: the judge back-test (run with R6_JUDGE_ROOT=judge/<name>).

A. The frozen R5 code alone: S0 at the 2025 calibration point (mode totals against
   runs/r5/demand/calibration-r5-s1/od/totals.json), the S1-vs-S0 demand inputs of every
   (population, year) group (against runs/cba/inputs) and the S1 committed-programme appraisal
   (against runs/cba/CBA-S1-committed-programme/results.json).
B. The layout adapter on the same judge: single-corridor layouts against their R5 cases.
Pass = every compared figure within 1 % (relative; absolute 1e-6 x scale for near-zero values).

  R6_JUDGE_ROOT=judge/v1-r5 .venv/bin/python optimise/backtest.py --ref-root . \
      --out runs/r6/judge-backtest

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import os
import sys

_J = os.path.abspath(os.environ["R6_JUDGE_ROOT"])
sys.path.insert(0, _J)
sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))

import argparse  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

TOL = 0.01
CHECK_CASES = ("S3-branch_spur-al-kharj", "S5-station_addition-al-jubayl")


def rel(a: float, b: float, scale: float = 1.0) -> float:
    if not np.isfinite(a) and not np.isfinite(b):
        return 0.0
    den = max(abs(b), 1e-6 * scale, 1e-12)
    return abs(a - b) / den


def part_a(root: Path, ref: Path, out: Path) -> list[dict]:
    from demand import gravity
    from economics import cba, demandruns

    rows = []
    ov = demandruns.overrides(root)
    cal = json.loads((ref / "runs/r5/demand/calibration-r5-s1/od/totals.json").read_text())
    r0 = gravity.run_model(
        gravity.RunConfig("S0", "un_wpp_medium_gastat2024", 2025, ov, {}, root, network="r4")
    )
    t0 = gravity.totals(r0)
    for m, v in cal["by_mode"].items():
        rows.append(
            {
                "test": "A1 S0 2025 trips by mode",
                "item": m,
                "judge": t0["by_mode"][m],
                "reference": v,
                "ref_file": "runs/r5/demand/calibration-r5-s1/od/totals.json",
            }
        )
    case = {
        "id": "CBA-S1-committed-programme",
        "baseline": "S0",
        "scenario_lines": "S1",
        "candidate_yaml": None,
    }
    inputs = out / "A-inputs"
    demandruns.run_all([case], root, inputs.resolve(), workers=4)
    for g in sorted((ref / "runs/cba/inputs").glob("*/scalars.parquet")):
        r = pd.read_parquet(g)
        r = r[r.case == case["id"]].iloc[0]
        j = pd.read_parquet(inputs / g.parent.name / "scalars.parquet").iloc[0]
        scale = max(abs(float(x)) for x in r.drop(["case", "population", "year"]))
        for col in r.index:
            if col in ("case", "population", "year"):
                continue
            rows.append(
                {
                    "test": "A2 S1 vs S0 demand inputs",
                    "item": f"{g.parent.name}:{col}",
                    "judge": float(j[col]),
                    "reference": float(r[col]),
                    "scale": scale,
                    "ref_file": f"runs/cba/inputs/{g.parent.name}/scalars.parquet",
                }
            )
    cy = yaml.safe_load((root / "cities/ksa/cba/CBA-S1-committed-programme.yaml").read_text())
    cy["demand_runs"] = str(inputs.resolve())
    cp = out / "A-case.yaml"
    cp.write_text(yaml.safe_dump(cy, sort_keys=False))
    res = cba.run_case(cp, 1, (out / "A-cba").resolve(), root)
    rref = json.loads((ref / "runs/cba/CBA-S1-committed-programme/results.json").read_text())
    rows += compare_results(res, rref, "A3 S1 programme appraisal", "CBA-S1-committed-programme")
    return rows


def compare_results(res: dict, rref: dict, test: str, cid: str) -> list[dict]:
    rows = []
    key = lambda r: (r["population"], r["horizon"], r["rate_case"])  # noqa: E731
    jm = {key(r): r for r in res["results"]}
    for r in rref["results"]:
        if r["horizon"] != 60 or r["rate_case"] != "greenbook_2026":
            continue
        j = jm[key(r)]
        for k in ("npv", "bcr", "pvb", "pvc"):
            for pq in ("P10", "P50", "P90"):
                rows.append(
                    {
                        "test": test,
                        "item": f"{r['population']}:60y:greenbook_2026:{k}:{pq}",
                        "judge": float(j[k][pq]) if j[k][pq] is not None else np.nan,
                        "reference": float(r[k][pq]) if r[k][pq] is not None else np.nan,
                        "scale": abs(float(r["pvc"]["P50"] or 1.0)),
                        "ref_file": f"runs/cba/{cid}/results.json",
                    }
                )
    return rows


def part_b(root: Path, ref: Path, out: Path) -> list[dict]:
    import layout as lay

    rows = []
    for cid in CHECK_CASES:
        lp = out / f"B-{cid}.yaml"
        lp.write_text(yaml.safe_dump({"id": f"backtest-{cid}", "corridors": [{"id": cid}]}))
        r = lay.evaluate(lp, (out / f"B-{cid}").resolve(), 1, 10000, 4, with_access=False)
        rref = json.loads((ref / f"runs/cba/CBA-{cid}/results.json").read_text())
        for x in rref["results"]:
            if x["horizon"] != 60 or x["rate_case"] != "greenbook_2026":
                continue
            pop = x["population"]
            row = next(
                a for a in r["appraisal_rows"] if a["population"] == pop and a["horizon"] == 60
            )
            for k, kk in (("npv", "npv"), ("bcr", "bcr"), ("pvc", "pvc")):
                for pq in ("P10", "P50", "P90"):
                    jk = f"{kk}_{pq.lower()}"
                    if jk not in row:
                        continue
                    rows.append(
                        {
                            "test": f"B adapter, single corridor {cid}",
                            "item": f"{pop}:60y:greenbook_2026:{k}:{pq}",
                            "judge": float(row[jk]),
                            "reference": float(x[k][pq]) if x[k][pq] is not None else np.nan,
                            "scale": abs(float(x["pvc"]["P50"] or 1.0)),
                            "ref_file": f"runs/cba/CBA-{cid}/results.json",
                        }
                    )
            rows.append(
                {
                    "test": f"B adapter, single corridor {cid}",
                    "item": f"{pop}:60y:greenbook_2026:pvb:P50",
                    "judge": float(row["pvb_p50"]),
                    "reference": float(x["pvb"]["P50"]),
                    "scale": abs(float(x["pvc"]["P50"] or 1.0)),
                    "ref_file": f"runs/cba/CBA-{cid}/results.json",
                }
            )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--parts", default="AB")
    a = ap.parse_args()
    root = Path(_J)
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for part, fn in (("A", part_a), ("B", part_b)):
        if part in a.parts:
            pd.DataFrame(fn(root, a.ref_root.resolve(), out)).to_csv(
                out / f"rows-{part}.csv", index=False
            )
    df = pd.concat(
        [pd.read_csv(out / f"rows-{x}.csv") for x in "AB" if (out / f"rows-{x}.csv").exists()]
    )
    df["rel_diff"] = [
        rel(j, r, s if s == s else 1.0)
        for j, r, s in zip(df.judge, df.reference, df.get("scale", 1.0), strict=True)
    ]
    df["pass"] = df.rel_diff <= TOL
    df.to_csv(out / "backtest.csv", index=False)
    s = df.groupby("test").agg(
        n=("pass", "size"), passed=("pass", "sum"), max_rel=("rel_diff", "max")
    )
    print(s.to_string())
    print("ALL PASS" if df["pass"].all() else "FAIL")


if __name__ == "__main__":
    main()
