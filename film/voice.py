"""Narration (R10 half 2): one WAV per script line, a timing table, two-pass loudnorm.

CLI:
  uv run python -m film.voice speak --cut main --lang ar [--only m-01-01,m-01-02] [--force]
  uv run python -m film.voice speak --cut trailer --lang en
  uv run python -m film.voice table --cut main --lang ar      (print the timing table)

Every `speak` passes the half-2 gate first (film/gate.py). Text comes from film/script/lines.csv
(never retyped); a spoken-text override for pronunciation only may be given in
film/voice/say.csv (cut, lang, line_id, say, reason). Settings and voice roles are in
cities/ksa/assumptions/film_voice.yaml.

Engines (default per language: `engine_by_lang` in the YAML; FIX_HALF2_QUALITY, 8 Nov 2026):
`elevenlabs` for English (one documentary narrator voice, Tariq's ElevenLabs account), `nabrah`
for Arabic (paid, approved: Nabrah public voices Daniah, Norah, Abdullah). Keys are read from the
main checkout's .env inside this process only, never printed or written. `chatterbox` is the open
fallback (Chatterbox Multilingual built-in voice through FILM_CHATTERBOX_PY, a local venv; used
only if a key is missing or a paid call fails). Arabic rows with a `speech_text` (full tashkeel,
lines.csv) send that text: it is the accepted line (or its say.csv override) plus diacritics
only, checked by film.script validate; subtitles keep the unvocalised accepted text.

Layout under film/audio (a symlink to the external volume):
  narration/raw/<engine>/<cut>-<lang>/<line_id>.wav    engine output, cached by text+voice hash
  narration/<cut>-<lang>/<line_id>.wav                 loudness-normalised, 48 kHz mono 16-bit
  narration/<cut>-<lang>/timing.csv                    one row per line (also copied, small, to
                                                       film/voice/timing/<cut>-<lang>.csv)
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

import httpx
import typer
import yaml

from common import REPO_ROOT
from film.gate import require

app = typer.Typer(add_completion=False, help="Narration (R10 half 2; gated).")

CONFIG = REPO_ROOT / "cities/ksa/assumptions/film_voice.yaml"
LINES = REPO_ROOT / "film/script/lines.csv"
SAY = REPO_ROOT / "film/voice/say.csv"
AUDIO = REPO_ROOT / "film/audio"
TIMING_COPY = REPO_ROOT / "film/voice/timing"
CHATTERBOX_PY = os.environ.get("FILM_CHATTERBOX_PY", "/tmp/r10-voice/venv-ar/bin/python")
TIMING_FIELDS = [
    "cut",
    "lang",
    "line_id",
    "section",
    "engine",
    "voice",
    "chars",
    "seconds",
    "input_i",
    "input_tp",
    "output_i",
    "output_tp",
    "said_override",
    "sha256",
    "voice_id",  # BUILD_MOVIE_EN: provider voice id and model on every row (empty on older tables)
    "model",
]


def load_config(path: Path = CONFIG) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main_checkout() -> Path:
    """The main checkout (holder of .env), also when running inside a worktree."""
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return Path(out).parent


def read_key(name: str, env_file: Path | None = None) -> str | None:
    """Read one key from the environment or the main checkout's .env; never print it."""
    if os.environ.get(name):
        return os.environ[name]
    path = env_file or Path(os.environ.get("FILM_ENV_FILE", main_checkout() / ".env"))
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*?)\s*$", line)
        if m and m.group(1) == name:
            return m.group(2).strip().strip('"').strip("'") or None
    return None


def load_lines(cut: str, lang: str, path: Path = LINES) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["cut"] == cut and r["lang"] == lang]


def load_say(path: Path = SAY) -> dict[tuple[str, str, str], str]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        return {(r["cut"], r["lang"], r["line_id"]): r["say"] for r in csv.DictReader(fh)}


def spoken_text(row: dict, say: dict) -> tuple[str, bool]:
    key = (row["cut"], row["lang"], row["line_id"])
    if row.get("speech_text"):  # vocalised (tashkeel) form of the accepted or say text
        return " ".join(row["speech_text"].split()), True
    if key in say:
        return " ".join(say[key].split()), True
    return " ".join(row["text"].split()), False


def voice_for(row: dict, cfg: dict, engine: str = "nabrah") -> str:
    if engine == "elevenlabs":
        return cfg["elevenlabs"]["voice"]["value"]
    roles = cfg["roles_by_section"]["value"]
    return roles[int(row["section"])]


