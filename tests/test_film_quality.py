"""FIX_HALF2_QUALITY (Tariq, 8 Nov 2026): tashkeel never changes a digit or a name, the
in-the-model / uncalibrated refrain is gone, the single closing notice sits on each cut's last
shot only, and the delivered trailers stay within 60-90 s."""

from __future__ import annotations

import csv
import re

from common import REPO_ROOT
from film import script, shots

LINES = REPO_ROOT / "film/script/lines.csv"
SHOTS = REPO_ROOT / "film/storyboard/shots.yaml"
REFRAIN = (
    "in the model",
    "in this model",
    "uncalibrated",
    "synthetic",
    "في النموذج",
    "هالنموذج",
    "غير معاير",
)


def _rows() -> list[dict[str, str]]:
    with LINES.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_speech_text_only_adds_tashkeel() -> None:
    say = script.read_say(REPO_ROOT / "film/script")
    rows = [r for r in _rows() if r.get("speech_text")]
    assert rows, "no vocalised lines"
    for r in rows:
        assert r["lang"] == "ar"
        assert script.speech_text_errors(r, say) == [], r["line_id"]
        base = say.get((r["cut"], r["lang"], r["line_id"]), r["text"])
        # digits identical, in order; letters identical once the marks are removed
        assert re.findall(r"\d", r["speech_text"]) == re.findall(r"\d", base)
        assert script.strip_tashkeel(r["speech_text"]) == script.strip_tashkeel(base)


def test_speech_text_check_catches_changes() -> None:
    r = {"cut": "trailer", "lang": "ar", "line_id": "t-04", "text": "بلد فيه 35.3 مليون"}
    r["speech_text"] = "بَلَد فِيه 35.3 مليون"
    assert script.speech_text_errors(r, {}) == []
    for bad in ("بَلَد فِيه 35.4 مليون", "بَلَد فِيه 35.3 مليار", "بَلَد 35.3 مليون"):
        assert script.speech_text_errors({**r, "speech_text": bad}, {}) != []
    assert script.speech_text_errors({**r, "lang": "en"}, {}) != []


def test_refrain_dropped_from_script_and_shots() -> None:
    for r in _rows():
        low = script.normalise(r["text"]).lower().replace("مُعايَر", "معاير")
        assert not any(p in low for p in REFRAIN), (r["cut"], r["lang"], r["line_id"])
        assert r["on_screen_label"] not in ("synthetic", "synthetic+not_official")
    for s in shots.load_shots(SHOTS):
        for lang in ("en", "ar"):
            low = s["on_screen_text"][lang].lower().replace("مُعايَر", "معاير")
            assert not any(p in low for p in REFRAIN), (s["id"], lang)


def test_single_closing_notice_on_real_shots() -> None:
    sl = shots.load_shots(SHOTS)
    assert shots.check_closing_notice(sl) == []
    last = {s["cut"]: s["id"] for s in sl}
    assert last == {"main": "sh-08-14", "trailer": "sh-08-54"}


def test_closing_notice_wording_uses_glossary_term_4() -> None:
    from film import render, sim

    assert "طلب تركيبي غير مُعايَر" in sim.CLOSING_NOTICE["ar"]
    assert sim.CLOSING_NOTICE["en"].lower().startswith("synthetic demand, uncalibrated")
    assert any("طلب تركيبي غير مُعايَر" in x for x in render.credits_lines("ar"))
    assert any(x.lower().startswith("synthetic demand") for x in render.credits_lines("en"))


def test_trailer_shots_use_the_sim_renderer() -> None:
    for s in shots.load_shots(SHOTS):
        if s["cut"] == "trailer":
            assert s["renderer"] == "sim_map", s["id"]


def test_delivered_trailer_length() -> None:
    for lang in ("en", "ar"):
        p = REPO_ROOT / f"film/assemble/edl-trailer-{lang}.csv"
        with p.open(encoding="utf-8", newline="") as fh:
            total = sum(float(r["duration_s"]) for r in csv.DictReader(fh))
        assert 60.0 <= total <= 90.0, (lang, total)


def test_m_08_06_unchanged_by_the_refrain_edit() -> None:
    with (REPO_ROOT / "film/script/refrain-edits.csv").open(encoding="utf-8") as fh:
        edited = {r["line_id"] for r in csv.DictReader(fh) if r["old"] != r["new"]}
    assert "m-08-06" not in edited
    for r in csv.DictReader((REPO_ROOT / "film/script/refrain-edits.csv").open(encoding="utf-8")):
        if r["new"].startswith("(line removed"):
            continue
        assert re.findall(r"\d+(?:\.\d+)?", r["old"]) == re.findall(r"\d+(?:\.\d+)?", r["new"])
