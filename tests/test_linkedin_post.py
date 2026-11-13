"""PUBLISH_PDF_POST (Tariq, 13 Nov 2026): the LinkedIn post draft
(docs/publish/linkedin-method-findings.md): length, hashtags, no links in the body, plain words,
the project label, and the first comment's links."""

from __future__ import annotations

import re

from common import REPO_ROOT
from film import cards

DOC = (REPO_ROOT / "docs/publish/linkedin-method-findings.md").read_text(encoding="utf-8")


def _block(heading: str) -> str:
    m = re.search(rf"^## {heading}\n\n```text\n(.*?)\n```", DOC, re.M | re.S)
    assert m, heading
    return m.group(1)


POST = _block("Post")
COMMENT = _block("First comment")


def test_length_and_stated_count() -> None:
    assert 1300 <= len(POST) <= 2000
    assert f"**{len(POST):,} characters**" in DOC


def test_hashtags_links_and_jargon() -> None:
    assert len(re.findall(r"#\w+", POST)) <= 3
    assert "http" not in POST and "github.com" not in POST
    assert cards.jargon_hits(POST) == [] and cards.jargon_hits(COMMENT) == []


def test_label_and_first_comment() -> None:
    label = "synthetic demand, uncalibrated: scenario comparison, not a forecast"
    assert label in POST and label in COMMENT.lower()
    assert "https://github.com/alturkestani/KSA-RailTwin" in COMMENT
    assert "feasibility-report.pdf" in COMMENT
