> **Document version:** docs/status/verify-INTEGRATE_R6.md v1.0 | 3 Nov 2026 | Author: red-team-verifier (claude-fable-5-1) | Status: verified (HEAD 2b7c04d)

# Verifier report: INTEGRATE_R6 (merge of track `r6` into `main`)

Read-only audit of `main` at HEAD 2b7c04d against `prompts/INTEGRATE_R6.md` v1.1, the coordinator's four acceptance criteria, `prompts/R6.md` (re-check of the merged state), `CLAUDE.md` and PROJECT.md sections 2, 7 and 9. Nothing was fixed. `git status --porcelain` empty before and after this audit (the README demo writes only to the gitignored `runs/skims/demo/`). Commands run 3 Nov 2026, about 21:35–21:55 Asia/Riyadh, in the main checkout.

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

## 1. Commands

| Command | Exit | Time | Output line |
|---|---|---|---|
| `make test` (ruff check, ruff format --check, pytest -q, docver, manifest) | 0 | 24.4 s | `All checks passed!`; `581 files already formatted`; pytest **473 passed** (473 progress dots, no F/E; `pytest --co` collects 473); `docver OK: 289 files`; `manifest OK: 386 rows` (log `logs/verify-INTEGRATE_R6-maketest.log`) |
| `uv run python -m common.licences check` | 0 | <1 s | `licences: 266 Markdown rows, 266 CSV rows, 0 differ` |
| README demo `uv run python -m network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones.geojson --seed 1 --out runs/skims/demo/` | 0 | 1.6 s (2.5 s on the first temp-dir run) | `nx_dijkstra_jeddah: 6 zones, 36 pairs, 0 unreachable, 6 snaps > 2.0 km (max 104.27 km)`; `meta.json` `code_version` `r5-29-g2b7c04d` (clean) |
| `uv run python -m optimise.judge verify --name v2-p5b` | 0 | 0.7 s | `judge/v2-p5b intact: sha256 2bdee7f587c53ba872cc5fd10a61475496daca76dddab6a1271c103644e592ea` |
| `uv run python -m optimise.judge verify --name v1-r5` | 0 | 0.6 s | `judge/v1-r5 intact: sha256 f20091cfc4854dc6078a9b46c311bd10c04074027a2947062fe8c8e0d9354fd3` |
| `uv run python -m common.scenarios validate` | 0 | <1 s | `ok 11 scenario files` (S0–S5, S6-L1..L5, candidate) |
| `uv run python -m common.cost_log summary` | 0 | <1 s | `TOTAL runs 54 hours 21.16 USD 709.84`; `r6 runs 1 hours 1.42 USD 33.43`; no paid rows |
| Determinism: README demo twice with `--seed 1` into two temp dirs | 0, 0 | — | `diff -rq -x meta.json` empty; `meta.json` identical apart from the timestamp |

## 2. Criteria

