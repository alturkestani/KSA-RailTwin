"""FIX_TRAILER_AR item 4 (Tariq, 12 Nov 2026): no finance jargon in any public film output,
inflected forms included (Arabic «صافي قيمته», «القيمة الحالية», «موجب/سالب»; English "NPV",
"net present value", "present value").

Public outputs checked: the four script Markdown files, the script text and spoken forms
(lines.csv text and speech_text, film/voice/say.csv), the subtitle files, every shot's on-screen
text and source caption, the credits and closing notice, and the local ASR transcripts of the four
final cuts' audio (film/voice/readback/final-*.txt, scripts/film_final_asr.py). With the external
volume present, also the social subtitle files, the script PDFs and the transcripts' freshness
(their SHA-256 matches the final MP4). The only allow-listed text is the single closing notice.
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from common import REPO_ROOT
from film import render, sim
from film.shots import load_shots
from tests.localdata import needs_local

TASHKEEL = re.compile("[ً-ْٰـ]")
MARKS = re.compile("[‎‏‪-‮⁦-⁩]")
AR_LETTER = "ء-ي"
BARRED_AR = (
    re.compile(r"صافي\s*(?:ال)?قيم"),  # صافي القيمة / صافي قيمته / صافي قيمتها
    re.compile(r"قيم(?:ه|ته|تها|تهم)?\s*(?:ال)?حالي"),  # القيمة الحالية / بقيمتها الحالية
    # موجب / سالب in any inflection (موجبة، سالبة، والسالب، بالموجب); «بموجب» (= "under") is not
    # finance and stays allowed.
    re.compile(rf"(?<![{AR_LETTER}])(?:[وفل]|بال|وال|فال|لل)?(?:ال)?(?:موجب|سالب)"),
)
BARRED_EN = (
    re.compile(r"\bNPVs?\b", re.IGNORECASE),
    re.compile(r"net\s+present\s+values?", re.IGNORECASE),
    re.compile(r"present\s+values?", re.IGNORECASE),
)
# The single closing notice is the only allow-listed text (it carries no barred term today; the
# allow-list keeps any future wording of it from tripping the check).
ALLOW = tuple(sim.CLOSING_NOTICE.values())
FINAL = ("main-en", "main-ar", "trailer-en", "trailer-ar")
OUT = "film/renders/out"


def norm(text: str) -> str:
    text = MARKS.sub("", TASHKEEL.sub("", text))
    text = re.sub("[إأآ]", "ا", text).replace("ة", "ه")
    for a in ALLOW:
        text = text.replace(a, " ").replace(TASHKEEL.sub("", a).replace("ة", "ه"), " ")
    return text


def hits(text: str) -> list[str]:
    t = norm(text)
    return [m.group(0) for p in BARRED_AR + BARRED_EN for m in p.finditer(t)]


def test_patterns_catch_inflected_forms() -> None:
    for bad in (
        "يبقى صافي قيمته الحالية موجب",
        "صَافِي قِيمَتَه الْحَالِيَّة",
        "صافي القيمة الحالية",
        "بقيمتها الحالية",
        "النتيجة سالبة",
        "والسالب",
        "the NPV stays",
        "net present value",
        "in present value",
    ):
        assert hits(bad), bad
    for ok in ("بموجب الترخيص", "صافي التكلفة على الدولة", "المنافع تزيد على التكاليف"):
        assert not hits(ok), ok
    assert len(ALLOW) == 2 and set(ALLOW) == set(sim.CLOSING_NOTICE.values())


def _public_texts() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted((REPO_ROOT / "film/script").glob("*.md")):
        if p.name != "pronunciation.md":  # internal TTS guide, not shown or spoken
            out[str(p.relative_to(REPO_ROOT))] = p.read_text("utf-8")
    with (REPO_ROOT / "film/script/lines.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            key = f"lines.csv {r['cut']}/{r['lang']}/{r['line_id']}"
            out[key] = r["text"] + "\n" + r["speech_text"]
    with (REPO_ROOT / "film/voice/say.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            out[f"say.csv {r['cut']}/{r['lang']}/{r['line_id']}"] = r["say"]
    for p in sorted((REPO_ROOT / "film/subs").glob("*.[sv][rt][tt]")):
        out[str(p.relative_to(REPO_ROOT))] = p.read_text("utf-8")
    for s in load_shots(REPO_ROOT / "film/storyboard/shots.yaml"):
        for k in ("on_screen_text", "source_caption"):
            for lang, v in (s.get(k) or {}).items():
                out[f"shots.yaml {s['id']} {k} {lang}"] = str(v)
    for lang in ("en", "ar"):
        out[f"credits {lang}"] = "\n".join(render.credits_lines(lang))
        out[f"closing credits {lang}"] = "\n".join(sim.closing_credits(lang))
    for c in FINAL:
        p = REPO_ROOT / f"film/voice/readback/final-{c}.txt"
        out[str(p.relative_to(REPO_ROOT))] = p.read_text("utf-8")
    return out


def test_no_barred_jargon_in_public_text_and_transcripts() -> None:
    texts = _public_texts()
    assert len([k for k in texts if "final-" in k]) == 4
    bad = {k: h for k, t in texts.items() if (h := hits(t))}
    assert bad == {}


def test_trailer_ar_t08_plain_wording() -> None:
    with (REPO_ROOT / "film/script/lines.csv").open(encoding="utf-8", newline="") as fh:
        rows = {(r["cut"], r["lang"], r["line_id"]): r for r in csv.DictReader(fh)}
    ar, en = rows["trailer", "ar", "t-08"], rows["trailer", "en", "t-08"]
    assert "يرجّع تكلفته حتى لو ارتفعت" in ar["text"]
    assert "المنافع تزيد على التكاليف بين 4.0 و5.6 مليار ريال" in ar["text"]
    assert ar["figure_values"] == en["figure_values"] == "4.0; 5.6"
    assert ar["sources"] == en["sources"] == "run:runs/r6/top5/top5.csv"
    assert ar["native_review"] == "pending" and ar["speech_text"]
    words = [w for w in ar["speech_text"].split() if re.search("[ء-ي]", w)]
    bare = [w for w in words if not TASHKEEL.search(w)]
    assert bare == ["مليار"]  # full tashkeel; «مليار» bare as in every other figure line


def test_trailer_ar_credits_drop_elevenlabs_keep_nabrah() -> None:
    ar = " ".join(sim.closing_credits("ar"))
    assert "ElevenLabs" not in ar and "George" not in ar
    assert "نبرة" in ar and "دانية" in ar and "نورة" in ar and "عبدالله" in ar
    en = " ".join(sim.closing_credits("en"))
    assert "ElevenLabs voice George" in en  # the English trailer is unchanged


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


@needs_local(*(f"{OUT}/ksa-rail-twin-{c}.mp4" for c in FINAL))
def test_transcripts_match_final_cuts() -> None:
    for c in FINAL:
        head = (REPO_ROOT / f"film/voice/readback/final-{c}.txt").read_text("utf-8")
        sha = re.search(r"^# sha256: ([0-9a-f]{64})$", head, re.M)
        assert sha, c
        assert sha.group(1) == _sha(REPO_ROOT / f"{OUT}/ksa-rail-twin-{c}.mp4"), c


@needs_local(f"{OUT}/social", f"{OUT}/script")
def test_no_barred_jargon_in_social_srt_and_script_pdfs() -> None:
    bad = {}
    for p in sorted((REPO_ROOT / f"{OUT}/social").glob("*.srt")):
        if not p.name.startswith("._") and (h := hits(p.read_text("utf-8"))):
            bad[p.name] = h
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext not installed")
    for p in sorted((REPO_ROOT / f"{OUT}/script").glob("*.pdf")):
        if p.name.startswith("._"):
            continue
        txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
        # pdftotext splits Arabic words into glyph runs: check with the spaces removed too.
        if h := hits(txt) + hits(re.sub(r"\s+", "", norm(txt))):
            bad[p.name] = h
    assert bad == {}
