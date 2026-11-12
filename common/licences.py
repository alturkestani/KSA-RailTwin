"""Licence register sync: `docs/licences.csv` is canonical; the Markdown table is generated from it.

CLI:
  uv run python -m common.licences check   (exit 1 if any Markdown row differs from the CSV)
  uv run python -m common.licences sync    (rewrite the Markdown table rows from the CSV)
  uv run python -m common.licences credits --out docs/credits.md   (R9: credits from the register,
      plus the Python dependency licences from uv.lock and the installed metadata and the
      JavaScript ones from web/package-lock.json; also rewrites the generated attribution block
      of NOTICE; `--check` exits 1 if either file is out of date)
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import typer

from common import REPO_ROOT

CSV = Path("docs/licences.csv")
MD = Path("docs/licences.md")
COLS = [
    "item",
    "version",
    "source_url",
    "licence",
    "open",
    "commercial_use",
    "attribution",
    "obligations",
    "used_in",
    "status",
    "approval",
]

app = typer.Typer(add_completion=False, help="Generate docs/licences.md rows from the CSV.")


def _cell(v: str) -> str:
    return " ".join((v or "").split()).replace("|", "\\|")


def csv_rows(root: Path = REPO_ROOT) -> list[str]:
    with (root / CSV).open(encoding="utf-8", newline="") as fh:
        return ["| " + " | ".join(_cell(r[c]) for c in COLS) + " |" for r in csv.DictReader(fh)]


def _table_span(lines: list[str]) -> tuple[int, int]:
    """Index of the first data row and one past the last row of the register table."""
    head = next(i for i, ln in enumerate(lines) if ln.startswith("| item | version |"))
    start = head + 2
    end = start
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    return start, end


def diff_count(root: Path = REPO_ROOT) -> tuple[int, int, int]:
    """(markdown rows, csv rows, differing row pairs by position)."""
    lines = (root / MD).read_text(encoding="utf-8").split("\n")
    start, end = _table_span(lines)
    md, cs = lines[start:end], csv_rows(root)
    diff = sum(1 for a, b in zip(md, cs, strict=False) if a != b) + abs(len(md) - len(cs))
    return len(md), len(cs), diff


@app.command()
def check(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Report Markdown rows that differ from the CSV."""
    n_md, n_csv, diff = diff_count(root)
    typer.echo(f"licences: {n_md} Markdown rows, {n_csv} CSV rows, {diff} differ")
    if diff:
        sys.exit(1)


@app.command()
def sync(root: Path = typer.Option(REPO_ROOT, hidden=True)) -> None:
    """Rewrite the Markdown table rows from the CSV (the CSV is canonical)."""
    p = root / MD
    lines = p.read_text(encoding="utf-8").split("\n")
    start, end = _table_span(lines)
    before = diff_count(root)[2]
    p.write_text("\n".join(lines[:start] + csv_rows(root) + lines[end:]), encoding="utf-8")
    typer.echo(f"licences: {before} differing rows rewritten from the CSV")


# --------------------------------------------------------------------------- credits (R9)
CREDITS = Path("docs/credits.md")
NOTICE = Path("NOTICE")
NOTICE_BEGIN = "--- BEGIN GENERATED ATTRIBUTIONS (uv run python -m common.licences credits) ---"
NOTICE_END = "--- END GENERATED ATTRIBUTIONS ---"
CREDITS_VERSION = "1.0"
CREDITS_DATE = "7 Nov 2026"
_NO_ATTRIBUTION = ("", "none", "n/a", "none required", "none required (courtesy credit)")


def register(root: Path = REPO_ROOT) -> list[dict[str, str]]:
    from common.sources import redact_model_ids

    with (root / CSV).open(encoding="utf-8", newline="") as fh:
        return [{k: redact_model_ids(v or "") for k, v in r.items()} for r in csv.DictReader(fh)]


def needs_attribution(r: dict[str, str]) -> bool:
    return " ".join(r["attribution"].split()).strip().lower() not in _NO_ATTRIBUTION


def _pkg_licence(name: str) -> str:
    import importlib.metadata as md

    try:
        m = md.metadata(name)
    except md.PackageNotFoundError:
        return "not installed on this platform (see the package on PyPI)"
    expr = m.get("License-Expression")
    if expr:
        return expr
    cls = [
        c.split("::")[-1].strip() for c in m.get_all("Classifier") or [] if c.startswith("License")
    ]
    if cls:
        return "; ".join(cls)
    lic = (m.get("License") or "").strip()
    return lic if lic and len(lic) <= 60 and "\n" not in lic else "see the package metadata"


def python_packages(root: Path = REPO_ROOT) -> list[tuple[str, str, str]]:
    import tomllib

    lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    own = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["name"]
    out = [
        (p["name"], p.get("version", ""), _pkg_licence(p["name"]))
        for p in lock.get("package", [])
        if p["name"] != own
    ]
    return sorted(out)


def js_packages(root: Path = REPO_ROOT) -> list[tuple[str, str, str]]:
    import json

    lock = json.loads((root / "web" / "package-lock.json").read_text(encoding="utf-8"))
    out = {}
    for k, v in lock.get("packages", {}).items():
        if not k:
            continue
        name = k.split("node_modules/")[-1]
        dev = " (dev)" if v.get("dev") else ""
        out[(name, v.get("version", ""))] = (v.get("license") or "not stated in the lock") + dev
    return sorted((n, ver, lic) for (n, ver), lic in out.items())


