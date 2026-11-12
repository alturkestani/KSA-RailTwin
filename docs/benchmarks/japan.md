> **Document version:** docs/benchmarks/japan.md v0.2 | 31 Oct 2026 | Author: benchmarks-researcher; index pointer by CP2_PREP | Status: draft

# Japan: Shinkansen (JR Central, JR East, JR West, JR Kyushu; JRTT for seibi shinkansen)

Scope and method. Research from open sources on 31 Oct 2026. Figures are in the currency and price basis of each source; nothing has been converted to SAR. Metric rows: `cities/ksa/benchmarks/metrics-japan.csv` (41 rows). Overrun candidates: `cities/ksa/benchmarks/overruns-japan.csv` (6 rows). Citation records: `docs/sources/bench-japan.csv` (19 records). Most primary figures are grade A (operator reports and notices, MLIT documents, a prefectural report). Peer-reviewed evidence is one journal article read from its abstract only. The ex-post ridership-versus-forecast evidence that the brief asked for was **not found in open sources**; section 3 says so and lists the searches.

Corrections to the brief's leads. (1) The intermediate-station study the brief attributes to "Bernard, Moriya et al." (CEPR DP15771) is not supported by the sources read. DP15771 is by Hayakawa, Koster, Tabuchi and Thisse[^S-bench-jp-012]. The intermediate-municipality finding is by Koster, Tabuchi and Thisse[^S-bench-jp-011]. (2) CEPR pages and PDFs returned HTTP 403 on every attempt, so the RIETI working-paper copy was used[^S-bench-jp-019]. (3) The Chuo Shinkansen total is 11.0 trillion yen in JR Central's own notice[^S-bench-jp-003]; a press figure of about 9 trillion yen was not used.

## 1. System facts

| metric | value | unit | price year | grade | source |
|---|---|---|---|---|---|
| Tokaido Shinkansen (first line) construction completed | 1964 | year | n/a | C | [^S-bench-jp-012] |
| Tokaido Shinkansen passengers, FY2024 (all train types) | 460,000 | passengers per day | n/a | A | [^S-bench-jp-005] |
| Tokaido Shinkansen train services, FY2024 (incl. extras) | 383 | services per day | n/a | A | [^S-bench-jp-005] |
| Tokyo–Shin-Osaka, fastest trains (March 2025 timetable) | 2 h 21 min | time | n/a | A | [^S-bench-jp-005] |
| Chuo Shinkansen Shinagawa–Nagoya, line extension (under construction; not operating) | 285.6 | km | n/a | A | [^S-bench-jp-004] |
| Hokkaido Shinkansen Shin-Hakodate–Sapporo (under construction) | 211 | km | not stated | A | [^S-bench-jp-002] |
| Hokuriku Shinkansen Kanazawa–Tsuruga (opened; date from secondary source) | 113 (MLIT appraisal document); about 125 (secondary) | km | n/a | A / D | [^S-bench-jp-002][^S-bench-jp-015] |
| Hokuriku Kanazawa–Tsuruga opening | 16 March 2024 | date | n/a | D (secondary) | [^S-bench-jp-015] |
| Construction body for the seibi shinkansen | JRTT (Japan Railway Construction, Transport and Technology Agency) | text | n/a | A | [^S-bench-jp-007] |
| Operator, Tokaido Shinkansen | JR Central | text | n/a | A | [^S-bench-jp-005] |

Operators and infrastructure. Lines are built by JRTT, a state agency, and operated by the JR companies. The brief names JR East, JR West and JR Kyushu. Their operating and ridership reports were not opened in this run, so their own figures are absent (section 10). Chuo Shinkansen is being built by JR Central, which funds it mainly from operating cash flow and borrowing[^S-bench-jp-003].

Delivery and funding. For Chuo Shinkansen, JR Central states that it will "fund the construction costs mainly through operating cash flow and the remaining amount through financing", and that about 2.4 trillion yen of new financing would be needed to cover construction costs on its 2035 calculation[^S-bench-jp-003]. For the seibi shinkansen, MLIT states that JRTT is the construction body for Kanazawa–Tsuruga[^S-bench-jp-007]. The state-and-local cost-sharing rules were not read in this run. Fukui Prefecture's 2019 report asks the government for national funding to cover the cost increase[^S-bench-jp-008]. The sources read do not describe a full funding model.

