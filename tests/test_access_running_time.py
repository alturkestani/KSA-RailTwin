"""R4 running-time model (access.running_time): determinism, kinematics, stop costs, the gate."""

from __future__ import annotations

import math
from pathlib import Path

import yaml

from access import running_time as rt
from common import REPO_ROOT
from network.graph import segment_minutes

FIXTURE = REPO_ROOT / "tests/fixtures/corridor.yaml"


def _fixture() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def test_running_time_is_deterministic() -> None:
    a = rt.pair_table(r := rt.build_run(_fixture()), r.stations.id.tolist())
    b = rt.pair_table(r2 := rt.build_run(_fixture()), r2.stations.id.tolist())
    assert a.equals(b)


def test_constant_acceleration_matches_closed_form() -> None:
    # HHR-like stop-to-stop run: 78.25 km at 300 km/h; with the power knee above line speed the
    # profile is the closed-form accelerate-cruise-brake run of network.graph.segment_minutes
    stock = rt.Stock("t", 300, 0.5, 400, 0.6, {"default": 0}, 0.0, 0.0)
    m, _, _ = rt.segment_profile(78.25, 300, stock)
    assert math.isclose(m, segment_minutes(78.25, 300, 0.5, 0.6), rel_tol=0.005)


def test_power_knee_slows_the_run() -> None:
    fast = rt.Stock("f", 300, 0.59, 400, 0.6, {"default": 0}, 0.0, 0.0)
    knee = rt.Stock("k", 300, 0.59, 144, 0.6, {"default": 0}, 0.0, 0.0)
    assert rt.segment_profile(78.25, 300, knee)[0] > rt.segment_profile(78.25, 300, fast)[0]


def test_stop_cost_exceeds_dwell() -> None:
    run = rt.build_run(_fixture())
    sc = rt.stop_costs(run, run.stations.id.tolist())
    assert len(sc) == 1
    assert (sc.stop_cost_min > sc.dwell_min).all()


def test_gate_is_leave_one_out() -> None:
    f = rt.timetable_factors(REPO_ROOT)
    gate = {g["id"]: g for g in f["gate"]}
    assert "hhr-mj-current" in gate
    g = gate["hhr-mj-current"]
    assert "hhr-mj-current" not in g["loo_pairs"]
    assert g["pass"] == (abs(g["error_pct"]) <= g["tolerance_pct"])
    assert f["generic"]["range"][0] <= f["generic"]["value"] <= f["generic"]["range"][1]


def test_classes_carry_provenance() -> None:
    cls = yaml.safe_load((REPO_ROOT / rt.CLASSES).read_text(encoding="utf-8"))
    for name, c in cls["classes"].items():
        for k in ("vmax_kmh", "accel_ms2", "power_knee_kmh", "decel_ms2"):
            assert "source" in c[k] or "assumption" in c[k], (name, k)
    assert Path(REPO_ROOT / rt.LINES).exists()


def test_brief_form_cli(tmp_path: Path) -> None:
    from typer.testing import CliRunner

    out = tmp_path / "rt"
    r = CliRunner().invoke(
        rt.app, ["--line", str(FIXTURE), "--pattern", "all-stop", "--seed", "1", "--out", str(out)]
    )
    assert r.exit_code == 0, r.output
    assert (out / "pairs.csv").exists() and (out / "stops.csv").exists()
