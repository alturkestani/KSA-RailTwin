"""Document version headers (source versioning layer 3).

Every `.md` under docs/, prompts/, .claude/ and film/script/ begins (after optional YAML front
matter) with:
  > **Document version:** <name> v<major.minor> | <date> | Author: <agent or person> | Status: <...>

CLI:
  uv run python -m common.docver check [paths ...]     (default: docs prompts .claude film/script)
  uv run python -m common.docver bump <file> [--major]  (minor + 1, date = today)
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import typer

from common import REPO_ROOT

DEFAULT_PATHS = ["docs", "prompts", ".claude", "film/script"]
HEADER = re.compile(
    r"^> \*\*Document version:\*\* (?P<name>\S.*?) v(?P<major>\d+)\.(?P<minor>\d+)"
    r"(?P<suffix>[^|]*)\| (?P<date>[^|]+?) \| Author: (?P<author>[^|]+?)"
    r" \| Status: (?P<status>\S.*)$"
)
DATE = re.compile(r"^(\d{1,2} [A-Z][a-z]{2} \d{4}|\d{4}-\d{2}-\d{2})")

app = typer.Typer(add_completion=False, help="Check and bump document version headers.")


def header_line(text: str) -> tuple[int, str] | None:
    """Index and text of the first content line after optional YAML front matter."""
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        try:
            i = lines.index("---", 1) + 1
        except ValueError:
            return None
    while i < len(lines) and not lines[i].strip():
        i += 1
    return (i, lines[i]) if i < len(lines) else None


def check_file(path: Path) -> str | None:
    """None if the header is valid, else the problem."""
    found = header_line(path.read_text(encoding="utf-8"))
    if found is None:
        return "empty file or unterminated front matter"
    m = HEADER.match(found[1])
    if not m:
        return f"line {found[0] + 1} is not a version header"
    if not DATE.match(m["date"]):
        return f"bad date {m['date']!r}"
    return None


def _in_worktree(f: Path, root: Path) -> bool:
    """True under `<root>/.worktrees/`; a checkout that itself sits in one is not skipped."""
    try:
        rel = f.resolve().relative_to(root.resolve()).parts
    except ValueError:
        rel = f.parts
    return ".worktrees" in rel


def iter_md(paths: list[str], root: Path = REPO_ROOT) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        target = Path(p) if Path(p).is_absolute() else root / p
        if target.is_file() and target.suffix == ".md":
            files.append(target)
        elif target.is_dir():
            files += sorted(f for f in target.rglob("*.md") if not _in_worktree(f, root))
    return files


def bump_text(text: str, major: bool = False, today: dt.date | None = None) -> str:
    found = header_line(text)
    if found is None or not HEADER.match(found[1]):
        raise ValueError("no version header to bump")
    i, line = found
    m = HEADER.match(line)
    assert m is not None
    ma, mi = int(m["major"]), int(m["minor"])
    ma, mi = (ma + 1, 0) if major else (ma, mi + 1)
    day = today or dt.date.today()
    date = day.isoformat() if re.match(r"\d{4}-", m["date"]) else day.strftime("%-d %b %Y")
    new = (
        f"> **Document version:** {m['name']} v{ma}.{mi}{m['suffix']}| {date} | "
        f"Author: {m['author']} | Status: {m['status']}"
    )
    lines = text.splitlines(keepends=True)
    end = "\n" if lines[i].endswith("\n") else ""
    lines[i] = new + end
    return "".join(lines)


@app.command()
def check(paths: list[str] = typer.Argument(None)) -> None:
    """Fail if any Markdown file under the paths lacks a valid version header."""
    files = iter_md(paths or DEFAULT_PATHS)
    bad = [(f, p) for f in files if (p := check_file(f))]
    for f, p in bad:
        typer.echo(f"FAIL {f.relative_to(REPO_ROOT) if f.is_relative_to(REPO_ROOT) else f}: {p}")
    if bad:
        raise typer.Exit(1)
    typer.echo(f"docver OK: {len(files)} files")


@app.command()
def bump(file: Path, major: bool = typer.Option(False, "--major")) -> None:
    """Increment the minor (or major) version and set today's date."""
    file.write_text(bump_text(file.read_text(encoding="utf-8"), major), encoding="utf-8")
    typer.echo(header_line(file.read_text(encoding="utf-8"))[1])  # type: ignore[index]


if __name__ == "__main__":
    app()
