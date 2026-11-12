> **Document version:** docs/alignments.md v1.4 | 6 Nov 2026 | Author: R4_ALIGN builder (gis-network-engineer, cost-estimator, screening-analyst roles); FIX_R7 (§0, §4a–§4c, §8: offset diagnosis, alignment weights v2, CP7 sensitivity); FIX_HHR_REROUTE (§4, §4a, §4b, §4d HHR re-route, §7 item 2: corrected HHR geometry); S6_L6_CONNECTED (v1.4: §4d `compare` uses every part) | Status: draft

# Terrain-aware alignments for the candidate corridors (R4_ALIGN)

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Every alignment here is **hypothetical (ours)**, an indicative engineering sketch, not a design. Planned lines stay "announced/planned"; this document adds no existing or committed line. All tables with numbers are generated from the run outputs into `docs/alignments-tables.md` (`scripts/r4a_doc_tables.py`); this page quotes them with their run ids.

**Reproduce:** `./network/run_r4a.sh 1` (`DATA=1` also rebuilds the OSM layers and the tile cache). On the M3 Pro, routing all 67 corridors takes about 1.5 minutes with 3 workers, and the validation about 30 s.

## 0. Limitation (read first)

**Alignment-offset limitation:** alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

This sentence is `common.labels.ALIGNMENT_LIMITATION`; every report module that prints a routed alignment, or a cost or running time built on one, prints it beside the synthetic-demand label. It describes the frozen weights v1 (`align_weights.yaml`, hash `2b718ecb…`), which every R4–R7 figure uses. "30 m terrain" is the Copernicus GLO-30 source; routing runs on it averaged to 3″ (about 90 m, §2).

FIX_R7 (4 Nov 2026) diagnosed the offsets (§4a), tuned a parallel weights set v2 with leave-one-out validation (§4b), and re-ran the CP7 corridors and R7 figures under it as a sensitivity (§4c). **v2 is not adopted:** it lowers the in-sample offset, but on every held-out line it does worse than v1, and in-sample it breaks HHR's length target (§4b). Whether v2 is adopted is Tariq's decision at the review; until then v1 and the sentence above stand.

## 1. What changed

Before R4_ALIGN, every S2–S4 candidate was a great-circle chain through its stations (A-corr-012). R4 costed it at the straight-line km and ran trains over 1.2 × that distance, with terrain from the nearest register town (A-corr-013) and placeholder tunnel/viaduct shares (A-corr-014). Each corridor is now routed over the terrain. Its km-posts are chainage along the routed line, its tunnel, viaduct and earthworks km and its terrain classes are measured, and curves tighter than the design-speed radius become speed restrictions in the running-time model. The 9 S5 station additions sit on existing or committed track and are not routed.

## 2. Data (manifest rows and licence register: `docs/licences.md`)

| layer | source | use |
|---|---|---|
| terrain | Copernicus DEM GLO-30 Public, averaged to 3″ (about 90 m), 241 tiles (`cop-dem-glo30-align-3as-2026-11-01`) | slope cost, smoothed grade, vertical profile, relief, hillshade |
| built-up, water, mangrove | ESA WorldCover 10 m 2021 v200, mode-resampled to 3″, CC BY 4.0 (`esa-worldcover-v200-align-3as-2026-11-01`, S-r4a-002) | urban penalty (with OSM), water = bridge |
| urban cores | OSM landuse residential, commercial, retail, industrial | urban penalty |
| protected areas | OSM boundary=protected_area / national_park, leisure=nature_reserve. **WDPA is not used:** its terms forbid commercial use and redistribution within derivative works (S-r4a-001), so the open OSM layer is the fallback | protected penalty |
| restricted zones | OSM landuse=military / military=* only. No other openly published restricted-zone data was found: "not available" in the licence register | military penalty |
| dunes and sabkha | OSM natural=sand/dune (the large sand seas are mapped) and natural=wetland with wetland=sabkha/saltmarsh/tidalflat/mud (or untyped). The USGS Arabian geology map was checked and rejected: it is attributed by age only (S-r4a-003). WorldCover has no sand or sabkha class | sand and sabkha penalties; along-line terrain class |
| wadis | OSM waterway=river/stream/wadi/canal/drain/ditch plus a D8 flow accumulation on the coarse DEM window (≥ 50 km², A-align-030) | wadi penalty per km inside a channel: crossing is short and cheap, running along is long and costly |
| existing corridors | OSM highway=motorway/trunk/primary (+ links) and the existing rail lines (`cities/ksa/lines/geojson`, layer existing) | corridor bonus |
| coastline | OSM natural=coastline (R3 row) | coastal class |

All are open: ODbL (OSM), CC BY 4.0 (WorldCover) and the free Copernicus DEM licence. The OSM layers are extracted by `network/align_osm.sh` and rasterised to bit-flag tiles by `network.align_data flags`. **Release flag for Tariq:** the committed sidecars (`cities/ksa/alignments/`) are produced from an OSM-derived cost surface. Whether they are an ODbL Produced Work or a Derivative Database is a release question, recorded rather than resolved silently.

## 3. Method (`network/align.py`; parameters `cities/ksa/assumptions/align_weights.yaml`, `docs/assumptions.md`)

1. **Cost surface per leg** (consecutive stations), inside an ellipse with the stations as foci: e = 1.35, widened to 1.7 and then 2.2 while the path reaches 97 % of the edge (A-align-005). A 16-connected edge of length L with grade g on the 500 m-smoothed DEM costs:
   - at grade (g ≤ cap): L × (1 + 3 (g/cap)²);
   - above the cap: L × structure factor × (g/cap). This is a **hard mask on at-grade running**: the only way through is a tunnel or viaduct. The structure factor is (tunnel + viaduct central) / 2 over the at-grade base central, from the cost register normalised to 2025 SAR exactly as `costs.estimate` prices them: **5.33 for HSR and 10.18 for conventional, mixed and commuter lines** (A-align-021). The first version divided raw register values in different currencies (GBP 2011 structures over an EUR 2016 base), which gave 4.0 and 7.6. The cost-estimator review caught it; the weights were re-tuned and every corridor re-routed.
   - Both are multiplied by (1 + area penalties: urban 1.5, protected 0.3, military 6, sand 0.1, sabkha 0.2, wadi 0.6, inland water 10). Open sea with no GLO-30 tile is impassable, and so is everything outside the OSM Saudi Arabia boundary (A-align-090). Water inside the tile set (WorldCover water and mangrove, OSM natural=water, sea pixels of coastal tiles) costs the water penalty and is bridged. That rule was added after the first full routing sent Jazan–Najran 235 km through Yemen.
   - They are multiplied by 0.75 where both cells lie within 1 km of a highway or an existing line.
