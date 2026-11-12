> **Document version:** docs/status/verify-R4.md v1.1 | 1 Nov 2026 | Author: red-team-verifier | Status: verified

# Verification: R4 (network evaluation), branch `r4`

Two passes, both read only; nothing fixed. Brief: `prompts/R4.md` v1.2 (tasks 1–8, Acceptance, the international-visitor section and the CP4 section). Rules: `CLAUDE.md`, `prompts/_common.md`. Builder summary: `docs/status/r4.md`.

- **Pass 1 (v1.0)**: HEAD `b36ea09` (r3-12-gb36ea09), clean tree. One open FAIL (acceptance (e)): the 9 `runs/network-eval/S5/summary.parquet` station-addition rows were single points with NaN opex, NaN uplift and NaN running time, while `docs/network-evaluation.md` and `docs/status/r4.md` claimed P10/P50/P90 capex and opex for every candidate. All other criteria PASS. Two notes: the brief's task-1 command form (`access.running_time --line …`, no `run`) did not execute; the Ramadan/Hajj per-day peak loads are given at the central share only.
- **Pass 2 (v1.1, this version)**: HEAD `54c800c` (r3-13-g54c800c), clean tree. Checks the builder's fix to (e), the brief-form CLI, `make test`, the docs, and that the earlier PASS items survived the change.

## 1. Pass-1 findings, summarised (full evidence in v1.0, commit `54c800c`)

| # | criterion | v1.0 | evidence (short) |
|---|---|---|---|
| A1 | `make test` (ruff, format, pytest, docver, manifest) | PASS | all five green; docver 273 files, manifest 377 rows |
| A2a | Haramain running-time gate ±10 % or departure explained and flagged | PASS (gate FAIL, explained) | `runs/access/running_time/factors-s1/factors.json`: hhr-mj-current −12.2 %, hhr-mj-2018 −40.0 %, `pass: false`; doc §1 states "Gate result: FAIL, departure explained and flagged" (A-r4-rt-007, CP5 item 1) |
| A2b | Isochrones for every CP1 metro, S0, S1 and every candidate; population from R3 zones | PASS | `runs/access/isochrones-summary-s1/reached_all.parquet` 7,722 rows = 11 metros × 78 scenarios; `access/isochrones.py:111,141` read the R3 zones and skims |
| A2c | Commute test: ranges and model language, no "will" | PASS | `grep -nwi will` over the R4 docs empty; 279 pairs × 78 scenarios re-computed |
| A2d | Jeddah coupling: matched-control runs with ids and teleport shares, or pending with estimate and reason | PASS | `runs/coupling/r4_hhr_jeddah_kaia/policy_report.json` seed 1; seeds 2–3 pending with estimate (≈70 min, ≈1.1 GB) and the read-only-checkout reason (CP5 item 7) |
| A2e | Every candidate cost traces to R1c ids and uplifts; `summary.parquet` has P10/P50/P90, never points | **FAIL** | S5: `capex_p10 = capex_p50 = capex_p90`, uplift/opex/running time NaN, unflagged; docs claimed ranges for S2…S5 |
| A3a–e | Pilgrim files + manifest; drop-in airport split + test; conflicts C-r4-intl-001/002 verified against the PDFs; HHR with/without segment vs ±15 %, `validation, not fitted`; Ramadan/Hajj peaks | PASS (A3e note: peaks at the central share only) | `git ls-files data/ksa/tables/pilgrims` = 46; `tests/test_demand_intl.py::test_new_year_row_is_picked_up`; `pdftotext` 5,893,474; `hhr_validation.csv` |
| A4-1…5a | Landbridge artefact fixed; air/bus recalibration (air −29.9 % `uncalibrated`, range not widened, reason stated); 24 created rows with roles and S-r4-roles sources; C-r4-tga-001…010; commute criterion in minutes with Badr 14 → 15 → 17 | PASS | `runs/r4/demand/calibration-r4-s1/calibration.json`; `screening/created_roles_r4.yaml`; `docs/sources/conflicts.md:379–390`; `runs/r4/screening/rank_changes.csv` |
| A5a/b | Spot-check, seed 20261101: 10 of 99 R4 source rows, 5 of 43 assumptions | PASS | 8 verified by WebFetch, 2 labelled unverified in the register and used only for an unscored role; no misquote; all 5 assumptions match YAML and source |
| A6 | Hygiene | PASS | porcelain empty; no `/Users/<x>` in tracked files; secrets grep empty; no `git push`; model ids only in the allowed places; nothing under `runs/`, `movies/`, `film/` |
| A7 | Three rail layers; no planned line as existing | PASS | `layer:` on every line YAML; candidates `hypothetical` |
| A8 | Determinism and run metadata | PASS | byte-identical re-runs; every sampled `meta.json` has seed, config hash, data hash `ad28d605…`, clean code version, label |
| A9 | Licence register for new items | PASS | `docs/licences-r4.csv` 11 rows, all columns; no paid item |
| A10 | Status files and cost log | PASS (pending noted) | status figures match; `R4:` line, `docs/STATUS.md` row and the cost-log row are written at hand-off / INTEGRATE_R4; one wrong claim (see A2e) |

