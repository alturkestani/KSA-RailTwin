# KSA Rail Twin

[![CI](https://github.com/alturkestani/KSA-RailTwin/actions/workflows/ci.yml/badge.svg)](https://github.com/alturkestani/KSA-RailTwin/actions/workflows/ci.yml)

> **Disclaimer.** This is an independent, personal and non-partisan simulation study. **Every modelled output is synthetic demand, uncalibrated: scenario comparison, not a forecast.** It is not a government plan and not endorsed by any agency, operator or company. No survey was fielded (the survey is designed only). Results are written "in the model, X changes by", never "will". Every cost and benefit is a P10/P50/P90 range, never a single point.

> **Release status (1.0.0, 12 Nov 2026).** Code published; native Saudi review of the Arabic pending; films follow the review. Until the review, the Arabic texts (executive summary, film scripts and subtitles) are unreviewed drafts, and where they differ from the English, the English text and the registers govern. The documentary films are not published yet.

KSA Rail Twin is a national, investment-grade **economic feasibility study** of additions to the Saudi rail network. It asks which corridors to add, in what order, at what cost and with what long-term benefit; who funds and owns them; what they mean for people, culture and work; and what France, Japan, Spain, China and other countries actually did. **Simulation is the tool; the decision case is the product.** It extends the author's city-scale TrafficTwin Jeddah project to the whole Kingdom. This repository runs without TrafficTwin ([`docs/publish/traffictwin.md`](docs/publish/traffictwin.md)).

## Headline result

In the model, the committed programme (S1: the Landbridge and its Riyadh section, and the Saudi section of the GCC Railway, all announced/planned or under procurement) has an NPV of −337,555 / −60,103 / 11,607 SAR m (P10 / P50 / P90) against today's network. That is the medium population case, at 2025 prices, discounted over 60 years. After every region and governorate was screened and combinations of 71 searchable corridors were searched, the addition that holds up best is small. It is **three new stations on existing or committed lines** (S6-L2: Al Jubayl and Dhahran in 2030, Duruma in 2050), with capex of 801 / 1,423 / 5,286 SAR m. In the model it is the only top layout that stays positive with every cost at its P90 in every population case. Adding the Al-Kharj spur (S6-L1) gives the highest robust NPV, but it turns negative at P90 cost in two of three population cases. A wider-reach option (S6-L3) is negative at P90 cost in every case. None of these is a recommendation to build. Sources: [`docs/executive-summary.en.md`](docs/executive-summary.en.md) §§1–2; runs `runs/cba/CBA-S1-committed-programme` and `runs/r6/top5/top5.csv` (frozen appraisal model judge v3, seed 1, 10,000 draws).

## Try it

You need `git`, `make` and [uv](https://docs.astral.sh/uv/). uv installs Python 3.12 for you if it is missing: `uv python install 3.12`. No API key, no paid service, no model download and no data download is needed.

```bash
git clone https://github.com/alturkestani/KSA-RailTwin && cd KSA-RailTwin
make setup     # uv sync: the locked dependencies (needs network once, for the packages)
make test      # ruff, pytest on tiny fixtures, document headers, data manifest
make demo      # screening -> cost-benefit appraisal -> dashboard API, on invented fixture data
```

Measured in a fresh clone on a laptop (Apple M3 Pro) on 12 Nov 2026, with a clean environment (only `PATH` and an empty `HOME`; no `.env`, no `data/` or `runs/`, no TrafficTwin): `make setup` 28 s, `make test` 120 s, `make demo` 2 s (pytest: 920 passed, 154 skipped with reasons, 0 failed). The full log is in [`docs/publish/checklist.md`](docs/publish/checklist.md) §6.

**Expected output of `make demo`** (the values are invented fixture numbers; never cite them):

```text
Label: synthetic demand, uncalibrated: scenario comparison, not a forecast (fixture data; invented values)
screening: 5 settlements -> 4 long list -> 4 short list; 10 weight-sweep corners
cba: CBA-fixture-corridor, 100 draws, 60y NPV P10/P50/P90 = -386 / -47 / 234 SAR million (fixture)
dashboard API: 7 endpoints answered (7 carry a label); web app not built (make demo-serve builds it)
outputs: runs/demo ; timings {...}
```

Outputs go to `runs/demo/` (gitignored). The demo downloads nothing and makes no external call. The dashboard API binds to `127.0.0.1` only and is stopped at the end.

In a fresh clone some tests **skip, with a reason**, instead of failing. Most need the author's local run outputs (`runs/`) or data (`data/`), which are not in the repository. Others need headless Chrome (the Arabic right-to-left render probe) or the TrafficTwin checkout (the optional Jeddah coupling; TrafficTwin Jeddah is the author's optional private companion project (not public; not required to run, test or reproduce this repository)). The manifest check runs with `--allow-missing` when `data/osm` is absent. No test calls a paid API.

`make demo-serve` keeps the fixture dashboard running on http://127.0.0.1:8766. It also serves the web app when `web/node_modules` exists (`cd web && npm ci` once); the browser then loads the base map from OpenFreeMap.

## Read the study

| document | what |
|---|---|
| [`docs/report/feasibility-report.md`](docs/report/feasibility-report.md) | the feasibility report: methods, results with ranges, benchmarks and risks. Per-region annexes are in [`docs/report/annex-regions/`](docs/report/annex-regions/); sources and assumptions are in [`annex-sources.md`](docs/report/annex-sources.md) and [`annex-assumptions.md`](docs/report/annex-assumptions.md) |
| [`docs/policy-brief.md`](docs/policy-brief.md) | the policy brief |
| [`docs/executive-summary.en.md`](docs/executive-summary.en.md), [`docs/executive-summary.ar.md`](docs/executive-summary.ar.md) | executive summaries in English and Arabic, with the same figures checked digit by digit (`uv run python -m common.sources bilingual-check`). **A native Saudi review of the Arabic text is still pending**; where the two differ in meaning, the English text and the registers govern |
| [`docs/rj-routes-study.md`](docs/rj-routes-study.md), [`docs/extra-travel-study.md`](docs/extra-travel-study.md) | side studies kept **beside** the main report: a Riyadh–Jeddah routing study and an extra-travel sensitivity; neither is the recommended programme or part of the report's results |
| [`docs/film.md`](docs/film.md) | the documentary (Arabic and English cuts, trailers): scripts, storyboard and subtitles are in [`film/`](film/). Audio and video are not in the repository (see Credits) |
| [`PROJECT.md`](PROJECT.md) | the brief: the decision questions, workstreams W1–W10, milestones and checkpoints |
| [`docs/licences.md`](docs/licences.md), [`docs/licences-release.md`](docs/licences-release.md), [`docs/credits.md`](docs/credits.md) | the licence and openness register, its release-compatibility note and the generated credits |

## Reproduce the main figures

All report and deck figures come from one deterministic command, which reads the run outputs under `runs/`:

```bash
uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/
```

`runs/` (about 5 GB) is not in the repository. The 106 run-output files the figures are drawn from (21.6 MB) ship in [`docs/publish/figure-inputs/`](docs/publish/figure-inputs/README.md). [`docs/publish/reproduce.md`](docs/publish/reproduce.md) gives four levels. The first is the fixture pipeline (`make demo`). The second rebuilds every published figure byte for byte from the shipped figure inputs (copy them into `runs/`, then run the command above). The third is an exact rebuild of everything from the author's full run archive, to be deposited on Zenodo (DOI to follow). The fourth is a re-run of the recorded chain from public data (Geofabrik OSM, Copernicus DEM, WorldPop, UN WPP, the committed GASTAT tables), with run times; it gives approximate numbers, and the gaps are listed.

## Repository map

| path | what |
|---|---|
| `PROJECT.md`, `CLAUDE.md` | the brief and the working rules |
| `.claude/agents/`, `.claude/skills/` | the subagents and skills that built the study |
| `prompts/`, `orchestrate.sh`, `run_track.sh` | per-milestone prompts and the orchestration scripts (the audit trail) |
| `common/` | shared helpers: manifest, run metadata, labels, document versions, schemas, sources, licences, credits, figures, report, demo |
| `rail/`, `network/` | rail layers and the national network build (W1) |
| `screening/` | Kingdom-wide candidate screening and coverage (W2) |
| `costs/` | cost register and reference-class uplifts (W3) |
| `economics/` | cost-benefit appraisal (W4) |
| `funding/` | funding, ownership and delivery models (W6) |
| `demand/`, `modechoice/`, `access/`, `coupling/` | demand, mode choice, running times and isochrones, and the optional TrafficTwin Jeddah coupling (W8) |
| `optimise/`, `judge/` | network optimisation and phasing (W9). `judge/` holds frozen local copies of the appraisal model (gitignored except its README) |
| `study/` | side-study code (Riyadh–Jeddah routing, extra travel) |
| `api/`, `web/` | the decision dashboard (read-only FastAPI, plus Vite/React/deck.gl/MapLibre) |
| `film/` | the documentary: scripts, storyboard, subtitles and the build code |
| `scenarios/` | scenario YAML (S0 today, S1 committed, S2–S5 generated corridor families, S6 layouts) |
| `cities/ksa/` | registers; lines in three layers (`existing`, `committed/under procurement`, `hypothetical (ours)`); costs, population and assumptions; the data manifest `sources.yaml` |
| `docs/` | report, brief, summaries, research outputs, registers (assumptions, sources, licences, cost log), status and verifier reports; `docs/publish/` holds the release checklist |
| `tests/` | unit tests on tiny, clearly fictional fixtures |
| `data/`, `runs/`, `logs/` | gitignored, except published source tables under `data/ksa/tables/` with READMEs |

## How the study is versioned

Three layers are all required ([`docs/versioning.md`](docs/versioning.md)):

1. **Git.** Conventional commits; one annotated tag per milestone (`r0` … `r9`, `r10-final`) after the independent red-team verifier's PASS; [`CHANGELOG.md`](CHANGELOG.md). Every run's `meta.json` records the seed, config hash, data hash and code version.
2. **The data manifest** [`cities/ksa/sources.yaml`](cities/ksa/sources.yaml) has one row per dataset (publisher, URL, edition, licence, access date, SHA-256). Every figure in a document cites a source record in [`docs/sources/index.csv`](docs/sources/index.csv) or an assumption in [`docs/assumptions.md`](docs/assumptions.md).
3. **Document headers.** Every file under `docs/`, `prompts/`, `.claude/` and `film/script/` starts with a version line; `make test` enforces it.

The author's decisions at each checkpoint (CP1–CP9) are recorded with dates in [`docs/STATUS.md`](docs/STATUS.md). The milestone verifier reports are in `docs/status/verify-*.md`.

## Credits

- **Built with Claude.** The study was orchestrated and coded with Claude Code (Anthropic), the orchestrator and coding assistant approved under rule 12. Inside the pipeline, open tools and open-weights models run locally come first.
- **Voices.** The Arabic narration of the documentary uses Nabrah AI (Nabrah Studio public voices). **Any published audio carries a credit to Nabrah AI (Nabrah Studio voices)**, as the author approved on 7 Nov 2026; Nabrah's terms set no exact wording. The English narration and other voices are credited in [`docs/credits.md`](docs/credits.md). Audio and video files are not in this repository: they are published separately by the author.
- **Data.** Map and network data: (c) OpenStreetMap contributors, ODbL 1.0, via Geofabrik; derived databases (for example `cities/ksa/alignments/`) stay ODbL. Statistics: General Authority for Statistics (GASTAT), credited; derived tables are marked as derived and are not official statistics. Every dataset, model, tool, voice, font, track and image is in [`docs/licences.md`](docs/licences.md) and [`docs/credits.md`](docs/credits.md); open licence questions are listed in [`docs/licences-blockers.md`](docs/licences-blockers.md).
- **Parent project.** Conventions, the dashboard scaffold and the Jeddah coupling come from TrafficTwin Jeddah, the author's optional private companion project (not public; not required to run, test or reproduce this repository). Its code is Apache-2.0 and its derived Jeddah network is ODbL; the adapted files are attributed in [`NOTICE`](NOTICE), and nothing else from it is included (see [`docs/publish/traffictwin.md`](docs/publish/traffictwin.md)).

## Licence and citation

Repository: <https://github.com/alturkestani/KSA-RailTwin>. Code: Apache-2.0 ([`LICENSE`](LICENSE), [`NOTICE`](NOTICE)). Data keep their own licences (above and in the register). To cite the study, use [`CITATION.cff`](CITATION.cff).

## Contributing, conduct, security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) (setup, the non-negotiable rules, adding a source, an assumption or a licence row), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1) and [`SECURITY.md`](SECURITY.md). Open gaps are listed in [`docs/good-first-issues.md`](docs/good-first-issues.md).

**The author publishes; nothing here pushes.** No script, builder or agent in this repository pushes, publishes, posts, emails or contacts anyone.
