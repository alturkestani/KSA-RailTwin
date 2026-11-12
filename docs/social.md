> **Document version:** docs/social.md v0.1 | 31 Oct 2026 | Author: socio-culture-analyst A (R1d) | Status: draft

# Social and cultural evidence (W7): literature review and equity frame

Scope: decision question 6 ("how would rail change people's lives, and for whom"). Part A reviews sourced evidence per W7 topic, separating **findings** (what a source says) from **inference** (our reading). Part B sets out the distributional (equity) method for R5/R8; it contains no results. Sources are rows in `docs/sources/r1d-soc.csv` (S-soc-001 to S-soc-052); ids S-soc-300 and above belong to the survey track's `docs/sources/r1d-soc-survey.csv`; S-0nn ids are in `docs/sources/index.csv`; assumptions are in `docs/assumptions.md` (A-social-nnn), to be merged into `docs/assumptions.md`. Cultural statements are sourced or marked as hypotheses to test in the survey (`docs/survey/`). Nothing here is a survey finding: the survey is designed only and has not been fielded.

## Summary

Counts per topic include sources reused from other topics; v = verified, s = secondary, u = unverified (unverified sources may be mentioned but carry no figure into a model). The source file has 52 rows: 26 verified, 12 secondary, 14 unverified.

| # | Topic | Evidence count | Main finding (sourced) | Main gap |
|---|---|---|---|---|
| 1 | Commuting behaviour and willingness to travel | 8 (5 v, 0 s, 3 u) | Q4 2025: 46.2 % of unemployed Saudi men and 63.8 % of women accept at most 1 h of commuting (S-soc-017); in a Riyadh pre-opening SP model, 5 min less walking to a station raised Metro ridership by 22 % (S-soc-019) | no public national household travel survey; Saudi intercity mode-choice models not read (S-soc-022) |
| 2 | Heat, car culture, first/last mile in summer | 6 (6 v) | national mean daily max 41.5 °C in July (S-soc-025); safe walking access to Riyadh public transport very limited in extreme heat (S-soc-026) | seasonal ridership, car ownership by income, feeder access: no Saudi evidence found |
| 3 | Women's mobility and labour-force participation | 17 (10 v, 4 s, 3 u) | Saudi female participation 20.2 % (Q4 2018, secondary) to 34.5 % (Q4 2025); unemployment 32.5 % to 10.3 % (S-soc-007, S-soc-001, S-soc-002); series breaks 2022, 2024 (Census-2022 base), 2025; 37.7 % of surveyed women switched to driving after 2018 (S-soc-011) | effect of transport access on women's employment: no Saudi evidence found |
| 4 | Family ties, weekend, Eid, Ramadan, Hajj/Umrah travel | 7 (4 v, 2 s, 1 u) | visiting friends and relatives 40.4 % of 2025 domestic trips (S-soc-031); 166,654 internal Hajj pilgrims 2025 (S-soc-028); 25.06 M internal Umrah performers 2025 (S-soc-029) | tribal ties: no Saudi evidence found; Eid and Ramadan travel by mode: no Saudi evidence found |
| 5 | Remote and hybrid work | 3 (0 v, 1 s, 2 u) | about 190,000 registered remote workers by Q2 2025, 85 % women (S-soc-035, secondary) | share of all workers working from home or hybrid, and its effect on travel: no Saudi evidence found |
| 6 | Housing affordability and decentralisation | 3 (1 v, 1 s, 1 u) | Riyadh Region real estate prices +10.7 % y/y in Q1 2025 vs +4.3 % nationally (S-soc-038); five-year Riyadh rent-increase freeze from 25 Sep 2025 (S-soc-040, secondary) | rail effects on residential location in KSA: no Saudi evidence found; housing-cost burden by income not read |
| 7 | Regional jobs and Saudisation | 4 (3 v, 1 s, 0 u) | Saudi unemployment Q4 2025 from 4.1 % (Riyadh) to 11.7 % (Northern Borders) (S-soc-016); 50.1 % of employed Saudis in the private sector (S-soc-041) | regional employment effect of transport access: no Saudi evidence found; current Nitaqat rules not read |
| 8 | Displacement, land acquisition, heritage, route sensitivity | 8 (1 v, 3 s, 4 u) | 2025 expropriation law (M/56): market value + 20 % and damages (S-soc-043, secondary); 8 World Heritage properties with coordinates (S-soc-046) | official law text not read; displacement outcomes of Saudi rail projects: no Saudi evidence found |

## Part A. Literature review

### 1. Commuting behaviour and willingness to travel in KSA

