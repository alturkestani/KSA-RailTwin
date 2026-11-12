"""Source-id lookup for the funding registers: every `S-...` id cited must have a row in a
`docs/sources/*.csv` file (the index or a track file such as `r1d-fund.csv`)."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from common import REPO_ROOT

SOURCES_DIR = REPO_ROOT / "docs" / "sources"
SOURCE_ID = re.compile(r"^S-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")


def known_source_ids(sources_dir: Path = SOURCES_DIR) -> set[str]:
    ids: set[str] = set()
    for path in sorted(Path(sources_dir).glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "id" not in reader.fieldnames:
                continue
            ids.update(row["id"].strip() for row in reader if (row.get("id") or "").strip())
    return ids


def unknown_ids(cited: list[str], known: set[str]) -> list[str]:
    return sorted({s for s in cited if s not in known})
