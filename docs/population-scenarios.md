> **Document version:** docs/population-scenarios.md v0.2 | 31 Oct 2026 | Author: demand-modeler (R3) | Status: draft

# Population scenarios to 2050/2060 (W8, R3 task 2)

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Every figure below is a scenario input or a scenario result. None is a prediction. The scenarios differ in their stated assumptions only; none of them is "the" future population. Write "in the scenario, population reaches X", never "will reach".

Files: `cities/ksa/population/` (schema in its `README.md`), code `demand/population.py`, tests `tests/test_demand_population.py`. Registers: assumptions `docs/assumptions.md` (A-pop-001 to A-pop-018, A-demand-030), sources `docs/sources/r3-pop.csv` (S-r3-pop-001 to S-r3-pop-035), licences `docs/licences.csv`. Rebuild with `uv run python -m demand.population build --seed 1`. A rebuild reproduces every file byte for byte (checked 31 Oct 2026).

## 1. What is and is not published

| item | finding | ids |
|---|---|---|
| GASTAT population projections (national or regional, to 2030/2050) | **Not published / not found.** GASTAT's methodology and quality report for "population projections and estimates" describes an annual product but gives no projected figure or horizon year. The 2024 estimates release covers 2023 and 2024 only, nationally, with no projection. Searched on 31 Oct 2026: the stats.gov.sa methodology page, the statistics index (S-091, already "not found" at R0), English and Arabic web searches ("GASTAT population projections 2030 2050", "الإسقاطات السكانية") | S-r3-pop-006, S-r3-pop-007, S-091 |
| GASTAT sub-national projections | **Not published / not found** (as above). No regional estimate after the 2022 census is published either | S-r3-pop-006; data/ksa/tables/gastat/README.md |
| UN WPP latest revision | **WPP 2024** (released 11 Jul 2024; the files are dated 13 Dec 2024). An interim update in 2026 corrects Togo only; "results for all other locations are unchanged". No WPP 2026 is listed on the UN download page. A third-party site says the next revision is postponed to 11 Jul 2027 (unverified) | S-r3-pop-001, S-r3-pop-003, S-r3-pop-004 |
| UN Data Portal API | The data endpoint needs a token (HTTP 401). No token was requested (rule 7). The 17 MB CSV was used instead | S-r3-pop-005 |
| UN World Urbanization Prospects | **WUP 2025** (released 18 Nov 2025): urban share to 2050 under national definitions and the new Degree of Urbanisation. The city-level file (58.7 MB) is over the 50 MB gate and was not downloaded, so no UN city projections are used | S-r3-pop-008, S-r3-pop-010, S-r3-pop-011 |
| Official Vision 2030 population target | **No plan document found.** Only press reports of the Crown Prince's remarks exist: national 50-60 M (2022) and 50-55 M (2023) by 2030; Riyadh 15-20 M by 2030 (2021). A 2024 report of a Riyadh target cut could not be read (unverified) | S-r3-pop-012, -013, -014, -015 |
| Sub-national (governorate) projections from any source | **None found.** Downscaling is our method (section 3), registered as A-pop-005 and A-pop-006 | n/a |

## 2. National series and the census anchor

**Anchor.** The base is the GASTAT Census 2022 total, 32,175,224 (S-cp2-gastat-007; the governorate table sums to it exactly). WPP 2024 gives 32,175.352 thousand (32,175,352 persons) for 1 July 2022 (S-r3-pop-001). The gap is **+128 persons (+0.0004 %)**: WPP 2024 is effectively fitted to the census. Every WPP series is still ratio-scaled by census / WPP Medium 2022 = 0.99999602, so that 2022 equals the census exactly in every scenario (A-pop-001). The census reference date (May 2022) is treated as the same epoch as 1 July (A-pop-002). WPP projection variants start in 2024, so 2022-2023 take the Medium estimates in every variant (A-pop-004).

