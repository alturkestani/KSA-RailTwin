> **Document version:** docs/regions/pilot-jazan.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, track pilot-jazan) | Status: draft

# Jazan (جازان) pilot sweep: coarse register

**Label: screening input, not a forecast.** This is the pilot (`PILOT_REGION_JAZAN`) of the region-sweep schema. It is not the full Jazan register (`REGION_JAZAN` in R2). Accessed 30 Oct 2026 (Asia/Riyadh). Source ids: `docs/sources/pilot-jazan.csv` (S-jazan-nnn) and the global index `docs/sources/index.csv`.

## 1. Governorate count

| source | count | status |
|---|---|---|
| GASTAT official list | **not read**: portal.saudicensus.sa did not connect on 30 Oct 2026 (S-jazan-015, S-090) | unverified |
| citypopulation.de, Census 2022 administrative list (S-jazan-001; global S-073) | **17** | secondary |
| Saudipedia, Jazan Emirate (S-jazan-003) | 16 (3 class A: Sabya, Abu Arish, Samtah; 13 class B; about 41 centres) | secondary |

Header key: `governorates_gastat: unverified` (Parquet metadata); `governorates_listed: 17`. **The discrepancy (16 vs 17) is flagged, not resolved.** The register carries 17 governorate rows, one per governorate of the citypopulation list, each with its centre. citypopulation marks Aṭ-Ṭuwāl, Fayfā and Harūb with a previous parent governorate (Ṣāmiṭah, Jīzān, Al-'Aydābī), so a newer-governorate effect is one possible reason for 16 vs 17. That is a hypothesis, not checked. Acceptance: 17 governorates listed; GASTAT count to be confirmed (Needs judgement 1).

## 2. What the register holds

- **20 rows:** 17 governorate centres (every governorate has at least one row) and 3 non-centre sample towns.
- **Towns ≥ 50,000 (Census 2022, secondary):** Jizan 173,919; Sabya 72,086; Abu Arish 69,632. Tagged `threshold_50k`.
- **Population missing (null, not guessed):** Al Harth, Ar Rayth, Harub, Fayfa. Their centres do not appear in the citypopulation places table (places of at least 2,500). Governorate-level totals exist, but a centre figure would be a guess.
- **Rail, by layer:**
  - *Existing:* the only existing line near Jazan is the Haramain HSR. Its nearest station to the region is Makkah (OSM node 10956967098, S-jazan-008), about 480–640 km from every row. No existing line or station lies in Jazan.
  - *Committed / under procurement:* no Jazan line or station is in any source. `dist_committed_km` is therefore null for every row. The Landbridge alignment (announced, Jeddah–Riyadh) has no published station coordinates in the repo, so no distance is computed.
  - *Hypothetical:* none; not a register field.
- **Metro (A-screen-013):** nearest approved metro by haversine. Jazan (tier 3) for 17 rows; Abha–Khamis Mushait (tier 2) for Ad Darb (60.1 km), Abu as Sadad (61.9 km) and Ar Rayth (77.6 km).
- **Road minutes:** null everywhere; `road_min_method: pending R1a skims`.
- **Distances:** great-circle haversine between OSM coordinates (A-screen-pilot-001), not road distances.

## 3. The register (generated from `cities/ksa/regions/pilot-jazan.parquet`)

| # | governorate | centre (EN / AR) | pop 2022 (S-jazan-002) | osm_id | lat, lon | 5k / 10k / 50k | dist existing km (Makkah HSR) | dist metro km | nearest metro | terrain | economic roles | sample |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jizan | Jizan / جيزان (centre) | 173,919 | 288992209 | 16.89470, 42.55800 | Y / Y / Y | 581.0 | 0.0 | Jazan (tertiary, A-screen-013) | coastal | port, industrial_city, administrative |  |
| 2 | Sabya | Sabya / صبيا (centre) | 72,086 | 1237961155 | 17.15023, 42.62150 | Y / Y / Y | 559.9 | 29.2 | Jazan (tertiary, A-screen-013) | coastal | administrative |  |
| 3 | Abu Arish | Abu Arish / أبو عريش (centre) | 69,632 | 8506762133 | 16.96610, 42.83810 | Y / Y / Y | 589.5 | 30.8 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 4 | Samtah | Samtah / صامطة (centre) | 43,301 | 1237961376 | 16.59722, 42.94389 | Y / Y / N | 630.3 | 52.7 | Jazan (tertiary, A-screen-013) | mixed | administrative, agriculture | Y |
| 5 | Bish | Bish / بيش (centre) | 32,679 | 6391743774 | 17.37560, 42.53720 | Y / Y / N | 533.9 | 53.5 | Jazan (tertiary, A-screen-013) | coastal | administrative |  |
| 6 | Ahad al Musarihah | Ahad al Musarihah / أحد المسارحة (centre) | 25,670 | 7699743951 | 16.71070, 42.95310 | Y / Y / N | 620.1 | 46.8 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 7 | Damad | Damad / ضمد (centre) | 26,079 | 1237961144 | 17.10510, 42.77950 | Y / Y / N | 573.1 | 33.2 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 8 | Ad Dayer | Ad Dayer / الدائر (centre) | 15,752 | 4941110005 | 17.33848, 43.13289 | Y / Y / N | 573.4 | 78.5 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 9 | Al Aridah | Al Aridah / العارضة (centre) | 10,902 | 1237961156 | 17.03952, 43.08371 | Y / Y / N | 597.2 | 58.2 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 10 | Al Aydabi | Al Aydabi / العيدابي (centre) | 10,357 | 1237961253 | 17.23520, 42.94040 | Y / Y / N | 570.6 | 55.6 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 11 | Farasan | Farasan / فرسان (centre) | 10,118 | 1013176773 | 16.70220, 42.11830 | Y / Y / N | 578.7 | 51.5 | Jazan (tertiary, A-screen-013) | coastal | administrative, tourism, heritage | Y |
| 12 | Ad Darb | Ad Darb / الدرب (centre) | 5,216 | 1237960408 | 17.73340, 42.25010 | Y / N / N | 484.1 | 60.1 | Abha-Khamis Mushait (tier 2) | coastal | administrative |  |
| 13 | Al Tuwal | Al Tuwal / الطوال (centre) | 4,671 | 1237961475 | 16.53082, 42.96901 | N / N / N | 638.0 | 59.6 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 14 | Al Harth | Al Harth / الحرث (centre) | – | none (see Needs merge-stage 2) | 16.78420, 43.15290 | N / N / N | 624.8 | 64.5 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 15 | Ar Rayth | Ar Rayth / الريث (centre) | – | 1237961077 | 17.60394, 42.85668 | N / N / N | 532.2 | 77.6 | Abha-Khamis Mushait (tier 2) | mixed | administrative |  |
| 16 | Harub | Harub / هروب (centre) | – | 1237961726 | 17.43983, 42.89273 | N / N / N | 549.1 | 70.3 | Jazan (tertiary, A-screen-013) | mixed | administrative |  |
| 17 | Fayfa | Fayfa / فيفا (centre) | – | 1237961319 | 17.26329, 43.10670 | N / N / N | 578.4 | 71.3 | Jazan (tertiary, A-screen-013) | escarpment_mountain | administrative |  |
| 18 | Ad Darb | Abu as Sadad / أبو السداد (town) | 9,940 | 7699743950 | 17.72522, 42.22878 | Y / N / N | 483.6 | 61.9 | Abha-Khamis Mushait (tier 2) | coastal | none sourced | Y |
| 19 | Sabya | Al Zabyah / الظبية (town) | 11,287 | 1237961139 | 17.11748, 42.66728 | Y / Y / N | 565.6 | 27.4 | Jazan (tertiary, A-screen-013) | coastal | none sourced | Y |
| 20 | Bish | Misliyah / مسلية (town) | 5,559 | 1237961012 | 17.45988, 42.55720 | Y / N / N | 527.2 | 62.8 | Jazan (tertiary, A-screen-013) | coastal | none sourced | Y |

Population is the Census 2022 value from citypopulation.de (secondary, crediting GASTAT; `pop_type: secondary`, `pop_year: 2022`). The `5k / 10k / 50k` column shows the tags. `terrain` is assumed by rule (A-screen-pilot-002) pending DEM classes; see Needs merge-stage 4.

## 4. Sample rationale (5 rows, `pilot_sample: true`)

The brief asked for 4–6 towns that test schema edges and a spread of roles. Jazan has no existing or committed rail line, so **no row is near (<25 km) an existing line; all 20 rows are far (>100 km).** The sample spans the other axes:

| row | why it was chosen |
|---|---|
| Abu as Sadad (9,940; non-centre, Ad Darb) | **Schema edge:** a non-centre town larger than its governorate centre Ad Darb (5,216). No sourced economic role. |
| Farasan (10,118; governorate centre, island) | **With roles:** tourism and heritage (S-jazan-010, -011). Coastal island centre. |
| Samtah (43,301; governorate centre) | **With role:** agriculture (S-jazan-012, a search snippet). Below 50k, so tests the threshold. |
| Al Zabyah (11,287; non-centre, Sabya) | **Without role:** about 5 km from Sabya (72,086), so it sits inside a 50k town's reach. |
| Misliyah (5,559; non-centre, Bish) | **Without role, 5k band:** `tag_5k` only (not `tag_10k`), tests the sensitivity tag. |

Other edges in the pilot: **unmapped OSM place**, Al Harth (no `place=*` node in the box query). Its coordinates are a Nominatim boundary centroid (S-jazan-006), a placeholder rather than a settlement point. **Town split across governorates:** not found in the sources, so not tested.

## 5. Exclusions

- **No row is excluded** (`screened: true` for all 20).
- **Not in the pilot (out of scope, not excluded):** the other places in the Census 2022 list. The citypopulation table has 74 places (≥ 2,500); 35 reach 5,000 and 13 reach 10,000. The register keeps 15 of the 35 places at or above 5,000 (the 17 centres where they are 5k+, plus 3 sample towns). The other 20 are out of pilot scope. The full R2 register must cover them under A-screen-001 (10k) and A-screen-002 (5k sensitivity).

## 6. Sources

Full list with access date and status: `docs/sources/pilot-jazan.csv`. Summary:
- Population and governorate list: S-jazan-001, S-jazan-002 (citypopulation.de, secondary, crediting GASTAT; global S-073).
- Governorate count, second opinion: S-jazan-003 (Saudipedia, secondary).
- Coordinates and `osm_id`: S-jazan-005 (OSM Overpass, ODbL), S-jazan-006 (Nominatim, Al Harth), S-jazan-007 (Najran, metro check).
- Existing rail: S-jazan-008 (OSM Makkah HHR station), cross-checked with S-001 (sar.hhr.sa).
- Economic roles: S-jazan-009 (JCPDI port and zone; secondary, location conflict), S-jazan-010 and -011 (Farasan), S-jazan-012 (Samtah).
- Terrain: S-jazan-013 (Wikipedia, approximate).
- GASTAT not reached: S-jazan-015 (and S-090).

## 7. Needs judgement

1. **Governorate count, 16 vs 17.** Saudipedia (16) vs citypopulation (17). GASTAT's own table is needed to settle it (portal.saudicensus.sa unreachable; stats.gov.sa reachable but its census table was not located). Pilot keeps 17 rows.
2. **Al Harth centre.** No OSM `place=*` node was found in the box query. The coordinate is the Nominatim boundary bbox centre (16.7842, 43.1529; relation 12430365), a placeholder. The Arabic centre name is the governorate name, not confirmed. Needs a real place node or a GASTAT locality record.
3. **Jizan port location.** The JCPDI port is reported 60 km north of Jizan in one source and 60 km south-east in another (S-jazan-009). The port and the industrial zone are attached to the Jizan centre row as roles without coordinates for the zone. Confirm before using in any document.
4. **Terrain classes are rule-based.** Coastal below longitude 42.75 E; mixed east of it; Fayfa escarpment_mountain (S-jazan-013). This is A-screen-pilot-002 and is not a DEM read. Copernicus DEM classes are needed in R2.
5. **Centre populations missing** for Ar Rayth, Harub, Fayfa and Al Harth (the governorate totals exist, the centre places do not in the 2022 places table). Needs the GASTAT locality table.
6. **Roles that were not sourced.** Sabya and Abu Arish (50k+) have only the administrative role (governorate centre). Al Tuwal is on the Yemen border, but no crossing is sourced: `border_crossing` not assigned.
7. **Samtah agriculture** rests on a search snippet of the Saudipedia page. Read the page before using the role.
8. **Governorate reassignments.** Aṭ-Ṭuwāl, Fayfā and Harūb are marked with a previous parent on citypopulation (see section 1). The governorate membership of their settlements should be checked in the GASTAT admin table.

## 8. Schema notes (for the coordinator)

- `common/schemas.py:RegionRow` allows `pop_type` ∈ {official, derived, grid}. The pilot uses `secondary` (the brief's instruction). The validation used a local subclass that accepts `secondary` and changes nothing else (`PILOT_REGION_JAZAN` status block).
- The brief's extra fields (`threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `terrain_basis`, `primary_to_find`, `road_min_method`, `dist_method`) are not in `RegionRow` (strict). They are written as extra Parquet/CSV columns and are not validated.
- `uv run python -m screening.region_sweep validate` does not exist yet (`screening/cli.py` is the R0 skeleton). The check was run as `RegionRow` validation with the subclass above.

Label: **screening input, not a forecast.**
