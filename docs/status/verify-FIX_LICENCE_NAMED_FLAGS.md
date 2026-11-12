> **Document version:** docs/status/verify-FIX_LICENCE_NAMED_FLAGS.md v1.1 | 7 Nov 2026 | Author: red-team-verifier (v1.0 pass 1; v1.1 pass 2) | Status: verified

# VERIFY_FIX_LICENCE_NAMED_FLAGS

Repo `main`; start HEAD 3314577; work commits f6e314c, 5db74eb; status commit 6c6eeb7 (HEAD). Brief: `prompts/FIX_LICENCE_NAMED_FLAGS.md` (Tariq's text plus the coordinator addendum). Status block: `docs/status/main.md` lines 1570–1631. Working tree clean at start (`git status --porcelain` empty).

## 1. Commands run

| command | result | time |
|---|---|---|
| `make test` (ruff check, ruff format --check, pytest, docver, manifest) | rc 0; "All checks passed!"; docver OK 370 files; manifest OK 388 rows | 50 s |
| `uv run pytest -q -o addopts=""` | **865 passed**, 10 warnings, 0 skipped, 0 xfail | 50 s |
| `uv run pytest tests/test_report_release.py` | 23 passed | <1 s |
| `uv run ruff check .` / `uv run ruff format --check .` | rc 0 / "729 files already formatted" | |
| `uv run python -m common.licences check` | 290 Markdown rows, 290 CSV rows, **0 differ** | |
| `uv run python -m common.licences credits --check` | "credits: up to date" | |
| `uv run python -m common.licence_blockers write` | "4 BLOCKER rows"; output byte-identical to HEAD (`git status --porcelain` empty afterwards) | |
| `uv run python -m common.sources licences-release --write docs/licences-release.md` | 290 rows written; byte-identical to HEAD (`git status --porcelain` empty afterwards) | |
| independent recount (`licence_rows` + `release_status`, rows numbered 1..290 in register order) | BLOCKER rows = **[94, 189, 191, 193]**, total **4** | |
| `git diff 3314577 HEAD -- docs/licences.csv docs/licences.md docs/licences-*.csv NOTICE docs/credits.md \| wc -c` | **0** | |
| `git tag --contains 3314577`; `git tag -l 'r9*'`; `git remote -v` | all empty | |

Determinism (procedure step 3): no simulation run in this fix; both generators were re-run and reproduced HEAD byte for byte (table above).

## 2. Criteria

| # | criterion | verdict | evidence |
|---|---|---|---|
| C1 | Rule gated on both strings; list kept; answered row graded by columns | **PASS** | `common/sources.py:238` `NAMED_FLAG_ANSWERED = ("7 Nov 2026 AST", "FIX_LICENCE_CITE_FACTS")`; `:241-243` `named_flag_answered` returns `all(s in ap ...)`; `:295` `if re.search(pat, item) and not named_flag_answered(r): return "BLOCKER"`. `NAMED_BLOCKERS` still defined (diff touches only the B9 why string). Test `tests/test_report_release.py:91` `test_named_flag_yields_only_to_both_strings` asserts both → COMPATIBLE, "" → BLOCKER, "Tariq, 7 Nov 2026 AST" alone → BLOCKER, "FIX_LICENCE_CITE_FACTS" alone → BLOCKER, both + licence "unclear" → BLOCKER; passes. Independent run: the 11 named-flag rows (133, 147, 153, 191, 193, 197, 236, 238, 246, 260, 262) all `named_flag_answered=True`; 9 graded OBLIGATIONS by their columns, 191 and 193 BLOCKER by their `licence` cell. |
| C2 | B9 why string no longer "unanswered"; Nabrah pattern kept | **PASS** | `common/sources.py:230` `r"Nabrah"` unchanged; `:232` "...attribution answered: attribute Nabrah on published audio". `tests/test_report_release.py:110` asserts `"unanswered" not in why` on the stripped Nabrah row; passes. |
| C3 | 189 and 94 still BLOCKER via their own columns | **PASS** | Row 189: licence "All rights reserved (no licence stated)", commercial_use N, approval "" → `('BLOCKER', 'commercial use not allowed (non-commercial terms)')`. Row 94: CPML, commercial_use "N (non-commercial)", approval "" → same reason. Neither matches a NAMED_BLOCKERS pattern. `docs/licences-release.md:160` (94) and `:255` (189) show **BLOCKER**; `docs/licences-blockers.md` HARD STOP section for #189. Test `tests/test_report_release.py:122` passes. |
| C4 | No register answer rewritten; rows 1, 153, 203, 246, 290 carry both strings | **PASS** | Register diff 0 bytes (command table). Approval cells read from `docs/licences.csv`: row 1 "...public citation of Claude approved (Tariq, 7 Nov 2026 AST; FIX_LICENCE_CITE_FACTS)"; 153 "...attribute Nabrah on published audio (Tariq, 7 Nov 2026 AST; FIX_LICENCE_CITE_FACTS)"; 203 "Tariq, 7 Nov 2026 AST (CRS definitions via PROJ/pyproj, no redistribution; FIX_LICENCE_CITE_FACTS)"; 246 and 290 "Tariq, 7 Nov 2026 AST (alignment sidecars released as ODbL share-alike derived databases; FIX_LICENCE_CITE_FACTS)". All five contain both strings; none was edited. |
| C5 | Measured BLOCKER total stated correctly everywhere; honest explanation; no licence invented; rule not widened | **PASS** | Independent recount = 4 (94, 189, 191, 193). `docs/licences-blockers.md:7` "Count: 4 BLOCKER rows", `:19` total 4, groups 2/1/1 (v1.2 header). `docs/licences-release.md` v0.6: §5 table rows 160/255/257/259 are the only **BLOCKER** cells; §1 sentences B1 (`:21`) and B2 (`:22`) say the row "stays BLOCKER in section 5 on its own columns: its `licence` cell reads unclear"; B3–B7, B9 (`:23-29`) say OBLIGATIONS; §2 (`:35`) and §6 (`:402`) Nabrah sentences say OBLIGATIONS; consistent with the regenerated table. `docs/STATUS.md:400` CP7 item 5 "4 BLOCKER rows (13 before FIX_LICENCE_NAMED_FLAGS, 46 before FIX_LICENCE_CITE_FACTS)" naming the four rows and "no licence invented". `docs/release-checklist.md:26` "4 BLOCKER rows ... unclear terms 2, non-commercial or all-rights-reserved 1, models and voices 1" naming the four. `docs/good-first-issues.md:569` "4 BLOCKER rows ... #94, #189, #191, #193", `:674` "H. licence blockers: 4 rows (46 at R9), 2 with a B-number (B1, B2)". Status block table lists 11 rows before → after with 191/193 BLOCKER and "Measured BLOCKER total: 4 (13 before)", explains the prompt expected 2 and why 191/193 remain (own `licence` cell "unclear"), and flags the decision for Tariq. Register cells of 191/193 unchanged (C4); rule requires both strings (C1). No stale "13 BLOCKER" statement remains in the named docs (grep; the one `13 rows` hit at `docs/STATUS.md:20` is the INTEGRATE_R3 CP4-approval count, unrelated). |
| C6 | Tests: B8 guard, four new tests, nothing disabled; `make test` rc 0; `licences check` 0 differ | **PASS** | `tests/test_report_release.py:81` B8 guard "a register row names model ids again" kept inside `test_named_blocker_rows_are_blockers` (`:70`); new `test_named_flag_yields_only_to_both_strings` (`:91`), `test_named_flag_rows_with_and_without_the_approval` (`:110`), `test_transit_costs_and_xtts_stay_blockers` (`:122`), `test_measured_blocker_total` (`:130`, `== 4`). `grep -n "pytest.mark.skip\|xfail\|pytest.skip"` on the file: no hits. 23 passed in the file; 865 passed overall; `make test` rc 0; `common.licences check` 0 differ. No other test asserts the blocker total (grep of `tests/` for `== 13` / `== 46` hits only unrelated file-count asserts in `test_report_build.py:86`, `test_region_sweep.py:26`). |
| C7 | Only allowed files touched; blockers generator VERSION line only; version bumped | **PASS** | `git diff --stat 3314577 HEAD`: 9 files (`common/licence_blockers.py` 2 lines, `common/sources.py` 13, `docs/STATUS.md` 4, `docs/good-first-issues.md` 6, `docs/licences-blockers.md` 51, `docs/licences-release.md` 52, `docs/release-checklist.md` 4, `docs/status/main.md` 65, `tests/test_report_release.py` 56). `common/licence_blockers.py` diff = `VERSION = "1.1"` → `"1.2"` only (`:27`); `docs/licences-blockers.md:1` header v1.2. README, executive summaries, `film/`, R8 report, RJ study: not in the diff. The status block's stated `git diff --stat` (8 files, +120/−68, before the block) matches `git diff --stat 3314577 5db74eb`. |
| C8 | No tag, no remote, no push | **PASS** | `git tag --contains 3314577` empty; `git tag -l 'r9*'` empty; `git remote -v` empty (no remote exists, so no push is possible); no `git push` in the three commits' diffs. |
| C9 | No model names/ids introduced into public-facing docs; no absolute home paths | **PASS** | Added lines of `docs/licences-release.md`, `docs/licences-blockers.md`, `docs/release-checklist.md`, `docs/good-first-issues.md`, `docs/STATUS.md` grepped for `claude-(fable\|opus\|haiku)`, "Fable 5", "Opus", "Hanko": no hits. `git diff --name-only 3314577 HEAD \| xargs grep -n "/Users/[a-z]"`: no hits. |
| C10 | Status block ends with `FIX_LICENCE_NAMED_FLAGS: done` or `... blocked - <reason>` (coordinator addendum; CLAUDE.md workflow: "ending each milestone with `R<n>: done` ... the orchestrator greps for that line"; verifier procedure step 12 "the milestone label line is present") | **FAIL** | `grep -rnE "NAMED_FLAGS:? ?(done\|blocked)" docs/status/main.md docs/STATUS.md docs/status/*.md` returns nothing. The block (`docs/status/main.md:1570-1631`) ends at `:1631` with "No tag; no remote; no push; no process killed." Every earlier fix block ends with the label line (`:663` `FIX_R8_RTL: done`, `:927` `FIX_HHR_REROUTE: done`, `:1450` `FIX_R9_COUNTS: done`, `:1568` `FIX_LICENCE_CITE_FACTS: done`). The addendum requires it explicitly: "end `FIX_LICENCE_NAMED_FLAGS: done` or `FIX_LICENCE_NAMED_FLAGS: blocked - <reason>`". |

Procedure items not applicable to this fix: number tracing and the P10/P50/P90, coverage, benchmark, CBA, film-script and tone checks (no model output, figure, register answer, coverage table or film file changed; the register diff is empty). The cost-log row for this run is not yet present (`grep NAMED_FLAGS docs/cost-log.md`: none); as with FIX_LICENCE_CITE_FACTS (row added at c994c35 after its verifier), it is appended at run end. Not graded, but it must be added before the run closes.

## 3. Failures

**F1 (C10).** `docs/status/main.md` FIX_LICENCE_NAMED_FLAGS block has no closing `FIX_LICENCE_NAMED_FLAGS: done` line. Evidence: grep above returns nothing; last line of the block (`docs/status/main.md:1631`) is "No tag; no remote; no push; no process killed." The orchestrator's handoff grep will not find the run's state. Every substantive criterion C1–C9 passes; the fix is one line plus a minor header bump of `docs/status/main.md`, but the criterion is an explicit addendum requirement and is open.

## 4. Spot-check sample

Not applicable as a random sample: no register row, cost row or benchmark figure changed (register diff 0 bytes). Instead, all five addendum rows (1, 153, 203, 246, 290) and the four BLOCKER rows (94, 189, 191, 193) were read directly from `docs/licences.csv` and re-graded with `release_status` (section 2, C3–C5); results match the status block's table and the generated documents. Seed: none (exhaustive, not sampled).

## 5. Three most important fixes

1. Append `FIX_LICENCE_NAMED_FLAGS: done` as the last line of the block in `docs/status/main.md` (bump its header minor), then re-verify (C10).
2. Append the cost-log row for this run (`uv run python -m common.cost_log add <jsonl>`) when the run closes, as the block itself promises.
3. For Tariq (not a defect of this run): decide rows 191 (MoF FY2026) and 193 (PFRAM), which stay BLOCKER only because their `licence` cell reads "unclear": record a terms value (for example "no licence statement; facts cited only") or accept them as disclosed blockers. Do not widen the named-flag rule.

VERDICT: FAIL (pass 1, superseded by section 6)

## 6. Pass 2 (7 Nov 2026; HEAD 4214b77)

Scope: re-check C10 and confirm C1–C9 still hold after the builder's commit 4214b77 (the only commit since pass 1, which ended at 6c6eeb7).

| check | result | evidence |
|---|---|---|
| Commit after pass 1 touched only `docs/status/` | **PASS** | `git diff --stat HEAD~1 HEAD`: `docs/status/main.md` (+5/−1) and `docs/status/verify-FIX_LICENCE_NAMED_FLAGS.md` (+56, the pass-1 report); 2 files, 61 insertions, 1 deletion. No code, register, generator, test or public document changed, so the evidence for C1–C9 in section 2 is unchanged. |
| C10: closing label line | **PASS** | `grep -n '^FIX_LICENCE_NAMED_FLAGS: done$' docs/status/main.md` → `1635:FIX_LICENCE_NAMED_FLAGS: done` (rc 0). Line 1635 is the last line of the file (`wc -l` = 1635); plain text at column 1, no backticks, bullet or trailing characters (checked with `cat -v`). Header bumped to v1.34 with the reason ("v1.34 verifier result and close line"). The preceding paragraph (`:1633`) records the pass-1 result accurately (C1–C9 PASS, C10 FAIL) and still promises the cost-log row at run end. |
| Tests / docver spot-check | **PASS** | `uv run pytest -q tests/test_report_release.py` → 23 passed, rc 0 (0.4 s). `uv run python -m common.docver check docs` → "docver OK: 231 files", rc 0. |
| Hygiene | **PASS** | `git status --porcelain` empty before and after the checks; `git tag --list` still ends `r8, r8.1, session1-pilot` (no new tag); `git remote -v` empty (no remote, no push possible). |

Open, not graded (unchanged from pass 1): the cost-log row for this run is not yet in `docs/cost-log.md` (`grep -n "FIX_LICENCE_NAMED_FLAGS" docs/cost-log.md`: none); the status block states it is appended at run end, as was done for FIX_LICENCE_CITE_FACTS. Fix 3 of section 5 (rows 191 and 193, a decision for Tariq) also stands.

F1 is closed. All criteria C1–C10 PASS.

VERDICT: PASS
