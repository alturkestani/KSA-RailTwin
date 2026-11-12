"""CLOSE_R10 (Tariq, 11 Nov 2026): trailer caption fix and the social-deliverable helpers."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from common import REPO_ROOT
from film.shots import load_shots
from film.social import concat_list, cue_html
from film.subs import Cue

NPV = re.compile(r"NPV|net present value|صافي القيمة الحالية|سالب", re.IGNORECASE)


def _shots() -> dict[str, dict]:
    return {s["id"]: s for s in load_shots(REPO_ROOT / "film/storyboard/shots.yaml")}


def test_trailer_shots_carry_no_npv_wording() -> None:
    for sid, s in _shots().items():
        if s.get("cut") != "trailer":
            continue
        text = str(s.get("visual", "")) + " ".join(
            str(v) for v in (s.get("on_screen_text") or {}).values()
        )
        assert not NPV.search(text), sid


def test_sh_08_51_plain_benefit_to_cost_wording() -> None:
    ost = _shots()["sh-08-51"]["on_screen_text"]
    assert "About 6 riyals back per riyal spent" in ost["en"]
    assert "كل ريال ينصرف يرجّع حوالي 6 ريالات" in ost["ar"]
    for lang in ("en", "ar"):  # the figures of the narration and the bar are kept
        assert "4.0" in ost[lang] and "5.6" in ost[lang]
    assert "S-r10-056" in _shots()["sh-08-51"]["data_source"]


def test_trailer_renderer_labels_carry_no_npv_wording() -> None:
    src = (REPO_ROOT / "film/sim.py").read_text("utf-8")
    block = src[src.index('S["sh-07-51"]') : src.index('S["sh-08-51"]')]
    assert not NPV.search(block)
    assert "benefits minus costs (worst population case)" in block


def test_caption_edit_log_rows() -> None:
    with (REPO_ROOT / "film/storyboard/caption-edits.csv").open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["shot_id"] in ("sh-07-51", "sh-08-51")]
    assert {(r["shot_id"], r["lang"]) for r in rows} == {
        (s, la) for s in ("sh-07-51", "sh-08-51") for la in ("en", "ar")
    }
    assert all(NPV.search(r["old"]) and not NPV.search(r["new"]) for r in rows)


def test_concat_list_fills_gaps_and_tail() -> None:
    blank, a, b = Path("/x/blank.png"), Path("/x/a.png"), Path("/x/b.png")
    cues = [Cue("1", 1.0, 2.5, ["one"]), Cue("2", 2.5, 4.0, ["two"])]
    lines = concat_list(cues, [a, b], blank, 10.0).splitlines()
    durs = [float(x.split()[1]) for x in lines if x.startswith("duration")]
    assert durs == [1.0, 1.5, 1.5, 6.0]
    assert sum(durs) == 10.0
    assert lines[-1] == f"file '{blank}'"  # concat demuxer: last file repeated


def test_cue_html_rtl_and_no_bidi_marks() -> None:
    h = cue_html(["‏مرحبا", "‏بكم"], "ar")
    assert 'dir="rtl"' in h and "‏" not in h
    assert 'dir="ltr"' in cue_html(["Hello"], "en")
