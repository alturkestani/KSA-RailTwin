> **Document version:** docs/status/verify-FIX_MBS_TITLE.md v1.0 | 11 Nov 2026 | Author: red-team-verifier (`claude-fable-5-1`) | Status: verified

# VERIFY_FIX_MBS_TITLE (r10 worktree; baseline c65cba9; run commits 5f1aff3, b59f92f, 4048958)

Read: `prompts/FIX_MBS_TITLE.md` (incl. coordinator addendum), `docs/status/r10.md` FIX_MBS_TITLE block, `docs/film.md` §000000, `git diff c65cba9..HEAD`. Verifier wrote only this file; nothing fixed, committed, tagged, pushed or contacted. Tree was clean at start (`git status --porcelain` empty); HEAD = 4048958.

## Commands run

| command | result |
|---|---|
| `cmp ../../prompts/FIX_MBS_TITLE.md prompts/FIX_MBS_TITLE.md` | identical |
| `make test` (ruff check, ruff format --check, pytest -q, docver check, manifest verify) | `All checks passed!`; `806 files already formatted`; pytest green (dots and skips only, 0 failures); `docver OK: 405 files`; `manifest OK: 388 rows`; EXIT=0 |
| `uv run python -m film.script validate film/script` | PASS, 158 lines (main/ar 11:43, main/en 12:02); 2 warnings, one of them `WARN main/en: spoken estimate 722.0 s over 720 s within the recorded allowance of 2.0 s (FIX_MBS_TITLE: ...)` |
| SHA-256 of all narration WAVs vs `film/voice/timing/*.csv` at HEAD and c65cba9 (script, 158 timing rows) | see C4 |
| `shasum -a 256` + `ffprobe` on the four cuts; `ffmpeg -map 0:s:0 -f srt` on all four; `pdftotext -layout` on the four script PDFs; `ffmpeg -af ebur128` on both main cuts | see C3, C5, C6 |

## Criteria

