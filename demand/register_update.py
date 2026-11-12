"""Apply the R3 register sidecars to the candidate register (CP3 decision 8, Tariq 31 Oct 2026).

Two sidecars, both written by R3 modules and keyed by `row_key`:
- `cities/ksa/zones/terrain_dem.parquet` (`demand.terrain classify`): the DEM terrain class
  replaces `terrain_class` on every row it covers (A-geo-011..022); the prior value stays in the
  sidecar (`terrain_class_prior`), so the change is reversible and logged;
- `runs/r3/skims_created/created_rows_skims.parquet` (`demand.register_skims run`): distance and
  road-time fields fill the cells that are NaN in the register (never overwrite a value).

The register keeps its column set (RegionRow fields); a change log goes to the run directory.
Re-running `screening/run_r2.sh` rebuilds the register from the region files and drops these
fields, so this step must follow it (hand-off recorded in docs/status/r3.md).

uv run python -m demand.register_update apply --seed 1 --out runs/r3/register_update/
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import typer

from common import REPO_ROOT
from common.runmeta import seed_option, write_meta

REGISTER = Path("cities/ksa/candidates.parquet")
TERRAIN = Path("cities/ksa/zones/terrain_dem.parquet")
SKIMS = Path("runs/r3/skims_created/created_rows_skims.parquet")
SKIM_FIELDS = (
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
)

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)


@app.callback()
def _group() -> None:
    """R3 register sidecars."""


def apply_terrain(reg: pd.DataFrame, terr: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Replace terrain_class by the DEM class; return the register and a change log."""
    t = terr.set_index("row_key")["terrain_class_dem"]
    out = reg.copy()
    new = out["row_key"].map(t)
    log = pd.DataFrame(
        {
            "row_key": out["row_key"],
            "terrain_before": out["terrain_class"],
            "terrain_after": new.where(new.notna(), out["terrain_class"]),
        }
    )
    out["terrain_class"] = log["terrain_after"].to_numpy()
    log = log[log.terrain_before.fillna("none") != log.terrain_after.fillna("none")]
    return out, log


def apply_skims(reg: pd.DataFrame, sk: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fill NaN distance/road cells from the sidecar; never overwrite an existing value."""
    out = reg.copy()
    s = sk.set_index("row_key")
    filled = []
    for i, key in out["row_key"].items():
        if key not in s.index:
            continue
        cells = []
        for f in SKIM_FIELDS:
            if f in out and pd.isna(out.at[i, f]) and pd.notna(s.at[key, f]):
                out.at[i, f] = s.at[key, f]
                cells.append(f)
        if cells:
            out.at[i, "road_min_method"] = s.at[key, "road_min_method"]
            filled.append({"row_key": key, "fields": ",".join(cells)})
    return out, pd.DataFrame(filled, columns=["row_key", "fields"])


@app.command()
def apply(
    register: Path = typer.Option(REGISTER),
    terrain: Path = typer.Option(TERRAIN),
    skims: Path = typer.Option(SKIMS),
    out: Path = typer.Option(Path("runs/r3/register_update")),
    seed: int = seed_option(),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Apply both sidecars in place to the register and log every change."""
    reg = pd.read_parquet(root / register)
    cols = list(reg.columns)
    reg, tlog = apply_terrain(reg, pd.read_parquet(root / terrain))
    reg, slog = apply_skims(reg, pd.read_parquet(root / skims))
    reg = reg[cols]
    reg.to_parquet(root / register, index=False)
    (root / out).mkdir(parents=True, exist_ok=True)
    tlog.to_csv(root / out / "terrain_changes.csv", index=False)
    slog.to_csv(root / out / "skims_filled.csv", index=False)
    summary = {
        "rows": len(reg),
        "terrain_changed_or_filled": len(tlog),
        "terrain_filled_from_none": int(tlog.terrain_before.isna().sum()),
        "skim_rows_filled": len(slog),
        "terrain_class_counts": reg["terrain_class"].value_counts(dropna=False).to_dict(),
        "road_min_metro_nan_after": int(reg["road_min_metro"].isna().sum()),
    }
    (root / out / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    write_meta(
        root / out,
        seed,
        {"register": str(register), "terrain": str(terrain), "skims": str(skims)},
        extra={"summary": summary, "assumptions": [f"A-geo-0{i}" for i in range(11, 23)]},
    )
    typer.echo(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    app()
