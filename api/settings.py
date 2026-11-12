"""Settings read at call time from the environment (pattern from TrafficTwin `api/settings.py`).

RAILTWIN_DATA_ROOT: the tree that holds `cities/ksa/` and `scenarios/` (default: the repo root;
tests point it at `tests/fixtures/api`). RAILTWIN_RUNS_ROOT: the run outputs (default
`<data root>/runs`; tests use `tests/fixtures/api/run_outputs`, because `runs/` is gitignored at
every depth). RAILTWIN_WEB_DIST: the built web app to serve at `/`
(default `web/dist`). Relative paths resolve against the repo root; no absolute host paths.
"""

from __future__ import annotations

import os
from pathlib import Path

from common import REPO_ROOT

CORS_ORIGINS_DEFAULT = "http://localhost:5173"


def _path(env: str, default: Path) -> Path:
    raw = os.environ.get(env)
    if not raw:
        return default
    path = Path(raw).expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def data_root() -> Path:
    """RAILTWIN_DATA_ROOT, default the repo root."""
    return _path("RAILTWIN_DATA_ROOT", REPO_ROOT)


def runs_root() -> Path:
    """RAILTWIN_RUNS_ROOT, default <data root>/runs (fixtures: tests/fixtures/api/run_outputs)."""
    return _path("RAILTWIN_RUNS_ROOT", data_root() / "runs")


def web_dist() -> Path:
    """RAILTWIN_WEB_DIST, default <repo>/web/dist."""
    return _path("RAILTWIN_WEB_DIST", REPO_ROOT / "web" / "dist")


def cors_origins() -> list[str]:
    raw = os.environ.get("RAILTWIN_CORS_ORIGINS", CORS_ORIGINS_DEFAULT)
    return [o.strip() for o in raw.split(",") if o.strip()]
