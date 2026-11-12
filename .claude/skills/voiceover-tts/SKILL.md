---
name: voiceover-tts
description: The W10 voice procedure: verifying each open and commercial TTS candidate's current availability, licence and commercial-use terms, the common Saudi-dialect test paragraph, the scoring sheet, Whisper read-back, the -16 LUFS loudness target, the no-sign-up rule and the side-by-side presentation at CP8. Use for all narration research, samples and final voice tracks.
---
> **Document version:** skills/voiceover-tts/SKILL.md v1.2 | 31 Oct 2026 | Author: coordinator | Status: active

# Voice-over and TTS

Rule 12: open-source TTS run locally comes first; commercial TTS and a human narrator are fallbacks presented side by side at CP8. Rule 7: never sign up for, pay for, or send text or audio to any external service without Tariq's written approval; free tiers only after he agrees. Verify every candidate's current offering yourself; do not assert a capability from memory.

## Candidates to verify (record each in the licence register with the licence actually read)
Open, local: Coqui XTTS-v2 (CPML, non-commercial — test only), F5-TTS, Chatterbox / Chatterbox Multilingual (used in TrafficTwin's Arabic edition; watermark), Piper, Meta MMS-TTS (Arabic variants), Fish-Speech, OpenVoice, Kokoro-82M (English; TrafficTwin's English voice), and any Arabic or Saudi-dialect open models or fine-tunes on Hugging Face (search; record repo, revision, licence). Datasets for evaluation or fine-tuning only if licensed: Common Voice Arabic, MGB/QASR, SADA (Saudi audio dataset) — read the terms. Commercial fallbacks (listed, not used): ElevenLabs, Azure Neural `ar-SA`, Google, AWS Polly, regional Arabic providers — current voice names, dialect claims and prices with the date read. Human Saudi voice-over artist: cost and timeline range with sources (rate cards, marketplaces), no contact.

## Test protocol
1. One Saudi-dialect test paragraph (about 60 s when spoken) from the draft script, approved by the `documentary-director`, containing: a range with numbers, three place names (e.g. الجموم، الطائف، أبها), a date, one model-label sentence, one English acronym (SAR). Same paragraph for every candidate; `film/audio/tests/<candidate>/` holds the WAV, the config, the model revision, the seed and the elapsed time.
2. Also one English paragraph for the English cut candidates.
3. Whisper read-back: transcribe every sample with `mlx-whisper` or `faster-whisper` (model and revision recorded) and compute character error rate against the text; list every mispronounced place name and number.
4. Scoring sheet (`film/audio/tests/scores.csv`): candidate, licence, commercial_use, dialect_authenticity (1–5), naturalness (1–5), place_names (1–5), numbers (1–5), stability (artefacts, hallucinated words; 1–5), speed_x_realtime, memory_gb, CER_whisper, notes. Scores are the builder's judgement and are labelled as such; the native-speaker review overrides them.
5. Fine-tuning option: only with a properly licensed Saudi-dialect dataset, within the memory ceiling (`local-models`) or with approved GPU; write the plan, do not run it before CP8.

## Final narration
`uv run python -m film.voice speak --cut ar --lines film/script/lines.csv --candidate <id> --seed 1 --out film/audio/ar/` one WAV per line, then the timing table (seconds per line) for the editor; loudness normalised to -16 LUFS integrated, true peak ≤ -1.5 dBTP (`ffmpeg loudnorm`, two-pass; report measured values). Pauses capped and tempo adjusted only if the native reviewer accepts the result (TrafficTwin capped pauses at 0.3 s and used ×1.12 tempo; treat as a starting point, registered as an assumption).

## CP8 presentation (`film/audio/tests/README.md`)
A table with open candidates first, then commercial, then the human artist: licence, commercial use, cost, sample path, scores, CER, the recommendation with reasons, and the caveat in bold: **true dialect quality usually needs a human narrator, or at least native review**. Tariq chooses; nothing is rendered before that.

**Model policy (Tariq, 31 Oct 2026):** a paid state-of-the-art model or API may be used for Saudi-dialect Arabic script and narration (R10) and for Arabic–English translation of final deliverables (R8) where it materially improves quality — only after the one-paragraph request in `docs/STATUS.md` is approved, with one open-vs-paid A/B sample shown first, every call logged with vendor and model, no personal or partner data sent, and no API keys in the repo (see `CLAUDE.md` "Model policy" and the `local-models` skill).

## Paid candidates and the A/B (Tariq, 31 Oct 2026; model policy)
- **Candidates:** Nabrah AI (https://www.nabrah.ai/, Riyadh; Nabrah Studio TTS; public voices **Daniah, Norah, Abdullah**; TTS 1k characters = 400 credits; terms read 31 Oct 2026, S-nabrah-002: outputs owned by the user, public release and broadcast not addressed → **blocked for public release until Nabrah confirms in writing**), **ElevenLabs** (terms to read at R10), and the **best open voice** (Chatterbox or the best of the open list above).
- **Gate:** paid-model request 1 in `docs/STATUS.md` was **approved by Tariq on 31 Oct 2026** (cap USD 60 list for Nabrah + ElevenLabs together; alert at USD 48). Still required before the first call: the account and keys exist (set by Tariq), the terms rows in the licence register are current, and the A/B script is final. Keys come from the environment only (`NABRAH_API_KEY`, `ELEVENLABS_API_KEY`, set by Tariq); never in the repo or in logs.
- **Protocol:** the same 2-minute Saudi-dialect script (from `film/script/`, white/Najdi register A-film-001) for all three; same loudness normalisation (-16 LUFS); Whisper read-back for each. Score sheet `film/audio/tests/scores.csv` columns: candidate, voice, pronunciation of place names (1–5, with the list of mispronounced names), dialect naturalness (1–5), prosody (1–5), stability/artefacts, cost per finished minute (USD, from the vendor's credit rule or invoice), licence status for public release. Native-speaker review column left for Tariq's reviewer.
- **Logging:** every paid call → `uv run python -m common.cost_log add-paid --vendor nabrah|elevenlabs --model <voice/model> --usd <x> --step R10-voice-ab --approved-usd <cap>`; alert at 80 %.
- **Presentation:** all three samples (open, Nabrah, ElevenLabs) side by side in `film/audio/tests/README.md` with the score sheet and licence status, to Tariq, before any production narration is committed (CP8).
- **Consent rule (binding):** no voice cloning of any real person without their written consent on file; this test uses public/stock voices only.
