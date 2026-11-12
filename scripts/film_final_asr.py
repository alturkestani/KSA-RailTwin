"""Local ASR transcripts of the four final cuts' audio (FIX_TRAILER_AR item 4).

The barred-jargon test (tests/test_film_jargon.py) reads these transcripts, so a term that only
the voice says (and no text file shows) is still caught. Runs outside the project venv, with
mlx-whisper and the cached mlx-community/whisper-large-v3-turbo weights, offline:
  HF_HUB_OFFLINE=1 uv run --no-project --python 3.12 --with mlx-whisper==0.4.3 \
    python scripts/film_final_asr.py [main-en main-ar trailer-en trailer-ar]
Writes film/voice/readback/final-<cut>-<lang>.txt: a header (source file, its SHA-256, model,
date) and one line per Whisper segment, "[start-end] text". Transcripts are a screen, not a
script: Whisper writes digits and may merge words.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import mlx_whisper

ROOT = Path(__file__).resolve().parents[1]
MODEL = "mlx-community/whisper-large-v3-turbo"
CUTS = ["main-en", "main-ar", "trailer-en", "trailer-ar"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def transcribe(cut_lang: str) -> Path:
    cut, lang = cut_lang.split("-")
    rel = f"film/renders/out/ksa-rail-twin-{cut}-{lang}.mp4"
    mp4 = ROOT / rel
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-i",
                str(mp4),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                str(wav),
            ],
            check=True,
        )
        r = mlx_whisper.transcribe(
            str(wav),
            path_or_hf_repo=MODEL,
            language=lang,
            temperature=0.0,
            condition_on_previous_text=False,
        )
    lines = [
        f"# source: {rel}",
        f"# sha256: {sha256(mp4)}",
        f"# model: {MODEL} (local, offline), language={lang}, temperature 0",
        f"# date: {dt.date.today().isoformat()}",
    ]
    for s in r["segments"]:
        lines.append(f"[{s['start']:.2f}-{s['end']:.2f}] {s['text'].strip()}")
    out = ROOT / f"film/voice/readback/final-{cut}-{lang}.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    for c in sys.argv[1:] or CUTS:
        print(c, transcribe(c), flush=True)
