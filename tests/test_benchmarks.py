"""rail.benchmarks: validation, conversion and the generated summary on a three-row fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from rail.benchmarks import convert, read_csv, summarise_rows, validate_rows


# A made-up index in the format of the single index (cities/ksa/costs/index.yaml, CP2 P2a): one
# fixture economy FXA using EUR, deflators and exchange rates chosen for easy arithmetic.
# FXA deflator 2010 = 80, 2025 = 120; EA deflator 2010 = 90, 2025 = 117; EUR per USD 2010 = 0.75,
# 2025 = 0.9; US deflator 2020 = 100, 2025 = 125; Saudi CPI 2010 = 100, 2020 = 110, 2025 = 132.
def _f(fid: str, method: str, cur: str, year: int, factor: float, **kw: str) -> dict:
    return {
        "id": fid,
        "method": method,
        "from_currency": cur,
        "from_year": year,
        "to_currency": "SAR",
        "to_year": 2025,
        "factor": factor,
        **kw,
    }


ITC, CTI = "inflate_then_convert", "convert_then_inflate"
INDEX = {
    "base": {"currency": "SAR", "price_year": 2025},
    "method_central": ITC,
    "method_sensitivity": CTI,
    "factors": [
        _f("I-eur-fxa-2010", ITC, "EUR", 2010, 120 / 80 / 0.9 * 3.75, country="FXA"),
        _f("I-eur-2010", ITC, "EUR", 2010, 117 / 90 / 0.9 * 3.75),
        _f("I-eur-2010-cti", CTI, "EUR", 2010, 1 / 0.75 * 3.75 * 132 / 100),
        _f("I-usd-2020", ITC, "USD", 2020, 125 / 100 * 3.75),
        _f("I-usd-2020-cti", CTI, "USD", 2020, 3.75 * 132 / 110),
    ],
}


def test_fixture_validates(fixtures: Path) -> None:
    rows = read_csv(fixtures / "benchmarks_metrics.csv")
    assert len(rows) == 3
    assert validate_rows(rows, {"S-fixture-001", "S-fixture-002", "S-fixture-003"}) == []


def test_validation_catches_blank_and_unknown() -> None:
    bad = {
        "row_id": "M-x-1",
        "metric": "cost_per_km",
        "value": "5",
        "currency": "",
        "price_year": "",
        "grade": "E",
        "source_id": "S-missing",
    }
    problems = " ".join(validate_rows([bad], set()))
    for needle in ("currency is blank", "price_year is blank", "grade 'E'", "S-missing"):
        assert needle in problems


def test_convert_central_and_sensitivity() -> None:
    """CP2 P2a: central = source-economy deflator before conversion, then the peg; the
    sensitivity converts at the price-year rate and inflates with the Saudi CPI."""
    out = convert(10, "EUR", 2010, "FXA", INDEX)
    assert out["central"] == pytest.approx(10 * 1.5 / 0.9 * 3.75)
    assert out["central_factor"]["id"] == "I-eur-fxa-2010"  # the economy's own row wins
    assert out["sensitivity"] == pytest.approx(10 / 0.75 * 3.75 * 1.32)
    other = convert(10, "EUR", 2010, "TUR", INDEX)  # EUR outside the euro area: the EA row
    assert other["central"] == pytest.approx(10 * 1.3 / 0.9 * 3.75)
    usd = convert(2, "USD", 2020, None, INDEX)
    assert usd["central"] == pytest.approx(2 * 1.25 * 3.75)
    assert usd["sensitivity"] == pytest.approx(2 * 3.75 * 1.2)
    none = convert(1, "XXX", 2010, None, INDEX)
    assert none["central"] is None and none["sensitivity"] is None


def test_summary_excludes_grade_d(fixtures: Path, tmp_path: Path) -> None:
    rows = read_csv(fixtures / "benchmarks_metrics.csv")
    (tmp_path / "fixture_a.md").write_text("x\nno reliable data found (searched: x)\n")
    md = summarise_rows(
        rows,
        INDEX,
        docs_dir=tmp_path,
        slugs=["fixture_a", "fixture_b"],
        levels={"M-fx-001": "line"},
    )
    assert md.startswith("> **Document version:** docs/benchmarks/README.md")
    assert "| fixture_a | [`fixture_a.md`](fixture_a.md) | 2 | 1/1/0/0 | 1 |" in md
    assert "| fixture_b | **missing** | 1 | 0/0/0/1 | 0 |" in md
    cost_section = md.split("## Cost per route-km")[1].split("## Other metrics")[0]
    assert "Fixture line 1" in cost_section and "Fixture line 2" not in cost_section
    assert "| fixture_a | 2 |" in cost_section  # one line row, both routes converted
    assert "| M-fx-003 | Fixture HSR B | cost_per_km |" in md.split("## Grade D rows")[1]
    assert (
        "| fixture_b | cost_per_km, ridership_vs_forecast, farebox_recovery or operating_ratio"
        in md
    )
