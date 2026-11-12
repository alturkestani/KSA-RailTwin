"""R7 value-for-money switching-value solver on the fictional fixture basis."""

from __future__ import annotations

import pytest

from funding import fiscal, vfm
from tests.test_funding_r7_fiscal import fixture_basis


@pytest.fixture(scope="module")
def params():
    return fiscal.load_params()


def test_vfm_definition(params):
    b = fixture_basis()
    v = vfm.vfm(b, params, "un_wpp_low")
    assert v["vfm"] == pytest.approx(v["psc"] - v["ppp"])
    assert v["vfm_pct_psc"] == pytest.approx(100 * v["vfm"] / v["psc"])


def test_switching_value_zeroes_vfm(params):
    b = fixture_basis()
    sv = vfm.switching_value(b, params, "un_wpp_low", "bid_contingency", (-0.95, 3.0))
    assert sv is not None
    assert vfm.vfm(b, params, "un_wpp_low", bid_contingency=sv)["vfm"] == pytest.approx(0, abs=1e-3)
    # VfM falls as the bid gets dearer and as private finance gets dearer
    lo = vfm.vfm(b, params, "un_wpp_low", bid_contingency=sv - 0.1)["vfm"]
    hi = vfm.vfm(b, params, "un_wpp_low", bid_contingency=sv + 0.1)["vfm"]
    assert lo > 0 > hi
    a = vfm.vfm(b, params, "un_wpp_low", private_finance_premium=0.0)["vfm"]
    z = vfm.vfm(b, params, "un_wpp_low", private_finance_premium=0.05)["vfm"]
    assert a > z


def test_no_switch_returns_none(params):
    b = fixture_basis()
    assert vfm.switching_value(b, params, "un_wpp_low", "bid_contingency", (2.0, 3.0)) is None


def test_assess_flags_unsourced_dependence(params):
    res = vfm.assess(fixture_basis(), params, "un_wpp_low")
    for name, d in res["drivers"].items():
        assert d["id"].startswith("A-fund-")
        assert d["sourcing"] == vfm.DRIVERS[name][1]
        assert d["sourced"] == (vfm.DRIVERS[name][1] == vfm.SOURCED)
        if d["switch_within_range"] and not d["sourced"]:
            assert name in res["depends_on_unsourced"]
    assert set(res["rate_sensitivity"]) == {
        "flat_5",
        f"const:{params['params']['sovereign_real_rate']['value']}",
    }


def test_reference_class_driver_is_not_sourced_for_ksa(params):
    """verify-R7 O11: the private-finance premium is a UK reference class, unclear for KSA."""
    assert vfm.DRIVERS["private_finance_premium"][1] == vfm.REFERENCE_CLASS
    res = vfm.assess(fixture_basis(), params, "un_wpp_low")
    assert "private_finance_premium" in res["not_sourced_for_ksa"]
    assert res["drivers"]["private_finance_premium"]["sourced"] is False
