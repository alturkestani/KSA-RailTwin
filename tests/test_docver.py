import datetime as dt
from pathlib import Path

from typer.testing import CliRunner

from common import docver

runner = CliRunner()
GOOD = (
    "> **Document version:** docs/x.md v1.2 | 30 Oct 2026 | Author: tests | Status: draft\n\n# X\n"
)


def test_repo_docs_have_headers() -> None:
    res = runner.invoke(docver.app, ["check"])
    assert res.exit_code == 0, res.output


def test_check_accepts_front_matter_and_rejects_missing(tmp_path: Path) -> None:
    ok = tmp_path / "ok.md"
    ok.write_text("---\nname: a\n---\n" + GOOD, encoding="utf-8")
    bad = tmp_path / "bad.md"
    bad.write_text("# no header\n", encoding="utf-8")
    assert docver.check_file(ok) is None
    assert docver.check_file(bad) is not None
    res = runner.invoke(docver.app, ["check", str(tmp_path)])
    assert res.exit_code == 1 and "bad.md" in res.output


def test_bump_minor_major_and_date() -> None:
    day = dt.date(2026, 11, 2)
    out = docver.bump_text(GOOD, today=day)
    assert out.startswith("> **Document version:** docs/x.md v1.3 | 2 Nov 2026 | Author: tests")
    out = docver.bump_text(GOOD, major=True, today=day)
    assert "v2.0 | 2 Nov 2026" in out
    assert out.endswith("# X\n")
    iso = GOOD.replace("30 Oct 2026", "2026-10-30")
    assert "v1.3 | 2026-11-02 |" in docver.bump_text(iso, today=day)


def test_iter_md_inside_a_worktree_checkout(tmp_path: Path) -> None:
    """A checkout under .worktrees/ checks its own files but skips nested worktrees."""
    root = tmp_path / "KSA-RailTwin" / ".worktrees" / "r1b"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "a.md").write_text(GOOD, encoding="utf-8")
    nested = root / "docs" / ".worktrees" / "x"
    nested.mkdir(parents=True)
    (nested / "b.md").write_text(GOOD, encoding="utf-8")
    found = docver.iter_md(["docs"], root=root)
    assert [f.name for f in found] == ["a.md"]
