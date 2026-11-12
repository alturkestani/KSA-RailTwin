"""R5 H3a: the international rail-share fit is exact and the Ramadan check is independent."""

import pytest

from demand.intl_fit import exact_share, ramadan_factor


def test_exact_share_reproduces_target() -> None:
    s = exact_share(observed=10.0, resident=6.0, legs_at_one=100.0)
    assert s == pytest.approx(0.04)
    assert 6.0 + s * 100.0 == pytest.approx(10.0)


def test_exact_share_needs_legs() -> None:
    with pytest.raises(ValueError):
        exact_share(10.0, 6.0, 0.0)


def test_ramadan_factor_flat_resident() -> None:
    # no international legs: a flat resident profile gives a factor of exactly 1
    assert ramadan_factor(12.0, 0.0, 0.0) == pytest.approx(1.0)
    # all international, Ramadan month = 3 x mean month
    assert ramadan_factor(0.0, 12.0, 3.0) == pytest.approx(3.0)