2. **Caps by line class** (prompts/R4_ALIGN.md item 1): HSR 2.5 %, mixed passenger/freight 1.25 %. Passenger-only conventional and commuter lines take 2.5 % (A-align-011; a spur that later carries freight would need 1.25 %).
3. **Two passes:** Dijkstra (scipy csgraph) on a 15″ grid over the whole window, then at 3″ inside a 3 km band around it, in 60 km pieces.
4. **Curvature:** the path is resampled every 50 m and Gaussian-smoothed with the smallest sigma (0–4 km) that gives every point R ≥ R_min, without moving more than 1.5 km from the least-cost path.
   - R_min = 11.8 v² / (E + I), with E + I fixed by Tariq's anchor (300 km/h → 7,000 m). That gives HSR 7,000 m, mixed (250 km/h) 4,861 m, conventional (200) 3,111 m and commuter (160) 1,991 m (A-align-012).
   - Tighter curves remain as speed restrictions v = √(R (E + I) / 11.8), rounded down to 10 km/h. They feed the running-time model through `alignment_routed.speed_restrictions`.
5. **Vertical profile:** a linear programme (HiGHS) fits a formation level with |grade| ≤ cap, minimising the L1 distance to the ground plus 5 × any excess beyond 15 m of fill or 25 m of cut.
   - Formation more than 15 m above ground = viaduct; more than 25 m below = tunnel; else earthworks (cut/fill volumes, A-align-045) or at grade. Water crossings are viaduct.
   - Stations are held at ground level unless the cap makes that impossible over the leg (`ends_relaxed`).
   - The cap is re-checked on the stored profile (`formation_cap_ok`, 5e-5 rounding tolerance).
   - A leg whose station ground levels differ by more than cap × routed length cannot meet the cap with any structure. The corridor is then flagged `profile_feasible: false`, with the leg and the minimum length at the cap in `infeasible_legs`, and it is **not costed** (A-align-091). One corridor is affected (§5).
6. **Terrain class** per 100 m (A-align-060), ordered as in R3: escarpment_mountain (relief ≥ 120 m in a 2 km box), sabkha, coastal (≤ 10 km), dunes, mixed (≥ 40 m), flat desert. These replace the proxy shares in the cost register's terrain split.
7. **Outputs per corridor** (`runs/align/corridors-s1/<id>/`):
   - `alignment.geojson` (routed line plus the straight sketch);
   - `profile.parquet` (every 100 m: ground, formation, structure, radius, max speed, terrain class, flags);
   - `summary.json` (length, detour ratio, tunnel/viaduct/earthworks km, cut/fill m³, max grade, speed restrictions, wadi crossings, km in urban/protected/military/sand/sabkha);
   - `meta.json` (seed, weights hash, tile index hash, code version).

   The sidecars `cities/ksa/alignments/<id>.{json,geojson}` (tracked) feed the corridor generator.

## 4. Validation on the three operating lines, then freeze

The same algorithm routed HHR (HSR class), SAR North passenger and SAR East passenger (mixed class) between their own stations. The line itself and its twin (SAR North freight, the SAR East legacy freight line) were excluded from the corridor bonus. Targets: length within ±5 % and mean offset < 2 km. The table is `docs/alignments-tables.md` §1 (run `runs/align/validation-s1`).

- **Length: target met on all three lines.**
- **Mean offset: target not met on any line** (HHR about 3.3 km on the stitched geometry, 3.399 km on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE), §4d; SAR North and SAR East about 9–10 km).

The routes follow the right macro corridors (maps `runs/align/maps/validation-*.png`). The offsets come from 10–50 km lateral choices across flat plateau and sand, where the cost surface is nearly indifferent and the real lines followed reasons outside it:

- SAR East's 1950s route via Al-Kharj and Haradh;
- the HHR approaches to Makkah and its inland swing north of KAEC;
- SAR North's line across the Qassim–Hail plain.

**Structures:** the model under-counts viaducts. On HHR, OSM tags about 44 km of bridge, while the model finds about 7 km, because the profile only calls a viaduct for fills above 15 m or water. Real lines also bridge wadis and urban sections. Tunnel km is of the right order on HHR. Measured viaduct km is therefore a **lower bound**.

**Tuning** (`docs/alignments-tables.md` §2; `runs/align/tune-s1`): coordinate descent, pass 1 with 2 sweeps over 6 parameters and pass 2 with one sweep over wadi, sabkha and corridor distance. It ends at an objective of 7.446 km (on the stitched HHR geometry; at the same frozen weights the objective would read about 7.473 km on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE), §4d; the weights stay frozen and were not re-tuned). Structure exponent 0 (no grade scaling over the cap) scores 8.11 km, exponent 1 scores 7.446 km. Protected areas are a policy weight (0.3, A-align-023), not tuned. An earlier search scored 0 as 0.004 km better, which is noise, and the King Salman Royal Reserve post-dates SAR North. The superseded search with the un-normalised structure factor is kept in `runs/align/superseded/`; it chose the same values.

**Frozen:** `align_weights.yaml` (`frozen: true`), hash `2b718ecbe6caead86e8424e621f90420815a6ada10ad6c4e1b7ffa00bca792d4` (`align_weights.sha256`), recorded in every corridor's `meta.json`. The adaptive window (A-align-005) and the Kingdom mask (A-align-090) were in place for the final tuning. `network.align reproduce --n 10 --seed 1` re-routes 10 random corridors from the frozen weights and byte-compares `alignment.geojson`, `summary.json` and `profile.parquet`: 10/10 identical (`runs/verify-r4a/reproduce/reproduce.csv`).

### 4a. Why the routed lines drift (diagnosis, FIX_R7)

`uv run python -m network.align_diag diagnose` (run `runs/align/diag-v1-s1`, on `runs/align/validation-s1`, weights v1) splits each line's mean offset **exactly** into station-to-station legs and causes. The metric is the symmetric one of §4: half the mean distance from 2,000 routed samples to the real (OSM) line, plus half the reverse. Each sample's share is offset ÷ 4,000 km, so the shares add up to the reported mean offset.

