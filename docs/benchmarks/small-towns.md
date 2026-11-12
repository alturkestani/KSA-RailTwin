> **Document version:** docs/benchmarks/small-towns.md v0.1 | 31 Oct 2026 | Author: benchmarks-researcher | Status: draft

# Small towns and intermediate stations on high-speed lines: did they gain, stay unchanged, or lose?

Cross-cutting file for W5 (source-id code `st`). The country dossiers hold system facts; this file gathers the empirical studies on intermediate and peripheral stations. Converted money values: none needed here (no cost figures in this file). Status: draft, 31 Oct 2026.

## Short answer

The evidence is mixed. The clearest peer-reviewed or audit findings on in-between and peripheral places are negative or null. The European Court of Auditors found no clear regeneration effect at 15 of its 18 audited stations[^S-bench-st-014]. Koster, Tabuchi and Thisse report a sizable employment decrease in in-between Shinkansen municipalities[^S-bench-st-001]. Qin reports GDP and GDP-per-capita falls in peripheral Chinese counties on upgraded lines[^S-bench-st-032].

The positive findings are real but narrower. They are mostly for GDP, prices or migration, not for jobs at the stop. Examples: about 8.5% higher GDP on average in three German counties with intermediate stops[^S-bench-st-030]; a higher in-migration effect for KTX stations outside the Seoul area[^S-bench-st-043]; and residential price rises near the Reggio Emilia Mediopadana station[^S-bench-st-051].

No study read measures station ridership against a matched non-station baseline. None measures population, jobs or land value for a small town against a matched control in a form that supports a planning number. The answer to "did they gain" therefore depends on the system, the outcome, the distance to the large city and where the station sits.

## 1. Method note

- **Source base.** Section 8 of the seven country dossiers (Japan, France, Spain, Germany, China, South Korea, Italy) was the starting point. Most sources cited there were re-opened in this pass (the exceptions are listed below), and the leads named in the brief were searched (Koster et al. 2022; Hayakawa et al.; Ahlfeldt and Feddersen; Qin 2017; Zheng and Kahn 2013; Garmendia and Ureña; Bazin et al.; Facchinetti-Mannone; Chen and Hall; Vickerman 2015; Blum, Haynes and Karlsson 1997). Taiwan, the UK (Ashford) and Naples Afragola were added. Searches were run on 31 Oct 2026.
- **Evidence rules.** Each figure and quote was read on a page or PDF opened in this pass; the PDFs are in `logs/r1b/pdf/small-towns/`. Quotes are 25 words or fewer and were checked by machine against the extracted text of that page or PDF (67 quote rows, 0 mismatches). Where a PDF prints a decimal point as a colon, the value is recorded as printed and read as a decimal; the same paper uses "8:5%" for 8.5%, which the SERC abstract prints as 8.5%[^S-bench-st-030].
- **What "intermediate" means here.** A station or municipality on a high-speed line between the principal endpoints, not one of the large cities at the ends. "Peripheral" follows the French usage ("gares TGV périphériques"): a station outside a town centre. No source read applies a common population threshold for a "small town". The studies classify places by travel-time band (UK), by county or municipality (China, Japan, Spain, Taiwan), or by station position (France, Italy). Each study's own unit is kept.
- **Direction.** Recorded as +, 0, − or mixed, as the study states it. Where a study gives no sign, the entry says so.
- **Grades** (benchmark-dossier): A = official or audit (European Court of Auditors); B = peer-reviewed journal article or book chapter (abstract read where the full text is paywalled); C = working paper, conference paper, operator research slides, association or NGO report, World Bank review and secondary citations. Working papers are graded C because the version read is not peer-reviewed; this is a judgement for the coordinator (see Escalations). No grade D source is used for any figure.
- **Not opened, so not used for any figure.** VoxEU column on Shinkansen intermediate places (HTTP 403). The published Ahlfeldt and Feddersen article (Journal of Economic Geography; the page was blocked). The PNAS version of Zheng and Kahn (blocked; the IGC working-paper copy with the same PNAS-format text was read instead). The Crozet and Dumont 2011 interview (HAL bot check). Ureña (2009) and Garmendia, Ribalaygua and Ureña (2012), both in *Cities* (repository record and search results only). Chen and Haynes (2019), cited via the World Bank. Lin, Feng and Huang (2008) on Taiwan (search summary only). The Berkeley slide used in the earlier Germany dossier (the download was not a PDF).
- **The "Bernard et al." Shinkansen lead.** Not confirmed. The only "Bernard et al. (2019)" in the RIETI paper is a production-networks paper cited there for a 25 km cut-off; it is not a station study and is not cited for any finding here.
- **The 10 to 40% Shinkansen range.** The earlier Japan dossier cites a 10 to 40% employment effect from the blocked VoxEU column and a search summary. It is not used in this file.

## 2. Systems

### 2.1 Shinkansen (Japan)

Summary. The one peer-reviewed study of in-between municipalities reads negative. The RIETI reduced-form estimates for station areas are positive: population density is higher by 9.1% in the main specification[^S-bench-st-004] and stays positive at 3.5% when the three largest metropolitan areas are excluded[^S-bench-st-007]. The authors flag selection bias. No station-level ridership study of an intermediate Shinkansen stop was found.

- **Koster, Tabuchi and Thisse (2022), *Journal of Economic Geography* 22(4): 711–753.** Grade B (abstract read; full text paywalled). Method: a spatial model of firm location with long-haul economies, estimated on Shinkansen data. Sample: Japan's Shinkansen; the abstract gives no years or municipality count[^S-bench-st-001]. Outcome: employment in "in-between" municipalities connected to the line. Direction: − ("a sizable decrease in employment")[^S-bench-st-001]. The abstract gives no percentage and does not define "in-between".
- **Hayakawa, Koster, Tabuchi and Thisse (2021), RIETI Discussion Paper 21-E-003.** Grade C (working paper). Two parts.
  - Counterfactual model: network extensions "may have large effects (up to a 30% increase in employment)" on connected municipalities, "although the effects are smaller for places with higher fixed costs"[^S-bench-st-002]. A model result, not an observed outcome.
  - Reduced form (Appendix B.2). A municipality counts as having a station if it is within 25 km[^S-bench-st-009]; municipality fixed effects; quadratic trends in the main column. Population density rises 9.1% in the main column[^S-bench-st-004] (printed "9:1%"), 4.1% in the sample of places with a station or planned station[^S-bench-st-005], and 3.5% when the three largest metropolitan areas are excluded[^S-bench-st-007]. Employment density rises 3.3% in the same sample as 4.1%[^S-bench-st-006]. Excluding the metropolitan areas, the employment effect is 2% and "too imprecise to be statistically signi…cant" (printed ligature)[^S-bench-st-008].
  - Conflict within the paper: the Section 2.4 summary gives the density effect as "varies from 2 to 4%"[^S-bench-st-003], which does not match the 9.1% in the main column. Both are recorded; see Escalations.
  - Access: a station within 25 km is associated with about 13% lower average rail travel time[^S-bench-st-009]. This is accessibility, not an outcome.
  - The authors caution that stations may have been built "in areas that grow for other reasons"[^S-bench-st-010], and that stations were opened in areas that "already attracted population"[^S-bench-st-063].
  - Direction: + for station-area density in the reduced form, with selection caveats; the employment effect is not significant once metropolitan areas are excluded.
