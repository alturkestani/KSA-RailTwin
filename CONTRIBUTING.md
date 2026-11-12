> **Document version:** CONTRIBUTING.md v1.2 | 12 Nov 2026 | Author: report-writer (R9); PUBLISH_PREP (v1.1: fresh-clone behaviour, skips, optional TrafficTwin and Chrome, consistent with the README); PUBLISH_EXPORT (v1.2: TrafficTwin is an optional private companion, Q6) | Status: draft

# Contributing to KSA Rail Twin

KSA Rail Twin is a personal, open-source, non-partisan economic feasibility study of a Saudi rail network. Simulation is the tool; the decision case is the product. Contributions are welcome when they keep to the rules below. Every modelled output is **"synthetic demand, uncalibrated: scenario comparison, not a forecast"**.

By taking part you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). Security issues go privately to the maintainer ([SECURITY.md](SECURITY.md)), not to a public issue.

## 1. Setup

You need [uv](https://docs.astral.sh/uv/), `git` and `make`. Python is pinned to 3.12 by `pyproject.toml` and `uv.lock`; never `pip install` into a system Python.

```bash
uv python install 3.12
make setup            # = uv sync (installs the locked dependencies and the dev group: ruff, pytest)
make test             # the README command
```

`make test` runs four steps:

| step | command | what it checks |
|---|---|---|
| `lint` | `uv run ruff check .` and `uv run ruff format --check .` | lint and formatting (line length 100) |
| `pytest` | `uv run pytest -q` | unit tests on the tiny fictional fixtures in `tests/fixtures/`; they run in seconds, and no national-scale run is ever part of the tests |
| `docver` | `uv run python -m common.docver check docs prompts .claude film/script` | every document carries a version header |
| `manifest` | `uv run python -m common.manifest verify` | every data file in `cities/ksa/sources.yaml` still has its recorded SHA-256 |

`data/` is not in the repository, so the manifest step cannot find the files in a fresh clone. The Makefile switches to `--allow-missing` by itself when `data/osm` is absent, and CI passes `MANIFEST_FLAGS=--allow-missing` explicitly. With the data built or downloaded, the check verifies every row. (`make data-links` links the author's local TrafficTwin checkout, read-only. TrafficTwin Jeddah is the author's optional private companion project (not public; not required to run, test or reproduce this repository): see `docs/publish/traffictwin.md`.)

In a fresh clone some tests **skip with a reason** instead of failing: the ones that need the gitignored `runs/` or `data/` (`tests/localdata.py`), headless Chrome (the Arabic render probe; set `CHROME_PATH` if Chrome is installed elsewhere) or the TrafficTwin checkout (set `TRAFFICTWIN` to its path). No test calls a paid API. A skip is fine; a failure is not.

`make demo` runs the fixture-scale demo: screening on the fixtures, then the fixture cost-benefit case, then the dashboard API on fixture data. It needs no `data/` and no network for the Python steps. Its outputs are fixture results, not study results, and carry the same label.

Other targets: `make cost` (cost-log summary), `make status` (milestone lines), `make region-prompts` (regenerates the per-region prompts), `make dashboard` (builds `web/` and serves the API and app on `127.0.0.1`; needs `cd web && npm install` once).

Engineering conventions: Python 3.12, type hints, `ruff` for lint and format, `pytest`, TypeScript strict in `web/`. Every module has a CLI (`uv run python -m <package>.<module> ...`) and a test on the fixtures. Every run takes `--seed` and writes `meta.json` (seed, config hash, data hash, code version from `git describe --always --dirty`).

## 2. The non-negotiable rules

These twelve rules are copied from `PROJECT.md` section 2. In them, "I", "me" and "my" mean the maintainer, Tariq Alturkestani. Two phrases are adapted for this public file and marked with square brackets: rule 9 names a company of the author's that has no part in this project, and rule 12 names the coding assistant's internal model labels; neither name is repeated here. Everything else is verbatim.

1. **No fabricated numbers.** Every figure is sourced (URL, publisher, date, access date) or flagged as an assumption in `docs/assumptions.md` (value, range, reason, status) through the `assumptions-register` skill. "Unknown/unverified" is acceptable. A guess presented as fact is a verifier FAIL. This applies equally to costs, benchmarks, survey findings and quotes.
2. **No silent omissions.** Every region and every GASTAT governorate appears in the coverage table, either as screened (with the result) or as excluded (with the reason). Every benchmark country the brief names appears in the benchmark dossier, with its findings or "no reliable data found". A gap is a verifier FAIL.
3. Label every modelled output **"synthetic demand, uncalibrated: scenario comparison, not a forecast"** until calibration says otherwise. Write "in the model, X reduced by", never "will reduce". Cost and benefit figures are always ranges (P10/P50/P90), never single points.
4. Use only public, licence-compatible data (open-source first, rule 12): OSM (ODbL, credited on every map), GASTAT (credited; derived tables marked as derived), SAR/HHR published facts, open population grids (GHSL/WorldPop, checking the licence), and published reports and peer-reviewed literature (cited). No Google, TomTom or HERE traffic, nothing scraped against a site's terms, and no imagery crops committed.
5. Planned lines are **"announced/planned"** with a source and date, never "existing". Keep three layers apart: `existing`, `committed/under procurement`, `hypothetical (ours)`.
6. Every scenario is compared against a matched baseline on the same zones, seed and parameters, with a sensitivity band. Appraisal follows a named standard (section 6d) and states any departures.
7. No real-world action. Builders and the coordinator never `git push`, publish, post, email, contact any agency, company or person, or field a survey. Surveys are **designed only**; humans field them. Do not sign up for, pay for, or send data to any external service (for example a cloud TTS provider) without my approval. Ask first, and use free tiers or trials only once I agree. I publish.
8. Commit nothing under `data/`, `runs/`, `movies/` or imagery, except small licence-compatible tables with a README. No secrets, no absolute home paths.
9. Keep this project personal. It has no content, branding, data or contacts from the author's business ventures [wording adapted for publication]. It stays independent and non-partisan: present options and evidence, and do not advocate for any entity.
10. Determinism: every run takes `--seed` and records seed, config hash, data hash and code version.
11. The **verifier** signs off every milestone: tests pass, the README command runs, acceptance criteria are met, every number traces to a source or a `runs/` output, coverage is complete, the assumptions register is complete, and the licence & openness register is complete. An open FAIL means the milestone is not done.
12. **Open-source first, as much as possible: data, models, software and voices.**
   - **Data:** use open and public sources first (section 2a). Proprietary or paid data is allowed only when no open alternative exists. In that case, flag it, explain why, and get my approval before use.
   - **Software:** use open-source tools (section 2a).
   - **AI models inside the pipeline** (extraction, OCR, translation drafts, embeddings, classification, local LLM tasks): prefer open-weights models run locally.
   - **Voices and audio:** open-source TTS run locally comes first. Commercial TTS and a human narrator are fallbacks only.
   - **The orchestrators are the exception.** Claude itself (supervisor and coders) [wording adapted for publication] stays as my chosen orchestrator and coder.
   - Every dataset, model, tool, voice, font, music track and image goes into the **licence & openness register** (`docs/licences.md` plus `docs/licences.csv`) with these columns: item, version, source URL, licence, open (Y/N), commercial use allowed (Y/N/unclear), attribution required (text), share-alike or other obligations, and where it is used. Before any public or commercial release, check licence compatibility (for example ODbL share-alike on derived databases, non-commercial model licences, CC-BY-NC music). Flag conflicts and do not resolve them silently.
   - **Compute:** prefer local compute on my Mac (Apple M3 Pro, 18 GB RAM, no CUDA; use Metal/MPS or CPU builds). Heavy jobs (large fine-tunes, 4K renders, big LLMs) may later move to sovereign or cloud GPU **only with my approval** (rule 7).

What this means for a contributor in practice:

- **No contact, no fieldwork.** Contributors never field the survey (`docs/survey/` is a design only), and never contact an agency, company or person on the project's behalf. The maintainer publishes.
- **Wording.** Write "in the model, X reduced by ...", never "will reduce". Every cost and benefit is a P10/P50/P90 range. Planned lines are "announced/planned" with a source and date.
- **Non-partisan.** Present options and evidence; do not advocate for or endorse any agency, company or programme.
- **Gitignored.** `data/`, `runs/`, `logs/`, `movies/`, `film/renders/`, `film/audio/`, `.env` and `.env.*` are gitignored. The only exception under `data/` is `data/ksa/tables/` (small licence-compatible tables, each with a README stating its licence).
- **No secrets, no absolute paths.** No API keys, tokens or passwords in any tracked file; keys are read from environment variables only. No absolute home paths in tracked files (`~` or `$HOME` only inside shell scripts).

## 3. Commits and the three versioning layers

The binding policy is [`docs/versioning.md`](docs/versioning.md). All three layers are required.

1. **Code: git.** Conventional commits, small and often: `feat(screening): ...`, `fix(economics): ...`, `docs(benchmarks): ...`, `data(...)` for manifest rows, `chore(...)`, `test(...)`, `film(...)`. Milestones are annotated tags (`r0`, `r1`, ..., `r9`) set after the verifier's PASS, with one section per tag in `CHANGELOG.md`.
2. **Data: the manifest `cities/ksa/sources.yaml`.** One row per dataset, extract, downloaded table, model weight file or media asset (id, name, publisher, URL, edition, licence, access date, SHA-256, bytes, local path, used_in). A changed upstream file gets a new row with a new edition, never an overwrite. Check with:
   ```bash
   uv run python -m common.manifest verify      # recomputes every hash; fails on a mismatch
   uv run python -m common.manifest hash        # the manifest's own hash (recorded as data_hash in meta.json)
   ```
3. **Documents: version headers.** Every Markdown file under `docs/`, `prompts/`, `film/script/`, `.claude/agents/` and `.claude/skills/` starts with
   `> **Document version:** <path or name> v<major.minor> | <date> | Author: <agent or person> | Status: draft | reviewed | verified`
   (agent and skill files: the first line after the YAML frontmatter). Bump the minor on every substantive edit and the major when the structure changes. Only the verifier or the maintainer sets `Status: verified`.
   ```bash
   uv run python -m common.docver check docs prompts .claude film/script
   uv run python -m common.docver bump <file>            # add --major for a structural change
   ```

## 4. How to add a source

Every number, quote and factual claim cites a source record (skill [`source-citation`](.claude/skills/source-citation/SKILL.md)). Two registers are involved: the **data manifest** (which bytes we used) for any file the pipeline reads, and the **citation index** (what we took from where) for every figure in a document.

**A data file the pipeline reads.** Put it under `data/ksa/<area>/` (gitignored), then register it before computing anything from it; the command computes the SHA-256 and size:

```bash
uv run python -m common.manifest add --id <stable-id> --name "<name>" --publisher "<publisher>" \
  --url <url> --edition "<upstream version or date>" --licence <SPDX id or terms name> \
  --path data/ksa/<area>/<file> --used-in <packages> [--accessed YYYY-MM-DD] [--notes "..."]
uv run python -m common.manifest verify
```

The row's `licence` must match the item's row in `docs/licences.csv` (section 6).

**A cited figure or claim.** The canonical index is `docs/sources/index.csv`; `docs/sources/index.md` is its generated human view. There is no `add` command (the one named in the skill was never built), so the procedure is:

1. Append one row to `docs/sources/index.csv` with the columns
   `id, claim, value, unit, url, publisher, title, published, accessed, locator, quote, status, primary_to_find, used_in`.
   The id is `S-<area>-<nnn>` (or the track prefix in use, for example `S-r5-cba-...`), unique and never reused. `value` is exactly as printed; `accessed` is the day you read it (Asia/Riyadh); `quote` is at most 25 words, verbatim; `status` is `verified` (read on the publisher's own site or document), `secondary` (an aggregator or press relay; then `primary_to_find` is required) or `unverified` (could not be read; it may be mentioned but cannot feed a model).
2. Regenerate the Markdown view: `uv run python scripts/regen_sources_index_md.py "<who, date>"`.
3. Cite it inline as `[^S-xxx]` with a footnote, or `(S-xxx)` in a table; in YAML as `source: S-xxx`.
4. Check that every cited id exists: `uv run python -m common.sources check <file> [<file> ...]`.
5. If two sources disagree, keep both records and add an entry to `docs/sources/conflicts.md`; never pick one silently.

In a track worktree, a builder may keep per-track source CSVs under `docs/sources/` (for example `cost-ksa.csv`, `bench-*.csv`); integration folds their rows into `index.csv`. Documents in both English and Arabic must pass `uv run python -m common.sources bilingual-check <en.md> <ar.md>` (every number matches digit by digit).

## 5. How to add an assumption

Any parameter that describes the real world (a threshold, weight, value of time, coefficient, cost uplift, discount rate, growth rate, dwell time) appears twice (skill [`assumptions-register`](.claude/skills/assumptions-register/SKILL.md)):

1. **In YAML**, never as a constant in code: under `cities/ksa/assumptions/*.yaml` or the module's config, with either a `source:` (an `S-xxx` id) or an assumption reference. The live files use the pattern

   ```yaml
   threshold: {value: 10000, unit: persons, assumption_id: A-screen-001}
   ```

   or `assumption: "<reasoning and plausible range>"`. The pydantic loaders in `common/schemas.py` reject a parameter that has neither (`parameter needs source: or assumption:/assumption_id:`).
2. **As a row in `docs/assumptions.md`**, in the register table:

   ```
   | id | parameter | value | unit | range | source or assumption | status | used in |
   ```

   - `id`: `A-<area>-<nnn>` (for example `A-screen-004`, `A-cost-012`, `A-cba-003`; region sweeps use the slug, `A-<slug>-001`).
   - `value`: the central value used; for a distribution, the P50 here and P10/P90 in `range`.
   - `source or assumption`: the `S-xxx` id, or one sentence of reasoning and the plausible range.
   - `status`: `assumed`, `sourced` or `calibrated` (only calibration sets `calibrated`); rows awaiting the maintainer's decision say so (for example `approval: pending CP<n>`).
   - `used in`: the YAML path and the module that reads it.

When a sourced value replaces an assumption, update the row (git keeps the history); a superseded row is kept and marked, not deleted. In a track worktree write the rows to `docs/assumptions-<track>.md` in the same format; integration merges them and deletes the fragment. Every run's `meta.json` and every report lists the assumption ids it depended on, with the label. There is no `common.assumptions check` CLI (the skill names one that was never built); the loaders above and the verifier's audit are the check.

## 6. How to add a licence row

Every dataset, model, tool, voice, font, music track and image needs a row in the licence and openness register (skill [`licence-register`](.claude/skills/licence-register/SKILL.md)). `docs/licences.csv` is canonical; the table in `docs/licences.md` is generated from it.

1. Read the licence text itself (not from memory) and append one row to `docs/licences.csv` with the columns
   `item, version, source_url, licence, open, commercial_use, attribution, obligations, used_in, status, approval`
   (`open` Y/N; `commercial_use` Y/N/unclear; `attribution` is the exact text to print, or `none`; `obligations` such as share-alike, non-commercial, notice file, or `none`; `approval` is empty for open items and must carry the maintainer's dated approval for any proprietary or paid item, which is not used until then).
2. Regenerate and check the Markdown table:
   ```bash
   uv run python -m common.licences sync     # rewrite docs/licences.md rows from the CSV
   uv run python -m common.licences check    # exit 1 if any Markdown row differs from the CSV
   ```
3. Refresh the release-compatibility table: `uv run python -m common.sources licences-release --write docs/licences-release.md`. Add the attribution to `NOTICE` when the item ships with the repository or its outputs, and regenerate the credits page (`uv run python -m common.licences credits --out docs/credits.md`, added in R9).

In a track worktree write `docs/licences-<track>.csv`/`.md`; integration merges them. Flag a licence conflict in the release note; never resolve it silently.

## 7. How a region sweep is re-run

The study covers all **13 regions**, with these slugs (skill [`region-sweep`](.claude/skills/region-sweep/SKILL.md)): `riyadh`, `makkah`, `madinah`, `eastern`, `qassim`, `asir`, `tabuk`, `hail`, `northern_borders`, `jazan`, `najran`, `al_baha`, `al_jouf`. Each region register lists every GASTAT governorate of the region (`governorates_gastat` must equal `governorates_listed`) and every settlement, screened or excluded with a reason. A sweep is a screening input, not a forecast.

1. **Prompts** (if the sweep is run by a region-scout agent): `make region-prompts` (= `./scripts/make_region_prompts.sh`) regenerates `prompts/REGION_<NAME>.md` from `prompts/REGION_TEMPLATE.md`; edit the template, never the generated files.
2. **Rebuild the register** with the region's own script under `screening/sweeps/<slug>/`. The file names differ by region (`build.py` or `build_register.py`, plus a document writer such as `doc.py`, `docs.py`, `report.py`, `render_doc.py`, `write_doc.py` or `write_docs.py`); the module docstring gives the exact command, for example:
   ```bash
   uv run python -m screening.sweeps.riyadh.build
   uv run python -m screening.sweeps.riyadh.doc
   ```
   Outputs: `cities/ksa/regions/<slug>.parquet` (governorate counts in the Parquet key-value header), its CSV mirror, and `docs/regions/<slug>.md`. Any new raw download goes under `data/ksa/<slug>/raw/` and into the manifest first (section 4); new parameters go into the assumptions register (section 5).
3. **Validate** the register against the `RegionRow` schema:
   ```bash
   uv run python -m screening.region_sweep validate cities/ksa/regions/<slug>.parquet --strict
   ```
4. **Geo-verify** unlocated or unsourced rows as the skill describes (`uv run --with rasterio python -m screening.geo_verify.cli estimate --which no-pop --region <slug> --seed 1`); estimates that fail the back-test gate stay in `notes`, never in `population`.
5. **Re-run the national chain afterwards.** A changed region register changes the merged register, the funnel and the coverage table, so these must be re-run in this order (each step is deterministic with `--seed`):
   ```bash
   ./screening/run_r2.sh 1          # merge the 13 registers, primary GASTAT match, control totals,
                                    # funnel and sensitivities, corridors, coverage table docs/coverage.md
   uv run python -m demand.register_update apply --seed 1 --out runs/r3/register_update/
   uv run python -m screening.commute_r4 roles --seed 1
   uv run python -m screening.commute_r4 minutes --seed 1
   uv run python -m screening.commute_r4 weights
   ./screening/run_r4.sh 1          # the funnel used by the study: runs/r4/funnel-<roles|minutes>/
   ```
   Caution: the corridor step inside `run_r2.sh` calls `screening.corridors generate` with its defaults (R2 scores, no routed alignments), which writes `cities/ksa/corridors/` and `scenarios/S2`–`S5`. The live corridor YAMLs are generated from `runs/r4/funnel-minutes/score/scores.parquet` with the routed alignments, so regenerate them afterwards with those inputs:
   ```bash
   uv run python -m screening.corridors generate --scores runs/r4/funnel-minutes/score/scores.parquet \
     --alignments cities/ksa/alignments --seed 1
   ```
   and review `git diff cities/ksa/corridors scenarios` before committing anything (or write to a temporary folder with `--out`, `--scenarios` and `--run-dir` and compare). The region annexes of the report are rebuilt from `docs/regions/` and `docs/coverage.md`.
6. Check that the coverage table still reconciles every GASTAT governorate (rule 2), then run `make test`.

These steps need the national data under `data/` (not in the repository); see `docs/data-sources.md` and `cities/ksa/sources.yaml` for where each file comes from.

## 8. Pull requests

- One topic per pull request, conventional commit messages, `make test` green (with `MANIFEST_FLAGS=--allow-missing` if you have no data).
- New figures carry a source id or an assumption id; new modelled outputs carry the label; new costs and benefits are P10/P50/P90 ranges.
- New dependencies, datasets, models, fonts or media carry a licence row in the same pull request.
- No files under `data/`, `runs/` or `movies/`, no imagery, no secrets, no absolute home paths.
- Good first issues are listed in [`docs/good-first-issues.md`](docs/good-first-issues.md).
