> **Document version:** docs/benchmarks/france.md v0.2 | 31 Oct 2026 | Author: benchmarks-researcher | Status: draft

# France: TGV / LGV (SNCF Voyageurs; SNCF Réseau)

Scope and method. Research from open sources on 31 Oct 2026. Documents were downloaded to `logs/r1b/pdf/france/` and read with `pdftotext -layout`; table cells that have no text layer were read from rendered page images and are marked as such in the citation record. Figures are in the currency and price basis of each source. Nominal values are kept as printed. Converted values: see README.md. Metric rows are in `cities/ksa/benchmarks/metrics-france.csv` (81 rows); overrun candidates are in `cities/ksa/benchmarks/overruns-france.csv` (27 rows). Evidence is mostly grade A (European Court of Auditors, the French environmental inspectorate IGEDD and its predecessor CGEDD, the ministry). Two academic papers (grade B) and one interview (grade C) are used for the small-town section. The national audit court's 2014 report was not read (see section 10).

## 1. System facts

| metric | value | unit | price year | grade | source |
|---|---|---|---|---|---|
| Completed HSR network, all lines (ECA Annex IV) | 2,548 | km | n/a (ECA cut-off c.2017; year not printed) | A | [^S-bench-fr-017] |
| Completed and in construction (same ECA row) | 2,628 | km | n/a | A | [^S-bench-fr-017] |
| LGV SEA new line, Tours-Bordeaux | 302 | km | n/a | A | [^S-bench-fr-025] |
| LGV SEA service start | July 2017 | date | n/a | A | [^S-bench-fr-024] |
| LGV SEA time saved, Paris-Montparnasse to Bordeaux | 51 | min | n/a | A | [^S-bench-fr-024] |
| LGV SEA direct TGV journey after opening | 2h03 | h:mm | n/a | A | [^S-bench-fr-024] |
| LGV Est Européenne, total length (both phases) | 406 | km | n/a | A | [^S-bench-fr-002] |
| LGV Est phase 1 opening (Table 17) | 2007 | year | n/a | A | [^S-bench-fr-095] |
| LGV Est phase 2 opening (Table 17) | 2016 | year | n/a | A | [^S-bench-fr-096] |
| Rhin-Rhône, length and opening | 138 km; 2011 | km; year | n/a | A | [^S-bench-fr-001] [^S-bench-fr-006] |
| LGV Méditerranée commercial service | June 2001 | date | n/a | A | [^S-bench-fr-069] |
| LGV Rhône-Alpes opening (as planned at the public inquiry) | 1994 | year | n/a | A | [^S-bench-fr-064] |
| Operators and infrastructure manager | SNCF Voyageurs (trains); SNCF Réseau (infrastructure, formerly RFF) | text | n/a | A | [^S-bench-fr-030] |
| SEA delivery model | concession to LISEA, awarded 2011; tolls to 2061 | text | n/a | A | [^S-bench-fr-031] |
| Earlier lines delivery model | direct public project management by RFF / SNCF Réseau | text | n/a | A | [^S-bench-fr-034] |
| SEA public subsidy, cumulative | 2.8 bn EUR 2017 (38 %) | EUR bn 2017 | 2017 | A | [^S-bench-fr-030] |
| SEA axis passengers, 2019 | 18.6 | million | n/a | A | [^S-bench-fr-029] |
| LGV Est phase 1 passengers, 2009 | 12 | million | n/a | A | [^S-bench-fr-055] |
| Completed HSR lines above 9 million passengers a year, 2016 | 3 of 7 audited completed lines | count | n/a | A | [^S-bench-fr-012] |

The ECA's calculated KPI row gives 15 million EUR per km of completed HSR for France. It is a network-wide average calculated by the ECA, not a line cost ([^S-bench-fr-018]).

## 2. Cost per km

Price basis differs by source and is stated in each row. Converted values: see README.md.

**(a) IGEDD 2025 Table 17, LGV lines, real cost in million EUR 2023 per LGV-only km.** The table gives forecast and real cost for ten French LGVs in M EUR 2023 (IGEDD restatement, INSEE IPC hors tabac). Real cost per km runs from 6.0 (LN 1, opened 1981/83) to 28.3 (LGV SEA, 2017). The IGEDD text calls the SEA figure the highest cost per km of French LGVs known ([^S-bench-fr-098]).

| line (opening) | LGV-only km | forecast, M EUR 2023 | real, M EUR 2023 | real / forecast | real M EUR 2023 per km | source |
|---|---|---|---|---|---|---|
| LN 1 Sud-Est (1981/83) | 381 | 2,271 | 2,291 | 101 % | 6.0 | [^S-bench-fr-089] |
| LN 2 Atlantique (1989/90) | 271 | 2,128 | 2,906 | 137 % | 10.7 | [^S-bench-fr-090] |
| LN 3 Nord (1994/96) | 326 | 4,528 | 4,556 | 101 % | 14.0 | [^S-bench-fr-091] |
| Interconnexion IdF (1994/96) | 97 | 1,740 | 1,909 | 110 % | 19.7 | [^S-bench-fr-092] |
| LN 4 Rhône-Alpes (1992/94) | 113 | 1,738 | 1,723 | 99 % | 15.3 | [^S-bench-fr-093] |
| LN 5 Méditerranée (2001) | 218 | 5,743 | 5,838 | 102 % | 26.8 | [^S-bench-fr-094] |
| LN 6 LGV Est phase 1 (2007) | 300 | 4,848 | 5,779 | 119 % | 19.3 | [^S-bench-fr-095] |
| LN 8 LGV Est phase 2 (2016) | 106 | 2,633 | 2,228 | 85 % | 21.0 | [^S-bench-fr-096] |
| LN 7 LGV Rhin-Rhône phase 1 (2011) | 137 | 2,796 | 3,533 | 126 % | 25.7 | [^S-bench-fr-097] |
| LGV SEA (2017) | 302 | 8,179 | 8,533 | 104 % | 28.3 | [^S-bench-fr-098] |

Computed check: the per-km values equal real cost divided by LGV-only km, to rounding (for example 8,533 / 302 = 28.3). The IGEDD text gives the SEA forecast as 8,176 M EUR 2017 "prix total" incl. accompanying works, while the table prints 8,179 M EUR 2023 for the forecast; both are kept (see Escalations). No terrain or tunnel share is stated in the sources read.

**(b) ECA SR19/2018, nominal, audit cut-off not printed.** Per km, initial and final estimates for the two French lines the ECA audited (lengths as in its Table 5). ECA states that all figures are nominal and prints no price year; the price year is recorded as unknown.

