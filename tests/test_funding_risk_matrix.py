"""Risk-allocation matrix template and filled matrices (W6; filled per corridor at R7)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from funding.models import RISK_KEYS
from funding.risk_matrix import DEFAULT_PATH, REQUIRED_METRICS, RiskMatrix, app, render

runner = CliRunner()


def _matrix(template: bool = True) -> dict:
    rows = []
    for r in RISK_KEYS:
        row = {
            "risk": r,
            "scope": "fixture",
            "public": None,
            "private": None,
            "shared": None,
            "mechanism_options": ["fixture clause"],
            "precedents": ["S-fixture-001"],
        }
        if not template:
            row["shared"] = "x"
            row["mechanism"] = "fixture clause"
        rows.append(row)
    metrics = [
        {
            "id": m,
            "definition": "fixture",
            "formula": "fixture",
            "unit": "fixture",
            "inputs": ["fixture"],
            "sources": ["S-fixture-001"],
        }
        for m in REQUIRED_METRICS
    ]
    d = {
        "version": "fixture",
        "template": template,
        "columns": ["public", "private", "shared"],
        "rows": rows,
        "fiscal_exposure_metrics": metrics,
    }
    if not template:
        d["corridor_family"] = "fixture_family"
        d["delivery_model"] = "ppp_dbfm"
    return d


def test_template_and_filled_validate() -> None:
    RiskMatrix.model_validate(_matrix(True))
    filled = RiskMatrix.model_validate(_matrix(False))
    assert "| construction |" in render(filled)


@pytest.mark.parametrize(
    "template,mutate",
    [
        (True, lambda d: d["rows"].reverse()),  # wrong order
        (True, lambda d: d["rows"][0].__setitem__("public", "x")),  # template must be empty
        (True, lambda d: d["fiscal_exposure_metrics"].pop()),  # metric missing
        (False, lambda d: d["rows"][0].__setitem__("public", "x")),  # two marks
        (False, lambda d: d["rows"][0].__setitem__("shared", None)),  # no mark
        (False, lambda d: d["rows"][0].__setitem__("shared", "yes")),  # not an x
        (False, lambda d: d.__setitem__("corridor_family", None)),
        (False, lambda d: d["rows"][0].__setitem__("precedents", [])),
    ],
)
def test_invalid_matrices_rejected(template: bool, mutate) -> None:
    raw = _matrix(template)
    mutate(raw)
    with pytest.raises(ValidationError):
        RiskMatrix.model_validate(raw)


@pytest.mark.skipif(not DEFAULT_PATH.exists(), reason="template not written yet")
def test_real_template_loads_and_sources_resolve() -> None:
    res = runner.invoke(app, ["validate", "--path", str(DEFAULT_PATH)])
    assert res.exit_code == 0, res.output