| # | Criterion | Result | Evidence |
|---|---|---|---|
| A1 | Every R6 branch merged with `--no-ff`, visible in `git log --merges` | PASS | one R6 branch, `r6` (tip ad29be1, `docs/status/r6.md` last line `R6: done`); `git log --merges` → `1fe457d merge(R6): r6`, parents `2c2bd93 ad29be1` (a true merge commit, not a fast-forward) |
| A2 | No history rewriting: 376e798 is an ancestor of HEAD | PASS | `git merge-base --is-ancestor 376e798 HEAD` → yes; `ad29be1` (r6 tip) is also an ancestor; `git branch --contains r6` lists `main` |
| A3 | Assumptions register is a superset: every `r6:docs/assumptions-r6.md` row on main, ids kept, sorted | PASS | 13 ids `A-r6-001…013` in the fragment, 13 on main; all 13 rows byte-identical (`grep -qxF` on each fragment row: 0 missing/changed); placed in id order between `A-r4-rt-012` (line 501) and `A-rcf-001` (line 515); fragment deleted (`ls docs/assumptions-r*.md` → only the pre-existing `docs/assumptions-r2.md`) |
| A4 | Main's pre-merge assumptions rows all still present and unchanged | PASS | `git show 376e798:docs/assumptions.md`: 712 `| A-` rows, 712 ids; main: 725 rows, 725 ids; `comm -23` of the id sets empty; every one of the 712 pre-merge rows found verbatim on main (0 `CHANGED`); section-2 (main table) count 652 → 665 = STATUS's "665 main-table rows" |
| A5 | Licence register superset (`r6:docs/licences-r6.csv` and pre-merge rows) | PASS | the 3 fragment rows (`HiGHS (MILP, via scipy.optimize.milp) [r6]`, `scipy.stats.spearmanr [r6 use]`, `matplotlib [r6 use]`) found verbatim in `docs/licences.csv` (lines 265–267); all 263 pre-merge CSV rows (`git show 376e798:docs/licences.csv`) found verbatim (0 `CHANGED`); 264 → 267 lines incl. header; `common.licences check` 0 differ; `docs/licences.md` line 284 records the fold; fragments `docs/licences-r6.{md,csv}` deleted. The original `HiGHS | 1.x | planned; unverified` row (csv line 71) is left beside the verified `[r6]` row as disclosed in STATUS (INTEGRATE_R6 decisions): not silently changed |
| A6 | Sources: no silent drop | PASS (n/a) | `git ls-tree r6 docs/sources/ | grep r6` empty: R6 added no `docs/sources/r6*.csv`; `docs/sources/index.*` untouched by b6a2a32 (`git show --stat b6a2a32`: 7 files, all registers, the fragments and `r6_search.yaml`) |
| A7 | `make test` passes on main | PASS | table above: 473 passed (462 → 473 as STATUS says), docver 289 (= 291 on the branch minus the two deleted Markdown fragments), manifest 386 |
| A8 | README demo command runs; deterministic | PASS | table above; two seed-1 runs byte-identical except the `meta.json` timestamp |
| A9 | Judge `v2-p5b` intact (sha256 2bdee7f5…); `v1-r5` intact | PASS | table above; `judge/` holds `README.md` (tracked), `v1-r5`, `v2-p5b`, `_retired-v2-p5b-uncal` (gitignored by `.gitignore` 26–28) |
| A10 | Runs and judge copies on main equal the track's | PASS | `diff -rq .worktrees/r6/runs/r6 runs/r6` (excluding `tmp/`) 0 lines; `diff -rq .worktrees/r6/judge judge` 0 lines; `runs/zones`, `runs/skims/r3-zones`, `runs/skims/r4-stations` 0 differing; `runs/_superseded/INTEGRATE_R6/` holds the 12 replaced files; every `runs/r6/...` path cited in `docs/r6-topology.md` and `docs/status/r6.md` exists on main (the only non-literal reference is the glob `runs/r6/ga/*/info.json`) |
| A11 | `docs/STATUS.md` measured numbers match | PASS | header v1.22, "Last updated 3 Nov 2026 (INTEGRATE_R6 …)"; disk "38 GiB free of 460 GiB" = `df -h ~` 38Gi; cost "709.84 over 54 runs, 21.16 agent-hours … R6 33.43" = `cost_log summary`; row 26: 473 tests ✔, 665 rows ✔, 266 = 266 ✔, 386 manifest ✔, judges intact ✔, demo 2.4 s (mine 1.6–2.5 s) ✔; merge 1fe457d ✔; CHANGELOG has the `## r6` entry with both R6 and INTEGRATE_R6 lines |
| A12 | `docs/STATUS.md` carries every blocker and conflict: the STATUS header conflict, the R6 checkpoint list, verify-R6 O1/O7/O10 | PASS | "INTEGRATE_R6 decisions" (line 200–203) records the header conflict and both-sides resolution, the register fold, the HiGHS double row and the runs replacement; "R6 open items" (lines 277–282) carries the six-item checkpoint decision list, "O1 inclusion-and-phasing front only; O7 A-r6-003 pending; O10 island corridors flagged, not rejected", the 31-of-111 dirty harness metas and the `r5-dirty` zones meta with its byte-identical rebuild, the budget-guard stop and the alignment-sidecar ODbL question; row 25 says R7 needs explicit approval |
| A13 | Handoff artefacts: `docs/status/main.md` INTEGRATE_R6 block, `INTEGRATE_R6: done` line, INTEGRATE_R6 cost-log row | **PENDING** (task order; not a FAIL, as verify-INTEGRATE_R5 A14) | `grep -n INTEGRATE_R6 docs/status/main.md` empty; the file ends at `INTEGRATE_R5: done`; `docs/cost-log.md` has the `r6-R6-try1` row (33.43) but no INTEGRATE_R6 row. STATUS row 26 already points to "`docs/status/main.md` (INTEGRATE_R6 block)" and to this report, so both references are dangling until task 6 is written. The prompt orders the verifier (task 4) before status (5) and handoff (6); the cost-log row is appended by `run_track.sh` at run end |
| B1 | R6 re-check: `scenarios/S6-L1..L5.yaml` present and valid | PASS | `common.scenarios validate` → `ok 11 scenario files`; each S6 file carries the label twice and `layers: [existing, committed, hypothetical]` |
| B2 | Labels, no advocacy wording | PASS | label in `docs/r6-topology.md` line 5, every S6 YAML, `cities/ksa/assumptions/r6_search.yaml` line 3; `grep -rniE "will (reduce|transform|cut|save|increase)|should build|must build"` over `docs/r6-topology.md`, `docs/r6/`, `scenarios/S6-L*.yaml`: empty |
| B3 | No absolute home paths, no secrets, no `git push` in scripts, nothing tracked under `data/`, `runs/`, `movies/`, `film/renders`, `film/audio`, `judge/` | PASS | `git ls-files -z | xargs -0 grep -ln "/Users/[a-z]"` empty; secret-pattern grep (`sk-ant-`, `AKIA…`, `ghp_…`, `ANTHROPIC_API_KEY=`) empty; `git push` appears only in `CLAUDE.md`, `PROJECT.md`, the verifier agent file and earlier verifier reports (the rule text, never a command in `scripts/`, `Makefile`, `orchestrate.sh`, `run_track.sh`, `optimise/`, `logs/`); `git ls-files runs/ movies/ film/renders film/audio judge/` → only `judge/README.md`; `data/` holds only the pre-R6 GASTAT/pilgrim tables with READMEs |
| B4 | No model names or content from the author's company in R6-added public-facing docs | PASS | `grep -rniE "fable|opus|haiku|claude-"` over `docs/r6-topology.md`, `docs/r6/`, `scenarios/S6-L*.yaml`: empty; the only hits in the wider tree are pre-R6 (`README.md:54` uses Tariq's labels only and says ids are never cited; `docs/licences.md:11` is the R0 register row, see O5) |
| B5 | `common/cost_log.py` has `add-paid` with tests | PASS | `common/cost_log.py:305` `@app.command("add-paid")`, `PAID_ALERT_SHARE = 0.8` (line 52), `ALERT: … % of approved USD` (line 330); `tests/test_cost_log.py:147` `test_add_paid_logs_rows_and_alerts_at_80_percent`, `:168` `test_summary_reports_paid_apart_from_claude_runs`; `README.md:9` documents the command |
| B6 | Three rail layers kept apart; planned lines never "existing" | PASS | S6 YAMLs declare the three layers and the hypothetical layer for the R6 corridors; `docs/r6-topology.md` §0 states the front is inclusion-and-phasing only; maps (`runs/r6/top5/L*-map.png`) carry the ODbL credit and the label (checked at verify-R6, files byte-identical on main per A10) |