## 2. Cost per km

Nominal values as printed. No source opened gives a price-year base for the MLIT construction-cost figures, and the year is recorded as "not stated". Adjusted SAR 2025 values: not converted in this dossier. The price-index factors are in `cities/ksa/costs/index.yaml` (series `I-price-jpy` and `I-fx-jpy-usd`; the single index since CP2 P2a, which replaced `index-r1b.yaml`); the conversion is run by the coordinator's `summarise` step after merge. Per-km rows are computed from two printed values and are marked "computed" in the metrics file.

| line or section | length (km) | total (m JPY) | m JPY per km (computed) | price basis | grade | source |
|---|---|---|---|---|---|---|
| Chuo, 2025 forecast total (includes rolling stock) | 285.6 | 11,000,000 | 38,515 | 2025 forecast, nominal | A | [^S-bench-jp-003][^S-bench-jp-004] |
| Chuo, CIP #1 and #2 initial estimate (civil and electrical; excludes rolling stock) | 285.6 | 5,520,000 | 19,328 | 2014–2018 approvals, nominal (inferred) | A | [^S-bench-jp-003][^S-bench-jp-004] |
| Chuo, Dec 2023 approved budget (CIP #3) | 285.6 | 7,048,200 | 24,679 | Dec 2023 approval, nominal (inferred) | A | [^S-bench-jp-004] |
| Hokkaido, Shin-Hakodate–Sapporo, MLIT construction cost (工事費) | 211 | 1,670,000 | 7,915 | not stated; document undated | A | [^S-bench-jp-002] |
| Hokuriku, Kanazawa–Tsuruga, MLIT total construction cost (総工事費) | 113 | 1,130,000 | 10,000 | not stated; document undated | A | [^S-bench-jp-002] |

Range across these rows: about 7,900 to 38,500 m JPY per km (computed). The spread is wide because the rows differ in scope (construction cost only, with or without rolling stock), in price basis, and in technology: the Chuo line is a maglev, mostly in tunnels, and is not a wheel-rail benchmark for a conventional HSR line. The Hokuriku per-km value depends on a length (113 km) that conflicts with the roughly 125 km in secondary sources[^S-bench-jp-015]; it is not secure.

Cross-check on the Chuo length. The 285.6 km figure is printed in JR Central's annual report[^S-bench-jp-004]. Its cost is printed in the notice[^S-bench-jp-003].

Press figure, not used for per-km: the Hokkaido headline total of 3.5 trillion yen, read on a Hokkaido Shimbun page, is an upper bound with a different scope from the 1.67 trillion yen construction cost[^S-bench-jp-010]. It is reported in section 7 only.

## 3. Ridership against forecast

No reliable outturn-versus-forecast pair for a Japanese Shinkansen line was found in open sources. Searched on 31 Oct 2026: JR Central annual reports 2025 and IR decks (Feb 2026); MLIT appraisal documents; Hokuriku and Tohoku ex-post evaluation terms in Japanese (事後評価, 需要予測, 利用者数); WCTR 2013 ex-post paper (abstract only; not opened)[^S-bench-jp-017]. The JRTT ex-post evaluation reports (事後評価報告書) for the Hokuriku Takasaki–Nagano and Tohoku Hachinohe–Shin-Aomori sections were not reached. A secondary document seen only in search results (not opened) reports a rise in use after the Takasaki–Nagano opening; its forecast comparison is not in the excerpt, so no figure is entered. **No reliable data found for ridership_vs_forecast.**

What the opened sources do give:

- Ex-ante forecasts, not outturns. The MLIT appraisal document gives forecast rail-user multiples by section (for example about 2.9 times for the Hokkaido Shin-Hakodate–Sapporo corridor, and about 1.1 to 1.3 times for Hokuriku corridors) as printed in its tables[^S-bench-jp-002]. These are forecast multiples and cannot be compared with outturns without the ex-post report.
- Recent operating trend. JR Central's Feb 2026 deck reports Tokaido passenger volume in the third quarter of FY2026.3 at 107% of FY2024 levels[^S-bench-jp-006]. This is a trend against the prior year, not against a forecast.
- Level. Tokaido carried an average of 460,000 passengers per day in FY2024[^S-bench-jp-005].

## 4. Farebox recovery / operating ratio

**No reliable data found** (searched: JR Central annual report 2025 (Shinkansen and Chuo sections), JR Central IR deck, 3Q FY2026.3, 2 Feb 2026; the JR East and JR West reports were not reached, 31 Oct 2026). The JR Central pages opened give no Tokaido Shinkansen operating ratio or farebox recovery. The Chuo Shinkansen notice says the line's operating cash flow is what funds construction, but gives no ratio[^S-bench-jp-003]. Do not infer a farebox figure from these sources.

## 5. Thresholds: density, city size, and the 200–800 km band

Density and city-size thresholds: **no reliable data found** (searched: MLIT trunk passenger flow survey (2000 release, read); RIETI DP 21-E-003; RIETI DP 22-E-060 (abstract)). No density or city-size cut-off for Shinkansen service was in the opened sources.

Rail share by distance (the test of the 200–800 km band). The MLIT survey for autumn 2000 (weekday) gives the representative mode for each trip distance band. Values are the printed bar labels[^S-bench-jp-001]:

| distance band | car | rail | air | grade | source |
|---|---|---|---|---|---|
| 100–200 km | 81.1% | 16.7% | not read | A | [^S-bench-jp-001] |
| 200–300 km | 74.6% | 22.2% | not read | A | [^S-bench-jp-001] |
| 300–500 km | 45.8% | 46.8% | 4.5% | A | [^S-bench-jp-001] |
| 500–700 km | 15.1% | 66.8% | 15.4% | A | [^S-bench-jp-001] |
| 700–1,000 km | 12.3% | 29.6% | 54.1% | A | [^S-bench-jp-001] |
| 1,000 km and over | not legibly labelled | 8.1% | 87.0% | A | [^S-bench-jp-001] |

The survey text itself states the same pattern: cars for trips under 300 km, rail for 300 to 700 km, and air for trips over 700 km[^S-bench-jp-001]. Across all trips in 2000, the shares were 68.7% car, 22.0% rail and 7.1% air[^S-bench-jp-001].

A 2010 pair is cited in the RIETI paper from MLIT 2019, not from the MLIT table: rail share of 43.7% for 300–500 km and "almost 70%" for 500–700 km[^S-bench-jp-012]. The MLIT 2019 table was not opened, so these are secondary (grade C).

Reading against the 200–800 km hypothesis:

- For: in this Japanese data, rail carries the largest share in the 300–700 km bands in both the 2000 survey and the 2010 secondary citation. Air takes the majority only beyond about 700 km.
- Against or complicating: car still carries 45.8% at 300–500 km (2000) and 15.1% at 500–700 km; the rail share at 300–500 km is only slightly above car. The band is a property of one country's network, fares, and 2000 car ownership, not a general law. The survey is descriptive: it does not test what would have happened without a line.
- Not tested: travel-time competitiveness in KSA. Japanese shares are not KSA shares.

The band is therefore a hypothesis that the Japanese descriptive shares are consistent with, not a result.

## 6. Station spacing, timetable and stopping patterns

Stopping pattern (Tokaido, FY2024 and March 2025 timetable): Nozomi stops at Shinagawa, Shin-Yokohama, Nagoya and Kyoto; Hikari stops at the Nozomi stations plus a few more; Kodama stops at all stations[^S-bench-jp-005]. Fastest trains take 2 h 21 min Tokyo to Shin-Osaka[^S-bench-jp-005]. The operator reports 383 services per day including extras[^S-bench-jp-005]. The JR Central annual report gives Tokyo (Shinagawa)–Nagoya at 86 minutes now and 40 minutes with the Chuo line, a planned figure[^S-bench-jp-004].

Station spacing: **No reliable data found** (searched: JR Central annual report 2025; JR East timetable site (search results only); no distance table opened, 31 Oct 2026). The RIETI paper records that the 1940 initial plan selected 18 municipalities for stations and that five more in-between stations were added after the 1964 opening, but gives no spacing[^S-bench-jp-012].

## 7. Overruns (cost, schedule) and renegotiations

Cost, Chuo Shinkansen (Shinagawa–Nagoya). The estimate has been raised three times in the sources read. Initial 5.52 trillion yen (CIP #1 and #2, 2014–2018) rose to 7.04 trillion yen (announced April 2021, approved Dec 2023) and is now 11.0 trillion yen (notice of 29 Oct 2025, about 4 trillion yen more)[^S-bench-jp-003][^S-bench-jp-004]. Computed: 11.0 over 5.52 is about +99%, and 11.0 over 7.048 is about +56%[^S-bench-jp-003][^S-bench-jp-004]. The notice attributes the rise to "price surges, responses to challenging construction work, and enhanced specifications"[^S-bench-jp-003]. The first estimate excludes rolling stock and the 2025 total includes it, so the first ratio mixes scope.

Schedule, Chuo Shinkansen. The annual report's project table gives "On or after 2027" for completion in its December 2023 approval table[^S-bench-jp-004]. The October 2025 notice provisionally sets opening at 2035 "solely for calculation purposes"[^S-bench-jp-003]. A press report gives 2034 as the earliest possible opening, from a JR Central statement of March 2024 (not opened)[^S-bench-jp-016]. Treat 2035 as a financing assumption and the 2034 date as unverified.

Cost, Hokuriku Kanazawa–Tsuruga. Fukui Prefecture reported in January 2019 an expected increase of 2,263 億円 and a planned Tsuruga opening at the end of FY2022[^S-bench-jp-008]. A press report of the MLIT approval on 31 March 2021 gives a further increase of 2,658 億円 and a one-year delay to the end of FY2023[^S-bench-jp-009]. The primary MLIT approval was not opened. A total construction cost of 11,300 億円 is printed in the MLIT appraisal document, but that document predates the increases, and its section and length need the caveat in section 2[^S-bench-jp-002]. Not computed as a percentage, because the baseline total at approval was not verified. The opening on 16 March 2024 is secondary (Wikipedia)[^S-bench-jp-015].

Cost and schedule, Hokkaido Shinkansen (Shin-Hakodate–Sapporo). The MLIT document prints a construction cost of 16,700 億円 for the 211 km section, undated[^S-bench-jp-002]. In December 2025 JRTT presented a trial estimate that cost could rise by up to 1.2 trillion yen, with the MLIT review panel keeping the opening at the end of FY2038 or later, and a headline gives a total of 3.5 trillion yen[^S-bench-jp-010]. The headline total has a different scope, so the ratio of about 2.1 is an upper bound, not a like-for-like overrun. The earlier target of the end of FY2030 is seen only in a press snippet (unverified)[^S-bench-jp-014]. The 8-year difference is recorded as "to verify".

Renegotiations. The sources describe the Hokkaido and Chuo changes as set by approval and review processes (panels, the MLIT approval of construction plans, a financing review). No renegotiation of a concession is described.

Ridership overruns: none found (see section 3).

Candidate observations are in `overruns-japan.csv` (6 rows). R1b sets no uplift.

## 8. Small-town evidence: did intermediate stations gain?

Summary. The evidence on in-between municipalities is mixed to negative in the peer-reviewed work read, and positive for connected places in simulation. No ex-post station-level ridership or economic study of an intermediate Shinkansen stop was found.

- **Koster, Tabuchi and Thisse (2022), Journal of Economic Geography 22(4): 711–753 (DOI 10.1093/jeg/lbab042).** Peer-reviewed, Grade B. Read from the abstract only; the article is paywalled. Finding: "'in-between' municipalities that are connected to the Shinkansen witness a sizable decrease in employment"[^S-bench-jp-011]. The abstract gives no percentage. The effect size (about 10 to 40%) appears only in a VoxEU column that could not be opened (HTTP 403) and in a search summary[^S-bench-jp-018]; it is unverified and is not used as a figure. Method: spatial general-equilibrium model with long-haul economies, estimated on Shinkansen data.
- **Hayakawa, Koster, Tabuchi and Thisse (2021), RIETI DP 21-E-003 (CEPR DP15771 counterpart).** Working paper, not peer-reviewed in this version, Grade C. Method: spatial quantitative general equilibrium with counterfactuals. Finding: network extensions "may have large effects (up to a 30% increase in employment)" on connected municipalities, "although the effects are smaller for places with higher fixed costs", and a welfare gain of about 5%[^S-bench-jp-012]. This is a model counterfactual, not an observed outcome. The paper's reduced-form section finds that opening a Shinkansen station has a positive effect on population and employment (Appendix B, within 25 km of a station)[^S-bench-jp-012].
- **Yoo, Kumagai, Kawasaki, Hong, Zhang, Shimamura and Managi (2022), RIETI DP 22-E-060.** Working paper, Grade C. Method: market-access regression on 1983–2020 Shinkansen data with IV checks. Finding: "most of the benefits are focused in Tokyo and other developed areas", and growth in cities outside these areas is "negative or statistically insignificant"[^S-bench-jp-013]. This is a negative result for non-metropolitan places, but it is about HSR market access, not about stops.
- **Cited, not opened:** Ahlfeldt and Feddersen (2018) report an 8:5% rise in GDP in three German counties with intermediate stops, and Qin (2013) reports falls in GDP per capita for non-urban Chinese counties on upgraded lines. Both are cited in the RIETI paper's literature review (printed as "8:5%" in the PDF text layer)[^S-bench-jp-012]. Grade C (secondary citation). The German study belongs to the Germany dossier.

Plain statement. The one peer-reviewed Japanese study read is negative for in-between municipalities. Model and working-paper results are positive for connected places on average, with smaller gains where fixed costs are high. The working paper on market access is negative or null outside the largest areas. None of these is an ex-post study of the intermediate-stop ridership that the brief asked for. Evidence is mixed, and the negative direction is from one peer-reviewed abstract. The paper's full text would be needed before any finding is quoted as an effect size.

Historic note. The RIETI paper says the 1940 initial plan selected 18 municipalities for stations, and that five more in-between stations were added after the 1964 opening[^S-bench-jp-012]. No study of those added stops was found.

## 9. Lessons for KSA (evidence-based, non-advocacy)

These are what the sources report, not recommendations.

- Cost estimates for Japanese Shinkansen projects have risen between approval stages. The largest rises in the opened sources are on the maglev (about double the initial estimate) and on the Hokkaido section (a press upper bound of about double the MLIT construction cost)[^S-bench-jp-003][^S-bench-jp-010]. Both sources attribute part of the increase to prices and to construction difficulty.
- Opening dates have moved by years. The Hokuriku section moved by one year at a 2021 approval, and the Hokkaido and Chuo dates have moved to the 2030s[^S-bench-jp-009][^S-bench-jp-010][^S-bench-jp-003].
- Mode share by distance in Japan (2000) shows rail carrying the largest share in the 300–700 km bands, with air dominating beyond about 700 km[^S-bench-jp-001]. This is descriptive for Japan and says nothing about KSA demand.
- The peer-reviewed evidence on intermediate places is mixed to negative (one abstract read). Any KSA intermediate-station case needs its own test, not a transfer of this result.

## 10. Gaps: "no reliable data found" items

- Ridership against forecast (ex-post): **no reliable data found** (searched 31 Oct 2026: JRTT ex-post reports (事後評価) for Hokuriku Takasaki–Nagano and Tohoku Hachinohe–Shin-Aomori via search terms only; JR Central and JR East IR decks; MLIT). The JRTT reports on the MLIT and JRTT sites are the primary to find.
- Farebox recovery and operating ratio: **no reliable data found** (JR East and JR West reports not reached; JR Central gives company-level figures only).
- Density and city-size thresholds: **no reliable data found** (no threshold in the sources read).
- Station spacing: **no reliable data found** (no distance table opened).
- Price-year conversion to SAR 2025: **not converted** in this dossier.
- Hokuriku Kanazawa–Tsuruga length: **conflict** (113 km in MLIT appraisal vs about 125 km in secondary sources). Unresolved.
- Chuo Shinkansen 2034 vs 2035: the press 2034 is unverified (D). The notice's 2035 is a calculation assumption.
- Primary documents not opened: MLIT 2015 trunk survey (the 2019 table cited by RIETI); MLIT and JRTT cost-approval documents for Hokuriku (2021) and Hokkaido (2025); JRTT ex-post evaluations; CEPR DP15771 and DP15905 (HTTP 403); VoxEU column (HTTP 403); Imai, Kariyazaki and Saiki (WCTR 2013, full text); the JEG article (paywalled, abstract only).
- Operator reports for JR East, JR West and JR Kyushu: not reached.

## Escalations

1. **Lead attribution.** The brief's lead "Bernard, Moriya et al." (CEPR DP15771 and the intermediate-station column) is not supported. The sources read give DP15771 as Hayakawa, Koster, Tabuchi and Thisse[^S-bench-jp-012], and the intermediate-municipality finding as Koster, Tabuchi and Thisse[^S-bench-jp-011]. Coordinator to confirm whether a separate "Bernard" paper exists before the small-towns file cites it.
2. **Hokuriku length conflict.** MLIT appraisal: 113 km (Kanazawa–Tsuruga)[^S-bench-jp-002]; secondary: about 125 km[^S-bench-jp-015]. Per-km value not secure. Needs the JRTT length.
3. **Hokkaido total cost.** The 3.5 trillion yen headline (press upper bound)[^S-bench-jp-010] and the 1.67 trillion yen MLIT construction cost[^S-bench-jp-002] are different scopes. A like-for-like overrun needs the JRTT estimate.
4. **Hokuriku cost increase.** Two figures (2,263 億円 expected in 2019[^S-bench-jp-008]; 2,658 億円 approved in 2021[^S-bench-jp-009]) are not reconciled; the 2021 approval was not opened.
5. **Ex-post ridership.** No reliable forecast-versus-outturn pair found. The JRTT ex-post reports are the decisive source, and they need a Japanese-language pull. Coordinator to decide whether to commission it.
6. **Price-year conversion.** Adjusted SAR values need the `summarise` step with the JPN series; the MLIT figures have no stated price year, so their adjusted cells would rest on an inferred year and should be flagged.

## Sources

[^S-bench-jp-001]: Ministry of Land, Infrastructure, Transport and Tourism (MLIT), "Analysis examples from the National Trunk Passenger Flow Survey (data: autumn 2000 weekday)", https://www.mlit.go.jp/kisha/kisha03/15/150306/150306.pdf, published 2015-03-06 (file date), accessed 2026-10-31.
[^S-bench-jp-002]: MLIT Railway Bureau, "整備新幹線（未着工区間）の整備効果等について ―投資効果及び収支採算性の計算結果― (資料4)", https://www.mlit.go.jp/common/000204608.pdf, published undated, accessed 2026-10-31.
[^S-bench-jp-003]: Central Japan Railway Company (JR Central), "Notice Concerning Total Construction Costs for the Chuo Shinkansen Section between Shinagawa and Nagoya", https://global.jr-central.co.jp/en/news/_pdf/2025/0008.pdf, published 2025-10-29, accessed 2026-10-31.
[^S-bench-jp-004]: JR Central, "Annual Report 2025 (Chuo Shinkansen section)", https://global.jr-central.co.jp/en/company/ir/annualreport/_pdf/annualreport2025-12.pdf, published 2025, accessed 2026-10-31.
[^S-bench-jp-005]: JR Central, "Annual Report 2025 (Tokaido Shinkansen: frequent and high capacity)", https://global.jr-central.co.jp/en/company/ir/annualreport/_pdf/annualreport2025-13.pdf, published 2025, accessed 2026-10-31.
[^S-bench-jp-006]: JR Central, "3rd Quarter Investor Meeting FY2026.3", https://global.jr-central.co.jp/en/company/ir/investor-meeting/2026/_pdf/im_2026_06.pdf, published 2026-02-02, accessed 2026-10-31.
[^S-bench-jp-007]: MLIT Railway Bureau, "第13回 金沢・敦賀間工程・事業費管理連絡会議の開催について", https://www.mlit.go.jp/report/press/content/001724871.pdf, published 2024-02-21, accessed 2026-10-31.
[^S-bench-jp-008]: Fukui Prefecture, "北陸新幹線レポート 第6号", https://www.pref.fukui.lg.jp/doc/shinkansen/report_d/fil/number6.pdf, published 2019-01-31, accessed 2026-10-31.
[^S-bench-jp-009]: Norimono News (trafficnews.jp), "北陸新幹線の敦賀開業「2023年度末」に 1年延期 2658億円増で計画変更認可", https://trafficnews.jp/post/106079, published 2021-03-31, accessed 2026-10-31.
[^S-bench-jp-010]: Hokkaido Shimbun, "北海道新幹線事業費、縮減策検証へ 1.2兆円上振れ受け 工期は議論せず", https://www.hokkaido-np.co.jp/article/1257622/, published 2025-12-26, accessed 2026-10-31.
[^S-bench-jp-011]: Koster, H.R.A., Tabuchi, T. and Thisse, J.-F., "To be connected or not to be connected? The role of long-haul economies", Journal of Economic Geography 22(4): 711–753, https://research.vu.nl/en/publications/to-be-connected-or-not-to-be-connected-the-role-of-long-haul-econ/, published 2022-07, accessed 2026-10-31.
[^S-bench-jp-012]: Hayakawa, K., Koster, H.R.A., Tabuchi, T. and Thisse, J.-F., "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", RIETI Discussion Paper 21-E-003, https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.
[^S-bench-jp-013]: Yoo, S., Kumagai, J., Kawasaki, K., Hong, S., Zhang, B., Shimamura, T. and Managi, S., "Double-Edged Trains: Economic Outcomes and Regional Disparity of High-Speed Railways", RIETI Discussion Paper 22-E-060, https://www.rieti.go.jp/jp/publications/dp/22e060.pdf, published 2022-06, accessed 2026-10-31.
[^S-bench-jp-014]: Jiji Press (via nippon.com), "Hokkaido Shinkansen Extension to Be Delayed until End of FY '38", https://nippon.com/en/news/yjj2025031000648, published 2025-03-10, accessed 2026-10-31 (search-result title only; unverified).
[^S-bench-jp-015]: Wikipedia, "Hokuriku Shinkansen", https://en.wikipedia.org/wiki/Hokuriku_Shinkansen, published undated, accessed 2026-10-31 (search-result summary only; secondary).
[^S-bench-jp-016]: Gleisbau-welt, "Delay of the Chuo Shinkansen maglev railway until 2034", https://www.gleisbau-welt.de/en/news/asia/delay-of-the-chuo-shinkansen-maglev-railway-until-2034, published 2024-03-29, accessed 2026-10-31 (search-result summary only; unverified).
[^S-bench-jp-017]: Imai, Kariyazaki and Saiki, WCTR 2013 abstract, "Ex-post evaluation of Tohoku and Kyushu Shinkansen", https://wctrs-society.com/wp-content/uploads/abstracts/rio/general/1336.pdf, published 2013, accessed 2026-10-31 (not opened).
[^S-bench-jp-018]: VoxEU/CEPR, "High speed rail may hurt intermediate places", https://voxeu.org/article/high-speed-rail-may-hurt-intermediate-places, published unknown, accessed 2026-10-31 (HTTP 403; search summary only; unverified).
[^S-bench-jp-019]: CEPR, discussion papers DP15771 and DP15905, https://cepr.org/publications/dp15905, published unknown, accessed 2026-10-31 (HTTP 403 on all CEPR URLs tried; not opened).
