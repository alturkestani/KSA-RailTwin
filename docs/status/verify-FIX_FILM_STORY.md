> **Document version:** docs/status/verify-FIX_FILM_STORY.md v1.1 | 11 Nov 2026 | Author: red-team-verifier (v1.1: pass 2 after commit 95f9e8a; v1.0: pass 1, FAIL F1) | Status: verified

# VERIFY_FIX_FILM_STORY (r10, commits 84bb1ac..HEAD; pass 1 at 5ce5580, pass 2 at 95f9e8a)

**Pass-1 verdict (5ce5580): FAIL (F1).** Pass-1 sections are kept below unchanged; the pass-2 section at the end supersedes the verdict.

Read-only pass on the r10 worktree, 11 Nov 2026, `RAILTWIN_RUNS_ROOT=~/Documents/Projects/KSA-RailTwin/runs`. Tree clean (`git status --porcelain` empty), no tag at or since 84bb1ac, no remote configured. Logs: `logs/verify-fix-film-story-maketest.log`, `logs/verify-fix-film-story-loudnorm.log`.

## Commands (exit codes, timing)

| command | result |
|---|---|
| `make test` (ruff check + format, pytest, docver, manifest) | exit 0, 57 s: "All checks passed!", docver OK 401 files, manifest OK 388 rows |
| `uv run pytest -q tests/test_film_story.py` | 7 passed |
| `uv run python -m film.script validate film/script/` | PASS, 158 lines (main 68 + 68; 1 pre-existing trailer/ar warning) |
| `uv run python -m film.shots check film/storyboard/shots.yaml --lines film/script/lines.csv` | PASS, 75 shots (64 main + 11 trailer) |
| `uv run python -m film.rights check film/rights_log.csv` | PASS, 66 rows |
| `uv run python -m film.subs check film/subs/ --fps 30` | PASS, 8 files, 830 cues (652 reading-speed warnings, pre-existing pattern) |
| `uv run python -m film.render trace --cut main --lang en` / `--lang ar` | "0 figure(s) not found" each, **but the manifest it reads has 58 rows, not 64 (see F1)** |
| `ffmpeg loudnorm print_format=summary` on both main MP4s | en −16.1 LUFS / −1.8 dBTP / LRA 4.5; ar −16.0 LUFS / −1.7 dBTP / LRA 4.1 |

## Criteria