- **Yoo, Kumagai, Kawasaki, Hong, Zhang, Shimamura and Managi (2022), RIETI Discussion Paper 22-E-060.** Grade C. Method: market-access approach on 1983–2020 data[^S-bench-st-011], with IV checks and counterfactual plans. Outcome: land prices, income and income per capita. Finding: "the economic growth due to HSR expansion of cities outside these areas is negative or statistically insignificant"[^S-bench-st-011], where "these areas" are Tokyo and other developed areas. Direction: − or 0 for non-metropolitan cities. This measures market access, not stops.
- **Sasaki, Ohashi and Ando (1997), *Annals of Regional Science* 31(1): 77–98.** Grade B. A supply-oriented regional econometric model with simulated networks. "denser Shinkansen network will not necessarily contribute to regional dispersion"[^S-bench-st-012]. A simulation, not an observed result.
- **Vickerman (1997), *Annals of Regional Science* 31(1): 21–38.** Grade B (review). Reports "evidence of increasing concentration into the main metropolitan centres"[^S-bench-st-013]. No new estimates.
- Ridership at intermediate Shinkansen stops: no reliable data found (searched: the RIETI, Koster and Yoo records above, and the IDEAS listing of *Annals of Regional Science* vol. 31, 1997, 31 Oct 2026).

### 2.2 TGV, including peripheral stations and "gares des betteraves" (France)

Summary. The best ex post evidence is an audit. It finds no clear regeneration effect at most audited stations, and one local response at a peripheral station. The academic papers are typologies or ex ante simulations: they describe weak network position and a duality between territories, but do not measure outcomes after opening.

- **The nickname.** "Gares des betteraves" is a critics' nickname for TGV stations in open countryside. The FNAUT (2008) report says it is applied "à partir de l'expérience de Haute Picardie"[^S-bench-st-023]. It is a description, not a planning category, and the sources read do not give a formal definition.
- **European Court of Auditors, Special Report 19/2018 (grade A).** Eighteen stations, two per audited line[^S-bench-st-014]. Method: expert review of change over time in jobs, property and businesses, with no counterfactual. "we saw no clear regeneration effects from 15 of the 18 stations"[^S-bench-st-014]. The one local response: the Belfort-Montbéliard opening "had encouraged shops and a hotel to open nearby"[^S-bench-st-015]. The Meuse TGV station, in open countryside, "is poorly accessible"[^S-bench-st-016].
- **Facchinetti-Mannone (2005), *Cahiers Scientifiques du Transport* 48: 45–58 (grade B; review status to confirm).** Method: graph-based nodality for twelve peripheral stations[^S-bench-st-020] (missions, stops, direct relations, reachability in under three hours). Outcome: network position, not town outcomes. Finding: peripheral stations in small and medium towns "présentent des performances nodales fort réduites et ne constituent que de simples haltes ferroviaires"[^S-bench-st-020]. Direction: − for network nodality. The data year is not stated in the article read.
- **Bazin, Beckerich, Delaplace and Masson (2006), *Cahiers Scientifiques du Transport* 49: 51–76 (grade B; ex ante).** Method: rail and road accessibility before the June 2007 opening, for Champagne-Ardenne towns. Reims centre: planned TGV journey time from Paris falls from 1h40 to 0h45[^S-bench-st-021], a reduction of "(-53 %)"[^S-bench-st-068]. Planned timetable, not an outturn. Finding: the LGV "introduira une dualité entre différents territoires de cette région"[^S-bench-st-022]. Direction: mixed, ex ante: gains for the northern towns on the line, and a possible duality for the rest.
- **FNAUT (2008), descriptive.** Grade C. An isolated station with few relations and few daily TGV stops "ne draine qu'une clientèle locale ou faiblement régionale"[^S-bench-st-024]. A description, not a count.
- **Crozet and Dumont (2011).** The interview "Les effets structurants sont un mythe" is recorded in the earlier France dossier. The HAL copy returned a bot check on 31 Oct 2026, so it is not used as evidence here.
- Verdict. The ex post audit is negative or null at 15 of 18 stations[^S-bench-st-014], with one positive local example[^S-bench-st-015]. No quantitative study with a counterfactual for a French peripheral station was found in the sources read. Ridership and land values for individual peripheral stations: no reliable data found.

### 2.3 AVE intermediate stops (Spain)

Summary. Mixed. The ECA's catchment analysis finds that some intermediate stops have too few people nearby to justify keeping them. A tourism study finds weak or no effects in smaller municipalities. A corridor study finds a gain for Ciudad Real and little for Puertollano. No Spanish study read is a station-level matched study of population or jobs.

