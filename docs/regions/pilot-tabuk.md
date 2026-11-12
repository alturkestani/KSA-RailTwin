> **Document version:** docs/regions/pilot-tabuk.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_TABUK) | Status: draft

# Tabuk pilot sweep (تبوك, slug `tabuk`)

**Screening input, not a forecast.** Coarse pilot sweep (the R2 full register is `REGION_TABUK`). It tests the schema on one region. Every population figure is a settlement figure from a secondary aggregator that credits GASTAT; every distance is a straight-line (haversine) figure; road minutes are pending R1a skims. Nothing here is calibrated.

Register: `cities/ksa/regions/pilot-tabuk.parquet` and `.csv` (9 rows, identical ids). Builder: `cities/ksa/regions/pilot-tabuk_build.py` (needs the `osmium` CLI and the GCC extract under `data/osm/`). Validation: every row passes `common.schemas.RegionRow`, and the file loads through `common.schemas.load_region_register`.

## 1. Governorate count: GASTAT vs listed (flagged, both sources)

| item | value | source |
|---|---|---|
| `governorates_gastat` | **unverified**: GASTAT's own governorate list was not reachable (portal.saudicensus.sa did not resolve on 2026-10-30) | S-072, S-090 |
| `governorates_listed` | **7 rows**: Al-Bad', Al-Wajh, Ḍubā', Ḥaql, Tabūk (the seat, as a governorate row), Taymā', 'Umluj | S-tabuk-001 (citypopulation admin table), S-tabuk-003 (Arabic Wikipedia), S-tabuk-004 (English Wikipedia: "six governorates, with Tabuk City serving as the seat") |
| alternative count | **6 governorates + the seat** (same six names; Tabuk municipality, Saudipedia and Arab Countries Guide wording) | search summaries; the municipality page returned 404 (S-tabuk-005) |
| possible 8th unit | **Hala Ammar (حالة عمار)**: a centre in the Tabuk municipality listing (search snippet) and a governorate in the Al-Ma'rifa list (search snippet, S-tabuk-021); no census population in the census place table | included as an unresolved row (`screened = false`) so that no unit is silently dropped |

The count of 7 uses the same convention as the citypopulation and Arabic Wikipedia tables (the seat is a governorate row). It is the working list, not a verified GASTAT figure. R2 must replace it with GASTAT's own list. Governorate populations (S-tabuk-001) sum to the region total of 886,036 (S-tabuk-016), which is the arithmetic check used.

## 2. Register rows

Columns follow `RegionRow`. `pop_type = secondary` is a new value added to `common/schemas.py` (see section 8). Tags: 10k and 5k follow A-screen-001/002; 50k is the sample tag. The sample column is `pilot_sample`.

