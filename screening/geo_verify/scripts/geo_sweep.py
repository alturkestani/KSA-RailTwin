"""Sensitivity sweep of extent parameters on the seed-1 back-test sample (cached tiles).

Run from the repo root after `backtest --seed 1`:
  uv run --with rasterio python -m screening.geo_verify.scripts.geo_sweep
Writes runs/geo_verify/backtest/sweep.csv (record-only; the estimators failed the 30 % gate).
"""

from __future__ import annotations

import itertools
import json

import pandas as pd

from common import REPO_ROOT
from screening.geo_verify import cli

BT = REPO_ROOT / "runs" / "geo_verify" / "backtest"


def main() -> None:
    cfg = cli._cfg()
    idx = cli._index(cfg)
    bt = pd.read_csv(BT / "backtest.csv")
    res = []
    for eps, ms, snap in itertools.product([100, 150, 200], [3, 5], [1500, 3000]):
        cfg2 = json.loads(json.dumps(cfg))
        cfg2["extent"]["eps_m"]["value"], cfg2["extent"]["min_samples"]["value"] = eps, ms
        cfg2["extent"]["snap_m"]["value"] = snap
        p = cli.params(cfg2)
        eg, eb, ratio = [], [], []
        for r in bt.itertuples():
            e = cli.estimate_one(r.lat, r.lon, cfg2, p, idx, [])
            eg.append(abs(e["grid"] - r.census_2022) / r.census_2022)
            eb.append(abs(e["buildings"] - r.census_2022) / r.census_2022)
            ratio.append(r.census_2022 / max(e["n_buildings"], 1))
        res.append(
            {
                "eps": eps,
                "min_samples": ms,
                "snap": snap,
                "mape_grid": pd.Series(eg).median(),
                "mape_bld": pd.Series(eb).median(),
                "census_per_building": pd.Series(ratio).median(),
            }
        )
        print(res[-1], flush=True)
    pd.DataFrame(res).to_csv(BT / "sweep.csv", index=False)


if __name__ == "__main__":
    main()
