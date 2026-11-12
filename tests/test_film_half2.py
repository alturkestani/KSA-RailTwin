"""R10 half 2 helpers: subtitle cue cutting, the edit list, spoken text and key reading."""

from __future__ import annotations

from pathlib import Path

from film import assemble, subs, voice
from film.subs import MAX_CHARS, MAX_DUR, MIN_DUR, Cue, Result, check_cues


def test_wrap_and_chunks_respect_limits() -> None:
    text = (
        "Who is off this map? The study screened all 150 governorates. In the 2022 census, "
        "Taif had about 913 thousand people; Tabuk, 624 thousand; Khamis Mushait, 601 thousand."
    )
    for ch in subs.chunks(text):
        rows = subs.wrap(ch)
        assert len(rows) <= 2 and all(len(r) <= MAX_CHARS for r in rows)
    assert " ".join(subs.chunks(text)) == " ".join(text.split())


def test_line_cues_fit_interval_and_pass_checker() -> None:
    text = "طيب، مين برّا هالخريطة؟ الدراسة فرزت كل المحافظات الـ150. في تعداد 2022، " * 2
    cues = subs.line_cues(text, 10.0, 34.0)
    assert cues[0][0] == 10.0 and abs(cues[-1][1] - 34.0) < 1e-6
    res = Result()
    check_cues(
        [Cue(str(i), s, e, subs.render_cue(t, "ar")) for i, (s, e, t) in enumerate(cues)], 30, res
    )
    assert not res.errors, res.errors
    assert all(MIN_DUR <= e - s <= MAX_DUR for s, e, _ in cues)
    assert all(row.startswith(subs.RLM) for row in subs.render_cue(cues[0][2], "ar"))


def test_edl_uses_measured_seconds() -> None:
    shots = [
        {
            "id": "sh-01-01",
            "cut": "main",
            "section": 1,
            "duration_s": 6.9,
            "narration_line_ids": ["m-01-01", "m-01-02"],
        },
        {
            "id": "sh-08-14",
            "cut": "main",
            "section": 8,
            "duration_s": 20.0,
            "narration_line_ids": [],
        },
        {
            "id": "sh-08-54",
            "cut": "trailer",
            "section": 8,
            "duration_s": 2.6,
            "narration_line_ids": ["t-11"],
        },
    ]
    timing = {"m-01-01": {"seconds": "5.0"}, "m-01-02": {"seconds": "4.0"}}
    cfg = {
        "shot_head_s": {"value": 0.5},
        "shot_tail_s": {"value": 1.0},
        "gap_between_lines_s": {"value": 0.3},
    }
    edl, lines = assemble.build_edl("main", "en", shots, timing, cfg)
    assert [r["shot_id"] for r in edl] == ["sh-01-01", "sh-08-14"]
    assert abs(edl[0]["duration_s"] - 10.8) < 0.04
    assert edl[1]["duration_s"] == 20.0 and abs(edl[1]["start_s"] - edl[0]["duration_s"]) < 1e-6
    assert lines[0]["start_s"] == 0.5 and lines[1]["start_s"] == 5.8


def test_spoken_text_override_and_roles() -> None:
    row = {"cut": "main", "lang": "en", "line_id": "m-01-01", "text": " A  b ", "section": "6"}
    assert voice.spoken_text(row, {}) == ("A b", False)
    assert voice.spoken_text(row, {("main", "en", "m-01-01"): "A  B"}) == ("A B", True)
    cfg = voice.load_config()
    assert voice.voice_for(row, cfg) == "Daniah"
    assert set(cfg["roles_by_section"]["value"].values()) == {"Abdullah", "Norah", "Daniah"}


def test_read_key_from_env_file_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("FAKE_API_KEY", raising=False)
    f = tmp_path / ".env"
    f.write_text("export FAKE_API_KEY='abc123'\nOTHER=1\n", encoding="utf-8")
    assert voice.read_key("FAKE_API_KEY", f) == "abc123"
    assert voice.read_key("MISSING_API_KEY", f) is None
    assert voice.read_key("FAKE_API_KEY", tmp_path / "nope") is None
