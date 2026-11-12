> **Document version:** docs/sources/r1a-lines-facts.md v0.1 | 31 Oct 2026 | Author: rail-data-scout (R1a) | Status: draft

# R1a line facts: sourced facts for one line YAML per rail line

Access date for every row: 2026-10-31 (Asia/Riyadh). Row ids: `S-r1a-nnn` in `docs/sources/r1a-lines.csv` (77 new rows); older ids (S-001 to S-091, S-lb-*, S-cp1-*) are reused from `docs/sources/index.csv`, not duplicated.

**Status key.** `verified` = read on the publisher's own page on 31 Oct 2026. `secondary` = aggregator, press or encyclopaedia, with the primary still to find. `unverified` = could not be read (search summary only, paywall, 403, DNS failure or no source). Nothing in this file feeds a model without a row; a figure with no row is not in this file.

**Read-method caveat.** Quotes were captured from the fetch tool's output. Verbatim wording was checked against that output but not against a raw page dump. Re-check quotes before any public use.

## 0. Makkah to Jeddah: the answer the brief asked for first

The brief's 43 min for 77 km is **secondary only**. It is in Wikipedia (S-005, reused; re-read 31 Oct 2026: "77-kilometre (48 mi) ride from Mecca to Al-Sulimaniyah–Jeddah takes 43 minutes"). No operator or primary timetable could be read:

- sar.hhr.sa/en/timetable is a search form with no times printed (S-r1a-003, unverified). The HHR home page prints no times or fares (S-r1a-004, verified absence).
- The other values found, all from non-primary sources, are listed in the table below. None is a measured or timetabled figure from SAR.

| Value | Source id | Status | Notes |
|---|---|---|---|
| 43 min, 77 km (Makkah to Al-Sulimaniyah) | S-005 | secondary | Wikipedia; the average 107 km/h. Primary to find: SAR/HHR timetable or statement. |
| 28 to 30 min (Makkah to Jeddah) | S-r1a-006 | secondary | Travel guide, fares stamped 28 Oct 2026. Table row "مكة إلى جدة | 28 دقيقة إلى 30 دقيقة". |
| 21 min (Makkah to Jeddah, pre-opening) | S-r1a-005 | unverified | Pre-opening projection, not a measured time. |
| 30 min (Jeddah central to Makkah) | S-r1a-007 | unverified | One press report; station pair not precise. |
| 1 h 45 min, 07:00 to 08:45 (Jeddah to Makkah, "Express") | S-r1a-008 | secondary | Aggregator, undated. At 77 km this is about 44 km/h, which does not fit a 300 km/h line. Treated as an error or a different route until a primary says otherwise (C-r1a-01). |

**Answer.** Use 43 min (S-005) as the working value with `secondary` status and a `primary_to_find`. Do not present it as verified. The 21 min figure is a projection and the 1 h 45 min figure is implausible. A dated sample by a person on the public HHR booking search would close this. No agent action was taken, and none should be taken without approval.

## 1. Haramain HSR (`hhr`)

| field | value | source id(s) |
|---|---|---|
| name EN | Haramain High Speed Railway | S-002 (Wikipedia name), S-001 (SAR page header) |
| name AR | قطار الحرمين السريع | unverified: the Arabic name was not read on a SAR page this run (the line-yaml example uses it; treat as a placeholder) |
| operator | Saudi Arabia Railways (SAR) / Haramain High Speed Railway (booking site) | S-001 (SAR page header, verified); S-r1a-001 |
| Renfe role | Renfe press release on 2023 ridership (secondary, S-012); O&M by the Al-Shoula Spanish-Saudi consortium per Wikipedia (S-008, secondary); O&M term 12 yrs / to 2030 / to 2038 conflicting (S-011, unverified) | S-012, S-008, S-011 |
| status | in service (GASTAT 2025: HHR is the largest share of passenger-km, 76.0 %; on-time 97.8 %) | S-013, S-014 (verified GASTAT) |
| opened | officially inaugurated 25 Sep 2018; opened to the public 11 Oct 2018; airport branch 11 Dec 2019 | S-r1a-019 (secondary), S-r1a-020 (secondary) |
| main line length | 449.2 km main line + 3.75 km airport branch | S-002 (secondary) |
| design speed | 320 or 360 km/h | S-003 (secondary) |
| operating speed | 300 km/h in service | S-003 (secondary); quote "trains are limited to a top speed of 300 km/h" |
| track | double (assumed by the line type) | unverified: no source read for track count |
| electrification | unverified | none read |
| gauge | standard (1435 mm in the schema; not read) | unverified |
| layer | existing | S-013 (GASTAT ridership establishes service) |
| km-posts | none published in any source read | (see S-006: 17/94/261 km unsourced) |

