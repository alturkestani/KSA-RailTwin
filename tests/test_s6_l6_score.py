"""S6_L6_SCORE: the full-judge v3 score of S6-L6 exists with the judge hash and seed; the scenario
`score:` block matches score.json; the note carries both labels, the A-r4-acc-004 sentence and the
fast-vs-full table, and its table 7b recomputes from the CSVs; runs/r6/top5/ is untouched; the
protected R6-R8 documents are unchanged against the run's start HEAD.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime

import pytest
import yaml

from common import REPO_ROOT
from common.labels import LABEL

SCORE = REPO_ROOT / "runs/r6/l6/score"
NOTE = REPO_ROOT / "docs/r6-l6-connected.md"
L6 = REPO_ROOT / "scenarios/S6-L6.yaml"
JUDGE_SHA = "d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee"
START_HEAD = "6149a8b0e59b879e824e05d28503483b13035485"  # HEAD at the start of S6_L6_SCORE
END_HEAD = "87cb9d0"  # S6_L6_SCORE accepted; R8_L6_PANEL starts here
PROTECTED = [
    "docs/policy-brief.md",
    "docs/executive-summary.en.md",
    "docs/executive-summary.ar.md",
    "docs/r6-topology.md",
    "docs/delivery-models.md",
    "docs/fiscal-exposure.md",
    "docs/licences.md",
    "docs/licences.csv",
    "docs/report/figures/figures-index.csv",
    "web",
    "api",
    "judge",
    "film",
    "cities/ksa/assumptions/access_network.yaml",
]
needs_score = pytest.mark.skipif(not (SCORE / "score.json").exists(), reason="no L6 score run")


@needs_score
def test_score_file_has_judge_hash_and_seed() -> None:
    s = json.loads((SCORE / "score.json").read_text())
    m = json.loads((SCORE / "meta.json").read_text())
    assert s["feasible"] and s["seed"] == 1 and s["draws"] == 10000
    assert m["seed"] == 1 and m["judge"] == "v3-variants" and m["judge_sha256"] == JUDGE_SHA
    assert m["code_version"].startswith("judge v3-variants @ 017234562c sha256 d9fef643")
    assert m["layout_hash"] and m["harness_code_version"]
    assert len(s["corridors"]) == 16 and s["capex_sar_m"]["capex_p50"] == pytest.approx(
        227212.97, abs=0.05
    )
    # all horizons x rate cases x population cases, as runs/r6/top5/<L>/score.json
    assert len(s["appraisal_rows"]) == 45
    # the judge's own file is kept; only the reported-only national reach was added
    raw = json.loads((SCORE / "score.judge.json").read_text())
    assert set(s) - set(raw) == {"national_reach_reported_only"}
    assert all(s[k] == raw[k] for k in raw)


@needs_score
def test_scenario_score_block_matches_score_json() -> None:
    s = json.loads((SCORE / "score.json").read_text())
    b = yaml.safe_load(L6.read_text())["score"]
    assert b["run_id"] == "runs/r6/l6/score" and b["judge_sha256"] == JUDGE_SHA
    assert b["robust_npv"] == pytest.approx(s["robust_npv"], abs=0.05)
    for k, p in (("low", "un_wpp_low"), ("medium", "un_wpp_medium"), ("high", "un_wpp_high")):
        assert b["npv_at_p50_cost"][k] == pytest.approx(s["npv_at_p50_cost"][p], abs=0.05)
        assert b["npv_at_p90_cost"][k] == pytest.approx(s["npv_at_p90_cost"][p], abs=0.05)
    for q in ("p10", "p50", "p90"):
        assert b["capex"][q] == pytest.approx(s["capex_sar_m"][f"capex_{q}"], abs=0.05)
        assert b["bcr_medium"][q] == pytest.approx(s[f"bcr_{q}"]["un_wpp_medium"], abs=5e-4)
    assert b["access_gain_120"] == s["access_gain_120"]
    f = b["fast_vs_full"]
    assert f["full_minus_fast"] == pytest.approx(s["robust_npv"] - f["robust_npv_fast"], abs=0.1)


def test_note_labels_access_sentence_and_fast_vs_full_table() -> None:
    t = NOTE.read_text(encoding="utf-8")
    assert "comparison layout, not the recommended programme" in t.lower()
    assert LABEL in t
    assert (
        "The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah "
        "with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are "
        "not rail-graph interchanges."
    ) in t
    assert "## 7. Full-judge score" in t and "### 7a. Fast mode vs full judge" in t
    assert "| robust NPV (min over population cases, at P50 cost) | −200,761 | **−191,660**" in t
    assert "1–17 % of capex" in t
    assert "neither a constraint nor an objective" in t
    for row in ("A-r6-130 |", "A-r6-131 |"):
        line = next(
            ln
            for ln in (REPO_ROOT / "docs/assumptions.md").read_text().splitlines()
            if ln.startswith("| " + row)
        )
        assert "diagnostic only, Tariq 6 Nov 2026" in line


@needs_score
def test_top5_untouched() -> None:
    t0 = datetime.fromisoformat(json.loads((SCORE / "meta.json").read_text())["created_utc"])
    files = [p for p in (REPO_ROOT / "runs/r6/top5").rglob("*") if p.is_file()]
    assert files
    assert max(p.stat().st_mtime for p in files) < t0.timestamp()


def test_protected_docs_unchanged_since_run_start() -> None:
    r = subprocess.run(
        ["git", "cat-file", "-e", START_HEAD], cwd=REPO_ROOT, capture_output=True, check=False
    )
    r_end = subprocess.run(
        ["git", "cat-file", "-e", END_HEAD], cwd=REPO_ROOT, capture_output=True, check=False
    )
    if r.returncode or r_end.returncode:
        pytest.skip("start HEAD not in this clone")
    # bounded to the S6_L6_SCORE window: R8_L6_PANEL (Tariq, 6 Nov 2026) later folds L6 into the
    # report, summaries and brief on purpose (tests/test_r8_l6_panel.py guards that run)
    d = subprocess.run(
        ["git", "diff", "--name-only", START_HEAD, END_HEAD, "--", *PROTECTED, "docs/report"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    # the generated assumptions annex mirrors the A-r6-130/131 status text (common.report build)
    assert set(d) <= {"docs/report/annex-assumptions.md"}, d


def _f0(x: float) -> str:
    return f"{x:,.0f}".replace("-", "−")


def _f2(x: float) -> str:
    return f"{x:.2f}".replace("-", "−")


def _m(x: float) -> str:
    return f"{x / 1e6:.2f} M"


def _expected_7b(r: dict) -> dict[str, str]:
    def j(*k: str, f=_f0) -> str:  # noqa: ANN001
        return " / ".join(f(r[c]) for c in k)

    return {
        "robust NPV": _f0(r["robust_npv"]),
        "NPV at P50 cost, low": j("npv_p50cost_low", "npv_p50cost_medium", "npv_p50cost_high"),
        "NPV at P90 cost": j("npv_p90cost_low", "npv_p90cost_medium", "npv_p90cost_high"),
        "NPV draws": j("npv_draws_p10_medium", "npv_draws_p50_medium", "npv_draws_p90_medium"),
        "BCR": j("bcr_p10_medium", "bcr_p50_medium", "bcr_p90_medium", f=_f2),
        "capex": j("capex_p10", "capex_p50", "capex_p90"),
        "NPV at P50 cost, medium: Green Book": j(
            "sens_greenbook_2026/30y", "sens_greenbook_2026/40y", "sens_greenbook_2026/60y"
        ),
        "NPV at P50 cost, medium, 60 y": j(
            "sens_drawn/60y", "sens_flat_5/60y", "sens_flat_7/60y", "sens_tag_declining/60y"
        ),
        "rail trips": f"{_m(r['rail_trips_2050_medium'])} "
        f"(+{_m(r['added_rail_trips_2050_medium'])})",
        "added rail passenger-km": f"{r['added_rail_pkm_m_2050_medium']:,.0f} M",
        "new route-km": f"{r['new_route_km']:,.1f}" if r["new_route_km"] else "0",
        "120-min reach gain": _m(r["access_gain_120"]),
        "national reach": f"{_m(r['national_reach_120_reported_only'])} "
        f"(+{_m(r['national_reach_gain_120_reported_only'])})",
        "CO2": _f0(r["co2_pv_p50_medium"]),
        "HHR": _m(r["hhr_pax_2050"]),
        "Landbridge": _m(r["landbridge_pax_2050"]),
        "wider economic": _f0(r["pv_wei_indicative_medium"]),
    }


@needs_score
def test_note_table_7b_recomputes_from_the_csvs() -> None:
    import pandas as pd

    rows = pd.concat(
        [
            pd.read_csv(REPO_ROOT / "runs/r6/top5/top5.csv"),
            pd.read_csv(SCORE / "S6-L6.csv"),
        ]
    ).to_dict("records")
    t = NOTE.read_text(encoding="utf-8").split("### 7b.")[1].split("What the full score")[0]
    lines = [ln for ln in t.splitlines() if ln.startswith("| ") and "---" not in ln][1:]
    assert len(lines) == 17
    checked = 0
    for ln in lines:
        cells = [c.strip().strip("*") for c in ln.strip("|").split("|")]
        label, vals = cells[0], cells[1:]
        assert len(vals) == 6
        key = next(k for k in _expected_7b(rows[0]) if label.startswith(k))
        for r, v in zip(rows, vals, strict=True):
            assert v == _expected_7b(r)[key], (label, r["layout"], v)
            checked += 1
    assert checked == 102