def ffprobe_seconds(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return float(out)


def loudnorm_measure(path: Path, i: float, tp: float, lra: float) -> dict:
    """First loudnorm pass: measured values as JSON."""
    res = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    blob = res.stderr[res.stderr.rindex("{") : res.stderr.rindex("}") + 1]
    return json.loads(blob)


def loudnorm_two_pass(src: Path, dst: Path, i: float, tp: float, lra: float) -> tuple[dict, dict]:
    """Two-pass loudnorm to 48 kHz mono 16-bit; returns (first-pass, output) measurements."""
    m = loudnorm_measure(src, i, tp, lra)
    flt = (
        f"loudnorm=I={i}:TP={tp}:LRA={lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
        f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
        f":offset={m['target_offset']}:linear=true"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp.wav")
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-af", flt]
        + ["-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(tmp)],
        check=True,
    )
    tmp.replace(dst)
    return m, loudnorm_measure(dst, i, tp, lra)


def nabrah_tts(text: str, voice_id: str, cfg: dict, key: str, tries: int = 4) -> bytes:
    n = cfg["nabrah"]
    body = {
        "model": n["model"],
        "input": text,
        "voice": voice_id,
        "response_format": n["response_format"],
        "stream": False,
        "use_cache": True,
    }
    last = ""
    for k in range(tries):
        try:
            r = httpx.post(n["url"], headers={"X-API-Key": key}, json=body, timeout=240)
        except httpx.HTTPError as exc:
            last = type(exc).__name__
        else:
            if r.status_code == 200 and r.content[:4] == b"RIFF":
                return r.content
            last = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code in (400, 401, 402, 403, 404, 422):
                break
        time.sleep(3 * (k + 1))
    raise RuntimeError(f"nabrah call failed ({last})")


def elevenlabs_tts(text: str, voice: str, cfg: dict, key: str, ctx: tuple[str, str]) -> bytes:
    """ElevenLabs text-to-speech: MP3 bytes (the free tier's format), one call, fixed seed."""
    e = cfg["elevenlabs"]
    body = {
        "text": text,
        "model_id": e["model"],
        "voice_settings": e["voice_settings"],
        "seed": e["seed"],
        "previous_text": ctx[0],
        "next_text": ctx[1],
    }
    url = e["url"].format(voice_id=e["voices"][voice]) + f"?output_format={e['output_format']}"
    try:
        r = httpx.post(url, headers={"xi-api-key": key}, json=body, timeout=240)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"elevenlabs call failed ({type(exc).__name__})") from exc
    if r.status_code != 200 or r.content[:3] not in (b"ID3", b"\xff\xfb", b"\xff\xf3"):
        raise RuntimeError(f"elevenlabs call failed (HTTP {r.status_code}: {r.text[:200]})")
    return r.content


def elevenlabs_remaining(key: str) -> tuple[str, int]:
    """(tier, characters left this cycle) from GET /v1/user/subscription (no charge)."""
    r = httpx.get(
        "https://api.elevenlabs.io/v1/user/subscription", headers={"xi-api-key": key}, timeout=30
    )
    r.raise_for_status()
    j = r.json()
    return str(j.get("tier")), int(j["character_limit"]) - int(j["character_count"])


def mp3_to_wav(data: bytes, dst: Path) -> None:
    tmp = dst.with_suffix(".mp3")
    tmp.write_bytes(data)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp)]
        + ["-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
        check=True,
    )
    tmp.unlink()


def chatterbox_tts(text: str, lang: str, dst: Path) -> None:
    """Open fallback: Chatterbox Multilingual built-in voice in a separate local venv."""
    code = (
        "import sys,soundfile as sf\n"
        "from chatterbox.mtl_tts import ChatterboxMultilingualTTS as M\n"
        "m=M.from_pretrained(device='mps')\n"
        "w=m.generate(sys.argv[1],language_id=sys.argv[2])\n"
        "sf.write(sys.argv[3],w.squeeze().cpu().numpy(),m.sr)\n"
    )
    env = dict(os.environ, HF_HUB_OFFLINE="1")
    subprocess.run([CHATTERBOX_PY, "-c", code, text, lang, str(dst)], check=True, env=env)


def cached_raw(engine: str, voice: str, text: str, cut: str, lang: str, lid: str) -> Path:
    h = text_hash(engine, voice, text)
    raw = AUDIO / "narration" / "raw" / engine / f"{cut}-{lang}" / f"{lid}.{h}.wav"
    raw.parent.mkdir(parents=True, exist_ok=True)
    return raw


def voice_id_for(engine: str, voice: str, cfg: dict) -> str:
    """The provider's id for a named voice (an identifier, not a secret); empty for Chatterbox."""
    return str(cfg.get(engine, {}).get("voices", {}).get(voice, "")) if engine in cfg else ""


def text_hash(engine: str, voice: str, text: str) -> str:
    return hashlib.sha256(f"{engine}|{voice}|{text}".encode()).hexdigest()[:16]


