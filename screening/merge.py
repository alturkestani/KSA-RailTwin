"""Merge region registers into one candidate register (W2; `screening-funnel` skill, stage 1).

Concatenates `RegionRow` tables, validates every row, de-duplicates (by `osm_type`+`osm_id`, else
by name and coordinates rounded to 3 decimals, about 100 m), adds `row_key` and
`funnel_stage = all`, and records per-region counts in the Parquet metadata and in
`<run-dir>/meta.json` (rule 10).

uv run python -m screening.merge --pattern "cities/ksa/regions/archive/pilot/pilot-*.parquet" \
    --out cities/ksa/candidates-pilot.parquet --seed 1
"""

from __future__ import annotations

import fnmatch
import glob
import json
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer

from common.runmeta import write_meta
from common.schemas import RegionRow, _plain

app = typer.Typer(add_completion=False, help="Merge region registers into the candidate register.")


def row_key(r: dict[str, Any]) -> str:
    if r.get("osm_id") is not None:
        return f"{r['region']}:{r.get('osm_type') or 'osm'}:{int(r['osm_id'])}"
    return f"{r['region']}:name:{r['name_en']}@{r['lat']:.3f},{r['lon']:.3f}"


def _dedup_key(r: dict[str, Any]) -> tuple:
    if r.get("osm_id") is not None:
        return ("osm", r.get("osm_type"), int(r["osm_id"]))
    return ("name", r["name_en"].casefold(), round(r["lat"], 3), round(r["lon"], 3))


def merge_frames(paths: list[Path]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate, concatenate and de-duplicate; return the frame and a report."""
    rows: list[dict[str, Any]] = []
    per_file: dict[str, int] = {}
    withheld: dict[str, Any] = {}
    for p in sorted(paths):
        df = pd.read_parquet(p)
        per_file[p.name] = len(df)
        md = pq.read_schema(p).metadata or {}
        if b"withheld_rows" in md:
            withheld[p.name] = json.loads(md[b"withheld_rows"])
        for rec in df.to_dict(orient="records"):
            row = RegionRow.model_validate({k: _plain(v) for k, v in rec.items()})
            rows.append(row.model_dump(mode="json"))
    seen: dict[tuple, int] = {}
    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, str]] = []
    for r in rows:
        k = _dedup_key(r)
        if k in seen:
            first = kept[seen[k]]
            dropped.append(
                {
                    "dropped": f"{r['region']}/{r['name_en']}",
                    "kept": f"{first['region']}/{first['name_en']}",
                    "key": str(k),
                }
            )
            continue
        seen[k] = len(kept)
        kept.append(r)
    out = pd.DataFrame(kept)
    out.insert(0, "row_key", [row_key(r) for r in kept])
    out["funnel_stage"] = "all"
    if out["row_key"].duplicated().any():
        raise ValueError("row_key is not unique after de-duplication")
    report = {
        "files": per_file,
        "rows_in": len(rows),
        "rows_out": len(out),
        "duplicates_dropped": dropped,
        "withheld_rows": withheld,
        "rows_per_region": {
            k: int(v) for k, v in out["region"].value_counts().sort_index().items()
        },
    }
    return out, report


def write_register(df: pd.DataFrame, report: dict[str, Any], out: Path) -> None:
    table = pa.Table.from_pandas(df, preserve_index=False)
    md = {**(table.schema.metadata or {}), b"merge_report": json.dumps(report).encode()}
    out.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table.replace_schema_metadata(md), out)


@app.command()
def main(
    pattern: str = typer.Option(..., "--pattern", help="glob of region register Parquet files"),
    exclude: list[str] = typer.Option(
        [], "--exclude", help="glob(s) of file names to leave out, e.g. 'pilot-*'"
    ),
    out: Path = typer.Option(..., "--out"),
    run_dir: Path = typer.Option(Path("runs/screening-pilot/merge"), "--run-dir"),
    seed: int = typer.Option(1, "--seed", min=0, help="recorded in meta.json (merge is exact)"),
) -> None:
    """Merge the registers matching PATTERN into OUT."""
    paths = [
        Path(p)
        for p in glob.glob(pattern)
        if not any(fnmatch.fnmatch(Path(p).name, x) for x in exclude)
    ]
    if not paths:
        raise typer.BadParameter(f"no file matches {pattern}")
    df, report = merge_frames(paths)
    write_register(df, report, out)
    write_meta(
        run_dir,
        seed,
        {"pattern": pattern, "exclude": exclude, "out": str(out)},
        {"step": "screening.merge", "report": report},
    )
    typer.echo(json.dumps({k: report[k] for k in ("rows_in", "rows_out", "rows_per_region")}))
    typer.echo(f"duplicates dropped: {len(report['duplicates_dropped'])}; wrote {out}")


if __name__ == "__main__":
    app()
