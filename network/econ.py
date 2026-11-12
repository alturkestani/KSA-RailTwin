"""Economic nodes table (PROJECT.md W1 "economic roles"): validates
cities/ksa/zones/economic_nodes.csv (written by rail-data-scout, one source id per row) and writes
cities/ksa/zones/economic_nodes.parquet. Rows without a source id are not written (prompt R1a,
task 3). Unlocated rows keep empty coordinates (never guessed) and `located = False`.

CLI: uv run python -m network.econ
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from common import REPO_ROOT
from common.schemas import KSA_LAT, KSA_LON, REGIONS

CSV = Path("cities/ksa/zones/economic_nodes.csv")
OUT = Path("cities/ksa/zones/economic_nodes.parquet")
ROLES = {
    "port",
    "industrial_city",
    "mining",
    "tourism",
    "heritage",
    "hajj_umrah",
    "airport",
    "university",
    "giga_project",
    "agriculture",
    "border_crossing",
    "military",
    "energy",
}

app = typer.Typer(add_completion=False, help="Economic nodes: validate CSV, write Parquet.")


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    problems: list[str] = []
    df = df.copy()
    src = df.source_id.fillna("").astype(str).str.strip()
    no_src = src.eq("") | ~src.str.startswith("S-")
    for nid in df.node_id[no_src]:
        problems.append(f"{nid}: no S- source id (row not written)")
    df = df[~no_src]
    bad_role = ~df.role.isin(ROLES)
    for nid, role in zip(df.node_id[bad_role], df.role[bad_role], strict=True):
        problems.append(f"{nid}: role {role!r} not in the enum (row not written)")
    df = df[~bad_role]
    dup = df.node_id.duplicated(keep="first")
    for nid in df.node_id[dup]:
        problems.append(f"{nid}: duplicate node_id (later row not written)")
    df = df[~dup]
    bad_region = df.region.notna() & ~df.region.isin(REGIONS)
    for nid in df.node_id[bad_region]:
        problems.append(f"{nid}: region not one of the 13 keys")
    lat = pd.to_numeric(df.lat, errors="coerce")
    lon = pd.to_numeric(df.lon, errors="coerce")
    df["lat"], df["lon"] = lat, lon
    df["located"] = lat.notna() & lon.notna() & ~df.location_method.eq("unlocated")
    box = df.located & ~(lat.between(*KSA_LAT) & lon.between(*KSA_LON))
    for nid in df.node_id[box]:
        problems.append(f"{nid}: coordinates outside the KSA sanity box (A-data-001)")
    df.loc[box, "located"] = False
    return df.reset_index(drop=True), problems


@app.command()
def main(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Validate the CSV and write the Parquet; print counts per role and the problems."""
    df, problems = validate(pd.read_csv(root / CSV, dtype=str))
    df.to_parquet(root / OUT, index=False)
    for p in problems:
        typer.echo(f"WARN {p}")
    counts = df.groupby("role").agg(rows=("node_id", "count"), located=("located", "sum"))
    typer.echo(counts.to_string())
    typer.echo(f"rows written {len(df)}; located {int(df.located.sum())}")


if __name__ == "__main__":
    app()
