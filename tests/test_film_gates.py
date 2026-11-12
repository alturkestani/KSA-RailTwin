"""R10 half-2 gate (film/gate.py): the commands stay shut unless every check passes.

Every CLI test closes the gate by pointing it at a volume that is not mounted, so nothing is
synthesised, rendered or assembled in CI; the unit tests drive evaluate() with a fake disk.
"""

from __future__ import annotations

import os
from collections import namedtuple
from pathlib import Path

import pytest
from typer.testing import CliRunner

from common import REPO_ROOT
from film import assemble, cli, gate, render, subs, voice
from film.gate import GATE_MESSAGE, LAUNCH_MARKER, evaluate

runner = CliRunner()
Usage = namedtuple("Usage", "total used free")
GiB = 1024**3


def _snapshot(*dirs: Path) -> set[str]:
    out: set[str] = set()
    for d in dirs:
        if d.exists():
            out |= {str(p) for p in d.rglob("*") if "__pycache__" not in str(p)}
    return out


@pytest.mark.parametrize(
    ("app", "args"),
    [
        (voice.app, ["speak", "--cut", "trailer", "--lang", "ar"]),
        (render.app, ["shot", "sh-01-01", "--lang", "en", "--dur", "1"]),
        (assemble.app, ["edl", "--cut", "trailer", "--lang", "en"]),
        (assemble.app, ["cut", "--cut", "trailer", "--lang", "en"]),
        (subs.app, ["build", "--cut", "trailer", "--lang", "en"]),
        (cli.app, ["voice", "speak", "--cut", "main", "--lang", "en"]),
    ],
)
def test_commands_closed_when_volume_missing(app, args, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("FILM_EXTERNAL_VOLUME", str(tmp_path / "not-mounted"))
    watched = [REPO_ROOT / "film" / d for d in ("script", "storyboard", "subs", "assemble")]
    before = _snapshot(*watched, tmp_path)
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        res = runner.invoke(app, args)
    finally:
        os.chdir(cwd)
    if app is assemble.app and args[0] == "cut" and res.exit_code == 1:
        # the edit list may be missing in a fresh clone: it fails before writing, also fine
        assert _snapshot(*watched, tmp_path) == before
        return
    assert res.exit_code == 2, res.output
    assert GATE_MESSAGE in res.output
    assert "not mounted" in res.output
    assert _snapshot(*watched, tmp_path) == before


def _root(tmp_path: Path, launched: bool = True, ext: Path | None = None) -> Path:
    root = tmp_path / "repo"
    (root / "docs/status").mkdir(parents=True)
    (root / "film").mkdir()
    text = "# status\n" + (f"{LAUNCH_MARKER} 7 Nov 2026\n" if launched else "")
    (root / "docs/status/r10.md").write_text(text, encoding="utf-8")
    if ext is not None:
        for d in ("renders", "audio"):
            (ext / d).mkdir(parents=True, exist_ok=True)
            (root / "film" / d).symlink_to(ext / d)
    return root


def _eval(root: Path, ext: Path, free_out: float, free_home: float, est: int = 0, mounted=True):
    def usage(path: str) -> Usage:
        return Usage(0, 0, int((free_home if path == "HOME" else free_out) * GiB))

    return evaluate(
        est,
        root=root,
        volume=str(ext.parent),
        external_root=str(ext),
        home_volume="HOME",
        usage=usage,
        is_mount=lambda p: mounted,
    )


def test_gate_opens_when_all_checks_pass(tmp_path: Path) -> None:
    ext = tmp_path / "vol" / "proj"
    rep = _eval(_root(tmp_path, ext=ext), ext, free_out=900, free_home=26)
    assert rep.ok, rep.failures


def test_gate_needs_recorded_launch(tmp_path: Path) -> None:
    ext = tmp_path / "vol" / "proj"
    rep = _eval(_root(tmp_path, launched=False, ext=ext), ext, 900, 26)
    assert not rep.ok and any("launch not recorded" in f for f in rep.failures)


def test_gate_needs_symlinks_onto_external(tmp_path: Path) -> None:
    ext = tmp_path / "vol" / "proj"
    ext.mkdir(parents=True)
    root = _root(tmp_path)
    (root / "film/renders").mkdir()  # a plain directory on the internal disk
    rep = _eval(root, ext, 900, 26)
    assert any("film/renders resolves to" in f for f in rep.failures)
    assert any("film/audio does not exist" in f for f in rep.failures)


def test_gate_render_floor_50_gib(tmp_path: Path) -> None:
    ext = tmp_path / "vol" / "proj"
    rep = _eval(_root(tmp_path, ext=ext), ext, free_out=49, free_home=26)
    assert any("50 GiB render gate" in f for f in rep.failures)


def test_gate_10_gb_floor_on_both_volumes(tmp_path: Path) -> None:
    ext = tmp_path / "vol" / "proj"
    root = _root(tmp_path, ext=ext)
    rep = _eval(root, ext, free_out=60, free_home=26, est=int(55 * GiB))
    assert any("under 10 GB free" in f for f in rep.failures)
    rep = _eval(root, ext, free_out=900, free_home=9)
    assert any("internal disk" in f for f in rep.failures)


def test_gate_unmounted(tmp_path: Path) -> None:
    ext = tmp_path / "vol" / "proj"
    rep = _eval(_root(tmp_path, ext=ext), ext, 900, 26, mounted=False)
    assert any("not mounted" in f for f in rep.failures)


def test_refuse_still_exits_2() -> None:
    import typer

    with pytest.raises(typer.Exit) as exc:
        gate.refuse()
    assert exc.value.exit_code == 2


def test_cli_help_lists_groups() -> None:
    res = runner.invoke(cli.app, ["--help"])
    assert res.exit_code == 0
    for name in ("script", "shots", "rights", "subs", "voice", "render", "assemble"):
        assert name in res.output
