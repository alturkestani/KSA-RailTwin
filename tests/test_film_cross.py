"""film.cross: cross-language subtitles of the main cuts (FILM_SUBS, 13 Nov 2026)."""

from __future__ import annotations

from pathlib import Path

import pytest

from film import cross
from film.subs import check_file

PAIRS = list(cross.PAIRS)


@pytest.mark.parametrize("pair", PAIRS)
def test_tables_pass_figures_names_honorific(pair: str) -> None:
    assert cross.table_errors(pair) == []


@pytest.mark.parametrize("pair", PAIRS)
def test_committed_srt_and_vtt_are_generated_from_the_table(
    pair: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cross, "SUBS", tmp_path)
    srt, vtt = cross.write(pair, cross.build_cues(pair))
    for f in (srt, vtt):
        committed = Path(cross.__file__).parent / "subs" / f.name
        assert committed.read_bytes() == f.read_bytes(), f.name


@pytest.mark.parametrize("pair", PAIRS)
def test_srt_limits_and_alignment(pair: str) -> None:
    for ext in ("srt", "vtt"):
        res = check_file(cross.SUBS / f"{pair}.{ext}")
        assert res.errors == [], res.errors[:3]
    assert cross.align_errors(pair) == []
    st = cross.stats(cross.SUBS / f"{pair}.srt")
    assert st["max_lines"] <= 2 and st["max_chars_per_line"] <= 42
    assert st["shortest_s"] >= 1.0 and st["longest_s"] <= 7.0


def _row(pair: str, lid: str) -> dict:
    return next(r for r in cross.table(pair) if r["line_id"] == lid)


def test_figure_check_catches_a_changed_digit() -> None:
    r = dict(_row("main-ar.en", "m-03-01"))
    r["subtitle_text"] = r["subtitle_text"].replace("32,175,224", "32,175,234")
    assert any("figures differ" in e for e in cross.row_errors(r, "ar", "en"))


def test_figure_check_needs_the_spelled_word() -> None:
    r = dict(_row("main-en.ar", "m-01-07"))
    assert r["spelled_figures"] == "1:ساعة"
    assert cross.row_errors(r, "en", "ar") == []
    r["spelled_figures"] = ""
    assert any("figures differ" in e for e in cross.row_errors(r, "en", "ar"))


def test_name_check_catches_a_dropped_name() -> None:
    r = dict(_row("main-ar.en", "m-08-02"))
    r["subtitle_text"] = r["subtitle_text"].replace("Duruma", "a third town")
    assert any("Duruma" in e for e in cross.row_errors(r, "ar", "en"))


@pytest.mark.parametrize(
    ("pair", "src", "sub"), [("main-ar.en", "ar", "en"), ("main-en.ar", "en", "ar")]
)
def test_honorific_is_full(pair: str, src: str, sub: str) -> None:
    r = dict(_row(pair, "m-03-03"))
    assert cross.HONORIFIC[sub] in r["subtitle_text"]
    r["subtitle_text"] = r["subtitle_text"].replace(cross.HONORIFIC[sub], "Mohammed bin Salman")
    assert any("honorific" in e for e in cross.row_errors(r, src, sub))


def test_arabic_subtitles_pending_review_and_no_tashkeel() -> None:
    rows = cross.table("main-en.ar")
    assert {r["native_review"] for r in rows} == {"pending"}
    assert not any(cross.TASHKEEL.search(r["subtitle_text"]) for r in rows)


def test_li_floor_reports_infeasible_target_and_split() -> None:
    p = cross.li_floor()
    assert p["floor_speech_only_s"] > p["target_s"]  # speech alone exceeds 14:50
    assert p["floor_speech_only_s"] <= p["floor_low_range_s"] <= p["current_s"]
    b = p["best_split"]
    assert b["before_section"] == "6"
    assert max(b["part1_s"], b["part2_s"]) <= p["target_s"]