- **European Court of Auditors (grade A).** Each intermediate stop adds an average of four to 12 minutes to a trip[^S-bench-st-017]. Some stations "do not have sufficient numbers of passengers in their immediate catchment areas"[^S-bench-st-018]. The catchment of some stations is "extremely small" (Guadalajara-Yebes, Calatayud)[^S-bench-st-026], and "there is reason to doubt the cost-efficiency and effectiveness of keeping these stations as stops on the high-speed line"[^S-bench-st-025]. Nine of the 14 audited high-speed lines lacked a sufficient passenger count in their 15- and 30-minute catchments[^S-bench-st-019]. Direction: − for these stops (an audit's assessment of catchment, not a measured impact).
- **Albalate, Campos and co-authors (2017), *Annals of Tourism Research* 65: 71–82 (grade B; abstract read).** Panel of "124 municipalities during the 2005-2012 period"[^S-bench-st-028], outcome visitors. Finding: AVE tourism effects are "in general, extremely weak or just restricted to larger cities"[^S-bench-st-027]. Direction: 0 to weak for smaller municipalities. The outcome is visitors, not residents.
- **Shen and co-authors (TRB 95th Annual Meeting paper; listed 2015-08 on the MIT record; grade C; abstract only).** Madrid–Seville corridor, 1990–2006[^S-bench-st-029], accessibility-based spatial autoregressive models. "HSR contributes to Ciudad Real with a relevant population increase, whereas it seldom benefits Puertollano"[^S-bench-st-029]. Direction: + for Ciudad Real, 0 for Puertollano. Coefficients not read.
- Cuenca and Segovia: no reliable data found (web search for impact studies, earlier pass, not repeated).
- Verdict: mixed. Two smaller cities on the same corridor diverge, and small-catchment stops are judged weak. No Spanish study read measures a station-level ridership or land-value gain against a matched control.

### 2.4 ICE Montabaur and Limburg (Germany)

- **Ahlfeldt and Feddersen, "From periphery to core: measuring agglomeration effects using high-speed rail" (LSE Research Online, SERC Discussion Paper 0172, 2015; published in *Journal of Economic Geography* 18(2): 355–390 per the LSE listing, article page not read).** Grade C (working-paper abstract read). Method: the Cologne–Frankfurt line provides exogenous variation in access to surrounding economic mass (paraphrase of the abstract)[^S-bench-st-030]. Sample: three counties with intermediate stops. Outcome: GDP. Finding: "a causal effect of about 8.5% on average of the HSR on the GDP of three counties with intermediate stops"[^S-bench-st-030]. Spillover: "declines by 50% ever 30 minutes of travel time, diminishing to 1% after about 200 minutes"[^S-bench-st-031] (printed "ever"). Direction: + for the three counties, on GDP.
- The abstract does not name the stops. The Germany dossier names Montabaur and Limburg; that naming was not re-verified here.
- Verdict: a positive GDP result for one corridor and three counties[^S-bench-st-030]. It does not test population, jobs, land values or town-level outcomes. No other German study of intermediate-stop effects was found (searched: ICE stops and regional employment, 31 Oct 2026; the results were forum posts and a municipal development document, neither used).

### 2.5 China: HSR counties, new towns and secondary cities

Summary. Mixed, and in parts negative. Upgrades that bypassed peripheral counties show losses. HSR new towns depend on station access and location. Secondary cities near megacities gain market potential.

- **Qin (2017), "'No county left behind?'", *Journal of Economic Geography* 17(3): 489–520 (grade B; abstract read; full text paywalled).** Method: quasi-experiment on counties affected by HSR upgrades of existing lines. The upgrades improved access in city nodes and bypassed peripheral counties[^S-bench-st-032]. Finding: "the affected counties on the upgraded railway lines experienced reductions in GDP and GDP per capita following the upgrade"[^S-bench-st-032]. Direction: − for bypassed peripheral counties.
- **Liu, Xu, Tian, Liu and Dong (2024), *Transport Policy* 159: 241–253 (grade B; abstract read).** Method: gradient-boosting model with SHAP explanation, for stations opened 2009–2019[^S-bench-st-034]. Findings: "travel convenience to HSR station and station location significantly enhance the development of HSR new towns"[^S-bench-st-034]; "the distances to the city center or pre-existing station exhibit negative impacts"[^S-bench-st-033]. The abstract also reports nonlinear and threshold effects; the thresholds are not in the abstract and were not read. Direction: mixed; − with distance to the centre, + with access.
- **World Bank (2019), "China's High-Speed Rail Development" (grade C; secondary citations).** "There are at least 139 cities with at least one HSR new town"[^S-bench-st-037]. Station development "contributes to about 3–13 percent of land value increase of the nearby area" (citing Chen and Haynes 2019; primary not opened)[^S-bench-st-036]. "many others failed because of the isolation from existing urban areas"[^S-bench-st-035]. Direction: + small (land value), − for many failures.
- **Ridership at intermediate centres (same World Bank report).** HSR "typically attracts 10–30 percent of the market"[^S-bench-st-038] between intermediate centres; conventional services have "many more intermediate stations, often far more conveniently located than the typical out-of-town HSR station"[^S-bench-st-039]. Direction: limited for intermediate centres.
- **Zheng and Kahn (2013), PNAS (grade B; the IGC working-paper copy, which has the PNAS-format text, was read).** Method: market potential and city real-estate prices along megacity-linked bullet-train routes. "We document a robust positive correlation between city growth in market potential and city growth in real estate prices"[^S-bench-st-041]. The gain is largest "for the secondary cities close to the megacities"[^S-bench-st-040]. Direction: + for secondary cities near megacities. The outcome is market potential and property prices, not population.
- Verdict: mixed to negative for peripheral and intermediate counties; positive for secondary cities within reach of a megacity and for well-accessed new towns. Ridership at intermediate centres is limited.

### 2.6 KTX "straw effect" (South Korea)

Summary. The studies disagree, and the disagreement is informative. A 2018 regression reports more in-migration outside the capital area. An earlier review finds no acceptable evidence of a straw effect. An accessibility study finds gains concentrated along the corridor. A station-pair forecast check finds the Cheonan-Asan segment close to forecast in the first year.

- **Heo, Kim and Yoo (2018), *Journal of the Korea Planning Association* (국토계획) 53(4): 107–122 (grade B; abstract read).** Method: multiple regression on 2000–2016 municipal population movements[^S-bench-st-042], with KTX-opening and station-location terms. Finding: "the net migrating population influx had risen by 3.70% after the beginning of the KTX operation"[^S-bench-st-042]. Higher where the station was outside the Seoul Metropolitan Area ("higher by 12.37%")[^S-bench-st-043], in non-urban places ("by 5.96%")[^S-bench-st-064], and in designated Innovative Cities ("by 2.91%")[^S-bench-st-065]. Direction: + for in-migration, larger outside the capital area. The abstract does not count stations or towns, and it is an observational regression, not a station-level causal design.
- **Heo (2010), *Journal of Urban Administration* 23(4): 59–74 (grade C; review-type article; abstract read).** "the straw effects of KTX have, based on the some indicators and the existing studies, no acceptable evidence so far"[^S-bench-st-044]. Direction: 0 (no evidence found). The same first author reports the 2018 result above from later data.
- **Kim and Sultana (2015), *Journal of Transport Geography* 45: 48–61 (grade B; abstract read).** Accessibility by extension stage, 2004–2018[^S-bench-st-045]. "the spatial equity is degenerated by the extension in 2010/2011 as the improvement of accessibility has been concentrated in cities along the primary HSR corridor"[^S-bench-st-045]. For the 2018 extension, "the relative degree of accessibility improvement will not be large enough for increasing the spatial equity of accessibility"[^S-bench-st-066]. Direction: mixed; more cities gain access, but the gains sit on the corridor.
- **Oh In-Tack (2005), Korean Society for Railway proceedings (grade C).** Seoul–Cheonan-Asan segment, first year (2004): forecast 2,467 and actual 2,230 per day, "90.4" per cent of forecast[^S-bench-st-046]. This is segment demand, not catchment demand, for one year. The paper does not test town outcomes.
- Station-area outcomes at Cheonan-Asan and other intermediate stops: no reliable data found (Korean-language searches on station-area development and vacancy, earlier pass; the results were property and marketing items).
- Verdict: mixed. One grade B regression points to in-migration outside the capital; one review finds no evidence of a straw effect; the accessibility study finds corridor-concentrated gains.

### 2.7 Italy: Reggio Emilia AV Mediopadana and Naples Afragola

Summary. One intermediate station has a peer-reviewed price study and an operator study. The academic study finds residential price gains and no commercial gain. The operator's index study finds small positive changes in an area that was already growing. Neither measures ridership or jobs, and both cover one station.

- Mediopadana "opened in 2013 as the only intermediate stop on the Milan–Bologna high-speed line"[^S-bench-st-047] (FS Research Centre slides).
- **Bottasso, Conti, Fiduccia, Robbiano and Tartaglia (2025), Springer book chapter (grade B; abstract read, full text paywalled).** Method: difference-in-differences on Italian housing-market (OMI) data, exploiting the quasi-random station location. Finding: residential prices, "price increases ranging between 2 and 6%", in areas 20–30 km or 15–30 minutes from the station[^S-bench-st-051]. Commercial property: "commercial properties saw minimal or no price increases"[^S-bench-st-052]. Direction: + residential; 0 commercial.
- **FS Research Centre (Cerullo and co-authors, 2025), conference slides (grade C; operator's own research).** Method: an urban-development index on a hexagonal grid, with a difference-in-differences across isochrones. "increases of 4.5% and 1.2% are observed respectively"[^S-bench-st-048] for the 15-minute walk-or-cycle and 30-minute cycle bands. Pre-trend: "the area was already experiencing growth before the station was built"[^S-bench-st-049]. The operator writes that "Mediopadana acted as a catalyst for urbanization"[^S-bench-st-050]. Direction: small +, with a pre-existing trend. The index is not population or jobs, and the operator is an interested party.
- **Naples Afragola.** No ex post study of ridership, property values or local development was found (searched: Italian-language query on economic and territorial effects, 31 Oct 2026). The results were opening coverage and pre-opening projections for the whole Naples–Bari line, which are not station evidence and are not used. No reliable data found.
- **Mediopadana ridership.** No reliable data found (searched: station ridership, FS and press, 31 Oct 2026).

### 2.8 Other systems found

- **UK, Ashford (HS1), ex post case, Preston and Wall (2008), *Planning Practice & Research* 23(3): 403–422 (grade B; abstract read).** One location with long-established high-speed services. "the wider economic benefits of HST are difficult to detect, as they are swamped by external factors"[^S-bench-st-055]. The abstract adds that benefits are more likely where large accessibility changes come with supportive planning policies (paraphrase; same source). Direction: 0 (hard to detect).
- **UK, InterCity 125/225 (upgraded, not a new HSR line), Chen and Hall (2011), *Journal of Transport Geography* 19: 689–704 (grade B; abstract read).** Six London-outbound routes, 26 local authorities, 30 years[^S-bench-st-056]. Three zones, "could be classified into three influential zones, namely 1-h, 2-h, and over-2-h towns"[^S-bench-st-056]. "HST has had substantial and demonstrable effects in aiding this transition within a 2-h travel limit of London"[^S-bench-st-067]; but "the effects have not been automatic or universal"[^S-bench-st-057]. Direction: + within two hours of London; not universal. The banding is by distance to London, so it bears on the distance question only indirectly.
- **Vickerman (2015), *Journal of Transport Geography* 42: 157–165 (grade B; abstract read; review of TEN-T evidence).** "both levels of service and potential economic impacts have been much less pronounced in these intermediate areas"[^S-bench-st-053]. The same abstract calls HSR "a successful alternative to both air and road over distances of 400–600 km"[^S-bench-st-054]. That is the author's statement, not a test of the band.
- **Taiwan HSR, Tsai, Guan and Chung (2020), *Journal of Transport and Land Use* 13(1) (grade B; abstract read).** Multilevel analysis of population and employment. "HSR-based towns, on average, may experience growing population and employment"[^S-bench-st-059]; "HSR-based counties are likely to experience relatively less growth of employment in the tertiary sector"[^S-bench-st-060]; "HSR stations located in urban or suburban settings may have a more significant spatial impact"[^S-bench-st-061]. Direction: + for towns; − for tertiary employment in counties; + for urban and suburban stations. Miaoli and Chiayi station results: no reliable data found (searched: Taiwan HSR station-area studies, 31 Oct 2026). Lin, Feng and Huang (2008) was seen in a search summary only and is not used.
- **Blum, Haynes and Karlsson (1997), *Annals of Regional Science* 31(1): 1–20 (grade C; conceptual introduction).** No empirical result. "High-speed trains could be used to solve two different accessibility problems"[^S-bench-st-058]. Cited for framing only.

## 3. Summary table

| system | study | method | sample | outcome | direction | grade | source |
|---|---|---|---|---|---|---|---|
| Shinkansen | Koster, Tabuchi, Thisse (2022) | spatial model | Japan Shinkansen (abstract gives no years) | employment, in-between municipalities | − | B | [^S-bench-st-001] |
| Shinkansen | Hayakawa et al. (RIETI 21-E-003) | reduced form, FE and trends; model counterfactual | stations within 25 km | population and employment density; model employment | + (9.1% main column; 3.5% ex-metro); model up to +30% | C | [^S-bench-st-002] [^S-bench-st-004] [^S-bench-st-007] |
| Shinkansen | Yoo et al. (RIETI 22-E-060) | market access, IV | 1983–2020 | land price, income | − or 0 outside developed areas | C | [^S-bench-st-011] |
| Shinkansen | Sasaki, Ohashi, Ando (1997) | simulation | hypothetical networks | dispersion | 0 to − | B | [^S-bench-st-012] |
| TGV | European Court of Auditors (2018) | audit review | 18 stations | regeneration | − or 0 (15 of 18); + at Belfort | A | [^S-bench-st-014] [^S-bench-st-015] |
| TGV | Facchinetti-Mannone (2005) | graph nodality | 12 peripheral stations | network position | − (structural) | B | [^S-bench-st-020] |
| TGV | Bazin et al. (2006) | ex ante accessibility | Champagne-Ardenne towns | planned journey time; duality | mixed (ex ante) | B | [^S-bench-st-021] [^S-bench-st-022] |
| AVE | European Court of Auditors (2018) | catchment audit | 14 audited lines | catchment; stop cost | − (small catchments) | A | [^S-bench-st-018] [^S-bench-st-019] [^S-bench-st-025] [^S-bench-st-026] |
| AVE | Albalate et al. (2017) | panel | 124 municipalities, 2005–2012 | visitors | 0 to weak (smaller municipalities) | B | [^S-bench-st-027] [^S-bench-st-028] |
| AVE | Shen et al. (TRB) | spatial autoregression | Madrid–Seville, 1990–2006 | population | + Ciudad Real; 0 Puertollano | C | [^S-bench-st-029] |
| ICE | Ahlfeldt and Feddersen (SERC 2015; JEG 2018) | quasi-experimental access | Cologne–Frankfurt, three counties | GDP | + (8.5% average) | C (published version not read) | [^S-bench-st-030] [^S-bench-st-031] |
| China | Qin (2017) | quasi-experiment | counties on upgraded lines | GDP, GDP per capita | − (bypassed counties) | B | [^S-bench-st-032] |
| China | Liu et al. (2024) | gradient boosting with SHAP | new HSR stations, 2009–2019 | new-town development | mixed (distance −; access +) | B | [^S-bench-st-033] [^S-bench-st-034] |
| China | World Bank (2019), citing Chen and Haynes (2019) | review; secondary citations | HSR new towns | land value; failures | + small (3–13%); − many failures | C | [^S-bench-st-035] [^S-bench-st-036] [^S-bench-st-037] |
| China | World Bank (2019), survey summary | onboard survey summary | intermediate centres | HSR share of trips | limited (10–30%) | C | [^S-bench-st-038] [^S-bench-st-039] |
| China | Zheng and Kahn (2013) | market potential, real-estate prices | megacity-linked cities | market potential; property prices | + for secondary cities near megacities | B | [^S-bench-st-040] [^S-bench-st-041] |
| South Korea | Heo, Kim, Yoo (2018) | regression, municipal migration 2000–2016 | municipalities | in-migration | + (3.70%; 12.37% outside SMA) | B | [^S-bench-st-042] [^S-bench-st-043] [^S-bench-st-064] [^S-bench-st-065] |
| South Korea | Heo (2010) | review of indicators | KTX | straw effect | 0 (no acceptable evidence) | C | [^S-bench-st-044] |
| South Korea | Kim and Sultana (2015) | accessibility model, 2004–2018 | KTX extension stages | accessibility; equity | mixed | B | [^S-bench-st-045] [^S-bench-st-066] |
| South Korea | Oh In-Tack (KSR 2005) | forecast against actual | Seoul–Cheonan-Asan segment | daily demand, 2004 | 90.4% of forecast | C | [^S-bench-st-046] |
| Italy | Bottasso et al. (2025) | difference-in-differences, OMI prices | Mediopadana | residential and commercial prices | + 2–6% residential; 0 commercial | B | [^S-bench-st-051] [^S-bench-st-052] |
| Italy | FS Research Centre (2025) | difference-in-differences, urban index | Mediopadana | urban development index | + small (4.5%, 1.2%); pre-existing trend | C | [^S-bench-st-048] [^S-bench-st-049] [^S-bench-st-050] |
| Italy | Naples Afragola | none found | — | — | no reliable data found | — | — |
| UK (Ashford) | Preston and Wall (2008) | ex post case and ex ante | Ashford | economic benefits | 0 (hard to detect) | B | [^S-bench-st-055] |
| UK (InterCity 125/225) | Chen and Hall (2011) | distance-band comparison, 30 years | six routes, 26 local authorities | local economic strength | + within 2 h; not universal | B | [^S-bench-st-056] [^S-bench-st-057] [^S-bench-st-067] |
| Taiwan | Tsai, Guan and Chung (2020) | multilevel analysis | Taiwan HSR towns and counties | population; employment | + towns; − tertiary counties; + urban stations | B | [^S-bench-st-059] [^S-bench-st-060] [^S-bench-st-061] |
| Europe (review) | Vickerman (2015) | review | TEN-T intermediate areas | service; economic impact | − (less pronounced) | B | [^S-bench-st-053] |

## 4. Where evidence is mixed or negative

Stated plainly. For in-between and peripheral places, the peer-reviewed and audit sources are negative or null in most of the cases read. The positive findings are narrower: they are about GDP (one corridor), prices (one station), migration (a regression, Korea) or market potential (secondary cities near megacities), not about jobs or ridership at the stop.

Negative or null results, listed so they are not lost in the positives:
- Japan, in-between municipalities: employment decrease[^S-bench-st-001]; growth outside Tokyo and other developed areas negative or statistically insignificant[^S-bench-st-011]; Shinkansen network not necessarily dispersing activity (simulation)[^S-bench-st-012].
- Japan, the RIETI employment estimate once metropolitan areas are excluded: 2% and not significant[^S-bench-st-008].
- France: 15 of 18 audited stations show no clear regeneration effect[^S-bench-st-014]; isolated stations draw "local or weakly regional" ridership[^S-bench-st-024].
- Spain: small-catchment stops judged cost-doubtful[^S-bench-st-025][^S-bench-st-026]; AVE tourism effects weak outside larger cities[^S-bench-st-027].
- China: bypassed peripheral counties lost GDP[^S-bench-st-032]; many HSR new towns failed[^S-bench-st-035]; HSR attracts 10–30% of trips between intermediate centres[^S-bench-st-038].
- UK (Ashford): wider benefits hard to detect[^S-bench-st-055].
- Korea: the 2010 review found no acceptable evidence of a straw effect[^S-bench-st-044]; the accessibility study finds equity gains limited for peripheral regions[^S-bench-st-066].
- Taiwan: fewer tertiary jobs in HSR-linked counties[^S-bench-st-060].

Conditions the studies name themselves:
1. **Distance to a large city.** In-between employment fell in Japan[^S-bench-st-001]; UK benefits are concentrated within two hours of London[^S-bench-st-067] and "not automatic or universal"[^S-bench-st-057]; AVE tourism effects are "restricted to larger cities"[^S-bench-st-027]; intermediate areas gain less[^S-bench-st-053].
2. **Station location relative to the town.** Distance to the centre or an existing station has negative effects on HSR new towns[^S-bench-st-033]; urban and suburban stations have a larger effect in Taiwan[^S-bench-st-061]; peripheral stations in small and medium towns are "simple haltes"[^S-bench-st-020]; the Meuse station is "poorly accessible"[^S-bench-st-016]. Heo et al. report higher in-migration for stations outside the capital area and in non-urban places[^S-bench-st-043][^S-bench-st-064]. That reads in the opposite direction to the peripheral-station findings, and the measures differ (migration, not station-area activity); it is not reconciled here.
3. **Stopping pattern and frequency.** Each intermediate stop adds four to 12 minutes[^S-bench-st-017]; some stops are "too close to each other" with too few passengers[^S-bench-st-018]; isolated stations with few daily stops draw local ridership[^S-bench-st-024].
4. **Access.** Travel convenience to the station is positive in the China new-town study[^S-bench-st-034]. The Meuse station's poor access is a finding in its own right[^S-bench-st-016].
5. **Local economy, planning and pre-trends.** Effects are smaller where fixed costs are higher[^S-bench-st-002]; supportive planning policies make benefits more likely (Preston and Wall, abstract; paraphrase, same source as 055); tertiary-sector growth is weaker in HSR-linked counties[^S-bench-st-060]. Pre-existing growth matters: Japanese stations were opened where places "already attracted population"[^S-bench-st-063]; the Mediopadana area was "already experiencing growth before the station was built"[^S-bench-st-049].

## 5. Gaps

- **Ridership.** No station-level study with a matched non-station control, for any intermediate or peripheral stop, in the sources read. Ridership evidence is limited to a first-year segment check at Cheonan-Asan[^S-bench-st-046], an audit's catchment review[^S-bench-st-019], a World Bank survey summary[^S-bench-st-038] and a descriptive FNAUT note[^S-bench-st-024].
- **Population, jobs and firms at intermediate stops.** No matched study read for Japan (only the reduced-form station estimate with selection caveats[^S-bench-st-004]), Spain, France or Italy. The Taiwan and Korea studies are regressions on municipal or county outcomes, not on stops.
- **Land values.** China (secondary citation[^S-bench-st-036]) and Italy (one station[^S-bench-st-051]) only. None read for Japan, Spain or Korea.
- **Naples Afragola.** No reliable data found.
- **Germany beyond Montabaur and Limburg.** One study (Ahlfeldt and Feddersen). No reliable data found for others.
- **Taiwan, Miaoli and Chiayi stations.** No reliable data found.
- **Spain.** Ureña (2009) on big intermediate cities and Garmendia, Ribalaygua and Ureña (2012) are bibliographic records only; their abstracts were not reachable, so no findings are used.
- **Primary sources not opened.** Chen and Haynes (2019); the Shen et al. coefficients; the Qin full text; the Liu thresholds; the Koster et al. full text; the VoxEU column; the PNAS version of Zheng and Kahn; the Ahlfeldt and Feddersen journal article; the Lin, Feng and Huang (2008) Taiwan study.
- **ECA annex.** The station-level criteria in the ECA annexes were not re-tabulated.
- **Conflicts recorded, not resolved.** (a) Hayakawa et al.: Section 2.4 gives 2–4% for density; Appendix B.2 gives 9.1% in the main column[^S-bench-st-003][^S-bench-st-004]. (b) Korea: the 2018 migration gains and the 2010 review's "no evidence" concern different outcomes and periods. (c) Italy: the operator's positive index and the academic commercial null measure different things.

## Escalations

1. **Grading of working papers.** RIETI, SERC and the IGC copy are graded C because the versions read are not peer-reviewed. Coordinator to confirm. Koster et al. (2022) is graded B from the published abstract, which was read. The Ahlfeldt and Feddersen journal article was not read, so its row stays C.
2. **Hayakawa et al. density figure.** Section 2.4 (2–4%)[^S-bench-st-003] and Appendix B.2 (9.1% main column)[^S-bench-st-004] conflict. Which figure the Japan dossier carries needs a decision after the full paper or print Table B.2 is checked.
3. **Earlier Japan dossier.** Its 10–40% employment range for Koster et al. (not verified here) comes from a blocked column and a search summary. This file does not use it. Recommend the Japan dossier keeps it marked "unverified, not used".
4. **Operator evidence.** The FS Research Centre slides come from the operator group; graded C. The coordinator decides whether the Mediopadana index may inform any KSA narrative.
5. **Heo et al. (2018) sign.** It points opposite to the peripheral-station findings. That is a question about the migration measure, not resolved here.
6. **Earlier Germany dossier claim.** The statement that the Ahlfeldt and Feddersen study makes no case for or against HSR was not re-verified (the Berkeley PDF did not download). It is not used here.

## Sources

[^S-bench-st-001]: Journal of Economic Geography (repository record, Vrije Universiteit Amsterdam), "To be connected or not to be connected? The role of long-haul economies", https://research.vu.nl/en/publications/to-be-connected-or-not-to-be-connected-the-role-of-long-haul-econ/, published 2022-07 (online 2021-12-10), accessed 2026-10-31.

[^S-bench-st-002]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-003]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-004]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-005]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-006]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-007]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-008]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-009]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-010]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-011]: RIETI (Discussion Paper 22-E-060; Kyushu University authors), "Double-Edged Trains: Economic Outcomes and Regional Disparity of High-Speed Railways", https://www.rieti.go.jp/jp/publications/dp/22e060.pdf, published 2022-06, accessed 2026-10-31.