| # | item | PASS/FAIL | evidence |
|---|---|---|---|
| 1 | prompt byte-identical to main | PASS | `cmp` silent; sha256 18d9cf473bbafda8…b52e4 on both `prompts/FIX_FILM_STORY.md` and `../../prompts/FIX_FILM_STORY.md` |
| 2 | every new figure traced; BCRs recomputed | **FAIL (F1: manifest)**, figures themselves PASS | Recomputed: `runs/cba/CBA-S1-committed-programme/results.json` results[25] (`un_wpp_medium`, 60, `greenbook_2026`) bcr.P50 = 0.30572 → 0.3 (m-08-01); `runs/r6/top5/top5.csv` bcr_p50_medium S6-L2 5.9618 → 6 (m-08-02), S6-L1 2.3293 → 2.3 (m-08-03), S6-L3 1.1201 → 1.1 (m-08-04); `runs/r6/l6/score/S6-L6.csv` bcr_p50_medium 0.060972 → 0.06 (m-08-19); `docs/rj-routes-study.md` §8a BCR P50 0.23/0.18/0.23/0.22/0.24 → 0.2 (m-08-08); `runs/r6/l6/national_reach.json` layouts.*.layout.120 = 32,739,046, S1.120 = 26,096,670 → 32.7 M / 26.1 M (m-08-17); `cities/ksa/corridors/trunk_gap/S2-trunk_gap-tabuk-sakaka.yaml` length_km 458.85 and `docs/r6-l6-connected.md` §2 "458.9" → caption 458.9, spoken "about 460" (m-08-16); 16 options / 18 cities: `docs/r6-l6-connected.md` §2 "Result: S6-L6 = 16 library options … all 18 required cities" (m-08-15); 10 km: `docs/coverage.md` rows Tabuk l.105, Abha l.83, Khamis Mushayt l.93, Jazan l.135, Najran l.141 all `served` = 0 (within 10 km of an existing station, A-screen-004) and `docs/network-evaluation.md` l.257 (m-08-14). Qualifiers checked: "even at high cost it pays back" = top5 S6-L2 npv_p90cost low/med/high 3,986 / 4,771 / 5,589 > 0; "no longer pays back in two of three" = S6-L1 −2,958 / −724 / +1,631; "does not pay back in any case" = S6-L3 −21,745 / −19,225 / −16,624. Geography of m-08-16: Jouf–Sakaka spur = `S3-branch_spur-sakaka` (57.1 km); Muwai on the Landbridge = `S3-branch_spur-bisha` hosts on `landbridge:muwai`; Abha–Baysh–Jazan = `S4-commuter_belt-abha-khamis-mushait-135` (to Baysh, 103.9 km) + `S4-commuter_belt-jazan-315` (to Baysh, 60.4 km). S-r10-050..056 present in `docs/sources/r10.csv` l.99–105 with repo-path locators. `trace_figures` run by hand on sh-08-15..20: found 10 / 18,16 / 458.9 / 32.7,26.1 / — / 0.06, 0 missing. No invented number found. |
| 3 | BCR sentences match after rounding; rounding-log complete | PASS | `film/storyboard/rounding-log.csv` 9 rows: exact 0.3057 / 5.9618 / 2.3293 / 1.1201 / 0.18–0.24 / 458.85 / 32739046 / 26096670 / 0.0610 → 0.3 / 6 / 2.3 / 1.1 / 0.2 / 460 / 32.7 M / 26.1 M / 0.06, each with line id, case ("BCR P50 of draws; UN WPP medium; 60 years; Green Book 2026" or the RJ/L6 case) and source path. All round correctly (0.061 → 0.06 by stated decision). |
| 4 | cities not routed: claim not falsified; film says it; list for Tariq | PASS | Searched `docs/report/**`, `docs/rj-routes-study.md`, `docs/extra-travel-study.md`, `docs/commute-test.md`, `docs/network-evaluation.md`, `docs/r6-l6-connected.md`, `runs/r6/l6/**` (layout, search, attachments, compare, national_reach, score/*), `runs/access/*` (reached.parquet = population bands by metro; `tabuk/isochrone_in_vehicle.geojson`), `runs/r6/l6/score/inputs/*` (scalars.parquet only): no door-to-door rail time from Tabuk, Abha, Khamis Mushait, Najran or Jazan to a big city. `docs/commute-test.md` l.130/138/139 hold town→anchor times (e.g. Baysh→Jazan belt 315: 75 min door-to-door), the reverse direction, not city→big-city. Film: m-08-18 en "The study did not route those trips", ar «الدراسة ما حسبت هالمشاوير»; sh-08-19 caption both languages; status block "Cities the study did not route (for Tariq)" lists the five. |
| 5 | routes from modelled alignments, no straight lines | PASS | `film/sim_main.py` l.136–148 `routed_lines` skips `kind == "straight_sketch"`, keeps every vertex of the rest; alignment files hold only `routed` (Tabuk–Sakaka 221 vertices, Abha–Bisha 131, Taif–Bisha 229, Abha belt 114, Jazan belt 49) plus a 2–3-point `straight_sketch`; `corridor_geom` l.151 reads `runs/align/corridors-s1/<id>/alignment.geojson` (v2 first); L6 scene l.2382–2385 reads `runs/r6/l6/L6.layout.yaml` through `corridor_geom`. Frames (ffmpeg → PNG, viewed): main-en/sh-08-17 at 5 s (Tabuk–Sakaka bending to Al-Jouf, spur to North Line) and 14.3 s (Taif–Bisha–Abha–Najran and the escarpment descent to Jazan, all curved), main-ar/sh-08-17 at 14.3 s (same, Arabic caption/legend), main-en/sh-08-16 at 8.5 s (16 additions, no straight segments), main-en/sh-04-05 at 8 s (no sketch lines). |
| 6 | finance-term lines gone | PASS | Regex (net present value, NPV, present value, robust value, fiscal, net cost, صافي القيمة الحالية, المالية العامة, القيمة الحالية) over `lines.csv` main text + speech_text (136 rows) and `shots.yaml` main on_screen_text/source_caption: 0 hits. `sim_main.py` on-screen labels for re-rendered shots: "benefits minus costs" (l.1187, 1782), "one: pays back its cost" (l.1859, 1960, 2181, 2579), "in today's money, 60 years" (l.2086); remaining matches are column names/docstrings. Judgement notes: "P10–P90" in sh-08-06's source caption and "standard appraisal values" (m-08-06, unchanged) are the only analyst terms left; not finance terms the brief names. |
| 7 | m-08-06 listed; meaning/figures/sources unchanged | PASS | `story-edits.csv` kind `meaning_unchanged` (en, ar); status block "m-08-06 is listed explicitly: meaning unchanged"; lines.csv diff for m-08-06: en only `text`, ar `text`/`speech_text`/`est_seconds`; `sources` and `figure_values` (60; 2.3; 19.3; 0.6; 7.4) identical to 84bb1ac. |
| 8 | every removed/rewritten line before → after, both languages | PASS | lines.csv vs 84bb1ac: exactly 9 rewritten + 6 new per language, no removals; all 30 `story-edits.csv` rows' `before` equal the 84bb1ac text and `after` equal HEAD text byte for byte; the status-block table carries the same 30 rows. |
| 9 | Arabic: rewords, tashkeel, read-back, native_review, say overrides | PASS | `ar-rewords.csv`: 18 FIX_FILM_STORY rows (15 text + 3 say); 15 changed ar rows `native_review = pending`; tashkeel: 453 Arabic tokens in the 15 speech_text rows, 0 bare outside مليون/مليار/digits; `film/voice/readback/main-ar.csv` rows for all 15 (CER 0.000–0.093); `say.csv` m-08-03/m-08-15/m-08-19 (ar) equal speech_text with harakat stripped (True ×3). |
| 10 | George only; only changed lines re-voiced | PASS | `film/voice/timing/main-en.csv`: 68 rows, all (George, JBFqnCBsd6RMkjVDRZzb, eleven_multilingual_v2); sha256 differs vs 84bb1ac only on m-04-07, m-08-01..08; m-08-14..19 added. main-ar: engine `nabrah` ×68, voices Daniah/Norah/Abdullah; same 9 + 6 lines; untouched rows changed only in the new empty `voice_id`/`model` columns. |
| 11 | Arabic credits without ElevenLabs | PASS | `credits_lines('ar')` voices line «الأصوات: نبرة (الأصوات العامة دانية ونورة وعبدالله)», no ElevenLabs/George; `credits_lines('en')` keeps "ElevenLabs voice George (English); Nabrah …". Frame main-ar/sh-08-14 at 6/10/14/18 s shows that line and the single closing notice. |
| 12 | loudness, durations, SHA, EDL | PASS | Measured: en −16.1 / −1.8, ar −16.0 / −1.7 (within ±0.5 of −16; TP ≤ −1.5); `loudness.csv` final_mp4 rows −16.09/−1.80 and −16.03/−1.72 agree. ffprobe 869.967 s / 1004.033 s; SHA-256 aaca43afbcdf5b98 / 4059f6d34e867878; sizes 257,762,974 / 282,075,199 B: all as in film.md §0000 and the status block. EDL: 64 shots each, max |ffprobe − duration_s| = 0.000 s. |
| 13 | paid TTS within limits; keys | PASS | `docs/cost-log.csv` PAID rows summed: ElevenLabs 3.09 (this run 0.65 + 0.03 = 0.68 ≤ 5; ≤ 15), Nabrah 3.83, combined 6.92 (< 48). Tally before the first call in commit 8be4347 (23:33:11) and after each batch in the status block. Key-pattern grep over `git ls-files`: empty; `.env` untracked, `.gitignore` l.18–19. |
| 14 | trailers untouched | PASS | SHA-256 trailer-en 81fa64ec4dd12f3b, trailer-ar 21df620d1994ec75; lines.csv trailer rows identical; shots.yaml 11 trailer shots identical; `git diff --stat` on film/subs and film/assemble shows only main-* files. |
| 15 | old cuts kept | PASS | `film/renders/_superseded/ksa-rail-twin-main-en.pre-fix-film-story-20261110.mp4` 4b9aadf29ec9e857 (236.8 MB), `-ar.…` b6fa4e80b0a43176 (257.8 MB). |
| 16 | single closing notice; no refrain | PASS | `film.shots check` PASS; refrain regex over the 15 changed/new lines (both languages) and 16 changed/new captions: 0 hits; no notice-like text on any main shot but sh-08-14; footers `none`. |
| 17 | labels, no advocacy, no IS content, no home paths, no model names | PASS | sh-08-16..20 `source: S6-L6 (comparison layout)`; m-08-15 "As a comparison, not a recommendation"; RJ labels in the status block; advocacy grep 0; "the private-list terms" grep over the 34 changed files 0; `/Users/[a-z]` grep over changed files 0; model-name grep in film text: only the pre-existing "Built with Claude (Anthropic)" credit (unchanged since 84bb1ac). |
| 18 | make test green; validators; film.md v1.6; status last line | PASS | See the commands table; `docs/film.md` header v1.6 (11 Nov 2026); last line of `docs/status/r10.md` = `R10: blocked - CP9 review required`; `FIX_FILM_STORY: done` absent as expected. |

## Failures

**F1 (item 2, evidence of tracing): the render manifests omit the six new shots, so the builder's "film.render trace 0 figures not found" covers 58 of 64 shots.** `film/assemble/renders-main-en.csv` and `renders-main-ar.csv` have 59 lines each (header + 58 rows, sh-01-01 … sh-08-14; `grep -c "sh-08-1[5-9]\|sh-08-20"` = 0). `film.render trace` (film/render.py l.1016–1027) only re-traces the rows already in that file, so sh-08-15 … sh-08-20 and their on-screen figures (10 km; 18 cities, 16 additions; 458.9 km; 32.7 M, 26.1 M; 0.06) were never written to the project's figure-trace record. The status block states "64 shots per main cut … `film.render trace` 0 figures not found (en, ar)" and film.md §0000 relies on the same claim: the number is what the tool printed, but it was not measured for the new shots. The figures themselves are correct (recomputed above; `trace_figures` by hand finds 0 missing on all six), so this is an evidence gap, not a wrong number; the handoff contract still requires the file.

## Minor notes (not FAILs)

1. `film/storyboard/rounding-log.csv` m-08-02 says "caption 6.0" and sh-08-02's `visual` says "about 6.0", but the on-screen caption now reads "about 6" (changed by the test fix in 5ce5580): stale note.
2. Status block, "Other decisions", last bullet: "the delivered cuts are longer (14:31 / 16:45)"; the outputs table, film.md and ffprobe say 14:30 / 16:44 (870.0 s / 1004.0 s).
3. `trace_figures` does not pick up the single digit "6" in sh-08-02's caption (traces only 0.8 and 5.3); verified by hand as round(5.962).
4. English credits still name Nabrah although no Nabrah voice is in the English cut (builder flagged it for CP9; not in this brief).
5. `docs/cost-log.md` has no Claude-cost row for the FIX_FILM_STORY run yet (the launcher writes it after the run).
6. `docs/commute-test.md` holds town→anchor door-to-door times in the Jazan and Asir belts (e.g. Baysh → Jazan belt 315, 75 min); they are not city→big-city times, so the film's statement stands, but the status list for Tariq could say so to pre-empt the question.
7. Arabic read-back quirks already flagged by the builder for ear checks (m-08-19 opening «وثمن» heard as "8"; m-08-16 opening «فيها»); native review of every changed Arabic row still pending.

## Spot-check sample

Not a register milestone (no candidate, cost or benchmark rows changed); the whole set of new and rewritten figures (15 lines × 2 languages, 16 captions, 9 rounding rows, 7 source rows) was checked against the run files and documents listed under item 2 instead of a 10 % sample.

## Three most important fixes

1. Regenerate `film/assemble/renders-main-{en,ar}.csv` with all 64 shots (or append rows for sh-08-15 … sh-08-20) and re-run `film.render trace` for both languages, then restate the trace claim in the status block and film.md §0000 with the shot count it covers.
2. Correct the stale "6.0" notes (rounding-log m-08-02, sh-08-02 `visual`) and the "14:31 / 16:45" sentence in the status block so every number matches the delivered cuts.
3. For CP9: decide on the English credits' Nabrah line and run the native Saudi review of the 15 changed Arabic rows (pending).

(Pass-1 verdict line, superseded: VERDICT: FAIL.)

## Pass 2 (11 Nov 2026, commit 95f9e8a; `git diff 5ce5580..HEAD`)

Scope of the fix commit: 10 files (`docs/film.md`, `docs/status/r10.md`, `docs/status/verify-FIX_FILM_STORY.md` (the pass-1 report, committed by the builder), `film/assemble/renders-main-{ar,en}.csv`, `film/render.py`, `film/storyboard/rounding-log.csv`, `film/storyboard/shots.yaml`, `film/storyboard/storyboard.md`, `tests/test_film_story.py`); nothing outside these. Tree clean before and after every command below; no tag, no remote.

| check | result | evidence |
|---|---|---|
| F1: manifest rows | PASS | `renders-main-en.csv` and `-ar.csv`: 64 rows each; `[shot_id] == [main shots of shots.yaml in file order]` True for both; `output` column has no `missing`. |
| F1: new shots traced, nothing not found | PASS | sh-08-15 `10`; sh-08-16 `18 16`; sh-08-17 `458.9`; sh-08-18 `32.7 26.1`; sh-08-19 (no figure); sh-08-20 `0.06`; `figures_not_found` empty on all 64 rows, both languages. Manifest `duration_s` equals `edl-main-{en,ar}.csv` on all 64 rows (max 0.0003 s); the nine previously stale rows (sh-04-07, sh-08-01..08, e.g. sh-08-01 16.967 → 13.067) now carry the delivered durations. |
| F1: trailer manifests unchanged | PASS | `git diff --stat 84bb1ac..HEAD -- film/assemble/renders-trailer-{en,ar}.csv` empty; after running `film.render trace` for main-en, main-ar, trailer-en, trailer-ar (each "0 figure(s) not found"), `git status --porcelain` empty, so the command is idempotent and the trailer manifests come out byte-identical. |
| F1: `trace` change sound and read-only w.r.t. renders | PASS | `film/render.py` l.1016–1047: builds rows from `_index()` filtered by cut (storyboard order), merges the old row if present, takes `duration_s` from `shot_durations()` (reads `film/assemble/edl-<cut>-<lang>.csv`), sets `output` by `mp4.exists()` only, then `trace_figures`; the only write is `write_manifest` to the CSV. No ffmpeg or render call; `film/renders` untouched (SHA-256 of both main cuts unchanged: aaca43afbcdf5b98 / 4059f6d34e867878 as measured in pass 1, files not in the diff). |
| F1: test | PASS | `tests/test_film_story.py::test_render_manifest_has_every_main_shot` asserts the row ids equal the main shot list and `figures_not_found` empty for en and ar; `make test` pass 2: exit 0, "All checks passed!" (`logs/verify-fix-film-story-maketest-pass2.log`). |
| Minor 1 ("6.0") | PASS | `rounding-log.csv` m-08-02 now "caption 'about 6'"; `shots.yaml` sh-08-02 `visual` and `storyboard.md` row say "middle, about 6"; no "6.0" left for sh-08-02 / m-08-02. |
| Minor 2 (14:31 / 16:45) | PASS | `docs/status/r10.md` l.343 now "(14:30 / 16:44)", matching 870.0 s / 1004.0 s. |
| Minor 3 (single-digit 6 not traced by the tool) | noted, unchanged | Tool limitation; the caption's "about 6" is verified by hand as round(5.962) and is in the rounding log. |
| Minor 4 (English credits name Nabrah) | unchanged, for CP9 | Not in this brief; builder's flag stands. |
| Minor 5 (Claude-cost row) | unchanged, expected | Written by the launcher after the run. |
| Minor 6 (commute-test town→anchor times) | noted, unchanged | Film claim still stands; no change required. |
| Minor 7 (Arabic ear checks, native review) | unchanged, for CP9 | As flagged by the builder. |
| film.md records the fix | PASS | `docs/film.md` §0000 "Checks that changed the first assembly" now ends with the F1 sentence (manifest rebuilt from the shot list and edit list, 64 rows, 0 not found, trailer manifests byte-identical, test added); header still v1.6 (the paragraph edit is inside the v1.6 section; no structural change). |
| Everything else from pass 1 | PASS, unchanged | No file under `film/script`, `film/voice`, `film/subs`, `film/assemble/edl-*`, `film/assemble/loudness.csv`, `film/sim_main.py`, `docs/sources` or `docs/cost-log.*` changed in 95f9e8a; pass-1 evidence for items 1 and 3–18 stands. |

No open FAIL remains.

VERDICT: PASS
VERIFY_FIX_FILM_STORY: PASS
