"""Run metadata (rule 10): every run writes `meta.json` with seed, config hash, data hash
(the manifest's SHA-256), code version (`git describe --always --dirty`), tool versions and a UTC
timestamp.

Library: `write_meta(run_dir, seed, config, extra)`, `config_hash`, `seed_option`, `rng`.
CLI:
  uv run python -m common.runmeta config-hash <file.yaml>
  uv run python -m common.runmeta show <run_dir>
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.metadata as md
import json
import platform
import random
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import typer
import yaml

from common import REPO_ROOT
from common.labels import LABEL
from common.manifest import DEFAULT_MANIFEST, manifest_hash

PACKAGES = [
    "pyyaml",
    "pydantic",
    "numpy",
    "pandas",
    "pyarrow",
    "duckdb",
    "shapely",
    "pyproj",
    "geopandas",
    "networkx",
    "typer",
    "scipy",
]

app = typer.Typer(add_completion=False, help="Run metadata: config hashes and meta.json.")


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def config_hash(config: Any) -> str:
    """SHA-256 of the canonical JSON of a config (key order does not matter)."""
    return hashlib.sha256(canonical_json(config).encode("utf-8")).hexdigest()


def code_version(root: Path = REPO_ROOT) -> str:
    try:
        out = subprocess.run(
            ["git", "describe", "--always", "--dirty"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def tool_versions(packages: list[str] = PACKAGES) -> dict[str, str]:
    versions = {"python": platform.python_version()}
    for p in packages:
        try:
            versions[p] = md.version(p)
        except md.PackageNotFoundError:
            versions[p] = "not installed"
    return versions


def build_meta(
    seed: int,
    config: Any,
    extra: dict[str, Any] | None = None,
    manifest: Path = DEFAULT_MANIFEST,
) -> dict[str, Any]:
    meta = {
        "seed": seed,
        "config_hash": config_hash(config),
        "data_hash": manifest_hash(manifest),
        "code_version": code_version(),
        "tool_versions": tool_versions(),
        "label": LABEL,
        "created_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }
    if extra:
        meta.update(extra)
    return meta


def write_meta(
    run_dir: Path,
    seed: int,
    config: Any,
    extra: dict[str, Any] | None = None,
    manifest: Path = DEFAULT_MANIFEST,
) -> Path:
    """Write `<run_dir>/meta.json`; `extra` may add e.g. `assumptions: [A-...]`."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "meta.json"
    meta = build_meta(seed, config, extra, manifest)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def seed_option(default: int = 1) -> Any:
    """Shared `--seed` option for typer CLIs: `seed: int = seed_option()`."""
    return typer.Option(default, "--seed", min=0, help="random seed (recorded in meta.json)")


def rng(seed: int) -> np.random.Generator:
    """Seed Python's `random` and return a NumPy Generator; use the Generator, not global state."""
    random.seed(seed)
    return np.random.default_rng(seed)


@app.command("config-hash")
def config_hash_cmd(path: Path) -> None:
    """Print the config hash of a YAML or JSON file."""
    typer.echo(config_hash(yaml.safe_load(path.read_text(encoding="utf-8"))))


@app.command()
def show(run_dir: Path) -> None:
    """Print a run's meta.json."""
    typer.echo((run_dir / "meta.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    app()