[^S-bench-st-012]: Annals of Regional Science (IDEAS abstract record; Springer), "High-speed rail transit impact on regional systems: does the Shinkansen contribute to dispersion?", https://ideas.repec.org/a/spr/anresc/v31y1997i1p77-98.html, published 1997 (vol. 31(1), pp. 77-98), accessed 2026-10-31.

[^S-bench-st-013]: Annals of Regional Science (IDEAS abstract record), "High-speed rail in Europe: experience and issues for future development", https://ideas.repec.org/a/spr/anresc/v31y1997i1p21-38.html, published 1997 (vol. 31(1), pp. 21-38), accessed 2026-10-31.

[^S-bench-st-014]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-015]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-016]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-017]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-018]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-019]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-020]: Cahiers Scientifiques du Transport (refereed journal; review status to confirm), "La nodalité des gares TGV périphériques", https://cst.episciences.org/12036/pdf, published 2005 (CST N° 48/2005), accessed 2026-10-31.

[^S-bench-st-021]: Cahiers Scientifiques du Transport (refereed journal), "L'arrivée de la LGV en Champagne-Ardenne et la nécessaire réorganisation des rapports de proximité", https://cst.episciences.org/12042/pdf, published 2006 (CST N° 49/2006), accessed 2026-10-31.

