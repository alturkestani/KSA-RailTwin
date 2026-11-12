> **Document version:** docs/regions/pilot-riyadh.md v1.1 | 31 Oct 2026 | Author: region-scout (PILOT_REGION_RIYADH) | Status: draft

# Riyadh pilot sweep (الرياض): coarse screening input

Synthetic demand, uncalibrated: scenario comparison, not a forecast. This is a screening input, not a forecast. It tests the register schema; the full Riyadh register is `REGION_RIYADH` (R2).

Register: `cities/ksa/regions/pilot-riyadh.parquet` (same rows in `pilot-riyadh.csv`). Build: `PYTHONPATH=. uv run python cities/ksa/regions/build_pilot_riyadh.py`. Sources: `docs/sources/pilot-riyadh.csv` (S-riyadh-001 to 015) plus existing S-nnn in `docs/sources/index.csv`. Assumptions: `docs/assumptions-pilot-riyadh.md`.

## Governorate count

- `governorates_gastat: 23`. This value comes from the citypopulation.de admin list, which credits GASTAT (S-riyadh-001; the same 23 names appear in S-073). **GASTAT's own table was not read:** `portal.saudicensus.sa` did not resolve on 30 Oct 2026 (S-090). The count is therefore unverified against the primary.
- `governorates_listed: 23`. Every governorate has one centre row (23 rows). Their populations sum to 8,591,748, the regional total on S-riyadh-001.
- **Discrepancy flagged:** the English Wikipedia count for the region is 22 (S-074 per-region table in `docs/gastat-regions.md`), and the Arabic Wikipedia list gives 23. The difference is whether the regional capital (Ar-Riyadh) is counted as a governorate. This pilot counts it, as S-073 does.

## Rows

