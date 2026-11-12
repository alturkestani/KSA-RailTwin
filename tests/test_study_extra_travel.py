"""STUDY_EXTRA_TRAVEL (Tariq, 7 Nov 2026): extra domestic trips and visitor / land-entry effects, a
research sensitivity on the study path. Synthetic demand, uncalibrated: scenario comparison, not a
forecast. Not the official ranking.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import datetime

import numpy as np
import pandas as pd
import pytest
import yaml

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL
from study import extra_travel as xt
from study import extra_travel_core as core
from tests.localdata import needs_local

START_HEAD = "e90ef4a"  # HEAD at the start of STUDY_EXTRA_TRAVEL (tag r9 + the prompt commit)
END_HEAD = "edcf6da"  # last commit of the run before this test file and the status block
NOTE = REPO_ROOT / "docs/extra-travel-study.md"
OUT = REPO_ROOT / xt.OUT
NOT_OFFICIAL = "Not the official ranking"
UNTOUCHED = [
    "film",
    "judge",
    "prompts",
    "web",
    "api",
    "NOTICE",
    "docs/licences.md",
    "docs/licences.csv",
    "docs/credits.md",
    "docs/report",
    "docs/policy-brief.md",
    "docs/executive-summary.en.md",
    "docs/executive-summary.ar.md",
    "docs/assumptions.md",
    "docs/sources/index.csv",
    "docs/sources/study-rj.csv",
    "docs/rj-routes-study.md",
    "scenarios",
    "cities/ksa/lines",
    "cities/ksa/corridors",
    "cities/ksa/cba",
    "cities/ksa/assumptions/demand_generation.yaml",
    "cities/ksa/assumptions/access_network.yaml",
    "cities/ksa/population/intl_segment.yaml",
    "cities/ksa/population/intl_airport_split.yaml",
    "demand",
    "modechoice",
    "economics",
    "optimise",
    "access",
]
needs_runs = needs_local(
    "runs/study/extra-travel/induced_summary.csv",
    "runs/study/extra-travel/induced/reproduction_check.json",
    "runs/study/extra-travel/baseline/rj_baseline.json",
    "runs/study/extra-travel/land/land_scenarios.json",
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


# --------------------------------------------------------------------------- pure functions
def _od(trips, cost, rail_share=0.2):
    n = len(trips)
    t = np.asarray(trips, float)
    return pd.DataFrame(
        {
            "o": [f"Z{i}" for i in range(n)],
            "d": [f"Y{i}" for i in range(n)],
            "trips": t,
            "cost_min": np.asarray(cost, float),
            "trips_car": t * 0.5,
            "trips_rail": t * rail_share,
            "trips_air": t * (0.5 - rail_share),
            "trips_bus": 0.0,
            "road_km": 100.0,
            "rail_km": 110.0,
            "air_gc_km": 90.0,
        }
    )


def test_induce_zero_is_identity() -> None:
    b, s = _od([100, 50], [200, 300]), _od([100, 50], [150, 300])
    pd.testing.assert_frame_equal(core.induce_od(b, s, 0.0), s)


def test_induce_proportional_factor_and_shares() -> None:
    b, s = _od([100, 50], [200, 300]), _od([100, 50], [150, 300])
    out = core.induce_od(b, s, -0.5)
    f = (150 / 200) ** -0.5
    assert out.trips.iloc[0] == pytest.approx(100 * f)
    assert out.trips.iloc[1] == pytest.approx(50)  # cost unchanged -> factor 1
    assert out.trips_rail.iloc[0] / out.trips.iloc[0] == pytest.approx(0.2)


def test_induce_rail_only_puts_generated_trips_on_rail() -> None:
    b, s = _od([100], [200]), _od([100], [150])
    out = core.induce_od(b, s, -0.5, "rail_only")
    gen = 100 * ((150 / 200) ** -0.5 - 1)
    assert out.trips_rail.iloc[0] == pytest.approx(20 + gen)
    assert out.trips_car.iloc[0] == pytest.approx(50)
    assert out.trips.iloc[0] == pytest.approx(
        out[[f"trips_{m}" for m in core.MODES]].sum(axis=1).iloc[0]
    )
    with pytest.raises(ValueError):
        core.induce_od(b, s, -0.5, "air_only")


def test_induced_factor_missing_costs_are_neutral() -> None:
    f = core.induced_factor(np.array([np.nan, 0.0, 100.0]), np.array([50.0, 50.0, 50.0]), -0.25)
    assert f[0] == 1.0 and f[1] == 1.0 and f[2] == pytest.approx(0.5**-0.25)


def test_port_mix_refuses_unassigned_ports() -> None:
    rows = pd.DataFrame({"port": ["A", "B"], "total": [3.0, 1.0]})
    mix = core.port_mix(rows, {"g1": {"ports": {"A": "Z1"}}, "g2": {"ports": {"B": "Z2"}}})
    assert mix["shares"] == {"g1": 0.75, "g2": 0.25}
    with pytest.raises(ValueError):
        core.port_mix(rows, {"g1": {"ports": {"A": "Z1"}}})


def test_land_scenario_no_path_no_rail_and_no_hajj_input() -> None:
    r = core.land_scenario(1000.0, 0.1, {"Z1": 0.5, "Z2": 0.5}, {"Z1": True}, 0.1, 0.25)
    assert r["entrants"] == pytest.approx(125.0)
    assert r["extra_entrants"] == pytest.approx(25.0)
    assert r["rail_trips_by_group"]["Z2"] == 0.0
    assert r["rail_trips"] == pytest.approx(62.5 * 2 * 0.1)
    assert "hajj" not in " ".join(core.land_scenario.__code__.co_varnames)


# --------------------------------------------------------------------------- frozen values
def test_frozen_central_values_unchanged() -> None:
    gen = yaml.safe_load((REPO_ROOT / "cities/ksa/assumptions/demand_generation.yaml").read_text())
    tr = gen["trip_rates"]
    assert (tr["tourism"]["value"], tr["leisure_vfr"]["value"]) == (2.403, 2.564)
    assert (tr["business"]["value"], tr["commute"]["value"]) == (0.977, 0.5)
    seg = yaml.safe_load((REPO_ROOT / "cities/ksa/population/intl_segment.yaml").read_text())
    assert seg["rail_share_given_path"]["value"] == 0.0286
    c = xt.cfg()
    assert set(c["induced"]["purposes"]) == {"tourism", "leisure_vfr", "business"}
    assert {"commute", "pilgrimage"} <= set(c["induced"]["unchanged"])
    assert c["official_ranking"] is False and c["land_ports"]["hajj_held_fixed"] is True


def test_untouched_areas_since_run_start() -> None:
    assert _diff(*UNTOUCHED) == []


def test_study_registers_stay_beside_the_study() -> None:
    idx = (REPO_ROOT / "docs/sources/index.csv").read_text()
    assert "S-xt-" not in idx
    rows = list(csv.DictReader((REPO_ROOT / "docs/sources/study-extra-travel.csv").open()))
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)) and all(i.startswith("S-xt-") for i in ids)
    oag = [r for r in rows if "oag.com/busiest-routes-world-2025" in r["url"]]
    assert len(oag) >= 6 and all(r["accessed"].startswith("2026-11-07") for r in oag)
    assert not any("transitcosts" in json.dumps(r).lower() for r in rows)
    am = (REPO_ROOT / "docs/study-extra-travel/assumptions.md").read_text()
    for i in range(1, 12):
        assert f"| A-xt-{i:03d} |" in am


def test_not_folded_into_r8_or_dashboard() -> None:
    paths = [
        *(REPO_ROOT / "docs/report").rglob("*.md"),
        REPO_ROOT / "docs/policy-brief.md",
        REPO_ROOT / "docs/executive-summary.en.md",
        REPO_ROOT / "docs/executive-summary.ar.md",
        *(REPO_ROOT / "api").rglob("*.py"),
        *[p for p in (REPO_ROOT / "web/src").rglob("*") if p.is_file()],
    ]
    for p in paths:
        t = p.read_text(encoding="utf-8", errors="ignore")
        assert "extra-travel" not in t and "extra_travel" not in t, p


# --------------------------------------------------------------------------- the note
def test_note_labels_limits_and_wording() -> None:
    t = NOTE.read_text(encoding="utf-8")
    assert LABEL in t and NOT_OFFICIAL in t and ALIGNMENT_LIMITATION in t
    captions = [ln for ln in t.splitlines() if ln.startswith("*Table")]
    assert len(captions) == 3
    for ln in captions:
        assert LABEL in ln and NOT_OFFICIAL in ln, ln
    assert "Hajj is held fixed in every scenario" in t
    assert "https://www.oag.com/busiest-routes-world-2025" in t and "7 Nov 2026" in t
    assert not re.search(r"\bwill\b", t, re.I)
    assert not re.search(r"\d\s*%\s*(of\s+)?GDP|GDP\s+by\s+\d", t, re.I)
    assert "Vision 2030" not in t
    for word in ("vignette", "family", "families", "pilgrim group", "a pilgrim who"):
        assert word not in t.lower(), word


@needs_runs
def test_note_table_3a_matches_summary() -> None:
    t = NOTE.read_text(encoding="utf-8")
    d = pd.read_csv(OUT / "induced_summary.csv")
    for r in d.itertuples():
        name = "zero (= published)" if r.case == "zero" else r.case
        row = next(
            ln for ln in t.splitlines() if ln.startswith(f"| {name} |") and ln.count("|") >= 13
        )
        assert f"{r.npv_p50_medium:,.0f}".replace("-", "−") in row
        assert f"{r.extra_trips_2050_medium:,.0f}" in row


# --------------------------------------------------------------------------- outputs
@needs_runs
def test_zero_case_reproduces_published_s1_vs_s0() -> None:
    chk = json.loads((OUT / "induced/reproduction_check.json").read_text())
    assert chk["inputs_identical"] and chk["results_identical"]
    assert chk["inputs_max_relative_difference"] == 0.0


@needs_runs
def test_meta_records_judge_seed_and_not_official() -> None:
    rec = json.loads((REPO_ROOT / "runs/r6/judge/v1-r5.hash.json").read_text())
    metas = [OUT / "baseline/meta.json", OUT / "land/meta.json"]
    metas += [OUT / "induced" / c / "meta.json" for c in xt.elasticity_cases()]
    for m in metas:
        d = json.loads(m.read_text())
        assert d["official_ranking"] is False and d["label"] == LABEL
        assert d["judge"] == "v1-r5" and d["judge_sha256"] == rec["sha256"]
        assert d["seed"] == 1 and d["config_hash"] and d["data_hash"]
        assert d["code_version"] and not d["code_version"].endswith("-dirty"), m


@needs_runs
def test_sensitivity_tables_carry_labels_and_hajj_fixed() -> None:
    s = json.loads((OUT / "induced_summary.json").read_text())
    assert s["official_ranking"] is False and s["label"] == LABEL
    assert all(r["not_official"] == "not the official ranking" for r in s["rows"])
    land = json.loads((OUT / "land/land_scenarios.json").read_text())
    assert land["official_ranking"] is False
    hajj = land["hajj_held_fixed"]["land"]
    assert all(r["hajj_land_held_fixed"] == hajj for r in land["rows"])
    assert all(r["rail_trips_entry_exit"] == 0 for r in land["rows"] if r["network"] == "S0")
    # pilgrimage and commute are never induced
    for c in xt.elasticity_cases():
        diag = json.loads((OUT / "induced" / c / "induced_diag.json").read_text())["groups"]
        assert all(
            set(g) - {"_scenario_all_purposes", "_baseline_all_purposes"}
            == {"tourism", "leisure_vfr", "business"}
            for g in diag.values()
        )


@needs_runs
def test_protected_runs_untouched() -> None:
    t0 = min(
        datetime.fromisoformat(json.loads(p.read_text())["created_utc"])
        for p in OUT.rglob("meta.json")
    )
    for d in (
        "runs/r6/top5",
        "runs/r6/l6",
        "runs/r7",
        "runs/cba/CBA-S1-committed-programme",
        "runs/cba/inputs",
    ):
        files = [p for p in (REPO_ROOT / d).rglob("*") if p.is_file()]
        if files:
            assert max(p.stat().st_mtime for p in files) < t0.timestamp(), d