**Findings.**
- **Official measure of willingness to commute.** The only official, recurring Saudi measure found is the Labour Force Survey question on the commuting time unemployed Saudis would accept. In Q4 2025, 46.2 % of unemployed Saudi men and 63.8 % of unemployed Saudi women would accept at most one hour; 31.6 % of men and 14.3 % of women would accept more than two hours (S-soc-017). This covers job seekers only, not the employed, and the questionnaire wording (one way or return, any mode) was not read.
- **Working hours.** Average usual weekly hours in main work, Q4 2025: Saudi men 41.5, Saudi women 39.2, non-Saudi men 48.2, non-Saudi women 48.5 (S-soc-018). This is relevant to time budgets, not a commuting measure.
- **Riyadh stated preference (before Metro opening).** The pre-opening SP study modelled car versus Metro in one neighbourhood. Walking time to the station had the largest modelled effect: in that model, 5 minutes less walking raised Metro ridership by 22 %. A 10 % fare increase reduced it by 6.9 %, and socioeconomic factors had only a marginal effect (S-soc-019, verified abstract). The scope is small (one neighbourhood), so the elasticities are not national.
- **Car dependence and pricing.** An online survey of Saudi nationals in Riyadh found more support for pricing measures framed around road safety and travel time than around congestion. Its authors describe car ownership and use in KSA as very high (S-soc-020). That is the authors' framing; the paper's own car-ownership figures were not read.
- **Observed rail use.** National rail passengers were 42.7 million (2024) and 156.4 million (2025), including urban metro; intercity rail passengers were 11.6 million and 10.9 million (index S-043, S-044, verified). The intercity bus network carried 4.39 million passengers in 2022, 91.7 % of its 2019 level (S-soc-021).
- **Intercity mode-choice evidence specific to Saudi Arabia exists but was not read.** This includes the Riyadh–Dammam SP models (S-soc-022), a Riyadh–Dammam HSR social-cost study (S-soc-023) and a 2026 book chapter on HSR in Saudi Arabia (S-soc-024). All are unverified and carry no figures.

**Inference (ours, to test).**
- H1.1: Intercity rail trips are mostly non-commuting (business, family, religious). Daily intercity commuting is likely limited to short pairs such as Makkah–Jeddah and Dammam–Riyadh outskirts. This is untested; no Saudi intercity trip-purpose split by mode was found (see §4 for the tourism-trip purposes).
- H1.2: Access and egress time probably weighs more than in-vehicle time (S-soc-019). The survey design carries an access-time attribute.

**Gaps.**
- No public national household travel survey (trip rates, purposes, commute times for the employed) was found. Nearest evidence: GASTAT LFS job-seeker commuting tolerance (S-soc-017) and city-level SP studies (S-soc-019, S-soc-020).
- Willingness to commute daily between cities: no Saudi evidence found. Nearest evidence: United Kingdom and Spain inter-urban value-of-time meta-analyses used by the survey track (`docs/sources/r1d-soc-survey.csv`, S-soc-302, S-soc-303).

Evidence count: 8 sources (5 verified, 0 secondary, 3 unverified): S-soc-017 to S-soc-024, plus index S-043/S-044 (verified, not recounted).

### 2. Heat, car culture and first/last mile in summer