| line | km | initial cost per km, M EUR | final cost per km, M EUR | source |
|---|---|---|---|---|
| LGV Est Européenne | 406 | 12.9 | 16.5 | [^S-bench-fr-002] |
| Rhin-Rhône | 138 | 14.9 | 18.8 | [^S-bench-fr-001] |

**(c) Project-level and phase-level figures.** Civil-works project of LGV Est phase 2 (Baudrecourt-Strasbourg), real cost divided by the 106 km stretch: 20.1 M EUR per km, nominal ([^S-bench-fr-007]; computed 2,130 / 106). Rhin-Rhône Branche Est, real cost divided by 137.5 km: 19 M EUR per km, nominal ([^S-bench-fr-008]; computed 2,610 / 137.5). The IGEDD 2025 LGV Est phase 2 opinion gives cost per km of 15.5 for phase 1 and 19 for phase 2 with no price basis printed in the extract ([^S-bench-fr-053] [^S-bench-fr-052]).

**Range.** On the French numbers read, real cost per LGV km runs from 6.0 to 28.3 M EUR 2023 across the ten Table 17 lines. The same corridors appear in other sources at different values: LGV Est at 16.5 (nominal, ECA final) and 19.3 and 21.0 (M EUR 2023, Table 17, phases 1 and 2); Rhin-Rhône at 18.8 (nominal, ECA final) and 25.7 (M EUR 2023, Table 17). These differ in price year, perimeter and whether financing costs are included. They are not reconciled here (see Escalations).

**Totals.** LGV SEA: real 8,533 M EUR 2023 in Table 17 ([^S-bench-fr-098]); 8,176 M EUR 2017 total initial investment price including accompanying works, which the IGEDD states as 9.4 bn EUR 2023 ([^S-bench-fr-039]); the concession's ex post accounting investment, which the IGEDD calls at most 7,151 M EUR 2017 including financing costs during works ([^S-bench-fr-038]). LGV Est phase 2: 1,971 M EUR in current euros and 1,804 M EUR at June 2008 prices, against a 2,010 M EUR forecast ([^S-bench-fr-047] [^S-bench-fr-048] [^S-bench-fr-049]). LGV Est phase 1: reconstituted 4,655 M EUR 2009 ([^S-bench-fr-051]), a figure the IGEDD quotes from the 2013 CGEDD report.

Coordinator note (31 Oct 2026): the European Court of Auditors states its cost figures in nominal terms. One price-year rule applies to every dossier: the report year 2018 (assumption A-bench-002), so converted values are a lower bound in 2025 prices. Converted values: see `README.md`.

## 3. Ridership vs forecast

Ratios are outturn over forecast, computed from printed values unless stated.

| line and outturn year | forecast | outturn | ratio | source |
|---|---|---|---|---|
| LGV EE phase 1, 2009 | 11.5 m (DAM 2002 expectation for phase 1, implied) | 12 m | 1.04 | [^S-bench-fr-055] [^S-bench-fr-056] |
| LGV SEA, 2019 | 19.4 m and 20.6 m (public inquiries 2005 and 2007; "à la mise en service", year not fixed) | 18.6 m | 0.90 to 0.96 | [^S-bench-fr-043] [^S-bench-fr-029] |
| Savoie-Dauphiné + Midi axes, 1996 | 17.5 m (DAM) | 14.8 m | 0.85 | [^S-bench-fr-065] |
| Savoie-Dauphiné + Midi axes, 2000 | 19.3 m (DAM) | 18.6 m | 0.96 | [^S-bench-fr-065] |
| LGV EE phase 2 traffic gain, 2019 | 0.934 m gain (ex ante) | 1.14 to 1.24 m gain (ex post) | 1.22 to 1.33 (gain ratio) | [^S-bench-fr-059] [^S-bench-fr-058] |

Points on method, as the sources state them:

- For SEA, the IGEDD attributes the overestimate "notamment" to an overestimate of air travel, so that less diversion from air to rail was realised than forecast ([^S-bench-fr-028]; the air diversion figures are in section 5). The IGEDD also says the quantitative analysis is insufficient because SNCF does not publish origin-destination passenger data ([^S-bench-fr-028]). It describes the LISEA ex post traffic study as partial and contradictory ([^S-bench-fr-028]).
- For LGV EE phase 2 the IGEDD says the mix of diverted and induced traffic differed between the approval file and the ex post study, and that the induced share in the approval file was "très surestimée à l'origine" ([^S-bench-fr-058]).
- The ECA benchmark of 9 million passengers a year (6 million in the opening year) is cited by the ECA from academic and institutional sources, not a French finding ([^S-bench-fr-011]). In 2016, three of the seven completed lines it audited carried more than 9 million ([^S-bench-fr-012]). The Commission's reply disputes the use of a minimum passenger volume, saying it "may pre-empt project solutions" that suit territorial needs ([^S-bench-fr-082]).

## 4. Farebox recovery / operating ratio

No reliable data found for a French HSR farebox recovery or operating ratio, by line or for the TGV network (searched: ECA SR19/2018, 2026-10-31; IGEDD 2025 SEA and 2025 LGV EE phase 2 opinions, 2026-10-31; the ART annual rail market report and SNCF Voyageurs 2025 results, searched on 2026-10-31 but seen only as search snippets, not read).

What the opened sources do say:

- The IGEDD says the SEA ex post assessment has no financial rate of return: "L'estimation du taux de rentabilite financiere (TRI financier) est manquante", and the statutory requirement is for one ([^S-bench-fr-033]).
- SNCF Voyageurs, in its own statement as reported by the IGEDD, said its balance on the LGV Est phase 2 was negative after the post-2019 change in infrastructure tolls ([^S-bench-fr-083]). That is a company statement, not an audited figure.
- The IGEDD states that the SEA socio-economic return depends mainly on user time savings ([^S-bench-fr-026]; the ex post value of 6% against 8% ex ante, [^S-bench-fr-027]).

The Cour des comptes 2014 report on high-speed rail may hold TGV economics beyond these sources. It was not read (section 10).

## 5. Thresholds: population density, city sizes, and the 200-800 km band

