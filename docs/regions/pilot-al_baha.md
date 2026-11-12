> **Document version:** docs/regions/pilot-al_baha.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_AL_BAHA) | Status: draft

# Al-Baha (الباحة) pilot sweep, slug `al_baha`

**Screening input, not a forecast.** Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. This is the coarse pilot sweep that tests the register schema; the full Al-Baha register is `REGION_AL_BAHA` in R2. Access date for every source: 30 Oct 2026 (Asia/Riyadh). Source ids are in `docs/sources/pilot-al_baha.csv` (`S-al_baha-nnn`) and in the Kingdom index (`S-070`, `S-072`, `S-090`).

## Governorate count

| source | count | status |
|---|---|---|
| citypopulation.de, Al-Bahah region table (credits GASTAT, census 2022-05-10): 9 governorates plus the Al-Bāḥah row | 10 rows | secondary (`S-al_baha-001`) |
| Wikipedia, Al-Bahah Province: 9 governorates listed, plus Al-Baha city as provincial capital | 9 (+ capital) | secondary (`S-al_baha-005`) |
| Saudipedia (search snippet, `docs/gastat-regions.md`): 9 governorates, plus the emirate | 9 (+ capital) | secondary (`S-073`/`S-076` family) |
| GASTAT official governorate list | **not reachable**: portal.saudicensus.sa did not resolve (`S-090`); governorate count unverified (`S-072`) | unverified |

`governorates_gastat: unknown` · `governorates_listed: 10` (rows; 9 governorates plus the Al-Bāḥah row, which is the regional capital). **Flagged, not resolved:** the listed count and the GASTAT count are both unverified. The register has one row per governorate centre, which is 10 rows: the 9 governorates and the Al-Bāḥah row. Read the GASTAT list before R2 (see Needs judgement).

## Register rows (10)

Generated from `cities/ksa/regions/pilot-al_baha.parquet` (the CSV carries the same rows and ids). Populations are **secondary** (citypopulation.de, credits GASTAT); every value is a settlement (place) figure, not a governorate total. Distances are great-circle, method `A-screen-pilot-001`. Road minutes are empty (`pending R1a skims`).

| row | centre (EN / AR) | governorate (EN) | OSM id | lat, lon | population | tags | dist existing km (nearest) | dist metro km (nearest, tier) | economic roles | pilot sample | screened |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AB-01 | Al-Bāḥah / الباحة | Al-Bāḥah | 295921642 | 20.01379, 41.46564 | 90,515 (S-al_baha-002, secondary, 2022) | 10k, 5k, 50k | 234.1 (Makkah Central) | 177.3 (Taif, tier 2) | administrative (S-al_baha-001) | no | yes |
| AB-02 | Al-'Aqīq / العقيق | Al-'Aqīq | 6767957154 | 20.28364, 41.65601 | 19,269 (S-al_baha-002, secondary, 2022) | 10k, 5k | 231.4 (Makkah Central) | 169.3 (Taif, tier 2) | administrative (S-al_baha-001), airport (S-al_baha-010) | yes | yes |
| AB-03 | Al-Ḥajrah / الحجرة | Al-Ḥajrah | 1236690663 | 20.19970, 41.07207 | null (no place figure) | – | 190.1 (Makkah Central) | 137.2 (Taif, tier 2) | administrative (S-al_baha-001) | no | yes |
| AB-04 | Al-Makhwāh / المخواة | Al-Makhwāh | 1236690590 | 19.77944, 41.43556 | 26,248 (S-al_baha-002, secondary, 2022) | 10k, 5k | 250.1 (Makkah Central) | 196.9 (Taif, tier 2) | administrative (S-al_baha-001) | yes | yes |
| AB-05 | Al-Mandaq / المندق | Al-Mandaq | 1237964146 | 20.11051, 41.28285 | 8,674 (S-al_baha-002, secondary, 2022) | 5k | 212.8 (Makkah Central) | 157.4 (Taif, tier 2) | administrative (S-al_baha-001) | yes | yes |
| AB-06 | Al-Qarā / القرى | Al-Qarā | – | NaN, NaN (not located) | null (no place figure) | – | – | – | administrative (S-al_baha-001) | no | no: centre not located |
| AB-07 | Baljurashī / بلجرشي | Baljurashī | – | 19.86121, 41.56098 | 35,985 (S-al_baha-003, secondary, 2022) | 10k, 5k | 252.9 (Makkah Central) | 196.9 (Taif, tier 2) | administrative (S-al_baha-001) | yes | yes |
| AB-08 | Banī Ḥasan / بني حسن | Banī Ḥasan | 3734863966 | 20.05350, 41.37367 | 6,344 (S-al_baha-002, secondary, 2022) | 5k | 224.0 (Makkah Central) | 168.0 (Taif, tier 2) | administrative (S-al_baha-001) | yes | yes |
| AB-09 | Ghāmid az-Zinād / غامد الزناد | Far'at Ghāmid az-Zinād | 6770793665 | 19.59444, 41.52011 | null (no place figure) | – | 271.3 (Makkah Central) | 184.9 (Abha, tier 2) | administrative (S-al_baha-001) | no | yes |
| AB-10 | Qilwah / قلوة | Qilwah | 8506335688 | 19.94011, 41.25130 | 13,069 (S-al_baha-002, secondary, 2022) | 10k, 5k | 223.9 (Makkah Central) | 171.6 (Taif, tier 2) | administrative (S-al_baha-001) | yes | yes |

