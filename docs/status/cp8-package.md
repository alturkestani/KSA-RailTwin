> **Document version:** docs/status/cp8-package.md v1.4 | 8 Nov 2026 | Author: R10 builder (v1.4: FIX_HALF2_QUALITY decision, single closing notice; v1.3: ACCEPT_FIX_CP8_NOTES, Tariq's acceptance, six notes, ClArTTS clone rejected; v1.2: FIX_CP8_NOTES fixes and Tariq's decisions; v1.1: source row count, storyboard sync) | Status: reviewed (CP8 plan accepted by Tariq, 7 Nov 2026; half 2 not started)

# CP8 review package: R10 half 1 (documentary film)

Everything below is a draft for Tariq's decision at CP8. Nothing was rendered or assembled, no paid API was called (USD 0 of the USD 60 TTS cap), no account was created and nothing was pushed. A human native Saudi speaker still has to review the Arabic script and audio before any release; Tariq arranges that.

## 00. ACCEPT_FIX_CP8_NOTES (7 Nov 2026): Tariq accepts FIX_CP8_NOTES and the written CP8 plan

Prompt: `prompts/ACCEPT_FIX_CP8_NOTES.md` v1.0 (byte-identical copy of the main checkout's file). Tariq accepted FIX_CP8_NOTES after an independent coordinator review of e97eaba. This is not approval to start half 2, render, assemble, download models, call paid TTS, merge to main, fast-forward, push, tag, add a remote, or contact anyone.

**Accepted (Tariq, 7 Nov 2026)**
- FIX_CP8_NOTES, with the notes below.
- The written CP8 plan: the scripts and the storyboard as they now stand; the dialect recommendation (educated white Saudi leaning Najdi for every narrator; MSA only for verbatim official quotes; Hijazi second choice); the voice hierarchy (Nabrah public voices Daniah, Norah and Abdullah first, once Tariq sets the keys; the Chatterbox built-in voice as the clean-licence fallback; NAMAA and Nabra-Saudi-82M allowed under MIT / Apache-2.0 even though the training corpus is unnamed, not automatic replacements).

**ClArTTS clone: not cleared (correction applied).** The Chatterbox clone from the ClArTTS reference clip ch_02_arabic_tts_dataset_417 (a real LibriVox reader) is not cleared and is not to be used. Section 4 marked it commercial use Y; that is corrected. Wherever the variant is graded, it now reads commercial use "unresolved / not cleared without written consent", status rejected for use, with the same reason: "rejected for use (Tariq, 7 Nov 2026, ACCEPT_FIX_CP8_NOTES): the ClArTTS clip ch_02_arabic_tts_dataset_417 is a real LibriVox reader's voice; cloning it breaks the no-cloning rule; not cleared without that reader's written consent". Files: §4 table below; `film/voice/README.md` v1.3 (rows 1 and 4, note A); `film/voice/scores.csv` (`commercial_use` and `notes`); `film/rights_log.csv` (status `rejected`); `film/licences-r10.csv` (`commercial_use` and `status`). The NAMAA run with the same clip (README row 4, `namaa-saudi-clartts`) clones the same reader, so it gets the same correction. The no-cloning rule stands.

**Unchanged**
- Native review stays pending on every Arabic row. Nobody was contacted.
- Half 2 is not started. Disk gate stays at ≥ 50 GiB; about 23 GiB free (`df -h ~`, 7 Nov 2026). No render.
- No merge to main in this run; integration waits for a separate ask. It has to be a merge, not a fast-forward: merge-base e9e0433; main has commits r10 lacks (ed419ce prompt; cda7a23 and a345f28 cost rows; and since then a34b8cc, the ACCEPT_FIX_CP8_NOTES prompt).

**Notes recorded (Tariq, 7 Nov 2026; verbatim, non-blocking; no new study)**
1. Diffstat vs 6cec58f is 22 files, +705/−139 (not +704/−139).
2. docver 389 files; manifest 388 rows (do not collapse both to 388).
3. PNG-cache planning assumes the longest shot is 19.2 s and ignores the 20 s credits; correcting that is about 8.8 / 19.2 / 60.6 GB. Optional to note; do not render.
4. English narration plus credits is 708.8 s (11:49). More than about 11.2 s of extra breathing room would pass 12 minutes; do not write that "any" breathing room would.
5. S-r10-013 claim column still says "Jeddah to Abha nonstop block time" while the locator and card are Abha → Jeddah, valid to 28 March 2026. Optional register cleanup later; do not invent a forward-direction time.
6. Arabic m-08-06 second clause elides a repeated «يقدّر»; meaning is clear; leave wording polish for the native reviewer.

Applied from the notes: note 1 in `docs/status/r10.md` (FIX_CP8_NOTES block); note 4 in §0 below and in `docs/status/r10.md`; note 2: the status files state the two counts separately (this run's measured counts are in `docs/status/r10.md`, ACCEPT_FIX_CP8_NOTES block). Notes 3, 5 and 6 are recorded only: the render estimate in §3 and the storyboard stays 8.8 / 19.1 / 60.4 GB until the next render-planning pass; S-r10-013 and the Arabic wording are unchanged.

## 0. FIX_CP8_NOTES (7 Nov 2026): Tariq's notes on this package, applied

Tariq reviewed the package at 6cec58f and approved eight fixes and a set of decisions (`prompts/FIX_CP8_NOTES.md`). The earlier verify-R10 PASS is not clearance for half 2. Per-fix before/after, with line and shot ids, is in `docs/status/r10.md` (FIX_CP8_NOTES block); the verifier report is `docs/status/verify-FIX_CP8_NOTES.md`.

**Fixes**
1. **m-08-06 / sh-08-06:** the first range (2.3–19.3 bn SAR) is now "users' travel time and cost savings, in present value" / «وفورات الناس في وقت التنقل وتكلفته، بقيمتها الحالية». It is no longer "travel time saved" or «قيمة الوقت اللي يرجع للناس»: `user_time_cost` is the rule of a half on the logsum composite cost and contains fares and car fuel (`docs/cba.md` §5 matrix row; the R8 report says "user time and cost savings"). The second range (0.6–7.4 bn) is "a safety benefit, road deaths and injuries avoided valued at standard appraisal values", not a crash count. Values unchanged from `runs/cba/CBA-S1-committed-programme/results.json` (un_wpp_medium, 60 years, greenbook_2026: `pv_user_time_cost` P10/P90 2313.139 / 19336.083 and `pv_safety` 595.837 / 7444.498 SAR million). The shot's source card states the basis: 2025 SAR, present value 2026, medium population, 60 years, Green Book 2026, P10–P90. Wider impacts stay in m-08-07.
2. **Timing:** shot durations recomputed from the covered lines (sh-01-04 14.8 → 16.2 s; sh-06-03 13.1 → 14.3 s; sh-02-02 6.1 → 5.4 s and sh-08-06 14.5 → 18.5 s after the two rewritten lines). `film.shots check --lines` now fails if any narrated shot's duration differs from its covered English lines, and `film.shots storyboard` plus `tests/test_film_real.py` fail if the storyboard tables, section titles, on-screen text or durations drift from `shots.yaml` / `meta.yaml`.
3. **Map-bearing frames:** sh-01-05 (held escarpment of sh-01-04: OSM + Copernicus), sh-01-07 (vignettes of sh-01-02/03/04/06: OSM + Copernicus) and sh-08-13 (held national map: OSM, legend) now carry `osm_credit: true`. A new rule makes any re-cut or held picture inherit the source shot's footer, OSM credit and Copernicus credit.
4. **Flight card sh-01-04:** "Jeddah → Abha · Air: 1 h 15 min" became "Jeddah – Abha · Air, Abha → Jeddah: 1 h 15 min (one airline's published schedule, now expired)"; the source caption names the direction and "valid to 28 March 2026" (S-r10-013). No forward-direction time was invented.
5. **Vision 2030 Arabic (m-03-05, m-03-07; sh-03-04, sh-03-05):** spoken paraphrase kept; the Arabic on-screen text now opens with «بمعنى النص، مو نصه الحرفي»; `quote_label` is per language, `{en: true, ar: false}`, so no English quotation styling reaches the Arabic card. No official Arabic Vision URL is registered, and none was added.
6. **sh-07-51:** footer none → `synthetic` (it re-uses the search-register scroll of sh-07-04). The same inheritance rule also caught **sh-01-51** (trailer vignettes re-cut from sh-01-03's OAG seat card and sh-01-04's hillshade): footer none → `synthetic+not_official`, Copernicus credit added; sh-01-07 likewise carries `synthetic+not_official`. No spoken-line labels were added on m-04-04, m-06-01, m-06-02 or t-06, and those four footers are unchanged.
7. **pronunciation.md:** the number-word example «ألف ومية وخمسين» (1,150) became 1,250 = «ألف وميتين وخمسين». No audio generated.
8. **m-02-02 / sh-02-02:** "inaugurated the first railway line: Riyadh to Dammam" → "inaugurated the Riyadh–Dammam railway line" (AR «دشّن الملك عبدالعزيز خط سكة حديد الرياض–الدمام»; S-r10-003). m-02-03 keeps "passenger trains reaching Qurayyat since 2022"; nothing calls the North Line "begun in 2022".

**Decisions recorded (Tariq, 7 Nov 2026; not reopened)**
- The extra-travel §5 lines, the OAG seat-count lines included, keep both labels ("synthetic demand, uncalibrated: scenario comparison, not a forecast" and "not the official ranking"); an "observed seat counts" source caption may sit beside them.
- Glossary term 4 stays «طلب تركيبي غير مُعايَر». `.claude/skills/motion-maps/SKILL.md` (v1.1) and `.claude/skills/documentary-script/SKILL.md` (v1.2) now prescribe it instead of «طلب اصطناعي». The voice test paragraph `film/audio/tests/ar.txt` (gitignored, recorded before this decision) still reads «طلب اصطناعي»; any later sample uses the glossary term.
- Length: the target is 8–12 minutes, no mandatory trim. English main cut 688.8 s narration (11:29), 708.8 s with the 20 s credits roll (11:49); more than about 11.2 s of extra breathing room would push it past 12 minutes (corrected 7 Nov 2026, ACCEPT_FIX_CP8_NOTES). Arabic 669.2 s (11:09), 689.2 s with credits (11:29).
- Paid A/B stays off until Tariq sets `NABRAH_API_KEY` and `ELEVENLABS_API_KEY`; combined cap USD 60, alert USD 48, USD 0 used.
- Voices: the hold on Nabra-Saudi-82M and NAMAA-Saudi-TTS is lifted; they are accepted under their published licences (Apache-2.0 / MIT) although the training corpus is unnamed. They are allowed options, not automatic replacements: Nabrah's public voices (Daniah, Norah, Abdullah) remain the first choice for Arabic and Chatterbox stays the clean-licence fallback, without any claim of exhaustive training-data provenance for Chatterbox. The no-cloning rule stands; the Chatterbox clone from the ClArTTS reference clip (a real LibriVox reader) is flagged in the rights log, not resolved. Recorded in `film/rights_log.csv`, `film/licences-r10.csv` and `film/voice/README.md` (v1.2). No model downloaded, no audio generated.
- Native review stays pending on every Arabic row; nobody was contacted.
- No render, no assembly, no merge to main, no INTEGRATE_R10. `main` has the cost-log row cda7a23 and `r10` branched from e9e0433, so they have diverged; integration waits until Tariq accepts this fix.
- Disk: about 20 GiB free; the render gate stays at ≥ 50 GiB. `/tmp/r10-voice` (2.4 GB) and the archives were left in place.

## 1. Dialect recommendation
File: `docs/dialect-recommendation.md` (v1.1); assumption `A-film-005` in `film/assumptions-r10.md` (refines Tariq's preference `A-film-001` in `docs/assumptions.md`).

- **Recommendation (not a decision):** one educated "white" Saudi register, leaning Najdi, for every narrator in the Arabic cut and trailer. MSA only for verbatim on-screen quotations of official documents. Hijazi is the second choice; a regional mix is not recommended.
- **Reasons, against the four W10 criteria:**
  - Intelligibility: sources describe the white register as understood across all regions (S-r10-d10 to d13).
  - Documentary tone: it carries a dignified register without MSA stiffness.
  - Broadcast practice: four Saudi documentary series were found and confirmed (S-r10-d06 to d09), but no page states the narration dialect. This criterion is the weak point, and the document says so. Please listen to one episode of each, or ask the native reviewer to, before deciding.
  - Voice availability: the three approved Nabrah voices are labelled "Saudi" (S-r10-d01 to d03). No Hijazi-labelled voice was found.
- **Voice roles (provisional, both cuts):** Abdullah as guide, Norah for history and the existing network, Daniah for method and numbers. To be settled after the A/B.

## 2. Scripts
| file | lines | estimated running time |
|---|---|---|
| `film/script/main.ar.md` | 63 | 11:09 |
| `film/script/main.en.md` | 63 | 11:29 |
| `film/script/trailer.ar.md` | 11 | 1:05 |
| `film/script/trailer.en.md` | 11 | 1:08 |

- Running times are estimated at 14 Arabic and 15 English characters per second plus 0.4 s per line (A-film-002 to 004). They will be measured when the narration exists.
- The Arabic is written natively in the recommended register; the English was written separately. The two cuts share line ids, sections and figures. `film.script validate` enforces that the figures match digit by digit.
- Source data: `film/script/lines.csv` (148 rows). Every Arabic row has `native_review = pending`. Place names: `film/script/pronunciation.md`.

**`lines.csv` counts per section** (identical in Arabic and English):

| section | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | total |
|---|---|---|---|---|---|---|---|---|---|
| main | 10 | 8 | 8 | 7 | 5 | 7 | 5 | 13 | 63 |
| trailer | 2 | 1 | 1 | 1 | 0 | 1 | 1 | 4 | 11 |

**How sources were handled.** New spine facts have `S-r10-` rows in `docs/sources/r10.csv` (97 rows: 001–049 facts and licence pages, d01–d14 dialect, v01–v34 voice). `docs/sources/r10-notes.md` compares Tariq's recollection with what each page says.

**Left out (no source found or not adequate):**
- Weekly flight counts: about 470 RUH–JED and about 67 Riyadh–Tabuk.
- Riyadh–Tabuk flight time.
- The Riyadh–Jeddah "1:35 to 2:00" flight time (aggregator snippets only).
- Riyadh Metro length (conflicting press figures).
- The 1916 Hejaz sabotage date (sources conflict).
- The Tabuk station museum (search snippet only).
- A count of road deaths avoided. No scored count exists, so m-08-06 narrates the monetised safety benefit (deaths and injuries avoided at standard appraisal values) instead (section 0, fix 1).

**Where the pages differ from Tariq's recollection (the page wins):**
- Haramain reached 300 km/h from 1 Jan 2020, not at the 2018 opening.
- Asir's 9.1 million is the formal target set in Jan 2025. The 2021 launch said "more than 10 million".
- Riyadh's 15 million is a remark to Reuters in Jul 2020, narrated as "under review". It is never presented as settled.

**Cut for length (sourced):** the Umrah land-entry line, the Hajj-permits line, and "rail does not simply replace flying".

## 3. Storyboard and shot list
Files: `film/storyboard/storyboard.md` (v1.3) and `film/storyboard/shots.yaml` (v1.1).

- **Shots:** 70 (main 59 for 708.8 s including a 20 s credits roll; trailer 11 for 67.5 s). Every one of the 74 line ids is covered by exactly one shot.
- **Renderers:** 32 dashboard captures (deck.gl), 37 Manim charts, 1 archival shot (ffmpeg only).
- **Content rules:** no AI footage, no logos. The OSM credit is on every map. Every modelled picture carries the footer. The Arabic footer uses the glossary term «طلب تركيبي غير مُعايَر».
- **Half-2 build items:** a dashboard cinema mode (hidden interface, camera keyframes, frame stepping, in-frame legend, footer and credit) plus new film layers: two-hour reach shading, a hillshade, Haram markers, the RJ sketches and the air arc.
- **Remotion:** source-available, not open source. Its free licence covers individuals and companies of up to 3 employees (read 7 Nov 2026). The plan uses Manim (MIT) instead, under rule 12.
- **Disk estimate for rendering (1080p30, both cuts and both trailers):** lean 8.8 GB; recommended 19.1 GB; upper 60.4 GB; 4K about 54 GB (recomputed after FIX_CP8_NOTES). The arithmetic is in the storyboard. About 20 GiB is free now, so the 50 GiB render gate needs about 30 GiB freed first.

## 4. Voice and TTS comparison
Files: `film/voice/README.md` (full table, v1.2), `film/voice/scores.csv` and `film/voice/disk-log.md`. The samples are in `film/audio/tests/<candidate>/`, which is gitignored and local only.

**Limit on the scores:** they are the builder's judgement from Whisper read-back, phoneme logs and signal checks. Nobody listened to the samples, and the native review overrides them.

| candidate | licence | commercial use | sample | CER (verbatim) |
|---|---|---|---|---|
| Chatterbox Multilingual V2, built-in voice | MIT | Y | `chatterbox-mtl-builtin/` | 0.165 |
| Chatterbox Multilingual V2, ClArTTS voice (clone of a real LibriVox reader) | MIT + CC BY 4.0 clip | unresolved / not cleared without written consent; rejected for use (Tariq, 7 Nov 2026: no-cloning rule) | `chatterbox-mtl-clartts/` | 0.301 |
| NAMAA-Saudi-TTS (two voices) | MIT; training data not named (accepted by Tariq, 7 Nov 2026) | unclear (licence Y; corpus unnamed) | `namaa-saudi-*/` | 0.211 / 0.183 |
| Nabra-Saudi-82M | Apache-2.0; training data not named (accepted by Tariq, 7 Nov 2026) | unclear (licence Y; corpus unnamed) | `nabra-saudi-82m/` | 0.074 |
| Piper ar_JO-kareem | GPL-3.0 engine; voice data licence not stated | unclear | `piper-ar_JO-kareem/` | 0.078 |
| Meta MMS-TTS ara | CC BY-NC 4.0 | N (test only; weights deleted) | `mms-tts-ara/` | 0.146 |
| Kokoro-82M af_heart / am_michael (English) | Apache-2.0 | Y | `kokoro-82m-*/` | 0.0075 / 0.0176 |
| Chatterbox V3, F5-TTS, Fish Audio, OpenVoice V2, NC Saudi fine-tunes | mixed | mixed | not run (download cap, licence, or no Arabic base voice) | — |
| Coqui XTTS-v2 | CPML (non-commercial) | N | licence research only; never downloaded; never in the film | — |
| Nabrah Studio (Daniah, Norah, Abdullah) | proprietary; cleared in writing 1 Nov 2026; attribute Nabrah | Y on a paid plan | not run: no `NABRAH_API_KEY` set | — |
| ElevenLabs | proprietary; commercial on paid plans only | Y on a paid plan | not run: no `ELEVENLABS_API_KEY` set | — |
| Azure ar-SA, Google ar-XA, AWS Polly, Orpheus Saudi (Groq) | proprietary | unclear (terms not read) | not used | — |
| Human Saudi narrator | per contract, with written usage rights | Y if contracted | not contacted | — |

Human narrator cost: about USD 70–320 per 10-minute cut, computed from published marketplace rates (not a quote).

**Recommendation (not a decision):**
- **Arabic:** Nabrah's public voices, if the approved A/B wins with a native reviewer. They are the only Saudi-dialect voices with written commercial, online and broadcast clearance. The clean-licence open fallback is Chatterbox V2 with its built-in voice, numbers written as words and line-by-line read-back.
- **English:** Kokoro-82M af_heart, with place names respelled in the spoken text.
- **True dialect quality usually needs a human narrator, or at least native review.**
- **Fine-tune:** listed as an option only. SADA is non-commercial; commissioned recordings with written training rights are the clean route. It needs Tariq's approval.

**Cost logged:** USD 0 paid; nothing to log in `docs/cost-log.*` for vendors. Disk used: about 4.4 GiB downloaded (packages and open weights), within the 6 GB cap for this task. The lowest free space was 16.0 GiB.

## 5. Rights log and licence register
- `film/rights_log.csv`: 64 rows (49 candidate, 13 rejected, 2 test only; NAMAA-Saudi-TTS and Nabra-Saudi-82M moved from test only to candidate on 7 Nov 2026). It covers voices and TTS models, 6 fonts, tools (Manim, Remotion, deck.gl, kepler.gl, MapLibre, ffmpeg, Blender), OSM (ODbL), the alignment sidecars (ODbL share-alike derived databases), Copernicus terrain, GASTAT tables, an optional basemap, 5 public-domain Hejaz Railway photographs (Library of Congress, read via Wikimedia Commons; loc.gov returned 403, so re-check before render) and music ("none chosen; CC0/CC BY only, no NC/ND").
- `film/licences-r10.csv`: 51 rows.
- Credits (half 2): Nabrah + Claude + KSA Rail Twin, per R10_LAUNCH.
- **Deviation:** the film registers live under `film/` (`film/assumptions-r10.md`, `film/licences-r10.csv`), not at `docs/assumptions-r10.md` or `docs/licences-r10.*`. The `docs/` files feed the R8 report annexes and the licence release note, and R10_LAUNCH bars changes to R8 files and licences. Merge them later only with a rebuild Tariq approves.

## 6. Verifier result (line by line, both scripts)
Report: `docs/status/verify-R10.md`.

- **Lines checked:** all 148, in both languages and both cuts. Every figure matched its run file or source row digit by digit, and the Vision 2030 quotes were re-checked in the live PDF.
- **Lines changed after the first pass:** 2. m-01-07 is now "one airline's published schedule listed" (the schedule source has expired). m-06-03 is now "two of the via-Taif sketches" (the Taif leg is shared).
- **Other fixes:** the Arabic label term now follows the glossary; the section-5 Arabic heading no longer uses «وش»; the A-film id clash is resolved; stale `film/_work` paths are repointed.
- **Lines removed for lack of a source:** the 7 facts listed in section 2, which never entered the script.
- The final verdict of the re-check is recorded in the report.

## 7. Open questions for Tariq

Items 1–7 were answered on 7 Nov 2026 (section 0). Kept here as asked, with the answer.

1. **m-08-06:** users' travel time and cost savings in present value (2.3 to 19.3 billion riyals; rule of a half on the composite cost, so fares and car fuel are inside it) and the monetised safety benefit, deaths and injuries avoided at standard appraisal values (0.6 to 7.4 billion), come from the published S1 run `runs/cba/CBA-S1-committed-programme/results.json` (2025 SAR, PV 2026, medium population, 60 years, Green Book 2026, P10–P90); the R8 report text does not quote them. Are they acceptable as "the study's own" figures? **Answer (7 Nov):** keep the sourced amounts with this meaning and basis (fix 1).
2. **OAG lines (m-01-05, m-05-02, m-05-03):** they carry "synthetic, not the official ranking" because R10_LAUNCH requires both labels on the extra-travel quotable lines, even though seat counts are observed data. Keep the label, or relabel them as sourced facts? **Answer:** keep both labels.
3. **Vision 2030 in Arabic:** source the official Arabic text so the Arabic cut can quote it verbatim? Today it paraphrases and says so on screen. **Answer:** keep the paraphrase, with an explicit Arabic on-screen note and no quotation styling (fix 5).
4. **Four shots (sh-04-04, sh-06-01, sh-06-02, sh-06-51)** carry the synthetic footer because their picture is model output, although their lines are unlabelled. Keep the footer, or label the lines too? **Answer:** keep the footers; no spoken-line labels.
5. **North Line date:** the script says passenger trains have reached Qurayyat since 2022 (one press source, partial). Do you want an earlier Riyadh–Hail start date sourced? **Answer:** keep "passenger trains reaching Qurayyat since 2022"; never "begun in 2022".
6. **Length:** the English main cut is estimated at 11:29 of narration (11:49 with credits). **Answer:** the target is 8–12 minutes; no mandatory trim.
7. **Voices:** set `NABRAH_API_KEY` and `ELEVENLABS_API_KEY` yourself if you want the approved A/B (cap USD 60, alert at USD 48). Decide whether Nabra-Saudi-82M and NAMAA stay out until their authors name the training data. **Answer:** the hold is lifted; allowed options, not automatic replacements; no cloning without written consent.
8. **Disk:** about 30 GiB must be freed to reach the 50 GiB render gate. The throwaway TTS environments in `/tmp/r10-voice` can be deleted after CP8.
9. **Native reviewer:** please arrange a native Saudi reviewer for the Arabic script now and for the audio later. Claude never contacts anyone.

## Decision of 8 Nov 2026 (FIX_HALF2_QUALITY, Tariq's ADD note ~01:01 AST)

For the film only, the per-line label rules (`prompts/R10_LAUNCH.md`: both labels on every extra-travel and RJ-study line) and the storyboard's per-shot footer rules are overridden: the synthetic notice ("synthetic demand, uncalibrated: scenario comparison, not a forecast"; Arabic glossary term 4, «طلب تركيبي غير مُعايَر») appears once, on the last slide and in the credits, and the narration no longer repeats "in the model" or "uncalibrated". The `label` column of `film/script/lines.csv` keeps the data (`none` where the stamp was dropped; before/after in `film/script/refrain-edits.csv`). PROJECT.md rule 3, the R8 report, the dashboard, the executive summaries and the studies are unchanged. Details: `docs/status/r10.md`, FIX_HALF2_QUALITY block.

