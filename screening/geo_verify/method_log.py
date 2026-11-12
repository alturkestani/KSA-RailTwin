"""Append-only JSONL method log: one entry per derived value (skill section 4)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def entry_id(kind: str, key: str) -> str:
    """Stable id from kind and key, e.g. `geo-est-3f2a9c1d`."""
    return f"geo-{kind}-" + hashlib.sha256(f"{kind}:{key}".encode()).hexdigest()[:8]


def append(path: Path, entry: dict[str, Any]) -> str:
    """Append one entry (needs id, method, inputs, parameters, value, band, run_id)."""
    for k in ("id", "method", "inputs", "parameters", "value", "band", "run_id"):
        if k not in entry:
            raise ValueError(f"method-log entry lacks {k!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str) + "\n")
    return entry["id"]


def read(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