| name (EN / AR) | governorate | centre | osm_id | lat, lon | population (year, type) | tag 10k / 5k / 50k | sample | dist existing km (nearest) | dist metro km (nearest, tier) | roles | terrain | screened |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tabuk / تبوك | Tabuk / تبوك | Y | 5418190413 | 28.40125, 36.56705 | 594,350 (2022, secondary, S-tabuk-002) | Y / Y / Y | N | 272.1 (unnamed OSM branch way w1180926881) | 0.0 (Tabuk, T2) | administrative (S-tabuk-004), airport (S-tabuk-013), heritage (S-tabuk-014) | mixed (assumed: A-screen-pilot-terrain-001) | Y |
| Umluj / أملج | Umluj / أملج | Y | 973472834 | 25.03028, 37.26223 | 46,229 (2022, secondary, S-tabuk-002) | Y / Y / N | Y | 250.6 (قطار الحرمين السريع (OSM w635445824)) | 245.2 (Madinah, T1) | none sourced | coastal (assumed: A-screen-pilot-terrain-001) | Y |
| Duba / ضباء | Duba / ضباء | Y | 1237957881 | 27.35208, 35.69207 | 39,543 (2022, secondary, S-tabuk-002) | Y / Y / N | Y | 413.9 (unnamed OSM branch way w1180926881) | 144.9 (Tabuk, T2) | port (S-tabuk-007) | coastal (assumed: A-screen-pilot-terrain-001) | Y |
| Al-Wajh / الوجه | Al-Wajh / الوجه | Y | 1237957986 | 26.24442, 36.45328 | 33,868 (2022, secondary, S-tabuk-002) | Y / Y / N | N | 381.1 (قطار الحرمين السريع (OSM w628772377)) | 240.1 (Tabuk, T2) | heritage (S-tabuk-012), airport (S-tabuk-011) | coastal (assumed: A-screen-pilot-terrain-001) | Y |
| Tayma / تيماء | Taymā' / تيماء | Y | 1237942492 | 27.62260, 38.53926 | 37,579 (2022, secondary, S-tabuk-002) | Y / Y / N | Y | 212.3 (قطار الشمال (OSM w499993382)) | 212.1 (Tabuk, T2) | heritage (S-tabuk-008) | mixed (assumed: A-screen-pilot-terrain-001) | Y |
| Haql / حقل | Haql / حقل | Y | 1236312441 | 29.28642, 34.94691 | 25,652 (2022, secondary, S-tabuk-002) | Y / Y / N | Y | 325.1 (قطار الشمال (OSM w856699578)) | 186.0 (Tabuk, T2) | border_crossing (S-tabuk-010) | coastal (assumed: A-screen-pilot-terrain-001) | Y |
| Al-Bad' / البدع | Al-Bad' / البدع | Y | 1237951657 | 28.48416, 35.01411 | 16,583 (2022, secondary, S-tabuk-002) | Y / Y / N | Y | 393.2 (قطار الشمال (OSM w1180926876)) | 152.1 (Tabuk, T2) | heritage (S-tabuk-009) | mixed (assumed: A-screen-pilot-terrain-001) | Y |
| Bi'r Ibn Hirmas / بئر ابن هرماس | Tabuk / تبوك | N | 1237958577 | 28.87000, 36.25774 | 4,964 (2022, secondary, S-tabuk-002) | N / N / N | N | 269.9 (unnamed OSM branch way w1180926881) | 60.2 (Tabuk, T2) | none sourced | mixed (assumed: A-screen-pilot-terrain-001) | N: below 5,000 (A-screen-002 sensitivity threshold) |
| Hala Ammar / حالة عمار | unresolved / غير محدد | N | 1237958860 | 29.16194, 36.07583 | null | N / N / N | N | 271.2 (قطار الشمال (OSM w96895732)) | 97.2 (Tabuk, T2) | none sourced | mixed (assumed: A-screen-pilot-terrain-001) | N: governorate unresolved (full text in `exclusion_reason`) |

Notes on individual rows (full text in the register `notes` column):
- **Tabuk**: governorate-level population 623,665 is not used for the row; the OSM `population` tag (512,629) is stale and unsourced, so it is not used either. The Hejaz station is 1.5 km from the row's point, on the historical line (section 4).
- **Umluj**: nearest metro is **Madinah (tier 1, 245 km)**, not Tabuk (381 km). Under A-screen-013 the rule is nearest by distance, so this is a schema edge (section 6). No airport in the governorate; the Al-Wajh domestic airport serves it (S-tabuk-011).
- **Al-Wajh**: not in the sample (the 5k–50k band is covered by Duba and Haql).
- **Bi'r Ibn Hirmas**: 4,964 (census) is below 5,000. The OSM tag (5,975) is not used. It is kept as the 5k-boundary check.
- **Hala Ammar**: no census population; the OSM tag (5,293) is not used.

## 3. Stratified sample of smaller towns (4–6 rows; 5 chosen)

All six census-listed places between 5,000 and 50,000 are governorate centres, so the sample is drawn from them. The band has no non-centre town, so the stratum is "governorate centres". Five were chosen.

