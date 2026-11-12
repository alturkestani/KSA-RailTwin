"""R5: rule of a half, effective density and the no-double-counting matrix (economics.benefits)."""

import copy

import numpy as np
import pandas as pd
import pytest

from economics import benefits as B


def test_rule_of_half() -> None:
    cs = B.rule_of_half([100.0, 0.0], [120.0, 10.0], [50.0, 80.0], [40.0, 60.0])
    assert cs.tolist() == [0.5 * 220 * 10, 0.5 * 10 * 20]


def test_matrix_has_no_double_counting() -> None:
    B.check_no_double_counting()  # the shipped matrix passes


def test_a_benefit_counted_twice_fails() -> None:
    m = copy.deepcopy(B.MATRIX)
    m["time_savings_again"] = dict(m["user_time_cost"])  # same channel added twice
    with pytest.raises(ValueError, match="double counting"):
        B.check_no_double_counting(m)


def test_a_stream_inside_user_benefits_fails() -> None:
    m = copy.deepcopy(B.MATRIX)
    m["fuel_savings"] = {
        "channel": "vehicle_operating_cost_fuel",  # already inside the logsum car cost
        "excludes": [],
        "in": "core",
        "method": "test",
    }
    with pytest.raises(ValueError, match="inside user_time_cost"):
        B.check_no_double_counting(m)


def test_land_value_and_scorecard_are_never_added() -> None:
    assert B.MATRIX["land_value_uplift"]["in"] == "capture_only"
    assert B.MATRIX["regional_development_vision2030"]["in"] == "scorecard"
    assert B.MATRIX["wei_agglomeration"]["in"] == "wei"  # reported separately


def test_effective_density_change() -> None:
    zones = pd.DataFrame({"zone_id": ["a", "b"], "jobs": [100.0, 300.0]})
    g0 = pd.DataFrame({"o": ["a"], "d": ["b"], "gc": [60.0]})
    g1 = pd.DataFrame({"o": ["a"], "d": ["b"], "gc": [30.0]})
    own = np.array([10.0, 10.0])
    out = B.effective_density_change(g0, g1, zones, 1.0, own)
    ed0, ed1 = 100 / 10 + 300 / 60, 100 / 10 + 300 / 30
    assert out[0] == pytest.approx(ed1 / ed0 - 1)
    assert out[1] == 0.0
    # a zero cut-off means no cut-off (TAG A2.4)
    assert B.effective_density_change(g0, g1, zones, 1.0, own, 0.0)[0] == pytest.approx(out[0])


def test_interpolation_is_flat_after_last_year() -> None:
    v = B.interpolate([2025, 2060], [1.0, 2.0], np.array([2025.0, 2042.5, 2060.0, 2090.0]))
    assert v.tolist() == [1.0, 1.5, 2.0, 2.0]
