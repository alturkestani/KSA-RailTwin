> **Document version:** docs/data-sources.md v0.3 | 31 Oct 2026 | Author: rail-data-scout (DATASCOUT_1H); R1a status table by the R1a builder and rail-data-scout (R1a) | Status: draft

# Data sources

This document follows TrafficTwin's source-table format. Every number here carries a source id (`S-nnn`, `docs/sources/index.csv`; human view `docs/sources/index.md`). Conflicts are in `docs/sources/conflicts.md` (`C-nnn`); the per-region governorate list is in `docs/gastat-regions.md`; licences are in `docs/licences.md` (the DATASCOUT_1H fragment was merged at PILOT_MERGE and deleted at CP2_PREP). Access date for this pass: **2026-10-30** (Asia/Riyadh).

Status values:
- `verified`: read on the publisher's own site or document on the access date.
- `secondary`: aggregator, press or trade press.
- `unverified`: unreadable (paywall, HTTP 403/404, DNS failure, snippet only) or no source found.

Quotes in the index were captured through a page-extraction tool. Byte-check them against the live page before they enter the report or the film.

Planned lines are **announced/planned**, never existing (rule 5).

## Verified in this pass (PROJECT.md section 4, fact by fact)

Each fact shows the brief's starting value, the value the source prints, the source id and its status. The brief is not overwritten.

