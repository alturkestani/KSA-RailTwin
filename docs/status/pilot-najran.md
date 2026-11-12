> **Document version:** docs/status/pilot-najran.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_NAJRAN, track pilot-najran) | Status: draft

# Track pilot-najran: status

## PILOT_REGION_NAJRAN: coarse pilot sweep of Najrān (slug `najran`) — 30 Oct 2026

**Built:** `cities/ksa/regions/pilot-najran.parquet` and `.csv` (9 rows, same IDs and order); `docs/regions/pilot-najran.md` (tables generated from the Parquet); `docs/assumptions-pilot-najran.md` (5 rows: A-screen-pilot-001, A-screen-pilot-002, A-najran-pop-001, A-najran-terrain-001, A-najran-osm-001); `docs/sources/pilot-najran.csv` (S-najran-001 to S-najran-010, ids prefixed `S-najran-`).

**Measured:**
- Governorates: `governorates_gastat: 7 (unverified)`; `governorates_listed: 7` (six governorates plus the regional capital Najrān). Sources: citypopulation.de (S-najran-001, S-073) and Saudipedia "six governorates + capital" (S-najran-003). GASTAT primary not reached (S-090).
- Region total 592,300; the seven governorate rows sum exactly to it.
- Towns ≥ 50,000: 2 (Najrān 381,431; Sharūrah 89,456).
- Pilot sample (`pilot_sample: true`, 5,000–50,000): 4 (Al-Mish'alīah 23,252; Ḥubūnā 12,738; Al-Wadī'ah 8,365; Khubāsh 7,182). This is the full sourced pool; the "near rail < 25 km" stratum is empty.
- Governorate centres below 5,000 kept as coverage rows and excluded from screening: Yadamah (4,983), Badr al-Janūb (2,709), Thār (no sourced population).
- Rows with a population: 8 of 9. Every population carries `pop_source`, `pop_year`, `pop_type`.
- Existing-rail distances: 562 km to 799 km (haversine to the nearest Saudi OSM rail vertex). Najrān has no rail. Committed distances: not computed (no `cities/ksa/lines/` yet).
- Metro distances: Najrān city 0.0 km (self, tertiary); all other rows 34.8 km to 308.8 km to Najrān.
- Validation: 9 of 9 rows pass `common/schemas.py:RegionRow` after two documented shims (`pop_type: secondary` mapped to `official` for the check only; extra columns dropped for the check only). `screening.region_sweep validate` does not exist in this worktree (`screening/cli.py` is the R0 skeleton), so the validate command was not run.
- Parquet and CSV agree: 9 rows each, same `osm_id` and `name_en` order.
- Facts by status (docs/sources/pilot-najran.csv): verified 1 (S-najran-004, OSM local file); secondary 8 (S-najran-001, 002, 003, 005, 006, 007, 008, 010); unverified 1 (S-najran-009, weak dune description).
- Elapsed time: about 15 minutes of wall time (estimate; the worktree snapshot was taken at 21:56 and the last file was written at about 22:06).
- Downloads: none. The OSM GCC extract was read locally; `osmium tags-filter` wrote intermediate extracts to `/tmp` (not committed). Disk: unchanged.

**Acceptance check (prompt's list):**
1. `governorates_listed == governorates_gastat`: **not met.** The listed count (7) matches the secondary sources, but GASTAT's own count could not be read. Recorded as `7 (unverified)`; no discrepancy is flagged.
2. Every row has `pop_source`, `pop_year`, `pop_type`; no population without a source: **met** (Thār has all three null).
3. Distances carry a method: **met** (A-screen-pilot-001).
4. No planned or committed line labelled existing: **met** (no committed rows).
5. Every economic role names a source: **met**.
6. Stratified sample has 4–6 rows with `pilot_sample: true` and a reason each: **met** (4 rows).
7. Parquet and CSV agree; Markdown table matches the Parquet: **met** (tables generated from the Parquet).

**Needs Opus judgement** (full list in `docs/regions/pilot-najran.md`):
- Khubāsh centre: village node n8503374507 (used) vs governorate node n6774251958 (55.5 km apart).
- Ḥubūnā centre: town node n11871306300 (used) vs governorate node n6769844117 (20.2 km apart).
- Najrān and Sharūrah centre rows use the city and town figures, not the governorate totals (421,902; 100,199).
- Sharūrah airport role rests on the airport name in S-najran-007; location unverified.
- Terrain for all rows is assumed (A-najran-terrain-001); the dune call is weakly sourced.
- Thār centre population: null until the GASTAT locality table is read.
- Whether to add `secondary` to `pop_type` and the pilot columns (`threshold_50k`, `pilot_sample`, `notes`, `osm_place_tag`) to `RegionRow` (see Schema gaps).

**Schema gaps found** (not changed; `common/` and `screening/` are not owned by this track): `pop_type` enum lacks `secondary`; `RegionRow` lacks `threshold_50k`, `pilot_sample`, `notes`, `osm_place_tag`, `dist_method`, `screen_stage`, `nearest_metro_tier`; `terrain_class` enum uses `dunes`/`coastal`/`mixed` (the prompt's `sand_dunes`/`coastal_plain` do not exist); no `screening.region_sweep` module; no `cities/ksa/lines/`.

**Could not verify:**
- GASTAT's official governorate count and every GASTAT Census 2022 population for Najrān: portal.saudicensus.sa does not resolve (S-090), and stats.gov.sa has no region tables. Every population is secondary (citypopulation.de).
- Terrain from DEM (not in scope for the pilot).
- Road minutes (pending R1a skims).
- Committed-line distances (no committed geometry in the repo; Landbridge, GCC railway and Riyadh Rail Link are not in the register).

**Not committed:** the builder and distance scripts are in `/tmp/najran_work/` (not in the repo, because the track may only write the files it owns). The register and its inputs are reproducible from the OSM extract (manifest `osm-gcc-2026-10-14`) and the source rows. Recommend moving the builder into `screening/` at R2.

**Commit:** `feat(screening): pilot sweep najran` on `pilot-najran` (see git log).

PILOT_REGION_NAJRAN: blocked - GASTAT primary governorate list and census locality table are unreachable (S-090); governorate count (7) and every population are secondary-sourced, so acceptance criterion 1 (governorates_listed == governorates_gastat) cannot be verified. The register, the sample and the Parquet/CSV/Markdown agreement are complete and can be used if the orchestrator accepts secondary sourcing for the pilot.
