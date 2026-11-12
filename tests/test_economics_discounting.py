"""R5: discounting identities (economics.discounting)."""

import numpy as np
import pytest

from economics import discounting as dc


def test_npv_of_known_annuity() -> None:
    # 100 a year in years 1..30 at a flat 3.5 %: annuity factor (1 - 1.035^-30) / 0.035
    df = dc.factors(dc.constant(0.035), 31)
    flows = np.r_[0.0, np.full(30, 100.0)]
    assert dc.npv(flows, df) == pytest.approx(100 * (1 - 1.035**-30) / 0.035, rel=1e-12)


def test_declining_schedule_is_a_running_product() -> None:
    gb = dc.SCHEDULES["greenbook_2026"]
    df = dc.factors(gb, 101)
    assert df[0] == 1.0
    assert df[30] == pytest.approx(1.03**-30)
    assert df[31] == pytest.approx(1.03**-30 / 1.025)
    assert df[76] == pytest.approx(1.03**-30 * 1.025**-45 / 1.0225)
    assert np.all(np.diff(df) < 0)


def test_rate_bands_and_shift() -> None:
    r = dc.rate_by_year(dc.SCHEDULES["tag_declining"], 80)
    assert r[0] == 0.035 and r[29] == 0.035 and r[30] == 0.03 and r[75] == 0.025
    s = dc.shifted(dc.SCHEDULES["greenbook_2026"], 0.01)
    assert s[0][2] == pytest.approx(0.04)


def test_irr_recovers_the_rate() -> None:
    flows = np.r_[-1000.0, np.full(30, 1000 * 0.06 / (1 - 1.06**-30))]
    assert dc.irr(flows) == pytest.approx(0.06, abs=1e-6)
    many = dc.irr_many(np.vstack([flows, -np.abs(flows)]))
    assert many[0] == pytest.approx(0.06, abs=1e-6)
    assert np.isnan(many[1])  # no sign change: no IRR


def test_payback_year() -> None:
    df = np.ones(6)
    # cumulative -10, -10, -6, -2, 2, 6: non-negative from index 4 = 2 years after opening (2)
    assert dc.payback_year(np.array([-10.0, 0, 4, 4, 4, 4]), df, 2) == 2.0
    assert dc.payback_year(np.array([-10.0, 0, 1, 1, 1, 1]), df, 2) == float("inf")