def neighbours(rows: list[dict], say: dict, i: int) -> tuple[str, str]:
    """Previous and next spoken lines (ElevenLabs uses them for continuous prosody)."""
    prev = spoken_text(rows[i - 1], say)[0] if i > 0 else ""
    nxt = spoken_text(rows[i + 1], say)[0] if i + 1 < len(rows) else ""
    return prev, nxt


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_timing(rows: list[dict], cut: str, lang: str, audio_root: Path) -> Path:
    out = audio_root / "narration" / f"{cut}-{lang}" / "timing.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    for dest in (out, TIMING_COPY / f"{cut}-{lang}.csv"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=TIMING_FIELDS)
            w.writeheader()
            w.writerows(rows)
    return out


def load_timing(cut: str, lang: str, root: Path | None = None) -> dict[str, dict]:
    path = (root or TIMING_COPY) / f"{cut}-{lang}.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        return {r["line_id"]: r for r in csv.DictReader(fh)}


def log_paid(chars: int, cfg: dict, note: str, engine: str = "nabrah") -> float:
    step = os.environ.get("FILM_STEP", "FIX_HALF2_QUALITY")  # the milestone label in the log
    if engine == "elevenlabs":
        e = cfg["elevenlabs"]
        usd = round(chars * e["usd_per_1000_chars"]["value"] / 1000, 2)
        vendor, model = "ElevenLabs", f"{e['model']} ({e['voice']['value']})"
        note = f"{note}; {chars:,} chars ({e['usd_per_1000_chars']['reason']})"
    else:
        n = cfg["nabrah"]
        credits = chars * n["credits_per_1000_chars"] / 1000
        usd = round(credits * n["usd_per_credit"]["value"], 2)
        vendor, model = "Nabrah AI", "nabrah_tts_v1 (Daniah, Norah, Abdullah)"
        note = f"{note}; {chars:,} chars = {credits:,.0f} credits (A-film-011 rate)"
    subprocess.run(
        ["uv", "run", "python", "-m", "common.cost_log", "add-paid", "--vendor", vendor]
        + ["--model", model, "--usd", f"{usd}"]
        + ["--step", f"Paid-model request 1 (R10 narration; {step})"]
        + ["--approved-usd", "60", "--note", note],
        check=True,
        cwd=REPO_ROOT,
    )
    return usd


@app.callback()
def _main() -> None:
    """Narration (R10 half 2; gated)."""


