> **Document version:** docs/status/verify-INTEGRATE_R2.md v1.1 | 31 Oct 2026 | Author: red-team-verifier (claude-fable-5-1, read-only); pass 2 at 811202e appended | Status: reviewed

# Verification: INTEGRATE_R2 (CP3 item-4 fix, zero-row drop, housekeeping, integration audit)

Scope: `main` at 98ef304 (2026-10-31 18:27:57 +03); commits since the CP3 record b2655d2: 47945e0, 8af22be, 4a8292d, 98ef304. Brief: `prompts/INTEGRATE_R2.md` v1.2 (acceptance list and the "Added 31 Oct 2026 18:30" items 1–5), `docs/STATUS.md` v1.14 (CP3 and INTEGRATE_R2 decisions), `docs/screening.md` v1.1 §2, §2a, §3, §8, `docs/status/verify-R2.md` (the 13 merges were passed there and are not re-audited). Nothing was fixed. Working tree clean before and after this audit (`git status --porcelain` empty; one side effect of my own, disclosed in §6, was restored to HEAD).

## 1. Commands (exit codes and timing)

| command | result | exit | time |
|---|---|---|---|
| `uv run ruff check .` | All checks passed! | 0 | 0.11 s |
| `uv run ruff format --check .` | 481 files already formatted | 0 | 0.03 s |
| `uv run pytest -q` | 318 collected (`--collect-only` sum), 318 passed, 0 failed (dots only; 311 at R2 + 7 in `tests/test_integrate_r2.py`) | 0 | 16.2 s wall |
| `uv run python -m common.docver check` | docver OK: 260 files | 0 | 0.10 s |
| `uv run python -m common.manifest verify` | manifest OK: 308 rows | 0 | 1.08 s |
| `uv run python -m common.licences check` | 210 Markdown rows, 210 CSV rows, 0 differ | 0 | 0.05 s |
| `uv run python -m common.cost_log check` | cost log OK: 45 rows | 0 | — |
| `make test` (lint, pytest, docver, manifest) | green | 0 | 17.8 s wall |
| README demo (`network.skims --backend osmnx --pbf data/osm/jeddah.osm.pbf --zones tests/fixtures/zones.geojson --seed 1`, written to `/tmp/verify-demo/skims1/`) | 6 zones, 36 pairs, 0 unreachable, 1.28 s | 0 | 2.09 s wall |
| `./screening/run_r2.sh 1` (determinism re-run, log `logs/verify-INTEGRATE_R2-run_r2.log`, gitignored) | EXIT=0; `git status --porcelain` empty afterwards | 0 | 11.95 s wall |

## 2. Criteria

