import pytest

from common.labels import LABEL, format_range


def test_label_text() -> None:
    assert LABEL == "synthetic demand, uncalibrated: scenario comparison, not a forecast"


def test_format_range() -> None:
    assert format_range(1.234, 2, 3.5, "SAR bn") == "P10 1.2 / P50 2.0 / P90 3.5 SAR bn"
    assert format_range(1000, 2000, 3000, digits=0) == "P10 1,000 / P50 2,000 / P90 3,000"


def test_format_range_rejects_unordered() -> None:
    with pytest.raises(ValueError):
        format_range(3, 2, 1)
