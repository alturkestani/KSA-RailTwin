> **Document version:** docs/plan.md v0.13 | 5 Nov 2026 | Author: coordinator; FIX_R8 (§6 cost estimate: model names replaced by class labels, R8-checkpoint review item 7); INTEGRATE_R8 (§0 CP1 pre-answers: a model label outside the exempt run table and cost estimate reworded to "verifier", R8 review item 2b); §0 model note, §1 population rule (with the GASTAT addendum) and §3 index by CP2_PREP; Open questions 9–24 added by screening-analyst (PILOT_MERGE); sections 1–3, 8, 9 rewritten by CP1_PREP | Status: draft (for Checkpoint 1; the pilot results update sections 1–3)

# Plan for Checkpoint 1

Everything below is a **proposal** for Tariq's approval at CP1. Thresholds and weights are registered assumptions (`A-screen-*`, `A-cba-*`), status `assumed`, approval `pending CP1`. The national pilot (section 10.4 of the brief) tests them before he decides; nothing in this plan is a town list.

## 0. Decisions already taken (30 Oct 2026)
- Repo at `~/Documents/Projects/KSA-RailTwin` (hyphen), as the brief says; `~/Documents/Projects/KSARailTwin` keeps the prompt.
- Source versioning in three layers (git tags per milestone, data manifest with SHA-256 and access dates, document version headers): `docs/versioning.md`.
- Models: the mapping of the supervisor, coder and verifier labels to model ids lives in `CLAUDE.md` ("Machine and models"), the agent files and the cost log only; it is not repeated in `docs/`.
- Budget: no USD cap (subscription); list-price costs still logged per run.
- Disk: ~17 GB free at R0, 26 GB at 18:30. Tariq confirmed (18:35): research-only tracks (DATASCOUT_1H, the pilot, R1b–R1d) run now; skims (R1a) need ≥ 15 GB free; ≥ 40 GB before R3; ≥ 50 GB before R10 renders. No external drive for now (maybe later). Models already in `~/.cache/huggingface` (Chatterbox, Kokoro-82M, Qwen2.5 1.5B/7B MLX 4-bit, whisper-large-v3-turbo) are reused, not re-downloaded.
- **Tariq's CP1 pre-answers (30 Oct 2026, 18:35):** population threshold 10k with a 5k sensitivity (A-screen-001/002 approved); metro set for commute belts = primary Riyadh, Jeddah, Makkah, Madinah, Dammam–Khobar–Dhahran; **secondary** Taif, Buraidah, Tabuk, Abha–Khamis Mushait; **tertiary** Jazan, Najran (A-screen-013); discount rate central case Green Book (superseded 31 Oct by CP1 D1a: the 2026 schedule 3.00/2.50/2.25 %, A-cba-001); price base year 2025 SAR with a documented FX/inflation index (GASTAT CPI first, World Bank deflators as fallback; A-cost-001); unattended overnight runs allowed for **all** phases with the CP stops honoured; Landbridge SR100bn vs USD 7bn: reconcile by arithmetic and sources (DATASCOUT_1H task, verifier review in LANDBRIDGE_RECONCILE); film register preference **white/Najdi** (W10 still documents the alternatives and the criteria); external drive: none now.

## 1. Screening criteria, thresholds and scoring weights (proposal; one criteria set)
**Label: pilot, proposed criteria pending CP1; screening input, not a forecast.** The canonical definition is `cities/ksa/assumptions/screening_weights.yaml` v0.2 (the file the funnel reads); this section describes exactly that file, line by line, and uses its ids. CP1_PREP (31 Oct 2026) merged the two earlier sets: plan v0.4's filters F1–F4 and its five score criteria are retired (mapping at the end of this section). Ids: `docs/assumptions.md`. Approved by Tariq on 30 Oct 2026: A-screen-001, -002, -013; every other id is `assumed`, approval `pending CP1`.

