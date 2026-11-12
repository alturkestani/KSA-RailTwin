> **Document version:** docs/sources/r1a-econ.md v0.2 | 31 Oct 2026 | Author: rail-data-scout (R1a) | Status: draft

# R1a economic nodes: sources, counts, gaps and conflicts

Outputs of this run (W1 "economic roles"):
- `cities/ksa/zones/economic_nodes.csv`: 100 node rows (one row per node).
- `docs/sources/r1a-econ.csv`: 21 new source records, S-r1a-200 to S-r1a-220, in the column layout of `docs/sources/index.csv`, accessed 2026-10-31.
- This file.

Not done in this run (written only as outputs above, per the task): the 21 rows are NOT yet appended to `docs/sources/index.csv`; the scratch extracts (OSM tag extract, saved pages) live in `/tmp/r1a-econ` and are not in `cities/ksa/sources.yaml`; no licence-register rows were written; the CSV has not been converted to `economic_nodes.parquet` (the `used_in` field names the parquet path as specified).

## 1. Counts per role

| role | rows | located: OSM | located: Wikidata | city_centroid | unlocated |
|---|---:|---:|---:|---:|---:|
| airport | 27 | 27 | 0 | 0 | 0 |
| port | 10 | 1 | 4 | 0 | 5 |
| industrial_city | 40 | 15 | 0 | 11 | 14 |
| mining | 2 | 2 | 0 | 0 | 0 |
| energy | 5 | 3 | 1 | 0 | 1 |
| heritage | 8 | 0 | 8 | 0 | 0 |
| hajj_umrah | 4 | 0 | 4 | 0 | 0 |
| giga_project | 3 | 2 | 1 | 0 | 0 |
| university | 1 | 0 | 0 | 1 | 0 |
| **total** | **100** | 50 | 18 | 12 | 20 |

Located = 80 rows (50 OSM, 18 Wikidata, 12 city_centroid). Unlocated = 20 rows, coordinates left empty, `location_method = unlocated`.

Industrial cities split: 36 MODON table rows, which are 30 industrial cities and 6 "MODON Oasis" entries, plus 4 RCJY cities. A search summary of the MODON About page gave 36 and another gave 35; the About page was not read. See conflict 6.

Status values: operating 88, inscribed 8, partly_open 2, under_construction 1, announced 1.

Source status of the 21 new records: verified 8, secondary 7, unverified 6. Reused verified or secondary ids from the cp1 set (already in `index.csv`): S-cp1-100 (GACA Feb 2025 report, airport names), S-cp1-102 (KSU), S-cp1-103 (SATORP), S-cp1-104 (Petro Rabigh, secondary), S-cp1-105 (YASREF, secondary), S-cp1-106 (Jubail Commercial, secondary), S-cp1-107 (Abqaiq, secondary), S-cp1-108 (Ras Tanura, secondary), S-cp1-111 (Jeddah Islamic, secondary).

Location methods: `osm:way/<id>`, `osm:node/<id>`, `osm:area/<id>` (osmium area ids, which are 2 x relation id for multipolygon relations and 2 x way id + 1 for closed ways; they are recorded as found, not converted), `wikidata:Q<id>` (CC0), `city_centroid` (OSM place node of the host city, not the site), `unlocated`.

## 2. Coverage by category

