> **Document version:** docs/status/main.md v1.40 | 12 Nov 2026 | Author: R0 builder; PUBLISH_EXPORT block (v1.40); PUBLISH_PREP_URL block (v1.39); PUBLISH_PREP block (v1.38); FIX_TRAILER_AR block (v1.37); FIX_LICENCE_CITE_TERMS block (v1.35; v1.36 verifier pass 2 result and close line); FIX_LICENCE_NAMED_FLAGS block (v1.33; v1.34 verifier result and close line); FIX_LICENCE_CITE_FACTS block (v1.32); FIX_R9_COUNTS block and R9-block count corrections (v1.30; v1.31 verifier result and status line); R9 block (v1.28; v1.29 verifier PASS, observations, status line); STUDY_RJ_SCORE block (v1.27); STUDY_RJ_FAMILIES block (v1.26); S6_L6_SCORE block (v1.24 start; v1.25 result, verifier, status line); S6_L6_CONNECTED block (v1.22; v1.23 verifier PASS and status line); FIX_HHR_REROUTE block (v1.21); FIX_HHR_JEDDAH block (v1.18; v1.19 corridor-bonus row, verdicts, follow-ups after VERIFY_FIX_HHR_JEDDAH; v1.20 verifier result and status line); FIX_R8_RTL block; FIX_R8 block; INTEGRATE_R8 block; FIX_R7 block and INTEGRATE_R7 correction; INTEGRATE_R7 block; later blocks by each main-track run | Status: active

# Track `main` — status

## R0 Skeleton and reuse audit — 30 Oct 2026
Built:
- `pyproject.toml` + `uv.lock` (ksa-railtwin, Python >=3.12,<3.13, `[tool.uv] package = false`, ruff line-length 100 with E F I UP B SIM, pytest `testpaths = ["tests"]`, `pythonpath = ["."]`); dependencies pyyaml pydantic numpy pandas pyarrow duckdb shapely pyproj geopandas networkx typer rich scipy matplotlib httpx; dev ruff pytest.
- `common/`: `manifest.py` (add/verify/hash), `cost_log.py` (add/summary/check), `runmeta.py` (`write_meta`, `config_hash`, `seed_option`, `rng`; CLI config-hash/show), `labels.py` (label + P10/P50/P90 formatter), `docver.py` (check/bump), `schemas.py` (`LineSpec`, `RegionRow`, `CostItem`, `CbaCase`, `Scenario`, `ZoneProps`, `SourceRow`, `Param`), `cli.py` (shared `--seed` + `version`).
- Package skeletons with `__init__.py`, `README.md` and `cli.py`: rail network screening costs demand modechoice access economics funding optimise coupling api.
- Fixtures (`tests/fixtures/`, all fictional): corridor line YAML (hypothetical, 3 stations), 6 zones GeoJSON, 5-town mini-region register Parquet (+ generator), 4-item cost register, 1 CBA case, stream-json sample. Tests: manifest round trip and mismatch, cost_log parsing and idempotence, runmeta determinism, docver on the repo, every fixture against its schema, every package CLI, hygiene (no payloads, no home paths, every dependency in the licence register).
- `data/osm`, `data/jeddah`, `data/traffictwin` symlinks (gitignored; `scripts/link_data.sh`); manifest rows for the GCC PBF and `jeddah.v2.net.xml`.
- `Makefile` (setup, data-links, test, cost, region-prompts, status), `.github/workflows/ci.yml`, `.gitignore`, `README.md`, `NOTICE`, `CHANGELOG.md`, `web/README.md`, `docs/assumptions.md`, `docs/cost-log.csv`, `docs/STATUS.md`.

Measured: 49 tests passed in 1.26 s; `make test` 3.3 s; docver 123 files; manifest 2 rows verified; 12/12 package CLIs; licence register 110 rows; disk free 26 GiB; cost so far USD 0.19 list (excludes this run, logged by `run_track.sh` at the end).

Decisions: see `docs/STATUS.md` (manifest `--allow-missing` for CI only; `--accessed` override; `scripts/link_data.sh`; fictional fixtures; three assumption rows).

Fixes and edits to coordinator files (only what R0 required):
- `docs/licences.md` / `.csv`: the 17 dependency rows got the locked version, the PyPI URL for that version and the licence read from PyPI's metadata (`status: verified 2026-10-30`); Python and uv rows confirmed; 26 transitive runtime dependencies added. Header bumped to v0.2. CSV kept with its CRLF line endings and its existing columns.
- `cities/ksa/sources.yaml`: two rows added by `common.manifest add` (header comments kept).
- `.gitignore`: rewritten from TrafficTwin's pattern (it is in R0's ownership list).

Observed, not changed (coordinator to decide):
- `docs/licences.csv` columns are `item,version,source_url,licence,open,commercial_use,attribution,obligations,used_in,status,approval`; the `licence-register` skill lists `attribution_required` and `notes` and no `status`. The data is complete either way.
- `scenarios/S0.yaml`/`S1.yaml` use `kind: scenario`, where the `scenario-yaml` skill lists `baseline_today`/`baseline_committed`; `common.schemas.Scenario` accepts any `kind` and both files validate.
- Skills reference CLIs that belong to later milestones (`common.licences`, `common.assumptions`, `common.scenarios`, `rail.lines`, `costs.register`, `screening.region_sweep`, `economics.cba`); not built at R0 ("no modelling code yet").
- `docs/plan.md` section 7 already lists osrm/r5py, PyMC, SUMO, pymoo/OR-Tools/HiGHS and the TTS/LLM stack per milestone; nothing appended.

Assumptions added: A-screen-001, A-screen-002, A-data-001.
Licences added: 26 transitive Python runtime dependencies; 17 direct dependency rows verified.
Could not verify: CI on GitHub (not pushed, by rule 7); reproduced locally from a clean clone instead.
Next: R1 (R1a data and network, R1b benchmarks, R1c cost register, R1d funding and social), after the DATASCOUT_1H pass and the national pilot for CP1.

Verifier: `red-team-verifier` on claude-fable-5-1, VERDICT: PASS (8/8 acceptance criteria; spot-check 17/17, seed 20261030), report `docs/status/verify-R0.md`. After it: added the two dev-only transitive rows it noted (`iniconfig`, `pluggy`) and refreshed the docver count in `docs/STATUS.md`; its other observations are for the coordinator (listed in `docs/STATUS.md` Open issues).

R0: done

## DATASCOUT_1H One-hour grounding verification pass — 30 Oct 2026
Start: 2026-10-30 20:52 +03 (first tool call, `date`). Time-box ends 21:52 +03.
Stop: 2026-10-30 21:04 +0300 (wall time about 14 minutes of the 60-minute box; four parallel `rail-data-scout` sub-tasks (topics: HHR/ridership, SAR/GCC/Metro, Landbridge/Al-Jumum, GASTAT) plus coordinator checks).

Built: `docs/sources/index.csv` and `index.md` (91 records S-001 to S-091), `docs/sources/conflicts.md` (C-001 to C-012), `docs/data-sources.md` v0.1 (with the "Verified in this pass" table mirroring PROJECT.md section 4), `docs/gastat-regions.md` v0.1, `docs/licences-datascout.md` and `.csv` (16 rows), `data/ksa/tables/` (2 files + README), 2 manifest rows.

Counts (index, all accessed 2026-10-30): **verified 22, secondary 54, unverified 15**. Every section 4 fact has at least one row; no fact is left without a row.

Landbridge cost conflict (C-001): **unresolved**. SR 100 bn (= USD 26.67 bn at 3.75) is the whole-programme figure attributed to SAR's CEO (MEED Jan/Feb/Aug 2026; secondary). USD 7 bn (= SR 26.25 bn, 26 % of the headline) is best read as the 2011 legacy estimate (SR 26 bn) reused by press (analysis). One outlet assigns it to the 35 km Riyadh package (USD 200 m/km; uncorroborated). ENR's page returned 403 (unverified). Hypotheses: (a) first phase: no evidence; (b) package: one secondary outlet; (c) legacy/price year: supported; (d) reporting error: possible. Hand-off to LANDBRIDGE_RECONCILE. MEED pid=114639: subscriber gate, no station list (S-061). "Jamuma" = Al-Jumum: stated by project owner, not published; site unlocated (S-062, S-063).

GASTAT governorate count: **not found within the hour** (census portal portal.saudicensus.sa did not resolve; DNS failure). 13 regions verified on GASTAT (S-070). Secondary totals 150 / 139 / 136 / 135 / 134 / 118. Working list = 150 rows (citypopulation.de crediting GASTAT) + 2 flagged = 152 rows in `docs/gastat-regions.md`.

Tables downloaded: `data/ksa/tables/gastat_railway_transport_statistics_2025_en.pdf` (242,797 bytes, GASTAT, unmodified) and `gastat_railway_key_indicators_2024_2025.csv` (1,286 bytes, derived). Census 2022 governorate/city tables: **not downloaded** (portal unreachable). The section 4 aggregator city figures could therefore not be replaced by GASTAT values; all ten exact values match the brief and stay `secondary` (S-080 to S-089).

Decisions:
- 2026-10-30: the working governorate universe is the 150-row census-2022 list (secondary), not the 136/139 Wikipedia totals. Reason: the most complete list avoids silent omissions (rule 2), and `docs/coverage.md` reconciles once the primary is read.
- 2026-10-30: the GASTAT Railway Transport Statistics 2025 publication (verified) is the primary ridership source. The 2023 figures of the brief stay secondary/unverified because the 2023 PDF returns 404.
- 2026-10-30: the SAR/USD conversion uses the existing assumption A-cost-001 (peg 3.75). No new assumption rows were needed; `docs/assumptions-datascout.md` was not created.
- 2026-10-30: quotes were captured via a page-extraction tool and are flagged in `index.md` for byte-checking before report or film use.

Needs Opus judgement:
1. Governorate count and list: read the Law of Provinces and amendments (boe.gov.sa) or GASTAT's admin table from another route; resolve Abanat and Al-Bayda (C-010).
2. Makkah/Madinah census region totals that look swapped in citypopulation.de (C-011); census date 9 vs 10 May 2022 (C-012).
3. HHR topology: KAIA on a branch vs the brief's main-line 0/77/17/94/261 km; design speed 300 vs 320/360 km/h (C-004).
4. Riyadh Metro opening dates: the brief swaps Lines 3 and 5 (C-005); cost USD 25 bn vs 22.5 bn vs USD 166 m/km.
5. SAR East: the brief lists Al-Kharj as a passenger stop, but SAR lists it on freight only; SAR's 1,775 km total vs 733 + 566 = 1,299 km (C-006).
6. Landbridge cost (C-001): ENR full text, SAR Riyadh Rail Link tender value, the CEO's original interview.
7. 2,618 M intercity passenger-km (2023): only a search-index extraction (S-042).

Checks: `common.docver check docs` OK; `common.manifest verify` OK (4 rows); ruff clean; pytest 49 passed.

DATASCOUT_1H: done

## LANDBRIDGE_RECONCILE Landbridge cost reconciliation — 30 Oct 2026
Start: 2026-10-30 21:05 +03. Stop: 2026-10-30 21:40 +03 (coordinator on `main`, claude-fable-5-1; research and arithmetic only, no modelling, no code).

Built: `docs/costs-landbridge.md` v1.0 (headline figures with sources and grades, conversion and per-km tables, comparator table, hypothesis table a–e, conclusion, register rows, resolution list); 34 new source rows `S-lb-001` to `S-lb-034` in `docs/sources/index.csv` and `index.md` (v0.2; totals now 125 rows: verified 26, secondary 79, unverified 20); `docs/sources/conflicts.md` v0.2 (C-001 status and resolution block).

Result (analysis, confidence medium): USD 7 bn (= SR 26.25 bn) is the 2008–2011 tender-era estimate (SR 26 bn) for a 950 + 115 km freight/container line, carried unchanged by English trade press (MEED to Apr 2025, ENR Jun 2026); SR 100 bn (= USD 26.67 bn) is the 2022–2026 official whole-programme estimate including trains (Minister Al-Jasser Mar and Nov 2022; SAR CEO Al-Malik Jan 2026). The 3.81× ratio mixes scope growth (1,065 km → 1,500 km new + 678 km upgraded), all-in content, higher design speed and 11–15 years of escalation; no source quantifies the split. Per km: 7.4–7.8 USD m/km (USD 7 bn over the core) vs 12.2–17.8 USD m/km (SR 100 bn over the full scope), both plausible on their own basis against the EC 2018 and World Bank 2014 bands and Haramain (35.3). Price year of SR 100 bn: not stated by any source. Register recommendation: SR 100 bn nominal, `derived`, null high pending the reference-class uplift; SR 26–26.6 bn history-only; Riyadh Rail Link package `unknown`.

