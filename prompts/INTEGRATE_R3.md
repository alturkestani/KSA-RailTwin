> **Document version:** prompts/INTEGRATE_R3.md v1.2 | 30 Oct 2026 | Author: coordinator (generated from INTEGRATE_TEMPLATE.md) | Status: active

# INTEGRATE_R3 — integrate the R3 track branches into `main`

You are a Claude Code builder on `claude-opus-5-5` in the **main checkout**, launched by the coordinator after the R3 tracks wrote `done` (or `blocked`) in their status files. **This run is the one place where `git merge` is allowed.** Skills: `milestone-handoff`, `assumptions-register`, `licence-register`, `source-citation`. No pushes, no tags (the coordinator tags), no rewriting of history (`git rebase`, `git reset --hard` and force options are forbidden). Disk gate: nothing new is downloaded here.

## Tasks
1. **Inventory**: list the R3 branches (`git branch --list 'r*'` filtered to this phase, e.g. `r1a r1b r1c r1d` for R1, `r2-<slug>` for R2, the single `r<n>` branch otherwise) and each branch's last status line in its `docs/status/<track>.md`. A `blocked` track is merged too (its partial work is valuable) but its blocker is carried into `docs/STATUS.md` "Open issues".
2. **Merge order**: data and shared-schema branches first, then research, then analysis (R1: `r1a`, `r1c`, `r1b`, `r1d`; R2: region slugs alphabetically, then any `r2` branch; single-track phases: the one branch). For each: `git merge --no-ff <branch> -m "merge(R3): <branch>"`. Resolve conflicts only in files whose ownership rules allow it: `common/` conflicts must be additive (keep both additions; never drop a function); `docs/assumptions.md`, `docs/licences.md/.csv`, `docs/sources/index.csv`, `cities/ksa/sources.yaml` are concatenated and de-duplicated by id (an id collision with different content is written to `docs/STATUS.md` as a conflict, both rows kept with a suffix, never silently picked). Any other conflict stops the merge: write `INTEGRATE_R3: blocked - conflict in <file> between <branches>` and stop.
3. **Register merges**: fold every `docs/assumptions-<track>.md` into `docs/assumptions.md` (keep ids; sort by id), every `docs/licences-<track>.{md,csv}` into `docs/licences.{md,csv}`, every `docs/sources/<track>*.csv` into `docs/sources/index.csv` and regenerate `docs/sources/index.md`; `uv run python -m common.manifest verify`; then delete the per-track register files from the tree (they live in git history).
4. **Verification on main**: `make test` (ruff, format, pytest, docver, manifest); the README demo command; the `red-team-verifier` subagent on the merged state against every acceptance list of the R3 prompts; fix only integration breakage (import paths, additive conflicts, broken links); any substantive FAIL goes to `docs/STATUS.md` "Open issues" with the track that owns it.
5. **Status and changelog**: update `docs/STATUS.md` (milestone table rows for the phase with evidence, measured numbers from this session, decisions, open issues, disk free, cost so far from `uv run python -m common.cost_log summary`); add the `CHANGELOG.md` line(s); commit `chore(R3): integrate tracks and update status`.
6. **Handoff**: status block in `docs/status/main.md` listing merged branches, conflicts and how each was resolved, verifier verdict, test count and time. End with `INTEGRATE_R3: done` or `INTEGRATE_R3: blocked - <reason>`. The coordinator then tags the milestone and, where the phase ends at a checkpoint, wakes Tariq.

## Acceptance (the verifier checks these)
- Every R3 branch is merged with `--no-ff` (visible in `git log --merges`); no history rewriting.
- Registers on main are supersets of the track registers with no silently dropped or overwritten ids.
- `make test` and the README command pass on main; the verifier report for the merged state exists.
- `docs/STATUS.md` reflects the merged state with measured numbers and carries every blocker and conflict.

## Added 31 Oct 2026 (coordinator): paid-model logging
If `common/cost_log.py` has no `add-paid` command yet, add it: `add-paid --vendor <v> --model <m> --usd <x> --step <s> --approved-usd <cap> [--note]` appends a row to `docs/cost-log.md`/`.csv` (run_id `paid-<vendor>-<YYYYMMDD-HHMM>`, track = the step, label `PAID`, models `<vendor>/<model>`, usd_list = the amount, outcome `paid`), keeps a running total per `--step` and prints a warning line `ALERT: <step> at <pct> % of approved USD <cap>` when the total reaches 80 %; `summary` shows paid totals separately from Claude Code runs. Tests. This implements rule 3 of the model policy in `CLAUDE.md`.

## Added 31 Oct 2026 (coordinator, from Tariq's CP4 decisions)
- After merging `r3`, mark the R3 register rows named in `docs/STATUS.md` "CP4 decisions" with `approval: Tariq, 31 Oct 2026 (CP4-na)` (A-pop-001/003/013, A-demand-003/030/032…036/059, A-geo-021, A-mode-021) and set SAR East + North rail to `calibrated` in the calibration table.
- Reconcile the scenario files: `scenarios/S*.yaml` name `cities/ksa/assumptions/modechoice.yaml`; the R3 files are `mode_choice_priors.yaml` + `mode_choice_r3.yaml` — point the scenarios at the R3 files (or add the expected file as a thin include) and validate.
- Log the two R3 conflicts in `docs/sources/conflicts.md`: TGA vs GASTAT intercity rail 2025 (11.7 M vs 10.9 M) and TGA Q1–Q2 bus vs GASTAT.
- Keep the R3 hand-offs visible for R4 in `docs/STATUS.md` Open issues: Landbridge/HHR artefact (1.70 M), air/bus recalibration, 24 created rows without roles, rail graph with transfers, commute criterion on road/rail time, international segment (data in `data/ksa/tables/pilgrims/`, spec in `prompts/R4.md`).
