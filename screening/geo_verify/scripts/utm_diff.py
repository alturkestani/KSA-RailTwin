"""CP2_PREP item 3: before/after diff of the record-only GEO_VERIFY outputs around the UTM fix.

Run from the repo root after snapshotting the old outputs to runs/cp2_prep/item3/before/ and
re-running backtest, the sweep, estimate (no-pop, secondary), seat (into
runs/cp2_prep/item3/after/seat) and validate-geocodes:
  uv run python -m screening.geo_verify.scripts.utm_diff
Writes runs/cp2_prep/item3/utm-diff.csv (one row per dataset x key x field) and prints a summary.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Proj

from common import REPO_ROOT
from screening.geo_verify import cli
from screening.geo_verify.geom import utm_epsg

ITEM = REPO_ROOT / "runs" / "cp2_prep" / "item3"
BEFORE, AFTER = ITEM / "before", REPO_ROOT / "runs" / "geo_verify"
EST_FIELDS = [
    "n_buildings",
    "grid",
    "buildings",
    "est_low",
    "est_central",
    "est_high",
    "extent_km2",
    "divergence",
]
BT_FIELDS = ["n_buildings", "grid", "buildings", "extent_km2", "ape_grid", "ape_buildings"]


def old_epsg(lon: float) -> int:
    """The pre-fix mapping (one zone east of EPSG), kept only to label the diff."""
    return 32637 if lon < 36.0 else 32638 if lon < 42.0 else 32639


def scale_ratio(lat: float, lon: float) -> float:
    """Linear scale factor old zone / new zone - 1 at the point."""
    kb = Proj(f"EPSG:{old_epsg(lon)}").get_factors(lon, lat).meridional_scale
    ka = Proj(f"EPSG:{utm_epsg(lon)}").get_factors(lon, lat).meridional_scale
    return kb / ka - 1.0


def _seat(path: Path) -> dict[str, dict]:
    vals = [json.loads(line)["value"] for line in path.read_text().splitlines() if line]
    return {v["label"]: v for v in vals if isinstance(v, dict) and "label" in v}


def build() -> pd.DataFrame:
    reg = cli.register().set_index(["register_file", "row_in_file"])[["lat", "lon"]]
    out: list[dict] = []
    for w in ["no-pop", "secondary"]:
        b = pd.read_csv(BEFORE / f"estimate/{w}/estimates-{w}.csv")
        a = pd.read_csv(AFTER / f"estimate/{w}/estimates-{w}.csv")
        m = b.merge(a, on=["register_file", "row_in_file"], suffixes=("_b", "_a"))
        assert len(m) == len(a) == len(b)
        for r in m.itertuples():
            lat, lon = reg.loc[(r.register_file, r.row_in_file)]
            base = {
                "dataset": f"estimate/{w}",
                "key": f"{r.register_file}:{r.row_in_file}",
                "name": r.name_en_b,
                "lat": lat,
                "lon": lon,
                "epsg_before": old_epsg(lon),
                "epsg_after": utm_epsg(lon),
                "scale_old_over_new_minus_1": scale_ratio(lat, lon),
            }
            for f in EST_FIELDS:
                vb, va = getattr(r, f + "_b"), getattr(r, f + "_a")
                out.append(base | {"field": f, "before": vb, "after": va})
    b = pd.read_csv(BEFORE / "backtest/backtest.csv")
    a = pd.read_csv(AFTER / "backtest/backtest.csv")
    for rb, ra in zip(b.itertuples(), a.itertuples(), strict=True):
        assert rb.name_en == ra.name_en
        base = {
            "dataset": "backtest",
            "key": rb.stratum,
            "name": rb.name_en,
            "lat": rb.lat,
            "lon": rb.lon,
            "epsg_before": old_epsg(rb.lon),
            "epsg_after": utm_epsg(rb.lon),
            "scale_old_over_new_minus_1": scale_ratio(rb.lat, rb.lon),
        }
        for f in BT_FIELDS:
            out.append(base | {"field": f, "before": getattr(rb, f), "after": getattr(ra, f)})
    sb = json.loads((BEFORE / "backtest/summary.json").read_text())
    sa = json.loads((AFTER / "backtest/summary.json").read_text())
    for k in ["grid", "buildings"]:
        for f in ["median_ape", "may_rank"]:
            out.append(
                {
                    "dataset": "backtest-summary",
                    "key": f,
                    "name": k,
                    "field": f,
                    "before": sb[f][k],
                    "after": sa[f][k],
                }
            )
    b = pd.read_csv(BEFORE / "backtest/sweep.csv")
    a = pd.read_csv(AFTER / "backtest/sweep.csv")
    for rb, ra in zip(b.itertuples(), a.itertuples(), strict=True):
        for f in ["mape_grid", "mape_bld", "census_per_building"]:
            out.append(
                {
                    "dataset": "backtest-sweep",
                    "key": f"eps{rb.eps}-ms{rb.min_samples}-snap{rb.snap}",
                    "name": "",
                    "field": f,
                    "before": getattr(rb, f),
                    "after": getattr(ra, f),
                }
            )
    sb, sa = _seat(BEFORE / "seat/method_log.jsonl"), _seat(ITEM / "after/seat/method_log.jsonl")
    for k, v in sa.items():
        if k in sb:
            out.append(
                {
                    "dataset": "seat",
                    "key": k,
                    "name": k,
                    "lat": v["lat"],
                    "lon": v["lon"],
                    "epsg_before": sb[k]["epsg"],
                    "epsg_after": v["epsg"],
                    "field": "km_to_boundary",
                    "before": sb[k]["km_to_boundary"],
                    "after": v["km_to_boundary"],
                }
            )
    for fn in ["geocodes.csv", "raw_geocodes.csv"]:
        b = pd.read_csv(BEFORE / f"validate-geocodes/{fn}")
        a = pd.read_csv(AFTER / f"validate-geocodes/{fn}")
        kc = [c for c in b.columns if "km" in c]
        for i, (rb, ra) in enumerate(zip(b.to_dict("records"), a.to_dict("records"), strict=True)):
            for f in kc:
                out.append(
                    {
                        "dataset": f"validate-geocodes/{fn}",
                        "key": str(i),
                        "name": str(rb.get("name_en", rb.get("file", ""))),
                        "field": f,
                        "before": rb[f],
                        "after": ra[f],
                    }
                )
    d = pd.DataFrame(out)
    nb = pd.to_numeric(d.before, errors="coerce")
    na = pd.to_numeric(d.after, errors="coerce")
    d["abs_change"] = na - nb
    with np.errstate(divide="ignore", invalid="ignore"):
        d["rel_change"] = np.where(nb.abs() > 0, (na - nb) / nb.abs(), np.nan)
    same = (d.before.astype(str) == d.after.astype(str)) | ((nb - na).abs() < 1e-9)
    d["changed"] = ~(same | (nb.isna() & na.isna()))
    return d


def main() -> None:
    d = build()
    d.to_csv(ITEM / "utm-diff.csv", index=False)
    print(d.groupby("dataset").changed.agg(["sum", "count"]).to_string())
    est = d[d.dataset.str.startswith("estimate")]
    for f in ["est_central", "est_low", "est_high", "grid", "buildings", "extent_km2"]:
        s = est[est.field == f].rel_change.abs().dropna()
        c = est[(est.field == f) & est.changed].rel_change.abs().dropna()
        print(
            f"{f}: rows with a value {len(s)}, changed {len(c)}, "
            f"max {100 * s.max():.4f} %, median (all) {100 * s.median():.4f} %, "
            f"median (changed) {100 * c.median():.4f} %"
        )
    sc = est[est.field == "est_central"].scale_old_over_new_minus_1 * 100
    print(
        f"linear scale old/new - 1: min {sc.min():.3f} median {sc.median():.3f} "
        f"max {sc.max():.3f} %"
    )


if __name__ == "__main__":
    main()
