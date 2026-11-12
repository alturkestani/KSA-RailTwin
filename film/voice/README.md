> **Document version:** film/voice/README.md v1.3 | 7 Nov 2026 | Author: R10 builder (v1.3: ACCEPT_FIX_CP8_NOTES, ClArTTS clone rejected for use; v1.2: FIX_CP8_NOTES, Tariq's decision on Nabra-Saudi-82M and NAMAA; v1.1: source and disk-log paths); voice-audio (R10) | Status: draft (CP8)

# Voice and TTS comparison for CP8 (R10, half 1)

This is the side-by-side that the `voiceover-tts` skill asks for. Open candidates come first, then commercial ones, then a human narrator. Every licence, price and claim below was read on 7 Nov 2026 from the candidate's own page, model card or API. The source rows are `docs/sources/r10.csv` (S-r10-v01 to S-r10-v34) and the licence rows are `film/licences-r10.csv`. The samples are in `film/audio/tests/<candidate>/` (gitignored). Each sample has a `config.json` with the model, revision, seed, settings, elapsed seconds, peak RSS, WAV SHA-256, the Whisper transcript and the CER. Tariq chooses at CP8. Nothing has been rendered.

**True dialect quality usually needs a human narrator, or at least native review.** Every score below is the builder's judgement, and a native Saudi reviewer overrides them (CP9, `film/script/review-log.md`).

## What was and was not done

- **Paid A/B not run: no key set by Tariq; approved cap USD 60 (alert 48) unused, USD 0 spent.** The environment check `env | grep -c -E '^(NABRAH|ELEVENLABS)_API_KEY='` returned 0. No account was created, nothing was paid, and no text or audio was sent to any service.
- Coqui XTTS-v2 was covered by licence research only (CPML, non-commercial). It was not downloaded or run.
- Open models ran locally on CPU in throwaway venvs under `/tmp` (outside the repo), one model at a time. Nothing was added to the repo's `pyproject`. Disk use is logged in `film/voice/disk-log.md`.
- **Limit of these scores:** the builder cannot listen to audio. Naturalness is therefore "n/a (not auditioned)". Dialect authenticity, place names, numbers and stability are scored from the Whisper read-back, the G2P phoneme logs and signal measurements (retries, clipping, repeats, truncation). They are not an ear test, so treat them as a first screen for Tariq and the native reviewer.

## Test texts

- `film/audio/tests/ar.txt`: the Saudi-dialect paragraph exactly as given (written for the test, native review pending). It has 341 characters and 57 words. It contains four figures written as digits (0.42, 4.66, 2050, 3.47), seven place-name mentions (الرياض، جدة، الطايف، أبها، الجموم، جدة، القريات), the model-label sentence and the acronym SAR.
- `film/audio/tests/ar-words.txt`: a variant written by the builder, with the numbers in words and SAR as «سار» (native review pending). TrafficTwin found that Chatterbox misreads digits but reads number words correctly (TrafficTwin `docs/movies-arabic.md`, RA-001), so this variant separates pronunciation from digit handling.
- `film/audio/tests/en.txt`: the English paragraph exactly as given.
- The spoken lengths came out between 21 and 48 s, not the 60 s planned. The paragraph is shorter than a minute at narration pace.

## Method

- Read-back used Whisper large-v3-turbo (MLX conversion `mlx-community/whisper-large-v3-turbo` at revision a4aaeec0, mlx-whisper 0.4.3, MIT), with the language forced and temperature 0.
- CER is the character edit distance divided by the length of the reference, after normalising both texts. Normalisation strips diacritics, tatweel and punctuation, unifies أ/إ/آ→ا, ى→ي, ة→ه, ؤ→و and ئ→ي, and converts Arabic-Indic digits to Western ones.
- Whisper writes spoken numbers as digits, so CER also penalises number words. For that reason a second, number-free figure is shown: the **tail CER**, which covers «هذا طلب ...» to the end (the model label, six place names and SAR).
- Speed is audio seconds divided by wall-clock seconds, including model load, on CPU. Memory is the peak RSS (`/usr/bin/time -l` or `getrusage`).

## Comparison table

| # | candidate | licence (source) | commercial use | cost | sample | dialect / places / numbers / stability (1-5) | CER verbatim (tail) | CER words (tail) |
|---|---|---|---|---|---|---|---|---|
| **Open, run locally** | | | | | | | | |
| 1 | Chatterbox Multilingual V2, ClArTTS voice (TrafficTwin's Arabic voice) | MIT code+weights, Perth watermark (S-r10-v01, v02); voice clip CC-BY-4.0 (v17) || unresolved / not cleared without written consent; status: rejected for use (note A) | free; 0.12x realtime, 4.5 GB | `chatterbox-mtl-clartts/ar.wav` | 1 / 2 / 1 / 2 | 0.301 (0.036) | — |
| 2 | Chatterbox Multilingual V2, built-in voice | MIT (v01, v02) | Y | free; 0.24x, 4.3 GB | `chatterbox-mtl-builtin/ar.wav`, `ar-words.wav` | 2 / 4 / 1 (words: 3) / 3 | 0.165 (0.094) | 0.221 (0.078) |
| 3 | NAMAA-Saudi-TTS (Chatterbox fine-tune), built-in voice | MIT; training data not named (v11) | unclear (flag) | free; 0.22x, 4.5 GB | `namaa-saudi-builtin/ar.wav`, `ar-words.wav` | 2 / 3 / 1 (words: 2) / 2 | 0.211 (0.203) | 0.296 (0.141) |
| 4 | NAMAA-Saudi-TTS, ClArTTS voice | MIT + CC-BY-4.0 (v11, v17) | unresolved / not cleared without written consent; status: rejected for use (note A) | free; 0.18x, 5.0 GB | `namaa-saudi-clartts/ar.wav` | 1 / 2 / 1 / 2 | 0.183 (0.135) | — |
| 5 | Nabra-Saudi-82M (Kokoro/StyleTTS2 fine-tune, voice af_msa) | Apache-2.0; 146.5 h single-speaker Saudi corpus, source not named (v12) | unclear (flag) | free; 3.0x, 1.8 GB | `nabra-saudi-82m/ar.wav`, `ar-words.wav` | 3 / 3 / 2 (words: 3) / 3 | **0.074** (0.078) | 0.270 (0.141, includes a Whisper silence hallucination) |
| 6 | Meta MMS-TTS ara | CC-BY-NC-4.0 (v06) | **N: test only** | free; 5.1x, 1.3 GB | `mms-tts-ara/ar.wav`, `ar-words.wav` | 1 / 3 / 1 (words: 4) / 2 | 0.146 (0.141) | 0.236 (0.135) |
| 7 | Piper 1.8.0 + ar_JO-kareem-medium | engine GPL-3.0-or-later; voice MIT tag, dataset licence not stated (v04, v05) | unclear (flag) | free; 24x, 0.6 GB | `piper-ar_JO-kareem/ar.wav`, `ar-words.wav` | 1 / 4 / 4 / 3 | 0.078 (0.062) | 0.229 (0.042) |
| 8 | Kokoro-82M af_heart (English) | Apache-2.0 (v09) | Y | free; 1.5x, 3.3 GB | `kokoro-82m-af_heart/en.wav` | n/a / 4 / 5 / 5 | 0.0075 | — |
| 9 | Kokoro-82M am_michael (English) | Apache-2.0 (v09) | Y | free; 1.7x, 4.1 GB | `kokoro-82m-am_michael/en.wav` | n/a / 3 / 5 / 4 | 0.0176 | — |
| **Open, not run** | | | | | | | | |
| 10 | Chatterbox Multilingual V3 | MIT (v01) | Y | free | skipped: 3.2 GB of new weights (t3 v3 2.14 GB + s3gen v3 1.06 GB) would breach this task's 6 GB download cap; its loader is on GitHub master (PyPI 0.1.7 is the last release) | — | — | — |
| 11 | F5-TTS | code MIT, weights CC-BY-NC-4.0 (v03) | N | — | not run: non-commercial weights, no Arabic in the base model | — | — | — |
| 12 | Fish Audio S1-mini / S2-pro / Drama-3 | CC-BY-NC-SA-4.0 / Fish Audio Research License (v07) | N | — | not run: non-commercial; S1-mini gated | — | — | — |
| 13 | OpenVoice V2 | MIT (v08) | Y | — | not run: no native Arabic base speaker | — | — | — |
| 14 | Coqui XTTS-v2 | CPML 1.0.0, non-commercial for the model and its outputs (v10) | N | — | licence research only: never downloaded, never in the film | — | — | — |
| 15 | Habibi-TTS SAU, NAMAA-Saudi-TTS-V2, Saudi-tts-v4, Magpie-TTS-Saudi-Arabic, voho-saudi-speak, OmniVoice-Najdi | CC-BY-NC(-SA)-4.0; several inherit SADA's terms (v13, v14) | N | — | not run: non-commercial | — | — | — |
| 16 | Fasee7-Najdi-Small, aszfezf/saudi-arabic-tts, AhmedEladl/saudi-tts | Apache-2.0 / MIT / Apache-2.0; training data not named (v13) | unclear | — | skipped: disk cap (VoxCPM2 base ~5 GB; 4.2 GB; 5.6 GB) | — | — | — |
| 17 | Magpie-Saqr-Najdi | NVIDIA Open Model License, gated (manual) (v13) | unclear | — | not run: gated (account needed, rule 7); trained on SADA-derived speakers | — | — | — |
| **Commercial (listed, not used)** | | | | | | | | |
| 18 | **Nabrah Studio** (Riyadh), public voices Daniah, Norah, Abdullah | proprietary; terms S-nabrah-002 | **Y for public voices on a paid plan**, cleared in writing by Nabrah.ai on 1 Nov 2026 (S-nabrah-005) | 400 credits per 1,000 chars; free trial 7,000 credits; Individual 45, Basic 100, Starter 225, Pro 400, Scale 850 SAR/month (v18). About 170-303 credits per finished minute (computed from these samples' 425-758 chars/min), so Basic covers about 430-760 finished minutes | not run: no `NABRAH_API_KEY` | — | — | — |
| 19 | ElevenLabs (Arabic in v4, v3, Multilingual v2 "Arabic (Saudi Arabia, UAE)", Flash v2.5) | proprietary; Terms of Use last updated 9 Oct 2026 (v19-v22) | Y on paid plans (§1(c)(ii)); N on Free (§1(c)(i)); user keeps rights in Output (§4(c)(ii)); training opt-out (§4(i)) | Starter USD 6/month (USD 1 first month), Creator USD 22, Pro USD 99; API USD 0.08 per 1,000 chars (multilingual), so about USD 0.03-0.06 per finished minute (computed) | not run: no `ELEVENLABS_API_KEY` | — | — | — |
| 20 | Azure Neural ar-SA: HamedNeural, ZariyahNeural | proprietary (v23, v24) | unclear (product terms not read) | USD 15 per 1M chars (S1, East US); 0.5M chars/month free (F0) | not used (rule 7) | — | — | — |
| 21 | Google Cloud TTS (Arabic = ar-XA only; no Saudi locale) | proprietary (v25, v26) | unclear (terms not read) | Chirp 3: HD USD 30, Neural2 USD 16, Standard USD 4 per 1M chars | not used | — | — | — |
| 22 | AWS Polly: Zeina (arb, standard), Hala and Zayd (ar-AE Gulf, neural); no ar-SA | proprietary (v27, v28) | unclear (terms not read) | Neural USD 16, Standard USD 4 per 1M chars | not used | — | — | — |
| 23 | Orpheus Arabic Saudi (Canopy Labs, hosted on Groq): Abdullah, Fahad, Sultan, Lulwa, Noura, Aisha | proprietary hosted; no terms on the page; weights not public (v29) | unclear | USD 40 per 1M chars; preview | not used | — | — | — |
| **Human** | | | | | | | | |
| 24 | Native Saudi voice-over artist (marketplace or studio) | per contract (usage and broadcast rights in writing) | Y if contracted | USD 0.10-0.25 per word for e-learning and long-form (VoiceBros, v30), so about USD 7-32 per finished minute or USD 70-320 per 10-minute cut at the measured 71-127 words/min (computed); a Saudi-accent profile on Voicecrafters starts at USD 75 per job (v31); standard delivery 24 h on VoiceBros. Fiverr, Voices.com and the GVAA guide could not be read (403 or sign-up gate) | not contacted (rule 7) | — | — | — |

**Note A (Tariq, 7 Nov 2026, ACCEPT_FIX_CP8_NOTES).** Rows 1 and 4 clone the voice of the ClArTTS clip ch_02_arabic_tts_dataset_417, a real LibriVox reader. Commercial use: unresolved / not cleared without written consent. Status: rejected for use: cloning it breaks the no-cloning rule; not cleared without that reader's written consent. The CC-BY-4.0 dataset licence does not clear voice cloning. The scores stay for the record only; the open fallback is the built-in Chatterbox voice (row 2).

The scores are builder judgement on a 1-5 scale. Full notes are in `film/voice/scores.csv`. Cost-per-minute figures are computations from list prices and the measured characters or words per minute of these samples. They are estimates, not quotes.

## What the samples showed

- **Digits break every open model except Piper.** Reading the verbatim paragraph:
  - Chatterbox heard «40404040» and «4080».
  - NAMAA heard «22», «64» and «20 و 20».
  - Nabra dropped the decimal point («سفر 42», «64», «43»).
  - MMS skipped the digits silently. This is the most dangerous failure for a figures film.
  - Only Piper returned 0.42, 4.66 and 3.47 exactly.

  With the numbers in words, Chatterbox got 3 of 4 right (3.47 heard 3.7), Nabra 3 of 4, MMS 4 of 4 and Piper 4 of 4. The production lines therefore need a separate spoken (`say`) text with numbers in words, as in TrafficTwin. The numbers must also be checked by ear and by read-back, line by line.
- **Repeats and hallucinated words:**
  - Chatterbox with the ClArTTS voice repeated a phrase and needed 5 clause retries.
  - NAMAA repeated «السعودية» with both voices.
  - The ClArTTS voice, which is the MSA reader that gave TrafficTwin 0 % CER on vowelised MSA, did badly on unvowelised dialect text: «بلياض» for الرياض and «أبهة» for أبها. Its number-free tail was nevertheless the cleanest of all (0.036).
- **Dialect signals (transcript evidence only):**
  - Nabra-Saudi-82M's read-back writes ق as ك in «متوكع» and «الكريات». This is consistent with the Saudi g-realisation of qaf, which only an ear can confirm. Nabra had the lowest verbatim CER (0.074).
  - Its G2P drops Latin words, so «(SAR)» disappears, and one pass truncates after about 510 phonemes, so it must be fed sentence by sentence.
  - NAMAA's dialect fine-tune showed no dialect signal in the read-back, and it was less stable than its Chatterbox base.
- **SAR:** Chatterbox with the built-in voice read it as «سار» (correct). The ClArTTS voice swallowed it, NAMAA said «صار», Piper said «وسئية», and Nabra and MMS dropped it. The script should write the acronym the way it is to be spoken (for example «سار») in the spoken text.
- **English (Kokoro):** both voices read every figure right. The place names need help: af_heart was heard as «Al-Jumim» and «Quraayat», and am_michael as «Abhaf» and «Quraia». Respellings in the spoken text (for example "Al-Joomoom", "Qurayyat") should be checked by ear.
- **Signal:**
  - Chatterbox and Piper clip (peak at or above 1.0). Final narration would need gain staging before the two-pass loudnorm to -16 LUFS.
  - Piper outputs 22.05 kHz and MMS 16 kHz, both below the 24 kHz of the others.
  - Chatterbox on CPU is slow (0.12-0.24x realtime), so a 10-minute cut is about 40-80 minutes of compute on this Mac (computed).

## Recommendation (builder's, for Tariq at CP8; not a decision)

1. **Arabic cuts: Nabrah Studio public voices, provided that** Tariq sets `NABRAH_API_KEY` and the approved A/B (cap USD 60, alert 48) is run on the same paragraph and on the 2-minute script, and a native Saudi reviewer prefers it. Reasons:
   - It is the only option with written commercial, online and broadcast clearance for a Saudi-dialect voice (S-nabrah-005).
   - Its three public voices match the three-voice plan in R10_LAUNCH.
   - Nabrah states the product is "purpose-built for the Saudi dialect" (S-nabrah-004). That is the vendor's claim, which the A/B must test.
   - Its list cost is small: one Basic month at 100 SAR covers about 430-760 finished minutes (computed).

   Published Nabrah audio must carry the Nabrah attribution (Tariq, 7 Nov 2026).
2. **Open fallback with a clean licence: Chatterbox Multilingual V2 (MIT)** with the built-in voice. Feed it the spoken text with numbers in words and «سار», clause by clause with retries, check every line with Whisper read-back, and have a native reviewer approve it. It is clean on licence and offline, and it read the place names well (places 4/5). It is MSA-leaning, slow on CPU, and watermarked (Perth).
3. **Allowed open options (decision, Tariq, 7 Nov 2026): Nabra-Saudi-82M and NAMAA-Saudi-TTS.** The hold "keep them out until the training data is named" is lifted: Tariq accepts both under their published licences (Apache-2.0 / MIT) even though the training corpus is unnamed. They are allowed options, not automatic replacements: Nabrah's public voices (Daniah, Norah, Abdullah) stay first choice for Arabic and Chatterbox stays the clean-licence fallback (clean on its licence; this does not claim exhaustive training-data provenance for Chatterbox, whose card does not name its data). The no-cloning rule stands: no model that clones a real identifiable person without written consent (the ClArTTS-reference clone variant is flagged in the rights log). Nothing was downloaded and no audio generated for this decision. The original assessment follows. **Nabra-Saudi-82M:** It gave the best verbatim CER and is the only sample showing a dialect feature in the read-back, and it is small and fast. Its Apache-2.0 licence is clean, but the 146.5 h training corpus is not named, and if it were SADA-derived it would carry CC BY-NC-SA. The same flag applies to NAMAA-Saudi-TTS. Both stay "commercial use: unclear" until the authors confirm the data source in writing. Contacting them is Tariq's step (rule 7).
4. **Not recommended:**
   - MMS-TTS: non-commercial, and it skips digits.
   - Piper kareem: Jordanian rather than Saudi, robotic, clips, and its data licence is unstated. Its digit handling is the best, but that is not enough.
   - XTTS-v2, F5-TTS, Fish Audio and the NC Saudi fine-tunes: non-commercial licences.
5. **English cut: Kokoro-82M af_heart** (Apache-2.0, CER 0.0075, TrafficTwin's English voice), with respelled place names in the spoken text and a listen-check.
6. **Human narrator** for the highest dialect quality, or if the Nabrah A/B disappoints: about USD 70-320 per 10-minute cut at the published marketplace per-word rates (computed), plus written usage and broadcast rights. This is a cost range, not a quote.

## Licence flags (not resolved here)

- MMS-TTS ara: CC-BY-NC-4.0, test only.
- XTTS-v2: CPML, non-commercial for the model and its outputs (the CPML caveat).
- F5-TTS weights and Fish Audio: non-commercial.
- SADA: CC BY-NC-SA 4.0. Habibi-TTS SAU and several Saudi fine-tunes inherit non-commercial terms from it.
- NAMAA-Saudi-TTS, Nabra-Saudi-82M, Fasee7-Najdi-Small, aszfezf/saudi-arabic-tts and AhmedEladl/saudi-tts: permissive licence tags, but the training data is not named, so commercial use is unclear.
- Piper ar_JO-kareem: dataset licence "See URL", and the dataset repo has no licence.
- Chatterbox: Perth watermark in every output (disclose it in the credits). The ClArTTS reference clip is rejected for use (note A), so no clone of it appears in the film.
- ElevenLabs: commercial use only on paid plans. Azure, Google, AWS and Groq: service terms not read in this pass.
- Nabrah: cleared in writing (1 Nov 2026) for its public voices on a paid plan; attribute Nabrah on published audio. Training opt-out is Enterprise-only. No voice cloning of a real person without written consent.

## Fine-tuning option (proposal only; not executed; needs Tariq's approval, disk and possibly GPU)

- **Data licences:**
  - SADA (about 667 h, mostly Saudi dialects) is CC BY-NC-SA 4.0 (S-r10-v32), so any voice trained on it would be non-commercial and share-alike. It suits only a strictly non-commercial release, and only if Tariq accepts that.
  - Common Voice Arabic is CC0 according to the Mozilla Data Collective listing (secondary, S-r10-v33). It is crowd-read and mostly MSA with many speakers, which is poor material for a single narrator voice. It is fine for read-back evaluation.
  - MGB-2 and QASR licences could not be verified (S-r10-v34).
- **Cleanest route:** commission 2-5 hours of studio recordings from a native Saudi narrator under a contract that grants training and synthetic-voice rights. Then fine-tune a permissive base: the Kokoro/StyleTTS2 class (Apache-2.0, 82M, the Nabra recipe) or the Chatterbox T3 (MIT, 0.5B). Labelled estimate:
  - Recording is about 4,300-7,600 words per hour of speech at 71-127 words/min, so about USD 430-1,900 per recorded hour at USD 0.10-0.25 per word (computed). A training-rights premium comes on top and has no sourced figure.
  - Compute: an 82M fine-tune may fit the M3 Pro (time unmeasured). A 0.5B T3 fine-tune probably needs a GPU, which requires Tariq's approval (rule 7).
  - Disk: tens of GB for audio and checkpoints (unmeasured). This is against the R10 gate of 50 GiB free.
- **Not before CP8.** The Nabrah A/B and a human narrator are faster and cheaper ways to answer the dialect question.

## Files

- `film/voice/README.md` (this file) and `film/voice/scores.csv` (tracked). Copies are in `film/audio/tests/README.md` and `film/audio/tests/scores.csv`, the skill path, which is gitignored.
- `film/licences-r10.csv`: one row per model, voice, dataset and service assessed, with the columns of `docs/licences.csv`.
- `docs/sources/r10.csv`: source rows S-r10-v01 to S-r10-v34, accessed 2026-11-07 (AST).
- `film/voice/disk-log.md`: disk before and after each download.
- `film/audio/tests/<candidate>/{ar.wav, ar-words.wav, en.wav, config.json}`, plus `ar.txt`, `ar-words.txt` and `en.txt` (gitignored).
