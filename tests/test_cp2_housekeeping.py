"""CP2_PREP housekeeping: licence MD mirrors the CSV; no fragments; no model ids in docs."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from common import REPO_ROOT
from common.licences import diff_count, sync

MODEL_ID = re.compile(r"claude-(fable|opus|haiku|sonnet)-\d")


def test_licence_markdown_matches_csv() -> None:
    n_md, n_csv, diff = diff_count(REPO_ROOT)
    assert n_md == n_csv and diff == 0


def test_sync_rewrites_differing_row(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    for f in ("licences.csv", "licences.md"):
        shutil.copy(REPO_ROOT / "docs" / f, tmp_path / "docs" / f)
    md = tmp_path / "docs/licences.md"
    lines = md.read_text(encoding="utf-8").split("\n")
    i = next(k for k, ln in enumerate(lines) if ln.startswith("| item | version |")) + 2
    lines[i] = lines[i].replace("|", "| edited", 1)
    md.write_text("\n".join(lines), encoding="utf-8")
    assert diff_count(tmp_path)[2] == 1
    sync(root=tmp_path)
    assert diff_count(tmp_path)[2] == 0


def test_no_track_fragments_left() -> None:
    docs = REPO_ROOT / "docs"
    left = [*docs.glob("assumptions-pilot-*.md"), *docs.glob("licences-pilot-*")]
    left += [*docs.glob("licences-datascout.*")]
    assert left == []


def test_no_model_ids_in_docs_outside_records() -> None:
    """Model ids stay in CLAUDE.md, agent files, the cost log, the licence row for Claude Code and
    the run records (docs/STATUS.md, docs/status/); never in the deliverable documents."""
    allowed = {"docs/STATUS.md", "docs/cost-log.md", "docs/licences.md"}
    hits = []
    for p in (REPO_ROOT / "docs").rglob("*.md"):
        rel = p.relative_to(REPO_ROOT).as_posix()
        if rel in allowed or rel.startswith("docs/status/"):
            continue
        if MODEL_ID.search(p.read_text(encoding="utf-8")):
            hits.append(rel)
    assert hits == []