### 1a. Ordered stations

| # | EN (as SAR prints) | AR (as SAR prints) | km-post | source |
|---|---|---|---|---|
| 1 | Makkah | مكة (dropdown: مكة المكرمة) | 0 (not published) | S-001, S-r1a-002 |
| 2 | Al-Sulimaniyah - JEDDAH | السليمانية - جدة | 77 km from Makkah (secondary, S-005) | S-001, S-r1a-002 |
| 3 | AIRPORT - JEDDAH | المطار- جدة (branch, 3.75 km) | branch; distance from main line not published | S-001, S-r1a-002, S-004 |
| 4 | KAEC | مدينة الملك عبدالله الاقتصادية | not published (S-006 unverified) | S-001, S-r1a-002 |
| 5 | Madinah | المدينة (dropdown: المدينة المنورة) | 449.2 km main line total (secondary, S-002) | S-001, S-r1a-002 |

Note: the Wikipedia list calls the Jeddah station "Jeddah Central" and gives "Jeddah Central ... out of service from 29 September 2019 to 31 March 2021" (S-r1a-020). SAR's booking site prints "Al-Sulimaniyah - JEDDAH" (C-r1a-03).

### 1b. Timetable sample (sampled 2026-10-31)

| item | value | source id | status |
|---|---|---|---|
| trips per day | not found on any primary page; a headline says "16 a day" (undated) | S-r1a-018 | unverified |
| first and last departure | not found | none | unverified |
| Makkah to Jeddah | 43 min (Wikipedia); 28 to 30 min (travel guide, 28 Oct 2026); 21 min (projection); 30 min (Jeddah central, press); 1 h 45 min (aggregator, Express 07:00 to 08:45) | S-005; S-r1a-006; S-r1a-005; S-r1a-007; S-r1a-008 | see section 0 |
| Mecca to Medina | 2 h 20 min (HHR 300 Special, 07:00 to 09:20, aggregator); "around 2 hours" (Wikipedia) | S-r1a-009; S-r1a-010 | secondary |
| airport station to Makkah | 54 min; "17 trips" quoted for Thursday 12 Nov 2026 (a future date, so not a sample) | S-r1a-011 | secondary |

### 1c. Fares sample (economy / business, SAR; sampled 2026-10-31 from a guide with fares checked 28 Oct 2026)

| route | economy | business | source | status |
|---|---|---|---|---|
| Makkah to Jeddah (Al-Sulimaniyah) | 43 | 90 | S-r1a-012 | secondary; direction unclear on the page |
| Makkah to KAIA (airport) | 65 | 101.4 | S-r1a-013 | secondary |
| Makkah to Madinah | 162 (or 150 per Gulf News, undated) | 455 | S-r1a-014 (unverified); S-r1a-016 (unverified) | unverified |
| Jeddah to Madinah | 135 (or 125 per Gulf News) | 375 | S-r1a-015 (unverified); S-r1a-016 (unverified) | unverified |
| Jeddah to Makkah, 2018 launch | 40 | 50 | S-r1a-017 | unverified; historical |

Fare notes: the guide says fares are before VAT and fees (search summary; unverified). No SAR/HHR fare table was readable. Fares are perishable: re-sample before CP6.

### 1d. Conflicts
See C-r1a-01 to C-r1a-04 at the end of this file.

## 2. SAR North passenger line (`sar-north-passenger`)

