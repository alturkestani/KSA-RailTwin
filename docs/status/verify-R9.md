> **Document version:** docs/status/verify-R9.md v1.0 | 7 Nov 2026 | Author: red-team-verifier | Status: verified

# Verify R9 — release preparation (main, start HEAD 5edba39, verified HEAD c5c6efe)

Read-only audit against `prompts/R9.md` v1.1 (acceptance), `prompts/R9_LAUNCH.md` v1.0 (Tariq's approval and the coordinator addendum; stricter rules win), PROJECT.md sections 2 and 7, `CLAUDE.md`, `docs/status/main.md` (R9 block) and `docs/STATUS.md` (R9 row, CP7 checklist). Nothing was fixed, committed, tagged, pushed or contacted; no process was killed. Working tree clean before and after (`git status --porcelain` empty; the demo outputs went to `runs/demo/` and `/tmp`, both outside the tree or gitignored).

## 1. Commands run (exit codes and timing)

| command | where | rc | time / result |
|---|---|---|---|
| `rm -rf /tmp/ksa-railtwin-verify && git clone -q . /tmp/ksa-railtwin-verify` | /tmp | 0 | 1 s |
| `make setup` | fresh clone | 0 | 1 s (uv cache warm) |
| `make test` | fresh clone | 0 | 103 s; ruff "All checks passed!", "720 files already formatted", `docver OK: 364 files`, `manifest OK: 388 rows` with `--allow-missing` (auto-selected: no `data/osm`) |
| `uv run pytest -o addopts="" -q` | fresh clone | 0 | **791 passed, 70 skipped** in 33 s (same figures as the status block) |
| `make demo` | fresh clone | 0 | 2 s; label printed; screening 5 → 4 → 4, 10 corners; CBA 100 draws, 60y NPV P10/P50/P90 = −386 / −47 / 234 (fixture); 7 endpoints answered, 7 labelled |
| `du -sh` clone | /tmp | — | 776 MB total, `.venv` 638 MB (status block: 794 MB / 653 MB; same order) |
| `make test` | main checkout | 0 | ruff OK, `docver OK: 364 files`, `manifest OK: 388 rows` (strict, no flag) |
| `uv run pytest -o addopts="" -q` | main checkout | 0 | **861 passed** in 50 s (status block: 861) |
| `uv run python -m common.demo run --seed 1 --out …` twice | main | 0 | 2 s each; see determinism below |
| `uv run python -m common.sources bilingual-check docs/executive-summary.en.md docs/executive-summary.ar.md` | main | 0 | `PASS: 271 numeric tokens … 271 … equal` |
| `uv run python -m common.licences credits --check` | main | 0 | `credits: up to date` |
| `uv run python -m common.licences check` | main | 0 | `290 Markdown rows, 290 CSV rows, 0 differ` |
| `uvx --offline cffconvert --validate -i CITATION.cff` | main | 0 | `Citation metadata are valid according to schema version 1.2.0.` |
| `git remote -v` | main | 0 | empty |
| `git tag` | main | 0 | cp1, cp1-prep, cp2, r0, r1, r2, r2-int, r3, r4, r5, r6, r6.1, r7, r8, r8.1, session1-pilot — **no `r9`** |

Determinism (procedure step 3): two `common.demo run --seed 1` runs to separate output directories; `diff -r` excluding `meta.json`, `timings.json`, `summary.json` (the latter holds the ephemeral port) → identical; `cba/meta.json` differs only in `created_utc`.

## 2. Criteria table

### A. Acceptance of `prompts/R9.md`

| # | criterion | verdict | evidence |
|---|---|---|---|
| A1 | Fresh-clone `make setup && make test && make demo` passes within the measured time; README command matches reality | PASS | Table in §1: 1 + 1 + 103 + 2 s = 107 s (status block: 140 s including a second `make test`); README.md "Quick start" gives exactly `make setup && make test && make demo` and describes the `--allow-missing` switch that `Makefile:6` (`MANIFEST_FLAGS ?= $(if $(wildcard data/osm),,--allow-missing)`) implements; `README.md` line 32 points to the R9 block for the measured times, which match |
| A2a | `git ls-files` contains no data payloads beyond small licence-compatible tables with READMEs | PASS (with the owner decision carried, O6) | `git ls-files data runs movies film/renders film/audio` = 74 files, all under `data/`: `data/README.md`, `data/ksa/tables/README.md`, `gastat/` (24 files, README) and `pilgrims/` (46 files, README); 19,508,165 bytes; 29 PDF, 29 XLSX, 10 CSV, 2 HTML, 4 MD; every tracked `data/` directory has a README; nothing under `runs/`, `movies/`, `film/renders/`, `film/audio/`; `git log --all --diff-filter=A` finds no file ever added under those paths that is no longer tracked. Disclosed with counts and sizes in `docs/release-checklist.md` A ("74 files (about 19 MB) … 29 of them are PDFs, which are publications rather than 'small tables'") and `docs/STATUS.md` CP7 item 2 |
| A2b | No secrets, no absolute home paths | PASS | `git ls-files -z \| xargs -0 grep -l "/Users/[a-z]"` empty; secret-pattern grep (`sk-ant-`, `AKIA…`, `ghp_…`, `xoxb-`, private-key headers, `api_key = "…"`) matches only the two earlier verifier reports that quote the patterns; no `.env*` tracked; `git push` appears in no file under `scripts/`, `Makefile`, `.github/`; 54 tracked images are the report, deck and study-rj figures (`docs/report/figures` 34, `docs/deck-figures` 16, `docs/study-rj` 4), no imagery crops |
| A2c | `NOTICE` and `docs/credits.md` cover every register item | PASS | `docs/licences.csv` = 290 rows; `docs/credits.md` §1 = 290 numbered rows, §2 = 55 Python, §3 = 159 JavaScript packages; rows whose `attribution` cell is not none/n-a = 162 (recomputed from the CSV) = 162 `- ` items in the NOTICE generated block; `credits --check` up to date; `tests/test_credits.py` enforces both; no `claude-`, `/Users/` or company string in `NOTICE` or `docs/credits.md` |
| A3a | Community files exist and cite their sources | PASS | `CONTRIBUTING.md` v1.0 (uv/ruff/pytest, the 12 rules copied from PROJECT.md §2 with the two adapted phrases marked in square brackets, source/assumption/licence-row procedures, region-sweep re-run); `CODE_OF_CONDUCT.md` v1.0: "adapted from the Contributor Covenant, version 2.1" with the v2.1 URL, FAQ and translations links, and an HTML comment naming the upstream file, branch, fetch date 2026-11-07 and CC BY 4.0, "Only change: the reporting placeholder"; `SECURITY.md` v1.0 (no secrets, scope, how to report, placeholder contact, supported versions) |
| A3b | `CITATION.cff` validates | PASS | `uvx --offline cffconvert --validate -i CITATION.cff` → valid against 1.2.0; fields: `cff-version 1.2.0`, `type: software`, author Alturkestani/Tariq, `version: r9`, `license: Apache-2.0`, TrafficTwin cited under `references` as parent project with the same URL as the register row (`docs/licences.csv`, `cities/ksa/sources.yaml`: `https://github.com/alturkestani/TrafficTwin`); label in `message` and `abstract` |
| A4 | No remote, push, release, Pages, issue or external post; status file states it | PASS | `git remote -v` empty; `git tag` has no `r9`; `docs/status/main.md` R9 "Checks": "`git remote -v`: empty. No push, remote, release, tag, Pages site, issue, package entry or external post was made"; `docs/release-checklist.md` line 5 and `docs/STATUS.md` CP7 checklist repeat it; `docs/good-first-issues.md` line 5: "Nothing in this list has been created on GitHub" |
| A5 | Every outstanding gap is listed in good-first issues rather than hidden; 5+ stated counts re-run | PASS | 7 counts recomputed independently (my own scripts, not the file's): `docs/data-sources.md` last-cell "not found/none found" = **9**, "unverified" = **21** (GFI §A: 9 / 21); `docs/assumptions.md` `\| A-` rows = **765**, awaiting (assumed+open+proposed+secondary+unverified) = **650**, `docs/study-rj/assumptions.md` 9 rows / **8** awaiting (§B: 765 / 650 / 8); `cities/ksa/benchmarks/metrics.csv` 524 rows A/B/C/D = **293/14/179/38**, `overruns.csv` 103 = **68/1/28/6** (§C: same); `cities/ksa/candidates.parquet` 1,224 rows, `pop_type` grid **906** / official 224 / derived 51 / null 43, grid ≥ 10k = **24**, ≥ 5k = **99** (§D: same); `docs/licences-blockers.md` table rows = **46**, with a B-number = **12**; group sum 21+9+2+6+2+3+0+3 = 46 (§H: same); `cities/ksa/lines/stations.geojson` **153** features, **13** not located (GFI-007: 153 / 13); `docs/benchmarks/README.md` gap column 5+9+10+5+9+22+17+16+16+14+15+15+21 = **174** (GFI-023: 174). The list also carries the deferred SUMO check (GFI-028), dashboard polish (GFI-032…035), STATUS open items (GFI-036…044) and the 46 blockers as owner decisions (GFI-045…054) with the Transit Costs hard stop marked "not an issue to work on" |

### B. Addendum (`prompts/R9_LAUNCH.md`)

| # | criterion | verdict | evidence |
|---|---|---|---|
| B1 | Executive-summary banners only; bodies unchanged; labels and "في النموذج"/"in the model" kept; no CP6 "not for circulation"; bilingual check passes; headers no longer "draft, pending native review"; not framed as a public-release decision | PASS | `git diff 5edba39..HEAD -- docs/executive-summary.{en,ar}.md`: one hunk each, lines 1–9 (header + banner) only; EN: "Reviewed on Tariq's request on 7 Nov 2026 together with the Arabic summary, and signed off for internal use; this is not a public-release decision"; AR: "رُوجع هذا الملخص بطلب من طارق في 7 نوفمبر 2026، واعتُمد للاستخدام الداخلي؛ وهذا ليس قراراً بالنشر العام"; the "Draft, pending native-speaker review", the Arabic مسودة sentence and "هذه مسودة للمراجعة عند نقطة التحقق CP6، وليست للتداول" dropped; the `> Labels: synthetic demand, uncalibrated …` block untouched; headers now `Status: reviewed` (EN v0.6) and `Status: reviewed (signed off for internal use)` (AR v1.0); `bilingual-check PASS 271 = 271`; `tests/test_ar_render.py`, `test_glossary_ar.py` inside the green suite |
| B2 | Nabrah: only that row changed in `docs/licences.csv`; text matches the addendum; B9 still a blocker; no other blocker cleared; Transit Costs not used or cited newly | PASS | `diff <(git show 5edba39:docs/licences.csv) docs/licences.csv` → exactly 2 lines (one `<`, one `>`), both the row `"Nabrah AI (Nabrah Studio TTS, …)"`; new `commercial_use`: "Y for audio from the public voices (Daniah, Norah, Abdullah) on a paid plan: commercial use, public online publication (YouTube, social platforms) and screening/broadcast confirmed in writing by Nabrah.ai, 1 Nov 2026 (S-nabrah-005)"; `attribution`: "unanswered: attribution requirement not addressed"; `obligations`: "no voice cloning of any real person without written consent … training opt-out is Enterprise-only"; `status`: "… BLOCKED for public release until the attribution question is answered". `docs/sources/index.csv` +1 row S-nabrah-005 naming sender and role only (no email address). Release table at 5edba39 vs HEAD parsed per row: 290 rows both, statuses OBLIGATIONS 109 / NOT IN RELEASE 59 / COMPATIBLE 53 / **BLOCKER 46** / VERIFY 23 both, **no row changed status**; `common/sources.py` B9 reason narrowed to "attribution requirement still unanswered"; `tests/test_fix_r8.py` now allows exactly one Nabrah row to differ from tag r8 and asserts every other row equal. Transit Costs: every added line in `git diff 5edba39..HEAD` that names it is a "do not use / hard stop" note; `docs/licences-blockers.md` dependency scan still 16 hits, none a value |
| B3 | Nothing R10/film written; no model downloads | PASS | `git diff 5edba39..HEAD --stat -- film` empty; `~/.cache/huggingface/hub` last modified 17 Oct 2026, nothing newer than 7 Nov under any model cache; status block: "no download beyond uv's local cache and one `uvx cffconvert`" |
| B4 | RJ study not folded into report/top5/SWITCHER/recommended programme; README mentions it only as beside the report | PASS | `docs/report/feasibility-report.md`, `docs/policy-brief.md`, `docs/executive-summary.en.md`: 0 matches for `rj-routes-study`/`RJ-A`/`RJ-C1`; `git diff 4da3bcf HEAD --name-only` over `docs/report`, `optimise`, `scenarios`, `cities/ksa/{lines,corridors,alignments}`, `runs`, `judge`, `web`, `api`: only `docs/report/annex-sources.md` (regenerated for S-nabrah-005); README.md line 19 "kept **beside** the main report: a study of sketches, not the recommended programme and not part of the report's results", line 52 "(beside the main study)" |

### C. Code and test changes

| # | item | verdict | evidence |
|---|---|---|---|
| C1 | Run-scoped guards pinned (`tests/test_r8_l6_panel.py`, `test_study_rj_families.py`, `test_study_rj_score.py`: `END_HEAD = "4da3bcf"`) do not hide anything beyond the approved edits | PASS | `git log --oneline -3 5edba39`: 5edba39 (coordinator: R9 prompts) ← **4da3bcf** (cost-log row) ← 754a7c4, so the pin is the last pre-R9 commit; `git diff --name-only 4da3bcf HEAD` restricted to the union of the three `UNTOUCHED` lists = `docs/executive-summary.{ar,en}.md`, `docs/licences.{csv,md}`, `docs/report/annex-sources.md`, `prompts/R9.md`, `prompts/R9_LAUNCH.md` (+ `docs/sources/index.csv` for S-nabrah-005): exactly the addendum's approved set; `test_r8_l6_panel.py:137` swaps "pending native review" for "Status: reviewed" (the approved header change) |
| C2 | `tests/localdata.py` `needs_local` skips only when gitignored inputs are absent | PASS | skipif keyed on `REPO_ROOT / <runs or data path>`.exists(); applied to `test_costs_register` (WB deflator JSON), `test_cp2_gastat_primary` (pilot capture), `test_report_figures` (study run metas, not `runs/` itself, so `make demo`'s `runs/demo` cannot mask them), `test_s6_l6_connected`, `test_study_rj_families` (library JSON); main checkout runs them: 861 passed vs 791 + 70 skipped in the clone |
| C3 | `tests/test_fix_r8.py` | PASS | see B2; `assert len(approved) == 1` and `approved <= set(state(old))` |
| C4 | `common/demo.py`: no magic real-world numbers; fixtures marked | PASS | all quantities from `tests/fixtures/demo_inputs.yaml` (`fixture: true`, `source: fixture`, header "FIXTURE: invented … never cite these values"; `load_inputs` raises if the flag is missing); screening weights from the registered `cities/ksa/assumptions/screening_weights.yaml`; CBA parameters from `economics.params.load()`; code constants are neutral multipliers (1.0, 0.0), the 0.3 s poll and a 10 s terminate wait; API bound to 127.0.0.1 on a free port, terminated in `finally`; `tests/fixtures/README.md` v1.3 lists the file; `tests/test_demo.py` checks label, P10 ≤ P50 ≤ P90 and seed determinism |
| C5 | `common/licences.py credits` | PASS | reads the CSV through `redact_model_ids`, `needs_attribution` on a fixed none-list, Python licences from installed metadata (License-Expression → classifiers → License), JS from the lock file; `--check` exits 1 when stale |
| C6 | `Makefile` | PASS | `demo`, `demo-serve` (port 8766, never 8765/8000), `credits`; `MANIFEST_FLAGS` strict in a full checkout (main: `manifest OK: 388 rows` with no flag) |
| C7 | `.github/workflows/ci.yml` | PASS | `uv sync --frozen`, `make test MANIFEST_FLAGS=--allow-missing`, then `make demo`; `fastapi` and `uvicorn` are main dependencies in `pyproject.toml` lines 26–27, so the demo's API runs without extras; no npm step (GFI-034 records that) |

### D. Standing audits on the new or changed public files

| # | criterion | verdict | evidence |
|---|---|---|---|
| D1 | No model ids or names | PASS | grep `claude-(fable\|opus\|haiku\|sonnet)\|Fable 5\|Hanko\|opus-5\|haiku-5` over README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CITATION.cff, NOTICE, docs/credits.md, docs/release-checklist.md, docs/good-first-issues.md, CHANGELOG.md, both summaries, licences-release/blockers: no hit; README "Models" section names no version; CONTRIBUTING rule 12 replaces the labels with "[wording adapted for publication]" |
| D2 | No content from the author's company | PASS | private-list grep over the same files: no hit; CONTRIBUTING rule 9 reads "no content, branding, data or contacts from the author's business ventures [wording adapted for publication]" |
| D3 | No absolute paths | PASS | grep `/Users/\|\$HOME\|~/` over the same files: only the two rule sentences that forbid them (CONTRIBUTING.md:66, release-checklist.md:15) |
| D4 | Non-partisan, no advocacy | PASS | README: "presents options and evidence and does not advocate for any agency, company or other entity"; no "should build"/"will transform"; no endorsement of any vendor (Nabrah is a register row with its blocker) |
| D5 | Numbers sourced or traceable | PASS | release checklist: 74 files / ≈19 MB / 24 + 46 / 29 PDF / `.git` 67 MB / largest blob 3.8 MB / 146 model-id files / 46 blockers (21/9/2/6/2/3/3) / 16 Transit Costs hits all re-measured and equal (commit count: see O2); status block: 1,689 tracked files, 2,078 source rows, 765 assumptions, 290 licences, 388 manifest rows, 791/70 and 861 tests all re-measured and equal; GFI counts: A5; credits header counts: A2c; README cites no figure beyond "13 regions" and milestone names |
| D6 | Synthetic/uncalibrated label where modelled outputs are mentioned | PASS | README first line (bold), CITATION.cff `message` and `abstract`, CONTRIBUTING §intro and rule 3, credits intro, GFI line 11, CHANGELOG r9 entry, the demo's stdout and its `results.json`/`api_meta.json` (`tests/test_demo.py`) |
| D7 | Version headers on docs files | PASS | `docver OK: 364 files` in both checkouts; the four root community files carry headers too (not required) |
| D8 | Planned lines never styled as existing | PASS | no line YAML, scenario, map or report body changed in R9 (`git diff 5edba39..HEAD --stat`: 40 files, none under `cities/ksa/lines`, `scenarios`, `docs/report/sections`) |

### Standing status checks (agent file step 12)

| item | verdict | evidence |
|---|---|---|
| `docs/STATUS.md` R9 row, CP7 checklist present; numbers match | PASS | line 34 R9 row; "CP7 checklist (R9 builder, 7 Nov 2026)" items 1–9; counts re-measured in D5 |
| `docs/status/main.md` R9 block numbers match measurement | PASS | clone 103 s / 2 s / 791 passed, 70 skipped; main 861 passed; 1,689 files; registers 290 / 2,078 / 765 / 388 |
| Milestone label line `R9: done` | PENDING (not a FAIL) | absent at c5c6efe by the approved sequencing: `prompts/R9_LAUNCH.md` ends "Verifier PASS, then stop with R9: done"; the builder writes it after this report |
| Cost-log row for the R9 run | PENDING (not a FAIL) | `grep R9 docs/cost-log.md` empty: the row is appended after the Claude Code run ends (CLAUDE.md "Costs"); the coordinator confirms it at close |

## 3. Failures

None.

## 4. Spot-check sample (procedure step 9)

Random-row re-verification against cited sources with WebFetch applies to the candidate register, cost register and benchmark dossiers, none of which R9 changed (`git diff 5edba39..HEAD --stat`: no file under `cities/ksa/`); their rows were sampled by verify-R8 and earlier. For R9 the sample is the seven good-first-issue counts recomputed in A5 (all equal) and the release-checklist measurements in D5 (all equal except O2).

## 5. Observations (not FAILs; for the coordinator or Tariq)

- O1 `docs/STATUS.md` line 5 still reads "Last updated: 4 Nov 2026 (INTEGRATE_R8 …)" while the version header says v1.41, 7 Nov 2026.
- O2 "521 commits" in `docs/release-checklist.md` A and `docs/STATUS.md` CP7 item 4: `git rev-list --count` gives 522 at the checklist commit 884270a and 528 at c5c6efe; the checklist itself says to re-run before publishing.
- O3 `make test` hides the pytest summary (`addopts = "-q"` doubled; already GFI-036); the status block's 791/70 and 861 are only visible with `-o addopts=""`.
- O4 `Makefile` `MANIFEST_FLAGS` keys on `data/osm` alone: a partial checkout with other `data/` present but no OSM symlink would also run `--allow-missing` silently.
- O5 `.github/ISSUE_TEMPLATE/*` is in the "You own" list of `prompts/R9.md` but was not created; it is not in the task list or acceptance, and `docs/good-first-issues.md` is the stated substitute.
- O6 Rule 8 says "small licence-compatible tables with a README"; 29 of the 74 tracked `data/` files are PDFs (largest 3.8 MB; 19.5 MB in total). They predate R9 (accepted at CP2), are fully disclosed, and are Tariq's CP7 decision (checklist A, CP7 item 2).
- O7 The Contributor Covenant text was fetched from GitHub on 7 Nov 2026 and `cffconvert` was fetched from PyPI via `uvx`: public reads, disclosed in the status block, no contact or sign-up.
- O8 `docs/policy-brief.md` line 5 still carries "Draft for review at checkpoint CP6; not for circulation": outside the addendum's scope, correctly left to Tariq (checklist D, CP7 item 6).

## 6. Three most important fixes (none blocking)

1. At close: add `R9: done` to `docs/status/main.md` and the R9 cost-log row (the two PENDING items), then refresh the "Last updated" line of `docs/STATUS.md` (O1) and the commit count (O2).
2. Before Tariq's CP7 decision on the tracked `data/` tables, nothing to change in the repository; the decision path is already written (checklist A).
3. Consider making the pytest summary visible in `make test` (GFI-036) so the next verifier can read the pass/skip counts from the README command's own output.

VERDICT: PASS
Overall: PASS
