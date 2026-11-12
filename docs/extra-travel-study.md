> **Document version:** docs/extra-travel-study.md v1.1 | 7 Nov 2026 | Author: STUDY_EXTRA_TRAVEL (main track builder; v1.1 table captions carry the exact label) | Status: draft

# Extra travel and land entry: a research sensitivity (STUDY_EXTRA_TRAVEL)

**Labels:** synthetic demand, uncalibrated: scenario comparison, not a forecast. Not the official ranking.

**Alignment limitation:** alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty. The S1 Landbridge used here is the committed line as sketched in the model (`cities/ksa/lines/landbridge.yaml`), not a published alignment.

**What this is.** Tariq asked (7 Nov 2026; `prompts/STUDY_EXTRA_TRAVEL.md`) whether a railway would do more than move people from air: whether it would create extra domestic trips and extra visitor travel, including Umrah and other visitors entering by land from the north (Jordan) and from the Gulf. This note is a tightly scoped sensitivity that sits beside the main programme, as the Riyadh–Jeddah study did (`docs/rj-routes-study.md`).

**What this is not.**
- It is not a new ranking. The official CBA ranking rule is unchanged: it excludes wider economic impacts and foreign-visitor benefits (A-cba-310).
- It is not a GDP or jobs study. No GDP percentage, jobs figure or quality-of-life index is derived here.
- It is not part of the R8 report, the summaries, the policy brief, the figure index or the dashboard.

**Frozen values not touched.** Published S1, L1–L6 and R8 figures are unchanged. So are the frozen central values of A-demand-012…015 (trip rates), A-demand-016/019 (pilgrimage totals), A-intl-001 (entry-port shares) and A-intl-003 (rail share 0.0286). Every variant lives in `cities/ksa/assumptions/extra_travel_study.yaml`, `docs/study-extra-travel/assumptions.md` (A-xt-001…011) and `docs/sources/study-extra-travel.csv` (S-xt-…). Like the RJ study registers, these stay beside the study.

**Engine.** The judge copy `judge/v1-r5` (tag r5) is the code behind the published S1-vs-S0 CBA (`runs/cba/CBA-S1-committed-programme`). It was run read-only through the study entry `study/extra_travel_judge.py`, and its fingerprint was checked before and after every call. The zero-elasticity case reproduces the published CBA inputs and results exactly: maximum relative difference 0 (`runs/study/extra-travel/induced/reproduction_check.json`). Outputs are in `runs/study/extra-travel/`, and every `meta.json` carries seed 1, config hash, data hash, `git describe`, the judge hash and `official_ranking: false`.

## 1. Air-market evidence (OAG, Busiest Routes 2025)

Source: OAG, "Busiest Routes 2025", https://www.oag.com/busiest-routes-world-2025, accessed 7 Nov 2026, 13:24 AST (fetched directly; not an AI overview or a fare blog). Rows S-xt-001…007.

| fact on the page (2025, scheduled seats, both directions) | value | row |
|---|---|---|
| Jeddah–Riyadh: place in OAG's top ten busiest routes | fifth | S-xt-001 |
| Jeddah–Riyadh: growth | fastest-growing route in that top ten; +13 % vs 2024; +22 % vs 2019 | S-xt-001, S-xt-002 |
| Jeddah–Riyadh: seats | 9.8 million (regional table: 9,819,558) | S-xt-002 |
| Jeddah–Riyadh: region | the only top-ten route outside Asia Pacific; the busiest domestic route in the Middle East (regional table) | S-xt-001, S-xt-002 |
| Jeddah–Riyadh: fare | average economy fare USD 95 one way, +27 % vs 2024 (annual average of the lowest available one-way fare, sampled in the first week of December); three airlines; 460 miles | S-xt-003 |
| Cairo–Jeddah | second busiest cross-border route; 5.8 million seats; +5 % vs 2024; +71 % vs 2019 | S-xt-005 |
| Dubai–Riyadh | seventh busiest cross-border route; 4.5 million seats; +4 % vs 2024; +42 % vs 2019 | S-xt-006 |
| Japan caution | Sapporo–Tokyo Haneda (12.1 million) and Fukuoka–Tokyo Haneda (11.5 million) are second and third, and OAG says Japan keeps this position "despite an extensive high speed rail network covering the country" | S-xt-007 |

