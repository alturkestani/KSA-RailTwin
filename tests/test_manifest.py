from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from common import manifest
from common.schemas import SourceRow

runner = CliRunner()


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    (root / "data").mkdir(parents=True)
    (root / "data" / "a.bin").write_bytes(b"hello rail")
    m = root / "sources.yaml"
    m.write_text("# header kept\nmanifest_version: 1\nsources: []\n", encoding="utf-8")
    return root, m


def _add(root: Path, m: Path, **kw: str) -> object:
    args = {
        "--id": "t-1",
        "--name": "test file",
        "--publisher": "tests",
        "--url": "https://example.org/a.bin",
        "--edition": "1",
        "--licence": "CC0-1.0",
        "--path": "data/a.bin",
        "--used-in": "tests,common",
    }
    args.update(kw)
    cli = [
        "add",
        *[x for kv in args.items() for x in kv],
        "--manifest",
        str(m),
        "--root",
        str(root),
    ]
    return runner.invoke(manifest.app, cli)


def test_add_verify_round_trip(tmp_path: Path) -> None:
    root, m = _setup(tmp_path)
    res = _add(root, m)
    assert res.exit_code == 0, res.output
    text = m.read_text(encoding="utf-8")
    assert text.startswith("# header kept")
    row = yaml.safe_load(text)["sources"][0]
    SourceRow.model_validate(row)
    assert row["local_path"] == "data/a.bin"
    assert row["bytes"] == 10
    assert row["used_in"] == ["tests", "common"]
    assert row["sha256"] == manifest.sha256_file(root / "data" / "a.bin")
    res = runner.invoke(manifest.app, ["verify", "--manifest", str(m), "--root", str(root)])
    assert res.exit_code == 0, res.output
    assert "2 rows" not in res.output and "1 rows" in res.output


def test_verify_detects_mismatch(tmp_path: Path) -> None:
    root, m = _setup(tmp_path)
    assert _add(root, m).exit_code == 0
    (root / "data" / "a.bin").write_bytes(b"hello RAIL")  # same size, different bytes
    res = runner.invoke(manifest.app, ["verify", "--manifest", str(m), "--root", str(root)])
    assert res.exit_code == 1
    assert "sha256 mismatch" in res.output


def test_verify_detects_missing_field_and_file(tmp_path: Path) -> None:
    root, m = _setup(tmp_path)
    assert _add(root, m).exit_code == 0
    data = yaml.safe_load(m.read_text(encoding="utf-8"))
    data["sources"][0]["licence"] = ""
    m.write_text(yaml.safe_dump(data), encoding="utf-8")
    problems = manifest.verify_rows(m, root)
    assert any("missing field licence" in p for p in problems)
    (root / "data" / "a.bin").unlink()
    assert any("file missing" in p for p in manifest.verify_rows(m, root))
    assert not any("file missing" in p for p in manifest.verify_rows(m, root, allow_missing=True))


def test_add_rejects_duplicate_and_outside_paths(tmp_path: Path) -> None:
    root, m = _setup(tmp_path)
    assert _add(root, m).exit_code == 0
    assert _add(root, m).exit_code != 0  # duplicate id
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"x")
    assert _add(root, m, **{"--id": "t-2", "--path": str(outside)}).exit_code != 0


def test_manifest_hash_changes_with_content(tmp_path: Path) -> None:
    root, m = _setup(tmp_path)
    h0 = manifest.manifest_hash(m)
    assert _add(root, m).exit_code == 0
    assert manifest.manifest_hash(m) != h0


def test_repo_manifest_rows_are_well_formed() -> None:
    data = manifest.load()
    for row in data["sources"]:
        SourceRow.model_validate(row)
    # structural check only (CI has no data/); hashes are checked by `make test`
    assert not [
        p for p in manifest.verify_rows(manifest.DEFAULT_MANIFEST, manifest.REPO_ROOT, True)
    ]


@pytest.mark.parametrize("bad", ["/abs/path", "~/x"])
def test_source_row_rejects_absolute_paths(bad: str) -> None:
    with pytest.raises(ValueError):
        SourceRow.model_validate(
            {
                "id": "x",
                "name": "x",
                "publisher": "x",
                "url": "x",
                "edition": "x",
                "licence": "x",
                "accessed": "2026-10-30",
                "local_path": bad,
            }
        )
