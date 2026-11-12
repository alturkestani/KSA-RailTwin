"""film.shots: storyboard schema and rules."""

from __future__ import annotations

import copy
from pathlib import Path

from typer.testing import CliRunner

from film import render, shots
from film.shots import check_shots, line_ids_by_cut, load_shots

FIX = Path(__file__).resolve().parent / "fixtures" / "film"
runner = CliRunner()


def _base() -> list[dict]:
    return load_shots(FIX / "shots.yaml")


def _ids() -> dict[str, set[str]]:
    return line_ids_by_cut(FIX / "script" / "lines.csv")


def test_fixture_passes() -> None:
    assert check_shots(_base(), _ids()) == []
    res = runner.invoke(
        shots.app, ["check", str(FIX / "shots.yaml"), "--lines", str(FIX / "script/lines.csv")]
    )
    assert res.exit_code == 0, res.output
    assert "PASS: 3 shots (main 8.9 s, trailer 2.6 s)" in res.output


def test_render_check_delegates() -> None:
    res = runner.invoke(render.app, ["check", str(FIX / "shots.yaml")])
    assert res.exit_code == 0 and "film.shots check PASS" in res.output


def _one(**changes) -> list[str]:
    s = copy.deepcopy(_base())
    s[1].update(changes)
    return check_shots(s, _ids())


def test_map_without_osm_credit() -> None:
    assert any("osm_credit" in e for e in _one(osm_credit=False))


def test_single_closing_notice() -> None:
    """FIX_HALF2_QUALITY: footer synthetic on each cut's last shot only, none elsewhere."""
    s = copy.deepcopy(_base())
    assert shots.check_closing_notice(s) == []
    s[0]["footer"] = "synthetic"  # a per-shot stamp in the middle of the main cut
    assert any("sh-01-01: footer must be none" in e for e in shots.check_closing_notice(s))
    s[0]["footer"] = "none"
    s[1]["footer"] = "none"  # the main cut's last shot lost the closing notice
    assert any("last main shot must carry" in e for e in shots.check_closing_notice(s))
    assert _one(footer="none") == []  # a run-sourced shot no longer needs its own footer


def test_unknown_narration_line_and_wrong_cut() -> None:
    assert any("m-09-09" in e for e in _one(narration_line_ids=["m-09-09"]))
    assert any("t-01 not in lines.csv for cut main" in e for e in _one(narration_line_ids=["t-01"]))


def test_ai_generated_needs_label() -> None:
    assert any("ai_label" in e for e in _one(ai_generated=True))
    assert _one(ai_generated=True, ai_label="AI-generated illustration") == []


def test_logo_rule() -> None:
    assert any("logo" in e for e in _one(visual="SAR logo over the map"))
    assert any("logo" in e for e in _one(logo="sar.png"))
    assert _one(visual="Map, no logo") == []


def test_enums_and_output() -> None:
    errs = _one(
        id="shot-1", type="drone", renderer="unreal", footer="maybe", output="renders/x.mp4"
    )
    for needle in (
        "sh-NN-NN",
        "type 'drone'",
        "renderer 'unreal'",
        "footer 'maybe'",
        "film/renders/",
    ):
        assert any(needle in e for e in errs), needle


def test_duplicate_id_and_none_source() -> None:
    s = copy.deepcopy(_base())
    s[2]["id"] = s[0]["id"]
    s[1]["data_source"] = "none"
    errs = check_shots(s, _ids())
    assert any("duplicate id" in e for e in errs)
    assert any("data_source 'none'" in e for e in errs)


def test_bad_duration_and_missing_key() -> None:
    s = copy.deepcopy(_base())
    s[0]["duration_s"] = 0
    del s[0]["visual"]
    errs = check_shots(s, None)
    assert any("duration_s" in e for e in errs)
    assert any("missing key visual" in e for e in errs)


def _rows() -> dict:
    return shots.load_line_rows(FIX / "script" / "lines.csv")


def test_duration_must_match_covered_english_lines() -> None:
    assert shots.check_durations(_base(), _rows()) == []
    s = copy.deepcopy(_base())
    s[1]["duration_s"] = 3.0
    errs = shots.check_durations(s, _rows())
    assert errs == ["sh-02-01: duration_s 3.0 != covered English lines 4.2"]
    s[1]["narration_line_ids"] = []  # an unnarrated shot (credits roll) is timed on its own
    assert shots.check_durations(s, _rows()) == []


def test_reused_or_held_picture_inherits_labels() -> None:
    s = copy.deepcopy(_base())
    s[1]["extra_credit"] = "Copernicus credit"
    s[0]["held_frame_from"] = ["sh-02-01"]  # title over the held synthetic map frame
    errs = shots.check_inheritance(s)
    for needle in ("osm_credit is not true", "needs extra_credit"):
        assert any(needle in e for e in errs), needle
    assert not any("weaker" in e for e in errs)  # footers are not inherited (FIX_HALF2_QUALITY)
    s[0].update(osm_credit=True, extra_credit="Copernicus credit")
    assert shots.check_inheritance(s) == []
    s[2].update(type="chart", reuse_of=["sh-02-01"])  # a chart re-cut keeps no map credit
    assert shots.check_inheritance(s) == []
    s[2]["reuse_of"] = ["sh-09-09"]
    assert any("unknown shot sh-09-09" in e for e in shots.check_inheritance(s))


def test_quote_label_is_per_language() -> None:
    s = copy.deepcopy(_base())
    s[0]["quote_label"] = True
    assert any("mapping with en and ar" in e for e in shots.check_quote_labels(s))
    s[0]["quote_label"] = {"en": True, "ar": True}
    assert shots.check_quote_labels(s) == []
    rows = _rows()
    rows[("main", "en", "m-01-01")]["on_screen_label"] = "quote"
    errs = shots.check_quote_lines(s, rows)
    assert any("quote_label.ar is true" in e for e in errs)  # the Arabic line paraphrases
    s[0]["quote_label"] = {"en": True, "ar": False}
    assert shots.check_quote_lines(s, rows) == []
    s[0]["quote_label"] = {"en": False, "ar": False}
    assert any("en quote line without quote_label" in e for e in shots.check_quote_lines(s, rows))


def test_storyboard_tables_round_trip(tmp_path: Path) -> None:
    meta = {"sections_en": {1: "One", 2: "Two"}, "sections_ar": {1: "واحد", 2: "اثنين"}}
    md = tmp_path / "storyboard.md"
    md.write_text("# x\n\n## 2. Shot list\n\nold\n\n#### stale\n\n## 3. Running times\n", "utf-8")
    shots.write_storyboard(md, _base(), meta)
    text = md.read_text(encoding="utf-8")
    assert shots.check_storyboard(text, _base(), meta) == []
    assert "#### Main cut, section 1: One / واحد (1 shots, 4.7 s)" in text
    s = copy.deepcopy(_base())
    s[1]["duration_s"] = 9.9
    assert any("differs" in e for e in shots.check_storyboard(text, s, meta))
    s = copy.deepcopy(_base())
    s[1]["on_screen_text"]["ar"] = "نص آخر"
    assert any("differs" in e for e in shots.check_storyboard(text, s, meta))
    meta2 = {**meta, "sections_en": {1: "Renamed", 2: "Two"}}
    assert any("differs" in e for e in shots.check_storyboard(text, _base(), meta2))
