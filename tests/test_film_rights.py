"""film.rights: the rights log rules."""

from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

from film import rights
from film.rights import check_rows, read_rows

FIX = Path(__file__).resolve().parent / "fixtures" / "film"
runner = CliRunner()


def test_fixture_passes() -> None:
    res = runner.invoke(rights.app, ["check", str(FIX / "rights_log.csv")])
    assert res.exit_code == 0, res.output
    assert "film.rights check PASS: 4 rows" in res.output


def _rows() -> list[dict[str, str]]:
    return read_rows(FIX / "rights_log.csv")


def test_xtts_in_film_cut_fails() -> None:
    rows = _rows()
    rows[2].update(status="used", used_in="film cut narration")
    errs = check_rows(rows)
    assert any("rejected or test_only" in e for e in errs)
    assert any("must not be used in a film cut" in e for e in errs)


def test_image_needs_attribution_and_link() -> None:
    rows = _rows()
    rows[3].update(attribution="", proof_link="commons page")
    errs = check_rows(rows)
    assert any("needs an attribution" in e for e in errs)
    assert any("proof_link must be an http(s) URL" in e for e in errs)


def test_enums_and_required() -> None:
    rows = _rows()
    rows[0].update(type="sticker", status="maybe", licence="")
    errs = check_rows(rows)
    assert any("type 'sticker'" in e for e in errs)
    assert any("status 'maybe'" in e for e in errs)
    assert any("licence is empty" in e for e in errs)


def test_bad_header(tmp_path: Path) -> None:
    f = tmp_path / "r.csv"
    shutil.copy(FIX / "rights_log.csv", f)
    f.write_text("item,type\nx,font\n", encoding="utf-8")
    res = runner.invoke(rights.app, ["check", str(f)])
    assert res.exit_code == 1
