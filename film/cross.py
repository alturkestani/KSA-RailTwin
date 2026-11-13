"""Cross-language subtitles for the main cuts (FILM_SUBS, Tariq 13 Nov 2026; media writes gated).

  uv run python -m film.cross build                  # film/subs/main-ar.en.srt, main-en.ar.srt
  uv run python -m film.cross check                  # tables, figures, names, cue limits, timing
  uv run python -m film.cross burn --pair main-ar.en # renders/out/social/subs/main-ar-subEN.mp4
  uv run python -m film.cross li-plan                # LinkedIn <= 14:50 feasibility + split point

The subtitle text of every narration line lives in film/subs/cross/<cut>-<audio>.<sub>.csv
(line_id, source_text, subtitle_text, spelled_figures, native_review); the SRTs are generated from
it, never retyped. source_text must equal the narration line (film/script/lines.csv `text`, the
display form of `speech_text`). Timing is not re-estimated: each line's cues sit inside that line's
measured narration interval in film/assemble/lines-<cut>-<audio>.csv and are cut with the same
packer as the same-language subtitles (film.subs.line_cues: at most 2 x 42 characters, 1-7 s).

Figure check: the numbers of each subtitle equal the numbers of the narration line it translates
(normalised as in film.script), except figures listed in spelled_figures as `<number>:<word>`, which
the source has as a digit and the subtitle as that word (e.g. `1:ساعة`). Names: every proper name in
NAMES appears in the subtitle exactly when it appears in the source. The Crown Prince is named with
the full honorific of the subtitle language. Arabic subtitles carry no tashkeel.

Burned-in copies follow film/social.py: Chrome-drawn cue PNGs overlaid in the top band (every main
shot carries its caption and credits at the bottom: storyboard on_screen_text), audio stream copied.
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import typer

from common import REPO_ROOT
from film import render as R
from film import social
from film.gate import require
from film.script import number_tokens
from film.subs import (
    Result,
    _ts,
    check_file,
    line_cues,
    parse_srt,
    render_cue,
    visible,
)

app = typer.Typer(add_completion=False, help="Cross-language subtitles (FILM_SUBS).")

CROSS = REPO_ROOT / "film/subs/cross"
SUBS = REPO_ROOT / "film/subs"
ASM = REPO_ROOT / "film/assemble"
LINES_CSV = REPO_ROOT / "film/script/lines.csv"
OUT = social.SOCIAL / "subs"
PAIRS = {"main-ar.en": ("main", "ar", "en"), "main-en.ar": ("main", "en", "ar")}
BURNED = {"main-ar.en": "main-ar-subEN", "main-en.ar": "main-en-subAR"}
FIELDS = ["line_id", "source_text", "subtitle_text", "spelled_figures", "native_review"]
TASHKEEL = re.compile("[\u064b-\u0652\u0670]")
HONORIFIC = {
    "en": "His Royal Highness Crown Prince Mohammed bin Salman",
    "ar": "صاحب السمو الملكي الأمير محمد بن سلمان، ولي العهد",
}
# (English pattern, Arabic pattern): proper names the film says; presence must match per line
NAMES: list[tuple[str, str]] = [
    (r"\bRiyadh\b", "الرياض"),
    (r"\bJeddah\b", "جدة"),
    (r"\bQurayyat\b", "القريات"),
    (r"\bAbha\b", "أبها"),
    (r"\bTabuk\b", "تبوك"),
    (r"\bAsir\b", "عسير"),
    (r"\bOAG\b", "أو إيه جي"),
    (r"Aqabat Shaar", "عقبة شعار"),
    (r"\bHejaz\b", "الحجاز"),
    (r"\bMadinah\b", "المدينة"),
    (r"\bAbdulaziz\b", "عبدالعزيز"),
    (r"\bDammam\b", "الدمام"),
    (r"\bQassim\b", "القصيم"),
    (r"\bHail\b", "حائل"),
    (r"\bAl-Jouf\b", "الجوف"),
    (r"\bHaramain\b|\bholy cities\b", "الحرمين"),
    (r"\bMakkah\b", "مكة"),
    (r"\bTaif\b", "الطائف"),
    (r"Khamis Mushait", "خميس مشيط"),
    (r"\bNajran\b", "نجران"),
    (r"\bJazan\b", "جازان"),
    (r"\bLandbridge\b", "الجسر البري"),
    (r"\bGCC\b|\bGulf\b", "الخليج"),
    (r"\bThe Line\b", "ذا لاين"),
    (r"\bReuters\b", "رويترز"),
    (r"Vision 2030", "رؤية 2030"),
    (r"\bJapan(?:ese)?\b", "اليابان|يابانية"),
    (r"\bQatar\b", "قطر"),
    (r"\bHofuf\b", "الهفوف"),
    (r"Ar Rusayfah", "الرصيفة"),
    (r"Al Jubayl", "الجبيل"),
    (r"\bDhahran\b", "الظهران"),
    (r"\bDuruma\b", "ضرما"),
    (r"Al-Kharj", "الخرج"),
    (r"Al-Jumum", "الجموم"),
    (r"\bSakaka\b", "سكاكا"),
    (r"\bBisha\b", "بيشة"),
    (r"North Line", "خط الشمال"),
    (r"East Line", "خط الشرق"),
    (r"General Authority for Statistics", "الهيئة العامة للإحصاء"),
    (r"[Cc]ivil [Aa]viation", "الطيران المدني"),
    (r"Royal Commission", "الهيئة الملكية"),
    (r"Mohammed bin Salman", "محمد بن سلمان"),
]


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def table(pair: str) -> list[dict]:
    return _read(CROSS / f"{pair}.csv")


def narration(cut: str, lang: str) -> dict[str, str]:
    rows = _read(LINES_CSV)
    return {r["line_id"]: r["text"] for r in rows if r["cut"] == cut and r["lang"] == lang}


def spelled(value: str) -> list[tuple[str, str]]:
    out = []
    for item in [x.strip() for x in value.split(";") if x.strip()]:
        num, _, word = item.partition(":")
        out.append((num.strip(), word.strip()))
    return out


def ar_forms(pattern: str) -> str:
    """Arabic name pattern plus its li- + al- contraction (الرياض -> للرياض)."""
    alts = pattern.split("|")
    return "|".join(alts + ["لل" + a[2:] for a in alts if a.startswith("ال")])


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text) is not None


def row_errors(row: dict, src_lang: str, sub_lang: str) -> list[str]:
    """Figures, names, honorific and script rules of one table row."""
    lid, src, sub = row["line_id"], row["source_text"], row["subtitle_text"]
    errs: list[str] = []
    want = Counter(number_tokens(src))
    for num, word in spelled(row["spelled_figures"]):
        if want[num] < 1:
            errs.append(f"{lid}: spelled figure {num} not in the source")
        elif word not in sub:
            errs.append(f"{lid}: spelled figure {num} has no {word!r} in the subtitle")
        want[num] -= 1
    got = Counter(number_tokens(sub))
    if +want != got:
        a, b = sorted(want.elements()), sorted(got.elements())
        errs.append(f"{lid}: figures differ (source {a}, subtitle {b})")
    for en, ar in NAMES:
        p_src, p_sub = (en, ar_forms(ar)) if src_lang == "en" else (ar_forms(ar), en)
        if _has(p_src, src) != _has(p_sub, sub):
            side = "source" if _has(p_src, src) else "subtitle"
            errs.append(f"{lid}: name {en!r}/{ar!r} in {side} only")
    if HONORIFIC[src_lang] in src and HONORIFIC[sub_lang] not in sub:
        errs.append(f"{lid}: honorific missing (want {HONORIFIC[sub_lang]!r})")
    if sub_lang == "ar":
        if TASHKEEL.search(sub):
            errs.append(f"{lid}: tashkeel in an Arabic subtitle")
        if re.search(r"[A-Za-z]", sub):
            errs.append(f"{lid}: Latin letters in an Arabic subtitle")
    if not sub.strip():
        errs.append(f"{lid}: empty subtitle")
    return errs


def table_errors(pair: str) -> list[str]:
    cut, audio, sub = PAIRS[pair]
    rows = table(pair)
    errs: list[str] = []
    if not rows or list(rows[0]) != FIELDS:
        return [f"{pair}.csv: columns must be {FIELDS}"]
    text = narration(cut, audio)
    timed = [r["line_id"] for r in _read(ASM / f"lines-{cut}-{audio}.csv")]
    if [r["line_id"] for r in rows] != timed:
        errs.append(f"{pair}.csv: line ids differ from lines-{cut}-{audio}.csv (order or set)")
    for r in rows:
        if " ".join(r["source_text"].split()) != " ".join(text.get(r["line_id"], "").split()):
            errs.append(f"{r['line_id']}: source_text differs from lines.csv ({audio})")
        if sub == "ar" and r["native_review"] != "pending":
            errs.append(f"{r['line_id']}: Arabic subtitle native_review must be 'pending'")
        errs += row_errors(r, audio, sub)
    return errs


def build_cues(pair: str) -> list[tuple]:
    cut, audio, _ = PAIRS[pair]
    subs = {r["line_id"]: r["subtitle_text"] for r in table(pair)}
    out = []
    for ln in _read(ASM / f"lines-{cut}-{audio}.csv"):
        for s, e, txt in line_cues(subs[ln["line_id"]], float(ln["start_s"]), float(ln["end_s"])):
            out.append((s, e, txt, ln["line_id"]))
    return out


def write(pair: str, cues: list[tuple]) -> tuple[Path, Path]:
    sub = PAIRS[pair][2]
    srt, vtt = SUBS / f"{pair}.srt", SUBS / f"{pair}.vtt"
    s_out, v_out = [], ["WEBVTT", ""]
    for i, (s, e, txt, _) in enumerate(cues, 1):
        body = "\n".join(render_cue(txt, sub))
        s_out.append(f"{i}\n{_ts(s, ',')} --> {_ts(e, ',')}\n{body}\n")
        v_out.append(f"{_ts(s, '.')} --> {_ts(e, '.')}\n{body}\n")
    srt.write_text("\n".join(s_out), encoding="utf-8")
    vtt.write_text("\n".join(v_out), encoding="utf-8")
    return srt, vtt


def align_errors(pair: str, srt: Path | None = None) -> list[str]:
    """Every cue inside exactly one narration interval; cues of a line join back to its row."""
    cut, audio, _ = PAIRS[pair]
    res = Result()
    cues = parse_srt((srt or SUBS / f"{pair}.srt").read_text(encoding="utf-8"), res)
    errs = list(res.errors)
    spans = _read(ASM / f"lines-{cut}-{audio}.csv")
    by: dict[str, list[str]] = {}
    for c in cues:
        hits = [
            sp["line_id"]
            for sp in spans
            if float(sp["start_s"]) - 0.002 <= c.start and c.end <= float(sp["end_s"]) + 0.002
        ]
        if len(hits) != 1:
            errs.append(f"cue {c.label}: not inside exactly one narration interval")
            continue
        by.setdefault(hits[0], []).append(" ".join(visible(x) for x in c.lines))
    for r in table(pair):
        got = " ".join(" ".join(by.get(r["line_id"], [])).split())
        if got != " ".join(r["subtitle_text"].split()):
            errs.append(f"{r['line_id']}: cues do not join back to the table row")
    return errs


def stats(srt: Path) -> dict:
    res = Result()
    cues = parse_srt(srt.read_text(encoding="utf-8"), res)
    durs = [c.end - c.start for c in cues]
    chars = [len(visible(x)) for c in cues for x in c.lines]
    return {
        "cues": len(cues),
        "longest_s": round(max(durs), 3),
        "shortest_s": round(min(durs), 3),
        "max_chars_per_line": max(chars),
        "max_lines": max(len(c.lines) for c in cues),
        "first_s": cues[0].start,
        "last_s": cues[-1].end,
    }


@app.callback()
def _main() -> None:
    """Cross-language subtitles (FILM_SUBS)."""


@app.command()
def build() -> None:
    """Write film/subs/<pair>.srt and .vtt from the tables and the measured line times."""
    require(5_000_000, quiet=True)
    for pair in PAIRS:
        errs = table_errors(pair)
        if errs:
            for e in errs:
                typer.echo(f"FAIL {pair}: {e}")
            raise typer.Exit(1)
        cues = build_cues(pair)
        srt, vtt = write(pair, cues)
        typer.echo(f"film.cross build {pair}: {len(cues)} cues -> {srt.name}, {vtt.name}")


@app.command()
def check() -> None:
    """Tables (figures, names, honorific), SRT/VTT validity and limits, alignment."""
    n = 0
    for pair in PAIRS:
        errs = table_errors(pair)
        for f in (SUBS / f"{pair}.srt", SUBS / f"{pair}.vtt"):
            res = check_file(f)
            errs += [f"{f.name}: {e}" for e in res.errors]
            for w in res.warnings:
                typer.echo(f"WARN {pair} {f.name}: {w}")
        errs += align_errors(pair)
        for e in errs:
            typer.echo(f"FAIL {pair}: {e}")
        n += len(errs)
        typer.echo(f"{pair}: {stats(SUBS / f'{pair}.srt')}")
    if n:
        raise typer.Exit(1)
    typer.echo("film.cross check PASS")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def audio_md5(path: Path) -> str:
    """MD5 of the demuxed audio packets (stream copy): equal means the audio is untouched."""
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-map", "0:a"]
        + ["-c", "copy", "-f", "md5", "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return out.strip()


@app.command()
def burn(
    pair: str = typer.Option(..., "--pair"),
    workers: int = typer.Option(4, "--workers"),
) -> None:
    """Burn the cross-language subtitles into the cut's picture (top band); audio copied."""
    cut, audio, sub = PAIRS[pair]
    src = social.cut_mp4(cut, audio)
    total = float(social.probe(src)["format"]["duration"])
    require(int(total * 4e6) + 200_000_000)
    res = Result()
    cues = parse_srt((SUBS / f"{pair}.srt").read_text(encoding="utf-8"), res)
    if res.errors:
        raise SystemExit(f"{pair}.srt: {res.errors[:3]}")
    work = R.RENDERS / "_social" / f"cross-{pair}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)
    blank = work / "blank.png"
    R.chrome_png(R.page("", transparent=True, lang=sub), blank, transparent=True)
    pngs = [work / f"cue{i:04d}.png" for i in range(1, len(cues) + 1)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(
            ex.map(
                lambda cp: R.chrome_png(social.cue_html(cp[0].lines, sub), cp[1], transparent=True),
                zip(cues, pngs, strict=True),
            )
        )
    lst = work / "subs.ffconcat"
    lst.write_text(social.concat_list(cues, pngs, blank, total), encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    mp4 = OUT / f"{BURNED[pair]}.mp4"
    tmp = mp4.with_suffix(".new.mp4")
    flt = (
        f"[1:v]fps={R.FPS},format=rgba[s];"
        "[0:v][s]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src)]
    cmd += ["-f", "concat", "-safe", "0", "-i", str(lst), "-filter_complex", flt]
    cmd += ["-map", "[v]", "-map", "0:a", "-r", str(R.FPS), "-c:v", "libx264", "-preset"]
    cmd += ["medium", "-crf", str(social.CRF), "-pix_fmt", "yuv420p", "-c:a", "copy", "-sn"]
    cmd += ["-map_metadata", "0", "-movflags", "+faststart", "-t", f"{total:.3f}", str(tmp)]
    subprocess.run(cmd, check=True)
    tmp.replace(mp4)
    shutil.copyfile(SUBS / f"{pair}.srt", OUT / f"{pair}.srt")
    same = audio_md5(src) == audio_md5(mp4)
    typer.echo(f"film.cross burn {pair}: {mp4} ({len(cues)} cues; audio packets identical: {same})")
    if not same:
        raise typer.Exit(1)


LI_TARGET_S = 14 * 60 + 50  # Tariq, FILM_SUBS item 3
LI_PLAN = ASM / "li-floor.csv"


def li_floor(cut: str = "main", lang: str = "ar") -> dict:
    """Shortest no-speech-loss lengths of a cut from its edit list and the line WAV durations.

    floor_speech_only: every head, gap, tail and silent shot removed (the line WAVs back to back);
    floor_low_range: head/gap/tail at the low ends of A-film-009/008/010, silent shots at their
    edit-list length. Both keep every narration WAV byte-identical."""
    edl = _read(ASM / f"edl-{cut}-{lang}.csv")
    lines = {r["line_id"]: r for r in _read(ASM / f"lines-{cut}-{lang}.csv")}
    head_lo, gap_lo, tail_lo = 0.3, 0.2, 0.4  # film_voice.yaml ranges of A-film-009/008/010
    rows, speech, low = [], 0.0, 0.0
    for r in edl:
        ids = r["line_ids"].split()
        sp = sum(float(lines[i]["end_s"]) - float(lines[i]["start_s"]) for i in ids)
        new = head_lo + sp + gap_lo * (len(ids) - 1) + tail_lo if ids else float(r["duration_s"])
        new = round(round(new * 30) / 30, 4)
        speech += sp
        low += new
        rows.append(
            {
                "shot_id": r["shot_id"],
                "section": r["section"],
                "old_duration_s": r["duration_s"],
                "speech_s": f"{sp:.3f}",
                "low_range_duration_s": f"{new:.4f}",
            }
        )
    starts: dict[str, float] = {}
    for r in edl:
        starts.setdefault(r["section"], float(r["start_s"]))
    total = float(edl[-1]["start_s"]) + float(edl[-1]["duration_s"])
    splits = [
        {"before_section": s, "part1_s": round(t, 3), "part2_s": round(total - t, 3)}
        for s, t in starts.items()
        if t > 0
    ]
    best = min(splits, key=lambda x: max(x["part1_s"], x["part2_s"]))
    return {
        "rows": rows,
        "current_s": round(total, 3),
        "floor_speech_only_s": round(speech, 3),
        "floor_low_range_s": round(low, 3),
        "target_s": LI_TARGET_S,
        "splits": splits,
        "best_split": best,
    }


@app.command("li-plan")
def li_plan() -> None:
    """Item 3 feasibility: is main-ar <= 14:50 reachable without cutting speech?"""
    p = li_floor()
    with LI_PLAN.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(p["rows"][0]), lineterminator="\n")
        w.writeheader()
        w.writerows(p["rows"])
    mm = lambda s: f"{int(s // 60)}:{s % 60:06.3f}"  # noqa: E731
    typer.echo(f"current {mm(p['current_s'])}; target {mm(p['target_s'])}")
    typer.echo(f"floor, speech only: {mm(p['floor_speech_only_s'])}")
    typer.echo(f"floor, low-range holds: {mm(p['floor_low_range_s'])}")
    for s in p["splits"]:
        a, b = mm(s["part1_s"]), mm(s["part2_s"])
        typer.echo(f"split before section {s['before_section']}: {a} + {b}")
    b = p["best_split"]
    typer.echo(f"best: before section {b['before_section']}")
    feasible = p["floor_speech_only_s"] <= p["target_s"]
    typer.echo(f"feasible without cutting speech: {feasible}")


if __name__ == "__main__":
    app()