Each sample takes one cause, in order:
1. offset ≤ 1 km: within DEM resolution, smoothing and OSM digitisation (A-align-110);
2. within 25 km of a station whose 3 km neighbourhood is ≥ 15 % urban or built-up: urban approach (A-align-111);
3. otherwise, its leg's cause.

A leg's cause comes from costing **both** geometries on the router's own surface, sampled every 90 m with the same edge cost (length × grade term or structure factor × (1 + area penalties) × corridor factor):
- if the real leg costs ≤ 2 % more, the surface is indifferent: lateral freedom, flat or on relief (A-align-112, A-align-113);
- otherwise, the largest positive component of the cost difference names the cause: the grade term, an area penalty, or the length and corridor terms (a corridor the surface cannot see).

The 90 m sampling is a diagnostic, not the router's 16-connected Dijkstra cost, so the ratios are approximate.

Per leg (cost in km-equivalents of flat, unpenalised line; "near a highway" = share of samples within about 2 km of an OSM motorway/trunk/primary):

<!-- gen:4a-legs -->
| line | leg | real km | routed km | leg mean offset km | surface cost real / routed | near a highway, real / routed | median relief m | leg cause | km of the line's mean offset, by cause |
|---|---|---|---|---|---|---|---|---|---|
| hhr | makkah → jeddah | 78.0 | 62.3 | 6.43 | 1.249 | 61% / 99% | 77 | unseen_corridor | within 1 km 0.01; urban station approach 0.85; corridor the surface cannot see 0.14 |
| hhr | jeddah → kaia | 18.9 | 18.1 | 0.38 | 1.271 | 100% / 100% | 26 | avoids_urban | within 1 km 0.01 |
| hhr | kaia → kaec | 119.6 | 86.0 | 3.01 | 1.963 | 61% / 97% | 8 | avoids_urban | within 1 km 0.01; urban station approach 0.24; urban penalty 0.41 |
| hhr | kaec → madinah | 266.8 | 259.9 | 2.82 | 1.102 | 16% / 28% | 39 | avoids_urban | within 1 km 0.11; urban station approach 0.12; urban penalty 1.41 |
| sar-north-passenger | riyadh-north → majmaah | 190.2 | 182.4 | 6.25 | 1.494 | 10% / 89% | 14 | unseen_corridor | urban station approach 0.20; corridor the surface cannot see 0.73 |
| sar-north-passenger | majmaah → al-qassim | 162.6 | 163.2 | 2.78 | 0.988 | 17% / 37% | 20 | lateral_freedom_flat | within 1 km 0.02; urban station approach 0.01; flat-terrain lateral freedom 0.33 |
| sar-north-passenger | al-qassim → hail | 269.8 | 289.3 | 19.93 | 1.565 | 53% / 84% | 9 | grade_choice | within 1 km 0.01; grade term 4.44 |
| sar-north-passenger | hail → al-jawf | 301.6 | 301.7 | 0.84 | 0.968 | 89% / 100% | 48 | lateral_freedom_relief | within 1 km 0.08; lateral freedom on relief 0.13 |
| sar-north-passenger | al-jawf → al-qurayyat | 318.1 | 325.5 | 15.05 | 1.597 | 11% / 100% | 13 | grade_choice | within 1 km 0.01; grade term 3.86 |
| sar-east-passenger | riyadh → hufuf | 309.8 | 312.3 | 12.75 | 1.127 | 58% / 95% | 14 | grade_choice | within 1 km 0.08; urban station approach 0.65; grade term 8.12 |
| sar-east-passenger | hufuf → abqaiq | 65.3 | 64.2 | 0.73 | 0.860 | 70% / 89% | 23 | lateral_freedom_flat | within 1 km 0.06; urban station approach 0.05 |
| sar-east-passenger | abqaiq → dammam | 73.9 | 71.0 | 1.58 | 0.963 | 75% / 100% | 16 | lateral_freedom_flat | within 1 km 0.02; urban station approach 0.16; flat-terrain lateral freedom 0.08 |
<!-- /gen:4a-legs -->

km of each line's mean offset attributed to each cause:

<!-- gen:4a-causes -->
| cause | hhr | sar-north-passenger | sar-east-passenger |
|---|---|---|---|
| within 1 km (DEM resolution, smoothing, OSM digitisation) | 0.14 | 0.12 | 0.16 |
| urban station approach (≤ 25 km of a station ≥ 15 % urban) | 1.22 | 0.21 | 0.86 |
| urban penalty: real line runs through urban cells the router avoids | 1.82 | 0.00 | 0.00 |
| grade term: real line takes grades the surface penalises (flat ground) | 0.00 | 8.29 | 8.12 |
| corridor the surface cannot see (longer real line, no surface reason) | 0.14 | 0.73 | 0.00 |
| flat-terrain lateral freedom (surface indifferent, ≤ 2 %) | 0.00 | 0.33 | 0.08 |
| lateral freedom on relief (surface indifferent, ≤ 2 %) | 0.00 | 0.13 | 0.00 |
| **mean offset (sum)** | **3.317** | **9.813** | **9.208** |
<!-- /gen:4a-causes -->

The decomposition above was computed on the stitched HHR geometry (mean 3.317 km). It was not recomputed on the corrected geometry, where the HHR mean offset is 3.399 km (corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE), §4d).

What the evidence says, line by line (in the model; three lines only):

