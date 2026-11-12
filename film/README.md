> **Document version:** film/README.md v1.1 | 8 Nov 2026 | Author: R10 builder (v1.1: R10_HALF2 external output layout, gate checks and half-2 commands) | Status: draft (CP9)

# film/: the W10 documentary tooling (R10)

Half 1 wrote and checked the bilingual script, storyboard, rights log and subtitle checker. Half 2 (launched by Tariq on 7 Nov 2026, `prompts/R10_HALF2.md`) produces narration, renders, subtitles and the four MP4s; the results and their caveats are in `docs/film.md`.

## Layout

| path | what |
|---|---|
| `script/lines.csv`, `script/meta.yaml` | the script: one row per line per language and cut; title, section titles and version header |
| `script/{main,trailer}.{ar,en}.md` | rendered from the two files above by `film.script render`; never edited by hand |
| `storyboard/shots.yaml` | shot list (one entry per shot, linked to script line ids) |
| `rights_log.csv` | every voice, model, font, music track, image, footage, tool, data set and service used in the film |
| `voice/timing/<cut>-<lang>.csv` | measured narration per line (engine, voice, seconds, loudness before/after); small, committed |
| `voice/readback/<cut>-<lang>.csv` | Whisper read-back CER per line (`scripts/film_readback.py`) |
| `assemble/edl-*.csv`, `assemble/lines-*.csv` | edit list (shot starts and durations) and line times from the measured narration |
| `assemble/renders-*.csv`, `assemble/loudness.csv` | render manifest (figures traced to the data sources) and measured loudness |
| `subs/{main,trailer}.{ar,en}.{srt,vtt}`, `subs/qa/` | subtitles built from `lines.csv` and the RTL/bidi QA screenshots |
| `assumptions-r10.md` | film assumptions register (A-film-*) |
| `audio`, `renders` | **symlinks** to the external volume (below); gitignored, never committed |

## External output (R10_HALF2)

Bulky output lives on `/Volumes/Extreme_SSD/Projects/KSA-RailTwin/` (ExFAT): `renders/`, `audio/`, `cache/`, `models/`, `assemble/`, `tmp/` and `archive/worktrees/`, with a `README.txt`. The git repository stays on the internal disk. In the r10 worktree `film/renders` and `film/audio` are Unix symlinks (on APFS) to the external `renders/` and `audio/`; `.gitignore` names them without a trailing slash so the symlinks themselves are ignored.

- `film/audio/narration/raw/<engine>/<cut>-<lang>/` engine output, cached by a hash of engine, voice and text
- `film/audio/narration/<cut>-<lang>/<line>.wav` loudness-normalised line WAVs (48 kHz mono 16-bit)
- `film/audio/master/<cut>-<lang>.wav` narration master per cut
- `film/renders/<cut>-<lang>/<shot>.mp4` and `frames/` (the HTML/PNG layers)
- `film/renders/out/ksa-rail-twin-<cut>-<lang>.mp4` the four deliverables; `film/renders/out/script/*.pdf` script PDFs

## The half-2 gate (`film/gate.py`)

`film.voice speak`, `film.render shot|all`, `film.assemble edl|cut|all` and `film.subs build` call `gate.require()` first and exit 2 without writing anything unless all of these hold: a line starting `R10_HALF2 launch recorded:` is in `docs/status/r10.md`; `/Volumes/Extreme_SSD` is mounted; `film/renders` and `film/audio` resolve inside `/Volumes/Extreme_SSD/Projects/KSA-RailTwin`; the output volume has at least 50 GiB free; and the next write (the command's own estimate) leaves at least 10 GB free on the output volume and on the internal disk. `film.render all` re-checks before every shot. Tests override the paths with `FILM_EXTERNAL_VOLUME`, `FILM_EXTERNAL_ROOT` and `FILM_HOME_VOLUME`.

## Commands

```
# half 1 (checks)
uv run python -m film.script validate film/script/
uv run python -m film.shots check film/storyboard/shots.yaml --lines film/script/lines.csv
uv run python -m film.rights check film/rights_log.csv
uv run python -m film.subs check film/subs/ --fps 30

# half 2 (gated), per cut (main|trailer) and language (ar|en)
uv run python -m film.voice speak --cut main --lang ar        # Nabrah; Chatterbox fallback per line
uv run python -m film.assemble edl --cut main --lang ar       # edit list from measured narration
RAILTWIN_RUNS_ROOT=~/Documents/Projects/KSA-RailTwin/runs \
  uv run python -m film.render all --cut main --lang ar       # 1080p30 shots
uv run python -m film.subs build --cut main --lang ar         # SRT + VTT
uv run python -m film.subs align-qa --cut main --lang ar      # text, timing, read-back CER
uv run python -m film.assemble cut --cut main --lang ar       # narration master + MP4
```

Keys: `film.voice` reads `NABRAH_API_KEY` from the environment or from the main checkout's `.env` inside its own process; it never prints, logs or writes a key. Settings: `cities/ksa/assumptions/film_voice.yaml` (voice ids, roles, loudness, pauses) and `cities/ksa/assumptions/film_timing.yaml` (half-1 estimates). In a worktree, `runs/` is not checked out: set `RAILTWIN_RUNS_ROOT` to the main checkout's `runs` directory so `run:` sources resolve and the render manifest can trace figures.

The film register is kept under `film/` and not as `docs/assumptions-r10.md` because `docs/assumptions*.md` feeds the R8 report annexes, and the film must not change any R8 reader-facing file.