- **Airports (GACA):** the GACA February 2025 operational report (S-cp1-100, read on 2026-10-31) names 27 airports. Each has a row. Positions and IATA codes come from OSM aerodrome features (`osm:`), since the GACA website has no airport list (S-r1a-218) and Matarat was unreachable. The report's unlabelled "International Airport" line is Prince Mohammed bin Abdulaziz (Madinah), confirmed by the adjacent line. Wadi al-Dawasir airport is IATA WAE in OSM.
- **Ports (Mawani):** the Mawani site could not be read (client-side app; static pages return 404; S-r1a-209). Ten names come from the Wikipedia list (S-r1a-208, secondary). Five have no position source and are unlocated.
- **MODON industrial cities:** all 36 rows from the MODON Cost-of-Industry table (S-r1a-204, verified, undated). 14 are unlocated, 11 are host-city centroids, 15 are OSM polygons matched by name.
- **RCJY industrial cities:** all four (Jazan, Ras Al-Khair, Yanbu, Jubail) from the RCJY city pages (S-r1a-200 to S-r1a-203, verified). Jazan and Yanbu have OSM polygons; Jubail and Ras Al-Khair are unlocated.
- **Ma'aden (mining):** only two rows. The Al-Jalamid mine (Wikipedia, S-r1a-211) and the Ras Al-Khair alumina and phosphate complex (RCJY page S-r1a-201 plus OSM). The maaden.com operations page returned 404; the home page has no site list. Other Ma'aden sites are not written (section 3).
- **Energy:** Ras Tanura, Abqaiq, YASREF and Petro Rabigh (secondary, S-cp1-104 to S-cp1-108) plus SATORP (verified, S-cp1-103, unlocated).
- **Heritage (UNESCO inscribed):** eight rows, from the Wikidata SPARQL on the UNESCO World Heritage property tag (S-r1a-205, secondary). The UNESCO list page is blocked (S-r1a-206, HTTP 403). Inscription years are not in the data fetched and are left unknown.
- **Hajj and Umrah:** Masjid al-Haram, Al-Masjid an-Nabawi, Muzdalifah and the Plain of Arafat (Wikidata, S-r1a-214). Makkah city itself is covered by the cp1 table (S-cp1-109).
- **Giga-projects:** NEOM (NEOM home page, S-r1a-212, undated; Port of NEOM open; partly_open), Oxagon (AI data centre phase 1 under construction, S-r1a-212), New Murabba (Wikidata, "planned downtown", secondary, date unknown).
- **Universities:** King Saud University main campus only (S-cp1-102, verified). Coordinates are the Riyadh city node, not the campus.
- **Border crossings:** none found (S-r1a-219). Searches for al-Haditha, King Fahd Causeway, al-Batha, al-Wadiah and al-Raqi returned no items; the OSM extract has no matching border_control feature in KSA.
- **Tourism (MoT/STA):** no MoT or STA list was readable (visitsaudi.com heritage page 404). No tourism row written beyond the UNESCO heritage rows.
- **Agriculture and military:** not searched in this run; none written.

## 3. Not found, not written, or left for escalation

Rule: an unsourced node is not written. A category with no sourced node is noted here as "none found".

- **Mawani ports not written:** Dhiba (appears only in search summaries and a menu snapshot, not read) and Ras Tanura port (not in the Wikipedia list). The official Mawani list was not reached.
- **Ma'aden sites not written (search summaries only, S-r1a-217, unverified):** Az-Zabirah (kaolin and low-grade bauxite), Al-Baithah (bauxite), Mahd adh-Dhahab (gold, production from 1988 per Saudipedia summary), Ad Duwayhi (gold, Makkah region per gulfbusiness summary), Bulghah, Sukhaybarat, Mansourah-Massarah, Al-Amar. Mahd adh-Dhahab and Az-Zabirah have OSM place nodes (town at 23.50N 40.88E; village at 28.00N 43.69E) that are not used as mine positions. Umm Wu'al: see conflicts. Wa'ad Al-Shamal phosphate is the MODON "Waad Al-Shamal City for Mining Industries" row (name match to an OSM mine polygon).
- **Energy not written:** Jafurah (no source read), Jazan refinery (Wikidata label only; OSM feature w899264339 exists but no description or status source), SAMREF and Luberef in Yanbu (S-cp1-105 says not separately sourced; OSM features exist: w585223969 and w585207620).
- **Giga-projects not written (no primary status readable):** Red Sea Global (redseaglobal.com 403, S-r1a-215), Qiddiya (Wikidata "entertainment megaproject", no status; qiddiya.com 403), Diriyah Gate (no coordinates, no status), King Salman Park (Wikidata "urban park", no status), Sports Boulevard (no coordinates, no status), AlUla as a giga-project (no RCU status page read; the AlUla town and airport are in the table only as Hegra heritage and the airport row), THE LINE and Trojena (named on the NEOM page without status), ROSHN (a developer, not a site).
- **Hajj and Umrah not written:** Mina (no Wikidata item found), Arafat as a separate node (covered by the Plain of Arafat row), Miqat sites (not searched).
- **Universities not written:** the Ministry of Education list of public universities was not found (S-r1a-216). Only KSU is written.
- **Border crossings:** none found (S-r1a-219).

