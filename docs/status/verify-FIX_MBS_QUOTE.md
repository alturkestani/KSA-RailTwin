> **Document version:** docs/status/verify-FIX_MBS_QUOTE.md v1.1 | 11 Nov 2026 | Author: red-team-verifier (claude-fable-5-1) (v1.1: pass 2 at 55bd54e, F1 closed; v1.0: pass 1 at e4d9e84) | Status: verified

# VERIFY_FIX_MBS_QUOTE: red-team verification of FIX_MBS_QUOTE

Pass 1: worktree `.worktrees/r10`, branch `r10`, HEAD e4d9e84, baseline 65e03be; tree clean (`git status --porcelain` empty). Pass 2 (section below): HEAD 55bd54e. Read-only; nothing fixed. Brief: `prompts/FIX_MBS_QUOTE.md` v1.0 (Tariq + coordinator addendum, 11 Nov 2026). Run 11 Nov 2026 (AST).

## Commands (item 9)

| command | result | time |
|---|---|---|
| `uv run ruff check .` | All checks passed, exit 0 | 0.07 s |
| `uv run ruff format --check .` | 803 files already formatted, exit 0 | 0.03 s |
| `uv run pytest` (`-o addopts="" -q`; `RAILTWIN_RUNS_ROOT` set) | **989 passed, 69 skipped, 0 failed**, 10 warnings, exit 0 | 46.4 s |
| `uv run python -m common.docver check docs prompts .claude film/script` | docver OK: 403 files, exit 0 | 0.2 s |
| `uv run python -m common.manifest verify` | manifest OK: 388 rows, exit 0 | 1.3 s |
| `uv run python -m film.script validate film/script/` | PASS: 158 lines (main/en 68 = 12:00, main/ar 68 = 11:40), 1 warning (trailer/ar 58.3 s, pre-existing), exit 0 | 0.1 s |
| `uv run python -m film.shots check film/storyboard/shots.yaml --lines film/script/lines.csv` | PASS: 75 shots (main 739.7 s, trailer 60.0 s), exit 0 | 0.1 s |
| `uv run python -m film.subs check film/subs/ --fps 30` | PASS: 8 files, 830 cues, 652 warnings (reading-speed warnings, same class as before), exit 0 | 0.06 s |

