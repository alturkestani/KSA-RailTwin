"""CP1_PREP data fixes to the 13 pilot registers (items 1.3 and 5), reproducible from the repo.

Inputs (this folder): `roles.csv` (economic roles to add, one line per role; only `decision ==
added` lines are applied) and `rows.yaml` (population updates and new rows, each with its S-cp1
source). Every changed register is re-validated against `RegionRow`, its Parquet key-value header
is kept (a withheld row that is now added is removed from `withheld_rows`), and the CSV mirror is
rewritten in the `screening.pilot_normalise` format. Idempotent: a role already present is skipped.

Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

uv run python -m screening.cp1_fixes.apply            # rewrites the pilot registers
uv run python -m screening.cp1_fixes.apply --dry-run  # report only
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import typer
import yaml

from common.schemas import TAG_5K, TAG_10K, TAG_50K, RegionRow, _plain
from screening.merge import row_key

HERE = Path(__file__).parent
REGIONS = Path("cities/ksa/regions/archive/pilot")  # pilot registers, archived at INTEGRATE_R2
app = typer.Typer(add_completion=False, help=__doc__)


def _records(path: Path) -> list[dict[str, Any]]:
    return [{k: _plain(v) for k, v in r.items()} for r in pd.read_parquet(path).to_dict("records")]


def _tags(rec: dict[str, Any]) -> None:
    pop = rec.get("population")
    rec["tag_10k"] = pop is not None and pop >= TAG_10K
    rec["tag_5k"] = pop is not None and pop >= TAG_5K
    if rec.get("threshold_50k") is not None:
        rec["threshold_50k"] = pop is not None and pop >= TAG_50K


def _add_source(rec: dict[str, Any], sid: str) -> None:
    if sid and sid not in rec["sources"]:
        rec["sources"] = [*rec["sources"], sid]


def apply_roles(recs: list[dict[str, Any]], roles: pd.DataFrame, log: Counter) -> None:
    by_key = {row_key(r): r for r in recs}
    for line in roles.itertuples():
        rec = by_key.get(line.row_key)
        if rec is None:
            raise KeyError(f"roles.csv: {line.row_key} not in the {line.region} register")
        have = {(r["role"], r["source"]) for r in rec["economic_roles"]}
        if (line.role, line.source_id) in have:
            continue
        rec["economic_roles"] = [
            *rec["economic_roles"],
            {"role": line.role, "source": line.source_id},
        ]
        _add_source(rec, line.source_id)
        log[line.region] += 1


def apply_rows(
    recs: list[dict[str, Any]], spec: dict[str, Any], meta: dict[bytes, bytes]
) -> list[str]:
    done = []
    by_key = {row_key(r): r for r in recs}
    for upd in spec.get("update", []):
        rec = by_key[upd["row_key"]]
        rec.update(upd["set"])
        _tags(rec)
        for sid in upd.get("add_sources", []):
            _add_source(rec, sid)
        done.append(f"update {upd['row_key']}")
    for new in spec.get("add", []):
        rec = {"economic_roles": [], "sources": [], **new}
        _tags(rec)
        if row_key(rec) in by_key:
            continue
        recs.append(rec)
        withheld = json.loads(meta.get(b"withheld_rows", b"[]"))
        withheld = [w for w in withheld if w["name_en"] != rec.get("withheld_name", rec["name_en"])]
        rec.pop("withheld_name", None)
        if withheld:
            meta[b"withheld_rows"] = json.dumps(withheld, ensure_ascii=False).encode()
        else:
            meta.pop(b"withheld_rows", None)
        done.append(f"add {row_key(rec)}")
    return done


def write_register(path: Path, recs: list[dict[str, Any]], meta: dict[bytes, bytes]) -> None:
    rows = [RegionRow.model_validate(r).model_dump(mode="json") for r in recs]
    new = pd.DataFrame(rows)
    table = pa.Table.from_pandas(new, preserve_index=False)
    table = table.replace_schema_metadata({**(table.schema.metadata or {}), **meta})
    pq.write_table(table, path)
    flat = new.copy()
    flat["economic_roles"] = flat["economic_roles"].map(
        lambda rs: ";".join(f"{r['role']}:{r['source']}" for r in rs)
    )
    flat["sources"] = flat["sources"].map(";".join)
    flat.to_csv(path.with_suffix(".csv"), index=False)


@app.command()
def main(
    roles_csv: Path = typer.Option(HERE / "roles.csv", "--roles"),
    rows_yaml: Path = typer.Option(HERE / "rows.yaml", "--rows"),
    regions: Path = typer.Option(REGIONS, "--regions"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Apply the role additions and row fixes; print a per-region report."""
    roles = pd.read_csv(roles_csv)
    roles = roles[roles["decision"] == "added"]
    spec = yaml.safe_load(rows_yaml.read_text(encoding="utf-8")) if rows_yaml.exists() else {}
    log: Counter = Counter()
    report: dict[str, Any] = {}
    for path in sorted(regions.glob("pilot-*.parquet")):
        region = path.stem.removeprefix("pilot-")
        recs = _records(path)
        meta = {
            k: v for k, v in (pq.read_schema(path).metadata or {}).items() if b"pandas" not in k
        }
        before = json.dumps(recs, sort_keys=True, default=str)
        apply_roles(recs, roles[roles["region"] == region], log)
        done = apply_rows(recs, spec.get(region, {}), meta)
        if json.dumps(recs, sort_keys=True, default=str) == before:
            continue
        report[region] = {"roles_added": log[region], "rows": done, "n_rows": len(recs)}
        if not dry_run:
            write_register(path, recs, meta)
    typer.echo(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    app()