| section 4 item | fact | brief value | source value | source | status |
|---|---|---|---|---|---|
| Haramain HSR | stations | Makkah (Rusaifah), Jeddah (Sulaymaniyah), KAIA, KAEC (Rabigh), Madinah | Makkah; Al-Sulimaniyah - JEDDAH; AIRPORT - JEDDAH; KAEC; Madinah | S-001 | verified |
| Haramain HSR | length | about 450 km (453 km) | 453.0 km infobox; 449.2 km main line + 3.75 km airport branch | S-002 | secondary |
| Haramain HSR | speed | 300 km/h | 300 km/h in-service limit; 320/360 km/h design | S-003 | secondary (C-004) |
| Haramain HSR | KAIA position | main-line stop | on a branch | S-004 | secondary (C-004) |
| Haramain HSR | Makkah–Jeddah | 77 km, about 43 min | 77 km, 43 min | S-005 | secondary |
| Haramain HSR | distances 17/94/261 km | 0/77/17/94/261 km | not found | S-006 | unverified |
| Haramain HSR | contract history | civil works packages; Spanish consortium for systems, operation, trains | package 1: SAR 6.79 bn, Al Rajhi Alliance, Mar 2009; phase II: Al-Shoula consortium, 26 Oct 2011; 35 trains for EUR 1.257 bn | S-007, S-008, S-009 | secondary |
| Haramain HSR | cost | to be researched | USD 9.4 bn "total contract value" (scope not stated) vs 6,736 million (Spanish press) | S-010 | unverified (C-004) |
| Haramain HSR | O&M term | not in brief | 12 years vs "until 2030" vs "to 2038" | S-011 | unverified (C-004) |
| Haramain HSR | ridership 2023 | about 6.97 M | 6.97 M | S-012 | secondary |
| Haramain HSR | ridership 2025 (new) | — | about 2,743 M passenger-km in 2025 (76.0 % of national rail passenger-km); on-time 97.8 % | S-013, S-014 | verified |
| North line (SAR) | passenger length | about 1,250 km | 1,250 km (SAR); 1,242 km (Wikipedia) | S-017, S-022 | verified |
| North line (SAR) | passenger route | Riyadh–Majmaah–Qassim–Hail–Jouf–Qurayyat–Al Haditha | same places | S-018 | verified |
| North line (SAR) | freight length | about 1,550 km | 1,550 km | S-019 | verified |
| North line (SAR) | network total (new) | — | 2,750 km | S-021 | verified (C-006) |
| North line (SAR) | cost | to be researched | SAR 20 bn (Wikipedia, uncited) vs SR 10 bn (2017 press snippet) | S-023 | unverified (C-007) |
| East line (SAR) | passenger length | 733 km double track | 733 km double track | S-024 | verified |
| East line (SAR) | passenger stations | Riyadh–Al-Kharj–Hofuf–Abqaiq–Dammam | Riyadh, Hufuf, Abqaiq, Dammam; Al-Kharj is on the 566 km freight line | S-025, S-026 | verified (C-006) |
| Saudi Landbridge (planned) | Riyadh–Jeddah length | about 950 km (MEED about 900 km) | 900 / 920 / 950 / 958 km | S-054, S-055, S-056 | secondary (C-002) |
| Saudi Landbridge (planned) | total new track | more than 1,500 km | more than 1,500 km | S-057 | secondary |
| Saudi Landbridge (planned) | speed | about 220–250 km/h | passenger design 250, operating 220 km/h | S-058 | secondary (C-002) |
| Saudi Landbridge (planned) | cost | SR 100 bn (USD 26.6 bn) vs USD 7 bn | SR 100 bn (USD 26.6 bn), whole programme, SAR CEO via MEED; USD 7 bn = 2011 legacy estimate, ENR page unread, one outlet assigns it to the Riyadh package | S-046 to S-053 | secondary / unverified (C-001, unresolved) |
| Saudi Landbridge (planned) | delivery | Chinese PPP talks ended; phased; target 2034 | same | S-059 | secondary |
| Saudi Landbridge (planned) | Riyadh section (new) | — | 35 km double track, tendered Feb 2026 | S-060 | secondary |
| Saudi Landbridge (planned) | MEED Projects pid=114639 | cite for the station list | subscriber gate; no station list visible | S-061 | unverified |
| Saudi Landbridge (planned) | "Jamuma" = Al-Jumum | confirmed by Tariq | stated by project owner (not published); one trade site names "Jumoum" without a location | S-062, S-063 | unverified (site unlocated) |
| GCC railway (planned) | Saudi section length | about 672 km | about 672 km | S-029 | secondary (C-008) |
| GCC railway (planned) | route | Al-Khafji–Dammam–Al-Batha | Kuwait border to UAE border; Dammam not confirmed | S-032 | secondary |
| GCC railway (planned) | design tenders | in 2026 | design-consultancy tender issued 7 May 2026 | S-030 | secondary |
| GCC railway (planned) | passenger speed | 220 km/h | 220 km/h | S-031 | secondary |
| Riyadh Metro | lines, length, stations | 6 lines, 176 km, 85 stations | 6 lines, 176 km, 85 stations (Wikipedia); 85 stations (RCRC, 2018) | S-033, S-034 | secondary; stations verified |
| Riyadh Metro | opening | phased Dec 2024 to Jan 2025 | Lines 1, 4, 6: 1 Dec 2024; Lines 2, 5: 15 Dec 2024; Line 3: 5 Jan 2025 | S-035, S-036, S-037 | secondary (C-005) |
| Riyadh Metro | cost | ENR "USD 25 B" (verify) | USD 25 bn (RCRC CEO via Argaam); USD 22.5 bn (Wikipedia); ENR not located | S-038, S-039 | secondary (C-005) |
| Rail ridership | rail passengers 2023 | 30.3 M | 30.3 M | S-041 | secondary (GASTAT 2023 PDF 404) |
| Rail ridership | intercity passenger-km 2023 | 2,618 M | search-index extraction only | S-042 | unverified (C-009) |
| Rail ridership | 2024 and 2025 (new) | — | passengers 42.7 M (2024), 156.4 M (2025); intercity 11.6 M, 10.9 M; passenger-km 3,724.3 M, 3,609.3 M | S-043, S-044, S-045 | verified |
| Al-Jumum | governorate, Makkah region | Makkah region | محافظة الجموم, Makkah Region Emirate | S-064 | verified |
| Al-Jumum | population (Census 2022) | 89,575 | 89,575 (governorate); 41,089 (town); 98,575 on the governorate page (no year, no source) | S-065, S-066, S-067 | secondary (C-003) |
| Al-Jumum | about 25 km from Makkah, 72 km from Jeddah; not on Haramain | as stated | no source found | S-068 | unverified (to measure in R1a) |
| City populations | Riyadh | 6.92 M | 6,924,566 | S-080 | secondary |
| City populations | Jeddah | 3.71 M | 3,712,917 | S-081 | secondary |
| City populations | Makkah | 2.39 M | 2,385,509 | S-082 | secondary |
| City populations | Madinah | 1.41 M | 1,411,599 | S-083 | secondary |
| City populations | Dammam | 1.39 M | 1,386,166 | S-084 | secondary |
| City populations | Tabuk | 0.59 M | 594,350 | S-085 | secondary |
| City populations | Buraidah | 0.57 M | 571,169 | S-086 | secondary |
| City populations | Taif | 0.56 M | 563,282 | S-087 | secondary |
| City populations | Khamis Mushait | 0.54 M | 535,065 | S-088 | secondary |
| City populations | Abha | 0.33 M | 334,290 | S-089 | secondary |