- **SAR East (9.21 km) and SAR North (9.81 km): the grade term, on flat ground.** About 8.1 and 8.3 km of the two means come from legs where the real line is costlier **because of grade**. The legs are Riyadh → Hufuf (leg mean 12.7 km), Al-Qassim → Hail (19.9 km) and Al-Jawf → Al-Qurayyat (15.0 km), and their median relief is only 9–15 m. The 500 m-smoothed surface model still carries metre-scale undulations (dunes, the DSM's surface objects). Under a quadratic grade term from zero, these make the router weave for flatter ground that earthworks would simply absorb. So the brief's "flat-terrain lateral freedom" (the surface indifferent) is only a small share: 0.08 km on SAR East, 0.46 km on SAR North (flat and relief legs together). The cost surface is not indifferent on these legs; it is over-sensitive. A historic route the surface cannot see (the SAR East Kharj–Haradh hypothesis) is not what the cost decomposition finds on the passenger line's Riyadh → Hufuf leg: the real leg is about as long as the routed one (309.8 vs 312.3 km), and the difference is grade.
- **The corridor bonus pulls the wrong way.** On 10 of the 12 legs the routed line runs within about 2 km of a highway on at least 84 % of its samples, and on every leg it does so at least as often as the real line. The real lines often stay away from the roads: SAR North Riyadh → Majmaah 10 % against 89 % routed, Al-Jawf → Al-Qurayyat 11 % against 100 %, HHR Makkah → Jeddah 61 % against 99 %. A stronger highway attractor, one of the candidate priors, would move the routes further from the real lines.
- **HHR (3.32 km on the stitched geometry; 3.399 km on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE)): urban.** The real line runs through urban landuse that the router avoids between Jeddah and Madinah (1.82 km, "avoids urban", mostly on KAIA → KAEC and KAEC → Madinah), and the station approaches account for 1.22 km. The Makkah → Jeddah leg is the Makkah approach loop: the real leg is 78.0 km against a routed 62.3 km, with no surface reason for the extra length (0.14 km "unseen corridor" outside the urban zones).
- **Protected areas, wadis and DEM resolution are minor.** The ≤ 1 km bucket is 0.12–0.16 km per line, and no leg's dominant cause is a protected-area or wadi avoidance.

### 4b. Alignment weights v2 (parallel, frozen; not adopted)

**Priors tested (open data only).** The tested priors come from the diagnosis and from data already in the routing surface:
- a grade dead-band (A-align-101): grades below d × cap cost nothing, since earthworks absorb them;
- longer grade smoothing (A-align-006 re-opened);
- a straightness penalty on flat cells (A-align-102/103): distance to the station-to-station chord;
- a weaker corridor bonus (A-align-029 re-opened, 0 or 0.1 against v1's 0.25);
- the urban penalty (A-align-022 re-opened).

The sources register holds no published reservation geometry that could serve as a prior: its HHR and SAR entries give lengths and station lists, not routes.

**Method** (`network.align_v2`, A-align-100): a full factorial grid of 108 combinations, each routed once per line (324 routings, about 30 minutes on 4 workers; `runs/align/tune-v2-s1/grid.csv`), with the v1 objective A-align-070. Two choices are made from it:
- **Leave-one-out:** for each line, the combination that is best on the other two lines is applied to it.
- **In-sample:** the combination that is best on all three becomes `cities/ksa/assumptions/align_weights_v2.yaml`, frozen with its SHA-256 `8da11430…` in `align_weights_v2.sha256`.

The v2 terms are absent from v1, so v1 routing is byte-identical with the new code: 10/10 corridors re-routed, including both CP7 corridors (`runs/align/scratch/fixr7-v1check`, `logs/fixr7-v1check.log`). `align_weights.yaml` is unchanged (hash `2b718ecb…`).

<!-- gen:4b-loo -->
| held-out line | trained on | chosen (dead-band / smoothing m / straightness / corridor bonus / urban) | training objective km | held-out mean offset km |
|---|---|---|---|---|
| hhr | sar-north-passenger, sar-east-passenger | 0.6 / 1000 / 0.0 / 0.1 / 1.5 | 4.011 | 5.79 |
| sar-north-passenger | hhr, sar-east-passenger | 0.0 / 1000 / 0.05 / 0.1 / 1.5 | 3.642 | 11.46 |
| sar-east-passenger | hhr, sar-north-passenger | 0.0 / 2000 / 0.0 / 0.1 / 1.5 | 5.295 | 13.38 |
| none (in-sample = weights v2) | all three | 0.3 / 2000 / 0.0 / 0.1 / 1.5 | 4.842 | n/a |
<!-- /gen:4b-loo -->

HHR held-out mean offset on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE): 5.957 km if recomputed (main + branch; 6.012 main only), against 5.791 on the stitched geometry. Not recomputed in the tuning run, and no new weights are adopted (§4d).

Before / after per reference line (v1 `runs/align/validation-s1`; v2 in-sample `runs/align/validation-v2-s1`; held-out `runs/align/validation-v2-loo-s1`, each line routed with the weights its fold chose without it). The OSM tunnel and bridge km are the real line's:

<!-- gen:4b-validation -->
| line | weights | routed km | length error | mean offset km | Hausdorff km | P90 offset km | tunnel km (OSM) | viaduct km (OSM bridge) | targets met |
|---|---|---|---|---|---|---|---|---|---|
| hhr | v1 (frozen) | 426.6 | -4.9% | 3.32 | 14.3 | 7.7 | 7.0 (9.3) | 6.8 (44.1) | length yes, offset no |
| hhr | v2 in-sample | 413.7 | -7.8% | 4.52 | 22.9 | 9.2 | 13.3 (9.3) | 15.0 (44.1) | length no, offset no |
| hhr | v2 held-out | 413.2 | -7.9% | 5.79 | 22.7 | 13.7 | 14.9 (9.3) | 14.5 (44.1) | length no, offset no |
| sar-north-passenger | v1 (frozen) | 1262.5 | +1.6% | 9.81 | 53.8 | 26.5 | 4.2 (0.5) | 10.2 (20.1) | length yes, offset no |
| sar-north-passenger | v2 in-sample | 1234.2 | -0.7% | 5.54 | 28.9 | 16.4 | 7.4 (0.5) | 11.9 (20.1) | length yes, offset no |
| sar-north-passenger | v2 held-out | 1234.1 | -0.7% | 11.46 | 36.6 | 28.2 | 7.7 (0.5) | 14.8 (20.1) | length yes, offset no |
| sar-east-passenger | v1 (frozen) | 447.6 | -0.3% | 9.21 | 34.4 | 28.9 | 0.6 (0.1) | 1.0 (0.4) | length yes, offset no |
| sar-east-passenger | v2 in-sample | 442.2 | -1.5% | 2.81 | 10.7 | 7.6 | 1.2 (0.1) | 2.2 (0.4) | length yes, offset no |
| sar-east-passenger | v2 held-out | 453.2 | +0.9% | 13.38 | 44.9 | 40.2 | 0.6 (0.1) | 0.6 (0.4) | length yes, offset no |
<!-- /gen:4b-validation -->

