> **Document version:** docs/status/verify-FIX_HHR_JEDDAH.md v1.3 | 6 Nov 2026 | Author: red-team-verifier (claude-fable-5-1); pass 4 after the builder's corrected line citations (55ab059); passes 1–3 kept below | Status: verified

# VERIFY_FIX_HHR_JEDDAH — phantom HHR chord in Jeddah + station-siting rule

Scope verified: `prompts/FIX_HHR_JEDDAH.md` v1.0, the 7 commits 4b9eb7f..df4fa53 on top of 0cc369e (branch `main`, HEAD df4fa53), and the FIX_HHR_JEDDAH block of `docs/status/main.md` v1.18. Read-only; nothing fixed. Working tree before and after verification: `git status --porcelain` empty.

## Commands run (repo root)

| Command | Exit | Time | Result line |
|---|---|---|---|
| `make test` (ruff check, ruff format --check, pytest, docver, manifest) | 0 | 45 s | `All checks passed!`; `679 files already formatted`; **745 passed** (dot count 10 × 72 + 25; no F/E/s); `docver OK: 344 files`; `manifest OK: 387 rows` |
| `uv run pytest -q tests/test_fix_hhr_jeddah.py` | 0 | 4 s | 13 passed (`grep -c "^def test_"` = 13) |
| `uv run python -m common.report check` | 0 | 3 s | `report check: PASS` |
| `uv run python -m rail.hhr_check --before-rev 0cc369e --out /tmp/vchk.json` | 0 | 4.8 s | JSON identical (sorted-key diff) to the builder's `runs/fix-hhr/check.json` |
| `uv run python -m rail.station_inventory --out /tmp/inv.csv` | 0 | 0.9 s | `284 rows`; CSV row-for-row identical to `runs/fix-hhr/stations-inventory.csv` |
| `uv run python -m common.figures jeddah-hhr --geojson <hhr.geojson / git show 0cc369e:…> --out /tmp/v_{after,before}.png` | 0 | — | pixel-identical to the committed PNGs (PIL `ImageChops.difference` bbox = None); bytes differ in the PNG header only |
| own geometry script (`python3 -I`, haversine over vertices, OSM-way-segment lookup in `existing_osm.geojson`) | 0 | — | see criterion 1 |
| own corridor script over `cities/ksa/alignments/**/*.geojson` (79 files) | 0 | — | see criterion 3 |
| `git diff 0cc369e..HEAD --stat`, `git tag --contains 0cc369e`, mtimes, hygiene greps | 0 | — | see criteria 2 and 6 |