**City populations.** All ten exact values match the brief's rounded values. They come from citypopulation.de crediting GASTAT, so they stay `secondary`. GASTAT's own table could not be read because portal.saudicensus.sa did not resolve (S-090), so the aggregator figures were **not** replaced by a GASTAT primary in this pass.

## W1. National data build and network

### In use
| Source | URL | Publisher/version | Licence or terms | Used for | Commit? | Status |
|---|---|---|---|---|---|---|
| OpenStreetMap GCC extract | https://download.geofabrik.de/asia/gcc-states-latest.osm.pbf | Geofabrik, replication 2026-10-14 (manifest `osm-gcc-2026-10-14`) | ODbL-1.0 | rail relations, road graph, places | No (symlink) | verified (R0) |
| GASTAT Railway Transport Statistics 2025 (EN) | stats.gov.sa (see S-043) | GASTAT, 2025 edition, file uploaded 2026-10-18 (manifest `gastat-rail-stats-2025-en`) | GASTAT use policy (S-069) | national and per-line passengers, passenger-km, freight 2024–2025 | Yes, `data/ksa/tables/` (242,797 bytes) | verified |
| Railway key indicators 2024–2025 (derived) | as above | Derived by KSA Rail Twin from GASTAT (manifest `gastat-rail-key-indicators-2024-2025`) | GASTAT use policy; marked as derived | calibration targets (W8) | Yes, `data/ksa/tables/` (1,286 bytes) | verified (transcribed) |
| SAR network page | http://www.sar.com.sa/about-sar/railnetwork/ | Saudi Arabia Railways, undated page (footer 2026) | published facts, cited | North and East line lengths and places | No (facts into line YAML with `source:`) | verified (S-017 to S-027) |
| HHR booking site | https://sar.hhr.sa/en/ | SAR (HHR) | published facts, cited | station names | No | verified (S-001); timetable and fares not printed (S-015, S-016) |

### Planned
| Source | URL | Publisher/version | Licence or terms | Used for | Commit? | Status |
|---|---|---|---|---|---|---|
| GASTAT Census 2022 tables (region, governorate, locality, Saudi/non-Saudi) | https://portal.saudicensus.sa/portal/public/1/15?type=TABLE | GASTAT | GASTAT use policy (S-069) | settlement universe, coverage | Yes, small tables with README | unverified: DNS failure on 2026-10-30 (S-090) |
| GASTAT population projection | https://www.stats.gov.sa/statistics?index=119025 | GASTAT | GASTAT use policy | W8 scenarios | — | not found (S-091); fallback is UN WPP (W8) |
| SAR/HHR timetables and fares | sar.hhr.sa, sar.com.sa | SAR | published facts | line YAML service patterns | No | unverified (booking search only) |
| RCRC Riyadh Metro system facts | https://www.rcrc.gov.sa | RCRC | published facts | metro layer | No | only the station count was verified (S-034) |

