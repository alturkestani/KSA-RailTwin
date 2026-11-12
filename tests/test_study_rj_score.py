"""STUDY_RJ_SCORE (Tariq, 6 Nov 2026): full-judge v3 scores of the five Riyadh-Jeddah study sketches
as Landbridge replacements (S1* + one sketch). Study sketch, not the recommended programme.
Synthetic demand, uncalibrated: scenario comparison, not a forecast.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime

import pytest
import yaml

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL
from study import rj

START_HEAD = "6291a1c"  # HEAD at the start of STUDY_RJ_SCORE
# R9 (7 Nov 2026): the run-scoped guard is pinned to the last commit before R9 (release
# preparation edits the licence register and the executive-summary banners by approval).
END_HEAD = "4da3bcf"
JUDGE_SHA = "d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee"
NOTE = REPO_ROOT / "docs/rj-routes-study.md"
SCORE = REPO_ROOT / rj.SCORE
PIDS = list(rj.PACKAGES)
UNTOUCHED = [
    "scenarios/S1.yaml",
    "scenarios/S6-L6.yaml",
    "scenarios/study/rj-a.yaml",
    "scenarios/study/rj-b.yaml",
    "scenarios/study/rj-c1.yaml",
    "scenarios/study/rj-c2.yaml",
    "scenarios/study/rj-lb.yaml",
    "scenarios/study/all-families.yaml",
    "cities/ksa/lines",
    "cities/ksa/corridors",
    "cities/ksa/alignments",
    "cities/ksa/alignments-study",
    "cities/ksa/assumptions/access_network.yaml",
    "network/graph_params.yaml",
    "docs/report",
    "docs/policy-brief.md",
    "docs/executive-summary.en.md",
    "docs/executive-summary.ar.md",
    "docs/assumptions.md",
    "docs/sources/index.csv",
    "docs/sources/study-rj.csv",
    "docs/licences.md",
    "docs/licences.csv",
    "docs/r6-l6-connected.md",
    "optimise",
    "judge",
    "web",
    "api",
    "film",
    "prompts",
]
needs_score = pytest.mark.skipif(
    not all((SCORE / p / "score.json").exists() for p in PIDS), reason="no STUDY_RJ_SCORE runs"
)


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


def _judge_lines(code: str, marker: str | None = None) -> dict:
    """Run `code` with the judge's files first on the path (as the study entry runs) and return
    the JSON it prints."""
    env = rj.judge_env(REPO_ROOT, REPO_ROOT / marker if marker else None)
    jr = REPO_ROOT / "judge" / rj.JUDGE
    if not jr.exists():
        pytest.skip("judge copy not present (gitignored)")
    r = subprocess.run(
        [rj.judge_python(), "-c", code],
        cwd=jr,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(r.stdout.strip().splitlines()[-1])


PRELUDE = (
    "import json, os, sys, runpy; sys.path.insert(0, os.environ['R6_JUDGE_ROOT']);\n"
    "{imp}\n"
    "from pathlib import Path; from access import railgraph; from optimise import layout as L\n"
    "L.patch_railgraph(); root = Path(os.environ['R6_JUDGE_ROOT'])\n"
    "cfg = railgraph.load_cfg(root)\n"
    "def lines(m=None): return railgraph.scenario_lines('S1', cfg, root, m)\n"
    "def ids(m=None): return [ld['id'] for ld in lines(m)]\n"
    "def dump(m=None): return json.dumps(lines(m), sort_keys=True, default=str)\n"
)
ENTRY = f"runpy.run_path('{REPO_ROOT / 'study/rj_judge.py'}', run_name='rj_judge')"


# --------------------------------------------------------------------------- outputs
@needs_score
@pytest.mark.parametrize("pid", PIDS)
def test_score_file_has_judge_hash_seed_and_omission(pid: str) -> None:
    d = SCORE / pid
    s = json.loads((d / "score.json").read_text())
    m = json.loads((d / "meta.json").read_text())
    assert s["feasible"] and s["seed"] == 1 and s["draws"] == 10000
    assert len(s["appraisal_rows"]) == 45  # 3 horizons x 5 rate cases x 3 population cases
    assert m["seed"] == 1 and m["judge"] == "v3-variants" and m["judge_sha256"] == JUDGE_SHA
    assert m["code_version"].startswith("judge v3-variants @ 017234562c sha256 d9fef643")
    assert m["layout_hash"] and m["harness_code_version"]
    assert not m["harness_code_version"].endswith("-dirty")
    assert m["landbridge_omitted"] is True and m["study_marker"] == "study_rj_replace"
    raw = json.loads((d / "score.judge.json").read_text())
    assert set(s) - set(raw) == {
        "national_reach_reported_only",
        "study",
        "_judge_sha256",
        "score_record",
    }
    assert all(s[k] == raw[k] for k in raw)


@needs_score
@pytest.mark.parametrize("pid", PIDS)
def test_graph_omits_landbridge_and_has_exactly_one_sketch(pid: str) -> None:
    rid = rj.PACKAGES[pid]
    s = json.loads((SCORE / pid / "score.json").read_text())
    assert s["corridors"] == [rid] and s["phases"] == {"2030": [rid]}
    by = s["by_line_2050_medium"]
    assert "landbridge" not in by and rid in by
    assert [k for k in by if k.startswith("RJ-")] == [rid]
    assert s["loads_2050_medium"]["landbridge"] is None
    assert s["loads_2050_medium_S1"]["landbridge"] is None  # S1 column = S1*
    # the line set the judge builds under the study marker
    marker = str(rj.SCORE / pid / "inputs/marker.yaml")
    lay = str(REPO_ROOT / rj.SCORE / pid / "inputs/layout.yaml")
    out = _judge_lines(
        PRELUDE.format(imp=ENTRY)
        + "import yaml, tempfile\n"
        + f"items = yaml.safe_load(open('{lay}'))['corridors']\n"
        + "m = L.write_marker(items, Path(tempfile.mkdtemp()) / 'm.yaml')\n"
        + "print(json.dumps({'s1': ids(), 'layout': ids(m)}))",
        marker,
    )
    assert "landbridge" not in out["s1"] and "landbridge" not in out["layout"]
    assert out["layout"] == out["s1"] + [rid]
    assert set(out["s1"]) == {
        "hhr",
        "sar-east-passenger",
        "sar-north-passenger",
        "riyadh-rail-link",
        "gcc-railway-ksa",
    }


def test_s1_and_published_top5_keep_landbridge_byte_unchanged() -> None:
    """Without the study marker, importing the study entry changes nothing: S1 and a published
    top-5 layout build the same line lists, byte for byte, as the plain judge."""
    top = REPO_ROOT / "runs/r6/top5/L1.layout.yaml"
    if not top.exists():
        pytest.skip("no published top-5 layout")
    code = (
        "import yaml, tempfile\n"
        f"items = yaml.safe_load(open('{top}'))['corridors']\n"
        "m = L.write_marker(items, Path(tempfile.mkdtemp()) / 'm.yaml')\n"
        "print(json.dumps({'s1': dump(), 'top': dump(m), 'ids': ids(), 'tids': ids(m)}))"
    )
    plain = _judge_lines(PRELUDE.format(imp="") + code)
    via = _judge_lines(PRELUDE.format(imp=ENTRY) + code)
    assert plain == via
    assert "landbridge" in plain["ids"] and "landbridge" in plain["tids"]


@needs_score
@pytest.mark.parametrize("pid", PIDS)
def test_costing_uses_routed_km_and_matches_study_s6(pid: str) -> None:
    import pandas as pd

    rid = rj.PACKAGES[pid]
    side = json.loads((REPO_ROOT / rj.STUDY / f"{rid}.json").read_text())
    spec = yaml.safe_load((SCORE / pid / "inputs/spec.yaml").read_text())
    corr = yaml.safe_load((SCORE / pid / "inputs" / f"{rid}.corridor.yaml").read_text())
    straight = yaml.safe_load((REPO_ROOT / rj.CORR / f"{rid}.yaml").read_text())["length_km"]
    assert spec["length_km"] == pytest.approx(side["length_km"], abs=1e-6)
    assert corr["length_km"] == pytest.approx(side["length_km"], abs=1e-6)
    assert abs(spec["length_km"] - straight) > 10  # never the straight end-to-end distance
    assert spec["track"] == "double" and spec["electrified"] is True
    assert spec["line_type"] == ("mixed" if rid == "RJ-LB" else "hsr")
    chk = json.loads((SCORE / pid / "inputs/check.json").read_text())
    assert chk["cost_run_identical_to_study"] is True
    assert chk["km"] == pytest.approx(side["length_km"], abs=1e-6)
    assert chk["ivt_end_to_end_min"] == pytest.approx(chk["times_csv_p50_all_stop_min"], abs=0.05)
    import numpy as np

    cap = pd.read_csv(REPO_ROOT / rj.RUNS / "costs-s1/capex.csv").set_index("route")
    s = json.loads((SCORE / pid / "score.json").read_text())
    dist = pd.read_parquet(SCORE / pid / "cost/rcf/distribution.parquet")
    for q in ("p10", "p50", "p90"):
        # the judge: "nearest" percentile of the same 10,000 draws (economics.cba.pct)
        v = float(np.percentile(dist.capex_uplifted, int(q[1:]), method="nearest"))
        assert s["capex_sar_m"][f"capex_{q}"] == pytest.approx(v, abs=1e-6)
        # the study's §6 table: interpolated percentile of the same draws, rounded to SAR m
        assert s["capex_sar_m"][f"capex_{q}"] == pytest.approx(
            cap.at[rid, f"uplifted_{q}_sar_m"], rel=1e-4
        )
    assert s["capex_sar_m"]["capex_base_p50"] == pytest.approx(
        cap.at[rid, "base_p50_sar_m"], rel=1e-4
    )


@needs_score
@pytest.mark.parametrize("pid", PIDS)
def test_scenario_score_block_matches_score_json(pid: str) -> None:
    sc = yaml.safe_load((REPO_ROOT / "scenarios/study" / f"{pid}.yaml").read_text())
    s = json.loads((SCORE / pid / "score.json").read_text())
    b = sc["score"]
    assert b == json.loads(json.dumps(s["score_record"])) | {"run": str(rj.SCORE / pid)}
    assert b["robust_npv"] == pytest.approx(s["robust_npv"], abs=0.05)
    assert b["capex_sar_m"]["capex_p50"] == pytest.approx(s["capex_sar_m"]["capex_p50"], abs=0.05)
    assert b["judge"].endswith(JUDGE_SHA) and b["seed"] == 1
    assert sc["baseline"] == "S1-star" and "landbridge" not in sc["lines"]["include"]
    assert sc["replaces"] == ["landbridge"] and sc["corridors"][0]["phase"] == 2030
    assert b["label"] == "study sketch, not the recommended programme" and LABEL in b["labels"]


@needs_score
def test_s1_star_reference_written_and_consistent() -> None:
    ref = json.loads((SCORE / "_s1-star/s1_star.json").read_text())
    assert "without the committed Landbridge" in ref["definition"]
    for pid in PIDS:
        s = json.loads((SCORE / pid / "score.json").read_text())
        assert s["rail_trips_2050_medium_S1"] == ref["rail_trips_2050_medium"]


def test_stacked_study_scenarios_remain_unscored() -> None:
    for rid in ("a", "b", "c1", "c2", "lb"):
        sc = yaml.safe_load((REPO_ROOT / f"scenarios/study/rj-{rid}.yaml").read_text())
        assert "score" not in sc
        assert "landbridge" in sc["lines"]["include"]
        assert any("not scored" in n.lower() for n in sc["notes"])
    assert "score" not in yaml.safe_load(
        (REPO_ROOT / "scenarios/study/all-families.yaml").read_text()
    )
    assert not (SCORE / "rj-a").exists() and not list(SCORE.glob("all-families*"))


def test_study_note_score_section() -> None:
    t = NOTE.read_text(encoding="utf-8")
    assert "## 8. Full-judge score" in t
    sec = t[t.index("## 8. Full-judge score") :]
    assert LABEL in sec and ALIGNMENT_LIMITATION in sec
    assert "study sketch, not the recommended programme" in sec
    assert (
        "The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah "
        "with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are "
        "not rail-graph interchanges."
    ) in sec
    assert "S1\\*" in sec and "outside the Haram boundary" in sec
    low = sec.lower()
    for bad in ("will reduce", "will transform", "vignette", "pilgrim", "muslim", "nationality"):
        assert bad not in low, bad
    assert " will " not in low


@needs_score
def test_note_table_matches_score_json() -> None:
    sec = NOTE.read_text(encoding="utf-8").split("## 8. Full-judge score")[1]
    for pid, rid in rj.PACKAGES.items():
        s = json.loads((SCORE / pid / "score.json").read_text())
        row = next(ln for ln in sec.splitlines() if ln.startswith(f"| {rid} |"))
        assert f"{s['robust_npv']:,.0f}".replace("-", "−") in row
        assert f"{s['capex_sar_m']['capex_p50']:,.0f}" in row


@needs_score
def test_protected_runs_untouched() -> None:
    t0 = min(
        datetime.fromisoformat(json.loads((SCORE / p / "meta.json").read_text())["created_utc"])
        for p in PIDS
    )
    for d in ("runs/r6/top5", "runs/r6/l6", "runs/r7"):
        files = [p for p in (REPO_ROOT / d).rglob("*") if p.is_file()]
        if files:
            assert max(p.stat().st_mtime for p in files) < t0.timestamp(), d


def test_untouched_areas_since_run_start() -> None:
    assert _diff(*UNTOUCHED) == []


@needs_score
def test_note_via_taif_table_recomputes() -> None:
    sec = NOTE.read_text(encoding="utf-8").split("### 8c.")[1]
    a = json.loads((SCORE / "replace-rj-a/score.json").read_text())
    for pid, rid in (
        ("replace-rj-b", "RJ-B"),
        ("replace-rj-c1", "RJ-C1"),
        ("replace-rj-c2", "RJ-C2"),
    ):
        s = json.loads((SCORE / pid / "score.json").read_text())
        row = next(ln for ln in sec.splitlines() if ln.startswith(f"| {rid} "))
        dn = s["robust_npv"] - a["robust_npv"]
        dc = s["capex_sar_m"]["capex_p50"] - a["capex_sar_m"]["capex_p50"]
        assert f"{dn:,.0f}".replace("-", "−") in row and f"+{dc:,.0f}" in row