**Findings.**
- **Heat exposure.** National-average daily maximum temperature (1991–2020) is 40.7 °C in June, 41.5 °C in July and 41.6 °C in August, against 21.7 °C in January (S-soc-025). These are national grid averages; coastal humidity (Jeddah, Dammam) and city values are not captured.
- **Walking access in heat.** A heat-strain study of Riyadh's new public-transport network found that safe walking access to stops and stations "remains very limited across Riyadh under extreme heat" (S-soc-026, verified abstract; safe-distance values not read). In the pre-opening Riyadh SP study, walking time to the station was the most influential attribute (S-soc-019).
- **No measured heat effect on walk valuation.** A worldwide meta-analysis found no significant difference in the walk-time multiplier between high-temperature countries and others. The authors note this was a simple dichotomy only (S-soc-027). This is weak evidence either way, not proof that heat does not matter.
- **Car dependence.** Riyadh survey authors describe car ownership and use in KSA as very high (S-soc-020, authors' framing). Women's switching to driving after 2018 added drivers to household cars (S-soc-011).

**Inference (ours, to test).**
- H2.1: In summer, the acceptable walking access distance to a station is shorter than in winter, so station catchments should be modelled with car or feeder access (park-and-ride, drop-off, feeder bus, ride-hailing) rather than walking alone. The survey should test this with a seasonal framing of the access attribute.
- H2.2: Shaded or air-conditioned access (covered walkways, feeder buses) may matter more than in-vehicle comfort for first/last-mile choice. This is a hypothesis; no Saudi measurement was found.
- Hypotheses are stated without any claim about "car culture" as a cultural trait. The evidence above concerns ownership, use and climate, not attitudes.

**Gaps.**
- Seasonal variation in public-transport ridership in KSA (summer against winter): no Saudi evidence found. Nearest evidence: none read. The GASTAT railway statistics may hold monthly passengers (to check in W8).
- Car ownership per household by region and income: not found in open sources read today (Part B data table).
- Feeder and ride-hailing access to intercity stations: no Saudi evidence found. Nearest evidence: none read in this pass.
- Heat and walking valuation: no Saudi evidence found. Nearest evidence: worldwide meta-analysis (S-soc-027) and a Riyadh heat-strain model (S-soc-026).

Evidence count: 6 sources (6 verified, 0 secondary, 0 unverified): S-soc-025 to S-soc-027 new; S-soc-019, S-soc-020 (from §1) and S-soc-011 (from §3) reused.

### 3. Women's mobility and labour-force participation since 2018

**Findings.**

Trend table: Saudi women (nationals, aged 15+), fourth quarter of each year. Values are as published by the source named in the row; the series is **not** methodologically continuous (breaks listed below the table). Derived table transcribed from GASTAT and Jadwa (credit: GASTAT Labour Force Survey).

| Quarter | Female participation rate (%) | Female unemployment rate (%) | Male unemployment rate (%) | Source | Status | Break note |
|---|---|---|---|---|---|---|
| Q4 2018 | 20.2 | 32.5 | not captured | S-soc-007 | secondary (Jadwa reporting GASTAT) | pre-2020 survey design |
| Q4 2019 | 26.0 | 30.8 | not captured | S-soc-008 | unverified (snippet; cannot carry a figure into a model) | possibly a revised series |
| Q4 2020 | 33.2 | 24.4 | 7.1 | S-soc-009 | secondary (Jadwa reporting GASTAT) | |
| Q4 2021 | 34.7 | 22.9 | 5.4 | S-soc-001, S-soc-002 | verified | CATI only (S-soc-003) |
| Q4 2022 | 35.5 | 15.7 | 4.3 | S-soc-001, S-soc-002 | verified | CAPI+CATI from Q2 2022; new population-estimate method Q2 2022 (S-soc-006) |
| Q4 2023 | 35.0 (first published 35.5) | 13.9 (first published 13.7) | 4.6 | S-soc-001, S-soc-002, S-soc-006 | verified | restated on the Census-2022 base (S-soc-005) |
| Q4 2024 | 36.0 | 11.9 | 4.3 | S-soc-001, S-soc-002 | verified | Census-2022 population base (from Q1 2024 release) |
| Q4 2025 | 34.5 | 10.3 | 5.6 | S-soc-001, S-soc-002 | verified | new questionnaire and dwelling sample from Q1 2025 (S-soc-004) |

Series breaks (sourced):
- **2024 population-base break.** GASTAT states that its Q1 2024 results followed "a reassessment of data from the fourth quarter of 2023 based on the Saudi Census 2022" (S-soc-005). The Q4 2023 figures as first published (13.7 % unemployment, 35.5 % participation) differ from the restated figures in the 2025 workbook (13.9 %, 35.0 %) (S-soc-006, S-soc-001, S-soc-002). Compare levels across this break with care.
- **Q2 2022.** A new population-estimate methodology (2021 mid-year base) and a move from telephone-only to mixed CAPI/CATI collection (S-soc-003, S-soc-006).
- **Q1 2025.** A redesigned questionnaire, a new dwelling sample on the 2022 Census frame, and face-to-face collection (S-soc-004).
- **2018–2020.** Values come from Jadwa's summaries of GASTAT releases (secondary) and one unverified snippet. GASTAT's own Q4 2018–Q4 2022 bulletins in the local cache turned out to be HTML error pages, and two direct GASTAT PDF links returned 404 today. Whether the pre-2021 figures are on the same basis as the 2021+ workbook series is **unknown**. (Example: Jadwa gives 23.2 % participation for Q2 2019, while the snippet gives 26.0 % for Q4 2019; S-soc-008.)

Regional spread, Q4 2025 (S-soc-015, S-soc-016): Saudi female participation ranges from 27.0 % (Madinah) to 42.4 % (Riyadh), and Saudi female unemployment from 6.5 % (Riyadh) to 16.3 % (Northern Borders). The regional values are in Part B, table B2.

Driving decree and mode switching:
- A royal decree reported on 26 September 2017 provided for driving licences for women, to be implemented by June 2018 (S-soc-014, unverified: snippets only; primary to find). Women could drive from 24 June 2018 (S-soc-013, secondary).
- About a year after the decree, a survey of more than 20,000 women (She Drives KSA) found that 22.7 % had switched from riding as a passenger in a household car to driving it, and 37.7 % in total had switched to driving the household car. Employed, younger (18–39), highly educated and single women were more likely to switch. Unemployed, lower-educated and lower-income women were more likely to keep their previous mode (S-soc-011, verified abstract). The sampling frame and weighting were not read, so we do not know whether these shares represent all Saudi women. A related 2022 study on women's intention to drive exists (S-soc-012, unverified; not read).
- Commuting tolerance differs by sex. In Q4 2025, 9.3 % of unemployed Saudi women would not accept work outside their area of residence and 63.8 % would accept at most one hour; for men the shares are 5.0 % and 46.2 % (S-soc-017). Jadwa's reading of the Q4 2024 survey is that 78 % of unemployed women prefer at most one hour or a job in their own area, against 53 % of men (S-soc-010, secondary).
- Jadwa attributes part of the rise in female participation to policies on access to transport and childcare (S-soc-010). That is the source's interpretation, not a measured effect. The policy programmes themselves (for example a women's commuting-support scheme) were **not** read in this pass; that is a gap.

