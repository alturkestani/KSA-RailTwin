# CLAUDE.md — KSA Rail Twin

> **Document version:** CLAUDE.md v1.4 | 30 Oct 2026 (Asia/Riyadh) | Author: coordinator ("Fable 5" = `claude-fable-5-1`) | Status: active

Read `PROJECT.md` first. It is the brief: the real goal (a national, investment-grade economic feasibility study of a Saudi rail network; simulation is the tool, the decision case is the product), the decision questions, the workstreams W1–W10, the agent topology, the repository layout, the milestones R0–R10 and the checkpoints. This file holds the working rules. The rules in the next section are copied **verbatim** from PROJECT.md section 2 and are non-negotiable.

This is a personal, open-source, non-partisan project of Tariq Alturkestani. It has nothing to do with the author's company: no content, branding, data or contacts from that company appear here.

## Non-negotiable rules (verbatim from PROJECT.md section 2)

1. **No fabricated numbers.** Every figure is sourced (URL, publisher, date, access date) or flagged as an assumption in `docs/assumptions.md` (value, range, reason, status) through the `assumptions-register` skill. "Unknown/unverified" is acceptable. A guess presented as fact is a verifier FAIL. This applies equally to costs, benchmarks, survey findings and quotes.
2. **No silent omissions.** Every region and every GASTAT governorate appears in the coverage table, either as screened (with the result) or as excluded (with the reason). Every benchmark country the brief names appears in the benchmark dossier, with its findings or "no reliable data found". A gap is a verifier FAIL.
3. Label every modelled output **"synthetic demand, uncalibrated: scenario comparison, not a forecast"** until calibration says otherwise. Write "in the model, X reduced by", never "will reduce". Cost and benefit figures are always ranges (P10/P50/P90), never single points.
4. Use only public, licence-compatible data (open-source first, rule 12): OSM (ODbL, credited on every map), GASTAT (credited; derived tables marked as derived), SAR/HHR published facts, open population grids (GHSL/WorldPop, checking the licence), and published reports and peer-reviewed literature (cited). No Google, TomTom or HERE traffic, nothing scraped against a site's terms, and no imagery crops committed.
5. Planned lines are **"announced/planned"** with a source and date, never "existing". Keep three layers apart: `existing`, `committed/under procurement`, `hypothetical (ours)`.
6. Every scenario is compared against a matched baseline on the same zones, seed and parameters, with a sensitivity band. Appraisal follows a named standard (section 6d) and states any departures.
7. No real-world action. Builders and the coordinator never `git push`, publish, post, email, contact any agency, company or person, or field a survey. Surveys are **designed only**; humans field them. Do not sign up for, pay for, or send data to any external service (for example a cloud TTS provider) without my approval. Ask first, and use free tiers or trials only once I agree. I publish.
8. Commit nothing under `data/`, `runs/`, `movies/` or imagery, except small licence-compatible tables with a README. No secrets, no absolute home paths.
9. Keep this project personal. It has no content, branding, data or contacts from the author's company. It stays independent and non-partisan: present options and evidence, and do not advocate for any entity.
10. Determinism: every run takes `--seed` and records seed, config hash, data hash and code version.
11. The **verifier** signs off every milestone: tests pass, the README command runs, acceptance criteria are met, every number traces to a source or a `runs/` output, coverage is complete, the assumptions register is complete, and the licence & openness register is complete. An open FAIL means the milestone is not done.
12. **Open-source first, as much as possible: data, models, software and voices.**
   - **Data:** use open and public sources first (section 2a). Proprietary or paid data is allowed only when no open alternative exists. In that case, flag it, explain why, and get my approval before use.
   - **Software:** use open-source tools (section 2a).
   - **AI models inside the pipeline** (extraction, OCR, translation drafts, embeddings, classification, local LLM tasks): prefer open-weights models run locally.
   - **Voices and audio:** open-source TTS run locally comes first. Commercial TTS and a human narrator are fallbacks only.
   - **The orchestrators are the exception.** Claude itself ("Fable 5" supervisor; Opus and "Hanko" coders) stays as my chosen orchestrator and coder.
   - Every dataset, model, tool, voice, font, music track and image goes into the **licence & openness register** (`docs/licences.md` plus `docs/licences.csv`) with these columns: item, version, source URL, licence, open (Y/N), commercial use allowed (Y/N/unclear), attribution required (text), share-alike or other obligations, and where it is used. Before any public or commercial release, check licence compatibility (for example ODbL share-alike on derived databases, non-commercial model licences, CC-BY-NC music). Flag conflicts and do not resolve them silently.
   - **Compute:** prefer local compute on my Mac (Apple M3 Pro, 18 GB RAM, no CUDA; use Metal/MPS or CPU builds). Heavy jobs (large fine-tunes, 4K renders, big LLMs) may later move to sovereign or cloud GPU **only with my approval** (rule 7).

