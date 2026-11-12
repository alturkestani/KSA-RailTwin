> **Document version:** docs/status/verify-FIX_CP8_NOTES.md v1.0 | 7 Nov 2026 | Author: red-team-verifier (claude-fable-5-1) | Status: verified

# Verification: FIX_CP8_NOTES (R10 half 1, Tariq's CP8 notes applied)

Scope: worktree `.worktrees/r10`, branch `r10`, HEAD 9caa451 (5 commits since 6cec58f; 21 files, +621/−138). Governing text: `prompts/FIX_CP8_NOTES.md` v1.0 (wins); builder claims in `docs/status/r10.md` v1.2 (FIX_CP8_NOTES block) and `docs/status/cp8-package.md` v1.2 §0. Read-only pass: nothing fixed, committed, killed or started. Run files read from `../../runs` only.

## 1. Commands (exit codes and timing)

| command | result |
|---|---|
| `make test` (ruff check, ruff format --check, pytest -q, docver, manifest) | exit 0, 42.8 s; "All checks passed!", docver OK 389 files, manifest OK 388 rows |
| `uv run pytest -q -o addopts=""` (summary line, which `addopts = "-q"` hides) | 884 passed, 69 skipped in 39.0 s (matches the builder's count) |
| `uv run python -m film.shots check film/storyboard/shots.yaml --lines film/script/lines.csv` | exit 0, "PASS: 70 shots (main 708.8 s, trailer 67.5 s)" |
| `uv run python -m film.shots storyboard film/storyboard/shots.yaml` | exit 0, "storyboard.md matches shots.yaml" |
| `RAILTWIN_RUNS_ROOT=../../runs uv run python -m film.script validate film/script/ --strict-runs` | exit 0, 148 lines (main/ar 63 lines 11:09, main/en 63 lines 11:29, trailer/ar 1:05, trailer/en 1:08), 0 warnings |
| `uv run python -m film.rights check film/rights_log.csv` | exit 0, 64 rows (candidate 49, rejected 13, test_only 2) |
| `uv run python -m common.docver check` | exit 0, 389 files |
| `tail -c 60 docs/status/r10.md \| od -c` | ends `R 1 0 :   b l o c k e d   -   C P 8   a p p r o v a l   r e q u i r e d \n` (exact line, final newline, nothing after) |
| `cmp prompts/FIX_CP8_NOTES.md ../../prompts/FIX_CP8_NOTES.md` | identical |
| `git status --porcelain` | clean |
| `git tag --points-at HEAD` / `git remote -v` | empty / empty |
| `git merge-base --is-ancestor HEAD main` | false: r10 not merged; `main` at ed419ce, r10 diverged as the brief states |
| `film.script estimate` on a copy of `film/script/` | reproduces `lines.csv` byte for byte (the four changed `est_seconds` come from the timing YAML, not by hand) |

## 2. Criteria

| # | criterion | result | evidence |
|---|---|---|---|
| 1a | m-08-06 amounts kept and traced | PASS | `../../runs/cba/CBA-S1-committed-programme/results.json`: `units` = "SAR million, 2025 prices, PV at the A-cba-301 year"; entry population `un_wpp_medium`, horizon 60, rate_case `greenbook_2026`: `pv_user_time_cost` P10 2313.139 / P90 19336.083, `pv_safety` P10 595.837 / P90 7444.498 → 2.3–19.3 and 0.6–7.4 bn; A-cba-301 = PV year 2026 (`docs/assumptions.md` line 157). `lines.csv` figure_values `60; 2.3; 19.3; 0.6; 7.4` in both languages; sources unchanged |
| 1b | first range not "travel time saved" / «قيمة الوقت اللي يرجع للناس» | PASS | EN m-08-06: "users' travel time and cost savings, in present value"; AR: «وفورات الناس في وقت التنقل وتكلفته، بقيمتها الحالية»; sh-08-06 on_screen_text EN "users' travel time and cost savings", AR «وفورات الناس في وقت التنقل وتكلفته»; CP8 question 1 reworded (`cp8-package.md` line 139). Consistent with `docs/cba.md` line 82 (user_time_cost: rule of a half on the logsum composite cost; contains fares and car fuel) and the R8 wording "user time and cost savings" (`docs/report/feasibility-report.md` line 259) |
| 1c | second range a monetised safety benefit, not a crash count | PASS | EN "a safety benefit, road deaths and injuries avoided valued at standard appraisal values"; AR «وفائدة السلامة، يعني الوفيات والإصابات اللي تُتجنَّب محسوبة بقيم التقييم المعتادة»; sh-08-06 visual: "monetised safety benefit (…; not a crash count)" |
| 1d | source card basis | PASS | sh-08-06 `source_caption` EN "Basis: 2025 SAR, present value 2026, medium population, 60 years, Green Book 2026 discounting, P10–P90 (S1 committed programme run)"; AR equivalent «ريالات 2025، قيمة حالية لسنة 2026، سيناريو السكان المتوسط، 60 سنة، خصم الكتاب الأخضر 2026، P10–P90» |
| 1e | WEI only in m-08-07 | PASS | m-08-06 has no WEI; sh-08-06 visual: "Wider economic impacts are not on this card (sh-08-07)"; m-08-07 unchanged |
| 1f | Arabic reads naturally and says the same as the English | PASS (flag) | Same figures digit by digit (validate PASS). Reads naturally in the recommended register. Flag only: the second clause «وفائدة السلامة … بين 0.6 و7.4 مليار» relies on the elided verb «يقدّر» from the first sentence; acceptable spoken Arabic, for the native reviewer to confirm. `common.ar_render bidi-probe` on an HTML render of `main.ar.md` reported 0 numeric runs (the probe does not pick up this Markdown layout), so number order rests on the validate digit check and reading |
| 2a | every narrated shot's duration = sum of covered EN est_seconds | PASS | independent recomputation over 70 shots: 0 mismatches; every EN line covered by exactly one shot; the only unnarrated shot is sh-08-14 (20.0 s credits) |
| 2b | per-cut totals | PASS | independent sums from `lines.csv`: main EN 688.8 s (11:29), main AR 669.2 s (11:09), trailer EN 67.5 s, AR 64.7 s; picture from `shots.yaml`: main 708.8 s (= 688.8 + 20.0 credits, 11:49), trailer 67.5 s; AR with credits 689.2 s (11:29). All equal to storyboard.md §3 and the r10.md block |
| 2c | render disk estimate arithmetic | PASS | from the stated assumptions: lean 8.78 → 8.8 GB, recommended 19.05 → 19.1 GB, upper 60.37 → 60.4 GB; 4K 31.83 + 11.52 + 8.67 + 2.4 = 54.4 ≈ 54 GB. Note (pre-existing at 6cec58f, not introduced here): the PNG-cache row assumes "longest shot 19.2 s = 576 frames"; sh-08-02 is the longest narrated shot at 19.2 s but the credits roll sh-08-14 is 20.0 s (600 frames), which would make that row 1.2 / 3.0 / 4.8 GB and the totals about 8.8 / 19.2 / 60.6 GB |
| 2d | `film.script estimate` changed only m-02-02 and m-08-06 est_seconds | PASS | row-by-row diff of `lines.csv` against 6cec58f: changes only in (ar, en) × (m-02-02, m-08-06), columns `text` and `est_seconds` (5.8→5.0, 14.9→17.3, 6.1→5.4, 14.5→18.5); `estimate` on a copy reproduces the file |
| 2e | a test checks storyboard text, section titles and durations and fails on drift | PASS | `tests/test_film_real.py::test_storyboard_matches_shots_meta_and_line_times` calls `shots.check_storyboard` (generated section-2 tables vs the file: durations, on-screen text, section titles from meta.yaml), `check_durations`, `check_inheritance`, `check_quote_labels`, `check_quote_lines`; `tests/test_film_shots.py::test_storyboard_tables_round_trip` proves drift detection for a changed duration, changed Arabic on-screen text and a renamed section; `test_duration_must_match_covered_english_lines` proves the duration check fires (`film/shots.py` lines 186–396) |
| 3a | sh-01-05, sh-01-07, sh-08-13 osm_credit true; sh-01-05 keeps Copernicus | PASS | shots.yaml: sh-01-05 `osm_credit: true`, `held_frame_from: [sh-01-04]`, `extra_credit: Copernicus WorldDEM-30…`, legend; sh-01-07 `osm_credit: true`, held from sh-01-02/03/04/06, Copernicus; sh-08-13 `osm_credit: true`, legend, data_source existing+committed geojson |
| 3b | no other map-bearing shot lacks the OSM credit | PASS | scan of every shot whose type is map_animation or whose visual mentions map/hillshade/escarpment/vignette: only sh-05-03 (text-only caution card, "no Japanese map") and sh-08-14 (credits roll, which carries the OSM credit as text) have `osm_credit: false`; `check_inheritance` passes |
| 4 | sh-01-04 card direction and dated status match S-r10-013; no invented forward time | PASS | `docs/sources/r10.csv` S-r10-013: Abha–Jeddah XY 436 duration 1:15, "validity to 2026-03-28, expired", "no Jeddah-to-Abha duration read". Card EN "Jeddah – Abha · … · Air, Abha → Jeddah: 1 h 15 min (one airline's published schedule, now expired)"; AR «بالطيارة، أبها ← جدة: ساعة و15 دقيقة (جدول منشور لشركة طيران واحدة، انتهت صلاحيته)»; source_caption "Abha → Jeddah schedule, valid to 28 March 2026"; visual "no Jeddah → Abha time is sourced". m-01-07 unchanged ("listed Abha to Jeddah") |
| 5 | Vision 2030 Arabic | PASS | m-03-05 AR keeps «بمعنى كلامها», m-03-07 AR keeps «وهذا معنى النص، مو نصه الحرفي» (unchanged in the diff); sh-03-04 AR opens «رؤية 2030، بمعنى النص مو نصه الحرفي:», sh-03-05 AR «بمعنى النص، مو نصه الحرفي:»; `quote_label: {en: true, ar: false}` on both; `check_quote_lines` refuses `ar: true` over the unlabelled Arabic lines (EN lines are `quote`, AR lines unlabelled); data_source still S-r10-019/020/021/022, `docs/sources/r10.csv` not in the diff, no Arabic Vision URL, no new quote |
| 6a | sh-07-51 footer synthetic | PASS | shots.yaml sh-07-51 `footer: synthetic` (reuse_of sh-07-02 none + sh-07-04 synthetic) |
| 6b | m-04-04, m-06-01, m-06-02, t-06 unchanged, no labels; sh-04-04/06-01/06-02/06-51 footers unchanged | PASS | the four lines have empty `on_screen_label` in both languages and are not in the diff; the four shots keep `footer: synthetic` (not in the diff) |
| 6c | extra changes: sh-01-51 and sh-01-07 → synthetic+not_official, Copernicus on sh-01-51 | PASS (judgement noted) | Both show the sh-01-03 vignette (OAG seat card, footer synthetic+not_official per Tariq's decision) and the sh-01-04 hillshade (Copernicus), so under the "never weaker, inherit credits" rule the stronger footer and the DEM credit follow the picture. Consistent with the decision that the OAG lines keep both labels. Judgement for Tariq: the film's title card (sh-01-07, line m-01-10, no line label) will now carry "not the official ranking" because of one vignette; defensible, but it is a visible choice |
| 7 | pronunciation.md 1,250 example | PASS | line 52: "1,250 = «ألف وميتين وخمسين»"; «ألف ومية وخمسين» gone (test asserts it); header v1.1 |
| 8 | m-02-02 wording; North Line date | PASS | EN "inaugurated the Riyadh–Dammam railway line", AR «دشّن الملك عبدالعزيز خط سكة حديد الرياض–الدمام», still S-r10-003 (SAR timeline, Oct 1951); sh-02-02 "October 1951 · Riyadh–Dammam railway line inaugurated"; m-02-03 unchanged "passenger trains reaching Qurayyat since 2022" (S-r10-004, first services 31 Mar 2022); grep "begun in 2022": none |
| D1 | OAG / §5 lines keep both labels | PASS | `lines.csv` m-01-05, m-05-02, m-05-03, t-02 (ar and en) `on_screen_label = synthetic+not_official`; shots sh-01-03, sh-05-02, sh-05-03, sh-01-52 footers match; sh-01-03 source caption "Source: OAG, Busiest Routes 2025" |
| D2 | glossary term 4 unchanged; the two skills match it; no other skill rewrite | PASS | `docs/glossary.ar.md` not in the diff (row 4 «طلب تركيبي غير مُعايَر»); `.claude/` diff = exactly motion-maps/SKILL.md (v1.1, line 34) and documentary-script/SKILL.md (v1.2, line 29), 2 lines each; grep «اصطناعي» in tracked `film/` and `.claude/`: none (only gitignored `film/audio/tests/*`, `film/voice/scores.csv` and the glossary's rejected-forms column) |
| D3 | voice-model decision recorded | PASS | `film/rights_log.csv`: NAMAA-Saudi-TTS and Nabra-Saudi-82M test_only → candidate with "hold lifted, accepted under its published licence…, an allowed option, not an automatic replacement (Nabrah public voices first, Chatterbox the clean-licence fallback); the no-cloning rule stands"; ClArTTS clone row flagged (real LibriVox reader); `film/licences-r10.csv` approval column filled on both rows; `film/voice/README.md` v1.2 §3 ("this does not claim exhaustive training-data provenance for Chatterbox"); `cp8-package.md` v1.2 §0 |
| D4 | native review pending on every Arabic row | PASS | 74 of 74 Arabic rows `native_review = pending` |
| P1 | no model downloaded, no audio generated | PASS | commits 17:43–17:58 AST; newest file under `film/audio/` 16:41 (tests/README.md); `~/.cache/huggingface/hub` newest entry 15:14 (NAMAA, half-1 work); nothing under `film/audio`, the HF cache or `/tmp/r10-voice` newer than commit 3cd7191; free disk 23 GiB |
| P2 | no merge, tag, remote | PASS | see §1 |
| P3 | prompt byte-identical | PASS | `cmp` identical |
| P4 | make test green; the four film commands pass | PASS | see §1 |
| P5 | status file ends with the exact line | PASS | `od -c` tail above |
| P6 | no absolute home paths or model names in changed film files | PASS | grep for the absolute home-path prefix, `claude-`, `Opus`, `Haiku`, `Fable`, `Hanko` over the changed `film/` files: none ("Claude" in the sh-08-14 credits roll is unchanged and was accepted at verify-R10 9b per R10_LAUNCH) |
| P7 | version headers bumped on changed docs | PASS | main/trailer .ar/.en v1.2, pronunciation v1.1, storyboard v1.3, shots.yaml v1.1, meta.yaml 1.2, voice README v1.2, cp8-package v1.2, r10.md v1.2, both skills bumped; docver OK |
| P8 | status block content (before/after per fix, totals, estimate, test count, cost estimate) | PASS, placeholders open | all present; `DIFFSTAT_PLACEHOLDER` and `VERIFIER_PLACEHOLDER` remain by design (filled after this report), and the `FIX_CP8_NOTES: done` line the coordinator addendum requires at the end of the block is not yet written. Both must be completed before the launcher reads the file; the file's last line must stay `R10: blocked - CP8 approval required` |

## 3. Failures

None.

## 4. Other defects found (not FAILs for this fix)

1. `film/storyboard/storyboard.md` §4, PNG-cache row: "longest shot 19.2 s × 30 fps = 576 frames" ignores the 20.0 s credits roll (sh-08-14, 600 frames). Pre-existing at 6cec58f; the stated arithmetic is otherwise correct and the difference is about 0.1 GB per column.
2. `storyboard.md` §1 line 36 still lists the hillshade shots as "sh-01-04, sh-06-01, sh-06-03, sh-06-51" while line 45 (new) correctly adds sh-01-05, sh-01-07 and sh-01-51 as carrying the Copernicus credit by inheritance; the two sentences should agree.
3. `docs/status/r10.md` block: the `FIX_CP8_NOTES: done` line is absent (see P8).

## 5. Spot-check sample

Not a register milestone; the brief's eight items were each checked against their named source (CBA results.json, `docs/cba.md`, the R8 report, S-r10-003/004/013/016/019–022, the glossary, the timing YAML via `film.script estimate`). No fabricated or misquoted figure found.

## 6. Three most important follow-ups

1. Fill the two placeholders and add `FIX_CP8_NOTES: done` at the end of the block, keeping `R10: blocked - CP8 approval required` as the last line.
2. Tariq to confirm the title card sh-01-07 (and trailer sh-01-51) carrying "not the official ranking" because they include the OAG seat vignette, or to drop that vignette from the grid.
3. Align storyboard §1 line 36 with line 45, and note the 20.0 s credits roll in the PNG-cache assumption at the next storyboard edit.

VERDICT: PASS