| # | criterion | verdict | evidence |
|---|---|---|---|
| A1 | every R2 branch merged `--no-ff`; no history rewriting since b2655d2 | PASS | `git log --merges`: 13 merge commits 9114a96 (al_baha) … 109a915 (tabuk), one per `r2-<slug>` branch (`git branch --list 'r2*'` = 13); the 4 commits after b2655d2 are plain commits (`git reflog`: only `commit:` entries, no reset/rebase/amend); b2655d2 is an ancestor of HEAD |
| A2a | `docs/assumptions.md` superset: A-r2-003/004 added, A-r2-001 extended, no ids removed | PASS | `comm` of `^\| A-` ids b2655d2 vs HEAD: 0 removed, 2 added (A-r2-003 line 220, A-r2-004 line 221); A-r2-001 line 218 carries "Extended at INTEGRATE_R2 (CP3 4a …)"; header v1.14 |
| A2b | `docs/licences.csv/.md` same row count as b2655d2, every row 11 cells, `licences check` clean | PASS | 211 lines (header + 210) at both b2655d2 and HEAD; `csv.reader` cell count `Counter({11: 211})`; `licences check` 0 differ; diff vs b2655d2 = 2 rows changed in place (OSM `used_in`; World Bank WDI obligations cell re-quoted), no row added or removed |
| A2c | `docs/sources/index.csv` no ids removed; `index.md` regenerated | **FAIL (F3)** | CSV: 1,816 lines at both commits, 0 ids removed, 1 row changed (S-qassim-003 `used_in` += `screening/primary_match.py …INTEGRATE_R2`). `docs/sources/index.md` was **not** regenerated: unchanged since b2655d2 (`git diff --stat b2655d2..HEAD` lists no `index.md`); `grep -c primary_match` on its S-qassim-003 row = 0; running `scripts/regen_sources_index_md.py` produces a 1-line diff (restored, §6) |
| A2d | `cities/ksa/sources.yaml`: one new row `osm-gcc-place-areas-extract-2026-10-14`; manifest verifies | PASS | `git diff b2655d2..HEAD` = exactly that row (ODbL-1.0, 35,635,762 bytes, sha256 54dc1d44…adfa0b3); `shasum -a 256 data/ksa/osm/gcc-place-areas.geojsonseq` = 54dc1d44…adfa0b3, `ls -l` 35635762; 307 → 308 ids, none removed; `manifest verify` OK 308 |
| A3 | `make test` and README command pass on main | PASS | §1 |
| A4 | `docs/STATUS.md` reflects the merged state with measured numbers; carries every blocker and conflict | **FAIL (F2)** (milestone row and decisions PASS; header and handoff pointer FAIL) | Milestone row line 18 re-measured: 1,224 register rows (parquet), long list 198 / short list 60 / 76 corridors (`ls cities/ksa/corridors/*/` = 76 YAML; S2 23, S3 17, S4 27, S5 9 by scenario file refs ÷ 2), 33 known unplaced (222,950 persons; 1 ≥ 10k) (`primary_cities.csv`), 11 of 12 placed, Jubail IC rank 16 and Al Jubayl #2 (`check.json`) — all match. Decisions block lines 110–116 and open issues lines 159, 161, 162 present. No merge conflict or blocker existed in this run. **But** line 5 "Last updated" still names INTEGRATE_R1; line 7 disk 52 GiB vs `df -h ~` 49 GiB now; line 8 cost "284.53 over 29 runs … before the INTEGRATE_R1 row" vs `cost_log summary` 402.47 USD over 45 runs (prompt task 5 asks for disk free and cost so far from `summary`); line 18 points to "`docs/status/main.md` (INTEGRATE_R2 block)" which does not exist (`grep -n INTEGRATE_R2 docs/status/main.md` → only the CP2_PREP line 221; file ends `R2: done`, no `INTEGRATE_R2: done`) |
| B1 | Jubail Industrial City (172,233) its own row, `official`/`verified`, not folded into Al Jubayl | PASS | `candidates.parquet` row 1200 `eastern:node:1237806971` "Al Jubayl Royal Commission" 172,233 `official` `verified` `S-cp2-gastat-008` 27.0761 N 49.5903 E; row 116 `eastern:node:38903292` "Al Jubayl" 302,446 `official` `verified`; OSM extract: node 1237806971 `place=locality`, name اللجنة الملكية في الجبيل, `name:en` Al Jubayl Royal Commission at [49.590278, 27.076111] — the only object with that name in both extracts |
| B2 | Jubail rank before/after and S2–S5 changes reported | PASS | `runs/integrate_r2/check/check.json`: Al Jubayl r2 score 0.9194 rank 2 (2–2) → final 0.9196 rank 2 (2–2); JIC rank 16 (6–22), short list; `docs/screening.md` §2a table and corridor paragraph (added `S5-station_addition-al-jubayl-royal-commission`, `S5-…-banban`, `S3-branch_spur-yanbu`, `S4-…-riyadh-315`; removed 2; changed 2); `scenarios/S5.yaml` lines 23/33 reference the new file; `cities/ksa/corridors/station_addition/S5-station_addition-al-jubayl-royal-commission.yaml` exists, `layer: hypothetical`, alignment point [27.07611, 49.59028] |
| B3 | the other 11 ≥ 10k cities placed with evidence + seat check, or "known, unplaced" | PASS | `primary_cities.csv`: matched 214 / created 24 / unmatched 33; the 12 R2-unmatched ≥ 10k resolve as: Arqa, Alkalabiuh, Almunayzilh, Albitaliuh, Alhaliluh (relay bridge OSM extract), Alqawz (relay bridge, existing row), Wadi Al Oqool farms, Alulya, Benban, Alhasma (judgement, `primary_match_decisions.yaml` v1.1), Jubail IC (judgement); Iiskan Alkalabiuh 12,817 "known, unplaced" in `docs/screening.md` §2 table and STATUS line 159. `runs/integrate_r2/geo_verify/seat-*`: 13 directories (the 11 + Alramiluh + Alshaquh Aleulya), every `method_log.jsonl` `inside: True` with governorate polygon id; `meta.json` seed 1 |
| B4 | spot-check ≥ 4 placements against the source files; factual claims true | PASS (one wording slip, O1) | §3 |
| B5 | Ghata and the Al-Ahsa OSM-created rows flagged `derived` | PASS | `al_jouf:node:1236744649` Ghutti 6,653 `derived`/`verified`; all 20 "relay bridge (OSM extract)" created rows `derived` (12 Al-Ahsa incl. At Taraf 29,588, Al `Umran 22,781, Al Munayzala, Al Battaliyah, Al Hulaylah …); judgement rows `derived` except JIC and Dariyah `official` as A-r2-004 states; register totals official 224 / derived 51 / grid 906 / none 43 = 1,224 (matches §3) |
| C1 | 478 zero-population grid rows dropped from candidates, kept in settlements | PASS | `runs/r2/control_total/dropped_zero_grid.csv` 478 rows (riyadh 393, tabuk 64, al_jouf 21); 0 of their `row_key`s in `candidates.parquet`; all 478 `osm_id`s in `settlements.parquet` (7,371 rows) with `grid_population == 0`; candidates `pop_grid_raw == 0` count 0 |
| C2 | row count and rank changes reported (none expected) | PASS | `check.json` `register_rows` 1691 → 1702 → 1224; `drop_vs_item1`: long list 198 = 198, short list 60 = 60, `rank_changed: 0`; `docs/screening.md` §2a last sentence; `docs/candidates.md` line 5 |
| C3 | coverage still 150 = 150, 0 governorates without a row | PASS | `docs/coverage.md` line 180: "governorates in table = 150; governorates_gastat = 150 (S-cp2-gastat-007); regions = 13 of 13; register rows = 1224 … 0 unmapped; governorates with no register row = 0; governorates excluded = 0" |
| D1 | `docs/licences.csv` no row with the wrong cell count | PASS | A2b |
| D2 | 13 pilot registers archived with README; every code path repointed | PASS | `cities/ksa/regions/archive/pilot/`: 13 `.parquet` + 13 `.csv` + 2 build scripts + `README.md` v1.0; `git diff b2655d2..HEAD` shows 14 path constants/defaults repointed in `screening/{merge,region_sweep,pilot_normalise,gastat,cp1_fixes/apply,geo_verify/cli}.py`, `run_pilot_funnel.sh`, 5 `sweeps/*/build.py`, `tests/test_region_sweep.py`; the remaining `regions/pilot-` hits outside `pilot_builders/` and the archive are docstrings and prose strings only (`sweeps/{al_jouf,eastern,najran,riyadh}/build.py` lines 4–9, `eastern/build.py:569`, `najran/write_docs.py:249`, `jazan/geo_estimates.py:4`, `qassim/geo_nopop.py:5`), no file read |
| D3 | 13 national registers pass `region_sweep validate --strict` | PASS | all 13 print `ok` (al_baha 16 rows/10 gov … riyadh 1096/23, tabuk 119/7) |
| E1 | CP3 approvals recorded (A-screen-006, -040, A-corr-001…015, A-r2-001/002) and 7a exemptions in STATUS | PASS | `docs/assumptions.md`: A-screen-006 "approval: Tariq, 31 Oct 2026 (CP3 2a)", A-screen-040 "(CP3 5a)", 15 A-corr rows "(CP3 6a)", A-r2-001/002 "(CP3 4a)"; STATUS lines 99–108 (CP3) and 111 (INTEGRATE_R2: approvals and the 7a exemptions `docs/plan.md` §6, Claude Code licence row); `tests/test_cp2_housekeeping.py` line 44 allows exactly STATUS, cost-log, licences.md |
| E2 | per-region scale factors and the Jubail check in `docs/screening.md` | PASS | §3 table: 13 regions with `grid_scale_factor` vs `factor_at_r2` (e.g. riyadh 0.6294 vs 0.704, eastern 0.8527 vs 1.0); §2a Jubail table |
| F1 | determinism: `run_r2.sh 1` regenerates tracked outputs byte-identically | PASS | sha256 of `cities/ksa/candidates.parquet`, `docs/coverage.md`, `docs/screening.md`, `docs/candidates.md`, `scenarios/S2–S5.yaml` recorded before and after: identical (8/8); `git status --porcelain` empty after the run |
| F2 | run `meta.json` records seed, config hash, data hash, code version | PASS | `runs/r2/score/meta.json` and `runs/r2/corridors/meta.json`: seed 1, config_hash, data_hash 57d7e5b6…, code_version `r2-5-g98ef304`, label; `runs/integrate_r2/geo_verify/seat-*/meta.json` same fields (code_version `r2-1-gb2655d2-dirty`, O4) |
| F3 | labels present | PASS | "screening input, not a forecast": `docs/screening.md` (2), `docs/candidates.md`, `docs/coverage.md`, `scenarios/S2–S5.yaml` (2 each), every corridor YAML header, `check.json` `label` |
| F4 | no absolute home paths, secrets, `git push`; no content from the author's company; no model names in public docs changed since b2655d2 | PASS | `grep -rn "/Users/[a-z]" $(git ls-files)` empty; secrets grep empty; `git push` grep over tracked `.sh/.py/Makefile` empty; the private-list terms only in the rule texts of PROJECT.md and agent files; model ids in changed docs only in the Claude Code licence row (7a exemption); `git ls-files data runs movies film/renders film/audio` = READMEs and the GASTAT tables committed at CP2_PREP (pre-existing, registered) |
| F5 | no planned line styled as existing | PASS | all 76 corridor YAMLs `layer: hypothetical` with "(hypothetical)" in `name_en`; the 17 `layer: existing` / 9 `layer: committed` strings inside them are the base-line references, not the corridors |
| F6 | no unflagged assumption: PLACE_RANK, DERIVED_TIERS, drop rule registered | **FAIL (F1)** | `screening/primary_match.py` line 76 PLACE_RANK → A-r2-003 (register line 220); line 74 DERIVED_TIERS → A-r2-004 (line 221). The CP3 5a drop rule (`control_total.drop_zero`, `--drop-zero-grid` default in `run_r2.sh`) has **no row** in `docs/assumptions.md`: `grep -iE "zero-population|drop-zero|zero grid|raw WorldPop value of 0"` returns nothing; A-screen-040's "(CP3 5a)" is the approval of the scaling rule, its text does not mention the drop. The rule is documented only in STATUS line 114, `screening.md` §1 step 3, the code docstring and CHANGELOG |

## 3. Spot-checks

Sources opened: `data/ksa/pilot-qassim/raw/citypop_cities.html` (88,977 bytes, 30 Oct 21:31), `data/ksa/regions-pilot/citypop-eastern-census2022.html` (63,386 bytes), `data/ksa/osm/gcc-places.geojsonseq` (6,798,730 bytes), `data/ksa/osm/gcc-place-areas.geojsonseq` (35,635,762 bytes); every id/name looked up by parsing the GeoJSON-seq lines.

**National relay page (the six figures named in the brief), each found exactly once with the cited name and region code:** 'Irqah / عرقة RYD 42,179; Mazāri' Wādī al-'Uqūl [Wadi al-Aqool Farms] / مزارع وادي العاقول MDM 24,381; Al-Qūz / القوز MKM 22,374; Al-Kulābiyah / الكلابية SHQ 21,992; Al-Munaīzilah / المنيزلة SHQ 21,346; Al-'Ulāyah / العلاية ASI 20,250 (2010 column 19,956, as the Alulya evidence says).

**Eastern relay page, each once, all "Place, Al-'Aḥsā'":** Aṭ-Ṭaraf 29,588; Al-'Umrān 22,781; Al-Kulābiyah 21,992; Al-Munaīzilah 21,346; Al-Jurn [Al-Gorn] 20,329; Al-Baṭaliyah 15,146; Āskān al-Kulābiyah / اسكان الكلابيه 12,817; Al-Ḥulaylah 12,337; Ar-Rumaīlah 9,741; Ash-Shaqīq 5,092.

**OSM extracts, cited objects (type, name, coordinates as in the evidence):** node 1237806971 locality اللجنة الملكية في الجبيل [49.590278, 27.076111]; node 38903292 city الجبيل [49.653216, 27.000697]; node 1236703756 neighbourhood عرقة; node 1236702237 suburb بنبان [46.588056, 25.001667]; node 1236702180 locality بنبن; node 1237961320 village الحصمة / Al Hasamah [42.971389, 16.834444]; node 1236691814 village العاقول [39.7779, 24.5322]; node 12830607203 neighbourhood العاقول [39.7149, 24.5170]; node 1236690508 city سبت العلاية (`alt_name:ar` العلاية); ways 1566620126 village الكلابيه, 671079959 neighbourhood المنيزلة, 958521889 neighbourhood البطالية, 958034613 neighbourhood الحليلة, 1299457406 suburb الشقة العليا — all present as MultiPolygons in the areas extract.

**Factual claims in the evidence texts, re-computed:**
- Jubail IC: node → Al Jubayl node 10.45 km (text "10.4 km NW": bearing N and W, true); node → mean of the 14 district representative points (27.1155 N, 49.5542 E per `jic.json`) 5.65 km (text 5.7 km NNW, true); "only OSM place named for the Royal Commission": 1 object in nodes, 0 in areas (true); seat check inside Al Jubayl Governorate, 0.7 km from its boundary (O3).
- Benban: "only OSM place named بنبان": 1 (true); بنبن locality 1236702180 exists (true).
- Wadi Al Oqool: "two places named العاقول in Madinah region": 3 nationally, the third (node 747667429) at 43.87 E 26.26 N is in Qassim (true).
- Alulya: "the only Asir place with that name": the only other العلاية node (1721860049) is at 57.44 E 23.39 N (Oman) (true); grid 7,594 / 20,250 = 0.375 (true).
- Alhasma: "الحصمة is the only exact spelling": 1 (true); حسمى two Tabuk nodes (village + locality at 35.8 E, 28.5–28.8 N, true); الحصيمة one Jazan neighbourhood (true); الحسمة one hamlet (true); الحسام two neighbourhoods (true); ال هيصم one hamlet (true); **الحصامة "three Jazan villages/hamlets": the extract has four (3 villages + 1 hamlet)** (O1); 3,055 / 13,028 = 0.234 (text 0.23, true); the "mapped residential areas إسكان الحصمة and قرية الحصمة" are not place objects and cannot be checked from these extracts (unverified, not contradicted).
- Ghata: 2,048 / 6,653 = 0.308 (text 0.31, true).
- Iiskan Alkalabiuh: no object named اسكان الكلابيه / اسكان الكلابية / إسكان الكلابية in either extract (the "known, unplaced" reason is true).

**Random 10 % of the 24 created rows (seed 20261031, `random.sample(range(24), 3)` → indices 7, 9, 23):**
| row | figure in source | OSM object | register row | result |
|---|---|---|---|---|
| Aljurn 20,329 (relay bridge, OSM extract) | eastern relay: Al-Jurn [Al-Gorn] الجرن 20,329, Al-'Aḥsā' | node 1237339379 neighbourhood الجرن [49.6209, 25.5134] | `eastern:node:1237339379` Al Jarn, governorate Al-Ahsa, 20,329 `derived`/`verified`, sources S-cp2-gastat-008 + osm-gcc-places-extract | PASS |
| Alhasma 13,028 (judgement) | TA1 figure (S-cp2-gastat-008); claims checked above | node 1237961320 village الحصمة | `jazan:node:1237961320` Al Hasamah, Ahad Al Masarihah, 13,028 `derived`/`verified`; universe grid 3,055; seat inside (1.37 km to boundary) | PASS (O1 wording) |
| Alshaqiq 5,092 (relay bridge, OSM extract) | eastern relay: Ash-Shaqīq الشقيق 5,092, Al-'Aḥsā' | node 1237339408 neighbourhood الشقيق [49.5758, 25.4829]; 6 places share the name nationally, this is the one inside Al-Ahsa | `eastern:node:1237339408` Ash Shuqayq, Al-Ahsa, 5,092 `derived`/`verified` | PASS |

Live WebFetch re-verification was not needed: every figure traces to the archived relay pages (registered relays, D11a) or the TA1 export already verified at CP2_PREP/R2, and the OSM objects to the manifest-hashed extracts.

## 4. Failures (exact evidence)

- **F1 — zero-row drop rule not in the assumptions register (criterion F6).** `screening/control_total.py` lines 89–92 (`drop_zero`: grid rows with `pop_grid_raw == 0` leave the register) and `screening/run_r2.sh` line 14 (`DROP_ZERO` default 1) implement a behavioural rule that changes the register from 1,702 to 1,224 rows, approved by Tariq (CP3 5a). `docs/assumptions.md` v1.14 has no row for it (grep for "zero", "drop-zero", "raw WorldPop value of 0" over the register: no hit; A-screen-040 line 302 describes scaling only). CLAUDE.md engineering rules and the `assumptions-register` skill line 11 require a register row; A-r2-004, a comparable Tariq-decided rule, was registered, so the register is now inconsistent about what the CP3 5a decision did.
- **F2 — STATUS header and handoff pointer (criterion A4).** `docs/STATUS.md` line 5 "Last updated … (INTEGRATE_R1 …)"; line 7 "52 GiB free" vs 49 GiB measured (`df -h ~`, 31 Oct 18:4x); line 8 "284.53 over 29 runs … before the INTEGRATE_R1 row" vs `cost_log summary` TOTAL 45 runs, USD 402.47; line 18 cites "`docs/status/main.md` (INTEGRATE_R2 block)" and "verifier `docs/status/verify-INTEGRATE_R2.md`", but `docs/status/main.md` (254 lines) has no INTEGRATE_R2 block and ends `R2: done`. Prompt task 5 lists "disk free, cost so far from `uv run python -m common.cost_log summary`" and task 6 the status block ending `INTEGRATE_R2: done`. (Task 6 is sequenced after this verifier, so the block itself may legitimately follow; the dangling pointer and the stale header lines in a commit titled "update status" are the FAIL.)
- **F3 — `docs/sources/index.md` not regenerated after the CSV edit (criterion A2c).** `docs/sources/index.csv` row S-qassim-003 gained `screening/primary_match.py (national relay page …, INTEGRATE_R2)` in `used_in` (commit 4a8292d); `docs/sources/index.md` line 245 still shows the old `used_in`; `scripts/regen_sources_index_md.py` yields a one-line diff. `docs/versioning.md` and INTEGRATE task 3 make the CSV canonical and the Markdown generated; the two files disagree on one row.

## 5. Observations (non-blocking)

- O1: Alhasma evidence (decisions YAML and `docs/screening.md` §2) says الحصامة = "three Jazan villages/hamlets"; the places extract holds four (3 villages, 1 hamlet). The placement conclusion is unaffected.
- O2: `uv run python -m common.assumptions check` (named in the `assumptions-register` skill line 31) does not exist (`No module named common.assumptions`); pre-existing, already listed in STATUS line 171.
- O3: the Jubail Industrial City node sits 0.7 km inside the Al Jubayl governorate polygon (seat log); the actual industrial city extends north-west of it. Fine for a point placement; R3/R4 should not read the node as the city's extent.
- O4: `runs/integrate_r2/geo_verify/seat-*/meta.json` carry `code_version: r2-1-gb2655d2-dirty` (run before the commits); the R2 chain metas carry `r2-5-g98ef304` (clean; refreshed by my determinism re-run, which rewrote the gitignored `runs/r2/` with identical tracked outputs).
- O5: the settlement-universe row for Sabt Al 'Alayah (node 1236690508) carries `population 200000, pop_type derived` (an OSM tag) while the register now holds 20,250 `derived`/`verified` from TA1; R3 must read the register, not the universe, for that row.
- O6: `scripts/regen_sources_index_md.py` takes no arguments and regenerates on any invocation (including `--help`), which is how my side effect in §6 arose.
- O7: the cost-log row for the INTEGRATE_R2 run is not yet present (last row `main-R2-try1`); `run_track.sh` appends it at run end, as in earlier milestones.

## 6. Disclosure of this audit's side effects

- `./screening/run_r2.sh 1` rewrote the gitignored `runs/r2/` tree (new `created_utc` in the metas); the eight tracked outputs were byte-identical (§2 F1) and `git status --porcelain` was empty afterwards.
- `uv run python scripts/regen_sources_index_md.py --help` regenerated `docs/sources/index.md` (1 line changed, the F3 row); I restored it with `git checkout -- docs/sources/index.md`; tree clean again.
- The README demo was written to `/tmp/verify-demo/skims1/`, not `runs/skims/demo/`; `logs/verify-INTEGRATE_R2-run_r2.log` (gitignored) holds the chain log.

## 7. Three most important fixes

1. Register the CP3 5a drop as a rule row in `docs/assumptions.md` (e.g. `A-r2-005`: grid rows with `pop_grid_raw == 0` leave the register and stay in `cities/ksa/zones/settlements.parquet`; 478 rows, riyadh 393 / tabuk 64 / al_jouf 21; alternative "keep them" = the R2 state; approval: Tariq, 31 Oct 2026 (CP3 5a); used in `screening/control_total.py`, `screening/run_r2.sh`) and cite the id in `control_total.drop_zero` and `docs/screening.md` §1.
2. Refresh `docs/STATUS.md` lines 5, 7, 8 (last updated = INTEGRATE_R2; disk = `df -h ~` at the time; cost so far = `cost_log summary`) and write the `docs/status/main.md` INTEGRATE_R2 block (branches: none merged here; conflicts: none; verifier verdict; 318 tests, 16 s) ending `INTEGRATE_R2: done`, so that STATUS line 18 points at something that exists.
3. Regenerate `docs/sources/index.md` with `uv run python scripts/regen_sources_index_md.py` (1 row) and commit it with the two edits above; re-run `make test` and `licences check`.

(Pass-1 verdict at 98ef304 was FAIL on F1–F3; superseded by §8.)

## 8. Pass 2 (HEAD 811202e, 31 Oct 2026)

Scope: commit 811202e "fix(R2-int): verifier pass-1 fixes" (8 files: `docs/STATUS.md`, `docs/assumptions.md`, `docs/screening.md`, `docs/sources/index.md`, `docs/status/main.md`, `screening/control_total.py`, `screening/primary_match_decisions.yaml`, plus my pass-1 report). Working tree clean before and after (my chain re-run and one `regen_sources_index_md.py` diff test were restored to HEAD, see below).

### 8.1 Pass-1 findings re-checked

| finding | verdict | evidence |
|---|---|---|
| F1 — drop rule unregistered | **closed** | `docs/assumptions.md` line 303: `A-screen-041` "register membership of grid rows without population evidence": rule, value "a grid row (`pop_type: grid`) whose raw WorldPop value (`pop_grid_raw`) is 0 leaves the candidate register; it stays in `cities/ksa/zones/settlements.parquet`", alternative "keep the rows (the R2 state, `DROP_ZERO=0`)", source Tariq CP3 5a with the 478 / 393 / 64 / 21 figures and the 0-rank-change result, approval "Tariq, 31 Oct 2026 (CP3 5a)", used in `screening/control_total.py` (`drop_zero`, `--drop-zero-grid`) and `screening/run_r2.sh`. `screening/control_total.py` line 90 docstring cites A-screen-041. Register ids vs b2655d2: 0 removed, 3 added (A-r2-003, A-r2-004, A-screen-041) |
| F2 — STATUS header and handoff pointer | **closed** | `docs/STATUS.md` line 5 "Last updated: 31 Oct 2026 (INTEGRATE_R2 …)"; line 7 "49 GiB free of 460 GiB (`df -h ~`, 31 Oct 2026, INTEGRATE_R2)" (measured now 50 GiB; time-stamped, within rounding of the intervening runs); line 8 "402.47 over 45 runs, 12.03 agent-hours … before the INTEGRATE_R2 row" = `cost_log summary` TOTAL 45 runs / 12.03 h / USD 402.47. `docs/status/main.md` now has the "## INTEGRATE_R2 integration audit and CP3 fixes" block; its `INTEGRATE_R2: done` line is absent by design until this PASS (coordinator's instruction) |
| F3 — `index.md` not regenerated | **closed, and corrected** | On re-examination the generator `scripts/regen_sources_index_md.py` (COLS, lines 18–19) does not emit the `used_in` column, so the S-qassim-003 CSV edit could never change a data row of `index.md`; the one-line diff I saw at pass 1 was the hand-edited "Rows: …" provenance line, not a stale row. My pass-1 statement that "line 245 still shows the old `used_in`" was wrong: the Markdown has never carried `used_in`. At 811202e the provenance line reads "generated … by INTEGRATE_R2, 31 Oct 2026 (S-qassim-003 used_in)"; a fresh regeneration reproduces all 1,815 data rows byte-identically and differs only in that hand-written provenance line (restored with `git checkout -- docs/sources/index.md`). No register inconsistency exists |
| O1 — Alhasma "three" الحصامة | closed | `screening/primary_match_decisions.yaml` and `docs/screening.md` §2 now read "الحصامة (four Jazan places: three villages, one hamlet; grid 308 where tagged)", matching the extract (3 villages + 1 hamlet) |

### 8.2 Regression checks at 811202e

| command | result | exit |
|---|---|---|
| `make test` | ruff "All checks passed!", 482 files formatted, docver OK 261 files, manifest OK 308 rows; 17.0 s wall | 0 |
| `uv run pytest -q` | 318 collected, 318 passed, 0 F | 0 |
| `uv run python -m common.licences check` | 210 = 210, 0 differ | 0 |
| `uv run python -m common.docver check` | OK 261 files (includes this report) | 0 |
| `./screening/run_r2.sh 1` (log `logs/verify-INTEGRATE_R2-run_r2-pass2.log`) | EXIT 0; the 8 tracked outputs (`candidates.parquet`, `coverage.md`, `screening.md`, `candidates.md`, `S2–S5.yaml`) byte-identical by sha256; `git status --porcelain` empty afterwards | 0 |
| home-path grep over the 8 changed files | empty | — |

### 8.3 Numbers in the new `docs/status/main.md` INTEGRATE_R2 block, re-measured

| claim in the block | measured | result |
|---|---|---|
| Al Jubayl rank 2 → 2, score 0.9194 → 0.9196, range 2–2; JIC rank 16 (6–22), short list | `runs/integrate_r2/check/check.json` `jubail.r2` / `jubail.final`, `enter[0]` | true |
| Dammam–Khobar–Dhahran 315° belt 77.0 → 87.5 km, 2 → 3 stations | `S4-commuter_belt-dammam-khobar-dhahran-315.yaml`: `length_km` 77.0 at b2655d2, 87.5 now; `stations:` entries 2 → 3 | true |
| long list 189 → 198, short list 60 → 60; enter JIC #16, Banban #52; leave Samitah 59 → 61, Yanbu Industrial City 60 → 63 | `check.json` `item1_vs_r2` | true |
| top-30 stable 23/30; Kendall tau min 0.878, median 0.936 (was 0.885 / 0.938) | `docs/screening.md` §5: 23 of 30; min 0.8781, median 0.9358; R2 values in `docs/status/main.md` R2 block (0.885 / 0.938) | true |
| corridors 74 → 76, S5 7 → 9 | `git ls-files cities/ksa/corridors` = 76; `scenarios/S5.yaml` corridor refs 14 → 18 (two refs per corridor: 7 → 9) | true |
| control-total factors riyadh 0.7040 → 0.6294, makkah 0.7554 → 0.7315, madinah 0.8733 → 0.7923, qassim 0.6305 → 0.6146, eastern 1.0 → 0.8527, others unchanged | `docs/screening.md` §3 `factor_at_r2` vs `grid_scale_factor` (asir, tabuk, hail, jazan 1.0 = 1.0; northern_borders 0.6311, najran 0.9289, al_baha 0.6918, al_jouf 0.8028 unchanged) | true |
| 478 rows dropped (393 / 64 / 21), 1,702 → 1,224, 0 rank changes | `dropped_zero_grid.csv`, `check.json` `register_rows`, `drop_vs_item1.rank_changed = 0` | true |
| 238 of 271 placed (214 matched, 24 created), 33 unplaced (222,950; 1 ≥ 10k); 13 seat checks | `primary_cities.csv` status counts; 13 `seat-*` directories, all `inside: True` | true |
| 25 `derived` primary-city rows; JIC and Dariyah `official` | `primary_cities.csv` `pop_type` by tier (20 OSM-extract + 5 judgement `derived`; 2 judgement `official`) | true |
| licences 211 lines × 11 cells, 210 = 210; 14 code paths repointed; 13 registers `--strict` | pass-1 D1–D3 (unchanged files) | true |
| assumptions +3 / 0 removed; sources index 1,815 rows; manifest 308 (+1) | `comm` on ids; `tail -n +2 index.csv \| wc -l` = 1,815; `manifest verify` 308 | true |
| 318 passed (+7); README demo about 2 s; chain about 12 s byte-identical | §8.2; pass-1 §1 (2.09 s; 11.95 s) | true |

### 8.4 Residual observations (non-blocking, unchanged from §5)
O2 (`common.assumptions check` CLI absent, pre-existing), O3 (JIC node 0.7 km inside the governorate boundary), O4 (seat-check metas `-dirty`), O5 (Sabt Al 'Alayah universe row 200,000 vs register 20,250), O6 (`regen_sources_index_md.py` has no argument guard), O7 (INTEGRATE_R2 cost-log row appended at run end).

### 8.5 Disclosure
This pass re-ran the chain (gitignored `runs/r2/` rewritten; tracked outputs identical) and ran the index generator once to test F3 (one-line provenance diff, restored with `git checkout -- docs/sources/index.md`). Tree clean apart from this report edit.

All INTEGRATE_R2 acceptance criteria and items 1–5 of the 18:30 addendum are met; F1–F3 closed; no regression.

VERDICT: PASS
