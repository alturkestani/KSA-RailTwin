"""Region register validation (W2; `region-sweep` skill).

`validate` checks one region register (Parquet, plus its CSV mirror when present):
every row validates against `common.schemas.RegionRow`; one region per file; no duplicate
`osm_type`+`osm_id`; the header (Parquet key-value metadata) records `governorates_gastat` and
`governorates_listed`, and when both are integers they are equal and match the number of distinct
governorates in the rows. An unverified or missing GASTAT count is a warning (the pilots could not
reach GASTAT, S-090); `--strict` turns warnings into failures (R2 sweeps after GASTAT is read).

uv run python -m screening.region_sweep validate \
  cities/ksa/regions/archive/pilot/pilot-riyadh.parquet
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
import typer

from common.schemas import RegionRow, _plain

app = typer.Typer(add_completion=False, help=__doc__, no_args_is_help=True)
HEADER_KEYS = ("governorates_gastat", "governorates_listed")


def _int(v: str | None) -> int | None:
    m = re.fullmatch(r"\s*(\d+)\s*", v or "")
    return int(m.group(1)) if m else None


def header(path: Path) -> dict[str, str]:
    md = pq.read_schema(path).metadata or {}
    return {k.decode(): v.decode() for k, v in md.items() if k != b"pandas"}


def validate_file(path: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    """Return (errors, warnings, facts) for one register."""
    errors: list[str] = []
    warnings: list[str] = []
    df = pd.read_parquet(path)
    for i, rec in enumerate(df.to_dict(orient="records")):
        try:
            RegionRow.model_validate({k: _plain(v) for k, v in rec.items() if k != "row_key"})
        except ValueError as e:
            first = str(e).splitlines()
            errors.append(f"row {i} ({rec.get('name_en')}): {' '.join(first[:3])}")
    regions = sorted(set(df["region"])) if "region" in df else []
    if len(regions) != 1:
        errors.append(f"expected one region per file, found {regions}")
    if "osm_id" in df:
        ids = df.dropna(subset=["osm_id"])
        key = (
            ids.get("osm_type", pd.Series("?", index=ids.index)).fillna("?").astype(str)
            + ":"
            + ids["osm_id"].astype("int64").astype(str)
        )
        dup = sorted(set(key[key.duplicated()]))
        if dup:
            errors.append(f"duplicate OSM ids: {dup}")
    n_gov = int(df["governorate"].nunique()) if "governorate" in df else 0
    hdr = header(path)
    gastat, listed = (_int(hdr.get(k)) for k in HEADER_KEYS)
    missing = [k for k in HEADER_KEYS if k not in hdr]
    if missing:
        warnings.append(f"header lacks {', '.join(missing)}")
    if gastat is None and "governorates_gastat" in hdr:
        warnings.append(f"governorates_gastat not an integer: {hdr['governorates_gastat'][:60]!r}")
    if gastat is not None and listed is not None and gastat != listed:
        errors.append(f"governorates_gastat {gastat} != governorates_listed {listed}")
    if listed is not None and listed != n_gov:
        errors.append(f"governorates_listed {listed} != {n_gov} distinct governorates in the rows")
    csv = path.with_suffix(".csv")
    if csv.exists():
        c = pd.read_csv(csv)
        if len(c) != len(df):
            errors.append(f"CSV mirror has {len(c)} rows, Parquet {len(df)}")
        elif list(c["name_en"]) != list(df["name_en"]):
            errors.append("CSV mirror rows differ from the Parquet (name_en order)")
    else:
        warnings.append("no CSV mirror")
    facts = {"rows": len(df), "region": regions, "governorates_in_rows": n_gov, **hdr}
    return errors, warnings, facts


@app.callback()
def main() -> None:
    """Region register tools (`validate`)."""


@app.command()
def validate(
    paths: list[Path] = typer.Argument(..., help="region register Parquet file(s)"),
    strict: bool = typer.Option(False, "--strict", help="warnings fail too"),
) -> None:
    """Validate region registers against RegionRow and the governorate-count header."""
    failed = False
    for p in paths:
        errors, warnings, facts = validate_file(p)
        for e in errors:
            typer.echo(f"FAIL {p.name}: {e}")
        for w in warnings:
            typer.echo(f"{'FAIL' if strict else 'WARN'} {p.name}: {w}")
        failed |= bool(errors) or (strict and bool(warnings))
        n, g = facts["rows"], facts["governorates_in_rows"]
        typer.echo(f"{'ok  ' if not errors else 'bad '} {p.name}: {n} rows, {g} governorates")
    if failed:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
