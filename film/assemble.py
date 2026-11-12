"""Edit list, narration master and cut assembly with ffmpeg (R10 half 2; gated).

CLI (order of a full build; each step passes the half-2 gate):
  uv run python -m film.assemble edl --cut main --lang ar        edit list from measured narration
  uv run python -m film.render all --cut main --lang ar           shots at 1080p30
  uv run python -m film.subs build --cut main --lang ar           SRT + VTT from lines.csv
  uv run python -m film.assemble cut --cut main --lang ar         MP4 with narration + subtitles
  uv run python -m film.assemble all                              all four (main/trailer x ar/en)

Edit list (film/assemble/edl-<cut>-<lang>.csv, committed, small): shots in storyboard order; a
narrated shot lasts head + its lines + gaps + tail (A-film-008..010, film_voice.yaml); a shot
without narration keeps its storyboard duration_s. Line times go to
film/assemble/lines-<cut>-<lang>.csv (the subtitle timing source).
Narration master: every line WAV placed at its start, then a two-pass loudnorm of the whole track
to -16 LUFS / -1.5 dBTP (A-film-007); measured values in film/assemble/loudness.csv.
No music bed (none cleared without a new account; docs/film.md).
Outputs (external volume through film/renders): film/renders/out/ksa-rail-twin-<cut>-<lang>.mp4.
"""

from __future__ import annotations

import csv
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
import typer

from common import REPO_ROOT
from film.gate import require
from film.shots import load_shots
from film.voice import AUDIO, load_config, load_timing, loudnorm_measure, loudnorm_two_pass

app = typer.Typer(add_completion=False, help="Edit list and cut assembly (R10 half 2; gated).")

SHOTS = REPO_ROOT / "film/storyboard/shots.yaml"
ASM = REPO_ROOT / "film/assemble"
RENDERS = REPO_ROOT / "film/renders"
SUBS = REPO_ROOT / "film/subs"
SR = 48000
CUTS = (("main", "ar"), ("main", "en"), ("trailer", "ar"), ("trailer", "en"))
TITLE = {
    "ar": "سكة تربط البلد",
    "en": "A Railway to Connect the Country",
}


def build_edl(cut: str, lang: str, shots: list[dict], timing: dict[str, dict], cfg: dict):
    head = cfg["shot_head_s"]["value"]
    tail = cfg["shot_tail_s"]["value"]
    gap = cfg["gap_between_lines_s"]["value"]
    edl, lines = [], []
    t = 0.0
    for s in [x for x in shots if x["cut"] == cut]:
        ids = s.get("narration_line_ids") or []
        if ids:
            cur = t + head
            for i, lid in enumerate(ids):
                sec = float(timing[lid]["seconds"])
                lines.append(
                    {
                        "line_id": lid,
                        "shot_id": s["id"],
                        "start_s": round(cur, 3),
                        "end_s": round(cur + sec, 3),
                    }
                )
                cur += sec + (gap if i < len(ids) - 1 else 0)
            dur = cur + tail - t
        else:
            dur = float(s["duration_s"])
        dur = round(round(dur * 30) / 30, 4)  # whole frames
        edl.append(
            {
                "shot_id": s["id"],
                "section": s["section"],
                "start_s": round(t, 3),
                "duration_s": dur,
                "line_ids": " ".join(ids),
                "storyboard_s": s["duration_s"],
            }
        )
        t += dur
    return edl, lines


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")


def narration_master(cut: str, lang: str) -> tuple[Path, dict]:
    edl = _read(ASM / f"edl-{cut}-{lang}.csv")
    lines = _read(ASM / f"lines-{cut}-{lang}.csv")
    total = float(edl[-1]["start_s"]) + float(edl[-1]["duration_s"])
    buf = np.zeros(int(round(total * SR)) + SR, dtype="int32")
    for ln in lines:
        a = read_wav(AUDIO / "narration" / f"{cut}-{lang}" / f"{ln['line_id']}.wav")
        i = int(round(float(ln["start_s"]) * SR))
        buf[i : i + len(a)] += a
    buf = np.clip(buf[: int(round(total * SR))], -32768, 32767).astype("<i2")
    raw = AUDIO / "master" / f"{cut}-{lang}.placed.wav"
    raw.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(buf.tobytes())
    lo = load_config()["loudness"]
    out = AUDIO / "master" / f"{cut}-{lang}.wav"
    tp = lo["true_peak_dbtp"] - lo.get("aac_headroom_db", 0.0)  # AAC adds inter-sample peaks
    first, final = loudnorm_two_pass(raw, out, lo["integrated_lufs"], tp, lo["lra"])
    return out, {"first": first, "final": final, "seconds": total}