**The 2024 gap.** GASTAT's mid-2024 estimate is 35,300,280 (S-cp2-gastat-006). WPP 2024 Medium for 2024 is 33,962,757, so GASTAT is **3.94 % (1.34 M) higher** (S-r3-pop-001). GASTAT reports an average 4.6 % a year since the census (S-r3-pop-007). The GASTAT 2024 figure is above even the WPP upper 95 % bound for 2025 (35.24 M). WPP 2024 was finalised before GASTAT's 2023-24 estimates were published. The sensitivity scenario `un_wpp_medium_gastat2024` re-anchors the WPP Medium growth path to GASTAT 2024 and holds the ratio 1.0394 to 2060 (A-pop-003). Whether the gap persists, narrows or widens is not known. This is a CP4 decision item.

National totals in each scenario, million persons (annual values in the YAML files; derived from the cited sources and assumptions):

| scenario (kind) | 2022 | 2025 | 2030 | 2035 | 2040 | 2045 | 2050 | 2055 | 2060 | ids |
|---|---|---|---|---|---|---|---|---|---|---|
| `baseline` (baseline_census) | 32.18 | 32.18 | 32.18 | 32.18 | 32.18 | 32.18 | 32.18 | 32.18 | 32.18 | S-cp2-gastat-007; A-pop-007 |
| `un_wpp_low` (projection_un_wpp) | 32.18 | 34.48 | 36.98 | 38.96 | 40.81 | 42.60 | 44.31 | 45.89 | 47.29 | S-r3-pop-001; A-pop-001, 002, 004 |
| `un_wpp_medium` (projection_un_wpp) | 32.18 | 34.57 | 37.44 | 40.01 | 42.59 | 45.16 | 47.69 | 50.20 | 52.68 | S-r3-pop-001; A-pop-001, 002, 004 |
| `un_wpp_high` (projection_un_wpp) | 32.18 | 34.66 | 37.91 | 41.07 | 44.37 | 47.71 | 51.09 | 54.61 | 58.31 | S-r3-pop-001; A-pop-001, 002, 004 |
| `un_wpp_constant_fertility` (projection_un_wpp) | 32.18 | 34.56 | 37.49 | 40.28 | 43.22 | 46.27 | 49.39 | 52.61 | 55.96 | S-r3-pop-001; A-pop-001, 002, 004 |
| `un_wpp_zero_migration` (projection_un_wpp) | 32.18 | 34.38 | 36.61 | 38.61 | 40.42 | 42.05 | 43.44 | 44.54 | 45.25 | S-r3-pop-001; A-pop-001, 002, 004 |
| `un_wpp_medium_gastat2024` (sensitivity) | 32.18 | 35.93 | 38.92 | 41.59 | 44.27 | 46.93 | 49.57 | 52.18 | 54.75 | S-r3-pop-001, S-cp2-gastat-006; A-pop-003 |
| `vision2030_policy` (policy_vision2030) | 32.18 | 37.96 | 50.00 | 53.43 | 56.87 | 60.30 | 63.69 | 67.04 | 70.34 | S-r3-pop-012, -013, S-r3-pop-001; A-pop-009, 010 |

WPP 2024 probabilistic projection (stored in `un_wpp_medium.yaml`, census-anchored, million persons; S-r3-pop-001, A-pop-001):

| WPP 2024 probabilistic | 2025 | 2030 | 2035 | 2040 | 2045 | 2050 | 2055 | 2060 |
|---|---|---|---|---|---|---|---|---|
| lower_95 | 33.65 | 34.14 | 34.73 | 35.31 | 36.00 | 37.16 | 38.20 | 38.96 |
| lower_80 | 33.83 | 35.04 | 36.29 | 37.55 | 38.80 | 40.26 | 41.81 | 43.01 |
| median | 34.57 | 37.44 | 40.01 | 42.59 | 45.16 | 47.69 | 50.20 | 52.68 |
| upper_80 | 35.03 | 39.67 | 43.62 | 47.52 | 51.13 | 55.20 | 59.24 | 63.27 |
| upper_95 | 35.24 | 40.63 | 45.15 | 49.71 | 54.52 | 59.07 | 63.87 | 68.48 |