| sample row | population | why it was chosen | stratum |
|---|---|---|---|
| Umluj | 46,229 | no sourced economic role; schema edge (nearest metro is Madinah, tier 1; governorate and town populations differ) | without a sourced role; schema edge |
| Duba | 39,543 | sourced port role (ferry to Egypt); far from existing rail (414 km) | far (>100 km); with a sourced role |
| Tayma | 37,579 | heritage role (UNESCO Tentative List); closest existing line of the six (SAR North line, 212 km) | far; heritage; closest line |
| Haql | 25,652 | border adjacency to Aqaba (sourced); far from existing rail (325 km) | far; border role |
| Al-Bad' | 16,583 | heritage role (Nabataean sites, sourced); far from existing rail (393 km); two population levels | far; heritage |

**Near (<25 km) stratum is empty.** No town in the 5k–50k band is within 25 km of an existing line. There is also no sourced committed line in the Tabuk region (section 4), so "near a committed line" cannot be tested either. Al-Wajh (33,868, heritage and airport) is registered but not sampled.

## 4. Rail layers and exclusions

| layer | what the pilot found | used as |
|---|---|---|
| `existing` | OSM `railway=rail` ways in service, excluding sidings, yards, spurs and crossovers. Named: **SAR North line (قطار الشمال)** and **Haramain HSR (قطار الحرمين السريع)**; several unnamed OSM branch ways | `nearest_existing`, `dist_existing_km` |
| `historical` | Hejaz Railway, OSM `abandoned` / `disused` (سكة حديد الحجاز القديمة). Tabuk station is restored as a museum (S-tabuk-014, S-tabuk-004). Passes within 2 km of Tabuk city and Bi'r Ibn Hirmas | recorded in notes; **not counted as existing** |
| `committed` | **None found for the Tabuk region.** The SAR North line's published passenger places do not include a Tabuk-region place (S-018: Riyadh, Majmaah, Qassim, Hail, Jouf, Qurayyat, Al Haditha). The Landbridge route is Riyadh–Jeddah (S-046 to S-057). | `nearest_committed` = null |
| announced, status unclear | NEOM rail: "The Spine" and "Neom Connector high-speed line", near Sharma and the northern Red Sea coast. A contractor update reports NEOM ended the Neom Connector contract (21 May 2026) and The Line is delayed past 2030 (S-tabuk-018). Both are snippet-only. OSM carries `construction` tags (NEOM Spine railway, Highland tunnel) | **not used**: the three-layer rule has no "announced" layer (Needs judgement, section 7) |

Excluded from the register and why:
- Census-listed places below 5,000 other than Bi'r Ibn Hirmas (Al-'Amūd 3,292; Al-Ḥaruh ash-Shamālīuh 2,543; Al-Mūīlaḥ 3,787; An-Naṣbuh 2,729; Mazāri' Shamāl Ṭarīq al-Madīnah 1 and 2: 4,458 and 2,603). Not registered in the pilot, as the schema-check sweep does not need them. R2 must register them, with OSM ids where OSM has them.
- Hala Ammar (no census population; governorate unresolved).
- 2023 social-media figures (S-tabuk-017) and a 753,730 figure (S-tabuk-019): conflicting, unverified, not used.

## 5. Distances

- **Method (A-screen-pilot-001):** great-circle (haversine) from the OSM node of the settlement to the nearest vertex of the nearest qualifying OSM rail way, after densifying each way to 0.5 km steps. The line is straight-line, so road distance is larger. Road minutes are null with `road_min_method = pending R1a skims`.
- **Metro (A-screen-013):** nearest of the 14 approved metro city nodes (pinned by OSM id). Tabuk is nearest for every row except Umluj (Madinah, 245 km vs Tabuk 381 km).
- Spot-check: Tayma to Tabuk by hand gives about 211 km; the computed value is 212.1 km.

## 6. Schema notes (common/schemas.py, additive)

