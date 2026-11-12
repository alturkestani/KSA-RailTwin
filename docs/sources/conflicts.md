> **Document version:** docs/sources/conflicts.md v0.14 | 6 Nov 2026 | Author: FIX_HHR_REROUTE (C-fixhhr-001 dated note, left open); FIX_HHR_JEDDAH (C-fixhhr-001); R5 (C-r4-intl-002 closed, H5); R4 (C-r4-tga-001…010, C-r4-intl-001…003); INTEGRATE_R3 (C-r3-001…003, TGA vs GASTAT rail and bus); R2 (C-gastat-003/004 resolved, C-r2-001/002); rail-data-scout (DATASCOUT_1H); C-010/C-011 resolved and C-cp2-601…603 by CP2_PREP (item 1 addendum); C-gastat-001…005 and C-cp2-601/602 causes by CP2_PREP (item 1 addendum 2); C-001 resolution by coordinator (LANDBRIDGE_RECONCILE); C-r1a-* by R1a builder and rail-data-scout (R1a); C-geo-* by GEO_VERIFY; R1c proposals recorded by INTEGRATE_R1; model id removed and C-r1a-22 HHR decomposition by CP2_PREP | Status: draft

# Source conflicts

One entry per pair or set of figures that disagree. Nothing is averaged and no figure is picked silently (`source-citation` skill). Ids refer to `docs/sources/index.csv`. Text labelled **analysis** is our reading, not a sourced fact. All arithmetic was run in Python on 2026-10-30, with the SAR/USD peg of 3.75 (assumption `A-cost-001`, `docs/assumptions.md`).

## C-001 Saudi Landbridge cost: SR 100 bn (USD 26.6 bn) vs USD 7 bn — status: **resolved as different vintages and scopes (analysis, medium confidence); price year still open**. Full reconciliation: `docs/costs-landbridge.md`

**Figure 1: SR 100 bn ≈ USD 26.6 bn.** Attributed to SAR's CEO, Bashar Al-Malik, by MEED on 21 Jan 2026 (S-046), 12 Feb 2026 and 31 Aug 2026 (S-047; MEED adds that the figure is the whole Landbridge, "not only the Riyadh section"), and by Construction Review on 19 Feb 2026 (S-048). Scope: the whole programme. Price year: not stated. Currency: SAR, with USD as the outlet's conversion. The CEO's original interview was not found, so all four rows are `secondary`.

**Figure 2: USD 7 bn.** ENR, "Saudi Arabia moves forward on $7B rail Landbridge project" (S-049). The page returned HTTP 403 on 30 Oct 2026; only a search snippet was read: "at a total cost of $7 billion, although the entire project is seen as requiring an investment of $26.6 billion". Status `unverified`. The publication date (June 2026 per the brief) is not confirmed. The same USD 7 bn appears as:
- a whole-project estimate in 2011 ("more than SR26 billion ($7 billion)", S-052; "up to USD 7 billion", S-053);
- a whole-project estimate in March 2021, attributed to the Minister of Transport (S-051);
- the value of the 35 km Riyadh section design-and-build package, in one outlet only (Construction Review, 19 Feb and 31 Aug 2026; S-050). MEED's two articles on the same tender give no package value.

**Arithmetic** (Python, 30 Oct 2026; peg 3.75 SAR/USD):

| quantity | value |
|---|---|
| SR 100 bn ÷ 3.75 | USD 26.67 bn (outlets print 26.6, a truncation) |
| USD 7 bn × 3.75 | SR 26.25 bn = **26 %** of SR 100 bn (26.25 %) |
| 2011 figure SR 26 bn ÷ 3.75 | USD 6.93 bn (consistent with "USD 7 bn") |
| SR 100 bn ÷ SR 26 bn | 3.85 × |
| USD 26.67 bn ÷ ~950 km (Riyadh–Jeddah line, S-055) | USD 28.07 m/km |
| USD 26.67 bn ÷ 900 km (MEED length, S-054) | USD 29.63 m/km |
| USD 26.67 bn ÷ 1,500 km ("more than 1,500 km of new track", S-057) | USD 17.78 m/km (upper bound, as track exceeds 1,500 km) |
| USD 7 bn ÷ ~950 km | USD 7.37 m/km |
| USD 7 bn ÷ 900 km | USD 7.78 m/km |
| USD 7 bn ÷ 1,500 km | USD 4.67 m/km |
| USD 7 bn ÷ 35 km (Riyadh section, S-060) | USD 200 m/km |

Per-km figures divide nominal totals of unknown price year by route or track length. They are not cost estimates; the cost register (W3) normalises them.

**Hypotheses:**
- **(a) USD 7 bn is the first phase.** No evidence. Every source that gives USD 7 bn describes it as the whole project, as an investment floor, or (one outlet) as the Riyadh package. None calls it a phase.
- **(b) USD 7 bn is a single package (civil works or systems).** Weak evidence: one secondary outlet (S-050) assigns USD 7 bn to the 35 km Riyadh design-and-build package (civil works, viaducts, utilities, signalling). It is uncorroborated: MEED gives no package value and no SAR tender or award notice was found. **Analysis:** at USD 200 m/km this would be in metro or urban-viaduct territory, possible for a dense Riyadh section but unusual for a mixed freight/passenger line. Treat as unconfirmed.
- **(c) A different price year or a legacy estimate.** Supported (best-supported reading). USD 7 bn / SR 26 bn is the 2011 whole-project estimate (S-052, S-053), repeated in 2021 (S-051) and in October 2025 press. The 2011 and 2021 scope was described as ~950 km Riyadh–Jeddah plus a Dammam–Jubail link (S-055); the 2026 programme is "more than 1,500 km of new track" (S-057). Neither figure states a price year. **Analysis:** ENR's "$7B" headline most likely reuses the legacy estimate while its own text gives USD 26.6 bn for the entire project. The 3.85× rise would then combine scope growth, 15 years of cost escalation and the shift from a PPP to phased state delivery. None of these components has been quantified.
  - A second search (coordinator, 30 Oct 2026) returned an index summary of the same ENR page. It describes "a $7 billion, roughly 1,500 km freight and passenger network" with a 950 km Jeddah–Riyadh line that "will not offer high-speed service", and mentions that the Jubail–Dammam section was inaugurated in April 2024. This is `unverified` (a search-index summary of a 403 page, not the text). If accurate, ENR applies the legacy USD 7 bn to today's ~1,500 km scope. The article date is then on or after April 2024, but June 2026 is still unconfirmed.
- **(d) A reporting error.** Possible, unproven. The snippet calls USD 7 bn the "total cost" while saying the entire project requires USD 26.6 bn, which is internally inconsistent unless "total cost" refers to a defined first scope. No correction was found.

**Reading (analysis):** use SR 100 bn (USD 26.67 bn, price year unknown) as the current whole-programme figure attributed to SAR's CEO. Keep USD 7 bn as a 2011 legacy estimate on a smaller scope. Neither enters the cost register as a point value; W3 records both as data points with scope and status.

**Next step:** the `LANDBRIDGE_RECONCILE` run (the coordinator) should (1) read the ENR article in full through a non-403 route and confirm its date, byline and the scope of "$7 billion"; (2) find SAR's tender or award notice for the Riyadh Rail Link with a value; (3) find the CEO's original interview (local Arabic media) for SR 100 bn, ideally with a price year; (4) read Railway Gazette International, 11 Oct 2011 for the legacy scope.