def _summary(pkgs: list[tuple[str, str, str]]) -> str:
    from collections import Counter

    c = Counter(lic for _, _, lic in pkgs)
    return "; ".join(f"{lic}: {n}" for lic, n in sorted(c.items(), key=lambda x: (-x[1], x[0])))


def render_credits(root: Path = REPO_ROOT) -> str:
    rows = register(root)
    py, js = python_packages(root), js_packages(root)
    n_att = sum(needs_attribution(r) for r in rows)
    out = [
        f"> **Document version:** docs/credits.md v{CREDITS_VERSION} | {CREDITS_DATE} | Author: R9 "
        "(generated by `uv run python -m common.licences credits --out docs/credits.md`) | "
        "Status: draft",
        "",
        "# Credits",
        "",
        "Generated from the licence and openness register (`docs/licences.csv`, canonical; "
        "`docs/licences.md` is its table), from `uv.lock` with the installed package metadata, "
        "and from `web/package-lock.json`. Do not edit by hand: change the register and re-run "
        "`make credits`. The release status of every item (BLOCKER, VERIFY, OBLIGATIONS, "
        "COMPATIBLE, NOT IN RELEASE) is in `docs/licences-release.md`; the open blockers are "
        "listed in `docs/licences-blockers.md`. An item listed here is credited, not cleared for "
        "release.",
        "",
        f"Register items: {len(rows)}; items whose register row names an attribution: {n_att} "
        "(also reproduced in the generated block at the end of `NOTICE`). Python packages in "
        f"`uv.lock`: {len(py)}. JavaScript packages in `web/package-lock.json`: {len(js)}.",
        "",
        "Map and network data: (c) OpenStreetMap contributors, ODbL 1.0, via Geofabrik. "
        "Statistics: GASTAT open data, credited; derived tables are marked as derived and are "
        "not official statistics. Parent project: TrafficTwin Jeddah (Apache-2.0). All modelled "
        'results are labelled "synthetic demand, uncalibrated: scenario comparison, not a '
        'forecast".',
        "",
        "## 1. Register items (datasets, models, tools, voices, fonts, music, images)",
        "",
        "| # | item | version | licence | open | attribution required | obligations | used in |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        cells = [r["item"], r["version"], r["licence"], r["open"], r["attribution"]]
        cells += [r["obligations"], r["used_in"]]
        out.append(f"| {i} | " + " | ".join(_cell(c) for c in cells) + " |")
    for title, pkgs, note in (
        (
            "## 2. Python dependencies (uv.lock)",
            py,
            "Licence from the installed package metadata (License-Expression, then License, then "
            "the trove classifiers); installed by `uv sync`, not vendored. Dev only: ruff, pytest.",
        ),
        (
            "## 3. JavaScript dependencies (web/package-lock.json)",
            js,
            "Licence as recorded in the lock file; `(dev)` marks build-only packages. Installed by "
            "`npm ci` in `web/`, not vendored; the runtime packages are bundled into `web/dist` "
            "(not committed).",
        ),
    ):
        out += ["", title, "", note, "", f"Summary: {_summary(pkgs)}.", ""]
        out += ["| package | version | licence |", "|---|---|---|"]
        out += [f"| {_cell(n)} | {_cell(v)} | {_cell(lic)} |" for n, v, lic in pkgs]
    return "\n".join(out) + "\n"


def render_notice_block(root: Path = REPO_ROOT) -> str:
    import textwrap

    lines = [
        NOTICE_BEGIN,
        "Every register item whose row names an attribution (docs/licences.csv; full credits",
        "with versions, licences and obligations: docs/credits.md). Listing is not clearance:",
        "release status per item is in docs/licences-release.md.",
        "",
    ]
    for r in register(root):
        if not needs_attribution(r):
            continue
        text = f"- {' '.join(r['item'].split())} [{' '.join(r['licence'].split())}]: "
        text += " ".join(r["attribution"].split())
        lines += textwrap.wrap(text, 98, subsequent_indent="  ", break_on_hyphens=False)
    lines.append(NOTICE_END)
    return "\n".join(lines)


def _notice_with_block(root: Path) -> str:
    text = (root / NOTICE).read_text(encoding="utf-8")
    block = render_notice_block(root)
    if NOTICE_BEGIN in text:
        head = text[: text.index(NOTICE_BEGIN)]
        tail = text[text.index(NOTICE_END) + len(NOTICE_END) :]
        return head + block + tail
    return text.rstrip("\n") + "\n\n" + block + "\n"


@app.command()
def credits(
    out: Path = typer.Option(CREDITS, "--out"),
    check_only: bool = typer.Option(False, "--check", help="exit 1 if out of date"),
    root: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Write docs/credits.md and the generated attribution block of NOTICE from the register."""
    target = out if out.is_absolute() else root / out
    want_c, want_n = render_credits(root), _notice_with_block(root)
    if check_only:
        have_c = target.read_text(encoding="utf-8") if target.exists() else ""
        have_n = (root / NOTICE).read_text(encoding="utf-8")
        stale = [
            n for n, a, b in (("credits", have_c, want_c), ("NOTICE", have_n, want_n)) if a != b
        ]
        typer.echo(f"credits: {'out of date: ' + ', '.join(stale) if stale else 'up to date'}")
        if stale:
            sys.exit(1)
        return
    target.write_text(want_c, encoding="utf-8")
    (root / NOTICE).write_text(want_n, encoding="utf-8")
    typer.echo(f"credits: wrote {out} and the NOTICE attribution block")


if __name__ == "__main__":
    app()