Could not verify: ENR full text (HTTP 403 by fetch tool and by curl with a browser user agent; web.archive.org not reachable from this tool); IRJ 2011 (403); Hill International project page (404); WAM Stage Two page (script-rendered; title only); the "في الصورة" broadcast and the MOT X post of 16 Nov 2022 (primaries not read). Arabic primaries found: Al-Eqtisad 20 Jan 2026 (CEO), Al-Madina 23 Mar 2022 and Mubasher 16 Nov 2022 (Minister), Okaz 22 Jun 2026 (the USD 7 bn report that bounds ENR's date). No SPA item on the cost was found.

Decisions:
- 2026-10-30: the "MEED Jul 2026" of the brief is identified as MEED, 14 Jul 2026, "Clarifications begin for Saudi Landbridge Riyadh section" (S-lb-005); it carries SR 100 bn and no package value.
- 2026-10-30: EUR 2016 PPP bands from the EC study are shown in USD at the ECB rate of 30 Oct 2026 (1.1172, S-lb-031) as an indicative conversion only, labelled crude; W3 normalises properly through `cities/ksa/costs/index.yaml`.
- 2026-10-30: the AED peg (3.6725) is cited from Gulf News (secondary) rather than added as an assumption, because `docs/assumptions.md` is outside this run's ownership; W3 should register it in `index.yaml`.
- 2026-10-30: the register rows are recommendations in `docs/costs-landbridge.md`; `cities/ksa/costs/cost_register.yaml` is W3's file (R1c) and was not touched.

Checks: `uv run python -m common.docver check docs` OK (see below). No code changed, so ruff/pytest/manifest were not re-run; the `red-team-verifier` is not invoked for this judgement run (not a milestone R<n>); the R1c verifier should spot-check S-lb rows.

Rule 7: no contact with MEED, ENR, SAR or anyone; nothing downloaded except two public PDFs (World Bank 2014 note, 0.8 MB; EC 2018 study, 1.8 MB) read in /tmp and not kept in the repository.

LANDBRIDGE_RECONCILE: done

## PILOT_MERGE National pilot: merge, coverage draft, draft funnel, scoping note — 30 Oct 2026
Start: 2026-10-30 22:09 +03 (first command). Run as `screening-analyst` on `claude-opus-5-5` in the main checkout; subagents `benchmarks-researcher` and `cost-estimator` (task 5, in parallel) and `red-team-verifier` (handoff).

Built (one commit per task; see `git log r0..HEAD`):
1. **Merge**: 13 `pilot-<slug>` branches merged with `--no-ff`, alphabetical order. `common/schemas.py` (edited three ways by asir, riyadh, tabuk) kept at main's version through the merges; `cities/ksa/sources.yaml` union (eastern + hail). Schema per coordinator decision 2 plus `osm_type`; `screening.pilot_normalise` rewrote all 13 registers (pop_type secondary → official + `pop_source_status: secondary` + `primary_to_find`; Makkah populations restored from its CSV; pilot-only columns kept in `notes`; Al-Qarā withheld, no coordinates). `screening.merge` → `cities/ksa/candidates-pilot.parquet`. Sources: 151 pilot rows into `docs/sources/index.csv`/`.md` (asir CSV repaired: two rows with unquoted commas). Assumptions: 60 pilot rows into `docs/assumptions.md`, scoped by region. Licences: DATASCOUT_1H and four pilot files merged into `docs/licences.md`/`.csv` (+2 rows). Manifest: the pilot raw files copied from the worktrees into `data/ksa/` (gitignored) and 6 rows added (16 rows verify).
2. **Coverage**: `screening.coverage` → `docs/coverage.md`, one row per governorate.
3. **Funnel**: `cities/ksa/assumptions/screening_weights.yaml` (skill defaults; every number has an assumption id; approval pending CP1); `screening.funnel long-list` and `score`; report `docs/screening-pilot.md`. Assumptions registered: A-screen-003..006, -014, -020..-030.
4. **Tests**: `tests/test_screening_pilot.py` (16 tests: new schema fields and rules, merge de-dup, long-list rules, determinism, sweep tolerance of 1 rank place on the fixture, no bare numbers in the weights file).
5. **Scoping note**: `docs/scoping-benchmarks-costs.md` (working tables in `logs/pilot_merge/`, gitignored).
6. **Plan**: `docs/plan.md` section 9, open questions 9–24 (no other section edited).

Measured:
- Pilot register: **185 rows** (13 regions; 0 duplicates; 150 with a population, all Census 2022 relayed by citypopulation.de); 1 row withheld (Al-Qarā).
- Governorates: GASTAT **unverified** (S-072, S-090: count from secondary sources, primary pending); working count **150** (S-073; the 150 populations sum to the S-077 national total 32,175,224); **152 in the table** (+2 conflict rows Abanat and Al-Bayḍā, explained row by row); 148 with a register row, 125 screened, 22 excluded, 3 not yet swept (Al-Qarā, Wādī al-Fara', Al-'Arḍiyāt); 1 register row unmatched (Hala Ammar, governorate unresolved).
- Funnel (seed 1; `runs/screening-pilot/`): long list **156** at 10,000 (168 at 5,000), served bucket **8**, did not pass 21, short list **60**. Rank stability: **24 of the top 30 (0.80)** stay in the top 30 in all 10 sweep corners (per-corner overlap 27–30). Both sensitivities (5k; committed layer included) leave the top 30 unchanged (30/30).
- Scoping reachability: benchmarks (17 rows) cost/km 0 yes / 11 partly / 6 no; ridership vs forecast 0 / 8 / 9; farebox 0 / 9 / 8. KSA cost points (48-row working table): 1 primary / 35 press / 12 none; no headline capex point has a primary in hand.
- `make test`: ruff and format clean, **65 tests passed**, docver OK on 178 files, manifest OK on 16 rows; 3.0 s wall.

Decisions: recorded with timestamps in `docs/STATUS.md` (Decisions): the coordinator's five, `osm_type`, the schema-merge handling, region-scoped assumption ids, skill numbering (A-screen-003..006) vs `docs/plan.md`, existing-layer-only scoring (A-screen-030), licence merge.

Could not verify: GASTAT's governorate list and every population at the primary (portal unreachable, S-090; all secondary); terrain (assumed in every pilot; no DEM); road distances (straight-line only, A-screen-027); Landbridge stop locations (committed layer not scored). Not committed (rule 8 / not mine): the coordinator's working-tree edits to `docs/cost-log.*`, `prompts/PILOT_MERGE.md`, `prompts/_common.md`, `run_track.sh`.

Cost: this run's row is appended to `docs/cost-log.md` by `run_track.sh` when the run ends; subagent tokens are in the run's JSON result.

VERIFY_PILOT_MERGE: done

### PILOT_MERGE closing note (builder)
- Verifier: `red-team-verifier` (claude-fable-5-1) **PASS**, 12/12 criteria, spot-check 18/18 register rows and 4/4 scoping leads (seed 20261030); report `docs/status/verify-PILOT_MERGE.md` (commit f158622).
- Fixed after the PASS (commit 48c8691, not re-audited; results unchanged, re-measured): verifier observation 3, `config_hash` now hashes input file content (two run dirs with identical inputs give one hash, scores byte-identical); observation 1, the model name copied from pilot notes no longer appears in `docs/coverage.md`. `make test` green again (65 tests, docver 179 files, manifest 16 rows).
- Open for Tariq / the coordinator (not fixed here): verifier observation 2, the citypopulation.de basis of every population and of the 150-governorate count needs Tariq's approval or a GASTAT primary before R2 (licence row flagged, approval pending); `docs/plan.md` open questions 9–24; the DATASCOUT_1H GASTAT PDF committed under `data/ksa/tables/` (verifier observation; coordinator to confirm it is allowed by rule 8).
- Elapsed: 22:09 to 22:41 +03 (about 32 minutes wall clock, measured from the first command to this note).

PILOT_MERGE: done

## CP1_PREP (31 Oct 2026, builder on `main`, WT=0)

Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

Built (commits `f7fa0bd..HEAD`, one or more per item):
1. **Item 1**: `screening_weights.yaml` v0.2 is the one criteria set; `docs/plan.md` §1 describes it; one A-screen id scheme (renumbering note in `docs/assumptions.md`). `screening/funnel.py`: `administrative` out of the role score and the role filter (A-screen-009), capped log rail gap with a 300 km cap (A-screen-021), `--gap-measure linear` and `--use-committed` sensitivities. Roles: `energy` added to `EconomicRoleName` (additive change in `common/schemas.py`), 27 sourced roles applied by `screening/cp1_fixes/apply.py` (3 proposed roles not added, reasons in `roles.csv`). Rerun: `./screening/run_pilot_funnel.sh 1`. New tests: administrative has no effect, the gap saturates at the cap, duplicate roles count once.
2. **Item 2**: A-cba-001…004 and -010, A-screen-007…012 with S-cp1 sources (rail-data-scout; `docs/sources/cp1-item2-appraisal.md`).
3. **Item 3**: `common/cost_log.py` gets `--status-file`, a worktree-first lookup, a tolerant status regex and `fix-outcomes` (11 rows corrected: 7 to done, 4 to blocked); one additive change in `run_track.sh`; 5 tests.
4. **Item 4**: 44 scripts in `screening/pilot_builders/` with a README; `docver` exclusion relative to the repository root, with a test; templates and the `region-sweep` skill on the merged schema; region prompts regenerated; `screening/region_sweep.py validate`, with 3 tests.
5. **Item 5**: Al-Qarā row (OSM admin centre node 9327998071) and 14 Riyadh seat populations (rail-data-scout; `docs/sources/cp1-item5-findings.md`); re-merged; coverage regenerated.
6. **Item 6**: citypopulation.de terms verified; a new licence row (approval pending Tariq, CP1); the 6 older rows marked superseded.
7. **Item 7**: plan §2, §3, §8 and §9; `docs/cp1-decision-pack.md` (draft); `screening-funnel` skill v1.2.

Measured (31 Oct 2026):
- Register: **186 rows**, 164 with a population (all `secondary`); coverage 152 governorate rows, 140 screened, 8 excluded, 2 not yet swept.
- Funnel, seed 1, code `session1-pilot-8-g127e382`, config hash `8a63ce04910b…`: long list **157** (169 at 5k), served 8, short list 60, top-30 stability **21 / 30** (was 24 / 30). Top 30 shares 22 towns with the run before item 1; Jazan 10 → 4, Riyadh 3 → 9. Linear-gap sensitivity: 26 / 30 overlap. 5k and committed sensitivities: top 30 unchanged.
- `make test`: ruff and format clean, **77 tests passed**, docver OK on 185 files, manifest OK on 16 rows; `common.cost_log check` OK on 19 rows. Disk: 24 GiB free.

Decisions (builder, 31 Oct 2026):
- The role source rule accepts a governorate-level tie for a centre row, but not a region-level one. So Rābigh port (KAEC) is kept and Tabuk giga_project (NEOM, province only) is not added. A CP1 decision is in the pack (D8).
- Riyadh giga_project (Diriyah Gate) and the Hafar al-Batin airport were not added, to avoid double counting.
- Al-Qarā point: the OSM admin_centre (Al Tawilah) rather than the label node, 1.1 km apart (D12).
- A-cba-001: the approved value is kept in the register and flagged for re-confirmation. The Green Book changed on 28 Oct 2026 (S-cp1-060); this is not resolved silently (D1).
- The 4 pilot runs whose status files say `blocked` are logged `blocked`, not `done` as the prompt expected (D14).
- `docs/STATUS.md` is not edited (not in this run's ownership list); the coordinator updates it from this block.
- Process slip: `git checkout -- <2 files>` was used once to restore `cities/ksa/regions/build_pilot_riyadh.py` and `pilot-tabuk_build.py` after an accidental local delete (no branch switch; both files are unchanged from HEAD). The prompt's rule forbids `git checkout`; recorded here.

Could not verify: GASTAT primary tables (portal unreachable again, S-cp1-028); the 2022 Green Book PDF (S-cp1-064); Riyadh seat identities (13 inferred by name); nothing else open on disk: correction, the first attempt to size the reclaim candidates did not run at all (`timeout` is not installed on macOS, so the loop printed "timeout" without calling `du`), and an earlier draft of plan §8 wrongly said `du` had exceeded 60 s. Re-measured with `du -sh` and `docker system df`: uv 7.9 GB, Docker 19.5 GB used / 5.0 GB reclaimable (not ~16 GB), Ollama 25 GB, Google cache 3.8 GB; plan §8 and pack D13 corrected (verifier note O3).

Cost: this run's row is appended by `run_track.sh` when the run ends.

VERIFY_CP1_PREP: done

### CP1_PREP closing note (builder)
- Verifier: `red-team-verifier` **PASS**, all 16 acceptance bullets of `prompts/CP1_PREP.md`; seeded spot-check (seed 20261031) 22/22; determinism byte-exact; report `docs/status/verify-CP1_PREP.md`.
- Fixed after the PASS (not re-audited): verifier note O3, the disk reclaim sizes are now measured (plan §8, pack D13: Docker 5.0 GB reclaimable of 19.5 GB used), plus the coverage 185-vs-186 note in the pack.
- Open for the coordinator (verifier notes, not fixed here): O2, two applied roles rest on pages not opened (S-cp1-109 Makkah hajj_umrah, S-cp1-116 Hofuf airport; both marked `secondary`); a Hala Ammar "unmatched row" line in `docs/coverage.md` itself; once Tariq decides D1, rewrite the A-cba-001 value column to one schedule.
- Elapsed: about 01:10 to 03:10 +03, 31 Oct 2026 (session start to this note; approximate).

CP1_PREP: done

## VERIFY_GREENBOOK (31 Oct 2026, verifier on `main`, read-only)

Purpose: Tariq's CP1 condition for decision D1a (A-cba-001). Report: `docs/status/verify-greenbook.md`.

- Fetched the three primary PDFs in `docs/sources/index.csv` rows S-cp1-060, S-cp1-061, S-cp1-062 (all HTTP 200, first attempt; sizes and SHA-256 in the report) plus the gov.uk Green Book landing page (`dateModified` 28 Oct 2026, change note "Updated to reflect changes to the approach to discounting.").
- Quoted verbatim: Green Book 2026 paras 6.52–6.55 (printed p.40): "3.00% in real terms for years 1 to 30 ... 2.50% for years 31 to 75, and then 2.25% for year 76 onwards"; supplementary guidance (October 2026) paras 2.1, 3.7–3.10 (p.7, p.12) and the full Annex A discount-factor table (pp.14–15, years 0–125); TAG A1.1 (May 2026) paras 2.7.4–2.7.6 (p.16): 3.5 % / 3 % / 2.5 %.
- Arithmetic: Annex A transition factors (years 30, 31, 75, 76, 125) recomputed and equal to the printed values at 4 d.p.
- Comparison: index rows, A-cba-001, plan §2 and §9, pack D1 (a) and (b) all match the sources digit by digit. No discrepancy.
- Observations for the coordinator (report §4): the supplementary guidance caps the schedule at year 125 (para 3.10) and defines it as forward rates (para 3.9); the supplementary PDF is not linked from the Green Book landing page; TAG file name `may-2025` vs cover May 2026.
- Nothing edited outside this block and the report. No push.

**VERDICT: PASS.** D1a's condition is met; the D1a/D1b choice stays with Tariq at CP1.

VERIFY_GREENBOOK: done

## INTEGRATE_R1 (31 Oct 2026, builder on `main`)

Merged branches (`git merge --no-ff`, order data → research → analysis): **r1a** a779c08 (`R1a: done`, `GEO_VERIFY: done`), **r1c** bc6128f (`R1c: done`), **r1b** 54f5f71 (`R1b: done`), **r1d** 3605320 (`R1d: done`). No history rewriting; pre-integration main c013b49 (plus one cost-log commit for the r1b row that was uncommitted on main) is an ancestor. All four worktrees were clean: no uncommitted first-attempt work.

Conflicts and resolution (all in registers; concatenated and de-duplicated by id; no id collision, so no suffixed rows were needed for ids):
- r1a: `docs/sources/index.csv`: main 388 + branch 547 rows → 551 (identical rows kept once).
- r1c: `cities/ksa/sources.yaml`: 275 + 4 → 279 rows (dumped with `common.manifest` settings; existing rows byte-identical).
- r1b: `cities/ksa/sources.yaml`: 279 + 3 → 282 rows.
- r1d: no conflict.

Register merges: `docs/assumptions.md` +211 rows (r1a 45, r1b 2, r1c 72, r1d 92; sorted by id; track preambles kept as notes); `docs/licences.{md,csv}` +45 track rows (3 r1a update rows kept with suffix `[r1a]`: OSRM (osrm-backend), networkx, OSMnx; r1b columns mapped) +3 rasterio dependencies → 202 rows, same order in both files; `docs/sources/index.csv` +1,206 rows (bench 790, cost 177, r1d 238, S-geo-001) → 1,757, `index.md` regenerated; manifest verify OK 282 rows. Per-track assumption and licence files deleted (git history); live references repointed. Per-track source CSVs kept (cited by name).

Carry-overs done: GEO_VERIFY re-verified on main (**PASS**, 8/8, 10/10 imagery and estimate spot-check, seed 31102026; `docs/status/verify-GEO_VERIFY.md` §8, last line authoritative); rasterio in `pyproject.toml` with licence rows; S-geo-001 in the source index; fixtures README rows (R1a and geo_verify fixtures); geo back-test visible in `docs/screening-pilot.md` §8 (both estimators above the 30 % gate, record-only, never used for ranking); NOTICE and `geo-verify` skill v1.1 say CDLA-Permissive-2.0 for the Microsoft footprints; R1a demo skim command in the root README; R1c conflict proposals recorded (not applied) in `docs/sources/conflicts.md`; `common.cost_log add-paid` (+ paid split in `summary`, 2 tests). Gitignored data, runs and logs from the worktrees copied into the main checkout as APFS clones.

Verifier (`red-team-verifier`, claude-fable-5-1, read-only): pass 1 at 3ec5eb3 FAIL (A7: two licence rows pointed at the deleted `docs/assumptions-r1d.md`) → fixed in b05988d; pass 2 FAIL (R4: licence CSV/MD row order differed for 3 rows; STATUS claim) → fixed in 72ed7c2; pass 3 **PASS** (`docs/status/verify-INTEGRATE_R1.md` v1.2, last line `VERDICT: PASS`). Spot-check: all 2,359 newly merged rows traced programmatically (0 unresolved S-/A- refs), 20 re-read at the live source (17 figures digit by digit, 3 status claims consistent).

Tests: `make test` green: ruff clean, 395 files formatted, **187 passed** in 9.2 s (pytest), docver 236 files, manifest 282 rows; README demo skim 2.0 s, identical to the R1a output.

Substantive issues (not integration breakage) carried to `docs/STATUS.md` "Open issues" with owners: WorldPop population basis 96 % unverified (r1a → R2/CP2), two price indices (r1b vs r1c), geo-verify UTM zone rule (O10), gitignored geo scripts (O9), run-meta data_hash (O1), stations.geojson rebuild caveat and Wadi ad-Dawasir note, `LineSpec` freight value, R1c open items, R1d licence flags, model ids in three docs (pre-existing), pilot register files left in the tree, licence md/csv wording pairs.

Disk free: 52 GiB (`df -h ~`). Cost so far: USD 284.53 list over 29 runs, 6.39 agent-hours before this run (this run's row is appended by `run_track.sh` when it ends). Elapsed: about 12:25 to 13:00 +03.

INTEGRATE_R1: done

## CP2_PREP (31 Oct 2026, builder on `main`)

Folds Tariq's CP2 decisions P1a–P4a, the HHR check and the stop research into `main` before R2 (prompt `prompts/CP2_PREP.md`). Subagents in the foreground, in parallel: `screening-analyst` (item 1), `cost-estimator` (item 2), `gis-network-engineer` (items 3 and 5), `rail-data-scout` (item 6 research); items 4 and 7 and all integration by the builder. Agents wrote register rows to fragments under `runs/cp2_prep/item<N>/` (gitignored, with `REPORT.md` each); the builder merged them. Commits: 5d17520 (item 4), f249b29 (item 7), d5485a3 (item 1), 1b36936 (item 2), 2d1e43b (item 3), ec4fa26 (item 5 + registers), 2c00ac2 (item 6), 83cfecf (close-out), 9a877ec (GASTAT tables), b41222e (addendum 1), e070d85 (primary tables), 2cc211d (source-id fix), 59f95c4 (addendum 2).

- **Population basis (item 1, A-screen-031…039; addenda 1 and 2):** settlement universe 7,371 rows = **official 215** (201 `verified` primary GASTAT city ≥ 5,000, 14 `secondary` relayed) · derived 80 (24 corroborated by the grid within 30 %, 56 not; derived rows are not gated, CP3 question) · grid corroborated **0** · grid unverified **7,076** (37 ≥ 10k, all gated). `tag_10k` 143 (141 after addendum 1; 181 as built). Pilot base case unchanged by the P1a rule and by addendum 2 (186 rows, long list 157, served 8, short list 60; addendum 2 left the top 30 and every rank identical; addendum 1's relayed figures had moved three top-30 ranks, Jizan 4 → 3, Aṭ-Ṭa'if 5 → 4, Yanbu' 3 → 5, `docs/screening-pilot.md` §5). `docs/network.md` §Population basis, `docs/screening-pilot.md` §5, §7–§8.
- **GASTAT addendum 1 (Tariq 14:40):** 19 tables committed and registered; relayed Census 2022 cities into registers/universe; 2010 cities > 5k grown at the governorate ratio as a third corroboration method (A-screen-035; 16.9 % median error on 138 official cities). **Addendum 2 (Tariq 15:25):** the primary TA1 governorate and city ≥ 5,000 exports committed (manifest 305 rows, licence row) and made the value of record. Primary vs relayed: **0 differences** (150/150 governorates, 60/60 cities, total/Saudi/non-Saudi; C-gastat-001). **Match: 202 of 271 primary cities → 201 settlements** (27,576,260 persons; tiers: relayed figure 58, identical figure 102, crosswalk 17, 2010 bridge 18, node name 7; A-screen-038); **69 unmatched** with reasons (35 ambiguous names, 22 no OSM node, 5 crosswalk none, 6 guard-rejected, 1 claimed twice). Register rows re-sourced 151 (one correction, Ash Shaharin 9,994 → 5,518, C-gastat-002); 38 changes > 2 % logged (C-gastat-005). C-cp2-601/602 causes found: the aggregator merged city + industrial city (302,446 + 172,233 = 474,679; 258,777 + 73,139 = 331,916). **Control total (A-screen-037):** grid outside matched cities 4,557,403 vs Other (< 5,000) 3,683,816; explained by the 915,148 in unmatched primary cities (residual 4,598,964, grid 41,561 below it); 7 regions over their residual; 2,048 rows flagged (172 possible double counting, 1,876 over-count/boundary). Coverage reconciles to `governorates_gastat: 150 (primary TA1 export, 31 Oct 2026)`. Source-id collision fixed (addendum 1 had reused S-cp2-601…606 of item 6 → S-cp2-gastat-001…006).
- **WorldPop back-test and flips (report only):** settlement allocation vs the 201 primary-matched settlements: median **0.710** (IQR 0.370–1.157; median abs error 49.6 %; 61 within 30 %); earlier 0.480 (60 relayed cities) and 0.637 (164 rows). Sensitivity now **÷ 0.71** (A-screen-039): grid-only rows ≥ 10k 37 → 70 (33 up by arithmetic; 55 at ÷ 0.64, 127 at ÷ 0.48); under the rule **1 up (Al-Saih), 0 down** at every ratio (`runs/screening-pilot/sens-grid-{071,064,048}/flips.csv`). Never applied to the base case.
- **Normalisation delta (item 2):** one index `cities/ksa/costs/index.yaml` (1,219 factors; the 882 earlier ids rebuild identically; cost register 207 items validate); `index-r1b.yaml` and its template deleted. 164 values (82 grade A–C rows × central/sensitivity), 120 comparable: 65 changed; central max |Δ| 0.001 % (rounding); sensitivity (now Saudi CPI after conversion) median 10.0 %, max 13.3 %; dossier medians −3.0 % (France) to −8.4 % (China, Italy). A-cost-002 approved, A-bench-001 superseded, A-cost-307 (EUR outside the euro area, AED, TWD) **pending**. `docs/benchmarks/normalisation-delta.md`.
- **UTM fix (item 3):** zone = floor((lon + 180)/6) + 1, checked against pyproj; boundary tests. Re-run: 74 of 140 central estimates changed, median 0.006 %, max 91.2 % (Al Harth 665 → 1,272, clusters joining at the 100 m threshold); back-test grid 66.74 → 66.73 %, buildings 59.44 → 59.50 %: **gate decision unchanged** (both fail, record-only); conflicts > 25 % 103 → 102. Geo scripts tracked (O9); GEO_VERIFY metas refreshed on clean 2c00ac2 (O1). `docs/geo-verify.md` §10.
- **Freight lines (item 4):** `LineSpec.line_type` gains `freight`; only `sar-north-freight` and `sar-east-freight-legacy` changed (S-cp2-401 SAR, S-cp2-402/403 secondary); `rail.lines validate` 15 files, 0 errors.
- **HHR decomposition (item 5):** (a) 13.10 + (b) 2.78 + 2.31 + (c) 0 + (d) 2.06 = **20.25 min** (envelope 18.94–22.25) vs the published 43 min, which is the **October 2018 opening timetable** (S-cp2-503/507). **C-r1a-22 kept open, residual 22.7 min** (20.7–24.1); 7.7–9.7 min against current secondary 28–30 min. Resolves with a current SAR timetable, an HHR speed profile, Talgo 350 SRO curves. `network/hhr_check.py`, `docs/network.md` §HHR-check, `docs/sources/conflicts.md`.
- **Stops (item 6):** of 14 unlocated: **1 resolved** (Al-Ahsa freight stop, OSM SAR Al Hufuf station), **11 low-confidence** (town/facility centroids with bands, A-stn-001…009), **2 unlocated** (Riyadh Rail Link connection points). Committed stops stay committed. `rail.lines build` now merges (full rebuild: 0 differing features, 14 kept; test). Served test: served 8 → 8, `dist_existing_km` unchanged, `dist_committed_km` changed on 15 pilot rows (max 13.1 km). `rail/station_research.yaml`, `docs/network.md` §2.
- **Housekeeping (item 7):** model ids removed from the three docs (test guards `docs/` outside STATUS, `docs/status/`, the cost log and the Claude Code licence row); 100 fragment rows found in the merged registers (0 missing) → 23 fragment files deleted, rule in `docs/versioning.md` §5; `docs/licences.md` table generated from the CSV (`common.licences sync`; 20 rows rewritten; now 205 = 205, 0 differ). Carry-overs open in `docs/STATUS.md` with "no release use until cleared": R1d licence flags, five zero-spread cost defaults.
- **Registers:** +19 S-cp2 sources and +8 S-cp2-gastat sources (index 1,784 rows, `index.md` regenerated by `scripts/regen_sources_index_md.py`), +22 assumptions (A-screen-031…039 with A-screen-034/036 superseded), +7 licence rows, +23 manifest rows (305; HHR 2018 timetable capture, stop extent radii, 21 GASTAT tables).

Decisions: INTEGRATE_R2–R9 prompts, regenerated as a side effect of `make_region_prompts.sh` (they pick up the coordinator's 31 Oct INTEGRATE_TEMPLATE addition), were restored to HEAD: coordinator-owned; re-run the script when the coordinator wants them. The King Abdulaziz Port point (Wikipedia coordinate vs OSM node, 4.4 km apart) is a choice recorded as A-stn-009 for the coordinator. `network.zones` tag_10k is not yet gated (R2).

Not done / could not verify: no Talgo 350 acceleration figure, no HHR speed profile, no current SAR timetable found; EPSG terms page HTTP 403 (licence row `unclear`). The GASTAT primary-matching leftovers (69 unmatched cities, C-gastat-003/004, the "Al Ahsa" node with a governorate-scale tag, 2,048 control-total flags) are carried to R2 in STATUS Open issues.

Verifier (`red-team-verifier`, read-only, label VERIFY_CP2_PREP): pass 1 at 8943db4 **FAIL** (F1: source row S-cp2-607 lost when addendum 1 reused the item 6 ids; F2: S-cp2-505 DOI returned 404) → fixed in f789fbc (row restored, citation-resolution test added; journal URL with values re-read in the PDF); pass 2 **PASS** (`docs/status/verify-CP2_PREP.md` v1.1, last line `VERDICT: PASS`).

Tests: `make test` green: ruff clean, **285 passed** (+98 since INTEGRATE_R1), docver 221 files, manifest 305 rows, cost log check 30 rows, licences 210 = 210. Disk free 52 GiB. Cost so far USD 304.90 list over 30 runs before this run (this run's row is appended by `run_track.sh`). Elapsed about 13:40 to 15:10 +03 (first attempt), then the resume run for the GASTAT addenda.

CP2_PREP: done

## R2 national screening (31 Oct 2026, screening-analyst on `main`)

Merged the 13 `r2-<slug>` branches in alphabetical order (`git merge --no-ff`; merges 9114a96 … 109a915). One conflict, `cities/ksa/sources.yaml` (al_jouf and makkah each added one row): both rows kept, manifest verifies at 307 rows. The region branches touched only `cities/ksa/regions/`, `docs/`, `screening/sweeps/<slug>/`, `cities/ksa/sources.yaml` and three new region tests (`tests/test_region_asir.py`, `test_hail_register.py`, `test_makkah_register.py`), all additive; no code outside `screening/` changed, so nothing was aborted. Gitignored sweep data copied from the worktrees as APFS clones. Chain: `./screening/run_r2.sh 1` (seed 1; outputs `runs/r2/`, each with `meta.json`); a second run left `cities/ksa/candidates.parquet`, the corridors and `docs/coverage.md` byte-identical.

- **Register:** 1,678 merged rows (al_baha 16, al_jouf 83, asir 37, eastern 57, hail 17, jazan 50, madinah 21, makkah 77, najran 13, northern_borders 57, qassim 35, riyadh 1,096, tabuk 119; 0 duplicates; every row validates against `RegionRow`) + 13 rows created for primary cities = **1,691** (`docs/candidates.md`). No region has zero rows; every governorate has at least one row.
- **Primary cities (addition 1):** 271 → **matched 212, created 13, unmatched 46** (614,199 persons; 12 ≥ 10,000), each unmatched city listed with its population in `docs/screening.md` §2. New tiers beyond CP2 (A-r2-001/002): archived citypopulation.de relays as an identical-figure bridge to Arabic name and region, then the full OSM place extract (Al-Ahsa villages are OSM neighbourhood nodes the R1a universe leaves out: 12 created, e.g. Aṭ-Ṭaraf 29,588), Arabic consonant skeleton with a size band from the CP2 back-test. Al-Hofuf keeps the declared Alhufuf + Almubriz combination (729,606).
- **Blocked sweeps resolved:** MADINAH: the 18 unassigned ≥ 10k cities are handled by the national matcher (none of the 12 still-unmatched ≥ 10k cities is placed in Madinah by any source; Wadi Al Oqool farms 24,381 kept unplaced and listed, decision file). NORTHERN_BORDERS: `screening.geo_verify.cli estimate` gained an additive `--registers` glob (pilot default unchanged) and ran from the main checkout on the 23 no-population rows (`runs/r2/geo_verify/estimate-northern_borders/`, seed 1; 5 open Microsoft footprint tiles fetched, ≈ 0.1 MB, registered dataset): highest band 3,160, so no row reaches 5,000; record-only (both estimators failed the 30 % back-test gate). AL_JOUF: Ghata 6,653 placed on node 1236744649 غطي by judgement (غطى/غطي, Al-Qurayyat membership, geo-verify `seat` inside the polygon 20.45 km from the boundary; grid 0.31 of the figure; conflict C-r2-001). Dariyah: two rows for one place; the place node keeps the figure, the relation row is a duplicate.
- **C-gastat-003/004:** primary wins, both values (0.0 % difference) and file names in `docs/sources/conflicts.md`; Adham on أضم, Alshazalah on Ash-Shanan via the Hail relay.
- **Control total (addition 2, A-screen-040):** 8 regions scaled (riyadh 0.7040, makkah 0.7554, madinah 0.8733, qassim 0.6305, northern_borders 0.6311, najran 0.9289, al_baha 0.6918, al_jouf 0.8028; 5 at 1.0); 1,222 register grid rows; register grid sum 2,076,812 → 1,642,789. Gate unchanged; ÷ 0.71 sensitivity on raw values: 1 flip up (Al-Saih), 0 down.
- **Funnel (CP1 criteria unchanged):** long list **189**, served 8, short list **60**; top-30 stable in all 10 corners 23/30; Kendall tau over 55 ranking pairs min 0.885, median 0.938. 5k sensitivity: long 357, 16 enter / 16 leave the short list (lists in `docs/screening.md` §7); linear gap 8/8; committed layer 3/3.
- **Corridor families:** 74 YAMLs (S2 trunk gaps 23, incl. the T2 speed gaps Jeddah–Riyadh and Riyadh–Dammam; S3 branches/spurs 17; S4 commuter belts 27 over 10 metros; S5 station additions 7), each with `rule_id`, `generated_from_ids`, sketch alignment, terrain/structure shares with method, assumptions used, `uncosted`; 21 dominated/merged/redirected candidates with reasons (`runs/r2/corridors/decisions.csv`, also in each scenario). `uv run python -m common.scenarios validate scenarios/` → ok 6 (new module, additive). Rules A-corr-001…015 registered.
- **Coverage:** `docs/coverage.md` 150 rows = governorates_gastat 150 (S-cp2-gastat-007), 13/13 regions, 0 unmapped register rows, 0 governorates without a row, 0 excluded (4 centre-only governorates pass by rule 2).
- **Registers:** 82 region assumption rows + 18 R2 rows merged into `docs/assumptions.md`; 13 region source CSVs into `docs/sources/index.csv` (+31 rows, 28 updated in place: `used_in` unions and status texts extended; index 1,815; `index.md` regenerated); 7 licence uses folded into existing rows (`common.licences check` 0 differ). Fragments deleted (`docs/versioning.md` §5); four region docs repointed. The sweep scripts under `screening/sweeps/` still name their fragment paths (regenerating a region doc would recreate a fragment).
- **Tests:** `make test` green: ruff clean, **311 passed** (+26: 13 R2 tests in `tests/test_screening_r2.py` run in about 2 s, plus 13 region tests), docver, manifest 307 rows.

Not done / could not verify: terrain is unclassified on 95 long-list rows (median fill) and no DEM read was made (corridor terrain shares are a register-row proxy); road skims for the 13 created rows are `pending skims`; corridor alignments are great-circle sketches; every corridor is uncosted. One row of `docs/licences.csv` (row 179) has more cells than the header (pre-existing; not touched).

Verifier pass 1 (`red-team-verifier`, read-only, label R2) at fe85d0e: **FAIL** on two hygiene items, technical criteria 1–9 PASS (spot-check: 223/224 primary-figure rows equal the TA1 table, the 224th the declared Al-Hofuf combination; corridors regenerate byte-identically). Fixed: (1) handoff completed (this block's status line, `docs/STATUS.md` milestone row, R2 decisions, CP3 decision list, open issue updated to 46 unmatched); (2) model labels removed from region docs, register notes and registers (CP2 P5 housekeeping), with `docs/plan.md` §6 and the Claude Code licence row left for the coordinator as listed exemptions; A-screen-040 now states the universe denominator; the 478 zero-population grid rows are a CP3 item. The chain was re-run after the note edits (only the input hashes in the corridor `source:` lines changed).

Elapsed: about 17:00 to 18:00 +03. Cost: the 13 REGION_* runs logged USD 53.68 list (`docs/cost-log.md`); this run's row is appended by `run_track.sh` when it ends (R2 cap USD 90, alert at 72).

Verifier pass 2: F1 and F2 closed (the `docs/plan.md` §6 label exemption accepted for R2, to confirm at CP3); new F3: the regenerated `scenarios/S2–S5.yaml` were not staged in af784f5 → committed in de5a9b1. Pass 3: **PASS** (`docs/status/verify-R2.md` v1.2, last line `VERDICT: PASS`). Non-blocking: the 11 `pilot-*.parquet` registers fail `region_sweep validate --strict` for pre-existing header reasons (unchanged since 10d954c; excluded from the R2 merge).

R2: done

## INTEGRATE_R2 integration audit and CP3 fixes (31 Oct 2026, builder on `main`)

Merged branches: none in this run. R2 had already merged the 13 `r2-<slug>` branches with `--no-ff` (9114a96 … 109a915; one additive conflict in `cities/ksa/sources.yaml`, both rows kept); the coordinator's addendum says not to re-merge. No history rewriting. Work done: the CP3 decisions (Tariq, 31 Oct 2026). Commits 47945e0, 8af22be, 4a8292d, 98ef304 and the verifier-fix commit after them.

- **Item 1, the 12 unmatched ≥ 10k primary cities (CP3 4a): 11 placed, 1 known, unplaced.** Jubail Industrial City (172,233) is its own register row, `eastern:node:1237806971` (OSM place اللجنة الملكية في الجبيل / Al Jubayl Royal Commission, 10.4 km NW of the Al Jubayl node; `official`/`verified` by Tariq's instruction), not folded into Al Jubayl (302,446). **Al Jubayl: rank 2 before and after (score 0.9194 → 0.9196, sweep range 2–2); Jubail Industrial City: rank 16 (sweep range 6–22), on the short list**, roles not assessed (scores 0 on that criterion). Corridors touching them: the Dammam–Khobar–Dhahran 315° commuter belt now carries both (77.0 → 87.5 km, 2 → 3 stations), and a new S5 station addition `S5-station_addition-al-jubayl-royal-commission` sits on the same alignment as `S5-station_addition-al-jubayl` (open issue for R4). The other ten: Arqa → عرقة (Riyadh), Alkalabiuh, Almunayzilh, Albitaliuh, Alhaliluh → Al-Ahsa OSM place polygons, Alqawz → القوز (existing register row), Alulya → Sabt Al 'Alayah, Wadi Al Oqool farms → village العاقول, Benban → suburb بنبان, Alhasma → village الحصمة (low confidence). **Iiskan Alkalabiuh (12,817, Al-Ahsa) stays known, unplaced** → R4. Method: national relay page S-qassim-003, OSM place polygons (new manifest row `osm-gcc-place-areas-extract-2026-10-14`), place-rank tie-break (A-r2-003), judgements (`screening/primary_match_decisions.yaml` v1.1). Geo-verify `seat`: all 13 new placements inside their governorate polygons (`runs/integrate_r2/geo_verify/seat-*`, seed 1). Totals: 238 of 271 placed (214 matched, 24 created), 33 known, unplaced (222,950 persons; 1 ≥ 10k).
- **`derived` flag (A-r2-004):** 25 primary-city rows placed by OSM extract or judgement carry `pop_type: derived` (incl. Ghata and the 12 Al-Ahsa rows CP3 named); Jubail Industrial City and Dariyah `official` by decision.
- **Item 2, zero-population rows (CP3 5a; A-screen-041):** 478 grid rows with raw value 0 dropped from the register (riyadh 393, tabuk 64, al_jouf 21), kept in the settlement universe; register 1,702 → 1,224 rows; **0 rank changes**, short list unchanged (as expected).
- **Effect of item 1 on the funnel:** long list 189 → 198, short list 60 → 60 (enter Jubail Industrial City #16 and Banban #52; leave Samitah #59 → #61 and Yanbu Industrial City #60 → #63); top-30 stable in all 10 corners 23/30 (unchanged); Kendall tau min 0.878, median 0.936 (was 0.885 / 0.938). Corridors 74 → 76 (S5 7 → 9; added S3 Yanbu spur, S4 Riyadh 315°, two S5; removed the merged Yanbu Industrial City spur and Jazan 090°). Control-total factors (CP4 material, `docs/screening.md` §3): riyadh 0.7040 → 0.6294, makkah 0.7554 → 0.7315, madinah 0.8733 → 0.7923, qassim 0.6305 → 0.6146, eastern 1.0 → 0.8527, others unchanged. Before/after: `runs/integrate_r2/check/check.json` (`screening.integrate_r2_check`).
- **Item 3, housekeeping:** `docs/licences.csv` row 180 (row 179 of data) rejoined (a comma had split the World Bank WDI obligations cell; 211 lines × 11 cells; 210 = 210). Pilot registers archived to `cities/ksa/regions/archive/pilot/` with README (they are samples and cannot pass `--strict`); 14 code paths repointed; the 13 national registers pass `--strict`.
- **Item 4:** CP3 approvals and the 7a exemptions recorded (STATUS, INTEGRATE_R2 decisions); scale factors and the Jubail check in `docs/screening.md` §2a and §3; CP4 open questions in §8.
- **Registers:** assumptions +3 (A-r2-003, A-r2-004, A-screen-041; A-r2-001 extended), 0 removed; licences 210 rows (OSM row `used_in` extended); sources index 1,815 rows (S-qassim-003 `used_in`), `index.md` regenerated; manifest 308 rows (+1). No per-track fragment files exist to fold (R2 deleted them).
- **Tests:** `make test` green: ruff clean, **318 passed** (+7 in `tests/test_integrate_r2.py`), docver, manifest 308 rows, licences check; README demo (`network.skims` on the Jeddah fixture) runs in about 2 s. The chain `./screening/run_r2.sh 1` regenerates every tracked output byte-identically on the committed tree (about 12 s).

Not done / could not verify: no GASTAT locality table, so Iiskan Alkalabiuh and 32 smaller cities stay unplaced; the Alhasma placement rests on name and size only; roles and terrain for the 24 created rows are not assessed (R3 terrain from DEM).

Verifier (`red-team-verifier`, read-only, label INTEGRATE_R2) pass 1 at 98ef304: **FAIL** on three items, all technical criteria PASS (spot-checks of 6 national-relay and 10 eastern-relay figures, 19 OSM objects and the evidence distances all match): F1 the CP3 5a drop rule had no assumptions row → A-screen-041 added; F2 STATUS header (last updated, disk, cost) stale and this block missing → updated, block written; F3 `docs/sources/index.md` not regenerated → regenerated. Observation O1 (Alhasma: four الحصامة places, not three) fixed in the decision text.

Verifier pass 2 at 811202e: **PASS** (`docs/status/verify-INTEGRATE_R2.md` v1.1, last line `VERDICT: PASS`): F1–F3 and O1 closed; numbers in this block re-measured; chain byte-identical; 318/318 tests. Non-blocking for R3: the settlement-universe row for Sabt Al 'Alayah carries an OSM tag of 200,000 while the register holds the TA1 figure 20,250 (R3 reads the register); `common.assumptions check` named in the skill does not exist (pre-existing).

Elapsed: about 18:05 to 18:50 +03. Disk free 49 GiB. Cost before this run USD 402.47 list over 45 runs; this run's row is appended by `run_track.sh` when it ends.

INTEGRATE_R2: done

## INTEGRATE_R3 integration of track r3 (31 Oct – 1 Nov 2026, builder on `main`)

Label for every modelled number: **synthetic demand, uncalibrated: scenario comparison, not a forecast** (one total `calibrated` at the 2025 point: SAR East + North rail, approved CP4-1a).

**Inventory.** One R3 branch: `r3` (15 commits, last cca22c2), status line `R3: done` (verifier `docs/status/verify-R3.md` pass 2 PASS). No `blocked` track.

**Merges.** `git merge --no-ff r3` → 50f9bbe `merge(R3): r3`. One conflict, `docs/STATUS.md` (the coordinator's CP4 decisions and pilgrim-data note vs R3's decisions and CP4 decision list in the same place): this run owns `docs/STATUS.md` (task 5), so both sections were kept in full and the header taken from `r3`. No other file conflicted; no history rewriting, no tag, no push.

**Registers** (commit 0427c91): assumptions 369 → 479 rows (+110 R3 rows sorted in by id: A-demand 59, A-geo 12, A-mode 21, A-pop 18; 0 collisions); licences 210 → 232 (+22; 0 item collisions; WPP placeholder row marked superseded); sources index 1,815 → 1,892 (+77 `S-r3-*`; 0 collisions), `index.md` regenerated; manifest 331 rows OK. Per-track `docs/assumptions-r3.md` and `docs/licences-r3.{md,csv}` deleted (git history); `docs/sources/r3-*.csv` kept (cited by documents and code). Live pointers repointed. CP4 approvals written into 13 rows; `docs/demand.md` §8 marks SAR East + North rail `calibrated` (CP4-1a).

**Coordinator addenda.** `add-paid` already present (no change). Scenarios: `cities/ksa/assumptions/modechoice.yaml` thin include (priors + R3 file) so the generated S2–S5 stay valid; `common.scenarios.check_mode_choice` (additive) + 3 tests; `validate` → ok 6 scenario files. Conflicts C-r3-001…003 in `docs/sources/conflicts.md`. R4 hand-offs listed in `docs/STATUS.md` Open issues. NOTICE: R3 attributions.

**Data and runs.** R3 data and 471 run files cloned from the `r3` worktree (`cp -c`, APFS, no new disk; common files byte-identical). `./demand/run_r3.sh 1` re-run on the committed tree 0427c91 (about 3 min): every OD SHA-256 of the S0 baseline, `calibration.json` and all 36 rows of `runs/demand/summary-s1/summary.csv` identical to the track except `code_version` (now `r2-int-20-g0427c91`); config hash `e58ff5e8f804…` unchanged. Log `logs/integrate_r3_run_r3.log`.

**Measured.** `make test` green: ruff clean, format clean, **401 passed** in 16.3 s (pytest junit; +3 new, one parametrised case replaced by a scoped test of the merged R3 rows), docver OK 266 files, manifest OK 331 rows, licences 232 = 232. README demo (`network.skims` on the Jeddah fixture) 2.1 s wall. Disk 48 GiB free. Cost before this run USD 476.29 list over 47 runs (R3 USD 56.17); this run's row is appended by `run_track.sh`. No paid model or API; no download; no contact with anyone.

**Not done / could not verify.** The TGA Q1–Q2 2025 rail figures behind C-r3-002 are not registered as separate source rows (read from the Argaam series; unverified). The addendum's "TGA Q1–Q2 bus" conflict maps to rail quarters (no TGA Q1 2025 bus figure exists); recorded as such.

**Verifier.** `red-team-verifier` (read-only, label INTEGRATE_R3) at 2cbf522: **PASS**, A1–A10 (`docs/status/verify-INTEGRATE_R3.md`, last line `VERDICT: PASS`; re-measured 401 passed in 16.65 s, README demo 2.4 s, spot-check 11 of 110 merged rows, seed 20261101). Observations fixed after the verdict: (1) `docs/demand.md` determinism and run-time notes now also state the main re-run (data hash `773494feadc0…`, code version `r2-int-20-g0427c91`; OD hashes unchanged); (2) six `S-r3-*` rows in `docs/sources/index.csv`, `r3-dem.csv`, `r3-pop.csv` repointed from the deleted fragment files to `docs/assumptions.md` / `docs/licences.csv`, `index.md` regenerated. (3) This run's cost row is appended by `run_track.sh` at run end; `data/ksa/tables/pilgrims/` stays untracked for R4 (both as designed). After the fixes: `make test` green, 401 passed, docver 267 files, manifest 331 rows.

Elapsed: about 23:50 (31 Oct) to 00:30 (1 Nov) +03.

INTEGRATE_R3: done

## INTEGRATE_R4 integration of track r4 (1 Nov 2026, builder on `main`)

**Synthetic demand, uncalibrated: scenario comparison, not a forecast** (for every R4 figure referred to here; figures in `docs/status/r4.md`).

**Inventory.** One phase branch, `r4`, holding two milestones: `R4: done` (verifier `docs/status/verify-R4.md` v1.1 PASS) and `R4_ALIGN: done` (verifier `docs/status/verify-R4_ALIGN.md` v1.2 PASS). No `blocked` track. No HOLD line in `logs/orch/PAUSE` at start.

**Merged.** `git merge --no-ff r4 -m "merge(R4): r4"` → 2f77f9d (parents cff5cce on main, bb0aedf = r4 tip). No conflict. Before the merge: the uncommitted R4/R4_ALIGN cost-log rows committed (cff5cce); the untracked `data/ksa/tables/pilgrims/` (46 files) checked byte-identical (SHA-256) to the copies committed on `r4` and moved aside so the merge could write them. No rebase, reset or force.

**Conflicts and resolution.** None in git. Register level: 0 assumption id collisions (79 rows), 0 source id collisions (102 rows); 1 licence item-name collision with different content (`Poppler pdftotext`, datascout vs r4 use) kept as two rows, the r4 one suffixed `[r4 use]`.

**Registers.** `docs/assumptions.md` 479 → 558 main-table rows (sorted by id; superseded/re-specified pointers on A-demand-051, A-screen-005, A-screen-022, A-corr-012); `docs/licences.{csv,md}` 232 → 254 (`common.licences check` 0 differ); `docs/sources/index.csv` 1,892 → 1,994, `index.md` regenerated (v0.9). Fragments `docs/assumptions-r4{,a}.md` and `docs/licences-r4{,a}.{md,csv}` deleted; `docs/sources/r4-*.csv` and `r4a.csv` kept (cited). Live pointers repointed (code, docs, YAML comments, S-r4a `used_in`). NOTICE: SUMO/OSRM block and an R4 attribution block.

**Data and runs.** `data/ksa/align` (740 files, 1.0 GB) and the R4 run directories cloned from the `r4` worktree (`cp -c`, no overwrite; `diff -rq` shows nothing missing on main). Chains not re-run on main (verified on `r4`; no input changed in the merge; the YAML comment edits do not change the parsed-YAML hashes, frozen weights hash `2b718ecb…a792d4` re-computed unchanged).

**Measured.** `make test` green: ruff clean, format clean, **430 passed** in about 17 s (401 → 430), docver OK 278 files, manifest OK 386 rows. README demo (`network.skims`, seed 1) exit 0 in 2.8 s, code version `r3-38-g90f852c` (clean). Disk 44 GiB free. Cost so far USD 567.55 list over 50 runs before this run's row; R4 phase 81.99 against the 90 estimate.

**Verifier.** `red-team-verifier` pass 1 at 42c90b0 (`docs/status/verify-INTEGRATE_R4.md`): FAIL F1, the regenerated `docs/sources/index.md` kept its old version header; observations: stale `used_in` on S-r4a-001…003, YAML comments (justification corrected), CP5 item 10 listed as a separate open issue, GACA/SPA terms not read (release check). Fixed in 60f33c6 (header v0.9, pointers repointed). Pass 2 at c0c11c0: **PASS** (F1 closed, observations addressed, frozen weights hash re-derived unchanged, `make test` 430 passed, README demo byte-identical across two seed-1 runs; last line of the report `VERDICT: PASS`). Its notes for the coordinator: mark `scripts/r4_licences.py` superseded at its next touch; the demo code version quoted above (`r3-38-g90f852c`) predates the fix commits; confirm the INTEGRATE_R4 cost-log row before tagging `r4`.

**Not done.** No R4 chain re-run on main; R4 substantive open items (HHR gate, air uncalibrated, seeds 2–3, offset target, viaduct lower bound, sidecar ODbL, earthworks pricing, Abha belt 315) are carried in `docs/STATUS.md` Open issues for CP5, owner track r4.

Elapsed: about 03:37 to 04:20 (1 Nov) +03.

INTEGRATE_R4: done

## INTEGRATE_R5 integration of track r5 (3 Nov 2026, builder on `main`)

**Synthetic demand, uncalibrated: scenario comparison, not a forecast** (for every R5 figure referred to here; figures in `docs/status/r5.md` and `docs/cba.md`).

**Inventory.** One phase branch, `r5`: last status line `R5: done` (`docs/status/r5.md:53`; verifier `docs/status/verify-R5.md` v1.2 PASS on pass 3). No `blocked` track.

**Merged.** `git merge --no-ff r5 -m "merge(R5): r5"` → cae59b8 (parents 1127d22 on main, 0258614 = r5 tip). No rebase, reset, force, tag or push.

**Conflicts and resolution.** Git: one, `docs/STATUS.md` header line (main's v1.19 vs r5's v1.19 with the R5 author entry). This run owns `docs/STATUS.md` (task 5; precedent INTEGRATE_R3), so both author lists were kept in one header, v1.20. Register level: 3 assumption ids collided by design (the fragment's "Updates to existing rows": A-mode-011 CP5 H2a, A-intl-003 CP5 H3a, A-r4-rt-010 CP5 H1a); both rows kept, the updated one with the id, the old one as `<id> [pre-R5]` with a superseded note; logged in `docs/STATUS.md` (INTEGRATE_R5 decisions). 0 licence item and 0 source id collisions. `common/schemas.py` change on r5 is additive (new optional `CbaCase` fields).

**Registers.** `docs/assumptions.md` 558 → 652 main-table rows (sorted by id, R5 track notes added; v1.18); `docs/licences.{csv,md}` 254 → 263 (`common.licences sync`, check 0 differ; R5 track notes; v1.6); `docs/sources/index.csv` 1,996 → 2,076 rows from `docs/sources/r5-{cba-a,cba-b,cost,hhr}.csv`, `index.md` regenerated (v0.11). Fragments `docs/assumptions-r5.md` and `docs/licences-r5.{md,csv}` deleted (git history); `docs/sources/r5-*.csv` kept (cited, as R4). Live pointers repointed in `docs/cba.md`, `docs/demand.md`, `docs/network-evaluation.md`, a comment in `cities/ksa/assumptions/cba_programme.yaml` and CP6 item 11. NOTICE: "Appraisal parameters (R5)" block (all 9 R5 licence rows, SGP added after the verifier's note). `common.cost_log add-paid` already present (INTEGRATE_R1).

**Data and runs.** R5 re-ran `runs/access`, `runs/costs`, `runs/network-eval` (rail-graph fix) and added `runs/cba`, `runs/r5`; the r5 worktree's runs were APFS-cloned onto main (`cp -c`): 1,115 new files, 675 replaced; main's R4-era copies kept under `runs/_superseded/INTEGRATE_R5/` (gitignored). `diff -rq` shows nothing missing on main. The two dirty scratch dirs (verify-R5 O14) carry a local `SUPERSEDED.md`. Chains not re-run on main (verified on `r5`; no input changed in the merge; YAML comment edit does not change the parsed-YAML config hash).

**Measured.** `make test` green: ruff clean, format clean, **462 passed** in about 22 s (430 → 462), docver OK 283 files (284 with the verifier report), manifest OK 386 rows; about 25 s in total. README demo (`network.skims`, seed 1) exit 0 in 2.1 s, code version `r4-21-g60ae856` (clean). Disk 42 GiB free. Cost so far USD 667.50 list over 52 runs before this run's row; R5 phase 90.59 against the estimate 80 (guard 120).

**Verifier.** `red-team-verifier` at 392627e (`docs/status/verify-INTEGRATE_R5.md`): **PASS**, 15 criteria (merge `--no-ff`, registers supersets with 94 fragment rows verbatim and 3 `[pre-R5]` rows, licences and sources prefix-identical, runs complete with no `-dirty` R5 meta, `make test` 462 passed, README demo byte-identical across two seed-1 runs apart from the timestamp, P10/P50/P90 recomputed for three cases, hygiene clean). Pending by task order: this block, the `done` line and the INTEGRATE_R5 cost-log row (the orchestrator appends it). Observations folded in this commit: NOTICE SGP line, CP6 item 12 "R5 merged ✔", verify-R5 O13–O15 carried to Open issues; `docs/assumptions-r2.md` remains in the tree (pre-existing, not an R5 file).

**Not done.** No R5 chain re-run on main. R5 open items (P5b zone split, judge back-test, ±15 % precondition, unclear IMF/SGP/CE Delft terms, verify-R5 O3/O5/O6/O8/O10/O13–O18) are carried in `docs/STATUS.md` Open issues, owner track r5 or r6.

Elapsed: about 17:58 to 18:15 (3 Nov) +03.

INTEGRATE_R5: done

## INTEGRATE_R6 integration of track r6 (3 Nov 2026, builder on `main`)

**Inventory.** One R6 branch, `r6` (tip ad29be1), last status line `R6: done` (verifier `docs/status/verify-R6.md` v1.1 PASS on pass 2). The working tree carried the uncommitted R6 cost-log row; committed first (2c2bd93) so the merge and the run metas start clean.

**Merges.** `git merge --no-ff r6` → 1fe457d `merge(R6): r6`. No history rewriting, no tag, no push.

**Conflicts and resolution.** Git: one, the `docs/STATUS.md` header line (main's v1.21 with the coordinator's R6-estimate entry vs r6's v1.21 with the R6 milestone-row entry). This run owns `docs/STATUS.md` (task 5; precedent INTEGRATE_R3/R5), so both author lists were kept in one header, v1.22. Register level: none (13 new A-r6 ids, 3 licence items with distinct names, no source rows).

**Registers (b6a2a32).** Assumptions +13 (A-r6-001…013, sorted into the main table: 652 → 665 rows); licences +3 (CSV appended, Markdown regenerated with `common.licences sync`: 266 = 266, 0 differ; the R0 `HiGHS … planned; unverified` row left as written beside the verified `[r6]` row); sources +0 (R6 wrote no `docs/sources/r6*.csv`; index unchanged). Track notes added to both registers; fragments deleted (history at 1fe457d); `cities/ksa/assumptions/r6_search.yaml` pointer repointed (v1.1; not a judge input).

**Data on main.** R6 re-ran `runs/zones/` and `runs/skims/` (P5b split): 12 files replaced with the track's versions, old copies in `runs/_superseded/INTEGRATE_R6/` (3.5 MB, gitignored). `runs/r6/` (7,043 files) and `judge/` (v1-r5, v2-p5b, _retired-v2-p5b-uncal; read-only) APFS-cloned with `cp -c`. `diff -rq` worktree vs main: 0 missing or differing under `runs/zones`, `runs/skims`, `runs/r6`. `optimise.judge verify`: v2-p5b intact (2bdee7f5…), v1-r5 intact (f20091cf…).

**Verification.** `make test` green: ruff, format, **473 passed** (462 → 473), docver, manifest 386 rows; about 25 s. README demo exit 0 in 2.4 s. `red-team-verifier` (read-only) on 2b7c04d: **PASS**, 0 FAILs (`docs/status/verify-INTEGRATE_R6.md`); its O1 condition (this block and the status line) is met here; the INTEGRATE_R6 cost-log row is appended by `run_track.sh` at run end (R5 precedent). Other observations carried: run metas `r5-dirty` on `runs/zones` and the two skims dirs (clean rebuild byte-identical, in STATUS); the R0 licence row with model ids (pre-R6, release check); the old HiGHS row to mark superseded at next touch; pre-existing unsorted `A-najran-*` rows and `docs/assumptions-r2.md` in tree; R6 doc headers still `draft`.

**Coordinator addenda.** `add-paid` already present in `common/cost_log.py` with tests (no change).

**Status and changelog (2b7c04d).** `docs/STATUS.md`: INTEGRATE_R6 milestone row, R6 row marked merged, INTEGRATE_R6 decisions, R6 open items (checkpoint list items 1–6, verify-R6 O1/O7/O10, dirty metas, budget-guard stop, ODbL note), disk 38 GiB (below the 40 GiB measured at R5; no download planned before R10's ≥ 50 GiB gate), cost USD 709.84 over 54 runs before this run's row. `CHANGELOG.md`: r6 section.

**Not done.** No R6 search re-run on main. The R6 checkpoint (layouts for R7, budget levels A-r6-003, judge v3 for variants, re-fit and international share, accessibility metric, new links) is for Tariq; R7 needs explicit approval.

Elapsed: about 20:49 to 21:03 (3 Nov) +03.

INTEGRATE_R6: done

## INTEGRATE_R6_V3 integration of track r6v3 (4 Nov 2026, builder on `main`)

**Inventory.** One R6_V3 branch, `r6v3` (tip 5ca3472), last status line `R6_V3: done` (verifier `docs/status/verify-R6_V3.md` v1.1 PASS on pass 2). The working tree carried the uncommitted R6_V3 cost-log row; committed first so the merge started from a clean tree.

**Merges.** `git merge --no-ff r6v3` → 593018e `merge(R6_V3): r6v3`. No history rewriting, no tag, no push.

**Conflicts and resolution.** None (git merged cleanly; no register id or licence item collided).

**Registers (035dd03 and the status commit).** Assumptions +7 (A-r6-101…107 after A-r6-013, byte-identical; 659 → 666 ids); licences +1 (`HiGHS … [r6v3 use]` after the `[r6]` row) and the R0 `HiGHS` row's status replaced as the fragment instructs (old status recorded in the `docs/licences.md` note); CSV = Markdown, 267 rows, 0 differ; sources +0 (no r6v3 source file). Fragments deleted (history at 593018e); pointers repointed in `docs/r6-topology.md` v1.2 and the comment in `cities/ksa/assumptions/r6v3_variants.yaml` v1.2 (`config_hash` hashes the parsed YAML: identical before and after, measured).

**Data on main.** `runs/r6/top5` replaced with the track's v3 copy (main's v2 copy in `runs/_superseded/INTEGRATE_R6_V3/r6/top5`, identical to `runs/r6/top5-v2`); `runs/r6/v3`, `runs/r6/top5-v2`, `runs/r6/judge/v3-variants.hash.json` and `judge/v3-variants` (read-only, 2,090 files) APFS-cloned; `runs/skims/demo/meta.json` superseded and regenerated. `diff -rq` worktree vs main: nothing missing or different under `runs/`. `optimise.judge verify`: `v3-variants` intact d9fef64384e2e25f… (= `docs/r6/judge-hashes.md`), `v2-p5b` intact 2bdee7f5….

**Layouts.** No layout changed; the CP7 set for R7 stays `scenarios/S6-L1..L3.yaml` (unchanged since tag `r6`). R7 not started.

**Verification.** `make test` green: ruff, format, **481 passed** (473 → 481), docver, manifest 386 rows; about 24 s. README demo exit 0 in 2.2 s. `red-team-verifier` pass 1 on 035dd03: FAIL F1 (the YAML comment still named the deleted fragment); fixed in the status commit; pass 2 below.

**Coordinator addenda.** `add-paid` already present in `common/cost_log.py` with tests (no change).

**Status and changelog.** `docs/STATUS.md` v1.24: R6_V3 and INTEGRATE_R6_V3 milestone rows, INTEGRATE_R6_V3 decisions, R6_V3 open items (pruned surface, search caps, verifier observations, ODbL note), disk 37 GiB, cost USD 738.89 over 56 runs before this run's row; `CHANGELOG.md` r6v3 section.

**Verifier verdict.** `red-team-verifier` pass 2 on 1e5de78: **PASS** (F1 closed; `config_hash` of the YAML `f43700ee…` identical before and after; README demo meta `r6-15-g1e5de78`, clean); report `docs/status/verify-INTEGRATE_R6_V3.md` v1.1. Tests: 481 passed, `make test` about 23 s.

**Not done.** R7 not started (CP7 approved it; the coordinator launches it). R6_V3 open items (pruned track surface, NSGA-II restart cap, re-score selection, verifier observations, ODbL note on alignment sidecars) are carried in `docs/STATUS.md` Open issues, owner track r6v3 or R8.

Elapsed: about 00:54 to 01:50 (4 Nov) +03.

INTEGRATE_R6_V3: done

## INTEGRATE_R7 integration of track r7 (4 Nov 2026, builder on `main`)

**Inventory.** One R7 branch, `r7` (tip bfb2f43), last status line `R7: done` (verifier `docs/status/verify-R7.md` v1.1 PASS on pass 2). The working tree carried the uncommitted R7 cost-log row; committed first (4b0e00f) so the merge started from a clean tree.

**Merges.** `git merge --no-ff r7` → 0245b34 `merge(R7): r7`. No history rewriting, no tag, no push.

**Conflicts and resolution.** No git conflict. Four register ids collided by design: the R7 fragment's `[R7 update]` rows A-fund-002, -006, -007, -008 set values R1d had left "not set (R7)". Both rows kept: the updated row carries the id, the R1d row is suffixed `[pre-R7]` with a superseded note (INTEGRATE_R5 convention); listed in `docs/STATUS.md` (INTEGRATE_R7 decisions).

**Registers (4b7fd38).** Assumptions +9 new (A-fund-101…109 after A-fund-011, byte-identical) and 4 updated: 732 → 745 rows; licences +0 (no R7 licence fragment); sources +1 (S-fund-r7-001 into `docs/sources/index.csv`, `index.md` v0.12 regenerated; `docs/sources/r7-fund.csv` kept by precedent). `docs/assumptions-r7.md` deleted (history at 0245b34); pointers repointed in `funding/report.py`, `docs/fiscal-exposure.md` v1.2 and the comment of `cities/ksa/assumptions/funding_r7.yaml` v1.2. `uv run python -m common.manifest verify`: 386 rows OK.

**Data on main.** `runs/r7` APFS-cloned from the worktree, then moved to `runs/_superseded/r7-from-track-INTEGRATE_R7/` and rebuilt by the R7 pipeline on clean 4b7fd38 (about 3 min): `fiscal.json` and `vfm.json` byte-identical; matrices, `recommendations.yaml` and both generated docs unchanged.

**Verification.** `make test` green: ruff, format, **497 passed** (481 → 497), docver 300 files, manifest 386 rows; 26.8 s wall. README command `make setup && make test` and the README skim demo (2.4 s) exit 0. `red-team-verifier` on the merged state: **PASS** on all five criteria (`docs/status/verify-INTEGRATE_R7.md`); observations O1 (A-fund-003 still "not set") and O2 (stub `docs/assumptions-r2.md`) carried to `docs/STATUS.md` Open issues; O4 checked and found already closed on main (evidence in `docs/STATUS.md`). [Corrected by FIX_R7 item 2, 4 Nov 2026: this was not a closure. verify-INTEGRATE_R7 O4 is verify-R7 O16/O18, and verify-R7's final pass-2 list (HEAD `fef64ea`, §7.6) still carries O16 and O18 as open. Their code fix (d00ab76, 02:05) landed after that pass and no verifier had re-checked it; regenerating the matrices, `recommendations.yaml` and both docs from it is a no-op. FIX_R7 adds tests for both, and they close only on VERIFY_FIX_R7's PASS. verify-R7 O4 itself (the "docver 299" count) was closed by d00ab76 (`docs/status/r7.md` reads 301). Full open/closed list: FIX_R7 block below.]

**Coordinator addenda.** `add-paid` already present in `common/cost_log.py` with tests (no change).

**Status and changelog.** `docs/STATUS.md` v1.25: R7 and INTEGRATE_R7 milestone rows, R7 and INTEGRATE_R7 decisions, R7 open items, disk 35 GiB, cost USD 767.79 over 58 runs before this run's row; `CHANGELOG.md` r7 section.

**Not done.** The R7 checkpoint (coordinator wakes Tariq); tag `r7` by the coordinator.

Elapsed: about 02:07 to 02:50 (4 Nov) +03.

INTEGRATE_R7: done

## FIX_R7 R7-checkpoint fix pass (4 Nov 2026, builder on `main`, claude-opus-5-5)

**Estimate (first line, runaway guard USD 60):** about USD 25–40 of list-price tokens for this run (one builder session of about 3 h plus one foreground verifier); compute is local (alignment re-routing: v2 tuning grid 108 combinations × 3 lines ≈ 70 min on 4 workers, recorded here before the run per the 90-minute rule; the smaller-sample result came first: one v2 combination on SAR East, 9.21 → 2.74 km mean offset, and the v1 base reproduced at 9.208 km). [Trace added after VERIFY_FIX_R7 pass 1: the trial combination is grid combo 55 (dead-band 0.3, smoothing 1,000 m, straightness 0.05, corridor bonus 0.1, urban 1.5) in `runs/align/tune-v2-s1/grid.csv`, SAR East mean offset 2.735 km.]

Commits (one per item, on `main`): d7a117b (1), bfc38b5 (2), 321b42a (3), 686e8c0 (5), 308efdc (4), then the status/handoff commits. Every run of item 4 was re-run from the committed HEAD 308efdc and reproduced byte for byte (diagnosis, both v2 validations, v2 sidecars, compare, fiscal, VfM, sensitivity; `logs/fixr7-rerun.log`; the dirty-stamped first outputs are kept in `runs/_superseded/fixr7-dirty/`).

**Item 1 (A-fund-003).** The `docs/assumptions.md` row now reads value `derived (see docs/fiscal-exposure.md; A-fund-007/008/101/010)`, status `derived`; its source note is kept, with the FIX_R7 date. The R7 track note in the register is updated. No "not set" echo of it exists in `cities/ksa/assumptions/funding_*.yaml` or `funding/*.py` (grep: 0 hits). Test `test_a_fund_003_is_derived_not_unset`.

**Item 2 (recommendations basis, availability legal list, main.md correction).**
- `funding/recommend.py` already copies `fiscal_series_method` and `judge_fiscal_cost_p50_60y` into every corridor and programme `basis`, and `LEGAL_BY_MODEL["ppp_dbfom_availability"]` already lists `fare_setting_authority`. Commit d00ab76 did this at 02:05 on 4 Nov, after verify-R7's last pass.
- Regenerating the 30 matrices, `recommendations.yaml` and both docs through the generators was a no-op. The YAML header went to v1.2 (provenance only); the matrices are byte-identical, so they keep v1.1.
- Tests `test_recommendations_basis_carries_series_method_and_judge_cross_check` (8 entities) and `test_availability_ppp_lists_fare_setting_authority`.
- **Correction of the INTEGRATE_R7 claim** (bracketed note in the INTEGRATE_R7 block above and in `docs/STATUS.md`): "O4 checked and found closed" was wrong. verify-INTEGRATE_R7 O4 *is* verify-R7 O16/O18, and verify-R7's final pass-2 list (§7.6) still carries both. The code fix was never verified. They close on VERIFY_FIX_R7's PASS.
- verify-R7 observations, exactly:
  - **closed before this run:** O2 and O3 (pass 2); O1 (`docs/status/r7.md` ends `R7: done`, `docs/STATUS.md` R7 row, cost-log R7 row present); O4 (r7.md says 301, by d00ab76; main counts 300 after the fragment deletion, verify-INTEGRATE_R7 O5); O13 and O15 (INTEGRATE_R7 rebuilt `runs/r7` from a clean HEAD); O14 (d00ab76 bumped the headers; the generators still carry literal version strings, bumped by hand, as here).
  - **this run closes, pending VERIFY_FIX_R7:** O16, O18 (item 2); O5 and O6 (item 5, as heading notes; O5's suggestion to print the bid-contingency range as the PPP range is not done).
  - **still open, carried to R8 (not in the FIX_R7 scope):** O7 (L2 timing-split footnote), O8 (demand-concession quantile labelling), O10 (S-fund-016 duplicate row), O11 ("sourced, reference class" third state), O17 (template note on Art. 18).
  - **no action:** O9 ("about one-eighth" accepted), O12 (pre-existing tracked GASTAT tables).

**Item 3 (housekeeping).**
- `docs/assumptions-r2.md` is deleted. Before deleting I checked it: **0 table rows**; the 18 ids it names (A-r2-001/002, A-screen-040, A-corr-001…015) and all 82 region-prefixed rows are in `docs/assumptions.md`. `docs/versioning.md` §5 (v1.3) now says that summary pages go with the fragments.
- `docs/STATUS.md` line 103 (the CP3 list) gets the dated bracket "[superseded 1 Nov 2026: R4_ALIGN routed every candidate corridor on Copernicus GLO-30 (`docs/alignments.md`); R5 H4a re-routed 17 under the frozen weights]".
- A grep of `docs/` for "no DEM" / "proxy terrain" / "sketch" statements presented as current found three more, annotated the same way: A-corr-013 and A-corr-014 in `docs/assumptions.md`, and `docs/candidates.md` §3 (v1.2).
- The other hits describe the screening register's town terrain class, which R4_ALIGN did not change (`docs/alignments.md` §6), or historical status blocks. They are left as they are.

**Item 4 (alignment quality).**
- (a) **Diagnosis** (`network/align_diag.py`, run `runs/align/diag-v1-s1`, table in `docs/alignments.md` §4a). Each line's mean offset is split exactly by leg and cause:
  - **SAR East 9.21 km:** grade term on flat ground 8.12, urban approach 0.86, within 1 km 0.16, flat lateral freedom 0.08.
  - **SAR North 9.81 km:** grade term 8.29, unseen corridor 0.73, lateral freedom 0.46, urban approach 0.21, within 1 km 0.12.
  - **HHR 3.32 km:** urban penalty 1.82, urban approach 1.22 (the Makkah approach loop), within 1 km 0.14, unseen corridor 0.14.
  - The corridor bonus pulls the routed lines onto highways the real lines avoid. Protected areas and wadis are never the dominant cause.
- (b) **Weights v2** (`cities/ksa/assumptions/align_weights_v2.yaml`, SHA-256 `8da11430…`, frozen; A-align-100…104; diagnosis thresholds A-align-110…113).
  - Search: a 108-combination grid × 3 lines with leave-one-out (`runs/align/tune-v2-s1`). The in-sample choice is dead-band 0.3, smoothing 2,000 m, straightness 0, corridor bonus 0.1, urban 1.5.
  - Mean offset in km, v1 → v2 in-sample → v2 held-out:

| line | v1 | v2 in-sample | v2 held-out |
|---|---|---|---|
| HHR | 3.32 | 4.52 | 5.79 |
| SAR North | 9.81 | 5.54 | 11.46 |
| SAR East | 9.21 | 2.81 | 13.38 |

  - Length error, v1 → v2 in-sample (held-out in brackets): HHR −4.9 % → **−7.8 % (outside ±5 %)** (−7.9 %); SAR North +1.6 % → −0.7 % (−0.7 %); SAR East −0.3 % → −1.5 % (+0.9 %).
  - Tunnel and viaduct km per line are in §4b.
  - **The improvement does not hold out of sample** (every held-out line is worse than v1), so v2 is reported as a sensitivity and not proposed for adoption.
  - v1 is untouched: `align_weights.yaml` hash `2b718ecb…`, and 10/10 corridors re-routed with v1 on the new code are byte-identical (`logs/fixr7-v1check.log`).
  - No published reservation geometry exists in the sources register to use as a prior.
- (c) **CP7 corridors.**
  - `S3-branch_spur-al-kharj` and `S4-commuter_belt-riyadh-225` use DEM-routed alignments under the frozen v1 weights (sidecar `weights_hash` `2b718ecb…`, `weights_frozen: true`, run `runs/align/corridors-s1/<id>`). This is the R4_ALIGN routing; **neither is among the 17 R5 H4a re-routes** (`runs/align/r5-h4a-s1/`).
  - `S5-station_addition-duruma` is a station addition on existing or committed track and **is not routed** (§7 decision 4), so v1/v2 does not apply. Al Jubayl and Dhahran (S5) are the same.
  - v2 routing (`cities/ksa/alignments-v2/`):
    - Al-Kharj: length −0.5 %, tunnel + viaduct 2.0 → 0.6 km (−70 %), earthworks 4.8 → 12.3 km, running time 47.9 → 47.7 min.
    - Riyadh-225: length 79.0 → 69.5 km (−12.0 %), tunnel + viaduct 8.0 → 13.7 km (+71 %), earthworks 18.1 → 29.6 km, running time 34.8 → 31.0 min. The max formation grade stays at the 2.5 % cap for both.
  - Both crossed the thresholds and were re-run through the R5 cost estimator (`runs/costs-v2/`; v1 control identical) and the frozen judge v3. The judge ran through a hash-checked overlay root: 26 of 2,117 files substituted, judge code untouched, and an unmodified-clone control reproduces R7's Al-Kharj score exactly. Outputs: `runs/r7/corridors-v2/<id>@2050/`, layouts S6-L1 and S6-L3 in `runs/r7-v2/top5/`, fiscal and VfM in `runs/r7-v2/`.
  - **R7 figures that moved** (SAR m, PV 2026, robust case; synthetic demand, uncalibrated: scenario comparison, not a forecast):

| entity | robust NPV | capex P10 / P50 / P90 | fully public net fiscal cost 60 y P10 / P50 / P90 | VfM |
|---|---|---|---|---|
| Al-Kharj spur | 4,309 → 4,577 | 5,433 / 9,771 / 36,018 → 5,210 / 9,272 / 33,868 | 5,258 / 7,523 / 21,226 → 5,127 / 7,247 / 20,087 | −4,230 → −4,013 |
| Riyadh belt 225 | −8,293 → −7,778 | 4,717 / 8,910 / 34,256 → 5,202 / 10,227 / 40,520 | 9,130 / 11,320 / 24,551 → 8,571 / 11,194 / 27,008 | −3,860 → −4,432 |
| S6-L1 | 11,023 → 11,297 | 6,233 / 11,194 / 41,304 → 6,010 / 10,695 / 39,154 | 4,676 / 8,441 / 23,615 → 4,536 / 8,197 / 22,626 | −5,124 → −4,907 |
| S6-L3 | 2,426 → 3,180 | 10,684 / 19,630 / 73,799 → 10,946 / 20,448 / 77,912 | 12,696 / 18,962 / 45,343 → 12,103 / 18,478 / 46,529 | −8,779 → −9,135 |

  - Every VfM sign is unchanged. Al Jubayl, Dhahran, Duruma and S6-L2 do not move.
  - The availability-PPP net fiscal cost before/after is in `docs/alignments.md` §4c.
  - The v1 figures in both R7 docs, `recommendations.yaml`, `runs/r6/` and `runs/r7/` are untouched. Each affected table carries one "Alignment v2 sensitivity: see `docs/alignments.md` §4c" line: 9 lines (5 + 4), from `funding/report.py`.
- (d) The limitation sentence is in `docs/alignments.md` §0 and in `common.labels.ALIGNMENT_LIMITATION`, with a test and the CLI `uv run python -m common.labels alignment`.

**Item 5 (caveats in table headings).** `funding/report.py` now prints a heading note above every numeric table in both docs (`docs/fiscal-exposure.md` v1.3, `docs/delivery-models.md` v1.2):
- the synthetic-demand label on every table;
- "availability-PPP figures: P10 = P50 by construction (fixed price; capex enters only through the overrun above the cushion)" where PPP figures appear. Checked: P10 = P50 holds for all 8 entities at 30 and 60 y;
- the A-fund-108 caveat where expected values appear: "E[capex] ≈ 1.69 × P50", with the per-entity range (1.68–1.74) computed from each entity's own P90/P50.

The generated diff is heading notes, version headers and the item-4c lines only. Test `test_numeric_tables_carry_heading_notes`.

**Item 6 (tag).** No tag created. At this run `git show-ref` shows **no `r7` tag**: the provisional tag at 20746aa is already gone. There is a track **branch** `refs/heads/r7` (bfb2f43, checked out in its worktree), so re-creating the tag `r7` will make git print "refname 'r7' is ambiguous". Use `refs/tags/r7` explicitly, or remove or rename the branch.

**Tests and checks.**
- `make test` green: ruff, format, pytest **506 passed** (497 → 506; +9 in `tests/test_fix_r7.py`), docver 301 files, manifest 386 rows (no new download), about 26 s.
- Both frozen judges verify intact (v3-variants `d9fef643…`, v2-p5b `2bdee7f5…`).
- No new dependency, data download or licence item. The v2 sidecars carry the v1 sidecars' OSM/Copernicus/WorldCover attributions, so the ODbL release question of `docs/alignments.md` §2 applies to them unchanged.

**Cost estimate:** about USD 30–40 list price for this builder session plus the verifier (within the USD 60 guard). The coordinator adds the measured row to `docs/cost-log.md`.

**Provenance re-stamp (after VERIFY_FIX_R7 pass 1).** The v2 tuning grid was re-run in full from the clean HEAD 4e0e48c (`runs/align/tune-v2-s1`, meta `r6.1-22-g4e0e48c`). All 324 rows and `chosen.json` are identical to the first run, which had reused 43 rows from the interrupted 162-combination start; the first run is in `runs/_superseded/fixr7-dirty/`. Pass 1 found one FAIL, the missing closing line below, plus four observations, now fixed: `docs/STATUS.md` stale A-fund-003 open item struck; ranges on A-align-103/111–113; the 2.74 km trial traced to grid combo 55; the cost-log row stays with the coordinator.

FIX_R7: done

VERIFY_FIX_R7: done

## INTEGRATE_R8 integration of track r8 (4 Nov 2026, builder on `main`)

**Inventory.** One R8 branch, `r8` (tip 7f6b61d), last status line `R8: done` (verifier `docs/status/verify-R8.md` PASS on pass 2). Main had three coordinator commits since the branch point (cost-log rows, orchestrator v1.6, the R8-review decisions and this prompt v1.2); the tree was clean.

**Merges.** `git merge --no-ff r8` → 2ae4fa9 `merge(R8): r8`. No history rewriting, no tag, no push.

**Conflicts and resolution.**
- Git: one, the `docs/STATUS.md` header line (main's v1.29 with the coordinator's "R8 review decisions" entry vs r8's v1.29 with the "R8 builder" entry). This run owns `docs/STATUS.md` (task 5; precedent INTEGRATE_R3/R5/R6), so both author lists were kept in one header, v1.30. No other file conflicted.
- Register level: one licence item collision, `MapLibre GL JS` (R0 row "5.x, planned; unverified" vs the R8 row "5.24.0, verified"). Both rows kept: the R8 row carries the name; the R0 row is `MapLibre GL JS [pre-R8]` with "superseded by the verified row MapLibre GL JS (R8), kept for history". Logged in `docs/STATUS.md` (INTEGRATE_R8 decisions). No assumption or source id collision (R8 wrote no such fragment).

**Registers (0861ad8).** Licences +22 (19 from `docs/licences-r8.csv`, 3 from `docs/licences-r8-figures.csv`): 268 → 290 rows in `docs/licences.csv`; `docs/licences.md` v1.9 regenerated (`common.licences sync`; check 290 = 290, 0 differ) with "R8 track notes"; the four fragment files deleted (history at 2ae4fa9). Assumptions +0, sources +0. Pointers to the deleted fragments repointed in `docs/licences-release.md` v0.3, `docs/report/figures/README.md` v1.2, a note string in `common/figures.py` and `NOTICE`. `uv run python -m common.manifest verify`: 386 rows OK.

**Data on main.** R8 re-ran `runs/r7/vfm` (verify-R7 O11, 7c5bf07): main's copy moved to `runs/_superseded/INTEGRATE_R8/r7/vfm/`, the track's APFS-cloned in; `diff -rq .worktrees/r8/runs runs` then shows nothing missing or differing outside `_superseded` (only the judge-root symlink loops are reported). Nothing downloaded; disk 34 GiB free.

**Tariq's R8-review items (prompt v1.2, "Added 4 Nov 2026").**
1. Google Chrome 156.0.8078.81 registered as approved local tool ("Tariq, 4 Nov 2026 (R8 review)"); the flag is closed in `docs/licences-release.md` §2 and the generated table grades it OBLIGATIONS (proprietary, approval recorded). Screenshots not retaken. (0861ad8)
2. (a) `funding/report.py`: `f0` rounds half away from zero and the options tables read the unrounded `fiscal.json` values, not the 0.1-rounded `recommendations.yaml` copy (the double rounding 14,611.498 → 14,611.5 → 14,612). `docs/delivery-models.md` v1.4 prints 14,611 as the report and brief do; side effect S6-L3 demand-risk P90 26,284 → 26,283 (file 26,283.49); `docs/fiscal-exposure.md` unchanged; rule stated once in the intro; `tests/test_integrate_r8.py` (2 tests). (51d80ba) (b) `docs/r6-topology.md:112` now says "the builder (the optimiser track)"; `docs/plan.md` §0 "Fable review" → "verifier review". The prompt's grep is not literally empty; every remaining hit is a repository path or file name (`.claude/…`, `CLAUDE.md`), the CLI `claude -p` in an internal note, the `opus4.kobv.de` source URL, the internal `docs/STATUS.md` log or the plan's exempt run table and cost estimate (`docs/plan.md:93–110`); classified in `docs/STATUS.md` and accepted by the verifier as defensible (O2). (b7976ff)
3. `docs/executive-summary.ar.md` v0.3: `Status: draft, pending native review` and the review line under the title; mirrored in the CP6 package list and `docs/licences-release.md` §6. (f22a897)
4. R9/R10 not started, prompts unedited; the sentence is in `docs/STATUS.md`; the USD 60 guard stays and the one-off R8 clearance (USD 62.67) is in the decisions block.
5. Milestone row: "R8 done; CP6 review package ready (the brief's CP6; session R8 checkpoint)".

**Coordinator addenda.** `add-paid` already present in `common/cost_log.py` with tests (no change).

**Verification.** `make test` green: ruff, format, pytest **664 passed** (506 → 664: R8's tests and 2 new), docver 335 files, manifest 386 rows; about 33 s. README command `make setup && make test` and the README skim demo (2.3 s) exit 0. `red-team-verifier` on the merged state (HEAD 00aa02a): **PASS** on every criterion (`docs/status/verify-INTEGRATE_R8.md`). Observations: O1 (this block and the cost-log row are run-end items: this block closes the first; `run_track.sh` appends the row); O2 (the `docs/plan.md` v0.12 header quoted the removed label: reworded in the closing commit; `docs/plan.md:110` stays under the CP3 7a exemption of the plan's run table and cost estimate). `web/node_modules` is not installed on main (gitignored), so `tsc` and `make dashboard` were verified by the verifier on the byte-identical sources in the r8 worktree.

**Status and changelog.** `docs/STATUS.md` v1.30: R8 and INTEGRATE_R8 rows, INTEGRATE_R8 decisions, R8 open items, disk 34 GiB, cost USD 858.38 over 62 runs (28.49 agent-hours) before this run's row; `CHANGELOG.md` r8 section. (00aa02a)

**Not done.** The R8 checkpoint (the brief's CP6 review: the coordinator wakes Tariq); tag `r8` by the coordinator (use `refs/tags/r8`: a branch named `r8` exists).

INTEGRATE_R8: done

## FIX_R8 R8-checkpoint fix pass (5 Nov 2026, builder on `main`)

**Cost estimate (first status line):** about USD 35–50 list price for this run plus the verifier, under the USD 60 single-run guard. The coordinator adds the measured row to `docs/cost-log.md`. No paid model or API, no push, no tag, no server started; R9/R10 and their prompts untouched; TrafficTwin not touched.

**Commits (one per item, on `main` from tag `r8`):** item 1 b15e174; item 3 ac9a3dd; item 2 eee53dd; item 9 c6c4250; item 4 8d4df99; item 7 71519ec; item 8 0814a3d; register `used_in` follow-up for items 4/8 d122b08; this block and the verifier report in the closing commit. Items 5 and 6 are the coordinator's (not done here).

### Changes per item
1. **fig09 title.** `common/figures.py` spec: EN `Phasing (2030, 2050) and stage gates (2027, 2047)`, AR `المراحل (2030 و2050) وبوابات القرار (2027 و2047)`. Rebuilt with `common.figures build` (report and deck fig09 share the spec; only fig09 changed byte-wise), so `docs/deck-figures/figures.csv`, `docs/report/figures/figures-index.csv` and the report caption follow. `common.report build`: the assembled report header now has its own version (`MAIN_REPORT_VERSION`, additive in `common/report.py`), v1.1 → v1.3 over items 1, 9, 7. Test `tests/test_fix_r8.py::test_fig09_title_in_spec_and_deck_csv`.
2. **Glossary.** `docs/glossary.ar.md` v1.1: 28 terms, each with the preferred form, rejected forms and the source (23 verbatim from Tariq, 5 builder-proposed for consistency and marked so: survey = `استبيان ميداني` so that `مسح` is never used; reach = `التغطية`; the 9b and 9c forms; `في النموذج`), plus §typography (item 4). Applied to every Arabic deliverable found by grepping for Arabic script: the AR summary; the AR figure titles fig05 (`البرنامج الملتزم به`), fig06 (`الحالة الأعلى عائداً`, was `المتفائلة`), fig08 (`التغطية`), fig11 (`الشراكة بين القطاعين العام والخاص بنظام مدفوعات الإتاحة`), rebuilt through `common.figures`. `web/` has one Arabic string (`الاسم`, a register column header; no glossary concept), `api/` none, `docs/report/**` only place names and quoted Arabic source titles (out of scope, stated in the glossary). `tests/test_glossary_ar.py` (49 tests): each preferred form is in the AR summary wherever the EN summary uses the concept; 23 rejected forms (`أجور`, `مسح`, `المتفائلة`, `متين`, `القيمة الحالية الصامدة`, `اصطناعي`, `المُحكِّم`, bare `البذرة`, `فرع الخرج`, bare `مجلس التعاون`, bare `الملتزم`, …) absent from the summary, the figure titles and Arabic strings in `web/`/`api/`; robust NPV glossed exactly once, at first use.
3. **AR summary** v0.4 (then v0.5–v0.7 by items 2, 9, 4): every replacement of the prompt applied verbatim: `إيرادات التذاكر` (L44), `الجهة التي تحدد تعرفة تذاكر الركاب` (L56), `فرز جميع المناطق والمحافظات` (L18), labels `طلب تركيبي غير مُعايَر` / `ومسارات الخطوط مخططات تقريبية استرشادية بأقل تكلفة على نموذج تضاريس بدقة 30 م` / `أزمنة الرحلة` (three label lines and the reading note), `نموذج التقييم judge v3` and `بالبذرة العشوائية 1` (L12 and the table head), `عبر جميع نطاقات المَعلَمات المسجَّلة`, `الشراكة بين القطاعين العام والخاص بنظام مدفوعات الإتاحة`, `التزام محتمل (طارئ)`, `هامش الحماية لدى الشريك الخاص`, `صافي التكلفة على المالية العامة` (L44), `حزام لقطارات الضواحي حول الرياض`, `بديل التغطية الأوسع` (L38, the table and the bullet), `الخط الفرعي إلى الخرج` (first mention, the table row, and wherever Al-Kharj is named), the WEIs sentence verbatim (L58), `ضمن عقد طرح الخط المضيف` (L56), `سكة حديد دول مجلس التعاون الخليجي` (L16), the Arabic draft note under the English one (L5). Unit on the spur figure: AR `4,231 مليون ريال`, EN `SAR 4,231 m`; the brief, report and `docs/r6-topology.md` got the unit with the item 9b rewrite. Bilingual check: 254 = 254 after item 3; **258 = 258** now (item 9 added `S6-L2` to both sides of the 9b sentence).
4. **RTL render check.** New `common/ar_render.py` (additive): Markdown → standalone HTML (`lang="ar"`, `dir="rtl"`, Noto Naskh Arabic and Noto Sans linked from `common/fonts/`) with markdown-it-py; PDF, screenshots and a table crop with the approved local headless Chrome; and `bidi-probe`, which lays the page out in Chrome and measures the on-screen x position of every character of every numeric run. **Before** (`runs/fix-r8/ar-render/before/`, tag-state text plus items 1–3, 9): **23 of 35 numeric runs out of order**: the U+2212 minus drawn right of its digits (`2,958−`), ` / ` triples (`−2,958 / −724 / +1,631`, `801 / 1,423 / 5,286`, `P10 / P50 / P90`) and `3–10` laid out right to left (P10 where an English reader expects P90), and the English and Arabic label lines merged into one mixed-direction paragraph. **Fix in the source** (glossary §typography): every numeric run (signed number, ` / ` or `–` range, quantile label) wrapped in U+2066 … U+2069 by `isolate_numeric_runs`; a bare `>` line between the English label line and its Arabic rendering; no Arabic word in the version header. **After: 0 of 29 runs out of order** (the six fewer are the English label lines, now their own LTR paragraphs). `common/sources.py` (additive): a directional isolate before a dash still marks a sign, so the bilingual check reads through isolates. Committed: `docs/report/figures/executive-summary.ar.html` (17.6 KB), `docs/report/figures/ar-render-page1.png` (411 KB, first screen 900 × 1273 CSS px at 1.5×) and `docs/report/figures/ar-render-table.png` (90 KB, options table cropped from the full-page capture by its rule colour); PDF, full-page capture and probe JSON (before and after) under `runs/fix-r8/ar-render/` (gitignored). `tests/test_ar_render.py` (4 tests): every numeric run of the AR summary is inside an isolate; HTML is RTL with the bundled font and under 300 KB; the probe flags unisolated runs and passes the committed HTML (skipped where Chrome is absent). Licence register: markdown-it-py and Google Chrome `used_in` extended (no status changed; `docs/licences.md` v1.10, 290 = 290, 0 differ).
5. (Coordinator) not done here. 6. (Coordinator) not done here; no server started.
7. **Wording.** `docs/plan.md` v0.13 §6 (line 110): "Opus-class", "Haiku-class", "verifier" runs, arithmetic unchanged (the run table at lines 93–104 stays under the CP3 7a exemption). `docs/report/sections/00-front-matter.md` v1.1: "The study compares options for extending Saudi Arabia's rail network: which corridors, in what order, at what cost, with what long-term benefit, funded and owned by whom, and with what effect on people." Report rebuilt; `common.report check` PASS.
8. **Licence blockers.** `docs/licences-blockers.md` generated by the new `common.licence_blockers` (same `release_status` rule as the release note; B1–B9 questions quoted from its §1; model ids redacted as in the release table). **Count: 46 BLOCKER rows** of 290. The prompt cites 48; no committed version shows 48: the R8 track's note (c97f724, b412f77) had 47 and the INTEGRATE_R8 note has 46, the difference being Google Chrome, closed by Tariq's approval. By group: press and secondary fact pages 21; statistical extracts with unclear terms 9; databases with non-commercial or all-rights-reserved terms 2 (Transit Costs Project, EPSG); CC BY-SA share-alike 6; ODbL derivative question 2 (B7, alignments-v2); models and voices 3 (B8 orchestrator row, Coqui XTTS-v2, B9 Nabrah); fonts and media 0; other 3 (xlogit, Schittenhelm 2011, B5 CE Delft). **Transit Costs Project: HARD STOP** at the top. Dependency scan of `docs/` (status logs excluded), `cities/ksa/benchmarks/` and 1,975 run metas: 16 hits, **none a figure, table, benchmark row or run value**: source-index citation S-cost-civil-018 (`docs/sources/index.csv:1360`, `index.md:1369`, `cost-civil.csv:19`, `report/annex-sources.md:1367`), the "searched, not used" notes for cost row C-line-type-commuter-atgrade-034 (`docs/costs.md:273`, `docs/sources/cost-notes-civil.md:32, 72, 96`; the register row has low/central/high null, status unknown), the A-cost-013 reason text (`docs/assumptions.md:194`, `report/annex-assumptions.md:194`), and the licence register and release note rows; the run metas and `cities/ksa/benchmarks/` have no hit. No status in `docs/licences.csv` changed (test compares licence, open, commercial use, status and approval of every row with tag `r8`).
9. **Wording checks** (tables below; tests `tests/test_fix_r8.py`: S1 NPV in a block or heading with "in the model"; every `4,231` sentence says "difference" and has no additive phrasing; every 120-minute reach sentence says five metros, national reach says "reported only").

**9a. S1 negative NPV** (grep `−337,555`, `−60,103`, `60,103`, `does not pass`, `لا يجتاز`, `سالب`):

| file:line | occurrence | "in the model" | action |
|---|---|---|---|
| docs/executive-summary.en.md:13 | −337,555 / −60,103 | same sentence ("In the model S1 itself…") | none |
| docs/executive-summary.ar.md:18 | −337,555 / −60,103 | same sentence (`وفي النموذج يبلغ…`) | none |
| docs/executive-summary.ar.md:39, 40 | `سالباً` | S6-L1 and S6-L3 at P90 cost, not S1 | n/a |
| docs/policy-brief.md:33 | table row −337,555 / −60,103 | missing in the table head and heading | **fixed**: head "committed programme S1 vs S0, in the model" (v0.3) |
| docs/report/sections/01-executive-summary.md:16 (report :121) | "does not pass in the model", −60,103 | same sentence | none |
| docs/report/sections/04-results.md:25 (report :305) | gen:s1 table row | paragraph above ("In the model, S1 against S0…") | strengthened: `gen_s1` head "NPV in the model, P10 / P50 / P90" |
| docs/report/annex-assumptions.md:445, annex-regions/madinah.md:18 | `60,103` = AlUla population | not an NPV | n/a |
| docs/deck-figures/figures.csv | none | | |

**9b. Al-Kharj 4,231** (grep `4,231`, `4231`): confirmed as robust NPV S6-L1 − S6-L2 = 11,022.94 − 6,791.61 = 4,231.33 from `runs/r6/top5/top5.csv` (`robust_npv`) and `runs/r6/top5/L1/score.json`, `L2/score.json`; `runs/r7/corridors/S3-branch_spur-al-kharj@2050/score.json` scores the spur alone over S1 at a robust NPV of 4,309.15, so the two differ and the figure is not an additive share.

| file:line | before | after |
|---|---|---|
| docs/executive-summary.en.md:32 | "about 4,231 of it from the spur" | "the difference between S6-L1 and the same layout without the spur is SAR 4,231 m of robust NPV; that layout is S6-L2" |
| docs/executive-summary.ar.md:39 | `يعود نحو 4,231 منه إلى الفرع` | `الفرق بين S6-L1 والمخطط نفسه دون الخط الفرعي إلى الخرج هو 4,231 مليون ريال من صافي القيمة الحالية الصامد؛ وذلك المخطط هو S6-L2` |
| docs/policy-brief.md:61 | "of which about 4,231 is the spur (L1 minus L2)" | "the difference between S6-L1 and the same layout without the spur (S6-L2) is SAR 4,231 m of robust NPV" |
| docs/report/sections/01-executive-summary.md:19 (report :124) | "About 4,231 of its 11,023 is the spur" | "The difference between S6-L1 and the same layout without the spur is SAR 4,231 m of robust NPV (S6-L1 − S6-L2, …)" |
| docs/report/sections/04-results.md:99 (report :379) | "about 4,231 of its 11,023 is the Al-Kharj spur" | "the difference between S6-L1 and the same layout without the spur (S6-L2) is SAR 4,231 m of robust NPV (11,023 against 6,792)" |
| docs/r6-topology.md:80 | "Of L1's 11,023, about 4,231 is the spur (L1 − L2)" | difference wording plus the 4,309 standalone score as the reason it is not a share (v1.4) |
| docs/r6-topology.md:45 (VERIFY_FIX_R8 pass 1: "SAR 4.2 bn of the 11.0 bn", a spelling the `4,231` grep missed) | "its value hangs on the Al-Kharj spur (SAR 4.2 bn of the 11.0 bn)" | "(the difference between S6-L1 and the same layout without the spur, L2, is SAR 4,231 m of robust NPV)" (v1.5); the test now also matches `4.2 bn` / `4.2 billion` and "of the 11" / "of its 11" |

**9c. 120-minute reach** (grep `120`, `3.56`, `4.25`, `5.30`, `دقيقة`, A-r6-104; full list `logs/fixr8-wording-c.txt`): qualified already (no change): EN summary none; brief :59; report 01:20; 03:97 (national reach "reported column only"); 04:93, :100, :169, :183 (fig08 caption); figures-index fig08. **Fixed** (qualifier added): EN summary :33 and AR summary :40 (`من الباب إلى الباب من المدن الخمس الكبرى`); brief :63 (twice), :65, :117; report 01:21 (5.30 M), 04:171 (S6-L4/L5 reach defined once in the sentence), 07:27 (reach gain); fig08 y-axis "…of the five metros" (rebuilt); national reach 04:187 now "reported only (a column outside the score, A-r6-104)". After VERIFY_FIX_R8 pass 1 (observation): `docs/r6-topology.md:99` layout-table head "Reach gain, 120 min door to door from the five metros". Not the reach measure (left as is): `40–120 road-km` (02:20, 04:205, 04:209: the 30-minute lens band) and the fig12 Dammam 120-minute isochrone band in `common/figures.py`.

**Tests and checks.** `make setup && make test` (the README command) exit 0: ruff, format, **pytest 724 passed** (665 at the start of this run, i.e. INTEGRATE_R8's 664 plus the cost-log test of 711742f; +59: `test_glossary_ar.py` 49, `test_ar_render.py` 4, `test_fix_r8.py` 6), docver 339 files (340 with the verifier report), manifest 386 rows; about 38 s. `common.sources bilingual-check` 258 = 258 PASS; `common.report check` PASS; `common.licences check` 290 = 290, 0 differ.

**Verifier.** `red-team-verifier`, label VERIFY_FIX_R8, foreground, report `docs/status/verify-FIX_R8.md`. Pass 1 (HEAD 576d883): **FAIL** on 9b only: `docs/r6-topology.md:45` still framed the spur as "SAR 4.2 bn of the 11.0 bn", a spelling the `4,231` grep missed; everything else PASS, including all 25 Arabic strings of the prompt matching character by character, the independent recount of 46 BLOCKER rows, the Transit Costs Project dependency scan, no licence status changed against tag `r8`, R9/R10 and `film/` untouched, idempotent figure and report rebuilds, bidi probe 23/35 → 0/29 reproduced. Fixed in bab5eda (wording, the layout-table head at :99 from the observation, and the 9b test widened to the bn spellings; the widened test fails on the old file). Pass 2 (HEAD bab5eda): **PASS**. Open observations (no FAIL): the cost-log row for this run is the coordinator's; `docs/plan.md:93–104` run table keeps model labels under the CP3 7a exemption.

**Screenshots for Tariq (item 4):** `docs/report/figures/ar-render-page1.png` and `docs/report/figures/ar-render-table.png`; before-state captures in `runs/fix-r8/ar-render/before/` (gitignored).

**Not done (by design).** Items 5 and 6 (coordinator); no tag, no push; R9/R10 not started.

FIX_R8: done

## FIX_R8_RTL RTL wrap fix for the Arabic executive summary (6 Nov 2026, builder on `main`)

Cost estimate (runaway guard USD 60): about USD 15–25 list price for this run including the verifier. Scope: the residual of FIX_R8 item 4 only. No tag, no push, R9/R10 and `film/` untouched, no licence status changed, no paid model or API.

**Commits.** Items 1 and 2: 104e58c (one commit: both items live in the same canonical `isolate_numeric_runs`, which first removes the existing LRI/PDI marks and then sets every isolate again, so a split commit would have left a non-idempotent intermediate state). Item 3: 4bbc194. This block and the verifier report go in the closing commit.

### What changed
1. **No break inside a numeric run** (`common/ar_render.py`, `docs/executive-summary.ar.md` v0.8, `docs/glossary.ar.md` v1.2 §typography):
   - **Source.** Inside every run the spaces around ` / ` (and a spaced `–`) are now U+00A0. A fully numeric parenthetical moves inside its isolate (`⁦(P10 / P50 / P90)⁩`). The table headers keep the Arabic words outside and only the label triple inside.
   - **Rendering.** `md_to_html` wraps every isolate in `<span class="nr">` with `white-space: nowrap`.
   - **Idempotent.** `isolate_numeric_runs` is canonical, so running it twice changes nothing (tested on every line of the AR summary). It also migrates the old `(⁦…⁩)` form.
   - **Bilingual check.** U+00A0 was already in `common.sources._SIGN_OK_BEFORE`, so `common/sources.py` is unchanged. Bilingual check: **258 = 258**.
   - **Probe.**
     - `bidi-probe` now runs at 900 px plus the narrow widths 480 and 360 px (`--viewports`). Headless Chrome's window cannot go below 500 px (measured: a 480 or 360 window lays out at 500), so each width is set on the root element (`html { width: Npx }`) and the probe fails if the measured root width differs.
     - The run pattern now includes a fully numeric parenthetical with its parentheses, even when the isolate sits inside them (the old form).
     - A run broken across lines **fails** even when its fragments keep LTR order and read top to bottom. That is stricter than the prompt's exception, and deliberate: Tariq's three cases were exactly such ordered fragments, which an RTL reader still meets slash-first. `order_ok` in the JSON keeps the prompt's weaker reading.
2. **Year and citation** (same commit):
   - **Isolation.** Every inline footnote reference `[^S-…]` (not a definition `[^S-…]:`) is its own LTR isolate placed directly after what it cites.
   - **Probe.** It now checks every footnote marker in RTL text: the marker must be on the same line as the word or number it follows, and to its left (the reading-order side).
   - **Pairs handled (5):**
     - `الكتاب الأخضر 2026⁦[^S-cp1-060]⁩` (§0, the number–marker pair Tariq named; the only `<number><marker>` pair)
     - `قيد الطرح⁦[^S-054]⁩⁦[^S-r1a-055]⁩⁦[^S-029]⁩` (§1: a word followed by three markers, each its own isolate, in sequence)
     - `بريطانية⁦[^S-fund-r7-001]⁩` (§3)
   - **Ids.** The AR summary has no `<id>[^S-…]` pair (no S6-/A- id carries a footnote), so none needed handling.
   - **Finding (before).** Headless Chrome at 900 px already drew the marker left of 2026. The probe found 0 of 5 markers misplaced on the old HTML at every width. The swap Tariq saw comes from `2026[S-cp1-060]` reading as one LTR token. In a renderer that turns the marker into a digit superscript (GitHub-style footnotes), the year and the marker would merge outright. The isolate fixes this in any renderer.
3. **Rebuilt** with the approved local headless Chrome:
   - `docs/report/figures/executive-summary.ar.html` (18.7 KB)
   - `ar-render-page1.png` (412 KB; first screen 900 × 1273 CSS px at 1.5×, as before)
   - `ar-render-table.png` (89 KB; table cropped from a full-page capture by its rule colour, as before)
   - No zoom images added. The PDF, full-page capture and probe JSON/TXT before and after are in `runs/fix-r8-rtl/` (gitignored).
   - **Visual check of the three cases (zoomed crops):**
     - §1 now ends `…مليون ريال (P10 / P50 / P90)` with the parenthetical whole on one line.
     - The S6-L1 cell reads `−2,958 / −724 / +1,631` on one line.
     - The benefits-to-cost header reads «نسبة المنافع إلى التكاليف» / `P10 / P50 / P90،` / «متوسط», with the triple whole.

### Probe table (numeric runs out of order, including wrapped; footnote markers misplaced)
"Before" is the committed v0.7 HTML (HEAD 0af76c5), measured with the new probe. Under the old probe it showed 0 of 29 at 900 px only, because the old probe accepted ordered wraps and did not see the parentheses.

| Viewport | Runs | Before: out of order (of which wrapped) | After: out of order (wrapped) | Markers | Before misplaced | After misplaced |
|---|---|---|---|---|---|---|
| 900 px | 29 | 8 (7) | 0 (0) | 5 | 0 | 0 |
| 480 px | 29 | 14 (13) | 0 (0) | 5 | 0 | 0 |
| 360 px | 29 | 15 (14) | 0 (0) | 5 | 0 | 0 |

The extra non-wrapped failure in each "before" row is `(P10 / P50 / P90)` in §1: with the parentheses outside the isolate, the RTL paragraph mirrored them around the LTR triple. Sources: `runs/fix-r8-rtl/before/probe.txt`, `runs/fix-r8-rtl/after/probe.txt`.

### Tests
`tests/test_ar_render.py`: 4 → 12 tests.
- idempotent isolation and migration of the old form
- no plain space around `/` or `–` inside any isolate, and every isolate in a nowrap span
- inline footnote markers isolated, the 2026 pair included
- the bilingual check reads through NBSP (token test and the real EN/AR pair)
- the probe returns 0 failures and 0 wraps at each of 900/480/360 px on the committed HTML
- the probe flags an ordered but wrapped run at 360 px, and passes the same run from `isolate_numeric_runs`
- the probe flags a marker after `S6-L1` without an isolate, and passes it with one

`make test`: ruff, **732 passed**, docver OK, manifest OK (386 rows).


**Verifier.** `red-team-verifier`, label VERIFY_FIX_R8_RTL, run in the foreground; report in `docs/status/verify-FIX_R8_RTL.md`. Pass 1 (HEAD 4bbc194): **PASS** on all seven criteria. It reproduced the probe before/after byte for byte (8/14/15 → 0/0/0, markers 0), judged the `html { width }` emulation sound and the strict wrap rule consistent with the brief, and visually confirmed Tariq's three cases and the 2026 marker. It also confirmed idempotence on all 69 lines, the bilingual check at 258 = 258, a wording diff limited to the version header, and the scope (seven files plus status; `common/sources.py`, licences, R9/R10 and `film/` untouched; no tag). Open notes (no FAIL): the cost-log row for this run belongs to the coordinator (from the run's JSONL). Any before-probe copy must sit three levels deep so that the font href resolves.

**Screenshots for Tariq:** `docs/report/figures/ar-render-page1.png` and `docs/report/figures/ar-render-table.png`.

FIX_R8_RTL: done

## FIX_HHR_JEDDAH phantom HHR chord in Jeddah + station-siting rule (6 Nov 2026, builder on `main`)

Cost estimate for this run: USD 25–40 list price (runaway guard USD 60); the coordinator logs the actual cost from the run's JSONL. Rules kept: no tag, no push, no R9/R10 (`prompts/` and `film/` untouched), no licence status change, no paid model or API. TrafficTwin was only read. No station was moved and no corridor was re-scored. **Nothing in R4_ALIGN or R5–R8 was re-run.**

### Item 1: HHR geometry (commits 4b9eb7f, 86b6bcc, da98a9d)
**Cause.** `rail.lines build` appended the KAIA branch path to the main LineString. The result jumped 17.32 km from KAIA (index 376) back to Al-Sulaimaniyah (index 377) and drew the Al-Sulaimaniyah–junction stretch twice (vertices 266–320 = 377–431).

**Fix.** Branch stations now form their own part, cut at the junction (`rail.lines.branch_parts`). HHR is a MultiLineString `main` + `branch` (`parts`, `part_to`, `part_km`); every other line stays a LineString, byte-identical. km-posts, `hhr.yaml` and all 153 stations are unchanged (the 14 located stations were preserved; only `stations.geojson` `generated` changed). `rail.lines validate`: 15 files, 0 errors; `common/schemas.py` needed no change, because shapely already reads MultiLineString. `network.align.osm_line` now returns the main part of a MultiLineString, a compatibility guard so that a future re-run does not crash; it was not run here.

**Visual check.** Visual check, Copernicus Sentinel-2 L2A S2B_37QED_20261027, 6 Nov 2026: the OSM branch follows a visible track from the junction south of the interchange, west along the highway, then north-west into KAIA. No line runs straight from the city to the airport. Manifest row `sentinel-2-l2a-cogs-hhr_kaia_branch` (gitignored cache); no imagery committed.

| | before (0cc369e) | after |
|---|---|---|
| geometry | LineString | MultiLineString (main, branch) |
| vertices | 1,100 | 989 + 57 |
| measured km | 484.59 | main 448.54 (= km-post span; 453 `length_km` −0.98 %); branch 6.69 |
| stitch | index 376 → 377, 17.32 km | none |
| repeated vertices | 55 | 0 |

The old 484.59 km = 448.54 main + 12.04 duplicated + 6.69 branch + 17.32 stitch. **Deviation from the acceptance criterion "branch ≈ 3.75 km ± 20 %":** OSM measures 6.69 km from the junction (main way 629481003 meets branch way 868371679), and the OSM graph has no shorter connection to the main line. The test pins 6.69 km, and the difference is logged as conflict **C-fixhhr-001** (S-002 3.75 km, secondary; open).

**Second deviation.** "No vertex jump > 2 km anywhere in `existing.geojson`" cannot hold literally: there are 402 segments over 2 km. All 402 join consecutive nodes of one OSM way (straight track over open ground), and a test checks exactly that against the OPL. The stitch test (a long segment that re-enters the drawn line without retracing it) passes on every line and catches index 376 on the old file. Observation, out of scope: `sar-east-freight-legacy` (9 vertices, Al-Ahsa) and `sar-north-freight` (24 vertices, near Hail) retrace short stub track out and back into a station. That is real track, not a chord.

**Figures.**
- `common.figures build`: only fig01 and fig12 (report and deck) changed, because they draw `existing.geojson`. The other 13 figures and `figures-index.csv` are byte-identical, and a second build is idempotent.
- `dashboard-map.png` was re-captured with the approved Chrome (`make dashboard`, `npm run screenshot dashboard-map`): byte-identical at national scale.
- No report caption or index entry changed.
- Before/after screenshots: `docs/report/figures/hhr-jeddah-before.png` (121 KB) and `docs/report/figures/hhr-jeddah-after.png` (108 KB), from `uv run python -m common.figures jeddah-hhr --geojson <file> --out <png>`, an additive helper. Both carry the OSM credit and the layer legend.

**Length-dependency table** (full version in `docs/network.md` §HHR geometry; reproduce with `uv run python -m rail.hhr_check --before-rev 0cc369e` → `runs/fix-hhr/check.json`).

| consumer | used | moves? |
|---|---|---|
| km-posts (`rail/lines.py`), `hhr.yaml` `length_km` 453 | (b) km-posts / 453 | no |
| R1a/R3/R4 rail graph, skims, running-time gate H1a −12.2 % | (b) | no |
| R5–R8 CBA, R6 topology, report, brief, summaries | (b) via the graph; routed corridor lengths from R4_ALIGN | not directly; yes through the routed alignments (corridor bonus and weights, below) |
| R4_ALIGN length check "HHR 426.6 vs 448.5 km" (−4.9 %) | (b) km-post span | no |
| **R4_ALIGN HHR offsets** (`runs/align/validation-s1`, `docs/alignments.md` §4, `docs/alignments-tables.md` §1) | **(a) stitched** | **yes**: mean 3.317 → 3.399 km (main + branch) / 3.432 (main only); p90 7.664 → 7.757 / 7.774; `osm_km_clipped` 483.331 → 454.070; bridge share 9.13 % → 9.72 %, tunnel 1.93 % → 2.05 % (km unchanged with the branch: 44.122 / 9.311) |
| **R4_ALIGN corridor bonus** (`network/align.py` `_rail_geoms` → `rail_mask`; every hypothetical corridor) | **(a)** | **yes, directly** (verifier finding): routed vertices in the chord's band: `S4-commuter_belt-jeddah-315` (6), `-000` (5), `-045` (1), `S2-trunk_gap-riyadh-jeddah` (1). Belts 000/315 are in S6-L5; CBA cases exist for 000, 315 and Riyadh–Jeddah; effect size unknown until re-routed |
| **A-align-070 tuning objective, weights v1 (7.446 km)** | (a) | **yes**: about 7.473 at the frozen weights; whether re-tuning picks other weights is unknown. The weights feed every routed corridor → R4–R8 lengths, costs, CBA |
| **FIX_R7 weights v2** (in-sample 4.842; held-out HHR 5.79, A-align-100) | (a) | **yes**: in-sample HHR 4.517 → 4.641; held-out 5.791 → 5.957 |
| FIX_R7 offset diagnosis (HHR 3.32 = urban 1.82 + approaches 1.22) | (a) | probably; not recomputed |
| `docs/alignments.md` §7 item 2 ("484.6 km … yards and approach tracks") | (a) | **yes: the text is wrong** (the excess was the stitch, the duplicated stretch and the branch) |
| `settlements.parquet` `dist_existing_(any_)line_km` | (a) | 1 of 7,371 rows if re-run: Jeddah 5.14 → 6.11 km; not re-run; no register rule reads it |
| S5 station-addition test (A-corr-011) | (a) | value moves for Jeddah (5.12 → 6.11 km), outcome no |
| fig01, fig12; dashboard API | (a) drawn | geometry only (rebuilt); `alignment_km` 484.59 → 455.23 is served but not displayed |

**Verdict.** Published figures depend on the stitched geometry:
- the R4_ALIGN HHR validation offsets and structure shares;
- the v1 tuning objective;
- the FIX_R7 v2 figures;
- the §7 sentence;
- the corridor-bonus band used to route every hypothetical corridor.

The routed lengths of `S4-commuter_belt-jeddah-000`, `-045`, `-315` and `S2-trunk_gap-riyadh-jeddah` can move directly on a re-route, and with them their running times, costs and CBA cases (incl. S6-L5). Every routed corridor can move if a re-tune picks other v1 weights. The existing lines' lengths, running times, skims and km-posts did not use the stitched length. Per the prompt the work stops here and nothing was re-run. Dependency chains:
- `hhr.geojson` → `network.align._rail_geoms` (corridor bonus) → routed `cities/ksa/alignments/*` (the four corridors above) → R4 running times/access → R5 costs/CBA → R6 (S6-L5) → R7/R8 figures;
- `hhr.geojson` → `network.align.compare` (offsets) → A-align-070 → frozen weights v1 → every routed corridor → R4–R8.

### Item 2: station siting (commits 263eb48, 167324f)
**Rule.** Written in Tariq's words in `docs/stations-siting.md` (new; `docs/` had no general siting note, and the site records in `docs/network.md` §2 stay), in the `line-yaml` skill (v1.1) and in `rail/README.md` (v1.1). Registered as **A-station-001**, `proposed, pending Tariq`, with the Haramain precedent (S-001, S-004, the OSM branch line). No best-practice search was made. The report annex was regenerated: one row added (`common.report build`; `report check` PASS).

**Inventory** (`uv run python -m rail.station_inventory`, `runs/fix-hhr/stations-inventory.csv`): 284 rows.
- All 153 `stations.geojson` stations and the 131 new S2–S5 corridor stations (53 sites), with S6 membership.
- By layer:
  - existing: city 112, airport 1 (`hhr:kaia`), on-airport-land 3 (Riyadh Metro L4 T1-2 and T3-4; SAR North Al-Qurayyat, 1.39 km from the URY aerodrome point, unverified), unplaced 3 (freight, as recorded)
  - committed: unplaced 10
  - historical: city 24
  - hypothetical: city 131
- 15 stations lie within 5 km of an airport point.
- Airport points are aerodrome centroids, not terminals (a stated proxy).
- **Landbridge Jeddah** is still the unpublished town-centroid placeholder at 21.55044, 39.17424 (`town_centroid:osm:node/1933393717`, `located: false`, `site_status: inferred`, `uncertainty_km` 13.9). Flag `unplaced`: 14.77 km from the JED point and 12.24 km from HHR KAIA.

**Proposal for Tariq** (nothing applied):
- **P1.** Landbridge Jeddah: keep the placeholder until SAR publishes a site, then check it against the rule. Any change re-runs S1 and so every scenario (R3/R4 demand and graph, R5 all cases, R6, R7/R8).
- **P2.** Bisha, Rafha, Jazan town points (2.6–3.1 km from an airport point; not on airport land; not in S6): keep. Any site search should apply the rule (R4_ALIGN, R4, R5 for those corridors).
- **P3.** Al-Qurayyat (existing): keep. Visual check open.
- **P4.** Riyadh Metro airport stations: keep (existing metro).
- **P5.** Adopt A-station-001 as a check in `screening.corridors` station additions (re-run S5, then R4_ALIGN, R5, R6 for changed corridors).

No current S2–S5 or S6 station would move under the rule.

### Tests and checks
- `tests/test_fix_hhr_jeddah.py`, 13 tests:
  - fixture branch build: MultiLineString, branch starts at the junction, no chord, km-posts unchanged
  - MultiLineString validates; a line without a branch stays a LineString
  - the rebuild preserves stations
  - HHR main within ±2 % of 453 and of the km-post span; branch 6.69 km (C-fixhhr-001)
  - no stitch in `existing.geojson`; no repeated vertex on HHR; every segment over 2 km is an OSM way segment
  - stations match the line YAML
  - the Jeddah figure is idempotent and under 1 MB; the screenshots exist
  - the inventory CSV parses with the expected flags; the flag rule; the stitch helper
- `make test` green: ruff, **745 passed** (732 → 745), docver 344 files, manifest 387 rows (one new row: the Sentinel-2 window).

### Follow-ups for Tariq (decisions; nothing done)
1. **R4_ALIGN re-route / re-tune** on the corrected geometry, at minimum the four corridors in the chord's band (`S4-commuter_belt-jeddah-000`, `-045`, `-315`, `S2-trunk_gap-riyadh-jeddah`), then R4–R8 for any that move. A full re-tune of A-align-070 is a larger decision; in it, v2 and the FIX_R7 diagnosis move too.
2. Correct the `docs/alignments.md` §7 item 2 sentence and the HHR offset figures in `docs/alignments.md` / `docs/alignments-tables.md` / annex A-align-100 once item 1 is decided (not edited here, because the brief says stop).
3. C-fixhhr-001: the branch length 3.75 km (secondary) vs 6.69 km OSM needs a SAR/HHR route description.
4. Adopt A-station-001 or not (and P1–P5 in `docs/stations-siting.md`). Al-Qurayyat (existing) visual check open.
5. Cost-log row for this run: the coordinator adds it from the run's JSONL (`common.cost_log add`).

### Incident
While stopping the local dashboard I ran `kill 2918`. That PID was **another process**, `.venv/bin/python -m uvicorn api.main:app --port 8000`, which this run had not started. The run's own server on 8765 was already stopped. If that port-8000 server was in use, it needs restarting (`uv run uvicorn api.main:app --port 8000`).

### Verifier
`red-team-verifier`, label VERIFY_FIX_HHR_JEDDAH, run in the foreground; report in `docs/status/verify-FIX_HHR_JEDDAH.md` v1.3.

| pass | HEAD | result | finding and fix |
|---|---|---|---|
| 1 | a17cc00 | FAIL | F1: the length-dependency table missed the R4_ALIGN corridor-bonus consumer (`network/align.py` `_rail_geoms` → `rail_mask` → `penalty_surface`). The stitched chord was a preferred band when routing every hypothetical corridor; four Jeddah-area corridors have vertices in it. The "only through a re-tune" sentence was wrong. Fixed: row added, both verdicts rewritten, follow-ups added (19e141c, 72ee913). |
| 2 | 72ee913 | FAIL | F1/F2 closed; the table was re-grepped as complete. F3: `docs/status/main.md` header not bumped. Fixed (ab00700). |
| 3 | ab00700 | FAIL | F4: wrong `align.py` line citations. Fixed (55ab059). |
| 4 | 55ab059 | **PASS** | All criteria. |

Pass 1 independently confirmed the geometry, the two declared deviations, that no station moved and no corridor was re-scored, the screenshots, the siting wording, the inventory counts, `make test` (745 passed) and `report check` PASS. It also confirmed that `prompts/`, `film/` and the licences are untouched.

FIX_HHR_JEDDAH: blocked - published figure depends on the stitched length: R4_ALIGN HHR validation offsets and structure shares, A-align-070 v1 tuning objective, FIX_R7 v2 figures, corridor-bonus routing of S4-commuter_belt-jeddah-000/-045/-315 and S2-trunk_gap-riyadh-jeddah (S6-L5, CBA cases), docs/alignments.md §7 item 2

## FIX_HHR_REROUTE re-route of the four chord-band corridors; A-station-001 adopted (6 Nov 2026, builder on `main`)

Cost estimate for this run: USD 30–45 list price (runaway guard USD 60); the coordinator logs the actual cost from the run's JSONL. Rules kept: no tag, no push, no R9/R10 (`prompts/` and `film/` untouched), no licence status change, no paid model or API. TrafficTwin was not touched. **No process was killed:** this run started no server or long-lived process. Commits: d6c8321, f8f9a03, 4b3891f, 6d6dcf9, 8438a5e, cb69b9b, and this block.

### Item 1: contained re-route (Tariq's decision 1)
**Band fix (d6c8321).** `network.align.rail_mask` now rasterises each part of a MultiLineString through `rail_parts`, so the corridor-bonus band covers the HHR main line and the real KAIA branch, and nothing joins the parts. Before the fix, `rasterize` was already given the MultiLineString, so the part handling was implicit; it is now explicit and tested. The `osm_line` part-0 guard is unchanged. Route metas also record `rail_layer_sha256` (per-line GeoJSON plus `existing.geojson`). Tests in `tests/test_fix_hhr_reroute.py`:
- two-part fixture: the branch vertices are in the band and the old chord is not;
- control: a stitched LineString does put the chord in the band;
- live `hhr.geojson`: the KAIA branch is in the band and the middle of the old KAIA → Al-Sulaimaniyah chord is not.

**Re-route (f8f9a03).**
- Command: `uv run python -m network.reroute route | control | band | deltas | apply --seed 1`, from clean commit d6c8321; every meta reads `code_version r8-34-gd6c8321`.
- Scope: only `S4-commuter_belt-jeddah-000`, `-045`, `-315` and `S2-trunk_gap-riyadh-jeddah`, under the frozen v1 weights. The hash `2b718ecbe6caead86e8424e621f90420815a6ada10ad6c4e1b7ffa00bca792d4` was checked before and after and equals `align_weights.sha256`. A-align-070 was not re-tuned.
- Metas record `hhr.geojson` 2afcaf8d… and `existing.geojson` 918facf8… (the corrected files).
- Outputs: full run in `runs/fix-hhr-reroute/align-s1/`; previous sidecars in `runs/fix-hhr-reroute/before/` (equal to the HEAD copies).
- Belt 045 left the corridor set at R5 H4a. It was routed from its last YAML (`git 6318367^`) and has nothing downstream.
- **Thresholds, set before the deltas** (`cities/ksa/assumptions/reroute_thresholds.yaml`; A-align-120…124, `proposed`). A corridor moved materially if any of these held: length change > 1 %; tunnel, viaduct or earthworks km change > 1 % (each tested on its own); all-stop running time change > 0.5 min; maximum lateral offset > 1 km. Reported, not a test: km of the new path more than 500 m from the old path.

**Per-corridor deltas** (`runs/fix-hhr-reroute/deltas.csv`; `docs/alignments.md` §4d):

| corridor | length km old → new | tunnel / viaduct / earthworks km | max grade | all-stop min, R4 model | mean / max offset km | km moved > 500 m | moved materially |
|---|---|---|---|---|---|---|---|
| S4-commuter_belt-jeddah-000 | 78.140 → 78.140 | 0.000 / 0.799 / 1.899, Δ 0 | 2.502 % → 2.502 % | 32.52 → 32.52 | 0.000 / 0.000 | 0.000 | **no** |
| S4-commuter_belt-jeddah-045 (not in the set) | 66.276 → 66.276 | 0.400 / 0.200 / 15.094, Δ 0 | 2.503 % → 2.503 % | 27.73 → 27.73 | 0.000 / 0.000 | 0.000 | **no** |
| S4-commuter_belt-jeddah-315 | 84.509 → 84.509 | 0.000 / 0.999 / 0.000, Δ 0 | 2.502 % → 2.502 % | 35.10 → 35.10 | 0.000 / 0.000 | 0.000 | **no** |
| S2-trunk_gap-riyadh-jeddah | 893.484 → 893.484 | 13.398 / 16.397 / 121.175, Δ 0 | 2.503 % → 2.503 % | 217.52 → 217.52 | 0.000 / 0.000 | 0.000 | **no** |

The old running times equal `runs/network-eval/S2|S4/summary.parquet` `run_min_kinematic` (217.520, 32.524, 35.095).

**Verdict: none of the four moved materially.** For each of them, `alignment.geojson`, `summary.json` and `profile.parquet` are byte-identical to the previous runs (`runs/align/r5-h4a-s1/` for 000 and Riyadh–Jeddah; `runs/align/corridors-s1/` for 045 and 315).

Why nothing moved (`runs/fix-hhr-reroute/band-diff.json`):
- The corridor flag of A-align-029 is "within 1 km of an OSM highway **or** existing rail". Every cell under the old chord is also within 1 km of a highway.
- At the coarse step (15″), 36 rail cells change but **0** corridor-flag cells do. At the fine step (3″), 219 rail cells change and 2 corridor-flag cells do; neither lies on any of the eight paths.
- Control (`network.reroute control`): today's code on the old stitched `hhr.geojson` (0cc369e) reproduces the previous runs byte for byte.
- FIX_HHR_JEDDAH's "routed vertices in the chord's band" (6/5/1/1) counted rail-band proximity, which had no effect on the cost surface.

The live sidecars `cities/ksa/alignments/<id>.json` were rewritten from the new runs; only the `run:` pointer changed. `screening.corridors generate` (scores `runs/r4/funnel-minutes/score/scores.parquet`) then reproduced every corridor YAML. Three YAMLs differ only in `alignment_routed.run`; the scenarios and `decisions.csv` are unchanged. `cities/ksa/alignments/summary.csv` is byte-identical.

**Downstream: nothing re-run, nothing changed** (the corridors did not move materially, so per the brief their figures stay untouched):
- R5 costs `runs/costs/<id>/`, skims and running times;
- judge v3 standalone scores, `runs/r7/corridors/`;
- R6 layouts: S6-L5 holds belts 000 and 315 (`scenarios/S6-L5.yaml`); no `scenarios/S6-L*.yaml` and no `runs/r6/top5/` input changed;
- the CBA cases `runs/cba/CBA-S2-trunk_gap-riyadh-jeddah*`, `CBA-S4-commuter_belt-jeddah-000*` and `-315*`;
- R7 fiscal/VfM (none of the four is in the CP7 layouts L1–L3);
- R8 report sections, brief, summaries EN/AR (so no bilingual check was needed), deck figures, `figures-index.csv` and dashboard API data.

`find runs/costs runs/cba runs/r6 runs/r7 runs/network-eval runs/access runs/align web/public api -newer <f353073 commit time>` returns 0 files. `git diff f353073 HEAD` is empty for `docs/report/` (except `annex-assumptions.md` and the 8 new maps), `docs/report/figures-index.csv`, `scenarios/`, the brief, both summaries, `prompts/`, `film/`, `docs/licences*`, `cities/ksa/lines/`, `cities/ksa/cba/`, `cities/ksa/costs/` and `align_weights.yaml`.

**HHR offset convention: main + branch.** The published figures now use main + branch (mean 3.399 km), because:
- the routed HHR validation line serves KAIA, which only the branch reaches;
- it is the drawn real geometry with no part dropped, the same rule as the band;
- Tariq's decision figures (7.473, 4.641, 5.957) use it.

Main only (3.432 km) is printed beside it in every table. Caveat: `network.align.validate` as coded (through the `osm_line` part-0 guard) would print the main-only values on a re-run.

| HHR figure (`runs/fix-hhr/check.json`) | stitched | **main + branch (published)** | main only |
|---|---|---|---|
| mean offset km | 3.317 | **3.399** | 3.432 |
| P90 / Hausdorff km | 7.664 / 14.328 | **7.757 / 14.330** | 7.774 / 14.329 |
| OSM length compared km | 483.331 | **454.070** | 447.391 |
| OSM tunnel km (share) | 9.311 (1.93 %) | **9.311 (2.05 %)** | 2.184 (0.49 %) |
| OSM bridge km (share) | 44.122 (9.13 %) | **44.122 (9.72 %)** | 42.225 (9.44 %) |
| A-align-070 objective at frozen v1 | 7.446 | **about 7.473** | about 7.484 |
| v2 in-sample / held-out HHR (not adopted) | 4.517 / 5.791 | **4.641 / 5.957** | 4.686 / 6.012 |

The frozen v1 weights stay frozen (the objective would read about 7.473 km). The FIX_R7 v2 in-sample and held-out HHR figures would read 4.641 / 5.957 km if recomputed; no new weights are adopted. Both points are recorded in `docs/alignments.md` §4d and in the A-align-070 and A-align-100 rows.

**§7 item 2** (`docs/alignments.md` line 328; 4b3891f):
- Old: "The OSM geometry includes yards and approach tracks (HHR 484.6 km of geometry against 448.5 km between Makkah and Madinah stations)."
- New: "The old HHR geometry measured 484.6 km against 448.5 km between the Makkah and Madinah stations. The extra length was the stitch (17.32 km), the duplicated Sulaimaniyah–junction stretch (12.04 km) and the KAIA branch (6.69 km) of a wrongly stitched LineString; it was not yards and approach tracks. On the corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE), the main line measures 448.54 km, equal to the station span, and the KAIA branch 6.69 km (`docs/network.md` §HHR geometry). The decision stands."

**Published numbers that change** (all are HHR validation and tuning figures; no corridor, cost, benefit or programme number changes). The old values stay printed, labelled "stitched geometry", and the new ones are labelled "corrected geometry, 6 Nov 2026 (FIX_HHR_REROUTE)". Run id for every new value: `runs/fix-hhr/check.json` (FIX_HHR_JEDDAH, `rail.hhr_check --before-rev 0cc369e`).

| file:line | old | new |
|---|---|---|
| `docs/alignments.md:68` | HHR mean offset "about 3.3 km" | + "3.399 km on the corrected geometry" |
| `docs/alignments.md:78` | tuning objective 7.446 km | + "about 7.473 km on the corrected geometry; weights stay frozen" |
| `docs/alignments.md:131` | (§4a decomposition, HHR 3.317 km) | note: stitched geometry, not recomputed; corrected 3.399 km |
| `docs/alignments.md:137` | HHR 3.32 km | + 3.399 km |
| `docs/alignments.md:166` | held-out HHR 5.79 km (§4b LOO table) | + 5.957 (main only 6.012), if recomputed |
| `docs/alignments.md:184` | HHR v1 3.32 / v2 4.52 / held-out 5.79; tunnel 9.3, bridge 44.1 | + 3.399 (P90 7.757, Hausdorff 14.33) / 4.641 / 5.957; main only 3.432 / 4.686 / 6.012 |
| `docs/alignments.md:188` | v2 HHR 4.52 km | + 4.641 km |
| `docs/alignments.md:189` | held-out HHR 5.79 | + 5.957 |
| `docs/alignments.md:236–285` | (new §4d) | offsets, shares, objective, v2 figures, deltas table |
| `docs/alignments.md:328` | §7 item 2 "yards and approach tracks" | stitch 17.32 + duplicate 12.04 + branch 6.69 km; main 448.54 km |
| `docs/alignments-tables.md:14` | (HHR row 3.32; P90 7.7; tunnel OSM 9.3 (1.93 %); bridge OSM 44.1 (9.13 %)) | added row: 3.40; P90 7.8; 9.3 (2.05 %); 44.1 (9.72 %) |
| `docs/alignments-tables.md:20` | – | note: main-only values; tuning 7.446 → about 7.473 |
| `docs/assumptions.md:55` and `docs/report/annex-assumptions.md:55` (A-align-070) | final objective 7.446 | + about 7.473 on the corrected geometry, frozen |
| `docs/assumptions.md:60` and `annex-assumptions.md:60` (A-align-100) | v1 3.32; v2 held-out HHR 5.79 | + v2 in-sample 4.641, held-out 5.957, v1 3.399 (main only 4.686 / 6.012 / 3.432) |
| `docs/assumptions.md:69–73` and `annex-assumptions.md:69–73` | – | A-align-120…124 (1 %, 1 %, 0.5 min, 1 km, 500 m / 50 m) |
| `docs/report/annex-assumptions.md:5` | 755 rows, header hash feb7ff1b6417… | 760 rows, header hash cda74f1f0e66…; "adopted 1" |

**Maps** (`uv run python -m network.reroute maps`; the map code is `common.figures.jeddah_hhr_map`, as for `hhr-jeddah-*`, with an additive `--corridor` overlay and `--extent`; the default output is byte-identical, which was checked):
- `docs/report/figures/reroute-S4-commuter_belt-jeddah-000-before.png` / `-after.png` (132 / 121 KB)
- `docs/report/figures/reroute-S4-commuter_belt-jeddah-045-before.png` / `-after.png` (141 / 131 KB)
- `docs/report/figures/reroute-S4-commuter_belt-jeddah-315-before.png` / `-after.png` (126 / 116 KB)
- `docs/report/figures/reroute-S2-trunk_gap-riyadh-jeddah-before.png` / `-after.png` (145 / 135 KB)

Each map carries the OSM credit and the layer legend (existing, hypothetical (ours), committed, historical), plus the synthetic label in the footer. "Before" draws the old stitched HHR with its 17.3 km stitch in red; "after" draws the main line and the branch junction. In the larger windows, only true stitches (`rail.hhr_check.stitch_jumps`) are marked.

### Item 2: C-fixhhr-001 stays open (decision 2; 6d6dcf9)
The 3.75 km note in `hhr.yaml` and the drawn 6.69 km OSM branch are unchanged (`git diff f353073 -- cities/ksa/lines/` is empty). The conflict row is unchanged apart from an appended "Left open by Tariq, 6 Nov 2026 (FIX_HHR_REROUTE)". No SAR figure was invented.

### Item 3: A-station-001 adopted (decision 3; 8438a5e)
**A-station-001 adopted; no station moved; no corridor re-scored for siting.**
- Register status: "adopted by Tariq, 6 Nov 2026 (in the words written; FIX_HHR_REROUTE)". The rule text is unchanged.
- `docs/stations-siting.md` v0.2 header line: "Adopted by Tariq, 6 Nov 2026, in the words written."
- P1–P5 applied as written:
  - P1: the Landbridge Jeddah placeholder is kept.
  - P2: Bisha, Rafha and Jazan stay town points.
  - P3: Al-Qurayyat is kept; its visual check is still open.
  - P4: the Riyadh Metro airport stations are kept.
  - P5: `screening.corridors.siting_check` runs in `generate`. A station the generator adds (not from `stations.geojson`, not `airport` class) within 1.5 km of an airport point is refused for S5 and flagged in `siting_flags` for S2–S4 (not dropped, because dropping it would be re-scoring for siting). Both are recorded as decision rows.
- Tests: an S5 fixture station on airport land is refused; an S4 fixture station is flagged, not moved, and still validates; existing and airport stations pass; the live corridors are unaffected.
- With the check in place, the generator reproduces all corridor YAMLs, `decisions.csv` and S2–S5 byte for byte. The closest generator-added station to an airport point is 2.59 km away.
- Line added to the `corridor-generator` skill (v1.1). Status wording updated in `line-yaml` (v1.2), `rail/README.md` (v1.2) and `rail/station_inventory.py`.

### Tests and checks
- `tests/test_fix_hhr_reroute.py`, 24 tests: the multi-part band fixture, the stitched control and the live HHR band; the threshold values and the materiality rule (12 cases); path offsets; the siting check (4); the re-route maps (exist, < 1 MB, idempotent, default map unchanged).
- `make test` green: ruff, **769 passed** (745 → 769), docver 346 files, manifest 387 rows (no new data rows). `common.report build` / `report check`: PASS.

### Verifier
`red-team-verifier`, label VERIFY_FIX_HHR_REROUTE, run in the foreground on HEAD 1b2f818; report `docs/status/verify-FIX_HHR_REROUTE.md`. **Pass 1: PASS** on all 15 criteria. It independently checked:
- the scope (four sidecars and three corridor YAMLs, `run:` only);
- the weights hash and the rail-layer hashes;
- the band tests;
- 12/12 byte-identical route outputs and clean metas;
- the deltas and running times;
- all HHR figures and the 7.473 arithmetic;
- that the published-number table covers every changed line in `docs/`;
- the untouched areas;
- the process rule;
- `make test` (769), `report check` PASS.

Its non-blocking observations:
- (1) the status line was still to be appended (done below);
- (2) `docs/alignments.md:285` "No published number changes." contradicted §4d's own table. It now reads "No corridor, cost, benefit or programme number changes; the HHR validation and tuning figures above are the only published numbers that change.";
- (3) cosmetic label overlaps in the maps (the stitch label touches the axis in the "before" maps; the legend sits near the Al-Jumum label in the S2 map), left as they are.

Follow-ups for Tariq (decisions; nothing done):
- `network.align.osm_line` returns the main part only, so a re-run of `network.align validate` would print the main-only HHR offsets (3.432 km), not the published main + branch convention (3.399 km). Decide whether `compare` should use every part before any future validation re-run.
- A-align-120…124 are `proposed`.
- Cost-log row for this run: the coordinator adds it (`common.cost_log add`).

FIX_HHR_REROUTE: done

## S6_L6_CONNECTED one connected rail system as a comparison layout (6 Nov 2026, builder on `main`)

Runaway-guard estimate (written first): about USD 25–40 list price for this run (one Opus builder, one verifier run), against the USD 60 guard. No judge run, no paid model or API, no download, no push, no tag. R9/R10, `film/`, the licences, the interchange thresholds, the stations, the alignments and the frozen judges are untouched.

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Every S6-L6 NPV is **fast mode, not a full-judge score; corridor interaction not included; the full judge overstated/understated fast mode by 1–17 % of capex in R6.** Note: `docs/r6-l6-connected.md` v1.0. Code: `optimise/connect.py`. Runs (seed 1): `runs/r6/l6/` (`components.json`, `search.json`, `attachments.json`, `compare.json`, `national_reach.json`).

### Commits per item
- Item 7: 0ef4623.
- Items 1–4: ad2dc43 (code, `r6_l6.yaml`, A-r6-130…134, tests).
- Item 5: 321afee (`scenarios/S6-L6.yaml`, map).
- Note for items 1–6: caa5ce8.
- Annex mirror: see "Deviation" below.

### Item 1: components (current rules, `network.graph`: walk 0.4 km A-r1a-030, same name 3.0 km A-r1a-032; unchanged)

| layout | components | islands / fragments (nearest gap) |
|---|---|---|
| S1 | **3** | main (SAR North, SAR East, Landbridge, Riyadh Rail Link, Riyadh Metro; 110 stations); HHR (5 stations): `landbridge:jeddah` ↔ `hhr:jeddah` **8.21 km**; GCC (3 stations): `sar-east-passenger:dammam` ↔ `gcc-railway-ksa:dammam` **3.74 km** |
| S6-L1, L2, L3 | 3 | as S1 (the Al Jubayl station sits on the GCC line) |
| S6-L4 | 4 | + Makkah belt 045: its Makkah station is **3.98 km** from HHR Makkah |
| S6-L5 | 4 | HHR (3.98 km from the Makkah belt), GCC (3.74), Madinah belt 045 (**8.96 km** from HHR Madinah) |

Tariq's diagnosis is confirmed to the hundredth of a km. Not fixed by widening the thresholds or by moving the Landbridge Jeddah placeholder (A-station-001 P1).

### Items 2–4: chosen set (S6-L6) and alternatives

Exact MILP over the R6_V3 library: 71 corridors plus their costed variants (A-r6-133). Lazy connectivity cuts; every set is re-checked on the real graph.

**S6-L6** (`scenarios/S6-L6.yaml`): 16 options, **capex P50 227,213 SAR m** (P10/P90 sums 122,532 / 860,035), **fast robust NPV −200,761**, 3,241.9 new route-km, **1 component**, 18 of 18 required cities on the graph.
- Every line corridor is the non-electrified variant: the lowest capex, so the capex-first rule picks it.
- Phases: best library phase (2050; Al Jubayl station 2030).
- The 16:
  - trunks Abha–Bisha, Abha–Najran, Al Jubayl–Hafar Al-Batin, Jeddah–Yanbu, Tabuk–Sakaka, Taif–Bisha;
  - spurs Al-Kharj, Arar, Bisha, Sakaka, Yanbu Industrial City;
  - belts Abha 135, Dammam 180, Jazan 315;
  - stations Al-Jarn, Al Jubayl.
- Per-corridor building blocks: note §2.

**Ties:** Al-Jarn ↔ Al-Oyun / Al-Qarah / Al-Umran (474.4 each).

**Next two sets:**
- 229,286 (+2,073): the Taif spur instead of the Yanbu spur.
- 230,946 (+3,733): Riyadh–Hafar instead of Al Jubayl–Hafar, with Al-Oyun.

The line set is the unique minimum.

**Item 3, joins** (`attachments.json`, all walk links at 0.000 km):
- Haramain: HHR Madinah ↔ Yanbu Industrial City spur → Yanbu ↔ Jeddah–Yanbu trunk → its Jeddah terminal ↔ `landbridge:jeddah`. Caveat: the trunk's Jeddah terminal is the A-screen-013 anchor, which has the placeholder's coordinates.
- GCC: GCC Dammam ↔ Dammam belt 180 → Al Jarn ↔ the Al-Jarn station inserted into SAR East.
- No 8.21 km or 3.74 km transfer is used.

**Item 4, chord band:**
- Allowed, the minimum is 215,332 (−11,880) and uses `S4-commuter_belt-jeddah-315` + Thuwal.
- Connectivity is possible without it, so **L6 is the version without** (none of the four in L6; `-045` is not in the library).
- Base corridors only (all electrified): 251,783 (+24,570; above B2), fast robust NPV −187,805.
- Ha'il + Ar Rass required as well: 247,564 (+20,351).

### Item 5: comparison (`compare.json`; L1–L5 full-judge figures as published, unchanged)

| layout | fast robust NPV | full-judge robust NPV (published) | capex P50 | B1/B2/B3 | 120-min reach gain, 5 metros | national reach 120 (gain), reported only | components | corridors | route-km |
|---|---|---|---|---|---|---|---|---|---|
| S6-L1 | 12,135 | 11,023 | 11,194 | y/y/y | 3.56 M | 26.67 M (+0.57 M) | 3 | 4 | 139.2 |
| S6-L2 | 7,826 | 6,792 | 1,423 | y/y/y | 3.56 M | 26.25 M (+0.15 M) | 3 | 3 | 0 |
| S6-L3 | 3,361 | 2,427 | 19,630 | y/y/y | 4.25 M | 26.67 M (+0.57 M) | 3 | 4 | 218.2 |
| S6-L4 | −7,005 | −7,934 | 36,726 | y/y/y | 4.67 M | 26.89 M (+0.79 M) | 4 | 5 | 313.4 |
| S6-L5 | −106,909 | −112,565 | 98,170 | y/y/y | 5.30 M | 26.63 M (+0.54 M) | 4 | 12 | 989.4 |
| **S6-L6** | **−200,761** | not scored | **227,213** | n/y/y | **0.43 M** | **32.74 M (+6.64 M)** | **1** | **16** | **3,241.9** |

Map: `docs/report/figures/s6-l6-connected-map.png` (176 KB). It is in the fig01 map family (`common.figures`), with the OSM credit and the four-layer legend. It is not added to `figures-index.csv`.

### Item 7: `osm_line` / `compare` on every part
`osm_line` returns the whole MultiLineString. `compare` clips part 0 and adds the branch whole. `align_diag` keeps main only.

Dry run (`uv run python -m network.align recompare`, existing path `runs/align/validation-s1`; no validation, re-tune or re-route):
- HHR: mean **3.399**, P90 **7.757**, Hausdorff 14.330, 454.070 OSM km;
- objective **7.4733**;
- SAR North / East unchanged (9.813 / 9.208).

`docs/alignments.md` v1.4 §4d carries the sentence. `docs/network.md` v0.11 updates the row that said `osm_line` returns the main line only.

### Deviation (reported, necessary)
`docs/report/annex-assumptions.md` gained the 5 A-r6-130…134 rows and a new header hash. It is a generated mirror of `docs/assumptions.md`: `tests/test_report_build.py::test_committed_report_matches_a_fresh_build` fails otherwise. `common.report build` changed no other file under `docs/report/`, and `report check` passes. No R6–R8 figure, summary, brief or figure index changed.

### Assumptions added
A-r6-130 (connectivity), A-r6-131 (on-the-graph test), A-r6-132 (required cities), A-r6-133 (search, objective, ties, alternatives), A-r6-134 (phases, fast-mode label). Parameters: `cities/ksa/assumptions/r6_l6.yaml`.

### Tests and checks
`make test` green:
- ruff;
- **783 passed** (769 + 5 `tests/test_align_compare_parts.py` + 9 `tests/test_s6_l6_connected.py`);
- docver 349 files;
- manifest 387 rows, no downloads;
- `report check` PASS.

Disk 30 GiB free.

### Decisions for Tariq (stop: nothing scored)
1. Score S6-L6 with the full judge v3 (one run, about 90 s): yes / no; non-electrified as built (227,213) or all base (251,783, above B2).
2. Carry L6 into R7 (delivery model) and R8 (report, dashboard): yes / no.
3. Connectivity in any future R6 round: constraint, objective or neither.
4. Ha'il and Ar Rass: required (+20,351) or reported.
5. The chord-band version (215,332) as a sensitivity only, or allowed.

### Verifier
`red-team-verifier`, label VERIFY_S6_L6_CONNECTED, ran in the foreground on HEAD 6272eb4; report `docs/status/verify-S6_L6_CONNECTED.md`. **Pass 1: PASS** on every criterion.

It independently recomputed:
- the components and gaps (8.211 / 3.738 / 3.984 / 8.956 km);
- the L6 graph (one component, 153 stations, 18 of 18 cities);
- the minimum, with its own flow MILP without lazy cuts: 227,213.0 with the same line corridors, and 215,332.4 with the chord band;
- hand-built alternatives, all dearer: Riyadh–Dammam trunk 240,063 / 240,538; Taif spur in place of Jeddah–Yanbu 234,141;
- `recompare`: 3.399 / 7.757 / 7.4733.

It also confirmed:
- no protected path changed;
- the annex mirror was necessary;
- `make test` is green (783).

Observations:
- O3: the model name in the `r6_l6.yaml` header was removed after the verifier.
- O4: `runs/r6/l6/meta.json` records only the last command and carries the `-dirty` code version; run outputs are not tracked.
- O5: naming in note §1 is cosmetic.
- Cost-log row: the coordinator adds it (`common.cost_log add`).

S6_L6_CONNECTED: done

## S6_L6_SCORE — 6 Nov 2026

Start HEAD 6149a8b. Cost estimate for this run: about USD 15–30 list price (one Opus builder session plus one foreground verifier; the judge runs locally at USD 0); runaway guard USD 60.

Scope (Tariq, 6 Nov 2026): one full-judge v3 score of `scenarios/S6-L6.yaml` as built (non-electrified, capex P50 227,213); written only into `docs/r6-l6-connected.md` and `scenarios/S6-L6.yaml`. Comparison layout, not the recommended programme. Synthetic demand, uncalibrated: scenario comparison, not a forecast.

### Run
- Judge `v3-variants` sha256 `d9fef64384e2e25f…`, checked with `optimise.judge verify` before and after. `judge/` is untouched.
- One full-judge run, 115 s, through the adapter as in R6/R6_V3:

  `R6_OUT=runs/r6/l6 uv run python -m optimise.search full --layout runs/r6/l6/L6.layout.yaml --out runs/r6/l6/score --all-cases --engine l6-score`

  Seed 1, 10,000 draws; all horizons × rate cases × population cases (45 appraisal rows).
- Post-judge bookkeeping with `uv run python -m optimise.connect score` (new, additive; it does not run the judge):
  - national reach (reported only) added to `score.json`; the judge's own file is kept as `score.judge.json`;
  - layout hash `2243d1863821` added to `meta.json`;
  - `S6-L6.csv` written (the `top5.csv` columns) and the map `S6-L6-map.png` (131 KB).
- `meta.json`: `code_version` `judge v3-variants @ 017234562c sha256 d9fef64384e2e25f`, harness `r8-54-g29b6aaf` (clean).
- Nothing was written under `runs/r6/top5/`.

### Score (full judge v3) beside fast mode and L1–L5
Comparison layout, not the recommended programme. Synthetic demand, uncalibrated: scenario comparison, not a forecast. Alignment limitation applies. SAR million, 2025 prices, PV 2026.

| layout | fast robust NPV | full robust NPV | NPV at P90 cost (low / med / high) | BCR P10 / P50 / P90 (medium) | capex P10 / P50 / P90 | added rail trips 2050 (medium) | five-metro 120-min gain | national reach 120 (reported only) |
|---|---|---|---|---|---|---|---|---|
| S6-L1 | 12,135 | 11,023 | −2,958 / −724 / 1,631 | 0.60 / 2.33 / 9.33 | 6,233 / 11,194 / 41,304 | +4.29 M | 3.56 M | 26.67 M (+0.57 M) |
| S6-L2 | 7,826 | 6,792 | 3,986 / 4,771 / 5,589 | 1.52 / 5.96 / 22.23 | 801 / 1,423 / 5,286 | +1.78 M | 3.56 M | 26.25 M (+0.15 M) |
| S6-L3 | 3,361 | 2,427 | −21,745 / −19,225 / −16,624 | 0.32 / 1.12 / 3.48 | 10,684 / 19,630 / 73,799 | +4.85 M | 4.25 M | 26.67 M (+0.57 M) |
| S6-L4 | −7,005 | −7,934 | −54,553 / −51,470 / −48,184 | 0.21 / 0.75 / 2.22 | 19,031 / 36,726 / 143,343 | +6.62 M | 4.67 M | 26.89 M (+0.79 M) |
| S6-L5 | −106,909 | −112,565 | −229,925 / −227,697 / −225,401 | 0.03 / 0.14 / 0.37 | 52,401 / 98,170 / 374,892 | +5.51 M | 5.30 M | 26.63 M (+0.54 M) |
| **S6-L6** | **−200,761** | **−191,660** | **−465,454 / −459,954 / −454,113** | **−0.08 / 0.06 / 0.37** | **122,532 / 227,213 / 860,035** | **+9.03 M** | **0.43 M** | **32.74 M (+6.64 M)** |

Fast vs full:
- For L6, full − fast = **+9,101 = 4.0 % of capex P50**. That is inside R6's 1–17 % band, but in the opposite direction: here the fast mode understated the robust NPV.
- HHR 2050 is 11.32 M (S1 11.27 M); Landbridge 2050 is 5.40 M (S1 4.76 M); CO2 PV P50 (medium) is 2,613.
- Full table: `docs/r6-l6-connected.md` §7b.

### Access model
**The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are not rail-graph interchanges.**
- They affect the access times, the five-metro reach, the national reach and the judge's island flags. The located graph also feeds the rail level of service behind trips and NPV; the size of that effect is not measured.
- They do not affect the rail graph's component count (A-r6-130: 1).
- The access model is unchanged.

### Decisions applied (Tariq, 6 Nov 2026)
- L6 is not carried into R7; no R7/R8 file changed.
- Connectivity is neither a constraint nor an objective in future R6 rounds. A-r6-130/131 status is now "diagnostic only, Tariq 6 Nov 2026"; no value changed.
- Ha'il and Ar Rass stay reported, not required.
- The chord band stays a sensitivity only.

### Deviation (reported, necessary)
`docs/report/annex-assumptions.md` is the generated mirror of the two status texts plus its source hash (`common.report build`; `tests/test_report_build.py` requires it). No other file under `docs/report/` changed. No register row was added.

### Untouched-areas evidence (`git diff --stat 6149a8b HEAD`)
| file | lines changed |
|---|---|
| `docs/assumptions.md` | 6 |
| `docs/r6-l6-connected.md` | 94 |
| `docs/report/annex-assumptions.md` | 6 |
| `docs/status/main.md` | this block |
| `docs/status/verify-S6_L6_SCORE.md` | 100 |
| `optimise/connect.py` | +127 |
| `scenarios/S6-L6.yaml` | 24 |
| `tests/test_s6_l6_score.py` | +192 |

Nothing else changed:
- no R7/R8 file, policy brief, summaries, `figures-index.csv`, `docs/r6-topology.md`, `docs/delivery-models.md` or `docs/fiscal-exposure.md`;
- no file in `web/`, `api/`, `runs/r7/`, `prompts/`, `film/` or `judge/`;
- no licence, the access model, `network/graph_params.yaml` or `runs/r6/top5/`.

No station moved, no alignment was added, no process was killed, and no paid API, tag or push was used.

### Tests and checks
- `make test` green: ruff; **789 passed** (783 + 6 in `tests/test_s6_l6_score.py`); docver; manifest 387 rows, no downloads.
- `report check`: PASS. Disk 29 GiB free.

### Verifier
`red-team-verifier`, label VERIFY_S6_L6_SCORE, run in the foreground; report `docs/status/verify-S6_L6_SCORE.md`.
- **Pass 1: FAIL** on criterion 4, note text only:
  - three BCR roundings (L2 P10, L5 P50, L6 P10);
  - "L4 and L5 lower both";
  - "16 line options".

  Fixed in 95ecde1, with a new cell-by-cell table test in 0f33cf3.
- **Pass 2: PASS** on every item. The verifier re-ran the judge independently: identical except `seconds`. It recomputed all 102 table cells.

### Cost
- Estimate for this run: about USD 15–30 list price (builder plus two verifier passes; the judge ran locally at USD 0). Runaway guard USD 60, not approached.
- The coordinator adds the cost-log row (`common.cost_log add`).

S6_L6_SCORE: done

## R8_L6_PANEL (6 Nov 2026; start HEAD 87cb9d0)
Run estimate: about USD 20–40 list price (one builder on claude-opus-5-5 plus verifier passes); runaway guard USD 60.

### What changed (commits e92cb46, fa127b5, b959529, 4314d85, 332a9c4, 6b74a4b, bbaebb9)
S6-L6 now appears as a **comparison layout, not the recommended programme**. It is described as a connectivity comparison, not a reach trade-off and not a search result. Its figures are read only from `runs/r6/l6/` (`score/S6-L6.csv`, `score/score.json`, `L6.layout.yaml`) and `scenarios/S6-L6.yaml`. Where it now appears:
- **Report §4.6** (`docs/report/sections/04-results.md` v1.2): a separate L6 paragraph with both labels, the A-r4-acc-004 sentence and judge v3 `d9fef643…` / seed 1. Figures: robust NPV −191,660; capex P50 227,213 (P10 / P90 122,532 / 860,035); BCR 0.06 (−0.08 / 0.37); +9.03 M trips; +6.64 M national reach (reported only); 0.43 M five-metro gain; fast mode −200,761 understated the full score by 9,101 (4.0 %).
  - The paragraph sits after the Figure 7/8 blocks, not directly under the L4/L5 paragraph. `report check` requires every S6-L4 mention within 3 lines of fig07/fig08, and every S6-L1 mention near the P90-cost statement; placed directly under, both failed. The verifier judged this placement acceptable.
  - `docs/report/feasibility-report.md` was rebuilt with `common.report build`, not hand-edited.
- **Figure 8** (`fig08-reach-tradeoff`, "S6-L1 to S6-L6"): L6 is a labelled open diamond, not a CP7 square. The caption separates L4/L5 (reach trade-off illustrations from the search) from L6 (connectivity comparison, not a search-front point) and gives L6's +6.64 M national reach (reported only). The y axis is still the five-metro reach (A-r6-007).
- **Figure 7**: caption only ("not on the R6 front … shown in Figures 8 and 16"). The svg/png are byte-identical in both directories. `runs/r6/pareto_front.csv` is unchanged.
- **Figure 16** (`fig16-l6-connected-map`, new): embeds the existing `s6-l6-connected-map.png` unchanged (no new geometry). Beside it: the L6 scorecard, both labels, the A-r4-acc-004 sentence, and provenance (connecting-set search plus L6 score, judge v3 `d9fef643…`, seed 1). It is in `figures-index.csv`, `figures/README.md` (v1.5) and §4.6. CP7 figures fig01, fig05, fig06, fig09–fig11 and fig15 are unchanged.
- **Dashboard/API**:
  - `FRAMING["S6-L6"]` = "comparison layout, not the recommended programme" with `trade_off_only` set. It gets its own caption, `api.contract.caption()`, not the L4/L5 one.
  - `/api/pareto` appends L6 with `kind: comparison`. `/api/programmes` and `/api/scenarios` include it. `/api/difference?scenario=S6-L6` returns 409.
  - The funnel count is still 5 (from `top5.csv`). `SWITCHER` is unchanged.
  - ParetoView: the default y range covers L1–L5 only; L6 is drawn as a labelled off-scale marker.
  - `web/dist` was rebuilt. `docs/report/figures/dashboard-pareto.png` was re-shot on a server I started on port 8799 and stopped by its own port; ports 8765 and 8000 were not touched.
- **Summaries and brief**: a parallel L6 sentence in `executive-summary.en.md` (v0.5), `executive-summary.ar.md` (v0.9, glossary terms, numeric runs isolated, bidi-probe 0 wrong; **still a draft pending Tariq's native read**) and `policy-brief.md` (v0.4). L1–L3 wording is unchanged.
- **`docs/r6-l6-connected.md` §5** (v1.3): the L6 full-judge cell now reads −191,660 (§7).

### Untouched-areas evidence (`git diff --stat 87cb9d0 HEAD`, 41 files)
Changed only: `api/` (README, contract, data, main), `common/figures.py`, the fig08 and fig16 files in `docs/report/figures/` and `docs/deck-figures/` (plus their indexes and README), `dashboard-pareto.png`, `executive-summary.ar.html`, the two summaries, the policy brief, `docs/r6-l6-connected.md`, `04-results.md` and the compiled report, `web/` (README, App, config comment, types, ParetoView), API fixtures (new `run_outputs/r6/l6/` and `scenarios/S6-L6.yaml`), and tests.

Nothing changed in:
- `runs/r6/top5/`, `top5.csv`, `runs/r7/` or `runs/r6/pareto_front.csv`;
- the R7 docs (delivery models, fiscal exposure, VfM) or fig09–fig11;
- `judge/`, `film/`, `prompts/`, `scenarios/` or `optimise/`;
- licences, the access model, `network/graph_params.yaml`, alignments, lines or stations;
- R9/R10.

No judge run, no tag, no push, no paid API, and no process killed except my own server on port 8799.

Two small deviations, both recorded:
1. Items 2–4 share `common/figures.py`, so they went into one commit (fa127b5).
2. `tests/test_s6_l6_score.py`'s protected-docs check is now limited to its own window (6149a8b..87cb9d0). Without that, it blocks this approved change. `tests/test_r8_l6_panel.py` guards the same areas from 87cb9d0 on.

Rebuilding the API fixtures also refreshed two unrelated line fixtures; I reverted them.

### Tests and checks
- `make test` green: ruff; **812 passed** (789 + 23 new: 9 in `tests/test_r8_l6_panel.py`, 7 in `test_api_dashboard.py`, 3 in `test_report_figures.py`, plus parametrised cases for fig16); docver 353 files; manifest 387 rows, no downloads.
- `report check`: PASS. Bilingual check: PASS (270 = 270). Disk 29 GiB free.

### Verifier
`red-team-verifier`, label VERIFY_R8_L6_PANEL, run in the foreground; report `docs/status/verify-R8_L6_PANEL.md`. **Pass 1: PASS** on all 10 criteria. It recomputed every number, confirmed fig07 and the source map are byte-identical, and checked mtimes to confirm no judge run.

### Cost
- Estimate for this run: about USD 25–40 list price (builder plus one verifier pass). Runaway guard USD 60, not approached.
- The coordinator adds the cost-log row.

R8_L6_PANEL: done

## STUDY_RJ_FAMILIES (6 Nov 2026; start HEAD 8dafdfe)
Run estimate: about USD 35–55 list price (one builder on claude-opus-5-5, one research subagent, verifier passes). Runaway guard USD 60. This estimate line was written at handoff, not at the start of the run as the prompt asked; recorded as a deviation.

A research and routing study: not a scored programme, not R9/R10. The judge was not run. No tag, no push, no paid model or API. No process was killed: the only processes started were three background routing jobs (PIDs 86067, 86071, 86075), which exited on their own. No server was started; ports 8765 and 8000 were not touched.

### Where the study lives
- **Note:** `docs/rj-routes-study.md`. Figures in `docs/study-rj/`; these are not in the R8 figure index.
- **Code:** `study/families.py`, `study/rj.py`. Parameters in `cities/ksa/assumptions/rj_study.yaml`.
- **Sketches:** `cities/ksa/alignments-study/` (corridor inputs, routed sidecars, `haram_markers.geojson`, README with credits). Scenarios in `scenarios/study/` (`all-families.yaml`, `rj-{lb,a,b,c1,c2}.yaml`).
- **Runs:** `runs/study/{families,rj}/`.
- **Registers:** sources S-rj-001…033 in `docs/sources/study-rj.csv`; assumptions A-rj-001…005 in `docs/study-rj/assumptions.md`; one manifest row, `osm-haram-markers-extract-2026-10-14`.

### Results
**All-families layout.** `S1-S5-all-families`: comparison layout, not the recommended programme; not scored. It is S1 plus 72 of the 73 R6_V3 library ids. The 73rd, jubail-two-stations, combines two S5 additions already drawn.
- S2: 23 corridors, 9,949.9 route-km.
- S3: 19 corridors, 3,075.1 route-km.
- S4: 20 corridors, 1,935.8 route-km.
- S5: 10 stations.
- Total: 14,960.9 route-km, summed over corridors with overlaps counted each time.

**Routed lengths** (frozen v1 weights `2b718ecb…`; all profiles feasible; no stitched chords; tunnel / viaduct km):

| route | stops | class | routed km | tunnel / viaduct km |
|---|---|---|---|---|
| RJ-LB | as-understood announced proxies | mixed | 967.4 | 24.9 / 25.9 |
| RJ-A | speed-oriented, no intermediate city | hsr | 887.2 | 14.7 / 17.8 |
| RJ-B | via Taif | hsr | 965.0 | 21.9 / 21.1 |
| RJ-C1 | via Taif + gateway SW on HHR | hsr | 975.9 | 25.1 / 25.9 |
| RJ-C2 | via Taif + gateway NW on HHR | hsr | 967.4 | 24.3 / 22.2 |

For reference, the S1 Landbridge (unchanged) is an 874.3 km great-circle chain scaled to 900 km.

**Non-stop in-vehicle P50** (R4 model × generic timetable factor; `times.csv`):

| route | 220 km/h | 250 km/h | 300 km/h | 350 km/h |
|---|---|---|---|---|
| RJ-A | 5:42 | 5:03 | 4:19 | 3:47 (P10 3:27, kinematic floor 2:57) |
| RJ-B | 6:18 | 5:37 | 4:53 | 4:22 |
| RJ-C1 | 6:30 | 5:50 | 5:07 | 4:36 |
| RJ-C2 | 6:21 | 5:40 | 4:54 | 4:23 |
| RJ-LB | 6:22 | 5:44 | — | — |

The S1 Landbridge as R4 models it, at 250 km/h, takes 5:07.
- No case reaches 2 h, even at its kinematic floor. Every P50 is inside the 2–9 h envelope.
- Air door-to-door is 3:11 with the block model (101 min), 3:20 with the 1:50 bound. The best rail door-to-door P50 is 4:57 (RJ-A at 350 km/h).
- Via-Taif penalty for through passengers, against RJ-A non-stop: +34–36 min (RJ-B), +35–38 min (RJ-C2), +47–49 min (RJ-C1).

**Capex, base P50** (cost register): RJ-A 82.3 bn SAR, RJ-B 93.2 (+13.2 %), RJ-C2 97.0 (+17.9 %), RJ-C1 98.7 (+19.8 %), RJ-LB 57.1 (mixed class). Uplifted P50 / P90: 106.6 / 366.2 to 127.8 / 444.4 bn SAR for the hsr routes. Ranges are in `capex.csv`.

**Siting recommendation (one paragraph).** A through Riyadh–Jeddah service keeps its through track and any through station outside the Haram boundary. The check used the 49 OSM marker boards: there is no official open polygon, and none was drawn. Every routed through track and every stop passes: the closest is RJ-C1 at 5.0 km from a board, and the gateway SW site is 5.3 km from one. HHR remains the branch into Makkah. If a Makkah-area call is wanted, the gateway belongs on the HHR alignment outside the boundary:
- **SW site:** 23.1 km along HHR from `hhr:makkah`, about 6 km beyond the HHR boundary board. It gives the shortest HHR link but needs the south-around descent from Taif (RJ-C1).
- **NW site:** near Bahrah, 45.5 km along HHR, 17.8 km from the nearest board. It is on the shorter north-around route (RJ-C2).

Both sites need a new HHR stop, which is not modelled (interchange rules and access model unchanged). Neither is on airport land (A-station-001). The announced Al-Jumum site is outside the boundary but has no HHR interchange.

### Decisions and deviations (recorded)
1. **Study scenario file names.** The files are `scenarios/study/all-families.yaml` and `rj-*.yaml`, not `S-all-families.yaml`. The citation checker reads `S-…` tokens as source ids, and the prompt's name was an example. The ids are `S1-S5-all-families` and `S1-study-rj-*`, which the scenario schema requires to start with `S` and a digit. Neither starts with S6.
2. **Registers kept beside the study.** `common.report build` reads `docs/assumptions*.md` and `docs/sources/index.csv` into the R8 annexes. Adding rows there made `annex-assumptions.md` stale, and rebuilding it would have changed an R8 reader-facing file. The study's sources (`docs/sources/study-rj.csv`) and assumptions (`docs/study-rj/assumptions.md`) therefore stay outside those files. As a result, `common.sources check docs/rj-routes-study.md` reports the S-rj ids as missing from `index.csv`, by design. A later integration can merge them if Tariq wants.
3. **`tests/test_r8_l6_panel.py` prompts check.** It now allows `prompts/STUDY_RJ_FAMILIES.md`, which the coordinator saved at 8dafdfe, before this run. The test failed at the start HEAD for that reason alone.
4. **Waypoints.** Two routing waypoints keep the least-cost paths outside the markers (A-rj-002). Gateways are snapped to the corrected HHR geometry (A-rj-003).
5. **350 km/h class.** It reuses the Talgo 350 kinematics with vmax 350 (A-rj-005).
6. **Curve limits** are recomputed on the joined path, so waypoint joins count.
7. **Commits per item.** `study/rj.py` serves items 3–7, so it went into the item 3 commit with later additions in the note commit. Item 2 (Landbridge note) and item 6 (economic note) are sections of the single study note commit.

### Tests and checks
- `make test` green: ruff; **829 passed** (812 + 17 new in `tests/test_study_rj_families.py`); docver 357 files; manifest 388 rows, no downloads. The README command ran (`network.skims` demo).
- `common.scenarios validate` passes on each file under `scenarios/study/`, one file at a time; directory mode cannot find the S1 baseline there.

### Untouched-areas evidence (`git diff --stat 8dafdfe HEAD`)
37 files changed, +4,591 / −1. The changes are:
- new study paths only: `study/`, `scenarios/study/`, `cities/ksa/alignments-study/`, `cities/ksa/assumptions/rj_study.yaml`, `docs/rj-routes-study.md`, `docs/study-rj/`, `docs/sources/study-rj.csv`, and `tests/test_study_rj_families.py`;
- one manifest row in `cities/ksa/sources.yaml`;
- the four-line allowance in `tests/test_r8_l6_panel.py`.

Nothing changed in any of these:
- `cities/ksa/lines/`, `scenarios/S1.yaml`, `network/graph_params.yaml`, `access_network.yaml`, `align_weights.yaml`, `cities/ksa/alignments/`, `cities/ksa/corridors/`;
- `runs/r6/top5/`, `runs/r7/`, `judge/`, `film/`;
- `docs/report/`, the summaries, the policy brief, the figure index, `web/`, `api/`;
- `docs/licences.md` and `.csv`, `docs/assumptions.md`, `docs/sources/index.csv`;
- R9/R10.

### Verifier
`red-team-verifier`, label VERIFY_STUDY_RJ_FAMILIES, run in the foreground; report `docs/status/verify-STUDY_RJ_FAMILIES.md`.

**Pass 1: 10/11 PASS.** The verifier:
- re-ran the running-time model for three routes and the S1 Landbridge row (identical);
- re-extracted the 49 markers from the registered extract (identical, Points only);
- reconciled the capex deltas, the 450/100 km/h arithmetic and the air figures.

The one FAIL was this status block, then incomplete: no test count, no diff evidence, no closing line, not committed. Both fixes are in a817617: this block is now complete, and the S-rj-012 locator wording now says "manned", as the cited page does.

**Pass 2: PASS (11/11).** Measured at a817617: protected-path diff empty; 829 passed; docver 358; manifest 388. The 37-file figure above is the content diff at 3217c44; at a817617 the diff is 39 files, the two extra being this status file and the verify report.

### Cost
- Estimate for this run: about USD 35–55 list price. Runaway guard USD 60, not knowingly exceeded.
- The coordinator adds the cost-log row.

STUDY_RJ_FAMILIES: done

## STUDY_RJ_SCORE (6 Nov 2026; start HEAD 6291a1c)
Run estimate: about USD 30–50 list price (one builder on claude-opus-5-5 plus foreground verifier passes; six local full-judge runs at USD 0, about 2–3 min each). Runaway guard USD 60.

Study sketch, not the recommended programme. Synthetic demand, uncalibrated: scenario comparison, not a forecast. Alignment limitation applies (`docs/rj-routes-study.md` §8). Nothing folded into R8, the summaries, the brief, the figure index or the dashboard.

### What was scored
Five replacement packages, each **S1\* + one RJ sketch instead of the committed Landbridge**, opened in 2030 (construction 2027; A-rj-008).
- **S1\*** = S1 without the committed Landbridge: existing lines (HHR, SAR North, SAR East) + Riyadh Rail Link + the Saudi GCC section.
- Increments are versus S1\*, not published S1; they are not tabled beside L1–L5.
- RJ-A/B/C1/C2 hsr, RJ-LB mixed; electrified double track; routed km from the sidecars.

### How (judge unchanged)
- Judge `v3-variants` sha256 `d9fef64384e2e25f…`: `optimise.judge verify` intact before and after (`logs/study-rj-score-judge-verify-{before,after}.log`); fingerprint checked before and after every run. `judge/` untouched.
- Seed 1, 10,000 draws, `--all-cases` (45 appraisal rows), about 42 s per run. Same `optimise/layout.py` evaluate path as S6_L6_SCORE, entered through the new harness `study/rj_judge.py`.
- **Landbridge omission:** only in `study/rj_judge.py`, only when the study replacement marker `study_rj_replace` is present. It wraps `access.railgraph.scenario_lines` so the judge's own S1 reference run is S1\*. It also resolves the sketch id to the routed scoring corridor and its cost run. Without the marker it changes nothing: a test shows S1 and the published top-5 L1 build byte-identical line lists, Landbridge included. `optimise.layout`'s default "S1 + items" is untouched. Every run's `meta.json` has `landbridge_omitted: true` and the marker name.
- **S1\* reference:** the judge's own S1 column inside the five runs, identical in all five (checked), written to `runs/study/rj/score/_s1-star/s1_star.json`. No separate run was needed; no published S1 number is used. S1\* 2050 medium: 14.45 M rail trips, HHR 11.04 M.
- **Running time:** routed chainage plus curve limits at the class line speed (hsr 300, mixed 250) and the generic factor, as in §5. The judge's end-to-end minutes equal the §5 P50 all-stop rows exactly (`inputs/check.json`).
- **Costing:** the §6 spec and costing files, re-run with the judge's own `costs.estimate`; identical draw for draw to `runs/study/rj/costs-s1/`.
- **Gateway skims (A-rj-007):** the frozen station skims lack the two gateway stops. 1,014 rows were added with the judge's own OSRM skim method; three existing stations recomputed with a max difference of 0. OSRM was started and stopped by `study.rj score-skims` only.
- **Terminal sites (A-rj-006):** the RJ terminals use the Landbridge's town-centroid placeholders. For scoring they take the Landbridge's A-r4-acc-004 placements (Jeddah with HHR Al-Sulaimaniyah, Riyadh with SAR Riyadh). The corridor files keep the placeholders; the access model is unchanged.

### Score (full judge v3; increments versus S1\*; SAR million, 2025 prices, PV 2026)

| sketch | robust NPV | NPV at P90 cost (low / med / high) | BCR P10 / P50 / P90 (medium) | capex P10 / P50 / P90 | added trips 2050 | sketch load 2050 | HHR 2050 (vs S1\*) | five-metro 120 gain | national reach 120 gain (reported only) |
|---|---|---|---|---|---|---|---|---|---|
| RJ-A | −84,338 | −271,115 / −266,885 / −262,869 | 0.05 / 0.23 / 0.80 | 63,119 / 106,611 / 366,237 | +3.94 M | 3.63 M | 11.52 M (+0.48) | 0.00 M | +0.00 M |
| RJ-B | −102,845 | −317,096 / −313,231 / −309,235 | 0.04 / 0.18 / 0.62 | 71,028 / 120,699 / 417,314 | +3.92 M | 4.08 M | 11.07 M (+0.04) | 0.00 M | +0.23 M |
| RJ-C1 | −100,036 | −329,422 / −324,563 / −319,466 | 0.05 / 0.23 / 0.79 | 74,707 / 127,770 / 444,346 | +5.00 M | 7.28 M | 8.92 M (−2.11) | 0.09 M | +0.23 M |
| RJ-C2 | −99,640 | −324,058 / −319,625 / −314,767 | 0.05 / 0.22 / 0.77 | 73,681 / 125,690 / 436,091 | +4.80 M | 5.46 M | 10.61 M (−0.43) | 0.00 M | +0.23 M |
| RJ-LB | −67,724 | −217,763 / −214,583 / −211,288 | 0.06 / 0.24 / 0.79 | 36,351 / 68,166 / 260,302 | +3.45 M | 3.48 M | 11.27 M (+0.24) | 0.11 M | +0.31 M |

Robust case: low population for all five. No NPV is positive at P50 or P90 cost in any population case. CO2 PV P50 (medium) and the via-Taif trade-off table are in `docs/rj-routes-study.md` §8a/§8c.

### Judge capex vs §6
They match: same routed sidecars, same 10,000 draws. The only difference is the percentile rule: the judge takes the nearest draw, §6 interpolates. The largest gap is 4.7 SAR m (RJ-LB P90; under 0.01 %). Table in §8b.

| sketch | judge P50 | §6 uplifted P50 | judge base P50 | §6 base P50 |
|---|---|---|---|---|
| RJ-A | 106,611 | 106,609 | 82,316 | 82,315 |
| RJ-B | 120,699 | 120,697 | 93,193 | 93,193 |
| RJ-C1 | 127,770 | 127,768 | 98,653 | 98,653 |
| RJ-C2 | 125,690 | 125,687 | 97,047 | 97,046 |
| RJ-LB | 68,166 | 68,165 | 57,095 | 57,095 |

### Decisions and deviations (recorded)
1. **Scenario file names:** `scenarios/study/replace-rj-{a,b,c1,c2,lb}.yaml`, not `rj-a-replace.yaml` (the prompt's name was an example), so the stacked `rj-*.yaml` glob does not catch them. Ids `S1-star-replace-rj-*`, baseline `S1-star`. Each passes `common.scenarios validate` on its own file.
2. **Harness entry instead of an optimise.search engine:** `optimise.search full` always builds "S1 + items" from the read-only judge copy. The study entry wraps the judge's functions at runtime instead. Nothing under `judge/`, `optimise/`, S1 or L1–L6 changed.
3. **Gateway skims and terminal placements** (A-rj-006/007), as above. Without the skims, RJ-C1/C2 could not be scored at all.
4. **`tests/test_r8_l6_panel.py` prompts check** now allows `prompts/STUDY_RJ_SCORE.md`, which the coordinator saved at 6291a1c, before this run. The test failed at the start HEAD for that reason alone (checked with the working changes stashed).
5. **A pilot RJ-A run** from a dirty tree (identical robust NPV −84,338) was moved to `runs/_superseded/study-rj-score-pilot-replace-rj-a-dirty/`. The final five ran at 06507ec (clean).
6. **No map:** each package has `scorecard.csv`; the existing `docs/study-rj/rj-routes-map.png` already shows the five routes.

### Untouched-areas evidence (`git diff --stat 6291a1c HEAD`, before this status block)
12 files, +1,621 / −5: `docs/rj-routes-study.md` (v1.1: §8 added; pointers in the intro, §6 and §7 only), `docs/status/main.md`, `docs/study-rj/assumptions.md` (A-rj-006…009), the five `scenarios/study/replace-rj-*.yaml`, `study/rj.py`, `study/rj_judge.py` (new), `tests/test_r8_l6_panel.py` (allowance), `tests/test_study_rj_score.py` (new).

Nothing changed in any of these:
- `judge/`, `optimise/`, `scenarios/S1.yaml`, `scenarios/S6-L6.yaml`, the stacked `scenarios/study/rj-*.yaml`, `all-families.yaml`;
- `cities/ksa/lines/`, `corridors/`, `alignments/`, `alignments-study/`, `access_network.yaml`, `network/graph_params.yaml`;
- `docs/report/`, the summaries, the policy brief, the figure index, `web/`, `api/`, `film/`, `prompts/`;
- `docs/licences.*`, `docs/assumptions.md`, `docs/sources/index.csv`, `docs/sources/study-rj.csv`, `docs/r6-l6-connected.md`;
- `runs/r6/top5/`, `runs/r6/l6/`, `runs/r7/` (mtime test).

No station moved in any file, no alignment added, no interchange threshold changed. No process was killed except the OSRM server `study.rj score-skims` started and stopped. No server, tag, push or paid API was used.

### Tests and checks
- `make test` green: ruff; **857 passed** (829 + 28 new in `tests/test_study_rj_score.py`); docver 359 files; manifest 388 rows, no downloads.
- Disk 28 GiB free.

### Verifier
`red-team-verifier`, label VERIFY_STUDY_RJ_SCORE, run in the foreground; report `docs/status/verify-STUDY_RJ_SCORE.md`. **Pass 1: PASS on every criterion; no FAIL.**
- It re-ran `make test` (857 passed) and `optimise.judge verify` (intact).
- It recomputed every cell of §8a–§8c and of this block from `score.json`, rounding included. It also recomputed the nearest-draw and interpolated capex percentiles from the cost draws.
- It confirmed the omission is gated on the study marker and that no protected path changed. The port-8765 dashboard (started before the run) is still listening; nothing was on port 8000.
- Observation, not a FAIL: the S1\* definition names the intercity lines. The Riyadh Metro is in `scenarios/S1.yaml` but outside the intercity demand model (A-demand-005), so it is not in the judge's S1 line set either way.

### Cost
- Estimate for this run: about USD 30–50 list price (builder plus one verifier pass; the six judge runs, including the superseded pilot, ran locally at USD 0). Runaway guard USD 60, not knowingly exceeded.
- The coordinator adds the cost-log row (`common.cost_log add`).

STUDY_RJ_SCORE: done

## R9 release preparation (7 Nov 2026; start HEAD 5edba39)

Approval: Tariq, 7 Nov 2026 (`prompts/R9_LAUNCH.md`, saved verbatim by the coordinator; task list `prompts/R9.md` v1.1). One run on `main`; no tag, no push, no remote, no Pages, no GitHub issue, no R10, no paid model; no TTS, render or model downloads. The permitted public source and tool reads were uv's local cache, one `uvx cffconvert` (open source, PyPI) for the CITATION.cff validation, and the Contributor Covenant 2.1 text fetched from GitHub (EthicalSource/contributor_covenant, as `CODE_OF_CONDUCT.md` records); no process killed (the dashboard step of `make demo` starts and stops its own API on a free port, never 8765 or 8000).

### What was done (commits on `main`)
| task | result | files |
|---|---|---|
| 1 README | rewritten: real goal, label up front, `make demo`, repository map, three-layer versioning, checkpoints and decision records, links (report, brief, EN/AR summaries, registers, credits), RJ study beside the report, the author publishes | `README.md` |
| 2 community files | CONTRIBUTING (uv, ruff, pytest, the 12 rules with rules 9 and 12 adapted for publication and marked, sources, assumptions, licence rows, region-sweep re-run), CODE_OF_CONDUCT (Contributor Covenant 2.1, fetched from the EthicalSource repository and diffed; contact placeholder), SECURITY, CITATION.cff (`version: r9`, no release date or repository URL; `uvx cffconvert --validate`: valid against CFF 1.2.0) | root |
| 3 credits and NOTICE | `common.licences credits` (`make credits`): `docs/credits.md` = 290 register items + 55 Python packages (uv.lock, installed metadata) + 159 JavaScript packages (`web/package-lock.json`); NOTICE gains a generated block of the 162 register items whose row names an attribution; `tests/test_credits.py` fails if either is stale; model ids redacted in the credits | `common/licences.py`, `docs/credits.md`, `NOTICE` |
| 4 good-first issues | GFI-001…054 for manual filing: data gaps (9 "not found", 21 unverified rows), 650 assumptions awaiting a source (+8 in the RJ study register), benchmark rows graded C/D (179 C, 38 D metric rows; 28 C, 6 D overrun rows), 906 grid-only register rows (24 at ≥ 10k named), the deferred SUMO rail check, dashboard polish, other open items, 46 licence blockers as owner decisions (Transit Costs: do-not-use note only) | `docs/good-first-issues.md` |
| 5 release checklist | steps for Tariq only: history (nothing to purge), the 74 tracked source tables under `data/` (≈ 19 MB, 29 PDFs) to confirm or purge, secrets and paths (none), third-party emails in `prompts/R9_LAUNCH.md`, commit author email, private working files that name model ids and the author's company, contact placeholder, licence blockers B1–B9 and the hard stop, CP6 and the policy-brief banner, Arabic summary internal-only, R10 out, tag `r9` by the coordinator, remote and push by Tariq | `docs/release-checklist.md` |
| 6 clean clone | see below | `Makefile`, `tests/localdata.py` |
| addendum 1 | EN/AR executive-summary banners only: reviewed on Tariq's request on 7 Nov 2026, signed off for internal use, not a public-release decision; CP6 draft sentences dropped; headers `Status: reviewed`; bodies unchanged; bilingual check 271 = 271; `tests/test_ar_render.py` and `tests/test_glossary_ar.py` pass | `docs/executive-summary.{en,ar}.md` |
| addendum 2 | Nabrah AI row only: commercial use, online publication and broadcast cleared for the public voices on a paid plan (S-nabrah-005: sender: the CEO of Nabrah.ai, 1 Nov 2026 09:38 AST; email addresses not copied into the register); attribution unanswered; training opt-out Enterprise-only; no cloning of a real person without written consent; B9 kept as a blocker (reason narrowed); every other row unchanged (`tests/test_fix_r8.py` now allows only this row to differ from tag r8); release note, blocker list, licences.md, sources index and report source annex regenerated | `docs/licences*`, `docs/sources/index.*`, `common/sources.py` (B9 reason text), `docs/report/annex-sources.md` |

### `make demo` (new)
`common.demo` on invented fixtures (`tests/fixtures/region_register.parquet`, `cba_case.yaml`, new `demo_inputs.yaml`, `tests/fixtures/api/`): screening (5 settlements → 4 long list → 4 short list, 10 weight-sweep corners) → the fixture CBA case with the real engine and registered parameters (100 draws; 60-year NPV P10/P50/P90 = −386 / −47 / 234 SAR million, invented) → the dashboard API on 127.0.0.1 (7 endpoints answered, each with its label), then stopped. About 2 s. `make demo-serve` keeps it on 127.0.0.1:8766 (builds `web/` when `web/node_modules` exists). CI runs `make demo` after `make test`.

### Clean-clone check (task 6)
`git clone . /tmp/ksa-railtwin-clean && cd /tmp/ksa-railtwin-clean && make setup && make test && make demo`, script `logs/r9-clean-clone.sh` (gitignored log `logs/r9-clean-clone-2.log`), clone of 884270a + the test-guard commit:
- First attempt: `make test` failed in the clone (21 failed, 3 errors): tests that read gitignored `runs/` metas, `data/ksa/costs/wb_NY.GDP.DEFL.ZS.json` and a pilot capture had no skip guard (CI never ran: no remote). Fixed: `tests/localdata.needs_local` skips them when those inputs are absent; the figure tests are keyed on the study run metas instead of on `runs/` itself (which `make demo` creates). The manifest check now defaults to `--allow-missing` only when `data/osm` is absent, so the README command works as written in a clone and stays strict in a full checkout.
- Second attempt (measured): clone 1 s; `make setup` 1 s (uv's local cache was warm; a machine without the cache downloads the locked wheels first); `make test` 103 s, rc 0 (791 passed, 70 skipped); `make demo` 2 s, rc 0; `make test` again after the demo 33 s, rc 0. Total 140 s. Disk: clone 794 MB, of which `.venv` 653 MB; free disk 30.6 → 30.5 GB.
- Main checkout: `make test` green (ruff, 861 passed, docver 364 files, manifest 388 rows strict) in 52 s.
- Attribution of the test counts (FIX_R9_COUNTS, 7 Nov 2026): 861 passed, docver 364 files, manifest 388 rows (main checkout) and 791 passed / 70 skipped (fresh clone) are the figures of the verifier run at c5c6efe (`docs/status/verify-R9.md`). They were not re-run at the final R9 HEAD f11a53c; the commits after c5c6efe (3a333c0, f11a53c) are documentation, the three issue templates and the cost-log row.

### Checks
- Files tracked: 1,693 at the final R9 HEAD f11a53c (`git ls-tree -r --name-only f11a53c | wc -l`); 1,689 was the count at the verifier's HEAD c5c6efe, and the verifier report plus the three issue templates added four files. `git ls-files` under `data/`/`runs/`/`movies/`: 74 files, all under `data/` (`data/README.md` and the README'd GASTAT and pilgrim source tables committed by earlier decisions; listed in the release checklist for Tariq's decision); none under `runs/` or `movies/`. No secrets (pattern scan), no `.env*`, no absolute home paths in tracked files.
- Registers: licences 290 Markdown rows = 290 CSV rows, 0 differ; sources index 2,078 rows (+1, S-nabrah-005); assumptions 765 rows (unchanged); manifest 388 rows OK.
- `git remote -v`: empty. No push, remote, release, tag, Pages site, issue, package entry or external post was made. Disk free: 29 GiB (`df -h ~`).
- Run-scoped test guards: `tests/test_r8_l6_panel.py`, `test_study_rj_families.py`, `test_study_rj_score.py` failed at the start only because the coordinator committed the R9 prompts; pinned to the last pre-R9 commit 4da3bcf (decision below).

### Decisions (R9 builder, 7 Nov 2026)
- Run-scoped "untouched since start" guards compare `START_HEAD..4da3bcf` (the last pre-R9 commit), as `tests/test_s6_l6_score.py` already did with its `END_HEAD`: they keep auditing their own runs, and R9's approved edits to the licence register and the executive-summary banners are not flagged.
- The Nabrah confirmation is recorded by sender name and role only; the email addresses in Tariq's verbatim prompt are not copied into any register (the prompt file itself is unchanged; listed in the release checklist).
- `docs/policy-brief.md` still says "Draft for review at checkpoint CP6; not for circulation": out of the addendum's scope (banners of the two summaries only), so left for Tariq (release checklist D).
- `CONTRIBUTING.md` adapts two phrases of rules 9 and 12 (the company name and the model labels) and marks them; every other rule is verbatim.
- The generated report annex `docs/report/annex-sources.md` keeps its generator's header (v1.0, 4 Nov 2026); only the S-nabrah-005 row and the index hash changed.
- `.github/ISSUE_TEMPLATE/` (owned by R9): three Markdown templates (bug report, data gap or source, question about a method or figure) for when the repository is published; nothing is created on GitHub.

### Verifier and close
- `red-team-verifier` (`docs/status/verify-R9.md` v1.0): **Overall: PASS** (0 FAILs) on pass 1. It re-ran the fresh clone itself (clone 1 s, setup 1 s, `make test` 103 s rc 0, `make demo` 2 s rc 0; 791 passed, 70 skipped; clone 776 MB, `.venv` 638 MB), `make test` in the main checkout (861 passed, strict manifest 388 rows), `make demo` twice with seed 1 (identical outputs except `created_utc`), the bilingual check (271 = 271), `licences credits --check`, `cffconvert --validate`, the one-row Nabrah diff, the unchanged release categories (46 BLOCKER before and after) and seven good-first-issue counts.
- Observations acted on after the PASS: `docs/STATUS.md` "Last updated" line brought to 7 Nov 2026; the commit-count wording in the release checklist and CP7 item 4 ("521 at the start of R9"); the owned `.github/ISSUE_TEMPLATE/*` files created. Left as recorded: `make test` hides the pytest summary line (GFI-036); `MANIFEST_FLAGS` keys on `data/osm` alone; the 29 tracked PDFs and the policy-brief banner are CP7 decisions for Tariq.
- Cost-log row: appended by `run_track.sh` at run end (not by this builder).
- No remote, push, tag, release, Pages site, issue or external post was made; `git remote -v` is empty.

R9: done


## FIX_R9_COUNTS (7 Nov 2026; start HEAD 8441ca7)

Prompt: `prompts/FIX_R9_COUNTS.md` v1.0 (Tariq's text, saved verbatim by the coordinator at 8441ca7). Documentation only; no tag, push, remote, R10, film, licence-row, code or test change.

Measured at the start HEAD 8441ca7 (`git rev-list --count <rev>` / `git ls-tree -r --name-only <rev> | wc -l`):

| revision | what | commits | tracked files |
|---|---|---|---|
| 4da3bcf | last pre-R9 commit | 514 | 1,676 |
| 5edba39 | R9 launch | 515 | 1,677 |
| c5c6efe | R9 verifier HEAD | 528 | 1,689 |
| f11a53c | final R9 HEAD | 530 | 1,693 |
| 8441ca7 | this run's start (FIX_R9_COUNTS prompt added) | 531 | 1,694 |

Corrections (only `docs/status/main.md`, `docs/STATUS.md`, `docs/release-checklist.md`):
1. R9 block, Checks: tracked files 1,693 at f11a53c; 1,689 kept as the count at c5c6efe (verifier report + three issue templates = four files).
2. "521 at the start of R9" (commits) replaced in `docs/STATUS.md` CP7 item 4 and `docs/release-checklist.md` A with the measured commit counts 514 at 4da3bcf, 515 at 5edba39, 530 at f11a53c. The historical observation line in the R9 block ("521 at the start of R9") is left as a quote of the old wording.
3. R9 block, approval line: the Contributor Covenant 2.1 fetch from GitHub (as `CODE_OF_CONDUCT.md` records) added beside uv's local cache and `uvx cffconvert`; "no TTS, render or model downloads" stated separately from those permitted public source and tool reads.
4. R9 block, clean-clone section: 861 passed / docver 364 / manifest 388 and 791 passed / 70 skipped attributed to the verifier run at c5c6efe; not re-run at f11a53c (later commits: documentation, issue templates, cost-log row).

No test asserts any of the corrected counts (`grep` of `tests/` for 1,689/1689/521: only unrelated numeric fixture values), so no test changed.

Verifier: `red-team-verifier` (`docs/status/verify-FIX_R9_COUNTS.md`), pass 1: all counts re-measured and equal; items 1–4, only-three-files, no tag, no remote, headers and `make test` (rc 0; docver 366, manifest 388) PASS. Its one FAIL was this missing status line, which is written after the verifier by the usual sequencing; added here, then a short pass 2. No cost-log row by this builder (appended at run end, as for R9).

FIX_R9_COUNTS: done


## FIX_LICENCE_CITE_FACTS (7 Nov 2026; start HEAD 34394cd)

Prompt: `prompts/FIX_LICENCE_CITE_FACTS.md` v1.0 (Tariq's text, saved verbatim with a header by the coordinator at 34394cd; not changed by this run). Register only. No tag, push, remote, R10 or film work.

**Row check.** Each row number was confirmed against `docs/licences.csv` (the numbers `docs/licences-blockers.md` v1.1 and `docs/licences-release.md` §5 print) before editing. Every number matched the group Tariq put it in, so no row was skipped. The edit script asserted each item-name prefix.

**Clearing method (the Chrome precedent).** The approval column reads "Tariq, 7 Nov 2026 AST (citation of published facts / study tables; FIX_LICENCE_CITE_FACTS)". Rows 1, 153, 203, 246 and 290 use their own decision text instead. Each row's status text records the decision. No licence was invented. Two kinds of column change were needed so the existing rule reads the decision:
- `commercial_use` "unclear" → "n/a" (no licensed reuse; facts cited only). This follows the existing convention of the press rows 121–123.
- `open` "unclear" → "n/a" (facts only, as on row 133).

On two rows, the `licence` text had to be reworded without changing its meaning:
- 132: "unclear: terms not read" → "terms not read (no licence statement captured)".
- 196: "unclear (World Bank … CRU TS licence to confirm)" → "World Bank open data terms (commonly CC BY 4.0); CRU TS licence not confirmed".

**Rows changed (44; id → item, grade before → after):**

| id | item | grade |
|---|---|---|
| 1 | Claude Code (orchestrator row; renamed) | BLOCKER → OBLIGATIONS |
| 7 | Saudi Open Data portal (data.gov.sa) | BLOCKER → OBLIGATIONS |
| 117 | SAR network page (published facts) | BLOCKER → OBLIGATIONS |
| 118 | HHR booking site sar.hhr.sa (published facts) | BLOCKER → OBLIGATIONS |
| 119 | RCRC website (published facts) | BLOCKER → OBLIGATIONS |
| 120 | Makkah Region Emirate, Al-Jumum governorate page | BLOCKER → OBLIGATIONS |
| 121 | MEED and MEED Projects (press) | BLOCKER → OBLIGATIONS |
| 122 | ENR (Engineering News-Record) (press) | BLOCKER → OBLIGATIONS |
| 123 | Trade and business press (Construction Review Online, Gulf Construction Online, Railway Ga | BLOCKER → OBLIGATIONS |
| 125 | GLMM (Gulf Labour Markets, Migration and Population) census tables | BLOCKER → OBLIGATIONS |
| 127 | Saudipedia | BLOCKER → OBLIGATIONS |
| 132 | Saudipedia (Arabic) emirate article: governorate count (corroboration) | BLOCKER → OBLIGATIONS |
| 133 | Search-extract web sources for economic roles (UNESCO, GSN, Maritime Executive, Wikipedia  | BLOCKER → BLOCKER |
| 136 | Asharq Al-Awsat article (Q3 2026 rail passengers) | BLOCKER → OBLIGATIONS |
| 141 | Arab News, Gulf Industry, CruiseMapper, Saudipedia (search snippets, facts only) | BLOCKER → OBLIGATIONS |
| 146 | Wikivoyage Duba and CruiseMapper Duba port schedule (search snippets) | BLOCKER → OBLIGATIONS |
| 147 | UNESCO World Heritage Tentative List entry 6575 (Ancient Walled Oases of Northern Arabia) | BLOCKER → BLOCKER |
| 148 | Visit Saudi, Saudi Tourism Guide, Kupi, New Civil Engineer (search snippets) | BLOCKER → OBLIGATIONS |
| 149 | datasaudi.sa Tabuk region page (search snippet) | BLOCKER → OBLIGATIONS |
| 153 | Nabrah AI (Nabrah Studio TTS, voice cloning; public voices Daniah, Norah, Abdullah) | BLOCKER → BLOCKER |
| 168 | Saudipedia, RCU (rcu.gov.sa), ROSHN (roshn.sa), MODON, RCJY, GACA pages (economic-node fac | BLOCKER → OBLIGATIONS |
| 183 | DfT TAG optimism bias workbook (reference-class curves, data: Oxford Global Projects 2020) | BLOCKER → OBLIGATIONS |
| 188 | Trade press and company releases (MEED guest pages, Railway Gazette, IRJ, Construction Rev | BLOCKER → OBLIGATIONS |
| 191 | MoF FY2026 pre-budget statement: medium-term fiscal estimates table (total expenditure 202 | BLOCKER → BLOCKER |
| 193 | IMF/World Bank PFRAM 2.0 conventions (firm vs contingent liabilities; worst-case contingen | BLOCKER → BLOCKER |
| 194 | GASTAT Labour Market Statistics Q4 2025 (LFS Excel tables): extracts transcribed into docs | BLOCKER → OBLIGATIONS |
| 195 | GASTAT Labour Market Statistics bulletins Q4 2023 and Q1 2025 (PDF): figures cited | BLOCKER → OBLIGATIONS |
| 196 | World Bank CCKP CRU TS 4.08 monthly tasmax climatology for SAU (values cited in docs/socia | BLOCKER → OBLIGATIONS |
| 197 | UNESCO World Heritage List open dataset (whc001), Saudi Arabia records: names, inscription | BLOCKER → BLOCKER |
| 201 | xlogit (Python mixed logit) | BLOCKER → NOT IN RELEASE |
| 203 | EPSG Geodetic Parameter Dataset (read through PROJ proj.db bundled in pyproj) | BLOCKER → OBLIGATIONS |
| 204 | HHR Train Schedule page (Oct 2018), Internet Archive Wayback Machine capture | BLOCKER → OBLIGATIONS |
| 205 | Schittenhelm (2011), Planning With Timetable Supplements in Railway Timetables | BLOCKER → OBLIGATIONS |
| 221 | SAPTCO Annual Report 2025 (English PDF) | BLOCKER → OBLIGATIONS |
| 234 | GACA press release: 19 million air passengers in Hajj 1446 (HTML capture) | BLOCKER → OBLIGATIONS |
| 235 | SPA news item N2326094: HHR Hajj 1446 seats (HTML capture) | BLOCKER → OBLIGATIONS |
| 236 | Wikipedia airport pages (27 Saudi airports, 'Airlines and destinations' tables) | BLOCKER → BLOCKER |
| 237 | Press and secondary pages for running times, rolling stock and bus cities (Railway Gazette | BLOCKER → OBLIGATIONS |
| 238 | Sources for the economic roles of the 24 created register rows (Royal Commission, Wikipedi | BLOCKER → BLOCKER |
| 246 | OpenStreetMap layers for the alignment cost surface (landuse urban, protected areas, milit | BLOCKER → BLOCKER |
| 260 | Handbook on the external costs of transport (CE Delft for the European Commission) | BLOCKER → BLOCKER |
| 262 | IMF World Economic Outlook database (KSA real GDP and population growth) | BLOCKER → BLOCKER |
| 263 | Saudi Global Ports / SAR intermodal dry-port tariff announcement | BLOCKER → OBLIGATIONS |
| 290 | Alignment sidecars weights v2 (cities/ksa/alignments-v2/) [r8 register gap] | BLOCKER → OBLIGATIONS |

**Special rows.**
- **1 (B8):** the item was renamed "Claude Code (Anthropic): orchestrator and coding assistant", and the attribution column now credits it the same way. The model ids were removed from the row; the mapping stays in CLAUDE.md, the agent files and the cost log. `NOTICE` and `docs/credits.md` gained the credit line (generated).
- **153 (B9):** the approval and status now record "attribute Nabrah on published audio". The written publication/broadcast clearance and the no-cloning obligations are unchanged.
- **201 (xlogit):** the status now starts "not used". Citation of the unused candidate is approved; it is not installed, and the MIT vs GPL-3.0 conflict is left unresolved. Grade: NOT IN RELEASE.
- **203 (EPSG):** CRS definitions are read through PROJ/pyproj only; the dataset is not redistributed.
- **246 and 290 (B7):** the obligations now say the committed sidecars (`cities/ksa/alignments/`, `alignments-v2/`) are released as ODbL share-alike derived databases, with OSM credit on every map. The `FLAG:` wording was removed.
- **Not touched:** 189 (Transit Costs: still a hard stop and BLOCKER; the release note and checklist note that citing it as a searched-but-excluded source is approved) and 94 (XTTS-v2: still BLOCKER, non-commercial).

**Measured BLOCKER total: 13 (was 46), not the expected 2.** `common.sources.release_status` grades 11 rows BLOCKER through its hard-coded `NAMED_BLOCKERS` list. That list matches on the item name before it reads any approval or status. The 11 rows are 133, 147, 197 and 238 (B3), 191 (B1), 193 (B2), 262 (B4), 260 (B5), 236 (B6), 246 (B7) and 153 (B9). Their answers are recorded in the register and in `docs/licences-release.md` §1. I did not edit the rule to force a different grade (prompt addendum: no code change). Clearing these 11 needs a small change in `common/sources.py`, for example letting a named flag yield when the row's approval cites this decision; that is Tariq's call. The other two BLOCKER rows are 189 and 94, as required. Row 290 (B7, not matched by name) is now OBLIGATIONS. Row 1 is OBLIGATIONS because the rename removed the `claude-` match. Grades after this run: OBLIGATIONS 141, NOT IN RELEASE 60, COMPATIBLE 53, VERIFY 23, BLOCKER 13 (290 rows).

**Regenerated (generators only):**
- `docs/licences.md` (`common.licences sync`; header v1.12)
- `docs/licences-release.md` table (§5) via `common.sources licences-release --write`
- `docs/licences-blockers.md` (`common.licence_blockers write`). Its header stays v1.1 because the version string lives in the generator code, which this run may not change. The Transit Costs dependency scan grew from 16 to 24 hits: all are mentions in R9-era files and in this run's text; no figure uses the source.
- `docs/credits.md` and `NOTICE` (`make credits`)

The report annexes did not need regeneration: `test_report_build` passes.

**Hand edits:**
- `docs/licences-release.md` v0.5: an answer line before each B1–B9 *Question* (the question text is unchanged, so the blockers parser still reads it); the §1 fact-citation paragraph, the §2 press and Nabrah sentences and the §6 Nabrah note.
- `docs/STATUS.md` v1.44 CP7 item 5: 46 → 13.
- `docs/release-checklist.md` v1.3, section C: blocker counts by group, the Transit Costs citation note and the scan count 24, the B7 and B9 answers.
- Not changed: the README body, credits prose, executive summaries, film/, R8 and the RJ study. `docs/good-first-issues.md` still says 46 (section H). It is neither status nor the release note, so it was left for Tariq.

**Tests (no code change):**
- `tests/test_fix_r8.py::test_no_licence_status_changed_since_r8`: the allowed set was widened from the Nabrah row to exactly these 44 rows (row 1 is matched under its r8 name by prefix). Every other row must still equal tag r8.
- `tests/test_report_release.py::test_named_blocker_rows_are_blockers`: the B8 pattern must now match no row, because B8 was answered by the rename. This is not a count assertion. The rename Tariq asked for broke the old expectation, so the test now guards against model ids returning to the row.

**Checks:**
- `make test` rc 0: ruff, pytest, docver 368, manifest 388
- `common.licences check`: 0 differ
- `licences credits --check`: up to date

**Verifier pass 1** (`docs/status/verify-FIX_LICENCE_CITE_FACTS.md`): 1 FAIL (C5b). Row 153's `attribution` cell still said "unanswered", and so did `NOTICE`, `docs/credits.md` and the B9 paragraph of the release note. Fixed:
- Row 153's attribution now reads "Nabrah AI (Nabrah Studio voice) credited on published audio (Tariq, 7 Nov 2026 AST)". The §6.4 AI-disclosure clause is kept.
- The B9 "Still open … (unanswered)" sentence is reworded.
- `licences sync`, the release table, the blockers file and `make credits` were regenerated. `make test` rc 0.

The section-5 reason string for row 153 still says "attribution requirement still unanswered": that text is the B9 entry of `NAMED_BLOCKERS` in `common/sources.py` (code, not changed in this run). It goes with the 11-row named-flag decision for Tariq.

**Verifier pass 2**: **Overall PASS**, recorded in `docs/status/verify-FIX_LICENCE_CITE_FACTS.md` v1.1.
- C5b is closed.
- Only row 153 changed in the fix; the 44-row set and the 13 BLOCKER total are unchanged.
- `make test` rc 0 (docver 369 including the verifier report; manifest 388).
- No tag; no remote.

Open items for Tariq:
1. Whether the `NAMED_BLOCKERS` flags B1–B7 and B9 should yield to a recorded answer. This is a code change in `common/sources.py` and would bring the total to 2 (189, 94).
2. `docs/good-first-issues.md` §H still says 46.

The cost-log row is appended at run end.

FIX_LICENCE_CITE_FACTS: done

## FIX_LICENCE_NAMED_FLAGS (7 Nov 2026; start HEAD 3314577)

Prompt: `prompts/FIX_LICENCE_NAMED_FLAGS.md` (Tariq's text, saved verbatim with a header by the coordinator at 3314577). One short run on `main`.

**Rule change (`common/sources.py`):** new `NAMED_FLAG_ANSWERED = ("7 Nov 2026 AST", "FIX_LICENCE_CITE_FACTS")` and `named_flag_answered(r)`. A NAMED_BLOCKERS match returns BLOCKER only when the row's `approval` cell does not hold **both** strings. If it holds both, the row is graded by its columns as usual. The NAMED_BLOCKERS list is kept. The B9 "why" now reads "attribution answered: attribute Nabrah on published audio"; the `Nabrah` pattern is unchanged.

**Addendum rows 1, 153, 203, 246, 290:** each `approval` cell already contains both "7 Nov 2026 AST" and "FIX_LICENCE_CITE_FACTS". No register cell was edited. `docs/licences.csv`, `docs/licences.md`, `NOTICE` and `docs/credits.md` are byte-identical to the start HEAD.

**Named-flag rows, before → after** (row numbers as in `docs/licences-release.md` §5):

| row | flag | before | after | reason after |
|---|---|---|---|---|
| 133 | B3 | BLOCKER | OBLIGATIONS | share-alike on derived databases or copied text |
| 147 | B3 | BLOCKER | OBLIGATIONS | attribution or notice as stated |
| 153 | B9 | BLOCKER | OBLIGATIONS | proprietary; approval recorded |
| 191 | B1 | BLOCKER | **BLOCKER** | own columns: `licence` = "unclear (no licence statement captured)" |
| 193 | B2 | BLOCKER | **BLOCKER** | own columns: `licence` = "unclear (IMF terms of use; not captured)" |
| 197 | B3 | BLOCKER | OBLIGATIONS | share-alike |
| 236 | B6 | BLOCKER | OBLIGATIONS | share-alike |
| 238 | B3 | BLOCKER | OBLIGATIONS | share-alike |
| 246 | B7 | BLOCKER | OBLIGATIONS | share-alike (ODbL) |
| 260 | B5 | BLOCKER | OBLIGATIONS | attribution or notice as stated |
| 262 | B4 | BLOCKER | OBLIGATIONS | proprietary; approval recorded |

B8 still matches no row (row 1 renamed). The test guard is kept.

**Measured BLOCKER total: 4** (13 before). The rows are 94 Coqui XTTS-v2 (commercial use N), 189 Transit Costs Project (commercial use N; hard stop), 191 MoF FY2026 and 193 PFRAM. The prompt expected 2. Rows 191 and 193 carry the approval, but the generic "terms unclear" rule still grades them on their `licence` cell. Per the prompt, no licence was invented and the rule was not widened. **For Tariq:** record a licence/terms value for rows 191 and 193 (for example "no licence statement; facts cited only"), or accept them as disclosed blockers.

**Generated:**
- `docs/licences-release.md`: table regenerated, v0.6. The §1 grade sentences for B1–B7 and B9, the §2 Nabrah sentence and the §6 Nabrah note were corrected to the new grades; the questions are unchanged.
- `docs/licences-blockers.md`: v1.2. The generator `VERSION` line in `common/licence_blockers.py` is the only change in that file.
- `make credits`: no change.

**Counts updated:**
- `docs/STATUS.md` v1.46, CP7 item 5: 13 → 4.
- `docs/release-checklist.md` v1.4, section C: 13 → 4, with the groups.
- `docs/good-first-issues.md` v1.1: line 569 46 → 4, with the four rows named and the R9 table and lists below marked as the v1.1 snapshot; the line-674 heading reads "4 rows (46 at R9), 2 with a B-number (B1, B2)".
- Not changed: the README body, executive summaries, film/, R8, the RJ study and the register answers.

**Tests:** in `tests/test_report_release.py`:
- `test_named_blocker_rows_are_blockers` is rewritten: an answered row grades the same as the row with its item name neutralised; an unanswered row is BLOCKER; the B8 guard is kept.
- New: `test_named_flag_yields_only_to_both_strings` (both strings → graded by columns; either string alone or none → BLOCKER; answered with unclear licence → BLOCKER).
- New: `test_named_flag_rows_with_and_without_the_approval` (the real Nabrah row with and without its approval; the B9 reason no longer says "unanswered").
- New: `test_transit_costs_and_xtts_stay_blockers`.
- New: `test_measured_blocker_total` (== 4).

**Checks:**
- `make test` rc 0: ruff, pytest 865 passed, docver 370, manifest 388.
- `common.licences check`: 0 differ.
- `licences credits --check`: up to date.

`git diff --stat 3314577` (before this status block): 8 files, +120/−68:
- `common/licence_blockers.py` 2
- `common/sources.py` 13
- `docs/STATUS.md` 4
- `docs/good-first-issues.md` 6
- `docs/licences-blockers.md` 51
- `docs/licences-release.md` 52
- `docs/release-checklist.md` 4
- `tests/test_report_release.py` 56

No tag; no remote; no push; no process killed.

**Verifier pass 1** (`docs/status/verify-FIX_LICENCE_NAMED_FLAGS.md`): C1–C9 PASS. One FAIL, C10: the closing label line was missing, because it was being held until the verifier ran. The line below closes it. Verifier pass 2 confirms. The cost-log row is appended at run end.

FIX_LICENCE_NAMED_FLAGS: done

## FIX_LICENCE_CITE_TERMS (7 Nov 2026; one run on main, WT=0)

Cost estimate (runaway guard USD 60): about USD 8-15 (two CSV cells, three generators, four count sentences, tests, one verifier pass). Start HEAD f109f16.

**Done (Tariq, 7 Nov 2026; prompt `prompts/FIX_LICENCE_CITE_TERMS.md`):**
- Item 1, commit 2a11ed2. Row 191 "MoF FY2026 pre-budget statement": the `licence` cell went from `unclear (no licence statement captured)` to `no licence statement captured; facts and derived study table cited only; MoF table not republished`.
- Item 2, commit f700cb7. Row 193 "IMF/World Bank PFRAM": the `licence` cell went from `unclear (IMF terms of use; not captured)` to `IMF terms of use not captured; concepts cited only; Excel tool not used`.
- In items 1 and 2, no other column changed: open, commercial_use, obligations, status and approval are byte-identical. A field-level diff of `docs/licences.csv` against f109f16 shows only column 3 (`licence`) of these two rows.
- No MoF or IMF licence and no permission to republish is claimed.
- Mirrors regenerated by the generators: `docs/licences.md` (`common.licences sync`), and `docs/credits.md` plus the NOTICE attribution block (`common.licences credits`). The credits check failed until they were regenerated, because it embeds the licence cell. The register items are unchanged.

**Grades** (`common.sources.release_status`, measured independently):

| row | before | after |
|---|---|---|
| 191 MoF FY2026 | BLOCKER (commercial use or terms unclear in the register) | OBLIGATIONS (attribution or notice as stated in the register) |
| 193 PFRAM | BLOCKER (commercial use or terms unclear in the register) | OBLIGATIONS (attribution or notice as stated in the register) |

**Measured BLOCKER total: 2** (4 before): 94 Coqui XTTS-v2 and 189 Transit Costs Project. Both are BLOCKER because commercial use is N. Not changed: rows 94 and 189, every approval cell, `named_flag_answered`, `NAMED_BLOCKERS`, and every other `release_status` rule.

**Item 4** (commits after f700cb7; see `git log f109f16..`):
- `docs/licences-release.md` v0.7: table regenerated. The B1 and B2 sentences now say the row is graded by its columns since FIX_LICENCE_CITE_TERMS, and that no licence is claimed.
- `docs/licences-blockers.md` v1.3: regenerated. The only code change is the generator's `VERSION` line in `common/licence_blockers.py`.
- Counts 4 → 2 in `docs/STATUS.md` v1.48 (CP7 item 5), `docs/release-checklist.md` v1.5 (section C) and `docs/good-first-issues.md` v1.2 (section H line and the line-674 heading). The R9 snapshot in section H is still labelled as the v1.1 snapshot.

**Tests** (`tests/test_report_release.py`):
- The named-flag tests are kept.
- `test_measured_blocker_total` changed from 4 to 2 and now names the two rows.
- New, parametrised over rows 191 and 193: `test_citation_only_licence_cells_are_not_blockers`. It checks the exact cell, that the cell has no "unclear", that the row grades OBLIGATIONS, and that an "unclear" licence cell makes the row BLOCKER again.
- `test_transit_costs_and_xtts_stay_blockers` is unchanged.

**Checks:**
- `make test` rc 0: ruff, pytest 867 passed (865 before), docver 372, manifest 388 (no downloads).
- `common.licences check`: 0 differ.
- `licences credits --check`: up to date.

`git diff --stat f109f16` (with the then-uncommitted start line of this block; without it: 11 files, +61/−37): 12 files, +65/−37:
- NOTICE 9
- `common/licence_blockers.py` 2
- `docs/STATUS.md` 4
- `docs/credits.md` 4
- `docs/good-first-issues.md` 6
- `docs/licences-blockers.md` 15
- `docs/licences-release.md` 14
- `docs/licences.csv` 4
- `docs/licences.md` 4
- `docs/release-checklist.md` 4
- `docs/status/main.md` 4
- `tests/test_report_release.py` 32

Not touched: film/, judge/, runs/, prompts/ (except the coordinator's commit of this prompt before start), rows 94 and 189. No tag, no push, no server started, no process killed. Cost estimate: about USD 8-15 (guard USD 60).

**Verifier pass 1** (`docs/status/verify-FIX_LICENCE_CITE_TERMS.md`): C1–C9 PASS. One FAIL, C10: the hand-maintained header of `docs/licences.md` was not bumped. Fixed: the header is now v1.13 (FIX_LICENCE_CITE_TERMS). The diff-stat note was also clarified (11 files, +61/−37 without this block's start line). Verifier pass 2 follows.

**Verifier pass 2** (`docs/status/verify-FIX_LICENCE_CITE_TERMS.md` v1.1): PASS on C1–C10 at e436fc0. `make test` rc 0, with 867 tests passing. The cost-log row is appended at run end by the coordinator, from this run's result JSON, as in the previous licence runs.

FIX_LICENCE_CITE_TERMS: done

## STUDY_EXTRA_TRAVEL (7 Nov 2026; one run on main, WT=0)

Cost estimate (runaway guard USD 60): about USD 25-45 (one OAG page fetch, baseline extract from stored runs, a post-processing induced-demand sensitivity on stored generalised costs, a visitor/land-entry memo, the study note, tests, verifier passes). Start HEAD e90ef4a (tag r9 at 42f810f plus the prompt commit).

**Done (Tariq, 7 Nov 2026; prompt `prompts/STUDY_EXTRA_TRAVEL.md`; study note `docs/extra-travel-study.md` v1.1).** Labels on every table: synthetic demand, uncalibrated: scenario comparison, not a forecast; not the official ranking.

- **Item 1, OAG as verified** (commit 33666e0; https://www.oag.com/busiest-routes-world-2025, fetched 7 Nov 2026 13:24 AST, HTTP 200, page SHA-256 1d6a7b3c…; rows S-xt-001…007 in `docs/sources/study-extra-travel.csv`):
  - Jeddah–Riyadh is "fifth placed" in OAG's 2025 top ten busiest routes by scheduled seats, and the fastest-growing route in that top ten.
  - Seats: 9.8 M (regional table 9,819,558), both directions; +13 % vs 2024, +22 % vs 2019.
  - It is the only top-ten route outside Asia Pacific and the busiest domestic route in the Middle East (regional table).
  - Fare: average economy fare USD 95 one way, +27 % (annual average of the lowest available fare, sampled in the first week of December).
  - Cairo–Jeddah: 5.8 M seats, second cross-border, +71 % vs 2019. Dubai–Riyadh: 4.5 M, seventh cross-border.
  - OAG's Japan caution is quoted.
  - No difference from the recollection figures. The only wording point: the page says "fifth placed", not "fifth busiest domestic route".
- **Item 2, baseline** (`runs/study/extra-travel/baseline/rj_baseline.json`; judge v1-r5 = the published S1-vs-S0 engine). Pair = Riyadh-metro zones × Jeddah-metro zones, both directions (A-xt-001). 2050 medium, S1:
  - one-way trips: rail 424,947; air 3,474,082; car 734,110; bus 24,344; total 4,657,483;
  - passenger-km: rail 382.3 M; air 2,960.4 M; car 702.6 M;
  - S0: air 3,777,702 and no rail.
  - Model air trips are 0.35 (S1) and 0.38 (S0) times OAG's 2025 seats. Not comparable quantities, so nothing is subtracted.
  - Rail fare 269.9 SAR (0.30 SAR/km, A-mode-037) against model air 277.8 SAR and OAG USD 95 ≈ 356 SAR at 3.75 (indicative).
- **Item 3, extra-travel range** (`runs/study/extra-travel/induced_summary.csv`). Elasticity on the composite generalised cost: −0.15 / −0.25 / −0.40 / −0.70, uncalibrated, TAG M2.1 bracket (A-xt-003). Tourism, leisure/VFR and business only.
  - Proportional allocation: +0.23–1.12 M trips a year nationally (2050 medium), about 76 % by car. Extra NPV P50 −293 to −1,394 SAR m (mainly carbon).
  - Rail-only bound: extra NPV P50 +516 / +1,476 SAR m.
  - S1-vs-S0 NPV P50 stays between −61,564 and −58,826 (published −60,103).
  - The zero case reproduces the published inputs and results exactly.
  - Riyadh–Jeddah pair: +13,400–63,100 trips a year.
- **Item 4, visitor and land-entry range** (`runs/study/extra-travel/land/land_scenarios.csv`). Hajj is held fixed in every row.
  - GASTAT 1440–1441 AH land ports: Jordan border 36.8 %, Gulf 24.1 %, Yemen 39.1 %.
  - S1 rail paths to Makkah exist from Al-Haditha, Al-Batha and King Fahd Causeway. Halat Ammar, Al-Raqi and Al-Wadiah have none. S0 has none.
  - S1 entry and exit rail trips: 21,911 a year (frozen 0.0286) up to 509,246 (labelled prior-high rail share, observed maximum land share, +25 % what-if volume).
  - "If counted" fare: SAR 11.7 m central to 368.6 m (high, per km). Outside the CBA.
  - Visitor-days: unknown (no representative stay length).
- **Not done (decision, cost guard):** the optional thicker layout (L1) or RJ-LB-vs-S1\* run. It needs the v3 phased layout adapter under a new wrapper; the S1-vs-S0 bracket already gives sign and scale.
- Commits: 33666e0 (item 1), 01431c4 (item 2), 4503992 (items 3–4 registers), 0e11f65 (status start), edcf6da (item 5 note), then the tests commit and this block.
- **Untouched-area evidence**, `git diff --stat e90ef4a HEAD` (at the tests commit): 9 files, +1,460, all new study files except this status file:
  - `cities/ksa/assumptions/extra_travel_study.yaml`, `docs/extra-travel-study.md`, `docs/sources/study-extra-travel.csv`, `docs/study-extra-travel/assumptions.md`;
  - `study/extra_travel{,_core,_judge}.py`, `tests/test_study_extra_travel.py`;
  - `docs/status/main.md`.
- Not touched: film/, judge/ (fingerprint checked before and after every call), runs/r6/, runs/r7/, runs/cba/, prompts/, licences, R8 files, frozen trip rates, A-intl-003, S1/HHR geometry. No paid model or API, no Transit Costs figure, no server started, no process killed, no tag, no push.
- `make test` rc 0: ruff; pytest 883 passed (867 before, +16); docver 376; manifest 388 rows (no downloads registered; the OAG page and the TAG PDF were read for citation only and not stored).
- Cost estimate: about USD 30–45 (guard USD 60).
- **Verifier** (`docs/status/verify-STUDY_EXTRA_TRAVEL.md`): **PASS** on C1–C10 at 8ff51a0.
  - It re-fetched the OAG page (same SHA-256) and the TAG PDF.
  - It re-derived the GASTAT land-port totals and recomputed Tables 2a, 3a and 4a with 0 mismatches.
  - It confirmed the frozen files are unchanged, the v1-r5 judge is intact, and no tag, push or killed process occurred.
  - Observation fixed after the PASS: the TAG rows' `published` cell now also says the PDF cover is dated November 2025 (gov.uk "last updated" 11 Dec 2025).
  - Not this run's step: the cost-log row is appended by the coordinator at run end.

STUDY_EXTRA_TRAVEL: done

## FIX_TRAILER_AR (Tariq, 12 Nov 2026; `prompts/FIX_TRAILER_AR.md`; post-close fix on main)

**Base.** Main checkout at d9bc3a4 (after CLOSE_R10 a8fc3c6), tree clean, runaway guard USD 200. R10 stays done; `docs/status/r10.md` keeps `R10: done` as its last line and points here.
- Set-up: `film/renders` and `film/audio` were created in the main checkout as symlinks to the existing external `renders/` and `audio/` (no copy, no new directory). `git status` stays clean of them (gitignored).
- Volumes at the start: internal 26 GiB free, Extreme SSD 917 GiB free. Both stayed above 10 GB throughout (lowest: internal 23.2 GiB, SSD 846 GiB).
- Paid-TTS tally before the first call (`docs/cost-log.csv` PAID rows): ElevenLabs 3.18, Nabrah 3.88, combined **USD 7.06**.

**Item 1, t-08 (ar).** «… يبقى صافي قيمته الحالية موجب حتى مع التكلفة المرتفعة: بين 4.0 و5.6 مليار ريال.» → «خيار المحطات الثلاث يرجّع تكلفته حتى لو ارتفعت: المنافع تزيد على التكاليف بين 4.0 و5.6 مليار ريال.»
- Figures (4.0; 5.6) and source (`run:runs/r6/top5/top5.csv`) unchanged.
- The wording is the main cut's: m-08-02 «حتى لو ارتفعت التكلفة، تظل ترجّع تكلفتها» and the sh-08-51 caption «المنافع تزيد على التكاليف».
- Full tashkeel in `speech_text`; `native_review = pending`. Logged in `story-edits.csv` and `ar-rewords.csv` (text and speech_text rows).
- **Decision (builder).** "About 6 riyals back per riyal" is not spoken. The validator requires identical figure_values for ar and en t-08, and the English trailer had to stay byte-identical. The "6" is already on screen at that moment in the sh-08-51 caption (S-r10-056; `rounding-log.csv` m-08-02, 5.9618).
- A first draft that spoke the "6" phrase was voiced (14.4 s). It would have made the trailer 91.7 s, over the 90 s ceiling, so it was shortened before any render.
- Re-voiced with Nabrah Daniah (same role voice): 12.0 s, −16.36 LUFS.
- Read-back (local whisper-large-v3-turbo, offline): CER 0.032. Whisper glues the figures as "4.05.6". Prompted for number words, it returns «أربعة فاصلة صفر وخمسة فاصلة ستة» twice, once with a prompt biased toward the wrong figures (3.0 / 7.4). So the audio is correct.
- Whisper environment: the old `/tmp/r10-voice` venv was half-purged by macOS, and an ephemeral uv env on the ExFAT SSD failed on `._` sidecars. The env therefore ran from the internal uv cache (`uv run --no-project --with mlx-whisper==0.4.3`). Weights went into the SSD `cache/hf` (about 1.6 GB, registered model; `film/licences-r10.csv` row 27). The failed SSD attempt left an unused partial uv build tree under the SSD `cache/uv` (not deleted).

**Item 2, Arabic trailer credits.** `film/sim.py` `closing_credits("ar")`: the George/ElevenLabs line is removed. The credits now read «التعليق الصوتي: أصوات نبرة العامة دانية ونورة وعبدالله (العربية)», and the closing notice stays. sh-08-54 re-rendered (ar only). Frame checked.

**Item 3, re-assembly.** sh-08-51 (ar; 13.4 s, was 11.0 s) and sh-08-54 (ar) re-rendered. Edit list, render manifest (0 figures not found), subtitles (`film.subs check` PASS, `align-qa` PASS with the old t-07 warning) and social burn rebuilt; `trailer.ar.pdf` re-rendered. Old files are in `renders/_superseded/*.pre-fix-trailer-ar-20261112.*`.
- **trailer-ar** `out/ksa-rail-twin-trailer-ar.mp4`: 89.3 s, −16.07 LUFS / −1.84 dBTP, SHA-256 64cf4389fb8d36895e4024628540a64227bfb25fa1ba79bccf7014f77e2f8ef1 (was ee3f81d4…, 86.9 s).
- `out/social/ksa-rail-twin-trailer-ar.subs.mp4`: SHA-256 68087af6b8a73dc27330609131495f6c259d35025110a78f55042d70beda634c.
- `.srt` (social copy = `film/subs/trailer.ar.srt`): SHA-256 3d85fc35ffe50d10c09e06e45df42d06ee80702fb76f52d937dc37686a84e7bf.
- `out/script/trailer.ar.pdf`: SHA-256 0dbae5ec1c67b90b78fe8298005d0e4d1912034ba7e6dfeeb8cf8f6aed6acadc.
- **Hash-checked before and after (all files under `out/`, every narration WAV, every trailer shot):** the only changes are those four files, `trailer-ar/t-08.wav`, two new raw-cache WAVs and shots sh-08-51 / sh-08-54 (ar).
- **Byte-identical:** main-en 540c5e41…, main-ar 391f72bf…, trailer-en 78802cd5…, their social copies, covers and the other PDFs. Hash lists are in `logs/fix-trailer-ar/` (gitignored).

**Item 4, inflected jargon.** New test `tests/test_film_jargon.py` (6 tests) and `scripts/film_final_asr.py`. ASR transcripts of the four final cuts' audio are in `film/voice/readback/final-*.txt` (local, offline; each records its MP4's SHA-256, checked by a test).
- It checks the patterns tashkeel-insensitively across these public outputs: scripts, `lines.csv` text and speech, `say.csv`, subtitles, captions, credits, transcripts, the social SRTs and the script PDFs.
- Allow-list: the single closing notice only. Result: no hits.
- **For Tariq:** the English trailer t-08 says "stays positive even at high cost". That is a finance-sense "positive". It is left as is because trailer-en had to stay byte-identical and the item lists only Arabic «موجب/سالب».

**Item 5.** `prompts/CLOSE_R10.md` v1.1: the addendum's absolute home path became `git -C .` (from the main checkout's root), with a header note; Tariq's text is unchanged. The `VERBATIM_PROMPTS` exemption is removed from `tests/test_hygiene.py`; the hygiene test passes.

**Item 6.** `git tag -a r10-final 92c5472`, with the message from the old tag object (raw message `cmp`-identical; `git tag -n99` output identical). `git rev-parse r10-final^{}` = 92c5472f7364462fd59b5023df2952cb86be7ffb. `git tag -d r10` (was 082d856). Branch `r10` (45b4dc3) and its worktree are kept; `r10` is no longer ambiguous.

**Paid TTS.** This run: Nabrah USD 0.03 (0.02 + 0.01; limit 0.05), ElevenLabs 0 (no call). Totals: ElevenLabs 3.18, Nabrah 3.91, **combined USD 7.09** of 60. Keys were read only inside the TTS process from the gitignored `.env`.

**Checks.** `make test` green at 80b3567: ruff and format; pytest 1074 passed, 0 failed, 0 skipped; docver 410 files; manifest 388 rows. Also passing: `film.script validate --strict-runs`, `film.subs check`, `align-qa trailer-ar`.

Commits: d8e2589 (item 5), ee9bbe5 (item 1), f7ae34a (item 2), 6717fa7 (item 3), 7356021 (item 4), 80b3567 (`docs/film.md` v1.10), then this block. No push, no remote, nobody contacted, no process killed that this run did not start.

**Verifier (`docs/status/verify-FIX_TRAILER_AR.md`, red-team-verifier, read-only): VERIFY_FIX_TRAILER_AR: PASS** (pass 1, at 40cd82e). It recomputed every hash, re-ran `make test` (1,074 passed), re-ran the t-08 read-back (audio says 4.0 and 5.6), checked the credits frame and the tag object. Notes for Tariq: (1) "about 6 riyals" is not spoken in t-08 (on screen only), a reasonable but non-literal reading of the addendum; speaking it would need the English line re-voiced too; (2) English t-08 "stays positive"; (3) `film/voice/timing/trailer-ar.csv` gained `voice_id`/`model` columns from the current `film.voice` writer (filled for t-08 only; cosmetic).

FIX_TRAILER_AR: done

## PUBLISH_PREP (Tariq, 12 Nov 2026 AST; `prompts/PUBLISH_PREP.md`; one run on main, WT=0; start HEAD a1d36aa)

Goal: make the repository ready for a public GitHub release. This run prepared only: no remote, no push, no publication, no export branch or folder, no history rewrite. Full findings and decisions: `docs/publish/checklist.md`.

**Item 1, secrets and personal data (full history).** Scope: 689 commits on all refs (including the merged `r10`) and 18 annotated tags. Tools: gitleaks 8.30.1 and trufflehog 3.99.8 (installed with Homebrew; `--no-verification`), plus a regex scan over every reachable blob. Findings: 16 rows (S1–S16). There are **no real secrets**: 11 tool hits are all false positives (6 `stations_key` digests, now allowlisted in `.gitleaks.toml`, so the re-scan finds 0; a UUID in a news URL; bytes in an xlsx). `.env` was never committed and never read. Home paths: 5 files, history only. Third-party vendor emails: 2 in `prompts/R9_LAUNCH.md`, redacted on main (bdfc214), and 1 in history only. Author email on 689 commits and 18 tags. Private company name and code names appear only as rule text and grep patterns (66 + 29 files; to be redacted in the export). One vendor executive's name appears as licence evidence (Q4). `main` was not rewritten. Two export options are given as text; B is recommended.

**Item 2, what ships.** Keep, drop and redact calls with reasons are in checklist §2. Drop (export only): 2 copied news pages and 4 DataPulse relays (`docs/publish/export-exclude.txt`). Redact in the export: the private names (R2). Keep: 61 GASTAT tables, code, registers, documents and the audit trail. Out (untracked): `logs/`, `runs/`, `judge/`, audio, video, model caches. Licence check: no committed item is non-redistributable after the drops; the 2 BLOCKER rows (94, 189) are unused.

**Item 3, TrafficTwin.** `docs/publish/traffictwin.md` and `traffictwin-references.csv` (550 lines in 245 files). The only run-time code path is the optional Jeddah coupling; its path is now overridable by `TRAFFICTWIN` (3a8fe84) and its test skips. Nothing new was vendored.

**Item 4, CP7 items.** Public-release banners on the policy brief and the report (1c6e9db). Arabic and English summaries carry public-use wording with "native Saudi review pending" (bilingual-check 273 = 273; bidi-probe 0 wrong; render refreshed, 32884cd). One `MAINTAINER-CONTACT` placeholder in CoC and SECURITY.

**Item 5, README.** A "Try it" README with headline, disclaimer, quick start, expected output, map, reproduction (`docs/publish/reproduce.md`), credits, licence and citation. `CITATION.cff` validates (cffconvert, schema 1.2.0); `CONTRIBUTING.md` v1.1 (de32b8b).

**Item 6, clean clone.** `env -i` with PATH and an empty temp HOME; no `.env`, no `data/`, no `runs/`, no TrafficTwin. Run A at 85afd41: setup 28 s, test 120 s, demo 2 s, exit 0; 920 passed, 154 skipped, 0 failed. Run A2 at 76bb464: same counts. Export dry run B2: 914 passed, 160 skipped, 0 failed, gitleaks clean. Fixes needed along the way: 897bd30 and 76bb464 (Chrome and missing-input tests skip instead of failing). Temp folders deleted.

**Item 7.** `docs/publish/checklist.md` v1.0 holds the push steps (repo `ksa-rail-twin`; create it private, check it, then make it public; Option B commands) and the open questions Q1–Q9.

Commits: 1c6e9db, 32884cd, 897bd30, 3a8fe84, a2f8f82, de32b8b, bdfc214, 85afd41, fbc92d5, 76bb464, cb8d45b, then this block. Paid TTS: no call (combined total stays USD 7.09). Nobody was contacted. The only process stopped was this run's own `gitleaks dir` scan.

**Verifier (`docs/status/verify-PUBLISH_PREP.md`, red-team-verifier, read-only).** Pass 1 at 9e2975d: FAIL on criterion 4 only. The reference table was stale (545 rows vs 550 after the README and CONTRIBUTING rewrite). All other criteria passed, including the verifier's own clean clone (setup 16 s, test 122 s, demo 2 s; 920 passed, 154 skipped, 0 failed) and an independent history scan that matched S1–S16 with nothing missed. Fixed in a53c606: table regenerated, counts updated, §1 counts pinned to the scan commit. **Pass 2 at a53c606: VERIFY_PUBLISH_PREP: PASS.** The verifier's precision note (generation commit wording) was applied in `traffictwin.md` v1.3 with this block. Cost-log row: added by the coordinator from this run's result, as usual.

PUBLISH_PREP: done

## PUBLISH_PREP_URL (Tariq, 12 Nov 2026 AST; `prompts/PUBLISH_PREP_URL.md`; one run on main, WT=0; start HEAD b9f4e5e)

Addendum to PUBLISH_PREP: the public repository is `https://github.com/alturkestani/KSA-RailTwin`. PUBLISH_PREP had not set a URL (README clone line `<repository URL>`, CITATION without `repository-code`), so this run set it.

- `README.md`: CI badge and link (`.github/workflows/ci.yml`), clone command, licence section. `CITATION.cff`: `repository-code` and `url`; `version` and `date-released` stay for Tariq (Q7); cffconvert valid (schema 1.2.0). Neither file carries a docver header.
- `docs/publish/checklist.md` v1.3, §7: push commands as text in two variants. **Variant (b) applies** (S5, S6, S7, S10 in history): push the clean export (Option B folder recommended, or Option A orphan branch), never `main`, no tags. Variant (a) (push `main` and tags) is printed for completeness only. If the rename from `-KSA-RailTwin` has not happened, Tariq renames first or uses the current name in the same commands. The Option B export and redaction block is unchanged.
- The README and CITATION edits moved referenced lines, so the dependency reference table in `docs/publish/` was regenerated (551 lines in 245 files; one extra row is the PUBLISH_PREP pass-2 status block) and its companion note updated to v1.4. Decision log entry in `docs/STATUS.md` v1.53.
- `make test` rc 0 (docver 417 files, manifest 388 rows). No network call to GitHub, no remote (`git remote -v` empty), nothing pushed, nobody contacted, no paid call, no process stopped.

Commits: 20ac17c, then this block.

**Verifier (`docs/status/verify-PUBLISH_PREP_URL.md`, red-team-verifier, read-only): VERIFY_PUBLISH_PREP_URL: PASS** (pass 1, at 20ac17c; 8 of 8 criteria; pytest 1074 passed, 0 failed). Its notes O1 (variant (a) would also publish the drop-list files and unredacted names) and O2 (Option A writes the remote into the private repository's shared config) were applied as wording in checklist v1.3. O3 (status line and cost-log row) is closed by this block and the coordinator.

PUBLISH_PREP_URL: done

## PUBLISH_EXPORT (Tariq, 12 Nov 2026 AST; `prompts/PUBLISH_EXPORT.md`; one run on main, WT=0; start HEAD 66deba0 on 5353a97)

Tariq answered checklist §8 Q1–Q9 and approved the public export. Answers applied on `main`, one commit per answer; export built as a new standalone repository; **no remote, no push, no tag**.

**Item 1, answers on `main`.**
- Q1 98d7af4: `SECURITY.md` v1.2 and `CODE_OF_CONDUCT.md` v1.2 point to GitHub private vulnerability reporting (Security tab, form URL); no email. It has to be enabled on github.com before the push (checklist §10).
- Q2 51912ec: CP6 closed (checklist §4, `docs/STATUS.md` R8 row).
- Q3 9d74440: `CLAUDE.md`, `.claude/`, `prompts/`, `docs/status/` and the cost log are published with R2.
- Q4 ca70ea8: the vendor executive's name is replaced by "the CEO of Nabrah.ai" in all 8 files (the two verbatim prompts get a header note); report annex rebuilt.
- Q5 8bc4d8d and 5e61f1b: the relays stay on the drop list. S-cp2-gastat-001 is marked "superseded for citation: cite GASTAT directly" (-007/-008/-002/-003; identical values, C-gastat-001). A-jazan-003 and A-screen-035 now cite GASTAT. The licence row's `used_in` notes the drop; it was first written to `status`, which `tests/test_fix_r8.py` freezes since r8, so it moved. `data/ksa/tables/gastat/README.md`, `index.md`, `licences.md` and both annexes are regenerated. Code and region registers keep the relay id as provenance (decision: rewriting them would change committed study inputs).
- Q6 afc5d32: TrafficTwin is "the author's optional private companion project (not public; not required …)" in README, CONTRIBUTING, NOTICE and CITATION (no link). Licence rows 16/156/287 keep the URL, labelled private. Nothing vendored. Reference table regenerated (now 553 lines in 246 files after e73b183).
- Q7 6131524: `CITATION.cff` version 1.0.0, `date-released` 2026-11-12 (cffconvert valid); CHANGELOG 1.0.0 section. **Noreply flag:** the plain `alturkestani@users.noreply.github.com` form links only for accounts whose noreply address dates from before mid-2017. Newer accounts need `<ID>+alturkestani@users.noreply.github.com`. Not checked online. If GitHub shows the commit unlinked, run the one-line amend in checklist §8 Q7 in the export folder.
- Q8 e47cd14 and 933b3a5: figure inputs ship under `docs/publish/figure-inputs/` (`.gitignore` un-ignores that path only). The 105 files were traced with an audit hook on the figure build, plus `runs/r6/top5/L1/score.json` (fig06's numbers; without it, its test failed instead of skipping in the first clean-clone run). Total 106 files, 21,647,100 bytes; largest 11,093,472 bytes. Includes `SHA256SUMS`, a README and licence row 291 (`tests/test_fix_r8.py` allows that one new row). `reproduce.md` v1.1: level 2 = figure inputs (exact), level 3 = full archive on Zenodo, DOI `10.5281/zenodo.[TO BE FILLED BY THE AUTHOR]`. List with sizes in checklist §9.
- Q9 60af569: "code published; native Saudi review of the Arabic pending; films follow the review" in the README (release-status note), CITATION, CHANGELOG, checklist and `docs/film.md` v1.11.
- Also: b4d533d `scripts/publish_export.sh`; 83fc742 checklist v1.4 §10 (procedure, pre-push steps, the two push commands as text); e73b183 STATUS decision entry and reference table.

**Item 2, export.** `scripts/publish_export.sh` from source commit **e73b183** → `~/Documents/Projects/KSA-RailTwin-public`. The folder did not exist before: a first build from b4d533d (commit c716f8d) was removed by this run after its clean-clone run found the fig06 test gap; it was rebuilt after the fix. Steps: `git archive` (1,997 files) → drop list (6 files) → **1,991 files** → R2 on 68 text files, 158 matches. Every match was reviewed before the build: they are the prohibition sentences, the verifiers' grep patterns, a banned-word list in `tests/test_report_figures.py`, and the script's own patterns. 0 binaries contain a name, so none was skipped. Residue check: empty. One commit: **41164cd015330ffcda306cf4dd9c2e5aabc37fcb**. Logs in `logs/publish-export/` (gitignored). Size: 99,671,951 bytes tracked, `.git` 63 MB.

**Item 3, checks on the export.**
- Residue grep (names, `/Users/[a-z]`, `/home/[a-z]`, vendor email domains): prints nothing. `/Users/` appears only in grep patterns and placeholders.
- Emails in text files: only noreply forms (`alturkestani@users.noreply.github.com`, the `<ID>+` and `username` examples in the checklist, `noreply@anthropic.com` in two verifier notes) and `git@github.com` (SSH notation in two verifier notes). The GASTAT/SPA PDFs keep the publishers' institutional contact lines (S8).
- gitleaks 8.30.1 `git` on the export history: **no leaks found** (with and without `-c .gitleaks.toml`).
- trufflehog 3.99.8 `git --no-verification`: **0 verified secrets, 5 unverified hits, all known false positives**: one UUID in a public MEES article URL (4 files; S2) and bytes inside a GASTAT xlsx (S3). So it is not a literal 0. Excluding those detectors or paths would hide the evidence, so they are reported as found.
- `git log --format='%an <%ae>'`: exactly 1 commit, `Tariq Alturkestani <alturkestani@users.noreply.github.com>` (author and committer). `git rev-list --all --count` = 1. Tags 0, remotes 0.
- Clean-env proof (`git clone` of the export into `$TMPDIR`; every step under `env -i PATH=<uv only>:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin HOME=<empty temp folder>`; no `.env`, SSD, TrafficTwin or `RAILTWIN_RUNS_ROOT`):

| step | exit | wall |
|---|---|---|
| `git clone` | 0 | 1 s |
| `make setup` | 0 | 16 s |
| `make test` (ruff, format, pytest, docver 420, manifest `--allow-missing` 388) | 0 | 130 s |
| `make demo` | 0 | 2 s |
| evidence: `uv run pytest -o addopts= -q -rs` | 0 | 44 s: **914 passed, 160 skipped, 0 failed** |
| reproduce level 2: copy figure inputs, `shasum -c` (0 not OK), `common.figures build`, `git status` | 0 | 15 s: **0 changed files (byte-identical)** |
| figure tests with the inputs present | 0 | 2 s: 45 passed, 7 skipped |

Skips, all with reasons: `runs/`/run outputs absent, STUDY_RJ runs absent, local data absent, Chrome unusable under the empty HOME, "start HEAD not in this clone" (squashed history), and the dropped relay. Temp clones were deleted afterwards.

**Private repository.** `git remote -v` empty. 18 tags unchanged; `r10-final` → 92c5472. History is this run's commits on top of 66deba0/5353a97 (no rewrite). `make test` green on `main` at e73b183 (rc 0; docver 420; manifest 388).

**For Tariq.**
- R2 is exact by design. Six verifier reports also carry other business-related words as grep terms only, with no content (3 terms; superseded by FIX_EXPORT_NAMES, which moved every such term to the gitignored list).
- `docs/licences-blockers.md` (generated 7 Nov) still says "register of 290 rows" (now 291). Its BLOCKER count (2) is unchanged. It was not regenerated, because a full regeneration also re-scans local run metas.

Paid calls: none (paid TTS stays USD 7.09). Nobody contacted. No process stopped except this run's own scan.

**Verifier (`docs/status/verify-PUBLISH_EXPORT.md`, red-team-verifier, read-only): VERIFY_PUBLISH_EXPORT: PASS** (pass 1 at 4a00ed4; 9 of 9 criteria). It rebuilt the export independently from e73b183 (`diff -r` 0 lines, 189 binaries `cmp`-identical) and re-ran gitleaks (0) and trufflehog (0 verified; the 5 unverified hits are the known S2/S3 false positives, which it judges to meet "0" in substance, not literally). Its own clean clone: setup 18 s, test 149 s, demo 2 s, rc 0; 915 passed, 159 skipped, 0 failed (one test more passes than in this run's clone, a Chrome-related skip). It confirmed the level-2 byte-identical figure rebuild and the private repository unchanged (no remote, 18 tags, `r10-final` → 92c5472, `make test` green). Notes: O2 generated docs keep their generation-date headers; O4 the export's `CLAUDE.md` reads "no the author's company content" (exact R2, cosmetic); O6 the blockers note's row count (flagged above). The cost-log row is the coordinator's.

PUBLISH_EXPORT: done
