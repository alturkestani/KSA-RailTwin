> **Document version:** docs/status/verify-INTEGRATE_R6_V3.md v1.1 | 4 Nov 2026 | Author: red-team-verifier (read-only; pass 1 v1.0 on 035dd03: FAIL on F1; pass 2: re-check of 1e5de78) | Status: verified

# Verification report: INTEGRATE_R6_V3 (merge of track `r6v3`, judge v3 / CP7-3, into `main`)

Verifier: `red-team-verifier` on the main checkout, branch `main`, HEAD `035dd03` (`git describe` → `r6-14-g035dd03`, `git status --porcelain` clean), 4 Nov 2026 01:00–01:25 Asia/Riyadh. Read: `CLAUDE.md`, `prompts/INTEGRATE_R6_V3.md`, `prompts/R6_V3.md`, `docs/status/verify-R6_V3.md` (track verdict PASS at `d5ee720`), `docs/r6-topology.md` v1.2, `docs/r6/judge-hashes.md`, `docs/assumptions.md` v1.21, `docs/licences.{md,csv}` v1.8, `docs/status/r6v3.md`. Scratch outputs went to `/tmp/vint/`.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

## 1. Commands run (exit code, wall time)

| Command | Exit | Time | Output line |
|---|---|---|---|
| `uv run ruff check .` | 0 | 0.09 s | `All checks passed!` |
| `uv run ruff format --check .` | 0 | 0.04 s | `592 files already formatted` |
| `uv run pytest -q -o addopts=""` | 0 | 22.0 s | `481 passed, 9 warnings in 22.04s` |
| `uv run python -m common.docver check` | 0 | 0.15 s | `docver OK: 295 files` (296 once this report exists) |
| `uv run python -m common.manifest verify` | 0 | 1.4 s | `manifest OK: 386 rows` |
| `make test` | 0 | 24.2 s | lint, format, pytest, docver, manifest all green |
| README command `uv run python -m network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones.geojson --seed 1 --out /tmp/vint/demo1/`, run twice | 0, 0 | 2.3 s, 2.1 s | `nx_dijkstra_jeddah: 6 zones, 36 pairs, 0 unreachable, 6 snaps > 2.0 km`; `skims.parquet` and `zones_snapped.parquet` byte-identical across the two runs; `meta.json` identical except `runtime_s`/`created_utc` |
| `uv run python -m optimise.judge verify --name v3-variants` | 0 | 0.7 s | `judge/v3-variants intact: sha256 d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee` |
| `uv run python -m optimise.judge verify --name v2-p5b` | 0 | 0.7 s | `judge/v2-p5b intact: sha256 2bdee7f587c53ba872cc5fd10a61475496daca76dddab6a1271c103644e592ea` |
| `uv run python -m optimise.judge verify --name v1-r5` | 0 | 0.7 s | `judge/v1-r5 intact: sha256 f20091cf…` |
| `diff -rq .worktrees/r6v3/runs/r6 runs/r6` | 0 | 4.7 s | no output (0 lines) |
| `diff -rq .worktrees/r6v3/judge/v3-variants judge/v3-variants` | 0 | — | only "Directory loop detected" notices on the TrafficTwin symlinks; no file differs |

## 2. Acceptance criteria

### 2a. `prompts/INTEGRATE_R6_V3.md` acceptance list

