"""Funding options register (W6): schema rules on a fictional fixture, and the real register."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from funding.models import DEFAULT_PATH, REQUIRED_IDS, RISK_KEYS, ModelsRegister, app

runner = CliRunner()
SOURCES_HEADER = (
    "id,claim,value,unit,url,publisher,title,published,accessed,locator,quote,status,"
    "primary_to_find,used_in\n"
)


def _option(oid: str, family: str = "ppp", mix: list[str] | None = None) -> dict:
    opt = {
        "id": oid,
        "name": f"Fixture {oid}",
        "family": family,
        "definition": "Fixture definition, long enough to pass the length check.",
        "who_pays": "fixture",
        "who_owns": "fixture",
        "who_operates": "fixture",
        "typical_term_years": {"low": 20, "high": 30, "source": "S-fixture-001"},
        "risk_allocation": dict.fromkeys(RISK_KEYS, "shared"),
        "fiscal_treatment": "fixture",
        "when_it_fits": "fixture",
        "examples": ["S-fixture-001"],
        "sources": ["S-fixture-001"],
    }
    if mix:
        opt["mix"] = mix
    return opt


def _register() -> dict:
    options = [_option(i) for i in REQUIRED_IDS]
    options.append(_option("hybrid_fixture", "hybrid", ["fully_public_budget", "ppp_dbfm"]))
    return {"version": "fixture", "label": "fixture", "risk_keys": RISK_KEYS, "options": options}


def test_fixture_register_validates() -> None:
    reg = ModelsRegister.model_validate(_register())
    assert len(reg.options) == len(REQUIRED_IDS) + 1


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["options"].pop(0),  # a required option missing
        lambda d: d["options"].pop(),  # no hybrid
        lambda d: d["options"][-1].pop("mix"),  # hybrid without mix
        lambda d: d["options"][-1].__setitem__("mix", ["fully_public_budget", "nope"]),
        lambda d: d["options"][0]["risk_allocation"].pop("land"),
        lambda d: d["options"][0]["risk_allocation"].__setitem__("land", "the state"),
        lambda d: d["options"][0].__setitem__("sources", []),
        lambda d: d["options"][0].__setitem__("examples", ["not-an-id"]),
        lambda d: d["options"][0]["typical_term_years"].pop("source"),
        lambda d: d["options"].append(copy.deepcopy(d["options"][0])),  # duplicate id
        lambda d: d["options"][0].__setitem__("mix", ["ppp_dbfm", "fully_public_sar"]),
    ],
)
def test_invalid_registers_rejected(mutate) -> None:
    raw = _register()
    mutate(raw)
    with pytest.raises(ValidationError):
        ModelsRegister.model_validate(raw)


def test_cli_flags_unknown_source_ids(tmp_path: Path) -> None:
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(_register()), encoding="utf-8")
    src = tmp_path / "sources"
    src.mkdir()
    (src / "x.csv").write_text(SOURCES_HEADER, encoding="utf-8")
    res = runner.invoke(app, ["validate", "--path", str(path), "--sources-dir", str(src)])
    assert res.exit_code == 1 and "S-fixture-001" in res.output
    (src / "x.csv").write_text(SOURCES_HEADER + "S-fixture-001,,,,,,,,,,,,,\n", encoding="utf-8")
    res = runner.invoke(app, ["validate", "--path", str(path), "--sources-dir", str(src)])
    assert res.exit_code == 0, res.output


@pytest.mark.skipif(not DEFAULT_PATH.exists(), reason="models.yaml not written yet")
def test_real_register_validates_and_sources_resolve() -> None:
    res = runner.invoke(app, ["validate", "--path", str(DEFAULT_PATH)])
    assert res.exit_code == 0, res.output
