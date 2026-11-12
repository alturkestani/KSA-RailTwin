> **Document version:** docs/good-first-issues.md v1.2 | 7 Nov 2026 | Author: report-writer (R9); FIX_LICENCE_NAMED_FLAGS (v1.1: section H blocker count 46 → 4); FIX_LICENCE_CITE_TERMS (v1.2: section H blocker count 4 → 2) | Status: draft

# Good-first issues and open gaps (for manual filing)

**Nothing in this list has been created on GitHub.** No issue, label, milestone or remote exists. Tariq opens the issues by hand when the repository is published. Each entry below is written so that it can be pasted into a GitHub issue as it stands.

This list includes every outstanding gap the repository records, as rule 2 ("no silent omissions") requires, and not only the easy ones. Each entry carries a label suggestion:

- `good first issue`: self-contained, needs no owner decision, and comes with a test that proves it is done.
- `data`: desk research for an open, licence-compatible source (rule 4). The source is recorded with the `source-citation` skill. Contributors use **published material only** and never contact any agency, company or person (rule 7).
- `docs`: register or document hygiene that changes no value.
- `needs-owner-decision`: **not a contributor task.** It waits for a decision by the project owner. It is listed here so the gap stays visible. Contributors should not open a pull request that settles it.

Every modelled output mentioned below is **synthetic demand, uncalibrated: scenario comparison, not a forecast**. Cost and benefit figures stay P10/P50/P90 ranges. Planned lines stay **announced/planned** (rule 5).

**Standard checks.** Every issue's acceptance test includes the standard checks: `make test` passes (ruff, pytest, `common.docver check`, `uv run python -m common.manifest verify`), and any new source id resolves with `uv run python -m common.sources check <changed files>`. The tests listed under each issue are in addition to these.

