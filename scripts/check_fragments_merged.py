"""Check that every row of the pilot/datascout register fragments exists in the merged registers.

Usage: uv run python scripts/check_fragments_merged.py [--delete]
Assumption rows match by id (plain or scoped `<id> [<region>]`, as PILOT_MERGE wrote them);
licence rows match by (item, source URL) in docs/licences.csv. Exit 1 if any row is missing.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def md_rows(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| A-"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def main() -> int:
    merged = {r[0]: r[1:] for r in md_rows(DOCS / "assumptions.md")}
    lic = list(csv.DictReader((DOCS / "licences.csv").open(encoding="utf-8")))
    lic_keys = {(r["item"].strip(), r["source_url"].strip()) for r in lic}
    lic_urls = {r["source_url"].strip() for r in lic}
    checked = missing = 0
    frags = sorted(DOCS.glob("assumptions-pilot-*.md"))
    for f in frags:
        region = re.sub(r"^assumptions-pilot-|\.md$", "", f.name)
        for r in md_rows(f):
            checked += 1
            key = f"{r[0]} [{region}]"
            if key not in merged and r[0] not in merged:
                missing += 1
                print(f"MISSING assumption {key} ({f.name})")
    lfrags = sorted(DOCS.glob("licences-pilot-*.csv")) + sorted(DOCS.glob("licences-datascout.csv"))
    for f in lfrags:
        for r in csv.DictReader(f.open(encoding="utf-8")):
            checked += 1
            item, url = r["item"].strip(), (r.get("source_url") or "").strip()
            if (item, url) not in lic_keys and url not in lic_urls:
                missing += 1
                print(f"MISSING licence {item!r} ({f.name})")
    md_frags = sorted(DOCS.glob("licences-pilot-*.md")) + [DOCS / "licences-datascout.md"]
    print(
        f"fragments: {len(frags)} assumption, {len(lfrags)} licence CSV, "
        f"{sum(p.exists() for p in md_frags)} licence MD; "
        f"rows checked {checked}, missing {missing}"
    )
    if missing:
        return 1
    if "--delete" in sys.argv:
        for p in [*frags, *lfrags, *md_frags]:
            if p.exists():
                p.unlink()
        print("deleted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
