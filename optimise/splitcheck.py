"""R6 CP6 P5b check: S0 at the 2025 calibration point under judge v1 (R5 zones) and v2 (split
zones), with the R5 fitted constants held (A-r6-011): mode totals and rail line totals.

  R6_JUDGE_ROOT=judge/v2-p5b .venv/bin/python optimise/splitcheck.py --out runs/r6/p5b

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.environ["R6_JUDGE_ROOT"]))

import argparse  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402


def main() -> None:
    from demand import gravity
    from economics import demandruns

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    root = Path(os.environ["R6_JUDGE_ROOT"]).resolve()
    ov = demandruns.overrides(root)
    r = gravity.run_model(
        gravity.RunConfig("S0", "un_wpp_medium_gastat2024", 2025, ov, {}, root, network="r4")
    )
    t = gravity.totals(r)
    a.out.mkdir(parents=True, exist_ok=True)
    keep = {k: t[k] for k in ("by_mode", "rail_by_line", "population")}
    keep["zones"] = int(len(r["zones"]))
    keep["label"] = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
    name = Path(os.environ["R6_JUDGE_ROOT"]).name
    (a.out / f"S0-2025-{name}.json").write_text(json.dumps(keep, indent=1) + "\n")
    print(json.dumps(keep["by_mode"]), keep["zones"])


if __name__ == "__main__":
    main()
