"""Data manifest (source versioning layer 2): `cities/ksa/sources.yaml`.

CLI:
  uv run python -m common.manifest add --id ... --name ... --publisher ... --url ... --edition ...
      --licence ... --path data/... [--used-in a,b] [--accessed YYYY-MM-DD] [--notes "..."]
  uv run python -m common.manifest verify [--allow-missing]
  uv run python -m common.manifest hash
"""

from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
from typing import Any

import typer
import yaml

from common import REPO_ROOT

DEFAULT_MANIFEST = REPO_ROOT / "cities" / "ksa" / "sources.yaml"
FIELDS = [
    "id",
    "name",
    "publisher",
    "url",
    "edition",
    "licence",
    "accessed",
    "sha256",
    "bytes",
    "local_path",
    "used_in",
    "notes",
]
REQUIRED = ["id", "name", "publisher", "url", "edition", "licence", "accessed"]
LOCAL_REQUIRED = ["sha256", "bytes"]

app = typer.Typer(add_completion=False, help="Data manifest: add, verify, hash.")


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def _header(path: Path) -> list[str]:
    """Leading comment lines of the manifest, kept on rewrite."""
    if not path.exists():
        return []
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            lines.append(line)
        else:
            break
    return lines


def load(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    if not path.exists():
        return {"manifest_version": 1, "sources": []}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("manifest_version", 1)
    data["sources"] = data.get("sources") or []
    return data


def save(data: dict[str, Any], path: Path = DEFAULT_MANIFEST) -> None:
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
    head = "\n".join(_header(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((head + "\n" if head else "") + body, encoding="utf-8")


def relative_path(path: Path, root: Path) -> str:
    """Store paths relative to the repo root; refuse paths outside it (no home paths)."""
    # symlinks are kept as written (data/osm -> TrafficTwin): never resolve them here
    p = path if path.is_absolute() else root / path
    try:
        return p.relative_to(root).as_posix()
    except ValueError:
        raise typer.BadParameter(f"{path} is outside the repo; use data/...") from None


def add_row(
    *,
    manifest: Path,
    root: Path,
    id: str,
    name: str,
    publisher: str,
    url: str,
    edition: str,
    licence: str,
    path: Path,
    used_in: list[str],
    accessed: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    data = load(manifest)
    if any(r.get("id") == id for r in data["sources"]):
        raise ValueError(f"id {id!r} already in {manifest}; a new edition needs a new id")
    rel = relative_path(path, root)
    target = root / rel
    if not target.is_file():
        raise FileNotFoundError(f"{rel} not found")
    row = {
        "id": id,
        "name": name,
        "publisher": publisher,
        "url": url,
        "edition": str(edition),
        "licence": licence,
        "accessed": accessed or dt.date.today().isoformat(),
        "sha256": sha256_file(target),
        "bytes": target.stat().st_size,
        "local_path": rel,
        "used_in": used_in,
        "notes": notes,
    }
    data["sources"].append(row)
    save(data, manifest)
    return row


def verify_rows(manifest: Path, root: Path, allow_missing: bool = False) -> list[str]:
    """Return a list of problems (empty = verified)."""
    problems: list[str] = []
    data = load(manifest)
    seen: set[str] = set()
    for i, row in enumerate(data["sources"]):
        rid = row.get("id") or f"<row {i}>"
        if rid in seen:
            problems.append(f"{rid}: duplicate id")
        seen.add(rid)
        for field in REQUIRED:
            if row.get(field) in (None, ""):
                problems.append(f"{rid}: missing field {field}")
        for field in FIELDS:
            if field not in row:
                problems.append(f"{rid}: field {field} absent (use null or empty)")
        lp = row.get("local_path")
        if not lp:
            continue
        if Path(lp).is_absolute():
            problems.append(f"{rid}: local_path must be relative ({lp})")
            continue
        for field in LOCAL_REQUIRED:
            if row.get(field) in (None, ""):
                problems.append(f"{rid}: missing field {field}")
        target = root / lp
        if not target.is_file():
            if not allow_missing:
                problems.append(f"{rid}: file missing at {lp}")
            continue
        size = target.stat().st_size
        if row.get("bytes") is not None and size != row["bytes"]:
            problems.append(f"{rid}: bytes {size} != manifest {row['bytes']}")
            continue
        if row.get("sha256") and sha256_file(target) != row["sha256"]:
            problems.append(f"{rid}: sha256 mismatch at {lp}")
    return problems


def manifest_hash(manifest: Path = DEFAULT_MANIFEST) -> str:
    return sha256_file(manifest) if manifest.exists() else ""


@app.command()
def add(
    id: str = typer.Option(..., "--id"),
    name: str = typer.Option(..., "--name"),
    publisher: str = typer.Option(..., "--publisher"),
    url: str = typer.Option(..., "--url"),
    edition: str = typer.Option(..., "--edition"),
    licence: str = typer.Option(..., "--licence"),
    path: Path = typer.Option(..., "--path", help="file under the repo (may be a symlink)"),
    used_in: str = typer.Option("", "--used-in", help="comma-separated packages or workstreams"),
    accessed: str = typer.Option(None, "--accessed", help="YYYY-MM-DD; default today"),
    notes: str = typer.Option("", "--notes"),
    manifest: Path = typer.Option(DEFAULT_MANIFEST, "--manifest"),
    root: Path = typer.Option(REPO_ROOT, "--root"),
) -> None:
    """Hash a file and append a row (accessed = today unless --accessed is given)."""
    row = add_row(
        manifest=manifest,
        root=root,
        id=id,
        name=name,
        publisher=publisher,
        url=url,
        edition=edition,
        licence=licence,
        path=path,
        used_in=[u.strip() for u in used_in.split(",") if u.strip()],
        accessed=accessed,
        notes=notes,
    )
    typer.echo(f"added {row['id']}: {row['bytes']} bytes, sha256 {row['sha256']}")


@app.command()
def verify(
    manifest: Path = typer.Option(DEFAULT_MANIFEST, "--manifest"),
    root: Path = typer.Option(REPO_ROOT, "--root"),
    allow_missing: bool = typer.Option(
        False, "--allow-missing", help="skip rows whose file is absent (CI has no data/)"
    ),
) -> None:
    """Recompute every hash; exit 1 on a mismatch, missing field or (unless allowed) file."""
    problems = verify_rows(manifest, root, allow_missing)
    n = len(load(manifest)["sources"])
    if problems:
        for p in problems:
            typer.echo(f"FAIL {p}", err=True)
        raise typer.Exit(1)
    typer.echo(f"manifest OK: {n} rows")


@app.command("hash")
def hash_cmd(manifest: Path = typer.Option(DEFAULT_MANIFEST, "--manifest")) -> None:
    """Print the manifest's own SHA-256 (recorded as data_hash in meta.json)."""
    typer.echo(manifest_hash(manifest))


if __name__ == "__main__":
    app()
