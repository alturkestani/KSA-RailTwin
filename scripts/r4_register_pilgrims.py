# ruff: noqa: E501
"""Register the 44 pilgrim files in the data manifest (R4, prompts/R4.md 'international-visitor segment').

Reads data/ksa/tables/pilgrims/sources.csv (url, retrieval time, licence, sha256 per file, written by
the coordinator) and appends one manifest row per file with `common.manifest add`, then checks that
the recomputed SHA-256 equals the one in sources.csv. Idempotent: rows already present are skipped.

  uv run python scripts/r4_register_pilgrims.py
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIR = Path("data/ksa/tables/pilgrims")


def slug(name: str) -> str:
    s = "".join(c.lower() if c.isalnum() else "-" for c in Path(name).name)
    while "--" in s:
        s = s.replace("--", "-")
    return "pilgrims-" + s.strip("-")


def main() -> int:
    man = yaml.safe_load((ROOT / "cities/ksa/sources.yaml").read_text(encoding="utf-8"))
    have = {r["id"] for r in (man if isinstance(man, list) else man.get("sources", man))}
    rows = list(csv.DictReader((ROOT / DIR / "sources.csv").open(encoding="utf-8")))
    bad = 0
    for r in rows:
        p = DIR / r["file_name"]
        sha = hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
        if sha != r["sha256"]:
            print(f"HASH MISMATCH {p}: {sha} vs {r['sha256']}")
            bad += 1
            continue
        rid = slug(r["file_name"])
        if rid in have:
            continue
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "common.manifest",
                "add",
                "--id",
                rid,
                "--name",
                f"{r['title']} ({r['file_name']})",
                "--publisher",
                r["publisher"],
                "--url",
                r["source_url"],
                "--edition",
                r["reference_period"],
                "--licence",
                r["licence_or_terms"],
                "--path",
                str(p),
                "--used-in",
                "W8,demand.intl,docs/network-evaluation.md",
                "--accessed",
                r["retrieved_at_utc"][:10],
                "--notes",
                f"{r['primary_or_relayed']}; {r['metric']}; {r['notes']}".strip("; "),
            ],
            check=True,
            cwd=ROOT,
        )
    for extra, name in (("sources.csv", "per-file source table"), ("README.md", "README")):
        rid = slug(extra)
        if rid not in have:
            subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "common.manifest",
                    "add",
                    "--id",
                    rid,
                    "--name",
                    f"Pilgrim arrivals tables: {name} (coordinator, 31 Oct 2026)",
                    "--publisher",
                    "KSA Rail Twin coordinator (derived listing of GASTAT/GACA/SPA files)",
                    "--url",
                    "n/a (local listing)",
                    "--edition",
                    "2026-10-31",
                    "--licence",
                    "Apache-2.0 (project text); cites GASTAT/GACA/SPA",
                    "--path",
                    str(DIR / extra),
                    "--used-in",
                    "W8,demand.intl",
                    "--accessed",
                    "2026-10-31",
                ],
                check=True,
                cwd=ROOT,
            )
    print(f"{len(rows)} files checked, {bad} hash mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
