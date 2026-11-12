"""FIX_MBS_TITLE (Tariq, 11 Nov 2026): the Crown Prince is named with his full honorific in
m-03-03 and sh-03-02; no bare «ولي العهد» or "the Crown Prince" without the name anywhere in the
main script, captions or subtitles. Fast checks on committed files only."""

from __future__ import annotations

import csv
import re

import yaml

from common import REPO_ROOT
from film import script

EN_NAME = "His Royal Highness Crown Prince Mohammed bin Salman"
AR_NAME = "صاحب السمو الملكي الأمير محمد بن سلمان، ولي العهد،"
EN_LINE = (
    "After The Line launch in July 2022, His Royal Highness Crown Prince Mohammed bin Salman told "
    "journalists the aim is 50 to 60 million people in the Kingdom by 2030, about half Saudis. "
    "Remarks, not a published programme target."
)
AR_LINE = (
    "وبعد إطلاق تصاميم ذا لاين في يوليو 2022، قال صاحب السمو الملكي الأمير محمد بن سلمان، ولي "
    "العهد، للصحفيين إن الهدف إن عدد سكان المملكة يوصل بين 50 و60 مليون بحلول 2030، ونصهم "
    "تقريباً سعوديين. وهذي تصريحات، مو هدف منشور في برنامج رسمي."
)
AR_SPOKEN = "صَاحِبُ السُّمُوِّ الْمَلَكِيِّ الْأَمِيرُ مُحَمَّدُ بْنُ سَلْمَانَ، وَلِيُّ الْعَهْدِ،"
MAIN_FILES = [
    "film/subs/main.en.srt",
    "film/subs/main.en.vtt",
    "film/subs/main.ar.srt",
    "film/subs/main.ar.vtt",
    "film/script/main.en.md",
    "film/script/main.ar.md",
]


def _rows(path: str) -> list[dict[str, str]]:
    with (REPO_ROOT / path).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _bare(text: str) -> list[str]:
    """Mentions of the title that are not part of the full honorific."""
    flat = " ".join(script.strip_tashkeel(text).replace("‏", "").split())
    out = []
    for m in re.finditer(r"Crown Prince", flat):
        start = m.start() - len("His Royal Highness ")
        if flat[max(0, start) : start + len(EN_NAME)] != EN_NAME:
            out.append(flat[max(0, m.start() - 30) : m.end() + 30])
    for m in re.finditer("ولي العهد", flat):
        if "الأمير محمد بن سلمان، ولي العهد" not in flat[max(0, m.start() - 40) : m.end()]:
            out.append(flat[max(0, m.start() - 30) : m.end() + 30])
    return out


def test_m_03_03_full_honorific() -> None:
    rows = {(r["cut"], r["lang"], r["line_id"]): r for r in _rows("film/script/lines.csv")}
    en, ar = rows["main", "en", "m-03-03"], rows["main", "ar", "m-03-03"]
    assert en["text"] == EN_LINE and ar["text"] == AR_LINE
    assert AR_SPOKEN in ar["speech_text"]
    assert script.strip_tashkeel(ar["speech_text"]) == script.strip_tashkeel(ar["text"])
    assert ar["native_review"] == "pending"
    for r in (en, ar):  # figures, sources and the qualifier unchanged
        assert [x.strip() for x in r["figure_values"].split(";")] == ["2022", "50", "60", "2030"]
        assert r["sources"].startswith("S-r10-057; S-r10-058; S-r10-025")


def test_no_bare_title_in_main_outputs() -> None:
    for r in _rows("film/script/lines.csv"):
        if r["cut"] == "main":
            assert not _bare(r["text"] + " " + r["speech_text"]), r["line_id"]
    shots = yaml.safe_load((REPO_ROOT / "film/storyboard/shots.yaml").read_text(encoding="utf-8"))
    for s in shots if isinstance(shots, list) else shots["shots"]:
        if s["cut"] == "main":
            assert not _bare(" ".join((s.get("on_screen_text") or {}).values())), s["id"]
            if s["id"] == "sh-03-02":
                assert EN_NAME in s["on_screen_text"]["en"]
                assert AR_NAME in s["on_screen_text"]["ar"]
    for f in MAIN_FILES:
        assert not _bare((REPO_ROOT / f).read_text(encoding="utf-8")), f


def test_edit_logs() -> None:
    for path, key in (
        ("film/storyboard/story-edits.csv", "line_id"),
        ("film/storyboard/caption-edits.csv", "shot_id"),
    ):
        rows = [r for r in _rows(path) if r[key] in ("m-03-03", "sh-03-02")]
        new = {r["lang"]: r.get("after", r.get("new")) for r in rows[-2:]}
        assert EN_NAME in new["en"] and AR_NAME in new["ar"], path
    rw = [r for r in _rows("film/storyboard/ar-rewords.csv") if r["line_id"] == "m-03-03"][-1]
    assert rw["reason"].startswith("FIX_MBS_TITLE") and rw["new"] == AR_LINE
    assert re.findall(r"\d", rw["old"]) == re.findall(r"\d", rw["new"])


def test_duration_allowance_is_narrow(tmp_path) -> None:
    """The recorded 2.0 s main/en allowance warns; anything beyond it is still an error."""
    import shutil

    sdir = tmp_path / "script"
    shutil.copytree(REPO_ROOT / "film/script", sdir)
    rep, _ = script.validate_dir(sdir, script.DEFAULT_TIMING, REPO_ROOT)
    assert not any("total" in e for e in rep.errors)
    assert any("recorded allowance" in w and "FIX_MBS_TITLE" in w for w in rep.warnings)
    rows = script.read_lines(sdir)
    r = next(x for x in rows if (x["cut"], x["lang"], x["line_id"]) == ("main", "en", "m-03-03"))
    r["est_seconds"] = f"{float(r['est_seconds']) + 0.5:.1f}"
    script.write_lines(sdir, rows)
    rep, _ = script.validate_dir(sdir, script.DEFAULT_TIMING, REPO_ROOT)
    assert any(e.startswith("main/en: total") for e in rep.errors)
