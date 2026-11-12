"""Control-total scaling of grid populations (A-screen-040; Tariq, 31 Oct 2026 16:25).

Per region: residual = primary TA1 region total (S-cp2-gastat-007) minus the primary cities
matched in the register (S-cp2-gastat-008; the residual holds the region's share of "Other
(< 5,000)" = 3,683,816 and any unmatched primary city). Grid sum = WorldPop-filled populations of
the settlement-universe rows that no primary city claims (`pop_type: grid`). Where the grid sum
exceeds the residual, the register's grid rows of that region are scaled down pro-rata by
residual / grid sum (`grid_scaled: true`, `grid_scale_factor`, unscaled value in `pop_grid_raw`);
otherwise the factor is 1.0 (never scaled up). The >= 10k gate is unchanged: scaled grid rows stay
`unverified` and are gated by the P1a corroboration rule; `tag_5k` follows the scaled value. The
0.71 grid sensitivity (A-screen-039) is reported on `pop_grid_raw`.

uv run python -m screening.control_total --register cities/ksa/candidates.parquet --seed 1
Label: screening input, not a forecast.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import typer

from common.runmeta import write_meta
from common.schemas import TAG_5K
from screening.funnel import tag_10k_rule
from screening.gastat import REGION_ORDER, read_ta1
from screening.primary_match import PRIMARY_SRC, UNIVERSE

app = typer.Typer(add_completion=False, help=__doc__)


def region_table(reg: pd.DataFrame, univ: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Per region: TA1 total, matched primary cities, residual, unclaimed grid sum, factor."""
    ta1 = read_ta1().set_index("region").population
    prim = reg[(reg.pop_source == PRIMARY_SRC) & reg.screened.astype(bool)]
    claimed_osm = {
        (t, int(i)) for t, i in zip(prim.osm_type, prim.osm_id, strict=True) if pd.notna(i)
    }
    claimed_sid = set(matches.settlement_id.dropna())
    free = univ[
        (univ.pop_type == "grid")
        & ~univ.settlement_id.isin(claimed_sid)
        & ~pd.Series(
            [(t, int(i)) in claimed_osm if pd.notna(i) else False
             for t, i in zip(univ.osm_type, univ.osm_id, strict=True)],
            index=univ.index,
        )
    ]  # fmt: skip
    t = pd.DataFrame(
        {
            "ta1_total": ta1,
            "matched_primary": prim.groupby("region").population.sum(),
            "n_matched_rows": prim.groupby("region").size(),
            "grid_universe": free.groupby("region").population.sum(),
            "n_grid_universe": free.groupby("region").size(),
        }
    ).reindex(REGION_ORDER)
    t = t.fillna(0)
    t["residual"] = t.ta1_total - t.matched_primary
    t["grid_minus_residual"] = t.grid_universe - t.residual
    ratio = np.where(t.grid_universe > 0, t.residual.clip(lower=0) / t.grid_universe, 1.0)
    t["grid_scale_factor"] = np.minimum(1.0, ratio).round(6)
    return t


def apply(reg: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """Scale the register's grid rows by their region's factor; keep the raw value."""
    reg = reg.copy()
    grid = (reg.pop_type == "grid") & reg.population.notna()
    f = reg.region.map(t.grid_scale_factor).fillna(1.0)
    reg["pop_grid_raw"] = reg.population.where(grid)
    reg["grid_scale_factor"] = f.where(grid)
    reg["grid_scaled"] = grid & (f < 1.0)
    reg.loc[grid, "population"] = (reg.loc[grid, "population"] * f[grid]).round()
    reg.loc[grid, "tag_5k"] = reg.loc[grid, "population"] >= TAG_5K
    reg.loc[grid, "tag_10k"] = tag_10k_rule(reg[grid])
    note = " | grid scaled to the region residual (A-screen-040): raw "
    for i in reg.index[reg.grid_scaled]:
        reg.at[i, "notes"] = (
            f"{reg.at[i, 'notes'] or ''}{note}{reg.at[i, 'pop_grid_raw']:,.0f} x "
            f"{reg.at[i, 'grid_scale_factor']:.4f}"
        ).lstrip(" |")
    return reg


def drop_zero(reg: pd.DataFrame) -> pd.DataFrame:
    """CP3 5a (Tariq, 31 Oct 2026; A-screen-041): grid rows with a raw WorldPop value of 0 carry no
    population evidence; they leave the register but stay in the settlement universe."""
    return reg[(reg.pop_type == "grid") & (reg.pop_grid_raw == 0)]


@app.command()
def main(
    register: Path = typer.Option(Path("cities/ksa/candidates.parquet"), "--register"),
    universe: Path = typer.Option(UNIVERSE, "--universe"),
    matches: Path = typer.Option(Path("runs/r2/primary_match/primary_cities.csv"), "--matches"),
    run_dir: Path = typer.Option(Path("runs/r2/control_total"), "--run-dir"),
    seed: int = typer.Option(1, "--seed", min=0, help="recorded in meta.json (exact arithmetic)"),
    drop_zero_grid: bool = typer.Option(
        False,
        "--drop-zero-grid",
        help="CP3 5a: drop grid rows whose raw value is 0 from the "
        "register (they stay in the settlement universe); listed in dropped_zero_grid.csv",
    ),
) -> None:
    """Compute the per-region factors, scale the register's grid rows, write the table."""
    reg = pd.read_parquet(register)
    if "pop_grid_raw" in reg and reg.pop_grid_raw.notna().any():
        raise typer.BadParameter("register already scaled: rebuild it from the merge first")
    t = region_table(reg, pd.read_parquet(universe), pd.read_csv(matches))
    new = apply(reg, t)
    g = new[new.pop_grid_raw.notna()]
    t["register_grid_rows"] = g.groupby("region").size().reindex(t.index).fillna(0).astype(int)
    t["register_grid_before"] = g.groupby("region").pop_grid_raw.sum().reindex(t.index).fillna(0)
    t["register_grid_after"] = g.groupby("region").population.sum().reindex(t.index).fillna(0)
    run_dir.mkdir(parents=True, exist_ok=True)
    dropped = drop_zero(new) if drop_zero_grid else new.iloc[0:0]
    if drop_zero_grid:
        new = new[~new.row_key.isin(dropped.row_key)].reset_index(drop=True)
        cols = [
            "row_key",
            "region",
            "governorate",
            "name_en",
            "name_ar",
            "pop_type",
            "pop_grid_raw",
        ]
        dropped[cols].to_csv(run_dir / "dropped_zero_grid.csv", index=False)
    t["register_zero_grid_dropped"] = (
        dropped.groupby("region").size().reindex(t.index).fillna(0).astype(int)
    )
    t.reset_index(names="region").to_csv(run_dir / "control_total.csv", index=False)
    new.to_parquet(register, index=False)
    summary = {
        "regions_scaled": [str(r) for r in t.index[t.grid_scale_factor < 1]],
        "rows_scaled": int(new.grid_scaled.sum()),
        "register_grid_before": round(float(t.register_grid_before.sum())),
        "register_grid_after": round(float(t.register_grid_after.sum())),
        "residual_national": int(t.residual.sum()),
        "grid_universe_national": round(float(t.grid_universe.sum())),
        "zero_grid_rows_dropped": int(len(dropped)),
        "register_rows": int(len(new)),
    }
    write_meta(run_dir, seed, {"register": str(register), "matches": str(matches)},
               {"step": "screening.control_total", "summary": summary})  # fmt: skip
    typer.echo(json.dumps(summary))


if __name__ == "__main__":
    app()
