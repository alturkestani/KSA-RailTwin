---
name: licence-register
description: How to record and check every dataset, model, tool, voice, font, music track and image in the licence and openness register (docs/licences.md and docs/licences.csv), apply the open-source-first decision rule, flag proprietary items for Tariq's approval, and write the release-compatibility note. Use whenever adding a dependency, downloading data or a model, choosing a voice, font, track or image, or preparing a release.
---
> **Document version:** skills/licence-register/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Licence and openness register

PROJECT.md rule 12. The register is `docs/licences.md` (table) and `docs/licences.csv` (same rows, machine-readable); in a worktree write `docs/licences-<track>.md`/`.csv` and integration merges.

## Columns (exact, in this order)
`item, version, source_url, licence, open, commercial_use, attribution_required, obligations, used_in, approval, notes`

| column | allowed values |
|---|---|
| item | dataset / model / tool / voice / font / music / image name |
| version | release, tag, replication timestamp, model revision, edition |
| source_url | where it was obtained |
| licence | SPDX id where one exists (`Apache-2.0`, `MIT`, `ODbL-1.0`, `CC-BY-4.0`, `EPL-2.0`, `GPL-3.0-only`, `CPML`, `Llama-3.x-Community`, ...) or the terms' name |
| open | `Y` / `N` |
| commercial_use | `Y` / `N` / `unclear` |
| attribution_required | the exact attribution text to print, or `none` |
| obligations | share-alike, non-commercial, no-derivatives, watermark, notice file, redistribution limits, `none` |
| used_in | paths or workstream (W1 ... W10) |
| approval | empty for open items; `<date>, Tariq` for any proprietary or paid item (rule 12 requires approval before use) |
| notes | caveats, conflicts, where the licence text was read |

CLI: `uv run python -m common.licences add --item ... --version ... --url ... --licence ... --open Y --commercial Y --attribution "..." --obligations "..." --used-in ...`; `uv run python -m common.licences check` fails when a row is missing a field, when `open = N` has no `approval`, or when a dependency in `pyproject.toml`/`web/package.json` or a model/font/track under `film/` has no row.

## Open-source-first decision rule
1. Is there an open dataset / tool / open-weights model / open voice that does the job? Use it and register it.
2. If not, write why in `notes`, mark `open = N`, and stop: the item is not used until `approval` is filled by Tariq (ask at the next checkpoint or report it as a blocker).
3. Claude itself as orchestrator and coder is the stated exception; it is still a row (`tool`, `Anthropic terms`, `open = N`, `approval: brief v5`).

## Known traps (read the licence text; do not assert from memory)
- **ODbL (OpenStreetMap, Geofabrik extracts):** attribution "© OpenStreetMap contributors" on every map; derived databases are share-alike; a Produced Work (map image, film frame) needs the credit but is not share-alike.
- **GASTAT use policy:** reuse allowed incl. commercial with acknowledgement; modified material must be marked as modified and not presented as official statistics.
- **Coqui XTTS-v2:** CPML, non-commercial; may be tested, not used in any release that could be commercial.
- **Chatterbox (Resemble):** MIT in TrafficTwin's record, embeds an inaudible watermark; re-check the current revision.
- **Llama community licence, Jais, ALLaM, Qwen, Mistral:** each has its own terms (use restrictions, attribution lines, acceptable-use policy); record the exact licence name and the clause that matters.
- **Music:** CC-BY-NC or CC-BY-ND tracks are excluded if any commercial use is possible; CC-BY-SA tracks make the film share-alike; prefer CC-BY or CC0.
- **Remotion:** company licence for organisations above a size threshold; check the current terms before use.
- **Fonts:** Noto, IBM Plex, Amiri are SIL OFL 1.1 (attribution in credits; not for sale on their own).
- **Imagery and archival photos:** public domain or CC only, with the proof link in `film/rights_log.csv`; Wikimedia Commons pages name the licence per file.
- **Whisper:** MIT weights; faster-whisper / whisper.cpp are MIT; models from Hugging Face may carry different terms.

## Release-compatibility note (before CP7 and before any public or commercial release)
Write `docs/licences-compatibility.md`: list every obligation that attaches to the release (attribution lines to print, share-alike effects on derived databases, non-commercial items that must be removed, watermark disclosures), the items with `commercial_use = unclear` and the question to resolve for each, and any conflict between two items. Flag conflicts and do not resolve them silently; Tariq decides.
