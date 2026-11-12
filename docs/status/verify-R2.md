> **Document version:** docs/status/verify-R2.md v1.2 | 31 Oct 2026 | Author: red-team-verifier (claude-fable-5-1); pass 3 appended | Status: verified

# Verification: R2 national screening (main checkout, HEAD fe85d0e + uncommitted R2 block in `docs/status/main.md`)

Read-only check against `prompts/R2.md` v1.1 (including the "Added 31 Oct 2026 16:25" section), PROJECT.md sections 2/7/9, CLAUDE.md and the coordinator's ten criteria. Nothing was fixed. Working tree at start: `git status --porcelain` = ` M docs/status/main.md` only.

## 1. Commands run (exit codes, timing)

| command | exit | evidence |
|---|---|---|
| `uv run ruff check .` | 0 | "All checks passed!" (0.2 s) |
| `uv run ruff format --check .` | 0 | clean |
| `uv run pytest -q` | 0 | all collected tests pass, 14.9 s; `tests/test_screening_r2.py` = 13 tests (13 dots). The project's pytest configuration suppresses the summary count line, so the builder's "311 passed" is plausible (dots end at 100 %) but not independently counted here |
| `uv run python -m common.docver check` | 0 | "docver OK: 259 files" |
| `uv run python -m common.manifest verify` | 0 | "manifest OK: 307 rows" |
| `uv run python -m common.scenarios validate scenarios/` | 0 | "ok 6 scenario files" |
| `uv run python -m screening.corridors validate` | 0 | "ok 74 corridor files" |
| `make test` (lint, pytest, docver, manifest) | 0 | 14.9 s |
| `uv run python -m screening.corridors generate --seed 1 --run-dir /tmp/r2v-corr --out /tmp/r2v-corr/out --scenarios /tmp/r2v-scen` | 0 | 1.6 s; `{"counts": {"trunk_gap": 23, "branch_spur": 17, "commuter_belt": 27, "station_addition": 7}, "decisions": 21}` |
| `diff -r /tmp/r2v-corr/out cities/ksa/corridors` | 0 | byte-identical (74 files) |
| S2–S5 regenerated vs committed | identical after replacing the `--out` path prefix (`/tmp/r2v-corr/out/` → `cities/ksa/corridors/`) | the only difference is the output path the CLI was given |

## 2. Criteria

