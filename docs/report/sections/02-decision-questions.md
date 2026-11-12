> **Document version:** docs/report/sections/02-decision-questions.md v1.0 | 4 Nov 2026 | Author: report-writer | Status: draft

# 2. Decision questions

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.

The brief (PROJECT.md §1) sets seven decision questions, all at national scope, and keeps the 30-minute commute test as one lens (runs/access/commute-test-s1/). The table gives each question, where the report answers it and the short answer in the model. The short answers are options with their evidence; none is advice to any entity.

> Labels: synthetic demand, uncalibrated: scenario comparison, not a forecast. alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and running times inherit that uncertainty.
| # | question (PROJECT.md §1) | where answered | short answer in the model (ranges; run ids in the sections) |
|---|---|---|---|
| 1 | **Network.** Across all 13 regions and every governorate, which links, branches, commuter belts and station additions create the most value? | §4.1–§4.3, Annex R | Four of 71 searchable corridors have a positive robust NPV when scored alone: three station additions and the Al-Kharj spur (runs/r6/v3/library/). No trunk gap or commuter belt does at any phase. |
| 2 | **Cost.** What does each option cost to build, run and renew, with land, financing and a realistic overrun allowance? | §3.5, §4.2–§4.4, §6.1 | Capex is a reference-class range with a heavy tail: P90 about 3.7 × P50 for every CP7 layout (runs/r6/top5/top5.csv; A-rcf-001). |
| 3 | **Benefit.** Do 30–60 year benefits exceed costs under honest assumptions? | §4.2–§4.4 | For the central case S6-L2, yes in every population case even at P90 cost; for the upside case S6-L1, in every case at P50 cost but not in the low and medium cases at P90 cost; for the reach alternative S6-L3, not at P90 cost. S6-L1: NPV at P90 cost −2,958 / −724 / +1,631 SAR m (low / medium / high), runs/r6/top5/top5.csv. |
| 4 | **Who pays and who owns.** Which delivery and funding model fits each corridor; who carries which risk; what is the fiscal exposure? | §4.5, §6.3, §6.5 | Fully public delivery is cheaper in expected PV than an availability PPP for every entity, robust to every registered range (runs/r7/vfm/vfm.json); 13 legal and institutional questions stay open (cities/ksa/funding/recommendations.yaml). |
| 5 | **Benchmarks.** What did France, Japan, Spain, Germany, China, South Korea, Italy, Morocco, Turkey, the UAE, Egypt and others do; did small towns gain? | §5 | Overruns are common, ridership is mostly below forecast where measured, and small-town effects are mixed to negative[^S-bench-st-014][^S-bench-st-001]. |
| 6 | **People.** How would rail change commuting, work, women's mobility, family and religious travel, housing and regional balance; who gains and who loses? | §4.7 | In the model the user benefits of every CP7 corridor fall in the Riyadh and Eastern regions; the high-unemployment tercile of regions gains nothing from them (runs/cba/CBA-S3-branch_spur-al-kharj and the station cases; A-cba-311). |
| 7 | **Optimisation and phasing.** Which network, technology, service pattern, fares and build sequence balance NPV, coverage, emissions and fiscal exposure to 2050/2060? | §4.6, §7 | The robust-NPV optimum is small and the budget levels do not bind (A-r6-003); reach costs NPV; §7 sets the phasing as stage-gates. |

The 30-minute lens: for towns 40–120 road-km from a metro, the committed programme gives no town around Riyadh a 30-minute in-vehicle rail time, while at least one generated candidate does for 49 of 105 such towns (runs/access/commute-test-s1/commute_test.parquet; §4.7).
