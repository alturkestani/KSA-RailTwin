"""Social deliverables from the final cuts (CLOSE_R10; gated): burned-in subtitles, SRTs, covers.

  uv run python -m film.social burn --cut main --lang ar     # renders/out/social/<name>.subs.mp4
  uv run python -m film.social plain --cut main --lang en    # byte-identical copy of the cut
  uv run python -m film.social cover --lang ar --at 760.0    # one sim_map frame + the film title
  uv run python -m film.social manifest                      # duration, size, SHA-256, flags

Nothing is re-voiced or re-cut. The burned versions overlay the cut's own subtitle file
(film/subs/<cut>.<lang>.srt, built from lines.csv) on its picture and copy its AAC audio stream
unchanged, so loudness and resolution are the cut's. This ffmpeg build has no libass, so each cue
is drawn by headless Chrome with the film's fonts (correct Arabic shaping and RTL order) and the
PNG sequence is overlaid with ffmpeg's concat demuxer. The cue sits in a band at the top of the
frame: the bottom of every shot carries the on-screen caption and the map credits. The band is at
most 800 px wide (x 560-1360), so it stays between the top-corner elements of the shots: the
three-layer legend (from x 1364 in English, mirrored in Arabic) and the "composite journey" pill.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import typer
import yaml

from common import REPO_ROOT
from film import render as R
from film.gate import require
from film.subs import Cue, Result, parse_srt

app = typer.Typer(add_completion=False, help="Social deliverables from the final cuts (CLOSE_R10).")

OUT = R.RENDERS / "out"
SOCIAL = OUT / "social"
SUBS = REPO_ROOT / "film/subs"
MANIFEST = REPO_ROOT / "film/assemble/social.csv"
META = REPO_ROOT / "film/script/meta.yaml"
LIMIT_S, LIMIT_BYTES = 15 * 60, 512 * 1024 * 1024  # LinkedIn video limits named in the prompt
CRF = 18  # same quality setting as the shot renders' overlay encode (film/render.py)


def cut_mp4(cut: str, lang: str) -> Path:
    return OUT / f"ksa-rail-twin-{cut}-{lang}.mp4"


def load_cues(cut: str, lang: str) -> list[Cue]:
    res = Result()
    cues = parse_srt((SUBS / f"{cut}.{lang}.srt").read_text(encoding="utf-8"), res)
    if res.errors:
        raise ValueError(f"{cut}.{lang}.srt: {res.errors[:3]}")
    return cues


def cue_html(lines: list[str], lang: str) -> str:
    d = "rtl" if lang == "ar" else "ltr"
    rows = "".join(f"<div>{html.escape(x.strip(chr(0x200F)))}</div>" for x in lines)
    css = (
        "<style>.sub{position:absolute;left:0;right:0;top:28px;text-align:center}"
        ".sub span{display:inline-block;box-sizing:border-box;max-width:800px;font-size:34px;"
        "line-height:1.36;"
        "font-weight:700;color:#FFFFFF;background:rgba(8,12,20,.80);padding:10px 26px;"
        "border-radius:8px}</style>"
    )
    return R.page(
        f'{css}<div class="sub"><span dir="{d}" lang="{lang}">{rows}</span></div>',
        transparent=True,
        lang=lang,
    )


def concat_list(cues: list[Cue], pngs: list[Path], blank: Path, total: float) -> str:
    """ffmpeg concat-demuxer script: the blank frame in gaps, each cue PNG for its span."""
    out, t = ["ffconcat version 1.0"], 0.0
    for c, p in zip(cues, pngs, strict=True):
        if c.start > t + 1e-6:
            out += [f"file '{blank}'", f"duration {c.start - t:.3f}"]
        out += [f"file '{p}'", f"duration {c.end - c.start:.3f}"]
        t = c.end
    out += [f"file '{blank}'", f"duration {max(total - t, 0.04):.3f}", f"file '{blank}'"]
    return "\n".join(out) + "\n"


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(out)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def name(cut: str, lang: str, kind: str) -> str:
    return f"ksa-rail-twin-{cut}-{lang}{'.subs' if kind == 'subs' else ''}"


@app.command()
def burn(
    cut: str = typer.Option(..., "--cut"),
    lang: str = typer.Option(..., "--lang"),
    workers: int = typer.Option(4, "--workers"),
) -> None:
    """Burn the cut's own subtitles into its picture; audio stream copied unchanged."""
    src = cut_mp4(cut, lang)
    info = probe(src)
    total = float(info["format"]["duration"])
    require(int(total * 4e6) + 200_000_000)
    cues = load_cues(cut, lang)
    work = R.RENDERS / "_social" / f"{cut}-{lang}"
    shutil.rmtree(work, ignore_errors=True)  # ExFAT: macOS ._ sidecars vanish with their file
    work.mkdir(parents=True, exist_ok=True)
    blank = work / "blank.png"
    R.chrome_png(R.page("", transparent=True, lang=lang), blank, transparent=True)
    pngs = [work / f"cue{i:04d}.png" for i in range(1, len(cues) + 1)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(
            ex.map(
                lambda cp: R.chrome_png(cue_html(cp[0].lines, lang), cp[1], transparent=True),
                zip(cues, pngs, strict=True),
            )
        )
    lst = work / "subs.ffconcat"
    lst.write_text(concat_list(cues, pngs, blank, total), encoding="utf-8")
    SOCIAL.mkdir(parents=True, exist_ok=True)
    mp4 = SOCIAL / f"{name(cut, lang, 'subs')}.mp4"
    tmp = mp4.with_suffix(".new.mp4")
    flt = (
        f"[1:v]fps={R.FPS},format=rgba[s];"
        "[0:v][s]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src)]
    cmd += ["-f", "concat", "-safe", "0", "-i", str(lst), "-filter_complex", flt]
    cmd += ["-map", "[v]", "-map", "0:a", "-r", str(R.FPS), "-c:v", "libx264", "-preset"]
    cmd += ["medium", "-crf", str(CRF), "-pix_fmt", "yuv420p", "-c:a", "copy", "-sn"]
    cmd += ["-map_metadata", "0", "-movflags", "+faststart", "-t", f"{total:.3f}", str(tmp)]
    subprocess.run(cmd, check=True)
    tmp.replace(mp4)
    shutil.copyfile(SUBS / f"{cut}.{lang}.srt", SOCIAL / f"{name(cut, lang, 'subs')}.srt")
    typer.echo(f"film.social burn {cut}-{lang}: {mp4} ({len(cues)} cues)")


@app.command()
def plain(cut: str = typer.Option(..., "--cut"), lang: str = typer.Option(..., "--lang")) -> None:
    """Byte-identical copy of the final cut, plus its subtitle file."""
    src = cut_mp4(cut, lang)
    require(src.stat().st_size + 10_000_000)
    SOCIAL.mkdir(parents=True, exist_ok=True)
    dst = SOCIAL / f"{name(cut, lang, 'plain')}.mp4"
    shutil.copyfile(src, dst)
    if sha256(dst) != sha256(src):
        raise SystemExit(f"copy differs: {dst}")
    shutil.copyfile(SUBS / f"{cut}.{lang}.srt", SOCIAL / f"{name(cut, lang, 'plain')}.srt")
    typer.echo(f"film.social plain {cut}-{lang}: {dst}")


@app.command()
def cover(
    lang: str = typer.Option(..., "--lang"),
    at: float = typer.Option(..., "--at", help="frame time (s) in the main cut"),
) -> None:
    """One frame of the main cut with the film title over its caption band (credits kept)."""
    require(50_000_000)
    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    work = R.RENDERS / "_social"
    work.mkdir(parents=True, exist_ok=True)
    frame = work / f"cover-frame-{lang}.png"
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{at:.3f}"]
        + ["-i", str(cut_mp4("main", lang)), "-frames:v", "1", str(frame)],
        check=True,
    )
    d = "rtl" if lang == "ar" else "ltr"
    # the project's standard label (rule 3), after a short "independent simulation" line
    sub = {"en": "An independent simulation study · ", "ar": "دراسة محاكاة مستقلة · "}[lang]
    sub += R.FOOTER[lang][0]
    credit = {  # the cover frame is the census shot sh-03-01 (population dots), so credit GASTAT
        "en": "Population: GASTAT, Census 2022 (derived)",
        "ar": "السكان: الهيئة العامة للإحصاء، تعداد 2022 (جداول مشتقة)",
    }[lang]
    body = (
        f'<img src="{frame.as_uri()}" style="position:absolute;left:0;top:0;width:{R.W}px;'
        f'height:{R.H}px">'
        '<div style="position:absolute;left:0;right:0;top:700px;height:322px;'
        'background:linear-gradient(rgba(5,8,16,0),rgba(5,8,16,1) 40%,rgba(5,8,16,1))"></div>'
        f'<div dir="{d}" lang="{lang}" style="position:absolute;left:120px;right:120px;'
        'top:808px;text-align:center;color:#FFF3DA">'
        f'<div style="font-size:84px;font-weight:700;line-height:1.2">'
        f"{html.escape(meta[f'title_{lang}'])}</div>"
        f'<div style="font-size:30px;margin-top:12px;color:#D8D2C4">{html.escape(sub)}</div>'
        f'<div style="font-size:22px;margin-top:8px;color:#B9B2A4">{html.escape(credit)}</div>'
        "</div>"
    )
    SOCIAL.mkdir(parents=True, exist_ok=True)
    staged = work / f"cover-{lang}.png"  # Chrome writes its .html beside the PNG: keep it in work
    R.chrome_png(R.page(body, transparent=False, lang=lang), staged, transparent=False)
    png = SOCIAL / f"ksa-rail-twin-cover-{lang}.png"
    shutil.copyfile(staged, png)
    typer.echo(f"film.social cover {lang}: {png} (frame at {at:.3f} s of main-{lang})")


@app.command()
def manifest() -> None:
    """Duration, size and SHA-256 of every file under renders/out/social/, with the limit flags."""
    rows = []
    for p in sorted(SOCIAL.iterdir()):
        if p.name.startswith(".") or p.suffix not in (".mp4", ".srt", ".png"):
            continue
        dur = float(probe(p)["format"]["duration"]) if p.suffix == ".mp4" else None
        size = p.stat().st_size
        flags = []
        if dur is not None and dur > LIMIT_S:
            flags.append("over 15:00 (LinkedIn limit)")
        if size > LIMIT_BYTES:
            flags.append("over 512 MB")
        rows.append(
            {
                "file": p.name,
                "duration_s": f"{dur:.3f}" if dur is not None else "",
                "duration": f"{int(dur // 60)}:{dur % 60:06.3f}" if dur is not None else "",
                "bytes": size,
                "mib": f"{size / 2**20:.1f}",
                "sha256": sha256(p),
                "flags": "; ".join(flags),
            }
        )
    with MANIFEST.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        typer.echo(
            f"{r['file']}\t{r['duration']}\t{r['mib']} MiB\t{r['sha256'][:16]}\t{r['flags']}"
        )


if __name__ == "__main__":
    app()
