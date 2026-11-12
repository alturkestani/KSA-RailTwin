> **Document version:** docs/sources/cp1-item6-citypopulation.md v1.0 | 31 Oct 2026 | Author: rail-data-scout (CP1_PREP) | Status: draft

# CP1 item 6: citypopulation.de terms of use, licence and archived copies

Access date for every row: 2026-10-31. Citation records: `docs/sources/cp1-item6.csv` (ids S-cp1-050 to S-cp1-059). Quotes in this note were checked against the fetched HTML (raw `curl` output, whitespace normalised, HTML entities decoded); a WebFetch summary was used only as a cross-check, never as a quote source. The FAQ quote joins two lines of the page. Nothing was contacted or signed up for; the only requests were plain GET requests to public pages.

## 1. Verdict

1. **Population figures: reuse allowed, commercial use allowed, attribution required.** The site's Terms of Use say the presented population data may be reused "for non-commercial as well as for commercial use" with City Population referenced (S-cp1-050, S-cp1-051).
2. **Licence version is in conflict.** The Terms (EN and DE) state CC BY 3.0. The HTML of the Saudi Arabia pages declares CC BY 4.0 (S-cp1-055, S-cp1-057). Both versions allow commercial reuse and require attribution, so the commercial answer does not change; the attribution text does. Unresolved; Tariq decides (see section 7).
3. **Maps, geodata, coordinates, site design, programs and images are not licensed.** The Terms reserve them to City Population (S-cp1-050, S-cp1-051). Do not reuse them; coordinates are not supplied at all.
4. **Redistribution:** the numbers may be redistributed with attribution. Copies of whole pages are not licensed: a saved page is mostly appearance and map code, which the Terms reserve (analysis, section 4.4).
5. **Archived HTML copies** may be kept privately, because the Terms are silent on private storage, but may not be redistributed. Proposed: keep them gitignored under `data/ksa/` only until the GASTAT primary table replaces them, then drop them (section 6). Pending Tariq (CP1).
6. **The original-source rule applies on top.** GASTAT is the underlying publisher. Its use policy permits commercial reuse if GASTAT is acknowledged and modifications are marked (S-cp1-058).

## 2. Pages read

| Id | URL | What it says on use | Read |
|---|---|---|---|
| S-cp1-050 | https://www.citypopulation.de/en/help/termsofuse/ | Full Terms: population data licence, maps, other data, privacy, disclaimer | Raw HTML, 21,923 bytes |
| S-cp1-051 | https://www.citypopulation.de/de/help/termsofuse/ | German version of the same Terms | Raw HTML, 25,936 bytes |
| S-cp1-052 | https://www.citypopulation.de/en/help/ | Refers users to the terms for reuse and referencing; data mostly census-based | Raw HTML, 10,577 bytes |
| S-cp1-053 | https://www.citypopulation.de/en/help/faq/ | Map cannot be exported to GIS | Raw HTML, 3,640 bytes |
| S-cp1-054 | https://www.citypopulation.de/ | Navigation: only the terms link is a legal link; no Impressum, imprint or About link | Raw HTML, 8,316 bytes |
| S-cp1-059 | https://www.citypopulation.de/de/ | German navigation: terms link | Raw HTML, 8,351 bytes |
| S-cp1-055 | https://www.citypopulation.de/en/saudiarabia/admin/ | Saudi regions and governorates; CC BY 4.0 link; source line GASTAT | Raw HTML, 104,479 bytes |
| S-cp1-056 | https://www.citypopulation.de/en/saudiarabia/cities/ | Saudi cities; source line; no licence link | Raw HTML, 88,977 bytes |
| S-cp1-057 | https://www.citypopulation.de/en/saudiarabia/qasim/ | Al-Qaseem region; CC BY 4.0 link | Raw HTML, 37,383 bytes |
| S-cp1-058 | https://stats.gov.sa/en/use-policy | GASTAT reuse conditions (original source) | Raw HTML, 202,040 bytes |

