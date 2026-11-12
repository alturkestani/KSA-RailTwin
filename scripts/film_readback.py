"""Whisper read-back of the narration lines (R10 half 2 QA; film.subs align-qa reads the result).

Runs in a local venv that has mlx-whisper (not a project dependency), from the cached
mlx-community/whisper-large-v3-turbo weights, offline:
  HF_HUB_OFFLINE=1 /tmp/r10-voice/venv-ar/bin/python scripts/film_readback.py main ar
Writes film/voice/readback/<cut>-<lang>.csv: line_id, engine, voice, cer, readback.
CER is a character error rate after light normalisation (diacritics, alef/ta-marbuta forms,
punctuation, thousands separators, "%" vs the spoken word); an intelligibility screen only.
"""

from __future__ import annotations

import csv
import re
import sys
import unicodedata
from pathlib import Path

import mlx_whisper

ROOT = Path(__file__).resolve().parents[1]


def norm(s: str, lang: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub("[ً-ْـ]", "", s)
    if lang == "ar":
        s = re.sub("[إأآ]", "ا", s).replace("ة", "ه").replace("ى", "ي").replace("%", " بالميه")
    else:
        s = s.lower().replace("%", " percent").replace("kilometers", "kilometres")
        s = s.replace("program ", "programme ")
        s = re.sub(r"(\d),(\d{3})", r"\1\2", s)
        s = re.sub(r"(\d+)000\b", r"\1 thousand", s)
    s = re.sub(r"[^\w\s.]", " ", s)
    s = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", s)
    return " ".join(s.split())


def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def main(cut: str, lang: str) -> None:
    texts = {
        r["line_id"]: r["text"]
        for r in csv.DictReader((ROOT / "film/script/lines.csv").open(encoding="utf-8"))
        if r["cut"] == cut and r["lang"] == lang
    }
    timing = list(
        csv.DictReader((ROOT / f"film/voice/timing/{cut}-{lang}.csv").open(encoding="utf-8"))
    )
    out = []
    for t in timing:
        wav = ROOT / f"film/audio/narration/{cut}-{lang}/{t['line_id']}.wav"
        r = mlx_whisper.transcribe(
            str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language=lang
        )
        a, b = norm(texts[t["line_id"]], lang), norm(r["text"], lang)
        cer = lev(a, b) / max(len(a), 1)
        out.append(
            {
                "line_id": t["line_id"],
                "engine": t["engine"],
                "voice": t["voice"],
                "cer": f"{cer:.3f}",
                "readback": r["text"].strip(),
            }
        )
        print(t["line_id"], out[-1]["cer"], flush=True)
    dst = ROOT / f"film/voice/readback/{cut}-{lang}.csv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