## 4. Conflicts (logged, not averaged)

1. **Al-Jalamid position.** Wikipedia (S-r1a-211) gives 31.28028 N, 40.10417 E. That point is exactly the OSM village node "حزم الجلاميد" (Hazm al-Jalamid). The Ma'aden mine polygon in OSM ("الجلاميد", way 597933729) is at 31.50662 N, 39.92987 E, about 30 km away. The row uses the mine polygon (`osm:way/597933729`). Escalate to geo-verify.
2. **Yanbu Commercial Port.** Wikidata (Q12246917) 24.06667 N, 38.05000 E; OSM way 143055851 at 24.08144 N, 38.07043 E, about 3 km apart. OSM used.
3. **Red Sea International Airport.** S-cp1-118 (Wikipedia) places it at Hanak, Tabuk Province. OSM (w1175996661) is at 25.6296 N, 37.08934 E. Both are in Tabuk; the Hanak statement is not reconciled. OSM position used.
4. **Ras Tanura refinery.** S-cp1-108 gives a location text ("near Jubail") that conflicts with the position. OSM way 676562519 (26.69178 N, 50.10069 E) and Wikidata (26.69190 N, 50.10790 E) agree; those are used. The page's location text is not used.
5. **Abqaiq.** S-cp1-107 gives a distance to Dhahran that conflicts with the other source (48 km vs about 60 km). The row uses the Wikidata oilfield item (25.93333 N, 49.66667 E), which is a field point, not the plant footprint. Escalate.
6. **MODON count.** The MODON Cost-of-Industry table has 36 rows: 30 industrial cities and 6 "MODON Oasis" entries. A search summary of the MODON About page says 36 and another says 35; the About page itself was not read. The table, not the summary, is used. Escalate if the MODON About page disagrees.
7. **Mawani port count.** Wikipedia (S-r1a-208) lists 10 entries (including NEOM and King Abdullah). Search summaries give nine (Saudipedia, Forbes: six commercial and three industrial) and ten (Logistics Manager). No count is written. Escalate: needs the Mawani list.
8. **RCJY port in Jazan.** The RCJY Jazan page (S-r1a-200) says the city "features the first port directly operated by the Royal Commission". That port is not in the Wikipedia Mawani list. Not written as a separate port row. Escalate: possibly the same as Jazan Port, or a missing node.
9. **Umm Wu'al.** One search summary (LLMpedia) calls it a phosphate mine; another (a LinkedIn project reference) calls it a greenfield phosphate project near Turaif with downstream plants at Ras Al-Khair. Not written. Escalate to Ma'aden's official list.
10. **Makkah and industrial city name mapping.** OSM "Makkah Al-Mukarrama Industrial City" (way 1372643537) is mapped to MODON's "First Industrial City in Makkah" by name only. Inferred, not confirmed.
11. **Name-matched industrial polygons.** Fifteen industrial-city rows (13 MODON, 2 RCJY) take their position from an OSM polygon matched by name. Four of those mappings are inferred rather than exact: MODON Qassim 1st (way 59445653), MODON Makkah 1st (way 1372643537), MODON Waad Al-Shamal (the Ma'aden Wa'ad Al-Shamal mine polygon, way 882569203) and RCJY Yanbu Industrial City (way 234567455, "صناعيه ينبع البحر"). All fifteen need the geo-verify imagery check.
12. **Jazan.** The MODON "Jazan Industrial City" and the RCJY "Jazan City for Primary and Downstream Industries" are different entities. Both are kept.
13. **Regions assigned without a source.** Uruq Bani Ma'arid (riyadh) and Al-Faw (riyadh): the region is assigned from the area name and coordinates only. Hail rock art coordinates are region-level (Wikidata 28.0 N, 40.9 E). Escalate.

## 5. Escalations (for the coordinator)