| field | value | source id(s) |
|---|---|---|
| name EN | North passenger line (Riyadh to Al Haditha) | S-018 (SAR, verified) |
| name AR | خط الشمال بين الرياض والقريات (Riyadh to Al Qurayyat; SAR's Arabic page) | S-r1a-026 (verified). Note: the Arabic page names the line to Qurayyat; the English page runs to Al Haditha (C-r1a-05). |
| operator | Saudi Arabia Railways (SAR) | S-017 (verified) |
| status | in service (fares on sale; SAR lists the line as its passenger line) | S-017, S-r1a-021 to S-r1a-024 |
| length | 1,250 km (SAR, "With a length of 1,250 Km") | S-017 (verified); Wikipedia 1,242 km (S-022, secondary; SAR is primary) |
| design or operating speed | unverified: not read | none |
| track | unverified | none |
| electrification | unverified | none |
| gauge | unverified | none |
| layer | existing | S-017 |
| km-posts | not published | none |

### 2a. Ordered stations

| # | EN (SAR) | AR | opening (secondary) | source |
|---|---|---|---|---|
| 1 | Riyadh (North) | not printed on SAR's Arabic page | 26 Feb 2017 | S-018; S-r1a-030; S-r1a-031 |
| 2 | Majmaah | not printed | 26 Feb 2017 | S-018; S-r1a-030; S-r1a-031 |
| 3 | Qassim (Buraydah) | not printed | 2017 (Wikipedia line page) or 2018 (list page) | S-018; S-r1a-030; S-r1a-031 (C-r1a-05) |
| 4 | Hail | not printed | 23 Nov 2017 (line page) or 2018 (list page) | S-018; S-r1a-030; S-r1a-031 (C-r1a-05) |
| 5 | Jouf (Sakaka) | not printed | 7 Nov 2018 (line page) or 2018 (list page) | S-018; S-r1a-030; S-r1a-031 (C-r1a-05) |
| 6 | Qurayyat | not printed | 31 Mar 2022 (line page) or 2018 (list page) | S-018; S-r1a-030; S-r1a-031 (C-r1a-05) |
| 7 | Al Haditha (terminus, SAR) | not printed | "proposed" per the Wikipedia list page | S-018; S-r1a-031 (C-r1a-05) |
| – | Al-Zulfi | not on SAR's list | "planned (no date)" per Wikipedia line page | S-r1a-030 (secondary) |

km-posts: not published. Station Arabic names: not printed on the SAR Arabic home page (S-r1a-028, verified absence); to be taken from the SAR station page or timetable.

### 2b. Timetable sample
No timetable was readable. The SAR home widget prints no departure times (S-r1a-025). Trips per day and journey times: unverified. The passenger charter PDF was not readable (S-r1a-029, unverified; metadata "last modified 4 Dec 2025" only).

### 2c. Fares sample (SAR home widget, read 31 Oct 2026; currency not printed; cards link to searches pre-filled for 25 Oct 2026 outbound and 1 Nov 2026 return, 1 adult)
| route | "from" fare | source |
|---|---|---|
| Riyadh to Hail | 125 | S-r1a-021 (verified) |
| Riyadh to Qassim | 80 | S-r1a-022 (verified) |

Class and low/high ranges: not shown. Treat as "from" prices only.

## 3. SAR North freight line (`sar-north-freight`)

| field | value | source id(s) |
|---|---|---|
| name EN | North freight line | S-020 (SAR, verified) |
| name AR | not read on SAR's Arabic page (which names only the car-shipping route) | S-r1a-026 (C-r1a-06 note) |
| operator | SAR | S-019 (verified) |
| status | open (Wikipedia list marks Jalamid, Hail, Zabirah and Ras Al-Khair as open, no dates) | S-019; S-r1a-032 (secondary) |
| length | 1,550 km (SAR, "With a length of 1,550 Km") | S-019 (verified) |
| speed, track, electrification, gauge | unverified | none |
| layer | existing | S-019 |

### 3a. Ordered points (SAR order)
1. Al-Jalamid mine (Northern Province) — S-020, S-r1a-032 (Wikipedia: "Jalamid")
2. Jouf — S-020
3. Hail — S-020, S-r1a-032
4. AlBaithah Junction — S-020 (Wikipedia: "Zabirah"; see C-r1a-06)
5. Ras AlKhair — S-020, S-r1a-032
km-posts: not published. Arabic names: not printed.

Proposed/under construction (Wikipedia list, secondary): Haditha, Al-Jawf junction, Jubail, Bosajata junction (S-r1a-032).

## 4. SAR East passenger line (`sar-east-passenger`)

| field | value | source id(s) |
|---|---|---|
| name EN | East passenger line (Riyadh to Dammam) | S-025 (verified) |
| name AR | خط الشرق بين الرياض والدمام | S-r1a-027 (verified) |
| operator | SAR | S-024 (verified) |
| status | in service (fares on the SAR home page; SAR says the East line runs daily, unverified) | S-024; S-r1a-023, S-r1a-024; S-r1a-043 (unverified) |
| length | 733 km double track (SAR, "double track with a total length of 733 km") | S-024 (verified) |
| network total | "approximately 1,775 km" (SAR East network, incl. freight) | S-027 (verified); 733 + 566 = 1,299 km (C-006) |
| speed, electrification, gauge | unverified | none |
| opened (secondary) | SRO Dammam–Riyadh stations opened 1981 (Dammam, Abqaiq, Al-Hofuf, Riyadh) | S-r1a-033 |
| layer | existing | S-024 |

### 4a. Ordered stations
| # | EN (SAR) | AR | source |
|---|---|---|---|
| 1 | Riyadh | not printed | S-025 |
| 2 | Hufuf (Al-Hofuf) | not printed (SAR and Wikipedia spelling differ) | S-025; S-r1a-033 |
| 3 | Abqaiq | not printed | S-025; S-r1a-033 |
| 4 | Dammam | not printed | S-025; S-r1a-033 |

km-posts: not published. Al-Kharj: **not a passenger stop on SAR's list** (S-025 lists four stops; S-026 places Al-Kharj on the freight line). The Dammam station article says Kharj lies on a Dammam–Riyadh line (unverified, S-r1a-035). Status open (C-r1a-09; extends C-006).

### 4b. Timetable sample (sampled 2026-10-31)
| item | value | source id | status |
|---|---|---|---|
| Riyadh to Dammam express 08:00 to 11:35 (3 h 35 min), aggregator | 3h 35m | S-r1a-040 | secondary |
| Riyadh to Dammam 4 h 10 to 4 h 30 (aggregators; distance 449 km per Seat61, 480 km per another) | 4h10–4h30 | S-r1a-041 | unverified |
| trips per day | "daily" (SAR statement via search summary); aggregator "every 4 hours" and two departures 16:30 and 20:35 | S-r1a-043; (aggregator, not logged separately) | unverified |
| first and last departure | not found | none | unverified |

The SAR home widget prints no times (S-r1a-025).

### 4c. Fares sample (SAR home widget; currency not printed; "from" prices)
| route | "from" | source | status |
|---|---|---|---|
| Hufuf to Dammam | 35 | S-r1a-023 | verified |
| Dammam to Riyadh | 90 | S-r1a-024 | verified |
| Riyadh to Dammam (aggregator: economy about 90, business about 180; another aggregator 20 to 150) | 90 / 180 / 20–150 | S-r1a-042 | unverified |

## 5. Dammam–Riyadh legacy freight line, SAR East freight (`sar-east-freight-legacy`)

| field | value | source id(s) |
|---|---|---|
| name EN | East freight line (the brief's "Dammam–Riyadh legacy freight line") | S-026 |
| operator | SAR; dry port concession to Saudi Global Ports (secondary, unverified) | S-026; S-r1a-036 |
| status | in service (freight; SAR lists it as its freight line; 2025 operational testing of a new Al-Ahsa freight line reported, unverified) | S-026; S-r1a-039 |
| length | 566 km (SAR, "The freight line is 566 km long") | S-026 (verified); 556/550/546 km (search summaries, unverified: S-r1a-038; C-r1a-10) |
| speed, track, electrification | unverified | none |
| layer | existing | S-026 |

### 5a. Ordered points (SAR order)
| # | EN (SAR) | AR | km-post | source |
|---|---|---|---|---|
| 1 | King Abdulaziz Port (Dammam) | not printed | not published | S-026; S-r1a-034 (Wikipedia: "King Abdul Aziz Port", opened 1950s) |
| 2 | Al-Ahsa | not printed | not published | S-026 |
| 3 | Buqayq | not printed | not published | S-026 |
| 4 | Al-Kharj | not printed | not published | S-026; S-r1a-034 (no date) |
| 5 | Haradh | not printed | not published | S-026; S-r1a-034 |
| 6 | Al-Tawdhihiyah | not printed | not published | S-026; S-r1a-034 |
| 7 | Riyadh (dry port) | not printed | not published | S-026; S-r1a-034 (Riyadh Dry Port opened 1950s; secondary) |

Dry port: Saudi Global Ports concession to run the Riyadh Dry Port ecosystem, target 1.5 million containers a year by 2030 (S-r1a-036, unverified). MOT goal of tripling Dammam–Riyadh freight capacity (S-r1a-037, unverified).

## 6. Riyadh Metro (`riyadh-metro-l1` to `riyadh-metro-l6`)

Operator: not read (riyadhmetro.sa did not resolve, S-r1a-054). The RCRC metro page prints the 85-station total but no line table (S-r1a-053, verified absence; S-034 for the 85 total). Per-line data is secondary (Wikipedia, S-r1a-045 to S-r1a-050).

| line | colour | length km (Wikipedia) | stations (Wikipedia) | termini (Wikipedia) | opened (Wikipedia) | Zawya length km (unverified) | ids |
|---|---|---|---|---|---|---|---|
| riyadh-metro-l1 | Blue (Line 1) | 38 | 25 | SAB Bank ↔ Ad Dar Al-Baida | 1 Dec 2024 | 38 | S-r1a-045; S-r1a-052 |
| riyadh-metro-l2 | Red (Line 2) | 25.3 | 15 | King Saud University ↔ King Fahd Sports City | 15 Dec 2024 | 25.3 | S-r1a-046; S-r1a-052; S-035 |
| riyadh-metro-l3 | Orange (Line 3) | 40.7 | 22 | Jeddah Road ↔ Khashm Al-An | 5 Jan 2025 | 41.1 | S-r1a-047; S-r1a-052; S-036 |
| riyadh-metro-l4 | Yellow (Line 4) | 29.6 | 9 | KAFD ↔ Airport T1-2 | 1 Dec 2024 | 29.7 | S-r1a-048; S-r1a-052 |
| riyadh-metro-l5 | Green (Line 5) | 12.9 | 12 | Ministry of Education ↔ National Museum | 15 Dec 2024 | 13.3 | S-r1a-049; S-r1a-052; S-035 |
| riyadh-metro-l6 | Purple (Line 6) | 29.9 | 11 | KAFD ↔ An Naseem | 1 Dec 2024 | 28.8 | S-r1a-050; S-r1a-052 |

**Totals.** 176 km and 6 lines (S-033, S-r1a-051). 85 stations (S-034, verified). Per-line sums: lengths 176.4 km (Wikipedia) and 176.2 km (Zawya), both within 0.4 km of 176 (C-r1a-07); station counts 94 (the per-line counts double-count interchanges; analysis) against 85 (C-r1a-08).

**Stations, ordered.** Not captured for any line in this run (gap).

**Timetable and fares.** Not captured (Riyadh Metro fares and frequencies are not in the sources read). Gap.

## 7. Saudi Landbridge (`landbridge`), committed / under procurement

| field | value | source id(s) |
|---|---|---|
| name EN | Saudi Landbridge (rail) | S-lb-001 to S-lb-008 (reused) |
| name AR | not read this run | unverified |
| operator | SAR (state procurement; PPP talks failed; phased delivery) | S-059 (secondary), S-054 |
| status | committed / under procurement (Riyadh section tendered; no award found) | S-r1a-055, S-r1a-059 (see Riyadh Rail Link) |
| length | Riyadh–Jeddah new line 900 km (MEED, Jan 2026), 920 km (Saudi Auto), 950 km (2021 press), 958 km (Wikipedia 2013 design contract); total new track more than 1,500 km | S-054, S-056, S-055, S-057; C-002 |
| design/operating speed | passenger 250 km/h design, up to 220 km/h operating; freight 140 design, 120 operating (2011 press, secondary) | S-058 |
| cost | SR 100 bn (USD 26.6 bn) whole programme, price year not stated; USD 7 bn legacy whole-project estimate (2011 and 2021) | S-046, S-047, S-048, S-lb-001 to S-lb-003; S-051, S-052, S-053, S-049 (see C-001 in docs/sources/conflicts.md) |
| layer | committed / under procurement | S-059; S-r1a-055 |
| track, electrification, gauge | unverified | none |

### 7a. Intermediate stations (planned; locations not given)
| name in source | source | status |
|---|---|---|
| Jumoum (Jamuma; Al-Jumum, الجموم, per the project owner) | S-062 (Saudi Auto, "three stations in Jumoum, Muwai and Dawadmi"); S-lb-018 (MEED Projects pid 114639 spelling "Jamuma, Moya and Al-Doadmi", paywalled, no location); S-063 (owner's identification, unverified) | **site unlocated** |
| Muwai (Moya) | S-062; S-lb-018 | site unlocated |
| Dawadmi (Al-Doadmi) | S-062; S-lb-018 | site unlocated |

Al-Jumum (governorate of Makkah region): S-064 (verified, makkah.gov.sa); population: S-065 (89,575 governorate, Census 2022 via citypopulation.de, secondary), S-066 (41,089 place, secondary), S-067 (98,575, unverified). Distances of about 25 km to Makkah and 72 km to Jeddah are unsourced (S-068); measure on the OSM road graph (R1a) only if a station location is adopted. Do not place the station on a map without a source (rule: "site unlocated").

## 8. Riyadh Rail Link (`riyadh-rail-link`), committed / under procurement

| field | value | source id(s) |
|---|---|---|
| identification | the Riyadh section of the Saudi Landbridge; MEED calls it "a new north-to-south railway line across the capital" and "the Riyadh Rail Link" | S-r1a-056 (secondary); S-060 (secondary) |
| length | 35 km double track, connecting SAR's North-South Railway to the Eastern Railway network | S-r1a-055 (secondary); S-060 |
| status | under procurement: design-and-build tender issued (29 Jan 2026 per MEED 31 Aug 2026); commercial proposals 30 Jun 2026; clarifications July 2026; award "expected imminently" at 31 Aug 2026 | S-r1a-055; S-lb-005 (MEED Jul 2026); S-060 (12 Feb 2026) |
| bidders (not awardees) | CCECC with Al-Ayuni; Nesma & Partners with CHEC; Al-Rashid with IC Ictas and Saipem; Saudi Binladin Group | S-r1a-057 (secondary) |
| design lead | Typsa (MEED headline, unverified) or Sener (TradeArabia headline, unverified) | S-r1a-058; S-r1a-059 (C-r1a-11) |
| package value | USD 7 bn (one outlet, uncorroborated; USD 200 m/km); MEED gives no value | S-050 (see C-001) |
| stations | none named in the source read (endpoints only: Riyadh, Jeddah, Dammam, Yanbu, King Abdullah Port in the wider network text) | S-r1a-055 |
| award date | none found after 31 Aug 2026 (not checked again beyond that date) | gap |
| layer | committed / under procurement | |

## 9. GCC railway, Saudi section (`gcc-railway-ksa`), announced / planned

| field | value | source id(s) |
|---|---|---|
| status | announced / planned; design-consultancy tender issued 7 May 2026, bids due 30 Jun 2026 | S-030 (secondary, MEED 12 May 2026) |
| length | about 672 km in Saudi Arabia | S-029 (secondary) |
| passenger design speed | 220 km/h | S-031 (secondary) |
| route | Kuwait border to UAE border; Dammam and Al-Khafji not confirmed in text read | S-032 (secondary); C-008 |
| stations, timetable, fares | none | gap |
| layer | announced/planned. The design tender is procurement; the route is not committed. Coordinator to decide the layer label. | |

## 10. Hejaz Railway (`hejaz-railway`), historical

| field | value | source id(s) |
|---|---|---|
| name EN | Hejaz Railway (Damascus–Medina; Saudi section) | S-r1a-066 (secondary) |
| opened | Medina reached on 1 Sep 1908 | S-r1a-066 (secondary; Wikipedia) |
| length | Damascus–Medina 1,300 km (Wikipedia text); Saudi section length not stated | S-r1a-070 (secondary; C-r1a-12) |
| gauge | narrow (no mm given) | S-r1a-077 (secondary) |
| closure | Saudi section "remained closed after 1920 and the fall of the Ottoman Empire" (no single date); 1924 plans dropped | S-r1a-068; S-r1a-069 (secondary); S-r1a-074 (Al-Ula station abandoned 1920, unverified) |
| preservation | Medina station is the Hejaz Railway Museum (opened 2006, secondary); ICOMOS record and UNESCO tentative list entry not read | S-r1a-071 (secondary); S-r1a-072, S-r1a-073 (unverified) |
| primary | Saudi Heritage Commission: not found | S-r1a-076 (unverified) |
| layer | historical | |
| status | closed; no service | |

### 10a. Saudi section stations with km markers (Wikipedia route table, secondary; origin of km not stated in the extract; S-r1a-067)
| station (EN as printed by Wikipedia) | km |
|---|---|
| Halat Ammar | 591.0 |
| Dhat al-Hajj | 610.0 |
| Bir Ibn Hermas | 635.0 |
| El-Hazim | 654.0 |
| Al-Muhtatab | 667.0 |
| Tabuk | 692.0 |
| Wadi al-Athily | 710.0 |
| Dahr al-Hajj / Qareen al-Ghazal | 737.0 |
| Dar al-Hajj | 743.0 |
| Al-Mustabagha | 753.0 |
| Al-Ukhaydir | 757.0 |
| Khamisa | 773.0 |
| Al-Assda (al-Khanzira) | 794.4 |
| Al-Mu'azzam | 830.0 |
| Khashm Sana' | 855.0 |
| Al-Muteli' | 883.0 and 904.0 |
| Dar al-Hamra | 885.0 |
| Abu Taqa | 912.0 |
| Al-Muzhim | 938.0 |
| Mabrakat al-Naka | 946.0 |
| Mada'in Saleh | 958.0 |
| Al-'Ula | 983.0 |
| Al-Badae' | 994.0 |
| Maghira | 1,003.0 |
| Matran | 1,029.0 |
| Zumrud | 1,048.0 |
| Bir Jadid | 1,079.0 |
| Al-Tawira | 1,099.0 |
| Wiban | 1,115.0 |
| Al-Madraj | 1,126.0 |
| Hadiyya | 1,144.0 |
| Jada'a | 1,166.3 |
| Abu al-Na'am | 1,176.0 |
| Stabl Antar | 1,194.5 |
| Al-Bweir | 1,215.0 |
| Bir Nassif | 1,245.0 |
| Al-Hafdour | 1,273.0 |
| Bir Abu Jabir | 1,290.5 |
| Bouat | 1,303.0 |
| Al-Hafirah | 1,309.0 |
| Bir Osman | 1,315.5 |
| Medina | 1,320.5 |
| Medina Citadel | 1,322.0 |

Derived (analysis, not a sourced length): 1,320.5 − 591.0 = 729.5 km between the first and last listed Saudi-section markers. This conflicts with the stated 1,300 km for Damascus–Medina (C-r1a-12). Arabic station names: not captured.

## Other items (announced only, or not found)
| item | status | ids |
|---|---|---|
| Jeddah Metro Blue Line, preliminary design consultancy tenders (reported 22 Jan 2026) | announced only; unverified | S-r1a-062 |
| Ras Al-Khair to Jubail rail link tenders ("by years end"; date not read) | announced only; unverified | S-r1a-063 |
| Qiddiya high-speed rail | no dated tender or contract found | S-r1a-064 |
| Makkah metro | no dated tender or contract found | S-r1a-065 |
| SAR phosphate second track, Eastern Province (freight; contract to Alomaier, about SR 4 bn-plus, MEED 20 Aug 2026) | dated contract, unverified; out of scope as a passenger line | S-r1a-061 |
| Landbridge Jubail–Dammam section, inaugurated April 2024 (ENR index summary) | unverified | S-r1a-060 |
| Riyadh Metro Red Line extension award (LinkedIn post) | not used: not a primary or a readable source | none |

## Conflicts, proposed for docs/sources/conflicts.md (C-r1a-nn)

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

## Notes for the coordinator

1. **line-yaml example.** The skill example cites S-013 (GASTAT passenger-km) for the observed 43 min Makkah–Jeddah pair and S-012 (Renfe press) for station km-posts. Both ids are wrong for those facts; the correct id for 43 min is S-005 (secondary). Not edited here (outside this track's outputs).
2. **Gaps that block the line YAMLs:** HHR and SAR timetables, first and last departures, trips per day, Arabic station names for the SAR lines, electrification and gauge for all lines except Hejaz, Riyadh Metro per-line stations, and operator details for the Riyadh Metro.
3. **Human actions (not agent actions):** a dated sample of the HHR booking search for Makkah–Jeddah and Riyadh–Dammam, done by a person on the public site.
4. **Layer labels.** Landbridge and Riyadh Rail Link: committed / under procurement. GCC railway: announced / planned, with the design tender as the only procurement step. Hejaz: historical. Others: existing.
5. **Announced-only items** have no line YAML. Jeddah Metro, Ras Al-Khair–Jubail, Qiddiya and Makkah metro stay in this file only.
