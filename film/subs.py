"""Subtitle checks for SRT and VTT (film/subs/).

CLI:
  uv run python -m film.subs check <dir-or-file> [--fps 30]
  uv run python -m film.subs build --cut main --lang ar     (R10 half 2; gated)
  uv run python -m film.subs align-qa --cut main --lang ar  (cue text and timing vs the narration)

`build` writes film/subs/<cut>.<lang>.srt and .vtt from film/script/lines.csv (the text is never
retyped) and the measured line times in film/assemble/lines-<cut>-<lang>.csv: each line is cut at
clause punctuation into cues of at most 2 x 42 characters and 7 s, timed in proportion to their
reading characters inside the line's narration interval, with a 2-frame gap. Arabic lines start
with U+200F (RLM) so players set right-to-left paragraph direction.
`align-qa` checks that the cues of every line join back to the script text exactly, lie inside
that line's narration interval, and (if film/voice/readback/<cut>-<lang>.csv exists) that the
Whisper read-back CER of the line is at most 0.30 (warning above 0.10; A-film-012).

Rules per file: UTF-8 without BOM; SRT cue numbers consecutive from 1; VTT starts with WEBVTT.
Per cue: duration 1.0-7.0 s; at most 2 lines; at most 42 characters per line (bidi marks
U+200E/U+200F/U+202A-U+202E/U+2066-U+2069 and tags not counted); reading speed <= 20 cps
(error) and >= 12 cps (else a warning), counting characters without whitespace, bidi marks or
Arabic diacritics (U+064B-U+0652). Between cues: no overlap and a gap of at least 2 frames.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

import typer

from common import REPO_ROOT
from film.gate import require

MIN_DUR, MAX_DUR = 1.0, 7.0
MAX_LINES, MAX_CHARS = 2, 42
MAX_CPS, MIN_CPS = 20.0, 12.0
GAP_FRAMES = 2
BIDI = re.compile("[‎‏‪-‮⁦-⁩]")
DIACRITICS = re.compile("[ً-ْ]")
TAG = re.compile(r"<[^>]*>")
SRT_TIME = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*$"
)
VTT_TS = r"(?:(\d{2,}):)?(\d{2}):(\d{2})\.(\d{3})"
VTT_TIME = re.compile(rf"^{VTT_TS}\s+-->\s+{VTT_TS}(?:\s+.*)?$")

app = typer.Typer(add_completion=False, help="Subtitle (SRT/VTT) checks.")


@dataclass
class Cue:
    label: str
    start: float
    end: float
    lines: list[str]


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    cues: int = 0


def _secs(h: str | None, m: str, s: str, ms: str) -> float:
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def visible(line: str) -> str:
    return BIDI.sub("", TAG.sub("", line))


def reading_chars(lines: list[str]) -> int:
    return sum(len(DIACRITICS.sub("", "".join(visible(ln).split()))) for ln in lines)


def _blocks(text: str) -> list[list[str]]:
    blocks, cur = [], []
    for ln in text.split("\n"):
        ln = ln.rstrip("\r")
        if ln.strip():
            cur.append(ln)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def parse_srt(text: str, res: Result) -> list[Cue]:
    cues: list[Cue] = []
    for i, b in enumerate(_blocks(text), start=1):
        if not b[0].strip().isdigit():
            res.errors.append(f"block {i}: missing cue number")
            continue
        if int(b[0]) != i:
            res.errors.append(f"cue {b[0]}: numbering not consecutive (expected {i})")
        m = SRT_TIME.match(b[1]) if len(b) > 1 else None
        if not m:
            res.errors.append(f"cue {b[0]}: bad timing line")
            continue
        g = m.groups()
        cues.append(Cue(b[0], _secs(*g[0:4]), _secs(*g[4:8]), b[2:]))
    return cues


def parse_vtt(text: str, res: Result) -> list[Cue]:
    if not text.startswith("WEBVTT"):
        res.errors.append("VTT file must start with WEBVTT")
    cues: list[Cue] = []
    for i, b in enumerate(_blocks(text), start=1):
        if b[0].startswith(("WEBVTT", "NOTE", "STYLE", "REGION")):
            continue
        t = 0 if "-->" in b[0] else 1
        if t >= len(b):
            res.errors.append(f"block {i}: no timing line")
            continue
        m = VTT_TIME.match(b[t])
        if not m:
            res.errors.append(f"block {i}: bad timing line")
            continue
        g = m.groups()
        label = b[0] if t else str(len(cues) + 1)
        cues.append(Cue(label, _secs(*g[0:4]), _secs(*g[4:8]), b[t + 1 :]))
    return cues


def check_cues(cues: list[Cue], fps: float, res: Result) -> None:
    gap = GAP_FRAMES / fps
    prev: Cue | None = None
    for c in cues:
        where = f"cue {c.label}"
        dur = c.end - c.start
        if not MIN_DUR - 1e-9 <= dur <= MAX_DUR + 1e-9:
            res.errors.append(f"{where}: duration {dur:.3f} s outside {MIN_DUR}-{MAX_DUR} s")
        if not c.lines:
            res.errors.append(f"{where}: no text")
        if len(c.lines) > MAX_LINES:
            res.errors.append(f"{where}: {len(c.lines)} lines (max {MAX_LINES})")
        for ln in c.lines:
            n = len(visible(ln))
            if n > MAX_CHARS:
                res.errors.append(f"{where}: line of {n} chars (max {MAX_CHARS})")
        if dur > 0:
            cps = reading_chars(c.lines) / dur
            if cps > MAX_CPS:
                res.errors.append(f"{where}: reading speed {cps:.1f} cps > {MAX_CPS:.0f}")
            elif cps < MIN_CPS:
                res.warnings.append(f"{where}: reading speed {cps:.1f} cps < {MIN_CPS:.0f}")
        if prev is not None:
            if c.start < prev.end:
                res.errors.append(f"{where}: overlaps cue {prev.label}")
            elif c.start - prev.end < gap - 1e-9:
                res.errors.append(
                    f"{where}: gap {c.start - prev.end:.3f} s after cue {prev.label} "
                    f"< {GAP_FRAMES} frames"
                )
        prev = c


def check_file(path: Path, fps: float = 30.0) -> Result:
    res = Result()
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        res.errors.append("UTF-8 BOM present")
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        res.errors.append("not valid UTF-8")
        return res
    cues = parse_srt(text, res) if path.suffix.lower() == ".srt" else parse_vtt(text, res)
    res.cues = len(cues)
    check_cues(cues, fps, res)
    return res


def subtitle_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*") if p.suffix.lower() in (".srt", ".vtt"))


SUBS_DIR = REPO_ROOT / "film/subs"
ASM_DIR = REPO_ROOT / "film/assemble"
LINES_CSV = REPO_ROOT / "film/script/lines.csv"
RLM = "\u200f"
CLAUSE = re.compile(r"(?<=[.!?؟:;،,])\s+")
CER_WARN, CER_FAIL = 0.10, 0.30  # A-film-012 (film/assumptions-r10.md)


def wrap(text: str, width: int = MAX_CHARS) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def chunks(text: str) -> list[str]:
    """Clause-first packing into chunks that wrap to at most two lines."""
    out: list[str] = []
    cur = ""
    for clause in CLAUSE.split(" ".join(text.split())):
        cand = f"{cur} {clause}".strip()
        if len(wrap(cand)) <= MAX_LINES:
            cur = cand
            continue
        if cur:
            out.append(cur)
        cur = ""
        for w in clause.split():
            cand = f"{cur} {w}".strip()
            if len(wrap(cand)) <= MAX_LINES:
                cur = cand
            else:
                out.append(cur)
                cur = w
    if cur:
        out.append(cur)
    return out


def _rc(text: str) -> int:
    return max(reading_chars([text]), 1)


def _balanced(text: str) -> list[str] | None:
    """Split text into two chunks of near-equal reading length, each at most two lines."""
    words = text.split()
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        if len(wrap(a)) <= MAX_LINES and len(wrap(b)) <= MAX_LINES:
            score = abs(_rc(a) - _rc(b))
            if best is None or score < best[0]:
                best = (score, [a, b])
    return best[1] if best else None


def line_cues(text: str, start: float, end: float, fps: float = 30.0) -> list[tuple]:
    parts = chunks(text)
    # split chunks whose share of time would exceed MAX_DUR
    while True:
        total = sum(_rc(p) for p in parts)
        long = [i for i, p in enumerate(parts) if (end - start) * _rc(p) / total > MAX_DUR]
        if not long:
            break
        i = long[0]
        words = parts[i].split()
        if len(words) < 2:
            break
        h = len(words) // 2
        parts[i : i + 1] = [" ".join(words[:h]), " ".join(words[h:])]
    # merge chunks shorter than MIN_DUR into a neighbour when the result still fits
    total = sum(_rc(p) for p in parts)
    i = 0
    while i < len(parts) and len(parts) > 1:
        if (end - start) * _rc(parts[i]) / total < MIN_DUR + GAP_FRAMES / fps:
            j = i - 1 if i > 0 else i + 1
            a, b = sorted((i, j))
            merged = f"{parts[a]} {parts[b]}"
            if len(wrap(merged)) <= MAX_LINES:
                parts[a : b + 1] = [merged]
                i = 0
                continue
            halves = _balanced(merged)
            if halves and halves != [parts[a], parts[b]]:
                parts[a : b + 1] = halves
                i = 0
                continue
        i += 1
    total = sum(_rc(p) for p in parts)
    cues, t = [], start
    gap = GAP_FRAMES / fps + 0.001
    for k, p in enumerate(parts):
        d = (end - start) * _rc(p) / total
        e = t + d - (gap if k < len(parts) - 1 else 0)
        cues.append((round(t, 3), round(e, 3), p))
        t += d
    return cues


def _ts(s: float, sep: str) -> str:
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d}{sep}{ms:03d}"


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def build_cues(cut: str, lang: str) -> list[tuple]:
    texts = {
        r["line_id"]: r["text"]
        for r in _read_csv(LINES_CSV)
        if r["cut"] == cut and r["lang"] == lang
    }
    out = []
    for ln in _read_csv(ASM_DIR / f"lines-{cut}-{lang}.csv"):
        for s, e, txt in line_cues(texts[ln["line_id"]], float(ln["start_s"]), float(ln["end_s"])):
            out.append((s, e, txt, ln["line_id"]))
    return out


def render_cue(text: str, lang: str) -> list[str]:
    rows = wrap(text)
    return [RLM + r for r in rows] if lang == "ar" else rows


def write_subs(cut: str, lang: str, cues: list[tuple]) -> tuple[Path, Path]:
    SUBS_DIR.mkdir(parents=True, exist_ok=True)
    srt, vtt = SUBS_DIR / f"{cut}.{lang}.srt", SUBS_DIR / f"{cut}.{lang}.vtt"
    s_out, v_out = [], ["WEBVTT", ""]
    for i, (s, e, txt, _) in enumerate(cues, 1):
        body = "\n".join(render_cue(txt, lang))
        s_out.append(f"{i}\n{_ts(s, ',')} --> {_ts(e, ',')}\n{body}\n")
        v_out.append(f"{_ts(s, '.')} --> {_ts(e, '.')}\n{body}\n")
    srt.write_text("\n".join(s_out), encoding="utf-8")
    vtt.write_text("\n".join(v_out), encoding="utf-8")
    return srt, vtt


def align_errors(cut: str, lang: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    texts = {
        r["line_id"]: " ".join(r["text"].split())
        for r in _read_csv(LINES_CSV)
        if r["cut"] == cut and r["lang"] == lang
    }
    spans = {r["line_id"]: r for r in _read_csv(ASM_DIR / f"lines-{cut}-{lang}.csv")}
    res = Result()
    cues = parse_srt((SUBS_DIR / f"{cut}.{lang}.srt").read_text(encoding="utf-8"), res)
    errors += res.errors
    by_line: dict[str, list[Cue]] = {}
    for c in cues:
        hits = [
            lid
            for lid, sp in spans.items()
            if float(sp["start_s"]) - 0.002 <= c.start and c.end <= float(sp["end_s"]) + 0.002
        ]
        if len(hits) != 1:
            errors.append(f"cue {c.label}: not inside exactly one narrated line interval")
            continue
        by_line.setdefault(hits[0], []).append(c)
    for lid, want in texts.items():
        got = " ".join(visible(" ".join(c.lines)) for c in by_line.get(lid, []))
        if " ".join(got.split()) != want:
            errors.append(f"{lid}: cue text does not join back to lines.csv")
    rb = REPO_ROOT / f"film/voice/readback/{cut}-{lang}.csv"
    if rb.exists():
        for r in _read_csv(rb):
            cer = float(r["cer"])
            if cer > CER_FAIL:
                errors.append(f"{r['line_id']}: read-back CER {cer:.3f} > {CER_FAIL}")
            elif cer > CER_WARN:
                warnings.append(f"{r['line_id']}: read-back CER {cer:.3f} > {CER_WARN}")
    else:
        warnings.append(f"no read-back table {rb.name}")
    return errors, warnings


@app.callback()
def _main() -> None:
    """Subtitle checks."""


@app.command()
def check(target: Path, fps: float = typer.Option(30.0, "--fps")) -> None:
    """Check every SRT/VTT file under TARGET; exit 1 on any error."""
    files = subtitle_files(target)
    if not files:
        typer.echo(f"FAIL no .srt or .vtt files under {target}")
        raise typer.Exit(1)
    n_err = n_warn = n_cues = 0
    for f in files:
        res = check_file(f, fps)
        n_cues += res.cues
        for w in res.warnings:
            typer.echo(f"WARN {f}: {w}")
        for e in res.errors:
            typer.echo(f"FAIL {f}: {e}")
        n_err += len(res.errors)
        n_warn += len(res.warnings)
    if n_err:
        typer.echo(f"film.subs check FAIL: {n_err} error(s) in {len(files)} file(s)")
        raise typer.Exit(1)
    typer.echo(f"film.subs check PASS: {len(files)} file(s), {n_cues} cues, {n_warn} warning(s)")


@app.command()
def build(cut: str = typer.Option(..., "--cut"), lang: str = typer.Option(..., "--lang")) -> None:
    """Half 2: build SRT and VTT for one cut and language from lines.csv and the edit list."""
    require(5_000_000, quiet=True)
    cues = build_cues(cut, lang)
    srt, vtt = write_subs(cut, lang, cues)
    typer.echo(f"film.subs build {cut}-{lang}: {len(cues)} cues -> {srt.name}, {vtt.name}")


@app.command("align-qa")
def align_qa(
    cut: str = typer.Option(..., "--cut"), lang: str = typer.Option(..., "--lang")
) -> None:
    """Cue text joins back to the script; cues sit inside their line's narration; read-back CER."""
    errors, warnings = align_errors(cut, lang)
    for w in warnings:
        typer.echo(f"WARN {w}")
    for e in errors:
        typer.echo(f"FAIL {e}")
    if errors:
        typer.echo(f"film.subs align-qa {cut}-{lang} FAIL: {len(errors)} error(s)")
        raise typer.Exit(1)
    typer.echo(f"film.subs align-qa {cut}-{lang} PASS ({len(warnings)} warning(s))")


if __name__ == "__main__":
    app()
