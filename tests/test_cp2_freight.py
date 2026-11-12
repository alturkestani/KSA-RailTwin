"""CP2 P4a: `freight` is a valid LineSpec.line_type and only sourced freight-only lines use it."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from common.schemas import LineSpec

ROOT = Path(__file__).resolve().parents[1]


def test_freight_line_type_accepted(fixtures: Path) -> None:
    base = yaml.safe_load((fixtures / "corridor.yaml").read_text(encoding="utf-8"))
    assert LineSpec.model_validate({**base, "line_type": "freight"}).line_type == "freight"
    with pytest.raises(ValidationError):
        LineSpec.model_validate({**base, "line_type": "cargo"})


def test_only_sourced_freight_lines_use_freight() -> None:
    freight = {
        f.stem
        for f in (ROOT / "cities/ksa/lines").glob("*.yaml")
        if yaml.safe_load(f.read_text(encoding="utf-8"))["line_type"] == "freight"
    }
    assert freight == {"sar-north-freight", "sar-east-freight-legacy"}
