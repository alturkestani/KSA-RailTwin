> **Document version:** docs/sources/r1a-data-inventory.md v0.1 | 31 Oct 2026 | Author: rail-data-scout (R1a) | Status: draft

# R1a data inventory: settlement universe, population grids, economy and demand

Access date for every row: **2026-10-31** (Asia/Riyadh). Source rows: `docs/sources/r1a-data.csv` (ids S-r1a-500 to S-r1a-531; the existing GASTAT rows S-069 to S-091 and the rail rows S-040 to S-045 are reused, not duplicated). Status vocabulary: `verified` (read on the publisher's site on the access date), `secondary` (press, aggregator, reproduction or search extract), `unverified` (not read, blocked, or not found). Task B status words are used in the Status column of the tables: `used`, `planned`, `not found`, `unverified`.

## 1. Headline

- **GASTAT Census 2022 primary tables: NOT reached.** `portal.saudicensus.sa` refused connections on 31 Oct 2026 (curl exit 000), as on 30 Oct (DNS). The stats.gov.sa census category pages load, but the document links are not in the static HTML, and open.data.gov.sa and data.gov.sa answer only with a WAF rejection to API calls. No official XLSX, CSV or PDF of the census region, governorate or locality tables was found, so **nothing was downloaded to `data/ksa/census/`** (the directory was created and is empty).
- **Governorate count as stated by GASTAT: not found.** The 13 region rows are confirmed by GASTAT's own news (S-070) and by a GLMM reproduction of the GASTAT census table (S-r1a-502), whose 13 regional totals sum exactly to the national total of 32,175,224 (checked in code). That reproduction has no governorate rows. The working count of 150 governorate rows (citypopulation.de, S-073) stays `secondary`, and the coverage table keeps reconciling to it with the conflict noted.
- **Population grids:** WorldPop Saudi Arabia 2020 downloaded (three files, 59 MB in total, hashed below). GHSL R2023A verified but not downloaded (the 100 m global tile is 5.59 GB; the 1 km global tile is 283 MB and was not needed for this pass).
- **Licence verdicts:** WorldPop = CC BY 4.0 (read on the hub page; attribution required, commercial use allowed). GHSL GHS-POP = CC BY 4.0 (quoted from the AWS Open Data registry; the JRC page could not be read as text, so the JRC confirmation is open). VIIRS VNP46A4 = licence not stated on the product page: **unclear, not used**.
- **Disk (CLAUDE.md gate 15 GiB):** start of session 32 GiB free; before the first download 29 GiB free; after the two first WorldPop files still 29 GiB; after the third file and the `uv` install of rasterio and numpy (run with `-I`) 26 GiB free. The downloads total about 59 MB; the 3 GiB difference in the last step is not from the downloads and has not been traced (the `uv` cache under the home directory is the likely cause, not verified).

## 2. Census and settlement universe (GASTAT primary)

What was tried on 31 Oct 2026, with the result for each:

| attempt | result |
|---|---|
| portal.saudicensus.sa (census table page, root) | connection failed (curl 000); unreachable on 30 Oct too (S-090) |
| stats.gov.sa census category (`statistics?index=119025`, census subindex 127380) | page loads; subindex lists are script-loaded; no XLSX, CSV or PDF links in the static HTML |
| stats.gov.sa census key results (search) | no PDF of census 2022 key results or region/governorate tables returned by search |
| open.data.gov.sa (dataset listing, API) | listing loads (empty extract); API blocked by a WAF rejection |
| data.gov.sa (CKAN API) | API blocked by a WAF rejection; no GASTAT census dataset in search |
| GLMM reproduction of GASTAT census 2022 region table (gulfmigration.grc.net/?p=9681) | 13 region rows; source line "Source: Saudi Arabia census 2022"; access printed 15 June 2023; **secondary** (S-r1a-502) |
| Argaam (31 May 2023 release date, national total 32,175,224) | secondary (S-r1a-501) |

Settlement-level data: no GASTAT locality (تجمع سكاني) table was found. Locality populations for untabulated towns therefore come from the grids in section 3 (`pop_type: grid`, `pop_source_status: secondary`), and any census-2022 figure for a town stays a `secondary` citypopulation.de value until the GASTAT table is read.

## 3. Population grids

### 3.1 WorldPop Saudi Arabia 2020 (verified; downloaded)

| file | resolution | constraint | UN-adjusted | cell sum (our sum, derived) | bytes | downloaded to |
|---|---|---|---|---|---|---|
| `sau_ppp_2020_1km_Aggregated_UNadj.tif` | 1 km (0.00833 deg), 2532 x 1941 | unconstrained, aggregated | yes | 34,813,867 | 10,216,812 | `data/ksa/grids/` |
| `sau_ppp_2020_UNadj_constrained.tif` | 100 m (0.000833 deg), 25315 x 19411 | constrained | yes | 34,813,867 | 13,573,955 | `data/ksa/grids/` |
| `sau_ppp_2020_constrained.tif` | 100 m | constrained | no | 37,034,282 | 35,702,740 | `data/ksa/grids/` |
| `sau_ppp_2020_UNadj.tif` (unconstrained 100 m) | 100 m | unconstrained | yes | not downloaded | 755 MB | listed only (over 500 MB) |
| `sau_ppp_2020.tif` (unconstrained 100 m) | 100 m | unconstrained | no | not downloaded | 910 MB | listed only (over 500 MB) |

- **Verdict on the grid choice:** use the UN-adjusted constrained 100 m file for untabulated towns (it matches the 1 km aggregate cell for cell in total, so the two are consistent). Do not use the non-adjusted constrained total (37.0 M) as a national figure.
- **Cross-check, not averaged:** the 2020 UN-adjusted total (34.8 M) is above the GASTAT census-2022 count (32.18 M, 10 May 2022). The gap mixes a year difference, a UN revision and the census count; log it as a conflict for W2 and W8 rather than blend them.
- **Licence:** "WorldPop datasets are available under the Creative Commons Attribution 4.0 International License." (hub page, Saudi Arabia 100 m, id 49877; the site-wide statement is on the Indonesia page, id 24826, which was read as well). DOI for the 100 m constrained product: 10.5258/SOTON/WP00684 (hub). The hub notes that datasets derived from OpenStreetMap or Microsoft building data fall under ODbL; these files are not stated to be derived from either, so check the per-file terms before any release.
- **Method (from the metadata report):** random-forest dasymetric disaggregation of census or administrative counts to 3 arc-second cells, using covariates that include 2016 VIIRS night lights and distance to roads and urban areas. These covariates matter for the geo-verify second estimator (they are not independent of night lights).

### 3.2 GHSL GHS-POP R2023A (verified listing; licence secondary; not downloaded)

| item | value | source |
|---|---|---|
| release | R2023A, epochs 1975 to 2030 in 5-year steps | S3 bucket `jrc-ghsl`, prefix `ghs-pop/r2023a/` (S-r1a-509, S-r1a-510) |
| resolution and projection | 100 m and 1 km, World Mollweide EPSG:54009 (also EPSG:4326 at 3 and 30 arc seconds) | AWS registry entry (S-r1a-511) |
| E2020 global 100 m | 5,588,564,329 bytes (not downloaded) | S3 listing |
| E2020 global 1 km | 283,202,782 bytes (not downloaded) | S3 listing |
| licence | CC BY 4.0: "GHSL data are provided under the Creative Commons Attribution 4.0 International (CC BY 4.0) license." | AWS Open Data registry (secondary); the JRC download page did not return text on the access date |

- **Verdict:** open and usable (CC BY 4.0, attribution required, commercial use allowed) once the JRC page is read. Status for the licence stays `secondary` until then.
- **Relation to WorldPop:** GHS-POP is built from the GPW census disaggregation informed by GHSL built-up areas, so it is not an independent population source from the same census counts. It is a second estimator with different covariates, which is what geo-verify needs.

## 4. Economy and demand inventory (Task B)

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

## 5. Downloads

| path | URL | bytes | SHA-256 | licence | edition |
|---|---|---|---|---|---|
| `data/ksa/grids/sau_ppp_2020_1km_Aggregated_UNadj.tif` | https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/SAU/sau_ppp_2020_1km_Aggregated_UNadj.tif | 10216812 | 6931471b02326202c078a5a3675909f4f076ce52a2477bb419d053a154a57f17 | CC BY 4.0 (WorldPop) | WorldPop 2020, 1 km, UN-adjusted, aggregated (listing 2020-06-22) |
| `data/ksa/grids/sau_ppp_2020_UNadj_constrained.tif` | https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/SAU/sau_ppp_2020_UNadj_constrained.tif | 13573955 | c3497fb189af23b8f266c858ed1d43485c71c0b262f11570fc9018dc5056239c | CC BY 4.0 (WorldPop) | WorldPop 2020, 100 m, constrained, UN-adjusted (listing 2020-09-20) |
| `data/ksa/grids/sau_ppp_2020_constrained.tif` | https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/BSGM/SAU/sau_ppp_2020_constrained.tif | 35702740 | 68e6da9516b80cc242760f996776a169c70a1cc03fc0996bc0953ca91853cce0 | CC BY 4.0 (WorldPop) | WorldPop 2020, 100 m, constrained, not UN-adjusted (DOI 10.5258/SOTON/WP00684) |
| `data/ksa/census/` | none (no GASTAT census file found under 50 MB) | 0 | n/a | n/a | directory created, empty |

Total grid downloads: 59,493,507 bytes (about 59 MB). Each file is under `data/` (gitignored). The SHA-256 values are for the coordinator to register in `cities/ksa/sources.yaml` (I did not edit the manifest). The cell sums in section 3.1 are my own sums of the rasters (rasterio, CRS EPSG:4326, nodata -99999 masked), so they are derived, not published totals.

## 6. Licence rows (licences.csv columns)

Ready for `docs/licences.csv` (open items have an empty `approval`; the two unclear items are flagged). Columns: item, version, source_url, licence, open, commercial_use, attribution_required, obligations, used_in, status, approval.

```csv
item,version,source_url,licence,open,commercial_use,attribution,obligations,used_in,status,approval
WorldPop Saudi Arabia 2020 population counts (1 km UN-adjusted aggregated; 100 m constrained UN-adjusted and not),2020 (listing 2020-06-22 and 2020-09-20),https://hub.worldpop.org/geodata/summary?id=49877,CC BY 4.0,Y,Y,"WorldPop (www.worldpop.org, University of Southampton), Saudi Arabia 2020 population counts, doi:10.5258/SOTON/WP00684, CC BY 4.0",Attribution; per-file check for OSM- or Microsoft-derived data (ODbL),W1 population grids (docs/sources/r1a-data-inventory.md),downloaded (verified),
"GHS-POP R2023A (Global Human Settlement Layer; population grid; 1 km and 100 m; epochs 1975 to 2030)",R2023A,https://registry.opendata.aws/ghs-pop/,CC BY 4.0,Y,Y,"European Commission JRC, GHS-POP R2023A (Schiavina, Freire, Carioli, MacManus, 2023), CC BY 4.0",Attribution; JRC licence page to confirm,W1 population cross-check (not downloaded),listed (licence secondary),
GASTAT census 2022 region table (as reproduced by GLMM),census 2022 (reference 10 May 2022),https://gulfmigration.grc.net/?p=9681,GASTAT use policy (reuse with acknowledgement; modified material marked),Y,Y,"Source: General Authority for Statistics (GASTAT), Saudi Arabia census 2022; modified material marked as modified",Acknowledge GASTAT; no presentation as official if modified,W2 coverage (docs/gastat-regions.md),secondary reproduction,
GASTAT Real Estate Price Index Q1 2025 (PDF),Q1 2025,https://www.stats.gov.sa/documents/20117/2435267/RPI+Q1+2025+EN.pdf/6385a45f-e30d-5744-0b2d-661512e15bec,GASTAT use policy,Y,Y,"Source: General Authority for Statistics (GASTAT), Real Estate Price Index",Acknowledge GASTAT; mark modified material,W1 demand covariate (planned),verified,
GASTAT Hajj 1446H statistics (headline and executive summary),1446H (2025),https://stats.gov.sa/en/w/news/49,GASTAT use policy,Y,Y,"Source: General Authority for Statistics (GASTAT), Hajj statistics 1446H",Acknowledge GASTAT,W1 demand (seasonal),verified (headline),
GASTAT railway transport statistics 2025 (existing row),2025 edition (uploaded 2026-10-18),https://www.stats.gov.sa/documents/20117/2435281/Railway+Transport+Statistics+Publication+2025+EN.pdf,GASTAT use policy,Y,Y,"Source: General Authority for Statistics (GASTAT), Railway Transport Statistics 2025",Acknowledge GASTAT,W1 (already in manifest),used,
VIIRS/NPP Black Marble VNP46A4 v2.0 (annual night lights; proxy),2.0 (DOI 10.5067/VIIRS/VNP46A4.002),https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A4,not stated on the product page; catalogue lists none (unclear),N,unclear,"NASA LAADS DAAC, VIIRS/NPP Black Marble VNP46A4 (licence to confirm)",Unknown until NASA data-use policy is read,W1 proxy (not used in R1a),unverified: licence unclear; not used,
UN World Population Prospects 2024 (national totals),2024 revision,https://population.un.org/wpp/downloads/,CC BY 3.0 IGO,Y,Y,"United Nations, Department of Economic and Social Affairs, Population Division, World Population Prospects 2024",Attribution (IGO licence); download page to confirm (HTTP 404 on 2026-10-31),W8 control totals (planned),unverified (download page),
"Argaam and other press (GACA, TGA, Hajj and airport figures cited as secondary)",n/a,https://www.argaam.com/en/article/articledetail/id/1831189,press copyright (Argaam; Al Riyadh; Aletihad),N,unclear,"Quoted figures attributed to the primary publisher (GACA, TGA, GASTAT); not reproduced as data",Not for redistribution; cross-check only,cross-check rows S-r1a-518 to S-r1a-521,secondary (cross-check only),Tariq (only if any figure is used as data)
IATA busiest airport pairs (airline-reported),2025 (press citing IATA),https://aircargoweek.com/iata-reveals-worlds-busiest-airport-pairs-for-2025/,IATA terms (not read),N,unclear,"IATA (airline-reported traffic, press citing IATA)",Not used as data; licence to read,cross-check only (S-r1a-530),secondary (cross-check only),Tariq (before any use as data)
GACA press releases (passenger totals),H1 2025 (31 Jul 2025 release),https://gaca.gov.sa/en/News/gaca-66-million-travelers-463k-flights-2025,GACA website terms (not read),N,unclear,"GACA (General Authority of Civil Aviation), H1 2025 passenger statistics",To read GACA terms before data use,cross-check rows S-r1a-519 and S-r1a-520,verified (page read); terms unread,Tariq (before any use as data)
"GLMM (Gulf Labour Markets, Migration and Population) reproductions of GASTAT tables",2026 access,https://gulfmigration.grc.net/?p=9681,GLMM site terms (not read),N,unclear,"GLMM, reproducing GASTAT tables (source line printed in table)",Use only as cross-check until the GASTAT primary is read,S-r1a-502 and S-r1a-523 and S-r1a-525,secondary,Tariq (before any use as data)
```

Notes on the rows: `open = N` on the press, IATA, GACA and GLMM rows does not say the sources are closed; it says their terms were not read. The licence-register check fails on `open = N` without an approval, which is the intended flag until each is read or removed.

## 7. Conflicts and cross-checks (not averaged)

- **Census 2022 national total vs WorldPop 2020 UN-adjusted sum:** 32,175,224 (GASTAT census, 10 May 2022, via press and GLMM) vs 34,813,867 (our sum over the UN-adjusted 2020 grid). Different years and different methods. Log as a conflict candidate (C-012 proposed) for the coordinator.
- **Mid-2024 national population:** GASTAT press figure 35,300,280 (S-r1a-525, secondary) vs the UN WPP 2024 mid-2024 figure of about 33.96 M quoted in a fact-check page (not read on the UN site). Log as a conflict candidate (C-013 proposed).
- **Governorate count:** 150 (citypopulation.de, S-073), 139 (S-074), 136 (S-075), 135 (S-076 variant) remain open; GASTAT primary not reached (S-r1a-503).
- **Real-estate Q4 2025 residential change:** a blog reports -2.2%, another -2.24%; the GASTAT Q4 release page gives only the overall -0.7% (S-r1a-515). Not used.
- **Bus statistics:** TGA Q2 2025 trips (44,000) and the Q4 2025 and Q2 2026 passenger figures come from press with different units (trips vs passengers). Not combined.

## 8. Escalations (for the coordinator)

1. **Register the downloads** in `cities/ksa/sources.yaml` (three WorldPop files, section 5) and run `uv run python -m common.manifest verify`. I did not edit the manifest.
2. **Licence rows:** add section 6 to `docs/licences.csv` (or the track file). The VNP46A4 row and the press/IATA/GACA/GLMM rows carry `open = N` or `unclear` and will fail the check until Tariq approves or they are removed.
3. **GASTAT census primary:** retry in a session where `portal.saudicensus.sa` resolves; if it does, the census XLSX (under 50 MB) goes to `data/ksa/census/` and needs a manifest row.
4. **UN WPP download URL:** `population.un.org/wpp/downloads/` returned 404 on 31 Oct 2026; the WPP 2024 CSV needs a fresh link before W8 uses it.
5. **GHSL JRC licence page:** read `ghsl.jrc.ec.europa.eu` licence text before the GHS-POP row is set to `verified`.
6. **Second-estimator grid (geo-verify):** GHS-POP E2020 at 1 km (283 MB) is the candidate second estimator if the coordinator wants it. Not downloaded; the 100 m global tile (5.6 GB) is out of scope.
7. **Escalated for W2:** whether to replace the 150-row list with the GASTAT list once the census portal is reachable (C-010 and C-011 unchanged).