| # | criterion | result | evidence |
|---|---|---|---|
| 1 | `docs/coverage.md` reconciles to 150 governorates (S-cp2-gastat-007); 13/13 regions; one row per governorate; every exclusion has a reason | **PASS** | Footer: "governorates in table = 150; governorates_gastat = 150 (primary TA1 governorate export, S-cp2-gastat-007); regions = 13 of 13; register rows = 1691 ... 0 unmapped ... governorates excluded = 0". Independent count of governorate rows by region column: riyadh 23, asir 18, makkah 17, jazan 17, qassim 13, eastern 12, al_baha 10, madinah 9, hail 9, tabuk 7, najran 7, northern_borders 4, al_jouf 4 = 150. No excluded rows exist, so no missing reasons; the 4 centre-only governorates are marked screened by rule 2 (header paragraph) |
| 2 | Filters/weights/thresholds = CP1 YAML, unchanged; sweep and stability reported with numbers | **PASS** | `git diff 10d954c -- cities/ksa/assumptions/screening_weights.yaml` = 0 lines. `docs/screening.md` §5 lines 165–168: 10 corners ±25 %, top-30 stable 23/30 (76.7 %), Kendall tau min 0.8851 / median 0.9377 over 55 pairs, per-corner tau and top-60 overlap listed. §4 filters with counts per region (lines 127–154) |
| 3 | Every corridor YAML has `rule_id` and `generated_from_ids`; none in S0/S1; scenarios and corridors validate; no hard-coded town list; reproducible | **PASS** | Loop over 74 YAMLs: 0 missing `rule_id`, `generated_from_ids`, `layer: hypothetical`, `assumptions_used`. No corridor id appears in `scenarios/S0.yaml` or `S1.yaml`. `screening/corridors.py`: metros come from `metro_table(self.reg, self.cfg)` (line 230) and `corridor_rules.yaml` `metro_tiers` → A-screen-013; the only town names in the file are in the docstring example (line 12). Regeneration with seed 1 is byte-identical (section 1) |
| 4 | No single-point benefit/cost claim in R2 outputs; label present | **PASS** | grep for `will reduce|will transform|should build|BCR|NPV|SAR [0-9]|USD [0-9]|billion|cost.. (of|is|are) [0-9]` over `docs/screening.md`, `docs/candidates.md`, `docs/coverage.md`, `scenarios/S2–S5.yaml`: no match. Every corridor YAML carries `cost_status: 'uncosted: no cost range yet (W3); excluded from CBA until priced'` and `label: screening input, not a forecast; indicative sketch alignment, uncosted` (74/74). Label "screening input, not a forecast" in screening.md (2), candidates.md, coverage.md, S2–S5 (1 each) |
| 5 | Determinism test passes; no `data/`/`runs/` payloads tracked | **PASS** | `tests/test_screening_r2.py:153 test_corridors_deterministic_hypothetical_and_traceable` passes; corridor regeneration identical. `git ls-files` under `data/`, `runs/`, `movies/`, `film/renders`, `film/audio`: only `data/README.md`, `data/ksa/tables/README.md`, the GASTAT tables under `data/ksa/tables/gastat/` with README and `sources*.csv`, and the two railway tables (all pre-R2, allowed by the coordinator) |
| 6 | `make test` passes | **PASS** | exit 0, 14.9 s (section 1) |
| 7 | 10 % spot-check of register rows (populations traceable) | **PASS** | Seed `numpy.random.default_rng(20261031)`, 15 of 1,691 rows (section 3). 13 grid rows: `pop_grid_raw × grid_scale_factor` rounds to `population` in every case (e.g. Al Qasab 6,348 × 0.704045 = 4,469; Al Nawariyah 7,458 × 0.755422 = 5,634; Hadban 1,775 × 0.802786 = 1,425). 2 official rows equal the primary table (`census2022_TA1_city5k_primary.xlsx`): Abwalsle 6,316, Alhutuh 6,786. Full pass over all 224 `S-cp2-gastat-008` rows with a `primary_city`: 223 equal the table exactly; the one non-literal is the declared combination Alhufuf 430,105 + Almubriz 299,501 = 729,606 (correct sum). 13 created rows (`primary_match_tier = relay bridge (OSM extract)`): all 13 equal the primary table; the 12 Al-Ahsa rows are found in `data/ksa/regions-pilot/citypop-eastern-census2022.html` with the Arabic name adjacent to the figure (Aṭ-Ṭaraf 29,588, Al-ʿUmrān 22,781, Al-Jurn 20,329, Al-Jishah 11,482, Tuwaythir 9,700, Al-Qārah 8,656, Al-Markaz 8,392, Al-Manṣūrah 7,622, Al-Qurayn 7,339, Al-Ḥawaṭah 6,786, Al-Jafr 6,772, Ash-Shuqayq 5,092); Al Hilaliyah (Qassim, 5,120) equals the primary table (not an Eastern relay row). Relay-bridge matched rows: Thebea 17,502 in the HTML and the table; Alshazalah 11,560 equals the table; Al Ghuwaybah 5,139 equals the table and the figure is in the HTML, but the register spelling الغويبة is not (spelling variant; observation) |
| 8 | Added-section items | **PASS** | §2 (lines 15–101): 271 → matched 212 / created 13 / unmatched 46 (614,199 persons; 12 ≥ 10k), tier table, "Still unmatched, each with its population" table incl. Wadi Al Oqool farms 24,381 (line 56). §3 (lines 103–126): per-region ta1_total, matched_primary, residual, grid_universe, factor, before → after sums; `docs/coverage.md` per-region table repeats factors and before → after. `docs/sources/conflicts.md` lines 310–311: C-gastat-003 (9,022 / 9,022, 0.0 %, `census2022_TA1_city5k_primary.xlsx`, S-makkah-001) and C-gastat-004 (11,560 / 11,560, 0.0 %, `data/ksa/hail/citypop_hail_census2022.csv`); C-r2-001 Ghata (line 359). Blocked sweeps: MADINAH, NORTHERN_BORDERS (`--registers` glob added to `screening.geo_verify.cli`, run output under `runs/r2/geo_verify/estimate-northern_borders/`), AL_JOUF Ghata placed on node 1236744649 with C-r2-001, as stated in the R2 block |
| 9 | Registers: A- ids resolve; no fragments left; S- ids resolve | **PASS** | 27 distinct `A-*` ids in `screening/primary_match.py`, `screening/control_total.py`, `cities/ksa/assumptions/corridor_rules.yaml`, corridor `assumptions_used`: all present in `docs/assumptions.md`. 5 distinct `S-*` ids in `docs/screening.md`: all in `docs/sources/index.csv`. No `docs/assumptions-r2-<region>.md`, no `docs/licences-r2-*` tracked. `docs/assumptions-r2.md` (11 lines) is a pointer page owned by the brief ("You own"), rows live in `docs/assumptions.md`; `docs/sources/r2-*.csv` stay by `docs/versioning.md` §5 ("Per-track source CSVs ... are not fragments") |
| 10 | No model names in docs outside STATUS/status/cost-log; no home paths; no content from the author's company | **FAIL** (model names) | `grep -rn "/Users/[a-z]" $(git ls-files)` empty; the private-list terms grep hits only the prohibition sentences in CLAUDE.md, PROJECT.md, agent files and earlier verify reports; secrets grep empty; `git push` only in rule text and verify reports. Model names: exact ids in `docs/licences.md:11` and `docs/licences.csv:2` ("Claude Code / claude-fable-5-1, claude-opus-5-5, claude-haiku-5-5"); the label "Opus" in `docs/plan.md` ("Opus-class"), `docs/assumptions.md` ("Opus item 2", "Opus item 4"), `docs/gastat-regions.md`, 26 files under `docs/regions/*.md` ("Needs Opus judgement"), and `cities/ksa/regions/*.csv`. `docs/STATUS.md` line 67 (P5) made "Housekeeping (model ids in docs ...) in the first R2 commit" an R2 condition; `git log 10d954c..HEAD -- docs/plan.md docs/gastat-regions.md docs/licences.md` shows no such edit. R2-owned outputs (`docs/screening.md`, `docs/candidates.md`, `docs/coverage.md`, S2–S5, corridor YAMLs) are clean |
| 11 | Handoff: status line, STATUS.md CP3 list, cost-log row (brief task 6; procedure step 12) | **FAIL** | `grep -nE "R2: (done|blocked)" docs/status/main.md` → no match: the R2 block ends with the "Not done / could not verify" paragraph and has no `R2: done` line, no elapsed time and no cost pointer (brief task 6 requires "elapsed, cost pointer" and the end line; `_common.md` v1.2 / STATUS P5: a run without a status line is reported, not accepted). `docs/STATUS.md` (v1.11) has no R2 handoff block and no CP3 decision list (`grep -nE "CP3 decision|## CP3"` → none; the only CP3 mentions are the pre-R2 P5/CP2 notes at lines 67, 75–76); the milestone table row 17 still reads "pilot merged (PILOT_MERGE); full sweep not started"; open issue 121 still says 69 unmatched cities (R2 reduced it to 46). `docs/cost-log.md` has rows for the 13 REGION_* sweeps but none for the R2 main-checkout run (last row `r2-hail-REGION_HAIL-try1`); if the orchestrator appends it after the run closes, say so in the block |

