"""R8_L6_PANEL (Tariq, 6 Nov 2026): S6-L6 folded into the R8 report, figures and dashboard as a
comparison panel like S6-L4/L5, without touching top5, R7, the judge, the access model or R9/R10.

Figure- and API-level checks live in tests/test_report_figures.py and tests/test_api_dashboard.py.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL

START_HEAD = "87cb9d0"  # HEAD at the start of R8_L6_PANEL
# R9 (7 Nov 2026): the run-scoped guard is pinned to the last commit before R9 (release
# preparation edits the licence register and the executive-summary banners by approval).
END_HEAD = "4da3bcf"
RUNS = REPO_ROOT / "runs"
RESULTS = REPO_ROOT / "docs/report/sections/04-results.md"
ACCESS = (
    "The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah with "
    "HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are not "
    "rail-graph interchanges"
)
# Areas this run must not change (prompt "Do not change").
UNTOUCHED = [
    "runs/r6/top5",
    "judge",
    "film",
    "docs/delivery-models.md",
    "docs/fiscal-exposure.md",
    "docs/licences.md",
    "docs/licences.csv",
    "cities/ksa/assumptions/access_network.yaml",
    "network/graph_params.yaml",
    "cities/ksa/alignments",
    "cities/ksa/lines",
    "web/src/config.ts",  # comment only is allowed: checked separately below
]


def _diff(*paths: str) -> list[str]:
    r = subprocess.run(
        ["git", "cat-file", "-e", START_HEAD], cwd=REPO_ROOT, capture_output=True, check=False
    )
    if r.returncode:
        pytest.skip("start HEAD not in this clone")
    return subprocess.run(
        ["git", "diff", "--name-only", START_HEAD, END_HEAD, "--", *paths],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()


def _l6_paragraph() -> str:
    text = RESULTS.read_text(encoding="utf-8")
    paras = [p for p in text.split("\n\n") if p.startswith("**Comparison layout, not the")]
    assert len(paras) == 1
    return paras[0]


def test_results_paragraph_has_both_labels_and_access_sentence() -> None:
    p = _l6_paragraph()
    assert "comparison layout, not the recommended programme".lower() in p.lower()
    assert "synthetic demand, uncalibrated: scenario comparison, not a forecast" in p
    assert "alignment limitation" in p and "docs/alignments.md" in p
    assert ACCESS in p and "the access model is unchanged" in p
    assert "not a reach trade-off and not a search result" in p
    for num in ("−191,660", "227,213", "122,532", "860,035", "0.06", "−0.08", "0.37"):
        assert num in p, num
    for num in ("+9.03 M", "+6.64 M", "0.43 M", "−200,761", "9,101", "4.0 %"):
        assert num in p, num
    assert "d9fef643" in p and "seed 1" in p and "A-r6-104" in p
    assert "will " not in p
    # in the section, after the L4/L5 paragraph, next to Figure 16
    text = RESULTS.read_text(encoding="utf-8")
    assert text.index("**Trade-off illustrations only") < text.index(p)
    assert text.index(p) < text.index("<!-- gen:fig-fig16-l6-connected-map -->")


def test_report_compiled_in_sync() -> None:
    rep = (REPO_ROOT / "docs/report/feasibility-report.md").read_text(encoding="utf-8")
    assert _l6_paragraph() in rep
    assert "figures/fig16-l6-connected-map.svg" in rep


@pytest.mark.skipif(not (RUNS / "r6/l6/score/S6-L6.csv").exists(), reason="runs/ missing")
def test_paragraph_numbers_match_runs() -> None:
    import pandas as pd

    r = pd.read_csv(RUNS / "r6/l6/score/S6-L6.csv").iloc[0]
    p = _l6_paragraph()
    assert f"{abs(round(r['robust_npv'])):,}" in p
    assert f"{round(r['capex_p50']):,}" in p
    assert f"+{r['added_rail_trips_2050_medium'] / 1e6:.2f} M" in p
    assert f"+{r['national_reach_gain_120_reported_only'] / 1e6:.2f} M" in p
    assert f"{r['access_gain_120'] / 1e6:.2f} M" in p


def test_top5_r7_and_frozen_areas_untouched() -> None:
    changed = _diff(*UNTOUCHED[:-1], "runs/r7", "prompts")
    # prompts/: only this run's prompt may differ (saved by the coordinator before the start HEAD)
    # STUDY_RJ_FAMILIES: the coordinator saved that later run's prompt at 8dafdfe, before its start
    # STUDY_RJ_SCORE: likewise, saved at 6291a1c before that run's start
    allowed = {
        "prompts/R8_L6_PANEL.md",
        "prompts/STUDY_RJ_FAMILIES.md",
        "prompts/STUDY_RJ_SCORE.md",
    }
    assert [c for c in changed if c not in allowed] == []
    r7 = [c for c in _diff("docs") if "r7" in c.lower() or "fiscal" in c or "vfm" in c.lower()]
    assert r7 == []
    for stem in ("fig01", "fig05", "fig06", "fig07", "fig09", "fig10", "fig11", "fig15"):
        assert not [c for c in _diff("docs/report/figures", "docs/deck-figures") if stem in c]


@pytest.mark.skipif(not (RUNS / "r6/top5/top5.csv").exists(), reason="runs/ missing")
def test_top5_csv_has_only_the_five_search_layouts() -> None:
    import pandas as pd

    t = pd.read_csv(RUNS / "r6/top5/top5.csv")
    assert list(t["layout"]) == ["S6-L1", "S6-L2", "S6-L3", "S6-L4", "S6-L5"]
    assert not (RUNS / "r6/top5/L6").exists() and not (RUNS / "r6/top5/L6.layout.yaml").exists()


def test_reader_facing_mentions() -> None:
    en = (REPO_ROOT / "docs/executive-summary.en.md").read_text(encoding="utf-8")
    ar = (REPO_ROOT / "docs/executive-summary.ar.md").read_text(encoding="utf-8")
    brief = (REPO_ROOT / "docs/policy-brief.md").read_text(encoding="utf-8")
    assert "S6-L6 is a comparison layout, not the recommended programme" in en
    assert "S6-L6" in ar and "مخطط للمقارنة، لا البرنامج الموصى به" in ar
    # R9 (7 Nov 2026): reviewed on Tariq's request, signed off for internal use
    assert "Status: reviewed" in ar.splitlines()[0]
    assert "**Comparison layout, not the recommended programme (S6-L6).**" in brief
    for doc in (en, brief):
        l6 = [ln for ln in doc.splitlines() if "S6-L6" in ln and "not the recommended" in ln]
        assert l6 and not any("further along the reach trade-off" in ln.lower() for ln in l6)


def test_l6_note_section5_scored() -> None:
    note = (REPO_ROOT / "docs/r6-l6-connected.md").read_text(encoding="utf-8")
    row = next(ln for ln in note.splitlines() if ln.startswith("| **S6-L6** | **−200,761**"))
    assert "not scored" not in row and "**−191,660** (§7)" in row


def test_labels_constant_unchanged() -> None:
    assert LABEL == "synthetic demand, uncalibrated: scenario comparison, not a forecast"
    assert ALIGNMENT_LIMITATION.startswith("alignments are indicative least-cost sketches")


def test_config_switcher_line_unchanged() -> None:
    cfg = (Path(REPO_ROOT) / "web/src/config.ts").read_text(encoding="utf-8")
    assert (
        'export const SWITCHER = ["S0", "S1", "S2", "S3", "S4", "S5", "S6-L2", "S6-L1", "S6-L3"]'
        " as const;" in cfg
    )