def record_loudness(cut: str, lang: str, stage: str, m: dict) -> None:
    p = ASM / "loudness.csv"
    rows = _read(p) if p.exists() else []
    rows = [r for r in rows if not (r["cut"] == cut and r["lang"] == lang and r["stage"] == stage)]
    rows.append(
        {
            "cut": cut,
            "lang": lang,
            "stage": stage,
            "integrated_lufs": m["input_i"],
            "true_peak_dbtp": m["input_tp"],
            "lra": m["input_lra"],
        }
    )
    rows.sort(key=lambda r: (r["cut"], r["lang"], r["stage"]))
    _write(p, rows)


def mux_cut(cut: str, lang: str) -> Path:
    edl = _read(ASM / f"edl-{cut}-{lang}.csv")
    vids = [RENDERS / f"{cut}-{lang}" / f"{r['shot_id']}.mp4" for r in edl]
    missing = [str(v) for v in vids if not v.exists()]
    if missing:
        raise FileNotFoundError(f"missing renders: {missing[:3]} ...")
    out_dir = RENDERS / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    lst = out_dir / f"{cut}-{lang}.concat.txt"
    lst.write_text("".join(f"file '{v}'\n" for v in vids), encoding="utf-8")
    picture = out_dir / f"{cut}-{lang}.picture.mp4"
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0"]
        + ["-i", str(lst), "-c", "copy", str(picture)],
        check=True,
    )
    audio = AUDIO / "master" / f"{cut}-{lang}.wav"
    srt = SUBS / f"{cut}.{lang}.srt"
    mp4 = out_dir / f"ksa-rail-twin-{cut}-{lang}.mp4"
    iso = {"ar": "ara", "en": "eng"}[lang]
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(picture),
        "-i",
        str(audio),
    ]
    cmd += ["-i", str(srt), "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy"]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-c:s", "mov_text"]
    cmd += ["-metadata:s:a:0", f"language={iso}", "-metadata:s:s:0", f"language={iso}"]
    cmd += ["-metadata", f"title={TITLE[lang]} ({cut})", "-movflags", "+faststart"]
    total = float(probe(picture)["format"]["duration"])  # not -shortest: subtitles end early
    tmp = mp4.with_suffix(".new.mp4")  # the previous cut stays until its replacement exists
    subprocess.run([*cmd, "-t", f"{total:.3f}", str(tmp)], check=True)
    tmp.replace(mp4)
    return mp4


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return json.loads(out)


@app.callback()
def _main() -> None:
    """Edit list and cut assembly (R10 half 2; gated)."""


@app.command()
def edl(cut: str = typer.Option(..., "--cut"), lang: str = typer.Option(..., "--lang")) -> None:
    """Write the edit list and line times from the measured narration."""
    require(1_000_000, quiet=True)
    rows, lines = build_edl(cut, lang, load_shots(SHOTS), load_timing(cut, lang), load_config())
    _write(ASM / f"edl-{cut}-{lang}.csv", rows)
    _write(ASM / f"lines-{cut}-{lang}.csv", lines)
    total = sum(float(r["duration_s"]) for r in rows)
    typer.echo(f"film.assemble edl {cut}-{lang}: {len(rows)} shots, {total:.1f} s")


@app.command("cut")
def cut_(cut: str = typer.Option(..., "--cut"), lang: str = typer.Option(..., "--lang")) -> None:
    """Narration master (two-pass loudnorm) + concatenated shots + mov_text subtitles."""
    edl_rows = _read(ASM / f"edl-{cut}-{lang}.csv")
    total = sum(float(r["duration_s"]) for r in edl_rows)
    require(int(total * 2.5e6) + 200_000_000)
    master, m = narration_master(cut, lang)
    record_loudness(cut, lang, "narration_master", m["final"])
    mp4 = mux_cut(cut, lang)
    # measure the delivered (AAC) audio of the final file
    final = loudnorm_measure(mp4, -16.0, -1.5, 11.0)
    record_loudness(cut, lang, "final_mp4", final)
    info = probe(mp4)
    dur = float(info["format"]["duration"])
    typer.echo(
        f"film.assemble cut {cut}-{lang}: {mp4} {dur:.1f} s; "
        f"{final['input_i']} LUFS, {final['input_tp']} dBTP"
    )


@app.command("all")
def all_() -> None:
    """Assemble all four outputs (needs edl, renders and subtitles for each)."""
    for cut, lang in CUTS:
        cut_(cut=cut, lang=lang)


if __name__ == "__main__":
    app()
