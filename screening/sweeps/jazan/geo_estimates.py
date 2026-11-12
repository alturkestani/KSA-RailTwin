# ruff: noqa: E501  (R2 merge: sweep script kept as written by the Jazan sweep)
"""REGION_JAZAN geo-verify estimates for unsourced and relayed rows (record only).

`screening.geo_verify.cli estimate` reads only cities/ksa/regions/pilot-*.parquet, so it cannot reach
the R2 register. This driver calls the same `estimate_one` (WorldPop grid + building footprints x
occupancy, DBSCAN extent) with the same parameters, back-test summary and method-log ids, for the
rows that are unverified (WorldPop gap-fill), relayed or unpopulated. The back-test gate fails
(docs/geo-verify.md section 3), so the values go to notes only and never into `population`.

Run:  PYTHONPATH=. .venv/bin/python screening/sweeps/jazan/geo_estimates.py
Outputs (gitignored): runs/geo_verify/estimate-r2-jazan/{estimates-r2.csv, method_log-r2.jsonl, meta.json}
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from common.runmeta import rng, write_meta
from screening.geo_verify import cli as gv
from screening.geo_verify import estimators, method_log

REPO = Path(__file__).resolve().parents[3]
REGISTER_REL = "cities/ksa/regions/jazan.parquet"
BACKTEST = REPO.parents[1] / "runs/geo_verify/backtest/summary.json"  # main checkout (read only)
RUN = REPO / "runs/geo_verify/estimate-r2-jazan"
SEED = 1


def main() -> None:
    rng(SEED)
    cfg = gv._cfg(gv.PARAMS)
    p = gv.params(cfg)
    idx = gv._index(cfg)
    bt = json.loads(BACKTEST.read_text())
    err, may = bt["median_ape"], bt["may_rank"]

    reg = pd.read_parquet(REPO / REGISTER_REL)
    sel = reg[reg.population.isna() | reg.pop_source_status.isin(["unverified", "secondary"])]
    RUN.mkdir(parents=True, exist_ok=True)
    log = RUN / "method_log-r2.jsonl"
    log.unlink(missing_ok=True)
    rows, dl = [], []
    for i, r in sel.iterrows():
        est = gv.estimate_one(r.lat, r.lon, cfg, p, idx, dl)
        lo, mid, hi = estimators.band(
            [est["grid"], est["buildings"]], [err["grid"], err["buildings"]]
        )
        mid_id = method_log.entry_id("est", f"{REGISTER_REL}:{i}")
        method_log.append(
            log,
            {
                "id": mid_id,
                "method": "grid (WorldPop) + buildings x occupancy over DBSCAN extent",
                "inputs": [
                    "worldpop-sau-2020-100m-unadj-constrained",
                    "msbuildings-ksa-2026-02-03",
                ],
                "parameters": [f"A-geo-00{k}" for k in range(1, 10)],
                "value": {"grid": est["grid"], "buildings": est["buildings"], "central": mid},
                "band": [lo, hi],
                "backtest_median_ape": err,
                "may_rank": may,
                "run_id": str(RUN.relative_to(REPO)),
                "target": r.name_en,
                "extent_bbox": est["extent_bbox"],
                "extent_km2": est["extent_km2"],
                "n_buildings": est["n_buildings"],
            },
        )
        rows.append(
            {
                "row_in_file": i,
                "osm_id": r.osm_id,
                "name_en": r.name_en,
                "governorate": r.governorate,
                "population": r.population,
                "pop_type": r.pop_type,
                "grid": est["grid"],
                "buildings": est["buildings"],
                "est_low": lo,
                "est_central": mid,
                "est_high": hi,
                "n_buildings": est["n_buildings"],
                "method_log_id": mid_id,
            }
        )
        print(
            f"{r.name_en}: grid {est['grid']:.0f} buildings {est['buildings']:.0f} n={est['n_buildings']}"
        )
    df = pd.DataFrame(rows)
    df.to_csv(RUN / "estimates-r2.csv", index=False)
    (RUN / "downloads-r2.json").write_text(json.dumps(dl, indent=2) + "\n")
    write_meta(RUN, SEED, cfg, {"which": "r2-jazan", "backtest": err, "rows": len(df)})
    print(f"estimated {len(df)} rows; downloads {len(dl)}")


if __name__ == "__main__":
    main()
