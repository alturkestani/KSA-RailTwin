> **Document version:** docs/versioning.md v1.3 | 4 Nov 2026 | Author: coordinator; §5 by CP2_PREP; §5 summary-page note by FIX_R7 | Status: active

# Source versioning policy

Tariq's instruction (30 Oct 2026): source versioning is important, in all three senses. This page is the binding policy; `CLAUDE.md` summarises it and the `red-team-verifier` checks it at every milestone.

## 1. Code: git

- One repository, `main` is the integration branch. Each track works on its own branch in a worktree under `.worktrees/<track>` (`run_track.sh` creates them). Builders commit on their branch only; nobody pushes (rule 7). Tariq publishes.
- Conventional commits: `feat(<pkg>): ...`, `fix(...)`, `docs(...)`, `data(...)` (manifest rows), `chore(...)`, `film(...)`. Small and often; a run leaves several commits, not one.
- Integration runs (`INTEGRATE_*`, `PILOT_MERGE`, `R2`) are the only runs that `git merge --no-ff` track branches into `main`.
- After the verifier's PASS on a milestone, the coordinator creates an **annotated tag** on `main`: `r0`, `r1a`, `r1b`, `r1c`, `r1d`, `r1` (after integration), `r2`, ..., `r10`. The tag message names the verifier report (`docs/status/verify-<LABEL>.md`) and the cost-log total at that point.
- `CHANGELOG.md` gets one section per tag.
- Every run directory under `runs/` records `git describe --always --dirty` in `meta.json` (via `common.runmeta`), so any figure in a report can be traced to the exact code.

## 2. Data: the manifest `cities/ksa/sources.yaml`

Every dataset, extract, downloaded table, model weight file and media asset used by the pipeline is a row:

```yaml
- id: osm-gcc-2026-10-14            # stable id; a new edition gets a NEW row (osm-gcc-2026-12-01), never an overwrite
  name: OpenStreetMap GCC states extract
  publisher: Geofabrik GmbH / OpenStreetMap contributors
  url: https://download.geofabrik.de/asia/gcc-states-latest.osm.pbf
  edition: "2026-10-14T20:21:12Z"    # upstream version, replication timestamp, release, table date
  licence: ODbL-1.0
  accessed: 2026-10-15
  sha256: <64 hex>
  bytes: 255369412
  local_path: data/osm/gcc-states-latest.osm.pbf   # relative; may be a symlink target
  used_in: [network, screening]
  notes: inherited from TrafficTwin (read-only checkout)
```

- `uv run python -m common.manifest add ...` computes the hash; `verify` recomputes every hash and fails on mismatch; `hash` prints the manifest's own SHA-256, which every `meta.json` records as `data_hash`.
- `verify` is part of `make test` and of the `milestone-handoff`, so a silently changed input cannot pass a milestone.
- Derived tables we compute are not manifest rows; they live under `runs/` or `cities/ksa/` with their producing run id. Small licensed tables committed to the repo (`data/ksa/tables/`) are manifest rows **and** carry a `README.md` with the licence.
- A row's `licence` must match its row in `docs/licences.csv` (the licence register answers "may we use and redistribute it"; the manifest answers "which bytes did we use").

## 3. Documents: version headers

Every Markdown file under `docs/`, `prompts/`, `film/script/`, `.claude/agents/`, `.claude/skills/` begins with:

```
> **Document version:** <path or name> v<major.minor> | <date> | Author: <agent or person> | Status: draft | reviewed | verified
```

- Agent and skill files (`.claude/agents/*.md`, `.claude/skills/*/SKILL.md`) must start with the YAML frontmatter Claude Code requires; their version line is the first line after it. `common.docver` accepts exactly that placement (verifier observation O1, R0).
- Bump the minor on every substantive edit; bump the major when the structure changes. `uv run python -m common.docver check docs prompts .claude film/script` enforces the header; `bump <file>` increments it.
- `Status: verified` may be set only by the `red-team-verifier` (or Tariq).
- Film scripts additionally keep a `lines.csv` with one row per spoken line and its source id, so a changed figure is traceable to the line that spoke it.

## 4. Sources: citation records

Not a fourth layer but the glue: every number cites an `S-nnn` record (`docs/sources/index.csv`, skill `source-citation`) with URL, publisher, publication date and **access date**, so a source that later changes online can be re-fetched and compared. Secondary aggregators are marked `secondary` with the primary to find.

## 5. Track register fragments

Tracks write their rows to fragments (`docs/assumptions-<track>.md`, `docs/licences-<track>.{md,csv}`; `prompts/_common.md`). **Track fragments are deleted at integration**, in the same run that merges their rows into `docs/assumptions.md` and `docs/licences.{md,csv}`, after a scripted check finds every fragment row in the merged register (`scripts/check_fragments_merged.py` for the pilot and DATASCOUT fragments, CP2_PREP, 31 Oct 2026). Git history keeps the fragments; live references are repointed to the merged register. Per-track source CSVs under `docs/sources/` are not fragments: they are cited by name and stay.

The rule covers summary pages too: a per-track page that only lists ids already in `docs/assumptions.md` is deleted with the fragments. The last one, `docs/assumptions-r2.md` (0 table rows; its 18 named ids and 82 region rows all present in the register), was deleted by FIX_R7 item 3 (4 Nov 2026; verify-INTEGRATE_R7 O2).

The licence register has one canonical file: `docs/licences.csv`. The Markdown table in `docs/licences.md` is generated from it (`uv run python -m common.licences sync`; `check` exits 1 on any difference, and `tests/test_cp2_housekeeping.py` runs it).