## Criteria

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | Sources: the three pages confirm the quoted sentences, publisher, dates and figures; new ids next free after S-r10-056; access time recorded | **PASS** | Fetched 11 Nov 2026. Argaam ar (id 1576375): headline «ولي العهد: بحلول عام 2030 نريد أن يصل عدد سكان المملكة من 50 إلى 60 مليون نسمة», date 2022/07/26, body «25 مليون منهم سعوديون و25 مليون وافد», «حديثه مع عدد من الصحافيين بعد إعلان تصاميم ذا لاين»; no 2040 / 100 million on the page. Argaam en (id 1576399): "Crown Prince expects Saudi Arabia's population to reach 50-60 million by 2030", 26/07/2022, "with half being foreigners", "Speaking to reporters after unveiling the designs of The Line project"; no 2040. France 24: "Issued on: 27/07/2022", "© 2022 AFP", dateline "Jeddah (Saudi Arabia) (AFP)", "The goal for 2030 is to have 50 million people -- half Saudis and half foreigners -- living in the kingdom", "By 2040 the target is 100 million people, he said.", "In a presentation Monday night" (no "journalists"). All match `docs/sources/r10.csv` rows 26 (S-r10-025), 106 (S-r10-057), 107 (S-r10-058) and `docs/sources/r10-notes.md` v1.1 lines 71-90. Highest id before this milestone S-r10-056 (row 105); new ids 057 and 058. Access "2026-11-11 (00:55 AST)" in all three rows. S-r10-025 status "verified (corroboration only)". |
| 2 | m-03-03 (en, ar) and sh-03-02 caption state The Line launch July 2022, told journalists, 50 to 60 million by 2030, about half Saudis, with the qualifier; traced to S-r10-057; Arabic rules | **PASS** | `film/script/lines.csv` m-03-03: en text "After The Line launch in July 2022, the Crown Prince told journalists the aim is 50 to 60 million people in the Kingdom by 2030, about half Saudis. Remarks, not a published programme target."; ar text «وبعد إطلاق تصاميم ذا لاين في يوليو 2022، قال ولي العهد للصحفيين إن الهدف إن عدد سكان المملكة يوصل بين 50 و60 مليون بحلول 2030، ونصهم تقريباً سعوديين. وهذي تصريحات، مو هدف منشور في برنامج رسمي.»; sources `S-r10-057; S-r10-058; S-r10-025; doc:docs/sources/r10-notes.md`; figure_values `2022; 50; 60; 2030`; ar native_review = pending. `film/storyboard/shots.yaml` sh-03-02 on_screen_text en/ar carry the same statement and the qualifier ("remarks, not a published programme target" / «تصريحات، مو هدف منشور في برنامج رسمي»), data_source `S-r10-057; S-r10-058; S-r10-025; ...`. Tashkeel: every Arabic word in speech_text is vowelled except مليون and digits (allowed exceptions); `strip_tashkeel(speech_text) == strip_tashkeel(text)` True under the project rule (`film/script.py:161-188`; the only raw difference is the tanween the plain text itself carries on تقريباً). `film/storyboard/ar-rewords.csv:42` logs the m-03-03 rewrite. Read-back `film/voice/readback/main-ar.csv:22`: nabrah / Abdullah, CER 0.059, figures 2022 / 50 / 60 / 2030 heard as written; `main-en.csv:22`: elevenlabs / George, CER 0.000. |
| 3 | No "100 million", "2040", «100 مليون» in main outputs | **PASS** | grep count 0 in: `film/script/lines.csv` main rows (text, speech_text, on_screen_label; incl. Arabic-Indic digits), `film/script/main.en.md`, `main.ar.md`, `film/storyboard/shots.yaml` main on_screen_text/visual/data_source, `film/subs/main.{en,ar}.{srt,vtt}`, `film/assemble/renders-main-{en,ar}.csv`, the embedded `0:s:0` tracks extracted with ffmpeg from `film/renders/out/ksa-rail-twin-main-{en,ar}.mp4` (362 / 402 cue lines; new text present at en line 224, ar line 232), and `pdftotext` of `film/renders/out/script/main.{en,ar}.pdf` (new text at en line 67, ar lines 81-87). Only the before/after edit logs (`story-edits.csv`, `caption-edits.csv`, `ar-rewords.csv`) and the superseded source note row 15 keep the old wording. |
| 4 | Only m-03-03 audio changed; George (en), Nabrah Abdullah (ar) | **PASS** | `git diff 65e03be HEAD -- film/voice/timing/*`: main-en.csv and main-ar.csv each 1 row changed (m-03-03; sha a83abb53… → d0311f9c…, 4bd61b67… → faadaaa0…); trailer-en.csv and trailer-ar.csv unchanged. All 158 WAVs under `film/audio/narration/<cut>-<lang>/` hashed: 158 match their timing-CSV sha256, 0 mismatches; m-03-03 en = d0311f9c5a22a847…, ar = faadaaa088d48533…. Voices in the changed rows: elevenlabs / George (voice id JBFqnCBsd6RMkjVDRZzb, same as before); nabrah / Abdullah (same as before). |
| 5 | Trailers byte-identical | **PASS** | `shasum -a 256`: en 81fa64ec4dd12f3b06150f3c0cae9e7a78bf2caceaa7a611f1c0c50b71cc8701, ar 21df620d1994ec759d539349eab5b5f85dde95ae449191633a1eb98d2504407e. |
| 6 | Both main cuts re-assembled; durations, SHA-256, loudness, edit lists, sh-03-02 renders | **PASS** | ffprobe: main-en 870.333 s, main-ar 1005.333 s. SHA-256 en 06b6b3327b551eeeeed87565830a1db4a0e909669cd34773edda9826c861521f, ar 4cae0dfe950bed285be66688a3ebc46e9536885883ec95a919e75c4afd6a52b8 = `docs/film.md` §00000 full hashes and the status block. `film/assemble/loudness.csv`: main en −16.09 LUFS / −1.80 dBTP, main ar −16.03 / −1.74 (final_mp4). EDL diff vs 65e03be: only sh-03-02 duration changed (en 14.6333 → 15.0, ar 17.4333 → 18.7333); 64 shots before and after, none added or removed. `film/renders/main-en/sh-03-02.mp4` 15.000 s, `main-ar/sh-03-02.mp4` 18.733 s = EDL and `renders-main-*.csv:18` (figures traced "2022, 50 60 2030"). Superseded cuts, shots and PDFs kept under `film/renders/_superseded/*.pre-fix-mbs-quote-20261111.*`. |
| 7 | Spend ≤ USD 1 ElevenLabs this run; combined 6.98 ≤ 48 / 60; no keys; .env untracked | **PASS** | `docs/cost-log.csv` rows 108-109 (track "… FIX_MBS_QUOTE"): ElevenLabs 0.04, Nabrah 0.02. Sum of all PAID rows: ElevenLabs 3.13, Nabrah 3.85, combined 6.98 (matches the status block and film.md). `git grep` for sk_/sk-/API_KEY=/AKIA patterns: no hits. `git ls-files | grep ^.env`: none; `.gitignore:18-19` ignores `.env` and `.env.*`; no `.env*` file in the worktree. |
| 8 | story-edits logs m-03-03 en+ar; film.md v1.7 with new hashes/durations; status block ends `FIX_MBS_QUOTE: done`; last line `R10: blocked - CP9 review required`; no R10 done; no merge/tag/push | **FAIL** | story-edits.csv:32-33 log m-03-03 en and ar (PASS). `docs/film.md` v1.7, §00000 with the new SHA-256 and 870.3 s / 1005.3 s (PASS). Last line of `docs/status/r10.md` is `R10: blocked - CP9 review required`; the block never claims R10 done (PASS). No merge commits in 65e03be..HEAD; tags are r7, r8, r8.1, r9, session1-pilot only; `main` is at efb6157 (not merged); no push in any commit message (PASS). **FAIL: `grep -n "FIX_MBS_QUOTE:" docs/status/r10.md` returns nothing (exit 1).** The block (lines 353-379) ends with the "Paid TTS (final)" paragraph and goes straight to the R10 line; the required end line `FIX_MBS_QUOTE: done` (brief item 5; coordinator addendum: "Write `FIX_MBS_QUOTE: done` … at the end of the status block") is absent. The orchestrator greps for that line (CLAUDE.md, Workflow), so the milestone is not machine-readable as done. |
| 9 | Lint, format, tests, docver, manifest, script/shots/subs checks | **PASS** | See the command table: all exit 0; 989 passed, 69 skipped, 0 failed. |
| 10 | No content from the author's company, no absolute home paths in changed files, no advocacy; line non-partisan and attributed | **PASS** | 32 files changed in 65e03be..HEAD; `grep -l "/Users/[a-z]"` on them: none; private-list grep: none. The line attributes the figures to the Crown Prince's remarks to journalists with the qualifier "Remarks, not a published programme target" in both languages; no "will", no endorsement; the shot shows "No portrait, no emblem". |