### Secondary (aggregators; replace with primaries before reporting)
| Source | URL | Publisher/version | Licence or terms | Used for | Commit? | Status |
|---|---|---|---|---|---|---|
| citypopulation.de census-2022 admin and city pages | https://www.citypopulation.de/en/saudiarabia/admin/ | T. Brinkhoff, crediting GASTAT | terms not checked (facts only, cited) | governorate list (S-073), city populations (S-080 to S-089), Al-Jumum (S-065, S-066) | No | secondary |
| GLMM census-2022 table | https://gulfmigration.grc.net/?p=9681 | Gulf Labour Markets, Migration and Population Programme, reproducing GASTAT | no explicit reuse licence (facts only) | national total, Saudi/non-Saudi split (S-077, S-078) | No | secondary |
| Wikipedia (HHR, Riyadh Metro, Landbridge, governorates) | en/ar.wikipedia.org | Wikipedia | CC BY-SA (text not copied; facts only) | cross-checks | No | secondary |
| MEED, ENR, Construction Review, Gulf Construction Online, Railway Gazette, Argaam, Saudi Auto | see index | trade and business press | press: facts only, cited | planned lines, costs, dates | No | secondary / unverified (paywall, 403) |

### Not found / to verify
- **GASTAT's governorate count and list.** Not found within the hour (S-072; C-010). Working list: `docs/gastat-regions.md` (150 rows + 2 flagged, secondary).
- **HHR inter-station distances.** The 17/94/261 km figures, the timetable and the fares were not found (S-006, S-015, S-016).
- **Intercity passenger-km 2023.** The 2,618 M figure needs a working URL for the GASTAT 2023 publication (S-042).
- **Landbridge cost and stations.** The ENR full text, SAR's Riyadh Rail Link tender/award value and the Landbridge station list with locations were not read (C-001).
- **Al-Jumum distances.** The road distances to Makkah and Jeddah will be measured in R1a (S-068).

## W1 status after R1a (31 Oct 2026)

Every dataset PROJECT.md W1 names, with its status: `used` (in an R1a output, manifest row with SHA-256 where a file is local), `planned`, `not found`, `unverified`. Details and attempts: `docs/sources/r1a-data-inventory.md` (S-r1a-500…531), `docs/sources/r1a-lines-facts.md` (S-r1a-001…077), `docs/sources/r1a-econ.md` (S-r1a-200…), `docs/network.md`.

