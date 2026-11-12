> **Document version:** docs/r6/judge-v3-backtest.md v1.0 | 3 Nov 2026 | Author: R6_V3 builder (optimizer) | Status: draft

# Judge v3 back-test against judge v2 (CP7-3, R6_V3 task 1)

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.**

**Result: PASS. 8,763 figures compared, 8,763 identical (exact equality, no tolerance; 7,563 of them numeric, the rest station/zone ids, flags and labels).** Rows: `runs/r6/v3/backtest/backtest-v3-vs-v2.csv`; summary `runs/r6/v3/backtest/backtest-summary.csv`; command `uv run python -m optimise.variants backtest`; runs `logs/r6v3/backtest.sh` (log `logs/r6v3/backtest.log`, 18:34–18:43 UTC, 3 Nov 2026).

## The change
- Judge v3 `judge/v3-variants` = commit 0172345 (`fix(optimise): judge v3 variant id`), 2,090 files, SHA-256 `d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee` (`runs/r6/judge/v3-variants.hash.json`; `docs/r6/judge-hashes.md`).
- Code change: one line in `optimise/layout.py` `variant_id`: `f"{item['id']}~{h}"` → `f"{item['id']}-v{h}"` (`diff judge/v2-p5b/optimise/layout.py judge/v3-variants/optimise/layout.py` shows that line only). A variant id is now `<corridor-id>-v<8-hex>`, which matches the LineSpec pattern `^S\d+-[a-z0-9_-]+$` (`tests/test_optimise_v3_variant_id.py`).
- File-by-file comparison of the two hash records: the 776 `runs/` inputs are byte-identical; 13 files differ and 18 are new in v3. Apart from `optimise/layout.py`, every one is a file the judge does not execute or read: documents, prompts, the cost log, registers, `optimise/search.py` and `optimise/report.py` (harness), `scenarios/S6-L*.yaml` and `scenarios/candidate.yaml` (the judge reads `scenarios/S1.yaml` only), `cities/ksa/assumptions/r6_search.yaml` (harness budgets), tests and scripts (they exist because v3 is frozen from the post-R6 branch, not from 7606b43).
- Before freezing (lesson from R6): one layout with every variant field (line type, single track, electrified false, a dropped station, on two corridors) and one track-only library run (`--phase-sweep`) were scored end to end through the fixed code (`runs/r6/v3/prefreeze/`).

## What was compared
| Test | Figures | Identical | v3 output | v2 reference |
|---|---|---|---|---|
| S0 2025: mode totals, rail line totals, population, zones | 16 | 16 | `runs/r6/v3/backtest/S0-2025-v3-variants.json` (`optimise/splitcheck.py`) | `runs/r6/p5b/S0-2025-v2-p5b.json` |
| S0 2025 trips by mode (back-test part A1) | 4 | 4 | `runs/r6/v3/backtest/A-v3-variants/rows-A.csv` | `runs/r6/v3/backtest/A-v2-p5b/rows-A.csv` (part A re-run on the frozen v2 judge) |
| S1 vs S0 demand inputs, 17 quantities × 10 (population, year) groups (A2) | 170 | 170 | same | same |
| S1 committed programme appraisal: NPV, BCR, PVB, PVC at P10/P50/P90, 3 population cases (A3) | 36 | 36 | same | same |
| S6-L1 `score.json`, all horizons and rate cases | 1,687 | 1,687 | `runs/r6/v3/backtest/L1/score.json` | `runs/r6/top5/L1/score.json` (moved to `runs/r6/top5-v2/L1/` at task 5) |
| S6-L2 | 1,682 | 1,682 | `…/L2/score.json` | `…/L2/score.json` |
| S6-L3 | 1,695 | 1,695 | `…/L3/score.json` | `…/L3/score.json` |
| S6-L4 | 1,711 | 1,711 | `…/L4/score.json` | `…/L4/score.json` |
| S6-L5 | 1,762 | 1,762 | `…/L5/score.json` | `…/L5/score.json` |

Excluded from the score.json comparison: `seconds` (wall time) and `layout` (file name). Part A's own pass/fail column compares with the pre-split R5 references and fails for both judges, as expected after the P5b split (`docs/r6/judge-backtest.md` §2); the v2-vs-v3 comparison above uses its `judge` column.

Every v3 run meta records `code_version: judge v3-variants @ 017234562c sha256 d9fef64384e2e25f` and a clean harness version (`runs/r6/v3/backtest/L*/meta.json`).
