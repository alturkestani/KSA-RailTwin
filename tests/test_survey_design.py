"""Survey design generator (design only, rule 7): schema, determinism, dominance, real config."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from common import REPO_ROOT
from demand.survey import SurveyDesign, app, generate, load_design


def _attr(aid: str, unit: str, levels: list, param: str, prior, **kw) -> dict:
    coding = "dummy" if isinstance(prior, list) else "linear"
    return {
        "id": aid,
        "label_en": aid,
        "label_ar": "سمة",
        "unit": unit,
        "levels": levels,
        "coding": coding,
        "param": param,
        "prior": prior,
        "source": "fixture",
        **kw,
    }


# Fictional design for tests only: every value is made up (`source: fixture`).
FIXTURE = {
    "version": "fixture",
    "label": "fixture; designed, not fielded",
    "design": {"n_tasks": 12, "n_blocks": 2, "dominance_task": True, "starts": 3, "max_sweeps": 10},
    "alternatives": [
        {
            "id": "car",
            "label_en": "Fixture car",
            "label_ar": "سيارة تجريبية",
            "asc": {"prior": 0.0, "source": "fixture"},
            "reference": True,
            "attributes": [
                _attr("ivt", "min", [60, 90, 120], "ivt", -0.02),
                _attr("cost", "SAR", [20, 40], "cost", -0.03),
            ],
        },
        {
            "id": "rail",
            "label_en": "Fixture rail",
            "label_ar": "قطار تجريبي",
            "asc": {"prior": 0.2, "source": "fixture"},
            "attributes": [
                _attr("ivt", "min", [40, 60, 80], "ivt", -0.02),
                _attr("cost", "SAR", [30, 50], "cost", -0.03),
                _attr(
                    "family_car",
                    "yes/no",
                    [0, 1],
                    "family_car",
                    [0.3],
                    level_labels_en=["no", "yes"],
                    level_labels_ar=["لا", "نعم"],
                ),
            ],
        },
    ],
}
FIXTURE_YAML = yaml.safe_dump(FIXTURE, allow_unicode=True, sort_keys=False)
REAL = REPO_ROOT / "docs" / "survey" / "design.yaml"
runner = CliRunner()


@pytest.fixture(scope="module")
def fixture_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("survey") / "design_tiny.yaml"
    path.write_text(FIXTURE_YAML, encoding="utf-8")
    return path


def _raw() -> dict:
    return yaml.safe_load(FIXTURE_YAML)


def test_fixture_validates(fixture_path: Path) -> None:
    cfg = load_design(fixture_path)
    assert cfg.parameters() == ["asc_rail", "ivt", "cost", "family_car[1]"]


def test_same_seed_same_design_different_seed_differs(fixture_path: Path) -> None:
    cfg = load_design(fixture_path)
    a, sa = generate(cfg, 1)
    b, sb = generate(cfg, 1)
    c, _ = generate(cfg, 2)
    assert a == b and sa == sb
    assert a != c


def test_blocks_tasks_and_dominance(fixture_path: Path) -> None:
    rows, summary = generate(load_design(fixture_path), 1)
    assert summary["tasks_per_respondent"] == 7
    assert summary["fielding"] == "designed, not fielded"
    for block in (1, 2):
        tasks = {r["task"] for r in rows if r["block"] == block}
        assert tasks == set(range(1, 8))
    dom = {
        (r["alternative"], r["attribute"]): r["level_index"]
        for r in rows
        if r["task_type"] == "dominance" and r["block"] == 1
    }
    # rail best (shortest time, lowest fare, family carriage), car worst
    assert dom[("rail", "ivt")] == 0 and dom[("rail", "cost")] == 0
    assert dom[("rail", "family_car")] == 1
    assert dom[("car", "ivt")] == 2 and dom[("car", "cost")] == 1


def test_cli_writes_csv_and_meta(tmp_path: Path, fixture_path: Path) -> None:
    out = tmp_path / "cs.csv"
    res = runner.invoke(
        app, ["design", "--config", str(fixture_path), "--seed", "1", "--out", str(out)]
    )
    assert res.exit_code == 0, res.output
    with out.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows and rows[0]["block"] == "1"
    meta = (tmp_path / "cs.csv.meta.json").read_text(encoding="utf-8")
    assert '"seed": 1' in meta and "d_error" in meta


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["alternatives"][0]["attributes"][0].pop("source"),
        lambda d: d["alternatives"][1].__setitem__("reference", True),
        lambda d: d.__setitem__("label", "fielded"),
        lambda d: d["design"].__setitem__("n_blocks", 5),
        lambda d: d["alternatives"][1]["attributes"][2].__setitem__("prior", 0.3),
        lambda d: d["alternatives"][1]["attributes"][0].__setitem__("prior", -0.5),
    ],
)
def test_invalid_configs_rejected(mutate) -> None:
    raw = _raw()
    mutate(raw)
    with pytest.raises(ValidationError):
        SurveyDesign.model_validate(raw)


@pytest.mark.skipif(not REAL.exists(), reason="docs/survey/design.yaml not written yet")
def test_committed_choice_sets_match_seed_1() -> None:
    cfg = load_design(REAL)
    rows, _ = generate(cfg, 1)
    committed = REPO_ROOT / "docs" / "survey" / "choice_sets.csv"
    with committed.open(encoding="utf-8") as f:
        got = list(csv.DictReader(f))
    assert len(got) == len(rows)
    for g, r in zip(got, rows, strict=True):
        assert g["alternative"] == r["alternative"] and g["attribute"] == r["attribute"]
        assert int(g["level_index"]) == r["level_index"]


def test_s_estimate_is_a_positive_lower_bound(fixture_path: Path) -> None:
    _, summary = generate(load_design(fixture_path), 1)
    s = summary["s_estimate"]
    assert s["binding_parameter"] in s["respondents_per_parameter"]
    assert s["max_respondents"] == max(s["respondents_per_parameter"].values())
    assert all(v > 0 for v in s["respondents_per_parameter"].values())