**Density and city-size thresholds.** No reliable data found for a numeric population-density or city-size threshold for French HSR (searched: ECA SR19/2018 paragraphs 70 to 81 and annexes; IGEDD 2008 and 2025 opinions; Facchinetti-Mannone 2005; Bazin et al. 2006; 2026-10-31). The only numeric benchmark found is ridership (9 million a year, [^S-bench-fr-011]). The ECA tests catchments at 15 and 30 minutes by car, and reports that nine of 14 audited lines and cross-border connections lacked enough people in those catchments for HSR to succeed ([^S-bench-fr-013]). That is a method, not a threshold.

**The 200-800 km band is a hypothesis.** The sources read do not test a 200 km or 800 km boundary. They contain distance-specific comparisons for a few city pairs of about 450 to 700 km, and a time threshold for air dominance. The evidence is set out for and against:

Evidence the ECA reads as favouring rail on city-centre-to-city-centre trips of about 450 to 700 km (ECA Table 6, travel-agent search, read from the rendered page; the search date is not printed):

- Madrid-Barcelona, 607 to 698 km: HSR door-to-door 6:00 to 8:20 at 159 to 181 EUR; air 6:30 to 8:00 at 227 to 253 EUR; car 10:40 to 18:20 at 138 to 190 EUR ([^S-bench-fr-021]). The ECA states that the air-rail modal split changed from 85:15 to 38:62 by 2016, after the 2008 opening ([^S-bench-fr-020]). This is a Spanish case, cited here because it is the in-band example in the ECA set.
- Paris-Strasbourg, 466 to 548 km: HSR 5:10 to 5:30 at 158 to 165 EUR; car 8:40 to 12:20 at 44 to 79 EUR; air and conventional rail shown as not available ([^S-bench-fr-022]).
- Berlin-Munich, 587 to 654 km: HSR 8:30 to 10:30 at 66 EUR; air 6:30 to 8:00 at 146 EUR; car 10:00 to 16:40 at 95 to 142 EUR ([^S-bench-fr-023]).

Evidence on air dominance and on air substitution in France:

- In the IGEDD's Paris-origin analysis (2005 data, from Campos and Gagnepain 2009), air is the most-used mode beyond 3 to 4 hours of rail journey ([^S-bench-fr-045]). Air block times vary little with distance, so air's relative advantage grows with distance ([^S-bench-fr-046]). This is a time threshold, not a distance threshold.
- The SEA ex ante forecast attributed 51 % of gains to air diversion under a fare-rise scenario ([^S-bench-fr-041]); the ex post model attributes 10 % ([^S-bench-fr-040]). The IGEDD heading reads "more than four times less air diversion than forecast" ([^S-bench-fr-042]).
- On the 2000-era Savoie-Dauphiné and Midi axes, air diversion was about 10 % of air traffic concerned and 23 % of new traffic in the ex post study ([^S-bench-fr-067]).
- The ECA states that high-speed rail in France costs most per kilometre travelled for business and leisure users in its sample ([^S-bench-fr-019]), a point on fares, not on mode share.

Reading: the cited 2005 French data show air dominating rail beyond about three to four hours of rail journey time, and the SEA forecast of diversion from air was high against the ex post model. The Spanish table shows large substitution on a 600 to 700 km route. Neither source establishes a distance band. The 200 to 800 km band stays a hypothesis for R1c.

## 6. Station spacing, timetable and stopping patterns