HHR rows on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE) (main + branch; `runs/fix-hhr/check.json`): v1 mean offset 3.399 km (P90 7.757, Hausdorff 14.33); v2 in-sample 4.641 km; v2 held-out 5.957 km. OSM tunnel and bridge km are unchanged with the branch (9.3 / 44.1 km). Main only: 3.432 / 4.686 / 6.012 km. The table above prints the stitched-geometry values from `runs/align/validation-*`.

**Reading.**
- **In-sample, v2 lowers the objective from 7.446 to 4.842 km.** SAR North falls from 9.81 to 5.54 km and SAR East from 9.21 to 2.81 km, through the dead-band (0.3) and 2 km smoothing.
- **But v2 worsens HHR** to 4.52 km (4.641 km on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE), if recomputed) and takes its length error to −7.8 %, outside the ±5 % target that v1 met.
- **Held out, every line is worse than under v1:** HHR 5.79 (5.957 on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE), if recomputed), SAR North 11.46, SAR East 13.38 km. Each fold picks the parameters that suit its two training lines, and the third line wants different ones. Two lines cannot identify a prior that transfers.

The improvement is therefore **not demonstrated out of sample**. The offset is mostly explained by causes that no single open prior fixes on all three lines: grade sensitivity on the SAR lines and urban corridor choices on HHR. The limitation in §0 stays. v2 remains useful as a sensitivity, an equally defensible alternative alignment that shows how much the R7 figures depend on the routing (§4c).

### 4c. The three CP7 corridors under weights v2 (sensitivity; R7 base figures unchanged)

**Which alignments R6/R7 used.**
- `S3-branch_spur-al-kharj` and `S4-commuter_belt-riyadh-225` are DEM-routed under the frozen weights v1. Their sidecars `cities/ksa/alignments/<id>.json` carry `weights_hash` `2b718ecb…`, `weights_frozen: true`, `status: routed` and `run: runs/align/corridors-s1/<id>`: the R4_ALIGN routing, not the R5 H4a re-route, whose 17 corridors in `runs/align/r5-h4a-s1/` do not include these two.
- `S5-station_addition-duruma` is a station addition on existing or committed track. It is **not routed** (§7 decision 4), so weights v1 and v2 do not apply to it. The sidecar `cities/ksa/alignments/S3-branch_spur-duruma.json` belongs to a different corridor, the S3 spur.

**Method** (`uv run python -m funding.r7v2 compare | costs | control | overlay | score | fiscal`):
1. Both routed corridors were re-routed with v2 into `cities/ksa/alignments-v2/` (sidecars and GeoJSON, same schema, label unchanged; runs `runs/align/corridors-v2-s1/`).
2. Both exceed the re-run thresholds (length ±2 %, or tunnel + viaduct or earthworks km ±5 %). They were re-costed with the R5 estimator into `runs/costs-v2/<id>/`; a v1 control re-costing reproduces `runs/costs/<id>/` exactly.
3. They were scored standalone at their CP7 phase (2050) with the frozen judge v3 into `runs/r7/corridors-v2/<id>@2050/`, and the layouts that contain them (S6-L1: Al-Kharj; S6-L3: both) into `runs/r7-v2/top5/<L>/`, with all cases as in R6_V3.
4. The judge reads its inputs from its own root, so its v2 inputs come through an APFS clone of `judge/v3-variants` (`runs/r7-v2/judge-root`). The clone substitutes only the two corridors' YAML, sidecar, cost run and costing spec: 26 of its 2,117 files change, all inside the substitutions, and the other 2,091 are hash-identical (`runs/r7-v2/judge-root.json`); judge code untouched; `optimise.judge verify --name v3-variants` still passes.
5. An unmodified clone reproduces R7's standalone Al-Kharj score exactly (`runs/r7-v2/control/`).
6. Fiscal exposure and VfM were recomputed from those scores into `runs/r7-v2/fiscal/` and `runs/r7-v2/vfm/` (`funding.inputs.OVERRIDES`, additive; empty for the base).

Geometry, v1 against v2:

<!-- gen:4c-geometry -->
| corridor | weights | length km | tunnel km | viaduct km | earthworks km | max formation grade | running time min | re-run |
|---|---|---|---|---|---|---|---|---|
| `S3-branch_spur-al-kharj` | v1 | 139.2 | 0.9 | 1.1 | 4.8 | 0.0250 | 47.9 |  |
| `S3-branch_spur-al-kharj` | v2 | 138.5 | 0.2 | 0.4 | 12.3 | 0.0250 | 47.7 | yes (length -0.5%, tunnel + viaduct -70.0%, earthworks +156.4%, running time -0.5%) |
| `S4-commuter_belt-riyadh-225` | v1 | 79.0 | 3.7 | 4.3 | 18.1 | 0.0250 | 34.8 |  |
| `S4-commuter_belt-riyadh-225` | v2 | 69.5 | 7.0 | 6.7 | 29.6 | 0.0250 | 31.0 | yes (length -12.0%, tunnel + viaduct +71.2%, earthworks +63.5%, running time -11.0%) |
| `S5-station_addition-al-jubayl` | n/a | not routed |  |  |  |  |  | no: station addition on existing or committed track: not routed (docs/alignments.md §7 decision 4); weights v1/v2 do not apply |
| `S5-station_addition-dhahran` | n/a | not routed |  |  |  |  |  | no: station addition on existing or committed track: not routed (docs/alignments.md §7 decision 4); weights v1/v2 do not apply |
| `S5-station_addition-duruma` | n/a | not routed |  |  |  |  |  | no: station addition on existing or committed track: not routed (docs/alignments.md §7 decision 4); weights v1/v2 do not apply |
<!-- /gen:4c-geometry -->

Every R7 figure that moved (SAR million, PV 2026, robust population case, synthetic demand, uncalibrated: scenario comparison, not a forecast; `runs/r7-v2/sensitivity.json`):

