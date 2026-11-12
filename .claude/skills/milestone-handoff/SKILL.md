---
name: milestone-handoff
description: End-of-milestone procedure: run tests, the manifest and document-header checks and the README command, invoke the red-team-verifier subagent, update docs/STATUS.md with measured numbers and decisions, commit, and write the handoff summary. Use at the end of every milestone R<n> and before stopping a session.
---
> **Document version:** skills/milestone-handoff/SKILL.md v1.1 | 30 Oct 2026 | Author: coordinator | Status: active

# Milestone handoff

Copied from TrafficTwin Jeddah with minimal changes; do not weaken it.

1. `uv run ruff check . && uv run ruff format --check . && uv run pytest -q && uv run python -m common.manifest verify && uv run python -m common.docver check docs prompts .claude` must pass.
2. Run the milestone's README demo command exactly as written in the README; fix the README if it differs from reality.
3. Ask the `red-team-verifier` subagent to check the milestone (it runs on `claude-fable-5-1`, never on the model that wrote the work). Fix every FAIL, then re-run the verifier. Do not declare done with an open FAIL.
4. Update `docs/STATUS.md` (create from the template below if missing). Numbers must be measured in this session, not estimated. Every number carries its run id, seed or source id.
5. Append this run's cost rows: `uv run python -m common.cost_log summary` and copy the total into STATUS.md.
6. Commit: `git add -A && git commit -m "feat(<area>): complete R<n> <title>"`. Check `git status` is clean and no data or secrets are tracked (`git ls-files | grep -E "^(data|runs|movies|film/renders|film/audio)/"` must be empty apart from READMEs and licensed tables). Do not tag (the coordinator tags) and never push.
7. End the session with the handoff summary (also appended to STATUS.md) and the status line `R<n>: done` or `R<n>: blocked - <reason>` in `docs/status/<track>.md`:

```
## R<n> <title> — <date>
Built: ...
Measured: rows in registers, governorates covered / GASTAT count, corridors, run ids and seeds, runtime, test count and time, disk free, cost so far ...
Decisions: ...
Assumptions added: A-... ids
Licences added: items
Could not verify: ...
Next: R<n+1> <title> — first three tasks
```

STATUS.md template:
```
# KSA Rail Twin — status
> **Document version:** docs/STATUS.md v<x.y> | <date> | Author: <agent> | Status: active
Last updated: <date>
Environment: <uv, python, node, git, ffmpeg versions; osrm/sumo/llama.cpp if installed; note: no ollama (removed 31 Oct 2026)>
Disk free (GB): <measured with df -h ~>
Cost so far (USD, list price): <from common.cost_log summary>
Disk confirmation: <"not yet: no downloads, extracts or renders" | "confirmed by Tariq on <date>">
## Milestones
| R | Title | State | Evidence |
## Measured
## Decisions
## Open issues
## Handoffs
```