Not read: the Creative Commons deed pages (cited by the site as `creativecommons.org/licenses/by/3.0/` and `/by/4.0/`); the Impressum (none found); the privacy and cookie sections were read for licence content only and are out of scope for this note.

Errors: none. `https://www.citypopulation.de/en/` returns a meta-refresh to `https://www.citypopulation.de/` (306 bytes), so the root page was read instead.

## 3. What the pages say (quoted)

**Population data (S-cp1-050, EN Terms, Data > Population Data).** Operative sentence: "for non-commercial as well as for commercial use under the condition that »City Population« is referenced as source". Attribution string: "Thomas Brinkhoff: City Population, http://www.citypopulation.de (or the URL of the specific page)". Web use: "Instead of labelling the URL, a hyperlink should be used by web media." Licence: "the CC BY 3.0 license holds". Third-party rights: "potential copyrights of the original sources (given in the tables' footnotes) must be observed".

**Same grant, German text (S-cp1-051).** "Sie dürfen die Bevölkerungsdaten vervielfältigen, verbreiten und öffentlich zugänglich machen" (copy, distribute, make publicly available), "sowohl für nicht-kommerzielle als auch für kommerzielle Zwecke" (non-commercial and commercial), "falls »City Population« wie folgt referenziert wird" (if referenced as follows). Licence: "Somit gilt die CC BY 3.0 Lizenz."

**Map data (S-cp1-050).** "The maps and other geospatial data are under the copyright of »City Population« and/or under the copyright of the organizations denoted at the maps." For CC BY-SA geodata: "please contact me or use the original download facilities." Coordinates: "Coordinate data of places cannot be delivered in general."

**Other data (S-cp1-050).** "All other data and resources, which are specific for »City Population«, like images, programs and appearance are under the copyright of »City Population«."

**Data basis (S-cp1-052).** "For using and referencing data from »City Population«, please, observe the terms of use." The help page also says some figures are the site's own: "In some cases, e.g. if no current figures are available, calculations of »City Population« are presented." (The page also states that most figures are "mostly based on census results and on official estimates".)

**Map export (S-cp1-053).** "How can I export the map to a GIS file? That is not possible."

**Site navigation (S-cp1-054, S-cp1-059).** Only one legal link: `href="/en/help/termsofuse/"` (EN) and `href="/de/help/termsofuse/"` (DE). No Impressum, imprint, About or licence page was found in either root page.

**Licence metadata on the Saudi pages (S-cp1-055, S-cp1-057).** `<link rel="licence" itemprop="license" href="http://creativecommons.org/licenses/by/4.0/">`. The cities page (S-cp1-056) has no licence link.

**Source credit (S-cp1-056).** "General Statistics Authority, Kingdom of Saudi Arabia." The admin page carries the same credit as "Source: General Statistics Authority, Kingdom of Saudi Arabia." (live page, line 180 of the stripped text).

**Liability (S-cp1-050).** "your use of the services is at your sole risk"; services are provided "as is" and "as available"; legal claims go to "courts located in Oldenburg (Oldb.), Germany".

**GASTAT (S-cp1-058).** Section 1.2.2: "provided that GASTAT is acknowledged as the official source and any modifications are clearly indicated", with reuse "for any purpose, including commercial use in accordance with the Open Data principle". Section 1.4.2: "Modified material must not be presented as official GASTAT statistics".

## 4. Analysis (not the site's words)

**4.1 What the grant covers.** The licence covers "the presented population data": the numbers as the site presents them. It does not cover maps, geodata, coordinates, images, programs or the site's appearance (all reserved). The Terms do not say whether the selection and layout of the tables (the site's compilation) is covered. Our use is limited to the numbers, so this gap does not block use; it does mean we should not copy table layouts or reproduce the page as a product.

