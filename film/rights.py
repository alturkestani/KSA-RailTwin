"""Rights log check (film/rights_log.csv).

CLI:
  uv run python -m film.rights check film/rights_log.csv

Columns: item,type,version,source,licence,attribution,proof_link,status,used_in,notes.
Rules: type and status from the enums below; item, source, licence and proof_link (http/https)
non-empty; image and footage rows need an attribution; any XTTS item (Coqui CPML,
non-commercial) must be rejected or test_only and never used in a film cut.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

import typer

COLUMNS = [
    "item",
    "type",
    "version",
    "source",
    "licence",
    "attribution",
    "proof_link",
    "status",
    "used_in",
    "notes",
]
TYPES = (
    "voice",
    "tts_model",
    "model",
    "font",
    "music",
    "image",
    "footage",
    "tool",
    "data",
    "service",
)
STATUSES = ("candidate", "approved", "rejected", "test_only", "used")
LINK = re.compile(r"^https?://\S+$")
XTTS = re.compile(r"xtts", re.IGNORECASE)

app = typer.Typer(add_completion=False, help="Rights log checks.")


def check_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for n, r in enumerate(rows, start=2):
        where = f"row {n} ({r.get('item', '')})"
        for k in ("item", "source", "licence", "proof_link"):
            if not (r.get(k) or "").strip():
                errors.append(f"{where}: {k} is empty")
        if r.get("proof_link") and not LINK.match(r["proof_link"].strip()):
            errors.append(f"{where}: proof_link must be an http(s) URL")
        if r.get("type") not in TYPES:
            errors.append(f"{where}: type {r.get('type')!r} not in {TYPES}")
        if r.get("status") not in STATUSES:
            errors.append(f"{where}: status {r.get('status')!r} not in {STATUSES}")
        if r.get("type") in ("image", "footage") and not (r.get("attribution") or "").strip():
            errors.append(f"{where}: {r['type']} needs an attribution")
        if XTTS.search(r.get("item") or ""):
            if r.get("status") not in ("rejected", "test_only"):
                errors.append(f"{where}: XTTS (non-commercial CPML) must be rejected or test_only")
            if "film cut" in (r.get("used_in") or "").lower():
                errors.append(f"{where}: XTTS must not be used in a film cut")
    return errors


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"header must be {','.join(COLUMNS)}, got {reader.fieldnames}")
        return [dict(r) for r in reader]


@app.callback()
def _main() -> None:
    """Rights log checks."""


@app.command()
def check(rights_csv: Path) -> None:
    """Validate the rights log; exit 1 on any error."""
    try:
        rows = read_rows(rights_csv)
    except (OSError, ValueError) as exc:
        typer.echo(f"FAIL {rights_csv}: {exc}")
        raise typer.Exit(1) from exc
    errors = check_rows(rows)
    for e in errors:
        typer.echo(f"FAIL {e}")
    if errors:
        typer.echo(f"film.rights check FAIL: {len(errors)} error(s) in {len(rows)} rows")
        raise typer.Exit(1)
    by_status = Counter(r["status"] for r in rows)
    parts = ", ".join(f"{s} {by_status[s]}" for s in STATUSES if by_status[s])
    typer.echo(f"film.rights check PASS: {len(rows)} rows ({parts})")


if __name__ == "__main__":
    app()
