> **Document version:** docs/status/verify-REGION_NAJRAN.md v1.1 | 31 Oct 2026 | Author: red-team-verifier | Status: verified

# Verifier report: REGION_NAJRAN (region sweep of Najrān, slug `najran`)

Reviewed read-only in worktree `.worktrees/r2-najran` (branch `r2-najran`, HEAD `8b68418`) on 31 Oct 2026 with `.venv/bin/python`. Files under review: `cities/ksa/regions/najran.parquet` / `.csv`, `docs/regions/najran.md`, `docs/assumptions-r2-najran.md`, `docs/sources/r2-najran.csv`, `docs/status/r2-najran.md`, `screening/sweeps/najran/build.py`, `write_docs.py`. Nothing was edited except this file.

## 1. Commands

| command | exit | time | output line |
|---|---|---|---|
| `.venv/bin/ruff check screening/sweeps/najran` | 0 | 0.1 s | `All checks passed!` |
| `.venv/bin/ruff format --check screening/sweeps/najran` | 0 | | `2 files already formatted` |
| `.venv/bin/ruff check .` / `ruff format --check .` | 0 / 0 | | `All checks passed!` / `403 files already formatted` |
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/najran.parquet` | 0 | 1.0 s | `ok   najran.parquet: 13 rows, 7 governorates` |
| `.venv/bin/python -m common.docver check docs` | 0 | | `docver OK: 102 files` (status block says 101: it was written before this verify file existed; the four new docs carry headers) |
| `.venv/bin/python -m pytest -q` | 1 | 67 s | `2 failed, 3 errors` — all `FileNotFoundError` on gitignored files absent from this worktree (`data/ksa/pilot-qassim/raw/citypop_admin.html` × 3 in `tests/test_cp2_gastat_primary.py`; `data/ksa/costs/wb_NY.GDP.DEFL.ZS.json` × 2 in `tests/test_costs_register.py`). No test touches Najrān code or data. `verify-CP2_PREP.md` line 97 records `285 passed` on the main checkout at the same HEAD. |
| `.venv/bin/python -m common.manifest verify` | 1 | | 63 × `FAIL ...: file missing` for gitignored `data/` entries (pilot-eastern/qassim/nb raw files, costs, benchmarks, hhr, `osm-ksa-rail`, `osm-gcc-admin-extract`, `osm-gcc-places-extract`). **No FAIL concerns a Najrān input:** the rows the sweep reads (`gastat-census2022-ta1-governorate-xlsx` line 4359, `gastat-census2022-ta1-city5k-xlsx` line 4376, `worldpop-sau-2020-100m-unadj-constrained` line 242, `osm-gcc-2026-10-14` line 7 of `cities/ksa/sources.yaml`) are not in the FAIL list and their files are present (the two GASTAT primary xlsx are tracked; `data/osm` and `data/ksa/geo`, `data/ksa/grids` are symlinks to the main checkout). The two `osm-gcc-*-extract` FAILs are R1a sub-extracts the sweep does not read. The status block describes this correctly. |
| README command | n/a | | The milestone has no README command; its command is the `validate --strict` call above. |
| Determinism | | | `build()` re-run in memory (no write) and diffed cell by cell against the committed Parquet: `rebuild vs committed parquet diffs: [] 0`; header 7/7. The build takes no `--seed` because nothing is stochastic (table lookups and haversine only). |

## 2. Acceptance criteria (prompt + region-sweep skill)

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | Governorate count reconciles to GASTAT | **PASS** | Parquet metadata `{'governorates_gastat': '7', 'governorates_listed': '7'}`; 7 distinct `governorate` values in 13 rows (Najran, Sharurah, Hubuna, Khubash, Yadamah, Badr Al Janub, Thar), each with an `is_governorate_centre` row. Primary export `census2022_TA1_governorate_primary.xlsx` (151 data rows = 150 governorates + `Total`): Najran 421,902 (row 17), Sharurah 100,199 (38), Hubuna 24,823 (112), Yadamah 16,160 (133), Thar 13,391 (137), Badr Al Janub 7,991 (148), Khubash 7,834 (149); sum 592,300. The export has no region column, so membership rests on S-073 (citypopulation.de admin page, WebFetch 31 Oct: 7 rows, same seven values, region total 592,300) and Saudipedia S-najran-003 (WebFetch: "Six governorates fall within ... Najran Province", i.e. 6 + capital). Both ways sourced; `A-najran-006` says so. |
| 2 | Every settlement ≥ 10k in the official table appears; ≥ 5k tagged; no population without source id and type | **PASS** | City export `census2022_TA1_city5k_primary.xlsx` (273 data rows = 271 cities + Other + Total): Najran 381,431; Sharurah 89,456; Al Mishaliah 23,252; Hubuna 12,738; Al Wadiah 8,365; Khubash 7,182 — all six are rows with `pop_type official`, `pop_source_status verified`, `pop_source S-cp2-gastat-008`; the four ≥ 10k carry `tag_10k true`. (The `Badr` 30,494 / 58,259 rows are Madinah's Badr, not Najrān.) R1a universe `settlements.parquet`: 187 Najrān settlements; 13 have official or grid population ≥ 5,000 and all 13 are register rows (`ge5k in universe but not in register: set()`); the other 174 are < 5,000 on both figures. 2010 cities Hairat Al Solam (5,820) and Taslan (5,284) are `unmatched` in `runs/gastat/apply/cities2010_growth.csv` and absent from the 2022 city export (grep `Hair|Tasl|Salam`: empty) — correctly listed as a gap, not guessed. `pop without source/type/year: 0`; `tag_5k` equals `population >= 5000` on all rows; `tag_10k` equals `population >= 10000 and pop_type != grid` on all rows. |
| 3 | No committed/hypothetical line called existing; every economic role has a source tying it to the town | **PASS** (one judgement item) | `cities/ksa/lines/landbridge.yaml`: `layer: committed`, `status: announced`, `source: S-054`; every row's `nearest_committed_station` reads `landbridge:muwai, Muwai/Moya, announced stop (S-062)`; S-062 (index.csv) names Muwai with no location, as stated. `nearest_existing` points only to `hhr` and `sar-east-passenger`. grep for "existing" in `docs/regions/najran.md` / status returns only the column names and the sentence "not an existing or built one". 13 roles, 13 with an `S-` source; each resolves in `docs/sources/*.csv`. Ties checked against `economic_nodes.parquet`: Najran airport `airport-eam-najran` (S-cp1-100;S-r1a-210, 21.9 km), MODON `modon-najran` (S-r1a-204;S-r1a-210, 13.4 km), `univ-najran` (S-r1a-221;S-r1a-210;S-r1a-222, 34.5 km), Sharurah airport `airport-shw-sharurah` (2.4 km from the row); `administrative` ← S-najran-001 governorate table; `border_crossing` ← S-najran-010 (WebFetch 31 Oct: page exists, Governor of Najran at Al-Wadeeah crossing, datePublished 2023-07-06; the CSV row says "date not captured" — it could be filled). **Judgement item, not a FAIL:** the `heritage` role (Hima, S-r1a-205) is tied to the Najrān city row only by R1a's `nearest_town_en` and `A-najran-005`; Hima's point is 82.0 km from Najrān and 47.2 km from Thār (a screened `tag_5k` row). The register flags it (Needs Opus judgement 9); Opus should decide whether the role moves to Thār or stays. |
| 4 | Parquet, CSV and Markdown table agree; register validates | **PASS** | `validate --strict`: ok. Parquet vs CSV: 13/13 rows, identical `osm_id` order, `parquet/csv scalar mismatches: 0`, roles and sources strings equal. Markdown tables A and B (13 rows each) regenerated from the Parquet and compared cell by cell (names, node, lat/lon to 5 dp, population + type/year/status, tags, screened, three distance/road-minute pairs, roles, terrain, exclusion): `md mismatches: 0`. |

## 3. Population rule and other checks

| check | verdict | evidence |
|---|---|---|
| Primary city figures `official` + `verified` | PASS | `primary rows official+verified: True 6` |
| GASTAT-relayed wins over grid | PASS | Yadamah (relayed 4,983, grid 7,695) and Badr Al Janub (2,709, grid 5,253) carry the relayed figure as `official` / `secondary` with `primary_to_find` set; the governorate totals (16,160; 7,991) are not used. |
| Grid rows: `pop_type grid`, `pop_source_status unverified`, `tag_10k false`, corroboration null | PASS | `grid rows: 5 all unverified: True any tag_10k: False corr null: True`; Abā al-Saʿūd (11,474) has `exclusion_reason = "grid-only population, uncorroborated"`, `screened true`. `A-najran-002` records the rule. 2010-growth check: none of the five has a matched 2010 city (cities2010_growth.csv), so no corroboration value exists to record. |
| No corrected figure in `population` | PASS | All 13 `population` values equal the R1a `settlements.parquet` value of record (6 × GASTAT primary, 2 × S-najran-002, 5 × WorldPop). Record-only geo-verify estimates (Thār 4,465; Badr 4,128; Najrān 89,968 …) appear in `notes` only. |
| Relayed vs primary conflict (> 2 %) | PASS | WebFetch of citypopulation.de Najrān places (31 Oct): 381,431 / 89,456 / 23,252 / 12,738 / 8,365 / 7,182 / 4,983 / 2,709 — identical to the primary export and the register (0.0 %). Thār, Abā al-Saʿūd, Al Mikhlaf, Al Nukaysi, Al ʿUraysah confirmed absent from that table, as the register says. |
| Control total | PASS | `runs/gastat/primary/control_total.csv` (main checkout): `najran, ta1_total 592300, matched 522424 (6), grid_unmatched 75223, residual 69876, grid_minus_residual 5347, exceeds True` = the figures in `A-najran-004`, the doc and the status. |
| Rule 1 spot-check (≥ 10 numbers) | PASS | All 13 populations, all 7 governorate totals, all 13 × (dist_existing, dist_committed, dist_metro, road_min_existing) and all 13 lat/lon pairs re-read from the source files and compared: 0 mismatches (section 2 and the scripts' output). Hima distance 82 km recomputed (82.0). Khubāsh/Ḥubūnā candidate-node distances (55.5 / 20.2 km) match `A-najran-osm-001` in `docs/assumptions.md` line 335; the Khubāsh metro distance 54.8 km matches the village-node choice recorded there. Sample = population, not random; no seed needed. |
| Rule 2 (no silent omissions) | PASS | 7/7 governorates; 13/13 ≥ 5k settlements of the universe; Al-Kharkhīr (3,277, 740 km away) and the two 2010-only towns are named with reasons. |
| Rule 5 (planned ≠ existing) | PASS | see criterion 3. |
| Schema words / pilot-only columns | PASS | `terrain_class` ∈ {mixed, dunes}; `osm_type = node` everywhere; `nearest_metro_tier = 3`; `threshold_50k` and `pilot_sample` null on all rows. |
| Source and assumption ids resolve | PASS | S-cp1-100, S-r1a-204/205/210/221/222/506/508, S-054, S-062, S-071, S-073, S-090, S-cp2-gastat-001/007/008, S-najran-001/002/003/004/010 all in `docs/sources/index.csv`; A-screen-001/002/009/013/031–033/035/037–039, A-screen-pilot-001, A-r1a-004, A-geo-003, A-najran-terrain-001, A-najran-osm-001 all in `docs/assumptions.md`. Note: `A-najran-001` cites S-najran-009, which is in `index.csv` and `pilot-najran.csv` but not in `docs/sources/r2-najran.csv`. |
| Absolute home paths / secrets / `git push` | PASS | `grep -rn "/Users/[a-z]"` over tracked files plus the seven new files: empty. Secrets grep: empty. No `git push`. The scripts use `REPO = Path(__file__).resolve().parents[3]`. |
| Nothing under `data/`, `runs/` added to git | PASS | `git status --porcelain` lists only the seven intended paths; `data/ksa/geo` and `data/ksa/grids` are untracked symlinks (gitignored). |
| Geo-verify step described accurately | PASS | `screening/geo_verify/cli.py` line 35: `REGISTERS = "cities/ksa/regions/pilot-*.parquet"`; `runs/geo_verify/estimate/{no-pop,secondary}` exist. Status block and doc item 12 state plainly that the run processed the pilot rows, not this register, and that no value entered `population`. The CLI gap belongs to the GEO_VERIFY owner. |
| Labels ("screening input, not a forecast"), tone, no model names, no content from the author's company | PASS | Label present at top and bottom of `docs/regions/najran.md`; no advocacy wording; no model ids in the docs. |
| Status numbers match measurement | PASS | 13 rows; 7/7; 4 ≥ 10k; 11 ≥ 5k; 13/13 roles; verified 6 / secondary 2 / unverified 5; +5,347: all reproduced. Minor: the doc says "Access date for every source row: 2026-10-31" while the five rows in `r2-najran.csv` carry `accessed 2026-10-30` (pilot rows carried over); re-fetched 31 Oct with the same values. |

## 4. Failures

| id | failure | evidence | fix needed |
|---|---|---|---|
| F1 | **Status line not in the required form.** The brief (prompt task 5 and the "Status line" rule) requires the last line of the status block to be `REGION_NAJRAN: done` or `REGION_NAJRAN: blocked - <reason>`; the orchestrator greps for it. | `docs/status/r2-najran.md` last line: `REGION_NAJRAN: pending verifier`. No other track status file uses this form (`grep -rn "pending verifier" docs/status/` → only this file). | Replace with `REGION_NAJRAN: done` once the other FAILs are closed (or `blocked - <reason>`). |
| F2 | **Handoff not committed.** Task 5 requires a commit `feat(screening): region sweep najran` including `screening/sweeps/najran/`. | `git status --porcelain`: all seven deliverables are `??` (untracked); `git log` HEAD `8b68418` is the CP2_PREP cost-log commit. The hygiene greps over `git ls-files` therefore do not cover these files (I grepped them explicitly). | Commit the seven paths on `r2-najran` with the conventional message. |
| F3 (environment) | **`pytest -q` and `common.manifest verify` are not green in the review environment.** Both fail only on gitignored files absent from this worktree; none concerns Najrān. | pytest: 2 failed, 3 errors, all `FileNotFoundError` (section 1). Manifest: 63 `file missing`, none for the GASTAT, WorldPop or `osm-gcc-2026-10-14` rows. | Coordinator to run `uv run pytest -q` and `uv run python -m common.manifest verify` on the main checkout after merging `r2-najran` and record the result in `docs/STATUS.md` before tagging. Not a builder defect. |

Coordinator follow-ups (outside the region-scout's ownership, not counted as builder FAILs): `docs/STATUS.md` has no REGION_NAJRAN line and `docs/cost-log.md` has no row for this run (only the pilot row, line 24).

## 5. Spot-check sample and results

Sample = every row (13 populations, 7 governorate totals, 13 × 4 distance fields, 13 coordinates) against `census2022_TA1_governorate_primary.xlsx`, `census2022_TA1_city5k_primary.xlsx` and `cities/ksa/zones/settlements.parquet`: 0 mismatches. Secondary sources re-fetched with WebFetch on 31 Oct 2026: S-najran-001/S-073 (citypopulation.de admin: 7 rows, 592,300) ✓; S-najran-002 (citypopulation.de Najrān places: 8 values identical) ✓; S-najran-003 (Saudipedia: "Six governorates", "around sixty-five administrative centers") ✓; S-najran-010 (ajel.sa: page exists, Al-Wadeeah crossing, published 2023-07-06) ✓. No fabricated or misquoted figure found.

## 6. Three most important fixes

1. Commit the seven deliverables on `r2-najran` (`feat(screening): region sweep najran`) — F2.
2. End `docs/status/r2-najran.md` with the plain line `REGION_NAJRAN: done` — F1.
3. Coordinator: re-run pytest and manifest verify on the main checkout after merge, add the REGION_NAJRAN line to `docs/STATUS.md` and a cost-log row — F3 and follow-ups. Opus to rule on the heritage-role attribution (Hima is nearer Thār than Najrān) and the five grid-only `tag_5k` rows, as listed in the register's "Needs Opus judgement".

First-pass verdict (superseded by section 7): FAIL.

## 7. Second pass (31 Oct 2026, after commit `304f168`)

Re-verified read-only in the same worktree after the coordinator's fixes. Commands re-run and the result per item:

| item | verdict | evidence |
|---|---|---|
| F1 status line | **PASS** | `grep -n "^REGION_NAJRAN:" docs/status/r2-najran.md` → `51:REGION_NAJRAN: done` (last line, plain text, no markup). |
| F2 handoff committed | **PASS** | `git log --oneline -1` → `304f168 feat(screening): region sweep najran`; `git show --stat 304f168`: 9 files, 999 insertions (the register pair, the three docs, the status file, the two scripts and the first-pass verify file). `git status --porcelain` empty before this section was appended. No `data/` or `runs/` path in the commit. |
| `.venv/bin/ruff check screening/sweeps/najran` / `ruff format --check` | PASS | `All checks passed!` / `2 files already formatted`, exit 0 / 0. |
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/najran.parquet` | PASS | `ok   najran.parquet: 13 rows, 7 governorates`, exit 0. Parquet metadata `governorates_gastat 7`, `governorates_listed 7`. |
| `.venv/bin/python -m common.docver check docs` | PASS | `docver OK: 103 files`, exit 0. |
| Parquet / CSV / Markdown agreement | PASS | 13/13 rows, same `osm_id` order; `parquet/csv mismatches: 0`; Markdown tables A and B re-parsed against the Parquet: `md rows A/B: 13 13 mismatches: 0`. `build()` re-run in memory: `rebuild diffs: 0`. |
| Field rules re-checked | PASS | populations without source/type/year 0; 5 grid rows all `unverified`, none `tag_10k`, corroboration null; 6 primary rows `official`+`verified`; 13 roles all `S-`; `tag_10k` 4, `tag_5k` 11; 7 governorates. |
| Assumption file (`docs/assumptions-r2-najran.md`) | PASS | 6 rows A-najran-001…006 with version header. A-najran-001 now reads "carried from the pilot's terrain assumption (A-najran-terrain-001; its source S-najran-009 is in the pilot file only and weakly sourced)": the id is named as a pointer into `docs/assumptions.md` line 334, not cited as an R2 source. The same text is in `write_docs.py` line 312, so a regeneration keeps it. |
| Source file (`docs/sources/r2-najran.csv`) | PASS | 5 rows (S-najran-001, 002, 003, 004, 010), unchanged values, every one re-fetched or file-checked in the first pass. |
| Access-date wording in `docs/regions/najran.md` | PASS | Line 5: "Access dates: 2026-10-31 for the GASTAT primary files and the R1a builds; 2026-10-30 for the pilot-derived secondary rows (kept unchanged in `docs/sources/r2-najran.csv`)". Matches the CSV rows (`accessed 2026-10-30`) and is in the generator (`write_docs.py` line 77). |
| Hima attribution flagged | PASS | Doc item 9 now states 82 km from Najrān and 47 km from the Thār row and asks Opus whether Thār should carry the role; also in `write_docs.py` line 240. Remains an open judgement item for Opus, not a register error. |
| Hygiene | PASS | `grep -rn "/Users/[a-z]" $(git ls-files)` empty; no `data/`, `runs/` files tracked by the commit. |
| F3 (environment: pytest / manifest in this worktree) | **open, coordinator** | Not re-run: unchanged cause (gitignored files absent from the worktree, none Najrān-related; see section 1). Not a defect of this milestone's files; the coordinator confirms green on the main checkout after merge, and adds the `docs/STATUS.md` line and the cost-log row. |

Everything the builder owns now meets the brief. The remaining item (F3 and the STATUS/cost-log rows) lies with the coordinator on the main checkout and does not concern the Najrān register, scripts or documents.

VERDICT: PASS
