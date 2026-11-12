> **Document version:** docs/status/pilot-al_jouf.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_AL_JOUF) | Status: draft

# Track `pilot-al_jouf` — status

## PILOT_REGION_AL_JOUF — coarse pilot sweep of Al-Jouf (الجوف), slug `al_jouf` — 30 Oct 2026

Built:
- `cities/ksa/regions/pilot-al_jouf.parquet` and `.csv`: 8 rows, same ids, cross-checked (row count, `osm_id`, `population`). Every row validated against `common.schemas.RegionRow` (8 of 8). Governorate counts in the Parquet metadata: `governorates_gastat = 4`, `governorates_listed = 4`.
- `docs/regions/pilot-al_jouf.md`: header; governorate count with the 3-versus-4 discrepancy flagged with both sources; the table (generated from the Parquet); sample rationale; exclusions; distance method; economic roles; schema gaps; "Needs Opus judgement"; "screening input, not a forecast".
- `docs/sources/pilot-al_jouf.csv`: S-al_jouf-001 to -009 (`index.csv` format, 14 fields, checked).
- `docs/assumptions-pilot-al_jouf.md`: A-screen-pilot-001 (haversine, nearest rail vertex), -002 (pop_type recording), -003 (place-level population), -004 (terrain null).

Counts:
- Rows written: **8** (4 governorate centres, 4 sample rows that are not centres; 5 rows carry the sample flag, one of them a centre).
- Governorates: GASTAT **4** (secondary; GASTAT primary not reached) / listed **4**. Discrepancy flagged: Wikipedia and Saudipedia's Emirate page say 3.
- Towns ≥ 50 000: **3** (Sakaka 204,174; Al-Qurayyat 167,080; Tubarjal 78,354). Dumat al-Jandal's centre is 42,362 (below 50k, in the sample).
- Sample: **5** rows with the sample flag (a reason for each in `docs/regions/pilot-al_jouf.md`). Far (>100 km) stratum not filled: no Al-Jouf settlement is that far from the SAR North alignment (largest 53.28 km).
- Facts: **verified 3** (OSM via Overpass and Nominatim: S-al_jouf-006, -007; SAR North places S-018); **secondary 6** (citypopulation.de S-001/-002 crediting GASTAT; Wikipedia and Saudipedia S-003/-004 read from search summaries only; Wikipedia Sakaka S-008; Arab News S-009); **unverified 1** (GASTAT portal S-al_jouf-005: no connection; GASTAT 2004 Al-Jouf PDF 404).

Verification and checks run:
- `RegionRow` validation: 8 of 8 rows pass. Parquet and CSV agree.
- Version headers: `docs/` checked file by file (18 Markdown files, all valid).
- `common/docver.py` bug: `iter_md` drops every file whose absolute path contains `.worktrees`, so `python -m common.docver check docs` reports "0 files" in any worktree. The check above was run per file instead. Report to the coordinator.
- Not run: ruff and pytest (no code changed); `uv run python -m screening.region_sweep validate` (module does not exist in this worktree: validated with `RegionRow` in Python instead).

Deviations from the brief (all recorded in the register document):
- `pop_type`: the schema has no `secondary` value; Census values from citypopulation.de are recorded as `official` with the secondary source row (A-screen-pilot-002). Needs Opus decision.
- Schema gaps: `threshold_50k`, `pilot_sample`, `notes`, `road_min_method` and `nearest_metro_tier` are not `RegionRow` fields (`extra="forbid"`). Carried in the Markdown, or inside `nearest_metro` as "Tabuk (tier 2, A-screen-013)". `common/schemas.py` was not changed.
- Governorate count: GASTAT primary not reached, so `governorates_gastat = 4` is secondary.
- Committed distances: `dist_committed_km` left null for every row. No committed alignment geometry exists in the repository, and no sourced Al-Jouf alignment was found.
- Terrain: `terrain_class` null on every row (A-screen-pilot-004); no DEM read in the pilot.
- Economic roles: Tubarjal border and Al-Qurayyat industrial were searched and not found; not recorded.

Needs Opus judgement:
1. Governorate count 3 or 4: the GASTAT list must settle it (the GASTAT census portal gave no connection on 30 Oct 2026).
2. `pop_type` for secondary-sourced census values: add `secondary` to the schema, or replace with the GASTAT locality table before use.
3. Name-only OSM matches to census places: Abu 'Ajram (node 5910483362, about 50 km west of Dumat, matched by Arabic name), Al-Fayāḍ (الفياض) and Ṣuwayr (صوير). Confirm the census Arabic.
4. Al-Ḥadīthah: SAR's North-line terminus "Al Haditha" (S-018) versus census Al-Ḥadīthah al-Qadīmah (3,956, below 5,000). Decide which governorate the terminus is in.
5. Jouf station (OSM الجوف, 29.6485, 39.8377): 17.7 km from the Dumat centre and 51 km from Sakaka; not assigned to a governorate. Is it the region's main station?
6. Terrain class (R1a DEM); economic roles for Tubarjal and Al-Qurayyat (sources needed).
7. Unmatched 5k–50k places: Ghaṭā (ambiguous OSM candidate) and Mīqūa' (Arabic match unconfirmed) are excluded, not guessed.
8. Far (>100 km) stratum: empty for Al-Jouf. Decide whether an empty stratum is acceptable in the pilot.

Licences: OSM data is ODbL 1.0. Coordinates and `osm_id` come from OSM via the Overpass and Nominatim APIs; no raw extract is stored in the repository. Licence register row and `cities/ksa/sources.yaml` entry for the API reads still to be added by the coordinator. No new datasets were downloaded (the disk gate was respected: no grids, no PBF).

Elapsed: about 10 minutes of wall time (first OSM query 21:58 GMT+3; this status written 22:08 GMT+3).

Commit: `feat(screening): pilot sweep al_jouf` (branch `pilot-al_jouf`; not pushed).

PILOT_REGION_AL_JOUF: done
