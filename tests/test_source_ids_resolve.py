"""Every source id cited in the rail line/station files and the CP2 population docs exists in
docs/sources/index.csv, and index ids are unique (VERIFY_CP2_PREP F1: S-cp2-607 had been lost when
the GASTAT rows reused the S-cp2-60x ids)."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "sources" / "index.csv"
ID = re.compile(r"\bS-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b")
# placeholders and words that match the pattern but are not ids
NOT_IDS = {"S-curve", "S-cost-rcf"}
FILES = [
    *sorted((ROOT / "cities" / "ksa" / "lines").glob("*.geojson")),
    *sorted((ROOT / "cities" / "ksa" / "lines").glob("*.yaml")),
    ROOT / "rail" / "station_research.yaml",
    ROOT / "docs" / "network.md",
    ROOT / "docs" / "screening-pilot.md",
    ROOT / "docs" / "geo-verify.md",
    ROOT / "docs" / "coverage.md",
    ROOT / "docs" / "sources" / "conflicts.md",
]


def _ids() -> list[str]:
    with INDEX.open(encoding="utf-8") as fh:
        return [r["id"] for r in csv.DictReader(fh)]


def test_index_ids_unique() -> None:
    ids = _ids()
    assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_cited_source_ids_resolve(path: Path) -> None:
    known = set(_ids())
    cited = {m for m in ID.findall(path.read_text(encoding="utf-8")) if "xx" not in m}
    missing = sorted(cited - known - NOT_IDS)
    assert not missing, missing
