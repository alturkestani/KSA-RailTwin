"""R8 closures of verify-R7 observations that are checked on the committed files."""

from __future__ import annotations

import collections
import csv

from common import REPO_ROOT


def test_source_index_ids_unique():
    """verify-R7 O10: one row per id in the canonical index (S-fund-016 kept once)."""
    rows = list(csv.DictReader((REPO_ROOT / "docs/sources/index.csv").open(encoding="utf-8")))
    dup = [k for k, v in collections.Counter(r["id"] for r in rows).items() if v > 1]
    assert dup == []
    assert sum(r["id"] == "S-fund-016" for r in rows) == 1


def test_fiscal_doc_carries_o7_o8_o11_notes():
    doc = (REPO_ROOT / "docs/fiscal-exposure.md").read_text(encoding="utf-8")
    assert "Timing note (verify-R7 O7" in doc
    assert "sorted values of the three runs at capex P10, P50 and P90" in doc
    assert "sourced, reference class — unclear for Saudi Arabia" in doc


def test_template_art18_note_is_usage_fees_only():
    """verify-R7 O17."""
    t = (REPO_ROOT / "cities/ksa/funding/risk_matrix_template.yaml").read_text(encoding="utf-8")
    assert "usage (access) fees under use agreements only" in t
