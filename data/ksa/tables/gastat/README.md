# GASTAT population tables for KSA Rail Twin

Retrieved 2026-10-31 (UTC) from Grok Bot's box, for CP2 decision P1a ("GASTAT-relayed figures win where they exist"). Full per-file provenance, licence and SHA-256 are in `sources.csv`. File names are the originals from the publisher. Tableau exports are named `<workbook>_<view>`.

## What is here

**Public export (Tariq, 12 Nov 2026, Q5):** the four DataPulse relay files (`census-2022-20260929.csv`, `census-2022-dictionary.csv`, `population-region-20260928.csv`, `population-region-dictionary.csv`) stay in the author's private repository only and are not in the public release. Cite GASTAT directly: the primary TA1 exports `census2022_TA1_governorate_primary.xlsx` (S-cp2-gastat-007) and `census2022_TA1_city5k_primary.xlsx` (S-cp2-gastat-008) and the TA9 region series (S-cp2-gastat-003) carry the same values (C-gastat-001, 0 differences). Code paths that still read the relay (`screening.gastat` cross-checks, the coverage rebuild) need the private file; their tests skip without it.

| Need | Best file | Level | Year | Status |
|---|---|---|---|---|
| Census 2022 by governorate (150), total/Saudi/non-Saudi/sex | census-2022-20260929.csv | governorate | 2022 | RELAYED (DataPulse, from GASTAT census Tableau). Governorates sum exactly to the KSA total of 32,175,224 |
| Census 2022 by city (60 main cities) | census-2022-20260929.csv | city | 2022 | RELAYED |
| Census 2022 by region | TA1-...pdf, TA2-...csv, TA9-...csv | region | 2022 | PRIMARY (official Tableau exports) |
| Region series 2010-2022 | TA9-...csv; population-region-20260928.csv | region | 2010-2022 | PRIMARY / RELAYED |
| Estimates 2023-2024 | Population_Estimates_*_2024* | national only | 2023-2024 | PRIMARY. GASTAT publishes 2023-24 estimates nationally by age, sex and nationality, with no region tables in the files |
| Census 2010 by governorate | twzy_lskn_fy_lmhfzt.xlsx (+ census31-prim-04.pdf) | governorate | 2010 | PRIMARY |
| Census 2010 cities >5,000 (~245) | lntyj_lwly_ltdd_2010_..._5000_...xlsx (EN), lntyj_lwly_ltdd_2010_nhyy_mntq_wmhfzt.xlsx (AR) | city | 2010 | PRIMARY |
| Census 2010 regions / detailed Kingdom results | twzy_lskn_fy_lmnzq_ldry_(1).xlsx, lntyj_ltfsylyh_llmmlk.xlsx | region / national | 2010 | PRIMARY |
| Census 2022 methodology | 1_VGA_..._Census_2022_Documentation_compressed.pdf | docs | 2022 | PRIMARY |

## What could not be got, and why

- **portal.saudicensus.sa** (all paths, e.g. https://portal.saudicensus.sa/portal and https://portal.saudicensus.sa/portal/public/1/15?type=TABLE): the TLS handshake is dropped (`SSL unexpected eof`) from this network as well as from the Mac, so the official census 2022 table downloads, including any locality-level tables, were not reachable. No bypass was attempted.
- **Census 2022 governorate/city/locality tables on tableau.stats.gov.sa** (TA1, TA12, TC1 "by Region, Governorate, City"): the dashboard CSV export returns an empty file. Setting the URL parameter to governorate renders a blank table, and the interactive view shows the Tableau "Unexpected Error" banner. Only the region-level default views export. The dashboards' own "Excel download" buttons need a full browser session. That was not tried.
- **Census 2022 locality (village/hijra) populations**: not found published anywhere reachable. GASTAT lists them only inside the census portal.
- **Official 2023-2025 regional estimates**: the 2024 estimates release has only national tables. No regional file was found on stats.gov.sa.
- **HDX COD-PS (cod-ps-sau)**: every resource download returns S3 `AccessDenied` (an HDX-side fault). It is region-level only, so nothing is lost.

## Caveats
- RELAYED files are third-party re-packagings that cite GASTAT. They are not official statistics. Use them for P1a, but label them `gastat_relayed`. Spot checks agree with the primary files (KSA and Riyadh totals).
- DataPulse CSVs start with 5 `#` comment lines. Read them with `pd.read_csv(path, comment="#")`.
- The 2010 census files are *preliminary results* (النتائج الأولية).
- Arabic file names are transliterations used by GASTAT's CMS (e.g. twzy_lskn_fy_lmhfzt = توزيع السكان في المحافظات).

## Addendum 2 (31 Oct 2026, 15:25 +03): primary Census 2022 TA1 exports

Two files exported by Tariq from the GASTAT TA1 Tableau dashboard with its own "Export as Excel" button (provenance, retrieval time and SHA-256 in `sources_tableau_2022.csv`; hashes checked by the coordinator). Source label `gastat_primary`. **They supersede `census-2022-20260929.csv` (DataPulse, relayed) at governorate and city level**; the relayed file stays as a cross-check only.

| File | Level | Rows | Columns | Total |
|---|---|---|---|---|
| census2022_TA1_governorate_primary.xlsx | governorate | 150 + Total | Governorate, Total, Saudi, Non-Saudi | 32,175,224 |
| census2022_TA1_city5k_primary.xlsx | city of 5,000 or more | 271 + "Other (Less than 5000 inhabitants)" (3,683,816) + Total | City, Total, Saudi, Non-Saudi | 32,175,224 |

Neither file carries a region column or Arabic names; `screening.gastat` joins them by English name (crosswalk `screening/gastat_crosswalk.yaml`).
