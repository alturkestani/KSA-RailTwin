"""film.script: the lines.csv rules, estimate and render (fixture script in tests/fixtures/film)."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from common.docver import check_file
from film import script
from film.script import COLUMNS, normalise, number_tokens, render_all, validate_dir

FIX = Path(__file__).resolve().parent / "fixtures" / "film"
TIMING = FIX / "timing.yaml"
ROOT = FIX / "root"
runner = CliRunner()


@pytest.fixture
def sdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv("RAILTWIN_RUNS_ROOT", raising=False)
    d = tmp_path / "script"
    shutil.copytree(FIX / "script", d)
    return d


def _rows(d: Path) -> list[dict[str, str]]:
    with (d / "lines.csv").open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _edit(d: Path, line_id: str, lang: str | None = None, rerender: bool = True, **changes: str):
    rows = _rows(d)
    for r in rows:
        if r["line_id"] == line_id and (lang is None or r["lang"] == lang):
            r.update(changes)
    script.write_lines(d, rows)
    if rerender:
        runner.invoke(script.app, ["estimate", str(d), "--timing", str(TIMING)])
        runner.invoke(script.app, ["render", str(d)])


def _errors(d: Path, **kw) -> list[str]:
    kw.setdefault("duration_limits", False)
    rep, _ = validate_dir(d, TIMING, ROOT, **kw)
    return rep.errors


def _has(errors: list[str], needle: str) -> bool:
    return any(needle in e for e in errors)


def test_fixture_passes(sdir: Path) -> None:
    rep, rows = validate_dir(sdir, TIMING, ROOT, duration_limits=False)
    assert rep.errors == []
    assert len(rows) == 12
    assert len(rep.warnings) == 2  # run: path unverifiable without RAILTWIN_RUNS_ROOT


def test_cli_validate_pass(sdir: Path) -> None:
    args = ["validate", str(sdir), "--timing", str(TIMING), "--ids-root", str(ROOT)]
    res = runner.invoke(script.app, [*args, "--no-duration-limits"])
    assert res.exit_code == 0, res.output
    assert "film.script validate PASS: 12 lines" in res.output


def test_strict_runs_and_runs_root(sdir: Path, tmp_path: Path, monkeypatch) -> None:
    assert _has(_errors(sdir, strict_runs=True), "unverifiable")
    runs = tmp_path / "main-runs"
    (runs / "fx").mkdir(parents=True)
    (runs / "fx" / "result.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("RAILTWIN_RUNS_ROOT", str(runs))
    rep, _ = validate_dir(sdir, TIMING, ROOT, strict_runs=True, duration_limits=False)
    assert rep.errors == [] and rep.warnings == []
    (runs / "fx" / "result.json").unlink()
    assert _has(_errors(sdir), "not found (repo or RAILTWIN_RUNS_ROOT)")


def test_unknown_s_id(sdir: Path) -> None:
    _edit(sdir, "m-01-01", sources="S-fx-999")
    assert _has(_errors(sdir), "S-fx-999 not found")


def test_unknown_a_id_and_doc_path(sdir: Path) -> None:
    _edit(sdir, "t-02", sources="A-fx-999;doc:docs/missing.md")
    errs = _errors(sdir)
    assert _has(errs, "A-fx-999 not found")
    assert _has(errs, "doc path docs/missing.md does not exist")


def test_missing_source(sdir: Path) -> None:
    _edit(sdir, "m-01-02", lang="en", sources="")
    assert _has(_errors(sdir), "no source")


def test_bad_source_token(sdir: Path) -> None:
    _edit(sdir, "m-01-02", sources="https://example.org")
    assert _has(_errors(sdir), "is not S-, A-, run: or doc:")


def test_number_not_in_figure_values(sdir: Path) -> None:
    _edit(sdir, "m-01-02", lang="en", text="The existing line runs 454 km between the cities.")
    assert _has(_errors(sdir), "numbers in text not in figure_values: 454")


def test_arabic_indic_normalisation() -> None:
    assert normalise("٢٬٩٥٨ و١٫٥ و۴۵٪") == "2958 و1.5 و45%"
    assert number_tokens("من ٢٬٩٥٨ إلى 4,100 (m-01-02, S-fx-001)") == ["2958", "4100"]


def test_arabic_digits_must_match_figures(sdir: Path) -> None:
    _edit(sdir, "m-01-01", lang="ar", text="تعرّفوا على نورة، تسوق ٤٦ دقيقة كل اتجاه.")
    assert _has(_errors(sdir), "numbers in text not in figure_values: 46")


def test_bilingual_figure_mismatch(sdir: Path) -> None:
    _edit(sdir, "m-01-02", lang="ar", figure_values="453;2", text="الخط القائم 453 كم و2 محطة.")
    assert _has(_errors(sdir), "m-01-02: figure_values differ")


def test_bilingual_missing_line_and_section(sdir: Path) -> None:
    rows = [r for r in _rows(sdir) if not (r["line_id"] == "t-01" and r["lang"] == "ar")]
    script.write_lines(sdir, rows)
    assert _has(_errors(sdir), "trailer/t-01: in en but not in ar")
    _edit(sdir, "m-01-02", lang="ar", section="2")
    assert _has(_errors(sdir), "m-01-02: section differs")


def test_run_source_needs_synthetic_label(sdir: Path) -> None:
    _edit(sdir, "m-02-01", lang="en", on_screen_label="")
    assert _has(_errors(sdir), "run: source needs on_screen_label synthetic* or none")
    _edit(sdir, "m-02-01", lang="en", on_screen_label="none")  # FIX_HALF2_QUALITY: stamp dropped
    assert not _has(_errors(sdir), "run: source needs")


def test_side_study_needs_not_official(sdir: Path) -> None:
    _edit(sdir, "m-02-02", lang="en", on_screen_label="synthetic")
    assert _has(_errors(sdir), "synthetic+not_official")
    _edit(sdir, "t-01", sources="doc:docs/extra-travel-study.md")
    assert _has(_errors(sdir), "t-01): side-study source")


@pytest.mark.parametrize(
    ("lang", "text"),
    [
        ("en", "In the model, rail will reduce travel time by 1.5 hours."),
        ("en", "We GUARANTEE 1.5 hours."),
        ("en", "The Transit Costs figure 1.5"),
        ("ar", "في النموذج سوف يقل الوقت ١٫٥ ساعة."),
    ],
)
def test_banned_phrases(sdir: Path, lang: str, text: str) -> None:
    _edit(sdir, "m-02-01", lang=lang, text=text)
    assert _has(_errors(sdir), "banned phrase")


def test_saw_allowed_in_non_synthetic_ar_line(sdir: Path) -> None:
    _edit(sdir, "t-01", lang="ar", text="سوف تربط السكة البلد.")
    assert not _has(_errors(sdir), "banned phrase")


def test_stale_render(sdir: Path) -> None:
    _edit(sdir, "t-01", lang="en", rerender=False, text="A railway that connects the country.")
    runner.invoke(script.app, ["estimate", str(sdir), "--timing", str(TIMING)])
    errs = _errors(sdir)
    assert _has(errs, "trailer.en.md is missing or stale")
    assert not _has(errs, "main.en.md")


def test_stale_estimate(sdir: Path) -> None:
    _edit(sdir, "t-01", lang="en", rerender=False, est_seconds="9.9")
    assert _has(_errors(sdir), "est_seconds 9.9 != estimate 2.6")


def test_schema_enums(sdir: Path) -> None:
    _edit(sdir, "t-02", lang="ar", native_review="n/a", on_screen_label="maybe", section="9")
    errs = _errors(sdir)
    assert _has(errs, "native_review 'n/a' invalid for lang ar")
    assert _has(errs, "on_screen_label 'maybe'")
    assert _has(errs, "section '9'")
    rows = _rows(sdir)
    rows[-1]["line_id"] = "m-01-09"
    rows[-1]["section"] = "x"
    script.write_lines(sdir, rows)
    errs = _errors(sdir)
    assert _has(errs, "does not match")
    assert _has(errs, "render failed")


def test_duration_limits(sdir: Path) -> None:
    """Over the ceiling is an error; under the floor is a warning since FIX_HALF2_QUALITY (the
    delivered cut, with shot heads and tails, is checked on the edit list instead)."""
    rep, _ = validate_dir(sdir, TIMING, ROOT, duration_limits=True)
    assert not any("total" in e for e in rep.errors)
    assert sum("spoken estimate" in w for w in rep.warnings) == 4
    assert any(w.startswith("main/ar: spoken estimate") for w in rep.warnings)
    _edit(sdir, "t-01", lang="en", rerender=False, est_seconds="95.0")
    rep, _ = validate_dir(sdir, TIMING, ROOT, duration_limits=True)
    assert any(e.startswith("trailer/en: total") for e in rep.errors)


def test_estimate_formula() -> None:
    t = {"ar": 14.0, "en": 15.0, "pause": 0.4}
    assert script.estimate_seconds("abc   def\n", "en", t) == round(7 / 15 + 0.4, 1)


def test_render_deterministic_and_headers(sdir: Path) -> None:
    a = render_all(sdir)
    assert a == render_all(sdir)
    for name in a:
        assert check_file(sdir / name) is None
    assert '<div dir="rtl">' in a["main.ar.md"] and "<div" not in a["main.en.md"]
    assert "[^m-02-02]: S-xt-001; A-fx-001" in a["main.en.md"]
    assert "*(on screen: synthetic)*" in a["main.en.md"]
    assert "*(على الشاشة: composite)*" in a["main.ar.md"]


def test_estimate_keeps_order_and_format(sdir: Path) -> None:
    before = (sdir / "lines.csv").read_bytes()
    res = runner.invoke(script.app, ["estimate", str(sdir), "--timing", str(TIMING)])
    assert res.exit_code == 0
    assert (sdir / "lines.csv").read_bytes() == before
    assert list(_rows(sdir)[0]) in (COLUMNS, COLUMNS[:-1])  # speech_text is optional


def test_real_meta_renders_valid_headers(tmp_path: Path) -> None:
    meta = Path(script.REPO_ROOT) / "film" / "script" / "meta.yaml"
    shutil.copy(meta, tmp_path / "meta.yaml")
    shutil.copy(FIX / "script" / "lines.csv", tmp_path / "lines.csv")
    for name, text in render_all(tmp_path).items():
        (tmp_path / name).write_text(text, encoding="utf-8")
        assert check_file(tmp_path / name) is None
