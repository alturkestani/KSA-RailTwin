"""CP2_PREP item 2 (P2a): one price index, the P2a arithmetic, and the delta log generator."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from costs import register
from rail import benchmarks

REPO = Path(__file__).resolve().parents[1]
INDEX = REPO / "cities" / "ksa" / "costs" / "index.yaml"


@pytest.fixture(scope="module")
def idx() -> dict:
    return yaml.safe_load(INDEX.read_text(encoding="utf-8"))


def _series(idx: dict, sid: str) -> dict[int, float]:
    return next(s for s in idx["series"] if s["id"] == sid)["values"]


def _fx(idx: dict, cur: str) -> dict[int, float]:
    return next(x for x in idx["fx"] if x["currency"] == cur)["lcu_per_usd"]


def _factor(idx: dict, fid: str) -> float:
    return next(f for f in idx["factors"] if f["id"] == fid)["factor"]


def test_one_index_file() -> None:
    assert not list((REPO / "cities" / "ksa" / "benchmarks").glob("index*.yaml"))
    assert benchmarks.DEFAULT_INDEX == register.INDEX == INDEX


def test_r1b_source_ids_kept(idx: dict) -> None:
    ids = {i["source"] for i in idx["inputs"]}
    assert {"S-bench-idx-001", "S-bench-idx-002", "S-bench-idx-003"} <= ids
    assert {"S-cost-idx-001", "S-cost-idx-002", "S-cost-idx-003", "S-cost-idx-004"} <= ids
    assert idx["method_assumption_id"] == "A-cost-002"


def test_series_kinds_follow_p2a(idx: dict) -> None:
    """SAR: CPI. Foreign currencies: GDP deflator, except the registered AED exception."""
    kinds = {s["id"]: s["kind"] for s in idx["series"]}
    assert kinds["I-price-sar"] == "cpi"
    assert kinds.pop("I-price-aed") == "cpi"  # A-cost-307: no 2025 UAE deflator in WDI
    kinds.pop("I-price-sar")
    assert set(kinds.values()) == {"gdp_deflator"}


def test_sar_items_inflate_with_cpi_only(idx: dict) -> None:
    cpi = _series(idx, "I-price-sar")
    assert _factor(idx, "I-sar-2016-sar-2025") == pytest.approx(cpi[2025] / cpi[2016], rel=1e-5)


def test_foreign_deflate_before_conversion_then_peg(idx: dict) -> None:
    peg = idx["peg_sar_per_usd"]["value"]
    us = _series(idx, "I-price-usd")
    assert _factor(idx, "I-usd-2010-sar-2025") == pytest.approx(us[2025] / us[2010] * peg, rel=1e-5)
    fra, eur_fx = _series(idx, "I-price-eur-fra"), _fx(idx, "EUR")
    want = fra[2025] / fra[2018] / eur_fx[2025] * peg
    assert _factor(idx, "I-eur-fra-2018-sar-2025") == pytest.approx(want, rel=1e-5)
    # Years before 2000 come from the folded-in R1b files (S-bench-idx-001).
    row = next(f for f in idx["factors"] if f["id"] == "I-eur-ita-1992-sar-2025")
    assert "S-bench-idx-001" in row["source"]


def test_sensitivity_converts_then_saudi_cpi(idx: dict) -> None:
    peg, cpi, eur_fx = idx["peg_sar_per_usd"]["value"], _series(idx, "I-price-sar"), _fx(idx, "EUR")
    want = 1 / eur_fx[2018] * peg * cpi[2025] / cpi[2018]
    assert _factor(idx, "I-eur-2018-sar-2025-cti") == pytest.approx(want, rel=1e-5)


def test_register_ignores_per_economy_rows(idx: dict) -> None:
    table = register.factor_table(idx, "inflate_then_convert")
    assert table[("EUR", 2016)]["id"] == "I-eur-2016-sar-2025"  # EA20, not a country row
    assert not any(f.get("country") for f in table.values())


def test_benchmark_lookup_prefers_economy_row(idx: dict) -> None:
    out = benchmarks.convert(1.0, "EUR", 2018, "DEU", idx)
    assert out["central_factor"]["id"] == "I-eur-deu-2018-sar-2025"
    assert out["sensitivity_factor"]["id"] == "I-eur-2018-sar-2025-cti"
    tur = benchmarks.convert(1.0, "EUR", 2018, "TUR", idx)
    assert tur["central_factor"]["id"] == "I-eur-2018-sar-2025"


def test_delta_markdown_counts_and_causes() -> None:
    before = [
        {
            "row_id": "M-x-1",
            "slug": "france",
            "level": "line",
            "value": "10",
            "currency": "EUR",
            "price_year": "2010",
            "country": "FRA",
            "route_a_economy": "FRA",
            "route_a": "100.0",
            "route_b": "90.0",
        },
        {
            "row_id": "M-x-2",
            "slug": "france",
            "level": "line",
            "value": "5",
            "currency": "AED",
            "price_year": "2019",
            "country": "ARE",
            "route_a_economy": "ARE",
            "route_a": "",
            "route_b": "20.0",
        },
    ]
    after = [
        {
            "row_id": "M-x-1",
            "central": 100.0,
            "central_factor": "I-eur-fra-2010-sar-2025",
            "central_series": "I-price-eur-fra",
            "sensitivity": 99.0,
            "sensitivity_factor": "I-eur-2010-sar-2025-cti",
        },
        {
            "row_id": "M-x-2",
            "central": 21.0,
            "central_factor": "I-aed-2019-sar-2025",
            "central_series": "I-price-aed",
            "sensitivity": 20.0,
            "sensitivity_factor": "I-aed-2019-sar-2025-cti",
        },
    ]
    md = benchmarks.delta_markdown(before, after, "index.yaml", "before.csv")
    assert md.startswith("> **Document version:** docs/benchmarks/normalisation-delta.md")
    assert "value pairs (row x measure): 4" in md
    assert "Changed" in md and ": 2 of 4" in md  # +10 % sensitivity and the new AED value
    assert "max 10.000 %" in md
    assert "newly converted: UAE CPI" in md
    assert "deflator vs CPI" in md
    with pytest.raises(ValueError):
        benchmarks.delta_markdown(before, after[:1], "i", "b")