## 3. Failures

None. Every acceptance criterion the coordinator listed (1–4) passes on the measured state; A13 is pending by task order and is the condition on this verdict (see §6).

## 4. Observations (not failures)

- O1. **Dangling references until task 6 is done.** `docs/STATUS.md` row 26 cites "`docs/status/main.md` (INTEGRATE_R6 block)" and `docs/status/verify-INTEGRATE_R6.md`; the first does not exist yet and the second is this file. The builder must write the block (merged branch `r6` at ad29be1, merge 1fe457d, the header conflict and its resolution, this verdict, 473 tests in 24.4 s, README demo 1.6–2.5 s, disk 38 GiB) and end it with `INTEGRATE_R6: done` before the coordinator tags `r6`; the coordinator should confirm the INTEGRATE_R6 cost-log row before tagging.
- O2. `runs/zones/meta.json`, `runs/skims/r3-zones/meta.json` and `runs/skims/r4-stations/meta.json` on main record `code_version: r5-dirty` (the P5b split outputs built before commit db1427c). STATUS carries it with the byte-identical clean rebuild (`runs/r6/p5b/zones-rebuild/`); acceptable, but these three metas remain the only live run records with a dirty code version on the judge's input path.
- O3. `docs/assumptions.md` has pre-existing out-of-order rows (`A-najran-osm-001`, `A-najran-pop-001`, `A-najran-terrain-001` and one more, `sort | diff` lines 395–397, 427) in the region-tagged section; not R6 and not changed by this integration. The A-r6 rows themselves are in order.
- O4. `docs/assumptions-r2.md` is still in the tree (noted at INTEGRATE_R5; pre-existing).
- O5. `docs/licences.md` line 11 / `docs/licences.csv` (R0 row "Claude Code / claude-fable-5-1, claude-opus-5-5, claude-haiku-5-5") carries the exact model ids, while `CLAUDE.md` says the mapping lives only in `CLAUDE.md`, the agent files and `docs/cost-log.md`. Pre-R6 and passed by every earlier verifier; raised for the coordinator because `docs/licences.md` is part of the public release set.
- O6. The HiGHS "1.x | planned; unverified" row (csv line 71) now sits beside the verified `[r6]` row (line 265) and the `[r4a]` LP row (line 251). Disclosed in STATUS as deliberate; mark the R0 row superseded at its next touch so the register does not read as three HiGHS items.
- O7. `docs/r6-topology.md` and `docs/status/r6.md` headers still say `Status: draft` after the R6 PASS and the merge (docver accepts it); bump to `reviewed`/`verified` at the next touch.
- O8. STATUS row 26 quotes the README demo at 2.4 s; this audit measured 2.5 s cold and 1.6 s warm. Same order, no issue.