<!-- gen:4c-figures -->
| entity | robust NPV | capex P10 / P50 / P90 | net fiscal cost 60 y, fully public, P10 / P50 / P90 | net fiscal cost 60 y, availability PPP, P10 / P50 / P90 | VfM (% of PSC) |
|---|---|---|---|---|---|
| `S3-branch_spur-al-kharj` | 4,309 → 4,577 | 5,433 → 5,210 / 9,771 → 9,272 / 36,018 → 33,868 | 5,258 → 5,127 / 7,523 → 7,247 / 21,226 → 20,087 | 11,253 → 10,786 / 11,253 → 10,786 / 23,174 → 21,946 | -4,230 → -4,013 (-38.5 % → -38.3 %) |
| `S4-commuter_belt-riyadh-225` | -8,293 → -7,778 | 4,717 → 5,202 / 8,910 → 10,227 / 34,256 → 40,520 | 9,130 → 8,571 / 11,320 → 11,194 / 24,551 → 27,008 | 14,721 → 15,098 / 14,721 → 15,098 / 26,286 → 28,963 | -3,860 → -4,432 (-26.2 % → -28.9 %) |
| `S6-L1` | 11,023 → 11,297 | 6,233 → 6,010 / 11,194 → 10,695 / 41,304 → 39,154 | 4,676 → 4,536 / 8,441 → 8,197 / 23,615 → 22,626 | 13,443 → 12,977 / 13,443 → 12,977 / 28,054 → 26,816 | -5,124 → -4,907 (-38.9 % → -38.8 %) |
| `S6-L3` | 2,426 → 3,180 | 10,684 → 10,946 / 19,630 → 20,448 / 73,799 → 77,912 | 12,696 → 12,103 / 18,962 → 18,478 / 45,343 → 46,529 | 27,495 → 27,410 / 27,495 → 27,410 / 53,112 → 54,584 | -8,779 → -9,135 (-32.2 % → -33.4 %) |

Unchanged (no routed corridor re-run in them): `S5-station_addition-al-jubayl`, `S5-station_addition-dhahran`, `S5-station_addition-duruma`, `S6-L2`.
<!-- /gen:4c-figures -->

The v1 figures in `docs/delivery-models.md`, `docs/fiscal-exposure.md`, `recommendations.yaml`, `runs/r6/` and `runs/r7/` are not overwritten. Each affected table there carries one "Alignment v2 sensitivity" line pointing here. If Tariq adopts v2, R6 and R7 would be re-run on v2 for every corridor, not only these two.

### 4d. HHR re-route (FIX_HHR_REROUTE, 6 Nov 2026): corrected geometry, offsets, deltas

FIX_HHR_JEDDAH found that `hhr.geojson` was a stitched LineString with a 17.32 km city-to-airport chord. It rebuilt the file as a MultiLineString: main line 448.54 km plus the KAIA branch, 6.69 km (`docs/network.md` §HHR geometry). This section applies Tariq's decisions of 6 Nov 2026. **Label: hypothetical alignments (ours), indicative engineering sketches, not designs; synthetic demand, uncalibrated: scenario comparison, not a forecast.**

**The frozen v1 weights stay frozen.** `align_weights.yaml` is unchanged (hash `2b718ecb…`, checked before and after the re-route). A-align-070 was not re-tuned. At the frozen weights, its objective would read about **7.473 km** on the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE) (7.446 on the stitched geometry). Weights v2 (FIX_R7, not adopted) would read **4.641 km** in-sample and **5.957 km** held out for HHR if recomputed (4.517 and 5.791 on the stitched geometry). **No new weights are adopted.**

**HHR validation figures**, corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE) (`runs/fix-hhr/check.json`, from `uv run python -m rail.hhr_check --before-rev 0cc369e`). Both conventions are printed below; one is published.

| HHR, weights v1 | stitched (published until 6 Nov 2026) | corrected, main + branch (**published convention**) | corrected, main only |
|---|---|---|---|
| OSM length compared, km (clipped to the routed ends) | 483.331 | 454.070 | 447.391 |
| mean offset, km | 3.317 | **3.399** | 3.432 |
| P90 offset, km | 7.664 | **7.757** | 7.774 |
| Hausdorff, km | 14.328 | **14.330** | 14.329 |
| OSM tunnel km (share) | 9.311 (1.93 %) | **9.311 (2.05 %)** | 2.184 (0.49 %) |
| OSM bridge km (share) | 44.122 (9.13 %) | **44.122 (9.72 %)** | 42.225 (9.44 %) |
| A-align-070 objective at the frozen weights, km | 7.446 | **about 7.473** | about 7.484 |
| v2 in-sample HHR mean offset, km (not adopted) | 4.517 | **4.641** | 4.686 |
| v2 held-out HHR mean offset, km (not adopted) | 5.791 | **5.957** | 6.012 |

**Convention: main + branch.** The routed HHR validation line runs from Makkah through Jeddah and **KAIA** to KAEC and Madinah, and KAIA station lies on the branch. The real track that serves the routed stations is therefore the main line plus the branch. Main + branch is also the drawn geometry with no part dropped, which is the same rule the corridor-bonus band now follows. Tariq's decision figures (7.473, 4.641, 5.957) use it too. `network.align compare` now uses every part; a future validate prints the main + branch figures (S6_L6_CONNECTED item 7, 6 Nov 2026: `osm_line` returns the whole MultiLineString, `compare` clips part 0 to the routed ends, adds the branch whole and measures to the nearest part). Dry check, no routing, no re-tune, no re-route (`uv run python -m network.align recompare`, the existing routed path `runs/align/validation-s1`): HHR mean 3.399 km, P90 7.757, Hausdorff 14.330, 454.070 OSM km compared; A-align-070 objective 7.4733; the SAR North and SAR East rows are unchanged (9.813 / 9.208 km). The routed lengths and the length check do not change (426.6 km against the 448.5 km station span, −4.9 %).

**Corridor-bonus band.** `network.align.rail_mask` now rasterises every part of a MultiLineString, so the band covers the HHR main line and the real KAIA branch, and nothing joins the parts. Test `tests/test_fix_hhr_reroute.py`: in a two-part fixture the branch vertices are in the band and the old chord is not, and on the live `hhr.geojson` the KAIA branch is in the band and the middle of the old KAIA → Al-Sulaimaniyah chord is not.

**Re-route of the four chord-band corridors** (`uv run python -m network.reroute route | control | band | deltas | apply --seed 1`; runs `runs/fix-hhr-reroute/`, code d6c8321, frozen v1 weights; previous sidecars kept in `runs/fix-hhr-reroute/before/`). Only these four corridors were re-routed. `S4-commuter_belt-jeddah-045` left the corridor set at R5 H4a, but its R4_ALIGN sidecar is still in `cities/ksa/alignments/`. It was routed from its last corridor YAML (`git 6318367^`) and has no costs, CBA case or layout downstream.