- **Second-line geo-verify not run.** The 20 unlocated rows, the 12 city_centroid rows, the 15 name-matched industrial polygons, Port of NEOM (candidate: OSM Oxagon Harbour, not used), and the Al-Jalamid conflict need the `geo-verify` skill (imagery, back-test, method log). Not done within this run's time budget. Positions in this table are OSM name matches, host-city centroids or Wikidata points.
- **Primary sources blocked:** Mawani port pages (client-side app, 404), MODON city detail pages (JavaScript), UNESCO list page (403), Red Sea Global (403), Qiddiya (403), Diriyah (403), ROSHN project pages (not reached). Retry in a browser-capable session or ask for a manual copy.
- **Licence and manifest:** the OSM extract (ODbL, attribution required), Wikidata (CC0), Wikipedia (CC BY-SA) and the RCJY, MODON, GACA and NEOM pages (terms not checked) need licence-register rows. The OSM extract's edition and origin URL are not recorded in the manifest; the scratch files in `/tmp/r1a-econ` are not in `cities/ksa/sources.yaml`.
- **Quotes:** S-r1a-200 to S-r1a-203 and S-r1a-204 quotes are verbatim from the curl text extraction. S-r1a-208, S-r1a-211 and S-r1a-212 quotes come from WebFetch output and must be re-checked against the page text before any publication (rule 1 and the source-citation skill).
- **Index merge:** append the 21 rows of `docs/sources/r1a-econ.csv` to `docs/sources/index.csv` and to `docs/sources/index.md`; run `uv run python -m common.sources check` on this folder.
- **Region for Uruq Bani Ma'arid and Al-Faw**, and for the GACA airport subtype labels (international or domestic, taken from the GACA names and the cp1 band notes): confirm.
- **Universities:** the MoE public university list (campus cities for all public universities) is still needed; only KSU is written.
- **Border crossings and Ma'aden site list:** still needed from ZATCA or the Ministry of Interior and from Ma'aden's annual report.

## 6. Sources (new, S-r1a-200 to S-r1a-220)

Full records are in `docs/sources/r1a-econ.csv`. Summary:

| id | what | status |
|---|---|---|
| S-r1a-200 | RCJY Jazan City page | verified |
| S-r1a-201 | RCJY Ras Al-Khair page | verified |
| S-r1a-202 | RCJY Yanbu page | verified |
| S-r1a-203 | RCJY Jubail page | verified |
| S-r1a-204 | MODON Cost-of-Industry table (36 rows) | verified |
| S-r1a-205 | Wikidata SPARQL, World Heritage in KSA | secondary |
| S-r1a-206 | UNESCO KSA page (403) | unverified |
| S-r1a-207 | Wikidata port items and coordinates | secondary |
| S-r1a-208 | Wikipedia, Saudi Ports Authority list | secondary |
| S-r1a-209 | Mawani home page (loading shell) | unverified |
| S-r1a-210 | OpenStreetMap GCC extract (element ids) | verified |
| S-r1a-211 | Wikipedia, Jalamid | secondary |
| S-r1a-212 | NEOM home page (undated) | verified |
| S-r1a-213 | Wikidata, Abqaiq oilfield | secondary |
| S-r1a-214 | Wikidata, Hajj sites and New Murabba | secondary |
| S-r1a-215 | Red Sea Global home page (403) | unverified |
| S-r1a-216 | MoE home page (no university list) | verified |
| S-r1a-217 | Ma'aden search summaries (not read) | unverified |
| S-r1a-218 | GACA airports page (no list) | verified |
| S-r1a-219 | Border crossing search (no items) | unverified |
| S-r1a-220 | Wikidata giga-project items (no status) | secondary |

Reused from cp1 (not duplicated): S-cp1-100, S-cp1-102, S-cp1-103, S-cp1-104, S-cp1-105, S-cp1-106, S-cp1-107, S-cp1-108, S-cp1-111.

