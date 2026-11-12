> **Document version:** docs/status/verify-R0.md v1.0 | 30 Oct 2026 | Author: red-team-verifier | Status: verified

# VERIFY_R0 — red-team audit of milestone R0 (skeleton and reuse audit)

Audited: main checkout, branch `main`, commit `5c83726`, `git status --porcelain` empty. Invoked by the R0 builder before handoff (read-only; this file is the only output; nothing committed by the verifier). Inputs read: `CLAUDE.md`, `PROJECT.md` sections 2, 5, 7, 8, 9, `prompts/R0.md`, `prompts/VERIFY_R0.md`, `prompts/_common.md`, `docs/STATUS.md`, `docs/status/main.md`. R0 has no modelling code, so number tracing covers the figures in R0's documents (STATUS, manifest, licence and assumptions registers, README/NOTICE/CHANGELOG claims).

## 1. Commands run (30 Oct 2026, main checkout)

| command | exit | time | output line |
|---|---|---|---|
| `uv run ruff check .` | 0 | 0.2 s | `All checks passed!` |
| `uv run ruff format --check .` | 0 | 0.1 s | `185 files already formatted` (43 Python files plus Markdown code blocks; `ruff format -v` shows the `.md` files are included by ruff's default `include`) |
| `uv run pytest -q` | 0 | 1.5 s wall | `49 passed in 1.05s` |
| `uv run python -m common.docver check docs prompts .claude` | 0 | 0.1 s | `docver OK: 125 files` |
| `uv run python -m common.manifest verify` | 0 | 0.3 s | `manifest OK: 2 rows` |
| `make test` (README command, part 2) | 0 | 1.5 s wall | lint, format, pytest, docver (125 files, incl. `film/script`), manifest all green |
| `make setup && make test` from a **clean clone** (`git clone` to a temp dir, data symlinks recreated with `ln -s "$HOME/..."`, fresh `uv sync`) | 0 | 34 s | identical output; strict `manifest verify` green with the symlinks present |
| `uv run python -m <pkg>.cli version` for `rail network screening costs demand modechoice access economics funding optimise coupling api` | 0 × 12 | — | e.g. `rail ksa-railtwin 0.0.1 code 5c83726 seed 1`; `--seed 7 version` prints `seed 7` |
| `uv run python -m common.cost_log check` / `summary` | 0 | — | `cost log OK: 1 rows`; TOTAL USD 0.19 |

## 2. Acceptance criteria (`prompts/R0.md`, one row each)

| # | criterion | verdict | evidence |
|---|---|---|---|
| A1 | `make test` passes from a clean `uv sync` (ruff, format, pytest < 30 s, docver, manifest verify) | **PASS** | clean clone run above: exit 0 in 34 s total including `uv sync`; pytest `49 passed in 1.05s` (< 30 s); `Makefile` lines 13–26 define `test: lint pytest docver manifest` |
| A2 | Every package has a working `uv run python -m <pkg>.cli version` | **PASS** | 12/12 exit 0 (table above); `common/cli.py` `make_app` supplies `--seed` via `seed_option()` and the `version` command |
| A3 | `cities/ksa/sources.yaml` has the PBF and the Jeddah network with real SHA-256 values and the manifest verifies | **PASS** | recomputed with `shasum -a 256`: `fffc7e74…6ad2073` (255,369,412 bytes) and `3d95746d…29bcbb` (376,548,262 bytes) match `cities/ksa/sources.yaml` lines 14–15 and 27–28; `manifest OK: 2 rows`; edition `2026-10-14T20:21:12Z` and access date 2026-10-15 match `~/Documents/Projects/TrafficTwin/docs/data-sources.md` line 13; network id `ae7645589de321f9` matches TrafficTwin `docs/network-v2.md` line 13; file mtime 2026-10-17 as stated |
| A4 | `docs/cost-log.md` exists with the header row; only real runs; the test writes to a temp copy | **PASS** | `docs/cost-log.md` lines 7–8 header; one real row (`manual-probe`, USD 0.19); no fixture row (`FIXTURE` run id absent); `tests/test_cost_log.py` lines 12–17 copy to `tmp_path`; `cost_log check` OK. Pending, not a FAIL: the row for this builder run (`logs/orch/main-R0-try1.jsonl`, no `result` event yet) is appended by `run_track.sh` line 45 when the run ends |
| A5 | `git ls-files` shows no `data/` payloads, secrets or absolute home paths | **PASS** | `git ls-files \| grep -E '^(data\|runs\|movies\|film/renders\|film/audio)/'` → `data/README.md` only; `grep -rn "/Users/[a-z]" $(git ls-files)` empty (exit 1); secrets grep (api key / secret / token / password / `sk-` / `AKIA`) returns only prose false positives; no tracked `.env`; `tests/test_hygiene.py` enforces the same in CI |
| A6 | Every `.md` under `docs/`, `prompts/`, `.claude/` passes `common.docver check` | **PASS** | `docver OK: 125 files` (= `git ls-files` count of `.md` under those paths plus `film/script`). Note: the 46 agent and skill files carry the header as the first line **after** the YAML frontmatter that Claude Code requires (`common/docver.py` lines 3–4 and `header_line` document this tolerance); `CLAUDE.md` line 53 says "begins with" — see observation O1 |
| A7 | `docs/licences.csv` lists every runtime dependency with its licence and `open = Y` | **PASS** | `uv export --no-dev` → 41 locked runtime packages; all 41 present in `docs/licences.csv` with the locked version, a licence string and `open = Y` (0 missing, 0 version mismatches); `docs/licences.md` has the same 110 rows as the CSV. PyPI spot-checks in section 4 |
| A8 | `docs/STATUS.md` numbers (test count, test time, free disk) were measured in this session | **PASS** | measured now: 49 tests (STATUS: 49); pytest 1.05 s (STATUS: 1.26 s; drift from cache warm-up); `make test` 1.5 s (STATUS: 3.3 s); `df -h ~` 26 Gi free of 460 Gi (STATUS: 26 GiB of 460 GiB); uv 0.11.13, Python 3.12.13, node v22.23.4, git 2.52.0, ffmpeg 9.0.2 all match; manifest 2 rows; 110 licence rows; cost USD 0.19. Docver count: STATUS says 123, measured 125 — the two extra files are `docs/STATUS.md` and `docs/status/main.md`, added in the same commit as the measurement (`git log --diff-filter=A`), so the figure was true when measured; see O2 |

Additional checks requested by the builder's prompt and the agent file:

| check | verdict | evidence |
|---|---|---|
| Determinism of `common.runmeta` | **PASS** | two `write_meta` calls with seed 42, `scenarios/S0.yaml` and the same `extra` → zero differing keys (even `created_utc`, same second); `config_hash` `cca25763…97197b` identical on two CLI calls; `data_hash` equals `common.manifest hash` (`5618bef4…f76093`); `code_version` `5c83726`; label string present |
| Label and ranges helper | **PASS** | `common.labels` prints the exact rule-3 string; `range 1.2 3.4 5.6 --unit "SAR bn"` → `P10 1.2 / P50 3.4 / P90 5.6 SAR bn`; `format_range` rejects unordered inputs |
| Assumptions register | **PASS** | three rows (A-screen-001/002, A-data-001), each with value, range, reason, status `assumed`, used-in; the constants in `common/schemas.py` lines 56–59 cite the ids; A-screen-001/002 trace to `PROJECT.md` line 104 ("included at ≥10k with a ≥5k sensitivity tag") |
| Fixtures are fictional and flagged | **PASS** | every fixture file begins with a `FIXTURE` comment or `"fixture": true`; cost items `status: assumed`, `source: fixture`; corridor `layer: hypothetical`; `tests/fixtures/README.md` forbids citing them |
| Three rail layers, planned vs existing | n/a at R0 | no line YAML beyond the fixture; `LineSpec` carries `layer`; S0/S1 scenario files validate |
| No content from the author's company | **PASS** | `grep -rniE "insurance"` over tracked files returns only the prohibition sentences themselves (CLAUDE.md, PROJECT.md, `_common.md`, agent files, VERIFY prompts) |
| No model ids in public-facing docs | **PASS** | ids appear only in `CLAUDE.md`, `.claude/`, `prompts/`, `docs/cost-log.*`, `docs/licences.*`, `docs/plan.md`, status files and the cost-log test fixture; `README.md` "Models" section uses the labels only; none in `NOTICE`, `CHANGELOG.md`, package READMEs or `web/README.md` |
| Advocacy / "will reduce" language | **PASS** | `grep -rniE "will reduce\|will transform\|should build\|will cut\|will save"` over README, NOTICE, docs and package READMEs: empty |
| No `git push` in scripts or logs | **PASS** | `orchestrate.sh` line 7 and `run_track.sh` contain no push; the only `git push` strings are the prohibition in the agent file and R9's "by Tariq only" |
| Symlinks use `$HOME`, not literal paths | **PASS** | `scripts/link_data.sh` line 7 (`$HOME/Documents/Projects/TrafficTwin`); the symlinks themselves are gitignored (`data/*`) |
| Proprietary items have recorded approval | **PASS** | the one `open = N` item in use (Claude Code orchestrator) carries approval "Tariq, brief v5 rule 12" (`PROJECT.md` rule 12 names the exception); every other non-open row is `planned` and unused at R0 |
| Coverage (13 regions, governorates, benchmark countries) | n/a at R0 | `docs/coverage.md` and the benchmark dossiers are R1/R2 deliverables; not required by `prompts/R0.md` |

## 3. Failures

None.

## 4. Spot-check (seed 20261030; `random.seed(20261030)`, 10 % of each register)

Sample: `docs/licences.csv` data rows 4, 28, 42, 52, 66, 69, 71, 75, 93, 101, 108 (11 of 110); `docs/assumptions.md` row A-screen-002 (1 of 3); `cities/ksa/sources.yaml` row `traffictwin-jeddah-v2-net` (1 of 2).

| id | register says | source checked (30 Oct 2026) | result |
|---|---|---|---|
| L004 Natural Earth | Public domain, no attribution required, status "unverified: confirm version" | naturalearthdata.com/about/terms-of-use: "All versions of Natural Earth raster + vector map data found on this website are in the public domain"; crediting unnecessary | consistent (row may now be marked verified) |
| L028 typer 0.27.3 | MIT, verified 2026-10-30 | PyPI JSON: `license_expression: "MIT"` | consistent |
| L042 fonttools 4.68.0 | MIT, verified 2026-10-30 | PyPI JSON: `license: "MIT"` | consistent |
| L052 pygments 2.21.0 | BSD-2-Clause | PyPI JSON: `license_expression: "BSD-2-Clause"` | consistent |
| L066 OR-Tools | Apache-2.0, planned; unverified | github.com/google/or-tools LICENSE: Apache License, Version 2.0 | consistent |
| L069 PuLP | MIT (to confirm), planned; unverified | github.com/coin-or/pulp LICENSE: MIT permission text, (c) 2002-2005 Jean-Sebastien Roy | consistent |
| L071 PyMC | Apache-2.0, planned; unverified | github.com/pymc-devs/pymc LICENSE: "PyMC is distributed under the Apache License, Version 2.0" (notes MIT-licensed AePPL code) | consistent |
| L075 deck.gl | MIT, planned; unverified | github.com/visgl/deck.gl LICENSE: MIT permission text, "Copyright Vis.gl contributors" | consistent |
| L093 Piper TTS | MIT (code); voices vary | github.com/rhasspy/piper LICENSE.md: "MIT License" (voice licences not on that page; the row correctly says "per voice") | consistent |
| L101 Manim Community | MIT, planned; unverified | github.com/ManimCommunity/manim LICENSE: "MIT License" | consistent |
| L108 Amiri | OFL-1.1, planned; unverified | raw.githubusercontent.com/aliftype/amiri/main/OFL.txt: "licensed under the SIL Open Font License, Version 1.1" (the `/blob/main/LICENSE` path is 404; the licence file is `OFL.txt`) | consistent |
| A-screen-002 | 5,000 persons sensitivity tag, source PROJECT.md W2 | `PROJECT.md` line 104: "included at ≥10k with a ≥5k sensitivity tag" | consistent |
| traffictwin-jeddah-v2-net | sha256 `3d95746d…29bcbb`, 376,548,262 bytes, ODbL-1.0, edition v2 / id `ae7645589de321f9`, file dated 2026-10-17 | `shasum -a 256` and `stat` on the symlinked file; TrafficTwin `docs/network-v2.md` line 13; TrafficTwin `NOTICE` line 14 (derived databases under `data/jeddah/*` remain ODbL) | consistent |

Additional dependency spot-checks against PyPI (direct dependencies): PyYAML 6.0.3 → `license: "MIT"` (register MIT); duckdb 2.0.0 → classifier "OSI Approved :: MIT License" (register MIT); matplotlib 3.11.2 → licence text "License agreement for matplotlib versions 1.3.0 and later", classifier PSF (register "Matplotlib licence (PSF-based ...)"); scipy 1.18.1 → classifier "OSI Approved :: BSD License" (register BSD-3-Clause with the classifier noted). Hit rate: 17/17 consistent; no fabricated or misquoted entry found.

## 5. Observations (not FAILs; for the coordinator)

- O1. Version-header placement: `CLAUDE.md` line 53 says every agent or skill file "begins with" the version line, but Claude Code requires YAML frontmatter first, so the header is the first line after the frontmatter and `common/docver.py` accepts that. Record this exception in `docs/versioning.md` (and the CLAUDE.md wording) so the rule and the tool agree.
- O2. `docs/STATUS.md` "docver OK on 123 files" is now 125 because the measurement preceded the commit that added STATUS.md and main.md themselves; pytest 1.26 s vs 1.05 s and `make test` 3.3 s vs 1.5 s are cache drift. Refresh at the next STATUS bump.
- O3. Cost log: the R0 builder run's row is pending until `run_track.sh` appends it after the run ends; `common.cost_log check` will flag `main-R0-try1.jsonl: result event but no row` if that step is skipped.
- O4. Licence register completeness beyond the criterion: dev-only transitive packages `iniconfig 2.3.1` and `pluggy 1.7.0` (pulled in by pytest) have no row; every runtime package does. `docs/licences.csv` column names (`attribution`, `obligations`, `status`, `approval`) differ from the `licence-register` skill's column list (`attribution_required`, `notes`): the builder recorded this; the coordinator should pick one.
- O5. `ruff format --check` counts 185 files because ruff formats code blocks inside Markdown by default; harmless, but the number in STATUS reads as a Python-file count.

## 6. Three most important fixes (none blocking)

1. Write the frontmatter exception into `docs/versioning.md` / `CLAUDE.md` so "begins with a version line" matches what `docver` enforces (O1).
2. When the builder run ends, confirm `run_track.sh` appended the R0 row and `uv run python -m common.cost_log check` is still OK; refresh the STATUS docver count to 125 (O2, O3).
3. Reconcile the `docs/licences.csv` column names with the `licence-register` skill (or amend the skill), and add rows for the two dev-only transitive packages (O4).

VERDICT: PASS
