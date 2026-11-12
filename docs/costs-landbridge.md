> **Document version:** docs/costs-landbridge.md v1.1 | 30 Oct 2026 | Author: coordinator (LANDBRIDGE_RECONCILE); model-id note removed by CP2_PREP | Status: draft

# Saudi Landbridge: reconciling SR 100 bn (USD 26.6 bn) with USD 7 bn

**Label:** this page reconciles published cost statements. It contains no modelled output. Every figure is nominal, as printed by its source, and carries an `S-` id from `docs/sources/index.csv` (rows `S-lb-001` to `S-lb-034` were added by this run; `S-046` to `S-063` come from `DATASCOUT_1H`). Text marked **analysis** is our reading, not a sourced fact. Arithmetic was run in Python on 30 Oct 2026; every step is reproducible from the inputs in the tables. Price years are stated where a source gives one; none of the Landbridge statements does.

Trigger: PROJECT.md section 4 flags the conflict ("reconcile them or flag the conflict"); Tariq asked on 30 Oct 2026, "can you try to come up with the math?". This page answers `docs/sources/conflicts.md` entry C-001.

## 1. The two headline figures

| figure | who said it, where, when | what the source says it covers | price year | evidence grade (benchmark-dossier A–D) | ids |
|---|---|---|---|---|---|
| **SR 100 bn (USD 26.6 bn)** | SAR CEO Bashar Al-Malik, TV programme "في الصورة", reported 20 Jan 2026: "بتكلفة تصل إلى حوالي 100 مليار ريال", complete before 2034, target 2032–2033 | the Landbridge as a whole ("المشروع الأهم والأضخم") | not stated | C (press, named official; broadcast not read) | S-lb-001 |
| same figure, English trade press | MEED 21 Jan, 12 Feb, 14 Jul, 31 Aug 2026; Construction Review 19 Feb and 14 Jul 2026 | whole programme: "more than 1,500 km of new track", 900 km Riyadh–Jeddah core; MEED (31 Aug) adds "not only the Riyadh section" | not stated | C | S-046, S-047, S-048, S-lb-005, S-lb-006, S-lb-033 |
| same figure, earlier | Minister of Transport Saleh Al-Jasser, press statement 22 Mar 2022: "نحو 100 مليار ريال", **including infrastructure and trains**, >1,300 km, 5–7 years to build; repeated at the Riyadh Economic Forum 16 Nov 2022 ("مجموع تكاليف هذا المشروع 100 مليار ريال", project "fully designed" with a Chinese-led alliance); Zawya/Argaam: "100-billion Saudi riyal ($26.61 billion)" in the financing stage | whole programme incl. rolling stock | not stated | C (press; the Ministry of Transport X post of 16 Nov 2022 is the primary to find) | S-lb-002, S-lb-003, S-lb-004 |
| **USD 7 bn** | ENR, "Saudi Arabia moves forward on $7B rail Landbridge project": snippet "at a total cost of $7 billion, although the entire project is seen as requiring an investment of $26.6 billion". Page HTTP 403 on 30 Oct 2026 (fetch tool and curl); date bounded to on or before 22 Jun 2026 by Okaz's report of it | "total cost" (snippet) for a ~1,500 km network; same article gives USD 26.6 bn for "the entire project" | not stated | D (unverified: snippet only) | S-049, S-lb-034, S-lb-007 |
| same USD 7 bn, scope >1,500 km | MEED 4 Apr 2025: "The estimated $7bn project comprises more than 1,500km of new track" (nine months before MEED switched to SR 100 bn) | whole programme | not stated | C | S-lb-008 |
| same USD 7 bn, six-line scheme | MEED 26 Jan 2023: "$7bn", seven years, six lines, 1,500 km new + 678 km upgraded; IRJ via Trackopedia Dec 2023: "€6.5 billion (US$7 billion) project" cost and financing "almost finalised" | whole programme | not stated | C | S-lb-009, S-lb-011 |
| same USD 7 bn, 2021 | Minister Al-Jasser via Saudi Gazette, 2 Mar 2021: "estimated cost of $7 billion"; 950 km + 115 km Dammam–Jubail | whole project | not stated | C | S-051, S-055 |
| same USD 7 bn, 2011–2012 | Council of Ministers decision 10 Oct 2011: "up to USD 7 billion" (Wikipedia citing Railway Gazette); Gulf Construction: "more than SR26 billion ($7 billion)"; IRJ: "originally tendered the Riyals 26bn ($US 6.93bn)"; Arab News Dec 2012: "estimated to cost SR 26.6 billion"; MEED Jan 2012: "long-delayed $7bn" | whole project, freight/container line, 950 km + 115 km | not stated (2008–2011 tender era) | C / D | S-052, S-053, S-lb-012, S-lb-014, S-lb-016, S-lb-017 |