[^S-bench-st-022]: Cahiers Scientifiques du Transport (refereed journal), "L'arrivée de la LGV en Champagne-Ardenne et la nécessaire réorganisation des rapports de proximité", https://cst.episciences.org/12042/pdf, published 2006 (CST N° 49/2006), accessed 2026-10-31.

[^S-bench-st-023]: FNAUT (association report; cover names DIACT as commissioner), "Les gares nouvelles du TGV « exurbanisées »: Fonctionnement et relation au territoire", https://fnaut.fr/uploads/2013/04/db08garestgvextra.pdf, published 2008-04 (avril 2008), accessed 2026-10-31.

[^S-bench-st-024]: FNAUT (association report), "Les gares nouvelles du TGV « exurbanisées »: Fonctionnement et relation au territoire", https://fnaut.fr/uploads/2013/04/db08garestgvextra.pdf, published 2008-04 (avril 2008), accessed 2026-10-31.

[^S-bench-st-025]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-026]: European Court of Auditors, "Special Report No 19/2018: A European high-speed rail network: not a reality but an ineffective patchwork", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018 (Special Report 19/2018), accessed 2026-10-31.

[^S-bench-st-027]: Universitat de Barcelona repository; Annals of Tourism Research 65: 71-82, "Tourism and high speed rail in Spain: Does the AVE increase local visitors?", https://diposit.ub.edu/items/d6d60933-7911-4ce6-9a54-2cf2fa6f62b7/full, published 2017 (Annals of Tourism Research vol. 65), accessed 2026-10-31.