Reading the table: in WPP 2024 the deterministic Low/High variants are much narrower than the probabilistic 80 % interval. Migration matters more than fertility here: in the zero-migration variant the population reaches 45.25 M in 2060, against 52.68 M in the medium scenario and 55.96 M with constant fertility.

**Urbanisation** (`urbanisation_wup2025.yaml`, S-r3-pop-008, S-r3-pop-010, A-pop-008). WUP 2025 urban share under national definitions: 84.13 % (2022), 85.36 % (2030), 87.45 % (2050). Degree of Urbanisation, cities and towns: 84.05 % (2022), 87.80 % (2050). WUP ends in 2050; 2055 and 2060 are held at the 2050 value (A-pop-008). In v0.1 the series is a context input for zoning and the urban/rural split. It does not change governorate shares, because a governorate zone mixes urban and rural land and no sourced mapping from the national share to governorates exists.

## 3. Sub-national downscaling (our method, registered)

No sub-national projection is published (section 1). `project(base_by_zone, scenario, year)` returns integer zone populations whose sum equals the scenario's national total **exactly** (largest-remainder rounding, ties in zone order; tested).

- **Zones.** The 150 GASTAT governorates (Census 2022 TA1 primary export, S-cp2-gastat-007) map to the 149 OSM governorate polygons G001-G149 (`cities/ksa/zones/governorates.geojson`) through the CP2 crosswalk (`screening.gastat`). Al Amoah (10,969; no OSM polygon, C-r1a-20) is merged into G031 Tathlith, whose polygon contains its seat node (A-pop-007). Base table: `cities/ksa/population/base_2022_governorates.csv`.
- **D1, constant shares (default, A-pop-005).** The Census 2022 governorate shares are held for every year. This adds no invented differential.
- **D2, regional trend (variant, A-pop-006).** Region shares drift by exp(w · d_r · (t − 2022)), with d_r = ln(g_r / g_KSA) / 12 from the GASTAT TA9 regional series 2010 and 2022 (S-cp2-gastat-003, values in `downscaling.yaml`). Governorate shares within a region are held. The weight is w = 0.5 (range 0 to 1). Region level is used, not governorate level: 33 governorates have no 2010 row, and 2010 parents include later splits. In the medium scenario in 2060, D2 moves region totals relative to D1 by −9.4 % (Makkah) to +8.1 % (Hail); Riyadh is +4.2 % and Eastern +7.2 % (`show --downscaling regional_trend`).
- **Policy override.** In `vision2030_policy` the Riyadh target is fixed on G138 (A-pop-011, A-pop-012) and the remaining total is spread over the other zones by the downscaling shares.
- **Giga add-ons** (section 5). They are applied on top of any scenario with `--giga p10|p50|p90|announced`. They **reallocate** by default (A-pop-013): the national total is unchanged, and the add-on is taken pro rata from the non-host zones. `additive` is the upper bound.

## 4. Vision 2030 policy scenario (labelled POLICY, not a forecast)

| item | stated figure | as used | grade | ids |
|---|---|---|---|---|
| national population 2030 | 50-60 M, "with half being foreigners" (Crown Prince, Jul 2022); 50-55 M (Jun 2023) | 50.0 M in 2030 (lower bound common to both); range 50-60 M; geometric path from the census, WPP Medium growth ratio after 2030 | B (press quoting the Crown Prince; no plan document) | S-r3-pop-012, S-r3-pop-013; A-pop-009, A-pop-010 |
| Riyadh 2030 | "around 15-20 million residents in 2030" (Crown Prince, FII, Jan 2021) | 15.0 M on the Ar Riyadh governorate (7,009,120 in 2022); range 10-20 M; share of national held after 2030 | B | S-r3-pop-014, S-r3-pop-016; A-pop-011, A-pop-012 |
| Riyadh target revised (2024) | reported pull-back of the doubling target; extracts give 10 M and 15 M | sensitivity bound only (10 M) | D (unverified, HTTP 403) | S-r3-pop-015 |
| tourism visits 2030 | 150 M a year (Minister of Tourism, Oct 2023: 75 M international and 75 M domestic; Jan 2026: 70 M and 80 M) | 150 M = 70 M + 80 M for the tourism purpose, never for population | B | S-r3-pop-017, S-r3-pop-018; A-pop-018 |
| tourism visits observed | 2025: about 122 M (preliminary); 2024: 29.7 M inbound and 86.2 M domestic | observed reference for tourism generation | B | S-r3-pop-018 |

