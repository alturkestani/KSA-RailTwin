"""INTEGRATE_R3: scenario files point at an existing mode-choice parameter file (thin include)."""

from __future__ import annotations

from pathlib import Path

import yaml

from common import REPO_ROOT
from common.scenarios import check_mode_choice


def test_repo_scenarios_mode_choice_files_exist() -> None:
    assert check_mode_choice(REPO_ROOT / "scenarios") == []


def test_include_lists_priors_and_r3() -> None:
    doc = yaml.safe_load((REPO_ROOT / "cities/ksa/assumptions/modechoice.yaml").read_text("utf-8"))
    assert doc["include"] == [
        "cities/ksa/assumptions/mode_choice_priors.yaml",
        "cities/ksa/assumptions/mode_choice_r3.yaml",
    ]


def test_missing_file_is_reported(tmp_path: Path) -> None:
    text = "id: S9\nmode_choice_params: cities/ksa/assumptions/nope.yaml\n"
    (tmp_path / "S9.yaml").write_text(text)
    errors = check_mode_choice(tmp_path)
    assert errors == ["S9.yaml: mode_choice_params cities/ksa/assumptions/nope.yaml missing"]
