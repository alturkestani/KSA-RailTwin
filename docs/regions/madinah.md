> **Document version:** docs/regions/madinah.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_MADINAH) | Status: draft

# Region sweep: Al-Madinah al-Munawwarah (المدينة المنورة), slug `madinah` (R2)

Screening input, not a forecast.

## 1. Governorate count (GASTAT vs listed)

- `governorates_gastat` = **9** (S-073: the relayed census governorate list gives 9 rows for the region, capital included). The primary TA1 governorate export (S-cp2-gastat-007) has all 9 names with populations; it has no region column, so membership rests on S-073.
- `governorates_listed` = **9** (distinct governorates in the rows). Equal: no discrepancy.
- Wādī al-Fara' has a row (governorate centre not identified; section 5). The pilot's '8 of 9' gap is closed by that row, not by a sourced seat.

## 2. Counts

- Rows in the register: **21** (9 governorate-centre rows, incl. Wādī al-Fara'; 12 other settlements).
- At or above 10,000 (`tag_10k`): **8** rows, all official GASTAT.
- Grid-only at or above 10,000, uncorroborated (kept, `tag_10k` false, `exclusion_reason` set): **2** rows.
- At or above 5,000 (`tag_5k`, sensitivity set): **20** rows.
- Settlements below 5,000 in the R1a universe, not written: **774** (rule 2: counted, not silently dropped).
- Economic roles recorded: **19** (each with an `S-` source); rows with no role: 14 (roles not assessed beyond the R1a nodes).
- Terrain: **not assessed** for every row (`terrain_class` null): no DEM terrain layer is in the R1a outputs and the disk gate forbids a new DEM download here (section 6).

## 3. Register (table)

Population: `official` = GASTAT primary (verified); `grid` = WorldPop gap-fill (unverified); `derived` = OSM tag. Distances are straight-line (haversine) to the nearest existing station (HHR) and the metro; road minutes are the R1a OSRM car skim.

| # | name (EN) | name (AR) | governorate | centre | population | type / status | ≥10k | ≥5k | dist existing km (road min) | nearest metro (tier) | roles |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Khaybar | خيبر | Khaybar | yes | 15,888 | official / verified | yes | yes | 142.8 (132) | Madinah (tier 1, A-screen-013) | heritage; tourism; agriculture |
| 2 | Al 'Uyun | العيون | Al Madinah Al Munawwarah | no | 11,547 | grid / unverified | no | yes | 14.9 (25) | Madinah (tier 1, A-screen-013) | — |
| 3 | Sidi Hamzah | سيدي حمزة | Al Madinah Al Munawwarah | no | 30,876 | grid / unverified | no | yes | 8.9 (14) | Madinah (tier 1, A-screen-013) | — |
| 4 | Al Hanakiyah | الحناكية | Al Hinakiyah | yes | 24,880 | official / verified | yes | yes | 94.0 (66) | Madinah (tier 1, A-screen-013) | — |
| 5 | Mahd adh Dhahab | مهد الذهب | Al Mahd | yes | 20,272 | official / verified | yes | yes | 161.4 (203) | Madinah (tier 1, A-screen-013) | mining |
| 6 | Al Faqir | الفقير | Wadi Al Fara | no | 7,231 | grid / unverified | no | yes | 116.8 (125) | Madinah (tier 1, A-screen-013) | — |
| 7 | Badr Hunayn | بدر | Badr | yes | 30,494 | official / verified | yes | yes | 120.1 (119) | Madinah (tier 1, A-screen-013) | heritage; tourism |
| 8 | Yanbu' | ينبع | Yanbu | yes | 258,777 | official / verified | yes | yes | 170.7 (154) | Madinah (tier 1, A-screen-013) | port; industrial_city; energy; airport; university |
| 9 | Medina | المدينة المنورة | Al Madinah Al Munawwarah | yes | 1,411,599 | official / verified | yes | yes | 9.0 (18) | Madinah (tier 1, A-screen-013) | airport; hajj_umrah; industrial_city; university |
| 10 | مغيراء | مغيراء | Al Ula | no | 5,012 | grid / unverified | no | yes | 275.3 (292) | Tabuk (tier 2, A-screen-013) | — |
| 11 | al 'Aiss | العيص | Al Is | yes | 8,760 | official / verified | no | yes | 173.6 (211) | Madinah (tier 1, A-screen-013) | — |
| 12 | (unnamed OSM node 6768368404) | (unnamed OSM node 6768368404) | Khaybar | no | 5,424 | grid / unverified | no | yes | 124.9 (120) | Madinah (tier 1, A-screen-013) | — |
| 13 | Ath Thamad | الثمد | Khaybar | no | 8,385 | official / verified | no | yes | 122.9 (116) | Madinah (tier 1, A-screen-013) | — |
| 14 | مصنع الإسمنت | مصنع الإسمنت | Yanbu | no | 5,559 | grid / unverified | no | yes | 218.1 (203) | Madinah (tier 1, A-screen-013) | — |
| 15 | سد الغاب | سد الغاب | Al Madinah Al Munawwarah | no | 5,139 | grid / unverified | no | yes | 19.1 (26) | Madinah (tier 1, A-screen-013) | — |
| 16 | Al Mohaffar | المحفر | Al Hinakiyah | no | 7,174 | derived / unverified | no | yes | 95.7 (74) | Madinah (tier 1, A-screen-013) | — |
| 17 | Al-Ula | العلا | Al Ula | yes | 40,760 | official / verified | yes | yes | 290.4 (307) | Tabuk (tier 2, A-screen-013) | airport; giga_project; heritage |
| 18 | الحسو | الحسو | Al Hinakiyah | no | 9,071 | grid / unverified | no | yes | 194.3 (180) | Madinah (tier 1, A-screen-013) | — |
| 19 | Al Wu'ayrah | الوعيرة | Al Madinah Al Munawwarah | no | 6,693 | grid / unverified | no | yes | 7.3 (18) | Madinah (tier 1, A-screen-013) | — |
| 20 | Yanbu' al-Sina'iyah (Yanbu Industrial City) | المدينة الصناعية بينبع | Yanbu | no | 73,139 | official / verified | yes | yes | 170.4 (—) | Madinah (tier 1, A-screen-013) | industrial_city |
| 21 | Wadi al-Fara' (governorate seat not identified) | وادي الفرع | Wadi Al Fara | yes | — | — | no | no | — (—) | — | — |

Node and station labels: `nearest_existing` is the R1a station id (`hhr:madinah`, `hhr:kaec`), named in the register; `nearest_committed` is the Saudi Landbridge committed layer, with its stations unlocated (R1a), so `nearest_committed_station` is null.

## 4. Exclusions and what is not in the table (rule 2)

- **Below 5,000:** 774 R1a settlements; not rows of this register (the sensitivity threshold is 5,000).
- **Grid-only, ≥ 10,000, uncorroborated:** Al 'Uyun, Sidi Hamzah. Kept as rows with `tag_10k` false; no second method was run (A-screen-031/032).
- **Wadi Al Oqool farms (GASTAT primary, 24,381, official):** NOT a row. It is an official ≥10,000 settlement the register should hold, but it has no OSM node and no coordinates in any source reached (the pilot also could not place it). `RegionRow` needs lat/lon, and a proxy point would give wrong distances. **Open: needs a located point (judgement at the merge).**
- **Wādī al-Fara' seat:** row kept with `screened: false`, no population, no distances. S-madinah-015 names seven subdivision centres and no seat; none is chosen.
- **GASTAT primary cities not matched to any settlement in the R1a universe:** 66 rows, not counting the two discussed above (Yanbu Industrial City, now a row; Wādī al-'Uqūl farms) and 'Other'. Their region is not stated in the primary export, and the R1a matching did not place them. Of these, **18** are at or above 10,000; any that belongs to Al-Madinah region would be a missing row. Listed in section 7. **Open: needs the GASTAT city-to-governorate table (judgement at the merge).**

## 5. Centres and the Wādī al-Fara' gap

- Every governorate of the 9 has a row. Centres are the place carrying the governorate's name (the census city row, matched in the R1a universe): Madinah, Yanbu', Al-Ula, Badr (Badr Hunayn, node 1237968680; pilot alternative way 87175609 is a `village`-tagged way with the same population), Khaybar, Al-Hinakiyah, Mahd adh-Dhahab, Al-'Aīṣ.
- Wādī al-Fara': no seat named in any source reached (S-madinah-015, S-madinah-017). The row is the governorate's polygon centroid, flagged as not a settlement.

## 6. Checks run

- Build: `.venv/bin/python -m screening.sweeps.madinah.build --seed 1`, then `.venv/bin/python -m screening.sweeps.madinah.report --seed 1`.
- `screening.region_sweep validate --strict cities/ksa/regions/madinah.parquet`: ok (rows, governorate header, CSV mirror, OSM ids unique).
- Yanbu: the pilot's 331,916 = primary 258,777 (city) + 73,139 (Yanbu Industrial City, added here). Exactly equal, so the pilot's figure was the city plus its industrial city (pilot judgement item 5 resolved).
- Population rule: 9 primary official rows (plus the Yanbu Industrial City row) use the primary figure, with no corroboration needed; grid rows are gated; the OSM tag row is `derived` and unverified.
- Road minutes: every R1a row has an OSRM car skim; the Industrial City row has none.
- Terrain: not assessed (see section 2).

## 7. Unmatched GASTAT primary cities (region not stated; not in the register)

The primary 5,000+ city export has 68 city rows not matched as official populations in the R1a universe before this sweep; one of them (Yanbu Industrial City) is placed in this register, and one (Wādī al-'Uqūl farms) is discussed in section 4. The list below is the ≥ 10,000 remainder, excluding Wādī al-'Uqūl farms (section 4), with region not assigned (the 2010 administrative-region column matched by name is unreliable: one false hit, 'Alulya' to 'Al-Ula', was rejected). Any of these that is in Al-Madinah must be added once the city-to-governorate table is found.

| city (GASTAT EN) | total 2022 | note |
|---|---|---|
| Alhufuf | 430,105 | region not stated |
| Almubriz | 299,501 | region not stated |
| Jubail Industrial City | 172,233 | region not stated |
| Arqa | 42,179 | region not stated |
| Altaraf | 29,588 | region not stated |
| Aleumran | 22,781 | region not stated |
| Alqawz | 22,374 | region not stated |
| Alkalabiuh | 21,992 | region not stated |
| Almunayzilh | 21,346 | region not stated |
| Aljurn | 20,329 | region not stated |
| Alulya | 20,250 | region not stated |
| Thebea | 17,502 | region not stated |
| Albitaliuh | 15,146 | region not stated |
| Alhasma | 13,028 | region not stated |
| Iiskan Alkalabiuh | 12,817 | region not stated |
| Alhaliluh | 12,337 | region not stated |
| Aljushuh | 11,482 | region not stated |
| Benban | 10,793 | region not stated |

## 8. Needs judgement (not resolved by guessing)

1. Wadi Al Oqool farms (24,381, official): located point needed; schema needs lat/lon.
2. Unmatched GASTAT ≥ 10,000 cities (section 7): region membership. Blocks the completeness acceptance until resolved.
3. Terrain class: a DEM-based classification (Copernicus or SRTM) is needed for all rows; not run (no download under the disk gate).
4. Al Mohaffar (7,174, OSM tag dated 2010) is the only OSM-tag figure in the register; it is older than the census.
5. Sidi Hamzah (grid 30,876, 9 km from the Madinah centre) and Al 'Uyun (grid 11,547): grid figures in the Madinah metro area; the Medina city figure may already include them. Not netted; the grid is not corroborated.
6. Badr seat: node 1237968680 (Badr Hunayn) vs way 87175609 (`village`-tagged, same 2022 population). Choice recorded; check the seat in a GASTAT or governorate source.
7. Landbridge: committed layer in R1a. Whether its alignment runs through Madinah or Yanbu is unverified (pilot S-madinah-006); the register's committed distances use the R1a alignment and say so.
8. Governorate centre spelling: 'Al Is' (GASTAT primary; spelled Al-'Aīṣ in S-073 and the pilot).

## 9. Sources

Source ids are in `docs/sources/r2-madinah.csv` (S-madinah-) and in `docs/sources/index.csv` (S-cp2-, S-r1a-, S-cp1-, S-073, S-001). Key ones: S-cp2-gastat-008 (primary city 5,000+), S-cp2-gastat-007 (primary governorates), S-073 (governorate list), S-r1a-506 (WorldPop 2020 100 m, constrained UN-adjusted), S-r1a-202/204/205/208/214/221/227/237 and S-cp1-100/105 (economic nodes), S-madinah-005/008–015 (pilot sources), S-madinah-016 (OSM population tags, ODbL), S-madinah-017 (governorate summary; search result, not fetched).

Licences: OpenStreetMap ODbL (credit: © OpenStreetMap contributors), GASTAT data (credited; use policy https://www.stats.gov.sa/en/use-policy), WorldPop CC BY 4.0 (`worldpop-sau-2020-100m-unadj-constrained`).