## Failures

**F1 (item 8): the status block has no `FIX_MBS_QUOTE: done` line.** `docs/status/r10.md` lines 377-379 read: the "Paid TTS (final)" paragraph, a blank line, then `R10: blocked - CP9 review required`. `grep -n "FIX_MBS_QUOTE:" docs/status/r10.md` → no match. The previous milestone shows the expected form at line 351 (`FIX_FILM_STORY: done`). Every substantive deliverable of the milestone checks out, but the brief makes this line the completion signal and the verifier is told not to soften a FAIL because the fix is small.

## Notes (not failures)

- Arabic read-back heard «وهذه تصريحات مهدف منشور» for «وهذي تصريحات، مو هدف منشور» (CER 0.059); the figures are heard correctly, which is what the digit audit requires. Native review remains pending for CP9, as recorded.
- The France 24 copy describes the occasion as "a presentation Monday night" and does not say "journalists"; the film follows the Saudi source (Argaam) for "told journalists", as the notes state. Consistent with the brief ("state only what a Saudi source confirms").
- `film.subs check` reports 652 warnings (reading-speed class), the same class the builder reports as unchanged; not re-counted against 65e03be.

## Fixes (in order)

1. Append `FIX_MBS_QUOTE: done` as the last line of the `## FIX_MBS_QUOTE` block in `docs/status/r10.md`, immediately before the blank line and `R10: blocked - CP9 review required` (keep that as the file's last line); bump the file's version line.
2. Nothing else is required for this milestone.
3. (Optional, for CP9) have the native reviewer confirm «مو هدف» is clearly separated in the Nabrah take, since the read-back merged it.

## Pass 2 (11 Nov 2026, HEAD 55bd54e; scope: F1 and the no-regression checks only)

Pass-1 findings above are kept as written at e4d9e84. Pass 2 re-checked only the four items in the coordinator's brief.

| # | check | verdict | evidence |
|---|---|---|---|
| P2-1 | F1: `docs/status/r10.md` has a plain `FIX_MBS_QUOTE: done` line at the end of the FIX_MBS_QUOTE block; last line still `R10: blocked - CP9 review required`; version header bumped; no `R10: done` | **PASS** | `grep -n "^FIX_MBS_QUOTE: done$" docs/status/r10.md` → `377:FIX_MBS_QUOTE: done` (start of line, no markup). `git diff e4d9e84 HEAD -- docs/status/r10.md`: the block gains a `make test` paragraph, a "Verifier" paragraph and the end line at lines 373-377, followed by a blank line and the unchanged last line `R10: blocked - CP9 review required` (line 379). Header line 1: v1.7 / 10 Nov 2026 → v1.8 / 11 Nov 2026 with the v1.8 note "FIX_FILM_STORY and FIX_MBS_QUOTE blocks, verifiers, end lines". `grep -n "^R10: done" docs/status/r10.md` → no match (exit 1). |
| P2-2 | Nothing else changed since e4d9e84 beyond `docs/status/r10.md` and this report | **PASS** | `git diff --stat e4d9e84 HEAD`: `docs/status/r10.md` 8 (+7/−1), `docs/status/verify-FIX_MBS_QUOTE.md` 53 (+53); 2 files changed, 60 insertions, 1 deletion. `git status --porcelain` empty before this report was edited. |
| P2-3 | `uv run python -m common.docver check docs prompts .claude film/script` | **PASS** | `docver OK: 404 files`, exit 0, 0.18 s (403 at pass 1 + this report). |
| P2-4 | Trailers byte-identical | **PASS** | `shasum -a 256`: en 81fa64ec4dd12f3b06150f3c0cae9e7a78bf2caceaa7a611f1c0c50b71cc8701, ar 21df620d1994ec759d539349eab5b5f85dde95ae449191633a1eb98d2504407e; identical to pass 1 and to the prefixes in the brief (81fa64ec4dd12f3b / 21df620d1994ec75). |

F1 is closed. No new finding. The pass-1 items 1-7, 9 and 10 were not re-run; P2-2 shows no file in their scope changed since e4d9e84. The optional note on the Nabrah take («مو هدف») stands for CP9 native review.

VERDICT: PASS

VERIFY_FIX_MBS_QUOTE: PASS
