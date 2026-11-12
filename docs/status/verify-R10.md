> **Document version:** docs/status/verify-R10.md v1.2 | 7 Nov 2026 | Author: red-team-verifier (claude-fable-5-1) (v1.2: final re-check after d1b9088, section 9; v1.1: re-check after 96ec425; absolute path removed from the scope line) | Status: verified

# Verification: R10 half 1 (documentary film; CP8 stop)

Scope: worktree `.worktrees/r10`, branch `r10`, HEAD 8e8c4cf (5 commits since e9e0433; 52 files, +5,225 lines). Governing texts: `prompts/R10_LAUNCH.md` (wins), `prompts/R10.md` half 1 tasks 1–6, `prompts/_common.md`, `CLAUDE.md`. Runs read from the main checkout's `runs/` directory (`RAILTWIN_RUNS_ROOT` set to it; the absolute path is not written here, hygiene rule). Read only; nothing fixed.

## 1. Commands (exit codes and timing)

| command | result |
|---|---|
| `uv run ruff check .` | exit 0, "All checks passed!" |
| `uv run ruff format --check .` | exit 0, 775 files already formatted |
| `uv run pytest -q` | exit 0, **876 passed, 69 skipped**, 10 warnings, 37.8 s |
| `uv run python -m common.docver check docs prompts .claude film/script` | exit 0, docver OK: 385 files |
| `uv run python -m common.manifest verify` (data/osm symlink present, full check) | exit 0, manifest OK: 388 rows |
| `RAILTWIN_RUNS_ROOT=… uv run python -m film.script validate film/script/ --strict-runs` | exit 0: 148 lines (main/ar 63 lines 11:06, main/en 63 lines 11:23, trailer/ar 11 lines 1:05, trailer/en 11 lines 1:08); 0 warnings |
| `uv run python -m film.shots check film/storyboard/shots.yaml --lines film/script/lines.csv` | exit 0: 70 shots (main 702.9 s, trailer 67.5 s) |
| `uv run python -m film.rights check film/rights_log.csv` | exit 0: 64 rows (candidate 47, rejected 13, test_only 4) |
| `uv run python -m film.subs check tests/fixtures/film/good.ar.srt` / `good.en.vtt` | exit 0 each: 2 cues, 0 warnings |
| `uv run python -m common.sources check film/script/*.md docs/dialect-recommendation.md film/storyboard/storyboard.md` | exit 1: every missing id is `S-r10-*`, `S-xt-*` (the CLI reads `docs/sources/index.csv` only). Re-checked every `S-` id in the scripts, lines.csv, storyboard, shots.yaml, dialect doc, voice README, rights log and licences-r10.csv against the union of `docs/sources/*.csv`: **0 unresolved ids** (S-r10-NNN/dNN/vNN in `docs/sources/r10.csv`; S-xt-* in `study-extra-travel.csv`). PASS on the merits; the CLI exit is by design. |
| CP8 gates: `film.render shot …`, `film.render all --cut en`, `film.assemble all`, `film.assemble cut --cut ar`, `film.voice speak --cut ar`, `film.subs build …` | each **exit 2** with the CP8 message; `film/renders/` does not exist; `film/audio/tests/` holds only the gitignored research samples |