## 5. Spot-check sample (seed 20261103)

R6 added no external sources, cost-register rows or benchmark rows, so the 10 % sample was drawn (Python `random.seed(20261103)`, `random.sample`, 2 of 16) from the 13 merged `A-r6-*` rows plus the 3 merged licence rows:

| Row | Claim | Re-verified against | Result |
|---|---|---|---|
| A-r6-003 | B1/B2/B3 = SAR 100,000 / 250,000 / 500,000 m = "1x / 2.5x / 5x the S1 committed programme's P50 uplifted capex (101,508 SAR m, `runs/costs/S1-*/rcf/summary.yaml`)" | `capex.uplifted.P50` in `runs/costs/S1-{gcc-railway-ksa,landbridge,riyadh-rail-link}/rcf/summary.yaml` = 41,512.2 + 55,857.7 + 4,138.1 = **101,508.0**; ×2.5 = 253,770, ×5 = 507,540; `cities/ksa/assumptions/r6_search.yaml` lines 9–11 set 100,000 / 250,000 / 500,000 with "about" and cite A-r6-003; status `assumed`, approval pending (checkpoint item 2) | PASS (rounded levels, labelled "about"; the anchor figure reproduces exactly) |
| `matplotlib [r6 use]` | version 3.11.2, `https://pypi.org/project/matplotlib/3.11.2/`, "Matplotlib licence (PSF-based)", open Y, commercial Y | WebFetch of the PyPI page: version 3.11.2, licence "Python Software Foundation License (License agreement for matplotlib versions 1.3.0 and later)", classifier OSI Approved; `uv.lock` pins 3.11.2; `uv run python -c "import matplotlib"` reports 3.11.2 (scipy 1.18.1 likewise matches the `[r6]` HiGHS and spearmanr rows) | PASS |

No fabricated or misquoted figure found.

## 6. Three most important fixes

1. Write the INTEGRATE_R6 block in `docs/status/main.md` and end it with `INTEGRATE_R6: done` (O1); confirm the INTEGRATE_R6 cost-log row lands before the `r6` tag.
2. At the next register touch, mark the R0 `HiGHS | 1.x | planned; unverified` row superseded by the `[r6]` row (O6) and decide whether the R0 Claude row in `docs/licences.md` should carry Tariq's labels instead of the exact model ids before any public release (O5).
3. Carry O2 (three `r5-dirty` run metas on the judge input path) into the R6 checkpoint note so Tariq sees it next to the byte-identical rebuild evidence; optionally re-run `runs/zones` and the two skims from a clean commit so the live metas are clean.

VERDICT: PASS