**Related:**
- **MEED Projects pid=114639** (https://meedprojects.com/project/114639/, S-061). The page is behind a subscriber gate and shows a template with no station list, so it was not read (`unverified`).
- **Al-Jumum as "Jamuma".** One trade site names Landbridge stations "Jumoum, Muwai and Dawadmi" with no location (S-062). The identification of "Jamuma" with Al-Jumum (الجموم) is **stated by the project owner** (Tariq, PROJECT.md section 4; S-063). It is not a published source, and the station site is unlocated.

**Resolution (LANDBRIDGE_RECONCILE, coordinator, 30 Oct 2026; analysis, confidence medium):** see `docs/costs-landbridge.md` for the sources (S-lb-001 to S-lb-034), the arithmetic and the hypothesis table. Summary:
- USD 7 bn = SR 26.25 bn at the peg = the **2008–2011 tender-era estimate** (SR 26 bn, "$US 6.93bn", S-lb-014; SR 26.6 bn in 2012, S-lb-016) for a 950 km Riyadh–Jeddah freight/container line plus 115 km Dammam–Jubail. English trade press carried it unchanged for the enlarged scope through MEED of Apr 2025 (S-lb-008) and ENR of Jun 2026 (S-049; Okaz's 22 Jun 2026 report of it, S-lb-007, bounds the date).
- SR 100 bn = USD 26.67 bn = the **2022–2026 official whole-programme estimate including trains**: Minister Al-Jasser, 22 Mar 2022 ("نحو 100 مليار ريال", infrastructure and trains, S-lb-002) and 16 Nov 2022 (S-lb-003); SAR CEO Al-Malik, Jan 2026, on the programme "في الصورة" (S-lb-001). Price year: not stated in any source.
- Hypotheses: (a) phase: no evidence; (b) Riyadh package or private PPP share: not supported (one outlet; USD 200 m/km fails the plausibility test; MEED gives no package value); (c) scope and content growth: supported; (d) legacy figure repeated: best supported; (e) reporting error: not an error, an un-updated figure.
- Per km: USD 7 bn over the 900–950 km core = 7.4–7.8 USD m/km (conventional-line construction band); SR 100 bn over >1,500 km new track = ≤ 17.8 USD m/km, or 12.2 over 2,178 km incl. upgrades (between the EC new-conventional and new-high-speed bands; Haramain all-in is 35.3). Both cells are plausible on their own vintage and scope.
- Cost register: carry SR 100 bn (nominal, price year not stated, all-in incl. trains, land/financing/contingency unknown) as `derived` with a null high pending the reference-class uplift; keep SR 26–26.6 bn as a history-only `sourced` row; the Riyadh Rail Link package value stays `unknown` until the award notice.
- Still open (Tariq to request, never this project): ENR full text; the MOT X post of 16 Nov 2022 and the Jan 2026 broadcast wording; the Riyadh Rail Link award value; Railway Gazette 11 Oct 2011 and the 2008 BOT tender basis.
- Related: the MEED Projects profile at the `project-profile/?pid=114639` URL (S-lb-018; paywalled, fields inconsistent) does show the Riyadh–Jeddah stations as "Jamuma, Moya and Al-Doadmi", which matches the brief's "Jamuma" spelling; it gives no location, so the Al-Jumum site stays unlocated (S-063).

## C-002 Landbridge Riyadh–Jeddah length — status: unresolved (range)
The sources give four values: 900 km (MEED, Jan 2026, S-054), 920 km (Saudi Auto, S-056), 950 km (2021 press, S-055) and 958 km (Wikipedia, 2013 design contract, S-056). The brief says ~950 km, with ~900 km from MEED. Carry 900–958 km with sources. Speeds also differ: 250 km/h design and 220 km/h operating for passengers (S-058), 200 km/h trains (Okaz via Gulf News), and 120/140/160 km/h for freight.

## C-003 Al-Jumum population — status: resolved for use (secondary), primary pending
- Governorate: 89,575 (Census 2022 via citypopulation.de crediting GASTAT, S-065; matches the brief).
- Place (town): 41,089 (S-066).
- The Makkah Region Emirate page prints 98,575, with no year and no source (S-067).

The governorate and the town are different perimeters, so the brief's 89,575 is the **governorate** figure. Distances of ~25 km to Makkah and ~72 km to Jeddah: no source found (S-068). The only 72 km figure found belongs to a Jeddah–Makkah highway project. R1a will measure both on the OSM road graph.

## C-004 Haramain HSR speed, topology and distances — status: open
- **Speed.** The brief gives 300 km/h as the design speed. Wikipedia (S-003) gives 300 km/h as the in-service limit and 320/360 km/h as the design speed.
- **Topology.** The brief places KAIA in a main-line sequence of 0/77/17/94/261 km. Wikipedia says the airport station is on a branch (S-004), with a 449.2 km main line plus a 3.75 km branch (S-002). Only 77 km (Makkah–Jeddah) is sourced, and it is secondary (S-005). The figures 17, 94 and 261 km are unsourced (S-006). **Analysis:** 77 + 17 + 94 + 261 = 449 km, which matches the 449.2 km main line arithmetically but is not evidence.
- **Cost.** USD 9.4 bn "total contract value", with no scope, conflicts with a Spanish-press 6,736 million (S-010).
- **O&M term.** The sources give 12 years, "until 2030" and "extended to 2038" (S-011).

## C-005 Riyadh Metro cost and opening dates — status: open
- **Cost.** USD 25 bn and USD 166 m/km are attributed to the RCRC CEO (Argaam, S-038), against USD 22.5 bn (Wikipedia, S-039). Arithmetic on 176 km: 25,000 ÷ 176 = USD 142.0 m/km; 25,000 ÷ 166 = 150.6 km implied; 22,500 ÷ 176 = USD 127.8 m/km. These do not reconcile on one length or scope. The ENR "USD 25 B" headline cited in the brief was not located.
- **Opening dates.** The brief puts Lines 2 and 3 on 15 Dec 2024 and Line 5 on 5 Jan 2025. Railway Gazette puts Lines 2 (Red) and 5 (Green) on 15 Dec 2024 (S-035) and Line 3 (Orange) on 5 Jan 2025 (S-036). Both rows are secondary; RCRC's per-line primary was not found.

## C-006 SAR East line — status: brief differs from SAR
- **Al-Kharj.** SAR lists the passenger line as Riyadh, Hufuf, Abqaiq, Dammam (S-025) and places Al-Kharj on the freight line (S-026). The brief lists Al-Kharj as a passenger stop.
- **Network total.** SAR prints 1,775 km (S-027), while 733 km passenger plus 566 km freight = 1,299 km. The page does not explain the gap.
- **North network total.** SAR prints 2,750 km (S-021); Railway Gazette (Jan 2026) prints 2,700 km.

## C-007 SAR North line cost and length — status: open
- **Cost.** SAR 20 bn (Wikipedia, uncited) vs SR 10 bn for the whole 2,750 km North network (2017 press snippet, page 403); see S-023.
- **Length.** SAR prints 1,250 km (S-017); Wikipedia prints 1,242 km (S-022). Use SAR's figure.

## C-008 GCC railway Saudi section — status: open
- **Length.** MEED prints about 672 km (S-029). Sub-section lengths seen in a MEED search snippet (141 + 200 + 151 + 21 km) sum to 513 km.
- **Network total.** Snippets give 2,117, 2,177 and 2,186 km.
- **Routing.** Dammam is not confirmed as a stop in the text read (S-032).

## C-009 National rail ridership 2023 — status: primary unreachable
- **Passengers.** 30.3 M rail passengers in 2023 comes from press quoting GASTAT (S-041). GASTAT's 2023 PDF returned 404.
- **Passenger-km.** The 2,618 M intercity passenger-km figure was seen only in a search-engine extraction of that PDF (S-042, `unverified`).
- **Later figures.** GASTAT's 2025 publication (S-043, S-045, verified) gives 42.7 M passengers and 3,724.3 M passenger-km for 2024, and 156.4 M passengers and 3,609.3 M passenger-km for 2025.
- **HHR ridership.** The ~6.97 M HHR passengers for 2023 (S-012) is a Renfe press figure (page 404 on the access date; excerpt only).
- **Analysis.** Press quotes an intercity share of 27.5 % of 30.3 M, which is about 8.3 M and exceeds HHR's 6.97 M. GASTAT's intercity category therefore includes the SAR North and East services.

## C-010 Governorate count — status: **resolved to 150 (relayed GASTAT census table, CP2_PREP item 1 addendum, 31 Oct 2026)**
- **Resolution (31 Oct 2026).** The GASTAT Census 2022 governorate table relayed by DataPulse (S-cp2-gastat-001) has 150 governorate rows summing to 32,175,224, the primary national total (TA9, S-cp2-gastat-003); every region's governorate sum equals the primary TA1/TA9 region total (S-cp2-gastat-002/S-cp2-gastat-003); all 150 figures are identical to S-073. `governorates_gastat: 150 (relayed, DataPulse ← GASTAT Tableau; primary PDF TA1 confirms the regions)`. The primary governorate view itself is still to find (portal unreachable). The two `conflict` rows (Abanat, Al-Bayda) stay as flagged in `docs/coverage.md`.
- **Published totals.** These differ: 150 (citypopulation.de rows crediting GASTAT, S-073; Saudipedia, S-076), 139 (English Wikipedia infobox, S-074), 136 (Wikipedia text on the 2012 increase, S-075), and 135, 134 and 118 in snippets.
- **Primary sources.** None was readable. The GASTAT census portal did not resolve (S-072, S-090), and the Ministry of Interior regions page lists no governorates.
- **Analysis.** The 150-row list counts each region's capital city as a governorate row; sources that write "N governorates plus the capital" give smaller totals. `docs/coverage.md` must reconcile to a primary count. Until one is read, use the 150-row list as the working universe (more complete, so no silent omission) and mark it secondary.

## C-011 Census 2022 Makkah and Madinah region totals — status: **resolved (primary TA1/TA9, CP2_PREP item 1 addendum, 31 Oct 2026)**
- **Resolution (31 Oct 2026).** The primary GASTAT tables give Makkah 8,021,463 and Madinah 2,137,983 (TA1, S-cp2-gastat-002; TA9, S-cp2-gastat-003), the GLMM values and the governorate sums; citypopulation.de's region rows (7,769,994; 2,389,452) are wrong (swapped share, as analysed below).
- **Region rows.** citypopulation.de's region rows (Makkah 7,769,994; Madinah 2,389,452) disagree with GLMM (8,021,463; 2,137,983) by exactly 251,469 in opposite directions (S-079).
- **Governorate rows.** citypopulation.de's own governorate rows sum to the GLMM values.
- **National total.** Both sources give 32,175,224 (S-077).
- **Analysis.** The two region rows look swapped. Use the GLMM values (consistent with the governorate sums) until the GASTAT table is read.

## C-012 Census 2022 reference date — status: open
GASTAT gives the evening of 8 Shawwal 1443 H = 9 May 2022 (S-071); secondaries print 10 May 2022. **Analysis:** this may be a night-of count against a calendar-day date. Not verified.

## R1a conflicts (31 Oct 2026)

**C-r1a-01 Makkah to Jeddah journey time.** 43 min for 77 km (Wikipedia, S-005, secondary) vs 28 to 30 min (travel guide, Oct 2026, S-r1a-006, secondary) vs 21 min (pre-opening projection, S-r1a-005, unverified) vs 30 min (Jeddah central, S-r1a-007, unverified) vs 1 h 45 min Express (aggregator, S-r1a-008, secondary; about 44 km/h, inconsistent with a 300 km/h line). Status: **open**. No primary read. Analysis: the 1 h 45 min row is the least plausible; the 43 min and 28 to 30 min rows differ by 13 to 15 min and may reflect different stops or Makkah stations. Primary to find: an HHR timetable or a sampled booking result with date.

**C-r1a-02 HHR fares.** Makkah–Jeddah economy 43 (guide, Oct 2026, S-r1a-012) vs 40 at launch in 2018 (S-r1a-017, unverified). Makkah–Madinah economy 162 (guide, S-r1a-014, unverified) vs 150 (Gulf News route list, S-r1a-016, unverified). Jeddah–Madinah 135 vs 125. The guide's direction ("one-way" vs "both directions") is unclear. Status: **open**. Primary to find: the HHR fare table.

**C-r1a-03 HHR station naming.** SAR prints "Al-Sulimaniyah - JEDDAH" (S-001, S-r1a-001); the Wikipedia list prints "Jeddah Central" and records it out of service 29 Sep 2019 to 31 Mar 2021 (S-r1a-020). Status: **open** (naming; use SAR's print name in the YAML).

**C-r1a-04 Mecca to Medina time.** "Around 2 hours" (Wikipedia, S-r1a-010) vs 2 h 20 min (HHR 300 Special, aggregator, S-r1a-009) vs about 2.5 h (search summary, unverified). Status: **open**.

**C-r1a-05 SAR North passenger opening dates and end point.** The Wikipedia line page gives Qassim 2017, Hail 23 Nov 2017, Al-Jouf 7 Nov 2018, Qurayyat 31 Mar 2022 (S-r1a-030); the Wikipedia list page gives 2018 for Qassim, Hail, Al-Jawf and Qurayyat (S-r1a-031). SAR's English page ends the passenger line at Al Haditha (S-018); the list page calls Al-Haditha "proposed". The Arabic SAR page names the line "to Al Qurayyat" (S-r1a-026). Status: **open**. Primary to find: SAR station notices with dates; SAR's own end point.

**C-r1a-06 SAR North freight junction name.** "AlBaithah Junction" (SAR, S-020) vs "Zabirah" (Wikipedia list, S-r1a-032). Status: **open** (possibly one junction under two names; not confirmed).

**C-r1a-07 Riyadh Metro lengths.** Wikipedia per-line (S-r1a-045 to S-r1a-050; sum 176.4 km) vs Zawya per-line (S-r1a-052; sum 176.2 km; Orange 41.1 vs 40.7, Yellow 29.7 vs 29.6, Green 13.3 vs 12.9, Purple 28.8 vs 29.9). Both reconcile to 176 km in total. Status: **open** (no RCRC or operator per-line page read; riyadhmetro.sa unreachable).

**C-r1a-08 Riyadh Metro station count.** 85 stations (RCRC, S-034; Zawya, S-051) vs 94 (sum of per-line counts in Wikipedia, S-r1a-045 to S-r1a-050) vs 84 (search summary, unverified). Analysis: 94 counts interchanges on two lines, so 85 is the network count. Status: **resolved as an analysis (medium confidence)**; confirm with RCRC.

**C-r1a-09 Al-Kharj on the East line.** The brief lists Al-Kharj as a passenger stop. SAR's passenger line has four stops and excludes Al-Kharj (S-025); SAR's freight line includes Al-Kharj (S-026). The Dammam station article describes a Dammam–Riyadh line via Kharj without service detail (S-r1a-035, unverified). Status: **open** (extends C-006). Primary to find: SAR station map or a dated timetable showing Al-Kharj.

**C-r1a-10 East freight length.** SAR: 566 km (S-026, verified). Search summaries: 556, 550 and 546 km (S-r1a-038, unverified). Status: **open** (use SAR's 566 km with the conflict noted).

**C-r1a-11 Riyadh Rail Link design lead.** Typsa (MEED, S-r1a-058, unverified) vs Sener (TradeArabia, S-r1a-059, unverified). Both are unread beyond headlines. Status: **open**. Primary to find: SAR consultancy award notice.

**C-r1a-12 Hejaz Damascus–Medina length and Medina marker.** 1,300 km (Wikipedia text, S-r1a-070) vs a Medina km marker of 1,320.5 (route table, S-r1a-067). Origin of the km markers is not stated. Status: **open** (a 20.5 km gap).

**C-r1a-13 Hejaz closure date.** "Closed after 1920" (Wikipedia, S-r1a-068); Al-Ula station abandoned 1920 (ArchNet, unverified, S-r1a-074); plans dropped 1924 (S-r1a-069); 1926 asset list (unverified, S-r1a-075). Status: **open** (a range, no primary). Primary to find: Saudi Heritage Commission or the Hejaz Railway Museum.

**C-r1a-14 Riyadh Rail Link tender date.** Issued 29 Jan 2026 (MEED 31 Aug 2026, S-r1a-055) vs "SAR tenders Riyadh section" headline dated 12 Feb 2026 (S-060); an award "expected by end of 2025" (MEED 12 Feb, per a search summary). Status: **open** (the dates describe different events; confirm with the SAR tender notice).

**C-r1a-15 SAR East passenger length.** SAR prints "double track with a total length of 733 km" (S-024, verified); the OSM track distance between the Riyadh and Dammam passenger stations is 449.1 km (S-r1a-808; cities/ksa/lines/sar-east-passenger.yaml), and Seat61 gives 449 km (S-r1a-041, unverified). Analysis: 733 km is not the station-to-station route length (perhaps a network or track total). Status: **open**; `length_km` left empty in the line file.

**C-r1a-16 Riyadh Metro station count in OSM.** 93 stop rows on the six OSM route relations, 82 unique names (S-r1a-801…806), against 85 stations (S-034) and 94 per-line (Wikipedia, C-r1a-08). Line 6 has 10 named stops in OSM against 11 per Wikipedia (one unnamed stop skipped). Status: **open** (OSM incomplete or names differ; RCRC list to read).

**C-r1a-17 SAR North freight length.** SAR: 1,550 km (S-019); OSM track distance Al-Jalamid proxy → Jouf → Hail → Al-Baithah proxy → Ras Al-Khair proxy: 1,374.5 km (S-r1a-808). The terminal points are proxies snapped 8.9–14.2 km from their places and branches are not counted. Status: **open (method difference)**.

**C-r1a-18 HHR inter-station distances.** Brief: 0/77/17/94/261 km (S-006 unverified). OSM track (S-r1a-808): Makkah–Jeddah 78.25 km; Jeddah–KAIA 18.77 km (via the branch); Jeddah–KAEC 102.54 km on the main line; KAEC–Madinah 267.75 km; Makkah–Madinah 448.54 km (Wikipedia main line 449.2 km, S-002). Status: **resolved for use (measured, secondary)**; operator table still to find.

**C-r1a-19 Al-Jumum distances.** Brief: about 25 km from Makkah and 72 km from Jeddah by expressway (S-068, unverified). Measured (S-r1a-809, OSRM free flow, city-centre nodes): Makkah 25.9 km great circle / 34.0 km road (27 min); Jeddah 54.8 km great circle / 75.4 km road (57 min). Status: **resolved for use (model measurement, uncalibrated)**.

**C-r1a-20 Governorate polygons.** OSM has 149 admin_level-6 polygons in KSA (cities/ksa/zones/governorates.geojson) against the 150-row working list plus 2 flagged rows (S-073, docs/gastat-regions.md). Per-region counts agree except Asir (17 vs 18; Al-Amwah likely missing in OSM, analysis) and the two flagged rows (Abanat, Al-Bayda), absent in OSM. Status: **open** (extends C-010).

**C-r1a-21 National population: WorldPop 2020 vs census 2022.** WorldPop 2020 100 m constrained UN-adjusted sum 34,813,867 (our sum; manifest worldpop-sau-2020-100m-unadj-constrained) vs census 2022 32,175,224 (S-r1a-502, secondary). Different years and methods; not blended. Grid allocations to settlements are relative estimates only (A-r1a-004). Status: **open**.

**C-r1a-22 Haramain running time (model reality check).** Pure kinematics at 300 km/h (S-003, S-cp2-501) with default acceleration 0.5 m/s², deceleration 0.6 m/s² and dwell 120 s (A-r1a-033…035) gives 18.2 min of running for Makkah–Jeddah (78.25 km) in runs/graph/S0/edges.parquet. The published 43 min (S-005, secondary) gives an implied average of 109 km/h on the OSM km (107 km/h on 77 km). **CP2_PREP decomposition (31 Oct 2026; `docs/network.md` §HHR-check; `uv run python -m network.hhr_check run --seed 1`):** (a) line-speed running 13.10 min over 65.52 km; (b) acceleration and braking 2.78 + 2.31 min (A-r1a-033/034 assumed; Talgo 350 SRO acceleration not found, S-cp2-506); (c) dwell 0 min, since there is no stop between Makkah and Jeddah (S-cp2-503); (d) recovery margin 2.06 min (UIC 451-1, 7 % + 1 min/100 km, S-cp2-505, A-hhr-002). Total **20.25 min** (envelope 18.94–22.25). Source of the 43 min: S-005 cites HHR's Train Schedule archived 19 Oct 2018 (S-cp2-507), which is the opening timetable (Makkah 08:00 → Jeddah 08:43; Makkah–Madinah non-stop 175 min; S-cp2-503). Current secondary listings give 28–30 min (S-cp2-504, S-r1a-006). Status: **open (model to calibrate), residual 22.7 min (20.7–24.1) against the 43 min, outside the ± 3 min re-close band (A-hhr-003); 7.7–9.7 min against the current secondary 28–30 min**. Analysis: no published speed profile explains the residual (A-hhr-001). To resolve: a current SAR timetable (S-r1a-003), an HHR line-speed or speed-restriction profile, and Talgo 350 SRO traction and braking curves. R4 must use an effective speed calibrated to a dated timetable, not the line speed.

## C-geo-Q1 Al-Qarā (Al-Bahah) coordinates: Wikidata/Wikipedia vs OSM — status: **resolved geometrically (GEO_VERIFY, 31 Oct 2026)**

Point-in-polygon against the OSM Al-Qarā governorate polygon (relation 12429803, `cities/ksa/zones/governorates.geojson`, UTM 37N (EPSG:32637; corrected from 38N by CP2_PREP, docs/geo-verify.md §10)), geodesic distances on WGS84 (`screening.geo_verify.cli seat`, method log `runs/geo_verify/seat/method_log.jsonl`):

| point | source | inside the Al-Qarā polygon | km to the boundary | method log |
|---|---|---|---|---|
| 29.8833, 40.2167 | Wikidata Q65040833 P625 (S-cp1-006), Wikipedia (S-cp1-007) | no | 1,010.29 (outside; 1,012.05 before the UTM fix) | geo-seat-8bc6e532 |
| 20.2508, 41.3504 | OSM label node 4975708122 (S-cp1-002) | yes | 6.92 | geo-seat-4b127b45 |
| 20.2475, 41.3607 | OSM admin_centre node 9327998071, Al Tawilah (S-cp1-003) | yes | 5.83 (5.84 before the UTM fix) | geo-seat-a4440de1 |
| 20.394, 41.328 | citypopulation.de page point (S-cp1-005) | yes | 9.93 (9.94 before the UTM fix) | geo-seat-fef79e01 |

The Wikidata/Wikipedia point lies 1,073.6 km (geodesic) from the OSM seat, in Al-Jawf: it is wrong for this entity. The register keeps the OSM seat (no change). Built-up evidence: the footprint cluster at the seat holds 900 buildings over 3.2 km² (A-geo-001…005; `runs/geo_verify/estimate/no-pop/`), the label node falls in the same cluster. Seat population: still not tabulated; derived estimate in the register notes only (record-only, back-test failed).

## C-geo-W1 Wadi ad-Dawasir seat town: "Wadi ad-Dawasir" vs Al-Khamasin — status: **open (geometry consistent with one town; name relation unsourced)**

- The register point (20.4602516, 44.799553) equals OSM place=city node 2632133047 "Wadi Ad Dawasir" (population tag 93,036), not the boundary centroid the row's note states (analysis: coordinates match to 7 decimals). The OSM place=village node 1236411997 "الخماسين / Al Khamasin" lies 4.17 km (geodesic) to the north-west. Both are inside the Wadi ad-Dawasir governorate polygon (relation 12423662; 39.36 and 43.51 km from its boundary (UTM 38N; 39.55 and 43.73 km in the pre-fix UTM 39N, CP2_PREP); geo-seat-0107d1ce, geo-seat-022d6078).
- Sentinel-2 (scene S2C_38QMH_20261026_0_L2A, cloud 0.0002 %, window 44.745–44.822 E, 20.435–20.508 N; method log geo-seat-b5d5f703): one continuous built-up area spans both nodes, with no break between them (visual reading).
- Building footprints cannot test it: the Microsoft footprint tile 122311131 has no buildings west of 44.824 E, so neither node gets a cluster (coverage gap, see `docs/geo-verify.md`).
- Reading (analysis): the census seat locality of 77,433 (S-cp1-025) and Al-Khamasin plausibly describe the same contiguous town, but no source read states that Al-Khamasin is the seat or part of the seat locality. Needs a GASTAT locality table or an official gazetteer. Nothing changed in the register except the derived-estimate note.

## GEO_VERIFY conflicts (31 Oct 2026): derived estimate vs relayed Census 2022 figure

Rule: geo-verify skill section 3 (> 25% divergence logs a row; both figures kept, nothing overwritten). The derived estimates come from two estimators that FAIL the 30 % back-test gate (`docs/geo-verify.md`), so these rows are weak evidence: they flag where a GASTAT locality table is most needed, not that the relayed figure is wrong. Status of every row: open. Method-log ids resolve in `runs/geo_verify/estimate/secondary/method_log-secondary.jsonl`.

| id | region | settlement | relayed figure (source) | derived central (band) | divergence | method log |
|---|---|---|---|---|---|---|
| C-geo-001 | al_baha | Al-'Aqīq | 19,269 (S-al_baha-002) | 6,699 (1,322–18,013) | -65% | geo-est-70aa0702 |
| C-geo-002 | al_baha | Al-Bāḥah | 90,515 (S-al_baha-002) | 14,994 (5,350–28,378) | -83% | geo-est-62b2b951 |
| C-geo-003 | al_baha | Al-Makhwāh | 26,248 (S-al_baha-002) | 6,769 (2,398–12,019) | -74% | geo-est-8ae47233 |
| C-geo-004 | al_baha | Baljurashī | 35,985 (S-al_baha-003) | 18,351 (3,789–47,160) | -49% | geo-est-db3ef018 |
| C-geo-005 | al_jouf | Abu 'Ajram | 5,610 (S-al_jouf-001) | 4,153 (1,496–7,785) | -26% | geo-est-5518f01a |
| C-geo-006 | al_jouf | Al-Fayāḍ | 5,532 (S-al_jouf-001) | 2,945 (779–5,904) | -47% | geo-est-5e5ca224 |
| C-geo-007 | al_jouf | Al-Qurayyat | 167,080 (S-al_jouf-001) | 45,746 (15,287–76,622) | -73% | geo-est-f3c4a847 |
| C-geo-008 | al_jouf | Sakaka | 204,174 (S-al_jouf-001) | 41,557 (14,994–75,151) | -80% | geo-est-cf3ae513 |
| C-geo-009 | al_jouf | Tubarjal | 78,354 (S-al_jouf-001) | 29,341 (5,989–76,277) | -63% | geo-est-9db046b9 |
| C-geo-010 | al_jouf | Ṣuwayr | 12,430 (S-al_jouf-001) | 5,982 (1,552–12,231) | -52% | geo-est-18ebd538 |
| C-geo-011 | asir | Abha | 334,290 (S-asir-001) | 37,434 (7,214–103,067) | -89% | geo-est-52d1a094 |
| C-geo-012 | asir | Ahad Rafidah | 79,202 (S-asir-001) | 23,198 (7,698–38,583) | -71% | geo-est-a05a3394 |
| C-geo-013 | asir | Bisha | 115,537 (S-asir-001) | 71,532 (22,264–121,943) | -38% | geo-est-b834f059 |
| C-geo-014 | asir | Khamis Mushait | 535,065 (S-asir-001) | 151,212 (49,073–314,648) | -72% | geo-est-4d965682 |
| C-geo-015 | asir | Sarat Abidah | 19,855 (S-asir-001) | 3,285 (627–9,132) | -83% | geo-est-92e83d76 |
| C-geo-016 | asir | Zahran al-Janub | 24,134 (S-asir-001) | 3,834 (605–12,880) | -84% | geo-est-375f1899 |
| C-geo-017 | eastern | Abqaiq (Buqayq) | 45,032 (S-eastern-001) | 1,429 (226–4,790) | -97% | geo-est-04a736ec |
| C-geo-018 | eastern | Al-Jubail (Al-Ahsa governorate) | 9,994 (S-eastern-001) | 513,755 (166,633–1,069,670) | +5041% | geo-est-ae416b3e |
| C-geo-019 | eastern | Al-Oyun | 35,226 (S-eastern-001) | 8,826 (1,502–27,512) | -75% | geo-est-0cec05e3 |
| C-geo-020 | eastern | Al-Qaisumah | 27,307 (S-eastern-001) | 10,716 (2,897–21,032) | -61% | geo-est-e4a8e130 |
| C-geo-021 | eastern | Ath-Thuqbah | 248,888 (S-eastern-001) | 152,501 (51,355–305,815) | -39% | geo-est-3a0cec69 |
| C-geo-022 | eastern | Dammam | 1,386,166 (S-eastern-001) | 503,061 (131,254–1,302,053) | -64% | geo-est-cb759223 |
| C-geo-023 | eastern | Dhahran | 143,936 (S-eastern-001) | 47,630 (14,529–105,441) | -67% | geo-est-f83fb23d |
| C-geo-024 | eastern | Hafar al-Batin | 387,096 (S-eastern-001) | 197,224 (59,909–344,498) | -49% | geo-est-899aa495 |
| C-geo-025 | eastern | Hofuf (Al-Hufuf–Al-Mubarraz) | 729,606 (S-eastern-001) | 513,267 (166,581–1,067,966) | -30% | geo-est-4387e161 |
| C-geo-026 | eastern | Jubail | 474,679 (S-eastern-001) | 42,774 (14,701–73,682) | -91% | geo-est-100bbb3d |
| C-geo-027 | eastern | Khafji | 78,691 (S-eastern-001) | 39,434 (8,274–99,717) | -50% | geo-est-c05d169a |
| C-geo-028 | eastern | Khobar | 409,549 (S-eastern-001) | 116,070 (38,222–238,023) | -72% | geo-est-b67529dd |
| C-geo-029 | eastern | Qatif | 87,332 (S-eastern-001) | 503,132 (131,299–1,301,973) | +476% | geo-est-4fc00188 |
| C-geo-030 | eastern | Rahimah | 57,030 (S-eastern-001) | 22,814 (6,960–39,676) | -60% | geo-est-ae6ac10b |
| C-geo-031 | eastern | Saihat | 84,818 (S-eastern-001) | 506,290 (131,905–1,312,302) | +497% | geo-est-df0b95db |
| C-geo-032 | eastern | Tarout | 117,646 (S-eastern-001) | 57,963 (21,029–105,403) | -51% | geo-est-c524d0b4 |
| C-geo-033 | hail | Ash-Shamlī | 9,163 (S-hail-001) | 12,425 (4,103–25,409) | +36% | geo-est-0b2ce934 |
| C-geo-034 | hail | Baq'ā' | 19,659 (S-hail-001) | 10,698 (1,816–33,447) | -46% | geo-est-f9f6febe |
| C-geo-035 | hail | Jubbah | 5,622 (S-hail-001) | 9,152 (3,146–17,976) | +63% | geo-est-cd15768c |
| C-geo-036 | hail | Mawqaq | 3,148 (S-hail-001) | 5,316 (1,856–9,305) | +69% | geo-est-be17cfdb |
| C-geo-037 | hail | Turubah | 8,590 (S-hail-001) | 3,482 (653–9,855) | -59% | geo-est-6f3fa482 |
| C-geo-038 | hail | Ḥā'il | 448,623 (S-hail-001) | 123,615 (30,960–261,875) | -72% | geo-est-76645cf3 |
| C-geo-039 | jazan | Abu Arish | 69,632 (S-jazan-002) | 36,249 (11,775–75,359) | -48% | geo-est-c2330611 |
| C-geo-040 | jazan | Ahad al Musarihah | 25,670 (S-jazan-002) | 8,770 (1,791–22,790) | -66% | geo-est-1b09fa5c |
| C-geo-041 | jazan | Al Tuwal | 4,671 (S-jazan-002) | 2,561 (474–7,344) | -45% | geo-est-c77b8e9f |
| C-geo-042 | jazan | Damad | 26,079 (S-jazan-002) | 18,954 (6,663–33,395) | -27% | geo-est-f89cfbc1 |
| C-geo-043 | jazan | Jizan | 173,919 (S-jazan-002) | 17,119 (3,683–42,218) | -90% | geo-est-1c56aca6 |
| C-geo-044 | jazan | Sabya | 72,086 (S-jazan-002) | 43,751 (15,065–75,510) | -39% | geo-est-dbe57da8 |
| C-geo-045 | jazan | Samtah | 43,301 (S-jazan-002) | 21,370 (5,563–43,559) | -51% | geo-est-014c7ddb |
| C-geo-046 | madinah | Al-Henakiyah | 24,880 (S-madinah-001) | 12,968 (4,563–22,870) | -48% | geo-est-b9707bf0 |
| C-geo-047 | madinah | Al-Madinah al-Munawwarah | 1,411,599 (S-madinah-001) | 210,932 (62,214–482,944) | -85% | geo-est-56a10b65 |
| C-geo-048 | madinah | Al-Ula | 40,760 (S-madinah-001) | 5,741 (1,269–13,775) | -86% | geo-est-cb877f28 |
| C-geo-049 | madinah | Badr | 30,494 (S-madinah-001) | 15,204 (4,542–27,004) | -50% | geo-est-9e561777 |
| C-geo-050 | madinah | Khaybar | 15,888 (S-madinah-001) | 4,416 (1,334–7,754) | -72% | geo-est-b503060d |
| C-geo-051 | madinah | Yanbu' al-Bahr | 331,916 (S-madinah-001) | 81,465 (25,137–140,079) | -75% | geo-est-3436e639 |
| C-geo-052 | makkah | Al-Jumūm | 41,089 (S-makkah-001) | 15,246 (3,077–40,080) | -63% | geo-est-3a45d151 |
| C-geo-053 | makkah | Al-Qunfudhah | 42,447 (S-makkah-001) | 8,515 (2,929–16,718) | -80% | geo-est-2113b138 |
| C-geo-054 | makkah | Al-Ḥawiyah | 171,610 (S-makkah-001) | 91,015 (33,029–169,364) | -47% | geo-est-ef7b5349 |
| C-geo-055 | makkah | Aṭ-Ṭa'if | 563,282 (S-makkah-001) | 157,092 (51,226–325,326) | -72% | geo-est-2e7c0a9f |
| C-geo-056 | makkah | Baḥrah | 70,118 (S-makkah-001) | 29,595 (9,982–59,257) | -58% | geo-est-d2719476 |
| C-geo-057 | makkah | Jiddah | 3,712,917 (S-makkah-001) | 768,543 (205,164–1,944,161) | -79% | geo-est-f9b72443 |
| C-geo-058 | makkah | Khulaīṣ | 20,139 (S-makkah-001) | 1,191 (202–3,724) | -94% | geo-est-c3352d51 |
| C-geo-059 | makkah | Makkah al-Mukarramah | 2,385,509 (S-makkah-001) | 432,223 (117,077–1,077,558) | -82% | geo-est-d6e69874 |
| C-geo-060 | makkah | Rābigh | 72,928 (S-makkah-001) | 18,950 (3,556–53,579) | -74% | geo-est-e7ae4b6d |
| C-geo-061 | makkah | Thuwal | 26,957 (S-makkah-001) | 14,510 (5,311–26,769) | -46% | geo-est-ccd65def |
| C-geo-062 | najran | Al-Mish'alīah | 23,252 (S-najran-002) | 8,339 (1,009–36,583) | -64% | geo-est-49ddeec2 |
| C-geo-063 | najran | Al-Wadī'ah | 8,365 (S-najran-002) | 5,213 (1,316–13,949) | -38% | geo-est-eb718bfd |
| C-geo-064 | najran | Badr al-Janūb | 2,709 (S-najran-002) | 4,128 (1,513–7,602) | +52% | geo-est-74f221bb |
| C-geo-065 | najran | Khubāsh | 7,182 (S-najran-002) | 1,430 (150–7,221) | -80% | geo-est-773b38ec |
| C-geo-066 | najran | Najrān | 381,431 (S-najran-002) | 89,968 (25,764–166,697) | -76% | geo-est-4d5cde0c |
| C-geo-067 | najran | Sharūrah | 89,456 (S-najran-002) | 52,622 (15,043–124,311) | -41% | geo-est-0a0db31a |
| C-geo-068 | najran | Ḥubūnā | 12,738 (S-najran-002) | 5,017 (1,184–11,276) | -61% | geo-est-52e16428 |
| C-geo-069 | northern_borders | Arar | 199,247 (S-northern_borders-001) | 42,073 (14,344–83,334) | -79% | geo-est-532f4b7f |
| C-geo-070 | northern_borders | Rafha | 63,929 (S-northern_borders-001) | 39,443 (10,017–82,402) | -38% | geo-est-ac0859d0 |
| C-geo-071 | northern_borders | Turaif | 61,395 (S-northern_borders-001) | 4,189 (337–27,616) | -93% | geo-est-24dad6c3 |
| C-geo-072 | qassim | 'Uyūn al-Jiwā' | 15,619 (S-qassim-002) | 7,775 (2,717–13,620) | -50% | geo-est-49b55175 |
| C-geo-073 | qassim | Al-Bukayriyah | 43,229 (S-qassim-002) | 25,594 (9,366–46,944) | -41% | geo-est-28b6de1d |
| C-geo-074 | qassim | Al-Khubarā' | 16,906 (S-qassim-002) | 9,597 (3,087–15,832) | -43% | geo-est-b8107633 |
| C-geo-075 | qassim | Al-Malīdā' | 6,967 (S-qassim-002) | 4,774 (1,265–9,561) | -31% | geo-est-617a01fa |
| C-geo-076 | qassim | Al-Quwārah | 5,646 (S-qassim-002) | 3,565 (758–8,899) | -37% | geo-est-adf3b38a |
| C-geo-077 | qassim | Ar-Rass | 107,902 (S-qassim-002) | 45,400 (9,554–114,471) | -58% | geo-est-82ba96de |
| C-geo-078 | qassim | Ash-Shimāiyah | 5,719 (S-qassim-002) | 2,656 (551–6,798) | -54% | geo-est-6e60a132 |
| C-geo-079 | qassim | Buraydah | 571,169 (S-qassim-002) | 113,540 (30,191–226,554) | -80% | geo-est-c6d4573a |
| C-geo-080 | qassim | Dakhnah | 6,354 (S-qassim-002) | 11,443 (2,115–41,803) | +80% | geo-est-f318d217 |
| C-geo-081 | qassim | Riyāḍ al-Khabrā' | 25,588 (S-qassim-002) | 17,079 (6,174–31,902) | -33% | geo-est-b2e27fdb |
| C-geo-082 | riyadh | Ad-Dawadmi | 86,861 (S-riyadh-009) | 25,042 (5,041–66,006) | -71% | geo-est-b4d0c88c |
| C-geo-083 | riyadh | Ad-Dilam | 39,267 (S-cp1-012) | 11,045 (3,055–21,192) | -72% | geo-est-aa64f7e7 |
| C-geo-084 | riyadh | Ad-Dir'iyah | 61,609 (S-riyadh-003) | 44,486 (11,162–119,726) | -28% | geo-est-96d47cdc |
| C-geo-085 | riyadh | Al-Jubaylah | 8,005 (S-riyadh-003) | 11,932 (3,116–24,242) | +49% | geo-est-b9786971 |
| C-geo-086 | riyadh | Al-Majma'ah | 70,243 (S-riyadh-008) | 35,271 (11,238–58,736) | -50% | geo-est-06a90e4e |
| C-geo-087 | riyadh | Al-Muzahimiyah | 55,604 (S-riyadh-004) | 16,861 (2,426–62,191) | -70% | geo-est-a1b362cc |
| C-geo-088 | riyadh | Al-Quwayiyah | 28,589 (S-cp1-016) | 9,452 (3,235–16,216) | -67% | geo-est-21a9fa79 |
| C-geo-089 | riyadh | As-Sulayyil | 25,136 (S-cp1-018) | 15,595 (4,947–26,085) | -38% | geo-est-a5334378 |
| C-geo-090 | riyadh | Hawtat Bani Tamim | 30,720 (S-cp1-020) | 9,222 (3,219–16,133) | -70% | geo-est-80dc0266 |
| C-geo-091 | riyadh | Layla | 29,698 (S-cp1-013) | 20,996 (6,634–35,254) | -29% | geo-est-f01aec66 |
| C-geo-092 | riyadh | Marat | 6,574 (S-cp1-022) | 11,516 (3,689–24,274) | +75% | geo-est-57665a46 |
| C-geo-093 | riyadh | Riyadh | 6,924,566 (S-080) | 1,810,951 (482,344–4,591,496) | -74% | geo-est-bc7c5167 |
| C-geo-094 | riyadh | Shaqra | 32,215 (S-cp1-023) | 21,175 (4,781–49,757) | -34% | geo-est-fefd3baf |
| C-geo-095 | riyadh | Thadiq | 7,433 (S-cp1-024) | 5,523 (1,227–13,187) | -26% | geo-est-73b35cd1 |
| C-geo-096 | tabuk | Al-Bad' | 16,583 (S-tabuk-002) | 9,036 (3,027–15,170) | -46% | geo-est-ed43f146 |
| C-geo-097 | tabuk | Al-Wajh | 33,868 (S-tabuk-002) | 12,656 (4,619–23,418) | -63% | geo-est-4b9daaa3 |
| C-geo-098 | tabuk | Duba | 39,543 (S-tabuk-002) | 10,724 (2,112–28,896) | -73% | geo-est-66f4a932 |
| C-geo-099 | tabuk | Haql | 25,652 (S-tabuk-002) | 18,874 (6,908–34,820) | -26% | geo-est-baeed3ad |
| C-geo-100 | tabuk | Tabuk | 594,350 (S-tabuk-002) | 134,515 (45,537–268,338) | -77% | geo-est-9d5894c7 |
| C-geo-101 | tabuk | Tayma | 37,579 (S-tabuk-002) | 16,485 (4,484–32,155) | -56% | geo-est-538d45af |
| C-geo-102 | tabuk | Umluj | 46,229 (S-tabuk-002) | 17,910 (5,146–33,074) | -61% | geo-est-c5c23ba7 |

## CP2_PREP item 1 addendum (31 Oct 2026): relayed Census 2022 city figures vs earlier figures (> 2 %)

`uv run python -m screening.gastat apply --seed 1` → `runs/gastat/apply/conflicts.csv`. The relayed GASTAT census table (S-cp2-gastat-001) is authoritative for governorate and city totals (Tariq, CP2_PREP addendum); the earlier figure is kept in the row's `notes`. All 150 governorate figures and 55 of the 60 city figures were identical; the rows below differ by more than 2 %.

| id | settlement | relayed Census 2022 (S-cp2-gastat-001) | earlier figure (source) | difference | reading (analysis) | status |
|---|---|---|---|---|---|---|
| C-cp2-601 | Al-Jubail (Eastern; register `eastern:osm:38903292`, `KSA-ST-00002`) | 302,446 | 474,679 (S-eastern-001, citypopulation.de; also S-eastern-002 Wikipedia) | −36.3 % | cause found (addendum 2): the primary TA1 city table lists Aljubayl 302,446 and Jubail Industrial City 172,233 separately (S-cp2-gastat-008); 302,446 + 172,233 = 474,679, the aggregator's figure, so the aggregator merged the two | resolved: primary figure 302,446 for the city node (Jubail Industrial City has no OSM place node, unmatched) |
| C-cp2-602 | Yanbu' al-Bahr (Madinah; `madinah:osm:3148037089`, `KSA-ST-01439`) | 258,777 | 331,916 (S-madinah-001, citypopulation.de) | −22.0 % | cause found (addendum 2): the primary table lists Yanbu 258,777 and Yanbaa As-Senayah (Yanbu Industrial City) 73,139 separately (S-cp2-gastat-008); 258,777 + 73,139 = 331,916, the aggregator's figure | resolved: primary figure 258,777 (Yanbu Industrial City has no OSM place node, unmatched) |
| C-cp2-603 | Safwa (Eastern; `KSA-ST-05170`, settlement universe only) | 45,676 | 50,447 (OSM `population` tag, `derived`) | −9.5 % | official beats derived (A-screen-031) | resolved: relayed figure used, identical to the primary Safwa row (addendum 2) |

Not a conflict: Al-Hofuf (430,105) + Al-Mubarraz (299,501) = 729,606, the combined register row (S-eastern-001), now sourced to S-cp2-gastat-001 as the sum. File defect: the Census 2010 cities xlsx prints Al Seeh's total as 103,216 while its parts sum to 234,607, the total printed in the GASTAT PDF (S-cp2-gastat-005); `screening.gastat` uses the sum of parts.

## CP2_PREP item 1 addendum 2 (31 Oct 2026): primary Census 2022 TA1 tables vs the relayed file and vs earlier figures

`uv run python -m screening.gastat primary --seed 1` → `runs/gastat/primary/` (`crosscheck_governorates.csv`, `crosscheck_cities.csv`, `city_matches.csv`, `changes.csv`). The primary TA1 exports (S-cp2-gastat-007 governorates, S-cp2-gastat-008 cities of 5,000 or more) are the value of record from CP2 on; the relayed DataPulse file (S-cp2-gastat-001) is a cross-check only (`secondary`).

| id | subject | primary (S-cp2-gastat-007/008) | other figure (source) | difference | reading (analysis) | status |
|---|---|---|---|---|---|---|
| C-gastat-001 | primary vs relayed, governorate by governorate (150) and city by city (60) | 150 governorates, 271 cities + Other | DataPulse relayed rows (S-cp2-gastat-001) | **0 differences** in total, Saudi and non-Saudi on all 150 governorates and all 60 relayed cities; 150 governorates joined by name, the 60 cities 20 by name and 40 by identical total (spelling variants such as Bariduh / Buraidah, Jayzan / Jazan, Alzahran / Al-Dahran); no unmatched name on either side | the relayed file is a faithful copy of the primary table | closed: nothing to resolve |
| C-gastat-002 | Ash Shaharin (Eastern; register `eastern:osm:695579475`, `KSA-ST-05310`) | 5,518 (Alshaharin) | 9,994 (S-eastern-001, citypopulation.de) | −44.8 % | 9,994 is the primary figure of the Al-Ahsa town Aljabil (الجبيل), which the pilot attached to the Ash Shaharin node (addendum 1 crosswalk note); the node now takes its own primary figure; Aljabil has no node in the universe (unmatched) | resolved: primary figure 5,518 |
| C-gastat-003 | المهد (Makkah; `KSA-ST-03308`, pilot row) | 9,022 is Adham in the primary table | 9,022 (S-makkah-001, citypopulation.de) on a node named المهد | name differs | the identical figure suggests the pilot attached Adham's figure to a differently named node; the 2010 bridge points Adham to أضم (a different node) | resolved at R2 (primary wins, Tariq 31 Oct 2026 16:25): Adham's primary 9,022 (S-cp2-gastat-008, `census2022_TA1_city5k_primary.xlsx`) sits on the R2 Makkah row أضم (`makkah:node:6768442812`, the 2010-bridge node), `official`/`verified`; relayed 9,022 (S-makkah-001, citypopulation.de) on the same row: difference 0.0 %; no register row carries 9,022 under المهد (`runs/r2/primary_match/primary_cities.csv`, tier `identical figure`) |
| C-gastat-004 | Ash Shinan (Hail; `KSA-ST-00998`, pilot row) | 11,560 is Alshazalah in the primary table | 11,560 (S-hail-001, citypopulation.de) on the node الشنان | name differs | as C-gastat-003; Alshazalah not identified | resolved at R2 (primary wins): the archived citypopulation.de Hail table (S-hail-001, `data/ksa/hail/citypop_hail_census2022.csv`) gives 11,560 to Ash-Shanan / الشنان, the only 11,560 in either table, so the primary city Alshazalah (TA1 export spelling; 11,560, S-cp2-gastat-008) is placed on `hail:node:1237555018` (tier `relay bridge`); relayed 11,560 vs primary 11,560: 0.0 %; the row now carries the primary figure, `official`/`verified` |
| C-gastat-005 | 38 rows whose figure changes by more than 2 % when the primary figure replaces it (37 universe rows that held OSM `population` tags or grid allocations, and the register row of C-gastat-002) | table below | table below | −47.7 % to +763.1 % | official beats derived and grid (A-screen-031); for grid rows the size of the change is the back-test error (`docs/geo-verify.md` §12) | resolved: primary figure used |

| table | key | primary city (export spelling) | previous | previous source | primary (S-cp2-gastat-008) | difference |
|---|---|---|---|---|---|---|
| pilot-eastern.parquet | eastern:osm:695579475 | Alshaharin | 9,994 | S-eastern-001 | 5,518 | -44.8 % |
| settlements.parquet | KSA-ST-00197 | Uqlat Alsuqur | 6,659 | osm-gcc-2026-10-14 node/747671382 population tag | 9,717 | +45.9 % |
| settlements.parquet | KSA-ST-00278 | King Abdullah Economic City | 2,087 | worldpop-sau-2020-100m-unadj-constrained | 5,126 | +145.6 % |
| settlements.parquet | KSA-ST-00281 | Mustawrah | 7,034 | osm-gcc-2026-10-14 node/1013647103 population tag | 6,220 | -11.6 % |
| settlements.parquet | KSA-ST-00381 | Harmah | 8,701 | osm-gcc-2026-10-14 node/1236399809 population tag | 7,775 | -10.6 % |
| settlements.parquet | KSA-ST-00411 | Al Ruwaydah | 6,478 | osm-gcc-2026-10-14 node/1236421438 population tag | 7,916 | +22.2 % |
| settlements.parquet | KSA-ST-00513 | Alsayl Alsaghir | 10,946 | worldpop-sau-2020-100m-unadj-constrained | 13,850 | +26.5 % |
| settlements.parquet | KSA-ST-00519 | Qia | 2,787 | worldpop-sau-2020-100m-unadj-constrained | 9,262 | +232.3 % |
| settlements.parquet | KSA-ST-00616 | Al Bijadyah | 6,985 | worldpop-sau-2020-100m-unadj-constrained | 8,560 | +22.5 % |
| settlements.parquet | KSA-ST-00644 | Sajer | 12,921 | osm-gcc-2026-10-14 node/1236696327 population tag | 14,858 | +15.0 % |
| settlements.parquet | KSA-ST-00691 | Hautat Sudair | 18,954 | osm-gcc-2026-10-14 node/1236702453 population tag | 14,813 | -21.8 % |
| settlements.parquet | KSA-ST-00751 | Al Hayathem | 10,495 | osm-gcc-2026-10-14 node/1236705176 population tag | 13,893 | +32.4 % |
| settlements.parquet | KSA-ST-00754 | Al Haier | 16,845 | osm-gcc-2026-10-14 node/1236705195 population tag | 13,951 | -17.2 % |
| settlements.parquet | KSA-ST-00836 | Namerah | 13,188 | worldpop-sau-2020-100m-unadj-constrained | 9,283 | -29.6 % |
| settlements.parquet | KSA-ST-00991 | Alajfir | 871 | worldpop-sau-2020-100m-unadj-constrained | 7,518 | +763.1 % |
| settlements.parquet | KSA-ST-01089 | Al Ithnayn | 8,046 | osm-gcc-2026-10-14 node/1237751840 population tag | 5,593 | -30.5 % |
| settlements.parquet | KSA-ST-01129 | Tameer | 9,406 | osm-gcc-2026-10-14 node/1237833868 population tag | 11,217 | +19.3 % |
| settlements.parquet | KSA-ST-01137 | Al Artawiyyah | 10,596 | osm-gcc-2026-10-14 node/1237835766 population tag | 8,684 | -18.0 % |
| settlements.parquet | KSA-ST-01201 | Abwalsle | 5,931 | osm-gcc-2026-10-14 node/1237960681 population tag | 6,316 | +6.5 % |
| settlements.parquet | KSA-ST-01206 | Al Madaya | 7,752 | osm-gcc-2026-10-14 node/1237960746 population tag | 7,330 | -5.4 % |
| settlements.parquet | KSA-ST-01212 | Almataean | 7,652 | osm-gcc-2026-10-14 node/1237960937 population tag | 7,116 | -7.0 % |
| settlements.parquet | KSA-ST-01218 | Alkharadiluh | 3,403 | worldpop-sau-2020-100m-unadj-constrained | 5,318 | +56.3 % |
| settlements.parquet | KSA-ST-01227 | Bahr Abu Sukaynah | 6,112 | osm-gcc-2026-10-14 node/1237961015 population tag | 10,862 | +77.7 % |
| settlements.parquet | KSA-ST-01238 | Hakimuh | 7,656 | osm-gcc-2026-10-14 node/1237961090 population tag | 6,991 | -8.7 % |
| settlements.parquet | KSA-ST-01254 | Alhusynaa | 6,230 | osm-gcc-2026-10-14 node/1237961152 population tag | 6,490 | +4.2 % |
| settlements.parquet | KSA-ST-01295 | Alrukubuh | 5,091 | osm-gcc-2026-10-14 node/1237961400 population tag | 6,191 | +21.6 % |
| settlements.parquet | KSA-ST-01304 | Aljaradiuh | 8,488 | osm-gcc-2026-10-14 node/1237961432 population tag | 7,092 | -16.4 % |
| settlements.parquet | KSA-ST-01321 | Alhada | 8,819 | osm-gcc-2026-10-14 node/1237963621 population tag | 5,639 | -36.1 % |
| settlements.parquet | KSA-ST-01438 | Al-Badie Al-Shamali | 7,194 | osm-gcc-2026-10-14 node/2999668494 population tag | 5,417 | -24.7 % |
| settlements.parquet | KSA-ST-01638 | Umm Al Doum | 6,853 | osm-gcc-2026-10-14 node/5526302860 population tag | 5,274 | -23.0 % |
| settlements.parquet | KSA-ST-01713 | Meegowa | 7,401 | worldpop-sau-2020-100m-unadj-constrained | 7,020 | -5.1 % |
| settlements.parquet | KSA-ST-02689 | Almuzaylaf | 8,508 | osm-gcc-2026-10-14 node/7699993028 population tag | 9,769 | +14.8 % |
| settlements.parquet | KSA-ST-03087 | Rawdat Sudair | 3,813 | worldpop-sau-2020-100m-unadj-constrained | 5,304 | +39.1 % |
| settlements.parquet | KSA-ST-03645 | Malahum | 5,480 | worldpop-sau-2020-100m-unadj-constrained | 8,932 | +63.0 % |
| settlements.parquet | KSA-ST-03694 | Dhahban | 18,041 | worldpop-sau-2020-100m-unadj-constrained | 9,436 | -47.7 % |
| settlements.parquet | KSA-ST-04203 | Mazhara | 1,301 | worldpop-sau-2020-100m-unadj-constrained | 6,397 | +391.7 % |
| settlements.parquet | KSA-ST-05310 | Alshaharin | 9,994 | S-eastern-001 | 5,518 | -44.8 % |
| settlements.parquet | KSA-ST-05552 | Ash Shuaybah | 2,667 | worldpop-sau-2020-100m-unadj-constrained | 5,286 | +98.2 % |

## R2 (31 Oct 2026, screening-analyst)

| id | item | value A | value B | difference | explanation | status |
|---|---|---|---|---|---|---|
| C-r2-001 | Ghata (GASTAT primary city, 6,653, S-cp2-gastat-008) vs OSM village غطي (`al_jouf:node:1236744649`) | primary 6,653 | WorldPop grid 2,048 (S-r1a-505) | grid = 0.31 of the census figure | identity by name (citypopulation.de writes غطى, S-al_jouf-010; ى/ي unified), governorate (Al-Qurayyat, S-al_jouf-002) and geo-verify `seat` (inside the Al-Qurayyat polygon, 20.45 km from its boundary; `runs/r2/geo_verify/seat`); the grid ratio is inside the back-test 5–95 % band (A-r2-002). Judgement in `screening/primary_match_decisions.yaml` | resolved (judgement; medium confidence): the row carries 6,653, `official`/`verified` |
| C-r2-002 | figures replaced by a primary figure at the R2 match, > 2 % (`runs/r2/primary_match/changes.csv`) | AL THIYBIA (`eastern:node:1013645726`) 14,442 derived (S-r1a-210) | Thebea 17,502 | +21.2 % | primary beats derived (A-screen-031) | resolved: primary |
| C-r2-002 | (continued) | Ghran (`makkah:node:6255263461`) 6,400 derived (S-makkah-009) | Ghuran 6,803 | +6.3 % | as above (tier `arabic skeleton`, size inside the IQR band) | resolved: primary |
| C-r2-002 | (continued) | Ghutti (`al_jouf:node:1236744649`) 2,048 grid | Ghata 6,653 | +224.9 % | C-r2-001 | resolved: primary |
| C-r2-002 | (continued) | Al Ghuwaybah (`eastern:node:11870738714`) 8,880 grid | Alghawibuh 5,139 | −42.1 % | grid allocation error (back-test, A-screen-039); relay bridge S-eastern-001 | resolved: primary |

## R3 (31 Oct 2026; logged by INTEGRATE_R3 from the r3 track notes)

Sources: `docs/sources/r3-cal.csv` (also in `docs/sources/index.csv`); notes in `cities/ksa/assumptions/demand_calibration.yaml` (target ids named below); rule A-demand-038. Grade A = GASTAT table, grade B = relayed by press. CP4 (Tariq, 31 Oct 2026) asks R4 to log every further TGA vs GASTAT conflict here.

| id | item | value A | value B | difference | explanation | status |
|---|---|---|---|---|---|---|
| C-r3-001 | intercity rail passengers 2025 (HHR + East + North), national | GASTAT Railway Transport Statistics 2025, Table 1-1: 10,938,371 (8,529,112 + 1,482,367 + 926,892; S-r3-cal-001, grade A) | TGA quarterly data summed by Argaam: 11.7 M (S-r3-cal-009, grade B, secondary) | +7.0 % (B vs A) | the gap sits in Q1 and Q2 (C-r3-002); Q3 and Q4 agree. Cause not stated by either publisher | resolved for the model: GASTAT used (A-demand-038); TGA kept as an unused target (`rail-intercity-pax-2025-tga-argaam`, `usable: false`) |
| C-r3-002 | intercity rail passengers, Q1 and Q2 2025 (TGA quarters vs GASTAT monthly Table 1-2 summed by quarter) | GASTAT: Q1 2,963,988, Q2 2,369,691 (sum 5,333,679); Q3 2,701,695 and Q4 2,902,997 (S-r3-cal-001) | TGA/Argaam: Q1 3.4 M, Q2 2.7 M (as recorded in the target note; the quarters are read from the Argaam series behind S-r3-cal-008/009 and are not registered as separate source rows: unverified); Q3 2.70 M, Q4 2.9 M (S-r3-cal-008, S-r3-cal-009) | Q1 + Q2: about +0.77 M (B − A); Q3, Q4: agree | the r3 track called this the "TGA Q1–Q2" conflict; the brief's addendum lists it as "TGA Q1–Q2 bus vs GASTAT", but the recorded figures are rail (no TGA Q1 2025 bus figure was found, A-demand-039). Possible causes (not verified): revisions after the TGA release, a scope difference (for example a metro or Al Mashaaer service counted in TGA's intercity line), or quarter boundaries | open: R4 to read the TGA bulletins for Q1–Q2 2025 if published |
| C-r3-003 | intercity bus passengers, TGA quarterly 2025 vs GASTAT Land Transport Statistics | GASTAT: about 4.1 M in 2023 (search-engine extraction, PDF returned 404) and 39.1 M in 2022 (via Argaam); 9.86 M in 2021 (S-r3-cal-024, unverified/secondary): a definitional break between editions | TGA 2025: Q2 958,000 + Q3 905,000 + Q4 884,000 = 2,747,000 (three quarters; S-r3-cal-020…022, secondary); Q1 2025 not found | not comparable (different years and scopes); no GASTAT 2025 bus figure is open | GASTAT's 2022 figure likely counts a wider scope (for example Umrah and non-scheduled coaches) than TGA's scheduled intercity count; not verified | open: the bus target stays TGA Q2–Q4 (A-demand-039) and bus stays `uncalibrated` (CP4-1a); R4 recalibrates against observed data |

## R4 (1 Nov 2026, R4 builder): TGA vs GASTAT in the calibration tables, and the pilgrim tables

| id | quantity | value A | value B | difference | resolution |
|---|---|---|---|---|---|
| C-r4-tga-001 | intercity rail passengers by line, Q3 2025 | GASTAT Table 1-2 (data: TGA), Jul-Sep summed: HHR 2,072,148, East 378,446, North 251,101 | TGA Q3 2025 via Argaam: HHR 2.07 M, East 0.38 M, North 0.25 M (S-r3-cal-008, secondary) | agree to the rounding of the relayed figures | checked, no conflict; the model uses GASTAT (grade A primary table) |
| C-r4-tga-002 | intercity rail passengers by line, Q4 2025 | GASTAT Table 1-2, Oct-Dec summed: HHR 2,300,521, East 367,579, North 234,897 | TGA Q4 2025 via Argaam: HHR 2.30 M, East 0.37 M, North 0.23 M (S-r3-cal-009, secondary) | agree to rounding | checked, no conflict; GASTAT used |
| C-r4-tga-003 | intercity rail passengers, Q1 and Q2 2025 | GASTAT Table 1-2: Q1 2,963,988, Q2 2,369,691 | TGA/Argaam Q1 3.4 M, Q2 2.7 M (as recorded in C-r3-002; unverified) | about +0.77 M (TGA higher) | open (C-r3-002 carried): no TGA Q1/Q2 2025 bulletin was read in R4; GASTAT used because it is the primary annual table and its Q3/Q4 match TGA exactly (C-r4-tga-001/002) |
| C-r4-tga-004 | all rail passengers incl. intracity, 2025 | GASTAT Table 1-2 total: 156,370,185 | Argaam's sum of the TGA quarters: 157.9 M (S-r3-cal-009, secondary) | +1.0 % | not used for calibration (context only, intracity outside the model); GASTAT recorded |
| C-r4-tga-005 | Riyadh Metro passengers, Q3 2025 | GASTAT Table 1-2, Jul-Sep: 25,209,058 | TGA via Argaam: 25.2 M (S-r3-cal-008) | agree to rounding | checked, no conflict; intracity, not a model target |
| C-r4-tga-006 | intercity rail 2025 national total | GASTAT 10,938,371 (S-r3-cal-001) | TGA/Argaam 11.7 M (S-r3-cal-009) | +7.0 % | as C-r3-001 (the whole gap sits in Q1-Q2, C-r4-tga-003); GASTAT used (A-demand-038) |
| C-r4-tga-007 | intercity bus passengers, 2022 | GASTAT Land Transport Statistics 2022 edition via Argaam: 39.1 M (S-r3-cal-024, unverified) | TGA/PTA route-month dataset as analysed by Alhawiti and Alghuson (2026): 4.39 M in 2022 (S-soc-021, peer-reviewed abstract) | about 8.9 times | open: different scopes (GASTAT likely counts Umrah and non-scheduled coaches); the model's bus target stays TGA Q2-Q4 2025 (A-demand-039), whose scheduled-service scope matches the bus nodes rule (A-r4-bus-002) |
| C-r4-tga-008 | intercity bus passengers, Q2 2025 by region | no GASTAT comparator (no 2025 GASTAT bus table is open) | TGA via Argaam: 958,000 national, Makkah 226,890, Riyadh 222,960, Eastern 144,970 ... (S-r3-cal-020) | not comparable | no conflict to resolve; the national figure enters the Q2-Q4 target (A-demand-039); the regional split is unused |
| C-r4-tga-009 | North Line passengers, Q3 2026 | no GASTAT 2026 table yet | TGA via Asharq Al-Awsat: 258,600 (S-hail-004) | not comparable | outside the 2025 calibration year; recorded only |
| C-r4-tga-010 | SAR-operated networks, 2024 (SAR statement, not TGA) | GASTAT intercity 2024: 11,590,197 (S-r3-cal-001) | SAR via Argaam: 13.7 M across its networks (S-r3-cal-006) | +18.2 % | scope: SAR's networks probably include the Al Mashaaer metro (as in its 2023 statement, S-r3-cal-007); GASTAT used |
| C-r4-intl-001 | foreign Umrah performers, Q1 2024 | GASTAT Q1 2024 workbook, Table 9 (Jan-Mar): 5,893,474 | 5,794,564 'PDF text' (prompts/R4.md and the pilgrims README); the Q1 2024 bulletin PDF in the folder prints 5,893,474 ('The total number of external Umrah performers was 5,893,474 in Q1 of 2024'), and 5,794,564 appears in none of the 44 files (pdftotext search, 1 Nov 2026) | +1.7 % (table vs the brief's text figure) | the table is used (prompts/R4.md); both logged; the text figure is not reproducible from the files in hand (unverified). Enters only the 2024 series, not the 2025 segment |
| C-r4-intl-002 | foreign Umrah performers, Q2 2025 | Umrah Statistics Q2 2025 EN.pdf and the Q2 workbook (Table 1.10): 1,405,116; upload stamp 9 Aug 2026 (URL t=1786339722854), workbook modified 6 Aug 2026 | Umrah Statistics for Q2 - 2025 - EN.pdf: 1,324,418; upload stamp 19 Nov 2025 (URL t=1763544957806); the pilgrims README calls this file the revised one | -5.7 % (earlier vs later upload) | the later release (1,405,116) is used as the revised one (prompts/R4.md 'use the revised release'), 2025 total 18,033,038; 1,324,418 (total 17,952,340) is the sensitivity. The README's labelling looks reversed: flagged for Tariq (CP5). **CLOSED (R5, 3 Nov 2026, CP5 decision H5):** the most recent official dated release is the 9 Aug 2026 file (PDF CreationDate 9 Aug 2026; the earlier file's is 19 Nov 2025), so 1,405,116 is the value of record (S-r5-h5-001; superseded release S-r5-h5-002). The two files differ in value but not in date order, so this is a revision, not a conflict between two releases of uncertain standing; no Tariq question needed |
| C-r4-intl-003 | airport split of foreign arrivals at KAIA vs PMIA | Umrah 1440-1442 AH pooled shares of the two airports: KAIA 69.7 %, PMIA 30.3 % (computed, runs/intl/split-s1) | Hajj 1443 / 2022 incoming pilgrim flights: KAIA 2,450 (65.6 %), PMIA 1,287 (34.4 %) (Hajj_Statistics_2022 Table 10) | KAIA share 4.1 points higher in the Umrah split | cross-check only (A-intl-002): flights are not passengers; the Umrah shares stay the assumed constant (A-intl-001) until a dated row arrives in intl_airport_split.yaml |
| C-fixhhr-001 | HHR KAIA airport branch length | S-002 (Wikipedia lead, secondary): 3.75 km airport branch (449.2 km main line) | OSM track from the junction (21.6234465 N, 39.215395 E; main way 629481003 meets branch way 868371679) to the KAIA station node: 6.69 km (`cities/ksa/lines/geojson/hhr.geojson` part `branch`, FIX_HHR_JEDDAH); straight line junction to KAIA about 5.9 km | +78 % (OSM vs S-002) | open. The OSM branch is followed by a visible track on Sentinel-2 (visual check, Copernicus Sentinel-2 L2A scene S2B_37QED_20261027, 6 Nov 2026; window `sentinel-2-l2a-cogs-hhr_kaia_branch`), and no shorter connection to the main line exists in the OSM graph, so 3.75 km cannot be a junction-to-terminal track distance on this layout. Possible readings (unverified): a different start point, one track only of a partly separated section, or an error in the secondary source. The geometry keeps the OSM length; no km-post or published figure uses the branch length (`docs/network.md` §HHR geometry). Needs a SAR/HHR route description. Left open by Tariq, 6 Nov 2026 (FIX_HHR_REROUTE): the 3.75 km note in `hhr.yaml` is unchanged; the drawn branch stays the 6.69 km OSM track. |
