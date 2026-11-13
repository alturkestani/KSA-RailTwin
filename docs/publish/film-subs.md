> **Document version:** docs/publish/film-subs.md v1.0 | 13 Nov 2026 | Author: main builder (FILM_SUBS) | Status: draft

# Film: cross-language subtitles, burned-in copies, LinkedIn Arabic cut (FILM_SUBS)

Tariq's request: `prompts/FILM_SUBS.md` (13 Nov 2026). Open tools only: ffmpeg, headless Chrome, the film's existing fonts. No TTS, no paid call, no new package, no push.

## What was made

Files are in `renders/out/social/subs/` on the external volume (`film/renders` symlink). They are not committed (rule 8). The SRT/VTT files are also committed under `film/subs/`.

| file | what | duration | bytes | SHA-256 |
|---|---|---|---|---|
| `main-ar.en.srt` | English subtitles for the Arabic cut | 0.600–988.020 s | 19,008 | 4dadde1fd4410d955b10b040c5ed190864b1d7703294a6381e8aeb1804382a9e |
| `main-en.ar.srt` | Arabic subtitles for the English cut | 0.600–851.375 s | 22,199 | 2191c619af723aa7dc7a03477807bd08796098d6bddc0048c32c278cea48ef70 |
| `main-ar-subEN.mp4` | Arabic cut with English subtitles burned in | 1008.833 s (16:48.8) | 250,974,762 | ecbc970e0377aec5ab3974ec66c42d79384c1d0525e10ee55fd78d257ae78a57 |
| `main-en-subAR.mp4` | English cut with Arabic subtitles burned in | 872.167 s (14:32.2) | 230,869,419 | 21472cde75d6e5f4106e0f527cd379a214ebed3b8a9b622f5b68e65d7bf1e578 |

- Both MP4s are H.264 1920×1080 at 30 fps with AAC audio, the same duration as their source cut. Their audio stream is a stream copy. `film.cross burn` checks that the MD5 of the demuxed audio packets matches the source: true for both.
- `main-ar-li.mp4` was **not made**. See item 3.

## How (item 1)

- Text: `film/subs/cross/main-ar.en.csv` and `film/subs/cross/main-en.ar.csv`, one row per narration line (68 each), with these columns: line id, source text, subtitle text, spelled figures, native_review. The source text equals the narration line in `film/script/lines.csv` (`text`, the display form of `speech_text`: removing the tashkeel and the spelled-out numbers of `speech_text` gives `text`). The builder drafted the translations from the accepted lines. Where the meaning is identical, it reused the other cut's narration wording.
- **Arabic subtitles: native_review = pending** (all 68 rows). They carry no tashkeel. Digits are Western, as in the film. The honorific is «صاحب السمو الملكي الأمير محمد بن سلمان، ولي العهد». English: "His Royal Highness Crown Prince Mohammed bin Salman".
- Vision 2030 (m-03-05 to m-03-07): the English cut quotes the document. No official Arabic wording is registered, so the Arabic subtitles carry the meaning with «بمعنى النص», as the Arabic narration does. They do not present a translation as a quotation. The English subtitles of the Arabic cut say "in paraphrase" / "the meaning of the text, not its exact wording", because the Arabic narration says that.
- Timing is not re-estimated. Each line's cues sit inside that line's measured narration interval (`film/assemble/lines-main-{ar,en}.csv`, from the per-line WAV timing in `film/voice/timing/`). The cues are cut by the same packer as the same-language subtitles (`film.subs.line_cues`).
- Generated, not retyped: `uv run python -m film.cross build`. Checks: `uv run python -m film.cross check` and `tests/test_film_cross.py` (13 tests).
- Figure test: the numbers of every subtitle equal the numbers of the narration line it translates. Two declared exceptions are written in words in the subtitle: m-01-07 "1 hour" → «ساعة» and m-05-04 "2 hours" → «ساعتين». The other way round, the Arabic narration says «بساعة» and «ساعتين», so the English subtitles of the Arabic cut say "an hour" and "two hours".
- The test also checks 43 proper names (present in the subtitle exactly when present in the source), the full honorific, the absence of tashkeel in the Arabic, and that the committed SRT/VTT are byte-identical to a fresh build.