The prompt's field names did not match `common/schemas.py`, and `screening/region_sweep` did not exist in this worktree. The register uses the schema's names (`dist_existing_km`, not `dist_km_existing`). To carry the pilot's acceptance fields, the following was added to `RegionRow` (existing rows still validate):
- `pop_type` now accepts `secondary` (the prompt's rule: a secondary aggregator is `secondary`, with `primary_to_find` filled);
- new optional fields with defaults: `primary_to_find`, `threshold_50k`, `pilot_sample`, `nearest_metro_tier`, `distance_method`, `road_min_method`, `terrain_source`, `notes`.

Schema edge cases recorded: Umluj's nearest metro is tier 1 (Madinah) while the region's secondary metro is Tabuk; governorate and town populations differ for all seven centres (ratio 1.05 to 1.51); Hala Ammar's governorate status is unresolved (the schema has no "unresolved" value, so it is `governorate = unresolved`).

## 7. Needs judgement

1. **Governorate count.** GASTAT's own list is unverified (S-072). The listed count is 7 (incl. the seat); the wording count is 6 (+ seat); Hala Ammar may make 8. Confirm before R2 and set `governorates_gastat` from GASTAT's table.
2. **Hala Ammar.** Governorate or centre? It has no census population in S-tabuk-002. Its row is kept (unresolved, screened false).
3. **NEOM rail layer.** "The Spine" and the Neom Connector are announced; one source reports the Neom Connector contract was ended (S-tabuk-018, snippet). The three-layer rule (`existing`, `committed`, `hypothetical`) has no place for an announced, unprocured line. Decide whether it is `committed` (only with procurement evidence) or left out of the layers until sourced.
4. **Historic Hejaz line.** The Layer literal has `historical`, but `RegionRow` carries no historic-line field. This pilot records it in notes only.
5. **Terrain classes are assumed** (A-screen-pilot-terrain-001). R1a should derive them from Copernicus DEM or SRTM (not read here: no tile was downloaded).
6. **Population level** (A-screen-pilot-002): settlement, not governorate. This decides whether Umluj clears 50k (on the town figure it does not).
7. **Metro rule for Umluj.** Nearest by distance gives Madinah (tier 1). Confirm whether Tabuk's tier should cover Umluj in the 30-minute test.
8. **Sample near stratum** is empty for this region (section 3).
9. **OSM share-alike.** Publication of a derived extract under ODbL (docs/licences-pilot-tabuk.md).

## 8. Sources

Full list with status: `docs/sources/pilot-tabuk.csv` (S-tabuk-001 to 020). Existing project sources cited: S-018 (SAR North line places), S-046 to S-057 (Landbridge, background), S-071 and S-072 and S-090 (GASTAT census date and the unreachable portal), S-073 (citypopulation 150-row list, secondary), and the manifest row `osm-gcc-2026-10-14` (ODbL, `cities/ksa/sources.yaml`).

Summary of status (21 rows): primary 2 (S-tabuk-006 OSM; S-tabuk-008 UNESCO, snippet only); secondary 13; unverified 6 (S-tabuk-005 returned 404; S-tabuk-017 and S-tabuk-019 conflicting numbers, not used; S-tabuk-018, S-tabuk-020 and S-tabuk-021 snippet-only claims, not used for register values). GASTAT primary figures: **none** (portal unreachable).

## 9. Conflicts

- C-tabuk-001: 2023 social post (S-tabuk-017) gives Tabuk city 448,000 and the governorate 624 thousand; the census table gives 594,350 and 623,665. Not used.
- C-tabuk-002: Hejaz station construction date: 1906, 1908 or 1909 across sources (S-tabuk-014). Not used for any register value.
- C-tabuk-003: OSM `population` tags differ from the census for every centre (e.g. Umluj 37,757; Duba 25,568; Tayma 30,411). Not used.
- C-tabuk-004: Tabuk city population 753,730 (S-tabuk-019) vs 594,350 (census). Not used.

Label for every figure in this file: **screening input, not a forecast.**
