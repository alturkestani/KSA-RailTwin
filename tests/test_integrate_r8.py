"""INTEGRATE_R8 fixes: one rounding rule in the funding docs (Tariq's R8-review item 2a)."""

from __future__ import annotations

from common import REPO_ROOT
from funding.report import f0


def test_f0_rounds_half_away_from_zero_once() -> None:
    assert f0(14611.497941813406) == "14,611"  # not 14,612 via the 14,611.5 yaml copy
    assert f0(2426.501921454321) == "2,427"
    assert f0(2.5) == "3"
    assert f0(-2.5) == "-3"
    assert f0(None) == "n/a"


def test_delivery_models_matches_report_and_brief() -> None:
    dm = (REPO_ROOT / "docs/delivery-models.md").read_text(encoding="utf-8")
    brief = (REPO_ROOT / "docs/policy-brief.md").read_text(encoding="utf-8")
    report = (REPO_ROOT / "docs/report/feasibility-report.md").read_text(encoding="utf-8")
    assert "4,859 / 14,611 |" in dm and "14,612" not in dm
    assert "half away from zero" in dm
    assert "14,611 at P90" in brief and "14,612" not in brief
    assert "4,859 / 14,611" in report and "14,612" not in report