**Settlement universe (stage 1).** All 13 regions; every GASTAT governorate (rule 2; coverage table `docs/coverage.md`); every GASTAT-tabulated locality; OSM `place=city|town|village` and GHSL/WorldPop clusters for places GASTAT does not tabulate (`pop_type: grid`). The pilot sampled centres, towns ≥ 50,000 (A-screen-014, pilot only) and 4–6 smaller towns per region.

**Population basis (CP2 P1a; Tariq, 31 Oct 2026; A-screen-031…039).** In Tariq's words: "GASTAT-relayed figures win where they exist; WorldPop fills gaps only, every gap row flagged `pop_type: grid`, `pop_source_status: unverified`. A grid-only settlement may pass the ≥ 10k test only if a second independent method (building footprints × occupancy, GHSL, or VIIRS-calibrated) corroborates it within 30 %. Sensitivity to report: WorldPop ÷ 0.64 (the back-test median ratio), with the list of settlements whose ≥ 10k status flips; the correction is **not** applied to the base case." Implementation: precedence official > derived > grid (A-screen-031); band abs(grid − other) / grid ≤ 0.30 (A-screen-032); methods `buildings_x_occupancy`, `ghs_pop_sum`, `viirs_calibrated` in `RegionRow.pop_corroboration` (A-screen-033); otherwise `tag_10k = false`, reason "grid-only population, uncorroborated". Sensitivity: `uv run python -m screening.funnel sensitivity-grid --ratio 0.64 --seed 1` (A-screen-034). Interpretations to confirm at CP3: the 5k sensitivity and derived rows are not gated. GASTAT addenda (Tariq, 31 Oct 2026): the **primary** Census 2022 TA1 exports `data/ksa/tables/gastat/census2022_TA1_governorate_primary.xlsx` (150 governorates, S-cp2-gastat-007) and `census2022_TA1_city5k_primary.xlsx` (271 cities of 5,000 or more plus "Other (< 5,000)" = 3,683,816, S-cp2-gastat-008) "supersede the relayed file at governorate and city level" (addendum 2, 15:25): a settlement matched to a primary city gets that figure as `pop_type: official`, `pop_source_status: verified`, and "the ≥ 10k test for those rows uses the primary figure only (no corroboration needed)" (matching tiers and guards A-screen-038; crosswalk `screening/gastat_crosswalk.yaml`); the DataPulse relayed table (S-cp2-gastat-001) is a cross-check only, "never the value of record where a primary row exists"; keep citypopulation.de only for localities neither table covers; log a conflict where figures differ by more than 2 %. Grid-filled populations outside the matched cities are checked against each region's residual (control total A-screen-037; `control_total_flag`, reporting only). Below city level keep the WorldPop gap-fill under the gate, with "a third method: the 2010 cities > 5k list grown at the governorate's 2010→2022 ratio" (`pop_corroboration: gastat2010_city_growth`, value = pop_2010 × gov_2022 / gov_2010, A-screen-035), which "counts as one of the independent corroboration methods". The sensitivity uses the back-test median against the primary cities: ÷ 0.71 (A-screen-039; earlier ÷ 0.48, A-screen-036, and ÷ 0.64, A-screen-034). Lookups and the 2010 estimates: `screening.gastat`; results in `docs/network.md` §Population basis.

**Long list (stage 2; `long_list:` in the YAML).**
| YAML key | rule | value | id |
|---|---|---|---|
| `threshold` | population ≥ threshold passes | 10,000 persons | A-screen-001 |
| `sensitivity` | rerun at this threshold | 5,000 persons | A-screen-002 |
| `role_passes` | a row with ≥ 1 sourced economic role passes, whatever its population; `administrative` does not count (A-screen-009) | true | A-screen-003 |
| `centres_always_pass` | governorate centres pass whatever their population | true | PROJECT.md §2 rule 2 |
| `served_km` | within this distance of a station of the layers in use → "served" bucket (station-addition family), not scored | 10 km | A-screen-004 |
| `pilot_distance_proxy` | straight-line (haversine) distance stands in for road distance until the R1a skims | straight-line | A-screen-027 |
| `use_committed` | committed-layer distances used in the served test and the rail gap | false in the pilot (existing layer only); true is the sensitivity | A-screen-030 |