<!-- deltas: runs/fix-hhr-reroute/deltas.csv -->
| corridor | length km old → new | tunnel / viaduct / earthworks km old → new | max formation grade | running time, all-stop, min (R4 model) old → new | mean / max lateral offset old–new path, km | km of path moved > 500 m | moved materially |
|---|---|---|---|---|---|---|---|
| S4-commuter_belt-jeddah-000 | 78.140 → 78.140 (0) | 0.000 / 0.799 / 1.899 → same (0) | 2.502 % → 2.502 % | 32.52 → 32.52 (0) | 0.000 / 0.000 | 0.000 | no |
| S4-commuter_belt-jeddah-045 (not in the set) | 66.276 → 66.276 (0) | 0.400 / 0.200 / 15.094 → same (0) | 2.503 % → 2.503 % | 27.73 → 27.73 (0) | 0.000 / 0.000 | 0.000 | no |
| S4-commuter_belt-jeddah-315 | 84.509 → 84.509 (0) | 0.000 / 0.999 / 0.000 → same (0) | 2.502 % → 2.502 % | 35.10 → 35.10 (0) | 0.000 / 0.000 | 0.000 | no |
| S2-trunk_gap-riyadh-jeddah | 893.484 → 893.484 (0) | 13.398 / 16.397 / 121.175 → same (0) | 2.503 % → 2.503 % | 217.52 → 217.52 (0) | 0.000 / 0.000 | 0.000 | no |

"Moved materially" was defined before the deltas were computed (`cities/ksa/assumptions/reroute_thresholds.yaml`, A-align-120…124, proposed). A corridor moved materially if any of these held: length change > 1 %; tunnel, viaduct or earthworks km change > 1 %; all-stop running time change > 0.5 min; maximum lateral offset > 1 km. **None of the four moved.** The routed `alignment.geojson`, `summary.json` and `profile.parquet` are byte-identical to the previous runs (`runs/align/r5-h4a-s1/` for 000 and Riyadh–Jeddah, `runs/align/corridors-s1/` for 045 and 315). The live sidecars now point at the new runs (`run:` only; the corridor YAMLs regenerated by `screening.corridors generate` differ from the previous ones in that line only).

**Why nothing moved** (`runs/fix-hhr-reroute/band-diff.json`, window 38.9–39.5 E, 21.2–22.0 N).
- The corridor flag (A-align-029) is "within 1 km of an OSM motorway/trunk/primary **or** an existing rail line".
- Every cell under the old chord also lies within 1 km of an OSM highway. At the coarse routing step (15″), the rail cells change (36), but the corridor flag changes in **0** cells. At the fine step (3″), it changes in 2 of 219 changed rail cells, and neither lies on any of the eight paths (four before, four after).
- The control (`network.reroute control`) routes the four on the old stitched `hhr.geojson` (0cc369e) with today's code. It reproduces the previous runs byte for byte, so the comparison isolates the geometry.
- FIX_HHR_JEDDAH counted routed vertices inside the chord's rail band (6/5/1/1). That band had no effect on the cost surface, because the highway corridor covered the same cells.

**Downstream.** No corridor moved materially, so nothing downstream was re-run:
- R5 costs (`runs/costs/<id>/`), skims and running times;
- judge v3 standalone scores and the S6 layouts (S6-L5 contains belts 000 and 315; no `scenarios/S6-L*.yaml` or `runs/r6/top5/` input changed);
- the Riyadh–Jeddah and belt CBA cases (`runs/cba/CBA-S2-trunk_gap-riyadh-jeddah*`, `CBA-S4-commuter_belt-jeddah-000*`, `-315*`);
- R7 fiscal/VfM (none of the four is in the CP7 layouts L1–L3);
- R8 documents and figures.

No corridor, cost, benefit or programme number changes; the HHR validation and tuning figures above are the only published numbers that change.

## 5. Results

Corridor-level results are in `docs/alignments-tables.md` §3–4: detour-ratio distribution, tunnel/viaduct/earthworks km by family and per corridor, the trunk alternatives, and before/after cost, running time, 30-minute test and ranks. The headlines, all from those tables (runs `runs/align/corridors-s1`, `runs/r4a/compare-s1`, seed 1):

**Routing**
- 67 corridors routed: 15,300.6 routed km against 13,645.4 straight-line km.
- Detour ratio: min 1.004, P10 1.032, P50 1.099, P90 1.299, max 1.870.
- Measured structures: 496.1 km tunnel, 549.9 km viaduct (a lower bound, §4), 3,062.2 km of earthworks.
- 254.7 km run under curve speed restrictions.
- The largest detours are escarpment climbs under the grade cap: Makkah commuter belt 090 at 1.87 (towards Taif), Jazan–Najran at 1.55, Taif spur at 1.51, Madinah–Yanbu at 1.50, Taif belt 270 at 1.47, Riyadh belt 180 at 1.46 (Tuwaiq).
- **Jazan–Najran is the extreme case:** sea level to about 2,400 m, mixed class at 1.25 %. It needs 108.7 km of tunnel and 69.8 km of viaduct in 295.6 km, so its base capex P50 rises from SAR 13.7 bn to 64.8 bn. At the 2.5 % passenger cap it would need fewer structures. **The class choice drives this corridor.**

**Costs**
- **One corridor is not costed:** S4 Abha belt 315, leg An-Nimas → Al-Majaridah, drops 1,892 m in 27.2 km of route. At the 2.5 % commuter cap it needs at least 75.7 km of line, so no profile meets the cap. It is flagged `profile_feasible: false` and left uncosted rather than given invented spiral tunnels (A-align-091). The red-team verifier found it (pass 1). It needs a station move, a different class or a development length, decided at CP5. Its running time and reach in the S4 summary still come from the infeasible profile; they are indicative only.
- Base capex P50 change per costed corridor: P10 −20.7 %, median −3.7 %, P90 +124.1 %.
- Flat-desert corridors get cheaper. The sketch-era proxies gave them viaduct and tunnel shares and an "unknown" terrain filled as flat desert; the measured shares are smaller, and viaduct is a lower bound. Arar–Hafar al-Batin falls from SAR 31.4 bn to 24.8 bn.
- Escarpment corridors get much dearer: the Abha–Khamis Mushait belts 135 and 270 go from SAR 10.2 and 8.7 bn to 29.0 and 24.9 bn.
- Sum of base capex P50 over S2–S5: SAR 969.1 bn before (76 corridors) and 1,101.6 bn after (75 costed). This is a sum of medians, for scale only.

