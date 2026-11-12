import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from common import REPO_ROOT
from common.schemas import (
    CbaCase,
    LineSpec,
    Param,
    RegionRow,
    Scenario,
    ZoneProps,
    load_cost_register,
    load_region_register,
)


def _yaml(p: Path) -> object:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def test_corridor_fixture(fixtures: Path) -> None:
    line = LineSpec.model_validate(_yaml(fixtures / "corridor.yaml"))
    assert line.layer == "hypothetical" and line.fixture
    assert len(line.stations) == 3


def test_line_rules(fixtures: Path) -> None:
    base = _yaml(fixtures / "corridor.yaml")
    assert isinstance(base, dict)
    with pytest.raises(ValidationError):  # hypothetical needs generated_from
        LineSpec.model_validate({**base, "generated_from": None})
    with pytest.raises(ValidationError):  # planned/hypothetical can never be in service
        LineSpec.model_validate({**base, "status": "in_service"})
    with pytest.raises(ValidationError):  # existing needs an operator
        LineSpec.model_validate({**base, "layer": "existing", "status": "in_service"})
    stations = [dict(s) for s in base["stations"]]
    stations[1]["km_post"] = 0
    with pytest.raises(ValidationError):
        LineSpec.model_validate({**base, "stations": stations})


def test_zones_fixture(fixtures: Path) -> None:
    gj = json.loads((fixtures / "zones.geojson").read_text(encoding="utf-8"))
    props = [ZoneProps.model_validate(f["properties"]) for f in gj["features"]]
    assert len(props) == 6 and all(p.fixture for p in props)


def test_region_register_fixture(fixtures: Path) -> None:
    rows = load_region_register(fixtures / "region_register.parquet")
    assert len(rows) == 5 and all(r.fixture for r in rows)
    assert any(r.population is None for r in rows)  # unsourced population stays null


def test_region_row_rules(fixtures: Path) -> None:
    row = load_region_register(fixtures / "region_register.parquet")[0].model_dump()
    with pytest.raises(ValidationError):
        RegionRow.model_validate({**row, "pop_source": None})
    with pytest.raises(ValidationError):
        RegionRow.model_validate({**row, "tag_10k": False})
    with pytest.raises(ValidationError):
        RegionRow.model_validate({**row, "screened": False, "exclusion_reason": None})
    with pytest.raises(ValidationError):
        RegionRow.model_validate({**row, "region": "not_a_region"})


def test_cost_register_fixture(fixtures: Path) -> None:
    items = load_cost_register(fixtures / "cost_register.yaml")
    assert len(items) == 4
    assert all(i.status == "assumed" and i.source == "fixture" for i in items)


def test_cost_item_rules(fixtures: Path) -> None:
    item = load_cost_register(fixtures / "cost_register.yaml")[0].model_dump()
    from common.schemas import CostItem

    with pytest.raises(ValidationError):  # unknown must not carry guessed values
        CostItem.model_validate({**item, "status": "unknown"})
    CostItem.model_validate(
        {**item, "status": "unknown", "low": None, "central": None, "high": None}
    )
    with pytest.raises(ValidationError):
        CostItem.model_validate({**item, "low": 50})
    with pytest.raises(ValidationError):
        CostItem.model_validate({**item, "status": "derived"})
    with pytest.raises(ValidationError):
        CostItem.model_validate({**item, "status": "sourced"})


def test_cba_fixture(fixtures: Path) -> None:
    case = CbaCase.model_validate(_yaml(fixtures / "cba_case.yaml"))
    assert case.baseline != case.scenario and case.fixture


def test_cba_rules(fixtures: Path) -> None:
    base = _yaml(fixtures / "cba_case.yaml")
    assert isinstance(base, dict)
    with pytest.raises(ValidationError):
        CbaCase.model_validate({**base, "baseline": base["scenario"]})
    benefits = {**base["benefits"], "wider_economic_impacts": {"report_separately": False}}
    with pytest.raises(ValidationError):
        CbaCase.model_validate({**base, "benefits": benefits})


def test_param_needs_source_or_assumption() -> None:
    Param.model_validate({"value": 1, "source": "S-001"})
    Param.model_validate({"value": 1, "assumption_id": "A-misc-001"})
    with pytest.raises(ValidationError):
        Param.model_validate({"value": 1})


@pytest.mark.parametrize("name", ["S0.yaml", "S1.yaml"])
def test_repo_scenarios_validate(name: str) -> None:
    Scenario.model_validate(_yaml(REPO_ROOT / "scenarios" / name))
