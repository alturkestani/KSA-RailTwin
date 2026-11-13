> **Document version:** docs/status/verify-FIX_EXPORT_NAMES.md v1.0 | 12 Nov 2026 | Author: red-team-verifier | Status: verified

# VERIFY_FIX_EXPORT_NAMES (red-team-verifier, read-only; main at 4c04c67)

Scope: `prompts/FIX_EXPORT_NAMES.md` (Tariq's prompt + coordinator addendum; the file is excluded from the export and is not quoted here) and the builder's FIX_EXPORT_NAMES block at the end of `docs/status/main.md` (v1.41). Export under test: `~/Documents/Projects/KSA-RailTwin-public`, commit e4c3ad1abe43e1e97f13b8a00ca5723349cfdc24, claimed built from private commit 506d4ad. Verifier model: `claude-fable-5-1`, which did not write the work. Nothing was fixed, nothing pushed, nobody contacted, no paid call.

Privacy rule followed: the private-name list is referred to only by its path `.publish/private-names.txt` and by counts. The grep pattern used everywhere below was built from that file at run time (`N="($(grep -v '^#' .publish/private-names.txt | cut -f1 | sed 's/ /[ _-]?/g' | paste -sd'|' -))"`, 15 alternatives, case-insensitive, substring-wide, a space in a term matching "-", "_" or nothing). No term appears in this report. Temporary folders were created under `$TMPDIR` and deleted; the shipped export folder was never written to.

## Commands run (exit code, timing)

| command | where | exit | note |
|---|---|---|---|
| `make test` (ruff check, ruff format --check, pytest -q, docver, manifest) | main 4c04c67 | 0 | 1 m 13 s; "All checks passed!", "828 files already formatted", docver OK 422, manifest OK 388 |
| `git grep -a -i -E -l "$N" HEAD -- . ':(exclude)prompts/FIX_EXPORT_NAMES.md'` | main | 0 files | criterion 2a |
| `git archive main` → temp, minus `docs/publish/export-exclude.txt`, `grep -rlaiE` | temp | 0 files | 2,000 → 1,993 files; criterion 2b |
| `grep -rlaiE --exclude-dir=.git "$N" .` | export | 0 files | 1,993 files on disk = 1,993 tracked |
| `pdftotext` of every PDF (null-safe `find -print0`, `</dev/null`), grep | export | 0 of 29 | |
| `unzip -p` of every xlsx/docx/pptx, grep | export | 0 of 29 | all 29 are xlsx |
| `git grep -a -i -E -l "$N" HEAD` | export | 0 files | |
| `git log -1 --format=%B \| grep -iEc "$N"` | export | 0 | commit message |
| `git log --format=%B 5450d57..HEAD \| grep -iEc "$N"` (also from a25cc63) | main | 0 | no commit message since 5450d57 names a term |
| `gitleaks git --no-banner -c .gitleaks.toml .` | export | 0 | 8.30.1; 1 commit, 47.21 MB, "no leaks found" |
| `trufflehog git file://<export> --no-update --json` | export | 0 | 3.99.8; verified 0, unverified 5 |
| `trufflehog filesystem <export> --no-update --json` | export | 0 | verified 0, unverified 9 (the same 5 + 4 copies in `.git/objects`) |
| `scripts/publish_export.sh 506d4ad` into a new temp folder (SRC=main checkout, Q7 identity, LOG=temp) | temp | 0 | rebuilt commit e4c3ad1…, tree 691a939822f0b7ff282ef2291a6fbc6399b21a87; `diff -r --exclude=.git` vs the shipped export: 0 lines |
| `scripts/publish_export.sh 506d4ad` from a temp clone with no `.publish/` | temp | 1 | "private-name list missing: …/.publish/private-names.txt"; no export folder created |
| `uv run pytest -q tests/test_private_names.py` | main | 0 | 2 passed |
| same test in a temp clone without the list | temp | 0 | 1 skipped ("private-name list absent (public clone)"), 1 passed |
| clean-env proof: fresh `git clone` of the export; `env -i HOME=<empty> PATH=~/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin UV_CACHE_DIR=~/.cache/uv LANG=en_US.UTF-8` | temp clone | setup 0 / test 0 / demo 0 | setup 0 s (shared uv cache), test 171 s (ran while `make test` on main was still finishing), demo 2 s; docver OK 421 (one fewer file than main: the excluded prompt), manifest OK 388 |
| reproduce level 2 in the clone (`cp -R docs/publish/figure-inputs/runs/. runs/`, `common.figures build`, `git status --short docs/report/figures docs/deck-figures`) | temp clone | 0 | 16 s; `git status` printed nothing = byte-identical |
| `uv run pytest -q tests/test_s6_l6_connected.py` in the clone after the level-2 copy | temp clone | 1 | `test_map_exists_small_and_idempotent` FAILED: reproduces the builder's pre-existing observation |

## Criteria

| # | criterion | result | evidence |
|---|---|---|---|
| 1 | List file exists, mode 600, gitignored, untracked, holds the previous R2 terms plus the nine new terms | **PASS** | `stat -f '%Lp %z'` → `600 463`; `git check-ignore -v` → `.gitignore:23:.publish/`; `git ls-files .publish` → 0. Content (counts only): 18 lines = 3 comments + 15 term lines, 2 with a TAB replacement; 15 distinct strings (14 after normalising spacing: the builder's "15 lines for 14 terms" is consistent). Cross-check against the prompt without printing: all 9 names in the prompt's item 2 are present (9/9); 6 list terms appeared in `scripts/publish_export.sh` at 5450d57 (the previous R2 set in its two spellings) and 9 did not (the new ones): 6 + 9 = 15. |
| 2a | Own grep: every tracked file at HEAD except the prompt → 0 | **PASS** | `git grep -a -i -E -l … HEAD -- . ':(exclude)prompts/FIX_EXPORT_NAMES.md'` → 0 files. The prompt itself matches (2 lines), as expected. Working tree (tracked + untracked, excluding `.git`, `.publish`, `.venv`, data/runs/logs) → 0 files. |
| 2b | `git archive main` minus the exclude list → 0 | **PASS** | 2,000 files archived; 7 paths removed per `docs/publish/export-exclude.txt`; 1,993 left; `grep -rlaiE` → 0 files. |
| 2c | Rebuilt export: bytes, PDFs, xlsx, git objects, commit message → 0 each | **PASS** | `grep -rlaiE` 0 files; `pdftotext` 0 of 29 PDFs; `unzip -p` 0 of 29 xlsx; `git grep -a -i -E` on e4c3ad1 → 0; commit message → 0. |
| 3a | Script and checklist contain no term, not even in a regex | **PASS** | `grep -ciE "$N"` → `scripts/publish_export.sh:0`, `docs/publish/checklist.md:0`. |
| 3b | Script reads the list at run time and refuses without it | **PASS** | `scripts/publish_export.sh:26` (`PRIVATE_NAMES=${PRIVATE_NAMES:-$SRC/.publish/private-names.txt}`), `:31` (`test -s … \|\| exit 1`), `:37` (pattern built from the file), `:63–68` (perl reads the file for redaction). Run from a temp clone without `.publish/`: exit 1, "private-name list missing", no export created. |
| 3c | Prompt listed in `export-exclude.txt` and absent from the export | **PASS** | `docs/publish/export-exclude.txt` last line = `prompts/FIX_EXPORT_NAMES.md`; in the export `ls prompts/FIX_EXPORT_NAMES.md` → No such file; `git ls-files \| grep -c FIX_EXPORT_NAMES` → 0. |
| 3d | "Drop the pattern" done properly; no "[private name]" inside a grep pattern; rule 9 identical across the three files; test/verifier logic still working | **PASS** | `git diff 5450d57..HEAD`: 73 files, +253/−110. Spot-check of 14 rewritten lines (sampled every 9th added line in `docs/status/verify-*.md`, `prompts/VERIFY_*.md`, `.claude/agents/`, `prompts/R8.md`): all read "content from the author's company" / "private-list grep" with the role kept and no term; 48 removed lines in verifier reports carried grep terms. `tests/test_report_figures.py`: one word dropped from the banned-word tuple (`"claude", "opus", "haiku", "fable"` remain). Rule 9 sentence md5 identical in `PROJECT.md:35`, `CLAUDE.md:19`, `prompts/_common.md:26`. `git grep -F '[private name]'` → 5 lines, all descriptive of the default replacement (`checklist.md:65,311`, `main.md:1884`, `publish_export.sh:12,68`), none inside a search pattern. Non-report files in the diff: `.gitignore`, `CLAUDE.md`, `PROJECT.md`, checklist, exclude list, `main.md`, `prompts/R8.md`, `prompts/_common.md`, the script, the two tests: no screening/cost/appraisal code touched. `make test` green on main (criterion 8). |
| 4 | `tests/test_private_names.py` exists, passes with the list, skips without it | **PASS** | File present (2 tests: tracked-file grep gated on `LIST.exists()`; gitignore + exclude-list check). With the list: 2 passed. In a temp clone without `.publish/`: 1 skipped ("private-name list absent (public clone)"), 1 passed. Also skipped in the clean-env clone of the export. |
| 5 | Export: one commit, Q7 identity, no remote, no tags, one branch; independent rebuild from 506d4ad identical | **PASS** | `git rev-list --all --count` 1; author and committer `Tariq Alturkestani <alturkestani@users.noreply.github.com>` 2026-11-12 12:00:00 +0300; `git remote` empty; 0 tags; branches: `main` only; `git status --porcelain` empty. Independent rebuild into a new temp folder: commit `e4c3ad1abe43e1e97f13b8a00ca5723349cfdc24`, tree `691a9398…` (same SHA and tree hash as the shipped export), `diff -r --exclude=.git` → 0 lines; script summary "files after archive: 2000 / after drop list: 1993 / redacted files: 0; matches: 0; binary files with a term: 0 / git grep of the commit: 0 matches". Temp folder deleted; the shipped export was never written to. |
| 6 | gitleaks 0; trufflehog 0 verified, unverified only the known false positives | **PASS** | gitleaks 8.30.1 with `.gitleaks.toml`: "no leaks found". trufflehog 3.99.8 `git`: 0 verified / 5 unverified = Refiner ×4 (the UUID path segment of the public news URL in `docs/report/annex-sources.md`, `docs/sources/index.csv`, `docs/sources/index.md`, `docs/sources/r2-jazan.csv`) + SQLServer ×1 (bytes in the GASTAT 2010 census xlsx under `data/ksa/tables/gastat/`): exactly the S2/S3 set of `verify-PUBLISH_EXPORT.md`. `filesystem`: 9 = the same 5 + 4 copies inside `.git/objects`. |
| 7 | Clean-env proof: fresh clone, `env -i`, setup/test/demo exit 0; level 2 byte-identical | **PASS** | Clone HEAD e4c3ad1. `make setup` 0 (0 s), `make test` 0 (171 s; docver OK 421, manifest OK 388), `make demo` 0 (2 s; CBA fixture P10/P50/P90 −386 / −47 / 234, 7 dashboard endpoints). Level 2: `common.figures build` exit 0 in 16 s; `git status --short docs/report/figures docs/deck-figures` printed nothing. Clone deleted. |
| 8 | Private repo untouched: no remote; 18 tags; `r10-final` → 92c5472; 5450d57 and a25cc63 ancestors; `make test` green on main | **PASS** | `git remote` empty; `git tag \| wc -l` 18; `r10-final^{commit}` = 92c5472f7364462fd59b5023df2952cb86be7ffb; `git merge-base --is-ancestor` yes for both; 6 commits on top of 5450d57 (734 total); `make test` on main 4c04c67 rc 0 (1 m 13 s). Working tree clean before and after this verification (only gitignored `logs/verify-fix-export-names-*.log` added). |
| 9 | Status block numbers reproduce; block quotes no term; no commit message since 5450d57 contains a term | **PASS** | 187 matches in 70 files at 5450d57: `git grep -a -i -E -o … 5450d57` → 187 occurrences; `-c` → 70 files (93 lines). HEAD → 0. 2,000 archived / 7 dropped / 1,993 shipped: reproduced in 2b and in the rebuild. 29 PDFs / 29 xlsx: reproduced. trufflehog 5 / 9: reproduced. Export commit SHA, identity, date, 1 commit, no remote/tag: reproduced. Clean-env: setup 0 s, demo 2 s, level 2 byte-identical reproduced; `make test` 171 s here vs the builder's 127 s (this run overlapped with `make test` on main; exit codes match). `make test` on main green: reproduced at 4c04c67 (the builder measured at 6c084ec). The `test_s6_l6_connected` observation reproduces in the clone after the level-2 copy. `git grep` of `docs/status/main.md` for the list → 0 (covered by 2a). Commit messages 5450d57..HEAD → 0. |

## Failures

None.

## Observations (not failures)

- O1. `docs/status/main.md` has no start-of-line `FIX_EXPORT_NAMES: done` line yet, and `docs/cost-log.md` has no FIX_EXPORT_NAMES row; both follow the project's pattern of being added by the coordinator after the verifier's verdict (as `PUBLISH_EXPORT: done` was added in bae3736, after the builder's block in 4a00ed4). The coordinator's close-out should add both.
- O2. The builder's clean-env `make test` wall time (127 s) is not reproduced exactly (171 s here) because this verification ran it concurrently with `make test` on main; exit codes and outputs match, and timing is not an acceptance criterion.
- O3. The pre-existing `tests/test_s6_l6_connected.py::test_map_exists_small_and_idempotent` failure after the level-2 copy in a public clone (the test is gated only on `runs/r6/l6/search.json`, which the figure inputs ship, but its map command needs other run files) is confirmed. It is outside this milestone's scope (no code under `tests/`, `optimise/` or `common/` other than the two named test files changed since e73b183) and does not affect `make test`, which passes in the clone. A skip-gate fix remains for Tariq's decision.
- O4. trufflehog is 0 verified / 5 unverified (the known public-URL UUID and GASTAT xlsx bytes), as in VERIFY_PUBLISH_EXPORT; a literal 0 would need a detector or path exclude.

## Spot-check sample

Not a register milestone: no candidate, cost or benchmark rows were changed (the diff touches only prompts, status reports, agent files, the rule-9 sentence, the publish script, the checklist, the exclude list, `.gitignore` and two test files). The spot-check was applied to the rewritten text instead: 14 sampled rewritten lines (seed: every 9th added line of the diff, in file order) plus the three rule-9 sentences; all read correctly with the role kept and no term.

## Three most important fixes

1. Coordinator close-out: append `FIX_EXPORT_NAMES: done` to `docs/status/main.md` and the cost-log row (O1).
2. Decide on the `test_s6_l6_connected` skip gate for public clones (O3; one-line change, Tariq's call).
3. Optional: a trufflehog exclude for the two known false positives if a literal 0 is wanted for public CI (O4).

VERIFY_FIX_EXPORT_NAMES: PASS
VERDICT: PASS
