"""R10 half 1: the real film files pass their own checkers (scripts, shot list, rights log)."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import yaml
from typer.testing import CliRunner

from film import rights, script, shots

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()


def test_script_validates() -> None:
    res = RUNNER.invoke(script.app, ["validate", str(REPO_ROOT / "film/script")])
    assert res.exit_code == 0, res.output


def test_shots_check_against_lines() -> None:
    args = ["check", str(REPO_ROOT / "film/storyboard/shots.yaml")]
    args += ["--lines", str(REPO_ROOT / "film/script/lines.csv")]
    res = RUNNER.invoke(shots.app, args)
    assert res.exit_code == 0, res.output


def test_every_line_has_a_shot() -> None:
    covered = {
        i
        for s in shots.load_shots(REPO_ROOT / "film/storyboard/shots.yaml")
        for i in s.get("narration_line_ids") or []
    }
    with (REPO_ROOT / "film/script/lines.csv").open(encoding="utf-8", newline="") as fh:
        ids = {r["line_id"] for r in csv.DictReader(fh)}
    assert ids - covered == set()


def test_rights_log_checks() -> None:
    res = RUNNER.invoke(rights.app, ["check", str(REPO_ROOT / "film/rights_log.csv")])
    assert res.exit_code == 0, res.output


def test_no_render_outputs_committed() -> None:
    tracked = (REPO_ROOT / "film").rglob("*")
    media = {".mp4", ".mov", ".wav", ".mp3", ".flac", ".png"}
    assert [
        p
        for p in tracked
        if p.suffix in media
        and "audio" not in p.parts
        and "renders" not in p.parts
        and not (p.suffix == ".png" and p.parent == REPO_ROOT / "film/subs/qa")
    ] == []  # R10_HALF2: the subtitle RTL QA screenshots belong in film/subs/qa/ (prompt)


def test_arabic_label_term_follows_glossary() -> None:
    """Glossary term 4: «طلب تركيبي غير مُعايَر»; «اصطناعي» is on the avoid list."""
    files = [REPO_ROOT / "film/script.py", REPO_ROOT / "film/storyboard/storyboard.md"]
    files += [REPO_ROOT / "film/storyboard/shots.yaml", REPO_ROOT / "film/script/lines.csv"]
    files += sorted((REPO_ROOT / "film/script").glob("*.ar.md"))
    assert [f.name for f in files if "اصطناعي" in f.read_text(encoding="utf-8")] == []


def test_storyboard_matches_shots_meta_and_line_times() -> None:
    """storyboard.md tables = shots.yaml (text, durations) + meta.yaml (section titles), and every
    narrated shot lasts exactly as long as its covered English lines (FIX_CP8_NOTES item 2)."""
    shot_list = shots.load_shots(REPO_ROOT / "film/storyboard/shots.yaml")
    meta = yaml.safe_load((REPO_ROOT / "film/script/meta.yaml").read_text(encoding="utf-8"))
    md = (REPO_ROOT / "film/storyboard/storyboard.md").read_text(encoding="utf-8")
    assert shots.check_storyboard(md, shot_list, meta) == []
    rows = shots.load_line_rows(REPO_ROOT / "film/script/lines.csv")
    assert shots.check_durations(shot_list, rows) == []
    assert shots.check_inheritance(shot_list) + shots.check_quote_labels(shot_list) == []
    assert shots.check_quote_lines(shot_list, rows) == []


def test_on_screen_numbers_appear_in_covered_lines() -> None:
    shot_list = shots.load_shots(REPO_ROOT / "film/storyboard/shots.yaml")
    rows = shots.load_line_rows(REPO_ROOT / "film/script/lines.csv")
    missing = []
    for s in shot_list:
        for lang in ("en", "ar"):
            text = " ".join(
                rows[(s["cut"], lang, i)]["text"]
                for i in s["narration_line_ids"]
                if (s["cut"], lang, i) in rows
            )
            extra = set(s.get("extra_figures") or [])  # declared, traced by film.render trace
            for n in re.findall(r"\d+(?:[.,]\d+)*", s["on_screen_text"][lang]):
                if n not in text and n not in extra:
                    missing.append((s["id"], lang, n))
    assert missing == []


def test_fix_cp8_notes_wording() -> None:
    """The m-08-06 benefit meaning, the Vision 2030 Arabic paraphrase note and the 1951 line."""
    rows = shots.load_line_rows(REPO_ROOT / "film/script/lines.csv")
    en, ar = rows[("main", "en", "m-08-06")]["text"], rows[("main", "ar", "m-08-06")]["text"]
    assert "time saved" not in en and "time and cost savings" in en and "safety benefit" in en
    assert "قيمة الوقت اللي يرجع" not in ar and "وتكلفته" in ar and "السلامة" in ar
    for lang in ("en", "ar"):
        assert "first railway" not in rows[("main", lang, "m-02-02")]["text"]
        assert "أول خط" not in rows[("main", lang, "m-02-02")]["text"]
    by_id = {s["id"]: s for s in shots.load_shots(REPO_ROOT / "film/storyboard/shots.yaml")}
    for sid in ("sh-03-04", "sh-03-05"):
        assert by_id[sid]["quote_label"] == {"en": True, "ar": False}
        assert "بمعنى النص" in by_id[sid]["on_screen_text"]["ar"]
    assert "2026" in by_id["sh-08-06"]["source_caption"]["en"]
    pron = (REPO_ROOT / "film/script/pronunciation.md").read_text(encoding="utf-8")
    assert "ألف ومية وخمسين" not in pron
