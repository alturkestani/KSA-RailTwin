> **Document version:** docs/sources/cost-notes-civil.md v1.0 | 31 Oct 2026 | Author: cost-estimator (R1c task 3, topic `civil`) | Status: draft

# R1c civil capex library: research notes

Outputs: `docs/sources/cost-civil.csv` (S-cost-civil-001 to -018), `cities/ksa/costs/cost_register.yaml` (73 proposed rows: 21 sourced, 45 derived, 4 assumed, 3 unknown). Every figure was read today in the named document. Values stay in source currency and price year (no conversion). "Derived" rows show their arithmetic in `derivation`; most derived rows differ from the source only in computing interquartile ends or a midpoint/median as the central value.

## 1. Line types (per route-km)

**EC DG REGIO / PwC 2018 (S-lb-030, detail in S-cost-civil-006).** Read in full (local PDF; Figure 2 checked on the page image). EUR 2016, PPP x PPI/HICP normalised, per double-track-equivalent km, EU projects 2000–2015. Three tiers are printed, each as "Q1-Q3: c ± p%":
- total investment: new conventional 8.2 ±16 %, new HS 14.1 ±16 %, upgrade conv 6.1 ±42 %, upgrade HS 5.4 ±60 %, rehabilitation 4.4 ±60 % (rows -001, -004, -007, -009, -011);
- construction: 7.2 ±19 % / 14.1 ±17 % / 5.4 ±39 % / 4.9 ±64 % (rows -002, -005, -008);
- base infrastructure (no tunnels, bridges, stations): 4.4 ±15 % / 8.4 ±12 % (rows -003, -006), upgrade conv 4.1 ±36 % (-010);
- single components: earthworks conv 0.9 ±65 %, HS 3.4 ±24 %; permanent way 1.7 ±39 % / 1.1 ±23 %; fencing 0.8 ±33 % (rows -012 to -016). Signalling, electrification and telecom figures (0.3–0.6 M€/km) are left to the systems topic.
- EC gives no numeric planning & design / ancillary shares in text (Figure 1 is a schematic only).

**Flag for the coordinator (not edited by me):** the S-lb-030 claim in `docs/sources/index.csv` and the "EC interquartile USD 6.5–9.6 m/km" band in `docs/costs-landbridge.md` use the **construction** cluster (7.2 ±19 %). The **total-investment** cluster for new conventional lines is 8.2 ±16 %. The like-for-like comparison for whole-project KSA figures is the total-investment band. The conclusion in costs-landbridge.md does not appear to flip, but the label should be corrected.

**World Bank 2014 China note (S-lb-029; extra tables in S-cost-civil-002, -004).** 350 km/h RMB 94–183 m/km (weighted avg 129); 250 km/h RMB 70–169 (avg 87), all-in incl. rolling stock and IDC (-017, -018). 200 km/h mixed lines RMB 89 and 99 m/km (-026). "Railway" excl. preparation, rolling stock and IDC ≈ 82 % of total (-035). Europe US$25–39 m/km (US$ 2012) (-019); four French LGVs EUR 18.1–25.7 m/km, total 22.2 (2013 estimates) (-020).

**ECA SR 19/2018 (S-cost-civil-001).** Average 25 M€/km excluding tunnelling projects; final/completion cost per km 13.7–49.7 (nominal) (-021). Initial construction estimates were 6.9–14.9 M€/km and aggregate overruns 44 % (project) / 78 % (line), with Stuttgart–Munich at 622 %. These figures belong in the reference-class register, not here.

**Campos, de Rus & Barrón (S-cost-civil-003).** I read the 2007 WCTR working paper. The 2009 Transport Policy article is paywalled. HSR construction 6–45 M€/km (2005), average 17.5 (45 projects); excludes planning and land (-022).

**PwC 2016 HS2 benchmarking (S-cost-civil-005).** GBP 2011 PPP, 20 European comparators: average £32m/route-km (11–79) (-023); rural sections £11–20m (-024); urban £43–61m; tunnel/viaduct-dominated subsections £72–93m.

**KSA/GCC data points (top-down, award values):**
- Haramain Phase 1 Package 1 civils SAR 6.79 bn / 444 km (Railway Gazette) → SAR 14.99–15.29 m/km (-025). Civil works only.
- SAR North-South civil and track packages (2007): SAR 3.73–4.32 m/km single-track freight (-027).
- Etihad Rail Stage One civil and track AED 3.3 bn for 266 km. This is kept as a lump (-028) because only one length is verified, which would make the per-km figure a single point. Per km = AED 12.41 m (arithmetic only).
- Baumgartner 2001 (via EC Tables 1–3, S-cost-civil-010): easy / average / difficult topography, all-in EUR 2000 (-029 to -032).

