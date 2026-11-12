> **Document version:** docs/film.md v1.11 | 12 Nov 2026 | Author: PUBLISH_EXPORT (v1.11: publication order, Tariq's answer Q9); R10 builder (v1.10: FIX_TRAILER_AR, Arabic trailer t-08 re-voiced in plain words, Arabic trailer credits without ElevenLabs, inflected-jargon test, §00000000; v1.9: CLOSE_R10, CP9 accepted, trailer NPV wording replaced, social deliverables, credits check, §0000000; v1.8: FIX_MBS_TITLE, m-03-03 / sh-03-02 name His Royal Highness Crown Prince Mohammed bin Salman in full, §000000; v1.7: FIX_MBS_QUOTE, the Crown Prince population line m-03-03 / sh-03-02 now states only what a Saudi source confirms, §00000; v1.6: FIX_FILM_STORY, north/south sequence on the S6-L6 comparison layout and plain benefit-to-cost wording in both main cuts, §0000; v1.5: BUILD_MOVIE_EN, English main cut and English trailer on the ElevenLabs Creator plan, §000; v1.4: BUILD_MOVIE, Arabic main cut rebuilt in the trailer style, §00; v1.3: verifier pass, final trailer hashes; v1.2: FIX_HALF2_QUALITY, new trailers, §0; v1.1: R10_HALF2 verifier fixes F1 credits card, F2 Chrome QA, minor corrections) | Status: reviewed (CP9 accepted by Tariq on 11 Nov 2026; nothing published)

# The documentary film: half-2 outputs (R10_HALF2)

Research film, not a promo and not a film of any ministry, SAR or PIF. Since FIX_HALF2_QUALITY (§0) the notice "synthetic demand, uncalibrated: scenario comparison, not a forecast" appears once, on the last slide and in the credits; §§1–4 below describe the R10_HALF2 state (card renderer, per-shot footers) and are kept for the record: where they differ, §0 governs. This is a **draft for CP9**: the Arabic narration has had no native review, and nothing is published.


## 000000000. PUBLISH_EXPORT (12 Nov 2026): publication order (Tariq's answer Q9)

**Code published; native Saudi review of the Arabic pending; films follow the review.** The repository (code, study documents, film scripts, storyboard and subtitles) is released as version 1.0.0. The films (Arabic and English main cuts, both trailers, social copies) are **not** published until the native Saudi review of the Arabic is done (§8: `native_review = pending` on every Arabic row). The review covers the Arabic narration, `film/voice/say.csv` and the subtitles; any change it brings is re-voiced and re-cut before the films are published. Audio and video stay out of the repository either way (rule 8); Nabrah attribution goes with any published audio.

## 00000000. FIX_TRAILER_AR (12 Nov 2026): Arabic trailer t-08 in plain words, Arabic trailer credits

`prompts/FIX_TRAILER_AR.md` (Tariq, 12 Nov 2026; a post-close fix, R10 stays done). Where earlier sections differ, this section governs. It closes the "Residual, open for Tariq" item of §0000000.

**1. Line t-08 (Arabic trailer).** Before: «خيار المحطات الثلاث يبقى صافي قيمته الحالية موجب حتى مع التكلفة المرتفعة: بين 4.0 و5.6 مليار ريال.» After: «خيار المحطات الثلاث يرجّع تكلفته حتى لو ارتفعت: المنافع تزيد على التكاليف بين 4.0 و5.6 مليار ريال.»
- The wording is the main cut's own: m-08-02 «وحتى لو ارتفعت التكلفة، تظل ترجّع تكلفتها» and the sh-08-51 caption «المنافع تزيد على التكاليف بين 4.0 و5.6 مليار ريال». Figures (4.0; 5.6) and source (`run:runs/r6/top5/top5.csv`, NPV at P90 cost 3,986 / 5,589 SAR m for the low / high population cases) are unchanged.
- "About 6 riyals back per riyal" (BCR P50 5.96, S-r10-056, `rounding-log.csv` m-08-02) stays on screen in the sh-08-51 caption at the same moment. It is not spoken, because the Arabic and English t-08 must carry identical figures (`film.script validate`) and the English trailer had to stay byte-identical.
- A first, longer draft that also spoke the "about 6 riyals" phrase was voiced (14.4 s; USD 0.02). It would have made the trailer 91.7 s, over the 90 s trailer ceiling, so it was replaced before assembly. The final line is 12.0 s and the trailer is 89.3 s.
- Full tashkeel in `speech_text` (bare: «مليار», digits). `native_review = pending`. Logged in `film/storyboard/story-edits.csv` and `ar-rewords.csv`.
- Re-voiced with Nabrah, voice Daniah (the section-8 role voice, as before). Read-back with local whisper-large-v3-turbo (offline): CER 0.032. Whisper writes the figures as "بين 4.05.6"; it glues the digit groups together. Prompted for number words, it returns «بين أربعة فاصلة صفر وخمسة فاصلة ستة مليار ريال» twice, including once with a prompt deliberately biased toward the wrong figures (3.0 / 7.4). So the audio says 4.0 and 5.6. The other 10 lines' read-back is unchanged.

**2. Arabic trailer credits** (`film/sim.py` `closing_credits("ar")`, sh-08-54). The line «التعليق الصوتي: ElevenLabs voice George (English)» is removed: no ElevenLabs audio is in this cut. The card now reads «التعليق الصوتي: أصوات نبرة العامة دانية ونورة وعبدالله (العربية)», followed by the OSM, GASTAT and Copernicus credits and the research-film line. The single closing notice «طلب تركيبي غير مُعايَر: مقارنة سيناريوهات، ليست توقعاً.» stays (frame checked). The English trailer credits are unchanged.

**3. Re-assembly.** sh-08-51 (13.4 s, was 11.0 s) and sh-08-54 were re-rendered in Arabic only. The edit list moved the three following shots by 2.4 s. Subtitles were rebuilt (16 cues; `film.subs check` PASS, `align-qa` PASS with the earlier t-07 warning). The social `.subs.mp4` was burned again and `trailer.ar.pdf` re-rendered (`common.ar_render`).

| file | duration | loudness | SHA-256 |
|---|---|---|---|
| `out/ksa-rail-twin-trailer-ar.mp4` | 89.3 s (1:29.3) | −16.07 LUFS / −1.84 dBTP | 64cf4389fb8d36895e4024628540a64227bfb25fa1ba79bccf7014f77e2f8ef1 |
| `out/social/ksa-rail-twin-trailer-ar.subs.mp4` | 89.3 s, 28.8 MiB | audio copied | 68087af6b8a73dc27330609131495f6c259d35025110a78f55042d70beda634c |
| `out/social/ksa-rail-twin-trailer-ar.subs.srt` (= `film/subs/trailer.ar.srt`) | 16 cues | | 3d85fc35ffe50d10c09e06e45df42d06ee80702fb76f52d937dc37686a84e7bf |
| `out/script/trailer.ar.pdf` | | | 0dbae5ec1c67b90b78fe8298005d0e4d1912034ba7e6dfeeb8cf8f6aed6acadc |

- Previous trailer-ar: ee3f81d42ec299b1… (86.9 s). The previous MP4, social files, the two shots and the PDF are in `renders/_superseded/*.pre-fix-trailer-ar-20261112.*`.
- **Unchanged, checked by SHA-256 before and after:** main-en 540c5e41…, main-ar 391f72bf…, trailer-en 78802cd5…, their social copies (plain, `.subs.mp4`, SRTs), both covers, the other three PDFs, and every other trailer shot.
- Of the narration WAVs, only `trailer-ar/t-08.wav` changed (plus two new raw-cache files under `raw/nabrah/trailer-ar/`).

**4. Barred-jargon test** (`tests/test_film_jargon.py`). It checks the inflected Arabic forms (any «صافي … قيم…», «القيمة/قيمته/بقيمتها الحالية», «موجب/سالب» in any inflection; «بموجب» allowed) and English "NPV", "net present value" and "present value". It does this tashkeel-insensitively across these public outputs:
- the script Markdown, `lines.csv` text and `speech_text`, and `say.csv`;
- the subtitle files, shot captions and source captions;
- both credit lists;
- local ASR transcripts of the four final cuts' audio: `film/voice/readback/final-{main,trailer}-{en,ar}.txt` (`scripts/film_final_asr.py`, whisper-large-v3-turbo, local, offline). Each transcript records its MP4's SHA-256, and a test checks it against the file.

With the external volume present, it also checks the social SRTs and the script PDFs (pdftotext). The only allow-listed text is the single closing notice. Result: no hits.
- Not caught by design: the English trailer t-08 says "stays positive even at high cost". "Positive" is the finance sense, but the prompt kept trailer-en byte-identical and listed only Arabic «موجب/سالب», so it is left for Tariq.

**Paid TTS.** This run: Nabrah USD 0.03 (two calls: 0.02 and 0.01; limit 0.05); ElevenLabs 0. Combined total 7.06 → **7.09** of the USD 60 cap.

## 0000000. CLOSE_R10 (12 Nov 2026): CP9 accepted, trailer wording, social files

`prompts/CLOSE_R10.md` (Tariq, 11 Nov 2026, 22:34 AST). **Tariq's CP9 verdict: accepted.** The main cuts keep their current lengths (en 14:32, ar 16:49). Tariq waived the CP8 target of 8 to 12 minutes. Where earlier sections differ, this section governs.

**Main cuts unchanged** (byte-identical to 97d5deb): en 540c5e41094ed2ce7f2d71be8ed3a44ce89407e38059ccc7eba378c31ada150e (872.2 s), ar 391f72bfcedf94d65ace316e2c65bfa73759c93398a80fed36f962fd3a5751bf (1008.8 s).

**1. Trailer wording (no new audio).**
- sh-08-51, on-screen caption: "Net present value at high cost: 4.0 to 5.6 billion SAR" became "About 6 riyals back per riyal spent in the middle case; even at high cost, benefits exceed costs by 4.0 to 5.6 billion SAR (2025 prices, 60 years)". The Arabic caption changed the same way. The new wording uses the main cuts' benefit-to-cost wording (sh-08-02, m-08-02): `S-r10-056`, `runs/r6/top5/top5.csv` (`bcr_p50_medium` 5.96; `npv_p90cost_low` / `_high` 3,986 / 5,589 million SAR).
- sh-07-51: the visual description changed. The on-screen axis label "↑ robust net present value" (Arabic «↑ صافي القيمة الحالية الصامد») also changed, to "↑ benefits minus costs (worst population case)" (Arabic «↑ المنافع ناقص التكاليف (أسوأ حالة للسكان)»). This is the main cut's label for the same quantity (sh-07-04; robust NPV = the worst of the three population cases, `docs/r6-topology.md` §0). The prompt named only the sh-07-51 description and asked for one re-render. The label, however, is on-screen text in a public output, so sh-07-51 was re-rendered too. Decision recorded in `docs/status/r10.md`.
- Both shots were re-rendered in both languages. Both trailers were re-assembled. Their audio and subtitle streams are bit-identical to the previous trailers (stream MD5 compared). All 160 narration WAVs are hash-identical (`main`/`trailer` × `en`/`ar`). ElevenLabs and Nabrah spend for this run: 0. The edits are logged in `film/storyboard/caption-edits.csv`. The previous files are in `renders/_superseded/*.pre-close-r10-20261112.mp4`.
- New trailers: en 78802cd553486ad249dcf2fef97aa1cd61f3ecfe69552e125195858c7ca38d30 (77.6 s; −16.22 LUFS / −1.87 dBTP), ar ee3f81d42ec299b133460f0ddad39f6a31941ad2bfa87addeab21f96a41961c4 (86.9 s; −16.06 LUFS / −1.88 dBTP). The loudness values are unchanged from the previous trailers.
- **Residual, open for Tariq.** The Arabic trailer narration line t-08 (audio, its subtitles and the trailer script PDF) still says «خيار المحطات الثلاث يبقى **صافي قيمته الحالية** موجب حتى مع التكلفة المرتفعة: بين 4.0 و5.6 مليار ريال». This is the inflected form of the term. The exact strings in the prompt ("NPV", "net present value", «صافي القيمة الحالية», «سالب») do not occur in any public output. The term itself does occur, and removing it needs a re-voice of t-08 (ar), which this prompt forbids (no new audio). The English t-08 ("stays positive even at high cost") does not use the term.

**2. Social deliverables** (`film/renders/out/social/`, made by `uv run python -m film.social burn|plain|cover|manifest`; manifest in `film/assemble/social.csv`).
- This ffmpeg build has no libass. Each subtitle cue is drawn by headless Chrome with the film's Noto fonts, which shape Arabic correctly in right-to-left order. The PNGs are overlaid through ffmpeg's concat demuxer as a top-centre band, because the bottom of each shot holds the caption and the map credits. The band is 34 px text, at most 800 px wide (x 560–1360), so it stays between the three-layer legend and the "composite journey" pill in the top corners. The first build (40 px, up to 1,240 px wide) could cover the pill; the verifier noted this, and the files were rebuilt.
- The burned versions are 1920×1080 at 30 fps, libx264 CRF 18, with the cut's AAC audio copied unchanged. Loudness is therefore the cut's own, and the audio-stream MD5 is identical. The soft subtitle track is dropped (`-sn`) so that subtitles do not show twice.
- The plain main cuts are byte-identical copies. The SRTs are byte-identical to `film/subs/*.srt`, which are built from `lines.csv`.

| file | duration | MiB | SHA-256 | flag |
|---|---|---|---|---|
| ksa-rail-twin-main-en.mp4 (plain) | 14:32.167 | 246.5 | 540c5e41094ed2ce7f2d71be8ed3a44ce89407e38059ccc7eba378c31ada150e | |
| ksa-rail-twin-main-en.subs.mp4 | 14:32.167 | 219.2 | 1e4a0b30499312659e25af6e3061e3f16a668f345df2d7a4b7a0488fe4b77126 | |
| ksa-rail-twin-main-ar.mp4 (plain) | 16:48.833 | 269.8 | 391f72bfcedf94d65ace316e2c65bfa73759c93398a80fed36f962fd3a5751bf | **over 15:00 (LinkedIn limit)** |
| ksa-rail-twin-main-ar.subs.mp4 | 16:48.833 | 240.7 | db245990ea68cc216a6cd357e58e1f38c1e47f8d0cc8bea105a89877c347446b | **over 15:00 (LinkedIn limit)** |
| ksa-rail-twin-trailer-en.subs.mp4 | 1:17.600 | 25.9 | e3e0aa38979021636f9798099983fb492e46b3817f4780862b1b755c31cf0d64 | |
| ksa-rail-twin-trailer-ar.subs.mp4 | 1:26.900 | 28.4 | 5fb4b818ed257f1a3f90acec6407a8d8a845228948209fb3700475a269fb7979 | |
| ksa-rail-twin-main-en.srt / .subs.srt | | 0.0 | 1788803e441f6972291d89d291cc93a8d738087fca099535cfdfc8b6d3108279 | |
| ksa-rail-twin-main-ar.srt / .subs.srt | | 0.0 | 4ca03cbea71541dbb3674aa5c068de83daf566d2e12579cce655e4219ce2d4b9 | |
| ksa-rail-twin-trailer-en.subs.srt | | 0.0 | 1a26492ec70490f8d7128596bde6b11e0b7d8697ba659ad43e35616ece705ca6 | |
| ksa-rail-twin-trailer-ar.subs.srt | | 0.0 | 7410f0f78a19403835ee90b19b1d5d6a7123eadbb6b901e7023787e7db917738 | |
| ksa-rail-twin-cover-en.png | | 0.5 | da45219dfdae1ece762fba2a7c6f19b719751d1d8f9d3b7aca7653cdfe220c1a | |
| ksa-rail-twin-cover-ar.png | | 0.5 | 0b555bdec8b7000d0738e3de08d236594091be128824779caf676e4253080c1a | |

- No file is over 512 MB. As the prompt expected, the Arabic main cut (both versions) is over 15:00. It is flagged and was not cut.
- Covers: one frame of the census shot sh-03-01 (population dots over the rail layers; en 204.8 s, ar 225.2 s). Over the frame's caption band sit the film title, "An independent simulation study · " plus the standard synthetic label, and "Population: GASTAT, Census 2022 (derived)". The frame's own OSM and Copernicus credit lines are kept.

- The stale `md → html` intermediates of the script PDFs (`renders/out/script/{main,trailer}.{en,ar}.html`, 8–10 Nov) still carried the pre-FIX_FILM_STORY wording ("net present value", «سالب»). They were moved to `renders/_superseded/script-*.stale-intermediate-pre-close-r10-20261112.html` (VERIFY_CLOSE_R10 pass 1, F1). `renders/out/script/` now holds only the four PDFs, which were re-rendered on 11 Nov.

**3. Credits and end card** (frames read from the four final files):
- main-en credits roll: "Voices: ElevenLabs voice George (English); Nabrah public voices Daniah, Norah, Abdullah (Arabic)". The closing notice "Synthetic demand, uncalibrated: a scenario comparison, not a forecast." follows "KSA Rail Twin: a research film, not an official film of any ministry or company".
- main-ar credits roll: «الأصوات: نبرة (الأصوات العامة دانية ونورة وعبدالله)», with the same notice in Arabic and «فيلم بحثي، مو فيلم رسمي لأي وزارة أو شركة». **There is no ElevenLabs credit on main-ar.** This is by design (FIX_FILM_STORY, Tariq 10 Nov 2026: George does not speak in the Arabic cut; all 68 lines are Nabrah, `film/voice/timing/main-ar.csv`), and ElevenLabs' terms require no attribution (`film/rights_log.csv`). The main cuts must stay byte-identical, so this was reported, not changed.
- trailer-en and trailer-ar end cards: "Narration: ElevenLabs voice George (English); Nabrah public voices Daniah, Norah and Abdullah (Arabic)", in Arabic on the Arabic trailer. Each card also has the closing notice and the research-film line. (The Arabic trailer also credits George, who does not speak in it: an over-credit, left as is.)
- The single closing disclaimer is present once on every cut. Its wording is the project's: "research film, not an official film of any ministry or company" plus "synthetic demand, uncalibrated". It does not use the prompt's paraphrase "independent simulation … not a government plan".

**4. Spend.** See `docs/spend-summary.md` (recomputed from the cost logs).


## 000000. FIX_MBS_TITLE (11 Nov 2026): the Crown Prince named with his full honorific

`prompts/FIX_MBS_TITLE.md` (Tariq, 11 Nov 2026). Where §00000 and earlier differ, this section governs for the two main cuts. **The trailers are untouched** (full SHA-256 before and after: en 81fa64ec4dd12f3b06150f3c0cae9e7a78bf2caceaa7a611f1c0c50b71cc8701, ar 21df620d1994ec759d539349eab5b5f85dde95ae449191633a1eb98d2504407e: OK).

| deliverable | path (through `film/renders`) | duration | size | SHA-256 (first 16) | loudness (two-pass; measured again on the MP4 with ffmpeg loudnorm) |
|---|---|---|---|---|---|
| main cut, English | `out/ksa-rail-twin-main-en.mp4` | 872.2 s (14:32) | 258.4 MB | 540c5e41094ed2ce (was 06b6b3327b551eee) | −16.09 LUFS, −1.83 dBTP (narration master −16.08 / −1.89) |
| main cut, Arabic | `out/ksa-rail-twin-main-ar.mp4` | 1008.8 s (16:49) | 282.9 MB | 391f72bfcedf94d6 (was 4cae0dfe950bed28) | −16.03 LUFS, −1.77 dBTP (narration master −16.03 / −1.90) |

H.264 1920×1080 30 fps, AAC 48 kHz (`eng` / `ara`), one `mov_text` subtitle track; `ffprobe` 11 Nov 2026 (872.166667 s / 1008.833333 s). Full SHA-256: en 540c5e41094ed2ce7f2d71be8ed3a44ce89407e38059ccc7eba378c31ada150e, ar 391f72bfcedf94d65ace316e2c65bfa73759c93398a80fed36f962fd3a5751bf. The previous cuts, the old sh-03-02 shots and the old script PDFs are kept as `renders/_superseded/*.pre-fix-mbs-title-20261111.*`; the assembler wrote `.new.mp4` first and renamed. Script PDFs `out/script/main.{en,ar}.pdf` re-rendered (`common.ar_render`).

**What changed.** Only line m-03-03 (both languages) and its shot sh-03-02; grep before editing (main and trailer scripts, `lines.csv`, captions, subtitle files, script PDFs) found no other mention of the title:
- English: "After The Line launch in July 2022, His Royal Highness Crown Prince Mohammed bin Salman told journalists the aim is 50 to 60 million people in the Kingdom by 2030, about half Saudis. Remarks, not a published programme target."
- Arabic (Tariq's suggested line, verbatim): «وبعد إطلاق تصاميم ذا لاين في يوليو 2022، قال صاحب السمو الملكي الأمير محمد بن سلمان، ولي العهد، للصحفيين إن الهدف إن عدد سكان المملكة يوصل بين 50 و60 مليون بحلول 2030، ونصهم تقريباً سعوديين. وهذي تصريحات، مو هدف منشور في برنامج رسمي.» Full tashkeel in `speech_text`, including «صَاحِبُ السُّمُوِّ الْمَلَكِيِّ الْأَمِيرُ مُحَمَّدُ بْنُ سَلْمَانَ، وَلِيُّ الْعَهْدِ،» (bare مليون and digits); `native_review = pending`; `ar-rewords.csv`.
- Caption sh-03-02 (both languages): the same full title; nothing else had to be shortened (frames checked: the side caption fits, title complete). `caption-edits.csv`, `story-edits.csv`.
- Figures (2022; 50; 60; 2030), sources (S-r10-057, S-r10-058, S-r10-025) and the qualifier unchanged.
- No bare «ولي العهد» or "the Crown Prince" without the name remains in the main script, captions, subtitle files or the embedded subtitle tracks (`tests/test_film_mbs_title.py`; embedded tracks extracted with ffmpeg 11 Nov 2026).

**Narration.** Only m-03-03 re-voiced (`--only m-03-03 --no-fallback`): English ElevenLabs George (`eleven_multilingual_v2`, 225 characters, USD 0.05), 15.418 s (was 13.607); Arabic Nabrah Abdullah (same section-3 role voice, 353 characters, USD 0.03), 20.840 s (was 17.320). Every other narration WAV is byte-identical (SHA-256 of all 160 files in the four narration folders before and after; only `main-en/m-03-03.wav` and `main-ar/m-03-03.wav` differ). Read-back (mlx-community/whisper-large-v3-turbo, local, offline): en CER 0.000, ar CER 0.009. Honorific check: every token of «صاحب السمو الملكي الأمير محمد بن سلمان» and «ولي العهد» comes back, in order, in one Whisper segment (3.16–8.00 s); the English read-back contains "His Royal Highness Crown Prince Mohammed bin Salman" verbatim. No human listened; native review stays pending.

**Timing.** sh-03-02 planning duration 13.1 → 15.4 s; edit lists rebuilt: sh-03-02 en 15.000 → 16.833 s, ar 18.733 → 22.233 s; every other shot keeps its duration. sh-03-02 re-rendered in both languages (figures traced 2022, 50, 60, 2030; 0 not found); render manifests rebuilt (`film.render trace`, 0 not found). Subtitles rebuilt (182 / 201 cues; `film.subs check` PASS, 646 warnings against 652 before, all reading-speed notes; `align-qa` PASS, ar: 1 warning, m-05-02, unchanged line).

**Planning estimate.** The English spoken estimate is now 722.0 s against the validator's 720 s ceiling, only because of the honorific; no other line may change in this run. `film/script/meta.yaml` records a 2.0 s `duration_allowance` for main/en, which `film.script validate` reports as a warning (anything beyond is still an error; test). For CP9: the delivered cuts already run 14:32 / 16:49 against the 8–12 minute target.

**Paid TTS.** This run: ElevenLabs USD 0.05 (limit 1), Nabrah USD 0.03. Totals: ElevenLabs 3.18 (of 15 approved), Nabrah 3.88, combined **USD 7.06 of 60** (alert 48 not reached).

## 00000. FIX_MBS_QUOTE (11 Nov 2026): the Crown Prince population line

`prompts/FIX_MBS_QUOTE.md` (Tariq, 11 Nov 2026). Where §0000 and earlier differ, this section governs for the two main cuts. **The trailers are untouched** (full SHA-256 before and after: en 81fa64ec4dd12f3b…, ar 21df620d1994ec75…: OK).

| deliverable | path (through `film/renders`) | duration | size | SHA-256 (first 16) | loudness (two-pass; measured again on the MP4 with ffmpeg loudnorm) |
|---|---|---|---|---|---|
| main cut, English | `out/ksa-rail-twin-main-en.mp4` | 870.3 s (14:30) | 257.9 MB | 06b6b3327b551eee (was aaca43afbcdf5b98) | −16.09 LUFS, −1.80 dBTP (narration master −16.09 / −1.89) |
| main cut, Arabic | `out/ksa-rail-twin-main-ar.mp4` | 1005.3 s (16:45) | 282.3 MB | 4cae0dfe950bed28 (was 4059f6d34e867878) | −16.03 LUFS, −1.74 dBTP (narration master −16.03 / −1.90) |

H.264 1920×1080 30 fps, AAC 48 kHz (`eng` / `ara`), one `mov_text` subtitle track; `ffprobe` 11 Nov 2026. Full SHA-256: en 06b6b3327b551eeeeed87565830a1db4a0e909669cd34773edda9826c861521f, ar 4cae0dfe950bed285be66688a3ebc46e9536885883ec95a919e75c4afd6a52b8. The previous cuts are kept as `renders/_superseded/ksa-rail-twin-main-{en,ar}.pre-fix-mbs-quote-20261111.mp4` (and the old sh-03-02 shots and script PDFs beside them); the assembler wrote `.new.mp4` first and renamed. Script PDFs `out/script/main.{en,ar}.pdf` re-rendered (`common.ar_render`).

**What changed.** Only line m-03-03 (both languages) and its shot sh-03-02:
- English: "After The Line launch in July 2022, the Crown Prince told journalists the aim is 50 to 60 million people in the Kingdom by 2030, about half Saudis. Remarks, not a published programme target."
- Arabic: «وبعد إطلاق تصاميم ذا لاين في يوليو 2022، قال ولي العهد للصحفيين إن الهدف إن عدد سكان المملكة يوصل بين 50 و60 مليون بحلول 2030، ونصهم تقريباً سعوديين. وهذي تصريحات، مو هدف منشور في برنامج رسمي.» (full tashkeel in `speech_text`, bare مليون and digits; `native_review = pending`; `ar-rewords.csv`).
- Caption sh-03-02 (both languages) says the same; `caption-edits.csv`. "100 million" / "2040" / «100 مليون» are gone from the main script, captions, subtitles (files and the embedded tracks) and the render manifests; only the before/after edit logs keep the old wording.
- Sources: S-r10-057 (Argaam, 26 Jul 2022, Arabic; primary), S-r10-058 (Argaam English edition), S-r10-025 (AFP original on France 24, corroboration of 50 million by 2030 only). Details and quotes: `docs/sources/r10-notes.md` §FIX_MBS_QUOTE.

**Narration.** Only m-03-03 re-voiced: English ElevenLabs George (`eleven_multilingual_v2`, 190 characters, USD 0.04), 13.607 s (was 13.235); Arabic Nabrah Abdullah (same section-3 role voice), 17.320 s (was 16.040), USD 0.02. Every other narration WAV is byte-identical (SHA-256 checked before and after for all 68 + 68 main and 11 + 11 trailer lines). Read-back (mlx-community/whisper-large-v3-turbo, local): en CER 0.000, ar CER 0.059 (all figures heard as written; no spoken-number override needed).

**Timing.** sh-03-02 planning duration 11.7 → 13.1 s (`film.shots check` against the English estimate); edit lists rebuilt: sh-03-02 en 14.633 → 15.000 s, ar 17.433 → 18.733 s; every other shot keeps its duration (start times shift). sh-03-02 re-rendered in both languages (figures traced: 2022, 50, 60, 2030; 0 not found); render manifests rebuilt (`film.render trace`, 0 not found). Subtitles rebuilt from `lines.csv` (181 / 201 cues; `film.subs check` PASS with the same warning count as before, `align-qa` PASS, ar: 1 warning, m-05-02, unchanged line).

**Paid TTS.** This run: ElevenLabs USD 0.04 (limit 1), Nabrah USD 0.02. Totals: ElevenLabs 3.13 (of 15 approved), Nabrah 3.85, combined **USD 6.98 of 60** (alert 48 not reached).

## 0000. FIX_FILM_STORY (10–11 Nov 2026): the whole country's connectivity, in plain words

`prompts/FIX_FILM_STORY.md` (Tariq, 10 Nov 2026; audience: the general public). Where §000 and earlier differ, this section governs for the two main cuts. **The trailers are untouched** (SHA-256 before and after, full hash checked: en 81fa64ec4dd12f3b, ar 21df620d1994ec75).

| deliverable | path (through `film/renders`) | duration | size | SHA-256 (first 16) | loudness (two-pass; measured again on the MP4 with ffmpeg loudnorm) |
|---|---|---|---|---|---|
| main cut, English | `out/ksa-rail-twin-main-en.mp4` | 870.0 s (14:30) | 257.8 MB | aaca43afbcdf5b98 (was 4b9aadf29ec9e857) | −16.09 LUFS, −1.80 dBTP (narration master −16.08 / −1.89) |
| main cut, Arabic | `out/ksa-rail-twin-main-ar.mp4` | 1004.0 s (16:44) | 282.1 MB | 4059f6d34e867878 (was b6fa4e80b0a43176) | −16.03 LUFS, −1.72 dBTP (narration master −16.03 / −1.90) |

H.264 1920×1080 30 fps, AAC 48 kHz (`eng` / `ara`), one `mov_text` subtitle track; `ffprobe` 11 Nov 2026. The previous cuts are kept outside `out/` as `renders/_superseded/ksa-rail-twin-main-{en,ar}.pre-fix-film-story-20261110.mp4` (the assembler also writes `.new.mp4` first and renames). Script PDFs `out/script/main.{en,ar}.pdf` re-rendered.

**1. North and south (new, section 8, after m-08-10).** Six new lines (m-08-14 … m-08-19, both languages) and six new `sim_map` shots (sh-08-15 … sh-08-20):

| shot | line | what is shown | figures (source) |
|---|---|---|---|
| sh-08-15 | m-08-14 | camera from Tabuk down to Asir, Najran and Jazan over today's lines; true-scale 10 km rings, no station inside | 10 km (`docs/coverage.md`, S-r10-050) |
| sh-08-16 | m-08-15 | the 16 additions of the S6-L6 connected layout draw themselves along their routed alignments | 16 additions, 18 cities (`docs/r6-l6-connected.md` §2, S-r10-051) |
| sh-08-17 | m-08-16 | north: Tabuk–Sakaka and the Jouf–Sakaka spur to the North Line; south: Abha–Khamis Mushait to Najran, to Bisha (then Taif, and Muwai on the Landbridge) and down the escarpment through Baysh to Jazan; relief at zoom detail | Tabuk–Sakaka 458.9 km on screen, "about 460" spoken (S-r10-052) |
| sh-08-18 | m-08-17 | committed and connected-layout stations glow; two bars of the whole population | 32.7 M vs 26.1 M within two hours of a station (`runs/r6/l6/national_reach.json`, S-r10-053; reported only, A-r6-104). No "in the model" refrain (single closing notice rule) |
| sh-08-19 | m-08-18 | the five cities with a question mark: door-to-door times not routed | none: **the study did not route these trips** (S-r10-054) |
| sh-08-20 | m-08-19 | benefit-to-cost bar of S6-L6 beside the line at 1 | about 0.06 riyals back per riyal (BCR P50 0.061, medium, 60 y; `runs/r6/l6/score/S6-L6.csv`, S-r10-055) |

Every S6-L6 storyboard row carries `source: S6-L6 (comparison layout)`; the single closing notice still covers it on screen. **Routes:** every hypothetical line is the corridor's routed least-cost path on the 30 m DEM (`runs/align/corridors-s1/<id>/alignment.geojson`, full vertex detail). The alignment files also hold a 2-point `straight_sketch`; the main-cut helper used to draw both, so `corridor_geom` now drops `straight_sketch` features (`routed_lines`, tested). That also removed straight sketches from sh-04-05 and sh-08-02 … 04, which were re-rendered.

**Not routed by the study (list for Tariq):** door-to-door rail times from Tabuk, Abha, Khamis Mushait, Najran and Jazan to the nearest big city on the S6-L6 layout (or any layout). No accepted file holds them (R8 report, `runs/r6/l6/`, coverage, RJ and extra-travel studies, commute test); the film says so (m-08-18). No new study was run.

**2. Plain language.** Nine lines rewritten in both languages (m-04-07, m-08-01 … 08; before/after in `film/storyboard/story-edits.csv` and the r10 status block): no net present value, robust value or fiscal range is spoken or shown any more. Money is said as "for every riyal spent, about X come back; below one, a line does not repay its cost": committed lines about 0.3; central case about 6; upside about 2.3; reach alternative about 1.1; Riyadh–Jeddah sketches about 0.2 ("which helps explain why there is no direct Riyadh–Jeddah railway today"). Each is the published BCR P50 of the same run and case (UN WPP medium, 60 years, Green Book 2026), rounded to one decimal; the S6-L6 value 0.061 is said as 0.06 (one decimal would read 0.1, +64 %). Every rounding is in `film/storyboard/rounding-log.csv`. **m-08-06** (listed as required): meaning unchanged; only "in present value" → "in today's money" (Arabic «بقيمتها الحالية» → «بقيمة فلوس اليوم»); figures and sources identical. Captions follow the same wording (full sentences); NPV range bars became benefit-to-cost bars with a bold line at 1 ("pays back its cost"); chart labels that said net present value (sh-04-07, sh-07-04) or present value (sh-08-06) now say "benefits minus costs" or "in today's money".

**Voices.** English: ElevenLabs George (`JBFqnCBsd6RMkjVDRZzb`, `eleven_multilingual_v2`) re-voiced only the 15 new or changed lines (`--only`; 3,130 characters, USD 0.65), then m-08-17 once more after its refrain was removed (USD 0.03); all 68 English lines are George. Arabic: Nabrah (Daniah; m-04-07 Abdullah) for the same 15 lines after the BUILD_MOVIE treatment (plain wording, full tashkeel in `speech_text`, bare مليون / مليار / digits; `film/storyboard/ar-rewords.csv`; `native_review = pending`); 3,875 characters, USD 0.32; then m-08-03, m-08-15 and m-08-19 again with the numbers spoken in words after the read-back (USD 0.06), and m-08-17 after its refrain was removed (USD 0.01). Read-back (mlx-whisper large-v3-turbo, local): English median CER 0.005, max 0.091; Arabic median 0.015, max 0.116 (m-05-02, unchanged line). Ear checks for Tariq: English m-08-04 / m-08-19 ("riyal" transcribed as "Riyadh" / "real"), m-08-15 ("additions" as "editions"); Arabic m-08-16 (opening «فيها» not transcribed), m-08-19 (opening «وثمن» transcribed as "8"), m-08-06 (the transcript ends with «ترجمة نانسي قنقر», most likely Whisper's known end-of-clip hallucination; not verified by ear).

**Checks that changed the first assembly.** `make test` caught three things, all fixed and the affected shots re-rendered (sh-08-01 … 04, 08, 18, 20) before the final assembly: (a) m-08-17 had brought back "In the model" / «في النموذج», against the single-closing-notice rule (removed; re-voiced); (b) captions and chart labels used the digit 1 ("below 1", "1: pays back"), which breaks the numbers-in-narration and labels-carry-words rules: now "one" / «واحد»; the central-case caption says "about 6" (not 6.0); sh-08-17 declares 458.9 as an `extra_figures` value (spoken "about 460"); (c) a new loop variable in `film/sim_main.py` shadowed the name sh-07-01's chart reads (renamed; sh-07-01's render predates it and is unchanged). The verifier's first pass (FAIL F1) found that the render manifests `film/assemble/renders-main-{en,ar}.csv` still listed only the 58 earlier shots, because shots rendered one by one are not added to them; `film.render trace` now rebuilds the manifest from the shot list and the edit list (64 rows each, 0 figures not found; the trailer manifests come out byte-identical), with a test. Four older tests pinned the previous state (58 shots, 62 Arabic lines, m-08-06 byte-identical, rewords keep digits) and were updated to the new state with the FIX_FILM_STORY rows checked by `tests/test_film_story.py`.

**Credits.** The Arabic cut's credits no longer name ElevenLabs George (he does not speak in it); Nabrah attribution kept (`film.render.credits_lines`). The English credits still name Nabrah although the English cut has no Nabrah voice: left as it was (not in the brief), flagged for CP9.

**Paid TTS.** This run: ElevenLabs USD 0.68 (limit 5), Nabrah USD 0.39. Total to date **USD 6.92 of the USD 60 cap** (ElevenLabs 3.09 of the 15 approved; Nabrah 3.83).

**Runtime.** Both main cuts run further over the 8–12 minute target: English 14:30 (+50.9 s on 819.1 s), Arabic 16:44 (+69.9 s on 934.1 s); the six new lines carry 58.1 s (English) and 68.4 s (Arabic) of narration; the shorter money lines save some of it back. Options for CP9 as in §1.


## 000. BUILD_MOVIE_EN (10 Nov 2026): the English main cut, and the English trailer re-voiced on a paid plan

`prompts/BUILD_MOVIE_EN.md` (Tariq, 10 Nov 2026: ElevenLabs paid use up to USD 10 inside the USD 60 combined paid-TTS cap). Where §00 and earlier differ, this section governs for the English files. The Arabic main cut and the Arabic trailer are untouched (SHA-256 checked before and after: main-ar b6fa4e80b0a43176, trailer-ar 21df620d1994ec75).

| deliverable | path (through `film/renders`) | duration | size | SHA-256 (first 16) | loudness (two-pass, measured) |
|---|---|---|---|---|---|
| main cut, English | `out/ksa-rail-twin-main-en.mp4` | 819.1 s (13:39) | 236.8 MB | 4b9aadf29ec9e857 | −16.10 LUFS, −1.73 dBTP (narration master −16.09 / −1.89) |
| trailer, English (re-voiced) | `out/ksa-rail-twin-trailer-en.mp4` | 77.6 s | 30.2 MB | 81fa64ec4dd12f3b (was 07b52f6556115c01, free tier) | −16.22 LUFS, −1.87 dBTP (narration master −16.21 / −1.90) |

H.264 1920×1080 30 fps, AAC 48 kHz (`eng`), one `mov_text` subtitle track (`eng`); `ffprobe` 10 Nov 2026. Loudness rows in `film/assemble/loudness.csv`.

**Plan.** `GET /v1/user/subscription` (10 Nov 2026, before any call): tier `creator`, status active, 0 of 170,283 characters used, monthly; next invoice USD 25.30 (subtotal 22.00). Creator = USD 22 a month for 121k credits, commercial licence (elevenlabs.io/pricing, read 10 Nov 2026); paid plans allow commercial use (Terms of Use §1(c), last updated 9 Oct 2026, read 10 Nov 2026). Spend is logged at USD 0.2091 per 1,000 characters sent (25.30 / 121,000; A-film-013), an upper bound: the account's own counter showed 4,842 characters used after 11,516 were sent.

**Narration.** All 62 English main lines: ElevenLabs George (`JBFqnCBsd6RMkjVDRZzb`), `eleven_multilingual_v2`, seed 1, `--no-fallback`, in four batches (sections 1–2, 3–4, 5–6, 7–8); the timing table (`film/voice/timing/main-en.csv`) now carries `voice_id` and `model` on every row. No Nabrah and no other voice on any English line; 717.7 s of narration. Read-back (mlx-whisper large-v3-turbo, local): median CER 0.005, max 0.091 (m-02-04: "300 km", "Medina", transcription format only). **m-03-02**: the read-back heard an extra word after "35.3 million" ("dozen" / "in Dursen"): the start of the next line ("In July 2022…") bleeding in through the next-line context. A forced retake with the same seed reproduced it (73 characters, USD 0.02), so the cached raw take was trimmed at the energy minimum after "million" (5.66 s, 40 ms fade, 0.3 s silence) and the line rebuilt from the cache; read-back now exact (CER 0.000), 5.96 s. Same voice, same take; no other line edited.

**Pictures and assembly.** Edit list from the measured narration (58 shots, 819.1 s); all 58 shots rendered with `renderer: sim_map` in English (`film.render all --jobs 4`, then sh-03-01 again at its shortened 16.333 s); every shot duration matches the edit list (ffprobe); 0 figures not found (`film/assemble/renders-main-en.csv`). Subtitles 174 cues; `film.subs check` PASS, `align-qa main-en` PASS (0 warnings). Single closing notice as in §0 (storyboard unchanged). m-08-06 untouched (`film/script/lines.csv` not edited in this run). Runtime 13:39 against the 8–12 minute target (options as in §1).

**English trailer.** Re-voiced with `--force` on the Creator plan (11 lines, 838 characters, USD 0.18): all 11 takes are new audio with the same durations to the millisecond, so the edit list, shots and subtitles are unchanged (`cmp`); read-back identical to the reviewed take. The free-tier file is kept outside `out/` as `renders/_superseded/ksa-rail-twin-trailer-en.free-tier-20261108.mp4` (not for release).

**Paid TTS.** This run: ElevenLabs USD 2.41 (main 2.21 + m-03-02 retake 0.02 + trailer 0.18), Nabrah 0. Total to date **USD 5.85 of the USD 60 cap** (Nabrah 3.44, ElevenLabs 2.41; ElevenLabs approval USD 10).

**Rights.** `film/rights_log.csv` and `film/licences-r10.csv` ElevenLabs George rows now record the Creator plan and commercial use; premade voice, no cloning; no attribution required, credited on the last slide.


## 00. BUILD_MOVIE (10 Nov 2026): the Arabic main cut in the trailer style

`prompts/BUILD_MOVIE.md` (Tariq, 10 Nov 2026). Where §0–§4 differ, this section governs for the main cuts. The trailers are untouched (SHA-256 first 16: en 07b52f6556115c01, ar 21df620d1994ec75, as in §0).

| deliverable | path (through `film/renders`) | duration | size | SHA-256 (first 16) | loudness (two-pass, measured) |
|---|---|---|---|---|---|
| main cut, Arabic | `out/ksa-rail-twin-main-ar.mp4` | 934.1 s (15:34) | 257.8 MB | b6fa4e80b0a43176 | −16.04 LUFS, −1.72 dBTP (narration master −16.03 / −1.90) |
| main cut, English | `out/ksa-rail-twin-main-en.mp4` | **not rebuilt here** (rebuilt by BUILD_MOVIE_EN, §000) | — | c19a7828e6667e35 then (superseded) | — |

H.264 1920×1080 30 fps, AAC 48 kHz (language `ara`), one `mov_text` subtitle track (`ara`); `ffprobe` 10 Nov 2026. Loudness rows in `film/assemble/loudness.csv`.

**English: blocked.** ElevenLabs `GET /v1/user/subscription` (10 Nov 2026): tier free, 8,950 characters left; the 62 English main lines need 10,605 spoken characters (the say.csv number words included; 9,608 in the plain text). As the prompt prescribes, no English line was synthesised, no voice was mixed and Nabrah was not used for English. A paid ElevenLabs plan is needed before the English narration (one free cycle of 10,000 characters is less than 10,605); the free tier is non-commercial only in any case (§0).

**Pictures.** All 58 main shots are `renderer: sim_map` (58, not 59: sh-06-07 was removed with m-06-07 by FIX_HALF2_QUALITY). The choreography is in `film/sim_main.py` (one scene per shot: moving camera over the Copernicus relief, the twin's GeoJSON, trains, pulses, range bars and diagrams read from the run files named in each shot's `data_source`); `film/sim.py` changed additively only (`prepare`/`frame_at`, photo insets for sh-02-01, main titles without the credits block, the credits roll), and 600 of 600 trailer frames were proven byte-identical before and after. Every main shot carries one full-sentence caption per language (`film/storyboard/caption-edits.csv`, 114 caption edits; digits unchanged, figures traced: `film/assemble/renders-main-ar.csv`, 58 shots, 0 figures not found), the layer legend, and the OSM and Copernicus credits; the single closing notice sits on sh-08-14 only, with the credits (`film.render.credits_lines`). Render: 1.6 GB of shots on the external drive, about 26 minutes with 4 jobs (21:05–21:31).

**Arabic narration.** Nabrah Abdullah / Norah / Daniah (roles unchanged) read the new `speech_text` column: full tashkeel on all 62 main Arabic lines; the only words left bare are مليون (20), مليار (11) and المجدولة (1) (read worse when vocalised, FIX_HALF2_QUALITY). Before tashkeel, ambiguous words were reworded in plain Saudi Arabic (`film/storyboard/ar-rewords.csv`: 22 rows, 12 lines reworded in the script text, 5 lines given new spoken number words and m-03-01's existing override reworded; no digit, name, source or claim changed; tested). Read-back (mlx-whisper large-v3-turbo, local, offline): three rounds; final CER median 0.015, maximum 0.116 (m-05-02, where the transcriber writes «أو إيه جي» as OEG, the numbers as digits and بالمية as %: the same words). Narration 832.6 s; subtitles 190 cues, `film.subs check` and `align-qa` PASS.

**Paid TTS.** This run: Nabrah USD 1.25 list equivalent (main-ar 1.08, re-synthesis 0.13 + 0.04), ElevenLabs 0. Total to date **USD 3.44 of the USD 60 cap**.

Script Markdown v1.4 and `out/script/main.ar.pdf` re-rendered.

**Runtime.** 15:34 against the 8–12 minute target (the tashkeel Nabrah read is slower: 832.6 s of narration, R10_HALF2 778.0 s). Options for CP9 as in §1 (trim lines, a registered tempo factor, shorter pauses).


## 0. FIX_HALF2_QUALITY (8 Nov 2026): the new trailers

Tariq watched the R10_HALF2 trailers and asked for a simulation look, not slides; an ElevenLabs documentary narrator for English; tashkeel on the Arabic Nabrah text; and (ADD note) no repeated "in the model / uncalibrated" refrain: the notice is said once, on the last slide and in the credits. The two trailers are rebuilt. **The main cuts are not rebuilt**: they wait for Tariq's watch of the new trailers. The files at `out/ksa-rail-twin-main-{ar,en}.mp4` are still the R10_HALF2 card versions (Nabrah English, per-shot stamps): do not treat them as final.

| deliverable | path (through `film/renders`) | duration | size | SHA-256 (first 16) | loudness (two-pass, measured) |
|---|---|---|---|---|---|
| trailer, English | `out/ksa-rail-twin-trailer-en.mp4` | 77.6 s | 30.2 MB | 07b52f6556115c01 | −16.22 LUFS, −1.86 dBTP |
| trailer, Arabic | `out/ksa-rail-twin-trailer-ar.mp4` | 86.9 s | 33.3 MB | 21df620d1994ec75 | −16.06 LUFS, −1.88 dBTP |

Both: H.264 1920×1080 30 fps, AAC narration, one `mov_text` subtitle track (unvocalised accepted text); `ffprobe`, 8 Nov 2026. Loudness from `film/assemble/loudness.csv` (target −16 LUFS / −1.5 dBTP, master −1.9 dBTP for AAC headroom, A-film-007). Script PDFs in `out/script/` re-rendered after the refrain edit.

**Pictures (renderer `sim_map`, `film/sim.py`).** Every frame is drawn: a night relief basemap computed from the registered Copernicus GLO-30 tiles (cop-dem-glo30-align-3as-2026-11-01; the Kingdom only, seas and neighbours in one dark tone), a moving camera, and the twin's own GeoJSON on top (regions, existing and committed lines, hypothetical alignments from `runs/align` and `runs/study/rj`). Per shot: a train runs the North Line to Qurayyat and an air arc draws to Jeddah (t-01); seat particles flow both ways on the Jeddah–Riyadh arc (t-02); Taif, Tabuk, Abha, Najran and Jazan pulse with true-scale 10 km rings (t-03); 507 zone dots grow by census population (t-04); a rail dot on the fastest Riyadh–Jeddah case races an air dot, timed by the study's door-to-door ratio, air ÷ rail = 0.64 (route RJ-A, `runs/study/rj/times-s1/times.csv`) (t-05); the Taif spur draws itself up the escarpment at full DEM detail (t-06); the optimiser's logged evaluations appear one by one (`runs/r6/results.tsv`, cost across, robust NPV up; the agent loop's 9 kept layouts in green) (t-07); the three central-case stations pulse while a range bar grows to 4.0–5.6 bn SAR (t-08); the state's net-cost ranges by delivery model with the median marked (`runs/r7/fiscal/fiscal.json`, S6-L2) (t-09); the national network at night (t-10); title, closing notice and credits (t-11). Moving trains are illustrative, not timetables (A-film-015). Captions: one full sentence per shot (what, units, year or horizon), about 17 characters per second of shot; extra caption figures are declared (`extra_figures`: 2025 prices, 60 years) and traced. Every on-screen number traced to its data source (`film/assemble/renders-trailer-*.csv`, 0 not found). Text layers come from local headless Chrome (Arabic shaped right-to-left), as before. No deck.gl/Kepler capture, no Manim, no paid video API; no new package (numpy, Pillow, rasterio, scipy, ffmpeg and Chrome are already registered). Render time: about 2¼ min per trailer with 4 jobs.

**Single closing notice.** "Synthetic demand, uncalibrated: a scenario comparison, not a forecast." (Arabic: glossary term 4, «طلب تركيبي غير مُعايَر: مقارنة سيناريوهات، ليست توقعاً.») sits on the trailer's last slide (sh-08-54) and in the main-cut credits (sh-08-14, `credits_lines`); no other shot carries a stamp (`film.shots check`, `check_closing_notice`). Script: 34 Arabic/English line edits plus m-06-07 and sh-06-07 removed (`film/script/refrain-edits.csv`, `film/storyboard/refrain-edits.csv`); digits, names and ranges unchanged (test).

**Voices.**
- English: ElevenLabs premade voice **George** (id JBFqnCBsd6RMkjVDRZzb, "Warm, Captivating Storyteller"), `eleven_multilingual_v2`, seed 1, previous/next line context; chosen over Daniel after a one-line A/B (both read t-06 back exactly; `film/voice/ab-fixq.csv`). No cloning. Read-back CER ≤ 0.05 on all 11 lines (`film/voice/readback/trailer-en.csv`). **Licence:** Tariq's account is on the free tier: non-commercial use only (Terms of Use §1(c)(i), last updated 9 Oct 2026, read 8 Nov 2026); the user keeps rights in Output (§4(c)(ii)). Regenerate on a paid plan before any commercial release.
- Arabic: Nabrah public voices Abdullah, Norah, Daniah (roles unchanged), fed the vocalised `speech_text` column of `lines.csv` (A-film-014: hand/LLM vocalisation, Saudi pronunciation, no case endings). Read-back showed that vocalising مليون، مليار، مجدول and dialect imperfect prefixes (يكبر، يغطي) made Nabrah worse, so those keep the accepted spelling; read-back CER now 0.00–0.07, except t-07 at 0.17 («عشرة آلاف» heard as «عشر آلاف»). Subtitles and on-screen Arabic keep the unvocalised accepted text. Attribute Nabrah on published audio. The Nabrah licence caveat from §2 (part generated while the workspace looked like a free trial) still stands.

**Paid TTS.** Nabrah USD 2.19 list equivalent to date (this run: +0.09 trailer-ar, +0.06 re-synthesis of 8 lines), ElevenLabs USD 0.00 (free tier; 1,050 of 10,000 characters this cycle). Combined USD 2.19 of the USD 60 cap.

**Disk.** Internal 33 GiB free; external 925 GiB free. Trailer shots 281 + 282 MB, basemap cache 10 MB (external `cache/sim`). Caches (`UV_CACHE_DIR`, HF, Torch) on the external `cache/`.

**Verifier.** `docs/status/verify-FIX_HALF2_QUALITY.md`: first pass FAIL only on the missing end-label lines (written last by design); minor picture notes fixed (central-case labels now appear with their panel, «أو إيه جي» kept on one line, Arabic y-axis label lifted; sh-08-51, sh-07-51, sh-01-52 re-rendered, both trailers re-assembled; hashes above are the final ones). Not changed: `docs/credits.md` row 154 still describes ElevenLabs as an R10 A/B candidate (it feeds the R8 annexes, so it is left for the integration step); the rights log and `film/licences-r10.csv` carry the current row.

**Still open.** Native Saudi review of every Arabic row and of the tashkeel (pending; nobody contacted). Tariq's watch of the new trailers decides the main-cut rebuild. Browser subtitle boxes overlap the credit line in some players (cosmetic).

## 1. Outputs

All bulky files are on the external volume `/Volumes/Extreme_SSD/Projects/KSA-RailTwin/`, reached from the r10 worktree through the symlinks `film/renders` → `…/renders` and `film/audio` → `…/audio` (both on the internal APFS disk; `.gitignore` names them without a trailing slash). Nothing under them is committed.

| deliverable | path (through `film/renders`) | duration | size | SHA-256 (first 16) |
|---|---|---|---|---|
| main cut, Arabic | `out/ksa-rail-twin-main-ar.mp4` | 880.9 s (14:41) | 58.9 MB | 4d49f0a74b15882a |
| main cut, English | `out/ksa-rail-twin-main-en.mp4` | 817.1 s (13:37) | 56.8 MB | c19a7828e6667e35 |
| trailer, Arabic (superseded by §0) | `out/ksa-rail-twin-trailer-ar.mp4` (overwritten) | 88.5 s | 6.5 MB | 139299499a75ac58 |
| trailer, English (superseded by §0) | `out/ksa-rail-twin-trailer-en.mp4` (overwritten) | 84.5 s | 6.0 MB | 2879dce6002430b8 |
| script PDFs with citations | `out/script/{main,trailer}.{ar,en}.pdf` | — | 52–165 KB | rendered from `film/script/*.md` by `common.ar_render` (local Chrome) |

Each MP4: H.264 1920×1080, 30 fps; AAC 48 kHz mono narration (192 kb/s requested; 138–153 kb/s measured); one `mov_text` subtitle track in the cut's language (language tags `ara` / `eng`); title metadata from `film/script/meta.yaml`. Measured with `ffprobe` on 8 Nov 2026. Shots: `film/renders/<cut>-<lang>/<shot>.mp4` (59 per main cut, 11 per trailer), every one equal to its edit-list duration within 0.04 s (checked). 4K masters: **not made** (1080p first; 4K was optional and was not started).

Runtime against the 8–12 minute target: **both main cuts run over** (Arabic 14:41, English 13:37, credits included). The narration is the cause: Nabrah reads Arabic at about 11.6 characters per second (the half-1 plan assumed 14, A-film-002) and the measured narration alone is 778.0 s (Arabic) and 714.3 s (English); the English grew when numbers were spelled out in words (§2). No tempo change was applied (the brief allows tempo changes only as registered assumptions, and native review is pending). Options for CP9: accept; trim lines (Tariq or the native reviewer); register a tempo factor (about 1.1 would be needed for Arabic); or shorten the pauses (A-film-008..010 add about 1.4 s per shot).

Trailers are inside the 60–90 s target.

## 2. Narration

- **Engine actually used: Nabrah** (`nabrah_tts_v1`, public voices) for **all 148 lines** of both cuts and both trailers; roles per section (A-film-006): Abdullah (guide: sections 1, 3, 4), Norah (history and existing network: 2, 5), Daniah (method and numbers: 6, 7, 8). Tables: `film/voice/timing/<cut>-<lang>.csv` (engine, voice, seconds, loudness before/after per line). One WAV per line under `film/audio/narration/<cut>-<lang>/`.
- **Credits ran out mid-run, then came back.** At the 40th English main-cut line Nabrah returned HTTP 400 ("no sufficient credits … or is not subscribed to a plan") after about 17,700 characters (≈ 7,000 credits, the free-trial size, S-nabrah-003). As the prompt prescribes, the remaining English lines fell back to Chatterbox built-in (reported, `film/audio/narration/main-en/fallback.txt`). At about 01:00 AST on 8 Nov Nabrah calls succeeded again (cause not visible through the API), and every fallback line was re-synthesised with Nabrah. **No Chatterbox audio is in any delivered file**; the fallback renditions stay on the external drive, unused (rights log: Chatterbox `test_only`).
- **Licence caveat for CP9:** Nabrah's written clearance (S-nabrah-005) covers public voices **on a paid plan**. About 17,700 characters were generated while the workspace looked like a free trial. Before any release, regenerate on a confirmed paid plan (`film.voice speak --force`; 21,855 spoken characters for all four) or get Nabrah's written confirmation that trial-generated audio is covered. Attribute Nabrah on published audio (credits roll does).
- **Spoken-number overrides.** The Whisper read-back found Nabrah reading "10,000" as "ten, zero" (t-07 in both languages, m-07-02 Arabic) and an English "422 thousand" misheard twice across two generations, and the Chatterbox fallback garbling decimals. 27 lines now have a spoken text with numbers in words (`film/voice/say.csv`, numbers only; script and subtitles unchanged; the method `film/script/pronunciation.md` §2 prescribes). After re-synthesis every figure in the script was checked against the read-back.
- **Lines for an ear check (read-back still ambiguous, not proven wrong):** m-06-02 Arabic (“بين ثلاثة وعشرة كيلو” transcribed as “بين 13”), m-08-04 English (“minus twenty-one point seven” transcribed as “minus 20 1.7”), t-07 Arabic (first word “حَكَم” transcribed as “كم”; CER 0.220), m-02-04 / m-06-04 / t-02 English (place names: Haramain, “through Riyadh–Jeddah”, “Jeddah–Riyadh”; CER 0.108–0.124). Read-back tables: `film/voice/readback/<cut>-<lang>.csv` (`scripts/film_readback.py`, mlx-whisper large-v3-turbo, local, offline).
- **A/B (approved 31 Oct 2026; sample, not a second film):** three number-heavy lines per language (`film/voice/ab-half2.csv`). Whisper CER: Nabrah 0.005–0.031 (Arabic), 0.010–0.027 (English); ElevenLabs free tier with premade voices 0.051–0.520 (Arabic; Saudi library voices are refused on the free tier, HTTP 402), 0.008–0.010 (English); open: Chatterbox built-in 0.137–0.747 (Arabic), Kokoro am_michael 0.000–0.019 (English). CER is an intelligibility screen, not a dialect or naturalness score. ElevenLabs free-tier output is not for commercial use and is not in the film.

## 3. Loudness (two-pass loudnorm, A-film-007)

| stage | main ar | main en | trailer ar | trailer en |
|---|---|---|---|---|
| narration master (−16 LUFS, −1.9 dBTP target) | −16.04 LUFS, −1.90 dBTP | −16.05, −1.90 | −16.10, −1.90 | −16.05, −1.88 |
| delivered MP4 (AAC) | **−16.04 LUFS, −1.55 dBTP** | **−16.06, −1.77** | **−16.10, −1.84** | **−16.06, −1.78** |

Source: `film/assemble/loudness.csv` (ffmpeg loudnorm measurement of each file; LRA 4.0–5.6 LU). The first assembly measured −1.32 to −1.40 dBTP after AAC encoding, above the −1.5 target, so the master is normalised with 0.4 dB headroom (`aac_headroom_db`, A-film-007). Per line, linear two-pass loudnorm gives −18.01 to −15.79 LUFS and at most −1.46 dBTP (`film/voice/timing/*.csv`); the per-cut master pass sets the delivered level.

No music bed: no CC0 or CC BY track could be obtained without a new account, so the film ships without music (rights log row "Music: none chosen").

## 4. Picture

- **Renderer (departure from the storyboard labels).** Every shot is drawn by `film/render.py`: three 1920×1080 layers per shot and language written as HTML with inline SVG and rendered by the local headless Google Chrome (as `common.ar_render`; Arabic shaped and right-to-left), then animated with ffmpeg (context-to-data dissolve, a 3.5 % push-in on the picture only, fades where the storyboard says fade or dissolve). The storyboard's `deckgl_capture` / `manim` labels were planning choices; deck.gl, MapLibre and Manim were not used (rights log notes). Animation is deliberately simple (draft quality): no animated counters or line-drawing; the data panels are static range bars.
- **Data.** Maps draw the twin's own GeoJSON (existing, committed, hypothetical alignments, regions, governorate points for labels; three-layer legend; OSM credit on every map frame). Hillshade on the seven shots with the Copernicus credit comes from the registered 3-arc-second GLO-30 tiles (`cop-dem-glo30-align-3as-2026-11-01`), display exaggeration ×4. Charts draw range bars from the storyboard's verified on-screen text. Every number in each shot's English on-screen text is looked up in that shot's `data_source` files (runs through `RAILTWIN_RUNS_ROOT`, S-/A- register rows), as text or by value at the token's precision and a 1/1e3/1e6/1e9 unit scale: **all found** in all four manifests (`film/assemble/renders-<cut>-<lang>.csv`, columns `figures_traced`, `figures_not_found`). This is a tracing aid, not a replacement for the verifier's check.
- **Labels on frame.** Footers (`synthetic`, `synthetic+not_official`), composite labels, Copernicus credit and quotation styling (English only) follow `film/storyboard/shots.yaml`; no logo of any entity; no AI-generated footage. Archival: two Library of Congress / Wikimedia Commons public-domain photographs (B. Moritz, 1906; Medina station, 1914) on sh-02-01, downloaded 8 Nov 2026 to the external drive only (rights log rows; loc.gov still returns 403 to a scripted request, so the rights statement is read from the Commons metadata).
- Shot durations follow the measured narration through the edit lists `film/assemble/edl-<cut>-<lang>.csv` (head 0.6 s, tail 0.8 s, 0.35 s between lines; A-film-008..010); `shots.yaml` keeps the planned English estimates, as its header says.

## 5. Subtitles

Built from `film/script/lines.csv` (never retyped) and the measured line times: `film/subs/{main,trailer}.{ar,en}.{srt,vtt}`; cues cut at clause punctuation, ≤ 2 × 42 characters, 1–7 s, 2-frame gaps; Arabic rows start with U+200F.

| file | cues | `film.subs check` | `film.subs align-qa` |
|---|---|---|---|
| main.ar | 177 | PASS, 162 warnings | PASS, 0 warnings |
| main.en | 184 | PASS, 83 warnings | PASS, 2 warnings (read-back CER m-02-04 0.124, m-06-04 0.108) |
| trailer.ar | 19 | PASS, 17 warnings | PASS, 1 warning (t-07 0.220) |
| trailer.en | 16 | PASS, 7 warnings | PASS, 1 warning (t-02 0.110) |

Every check warning is "reading speed < 12 cps" (the narration is slower than the subtitle floor, which is a warning, not an error). `align-qa` checks that each line's cues join back to the script text exactly, lie inside that line's narration interval, and that read-back CER ≤ 0.30 (warning above 0.10, A-film-012).

RTL/bidi QA (`scripts/film_subs_qa.py`): three cues per cut and language, shown as WebVTT over a clip of the delivered MP4 (starting at the cue) in two players, headless: Google Chrome (Blink, driven by puppeteer-core from the dashboard's `web/node_modules`, which waits until the track has an active cue) and Firefox (Gecko): 24 screenshots in `film/subs/qa/`, each showing its cue (Arabic digits in logical order, right-aligned, no reordering seen). The first Chrome captures showed no cue (verifier F2: the page could not seek because the local test server has no Range support); fixed and regenerated. Cosmetic note for CP9: the browser cue box overlaps the bottom-left footer label in some frames. A third renderer (mpv/libass) was not installed: installing it would have upgraded 23 Homebrew packages mid-run. The measured probe (`common.ar_render bidi-probe` over every Arabic cue) found 0 risky numeric runs (signed numbers, numeric ranges, quantile labels) and 0 errors, because the Arabic script writes signs and ranges in words; `film/subs/qa/bidi-*.json`.

## 6. Rights log and registers

`film/rights_log.csv`: 64 rows, `film.rights check` PASS (used 13, candidate 31, test_only 6, rejected 14). Used in the delivered film: Nabrah AI (narration), Noto Naskh Arabic and Noto Sans (fonts), Google Chrome headless and ffmpeg (tools), OpenStreetMap data and the alignment sidecars (ODbL), Copernicus GLO-30 (hillshade), GASTAT derived tables, the two LOC photographs; Whisper and mlx-whisper for QA only. Credits card (sh-08-14, `credits_lines()` in `film/render.py`): KSA Rail Twin (research film, not official), Nabrah (voices), Claude (Anthropic), OSM, GASTAT, SAR/HHR facts, OAG, GACA, the Copernicus credit and no-liability line, the archival photographers (rights-log attribution of the used images), the fonts (SIL OFL 1.1), the render tools (Google Chrome, ffmpeg) and a pointer to docs/credits.md and film/rights_log.csv. The first assembly's card still credited Chatterbox and printed raw register notes; the verifier caught it (F1), the card was rewritten, sh-08-14 re-rendered in both languages and both main cuts re-assembled (SHA-256 above). Latin runs on the Arabic card are LTR isolates. `film/licences-r10.csv` notes updated; assumptions A-film-006..012 in `film/assumptions-r10.md`. The ClArTTS-clone variants stay rejected and unused; Coqui XTTS-v2 stays out.

## 7. Disk, worktrees, spend

- Disk (8 Nov 2026, end of run): internal 33 GiB free; external 925 GiB free. Media written: renders 2.3 GB, audio 1.4 GB on the external drive. At launch: internal 26.2 GiB, external 931.1 GiB. During the run, swap pushed internal free space down to 13.7 GiB at its lowest; the gate re-checks the 10 GB floor before every shot and never closed.
- Worktrees: **none moved.** `git worktree move` cannot cross filesystems (`Cross-device link`, rc 128, first candidate `pilot-al_baha`); the run stopped there as instructed and deleted nothing (`docs/status/r10.md`). 39 worktrees still listed.
- Paid TTS: Nabrah USD 2.04 list equivalent (A-film-011 rate; about 9,950 credits over all calls; likely USD 0 actually charged for the trial part); ElevenLabs USD 0 (free tier). Well under the USD 60 cap (alert 48). Rows in `docs/cost-log.md`.

## 8. Native review

**Pending on every Arabic row** (`lines.csv` `native_review = pending`). No reviewer was contacted; Tariq arranges it. Publication order (Tariq, 12 Nov 2026, Q9): code published now; native Saudi review of the Arabic pending; films follow the review (§000000000). The Arabic narration, the number words in `film/voice/say.csv` and the ear-check lines in §2 go to the reviewer together.