## 2. Criteria table

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | lint, pytest, docver, manifest, film validators, sources ids | PASS | section 1 |
| 2a | every figure in all 148 lines matches its cited register row or run output digit by digit | PASS | section 3 (all 74 line ids × 2 languages checked; 0 digit mismatches) |
| 2b | claim wording supported; no status upgrade | PASS | Haramain "open since October 2018, up to 300 km/h from early 2020" (S-r10-007/008); Landbridge, GCC section, Saudi–Qatar line all "announced / under procurement / not built"; Riyadh 15 M = Reuters July 2020 remark, "under review" (S-r10-026/027); AFP July 2022 remarks attributed, "not a published programme target"; no "Vision 2040"; no population target attributed to Vision 2030 |
| 2c | labels per R10_LAUNCH; RJ reach numbers exact | PASS | lines.csv: 13 main + 2 trailer lines `synthetic+not_official` (every extra-travel and RJ-study line), 12 + 3 `synthetic`, 5 + 1 `composite`, 3 `quote`; m-08-09 "direct adds no one; three via Taif about 0.23 million; Landbridge-stops chain about 0.31 million" = replace-rj-a gain 0 / b,c1,c2 230,468 / lb 307,232; m-08-10 93,693 (C1) and 109,007 (LB) = score.csv `access_gain_120_five_metros`; no "+0.23–0.31 M for every sketch" |
| 2d | ranges, "in the model", no promises | PASS | every cost/benefit a P10–P90 range (m-08-01…07, t-08); `grep -nE "\bwill\b"` on the scripts: 0; «سوف/راح/بيصير»: 0 |
| 2e | excluded facts absent | PASS | no ~470 or 517 weekly flights, no Tabuk flight time or count, no 101-minute block as a schedule, no jobs/GDP/ridership claim, no pilgrim or visitor vignette, no Hajj/Umrah land-entry narration (grep `470|101|67 |pilgrim|حاج|معتمر`: only the Vision 2030 Umrah quote) |
| 2f | AR and EN carry the same facts and figures | PASS (note) | digit sets identical on 72 of 74 pairs; m-01-07 EN "1 hour 15 minutes" = AR «ساعة و15 دقيقة», m-05-04 EN "about 2 hours" = AR «حوالي ساعتين» (word forms, same value); trailer figures are a subset of the main cut (0 extra figures) |
| 2g | Arabic natively written in the recommended white register | PASS (native review pending) | «اللي، مو، كذا، ليه، هالـ، قدّام، عشان، شغّال، تنقرا»; no «سوف/الذي/إنّ»; none of the §5.1 avoid-list in narration («وش» appears only in the section-5 heading, see notes); sentence structure differs from the EN (not a translation); `native_review` = pending on all 74 AR rows |
| 3 | section 3 Vision quotes verbatim | PASS | m-03-05/06/07 strings equal the `quote` cells of S-r10-019/020/021/022; re-read in the live PDF (`saudi_vision203.pdf`, 85 pp., pdftotext): "To increase our capacity to welcome Umrah visitors from 8 million to 30 million every year" (p.18), "To have three Saudi cities be recognized in the top-ranked 100 cities in the world" (p.24), "to complete, improve and link our infrastructure internally and across borders" and "constructing shared road and railway networks" (p.57) |
| 4 | dialect recommendation argued against four W10 criteria, sourced, marked a recommendation, honest about broadcast practice | PASS | `docs/dialect-recommendation.md` §2 table scores a–d on all four criteria with S-r10-d01…d14; §3 states "Not verified: the register of the narration"; line 5 "This is a recommendation for Tariq, not a decision" |
| 5 | voice research: open first, commercial, human; licences; XTTS-v2 untouched; no paid call; caveat; fine-tune as option | PASS | `film/voice/README.md`: table rows 1–17 open, 18–23 commercial "not used", 24 human; "Paid A/B not run … USD 0 spent"; "Coqui XTTS-v2 … was not downloaded or run"; bold caveat line 7; fine-tune section "proposal only; not executed"; `docs/cost-log.md` has no R10 or paid-TTS row; `film/voice/disk-log.md` lowest free 16.0 GiB, 4.4 GiB downloaded, MMS cache deleted |
| 6 | rights and licences complete with proof; Remotion recorded; archival PD; ODbL sidecars; spot-check | PASS | 64 rights rows / 51 licence rows cover every model, voice, dataset, service, font, tool, image and the music policy; Remotion row (Free License for an individual, 5.0 draft noted); 5 LOC/Commons PD photographs with LCCN and proof links, LOC 403 disclosed; ODbL share-alike on the alignment sidecars (row 55); spot-check 7/7 + 3/3 + PDF (section 4) |
| 7 | storyboard: every line has a shot; footers match labels; OSM credit; no logos; no AI footage; disk estimate | PASS | all 74 line ids covered by exactly one shot; 0 shots with a footer weaker than a covered line's label; `osm_credit: true` on all 29 map_animation + 3 split_screen + 1 archival shots; `ai_generated: false` on 70/70; "No logo or emblem"; §4 disk table 8.7 / 18.9 / 60.0 GB, 21 GiB free, render gate ≥ 50 GiB |
| 8a | nothing rendered or assembled; gates exit 2 | PASS | section 1 |
| 8b | no new model downloads after research; no push/tag/remote | PASS | disk-log ends 15:48; `git remote -v` empty; no `r10` tag; `git status` clean |
| 8c | official figures, runs, `docs/licences.csv`, `docs/assumptions*.md`, `docs/sources/index.csv` untouched | PASS | `git diff e9e0433 --stat` on those paths: only `cities/ksa/assumptions/film_timing.yaml` (new, owned by R10) |
| 8d | deviation recorded (registers under `film/`) | PASS | `film/README.md` line 19 and `film/assumptions-r10.md` line 5 |
| 8e | status block, cost estimate first line, CP8 package file, closing line | **FAIL** | `docs/status/r10.md` and `docs/status/cp8-package.md` do not exist (F1, F2) |
| 9a | no "Transit Costs" figure in docs/ or film | PASS | film/: 0 hits; docs/: only the hard-stop and exclusion notes |
| 9b | no Claude model names in scripts, storyboard, dialect doc, voice README | PASS | grep `claude-(opus|haiku|fable)|Fable 5|Hanko|Opus` on the R10 diff: 0 ("Claude" appears once, in the credits roll sh-08-14, as R10_LAUNCH instructs) |
| 9c | no absolute home paths, no content from the author's company, no secrets, no `git push` in scripts | PASS | `/Users/[a-z]` in tracked files: 0; private-list terms only in the standing rule text; key-pattern grep on the R10 diff: 0; `git push` in `scripts/`, `film/`: 0 |
| 10 | Arabic on-screen label term matches `docs/glossary.ar.md` | **FAIL** | F3 |
| 11 | assumption register integrity | **FAIL** | F4 |
| 12 | CP8 documents point to files that exist | **FAIL** | F5 |

## 3. Line-by-line result (both languages, both cuts)

Lines checked: **148 of 148** (main 63 AR + 63 EN; trailer 11 AR + 11 EN). Every `S-`, `A-`, `doc:` and `run:` citation opened. Figures verified against:

- `runs/r6/top5/top5.csv`: S6-L2 capex_p10 800.6 / p90 5,286.1 → 0.8–5.3 bn; npv_p90cost low/med/high 3,986 / 4,771 / 5,589 → 4.0–5.6; S6-L1 capex 6,233 / 41,304 → 6.2–41.3, npv_p90cost −2,958 / −724 / +1,631 → −3.0 to +1.6, robust_npv 11,023 highest; S6-L3 access_gain_120 4,246,882 vs 3,563,760 → 4.25 vs 3.56 M, npv_p90cost −21,745 / −19,225 / −16,624 → −21.7 to −16.6; pv_wei L2 114,628 / L3 267,681 → 114.6–267.7; access_gain_60 = 0 for all five (m-04-05).
- `runs/cba/CBA-S1-committed-programme/results.json` entry 25 (greenbook_2026, 60 y, un_wpp_medium): npv P10/P50/P90 −337,554.7 / −60,103.2 / 11,607.0 → −337.6 / −60.1 / +11.6; pv_user_time_cost 2,313.1 / 19,336.1 → 2.3–19.3; pv_safety 595.8 / 7,444.5 → 0.6–7.4.
- `runs/r7/fiscal/fiscal.json` programmes.S6-L2.models.fully_public_sar.by_pop.un_wpp_low.net_fiscal_cost_60y p10 694.9 / p90 4,087.9 → 0.7–4.1 bn (matches executive summary §3).
- `runs/r6/v3/national_reach.json`: S1 120 = 26,096,670 of 35,927,621 → 26.10 of 35.93 M. `runs/r6/v3/results.tsv`: 47,109 lines incl. header → 47,108 rows.
- `runs/study/rj/score/score.csv`: bcr_p50_medium 0.228 / 0.182 / 0.227 / 0.221 / 0.244 → 0.18–0.24; every npv at p50 and p90 cost negative in all three population columns; national_reach_gain_120 0 / 230,468 ×3 / 307,232; access_gain_120_five_metros 93,693 (C1), 109,007 (LB), 0 otherwise. `times-s1/times.csv`: `vs_air_d2d_model_min` positive in all 32 rows, RJ-A 350 non-stop +106.3. `legs-s1/legs.csv`: RJ-B/C2 taif→wp-north 61.85 / 91.389 / 16.2 / 14.8.
- `runs/study/extra-travel`: Table 2a S1 424,947 / 3,474,082 / 4,657,483 → 0.42 / 3.47 / 4.66 M; `induced_summary.csv` low 230,329 → stress 1,117,199 → 0.2–1.1 M; largest P50 NPV change 2.51 % (stress_rail_only) → "at most about 2.5 %".
- Source rows: S-r10-003 (Oct 1951), -004 (Qurayyat 31 Mar 2022), -005/-006 (sleeper cabins, car carriage), -007 (11 Oct 2018), -008 (300 km/h, 1 Jan 2020), -010/-011/S-034/S-036 (six lines, 85 stations, 1 Dec 2024–5 Jan 2025), -013 (1:15), -014 (11 tunnels, 32 bridges), -016 (9.1 M by 2030, Jan 2025), -019…-022 (Vision quotes), -023 (32,175,224), -024 (35.3 M mid-2024), -025 (50 M / 100 M, AFP 27 Jul 2022), -026 (15 M, Reuters 8 Jul 2020), -027 (under review), -028 (785 km, ~2 h, Hofuf, Dammam, 8 Dec 2025), -029 (65 M of 140.9 M); S-xt-001/002/007 (5th, 9.8 M seats, +13 %, +22 %, Japan); S-017 (1,250 km); S-054 (900 km, 2034); S-cp2-gastat-007 + `docs/coverage.md` rows (Taif 913,374; Tabuk 623,665; Khamis Mushait 601,305; Abha 422,243; Najran 421,902; Jazan 200,911; served-within-10 km column 0 for all six; 150 governorates); S-cost-rcf-008 (n = 355); S-r1a-066/068 (1908; closed after 1920).

**Lines with a FAIL:** none on figures or wording.

**Lines to soften (not FAIL):**
- m-01-07 (AR/EN): "one airline lists Abha to Jeddah at 1 hour 15 minutes" rests on S-r10-013, an aggregator page whose schedule validity ended 28 Mar 2026 (status partial). Say "one airline's timetable listed" (past) or cite a current timetable.
- m-02-03: "passenger trains reaching Qurayyat since 2022" rests on one news source (S-r10-004, partial); acceptable, flagged in `r10-notes.md`.
- m-06-03: "one sketch" — the Taif → north waypoint leg is shared by RJ-B and RJ-C2 (legs.csv); "two sketches share" would be exact.
- Section-5 heading «وش تفتح السكة اليوم» (`film/script/meta.yaml` sections_ar.5, shown as a storyboard section title) uses «وش», which `docs/dialect-recommendation.md` §5.1 lists as a strong Najdi marker to avoid; not narrated, but on reviewer-facing material.

**Lines to remove:** none.

## 4. Spot-check (seed 20261107, `random.sample`)

Rights log, 7 of 64 rows (CSV rows 4, 11, 30, 40, 48, 50, 53), proof links opened with WebFetch on 7 Nov 2026:

| row | item | register says | page says | result |
|---|---|---|---|---|
| 4 | ClArTTS reference clip | CC-BY-4.0 | HF card licence `cc-by-4.0` | match |
| 11 | F5-TTS | code MIT; weights CC-BY-NC-4.0 (Emilia) | README: "Our code is released under MIT License. The pre-trained models are licensed under the CC-BY-NC license due to the training data Emilia" | match |
| 30 | ElevenLabs terms | last updated 9 Oct 2026; §1(c) free non-commercial, paid commercial | "Last Updated 09 October 2026"; free "only … for non-commercial purposes"; paid "may use the Services for commercial purposes" | match |
| 40 | Noto Sans Arabic | SIL OFL 1.1, Copyright 2022 The Noto Project Authors | OFL.txt: same two lines | match |
| 48 | MapLibre GL JS | BSD-3-Clause | LICENSE.txt: BSD 3-Clause, "Copyright (c) 2023, MapLibre contributors" | match |
| 50 | puppeteer-core | Apache-2.0 | LICENSE: Apache License, Version 2.0 | match |
| 53 | Blender | GPL-2.0-or-later (Cycles Apache-2.0); GPL does not attach to output | page: GPL v2 or later; Cycles Apache 2.0; "What you create with Blender is your sole property" | match |

