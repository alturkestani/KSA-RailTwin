"""R8 answer 5 and task 7: labels next to every length, cost, time or ridership table or figure,
no "will" in result sections, no model names, the S6-L1 risk statement, the L4/L5 rule."""

from __future__ import annotations

from pathlib import Path

import pytest

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL
from common.report import (
    LABEL_LINE,
    deliverables,
    l45_violations,
    label_violations,
    model_name_violations,
    run_checks,
    will_violations,
)

SECTIONS = sorted((REPO_ROOT / "docs/report/sections").glob("*.md"))
RESULT_SECTIONS = [f for f in SECTIONS if f.name[:2] in {"01", "04", "05", "06", "07"}]
FILES = deliverables()


def test_label_line_is_verbatim() -> None:
    assert LABEL in LABEL_LINE and ALIGNMENT_LIMITATION in LABEL_LINE
    assert LABEL_LINE.startswith("> Labels: ")


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_every_cost_length_time_ridership_table_or_figure_is_labelled(path: Path) -> None:
    assert label_violations(path.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("path", SECTIONS, ids=lambda p: p.name)
def test_every_section_carries_the_label_once(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert any(LABEL in ln and ALIGNMENT_LIMITATION in ln for ln in text.splitlines())


def test_label_rule_detects_a_missing_label() -> None:
    bad = "Text.\n\n| corridor | capex P50 (SAR m) |\n|---|---|\n| x | 1 |\n"
    assert label_violations(bad, require_once=False) != []
    good = f"{LABEL_LINE}\n| corridor | capex P50 (SAR m) |\n|---|---|\n| x | 1 |\n"
    assert label_violations(good, require_once=False) == []
    fig = "![Figure 1. Capex per km](figures/x.svg)\n"
    assert label_violations(fig, require_once=False) != []


@pytest.mark.parametrize("path", RESULT_SECTIONS, ids=lambda p: p.name)
def test_no_will_in_result_sections(path: Path) -> None:
    assert will_violations(path.read_text(encoding="utf-8")) == []


def test_will_audit_allows_only_quoted_metalanguage() -> None:
    assert will_violations('the report never writes "will"\n') == []
    assert will_violations("the line will reduce car trips\n") != []


def test_no_model_names_in_report_brief_summaries() -> None:
    targets = sorted((REPO_ROOT / "docs/report").rglob("*.md")) + [
        REPO_ROOT / p
        for p in (
            "docs/policy-brief.md",
            "docs/executive-summary.en.md",
            "docs/executive-summary.ar.md",
        )
    ]
    hits = {
        str(t): model_name_violations(t.read_text(encoding="utf-8")) for t in targets if t.exists()
    }
    assert {k: v for k, v in hits.items() if v} == {}


@pytest.mark.parametrize("path", SECTIONS, ids=lambda p: p.name)
def test_l4_l5_only_with_the_tradeoff_figures(path: Path) -> None:
    assert l45_violations(path.read_text(encoding="utf-8")) == []


@pytest.mark.skipif(
    not (REPO_ROOT / "runs/r6/top5/top5.csv").exists(),
    reason="run outputs not present in this checkout",
)
def test_report_check_passes() -> None:
    """Number tracing, S6-L1 risk statement, footnotes and assumption ids resolve, labels, names."""
    assert run_checks() == {}


def test_figure_source_rule_detects_drift() -> None:
    from common.report import figure_source_line, figure_source_violations

    row = {"stem": "fig04-x", "title_en": "T", "sources": "runs/a", "provenance": "p"}
    idx = {"fig04-x": row}
    head = f"![Figure 4. T](figures/fig04-x.svg)\n{LABEL_LINE}\n*Figure 4.* c\n"
    good = head + figure_source_line(row) + "\n"
    assert figure_source_violations(good, idx) == []
    bad = good.replace("Source: runs/a", "Source: runs/b")
    assert figure_source_violations(bad, idx) != []
    assert figure_source_violations("![Figure 9. Z](figures/fig09-y.svg)\n", idx) != []
