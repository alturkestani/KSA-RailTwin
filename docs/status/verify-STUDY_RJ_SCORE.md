> **Document version:** docs/status/verify-STUDY_RJ_SCORE.md v1.0 | 6 Nov 2026 | Author: red-team-verifier (claude-fable-5-1) | Status: verified

# VERIFY_STUDY_RJ_SCORE (read-only; HEAD 6d61dc4, start HEAD 6291a1c)

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Study sketch, not the recommended programme.

## Commands run (exit codes)
| command | result |
|---|---|
| `make test` | exit 0, 48 s: ruff check "All checks passed!", ruff format "708 files already formatted", pytest, `docver OK: 359 files`, `manifest OK: 388 rows` (no downloads) |
| `uv run pytest` | **857 passed**, 10 warnings, 44 s (matches the status block: 829 + 28 new) |
| `uv run pytest tests/test_study_rj_score.py` | 28 passed; `::test_s1_and_published_top5_keep_landbridge_byte_unchanged` passed on its own |
| `uv run python -m optimise.judge verify --name v3-variants` | exit 0: `judge/v3-variants intact: sha256 d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee` |
| `git diff --name-only 6291a1c HEAD -- judge optimise` | empty |
| `git diff --stat 6291a1c HEAD` | 12 files, +1,687 / −6 (at 1ce6b4e, before the status block: +1,621 / −5, as the block states) |
| `git status --porcelain` | clean; `git stash list` empty; no tag contains 6291a1c (`git describe` = r8.1-21-g6d61dc4) |
| README command | README names `make test` as the project command (README line 10); the milestone's reproduce block is in `docs/rj-routes-study.md` §8 (judge scoring commands not run here, per the verifier brief) |
| `common.scenarios validate` on each `scenarios/study/replace-rj-*.yaml` | `ok 1 scenario files` ×5 |

