"""Cost register: validate, normalise to the price base, list (`cost-register` skill).

The register (`cities/ksa/costs/cost_register.yaml`) keeps every figure in its SOURCE currency and
price year. `normalise` converts money units to SAR at the index base year (2025, A-cost-001) with
the factors in `cities/ksa/costs/index.yaml` and writes `cost_register.normalised.yaml` next to the
register; it never edits the source file.

CLI:
  uv run python -m costs.register validate cities/ksa/costs/cost_register.yaml
  uv run python -m costs.register normalise --to SAR --price-year 2025 \
      [--method inflate_then_convert]
  uv run python -m costs.register list --category station [--status sourced]
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

import typer
import yaml

from common import REPO_ROOT
from common.schemas import CostItem, load_cost_register

REGISTER = REPO_ROOT / "cities" / "ksa" / "costs" / "cost_register.yaml"
INDEX = REPO_ROOT / "cities" / "ksa" / "costs" / "index.yaml"
SOURCES_DIR = REPO_ROOT / "docs" / "sources"
DOCS = REPO_ROOT / "docs"

# Units whose values are money (millions or units of `currency`); the rest are not converted.
MONEY_UNITS = {
    "SAR_m_per_km",
    "SAR_m_per_station",
    "SAR_m_per_trainset",
    "SAR_m_per_yr",
    "SAR_per_train_km",
    "SAR_m_lump",
    "SAR_m_per_km_per_yr",
    "SAR_m_per_unit",
    "SAR_per_kwh",
    "SAR_per_fte_yr",
    "SAR_per_m2",
}
SID = re.compile(r"\bS-[A-Za-z0-9-]+\b")
AID = re.compile(r"^\|\s*(A-[a-z]+-[A-Za-z0-9-]+)\s*\|", re.M)

app = typer.Typer(add_completion=False, help="Cost register: validate, normalise, list.")


# --------------------------------------------------------------------------- loading
def load_index(path: Path = INDEX) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def factor_table(index: dict[str, Any], method: str) -> dict[tuple[str, int], dict[str, Any]]:
    """(currency, year) -> factor. Per-economy EUR rows (`country:`, used by the W5 benchmark
    tables, CP2 P2a) are skipped: register items carry no economy, so they use the EA20 row."""
    return {
        (f["from_currency"], int(f["from_year"])): f
        for f in index["factors"]
        if f["method"] == method and not f.get("country")
    }


def known_source_ids(sources_dir: Path = SOURCES_DIR) -> set[str]:
    ids: set[str] = set()
    for p in sorted(sources_dir.glob("*.csv")):
        with p.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("id", "").startswith("S-"):
                    ids.add(row["id"].strip())
    return ids


def known_assumption_ids(docs: Path = DOCS) -> set[str]:
    ids: set[str] = set()
    for p in sorted(docs.glob("assumptions*.md")):
        ids |= set(AID.findall(p.read_text(encoding="utf-8")))
    return ids


# --------------------------------------------------------------------------- checks
def check(
    items: list[CostItem],
    index: dict[str, Any] | None = None,
    source_ids: set[str] | None = None,
    assumption_ids: set[str] | None = None,
) -> list[str]:
    """Rules beyond the pydantic schema. Returns a list of problems (empty = valid)."""
    probs: list[str] = []
    table = factor_table(index, index["method_central"]) if index else None
    for it in items:
        where = it.id
        if it.status == "assumed":
            if it.source != "assumed":
                probs.append(f"{where}: status assumed needs source: assumed")
            if not it.assumption_id:
                probs.append(f"{where}: status assumed needs assumption_id (A-cost-nnn)")
        if it.status == "unknown" and not (it.searched or (it.notes and "search" in it.notes)):
            probs.append(f"{where}: status unknown needs `searched:` (where it was searched)")
        if it.status in ("sourced", "derived") and not it.source.startswith("S-"):
            probs.append(f"{where}: status {it.status} needs an S- source id")
        if (
            it.status != "unknown"
            and it.unit in MONEY_UNITS
            and it.price_year_basis == "assumed"
            and not it.assumption_id
        ):
            probs.append(f"{where}: an assumed price year needs assumption_id")
        refs = [it.source, *it.extra_sources]
        refs += SID.findall(it.derivation or "")
        if source_ids is not None:
            for s in refs:
                if s.startswith("S-") and s not in source_ids:
                    probs.append(f"{where}: source id {s} not found in docs/sources/*.csv")
        if assumption_ids is not None and it.assumption_id:
            for a in re.split(r"[,; ]+", it.assumption_id.strip()):
                if a and a not in assumption_ids:
                    probs.append(f"{where}: assumption id {a} not found in docs/assumptions*.md")
        if (
            table is not None
            and it.unit in MONEY_UNITS
            and it.status != "unknown"
            and (it.currency, it.price_year) not in table
        ):
            probs.append(f"{where}: no index factor for {it.currency} {it.price_year}")
    return probs


# --------------------------------------------------------------------------- normalise
def normalise_item(
    it: CostItem, table: dict[tuple[str, int], dict[str, Any]], base: dict[str, Any]
) -> dict[str, Any]:
    d = it.model_dump(exclude_defaults=False)
    if it.unit not in MONEY_UNITS or it.status == "unknown":
        d["normalised"] = it.unit not in MONEY_UNITS and it.status != "unknown"
        return d
    f = table[(it.currency, it.price_year)]
    for k in ("low", "central", "high"):
        d[k] = round(float(getattr(it, k)) * f["factor"], 6)
    d["original"] = {
        "currency": it.currency,
        "price_year": it.price_year,
        "low": it.low,
        "central": it.central,
        "high": it.high,
    }
    d["currency"] = base["currency"]
    d["price_year"] = base["price_year"]
    d["index_factor"] = {"id": f["id"], "factor": f["factor"], "source": f["source"]}
    d["normalised"] = True
    return d


def normalise(
    items: list[CostItem],
    index: dict[str, Any],
    to: str = "SAR",
    price_year: int = 2025,
    method: str | None = None,
) -> list[dict[str, Any]]:
    base = index["base"]
    if to != base["currency"] or price_year != base["price_year"]:
        raise ValueError(
            f"index base is {base['currency']} {base['price_year']}; rebuild the index for "
            f"{to} {price_year} (costs.index_build)"
        )
    table = factor_table(index, method or index["method_central"])
    return [normalise_item(it, table, base) for it in items]


def normalised_lookup(
    register: Path = REGISTER, index: Path = INDEX, method: str | None = None
) -> dict[str, dict[str, Any]]:
    """Register items by id, money values in the index base (used by the estimator)."""
    items = load_cost_register(register)
    return {d["id"]: d for d in normalise(items, load_index(index), method=method)}


# --------------------------------------------------------------------------- CLI
@app.command()
def validate(
    path: Path = typer.Argument(REGISTER),
    index: Path = typer.Option(INDEX, "--index"),
    refs: bool = typer.Option(True, "--refs/--no-refs", help="check S- and A- ids exist"),
) -> None:
    """Schema + register rules + every money item has an index factor + ids resolve."""
    items = load_cost_register(path)
    probs = check(
        items,
        load_index(index),
        known_source_ids() if refs else None,
        known_assumption_ids() if refs else None,
    )
    for p in probs:
        typer.echo(f"FAIL {p}")
    counts = Counter(i.status for i in items)
    typer.echo(f"{len(items)} items; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if probs:
        raise typer.Exit(1)
    typer.echo("OK")


@app.command("normalise")
def normalise_cmd(
    to: str = typer.Option("SAR", "--to"),
    price_year: int = typer.Option(2025, "--price-year"),
    register: Path = typer.Option(REGISTER, "--register"),
    index: Path = typer.Option(INDEX, "--index"),
    method: str = typer.Option("", "--method", help="default: the index's central method"),
    out: Path | None = typer.Option(None, "--out"),
) -> None:
    """Write `<register>.normalised.yaml` (never edits the register)."""
    idx = load_index(index)
    rows = normalise(load_cost_register(register), idx, to, price_year, method or None)
    out = out or register.with_name(register.stem + ".normalised.yaml")
    header = (
        f"# GENERATED by `costs.register normalise` from {register.name}: do not edit.\n"
        f"# Money units in {to} millions (or {to}) at {price_year} prices; method "
        f"{method or idx['method_central']} (A-cost-002); index {index.name}.\n"
    )
    out.write_text(header + yaml.safe_dump(rows, sort_keys=False, allow_unicode=True), "utf-8")
    typer.echo(f"wrote {out} ({len(rows)} items)")


@app.command("list")
def list_cmd(
    category: str = typer.Option("", "--category"),
    status: str = typer.Option("", "--status"),
    register: Path = typer.Option(REGISTER, "--register"),
) -> None:
    """Print id, status, range, unit, currency and price year."""
    for it in load_cost_register(register):
        if (category and it.category != category) or (status and it.status != status):
            continue
        rng = "unknown" if it.status == "unknown" else f"{it.low:g} / {it.central:g} / {it.high:g}"
        typer.echo(f"{it.id:45s} {it.status:8s} {rng:>28s} {it.unit} {it.currency} {it.price_year}")


if __name__ == "__main__":
    app()