[^S-bench-st-028]: Universitat de Barcelona repository, "Tourism and high speed rail in Spain: Does the AVE increase local visitors?", https://diposit.ub.edu/items/d6d60933-7911-4ce6-9a54-2cf2fa6f62b7/full, published 2017, accessed 2026-10-31.

[^S-bench-st-029]: TRB 95th Annual Meeting paper (MIT Mobility Initiative bibliography record), "Cross-City Comparison: Impacts of Madrid-Seville High-Speed Rail on Population Growth", https://mobility.mit.edu/biblio/shen-cross-city-comparison-impacts-madrid-seville-high-speed-rail-population, published 2015-08 (listed date), accessed 2026-10-31.

[^S-bench-st-030]: LSE Research Online (Spatial Economics Research Centre, SERCDP0172), "From periphery to core: measuring agglomeration effects using high-speed rail", https://researchonline.lse.ac.uk/id/eprint/64507, published 2015, accessed 2026-10-31.

[^S-bench-st-031]: LSE Research Online (SERCDP0172), "From periphery to core: measuring agglomeration effects using high-speed rail", https://researchonline.lse.ac.uk/id/eprint/64507, published 2015, accessed 2026-10-31.

[^S-bench-st-032]: Journal of Economic Geography (RePEc abstract record), "'No county left behind?' The distributional impact of high-speed rail upgrades in China", https://ideas.repec.org/a/oup/jecgeo/v17y2017i3p489-520..html, published 2017 (vol. 17(3), pp. 489-520), accessed 2026-10-31.