Do not use the **Transit Costs Project** (NYU Marron Institute). It is a hard stop (`docs/licences-blockers.md`, register row #189: all rights reserved, no licence stated). No figure, table or benchmark may come from it. It is not an issue to work on.

---

## A. Data gaps (`docs/data-sources.md`)

`docs/data-sources.md` (v0.3, 31 Oct 2026) has **9 table rows with status "not found"/"none found"** and **21 rows with status "unverified"** (counted on the last cell of each table row). It also has a five-item "Not found / to verify" list. Some rows predate later work (see GFI-001).

### GFI-001 Refresh the stale statuses in `docs/data-sources.md`
- **Files:** `docs/data-sources.md` (lines 88, 120, 122, 150, 157; "Not found / to verify" list), `docs/sources/index.csv`, `docs/gastat-regions.md`.
- **Gap:** several rows still say "unverified" or "not found" although later work obtained the source:
  - The GASTAT Census 2022 governorate table (150 rows) and the city ≥ 5,000 table are now primary TA1 exports: S-cp2-gastat-007/008 (`docs/STATUS.md`, CP2_PREP GASTAT decisions). Lines 88, 120, 122 and 157 still say "unverified (portal unreachable)". The governorate-count bullet still says "not found within the hour", and `docs/gastat-regions.md` (v0.1) still describes the 150-row list as secondary.
  - The SAPTCO row (line 150, `not found`, S-r1a-522) predates S-r3-cal-023 (the SAPTCO-Alsa southern concession figures) and the licence-register row "SAPTCO Annual Report 2025 (English PDF)".
- **Acceptance test:** each of those rows names the later source id and a status from the file's own legend (`verified`/`secondary`/`unverified`). `uv run python -m common.sources check docs/data-sources.md docs/gastat-regions.md` exits 0. The document version line is bumped.
- **Skill:** `source-citation`.
- **Label:** `docs`, `good first issue`.

### GFI-002 Find the GASTAT locality table (places below 5,000 inhabitants)
- **Files:** `docs/data-sources.md` line 123 ("GASTAT locality tables … not found"), `docs/screening.md` §2 ("Known, unplaced"), `docs/assumptions.md` A-al_jouf-003.
- **Gap:** no locality-level Census 2022 table has been found. Without it, the 33 known primary cities stay unplaced (`docs/screening.md` line 264: "a GASTAT locality table would place them"; one is ≥ 10,000). A-al_jouf-003 also stays an untested presumption.
- **Acceptance test:**
  1. A manifest row in `cities/ksa/sources.yaml` with SHA-256 and access date, and `uv run python -m common.manifest verify` passes. Alternatively, a dated "searched, not found" note naming where you searched.
  2. If found: the unplaced list in `docs/screening.md` §2 shrinks, each placement cites the new source id, and A-al_jouf-003 moves from "assumption" to `sourced`.
- **Skill:** `source-citation`, `region-sweep`.
- **Label:** `data`.

### GFI-003 GASTAT population projection and regional population estimates
- **Files:** `docs/data-sources.md` lines 89 (S-091), 153 (S-r1a-525) and 154 (UN WPP 2024 download page HTTP 404, S-r1a-526).
- **Gap:** the GASTAT projection and the regional estimates for 2023–2025 were not found. The UN WPP national control total rests on a secondary relay.
- **Acceptance test:** the rows move to `verified` with a new source id and a manifest row for any stored file. Any affected `A-pop-*` row in `docs/assumptions.md` names the new source.
- **Skill:** `source-citation`, `assumptions-register`.
- **Label:** `data`.

### GFI-004 Regional economic tables
- **Files:** `docs/data-sources.md` lines 143 (LFS regional tables), 144 (regional GDP, S-r1a-528), 145 (VIIRS night lights: licence unverified) and 147 (REGA/MoJ real-estate transactions, S-r1a-529).
- **Gap:** no open regional GDP, regional labour-force or transaction tables. The VIIRS product page states no licence.
- **Acceptance test:** each row is either `verified` with an source id, or stays `not found` with a dated "searched:" note. A VIIRS licence finding goes into `docs/licences.csv`, and `uv run python -m common.licences check` reports 0 differences after `sync`.
- **Skill:** `source-citation`, `licence-register`.
- **Label:** `data`.

### GFI-005 Observed travel data: domestic air OD, road counts, intercity bus
- **Files:** `docs/data-sources.md` lines 148 (air city pairs: "not found (OD)"), 149 (intercity bus: no TGA primary read), 150 (SAPTCO routes) and 155 (open road traffic counts, S-r1a-531). Related: `docs/assumptions.md` A-access-012 (car peak factor, assumed because no open intercity peak-speed data exist) and A-r4-air-001.
- **Gap:** no open origin–destination or count data to test the modelled air, bus and road flows. Those flows are synthetic demand, uncalibrated: scenario comparison, not a forecast.
- **Acceptance test:** a new source id per source, with the licence recorded in `docs/licences.csv` (Google, TomTom and HERE traffic are excluded by rule 4). The data-sources row is updated, and the dependent `A-` row names the source or stays `assumed` with the search recorded.
- **Skill:** `source-citation`, `licence-register`, `gravity-calibration` (if a table is found).
- **Label:** `data`.

### GFI-006 Official dated HHR timetable, fares and inter-station distances
- **Files:** `docs/data-sources.md` lines 27 (S-006: distances 17/94/261 km not found), 90 and 116 (timetables unverified: S-r1a-003, S-r1a-025). Also `cities/ksa/lines/hhr.yaml` and `network/hhr_check.yaml`.
- **Gap:** CP5 decision H1a accepts the HHR running-time model at ±15 % "until an official dated HHR timetable or speed profile exists, then re-run" (`docs/STATUS.md`, CP5 decisions). No such document has been found.
- **Acceptance test:** an official SAR/HHR document with a date, registered with an source id. The line YAML cites it under `source:`. `make test` passes. The re-run itself is an owner step.
- **Skill:** `source-citation`, `line-yaml`.
- **Label:** `data`.

### GFI-007 Announced/planned line facts and the 13 unlocated stations
- **Files:**
  - `docs/data-sources.md` lines 29–30 (Haramain cost and O&M term, C-004), 37 (North line cost, C-007), 43 (Landbridge cost, C-001), 46 (MEED Projects station list, S-061, paywall), 47 ("Jamuma" site unlocated, S-062/063) and 56 (intercity passenger-km 2023, C-009).
  - `cities/ksa/lines/stations.geojson`.
- **Gap:**
  - 153 stations in total. **13 have `located: false`.** Ten are committed: GCC railway Kuwait border, Dammam and UAE border; Landbridge Riyadh, Dawadmi, Muwai, Al-Jumum and Jeddah; and the two Riyadh Rail Link connections. Three are existing freight sites: Dammam port, Riyadh dry port and Ras Al-Khair.
  - The `uncertainty_km` values range from 1.1 to 19.9.
  - All committed lines remain **announced/planned**.
- **Acceptance test:** each station that gains a location cites an official publication. `located` becomes true with `location_method` and `source` set. `uv run python -m rail.lines validate cities/ksa/lines` exits 0, and `make test` passes. Each conflict row C-001/C-004/C-007/C-009 in `docs/sources/conflicts.md` is resolved, or stays open with the new evidence logged.
- **Skill:** `line-yaml`, `source-citation`, `geo-verify`.
- **Label:** `data`.

### GFI-008 Replace secondary aggregator rows with primaries
- **Files:** `docs/data-sources.md`:
  - "Secondary (aggregators)" table: citypopulation.de city populations S-080…S-089, GLMM census table, Wikipedia, MEED/ENR/trade press (line 99, "paywall, 403").
  - Line 125 (WorldPop: "derived, unverified").
  - Line 127 (Mawani ports: primary unverified).
- **Gap:** these facts are cited from aggregators or relays, and the file itself says to replace them with primaries "before reporting".
- **Acceptance test:** each replaced fact carries a primary source id with status `verified`. The aggregator row is kept as a cross-check (never overwritten), and `uv run python -m common.sources check docs/data-sources.md` exits 0.
- **Skill:** `source-citation`.
- **Label:** `data`, `good first issue` (one city per pull request).

---

## B. Assumptions awaiting sources (`docs/assumptions.md`, `docs/study-rj/assumptions.md`)

**`docs/assumptions.md` (v1.28) has 765 rows** (765 unique ids). Status, read from the status column (second-to-last cell):

| status | rows |
|---|---|
| assumed | 638 |
| sourced | 57 |
| derived | 21 |
| tuned | 11 |
| superseded | 11 |
| open | 5 |
| proposed | 5 |
| decided | 4 |
| approved | 2 |
| calibrated | 2 |
| applied | 2 |
| cross-check only | 1 |
| secondary | 1 |
| unverified | 1 |
| verified | 1 |
| accepted | 1 |
| merged | 1 |
| adopted | 1 |

The 11 `superseded` rows include the 7 `[pre-R5]`/`[pre-R7]` history rows, which are excluded below.

**Awaiting a source: 650 rows**: assumed 638, open 5, proposed 5, secondary 1, unverified 1. `docs/study-rj/assumptions.md` has 9 rows: 8 assumed, 1 derived. `docs/report/annex-assumptions.md` is a generated copy of the main register (same 765 rows), regenerated by `uv run python -m common.report build`. Do not edit it by hand.

Some `assumed` rows were approved by the owner at a checkpoint (for example A-cba-106 at CP6 P2a, and the P9a list). Approval does not make a value sourced. A contributor may add a source or a sourced range, but must not change an approved value without an owner decision.

Ids below are compact: `A-cba-001…004, 010` means A-cba-001 to A-cba-004 and A-cba-010.

### GFI-009 Repair the five malformed register rows
- **Files:** `docs/assumptions.md` lines 48, 49, 55, 784 and 789.
- **Gap:** unescaped `|` characters inside cells give the wrong cell count. The register format has 8 cells per row.
  - A-align-044 and A-align-045 (`|formation − ground|`, `|h|`) have 10 cells.
  - A-align-070 (`|length error|`) has 10 cells.
  - A-screen-pilot-002 [northern_borders] (`flat_desert | dunes`) has 9 cells.
  - A-screen-pilot-002 [najran] has 7 cells (a missing column).
- **Acceptance test:** the row-split command in "How these counts were produced" reports 8 cells for every row (escape as `\|`). The annex is regenerated with `uv run python -m common.report build`, and `uv run python -m common.report check` passes.
- **Skill:** `assumptions-register`.
- **Label:** `docs`, `good first issue`.

### GFI-010 Retire the region terrain rows replaced by the R3 DEM classes
- **Files:** `docs/assumptions.md`, `cities/ksa/candidates.parquet`.
- **Gap:** 11 region-sweep rows still say terrain is region-level, null or "pending DEM": A-al_baha-001, A-al_jouf-002 (open), A-hail-001, A-jazan-002, A-madinah-008 (unverified), A-makkah-010 (open), A-najran-001, A-northern_borders-001, A-qassim-001, A-riyadh-003 and A-tabuk-003. Yet `candidates.parquet` now has **0 null `terrain_class`** in 1,224 rows (flat_desert 781, mixed 202, escarpment_mountain 156, coastal 63, sabkha 13, dunes 9), from the R3 DEM rules A-geo-011…021.
- **Acceptance test:** each of the 11 rows reads `superseded` with the replacing ids. If a row is still used, it states where.
- **Skill:** `assumptions-register`.
- **Label:** `docs`, `good first issue`.

### GFI-011 Confirm or retire the 53 pilot-era rows
- **Files:** `docs/assumptions.md` "Pilot assumptions (merged by PILOT_MERGE, 30 Oct 2026)".
- **Gap:** 52 `A-screen-pilot-00n [region]` rows and A-screen-pilot-terrain-001 [tabuk] are all `assumed`. They describe the pilot register (haversine distances, region terrain, metro proxies), which R1a/R2/R3 rebuilt.
  - A-screen-pilot-001: al_baha, al_jouf, asir, eastern, hail, jazan, madinah, makkah, najran, northern_borders, qassim, riyadh, tabuk.
  - A-screen-pilot-002: al_baha, al_jouf, asir, eastern, hail, jazan, madinah, makkah, najran, northern_borders, riyadh, tabuk.
  - A-screen-pilot-003: al_baha, al_jouf, asir, eastern, jazan, madinah, makkah, riyadh.
  - A-screen-pilot-004: al_baha, al_jouf, asir, hail, jazan, madinah, northern_borders, riyadh.
  - A-screen-pilot-005: asir, eastern, hail, jazan, madinah, northern_borders.
  - A-screen-pilot-006: asir, hail, jazan, northern_borders.
  - A-screen-pilot-007: asir.
  - Also A-screen-pilot-terrain-001 [tabuk], A-najran-osm-001 [najran], A-najran-pop-001 [najran], A-najran-terrain-001 [najran] and A-qassim-terrain-001 [qassim] (the last four are counted in GFI-013).
- **Acceptance test:** each row either reads `superseded` with the replacing R1a/R2/R3 id, or keeps `assumed` with the file that still reads it.
- **Skill:** `assumptions-register`.
- **Label:** `docs`.

### GFI-012 Open and proposed rows waiting for an owner decision
- **Files:** `docs/assumptions.md`.
- **Gap:**
  - A-al_jouf-001 (governorate count 4 vs 3: "count conflict unresolved; merge-stage decision requested").
  - A-al_jouf-005 (Ghata: no located source; candidate OSM node not confirmed).
  - A-al_jouf-007 (MODON role on Sakaka: keep or drop).
  - A-align-120…124 (`proposed` materiality thresholds, FIX_HHR_REROUTE).
- **Acceptance test:** an owner decision recorded in `docs/STATUS.md`, and the row status updated to it.
- **Skill:** `assumptions-register`.
- **Label:** `needs-owner-decision`.

### GFI-013 Region-sweep assumptions (70 rows)
- **Files:** `docs/assumptions.md`, `docs/regions/<region>.md`, `cities/ksa/regions/<region>.parquet`.
- **Ids:**
  - A-al_baha-001…005; A-al_jouf-001…003, 005, 007; A-asir-001…005; A-eastern-002…009; A-hail-001…002; A-jazan-001…002, 004, 006…007 (007 `secondary`).
  - A-madinah-001…005, 007…008 (008 `unverified`); A-makkah-001…004, 007, 010 (010 `open`); A-najran-001…003, 005; A-najran-osm-001 [najran]; A-najran-pop-001 [najran]; A-najran-terrain-001 [najran].
  - A-northern_borders-001…005; A-qassim-001…006; A-qassim-terrain-001 [qassim]; A-riyadh-001…004, 006; A-tabuk-002…004.
  - This set includes the 11 terrain rows of GFI-010 and the 3 open A-al_jouf rows of GFI-012.
- **Gap:** location, role and population rules taken in the sweeps without a primary source. Example: A-al_baha-003, the host town of the Al-Bahah airport role, is "assumed, flagged".
- **Acceptance test:** for each row worked, either `sourced` with an source id, or `assumed` with a sourced range. The region parquet is unchanged unless the value changes. If it changes, `make test` passes and the region note in `docs/regions/` is updated.
- **Skill:** `region-sweep`, `geo-verify`, `assumptions-register`.
- **Label:** `data`.

### GFI-014 Appraisal assumptions (80 rows)
- **Files:** `docs/assumptions.md`, `cities/ksa/assumptions/cba_*.yaml`.
- **Ids:** A-cba-001…004, 010, 104…107, 109…119, 122…126, 130…131, 133…134, 137…140, 142, 201…224, 230…237, 301…310, 312…315.
- **Gap:** appraisal parameters (values of time, growth, externality unit values, opex shares) without a Saudi source. Several were approved by the owner, which does not make them sourced.
- **Acceptance test:** a row moves from `assumed` to `sourced` with an source id, or gains a sourced range. A value change re-runs nothing on its own: the CBA re-run is an owner step, and results stay P10/P50/P90.
- **Skill:** `cba-appraisal`, `assumptions-register`.
- **Label:** `data`.

### GFI-015 Demand, mode-choice and access assumptions (147 rows)
- **Files:** `docs/assumptions.md`, `cities/ksa/assumptions/` (demand, mode choice, access YAMLs).
- **Ids:**
  - A-demand-001…025, 027…050, 052…060; A-mode-001…041; A-access-010…012.
  - A-r4-acc-001…006; A-r4-air-001; A-r4-bus-001…002; A-r4-rt-001…010, 012; A-r4-cpl-002…004.
  - A-intl-001, 006…009; A-pop-001…003, 005…018.
- **Gap:** behavioural and demand constants transferred from the literature or set by judgement. Every output that depends on them is synthetic demand, uncalibrated: scenario comparison, not a forecast.
- **Acceptance test:** as in GFI-014. A KSA-specific source replaces a transfer, and the row names it.
- **Skill:** `gravity-calibration`, `isochrone-commute`, `assumptions-register`.
- **Label:** `data`.

### GFI-016 Cost and reference-class assumptions (55 rows)
- **Files:** `docs/assumptions.md`, `docs/costs.md`, `costs/config/`.
- **Ids:** A-cost-001…018, 100…101, 200…203, 250…251, 300…307, 401…403; A-rcf-029…040; A-r4-cost-001…003; A-hhr-001…003.
- **Gap:** cost spreads, terrain premiums and reference-class choices without a KSA outturn source. Do not draw on the Transit Costs Project.
- **Acceptance test:** a sourced value or range with an source id. `uv run python -m costs.register validate` exits 0 (it checks that source and assumption ids exist), and `make test` passes.
- **Skill:** `cost-register`, `reference-class-forecasting`, `assumptions-register`.
- **Label:** `data`.

### GFI-017 Network, alignment, station and geo-verify assumptions (103 rows)
- **Files:** `docs/assumptions.md`, `network/`, `docs/alignments.md`, `docs/geo-verify.md`.
- **Ids:** A-align-001…005, 011…012, 023…024, 028, 030, 040…045, 050…053, 060, 070, 081, 090…091, 100, 103, 110…113, 120…124 (120…124 `proposed`, see GFI-012); A-stn-001…009; A-r1a-001…028, 030…035, A-r1a-006b; A-geo-001…021; A-data-001.
- **Gap:** routing resolution, gradient caps, structure shares, geo-verify thresholds, station-siting rules.
- **Acceptance test:** as in GFI-014. Any alignment change is an owner re-run, because the frozen judge uses the weights.
- **Skill:** `osm-ksa-rail-network`, `geo-verify`, `line-yaml`, `assumptions-register`.
- **Label:** `data`.

### GFI-018 Screening, corridor and optimisation assumptions (72 rows)
- **Files:** `docs/assumptions.md`, `screening/`, `optimise/`, `docs/r6-topology.md`.
- **Ids:** A-screen-001…011, 013…014, 020…033, 035, 037…041, 043…044; A-corr-001…011, 013…015; A-r2-001, 003…004; A-r6-001…002, 004…007, 010, 013, 101…107, 130…134.
- **Gap:** weights, thresholds and search settings. Most are method choices, where the honest status may stay `assumed` with a stated reason and range.
- **Acceptance test:** every row worked has a range and a reason (or a source). `make test` passes.
- **Skill:** `screening-funnel`, `corridor-generator`, `pareto-optimizer`, `assumptions-register`.
- **Label:** `docs`.

### GFI-019 Funding, social, benchmark and film assumptions (70 rows)
- **Files:** `docs/assumptions.md`, `cities/ksa/funding/`, `docs/social.md`, `docs/survey/`.
- **Ids:** A-fund-001…002, 004…007, 009, 103…104, 106…109; A-social-001…002, 009…012, 014…015, 100…145; A-bench-001…002; A-film-001.
- **Gap:** PPP parameters (see also GFI-039), social and survey-design constants, benchmark conversion rules.
- **Acceptance test:** as in GFI-014. Survey items stay **designed only**: nobody fields a survey.
- **Skill:** `ppp-structuring`, `survey-design`, `benchmark-dossier`, `assumptions-register`.
- **Label:** `data`.

### GFI-020 Study-RJ assumptions (8 rows)
- **Files:** `docs/study-rj/assumptions.md`, `docs/rj-routes-study.md`.
- **Ids:** A-rj-001…006, 008…009 (`assumed`); A-rj-007 is `derived`.
- **Gap:** the Riyadh–Jeddah route-families study keeps a local register. It is a study sketch, not the recommended programme.
- **Acceptance test:** as in GFI-014. The rows stay in the local register, as the study's rule requires.
- **Skill:** `assumptions-register`.
- **Label:** `data`.

---

## Assumption totals by workstream (658 rows awaiting a source)

GFI-013 to GFI-020 above give the full id lists by workstream: 650 rows in the main register plus 8 in study-rj. No awaiting row is left out. The awaiting rows in the main register add up as follows (counted by the grouping command below):

| workstream | rows |
|---|---|
| appraisal | 80 |
| demand / mode / access | 147 |
| costs | 55 |
| network / alignment / geo | 103 |
| screening / corridors / optimisation | 72 |
| region sweeps | 70 |
| pilot rows | 53 |
| funding / social / benchmarks / film | 70 |
| **total** | **650** |

---

## C. Benchmark rows graded C or D

The grades are defined in `docs/benchmarks/METHOD.md`:
- A: primary official.
- B: peer-reviewed or audited.
- C: reputable secondary.
- D: unverified (Wikipedia, blogs, unsourced press, unopened snippets). D rows are "to verify" and excluded from the README totals.

Counts:
- `cities/ksa/benchmarks/metrics.csv`: 524 rows (A 293, B 14, C 179, D 38). It equals the 13 `metrics-<slug>.csv` files row for row.
- `cities/ksa/benchmarks/overruns.csv`: 103 rows (A 68, B 1, C 28, D 6).

### GFI-021 Verify or drop the 44 grade-D benchmark rows
- **Files:** `cities/ksa/benchmarks/metrics-<slug>.csv`, `overruns-<slug>.csv`, `docs/benchmarks/<slug>.md`, `docs/sources/bench-<slug>.csv`.
- **Metric rows graded D (38):**
  - egypt: M-eg-006, 017, 022…023, 027
  - japan: M-jp-023
  - morocco: M-ma-002…003, 005…006, 008, 011, 015, 018…020, 025, 040…041
  - spain: M-es-019…020, 038, 044
  - turkey: M-tr-018…020, 022…023, 027…030
  - uae: M-ae-014, 016…018, 020…021
- **Overrun rows graded D (6):** O-jp-006, OV-ma-003, OV-es-006…007, OV-tr-002…003.
- **Acceptance test:** for each row, either the page is opened and quoted (≤ 25 words, per `METHOD.md` evidence rule 1) and the grade moves to A/B/C, or the row stays D with "to verify".
  - `uv run python -m rail.benchmarks validate` exits 0.
  - `uv run python -m rail.benchmarks merge` and `summarise --metrics cities/ksa/benchmarks/metrics.csv --out docs/benchmarks/README.md` regenerate the README, whose D total falls accordingly.
- **Skill:** `benchmark-dossier`, `source-citation`.
- **Label:** `data`, `good first issue` (one dossier per pull request).

### GFI-022 Upgrade grade-C rows where a primary exists
- **Files:** as GFI-021, plus `docs/benchmarks/small-towns.md`.
- **Metric rows graded C (179):**
  - cautionary: M-caut-002…004, 012, 031…032
  - china: M-cn-001…047 (all 47 China rows)
  - egypt: M-eg-004…005, 009…010, 014, 025
  - germany: M-de-030, 033…036
  - italy: M-it-029…030, 033…039, 041
  - japan: M-jp-004, 011, 019, 022, 032…033
  - morocco: M-ma-004, 007, 009…010, 017, 021…024, 026…039
  - population_growth_peers: M-pop-004…011
  - south_korea: M-kr-003…017, 021…028
  - spain: M-es-002…004, 009, 018, 025, 060
  - turkey: M-tr-024…025, 031
  - uae: M-ae-002…013, 015, 019, 022…027, 029…043
- **Overrun rows graded C (28):** cn-O01; OV-eg-001…003; de-O08, de-O10; O-jp-003, O-jp-005; OV-ma-001…002, 004…009; OV-kr-001…007; OV-es-016; OV-caut-001, 003, 012, 013.
- **Small-towns dossier:** no metrics CSV. It grades its literature in prose: 3 grade B, 4 grade C (lines 33, 40, 53, 69).
- **Acceptance test:** as GFI-021. Both rows are kept when a primary conflicts with the secondary (evidence rule 6).
- **Skill:** `benchmark-dossier`, `source-citation`.
- **Label:** `data`.

### GFI-023 The 174 "no reliable data found" entries
- **Files:** `docs/benchmarks/README.md` (coverage table) and the per-dossier gap lists.
- **Entries per dossier (174 in total):** france 5, japan 9, spain 10, germany 5, china 9, south_korea 22, italy 17, morocco 16, turkey 16, uae 14, egypt 15, cautionary 15, population_growth_peers 21.
- **Primary audit documents not reached** (`docs/benchmarks/synthesis.md` §10): Cour des comptes 2014, Korea's BAI, Morocco's audit court on the final Al Boraq cost, and the California High-Speed Rail Authority plans.
- **Acceptance test:** each gap filled adds a metric row with grade and source id. The README count for that dossier falls after `rail.benchmarks summarise`. An entry still unfilled keeps its dated "searched:" note.
- **Skill:** `benchmark-dossier`.
- **Label:** `data`.

---

## D. Register towns with `pop_type: grid` (`cities/ksa/candidates.parquet`)

The register has 1,224 rows, by `pop_type`:

| pop_type | rows |
|---|---|
| grid | 906 |
| official | 224 |
| derived | 51 |
| null | 43 |

Grid rows (WorldPop 2020, `unverified`) are record-only and never used for ranking unless corroborated (A-screen-031…039). 819 grid rows are `grid_scaled` to the region residual (A-screen-040). One grid row carries `tag_10k`: Udhailiyah, `eastern:node:8357686563`, corroborated `gastat2010_city_growth`.

Grid rows per region:

| region | grid | grid ≥ 5,000 | grid ≥ 10,000 |
|---|---|---|---|
| al_baha | 8 | 0 | 0 |
| al_jouf | 52 | 7 | 1 |
| asir | 17 | 14 | 3 |
| eastern | 11 | 9 | 5 |
| hail | 5 | 5 | 0 |
| jazan | 20 | 19 | 1 |
| madinah | 9 | 5 | 1 |
| makkah | 41 | 22 | 6 |
| najran | 5 | 5 | 1 |
| northern_borders | 27 | 2 | 1 |
| qassim | 10 | 5 | 3 |
| riyadh | 656 | 4 | 2 |
| tabuk | 45 | 2 | 0 |
| **total** | **906** | **99** | **24** |

The full list of 906 rows is too long to print here. Produce it with the command in "How these counts were produced" (filter `pop_type == "grid"`).

### GFI-024 Corroborate the 24 grid-only towns at or above 10,000
- **Files:** `cities/ksa/candidates.parquet`, `cities/ksa/regions/<region>.parquet`, `docs/regions/<region>.md`, `docs/geo-verify.md`.
- **Rows** (region: name, `row_key`, grid population as in the `population` column):
  - al_jouf: Al `Isawiyah (`al_jouf:node:1236744674`, 12,422)
  - asir: Masloom (`asir:node:10956429893`, 12,376); Al Harayr (`asir:node:11870047759`, 10,260); King Faisal Military City (`asir:node:295925327`, 10,017)
  - eastern: Al `Aziziyah (`eastern:node:1236774102`, 12,771); Ar Rabi`iyah (`eastern:node:1237806646`, 12,501); Sanabis (`eastern:node:1237807066`, 12,145); Udhailiyah (`eastern:node:8357686563`, 11,999); As Sabat (`eastern:node:11871768364`, 11,032)
  - jazan: Al Jawah (`jazan:node:4946646307`, 21,104)
  - madinah: Sidi Hamzah (`madinah:node:1236691920`, 24,463)
  - makkah: Ash Sharai (`makkah:node:1236463853`, 83,726); Al Juranah (`makkah:node:1236463867`, 27,840); Bahrat al Qadimah (`makkah:node:1237963674`, 14,578); Shara'i` al Mujahidin (`makkah:node:1236463835`, 12,644); As Sifyani (`makkah:node:11871539787`, 11,462); Al Hamra (`makkah:node:1236462316`, 10,659)
  - najran: Aba Al Saud (`najran:node:6774270978`, 10,658)
  - northern_borders: Linah (`northern_borders:node:1236407820`, 11,117)
  - qassim: القبعيه (`qassim:node:6780012317`, 18,394); Ash Shihiyah (`qassim:node:1237555828`, 15,764); Dulay` Rashid (`qassim:node:747667494`, 11,022)
  - riyadh: Al-Saih (`riyadh:node:8274824536`, 87,243); Mugharrizat (`riyadh:node:1236703905`, 12,094)
- **Gap:** a grid value, not a GASTAT figure. Several may be neighbourhoods of a larger GASTAT city (for example Ash Sharai in Makkah, which `docs/STATUS.md` notes is "not in the primary city table").
- **Acceptance test:** `pop_corroboration` is set from a cited source, or the row's `notes` record why it is a part of a GASTAT city. The region note in `docs/regions/` is updated. `make test` passes. The funnel re-run is an owner step.
- **Skill:** `geo-verify`, `region-sweep`, `source-citation`.
- **Label:** `data`, `good first issue` (one town per pull request).

### GFI-025 The remaining grid-only rows (906 in total)
- **Files:** as GFI-024.
- **Gap:** 906 rows carry only a WorldPop grid population (counts per region in the table above). 99 are at or above 5,000.
- **Acceptance test:** as GFI-024, one region at a time. The per-region grid count falls only where a source corroborates or replaces the value.
- **Skill:** `region-sweep`, `geo-verify`.
- **Label:** `data`.

### GFI-026 The 43 register rows with no population
- **Files:** `cities/ksa/candidates.parquet` (`pop_type` null). 10 of them have `screened = True`.
- **Rows by region:**
  - al_baha (1): Al Qara (`al_baha:name:Al Qara@20.477,41.333`)
  - eastern (6): Al-Udayd (`eastern:osm:11871306304`); Al Ahsa (`eastern:node:8487320543`); Al Mubarraz (`eastern:node:1236714096`); Al-Bayda (`eastern:osm:1236739581`); Ras Tanura (`eastern:osm:1237805652`); النقيرة (`eastern:node:13971401177`)
  - jazan (2): Faifa (`jazan:node:1237961319`); Al Harth (`jazan:name:Al Harth@16.784,43.153`)
  - madinah (1): Wadi al-Fara' (governorate seat not identified)
  - makkah (3): Al-Ardiyat (`makkah:relation:12429530`); سلم الزواهر (`makkah:node:8868353298`); Turabah (`makkah:node:1236453863`)
  - northern_borders (23): Abu Sawr; Ad Duwayd; Al Hadaqah; Al Judayyidah; Al Lumayma'; Al `Ajrumiyah; As Saddah; Ibn Suqi; Umm Khunsur; Umm Radamah; Umm ad Diyan; Zahwah; jdedt arar; ragwah; ابن بشيت; ابن عجل; اللميماء; حدق الجندة; قليب غنيم; مركز الصحن; نواظر; هجرة ابن بكر; هجرة ابن عايش
  - qassim (6): Ad Dilaymiyah; Adh Dhibiyah; Al Fuwayliq; KHUSAIBAH; Wadi Al nakhil; Ḍariyah
  - tabuk (1): قرية الجديد
- **Gap:** most carry an exclusion reason. The most common, 22 rows, is "no sourced or grid population; no sourced economic role". Several are duplicates by design (for example Al Ahsa and Al Mubarraz, see A-eastern-003). The Wadi al-Fara' governorate seat is not identified (`docs/coverage.md` line 56).
- **Acceptance test:** a population with source and `pop_source_status`, or a confirmed exclusion reason. For Wadi al-Fara', a cited seat. `make test` passes.
- **Skill:** `region-sweep`, `geo-verify`, `source-citation`.
- **Label:** `data`.

### GFI-027 Economic roles of the created register rows
- **Files:** `screening/created_roles_r4.yaml`, `docs/STATUS.md` ("Created rows lack roles"; R3 hand-offs).
- **Gap:** `docs/STATUS.md` records that R4 assigned roles to the 24 created rows: "5 scored, 16 low-confidence unscored, 6 none". CP5 H6a keeps the low-confidence oasis-agriculture roles unscored. The role sources include CC BY-SA pages (licence blocker B3, GFI-047).
- **Acceptance test:** a role gains a primary source and a confidence change, recorded in the YAML with an source id. Scoring it is an owner decision (H6a).
- **Skill:** `region-sweep`, `source-citation`.
- **Label:** `data`, `needs-owner-decision` (for scoring).

---

## E. Deferred simulation checks

### GFI-028 Optional SUMO rail headway and capacity check (deferred at R4)
- **Files:** `docs/jeddah-coupling.md` §6, `docs/status/r4.md` line 60 ("Task 5, SUMO rail: deferred, method written"), `docs/STATUS.md` R4 open items ("Not done in R4: SUMO rail headway check"), `PROJECT.md` section 3 ("Optionally add SUMO rail for headway and capacity checks").
- **Gap:** never run. The written method:
  1. Build a synthetic double-track SUMO line at a trunk corridor's km-posts, with rail vClass and block signals.
  2. Run trains at the headway in `access_network.yaml` with the kinematics in `running_time_classes.yaml`.
  3. Measure the minimum stable headway and trains per hour per direction, and compare them with the service plan.
- **Acceptance test:**
  - A CLI with `--seed`, a `meta.json` (seed, config hash, data hash, code version) and a test on `tests/fixtures/`.
  - The result is written to `docs/` with the label "synthetic demand, uncalibrated: scenario comparison, not a forecast".
  - SUMO's version is added to `docs/licences.csv`.
  - `make test` passes. The national run is not part of CI.
- **Skill:** `line-yaml`, `isochrone-commute`, `licence-register`.
- **Label:** `needs-owner-decision` (optional scope in the brief). After a go-ahead, it is a contributor task.

### GFI-029 30 m alignment pass for a short list (deferred)
- **Files:** `docs/alignments.md` §7 (line 327: "90 m for every corridor; no 30 m pass"), `docs/assumptions.md` A-align-001.
- **Gap:** every corridor is routed at 3 arc-seconds (about 90 m). The 30 m pass was deferred to R6, and no R6 status file records it as run.
- **Acceptance test:** an owner decision on the short list. Then a run with `meta.json`, A-align-001 updated, and the alignment limitation label kept.
- **Skill:** `osm-ksa-rail-network`.
- **Label:** `needs-owner-decision`.

### GFI-030 Alignment items carried from R4_ALIGN
- **Files:** `docs/STATUS.md` (R4 / R4_ALIGN open items, "CP5 additions"), `docs/alignments.md`, `docs/assumptions.md` A-align-045, A-align-091.
- **Gap** (as written in `docs/STATUS.md`; confirm against the current `docs/alignments.md` before starting):
  - the mean-offset target was met on 0 of 3 validation lines;
  - viaduct km is a lower bound (HHR 6.8 vs 44.1 km OSM-tagged);
  - earthworks are measured but not priced (A-align-045: "no register item");
  - the S4 Abha belt 315 is grade-infeasible at 2.5 % (A-align-091);
  - there is no open source for restricted zones beyond OSM military areas.
- **Acceptance test:** each item either closed with evidence in `docs/alignments.md`, or kept with a dated reason. Pricing earthworks needs a cost-register row with a source.
- **Skill:** `osm-ksa-rail-network`, `cost-register`.
- **Label:** `data` (earthworks unit costs; restricted-zone sources), `needs-owner-decision` (re-routing).

### GFI-031 Jeddah coupling seeds 2–3 (decided: not run)
- **Files:** `docs/jeddah-coupling.md` §5.
- **Gap:** only seed 1 was run. Seeds 2–3 need population caches written inside the read-only TrafficTwin checkout. CP5 decision H7c: "the Jeddah coupling stays at one seed; the TrafficTwin read-only rule stays in full".
- **Acceptance test:** none for contributors. This is listed so the gap stays visible. Reopening it is the owner's decision.
- **Skill:** none.
- **Label:** `needs-owner-decision`.

---

## F. Dashboard polish (`web/`, `api/`)

### GFI-032 Difference mode: S1 per-line values cover only some lines
- **Files:** `web/src/views/DifferenceView.tsx` (line 107 prints the covered and uncovered lines), `api/data.py`, `docs/status/verify-R8.md` item 9 ("difference mode has S1 per-line values for three lines only"; kept as a declared limitation).
- **Gap:** the per-line S1 comparison is partial because the run files hold per-line values for a subset of lines.
- **Acceptance test:**
  - Every line in the selected programme has an S1 value, or the view lists the gap (as now).
  - `cd web && npm run typecheck && npm run build` pass, and `uv run pytest tests -k api` passes.
  - Computing new per-line values is an owner run.
- **Skill:** `scenario-yaml`.
- **Label:** `needs-owner-decision` (new run), `good first issue` (presentation only).

### GFI-033 `alignment_km` is served by the API but not displayed
- **Files:** `api/`, `web/src/`, `docs/status/main.md` (FIX_HHR_JEDDAH dependency table: "`alignment_km` 484.59 → 455.23 is served but not displayed").
- **Acceptance test:** the value appears in the line tooltip or panel with the alignment-limitation label (`common.labels.ALIGNMENT_LIMITATION`, never retyped). `npm run typecheck`, `npm run build` and the API tests pass. `npm run screenshot` re-shoots the affected view.
- **Skill:** `line-yaml`.
- **Label:** `good first issue`.

### GFI-034 CI does not type-check or build the dashboard
- **Files:** `.github/workflows/ci.yml` (no `npm` step), `web/package.json`, `docs/status/verify-INTEGRATE_R8.md` (line 28: `tsc` "not runnable on main" without `npm install`).
- **Acceptance test:** a CI job runs `cd web && npm ci && npm run typecheck && npm run build` and the same commands pass on a clean clone. No API keys are needed: the basemap is keyless.
- **Skill:** none specific.
- **Label:** `good first issue`.

### GFI-035 Arabic interface for the dashboard
- **Files:** `web/src/` (Arabic appears only in place names: `RegisterView.tsx` line 117 and `MapView.tsx` lines 139, 144), `docs/glossary.ar.md`.
- **Gap:** all interface strings, labels and the footer are English.
- **Acceptance test:** an owner decision on scope. Then the strings use the glossary forms, the RTL order is measured with `uv run python -m common.ar_render bidi-probe`, and the build passes. Native-speaker review is required before release.
- **Skill:** none specific.
- **Label:** `needs-owner-decision`.

Not issues (by design): S6-L4, S6-L5 and S6-L6 are kept out of the scenario switcher and appear only in the Pareto explorer with their captions (`web/README.md`). The RJ routes study is deliberately not in the dashboard (`docs/status/main.md`).

---

## G. Other open items from `docs/STATUS.md` "Open issues"

### GFI-036 `make test` hides the pytest summary line (doubled `-q`)
- **Files:** `Makefile` `pytest` target (`uv run pytest -q`), `pyproject.toml` line 50 (`addopts = "-q"`). This is verify-R5 observation O18, still open.
- **Acceptance test:** `make test` prints the pytest summary line (`N passed`).
- **Skill:** none.
- **Label:** `good first issue`.

### GFI-037 Opening years printed with thousands separators in `docs/cba.md`
- **Files:** `docs/cba.md` (74 table lines carry year triples such as `2,034 / 2,037 / 2,045`), the renderer behind `uv run python -m economics.cba report`. This is verify-R5 observation O6, still open.
- **Acceptance test:** the regenerated `docs/cba.md` contains no line matching `\| 2,0[2-9][0-9] / 2,0[2-9][0-9]`. No other number changes (`git diff --stat` shows only the year cells). `make test` passes.
- **Skill:** `cba-appraisal`.
- **Label:** `good first issue`.

### GFI-038 Remaining verify-R5 observations (O3, O5, O8)
- **Files:** `docs/STATUS.md` (R5 open items), `docs/cba.md`, `tests/fixtures/`.
- **Gap** (as carried in `docs/STATUS.md`; not re-checked for this list):
  - O3: TAG A3/A4.2 were not read although their values are used.
  - O5: the fixture CBA case is not runnable through `economics.cba run` (no cost run).
  - O8: some method rows have no range.
- **Acceptance test:**
  - O3: the TAG units cited with source ids.
  - O5: `uv run python -m economics.cba run` succeeds on the fixture case in seconds, with a pytest test.
  - O8: every method row has a range or "n/a" with a reason.
- **Skill:** `cba-appraisal`, `source-citation`.
- **Label:** `good first issue` (O5), `data` (O3).

### GFI-039 Funding and legal facts that could not be verified (R7)
- **Files:** `cities/ksa/funding/recommendations.yaml` (`legal_items`: 16 items, 13 `unclear`), `docs/status/r7.md` (line 45, "Could not verify"), `docs/funding.md`, `docs/fiscal-exposure.md`.
- **Unclear items:** sar_ownership_form, fiscal_reporting, pif_role, fare_setting_authority, railway_law_regulation, psp_regulations_thresholds, psp_relevant_agency, psp_railway_interaction, ncp_vfm_method, om_contract_status, host_line_procurement, lvc_instruments, land_expropriation. Each has its question in the YAML.
- **Not found:** no Saudi PPP cost of capital, MRG, termination or transaction-cost data (UK and LGV SEA reference classes are used and flagged); the PSP Implementing Regulations text.
- **Acceptance test:** an item moves to `clear` only with a published legal or official text cited by source id. Do not ask any agency; published texts only. `make test` passes.
- **Skill:** `ppp-structuring`, `source-citation`.
- **Label:** `data`.

### GFI-040 Search dimensions not covered by the frozen judge (R6_V3)
- **Files:** `docs/STATUS.md` (R6_V3 open items), `docs/r6-topology.md`, A-r6-101…103.
- **Gap:**
  - single vs double track has no term in the frozen cost or demand model (A-r6-102);
  - two or more station drops together were not enumerated (A-r6-101);
  - stage-2 combinations had no candidate (A-r6-103);
  - the 9 station additions have no variant field.
- **Acceptance test:** none for contributors. A new judge version is an owner decision.
- **Skill:** `pareto-optimizer`.
- **Label:** `needs-owner-decision`.

### GFI-041 Run-meta provenance notes
- **Files:** `docs/STATUS.md` (R6 open items: "31 of 111 judge-run metas carry a `-dirty` harness version"; "r1a non-geo run metas … still predate" the merged manifest).
- **Gap:** `runs/` is gitignored and not in the repository, so only the owner can refresh these.
- **Acceptance test:** at the next owner re-run, the new `meta.json` files carry a clean code version and the current manifest hash.
- **Skill:** none.
- **Label:** `needs-owner-decision`.

### GFI-042 Tidy stale lines in `docs/STATUS.md` "Open issues"
- **Files:** `docs/STATUS.md`.
- **Gap:** some non-struck lines are closed by later decisions:
  - "Five zero-spread cost defaults (R1c → R4)" is cleared by CP5 H10a and R5 ("ten zero-spread rows cleared before any BCR").
  - "Two S5 station additions 10.4 km apart" is decided by CP6 P6a (one shared station, in the model).
  - The "R1d licence flags" are now blockers B1, B2, B3 and the xlogit row in `docs/licences-blockers.md`.
- **Acceptance test:** each such line is struck through with the closing reference, and no open item is removed. This file is the coordinator's, so the owner applies the change.
- **Skill:** none.
- **Label:** `docs`, `needs-owner-decision`.

### GFI-043 Implement the `common.assumptions check` CLI named in the skill
- **Files:** `.claude/skills/assumptions-register/SKILL.md` line 31 (`uv run python -m common.assumptions check`), `common/` (no `assumptions.py` exists).
- **Related observations from `docs/STATUS.md` (R0):**
  - the licence CSV header differs from the `licence-register` skill's column list;
  - S0/S1 use `kind: scenario` rather than the skill's kinds.
- **Acceptance test:** `uv run python -m common.assumptions check` lists YAML parameters that lack `source:`/`assumption:` or a register row, and has a pytest test on `tests/fixtures/`. The change to `common/` is additive only. `make test` passes.
- **Skill:** `assumptions-register`.
- **Label:** `good first issue`.

### GFI-044 Native-speaker review of the Arabic executive summary
- **Files:** `docs/executive-summary.ar.md`, `docs/glossary.ar.md`.
- **Gap:** `docs/STATUS.md` (R8 open items): "draft, pending native-speaker review by Tariq; not for use outside the repository until signed off".
- **Acceptance test:** owner sign-off recorded in `docs/STATUS.md`. `uv run python -m common.sources bilingual-check` passes after any edit.
- **Skill:** none.
- **Label:** `needs-owner-decision`.

---

## H. Licence release blockers (owner decisions, not contributor tasks)

`docs/licences-blockers.md` (v1.3, 7 Nov 2026) lists **2 BLOCKER rows** out of a 290-row register: #94 Coqui XTTS-v2 and #189 Transit Costs Project (hard stop). Tariq's 7 Nov 2026 AST decisions (FIX_LICENCE_CITE_FACTS), the named-flag rule change (FIX_LICENCE_NAMED_FLAGS) and the citation-only licence cells of #191 MoF FY2026 (B1) and #193 IMF/World Bank PFRAM (B2) (FIX_LICENCE_CITE_TERMS) cleared the rest. The group table and row lists below are the R9 snapshot of v1.1 (46 BLOCKER rows), kept for history; use `docs/licences-blockers.md` for the current list:

| group | rows |
|---|---|
| press and secondary fact pages | 21 |
| statistical extracts with unclear terms | 9 |
| non-commercial or all-rights-reserved databases | 2 |
| CC BY-SA share-alike | 6 |
| ODbL derivative question | 2 |
| models and voices | 3 |
| fonts and media | 0 |
| other | 3 |

Of these, 12 rows carry a B-number (B1–B9), 1 is the Transit Costs hard stop, and 33 carry no B-number. Every item below is **`needs-owner-decision`**: rule 12 says the owner decides each row. A contributor may help only by reading and quoting published terms (with an source id). Contributors must never write to a rights holder. In every case, the acceptance test is the owner's decision recorded in `docs/licences.csv`, followed by `uv run python -m common.licence_blockers write` and `uv run python -m common.licences check` with 0 differences.

| id | blocker | register row(s) | question that clears it (from `docs/licences-release.md` §1) | skill |
|---|---|---|---|---|
| GFI-045 | B1 MoF FY2026 budget table | #191 | may the table be republished, or cited only? | `licence-register` |
| GFI-046 | B2 IMF/World Bank PFRAM conventions | #193 | is citing the concepts enough? | `licence-register` |
| GFI-047 | B3 UNESCO CC BY-SA | #133, #147, #197, #238 | commit a derived heritage layer under CC BY-SA, or keep UNESCO to cited facts? | `licence-register` |
| GFI-048 | B4 IMF WEO terms | #262 | may the series be reused in a public, possibly commercial, release? | `licence-register` |
| GFI-049 | B5 CE Delft handbook | #260 | confirm the reuse notice (Commission Decision 2011/833/EU) on the document | `licence-register`, `source-citation` |
| GFI-050 | B6 Wikipedia air-route set | #236 | is a list of airport pairs a fact list, or a CC BY-SA database extract? | `licence-register` |
| GFI-051 | B7 ODbL on the alignment sidecars | #246, and #290 (`alignments-v2/`, same question) | Produced Work or Derivative Database? | `licence-register` |
| GFI-052 | B8 orchestrator row name | #1 | rename the row for the public register; keep the identifiers in the private files only | `licence-register` |
| GFI-053 | B9 Nabrah AI attribution | #153 | what attribution, if any, must accompany published audio? Publication of the public voices on a paid plan is cleared; attribution is unanswered. The owner asks the vendor; contributors do not. | `licence-register` |

### GFI-054 The 32 other BLOCKER rows without a B-number
- **Files:** `docs/licences-blockers.md`.
- **Rows:** 33 rows carry no B-number. Row #290 belongs with B7 (GFI-051) and #189 is the Transit Costs hard stop, which leaves 32:
  - **Press and secondary fact pages (21):** #117 SAR network page; #118 HHR booking site; #119 RCRC; #120 Makkah Region Emirate (Al-Jumum); #121 MEED; #122 ENR; #123 trade and business press; #127 and #132 Saudipedia; #136 Asharq Al-Awsat; #141 and #148 search snippets; #149 datasaudi.sa; #168 economic-node facts; #188 trade press and company releases; #204 Wayback HHR schedule; #221 SAPTCO Annual Report 2025; #234 GACA Hajj release; #235 SPA HHR seats; #237 running-time press; #263 Saudi Global Ports tariff notice.
  - **Statistical extracts (6 without a B-number):** #7 data.gov.sa; #125 GLMM; #183 DfT TAG optimism-bias workbook; #194 and #195 GASTAT labour-market tables; #196 CRU TS climatology.
  - **Other rows (5):** #146 Wikivoyage/CruiseMapper; #203 EPSG dataset terms (epsg.org returned 403); #94 Coqui XTTS-v2 (non-commercial: keep out of any release); #201 xlogit (MIT vs GPL conflict: do not use until settled); #205 Schittenhelm (2011).
- **Gap:** for most fact rows the one question is "is citing a published fact with its source enough, and is anything beyond the fact reproduced?"
- **Acceptance test:** as for the table above.
- **Skill:** `licence-register`, `source-citation`.
- **Label:** `needs-owner-decision`.

**Do not use: Transit Costs Project** (register row #189). This is a hard stop, not an issue. No figure, table or benchmark may draw on it. `docs/licences-blockers.md` records that nothing in the repository does.

---

## How these counts were produced

Run from the repository root on 7 Nov 2026 (HEAD `4b15ae2`, clean tree).

```bash
# A. data-sources.md: last cell of each table row containing "not found"/"none found" (9) or "unverified" (21)
uv run python - <<'EOF'
import re
n={'not found':0,'unverified':0}
for line in open('docs/data-sources.md',encoding='utf-8'):
    if not line.startswith('|') or set(line.strip())<=set('|-: '): continue
    c=[x.strip() for x in line.strip().strip('|').split('|')]
    if c[0] in ('section 4 item','Source','W1 dataset'): continue
    s=c[-1].lower()
    if 'not found' in s or 'none found' in s: n['not found']+=1
    elif 'unverified' in s: n['unverified']+=1
print(n)
EOF

# B. assumptions: split on unescaped "|", status = second-to-last cell; 765 rows, 650 awaiting
uv run python - <<'EOF'
import re,collections
K=['assumed','assumption','sourced','derived','tuned','open','proposed','decided','calibrated','unverified',
   'secondary','verified','approved','accepted','adopted','merged','applied','rule applied','cross-check']
ALIAS={'assumption':'assumed','rule applied':'applied','cross-check':'cross-check only'}
def norm(s):
    t=s.lower()
    if 'superseded' in t: return 'superseded'
    return next((ALIAS.get(k,k) for k in K if t.startswith(k)),'other')
for path in ['docs/assumptions.md','docs/study-rj/assumptions.md']:
    rows=[[c.strip() for c in re.split(r'(?<!\\)\|',l.strip())[1:-1]]
          for l in open(path,encoding='utf-8') if l.startswith('| A-')]
    st=collections.Counter(norm(r[-2]) for r in rows)
    print(path,len(rows),st.most_common())
    print('awaiting:',sum(v for k,v in st.items() if k in ('assumed','open','proposed','unverified','secondary')))
    print('rows with != 8 cells:',[(r[0],len(r)) for r in rows if len(r)!=8])
    # workstream totals (GFI-013…019): id prefix → group
    G={'appraisal':'cba','demand':'demand mode access r4-acc r4-air r4-bus r4-rt r4-cpl intl pop',
       'costs':'cost rcf r4-cost hhr','network':'align stn r1a geo data','screening':'screen corr r2 r6',
       'pilot':'screen-pilot screen-pilot-terrain','fund_social':'fund social bench film','study_rj':'rj'}
    inv={p:g for g,ps in G.items() for p in ps.split()}
    aw=[r[0] for r in rows if norm(r[-2]) in ('assumed','open','proposed','unverified','secondary')]
    print(collections.Counter(inv.get(re.match(r'A-(.+)-\d+[a-z]?$',i.split(' ')[0]).group(1),'regions') for i in aw))
EOF

# C. benchmarks: grades
uv run python -c "import pandas as pd;m=pd.read_csv('cities/ksa/benchmarks/metrics.csv');o=pd.read_csv('cities/ksa/benchmarks/overruns.csv');print(m.grade.value_counts().to_dict(),o.grade.value_counts().to_dict());print(m[m.grade.isin(['C','D'])].groupby(['slug','grade']).row_id.apply(list))"
grep -o -E "Grade [A-D]\b" docs/benchmarks/small-towns.md | sort | uniq -c

# D. register populations
uv run python -c "import pandas as pd;d=pd.read_parquet('cities/ksa/candidates.parquet');g=d[d.pop_type=='grid'];print(d.pop_type.value_counts(dropna=False).to_dict());print(g.groupby('region').size());print((g.population>=5000).sum(),(g.population>=10000).sum());print(g[['region','name_en','name_ar','row_key','population']].sort_values(['region','population']).to_string())"
uv run python -c "import pandas as pd;d=pd.read_parquet('cities/ksa/candidates.parquet');print(d.terrain_class.isna().sum(),d.terrain_class.value_counts().to_dict())"

# Stations: 153 features, 13 with located == false
uv run python -c "import json;f=json.load(open('cities/ksa/lines/stations.geojson'))['features'];print(len(f),[(p['layer'],p['station_id']) for p in (x['properties'] for x in f) if not p.get('located')])"

# E–G. deferrals and open items
grep -n -i "sumo" docs/STATUS.md docs/status/r4.md docs/jeddah-coupling.md
grep -c -E "\| 2,0[2-9][0-9] / 2,0[2-9][0-9]" docs/cba.md            # 74
grep -n "pytest" Makefile; grep -n addopts pyproject.toml
uv run python -c "import yaml;d=yaml.safe_load(open('cities/ksa/funding/recommendations.yaml'));print([(k,v['status']) for k,v in d['legal_items'].items()])"
grep -n -i "npm\|web" .github/workflows/ci.yml                        # no output

# H. licence blockers: 2 rows (46 at R9), none with a B-number
grep -c "^| [0-9]" docs/licences-blockers.md
grep "^| [0-9]" docs/licences-blockers.md | awk -F'|' '{print $4}' | sort | uniq -c
```

## Summary table

| id | title | label | skill |
|---|---|---|---|
| GFI-001 | Refresh stale statuses in data-sources.md | docs, good first issue | source-citation |
| GFI-002 | GASTAT locality table (< 5,000) | data | source-citation, region-sweep |
| GFI-003 | Population projection and regional estimates | data | source-citation, assumptions-register |
| GFI-004 | Regional economic tables | data | source-citation, licence-register |
| GFI-005 | Air OD, road counts, intercity bus | data | source-citation, licence-register, gravity-calibration |
| GFI-006 | Official dated HHR timetable, fares, distances | data | source-citation, line-yaml |
| GFI-007 | Planned-line facts and 13 unlocated stations | data | line-yaml, source-citation, geo-verify |
| GFI-008 | Replace secondary aggregator rows | data, good first issue | source-citation |
| GFI-009 | Repair five malformed register rows | docs, good first issue | assumptions-register |
| GFI-010 | Retire 11 region terrain rows (R3 DEM) | docs, good first issue | assumptions-register |
| GFI-011 | Confirm or retire 53 pilot-era rows | docs | assumptions-register |
| GFI-012 | Open and proposed rows (owner) | needs-owner-decision | assumptions-register |
| GFI-013 | Region-sweep assumptions (70) | data | region-sweep, geo-verify, assumptions-register |
| GFI-014 | Appraisal assumptions (80) | data | cba-appraisal, assumptions-register |
| GFI-015 | Demand, mode, access assumptions (147) | data | gravity-calibration, isochrone-commute, assumptions-register |
| GFI-016 | Cost and reference-class assumptions (55) | data | cost-register, reference-class-forecasting |
| GFI-017 | Network, alignment, geo assumptions (103) | data | osm-ksa-rail-network, geo-verify, line-yaml |
| GFI-018 | Screening, corridor, optimisation assumptions (72) | docs | screening-funnel, corridor-generator, pareto-optimizer |
| GFI-019 | Funding, social, benchmark, film assumptions (70) | data | ppp-structuring, survey-design, benchmark-dossier |
| GFI-020 | Study-RJ assumptions (8) | data | assumptions-register |
| GFI-021 | Verify or drop 44 grade-D benchmark rows | data, good first issue | benchmark-dossier, source-citation |
| GFI-022 | Upgrade 207 grade-C rows (+ 4 prose grades) | data | benchmark-dossier, source-citation |
| GFI-023 | 174 "no reliable data found" entries | data | benchmark-dossier |
| GFI-024 | Corroborate 24 grid-only towns ≥ 10,000 | data, good first issue | geo-verify, region-sweep, source-citation |
| GFI-025 | Remaining grid-only rows (906) | data | region-sweep, geo-verify |
| GFI-026 | 43 register rows with no population | data | region-sweep, geo-verify, source-citation |
| GFI-027 | Roles of the created register rows | data, needs-owner-decision | region-sweep, source-citation |
| GFI-028 | Optional SUMO rail headway and capacity check | needs-owner-decision | line-yaml, isochrone-commute, licence-register |
| GFI-029 | 30 m alignment pass | needs-owner-decision | osm-ksa-rail-network |
| GFI-030 | Alignment items carried from R4_ALIGN | data, needs-owner-decision | osm-ksa-rail-network, cost-register |
| GFI-031 | Jeddah coupling seeds 2–3 (decided: not run) | needs-owner-decision | none |
| GFI-032 | Difference mode S1 per-line coverage | needs-owner-decision, good first issue | scenario-yaml |
| GFI-033 | Display `alignment_km` | good first issue | line-yaml |
| GFI-034 | CI build and type-check of `web/` | good first issue | none |
| GFI-035 | Arabic dashboard interface | needs-owner-decision | none |
| GFI-036 | Doubled `-q` hides pytest summary | good first issue | none |
| GFI-037 | Opening-year separators in cba.md (74 lines) | good first issue | cba-appraisal |
| GFI-038 | Remaining verify-R5 observations O3, O5, O8 | good first issue, data | cba-appraisal, source-citation |
| GFI-039 | R7 legal and funding facts (13 unclear) | data | ppp-structuring, source-citation |
| GFI-040 | Search dimensions outside the frozen judge | needs-owner-decision | pareto-optimizer |
| GFI-041 | Run-meta provenance | needs-owner-decision | none |
| GFI-042 | Tidy stale STATUS.md open-issue lines | docs, needs-owner-decision | none |
| GFI-043 | `common.assumptions check` CLI | good first issue | assumptions-register |
| GFI-044 | Native-speaker review, Arabic summary | needs-owner-decision | none |
| GFI-045 | B1 MoF FY2026 budget table | needs-owner-decision | licence-register |
| GFI-046 | B2 PFRAM conventions | needs-owner-decision | licence-register |
| GFI-047 | B3 UNESCO CC BY-SA | needs-owner-decision | licence-register |
| GFI-048 | B4 IMF WEO terms | needs-owner-decision | licence-register |
| GFI-049 | B5 CE Delft handbook | needs-owner-decision | licence-register, source-citation |
| GFI-050 | B6 Wikipedia air-route set | needs-owner-decision | licence-register |
| GFI-051 | B7 ODbL alignment sidecars | needs-owner-decision | licence-register |
| GFI-052 | B8 orchestrator row name | needs-owner-decision | licence-register |
| GFI-053 | B9 Nabrah AI attribution | needs-owner-decision | licence-register |
| GFI-054 | 32 other BLOCKER rows | needs-owner-decision | licence-register, source-citation |
