> **Document version:** docs/status/verify-PUBLISH_PREP_URL.md v1.0 | 12 Nov 2026 | Author: red-team-verifier | Status: verified

# VERIFY_PUBLISH_PREP_URL — repository URL addendum on `main` (read-only review)

**Scope.** `prompts/PUBLISH_PREP_URL.md` applied on the main checkout. Run started at b9f4e5e; the change is commit 20ac17c (`git diff b9f4e5e..20ac17c`: 6 files, +48/−26). HEAD at review: 20ac17c, `git status --porcelain` empty. PUBLISH_PREP itself: PASS earlier (`docs/status/verify-PUBLISH_PREP.md`). This review made no network call, added no remote, pushed nothing, edited nothing but this file.

## Commands run

| Command | Result |
|---|---|
| `make test` (ruff check, ruff format --check, pytest -q, docver, manifest), log `logs/verify-PUBLISH_PREP_URL-make-test.log` | rc 0; `All checks passed!`; `822 files already formatted`; `docver OK: 417 files`; `manifest OK: 388 rows`; real 1m02.7s |
| `uv run pytest -q -o addopts="" -p no:warnings` (summary line, because `addopts = "-q"` plus the Makefile's `-q` hides it) | `1074 passed in 59.54s`, rc 0, 0 failed, 0 skipped (local data present) |
| `uvx --offline cffconvert --validate -i CITATION.cff` | `Citation metadata are valid according to schema version 1.2.0.`, rc 0 |
| `git remote -v` / `git config --get-regexp '^remote\.'` | both empty (rc 1 on the config lookup = no remote keys) |
| `git branch -a` / `git worktree list` | `main` + the 38 track branches and their `.worktrees/` (unchanged); no `public` branch; `ls ~/Documents/Projects/KSA-RailTwin-public*` → no such file |
| `git grep -nIi -E 'traffictwin\|data/osm\|data/jeddah\|data/traffictwin' -- ':!docs/publish' ':!docs/status/verify-PUBLISH_PREP*'` | 551 lines; (file,line) set identical to `docs/publish/traffictwin-references.csv` (diff empty); CSV text column matches HEAD for all 551 rows |

## Criteria

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | URL identical everywhere | **PASS** | `grep -c 'https://github.com/alturkestani/KSA-RailTwin'`: README.md 3 (line 3 badge image + link, line 18 clone, line 107 licence section), CITATION.cff 2 (line 9 `repository-code`, line 10 `url`), docs/publish/checklist.md 4 (line 103 statement, lines 112, 152, 167 `git remote add origin`). Variant grep (`ksa-rail-twin`, `ksa_rail_twin`, `KSA-RailTwin.git`, `git@github.com:`, `<repository URL>`, `<your-account>`) over README.md, CITATION.cff, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, NOTICE, pyproject.toml, web/package.json, docs/publish/: no hit. Every other `github.com` URL in those files is a third-party repository (TrafficTwin, mozilla/diversity, EthicalSource/contributor_covenant, microsoft/GlobalMLBuildingFootprints, openai/whisper, resemble-ai/chatterbox, rhasspy/piper). `-KSA-RailTwin` appears only in checklist.md:103 (the rename fallback), docs/STATUS.md:539 and prompts/PUBLISH_PREP_URL.md:3. Repo-wide, `ksa-rail-twin` occurs only as film render file names (`docs/film.md`, `.claude/agents/film-editor.md`), not as a repository reference. The badge target `.github/workflows/ci.yml` exists (`name: ci`). |
| 2 | CITATION.cff validates; version/date-released unset | **PASS** | cffconvert valid (above). `version: "unreleased (prepared after tag r10-final)"` at line 15 is unchanged from b9f4e5e (line 13 there); no `date-released` key in either version. The `message` block now says only version and date-released are set on release day (diff lines 6–7). |
| 3 | No remote, no export branch/folder, nothing pushed | **PASS** | `git remote -v` empty; no `remote.*` config keys; no `public` branch in `git branch -a`; no `~/Documents/Projects/KSA-RailTwin-public` or `-public-wt`; `git tag` unchanged (last: r8.1, r9, session1-pilot); no `git push` in `Makefile`, `scripts/`, `.github/` (grep rc 1). |
| 4 | Checklist §7: two text-only variants, correct applicability, safe commands, export block unchanged, rename note | **PASS** | checklist.md:105 "Which one applies, from the §1 scan: variant (b)", citing S5, S6, S7, S10; consistent with §1 rows 19–24 (S5 history only, S6 redacted on main but in history, S7 history only, S10 author email on 689 commits and 18 tags). Variant (a) (lines 107–115) is marked "Does not apply … not recommended" and is the only block with `git push -u origin main` + `git push origin --tags` on the private checkout. Variant (b)/Option B (lines 117–155): `cd ~/Documents/Projects/KSA-RailTwin-public` then `git remote add origin …` and `git push -u origin main` of the export folder; comment "not the private main"; line 155 "Push no tags from the export (it has none) and never add this remote to the private repository". Option A (lines 157–169): `git push origin public:main` only; comment "never --all, never --tags, never main". The Option B export/redaction script block (`# --- Option B` … `gitleaks git …`, 24 lines) is byte-identical to `git show b9f4e5e:docs/publish/checklist.md` (diff empty). Option A changed only by the added `git remote add origin` line and the two comments. Rename note present at line 103 ("If the rename from `-KSA-RailTwin` to `KSA-RailTwin` has not happened yet …"). Q7 (line 178) now excludes the URL. See observations O1–O2. |
| 5 | Nothing else changed | **PASS** | `git diff --stat b9f4e5e..20ac17c`: CITATION.cff, README.md, docs/STATUS.md, docs/publish/checklist.md, docs/publish/traffictwin-references.csv, docs/publish/traffictwin.md only. CSV diff: 7 row pairs are line shifts (CITATION.cff 38→40, 42→44; README.md 5→7, 22→24, 36→38, 75→77, 101→103) caused by the 2 added lines in each file, plus one new row `docs/status/main.md,1811` (the VERIFY_PUBLISH_PREP pass-2 block added in a0bfa21, which touched docs/status/main.md +5). Regenerated grep = 551 lines, 245 files, identical (file,line) set; kind counts 17 runtime / 47 code comment / 74 CBA label / 17 manifest / 61 licence / 14 config / 6 test (1 skip guard + 5 text) / 32 agent-skill / 108 record / 175 documentation = 551, matching traffictwin.md and checklist.md §3 (551 in 245). STATUS.md changes: header bump and the PUBLISH_PREP_URL decision-log block only. |
| 6 | Docver headers bumped; README/CITATION carry none | **PASS** | checklist.md v1.1→v1.2, traffictwin.md v1.3→v1.4, STATUS.md v1.52→v1.53 (first lines). `git show b9f4e5e:README.md` and `:CITATION.cff` contain no `Document version` line (grep count 0), same at HEAD; `docver OK: 417 files`. |
| 7 | `make test` green; no home paths; no private company content | **PASS** | rc 0, 1074 passed, 0 failed (above). `grep -nE '/Users/[a-z]\|/home/[a-z]'` on the six changed files: no hit; `git grep` over all tracked files: no hit. Added diff lines grepped for the private company name, code names, keys/tokens: the only hit is the word "secret" in "None is a secret" (checklist.md:105). |
| 8 | No paid calls, nobody contacted | **PASS** | Docs-only diff; no change to `docs/cost-log.*`, `film/` or any vendor ledger; STATUS block and checklist §7 state no GitHub call, no remote, nothing pushed; no network call made in this review either. |

## Observations (not failures)

- **O1.** Variant (a), checklist.md:107, says of S5/S6/S7/S10 "they are in history only; HEAD is clean". That is true for those four items, but a push of `main` under (a) would also publish the six files in `docs/publish/export-exclude.txt` (§2 drop list) and the unredacted private name and code names that R2 redacts in the export (S13, 66 files at HEAD). Variant (a) is marked not applicable, so no criterion fails; one sentence saying that (a) also skips the §2 drop list and the R2 redaction would make it safe to read in isolation.
- **O2.** Option B's closing line (checklist.md:155) says "never add this remote to the private repository", while Option A (line 167) adds the remote from an orphan worktree, which writes it into the private repository's shared config. Option A is already labelled the riskier path and its push is restricted to `public:main`; the wording is slightly inconsistent, not unsafe.
- **O3.** `docs/status/main.md` ends with `PUBLISH_PREP: done`; it has no PUBLISH_PREP_URL block or `PUBLISH_PREP_URL: done` line yet, and `docs/cost-log.md` has no PUBLISH_PREP_URL row. For PUBLISH_PREP both were added after the verifier's PASS (a0bfa21, 387a8e2); the coordinator addendum asks for the same here. Not among criteria 1–8; the coordinator adds them when closing.
- **O4.** `docs/status/main.md` (PUBLISH_PREP block, "Item 7") still records "repo `ksa-rail-twin`" as what checklist v1.0 held. It is a dated status record, not a public-facing file under criterion 1, and the §7 text itself is correct.
- **O5.** Commit 20ac17c carries the author's personal email, as every commit does (S10); consistent with variant (b) applying.

## Three most important fixes (none blocking)

1. Add to variant (a) that pushing `main` also skips the §2 drop list and the R2 redaction (O1).
2. Reconcile the "never add this remote to the private repository" sentence with Option A, or state that Option A does add it and why that is tolerated (O2).
3. When closing: PUBLISH_PREP_URL block ending `PUBLISH_PREP_URL: done` in `docs/status/main.md` and a cost-log row (O3).

VERIFY_PUBLISH_PREP_URL: PASS

VERDICT: PASS
