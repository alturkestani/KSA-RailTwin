> **Document version:** prompts/INTEGRATE_R6_V3_V3.md v1.0 | 3 Nov 2026 | Author: coordinator (from INTEGRATE_R6_V3.md; CP7-3) | Status: active

# INTEGRATE_R6_V3 — integrate the R6_V3 track branch (`r6v3`, judge v3 re-run) into `main`

You are a Claude Code builder on `claude-opus-5-5` in the **main checkout**, launched by the coordinator after the R6 tracks wrote `done` (or `blocked`) in their status files. **This run is the one place where `git merge` is allowed.** Skills: `milestone-handoff`, `assumptions-register`, `licence-register`, `source-citation`. No pushes, no tags (the coordinator tags), no rewriting of history (`git rebase`, `git reset --hard` and force options are forbidden). Disk gate: nothing new is downloaded here.

## Tasks
1. **Inventory**: list the R6_V3 branch (`r6v3`) (`git branch --list 'r*'` filtered to this phase, e.g. `r1a r1b r1c r1d` for R1, `r2-<slug>` for R2, the single `r<n>` branch otherwise) and each branch's last status line in its `docs/status/<track>.md`. A `blocked` track is merged too (its partial work is valuable) but its blocker is carried into `docs/STATUS.md` "Open issues".
2. **Merge order**: data and shared-schema branches first, then research, then analysis (R1: `r1a`, `r1c`, `r1b`, `r1d`; R2: region slugs alphabetically, then any `r2` branch; single-track phases: the one branch). For each: `git merge --no-ff <branch> -m "merge(R6_V3): <branch>"`. Resolve conflicts only in files whose ownership rules allow it: `common/` conflicts must be additive (keep both additions; never drop a function); `docs/assumptions.md`, `docs/licences.md/.csv`, `docs/sources/index.csv`, `cities/ksa/sources.yaml` are concatenated and de-duplicated by id (an id collision with different content is written to `docs/STATUS.md` as a conflict, both rows kept with a suffix, never silently picked). Any other conflict stops the merge: write `INTEGRATE_R6_V3: blocked - conflict in <file> between <branches>` and stop.
3. **Register merges**: fold every `docs/assumptions-<track>.md` into `docs/assumptions.md` (keep ids; sort by id), every `docs/licences-<track>.{md,csv}` into `docs/licences.{md,csv}`, every `docs/sources/<track>*.csv` into `docs/sources/index.csv` and regenerate `docs/sources/index.md`; `uv run python -m common.manifest verify`; then delete the per-track register files from the tree (they live in git history).
4. **Verification on main**: `make test` (ruff, format, pytest, docver, manifest); the README demo command; the `red-team-verifier` subagent on the merged state against every acceptance list of the `prompts/R6_V3.md` acceptance list; fix only integration breakage (import paths, additive conflicts, broken links); any substantive FAIL goes to `docs/STATUS.md` "Open issues" with the track that owns it.
5. **Status and changelog**: update `docs/STATUS.md` (milestone table rows for the phase with evidence, measured numbers from this session, decisions, open issues, disk free, cost so far from `uv run python -m common.cost_log summary`); add the `CHANGELOG.md` line(s); commit `chore(R6_V3): integrate track and update status`.
6. **Handoff**: status block in `docs/status/main.md` listing merged branches, conflicts and how each was resolved, verifier verdict, test count and time. End with `INTEGRATE_R6_V3: done` or `INTEGRATE_R6_V3: blocked - <reason>`. The coordinator then tags the milestone and, where the phase ends at a checkpoint, wakes Tariq.

## Acceptance (the verifier checks these)
- The `r6v3` branch is merged with `--no-ff` (visible in `git log --merges`); no history rewriting.
- Registers on main are supersets of the track registers with no silently dropped or overwritten ids.
- `make test` and the README command pass on main; the verifier report for the merged state exists.
- `docs/STATUS.md` reflects the merged state with measured numbers and carries every blocker and conflict.

## Added 31 Oct 2026 (coordinator): paid-model logging
If `common/cost_log.py` has no `add-paid` command yet, add it: `add-paid --vendor <v> --model <m> --usd <x> --step <s> --approved-usd <cap> [--note]` appends a row to `docs/cost-log.md`/`.csv` (run_id `paid-<vendor>-<YYYYMMDD-HHMM>`, track = the step, label `PAID`, models `<vendor>/<model>`, usd_list = the amount, outcome `paid`), keeps a running total per `--step` and prints a warning line `ALERT: <step> at <pct> % of approved USD <cap>` when the total reaches 80 %; `summary` shows paid totals separately from Claude Code runs. Tests. This implements rule 3 of the model policy in `CLAUDE.md`.

## Added 3 Nov 2026 (coordinator): R6_V3 specifics
- The track re-ran `runs/r6/` outputs with judge v3; replace the main copies with the track's (APFS clone), keep the v2 copies under `runs/_superseded/INTEGRATE_R6_V3/` (gitignored), and clone the new `judge/v3-variants/` read-only directory onto main; `uv run python -m optimise.judge verify` must show v3 intact with the hash recorded in `docs/r6/judge-hashes.md`.
- `docs/STATUS.md`: an R6_V3 milestone row, the layouts that changed (or "no layout changed"), and the final CP7 layout set for R7 (`scenarios/S6-L1..L3.yaml` as left by the track). Do not start R7.
