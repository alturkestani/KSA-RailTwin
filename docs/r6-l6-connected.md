> **Document version:** docs/r6-l6-connected.md v1.3 | 6 Nov 2026 | Author: S6_L6_CONNECTED (main track builder); v1.1 S6_L6_SCORE (§7 full-judge score, §8 future rounds, Tariq's decisions under §6); v1.2 BCR rounding and two §7b statements corrected after VERIFY_S6_L6_SCORE pass 1; R8_L6_PANEL (v1.3: §5 published full-judge cell) | Status: draft

# S6-L6: one connected rail system (comparison layout, not the recommended programme)

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Write "in the model, X changes by", never "will". Money is SAR million, 2025 prices; capex is P50 uplifted and undiscounted; NPVs are present values at 2026 (A-cba-301).

**Alignment limitation:** alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty (`docs/alignments.md` §0, §4).

**Fast mode, not a full-judge score.** Every NPV for S6-L6 below is the sum of single-corridor library scores (A-r6-006): **fast mode, not a full-judge score; corridor interaction not included; the full judge overstated/understated fast mode by 1–17 % of capex in R6.** Sections 2–5 are fast mode. **The full-judge v3 score of S6-L6 is in §7** (S6_L6_SCORE, 6 Nov 2026). No R6–R8 figure, document or figure index changes.

**Header note (item 7):** `network.align compare` now uses every part of a MultiLineString; a future `validate` prints the main + branch HHR figures (mean 3.399 km, P90 7.757, objective about 7.473), not the main-only ones (`docs/alignments.md` §4d).

Inputs: `scenarios/S1.yaml`, `scenarios/S6-L1..L5.yaml`, the R6_V3 library `runs/r6/v3/library/` (73 base corridors identical to `runs/r6/library/`, 143 costed variants). Code: `optimise/connect.py`; parameters `cities/ksa/assumptions/r6_l6.yaml`; assumptions A-r6-130…134. Run outputs (seed 1): `runs/r6/l6/components.json`, `search.json`, `attachments.json`, `compare.json`, `national_reach.json`. Reproduce: `uv run python -m optimise.connect components | search | scenario | compare | map`.

## 1. Why S1 is three components

The rail graph is `network.graph.build_graph` with the current interchange rules, unchanged: stations of different lines are linked if they are within **0.4 km** (A-r1a-030) or carry the same normalised name within **3.0 km** (A-r1a-032) (`network/graph_params.yaml`). A layout's corridors are added the way the judge adds them: line corridors are appended, station additions are inserted into their host line (`access.railgraph.insert_station`). Nothing was widened, and no station moved: the Landbridge Jeddah terminal stays the unpublished town-centroid placeholder (A-station-001, P1).

Tariq's diagnosis holds, with the measured distances (`runs/r6/l6/components.json`):

| S1 component | lines | stations |
|---|---|---|
| c0 (main) | SAR North passenger, SAR East passenger, Landbridge, Riyadh Rail Link, Riyadh Metro L1–L6 | 110 |
| c1 (Haramain island) | HHR | 5: Makkah, Jeddah (Al-Sulaimaniyah), KAIA, KAEC, Madinah |
| c2 (GCC island) | GCC railway (Saudi section) | 3: Dammam (not confirmed), Kuwait border proxy, UAE border proxy |

| gap | nearest stations | km | why no link |
|---|---|---|---|
| c0–c1 | `landbridge:jeddah` (Jeddah, terminal site not published) ↔ `hhr:jeddah` (Al-Sulaimaniyah) | **8.21** | above 0.4 km, and the names differ |
| c0–c2 | `sar-east-passenger:dammam` (Dammam) ↔ `gcc-railway-ksa:dammam` (Dammam, not confirmed) | **3.74** | above 0.4 km; the names differ after normalisation, and 3.74 km is above 3.0 km anyway |

The rest of the R4 rail model joins these sites differently: the access model (`access_network.yaml` station_sites, A-r4-acc-004) co-locates the Landbridge Jeddah terminal with HHR Al-Sulaimaniyah and the GCC Dammam station with SAR Dammam, for door-to-door times. That is a site override for the demand model, not an interchange rule of the rail graph, and it is not used here.

**S6-L1 to L5 under the same rules** (each corridor added at its layout phase; the count is for the full layout):

| layout | components | islands and fragments (nearest gap, km) |
|---|---|---|
| S1 | 3 | HHR (8.21); GCC (3.74) |
| S6-L1 | 3 | HHR (8.21); GCC + the Al Jubayl station, which sits on the GCC line (3.74) |
| S6-L2 | 3 | as L1 |
| S6-L3 | 3 | as L1 |
| S6-L4 | 4 | as L1 + Makkah belt 045 (`S4-commuter_belt-makkah-045`; its Makkah station is **3.98** km from HHR Makkah; same name, but above 3.0 km) |
| S6-L5 | 4 | HHR (Makkah belt 045's Makkah station 3.98 km from HHR Makkah; the belt itself now reaches c0 through the other Makkah and Jeddah belts); GCC (3.74); Madinah belt 045 (`S4-commuter_belt-madinah-045`; **8.96** km from HHR Madinah) |

The R6 search optimised robust NPV (A-r6-001) and treated an island as allowed and flagged (A-r6-005), not as a constraint; none of L1–L5 joins any island.

## 2. The smallest connecting set

**Requirements** (A-r6-130…132):
- (a) one component under the current rules;
- (b) every required city on the graph: the five metros, Taif, Buraidah (Qassim), Tabuk, Abha–Khamis Mushait, Jazan, Najran, and the S2-family cities named in the brief: Yanbu, Bisha, Arar, Hafar Al-Batin, Sakaka, Al-Kharj, Al Jubayl (18). Ha'il and Ar Rass (S2 end points not named in the list) are reported, and a sensitivity requires them.

**"On the graph" test** (A-r6-131). Each city's reference point is the point the S2–S4 corridor YAMLs use for it (A-screen-013 metro anchor or register point):
- T1: a station of the one component meets the interchange rules with that point;
- T2 (otherwise): a station lies within the served distance, which is 10 km for towns (A-screen-004) and 25 km for metro anchors (A-corr-015).

The A-r6-007 reach fallback was not needed.

**Pool:** the 71 searchable corridors (A-r6-008) and their 143 costed R6_V3 variants (line type, non-electrified, dropped station), at most one option per corridor. The four FIX_HHR chord-band corridors are excluded from L6 (item 4). `S4-commuter_belt-jeddah-045` left the corridor set at R5 H4a and is not in the library.

**Method** (A-r6-133):
- An exact MILP (scipy/HiGHS) on an "item graph": the S1 components and the library options are the nodes, with an arc wherever two items have stations that meet the interchange rules.
- Connectivity is enforced by lazy node-separator cuts.
- The objective is capex P50 first, then the number of corridors.
- Every set found is re-checked on the real `network.graph`.
- Ties are equal-capex swaps that stay feasible.
- Each next set must drop at least one line corridor of every earlier set.
- Run time is 5 min on the Mac. No judge run.

**Result: S6-L6 = 16 library options, capex P50 227,213, one component, all 18 required cities on the graph** (`scenarios/S6-L6.yaml`).
- Every line corridor is the costed **non-electrified** variant (`electrified: false`, A-r6-101 (b)). It is the cheapest costed option of each corridor, so the capex-first rule picks it. R6_V3 found that no non-electrified variant improves any corridor's robust NPV.
- The all-base (electrified) version of the same 16 corridors is shown in §4.
- Phases are each option's best single-corridor library phase (A-r6-134). That is 2050 for every loss-making corridor; the Al Jubayl station is at 2030.

Building blocks from the library (`runs/r6/v3/library/<option>/score.json`; robust NPV = the minimum over the three population cases; reach gain = 2025 population newly within 120 door-to-door minutes of the five metros, that corridor alone, A-r6-007):

| corridor (option) | family | phase | robust NPV at best phase | robust NPV at 2030 | capex P10 / P50 / P90 | 120-min reach gain alone | route-km |
|---|---|---|---|---|---|---|---|
| `S2-trunk_gap-abha-khamis-mushait-bisha` (non-electrified) | trunk_gap | 2050 | -14,325 | -24,922 | 8,484 / 15,627 / 58,847 | 0 | 228.4 |
| `S2-trunk_gap-abha-khamis-mushait-najran` (non-electrified) | trunk_gap | 2050 | -22,696 | -39,896 | 15,329 / 30,390 / 121,022 | 0 | 297.4 |
| `S2-trunk_gap-al-jubayl-hafar-al-batin` (non-electrified) | trunk_gap | 2050 | -20,754 | -36,040 | 11,034 / 19,150 / 68,542 | 0 | 402.7 |
| `S2-trunk_gap-jeddah-yanbu` (non-electrified) | trunk_gap | 2050 | -16,599 | -29,008 | 9,200 / 15,985 / 57,257 | 0 | 325.0 |
| `S2-trunk_gap-tabuk-sakaka` (non-electrified) | trunk_gap | 2050 | -24,819 | -42,734 | 12,656 / 22,037 / 79,140 | 0 | 458.9 |
| `S2-trunk_gap-taif-bisha` (non-electrified) | trunk_gap | 2050 | -16,488 | -28,708 | 9,399 / 16,854 / 62,076 | 0 | 293.3 |
| `S3-branch_spur-al-kharj` (non-electrified) | branch_spur | 2050 | 3,916 | 1,942 | 4,918 / 8,732 / 31,886 | 0 | 139.2 |
| `S3-branch_spur-arar` (non-electrified) | branch_spur | 2050 | -10,911 | -18,917 | 6,106 / 10,672 / 38,522 | 0 | 194.9 |
| `S3-branch_spur-bisha` (non-electrified) | branch_spur | 2050 | -15,797 | -27,358 | 8,564 / 14,824 / 52,927 | 0 | 302.3 |
| `S3-branch_spur-sakaka` (non-electrified) | branch_spur | 2050 | -3,693 | -6,666 | 2,738 / 4,882 / 17,986 | 0 | 57.1 |
| `S3-branch_spur-yanbu-al-sina-iyah-yanbu-ind` (non-electrified) | branch_spur | 2050 | -14,713 | -26,418 | 10,810 / 20,839 / 81,313 | 0 | 226.8 |
| `S4-commuter_belt-abha-khamis-mushait-135` (non-electrified) | commuter_belt | 2050 | -23,182 | -41,206 | 14,647 / 32,196 / 136,422 | 0 | 103.9 |
| `S4-commuter_belt-dammam-khobar-dhahran-180` (non-electrified) | commuter_belt | 2050 | -18,163 | -31,393 | 5,494 / 9,519 / 34,159 | 7,659 | 151.6 |
| `S4-commuter_belt-jazan-315` (non-electrified) | commuter_belt | 2050 | -6,902 | -12,330 | 2,619 / 4,557 / 16,412 | 0 | 60.4 |
| `S5-station_addition-al-jarn` | station_addition | 2050 | -686 | -1,050 | 267 / 474 / 1,762 | 0 | 0.0 |
| `S5-station_addition-al-jubayl` | station_addition | 2030 | 4,982 | 4,982 | 267 / 474 / 1,762 | 422,823 | 0.0 |
| **S6-L6, fast-mode additive estimate (A-r6-006)** | | | **−200,761** | | **122,532 / 227,213 / 860,035** | **430,482** (union) | **3,241.9** |

Fast-mode notes:
- The robust NPV total is the A-r6-006 definition: the minimum over the population cases of the summed NPVs. The sum of the per-row minima is −200,829.
- The capex P10 and P90 totals are sums of corridor P10s and P90s, i.e. perfect correlation. They are not a P10/P90 of the programme.
- Every figure in this table is **fast mode, not a full-judge score; corridor interaction not included; the full judge overstated/understated fast mode by 1–17 % of capex in R6.**

**Ties** (equal capex, feasible on the graph): the Al-Jarn station addition (474.4) can be swapped for the Al-Oyun, Al-Qarah or Al-Umran station additions. Dammam belt 180 runs through those towns, so any one of the four joins it to SAR East.

**Next two sets** (no chord band; each drops a line corridor of every earlier set):

| set | capex P50 | Δ vs L6 | fast robust NPV | corridors | change |
|---|---|---|---|---|---|
| S6-L6 | 227,213 | — | −200,761 | 16 | — |
| next 1 | 229,286 | +2,073 | −198,122 | 16 | the Taif spur (`S3-branch_spur-at-ta-if`, hosts on HHR Makkah) replaces the Yanbu spur; Haramain joined at HHR Makkah |
| next 2 | 230,946 | +3,733 | −200,257 | 16 | the Riyadh–Hafar Al-Batin trunk replaces the Al Jubayl–Hafar Al-Batin trunk; Al-Oyun replaces Al-Jarn (tie class) |

The minimum is unique at the level of line corridors: no other line set reaches 227,213.

## 3. Joining the islands (verified on the graph, `runs/r6/l6/attachments.json`)

| island | joined by | through | rule |
|---|---|---|---|
| Haramain (c1) | `S3-branch_spur-yanbu-al-sina-iyah-yanbu-ind` (Yanbu Industrial City spur, hosts on HHR) + `S2-trunk_gap-jeddah-yanbu` | HHR Madinah ↔ the spur's Madinah station, **0.000 km**; the spur's Yanbu ↔ the trunk's Yanbu, 0.000 km; the trunk's Jeddah terminal ↔ `landbridge:jeddah`, **0.000 km** | walk (≤ 0.4 km) at every link |
| GCC (c2) | `S4-commuter_belt-dammam-khobar-dhahran-180` + the Al-Jarn station addition (inserted into SAR East) | GCC Dammam ↔ the belt's Dammam–Khobar–Dhahran terminal, **0.000 km**; the belt's Al Jarn ↔ SAR East Al Jarn (inserted), **0.000 km**; SAR East continues to Hufuf | walk (≤ 0.4 km) |

The Haramain island is not joined across the 8.21 km Jeddah gap. It is joined at HHR Madinah by a corridor that was already studied and hosts on HHR, which is the brief's example "Jeddah–Yanbu plus the Yanbu spur". The GCC island is not joined by a silent 3.74 km Dammam interchange. It is joined by a studied commuter belt whose terminal is the GCC Dammam point and which meets SAR East at Al Jarn.

The Al Jubayl–Hafar Al-Batin trunk also attaches to the GCC line at the Al Jubayl station addition, which the library inserts into the GCC railway. That puts Al Jubayl and Hafar Al-Batin on the graph.

**Caveat on the Jeddah link.** The Jeddah–Yanbu trunk's Jeddah terminal is the A-screen-013 Jeddah metro anchor. It has the same coordinates as the unpublished Landbridge Jeddah placeholder (21.55044 N, 39.17424 E), so the main-side link holds only while the placeholder stands (A-station-001 P1). If a Landbridge Jeddah site is ever published, the link has to be re-checked under the same rules.

**Cities** (`search.json` → `check`):
- On the graph by T1 at 0.000 km: Riyadh, Jeddah, Dammam–Khobar–Dhahran, Taif, Tabuk, Abha–Khamis Mushait, Jazan, Najran, Yanbu, Bisha, Arar, Hafar Al-Batin, Sakaka, Al-Kharj and Al Jubayl.
- By T2:
  - Makkah: HHR Makkah, 3.98 km from the Makkah anchor;
  - Madinah: HHR Madinah, 8.96 km from the Madinah anchor;
  - Buraidah: SAR North's Qassim station, 21.52 km from the Buraidah anchor.
- Reported, not on the graph:
  - Ha'il: SAR North Hail is 18.9 km from the register point, above 10 km;
  - Ar Rass: 90.9 km.
- Requiring Ha'il and Ar Rass too costs 247,564 (+20,351; 18 options: the Ar Rass–Ha'il trunk and the Ar Rass spur are added, and Al-Umran replaces Al-Jarn; fast robust NPV −220,481).

## 4. The chord-band corridors (item 4)

When the four FIX_HHR chord-band corridors are allowed, the minimum is **215,332**, 11,880 less than L6, and it uses one of them:
- `S4-commuter_belt-jeddah-315`, with the Thuwal station addition on HHR, joins the Haramain island at Thuwal instead of through the Yanbu spur;
- fast robust NPV −200,684;
- 17 options.

Its next two sets (219,065 and 220,187) also contain belt 315.

Connectivity is possible without the chord band, so **L6 is the version without it** (227,213; difference +11,880). None of `S4-commuter_belt-jeddah-000`, `-315` or `S2-trunk_gap-riyadh-jeddah` is in L6. `-045` is not in the library.

**Base corridors only (no variants, chord band excluded):**
- the same 16 corridors, all electrified;
- capex P50 251,783 (+24,570), P10/P90 sums 134,713 / 957,798;
- fast robust NPV −187,805 (12,956 less negative than L6);
- above B2 (250,000) by 1,783.

## 5. Comparison with S6-L1…L5 (`runs/r6/l6/compare.json`)

| layout | fast robust NPV (A-r6-006) | published full-judge robust NPV | capex P50 | within B1 / B2 / B3 (100 / 250 / 500 bn) | 120-min reach gain, five metros (union, A-r6-006) | national reach at 120 min, reported only (gain vs S1) | components | corridors | new route-km |
|---|---|---|---|---|---|---|---|---|---|
| S6-L1 | 12,135 | 11,023 | 11,194 | yes / yes / yes | 3.56 M | 26.67 M (+0.57 M) | 3 | 4 | 139.2 |
| S6-L2 | 7,826 | 6,792 | 1,423 | yes / yes / yes | 3.56 M | 26.25 M (+0.15 M) | 3 | 3 | 0 |
| S6-L3 | 3,361 | 2,427 | 19,630 | yes / yes / yes | 4.25 M | 26.67 M (+0.57 M) | 3 | 4 | 218.2 |
| S6-L4 | −7,005 | −7,934 | 36,726 | yes / yes / yes | 4.67 M | 26.89 M (+0.79 M) | 4 | 5 | 313.4 |
| S6-L5 | −106,909 | −112,565 | 98,170 | yes / yes / yes | 5.30 M | 26.63 M (+0.54 M) | 4 | 12 | 989.4 |
| **S6-L6** | **−200,761** | **−191,660** (§7) | **227,213** | **no** / yes / yes | **0.43 M** | **32.74 M (+6.64 M)**; 60 min 28.88 M (+6.54 M) | **1** | **16** | **3,241.9** |

Sources and notes:
- L1–L5: full-judge figures and national reach are as published (`runs/r6/top5/top5.csv`, unchanged). Fast-mode figures are recomputed with `optimise.variants.FastV`; L1's 12,135 equals the published fast MILP value.
- L6 national reach: the R6_V3 harness `optimise/reach.py` with the judge v3 files. It is a reported column only, never a score (A-r6-104); it is not a judge run.
- The S1 national reach reproduces the published 26.10 M at 120 min and 22.35 M at 60 min.

What the comparison says, in the model:
- **Connecting everything costs money.** L6 is the most negative layout in fast mode (−200,761), 1.9 times L5 (−106,909), on 2.3 times L5's capex. It lies above B1 and inside B2 and B3.
- **The reach metrics disagree.**
  - Five-metro reach: L6's 120-min gain (0.43 M) is the smallest of the six. Its long trunks and spurs serve towns far from the five metros. Only the Al Jubayl station and Dammam belt 180 add five-metro reach. L6 has no Dhahran station, which alone reaches 3.04 M of L1–L3's 3.56 M (library `S5-station_addition-dhahran`).
  - National reach: L6's 120-min gain (+6.64 M) is about eight times the best of L1–L5 (+0.79 M, L4). Station access to the whole network is the metric where a connected system shows.
- **Components:** L6 is the only layout with one component; L1–L3 have 3, and L4–L5 have 4.

## 6. Stop for Tariq (decisions asked at S6_L6_CONNECTED; taken 6 Nov 2026, below)

1. Score S6-L6 with the full judge v3 (one run, about 90 s per layout; `optimise.search full`): yes / no. If yes, choose the variant set: as built, non-electrified (227,213), or all base, electrified (251,783, above B2).
2. Carry L6 into R7 (delivery model) and R8 (report, dashboard): yes / no. Today it appears in no R7/R8 file, the dashboard (`api/data.py` LAYOUTS) or the figure index.
3. Connectivity in any future R6 round: a constraint (one component, as here), an objective (for example, the number of components or the national-reach gain), or neither.
4. Ha'il and Ar Rass: required or reported (+20,351 capex if required).
5. The chord-band version (215,332, `S4-commuter_belt-jeddah-315` and Thuwal): keep it as a sensitivity only (as here), or allow it once the corridor is accepted after FIX_HHR_REROUTE (it did not move: `docs/alignments.md` §4d).

**Decisions taken (Tariq, 6 Nov 2026; `prompts/S6_L6_SCORE.md`):**
1. Score S6-L6 with the full judge v3, **as built** (non-electrified variants, capex P50 227,213). The all-base electrified set (251,783, above B2) is **not** scored: it stays the capex sensitivity in §4. Result in §7.
2. **Do not carry L6 into R7.** CP7-1 stays: R7 is L1–L3. L4, L5 and L6 are comparison illustrations, not the recommended programme. No R7 file, delivery model or published R6–R8 figure changes. Whether to show L6 as a comparison panel in the R8 report, dashboard and figure index is a separate decision once Tariq has the score.
3. Connectivity is **neither a constraint nor an objective** in any future R6 round (§8).
4. **Ha'il and Ar Rass stay reported, not required.** The Ar Rass–Ha'il trunk and the Ar Rass spur are **not** added to L6.
5. **The chord-band version (215,332; Jeddah belt 315 + Thuwal) stays a sensitivity only.** It does not replace L6.

## 7. Full-judge score (S6_L6_SCORE)

**Comparison layout, not the recommended programme. Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** In the model only. Money is SAR million, 2025 prices; NPVs are PV at 2026 (A-cba-301); capex is P50 uplifted and undiscounted. **Alignment limitation:** lengths, costs, running times and ridership below inherit the indicative-alignment uncertainty (mean lateral offset 3–10 km on three reference lines; lengths ±5 %; `docs/alignments.md` §0, §4).

**Run.** One full-judge run of `runs/r6/l6/L6.layout.yaml` (= `scenarios/S6-L6.yaml` `layout:`, as built): judge `v3-variants` (sha256 `d9fef643…`, checked before and after the run with `optimise.judge verify`), seed 1, 10,000 draws, `--all-cases` (horizons 30 / 40 / 60 years × the five rate cases × the three population cases), the same contexts as `runs/r6/top5/<L>/score.json`. Inputs were supplied only through the adapter: `R6_OUT=runs/r6/l6 uv run python -m optimise.search full --layout runs/r6/l6/L6.layout.yaml --out runs/r6/l6/score --all-cases --engine l6-score` (115 s). Post-judge bookkeeping, which does not run the judge: `uv run python -m optimise.connect score` adds the reported-only national reach (A-r6-104) to `score.json` the way `optimise.report_v3` did for L1–L5, keeps the judge's own file as `score.judge.json`, records the layout hash `2243d1863821` in `meta.json` and writes the scorecard row `S6-L6.csv` (the `top5.csv` columns) and the map `S6-L6-map.png`. Outputs: `runs/r6/l6/score/` (`score.json`, `score.judge.json`, `meta.json` with `code_version` `judge v3-variants @ 017234562c sha256 d9fef64384e2e25f` and `harness_code_version` `r8-54-g29b6aaf`). Nothing is written under `runs/r6/top5/`.

### 7a. Fast mode vs full judge

| S6-L6 | fast mode (A-r6-006, §2) | full judge v3 | full − fast |
|---|---|---|---|
| robust NPV (min over population cases, at P50 cost) | −200,761 | **−191,660** (binding case: UN WPP low) | **+9,101 = 4.0 % of capex P50** |
| capex P10 / P50 / P90 | 122,532 / 227,213 / 860,035 (sums) | 122,532 / 227,213 / 860,035 | 0 (capex is exact in fast mode) |
| 120-min reach gain, five metros (A-r6-007) | 0.43 M (430,482) | 0.43 M (430,482) | 0 |

- **The magnitude is inside the R6 band.** In R6 the full judge differed from fast mode by 1–17 % of capex (`docs/r6-topology.md`, "Fast vs full", 14 re-scored front layouts). L6's gap is 4.0 %.
- **The direction is the opposite of R6.** In R6 the fast mode overstated robust NPV because corridors compete for the same trips. For L6 the fast mode **understates** it: the full judge is 9,101 less negative. A likely reading, not decomposed here: L6's corridors mostly feed one another and the existing lines instead of competing. For example, in the model the Landbridge 2050 load rises from 4.76 M (S1) to 5.40 M, which no single-corridor score sees. The fast mode sums single-corridor scores, each against S1, so it misses that interaction.
- The fast figures stay as published in §2–§5; they are labelled fast mode.

### 7b. Score table (full judge) beside S6-L1…L5

L1–L5 are the published full-judge v3 figures (`runs/r6/top5/top5.csv`, unchanged). L6 is `runs/r6/l6/score/S6-L6.csv` (same columns). Population cases: UN WPP low / medium / high.

| figure | S6-L1 | S6-L2 | S6-L3 | S6-L4 | S6-L5 | **S6-L6** |
|---|---|---|---|---|---|---|
| robust NPV (min over population cases, P50 cost; 60 y, Green Book 2026) | 11,023 | 6,792 | 2,427 | −7,934 | −112,565 | **−191,660** |
| NPV at P50 cost, low / medium / high | 11,023 / 13,255 / 15,556 | 6,792 / 7,572 / 8,384 | 2,427 / 4,890 / 7,428 | −7,934 / −4,864 / −1,617 | −112,565 / −110,365 / −108,017 | **−191,660 / −186,419 / −181,155** |
| NPV at P90 cost, low / medium / high | −2,958 / −724 / 1,631 | 3,986 / 4,771 / 5,589 | −21,745 / −19,225 / −16,624 | −54,553 / −51,470 / −48,184 | −229,925 / −227,697 / −225,401 | **−465,454 / −459,954 / −454,113** |
| NPV draws P10 / P50 / P90, medium | −5,243 / 11,301 / 40,819 | 1,051 / 7,053 / 18,604 | −20,113 / 2,215 / 34,873 | −48,564 / −8,477 / 32,796 | −222,390 / −109,484 / −67,710 | **−450,693 / −188,893 / −101,977** |
| BCR P10 / P50 / P90, medium | 0.60 / 2.33 / 9.33 | 1.52 / 5.96 / 22.23 | 0.32 / 1.12 / 3.48 | 0.21 / 0.75 / 2.22 | 0.03 / 0.14 / 0.37 | **−0.08 / 0.06 / 0.37** |
| capex P10 / P50 / P90 | 6,233 / 11,194 / 41,304 | 801 / 1,423 / 5,286 | 10,684 / 19,630 / 73,799 | 19,031 / 36,726 / 143,343 | 52,401 / 98,170 / 374,892 | **122,532 / 227,213 / 860,035** |
| NPV at P50 cost, medium: Green Book 2026 30 y / 40 y / 60 y | 6,227 / 8,020 / 13,255 | 4,035 / 5,307 / 7,572 | −46 / 367 / 4,890 | −7,833 / −8,870 / −4,864 | −82,021 / −99,727 / −110,365 | **−144,193 / −172,492 / −186,419** |
| NPV at P50 cost, medium, 60 y: drawn / flat 5 % / flat 7 % / TAG declining | 11,096 / 3,503 / 946 / 9,866 | 6,740 / 3,225 / 1,535 / 6,155 | 3,139 / −716 / −1,433 / 2,799 | −6,550 / −6,684 / −5,126 / −5,769 | −104,892 / −52,563 / −28,688 / −91,563 | **−177,158 / −97,505 / −56,111 / −158,182** |
| rail trips 2050, medium (added vs S1) | 23.41 M (+4.29 M) | 20.90 M (+1.78 M) | 23.96 M (+4.85 M) | 25.74 M (+6.62 M) | 24.63 M (+5.51 M) | **28.14 M (+9.03 M)** |
| added rail passenger-km 2050, medium | 669 M | 17 M | 790 M | 936 M | 418 M | **2,363 M** |
| new route-km | 139.2 | 0 | 218.2 | 313.4 | 989.4 | **3,241.9** |
| 120-min reach gain, five metros (A-r6-007; 60-min gain 0 for all six) | 3.56 M | 3.56 M | 4.25 M | 4.67 M | 5.30 M | **0.43 M** |
| national reach at 120 min, reported only (gain vs S1 26.10 M; A-r6-104) | 26.67 M (+0.57 M) | 26.25 M (+0.15 M) | 26.67 M (+0.57 M) | 26.89 M (+0.79 M) | 26.63 M (+0.54 M) | **32.74 M (+6.64 M)** |
| CO2 benefit, PV P50, medium (60 y, Green Book 2026) | 7,126 | 3,202 | 7,684 | 9,365 | 6,490 | **2,613** |
| HHR passengers 2050, medium (S1 11.27 M) | 11.28 M | 11.27 M | 11.28 M | 10.77 M | 10.35 M | **11.32 M** |
| Landbridge passengers 2050, medium (S1 4.76 M) | 5.60 M | 5.27 M | 5.11 M | 4.94 M | 4.55 M | **5.40 M** |
| wider economic impacts, PV P50, medium (indicative, not in NPV) | 142,741 | 114,628 | 267,682 | 310,951 | 370,715 | **194,050** |

What the full score says, in the model:
- **S6-L6 has the most negative robust NPV of the six layouts**: −191,660, against −112,565 for L5. It is negative in every population case, every horizon and every rate case at P50 cost; at P90 cost it is −454,113 to −465,454. The medium-case BCR range is −0.08 / 0.06 / 0.37 (P10 / P50 / P90). A negative BCR P10 means total benefits are negative in the low draws. Air quality is the one large negative benefit stream: PV P50 −10,873 against total benefits of 14,908 (medium, 60 y, Green Book 2026; `score.json` `appraisal_rows`; all 14 line corridors are the non-electrified variants; the two station additions have no traction option). The model's attribution of air quality to traction is not decomposed here.
- **It carries the most rail trips** (+9.03 M in 2050, medium; L4 has +6.62 M) and the most added passenger-km (2,363 M), on 3,242 new route-km. Per new route-km, it adds 2,785 trips against 30,828 for L1 (`added_trips_per_new_route_km`, `S6-L6.csv`).
- **The reach metrics still disagree** (as in §5). The five-metro 120-min gain is the smallest (0.43 M). The national reach gain, reported only, is about eight times L4's (+6.64 M against +0.79 M).
- **HHR and Landbridge loads in 2050 do not fall.** In the model, HHR goes from 11.27 M to 11.32 M and Landbridge from 4.76 M to 5.40 M. L5 lowers both; L4 lowers HHR (10.77 M) and raises Landbridge (4.94 M).

### 7c. Judge flags (`score.json` `flags`)
- Protected areas (WDPA, flagged, allowed): Tabuk–Sakaka 254.8 km, Bisha spur 28.2 km, Arar spur 2.2 km.
- "island (touches neither S1 nor another layout corridor)" on `S2-trunk_gap-al-jubayl-hafar-al-batin` and `S4-commuter_belt-dammam-khobar-dhahran-180`. This is the judge's phase-deliverability diagnostic (A-r6-005: a line corridor's **terminal** within 1 km of an S1 station or of another layout line corridor). It is not the rail-graph component count. Two reasons, both checked:
  - Station additions are not part of that test, so the Al Jubayl terminal of the Hafar Al-Batin trunk does not count, even though it meets the inserted GCC Al Jubayl station at 0.000 km (`attachments.json`).
  - The judge places GCC Dammam at the SAR Dammam site (A-r4-acc-004, below), so belt 180's Dammam terminal is about 3.7 km from it, above 1 km.
