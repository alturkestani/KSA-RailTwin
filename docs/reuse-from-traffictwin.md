> **Document version:** docs/reuse-from-traffictwin.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: reviewed (read-only audit of `~/Documents/Projects/TrafficTwin` on 30 Oct 2026)

# Reuse audit: what KSA Rail Twin takes from TrafficTwin Jeddah

TrafficTwin (Apache-2.0, 198 commits, v0.1.0) is the parent project. It is **read-only** for this repository: we read it, copy files out of it, or symlink its large data; we never edit, commit to, or run destructive commands in it. Two lines per item, as the brief asks.

## Conventions
- **CLAUDE.md**: uv with pinned Python 3.12, ruff, pytest, a CLI per module, YAML for every behavioural constant, background runs with logs under `logs/`, worktree tracks, STATUS discipline. Reused as the base of our `CLAUDE.md`; SUMO specifics replaced by the national graph/skim stack and the three rail layers.
- **PROJECT.md**: brief structure (goals, non-goals, stack, data, layout, acceptance criteria per feature, milestones, open questions, first prompt). Our `PROJECT.md` is Tariq's v5 brief; its structure already follows this pattern.
- **prompts/_common.md, _resume.md**: the track contract (`M<n>: done` / `blocked - <reason>`), file ownership, worktree-only commits, 90-minute rule, handoff at every end. Copied nearly verbatim with `R<n>` labels, the manifest/docver checks and the integration-run merge exception.
- **orchestrate.sh, run_track.sh**: zsh, worktrees under `.worktrees/`, `claude -p ... --output-format stream-json`, 4 tries, 15-minute sleep on rate limits, status-line grep. Copied; added `--model` per track, a batch runner (at most 4 parallel), and cost logging from the JSON result.

## Agents and skills
- **Agents** (`data-scout`, `demand-modeler`, `sumo-engineer`, `viewer-engineer`, `strategist-engineer`, `imagery-analyst`, `verifier`; all `model: inherit`): short frontmatter plus 10–15 imperative lines. Our 21 agents follow the format with exact model ids; `verifier` → `red-team-verifier` with the extended audit list; `data-scout` → `rail-data-scout`.
- **Skills** (`assumptions-register`, `milestone-handoff`, `policy-yaml`, `sumo-run`, `osm-jeddah-network`, `lane-audit-imagery`): mechanical procedures with row formats and commands. `assumptions-register` and `milestone-handoff` copied with minimal changes (R labels, manifest and docver checks, red-team-verifier); `policy-yaml` became `scenario-yaml`; `osm-jeddah-network` inspired `osm-ksa-rail-network`.

## Methods
- **docs/loop-mode-choice.md**: binary car-vs-Loop logit with a 108-set coefficient sweep replacing a fixed shift share; ridership reported as a structured sensitivity, never a forecast. Generalised in `modechoice/` to a multinomial car/rail/air/bus logit with the same sweep-and-report discipline.
- **docs/population.md**: GASTAT 2022 control total spread over OSM districts by footprint/street/landuse weights; `default_rng(seed)` everywhere; hashed outputs keyed into run ids. Reused at governorate level (finer around metros) in `demand/`.
- **docs/data-sources.md**: source table (URL, publisher/version, licence, model mapping, commit?, status) with access dates and explicit "verified vs inference" notes; the GASTAT use policy already analysed. Format copied by the `source-citation` skill; GASTAT policy row reused in `docs/licences.md`.
- **docs/policies.md**: matched-control reporting (a placebo re-route control exposes routing gains), deltas over levels, teleport share as a quality flag. Reused as the matched-baseline rule for every scenario (S0 baseline, same zones/seed/parameters, sensitivity band).
- **docs/movies.md, docs/movies-arabic.md**: narration YAML → offline TTS (Kokoro-82M English; Chatterbox Multilingual with a CC-BY-4.0 ClArTTS reference voice for Arabic) → timing → -16 LUFS → mux with subtitles; Whisper read-back as the intelligibility check. Reused as the W10 pipeline pattern; the Arabic candidate list and test protocol are the starting point for the Saudi-dialect test (MSA ≠ dialect: new samples required).

## Data (symlinked, never copied)
- `data/osm/gcc-states-latest.osm.pbf` (243 MB, Geofabrik, replication 2026-10-14T20:21:12Z, ODbL) → `data/osm/` symlink and a manifest row. Saves a download and 243 MB of disk.
- `data/jeddah/jeddah.v2.net.xml` and the 10 % weekday baseline run (`runs/baseline-weekday-f0.1-s1-ae764558-...`) → used read-only by `coupling/` for the Jeddah decongestion test via TrafficTwin's own `sim.runner` matched-control runs.
- TrafficTwin's `data/` (9.0 GB), `runs/` (7.9 GB) and `movies/` (1.4 GB) are part of why the Mac has only ~17 GB free; nothing of it is duplicated here.

## Presentation
- **web/** (Vite + React + deck.gl + MapLibre, TypeScript strict, no API keys) and **api/** (FastAPI serving run outputs, bins, districts, decisions). Scaffold reused in R4/R8 for the national decision dashboard with the three-layer legend, scenario switcher, Pareto explorer and difference mode.

## Budget reference
- Jeddah: 27 Claude Code runs, about 41 agent-hours, about USD 420 list price (`Claude outputs/TrafficTwin-Riyadh-prompt.md`). This study has far more research; the estimate is in `docs/plan.md` and actuals go to `docs/cost-log.md` per run.