**4.2 Commercial use.** Yes for the population figures, under either CC BY version (both expressly permit commercial use). Not granted for maps, geodata or site resources. Recorded as `Y` for the population figures in the proposed row; the qualifier is in the notes.

**4.3 Attribution.** Minimum wording, from S-cp1-050: "Thomas Brinkhoff: City Population, http://www.citypopulation.de (or the URL of the specific page)". Add the GASTAT credit: the page credits "General Statistics Authority, Kingdom of Saudi Arabia" (S-cp1-056) and GASTAT's own condition is acknowledgement "as the official source" (S-cp1-058). Our proposed credit line is in section 5. Note the name variance: the site says "General Statistics Authority"; GASTAT's own page is GASTAT. Inference, not verified: same body. Counsel or the GASTAT portal should confirm before any formal use.

**4.4 Redistribution.** Numbers: allowed with attribution. Page copies: not licensed. An archived HTML page carries the reserved "appearance", map code and third-party script load, not only the numbers. So redistributing it (commit, data room, release, film) is outside the licence. Redistributing derived tables with citation is the route we use.

**4.5 Share-alike and other obligations.** The population figures carry no share-alike condition in the Terms. Obligations that do attach: attribution; a hyperlink in web media; the third-party (GASTAT) conditions; and, for any modified figure, a clear statement that it was modified and is not an official GASTAT statistic (GASTAT s. 1.4.2). Area figures on the regional pages are "computed by using geospatial data" (archived Eastern copy, `data/ksa/regions-pilot/citypop-eastern-census2022.html`); those derive from geodata that is reserved, so do not reuse area figures from this site without a separate source.

**4.6 Where the site's figures are not GASTAT figures.** Some places are the site's own calculations (S-cp1-052). Label any figure from that category as "citypopulation.de calculation", not as GASTAT.

**4.7 Jurisdiction.** The Terms are German-law terms (courts in Oldenburg). This note is not legal advice; counsel should confirm the reading of "presented population data" and the status of the compilation if the project goes public.

## 5. Proposed licence-register row (for approval; not written to `docs/licences.csv`)

