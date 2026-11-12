"""STUDY_RJ_SCORE: the frozen judge v3 scoring one Riyadh-Jeddah replacement package.

A package is S1* plus one study sketch, where S1* = S1 without the committed Landbridge (existing
lines + Riyadh Rail Link + the Saudi GCC section). Run with the judge's files first on the import
path, as `optimise/layout.py` and `optimise/reach.py` are run (this file is harness; the judge's
functions are called unchanged and nothing under judge/ is written):

  R6_JUDGE_ROOT=judge/v3-variants STUDY_RJ_MARKER=runs/study/rj/score/<id>/inputs/marker.yaml \
      .venv/bin/python study/rj_judge.py evaluate --layout ... --out ... --all-cases

The wrappers apply ONLY when STUDY_RJ_MARKER names a file with a `study_rj_replace:` block (the
study replacement marker). Without it this module patches nothing, so S1, the R6 top-5 and L1-L6
are scored exactly as before (`optimise.layout`'s default "S1 + items" is untouched). With it:
- `access.railgraph.scenario_lines`: the line set "S1" omits the lines in `omit_lines`
  (landbridge), so the judge's own S1 reference run is S1* and every increment is versus S1*;
- `optimise.layout.corridor_path` / `FAMILY_DIRS` / `cost_refs_for`: the sketch id resolves to the
  scoring corridor written by `study.rj score-inputs` (routed chainage and curve limits from the
  study sidecar and profile) and to its cost run (the judge's `costs.estimate` on the study spec);
  it is appraised as a line corridor (family trunk_gap, as every R5/R6 line corridor);
- `access.railgraph.STATION_SKIMS`: the frozen station skims plus rows for the two study stops that
  have none (gateway SW/NW), computed with the judge's own skim method (`skims` below).

The wrappers are installed at import, so the judge's spawned demand workers (which re-import this
file as their main module) carry them too.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import os
import sys

_J = os.path.abspath(os.environ["R6_JUDGE_ROOT"])
if _J not in sys.path:
    sys.path.insert(0, _J)

import argparse  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

import yaml  # noqa: E402

LABEL = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
MARKER_KEY = "study_rj_replace"


def load_marker(path: str | Path) -> dict | None:
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return d.get(MARKER_KEY) if isinstance(d, dict) else None


def install(m: dict) -> None:
    """Install the study wrappers for one replacement marker (see the module docstring)."""
    from access import railgraph
    from optimise import layout as L

    omit = set(m["omit_lines"])
    sid = m["sketch_id"]
    corridor = Path(m["corridor"])
    cost = dict(m["cost"])
    orig_lines = railgraph.scenario_lines

    def scenario_lines(scenario, cfg, root=railgraph.REPO_ROOT, candidate=None):
        lines = orig_lines(scenario, cfg, root, candidate)
        if scenario == "S1":
            lines = [ld for ld in lines if ld["id"] not in omit]
        return lines

    railgraph.scenario_lines = scenario_lines
    if m.get("skims"):
        railgraph.STATION_SKIMS = Path(m["skims"])
    orig_path = L.corridor_path
    L.corridor_path = lambda cid, root: corridor if cid == sid else orig_path(cid, root)
    L.FAMILY_DIRS = {**L.FAMILY_DIRS, sid.split("-")[0]: "trunk_gap"}
    orig_cost = L.cost_refs_for
    L.cost_refs_for = lambda item, root, out, seed: (
        dict(cost) if item["id"] == sid else orig_cost(item, root, out, seed)
    )


_M = os.environ.get("STUDY_RJ_MARKER")
MARKER = load_marker(_M) if _M else None
if MARKER:
    install(MARKER)


def skims(stations: Path, out: Path, check_keys: list[str]) -> None:
    """Rows of the R4 station skims for stops that have none, by the judge's own method
    (`access.railgraph skims`: OSRM /table, MLD, car, free flow, zone points of demand.supply).
    The frozen table is copied unchanged and the new rows appended; `check_keys` (stations that
    already have a skim) are recomputed and must match the frozen rows exactly."""
    import numpy as np
    import pandas as pd

    from access import railgraph
    from demand.supply import zone_points
    from network import osrm as osrm_mod

    root = Path(_J)
    frozen = pd.read_parquet(root / railgraph.STATION_SKIMS / "zone_station.parquet")
    pts = json.loads(stations.read_text())
    need = sorted({k for k in pts if k not in set(frozen.key)})
    keys = need + list(check_keys)
    z = zone_points(root)
    sl = np.array([[pts[k]["lon"], pts[k]["lat"]] for k in keys], dtype=float)
    zl = z[["lon", "lat"]].to_numpy()
    with osrm_mod.server(root / railgraph.OSRM_DIR, max_table=1000) as url:
        zs = osrm_mod.table(url, zl, sl, batch=100)
        sz = osrm_mod.table(url, sl, zl, batch=100)
    n, m = len(z), len(keys)
    df = pd.DataFrame(
        {
            "zone_id": np.repeat(z.zone_id.to_numpy(), m),
            "key": np.tile(np.array(keys), n),
            "to_min": (zs["duration_s"] / 60).ravel().round(2),
            "to_km": (zs["distance_m"] / 1000).ravel().round(3),
            "from_min": (sz["duration_s"].T / 60).ravel().round(2),
            "from_km": (sz["distance_m"].T / 1000).ravel().round(3),
        }
    )
    chk = df[df.key.isin(check_keys)].merge(
        frozen[frozen.key.isin(check_keys)], on=["zone_id", "key"], suffixes=("", "_frozen")
    )
    diffs = {
        c: float(np.nanmax(np.abs(chk[c] - chk[f"{c}_frozen"])))
        for c in ("to_min", "to_km", "from_min", "from_km")
    }
    if len(chk) != n * len(check_keys) or any(v > 0 for v in diffs.values()):
        raise SystemExit(f"skim check failed: {len(chk)} rows, max abs diff {diffs}")
    new = df[df.key.isin(need)]
    out.mkdir(parents=True, exist_ok=True)
    pd.concat([frozen, new], ignore_index=True).to_parquet(
        out / "zone_station.parquet", index=False
    )
    (out / "skims.json").write_text(
        json.dumps(
            {
                "label": LABEL,
                "method": "access.railgraph skims (judge v3 copy): OSRM /table MLD car, free flow",
                "frozen_rows": len(frozen),
                "added_keys": need,
                "added_rows": len(new),
                "unreachable_added": int(new.to_min.isna().sum()),
                "check_keys": list(check_keys),
                "check_max_abs_diff": diffs,
                "osrm_version": osrm_mod.osrm_version(),
            },
            indent=1,
        )
        + "\n"
    )
    print(json.dumps({"added": need, "check_max_abs_diff": diffs}))


def main() -> None:
    ap = argparse.ArgumentParser(description="STUDY_RJ_SCORE judge entry (see module docstring)")
    ap.add_argument("cmd", choices=["evaluate", "reach", "skims"])
    ap.add_argument("--layout", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--stations", type=Path)
    ap.add_argument("--check-keys", default="")
    ap.add_argument("--reach-script", type=Path)
    a, rest = ap.parse_known_args()
    if a.cmd == "skims":
        skims(a.stations, a.out, [k for k in a.check_keys.split(";") if k])
        return
    if not MARKER:
        raise SystemExit("STUDY_RJ_MARKER with a study_rj_replace block is required")
    if a.cmd == "evaluate":
        from optimise import layout as L

        sys.argv = ["layout.py", "evaluate", "--layout", str(a.layout), "--out", str(a.out), *rest]
        L.main()
    else:  # national reach (reported only, A-r6-104) by the R6_V3 harness script, unchanged
        import runpy

        sys.argv = ["reach.py", "--layouts", str(a.layout), "--out", str(a.out)]
        runpy.run_path(str(a.reach_script), run_name="__main__")


if __name__ == "__main__":
    main()