**Inference (ours, to test).**
- H3.1: Women's tolerance of long commutes is lower than men's (S-soc-017), so the access and egress legs and the station environment may weigh more in women's mode choice. Survey attributes test this: access time, women-only or family carriage (`docs/survey/`).
- H3.2: Rail access is likely to matter more for women without a household car or a licence. The 2021 study points to the lower-income and lower-education groups (S-soc-011). Car availability by sex and income is **not available** in the open data catalogued so far (Part B).
- No causal claim is made that rail raises female participation.

**Gaps.**
- No published Saudi estimate of the effect of public-transport access on women's employment was found. Nearest evidence: no study read in this pass. Candidate to search: the international literature on transit access and female employment (for example urban studies from India or Latin America).
- GASTAT primary bulletins for Q4 2018–Q4 2020 were not read.
- Women-only or family carriage demand: no Saudi evidence found; this is a survey hypothesis.

Evidence count: 17 sources (10 verified, 4 secondary, 3 unverified): S-soc-001 to S-soc-017.

### 4. Family ties, weekend and Eid travel, Friday, Ramadan, Hajj and Umrah

**Findings.**
- **Visiting family and friends is a leading domestic travel purpose.** In 2025, visiting friends and relatives was the leading purpose of domestic tourism trips: 37.7 million tourists, 40.4 % of domestic trips, out of 93.3 million domestic tourists (S-soc-031, verified, DataSaudi). For 2024, the Ministry of Tourism split reported by Argaam was entertainment 37 %, visiting family and friends 35 %, religious 13 %, business 10 %, other 4 %, out of about 86.2 million domestic tourists (S-soc-032, secondary). "Domestic tourism" counts overnight trips, so day trips are not included.
- **Seasonality.** The 2025 monthly peak of domestic tourists was March 2025, with 9.29 million (S-soc-031). Our inference (dates to source): that month contained the end of Ramadan and Eid al-Fitr 1446H. Monthly series by purpose were not read.
- **Weekend.** The official weekend moved from Thursday–Friday to Friday–Saturday on 29 June 2013 for government and financial institutions, and for schools from 2013-14. The private-sector weekend was left to employers (S-soc-033, secondary).
- **Ramadan working hours.** For Muslims, Ramadan working hours are capped at 6 hours a day or 36 a week, against the standard 8 a day or 48 a week (S-soc-034, verified, MHRSD). This shifts peak travel times during the month.
- **Hajj 2025 (1446H).** There were 1,673,230 pilgrims. Of these, 166,654 were internal (10 %) and 1,506,576 external; 95.3 % of external pilgrims arrived by air and 4.4 % by land (S-soc-028, verified, GASTAT). Hajj is a short, fixed-date peak with a large share of non-resident travellers.
- **Umrah.** In 2025 there were 43,088,121 Umrah performers, 25,055,083 of them internal (S-soc-029, verified, DataSaudi). In December 2025, internal performers by region were highest in Makkah, Riyadh and Jazan; the page does not say whether "region" means residence or place of performance. The 2024 figures (35.68 million, 18.88 million domestic; S-soc-030) are unverified.
- **Friday.** Beyond the weekend rule, no source was read on Friday travel patterns, such as the timing of Friday prayer and its effect on train departure demand. This is a gap.

**Inference (ours, to test).**
- H4.1: Intercity rail demand has strong peaks at Eid, the summer holidays and the end of Ramadan, and weekly peaks around the Friday–Saturday weekend. Visiting family is the largest overnight purpose (S-soc-031). The capacity case should test peak-day loads, not only annual averages.
- H4.2: Internal Umrah volumes (S-soc-029) point to large domestic flows to Makkah and Madinah outside the Hajj season. These are relevant to Haramain and any Riyadh–Makkah option. No mode split was read.
- H4.3: Family group travel (several adults and children) may favour car travel because the cost per vehicle is shared, and may favour family carriages on rail. This is a survey hypothesis (party size, family carriage attribute); no Saudi evidence was found.

