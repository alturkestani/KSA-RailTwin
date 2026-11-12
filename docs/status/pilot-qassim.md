> **Document version:** docs/status/pilot-qassim.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_QASSIM) | Status: draft

# Status: pilot-qassim (PILOT_REGION_QASSIM)

## Block: pilot sweep, Qassim (slug `qassim`), 30 Oct 2026

**Built:** `cities/ksa/regions/pilot-qassim.parquet` and `.csv` (19 rows), `docs/regions/pilot-qassim.md`, `docs/assumptions-pilot-qassim.md` (A-screen-pilot-001, A-qassim-terrain-001), `docs/sources/pilot-qassim.csv` (S-qassim-001 to 007 and 009; 008 unused), this file.

**Counts**
- Rows written: 19 = 13 governorate centres + 1 excluded row (Abanat) + 5 pilot samples.
- Governorates: `governorates_gastat` = 13 (secondary, as credited to GASTAT by citypopulation.de; GASTAT's own table not reached) and `governorates_listed` = 13. Equal, but the GASTAT figure is not primary. Conflicts: Wikipedia infobox 12, Arabic Wikipedia 14 (adds Abanat, excluded).
- Towns ≥ 50,000: 3 (Buraydah 571,169; 'Unaīzah 183,319; Ar Rass 107,902), all governorate centres. Open point: Buraydah governorate's remainder of 106,478 persons is not placed (see region report section 3).
- Pilot sample: 5 non-centre towns, 5k–50k (Al-Quwārah, Al-Malīdā', Al-Khubarā', Qibah, Dakhnah), each with a written reason. Near arm: 1 (5.4 km); mid: 2 (30.7, 62.1 km); far: 2 (101.3, 134.3 km). Sample role arm: 0 sourced roles found.
- Coordinates: 16 OSM place nodes or ways (including the excluded Abanat node); 3 boundary-relation centroids (Bukayriyah, Midhnab, Ḍariyah); the Ḍariyah centroid is flagged as unresolved and its distances are invalid.

**Facts: verification status**
- Primary-verified (read at the primary source): 0. The GASTAT census portal did not connect on the access date.
- Secondary: all populations (citypopulation.de, crediting GASTAT; the 13 governorate populations sum exactly to the region total 1,336,179); the governorate list (citypopulation.de and Wikipedia table); the North-line "Operating" status and the Al-Qassim station (Wikipedia infobox and station table); OSM coordinates and osm_ids (ODbL); the rail geometry (Overpass, timestamp 2026-10-30T18:25:51Z).
- Unverified: economic roles for Unaīzah (tourism) and Ar Rass (agriculture), from search summaries that were not opened; the terrain description (Najd plateau, 600–750 m, Ad Dahna dunes), also a search summary; Buraydah's administrative role is from the Wikipedia article (fetched, not verbatim-checked).
- Raw inputs are archived under `data/ksa/pilot-qassim/raw/` (gitignored), SHA-256 in `docs/sources/pilot-qassim.csv`. Not yet registered in `cities/ksa/sources.yaml`, which this track does not own; the coordinator should add the four raw rows (citypop admin, citypop Qassim page, citypop cities page, Overpass rail; 40 Nominatim JSON files as one group).

**Validation**
- Canonical `common/schemas.py:RegionRow`: **16 of 19 rows fail**, all on `pop_type` (`'secondary'` is not an allowed value; checked field by field). The 3 rows without population pass.
- Pilot extension (local subclass, adds `secondary` and the extra columns; not committed): 19 of 19 pass.
- Parquet and CSV agree: 19 rows each, same ids and order.
- `screening.region_sweep validate` does not exist in this worktree (the screening package is a skeleton), so the validation above is a one-off check, not the CLI.
- docver: `uv run python -m common.docver check docs` reports "0 files" from this worktree. Cause: `iter_md` skips every path containing `.worktrees`, and this worktree's own path contains that segment. Checked the three new Markdown files individually with `check_file`: all OK. Likely a shared-code bug to fix in `common/docver.py` (not changed here).

**Decisions taken**
- `pop_type = secondary` for all populated rows, as the prompt requires; the schema does not allow it, so the register cannot pass canonical validation (see the blocker below).
- Pilot-only fields written as extra columns (`threshold_50k`, `pilot_sample`, `notes`, `dist_method`, `road_min_method`, `terrain_status`, `nearest_metro_tier`, `coord_flag`), because `RegionRow` forbids extra fields.
- Ash-Shimāiyah's centre (5,719) is kept as a governorate row even though it is below 10k: rule 2 requires every governorate to appear.
- 'Uqalt aṣ-Ṣuqūr and Al-'Asyāḥ have null populations (their centre place rows are not in the source); their governorate totals are not used as centre populations.
- Abanat is an excluded row, not a governorate, pending GASTAT.
- Hijrat 'Uqlat aṣ-Ṣuqūr (9,717) is not a row: no OSM place node, so no coordinates. Listed as an omission in the region report.
- Nearest approved metro set to Buraydah (tier 2) for every row, checked against Buraydah only; the other approved metros were not computed.
- Committed distances are null: no committed alignment through Qassim is in any source reached.
- Terrain set to `flat_desert` for all rows as an assumption (A-qassim-terrain-001), pending a DEM read.

**Could not verify**
- GASTAT's own governorate list and populations (portal not reachable).
- The Qassim station's distance from Buraydah (the search snippet said about 10 km east; not used as a number).
- Economic roles beyond Buraydah, and any role for the sample towns.
- Citypopulation.de's terms of use (not read; relevant to licence register rows; not yet added to `docs/licences-*.csv`, which this track does not own).

**Elapsed:** about 11 minutes wall time (session files stamped 21:22; this block written 21:33).

**Needs Opus judgement**
1. `RegionRow.pop_type`: allow `secondary` (additive change to `common/schemas.py`), or map secondary to an existing value in R2. This decides whether validation can pass.
2. The pilot-only fields: add them to `RegionRow` or move them to a sidecar file.
3. Buraydah governorate remainder (106,478): whether a settlement of 50k or more sits outside the city proper.
4. Ḍariyah coordinates and distances: replace the boundary centroid with a place node.
5. Bukayriyah and Midhnab: replace boundary centroids with place nodes.
6. Economic roles: confirm Unaīzah (tourism) and Ar Rass (agriculture) against a primary source; find roles for sample towns.
7. Terrain: DEM read in R2 (dune fields may apply).
8. docver's `.worktrees` exclusion (shared code).

**Handoff:** the register is written and usable for the schema review, but the canonical validator rejects it on one field.

PILOT_REGION_QASSIM: blocked - canonical RegionRow rejects pop_type 'secondary' on 16 rows (the pilot extension passes all 19); schema decision needed (Opus judgement item 1).
