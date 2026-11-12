"""Regenerate the table and row counts of docs/sources/index.md from docs/sources/index.csv.

Usage: uv run python scripts/regen_sources_index_md.py "<who, date>"
The CSV is canonical; the Markdown table repeats its rows in the same order (columns below).
"""

from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "docs/sources/index.csv"
MD = ROOT / "docs/sources/index.md"
COLS = ["id", "claim", "value", "unit", "publisher", "published", "locator", "status", "url"]
COLS += ["quote", "primary_to_find"]


def _cell(v: str) -> str:
    return " ".join((v or "").split()).replace("|", "\\|")


def main(who: str) -> None:
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    table = ["| " + " | ".join(_cell(r[c]) for c in COLS) + " |" for r in rows]
    pref = collections.Counter(
        "S-<number>" if re.match(r"^S-\d", r["id"]) else r["id"].split("-")[1] for r in rows
    )
    status = collections.Counter((r["status"].split() or ["?"])[0] for r in rows)
    lines = MD.read_text(encoding="utf-8").split("\n")
    head = next(i for i, ln in enumerate(lines) if ln.startswith("| id | claim |"))
    start = end = head + 2
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    k = next(i for i, ln in enumerate(lines) if ln.startswith("Rows: "))
    by_pref = "; ".join(
        f"{p} {n}" for p, n in sorted(pref.items(), key=lambda x: (x[0] != "S-<number>", x[0]))
    )
    by_status = ", ".join(f"{s} {n}" for s, n in sorted(status.items()))
    lines[k] = (
        f"Rows: {len(rows)} (generated from `docs/sources/index.csv` by {who}; per-track detail "
        "files `docs/sources/<track>-*.csv` stay in place because documents cite them). "
        f"Rows by id prefix: {by_pref}. Status counts by first word: {by_status}."
    )
    lines[start:end] = table
    MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"index.md: {len(rows)} rows")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "scripts/regen_sources_index_md.py")
