> **Document version:** docs/status/verify-REGION_HAIL.md v3.0 | 31 Oct 2026 | Author: red-team-verifier (read-only; pass 3) | Status: verified

# Verifier report, pass 3: REGION_HAIL (track `r2-hail`)

Scope: closure of the pass-2 findings (F1, F2, W8), the acceptance criteria of `prompts/REGION_HAIL.md` v1.4, an independent re-derivation of the resolved population from the raw inputs, determinism, the command battery, hygiene and the status file. Worktree `.worktrees/r2-hail`, branch `r2-hail`, HEAD `8b68418`; all deliverables still untracked (`git status --porcelain`: 11 `??` entries incl. this file and the two earlier reports; `git diff --stat` empty, no tracked file modified). Nothing was edited except this file. Access date for every live check: 2026-10-31 (Asia/Riyadh). Pass-2 report kept at `verify-REGION_HAIL-pass2.md`.

## 1. Pass-2 findings: closed or not (read from the code and docs as they are now)

| finding | verdict | evidence |
|---|---|---|
| F1 (pass 1): three towns tagged ≥ 5k on grid/OSM figures that the relayed table contradicts | **closed, PASS** | Register has no `Al Khuttah`, `Al Hulayfah Assofla`, `Al Qa\`id` row (`name_en` checked on all 17 rows). My own re-application of the relayed table (independent parse of `data/ksa/hail/citypop_hail_census2022.csv`, SHA-256 `6db1854b…ba51` = `cities/ksa/sources.yaml:140`, 3,405 bytes) resolves them to 3,355 / 4,151 / 2,913 and finds **0** excluded rows at or above 5,000 on the resolved figure. |
| F2 (pass 2): stale A-hail-002 row; dead note branches; stale module docstring | **closed, PASS** | `docs/assumptions-r2-hail.md:10` now reads "used for one row: Al-Malwi (الملوي) 15,000 … The other OSM-tag town in the earlier draft (Al Qa'id, 5,523, 2010) is now replaced by its relayed GASTAT figure (2,913)"; register: `pop_source == S-hail-003` on exactly 1 row (Al-Malwi, `tag_10k` true), consistent with the row's `used in`. `build_register.py:390-393`: the OSM branch is now generic (tag value, node id, tag year from the record); no `KSA-ST-00952` / `KSA-ST-00297` literals remain anywhere in the file. Module docstring `build_register.py:11-12`: "a GASTAT-relayed figure (S-hail-001, matched by Arabic name and governorate) replaces a grid or OSM figure; the GASTAT primary figure and the R1a universe basis are used otherwise", which is what the code does. |
| W8 (pass 2): name-only relayed match collides across governorates | **closed, PASS** | `build_register.py:214-217` `_gov_key` strips the `محافظة ` prefix; `:220-235` `_relayed_places` keys by `(name, governorate)` and raises `SystemExit("duplicate relayed place …")` on a repeated key; `:238-261` `_apply_relayed_precedence` keys every universe row the same way and raises when two universe rows share a key that the relayed table matches (`:252-253`). Exercised by me (not only read): on the real universe the guard is silent and yields 6 overrides; forcing `KSA-ST-06541` (Arrwodhah) into `محافظة حائل` raises `two universe rows share ('الروضة', 'حائل'), which the relayed table matches`; appending a second `Jubbah` row to a copy of the relayed file raises `duplicate relayed place ('جبة', 'حائل')`; `_gov_key("محافظة الحائط") == "الحائط"`; `_ar_key("القاعـد") == "القاعد"`. Arrwodhah (`KSA-ST-06541`, Al-Ḥā'īṭ) now keeps its own grid figure 28; Al Ruwda (`KSA-ST-00355`, Ḥā'il) takes 2,906, whose governorate on the live page is Ḥā'il. |

Residual (not a FAIL): the function docstring `build_register.py:241` still says "matched by Arabic name to every grid or OSM row" (incomplete: governorate omitted); no test covers the governorate-keyed match or either guard (pass-2 fix 2 asked for a test with the الروضة pair; the test file has 7 tests, none of them this).

## 2. Acceptance criteria (prompt "Acceptance")