Committed lines (Landbridge, GCC, Riyadh Rail Link): `dist_committed_km` is empty for every row. No station coordinates for the committed lines are in the sources (for example Al-Jumum is unlocated, `S-062`/`S-063`), so the distance is not guessed. None of the three is labelled existing.

Existing rail: the only existing stations used are the Haramain HSR stations Makkah Central (OSM node 10956967098, 21.41766 N, 39.78853 E) and Jeddah Al-Sulaymaniyah (OSM way 485762503). Makkah Central is nearer in every row, so the table uses it. Al-Baha has no existing line in the sources. Distances are to the station, not the alignment; the alignment could be closer, so these are station-based values.

Metro (A-screen-013, approved tiers): the nearest metro for every row is Taif or Abha (secondary tier). Makkah (primary) is 232 km or more from every row, so it is never nearest here. Makkah distance is taken to the Haramain station as a proxy: no Makkah city coordinate is sourced.

Terrain: `escarpment_mountain` for all rows, from the Sarawat Mountains range (`S-al_baha-009`). This is a region-level class, not a DEM result. The DEM was not sampled (pilot, no downloads). The word "escarpment" is not on the Wikipedia page and the UNESCO tentative-list page returned 403, so the wording is unverified; see the assumption register.

## Pilot sample (6 rows, `pilot_sample: true`)

The brief asks for 4–6 towns between 5,000 and 50,000 across near and far, with and without a sourced role. In Al-Baha no sampled town is near (< 25 km) to a line: all six are between 213 and 253 km from Makkah Central. The "near" stratum is empty and is recorded as empty, not filled.

- **Al-'Aqīq** (AB-02): With economic role (airport). Far from existing rail (231 km).
- **Al-Makhwāh** (AB-04): Without sourced role. Far from rail (250 km). Mid band (26,248).
- **Al-Mandaq** (AB-05): Without sourced role. Lower band (8,674). Far from rail (213 km).
- **Baljurashī** (AB-07): Unmapped OSM place (no place node). Governorate total 51,787 vs town 35,985 tests the settlement-vs-governorate rule. Far from rail (253 km).
- **Banī Ḥasan** (AB-08): Centre conflict (OSM town vs Saudipedia). Smallest sampled town (6,344). Without sourced role. Far from rail (224 km).
- **Qilwah** (AB-10): Two OSM candidates for the centre (town vs governorate node). Without sourced role. Far from rail (224 km).

Sample edge cases tested: an OSM place missing (Baljurashī, no place node), a governorate seat tagged `place=village` (Al-Ḥajrah, not sampled but listed), and two conflicting centre candidates (Qilwah, Banī Ḥasan). A governorate centre smaller than a non-centre town could not be tested: no non-centre town in Al-Baha has a sourced population in these sources.

## Exclusions (rule 2: every governorate is in the register)

