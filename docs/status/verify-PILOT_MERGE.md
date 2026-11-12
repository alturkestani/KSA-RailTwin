> **Document version:** docs/status/verify-PILOT_MERGE.md v1.0 | 30 Oct 2026 | Author: red-team-verifier (claude-fable-5-1) | Status: verified

# VERIFY_PILOT_MERGE — red-team audit of milestone PILOT_MERGE

Audited at HEAD `6bcac06` on `main`, 30 Oct 2026 22:29–22:50 +03. Read: `CLAUDE.md`, `PROJECT.md` sections 2, 5 (W2, W3, W5), 7, 9; `prompts/PILOT_MERGE.md` v1.1 (Acceptance + coordinator decisions 21:58); `prompts/VERIFY_PILOT_MERGE.md`; `docs/STATUS.md` v1.2; the builder's block in `docs/status/main.md` (lines 92–114). Nothing was edited except this file and one status line. The builder's closing `PILOT_MERGE: done` line is absent by design (added after this verdict) and is not scored.

## 1. Commands (exit code, wall time)

| command | exit | time | output line |
|---|---|---|---|
| `uv run ruff check .` | 0 | 0.18 s | `All checks passed!` |
| `uv run ruff format --check .` | 0 | 0.03 s | `245 files already formatted` |
| `uv run pytest -q` | 0 | 2.39 s | `65 passed in 1.80s` (16 in `tests/test_screening_pilot.py`; slowest 0.64 s) |
| `uv run python -m common.docver check docs prompts .claude` | 0 | 0.06 s | `docver OK: 178 files` |
| `uv run python -m common.manifest verify` | 0 | 0.32 s | `manifest OK: 16 rows` |
| README command `uv run python -m screening.cli version` | 0 | <1 s | prints the package version |
| milestone commands (`screening.funnel long-list` + `score`, seed 1), run twice into scratch dirs | 0 | 2.85 s for both | see section 3 |
| `uv run python -m screening.coverage` (regenerate) then `git diff --exit-code docs/coverage.md` | 0 | — | `docs/coverage.md` byte-identical before and after (`cmp` clean, `git diff` clean) |
| `uv run python -m common.cost_log check` | 0 | — | `cost log OK: 18 rows` (includes the coordinator's uncommitted rows) |

## 2. Acceptance criteria

| # | criterion (prompts/PILOT_MERGE.md) | verdict | evidence |
|---|---|---|---|
| A1 | `docs/coverage.md` has exactly one row per GASTAT governorate and reconciles to the GASTAT count, or the difference is explained row by row | **PASS** (count from secondary, primary pending, as coordinator decision 4 allows) | 152 numbered rows (`grep -c "^| [0-9]"`); statuses 125 screened / 22 excluded / 3 not yet swept / 2 conflict = 152; no duplicate region+governorate pair among rows 1–150. Independent parse of the archived page `data/ksa/pilot-qassim/raw/citypop_admin.html` (manifest `citypop-admin-census2022`): **150** rows with `rstatus = Governorate`, last census column sums to **32,175,224**; the 150 table populations also sum to 32,175,224 = S-077 (GLMM page fetched: 32,175,224). Per-region governorate counts 10+4+18+12+9+17+9+17+7+4+13+23+7 = 150 (lines 182–195). The +2 conflict rows (Abanat, Al-Bayḍā) are explained at lines 163–164 and 171–173. GASTAT primary still unreached: S-072, S-090; coverage.md line 7 and line 169 say so in the prescribed words |
| A2 | Every weight and threshold is a registered assumption with `approval: pending CP1`; no weight appears as a bare number | **PASS** | `cities/ksa/assumptions/screening_weights.yaml`: file-level `approval: pending CP1` (line 9); every number is `{value, assumption_id}` (lines 12–62, metros 69–79); the two non-assumption entries carry `source:` (lines 16, 63). Register rows A-screen-003..006, -020..-030 in `docs/assumptions.md` lines 16–31 each say "approval: pending CP1"; A-screen-001/002 (lines 9–10) record Tariq's pre-CP1 answer of 30 Oct. `tests/test_screening_pilot.py::test_weights_file_has_no_bare_numbers` (line 163) guards it. `screening/funnel.py` has no real-world constant outside the YAML (`EARTH_R_KM` line 39 is a geometry constant; `0.5` in `_minmax` is a documented neutral value for a degenerate column) |
| A3 | `screening.funnel` is deterministic (test) and the sweep results are reported, not just computed | **PASS** | `test_funnel_deterministic` (line 144). Two fresh seed-1 runs: `longlist.parquet`, `scores.parquet`, `sweep.parquet`, `ranks.parquet` byte-identical to each other **and** to the builder's `runs/screening-pilot/`; `summary.json` identical. Sweep reported in `docs/screening-pilot.md` §4 (10 corners, per-corner overlaps 29/28/28/29/27/29/29/28/30/28, stability 24/30 = 0.80, leavers and entrants named) and §5 (rank range and share of corners per candidate); all values equal `summary.json` |
| A4 | The scoping note names every benchmark country from W5 and every KSA cost data point from W3 with a reachability status | **PASS** | `docs/scoping-benchmarks-costs.md` §1 rows: France, Japan, Spain, Germany, China, South Korea, Italy (Frecciarossa and Italo separately), Morocco, Turkey, UAE, Egypt, California HSR, UK HS2, plus found Taiwan, Brightline, Portugal; small-town evidence (Shinkansen, TGV, AVE) in the closing paragraph. §2 rows: Haramain (5), SAR North (4), SAR East (2), Riyadh Metro (2), Landbridge (1), plus GCC/Jubail/metros, SAR financials, KAPSARC. Counts in the note (17 rows: 0/11/6, 0/8/9, 0/9/8; 48 rows: 1/35/12) re-tallied from the table and from `logs/pilot_merge/scoping_costs.md` lines 82–87: equal |
| A5 | Nothing labelled a forecast; every number has an `S-nnn` or `A-xxx` | **PASS** | Label on `docs/screening-pilot.md` line 5, `docs/coverage.md` line 5, the YAML line 3 and every `meta.json`. Grep for "will reduce/transform", "should build", bare "forecast": none outside the "not a forecast" label and the metric name "ridership vs forecast". Report figures re-derived from `runs/screening-pilot/`: per-region counts (`counts.json`), 156/8/21/60, 168 (5k), 155 and served 9 (committed), top-30 criterion values and scores, drivers table, missing counts 31/38/84, metro anchors (S-080, S-makkah-001, S-madinah-001, S-eastern-001 sum 1,939,651, S-qassim-002, S-tabuk-002, S-asir-001 sum 869,355, S-jazan-002, S-najran-002), Jazan ≥ 483.6 km and Najran 562.1–798.9 km from the register: all match. Scoping note contains no cost, ridership or ratio figure; every id cited (S-007…S-063, S-lb-*) exists in `docs/sources/index.csv` |
| D1 | Coordinator decision 1: all 13 pilot branches merged `--no-ff` | **PASS** | `git log --merges r0..HEAD`: 13 `merge(pilot): pilot-<slug>` commits, alphabetical |
| D2 | Decision 2: schema (`pop_source_status`, `primary_to_find`, pilot fields, `extra="forbid"`, terrain vocabulary, mapping recorded, tests) | **PASS** | `common/schemas.py` lines 53, 64, 225, 235–236, 250, 256–260, 276–287; register: 150 rows `official` + `secondary`, 35 null; `terrain_class` values only schema words (mixed 58, flat_desert 50, escarpment_mountain 13, coastal 13, dunes 3, null 48); mapping and "0 rows needed it" in `docs/screening-pilot.md` §2 (the prompt words do survive in the 14 `prompts/PILOT_REGION_*.md`, as stated); tests lines 52–105 |
| D3 | Decision 3: metro tiers A-screen-013 in `nearest_metro_tier` and the commute criterion | **PASS** | YAML `metros:` block (11 metros, tiers 1/2/3); register `nearest_metro_tier` filled on 185/185 (67/91/27); `summary.json` `metros` |
| D4 | Decision 4: reconcile to the DATASCOUT_1H count; "count from secondary sources, primary pending" | **PASS** | `docs/gastat-regions.md` lines 10–14 (150, S-073); `docs/coverage.md` lines 7, 169–170 |
| D5 | Decision 5: decisions recorded in `docs/STATUS.md` with timestamp and "coordinator" | **PASS** | `docs/STATUS.md` lines 41–45 (21:58, coordinator) plus the builder's own at 46–51 |
| T4 | Tests run on fixtures in under 5 s, check determinism and sweep tolerance | **PASS** | 16 tests, slowest 0.64 s; `RANK_TOLERANCE = 1` (line 23); `test_sweep_changes_scores_not_order` (line 152) |
| T6 | `docs/plan.md` "Open questions" extended, no other section edited | **PASS** | §9 items 9–24 (lines 93–122); header v0.4 names the edit; §0–8 untouched per `git log -p` |
| T7 | Status block numbers match what was measured | **PASS** | 185 rows / 0 duplicates (12 rows share a null OSM id and are keyed by name+coords; `row_key` unique) / 150 populated; 150 and 152; 148/125/22/3; 156, 168, 8, 21, 60; 24/30 and 27–30; 17-row and 48-row tallies; 65 tests; docver 178; manifest 16: all equal |

## 3. Determinism

`long-list` + `score`, seed 1, run twice into `runs/_verify/{a,b}` (deleted afterwards). Parquet outputs byte-identical (sha256) across the two runs and against `runs/screening-pilot/`; `summary.json` identical. `meta.json` differs only in `created_utc` and `code_version` (`r0-40-g6bcac06-dirty` now, the "dirty" being the coordinator's uncommitted files; the builder's `r0-36-gcfe44f3-dirty` is explained at `docs/screening-pilot.md` line 19). The score step's `config_hash` differs (9bbb7fee… vs 4f1742f0…) because `write_meta` hashes `{"weights", "sweep", "input": str(inp)}` (`screening/funnel.py` line 365) and the input path differed; outputs did not. See O5.

## 4. Hygiene

- `git status --porcelain`: only the coordinator's five uncommitted files (`docs/cost-log.*`, `prompts/PILOT_MERGE.md`, `prompts/_common.md`, `run_track.sh`), not part of this milestone, not committed by me.
- `git ls-files` under `data/`, `runs/`, `movies/`, `film/renders/`, `film/audio/`: `data/README.md`, `data/ksa/tables/README.md`, `gastat_railway_key_indicators_2024_2025.csv` (1.3 KB), `gastat_railway_transport_statistics_2025_en.pdf` (243 KB) — the last three from DATASCOUT_1H (commit a6e7580, 21:05, before this milestone), README cites the GASTAT use policy. See O7.
- `grep "/Users/[a-z]"` over tracked files: empty. Secrets grep: empty. No tracked `.env`. `git push` appears only in the rule texts (CLAUDE.md, PROJECT.md, prompts, agent file, verify-R0); `logs/` is gitignored.
- Model labels: none in `docs/screening-pilot.md` or `docs/scoping-benchmarks-costs.md`; `docs/coverage.md` lines 38 and 95 carry "Needs Opus 3" / "needs Opus judgement" copied from pilot notes. See O1.
- content from the author's company: only in the rule sentences that forbid it. Advocacy: none; `docs/screening-pilot.md` line 5 says scores "do not say a line should be built".
- Version headers: docver OK on 178 files; the YAML carries its own version comment (line 2).

## 5. Licence and openness register

`docs/licences.md` and `.csv`: 151 rows each, same items. Rows cover the milestone's inputs: OSM via Nominatim/Overpass and the GCC extract (ODbL, attribution text present), citypopulation.de (five rows; "terms not checked / unclear / approval pending"), GLMM, Wikipedia (CC BY-SA, facts only), Saudipedia, UNESCO and press sources, the archived admin HTML. Conflicts are flagged, not resolved: citypopulation.de terms unread (STATUS.md line 51, plan.md Q20), MEED Projects paywalled and not used (scoping note §3 item 5). No model, voice, font, track or image was used. See O3.

## 6. Spot-check (seed 20261030)

Sample: `numpy.random.default_rng(20261030).choice(185, 18)` over the register sorted by `row_key` (10 % of 185 = 18); scoping rows: `default_rng(20261030).choice(34, 4)` over the 17 + 17 note rows → Japan, Taiwan HSR, Haramain 2026 train order, SAR North packages.

| row_key | claim checked | source fetched | result |
|---|---|---|---|
| al_jouf:osm:1236739661 An-Nabak Abū Qaṣr | pop 5,374 (S-al_jouf-001) | citypopulation.de/en/saudiarabia/jawf/ | match |
| al_jouf:osm:1236744823 Al-Qurayyat | pop 167,080; served 6.13 km | same page (place 167,080; gov 195,016) | match |
| asir:osm:11891866421 Balqarn | no population (centre not in places table) | citypopulation.de/en/saudiarabia/asir/ | confirmed absent (only Al-'Ulāyah under Balqarn) |
| asir:osm:7700248106 Ahad Rafidah | pop 79,202 (S-asir-001) | same | match |
| asir:osm:983083570 Khamis Mushait | pop 535,065; role military (S-asir-008) | same; globalsecurity.org → HTTP 402, confirmed via en.wikipedia.org/wiki/King_Khalid_Air_Base ("near Khamis Mushait") | match |
| eastern:osm:1013645811 Saihat | pop 84,818 (S-eastern-001) | citypopulation.de/en/saudiarabia/eastern/ | match |
| eastern:osm:19120268 Ath-Thuqbah | pop 248,888 | same | match |
| eastern:osm:208501048 Hofuf (Al-Hufuf–Al-Mubarraz) | pop 729,606 (one combined entry); roles heritage, agriculture (S-eastern-006) | same (combined entry 729,606); whc.unesco.org/en/decisions/7129/ → HTTP 403, confirmed via en.wikipedia.org/wiki/Al-Ahsa_Oasis (WHS 2018, criteria iii–v, date palms) | match |
| hail:osm:1237937470 Jubbah | pop 5,622 (S-hail-001); role heritage (S-hail-005) | citypopulation.de/en/saudiarabia/hail/; worldheritagesite.org → HTTP 403, confirmed via en.wikipedia.org/wiki/Rock_Art_in_the_Hail_Region (2015; Jabal Umm Sinman at Jubbah) | match |
| jazan:osm:1237961319 Fayfa | no population | citypopulation.de/en/saudiarabia/jazan/ | confirmed absent from places table (governorate 19,346 = coverage row 115) |
| jazan:osm:4941110005 Ad Dayer | pop 15,752 (S-jazan-002) | same | match |
| makkah:node:295919318 Maysān | no population | citypopulation.de/en/saudiarabia/makkah/ | confirmed absent (governorate 28,765 = coverage row 133) |
| makkah:relation:12429525 Al-Līth | pop 20,811 (S-makkah-001) | same | match |
| najran:osm:6774224946 Yadamah | pop 4,983 (S-najran-002); excluded < 5,000 | citypopulation.de/en/saudiarabia/najran/ | match |
| northern_borders:osm:1236745582 Al-Uwayqilah | pop 17,055 (S-northern_borders-001) | citypopulation.de/en/saudiarabia/northern/ | match (page spells Al-'Awayqīlah) |
| qassim:node:747671390 Al-Quwārah | pop 5,646 (S-qassim-002) | citypopulation.de/en/saudiarabia/qasim/ | match |
| riyadh:node:1014940282 Al-Uyaynah | pop 8,649 (S-riyadh-003) | citypopulation.de/en/saudiarabia/riyad/0102__ad_diriyah | match (also Ad-Dir'iyah 61,609, Al-Jubaylah 8,005, gov 95,834) |
| riyadh:node:1237933651 Al-Ghat | no population; role university (S-riyadh-011) | en.wikipedia.org/wiki/Majmaah_University | match ("branch campuses in Al Zulfi, Al Ghat, Rumah, and Hotat Sudair") |

Incidental matches on the same pages: Jiddah 3,712,917; Makkah 2,385,509; Taif 563,282; Thuwal 26,957; Al-Hawiyah 171,610; Jizan 173,919; Sabya 72,086; Farasan 10,118; Abu Arish 69,632; Najran 381,431; Sharurah 89,456; Arar 199,247; Buraydah 571,169; Ar-Rass 107,902; Hail 448,623; Abha 334,290; Muhayil 97,967; Jubail 474,679; Dammam 1,386,166 + Khobar 409,549 + Dhahran 143,936 = 1,939,651; governorate-row counts per page (4, 18, 12, 9, 17, 17, 7, 4, 13) equal the coverage per-region table. S-077/S-078/S-079 (GLMM): 32,175,224; 18,792,262 / 13,382,962; Makkah 8,021,463, Madinah 2,137,983: all match. S-073: 150 rows on the archived page.

Scoping rows: Japan — Wikibooks Kyushu casebook exists, student page with an actual-vs-model table and no cost figure (consistent with "partly / grade D"); Taiwan — worldtransitresearch.info/research/1382 exists (Cheng 2010, "unsatisfied ridership"), consistent with "partly"; Haramain 2026 order — railwaynews.net article exists (24 Feb 2026, 20 Talgo trains, maintenance to 2033, option 2038), consistent with "press"; SAR North packages — railway-technology.com article exists (9 Jan 2012, three contracts, no section lengths), consistent with "press, package lengths not given".

**Hit rate: 18/18 register rows, 4/4 scoping rows; no fabricated or misquoted figure.** Three cited URLs are blocked to automated fetch (402/403); the register rows already say "search extract" and the claims were confirmed through alternate pages (O8).

## 7. Observations (not FAILs for this milestone; carry forward)

- **O1.** `docs/coverage.md` lines 38 and 95 contain the workflow label "Opus" (from `docs/status/pilot-madinah.md` and the Asir exclusion note). Not in the verify prompt's public-facing set, but the coverage table is a W2 deliverable that will be reused in R2 and the report annex: remove before then.
- **O2.** GASTAT's governorate list and every population remain secondary (S-072, S-090). Allowed by coordinator decision 4 and said in the right words everywhere; it is still the single largest open item for R2.
- **O3.** citypopulation.de terms unread while 150/150 populations, the 150 count and an archived HTML copy depend on it; the register flags "approval pending". Tariq's decision (read the terms, approve, or replace with GASTAT tables) should be recorded in `docs/STATUS.md`.
- **O4.** This run's cost-log row is appended by `run_track.sh` when the run ends (same as R0); `cost_log check` passes on the 18 rows present, 15 of them in the coordinator's uncommitted diff.
- **O5.** `screening.funnel score` hashes the `--in` path into `config_hash`, so identical inputs in different run dirs get different config hashes; hash the long-list content (or the long-list `meta.json` hash) instead.
- **O6.** The gitignored `logs/pilot_merge/scoping_costs.md` row 1e attributes the Railway News article to "citing Talgo's CNMV notice"; the article does not mention a CNMV notice. The tracked note says only "primary reachable, not opened": treat the CNMV filing as a lead to confirm in R1c.
- **O7.** `data/ksa/tables/gastat_railway_transport_statistics_2025_en.pdf` (243 KB, DATASCOUT_1H) is a publication rather than a table under rule 8; the README records the GASTAT use policy. Coordinator to confirm it stays.
- **O8.** S-asir-008, S-eastern-006 and S-hail-005 point at pages that refuse automated fetch; add the confirming alternates (Wikipedia pages above) as corroboration rows at R2.
- **O9.** A-screen-001/002 already carry Tariq's 30 Oct approval; the blanket "approval pending CP1" sentence in `docs/screening-pilot.md` line 5 is slightly overbroad for those two.
- **O10.** `docs/benchmarks/README.md` does not exist yet; it is an R1b artefact, so the W5 country check was applied to the scoping note (A4).
- **O11.** The milestone's own README command is generic (`screening.cli version`); the funnel and coverage commands are documented in `docs/screening-pilot.md` §1 rather than `README.md`.

## 8. Three most important fixes

1. Remove the "Opus" labels from the pilot notes that feed `docs/coverage.md` (lines 38, 95) and regenerate with `screening.coverage`, so no Claude label reaches the W2 deliverable (O1).
2. Close the population provenance gap before R2: reach GASTAT's primary governorate and locality tables (open.data.gov.sa, Law of Provinces on boe.gov.sa) and either read and record citypopulation.de's terms with Tariq's approval in `docs/STATUS.md` or swap the source (O2, O3).
3. Make `screening.funnel score` write a path-independent `config_hash`, and append this run's cost-log row when `run_track.sh` closes, then re-run `uv run python -m common.cost_log check` (O4, O5).

VERDICT: PASS
