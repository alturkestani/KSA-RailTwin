"""Road skims for register rows that have none (R3 task 2: the rows created at the R2 merge carry
`road_min_method == 'pending skims'`, plus a few rows that never got a skim).

Reuses `network.distances register` unchanged: the selected rows are written to a temporary
register file under the run directory, `network.distances.register_cmd` computes the distance
fields with the national OSRM files (osrm-routed is started and stopped by
`network.osrm.server`, inside register_cmd), and the result is reduced to a sidecar keyed by
row_key. Three rows that already have skims are recomputed in the same call as a consistency check
against the register (tolerance 0.1 min).

Road times are OSRM MLD car, free flow, uncalibrated (S-r1a-809). Committed-line stations are
unlocated proxies (A-r1a-006). The sidecar is not merged into the register here: the coordinator
applies it.

CLI:
  uv run python -m demand.register_skims run --seed 1 --out runs/r3/skims_created/
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import typer

from common import REPO_ROOT
from common.runmeta import rng, seed_option, write_meta
from network import distances
from network import osrm as osrm_mod

REGISTER = Path("cities/ksa/candidates.parquet")
OSRM_DIR = Path("data/ksa/osrm/gcc-states-latest")
ROAD = ["road_min_existing", "road_min_committed", "road_min_metro"]
FIELDS = [
    "dist_existing_km",
    "road_min_existing",
    "nearest_existing",
    "dist_committed_km",
    "road_min_committed",
    "nearest_committed",
    "nearest_committed_station",
    "dist_metro_km",
    "road_min_metro",
    "nearest_metro",
    "nearest_metro_tier",
]
TOL_MIN = 0.1
app = typer.Typer(add_completion=False, help="Road skims for register rows without them.")


@app.callback()
def main() -> None:
    """Road skims for register rows without them (R3)."""


def select(reg: pd.DataFrame) -> pd.DataFrame:
    """Rows with any road field NaN and a location."""
    need = reg[ROAD].isna().any(axis=1)
    return reg[need & reg.lat.notna() & reg.lon.notna()]


def check_rows(reg: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    """n rows that already have all three road fields from an OSRM skim (seeded choice)."""
    ok = reg[reg[ROAD].notna().all(axis=1) & reg.road_min_method.fillna("").str.contains("osrm")]
    idx = rng(seed).choice(len(ok), size=min(n, len(ok)), replace=False)
    return ok.iloc[np.sort(idx)]


def location_basis(row: pd.Series) -> str:
    cols = ("row_key", "road_min_method", "data_flag", "notes", "exclusion_reason")
    text = " ".join(str(row.get(c) or "") for c in cols)
    if "centroid" in text or "not located" in text or "not identified" in text:
        return "polygon point, not a located settlement centre (distances indicative)"
    return "register point"


@app.command("run")
def run(
    out: Path = typer.Option(Path("runs/r3/skims_created"), "--out"),
    register: Path = typer.Option(REGISTER, "--register"),
    osrm_dir: Path = typer.Option(OSRM_DIR, "--osrm-dir"),
    n_check: int = typer.Option(3, "--n-check", help="rows with skims recomputed as a check"),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Compute the distance fields for the rows without skims; write the sidecar and meta.json."""
    t0 = time.time()
    reg = pd.read_parquet(root / register)
    todo, chk = select(reg), check_rows(reg, n_check, seed)
    no_loc = reg[reg[ROAD].isna().any(axis=1) & (reg.lat.isna() | reg.lon.isna())]
    batch = pd.concat([todo, chk]).reset_index(drop=True)
    out_dir = root / out
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_in, tmp_out = out / "register_input.parquet", out / "register_output.parquet"
    batch[["row_key", "lat", "lon"]].to_parquet(root / tmp_in, index=False)
    # network.distances.register: same sets, same OSRM server context manager, same rounding
    distances.register_cmd(
        inp=tmp_in,
        out=tmp_out,
        backend="osrm",
        osrm_dir=osrm_dir,
        out_run=out / "register_cmd",
        seed=seed,
        root=root,
    )
    res = pd.read_parquet(root / tmp_out)
    res["road_min_method"] = res["road_min_method"] + " via network.distances register (R3)"
    created = res.iloc[: len(todo)].copy()
    created["location_basis"] = [location_basis(r) for _, r in todo.iterrows()]
    created["prior_road_min_method"] = todo.road_min_method.to_numpy()
    for c in ROAD:
        created[f"{c}_reachable"] = created[c].notna()
    cols = [
        "row_key",
        *FIELDS,
        "dist_method",
        "road_min_method",
        "location_basis",
        "prior_road_min_method",
        *[f"{c}_reachable" for c in ROAD],
    ]
    created = created[cols].sort_values("row_key").reset_index(drop=True)
    created.to_parquet(out_dir / "created_rows_skims.parquet", index=False)

    checks = []
    got = res.iloc[len(todo) :].reset_index(drop=True)
    for i, (_, r) in enumerate(chk.iterrows()):
        g = got.iloc[i]
        item = {"row_key": r.row_key}
        for c in ROAD:
            item[c] = {
                "register": float(r[c]),
                "recomputed": float(g[c]),
                "abs_diff": round(abs(float(r[c]) - float(g[c])), 3),
            }
        for c in ("nearest_existing", "nearest_committed_station", "nearest_metro"):
            item[c] = {"register": r[c], "recomputed": g[c], "same": bool(r[c] == g[c])}
        item["within_tolerance"] = all(item[c]["abs_diff"] <= TOL_MIN for c in ROAD)
        checks.append(item)
    still = created[created[ROAD].isna().any(axis=1)]
    summary = {
        "rows_without_skims_in_register": int(reg[ROAD].isna().any(axis=1).sum()),
        "rows_computed": len(created),
        "rows_without_location": len(no_loc),
        "rows_with_pending_skims_method": int((todo.road_min_method == "pending skims").sum()),
        "created_at_merge_primary_match_tier_notnull": int(todo.primary_match_tier.notna().sum()),
        "breakdown_prior_method_x_tier": {
            f"{m} | tier={'set' if t else 'null'}": int(n)
            for (m, t), n in todo.groupby(
                [todo.road_min_method.fillna("NaN"), todo.primary_match_tier.notna()]
            )
            .size()
            .items()
        },
        "still_nan_after_run": {
            r.row_key: [c for c in ROAD if pd.isna(r[c])] for _, r in still.iterrows()
        },
        "polygon_point_rows": created.loc[
            created.location_basis.str.startswith("polygon"), "row_key"
        ].tolist(),
        "consistency_check_tolerance_min": TOL_MIN,
        "consistency_check": checks,
        "consistency_all_within_tolerance": all(c["within_tolerance"] for c in checks),
        "seconds": round(time.time() - t0, 1),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    pbf = root / osrm_dir / "gcc-states-latest.osm.pbf"
    write_meta(
        out_dir,
        seed,
        {"register": str(register), "osrm_dir": str(osrm_dir), "n_check": n_check},
        extra={
            "osrm_version": osrm_mod.osrm_version(),
            "pbf_sha256": osrm_mod.sha256_file(pbf) if pbf.exists() else "pbf not found",
            "method": "network.distances.register_cmd (OSRM MLD car, free flow, uncalibrated)",
            "assumptions": ["A-r1a-006", "A-r1a-007", "A-r1a-008", "A-r1a-009", "A-r1a-027"],
            "summary_file": "summary.json",
        },
    )
    typer.echo(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "rows_computed",
                    "still_nan_after_run",
                    "consistency_all_within_tolerance",
                    "seconds",
                )
            },
            indent=1,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    app()
