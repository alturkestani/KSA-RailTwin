> **Document version:** docs/status/verify-REGION_ASIR.md v2.0 | 31 Oct 2026 | Author: red-team-verifier (claude-fable-5-1) | Status: verified

# Verification: REGION_ASIR, second run (after the Tanumah fix)

Read-only re-verification in worktree `r2-asir` against `prompts/REGION_ASIR.md` v1.4 (acceptance section, status-line rule on line 20, handoff on line 27), PROJECT.md rules 1, 2, 5, 10, 11 and the coordinator's list of checks. No WebFetch or WebSearch (coordinator instruction). All commands ran with `.venv/bin/python`; the verification scripts ran in memory and wrote nothing. The first-run report (`docs/status/verify-REGION_ASIR-run1.md`) was read only to confirm each finding's status; the verdict below is from this run's evidence.

Known and accepted by the coordinator (reported, not counted): `common.manifest verify` 279 `file missing` lines (gitignored raw data absent from this worktree); full `pytest` 2 failed + 3 errors, all `FileNotFoundError` on gitignored data (`tests/test_costs_register.py`, `tests/test_cp2_gastat_primary.py`); the heading "Needs Opus judgement" (prescribed by `prompts/REGION_ASIR.md:26`; 7 occurrences of "Opus" in `docs/regions/asir.md`, down from 9); the uncommitted state (`git status --porcelain`: 9 untracked paths; the coordinator commits after PASS).

## Step 1: commands