Also checked (procedure steps 3, 10, 11): determinism confirmed by regeneration; planned/committed lines are not styled as existing in R2 outputs (corridor `connects_to` entries carry `layer:`); no advocacy phrasing found; every number in the R2 block that I re-measured matches (1,691 rows; 236 official / 27 derived / 1,385 grid / 43 none; 1,222 grid rows scaled; 74 YAMLs = 23/17/27/7; 21 decisions; 150 governorates; stability 23/30; tau 0.885/0.938; the 8 scale factors).

## 3. Spot-check sample (seed 20261031, `default_rng.choice(1691, 15, replace=False)`)

| region | name_en | population | pop_type | pop_source | check |
|---|---|---|---|---|---|
| riyadh | Alhamdiyah | 0 | grid | S-r1a-505 | raw 0 × 0.704045 = 0 ✓ |
| riyadh | Umm al Kabash | 862 | grid | S-r1a-505 | 1,224 × 0.704045 = 861.8 ✓ |
| riyadh | الفايزية | 0 | grid | S-r1a-505 | raw 0 ✓ |
| eastern | Al Haoutah (Alhutuh) | 6,786 | official | S-cp2-gastat-008 | primary table 6,786 ✓ (created row; HTML الحوطة 6,786 ✓) |
| jazan | Abu as Sala (Abwalsle) | 6,316 | official | S-cp2-gastat-008 | primary table 6,316 ✓ |
| riyadh | Al Qasab | 4,469 | grid | S-r1a-505 | 6,348 × 0.704045 = 4,469.3 ✓ |
| al_jouf | Al Jarawi | 0 | grid | S-r1a-505 | raw 0 ✓ |
| tabuk | رأس الخريطه | 48 | grid | S-r1a-505 | 48 × 1.0 ✓ (unscaled region) |
| al_jouf | Hadban | 1,425 | grid | S-r1a-505 | 1,775 × 0.802786 = 1,424.9 ✓ |
| riyadh | الحفنة | 467 | grid | S-r1a-505 | 664 × 0.704045 = 467.5 ✓ |
| riyadh | الشرمية | 96 | grid | S-r1a-505 | 137 × 0.704045 = 96.5 ✓ |
| makkah | Al Nawariyah | 5,634 | grid | S-r1a-505 | 7,458 × 0.755422 = 5,633.9 ✓ |
| riyadh | Nabwan | 54 | grid | S-r1a-505 | 77 × 0.704045 = 54.2 ✓ |
| riyadh | Al Barrah | 318 | grid | S-r1a-505 | 452 × 0.704045 = 318.2 ✓ |
| riyadh | Al `Adhar | 815 | grid | S-r1a-505 | 1,158 × 0.704045 = 815.3 ✓ |

15/15 consistent; `pop_source_status` is `unverified` on every grid row and `verified` on both official rows. No fabricated or misquoted figure found in the sample, the 13 created rows, the 3 relay-bridge rows or the full 224-row primary comparison.

## 4. Failures (exact evidence)

1. **Handoff incomplete (criterion 11).** `docs/status/main.md` R2 block has no `R2: done` / `R2: blocked` line (grep empty), no elapsed time, no cost pointer. `docs/STATUS.md` v1.11: no R2 block, no CP3 decision list, milestone table row 17 stale ("full sweep not started"), open issue 121 stale (69 → 46). `docs/cost-log.md`: no row for the R2 main run.
2. **Model names in docs (criterion 10).** `docs/licences.md:11`, `docs/licences.csv:2` (exact ids); "Opus" labels in `docs/plan.md`, `docs/assumptions.md`, `docs/gastat-regions.md`, 26 `docs/regions/*.md`, `cities/ksa/regions/*.csv`. STATUS P5 assigned this housekeeping to the first R2 commit; it was not done. (The licence-register row may deserve an explicit coordinator exemption as the register entry for the orchestrator tool; that is a decision to record, not a silent pass.)

## 5. Non-blocking observations

- 478 grid rows carry `population = 0` (3 of the 15 sampled); they are `unverified` and below every gate, but a zero WorldPop value usually means an empty cell at the point, not an empty place. Worth a line in `docs/candidates.md` §2 and the CP3 list.
- `docs/screening.md` §3 computes the scale factor on the **universe** grid sum (e.g. makkah 934,520) and applies it to the **register** grid rows (469,190 → 354,437). The method sentence says so; the brief's wording ("the region's WorldPop-filled settlement populations") admits either reading. Record the choice as part of A-screen-040's text so the CP3 reader does not have to infer it.
- Al Ghuwaybah (`eastern:node:11870738714`): the relay HTML holds 5,139 but not the register spelling الغويبة; the primary table matches, so the figure is sound.
- `docs/sources/r2-*.csv` (13 files) and `docs/assumptions-r2.md` remain tracked by design (`docs/versioning.md` §5; brief "You own"); the status wording "Fragments deleted" is accurate for the assumptions/licences fragments only.
- `screening/sweeps/*` scripts still write fragment paths (builder's own note); `docs/licences.csv` row 179 has more cells than the header (pre-existing, builder's note).
- pytest summary line suppressed by configuration: the pass count in status blocks cannot be confirmed from `pytest -q` output alone.
- `docs/coverage.md` v2.0 and `docs/candidates.md` v1.0 are `Status: draft`; fine before CP3, but they should move to `reviewed` once the coordinator accepts the CP3 list.

## 6. Three most important fixes

1. Close the handoff: append `R2: done` (with elapsed and the cost-log pointer) to the R2 block in `docs/status/main.md`; add an R2 block and the CP3 decision list (short list 60, four families 23/17/27/7, thresholds confirmed, 46 unmatched cities, 8 scale factors, 478 zero-population rows) to `docs/STATUS.md`; update milestone row R2 and open issue 121; add the cost-log row.
2. Do the P5 model-label housekeeping across `docs/` (or record a dated coordinator decision exempting the licence-register row and the historic "Needs Opus judgement" notes in the region docs, and reword the rest).
3. State in A-screen-040 / `docs/screening.md` §3 that the factor denominator is the universe grid sum, and list the 478 zero-population grid rows as a CP3 item.

Pass 1 verdict (HEAD fe85d0e): FAIL (failures 1 and 2 above).

---

# Pass 2 (HEAD af784f5, main checkout; 31 Oct 2026)

Scope per the coordinator: re-check the two pass-1 failures (F1 handoff, F2 model labels), confirm nothing regressed. Read-only. Working tree at start: `git status --porcelain` = ` M scenarios/S2.yaml`, ` M scenarios/S3.yaml`, ` M scenarios/S4.yaml`, ` M scenarios/S5.yaml` (see F3).

## P2.1 Commands run

| command | exit | evidence |
|---|---|---|
| `make test` (ruff, pytest, docver, manifest) | 0 | 16.9 s wall; "docver OK: 260 files"; "manifest OK: 307 rows" |
| `uv run python -m common.scenarios validate scenarios/` | 0 | "ok 6 scenario files" (working tree); also 0 / "ok 6" on the HEAD-committed copies extracted to `/tmp/r2v2/head-scen` (the validator does not check the `source:` hash) |
| `uv run python -m screening.corridors validate` | 0 | "ok 74 corridor files" |
| `for f in cities/ksa/regions/*.parquet; do uv run python -m screening.region_sweep validate --strict $f; done` | 13 of 26 pass, 11 fail | the 13 R2 registers (`al_baha, al_jouf, asir, eastern, hail, jazan, madinah, makkah, najran, northern_borders, qassim, riyadh, tabuk`) all pass `--strict`; the 11 failures are all `pilot-*.parquet` ("header lacks governorates_gastat, governorates_listed" or a non-integer `governorates_gastat`). Pre-existing, not a regression: the same files fail identically when extracted from fe85d0e and from 10d954c (pre-R2). They are the PILOT_MERGE inputs for `candidates-pilot.parquet` and are excluded from the R2 merge (`screening/merge.py --exclude 'pilot-*'`); `pilot-asir` and `pilot-makkah` were not expected to carry the R2 header |
| `uv run python -m screening.corridors generate --seed 1 --run-dir /tmp/r2v2/regen --out /tmp/r2v2/regen/out --scenarios /tmp/r2v2/regen/scen` | 0 | counts 23/17/27/7, 21 decisions; `diff -r` against `cities/ksa/corridors` = 74 files identical; regenerated S2–S5 identical to the **working-tree** `scenarios/S2–S5.yaml` after the output-path prefix is normalised, but **not** to the HEAD-committed copies (one line each, see F3) |
| `git grep -n -w -E "Opus|Haiku|Hanko|Fable" -- docs cities ':!docs/STATUS.md' ':!docs/status' ':!docs/cost-log*'` | hits in one file | `docs/plan.md` only (lines 13, 93–104, 107, 110: the §6 run table and the cost estimate). `docs/assumptions.md`, `docs/gastat-regions.md`, `docs/regions/*.md`, `cities/ksa/regions/*.csv` and the Parquet `notes` are clean |
| `git diff fe85d0e af784f5 --stat` | | 143 files: 74 corridor YAMLs (2 lines each), region CSV/Parquet, `docs/regions/*.md`, `docs/assumptions.md`, `docs/gastat-regions.md`, `docs/licences.*`, `docs/sources/*`, `docs/STATUS.md`, `docs/status/main.md`, `docs/status/verify-R2.md`, `candidates*.parquet`, `candidates-pilot-r1a.parquet`. Spot-check of 2 corridor diffs (`S2-trunk_gap-riyadh-jeddah.yaml`, `S4-commuter_belt-jeddah-000.yaml`): only the `source:` line, `candidates.parquet 2f1a756a066b` → `0fb14aee9e68`. Sample of `cities/ksa/regions/qassim.csv`: the non-"Opus" line changes are the regenerated rows (notes text), no population or coordinate change found in the sample |

## P2.2 Re-check of the pass-1 failures

| # | item | result | evidence |
|---|---|---|---|
| F1 | Handoff: STATUS.md R2 milestone row, "### R2 decisions", "### CP3 decision list", open issue 69 → 46; main.md R2 block with elapsed and cost pointer | **PASS** | `docs/STATUS.md` v1.12: line 17 milestone row R2 "done on `main` (verifier: `docs/status/verify-R2.md`); CP3 next; 1,691 register rows, long list 189, short list 60, 74 corridors"; line 80 `### R2 decisions (screening-analyst on main, 31 Oct 2026)`; line 90 `### CP3 decision list`; line 139 open issue "R2 placed 225 of the 271 primary cities (212 matched, 13 created); **46 remain unmatched (614,199 persons, 12 ≥ 10,000)**" with the CP2_PREP 69-city text kept as history. `docs/status/main.md` line 231 `## R2 national screening`, line 250 "Elapsed: about 17:00 to 18:00 +03. Cost: the 13 REGION_* runs logged USD 53.68 list (`docs/cost-log.md`); this run's row is appended by `run_track.sh` when it ends (R2 cap USD 90, alert at 72)". The plain-text `R2: done` line and the cost-log row for the main run are absent, as the coordinator said to expect (builder appends the line after PASS; `run_track.sh` appends the row; precedent INTEGRATE_R1, CP2_PREP) |
| F2 | Model labels outside STATUS / `docs/status/` / cost-log | **PASS with a recorded exemption** | Grep above: only `docs/plan.md` remains. The builder recorded the exemption in `docs/STATUS.md` line 88 ("Left for the coordinator: `docs/plan.md` §6 run table ... and the Claude Code licence row (the existing CP2_PREP exemption in `tests/test_cp2_housekeeping.py`)") and as CP3 item 6 (line 96). Judgement: acceptable for R2. `docs/plan.md` is the coordinator's internal run plan (`Status: draft (for Checkpoint 1 ...)`), it uses labels not ids, and the brief's rule (CLAUDE.md "Machine and models") forbids model names in regulator- or public-facing documents; plan.md is neither, and it is the same class of record as the cost log. The licence-register row is the register entry for the orchestrator tool and is already an explicit allow-list entry in `tests/test_cp2_housekeeping.py:44`. Condition for later milestones, not R2: the repository is published at R9, so at R9 either Tariq confirms the exemption (CP3 item 6) or the §6 table is reworded; the housekeeping test only matches exact ids (`claude-(fable|opus|haiku|sonnet)-\d`), so it will not catch a reintroduced label |

## P2.3 New failure found in pass 2

**F3. Committed `scenarios/S2–S5.yaml` cite a candidates hash that no longer exists in the repository (regression introduced by af784f5).**

- `shasum -a 256 cities/ksa/candidates.parquet` = `0fb14aee9e68...` (file unchanged vs HEAD; `screening/corridors.py:147` uses the first 12 hex characters).
- `git show HEAD:scenarios/S2.yaml | grep -o "candidates.parquet [0-9a-f]*"` → `candidates.parquet 2f1a756a066b` (same in S3, S4, S5).
- `git show HEAD:cities/ksa/corridors/trunk_gap/S2-trunk_gap-riyadh-jeddah.yaml` → `candidates.parquet 0fb14aee9e68` (all 74 corridor YAMLs were updated in af784f5; `git diff fe85d0e af784f5 --stat` lists no `scenarios/` file).
- Seed-1 regeneration (P2.1) reproduces the 74 corridors byte-for-byte and the **working-tree** S2–S5 exactly, but differs from the **HEAD-committed** S2–S5 by exactly that `source:` line in each file. The four uncommitted ` M scenarios/S*.yaml` edits are the regenerated, correct files that the chain re-run produced and the builder did not stage.
- Why it is a FAIL and not an observation: pass-1 criterion 3 ("reproducible"; regeneration identical to committed) no longer holds at HEAD; rule 10 / `docs/versioning.md` make the `source:` hash the link from a scenario file to the tracked data; the `r2` tag would freeze four scenario files that cannot be traced to any tracked `candidates.parquet`; and `git status --porcelain` is not clean (procedure step 4). The fix is one commit (`git add scenarios/S2.yaml scenarios/S3.yaml scenarios/S4.yaml scenarios/S5.yaml` and commit), after which `git diff HEAD --stat` must be empty and `git show HEAD:scenarios/S2.yaml` must cite `0fb14aee9e68`. A FAIL is not softened because the fix is small.

## P2.4 Regression check summary

- No regression in tests, lint, docver, manifest, scenario or corridor validation, or the 13 R2 region registers (all `--strict` clean).
- The 11 `pilot-*.parquet` strict failures pre-date R2 (identical at 10d954c) and are outside the R2 merge; they are noted here so the next pass does not re-discover them. Recommended (non-blocking): either give the pilot registers the R2 header or document in `docs/regions/README`/`screening/region_sweep.py` that `--strict` applies to R2 registers only.
- Register `notes` edits in af784f5 are text-only in the sampled rows; population and coordinate values were not changed in the sample (qassim.csv). Pass-1 spot-check figures (section 3) stand, since `candidates.parquet` is byte-identical between the pass-1 regeneration input and HEAD for the fields checked (the Parquet grew by 255 bytes from notes text).

## P2.5 Three most important fixes (pass 2)

1. Commit the four regenerated `scenarios/S2–S5.yaml` so the committed `source:` line cites `candidates.parquet 0fb14aee9e68`, matching the tracked file and the 74 corridor YAMLs; then re-run `uv run python -m screening.corridors generate --seed 1 ...` and confirm the regenerated S2–S5 equal HEAD. This is the only open item.
2. At CP3, put the `docs/plan.md` §6 model-label exemption (STATUS line 88 / CP3 item 6) to Tariq explicitly; before R9 either reword the table or record his approval in STATUS.
3. Non-blocking: declare the scope of `region_sweep validate --strict` (R2 registers) or upgrade the `pilot-*` headers, so the full-directory loop runs clean.

Pass 2 verdict: FAIL (F3 open; superseded by pass 3 below).

## Pass 3 (31 Oct 2026, HEAD de5a9b1; scope limited to F3 re-check as instructed by the coordinator)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Working tree clean | PASS | `git status --porcelain` -> empty, rc 0 (before this file was edited) |
| 2 | Committed S2-S5 cite the tracked candidates hash | PASS | `shasum -a 256 cities/ksa/candidates.parquet` -> `0fb14aee9e68...c3c0e4`; `git show HEAD:scenarios/S2.yaml` line 106, `S3.yaml` line 125, `S4.yaml` line 93, `S5.yaml` line 49 each read `... from candidates.parquet 0fb14aee9e68, scores.parquet`; prefix matches |
| 3 | Scenario validation | PASS | `uv run python -m common.scenarios validate scenarios/` -> `ok 6 scenario files`, rc 0, 0.41 s |

F3 is closed by commit de5a9b1 (`fix(scenarios): commit regenerated S2-S5 (candidates hash 0fb14aee9e68)`). F1 and F2 were closed in pass 2 and were not re-opened. No new findings. The two non-blocking recommendations from pass 2 (CP3 model-label exemption in `docs/plan.md` section 6; scope of `region_sweep validate --strict`) stand as recommendations, not FAILs.

VERDICT: PASS