- **Al-Qarā** (row AB-06): `screened: false`. The centre is not located: no OSM place node was found and no coordinate source exists. Its governorate total is 19,586 (`S-al_baha-001`); that total is not used as a centre population. The row stays so that every governorate has a row. It fails the schema because coordinates are required (see the report).
- No other row is excluded. Rows without a town population (Al-Ḥajrah, Ghāmid az-Zinād) stay screened with `population: null`.

## Economic roles (sourced only)

- Administrative (governorate seat): all 10 rows, `S-al_baha-001` (citypopulation governorate table).
- Airport: Al-Aqiq (row AB-02), King Saud Domestic Airport, domestic only, "located in Al-Aqiq" (`S-al_baha-010`, Wikipedia). No distance from the town to the airport was sourced.
- Region-level, not attached to a town: summer tourism and honey (about 1,000 t, about 20 % of Kingdom production, no year, AJEL 27 Jul 2025, `S-al_baha-011`). Pomegranate and "over 8,000 tons" figures from a search snippet are not verified and are not used. Heritage villages (Dhee Ain and others) come from a travel guide (weak) and are not used.
- University: no sourced campus in Baljurashī, Al-Makhwāh, Qilwah, Al-Aqiq or Banī Ḥasan. Al-Baha University's Wikipedia page returned 404. Left empty.
- Giga-project, Hajj/Umrah, mining, port, border crossing, military, industrial city: none found for Al-Baha in the sources read.

## Needs judgement