**Running times**
- Median change −7.0 % (P10 −13.7 %, P90 +18.1 %). The routed length (median detour 1.10) replaces the 1.2 route factor, and curve limits apply only where the smoothing could not reach R_min.

**30-minute test**
- 1,439 town–metro pairs within 30 in-vehicle minutes before, 1,441 after: 2 gained, 0 lost.
  - Sarat Abidah on Abha–Najran: 30.3 → 27.0 min.
  - Farasan on the Jazan belt 225: 33.2 → 29.2 min. Farasan is an island: the routed belt crosses 38.2 km of open sea as a bridge priced at the viaduct rate (a lower bound). This is the R4 sea-crossing artefact, already on the CP5 list (decision 2: drop this belt).

**Ranks**
- 47 corridors move more than 5 places by uplifted capex or by capex per person newly reached within 60 minutes (the uncosted belt has no rank). Ranks are relative, so the escarpment corridors moving down push the flat ones up. The list is in `docs/alignments-tables.md` §4.

## 6. Re-run of screening and corridor generation

- **Corridor generation** was re-run with the R2 inputs unchanged (candidates `d31ec39b4d9a`, from git `c52439b^`; scores `7b98bec42055`; rules `c677aa2ed78b`). The unmodified generator reproduces the 76 committed corridor YAMLs byte for byte from these inputs, so the regeneration isolates the alignment effect and does not pre-empt CP5 decision 2 (regenerate from the R4 short list).
  - With `--alignments`, each routed corridor takes its routed km-posts, length, terrain and structures (A-align-080).
  - The trunk detour test (A-corr-005) divides the rail path by the **routed** length where one exists (A-align-081: a change of the rule's denominator, recorded as its own assumption). Two network/routed ratios fall below 1 (Jeddah–Madinah via HHR 0.98; the T2 speed-gap corridor Riyadh–Jeddah via the Landbridge 0.98): the existing line is shorter than our terrain-routed line. Every generated T1 corridor has no rail path at all, so the ratio cannot remove any of them. The only T2 pair the lower ratio could add, Riyadh–Madinah, stays at 1.67 > 1.4. Where a generated corridor and an alternative share the same stations (Riyadh–Dammam), the test uses the generated corridor's sidecar: HSR class, 401.2 km, ratio 1.14. The mixed-class alternative routed for the test is 404.6 km (1.13); the decision is the same. **The corridor set is unchanged: 76 (23/17/27/9).** Station ids and coordinates are identical; only the km-posts and the routed fields change.
  - The four trunk pairs not generated in R2 were routed too (`cities/ksa/alignments/alternatives/`), so the test could be re-run on them: Jeddah–Madinah, Riyadh–Buraidah and Riyadh–Dammam (dominated) and Riyadh–Madinah (not a speed gap).
- **The screening funnel** (`screening/run_r4.sh`) was re-run after the routing. Its criteria are population, distance to the S0 lines, road minutes or S0 rail minutes to a metro, economic roles and the register terrain class. None of them reads a hypothetical alignment, so **no town can change rank because of R4_ALIGN, and none does** (diff in `runs/r4a/compare-s1/towns.csv`). Rank changes of more than 5 places are therefore reported for **corridors** (`docs/alignments-tables.md` §4), by uplifted P50 capex and by uplifted P50 capex per person newly reached within 60 in-vehicle minutes.

## 7. Decisions (no one to ask; recorded)

1. **90 m for every corridor; no 30 m pass.** Routing at 3″ takes about 1.5 minutes for all 67 corridors with 3 workers. A 30 m pass for a short list is deferred because no corridor short list exists before R6 (A-align-001).
2. **Length reference for validation:** the line YAML's along-track station span, not the full OSM geometry. The old HHR geometry measured 484.6 km against 448.5 km between the Makkah and Madinah stations. The extra length was the stitch (17.32 km), the duplicated Sulaimaniyah–junction stretch (12.04 km) and the KAIA branch (6.69 km) of a wrongly stitched LineString; it was not yards and approach tracks. On the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE), the main line measures 448.54 km, equal to the station span, and the KAIA branch 6.69 km (`docs/network.md` §HHR geometry). The decision stands.
3. **Protected-area weight kept at 0.3** against a noise-level tuning preference for 0 (§4).
4. **Station additions are not routed** (on existing or committed track).
5. **Passenger-only conventional and commuter lines take the 2.5 % cap**; mixed lines keep Tariq's 1.25 %.
6. **WDPA not used** (non-commercial); OSM protected areas instead.
7. **Earthworks are measured but not priced separately:** the register has no earthworks item, and the at-grade base includes earthworks (C-line-type-*-ec-base). Escarpment and coastal terrain still carry no premium (`costs/config/estimate_map.yaml`); their cost now comes through the measured structures.

## 8. What could not be done

- The mean-offset target (< 2 km) was not met on any validation line (§4).
- FIX_R7 (4 Nov 2026): the offsets were diagnosed (§4a), and a weights set v2 tuned with leave-one-out validation did not improve any held-out line (§4b). The limitation sentence in §0 applies to every R4–R7 figure.
- Viaducts are under-counted (no wadi or urban viaduct rule): HHR 6.8 km modelled against 44.1 km of OSM bridge tags. Measured viaduct km and the structure capex are lower bounds (cost-estimator review). A viaduct-share uplift from this validation (n = 1) would need Tariq's approval.
- One open-sea crossing (Jazan belt 225 to Farasan, 38.2 km) is priced at the viaduct rate, a lower bound for a sea bridge.
- Heavy earthworks (e.g. 10.6 M m³ of fill on Abha–Bisha) are measured but not priced: there is no register item.
- No 30 m pass.
- No openly published restricted-zone data beyond OSM military areas.
- Flow accumulation is window-limited, without pit filling.
- No vertical-curve constraint in the profile.
- The DEM is a surface model: buildings remain in urban sections despite the median filter.
- The 9 station additions were not re-run, since nothing changed for them.
