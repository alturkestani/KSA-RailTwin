> **Document version:** docs/screening-pilot.md v0.7 | 31 Oct 2026 | Author: screening-analyst (PILOT_MERGE); §5, §7 and §8 refreshed by the CP2_PREP GASTAT addenda 1 and 2; sections 1 and 3–8 updated by CP1_PREP; §8 geo-verify back-test note by INTEGRATE_R1; §7 grid sensitivity and §8 settlement-universe counts by CP2_PREP | Status: draft

# National pilot: merged register and draft screening funnel

**Label: pilot, proposed criteria pending CP1; screening input, not a forecast.** Every threshold and weight below is a registered assumption (`docs/assumptions.md`, status `assumed`, approval `pending CP1`). The funnel ran on the 13 pilot registers only: a coarse sample built to test the schema (governorate centres, towns ≥ 50,000 and 4–6 stratified smaller towns per region). It is **not** the national register (R2) and was not padded with towns the pilots did not sweep. Scores rank candidates for further study; they do not say a line should be built. Populations are Census 2022 figures relayed by secondary sources (GASTAT's portal was unreachable, S-090); distances are straight-line (A-screen-027).

## 1. What ran (rule 10)

| step | command | output (gitignored `runs/`) |
|---|---|---|
| normalise | `uv run python -m screening.pilot_normalise --pattern "cities/ksa/regions/pilot-*.parquet"` | the 13 registers rewritten in place (Parquet + CSV) |
| merge | `uv run python -m screening.merge --pattern "cities/ksa/regions/pilot-*.parquet" --out cities/ksa/candidates-pilot.parquet --seed 1` | `cities/ksa/candidates-pilot.parquet`; `runs/screening-pilot/merge/meta.json` |
| long list | `uv run python -m screening.funnel long-list --in cities/ksa/candidates-pilot.parquet --threshold 10000 --sensitivity 5000 --seed 1` | `runs/screening-pilot/long-list/` |
| score | `uv run python -m screening.funnel score --weights cities/ksa/assumptions/screening_weights.yaml --sweep 0.25 --seed 1` | `runs/screening-pilot/score/` (`scores.parquet`, `sweep.parquet`, `ranks.parquet`, `summary.json`) |
| sensitivity: 5k | same two steps with `--threshold 5000`, run dirs `long-list-5k`, `score-5k` | `runs/screening-pilot/score-5k/` |
| sensitivity: committed layer | same with `use_committed: true` (the skill default), run dirs `long-list-committed`, `score-committed` | `runs/screening-pilot/score-committed/` (weights copy in `weights_used.yaml`) |
| sensitivity: linear rail gap (CP1_PREP) | `score --gap-measure linear`, run dir `score-linear-gap` (the v0.1 min-max measure) | `runs/screening-pilot/score-linear-gap/` |
| coverage | `uv run python -m screening.coverage` | `docs/coverage.md` |
| CP1_PREP data fixes | `uv run python -m screening.cp1_fixes.apply` (roles and item 5 rows, then the merge again) | the 13 registers (Parquet + CSV) |
| CP1_PREP whole chain | `./screening/run_pilot_funnel.sh 1` (merge, long list, score, 5k, linear gap, committed, coverage) | as above; the pre-CP1_PREP outputs are kept in `runs/screening-pilot-before-cp1/` |

**CP1_PREP rerun (31 Oct 2026):** score run `meta.json`: seed 1, config hash `8a63ce04910b…`, data hash (manifest) `885dae6682d8…`, code `session1-pilot-8-g127e382` (clean tree); three consecutive runs gave the same config hash and counts. Settings changed by CP1_PREP item 1: rail gap on a capped log scale (A-screen-021), `administrative` out of the role score and the role filter (A-screen-009), `energy` role (A-screen-010), 27 sourced roles added, 14 Riyadh seat populations, the Al-Qarā row (sections 3 and 8). **Before CP1_PREP (30 Oct 2026):** score run `meta.json`: seed 1, config hash `fe62981d2ad5…` (weights, sweep and the SHA-256 of the input files, so it does not depend on the run directory), data hash (manifest) `885dae6682d8…`, code `r0-41-gf158622-dirty` (the uncommitted change was this content-hash fix and the coverage note filter, committed straight after the run; the funnel's results are unchanged from the verified run). Same seed and inputs give identical scores and ranks (`tests/test_screening_pilot.py::test_funnel_deterministic`).

## 2. Merge and schema decisions (coordinator decisions 30 Oct 2026, 21:58)

- **13 branches merged** in alphabetical order (`git merge --no-ff pilot-<slug>`): every region's files kept. `common/schemas.py` was edited by asir, riyadh and tabuk in three different ways; the merges kept main's version and the coordinator's single design was applied once afterwards. `cities/ksa/sources.yaml`: eastern and hail both appended rows (union).
- **Schema** (`RegionRow`, `extra="forbid"` kept): `pop_type` stays `official | derived | grid`; new optional `pop_source_status` (`verified | secondary | unverified`), `primary_to_find`, `threshold_50k`, `pilot_sample`, `nearest_metro_tier` (1 | 2 | 3), `road_min_method`, `dist_method`, `notes`, and one field beyond the coordinator's list, **`osm_type`** (`node | way | relation`), because OSM node, way and relation ids overlap and the merge de-duplicates by OSM id. New validators: `threshold_50k` must agree with the settlement population (A-screen-014); an official figure from a secondary source needs `primary_to_find`; `pilot_sample` needs its reason in `notes`.
- **Rows rewritten** by `screening.pilot_normalise` (all 13 regions, not only madinah and qassim):
  - `pop_type: secondary` (al_baha, asir, hail, jazan, madinah, najran, northern_borders, qassim, riyadh, tabuk) → `official` + `pop_source_status: secondary` + `primary_to_find`. Every one of the 150 populated rows is a Census 2022 figure relayed by citypopulation.de (which credits GASTAT); none is an aggregator's own estimate, so none became `derived`.
  - al_jouf and eastern had written the same relayed figures as plain `official`: they got the same status fields.
  - **Makkah** had kept its populations out of the Parquet (only in the CSV column `population_secondary`): 17 populations restored from the CSV (rows aligned by OSM id, checked).
  - Pilot-only columns with no schema field (`sample_reason`, `pilot_reason`, `terrain_basis`, `terrain_source`, `terrain_status`, `osm_place_tag`, `coord_flag`, `coords_method`, `screen_stage`, `assumption_id`, `dist_station_qassim_km`, `row_id`) are kept verbatim in `notes` as `<column>: <value>`; `distance_method` → `dist_method`; `name_osm_type` → `osm_type`. `nearest_metro_tier` filled from the pilot's metro name with A-screen-013 where the pilot left it empty.
  - **Al-Qarā** (Al-Baha) has no coordinate source; `RegionRow` requires lat/lon, so the row is withheld (listed in the Parquet metadata and in `docs/coverage.md`, status "not yet swept").
  - Result: 185 rows, all valid `RegionRow`; 0 duplicates.
- **Terrain vocabulary**: the schema values stand (`flat_desert, dunes, sabkha, escarpment_mountain, coastal, mixed`). Mapping `sand_dunes → dunes`, `coastal_plain → coastal`: **0 rows needed it**: every pilot already wrote schema values (madinah and tabuk recorded the mapping in their status). The prompt words survive in `prompts/PILOT_REGION_*.md` (13 files and the template) and in four pilot region docs: coordinator to fix the templates.
- **Assumption ids**: the pilots reused `A-screen-pilot-001…007` with different meanings per region, so the merged register scopes each by region (`A-screen-pilot-002 [hail]`); nothing renumbered.
- **Sources**: 151 pilot rows appended to `docs/sources/index.csv` (ids unchanged, prefixed `S-<region>-`). The asir file had two rows with unquoted commas; the cells were rejoined by hand (S-asir-001, S-asir-003).

## 3. Funnel counts per region (CP1_PREP rerun, 31 Oct 2026)

Stage 1 = every register row. Long list = filters below at 10,000 (A-screen-001); served = within 10 km (A-screen-004) of an existing station, kept for the station-addition family. "Did not pass" = below the threshold, no sourced scored role, not a governorate centre (or excluded by the sweep). Counts from `runs/screening-pilot/long-list/counts.json`, `long-list-5k/` and `score/scores.parquet` (seed 1).

| region | all rows | long list (10k) | served bucket | long list (5k sensitivity) | did not pass | short list | top 30 | long-list rows carrying a sweep exclusion note |
|---|---|---|---|---|---|---|---|---|
| al_baha | 10 | 10 | 0 | 10 | 0 | 0 | 0 | 0 |
| al_jouf | 8 | 4 | 1 | 7 | 3 | 0 | 0 | 0 |
| asir | 18 | 18 | 0 | 18 | 0 | 9 | 3 | 1 |
| eastern | 22 | 17 | 3 | 17 | 2 | 5 | 1 | 0 |
| hail | 11 | 10 | 0 | 11 | 1 | 1 | 1 | 3 |
| jazan | 20 | 18 | 0 | 20 | 2 | 5 | 4 | 0 |
| madinah | 9 | 7 | 1 | 8 | 1 | 5 | 3 | 0 |
| makkah | 18 | 17 | 1 | 17 | 0 | 7 | 4 | 1 |
| najran | 9 | 9 | 0 | 9 | 0 | 2 | 1 | 3 |
| northern_borders | 8 | 4 | 0 | 5 | 4 | 3 | 1 | 0 |
| qassim | 19 | 15 | 0 | 17 | 4 | 6 | 1 | 0 |
| riyadh | 25 | 21 | 2 | 23 | 2 | 13 | 9 | 0 |
| tabuk | 9 | 7 | 0 | 7 | 2 | 4 | 2 | 0 |
| total | 186 | 157 | 8 | 169 | 21 | 60 | 30 | 8 |

**Before → after CP1_PREP:** all rows 185 → 186 (Al-Qarā added); long list at 10k 156 → 157; served 8 → 8; long list at 5k 168 → 169; did not pass 21 → 21; short list 60 → 60; long-list rows carrying a sweep exclusion note 22 → 8 (the 14 Riyadh seats now have a population and are `screened`). Per region the short list moved most in Riyadh (5 → 13) and Jazan (15 → 5).

Filters (skill stage 2; `cities/ksa/assumptions/screening_weights.yaml` v0.2, described in `docs/plan.md` §1):
- governorate centres always pass (rule 2), whatever their population;
- other rows pass if the sweep kept them (`screened`) and population ≥ 10,000 (A-screen-001; 5,000 sensitivity A-screen-002) **or** they have ≥ 1 sourced economic role other than `administrative` (A-screen-003, A-screen-009);
- served bucket: straight-line distance ≤ 10 km (A-screen-004, A-screen-027) to an **existing** line (pilot: existing layer only, A-screen-030; section 7).

The long list stays large (157 of 186) because the pilot sampled governorate centres, which pass by rule.

## 4. Weights, sweep and rank stability

| criterion | measure | weight | id |
|---|---|---|---|
| population | log10(population), min-max over the long list | 0.30 | A-screen-020 |
| rail gap | log10(1 + min(d, 300)) / log10(301), d = straight-line distance (km) to the nearest existing line; saturates at 300 km (cap range 200–500) | 0.20 | A-screen-021 |
| commute | max over metros 40–120 km away (A-screen-005) of tier factor (1.0 / 0.6 / 0.3, A-screen-026) × log10(metro population) / log10(largest) | 0.20 | A-screen-022 |
| economic roles | distinct sourced roles except `administrative` (A-screen-009), capped at 3 (A-screen-008), ÷ 3 | 0.20 | A-screen-023 |
| terrain | 1 + penalty (flat/coastal 0, dunes/sabkha −0.5, escarpment −1, mixed −0.5) | 0.10 | A-screen-024, A-screen-025 |

Metros (A-screen-013) are anchored on register rows as before (populations: S-080, S-makkah-001, S-madinah-001, S-eastern-001, S-qassim-002, S-tabuk-002, S-asir-001, S-jazan-002, S-najran-002). Makkah, Madinah and Riyadh sit in the served bucket (existing stations within 10 km), so they are metros for the commute criterion but are not scored themselves.

**Sweep** (A-screen-029): each weight × 0.75 and × 1.25, one at a time, renormalised: 10 corners. **Short list** (A-screen-006): top 60 plus any candidate in the top 60 in ≥ 80 % of corners: 60 candidates (none added by the stability rule).

**Rank stability of the top 30: 21 of 30 (0.70) stay in the top 30 in all 10 corners** (before CP1_PREP: 24 of 30, 0.80). Overlap of each corner's top 30 with the base top 30: population −/+ 28 / 28; rail gap 28 / 28; commute 26 / 27; economic roles 28 / 27; terrain 29 / 27. The nine that leave in some corner (share of corners in the top 30): Durma 0.9, Bish 0.9, Huraymila 0.8, Thuwal 0.8, Wadi ad-Dawasir 0.8, Al-Ula 0.7, Al-Hariq 0.6, Muhayil 0.6, Ḥā'il 0.5. The lower stability is the analysis expected from the cap: with 36 % of long-list rows saturated at the cap (rail-gap score 1.0) the scores bunch, so small weight changes reorder the 20–35 band.

## 5. Top 30 of the short list (pilot, proposed criteria pending CP1; CP1_PREP rerun, refreshed after the CP2_PREP GASTAT addendum)

**GASTAT addendum rerun (31 Oct 2026, seed 1, `./screening/run_pilot_funnel.sh 1`).** The relayed Census 2022 city figures (S-cp2-gastat-001) replaced the aggregator figures on 58 register rows (identical values re-sourced, except Jubail 474,679 → 302,446 and Yanbu' 331,916 → 258,777; C-cp2-601/602). Long list 157, served 8, short list 60 and top-30 stability 21 / 30 are unchanged, the top 30 holds the same towns, and only three ranks moved: Jizan 4 → 3, Aṭ-Ṭa'if 5 → 4, Yanbu' al-Bahr 3 → 5 (the run before the addendum is archived in `runs/cp2_prep/addendum/before/`). The sensitivities in §7 give the same counts as before (5k: 169 long, 21 / 30; linear gap 24 / 30; committed layer 156 long, 9 served, 22 / 30). The table below is regenerated from `runs/screening-pilot/score/scores.parquet`. **Primary GASTAT rerun (addendum 2, 31 Oct 2026, seed 1, `uv run python -m screening.gastat primary --seed 1` then `./screening/run_pilot_funnel.sh 1`).** 151 register rows now carry the primary Census 2022 TA1 city figure (S-cp2-gastat-008, `verified`); all were identical to the figures they replace except the Ash Shaharin row (9,994 → 5,518, C-gastat-002; below 10k before and after). Long list 157, served 8, short list 60, stability 21 / 30, the top 30 and every rank in it are unchanged; the sensitivities give the same counts. Population sources in the table are re-read from the scores file.

Criterion columns are the scaled criterion values (0–1) before weighting; score = weighted sum; "imputed" lists criteria filled by A-screen-028. Source: `runs/screening-pilot/score/scores.parquet` (seed 1, code `session1-pilot-8-g127e382`); "rank before item 1" from `runs/screening-pilot-before-cp1/score/scores.parquet`.

| rank | town (EN / AR) | region | population (source) | population | rail gap | commute | roles | terrain | score | rank range, 10 corners | share of corners in top 30 | imputed criteria | rank before item 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jiddah / جدة | makkah | 3,712,917 (S-cp2-gastat-008) | 1.000 | 0.452 | 0.932 | 1.000 | 0.500 | 0.8269 | 1–1 | 1.0 | terrain | 6 |
| 2 | Jubail / الجبيل | eastern | 302,446 (S-cp2-gastat-008) | 0.653 | 0.772 | 0.919 | 1.000 | 0.500 | 0.7840 | 2–2 | 1.0 | terrain | 7 |
| 3 | Jizan / جيزان | jazan | 173,919 (S-cp2-gastat-008) | 0.576 | 1.000 | 0.000 | 1.000 | 1.000 | 0.6729 | 3–6 | 1.0 | — | 1 |
| 4 | Aṭ-Ṭa'if / الطائف | makkah | 563,282 (S-cp2-gastat-008) | 0.739 | 0.739 | 0.932 | 0.333 | 0.500 | 0.6727 | 3–5 | 1.0 | terrain | 15 |
| 5 | Yanbu' al-Bahr / ينبع البحر | madinah | 258,777 (S-cp2-gastat-008) | 0.631 | 0.902 | 0.000 | 1.000 | 1.000 | 0.6697 | 4–7 | 1.0 | — | 14 |
| 6 | Badr / بدر | madinah | 30,494 (S-cp2-gastat-008) | 0.335 | 0.841 | 0.899 | 0.667 | 0.500 | 0.6318 | 4–8 | 1.0 | — | 12 |
| 7 | Rimah / رماح | riyadh | 25,031 (S-cp2-gastat-008) | 0.308 | 0.829 | 1.000 | 0.333 | 1.000 | 0.6249 | 5–9 | 1.0 | — | 13 |
| 8 | Tabuk / تبوك | tabuk | 594,350 (S-cp2-gastat-008) | 0.746 | 0.983 | 0.000 | 0.667 | 0.500 | 0.6038 | 6–11 | 1.0 | — | 5 |
| 9 | Najrān / نجران | najran | 381,431 (S-cp2-gastat-008) | 0.685 | 1.000 | 0.000 | 0.667 | 0.500 | 0.5888 | 7–13 | 1.0 | — | 2 |
| 10 | Ar-Rass / الرس | qassim | 107,902 (S-cp2-gastat-008) | 0.510 | 0.785 | 0.505 | 0.333 | 1.000 | 0.5778 | 9–12 | 1.0 | — | 19 |
| 11 | Arar / عرعر | northern_borders | 199,247 (S-cp2-gastat-008) | 0.595 | 0.800 | 0.000 | 0.667 | 1.000 | 0.5719 | 10–15 | 1.0 | — | 11 |
| 12 | Ad-Dilam / الدلم | riyadh | 39,267 (S-cp2-gastat-008) | 0.370 | 0.780 | 1.000 | 0.000 | 1.000 | 0.5670 | 8–18 | 1.0 | economic_roles | 70 |
| 13 | Al-Muzahimiyah / المزاحمية | riyadh | 55,604 (S-cp2-gastat-008) | 0.418 | 0.684 | 1.000 | 0.000 | 1.000 | 0.5624 | 9–21 | 1.0 | economic_roles | 21 |
| 14 | Al-Ḥawiyah / الحوية | makkah | 171,610 (S-cp2-gastat-008) | 0.574 | 0.757 | 0.932 | 0.000 | 0.500 | 0.5601 | 10–20 | 1.0 | economic_roles,terrain | 23 |
| 15 | Az-Zulfi / الزلفي | riyadh | 68,317 (S-cp2-gastat-008) | 0.447 | 0.744 | 0.505 | 0.333 | 1.000 | 0.5505 | 14–18 | 1.0 | — | 26 |
| 16 | Sabya / صبيا | jazan | 72,086 (S-cp2-gastat-008) | 0.454 | 1.000 | 0.521 | 0.000 | 1.000 | 0.5405 | 14–23 | 1.0 | economic_roles | 3 |
| 17 | Bisha / بيشة | asir | 115,537 (S-cp2-gastat-008) | 0.520 | 1.000 | 0.000 | 0.667 | 0.500 | 0.5392 | 12–23 | 1.0 | — | 51 |
| 18 | Al-Wajh / الوجه | tabuk | 33,868 (S-cp2-gastat-008) | 0.350 | 1.000 | 0.000 | 0.667 | 1.000 | 0.5382 | 13–24 | 1.0 | — | 22 |
| 19 | Khamis Mushait / خميس مشيط | asir | 535,065 (S-cp2-gastat-008) | 0.732 | 1.000 | 0.000 | 0.333 | 0.500 | 0.5362 | 14–28 | 1.0 | — | 17 |
| 20 | Farasan / فرسان | jazan | 10,118 (S-cp2-gastat-008) | 0.182 | 1.000 | 0.230 | 0.667 | 1.000 | 0.5340 | 14–26 | 1.0 | — | 4 |
| 21 | Al-Kharj / الخرج | riyadh | 295,462 (S-cp2-gastat-008) | 0.650 | 0.858 | 0.000 | 0.333 | 1.000 | 0.5332 | 15–27 | 1.0 | — | 31 |
| 22 | Durma / ضرما | riyadh | 16,344 (S-cp2-gastat-008) | 0.249 | 0.718 | 1.000 | 0.000 | 1.000 | 0.5182 | 16–32 | 0.9 | economic_roles | 75 |
| 23 | Al-Ula / العلا | madinah | 40,760 (S-cp2-gastat-008) | 0.375 | 0.994 | 0.000 | 1.000 | 0.000 | 0.5115 | 18–36 | 0.7 | — | 34 |
| 24 | Huraymila / حريملاء | riyadh | 9,842 (S-cp2-gastat-008) | 0.179 | 0.772 | 1.000 | 0.000 | 1.000 | 0.5079 | 18–39 | 0.8 | economic_roles | 73 |
| 25 | Bish / بيش | jazan | 32,679 (S-cp2-gastat-008) | 0.345 | 1.000 | 0.521 | 0.000 | 1.000 | 0.5076 | 21–31 | 0.9 | economic_roles | 9 |
| 26 | Thuwal / ثول | makkah | 26,957 (S-cp2-gastat-008) | 0.318 | 0.510 | 0.960 | 0.333 | 0.500 | 0.5062 | 20–38 | 0.8 | terrain | 28 |
| 27 | Wadi ad-Dawasir / وادي الدواسر | riyadh | 77,433 (S-cp2-gastat-008) | 0.464 | 1.000 | 0.000 | 0.333 | 1.000 | 0.5059 | 23–32 | 0.8 | — | 110 |
| 28 | Al-Hariq / الحريق | riyadh | 6,895 (S-cp2-gastat-008) | 0.129 | 0.831 | 1.000 | 0.000 | 1.000 | 0.5050 | 19–42 | 0.6 | economic_roles | 64 |
| 29 | Muhayil / محايل عسير | asir | 97,967 (S-cp2-gastat-008) | 0.497 | 1.000 | 0.521 | 0.000 | 0.500 | 0.5032 | 25–33 | 0.6 | economic_roles | 29 |
| 30 | Ḥā'il / حائل | hail | 448,623 (S-cp2-gastat-008) | 0.707 | 0.524 | 0.000 | 0.667 | 0.500 | 0.5004 | 21–37 | 0.5 | — | 16 |

By region, the top 30 holds Riyadh 9, Makkah 4, Jazan 4, Madinah 3, Asir 3, Tabuk 2, and 1 each from Eastern, Najran, Qassim, Northern Borders and Ḥā'il; Al-Baha and Al-Jouf have none.

**Before → after.** 22 of the 30 are the same towns. Entered: Ad-Dilam, Bisha, Al-Kharj, Durma, Al-Ula, Huraymila, Wadi ad-Dawasir, Al-Hariq (six of them Riyadh seats). Left: Sharūrah, Samtah, Abha, Ad Dayer, Al Aydabi, Ad Darb, Ahad al Musarihah, Abu Arish (seven in the far south). Decomposition (analysis, same seed): with the **new data and the old linear gap** (`score-linear-gap`) the top 30 shares 24 towns with the old run, so the data fixes (new Riyadh populations, roles, `administrative` out) account for 6 changes; **on the new data**, switching linear → capped log shares 26 of 30, so the measure change accounts for 4 (Sharūrah, Samtah, Buraydah and Zahran al-Janub are top 30 under the linear gap only).

<details><summary>Before item 1 (PILOT_MERGE run, 30 Oct 2026; linear rail gap, administrative scored, pre-fix registers)</summary>

| rank | town (EN / AR) | region | population (source) | population | rail gap | commute | roles | terrain | score | rank range, 10 corners | share of corners in top 30 | imputed criteria |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jizan / جيزان | jazan | 173,919 (S-jazan-002) | 0.576 | 0.724 | 0.000 | 1.000 | 1.000 | 0.6176 | 1–2 | 1.0 | — |
| 2 | Najrān / نجران | najran | 381,431 (S-najran-002) | 0.685 | 0.791 | 0.000 | 1.000 | 0.500 | 0.6136 | 1–2 | 1.0 | — |
| 3 | Sabya / صبيا | jazan | 72,086 (S-jazan-002) | 0.454 | 0.697 | 0.521 | 0.333 | 1.000 | 0.5465 | 3–6 | 1.0 | — |
| 4 | Farasan / فرسان | jazan | 10,118 (S-jazan-002) | 0.182 | 0.721 | 0.230 | 1.000 | 1.000 | 0.5449 | 3–7 | 1.0 | — |
| 5 | Tabuk / تبوك | tabuk | 594,350 (S-tabuk-002) | 0.746 | 0.332 | 0.000 | 1.000 | 0.500 | 0.5403 | 3–8 | 1.0 | — |
| 6 | Jiddah / جدة | makkah | 3,712,917 (S-makkah-001) | 1.000 | 0.003 | 0.932 | 0.000 | 0.500 | 0.5370 | 3–11 | 1.0 | economic_roles, terrain |
| 7 | Jubail / الجبيل | eastern | 474,679 (S-eastern-001) | 0.715 | 0.090 | 0.919 | 0.333 | 0.500 | 0.5330 | 4–10 | 1.0 | terrain |
| 8 | Sharūrah / شرورة | najran | 89,456 (S-najran-002) | 0.484 | 0.939 | 0.000 | 0.667 | 0.500 | 0.5163 | 5–12 | 1.0 | — |
| 9 | Bish / بيش | jazan | 32,679 (S-jazan-002) | 0.345 | 0.664 | 0.521 | 0.333 | 1.000 | 0.5071 | 6–12 | 1.0 | — |
| 10 | Samtah / صامطة | jazan | 43,301 (S-jazan-002) | 0.384 | 0.786 | 0.230 | 0.667 | 0.500 | 0.5017 | 7–16 | 1.0 | — |
| 11 | Arar / عرعر | northern_borders | 199,247 (S-northern_borders-001) | 0.595 | 0.108 | 0.000 | 1.000 | 1.000 | 0.5001 | 6–14 | 1.0 | — |
| 12 | Badr / بدر | madinah | 30,494 (S-madinah-001) | 0.335 | 0.139 | 0.899 | 0.667 | 0.500 | 0.4916 | 8–15 | 1.0 | — |
| 13 | Rimah / رماح | riyadh | 25,031 (S-riyadh-006) | 0.308 | 0.130 | 1.000 | 0.333 | 1.000 | 0.4850 | 9–17 | 1.0 | — |
| 14 | Yanbu' al-Bahr / ينبع البحر | madinah | 331,916 (S-madinah-001) | 0.666 | 0.204 | 0.000 | 0.667 | 1.000 | 0.4737 | 12–16 | 1.0 | — |
| 15 | Aṭ-Ṭa'if / الطائف | makkah | 563,282 (S-makkah-001) | 0.739 | 0.072 | 0.932 | 0.000 | 0.500 | 0.4725 | 10–19 | 1.0 | economic_roles, terrain |
| 16 | Ḥā'il / حائل | hail | 448,623 (S-hail-001) | 0.707 | 0.011 | 0.000 | 1.000 | 0.500 | 0.4644 | 13–21 | 1.0 | — |
| 17 | Khamis Mushait / خميس مشيط | asir | 535,065 (S-asir-001) | 0.732 | 0.575 | 0.000 | 0.333 | 0.500 | 0.4512 | 14–23 | 1.0 | — |
| 18 | Abha / أبها | asir | 334,290 (S-asir-001) | 0.667 | 0.564 | 0.000 | 0.667 | 0.000 | 0.4462 | 16–24 | 1.0 | — |
| 19 | Ar-Rass / الرس | qassim | 107,902 (S-qassim-002) | 0.510 | 0.098 | 0.505 | 0.333 | 1.000 | 0.4403 | 17–24 | 1.0 | — |
| 20 | Ad Dayer / الدائر | jazan | 15,752 (S-jazan-002) | 0.244 | 0.714 | 0.521 | 0.333 | 0.500 | 0.4368 | 15–25 | 1.0 | — |
| 21 | Al-Muzahimiyah / المزاحمية | riyadh | 55,604 (S-riyadh-004) | 0.418 | 0.049 | 1.000 | 0.000 | 1.000 | 0.4353 | 15–29 | 1.0 | economic_roles |
| 22 | Al-Wajh / الوجه | tabuk | 33,868 (S-tabuk-002) | 0.350 | 0.470 | 0.000 | 0.667 | 1.000 | 0.4323 | 18–27 | 1.0 | — |
| 23 | Al-Ḥawiyah / الحوية | makkah | 171,610 (S-makkah-001) | 0.574 | 0.081 | 0.932 | 0.000 | 0.500 | 0.4250 | 17–33 | 0.9 | economic_roles, terrain |
| 24 | Al Aydabi / العيدابي | jazan | 10,357 (S-jazan-002) | 0.186 | 0.711 | 0.521 | 0.333 | 0.500 | 0.4187 | 20–29 | 1.0 | — |
| 25 | Ad Darb / الدرب | jazan | 5,216 (S-jazan-002) | 0.091 | 0.601 | 0.521 | 0.333 | 1.000 | 0.4182 | 17–32 | 0.9 | — |
| 26 | Az-Zulfi / الزلفي | riyadh | 68,317 (S-riyadh-009) | 0.447 | 0.074 | 0.505 | 0.333 | 1.000 | 0.4166 | 22–30 | 1.0 | — |
| 27 | Ahad al Musarihah / أحد المسارحة | jazan | 25,670 (S-jazan-002) | 0.311 | 0.773 | 0.230 | 0.333 | 0.500 | 0.4107 | 22–31 | 0.9 | — |
| 28 | Thuwal / ثول | makkah | 26,957 (S-makkah-001) | 0.318 | 0.009 | 0.960 | 0.333 | 0.500 | 0.4060 | 21–44 | 0.7 | terrain |
| 29 | Muhayil / محايل عسير | asir | 97,967 (S-asir-001) | 0.497 | 0.491 | 0.521 | 0.000 | 0.500 | 0.4013 | 25–38 | 0.6 | economic_roles |
| 30 | Abu Arish / أبو عريش | jazan | 69,632 (S-jazan-002) | 0.449 | 0.735 | 0.000 | 0.333 | 0.500 | 0.3984 | 23–37 | 0.5 | — |

By region, the top 30 holds Jazan 10, Makkah 4, Riyadh 3, Asir 3, Najran 2, Tabuk 2, Madinah 2, and 1 each from Eastern, Northern Borders, Ha'il and Qassim; Al-Baha and Al-Jouf have none.

</details>

## 6. Which criteria drive the ranking

`runs/screening-pilot/score/summary.json`, `drivers` (CP1_PREP rerun; before-CP1_PREP values in brackets, from `runs/screening-pilot-before-cp1/score/summary.json`):

| criterion | weight | mean share of the score, top 30 | mean share, whole long list | Spearman with the score (long list) |
|---|---|---|---|---|
| population | 0.30 | 0.254 (0.308) | 0.212 (0.273) | 0.631 (0.534) |
| rail gap | 0.20 | 0.299 (0.173) | 0.466 (0.220) | −0.010 (0.267) |
| commute | 0.20 | 0.166 (0.180) | 0.098 (0.131) | 0.413 (0.437) |
| economic roles | 0.20 | 0.144 (0.195) | 0.067 (0.127) | 0.587 (0.576) |
| terrain | 0.10 | 0.136 (0.145) | 0.157 (0.249) | 0.380 (0.115) |

Reading (analysis): **population and economic roles separate the top from the rest**; commute adds the metro belts (Riyadh's ring now shows: four newly populated Riyadh seats in the top 30, Ad-Dilam, Durma, Huraymila and Al-Hariq, sit 59–114 km straight-line from Riyadh on flat terrain, commute = 1.0; `scores.parquet` `nearest_metro_km_calc`). **Rail gap no longer pulls the far south up**: on the capped log scale every row beyond ~150 km scores 0.88 or more, and every row beyond 300 km scores 1.0, so the criterion now mainly separates towns near a line (e.g. Jiddah 0.45 at 12 km) from the rest. It still carries a large share of every score (0.466 of the average long-list score) but has almost no rank correlation with the total (−0.01): it is close to a constant for most rows. CP1 may prefer a smaller cap (A-screen-021 range 200–500 km) or a lower weight; the linear sensitivity is section 7.

## 7. Sensitivities (CP1_PREP rerun)

- **5,000 threshold** (A-screen-002): 12 more rows reach the long list (169); all rank 35th or lower (Al-Uyaynah 35, Al-Jubaylah 39, Abu as Sadad 47, Misliyah 64, Dakhnah 78, the rest 117th or lower). **Top 30 unchanged (30 / 30)**, stability 21 / 30. Before CP1_PREP: 30 / 30, 24 / 30.
- **Linear rail gap** (the v0.1 measure, `--gap-measure linear`): top 30 shares 26 of 30 with the base; in: Sharūrah (13), Samtah (17), Buraydah (29), Zahran al-Janub (30); out: Durma, Al-Ula, Huraymila, Al-Hariq. Stability 24 / 30.
- **Committed layer included** (skill default; A-screen-030 set to true via `--use-committed`): only Asir (18 rows) and Riyadh (25 rows) filled `dist_committed_km`, both to Landbridge stops whose locations are not published (S-061 unreadable; S-062 names only). Including it moves **Ad-Dawadmi** into the served bucket on an unlocated stop (long list 156, served 9); **top 30 unchanged (30 / 30)**, stability 22 / 30. The pilot keeps the existing layer only until committed geometry is sourced (R1a).

- **Grid populations ÷ 0.71, ÷ 0.64 and ÷ 0.48 (CP2 P1a, report only; A-screen-031…039).** `uv run python -m screening.funnel sensitivity-grid --ratio 0.71 --seed 1 --run-dir runs/screening-pilot/sens-grid-071` (and `--ratio 0.64` → `sens-grid-064`, `--ratio 0.48` → `sens-grid-048`; each writes `flips.csv`, `counts.json`, `meta.json`). Run after `screening.gastat apply` and `screening.gastat primary`. **Old and new values:** 0.64 was the grid / tabulated median 0.637 of the first back-test on 164 rows (A-screen-034); 0.48 the median 0.480 against the 60 relayed Census 2022 cities (A-screen-036, addendum 1); **0.71 is the median 0.710 against the 201 settlements matched to the primary GASTAT cities of 5,000 or more (A-screen-039, addendum 2; `docs/geo-verify.md` §12), the ratio this sensitivity now uses.** The ≥ 10k test is re-run under the P1a rule (`rule`: a grid-only figure counts only if a second method agrees within 30 %, re-checked on the corrected figure, so flips can go either way) and as plain arithmetic (`raw`: population ≥ 10k, flips up only).

| table | ratio | rows | grid-only rows | grid-only with a second-method value | grid-only ≥ 10k (base) | grid-only ≥ 10k (÷ ratio) | `tag_10k` under the rule, base | `tag_10k` under the rule, ÷ ratio | flips under the rule (up / down) | raw flips (up / down) |
|---|---|---|---|---|---|---|---|---|---|---|
| pilot register (`cities/ksa/candidates-pilot.parquet`) | 0.71, 0.64 and 0.48 | 186 | 0 | 0 | 0 | 0 | 117 | 117 | 0 / 0 | 0 / 0 |
| settlement universe (`cities/ksa/zones/settlements.parquet`) | **0.71** | 7,371 | 7,076 | 4 | 37 | 70 | 143 | 144 | 1 / 0 | 33 / 0 |
| settlement universe | 0.64 | 7,371 | 7,076 | 4 | 37 | 92 | 143 | 144 | 1 / 0 | 55 / 0 |
| settlement universe | 0.48 | 7,371 | 7,076 | 4 | 37 | 164 | 143 | 144 | 1 / 0 | 127 / 0 |

Reading: **the pilot base case is unchanged by the sensitivity** — the pilot register has no grid-only row (the funnel was run before and after the P1a code, `runs/cp2_prep/item1/{before,after}/`, and again after each GASTAT addendum, §5). In the settlement universe four grid-only rows carry a second-method value (the Census 2010 city grown at its governorate ratio, A-screen-035; two of the six in addendum 1 are now primary-matched); none is within 30 % in the base case. **Under the rule one row flips up at every ratio: Al-Saih (Riyadh)**, grid 138,604, 2010-growth estimate 232,644 (68 % apart; 19 % at ÷ 0.71); nothing flips down. As arithmetic, ÷ 0.71 lifts 33 grid-only rows above 10,000 (`flips.csv`, `flip_raw = up`): these are the settlements whose status would flip if a second method corroborated them. Never applied to the base case.

## 8. Data caveats found by the merge (fix in R1a / R2), and the CP1_PREP role and population fixes

**Settlement universe by population basis (CP2 P1a, 31 Oct 2026; A-screen-031…039; after GASTAT addenda 1 and 2).** Rule applied to `cities/ksa/zones/settlements.parquet` (7,371 rows) by `screening.gastat apply` (addendum 1) and `screening.gastat primary` (addendum 2; `runs/gastat/primary/summary.json`): **official 215**, of which **201 `verified`** (primary GASTAT Census 2022 TA1 city of 5,000 or more, S-cp2-gastat-008; 202 cities, Alhufuf + Almubriz combined) and 14 `secondary` (citypopulation.de figures the primary city table does not list); **derived 80** (OSM `population` tags), of which **24 corroborated** and **56 uncorroborated** against the WorldPop grid within 30 % (reporting only: derived rows are not gated, A-screen-031 (b)); **grid 7,076, all grid-unverified, 0 grid-corroborated** (4 have a 2010-growth value, none within 30 %). Rows ≥ 10,000: official 134 (133 verified), derived 9, grid-only 37 (all gated: `tag_10k = false`, `exclusion_reason: "grid-only population, uncorroborated"`). `tag_10k` is **143** (141 after addendum 1; 181 as built by `network.zones`). The 37 grid-only rows ≥ 10k include two large ones, Al-Saih (Riyadh, 138,604; its Census 2010 figure was 234,607, S-cp2-gastat-005) and Ash Sharai (Makkah, 114,461): neither name is in the primary city table (Al-Saih lies in Al-Kharj governorate and may be counted inside the Al-Kharj city figure: not verified), so they need a second method in R2, not a pass on the grid.

**GASTAT tables (CP2_PREP item 1 addenda, 31 Oct 2026).** Addendum 2: the primary TA1 exports (S-cp2-gastat-007/008) supersede the relayed DataPulse file, which matches them exactly (150 / 150 governorates, 60 / 60 cities, total, Saudi and non-Saudi; C-gastat-001). 202 of 271 primary cities are matched to settlements (tiers and the 69 unmatched with reasons: `docs/network.md` §Population basis); the control total (A-screen-037): grid-filled settlements outside the matched cities sum to 4,557,403 against the primary "Other (< 5,000)" row of 3,683,816, explained by the 915,148 people of the unmatched primary cities (residual 4,598,964); 7 regions exceed their residual and 2,048 grid rows are flagged (172 possible double counting with a city extent, 1,876 grid over-count or boundary mismatch). Census 2010 cities > 5,000 grown at the governorate ratio (A-screen-035) back-test against the 138 official cities they matched in addendum 1 at a median absolute error of 16.9 % (IQR 7.1–36.6 %). **WorldPop back-test** (settlement allocation, A-r1a-004 radius): against the 201 primary-matched settlements median grid / census **0.710** (IQR 0.370–1.157, median absolute error 49.6 %, 61 within 30 %); against the 60 relayed cities (addendum 1) 0.480 (IQR 0.307–0.727); first back-test on 164 rows 0.637 (IQR 0.332–1.104); governorate polygons 1.280 (IQR 1.018–1.682, n = 149). The sensitivity in §7 uses 0.71 (A-screen-039); it is not applied to the base case. Not available: Census 2022 localities below 5,000 and 2023–25 regional estimates, so below city level the WorldPop gap-fill stays, under the P1a gate. Details: `docs/network.md` §Population basis, `docs/geo-verify.md` §11–§12.

**Economic roles added by CP1_PREP item 1.3 (31 Oct 2026).** Sources `S-cp1-100`…`S-cp1-119` (`docs/sources/index.csv`, access date 2026-10-31; 15 verified, 12 secondary of the 27 applied); lines in `screening/cp1_fixes/roles.csv` (applied by `screening.cp1_fixes.apply`). Per region: **makkah 7** (Makkah hajj_umrah; Jiddah port, airport, hajj_umrah gateway; Rābigh energy and port, the port tied to the governorate via King Abdullah Economic City; Aṭ-Ṭa'if airport), **eastern 7** (Jubail port and energy; Ras Tanura energy; Abqaiq energy; Hofuf airport; Al-Qaisumah airport; Khobar tourism, governorate-level), **riyadh 4** (Riyadh airport and university; Wadi ad-Dawasir airport; Ad-Dawadmi airport), **madinah 3** (Yanbu' energy and airport; Al-Ula airport), **northern_borders 2** (Arar, Turaif airports), **jazan 1** (Jizan airport), **asir 1** (Bisha airport), **qassim 1** (Buraydah airport), **al_baha 1** (Al-Bāḥah airport); **al_jouf, hail, najran, tabuk 0**. Total 27. Not added (decisions recorded in `roles.csv`): Tabuk giga_project (NEOM tied to Tabuk Province only, S-cp1-114; a CP1 decision), Riyadh giga_project (Diriyah Gate is on the Ad-Dir'iyah row already), Hafar al-Batin airport (the one Al-Qaisumah/Hafr Al-Batin airport is counted on the Al-Qaisumah row). None found: Rābigh giga_project, Khobar port/airport/energy, Umluj airport (Red Sea International is in Hanak, S-cp1-118), Al-Qurayyat airport (not in the GACA report, S-cp1-100). Rule applied (A-screen-011): a role counts when its source ties it to the town, or to the governorate whose centre the row is; a region-level tie does not count.

**Geo-verify back-test (GEO_VERIFY, track r1a, merged by INTEGRATE_R1 on 31 Oct 2026).** Both independent population estimators failed the 30 % back-test gate (A-geo-*, `docs/geo-verify.md` §3; run `runs/geo_verify/backtest/`, seed 1, 10 stratified settlements against relayed Census 2022 figures): median absolute error **grid 67 %, buildings × occupancy 59 %**; the best setting inside the declared ranges reached 42 % / 52 %. Decision: **record-only**. The estimates are written into the `notes` column of the 13 pilot registers (186 rows; 140 rows got an estimate) and the divergences > 25 % are listed as C-geo-001…103 in `docs/sources/conflicts.md`; **no estimate enters `population`, the funnel or the ranking**. The funnel counts and the top 30 in this document are unchanged by the merge (only `notes` changed in `cities/ksa/candidates-pilot.parquet`).

**Populations and rows added by CP1_PREP item 5.** 14 Riyadh governorate seats got a Census 2022 seat-town population (S-cp1-012…025, citypopulation.de crediting GASTAT, `secondary`, `primary_to_find` = the GASTAT locality table; seat identity inferred by name match, Layla from the pilot register) and are now `screened`. Al-Qarā (Al-Baha) has a row: OSM admin centre node 9327998071 (S-cp1-003), no settlement population (not tabulated, S-cp1-005). GASTAT's portal was unreachable again on 31 Oct 2026 (S-cp1-028).


- **Distance reference differs by region** (all straight-line, A-screen-027): station points: al_baha (A-screen-pilot-002 [al_baha]), eastern (-002 [eastern]), hail (-006 [hail]), jazan (Makkah HHR station, -006 [jazan]), madinah (four HHR stations, -004 [madinah]), makkah (located HHR stations, -002 [makkah]); nearest rail vertex: al_jouf (-001 [al_jouf]), najran (-001 [najran]), northern_borders (North line, -005 [northern_borders]), qassim (-001 [qassim]), tabuk (densified, -001 [tabuk]); place-centre proxies: riyadh (-004 [riyadh]); asir: its station set (-005 [asir]). A vertex distance understates the station distance, so the served test is generous in the five vertex regions (Al-Qurayyat is served at 6.13 km to a line vertex).
- **Jiddah is not in the served bucket**: the Makkah pilot located only the airport HHR station (12.2 km); the central Al-Sulaymaniyah station was not located (pilot decision 4, docs/status/pilot-makkah.md). With it, Jiddah (rank 6) would move to the served bucket.
- **Riyadh station proxies** put Riyadh and Al-Majma'ah at 0.0 km (place centre = station; A-screen-pilot-004 [riyadh]).
- **Terrain is assumed everywhere** (region-level descriptions; no DEM); null in al_jouf, eastern and makkah.
- **Populations**: all 150 are secondary relays (S-073 family); 35 rows have none (centre not in the ≥ 2,500 locality table, or not sourced).
- **Coordinates**: some centres are boundary-relation centroids (makkah 6, qassim 3, riyadh several; flagged in `notes`); Balqarn (Asir) is provisional; Hala Ammar (Tabuk) has no governorate.

## 9. Sources and open questions

Sources: `docs/sources/index.csv` (S-070 to S-090 and the `S-<region>-` rows cited per row), `docs/assumptions.md` (A-screen-001 to -006, -013, -014, -020 to -030 and the region-scoped pilot rows). Open questions raised by the pilot are in `docs/plan.md`, section "Open questions".