## Criteria (prompt `prompts/STUDY_RJ_SCORE.md` + verifier brief items 1–12)

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | Tests green, docver, manifest verify without downloads, README command | PASS | table above; `make test` exit 0; pytest 857 passed |
| 2a | Judge frozen: verify intact, sha256 d9fef643… | PASS | `optimise.judge verify` output above; `logs/study-rj-score-judge-verify-{before,after}.log` both show the same sha256; every `meta.json` has `judge_sha256` d9fef643…, `judge_fingerprint_checked: true` |
| 2b | `git diff --name-only 6291a1c HEAD -- judge optimise` empty | PASS | empty |
| 2c | No file under `judge/` newer than the run start | PASS | `find judge -type f -newer runs/study/rj/score/replace-rj-a/meta.json` empty; newest file under `judge/` is 4 Nov 2026 (`judge/README.md`); runs created 2026-11-06T20:28:06Z…20:31:00Z |
| 3a | Landbridge omitted only under the study marker | PASS | `study/rj_judge.py` lines 72–74: `MARKER = load_marker(_M) if _M else None; if MARKER: install(MARKER)`; `install()` wraps `railgraph.scenario_lines` to drop `omit_lines` only for `scenario == "S1"`; `optimise/` unchanged (diff empty); `tests/test_study_rj_score.py::test_s1_and_published_top5_keep_landbridge_byte_unchanged` passed (asserts `"landbridge" in plain["ids"]`) |
| 3b | Each score.json: no landbridge in `by_line_2050_medium`, exactly one RJ sketch | PASS | by_line keys for all five = `[RJ-x, gcc-railway-ksa, hhr, riyadh-rail-link, sar-east-passenger, sar-north-passenger]`; `loads_2050_medium.landbridge` = None (no pretended landbridge_pax) |
| 3c | meta.json: landbridge_omitted, marker, judge sha256, seed 1, layout hash, git describe, not dirty | PASS | all five: `landbridge_omitted: true`, `study_marker: study_rj_replace`, `omitted_lines: [landbridge]`, `seed: 1`, `layout_hash` (7fd82b605445 / cd644c13a828 / 29870883bd89 / 6b32d9e5744a / 3c87e77116fe), `harness_code_version: r8.1-15-g06507ec` (clean, no `-dirty`); `code_version: judge v3-variants @ 017234562c` |
| 3d | 45 appraisal rows, 10,000 draws | PASS | every score.json: `draws = 10000`, `len(appraisal_rows) = 45` = 3 horizons [30,40,60] × 5 rate cases × 3 population cases |
| 4a | Routed km, not straight | PASS | scoring corridor and cost `spec.yaml` `length_km` = sidecar `length_km`: RJ-A 887.212 (corridor file 844.182), RJ-B 965.029 (889.349), RJ-C1 975.933 (884.109), RJ-C2 967.444 (892.82), RJ-LB 967.389 (874.324); `check.json` `km` equals the same values |
| 4b | Running time = §5 P50 all-stop at class speed | PASS | `inputs/check.json` `ivt_end_to_end_min` = `times.csv` p50_min all-stop: RJ-A 259.1 @300, RJ-B 296.1 @300, RJ-C1 313.6 @300, RJ-C2 301.1 @300, RJ-LB 355.2 @250 (generic factor 1.281) |
| 4c | Cost run identical to `runs/study/rj/costs-s1/<id>/estimate` | PASS | re-compared `cost/rcf/distribution.parquet` (10,000 × 8) element-wise: identical for all five |
| 4d | Judge capex P10/P50/P90 recomputed (numpy `nearest`) vs score.json and §6 (interpolated) | PASS | nearest-draw percentiles reproduce score.json to 0.000 for all 15 cells and base P50; linear percentiles reproduce `costs-s1/capex.csv` (the §6 table) to < 0.5 after rounding; largest judge-vs-§6 gap 4.73 (RJ-LB P90), as §8b states (4.7) |
| 4e | Every relied-on capex/time traces to a routed sidecar + frozen judge | PASS | 4a–4d; `score_corridor` re-run in-process twice gives byte-identical YAML equal to `inputs/<id>.corridor.yaml`; `ivt_check` re-run equals `check.json` (determinism, no writes) |
| 5a | §8a two tables recomputed from score.json | PASS | every cell re-derived (robust NPV, NPV at P50/P90 cost ×3 pops, BCR P10/P50/P90 medium, capex, added trips/pkm vs S1*, sketch load, HHR load and delta vs S1* 11,035,618.9, five-metro 120 gain (C1 93,693 → 0.09 M; LB 109,007 → 0.11 M), national reach gain and level, CO2 PV P50 = appraisal row medium/60/greenbook_2026 `pv_carbon_p50`: 13,648.8 / 11,006.9 / 14,679.4 / 13,985.8 / 11,106.8); rounding correct, including −102,845 (raw −102,845.49) and −99,640 (raw −99,639.52) |
| 5b | §8b table | PASS | matches score.json and capex.csv; gaps 3.0 / 3.8 / 4.5 / 3.9 / 4.7 recomputed |
| 5c | §8c via-Taif table and bullets | PASS | vs RJ-A: NPV −18,507.7 / −15,301.7 / −15,698.4; capex +14,088.6 / +19,079.1 / +21,159.6; trips −0.02 / +0.86 / +1.07 M; loads +0.45 / +1.83 / +3.65 M; pkm fall 380.9 → "381 M"; 37.0 min; RJ-LB +16,613.4, capex −38,444.7, −0.49 M trips; BCR P50 0.18–0.24 |
| 5d | Status-block tables | PASS | identical values to §8a (P50-cost column omitted) and §8b |
| 5e | `scenarios/study/replace-rj-*.yaml` `score:` = `score_record` | PASS | dict equality after removing `run`: True ×5 |
| 5f | `_s1-star/s1_star.json` = `*_S1` fields of every run | PASS | trips 14,447,270.03, pkm 2,537.15, loads, five-metro S1 and national reach S1* equal in all five |
| 6 | Increments vs S1*, never published S1; not tabled beside L1–L5; no published figure changed | PASS | `score_record.increment_vs` = "S1* …, not published S1"; §8 mentions L1–L5 only to say they are not tabled together; `docs/report/`, `docs/r6-l6-connected.md`, `runs/r6/top5`, `runs/r6/l6`, `runs/r7` unchanged (diff + mtimes) |
| 7 | Stacked `rj-*.yaml` and `all-families.yaml` unchanged and unscored | PASS | not in `git diff --stat`; only the five `replace-rj-*.yaml` carry a `score:` key; `rj-a.yaml` label "not scored", `all-families.yaml` note "not scored" |
| 8a | §8 labels, alignment limitation, A-r4-acc-004 sentence, S1* definition, siting language, no vignette, no "will" | PASS | §8 line 310: both labels; "Alignment limitation:" paragraph; the sentence "The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are not rail-graph interchanges." is word-for-word the `docs/r6-l6-connected.md` line 250 sentence, followed by how the placeholders apply to the RJ terminals; S1* defined; "through track … stays outside the Haram boundary"; grep for pilgrim/family/student/worker/commuter in §8 empty; `\bwill\b` in the file appears only inside the two "never 'will'" label lines |
| 8b | §§1–6 changed only by pointers | PASS | `git diff 6291a1c HEAD -- docs/rj-routes-study.md`: header bump v1.1; intro sentence "Later (STUDY_RJ_SCORE…): see section 8"; §7 bullet "(Section 8 now scores them…)"; §7 files list pointer; rest is the appended §8 |
| 9a | Untouched areas | PASS | `find -newer <run start 23:17:56 +03>` = 0 files in `runs/r6/top5`, `runs/r6/l6`, `runs/r7`, `docs/report`, `web`, `api`, `film`, `prompts`, `cities/ksa/{lines,corridors,alignments,alignments-study}`, `access_network.yaml`, `network/graph_params.yaml`, `scenarios/S1.yaml`, `judge`, `docs/licences.*`, `docs/assumptions.md`, `docs/sources/index.csv`; none in the diff stat; `tests/test_study_rj_score.py::test_protected_runs_untouched` and `::test_untouched_areas_since_run_start` pass |
| 9b | A-rj rows local; A-rj-006…009 present with source/assumption and status | PASS | `grep -c "A-rj-" docs/assumptions.md` = 0; `docs/study-rj/assumptions.md` v1.1 adds A-rj-006 (assumed), A-rj-007 (derived; 1,014 rows = 2 × 507 zones; `_skims/skims.json` check_max_abs_diff 0.0 on three keys), A-rj-008 (assumed, 2030 vs 2034), A-rj-009 (assumed) |
| 10a | No process killed that the run did not start | PASS | port 8765: `uvicorn api.main:app --port 8765` PID 75079 started 21:12:05 (before the run's 23:17 start) and still listening; port 8000: nothing listening now and no evidence anything was (no `8000` in any `logs/study-rj-score*`); the only server started was OSRM via the judge copy's `network/osrm.py::server` (free port, `proc.terminate()`/`kill()` on its own child only) |
| 10b | No tag, push, paid API, secrets, home paths | PASS | no tag contains 6291a1c; `git diff 6291a1c HEAD | grep "/Users/"` empty; secrets grep empty; cost estimate names only local judge runs at USD 0; absolute paths exist only in `runs/…/inputs/marker.yaml`, which is gitignored (`.gitignore:7`) |
| 11 | Status block complete | PASS | five-row score table, judge-capex-vs-§6 table, S1* definition, `git diff --stat` evidence (12 files, +1,621/−5 at 1ce6b4e: verified), test count 857, run estimate USD 30–50 (guard 60); decisions 1–6 recorded (gateway skims, terminal placements, test allowance in `tests/test_r8_l6_panel.py` adding `prompts/STUDY_RJ_SCORE.md` to the allowed set, pilot run in `runs/_superseded/study-rj-score-pilot-replace-rj-a-dirty/`, present). "STUDY_RJ_SCORE: done" intentionally absent (added after PASS). Cost-log row: not yet present, as for every earlier milestone it is appended by the coordinator from the run's JSON after the run exits (rows 75–78 precedent); not a FAIL |
| 12 | Judgement calls A-rj-006 / A-rj-007 vs the rules | PASS (see assessment) | below |

## Assessment of the two judgement calls (item 12)
- **A-rj-006 (RJ terminals take the Landbridge's A-r4-acc-004 placements).** The RJ corridor files' terminals are the identical Landbridge placeholders (riyadh 24.638916/46.71601, jeddah 21.550443/39.174236 in both `landbridge.yaml` and `alignments-study/corridors/RJ-*.yaml`). For the Landbridge the access model resolves those placeholders to `access_network.yaml station_sites.landbridge` (24.65/46.741; 21.517643/39.245363). The scoring corridors (`runs/…/inputs/<id>.corridor.yaml`, an adapter input) carry those same two sites with `placeholder_lat/lon` and a `site_override` note; the corridor files, `access_network.yaml`, `landbridge.yaml` and the chainage (km_post 0 … routed km) are unchanged. Rules as written: the access model is not changed (file unchanged, no new override key); no existing or committed station is moved; the inputs go through the adapter. The prompt itself asked to "say how the same Jeddah/Riyadh placeholders apply to the RJ terminals", which §8 and A-rj-006 do. Consistent and disclosed (§8 "Access model" bullet, A-rj-006, status block). Note for the reader: the terminal node sits ~8 km from the routed alignment's end while the chainage is kept, exactly as for the Landbridge under the access model.
- **A-rj-007 (skim rows for gateway SW/NW).** The frozen skim table lacks rows for two stops that exist only in these sketches; without them RJ-C1/C2 could not be scored. The rows were produced with the judge copy's own `access.railgraph skims` method (OSRM /table MLD, car, free flow, same zone points), the frozen 39,039 rows copied unchanged, and three existing stations recomputed with max abs diff 0.0 (`_skims/skims.json`). This extends an input table for new stations; it does not change the access model's formulas, thresholds or any existing row. Disclosed (§8, A-rj-007, status block). Consistent with "do not change the access model" and "supply inputs through the adapter".

## Spot-check (external citations newly used in §8)
Sample = every external source newly relied on in the milestone's text (1 row; no random draw needed): **S-rj-022** (`docs/sources/study-rj.csv` row 13, Arab News, 21 Jan 2026, accessed 6 Nov 2026). WebFetch of https://www.arabnews.com/node/2630157/saudi-arabia on 6 Nov 2026 confirms the quoted sentence "a new railway linking Riyadh and Jeddah is planned to be completed in phases by 2034", attributed to Saudi Railway Co. CEO Bashar Al-Malik, published 21 Jan 2026. Match. C-001 (SR 100 bn / USD 7 bn) is cited only as "not used" and pre-dates this run.

## Determinism
`study.rj score` was not re-run (per the brief). In-process re-runs of `score_corridor(rid, 1)` and `ivt_check(...)` twice for all five sketches gave identical dicts, equal to the committed-run inputs (`inputs/<id>.corridor.yaml`, `check.json`). The judge's cost run reproduces the §6 run draw for draw at seed 1.

## Failures
None.

## Observations (not FAILs)
1. The S1* definition text lists "existing lines (HHR, SAR North, SAR East)"; the actual S1* line set also includes `riyadh-metro` (an existing line in `S1.yaml`). The definition follows the prompt's wording and "existing lines" covers it, but the parenthetical could name Riyadh Metro.
2. `meta.json` stores git describe under `harness_code_version` (judge version under `code_version`), not a key literally named `git_describe`; the value is present and clean.
3. The cost-log row for this run will need appending after the run exits (coordinator step).

## Three most important fixes
None required. If anything: (1) name Riyadh Metro in the S1* parenthetical in §8 and the status block; (2) append the cost-log row after the run; (3) nothing else.

VERDICT: PASS