**Checked against the coordinator's recollection.** Every figure in the prompt matches the live page. Two wording points:
- The page says "fifth placed" in its top ten busiest routes and lists cross-border routes separately. It does not use the phrase "fifth busiest domestic route".
- "Busiest domestic route in the Middle East" comes from the page's regional table.

This annual report is preferred over any blog quoting "8 million seats / +22 % year-on-year". The IATA airport-pair item (S-r1a-530) stays as recorded.

**What seats are.** Seats are scheduled capacity in both directions. They are not passengers flown, and no open load factor or GACA city-pair passenger table was found (`docs/data-sources.md`). The figures above describe the air market; they are not inputs to the model.

## 2. The frozen model on Riyadh–Jeddah (published S1)

**Pair definition (A-xt-001).** Every zone of the Riyadh metro (G138-H001…H040) × every zone of the Jeddah metro (G089-H001…H039), both directions, all five purposes, 2050, UN WPP medium, from the published S1 and S0 runs (judge v1-r5). Source: `runs/study/extra-travel/baseline/rj_baseline.json`.

*Table 2a. One-way trips and passenger-km per year on the pair, 2050 medium. Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. Not the official ranking.*

| run | rail trips | air trips | car trips | bus trips | all modes | rail pkm (M) | air pkm (M) | car pkm (M) | bus pkm (M) |
|---|---|---|---|---|---|---|---|---|---|
| S0 (no Landbridge) | 0 | 3,777,702 | 799,494 | 26,567 | 4,603,763 | 0 | 3,219.1 | 765.1 | 25.3 |
| S1 (published) | 424,947 | 3,474,082 | 734,110 | 24,344 | 4,657,483 | 382.3 | 2,960.4 | 702.6 | 23.2 |

- In the model, S1 moves about 0.30 M air trips and 0.07 M car trips on the pair to rail.
- The pair's total rises by 0.05 M. That rise is destinations redistributing toward the pair, not new national travel: the national total is 384,578,627 trips in both S0 and S1.
- The Riyadh–Jeddah study packages (`runs/study/rj/score/score.csv`, judge v3, increments versus S1\*, read only) carry 3.48 M (RJ-LB) to 7.28 M (RJ-C1) sketch passengers in 2050 medium (`docs/rj-routes-study.md` §8a). Those are line loads of every pair using the sketch, not this pair.

**Against the OAG seats.**
- The model's 2050 air trips on this metro pair are 0.38 (S0) and 0.35 (S1) times OAG's 2025 seat count.
- These are not the same quantity, so nothing is subtracted and the model is not declared wrong:
  - seats are capacity, not passengers;
  - the airport pair carries connecting passengers, foreign visitors and residents from outside the two metro zone sets (Makkah, Taif and others use JED);
  - the model's air demand is not calibrated to air traffic: block times, fares and headways are assumptions (A-mode-029…031).

**What the frozen model holds fixed.**
- Domestic trips per resident are fixed rates: tourism 2.403, leisure/VFR 2.564, business 0.977, commute 0.5 (A-demand-012…015). Gravity distributes them, so a cheaper or faster railway changes mode and destination, not how many trips exist.
- Internal pilgrimage totals are fixed by origin (A-demand-016, A-demand-019; A-demand-031).
- Foreign visitors carry no user benefits or fares in the official CBA (A-cba-310).
- In the scored Riyadh–Jeddah sketches, air stays ahead door-to-door in every rail case modelled (`docs/rj-routes-study.md` §5).

**Fare versus speed, indicative only (not a scored table).**