1. **Schema (`common/schemas.py`, not editable by this track; additive-only rule).** `RegionRow` rejects `pop_type: secondary` (10 populated rows), so validation passes only with `secondary` mapped to `official`, which is a validation-only substitute and is not written to the file. `RegionRow` has no `threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `road_min_method`, `notes` or `primary_to_find`, and it forbids extras, so those are extra Parquet columns. The brief's `dist_km_existing` naming is the schema's `dist_existing_km`; the schema name is used. The brief's `coastal_plain` is `coastal` in the schema; not needed for Al-Baha.
2. **Al-Qarā coordinates.** `lat`/`lon` are required by `RegionRow`. Options: locate the centre (GASTAT or OSM), or make coordinates optional for `screened: false` rows.
3. **Governorate count.** 10 rows (citypopulation) versus 9 (Wikipedia and Saudipedia). GASTAT's list is unreachable. Decide whether the Al-Bāḥah row is a governorate or the regional capital, after the GASTAT list is read.
4. **Baljurashī, 50k rule.** Governorate total 51,787 (≥ 50k) but town 35,985 (< 50k). The threshold is applied to settlements, so `threshold_50k` is false. Confirm.
5. **Banī Ḥasan and Qilwah centres.** Banī Ḥasan: OSM town vs Saudipedia's Bidan / Wadi Al-Sadr. Qilwah: town node 8506335688 vs governorate node 6768458212 (20.0000 N, 41.0833 E). Both kept as conflicts.
6. **Al-Ḥajrah centre tagged `place=village`** in OSM, while being a governorate seat. Kept as-is; the tag is OSM's. Population unsourced.
7. **Committed-line distances.** Not computed: no sourced station coordinates. Needed for the R1a line layer.
8. **Terrain.** Region-level class; per-town class needs the DEM (R1a).

## Notes per row

- **AB-01 Al-Bāḥah:** Region capital and governorate seat. Population 90,515 is the citypopulation place row (same figure as the governorate row). Only pilot town at or above 50k (threshold_50k). OSM node is place=city. Roles limited to administrative; region-level tourism and honey claims (S-al_baha-011) are in docs/regions/pilot-al_baha.md, not attached to this town.
- **AB-02 Al-'Aqīq:** Governorate centre (town). King Saud Domestic Airport (IATA ABT) is described as located in Al-Aqiq, domestic flights only (Wikipedia, S-al_baha-010). The airport role is the only sourced role in the pilot sample; no distance from the town to the airport was sourced.
- **AB-03 Al-Ḥajrah:** Governorate seat is OSM place=village (node 1236690663), smaller than several non-centre towns elsewhere; the schema edge case the brief asks for. No place-level census figure sourced: the governorate row (12,136, S-al_baha-001) is the governorate total and is not used as the centre population. Population null, so no tag.
- **AB-04 Al-Makhwāh:** Governorate centre (town, OSM place=town). Governorate total 48,333 (S-al_baha-001) is below 50k; the town figure 26,248 is the place row. Sample: far from rail, no sourced role.
- **AB-05 Al-Mandaq:** Governorate centre (town). Place row 8,674 (S-al_baha-002); governorate total 20,010. Tag_5k only. Sample: lower band, no sourced role, far from rail (213 km).
- **AB-06 Al-Qarā:** Row kept so that every governorate has a row (rule 2). lat/lon left as NaN because no sourced coordinate exists; RegionRow requires coordinates, so this row fails validation until the centre is located. The Wikipedia 'Al-Qura' article describes a different governorate (29.9 N, 40.2 E) and was discarded.
- **AB-07 Baljurashī:** Governorate centre (town). Unmapped OSM place: no place=* node found by Nominatim (only the governorate boundary relation 12429798), so osm_id null. Coordinates from Wikipedia (secondary). Governorate total 51,787 is at or above 50k but the town (35,985) is below 50k: the threshold applies to settlements, so threshold_50k is false (Needs judgement).
- **AB-08 Banī Ḥasan:** Governorate centre conflict: OSM town node 'Bani Hasan' versus Saudipedia, which lists Bidan (Category A) and Wadi Al-Sadr (Category B) as centres (S-al_baha-012). Place row 6,344 (S-al_baha-002) vs governorate total 15,496 (S-al_baha-001 and S-al_baha-012 agree). Wikipedia's 35,082 for this governorate disagrees with both and is not used.
- **AB-09 Ghāmid az-Zinād:** Governorate centre (town, OSM place=town). No place-level census figure sourced: the governorate total 12,506 (S-al_baha-001) is not the centre population. Population null, so no tag. Nearest metro is Abha, not Taif.
- **AB-10 Qilwah:** Governorate centre (town, OSM node 8506335688). A second OSM node, 6768458212, is tagged place=governorate at 20.0000 N, 41.0833 E; kept as a conflict, the town node is used. Governorate total 31,197 (S-al_baha-001) vs town 13,069 (S-al_baha-002).

## Sources

Full rows in `docs/sources/pilot-al_baha.csv`. Summary:

- `S-al_baha-001` citypopulation.de, Al-Bahah region admin table (census 2022-05-10, region total 339,174): https://www.citypopulation.de/en/saudiarabia/admin/ (secondary; credits GASTAT)
- `S-al_baha-002` citypopulation.de, Al-Bahah region place table: https://citypopulation.de/en/saudiarabia/bahah/ (secondary; credits GASTAT)
- `S-al_baha-003` citypopulation.de, Baljurashī place page: https://citypopulation.de/en/saudiarabia/bahah/baljurashī/12002__baljurashī/ (secondary)
- `S-al_baha-004` Wikipedia, Baljurashi (coordinates only): https://en.wikipedia.org/wiki/Baljurashi (secondary)
- `S-al_baha-005` Wikipedia, Al-Bahah Province (governorate list; no named source): https://en.wikipedia.org/wiki/Al-Bahah_Province (secondary)
- `S-al_baha-006` OpenStreetMap place nodes via Nominatim (ODbL): https://nominatim.openstreetmap.org/ (verified; IDs and coordinates)
- `S-al_baha-007` OpenStreetMap Haramain station nodes (ODbL): verified
- `S-al_baha-008` Wikipedia, Haramain high-speed railway (opened 11 Oct 2018): https://en.wikipedia.org/wiki/Haramain_high-speed_railway (secondary)
- `S-al_baha-009` Wikipedia, Sarawat Mountains: https://en.wikipedia.org/wiki/Sarawat_Mountains (secondary)
- `S-al_baha-010` Wikipedia, Al-Aqiq (airport location): https://en.wikipedia.org/wiki/Al-Aqiq (secondary)
- `S-al_baha-011` AJEL, honey article (27 Jul 2025): https://english.ajel.sa/lifestyle/al-baha-honey-blending-culinary-tradition-with-economic-and-tourism-growth (secondary; region-level)
- `S-al_baha-012` Saudipedia, Bni Hasan governorate: https://saudipedia.com/en/bni-hasan-governorate (secondary)
- Kingdom index: `S-070` (13 regions, verified); `S-072` (governorate count, unverified); `S-090` (GASTAT portal, unreachable).

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast. Screening input, not a forecast.
