"""R1c: cost register schema, rules, index and normalisation round trip."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from common.schemas import CostItem, load_cost_register
from costs import register
from costs.index_build import build
from tests.localdata import needs_local

REPO = Path(__file__).resolve().parents[1]
REAL_REGISTER = REPO / "cities" / "ksa" / "costs" / "cost_register.yaml"
REAL_INDEX = REPO / "cities" / "ksa" / "costs" / "index.yaml"


def _item(**kw: object) -> dict:
    base = {
        "id": "C-fixture-line-001",
        "item": "Fixture line",
        "category": "line_type",
        "line_type": "conventional_passenger",
        "terrain": "flat_desert",
        "unit": "SAR_m_per_km",
        "currency": "EUR",
        "price_year": 2016,
        "low": 5.0,
        "central": 7.0,
        "high": 9.0,
        "source": "S-cost-idx-004",
        "status": "sourced",
    }
    return {**base, **kw}


def _index() -> dict:
    return yaml.safe_load(REAL_INDEX.read_text(encoding="utf-8"))


def test_fixture_register_still_valid(fixtures: Path) -> None:
    assert len(load_cost_register(fixtures / "cost_register.yaml")) == 4


def test_new_optional_fields_and_units() -> None:
    it = CostItem.model_validate(
        _item(unit="SAR_m_per_km_per_yr", approach="bottom_up", scope="x", layer="n/a")
    )
    assert it.approach == "bottom_up"
    with pytest.raises(ValidationError):
        CostItem.model_validate(_item(unit="furlongs"))
    with pytest.raises(ValidationError):
        CostItem.model_validate(_item(layer="maybe"))


def test_rules_beyond_schema() -> None:
    bad = [
        CostItem.model_validate(_item(status="assumed", source="assumed")),  # no assumption id
        CostItem.model_validate(
            _item(status="unknown", low=None, central=None, high=None)
        ),  # no `searched`
        CostItem.model_validate(_item(source="S-does-not-exist")),
        CostItem.model_validate(_item(currency="XYZ")),  # no index factor
    ]
    probs = register.check(bad, _index(), register.known_source_ids(), set())
    joined = "\n".join(probs)
    assert "assumption_id" in joined
    assert "searched" in joined
    assert "S-does-not-exist" in joined
    assert "no index factor for XYZ" in joined


@needs_local("data/ksa/costs/wb_NY.GDP.DEFL.ZS.json")
def test_index_factor_matches_hand_arithmetic() -> None:
    idx = build()
    f = {x["id"]: x for x in idx["factors"]}
    eur = f["I-eur-2016-sar-2025"]
    s = next(x for x in idx["series"] if x["currency"] == "EUR")["values"]
    fx = next(x for x in idx["fx"] if x["currency"] == "EUR")["lcu_per_usd"]
    assert eur["factor"] == pytest.approx(s[2025] / s[2016] / fx[2025] * 3.75, rel=1e-6)
    assert f["I-sar-2025-sar-2025"]["factor"] == pytest.approx(1.0)
    assert f["I-usd-2025-sar-2025"]["factor"] == pytest.approx(3.75)


@needs_local("data/ksa/costs/wb_NY.GDP.DEFL.ZS.json")
def test_committed_index_is_current() -> None:
    """index.yaml is generated: rebuilding from the manifest rows gives the same factors."""
    built = {x["id"]: x["factor"] for x in build()["factors"]}
    committed = {x["id"]: x["factor"] for x in _index()["factors"]}
    assert built == committed


def test_normalise_round_trip(tmp_path: Path) -> None:
    items = [
        CostItem.model_validate(_item()),
        CostItem.model_validate(_item(id="C-fixture-pct-001", unit="pct", currency="SAR")),
        CostItem.model_validate(
            _item(
                id="C-fixture-unk-001",
                status="unknown",
                low=None,
                central=None,
                high=None,
                searched="nowhere (test)",
            )
        ),
    ]
    idx = _index()
    rows = {r["id"]: r for r in register.normalise(items, idx)}
    money = rows["C-fixture-line-001"]
    f = money["index_factor"]["factor"]
    assert money["currency"] == "SAR" and money["price_year"] == 2025
    for k in ("low", "central", "high"):  # round trip back to the source values
        assert money[k] / f == pytest.approx(money["original"][k])
    assert rows["C-fixture-pct-001"]["low"] == 5.0  # non-money units untouched
    assert rows["C-fixture-unk-001"]["central"] is None
    with pytest.raises(ValueError):
        register.normalise(items, idx, to="USD")


def test_normalise_cli_never_edits_source(tmp_path: Path) -> None:
    src = tmp_path / "reg.yaml"
    src.write_text(yaml.safe_dump([_item()]), encoding="utf-8")
    before = src.read_bytes()
    from typer.testing import CliRunner

    res = CliRunner().invoke(
        register.app, ["normalise", "--register", str(src), "--index", str(REAL_INDEX)]
    )
    assert res.exit_code == 0, res.output
    assert src.read_bytes() == before
    assert (tmp_path / "reg.normalised.yaml").exists()


@pytest.mark.skipif(not REAL_REGISTER.exists(), reason="register not built yet")
def test_real_register_validates() -> None:
    items = load_cost_register(REAL_REGISTER)
    probs = register.check(
        items, _index(), register.known_source_ids(), register.known_assumption_ids()
    )
    assert probs == []
    for it in items:  # never a bare point for an assumed item
        if it.status == "assumed":
            assert it.low < it.high, it.id
