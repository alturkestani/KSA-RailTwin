> **Document version:** judge/README.md v1.1 | 4 Nov 2026 | Author: R6 builder (optimizer); R6_V3 builder (v3 entry) | Status: reviewed

# `judge/` — the locked R6 judge (read-only copies, gitignored)

Each `judge/<name>/` is a read-only copy of the demand model and appraisal built by
`uv run python -m optimise.judge freeze --ref <git ref> --name <name>`: `git archive` of the ref,
APFS clones of the `runs/` inputs it reads (`optimise.judge.RUN_INPUTS`), `data/` linked to the
manifest-hashed data, then `chmod -R a-w`. Its SHA-256 per file is in `runs/r6/judge/<name>.hash.json`
(summary in `docs/r6/judge-hashes.md`). Rebuild it from the ref and compare with
`uv run python -m optimise.judge verify --name <name>`.

- `v1-r5`: tag `r5` (R5 as merged). Used only for the back-test (`docs/r6/judge-backtest.md`).
- `v2-p5b`: the R6 commit that adds the CP6 P5b zone split (Al-Ahsa G033, Al Jubayl G034) and the
  layout adapter `optimise/layout.py`; the judge of every R6 search and re-score.
- `v3-variants`: commit 0172345, v2 plus the one-line variant-id fix (`<id>-v<8-hex>`, CP7-3); the
  judge of every R6_V3 run (harness default `R6_JUDGE=v3-variants`); reproduces v2 exactly
  (`docs/r6/judge-v3-backtest.md`).

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
