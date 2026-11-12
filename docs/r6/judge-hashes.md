> **Document version:** docs/r6/judge-hashes.md v1.1 | 3 Nov 2026 | Author: R6 builder (optimizer); R6_V3 builder (judge v3 row) | Status: reviewed

# R6 judge hashes

Full per-file SHA-256 lists: `runs/r6/judge/<name>.hash.json`. Rebuild any judge from its commit with `uv run python -m optimise.judge freeze --ref <commit> --name <new name>` (the `runs/` inputs listed in `optimise.judge.RUN_INPUTS` must be the ones recorded) and check with `optimise.judge verify`. `data/` is linked, not copied, and is covered by the manifest hash (`cities/ksa/sources.yaml`) in every run meta.

| Judge | Commit | Files | SHA-256 | Use |
|---|---|---|---|---|
| `v1-r5` | d5c43c6 (tag `r5`) | 2,052 | `f20091cfc4854dc6078a9b46c311bd10c04074027a2947062fe8c8e0d9354fd3` | back-test only |
| `v2-p5b-uncal` (retired) | db1427c | 2,058 | `64fff0c8dd22f85de450b337cdea2e8e48d2294c97b5a0d5477ac544d532e99e` | split with R5 constants; failed the calibration check, never used by a search |
| `v2-p5b` | 7606b43 | 2,072 | `2bdee7f587c53ba872cc5fd10a61475496daca76dddab6a1271c103644e592ea` | every R6 search and re-score (R6, v2); back-test reference for v3 |
| **`v3-variants`** | 0172345 | 2,090 | `d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee` | **every R6_V3 run (CP7-3)**: v2 + the one-line variant-id fix (`<id>-v<8-hex>`); reproduces v2 exactly (`docs/r6/judge-v3-backtest.md`) |

R6_V3 (judge v3): the harness default is `R6_JUDGE=v3-variants`, `R6_OUT=runs/r6/v3`; full SHA-256 at the start and end of the v3 library (`runs/r6/v3/library/library.json`, `variants-stage1.json`, `variants-stage2.json`), the MILP (`runs/r6/v3/milp/info.json`), every GA run (`runs/r6/v3/ga/*/info.json`) and the re-score (`runs/r6/v3/rescore/rescore.json`); every v3 run meta records `judge v3-variants @ 017234562c sha256 d9fef64384e2e25f`.

Checks: the fast fingerprint (path, size, mtime of every file) before every judge call (`optimise.search.run_judge`); the full SHA-256 at the start and end of the library build and of every GA run (`runs/r6/library/library.json`, `runs/r6/ga/*/info.json`); the verifier re-runs `optimise.judge verify --name v2-p5b`.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
