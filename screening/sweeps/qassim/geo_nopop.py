# Document version: screening/sweeps/qassim/geo_nopop.py v1.0 | 31 Oct 2026 |
# Author: region-scout (REGION_QASSIM) | Status: draft
"""GEO_VERIFY no-pop step for the Qassim register (region-sweep skill, geo-verify step).

`screening.geo_verify.cli estimate` globs `cities/ksa/regions/pilot-*.parquet` only, so it cannot
see `qassim.parquet`. This wrapper points that module at the R2 register for one call and leaves
the estimator itself unchanged (the back-test gate and the record-only rule still apply: the
values go in notes, never in `population`).

Run: `uv run --with rasterio python -m screening.sweeps.qassim.geo_nopop`
"""

from __future__ import annotations

from screening.geo_verify import cli

REGISTER_GLOB = "cities/ksa/regions/qassim.parquet"


def main() -> None:
    cli.REGISTERS = REGISTER_GLOB
    cli.estimate(
        seed=1,
        which="no-pop",
        limit=0,
        region="qassim",
        backtest_dir=cli.RUNS / "backtest",
        run_dir=cli.RUNS / "estimate",
        params_file=cli.PARAMS,
    )


if __name__ == "__main__":
    main()