In the policy scenario, population reaches 50.0 M in 2030, 63.7 M in 2050 and 70.3 M in 2060. Riyadh governorate reaches 15.0 M in 2030 and 21.1 M in 2060. To reach the 2030 figure from the GASTAT 2024 estimate would take about 6 % a year, against the 4.6 % a year GASTAT reports since the census (S-r3-pop-007).

Grades used here and in section 5: **A** read on the publisher's own site on the access date (source status `verified`); **B** reputable press or trade press quoting a named official or the company; **C** press citing unnamed people, or trade press relaying a release we could not open; **D** search extract or a page not read (source status `unverified`; never feeds a figure).

## 5. Giga-projects: announced versus delivered (add-on only, never in the base)

`cities/ksa/population/scenarios/gigaprojects.yaml`; delivered shares are registered judgements (A-demand-030). Every `giga_project` row of `cities/ksa/zones/economic_nodes.csv` is listed. The add-on ramps linearly from 2025 to the target year (A-pop-014). Undated targets take 2045 (A-pop-015). Zones are by point-in-polygon (A-pop-017). Visitors feed tourism only (A-pop-018).

| project | zone | announced (target year) | grade | delivered / observed status | grade | delivered share P10 / P50 / P90 | ids |
|---|---|---|---|---|---|---|---|
| NEOM: THE LINE (2030) | G145 Duba | 1.5 M residents (2030), stated for "NEOM's first phase" (S-r3-pop-012); attributing it to THE LINE is this track's reading | B | NEOM: "advancing through a phased, demand-led approach", no resident figure; work halted until at least after 2030, 2030 target up to 100,000 | A (NEOM page); C (Semafor, unnamed sources) | 0 / 0.02 / 0.067 | S-r3-pop-012, -019, -020 |
| NEOM: THE LINE (2045) | G145 | 9 M residents (2045), the same first-phase statement (S-r3-pop-012) | B | as above | A; C | 0 / 0.01 / 0.05 | S-r3-pop-012, -019, -020 |
| NEOM: Trojena | G147 Tabuk | 7,000 residents, 10,000 jobs, 700,000 visitors a year (2030) | B | no new investment until after 2030; 2029 Asian Winter Games moved | C; secondary | 0 / 0.1 / 0.4 | S-r3-pop-021, -020, S-r1a-233 |
| NEOM: Oxagon | G145 (nearest; node offshore) | no resident or jobs target found; port 1.5 M TEU by 2030 | A | Oxagon Hive capacity for up to 2,400 people; port operating at 250,000 TEU; spending continues | A; C | observed 2,400 (share 1.0) | S-r3-pop-022, -020 |
| Red Sea Global: The Red Sea | G149 Umluj | 1 M tourists a year; 8,000 rooms by 2030 | B | first destination open Nov 2023; three Shura Island resorts Sep 2025 | secondary | 0.3 / 0.6 / 0.9 (visitors) | S-r3-pop-023, S-r1a-226 |
| Red Sea Global: AMAALA | G143 Al Wajh | Triple Bay above 1,600 rooms (no visitor or jobs figure read) | B | Six Senses AMAALA opened Jul 2026; six more resorts in the year | B | 0.3 / 0.6 / 0.9 (no quantity yet) | S-r3-pop-024, -025, -035 |
| Qiddiya City | G134 Duruma | 600,000 residents, 48 M visits, 325,000 jobs, no year (Dec 2023); restated 500,000 residents and 85,000 jobs by 2030 (Jan 2026) | B | Six Flags Qiddiya City opened 31 Dec 2025 | B | 0.1 / 0.3 / 0.6 | S-r3-pop-026, -027 |
| AlUla | G074 Al Ula | area population 130,000, 38,000 jobs, 2 M visitors a year (2035) | B | partly open; international flights approved Mar 2021 | secondary | 0.2 / 0.5 / 0.8 of (130,000 − 60,103) | S-r3-pop-028, S-r1a-227; A-pop-016 |
| Diriyah | G121 Ad Diriyah | 100,000 residents, 178,000 jobs, 50 M visits a year "by the end of the decade" (read as 2030); 2020 version: 100,000 residents, 25 M visitors | A | under construction; contracts still being awarded Oct 2026 | A | 0.3 / 0.6 / 0.9 | S-r3-pop-029, -030 |
| ROSHN: SEDRA | G138 Ar Riyadh | 30,000+ homes (no resident figure) | A | partly open since 2022 | secondary | no quantity (would double count Riyadh growth) | S-r3-pop-031, S-r1a-231 |
| New Murabba | G121 (flag: alternative G138) | 104,000 homes, 334,000 direct and indirect jobs (2030) | C | announced; delivery status not read | secondary | 0.05 / 0.2 / 0.5 (jobs) | S-r3-pop-032, -033, S-r1a-214 |
| King Salman Park | G138 Ar Riyadh | 12,000 units, about 400,000 visitors a day, complete by 2024 (2019 plan) | B | under construction (tunnel opened Feb 2024) | secondary | 0.2 / 0.5 / 0.8 (no resident quantity) | S-r3-pop-034, S-r1a-234 |
| Sports Boulevard | unlocated | none read | n/a | phase 1 opened Feb 2025 | secondary | no quantity | S-r1a-235 |