| # | criterion | verdict | evidence |
|---|---|---|---|
| C1 | Prompt byte-identical to main checkout | PASS | `cmp` silent; committed first in 5f1aff3 |
| C2a | m-03-03 en text == Tariq's EN line | PASS | `film/script/lines.csv` row (main,en,m-03-03): exact string equality checked by script |
| C2b | m-03-03 ar text == Tariq's suggested line | PASS | row (main,ar,m-03-03): exact equality |
| C2c | ar speech_text has full tashkeel incl. «صَاحِبُ السُّمُوِّ الْمَلَكِيِّ الْأَمِيرُ مُحَمَّدُ بْنُ سَلْمَانَ», strips to the text | PASS | substring present; `script.strip_tashkeel(speech_text) == strip_tashkeel(text)` (tests/test_film_mbs_title.py::test_m_03_03_full_honorific passes; my own strip differed only on تقريباً tanween placement, pre-existing since FIX_MBS_QUOTE) |
| C2d | native_review pending | PASS | ar row `native_review = pending`; en `n/a` (unchanged convention) |
| C2e | figures, sources, qualifier unchanged vs c65cba9 | PASS | both rows `figure_values = 2022; 50; 60; 2030`, `sources = S-r10-057; S-r10-058; S-r10-025; doc:docs/sources/r10-notes.md`, `on_screen_label` empty; identical in `git show c65cba9:film/script/lines.csv`; "Remarks, not a published programme target." / «وهذي تصريحات، مو هدف منشور في برنامج رسمي.» retained. S-r10-057/058 (Argaam, 26 Jul 2022, `docs/sources/r10-notes.md` L77–78) attribute the remarks to the Crown Prince, so the added name is sourced |
| C3a | No bare «ولي العهد» / "Crown Prince" without the name in lines.csv (main), main.en.md, main.ar.md, shots.yaml captions, main.*.srt/vtt | PASS | tashkeel-insensitive scan: every occurrence adjacent to «محمد بن سلمان» / preceded by "His Royal Highness" and followed by "Mohammed bin Salman" (subtitle cues only break the name across a line: en cue 00:03:4x "His Royal Highness Crown Prince Mohammed / bin Salman", ar cue 52 00:04:03.887 «...الأمير محمد بن / سلمان، ولي العهد،») |
| C3b | Embedded mov_text tracks of main-en / main-ar | PASS | extracted (868 / 897 lines); same single cue each, full name present |
| C3c | Script PDFs main.en.pdf / main.ar.pdf | PASS | pdftotext: en "His Royal Highness Crown Prince Mohammed bin / Salman told journalists"; ar glyph run split by pdftotext but reads «صاحب السمو الملكي الأمير محمد ب سلما ، ولي العهد»: name present, one occurrence |
| C3d | Trailers and trailer scripts: no mention, unchanged | PASS | 0 occurrences in trailer.{en,ar}.md, trailer subs, embedded trailer tracks, trailer PDFs; `git diff --stat c65cba9..HEAD -- film/script/trailer* film/subs/trailer* film/assemble/*trailer* film/voice/*/trailer*` empty |
| C4 | Only m-03-03 audio changed | PASS | 158 timing rows at HEAD vs c65cba9: only `main-en/m-03-03` and `main-ar/m-03-03` sha256 differ; every current WAV matches its HEAD timing hash (0 mismatches); every WAV other than the two m-03-03 files matches its c65cba9 hash. New hashes: en `1b00723a40b0353d…` 15.418 s, ar `06fac9fb0fa98953…` 20.840 s. Note: folders also hold macOS `._*.wav` AppleDouble files and one untracked `m-06-07.wav` per main folder that are in no timing table (gitignored, not used by the assembler) |
| C5 | Trailers byte-identical | PASS | en `81fa64ec4dd12f3b06150f3c0cae9e7a78bf2caceaa7a611f1c0c50b71cc8701` (77.6 s, mtime 10 Nov 22:37); ar `21df620d1994ec759d539349eab5b5f85dde95ae449191633a1eb98d2504407e` (86.9 s, mtime 8 Nov 03:23) |
| C6 | Main cut SHA-256, durations, loudness match film.md §000000 and loudness.csv | PASS | en `540c5e41094ed2ce7f2d71be8ed3a44ce89407e38059ccc7eba378c31ada150e`, ffprobe 872.166667 s; ar `391f72bfcedf94d65ace316e2c65bfa73759c93398a80fed36f962fd3a5751bf`, ffprobe 1008.833333 s; ebur128 integrated −16.1 / −16.0 LUFS (loudness.csv −16.09 / −16.03; film.md same). sh-03-02 renders ffprobe 16.833 / 22.233 s = renders-main-*.csv and EDL |
| C7 | Edit logs | PASS | story-edits.csv: 2 new m-03-03 rows (en, ar) before/after with reason "FIX_MBS_TITLE…"; caption-edits.csv: 2 new sh-03-02 rows (en, ar); ar-rewords.csv: 1 new m-03-03 row (old → new, tashkeel note, native_review pending, digits identical) |
| C8 | Read-back | PASS | readback/main-en.csv m-03-03 CER 0.000, text contains "His Royal Highness Crown Prince Mohammed bin Salman"; readback/main-ar.csv m-03-03 CER 0.009 (was 0.059), all nine tokens صاحب السمو الملكي الأمير محمد بن سلمان ولي العهد present in order |
| C9 | Spend | PASS | cost-log.csv PAID rows labelled FIX_MBS_TITLE: ElevenLabs 0.05 (≤ 1), Nabrah 0.03. Sum of all 33 PAID rows: combined **USD 7.06** (ElevenLabs 3.18, Nabrah 3.88); alert 48 not reached. No key patterns in the diff; `git ls-files` has no `.env` |
| C10 | `duration_allowance` narrow, recorded, transparent | PASS (judgement) | meta.yaml: single key `main/en`, 2.0 s, named reason, explanatory comment; script.py warns only when `hi < total <= hi + allowance`, errors beyond (test_duration_allowance_is_narrow exercises +0.5 s → error). Keeping Tariq's verbatim wording is consistent with the brief: the brief fixes the wording and bars changes to any other line, and the 720 s figure is a planning estimate (actual cuts 14:32 / 16:49 are already a CP9 item). The allowance is listed for CP9 in r10.md and film.md |
| C11a | make test green | PASS | EXIT=0 (see commands) |
| C11b | no absolute home paths / IS content / secrets in tracked changes | PASS | `git diff c65cba9..HEAD` greps for `/Users/[a-z]`, "the private-list terms", key patterns all empty |
| C11c | no merge, tag, push | PASS | 0 merge commits in c65cba9..HEAD; no tag at HEAD; no `git push` in changed files |
| C12 | Status block content | PASS (with note) | r10.md v1.9 FIX_MBS_TITLE block: numbers (15.418 / 20.840 s; 872.2 / 1008.8 s; −16.09 / −16.03; SHA prefixes; 0.05 + 0.03; 7.06) all match what I measured. By design the block has no `FIX_MBS_TITLE: done` line and the file's last line is not yet `R10: blocked - CP9 review required`: both are to be written by the builder after this report (launch message) |

## Spot-check (visual)

Frames at 8 s of `film/renders/main-{en,ar}/sh-03-02.mp4`: both captions fit the side card with the full title, no portrait or emblem, OSM/Copernicus credit and layer legend present. No new figures were introduced in this run, so the figure spot-check is the FIX_MBS_QUOTE one (S-r10-057/058 re-read above).

## Failures

None.

## Observations (not failures)

1. `film/audio/narration/*` contain 160 macOS `._*.wav` AppleDouble files (ExFAT artefacts) and an orphan `m-06-07.wav` in each main folder; harmless and gitignored, but a `find -name '._*' -delete` before the next hash tally would make the "160 WAVs" count exact.
2. The builder's status block says the honorific read-back segment spans 3.16–8.00 s; I verified token presence, not timestamps.
3. The ar `speech_text` carries tanween before the alef (تَقْرِيبًا) while the text has it after (تقريباً); the repo's `strip_tashkeel` treats them as equal. Pre-existing, cosmetic.

## New cut hashes and durations (for the record)

- main-en: `540c5e41094ed2ce7f2d71be8ed3a44ce89407e38059ccc7eba378c31ada150e`, 872.166667 s (14:32), 258,445,585 bytes
- main-ar: `391f72bfcedf94d65ace316e2c65bfa73759c93398a80fed36f962fd3a5751bf`, 1008.833333 s (16:49), 282,901,348 bytes
- trailer-en: `81fa64ec4dd12f3b06150f3c0cae9e7a78bf2caceaa7a611f1c0c50b71cc8701`, 77.6 s (unchanged)
- trailer-ar: `21df620d1994ec759d539349eab5b5f85dde95ae449191633a1eb98d2504407e`, 86.9 s (unchanged)

VERIFY_FIX_MBS_TITLE: PASS
