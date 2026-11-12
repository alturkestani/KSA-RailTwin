"""R6: judge hashing and the layout adapter's pure helpers (tiny inputs, seconds)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from optimise import judge, layout


def test_full_hash_and_fingerprint_detect_edits(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    f = tmp_path / "a" / "x.txt"
    f.write_text("one")
    h1, files = judge.full_hash(tmp_path)
    fp1 = judge.fingerprint(tmp_path)
    assert list(files) == ["a/x.txt"]
    f.write_text("two")
    os.utime(f, ns=(1, 1))
    assert judge.full_hash(tmp_path)[0] != h1
    assert judge.fingerprint(tmp_path) != fp1


def test_hash_ignores_pycache_and_symlinks(tmp_path: Path) -> None:
    (tmp_path / "m.py").write_text("x = 1")
    h1, _ = judge.full_hash(tmp_path)
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "m.cpython-312.pyc").write_bytes(b"\0")
    (tmp_path / "link").symlink_to(tmp_path / "m.py")
    assert judge.full_hash(tmp_path)[0] == h1


def test_variant_id_is_stable_and_order_free() -> None:
    a = {"id": "S2-x", "line_type": "hsr", "track": "single"}
    b = {"track": "single", "line_type": "hsr", "id": "S2-x"}
    assert layout.variant_id(a) == layout.variant_id(b)
    assert layout.variant_id({"id": "S2-x", "phase": 2035}) == "S2-x"
    assert layout.variant_id(a).startswith("S2-x-v")  # judge v3 (CP7-3); v2 used "~"


def test_tranches_group_by_phase_in_order(tmp_path: Path) -> None:
    p = tmp_path / "l.yaml"
    p.write_text(
        yaml.safe_dump(
            {
                "corridors": [
                    {"id": "S3-a", "phase": 2040},
                    {"id": "S5-b"},
                    {"id": "S2-c", "phase": 2030},
                ]
            }
        )
    )
    tr = layout.tranches(layout.load_layout(p))
    assert [ph for ph, _ in tr] == [2030, 2040]
    assert [c["id"] for c in tr[0][1]] == ["S5-b", "S2-c"]


def test_bad_phase_rejected(tmp_path: Path) -> None:
    p = tmp_path / "l.yaml"
    p.write_text(yaml.safe_dump({"corridors": [{"id": "S3-a", "phase": 2033}]}))
    with pytest.raises(ValueError):
        layout.load_layout(p)


def test_corridor_path_by_family_prefix() -> None:
    root = Path(".")
    assert layout.corridor_path("S3-branch_spur-al-kharj", root) == Path(
        "cities/ksa/corridors/branch_spur/S3-branch_spur-al-kharj.yaml"
    )
    assert layout.corridor_path("S5-station_addition-al-jubayl", root).parts[3] == (
        "station_addition"
    )