| | main-ar.en (English subs, Arabic audio) | main-en.ar (Arabic subs, English audio) |
|---|---|---|
| cues | 212 | 170 |
| two-line cues | 157 | 106 |
| longest cue | 6.794 s | 6.880 s |
| shortest cue | 1.089 s | 1.096 s |
| max characters per line | 42 | 42 |
| max lines per cue | 2 | 2 |
| reading speed, max | 16.5 cps | 13.8 cps |
| cues under 12 cps (warning only) | 149 | 163 |
| `film.subs check` | PASS | PASS |

- Placement: every main shot carries its caption, credits and OSM line at the bottom or the side (storyboard `on_screen_text`). So every burned cue sits in the top band (x 560–1360, y from 28 px), the `film/social.py` layout that clears the legend and the composite pill. The sidecar SRTs carry no position tags: `{\an8}` is not portable, and LinkedIn's handling is unknown. Players put sidecar cues at the bottom, where they may overlap the caption band.
- RTL: Chrome draws the Arabic cues with the film's fonts. The measured `common.ar_render bidi-probe` over every Arabic cue found 0 risky numeric runs and 0 errors at 900, 480 and 360 px (`film/subs/qa/bidi-main-en.ar.json`). Ranges are written in words («بين 0.8 و5.3»). A frame of `main-en-subAR.mp4` at 230 s was viewed: shaped, right to left, clear of the legend.
- Cosmetic, known: the shared packer splits long clauses by word, so a few cues end with a short orphan word on line 2 (for example "… told Reuters in July 2020 / the"). The text is unchanged; it can be improved in a later pass.

## Item 3: LinkedIn Arabic cut ≤ 14:50: not possible without cutting speech

`uv run python -m film.cross li-plan` (shot-by-shot table in `film/assemble/li-floor.csv`):

| | length |
|---|---|
| main-ar today | 16:48.834 (1008.834 s) |
| target | 14:50.000 (890 s) |
| narration WAVs alone, back to back (every head, gap, tail and silent slide removed) | **14:59.040 (899.040 s)** |
| holds at the low ends of their assumption ranges (head 0.3 s, gap 0.2 s, tail 0.4 s; A-film-009/008/010), the 20 s closing notice kept | 16:04.067 |

The 68 narration WAVs alone already run 9.04 s over the target. No tightening of pauses, holds or slides can reach 14:50 with byte-identical speech, so per the prompt no LinkedIn cut was assembled, no speech was cut, and nothing was re-timed. The shortest no-speech-loss length is 14:59.04 in theory (zero pauses, not watchable). A realistic shortest is about 16:04 with the holds at their low ends, or 15:44.067 if the 20 s closing notice is also cut to zero.

**Proposed 2-part split** at the chapter boundary that balances the parts best, before section 6, "How we routed and priced it" / «كيف رسمنا المسار وسعّرناه»:

| part | sections | length at today's timing |
|---|---|---|
| 1 | 1–5 (journeys, the map, a growing country, who rides, what rail unlocks) | 7:59.367 |
| 2 | 6–8 (routing and pricing, the search, cost and economic impact, closing notice) | 8:49.467 |

Both parts fit LinkedIn's 15:00 limit without any tightening. The other chapter boundaries are in `li-plan`'s output. Part 2 would need its own title card and part 1 its closing notice: both are editorial choices for Tariq.

## Item 4: originals unchanged

SHA-256 before the run (01:05 AST) and after the burns, both measured:

| file | before = after |
|---|---|
| ksa-rail-twin-main-ar.mp4 | 391f72bfcedf94d65ace316e2c65bfa73759c93398a80fed36f962fd3a5751bf |
| ksa-rail-twin-main-en.mp4 | 540c5e41094ed2ce7f2d71be8ed3a44ce89407e38059ccc7eba378c31ada150e |
| ksa-rail-twin-trailer-ar.mp4 | 64cf4389fb8d36895e4024628540a64227bfb25fa1ba79bccf7014f77e2f8ef1 |
| ksa-rail-twin-trailer-en.mp4 | 78802cd553486ad249dcf2fef97aa1cd61f3ecfe69552e125195858c7ca38d30 |

Labels: the burned copies keep the film's own picture, including the closing notice "synthetic demand, uncalibrated: scenario comparison, not a forecast". The subtitles add no figure that the narration does not say.