**Gaps.**
- **Tribal ties as a travel driver:** no Saudi evidence found in the sources read; nearest evidence: none. No statement on tribal ties is made in this study. The VFR share (S-soc-031) measures family visits, not tribal affiliation.
- Eid travel volumes by mode and corridor (road counts, air, rail): no Saudi evidence found in sources read. Nearest evidence: monthly domestic-tourism totals (S-soc-031).
- Ramadan intercity travel patterns (night travel, Makkah in the last ten nights): no Saudi evidence found in sources read. Nearest evidence: the working-hours rule (S-soc-034) and Umrah totals (S-soc-029).
- Friday travel timing: no Saudi evidence found.

Evidence count: 7 sources (4 verified, 2 secondary, 1 unverified): S-soc-028 to S-soc-034.

### 5. Remote and hybrid work

**Findings.**
- **Registered remote work is small and mostly female.** By the end of Q2 2025 there were about 190,000 remote workers, 85 % of them women (S-soc-035, secondary, MHRSD figures via the press). For scale (our arithmetic, not a source statement), this is small against total employment. National employed totals are in the GASTAT LFS; the survey track's S-soc-338 reports 18.2 million employed in Q2 2025 (secondary).
- **Programme counts are cumulative.** MHRSD also reports cumulative remote-work contracts since 2019, about 280,000 to Q3 2025, and about 115,000 remote employees in H1 2023 (S-soc-036, unverified snippet). These counts measure registered programme contracts, not the share of all workers who sometimes work from home.

**Inference (ours, to test).**
- H5.1: Registered remote work is concentrated among women (S-soc-035). It may substitute for commuting for some women whose commuting tolerance is low (S-soc-017); remote work and rail access could therefore be alternative routes to participation. Untested.
- H5.2: Hybrid work (some days in the office) changes weekly commuting frequency more than the number of commuters. For intercity rail it may enable longer, less frequent commutes (for example weekly Riyadh–Qassim). No Saudi evidence was found; this is a survey item (days per week in the workplace).

**Gaps.**
- **Share of employed people working from home or hybrid** (all workers, not only registered programme contracts): no Saudi evidence found. Nearest evidence: United States survey literature (S-soc-037, unverified; not read).
- **Effect of remote or hybrid work on intercity travel:** no Saudi evidence found. Nearest evidence: none read in this pass.
- The LFS workbook (Q4 2025) has no place-of-work table among its 44 tables (checked against its index, S-soc-001 file). A future LFS module would be the natural source.

Evidence count: 3 sources (0 verified, 1 secondary, 2 unverified): S-soc-035 to S-soc-037.

### 6. Housing affordability and decentralisation away from Riyadh and Jeddah

**Findings.**
- **Price pressure concentrated in Riyadh in early 2025.** In Q1 2025 the national real estate price index rose 4.3 % year on year, driven mainly by Riyadh Region (+10.7 %). Makkah Region rose 1.5 % and Eastern Region fell 5.5 %. Northern Borders, Al-Jouf and Najran rose 8.7 %, 8.2 % and 5.6 % (S-soc-038, verified, GASTAT). By Q4 2025 the national index was reported 0.7 % lower year on year (S-soc-039, unverified snippet).
- **Policy response in Riyadh.** From 25 September 2025, rent increases for residential and commercial properties within Riyadh's urban boundaries are frozen for five years. The aim stated in the report is to address surging rents in the capital, and the freeze may be extended to other cities (S-soc-040, secondary; primary to find).
- **Population concentration.** Census 2022 city populations (Riyadh 6.92 million, Jeddah 3.71 million) are in the project index (S-080, S-081, secondary). They describe concentration, not its trend.

**Inference (ours, to test; presented as a trade-off, without advocacy).**
- **Decentralisation versus agglomeration.** Faster intercity links can work both ways. Lower housing costs in satellite towns or secondary cities (for example Al-Kharj, Qassim, Makkah–Jeddah corridor towns) may draw households out of Riyadh or Jeddah if they can commute or work hybrid. The same links can also strengthen the pull of the largest city for jobs and services. The literature reviewed by the benchmarks track (W5) is the place to weigh this. This document takes no position on which outcome is preferable.
- H6.1: Where a rail station sits within commuting time of Riyadh, land and rent prices near the station may rise and erode the affordability gain for low-income renters (an equity risk; Part B, "who pays").

**Gaps.**
- **Rail effects on residential location or house prices in KSA:** no Saudi evidence found. Nearest evidence: international HSR and commuter-rail capitalisation studies (to be drawn from the W5 benchmark dossier; none read in this pass).
- **Rent levels and housing-cost burden by region and income** (share of income spent on housing): not read. The GASTAT household income and expenditure survey 2023 PDF returned 404 (survey track S-soc-336, unverified).
- **Migration from Riyadh and Jeddah to other regions** (internal migration flows): no source read in this pass.

Evidence count: 3 sources (1 verified, 1 secondary, 1 unverified): S-soc-038 to S-soc-040, plus index S-080/S-081 (secondary, not recounted).

