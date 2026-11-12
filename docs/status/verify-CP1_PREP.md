> **Document version:** docs/status/verify-CP1_PREP.md v1.0 | 31 Oct 2026 | Author: red-team-verifier | Status: verified

# VERIFY_CP1_PREP — independent red-team audit of milestone CP1_PREP

Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

Scope: main checkout, HEAD `9b5739e` (builder commits `f7fa0bd..HEAD`, 12 commits), read-only. Audit against `prompts/CP1_PREP.md` (seven items and the **Acceptance (verifier)** list), PROJECT.md §2, §5, §7, §9, CLAUDE.md and `.claude/agents/red-team-verifier.md`. Nothing was fixed; the only file written is this report. Working tree at audit time: `git status --porcelain` = ` M docs/status/main.md` (the builder's uncommitted header bump v1.0 → v1.1 only).

## 1. Commands run (31 Oct 2026, 01:00–02:00 +03)

| command | exit | time | output line |
|---|---|---|---|
| `uv run ruff check .` | 0 | 0.15 s | `All checks passed!` |
| `uv run ruff format --check .` | 0 | 0.04 s | `301 files already formatted` |
| `make test` (ruff, format, pytest, docver, manifest) | 0 | 3.1 s | `77 passed`; `docver OK: 185 files`; `manifest OK: 16 rows` |
| `uv run python -m common.docver check docs prompts .claude` | 0 | 0.06 s | `docver OK: 185 files` |
| `uv run python -m common.manifest verify` | 0 | 0.37 s | `manifest OK: 16 rows` |
| `uv run python -m common.cost_log check` | 0 | 0.08 s | `cost log OK: 19 rows` |
| `uv run python -m screening.region_sweep validate cities/ksa/regions/pilot-*.parquet` | 0 | 0.43 s | 13 × `ok` (10/8/18/22/11/20/9/18/9/8/19/25/9 rows); 9 `WARN` on missing or non-integer `governorates_gastat` headers (GASTAT count unverified, known) |
| `uv run python -m common.cost_log summary` | 0 | — | `TOTAL runs 19 hours 3.69 USD 53.20`; main 42.61, coordinator 0.19, pilots 10.40 (sum of the 14 pilot rows) |
| determinism (section 4) | 0 | — | `long-list` 186/157/8/169; `score` ×2: identical `scores.parquet` (SHA-256 prefix `9e61baf92468b559` for s1, s2 and `runs/screening-pilot/score/`) |

## 2. Acceptance criteria (prompts/CP1_PREP.md, "Acceptance (verifier)")

| # | criterion | verdict | evidence |
|---|---|---|---|
| A1 | One criteria set: plan §1 and the YAML agree line by line | PASS | `cities/ksa/assumptions/screening_weights.yaml` v0.2 vs `docs/plan.md` §1 compared key by key: long_list (threshold 10,000 A-screen-001; sensitivity 5,000 -002; role_passes -003; served_km 10 -004; centres_always_pass rule 2; straight-line -027; use_committed false -030), five criteria (weights 0.30/0.20/0.20/0.20/0.10 = -020…-024; rail-gap log_capped, cap 300 range 200–500 -021; band 40–120 -005; tier factors 1.0/0.6/0.3 -026; roles list incl. energy -007/-010, cap 3 -008, exclude administrative -009, source rule -011; terrain penalties incl. mixed −0.5 -025; missing rules -028), sweep 0.25 -029, short list 60 / 0.8 -006, report_top 30 (sourced to PILOT_MERGE), metros -013. No divergence found. |
| A2 | No duplicate assumption ids; no id with two meanings | PASS | `grep -oE "^\| A-[a-z]+-[0-9]{3}" docs/assumptions.md | sort | uniq -c`: every id appears exactly once (33 ids). Renumbering note: `docs/assumptions.md` line 44 ("Renumbered 31 Oct 2026 … No id is used for two meanings") and the A-screen-004 row; A-screen-012 row reads "merged into A-screen-023 (31 Oct 2026)", status `merged`. Plan §1 closing paragraph maps the retired F1–F4 ids. |
| A3 | Every A-screen/A-cba id named in the prompt exists with URL + access date | PASS | Rows present once each: A-screen-001…014, -020…-030, A-cba-001…004, -010. Each (except the merged pointer A-screen-012) carries "Sources (accessed 2026-10-31): S-cp1-…" resolving to `docs/sources/index.csv` rows with URL and access date (S-cp1-200…210 for the brief-internal ids, S-cp1-060…098 for A-cba, S-cp1-204/207/208/209/210 for the screening rows). Approval text: "Tariq, 30 Oct 2026" on -001, -002, -013, A-cba-001 (flagged "RE-CONFIRM"); "pending CP1" on all others. |
| A4 | `administrative` has zero effect on any score (test) | PASS | `tests/test_screening_pilot.py::test_administrative_role_does_not_change_any_score` (lines 189–200) and `::test_duplicate_roles_count_once`; `screening/funnel.py::scored_roles` drops `exclude_from_score` roles in both the long-list filter (line ~100) and the criterion (line ~203). `runs/screening-pilot/score/summary.json` records `roles_excluded_from_score: ["administrative"]`. |
| A5 | Rail gap saturates at the cap (test) | PASS | `tests/test_screening_pilot.py::test_rail_gap_log_measure_saturates_at_cap` (lines 203–214): g(300) ≈ 1.0, g(450) = g(900) = 1.0, monotone below the cap, NaN preserved, linear measure keeps rising, unknown measure raises. `funnel.gap_measure` implements `log10(1+min(d,cap))/log10(1+cap)`. Measured on the real run: 56 of 157 long-list rows (35.7 %) have `c_rail_gap` = 1.0. |
| A6 | Funnel rerun outputs and `docs/screening-pilot.md` updated with before/after | PASS | `runs/screening-pilot/{merge,long-list,long-list-5k,long-list-committed,score,score-5k,score-committed,score-linear-gap}/` each with `meta.json` (seed 1, code `session1-pilot-8-g127e382`, data hash `885dae66…`); `runs/screening-pilot-before-cp1/` kept. `docs/screening-pilot.md` v0.3 §3 (counts before → after), §4 (stability 21/30, was 24/30), §5 (top 30 with "rank before item 1" column and a collapsed "Before item 1" table), §6 (drivers with bracketed before values), §7 (sensitivities), §8 (27 roles per region). All quoted values re-derived from the parquet files (section 3 below). |
| A7 | `docs/cost-log.md` outcome column correct for every run | PASS | Recomputed against the status files: `R0: done` (main.md:36), `DATASCOUT_1H: done` (:69), `LANDBRIDGE_RECONCILE: done` (:90), `PILOT_MERGE: done` (:124); pilots `done` for al_jouf, asir, eastern, hail, jazan, makkah, northern_borders, riyadh, tabuk (status line in backticks, tolerated); `blocked` for al_baha (pilot-al_baha.md:42), madinah (:56), najran (:54), qassim (:60), all of whose status files end `… : blocked - …`. No `failed` row. The prompt's expectation of `done` for all 13 pilots is not supported by the status files; the builder recorded this as decision D14 rather than relabelling (correct). tabuk try1: stream-json result `is_error: false` and the status line exists, so `done` follows the stated rule (observation O3). |
| A8 | `cost_log check` passes | PASS | `cost log OK: 19 rows` (exit 0); `docs/cost-log.md` and `.csv` agree row for row. Tests: `tests/test_cost_log.py` 10 tests incl. `test_status_line_tolerates_backticks_and_bold`, `test_error_result_is_failed_even_with_status_line`, `test_status_file_prefers_worktree`, `test_fix_outcomes_rewrites_both_files`, `test_add_accepts_status_file`. `run_track.sh` diff vs f7fa0bd: exactly one changed line (adds `--status-file "$dir/docs/status/$track.md"`). |
| A9 | `screening/pilot_builders/` holds every recoverable script; unrecoverable ones listed | PASS | 44 `.py` files + `README.md` (v1.0) with origin path, last-modified time and role per file, 13 of 13 regions; "Not recoverable" section lists the one-off `python -c`/heredoc commands (only in gitignored logs) and the non-pilot helpers deliberately not copied. Scripts carry `# Origin: /tmp/...` headers; `/tmp` appears only in those headers and in archival `open("/tmp/...")` calls, documented as not runnable. No `/Users/` path in the folder. |
| A10 | `docver check` inside a worktree path counts files | PASS | `tests/test_docver.py::test_iter_md_inside_a_worktree_checkout`; `common/docver.py::_in_worktree` uses `relative_to(root)`. Independent run: a copy of `common/` placed at `/tmp/vcp1/wt/.worktrees/r1x/` resolved `REPO_ROOT` to that path, reported `FAIL docs/bad.md` (exit 1) and, after removing it, `docver OK: 1 files` (exit 0). |
| A11 | Templates and skill carry the merged schema | PASS | `prompts/REGION_TEMPLATE.md`, `prompts/PILOT_REGION_TEMPLATE.md`, `.claude/skills/region-sweep/SKILL.md` each name `pop_source_status`, `primary_to_find`, `osm_type`, `nearest_metro_tier`, `tag_5k` ("never `threshold_5k`"), `threshold_50k`/`pilot_sample` as pilot-only, the six schema terrain words (with "not `sand_dunes`, `coastal_plain`"), the role enum incl. `energy`, the `/tmp` rule (scripts under `screening/sweeps/{{SLUG}}/`, raw downloads under `data/ksa/{{SLUG}}/raw/` + manifest row), and `region_sweep validate`. 13 regenerated `prompts/REGION_*.md` (v1.1, 31 Oct 2026) carry the rules; `scripts/make_region_prompts.sh` parses (`bash -n`). |
| A12 | `screening.region_sweep validate` exists and passes on all 13 pilot files | PASS | Section 1 row 7 (13 × `ok`, exit 0); `tests/test_region_sweep.py` (3 tests: all pilot registers validate, header-count mismatch fails, bad role fails). |
| A13 | Al-Qarā has coordinates and a register row | PASS | `cities/ksa/candidates-pilot.parquet` row `al_baha:node:9327998071`: lat 20.2475218, lon 41.3607144, `is_governorate_centre` true, `screened` true, population null (not tabulated, S-cp1-005), `primary_to_find` set; same in `cities/ksa/regions/pilot-al_baha.{parquet,csv}`. Live OSM API 0.6 (31 Oct 2026): node 9327998071 lat 20.2475218 lon 41.3607144, `place=town`, `capital=6`, `name=الأطاولة`, `name:en=Al Tawilah`, version 5 of 2025-01-26 — matches S-cp1-003 exactly. `docs/coverage.md` row 6: Al-Qarā `screened`, no "not yet swept" line. Second-source conflict (Wikidata/Wikipedia at 29.883, 40.217, Al-Jawf) re-fetched and confirmed; correctly not used. |
| A14 | Riyadh seat populations found or each listed as not found with sources tried | PASS | `cities/ksa/regions/pilot-riyadh.parquet`: 14 of 14 seats have `population`, `pop_source` S-cp1-012…025, `pop_source_status` secondary, `primary_to_find`, `screened` true (Ad-Dilam 39,267; Layla 29,698; Al-Ghat 8,683; Al-Hariq 6,895; Al-Quwayiyah 28,589; Ar-Rayn 2,726; As-Sulayyil 25,136; Durma 16,344; Hawtat Bani Tamim 30,720; Huraymila 9,842; Marat 6,574; Shaqra 32,215; Thadiq 7,433; Wadi ad-Dawasir 77,433). Spot-checked 6 of 14 on the live page (section 5): all match. GASTAT attempts logged with results (S-cp1-026…028; `portal.saudicensus.sa` HTTP 000 and the open-data API "Request Rejected" reproduced by me on 31 Oct 2026). |
| A15 | citypopulation.de row in the licence register with verified terms | PASS | `docs/licences.md` line 162 / `docs/licences.csv` last row: CC BY 3.0 per Terms of Use vs CC BY 4.0 in page HTML flagged as a CONFLICT (not resolved silently), open Y (figures only), commercial Y with attribution, attribution wording, obligations, archived-HTML policy, status `verified 2026-10-31`, approval `pending Tariq (CP1)`; six older rows marked superseded. Live fetch of `https://www.citypopulation.de/en/help/termsofuse/`: "the CC BY 3.0 license holds", "for non-commercial as well as for commercial use", attribution "Thomas Brinkhoff: City Population, http://www.citypopulation.de", maps/geodata/coordinates/images reserved; page undated — all as registered. |
| A16 | `docs/cp1-decision-pack.md` exists, complete, no model names, every number traceable | PASS | File present (v0.1, header + label line), sections: built, verified numbers (table with trace column), assumed (grouped screening/appraisal/cost/film/data), blocked, cost, 14 decisions with recommended option first and the id each sets. `grep -nEi "claude|opus|haiku|fable|hanko|sonnet|gpt|gemini|anthropic"` → no match. Every number traced (section 3). |

## 3. Number tracing (decision pack, status block, plan §2/§8, screening-pilot.md)

All values below were re-derived by me from `runs/`, the register parquet files, `docs/cost-log.csv`, `df -h ~` or the cited source; "✓" = matches the document.

| figure in the documents | my measurement | trace |
|---|---|---|
| register 186 rows (was 185); 164 with a population, all `secondary`; 0 verified | 186; `population` non-null 164; `pop_source_status` {secondary: 164, null: 22} ✓ | `cities/ksa/candidates-pilot.parquet`; `runs/screening-pilot/merge/meta.json` rows_out 186 |
| long list 157 (was 156), served 8 (8), 5k long list 169 (168), short list 60 | after: 157/8/169/60; before (`runs/screening-pilot-before-cp1/long-list/meta.json`): all 185, long 156, served 8, 5k 168 ✓ | long-list `summary.json`, `score/summary.json` `n_short` 60 |
| top-30 stability 21/30 (was 24/30) | `score/summary.json` 21 (0.70); before-cp1 24 (0.80) ✓ | |
| 22 towns in common before/after; Jazan 10 → 4; Riyadh 3 → 9 | 22; after {riyadh 9, makkah 4, jazan 4, madinah 3, asir 3, tabuk 2, 5 × 1}; before {jazan 10, makkah 4, riyadh 3, asir 3, najran 2, tabuk 2, madinah 2, 4 × 1} ✓ | `scores.parquet` both runs, `rank` ≤ 30 |
| linear-gap sensitivity 26/30 with base; 24/30 with the old run (6 data changes, 4 cap changes) | linear ∩ after = 26; linear ∩ before = 24 ✓ | `score-linear-gap/scores.parquet` |
| 5k and committed sensitivities: top 30 unchanged | 5k ∩ base = 30; committed ∩ base = 30 ✓ | `score-5k/`, `score-committed/` |
| committed layer moves Ad-Dawadmi to the served bucket (served 9) | committed served set = base set + Ad-Dawadmi ✓ | `long-list-committed/longlist.parquet` |
| 36 % of long-list rows saturate at the cap | 56/157 = 35.7 % ✓ | `score/scores.parquet` `c_rail_gap == 1.0` |
| top-30 table rank 1 Jiddah 0.8269, rank 30 Ḥā'il 0.5004 | ✓ | `score/scores.parquet` |
| Spearman rail gap −0.01; drivers table | `spearman_with_score.rail_gap` −0.0104; other values match §6 ✓ | `score/summary.json` |
| coverage 152 rows, 149 with a register row, 140 screened, 8 excluded, 2 not yet swept, 13/13 regions, 150 S-073 rows sum 32,175,224 | `docs/coverage.md` totals line and summary ✓ (register-rows column totals 185 because Hala Ammar (Tabuk) has no governorate match; see O5) | generated file; S-073, S-077 |
| cost USD 53.20, 19 runs, 3.69 h; main 42.61; pilots 10.40; probe 0.19 | `cost_log summary` TOTAL 19 / 3.69 / 53.20; main 42.61; coordinator 0.19; 14 pilot rows sum 10.40 (0.81+0.59+0.92+1.03+0.63+0.75+0.75+1.32+0.73+0.72+0.07+0.74+0.66+0.68) ✓ | `docs/cost-log.csv` |
| disk 24 GiB free of 460 GiB; thresholds 15/40/50 → 16 and 26 GiB short | `df -h ~`: 460Gi / 402Gi used / 24Gi avail, 95 % ✓; 40−24 = 16, 50−24 = 26 ✓ | measured 31 Oct 2026 |
| Landbridge SR 100 bn = USD 26.667 bn at 3.75; 3.81 × USD 7 bn | 100/3.75 = 26.667; 26.667/7 = 3.81 ✓; `docs/costs-landbridge.md` lines 32, 34 | A-cost-001; S-lb-001…003 |
| D5 transfer factor 1.07–1.14 from ratio 1.142, e = 0.5…1.015 | 1.142^0.5 = 1.069; 1.142^1.015 = 1.144 ✓ | S-cp1-097/098 (WDI 73,783.56 / 64,606.50 → 1.142) |
| 27 roles applied (makkah 7, eastern 7, riyadh 4, madinah 3, northern_borders 2, jazan/asir/qassim/al_baha 1), 3 not added | `screening/cp1_fixes/roles.csv`: 27 `added`, 3 `not added` with reasons; per-region counts ✓; register rows carry the roles (e.g. Jiddah [port, airport, hajj_umrah], Jubail [industrial_city, port, energy], Yanbu [port, industrial_city, energy, airport], Al-Ula [giga_project, heritage, tourism, airport], Hofuf [heritage, agriculture, airport], Dammam [port, airport], Makkah [hajj_umrah], Madinah [hajj_umrah, airport]) — every "at minimum" item of prompt item 1.3 is present or listed as not found | |
| plan §8 reclaim sizes uv ~7 GB, Docker ~16 GB, Ollama ~25 GB, Google ~3.8 GB | quoted from the coordinator and labelled "not re-measured" in the plan. My `du` also exceeded 100 s on all four; `docker system df`: images 5.80 GB (3.35 reclaimable), containers 1.20, volumes 7.95 (0.36 reclaimable), build cache 4.46 → ≈ 19.4 GB total, ≈ 5.0 GB reclaimable without removing active images/volumes (3 images and 2 volumes are active) | observation O4 |

### A-cba source checks (mandated)

| S-id | claim in register | what I read on 31 Oct 2026 | result |
|---|---|---|---|
| S-cp1-060 | Green Book 2026 para 6.54: 3.00 % (1–30), 2.50 % (31–75), 2.25 % (76+) | PDF `The_Green_Book_2026.pdf` (cover "THE GREEN BOOK … 2026", 86 pp), para 6.54: "It is set at 3.00% in real terms for years 1 to 30 of an appraisal. It is 2.50% for years 31 to 75, and then 2.25% for year 76 onwards." gov.uk publication page: Last updated **28 October 2026**, change note "Updated to reflect changes to the approach to discounting." | verbatim match; the 28 Oct 2026 update is real and material |
| S-cp1-061 | supplementary guidance Oct 2026 para 3.8 | PDF "Discounting, Green Book supplementary guidance, October 2026", para 3.7: "3.00% for years 1 to 30 … 2.50% for years 31 to 75 … 2.25% for years 76 to 125" | match (list sits under 3.7/3.8) |
| S-cp1-062 | TAG A1.1 May 2026 para 2.7.6: 3.5 % to year 30, 3 % 31–75, 2.5 % 76+ | cover "TAG Unit A1.1 Cost-Benefit Analysis May 2026"; 2.7.6: "3.5% should be applied for years between the current year (the year the appraisal is taking place) and year 30 … 3% for years 31 to 75 … 2.5% for year 76 onwards" | verbatim match |
| S-cp1-067 | EC CBA guide Dec 2014 §2.8.1 box: 5 % Cohesion, 3 % others; §2.8.8 is GHG | cover "Guide to Cost-Benefit Analysis of Investment Projects … December 2014"; box "SOCIAL DISCOUNT RATE: THE EUROPEAN COMMISSION BENCHMARK" under 2.8.1 Introduction: "5 % is used for major projects in Cohesion countries and 3 % for the other Member States"; 2.8.8 = "Evaluation of GHG emissions"; no 7 % SDR in the text | verbatim match; section correction confirmed |
| S-cp1-074 | NDMC GMTN page: 2036 tranche 4.875 %, 2056 5.875 %; 2029 4.125 %, 2031 4.375 %; USD 11.5 bn | page table (column "Yield"): 12/01/2029 4.125 %, 12/01/2031 4.375 %, 12/01/2036 4.875 %, 12/01/2056 5.875 %; total 11,500,000,000 USD | match (the "12/01/2026 = 12 Jan" reading is flagged as an assumption in the register) |
| S-cp1-090 | TAG A1.3 May 2026 para 4.5.1 elasticity 1.015 | cover "TAG Unit A1.3 User and Provider Impacts May 2026"; 4.5.1: "Both the work and non-work values of time (excluding journeys by LGV or OGV) are assumed to increase with income over time with an elasticity of 1.015." | verbatim match |
| S-cp1-085/086/087/088/089 (A-cba-004) | 60 years; ≤ 100 years; residual value rules; Table 2 lives; GB 6.11 and 8.32 | TAG 2.3.5 "in all cases should be no more than 100 years"; 2.3.10 "Residual asset values should be included in CBA of projects with finite lives of fewer than 60 years"; 2.3.11 "should not be included for projects with indefinite lives…"; Table 2 railways: track 14 to 40, electrification 30 to 40, signalling 10 to 50, telecommunications 7 to 40, earthworks 100, bridges/tunnels up to 100; GB 6.11 "60 years for infrastructure, such as roads, railways and new buildings"; 8.32 "An asset's residual value or liability at the end of the appraisal period should be included to reflect its opportunity cost." | all match |

## 4. Determinism

`uv run python -m screening.funnel long-list --threshold 10000 --sensitivity 5000 --seed 1 --run-dir /tmp/vcp1/a` → `{"all": 186, "long_threshold": 157, "served": 8, "pass_sensitivity_not_served": 169}`; then `score --sweep 0.25 --seed 1 --in /tmp/vcp1/a/longlist.parquet` twice (s1, s2). `scores.parquet` s1 = s2 = `runs/screening-pilot/score/scores.parquet` byte for byte (SHA-256 prefix `9e61baf92468b559`); `summary.json` identical apart from nothing (no timestamps in it); `meta.json` differs only in `created_utc`. `tests/test_screening_pilot.py::test_funnel_deterministic` also passes. PASS.

## 5. Spot-check (seed 20261031; `random.Random(20261031).sample`)

Sample: 3 of the 27 applied roles (10 %), 2 of the 14 Riyadh seat populations, and 11 of the 108 S-cp1 rows (10 %), plus the five mandated A-cba URLs (section 3). Every sampled figure was re-read on its source on 31 Oct 2026.

| id / row | claim | source read | result |
|---|---|---|---|
| roles idx 7: `madinah:osm:3148037089` Yanbu' airport, S-cp1-100 | airport named in GACA Feb 2025 report | GACA `202502_OPS_Public-Report_E.pdf` (3 pp): "Prince Abdulmohsin bin Abdulaziz International Airport - Yanbu" present | hit |
| roles idx 9: `eastern:osm:38903292` Jubail energy, S-cp1-103 | SATORP "located in the industrial city of Jubail" | totalenergies.com SATORP page (after its 301 redirect): "a refining and petrochemical platform located in the industrial city of Jubail on the country's east coast." | hit |
| roles idx 24: `riyadh:node:1236695687` Ad-Dawadmi airport, S-cp1-100 | "Al-Dawadmi Airport" in the GACA report | present in the domestic list | hit |
| S-cp1-018 As-Sulayyil | 25,136 (place); governorate 35,271 | citypopulation.de/en/saudiarabia/riyad/: As-Sulayyil 23,607 / 26,639 / 25,136; governorate 35,271 | hit |
| S-cp1-023 Shaqra | 32,215; governorate 46,403 | Shaqrā' 22,863 / 26,651 / 32,215; governorate 46,403 | hit |
| S-cp1-006 | Wikidata Q65040833 P625 = 29.8833, 40.2167; population 31,480 | Special:EntityData JSON: lat 29.88333333, lon 40.21666667; P1082 +31480 (also 27112, 4368) | hit (and the coordinate conflict is real) |
| S-cp1-010 | Al-Jawf Qara village node 1236739557 at 29.876944, 40.226944 | OSM API node 1236739557: lat 29.8769440 lon 40.2269440, `place=village`, name قارا (Nominatim itself not re-queried; the referenced object checked on the OSM API) | hit |
| S-cp1-014 Al-Ghat | 8,683; governorate 10,799 | 6,977 / 8,746 / 8,683; governorate 10,799 | hit |
| S-cp1-021 Huraymila | 9,842; governorate 21,758 | 8,460 / 9,696 / 9,842; governorate 21,758 | hit |
| S-cp1-027 | open.data.gov.sa API: HTTP 200 body "Request Rejected" | reproduced: HTTP 200, `<title>Request Rejected</title>` with a support ID; `portal.saudicensus.sa` HTTP 000 | hit |
| S-cp1-050 | Terms of Use: CC BY 3.0; "for non-commercial as well as for commercial use under the condition that »City Population« is referenced" | page: "the CC BY 3.0 license holds"; quote present verbatim; maps/geodata/coordinates/images reserved; undated | hit |
| S-cp1-053 | FAQ: "How can I export the map to a GIS file? That is not possible." | FAQ page: present verbatim | hit |
| S-cp1-082 | Arab News 19 Aug 2026: SR9.52 bn ($2.54 bn), five tranches 2031–2041, no yield | article 19 Aug 2026 "Saudi Arabia raises $2.54bn in August sukuk issuance": sentences present; no rate given | hit |
| S-cp1-087 | TAG A1.1 Table 2 railway lives | Table 2 as extracted (section 3) | hit |
| S-cp1-103 | (same as roles idx 9) | | hit |
| S-cp1-202 | PROJECT.md "40–120 km" | PROJECT.md line 24: "For towns 40–120 km from each major city…" | hit |

Also confirmed on the Riyadh page: Ad-Dilam 39,267, Layla 29,698, Wadi ad-Dawasir 77,433 (S-cp1-012, -013, -025), no "Al-Khamasin" row, source line "General Statistics Authority, Kingdom of Saudi Arabia (web)".

**Hit rate: 22 / 22 (100 %). No fabricated or misquoted figure found.**

## 6. Hygiene and governance

- `git status --porcelain`: ` M docs/status/main.md` (header bump only; the builder's `CP1_PREP` block itself is committed in `9b5739e`).
- `git ls-files` under `data/`, `runs/`, `movies/`, `film/renders/`, `film/audio/`: only `data/README.md`, `data/ksa/tables/README.md`, a 1.3 KB derived CSV and the 243 KB GASTAT one-page PDF, all from DATASCOUT_1H with licence stated in the README. Nothing added by this milestone.
- `git ls-files | xargs grep -ln "/Users/[a-z]"`: empty. Secrets grep (API-key patterns): empty. `git push` appears only in rule text (CLAUDE.md, PROJECT.md, `_common.md`, R9 prompt, verifier agent, earlier verify reports), never as a command in a script.
- the private-list terms: only in the rule sentences of CLAUDE.md, PROJECT.md, agents, prompts and earlier verify reports. No content.
- Model names: none in `docs/cp1-decision-pack.md`; they appear in `docs/plan.md` §0 and §5 (internal planning document, allowed by CLAUDE.md "this mapping lives only here, in the agent files and in docs/cost-log.md" is narrower than current practice: see O6).
- Labels: the pilot label is on the YAML, plan §1, screening-pilot.md, coverage.md, the pack and every `summary.json`/`meta.json`; "will reduce" phrasing: none found in the milestone documents. No advocacy language in the pack (options and evidence only).
- Version headers: every file under `docs/`, `prompts/`, `.claude/` passes `docver` (185 files); `docs/status/*.md` all start with the header.
- Layers: no line YAML touched by this milestone; `use_committed: false` recorded as A-screen-030 with the committed run as a sensitivity.

## 7. Failures

None. Every acceptance bullet has a PASS with evidence above.

## 8. Observations (not acceptance failures; for the coordinator and CP1)

- **O1 — Process slip, recorded by the builder.** `git checkout -- <2 files>` was used once on `main` to restore two tracked builder scripts after an accidental delete (status block). The files are identical to HEAD; no data loss. The prompt forbids `git checkout` for builders; it is disclosed, which is the right outcome, but the coordinator should re-state the rule (use `git restore` only via the coordinator, or avoid deletes).
- **O2 — Two of the 27 applied roles rest on unopened pages.** S-cp1-109 (Makkah hajj_umrah: "search extract (page not opened)", "no verbatim capture") and S-cp1-116 (Hofuf airport: "search summary only"). Both are honestly flagged `secondary` and the facts are not in doubt (Hofuf's airport is also "Al-Ahsa International Airport" in the GACA report, S-cp1-100), but A-screen-011 asks for a source that ties the role to the town; R2 should open the pages or swap to S-cp1-100 for Hofuf.
- **O3 — tabuk try1 outcome.** The orchestrator log (21:35:27) shows try1 fell into the "rate-limited; sleeping 15 min" branch, yet its stream-json `result` has `is_error: false` and the status line (in backticks) was already present, so `fix-outcomes` marks try1 `done` and try2 (1.1 min, 11 turns) also `done`. Per the builder's stated rule this is consistent; the orchestrator's old non-tolerant grep caused the retry. Consider a `retried`/`redundant` note on try2 so the cost per region is not read as two full runs.
- **O4 — Plan §8 reclaim sizes are unmeasured and partly stale.** The uv/Ollama/Google figures are the coordinator's; `du` timed out for the builder and for me. `docker system df` today: ≈ 19.4 GB total but only ≈ 5.0 GB reclaimable without deleting the 3 active images and 2 active volumes, so D13's "Docker ~16 GB" assumes removing Docker content that is in use. State this in D13 before Tariq decides.
- **O5 — Coverage per-region table totals 185 register rows while the register has 186.** The unmatched row is Hala Ammar (Tabuk, no governorate; already noted in screening-pilot.md §8 and gastat-regions.md). `docs/coverage.md` should say so in its summary so 185 ≠ 186 is not read as a lost row.
- **O6 — Model ids in `docs/plan.md` §0 and §5.** CLAUDE.md says the label→model mapping "lives only" in CLAUDE.md, agent files and `docs/cost-log.md`. `docs/plan.md` is an internal planning document, not regulator- or public-facing, so this is not a FAIL, but the coordinator should decide whether plan.md counts as internal before R8.
- **O7 — Status block ending.** `docs/status/main.md` has no `CP1_PREP: done` line yet (the Handoff says it follows the verdict), and `docs/STATUS.md` has no CP1_PREP entry (outside the builder's ownership). Both are the coordinator's next step. This run's cost-log row is appended when `run_track.sh` closes, as for every previous milestone.
- **O8 — A-cba-001 value column still shows the approved 3.5/3.0/2.5 % with a "RE-CONFIRM" flag** while the primary source (Green Book, 28 Oct 2026) gives 3.00/2.50/2.25 %. This is the correct handling (approved value kept, conflict escalated as D1, not resolved silently); D1 must be decided at CP1 before any R5 appraisal run.

## 9. Three most important fixes (for the coordinator / CP1, not blockers for this milestone)

1. **Decide D1 (A-cba-001) at CP1 with the 28 Oct 2026 Green Book in hand**, and then rewrite the A-cba-001 value column to the chosen schedule (the current row carries two schedules). Until then, no appraisal run may cite A-cba-001 as settled.
2. **Fix D13's Docker assumption and measure the reclaim candidates** before Tariq rules on disk: `docker system df` gives ≈ 5 GB reclaimable, not 16 GB, unless active images/volumes are removed; run `du` with no time limit (background) for uv, Ollama and Google caches and replace "not re-measured" in plan §8.
3. **Close the two weak role sources (O2)** by opening S-cp1-109 and S-cp1-116 (or re-pointing Hofuf to S-cp1-100) and, in the same pass, add the Hala Ammar unmatched-row note to `docs/coverage.md` (O5) so the 185/186 counts reconcile on the page.

VERDICT: PASS
