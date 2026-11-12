"""INTEGRATE_R2 before/after check (CP3 4a and 5a; Tariq, 31 Oct 2026).

Compares three runs of `screening/run_r2.sh` on seed 1: the R2 state (`--before`), the item-1 fix
only (12 unmatched >= 10k primary cities placed, zero-population grid rows kept: `--nodrop`,
`DROP_ZERO=0`) and the final state (`--after`, zero rows dropped). Reports register and list
counts, short-list entries and exits, rank changes, Jubail's and Jubail Industrial City's scores,
corridors that changed (and those touching either place) and the control-total factors.

uv run python -m screening.integrate_r2_check --before runs/integrate_r2/before \
  --nodrop runs/integrate_r2/item1-nodrop --after runs/r2 --run-dir runs/integrate_r2/check
Label: screening input, not a forecast.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import typer

from common.runmeta import write_meta

app = typer.Typer(add_completion=False, help=__doc__)

JUBAIL = "eastern:node:38903292"  # Al Jubayl (TA1 Aljubayl 302,446)
JIC = "eastern:node:1237806971"  # Jubail Industrial City (TA1 172,233), CP3 4a
SCORE_COLS = ["name_en", "population", "score", "rank", "rank_min", "rank_max", "short_list",
              "c_population", "c_rail_gap", "c_commute", "c_economic_roles", "c_terrain",
              "missing"]  # fmt: skip


def _run(d: Path, register: Path | None = None) -> dict[str, Any]:
    reg = pd.read_parquet(register or d / "candidates.parquet")
    return {
        "register": reg,
        "scores": pd.read_parquet(d / "score" / "scores.parquet"),
        "corridors": pd.read_csv(d / "corridors" / "corridors.csv"),
        "control": pd.read_csv(d / "control_total" / "control_total.csv"),
    }


def _rec(s: pd.DataFrame, key: str) -> dict[str, Any] | None:
    r = s[s.row_key == key]
    if r.empty:
        return None
    out = r.iloc[0][SCORE_COLS].to_dict()
    return {k: (v.item() if hasattr(v, "item") else v) for k, v in out.items()}


def compare_scores(a: pd.DataFrame, b: pd.DataFrame) -> dict[str, Any]:
    """Short-list entries/exits and rank changes between two score tables (row_key keyed)."""
    sa, sb = set(a[a.short_list].row_key), set(b[b.short_list].row_key)
    ia, ib = a.set_index("row_key"), b.set_index("row_key")
    m = a[["row_key", "rank"]].merge(b[["row_key", "rank"]], on="row_key", how="outer",
                                     suffixes=("_before", "_after"))  # fmt: skip
    changed = m[m.rank_before.ne(m.rank_after)]
    moved = changed.dropna()
    return {
        "long_list": [len(a), len(b)],
        "short_list": [len(sa), len(sb)],
        "enter": [{"row_key": k, "name_en": ib.at[k, "name_en"], "rank": int(ib.at[k, "rank"])}
                  for k in sorted(sb - sa, key=lambda k: ib.at[k, "rank"])],
        "leave": [{"row_key": k, "name_en": ia.at[k, "name_en"], "rank_before":
                   int(ia.at[k, "rank"]), "rank_after": int(ib.at[k, "rank"])
                   if k in ib.index else None}
                  for k in sorted(sa - sb, key=lambda k: ia.at[k, "rank"])],
        "new_in_long_list": int(m.rank_before.isna().sum()),
        "left_long_list": int(m.rank_after.isna().sum()),
        "rank_changed": int(len(moved)),
        "max_abs_rank_shift": int((moved.rank_after - moved.rank_before).abs().max())
        if len(moved) else 0,
        "moved_down": int((moved.rank_after > moved.rank_before).sum()),
        "max_down": int((moved.rank_after - moved.rank_before).max()) if len(moved) else 0,
        "moved_up": [{"row_key": r.row_key, "name_en": ib.at[r.row_key, "name_en"],
                      "rank_before": int(r.rank_before), "rank_after": int(r.rank_after)}
                     for r in moved[moved.rank_after < moved.rank_before].itertuples()],
    }  # fmt: skip


def compare_corridors(a: pd.DataFrame, b: pd.DataFrame, keys: list[str]) -> dict[str, Any]:
    """Corridor ids added/removed, rows whose generated_from or geometry summary changed, and
    every corridor generated from one of `keys` (before and after)."""
    ia, ib = a.set_index("id"), b.set_index("id")
    both = sorted(set(ia.index) & set(ib.index))
    cols = ["generated_from", "length_km", "stations", "line_type", "rule"]
    changed = [
        {"id": i, **{f"{c}_before": ia.at[i, c] for c in cols if ia.at[i, c] != ib.at[i, c]},
         **{f"{c}_after": ib.at[i, c] for c in cols if ia.at[i, c] != ib.at[i, c]}}
        for i in both
        if any(ia.at[i, c] != ib.at[i, c] for c in cols)
    ]  # fmt: skip

    def touching(d: pd.DataFrame) -> list[dict[str, Any]]:
        hit = d[d.generated_from.astype(str).map(lambda g: any(k in g for k in keys))]
        return hit[["id", "line_type", "length_km", "stations", "generated_from"]].to_dict(
            "records"
        )

    return {
        "count": [len(a), len(b)],
        "by_family_after": {k: int(v) for k, v in b.family.value_counts().items()},
        "added": sorted(set(ib.index) - set(ia.index)),
        "removed": sorted(set(ia.index) - set(ib.index)),
        "changed": changed,
        "touching_before": touching(a),
        "touching_after": touching(b),
    }


def _clean(o: Any) -> Any:
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o]
    if hasattr(o, "item"):
        return o.item()
    if isinstance(o, float) and pd.isna(o):
        return None
    return o


@app.command()
def main(
    before: Path = typer.Option(Path("runs/integrate_r2/before"), "--before"),
    nodrop: Path = typer.Option(Path("runs/integrate_r2/item1-nodrop"), "--nodrop"),
    after: Path = typer.Option(Path("runs/r2"), "--after"),
    after_register: Path = typer.Option(Path("cities/ksa/candidates.parquet"), "--after-register"),
    run_dir: Path = typer.Option(Path("runs/integrate_r2/check"), "--run-dir"),
    seed: int = typer.Option(1, "--seed", min=0, help="recorded in meta.json (no sampling)"),
) -> None:
    """Write check.json (item 1, item 2 and the Jubail check) and print a summary."""
    A, N, F = _run(before), _run(nodrop), _run(after, after_register)
    ctrl = A["control"][["region", "grid_scale_factor"]].merge(
        F["control"][["region", "grid_scale_factor", "register_zero_grid_dropped"]],
        on="region", suffixes=("_r2", "_now"),
    )  # fmt: skip
    out = {
        "label": "screening input, not a forecast",
        "register_rows": {
            "r2": len(A["register"]),
            "item1": len(N["register"]),
            "final": len(F["register"]),
        },  # fmt: skip
        "item1_vs_r2": compare_scores(A["scores"], N["scores"]),
        "drop_vs_item1": compare_scores(N["scores"], F["scores"]),
        "final_vs_r2": compare_scores(A["scores"], F["scores"]),
        "jubail": {"r2": _rec(A["scores"], JUBAIL), "final": _rec(F["scores"], JUBAIL)},
        "jubail_industrial_city": {"r2": _rec(A["scores"], JIC), "final": _rec(F["scores"], JIC)},
        "corridors": compare_corridors(A["corridors"], F["corridors"], [JUBAIL, JIC]),
        "control_total": ctrl.to_dict("records"),
    }
    out = _clean(out)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                        encoding="utf-8")  # fmt: skip
    write_meta(run_dir, seed, {"before": str(before), "nodrop": str(nodrop), "after": str(after)},
               {"step": "screening.integrate_r2_check"})  # fmt: skip
    keys = ("register_rows", "jubail", "jubail_industrial_city")
    typer.echo(json.dumps({k: out[k] for k in keys}, default=str))


if __name__ == "__main__":
    app()