**Short-list score (stage 3; `criteria:`).** Weights sum to 1.
| criterion | weight (id) | measure (as the YAML states it) | other parameters (id) | missing value (A-screen-028) |
|---|---|---|---|---|
| population | 0.30 (A-screen-020) | log10(population), min-max scaled over the long list | — | minimum of the long list |
| rail gap | 0.20 (A-screen-021) | log10(1 + min(d, cap)) / log10(1 + cap), d = straight-line distance to the nearest line of the layers in use; farther = higher, saturates at the cap | `measure_kind` log_capped (linear min-max = the v0.1 measure, run as the `score-linear-gap` sensitivity); `cap_km` 300 km, range 200–500 (A-screen-021) | median |
| commute | 0.20 (A-screen-022) | max over metros whose distance lies in the band of tier_factor × log10(metro pop) / log10(largest metro pop) | `band_km` 40–120 km (A-screen-005); tier factor 1.0 / 0.6 / 0.3 (A-screen-026); metro set and tiers (A-screen-013) | never missing (computed from coordinates) |
| economic roles | 0.20 (A-screen-023; A-screen-012 merged into it) | count of distinct sourced roles, excluding `exclude_from_score`, capped, ÷ cap | role list (A-screen-007): port, industrial_city, mining, tourism, heritage, hajj_umrah, airport, university, giga_project, agriculture, border_crossing, military, administrative, energy; `energy` added (A-screen-010); `cap` 3 (A-screen-008); `exclude_from_score` [administrative] (A-screen-009); one source per role tied to the town (A-screen-011) | 0 (empty list) |
| terrain | 0.10 (A-screen-024) | 1 + penalty (flat = 1, escarpment = 0) | penalties: flat_desert 0, coastal 0, dunes −0.5, sabkha −0.5, escarpment_mountain −1 (A-screen-024); mixed −0.5 (A-screen-025) | median |

**Sweep and short list (`sweep:`, `short_list:`).** Each weight × (1 ± 0.25), one at a time, renormalised: 10 corners (A-screen-029). Short list = top 60 plus every candidate in the top 60 in ≥ 80 % of corners (A-screen-006). The top 30 is a reporting size, not a criterion. Ties are broken by a seeded permutation (seed 1).