### 7. Regional jobs and Saudisation

**Findings.**
- **Regional labour-market gaps (Q4 2025).** Saudi unemployment ranges from 4.1 % in Riyadh to 11.7 % in Northern Borders. Jazan (11.5 %), Asir (11.0 %), Tabuk (10.3 %) and Al-Baha (10.0 %) are also at 10 % or above (S-soc-016). Saudi participation is highest in Riyadh (56.5 %) and Eastern (53.4 %) and lowest in Madinah (41.6 %), Al-Baha (41.7 %), Jazan (41.8 %) and Asir (42.0 %) (S-soc-015). Regional values carry sampling error that the workbook does not publish.
- **Sector of employment.** In Q4 2025, 50.1 % of employed Saudis worked in the private sector and 49.2 % in the public sector. The private share for Saudi women was 65.4 %. Non-Saudis were mostly private-sector (71.5 %), and 79.7 % of employed non-Saudi women were in an "other" sector that the table does not define (S-soc-041). The Saudi private share was 46.3 % in Q1 2021 (S-soc-041, Table 3-6-2).
- **Saudisation policy.** Private-sector Saudisation rose from 19.9 % (2017) to 21.8 % (2018). Retail Saudisation stages in 2018 targeted 70 % of sales jobs (S-soc-042, secondary). Current Nitaqat rules and the current private-sector Saudi share by region were **not read** in this pass.

**Inference (ours, to test).**
- H7.1: Regions with high Saudi unemployment and low participation (Northern Borders, Jazan, Asir, Al-Baha, Tabuk) may gain most if rail widens the reachable job market. They are also the regions where a station is least likely in a demand-led network. This is the core equity tension for Part B, stated without a position.
- H7.2: Rail construction and operation jobs and their Saudisation share are a separate channel (W3/W6). No Saudi rail-workforce source was read.

**Gaps.**
- **Effect of intercity transport access on regional employment in KSA:** no Saudi evidence found. Nearest evidence: international HSR regional-economy studies (W5 benchmark dossier; none read here).
- Regional private-sector Saudisation rates (administrative data, GOSI): not read.
- Rail-sector workforce and Saudisation: no source read.

Evidence count: 4 sources (3 verified, 1 secondary, 0 unverified): S-soc-041, S-soc-042, plus S-soc-015 and S-soc-016 reused from §3.

### 8. Displacement, land acquisition, heritage sites and route sensitivity

**Findings.**
- **Land acquisition law (current).** A new Law of Expropriation of Real Estate for Public Interest and Temporary Seizure was issued by Royal Decree M/56 of 12/3/1447H (4 September 2025), approved by Council of Ministers Resolution 177. Summaries say that compensation is fair market value plus a 20 % premium and direct damages; that temporary possession is paid at rental value plus 20 % and damages; that tenants, mortgagees and usufruct holders have explicit rights; and that authorities must show state-owned land cannot meet the need before taking private land (S-soc-043, secondary, law-firm summary). The 1424H law (M/15) still governs cases whose procedures were approved before the new law took effect (S-soc-044, secondary). The reported entry-into-force date is 17 January 2026 (S-soc-045, unverified). The official text and its article numbers were **not read** (primary to find). No figure from these summaries enters a model until the text is read.
- **Heritage law.** The Antiquities, Museums and Urban Heritage Law (Royal Decree M/3, 9/1/1436H) is reported in force and amended. An amendment allows acquisition of heritage sites and adjacent land through the expropriation law. Planning schemes that contain heritage sites are reported to need heritage-authority approval (S-soc-047, unverified). The national antiquities register is reported at 12,991 sites (S-soc-048, unverified). Whether a public, geolocated register exists is **unknown**.
- **World Heritage properties.** Saudi Arabia has 8 World Heritage properties, with point coordinates in UNESCO's open dataset (CC BY-SA 4.0): Hegra (2008), At-Turaif in ad-Dir'iyah (2010), Historic Jeddah (2014), Rock Art in the Hail Region (2015), Al-Ahsa Oasis (2018), Ḥimā Cultural Area (2021), 'Uruq Bani Ma'arid (2023, natural) and Al-Faw (2024) (S-soc-046, verified). Several lie near existing or announced corridors: Historic Jeddah on the Haramain/Landbridge approach, At-Turaif near Riyadh, Al-Ahsa Oasis near the East line at Hofuf, and Hegra near possible north-west alignments. This proximity is our inference, to be measured in R1a/R2 with the coordinates; it is not a finding.
- **Displacement precedent (urban redevelopment, not rail).** In 2022, Jeddah Governorate's Undeveloped Neighborhoods Committee began paying SR 1 billion in compensation to the first owners of demolished properties in 26 districts (18.5 million m²). Owners without legal ownership documents were compensated for the building only (S-soc-049, secondary). Amnesty International reported more than half a million residents affected and said foreign nationals were excluded from compensation (S-soc-050, unverified; NGO figures). The official count and the NGO count are not reconciled here. Both are reported, attributed, and neither is endorsed.

