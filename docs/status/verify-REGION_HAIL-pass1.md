> **Document version:** docs/status/verify-REGION_HAIL.md v1.0 | 31 Oct 2026 | Author: red-team-verifier (read-only) | Status: verified

# Verifier report: REGION_HAIL (track `r2-hail`)

Scope: `prompts/REGION_HAIL.md` v1.4 acceptance criteria plus the launcher's check list. Worktree `.worktrees/r2-hail`, branch `r2-hail`, HEAD `8b68418`; all deliverables are untracked (`git status --short`: 8 `??` entries). Nothing was edited; the only file created is this one. Access date for every live check: 2026-10-31.

## 1. Commands run

| command | result | time |
|---|---|---|
| `.venv/bin/pytest -q tests/test_hail_register.py tests/test_region_sweep.py tests/test_docver.py` | 13 passed, exit 0 | 1.4 s |
| `.venv/bin/ruff check screening/sweeps/hail tests/test_hail_register.py` | All checks passed, exit 0 | |
| `.venv/bin/ruff format --check` (same paths) | 3 files already formatted, exit 0 | |
| `.venv/bin/python -m common.docver check docs` | `docver OK: 102 files`, exit 0 (status file claims 101; see W2) | |
| `.venv/bin/python -m common.manifest verify` | `manifest OK: 305 rows`, exit 0 (via the local gitignored symlinks, see §5) | |
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/hail.parquet` | `ok hail.parquet: 20 rows, 9 governorates`, exit 0 | |
| `build_register --dry-run` twice; `build_rows()` in memory vs on-disk Parquet | identical summaries; 0 cell differences across 20 rows x 43 columns; header `{governorates_gastat: 9, governorates_listed: 9, road_target_mismatch: 5}` | |
| `write_doc --dry-run` vs `docs/regions/hail.md` | identical except one trailing blank line added by `typer.echo` | |

## 2. Acceptance criteria (prompt section "Acceptance")

| # | criterion | verdict | evidence |
|---|---|---|---|
| A1 | Governorate count reconciles to GASTAT or the discrepancy is sourced both ways | PASS | `census2022_TA1_governorate_primary.xlsx` rows 13, 48, 66, 104, 118, 124, 129, 131, 137 (0-based data index): Hail 498,575; Al Hait 74,596; Baqa 56,362; Ash Shinan 29,419; Ash Shamli 20,946; Simira 19,563; As Sulaymi 17,343; Mawqaq 16,835; Al Ghazalah 12,767; sum recomputed = **746,406** = S-hail-001 region total (`docs/sources/index.csv`, and live citypopulation.de page read 2026-10-31: 746,406). Working list `docs/gastat-regions.md:176-188` has the same nine. Parquet header 9/9. The xlsx has 150 governorate rows + a `Total` row (151 data rows); the doc's "150" is correct. |
| A2 | Every settlement >= 10k in the official table appears; sensitivity rows >= 5k are tagged; no population without a source id and type | **FAIL** | Presence of >= 10k rows is met: primary city table Hail 448,623 (row 10), Baqa 19,659 (row 115) are in the register; `Alshazalah` 11,560 (row 143) is left unmatched by `screening/gastat_crosswalk.yaml:70` and the register carries the same figure for Ash Shinan from S-hail-001 with the conflict logged. No other primary city row maps to Hail (all 273 rows scanned by name pattern and by value). Every row with a population has `pop_source`, `pop_year`, `pop_type` (0 nulls). **But the >= 5k tagging rests on the wrong population basis for three rows (finding F1):** the GASTAT-relayed S-hail-001 table, cited by the register, carries Al-Khuṭah (الخطة) 3,355, Al-Qā'id (القاعد) 2,913 and Al-Ḥalīfah as-Suflā (الحليفة السفلى) 4,151 (file `data/ksa/hail/citypop_hail_census2022.csv` rows 14-15, 13; live page confirms), while the register gives Al Khuttah 9,636 (grid), Al Qa`id 5,523 (OSM tag 2010) and Al Hulayfah Assofla 8,990 (grid), all `tag_5k: true`, with notes stating "no GASTAT or OSM figure" / "the only figure for the town". The Arabic names match exactly. The population rule (A-screen-031, prompt line 13, skill line 28: official > derived > grid; "GASTAT-relayed figures win where they exist") is violated and the notes are false. |
| A3 | No committed or hypothetical line is called existing; every economic role has a source | PASS | `cities/ksa/lines/sar-north-passenger.yaml:7` `layer: existing`, `hhr.yaml:7` `layer: existing`, `landbridge.yaml:7` `layer: committed`, `:9` `status: announced`. Register `nearest_existing` is only `sar-north-passenger:hail` / `hhr:madinah`; `nearest_committed` only `landbridge`; doc §9 and notes say "committed, unlocated". All 5 roles carry a source id that resolves in `docs/sources/index.csv` (S-hail-006, S-r1a-204, S-hail-007, S-hail-005) and ties to the town (GACA/Wikipedia: HAS/OEHL serves Hail City; Wikipedia university list: "University of Hail, 2006, Ha'il"; uoh.edu.sa is the official site). |
| A4 | Parquet, CSV and the Markdown table agree; the register validates | PASS | CSV: 20 rows, same 43 columns, every compared column equal (names, population, sources, tags, governorate, road minutes, roles, sources lists). Markdown table regenerated from the Parquet is identical. `validate --strict` exit 0; `test_hail_csv_mirror_matches_parquet` passes. |