**Metros (`metros:`, A-screen-013, approved).** Tier 1 Riyadh, Jeddah, Makkah, Madinah, Dammam–Khobar–Dhahran; tier 2 Taif, Buraidah, Tabuk, Abha–Khamis Mushait; tier 3 Jazan, Najran. Each is anchored on register rows (OSM coordinate, Census 2022 population with the row's own source id); a metro's distance is to its nearest anchor and its size the sum of its anchors.

**Equity lens** (not in the score, reported beside it): regional balance, towns with no station, freight-only corridors.

**Retired from plan v0.4 §1 (renumbered 31 Oct 2026).** F1 "≥ 15 km road distance" (was A-screen-003) → the served test, now A-screen-004 at 10 km straight-line (15 km road distance stays the documented alternative in A-screen-004's range). F2 "commute band" (was A-screen-004) → A-screen-005. F3 "economic role or population ≥ 50k" (was A-screen-005) → A-screen-003, without the 50k clause (50k is the pilot sampling tag A-screen-014 only). F4 "terrain raises cost class" (was A-screen-006) → the terrain criterion A-screen-024/-025; terrain also enters costs in R1c. A-screen-006 now means the short-list rule. Score criteria "population within 30 min road" and "corridor fit (detour factor, through-passenger penalty)" need road skims and corridor geometry; they are deferred to R2/R4 (corridor families and isochrones) and are not part of the CP1 screening score. "Unserved-ness as road time" is the rail-gap criterion on straight-line distance until R1a.

## 2. Appraisal standard and discount-rate set (proposal)
Rows in `docs/assumptions.md`; sources in `docs/sources/index.csv` (S-cp1-060…098, accessed 31 Oct 2026; detail in `docs/sources/cp1-item2-appraisal.md`).
- **Primary standard:** UK HM Treasury **Green Book** with **DfT TAG** unit values and methods (A2.4 for wider economic impacts), cross-checked against the **EU Guide to CBA of Investment Projects (Dec 2014)** and World Bank transport appraisal guidance; Saudi guidance (SAR, MEP, NCP) applied where published (none found yet). Departures stated in `docs/cba.md` (R5).
- **Central social discount rate (A-cba-001, CP1 D1a, 31 Oct 2026):** **3.00 % (years 1–30), 2.50 % (31–75), 2.25 % (76–125)**, real — the Green Book 2026 schedule (para 6.54, S-cp1-060; supplementary guidance para 3.8 and Annex A, S-cp1-061; quoted verbatim in `docs/status/verify-greenbook.md`). The DfT TAG A1.1 (May 2026) schedule 3.5 / 3.0 / 2.5 % (S-cp1-062, S-cp1-063) runs as a sensitivity.
- **Sensitivities (A-cba-002):** 5 % and 7 %. The EC benchmark is 5 % for Cohesion countries and 3 % otherwise, in §2.8.1 of the guide (not §2.8.8; S-cp1-067). No MDB transport guidance gives 7 %: it appears only in the World Bank 2016 note's OECD-derived table of national rates and its 2–10 % growth-linked range (S-cp1-069, S-cp1-070). ADB uses a 9 % minimum EIRR (S-cp1-072), an alternative upper bound.
- **Commercial/financial rate for FIRR (A-cba-003):** 6–8 %, assumed, as a premium over sovereign borrowing: 2026 USD sovereign points 4.875 % (10-year) and 5.875 % (30-year) in Jan 2026 (S-cp1-074), 5.598 % (10-year sukuk, Sep 2026, secondary, S-cp1-079). The evidence is nominal USD; the basis of the 6–8 % (real or nominal, USD or SAR) is a CP1 choice.
- **Horizons (A-cba-004):** 60 years after opening (Green Book para 6.11 "60 years for infrastructure, such as roads, railways", S-cp1-088; TAG A1.1 para 2.3.3, S-cp1-085); 30 and 40 years as finite-life scenario variants with residual value (TAG A1.1 paras 2.3.10–2.3.11, S-cp1-086; Green Book para 8.32, S-cp1-089); 100 years maximum as a sensitivity (TAG 2.3.5). No source gives 30 or 40 years as a rail standard. Price base 2025 SAR (A-cost-001).
- **Value of time (A-cba-010):** DfT TAG Table A1.3.1 (2023 GBP per hour: working 25.23 perceived / 30.03 market, commuting 15.51, other 7.08; S-cp1-092) transferred to KSA by the ratio of GDP per capita at PPP (2025: Saudi Arabia 73,783.56, UK 64,606.50 current international $, S-cp1-097, S-cp1-098; ratio 1.142, derived) raised to an income elasticity e: 1.015 (TAG A1.3 para 4.5.1, S-cp1-090) with 0.5–0.8 (World Bank TRN-15, S-cp1-095) as the sensitivity range, so a transfer factor of 1.07–1.14 (derived); fallback 0.3 × household income per head for non-work time (TRN-15, S-cp1-096). Assumed until a Saudi value-of-time study is found.
- Label for every appraisal output: synthetic demand, uncalibrated: scenario comparison, not a forecast; costs and benefits as P10/P50/P90.

## 3. Cost-register schema (proposal; aligned with the `cost-register` skill and `common/schemas.py:CostItem`)
`cities/ksa/costs/cost_register.yaml` (R1c), one item per row, validated by `CostItem`:
| field | values |
|---|---|
| `id` | `C-<category>-<slug>-nnn` (pattern `^C-[a-z0-9-]+$`) |
| `item` | free text |
| `category` | line_type, terrain, structure, system, station, depot, rolling_stock, signalling, electrification, power, land, utilities, design_pm, contingency, opex, renewal, financing |
| `line_type` | hsr, conventional_passenger, mixed, commuter, upgrade, n/a |
| `terrain` | flat_desert, dunes, sabkha, escarpment_mountain, coastal, n/a |
| `unit` | SAR_m_per_km, SAR_m_per_station, SAR_m_per_trainset, SAR_m_per_yr, SAR_per_train_km, pct_of_capex, pct_per_yr, SAR_m_lump |
| `currency`, `price_year` | ISO code; integer year |
| `low`, `central`, `high` | numbers or null (a null central is allowed: no point estimate without a distribution) |
| `source`, `status` | `S-` id or `assumed`; sourced, derived, assumed, unknown |
| `derivation`, `assumption_id`, `notes` | index used for a derived item (`cities/ksa/costs/index.yaml`), `A-cost-nnn` for an assumed item, free text |

`index.yaml` is the only price and FX index of the project (CP2 P2a, 31 Oct 2026; also used by the W5 benchmarks, the R1b `index-r1b.yaml` folded in and deleted) with rows `id, method, from_currency, from_year, to_currency, to_year, factor, source` (A-cost-001: 2025 SAR; A-cost-002: Saudi CPI for SAR items; for foreign-currency items the source economy's World Bank GDP deflator before conversion, then the 2025 rate and the peg 3.75; exceptions A-cost-307). Reference-class uplifts in `uplifts.yaml` (`reference-class-forecasting` skill), reported as P50/P80.

**The Landbridge rows proposed in `docs/costs-landbridge.md` §4, mapped to this schema** (R1c writes them; every value is that document's, nominal as printed):
| proposed row | id (proposal) | category / line_type / terrain | unit | low / central / high | price_year | status |
|---|---|---|---|---|---|---|
| programme as stated by SAR / MOT | `C-programme-landbridge-001` | line_type / mixed / n/a | SAR_m_lump | 100,000 / 100,000 / null | **2022 (assumed, A-cost-00n: the price year is not stated; statements of 2022 and 2026)** | derived (S-lb-001, S-lb-002, S-lb-003, S-046) |
| top-down per km, whole programme | `C-line-landbridge-perkm-001` | line_type / mixed / n/a | SAR_m_per_km | 45.9 / null / 66.7 | as above | derived (two denominators, not a distribution) |
| legacy estimate (history only) | `C-programme-landbridge-legacy-001` | line_type / mixed / n/a | SAR_m_lump | 26,000 / 26,250 / 26,600 | 2008–2011 tender basis: needs one integer year (assumed) | sourced, secondary (S-lb-014, S-052, S-lb-016, S-051) |
| Riyadh Rail Link package | `C-line-riyadh-rail-link-001` | line_type / mixed / n/a | SAR_m_lump | null / null / null | unknown | unknown (until the award notice) |

Gaps between the Landbridge proposal and the schema, for R1c (no schema change made here): (1) `price_year` is a required integer but the SR 100 bn price year is unknown, so it needs an `A-cost-` assumption; (2) the proposal's `scope` column has no field (goes in `notes`, or an optional `scope` field added additively); (3) there is no `layer` field, although Landbridge is a committed/under-procurement line (rule 5), so the layer goes in `notes` or an optional field; (4) `category` has no "programme" value, so whole-programme figures sit under `line_type` with `line_type: mixed`.

## 4. Benchmark country list
France (TGV/LGV), Japan (Shinkansen), Spain (AVE), Germany (ICE), China (CR HSR), South Korea (KTX), Italy (Frecciarossa + Italo open access), Morocco (Al Boraq), Turkey (YHT), UAE (Etihad Rail), Egypt (HSR under construction); cautionary class: California HSR, UK HS2 and others found; population-growth peers to be chosen in R1b (candidates: India, Indonesia, Türkiye; shrinking: Japan rural lines). Every named system gets a dossier or "no reliable data found".

## 5. Workstream and track plan (R1–R9) and region-scout batching
| phase | tracks (parallel) | model | est. runs | est. agent-hours |
|---|---|---|---|---|
| first session | R0 (main), DATASCOUT_1H, pilot (13 Hanko + 1 Opus merge) | Opus / Haiku | 16 | 10 |
| R1 | R1a data+network, R1b benchmarks, R1c costs, R1d funding+social (4 worktrees), INTEGRATE_R1 | Opus | 8–10 | 24 |
| R2 | 13 × REGION (Haiku, batches of 4), R2 merge+funnel+families (Opus), INTEGRATE_R2 | Haiku / Opus | 16 | 14 |
| R3 | demand + population scenarios (one heavy track), CP4 | Opus | 3 | 12 |
| R4 | network evaluation + Jeddah coupling (heavy; SUMO via TrafficTwin) | Opus | 3 | 12 |
| R5 | CBA | Opus | 3 | 10 |
| R6 | optimisation + phasing, CP5 | Opus | 3 | 12 |
| R7 | delivery model per corridor | Opus | 2 | 6 |
| R8 | report, dashboard, brief, bilingual summary, figures, CP6 | Opus | 5 | 16 |
| R9 | release prep, CP7 | Opus | 1 | 3 |
| R10 | film: pre-CP8 (4 runs), post-CP8 render/assemble/verify (4 runs) | Opus / Haiku | 8 | 20 |
| verification | VERIFY_<label> after every milestone | Fable | 15 | 8 |
| **total** | | | **≈ 85–90 runs** | **≈ 150 agent-hours** |

Region-scouts run in batches of 4 (MAX_PARALLEL), each a worktree `r2-<slug>`; TrafficTwin averaged about 91 minutes per run (41 agent-hours / 27 runs, from the brief); Haiku region sweeps are assumed to take 20–40 minutes each (estimate, to be measured in the pilot), so R2 is an overnight phase. Compute tracks (R3, R4, R6) run alone.

## 6. Estimated agent-hours and USD cost
TrafficTwin: 27 runs ≈ USD 420 ≈ USD 15.5/run (Opus-class). Estimate here: ~60 Opus-class runs × USD 15 + ~30 Haiku-class runs × USD 2 + ~15 verifier runs × USD 10 ≈ **USD 1,100–1,400 list price** (range reflects retries and the film). Actuals accrue in `docs/cost-log.md`; Tariq's subscription means these are reference figures. Wall time: 4–6 weeks of mostly overnight runs with checkpoints between phases.

## 7. Dependencies to add per milestone (none installed at R0; disk gate applies)
| milestone | packages / tools | disk |
|---|---|---|
| R1a | osmium-tool (brew), OSMnx, r5py (+ JVM) or OSRM build, GHSL/WorldPop tiles for KSA | 3–8 GB |
| R3 | PyMC | <1 GB |
| R4 | eclipse-sumo wheel (uses TrafficTwin's venv read-only where possible) | <1 GB |
| R6 | pymoo, OR-Tools or HiGHS | <1 GB |
| R8 | Node 22, Vite, React, deck.gl, MapLibre (npm) | ~0.5 GB |
| R10 | MLX (`mlx-lm`, `mlx-whisper`) + at most one Arabic open-weights LLM (≤ 5 GB, licence permitting; else the cached Qwen2.5-7B 4-bit), Whisper large-v3-turbo weights (~1.6 GB), 3–6 TTS candidates, fonts, Manim — no Ollama (removed 31 Oct 2026)  **Paid narration candidates under the model policy (Tariq, 31 Oct 2026):** Nabrah AI (Riyadh; public voices Daniah, Norah, Abdullah; licence register row: blocked for public release until Nabrah confirms publication/broadcast rights in writing) and ElevenLabs, in one A/B against the best open voice on the same 2-minute Saudi-dialect script, scored on place-name pronunciation, dialect naturalness, prosody and cost per finished minute; all three samples go to Tariq (paid-model request 1 in docs/STATUS.md; no account or spend before approval; `NABRAH_API_KEY` set by Tariq). No voice cloning of any real person without written consent. | 10–20 GB |

## 8. Disk plan (measured 31 Oct 2026)
- **Free now: 24 GiB of 460 GiB** (`df -h ~`, 31 Oct 2026, 02:00 +03; 95 % used). Earlier: ~17 GB at R0, 26 GiB at 30 Oct 18:30.
- **Thresholds (Tariq, 30 Oct 2026):** ≥ 15 GB free for R1a (skims, OSRM/r5 extracts): **met now** (24 GiB); ≥ 40 GB before R3; ≥ 50 GB before R10 renders and local models: **not met** (16 and 26 GiB short).
- **Reclaim candidates (measured 31 Oct 2026, `du -sh` and `docker system df`):** uv cache **7.9 GB** (`~/.cache/uv`; `uv cache clean` is safe, re-downloads on demand); Docker **19.5 GB used, of which 5.0 GB reclaimable** without removing active images or volumes (images 3.35, stopped containers 1.20, volumes 0.36, build cache 0.09; the coordinator's earlier "~16 GB" is the total, not the reclaimable part); Ollama models **25 GB** (`~/.ollama/models`; only if no model there is needed); Google cache **3.8 GB** (`~/Library/Caches/Google`). uv + Docker reclaimable + Google ≈ 16.7 GB, which only just reaches the 40 GB threshold before R3; the 50 GB threshold before R10 also needs Ollama's 25 GB or active Docker data removed. Tariq's call: nothing is deleted by a builder.
- **Done 31 Oct 2026:** uv cache (8.1 GiB), Docker (6.9 GB) and most of the Google cache reclaimed at 09:30 (34 GiB free); then Tariq removed Ollama and its 25 GB of models (**52 GiB free**, measured 31 Oct). The R3 gate (≥ 40 GiB) and the R10 gate (≥ 50 GiB) are met today; R10 model downloads are limited to one Arabic LLM (≤ 5 GB) plus Whisper and TTS weights, and the Hugging Face cache (Qwen2.5-7B/1.5B MLX, e5-large, Chatterbox) is reused.
- TrafficTwin holds ~18 GB (`data/` 9.0, `runs/` 7.9, `movies/` 1.4); symlinked, never copied. Models already in `~/.cache/huggingface` are reused.
- Every download over 500 MB: `df -h ~` first, size recorded in `docs/STATUS.md`.

## 9. Open questions: status after CP1_PREP (31 Oct 2026)
Status: **answered** (Tariq decided, or a run settled it with evidence), **proposed** (a recommendation awaits CP1), **open** (no proposal yet). The full questions as raised are in git history (`docs/plan.md` v0.4); the decision pack (`docs/cp1-decision-pack.md`) lists the choices.

| # | question (short) | status | answer or proposal |
|---|---|---|---|
| 1 | population threshold | answered | 10k with a 5k sensitivity (A-screen-001/002, Tariq 30 Oct). Rerun: the 5k run leaves the top 30 unchanged (docs/screening-pilot.md §7) |
| 2 | metro set | answered | three tiers (A-screen-013, Tariq 30 Oct) |
| 3 | discount-rate central case | answered (CP1 D1a, 31 Oct 2026) | Green Book 2026 schedule 3.00/2.50/2.25 % central (verified verbatim, docs/status/verify-greenbook.md); TAG 3.5/3.0/2.5 % as sensitivity (A-cba-001) |
| 4 | price base and index | answered | 2025 SAR, GASTAT CPI, World Bank deflators fallback, peg 3.75 (A-cost-001) |
| 5 | unattended overnight runs | answered | allowed for all phases with CP stops honoured (Tariq 30 Oct) |
| 6 | Landbridge SR 100 bn vs USD 7 bn | answered (analysis) | different vintages and scopes (docs/costs-landbridge.md; conflict C-001); price year of SR 100 bn still open (§3) |
| 7 | film register | answered | white/Najdi preference (A-film-001); W10 documents alternatives |
| 8 | external drive | answered | none for now (§8: reclaim candidates instead) |
| 9 | settlement or governorate population | proposed | settlement (place) figure for every row, governorate totals context only (templates and region-sweep skill, CP1_PREP) |
| 10 | centres without a population pass by rule 2 | proposed | keep rule 2 (rule 2 of the brief); the 14 Riyadh seats now have populations, so long-list rows with a sweep exclusion note fell from 22 to 8 |
| 11 | merged/composite places | proposed | one row per census place as tabulated (Hofuf with Al-Mubarraz, Yanbu' with its industrial city) until the GASTAT locality table allows a split; flagged in `notes` |
| 12 | GASTAT's own governorate list | open | still unreachable on 31 Oct 2026 (portal no connection; open.data.gov.sa API rejected the query: S-cp1-026…028). Coverage stays at 150 (S-073). Next: boe.gov.sa Law of Provinces, GASTAT yearbook |
| 13 | conflict rows (Abanat, Al-Bayḍā, Hala Ammar, Wādī al-Fara', Al-Qarā, Al-'Arḍiyāt) | proposed | Al-Qarā now located (OSM admin centre node 9327998071, S-cp1-003); the others stay flagged for R2 |
| 14 | one distance rule | proposed | R1a: road distance to the nearest station of a passenger service from `cities/ksa/lines/`; locate Jeddah Al-Sulaymaniyah station |
| 15 | committed layer | proposed | keep existing-only in the pilot (A-screen-030); the committed sensitivity leaves the top 30 unchanged; revert when committed geometry is sourced |
| 16 | served threshold 10 km vs 15 km road | proposed | 10 km straight-line now (A-screen-004), 15 km road in the range once skims exist |
| 17 | two criteria sets, two numberings | answered | one set (the YAML), one id scheme (§1; register note "renumbered 31 Oct 2026") |
| 18 | linear rail gap favours the far south | answered (pending CP1 approval) | capped log, cap 300 km (A-screen-021): Jazan 10 → 4 of the top 30; linear kept as a sensitivity. New issue: 36 % of long-list rows saturate at the cap |
| 19 | pilot-only choices (A-screen-025, -026, -028) | proposed | keep until DEM (R1a) and road skims; approve or adjust at CP1 |
| 20 | data gaps (secondary populations, assumed terrain, uneven roles) | proposed | citypopulation.de terms verified (`docs/licences.md`: figures CC BY, attribution required); 27 roles added with sources; 106 long-list rows still have no scored role, terrain assumed everywhere (DEM in R1a) |
| 21 | energy role; Hejaz layer; region-prefixed assumption ids | answered (energy, ids) / open (Hejaz) | `energy` added (A-screen-010); templates require `A-<slug>-nnn`; a historical-Hejaz field is not added (the `historical` line layer exists) |
| 22 | docver skipped worktrees | answered | fixed (`common/docver.py`, relative to the repository root; test added) |
| 23 | templates and skill on the merged schema; `region_sweep validate` | answered | done; `uv run python -m screening.region_sweep validate` passes on all 13 pilot files |
| 24 | raw files and /tmp scripts | answered (scripts) / open (raw files) | 44 scripts recovered into `screening/pilot_builders/`; the 40 Qassim Nominatim JSONs are still not in the manifest (R2 rule: raw files under `data/ksa/<slug>/raw/` and in the manifest) |
