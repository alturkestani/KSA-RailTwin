"""R4 Jeddah coupling: the policy YAML validates against TrafficTwin's schema (read-only)."""

from __future__ import annotations

import pytest
import yaml

from common import REPO_ROOT
from coupling import jeddah

POLICY = REPO_ROOT / "coupling/policies/r4_hhr_jeddah_kaia.yaml"


@pytest.mark.skipif(
    not (jeddah.TRAFFICTWIN / "sim/schemas.py").exists(), reason="TrafficTwin checkout absent"
)
def test_policy_validates_against_traffictwin_schema() -> None:
    model = jeddah.traffictwin_policy_model()
    pol = model.model_validate(yaml.safe_load(POLICY.read_text(encoding="utf-8")))
    t = pol.transforms[0]
    assert t.type == "pt_line" and 0 < t.shift_share < 1 and len(t.stops) >= 2


def test_non_runnable_families_have_a_reason() -> None:
    cfg = jeddah.load_cfg(REPO_ROOT)
    for f in cfg["families"]:
        assert f["runnable"] or f.get("reason")


def test_command_points_outputs_into_this_repo() -> None:
    cmd = jeddah.command("r4_hhr_jeddah_kaia")
    assert "--runs-dir" in cmd and str((REPO_ROOT / "runs/coupling").resolve()) in cmd
    assert "PYTHONDONTWRITEBYTECODE=1" in cmd
