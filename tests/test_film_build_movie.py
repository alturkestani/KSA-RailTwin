"""BUILD_MOVIE (Tariq, 10 Nov 2026): every main shot is a sim_map shot with one full-sentence
caption; every main Arabic line has full tashkeel except the listed exceptions; Arabic rewords
change no digit; m-08-06 stays byte-identical."""

from __future__ import annotations

import csv
import re

from common import REPO_ROOT
from film import script, shots

LINES = REPO_ROOT / "film/script/lines.csv"
SHOTS = REPO_ROOT / "film/storyboard/shots.yaml"
TASHKEEL = re.compile("[ً-ْٰ]")
ARABIC = re.compile("[ء-ي]")
# words proven to read worse when vocalised (FIX_HALF2_QUALITY read-back; BUILD_MOVIE item 3)
BARE_OK = {"مليون", "مليار", "المجدولة"}
M_08_06 = {
    "en": "What comes back? For the committed lines over 60 years, the model puts users' travel "
    "time and cost savings, in present value, at 2.3 to 19.3 billion riyals, and a safety "
    "benefit, road deaths and injuries avoided valued at standard appraisal values, at 0.6 to "
    "7.4 billion.",
}


def _rows() -> list[dict[str, str]]:
    with LINES.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_every_main_shot_is_sim_map_with_credits_and_legend() -> None:
    main = [s for s in shots.load_shots(SHOTS) if s["cut"] == "main"]
    assert len(main) == 64  # 58 + sh-08-15..20 (FIX_FILM_STORY)
    for s in main:
        assert s["renderer"] == "sim_map", s["id"]
        assert s.get("osm_credit") and s.get("extra_credit") and s.get("layer_legend"), s["id"]


def test_main_captions_are_full_sentences() -> None:
    for s in shots.load_shots(SHOTS):
        if s["cut"] != "main" or s["id"] == "sh-08-14":  # the credits roll keeps its title
            continue
        for lang in ("en", "ar"):
            t = str(s["on_screen_text"][lang]).strip()
            assert "·" not in t, (s["id"], lang)
            assert t[-1] in ".?!؟'’\"»", (s["id"], lang, t)


def test_main_arabic_lines_fully_vocalised() -> None:
    ar = [r for r in _rows() if r["cut"] == "main" and r["lang"] == "ar"]
    assert len(ar) == 68  # 62 + m-08-14..19 (FIX_FILM_STORY)
    say = script.read_say(REPO_ROOT / "film/script")
    for r in ar:
        assert r["speech_text"], r["line_id"]
        assert script.speech_text_errors(r, say) == [], r["line_id"]
        for w in r["speech_text"].split():
            if ARABIC.search(w) and not TASHKEEL.search(w):
                assert re.sub("[^ء-ي]", "", w) in BARE_OK, (r["line_id"], w)


def test_rewords_keep_digits() -> None:
    with (REPO_ROOT / "film/storyboard/ar-rewords.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows
    # FIX_FILM_STORY and FIX_MBS_QUOTE rows rewrite lines with new figures by design; the
    # FIX_MBS_TITLE row adds a name by design (tests/test_film_story.py,
    # tests/test_film_mbs_quote.py, tests/test_film_mbs_title.py).
    fixes = ("FIX_FILM_STORY", "FIX_MBS_QUOTE", "FIX_MBS_TITLE")
    rows = [r for r in rows if not r["reason"].startswith(fixes)]
    for r in rows:
        assert r["digits_identical"] == "yes" and r["names_identical"] == "yes"
        if r["field"] == "text":
            assert re.findall(r"\d", r["old"]) == re.findall(r"\d", r["new"]), r["line_id"]
    assert "m-08-06" not in {r["line_id"] for r in rows}


def test_m_08_06_text_byte_identical() -> None:
    rows = {(r["cut"], r["lang"], r["line_id"]): r for r in _rows()}
    # FIX_FILM_STORY (Tariq, 10 Nov 2026): the only change allowed and listed is the finance term.
    want = M_08_06["en"].replace("in present value", "in today's money")
    assert rows[("main", "en", "m-08-06")]["text"] == want
    ar = rows[("main", "ar", "m-08-06")]
    assert ar["text"].startswith("وكم يرجع؟ للخطوط الملتزم بها خلال 60 سنة، النموذج يقدّر")
    assert script.strip_tashkeel(ar["speech_text"]) == script.strip_tashkeel(ar["text"])
