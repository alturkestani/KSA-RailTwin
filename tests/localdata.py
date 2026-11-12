"""Skip markers for tests that read gitignored local inputs (runs/, data/), absent in a fresh
clone and in CI (R9 clean-clone check)."""

from __future__ import annotations

import pytest

from common import REPO_ROOT

# Run metas that common.figures.provenance and the study tests read.
STUDY_RUNS = (
    "runs/cba/CBA-S1-committed-programme/meta.json",
    "runs/r6/top5/L1/meta.json",
    "runs/r7/fiscal/meta.json",
    "runs/r2/score/meta.json",
    "runs/access/S1/meta.json",
    "runs/r6/l6/meta.json",
)


def needs_local(*rel: str) -> pytest.MarkDecorator:
    """Skip when any of the repo-relative paths is missing."""
    missing = [r for r in rel if not (REPO_ROOT / r).exists()]
    return pytest.mark.skipif(bool(missing), reason=f"local gitignored inputs missing: {missing}")
