> **Document version:** docs/status/verify-R8.md v1.1 | 4 Nov 2026 | Author: red-team-verifier (claude-fable-5-1; read-only; v1.1: pass 2 on HEAD 0509009) | Status: reviewed

# verify-R8 — final deliverables (worktree `r8`, HEAD c97f724, pass 1)

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

Scope: `prompts/R8.md` tasks 1–8 and acceptance list, the "R7-checkpoint answers" (v1.1 in the worktree; the coordinator's v1.2 on `main` corrects answer 2: Arabic drafted natively in-session, no local model required, no external API), PROJECT.md §2 and §9 (R8), `docs/status/r8.md`, the four handoff notes under `logs/`. Nothing was edited except this file.

## 1. Commands run (4 Nov 2026)

| command | result | time |
|---|---|---|
| `make test` (ruff check, ruff format --check, pytest, docver, manifest) | exit 0; ruff "All checks passed!"; **658 passed**; `docver OK: 336 files`; `manifest OK: 386 rows` | 33.1 s (pytest 29.8 s) |
| `uv run python -m common.report check` | `report check: PASS` | < 2 s |
| `uv run python -m common.sources bilingual-check docs/executive-summary.en.md docs/executive-summary.ar.md` | `bilingual-check PASS: 248 numeric tokens in …en.md, 248 in …ar.md; equal` | < 2 s |
| `grep -rn -i "claude\|opus\|haiku\|fable" docs/report docs/policy-brief.md docs/executive-summary.*` | empty (exit 1) | — |
| `uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/` then `uv run python -m common.report build`, then `git status --porcelain` | both exit 0; **git status empty**: rebuild is byte-identical (no `git restore` needed) | 10.1 s + 0.9 s |
| `cd web && npx tsc --noEmit` | exit 0 (strict) | 1.8 s |
| `uv run pytest tests/test_api_dashboard.py tests/test_report_*.py` | 151 passed | 5.8 s |
| `git status --porcelain` at start and end | clean | — |

Determinism (step 3): the report and figure pipelines are the smallest relevant CLIs for this milestone (no `--seed` CLI run is new in R8); two consecutive builds produced identical tracked files (see above). The handoff states the figure build takes `--seed` (default 1) for the benchmark strip jitter only.

## 2. Criteria table

| # | criterion (prompt acceptance + PROJECT.md §9 R8 + verifier procedure) | PASS/FAIL | evidence |
|---|---|---|---|
| C1 | Every number in the report, brief and summaries traces to a source id, assumption id or run id | **FAIL** (F2, F3) | 30 numbers traced (§4 below) all match their run files; but the report states construction starts of 2030/2050 where the register, the figure and the brief say 2027/2047 (F2), and five figure captions cite run ids that are not the figure's sources (F3) |
| C2 | Every figure generated from run outputs; none hand-drawn | PASS | `common/figures.py` reads run files; only numeric literal in result text is the handoff note string at lines 1794–1800 (tested against `runs/r6/top5/L1/score.json` by `tests/test_report_figures.py`); rebuild byte-identical |
| C3 | The two executive summaries pass the digit-by-digit bilingual check | PASS | 248 = 248 tokens; Arabic reads as native MSA with the same structure and facts, Western digits; L1 risk statement present in every Arabic block that names S6-L1 |
| C4 | Every map shows the layer legend and the OSM credit | PASS | SVG grep: fig01 and fig12 carry `OpenStreetMap` (3 each) and the four-layer legend ("committed / under procurement (announced/planned)"); dashboard `MapView.tsx` lines 76–78 (custom attribution, never compact) and 270–299 (Legend with the four layers and credit); `dashboard-map.png` viewed: legend, "© OpenStreetMap contributors | OpenFreeMap © OpenMapTiles", footer labels |
| C5 | Every modelled result carries the synthetic label and ranges | PASS | all 15 SVGs: synthetic label ×2, judge hash ×2; `ALIGNMENT_LIMITATION` on the 13 figures with a length/cost/time/ridership (fig02, fig03 are counts); `report check` label rule PASS; `tests/test_report_labels.py` on report, sections, brief, both summaries; dashboard footer from `/api/meta` (`Footer.tsx`), API envelope `api/contract.py:55`; cost and benefit figures are P10/P50/P90 throughout (single modelled values are reach and 2050 trips, labelled deterministic / medium) |
| C6 | No model names in report, brief, summaries | PASS | grep empty; `opus4.kobv.de` URLs masked with a character reference in the generated annexes (declared in each annex header) |
| C7 | No content from the author's company | PASS | `grep -rli insurance` over R8 deliverables hits only A-cost-301 ("social insurance"), A-mode-023 ("insurance … not perceived per trip") and S-fund-247 ("Ping An Insurance"): unrelated |
| C8 | No advocacy; non-partisan | PASS | §0.1, §0.5, §7 and the brief state "options and evidence", "not an endorsement"; delivery model written as "the R7 analysis names … (analyst's judgement)"; S1 reading in §4.1 is framed as uncounted benefits, not advocacy |
| C9 | No "will" in result statements | PASS | `grep -n "\bwill\b"` on sections 01–07, brief, EN summary: empty; one hit in `feasibility-report.md` inside the quoted claim of `[^S-soc-017]` (GASTAT table caption, source text) |
| C10 | Dashboard builds and serves locally with fixture data; API tests pass | PASS | `web/dist/` present, `web/node_modules` present, `make dashboard` target (Makefile 42–45), `tsc --noEmit` clean, 35 API tests in the 151; five screenshots in `docs/report/figures/dashboard-*.png` (< 1.5 MB each) |
| C11 | `docs/licences-release.md` lists every register item with compatibility status and every conflict | PASS | generated table of 289 rows (268 `licences.csv` + fragments); B1–B9 each a named blocker with its question (MoF table, PFRAM, UNESCO CC BY-SA, IMF WEO, CE Delft, Wikipedia air routes, ODbL on `alignments/` and `alignments-v2/`, model ids in the R0 row, Nabrah); Google Chrome flagged "approval pending", not resolved; `tests/test_report_release.py` checks every row is in the note; `common.licences check`: 268 = 268, 0 differ |
| C12 | Framing: L2 central, L1 upside with its P90 risk statement wherever L1 appears, L3 reach, all vs S1; L4/L5 trade-off illustrations only | PASS | §0.4, §1.2, §4.4–4.6, §7, brief §1/§3, both summaries; `report check` rule "S6-L1 risk statement in every block naming S6-L1" and "S6-L4/L5 only within 3 lines of fig07/fig08" PASS; fig07/fig08 SVG text "trade-off illustration only: no recommendation"; dashboard: "S6-L4 and S6-L5 appear only in the Pareto explorer (trade-off illustration only)" and `/api/difference` 409 for them |
| C13 | v1 alignment weights in headlines, v2 only in the risks sensitivity | PASS | SVG grep for `alignments-v2|top5-v2|r7-v2|weights v2`: 0 hits in all 15; v2 only in §6.4 (`runs/r7-v2/sensitivity.json`: L1 11,022.9 → 11,297.3; L3 2,426.5 → 3,179.9 verified) and brief §8 |
| C14 | The 13 legal items as open questions, no legal position inferred | PASS | §6.5 generated table (13 rows, each a question with sources); brief §7 lists all 13; both summaries give the count and pointer |
| C15 | Labels: `ALIGNMENT_LIMITATION` + synthetic label beside every length/cost/time/ridership table, figure, section; dashboard footer | PASS | `tests/test_report_labels.py` + `report check` label rule; every `gen` block and figure in sections 01–07 carries both; `Footer.tsx` prints both from `/api/meta` |
| C16 | Coverage: 13/13 regions, 150 governorates reconciled | PASS | `docs/report/annex-regions/` 13 files; fig03 keys 13 regions / 150 governorates (`docs/coverage.md` reconciliation); §1.1, §2 Q1 |
| C17 | Benchmarks: every W5 country named | PASS | §5 names France, Japan, Spain, Germany, China, South Korea, Italy, Morocco, Turkey, UAE, Egypt, California HSR, HS2 (grep counts ≥ 2 each) |
| C18 | Assumptions register complete; ranges where required | PASS | annex-assumptions 754 rows = register 754 rows (0 missing either way); 75-row random sample identical to the register |
| C19 | Spot-check (10 %) of the source and assumption annexes | PASS | seed 8: 207 of 2,077 source rows and 75 of 754 assumption rows compared programmatically to `docs/sources/index.csv` / `docs/assumptions*.md` (0 mismatches beyond the declared `opus4.kobv.de` masking); 6 cited sources re-verified on the web (§5 below), all match |
| C20 | CBA double counting; planned lines never styled existing; matched baselines; departures stated | PASS | §3 "generated no-double-counting matrix (`docs/cba.md` §5)", WEIs excluded from every score, land value uplift "a capture potential, not a benefit", Jeddah decongestion zero; committed lines "announced/planned" with source and date in §0.1, brief §2, summaries; every table names its baseline (S1 vs S0; layouts vs S1); departures listed in §3 |
| C21 | Hygiene: tracked files under `data/`, `runs/`, `movies/`, `film/renders/`, `film/audio/`; home paths; secrets; `git push` | PASS | `git ls-files` under those paths = the previously accepted small GASTAT/pilgrim tables with READMEs only; `grep -rn "/Users/[a-z]"` over tracked files: empty; secrets greps: empty; `git push` in scripts/logs: none |
| C22 | verify-R7 closures O7/O8/O10/O11/O17 listed in `docs/status/r8.md` with commits | PASS | five lines with commits 9acb317, 7c5bf07, 891dfd7 (all on the branch: `git log main..r8`); `runs/r7/vfm/vfm.json` shows `sourcing` ∈ {assumption, reference_class}; `tests/test_report_r8_closures.py` in the suite |
| C23 | Report build reproducible; a changed source row changes the appendix | PASS | byte-identical rebuild; `tests/test_report_build.py` (8 tests) incl. `test_committed_report_matches_a_fresh_build` |
| C24 | Arabic drafting rule (prompt v1.2) and model policy: no paid model or API, no keys | PASS | handoffs: "no local-model A-side exists", "No paid model was requested or used"; no `.env` or key tracked; v1.2 removes the open-model draft requirement (O1) |
| C25 | STATUS and status files: milestone label line present; status block; CP6 package list in `docs/STATUS.md`; cost-log row | **FAIL** (F1) | `docs/status/r8.md` v0.1 is "(in progress)" with only the setup and closure lines; no `R8: done` / `R8: blocked` line; `docs/STATUS.md:32` still "R8 \| Final deliverables \| not started \| —"; no CP6 package list; `docs/cost-log.md` last row is `main-FIX_R7-try1` |
| C26 | Tone and scope: no logos, no vendor endorsement, no Claude labels in public-facing documents | PASS | see C6–C8; dashboard title "KSA Rail Twin: decision dashboard" |

## 3. Failures (exact evidence)

**F1. Milestone handoff not written (task 8; criterion 12).** `docs/status/r8.md` (v0.1, "## R8 — 4 Nov 2026 (in progress)") has no status block (report sections, figure count, dashboard build status, bilingual result, release-note conflicts) and no closing `R8: done` or `R8: blocked - <reason>` line, which the orchestrator greps for. `docs/STATUS.md` line 32: `| R8 | Final deliverables | not started | — |`; no "CP6 package list" section (prompt task 8: "Write the CP6 package list into docs/STATUS.md"). `docs/cost-log.md` has no row for the R8 run (last row `2026-11-04 | main-FIX_R7-try1`). The deliverables exist and test green, but the milestone is not handed off.

**F2. "Construction start" contradicts the register, the figure and the brief (number tracing, C1).** The report writes the optimiser's phase years as construction starts: `docs/report/sections/00-front-matter.md` §0.4 "S6-L1 (S6-L2 plus the Al-Kharj spur, **construction start 2050**)"; `04-results.md` §4.4 row "corridors (construction start) | … (2030); Duruma station (2050)"; `07-phased-programme.md` §7 "The construction starts (2030, 2050) are the optimiser's phases (A-r6-002)" and the gate rows "G1 … construction start 2030", "G2 … construction start 2050", "G3 … construction start 2050". The register says the opposite: `A-r6-002` "construction start of a phase = phase year − 3 (2030 → 2027, …, 2050 → 2047)"; `optimise/layout.py:55` `START_LAG = 3`; `fig09-stage-gates` draws construction windows 2027–2030 and 2047–2050 with "gate 2027" / "gate 2047" (viewed; subtitle "bar = construction window (phase − 3 … phase − 1, A-r6-002)"); `docs/policy-brief.md` §6 "a stage gate before construction (2047 for the 2050 phase, A-r6-002)"; `runs/r7/fiscal/fiscal.json` S6-L1 `timing_p50_5y` puts the spur's capex in 2046–2050. A decision-facing date is stated with the wrong meaning in three report sections and disagrees with the report's own Figure 9.

**F3. Figure captions and source lines in the report do not describe the figures that were generated (C1, C2 tracing).** Compared the section captions with the rendered PNG/SVG text and `figures-index.csv`:
- Figure 4 (`04-results.md`): caption source "runs/r6/v3/library/<id>/score.json; judge v3" — the figure's footer and index: `runs/cba/CBA-S2..S5-*/results.json (73 cases)` (R5 CBA, before the CP6 zone split).
- Figure 9 (`07-phased-programme.md`): caption "Stage-gates: G0 evidence, G1 …, G2 …, G3 …, and the reach alternative R, with what must be true at each" — the figure shows construction windows, planned openings and the two gate years only; no G0/R and no conditions.
- Figure 12 (`04-results.md`): caption "Commute-shed isochrones (30 / 45 / 60 door-to-door minutes) around the five metros under S1 and the CP7 layouts"; source "runs/access/ (R4 rail graph, summer factor A-access-011)" — the figure (viewed) is Jeddah S0 vs S1 and Dammam–Khobar–Dhahran S1 vs S1 + Dhahran station at 120 and 90 minutes, from four named `isochrone_door_to_door.geojson` files.
- Figure 14 (`06-risks.md`): caption "… for the CP7 corridors" — the figure shows S1 and the Al-Kharj spur only.
- Figure 15 (`04-results.md`): caption "Capex ranges … by corridor and family", source "runs/r6/v3/library/<id>/score.json; cost runs runs/costs/" — the figure is S1 and the three CP7 layouts from `runs/cba/CBA-S1-committed-programme/draws.parquet` and `runs/r6/top5/top5.csv`.
- Figure 13 (`05-benchmarks.md`): source "CP7 corridors from runs/r6/v3/library/ and runs/r7/corridors/" — the index lists `runs/r7/fiscal/fiscal.json` and the two corridor YAMLs.
- In addition, the rendered `fig09-stage-gates.png` (report and deck) cuts the mandated S6-L1 statement at the right edge: the subtitle ends "… -2,958 / -724 / 1,631 SA" (the SVG string is complete but overflows the canvas), so the required statement is not legible on that figure.
The figures themselves are correct and traced (§4); the report text pointing at them is not. `report check` does not compare captions with `figures-index.csv`, so this passed the builder's own gate.

## 4. Number tracing (30 numbers, all verified against the run files unless marked)

| # | statement (where) | value in document | run / register value |
|---|---|---|---|
| 1 | S6-L1 NPV at P90 cost low/medium/high (everywhere L1 appears) | −2,958 / −724 / +1,631 | `top5.csv` npv_p90cost_* −2,957.61 / −723.93 / 1,630.85; `L1/score.json` npv_at_p90_cost identical |
| 2 | S6-L2 NPV at P90 cost | 3,986 / 4,771 / 5,589 | 3,986.41 / 4,771.25 / 5,589.37 |
| 3 | S6-L3 NPV at P90 cost | −21,745 / −19,225 / −16,624 | −21,744.87 / −19,224.97 / −16,624.23 |
| 4 | robust NPV L2 / L1 / L3 | 6,792 / 11,023 / 2,427 | 6,791.61 / 11,022.94 / 2,426.50 |
| 5 | capex P10/P50/P90 L2 | 801 / 1,423 / 5,286 | 800.59 / 1,423.07 / 5,286.11 |
| 6 | capex L1 | 6,233 / 11,194 / 41,304 | 6,233.18 / 11,194.20 / 41,304.41 |
| 7 | capex L3 | 10,684 / 19,630 / 73,799 | 10,683.54 / 19,630.11 / 73,798.60 |
| 8 | BCR medium L2 / L1 / L3 | 1.52/5.96/22.23; 0.60/2.33/9.33; 0.32/1.12/3.48 | bcr_p10/p50/p90_medium match to 2 dp |
| 9 | NPV draws P10/P50/P90 medium L2 / L1 / L3 | 1,051/7,053/18,604; −5,243/11,301/40,819; −20,113/2,215/34,873 | npv_draws_* match |
| 10 | L1 − L2 (spur share); L1 − L3; SAR/person (brief) | 4,231; 8,596; ≈ 12,600 | 4,231.33; 8,596.43; 12,584 |
| 11 | reach gain 120 min L2 / L1 / L3 / L4 / L5 | 3.56 / 3.56 / 4.25 / 4.67 / 5.30 M | 3,563,760 / 3,563,760 / 4,246,882 / 4,674,103 / 5,298,080 |
| 12 | L4 / L5 robust NPV; L5 capex P50 | −7,934 / −112,565; 98,170 | −7,933.73 / −112,564.92; 98,169.68 |
| 13 | reach front cost vs L1 (§1.2) | SAR 123.6 bn | L5 − L1 = −123,587.85 |
| 14 | added rail trips 2050 L2 / L1 / L3 | 1.78 / 4.29 / 4.85 M | 1,780,993 / 4,292,013 / 4,847,648 |
| 15 | 30 y / 40 y / flat 5 % / flat 7 % NPV (§4.4, brief §5) | L2 4,035/5,307; 3,225/1,535; L1 6,227/8,020; 3,503/946; L3 −46/367; −716/−1,433 | sens_* columns match |
| 16 | WEI PV P50 medium L2 / L1 / L3 | 114,628 / 142,741 / 267,682 | pv_wei_indicative_medium match |
| 17 | national reach S1 26.10 M of 35.93 M; gain 0.15 / 0.57 M | §4.6 | `national_reach.json` S1 120 = 26,096,670; population 35,927,621; gains 152,514 / 569,212 |
| 18 | S1 vs S0 NPV / BCR by population case (§4.1 table, brief §2, summaries) | −337,555/−60,103/11,607; 0.07/0.31/1.26 (medium); low and high rows | `CBA-S1-committed-programme/results.json` rows horizon 60, greenbook_2026: match |
| 19 | S1 fiscal cost low/medium/high | 46,359/99,309/413,986; 45,021/98,408/412,441; 43,770/97,461/410,092 | results.json fiscal_cost; `fiscal.json` baseline_s1 `un_wpp_low|60` identical |
| 20 | net fiscal cost 60 y fully public L2 / L1 / L3 (+ expected) | 695/1,283/4,088 (2,171); 4,676/8,441/23,615 (13,177); 12,696/18,962/45,343 (27,275) | `fiscal.json` net_fiscal_cost_60y match |
| 21 | availability PPP and demand-risk rows; contingent liabilities 4,859 / 14,611; spur 3,963 / 11,921 | §4.5, §6.3, brief §4 | fiscal.json: 2,166/2,166/4,866; 13,443/13,443/28,054; 8,409/…; 4,858.78 / 14,611.50; spur 3,963 / 11,921 |
| 22 | peak budget share P50 / P90 (year) | 0.024 % / 0.091 % (2027); 0.179 % / 0.662 % (2047); 0.327 % / 1.230 % (2047) | fiscal.json budget_share central peak_pct match |
| 23 | fare cover (PV fares ÷ PV opex+renewals) L2 / L1 / L3 | 0.46 / 0.41 / 0.19 | fiscal.json `fare_over_opex_60y` un_wpp_low 0.4625 / 0.4096 / 0.1927 |
| 24 | VfM L2 / L1 / L3 (% PSC); flat 5 % / sovereign | −894 (−41.2 %) / −5,124 (−38.9 %) / −8,779 (−32.2 %); −366/−705, −1,563/−3,596, −2,591/−6,091 | `vfm.json` central and rate_sensitivity match; corridor rows (−4,230, −3,860, −344, −344, −205) match |
| 25 | VfM switching values L1 (brief §4) | −0.81 / −0.018 / −0.77 | bid_contingency −0.8077; private_finance_premium −0.0181; transaction_cost −0.773 |
| 26 | switching values S1 / spur / Duruma / Dhahran / Al Jubayl / belt 225 | 163 %, 0.26, 8.94, 0.27 %; 66 %, 1.09, 0.85, 3.03 %; 52 %, 1.46, 0.72, 4.02 %; 17 %, 5.43, n/a, 10.37 %; 6 %, 15.29, 18.69 %; 422 % | `switching_values.json` of each case: match |
| 27 | tornado swings S1 capex 333,630; spur ridership 24,528, capex 24,264, VoT 6,400 | §6.1, brief §5 | `tornado.csv` swing_npv 333,630.0; 24,527.7; 24,264.4; 6,399.7 |
| 28 | corridor standalone capex and NPV at P90 cost (§4.3, §7) | 267/474/1,762; 5,433/9,771/36,018; 4,717/8,910/34,256; −121/−30/61; −6,870/−5,419/−3,866 | fiscal.json corridors basis match |
| 29 | families at 2030 (§1.2, §4.2); variants (§4.2); non-electrified spur (§4.4) | −957,580 on 761,974; −308,853/248,441; −405,554/203,343; −1,174/6,745; +19,758 → −47,603; −2,008 and 10,648 | `runs/r6/compare/S2..S5/score.json`; `docs/r6-topology.md` §0.2 line 52; `cp7.csv` row 5 (−2,007.72; 10,647.65) |
| 30 | funnel 7,371 / 1,224 / 198 / 60 / 150 governorates; 71 searchable | fig02, §1.1 | settlements.parquet 7,371; candidates.parquet 1,224; `runs/r2/score/summary.json` n_long 198, n_short 60; coverage 150; 73 base − 2 retired |

Register rows checked: A-r6-002 (construction start = phase − 3), A-rcf-001 (P90 3.69 via P95 4.19 class), A-rcf-029 (P50 0.70), A-fund-108, A-r6-003 (B1 100,000; S1 P50 101,508), A-cba-313, A-r6-105, A-align-100: all present with source or assumption and status.

## 5. Spot-check sample (seed 8) and web re-verification

- `docs/report/annex-sources.md`: 2,077 rows = `docs/sources/index.csv` 2,077 ids (none missing either way); 207 sampled rows: url, publisher and accessed date present verbatim in the annex row (2 "mismatches" are the declared `opus4.kobv.de` character-reference masking).
- `docs/report/annex-assumptions.md`: 754 rows = register; 75 sampled rows byte-identical.
- Web re-verification (6 sources cited in the brief, summaries and §1.5/§5): S-bench-fr-086 "all audited high-speed lines had cost overruns of more than 25 % (Table 5)" (ECA SR 19/2018 para 53, PDF text) MATCH; S-bench-st-014 "no clear regeneration effects from 15 of the 18 stations" (para 77) MATCH; S-fund-r7-001 NAO HC 718 para 1.17 "2% to 3.75% above the cost of government gilts", "between 2% and 4%", "more than 5%" MATCH; S-fund-265 Wikipedia Haramain: slated 2012, inaugurated 25 Sep 2018, opened 11 Oct 2018, 6.97 M (2023), 60 M/yr projected, US$9.4 bn MATCH ("about an eighth" = 6.97/60 = 0.116); S-bench-kr-009 "actual ridership rates have been approximately half those originally estimated" MATCH; S-soc-029 datasaudi Umrah 2025 internal 25,055,083 (total 43,088,121) MATCH. No fabricated or misquoted figure found.

## 6. Observations (not FAILs; record or fix at the coordinator's discretion)

1. `prompts/R8.md` in the worktree is v1.1; `main` carries v1.2 (Arabic drafted natively in-session; no local model required; no external API). The three handoffs flag "no local-model A-side" against v1.1; v1.2 removes that requirement. Record the v1.2 basis in the R8 status block.
2. Ridership reference-class ratio: the report says "P50 0.70, A-rcf-029" (§1.4, §3, §5.3, §6.2); the brief §5 says "median about 0.69, A-rcf-029". A-rcf-029 is 0.70; 0.693 is `central_ridership_ratio` in every `switching_values.json`. Use one figure with its right source.
3. S6-L3 robust NPV is printed 2,427 in §4.4/§7 and 2,426 in §1.4 and §6.4 (file value 2,426.5). One rounding.
4. `docs/delivery-models.md:353` prints 14,612 for the L1 availability-PPP contingent liability at P90; `fiscal.json` 14,611.50 (printed 14,611 in the report, brief and `docs/fiscal-exposure.md`). R7 document, not R8-owned.
5. O11 closure wording in `docs/status/r8.md`: "`depends_on_unsourced` counts every driver not sourced for Saudi Arabia" does not match `funding/vfm.py:116` (it lists only drivers whose switch lies within range and are unsourced; it is `[]` for every entity because no driver switches in range); `not_sourced_for_ksa` (line 117) is the list that names the premium. The code change is fine; the status sentence is not.
6. Licence release note: the heuristic grades the generic "UN World Population Prospects", "GHSL" and "WorldPop" rows NOT IN RELEASE (superseded by the versioned rows 158/212/226) without saying so; the generated row 1 masks the model ids ("[model ids: see docs/licences.md]") while `licences.csv` row 2 still names them (B8 stays open, as intended). Google Chrome remains "approval pending" (correct: flagged, not resolved).
7. `docs/r6-topology.md:112` still reads "in-session Claude turns" (INTEGRATE_R7 open item "reword before R8", owner R8/coordinator). Outside the R8 grep set, so C6 passes; still open.
8. fig14 footer prints "judge v3 d9fef643… · seed 1" on an R5-CBA figure (its note says R5); the brief's "named on every figure" rule is met but the pairing is odd. fig12: Dammam S1 counts 72,170 people within 120 min against 3,113,662 with the Dhahran station (run files, R4/R5); a reader will ask why: explain in the caption.
9. Dashboard legend reads "committed/under procurement" without "(announced/planned)" (figures and API carry it); difference mode has S1 per-line values for three lines only (handoff item 7); `tests/fixtures/README.md` still says every fixture value is invented while `tests/fixtures/api/` holds trimmed real run outputs (own README says so; top README not updated).
10. fig01 inset: the "Duruma (S6-L2, S6-L1; 2050)" label overlaps the Riyadh station cluster.
11. 15 deck figures with EN/AR titles (task asked 12–20) and `figures.csv` with the five required columns: fine. The Arabic figure titles were written natively (prompt v1.2 allows this).
12. R8 tests are skipped, not failed, when `runs/` is absent (handoff); the integration clone of `runs/` must precede `make test` on `main` (memory note).

## 7. Three most important fixes

1. Write the handoff: status block in `docs/status/r8.md` ending `R8: done` (or `blocked`), the R8 row and the CP6 package list in `docs/STATUS.md`, the cost-log row (F1).
2. Replace "construction start 2030/2050" with phase/opening wording and the A-r6-002 construction starts (2027/2047) in §0.4, §4.4 and §7, consistent with Figure 9 and the brief (F2).
3. Re-caption Figures 4, 9, 12, 13, 14 and 15 from `figures-index.csv` (title, caption, sources) and widen or wrap the fig09 subtitle so the S6-L1 P90 statement is legible; add a `report check` rule that every `![Figure n.` caption's source line names the figure's indexed sources (F3).

VERDICT: FAIL

---

# Pass 2 — HEAD 0509009 (fixes b412f77, 0509009), 4 Nov 2026

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.

Scope: re-check of F1–F3 and observations 1–12 of pass 1, the gates, determinism of the figure and report builds, ten-plus numbers touched by the fixes, and a sweep of the changed files for new issues. Nothing was edited except this file. The coordinator's instruction for this pass: the closing `R8: done` line is written by the builder only after a PASS, so its absence is not a FAIL here.

## P2.1 Commands run

| command | result | time |
|---|---|---|
| `make test` (ruff check, ruff format --check, pytest, docver, manifest) | exit 0; "All checks passed!"; **662 passed, 10 warnings** (`uv run pytest --tb=no -q -o addopts="" -rs`; the project's `addopts = "-q"` plus `-q` hides the summary line, which is why a plain `pytest -q` prints no count); `docver OK: 337 files`; `manifest OK: 386 rows` | 33.6 s (pytest 31.3 s) |
| `uv run python -m common.report check` | `report check: PASS` (now includes the rule `figure-sources`: `common/report.py:1660–1683`, wired at line 1710) | < 2 s |
| `uv run python -m common.sources bilingual-check docs/executive-summary.en.md docs/executive-summary.ar.md` | `PASS: 254 numeric tokens … 254; equal` (248 → 254: the six tokens 2030, 2050, 2027, 2047, 6, 002 added in both languages) | < 2 s |
| `grep -rn -i "claude\|opus\|haiku\|fable" docs/report docs/policy-brief.md docs/executive-summary.*` | empty (exit 1) | — |
| `uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/`, then `uv run python -m common.report build`, then `git status --porcelain` | exit 0 / exit 0; **git status empty** (byte-identical rebuild; no `git restore` needed) | 13.6 s + 1.0 s |
| `cd web && npx tsc --noEmit` | exit 0 (strict) | 1.7 s |
| `git status --porcelain` at start and end | clean | — |

## P2.2 Pass-1 failures

| id | status | evidence |
|---|---|---|
| F1 handoff | **fixed** (one part accepted) | `docs/status/r8.md` v1.0: status block with report sections (9), figures (15 + 15), dashboard build (`tsc`, `npm run build`, 35 API tests, 5 screenshots), bilingual 254 = 254, release-note rows (290) and blockers (B1–B9 + Google Chrome), decisions D-r8-01..04, "Not fixed here", measured line (`make test` 662 / docver 337 / manifest 386: all three match what I measured). `docs/STATUS.md` v1.29 line 32: R8 row with the same figures; section "R8 decisions and CP6 package" with the seven-item CP6 package list and the pending Google Chrome approval. Closing `R8: done` line: absent by design until this PASS (coordinator's instruction). **Cost-log row**: still absent (`docs/cost-log.md` last row `main-FIX_R7-try1`); `r8.md` says "appended by `run_track.sh` at run end". Accepted with the same reason as the done line, as in verify-R7 (O1: "at integration … add the cost-log row"); it must exist before the `r8` tag (see P2.6). |
| F2 construction-start wording | **fixed** | `00-front-matter.md:25` new "Phase years" convention bullet (2030/2035/2040/2050 phase years; construction 2027/2032/2037/2047; gate for a 2050 phase in 2047); `:32` "S6-L1 … in phase 2050, construction from 2047 by A-r6-002"; `04-results.md:32` and `:84` row header "corridors (phase year; construction starts 3 years earlier, A-r6-002)" with "(phase 2030)" / "(phase 2050)" cells (generated by `common/report.py` `_layout_rows`); `07-phased-programme.md:9` "construction starts three years earlier (2027 and 2047, A-r6-002), so each gate falls before construction", G1 "phase 2030, gate and construction start 2027", G2/G3 "phase 2050, gate and construction start 2047"; brief `:21`, `:116`, `:144` and both summaries (`en.md:31`, `ar.md` same bullet) say the same. Register: `docs/assumptions.md:525` A-r6-002 "phase year − 3 (2030 → 2027 … 2050 → 2047)"; `optimise/layout.py:55` `START_LAG = 3`. Figure 9 (viewed): bars 2027–2030 and 2047–2050, "gate 2027" / "gate 2047". The report, the brief, the summaries, the figure and the register now agree. |
| F3 figure captions | **fixed** | Captions are generated: `common/report.py` `gen_figure` (lines 1003–1022) writes the `![Figure n. <title_en>]` line, the label line, `*Figure n.* <caption>` and `Source: <sources>. Provenance: <provenance>.` from `docs/report/figures/figures-index.csv`; `<!-- gen:fig-… -->` blocks in sections 01, 03, 04, 05, 06, 07. I compared all 15 captions in the sections (grep `^\*Figure\|^!\[Figure`) with the 15 index rows: identical text. Fig 4 source now `runs/cba/CBA-S2..S5-*/results.json (73 cases)` with provenance `R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1`; Fig 9 caption now describes construction windows, openings and gates; Fig 12 caption now Jeddah S0 vs S1 and Dammam S1 vs S1 + Dhahran, with the ten access files; Fig 13 sources the two corridor YAMLs, `metrics.csv`, `cost_levels.yaml`, `fiscal.json`; Fig 14 "S1 … and the Al-Kharj spur" from the four tornado/switching files; Fig 15 "S1 and the CP7 layouts" from `draws.parquet` and `top5.csv` (`feasibility-report.md:149, 219, 226, 293, 331, 338, 387, 394, 437, 444, 457, 464, 522, 582, 669`). `report check` rule `figure-sources` fails the build if a title or source line departs from the index; `tests/test_report_figures.py` extended (+53 lines). fig09 subtitle: viewed `fig09-stage-gates.png`, the full line "… S6-L1 NPV at P90 cost low/medium/high: -2,958 / -724 / 1,631 SAR m." is legible inside the canvas; the build now refuses a figure with text beyond the canvas (`clipped_texts`, `docs/report/figures/README.md`). |

## P2.3 Pass-1 observations

| # | status | evidence |
|---|---|---|
| 1 prompt v1.1 vs v1.2 | recorded | `r8.md` D-r8-01 names the v1.2 basis; `STATUS.md` R8 decisions line. |
| 2 ridership 0.69 vs 0.70 | fixed | Every statement now reads "median 0.69 … in the draws, central ridership ratio 0.693 in `runs/cba/…/switching_values.json`; class A-rcf-029" (`01-executive-summary.md:32`, `03-methods.md:66`, `05-benchmarks.md:28`, `06-risks.md:37`, brief `:109`). File: `central_ridership_ratio` 0.6931289883 in both `CBA-S3-branch_spur-al-kharj` and `CBA-S1-committed-programme` `switching_values.json`; A-rcf-029 P50 0.70 (`docs/assumptions.md:572`). One figure, right source. |
| 3 S6-L3 2,426 vs 2,427 | fixed | `common/report.py` `fm` now rounds half away from zero (Decimal ROUND_HALF_UP); 2,427 in `01-executive-summary.md:20, 34`, `04-results.md:85–86`, `06-risks.md:64`, `07-phased-programme.md:27`, brief `:49, 63`, both summaries (`en.md:25`, `ar.md:27`); rule stated in `00-front-matter.md:26`. File 2,426.50 (`top5.csv`). Side effect checked: `annex-regions/eastern.md:67` 88.3 → 88.4 km for `S3-branch_spur-al-jubayl` (YAML `length_km: 88.35`), consistent with the rule; no sign or ranking changed (D-r8-03). |
| 4 `docs/delivery-models.md:353` 14,612 | still open, accepted | R7 document outside R8 ownership; listed in `r8.md` "Not fixed here" and in the CP6 package item 7. |
| 5 O11 closure wording | fixed | `r8.md:16` now says `depends_on_unsourced` "lists only those … whose switching value falls inside the registered range … empty in every case", and `not_sourced_for_ksa` names the premium: matches `funding/vfm.py:116–117`. |
| 6 release note: superseded rows; model-id masking | fixed / unchanged by design | `docs/licences-release.md` v0.2 rows 9, 10, 11, 70, 124, 130, 135, 139, 144, 151 now name the versioned row that carries the release status; status-key text explains the convention; B7 now cites the new `alignments-v2/` row. Row 1 keeps the pointer "[model ids: see docs/licences.md]" (B8 stays open, as intended). Google Chrome still "approval pending". |
| 7 `docs/r6-topology.md:112` | still open, accepted | outside the R8 grep set and ownership; in `r8.md` "Not fixed here" and CP6 item 7. |
| 8 fig14 footer; fig12 Dammam | fixed | fig14 (viewed) footer "R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1 · source: …tornado.csv; …switching_values.json" (no judge-v3 pairing); fig04 same provenance per the index. fig12 (viewed) carries the generated note "Door-to-door counts only zones reached by a rail ride (same-station trips excluded). Dammam, S1: 1 zone within 120 min (72,170 people, outside the metro); the Dhahran station 12.6 km from Dammam adds a short ride … (10 zones within 90 min, 22 within 120). Bands drawn: 90 and 120 min; 30, 45, 60 min reach no zone in these runs." |
| 9 dashboard legend; fixture README | fixed | `web/src/components/MapView.tsx` legend "committed/under procurement (announced/planned)" plus the generated line "Committed lines are announced/planned, not existing (source, date): gcc-railway-ksa (S-029, 2026-05-12); landbridge (S-054, 2026-01-21); riyadh-rail-link (S-r1a-055, 2026-08-31)" (viewed in `dashboard-map.png`; `api/data.py` adds `source_date`); `tests/fixtures/README.md` v1.2 states the `api/` exception. Difference-mode limitation (three lines) stays and is declared in the view and in `r8.md`. |
| 10 fig01 inset label overlap | fixed | viewed: "Duruma (S6-L2, S6-L1; 2050)" now sits left of the station in the inset, clear of the Riyadh cluster. |
| 11 deck figures | fine | unchanged. |
| 12 tests skip without `runs/` | accepted | integration note (memory: clone `runs/` before `make test` on `main`). |

## P2.4 Spot-check of numbers touched by the fixes (13 checked, 13 match)

| # | statement (where) | document | run / register |
|---|---|---|---|
| 1 | construction starts 2027 / 2047 for phases 2030 / 2050 (§0.4, §4.4, §7, brief §1/§6/§8, summaries) | 2027 / 2047 | A-r6-002 `docs/assumptions.md:525`; `optimise/layout.py:55` `START_LAG = 3` |
| 2 | S6-L3 robust NPV (everywhere) | 2,427 | `top5.csv` 2,426.5019 (half away from zero) |
| 3 | S6-L3 under weights v2 (§1.4, §6.4) | 2,427 → 3,180 | `runs/r7-v2/sensitivity.json` S6-L3 robust_npv [2426.5, 3179.9] |
| 4 | S6-L1 under weights v2 | 11,023 → 11,297 | [11022.9, 11297.3] |
| 5 | ridership ratio (§1.4, §3, §5.3, §6.2, brief §5) | median 0.69; central 0.693; class 0.70 | `switching_values.json` central_ridership_ratio 0.69313 (S1 and S3 cases); A-rcf-029 P50 0.70 |
| 6 | fig09 subtitle S6-L1 NPV at P90 cost | −2,958 / −724 / 1,631 | `top5.csv` −2,957.61 / −723.93 / 1,630.85 |
| 7 | fig09 gates and windows | gate 2027, 2047; bars 2027–2030, 2047–2050 | A-r6-002; `fiscal.json` S6-L1 spur capex 2046–2050 (pass 1 #F2) |
| 8 | fig12 Dammam S1 120 min; +Dhahran 90 / 120 min | 1 zone, 72,170; 10 zones, 2,106,224; 22 zones, 3,113,662 | `runs/access/S1/reached.parquet` and `…/S5-station_addition-dhahran/reached.parquet` (metro "Dammam–Khobar–Dhahran", mode door_to_door): identical |
| 9 | fig12 Dhahran–Dammam distance | 12.6 km | `S5-station_addition-dhahran.yaml` km posts: 12.60 |
| 10 | fig12 Jeddah S0 / S1 120 min | 5,575,730 / 5,684,737 | `runs/access/S0|S1/reached.parquet` Jeddah: identical |
| 11 | fig04 / fig14 provenance | R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1 | `runs/cba/*/meta.json` code_version r4-15-g3d49c58, seed 1 (three cases sampled) |
| 12 | fig14 switching values (unchanged by the fix, re-read on the new render) | S1: demand 163 %, capex × 0.26, VoT × 8.94, rate 0.27 %; spur: 66 %, × 1.09, × 0.85, 3.03 % | pass 1 #26 (`switching_values.json`): match |
| 13 | `annex-regions/eastern.md:67` spur length | 88.4 | YAML 88.35 |

Captions vs `figures-index.csv`: all 15 titles and captions identical (P2.2 F3); `report check` rule `figure-sources` PASS.

## P2.5 New-issue sweep of the 35 non-image files changed since c97f724

- Home paths `grep -n "/Users/[a-z]"`: empty. Model names: hits only in `common/report.py` (the regex itself and a docstring), `tests/test_*.py` (the forbidden-word lists), `tests/fixtures/README.md` ("Claude Code stream-json" fixture, pre-existing), `docs/status/*`, `docs/STATUS.md` and the release note row 1 pointer: none in the report, brief, summaries, figures or dashboard. `\bwill\b` in sections 01–07, brief, EN summary, both figure READMEs: empty. Advocacy phrases: only `00-front-matter.md:11` "The study asks whether Saudi Arabia should build …" (the question being studied, unchanged since pass 1, not a recommendation). `git push` in tracked scripts/Makefile: none.
- Labels: the synthetic label and `ALIGNMENT_LIMITATION` are on every re-rendered figure (viewed fig01, fig09, fig12, fig14; `tests/test_report_labels.py` +13 lines); the dashboard footer unchanged. Framing (L2 central, L1 upside with its P90 statement, L3 reach, L4/L5 illustrations only) unchanged; the generated figure source line appends the S6-L1 risk sentence wherever a caption names S6-L1 (`gen_figure`, `L1_MARK`), seen on Figures 1, 5, 6, 7, 8, 9, 15.
- Hygiene: `git ls-files` under `data/`, `runs/`, `movies/`, `film/` unchanged from pass 1; `web/node_modules` and `web/dist` untracked and ignored; git status clean before and after both rebuilds.
- `docs/STATUS.md:32` says "done on track `r8` (`R8: done` …)" while `docs/status/r8.md` does not yet carry that line: consistent once the builder appends it after this PASS; not a defect of the deliverables.

## P2.6 Criteria (pass 2)

| # | criterion | PASS/FAIL | evidence |
|---|---|---|---|
| C1 | number tracing in report, brief, summaries | **PASS** | F2 and F3 fixed; 13 touched numbers re-traced (P2.4); pass-1 table of 30 unchanged |
| C2 | figures generated from run outputs | PASS | rebuild byte-identical; captions and source lines generated from the index |
| C3 | bilingual check | PASS | 254 = 254 |
| C4 | maps: layer legend and OSM credit | PASS | fig01, fig12, dashboard (viewed); legend "(announced/planned)" now also in the dashboard |
| C5 | synthetic label and ranges | PASS | P2.5 |
| C6 | no model names in public-facing deliverables | PASS | grep empty |
| C7 | no content from the author's company | PASS | unchanged from pass 1 |
| C8 | non-partisan, no advocacy | PASS | P2.5 |
| C9 | no "will" in result statements | PASS | grep empty |
| C10 | dashboard builds; API tests | PASS | `tsc` clean; 662 tests incl. the 35 + 8 new API/legend tests |
| C11 | licence release note complete, conflicts flagged | PASS | v0.2; superseded rows explained; Chrome still flagged, not resolved |
| C12–C24 | framing, v1/v2 weights, legal items, labels, coverage, benchmarks, assumptions, spot-check, method checks, hygiene, R7 closures, reproducibility, Arabic/model policy | PASS | unchanged from pass 1; O5 wording corrected |
| C25 | STATUS and status files | **PASS** (conditional) | status block, STATUS.md row, decisions, CP6 package list present and matching what I measured (662 / 337 / 386 / 254); `R8: done` line and the cost-log row are run-end items by the coordinator's instruction and the R7 precedent: both must be present before the `r8` tag |
| C26 | tone and scope | PASS | unchanged |

## P2.7 Remaining items for the coordinator (none is a FAIL)

1. Append `R8: done` to `docs/status/r8.md` and the R8 cost-log row (`run_track.sh`) before tagging `r8`.
2. At integration: `docs/delivery-models.md:353` (14,612 → 14,611), `docs/r6-topology.md:112` wording, and Tariq's decision on Google Chrome for the screenshots (or retake with Chromium).
3. Clone `runs/` and `data/ksa/` into `main` before `make test` there (R8 tests skip without them).

VERDICT: PASS