## 3. Launcher's detailed checks

| check | verdict | evidence |
|---|---|---|
| Governorate count and sum | PASS | see A1; none of the nine governorate totals equals any register population. |
| Official table coverage; Makkah Turubah not used | PASS | City xlsx row 83 `Turubah 28,279` is not in the register; row 180 `Turba 8,590` is the Hail row (universe `KSA-ST-00937`, OSM node 1237534271 at 28.26 N 42.92 E, Baqa governorate). Eight primary matches (Hail, Baqa, Alshamli 9,163, Turba 8,590, Alhait 8,289, Alajfir 7,518, Jabah 5,622, Alghazalah 5,592) = the 8 `verified` rows. `Bani Hasan 6,344` (row 222) equals Asbatr's grid value by coincidence and is not used. |
| Grid rows `unverified`; no grid `tag_10k` | PASS | 7 grid rows, all `unverified`, `tag_10k` all false; `pop_corroboration` null everywhere (none run). |
| Every population has source/year/type | PASS | 0 nulls in `pop_source`, `pop_year`, `pop_type` for 20 rows. |
| No governorate total used as settlement population | PASS | nine totals vs 20 populations: no match; centre notes say "governorate total ... is not a settlement figure". |
| Population precedence (official > derived > grid) | **FAIL** | F1 (three rows). |
| Economic roles vs `economic_nodes.parquet` | PASS | 5 nodes with `region == hail`: `airport-has-hail` (S-cp1-100), `modon-hail` (S-r1a-204), `heritage-hail-rock-art` (S-r1a-205, region-level position), `univ-hail` (S-r1a-221), `maaden-az-zabirah-bauxite` (S-r1a-236, region unverified, 27.93 N 43.71 E, ~85 km from the nearest register town). All five are named in `docs/regions/hail.md` §5; four are attached to Ha'il/Jubbah rows; the mine is deliberately unassigned and said so. Observation (not a FAIL): the rock-art site's second component, Shuwaymis (Al-Ḥā'īṭ governorate), carries no heritage role on any row; worth an Opus-judgement line. |
| Layer labels | PASS | see A3. |
| Number spot-check (>= 10) | PASS (with F1 exception) | Verified against the xlsx/universe/sources: 498,575; 74,596; 56,362; 20,946; 19,563; 17,343; 16,835; 12,767; 29,419; 746,406; Turubah governorate 41,769 (xlsx row 89); 448,623; 19,659; 9,163; 8,590; 8,289; 7,518; 5,622; 5,592; 11,560 (Alshazalah); 28,279; 168 nodes; 634 grid rows in the universe; 650 universe rows; 20 haversine distances recomputed from the station coordinates in the line YAMLs, all equal to the register to 0.01 km (e.g. Ha'il 18.90 km to `sar-north-passenger:hail` at 27.683 N 41.755 E). The three "no GASTAT figure" notes are the only numbers found to be wrong (F1). |
| Count checks (650 / 630 / 422 / 208 / 20 / 4 / 18 / 7 / 8 / 5 / 7) | PASS as recomputed | Universe `region == 'hail'`: 650; not in register: 630 = hamlet 422 + village 208; largest not written 4,411 (As Sufun, grid); no not-written row has `osm_population >= 5,000`. Register: 20 rows, 9 centres, `tag_10k` 4, `tag_5k` 18, grid 7, verified 8, secondary 5, unverified 7. These reproduce the claims; F1 means the right `tag_5k` count is 15 (secondary 7, grid 5) once precedence is applied. |
| Geo-verify not re-run | PASS (disclosed) | Status §"Could not do" and doc §6 say so; pilot estimates carried in notes only; WorldPop raster absent from the worktree (`data/ksa/grids` is a symlink to the main checkout, not read). |
| Manifest symlinks gitignored, untracked | PASS | `git check-ignore -v data/ksa/hail` -> `.gitignore:5: data/ksa/*`; `git ls-files data/` lists only `data/README.md` and `data/ksa/tables/**`; the 11 directory symlinks and `data/ksa/hail/citypop_hail_census2022.csv` are untracked. |
| No licence rows needed | PASS | No download; inputs already in `docs/licences.csv` (OSM line 3/156, GASTAT line 7/116/208, WorldPop 12/158, OSRM 165, citypopulation Hail 136). `data/ksa/hail/raw/{gov,city5k}_primary.csv` are CSV dumps of the tracked xlsx, not read by the builder and not downloads. |
| Home paths / the private-list terms / secrets / `git push` in the new files | PASS | all greps empty (`grep -n "/Users/"` on the 8 new files: exit 1). |
| Model names in new docs | WARN | "Opus judgement" appears (`docs/regions/hail.md:77`, `docs/assumptions-r2-hail.md:10`, status lines 21/23/35, CSV notes). It is the heading the prompt itself mandates (`prompts/REGION_HAIL.md:26` "Needs Opus judgement" list), so this is a template-vs-CLAUDE.md conflict for the coordinator, not a builder fault. No `claude-`, `haiku`, `fable`, `sonnet`. |
| Label | PASS | `docs/regions/hail.md:5` "Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast." No "will reduce". |
| Determinism | PASS | see §1 (no seed needed: deterministic build from fixed inputs; two runs identical). |

## 4. Failures (exact evidence)

**F1 (FAIL, A2 / population rule).** Three register rows ignore a GASTAT-relayed figure that the track's own source carries, and their notes deny the figure exists.

| row | register (`cities/ksa/regions/hail.parquet`) | S-hail-001 (`data/ksa/hail/citypop_hail_census2022.csv`; live page 2026-10-31) | consequence |
|---|---|---|---|
| الخطة Al Khuttah (`KSA-ST-00973`, row 5) | 9,636 `grid`/`unverified`, `tag_5k: true`; note "no GASTAT or OSM figure" | Al-Khuṭah, Ḥā'il gov., **3,355** | must be `official`/`secondary` 3,355; `tag_5k: false` |
| الحليفة السفلى Al Hulayfah Assofla (`KSA-ST-00297`, row 7) | 8,990 `grid`/`unverified`, `tag_5k: true`; note "no GASTAT or OSM figure" | Al-Ḥalīfah as-Suflā, Al-Ḥā'īṭ gov., **4,151** | must be `official`/`secondary` 4,151; `tag_5k: false` |
| القاعد Al Qa`id (`KSA-ST-00952`, row 17) | 5,523 `derived`/`secondary` (OSM tag 2010), `tag_5k: true`; note "the only figure for the town" | Al-Qā'id, Ḥā'il gov., **2,913** (and a separate place Munīfat al-Qā'id 4,688) | official beats derived (skill line 28): 2,913, `tag_5k: false` |

Rules broken: `prompts/REGION_HAIL.md:13` ("GASTAT-relayed figures win where they exist; WorldPop fills gaps only"), `:14` ("keep citypopulation.de only for localities neither table covers": these three are in neither primary table, so S-hail-001 applies), skill `region-sweep` line 28 (precedence official > derived > grid), rule 1 (the notes state a non-fact). Knock-on errors: doc §2 (`tag_5k` 18; secondary 5; grid 7), §4 ("none of the 630 has a grid or OSM figure at or above 5,000" stays true, but the three rows' basis is wrong), §7 item 3 ("the only >= 5k rows without a GASTAT figure"), status "Measured" lines 12-13 and the A-hail-002 row ("the only figure for the town"). The builder worked from the R1a universe's `population_basis` without re-checking the S-hail-001 place list it cites; the pilot had matched only its own 11 rows to S-hail-001.

## 5. Warnings and open items (not acceptance FAILs)

- **W1 Deliverables uncommitted.** Prompt task 5 requires the commit `feat(screening): region sweep hail`; all eight files are `??`. Required before the track can be merged.
- **W2 Status number mismatch.** `docs/status/r2-hail.md:16` says `docver` OK on 101 files; measured 102 (the status file itself, written 16:31:55, post-dates the check). Update after the F1 fix.
- **W3 `dist_method` text is inaccurate for 5 rows.** It reads "great-circle to the station the road skim targets", but for Al-Malwi, Al Hulayfah Assofla, Al Hayit, Ayal Obaid and Dhurayghit `dist_committed_km` is to `landbridge:muwai`/`dawadmi` while `road_min_committed` is to `landbridge:al-jumum` (header `road_target_mismatch: 5`; the notes say so, the method string does not).
- **W4 Status label line absent by design** ("`REGION_HAIL: done` is written only after a PASS"); the cost log has no REGION_HAIL row yet (coordinator step after the run). Both remain open.
- **W5 S-hail-005 not re-verifiable live:** worldheritagesite.org and whc.unesco.org both returned HTTP 403 today; the Jubbah (Jabal Umm Sinman) component is consistent with the inscription record but was not re-read. GACA's page redirected to its Arabic home; the airport tie was confirmed via Wikipedia (HAS/OEHL, "located in Hail City, serving Hail Province"). MODON page: TLS certificate error, not re-read.
- **W6 Transcription gap in the pilot's S-hail-001 file** (not this track's file): the live page lists Al-Ḥafīr (Mawqaq) 3,243, absent from the 17-place transcription. Below 5k, no effect here; report to the pilot/coverage audit.
- **W7 Al-Malwi** (OSM tag 15,000 dated 1950, 25.34 N 40.38 E) is correctly flagged; it is the only `tag_10k` row resting on an OSM tag, and the position is at or beyond the plausible southern edge of Al-Ḥā'īṭ. Left to Opus as the track says.

## 6. Spot-check sample (seed 20261031, `random.sample`)

Register rows 9 (Al Ajfar 7,518) and 7 (Turubah 8,590): both equal the primary city xlsx (`Alajfir` row 194; `Turba` row 180) and the live citypopulation.de page (Al-Ajfir 7,518; Turubah 8,590, Baq'ā'). PASS.
Sources S-r1a-221 (Wikipedia university list: "University of Hail | 2006 | Ha'il | www.uoh.edu.sa", PASS) and S-hail-005 (not reachable, HTTP 403; see W5).
Additional live reads: citypopulation.de Hail page (all 9 governorate totals, region total 746,406, and the 18 place rows: PASS, and the source of F1); uoh.edu.sa (official site, "جامعة حائل": PASS); Wikipedia Ha'il Regional Airport (HAS/OEHL serving Hail City: PASS).

## 7. Three most important fixes

1. **Apply the population precedence for Al Khuttah, Al Hulayfah Assofla and Al Qa`id** from S-hail-001 (3,355 / 4,151 / 2,913; `pop_type: official`, `pop_source_status: secondary`, `primary_to_find` the GASTAT locality table), set `tag_5k: false`, decide whether the rows stay (below 5k, not centres: either drop them under A-hail-001 or keep them with `screened: false` and a reason), correct the notes, and add a builder step that matches every candidate's Arabic name against the S-hail-001 place list before accepting a grid or OSM figure. Then regenerate the doc and the counts (expected `tag_5k` 15, secondary 7, grid 5) and the status block.
2. **Commit the deliverables** (`feat(screening): region sweep hail`, including `screening/sweeps/hail/` and the test), refresh the status numbers (docver count) and only then write the plain `REGION_HAIL: done` line; the coordinator adds the cost-log row.
3. **Make `dist_method` true for the five mismatched rows** (either compute the great-circle distance to the road target as well or change the method string), and have the coordinator settle the "Needs Opus judgement" heading against CLAUDE.md's no-model-names rule in the region template.

VERDICT: FAIL