Other figures on the record (not headlines, kept for the hypotheses): USD 5,000 m, the 2007 BOT bids (S-lb-013); SR 50–60 bn, the SRO advisers' estimate reported by Al-Hayat in Oct 2011 (S-lb-015; date from a forum repost, unverified); USD 10.6 bn, the "agreed project value" SPA reported for the SAR–CCECC MoU of Oct 2018 (S-lb-010); USD 7 bn as the Riyadh Rail Link package value, Construction Review only (S-050); MEED Projects profile: "US$26650 million" in the description and "Net Value $20250m" (S-lb-018, paywalled, fields inconsistent); Hill International project sheet "Project Value $7 Billion" (S-lb-019, 404, snippet only).

## 2. Arithmetic

Inputs: SAR/USD official rate 3.75 (SAMA, S-lb-020; assumption A-cost-001 in `docs/assumptions.md` uses the same peg). Lengths: 900 km (MEED, S-054), 950 km (2021 press and Wikipedia lead, S-055), 958 km (2013 design contract, S-lb-017), "more than 1,500 km of new track" (S-057), 1,500 km new + 678 km upgraded = 2,178 km (S-lb-009). Per-km cells divide a nominal total of unknown price year by a route length; they are comparators, not estimates.

### 2a. Conversions

| step | result |
|---|---|
| SR 100 bn ÷ 3.75 | **USD 26.667 bn** (outlets print 26.6, a truncation; MEED Projects prints 26,650 m) |
| USD 7 bn × 3.75 | **SR 26.25 bn** = **26.25 %** of SR 100 bn |
| USD 26.667 bn ÷ USD 7 bn | **3.81 ×** |
| SR 26 bn ÷ 3.75 (2011) | USD 6.93 bn (matches IRJ's "$US 6.93bn", S-lb-014) |
| SR 26.6 bn ÷ 3.75 (2012) | USD 7.09 bn (matches "$7 bn") |

### 2b. The four cells and their neighbours (USD m per route-km, nominal)

| length basis | USD 26.667 bn (SR 100 bn) | USD 7 bn | SR 100 bn in SR m/km |
|---|---|---|---|
| 900 km core (S-054) | **29.6** | **7.8** | 111.1 |
| 950 km core (S-055) | **28.1** | **7.4** | 105.3 |
| 958 km core (S-lb-017) | 27.8 | 7.3 | 104.4 |
| >1,500 km new track (S-057): the cell is an **upper bound** because the track exceeds 1,500 km | **17.8** | **4.7** | 66.7 |
| 2,178 km = 1,500 new + 678 upgraded (S-lb-009) | 12.2 | 3.2 | 45.9 |
| 35 km Riyadh Rail Link (S-060; USD 7 bn per S-050 only) | — | 200 | — |

Historical statements on their own scope: SR 26.6 bn over 950 + 115 = 1,065 km = SR 25.0 m/km = USD 6.7 m/km (2012, S-lb-016, S-055); SR 50–60 bn over 958 km = USD 13.9–16.7 m/km (2011 advisers' estimate, S-lb-015); USD 10.6 bn over 960 km = USD 11.0 m/km (2018 MoU value, S-lb-010); USD 5 bn over 1,065 km = USD 4.7 m/km (2007 bids, S-lb-013).

### 2c. Comparators (nominal, as published; price year = statement year unless stated)

| project | cost as published | length | USD m per route-km | scope per the source | grade | ids |
|---|---|---|---|---|---|---|
| Haramain HSR (KSA, 300 km/h, opened 2018) | SR 60 bn ($16 bn), Minister Al-Amoudi, Mar 2018; OBG 2019 same; Arab News Dec 2012: "two phases, about SR 51.5 billion" | 453 km (S-002) | **35.3** (SR 60 bn); 30.3 (SR 51.5 bn) | whole project, two phases (civil; systems, rolling stock, stations, O&M) | C | S-lb-021, S-lb-022, S-lb-016, S-002 |
| SAR North–South (KSA, freight-led, diesel, largely single track, flat desert) | US$5.33 bn construction "excluding compensations for real estate expropriations" (SAR chairman, Mar 2012); SR 20 bn (Arab News Dec 2012); $3.5 bn (2010 estimate) | 2,750 km (S-lb-023); 2,400 km (S-lb-024) | **1.9** (5.33 bn / 2,750); 1.5 (3.5 bn / 2,400) | construction, excl. land | C | S-lb-023, S-lb-016, S-lb-024 |
| Etihad Rail Stage Two (UAE, diesel freight now, passenger later, double track) | AED 18 bn total value of Stage Two contracts (WAM, May 2020; title only, page script-rendered) | 605 km | **8.1** (AED 29.8 m/km at 3.6725, S-lb-026) | contracts awarded, not outturn | D (unverified page) | S-lb-025, S-lb-026 |
| Al Boraq (Morocco, 320 km/h new line + 220 km/h upgrade, opened 2018) | MAD 22.9 bn ($2.4 bn) "total cost" per MAP; MEED: budget about €1.8 bn ($2.1 bn) with extra funding during construction | 183 km HSR + 137 km upgraded = 320 km | **13.1** over 183 km; **7.5** over 320 km | whole project (both sections) | C | S-lb-027, S-lb-028 |
| Europe, new HSR ≥300 km/h (World Bank 2014 note, tables 4–5) | US$25–39 m/km (2012 US$: Córdoba–Málaga 27, Madrid–Barcelona 29, LGV Est 31, Madrid–Valladolid 39); four French LGVs under construction 2013: €18.1–25.7 m/km | — | **25–39** | construction (excl. land, rolling stock, IDC where stated) | B | S-lb-029 |
| China HSR (same note) | RMB 70–169 m/km overall; 250 km/h about RMB 87 m/km; 350 km/h infrastructure about US$17–21 m/km | — | **17–21** (350 km/h infrastructure) | infrastructure | B | S-lb-029 |
| EU cohesion rail projects, new lines (EC/PwC 2018, EUR 2016 PPP) | new conventional lines: interquartile 7.2 ± 19 % = **€5.8–8.6 m/km**; new high-speed: 14.1 ± 17 % = **€11.7–16.5 m/km**; conventional upgrade 5.4 ± 39 % = €3.3–7.5 m/km | — | indicative USD at 1.1172 (S-lb-031, today's rate applied to 2016 euros, so crude): conventional **6.5–9.6**; HS **13.1–18.4**; upgrade 3.7–8.4 | construction works as funded, by category | B | S-lb-030, S-lb-031 |
| Literature bands cited by the EC study | Baumgartner: double track 100 km/h, easy topography, 2 (1–4) M€/km; double track 300 km/h, easy, 3 (2–6) M€/km (older price basis, not stated); PwC HS2 comparators: rural sections 12.5–22.7 M€/km, urban 48.8–69.2; DTU: 11.47–62.72 M€/km | — | — | all-in (Baumgartner); construction (PwC, DTU) | B/C | S-lb-030 |

### 2d. Which cells are plausible against those bands (analysis)

- **USD 7 bn over 900–950 km (7.4–7.8 m/km)** sits inside the new-conventional-line band (EC interquartile USD 6.5–9.6 m/km) and next to Etihad Rail Stage Two (8.1) and Al Boraq over its full length (7.5). It is plausible as a **construction-level estimate for a 200 km/h-class mixed line in easy terrain**, which is what the 2008–2012 statements describe ("freight/container line", S-052). It is implausible as the all-in cost of a 250 km/h double-track line with stations and rolling stock.
- **USD 7 bn over >1,500 km (≤ 4.7 m/km)** is below every band except SAR North–South (1.9, single track, freight, excluding land) and the Baumgartner easy-topography figure for 100 km/h track. For a 250 km/h design-speed double-track line with signalling and stations it is not plausible as a 2026 all-in figure.
- **USD 26.667 bn over 900–950 km (28–30 m/km)** matches European HSR construction (25–39) and is below Haramain all-in (35.3). It would be plausible only if SR 100 bn bought the core line alone; the sources say it buys the whole programme, so this cell overstates the per-km cost.
- **USD 26.667 bn over >1,500 km (≤ 17.8 m/km)**, or 12.2 m/km if the 678 km of upgrades are included, sits between the new-conventional (6.5–9.6) and new-high-speed (13.1–18.4) bands of the EC study and matches China's 350 km/h infrastructure band (17–21) and Al Boraq over its HSR section (13.1). For a 250 km/h design-speed double-track line that **includes trains, stations and systems** (the Minister's scope, S-lb-002), this is the plausible cell.
- **USD 7 bn over the 35 km Riyadh Rail Link (200 m/km)** is metro-tunnel territory (the EC study's urban comparators run 48.8–69.2 M€/km; only predominantly tunnelled sections reach 81.7–105.5). A viaduct-heavy urban link could exceed the surface bands, but 200 m/km is five to six times the EC urban range. MEED, which covers the same tender in four articles, gives no package value. Not plausible as stated.

## 3. Hypotheses

| hypothesis | evidence found | grade | verdict (analysis) |
|---|---|---|---|
| (a) USD 7 bn = phase 1 (e.g. Jeddah–Riyadh only, or civil works only) | No source calls USD 7 bn a phase. Every carrier of the figure (2011, 2012, 2021, 2023, Apr 2025, ENR Jun 2026) applies it to the whole project, and from 2023 to the full >1,500 km six-line scheme (S-lb-009, S-lb-008, S-lb-007). The 2011–2012 scope was a "freight/container line" (S-052), which is a civil-works-level reading, but no source splits civil from systems. | — | **no evidence** as a phase; weak support as a civil-works-level scope by vintage (see c/d) |
| (b) USD 7 bn = one contract package or the private share of the former PPP | Construction Review alone (S-050) assigns USD 7 bn to the 35 km Riyadh package; MEED's four articles on that tender give no value (S-lb-005, S-lb-033, S-047); Railway Gazette gives none (S-lb-032); 200 m/km fails the plausibility test (2d). PPP side: the 2007 BOT bids were for a "$5,000 million" project (S-lb-013); the 2018 MoU value was USD 10.6 bn (S-lb-010); the 2023 IRJ wording is "cost and financing structure of the €6.5 bn (US$7 bn) project" (S-lb-011), i.e. the whole scheme, not a private share. | C (against) | **not supported**. The Construction Review attribution is most likely the programme's legacy figure pasted onto the package (analysis). |
| (c) SR 100 bn includes rolling stock, stations, land or financing, or the full >1,500 km programme, while USD 7 bn is track-only | Supported on scope: the Minister's SR 100 bn explicitly covers "البنية التحتية والقطارات وغيرها" (infrastructure, trains and other items; S-lb-002) for a >1,300 km (2022) / >1,500 km + 678 km upgrade (2023–2026) programme. The USD 7 bn / SR 26 bn figure dates from a 950 + 115 km scope described as a freight/container line (S-052, S-055, S-lb-012). Not supported on "track-only": no source says what USD 7 bn excludes. | C | **supported for scope growth and all-in content**; the exclusions of USD 7 bn are unknown |
| (d) Different price years; an earlier (2008–2011) estimate repeated by ENR | Strongly supported. SR 26 bn / USD 6.93–7.09 bn is the 2008–2011 tender basis (S-lb-014 snippet, S-052, S-lb-016, S-lb-017). The same USD 7 bn was carried unchanged by English trade press in 2012, 2021, Jan 2023, Dec 2023 and **Apr 2025** (MEED itself, for the >1,500 km scope, S-lb-008), while Arabic sources carried SR 100 bn from **Mar 2022** (S-lb-002, S-lb-003). MEED switched to SR 100 bn only after the CEO's Jan 2026 statement. ENR's June 2026 text (snippet) carries both: "$7 billion" as "total cost" and "$26.6 billion" for "the entire project" (S-049). | C | **best-supported reading**: the two figures are different vintages of the same programme, and ENR's headline reuses the legacy figure |
| (e) A reporting error (SR 7 bn? USD 27 bn misread?) | No correction found. "SR 7 bn" appears nowhere. "USD 27 bn" appears only as a rounding of 26.6 (Zawya headline, S-lb-004; MEED "$27bn" in one piece). The ENR snippet is internally inconsistent only if "total cost" and "entire project" mean the same thing; read as "cost on the old basis" vs "investment now seen as required", it is a carried-forward figure, not a typo. | — | **not an error in the figures**; an un-updated figure (see d) |

## 4. Conclusion (analysis; confidence: medium)

1. **The figures are not alternatives for the same quantity.** USD 7 bn (SR 26.25 bn at the peg; SR 26–26.6 bn in the 2011–2012 statements) is the 2008–2011 tender-era estimate for a 950 km Riyadh–Jeddah freight/container line plus a 115 km Dammam–Jubail link. SR 100 bn (USD 26.67 bn) is the 2022–2026 official estimate for the whole programme (>1,500 km of new track plus 678 km of upgrades, 250 km/h design speed) **including trains**, stated by the Minister of Transport in March and November 2022 and by SAR's CEO in January 2026. English trade press, including MEED until April 2025 and ENR in June 2026, kept repeating USD 7 bn for the enlarged scope; ENR's own text gives USD 26.6 bn for the entire project.
2. **The 3.81 × ratio therefore combines** scope growth (1,065 km → 1,500 km new + 678 km upgraded; by route-km alone ×1.4 new-track-only or ×2.0 including upgrades), the inclusion of rolling stock, stations and systems in the later figure, a higher design speed (250 vs the freight-line basis), and 11–15 years of cost escalation between the two price bases. None of these components is quantified by any source; the split above is route-km arithmetic, not a cost decomposition.
3. **Per-km plausibility** supports this reading: USD 7 bn is a conventional-line construction figure per km (7.4–7.8 m/km over the core), while SR 100 bn over the full scope (12.2–17.8 USD m/km) sits where a 250 km/h mixed line with stations and trains would be expected against the EC and World Bank bands and against Haramain (35.3 all-in, 300 km/h).
4. **What this does not resolve:** the price year of SR 100 bn (2022 statement reused in 2026: it may not have been re-based); whether SR 100 bn includes land, financing costs or contingency; what USD 7 bn excluded; and the Riyadh Rail Link package value (expected at award, which MEED Projects dated October 2026).

### What the cost register (W3) should carry

| register item | low | central | high | unit | price year | scope | source | status |
|---|---|---|---|---|---|---|---|---|
| Landbridge programme, as stated by SAR / MOT | SR 100 bn | SR 100 bn | null (apply the `reference-class-forecasting` uplift at W3; no published higher figure exists) | SAR bn, nominal | not stated (statements of Mar 2022, Nov 2022, Jan 2026; treat as 2022 nominal until re-based or confirmed) | >1,500 km new track + 678 km upgrades, 250 km/h design, infrastructure and trains ("وغيرها"); land, financing and contingency unknown | S-lb-001, S-lb-002, S-lb-003, S-046 | `derived` (official pre-tender estimate; no breakdown) |
| Landbridge top-down per km, whole programme | SR 45.9 m/km (over 2,178 km incl. upgrades) | — (no central: the two bounds are different denominators, not a distribution) | SR 66.7 m/km (over 1,500 km new track; upper bound) | SAR m per route-km, nominal | as above | all-in incl. trains | derived from the row above with S-057, S-lb-009 | `derived` |
| Landbridge legacy estimate (history only; not for appraisal) | SR 26 bn | SR 26.25 bn (USD 7 bn) | SR 26.6 bn | SAR bn, nominal | 2008–2011 tender basis | 950 km + 115 km freight/container line, exclusions unknown | S-lb-014, S-052, S-lb-016, S-051 | `sourced` (secondary) |
| Riyadh Rail Link (35 km) package value | null | null | null | SAR bn | — | design and build: viaducts, civil, utilities, signalling | S-050 rejected (see 3b) | `unknown` until the award notice |

Rule 3 applies to any use of these rows: ranges only, and "in the model" wording.

### What would resolve it (requests for Tariq to make; this run contacted no one)

1. **ENR full text** (subscriber access or a print copy): confirm the date, byline and what "$7 billion" is attributed to. S-049 / S-lb-034.
2. **Ministry of Transport X post of 16 Nov 2022** and the "في الصورة" broadcast of Jan 2026: the exact wording of SR 100 bn (what it includes; any price year). S-lb-003, S-lb-001.
3. **SAR's Riyadh Rail Link award notice** (MEED Projects expected October 2026): the first package value on the record. S-lb-018.
4. **Railway Gazette International, 11 Oct 2011**, and the 2008 SRO BOT tender documents: the basis of SR 26 bn (scope, exclusions, price year). S-lb-014, S-lb-017.
5. A SAR or NCP programme document (business case or PPP market sounding) giving the SR 100 bn breakdown by line, by cost element and by phase.

## Sources

All rows are in `docs/sources/index.csv` (accessed 2026-10-30, Asia/Riyadh). New in this run: S-lb-001 to S-lb-034. Reused from DATASCOUT_1H: S-002, S-046 to S-063. Quotes were captured through a page-extraction tool and must be byte-checked against the live page before they reach a report or the film (`source-citation` skill).