| # | criterion | verdict | evidence |
|---|---|---|---|
| A1 | Governorate count reconciles to GASTAT or the discrepancy is sourced both ways | PASS | My read of `census2022_TA1_governorate_primary.xlsx` (151 data rows incl. Total): Hail 498,575; Al Hait 74,596; Baqa 56,362; Ash Shinan 29,419; Ash Shamli 20,946; Simira 19,563; As Sulaymi 17,343; Mawqaq 16,835; Al Ghazalah 12,767; sum **746,406** = relayed region total (file line 28) = live citypopulation.de total today. `docs/gastat-regions.md:176` "Ḥā'il: 9 rows". Parquet header `governorates_gastat 9`, `governorates_listed 9`; 9 distinct governorates; 9 centres. |
| A2 | Every settlement ≥ 10k in the official table appears; ≥ 5k rows tagged; no population without source id and type | PASS | The city xlsx has no region column (columns: City, Total, Saudi, Non-Saudi; 273 city rows, 155 ≥ 10k), so the Ḥā'il ≥ 10k set is fixed from the GASTAT-credited relayed list of all Ḥā'il places ≥ 2,500, re-read live today: exactly Ḥā'il 448,623, Baq'ā' 19,659, Ash-Shanān 11,560. All three are rows (the first two on the primary table, `verified`; the third on S-hail-001 with the `Alshazalah` 11,560 conflict logged in the row note, `screening/gastat_crosswalk.yaml:70`, doc §6 and §7.2). `tag_5k == population >= 5000` on all 17 rows (15 true); `tag_10k == population >= 10000 and pop_type != grid` (4 true). 0 nulls in `population`, `pop_source`, `pop_year`, `pop_type`; every id in `pop_source`, `sources` and `economic_roles[].source` resolves in `docs/sources/index.csv` + `r2-hail.csv` (unresolved set empty). |
| A3 | No committed or hypothetical line is called existing; every economic role has a source | PASS | `lines/sar-north-passenger.yaml:7` `layer: existing`, `hhr.yaml:7` `layer: existing`, `landbridge.yaml:7` `layer: committed`, `:9` `status: announced`; register `nearest_existing` ∈ {`sar-north-passenger:hail`, `hhr:madinah`}, `nearest_committed` = `landbridge` only; notes say "(committed, unlocated)"; doc §9. 5 roles (Ḥā'il: administrative S-hail-006, airport S-hail-006, industrial_city S-r1a-204, university S-hail-007; Jubbah: heritage S-hail-005), all resolving; `economic_nodes.parquet` has 168 nodes, 5 with `region == hail` (airport-has-hail, modon-hail, heritage-hail-rock-art, maaden-az-zabirah-bauxite deliberately unassigned per doc §5, univ-hail). |
| A4 | Parquet, CSV and the Markdown table agree; the register validates | PASS | Parquet vs CSV: 17 × 42 cells, 0 differences (my own comparison). `write_doc --dry-run` output = `docs/regions/hail.md` except the trailing newline `typer.echo` appends (`diff` shows only line 90 blank). `validate --strict`: `ok hail.parquet: 17 rows, 9 governorates`, exit 0. |

## 3. Independent re-derivation from the raw inputs

Inputs: `cities/ksa/zones/settlements.parquet` (`region == hail`: 650 rows; `pop_source`: WorldPop 634, primary city xlsx 8, S-hail-001 3, OSM tag 5), the relayed CSV (17 place rows, 9 governorate rows, 1 total; parsed by me with my own tatweel/prefix normalisation), the two GASTAT xlsx. Result, with the builder's `CENTRES` set as the only thing taken from the code:

| quantity | mine | register / doc | verdict |
|---|---|---|---|
| rows selected (centres ∪ resolved ≥ 5,000) | 17; same 17 `osm_id`s as the Parquet; `population` equals my resolved figure on all 17 | 17 | PASS |
| universe rows replaced by a relayed figure | **6**: Al Hulayfah Assofla 8,990→4,151 (Al-Ḥā'īṭ); Al Ruwda 1,076→2,906; Al Qa\`id 5,523→2,913; Munifat al Qa\`id 467→4,688; An Nisiyah 1,272→4,597; Al Khuttah 9,636→3,355 (all Ḥā'il) | doc §4: "6 R1a universe rows … (Al Hulayfah Assofla, Al Ruwda, Al Qa\`id, Munifat al Qa\`id, An Nisiyah, Al Khuttah)" | PASS. **Note for the coordinator:** the launcher's brief says "the 7 replaced universe rows listed in docs/regions/hail.md section 4"; the doc now lists 6, and 6 is correct. The seventh of pass 2 (Arrwodhah, Al-Ḥā'īṭ) was the false W8 override and no longer matches, as intended. |
| not written | 633 = hamlet 422 + village 209 + town 2 (Al Qa\`id 2,913, Al Khuttah 3,355) | 633 / 422 / 209 / 2 | PASS |
| largest excluded resolved population | 4,688 (Munifat al Qa\`id) | 4,688 | PASS |
| excluded rows ≥ 5,000 on the resolved figure | 0 | "no other" (doc §4; builder assertion `write_doc.py:77`) | PASS |
| name-only collisions the relayed table would hit | 1 (الروضة ×2); with the governorate key: 0 | — | confirms W8 closed |
| population types / statuses | official 11, grid 5, derived 1; verified 8, secondary 4, unverified 5 | same (doc §2; status) | PASS |

## 4. Determinism

`build_register --dry-run` twice: both `rows 17; centres 9; tag_10k 4; tag_5k 15; header {'governorates_gastat': '9', 'governorates_listed': '9', 'road_target_mismatch': '4'}`, exit 0. `write_doc --dry-run` twice: identical SHA-256 `96cf3edc…1ab9f`; equal to `docs/regions/hail.md` up to the trailing newline. PASS.

## 5. Commands

| command | result | exit | time |
|---|---|---|---|
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/hail.parquet` | `ok hail.parquet: 17 rows, 9 governorates` | 0 | 0.8 s |
| `.venv/bin/pytest -q -p no:warnings tests/test_hail_register.py tests/test_region_sweep.py tests/test_docver.py` | 14 passed | 0 | 1.0 s |
| `.venv/bin/ruff check screening/sweeps/hail tests/test_hail_register.py` | All checks passed | 0 | |
| `.venv/bin/ruff format --check` (same paths) | 3 files already formatted | 0 | |
| `.venv/bin/python -m common.docver check docs` | `docver OK: 105 files` | 0 | |
| `.venv/bin/python -m common.manifest verify` | `manifest OK: 305 rows` | 0 | 1.2 s |

All PASS.

## 6. Hygiene

| check | verdict | evidence |
|---|---|---|
| Absolute home paths in the 8 new tracked-to-be files | PASS | `grep -n "/Users/[a-z]"` empty (the only one is the gitignored, untracked symlink `data/ksa/hail/citypop_hail_census2022.csv`). |
| the private-list terms | PASS | grep empty. |
| "will reduce", `git push`, secrets | PASS | greps empty. |
| `git ls-files data/ runs/ movies/` | PASS | only `data/README.md` and `data/ksa/tables/**` (licensed GASTAT tables with README). |
| Label | PASS | `docs/regions/hail.md:5` "Screening input, not a forecast. Synthetic demand, uncalibrated: scenario comparison, not a forecast." |
| Model names | PASS with note | No `claude-`, `haiku`, `sonnet`, `fable`. "Opus" appears only as "Opus judgement": the heading `docs/regions/hail.md:75` / `write_doc.py:159` (mandated by `prompts/REGION_HAIL.md:26` and `REGION_TEMPLATE.md:26`) and references to that list in `build_register.py:401,409`, `cities/ksa/regions/hail.csv` rows 4-5 (notes), `docs/status/r2-hail.md:23,25,43`, `docs/assumptions-r2-hail.md:10`. As instructed, I report it: it is outside the heading itself, in notes and working documents, none regulator- or public-facing. Template-vs-CLAUDE.md question for the coordinator, unchanged from passes 1-2. |

## 7. Status file `docs/status/r2-hail.md`

| check | verdict | evidence |
|---|---|---|
| Register counts 17 / 9 / 4 / 15 / 8 / 4 / 5 / 5 / 650 / 633 / 422 / 209 / 2 / 4,688 / 305 / 7 tests | PASS | all reproduce (sections 3 and 5 above; `grep -c "^def test_"` = 7). |
| Replaced-row count and method description | **FAIL** | Line 18: "the builder now matches every grid or OSM row by Arabic name against the relayed table … **Seven** universe rows are replaced in this way (Al Hulayfah Assofla, Al Ruwda, Al Qa\`id, Munifat al Qa\`id, An Nisiyah, Al Khuttah, **Arrwodhah**; the doc lists them by name)". Measured: **6**; `docs/regions/hail.md:58` lists six and not Arrwodhah; the builder (`build_register.py:249`) matches by (name, governorate), not by name. Line 7 ("the population precedence applied by name against the relayed table") and line 22 ("Matching is by Arabic name with tatweel removed") state the superseded method as the current one; only line 31 states the current one. A number in the status block that does not match the register, and a method description contradicted by the code, is the same defect class as pass-2 F2 (procedure step 12: every number matches what was measured). |
| docver count | WARN | line 16 "104 files"; measured 105 (the pass-2 copy now exists; this count moves with the verifier's own files, so a warning as in pass 2). |
| Label line | PASS | last line is "**Verifier:** pass 3 pending …"; no `REGION_HAIL: done`, correct before a PASS. |

## 8. Spot-check sample (seed 3, `random.sample(range(17), 2)`)

- Row 4, Ash-Shamlī (الشملي) 9,163, `S-cp2-gastat-008`, verified: xlsx `Alshamli` 9,163 (my read); live citypopulation.de Ash-Shamly 9,163, governorate Ash-Shamlī. PASS.
- Row 7, Al Ajfar (الأجفر) 7,518, `S-cp2-gastat-008`, verified: xlsx `Alajfir` 7,518; crosswalk `Alajfir: KSA-ST-00991` (`gastat_crosswalk.yaml:56`); live page Al-Ajfir 7,518, Baq'ā'. PASS.
- Live page, additionally: all 9 governorate figures, the total 746,406, Ḥā'il 448,623, Baq'ā' 19,659, Ash-Shanān 11,560, Ar-Rarwḍah 2,906 (Ḥā'il), Al-Khuṭah 3,355, Al-Ḥalīfah as-Suflā 4,151 (Al-Ḥā'īṭ), Al-Qā'id 2,913, Munīfat al-Qā'id 4,688, Al-Ḥafīr 3,243 (Mawqaq; still absent from the transcription, pass-1 W6, below 5k): every figure the register or the override step uses matches. No fabricated or misquoted figure found.
- Role source S-hail-006 (`https://gaca.gov.sa/web/en-gb/airport/hail-airport`): today the server redirects to the GACA home page, so the cited page could not be re-read; the airport role is independently carried by `economic_nodes.parquet` row `airport-has-hail` (S-cp1-100, GACA OPS report, verified). Not a contradiction; recorded as not live-verifiable today.

## 9. Open items I could not verify

- S-hail-006 (redirect today), S-hail-005 and S-r1a-204 (pass 2: 403 / TLS error; not retried) at their cited URLs; all three have a register-row or node trace.
- Geo-verify estimates not re-run in this track (disclosed deviation, status line 36; raster not in the worktree, disk gate).
- Elapsed time not recorded ("Not timed", status line 39; prompt task 5 asks for it in the status block).
- Still open from pass 2, warnings only: W3 `dist_method` string inaccurate for the 4 `road_target_mismatch` rows (e.g. CSV row 4: method says "to the station the road skim targets" while `nearest_committed_station` is `landbridge:muwai` and the road target is `landbridge:al-jumum`); W9 `used_in` for S-hail-001 still names only the pilot (`sources.yaml:143-144`, `index.csv:169`); W10 `docs/regions/hail.md` v1.0 hard-coded in `write_doc.py:26` and `docs/assumptions-r2-hail.md` v1.0 after substantive rewrites; W1/W4 uncommitted, no cost-log row (`docs/cost-log.md` has only the pilot row, line 18), no `docs/STATUS.md` entry (coordinator steps after a PASS).

## 10. Three most important fixes

1. **Make `docs/status/r2-hail.md` true of the current build:** line 18 "Seven … Arrwodhah" → six rows without Arrwodhah (or mark that sentence as the pass-1 state and point to line 31); lines 7 and 22 → "by Arabic name and governorate (prefix `محافظة ` stripped, tatweel removed)"; line 16 docver → the count at commit. Then the plain `REGION_HAIL: done` line.
2. **Finish the W8 closure in code:** fix the `_apply_relayed_precedence` docstring (`build_register.py:241`) and add the test pass 2 asked for (the الروضة pair resolves to one override; a forced duplicate key raises).
3. **Close the handoff warnings before commit:** `dist_method` for the 4 mismatched rows, the two S-hail-001 `used_in` records, the document versions, then commit `feat(screening): region sweep hail`; coordinator adds the cost-log row and settles the "Needs Opus judgement" heading.

VERDICT: FAIL
