"""R9: docs/credits.md and the generated NOTICE block cover every licence-register item."""

from __future__ import annotations

from common import REPO_ROOT
from common.licences import (
    NOTICE_BEGIN,
    NOTICE_END,
    needs_attribution,
    register,
    render_credits,
    render_notice_block,
)


def test_credits_file_is_current_and_covers_every_item() -> None:
    have = (REPO_ROOT / "docs/credits.md").read_text(encoding="utf-8")
    assert have == render_credits()
    rows = register()
    table = [ln for ln in have.splitlines() if ln.startswith("| ") and ln[2:3].isdigit()]
    assert len(table) == len(rows)
    assert "claude-" not in have  # model ids stay in the private register rows


def test_notice_block_is_current_and_lists_every_attribution() -> None:
    notice = (REPO_ROOT / "NOTICE").read_text(encoding="utf-8")
    block = notice[notice.index(NOTICE_BEGIN) : notice.index(NOTICE_END) + len(NOTICE_END)]
    assert block == render_notice_block()
    n = sum(needs_attribution(r) for r in register())
    assert sum(ln.startswith("- ") for ln in block.splitlines()) == n
    assert "/Users/" not in notice
