"""CP2_PREP item 5: Haramain running-time decomposition (C-r1a-22) on the repo config."""

from __future__ import annotations

import json
import math

import pytest

from network import hhr_check
from network.graph import segment_minutes


def test_decompose_matches_graph_kinematics() -> None:
    c = hhr_check.decompose(78.25, 300, 0.5, 0.6, 0, 120, 0.07, 1.0)
    assert c.running_min == pytest.approx(segment_minutes(78.25, 300, 0.5, 0.6), rel=1e-12)
    assert c.running_min == pytest.approx(18.196, abs=0.001)
    # (a) cruise km and minutes; (b) accel/brake: v = 83.33 m/s, t = v/a, d = v^2/2a
    assert c.accel_min == pytest.approx(83.333 / 0.5 / 60, rel=1e-4)
    assert c.decel_km == pytest.approx(83.333**2 / 1.2 / 1000, rel=1e-4)
    assert c.cruise_km + c.accel_km + c.decel_km == pytest.approx(78.25)
    assert c.accel_decel_loss_min == pytest.approx(c.running_min - 78.25 / 300 * 60)
    # (c) no intermediate stop; (d) 7 % of running + 1 min/100 km
    assert c.dwell_min == 0.0
    assert c.recovery_min == pytest.approx(0.07 * c.running_min + 0.7825)


def test_dwell_counts_stops() -> None:
    assert hhr_check.decompose(78.25, 300, 0.5, 0.6, 2, 120, 0, 0).dwell_min == 4.0


def test_short_segment_rejected() -> None:
    with pytest.raises(ValueError):
        hhr_check.decompose(5.0, 300, 0.5, 0.6, 0, 120, 0, 0)


def test_cruise_for_target_inverts() -> None:
    v = hhr_check.cruise_for_target(78.25, 30.0, 0.5, 0.6, 0.07, 1.0)
    total = segment_minutes(78.25, v, 0.5, 0.6) * 1.07 + 0.7825
    assert total == pytest.approx(30.0, abs=1e-6)
    assert math.isnan(hhr_check.cruise_for_target(78.25, 5.0, 0.5, 0.6, 0.07, 1.0))


def test_analyse_repo_config_keeps_conflict_open(tmp_path) -> None:
    res = hhr_check.analyse(hhr_check.load())
    assert res["central"]["total_min"] == pytest.approx(20.25, abs=0.01)
    assert res["closes_43"] is False
    assert res["closes_43_anywhere_in_envelope"] is False
    assert res["residual_min"]["opening_2018"]["central"] == pytest.approx(22.75, abs=0.01)
    lo, hi = res["envelope_total_min"]
    assert lo < res["central"]["total_min"] < hi


def test_cli_writes_outputs(tmp_path) -> None:
    hhr_check.run(seed=1, config=hhr_check.CONFIG, run_dir=tmp_path)
    s = json.loads((tmp_path / "summary.json").read_text())
    assert s["published_min"]["opening_2018"] == 43
    assert (tmp_path / "components.csv").exists() and (tmp_path / "meta.json").exists()
