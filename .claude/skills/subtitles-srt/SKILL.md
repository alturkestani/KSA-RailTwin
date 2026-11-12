---
name: subtitles-srt
description: Producing and checking SRT and VTT subtitle files per language for both cuts and both trailers, with right-to-left Arabic rendered correctly, line-length and reading-speed limits, timing checks, mov_text muxing and QA by Whisper alignment. Use for everything under film/subs/.
---
> **Document version:** skills/subtitles-srt/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Subtitles (SRT/VTT)

Outputs per cut and trailer: `film/subs/<cut>.<lang>.srt` and `.vtt` for `ar` and `en` (Arabic cut: Arabic subtitles plus optional English; English cut: English plus optional Arabic). Text comes from `film/script/lines.csv` (the approved, native-reviewed lines), never retyped; figures identical to the script (digit-by-digit check).

## Timing
- Source of truth: the narration timing table from `film.voice` (start/end per line) aligned to the final audio with Whisper (`mlx-whisper` word timestamps or `whisperx`-style alignment; record the tool and model).
- Minimum duration 1.0 s, maximum 7.0 s per cue; gap ≥ 2 frames; no cue crosses a hard cut (shot boundaries from `film/storyboard/shots.yaml`).
- Reading speed 17–20 characters per second (Arabic counted in characters after shaping, excluding diacritics); split or extend cues that exceed 20 cps; flag any below 12 cps for review.
- Max 42 characters per line, max 2 lines; break at phrase boundaries, never inside a number or a place name.

## RTL Arabic correctness
- Store text as logical-order UTF-8; players handle bidi. Wrap each Arabic cue with the RLE/PDF or RLM marks only where mixed Latin (e.g. "SAR", "HSR") or digits break the order; test in at least two players (QuickTime/IINA or mpv, VLC) and screenshot the result into `film/subs/qa/`.
- Punctuation: Arabic comma «،», Arabic question mark «؟», Arabic semicolon «؛»; numbers in Arabic-Indic or Western digits consistently per the script's decision (recorded as an assumption `A-film-0xx`).
- Fonts for burned-in previews: Noto Naskh Arabic (OFL), registered.

## Formats and muxing
- SRT: numbered cues, `HH:MM:SS,mmm --> HH:MM:SS,mmm`, blank line between cues, UTF-8 without BOM.
- VTT: `WEBVTT` header, dot decimal separator, optional `STYLE` block; one cue identifier per line id.
- Mux as a selectable track: `ffmpeg -i cut.mp4 -i cut.ar.srt -c copy -c:s mov_text -metadata:s:s:0 language=ara -metadata:s:s:0 title="العربية" out.mp4` (add the second language as a second stream). Burned-in versions for the trailers only, if the storyboard asks.

## Commands and QA
`uv run python -m film.subs build --cut ar --lang ar --timing film/audio/ar/timing.json --lines film/script/lines.csv --out film/subs/` writes SRT and VTT; `uv run python -m film.subs check film/subs/` validates durations, cps, line lengths, overlaps, cue/line-id coverage (every narrated line has a cue), and runs the digit check against the script; `uv run python -m film.subs align-qa --audio film/audio/ar/mix.wav --srt film/subs/main.ar.srt` re-transcribes the audio with Whisper and reports the cues whose text differs from the transcript beyond a tolerance (hint of mistimed or mismatched cues). The `red-team-verifier` reads the check report; a failing check is a FAIL.