Add-on totals over all projects (residents, persons; `giga_increments`, ramp A-pop-014). In 2030: P10 51,890 / P50 148,074 / P90 310,659 against 2,519,348 announced. In 2050: P10 96,379 / P50 338,048 / P90 901,118 against 9,679,297 announced. Jobs in 2030: P10 82,400 / P50 209,600 / P90 397,400 against 626,000 announced. The gap between announced and delivered is dominated by THE LINE (9 M announced for 2045). With the reallocate mode the national total does not change: in the medium scenario with P50 add-ons in 2050, the five host zones gain 338,048 people taken pro rata from the other 144.

Conflicts recorded here (not resolved silently): Qiddiya residents (600,000 in Dec 2023 against 500,000 in Jan 2026; the later figure is used); the Vision 2030 tourism split (75/75 against 70/80; the later one is used, A-pop-018); Diriyah visitors (25 M in 2020 against 50 M in 2024; the later one is used); Riyadh target (15-20 M in 2021 against an unread 2024 revision).

## 6. Matched baseline, seeds and run metadata

Every population scenario shares the zones (`base_2022_governorates.csv`) and the 2022 census base with `baseline` (rule 6). Downscaling and add-ons are deterministic, so `--seed` is recorded in `meta.json` but not used. `build` writes `runs/population/build/meta.json` (seed, config hash, manifest hash, code version, assumption ids, validation result). `show --out` writes `zones.parquet` and `meta.json`.

## 7. Open items for CP4

1. Which national anchor to use: the census-anchored WPP (default) or the GASTAT 2024 re-anchored sensitivity (A-pop-003). GASTAT 2024 lies above the WPP 95 % band.
2. Whether the Vision 2030 policy scenario (50 M in 2030; press-reported statements, no plan document) is run as a scenario at all, and with which Riyadh value.
3. Giga add-on treatment: the delivered shares (A-demand-030), reallocate against additive (A-pop-013), and the New Murabba zone (G121 or G138).
4. Primary sources to replace secondary ones: PIF/NEOM releases (THE LINE, Trojena, New Murabba), Red Sea Global and Qiddiya pages (HTTP 403 here), the RCU masterplan, an RCRC statement on the Riyadh target.
