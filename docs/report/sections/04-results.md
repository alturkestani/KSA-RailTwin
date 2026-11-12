> **Document version:** docs/report/sections/04-results.md v1.2 | 6 Nov 2026 | Author: report-writer; FIX_R8 (v1.1: spur figure as a layout difference, five-metro reach qualifier, national reach 'reported only', item 9); R8_L6_PANEL (v1.2: S6-L6 comparison paragraph and Figure 16 in §4.6) | Status: draft

# 4. Results

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

Everything in this section is "in the model": a scenario comparison on synthetic, uncalibrated demand, each case against its matched baseline on the same zones, seed and parameters (rule 6). Money is SAR million at 2025 prices, PV 2026; every cost and benefit is a P10 / P50 / P90 range. R6/R7 figures come from judge v3 (`v3-variants`, SHA-256 `d9fef643…`), seed 1, 10,000 draws, alignment weights v1 (runs/r6/v3/library/library.json). The tables between `gen` markers are regenerated from the run files by `uv run python -m common.report build`.

<!-- gen:fig-fig01-national-map -->
![Figure 1. National rail map: existing, committed, historical and hypothetical layers](figures/fig01-national-map.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 1.* Map of the existing, committed/under-procurement (announced/planned) and historical lines with the hypothetical CP7 additions: the station additions of S6-L2 (also in S6-L1/S6-L3 as labelled), the Al-Kharj spur (S6-L1, S6-L3) and the Riyadh belt 225 (S6-L3) on the frozen v1 alignments, with a Riyadh inset.
Source: cities/ksa/alignments/S3-branch_spur-al-kharj.geojson; cities/ksa/alignments/S4-commuter_belt-riyadh-225.geojson; cities/ksa/corridors/station_addition/S5-station_addition-al-jubayl.yaml; cities/ksa/corridors/station_addition/S5-station_addition-duruma.yaml; cities/ksa/corridors/station_addition/S5-station_addition-dhahran.yaml; cities/ksa/lines/geojson/existing.geojson; cities/ksa/lines/geojson/committed.geojson; cities/ksa/lines/geojson/historical.geojson; cities/ksa/lines/stations.geojson; runs/r6/top5/L1.layout.yaml; runs/r6/top5/L2.layout.yaml; runs/r6/top5/L3.layout.yaml; cities/ksa/zones/regions.geojson. Provenance: registers cities/ksa (lines, zones, corridors) · judge v3 d9fef643… · seed 1. S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:fig-fig01-national-map -->

## 4.1 The committed programme (S1 against S0)

S1 is the baseline for every other result, so its own appraisal matters for reading them. In the model, S1 against S0 has a P50 BCR well below 1 in every population case; its P90 BCR crosses 1 only in the medium and high cases (runs/cba/CBA-S1-committed-programme). S1 is committed, so this study does not re-decide it; the result says that the committed lines depend on benefits the model does not count (freight, which is zero here, A-cba-309; international visitors' capacity value, A-cba-310) or on demand above the synthetic base.

<!-- gen:s1 -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| population case | NPV in the model, P10 / P50 / P90 (SAR m) | BCR P10 / P50 / P90 (without WEIs) | fiscal cost to the state P10 / P50 / P90 (SAR m, fully public) |
|---|---|---|---|
| UN WPP low | −343,360 / −63,491 / 4,922 | 0.06 / 0.28 / 1.10 | 46,359 / 99,309 / 413,986 |
| UN WPP medium | −337,555 / −60,103 / 11,607 | 0.07 / 0.31 / 1.26 | 45,021 / 98,408 / 412,441 |
| UN WPP high | −333,398 / −56,608 / 18,534 | 0.07 / 0.34 / 1.42 | 43,770 / 97,461 / 410,092 |
Run: runs/cba/CBA-S1-committed-programme (R5 CBA, seed 1, 10,000 draws; S1 against S0; 60 years, Green Book 2026 declining rate A-cba-001; SAR m, 2025 prices, PV 2026).
<!-- /gen:s1 -->

## 4.2 Corridor families (each corridor alone, against S1)

Each of the 71 searchable corridors was scored alone at every phase (2030, 2035, 2040, 2050; construction starts three years earlier, A-r6-002). In the model, only four have a positive robust NPV at their best phase: the Al Jubayl, Dhahran and Duruma station additions and the Al-Kharj spur. Every trunk gap, every commuter belt and every other spur loses money in every population case at every phase; for each loss-maker, deferral to 2050 reduces the loss through the lower present value of capex (runs/r6/v3/library/; `docs/r6-topology.md` §0). No variant (line type, electrification, a dropped stop) turns a negative corridor positive (runs/r6/v3/library/variants-stage1.json).

<!-- gen:families -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| family | corridors (searchable) | robust NPV at 2030, lowest to highest (SAR m) | capex P50 at 2030, lowest to highest (SAR m) | BCR P50 at 2030 (medium), lowest to highest | positive robust NPV at the best phase (SAR m, phase) | whole family at 2030: robust NPV on capex P50 (SAR m) | R5 CBA P50 BCR range (cases ≥ 1), medium, 60 y |
|---|---|---|---|---|---|---|---|
| S2 trunk gaps | 23 | −123,523 to −24,683 | 15,857 to 113,439 | −0.01 to 0.31 | 0 | −957,580 on capex P50 761,974 | −0.01 to 0.24 (0 of 23) |
| S3 branches and spurs | 19 | −35,179 to 2,254 | 4,632 to 26,648 | −0.01 to 1.15 | 1: `S3-branch_spur-al-kharj` 4,309 at 2050 | −308,853 on capex P50 248,441 | −0.01 to 0.99 (0 of 19) |
| S4 commuter belts | 20 | −38,309 to −6,791 | 4,900 to 33,064 | 0.00 to 0.45 | 0 | −405,554 on capex P50 203,343 | −0.01 to 0.38 (0 of 20) |
| S5 station additions | 9 | −4,076 to 4,982 | 474 to 2,950 | −0.50 to 33.21 | 3: `S5-station_addition-al-jubayl` 4,982 at 2030, `S5-station_addition-dhahran` 2,362 at 2030, `S5-station_addition-duruma` 481 at 2050 | −1,174 on capex P50 6,745 | −0.58 to 45.12 (5 of 11) |
Runs: runs/r6/v3/library/<id>/score.json (standalone, every phase; Judge v3 (`v3-variants`, SHA-256 `d9fef643…`, docs/r6/judge-hashes.md), seed 1, 10,000 draws, frozen alignment weights v1); whole families runs/r6/compare/S2…S5/score.json; R5 CBA runs/cba/summary.parquet (seed 1, 10,000 draws, before the CP6 zone split). The two retired Jubail variants (CP6 P6a) are left out of the counts.
<!-- /gen:families -->

The largest variant gain is on the Riyadh–Jeddah trunk gap: in the model, building it as a conventional line instead of high speed improves its robust NPV by 19,758 but leaves it at −47,603 (runs/r6/v3/library/variants-stage1.json; `docs/r6-topology.md` §0.2).

<!-- gen:fig-fig04-bcr-bands-by-family -->
![Figure 4. BCR ranges per corridor case, by family (P10/P50/P90)](figures/fig04-bcr-bands-by-family.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 4.* P10–P90 line and P50 dot of the BCR without wider impacts for every R5 corridor CBA case against S1, in four family panels (S2–S5); UN WPP medium, 60 years, Green Book 2026; corridors of the CP7 layouts in orange.
Source: runs/cba/CBA-S2..S5-*/results.json (73 cases). Provenance: R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1.
<!-- /gen:fig-fig04-bcr-bands-by-family -->

<!-- gen:fig-fig15-capex-ranges -->
![Figure 15. Capex ranges: S1 and the CP7 layouts](figures/fig15-capex-ranges.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 15.* Undiscounted uplifted capex P10/P50/P90 (log scale) of S1 (the 10,000 R5 draws) and of the increments over S1 of S6-L2, S6-L1 and S6-L3 (judge v3 quantiles).
Source: runs/cba/CBA-S1-committed-programme/draws.parquet; runs/r6/top5/top5.csv. Provenance: R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1 · judge v3 d9fef643… · seed 1. S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:fig-fig15-capex-ranges -->

## 4.3 The five CP7 corridors, standalone at their CP7 phase

<!-- gen:cp7-corridors -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| corridor (standalone, at its CP7 phase) | capex P10 / P50 / P90 (SAR m) | robust NPV (SAR m) | NPV at P90 cost, low / medium / high (SAR m) | BCR P10, low / medium / high | run |
|---|---|---|---|---|---|
| Al Jubayl station (GCC Railway) (`S5-station_addition-al-jubayl`) | 267 / 474 / 1,762 | 4,982 | 4,007 / 4,538 / 5,082 | 2.76 / 3.08 / 3.43 | `runs/r6/v3/library/S5-station_addition-al-jubayl/score.json` |
| Dhahran station (SAR East line) (`S5-station_addition-dhahran`) | 267 / 474 / 1,762 | 2,362 | 1,262 / 1,533 / 1,818 | 1.23 / 1.34 / 1.46 | `runs/r6/v3/library/S5-station_addition-dhahran/score.json` |
| Duruma station (Landbridge) (`S5-station_addition-duruma`) | 267 / 474 / 1,762 | 481 | −121 / −30 / 61 | 0.63 / 0.70 / 0.76 | `runs/r7/corridors/S5-station_addition-duruma@2050/score.json` |
| Al-Kharj spur (`S3-branch_spur-al-kharj`) | 5,433 / 9,771 / 36,018 | 4,309 | −6,870 / −5,419 / −3,866 | 0.37 / 0.42 / 0.47 | `runs/r7/corridors/S3-branch_spur-al-kharj@2050/score.json` |
| Riyadh commuter belt 225 (Al Muzahimiyah, Duruma) (`S4-commuter_belt-riyadh-225`) | 4,717 / 8,910 / 34,256 | −8,293 | −18,991 / −18,663 / −18,329 | 0.06 / 0.06 / 0.07 | `runs/r7/corridors/S4-commuter_belt-riyadh-225@2050/score.json` |
Run: runs/r7/fiscal/fiscal.json, corridor `basis` (Judge v3 (`v3-variants`, SHA-256 `d9fef643…`, docs/r6/judge-hashes.md), seed 1, 10,000 draws, frozen alignment weights v1). Standalone corridors do not add up to a layout: corridors compete for the same trips.
<!-- /gen:cp7-corridors -->

Reading the table: the two 2030 station additions are positive even at P90 cost; Duruma is close to zero at P90 cost; the Al-Kharj spur is positive at P50 cost but negative at P90 cost in every population case when scored alone; the Riyadh commuter belt 225 is negative at P50 cost (runs/r7/fiscal/fiscal.json).

## 4.4 Programmes against S1: central, upside and reach

<!-- gen:programmes -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| (each against S1; SAR m, 2025 prices, PV 2026, 60 years, Green Book 2026) | S6-L2 | S6-L1 | S6-L3 |
|---|---|---|---|
| role | central case | upside case (carries the Al-Kharj spur's P90 cost risk) | reach alternative |
| corridors (phase year; construction starts 3 years earlier, A-r6-002) | Al Jubayl station, Dhahran station (phase 2030); Duruma station (phase 2050) | Al Jubayl station, Dhahran station (phase 2030); Al-Kharj spur, Duruma station (phase 2050) | Al Jubayl station, Dhahran station (phase 2030); Al-Kharj spur, Riyadh commuter belt 225 (phase 2050) |
| robust NPV (worst population case, P50 PVB − P50 PVC) | 6,792 | 11,023 | 2,427 |
| NPV at P50 cost, low / medium / high | 6,792 / 7,572 / 8,384 | 11,023 / 13,255 / 15,556 | 2,427 / 4,890 / 7,428 |
| NPV at P90 cost, low / medium / high (held-out test) | 3,986 / 4,771 / 5,589 | −2,958 / −724 / 1,631 | −21,745 / −19,225 / −16,624 |
| NPV P10 / P50 / P90 of the draws (medium) | 1,051 / 7,053 / 18,604 | −5,243 / 11,301 / 40,819 | −20,113 / 2,215 / 34,873 |
| BCR P10 / P50 / P90 (medium, without WEIs) | 1.52 / 5.96 / 22.23 | 0.60 / 2.33 / 9.33 | 0.32 / 1.12 / 3.48 |
| capex P10 / P50 / P90 (uplifted, undiscounted) | 801 / 1,423 / 5,286 | 6,233 / 11,194 / 41,304 | 10,684 / 19,630 / 73,799 |
| added rail trips 2050, medium (vs S1) | 1.78 M | 4.29 M | 4.85 M |
| new route-km | 0 | 139 | 218 |
| reach gain within 120 door-to-door min of the five metros (2025 population) | 3.56 M | 3.56 M | 4.25 M |
| Green Book 2026 at 30 / 40 years; flat 5 % / 7 % (NPV at P50 cost, medium) | 4,035 / 5,307; 3,225 / 1,535 | 6,227 / 8,020; 3,503 / 946 | −46 / 367; −716 / −1,433 |
Run: runs/r6/top5/top5.csv and runs/r6/top5/L1|L2|L3/score.json (Judge v3 (`v3-variants`, SHA-256 `d9fef643…`, docs/r6/judge-hashes.md), seed 1, 10,000 draws, frozen alignment weights v1). NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv for S6-L1.
<!-- /gen:programmes -->

- **S6-L2, the central case.** In the model it stays positive at P90 cost in every population case and its NPV P10 of the draws is positive (1,051, medium); its capex is about one-eighth of S6-L1's at P50 (1,423 against 11,194). It gives up the Al-Kharj spur's added trips (runs/r6/top5/top5.csv).
- **S6-L1, the upside case.** It has the highest robust NPV found by every engine (runs/r6/v3/milp/; runs/r6/v3/ga/), and the difference between S6-L1 and the same layout without the spur (S6-L2) is SAR 4,231 m of robust NPV (11,023 against 6,792); the spur also adds about SAR 36 bn to capex P90 against about SAR 9.8 bn at P50. It carries that risk: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv. A non-electrified spur narrows the P90 loss (low case −2,958 → −2,008) but lowers the robust NPV to 10,648, so it was not adopted (runs/r6/v3/cp7/cp7.csv; A-r6-105).
- **S6-L3, the reach alternative.** In the model it adds 0.68 M people within 120 door-to-door minutes of the five metros relative to S6-L1 and S6-L2 (4.25 M against 3.56 M), for a robust NPV 8,596 below S6-L1's; it is negative at P90 cost in every case and at 30 years or flat 5 % / 7 % (runs/r6/top5/top5.csv). None of the seven variant edits tried on it improved it (runs/r6/v3/cp7/cp7.csv).
- **Wider economic impacts** (TAG A2.4, indicative only, not in any score): PV P50 114,628 (S6-L2), 142,741 (S6-L1), 267,682 (S6-L3), medium case (runs/r6/top5/top5.csv). They are far larger than the user benefits for reasons the CBA note explains (`docs/cba.md` §7); they are not used for any decision here.

<!-- gen:fig-fig06-l1-p90-cost-risk -->
![Figure 6. S6-L1 upside case: NPV at P50 and at P90 capex](figures/fig06-l1-p90-cost-risk.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 6.* Incremental NPV over S1 at P50 and at P90 capex for the low, medium and high population cases: S6-L1 highlighted (the Al-Kharj spur's P90 cost risk), S6-L2 and S6-L3 faint for scale.
Source: runs/r6/top5/top5.csv; runs/r6/top5/L1/score.json. Provenance: judge v3 d9fef643… · seed 1. S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:fig-fig06-l1-p90-cost-risk -->

<!-- gen:fig-fig12-isochrones -->
![Figure 12. Door-to-door isochrones: Jeddah and Dammam](figures/fig12-isochrones.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 12.* Door-to-door isochrones from each metro's boarding stations: Jeddah S0 (hatched) against S1 (filled); Dammam–Khobar–Dhahran S1 (hatched) against S1 plus the Dhahran station addition of all three CP7 layouts (filled); the bands drawn are the ones that reach at least one zone (listed on the figure).
Source: runs/access/S0/jeddah/isochrone_door_to_door.geojson; runs/access/S1/jeddah/isochrone_door_to_door.geojson; runs/access/S1/dammam/isochrone_door_to_door.geojson; runs/access/S5-station_addition-dhahran/dammam/isochrone_door_to_door.geojson; cities/ksa/lines/stations.geojson; cities/ksa/lines/geojson/existing.geojson; cities/ksa/lines/geojson/committed.geojson; runs/access/S1/reached.parquet; runs/access/S5-station_addition-dhahran/reached.parquet; access/railgraph.py (same-station trips excluded). Provenance: R4/R5 access runs/access (code r4-15-g3d49c58) · seed 1 · registers cities/ksa (lines, zones, corridors).
<!-- /gen:fig-fig12-isochrones -->

## 4.5 Fiscal exposure and delivery models

<!-- gen:fiscal -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| programme | delivery model | net fiscal cost PV 60 y P10 / P50 / P90 (expected), SAR m | peak share of state expenditure at P50 / P90 capex (year) | contingent liabilities PV expected / P90, SAR m |
|---|---|---|---|---|
| S6-L2 | `fully_public_sar` | 695 / 1,283 / 4,088 (2,171) | 0.024 % / 0.091 % (2027) | 0 / 0 |
| S6-L2 | `ppp_dbfom_availability` | 2,166 / 2,166 / 4,866 (3,065) | 0.007 % / 0.007 % (2050) | 899 / 2,700 |
| S6-L1 | `fully_public_sar` | 4,676 / 8,441 / 23,615 (13,177) | 0.179 % / 0.662 % (2047) | 0 / 0 |
| S6-L1 | `ppp_dbfom_availability` | 13,443 / 13,443 / 28,054 (18,301) | 0.057 % / 0.057 % (2050) | 4,859 / 14,611 |
| S6-L1 | `ppp_dbfom_demand_risk` | 8,409 / 8,409 / 23,592 (13,450) | 0.230 % / 0.230 % (2047) | 5,041 / 15,182 |
| S6-L3 | `fully_public_sar` | 12,696 / 18,962 / 45,343 (27,275) | 0.327 % / 1.230 % (2047) | 0 / 0 |
| S6-L3 | `ppp_dbfom_availability` | 27,495 / 27,495 / 53,113 (36,054) | 0.114 % / 0.114 % (2050) | 8,559 / 25,617 |
| S6-L3 | `ppp_dbfom_demand_risk` | 17,723 / 17,723 / 44,007 (26,495) | 0.479 % / 0.479 % (2047) | 8,771 / 26,283 |
Run: runs/r7/fiscal/fiscal.json, population case un_wpp_low (robust), Judge v3 (`v3-variants`, SHA-256 `d9fef643…`, docs/r6/judge-hashes.md), seed 1, 10,000 draws, frozen alignment weights v1. Availability-PPP figures have P10 = P50 by construction (fixed price; capex enters only through the overrun above the private cushion); expected values rest on the lognormal tail A-fund-108. S6-L1, the upside case: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.

S1 baseline (fully public, 60 y, un_wpp_low): fiscal cost P10 / P50 / P90 46,359 / 99,309 / 413,986 SAR m (runs/cba/CBA-S1-committed-programme, via runs/r7/fiscal/fiscal.json `baseline_s1`); every programme figure above is incremental to S1.
<!-- /gen:fiscal -->

<!-- gen:vfm -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| entity | E[PSC] (SAR m) | E[availability PPP] (SAR m) | VfM (% of PSC); > 0 favours the PPP | sign robust to every registered range | VfM at flat 5 % / sovereign real rate (SAR m) |
|---|---|---|---|---|---|
| `S6-L2` | 2,171 | 3,065 | −894 (−41.2 %) | yes | −366 / −705 |
| `S6-L1` | 13,177 | 18,301 | −5,124 (−38.9 %) | yes | −1,563 / −3,596 |
| `S6-L3` | 27,275 | 36,054 | −8,779 (−32.2 %) | yes | −2,591 / −6,091 |
| `S3-branch_spur-al-kharj` | 10,986 | 15,216 | −4,230 (−38.5 %) | yes | −1,197 / −2,890 |
| `S4-commuter_belt-riyadh-225` | 14,747 | 18,607 | −3,860 (−26.2 %) | yes | −1,086 / −2,635 |
| `S5-station_addition-al-jubayl` | 476 | 821 | −344 (−72.2 %) | yes | −154 / −282 |
| `S5-station_addition-dhahran` | 991 | 1,335 | −344 (−34.7 %) | yes | −154 / −282 |
| `S5-station_addition-duruma` | 653 | 859 | −205 (−31.4 %) | yes | −58 / −140 |
Run: runs/r7/vfm/vfm.json (60 years, robust case; Judge v3 (`v3-variants`, SHA-256 `d9fef643…`, docs/r6/judge-hashes.md), seed 1, 10,000 draws, frozen alignment weights v1); parameters A-fund-002, A-fund-007, A-fund-008, A-fund-102, A-fund-103. The private-finance premium is sourced from a UK reference class and is unclear for Saudi Arabia[^S-fund-r7-001]. S6-L1, the upside case: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:vfm -->

What drives the result in the model: fares cover a small share of operating costs, so every option leaves the state paying; private finance at a premium costs about what the transferred construction risk is worth; and the transfer stops at the private equity cushion while the capex tail (P90 about 3.7 × P50) goes far beyond it, so the state keeps the tail under every model (runs/r7/fiscal/fiscal.json; A-fund-102). On that evidence the R7 analysis names fully public delivery as the best fit for every CP7 corridor and programme (analyst's judgement, `docs/delivery-models.md`), with the alternatives set out beside it. The arguments for a PPP are in §6.3; the conditions under which the sign would change are the switching values in `docs/fiscal-exposure.md` (for example, a fixed-price bid about 80 % below the un-uplifted base estimate, A-fund-007).

<!-- gen:fig-fig10-fiscal-exposure -->
![Figure 10. Fiscal exposure by delivery model (60-year PV)](figures/fig10-fiscal-exposure.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 10.* Net fiscal cost to the state (PV 60 years, low population) of each CP7 layout under fully public delivery, availability PPP and demand-risk concession: P10–P90 bar, P50 line and expected value; S1 baseline (fully public, against S0) beside.
Source: runs/r7/fiscal/fiscal.json; runs/cba/CBA-S1-committed-programme. Provenance: R7 funding engine runs/r7 on judge v3 d9fef643… scores · seed 1 · R5 CBA runs/cba (economics.cba, code r4-15-g3d49c58) · seed 1.
<!-- /gen:fig-fig10-fiscal-exposure -->

<!-- gen:fig-fig11-vfm -->
![Figure 11. Value for money: public sector comparator against availability PPP](figures/fig11-vfm.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 11.* Expected net fiscal cost (PV 60 years, low population) of the public sector comparator and of an availability PPP for the three CP7 layouts and their five corridors, with P10/P50/P90 whiskers and the VfM difference (% of PSC).
Source: runs/r7/vfm/vfm.json; runs/r7/fiscal/fiscal.json. Provenance: R7 funding engine runs/r7 on judge v3 d9fef643… scores · seed 1.
<!-- /gen:fig-fig11-vfm -->

## 4.6 Trade-offs: the Pareto front and the reach front

In the model the robust-NPV optimum is small and the budget does not bind: the exact MILP gives the same four-corridor layout (S6-L1) at B1, B2 and B3 (runs/r6/v3/milp/; A-r6-003). The trade-off runs on reach. Moving from 3.56 M people within 120 door-to-door minutes of the five metros (S6-L1, S6-L2) up the reach front costs robust NPV at every step, and the overall front ends at about 5.42 M people at SAR 214–235 bn capex, so B3 (SAR 500 bn) never binds (runs/r6/v3/ga/; runs/r6/v3/rescore/). S6-L1, the optimum, carries the Al-Kharj spur's P90 cost risk: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.

**Trade-off illustrations only (no recommendation, no delivery model, no stage-gate).** Two layouts from the optimisation show what reach (people within 120 door-to-door minutes of the five metros) costs: S6-L4 (S6-L3 plus the Makkah belt 045) reaches 4.67 M people for a robust NPV of −7,934, and S6-L5 (the two 2030 stations plus ten commuter belts in four metros) reaches 5.30 M for −112,565 on capex P50 98,170 (runs/r6/top5/top5.csv). They appear in Figures 7 and 8 only.

<!-- gen:fig-fig07-pareto-front -->
![Figure 7. Pareto front: NPV against capex](figures/fig07-pareto-front.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 7.* R6 full-judge front points (medium-population NPV at P50 cost against capex P50, bar = low–high population) with S6-L1, S6-L2 and S6-L3 marked by P10–P90 of the NPV draws and of capex in a zoom panel; S6-L4/L5 are unlabelled front points (trade-off illustration only). S6-L6 is not on the R6 front (it was built by the connectivity search, not the NPV/reach search) and is shown in Figures 8 and 16.
Source: runs/r6/pareto_front.csv; runs/r6/top5/top5.csv. Provenance: R6 full-judge front runs/r6/pareto_front.csv (judge v2-p5b, reproduced exactly by v3: docs/r6/judge-v3-backtest.md) · judge v3 d9fef643… · seed 1. S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:fig-fig07-pareto-front -->

<!-- gen:fig-fig08-reach-tradeoff -->
![Figure 8. Cost against reach: S6-L1 to S6-L6](figures/fig08-reach-tradeoff.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 8.* Capex P50 with P10–P90 bars against the five-metro 120-minute door-to-door reach gain over S1 (A-r6-007) for S6-L1 to S6-L6, over the R6 front points. S6-L4 and S6-L5 are reach trade-off illustrations from the search only: no recommendation. S6-L6 is a connectivity comparison (the smallest-capex connecting set), not a search-front point and not a recommendation; its national reach gain is +6.64 M (reported only, A-r6-104), which the plotted five-metro measure does not show.
Source: runs/r6/top5/top5.csv; runs/r6/pareto_front.csv; runs/r6/l6/score/S6-L6.csv. Provenance: judge v3 d9fef643… · seed 1 · R6 full-judge front runs/r6/pareto_front.csv (judge v2-p5b, reproduced exactly by v3: docs/r6/judge-v3-backtest.md) · S6-L6 full-judge score runs/r6/l6/score (judge v3 d9fef643… · seed 1, layout 2243d1863821). S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.
<!-- /gen:fig-fig08-reach-tradeoff -->

**Comparison layout, not the recommended programme (no recommendation, no delivery model, no stage-gate).** S6-L6 is not a reach trade-off and not a search result: it was built afterwards, by the connectivity MILP, as the smallest-capex connecting set from the R6_V3 single-corridor library: 16 non-electrified options, one rail-graph component, 18 of 18 required cities on the graph (`docs/r6-l6-connected.md`; A-r6-130 to A-r6-134). Scored with the full judge v3 (hash d9fef643…, seed 1), its robust NPV is −191,660 at capex P50 227,213 (P10 / P90 122,532 / 860,035), and its medium-case BCR is 0.06 at P50 (P10 / P90 −0.08 / 0.37) (scenarios/S6-L6.yaml `score:`; runs/r6/l6/score/S6-L6.csv). In the model it adds the most rail trips of the six layouts (+9.03 M in 2050, medium; S6-L4 +6.62 M) and the most national reach (+6.64 M people within 120 minutes of a station, reported only, A-r6-104; S6-L4 +0.79 M), but the smallest five-metro 120-minute gain (0.43 M; S6-L2 3.56 M), because its long trunks and spurs sit far from the five metros and it has no Dhahran station (S6-L1 to S6-L5 from runs/r6/top5/top5.csv). Fast mode gave −200,761, so it understated the full score by 9,101 (4.0 % of capex P50). That is the opposite of R6, where fast mode overstated it; the likely reading (not decomposed) is that these corridors feed each other instead of competing for the same trips (`docs/r6-l6-connected.md` §7a). The judge still uses the access-model site overrides (A-r4-acc-004: Landbridge Jeddah with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam) for door-to-door times; those are not rail-graph interchanges, and the access model is unchanged. Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast; alignment limitation: lengths, costs, running times and ridership inherit the indicative-alignment uncertainty (`docs/alignments.md` §0, §4). S6-L6 appears in Figures 8 and 16 only; it is not on the R6 front in Figure 7.

<!-- gen:fig-fig16-l6-connected-map -->
![Figure 16. S6-L6: one connected rail system (comparison layout, not the recommended programme)](figures/fig16-l6-connected-map.svg)
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
*Figure 16.* The existing connected-system map of S6-L6 from the connecting-set search (S6_L6_CONNECTED), reused unchanged: S1 lines and the 16 library options of S6-L6 as one rail-graph component, the corridors joining an S1 island highlighted and the 18 required cities annotated, beside the S6-L6 full-judge v3 scorecard. Comparison layout, not the recommended programme; the access-model site overrides (A-r4-acc-004) are not rail-graph interchanges.
Source: docs/report/figures/s6-l6-connected-map.png; runs/r6/l6/search.json; runs/r6/l6/score/S6-L6.csv; scenarios/S6-L6.yaml. Provenance: S6-L6 connecting-set search runs/r6/l6/search.json (optimise.connect, code r8-45-g0ef4623-dirty) · seed 1 · S6-L6 full-judge score runs/r6/l6/score (judge v3 d9fef643… · seed 1, layout 2243d1863821) · registers cities/ksa (lines, zones, corridors).
<!-- /gen:fig-fig16-l6-connected-map -->

No layout brings any new zone within 60 door-to-door minutes of a metro (runs/r6/top5/top5.csv, `access_gain_60` = 0). The national reach, reported only (a column outside the score, A-r6-104), counts every zone within 120 door-to-station minutes of any station: S1 alone reaches 26.10 M of 35.93 M people, and the CP7 layouts add 0.15 M (S6-L2) to 0.57 M (S6-L1, S6-L3) (runs/r6/v3/national_reach.json; A-r6-104). S6-L1 carries the Al-Kharj spur's P90 cost risk: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv.

## 4.7 People, equity and the 30-minute lens

**Who gains, in the model.** Splitting each case's user benefits half to the origin and half to the destination zone (TAG A4.2 share-of-benefit against share-of-population[^S-soc-051]): the Al-Kharj spur's benefits fall about 90 % in the Riyadh region, the Al Jubayl and Dhahran stations' about 100 % in the Eastern Province, and Duruma's and the Riyadh belt's in the Riyadh region. Grouping regions into terciles of Saudi unemployment (a regional proxy, not household income, A-cba-311; LFS Q4 2025[^S-soc-016]) the high-unemployment tercile (14.6 % of the population) receives 0.0 % of the user benefits of every CP7 corridor (runs/cba/CBA-S3-branch_spur-al-kharj, runs/cba/CBA-S5-station_addition-al-jubayl, runs/cba/CBA-S5-station_addition-dhahran, runs/cba/CBA-S5-station_addition-duruma, runs/cba/CBA-S4-commuter_belt-riyadh-225; `docs/distribution.md`). These are R5 CBA runs (before the CP6 zone split); the regional pattern, not the level, is the finding.

**Who is left out.** In the Riyadh region 17 towns of 10,000 or more (617,718 people) stay more than 30 km from every station after the Al-Kharj spur, and in the Eastern Province 10 towns (638,328 people) after the Al Jubayl station (A-cba-313; runs/cba/CBA-S3-branch_spur-al-kharj, runs/cba/CBA-S5-station_addition-al-jubayl).

**Who pays.** The state, through the net fiscal cost in §4.5; users pay fares (PV in each case's distribution table). Fare-to-income ratios cannot be computed: no income-by-zone source exists (`docs/social.md` B4).

**Social evidence that bears on the results** (`docs/social.md`, literature review; sources verified unless marked):

- Commuting tolerance: in Q4 2025, 46.2 % of unemployed Saudi men and 63.8 % of unemployed Saudi women accept at most one hour of commuting[^S-soc-017].
- Heat and first/last mile: the national mean daily maximum in July is 41.5 °C[^S-soc-025], and safe walking access to public transport in Riyadh is very limited in extreme heat[^S-soc-026]; the model applies a summer access factor (A-access-011) but no Saudi seasonal ridership evidence was found.
- Women's mobility: Saudi female labour-force participation rose from 20.2 % (Q4 2018, secondary) to 34.5 % (Q4 2025)[^S-soc-007][^S-soc-001][^S-soc-002], and 37.7 % of surveyed women switched to driving after 2018[^S-soc-011]; no Saudi evidence was found on the effect of transport access on women's employment.
- Family and religious travel: visiting friends and relatives was 40.4 % of 2025 domestic trips[^S-soc-031]; 25.06 M internal Umrah performers in 2025[^S-soc-029]. International pilgrims carry no user benefits in the model (A-cba-310).
- Land and heritage: the 2025 expropriation law sets compensation at market value plus 20 % and damages (secondary)[^S-soc-043]; the expropriation procedure for a rail alignment is one of the open questions in §6.5.

**The 30-minute lens.** For towns 40–120 road-km from each metro (A-screen-005, A-screen-013), in the model:

<!-- gen:commute -->
> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| metro | towns 40–120 road-km | ≤ 30 min in-vehicle rail: S0 | S1 | with at least one S2–S5 candidate |
|---|---|---|---|---|
| Abha–Khamis Mushait | 13 | 0 | 0 | 0 |
| Buraidah | 42 | 0 | 0 | 0 |
| Dammam–Khobar–Dhahran | 7 | 0 | 0 | 0 |
| Jazan | 36 | 0 | 0 | 0 |
| Jeddah | 23 | 14 | 14 | 17 |
| Madinah | 1 | 0 | 0 | 0 |
| Makkah | 17 | 3 | 3 | 4 |
| Najran | 5 | 0 | 0 | 0 |
| Riyadh | 105 | 0 | 0 | 49 |
| Tabuk | 4 | 0 | 0 | 0 |
| Taif | 26 | 0 | 0 | 2 |
Run: runs/access/commute-test-s1/commute_test.parquet (seed 1; towns from the register, road km from OSRM, running-time band A-r4-rt-011, summer factor A-access-011).
<!-- /gen:commute -->

Around Riyadh no town has a 30-minute in-vehicle rail time under S0 or S1, and at least one generated candidate gives one to 49 of 105 such towns; around Jeddah the existing and committed lines already give it to 14 of 23 (runs/access/commute-test-s1/commute_test.parquet). Door-to-door times are much longer than in-vehicle times once access, waiting and the summer factor are counted (`docs/commute-test.md`).