25 rows: 23 governorate centres plus 2 non-centre sample towns (Al-Uyaynah and Al-Jubaylah, both in Ad-Dir'iyah). `screened = no` for 14 rows, each with its reason in `exclusion_reason`. Distances are haversine from the proxies in `docs/assumptions.md` (A-screen-pilot-001, -003, -004 [riyadh]; the track fragment was deleted at CP2_PREP). Road minutes are empty (`road_min_method: pending R1a skims`). The `dist Landbridge` column is the planned Riyadh–Jeddah line (announced/planned, not existing). `dist existing` is measured to SAR's passenger place proxies (North: Riyadh, Al-Majma'ah).

| name (EN) | name (AR) | governorate | centre | population (Census 2022) | source | tags 5k / 10k / 50k | dist existing km | dist Landbridge km | dist Riyadh metro km | screened | pilot sample | economic roles (source) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Riyadh | الرياض | Ar-Riyadh | yes | 6,924,566 | S-080 | Y / Y / Y | 0.0 | 236.4 | 0.0 | yes |  |  |
| Ad-Dawadmi | الدوادمي | Ad-Dawadmi | yes | 86,861 | S-riyadh-009 | Y / Y / Y | 184.2 | 0.0 | 236.4 | yes |  |  |
| Ad-Dilam | الدلم | Ad-Dilam | yes |  |  | N / N / N | 84.6 | 287.4 | 84.6 | no |  |  |
| Ad-Dir'iyah | الدرعية | Ad-Dir'iyah | yes | 61,609 | S-riyadh-003 | Y / Y / Y | 19.0 | 223.0 | 19.0 | yes |  | heritage (S-riyadh-012); giga_project (S-riyadh-013) |
| 'Afif | عفيف | 'Afif | yes | 47,340 | S-riyadh-005 | Y / Y / N | 331.1 | 162.8 | 393.9 | yes | yes |  |
| Layla | ليلى | Al-Aflaj | yes |  |  | N / N / N | 260.9 | 341.5 | 260.9 | no |  |  |
| Al-Ghat | الغاط | Al-Ghat | yes |  |  | N / N / N | 41.8 | 179.9 | 235.3 | no |  | university (S-riyadh-011) |
| Al-Hariq | الحريق | Al-Hariq | yes |  |  | N / N / N | 113.7 | 236.5 | 113.7 | no |  |  |
| Al-Kharj | الخرج | Al-Kharj | yes | 295,462 | S-riyadh-007 | Y / Y / Y | 133.1 | 342.9 | 133.1 | yes |  | military (S-riyadh-014) |
| Al-Majma'ah | المجمعة | Al-Majma'ah | yes | 70,243 | S-riyadh-008 | Y / Y / Y | 0.0 | 184.2 | 196.9 | yes |  | university (S-riyadh-011) |
| Al-Muzahimiyah | المزاحمية | Al-Muzahimiyah | yes | 55,604 | S-riyadh-004 | Y / Y / Y | 48.7 | 191.0 | 48.7 | yes |  |  |
| Al-Quwayiyah | القويعية | Al-Quwayiyah | yes |  |  | N / N / N | 158.4 | 103.0 | 158.4 | no |  |  |
| Ar-Rayn | الرين | Ar-Rayn | yes |  |  | N / N / N | 172.9 | 156.1 | 172.9 | no |  |  |
| As-Sulayyil | السليل | As-Sulayyil | yes |  |  | N / N / N | 479.3 | 465.0 | 479.3 | no |  |  |
| Az-Zulfi | الزلفي | Az-Zulfi | yes | 68,317 | S-riyadh-009 | Y / Y / Y | 68.9 | 205.4 | 265.5 | yes |  | university (S-riyadh-011) |
| Durma | ضرما | Durma | yes |  |  | N / N / N | 59.1 | 177.4 | 59.1 | no |  |  |
| Hawtat Bani Tamim | حوطة بني تميم | Hawtat Bani Tamim | yes |  |  | N / N / N | 129.1 | 277.1 | 129.1 | no |  |  |
| Huraymila | حريملاء | Huraymila | yes |  |  | N / N / N | 80.8 | 189.1 | 80.8 | no |  |  |
| Marat | مرات | Marat | yes |  |  | N / N / N | 93.2 | 126.0 | 135.8 | no |  |  |
| Rimah | رماح | Rimah | yes | 25,031 | S-riyadh-006 | Y / Y / N | 112.6 | 303.9 | 112.6 | yes | yes | university (S-riyadh-011) |
| Shaqra | شقراء | Shaqra | yes |  |  | N / N / N | 73.5 | 121.3 | 162.3 | no |  |  |
| Thadiq | ثادق | Thadiq | yes |  |  | N / N / N | 86.5 | 173.0 | 111.8 | no |  |  |
| Wadi ad-Dawasir | وادي الدواسر | Wadi ad-Dawasir | yes |  |  | N / N / N | 504.6 | 450.6 | 504.6 | no |  |  |
| Al-Uyaynah | العيينة | Ad-Dir'iyah | no | 8,649 | S-riyadh-003 | Y / N / N | 44.2 | 207.9 | 44.2 | yes | yes |  |
| Al-Jubaylah | الجبيلة | Ad-Dir'iyah | no | 8,005 | S-riyadh-003 | Y / N / N | 41.0 | 213.4 | 41.0 | yes | yes |  |

Layers: existing = SAR North passenger (S-018); committed/planned = Landbridge Riyadh–Jeddah, intermediate Dawadimi (S-062, announced); metro = Riyadh Metro, in operation since Dec 2024 (S-037, secondary). The Riyadh Rail Link (35 km, committed, S-060) has no station coordinates in any source, so no distance is computed for it.

## Towns at or above 50,000 (`threshold_50k`)

Seven rows, all governorate centres: Riyadh (6,924,566), Al-Kharj (295,462), Al-Majma'ah (70,243), Az-Zulfi (68,317), Ad-Dawadmi (86,861), Ad-Dir'iyah (61,609), Al-Muzahimiyah (55,604). **All seven populations are secondary** (citypopulation.de crediting GASTAT, or Wikipedia); none is a GASTAT primary. The Riyadh figure is S-080 and conflicts with Wikipedia's 7,000,100. The Al-Kharj and Az-Zulfi coordinates are governorate-centroid proxies, so their distances are approximate.

No non-centre town in the region was found at or above 50,000 in the sources read. Wadi ad-Dawasir's governorate total is 91,535, but the centre town figure is unresolved (see below).

## Stratified pilot sample (4 rows, `pilot_sample = true`)

| row | population | why it was sampled |
|---|---|---|
| Rimah (رماح) | 25,031 | far (about 113 km from the Riyadh proxy, about 180 km from Al-Majma'ah); **with** a sourced role (Majmaah University branch campus, S-riyadh-011); a governorate centre. |
| 'Afif (عفيف) | 47,340 | far (about 331 km from the Riyadh proxy); **without** a sourced role; **schema edge**: no OSM place node found, so `osm_id` is null and the coordinate is a boundary-centroid proxy (A-screen-pilot-003). |
| Al-Uyaynah (العيينة) | 8,649 | mid-distance (about 44 km); **without** a sourced role; non-centre town in Ad-Dir'iyah (tests the sub-governorate tier and `tag_5k` without `tag_10k`). |
| Al-Jubaylah (الجبيلة) | 8,005 | mid-distance (about 41 km); **without** a sourced role; non-centre town (same governorate as Al-Uyaynah; `tag_5k` only). |

**Gap:** no "near" (under 25 km) sample. The only town within 25 km of a proxy station is Ad-Dir'iyah (19 km), which is above 50,000. A near-rail small town can only be tested once station geometry is available (R1a). This is recorded, not hidden.

## Exclusions and unscreened rows (`screened = false`)

14 of the 23 centres have no sourced centre-town population. The governorate total exists, but the centre figure does not. Each row carries its reason:

- **Population not sourced (13 rows):** Ad-Dilam, Layla (Al-Aflaj), Al-Ghat, Al-Hariq, Al-Quwayiyah, Ar-Rayn, As-Sulayyil, Durma, Hawtat Bani Tamim, Huraymila, Marat, Shaqra, Thadiq. Governorate totals are in `notes`. R2 takes the centre figure from the GASTAT table.
- **Wadi ad-Dawasir (1 row):** centre population unresolved (needs judgement; see below).

Nothing was excluded for being below a threshold: every town with a sourced population is kept, and no town below 5,000 is in the register.

## Coverage against the 23 governorates

| governorate | centre row | status |
|---|---|---|
| Ad-Dawadmi | Ad-Dawadmi | screened (86,861) |
| Ad-Dilam | Ad-Dilam | not screened (no centre pop; centroid coordinate) |
| Ad-Dir'iyah | Ad-Dir'iyah | screened (61,609) |
| 'Afif | 'Afif | screened, pilot sample (47,340; unmapped OSM place) |
| Al-Aflaj | Layla (OSM place; identity unverified) | not screened |
| Al-Ghat | Al-Ghat | not screened |
| Al-Hariq | Al-Hariq | not screened |
| Al-Kharj | Al-Kharj | screened (295,462; centroid coordinate) |
| Al-Majma'ah | Al-Majma'ah | screened (70,243) |
| Al-Muzahimiyah | Al-Muzahimiyah | screened (55,604) |
| Al-Quwayiyah | Al-Quwayiyah | not screened |
| Ar-Rayn | Ar-Rayn | not screened |
| Ar-Riyadh | Riyadh | screened (6,924,566) |
| As-Sulayyil | As-Sulayyil | not screened |
| Az-Zulfi | Az-Zulfi | screened (68,317; centroid coordinate) |
| Durma | Durma | not screened |
| Hawtat Bani Tamim | Hawtat Bani Tamim | not screened |
| Huraymila | Huraymila | not screened |
| Marat | Marat | not screened |
| Rimah | Rimah | screened, pilot sample (25,031) |
| Shaqra | Shaqra | not screened |
| Thadiq | Thadiq | not screened |
| Wadi ad-Dawasir | Wadi ad-Dawasir | not screened (centre unresolved) |

## Needs judgement

1. **Wadi ad-Dawasir centre population.** The 91,535 total is a governorate figure; no town-level value was found. Keep unscreened until a primary figure exists.
2. **Al-Aflaj centre identity.** The OSM place node is "Layla", inside the Al Aflaj governorate. Confirm the GASTAT centre and its Arabic name; the Arabic name ليلى is not sourced.
3. **Al-Kharj and Az-Zulfi coordinates.** Only the governorate boundary centroid was found. Taking the town node would move the distances by tens of kilometres.
4. **Riyadh population.** S-080 (6,924,566, citypopulation city-proper) conflicts with the 7,000,100 in Wikipedia (S-riyadh-009) and the 7,009,120 governorate total (S-riyadh-001). The register uses S-080 as the index does.
5. **Hotat Sudair** (a Majmaah University branch per S-riyadh-011) is not mapped to Hawtat Bani Tamim: the naming match is unconfirmed.
6. **Terrain.** Only Riyadh has a sourced class (escarpment, S-riyadh-015). The default flat_desert is assumed (A-screen-pilot-002) and needs the DEM check in R1a.

## Sources

Governorate list: S-073 (secondary); S-072 and S-090 (GASTAT, unverified). Populations: S-080 (existing); S-riyadh-001 to 009 (citypopulation.de crediting GASTAT, Wikipedia). Coordinates: S-riyadh-010 (OSM via Nominatim, ODbL). Rail proxies: S-018 and S-025 (SAR, verified place lists); S-062 (Landbridge intermediate, secondary); S-037 (Riyadh Metro, secondary); S-060 (Riyadh Rail Link, secondary). Economic roles: S-riyadh-011 (Majmaah University), S-riyadh-012 (UNESCO At-Turaif), S-riyadh-013 (PIF Diriyah Company), S-riyadh-014 (Prince Sultan Air Base). Terrain: S-riyadh-015 (Tuwaiq, secondary).

Checked against a primary source: the SAR place lists (S-018, S-025) and the Riyadh Metro project station count (S-034, RCRC). Everything else is secondary or unverified, as the status column in `docs/sources/pilot-riyadh.csv` says.
