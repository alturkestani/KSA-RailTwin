"""film.subs: SRT/VTT checks."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from film import subs
from film.subs import check_file

FIX = Path(__file__).resolve().parent / "fixtures" / "film"
runner = CliRunner()


def test_good_files_pass() -> None:
    for name in ("good.ar.srt", "good.en.vtt"):
        res = check_file(FIX / name)
        assert res.errors == [] and res.warnings == [], (name, res.errors, res.warnings)
        assert res.cues == 2


def test_bad_file_errors() -> None:
    errs = check_file(FIX / "bad.srt").errors
    assert any("overlaps cue 1" in e for e in errs)
    assert any("line of 60 chars" in e for e in errs)
    assert any("cps > 20" in e for e in errs)


def test_cli_dir(tmp_path: Path) -> None:
    for name in ("good.ar.srt", "good.en.vtt"):
        (tmp_path / name).write_bytes((FIX / name).read_bytes())
    res = runner.invoke(subs.app, ["check", str(tmp_path)])
    assert res.exit_code == 0 and "2 file(s), 4 cues" in res.output
    (tmp_path / "bad.srt").write_bytes((FIX / "bad.srt").read_bytes())
    assert runner.invoke(subs.app, ["check", str(tmp_path)]).exit_code == 1


def _srt(tmp_path: Path, body: str, name: str = "x.srt", bom: bool = False) -> Path:
    p = tmp_path / name
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + body.encode("utf-8"))
    return p


def test_gap_numbering_lines_duration_bom(tmp_path: Path) -> None:
    body = (
        "1\n00:00:01,000 --> 00:00:02,500\nOne line of text here\n\n"
        "3\n00:00:02,520 --> 00:00:10,000\na\nb\nc\n"
    )
    errs = check_file(_srt(tmp_path, body, bom=True)).errors
    for needle in ("BOM", "not consecutive", "< 2 frames", "3 lines", "duration 7.480"):
        assert any(needle in e for e in errs), needle


def test_bidi_marks_and_diacritics_not_counted(tmp_path: Path) -> None:
    line = "⁧" + "ب" * 40 + "⁩" + "‏"
    body = f"1\n00:00:01,000 --> 00:00:03,500\n{line}\n"
    assert check_file(_srt(tmp_path, body)).errors == []
    marked = "بَ" * 30  # 30 letters + 30 fathas over 2.5 s -> 12 cps counted, 60 chars long
    body = f"1\n00:00:01,000 --> 00:00:03,500\n{marked}\n"
    res = check_file(_srt(tmp_path, body))
    assert not any("cps" in e for e in res.errors)
    assert any("line of 60 chars" in e for e in res.errors)


def test_vtt_header_required(tmp_path: Path) -> None:
    p = _srt(tmp_path, "00:00:01.000 --> 00:00:03.000\nHello there, friends\n", "x.vtt")
    assert any("WEBVTT" in e for e in check_file(p).errors)


def test_build_is_gated(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("FILM_EXTERNAL_VOLUME", str(tmp_path / "not-mounted"))
    res = runner.invoke(subs.app, ["build", "--cut", "trailer", "--lang", "en"])
    assert res.exit_code == 2
    assert "R10 half 2 gate closed" in res.output
