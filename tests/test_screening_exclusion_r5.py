"""R5 (CP5 H4a): corridors named in `exclude_corridors` are dropped by rule, recorded, and
rejected by `validate`; the tracked rule file carries the Farasan sea-crossing belt (fixtures)."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import typer
import yaml
from test_screening_r2 import _generate

from screening import corridors

ROOT = Path(__file__).resolve().parents[1]
FARASAN = "S4-commuter_belt-jazan-225"


def _rules() -> dict:
    return yaml.safe_load(corridors.RULES.read_text(encoding="utf-8"))


def test_tracked_rules_exclude_the_farasan_belt():
    ex = {e["id"]: e for e in corridors.exclusions(_rules())}
    assert FARASAN in ex
    assert "H4a" in ex[FARASAN]["decision"] and "sea" in ex[FARASAN]["reason"]


def test_exclusion_drops_and_records(tmp_path):
    fams = _generate(tmp_path)
    belt = fams["commuter_belt"][0]
    rules = copy.deepcopy(_rules())
    rules["exclude_corridors"] = [
        {"id": belt["id"], "members": belt["generated_from_ids"], "reason": "r", "decision": "d"},
        {"id": "S3-branch_spur-not-generated", "reason": "r2", "decision": "d2"},
    ]
    dec: list[dict] = []
    out = corridors.apply_exclusions(fams, rules, dec)
    assert belt["id"] not in {c["id"] for c in out["commuter_belt"]}
    n_before = sum(len(v) for v in fams.values())
    assert sum(len(v) for v in out.values()) == n_before - 1
    hit = [d for d in dec if d["candidate"] == belt["id"]]
    assert hit and hit[0]["family"] == "commuter_belt" and hit[0]["decision"].startswith("excluded")
    miss = [d for d in dec if d["candidate"] == "S3-branch_spur-not-generated"]
    assert miss and miss[0]["family"] == "branch_spur" and "not triggered" in miss[0]["decision"]


def test_exclusion_without_rules_is_a_no_op(tmp_path):
    fams = _generate(tmp_path)
    dec: list[dict] = []
    assert corridors.apply_exclusions(fams, {}, dec) == fams and dec == []


def test_exclusion_premise_change_stops_generation(tmp_path):
    fams = _generate(tmp_path)
    belt = fams["commuter_belt"][0]
    rules = {
        "exclude_corridors": [{"id": belt["id"], "members": ["x"], "reason": "r", "decision": "d"}]
    }
    with pytest.raises(ValueError, match="review the exclusion"):
        corridors.apply_exclusions(fams, rules, [])


def test_exclusion_entry_needs_reason_and_decision():
    with pytest.raises(ValueError, match="lacks"):
        corridors.exclusions({"exclude_corridors": [{"id": "S4-x"}]})


def test_validate_rejects_an_excluded_corridor(tmp_path):
    belt = _generate(tmp_path)["commuter_belt"][0]
    f = tmp_path / "c" / f"{belt['id']}.yaml"
    f.parent.mkdir()
    f.write_text(yaml.safe_dump(corridors._py(belt), allow_unicode=True), encoding="utf-8")
    r = tmp_path / "rules.yaml"
    r.write_text(yaml.safe_dump({"exclude_corridors": []}), encoding="utf-8")
    corridors.validate(f.parent, r)  # passes without the rule
    r.write_text(
        yaml.safe_dump({"exclude_corridors": [{"id": belt["id"], "reason": "r", "decision": "d"}]}),
        encoding="utf-8",
    )
    with pytest.raises(typer.BadParameter, match="excluded"):
        corridors.validate(f.parent, r)


def test_tracked_corridor_set_has_no_excluded_id():
    ex = {e["id"] for e in corridors.exclusions(_rules())}
    ids = {p.stem for p in (ROOT / "cities/ksa/corridors").rglob("*.yaml")}
    assert not ids & ex
