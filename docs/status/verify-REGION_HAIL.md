> **Document version:** docs/status/verify-REGION_HAIL.md v4.0 (pass 4, focused) | 31 Oct 2026 | Author: red-team-verifier (`claude-fable-5-1`) | Status: verified

# Verifier report: REGION_HAIL, pass 4 (focused re-check of pass 3 item 7)

Scope (as instructed by the coordinator): pass 3 passed every acceptance item and command and failed only item 7, the status file (`docs/status/r2-hail.md`), on a wrong replaced-row count ("seven") and a name-only description of the relayed matching. This pass re-checks the corrected status file and re-runs the register, doc and command checks that back it. Earlier reports: `verify-REGION_HAIL-pass1.md`, `-pass2.md`, `-pass3.md` (the pass-3 file was copied aside by this pass before overwriting). Read-only; nothing was fixed.

Worktree `.worktrees/r2-hail`, branch `r2-hail`; all deliverables still untracked (`git status --porcelain`: 12 `??` entries, no modified tracked file). Every count below was recomputed from `cities/ksa/regions/hail.parquet` and `cities/ksa/zones/settlements.parquet` with the builder's own functions, not read from the documents.

## Criteria table

| # | item | result | evidence |
|---|---|---|---|
| 1a | Status file: replaced-row count is six and the names equal `docs/regions/hail.md` §4 | PASS | `r2-hail.md` line 18: "Six universe rows are replaced in this way (Al Hulayfah Assofla, Al Ruwda, Al Qa`id, Munifat al Qa`id, An Nisiyah, Al Khuttah)". `hail.md` line 58 lists the same six in the same order. Builder `_apply_relayed_precedence` on the 650-row universe returns 6 overrides: KSA-ST-00297 Al Hulayfah Assofla 8,990→4,151; -00355 Al Ruwda 1,076→2,906; -00952 Al Qa`id 5,523→2,913; -00960 Munifat al Qa`id 467→4,688; -00962 An Nisiyah 1,272→4,597; -00973 Al Khuttah 9,636→3,355. `grep -n seven` on the status file, doc and assumptions: no hit. |
| 1b | Status file: matching described as (Arabic name, Arabic governorate), tatweel removed, 'محافظة ' prefix stripped; no name-only description as the current method | PASS | `r2-hail.md` line 22: "Matching is by (Arabic name, Arabic governorate), with tatweel removed and the universe's 'محافظة ' prefix stripped from governorates; a duplicate that a relayed match could hit is an error." Code agrees: `build_register.py` lines 209-217 (`_ar_key` strips `ـ`, `_gov_key` strips the prefix), 220-234 (keyed by the tuple, duplicate raises), 244-258 (match on the tuple, ambiguous match raises). Docstring line 11: "matched by Arabic name and governorate". The only "by Arabic name" left in the status file is line 18, inside the paragraph headed "Verifier pass 1 — FAIL (fixed here)", i.e. an explicitly historical note, and the pass-2 paragraph (line 31) records the change to (name, governorate). |
| 1c | Status file: docver count matches `common.docver check docs` | PASS (with a note) | Status line 16 says "OK (105 files)". `common.docver check` on a copy of `docs/` without this pass's archived `verify-REGION_HAIL-pass3.md` → `docver OK: 105 files`. On the live tree it now reports 106, the extra file being the pass-3 archive this verifier created at 16:5x after the status file was written (status mtime 16:57:19). The builder's figure was correct when written; the close-out edit should re-run docver and write the then-current count (W1). |
| 1d | Status file: Measured numbers | PASS | Recount from `hail.parquet` (17 × 42): rows 17; `is_governorate_centre` 9; `tag_10k` 4 (Ha'il 448,623 verified; Baqa 19,659 verified; Al-Malwi 15,000 derived/secondary; Ash Shinan 11,560 official/secondary); `tag_5k` 15; `pop_type` grid 5; `pop_source_status` verified 8 / secondary 4 / unverified 5; economic roles 5 (Ha'il 4 + Jubbah 1); `screened: false` 2 (Mawqaq 3,148, Simira' 3,105). Universe recount: 650 Ḥā'il rows, 17 selected, 633 excluded = hamlet 422 + village 209 + town 2; largest excluded resolved population 4,688 (Munifat al Qa`id, after the relayed override); excluded rows ≥ 5,000: 0. All equal the status file lines 11-15 and the doc §2/§4. |
| 2 | `docs/regions/hail.md` §4 equals the parquet and the generator | PASS | `.venv/bin/python -m screening.sweeps.hail.write_doc --dry-run` exit 0; `diff` against `docs/regions/hail.md` shows only a trailing blank line (`90d89`), which the instruction allows. §4 text (line 58): 633 of 650; hamlet 422, village 209, town 2; largest excluded 4,688; six names; matches the recount in 1d. |
| 3a | `region_sweep validate --strict cities/ksa/regions/hail.parquet` | PASS | `ok   hail.parquet: 17 rows, 9 governorates`, exit 0, 1 s. |
| 3b | `pytest -q -p no:warnings tests/test_hail_register.py tests/test_region_sweep.py tests/test_docver.py` | PASS | 14 passed, exit 0, 1 s. |
| 3c | `common.manifest verify` | PASS | `manifest OK: 305 rows`, exit 0 (status line 16 says 305). |
| 3d | `ruff check screening/sweeps/hail tests/test_hail_register.py` | PASS | `All checks passed!`, exit 0. Also `ruff format --check` on the same paths: 3 files already formatted. |
| 4 | Last line of `docs/status/r2-hail.md` is not `REGION_HAIL: done` before a PASS | PASS | Last line (47): "**Verifier:** pass 3 pending (red-team-verifier, read-only; `REGION_HAIL: done` is written only after a PASS)." `grep "REGION_HAIL: done\|REGION_HAIL: blocked"` finds no label line. |

## Failures

None.

## Warnings (not FAILs; fold into the close-out edit that writes the label line)

- **W1 Stale process lines in the status file.** Line 45 "Next: verifier pass 3", line 47 "pass 3 pending" and line 31 "Pass 2's report is at `docs/status/verify-REGION_HAIL.md` before pass 3 overwrites it" describe a state that has passed: pass 2 is at `verify-REGION_HAIL-pass2.md`, pass 3 at `-pass3.md`, and this is pass 4. The docver count will read 106 once the pass-3 archive is in the tree. Update these when `REGION_HAIL: done` is appended; bump the header to v1.2.
- **W2 Generator wording.** `write_doc.py` line 142 (→ `hail.md` line 58) says the relayed table "replaces by name"; the builder matches on (name, governorate). Harmless in the doc's context because the matching rule is spelled out in the status file and the code, but "by name and governorate" would remove the last loose phrasing.

## Spot-check

Not repeated in this focused pass; the pass-3 sample (10 % of register rows against S-cp2-gastat-008 / S-hail-001, live re-reads) stands and no register value changed since (parquet unchanged: 17 rows, 15 at 5k, 4 at 10k, identical populations to the pass-3 table).

## Three most important fixes (none blocking)

1. Replace the stale "pass 3 pending" / "Next: verifier pass 3" / pass-2 location lines and re-run docver for the count at close-out (W1).
2. Change "replaces by name" to "replaces by (Arabic name, governorate)" in `write_doc.py` and regenerate the doc (W2).
3. Carry forward the already-recorded open items (geo-verify re-run, Al-Malwi 1950 tag, Alshazalah match, coverage audit 150 vs 152) into the R2 roll-up; they are not REGION_HAIL blockers.

VERDICT: PASS
