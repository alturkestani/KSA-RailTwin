> **Document version:** docs/status/verify-REGION_HAIL.md v2.0 | 31 Oct 2026 | Author: red-team-verifier (read-only; pass 2) | Status: verified

# Verifier report, pass 2: REGION_HAIL (track `r2-hail`)

Scope: `prompts/REGION_HAIL.md` v1.4 acceptance criteria, the launcher's pass-2 check list and the relayed-file incident. Worktree `.worktrees/r2-hail`, branch `r2-hail`, HEAD `8b68418`; all deliverables still untracked (`git status --porcelain`: 10 `??` entries, no modified tracked file). Nothing was edited; the only file written is this one (the pass-1 report is kept at `verify-REGION_HAIL-pass1.md`). Access date for every live check: 2026-10-31 (Asia/Riyadh).

## 1. Commands run

| command | result | time |
|---|---|---|
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/hail.parquet` | `ok hail.parquet: 17 rows, 9 governorates`, exit 0 | 0.8 s |
| `.venv/bin/pytest -q -p no:warnings tests/test_hail_register.py tests/test_region_sweep.py tests/test_docver.py` | 14 passed, exit 0 (7 of them in `test_hail_register.py`) | 0.9 s |
| `.venv/bin/pytest -q -p no:warnings` (full suite) | 76 passed, exit 0 | 16.4 s |
| `.venv/bin/ruff check screening/sweeps/hail tests/test_hail_register.py` | All checks passed, exit 0 | |
| `.venv/bin/ruff format --check` (same paths) | 3 files already formatted, exit 0 | |
| `.venv/bin/python -m common.docver check docs` | `docver OK: 104 files`, exit 0 (status file says 103; W2) | |
| `.venv/bin/python -m common.manifest verify` | `manifest OK: 305 rows`, exit 0 | 1.3 s |
| `build_register --dry-run` twice | identical: `rows 17; centres 9; tag_10k 4; tag_5k 15; header {governorates_gastat: 9, governorates_listed: 9, road_target_mismatch: 4}` | |
| `write_doc --dry-run` vs `docs/regions/hail.md` | identical except the trailing newline added by `typer.echo` | |
| Parquet vs CSV, all 42 columns x 17 rows | 0 cell differences | |

## 2. Incident: relayed file `data/ksa/hail/citypop_hail_census2022.csv` (S-hail-001, manifest `citypop-hail-census2022`)

| check | result |
|---|---|
| Path in this worktree | symlink `data/ksa/hail/citypop_hail_census2022.csv -> ~/Documents/Projects/KSA-RailTwin/data/ksa/hail/citypop_hail_census2022.csv` (main checkout; gitignored by `.gitignore:5 data/ksa/*`; the symlink itself is untracked) |
| SHA-256 of the current file | `6db1854b42a79c146947e934952b9e67e187806ee661cdb15271d3c41644ba51` = `cities/ksa/sources.yaml:140` |
| Bytes | 3,405 = `sources.yaml:141` |
| Pilot-hail copy (`.worktrees/pilot-hail/data/ksa/hail/citypop_hail_census2022.csv`, a regular file) | same SHA-256, 3,405 bytes: byte-identical |
| Al-Qā'id row present | line 16: `place,Al-Qa'id,القاعـد,Ha'il,حائل,2913,2022-05-10,...` (tatweel in the Arabic name, as the builder's `_ar_key` expects) |
| Content vs the live page | all 9 governorate rows, the region total 746,406 and all 17 place rows match the citypopulation.de Ḥā'il page read today; the page has one extra place, Al-Ḥafīr (Mawqaq) 3,243, missing from the transcription (pass-1 W6, pilot file, below 5k, no effect) |
| `manifest verify` | OK, 305 rows |
| Tracked files touched by the incident | none: `git diff --stat` empty in this worktree; `cities/ksa/sources.yaml` and `data/` clean in the main checkout (`git -C <main> status --porcelain`) |
| Does the register depend on an unregistered change? | No. My own parse of the registered file (independent of the builder's code) reproduces the builder's result exactly: 7 universe rows matched by Arabic name (tatweel removed), the same resolved populations, 633 not written (hamlet 422, village 209, town 2), largest excluded 4,688, and `register population == resolved universe population` for all 17 rows. |

Verdict on the incident: **PASS** (restored byte-for-byte; manifest and content verified). Observation for the coordinator: a gitignored symlink into the main checkout gives a track write access to a manifest-registered raw file with no git protection; the main-checkout file's mtime is 16:42:37 today (the restore). Consider `chmod a-w` on manifest-registered raw files or copying instead of linking.

## 3. Acceptance criteria (prompt section "Acceptance")

| # | criterion | verdict | evidence |
|---|---|---|---|
| A1 | Governorate count reconciles to GASTAT or the discrepancy is sourced both ways | PASS | `census2022_TA1_governorate_primary.xlsx` (0-based data rows 13, 48, 66, 104, 118, 124, 129, 131, 137): Hail 498,575; Al Hait 74,596; Baqa 56,362; Ash Shinan 29,419; Ash Shamli 20,946; Simira 19,563; As Sulaymi 17,343; Mawqaq 16,835; Al Ghazalah 12,767; recomputed sum **746,406** = S-hail-001 region total (file line 28; live page today 746,406). `docs/gastat-regions.md:176` "Ḥā'il: 9 rows". Parquet header 9/9; 9 distinct governorates in the rows; every centre present (`is_governorate_centre` 9). The xlsx has 151 data rows (150 governorates + Total): the doc's "150" is right. |
| A2 | Every settlement ≥ 10k in the official table appears; sensitivity rows ≥ 5k are tagged; no population without a source id and type | PASS | Primary city table rows for Hail: Hail 448,623 (row 10), Baqa 19,659 (row 115) in the register; `Alshazalah` 11,560 (row 143) unmatched by the crosswalk and carried as Ash-Shanān 11,560 from S-hail-001 with the conflict logged (row note, doc §6, §7.2); a name-pattern scan of all 273 city rows finds no other Hail town. **Pass-1 F1 is closed:** Al Khuttah, Al Hulayfah Assofla and Al Qa\`id are absent (`name_en` and `name_ar` both checked); the builder's `_apply_relayed_precedence` (`build_register.py:224-241`) replaces the grid/OSM figures 9,636 / 8,990 / 5,523 by the relayed 3,355 / 4,151 / 2,913 before selection; my independent re-application finds **no remaining grid or OSM row at or above 5,000 whose Arabic name matches S-hail-001**, with exact keys and also with hamza/yā'/tā' marbūṭah normalisation (the five grid rows As Sulaymi, Ayal Obaid, Asbatr, Dhurayghit, Al Wudayy and the OSM row Al-Malwi have no relayed counterpart). `tag_5k` equals `population >= 5000` on all 17 rows (15 true); `tag_10k` equals `population >= 10000 and pop_type != grid` (4 true). 0 nulls in `population`, `pop_source`, `pop_year`, `pop_type`; every `pop_source` id resolves in `docs/sources/index.csv`. |
| A3 | No committed or hypothetical line is called existing; every economic role has a source | PASS | `cities/ksa/lines/sar-north-passenger.yaml` `layer: existing`, `hhr.yaml` `layer: existing`, `landbridge.yaml` `layer: committed`, `status: announced`; register `nearest_existing` only `sar-north-passenger:hail` / `hhr:madinah`, `nearest_committed` only `landbridge`; doc §9 and notes say "committed, unlocated". 5 roles, each with a source id (S-hail-006 x2, S-r1a-204, S-hail-007, S-hail-005), all resolving; they match the 5 `region == hail` rows of `economic_nodes.parquet` (airport-has-hail, modon-hail, heritage-hail-rock-art, univ-hail; the Az Zabirah mine deliberately unassigned and said so in doc §5). |
| A4 | Parquet, CSV and the Markdown table agree; the register validates | PASS | 0 cell differences Parquet vs CSV (42 columns); `write_doc --dry-run` output identical to `docs/regions/hail.md`; `validate --strict` exit 0; builder deterministic (two dry runs identical). |

## 4. Launcher's pass-2 checks

| check | verdict | evidence |
|---|---|---|
| Three wrong rows gone; no other ≥ 5k grid/OSM row unresolved against S-hail-001 | PASS | see A2. The 7 replaced universe rows (my recomputation = builder's list): Al Hulayfah Assofla 8,990 -> 4,151; Al Ruwda 1,076 -> 2,906; Al Qa\`id 5,523 -> 2,913; Munifat al Qa\`id 467 -> 4,688; An Nisiyah 1,272 -> 4,597; Al Khuttah 9,636 -> 3,355; Arrwodhah 28 -> 2,906 (but see W8). |
| Counts in `docs/regions/hail.md` and `docs/status/r2-hail.md` recomputed from the Parquet and the R1a universe | PASS | rows 17; centres 9; `tag_10k` 4; `tag_5k` 15; grid 5 (none ≥ 10k, `pop_corroboration` null everywhere); verified 8; secondary 4 (S-hail-001 x3 + OSM tag x1); unverified 5; roles 5; universe `region == 'hail'` 650 (634 grid, 8 primary, 3 S-hail-001, 5 OSM tags); not written 633 = hamlet 422 + village 209 + town 2 (Al Qa\`id, Al Khuttah); largest excluded resolved 4,688; `road_target_mismatch` 4. All match the doc and the status block. |
| Figures spot-checked (≥ 10) | PASS | Against the GASTAT xlsx: 498,575; 74,596; 56,362; 29,419; 20,946; 19,563; 17,343; 16,835; 12,767; Turubah governorate 41,769 (row 89); city rows 448,623; 19,659; 9,163 (Alshamli); 8,590 (Turba); 8,289 (Alhait); 7,518 (Alajfir); 5,622 (Jabah); 5,592 (Alghazalah); 11,560 (Alshazalah); 28,279 (Makkah Turubah, not used); 6,344 (Bani Hasan, coincides with Asbatr's grid value, not used); "Other (< 5000)" 3,683,816. Against S-hail-001 (file and live page): 3,355; 4,151; 2,913; 4,688; 4,597; 2,906; 3,148; 3,105; 11,560; 746,406. Haversine recomputed from the station coordinates in the line YAMLs for all 17 rows x 2 targets: 0 mismatches above 0.05 km. |
| Governorate reconciliation | PASS | A1. |
| `validate --strict` | PASS | exit 0. |
| Hygiene: home paths, the private-list terms, secrets, `git push`, "will reduce" in the new files | PASS | all greps empty (exit 1) on the 10 new paths. `git ls-files data/` lists only `data/README.md` and `data/ksa/tables/**`; `data/ksa/hail` and `raw/` are ignored (`.gitignore:5`). |
| Model names in the new files | WARN (unchanged from pass 1) | "Opus judgement" in `docs/regions/hail.md:75`, `write_doc.py:159`, status lines 23/25/41, `build_register.py:381,389`, CSV notes rows 4-5. The heading is mandated by `prompts/REGION_HAIL.md:26`; template-vs-CLAUDE.md conflict for the coordinator. No `claude-`, `haiku`, `fable`, `sonnet`. |
| Label | PASS | `docs/regions/hail.md:5`. |
| Status block numbers vs measured | PASS except W2 | 17 / 9 / 4 / 15 / 8 / 4 / 5 / 5 / 650 / 633 / 422 / 209 / 2 / 4,688 / 305 all reproduce; docver 103 claimed vs 104 measured. |

## 5. Failures (exact evidence)

**F2 (FAIL): the assumptions register misstates where A-hail-002 is applied.** `docs/assumptions-r2-hail.md:10` reads "used for two rows: Al Malwi (الملوي) 15,000 ... and Al Qa'id 5,523 (year 2010)" with `used in: cities/ksa/regions/hail.parquet (population, tag_10k)`. The register has no Al Qa\`id row and uses an OSM tag for exactly one row (`pop_source == S-hail-003`: 1; `pop_type == derived`: 1). The 5,523 figure is now superseded by the relayed 2,913 under the very precedence the fix introduced, and the pass-1 fix list named this row ("the A-hail-002 row ('the only figure for the town')"). A register row that claims an assumption drives a `population` cell that does not exist is a register-accuracy failure (rule 11: "the assumptions register is complete"; procedure step 12: every number matches what is measured). The document header is still v1.0 and the row was not touched by the fix. Knock-on: `build_register.py:391-396` keeps the dead note branches for `KSA-ST-00952` ("OSM population tag 5,523 (2010); the only figure for the town") and `KSA-ST-00297`; they are unreachable today but would re-emit the false note if either row ever re-entered the selection, and the module docstring (`build_register.py:11-13`) still says selection is "on the population basis the R1a universe carries", which is no longer true.

No other FAIL. Pass-1 F1 is closed.

## 6. Warnings and open items (not acceptance FAILs)

- **W1 Deliverables uncommitted** (prompt task 5: `feat(screening): region sweep hail`). All ten paths are `??`.
- **W2 docver count:** status line 16 says 103 files; measured 104 (this verdict file and the pass-1 copy both exist). Refresh at commit.
- **W3 `dist_method` text still inaccurate for 4 rows** (Al-Malwi, Al Hayit, Ayal Obaid, Dhurayghit): the string says "great-circle to the station the road skim targets" while `dist_committed_km` is to `landbridge:muwai`/`dawadmi` and `road_min_committed` to `landbridge:al-jumum` (header `road_target_mismatch: 4`). The notes say so; the method string does not. Pass-1 fix 3, not done.
- **W4 Status label line and cost log:** no `REGION_HAIL: done` line (by design until PASS); `docs/cost-log.md` has only the pilot row (line 18), no REGION_HAIL row; `docs/STATUS.md` has no REGION_HAIL entry. Coordinator steps after a PASS.
- **W5 Sources not re-verifiable live today:** S-hail-005 (worldheritagesite.org 403; whc.unesco.org 403) and S-r1a-204 (modon.gov.sa TLS certificate error). Fallback reads: Wikipedia "Rock Art in the Hail Region" (inscribed 2015; Jubbah component at Jabal Umm Sinman "90 km northwest of Ha'il"; second component Al-Shuwaymis, Jabal al-Manjor and Raat, "250 km southwest of Ha'il on the border between the provinces of Ha'il and Medina") supports the Jubbah heritage role; the MODON node (`modon-hail`, 27.47 N 41.80 E, S-r1a-204) exists in `economic_nodes.parquet`, which is the register-row trace the procedure allows.
- **W6 Transcription gap (pilot file):** Al-Ḥafīr (Mawqaq) 3,243 on the live page is absent from S-hail-001. Below 5k; for the pilot/coverage audit.
- **W7 Al-Malwi** (OSM tag 15,000 dated 1950 at 25.34 N 40.38 E) remains the only `tag_10k` row on an OSM tag; flagged (A-hail-002, doc §7.1). Opus judgement still open.
- **W8 Name-only match produces one false override.** Two universe rows carry the Arabic name الروضة: `KSA-ST-00355` Al Ruwda (village, Ḥā'il governorate, 26.80 N 41.67 E, grid 1,076) and `KSA-ST-06541` Arrwodhah (hamlet, Al-Ḥā'īṭ governorate, 25.62 N 40.39 E, grid 28). The relayed Ar-Rarwḍah 2,906 is in **Ḥā'il governorate** (file line 18; live page). `_apply_relayed_precedence` assigns 2,906 to both, so the hamlet 130 km away in another governorate is "replaced" by a figure that is not its own, and doc §4 lists Arrwodhah among the seven replaced rows. No effect on this register (both rows stay below 5k and are not written), but the method is unsafe for reuse: in another region a name-only match could overwrite a ≥ 5k town with a smaller homonym's figure, or the reverse. The match key should be (Arabic name, governorate), with a hard error on ambiguity.
- **W9 Dependency records not updated:** `cities/ksa/sources.yaml:143-144` `used_in: W2 pilot (pilot-hail)` and `docs/sources/index.csv` S-hail-001 `used_in: cities/ksa/regions/pilot-hail.parquet; docs/regions/pilot-hail.md`; both now also feed `cities/ksa/regions/hail.parquet` (3 populations and 7 overrides).
- **W10 Document versions:** `docs/regions/hail.md` changed substantively (20 -> 17 rows) but `write_doc.py:25` hard-codes v1.0; `docs/assumptions-r2-hail.md` is v1.0 and stale (F2). CLAUDE.md: bump the minor on every substantive edit. Since neither file has been committed yet, this is a warning; set the versions at commit.
- **W11 Shuwaymis** (second rock-art component, Al-Ḥā'īṭ) carries no heritage role on any row; listed by the builder for Opus judgement (status line 41). Fine as disclosed.

## 7. Spot-check sample (seed 20261031, `random.sample`)

Register rows 9 (Ayal Obaid 6,561, grid) and 7 (Al Ajfar 7,518, primary): Ayal Obaid equals the R1a universe value 6,561 (grid, no external source by design, `unverified`); Al Ajfar equals xlsx `Alajfir` row 194 and the live citypopulation.de page (Al-Ajfir, Baq'ā', 7,518). PASS.
Sources S-r1a-204 (MODON: TLS error today; node present in `economic_nodes.parquet`) and S-hail-005 (403 today; Wikipedia fallback consistent). Not re-read at the cited URL (W5); no contradiction found.
Additional live read: citypopulation.de Ḥā'il page, all 9 governorate totals, the region total and all 18 place rows: every figure used by the register and by the override step matches (and confirms Ar-Rarwḍah's governorate for W8).

## 8. Three most important fixes

1. **Correct A-hail-002** (`docs/assumptions-r2-hail.md:10`): one row (Al-Malwi 15,000); say that Al Qa\`id's OSM tag 5,523 was superseded by the relayed 2,913 and is not used; bump the document version. Remove the dead note branches for `KSA-ST-00952` and `KSA-ST-00297` in `build_register.py:391-396` and fix the module docstring (lines 11-13) to describe the resolved basis.
2. **Match the relayed table on (Arabic name, governorate)** in `_apply_relayed_precedence`, raise on an ambiguous match, add a test with the الروضة pair, and regenerate doc §4 (Arrwodhah should drop out of the replaced list: expected 6 overrides, counts unchanged).
3. **Close the handoff:** commit (`feat(screening): region sweep hail`), make `dist_method` true for the 4 mismatched rows, update the two `used_in` records (W9), refresh the docver count, set the document versions, then the plain `REGION_HAIL: done` line; the coordinator adds the cost-log row and settles the "Needs Opus judgement" heading against CLAUDE.md.

VERDICT: FAIL
