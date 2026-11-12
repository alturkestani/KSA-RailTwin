> **Document version:** docs/spend-summary.md v1.0 | 12 Nov 2026 | Author: R10 builder (CLOSE_R10 item 4) | Status: draft

# Spend summary at the close of R10

Recomputed on 12 Nov 2026 from the run logs, not copied from earlier summaries. Claude figures are **list-price reference costs only**: Tariq is on a subscription plan, so they are not charges. Paid text-to-speech (TTS) figures are the logged USD equivalents of the credits used (model policy, `CLAUDE.md`).

## Method

- Source: `docs/cost-log.csv`. When this file was written, the `r10` branch and `main` each held rows the other lacked. `main` had the ten Claude run rows for the R10 runs (R10 to FIX_MBS_TITLE). `r10` had the 33 `PAID` TTS rows. Both share the 77 rows from merge base e9e0433. The figures below come from the **union** of the two files: 77 + 10 + 33 = 120 rows, with exact duplicate rows dropped and rows kept in date order. That union is the content `docs/cost-log.csv` has after the CLOSE_R10 merge, so anyone can recompute the figures from the merged file with `uv run python -m common.cost_log summary`.
- Claude runs = every row whose `label` is not `PAID`. Agent-hours = the sum of `duration_min` / 60, which is wall-clock run time as logged. Runs = row count, including the 30 Oct model-id probe row and every retry ("try") row.
- Paid TTS = rows with `label` = `PAID`, split by the vendor named in `models`.
- Not included: the CLOSE_R10 run itself. The launcher appends its Claude row to `main` after the run ends. This run made no TTS calls.

## Claude (list price, reference only)

| scope | runs | agent-hours | USD (list) | tokens |
|---|---|---|---|---|
| whole project, R0 to FIX_MBS_TITLE (all tracks) | 87 | 46.26 | 1,249.86 | 2,808,069,558 |
| of which the `r10` track (R10, FIX_CP8_NOTES, ACCEPT_FIX_CP8_NOTES, R10_HALF2, FIX_HALF2_QUALITY, BUILD_MOVIE, BUILD_MOVIE_EN, FIX_FILM_STORY, FIX_MBS_QUOTE, FIX_MBS_TITLE) | 10 | 9.37 | 191.58 | 391,791,896 |

The per-track breakdown is in the output of `uv run python -m common.cost_log summary` (default `--by track`) run on the merged log.

## Paid TTS (approved cap USD 60; alert at USD 48)

| provider | calls logged | USD | notes |
|---|---|---|---|
| ElevenLabs | 12 | 3.18 | English narrator George. Two early rows (8 Nov A/B test and the free-tier trailer) are USD 0.00. Paid-plan rows are priced at the Creator-plan rate (see the row notes). Separate ElevenLabs approval: USD 15. |
| Nabrah | 21 | 3.88 | Arabic voices Daniah, Norah and Abdullah, priced at the Basic-plan rate (A-film-011). |
| **combined** | **33** | **7.06** | 11.8 % of the USD 60 cap. CLOSE_R10 added USD 0 (no TTS calls). |

## Not logged

- Human time (Tariq's reviews, CP checkpoints) is not logged.
- The `cost-log` rows record list price per run, not per subagent. Agent-hours count each run once, even when it ran parallel subagents.
