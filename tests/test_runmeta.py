import json
from pathlib import Path

from common import runmeta
from common.labels import LABEL


def test_config_hash_is_order_independent() -> None:
    a = {"seed": 1, "zones": ["z1", "z2"], "params": {"x": 1.0, "y": 2}}
    b = {"params": {"y": 2, "x": 1.0}, "zones": ["z1", "z2"], "seed": 1}
    assert runmeta.config_hash(a) == runmeta.config_hash(b)
    assert runmeta.config_hash(a) != runmeta.config_hash({**a, "seed": 2})


def test_write_meta_is_deterministic(tmp_path: Path) -> None:
    cfg = {"corridor": "fixture", "draws": 10}
    p1 = runmeta.write_meta(tmp_path / "r1", 7, cfg, {"assumptions": ["A-misc-001"]})
    p2 = runmeta.write_meta(tmp_path / "r2", 7, cfg, {"assumptions": ["A-misc-001"]})
    m1, m2 = (json.loads(p.read_text(encoding="utf-8")) for p in (p1, p2))
    for m in (m1, m2):
        m.pop("created_utc")
    assert m1 == m2
    assert m1["seed"] == 7
    assert m1["label"] == LABEL
    assert len(m1["config_hash"]) == 64
    assert len(m1["data_hash"]) == 64
    assert m1["code_version"]
    assert m1["tool_versions"]["python"].startswith("3.12")
    assert m1["assumptions"] == ["A-misc-001"]


def test_rng_is_seeded() -> None:
    assert runmeta.rng(3).random() == runmeta.rng(3).random()
    assert runmeta.rng(3).random() != runmeta.rng(4).random()