- Station spacing (ECA Annex VII): LGV Est Paris-Strasbourg, 441 km with 5 stations, average distance between stations 110 km (shortest 68 km, longest 137 km) ([^S-bench-fr-009]). LGV Rhin-Rhône Dijon-Mulhouse, 205 km with 4 stations, average 68 km (shortest 46 km, longest 82 km) ([^S-bench-fr-010]).
- Across the audited lines the ECA reports four stations on Rhin-Rhône and 15 on Berlin-Munich, with distances from 26 to 253 km ([^S-bench-fr-081]).
- Stopping time penalty (ECA Annex VII, the ECA's own calculation): on LGV Est, the most direct trip takes 106 min and the least direct 119 min; 7 min per intermediate stop ([^S-bench-fr-009]). On Rhin-Rhône, 62 and 74 min, with 6 min per intermediate stop ([^S-bench-fr-010]).
- Services: the ECA says the two audited French lines "had very few connections" in frequency ([^S-bench-fr-084]). The IGEDD says the post-SEA reorganisation of SNCF Voyageurs services was criticised for fewer or insufficient frequencies ([^S-bench-fr-028]).
- SEA: the direct TGV Paris-Bordeaux journey is 2h03 ([^S-bench-fr-024]); the IGEDD does not extract the SEA intermediate-stop pattern in the sources read.

## 7. Overruns (cost, schedule) and renegotiations

**Capital cost, ECA audit (nominal).** LGV Est Européenne: final against initial estimate +28.1 % ([^S-bench-fr-002]). Rhin-Rhône: +26.1 % ([^S-bench-fr-001]). The ECA states that all audited HSR lines had overruns above 25 % ([^S-bench-fr-086]). At project level, the Rhin-Rhône Branche Est project is +12.9 % (computed, [^S-bench-fr-008]) and the LGV Est phase 2 civil-works project is -9.0 % (computed, [^S-bench-fr-007]). The ECA also records a French CBA with a negative economic NPV accepted for EU co-funding for the Rhin-Rhône East section ([^S-bench-fr-085]).

**Capital cost, IGEDD (M EUR 2023, computed from printed ratios).** Real against forecast across the ten Table 17 lines: LN 1 +1 %, LN 2 +37 %, LN 3 +1 %, Interconnexion IdF +10 %, LN 4 -1 %, LN 5 +2 %, LN 6 +19 %, LN 8 -15 %, LN 7 +26 %, LGV SEA +4 % ([^S-bench-fr-089] to [^S-bench-fr-097], [^S-bench-fr-098]; the rows are in `overruns-france.csv`). The range is -15 % to +37 %, and the lines most above forecast are the 1989/90 Atlantic line and the 2011 Rhin-Rhône phase 1.

**Other lines and phases.**

- LGV Est phase 1: +19.2 % (3,905 to 4,655 M EUR 2009, as quoted by the IGEDD from the 2013 CGEDD report) ([^S-bench-fr-051]). The IGEDD says phase 1's ex post socio-economic return was 3.7 %, below the 8 % minimum used at the time of the public inquiry and the 4 % threshold in force since 2005 ([^S-bench-fr-060]).
- LGV Est phase 2: about 10 % below the approval forecast; computed -10.2 % (1,804 against 2,010 M EUR, both June 2008 prices) ([^S-bench-fr-050] [^S-bench-fr-049] [^S-bench-fr-048]). The main explanation given, as the IGEDD reports it, is the post-2008 construction market ([^S-bench-fr-050]).
- LGV Rhône-Alpes: infrastructure cost 1,261 M EUR, 22 % above the public-inquiry cost ([^S-bench-fr-063]). Its ex post 20-year economic IRR was 6.3 % against 10.4 % at the DUP and 9 % at the DAM ([^S-bench-fr-068]).
- LGV Méditerranée: infrastructure 4,362 M EUR 2003 against 4,202 M EUR forecast in the DAM for the project as built, computed +3.8 %; the DAM's price basis is not printed ([^S-bench-fr-070] [^S-bench-fr-071]). Realisation ran about three years longer than planned, 12 years in all ([^S-bench-fr-072]).
- LGV SEA (concession): ex post 7,151 M EUR 2017 against the 2007 estimate indexed to 2017 (7,203), computed -0.7 % ([^S-bench-fr-036] [^S-bench-fr-038]), and against the 2011 revised estimate (7,446), computed -4.0 % ([^S-bench-fr-037]). The 7,151 figure includes financing costs during works, so these are upper bounds. The IGEDD says the concession protected taxpayers from budget overruns and that delivery ran without delay, but that competitive tendering did not reduce the cost per km, which the IGEDD says reached a record level ([^S-bench-fr-032] [^S-bench-fr-031]). It names cost drivers: 320 km/h specifications, environmental precautions, and public-works prices rising about three times faster than general inflation over a decade ([^S-bench-fr-032]).

**Schedule.** LGV Est: ECA Table 2 gives 24 years from planning (1992) to operation (2016), with 14 years of works ([^S-bench-fr-005]). Rhin-Rhône: 19 years from planning (1992) to operation (2011), with 5 years of works ([^S-bench-fr-006]). LGV Méditerranée ran about 3 years late ([^S-bench-fr-072]). LGV Rhône-Alpes opened as planned in 1994 ([^S-bench-fr-064]). SEA opened without delay per the concession ([^S-bench-fr-031]).

**Renegotiations.** No renegotiation of a French HSR concession appears in the sources read. The SEA concession transferred cost risk to LISEA ([^S-bench-fr-032]). Public subsidy on SEA is 38 % of cost, against 60 % for the LGV Est first section and 80 % for its second, and 75 % for Rhin-Rhône, as the IGEDD reports them; the IGEDD marks the 80 % figure as subject to validation ([^S-bench-fr-035] [^S-bench-fr-087] [^S-bench-fr-088]).

## 8. Small-town evidence: did intermediate and peripheral stations gain?

Evidence is mixed to negative for French peripheral and intermediate TGV stations. No quantitative, peer-reviewed ex post study of the regeneration effect of a French peripheral station was found in the sources read. The rows are summarised below with method, sample, finding and grade.

| study | method | sample | finding as published | grade |
|---|---|---|---|---|
| ECA SR19/2018 paras 75 to 77 | expert review of 18 audited stations (two per line): access, services, size, connections, and change in jobs, property and businesses over time | 18 stations, two per audited line (ECA para 75); French examples: Meuse TGV, Lorraine TGV, Besançon Franche-Comté, Belfort-Montbéliard | "we saw no clear regeneration effects from 15 of the 18 stations"; Meuse TGV "poorly accessible", isolated in the countryside; Belfort-Montbéliard opening drew shops and a hotel ([^S-bench-fr-015] [^S-bench-fr-014]) | A |
| Facchinetti-Mannone 2005, Cahiers Scientifiques du Transport 48 | graph-based nodality analysis of twelve peripheral TGV stations: missions, stops, relations, share of nodes reachable under 3 hours | twelve peripheral stations, e.g. Vendôme (1 mission, 11 stops), Haute-Picardie (4 missions, 17 stops, 147 relations) | peripheral stations in small and medium towns have "des performances nodales fort réduites" and are mostly simple stops; only Méditerranée and Île-de-France interconnection stations work as real rail nodes ([^S-bench-fr-074] [^S-bench-fr-075] [^S-bench-fr-076]) | B (refereed journal; review status to confirm); the data year is not stated in the extract read |
| Bazin, Beckerich, Delaplace and Masson 2006, Cahiers Scientifiques du Transport 49 | ex ante accessibility simulation of rail and road times for Champagne-Ardenne towns, before the June 2007 opening | Reims, Châlons, Vitry-le-François, Charleville-Mézières, Rethel, Sedan; rail times from SNCF data, road from Michelin | Reims centre 1h40 to 0h45 (-53 %) by TGV; the LGV "est susceptible de favoriser l'amélioration de l'accessibilité à Paris de seulement quelques villes" and creates "une dualité" between territories ([^S-bench-fr-077] [^S-bench-fr-078]) | B (refereed journal) but ex ante, not an ex post evaluation |
| Crozet and Dumont 2011 interview, Ville, Rail & Transports 525 | expert interview | none (opinion) | "Les effets structurants sont un mythe" ([^S-bench-fr-073]) | C (interview, not a study) |

Reading. The ex post evidence is the ECA's expert review: no clear regeneration effect at 15 of 18 stations, with one station (Belfort-Montbéliard) showing local shops and a hotel after opening. The academic papers are typologies and ex ante simulations, and do not measure employment or property effects after opening. The interview is an opinion that rejects structuring effects for the region as a whole. The French evidence does not show regeneration at most peripheral stations. It does not measure losses either, and no quantitative study was found that measures either effect. The term "gare des betteraves" from the brief is not used in the sources read, so the critique is recorded here only as the ECA and the academic papers describe peripheral stations.

## 9. Lessons for KSA (evidence-based, non-advocacy)

These are what the sources read support. They are not a recommendation to build or not to build.

- The French cost record is wide: real cost per LGV km runs from 6.0 to 28.3 M EUR 2023 across the ten Table 17 lines. The lowest is the 1981/83 LN 1 line and the highest the 2017 SEA ([^S-bench-fr-098]). The ECA found overruns above 25 % on every audited HSR line in its EU-wide sample ([^S-bench-fr-086]). The IGEDD says the cost per km of the SEA is a record ([^S-bench-fr-032]).
- SEA's 2019 traffic was 4 to 10 % below the public-inquiry forecasts, and the air-diversion share in the forecast (51 % of gains) was about five times the ex post share (10 %) ([^S-bench-fr-043] [^S-bench-fr-041] [^S-bench-fr-040]). The IGEDD ties the ridership gap to the air assumption ([^S-bench-fr-028]). On LGV Est phase 1 the outturn was 4 % above its expectation ([^S-bench-fr-055]). Results differ by line and by the forecast year used.
- Appraisal records matter for learning: the IGEDD found SEA's ex post financial return missing ([^S-bench-fr-033]), and the SNCF data on origin-destination passengers not public ([^S-bench-fr-028]). The ECA found CBAs used as a formality and a negative-NPV project accepted ([^S-bench-fr-085]).
- Cost-risk allocation in the SEA concession protected the public purse from overruns ([^S-bench-fr-032]), while the public subsidy share was lower than on earlier lines ([^S-bench-fr-035]). The sources do not show whether the concession cost the public less overall; the IGEDD says the financial appraisal that would show it is missing ([^S-bench-fr-033]).
- Intermediate and peripheral stations: the ECA's expert review and the academic papers do not show regeneration at most stations, and access was the binding problem for some ([^S-bench-fr-015] [^S-bench-fr-014]). The Facchinetti-Mannone conclusion ties a station's nodal performance to its place in the network and the size of the town it serves ([^S-bench-fr-076]).
- Time and distance: French evidence puts air dominance at about three to four hours of rail journey ([^S-bench-fr-045]). Madrid-Barcelona shows strong rail share at 600-plus km ([^S-bench-fr-020]). Neither establishes a distance band.

## 10. Gaps: "no reliable data found" items

- Farebox recovery and operating ratio for TGV or LGV lines: no reliable data found (searched: ECA SR19/2018; IGEDD 2025 SEA and EE2 opinions; ART annual rail reports and SNCF Voyageurs 2025 results, which were seen only as search snippets on 2026-10-31, not read).
- Density and city-size thresholds for French HSR: no reliable data found (searched: as in section 5).
- Cour des comptes 2014 report, "La grande vitesse ferroviaire: un modèle porté au-delà de sa pertinence": NOT READ. The copy surfaced by search returned HTTP 404 on WebFetch, and the ccomptes.fr PDF was not opened. No figure in this dossier comes from it ([^S-bench-fr-080]).
- Ex post line-level ridership and operating accounts for SEA and LGV Est: SNCF does not publish origin-destination passenger data (as the IGEDD states, [^S-bench-fr-028]).
- Quantitative ex post studies of French peripheral-station effects: none found in the sources read. Further searches (HAL, episciences, Cahiers Scientifiques du Transport, Revue d'économie régionale et urbaine) were not completed within this session; a search snippet lists a French version of the Bazin et al. paper in the Revue d'économie régionale et urbaine (vol. 62), not read.
- Downloads not used: the IGEDD 2025 Marseille-Aix phase 1 opinion (a regional line, not HSR); the 2016 road-bilan A432 opinion (a motorway, not rail); the 2001 CGPC TGV Atlantique bilan (not read in detail); the SNCF Réseau 2025 LGV EE phase 2 assessment (not read beyond the IGEDD opinion); the 2013 CGEDD 009145-01 report on LGV Est phase 1, whose local copy is an error page and not usable. Its figures are cited only through the IGEDD 2025 opinion.
- Terrain and tunnel shares for French lines: not stated in the sources read.
- Price-year conversion to SAR: done by `rail.benchmarks summarise`. Converted values: see README.md.

## Escalations

1. Per-km conflict for the same corridor. LGV Est phases 1 and 2: IGEDD 2025 EE2 opinion gives 15.5 and 19 (price basis not printed); Table 17 gives 19.3 and 21.0 (M EUR 2023); ECA gives 12.9 initial and 16.5 final (nominal, year not printed). Both sets kept. Needs a price-year and perimeter decision in R1c.
2. SEA forecast cost. IGEDD text: 8,176 M EUR 2017 "prix total" (incl. accompanying works). IGEDD Table 17 prints 8,179 M EUR 2023 for the same forecast. The two differ in price basis and by rounding and perimeter. Both kept. A further basis, computed here and not printed by the IGEDD, divides the concession's ex post accounting investment (7,151 M EUR 2017) by 302 km to give 23.7 M EUR 2017 per km; it is kept in the metric rows as a computed row.
3. LGV EE phase 2 opening date. The IGEDD 2025 opinion gives end-2016; Table 17 gives 2016; a press snippet (not read) gives a different day. Not resolved.
4. Rhin-Rhône perimeter. ECA Table 5 gives 2,588 M EUR nominal for 138 km; ECA Annex III project 2007-FR-24070-P gives 2,610 M EUR real for 137.5 km; Table 17 LN 7 gives 3,533 M EUR 2023 for 137 km. Three perimeters and price bases.
5. ECA Table 6, Paris-Strasbourg: the HSR door-to-door time of 5:10 to 5:30 looks long for a 466 to 548 km trip with direct TGV service. The values were read from the rendered page image and are recorded as printed. A second reader should confirm the row alignment before any figure uses them.
6. Ridership benchmark: the 9 million passengers a year is a cited benchmark from the ECA, not an empirical threshold. Flag it as a benchmark in any R1c use.
7. Overrun baselines: several IGEDD ratios are computed from printed ratios, and the LGV Méditerranée and LGV Rhône-Alpes baselines have no printed price basis. The overrun rows are candidates for R1c, with no uplift applied here.

## Sources

[^S-bench-fr-001]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Table 5 (PDF p.36; printed p.35); values as printed, nominal per the table note. Quote: "Rhin-Rhône 138 2 588 2 053 26.1 % 14.9 18.8". Status: verified; grade per the source table.

[^S-bench-fr-002]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Table 5 (PDF p.36; printed p.35). Quote: "LGV Est Européenne 406 6 712 5 238 28.1 % 12.9 16.5". Status: verified; grade per the source table.

[^S-bench-fr-005]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Table 2 (PDF p.22; printed p.21). Quote: "LGV Est Européenne 1992 2002 2016 24 14". Status: verified; grade per the source table.

[^S-bench-fr-006]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Table 2 (PDF p.22; printed p.21). Quote: "Rhin - Rhône 1992 2006 2011 19 5". Status: verified; grade per the source table.

[^S-bench-fr-007]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Annex III (PDF p.67; printed p.66-67), French rows. Quote: "2 340 76 2 130 76 106 20.1". Status: verified; grade per the source table.

[^S-bench-fr-008]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Annex III (PDF p.67), French rows. Quote: "2 312 198 2 610 198 137.5 19". Status: verified; grade per the source table.

[^S-bench-fr-009]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Annex VII (PDF p.76; printed p.75), row 'LGV Est Européenne Paris - Strasbourg'. Quote: "LGV Est Européenne Paris - Strasbourg 441 5 110 68 137 106 119 13 7". Status: verified; grade per the source table.

[^S-bench-fr-010]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Annex VII (PDF p.76; printed p.75), row 'LGV Rhin-Rhône Dijon - Mulhouse'. Quote: "LGV Rhin-Rhône Dijon - Mulhouse 205 4 68 46 82 62 74 12 6". Status: verified; grade per the source table.

[^S-bench-fr-011]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 79 (PDF p.47; printed p.46-47) and footnote 43. Quote: "a high-speed line should ideally have nine million passengers, or at least six million in the opening year to". Status: verified; grade per the source table.

[^S-bench-fr-012]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 79 (PDF p.47). Quote: "In 2016, only three lines actually carried more than nine million passengers per year". Status: verified; grade per the source table.

[^S-bench-fr-013]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 81 (PDF p.48; printed p.47-48). Quote: "Nine of the 14 audited high-speed lines and cross-border connections did not have a sufficiently high number". Status: verified; grade per the source table.

[^S-bench-fr-014]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 75 and Picture 3 (PDF p.45; printed p.44-45). Quote: "the Meuse TGV station (Picture 3) on the LGV Est-Européenne is poorly accessible". Status: verified; grade per the source table.

[^S-bench-fr-015]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 77 (PDF p.46; printed p.45-46). Quote: "we saw no clear regeneration effects from 15 of the 18 stations". Status: verified; grade per the source table.

[^S-bench-fr-017]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Annex IV (PDF p.69; printed p.68-69), France row of the first table. Quote: "France 2 548 2 628 38 395 40 382 1 406 49.0 67.0". Status: verified; grade per the source table.

[^S-bench-fr-018]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Annex IV calculated KPI table (PDF p.69), France row. Quote: "France 15 15 573 603 0.22 0.23 21 19.2 731". Status: verified; grade per the source table.

[^S-bench-fr-019]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 60(v) (PDF p.39; printed p.38). Quote: "Overall, high-speed rail in France costs most per kilometre travelled". Status: verified; grade per the source table.

[^S-bench-fr-020]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 62(i) (PDF p.40; printed p.39). Quote: "the modal split between air and rail has changed from 85:15 to 38:62 in 2016". Status: verified; grade per the source table.

[^S-bench-fr-021]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Table 6 (PDF p.40; printed p.39), read from the rendered page (table image; cells as printed). Quote: "High-speed rail 6:00-8:20 159-181 (rendered table image, row 'High-speed rail')". Status: verified; grade per the source table.

[^S-bench-fr-022]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Table 6 (PDF p.40; printed p.39), read from the rendered page (table image). Quote: "Paris-Strasbourg column: car 8:40-12:20 44-79; coach 13:00-22:40 33-55; HSR 5:10-5:30 158-165 (rendered table image)". Status: verified; grade per the source table.

[^S-bench-fr-023]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Table 6 (PDF p.40; printed p.39), read from rendered page (table image). Quote: "Berlin Potsdamer Platz - Munich Marienplatz: HSR 8:30-10:30 66 (rendered table image)". Status: verified; grade per the source table.

[^S-bench-fr-024]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8; printed 8/106). Quote: "a reduit de 51 minutes les temps de parcours". Status: verified; grade per the source table.

[^S-bench-fr-025]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "la construction d’un tronçon neuf de 302 km entre Tours et Bordeaux". Status: verified; grade per the source table.

[^S-bench-fr-026]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "entraine une révision ex post du TRI-SE à 6%". Status: verified; grade per the source table.

[^S-bench-fr-027]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "alors qu’il était estimé ex ante à 8%". Status: verified; grade per the source table.

[^S-bench-fr-028]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "promettaient une frequentation en hausse de +21% a +28%". Status: verified; grade per the source table.

[^S-bench-fr-029]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "En 2019, SNCF Voyageurs a transporte 18,6 millions de voyageurs". Status: verified; grade per the source table.

[^S-bench-fr-030]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "Ce niveau de subvention cumulee (2,8 Mds€2017) de 38%". Status: verified; grade per the source table.

[^S-bench-fr-031]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "le concessionnaire dispose du droit d’y percevoir les peages ferroviaires jusqu’en 2061". Status: verified; grade per the source table.

[^S-bench-fr-032]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Résumé (PDF p.8). Quote: "la mise en concurrence de la concession n’a pas permis de reduire le cout kilometrique de la LGV, qui a atteint un niveau record". Status: verified; grade per the source table.

[^S-bench-fr-033]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §1.3 (PDF p.16-17; printed p.16-17). Quote: "L’estimation du taux de rentabilite financiere (TRI financier) est manquante". Status: verified; grade per the source table.

[^S-bench-fr-034]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: § on delivery models (PDF p.26). Quote: "Elles ont ete construites en maîtrise d’ouvrage directe par SNCF, RFF et desormais SNCF Reseau". Status: verified; grade per the source table.

[^S-bench-fr-035]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §5.1 (PDF p.76; printed 76/106). Quote: "les subventions publiques, pour un total de 2 817 M€". Status: verified; grade per the source table.

[^S-bench-fr-036]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §4.3.6 (PDF p.73). Quote: "puis le deuxieme de 5 863 M€2006 en 2007". Status: verified; grade per the source table.

[^S-bench-fr-037]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §4.3.6 (PDF p.73). Quote: "est revise en 2011 a 7 446 M€2017". Status: verified; grade per the source table.

[^S-bench-fr-038]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §4.3.5-4.3.6 (PDF p.72-73). Quote: "Ex post, le montant comptable d’investissement au titre de la concession est de 7 151 M€2017". Status: verified; grade per the source table.

[^S-bench-fr-039]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §4.3.6 (PDF p.73). Quote: "Le prix total de l’investissement inital de la LGV SEA est donc de 8 176 M€2017". Status: verified; grade per the source table.

[^S-bench-fr-040]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §3.3.5 (PDF p.53-54; printed 53-54). Quote: "La modelisation ex post conclut a un report de 10% de l’aerien". Status: verified; grade per the source table.

[^S-bench-fr-041]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §3.3.5 (PDF p.53). Quote: "Dans le scenario « avec hausse tarifaire », a 51% de voyageurs reportes de l’aerien". Status: verified; grade per the source table.

[^S-bench-fr-042]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §3.3.5 heading (PDF p.53). Quote: "Plus de quatre fois moins de reports de l’avion que prévu". Status: verified; grade per the source table.

[^S-bench-fr-043]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §3.3.3-3.3.4 (PDF p.49). Quote: "a la mise en service, respectivement de 19,4 millions de voyageurs et 20,6 millions de voyageurs". Status: verified; grade per the source table.

[^S-bench-fr-045]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Graphique 9 and source note (PDF p.48). Quote: "Au-delà de 3-4 heures de trajet en train, l’avion est le plus utilisé". Status: verified; grade per the source table.

[^S-bench-fr-046]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §3.3.3 (PDF p.48). Quote: "le temps de parcours en avion varie peu en fonction de la distance parcourue". Status: verified; grade per the source table.

[^S-bench-fr-047]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §1.1 (PDF p.10; printed 10/30). Quote: "est de 1 971 millions d’euros courants". Status: verified; grade per the source table.

[^S-bench-fr-048]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §1.1 (PDF p.10). Quote: "ce montant s’élève à 1 804 M€ CE 06/2008 HT". Status: verified; grade per the source table.

[^S-bench-fr-049]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §1.1 (PDF p.10). Quote: "présentait une estimation de l’investissement en infrastructures de 2 010 millions d’euros CE 06/2008 HT". Status: verified; grade per the source table.

[^S-bench-fr-050]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §1.1 (PDF p.10). Quote: "Le coût final de la LGV EE 2 est inférieur de 206 millions d’euros". Status: verified; grade per the source table.

[^S-bench-fr-051]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §1.1 (PDF p.10); primary CGEDD 009145-01 (July 2013) not opened. Quote: "est passé de la prévision de 3 905 M€2009 à 4 655 M€2009". Status: verified; grade per the source table.

[^S-bench-fr-052]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §1.1 ratios table (PDF p.11). Quote: "Phase 2 19 67". Status: verified; grade per the source table.

[^S-bench-fr-053]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §1.1 ratios table (PDF p.11). Quote: "Phase 1 15,5 51,7". Status: verified; grade per the source table.

[^S-bench-fr-055]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §3 (PDF p.19). Quote: "s'élève à 12 millions de voyageurs en 2009". Status: verified; grade per the source table.

[^S-bench-fr-056]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §3 and footnote 16 (PDF p.19). Quote: "de 15,5 millions de voyages/an ramenés à 11,5". Status: verified; grade per the source table.

[^S-bench-fr-058]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §3 (PDF p.20). Quote: "Le gain de trafic ferroviaire estimé ex post serait compris entre 1,14 et 1,24 million de". Status: verified; grade per the source table.

[^S-bench-fr-059]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §3 (PDF p.20). Quote: "à comparer à un gain estimé ex ante de 0,934 million de voyageurs". Status: verified; grade per the source table.

[^S-bench-fr-060]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §6 (PDF p.23). Quote: "En phase 1, le TRI socio-économique constaté ex post était en effet de 3,7 %". Status: verified; grade per the source table.

[^S-bench-fr-063]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: Section LGV Rhône-Alpes §3 (PDF p.8; printed 4). Quote: "Le coût de l'infrastructure, 1261 M€, est supérieur de 22% au coût prévu dans l’enquête". Status: verified; grade per the source table.

[^S-bench-fr-064]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Rhône-Alpes §3 (PDF p.8). Quote: "Le délai de réalisation, avec une ouverture en 1994, est celui prévu lors de l’enquête d’UP". Status: verified; grade per the source table.

[^S-bench-fr-065]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Rhône-Alpes traffic table (PDF p.11). Quote: "Total 17,5 14,8 19,3 18,6". Status: verified; grade per the source table.

[^S-bench-fr-067]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Rhône-Alpes traffic (PDF p.11). Quote: "Le taux de détournement de l'aérien représente environ 10% du trafic aérien". Status: verified; grade per the source table.

[^S-bench-fr-068]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Rhône-Alpes socio-economic appraisal (PDF p.13). Quote: "Sur une période de 20 ans, le TRI est de 6,3% a posteriori contre 10,4% a priori (DUP)". Status: verified; grade per the source table.

[^S-bench-fr-069]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Méditerranée history (PDF p.29). Quote: "juin 2001: mise en service commerciale". Status: verified; grade per the source table.

[^S-bench-fr-070]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Méditerranée §3 (PDF p.30) and cost table (PDF p.31; M€2003). Quote: "Le coût prévu à la DAM pour le projet finalement réalisé était de 4202 M€". Status: verified; grade per the source table.

[^S-bench-fr-071]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Méditerranée §3 (PDF p.30). Quote: "Le coût de l'infrastructure, 4362 M€, ne peut être directement comparé". Status: verified; grade per the source table.

[^S-bench-fr-072]: CGEDD (Conseil général de l'environnement et du développement durable), "Rapport n° 005448-01 (CGPC/CGEDD): Rapport sur les bilans LOTI: LGV Rhône-Alpes, LGV Méditerranée, gares nouvelles", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/5448-01_cle27828d-1.pdf, published juillet 2008, accessed 2026-10-31. Locator: LGV Méditerranée §3 (PDF p.30). Quote: "Le délai de réalisation a été plus long que prévu d'environ 3 ans". Status: verified; grade per the source table.

[^S-bench-fr-073]: Yves Crozet and François Dumont (interview in Ville, Rail & Transports, n° 525), "Retour sur les effets économiques du TGV. Les effets structurants sont un mythe (interview)", https://shs.hal.science/halshs-01094554v1, published 2011 (magazine date 27/07/2011; HAL deposit 12 Dec 2014), accessed 2026-10-31. Locator: interview pp.48-51 (HAL copy, page 1 and magazine footer). Quote: "Les effets structurants sont un mythe". Status: verified; grade per the source table.

[^S-bench-fr-074]: Valérie Facchinetti-Mannone (Université de Bourgogne, THEMA); Cahiers Scientifiques du Transport (refereed journal; review status to confirm), "La nodalité des gares TGV périphériques", https://cst.episciences.org/12036/pdf, published 2005 (CST N° 48/2005), accessed 2026-10-31. Locator: Tableau 1, p.51-52 of the article (printed). Quote: "Haute-Picardie 4 17 147 34 3 40 38 %". Status: verified; grade per the source table.

[^S-bench-fr-075]: Valérie Facchinetti-Mannone (Université de Bourgogne, THEMA); Cahiers Scientifiques du Transport (refereed journal), "La nodalité des gares TGV périphériques", https://cst.episciences.org/12036/pdf, published 2005 (CST N° 48/2005), accessed 2026-10-31. Locator: Tableau 1 (article p.51-52). Quote: "Vendôme 1 11 32 3 2 22 100 %". Status: verified; grade per the source table.

[^S-bench-fr-076]: Valérie Facchinetti-Mannone (Université de Bourgogne, THEMA); Cahiers Scientifiques du Transport (refereed journal), "La nodalité des gares TGV périphériques", https://cst.episciences.org/12036/pdf, published 2005 (CST N° 48/2005), accessed 2026-10-31. Locator: Conclusion (article p.56-57). Quote: "Les gares TGV implantées en périphérie des villes petites et moyennes". Status: verified; grade per the source table.

[^S-bench-fr-077]: Sylvie Bazin, Christophe Beckerich, Marie Delaplace, Sophie Masson; Cahiers Scientifiques du Transport (refereed journal), "L'arrivée de la LGV en Champagne-Ardenne et la nécessaire réorganisation des rapports de proximité", https://cst.episciences.org/12042/pdf, published 2006 (CST N° 49/2006), accessed 2026-10-31. Locator: Tableau 'Voyage en train direct / jour' (article p.58-59 printed). Quote: "Reims centre 215 556 172 1h40 0h45 12 8 143 1h28". Status: verified; grade per the source table.

[^S-bench-fr-078]: Sylvie Bazin, Christophe Beckerich, Marie Delaplace, Sophie Masson; Cahiers Scientifiques du Transport (refereed journal), "L'arrivée de la LGV en Champagne-Ardenne et la nécessaire réorganisation des rapports de proximité", https://cst.episciences.org/12042/pdf, published 2006 (CST N° 49/2006), accessed 2026-10-31. Locator: Conclusion (article p.73-74 printed). Quote: "la LGV est susceptible de favoriser l’amélioration de l’accessibilité à Paris de seulement quelques villes du nord". Status: verified; grade per the source table.

[^S-bench-fr-080]: Cour des comptes (France), "La grande vitesse ferroviaire: un modèle porté au-delà de sa pertinence", https://temis.documentation.developpement-durable.gouv.fr/docs/Temis/0083/Temis-0083180/22248.pdf, published October 2014, accessed 2026-10-31. Locator: not read. Quote: "not read". Status: unverified; grade per the source table.

[^S-bench-fr-081]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 70 (PDF p.43; printed p.42). Quote: "The number of stations ranges from four (LGV Rhin-Rhône) to 15". Status: verified; grade per the source table.

[^S-bench-fr-082]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: Commission replies, Executive summary IX (PDF p.92). Quote: "The inclusion of minimum passenger volumes may pre-empt project solutions". Status: verified; grade per the source table.

[^S-bench-fr-083]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD sur le bilan LOTI de la ligne à grande vitesse Est-européenne phase 2 (rapport n° 016386-01)", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/016386-01_rapport_publie_cle5a515d.pdf, published Oct 2025, accessed 2026-10-31. Locator: §6 (PDF p.23). Quote: "SNCF voyageurs a indiqué avoir un bilan négatif du fait de l’évolution". Status: verified; grade per the source table.

[^S-bench-fr-084]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 60(iii) (PDF p.39; printed p.38). Quote: "and the two audited French lines had very few connections". Status: verified; grade per the source table.

[^S-bench-fr-085]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 50(i) (PDF p.34; printed p.33). Quote: "A CBA with a negative economic net present value was accepted for EU co-funding". Status: verified; grade per the source table.

[^S-bench-fr-086]: European Court of Auditors, "A European high-speed rail network: not a reality but an ineffective patchwork (Special Report No 19/2018)", https://www.eca.europa.eu/Lists/ECADocuments/SR18_19/SR_HIGH_SPEED_RAIL_EN.pdf, published 2018, accessed 2026-10-31. Locator: para 53 (PDF p.35; printed p.34). Quote: "all audited high-speed lines had cost overruns of more than 25 %". Status: verified; grade per the source table.

[^S-bench-fr-087]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §5.1 (PDF p.76; printed 76/106). Quote: "60% pour la première section". Status: verified; grade per the source table.

[^S-bench-fr-088]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: §5.1 (PDF p.76; printed 76/106). Quote: "de la LGV Rhin-Rhône (75%)". Status: verified; grade per the source table.

[^S-bench-fr-089]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 1 Sud-Est 1981/1983 425 381 44 104 2 271 M€ 101% 2 291 M€ 6,0". Status: verified; grade per the source table.

[^S-bench-fr-090]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 2 Atlantique 1989/1990 292 271 21 52 2 128 M€ 137% 2 906 M€ 10,7". Status: verified; grade per the source table.

[^S-bench-fr-091]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 3 Nord 1994/1996 346 326 20 86 4 528 M€ 101% 4 556 M€ 14,0". Status: verified; grade per the source table.

[^S-bench-fr-092]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "Interconnexion IdF 1994/1996 105 97 8 31 1 740 M€ 110% 1 909 M€ 19,7". Status: verified; grade per the source table.

[^S-bench-fr-093]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 4 Rhône-Alpes 1992/1994 122 113 9 30 1 738 M€ 99% 1 723 M€ 15,3". Status: verified; grade per the source table.

[^S-bench-fr-094]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 5 Méditerranée 2001 259 218 41 78 5 743 M€ 102% 5 838 M€ 26,8". Status: verified; grade per the source table.

[^S-bench-fr-095]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 6 LGV Est ph.1 2007 335 300 35 94 4 848 M€ 119% 5 779 M€ 19,3". Status: verified; grade per the source table.

[^S-bench-fr-096]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 8 LGV Est ph.2 2016 122 106 16 31 2 633 M€ 85% 2 228 M€ 21,0". Status: verified; grade per the source table.

[^S-bench-fr-097]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LN 7 LGV RR ph.1 2011 146 137 9 58 2 796 M€ 126% 3 533 M€ 25,7". Status: verified; grade per the source table.

[^S-bench-fr-098]: IGEDD (Inspection générale de l'environnement et du développement durable), "Avis de l'IGEDD n°014932-01: Bilan socio-économique ex post de la LGV SEA", https://www.igedd.developpement-durable.gouv.fr/IMG/pdf/014932-01_rapport_publie_cle5d1f6c.pdf, published Sept 2025, accessed 2026-10-31. Locator: Tableau 17 (PDF p.73); table is an image, row read from the rendered page. Quote: "LGV SEA 2017 340 302 38 51 8 179 M€ 104% 8 533 M€ 28,3". Status: verified; grade per the source table.