Source register, 3 of 29 `S-r10-NNN` rows:

| id | register | live page | result |
|---|---|---|---|
| S-r10-014 | 11 tunnels, 32 bridges; Arab News 27 Jul 2024 | "creating 11 tunnels, and erecting 32 bridges"; dated July 27, 2024 | match |
| S-r10-016 | 9.1 M annual visitors by 2030, formal target; Al-Dabbagh, 27 Jan 2025 | "The formal target for Asir is 9.1 million annual visitors by the year 2030" (Hashem Al-Dabbagh, CEO); 27 Jan 2025 | match |
| S-r10-020 (+019, 021, 022) | Vision 2030 PDF quotes | all four strings present verbatim in the PDF text (pp. 18, 24, 57; two-column wrap) | match |

No fabricated or misquoted figure found.

## 5. Failures (exact evidence)

**F1. No status file.** `docs/status/r10.md` does not exist (`ls docs/status/` lists r1a…r9 only; `git diff e9e0433 --stat -- docs/status/` is empty). Required by `prompts/R10_LAUNCH.md` addendum 1 ("Write your own estimate in the first status line"), addendum 4 ("Status file `docs/status/r10.md`; the closing line is `R10: blocked - CP8 approval required`"), `prompts/R10.md` task 6 and `prompts/_common.md`. The orchestrator's `make status` grep finds no R10 line.