## 2. Pass 2: commands (procedure step 1), HEAD `54c800c`

| command | exit | time | result |
|---|---|---|---|
| `make test` (= ruff check, ruff format --check, pytest -q, docver check, manifest verify) | 0 | 18.9 s | ruff "All checks passed!", 533 files formatted; **417 passed in 17.3 s**; `docver OK: 274 files`; `manifest OK: 377 rows` |
| `uv run python -m access.running_time --line cities/ksa/lines/hhr.yaml --pattern all-stop --seed 1 --out runs/verify-r4/x1` (the brief's form, twice: x1, x2) | 0 / 0 | 0.67 s | runs; `pairs.csv`, `stops.csv`, `validation.json` byte-identical between x1 and x2; `meta.json` identical apart from `created_utc` |
| `… access.running_time run --line … --out runs/verify-r4/x3` | 0 | — | `pairs.csv` identical to the brief-form output (the two forms are the same code path) |
| `uv run python -m access.running_time` (no arguments) / `--help` | 0 / 0 | — | prints help |
| `uv run python -m network.evaluate summary --seed 1` (after copying the builder's four parquets and metas aside) | 0 | 6.6 s | S2/S3/S4/S5 `summary.parquet` identical to the builder's, column by column; `meta.json` identical apart from `created_utc`; `code_version` `r3-13-g54c800c` (clean), seed 1, `data_hash` `ad28d605…`, label present |
| `git status --porcelain` after all runs | — | — | empty (`runs/verify-r4/` is gitignored) |

Diff reviewed: `git diff r3-12-gb36ea09 HEAD --stat` = `access/running_time.py` (+16: a Typer callback that maps the brief's form onto `run`), `network/evaluate.py` (+31/−10: `cost_row` S5 branch and the station-addition case in `summary_cmd`), `docs/network-evaluation.md` (3 lines), `docs/status/r4.md` (1 line), `docs/status/verify-R4.md` (v1.0 added). No register, source, licence, YAML or test file changed, so the pass-1 spot-check sample and the A3–A9 evidence stand unchanged; the pass-1 running-time and HHR re-runs were repeated above and remain identical.

## 3. Pass 2: acceptance (e) re-examined

**What the parquet now holds** (`runs/network-eval/S5/summary.parquet`, 9 rows; read with pandas):

| candidate | host class | base capex P10=P50=P90 | uplifted P10 / P50 / P80 / P90 (SAR m) | opex | added min per through train P10 / P50 / P90 |
|---|---|---|---|---|---|
| al-jubayl, duruma, al-jubayl-royal-commission, ra-s-tannurah (mixed) | intercity_250 | 395.78 | 317.5 / 472.5 / 878.4 / 1,469.7 | NaN + `opex_note` | 4.78 / 5.26 / 8.77 |
| az-zulfi, al-oyun, banban, al-umran (conventional_passenger) | intercity_200 | 395.78 | 317.5 / 472.5 / 878.4 / 1,469.7 | NaN + `opex_note` | 4.60 / 5.07 / 8.44 |
| thuwal (hsr) | hsr_talgo350 | 2,269.01 | 2,068.4 / 2,938.7 / 5,365.1 / 8,698.9 | NaN + `opex_note` | 5.38 / 5.92 / 9.86 |

Columns and text, all nine rows: `run_min_basis` = "added minutes per through train (stop cost of the new station)"; `capex_basis` = "new station only: register station item (zero-spread R1c default, no release use until cleared) x the reference-class capex multiplier draws of the same run"; `opex_note` = "unknown: the R1c register has no per-station operating item and an added stop adds no train-km (the register's opex units)"; `cost_register_ids` = `C-station-sar-north-2012-001` (or `-hsr-intermediate-ksa-002` for Thuwal) + "uplifts as in runs/costs/<id>/rcf/summary.yaml"; `cost_run` = `runs/costs/S5-station_addition-<x>`. S2–S4 (67 rows) carry the same new columns (`capex_uplifted_p10/p90`, `opex_note`, `run_min_basis` = "end-to-end all-stop"), still 0 point rows.

**Independent re-computation.**
- Uplifted quantiles: for each of the 9 rows, `base P50 × runs/costs/<cost_run>/rcf/distribution.parquet.capex_multiplier` (10,000 draws; multiplier P10/P50/P90 0.802 / 1.194 / 3.713 conventional, 0.912 / 1.295 / 3.834 HSR) and `np.percentile` at 10/50/80/90 reproduce `capex_uplifted_*` with a maximum difference of 0.0. The uplift is the run's own reference-class draw (`rcf/summary.yaml`: `U-capex-rail-sobc`, S-cost-rcf-008, A-rcf-001).
- Running time: `run_min_p10/p50/p90 ÷ run_min_kinematic` = 1.164 / 1.281 / 2.134 in every row = the generic timetable factor and its range in `factors.json` (A-r4-rt-011, whose `used_in` lists `network/evaluate.py`). The Thuwal kinematic stop cost, 4.62 min, equals the HHR per-stop cost in `runs/verify-r4/x1/stops.csv` (hsr class, 2.0 min dwell), so the station-addition figure is the same stop-cost model as task 1.
- Base point: `runs/costs/S5-station_addition-al-jubayl/trace.csv` row 7, `station[intermediate]`, `C-station-sar-north-2012-001`, quantity 1, P10 = P50 = P90 = 395.78; the register item itself has `low: 314, high: 314` ("Single arithmetic point (one contract, five stations; per-station split not published)"); Thuwal's `C-station-hsr-intermediate-ksa-002` has `low: 1750, high: 1750` ("Single printed figure, so low = central = high"). The zero spread is the register's, not R4's, and is an open R1c item in `docs/STATUS.md:216,218` ("no release use until cleared").
- Opex "unknown": `cities/ksa/costs/cost_register.yaml` holds 26 `category: opex` items, all per train-km, per route-km (or single-track km) per year, per FTE, per kWh or percentages; none is per station. The cost run's own opex rows are whole-host-line train-km and route-km quantities (trace rows 15–17), which a one-station addition does not change. The claim in `opex_note` is correct.

**Judgement under the rules.** Rule 1 accepts "unknown" when it is stated as such; rule 3 forbids single points as cost figures. In the acceptance artefact every station-addition row now reports a capex **range** (uplifted P10–P90, traced to the register item and to the uplift run), a running-time **band**, an explicit **unknown** for incremental opex with its reason, and the register ids and run ids; the only remaining point is the register's base figure, named as such in the row and already an open, tracked R1c item that R4 does not own (`costs/`, `cities/ksa/costs/`). No guess is presented as fact, no point is presented as a cost estimate. **(e) PASS.**

Residual defects found in pass 2 (none is an acceptance failure; all go to INTEGRATE_R4):
- R1. `docs/network-evaluation.md:267` (the hand-written `<!-- r4:summary -->` table, not generated by code) still prints S5 as "5.4 (5.4–5.4)": the degenerate base range in range notation, two lines after the paragraph that explains the base is a register point. Pass-1 fix 1 asked for this cell to be a flagged point or the uplifted range (4.6 / 6.7 / 20.5 bn summed P10/P50/P90); it was not changed.
- R2. `docs/status/r4.md:61` still reads "P10/P50/P90 capex and opex, uplifted P50/P80" for S2…S5; the correction lives only in the sub-bullet (line 62) and "P50/P80" is now stale (the files carry P10/P50/P80/P90).
- R3. `docs/status/r4.md:62` bands "about SAR 0.32–1.47 bn P10–P90" and "about 4.6–8.8 min" describe the eight conventional/mixed stations; Thuwal (HSR) is 2.07–8.70 bn and 5.4–9.9 min. Say "eight of nine; Thuwal …".
- R4. No test exercises the S5 `cost_row` branch, the station-addition case in `summary_cmd`, or the new `_default` callback (the diff adds no tests; the regression that pass 1 found would still not be caught by `pytest`).
- R5. `docs/network-evaluation.md` and `docs/status/r4.md` stayed at v1.0 after substantive edits (CLAUDE.md source-versioning rule: bump the minor). `docver` passes (format only); all edits are same-day on `Status: draft`, so the header still identifies the text, but INTEGRATE_R4 should bump them.
- R6. The "unknown" incremental station opex and the per-stop × timetable-factor method are stated in the parquet, the doc and the status, not as a register row; `docs/assumptions-r4.md` has no entry for either (no new YAML constant was introduced, so procedure step 6 is met; recorded for completeness).

## 4. Pass 2: the other items

| # | check | verdict | evidence |
|---|---|---|---|
| P2-1 | Brief-form CLI runs and is deterministic | PASS | table in §2; x1 ≡ x2 ≡ `run` form |
| P2-2 | `make test` green at HEAD | PASS | 417 passed; ruff, format, docver 274, manifest 377 |
| P2-3 | Docs and status no longer overclaim | PASS (R1–R3 noted) | `docs/network-evaluation.md:251` now states the base point is a register limitation, the range is the uplifted capex, opex is unknown with the reason, running time is minutes added per through train; `:258` "(station additions: opex unknown, see above)"; `:6` cites the brief's command form. `docs/status/r4.md:62` carries the same. `grep -nwi will` over the five R4 docs still empty |
| P2-4 | Earlier PASS items unbroken | PASS | diff touches no register, source, licence, YAML, test or run input; `summary` re-run reproduces S2–S4 (sums 607,149 / 159,034 / 197,467 SAR m as in the doc table) and S5 identically; running-time and HHR outputs identical to pass 1; hygiene greps re-run empty; porcelain empty |
| P2-5 | Peak loads band (pass-1 note) | unchanged | doc §4 not in the diff; the per-day Ramadan/Hajj loads remain at the central share only (CP5 / INTEGRATE_R4 item) |
| P2-6 | Status lines | as pass 1 | `R4:` line absent before the verdict (expected); `docs/STATUS.md` R4 row "not started" and the cost-log row are written at hand-off / INTEGRATE_R4 |

## 5. Spot-check sample

Unchanged from pass 1 (seed 20261101): sources S-r4-roles-016, S-r4-rt-012, S-r4-rt-015, S-r4-net-008, S-r4-rt-008, S-r4-roles-010, S-r4-rt-006, S-r4-rt-007, S-r4-roles-005, S-r4-rt-029 (8 verified by WebFetch, 2 labelled unverified in the register and used only for an unscored role); assumptions A-r4-acc-006, A-r4-air-001, A-r4-rt-009, A-r4-rt-010, A-intl-005 (all match). The fix added no source, assumption or licence row, so no re-sample was needed. Pass-2 number tracing: the nine S5 rows ↔ `runs/costs/<id>/trace.csv` and `rcf/distribution.parquet`; the factor band ↔ `factors.json`; the status bands ↔ the parquet (with the Thuwal caveat R3).

## 6. Three most important fixes (for INTEGRATE_R4; none blocks the verdict)

1. **Doc §6 table and status line 61–62**: show the S5 cost as the uplifted range (per candidate or summed 4.6 / 6.7 / 20.5 bn P10/P50/P90) with the base marked "register point, R1c open item", replace "uplifted P50/P80" with "P10/P50/P80/P90", and qualify the status bands as eight of nine with Thuwal's 2.07–8.70 bn and 5.4–9.9 min. Bump both documents to v1.1.
2. **Tests**: a fixture test for the station-addition path (`cost_row` S5 branch: uplifted quantiles present and ordered, `opex_note` set; `summary_cmd`: `run_min_*` = stop cost × factor band) and one for the brief-form callback, so the pass-1 regression cannot recur silently.
3. **Peak loads with a band** (carried from pass 1): the per-day Ramadan/Hajj/average loads in doc §4 and the status block should carry the low–high share band like the annual column, since the central share overshoots HHR by 90 % in the builder's own validation.

VERDICT: PASS