| command | result | time |
|---|---|---|
| `.venv/bin/ruff check .` | All checks passed, exit 0 | < 5 s |
| `.venv/bin/ruff format --check .` | 407 files already formatted, exit 0 | < 5 s |
| `.venv/bin/python -m pytest -q tests/test_region_asir.py` | 3 passed | < 3 s |
| `.venv/bin/python -m pytest -q` | 2 failed, 3 errors (accepted, gitignored data); all others passed | ~14 s |
| `.venv/bin/python -m common.docver check docs/regions/asir.md docs/assumptions-r2-asir.md docs/status/r2-asir.md` | docver OK: 3 files, exit 0 | < 1 s |
| `.venv/bin/python -m common.manifest verify` | 279 FAIL lines, all `file missing`; 0 non-missing failures (hash or otherwise) | < 2 s |
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/asir.parquet` | `ok   asir.parquet: 37 rows, 18 governorates`, exit 0 | 0.48 s |

Determinism (step 3): `build_rows()` called twice in memory gives identical row lists (sha256 of the sorted-key JSON `e5535ae08d11413c` both times, 37 rows). Rebuilt rows against the committed `asir.parquet`: every column equal (`economic_roles` and `sources` equal after list normalisation; the only difference is list vs. array representation). PASS.

## First-run findings: status

| finding | status now | evidence |
|---|---|---|
| F1 Tanumah (rule 1, acceptance bullet 2) | **RESOLVED** | Primary table `data/ksa/tables/gastat/census2022_TA1_city5k_primary.xlsx` (273 rows; columns City, Total, Saudi, Non-Saudi), row index 140: `Tanawma | 12442 | 7469 | 4973` (Tathlith, row 124: `15854 | 12442 | 3412`, the coincidence that caused the first error). Register row `osm_id 5889480125` (universe KSA-ST-01711): `population 12442`, `pop_type official`, `pop_source S-cp2-gastat-008`, `pop_source_status verified`, `pop_year 2022`, `tag_10k True`, `tag_5k True`, `screened True`, `primary_to_find` null; `build_register.py:143-148` sets `pop=("official", 12442, S_PRIMARY_CITY, "verified", None, 2022), primary="Tanawma"`. The universe row has `pop_quality tabulated_primary`, `population 12442`; the register keeps it. |
| F2 status-file form (prompt lines 20 and 27) | **OPEN** | `grep -n "^REGION_ASIR:" docs/status/r2-asir.md` returns nothing; the file (25 lines) ends with `- **Elapsed:** not measured.` The required plain last line `REGION_ASIR: done` or `REGION_ASIR: blocked - <reason>` is absent, and elapsed is still "not measured". Line 24 of the same file states "F2 (status form, fixed here)", which is not true of the file as it stands. Partially fixed: the S-asir id range is now correct (line 15: "S-asir-001, 003 to 014; there is no S-asir-002"; the CSV holds exactly those 13 ids) and the manifest note now gives the full 279 count. |
| F3 "Needs Opus judgement" | accepted by the coordinator | Heading at `docs/regions/asir.md:80`; prescribed by the prompt. Not counted. |
| F4 uncommitted work | expected | Coordinator commits after PASS. Not counted. |

## Criteria table

| # | criterion | result | evidence |
|---|---|---|---|
| 1 | 18 governorates reconcile to the primary table; one centre per governorate; Parquet header | PASS | Header `{'governorates_gastat': '18', 'governorates_listed': '18', 'seed': '1'}`. All 18 names in `build_register.GOVERNORATES_GASTAT` found in `census2022_TA1_governorate_primary.xlsx` (151 rows), 0 missing; their `Total` sums to 2,024,285 = the region total cited in `docs/regions/asir.md:24`. 18 centre rows, 18 distinct governorates. |
| 2 | Official populations equal the primary city table; derived = universe `osm_population`; grid = universe `grid_population` | PASS | All 14 rows with a `primary=` name checked (not a sample): Abha 334,290; Ahad Rafidah 79,202; Almajardah 21,837; Alnamas 22,541; Bishah 115,537; Khamis Mushait 535,065; Muhayil 97,967; Sarat Abidah 19,855; **Tanawma 12,442**; Fareah Tarib 8,722; Tathlith 15,854; Zahran Aljanub 24,134; Bahr Abu Sukaynah 10,862; Al Ithnayn 5,593; 14/14 equal. The 2 secondary official rows (Al-Birk 3,987; Al Harajah 4,540) are below 5,000 and absent from the primary table, as expected. 3 derived rows = `osm_population`, 18 grid rows = `grid_population`, 0 mismatches. All 14 universe `tabulated_primary` rows keep their primary figure (14/14). Completeness: 952 universe rows in G015–G031; 0 rows with population ≥ 5,000 missing from the register. |
| 3 | Grid rows ≥ 10,000 held out of `tag_10k` with the "grid-only population, uncorroborated" reason | PASS | Masloom 12,376; Al Harayr 10,260; King Faisal Military City 10,017: `tag_10k` False, `tag_5k` True, `screened` True, `exclusion_reason` "grid-only population, uncorroborated (WorldPop N; no second method run for this settlement, A-screen-033)". Exactly 3 rows. |
| 4 | `tag_5k` == population ≥ 5,000; `tag_10k` == population ≥ 10,000 except the gate; doc counts | PASS | 0 `tag_5k` errors; 0 `tag_10k` errors outside the gate; 0 null populations. Parquet counts: `tag_10k` 13, `tag_5k` 32, gate 3, screened out 1, centres 18; `pop_type` official 16 / derived 3 / grid 18 / null 0; status verified 14 / secondary 5 / unverified 18. These equal `docs/regions/asir.md:15-20` (13, 32, 3, 1, 16/3/18/0, 14/5/18) and `docs/status/r2-asir.md:8, :10`. |
| 5 | Distances and road minutes match the universe | PASS | Merge on `osm_id` (37/37 matched). Random 5, seed 20261031: Al Bashaer 289.8/292.1/300.3/306.7/180.2/217.8; Fir'ah Tarib 477.4/527.7/455.9/482.9/57.7/51.6; Tandahah 467.8/493.5/468.8/477.3/12.8/17.4; Al-Harjah 539.9/539.9/529.2/547.2/79.1/71.8; Dirs 399.6/415.8/423.3/423.1/57.4/71.2 (existing km/min, committed km/min, metro km/min), all equal to the universe. All 37 rows, 6 columns: 0 mismatches. |
| 6 | Parquet, CSV and Markdown agree | PASS | 37/37/37 rows; CSV columns identical; CSV vs Parquet on `osm_id`: 0 mismatches in population, `tag_10k`, `tag_5k`, `screened`. Markdown table (37 rows) vs Parquet on name: 0 mismatches in population, type/status, ≥10k, ≥5k, screened. Tanumah row `docs/regions/asir.md:44`: `12,442 | official / verified | Y | Y`. |
| 7 | `validate --strict` passes | PASS | `ok   asir.parquet: 37 rows, 18 governorates`, exit 0. |
| 8 | Every economic role has an S- source that resolves; `nearest_existing` names only existing stations; committed never styled existing | PASS | 9 roles on 4 towns, all sources `S-`; every cited id (S-asir-001, -008, -009, -010, -012, -013, S-cp1-100, S-cp2-gastat-008, S-r1a-204, -221, -240) resolves in `docs/sources/index.csv` or `docs/sources/r2-asir.csv`. `nearest_existing` = {"Haramain HSR (existing) - Makkah station"}; `nearest_committed` = {"Saudi Landbridge (committed; announced/planned)"}; stations both carry "(committed)". |
| 9 | Tanumah wording: no "null" or "rejected" Tanumah anywhere | PASS | `grep -n -i "tanumah\|tanawma\|01711"` over `docs/regions/asir.md`, `docs/assumptions-r2-asir.md`, `docs/status/r2-asir.md`, `screening/sweeps/asir/*.py`, `tests/`, `docs/sources/r2-asir.csv`: every hit states 12,442 from the primary table (asir.md:44, :94, :96; A-asir-003 `docs/assumptions-r2-asir.md:11` "the primary table figure 12,442 (Tanawma) is used"; S-asir-013 quote now says only that the OSM tag 14,684 equals the 2010 count). The one "null"/"rejecting" mention (`docs/status/r2-asir.md:12`) is the past-tense correction record ("an earlier build set Tanumah to null ... the rejection was wrong"), which is the required audit trail, not a current claim. The "GASTAT's 271-city table has no Tanumah row" sentence is gone. |
| 10 | Hygiene: no `/Users/` paths, no secrets, no `git push`; nothing new under `data/`, `runs/`, `movies/` | PASS | `grep -n "/Users/"` over the 9 new files: only the first-run report quoting the grep pattern itself (`verify-REGION_ASIR-run1.md:33`), no path. Secrets/`git push` grep: no match. `git ls-files data runs movies film/renders film/audio`: READMEs and the CP2 GASTAT tables only. |
| 11 | Labels, version headers, assumptions | PASS | `docs/regions/asir.md:5` carries "Synthetic demand, uncalibrated: scenario comparison, not a forecast" and "Screening input, not a forecast"; no "will reduce". Version headers on the three docs (docver OK). A-asir-001..005 registered, all `assumed`. Licences stated (`asir.md:106`); no new dataset. Note (not a failure, nothing committed yet): `docs/regions/asir.md` and `docs/assumptions-r2-asir.md` keep v1.0 after the Tanumah edit while the status file went to v1.1. |
| 12 | Status file: numbers match, milestone label line present, elapsed recorded | **FAIL** | Numbers match the Parquet (18/18; 37 = 18 + 19, 1 out; 13 = 12 official + 1 derived; 32; 3; 9 roles on 4 towns; 14/5/18; terrain 1). But: no `REGION_ASIR: done` / `blocked` last line (prompt line 20: "the last line of your status block is plain text at the start of the line ... `REGION_ASIR: done`"; line 27: "End with `REGION_ASIR: done`"); `Elapsed: not measured` (line 25; the prompt asks for elapsed and "not measured" is a FAIL under the verifier procedure); line 24 asserts F2 is fixed. Cost-log row for this run: none yet (coordinator's post-run step). |

Prompt acceptance bullets: governorate count reconciles (PASS); every settlement ≥ 10k in the official table appears, ≥ 5k tagged, no population without source id and type (PASS, Tanumah now included); no committed/hypothetical line called existing, every role sourced (PASS); Parquet/CSV/Markdown agree and the register validates (PASS).

## Failures with exact evidence

**F2 (open; prompt lines 20 and 27; verifier procedure step 12).** `docs/status/r2-asir.md` v1.1 ends at line 25 with `- **Elapsed:** not measured.`; `grep -n "^REGION_ASIR:"` finds no line. The orchestrator greps for `REGION_ASIR: done`; without it the milestone cannot be closed by the workflow in CLAUDE.md ("ending each milestone with `R<n>: done` or `R<n>: blocked - <reason>`; the orchestrator greps for that line"). Line 24 says "F2 (status form, fixed here)", which contradicts the file. Elapsed time is still not recorded.

No other failure. F1 is closed on primary evidence; F3 is accepted by the coordinator; F4 is the expected pre-commit state.

## Spot-check (step 9)

WebFetch prohibited; offline against the primary GASTAT tables, the value of record for this milestone. Sample: all 14 verified official rows (100 %, seed n/a), 14/14 equal to the primary `Total`; 2/2 secondary official rows correctly absent from the table; 18/18 governorate names found, sum 2,024,285. Distances: random 5 of 37 (seed 20261031), 30/30 values equal to the universe, plus a full 37-row check with 0 mismatches. No fabricated or misquoted figure found.

## Three most important fixes

1. Append the plain last line `REGION_ASIR: done` to `docs/status/r2-asir.md` (no bullet, bold or backticks) and record the elapsed time; correct line 24 so it does not claim F2 fixed until it is. Bump the file to v1.2.
2. Coordinator: commit as `feat(screening): region sweep asir` (including `screening/sweeps/asir/`, `tests/test_region_asir.py` and both verifier reports) and add the cost-log row; run `common.manifest verify` from the main checkout where the raw data lives.
3. Optional hardening (not required for PASS): the Tanumah regression was caught by the verifier, not by a test; a test asserting that every universe Asir row with `pop_quality == tabulated_primary` keeps its primary figure in the register would make a dropped primary row fail the build.

VERDICT: FAIL
