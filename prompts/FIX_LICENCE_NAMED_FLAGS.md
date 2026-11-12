> **Document version:** prompts/FIX_LICENCE_NAMED_FLAGS.md v1.0 | 7 Nov 2026 | Author: Tariq (verbatim; header and a short coordinator addendum added) | Status: active

# FIX_LICENCE_NAMED_FLAGS — after FIX_LICENCE_CITE_FACTS verified at c994c35 (7 Nov 2026 AST). One short run on main, Opus, USD 60 guard, verifier inside, then stop. No tag, no push, no remote, no R10, no film.

Tariq approved a small change in common/sources.py so a NAMED_BLOCKERS match does not force BLOCKER when that row's approval records the 7 Nov 2026 AST FIX_LICENCE_CITE_FACTS decision. Require both "7 Nov 2026 AST" and "FIX_LICENCE_CITE_FACTS" in the approval field, then grade the row by its columns as usual. Do not delete the NAMED_BLOCKERS list: a matching row without that approval must still be BLOCKER.

Also update the B9 "why" string so it no longer says the attribution requirement is unanswered (the register now records: attribute Nabrah on published audio). Leave the Nabrah name pattern in place.

Do not lift the Transit Costs hard stop (189) or clear XTTS-v2 (94). They are not named-flag rows; they stay BLOCKER via their own columns (unused / non-commercial). Do not invent a licence. Do not rewrite the 44 already-recorded register answers except where a generator must refresh derived docs from the current cells.

Update tests/test_report_release.py so named flags answered by that approval are no longer asserted to be BLOCKER; keep the B8 guard that no row may name model ids again. Do not disable the test. Change no other code unless a count-asserting test asserts the BLOCKER total you are correcting (then update that assertion to the measured value).

Regenerate docs/licences-blockers.md (`uv run python -m common.licence_blockers write`) and the release note / credits / NOTICE / other generated files the existing commands require. Update the current BLOCKER count wherever status or the release note states 13, and the leftover "46 BLOCKER" figures in docs/good-first-issues.md (around lines 569 and 674), to the measured total. Expected remaining BLOCKER rows: 189 (Transit Costs, unused/hard stop) and 94 (XTTS-v2, non-commercial), unless the generator measures a different total — report the measured count, do not invent one.

Do not change the README body, executive summaries, film/, R8, or the RJ study, except generated annexes if a generator requires them. Do not create tag r9. Do not kill processes you did not start.

Save this prompt verbatim with a version header as prompts/FIX_LICENCE_NAMED_FLAGS.md. Verifier PASS, then stop.

Coordinator addendum (7 Nov 2026): rows 1, 153, 203, 246 and 290 carry their own decision text from FIX_LICENCE_CITE_FACTS rather than the standard approval sentence: check that each of them contains both required strings ("7 Nov 2026 AST" and "FIX_LICENCE_CITE_FACTS"); if one does not, add the two strings to that row's approval cell (the recorded decision text stays), and say so, rather than widening the rule. Add tests in the same test file: a named-flag row with the approval → graded by its columns; the same row without the approval → BLOCKER; 189 and 94 → BLOCKER; and the measured total. Bump `docs/licences-blockers.md`'s generator version string (it lives in `common/licence_blockers.py`, which this run may touch for that line only). Status block in `docs/status/main.md` with the before/after grade table for the 11 named-flag rows, the measured total, `git diff --stat` against the start HEAD, test count; end `FIX_LICENCE_NAMED_FLAGS: done` or `FIX_LICENCE_NAMED_FLAGS: blocked - <reason>`; verifier label `VERIFY_FIX_LICENCE_NAMED_FLAGS` (foreground; it checks the rule change is gated on both strings, the B9 string, 189/94 still BLOCKER, no register answer rewritten, the counts in every named place, no tag/remote).
