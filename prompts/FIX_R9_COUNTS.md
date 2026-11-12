> **Document version:** prompts/FIX_R9_COUNTS.md v1.0 | 7 Nov 2026 | Author: Tariq (verbatim; header and a coordinator addendum added) | Status: active

# FIX_R9_COUNTS — documentation only, after verifying R9 at f11a53c (7 Nov 2026 AST). One short run on main, Opus, USD 60 guard, verifier inside, then stop. No tag, no push, no remote, no R10, no film, no licence-row edits, no code or test changes unless a status-count test asserts a number you are correcting (then update that assertion to the measured value).

Correct these documentation mismatches only:

1. Final tracked-file count is 1,693, not 1,689. 1,689 was correct at the verifier's HEAD c5c6efe; the verifier report plus three issue templates added four files. Update docs/status/main.md (and any other status line that states 1,689 as the final R9 count) so the final figure is 1,693, and note that 1,689 was the count at c5c6efe.

2. "521 at the start of R9" is wrong in docs/STATUS.md and docs/release-checklist.md. Measured: 514 tracked files at pre-R9 4da3bcf, 515 at launch 5edba39, and 530 now. Replace 521 with these measured figures, or drop the incidental historical count. Do not invent another number.

3. Where status says the only fetches were uv's local cache and one uvx cffconvert: also acknowledge the Contributor Covenant 2.1 fetch from GitHub that CODE_OF_CONDUCT.md already documents. Distinguish "no TTS, render or model downloads" from those permitted public source and tool reads.

4. Attribute the test counts (861 passed, docver 364, manifest 388; clone 791 passed / 70 skipped) to the verifier run at c5c6efe, not as a re-run at final HEAD f11a53c. The later commits were documentation, issue templates and the cost-log row.

Do not change the README body, credits, executive summaries, Nabrah or other licence rows, film/, R8, or the RJ study. Do not create tag r9 (the coordinator will tag after this lands, on Tariq's word). Do not kill processes you did not start.

Save this prompt verbatim with a version header as prompts/FIX_R9_COUNTS.md. Verifier PASS, then stop.

Coordinator addendum (7 Nov 2026, measured on the Mac before launch): item 2's figures are **commit counts** (`git rev-list --count`): 514 at 4da3bcf, 515 at 5edba39, 528 at c5c6efe, 530 at f11a53c; the sentences being corrected ("your email on every commit (521 at the start of R9)") are about commits, so write them as commits. Tracked files (`git ls-tree -r --name-only <rev> | wc -l`) were 1,676 at 4da3bcf, 1,677 at 5edba39, 1,689 at c5c6efe and 1,693 at f11a53c; item 1 uses these. Re-measure both at your own start HEAD and state it; every corrected figure names its revision. Only `docs/status/main.md`, `docs/STATUS.md`, `docs/release-checklist.md` (and a count-asserting test if one exists) change; status block in `docs/status/main.md`, ending `FIX_R9_COUNTS: done` or `FIX_R9_COUNTS: blocked - <reason>`; the verifier label is `VERIFY_FIX_R9_COUNTS` (foreground; it re-measures the counts at the named revisions and checks that nothing else changed).
