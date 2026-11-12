"""R6_V3 national reach column (CP7-5, A-r6-104): reported only, never part of the score.

The 2025 population (un_wpp_medium_gastat2024, the R4 isochrone base) of the zones within 60 and
120 door-to-station minutes of ANY station of the network (S1 existing + committed lines and the
layout's corridors, variants applied), nationally. A zone is reached in band b when
(road minutes to its nearest such station + terminal minutes) x summer factor <= b
(A-demand-046, A-access-011). The judge's 90-min station access cap (A-demand-045) is NOT applied:
with it the 120-min band would equal "road <= 90 min"; the cap-limited figure is reported beside
it. Stations of connector-only lines are not boarding points (A-r4-acc-005), as in
`access.isochrones`. Road minutes come from the existing station skims
(`runs/skims/r4-stations/zone_station.parquet`); nothing is re-routed.

Run with the judge's files on the path (the judge's functions, unchanged; this file is harness):

  R6_JUDGE_ROOT=judge/v3-variants .venv/bin/python optimise/reach.py \
      --layouts a.yaml,b.yaml --out runs/r6/v3/reach.json

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import os
import sys

_J = os.path.abspath(os.environ["R6_JUDGE_ROOT"])
sys.path.insert(0, _J)

import argparse  # noqa: E402
import json  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

LABEL = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
BANDS = (60, 120)


def _v(node):
    return node["value"] if isinstance(node, dict) and "value" in node else node


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layouts", required=True, help="comma-separated layout YAMLs")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    root = Path(_J)
    from access import isochrones as iso
    from access import railgraph
    from optimise import layout as lay

    lay.patch_railgraph()
    cfg = railgraph.load_cfg(root)
    sup = yaml.safe_load((root / railgraph.SUPPLY).read_text(encoding="utf-8"))
    term = float(_v(sup["rail"]["terminal_min"]))
    cap = float(_v(sup["rail"]["station_access"]["max_road_min"]))
    summer = iso.summer_factor(root)
    conn = set(_v(cfg.get("connector_lines", {"value": []})))
    zs = pd.read_parquet(root / railgraph.STATION_SKIMS / "zone_station.parquet")
    zones = iso.zones_table(root)[["zone_id", "population"]]
    total = float(zones.population.sum())

    def keys(marker: Path | None) -> set[str]:
        pts = [
            (float(s["lat"]), float(s["lon"]))
            for ld in railgraph.scenario_lines("S1", cfg, root, marker)
            if ld["id"] not in conn
            for s in ld["stations"]
        ]
        st = pd.DataFrame(pts, columns=["lat", "lon"])  # keys as railgraph.zone_station_times
        out = set(st.lat.round(5).astype(str) + "," + st.lon.round(5).astype(str))
        miss = out - set(zs.key)
        if miss:
            raise KeyError(f"{len(miss)} stations without a skim: {sorted(miss)[:5]}")
        return out

    def reach(ks: set[str]) -> dict[str, float]:
        acc = zs[zs.key.isin(ks)].groupby("zone_id").to_min.min()
        z = zones.assign(acc=zones.zone_id.map(acc))
        d2s = (z.acc + term) * summer
        out = {str(b): float(z.population[d2s <= b].sum()) for b in BANDS}
        out["120_within_access_cap"] = float(z.population[(d2s <= 120) & (z.acc <= cap)].sum())
        return out | {"n_stations": len(ks)}

    s1 = reach(keys(None))
    res = {
        "label": LABEL,
        "note": "national reach: reported column only, never in the score (CP7-5, A-r6-104)",
        "population_total_2025": total,
        "terminal_min": term,
        "access_cap_min": cap,
        "summer_factor": summer,
        "S1": s1,
        "layouts": {},
    }
    with tempfile.TemporaryDirectory() as td:
        for p in filter(None, a.layouts.split(",")):
            d = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
            items = [dict(c) for c in d.get("corridors", [])]
            m = lay.write_marker(items, Path(td) / "m.yaml")
            r = reach(keys(m) if items else keys(None))
            res["layouts"][p] = {
                "layout": r,
                "gain": {str(b): r[str(b)] - s1[str(b)] for b in BANDS},
            }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"S1": s1, "n": len(res["layouts"])}))


if __name__ == "__main__":
    main()