| item | value | source |
|---|---|---|
| model rail fare on the pair (S1, trip-weighted) | 269.9 SAR (0.30 SAR/km × 899.7 rail-km) | A-mode-037; rj_baseline.json |
| model air fare on the pair (trip-weighted) | 277.8 SAR | A-mode-030 (150 SAR + 0.15 SAR/km) |
| OAG average economy fare, 2025 | USD 95 ≈ 356 SAR at the 3.75 peg | S-xt-003; S-lb-020; A-xt-009 |
| model in-vehicle time, rail / air | 323 min / 101 min | rj_baseline.json (A-mode-029) |
| model headway, rail / air | 120 min / 30 min | A-demand-049; A-mode-031 |

The OAG fare is an average of the lowest available fares at one sampling point, so the comparison is indicative. In the model, rail's ticket is already slightly below air's, yet air keeps most of the pair because of rail's in-vehicle time and headway. A cheaper ticket is a separate lever from speed; it is not tested as a scored scenario here.

## 3. Induced-demand sensitivity (study path only)

**Method (A-xt-002, A-xt-003).**
- For tourism, leisure/VFR and business, the scenario's trips on each pair are scaled by (C1/C0)^e. C is the frozen model's composite generalised cost on that pair (the logsum, in car in-vehicle minutes): C0 from S0 and C1 from S1.
- By default each pair's mode shares are kept (proportional allocation).
- Commute is unchanged: TAG says a frequency response is not normally needed for doubly-constrained commuting (S-xt-010). Pilgrimage is unchanged: internal Hajj and Umrah totals stay fixed.
- The modified OD tables then go through the frozen benefit extraction and the frozen Monte Carlo CBA: 10,000 draws, seed 1, the same draws as the published run, so per-draw differences are valid.
- Generated trips get user benefits by the frozen rule of a half (`economics.benefits.rule_of_half`; the CBA case's `rule_of_half: true`).

**No Saudi-calibrated elasticity exists.** TAG M2.1 publishes no trip-frequency value. It says the effect "is likely to be small" and has "little evidence" behind it (§4.6.3; S-xt-010). The bracket below is therefore uncalibrated:

| case | e | basis |
|---|---|---|
| low | −0.15 | lower end of TAG's fuel-cost realism range (S-xt-011) |
| central | −0.25 | the TAG meta-model mean (S-xt-011) |
| high | −0.40 | TAG's "long-distance discretionary" level (S-xt-012) |
| stress | −0.70 | outside every sourced figure |

Those TAG figures are modal elasticities that include mode switching, so they over-state a pure frequency response.

Two rail-only cases form a rail-favourable bound (A-xt-011): on pairs that rail already serves, every generated trip is a rail trip. No extra train-km or capacity cost is added, so the bound is optimistic for rail.

*Table 3a. S1 versus S0 with induced domestic trips; 2050 medium for annual quantities; NPV and BCR in SAR million, 2025 prices, PV 2026, 60 years, Green Book 2026 rate (A-cba-001); UN WPP medium. Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. Not the official ranking.*

| case | e | allocation | extra trips (all modes) | of which rail / air / car | extra pkm (M) all / rail | extra fare 2050 (SAR m) | NPV P10 / P50 / P90 | BCR P10 / P50 / P90 | extra NPV P10 / P50 / P90 (per draw) | extra PV user time P10 / P50 / P90 | extra PV fare (P50 − P50) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zero (= published) | 0.00 | — | 0 | 0 / 0 / 0 | 0.0 / 0.0 | 0.0 | −337,555 / −60,103 / 11,607 | 0.068 / 0.306 / 1.256 | 0 / 0 / 0 | 0 / 0 / 0 | 0 |
| low | −0.15 | proportional | 230,329 | 34,462 / 19,080 / 175,461 | 57.4 / 10.6 | 3.2 | −337,924 / −60,425 / 11,040 | 0.067 / 0.303 / 1.245 | −756 / −293 / −95 | 12 / 39 / 104 | 48 |
| central | −0.25 | proportional | 386,524 | 57,888 / 31,864 / 294,554 | 96.1 / 17.8 | 5.4 | −338,365 / −60,591 / 10,659 | 0.067 / 0.301 / 1.238 | −1,264 / −490 / −158 | 21 / 66 / 175 | 80 |
| high | −0.40 | proportional | 624,918 | 93,724 / 51,138 / 476,487 | 154.7 / 28.7 | 8.7 | −338,890 / −60,998 / 9,855 | 0.066 / 0.297 / 1.225 | −2,034 / −788 / −254 | 34 / 106 / 283 | 129 |
| stress | −0.70 | proportional | 1,117,199 | 168,011 / 90,043 / 852,827 | 274.3 / 51.2 | 15.4 | −339,187 / −61,564 / 8,678 | 0.065 / 0.291 / 1.196 | −3,602 / −1,394 / −449 | 61 / 191 / 508 | 230 |
| central_rail_only | −0.25 | rail_only | 386,524 | 386,795 / 0 / −261 | 98.1 / 98.1 | 29.6 | −337,361 / −59,668 / 12,372 | 0.068 / 0.308 / 1.277 | 186 / 516 / 1,038 | 21 / 66 / 175 | 440 |
| stress_rail_only | −0.70 | rail_only | 1,117,199 | 1,117,949 / 0 / −725 | 279.6 / 279.7 | 84.3 | −335,760 / −58,826 / 13,935 | 0.069 / 0.312 / 1.319 | 531 / 1,476 / 2,969 | 61 / 191 / 508 | 1,255 |

Sources: `runs/study/extra-travel/induced_summary.csv`, built from `runs/study/extra-travel/induced/<case>/{cba/results.json, cba/draws.parquet, inputs/, induced_diag.json}`.
- Small negative car entries in the rail-only rows are pairs where S1 raised the composite cost, which are handled proportionally.
- "Extra PV fare" is a difference of medians. The per-draw columns are differences on the same draw.
- Extra user benefit in 2050 is 0.03–0.15 M hours a year across the bracket.

**What the sensitivity shows, in the model.**
- **Proportional allocation.** Generated travel is 0.23–1.12 M one-way trips a year in 2050, against 384.6 M national trips (0.06–0.29 %). About three quarters of it is by car, because the trips are generated on pairs whose composite cost fell and they follow those pairs' existing mode shares. S1's NPV falls by 293–1,394 SAR m at P50.
  - At central e, the P50 components (difference of medians) are: carbon −388; non-fuel vehicle operating cost −110; safety −65; interurban decongestion −13; user time +66; fare +80.
  - The extra car and air trips add emissions and crashes, and the user benefit of a generated trip is small (rule of a half).
- **Rail-only bound.** NPV rises by 516 (central) to 1,476 (stress) SAR m at P50, mostly through fares.
- **Neither direction changes the overall result.** S1 versus S0 stays at NPV P50 between −61,564 and −58,826 SAR m and BCR P50 between 0.29 and 0.31 in every case.
- **Generated share of rail trips.** Generated rail trips are 0.8–3.8 % of S1's added rail trips under proportional allocation and 8.4–20.9 % under the rail-only bound.
  - For context only (different country, definition and network): the World Bank's estimate for Chinese high-speed rail is that 18 % of passengers would not have travelled without it (S-bench-cn-035).
- **On Riyadh–Jeddah itself** (rj_baseline.json, `induced_on_pair`), the bracket adds 13,400–63,100 one-way trips a year (2050 medium), against 4.66 M on the pair in S1. Under proportional allocation most of these are air trips; under the rail-only bound all are rail.

**Not done (cost guard).** No thicker published layout (L1) and no RJ-LB-versus-S1\* run were added. Both need the v3 phased layout adapter (`optimise/layout.py` tranche logic) under a new study wrapper. The S1-versus-S0 bracket already shows the sign and scale of the effect. Recorded in `docs/status/main.md`.

## 4. Visitor and land-entry scenarios (study path only)

**Hajj is held fixed in every scenario.** Hajj is permit-constrained: a railway may change how pilgrims arrive and move, not how many permits are issued. Foreign Hajj arrivals stay at 1,506,576, of which 66,465 come by land (2025, GASTAT, frozen `demand.intl`), and they are not an input to any row below. Internal Hajj (166,654; A-social-007) and internal Umrah totals are also unchanged.

**What the frozen model does.**
- Foreign Umrah entrants are split by entry port (A-intl-001).
- Land entrants have no entry leg; only their Makkah↔Madinah legs are modelled.
- Rail carries 0.0286 of a leg wherever the rail graph has a path (A-intl-003).
- No behavioural rule lets easier land access bring more visitors.

**Land ports (S-xt-020).** In the GASTAT Umrah bulletins for 1440 and 1441 AH (Table 3; 1441 covers Muharram–Rajab only, and 1442 has no land entries), 954,082 foreign performers entered by land:

| border | ports and model zones | share of land entrants | rail path to the Makkah zone in S0 / S1 |
|---|---|---|---|
| Jordan | Halat Ammar → Tabuk G147-H010 (26.3 %); Al-Haditha → Al Qurayyat G011 (10.5 %) | 36.8 % | Halat Ammar: none / none. Al-Haditha: none / yes, 2,109 rail-km via Riyadh (SAR North + Riyadh Rail Link + Landbridge) against 1,514 road-km |
| Gulf | Al-Batha → Al Udayd G037 (13.2 %); Al-Raqi → Hafar Al Batin G039 (9.4 %); King Fahd Causeway → Khobar G040-H003 (1.5 %) | 24.1 % | Al-Batha: none / yes, 1,588 rail-km (Saudi GCC section + SAR East + Landbridge) against 1,337 road-km. Causeway: none / yes, 1,292 rail-km against 1,289 road-km. Al-Raqi: none / none |
| Yemen | Al-Wadiah → Sharurah G100 (A-xt-005) | 39.1 % | none / none |

Port-to-zone assignments are A-xt-004 and A-xt-005; two identifications still need verifying. The bulletins have no Salwa (Qatar) row for these years. The model's rail stops at the Saudi side: the GCC railway beyond the border is not modelled.

**Scenario rules.**
- Each land entrant gets one entry and one exit leg between the border zone and the Makkah zone (A-xt-008).
- 2025 arrivals are applied to each network, with no growth.
- The rail share given a path is the frozen 0.0286 or one of two labelled study variants (A-xt-006).
- The land share is the frozen 0.0843 or the observed 1440–1442 maximum 0.0954.
- Extra land-entry volume is 0, +10 % or +25 %: a what-if with no source (A-xt-007).
- The frozen rule applies a flat share to any path, including a 2,109 rail-km route where the road is 1,514 km, so the higher rail-share variants are generous.

*Table 4a. Foreign Umrah land entrants and their onward rail entry and exit trips per year, S1 network, 2025 arrivals; S0 gives 0 rail trips in every row (no path). Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. Not the official ranking.*

| land share | rail share given a path | extra land volume | land entrants | of which extra (what-if) | rail entry + exit trips | Jordan border / Gulf border | fare if counted, SAR m (0.20 / 0.30 / 0.405 per km) |
|---|---|---|---|---|---|---|---|
| frozen 0.0843 | frozen 0.0286 | +0 % | 1,520,185 | 0 | 21,911 | 9,133 / 12,778 | 7.8 / 11.7 / 15.9 |
| frozen 0.0843 | frozen 0.0286 | +25 % | 1,900,231 | 380,046 | 27,388 | 11,416 / 15,973 | 9.8 / 14.7 / 19.8 |
| frozen 0.0843 | pre-R5 0.176 | +0 % | 1,520,185 | 0 | 134,835 | 56,201 / 78,634 | 48.2 / 72.3 / 97.6 |
| frozen 0.0843 | prior high 0.47 | +0 % | 1,520,185 | 0 | 360,070 | 150,082 / 209,989 | 128.7 / 193.0 / 260.6 |
| observed max 0.0954 | frozen 0.0286 | +0 % | 1,719,991 | 0 | 24,791 | 10,333 / 14,458 | 8.9 / 13.3 / 17.9 |
| observed max 0.0954 | prior high 0.47 | +25 % | 2,149,989 | 429,998 | 509,246 | 212,260 / 296,986 | 182.0 / 273.0 / 368.6 |

The full 18-row grid (every land share × rail share × extra volume) is in `runs/study/extra-travel/land/land_scenarios.csv`. The range is 21,911–509,246 rail trips a year.

**Reading it.**
- On the frozen central values, S1 gives land entrants about 22,000 rail entry and exit trips a year. S0 gives none, because no rail path links any land border to Makkah.
- Even the most generous combination (509,246) is small next to the 1.54 M foreign-visitor trips the frozen S1 already puts on HHR (`runs/r5/intl/S1-s1/totals.json`).
- **The largest Jordan-border flow, Halat Ammar, has no rail path in S1.** The Jordan-border rail trips come from Al-Haditha only, by way of Riyadh.
- **Gulf trips come from Al-Batha and the Causeway**, along the Saudi GCC section and SAR East.
- **Extra visitors (what-if only).** 152,019–429,998 extra land entrants a year under the +10 % / +25 % bracket. This has no source and is not a forecast.
- **Visitor-days are not computed.** No representative stay-length figure for foreign Umrah performers was found. The only local table (1442 AH) is a COVID year with 12,653 performers, and the Hajj stay figures do not apply to Umrah. So: unknown.
- The fare column is an "if counted" illustration (A-xt-010). No visitor user benefit is computed, because the frozen model has no generalised cost for visitors. Neither enters the official CBA (A-cba-310).

## 5. Quotable summary for the documentary

Each line below holds only with its labels: **synthetic demand, uncalibrated: scenario comparison, not a forecast; not the official ranking.**

| point | honest wording | source |
|---|---|---|
| Air market | "In 2025 Jeddah–Riyadh was fifth in OAG's top ten busiest air routes by scheduled seats, about 9.8 million seats in both directions, and the fastest-growing route in that top ten (+13 % on 2024, +22 % on 2019)." Accessed 7 Nov 2026. Seats are capacity, not passengers. | S-xt-001, S-xt-002 |
| The model's pair | "In the model, in 2050, rail takes about 0.42 million of 4.66 million one-way trips a year between the Riyadh and Jeddah metro areas; air keeps about 3.47 million." | Table 2a |
| Mode shift versus new travel | "In the model, the committed lines move trips between modes and destinations; the national number of trips is the same with and without them." | §2 |
| Extra travel | "If cheaper or faster travel also creates trips (an uncalibrated sensitivity, elasticity −0.15 to −0.70), the model adds about 0.2–1.1 million trips a year nationally in 2050, 0.06–0.29 % of all trips. If they follow today's mode shares, most go by car and the appraisal gets slightly worse; if all go by rail, it gets slightly better. Either way, the committed programme's NPV changes by at most about 2.5 % at P50." | Table 3a |
| Land entry | "In the model, Umrah visitors entering by land gain a rail path to Makkah from two Gulf crossings and one Jordan crossing; on the frozen rail share that is about 22,000 rail trips a year, and up to about 0.5 million under generous, labelled what-ifs. The busiest Jordan crossing in the data, Halat Ammar, has no rail path." | Table 4a |
| Hajj | "Hajj numbers are set by permits: a railway can change how pilgrims travel, not how many come. Every scenario holds Hajj fixed." | §4 |
| Japan caution | "Japan has an extensive high-speed rail network covering the country, yet the world's second and third busiest air routes in 2025 were Japanese domestic routes (OAG)." | S-xt-007 |

Alignment limitation: see the head of this note. No figure here is a GDP, jobs or visitor-spending estimate. The Transit Costs Project was not used (hard stop; no figures from it).

## 6. Reproduce

```
uv run python -m study.extra_travel baseline --seed 1
uv run python -m study.extra_travel land --seed 1
uv run python -m study.extra_travel induced --seed 1    # about 3.5 min on the M3 Pro
uv run python -m study.extra_travel summary
```

Files:
- code: `study/extra_travel.py`, `study/extra_travel_core.py`, `study/extra_travel_judge.py`;
- configuration: `cities/ksa/assumptions/extra_travel_study.yaml`;
- runs: `runs/study/extra-travel/` (gitignored);
- registers: `docs/study-extra-travel/assumptions.md`, `docs/sources/study-extra-travel.csv`;
- tests: `tests/test_study_extra_travel.py`.