- On the `network.graph` rail graph (A-r6-130), L6 is still one component (§1–§3). The flags change no figure: an island is allowed, and the flag is not an error.

### 7d. Access model (A-r4-acc-004; not changed)

**The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are not rail-graph interchanges.** The access model was not changed in this run.

Which L6 figures it affects and which it does not:
- **It affects** every figure built on the judge's door-to-door and station-position graph (`access.railgraph`, which applies the overrides when it loads the S1 lines):
  - the access times;
  - the 120-min reach gain for the five metros (0.43 M);
  - the national reach, reported only (32.74 M);
  - the judge's island flags (§7c).
  
  The same located graph also supplies the rail level of service to the demand model, so trips, loads and NPV are computed with the overridden sites as well. No run without the override was made (the access model must not change), so the size of that effect on L6 is not measured.
- **It does not affect** the rail graph's component count. That count uses `network.graph.build_graph` and the line YAML station sites under the unchanged interchange rules (A-r6-130: 1 component; S1: 3). The overrides are not interchanges in that graph. Nothing in L6's connectivity (§1–§3) relies on them.

## 8. Future rounds (Tariq, 6 Nov 2026)

- **Connectivity is neither a constraint nor an objective in any future R6 round.**
- The search objective stays robust NPV (A-r6-001).
- The five-metro 120-min band stays the reach score (A-r6-007, CP7-5).
- Component count and national reach stay reported diagnostics only (A-r6-104).
- A-r6-130 (connectivity) and A-r6-131 (on-the-graph test) are now "diagnostic only, Tariq 6 Nov 2026". They define how S6-L6 was built and how components are counted; no value changed.
- Ha'il and Ar Rass stay reported, not required; the Ar Rass–Ha'il trunk and the Ar Rass spur are not added to L6.
- The chord-band version (215,332, Jeddah belt 315 + Thuwal) stays a sensitivity only and does not replace L6.
- S6-L6 is a comparison layout, not the recommended programme: R7 stays L1–L3 (CP7-1).

