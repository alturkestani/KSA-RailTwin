---
name: cost-log
description: How every Claude Code run is logged in docs/cost-log.md and docs/cost-log.csv with common.cost_log (parsing the stream-json result for list-price USD, duration, tokens and models), the row format, the summary command and how the totals reach docs/STATUS.md and the checkpoint reports. Use after every builder run and at every milestone handoff.
---
> **Document version:** skills/cost-log/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Cost log

PROJECT.md section 3 asks for the actual cost per run in `docs/cost-log.md`. The plan is a subscription, so the USD figures are Claude Code's list-price estimates (`total_cost_usd` in the result event), labelled "list price, reference only"; agent-hours come from `duration_ms`.

## Where the data comes from
`run_track.sh` saves every run as `logs/orch/<track>-<label>-try<n>.jsonl` (`claude -p ... --output-format stream-json --verbose`). The last event with `"type":"result"` carries `total_cost_usd`, `duration_ms`, `duration_api_ms`, `num_turns`, `usage` (input, output, cache creation and cache read tokens) and `modelUsage` (one key per model id with its tokens and cost). `run_track.sh` calls the logger automatically after each try; call it by hand for ad-hoc runs.

## Commands
- `uv run python -m common.cost_log add logs/orch/r1b-R1b-try1.jsonl --track r1b --label R1b --try 1 [--note "..."]` appends one row (idempotent: a log file already logged is skipped with a message).
- `uv run python -m common.cost_log summary [--by track|label|model|day]` prints totals: runs, agent-hours, list-price USD, tokens; `--md` prints the table for `docs/STATUS.md`.
- `uv run python -m common.cost_log check` verifies the CSV and the Markdown table agree and that every `logs/orch/*.jsonl` with a result event has a row.

## Row format (`docs/cost-log.md` table and `docs/cost-log.csv`, same columns)
| date | run_id | track | label | models | try | duration_min | turns | input_tokens | output_tokens | cache_read_tokens | cache_write_tokens | usd_list | outcome | notes |
- `date`: UTC date of the result event; `run_id`: the log file basename; `models`: model ids from `modelUsage` joined by `+`; `outcome`: `done` / `blocked` / `failed` / `rate-limited` (from the status line and the log); `notes`: free text (e.g. "pilot, 4 regions").

## Reporting
`docs/STATUS.md` carries "Cost so far (USD, list price)" and agent-hours from `summary`; every checkpoint report to Tariq states the cost so far and the estimate for the next milestone (from `docs/plan.md`, revised with the measured average per run). TrafficTwin's reference: 27 runs, about 41 agent-hours, about USD 420.

## Rules
- The log contains only real runs; tests use a copy under a temp directory (`tests/fixtures/stream-json-sample.jsonl` is the parsing fixture).
- Never delete or edit a row; corrections are new rows with `notes: corrects <run_id>`.
- Model ids appear here and in `CLAUDE.md` and the agent files only; public documents never cite them.