[^S-bench-st-033]: Transport Policy (RePEc abstract record), "What matters in promoting new town by High-Speed Railway station? Evidence from China", https://ideas.repec.org/a/eee/trapol/v159y2024icp241-253.html, published 2024 (vol. 159, pp. 241-253), accessed 2026-10-31.

[^S-bench-st-034]: Transport Policy (RePEc abstract record), "What matters in promoting new town by High-Speed Railway station? Evidence from China", https://ideas.repec.org/a/eee/trapol/v159y2024icp241-253.html, published 2024 (vol. 159, pp. 241-253), accessed 2026-10-31.

[^S-bench-st-035]: World Bank (International Development in Focus), "China's High-Speed Rail Development", https://documents1.worldbank.org/curated/en/933411559841476316/pdf/Chinas-High-Speed-Rail-Development.pdf, published 2019-06-06, accessed 2026-10-31.

[^S-bench-st-036]: World Bank (International Development in Focus), "China's High-Speed Rail Development", https://documents1.worldbank.org/curated/en/933411559841476316/pdf/Chinas-High-Speed-Rail-Development.pdf, published 2019-06-06, accessed 2026-10-31.

[^S-bench-st-037]: World Bank (International Development in Focus), "China's High-Speed Rail Development", https://documents1.worldbank.org/curated/en/933411559841476316/pdf/Chinas-High-Speed-Rail-Development.pdf, published 2019-06-06, accessed 2026-10-31.

[^S-bench-st-038]: World Bank (International Development in Focus), "China's High-Speed Rail Development", https://documents1.worldbank.org/curated/en/933411559841476316/pdf/Chinas-High-Speed-Rail-Development.pdf, published 2019-06-06, accessed 2026-10-31.

[^S-bench-st-039]: World Bank (International Development in Focus), "China's High-Speed Rail Development", https://documents1.worldbank.org/curated/en/933411559841476316/pdf/Chinas-High-Speed-Rail-Development.pdf, published 2019-06-06, accessed 2026-10-31.

[^S-bench-st-040]: IGC working paper C-6017-CHN-1 (copy of the Zheng and Kahn paper, PNAS format), "China's bullet trains facilitate market integration and mitigate the cost of megacity growth", https://www.theigc.org/sites/default/files/2013/02/Zheng-Khan-2013-Working-Paper.pdf, published 2013-02 (WP); PNAS 2013, accessed 2026-10-31.

[^S-bench-st-041]: IGC working paper C-6017-CHN-1, "China's bullet trains facilitate market integration and mitigate the cost of megacity growth", https://www.theigc.org/sites/default/files/2013/02/Zheng-Khan-2013-Working-Paper.pdf, published 2013-02 (WP); PNAS 2013, accessed 2026-10-31.

[^S-bench-st-042]: Korea Planning Association, 국토계획 53(4): 107-122 (repository record), "고속철도(KTX)의 입지효과 및 개통으로 인한 수도권인구집중 완화효과 분석 (Analysis of Effect of High-Speed Train (KTX) Station Location and Mitigation of Population Congestion in Seoul Metropolitan Area by KTX Operation)", https://scholarworks.bwise.kr/cau/handle/2019.sw.cau/2643?mode=full, published 2018, accessed 2026-10-31.

[^S-bench-st-043]: Korea Planning Association, 국토계획 53(4): 107-122 (repository record), "고속철도(KTX)의 입지효과 및 개통으로 인한 수도권인구집중 완화효과 분석 (Analysis of Effect of High-Speed Train (KTX) Station Location and Mitigation of Population Congestion in Seoul Metropolitan Area by KTX Operation)", https://scholarworks.bwise.kr/cau/handle/2019.sw.cau/2643?mode=full, published 2018, accessed 2026-10-31.

[^S-bench-st-044]: Korean Association for Urban Administration, Journal of Urban Administration 23(4): 59-74 (repository record), "고속철도(KTX)의 빨대효과에 대한 비판적 검토 (A Critical Review on the Straw Effects of High Speed Train)", https://scholarworks.bwise.kr/cau/handle/2019.sw.cau/34534, published 2010, accessed 2026-10-31.

[^S-bench-st-045]: Journal of Transport Geography 45: 48-61 (RePEc abstract record), "The impacts of high-speed rail extensions on accessibility and spatial equity changes in South Korea from 2004 to 2018", https://ideas.repec.org/a/eee/jotrge/v45y2015icp48-61.html, published 2015 (vol. 45), accessed 2026-10-31.

[^S-bench-st-046]: Korean Society for Railway (KSR) proceedings; author Oh In-Tack, "Comparative Analysis of Forecasted and Measured Traffic Demand for Gyung-bu High Speed Railway", https://koreascience.kr/article/CFKO200511722752495.pdf, published 2005-11-01, accessed 2026-10-31.

[^S-bench-st-047]: Ferrovie dello Stato Italiane / RFI (FS Research Centre), 5th International Symposium on HSR Socioeconomic Impacts, "High-Speed Rail as a Catalyst for High-quality urban development: Lessons from Case Studies", https://www.fsitaliane.it/content/dam/fsitaliane/Documents/centro-studi/studi-e-ricerche/2026/20250910_FSRC_HSR_Urban_Development.pdf, published 2025-09-10, accessed 2026-10-31.

