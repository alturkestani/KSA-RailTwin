---
name: motion-maps
description: Rendering map animations and charts for the film and the report from run outputs only (deck.gl/kepler.gl captures, Manim or Remotion with its licence checked, Blender optional, ffmpeg), the style guide (open Arabic fonts, labels, three-layer legend, OSM credit, synthetic footer), the storyboard and shot-list format, and the disk gate. Use for W10 storyboards, renders and any animated figure.
---
> **Document version:** skills/motion-maps/SKILL.md v1.1 | 7 Nov 2026 | Author: coordinator (v1.1: R10 FIX_CP8_NOTES, Arabic footer aligned to glossary term 4) | Status: active

# Motion maps and charts

Every frame is drawn from `runs/` outputs or the registers; nothing is animated by hand and no figure is typed in. TrafficTwin's `scripts/movies/` (headless Chrome capture of the deck.gl viewer, spec YAML per film, ffmpeg assembly) is the pattern to copy out (read-only checkout).

## Storyboard and shot list (`film/storyboard/`)
`storyboard.md` (one row per shot: id, section 1–8, duration s, visual, data source run id or register, on-screen text EN/AR, narration line ids, transition) and `shots.yaml`:
```yaml
- id: sh-04-02
  section: 4
  type: map_animation            # map_animation | chart | title | archival | split_screen | talking_label
  run: runs/scenarios/S6-env2-ppp-s1/
  layer_legend: true             # existing / committed / hypothetical always visible
  camera: {from: [45.0, 24.7, 5.5], to: [41.0, 22.5, 6.5], seconds: 12}
  overlay: {label_en: "Hypothetical network, S6 envelope 2", label_ar: "شبكة افتراضية، السيناريو S6 الغلاف 2"}
  footer: synthetic                # mandatory on every modelled shot
  renderer: deckgl_capture         # deckgl_capture | manim | remotion | blender | ffmpeg_only
  output: film/renders/sh-04-02.mp4
```

## Renderers (open tools; each in the licence register before first use)
- **deck.gl / kepler.gl capture:** the dashboard in cinema mode (`web/?cinema=<shot>`), headless Chrome, 1920×1080 at 30 fps (4K only if the disk gate and time allow); the same code path TrafficTwin used.
- **Manim (Community, MIT)** for charts: tornado, Pareto fronts, cost ranges (P10/P50/P90 bands), ridership vs forecast; data read from `runs/` CSV/Parquet at render time.
- **Remotion:** check the current licence (company licence above a size threshold) and record it before using; otherwise prefer Manim.
- **Blender (GPL):** optional 3D flyovers; memory-heavy; only after the disk and memory check.
- **ffmpeg:** assembly, overlays, subtitles (`subtitles-srt`), loudness.

## Style guide
Fonts: Noto Naskh Arabic / Noto Sans Arabic for Arabic, Noto Sans or IBM Plex Sans for Latin (SIL OFL; register them). Arabic text shaped and RTL-correct (test with a rendered frame, not the source). Colours: colour-blind-safe palette; the three layers distinguishable by colour and dash (existing solid, committed dashed, hypothetical dotted) with a legend on every map. Labels bilingual where space allows. OSM credit "© OpenStreetMap contributors" on every map frame; data credits (GASTAT, SAR/HHR, Geofabrik) in the credits roll. Footer on every modelled shot: "synthetic demand, uncalibrated: scenario comparison, not a forecast" / «طلب تركيبي غير مُعايَر: مقارنة سيناريوهات، ليست توقعاً» (glossary term 4, `docs/glossary.ar.md`). No logos of SAR, PIF or any entity. Any AI-generated footage minimal and labelled on screen.

## Commands
`uv run python -m film.render shot sh-04-02 --fps 30 --res 1080p --seed 1` (one shot); `uv run python -m film.render all --cut ar|en`; `uv run python -m film.render check` verifies every shot's run exists, every frame set has the footer and legend flags, and fonts are registered.

## Disk gate and budget
Renders go to `film/renders/` (gitignored). Before rendering: `df -h ~`, estimate size (1080p30 ≈ 0.5–1 GB per 10 min intermediate), record it in the status file; stop if free disk would drop below 10 GB. 4K masters only if the Mac can do it after 1080p is done.
