> **Document version:** docs/benchmarks/germany.md v0.3 | 31 Oct 2026 | Author: benchmarks-researcher; index pointer by CP2_PREP | Status: draft

# Germany: ICE (Deutsche Bahn; DB InfraGO)

Scope and method. Research from open sources on 31 Oct 2026 (read sessions, not snippets, except where marked). Figures are in the currency and price basis of each source. Price-year conversion to SAR 2025 is not done in this file (at R1b the index was not present in this worktree); converted values are generated in `README.md` by `rail.benchmarks summarise` with the single price index `cities/ksa/costs/index.yaml` (CP2 P2a, A-cost-002; it replaced `index-r1b.yaml` and A-bench-001). Metric rows are in `cities/ksa/benchmarks/metrics-germany.csv`; overrun candidates are in `cities/ksa/benchmarks/overruns-germany.csv`. Dossier evidence is mostly grade A (EU audit, Federal Government answers to the Bundestag, the operator's annual report, a state press release). Ridership shares and the current Stuttgart 21 position are grade C or unverified, and are labelled as such.

## 1. System facts

| metric | value | unit | price year | grade | source |
|---|---|---|---|---|---|
| First German high-speed lines (ICE) | opened in the early 1990s | year | n/a | A | [^S-bench-de-059] |
| Berlin–Munich audited length | 671 | km | n/a | A | [^S-bench-de-001] |
| Berlin–Munich opening (52 km not before 2018) | 2017 | year | n/a | A | [^S-bench-de-011] |
| Stuttgart–Munich audited length (excludes Stuttgart 21) | 267 | km | n/a | A | [^S-bench-de-002][^S-bench-de-022] |
| Neubaustrecke Wendlingen–Ulm project length | 59.6 | km | n/a | A | [^S-bench-de-008] |
| Neubaustrecke Wendlingen–Ulm opened | 9 Dec 2022 | date | n/a | A | [^S-bench-de-053] |
| DB Fernverkehr rail passengers | 134.5 | million, 2025 | n/a | A | [^S-bench-de-044] |
| DB Fernverkehr transport performance | 45.2 | bn passenger-km, 2025 | n/a | A | [^S-bench-de-045] |
| DB Fernverkehr revenue (Umsatz) | 6,407 | m EUR, 2025 | nominal, year 2025 | A | [^S-bench-de-058] |
| DB Fernverkehr passenger-services share of revenue | 92 | %, 2025 | n/a | A | [^S-bench-de-061] |
| Infrastructure manager | DB InfraGO | text | n/a | A | [^S-bench-de-060] |

Operator and infrastructure. Long-distance services are run by DB Fernverkehr AG, which reports its own segment figures (above). The infrastructure side is DB InfraGO. The ECA reviewed Berlin–Munich (opened 2017[^S-bench-de-011]), Stuttgart–Munich (expected 2025 at the time of the audit[^S-bench-de-012]) and four German project segments[^S-bench-de-005][^S-bench-de-006][^S-bench-de-007][^S-bench-de-008]. A German national network total for ICE-carrying line-km was not found in the sources read (see section 10).

Delivery and funding. The ECA states that cost overruns are borne by national budgets[^S-bench-de-021]. The Stuttgart 21 project was covered by a financing agreement of 2 April 2009 with a cost ceiling of 4.526 bn EUR at the 2004 cost level[^S-bench-de-033]. In March 2013 the DB Supervisory Board raised the financing framework by 2 bn EUR, from 4.526 bn to 6.526 bn EUR[^S-bench-de-031]. For two German sections (Halle/Leipzig–Erfurt–Ebensfeld and Stuttgart–Wendlingen–Ulm) no cost-benefit analysis was made when the decision was taken, according to the ECA[^S-bench-de-013].

## 2. Cost per km

Nominal values as printed. Price year: the ECA states that all its figures are nominal and that data are as of the audit; the year is inferred as 2017 and is flagged in the metrics file. Converted SAR 2025 values: not converted (see scope note).

| line or segment | length (km) | initial estimate (m EUR/km) | final or real (m EUR/km) | total (m EUR) | price basis | grade | source |
|---|---|---|---|---|---|---|---|
| Berlin–Munich | 671 | 12.4 | 21.9 | 14,682 (as audited) | nominal; 2017 inferred | A | [^S-bench-de-001] |
| Stuttgart–Munich (excludes Stuttgart 21) | 267 | 6.9 | 49.7 | 13,273 | nominal; 2017 inferred | A | [^S-bench-de-002][^S-bench-de-022] |
| Stuttgart–Munich, text: most recent constructions | n/a | n/a | above 40 | n/a | nominal; 2017 inferred | A | [^S-bench-de-003] |
| VDE 8.1 Ebensfeld–Erfurt (project) | 60.9 | n/a | 13.4 | 815 real (705.8 initial) | nominal; 2017 inferred | A | [^S-bench-de-005] |
| VDE 8.2 Erfurt–Leipzig/Halle (project) | 122 | n/a | 6.3 | 770 real (762 initial) | nominal; 2017 inferred | A | [^S-bench-de-006] |
| Stuttgart–Wendlingen incl. Stuttgart 21 (project) | 57 | n/a | 114.5 | 6,526 real (2,894.5 initial) | nominal; 2017 inferred | A | [^S-bench-de-007] |
| Neubaustrecke Wendlingen–Ulm (project) | 59.6 | n/a | 54.7 | 3,259 real (2,065.5 initial) | nominal; 2017 inferred | A | [^S-bench-de-008] |

Range across the German rows: 6.3 to 114.5 m EUR/km (segments, real cost); 21.9 to 49.7 m EUR/km (full line, as audited, excluding Stuttgart 21 for Stuttgart–Munich). The range is wide because the rows mix long bored or urban-node sections with line totals, and so are not like-for-like. Cost per minute saved, as printed in the ECA table, is 104.87 m EUR for Berlin–Munich[^S-bench-de-009] and 368.69 m EUR for Stuttgart–Munich[^S-bench-de-010].

The ECA attributes the high Stuttgart–Munich figures to scarcity of land, the crossing of urban nodes, viaducts and extensive tunnelling, and notes that costs "could be lower with little impact on rail operations"[^S-bench-de-003]. That is the ECA's own reading; it is not a sensitivity test.

Coordinator note (31 Oct 2026): the European Court of Auditors states its cost figures in nominal terms. One price-year rule applies to every dossier: the report year 2018 (assumption A-bench-002), so converted values are a lower bound in 2025 prices. Converted values: see `README.md`.

## 3. Ridership against forecast

**VDE 8.1 Berlin–Munich (opened December 2017).** The Federal Government reports DB AG figures: 4.9 million long-distance passengers in 2018 on the VDE 8.1 route via Jena, a rise of 2.5 million on the comparable connection, or 104 %[^S-bench-de-038]. The government cites the forecast in Drucksache 16/1379 (2006) as 1.8 million additional passenger trips[^S-bench-de-040]. The ratio of the outturn increase to the forecast is 1.39, computed by us from those two printed numbers[^S-bench-de-038][^S-bench-de-040]. The bases may differ (route definition, year, and forecast scope), so the ratio is not a like-for-like forecast-outturn test. The 2006 document itself was not opened.

**Press figure, conflicting.** A December 2018 press report quotes DB as having counted "so far" 4.4 million travellers between Berlin and Munich[^S-bench-de-051]. The counting basis is not given and differs from the 4.9 million above. Both rows are kept.

**VDE 8.2 Frankfurt–Berlin.** DB AG reports 8.9 million passengers in 2018 on the Frankfurt–Berlin connections via Braunschweig or Erfurt[^S-bench-de-039]. No forecast for this corridor was found.

**Benchmark, not a German criterion.** The ECA states that a high-speed line should ideally carry nine million passengers a year, or six million in the opening year[^S-bench-de-020]. It sources the figure to academic and institutional literature (footnote 43 of the report). It is an EU audit benchmark, not a German planning test. The ECA also records that only three of the audited completed lines carried more than nine million in 2016, none of them German[^S-bench-de-020].

**Network level (not line).** DB Fernverkehr carried 134.5 million rail passengers in 2025, up from 132.0 million in 2024[^S-bench-de-044]. This is the segment total, not a line figure.

**Ex-post evaluation.** The Federal Government says it holds no route-related survey of network traffic growth or modal shift from car and air after the VDE 8 commissioning[^S-bench-de-041]. It also says a retrospective estimate of the economic benefit of the completed sections is not possible; the last BVWP assessment was for prognosis year 2030[^S-bench-de-042].

## 4. Farebox recovery and operating ratio

No line-level farebox recovery or operating ratio was found for any German high-speed line (searched: DB Fernverkehr 2025 report, Bundestag answers on VDE 8, ECA, 31 Oct 2026). The DB Fernverkehr segment reported revenue of 6,407 m EUR in 2025[^S-bench-de-058] and a result after tax of -290 m EUR, against -427 m EUR in 2024[^S-bench-de-046]. This is a segment result after tax, not an operating ratio, and it is not a line measure. It must not be used as a farebox figure.

## 5. Thresholds and the 200–800 km band

**Density and city-size thresholds.** No reliable data found (searched: Bundestag and DB terms for ICE stop criteria, population or city-size thresholds, 31 Oct 2026). Search snippets from academic theses on population and ICE stops were seen and not used: they are not verified, and none gives a threshold.

**The 200–800 km band (a hypothesis, tested against German evidence).**

*Evidence that fits the band:*
- On Berlin–Munich (587–654 km by the ECA's city-centre measure), the ECA finds high-speed rail "the second-fastest option, and it is cheaper" door-to-door than air[^S-bench-de-018][^S-bench-de-019]. Cheaper than air is consistent with the band; the ECA does not say rail beats air on time.
- A December 2018 press report, citing a DB and Telefónica market study, gives the rail share of Berlin–Munich travellers as 46 % after opening, with air at 30 % and car or bus at 24 %[^S-bench-de-049]. Before opening the same press report gives rail at 23 % and air at 48 %, the leading mode[^S-bench-de-050]. This is the closest German evidence on air–rail substitution in the band. The study was not located, and the government says it holds no route-level data on modal shift from air and car[^S-bench-de-041].

*Evidence that qualifies it:*
- On the same corridor, the ECA says "Air travel is fastest, but expensive"[^S-bench-de-019]. Rail is therefore not the fastest door-to-door option on Berlin–Munich.
- Operational speed is low. The average speed on the audited German connections was 103 km/h, against 157 km/h in Spain[^S-bench-de-016]. Across the audited lines, trains ran at about 45 % of design speed on average[^S-bench-de-064].
- The 267 km Stuttgart–Munich line is below the band. The ECA reports that its ticket prices are lower than conventional rail[^S-bench-de-062], but no modal-share figure was found for it.

*Reading.* German evidence is consistent with the band on one corridor (cheaper than air, a press-reported shift from air) and does not confirm it as a general rule. The one independent-sounding check (the ECA's door-to-door analysis) finds air faster on the same pair. The band remains a hypothesis.

## 6. Station spacing, timetable and stopping patterns

**Station spacing.** On the Berlin–Munich route (672 km, 15 stations) the average distance between stations is 48 km; the shortest is 2 km and the longest 94 km[^S-bench-de-015]. On Stuttgart–Munich (267 km, 8 stations) the average is 38 km; the shortest is 6 km and the longest 191 km[^S-bench-de-014].

**Stopping pattern.** The difference between the most direct and the least direct service is 72 minutes on Berlin–Munich (240 against 312 minutes) and 20 minutes on Stuttgart–Munich (134 against 154)[^S-bench-de-015][^S-bench-de-014]. The ECA notes that some German high-speed lines have 50–60 connections per day[^S-bench-de-017]. A press report describes five ICE a day in each direction, in under four hours, on Berlin–Munich[^S-bench-de-052].

**Deutschlandtakt.** The Federal Government expects the half-hourly long-distance service to be run commercially, by rail operators without subsidy[^S-bench-de-043]. This is an expectation; no evaluation was found. In the preamble to a Bundestag answer, the questioners argue that the connection points at Erfurt and Halle limit the Deutschlandtakt's effects[^S-bench-de-065]. This is an opposition view, not a finding, and is recorded as such.

## 7. Overruns and renegotiations

| observation | baseline | outturn | ratio or change | grade | source |
|---|---|---|---|---|---|
| Berlin–Munich, initial estimate to total cost (ECA Table 5) | 8,337 m EUR | 14,682 m EUR | 76.1 % printed; 1.76 computed | A | [^S-bench-de-001] |
| Stuttgart–Munich, excl. Stuttgart 21 (ECA Table 5) | 1,838 m EUR | 13,273 m EUR | 622.1 % printed; 7.22 computed | A | [^S-bench-de-002][^S-bench-de-004] |
| VDE 8.1 Ebensfeld–Erfurt (ECA Annex III) | 705.8 m EUR | 815 m EUR | +15.5 % computed | A | [^S-bench-de-005] |
| VDE 8.2 Erfurt–Leipzig/Halle (ECA Annex III) | 762 m EUR | 770 m EUR | +1.0 % computed | A | [^S-bench-de-006] |
| Stuttgart–Wendlingen incl. Stuttgart 21 (ECA Annex III) | 2,894.5 m EUR | 6,526 m EUR | +125.5 % computed | A | [^S-bench-de-007] |
| Neubaustrecke Wendlingen–Ulm (ECA Annex III) | 2,065.5 m EUR | 3,259 m EUR | +57.8 % computed | A | [^S-bench-de-008] |
| Stuttgart 21, DB announcement of Dec 2012 vs the 2009 cost ceiling | 4,526 m EUR | 6,800 m EUR | +50.2 % computed | A | [^S-bench-de-032][^S-bench-de-033] |
| Stuttgart 21, faction's statement of official estimates | 2.46 bn EUR at planning start | about 11.5 bn EUR to end-2025 (excl. Pfaffensteigtunnel) | about 4.7x computed | C | [^S-bench-de-036] |
| Stuttgart 21, Bundestag 2018: estimate vs contractually secured amount | 4.5 bn EUR contractually secured | 8.2 bn EUR estimate (gap 3.7 bn, computed) | n/a | A | [^S-bench-de-034] |
| Neubaustrecke Wendlingen–Ulm, schedule | one year later than planned (2021 implied) | opened 9 Dec 2022 | +1 year | A | [^S-bench-de-035][^S-bench-de-053] |
| Berlin–Munich, planning to opening | planning 1991 | opened 2017 (26 years from planning start) | 26 years, descriptive | A | [^S-bench-de-011] |
| Stuttgart 21, schedule | original opening planned for 2008 | December 2026 opening abandoned at end 2025 | about 18 years to the abandoned date; the faction says "fast 20 Jahre" for the whole slip | C | [^S-bench-de-063][^S-bench-de-037] |

Notes. The ECA's 622.1 % for Stuttgart–Munich is a ratio on a small baseline, and its totals exclude Stuttgart 21[^S-bench-de-022]. The ECA's Stuttgart–Wendlingen "real" figure of 6,526 m EUR equals the 2013 financing framework[^S-bench-de-031]; it is therefore not an independent outturn, and should be checked against a DB outturn before use. The Wendlingen–Ulm cost conflicts across sources: the ECA gives 3,259 m EUR[^S-bench-de-008], the Federal Government in 2018 gave 3.7 bn EUR after a rise of 460 m EUR[^S-bench-de-035], and the state release of 2022 gives "just under four billion" without a price basis[^S-bench-de-054]. All three are kept.

Stuttgart 21 current position. The ECA states the project's highest overrun was 83 % for the Stuttgart 21 station[^S-bench-de-023]. The current opening date and total cost are not settled in any source read: a press report gives 2031 and about 14.5 bn EUR[^S-bench-de-055][^S-bench-de-057], but the press pages were not readable and the DB release was not reached. These figures are **unverified** and are not used in the cost or overrun metrics.

## 8. Small-town evidence: did intermediate stations gain?

**The study.** Ahlfeldt and Feddersen study the Cologne–Frankfurt high-speed line, which has intermediate stations at Montabaur and Limburg[^S-bench-de-028]. The authors use the intermediate stations as a source of exogenous variation in access to economic centres[^S-bench-de-028]. The published version appeared in the Journal of Economic Geography, volume 18, issue 2, starting on page 355 (2018)[^S-bench-de-027].

**Finding (as stated in the abstract of the 2015 working paper).** The authors find a causal effect of about 8.5 % on average on the GDP of the three counties with intermediate stops[^S-bench-de-024]. The strength of the spillover falls by half for each 30 minutes of travel time and is about 1 % after about 200 minutes[^S-bench-de-025]. Their preferred elasticity of output with respect to market potential is 12.5 %[^S-bench-de-026].

**Grade and caveat.** The peer-reviewed article is grade B, but the figures above were read in the 2015 working paper abstract, so they are grade C until the 2018 abstract is checked. The authors also say the study makes no statement for or against high-speed rail, is no substitute for a cost-benefit analysis, and makes no case specifically for intermediate stops[^S-bench-de-028].

**Direction and scope.** Within one corridor the result is positive for the counties with the stops, measured as GDP and accessibility. It is not a test of small-town population or employment outcomes, and it is not a finding that intermediate stops are worth their cost. No other German study of intermediate-station effects was found (searched: ICE stops and regional employment, 31 Oct 2026). The German evidence is therefore positive but single-corridor and unreplicated. It is neither mixed nor negative; it is thin.

## 9. Lessons for KSA (evidence-based, non-advocacy)

- The ECA names urban nodes, land scarcity, viaducts and long tunnels as the cost drivers on the most expensive German line[^S-bench-de-003]. The sources read do not decompose the cost per km, so the attribution is the ECA's and is not tested here.
- Two German sections were decided without a cost-benefit analysis at the time of the decision; a CBA was made later, ex post[^S-bench-de-013]. The ECA treats this as a governance point.
- Ex-post evaluation is missing for the VDE 8 lines: no route-level modal-shift survey, and no retrospective benefit estimate[^S-bench-de-041][^S-bench-de-042]. The evidence gap is the finding.
- The Berlin–Munich forecast comparison is favourable in direction but not like-for-like. A single corridor with a press-reported modal shift does not establish a general distance band.
- The ECA's ridership benchmark (nine million a year) and its door-to-door method are EU tools. They are not a KSA test.

## 10. Gaps: "no reliable data found" items

- **Density and city-size thresholds:** no reliable data found (searched: Bundestag, DB and academic terms, 31 Oct 2026).
- **Line-level farebox recovery and operating ratio:** no reliable data found (searched: DB Fernverkehr 2025 report, Bundestag answers, ECA, 31 Oct 2026). Segment figures are not a line ratio.
- **BVWP cost-benefit ratio (NKV) for Berlin–Munich or VDE 8:** no reliable data found. The bvwp-projekte.de index was read; the project dossiers were not reached (searched: bvwp-projekte.de and Bundestag, 31 Oct 2026).
- **Köln–Rhein/Main new line (opening year not verified in a source read):** no reliable cost found (searched: Bundestag and web, 31 Oct 2026). Old DM and euro figures seen in search results conflict and are not used.
- **Bundesrechnungshof primary reports:** the 2008 report is cited only as quoted in Drucksache 16/11066. No later BRH report on German high-speed lines was found on bundesrechnungshof.de in the search (31 Oct 2026).
- **Stuttgart 21 current cost and opening date:** unverified press only (sources 55 and 57). The DB press release and the railmarket page were not readable.
- **Wendlingen–Ulm final cost:** three conflicting figures (section 7).
- **Stuttgart 21 cost history:** the ECA's 6,526 m EUR equals the 2013 framework (section 7).
- **Deutschlandtakt target timetable (Zielfahrplan 2030):** located as a PDF, not opened.
- **Original 2006 forecast (Drucksache 16/1379):** not opened; cited through Drucksache 19/7577.
- **Ahlfeldt and Feddersen 2018 abstract:** the JEG page did not return the abstract; figures are from the 2015 working paper.
- **Price-year conversion:** not done in this file; generated in `README.md` with the single price index `cities/ksa/costs/index.yaml` (CP2 P2a, A-cost-002; it replaced `index-r1b.yaml` and A-bench-001).

## Escalations

1. **Conflicting Berlin–Munich ridership for 2018:** 4.9 million (Federal Government quoting DB AG[^S-bench-de-038]) against 4.4 million (press quoting DB[^S-bench-de-051]). Counting basis unknown. Both kept; coordinator to decide which the R1c reference class uses.
2. **Wendlingen–Ulm cost:** 3,259 m EUR (ECA audit[^S-bench-de-008]) against 3.7 bn EUR (Federal Government, 2018[^S-bench-de-035]) against "just under four billion" (state release, 2022[^S-bench-de-054]). Possibly different scopes or dates. Not resolved.
3. **Stuttgart 21 total:** the ECA figure (6,526 m EUR[^S-bench-de-007]) equals the 2013 framework[^S-bench-de-031]; the 2018 estimate is 8.2 bn EUR[^S-bench-de-034]; a faction statement gives about 11.5 bn EUR (grade C[^S-bench-de-036]); the press reports about 14.5 bn EUR (unverified[^S-bench-de-055]). Coordinator to decide the reference figure after a DB primary is read.
4. **DB punctuality:** 60.1 % (foreword[^S-bench-de-048]) against 65.5 % (Lagebericht "Reisendenpünktlichkeit"[^S-bench-de-047]). The definitions differ; not resolved.
5. **Ahlfeldt and Feddersen figures:** the 8.5 %[^S-bench-de-024], decay and elasticity figures are from the 2015 working-paper abstract. Re-verify against the 2018 JEG abstract before use in any output.
6. **Forecast comparability:** the ratio of 1.39 (section 3[^S-bench-de-038][^S-bench-de-040]) mixes a 2006 forecast with a 2018 DB statement. Flagged, not corrected.

## Sources

[^S-bench-de-001]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-002]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-003]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-004]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-005]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-006]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-007]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-008]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-009]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-010]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-011]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-012]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-013]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-014]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-015]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-016]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-017]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-018]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-019]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-020]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-021]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-022]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-023]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-024]: Ahlfeldt and Feddersen, "From periphery to core: measuring agglomeration effects using high-speed rail", LSE Research Online, https://researchonline.lse.ac.uk/id/eprint/64507, published 2015, accessed 2026-10-31.
[^S-bench-de-025]: Ahlfeldt and Feddersen, "From periphery to core: measuring agglomeration effects using high-speed rail", LSE Research Online, https://researchonline.lse.ac.uk/id/eprint/64507, published 2015, accessed 2026-10-31.
[^S-bench-de-026]: Ahlfeldt and Feddersen, "From periphery to core: measuring agglomeration effects using high-speed rail", LSE Research Online, https://researchonline.lse.ac.uk/id/eprint/64507, published 2015, accessed 2026-10-31.
[^S-bench-de-027]: Oxford University Press, Journal of Economic Geography, "From periphery to core: measuring agglomeration effects using high-speed rail", https://academic.oup.com/joeg/article/18/2/355/3778385, published 2018, accessed 2026-10-31.
[^S-bench-de-028]: UC Berkeley Goldman School of Public Policy, "Economic Impacts of HSR" presentation, panel 4 (Ahlfeldt), https://gsppi.berkeley.edu/programs/highspeedrail/2011pdfs/Panel%204_Economic%20Impacts%20of%20HSR/Panel%204_Ahlfeld.pdf, published 2011, accessed 2026-10-31.
[^S-bench-de-029]: Deutscher Bundestag, "Drucksache 16/11066", https://dserver.bundestag.de/btd/16/110/1611066.pdf, published 2008-11-25, accessed 2026-10-31.
[^S-bench-de-030]: Deutscher Bundestag, "Drucksache 16/11066", https://dserver.bundestag.de/btd/16/110/1611066.pdf, published 2008-11-25, accessed 2026-10-31.
[^S-bench-de-031]: Deutscher Bundestag, "Drucksache 18/1241, Kosten von Stuttgart 21", https://dserver.bundestag.de/btd/18/012/1801241.pdf, published 2014-04-25, accessed 2026-10-31.
[^S-bench-de-032]: Deutscher Bundestag, "Drucksache 18/1241, Kosten von Stuttgart 21", https://dserver.bundestag.de/btd/18/012/1801241.pdf, published 2014-04-25, accessed 2026-10-31.
[^S-bench-de-033]: Deutscher Bundestag, "Drucksache 18/1241, Kosten von Stuttgart 21", https://dserver.bundestag.de/btd/18/012/1801241.pdf, published 2014-04-25, accessed 2026-10-31.
[^S-bench-de-034]: Deutscher Bundestag, "Drucksache 19/1534, Offene Frage zu Stuttgart 21 und der Neubaustrecke Wendlingen – Ulm", https://dserver.bundestag.de/btd/19/015/1901534.pdf, published 2018-04-04, accessed 2026-10-31.
[^S-bench-de-035]: Deutscher Bundestag, "Drucksache 19/1534, Offene Frage zu Stuttgart 21 und der Neubaustrecke Wendlingen – Ulm", https://dserver.bundestag.de/btd/19/015/1901534.pdf, published 2018-04-04, accessed 2026-10-31.
[^S-bench-de-036]: Deutscher Bundestag, "Drucksache 21/4465, Antrag", https://dserver.bundestag.de/btd/21/044/2104465.pdf, published 2026-03-03, accessed 2026-10-31.
[^S-bench-de-037]: Deutscher Bundestag, "Drucksache 21/4465, Antrag", https://dserver.bundestag.de/btd/21/044/2104465.pdf, published 2026-03-03, accessed 2026-10-31.
[^S-bench-de-038]: Deutscher Bundestag, "Drucksache 19/7577, Verkehrliche Wirkungen des Verkehrsprojekts Deutsche Einheit Nr. 8 nach Gesamtinbetriebnahme im Dezember 2017", https://dserver.bundestag.de/btd/19/075/1907577.pdf, published 2019-02-07, accessed 2026-10-31.
[^S-bench-de-039]: Deutscher Bundestag, "Drucksache 19/7577, Verkehrliche Wirkungen des Verkehrsprojekts Deutsche Einheit Nr. 8 nach Gesamtinbetriebnahme im Dezember 2017", https://dserver.bundestag.de/btd/19/075/1907577.pdf, published 2019-02-07, accessed 2026-10-31.
[^S-bench-de-040]: Deutscher Bundestag, "Drucksache 19/7577, Verkehrliche Wirkungen des Verkehrsprojekts Deutsche Einheit Nr. 8 nach Gesamtinbetriebnahme im Dezember 2017", https://dserver.bundestag.de/btd/19/075/1907577.pdf, published 2019-02-07, accessed 2026-10-31.
[^S-bench-de-041]: Deutscher Bundestag, "Drucksache 19/7577, Verkehrliche Wirkungen des Verkehrsprojekts Deutsche Einheit Nr. 8 nach Gesamtinbetriebnahme im Dezember 2017", https://dserver.bundestag.de/btd/19/075/1907577.pdf, published 2019-02-07, accessed 2026-10-31.
[^S-bench-de-042]: Deutscher Bundestag, "Drucksache 19/7577, Verkehrliche Wirkungen des Verkehrsprojekts Deutsche Einheit Nr. 8 nach Gesamtinbetriebnahme im Dezember 2017", https://dserver.bundestag.de/btd/19/075/1907577.pdf, published 2019-02-07, accessed 2026-10-31.
[^S-bench-de-043]: Deutscher Bundestag, hib (Heute im Bundestag), "hib-Meldung on the government answer (Drucksache 21/838)", https://www.bundestag.de/presse/hib/kurzmeldungen-1102274, published 2025-07-17, accessed 2026-10-31.
[^S-bench-de-044]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-045]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-046]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-047]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-048]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-049]: L-IZ (Leipziger Internetzeitung), "Die Bahn hat ihre Fahrgastzahlen zwischen München und Berlin mehr als verdoppelt", https://www.l-iz.de/wirtschaft/mobilitaet/2018/12/Die-Bahn-hat-ihre-Fahrgastzahlen-zwischen-Muenchen-und-Berlin-mehr-als-verdoppelt-247632, published 2018-12-01, accessed 2026-10-31.
[^S-bench-de-050]: L-IZ (Leipziger Internetzeitung), "Die Bahn hat ihre Fahrgastzahlen zwischen München und Berlin mehr als verdoppelt", https://www.l-iz.de/wirtschaft/mobilitaet/2018/12/Die-Bahn-hat-ihre-Fahrgastzahlen-zwischen-Muenchen-und-Berlin-mehr-als-verdoppelt-247632, published 2018-12-01, accessed 2026-10-31.
[^S-bench-de-051]: L-IZ (Leipziger Internetzeitung), "Die Bahn hat ihre Fahrgastzahlen zwischen München und Berlin mehr als verdoppelt", https://www.l-iz.de/wirtschaft/mobilitaet/2018/12/Die-Bahn-hat-ihre-Fahrgastzahlen-zwischen-Muenchen-und-Berlin-mehr-als-verdoppelt-247632, published 2018-12-01, accessed 2026-10-31.
[^S-bench-de-052]: L-IZ (Leipziger Internetzeitung), "Die Bahn hat ihre Fahrgastzahlen zwischen München und Berlin mehr als verdoppelt", https://www.l-iz.de/wirtschaft/mobilitaet/2018/12/Die-Bahn-hat-ihre-Fahrgastzahlen-zwischen-Muenchen-und-Berlin-mehr-als-verdoppelt-247632, published 2018-12-01, accessed 2026-10-31.
[^S-bench-de-053]: Land Baden-Württemberg, "Neubaustrecke Wendlingen-Ulm eröffnet", https://www.baden-wuerttemberg.de/de/service/alle-meldungen/meldung/pid/neubaustrecke-wendlingen-ulm-eroeffnet, published 2022-12-09, accessed 2026-10-31.
[^S-bench-de-054]: Land Baden-Württemberg, "Neubaustrecke Wendlingen-Ulm eröffnet", https://www.baden-wuerttemberg.de/de/service/alle-meldungen/meldung/pid/neubaustrecke-wendlingen-ulm-eroeffnet, published 2022-12-09, accessed 2026-10-31.
[^S-bench-de-055]: Railmarket and other press (search result only; not read), https://railmarket.com/news/infrastructure/59295-stuttgart-21-costs-rise-to-eur14-5bn, published unknown (2026), accessed 2026-10-31. Status unverified.
[^S-bench-de-056]: Deutscher Bundestag answer quoting DB estimate of 2010 (search result only; not read), https://kleineanfragen.de/bundestag/18/2239-sachstand-neubaustrecke-wendlingen-ulm.pdf, published unknown, accessed 2026-10-31. Status unverified.
[^S-bench-de-057]: Stuttgarter Zeitung (search result only; not read), https://www.stuttgarter-zeitung.de/inhalt.stuttgart-21-bahn-bestaetigt-start-von-s21-verschiebt-sich-auf-ende-2031.24f94a48-c22c-4540-ad5a-546e144fa3d3.html, published unknown (2026), accessed 2026-10-31. Status unverified.
[^S-bench-de-058]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-059]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-060]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-061]: DB Fernverkehr AG, "Geschäftsbericht 2025", https://ir.deutschebahn.com/fileadmin/Deutsch/2026/Toechter_2025/DB25_Fernverkehr_web.pdf, published 2026, accessed 2026-10-31.
[^S-bench-de-062]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-063]: Deutscher Bundestag, "Drucksache 21/4465, Antrag", https://dserver.bundestag.de/btd/21/044/2104465.pdf, published 2026-03-03, accessed 2026-10-31.
[^S-bench-de-064]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31.
[^S-bench-de-065]: Deutscher Bundestag, "Drucksache 19/7577, Verkehrliche Wirkungen des Verkehrsprojekts Deutsche Einheit Nr. 8 nach Gesamtinbetriebnahme im Dezember 2017", https://dserver.bundestag.de/btd/19/075/1907577.pdf, published 2019-02-07, accessed 2026-10-31.
