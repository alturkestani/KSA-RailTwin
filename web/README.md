> **Document version:** web/README.md v1.2 | 6 Nov 2026 | Author: viz-engineer (v1.0: R0 builder); R8_L6_PANEL (v1.2: S6-L6 in the Pareto explorer) | Status: draft

# `web/`: decision dashboard (R8)

Vite + React 19 + TypeScript strict + deck.gl 9.4 + MapLibre GL JS 5, after TrafficTwin Jeddah's viewer (Apache-2.0, see `NOTICE`). No API keys: the basemap is OpenFreeMap's keyless Positron style (OSM data; `?basemap=none` gives a plain background with the OSM region outlines). Open fonts only (Noto Sans, Noto Naskh Arabic; OFL-1.1, bundled). All data comes from `api/` (contract v1.0, `api/README.md`).

```bash
df -h ~                                   # disk gate before the first install (about 220 MB)
cd web && npm install                     # once
make dashboard                            # repo root: build + serve http://127.0.0.1:8765
# development: API on :8000 and the Vite dev server on :5173 (proxies /api)
uv run uvicorn api.main:app --port 8000 & (cd web && npm run dev)
```

| script | what |
|---|---|
| `npm run typecheck` | `tsc --noEmit` (strict, `noUncheckedIndexedAccess`) |
| `npm run build` | typecheck + bundle in `dist/` (gitignored) |
| `npm run screenshot [-- dashboard-map ...]` | headless capture of the views into `docs/report/figures/dashboard-*.png` (puppeteer-core + the installed Chrome or Chromium via `CHROME_PATH`; `RT_WEB_URL`, `RT_SHOT_DIR`, `RT_BASEMAP=none`). The `motion-graphics` track can reuse `SHOTS` |

## Views

- **National map**: the four layers in the legend, each with its own style (existing solid blue; committed/under procurement long-dash amber; hypothetical (ours) dotted violet with ring stations; historical sparse grey dots). A planned line is never drawn in the existing style (rule 5). The OSM credit is always visible (attribution control, not compact) and repeated in the legend.
- **Register & funnel**: filters by region, funnel stage and minimum population; the funnel from 1,224-row register to the five layouts (counts from the API); register points on the map coloured by stage.
- **Scenario and programme switcher**: S0–S5, S6-L2 (central case), S6-L1 (upside case, with the Al-Kharj spur P90 cost note wherever it appears), S6-L3 (reach alternative); population case selector. S6-L4, S6-L5 and S6-L6 are not in the switcher.
- **Cost/benefit ranges**: P10/P50/P90 bars (never a single point) for NPV, capex and BCR of the programmes against S1; S1 against S0; every corridor of a family against S1; net fiscal cost by delivery model; VfM low/central/high.
- **Pareto explorer**: robust NPV against reach (or capex) with the low/high population band per point; S6-L4 and S6-L5 appear only here, captioned "trade-off illustration only: no recommendation". S6-L6 also appears only here, captioned "comparison layout, not the recommended programme" (a connectivity comparison, not a search-front point); its robust NPV lies below the default y range, so it is drawn as a labelled marker at the bottom edge until "full y range" is ticked.
- **Difference mode**: the selected programme (or a family corridor) minus S1, with the added corridors highlighted on the map.

Every view has the footer with the synthetic-demand label, the alignment limitation (both from `/api/meta`, i.e. `common.labels`), judge v3 and seed 1. URL parameters: `view`, `scenario`, `pop`, `basemap=none`. `window.__rt.ready()` tells the capture script when data and map have settled.

Layout: `src/App.tsx` (shell, switcher, tabs), `src/api.ts` + `src/types.ts` (contract), `src/config.ts` (display styles), `src/components/` (MapView, RangeChart, Footer), `src/views/` (ScenarioPanel, RegisterView, RangesView, ParetoView, DifferenceView), `scripts/screenshot.mjs`.