| # | Criterion | Result | Evidence |
|---|---|---|---|
| I1 | `r6v3` merged with `--no-ff`, visible in `git log --merges`; no history rewriting | PASS | `git log --merges --oneline -3` → `593018e merge(R6_V3): r6v3`, `1fe457d merge(R6): r6`, `cae59b8 merge(R5): r5`; `593018e` has two parents `2e8a1ca` (main) and `5ca3472` (= `git rev-parse r6v3`, "docs(r6v3): VERIFY_R6_V3 PASS (pass 2); R6_V3 done"); `git merge-base --is-ancestor r6v3 main` → yes. `git reflog --date=iso` from `8bb11ec` (3 Nov 21:24) to HEAD shows only `commit`, `merge r6v3: Merge made by the 'ort' strategy`, `commit`: no reset, rebase or amend. `git diff r6v3 main --stat` → 9 files: the three deleted fragments, `docs/assumptions.md`, `docs/licences.{md,csv}`, `docs/cost-log.{md,csv}`, `docs/r6-topology.md` (the fold commit `035dd03` plus the R6_V3 cost-log row `2e8a1ca`), nothing else |
| I2 | Registers on main are supersets of the track registers; no silently dropped or overwritten ids | PASS | **Assumptions:** `git show r6v3:docs/assumptions-r6v3.md` has 7 rows A-r6-101…107; all 7 are in `docs/assumptions.md` lines 515–521, directly after A-r6-013 (line 514), and the 7 rows are byte-identical to the fragment (`diff` of the sorted row sets → empty). Row count: branch `docs/assumptions.md` 659 ids, main 666 = 659 + 7; `comm -23` branch→main → none dropped; duplicate-id check → none. `diff <(git show r6v3:docs/assumptions.md) docs/assumptions.md` → only the header (v1.20 → v1.21) and the 7 inserted lines. A-r6-003 status `approved`, A-r6-011 `accepted` (lines 504, 512) carried from the branch. **Licences:** fragment `git show r6v3:docs/licences-r6v3.csv` = 2 rows; `diff <(git show r6v3:docs/licences.csv) docs/licences.csv` → line 71 (R0 `HiGHS`) status "planned; unverified" → the fragment's superseded text, and the `[r6v3 use]` row appended at line 266 after the `[r6]` row (265); 267 → 268 lines; `licences.md` the same two changes plus the INTEGRATE_R6_V3 note at line 287 recording the old status. CSV: 11 columns on every one of the 267 data rows, no duplicate item names. The status replacement is what the fragment itself instructs ("INTEGRATE replaces the status of the R0 row with this text"), and the old text is recorded in the note: not silent. No `docs/sources/r6v3*.csv` existed on the branch (`git ls-tree -r r6v3` → only the three fragments), so `docs/sources/index.csv` had nothing to fold. Fragments deleted from the tree (`035dd03` stat: 3 deletions) |
| I3 | `make test` and the README command pass on main; the verifier report for the merged state exists | PASS | §1: `make test` exit 0 in 24.2 s; README command exit 0 in 2.3 s, deterministic across two runs; this file is the report |
| I4 | `docs/STATUS.md` reflects the merged state with measured numbers and carries every blocker and conflict | PENDING (by the coordinator's instruction, not counted as FAIL) | `docs/STATUS.md` v1.23 (3 Nov) has no R6_V3 or INTEGRATE_R6_V3 milestone row (`grep -n "R6_V3\|INTEGRATE_R6_V3" docs/STATUS.md` → only the CP7-3 decision line 268 and line 272); `docs/status/main.md` has no INTEGRATE_R6_V3 block (`grep -c` → 0); `CHANGELOG.md` has no r6v3 line; `docs/cost-log.csv` has the R6_V3 track row (line 57: `r6v3-R6_V3-try1 … 23.82 … done`) but no INTEGRATE_R6_V3 row yet. §5 lists what these must carry |

### 2b. `prompts/INTEGRATE_R6_V3.md` "R6_V3 specifics" (3 Nov addition)

| # | Criterion | Result | Evidence |
|---|---|---|---|
| S1 | Main `runs/r6/` copies replaced by the track's (APFS clone); v2 copies kept under `runs/_superseded/INTEGRATE_R6_V3/` | PASS | `diff -rq .worktrees/r6v3/runs/r6 runs/r6` → nothing missing or different (0 lines); `diff -rq .worktrees/r6v3/runs runs` → the only extra entry is `Only in runs/_superseded: INTEGRATE_R6_V3`. `runs/_superseded/INTEGRATE_R6_V3/r6/top5` (main's old top5) `diff -rq` against `runs/r6/top5-v2` → identical; `runs/_superseded/INTEGRATE_R6_V3/skims/demo/meta.json` holds the old demo meta. Sizes: `runs/r6/v3` 676 MB, superseded 1.7 MB |
| S2 | `judge/v3-variants/` cloned onto main read-only; `optimise.judge verify` shows v3 intact with the hash in `docs/r6/judge-hashes.md` | PASS | `ls -ld judge/v3-variants` → `dr-xr-xr-x`; `find judge/v3-variants -perm -u+w -type f \| wc -l` → 0 of 2,090; verify output `d9fef643…9fee` = `docs/r6/judge-hashes.md` row `v3-variants` (commit 0172345, 2,090 files) = `runs/r6/judge/v3-variants.hash.json` (`n_files` 2090, `sha256` d9fef643…, `commit` 017234562c…); v2-p5b and v1-r5 still intact. `git ls-files judge/` → `judge/README.md` only (the copies are gitignored) |
| S3 | `runs/skims/demo` on main | PASS (observation O2) | `diff -rq .worktrees/r6v3/runs/skims/demo runs/skims/demo` → `meta.json` differs (expected: re-run on main); the two metas differ only in `created_utc`, `runtime_s`, `code_version` (`r6-8-g8b98ce8-dirty` vs `r6-13-g593018e-dirty`), `config_hash` and the relative `pbf` path; `skims.parquet`/`zones_snapped.parquet` identical and identical to my two runs |
| S4 | `docs/STATUS.md`: R6_V3 row, layouts that changed, final CP7 layout set for R7; R7 not started | PENDING (as I4) / PASS on "R7 not started" | no `r7` branch or worktree work beyond the pre-existing `prompts/R7.md` edit (in the merge, from the coordinator's CP7 chain commit `8bb11ec`); `git branch --list 'r7*'` → none |

### 2c. `prompts/R6_V3.md` acceptance list re-checked on the merged state

| # | Criterion | Result | Evidence on `main` at `035dd03` |
|---|---|---|---|
| V1 | `judge/v3-variants/` read-only; hash in `docs/r6/judge-hashes.md`; every v3 run meta records it | PASS | S2 above; 261 top-level run metas under `runs/r6/v3/*/*/meta.json` carry `judge: v3-variants` and `judge_sha256: d9fef643…` (0 bad); `code_version: judge v3-variants @ 017234562c sha256 d9fef64384e2e25f`; sub-run metas inside the judge carry the worktree `git describe` (`r6-8-g8b98ce8`) as the track verifier recorded and §6 of the topology document discloses |
| V2 | v3 reproduces v2 on S0, S1, S6-L1..L5; only code change the variant id | PASS (unchanged by the merge) | `docs/r6/judge-v3-backtest.md` v1.0 on main ("8,763 / 8,763 identical"); `runs/r6/v3/backtest/` identical to the worktree (S1); `git diff tags/r6 --name-status` lists `optimise/layout.py` M (the one-line id fix verified by the track verifier at 1c); judge copies unchanged since the track (same sha) |
| V3 | Variant ids accepted by LineSpec; library and `results.tsv` with hypotheses; pruning rules registered | PASS | `tests/test_optimise_v3_variant_id.py` and `tests/test_optimise_v3_search.py` in the 481 passing tests; `runs/r6/v3/library/` and `results.tsv` identical to the worktree (S1); A-r6-101…107 on main (I2) with their YAML `cities/ksa/assumptions/r6v3_variants.yaml` (`pruning`, `search.max_restarts`, `search.rescore_capex_quantiles`, `national_reach`) tracked on main |
| V4 | CP7 layout set stated with before/after numbers; no adopted variant changes the P90 sign; L2 positive at P90 cost in every case | PASS | `docs/r6-topology.md` §0.2 table, all 13 rows re-read against `runs/r6/v3/cp7/cp7.csv` on main (see §3): every robust NPV, Δ, capex P50, Δ, capex P90 and the three P90-cost NPVs match to the rounded SAR m; `adoptable_A_r6_105` False on all 10 edit rows; L2 `npv_p90cost_low/medium/high` 3,986.41 / 4,771.25 / 5,589.37 > 0; `git diff tags/r6 --stat -- scenarios/` → empty (S6-L1..L5 untouched; no `-v2` copies, none needed); §0 opens with "no variant improves S6-L1, S6-L2 or S6-L3" |
| V5 | National reach a reported column only; A-r6-003 approved, A-r6-011 accepted; headers `reviewed` | PASS | `runs/r6/top5/top5.csv` on main: columns `national_reach_60_reported_only`, `national_reach_120_reported_only`, `national_reach_gain_{60,120}_reported_only`; each `runs/r6/top5/L*/score.json` has the block under `national_reach_reported_only` with the note "never in the score"; `robust_npv` of L1/L2/L3 (11,022.94 / 6,791.61 / 2,426.50) equal to `cp7.csv` and to the v3 back-test (S1); `docs/assumptions.md` lines 504/512 `approved`/`accepted`; `docs/r6-topology.md` and `docs/r6/judge-hashes.md` line 1 `Status: reviewed` |
| V6 | No new dependency; TrafficTwin untouched; no push | PASS | `git diff tags/r6 --stat -- pyproject.toml uv.lock` → empty; `git remote -v` → no remote (a push is impossible); `grep -rn "git push" scripts/ orchestrate.sh Makefile` → none; the `git push` strings in `logs/orch/*.jsonl` are all verifier grep commands searching for that string (checked by parsing every `tool_use` command: none executes a push); TrafficTwin not touched by this milestone (no command of the integration run addresses it; the track verifier confirmed its status on 4 Nov) |

### 2d. Standing checks (verifier procedure)

| # | Check | Result | Evidence |
|---|---|---|---|
| H1 | `git status --porcelain` clean; nothing tracked under `data/`, `runs/`, `movies/`, `film/renders/`, `film/audio/` beyond READMEs and licensed tables | PASS | clean; `git ls-files runs/ movies/ film/renders/ film/audio/` → none; `data/` holds only the pre-R6 GASTAT/pilgrim licensed tables with `README.md` files |
| H2 | No absolute home paths or secrets in tracked files | PASS | `git ls-files -z \| xargs -0 grep -ln "/Users/[a-z]"` → none; secrets regex grep (API keys, AWS, GitHub, Slack, private-key headers) → none |
| H3 | No content from the author's company; no model names in public-facing documents added by this milestone | PASS (observation O3) | private-list `grep -i` over tracked non-log files → only the prohibition sentences in `prompts/VERIFY_*.md` and `prompts/R8.md`; model-name grep over `docs/r6-topology.md`, `docs/r6/*.md`, `scenarios/*.yaml`, the r6v3 YAML → only the pre-existing `docs/r6-topology.md:112` ("in-session Claude turns", R6 v1.0, unchanged by this milestone; carried as an observation by verify-R6 and verify-R6_V3) |
| H4 | Labels and phrasing | PASS | label present in `docs/r6-topology.md` (×2), `docs/r6/judge-v3-backtest.md`, `docs/r6/judge-hashes.md`, `docs/status/r6v3.md` (×2), `judge/README.md`, `cities/ksa/assumptions/r6v3_variants.yaml`, every `cp7.csv` row and `national_reach.json`; `grep -iE "will reduce\|will transform\|should build"` over the R6 documents → none |
| H5 | Determinism | PASS | README command twice with `--seed 1`: parquet outputs byte-identical, `meta.json` identical except timing (§1) |
| H6 | Document headers bumped by the fold | PASS | `docs/assumptions.md` v1.20 → v1.21, `docs/licences.md` v1.7 → v1.8, `docs/r6-topology.md` v1.1 → v1.2, each naming INTEGRATE_R6_V3 and the change; docver OK |
| H7 | No dangling references to the deleted fragment files in tracked files (task 3 deletes them; task 4 fixes broken links) | **FAIL** | `git grep -nE "assumptions-r6v3\|licences-r6v3" -- . ':!docs/status/*' ':!prompts/*' ':!CHANGELOG.md' ':!logs/*'` → two hits. `docs/licences.md:287` is the fold note ("removed at INTEGRATE_R6_V3; see git history at merge commit 593018e"): fine. **`cities/ksa/assumptions/r6v3_variants.yaml:3`: `# Every value is a registered assumption (docs/assumptions-r6v3.md, A-r6-1xx).`** points at a file that no longer exists on main. The builder left it on purpose "so its config hash recorded in run metas stays valid", but that premise is false: `common/runmeta.py:53` `config_hash` is the SHA-256 of the canonical JSON of the **parsed** config, and `optimise/variants.py:60` loads this file with `yaml.safe_load`, which drops comments. Test: `config_hash(yaml.safe_load(text))` equals `config_hash(yaml.safe_load(text with the comment repointed))` → `True`. No recorded hash depends on the comment (the run metas' `config_hash` values differ per layout and none hashes the file bytes), so the repoint is free, and `docs/r6-topology.md` §0.2 received exactly this repoint in `035dd03`. See §4 F1 |

## 3. Number tracing and spot-check

This milestone adds no externally sourced figure; every new or moved figure is a `runs/` output, so the 10 % WebFetch sample does not apply. Instead, every figure of the §0.2 table and the §0.1 national-reach rows was re-read from the run files **on main** (not from the worktree):

| Figure in `docs/r6-topology.md` | Run file on main | Match |
|---|---|---|
| L1 11,023 / 11,194 / 41,304 / −2,958 / −724 / 1,631 | `runs/r6/v3/cp7/cp7.csv` row S6-L1: 11022.94 / 11194.20 / 41304.41 / −2957.61 / −723.93 / 1630.85 | yes |
| L1 spur non-elec 10,648 (−375) / 10,156 (−1,039) / 37,172 / −2,008 / 230 / 2,571 | row S6-L1-kharj_nonelec: 10647.65 (−375.29) / 10155.54 (−1038.66) / 37171.66 / −2007.72 / 230.03 / 2571.03 | yes |
| L1 commuter 5,224 (−5,799) / 11,209 (+15) / 41,153 / −8,213 / −5,689 / −3,055 | row S6-L1-kharj_commuter: 5223.55 (−5799.38) / 11209.28 (+15.08) / 41152.75 / −8213.41 / −5688.58 / −3055.32 | yes |
| L1 commuter + non-elec 1,867 (−9,156) / 10,171 (−1,024) / 37,020 / −10,187 / −7,635 / −4,996 | row S6-L1-kharj_commuter-nonelec: 1867.40 (−9155.54) / 10170.61 (−1023.59) / 37019.99 / −10187.28 / −7635.38 / −4995.98 | yes |
| L2 6,792 / 1,423 / 5,286 / 3,986 / 4,771 / 5,589 | row S6-L2: 6791.61 / 1423.07 / 5286.11 / 3986.41 / 4771.25 / 5589.37 | yes |
| L3 2,427 / 19,630 / 73,799 / −21,745 / −19,225 / −16,624 | row S6-L3: 2426.50 / 19630.11 / 73798.60 / −21744.87 / −19224.97 / −16624.23 | yes |
| L3 drop Al-Muzahimiyah 1,742 (−684) / 19,479 (−151) / 73,262 / −22,256 / −19,847 / −17,343 | row …r225_drop-muzahimiyah: 1742.36 (−684.14) / 19479.24 (−150.87) / 73262.11 / −22256.34 / −19847.11 / −17343.41 | yes |
| L3 belt 225 non-elec −380 (−2,807) / 19,005 (−626) / 71,309 / −23,742 / −21,183 / −18,645 | row …r225_nonelec: −380.14 (−2806.64) / 19004.53 (−625.58) / 71309.49 / −23742.21 / −21183.24 / −18645.01 | yes |
| L3 belt 225 non-elec + drop −1,040 (−3,466) / 18,854 (−776) / 70,773 / −24,242 / −21,777 / −19,347 | row …r225_nonelec-drop: −1039.71 (−3466.21) / 18853.66 (−776.45) / 70772.997 / −24242.05 / −21776.89 / −19347.25 | yes |
| L3 Al-Kharj non-elec −144 (−2,571) / 18,591 (−1,039) / 69,666 / −22,944 / −20,429 / −17,863 | row …kharj_nonelec-r225_base: −144.25 (−2570.75) / 18591.44 (−1038.66) / 69665.85 / −22944.24 / −20428.61 / −17863.40 | yes |
| L3 Al-Kharj non-elec + drop −806 (−3,233) / 18,441 (−1,190) / 69,129 / −23,442 / −21,037 / −18,568 | row …kharj_nonelec-r225_drop-muzahimiyah: −806.22 (−3232.73) / 18440.57 (−1189.53) / 69129.36 / −23442.23 / −21037.37 / −18567.57 | yes |
| L3 both non-elec 215 (−2,212) / 17,966 (−1,664) / 67,177 / −21,754 / −19,272 / −16,747 | row …kharj_nonelec-r225_nonelec: 214.98 (−2211.52) / 17965.87 (−1664.24) / 67176.74 / −21754.20 / −19271.95 / −16746.86 | yes |
| L3 both non-elec + drop −447 (−2,873) / 17,815 (−1,815) / 66,640 / −22,247 / −19,864 / −17,451 | row …kharj_nonelec-r225_nonelec-drop: −446.98 (−2873.48) / 17814.998 (−1815.11) / 66640.24 / −22247.02 / −19864.14 / −17450.65 | yes |
| "Final layout set": spur share ≈ 4,231; P90 Δ ≈ 36 bn; P50 Δ ≈ 9.8 bn | 11,022.94 − 6,791.61 = 4,231.3; 41,304.41 − 5,286.11 = 36,018.3; 11,194.20 − 1,423.07 = 9,771.1 | yes |
| §0.1 national reach 60/120: L1 23.36/26.67 M, L2 22.94/26.25, L3 23.40/26.67, L4 24.38/26.89, L5 24.21/26.63; S1 22.35/26.10 of 35.93 M; gains L1 +1.01/+0.57, L2 +0.59/+0.15, L3 +1.05/+0.57, L4 +2.04/+0.79, L5 +1.87/+0.54; L1 cap-limited 26.47 M | `runs/r6/top5/top5.csv` and `runs/r6/top5/L*/score.json` `national_reach_reported_only`: 23,356,939 / 26,665,882; 22,940,241 / 26,249,184; 23,397,680 / 26,665,882; 24,384,863 / 26,888,852; 24,214,053 / 26,634,590; S1 22,345,984 / 26,096,670 of 35,927,621; gains 1,010,955 / 569,212; 594,257 / 152,514; 1,051,696 / 569,212; 2,038,879 / 792,182; 1,868,069 / 537,920; `within_120_with_access_cap` 26,471,658 | yes |
| §0.2 "registers A-r6-101…107 (`docs/assumptions.md` …)" (the repointed sentence) | `docs/assumptions.md` lines 515–521 | yes |

Every figure traced matches. The track verifier's recomputations (library counts, MILP, GA fronts, re-score Spearman 0.992) were not repeated: the run files are byte-identical to the worktree's (`diff -rq` empty) and no code path changed on main since the track verdict except the fold commit (docs only).

## 4. Failures (exact evidence)

**F1 — stale pointer to a deleted file, left on a false premise (H7).** `cities/ksa/assumptions/r6v3_variants.yaml`, line 3: `# Every value is a registered assumption (docs/assumptions-r6v3.md, A-r6-1xx).` The file `docs/assumptions-r6v3.md` was deleted in `035dd03` (task 3) and the rows now live in `docs/assumptions.md` A-r6-101…107. `prompts/INTEGRATE_R6_V3.md` task 4 puts "broken links" inside the builder's remit. The stated reason for not repointing it (keeping the run metas' `config_hash` valid) does not hold: `common/runmeta.py:53` hashes `canonical_json(config)` of the dict returned by `yaml.safe_load` (`optimise/variants.py:60`), which carries no comments; the hash is unchanged by the edit (tested, `True`). The equivalent pointer in `docs/r6-topology.md` §0.2 was repointed in the same commit, so the two documents are now inconsistent about where A-r6-1xx lives. The track verifier failed the same class of defect at R6_V3 (A-r6-104's non-existent path); it is not softened here because the fix is one line.

No other failure. Every run, hash, register row, test and figure checked is correct on main.

## 5. Pending by design (not FAILs): what `docs/STATUS.md`, `docs/status/main.md` and `CHANGELOG.md` must carry

The builder writes these after this report. They must state the numbers measured here, not the track's:

1. `docs/STATUS.md` (header bump, 4 Nov 2026): milestone rows **R6_V3** (done on track `r6v3`, `R6_V3: done`, verifier `docs/status/verify-R6_V3.md` v1.1 PASS on pass 2, merged by INTEGRATE_R6_V3) and **INTEGRATE_R6_V3** (merge `593018e` `--no-ff`, no conflict; fold `035dd03`; verifier this file); measured numbers: 481 tests, docver 295 (296 with this report), manifest 386, README command exit 0 in about 2.3 s, judge v3 `d9fef643…` intact, v2 `2bdee7f5…` intact, 7 assumption rows and 1 licence row folded plus the R0 HiGHS status replacement, `runs/r6` identical to the track (`diff -rq` empty), `runs/_superseded/INTEGRATE_R6_V3/` holds main's old `top5` (= `top5-v2`) and the old demo meta; disk `df -h ~` 37 GiB free (below the R3 gate of 40 GiB; above the R1a gate); cost so far `uv run python -m common.cost_log summary` TOTAL 56 runs, USD 738.89 list, r6v3 USD 23.82 (an INTEGRATE_R6_V3 cost row is still to be appended by the orchestrator).
2. "Layouts that changed": **none**; the final CP7 layout set for R7 is `scenarios/S6-L1..L3.yaml` as at tag `r6` (`git diff tags/r6 -- scenarios/` empty), with the L1 Al-Kharj P90-cost risk stated (§0.2).
3. Open issues carried from verify-R6_V3 observations: gitignored `runs/r6/v3/national_reach.json` (layout keys) and `runs/r6/v3/rescore/fast_vs_full.csv` (`source` column) store absolute paths under the `.worktrees/r6v3` checkout (allowed under rule 8 for untracked files; never copy them into `docs/`); `docs/r6-topology.md:112` "in-session Claude turns" to be reworded before R8's public documents; CP7 `results.tsv` hypotheses are file names; if `rescore_capex_quantiles` ever changes, `runs/r6/v3/rescore/` must be re-run or marked as produced under value 6. Plus F1 above until fixed.
4. `docs/status/main.md`: INTEGRATE_R6_V3 block (merged branch `r6v3` at `5ca3472`, conflicts none, verifier verdict, test count 481 and time, elapsed), ending `INTEGRATE_R6_V3: done` (only once F1 is fixed and re-verified) or `blocked`.
5. `CHANGELOG.md`: an `r6v3` (or R6_V3 + INTEGRATE_R6_V3) section line.

## 6. Observations (not FAILs)

- **O1** `runs/skims/demo/meta.json` on main records `code_version: r6-13-g593018e-dirty`: the builder ran the README demo with the fold edits uncommitted. My clean re-run gives `r6-14-g035dd03`. Re-run the README command once after the final status commit so the demo meta on main carries a clean code version (memory note "Run meta -dirty from staged files").
- **O2** `.worktrees/r6v3/runs/skims/demo/meta.json` also carries `-dirty` and a different relative `pbf` path (`../../../TrafficTwin/...` vs `../TrafficTwin/...`): both resolve to the same symlinked file (`pbf_sha256` identical), so the data hash is unaffected.
- **O3** `docs/r6-topology.md:112` names "Claude" (pre-existing, R6 v1.0). It is an internal methods document today, but CLAUDE.md asks that model names stay out of public-facing documents; reword before R8 draws on it.
- **O4** `judge/README.md` v1.1 and the r6v3 YAML are outside docver's paths; both headers were read by eye and are well-formed.
- **O5** `make test` reports `592 files already formatted` on main (the track reported 593/594 in its worktree, which had the fragment files and the verifier report): informational.

## 7. The three most important fixes

1. Repoint `cities/ksa/assumptions/r6v3_variants.yaml` line 3 to `docs/assumptions.md` (A-r6-101…107; "folded from the r6v3 fragment at INTEGRATE_R6_V3"), bump its header to v1.2 with INTEGRATE_R6_V3 as an author, and state in `docs/STATUS.md` that the edit changes no `config_hash` (parsed-YAML hash; comments excluded). One line; no run needs re-running.
2. Write the pending `docs/STATUS.md` rows, decisions and open issues, `docs/status/main.md` block and `CHANGELOG.md` line with the numbers in §5, then append the INTEGRATE_R6_V3 cost-log row.
3. Re-run the README command after the final commit so `runs/skims/demo/meta.json` on main records a clean `code_version` (O1); then re-run this verifier for the closing verdict.

Pass-1 verdict (HEAD 035dd03): FAIL on F1.

---

## 8. Pass 2 (4 Nov 2026, 01:30–01:45 Asia/Riyadh): re-check of the builder's fix and the pending items, HEAD `1e5de78`

Scope: HEAD `1e5de78` (`chore(R6_V3): integrate track and update status`; `git describe` → `r6-15-g1e5de78`; `git status --porcelain` clean). `git show --stat 1e5de78` → 6 files: `CHANGELOG.md`, `cities/ksa/assumptions/r6v3_variants.yaml`, `docs/STATUS.md`, `docs/assumptions.md`, `docs/status/main.md` and the pass-1 copy of this report; no code, scenario, test, run or judge file changed (`git diff 035dd03 HEAD --name-status` lists only those six). Pass-1 items that no file in `1e5de78` could touch (merge structure I1, register supersets I2, runs/judge clones S1–S2, R6_V3 criteria V2–V6, number tracing §3) stand and were spot-confirmed where cheap.

### 8.1 Commands run (exit code, wall time)

| Command | Exit | Time | Output line |
|---|---|---|---|
| `make test` (ruff check, ruff format --check, pytest, docver, manifest) | 0 | 22.4 s | `All checks passed!`; `593 files already formatted`; `docver OK: 296 files`; `manifest OK: 386 rows` |
| `uv run pytest -q -o addopts=""` | 0 | 22.3 s | `481 passed, 9 warnings in 22.27s` |
| `uv run python -m optimise.judge verify --name v3-variants` | 0 | 0.7 s | `judge/v3-variants intact: sha256 d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee` |
| `diff -rq .worktrees/r6v3/runs/r6 runs/r6` | 0 | — | 0 lines |
| `uv run python -m common.cost_log summary` | 0 | — | `TOTAL runs 56 hours 24.87 USD 738.89` |
| `df -h ~` | 0 | — | 37 Gi free of 460 Gi |

### 8.2 Items re-checked

| Item | Result | Evidence |
|---|---|---|
| **F1** stale pointer in the r6v3 YAML | **PASS** | `cities/ksa/assumptions/r6v3_variants.yaml:3` now reads `# Every value is a registered assumption (docs/assumptions.md, A-r6-1xx; folded from the r6v3 fragment at INTEGRATE_R6_V3).`; line 1 header bumped to v1.2 with `INTEGRATE_R6_V3 (register pointer)` as an author. `git diff 035dd03 HEAD -- cities/ksa/assumptions/r6v3_variants.yaml` changes comment lines only (non-comment line set identical). Hash: `config_hash(yaml.safe_load(old))` = `config_hash(yaml.safe_load(new))` = `f43700eeed6272e4…`, identical → no run meta is affected. `git grep -nE "assumptions-r6v3\|licences-r6v3"` outside status/prompts/changelog/logs → only the two fold notes (`docs/assumptions.md:694`, `docs/licences.md:287`), both of which say the file was removed and point at the merge commit: no dangling pointer remains |
| **I4** `docs/STATUS.md` reflects the merged state with measured numbers, blockers and conflicts | **PASS** | v1.24, 4 Nov 2026, author INTEGRATE_R6_V3. Rows **R6_V3** (done on `r6v3`, verifier v1.1 PASS on pass 2, merged; judge `d9fef643…`, back-test 8,763 / 8,763, 143 variants, no layout changed, L1 11,023 / L2 6,792 / L3 2,427) and **INTEGRATE_R6_V3** (merge 593018e no conflict; assumptions +7, licences +1 with the R0 HiGHS status updated, sources +0; 481 tests; manifest 386; judges v3 and v2 intact; README demo exit 0 in 2.2 s) match what I measured (my README timing 2.1–2.3 s). "Last updated" line states **no layout changed** and that the CP7 set for R7 stays `scenarios/S6-L1..L3.yaml`; R7 not started (`git branch --list 'r7*'` → none; no `r7` worktree). Disk 37 GiB (`df -h ~` → 37 Gi) with the R3 gate note; cost 738.89 over 56 runs, 24.87 h, "before the INTEGRATE_R6_V3 row, which `run_track.sh` appends at run end" (= `cost_log summary`). Decisions block records the merge order (cost-log row committed first), the register fold with the old HiGHS status, the clones and superseded copies, the layout decision with the L1 P90-cost figures (−2,958 / −724 / 1,631 = `cp7.csv`), and the pointer fix with the hash statement ("`config_hash` hashes the parsed YAML, so no run meta changes; measured identical before and after": true, see F1). Open items carry the verify-R6_V3 and pass-1 observations (absolute worktree paths in two gitignored files, D-r6v3-08 rounding, file-name hypotheses, 286 sub-run metas, line 112 rewording for R8, the A-r6-107 re-run condition, the ODbL alignment note). Conflicts: none to carry (none occurred) |
| **S4** STATUS: layouts that changed; final CP7 layout set; R7 not started | **PASS** | as I4: "no layout changed"; set = S6-L2 (cost-robust, positive at P90 cost in every case), S6-L1 (highest robust NPV, Al-Kharj spur P90 risk stated), S6-L3 optional; `git diff tags/r6 --stat -- scenarios/` still empty |
| `docs/status/main.md` INTEGRATE_R6_V3 block | **PASS** (closing line pending by design) | v1.11; block lists the merged branch `r6v3` (tip 5ca3472, `R6_V3: done`), the merge 593018e, "Conflicts and resolution: None", the register fold figures, the data clones and `diff -rq` result, the layout decision, verification numbers (481 passed, 473 → 481, manifest 386, about 24 s; README demo 2.2 s), the pass-1 FAIL and its fix, and the STATUS/CHANGELOG summary. The final `INTEGRATE_R6_V3: done` line is to be appended after this verdict, as the coordinator instructed |
| `CHANGELOG.md` | **PASS** | new section `## r6v3 — 2026-11-04`: one R6_V3 line (judge v3 hash, 8,763 / 8,763, 143 variants, national reach reported column, no layout changed, "in the model, S6-L1 11.0 bn and S6-L2 6.8 bn", the label, tests 473 → 481) and one INTEGRATE_R6_V3 line (merge, registers +7/+1/+0, clones). Figures match the run files and §3 |
| `docs/assumptions.md` track note | **PASS** | line 694 "R6_V3 track notes (INTEGRATE_R6_V3, 4 Nov 2026)": 7 rows, removed after the merge with the merge commit named, inserted after A-r6-013 byte-identical, no collision, YAML named, label present. Header v1.21 unchanged (already credited INTEGRATE_R6_V3 in 035dd03); docver OK |
| **O1** README demo meta on main clean | **PASS** | `runs/skims/demo/meta.json`: `code_version: r6-15-g1e5de78` (no `-dirty`), `seed 1`, `created_utc 2026-11-03T22:11:20+00:00` (after the commit) |
| Cost-log row for INTEGRATE_R6_V3 | pending by design | `grep -c INTEGRATE_R6_V3 docs/cost-log.csv` → 0; appended by `run_track.sh` at run end, as for every previous INTEGRATE run (the R6_V3 track row is present, line 57) |
| Regression: judge, runs, hygiene | **PASS** | v3 intact (same sha as pass 1); `diff -rq .worktrees/r6v3/runs/r6 runs/r6` → 0 lines; `git ls-files runs/ movies/ film/renders/ film/audio/` → none; `git ls-files -z \| xargs -0 grep -ln "/Users/[a-z]"` → none; `git status --porcelain` clean before this edit |

### 8.3 Observations (not FAILs)

- The coordinator's message quotes the before/after hash as `952f0042583873a5…`. That prefix is `sha256(json.dumps(parsed, sort_keys=True))`, not the project's `common.runmeta.config_hash` (canonical JSON with compact separators), which gives `f43700eeed6272e4…` for the same dict. Both are identical before and after the edit, and neither prefix is written in any tracked document (`git grep` → none), so no document figure is affected; cite `config_hash` if the value is ever recorded.
- `make test` prints the pytest summary through `uv run pytest -q` with the repository `addopts`; the plain `481 passed` line was confirmed by a direct run (8.1).
- Pass-1 observations O2–O5 stand (worktree demo meta `-dirty`, `docs/r6-topology.md:112`, YAML and `judge/README.md` outside docver, format file count), all recorded in `docs/STATUS.md` open items or immaterial.

### 8.4 Verdict

F1 is closed with evidence; the pending status, changelog and register-note items are written with numbers that match what was measured; the fix commit touches no code, run or judge; tests, lint, docver, manifest and the judge hash are green at HEAD `1e5de78`. The only open items (the `INTEGRATE_R6_V3: done` line in `docs/status/main.md` and the INTEGRATE_R6_V3 cost-log row) are ordered after this verdict by the prompt and the orchestrator.

VERDICT: PASS