Sources: MODON Cost of Industry (https://www.modon.gov.sa/en/Cost-of-Industry); RCJY city pages (https://www.rcjy.gov.sa/en/jazan, /ras-al-khair, /yanbu, /jubail); GACA OPS report Feb 2025 (https://gaca.gov.sa/-/media/Files/PDF/Reports/202502_OPS_Public-Report_E.pdf); NEOM (https://www.neom.com/en-us); Wikipedia (https://en.wikipedia.org/wiki/Saudi_Ports_Authority, https://en.wikipedia.org/wiki/Jalamid); Wikidata (https://query.wikidata.org/, https://www.wikidata.org/w/api.php); OpenStreetMap (https://www.openstreetmap.org/, ODbL).

## Gap fill (pass 2)

Pass 2 appends rows only. `cities/ksa/zones/economic_nodes.csv` now has 168 rows (100 from pass 1, 68 added). `docs/sources/r1a-econ.csv` now has 45 records (S-r1a-200 to S-r1a-244); the 24 new records are S-r1a-221 to S-r1a-244. No existing row was rewritten. Accessed 2026-10-31 on every new record. Scratch files are in `/tmp/r1a-econ2` (OSM extracts from `data/osm/gcc-states-latest.osm.pbf`, read-only, plus saved pages). No sign-ups, no contact.

### 1. Rows added per role

| role | added | located by OSM element (S-r1a-210, verified) | located by Wikipedia coordinates (secondary) | unlocated |
|---|---:|---:|---:|---:|
| giga_project | 8 | 0 | 7 | 1 |
| hajj_umrah | 6 | 0 | 1 | 5 |
| mining | 8 | 3 | 2 | 3 |
| border_crossing | 12 | 9 | 1 | 2 |
| tourism | 4 | 1 | 3 | 0 |
| port | 2 | 1 | 1 | 0 |
| university | 28 | 26 | 1 | 1 |
| **total** | **68** | **40** | **16** | **12** |

The 12 unlocated rows are Sports Boulevard, the five Miqat sites, Sukhaybarat, Ad Duwayhi, Mansourah-Massarah, Salwa, Al-Wadiah and Saudi Electronic University. Port rows: Ras Tanura uses the OSM town node (OSM column); Dhiba uses the Wikipedia Duba point (Wikipedia column).

Node `status` values added: operating 45, unverified 15, partly_open 6, under_construction 2. In this column `unverified` means the operating state is not sourced; it is not a source status.

Source status of the 24 new records: verified 2 (S-r1a-228 Royal Commission for AlUla home page; S-r1a-232 ROSHN home page), secondary 22 (Wikipedia pages, Saudipedia, and the Wikipedia list). The OSM element source S-r1a-210 (verified, pass 1) is reused for every OSM-located row. Unverified sources reused from pass 1: S-r1a-209 (Mawani) and S-r1a-217 (Ma'aden search summaries).

### 2. Per role: what was sourced and how

- **giga_project (8 rows).** Red Sea Global (Wikipedia coordinates, S-r1a-226; partly open, Sep 2025); AlUla (Wikipedia town point, S-r1a-227; RCU page S-r1a-228); Qiddiya City (S-r1a-229; partly open, 31 Dec 2025); Diriyah Gate (Wikipedia Diriyah point, S-r1a-230; partly open, 2019 per Diriyah Arena); SEDRA as ROSHN's first community (S-r1a-231, opened 2022 per infobox; ROSHN home page S-r1a-232); Trojena (S-r1a-233; under construction; 2029 Asian Winter Games moved, 2026); King Salman Park (S-r1a-234; under construction; tunnel opened 29 Feb 2024); Sports Boulevard (S-r1a-235; partly open, phase 1 27 Feb 2025; no coordinates, unlocated). The official sites for Red Sea Global, Qiddiya and Diriyah returned 403; PIF returned 403. Status for these is secondary. Diriyah Gate status is taken from the Diriyah town article, not from the DGDA: escalate.
- **hajj_umrah (6).** Mina (S-r1a-224, Wikipedia coordinates; status Active, undated). Five miqat sites (S-r1a-225): Dhul-Hulayfah, Al-Juhfah, Qarn al-Manazil, Yalamlam and Dhat Irq. The Wikipedia miqat list gives location text and distance from Mecca only, with no coordinates, so all five are unlocated. The OSM village "Al Juhfah" (27.07 N, 42.24 E) is a different place and is not used. "Abyar Ali" (the brief's alias for Dhul-Hulayfah) is not in any source read.
- **mining (8).** Ba'itha bauxite (Wikipedia Ma'aden article, S-r1a-236: operations from May 2014; coordinates as printed there); Az Zabirah bauxite (OSM mine polygon 2889887038 matched by name, S-r1a-236 and S-r1a-210; the Wikipedia article names the mine on the freight line); Mahd adh-Dhahab (Wikipedia point, S-r1a-237; status unverified); Bulghah, Al-Amar (OSM hamlet points matched by name only, S-r1a-217 for the site names; unverified); Sukhaybarat, Ad Duwayhi and Mansourah-Massarah (named in S-r1a-217 only; unlocated). Umm Wu'al is not written (see conflicts).
- **border_crossing (12).** OSM named border posts (S-r1a-210): Al-Batha and Al-Ghuwaifat (Saudi-UAE; side not confirmed), Al-Haditha (Jordan; the Jordan side is from the Arabic name only), Al-Mudawara (Jordan; not in the brief, added because OSM names it), Al-Durra (type and country pair unknown), Al-Ruqi (Kuwait), Al-Salmi (Kuwait; not in the brief), Al-Khafji (Kuwait), Arar (Iraq; the brief's Jadidat Arar is not an OSM name). King Fahd Causeway (Wikipedia coordinates, S-r1a-238). Unlocated: Salwa (OSM passport and customs areas near 24.72 N, 50.76 E are generic and not used) and Al-Wadiah (no OSM match, no source). ZATCA's border crossing page was not read: no official list.
- **tourism (4).** Abha, Taif and Jeddah Corniche (Wikipedia coordinates, S-r1a-239 to S-r1a-241); Farasan Islands (OSM archipelago node 322595136, S-r1a-210; Wikipedia cross-check S-r1a-244). Edge of the World (Saudi site) was not found: no Wikipedia page for the site resolved, so it is not written. The MoT and visitsaudi.com pages were reached but gave no destination list with coordinates, so no MoT-sourced row is written.
- **port (2).** Dhiba (Duba town point, S-r1a-242; port name from S-r1a-209 and the search summaries only; Dhiba = Duba is an inference; status unverified). Ras Tanura (OSM town node 1237805652, S-r1a-210; Wikipedia cross-check S-r1a-243). The Ras Tanura row is a town-level point, not the terminal.
- **university (28).** The public list is DERIVED: the Wikipedia list (S-r1a-221, province table with city) minus the 15 private institutions named by Saudipedia (S-r1a-222). That gives 27 universities plus 2 university colleges (Yanbu, Jubail) = 29, which matches the Saudipedia count of twenty-nine governmental universities (a search summary, not read). King Saud University already exists in pass 1 (univ-king-saud, city centroid) and is not duplicated. Campus positions are OSM polygons or nodes matched by name (S-r1a-210); King Fahd University of Petroleum and Minerals uses the Wikipedia infobox point (S-r1a-223), since no OSM match was found. Saudi Electronic University has no usable OSM campus point and is unlocated. The Ministry of Education list is NOT read; the derived list is not confirmed against it.

### 3. Conflicts (logged, not averaged)

1. **Al-Juhfah miqat vs village.** Miqat text says Rabigh (S-r1a-225). OSM "الجحفة" village at 27.07 N, 42.24 E is another place. Not used. Escalate to geo-verify.
2. **King Saud University position.** Pass 1 uses the Riyadh city centroid (24.63892 N, 46.71601 E). The OSM campus features are at 24.4746 N, 46.2587 E (polygon "King Saud University", 667505930, about 50 km south-east of Riyadh) and at 24.7171 N, 46.6194 E (college node 1236703863, "Jami'at al Malik Sa'ud"). The second is nearer the main campus. Pass 1 row NOT changed. Escalate: replace with a geo-verified point.
3. **Mahd adh-Dhahab.** Wikipedia article point 23.5036 N, 40.8597 E (secondary) vs OSM town 23.49959 N, 40.87916 E: about 3 km apart. The Wikipedia point is used; it is a town point, not a mine footprint. Escalate.
4. **Ras Tanura.** OSM town node 26.70742 N, 50.06735 E vs Wikipedia 26.70639 N, 50.05278 E: about 1.4 km apart. OSM used.
5. **Dhiba port.** Name equivalence to Duba (ضباء) is an inference; the Mawani list was not readable. Escalate.
6. **Arar post.** The brief names Jadidat Arar; OSM has "عرعر" and two "border control" areas (31.39 N, 41.46 E and 31.39 N, 41.45 E). The node at 31.33 N, 41.44 E is used. Escalate which post is meant.
7. **Al-Durra.** Only an OSM node; crossing type and country pair are not in any source. Listed, flagged. Escalate before any use as a crossing.
8. **Trojena status.** Wikipedia says the 2029 Asian Winter Games moved and some contracts were cancelled (2026), yet the article infobox still reads under construction. Recorded as under_construction (secondary). Escalate.
9. **Umm Wu'al.** Still conflicting between a phosphate mine and a greenfield project (pass 1, conflict 9). Not written.
10. **Public university list.** Derived, not read from the Ministry. The 2 college rows (Yanbu, Jubail) are a judgement to reach the count of 29. Escalate.

### 4. Still missing (escalation list)

- **Ministry of Education list of public universities** with campus cities: not read (moe.gov.sa has no list in the page reached in pass 1). Needed to confirm the 29 and the campus cities.
- **ZATCA border crossing list** (official): not read. Salwa and Al-Wadiah are unlocated; the names and positions of the other crossings are from OSM only.
- **Ma'aden site list** (official, annual report): not read. Sukhaybarat, Ad Duwayhi and Mansourah-Massarah unlocated; Bulghah, Al-Amar and Mahd adh-Dhahab need a primary source.
- **Giga-project primary statuses:** Red Sea Global, Qiddiya and Diriyah sites returned 403; PIF returned 403. Status is from Wikipedia (secondary). Primary needed: Red Sea Global, Qiddiya City and DGDA press pages; NEOM for Trojena.
- **Geo-verify.** The 12 unlocated rows and the OSM name-matched rows (Az Zabirah, Bulghah, Al-Amar, Al-Batha, Al-Ghuwaifat, Al-Durra, Ras Tanura, Dhiba) need the second-line `geo-verify` pass. Not run in this pass.
- **Licence register.** New dataset uses: Wikipedia (CC BY-SA 4.0), Saudipedia (terms not checked), OSM (ODbL, attribution required), the RCU and ROSHN home pages (terms not checked). Rows to be written by the `licence-register` skill; not written here.

### 5. Sources added in pass 2 (S-r1a-221 to S-r1a-244)

| id | what | status |
|---|---|---|
| S-r1a-221 | Wikipedia, list of universities and colleges (province, city) | secondary |
| S-r1a-222 | Saudipedia, 15 private universities (basis for the public derivation) | secondary |
| S-r1a-223 | Wikipedia, KFUPM infobox coordinates | secondary |
| S-r1a-224 | Wikipedia, Mina infobox (coordinates, status Active) | secondary |
| S-r1a-225 | Wikipedia, Miqat list (location text, distances) | secondary |
| S-r1a-226 | Wikipedia, The Red Sea Destination | secondary |
| S-r1a-227 | Wikipedia, AlUla | secondary |
| S-r1a-228 | Royal Commission for AlUla home page | verified |
| S-r1a-229 | Wikipedia, Qiddiya | secondary |
| S-r1a-230 | Wikipedia, Diriyah | secondary |
| S-r1a-231 | Wikipedia, Sedra (Riyadh) | secondary |
| S-r1a-232 | ROSHN home page (SEDRA listed under communities) | verified |
| S-r1a-233 | Wikipedia, Trojena | secondary |
| S-r1a-234 | Wikipedia, King Salman Park | secondary |
| S-r1a-235 | Wikipedia, Sports Boulevard | secondary |
| S-r1a-236 | Wikipedia, Saudi Arabian Mining Company (Ma'aden) | secondary |
| S-r1a-237 | Wikipedia, Mahd adh-Dhahab | secondary |
| S-r1a-238 | Wikipedia, King Fahd Causeway | secondary |
| S-r1a-239 | Wikipedia, Jeddah Corniche | secondary |
| S-r1a-240 | Wikipedia, Abha | secondary |
| S-r1a-241 | Wikipedia, Taif | secondary |
| S-r1a-242 | Wikipedia, Duba, Saudi Arabia | secondary |
| S-r1a-243 | Wikipedia, Ras Tanura | secondary |
| S-r1a-244 | Wikipedia, Farasan Islands | secondary |

Reused: S-r1a-210 (OSM, verified), S-r1a-209 (Mawani, unverified), S-r1a-215 (Red Sea Global home page, 403, unverified), S-r1a-217 (Ma'aden search summaries, unverified).
