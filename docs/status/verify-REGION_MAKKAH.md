> **Document version:** docs/status/verify-REGION_MAKKAH.md v1.1 | 31 Oct 2026 | Author: red-team-verifier | Status: verified

# Verifier report: REGION_MAKKAH (track `r2-makkah`)

Read-only review in the worktree `.worktrees/r2-makkah` with `.venv/bin/python`, 31 Oct 2026 16:25–16:35 +03. Nothing was fixed, committed or pushed. Scratch rebuilds went to `logs/verify-makkah-scratch/` (gitignored `logs/`).

## 1. Commands

| command | result | time |
|---|---|---|
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/makkah.parquet` | `ok makkah.parquet: 77 rows, 17 governorates`, exit 0, no warnings | 0.75 s |
| `.venv/bin/python -m pytest -q tests/test_makkah_register.py` | 3 passed, exit 0 | 0.53 s |
| `.venv/bin/ruff check screening/sweeps tests/test_makkah_register.py` | All checks passed, exit 0 | |
| `.venv/bin/ruff format --check` (same paths) | 4 files already formatted, exit 0 | |
| `.venv/bin/python -m common.docver check docs` | `docver OK: 103 files` (the worktree filter bug did not show here) | |
| `.venv/bin/python -m common.manifest verify` | 279 FAIL, all `file missing` under `data/ksa/...` (gitignored data present only in the main checkout). Known and accepted per the coordinator; the R2 row `nominatim-ardhiyat-boundary-2026-10-31` verifies: `shasum -a 256` = `826d9875…f60c9`, 505 bytes, equal to `cities/ksa/sources.yaml`. | |
| determinism: `build_rows()`+`write_outputs()`+`write_markdown()` run twice into scratch dirs (seed has no effect; the build has no randomness) | run1 == run2 byte-identical for `.parquet`, `.csv`, `.md`; and byte-identical to the committed artefacts | |

## 2. Acceptance criteria

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | Governorate count reconciles to GASTAT | PASS | Parquet header `governorates_gastat=17`, `governorates_listed=17`; `runs/gastat/region_check.csv` row `makkah,8021463,8021463,8021463,8021463,17,True`; `docs/gastat-regions.md:32` (Makkah 17) and `:212` ("17 rows"); A-makkah-008 says the count is a name join because the primary table has no region column. 17 centre rows, one per governorate (`centres per gov` all = 1). |
| 2 | Every settlement ≥ 10,000 in the official table appears as a row | **FAIL** (F1) | The 15 primary cities matched to Makkah settlements (`city_matches.csv`, `total ≥ 10000`) are all rows with `pop_type=official`, `verified`, `tag_10k=true` (count 15 = test). The 69 unmatched rows of `city_matches.csv` equal section 3 of `docs/regions/makkah.md` exactly (set difference empty both ways; sum 915,148). **But** the unmatched primary city `Alqawz 22,374` (`city_matches.csv:103`, S-cp2-gastat-008) is the Makkah town القوز in Al-Qunfudhah governorate; its match failed only because the name matcher tried `KSA-ST-06114` (a hamlet also named القوز in Khulays, grid population 0). The register's `Al Quoz` row (`KSA-ST-01313`, القوز, place=town, Al-Qunfudhah, node 1237962247) carries the OSM 2010 tag 23,391 as `derived`/`secondary`, `tag_10k=true`, with `primary_to_find = "GASTAT Census 2022 table for this locality"` and the note "OSM population tag, not a GASTAT figure" (register row 18), while `docs/regions/makkah.md:114` lists Alqawz as "not in the register" and the Opus list (section 6) does not name it. By the register's own account an official ≥ 10k Makkah city is not in the register, and the row that very probably is that city says no GASTAT figure exists. The two figures differ by 4.5 %. See F1. |
| 3 | `tag_5k` correct; no population without source id and `pop_type` | PASS | `tag_5k` true = 68 = rows with population ≥ 5,000 (no mismatch); every row with a population has `pop_source`, `pop_type`, `pop_year`, `pop_source_status` (query returned empty). Sources: S-r1a-505 ×41, S-cp2-gastat-008 ×25, S-makkah-009 ×6, S-makkah-001 ×2, null ×3 (the three no-population rows). |
| 4 | No committed/hypothetical line called existing; every economic role has a present S- id | PASS | `nearest_existing` ∈ {hhr:makkah, hhr:kaia, hhr:kaec, hhr:jeddah}; `nearest_committed` ∈ {landbridge:al-jumum, landbridge:jeddah, landbridge:muwai}; `nearest_committed_station` = "… (site unlocated; approximate, R1a)"; no note contains "existing". 20 roles on 7 rows; all 20 source ids (S-cp1-100/104/109/110/111, S-r1a-204/205/214/221/225/239/241, S-makkah-003) resolve in `docs/sources/*.csv` (missing set empty). |
| 5 | Parquet, CSV and Markdown agree; validates `--strict` | PASS | 77/77/77 rows; Parquet-vs-CSV: 0 mismatches over every scalar column; Markdown table vs Parquet: 0 mismatches on name EN/AR, governorate, population, pop type, 10k, 5k, screened. Seeded spot check (seed 20261031, rows 5, 9, 26, 28, 30, 31, 39, 48, 60, 65: `Usfan 5,761; غميقة 12,869; Shaqsan 11,688; Qiya 9,262; Al `Arfa' 9,168; Ushayrah 8,425; Bahrah 70,118; Mecca 2,385,509; `AbidalQurashi 6,542; بني سعد 6,482) identical in all three files. Strict validation exit 0. |

## 3. Rules

| rule | verdict | evidence |
|---|---|---|
| 1 No fabricated numbers; grid gate | PASS (gate) / see F1 (precedence) | Grid rows 41, all `unverified`; 12 grid rows ≥ 10,000 all `tag_10k=false` with `exclusion_reason="grid-only population, uncorroborated"`, `screened=true`; grid rows with `tag_10k=true` = 0 (test asserts the same). `pop_corroboration` null everywhere (no second method was run; honest). Adham override 9,022 documented at `build.py:92-114`, A-makkah-003, status decision 1, md section 6 item 1; the Al-Mahd drop at `build.py:112`, A-makkah-005, status decision 2, md item 8. Attribution: `screening/gastat_crosswalk.yaml:68-69` itself says "its figure 9,022 sits on the pilot row المهد … the 2010 bridge points to أضم instead: left unmatched". The register follows the bridge, not the crosswalk's "none"; the Adham node is 7.7 km from the Al-Mahd node, inside the same governorate, and `city_matches.csv:168` shows the figure is in the primary export under the name "Adham". Defensible, and disclosed as an assumption with the identity left open. Nit: the figure is cited as the relay S-makkah-001 although the identical row exists in the primary S-cp2-gastat-008; the row's `primary_to_find` says so, which is adequate. |
| 2 No silent omissions | PASS | 17/17 governorates have a centre row; 8 rows `screened=false`, each with a reason (1 duplicate, 1 centroid centre, 1 OSM tag without year, 5 towns < 5,000); the 12 grid-gate rows keep `screened=true` as the brief requires. Unmatched primary cities listed in full. |
| 3 Label | PASS | `docs/regions/makkah.md:5` "Screening input, not a forecast. Label: synthetic demand, uncalibrated: scenario comparison, not a forecast." and `:206`. No "will reduce" phrasing in the R2 files. |
| 5 Planned lines not "existing" | PASS | as criterion 4. |
| 7/9 No real-world action; no content from the author's company | PASS | `grep -i insurance|MGA|tawuniya|bupa|nphies|solutions` over the 10 R2 files: no hit; `grep "git push"` over the scripts: no hit. Nominatim was queried once (a public read-only API, raw response registered); no sign-up or payment. |
| 8 Hygiene | PASS | `grep -E "/Users/[a-z]|/home/"` over the R2 files: no hit; secrets grep: no hit; `git ls-files data runs movies film/renders film/audio` shows only the pre-existing GASTAT tables with READMEs (not R2); the R2 raw JSON is gitignored and in the manifest; the scratch dir is under gitignored `logs/`. `git status --porcelain`: all R2 files are untracked (`??`) and `cities/ksa/sources.yaml` modified; nothing committed yet (see F2). |
| Assumptions register | PASS | A-makkah-001…010 present with value, unit, range, source/assumption, status, used-in; `build.py` constants reference A-makkah-001/007, A-screen-pilot-001 and A-screen-031/032/038. |
| Licence register | PASS | `docs/licences-r2-makkah.csv` rows: OSM + Nominatim (ODbL, share-alike flagged), WorldPop 2020 (CC BY 4.0), GASTAT TA1 primary (use policy to confirm, pending Tariq), citypopulation.de (terms not checked, pending Tariq). OSRM (road minutes) is in the shared `docs/licences.csv:165` (R1a). No conflict resolved silently. |
| Document headers | PASS | All four Markdown files start with the version line (first lines read). |
| STATUS / handoff (verifier step 12; brief task 5) | **FAIL** (F2) | `docs/status/r2-makkah.md` has no `REGION_MAKKAH: done` / `blocked` line (`grep "^REGION_MAKKAH:"` exit 1; last line is "**Verifier.** Pending …"); nothing is committed; `docs/cost-log.md` has no row for this run (only the pilot row at line 13). |

## 4. Failures (exact evidence)

**F1. Official ≥ 10k figure for Al Quoz bypassed and not disclosed on the row (criterion 2; rule 1 precedence "official > derived", prompt line 14 "GASTAT figures win where they exist").**
- `runs/gastat/primary/city_matches.csv:103`: `Alqawz,22374,15873,6501,,,,universe (name): KSA-ST-06114 fails the plausibility guard (A-screen-038)`.
- `settlements.parquet`: `KSA-ST-06114` = Al Qawz القوز, hamlet, Khulays, grid 0, lat 22.02 N (the wrong candidate); `KSA-ST-01313` = Al Quoz القوز, town, Al Qunfudhah, lat 18.97 N, OSM tag 23,391 (2010), grid 11,854 (the likely match; 22,374 vs 23,391 = 4.5 %).
- Register row 18 (`Al Quoz`): `pop_source=S-makkah-009`, `pop_type=derived`, `pop_year=2010`, `tag_10k=true`, `primary_to_find="GASTAT Census 2022 table for this locality"`, notes "OSM population tag, not a GASTAT figure". `docs/regions/makkah.md:114` lists Alqawz 22,374 as "not in the register"; section 6 does not name it.
- The verifier does not decide the identity. The defect is that the register states no GASTAT figure exists for this locality while the primary export it read has one, that `tag_10k` rests on a 2010 volunteer tag where a 2022 official figure is available, and that the ambiguity is not in the Opus list. Same pattern below 10k (not criterion-2 failures, same fix): `Eshyrh 9,517` vs `Ushayrah` 8,425 derived 2010; `Ghuran 6,803` vs `Ghran` 6,400 derived with tag year 1882; `Alsayl 6,064` vs `Assel` 7,157 grid; `Aleurafa' 5,432` vs `Al `Arfa'` 9,168 grid; `Malkan 5,196`, `Alshaqiraa 6,069`, `Al Shoudayda 5,156` have no register row at all.

**F2. Handoff incomplete (brief task 5; verifier step 12).** No `REGION_MAKKAH: done` or `blocked` last line in `docs/status/r2-makkah.md`; no commit (`git status --porcelain` shows every R2 file as `??`); no cost-log row. The status file says the line is deferred to this verdict; the brief says the line ends the status block regardless.

## 5. Findings (not FAIL)

1. `docs/regions/makkah.md:99` heading "Unmatched GASTAT cities (not in the register)" is contradicted by its own row `Adham 9,022` (`:132`), which is in the register by override. Say "unmatched by the crosswalk" and mark the rows that the register attributes anyway.
2. 60 cells of the Markdown table print the literal `nan` (pop type, status and exclusion columns for rows without a population or exclusion; `build.py:689-693` uses `or ''`, which does not catch NaN). Cosmetic, but a public-facing table should not show `nan`.
3. A-makkah-004 (Al-Ardiyat centroid) is clearly disclosed: exclusion reason on the row, notes, assumptions row, status decision 4, md section 6 item 2, source S-makkah-008 with the raw JSON registered. The table shows `dist exist km 297.3` for a centroid; the caveat "to the located stations, not to the alignment" lives only in `notes`, which the Markdown table does not print.
4. A-makkah-003 (Adham) is clearly disclosed (see rule 1 above). Universe defect: `settlements.parquet` holds 9,022 on `KSA-ST-03308` (المهد, village, 7.7 km from the Adham node) and 10,484 (OSM 2010) on `KSA-ST-01876`; the register drops the former and overrides the latter. Coordinator defect, as briefed; not a register FAIL.
5. `Ghran` (6,400) carries OSM tag year 1882, flagged in notes; the likely primary counterpart `Ghuran 6,803` (F1 list) would replace it.
6. Known/accepted: manifest 279 "file missing" FAILs (data only in the main checkout); `common.docver check docs` actually passed here (103 files), so the filter bug did not reproduce in this run.
7. Spot check of sources: `city_matches.csv` is a `runs/` output, not a web source; the pilot source rows S-makkah-001…007 were not re-fetched (pilot scope, already verified at PILOT_MERGE). No figure in the R2 documents was found that lacks an S- id, an A- id or a `runs/` output.

## 6. Three most important fixes

1. Al Quoz: add the Alqawz 22,374 primary row to the Opus list and to the row's `primary_to_find`/notes; either request a crosswalk entry `Alqawz: KSA-ST-01313` (the crosswalk is a shared file, so via the coordinator) and rebuild with `official`/`verified`, or keep `derived` but state on the row that a primary figure exists and the identity is open. Do the same cross-reference for Eshyrh, Ghuran, Alsayl, Aleurafa', Malkan, Alshaqiraa and Al Shoudayda (likely-Makkah names), without resolving them by guessing.
2. Finish the handoff: `REGION_MAKKAH: done` (or blocked) as the plain last line of the status block, the `feat(screening): region sweep makkah` commit including `screening/sweeps/makkah/`, and the cost-log row.
3. Markdown table: no literal `nan`; retitle section 3 so it does not contradict the Adham override.

VERDICT: FAIL

---

# Pass 2 (31 Oct 2026, about 17:05 +03; supersedes the pass 1 verdict above)

Read-only re-check in the same worktree with `.venv/bin/python`. Nothing fixed, committed or pushed; scratch rebuilds under gitignored `logs/verify-makkah-scratch2/`. Pass 1's F2 (status last line, commit, cost-log row) is the coordinator's step by the coordinator's instruction and is not counted here.

## Commands

| command | result | time |
|---|---|---|
| `.venv/bin/python -m screening.region_sweep validate --strict cities/ksa/regions/makkah.parquet` | `ok   makkah.parquet: 77 rows, 17 governorates`, exit 0, no warnings | 0.85 s |
| `.venv/bin/python -m pytest -q tests/test_makkah_register.py` | 3 passed, exit 0 | 0.92 s |
| `.venv/bin/ruff check screening/sweeps tests/test_makkah_register.py` | All checks passed, exit 0 | |
| `.venv/bin/ruff format --check` (same paths) | 4 files already formatted, exit 0 | |
| `.venv/bin/python -m common.docver check docs` | `docver OK: 104 files` | |
| `.venv/bin/python -m common.manifest verify` | 279 `file missing` (known, accepted: data only in the main checkout); no other failure | |
| determinism: `build_rows()` + `write_outputs()` + `write_markdown()` twice into scratch dirs | run1 == run2 == committed artefacts, SHA-256 `b483561eec46…` (parquet), `e7a0c90b9997…` (csv), `736b41521147…` (md) | 0.35 s / 0.11 s |

## Items

| # | item | verdict | evidence |
|---|---|---|---|
| 1a | Governorate count 17 | PASS | Parquet metadata `governorates_gastat=17`, `governorates_listed=17`; `df.governorate.nunique()` = 17 (Adam, Al-Ardiyat, Al-Jumum, Al-Kamil, Al-Khurmah, Al-Lith, Al-Muwayh, Al-Qunfudhah, At-Ta'if, Bahrah, Jiddah, Khulays, Makkah al-Mukarramah, Maysan, Rabigh, Ranyah, Turubah); validate `--strict` prints 17. |
| 1b | Official ≥ 10k rows all present (15) | PASS | rows with `pop_type=official` and `population ≥ 10000` = 15, all `tag_10k=True`, all `pop_source_status=verified` (query output); test asserts the same. |
| 1c | `tag_5k` correct; no population without source | PASS | `tag_5k` true = 68 = rows with population ≥ 5,000; mismatches 0. Rows with a population and a null `pop_source` / `pop_type` / `pop_year` / `pop_source_status`: 0 / 0 / 0 / 0. `tag_10k` true = 16 (15 official + Al Quoz derived), as the status block states. |
| 1d | Committed lines never called existing; roles sourced | PASS | `nearest_existing` ∈ {hhr:makkah, hhr:kaia, hhr:kaec, hhr:jeddah}; `nearest_committed` ∈ {landbridge:al-jumum, landbridge:jeddah, landbridge:muwai}; no text column other than `nearest_existing` contains the word "existing". Roles unchanged from pass 1 (20 on 7 rows; all 20 S- ids resolved in pass 1; the rebuild is byte-identical, so the role data did not change). |
| 1e | Parquet, CSV, md agree | PASS | 77 / 77 / 77 rows; Parquet vs CSV: 0 mismatches over every scalar column (null pattern, numbers and strings); md table vs Parquet checked in pass 1 and the md is byte-identical to the rebuild from the same Parquet. |
| 2 | validate / pytest / ruff | PASS | table above; all exit 0. |
| 3a | `grep -nwi nan docs/regions/makkah.md` | PASS | no hit (exit 1); `build.py` `cell()` now returns `""` for None and NaN. |
| 3b | `grep -n "/Users/"` over the 10 R2 files and `screening/sweeps/makkah/*.py` | PASS | no hit (exit 1). |
| 3c | private-list terms (`insurance|MGA|tawuniya|bupa|nphies|solutions`, case-insensitive) over the same files | PASS | no hit (exit 1). Secrets grep: no hit. `git push` in `screening/sweeps`, tests: no hit. |
| 4 | Grid gate | PASS | grid rows 41, all `unverified`; grid rows ≥ 10,000 = 12; grid rows with `tag_10k=True` = 0; all 12 carry `exclusion_reason="grid-only population, uncorroborated"`. |
| F1 re-check | name candidates on the rows and in the md | PASS | Parquet and CSV `notes` identical: Al Quoz "…primary TA1 'Alqawz' 22,374 (unmatched; same Arabic name القوز; identity open): if confirmed, the official figure replaces the OSM tag 23,391; tag_10k stays true"; Ushayrah ← Eshyrh 9,517; Ghran ← Ghuran 6,803; Assel ← Alsayl 6,064; Al `Arfa' ← Aleurafa' 5,432 (all "identity open"). `docs/regions/makkah.md:99` heading now "Unmatched primary TA1 cities (name candidates are in the notes)"; `:199` (section 6 item 4) names the five pairs and states Malkan 5,196, Al Shoudayda 5,156, Alshaqiraa 6,069 have no candidate row, "Not changed without identity". Section 3 = 69 rows, set-equal to the 69 unmatched rows of `runs/gastat/primary/city_matches.csv` (md−cm = ∅, cm−md = ∅, no value differences, sum 915,148). No population value changed (rebuild hashes above). The remaining rows whose notes say "OSM population tag, not a GASTAT figure" without a candidate (Zalim 5,090, Missan 5,227, Saabar 6,237) have no resembling name in the export (`grep -iE "zal|dhal|missan|maysan|saab|sabar"` returns only Alshazalah/Alghazalah, different places); the phrase describes the OSM value, not a claim that no GASTAT figure exists. |
| smaller (a)(b)(c) | nan cells; section 3 heading and duplicate sentence; Al-Ardiyat caveat | PASS | (a) item 3a; (b) heading at `:99` no longer says "not in the register" (Adham 9,022 sits in that table at section-3 row 34 and in the register by override, no longer a contradiction), duplicated sentence gone; (c) `docs/regions/makkah.md:10` "Al-Ardiyat's centre is a centroid; its distances are to located stations, not to the alignment". |
| status / hygiene | | PASS (as scoped) | `docs/status/r2-makkah.md:48` has the verifier section; counts in it (77 rows, 17/17, 16 `tag_10k`, 68 `tag_5k`, 41 grid, 12 grid ≥ 10k held false, 15 official ≥ 10k) match the measurements above. `git status --porcelain`: only `cities/ksa/sources.yaml` modified; R2 files untracked (`??`), nothing under `data/`, `runs/`, `movies/`, `film/` added. The milestone last line, the commit and the cost-log row are the coordinator's step (not counted). |

## Open, not FAIL (carried from pass 1)

1. Universe defect: `settlements.parquet` holds 9,022 on `KSA-ST-03308` (coordinator item, as briefed).
2. Identity of Alqawz / Eshyrh / Ghuran / Alsayl / Aleurafa' remains open on the rows; a crosswalk entry (shared file, coordinator) would convert Al Quoz to `official`/`verified`. No guessing was done, which is the right call.
3. Handoff steps F2 for the coordinator: `REGION_MAKKAH: done` as the last line of `docs/status/r2-makkah.md`, the `feat(screening): region sweep makkah` commit (including `screening/sweeps/makkah/` and the `sources.yaml` row), and the cost-log row.

VERDICT: PASS