- **item:** City Population (citypopulation.de) population figures, Saudi Arabia Census 2022 governorate and place tables, as relayed from GASTAT (secondary aggregator; cross-check rows only)
- **version:** Terms of Use (EN and DE) read 31 Oct 2026; Saudi pages fetched 31 Oct 2026 (admin, cities, Al-Qaseem region); pages carry no date
- **source_url:** https://www.citypopulation.de/en/help/termsofuse/ ; https://www.citypopulation.de/en/saudiarabia/admin/ ; https://www.citypopulation.de/en/saudiarabia/cities/ ; https://www.citypopulation.de/en/saudiarabia/qasim/
- **licence:** CC BY 3.0 (stated in the Terms of Use, EN and DE); CC BY 4.0 (declared in the HTML of the Saudi pages). CONFLICT, unresolved.
- **open:** Y (population figures only; maps, geodata, coordinates, site design, programs and images are not open, see notes)
- **commercial_use:** Y (population figures only, with attribution; maps, geodata and site resources are not licensed for reuse)
- **attribution_required:** "Population data: Thomas Brinkhoff: City Population, http://www.citypopulation.de (URL of the page), licence CC BY [3.0 or 4.0 - to fix]; underlying official source: General Authority for Statistics (GASTAT), Kingdom of Saudi Arabia, Census 2022." Any modified figure: "Modified from [source]; not an official GASTAT statistic."
- **obligations:** attribution; hyperlink in web media; GASTAT conditions (acknowledged as official source; modifications marked; not presented as official GASTAT statistics); no redistribution of maps, geodata, coordinates, site pages or archived HTML (reserved to City Population); CC BY-SA geodata not covered (contact site owner, not done); no share-alike on the figures
- **used_in:** `data/ksa/hail/citypop_hail_census2022.csv` (derived transcription); `data/ksa/regions-pilot/citypop-eastern-census2022.html` and `data/ksa/pilot-qassim/raw/citypop_*.html` (archived copies, see section 6); `docs/sources/index.csv` citypopulation rows (S-065 to S-089 and the S-*-001/002 rows); `docs/sources/pilot-*.csv`
- **status:** verified 2026-10-31 (terms text read on the publisher's site); licence version conflict open (see notes)
- **approval:** pending Tariq (CP1)
- **notes:** Replaces, on approval, the rows in `docs/licences.csv` at lines 125, 131, 136, 140, 145 and 152, which read "terms not checked" or "unclear". Commercial use is `Y` for the figures only. Conflict CC BY 3.0 vs 4.0 to be logged in `docs/sources/conflicts.md` on approval. GASTAT is a separate row (its use policy, S-cp1-058) and governs the underlying numbers too.

## 6. Archived HTML copies under `data/ksa/` (analysis and proposal)

Files: `data/ksa/regions-pilot/citypop-eastern-census2022.html`; `data/ksa/pilot-qassim/raw/citypop_admin.html`; `data/ksa/pilot-qassim/raw/citypop_cities.html`; `data/ksa/pilot-qassim/raw/citypop_qasim_region.html`.

Checks run on 31 Oct 2026: the live `admin` and `cities` pages were compared with the archived copies. The admin page differs only in one server cache-timing comment (`sha256` of the live copy `8d6e97e8…`, of the archived copy `b4f28542…`). The Al-Qaseem page differs only in the same comment. The cities page is identical. So the archived copies match the live pages on 31 Oct 2026 (dates of capture for the Eastern copy are not recorded in the file).

- **Redistribution:** not licensed. The Terms reserve appearance, programs and maps (S-cp1-050). A saved page is mostly those things. Do not commit, publish, put in a data room or release, or include in film or app assets.
- **Private local keeping:** the Terms are silent. Nothing in them forbids a private copy for verification. But the licence does not reach the page's reserved parts, so the position is "not licensed, not forbidden". Proposal: keep the four files only in `data/ksa/` (gitignored by `.gitignore` rule `data/*`), for verification only, until the GASTAT primary table is obtained; then delete them.
- **If Tariq says drop them now** (the consequence the brief asks for, where the terms are silent or forbid redistribution): keep only derived numbers with citation (the `docs/sources/index.csv` rows and `data/ksa/hail/citypop_hail_census2022.csv`, which is a transcription marked as secondary), and delete the archived HTML. The derived numbers are secondary until the GASTAT table replaces them (source-citation skill).

## 7. Conflicts, escalations and questions for Tariq (CP1)

1. **Licence version conflict (CC BY 3.0 in the Terms vs CC BY 4.0 in the page HTML).** Unresolved. Proposed handling: print both in the attribution until Tariq decides, and comply with the stricter CC BY 4.0 conditions (indicate changes, link the licence). Analysis from the CC BY 4.0 legal code, not re-read in this run.
2. **Archived HTML copies:** keep (private, gitignored, until replaced) or drop now. One decision: Tariq (CP1).
3. **Existing `docs/licences.csv` rows** at lines 125, 131, 136, 140, 145, 152 say "terms not checked" or "unclear". They are superseded on approval of section 5. Not edited here.

## 8. Not verified

- The legal effect of the German-law Terms, and whether the site's table compilation is a protected database, were not assessed by counsel.
- The CC BY 3.0 and 4.0 deed texts were not fetched; the attribution conditions above are from the Terms and the CC BY 4.0 legal code as known to the author.
- The Terms carry no date; the "as of" for the terms is the access date (31 Oct 2026).
- Equivalence of "General Statistics Authority" (site credit) and GASTAT: inference, not verified.
- The Eastern archived copy has no URL or capture date in the file; its URL is taken from `docs/sources/index.csv` (S-eastern-001) and not re-read.
- No WebFetch summary was used as a quote source. Summaries that disagreed with the raw HTML were not carried over.
