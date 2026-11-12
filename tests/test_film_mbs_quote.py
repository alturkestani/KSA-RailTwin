"""FIX_MBS_QUOTE (Tariq, 11 Nov 2026): the Crown Prince population line states only what a
Saudi source confirms (Argaam, 26 Jul 2022: 50 to 60 million by 2030). Fast checks on committed
files only."""

from __future__ import annotations

import csv

import yaml

from common import REPO_ROOT

GONE = ("100 million", "2040", "100 مليون")
MAIN_FILES = [
    "film/subs/main.en.srt",
    "film/subs/main.en.vtt",
    "film/subs/main.ar.srt",
    "film/subs/main.ar.vtt",
    "film/script/main.en.md",
    "film/script/main.ar.md",
    "film/assemble/renders-main-en.csv",
    "film/assemble/renders-main-ar.csv",
]


def _rows(path: str) -> list[dict[str, str]]:
    with (REPO_ROOT / path).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_no_2040_figure_in_main_outputs() -> None:
    for r in _rows("film/script/lines.csv"):
        if r["cut"] == "main":
            assert not [g for g in GONE if g in r["text"] + r["speech_text"]], r["line_id"]
    shots = yaml.safe_load((REPO_ROOT / "film/storyboard/shots.yaml").read_text(encoding="utf-8"))
    for s in shots if isinstance(shots, list) else shots["shots"]:
        if s["cut"] == "main":
            text = " ".join((s.get("on_screen_text") or {}).values())
            assert not [g for g in GONE if g in text], s["id"]
    for f in MAIN_FILES:
        body = (REPO_ROOT / f).read_text(encoding="utf-8")
        assert not [g for g in GONE if g in body], f


def test_m_03_03_uses_the_saudi_source() -> None:
    rows = {(r["lang"], r["line_id"]): r for r in _rows("film/script/lines.csv")}
    for lang in ("en", "ar"):
        r = rows[lang, "m-03-03"]
        assert r["sources"].split(";")[0].strip() == "S-r10-057"
        assert [x.strip() for x in r["figure_values"].split(";")] == ["2022", "50", "60", "2030"]
    assert "50 to 60 million" in rows["en", "m-03-03"]["text"]
    assert "not a published programme target" in rows["en", "m-03-03"]["text"]
    ar = rows["ar", "m-03-03"]
    assert "بين 50 و60 مليون" in ar["text"] and "مو هدف منشور في برنامج رسمي" in ar["text"]
    assert ar["speech_text"] and ar["native_review"] == "pending"


def test_new_source_rows_and_edit_logs() -> None:
    src = {r["id"]: r for r in _rows("docs/sources/r10.csv")}
    assert "argaam.com/ar/" in src["S-r10-057"]["url"]
    assert "argaam.com/en/" in src["S-r10-058"]["url"]
    assert "france24.com" in src["S-r10-025"]["url"]
    edits = {(r["line_id"], r["lang"]) for r in _rows("film/storyboard/story-edits.csv")}
    assert ("m-03-03", "en") in edits and ("m-03-03", "ar") in edits
    rewords = [r for r in _rows("film/storyboard/ar-rewords.csv") if r["line_id"] == "m-03-03"]
    # FIX_MBS_TITLE appends a later row for the same line (tests/test_film_mbs_title.py)
    assert any(r["reason"].startswith("FIX_MBS_QUOTE") for r in rewords)