**Commuter/suburban:** no open at-grade per-km benchmark found (-034 `unknown`). Flyvbjerg et al. 2008 (CC BY 4.0) urban metro US$50–100m (Europe) / 50–150m (incl. US), 2002 prices, all-in. Row -033 is metro-class and serves as an upper reference only. The Transit Costs Project database states no licence ("All rights reserved", S-cost-civil-018), so it is not used. Flag it for the licence register before any use.

## 2. Terrain

- **Escarpment/mountain:** Baumgartner ratios give +233 % (average topography) to +1233 % (difficult) for 300 km/h, and +250 % to +900 % for 100 km/h (-036, -037). They are dated and very wide, so treat them as a cross-check only. The better method is structure share × unit cost: WB "mountainous areas … as high as 80 percent of the alignment length" (-055, range 66–80 %). Campos: infrastructure building is usually 10–25 % of total investment; singular structures "may easily double this amount (up to 40%)".
- **Dunes:** no published per-km premium was found. Evidence: Nafud embankments up to 70 m high and 200 m wide at the base, 125 million m³ over 140 km (≈0.89 million m³/km) (S-cost-civil-012, no cost). The SAR North Nafud package costs SAR 4.32 m/km against 3.73–3.99 for the other packages, but package boundaries do not isolate terrain. Namibia Aus–Lüderitz: a sand-shelter tunnel structure costs N$115.5 m/km (-039), against N$5.2–7.0 m/km for track. Sand removal plus maintenance on ballasted track costs N$2.81–5.55 m/km/yr (-041; category `opex`, hand-off to the opex track). The premium is assumed (A-cost-200, -038).
- **Sabkha:** no unit cost found. Etihad Rail did ground improvement (Keller, 13 km; rapid impact / dynamic compaction to 10 m), but no value is published. The premium is assumed (A-cost-201, -040).

## 3. Structures

- Tunnels: PwC £18–62m/route-km (avg 36, GBP 2011) (-042). Baumgartner bare double-track tunnel EUR 30 (20–70) (2000) (-043). WB China 250 km/h RMB 60–95m/km (-044); the WB text gives China tunnels US$10–15m/km and cites US$43m (NZ), US$50m (US) and US$60m (AU) (Efron & Read 2012). HS2 Phase 2: £21,000–26,900 per single bored metre, which gives £42–53.8m per twin-bore km by our arithmetic (-047).
- Viaducts/bridges: PwC £13–53m (avg 31) (-048); WB China RMB 57–73m/km (-049; actual ShiZheng RMB 60–70m/km); HS2 £23–32m/km (-050); Baumgartner bridges EUR 10–50 (-051); PwC earthworks £4–8m (-052).
- Ratios (Pickrell 1985 via Flyvbjerg 2008): elevated = at-grade +71–79 %; tunnel = at-grade +347–357 % (-045, -046).
- Shares: China bridges+viaducts+tunnels 66–80 % of route-km for HSR (-053) and 48–53 % for 200 km/h mixed lines (-054). They are high because China puts lines on viaducts over fertile plains. Cost shares at 250 km/h: tunnels 16–29 %, viaducts 13–25 % of total (-057, -058). No source gives the share for flat desert, so it is assumed (A-cost-202, -056).
- **Conflict (data handling, not values):** EC/PwC 2018 reprints the PwC tunnel and viaduct ranges as "20.4 to 70.3 M £/km" and "14.7 to 60.1 M £/km". These are the GBP figures × 1.13449 (EC footnote 17), i.e. EUR mislabelled as GBP. The register uses the PwC primary (GBP 2011).

## 4. Land and utilities

- Land share: China 4–8 % (HSR) and 6–9 % (mixed) of total cost (-059, -060); PwC £0.5–6.4m/route-km, median 1.25 (-061); Campos planning + land 5–10 % (-062, a combined item that must not be double-counted with design rows); California site work + ROW 17.6 % (-063).
- KSA: Haramain total SAR 63 bn "including expropriation" (S-cost-civil-015, 2015) and compensation SAR 6.5 bn paid "so far" (Oct 2013, S-cost-civil-016, **unverified**, page returned 403). Together they give ≈10.3–10.8 % (-064). This is a lower bound and mixes nominal years. SAR North cost statements exclude expropriation (S-lb-023).
- Utilities: no open interurban source was found, so the share is assumed (A-cost-203, -065). Urban utilities stay `unknown` (-066). An "8–10 % (1996 light rail, incl. betterments)" figure appeared only in a search summary and was not used.

## 5. Design, PM, contingency