**F2. No CP8 package.** `docs/status/cp8-package.md` does not exist. Required by R10_LAUNCH addendum 3 (dialect recommendation and reasons; links to both scripts and trailers with running times; lines.csv counts per section and language; storyboard and shot-list summary; voice/TTS table with licences, sample paths and cost; rights log; the verifier's line-by-line result; open questions). The material exists across `film/` but the one review file Tariq asked for is missing.

**F3. Arabic label term contradicts the glossary.** `docs/glossary.ar.md` term 4 (Tariq): use «طلب تركيبي غير مُعايَر»; avoid «طلب اصطناعي», «اصطناعي». The film uses the avoided term in reader-facing places: `film/script.py` lines 91–92 (rendered into `film/script/main.ar.md` line 7 and `film/script/trailer.ar.md` line 7: "synthetic = طلب اصطناعي غير معايَر … synthetic+not_official = اصطناعي من دراسة جانبية") and the on-screen AR footer in `film/storyboard/shots.yaml` / `storyboard.md` line 40 («طلب اصطناعي، غير معاير: مقارنة سيناريوهات، ليست توقعاً»). The narration itself (m-06-07, m-08-11, t-10) and `docs/dialect-recommendation.md` §5.3 use the glossary term, so the film contradicts its own rule. FIX_R8 made glossary consistency a tested rule for the Arabic summary; the footer is the label rule 3 puts on every modelled frame.

**F4. Duplicate assumption id.** `film/assumptions-r10.md` line 9 defines `A-film-001` ("Register of the Arabic narration …, recommendation pending Tariq at CP8") while `docs/assumptions.md` line 293 already holds `A-film-001` ("Arabic narration register preference … Tariq's preference, 30 Oct 2026"). One id, two registers, two texts; `cities/ksa/assumptions/film_timing.yaml` and the dialect doc cite A-film-001 without saying which.

**F5. CP8 documents cite files that do not exist.** `film/voice/README.md` lines 5, 13, 136, 137 point to `film/_work/voice-sources.csv` and `film/_work/voice-disk-log.md`; `docs/dialect-recommendation.md` line 9 points to `film/_work/dialect-sources.csv` and `film/_work/dialect-assumptions.md`. `film/_work/` is not in the tree (`ls film/_work`: No such file). The tracked equivalents are `docs/sources/r10.csv`, `film/voice/disk-log.md` and `film/assumptions-r10.md`. "Not found" is a FAIL for source tracing in the two documents Tariq reads at CP8.

## 6. Notes (no verdict impact)

- `common.sources check` cannot see `docs/sources/r10.csv` or the study CSVs; a registry option would let CI run it on the film files.
- OAG seat lines (m-01-05, t-02) carry `synthetic+not_official` although they are published facts; this follows R10_LAUNCH ("holds only with both labels") and the storyboard asks Tariq to confirm (open question 3).
- AR m-03-05…07 carry no `quote` label (the Arabic paraphrases, «بمعنى كلامها»); the storyboard shows the meaning without quotation marks and raises sourcing the official Arabic text (open question 1). Consistent with rule 1.
- `docs/STATUS.md` line 444 ("R9/R10 (film): not approved, 4 Nov 2026; Nabrah AI stays a release blocker") predates the 7 Nov approval at line 420; the coordinator may want to reconcile at the status update.
- `film/script/review-log.md` is referenced as the native-review log but not yet created (to be created by the reviewer; fine).

## 7. Three most important fixes

1. Write `docs/status/r10.md` (cost estimate on the first status line, the CP8 status block, pointer to the package, closing line `R10: blocked - CP8 approval required`) and `docs/status/cp8-package.md` with every item in R10_LAUNCH addendum 3, including this verifier result (148 lines checked, 0 changed, 0 removed, 4 to soften).
2. Replace «طلب اصطناعي» / «اصطناعي» with the glossary term «طلب تركيبي غير مُعايَر» in `film/script.py` lines 91–92 (then `film.script render`) and in the AR footers of `film/storyboard/shots.yaml` (then regenerate `storyboard.md`); add the glossary avoid-list to a film test.
3. Resolve the `A-film-001` collision (renumber the film row or make it a pointer to the existing docs row, and update `film_timing.yaml` / the dialect doc) and repoint the `film/_work/*` references to `docs/sources/r10.csv`, `film/voice/disk-log.md` and `film/assumptions-r10.md`.

VERDICT (first pass, HEAD 8e8c4cf): FAIL

## 8. Re-check after 96ec425 (7 Nov 2026, red-team-verifier, read only)

Scope: HEAD 96ec425 (`fix(film): verifier items …; status block and CP8 package`; 18 files, +341/−37). Working tree clean at the start of the re-check. The only edit made by the verifier is to this file (v1.1).

### 8.1 Commands

| command | result |
|---|---|
| `uv run ruff check .` / `uv run ruff format --check .` | exit 0 / exit 0 (778 files already formatted) |
| `uv run pytest -q` at HEAD 96ec425 | **1 failed**, 41.3 s: `tests/test_hygiene.py::test_no_absolute_home_paths_tracked` → `hits == ['docs/status/verify-R10.md']`. The hit is line 5 of **this report** (the `RAILTWIN_RUNS_ROOT=/Users/…` path written in v1.0 and committed by the builder in 96ec425). Removed in v1.1; `uv run pytest -q` on the edited tree: see 8.1a below. No other test fails. |
| `uv run python -m common.docver check docs prompts .claude film/script` | exit 0: docver OK, 388 files |
| `uv run python -m common.manifest verify` (full check, `data/osm` symlink present) | exit 0: manifest OK, 388 rows |
| `film.script validate film/script/ --strict-runs` (runs root = main checkout) | exit 0: 148 lines (main/ar 63 = 11:08, main/en 63 = 11:26, trailer/ar 11 = 1:05, trailer/en 11 = 1:08), 0 warnings; run twice, outputs identical |
| `film.shots check film/storyboard/shots.yaml --lines film/script/lines.csv` | exit 0: 70 shots (main 702.9 s, trailer 67.5 s); run twice, identical |
| `film.rights check film/rights_log.csv` | exit 0: 64 rows (candidate 47, rejected 13, test_only 4) |
| `film.render all --cut en`, `film.voice speak --cut ar` | exit 2 with the CP8 message; `film/renders/` absent; `film/audio/tests/` holds only the gitignored samples |
| `git diff e9e0433 --stat -- docs/licences.csv docs/assumptions.md docs/assumptions-*.md docs/sources/index.csv docs/report/ runs/` | empty (protected paths untouched) |
| `git diff e9e0433 --stat -- docs/STATUS.md CHANGELOG.md docs/cost-log.md docs/cost-log.csv .claude/` | empty |
| hygiene greps on `git ls-files`: `/Users/[a-z]` | 1 hit = this report (fixed in v1.1); secrets pattern: 0; `git push` in `scripts/`, `film/`, `Makefile`: 0; `git status --porcelain`: clean before the verifier's edit |

### 8.2 Items

| # | item | verdict | evidence |
|---|---|---|---|
| 1a | `docs/status/r10.md` exists; version header; cost estimate in the first line after the header; status block; last line exactly `R10: blocked - CP8 approval required` | PASS | line 1 header v1.0; line 3 "Run cost estimate (builder's own, list price): about USD 75–95 … Paid TTS: USD 0 of the separate USD 60 cap"; sections Half 1 deliverables / Decisions / Checks / Open questions; `od -c` on the tail: `\n\nR10: blocked - CP8 approval required\n`, plain text at column 0 |
| 1b | `docs/status/cp8-package.md` exists with a version header and every addendum-3 item | PASS (content) | line 1 header v1.0; §1 dialect + reasons against the four criteria; §2 four script links with running times; §2 lines.csv counts per section (main 10/8/8/7/5/7/5/13 = 63; trailer 2/1/1/1/0/1/1/4 = 11, identical per language: re-counted from `lines.csv` with csv.DictReader, 148 rows, 74 ids, AR `native_review` pending ×74); §3 storyboard summary; §4 voice/TTS table with licences, sample paths or skipped reasons, cost "USD 0"; §5 rights log; §6 verifier result; §7 nine open questions |
| 1c | counts and figures stated in r10.md / cp8-package.md match the files | **FAIL (F7)** | shots 70 = 59 main (702.9 s, sh-08-14 credits 20.0 s) + 11 trailer (67.5 s) ✓; renderers deckgl_capture 32 / manim 37 / ffmpeg_only 1 ✓; `rights_log.csv` 64 rows (47/13/4), 6 `font` rows, 5 `image` rows ✓; `licences-r10.csv` 51 rows ✓; `lines.csv` 148 rows ✓; running times = `film.script validate` ✓; CER column of `film/voice/scores.csv` = the §4 table (0.165, 0.301, 0.211/0.183, 0.074, 0.078, 0.146, 0.0075/0.0176) ✓; narrator "USD 70–320" = `film/voice/README.md` line 106 ✓; Remotion "up to 3 employees" = `rights_log.csv` row 46 ✓; Nabrah "cleared in writing 1 Nov 2026" = S-nabrah-005 (published 2026-11-01 09:38 AST, verified) ✓. **Mismatch:** `docs/sources/r10.csv` has **97** data rows (csv.DictReader; `wc -l` = 98 lines including the header: S-r10-001…049 = 49, d01…d14 = 14, v01…v34 = 34), but `docs/status/r10.md` line 19 and `docs/status/cp8-package.md` line 37 say "98 rows"; the package's own breakdown sums to 97. |
| 2 | Arabic label term follows glossary term 4 («طلب تركيبي غير مُعايَر»); no «اصطناعي» in `film/script.py`, the rendered `*.ar.md`, `storyboard.md`, `shots.yaml` | PASS | `film/script.py` lines 91–92 now «طلب تركيبي غير مُعايَر» / «تركيبي من دراسة جانبية»; `main.ar.md` line 7, `trailer.ar.md` line 7, both fixtures, `storyboard.md` line 40 («… (glossary term 4, `docs/glossary.ar.md`)»), `shots.yaml` lines 1182 and 1452; grep «اصطناعي» over those files: 0; new test `tests/test_film_real.py::test_arabic_label_term_follows_glossary` guards it. Remaining hits outside scope: `.claude/skills/documentary-script/SKILL.md` line 29 and `.claude/skills/motion-maps/SKILL.md` line 34 (pre-R10, unchanged since e9e0433) still prescribe «طلب اصطناعي، غير معاير» for the footer: a half-2 risk, see note N1; `film/voice/scores.csv` row 4 notes column quotes a Whisper read-back of the research sample («اصطناعي» heard «الصناعي»), research record only |
| 3 | A-film id clash resolved | PASS | `film/assumptions-r10.md` v1.1 line 9 = `A-film-005` "refines A-film-001 in docs/assumptions.md (Tariq's preference, 30 Oct 2026)"; `A-film-001` defined only at `docs/assumptions.md` line 293 (and its R8 annex mirror); `docs/dialect-recommendation.md` v1.1 line 9 "assumption `A-film-005` in `film/assumptions-r10.md`"; `cp8-package.md` line 8 and `r10.md` line 12 say the same; `film_timing.yaml` cites A-film-002…004 only; `git ls-files | xargs grep A-film-00[0-9]`: no other definition |
| 4 | no `film/_work` references in tracked files | PASS | `git ls-files | xargs grep -n "film/_work"`: only the three status files, each describing the fix historically (`cp8-package.md` line 107, `r10.md` line 35, this report F5); `film/voice/README.md` lines 5, 13, 136, 137 now `docs/sources/r10.csv` and `film/voice/disk-log.md`; `docs/dialect-recommendation.md` line 9 now `docs/sources/r10.csv` and `film/assumptions-r10.md` |
| 5a | m-01-07 (AR/EN) supported by S-r10-013; figures digit by digit | PASS | EN "one airline's published schedule listed Abha to Jeddah at 1 hour 15 minutes"; AR «جدول إحدى شركات الطيران حدّد رحلة أبها–جدة بساعة و15 دقيقة» (past tense, same meaning); S-r10-013 value "1:15 (nonstop, from one airline schedule; validity to 2026-03-28, expired)", status partial, `primary_to_find` = current airline timetable; `figure_values` "11; 32; 1; 15" in both languages; est_seconds re-estimated (AR 10.5 → 10.8, EN 9.7 → 11.1; `validate` enforces) |
| 5b | m-06-03 (AR/EN) and sh-06-03 supported by `docs/rj-routes-study.md` §3 and `legs.csv` | PASS (script, shots.yaml) | `docs/rj-routes-study.md` line 95: "RJ-B, RJ-C2 \| Taif → north waypoint \| 61.9 \| 91.4 \| 1.48 \| 16.2 \| 14.8"; line 96: RJ-C1 takes the south waypoint (62.0 / 117.0 / 19.5 / 20.5); `runs/study/rj/legs-s1/legs.csv` rows `RJ-B,taif,wp-north,61.85,91.389,1.478,16.2,14.8` and `RJ-C2,taif,wp-north,…` identical. Three via-Taif sketches (B, C1, C2); two share this leg: "two of the via-Taif sketches" (EN) / «في مخططين من اللي يمرّون بالطائف» (AR) is exact; figures 61.9 / 91.4 / 16.2 / 14.8 identical in both languages and in `shots.yaml` lines 773–774 ("two via-Taif sketches" / «مخططين يمرّون بالطائف») |
| 5c | storyboard.md consistent with shots.yaml and meta.yaml after the fix | **FAIL (F6)** | `film/storyboard/storyboard.md` line 117 (sh-06-03 row) still carries the pre-fix on-screen text "Taif descent, **one sketch**: 61.9 km …" / «نزلة الطائف، **أحد المخططات**: …» while `shots.yaml` lines 773–774 say "two via-Taif sketches" / «مخططين يمرّون بالطائف» (only the description column of that row was updated). `storyboard.md` line 101 still titles section 5 «**وش** تفتح السكة اليوم» while `film/script/meta.yaml` line 24 and `main.ar.md` now read «اللي تفتحه السكة اليوم». `cp8-package.md` line 107 states "the section-5 Arabic heading no longer uses «وش»": not true for the storyboard. No test or generator keeps `storyboard.md` in step with `shots.yaml` (`film.shots check` reads the YAML only). |
| 6a | lint, pytest, docver, manifest | **FAIL at HEAD (F8)** | pytest: 1 failed (`test_no_absolute_home_paths_tracked`, hit = this report, line 5 of v1.0). Fixed in this v1.1; the fix is uncommitted until the coordinator commits it. Lint, format, docver, manifest: exit 0. |
| 6b | film validators pass; no renders; protected paths untouched since e9e0433 | PASS | section 8.1 |
| 7 | nothing else broken by 96ec425 | PASS | `git diff 391b7ba..HEAD -- film/script/lines.csv`: exactly the 4 rows of m-01-07 and m-06-03 (AR+EN), sources and figure_values unchanged; `git diff 8e8c4cf..HEAD -- film/storyboard/shots.yaml`: only sh-06-03 `on_screen_text`; rendered `main.*.md` differ from 8e8c4cf only in the header, the running time (11:06 → 11:08, 11:23 → 11:26), the label legend, the section-5 heading and the two lines; `validate` byte-compares the rendered files with `render` output and passes; fixtures updated in step; 8 new test lines only |

### 8.1a pytest on the edited tree

`uv run pytest -q` after the v1.1 edit of this file: **877 passed, 69 skipped**, 10 warnings (the hygiene test passes; no other change). The verdict below still counts F8 because the verified HEAD 96ec425 fails pytest until this report is committed.

### 8.3 Failures remaining (exact evidence)

**F6. Storyboard out of step with the shot list and the script after the fix.** `film/storyboard/storyboard.md` line 117, columns "on-screen EN / AR": "Taif descent, one sketch: 61.9 km straight line → 91.4 km of track · 16.2 km tunnel · 14.8 km viaduct" / «نزلة الطائف، أحد المخططات: …», against `film/storyboard/shots.yaml` lines 773–774: "Taif descent, two via-Taif sketches: …" / «نزلة الطائف، مخططين يمرّون بالطائف: …». Same file line 101: "#### Main cut, section 5: What rail already unlocks / وش تفتح السكة اليوم" against `film/script/meta.yaml` line 24 «اللي تفتحه السكة اليوم» and `film/script/main.ar.md` "## 5. اللي تفتحه السكة اليوم". `docs/status/cp8-package.md` line 107 claims the heading fix. Two reviewer-facing documents now state different on-screen text for the same shot, and the CP8 package reports a fix that is incomplete.

**F7. Stated register size does not match the file.** `docs/status/r10.md` line 19 and `docs/status/cp8-package.md` line 37: "`docs/sources/r10.csv` (98 rows)". Measured: 97 data rows (49 + 14 + 34, the package's own breakdown); 98 is the `wc -l` line count including the header.

**F8. pytest fails at HEAD 96ec425** on `tests/test_hygiene.py::test_no_absolute_home_paths_tracked` because the builder committed v1.0 of this report, whose scope line held an absolute home path. Corrected in v1.1 (this file); the coordinator must commit the corrected report. No builder file is involved.

### 8.4 Notes (no verdict impact)

- N1. `.claude/skills/motion-maps/SKILL.md` line 34 and `.claude/skills/documentary-script/SKILL.md` line 29 still prescribe the glossary-avoided footer «طلب اصطناعي، غير معاير». They predate R10 and are agent-facing, but the half-2 renderer will read them; align them with glossary term 4 before half 2.
- N2. Disk figure: `storyboard.md` line 5 and `cp8-package.md` §3 say "about 21 GiB free"; `docs/status/r10.md` line 29 says "23 GiB free at the stop" (`disk-log.md` line 13 shows 23.66 GiB at 15:06 before the model downloads). Different moments, both plausible; state one figure with its time.
- N3. `docs/cost-log.md` has no R10 row yet; the builder cannot log its own run and `r10.md` line 3 says the coordinator logs the measured figure. Unchanged from the first pass.
- N4. `cp8-package.md` §6 counts "lines removed" as the 7 facts that never entered the script; the verifier's count of removed script lines is 0 (both passes). Wording, not a figure.

### 8.5 Three fixes

1. Regenerate or edit `film/storyboard/storyboard.md` line 117 (on-screen EN/AR for sh-06-03 = the `shots.yaml` text) and line 101 (section-5 title = `meta.yaml` sections_ar.5); add a test that the storyboard's on-screen columns and section titles equal `shots.yaml` / `meta.yaml`.
2. Correct "98 rows" to "97 rows" in `docs/status/r10.md` line 19 and `docs/status/cp8-package.md` line 37 (or count with `csv.DictReader`).
3. Commit this report v1.1 so `pytest` passes at the verified HEAD; keep absolute paths out of every tracked file, status reports included.

Verdict at v1.1 (section 8, superseded by section 9): FAIL

## 9. Final re-check after d1b9088 (7 Nov 2026, red-team-verifier, read only)

Scope (narrow, as instructed by the coordinator): the three open items F6, F7, F8 from section 8, plus the diff scope since 96ec425, the full test/lint/docver runs, and the `r10.md` end line. HEAD d1b9088 (`fix(film): re-check items (storyboard synced, source row count, verifier report v1.1 without home path)`); `git status --porcelain` empty at the start. The only edit made by the verifier is to this file (v1.2).

### 9.1 Commands

| command | result |
|---|---|
| `git diff 96ec425..HEAD --stat` | 4 files, +76/−10: `docs/status/cp8-package.md` (4), `docs/status/r10.md` (8), `docs/status/verify-R10.md` (68), `film/storyboard/storyboard.md` (6). Nothing outside `docs/status/*` and `film/storyboard/storyboard.md`. |
| `uv run pytest -q -p no:warnings` (full run, output to a log) | **exit 0**; progress lines reach `[100%]` with passes and skips only, no `F`; `tests/test_hygiene.py` alone: 3 passed |
| `uv run ruff check .` | exit 0: "All checks passed!" |
| `uv run ruff format --check .` | exit 0: 778 files already formatted |
| `uv run python -m common.docver check docs prompts .claude film/script` | exit 0: docver OK, 388 files |
| `git ls-files -z \| xargs -0 grep -nE "/Users/[a-z]\|/home/[a-z]"` | exit 1 (no hit in any tracked file) |
| `tail -n 1 docs/status/r10.md \| od -c` | `R 1 0 :   b l o c k e d   -   C P 8   a p p r o v a l   r e q u i r e d \n`, preceded by a blank line |

### 9.2 Items

| # | item | verdict | evidence |
|---|---|---|---|
| F6 | `storyboard.md` sh-06-03 on-screen text and section-5 Arabic heading in step with `shots.yaml` / `meta.yaml` | PASS | `film/storyboard/storyboard.md` v1.2, line 117 on-screen EN/AR = "Taif descent, two via-Taif sketches: 61.9 km straight line → 91.4 km of track · 16.2 km tunnel · 14.8 km viaduct" / «نزلة الطائف، مخططين يمرّون بالطائف: 61.9 كيلو بخط مستقيم ← 91.4 كيلو سكة · 16.2 كيلو أنفاق · 14.8 كيلو جسور», byte-equal to `film/storyboard/shots.yaml` lines 773–774; line 101 "#### Main cut, section 5: What rail already unlocks / اللي تفتحه السكة اليوم" = `film/script/meta.yaml` lines 15 and 24 and `film/script/main.ar.md` "## 5. اللي تفتحه السكة اليوم". Programmatic sweep (PyYAML + the Markdown table rows): all 8 cut/section headings equal `meta.yaml` `sections_en`/`sections_ar`; all 70 shot rows have on-screen EN and AR equal to `shots.yaml` `on_screen_text` (0 mismatches, 0 missing rows). The diff since 96ec425 touches only the header, line 101 and line 117 of the storyboard. |
| F7 | stated size of `docs/sources/r10.csv` matches the file | PASS | `csv.reader`: 98 lines including the header, **97 data rows**, header `id,claim,value,unit,url,…`; `docs/status/r10.md` line 19 and `docs/status/cp8-package.md` line 37 now read "97 rows" (the package keeps the breakdown 001–049, d01–d14, v01–v34 = 49 + 14 + 34 = 97). No other "98 rows" claim remains in the three status files. |
| F8 | no absolute home path in the committed verify report; `tests/test_hygiene.py` passes at HEAD | PASS | v1.1 of this report is committed in d1b9088; grep `/Users/[a-z]` and `/home/[a-z]` over `docs/status/verify-R10.md`: 0 hits; over all tracked files (`git ls-files -z`): 0 hits; `uv run pytest -q -p no:warnings tests/test_hygiene.py`: 3 passed; full suite exit 0 at HEAD. |
| D | diff since 96ec425 limited to `docs/status/*` and `film/storyboard/storyboard.md` | PASS | section 9.1, first row. Content of the non-report changes: `cp8-package.md` header v1.1 + "97 rows"; `r10.md` header v1.1, "97 rows", the disk sentence now states both moments (23 GiB at the stop, 21 GiB when the storyboard estimate was written: closes note N2), and one half-2 note on the two skill files (note N1); `storyboard.md` as in F6. No change to `film/script/*`, `shots.yaml`, registers, `docs/STATUS.md`, `CHANGELOG.md`, the cost log or `.claude/`. |
| T | `uv run pytest -q -p no:warnings` exit 0 | PASS | section 9.1 |
| L | `uv run ruff check . && uv run ruff format --check .` | PASS | exit 0 / exit 0 |
| V | `uv run python -m common.docver check docs prompts .claude film/script` | PASS | exit 0, 388 files (this file's v1.2 header keeps the format) |
| S | `docs/status/r10.md` ends with `R10: blocked - CP8 approval required` | PASS | section 9.1, last row; the end line is unchanged by d1b9088 |
| H | no absolute home path written in this report | PASS | the v1.2 text uses repository-relative paths only; the tracked-file grep above is the test |

### 9.3 Notes (no verdict impact)

- N5. The verifier's first heading sweep reported a false mismatch on section 1 («أربع رحلات (شخصيات مركّبة)») because the regex stopped at the first "(" inside the Arabic title; re-read lines 53 and 152 of the storyboard: identical to `meta.yaml` line 21. Recorded so nobody repeats the false alarm.
- N1 (carried): the two skill files named in `docs/status/r10.md` (half-2 note) still carry the older footer wording; outside this track's ownership and outside half 1.
- N3 (carried): `docs/cost-log.md` still has no R10 row; the coordinator logs it from the run JSON.

### 9.4 Three remaining actions (half 2, not half-1 blockers)

1. Add a test that the storyboard's on-screen columns and section titles equal `shots.yaml` / `meta.yaml` (the sweep in F6 was done by hand this time).
2. Align `.claude/skills/motion-maps/SKILL.md` and `documentary-script/SKILL.md` footer wording with glossary term 4 before any render.
3. Coordinator: add the R10 half-1 row to `docs/cost-log.md` from the run JSON.

All three open items from section 8 are closed with evidence, and every command in the coordinator's final list exits 0. R10 half 1 is verified up to the CP8 stop; it stays `R10: blocked - CP8 approval required` by design until Tariq approves.

VERDICT: PASS