**Inference (ours, route sensitivity; method for R1a/R2/R8).**
- Route options should carry screening flags: inside or within a buffer of a World Heritage property (S-soc-046); crossing a registered antiquities site (data availability unknown, S-soc-048); through dense residential land (displacement); and through informal-tenure areas, where the 2022 precedent shows compensation may depend on title documents (S-soc-049). Buffer distances are assumptions (A-social register), not rules.
- Expropriation cost belongs in the W3 cost register (land), using the market value + 20 % rule only after the law text is read. Who bears displacement costs, especially renters and expatriate occupants without title, belongs in Part B ("who pays").

**Gaps.**
- **Displacement and resettlement outcomes of rail projects in KSA** (for example the Haramain HSR or Riyadh Metro land take): no Saudi evidence found. Nearest evidence: none read in this pass; the World Bank Environmental and Social Standard 5 (land acquisition) is a candidate method reference, not read.
- **Heritage impact assessments for Saudi rail:** no Saudi evidence found.
- **Official text of the 2025 expropriation law:** not read (BOE/Umm al-Qura); the summaries are secondary.

Evidence count: 8 sources (1 verified, 3 secondary, 4 unverified): S-soc-043 to S-soc-050.

## Part B. Equity frame (method only, no results)

Purpose: define how R5 (CBA) and R8 (report and dashboard) will show **who gains, who pays and who is left out** for each corridor family and programme, by region and by income band. This section contains **no results**. Any later output carries the label **"synthetic demand, uncalibrated: scenario comparison, not a forecast"**, and benefits and costs are shown as P10/P50/P90 ranges (rules 3 and 6).

**Standard followed.** DfT TAG Unit A4.2 (S-soc-051). It sets out a three-step process (screening, assessment, appraisal) and eight indicators: user benefits, noise, air quality, accidents, security, severance, accessibility, personal affordability. User benefits by income group are compared as each group's **share of benefits** against its **share of the population** in the impact area. The comparison is graded on TAG's seven-point scale. Concentration curves and indices (S-soc-052) are an optional summary across income. Departures from TAG are stated in B4.

#### B1. Steps, indicators and data

| Step | What is done | Indicator(s) | Data needed | Availability (per `docs/data-sources.md` and this review) |
|---|---|---|---|---|
| 1. Screening | For each corridor family, flag which of the eight TAG indicators could have distributional effects, and which social groups are exposed | screening proforma (yes/no per indicator) | corridor geometry (W1/W2), station list (line YAML), settlement register | corridor geometry: R1a/R2 (in progress); settlement register: pilot (`docs/coverage.md`, secondary populations) |
| 2a. Impact area | Define the area that gains access (station catchments by access mode and season) and the area that bears costs (alignment buffer, land take, severance) | catchment population; population within the alignment buffer | OSM road graph (access skims); station locations; buffer widths (assumption) | OSM GCC extract: verified (R0). Summer-catchment adjustment: assumption (§2, A-social-001) |
| 2b. Social groups | Count groups in each zone: region, governorate, Saudi/non-Saudi, sex, age, income band, car availability, licence holding | group shares per zone | Census 2022 tables by governorate (nationality, sex, age); income by region/governorate; car ownership by household | Census 2022 tables: **unverified** (portal DNS failure, S-090 in index); income by region: **not available** (HIES 2023 PDF 404; survey track S-soc-336 unverified); car ownership by household: **not available**; licence holding by sex: **not available** |
| 2c. Labour-market context | Regional participation and unemployment by sex and nationality | LFPR, unemployment (Table B2) | GASTAT LFS regional tables | **available** (S-soc-015, S-soc-016, verified, Q4 2025) |
| 2d. Amenities | Hospitals, universities, religious sites, heritage sites reached or affected | count of amenities per catchment | OSM POIs; UNESCO WHS points (S-soc-046); antiquities register | OSM: verified; WHS: verified (CC BY-SA, share-alike flag); antiquities register: **unknown** (S-soc-048) |
| 3a. User benefits by group | Allocate modelled generalised-cost savings (W8 + W4) to origin zones, then to groups by zone shares | share of benefits vs share of population, by region and by income band (quintile or national bands) | W8 zone-level demand and generalised costs (R3); W4 benefits (R5); group shares from 2b | W8/W4 outputs: **not yet produced** (R3/R5). Income bands per zone: **not available** (see B4 proxy) |
| 3b. Who pays | (i) Fiscal: public funding share, without assuming any tax incidence; (ii) users: fares as a share of income per band (affordability); (iii) local: land take, displacement, severance, noise near the line | fare-to-income ratio by band; households/population within the land-take buffer; tenure (owner/renter/no title) | fares (line YAML; survey priors); income by band; buildings in the buffer (OSM buildings); tenure data | fares: secondary (survey track S-soc-318 to S-soc-321); income by band: **not available**; OSM buildings: available (completeness unknown); tenure by area: **not available**; expropriation compensation rule: secondary (S-soc-043) |
| 3c. Who is left out | Zones and groups with no gain: (i) towns without a station within the access threshold; (ii) freight-only corridors (passenger benefit zero by construction); (iii) non-drivers and households without a car where station access needs a car; (iv) women where access conditions deter use (§3 hypotheses); (v) expatriates (fare and access; data by nationality); (vi) low-income bands | population and group shares outside every catchment, by region; freight-only km and population along them | W2 coverage table (`docs/coverage.md`); line YAML `service:` freight/passenger; catchments from 2a | W2 coverage: pilot draft (R2 completes); freight/passenger flags: line YAML (R1a); car availability: **not available** |
| 3d. Grading and reporting | TAG seven-point grade per indicator and group; tables by region (13 rows) and by income band (5 rows or national bands); matched baseline per rule 6 | grade; P10/P50/P90 of benefit shares | outputs of 3a–3c with Monte Carlo draws (R5) | method only; R5/R8 |