- PwC indirects (design, PM, insurance) 7.5–20.4 % of construction, median 15.3 (-067). Campos supervision/QC 1–5 % (-069). Sound Transit ST3 FTA SCC 80: 32 % of construction for projects over $25M, 48 % for those under $25M (-068).
- Contingency: PwC 10–30 % at early-estimate maturity (-070). ST3 unallocated (SCC 90) prints "10 20 percent" of SCC 10–80, a tracked-change residue, so the row carries 10–20 (-071). ST3 allocated contingency is 30 % at system-plan stage (-072). These are estimating contingencies. The reference-class (optimism-bias) uplift is separate, so check for stacking.
- An FRA high-speed rail document cited as "13.5 % professional services" returned 403 and was not used.

## 6. Conflicts (both kept, never averaged)

| topic | figures | note |
|---|---|---|
| Haramain route length for per-km civils | 444 km (Railway Gazette 2009, S-cost-civil-007) vs 453 km (S-002) | per-km range 14.99–15.29 carries both |
| Haramain total cost | SAR 63 bn incl. expropriation (2015, S-cost-civil-015) vs SAR 60 bn (2018, S-lb-021) | different dates and possibly different scope; both used as denominators in -064 |
| SAR North Phase A contract | US$765m / 818 km (Construction Briefing 2008) vs SAR 2.8 bn / 750 km third package (Railway Technology 2010) | possibly the same contract described differently; not used as separate rows |
| PwC tunnel/viaduct units | PwC GBP vs EC reprint labelled GBP but in EUR | use PwC primary |
| ECA vs EC on HSR per km | ECA 25 M€/km nominal average (13.7–49.7) vs EC total-investment 14.1 ±16 % (EUR 2016) | different samples (10 audited lines vs EU cohesion/TEN-T database) and price bases |

## 7. Unknowns (with where searched)

- Commuter at-grade civil + track per km (-034): EC/PwC, Transit Costs Project, Flyvbjerg 2008, web search.
- Sand fencing / sand-mitigation capex per km (-073): Haramain, SAR North, Etihad Rail, ONCF, SNIM. Searched: web (EN/AR), Railway Gazette, Construction Briefing, Raffaele et al. 2022 (403), SMaRT project page.
- Urban utilities diversion share (-066).
- Not reached within budget: UIC HSR cost studies/InfraCost, ITF/OECD rail cost papers, and the Trafikverket "New main lines cost benchmarking" study (2021; URL returned 404).

## 8. Proposed assumption rows (block A-cost-200 to A-cost-249; used 200–203)

| id | parameter | value | unit | range | source or assumption | status | used in |
|---|---|---|---|---|---|---|---|
| A-cost-200 | Dune terrain capex premium on civil + track over flat desert | 25 | % | 5–100 | assumption: no published per-km dune premium; bounded by Nafud earthworks (~0.89 Mm³/km, 70 m embankments, S-cost-civil-012), SAR North package costs (S-cost-civil-008) and the Namib sand-shelter option (S-cost-civil-013) | assumed | cities/ksa/costs/cost_register.yaml (C-terrain-dunes-uplift-038) |
| A-cost-201 | Sabkha terrain capex premium on civil + track over flat desert | 20 | % | 5–60 | assumption: ground improvement needs on sabkha are documented (Etihad Rail/Keller), but no cost is published | assumed | cost_register.yaml (C-terrain-sabkha-uplift-040) |
| A-cost-202 | Structures share of route-km in flat desert | 5 | % | 1–15 | assumption: no desert-line share published; Chinese plains shares (48–80 %, S-cost-civil-002) reflect a viaduct-over-farmland policy that does not apply | assumed | cost_register.yaml (C-structure-share-flat-desert-056) |
| A-cost-203 | Utilities diversion share of capex, interurban | 1.5 | % of capex | 0.5–5 | assumption: no open interurban source found | assumed | cost_register.yaml (C-utilities-diversion-065) |

## 9. Primaries to find

1. Campos & de Rus 2009, Transport Policy 16(1) (published version of S-cost-civil-003).
2. Baumgartner 2001, "Prices and costs in the railway sector" (EPFL-LITEP), original tables.
3. SAR/SRO award notices: Haramain Phase 1 Package 1, SAR North 2007 civil packages, and any sand-protection contracts.
4. Al Arabiya 6 Oct 2013 full text (S-cost-civil-016), or an SRO statement of Haramain expropriation compensation.
5. Etihad Rail press release or annual report for the Stage One value and length (264 vs 266 km), plus any sabkha ground-improvement value.
6. Raffaele, Coste & Glabeke 2022 (J. Struct. Eng.), sand-mitigation life-cycle costs.
7. UIC HSR cost/InfraCost studies; ITF/OECD rail infrastructure cost papers; Trafikverket new main lines benchmarking (2021).
8. FTA SCC guidance with national ranges for SCC 80 and SCC 90; the FRA HSR professional-services document (403 today).
9. Transit Costs Project data licence (NYU Ultraviolet DOI 10.58153/9wnjp-kez15) before any use.