## Criteria

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1a | `hhr.geojson` = `existing.geojson` feature 0, MultiLineString main + branch | PASS | own script: `hhr==existing f0 geometry: True`; type `MultiLineString`, `parts ['main','branch']`, `part_to [null,'kaia']`, `part_km [448.54, 6.69]`; `existing.geojson` holds 10 LineString + 1 MultiLineString |
| 1b | Chord KAIA → Al-Sulaimaniyah gone | PASS | own script: no segment joins (39.1737763, 21.660417) and (39.2444797, 21.5192451) in either part; `hhr_check` `stitches.after = []`; before: index 376, 17.32 km |
| 1c | No duplicated stretch | PASS | repeated vertices main 0, branch 0; segments shared between parts 0 (before: 55 repeated, 266–320 = 377–431) |
| 1d | Branch is a stub from the junction | PASS | branch vertex 0 = (39.215395, 21.6234465), which is a vertex of the main part; last vertex = KAIA node; 57 vertices, 6.69 km, every vertex and segment is an OSM way segment of the "Haramain high-speed rail (Jeddah Airport branch line)" ways (`existing_osm.geojson`, 20 ways) |
| 1e | Main part = km-post span 448.54 km | PASS | main 989 vertices, 448.54 km = `hhr.yaml` last km-post 448.54 (Makkah 0.0 → Madinah 448.54); vs `length_km` 453: −0.98 % |
| 1f | Deviation: branch 6.69 km vs "≈3.75 km ±20 %" honest and justified | PASS | one OSM track from the junction to the KAIA node sums to ≈ 6.5–6.7 km in `existing_osm.geojson` (way lengths 1.70 + 2.52 + 0.14 + 0.37 + 0.87 + 0.87 plus the junction stub); the straight line junction → KAIA is 5.9 km, so 3.75 km cannot be a junction-to-terminal track length on this layout. Logged as C-fixhhr-001 (`docs/sources/conflicts.md`, open, +78 %), pinned by a test, not hidden |
| 1g | Deviation: "no vertex jump > 2 km" replaced by stitch test + OSM-way-segment test, honest and justified | PASS | own count: 402 segments > 2 km in `existing.geojson`; 0 of them fail the OSM-way-segment lookup; the literal criterion is impossible on OSM straight track, and the stitch test catches index 376 on the old file (`hhr_check` before) |
| 1h | `docs/network.md` §HHR geometry numbers vs `hhr_check` output | PASS | 1,100 / 989 + 57 vertices; 484.59 / 448.54 / 6.69 / 455.23 km; 17.32 km at 376 → 377; 55 repeats; reconciliation 448.54 + 12.04 + 6.69 + 17.32 = 484.59 and 78.29 + 18.73 + 17.32 + 370.25 = 484.59 (arithmetic checked); 36 segments > 2 km on main, longest 17.2 km at index 588 (`max_segment.index 588, 17.2`); offsets 3.317 → 3.399 / 3.432, p90 7.664 → 7.757 / 7.774, `osm_km_clipped` 483.331 → 454.070 / 447.391, v2 4.517 → 4.641 / 4.686, held-out 5.791 → 5.957 / 6.012, bridge 44.122 km (9.13 % → 9.72 %), tunnel 9.311 km (1.93 % → 2.05 %), A-align-070 7.446 + (3.399 − 3.317)/3 = 7.473 and 7.484 main-only: all match `/tmp/vchk.json` |
| 1i | Visual check logged, no imagery committed, no DEM sketch | PASS | `cities/ksa/sources.yaml` row `sentinel-2-l2a-cogs-hhr_kaia_branch`; `data/ksa/geo/s2/hhr_kaia_branch.png` gitignored (`.gitignore:5`); `runs/fix-hhr/s2_branch_*.png` under gitignored `runs/`; geometry vertices are 100 % OSM nodes |
| 2a | No station moved | PASS | `git diff 0cc369e..HEAD -- cities/ksa/lines/stations.geojson` = `generated: 2026-10-31 → 2026-11-06` only; `git diff --stat -- 'cities/ksa/lines/*.yaml'` empty |
| 2b | No corridor re-scored; R4_ALIGN, R5–R8 not re-run | PASS | `git diff --stat` empty for `cities/ksa/corridors`, `cities/ksa/alignments`, `scenarios`; newest files: `runs/cba` 3 Nov 16:54, `runs/r6` 4 Nov 00:18, `runs/r7` 4 Nov 16:48, `runs/align` 4 Nov 11:39, `cities/ksa/alignments` 3 Nov 17:58, `scenarios` 3 Nov 20:50 (all before 6 Nov); `network/align.py` diff = the 3-line `osm_line` guard only |
| 3a | Length-dependency table complete | **FAIL** | A reader of `cities/ksa/lines/geojson/*.geojson` is missing: `network/align.py:254 _rail_geoms` → `rail_mask` (l. 287) → `penalty_surface` (l. 346, `corr = on("highway") \| rail`, dilated by `corridor_km` 1.0 km) → `build_graph` (`1 − corridor_bonus`, 0.25 in v1 / 0.1 in v2) at both routing resolutions (l. 550, 607). `route_corridor` passes `exclude or []` (l. 797), so **every hypothetical corridor was routed with the stitched HHR geometry (chord and duplicated stretch) in its corridor-bonus mask**. `docs/alignments.md:32` itself lists "the existing rail lines (`cities/ksa/lines/geojson`, layer existing) → corridor bonus" as a routing input. Neither the §HHR geometry table nor the status block has this row |
| 3b | Verdict sentence accurate | **FAIL** | "Those figures could still change indirectly, but only if a re-tune with the corrected geometry picked different v1 weights" is not the only chain. Own script: 6 routed alignments have a vertex within 30 km of the chord (`S2-trunk_gap-riyadh-jeddah` 0.04 km, `S4-commuter_belt-jeddah-045` 0.13, `-315` 0.83, `-000` 1.19, `S2-trunk_gap-jeddah-yanbu` 1.92, `alternatives/S2-trunk_gap-jeddah-madinah` 2.34), and 4 of them have vertices inside the 1.5 km band of the chord while > 1.5 km from the true HHR: belt 315 six consecutive vertices (idx 5–10, 0.83–1.25 km from the chord, 1.5–3.5 km from the real track), belt 000 five (idx 7–11), Riyadh–Jeddah and belt 045 one each (a crossing at 0.04 / 0.13 km). Belts 000 and 315 are in `scenarios/S6-L5.yaml` and the CBA (`runs/cba/run_all.json`, `docs/cba.md`); Riyadh–Jeddah (893.484 km) and Jeddah–Yanbu are CBA cases. Whether re-routing with the fixed geometry moves these paths (the highway bonus overlaps there) is unknown without re-routing, which the brief forbids in this run; the dependency must be stated, not omitted |
| 3c | Every "no" in the table right (km-post users) | PASS | `access/running_time.py`, `access/railgraph.py`, `network/graph.py` have no `geojson`/`alignment_km` read (grep; `railgraph.py` hits are `stations.geojson` source strings and `runs/zones/points.geojson`); `hhr.yaml` byte-identical; KAIA km-post 97.02 unchanged |
| 3d | Other consumers | PASS | `network/distances.py:76`, `screening/corridors.py:203`, `optimise/report.py:51`, `web/src/components/MapView.tsx:36` and `common/figures.py` read MultiLineString; `api/data.py:159` serves `existing.geojson`; `network/align_diag.py:179` via `osm_line` (main part); all are in the table or named as maps-only, except 3a |
| 3e | `blocked` verdict right | PASS (direction) | Published R4_ALIGN HHR offsets, structure shares, A-align-070 objective, FIX_R7 v2 figures and `docs/alignments.md:271` were computed on the stitched geometry (recomputed above); per the brief the run must stop. The verdict is honest as far as it goes; its list is incomplete (3a/3b) |
| 4a | Before/after screenshots exist, ≤ 1 MB, OSM credit, layers legend | PASS | 123,491 and 110,316 bytes, 968 × 1138 RGBA; viewed: "© OpenStreetMap contributors (ODbL)", legend "rail layers (never mixed)" with existing / committed / historical and the stitched segment (before) or branch junction (after); before shows the 17.3 km chord, after shows main line + branch from the junction |
| 4b | Only fig01/fig12 changed; rebuild idempotent | PASS | `git diff --stat`: fig01/fig12 png+svg in `docs/report/figures` and `docs/deck-figures`, the two Jeddah PNGs; `figures-index.csv`, `dashboard-map.png` and the other 13 figures not in the diff. Jeddah maps re-rendered now: pixel-identical; PNG bytes differ at offset 68 (header metadata), so "idempotent" holds in-session (`test_jeddah_figure_is_idempotent`, `read_bytes()` equality) and pixel-wise across sessions |
| 5a | Siting rule in Tariq's wording | PASS | `docs/stations-siting.md` §1 quote matches brief item 2 phrase for phrase ("do not colocate main stations on airport land … It is better that they are not colocated … city station that serves the urban catchment … separate airport station on a short branch … An airport stop is an extra halt, not a substitute for the city station"); same wording in `.claude/skills/line-yaml/SKILL.md` (v1.1, one paragraph) and `rail/README.md` (v1.1); "no best-practice search" stated |
| 5b | A-station-001 status | PASS | `docs/assumptions.md` row A-station-001, status `proposed, pending Tariq`, precedent S-001/S-004 + OSM branch line; `docs/report/annex-assumptions.md` regenerated (755 rows, `proposed 1`) |
| 5c | Inventory counts match doc and status block | PASS | tool: 284 rows; existing city 112 / airport 1 / on-airport-land 3 / unplaced 3; committed unplaced 10; historical city 24; hypothetical city 131; 15 within 5 km of an airport point: identical in `docs/stations-siting.md` §2 and the status block; CSV identical to `runs/fix-hhr/stations-inventory.csv` |
| 5d | Landbridge Jeddah stated correctly | PASS | CSV row: `landbridge:jeddah … 21.55044, 39.17424, town_centroid:osm:node/1933393717 (Jeddah city), located False, JED 14.77, unplaced`; doc says the same; 8.21 km to Al-Sulaimaniyah and 12.24 km to KAIA recomputed |
| 5e | Proposal applies nothing | PASS | P1–P5 are options with the re-runs each would need; no file under `cities/`, `scenarios/` or `runs/` changed (2a/2b) |
| 6a | R9/R10, licences untouched | PASS | `git diff 0cc369e..HEAD --stat` has no `prompts/`, `film/`, `docs/licences*` |
| 6b | No paid API, no tag | PASS | no `openai/anthropic/elevenlabs/httpx/requests.post` in the new modules; `git describe` = `r8-26-gdf4fa53`, no new tag |
| 6c | No absolute home paths, secrets, `git push`, content from the author's company, model names in public-facing docs | PASS | greps over the changed tracked files: all empty (the "token" hits are survey "panel token" and RTL probe text in older status blocks; model ids appear only in `docs/status/` and the verifier header, as CLAUDE.md allows) |
| 7 | `make test` green, docver, manifest 387 rows, Sentinel-2 row SHA | PASS | see commands; `shasum -a 256 data/ksa/geo/s2/hhr_kaia_branch.png` = `353f906b…4170102`, 1,541,159 bytes = manifest row; `report check: PASS` |
| 8 | Every number in the new docs traces | PASS | all §HHR geometry and status-block figures reproduce from `rail.hhr_check` (identical JSON) or `rail.station_inventory` (identical CSV); the branch length conflict cites S-002; the visual check cites the manifest row |
| 12 | STATUS / status block | PASS with note | test count 745, docver 344, manifest 387 match; label line present (builder's intended `blocked` ending). Cost-log row: none yet for FIX_HHR_JEDDAH (`docs/cost-log.md` ends at FIX_R8_RTL); the block says `run_track.sh` appends it at run end, as for earlier runs |

## Failures (exact evidence)

**F1 — missing consumer in the length-dependency table (criterion 3a).** `network/align.py`:
- l. 254–266 `_rail_geoms`: `for p in sorted((Path(root_s) / LINES / "geojson").glob("*.geojson"))` … keeps every single-feature file with `layer == "existing"` except `riyadh-metro*` → includes `hhr.geojson`.
- l. 287–299 `rail_mask`: rasterises those geometries (`all_touched=True`) minus `exclude`.
- l. 346+ `penalty_surface`: `corr = on("highway") | rail`, `binary_dilation` by `corridor_km` (1.0 km, A-align-029).
- l. 396, 410 `build_graph`: edge cost × `(1 − corridor_bonus)` where both cells are in `corr` (0.25 v1; 0.1 v2).
- l. 550 and 607 `route_leg`: both resolutions call `rail_mask(g, exclude, root)`; l. 797 `route_corridor`: `exclude or []`.

So the stitched chord (17.32 km, no track) and the duplicated stretch were a 1 km-wide cost-bonus band in the cost surface of every routed corridor whose window covered west Jeddah. `docs/alignments.md:32` lists this input. Neither `docs/network.md` §HHR geometry nor the status block table has a row for it.

**F2 — the verdict sentence understates the chain (criterion 3b).** Status block and `docs/network.md`: "They could change only through a re-tune of the R4_ALIGN weights." Own measurement (`/tmp/vcorr.py`, 79 alignment files):

| routed alignment (`cities/ksa/alignments/`) | min vertex distance to the chord | vertices ≤ 1.5 km from the chord and > 1.5 km from the true HHR | downstream use |
|---|---|---|---|
| `S4-commuter_belt-jeddah-315.geojson` (84.509 km) | 0.83 km | 6 (idx 5–10) | S6-L5; CBA |
| `S4-commuter_belt-jeddah-000.geojson` (78.14 km) | 1.19 km | 5 (idx 7–11) | S6-L5; CBA |
| `S4-commuter_belt-jeddah-045.geojson` (66.276 km) | 0.13 km | 1 (idx 2) | — |
| `S2-trunk_gap-riyadh-jeddah.geojson` (893.484 km) | 0.04 km | 1 (idx 461) | CBA |
| `S2-trunk_gap-jeddah-yanbu.geojson` | 1.92 km | 0 | CBA |
| `alternatives/S2-trunk_gap-jeddah-madinah.geojson` | 2.34 km | 0 | — |

These routed lengths feed R4 running times and access, R5 costs and CBA, R6 layout L5 and R7/R8 figures without any re-tune. The effect size is unknown (a highway bonus overlaps the same cells, and the Jeddah endpoint is the town-centroid placeholder 5–8 km away); it stays unknown until the corridors are re-routed, which this run correctly did not do. The `blocked` line must list this chain.

## Judgement on the builder's intended ending

`FIX_HHR_JEDDAH: blocked - published figure depends on the stitched length: …` is the correct and honest outcome: the brief says to stop when a published figure depends on the stitched geometry, and the recomputed R4_ALIGN offsets, structure shares, tuning objective, FIX_R7 v2 figures and the `docs/alignments.md:271` sentence do. It is not a failure of the run. The list after the colon is incomplete (F1/F2): it must add the corridor-bonus mask path and the four to six routed corridors above, and the sentence "only through a re-tune" must be corrected.

## Deviations judged

- Branch 6.69 km vs "≈3.75 km ± 20 %": justified. OSM has no shorter junction-to-terminal track; recorded as C-fixhhr-001 and pinned by a test rather than forced to pass.
- "No vertex jump > 2 km" → stitch test + OSM-way-segment test: justified. 402 segments over 2 km exist on straight OSM track; all 402 verified here as consecutive nodes of one OSM way; the stitch test fails the old file and passes the new one.

## Spot-check

Procedure step 9 (10 % random rows of the candidate, cost and benchmark registers against their sources) does not apply: this run changed none of those registers. Instead every figure in `docs/network.md` §HHR geometry, `docs/stations-siting.md` and the status block was recomputed in full from `rail.hhr_check` (JSON identical) and `rail.station_inventory` (CSV identical), and the geometry was re-derived from `existing_osm.geojson` independently of the builder's code (own script). No misquoted figure found.

## Incident (noted, not a criterion)

The builder reports killing PID 2918, an unrelated `uvicorn api.main:app --port 8000` it had not started. Not verifiable after the fact; the status block records it with the restart command.

## Three most important fixes (documentation only; no re-run)

1. Add the missing row to the length-dependency table in `docs/network.md` §HHR geometry and the status block: `network/align.py` `_rail_geoms` / `rail_mask` / corridor bonus (A-align-029) read `cities/ksa/lines/geojson/*.geojson` (layer existing) when routing every hypothetical corridor; used (a) stitched, drawn; moves: unknown without re-routing; list the four alignments with vertices in the chord's 1 km band and the two more with windows over it, and their S6/CBA use.
2. Correct the verdict sentence in both places ("only through a re-tune" → also directly through the routed corridors above) and extend the `FIX_HHR_JEDDAH: blocked - …` list accordingly, so Tariq's decision covers re-routing the Jeddah corridors as well as the re-tune.
3. Add `docs/alignments.md:271` and this mask path to the list of items the eventual R4_ALIGN re-run must touch, and record the pending cost-log row and the open Al-Qurayyat visual check (P3) as follow-ups in `docs/STATUS.md`.

Pass 1 verdict: FAIL (superseded by Pass 2 below).

---

# Pass 2 (HEAD 72ee913; `git diff a17cc00..HEAD`)

Scope: the builder's docs-only response to F1/F2 (commits 19e141c, 72ee913: `docs/network.md` v0.7 §HHR geometry, the FIX_HHR_JEDDAH block of `docs/status/main.md`, and this report committed), plus a check that nothing else moved since pass 1. Read-only; nothing fixed. `git status --porcelain` empty before and after.

## Commands run (repo root)

| Command | Exit | Time | Result line |
|---|---|---|---|
| `make test` (log `logs/verify-fix-hhr-pass2-make-test.log`) | 0 | 41 s | `All checks passed!`; `680 files already formatted`; **745** dots on the pytest progress lines, 0 `F`/`E`/`s`; `docver OK: 345 files` (344 + this report); `manifest OK: 387 rows` |
| `git diff --stat a17cc00..HEAD` | 0 | — | 3 files: `docs/network.md`, `docs/status/main.md`, `docs/status/verify-FIX_HHR_JEDDAH.md`; nothing under code, `cities/`, `scenarios/`, `prompts/`, `film/`, `docs/licences*`, figures |
| `find runs cities scenarios data -newermt 2026-11-06T14:04:42+03:00 -type f` (pass-1 commit time; `runs/_superseded` excluded) | 0 | — | no file |
| `git grep -n -E 'lines/geojson\|"geojson"\|existing\.geojson\|hhr\.geojson\|existing_osm' -- '*.py' '*.ts' '*.tsx' '*.sh' Makefile ':!tests/'` and `git grep -n alignment_km -- ':!docs/' ':!prompts/' ':!film/'` | 0 | — | see 3a-2 |
| own script `/tmp/vcorr2.py` (`python3 -I`; vertex distance to the chord KAIA → Al-Sulaimaniyah and to the current `hhr.geojson` main + branch) over `cities/ksa/alignments/**` (79 files) and `cities/ksa/alignments-v2/**` (2 files) | 0 | — | see 3a-3 |
| own script `/tmp/vseg.py` (segment sampling every 50 m, band ≤ 1.1 km from the chord and > 1.1 km from the true HHR) | 0 | — | see 3a-4 |
| `grep -n -E 'jeddah' scenarios/S6-L5.yaml`; `grep -c "CBA-…" runs/cba/run_all.json docs/cba.md` | 0 | — | see 3a-5 |

## Criteria (pass 2)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1a–1i | Geometry (chord gone, branch stub, km-posts, numbers, visual check) | PASS (carried) | no file under `cities/ksa/lines/`, `rail/`, `network/` changed since pass 1 (`git diff --stat a17cc00..HEAD`) |
| 2a–2b | No station moved; no corridor re-scored; no re-run | PASS (carried) | same diff; no newer file under `runs/`, `cities/`, `scenarios/`, `data/` |
| 3a-1 | Length-dependency table has the corridor-bonus consumer | **PASS** | `docs/network.md:122` new row "**R4_ALIGN corridor bonus** (`network/align.py` `_rail_geoms` → `rail_mask` → `penalty_surface`, 1 km dilation, bonus 0.25 v1 / 0.1 v2; `docs/alignments.md` §2)"; `docs/status/main.md:703` same row in the status block |
| 3a-2 | No other reader of the existing-line geojson or of `alignment_km` is missing | **PASS** | code readers of `cities/ksa/lines/geojson/*`: `api/data.py:31,158` (dashboard, in table), `common/figures.py:60,624,1575,2366` (maps, in table), `network/align.py:258` (`_rail_geoms`, now in table) and `:1246` (`osm_line`, validation rows), `network/distances.py:39`, `optimise/report.py:78,85` (maps only), `rail/hhr_check.py`, `rail/lines.py`, `rail/osm.py` (writers), `screening/corridors.py:199` (S5 row). `alignment_km` outside docs: `network/align.py:1337,1359` (validation `compare`, in table), `rail/hhr_check.py:115`, `rail/lines.py:369` (writer), `web/src/types.ts:50` (in table). `network/align_v2.py:287` routes through `al.route_corridor`, so v2 used the same mask: covered by the row's "none in `cities/ksa/alignments-v2`" (3a-3). Nothing missing |
| 3a-3 | Row numbers: 6 / 5 / 1 / 1 vertices; none in alignments-v2 | **PASS** | own script: `S4-commuter_belt-jeddah-315` 6 (idx 5–10, min 0.83 km to the chord), `-000` 5 (idx 7–11, 1.19 km), `-045` 1 (idx 2, 0.13 km), `S2-trunk_gap-riyadh-jeddah` 1 (idx 461, 0.04 km); `S2-trunk_gap-jeddah-yanbu` 0 (1.92 km), `alternatives/S2-trunk_gap-jeddah-madinah` 0 (2.34 km); all 73 other files > 30 km away. `cities/ksa/alignments-v2/` holds only `S3-branch_spur-al-kharj` and `S4-commuter_belt-riyadh-225` (both > 30 km from the chord): "none" is right |
| 3a-4 | The four-corridor list is complete at segment level (pass-1 fix 1 asked for "two more with windows over it") | **PASS** | segment sampling: belt 315 54 sampled points inside the band, belt 045 44, Riyadh–Jeddah 44, belt 000 0 at the fine band (nearest 1.19 km) but inside the **coarse-pass** band: `coarse_arcsec` 15 (≈ 450 m, A-align-003), `cells = round(1000 / 450) = 2` (`network/align.py:371`) → 0.9 km dilation plus up to one rasterised cell ≈ 1.35 km, and the fine pass is confined to `fine_band_km` 3.0 around the coarse path. Jeddah–Yanbu (1.92 km) and the Jeddah–Madinah alternative (2.34 km) lie outside even the coarse band; removing a bonus only raises the cost of band cells, so a least-cost path that never enters the band is unchanged. The builder's four are the complete set; my pass-1 "two more" was over-inclusive and the builder was right not to add them |
| 3a-5 | S6-L5 has belts 000 and 315; the CBA cases exist | **PASS** | `scenarios/S6-L5.yaml:26–27,44,46` list `S4-commuter_belt-jeddah-000` and `-315`; `runs/cba/run_all.json` and `docs/cba.md` each contain `CBA-S4-commuter_belt-jeddah-000`, `CBA-S4-commuter_belt-jeddah-315`, `CBA-S2-trunk_gap-riyadh-jeddah` once; no CBA case for `-045`, as the row implies |
| 3a-6 | Row's parameter values and citations | PASS with note | `cities/ksa/assumptions/align_weights.yaml:52–53` `corridor_bonus` 0.25, `corridor_km` 1.0 (A-align-029); `align_weights_v2.yaml:312` `corridor_bonus: 0.1`; `docs/alignments.md:32` (§2, lines 21–36) lists the input. Note: the citation "`network/align.py` l. 252–290" covers `_rail_geoms` (254) and `rail_mask` (287) only; `penalty_surface` is at 346 and `build_graph` at 377. The function names identify the chain, so no FAIL |
| 3b | Verdict sentences accurate | **PASS** | `docs/network.md:131` and `docs/status/main.md:712–720`: both now name the corridor-bonus band, the four corridors, the direct chain (`_rail_geoms` → routed alignments → R4 → R5 CBA → R6 S6-L5 → R7/R8) and the indirect chain (offsets → A-align-070 → weights v1 → every corridor). "The existing lines' lengths, running times, skims and km-posts did not use the stitched length" is right (criterion 3c, carried). The old "only through a re-tune" sentence is gone from both files (`grep -n "only through a re-tune"` empty) |
| 3c–3d | km-post users; other consumers | PASS (carried) | unchanged code; 3a-2 re-grep |
| 3e | Intended `blocked` line accurate and complete | **PASS** with wording note | `FIX_HHR_JEDDAH: blocked - published figure depends on the stitched length: R4_ALIGN HHR validation offsets and structure shares, A-align-070 v1 tuning objective, FIX_R7 v2 figures, corridor-bonus routing of S4-commuter_belt-jeddah-000/-045/-315 and S2-trunk_gap-riyadh-jeddah (S6-L5, CBA cases), docs/alignments.md §7 item 2` lists every "yes" row of the table (offsets, structure shares, v1 objective, v2 figures, corridor bonus, §7 item 2 = `docs/alignments.md:271`). The FIX_R7 offset diagnosis ("probably; not recomputed") is covered by follow-up 1 ("v2 and the FIX_R7 diagnosis move too"). The S5 value 5.12 → 6.11 km is published nowhere outside the table itself (`git grep '5\.12' -- 'docs/*.md'`: only `docs/network.md:129`), so it is correctly left out. Wording: the corridor bonus depends on the stitched *geometry* (the chord's cells), not its length; the verdict paragraphs say "geometry", the label line says "length". Not a FAIL |
| 4a–4b, 5a–5e, 6a–6c, 7, 8 | Screenshots, siting rule, A-station-001, inventory, hygiene, checks, number tracing | PASS (carried) | no related file changed; `make test` green; greps over the three changed files for home paths, secrets, `git push`, the private-list terms and model names (outside `docs/status/`): empty |
| 12a | Status block numbers match | PASS | 745 tests, 13 in `tests/test_fix_hhr_jeddah.py`, docver 344 (at the builder's HEAD; 345 now with this report), manifest 387 |
| 12b | Label line | PASS with note (as in pass 1) | not yet in `docs/status/main.md` (`grep -n '^FIX_HHR_JEDDAH:'` empty); the builder's intended line is judged in 3e and is correct as written |
| 12c | Cost-log row | PASS with note (as in pass 1) | `docs/cost-log.md` still ends at `main-FIX_R8_RTL-try1`; follow-up 5 assigns the row to the coordinator (`common.cost_log add` from the run's JSONL) |
| 12d | Version header bumped on every substantive edit (CLAUDE.md "Source versioning", layer 3) | **FAIL** | `docs/status/main.md` header is `v1.18` at a17cc00, df4fa53, 19e141c **and** 72ee913 (`git show <rev>:docs/status/main.md \| head -1`). Commits 19e141c and 72ee913 added a table row, rewrote the verdict paragraph and added a "Follow-ups for Tariq" section: substantive edits with no bump, while `docs/network.md` was bumped v0.6 → v0.7 for the same change. Precedent: `verify-INTEGRATE_R4.md` A9 failed an un-bumped header; `verify-FIX_R8.md` criterion 9 checks bumps |

## Failures (exact evidence)

**F3 — `docs/status/main.md` edited twice without a version bump (12d).** `git log --format=%h -- docs/status/main.md`: 72ee913 ("FIX_HHR_JEDDAH follow-ups"), 19e141c ("corridor-bonus dependency"), both after a17cc00 which set v1.18; `head -1 docs/status/main.md` at HEAD still reads `docs/status/main.md v1.18 | 6 Nov 2026`. The diff (`git diff a17cc00..HEAD -- docs/status/main.md`) is +23/−6 lines: the new corridor-bonus row (l. 703), the changed R5–R8 row (l. 700), the rewritten verdict (l. 712–720) and the new Follow-ups section (l. 747–753). CLAUDE.md: "Bump the minor on every substantive edit." `docver check` passes because it checks the header's presence and format, not whether it moved.

F1 and F2 (pass 1) are closed by 3a-1 to 3a-5 and 3b.

## Spot-check

Nothing else changed since pass 1: `git diff --stat a17cc00..HEAD` lists only the three docs files; no untracked file under `runs/`, `cities/`, `scenarios/` or `data/` is newer than the pass-1 commit; `make test` is green with the same 745 tests. Every number in the new row (6/5/1/1, indices, bonus 0.25/0.1, 1 km, S6-L5 membership, the three CBA ids) was recomputed independently of the builder's code (own scripts over the geojson files, greps of `scenarios/S6-L5.yaml`, `runs/cba/run_all.json`, `docs/cba.md`, `align_weights*.yaml`).

## Three most important fixes

1. Bump `docs/status/main.md` to v1.19 (date 6 Nov 2026, author line "FIX_HHR_JEDDAH block (corridor-bonus row, verdict, follow-ups after the verifier)") and append the label line exactly as intended (3e). A wording improvement, optional: "depends on the stitched geometry" instead of "stitched length", since the corridor-bonus chain depends on the chord's cells, not its length.
2. In `docs/network.md:122`, cite `network/align.py` l. 254–290 (`_rail_geoms`, `rail_mask`), 346–375 (`penalty_surface`, dilation) and 377+ (`build_graph`, `1 − corridor_bonus`) rather than "l. 252–290", so the chain's three functions each have a line.
3. Coordinator: add the FIX_HHR_JEDDAH cost-log row (follow-up 5) and the open items 1–4 of the Follow-ups section to `docs/STATUS.md` open issues, so the re-route/re-tune decision is on the checkpoint list.

Pass 2 verdict: FAIL (superseded by Pass 3 below).

---

# Pass 3 (HEAD ab00700; `git diff 72ee913..HEAD`)

Scope: the builder's response to F3 (commit ab00700: `docs/status/main.md` header v1.18 → v1.19; `docs/network.md` v0.7 → v0.8 with line citations in the corridor-bonus row; the pass-2 report committed), plus a check that nothing else moved since pass 2. Read-only; nothing fixed. `git status --porcelain` empty before verification. Full pytest not re-run: the diff touches no code (`git diff --name-only 72ee913..HEAD | grep -v '^docs/'` is empty) and `network/align.py` was last changed at 4b9eb7f, before pass 1.

## Commands run (repo root)

| Command | Exit | Time | Result line |
|---|---|---|---|
| `git diff --stat 72ee913..HEAD` | 0 | — | 3 files, +61/−4: `docs/network.md` (header + one table cell), `docs/status/main.md` (header line only), `docs/status/verify-FIX_HHR_JEDDAH.md` (pass 2) |
| `uv run ruff check .`; `uv run ruff format --check .` | 0 / 0 | — | `All checks passed!`; `680 files already formatted` |
| `uv run python -m common.docver check docs prompts .claude film/script` | 0 | 0.3 s | `docver OK: 345 files` |
| `uv run python -m common.manifest verify` | 0 | 1.6 s | `manifest OK: 387 rows` |
| `grep -n -E "^def (_rail_geoms\|rail_mask\|penalty_surface\|build_graph)\b" network/align.py`; `grep -n "build_graph(" network/align.py`; `sed -n` around each cited line | 0 | — | see 13a–13c |
| `find runs cities scenarios data -newermt "2026-11-06 14:05:30 +0300" -type f` (pass-2 commit time; `runs/_superseded` pruned) | 0 | — | no file |
| greps over the three changed files for home paths; `git push` in tracked scripts | 1 (no match) | — | empty |

## Criteria (pass 3)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 12d (F3) | `docs/status/main.md` header bumped after its substantive edits | **PASS** | `git diff 72ee913..HEAD -- docs/status/main.md` = the header line only: `v1.18` → `v1.19 \| 6 Nov 2026 \| Author: … FIX_HHR_JEDDAH block (v1.18; v1.19 corridor-bonus row, verdicts, follow-ups after VERIFY_FIX_HHR_JEDDAH) …`. F3 closed |
| 13a | `docs/network.md:123` citations that land on the named definition | PASS (3 of 6) | `network/align.py:287 def rail_mask`, `:346 def penalty_surface`, `:377 def build_graph` match the cited 287 / 346 / 377 |
| 13b | `_rail_geoms` cited at l. 252 | **FAIL** | `network/align.py:252` is the comment `# --- … rail lines layer`; l. 253 `@functools.lru_cache(maxsize=1)`; l. 254 `def _rail_geoms(root_s: str) -> dict[str, Any]:`. The other three citations use the `def` line; this report's pass-1 F1 (l. 59) and pass-2 fix 2 (l. 156) both gave 254 |
| 13c | "`build_graph` l. 377 (called at both resolutions, l. 550, 607)" | **FAIL** | l. 550 `pen, corr = penalty_surface(gc, w, facc, rail_mask(gc, exclude, root))` and l. 607 `penf, corrf = penalty_surface(gf, w, fa, rail_mask(gf, exclude, root))` are the `rail_mask` → `penalty_surface` calls (as pass-1 F1, l. 63, states). `build_graph(` is called at l. 554 (`m, nid = build_graph(gc, mask, kl, w, pen, corr, conn)`) and l. 611 (`mf, nidf = build_graph(gf, bmask & ksa_mask(gf, root), kl, w, penf, corrf, conn)`). The two numbers are real lines of the chain, attached to the wrong function |
| 13d | `docs/network.md` header bumped for the edit | PASS | v0.7 → v0.8, author note "corridor-bonus row and line citations after the verifier" |
| 13e | Status-block copy of the row consistent with `docs/network.md` | PASS | `docs/status/main.md:703` names the function chain without line numbers (`grep -n -E 'align\.py[^|]*l\. ?[0-9]' docs/status/main.md` empty), so the two documents cannot disagree on line numbers; the row's figures (6/5/1/1, S6-L5, three CBA ids) are byte-unchanged since pass 2 (3a-3, 3a-5) |
| 1a–2b, 3a-1…3b, 3c–5e, 7, 8 | Pass-1 and pass-2 results | PASS (carried) | no file outside `docs/` in the diff; no file under `runs/`, `cities/`, `scenarios/`, `data/` newer than the pass-2 commit; `network/align.py` unchanged since 4b9eb7f, so the pass-1 readings of it stand; ruff, docver and manifest green; pytest not re-run (identical code to the pass-2 `make test`, 745 passed) |
| 6a–6c | R9/R10, licences, prompts, film untouched; no paid API, no tag; hygiene | PASS (carried) | `git diff --name-only 72ee913..HEAD` = the three docs files; greps empty; `git describe` still `r8-…`, no new tag |
| 12b | Label line | PASS with note (as in passes 1–2) | `grep -n '^FIX_HHR_JEDDAH:' docs/status/main.md` still empty; appended by the run wrapper at run end, wording judged in pass-2 3e |
| 12c | Cost-log row | PASS with note (as in passes 1–2) | `docs/cost-log.md` still ends at `main-FIX_R8_RTL-try1` (`grep -c FIX_HHR_JEDDAH` = 0); coordinator follow-up 5 |

## Failures (exact evidence)

**F4 — three of the six new line citations in `docs/network.md:123` do not point where they say (13b, 13c).** The cell reads: `` `network/align.py` `_rail_geoms` l. 252, `rail_mask` l. 287, `penalty_surface` l. 346, `build_graph` l. 377 (called at both resolutions, l. 550, 607) ``. Against `network/align.py` at HEAD (last changed 4b9eb7f; unchanged since pass 1):

| cited | the file at that line | right line |
|---|---|---|
| `_rail_geoms` l. 252 | l. 252 `# ---- … rail lines layer` (section comment); l. 253 `@functools.lru_cache(maxsize=1)` | **254** `def _rail_geoms(root_s: str) -> dict[str, Any]:` |
| `build_graph` "called at both resolutions, l. 550, 607" | l. 550 `pen, corr = penalty_surface(gc, w, facc, rail_mask(gc, exclude, root))`; l. 607 `penf, corrf = penalty_surface(gf, w, fa, rail_mask(gf, exclude, root))` | `build_graph(` is called at **554** and **611**; 550 / 607 are the `rail_mask` → `penalty_surface` calls |
| `rail_mask` 287, `penalty_surface` 346, `build_graph` 377 | the `def` lines | correct |

The citation is the evidence column of the length-dependency row that F1 added, and tightening it was pass-2 fix 2 (which gave 254–290 / 346–375 / 377+); it is the one change this pass was asked to verify. A reader following "l. 252" lands on a comment, and one following "l. 550" as a `build_graph` call finds `penalty_surface`. Pass-2 3a-6 let the loose range "l. 252–290" pass because the function names identified the chain; a specific line citation that is wrong is a misquote and does not get that allowance. No number of real-world meaning is affected and the fix is one cell, but the brief says not to soften a FAIL because the fix looks easy.

F3 (pass 2) is closed by 12d. F1/F2 (pass 1) stay closed.

## Spot-check

Nothing else changed since pass 2: `git diff --name-only 72ee913..HEAD` lists only the three docs files; `docs/status/main.md` changed in its header line alone; `docs/network.md` in its header and the one cell above; no newer file under `runs/`, `cities/`, `scenarios/`, `data/`. The six line numbers were checked one by one against `network/align.py` (`grep -n`, `sed -n`). Nothing else in the cell changed, so the pass-2 recomputation of its figures (6/5/1/1 vertices, bonus 0.25/0.1, 1 km, S6-L5 membership, three CBA ids) stands.

## Three most important fixes

1. `docs/network.md:123`: `_rail_geoms` l. **254**; and either "`penalty_surface(…, rail_mask(…))` called at both resolutions, l. 550, 607; `build_graph` l. 377, called l. 554, 611" or drop the call-site numbers. Bump `docs/network.md` to v0.9 with the edit.
2. Coordinator, unchanged from pass 2: append the `FIX_HHR_JEDDAH: blocked - …` label line (pass-2 3e wording) at run end and the cost-log row (follow-up 5).
3. Coordinator, unchanged: carry the Follow-ups items 1–4 and the re-route/re-tune decision to `docs/STATUS.md` open issues for the checkpoint.

Pass-3 verdict: FAIL (F4 open; closed in pass 4 below).

---

# Pass 4 (HEAD 55ab059; `git diff ab00700..HEAD`)

Scope: the builder's response to F4 (commit 55ab059: `docs/network.md` v0.8 → v0.9 with the eight line citations in the corridor-bonus row's evidence cell; the pass-3 report committed), plus a check that nothing else moved since pass 3. Read-only; nothing fixed. `git status --porcelain` empty before verification. Full pytest not re-run: the diff touches no code (`git diff --stat ab00700..HEAD` = the two docs files) and `network/align.py` is byte-identical to pass 3 (`git diff --quiet ab00700..HEAD -- network/align.py` exits 0; last changed 4b9eb7f, before pass 1).

## Commands run (repo root)

| Command | Exit | Time | Result line |
|---|---|---|---|
| `git diff --stat ab00700..HEAD` | 0 | — | `docs/network.md` (+2/−2: header and one cell), `docs/status/verify-FIX_HHR_JEDDAH.md` (+60/−1: pass 3); 2 files, +62/−3 |
| `grep -n "def _rail_geoms\|def rail_mask\|def penalty_surface\|def build_graph" network/align.py` | 0 | — | `254:def _rail_geoms`, `287:def rail_mask`, `346:def penalty_surface`, `377:def build_graph` |
| `grep -n "penalty_surface(\|build_graph(" network/align.py` | 0 | — | defs 346, 377; calls `550: pen, corr = penalty_surface(gc, w, facc, rail_mask(gc, exclude, root))`, `554: m, nid = build_graph(gc, …)`, `607: penf, corrf = penalty_surface(gf, w, fa, rail_mask(gf, exclude, root))`, `611: mf, nidf = build_graph(gf, …)` |
| `sed -n '252,254p;548,556p;605,613p' network/align.py` | 0 | — | l. 252 section comment, l. 253 `@functools.lru_cache(maxsize=1)`, l. 254 `def _rail_geoms`; the coarse (gc) and fine (gf) blocks as above |
| `uv run ruff check .`; `uv run ruff format --check .` | 0 / 0 | — | `All checks passed!`; `680 files already formatted` |
| `uv run python -m common.docver check docs prompts .claude film/script` | 0 | 0.2 s | `docver OK: 345 files` |
| `uv run python -m common.manifest verify` | 0 | 1.3 s | `manifest OK: 387 rows` |
| `find runs cities scenarios data -newermt "2026-11-06 14:12:16 +0300" -type f -not -path 'runs/_superseded/*'` (pass-3 commit time) | 0 | — | no file |
| `grep -n "/Users/[a-z]" docs/network.md docs/status/verify-FIX_HHR_JEDDAH.md`; `git ls-files \| grep -E '\.(sh\|py)$' \| xargs grep -l 'git push'` | 1 (no match) | — | empty; 0 files |
| `git describe --always --dirty`; `git describe --tags --abbrev=0` | 0 | — | `r8-30-g55ab059`; last tag `r8` (no new tag) |

## Criteria (pass 4)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 13b (F4) | `_rail_geoms` cited at its `def` line | **PASS** | cell: `_rail_geoms` l. 254; `network/align.py:254 def _rail_geoms(root_s: str) -> dict[str, Any]:` |
| 13a | `rail_mask`, `penalty_surface`, `build_graph` cited at their `def` lines | PASS | cell: 287 / 346 / 377; `network/align.py:287 def rail_mask`, `:346 def penalty_surface`, `:377 def build_graph` |
| 13c (F4) | call sites attached to the right function | **PASS** | cell: "`penalty_surface(…, rail_mask(…))` called at both resolutions, l. 550 and 607, `build_graph` called l. 554 and 611"; `network/align.py:550` and `:607` are the `penalty_surface(…, rail_mask(…))` calls (coarse `gc`, fine `gf`); `:554` and `:611` are the `build_graph(` calls. All eight numbers match; no other `build_graph(` or `penalty_surface(` call exists in the file (`grep -n` lists exactly the two defs and four calls) |
| 13d | `docs/network.md` header bumped for the edit | PASS | v0.8 → v0.9, author note "… line citations after the verifier, passes 1–3"; `git diff ab00700..HEAD -- docs/network.md` = header line + the one cell, nothing else |
| 13e | Status-block copy of the row consistent with `docs/network.md` | PASS (carried) | `docs/status/main.md` unchanged since ab00700 (not in the diff; header still v1.19); it carries no line numbers (pass-3 13e), so it cannot disagree; the row's figures (6/5/1/1, S6-L5, three CBA ids) are byte-unchanged in the cell (the diff changes only the evidence column) |
| 14 | Diff touches only the two docs files | PASS | `git diff --stat ab00700..HEAD` lists `docs/network.md` and `docs/status/verify-FIX_HHR_JEDDAH.md` only; `git log --oneline ab00700..HEAD` = one commit, 55ab059 |
| 15 | docver and manifest pass | PASS | `docver OK: 345 files` (exit 0); `manifest OK: 387 rows` (exit 0) |
| 1a–2b, 3a-1…3b, 3c–5e, 7, 8 | Pass-1 and pass-2 results | PASS (carried) | no file outside `docs/` in the diff; no file under `runs/`, `cities/`, `scenarios/`, `data/` newer than the pass-3 commit; `network/align.py` unchanged since 4b9eb7f, so the pass-1 readings stand; ruff, docver and manifest green; pytest not re-run (identical code to the pass-2 `make test`, 745 passed) |
| 6a–6c | R9/R10, licences, prompts, film untouched; no paid API, no tag; hygiene | PASS (carried) | diff = the two docs files; home-path and `git push` greps empty; `git describe` = `r8-30-g55ab059`, last tag `r8` |
| 12d (F3) | `docs/status/main.md` header bumped | PASS (carried) | v1.19 at HEAD, unchanged since ab00700 |
| 12b | Label line | PASS with note (as in passes 1–3) | `grep -n '^FIX_HHR_JEDDAH:' docs/status/main.md` still empty; appended by the run wrapper at run end, wording judged in pass-2 3e |
| 12c | Cost-log row | PASS with note (as in passes 1–3) | `docs/cost-log.md` still ends at `main-FIX_R8_RTL-try1` (`grep -c FIX_HHR_JEDDAH` = 0); coordinator follow-up 5 |

## Failures (exact evidence)

None open. F4 (pass 3) is closed by 13b and 13c: every one of the eight line numbers in the cell lands on the line it names. F3 (pass 2) stays closed by 12d; F1 and F2 (pass 1) stay closed.

## Spot-check

Nothing else changed since pass 3: `git diff --name-only ab00700..HEAD` lists the two docs files; `docs/network.md` changed in its header and the one evidence cell; no newer file under `runs/`, `cities/`, `scenarios/`, `data/`. The eight line numbers were checked one by one against `network/align.py` (`grep -n` for the four `def` lines and all `penalty_surface(` / `build_graph(` occurrences; `sed -n` around 252–254, 548–556 and 605–613). The non-evidence columns of the row are byte-identical to pass 2, so the pass-2 recomputation of its figures (6/5/1/1 vertices, bonus 0.25/0.1, 1 km dilation, S6-L5 membership, three CBA ids) stands.

## Three most important fixes

None required for this label. Carried forward for the coordinator, unchanged from passes 2 and 3:

1. Append the `FIX_HHR_JEDDAH: blocked - …` label line (pass-2 3e wording) to `docs/status/main.md` at run end, and add the cost-log row (follow-up 5); then re-check 12b and 12c.
2. Carry the Follow-ups items 1–4 and the re-route/re-tune decision (the corridor-bonus dependency: belts 000/315 in S6-L5 and three CBA cases routed against the old chord; effect size unknown until re-routed) to `docs/STATUS.md` open issues for the checkpoint.
3. No third fix.

VERDICT: PASS