#### B2. Regional labour-market baseline (input descriptor, not a model result)

Derived table transcribed from GASTAT LFS Q4 2025 (S-soc-015, S-soc-016). Saudis aged 15+. Sampling errors are not published.

| Region | Saudi participation, total (%) | Saudi female participation (%) | Saudi unemployment, total (%) | Saudi female unemployment (%) |
|---|---|---|---|---|
| Riyadh | 56.5 | 42.4 | 4.1 | 6.5 |
| Makkah | 48.3 | 33.0 | 9.1 | 12.7 |
| Madinah | 41.6 | 27.0 | 8.7 | 12.1 |
| Qassim | 48.2 | 34.7 | 6.9 | 11.0 |
| Eastern Province | 53.4 | 35.9 | 5.8 | 8.4 |
| Asir | 42.0 | 27.6 | 11.0 | 15.1 |
| Tabuk | 45.0 | 28.2 | 10.3 | 14.1 |
| Hail | 45.3 | 31.1 | 7.9 | 12.7 |
| Northern Borders | 46.2 | 32.0 | 11.7 | 16.3 |
| Jazan | 41.8 | 28.7 | 11.5 | 15.1 |
| Najran | 50.6 | 37.0 | 6.2 | 7.3 |
| Al-Baha | 41.7 | 27.5 | 10.0 | 15.3 |
| Al-Jouf | 48.0 | 35.1 | 8.1 | 11.9 |
| Kingdom | 49.5 | 34.5 | 7.2 | 10.3 |

#### B3. Output tables to be produced in R5/R8 (templates; empty by design)

Table B3a, by region (13 rows + Kingdom). Columns: population (Census 2022); share of population in any station catchment; share of national user benefits (P10/P50/P90); share of population; benefit-share ÷ population-share; population in towns of 10,000+ without a station (count of towns); freight-only route-km; population within the land-take buffer; TAG grade.

Table B3b, by income band (5 rows). Columns: share of population; share of user benefits (P10/P50/P90); fare-to-income ratio on the median trip; share without car access in catchments; TAG grade. **Blocked** until an income-by-zone source exists (B4).

Table B3c, by group (Saudi women, Saudi men, non-Saudi women, non-Saudi men, under 25, 65+, no car in household). Columns: share of population; share of benefits; access-mode constraint flags.

#### B4. Departures from TAG and open data problems

- **No small-area deprivation index.** TAG uses the English Index of Multiple Deprivation (S-soc-051); no Saudi equivalent was found. Proposed proxy, to be decided at the checkpoint: income band by region from HIES 2023 if its tables are published (unverified), else nationality × region using LFS shares, with the limit stated. Wage-by-nationality figures are secondary (survey track S-soc-338).
- **Non-residents.** Hajj and Umrah pilgrims from abroad (S-soc-028, S-soc-029) gain user benefits but are not residents. Report them as a separate row rather than spreading them into regional income bands.
- **Expatriate residents** are part of the population (Census 2022), but income, car and licence data by nationality and region were not found. Report them as a group with an explicit data gap.
- **Tax incidence of public funding** is not modelled. "Who pays" shows fiscal exposure (W6/R7) as a total, not by income band.
- **Displacement.** Compensation rules are taken from secondary summaries until the 2025 law text is read (S-soc-043). Renters and occupants without title are flagged, following the 2022 Jeddah precedent (S-soc-049).

Evidence count (Part B method): 2 new sources (2 verified): S-soc-051, S-soc-052; data rows reused from Part A.
