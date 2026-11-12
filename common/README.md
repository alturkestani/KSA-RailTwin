> **Document version:** common/README.md v1.0 | 30 Oct 2026 | Author: R0 builder | Status: draft

# `common/` (shared helpers)

Shared code every track uses. Changes from track worktrees are ADDITIVE only (`prompts/_common.md`).

| module | CLI | does |
|---|---|---|
| `manifest.py` | `python -m common.manifest add / verify [--allow-missing] / hash` | data manifest `cities/ksa/sources.yaml` (SHA-256, bytes, access date) |
| `cost_log.py` | `python -m common.cost_log add / summary / check` | Claude Code run costs in `docs/cost-log.md` and `.csv` (list price, reference only) |
| `runmeta.py` | `python -m common.runmeta config-hash / show` | `write_meta()` writes `meta.json` (seed, config hash, manifest hash, `git describe`, versions, UTC time) |
| `labels.py` | `python -m common.labels [range p10 p50 p90]` | the label "synthetic demand, uncalibrated: scenario comparison, not a forecast" and the P10/P50/P90 formatter |
| `docver.py` | `python -m common.docver check [paths] / bump <file>` | document version headers (`docs/versioning.md`) |
| `schemas.py` | (library) | pydantic models: `LineSpec`, `RegionRow`, `CostItem`, `CbaCase`, `Scenario`, `ZoneProps`, `SourceRow`, `Param` |
| `cli.py` | (library) | `make_app()`: every package CLI has `--seed` and `version` |