[^S-bench-st-048]: Ferrovie dello Stato Italiane / RFI (FS Research Centre), "High-Speed Rail as a Catalyst for High-quality urban development: Lessons from Case Studies", https://www.fsitaliane.it/content/dam/fsitaliane/Documents/centro-studi/studi-e-ricerche/2026/20250910_FSRC_HSR_Urban_Development.pdf, published 2025-09-10, accessed 2026-10-31.

[^S-bench-st-049]: Ferrovie dello Stato Italiane / RFI (FS Research Centre), "High-Speed Rail as a Catalyst for High-quality urban development: Lessons from Case Studies", https://www.fsitaliane.it/content/dam/fsitaliane/Documents/centro-studi/studi-e-ricerche/2026/20250910_FSRC_HSR_Urban_Development.pdf, published 2025-09-10, accessed 2026-10-31.

[^S-bench-st-050]: Ferrovie dello Stato Italiane / RFI (FS Research Centre), "High-Speed Rail as a Catalyst for High-quality urban development: Lessons from Case Studies", https://www.fsitaliane.it/content/dam/fsitaliane/Documents/centro-studi/studi-e-ricerche/2026/20250910_FSRC_HSR_Urban_Development.pdf, published 2025-09-10, accessed 2026-10-31.

[^S-bench-st-051]: Springer book chapter (IDEAS abstract record), Socioeconomic Impacts of High-Speed Rail Systems, "Does the Opening of a High-Speed-Rail Station Impact House Prices? Evidence from a Quasi-Natural Experiment: Reggio Emilia", https://ideas.repec.org/h/spr/prbchp/978-3-031-82528-6_16.html, published 2025, accessed 2026-10-31.

[^S-bench-st-052]: Springer book chapter (IDEAS abstract record), "Does the Opening of a High-Speed-Rail Station Impact House Prices? Evidence from a Quasi-Natural Experiment: Reggio Emilia", https://ideas.repec.org/h/spr/prbchp/978-3-031-82528-6_16.html, published 2025, accessed 2026-10-31.

[^S-bench-st-053]: Journal of Transport Geography 42: 157-165 (Kent repository record), "High-speed rail and regional development: the case of intermediate stations", https://kar.kent.ac.uk/50469/, published 2015 (vol. 42), accessed 2026-10-31.

[^S-bench-st-054]: Journal of Transport Geography (Kent repository record), "High-speed rail and regional development: the case of intermediate stations", https://kar.kent.ac.uk/50469/, published 2015 (vol. 42), accessed 2026-10-31.

[^S-bench-st-055]: Planning Practice & Research 23(3): 403-422 (Taylor & Francis; repository record), "The ex-ante and ex-post economic and social impacts of the introduction of high-speed trains in South East England", https://researchportal.port.ac.uk/en/publications/the-ex-ante-and-ex-post-economic-and-social-impacts-of-the-introd/, published 2008, accessed 2026-10-31.

[^S-bench-st-056]: Journal of Transport Geography 19: 689-704 (RePEc abstract record), "The impacts of high-speed trains on British economic geography: a study of the UK's InterCity 125/225 and its effects", https://ideas.repec.org/a/eee/jotrge/v19y2011i4p689-704.html, published 2011, accessed 2026-10-31.

[^S-bench-st-057]: Journal of Transport Geography 19: 689-704 (RePEc abstract record), "The impacts of high-speed trains on British economic geography: a study of the UK's InterCity 125/225 and its effects", https://ideas.repec.org/a/eee/jotrge/v19y2011i4p689-704.html, published 2011, accessed 2026-10-31.

[^S-bench-st-058]: Annals of Regional Science 31(1): 1-20 (IDEAS abstract record), "Introduction to the special issue: The regional and urban effects of high-speed trains", https://ideas.repec.org/a/spr/anresc/v31y1997i1p1-20.html, published 1997, accessed 2026-10-31.

[^S-bench-st-059]: Journal of Transport and Land Use 13(1): 317-341 (Tsai, Guan and Chung), "Multilevel spatial impact analysis of high-speed rail and station placement", https://jtlu.org/index.php/jtlu/article/view/1667, published 2020, accessed 2026-10-31.

[^S-bench-st-060]: Journal of Transport and Land Use 13(1): 317-341, "Multilevel spatial impact analysis of high-speed rail and station placement", https://jtlu.org/index.php/jtlu/article/view/1667, published 2020, accessed 2026-10-31.

[^S-bench-st-061]: Journal of Transport and Land Use 13(1): 317-341, "Multilevel spatial impact analysis of high-speed rail and station placement", https://jtlu.org/index.php/jtlu/article/view/1667, published 2020, accessed 2026-10-31.

[^S-bench-st-063]: RIETI (Discussion Paper 21-E-003), "High-speed Rail and the Spatial Distribution of Economic Activity: Evidence from Japan's Shinkansen", https://www.rieti.go.jp/jp/publications/dp/21e003.pdf, published 2021-01, accessed 2026-10-31.

[^S-bench-st-064]: Korea Planning Association, 국토계획 53(4): 107-122 (repository record), "고속철도(KTX)의 입지효과 및 개통으로 인한 수도권인구집중 완화효과 분석 (Analysis of Effect of High-Speed Train (KTX) Station Location and Mitigation of Population Congestion in Seoul Metropolitan Area by KTX Operation)", https://scholarworks.bwise.kr/cau/handle/2019.sw.cau/2643?mode=full, published 2018, accessed 2026-10-31.

[^S-bench-st-065]: Korea Planning Association, 국토계획 53(4): 107-122 (repository record), "고속철도(KTX)의 입지효과 및 개통으로 인한 수도권인구집중 완화효과 분석 (Analysis of Effect of High-Speed Train (KTX) Station Location and Mitigation of Population Congestion in Seoul Metropolitan Area by KTX Operation)", https://scholarworks.bwise.kr/cau/handle/2019.sw.cau/2643?mode=full, published 2018, accessed 2026-10-31.

[^S-bench-st-066]: Journal of Transport Geography 45: 48-61 (RePEc abstract record), "The impacts of high-speed rail extensions on accessibility and spatial equity changes in South Korea from 2004 to 2018", https://ideas.repec.org/a/eee/jotrge/v45y2015icp48-61.html, published 2015 (vol. 45), accessed 2026-10-31.

[^S-bench-st-067]: Journal of Transport Geography 19: 689-704 (RePEc abstract record), "The impacts of high-speed trains on British economic geography: a study of the UK's InterCity 125/225 and its effects", https://ideas.repec.org/a/eee/jotrge/v19y2011i4p689-704.html, published 2011, accessed 2026-10-31.

[^S-bench-st-068]: Cahiers Scientifiques du Transport (refereed journal), "L'arrivée de la LGV en Champagne-Ardenne et la nécessaire réorganisation des rapports de proximité", https://cst.episciences.org/12042/pdf, published 2006 (CST N° 49/2006), accessed 2026-10-31.