## Machine and models
- Apple M3 Pro, 18 GB RAM, no CUDA (Metal/MPS or CPU builds only), macOS. Present: claude (Claude Code 2.1.x), uv 0.11, python3 (3.14 system), node 22, npm, brew, git, ffmpeg, caffeinate. Missing at R0: sumo, osrm, blender, manim (install only when a track needs them; record the path used in `docs/STATUS.md`). **Ollama was removed on 31 Oct 2026 (Tariq; D13 follow-up): no track assumes it. Local models run through MLX (`mlx-lm`, `mlx-whisper`) with `llama.cpp` as fallback; see the `local-models` skill for what is already cached.**
- **Disk**: about 17 GB free at R0; 52 GiB free on 31 Oct 2026 after the cache and Ollama clean-up (CP1 D13a and follow-up). Gates: R1a skims ≥ 15 GiB free, R3 ≥ 40 GiB, R10 renders and model downloads ≥ 50 GiB; geo caches ≤ 5 GB. Symlink TrafficTwin data; never copy it. Check `df -h ~` before any download over 500 MB and record the size in the status file.
- Python **3.12** pinned via uv (`uv python install 3.12 && uv venv --python 3.12`); `uv sync` installs; `uv run` runs. Never `pip install` into the system Python.
- **Model mapping (Tariq's labels → exact ids on this Claude plan, verified 30 Oct 2026):** "Fable 5" (supervisor/orchestrator, red-team-verifier) = `claude-fable-5-1`; Opus (coders, judgement) = `claude-opus-5-5` (the Claude Code default here; 1M context); "Hanko" (bulk, light tasks) = `claude-haiku-5-5`. Agent files name these ids in `model:`. Never cite model names in regulator- or public-facing documents; this mapping lives only here, in the agent files and in `docs/cost-log.md`.
- TrafficTwin (`~/Documents/Projects/TrafficTwin`, `~/Documents/Projects/TrafficTwin-publish`) is **read-only**: read, copy out, or symlink; never edit, commit to, or run destructive commands there.

## Model policy (Tariq, 31 Oct 2026; paid models and APIs)
Open/local models stay the default for bulk, low-stakes work. Paid state-of-the-art models and APIs are allowed where they **materially improve quality**, especially: Saudi-dialect Arabic script and narration (R10), Arabic–English translation of final deliverables (R8), and extraction or verification of hard Arabic sources. Ollama is not needed.

Rules (binding for every track):
1. **Before first use of any paid model or API**, write a one-paragraph request in `docs/STATUS.md` (what step, which model/vendor, why open isn't good enough, estimated USD, licence/terms for commercial and public release) and **stop that step until Tariq approves**. Other tracks continue.
2. Prefer **one A/B test** (open vs paid, the same 2-minute sample) and show Tariq both before committing.
3. **Log every paid call** in the cost log (`docs/cost-log.md`/`.csv`) with vendor and model; **alert Tariq at 80 %** of any approved amount.
4. **Never send personal data, credentials or unpublished partner material** to any API.
5. **Never store API keys in the repo**; ask Tariq to set them as environment variables (named in the request), read them from the environment only, and keep `.env*` gitignored.

Rule 12's open-source-first order still applies to everything else; this policy is the approved exception path. Claude (`claude-fable-5-1`, `claude-opus-5-5`, `claude-haiku-5-5`) as orchestrator and coder is already approved by the brief and needs no request.

## Engineering rules
- Python 3.12, type-hinted, `ruff` (lint + format), `pytest`; TypeScript strict in `web/`.
- Every module has a CLI (`uv run python -m screening.funnel ...`) and a test on the tiny fixtures in `tests/fixtures/` (1 corridor, 6 zones, 1 mini-region register, 1 cost register, 1 CBA case). Tests run in seconds; national-scale runs are never part of CI or pytest.
- Determinism (rule 10): every run takes `--seed` and writes `meta.json` with seed, config hash, data hash (from `cities/ksa/sources.yaml`), code version (`git describe --always --dirty`) and tool versions.
- Every behavioural, cost or appraisal constant lives in YAML with `source:` or `assumption:` and is registered via the `assumptions-register` skill (`docs/assumptions.md`). No magic numbers in code. Cost items go through the `cost-register` skill; licences through the `licence-register` skill.
- Handoff contract: every handoff is a file (YAML/Parquet/GeoJSON/Markdown plus a `docs/status/<track>.md` entry). Nobody passes numbers in chat.
- Keep layers separate: data build (`rail/`, `network/`), screening (`screening/`), costs (`costs/`), demand and mode choice (`demand/`, `modechoice/`, `access/`), appraisal (`economics/`, `funding/`), optimisation (`optimise/`), the TrafficTwin coupling (`coupling/`), presentation (`api/`, `web/`), film (`film/`). Shared helpers in `common/`.
- Three rail layers never mix: `existing`, `committed/under procurement`, `hypothetical (ours)`. Every line YAML carries `layer:` and `source:`; the viewer and every map legend show the layer.
- Labels: every modelled output says **"synthetic demand, uncalibrated: scenario comparison, not a forecast"**; write "in the model, X reduced by", never "will reduce"; every cost and benefit is a P10/P50/P90 range.
- No secrets, no absolute home paths in tracked files (`~` and `$HOME` only in shell scripts). `.env` gitignored. `data/`, `runs/`, `movies/`, `film/renders/`, `film/audio/` gitignored; small licence-compatible tables may be committed with a `README.md` stating the licence.
- Licence Apache-2.0 for code; `NOTICE` attributes OpenStreetMap (ODbL), GASTAT open data, and every other dataset or tool as it is added (mirror `docs/licences.md`).

## Source versioning (three layers; all required)
1. **Git.** Conventional commits (`feat(screening): ...`, `docs(benchmarks): ...`), small and often, on the track branch. One annotated tag per completed milestone (`r0`, `r1a`, `r1b`, ..., `r10`) created by the coordinator after the verifier's PASS. `CHANGELOG.md` gets a line per milestone. Builders never `git push`.
2. **Data manifest.** Every dataset, extract and downloaded table is a row in `cities/ksa/sources.yaml` (id, name, publisher, URL, edition/version, licence, accessed date, SHA-256, bytes, local path, used_in). `uv run python -m common.manifest verify` must pass before a milestone is done; a run's `meta.json` records the manifest hash. A changed upstream file gets a new row with a new edition, never an overwrite.
3. **Document headers.** Every file under `docs/`, `prompts/`, `film/script/` and every agent or skill file begins with a version line (for agent and skill files: the first line after the YAML frontmatter that Claude Code requires): `> **Document version:** <name> v<major.minor> | <date> | Author: <agent or person> | Status: draft / reviewed / verified`. Bump the minor on every substantive edit; the major when the structure changes.

## Workflow
- Parallel tracks run in git worktrees under `.worktrees/` on branches named after the track (`r1a`, `r1b`, ...); `prompts/_common.md` has the ownership and merge rules. Status per track in `docs/status/<track>.md`, ending each milestone with `R<n>: done` or `R<n>: blocked - <reason>`; the orchestrator greps for that line.
- Work milestone by milestone in the order of PROJECT.md section 9. Do not start the next milestone until the current one passes its acceptance criteria and the `red-team-verifier` writes PASS.
- Research tracks (benchmarks, costs, funding, social) are light and may run three or four at once; compute tracks are heavy and run alone. At most three or four Claude Code builders at once on this Mac.
- Before any run expected to take more than 90 minutes: record the estimate in the status file and produce a smaller-sample result first.
- Long commands go in the background with logs under `logs/`; poll the log, do not block more than two minutes.
- Keep `docs/STATUS.md` current (skill `milestone-handoff`). Decisions between checkpoints are recorded there with a date and the reason.
- Costs: after every Claude Code run, `uv run python -m common.cost_log add <jsonl>` appends a row to `docs/cost-log.md` (list-price USD from the JSON result; the plan is a subscription, so the figures are reference costs, not charges).
- When something cannot be verified, say so in the status file and the relevant register; never guess.
- Checkpoints (CP1–CP9, PROJECT.md section 10) stop the work and wake Tariq. Between checkpoints builders decide, record and continue. Only a checkpoint or a blocker wakes him.

## Subagents (`.claude/agents/`; frontmatter `name`, `description`, `tools`, `model`)
`rail-data-scout`, `region-scout` (parameterised by region; one prompt per region under `prompts/REGION_<name>.md`), `screening-analyst`, `gis-network-engineer`, `cost-estimator`, `economist`, `benchmarks-researcher`, `funding-ppp-analyst`, `socio-culture-analyst`, `demand-modeler`, `mode-choice-modeler`, `sim-engineer`, `optimizer`, `viz-engineer`, `report-writer`, `documentary-director`, `motion-graphics`, `voice-audio`, `subtitles`, `film-editor`, `red-team-verifier`. Their owners and models are in PROJECT.md section 7. The `red-team-verifier` reads only, runs on `claude-fable-5-1` (never the model that wrote the work), and writes PASS/FAIL with evidence; it does not fix.

## Skills (`.claude/skills/<name>/SKILL.md`)
`assumptions-register`, `milestone-handoff` (copied from TrafficTwin), `source-citation`, `licence-register`, `local-models`, `region-sweep`, `screening-funnel`, `corridor-generator`, `cost-register`, `reference-class-forecasting`, `cba-appraisal`, `ppp-structuring`, `benchmark-dossier`, `survey-design`, `pareto-optimizer`, `osm-ksa-rail-network`, `line-yaml`, `gravity-calibration`, `isochrone-commute`, `scenario-yaml`, `documentary-script`, `motion-maps`, `voiceover-tts`, `subtitles-srt`, `geo-verify` (standing method, 31 Oct 2026: imagery and geometry as a second line of evidence for locations and missing populations). Use them when their description matches the task; `source-citation`, `assumptions-register` and `licence-register` apply to every track.