@app.command()
def speak(
    cut: str = typer.Option(..., "--cut", help="main or trailer"),
    lang: str = typer.Option(..., "--lang", help="ar or en"),
    engine: str = typer.Option("", "--engine", help="elevenlabs, nabrah or chatterbox"),
    only: str = typer.Option("", "--only", help="comma-separated line ids"),
    force: bool = typer.Option(False, "--force", help="re-synthesise even if cached"),
    no_cost_log: bool = typer.Option(False, "--no-cost-log", help="tests only"),
    fallback: bool = typer.Option(
        True, "--fallback/--no-fallback", help="BUILD_MOVIE: --no-fallback stops on a paid failure"
    ),
) -> None:
    """Synthesise one WAV per line, loudness-normalise it and write the timing table."""
    cfg = load_config()
    rows = load_lines(cut, lang)
    if not rows:
        typer.echo(f"no lines for cut={cut} lang={lang}")
        raise typer.Exit(1)
    est = sum(len(r["text"]) for r in rows) / 12 * 48000 * 2 * 3  # raw + normalised + slack
    require(int(est))
    engine = engine or cfg.get("engine_by_lang", {}).get(lang) or cfg["engine"]
    say = load_say()
    want = {x for x in only.split(",") if x}
    key_name = {"nabrah": "NABRAH_API_KEY", "elevenlabs": "ELEVENLABS_API_KEY"}.get(engine)
    key = read_key(key_name) if key_name else None
    if key_name and not key:
        if not fallback:
            typer.echo(f"{key_name} not found: nothing sent, no fallback")
            raise typer.Exit(3)
        typer.echo(f"{key_name} not found: falling back to chatterbox (reported)")
        engine = "chatterbox"
    if engine == "elevenlabs":
        need = sum(len(spoken_text(r, say)[0]) for r in rows if not want or r["line_id"] in want)
        tier, left = elevenlabs_remaining(key or "")
        typer.echo(f"ElevenLabs tier {tier}: {left:,} characters left; this call needs <= {need:,}")
        if need > left:
            typer.echo("not enough ElevenLabs characters left: nothing sent")
            raise typer.Exit(1)
    lo = cfg["loudness"]
    timing_path = TIMING_COPY / f"{cut}-{lang}.csv"
    old = load_timing(cut, lang) if timing_path.exists() else {}
    out_rows: list[dict] = []
    failures: list[str] = []
    nabrah_down = False
    paid_chars = 0
    for i, r in enumerate(rows):
        lid = r["line_id"]
        if want and lid not in want:
            if lid in old:
                out_rows.append(old[lid])
            continue
        text, overridden = spoken_text(r, say)
        line_engine = engine
        paid = engine in ("nabrah", "elevenlabs")
        voice = voice_for(r, cfg, engine) if paid else "chatterbox-builtin"
        ctx = neighbours(rows, say, i) if engine == "elevenlabs" else ("", "")
        key_text = "|".join((text, *ctx)) if any(ctx) else text
        raw = cached_raw(engine, voice, key_text, cut, lang, lid)
        if paid and nabrah_down and (force or not raw.exists()):
            line_engine = "chatterbox"
        elif engine == "elevenlabs" and (force or not raw.exists()):
            try:
                mp3_to_wav(elevenlabs_tts(text, voice, cfg, key or "", ctx), raw)
                paid_chars += len(text)
            except RuntimeError as exc:
                failures.append(f"{lid}: {exc}")
                if not fallback:  # never mix voices (BUILD_MOVIE)
                    typer.echo(f"{lid}: ElevenLabs failed ({exc}); stopping, no fallback")
                    break
                typer.echo(f"{lid}: ElevenLabs failed ({exc}); falling back to chatterbox")
                line_engine = "chatterbox"
                nabrah_down = True
        elif engine == "nabrah" and (force or not raw.exists()):
            try:
                vid = cfg["nabrah"]["voices"][voice]
                raw.write_bytes(nabrah_tts(text, vid, cfg, key or ""))
                paid_chars += len(text)
            except RuntimeError as exc:
                failures.append(f"{lid}: {exc}")
                if not fallback:  # never mix voices (BUILD_MOVIE)
                    typer.echo(f"{lid}: Nabrah failed ({exc}); stopping, no fallback")
                    break
                typer.echo(f"{lid}: Nabrah failed ({exc}); falling back to chatterbox (reported)")
                line_engine = "chatterbox"
                nabrah_down = True
        if line_engine == "chatterbox":
            voice = "chatterbox-builtin"
            raw = cached_raw("chatterbox", voice, text, cut, lang, lid)
            if force or not raw.exists():
                chatterbox_tts(text, lang, raw)
        dst = AUDIO / "narration" / f"{cut}-{lang}" / f"{lid}.wav"
        m1, m2 = loudnorm_two_pass(raw, dst, lo["integrated_lufs"], lo["true_peak_dbtp"], lo["lra"])
        out_rows.append(
            {
                "cut": cut,
                "lang": lang,
                "line_id": lid,
                "section": r["section"],
                "engine": line_engine,
                "voice": voice,
                "chars": len(text),
                "seconds": f"{ffprobe_seconds(dst):.3f}",
                "input_i": m1["input_i"],
                "input_tp": m1["input_tp"],
                "output_i": m2["input_i"],
                "output_tp": m2["input_tp"],
                "said_override": "yes" if overridden else "",
                "sha256": sha256_file(dst),
                "voice_id": voice_id_for(line_engine, voice, cfg),
                "model": cfg.get(line_engine, {}).get("model", ""),
            }
        )
        typer.echo(f"{lid} {voice} {out_rows[-1]['seconds']} s, {m2['input_i']} LUFS")
    if failures and not fallback:
        if paid_chars and not no_cost_log:
            log_paid(paid_chars, cfg, f"narration {cut}-{lang}: stopped after a failure", engine)
        typer.echo(f"stopped: {failures[0]} (timing table not rewritten)")
        raise typer.Exit(3)
    path = write_timing(out_rows, cut, lang, AUDIO)
    if failures:
        fail_log = AUDIO / "narration" / f"{cut}-{lang}" / "fallback.txt"
        fail_log.write_text("\n".join(failures) + "\n", encoding="utf-8")
        typer.echo(f"{len(failures)} line(s) fell back to chatterbox: see {fail_log}")
    total = sum(float(x["seconds"]) for x in out_rows)
    typer.echo(f"film.voice speak: {len(out_rows)} lines, {total:.1f} s narration -> {path}")
    if paid_chars and not no_cost_log:
        log_paid(paid_chars, cfg, f"narration {cut}-{lang}: {len(out_rows)} lines", engine)


@app.command()
def table(cut: str = typer.Option(..., "--cut"), lang: str = typer.Option(..., "--lang")) -> None:
    """Print the committed timing table for one cut and language."""
    rows = load_timing(cut, lang)
    for r in rows.values():
        typer.echo(f"{r['line_id']}\t{r['voice']}\t{r['seconds']}\t{r['output_i']}")
    typer.echo(f"total {sum(float(r['seconds']) for r in rows.values()):.1f} s")


if __name__ == "__main__":
    app()
