"""Write docs/licences-r4.md from docs/licences-r4.csv (R4 track licence fragment; same columns as
docs/licences.md). Edit the CSV, then run: uv run python scripts/r4_licences.py"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEAD = (
    "> **Document version:** docs/licences-r4.md v{ver} | 1 Nov 2026 | Author: R4 builder "
    "(sim-engineer, gis-network-engineer) | Status: draft\n\n# Licence & openness register: R4 "
    "fragment\n\nTrack fragment in the format of `docs/licences.md` (rule 12); INTEGRATE_R4 merges "
    "it. Machine-readable copy: `docs/licences-r4.csv`.\n\n"
)


def main(ver: str = "1.0") -> None:
    rows = list(csv.reader((ROOT / "docs/licences-r4.csv").open(encoding="utf-8")))
    out = [HEAD.format(ver=ver), "| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
    out += ["| " + " | ".join(c.replace("|", "/") for c in r) + " |" for r in rows[1:]]
    (ROOT / "docs/licences-r4.md").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "1.0")