| W1 dataset | source | used in | manifest id | status |
|---|---|---|---|---|
| OSM rail relations, ways and stations | Geofabrik GCC extract, ODbL | cities/ksa/lines/* | osm-gcc-2026-10-14; osm-ksa-rail-extract-2026-10-14 | used |
| SAR/HHR published lines and stations | sar.com.sa, sar.hhr.sa (S-001, S-017…S-026, S-r1a-001…043) | rail/specs, line YAMLs | — (facts, cited) | used (verified for SAR line lengths and place lists; HHR details secondary) |
| SAR/HHR timetables | sar.hhr.sa, sar.com.sa | — | — | unverified: search forms only (S-r1a-003, S-r1a-025); Makkah–Jeddah 43 min secondary (S-005) |
| SAR/HHR fares | SAR home widget (S-r1a-021…024, verified "from" prices); HHR travel guide (S-r1a-012/013, secondary) | hhr, sar-north-passenger, sar-east-passenger YAMLs | — | used (sampled 2026-10-31; re-sample before CP6) |
| Planned lines: Landbridge, Riyadh Rail Link, GCC railway Saudi section | MEED (S-054, S-r1a-055, S-029), Saudi Auto (S-062), MEED Projects pid=114639 (S-lb-018, paywall) | committed line YAMLs | — | used (announced/procurement/design; sites unlocated) |
| Hejaz Railway (historical) | Wikipedia (S-r1a-066…077, secondary); OSM relation 1277794 | hejaz-railway.yaml | osm-ksa-rail-extract-2026-10-14 | used (historical layer) |
| GASTAT regions and governorates (official list) | stats.gov.sa, portal.saudicensus.sa | — | — | unverified: primary unreachable (S-r1a-500); 13 regions confirmed (S-070, S-r1a-502); OSM polygons used for geometry (149, C-r1a-20) |
| OSM admin boundaries (regions, governorates) | Geofabrik GCC extract, ODbL | cities/ksa/zones/{ksa,regions,governorates}.geojson | osm-gcc-admin-extract-2026-10-14 | used |
| GASTAT Census 2022 population (region, governorate) | portal.saudicensus.sa | — | — | unverified (primary unreachable); pilot figures via citypopulation.de (secondary) carried into settlements |
| GASTAT locality tables | GASTAT | — | — | not found |
| OSM place nodes (with population tags) | Geofabrik GCC extract, ODbL | settlements.parquet | osm-gcc-places-extract-2026-10-14 | used (118 population tags, secondary) |
| WorldPop 2020 population grid | WorldPop, CC BY 4.0 | settlements.parquet (7,089 grid rows) | worldpop-sau-2020-100m-unadj-constrained (+ 1 km cross-check, 100 m unadjusted unused) | used (derived, unverified) |
| GHSL GHS-POP R2023A | JRC via AWS, CC BY 4.0 (secondary) | — | — | planned (GEO_VERIFY second estimator; 283 MB 1 km file) |
| Ports (Mawani) | Mawani site unreadable; Wikipedia list (secondary) | economic_nodes | — | used (secondary); Mawani primary unverified |
| Industrial cities (MODON; RCJY) | modon.gov.sa; rcjy.gov.sa | economic_nodes | — | used |
| Mining (Ma'aden) | maaden.com.sa list unreadable; Wikipedia/OSM | economic_nodes | — | used (partial) |
| Airports (GACA) | GACA report Feb 2025 (S-cp1-100); OSM aerodromes | economic_nodes | — | used |
| Universities | KSU page (S-cp1-102); MoE list | economic_nodes | — | used (partial; MoE list not read) |
| Heritage and tourism | UNESCO list (403); Wikidata | economic_nodes | — | used (secondary) |
| Hajj/Umrah nodes | Wikidata; GASTAT Hajj 1446H (S-r1a-516) | economic_nodes | — | used |
| Giga-projects (NEOM, Red Sea Global, AlUla, Qiddiya, Diriyah, ROSHN) | project sites (several 403), PIF/SPA/Wikipedia | economic_nodes (`announced` etc. with date) | — | used (partial; see r1a-econ.md) |
| Road skims (OSRM on the GCC PBF) | OSRM 26.10.0 | settlements distance fields; runs/skims/national-governorates | osm-gcc-2026-10-14 | used (free flow, uncalibrated) |
| r5py | — | — | — | not used (OSRM covers the national case) |
| TrafficTwin Jeddah peak times | TrafficTwin (read-only) | — | traffictwin-jeddah-v2-net | planned (R4 coupling) |

### Economy and demand inventory (from docs/sources/r1a-data-inventory.md §4; inventory only, no modelling)

| Source | URL | Publisher / version | Licence or terms | Used for | Commit? | Status |
|---|---|---|---|---|---|---|
| GASTAT Labour Force Survey, regional tables | not found; GLMM reproduction https://gulfmigration.grc.net/saudi-arabia-labour-force-participation-rates-by-nationality-saudi-non-saudi-and-sex-q1-2021-q3-2025/?print=pdf (rates, national, Q1 2021 to Q3 2025, S-r1a-523) | GASTAT (LFS revised to census 2022), reproduced by GLMM | GASTAT use policy (S-069) for the primary; GLMM terms not read | labour-market proxy for demand (regional) | No | `not found` (regional); national rates `secondary` |
| Regional GDP (GASTAT, by region) | not found (S-r1a-528) | GASTAT | n/a | regional economic weight | No | `not found` |
| VIIRS night lights, annual (VNP46A4 v2.0) | https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A4 (15 arc second, 2012 onward, DOI 10.5067/VIIRS/VNP46A4.002) | NASA LAADS DAAC (VIIRS/NPP Black Marble) | not stated on the product page; data.gov lists none (S-r1a-512, S-r1a-513); **unclear** | **proxy only** for activity or urbanisation (not population) | No | `unverified` (licence) |
| Real-estate price index, GASTAT REPI | https://www.stats.gov.sa/documents/20117/2435267/RPI+Q1+2025+EN.pdf/6385a45f-e30d-5744-0b2d-661512e15bec (Q1 2025, read; regional annual change, S-r1a-514); Q4 2025 release https://stats.gov.sa/en/w/news/157 (S-r1a-515) | GASTAT, base year 2023, Geo-AI method from Q3 2024 | GASTAT use policy (S-069): reuse with acknowledgement, modified material marked | regional price growth (a covariate, not a price level) | No | `planned`; the Q1 2025 PDF is `verified` |
| Real-estate transactions, MoJ or REGA index | not found (S-r1a-529) | MoJ / REGA | n/a | price indicator | No | `not found` |
| Air passenger city pairs (domestic OD) | not found. GACA H1 2025 release https://gaca.gov.sa/en/News/gaca-66-million-travelers-463k-flights-2025 (over 66 M passengers, no city-pair table, S-r1a-519); full-year 2025 140.9 M via Argaam (S-r1a-520); IATA busiest pairs (Jeddah-Riyadh top 10, S-r1a-530) | GACA; Matarat (not found); IATA (airline-reported, not open) | GACA terms not read; IATA not open | air demand proxy; no OD pairs yet | No | `not found` (OD); totals `verified` (GACA H1) |
| Intercity bus | Q2 2025 trips https://www.argaam.com/en/article/articledetail/id/1831189 (S-r1a-521); Q4 2025 (884,000 intercity passengers) and Q2 2026 (892,000) seen in press without a captured URL | TGA (Transport General Authority), via press | TGA terms not read | intercity bus demand, a competitor to rail | No | `unverified` (no TGA primary read) |
| SAPTCO annual report, routes | not found (S-r1a-522) | SAPTCO | n/a | bus routes | No | `not found` |
| GASTAT railway statistics | https://www.stats.gov.sa/documents/20117/2435281/Railway+Transport+Statistics+Publication+2025+EN.pdf (S-040, S-043 to S-045) | GASTAT, 2025 edition | GASTAT use policy (S-069) | national and per-line rail demand | Yes, `data/ksa/tables/` (already in the manifest) | `used` (verified) |
| Hajj and Umrah statistics | Hajj 1446H headline https://stats.gov.sa/en/w/news/49 (1,673,230; S-r1a-516); executive summary https://www.stats.gov.sa/documents/d/guest/hajj-report-1446h-en-1- (S-r1a-517, search extract); 1447H 1,707,301 (press, S-r1a-518) | GASTAT (Ministry of Interior administrative records); Ministry of Hajj and Umrah figures not found | GASTAT use policy (S-069) | pilgrim-season travel demand, a seasonal peak for rail | No | `verified` (1446H headline); `secondary` (summary, 1447H) |
| GASTAT population estimates by region, 2023 to 2025 | not found (S-r1a-525); mid-2024 national 35,300,280 via press | GASTAT (Population Estimates Statistics 2024) | GASTAT use policy (S-069) | regional population base for 2024 to 2025 | No | `not found` (regional); national `secondary` |
| UN World Population Prospects 2024 (national) | population.un.org download page returned HTTP 404 on 31 Oct 2026; 2025 value 34,566,328 via populationpyramid.net (S-r1a-526) | UN DESA Population Division, WPP 2024 | CC BY 3.0 IGO (UN Summary of Results, S-r1a-527; secondary) | national control total for projections (W8) | No | `unverified` (download page); national value `secondary` |
| Open road traffic counts (MoT, Roads General Authority) | none found (S-r1a-531) | MoT / RGA | n/a | road traffic baseline | No | `not found` |
| Census 2022 region table (GLMM reproduction) | https://gulfmigration.grc.net/?p=9681 (S-r1a-502) | GASTAT census 2022, reproduced by GLMM | GASTAT use policy (S-069) for the primary | 13 regional totals for coverage (W2) | No (table reproduced in the register only) | `secondary` |
| Census 2022 primary tables (region, governorate, locality) | https://portal.saudicensus.sa/portal/public/1/15?type=TABLE (S-r1a-500) | GASTAT | GASTAT use policy (S-069) | governorate and locality populations (W2, W8) | No | `unverified` (portal unreachable) |

## W2, W3, W5–W10
No sources were added in this pass, except the cost data points listed above (Landbridge, HHR, SAR North, Riyadh Metro). Those are inputs to the W3 cost register as `secondary`/`unverified` data points with their scope; none is a register value yet.
