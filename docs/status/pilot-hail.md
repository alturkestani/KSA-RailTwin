> **Document version:** docs/status/pilot-hail.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, track pilot-hail) | Status: draft

# Track `pilot-hail` — status

## PILOT_REGION_HAIL — 30 Oct 2026

**Built:** coarse pilot register for Ḥā'il (slug `hail`): `cities/ksa/regions/pilot-hail.parquet` and `.csv` (same 11 rows, same ids), `docs/regions/pilot-hail.md`, `docs/assumptions-pilot-hail.md` (6 rows), `docs/sources/pilot-hail.csv` (8 `S-hail-` rows), `docs/licences-pilot-hail.md` and `.csv` (3 rows), a transcription of the citypopulation.de Hail page in `data/ksa/hail/` (gitignored; manifest row `citypop-hail-census2022`).

**Measured:**
- Governorates: GASTAT **not reached** (portal DNS failure, S-hail-002). Count **9 (secondary)**, listed 9 (citypopulation.de, S-hail-001; matches S-073). Flagged, not confirmed by a primary.
- Rows: 11 (9 governorate centres, Jubbah, Turubah). Screened 8, excluded 3 (As-Sulaymī, Mawqaq, Simīrā' with reasons).
- Towns ≥ 50,000: 1 (Ḥā'il, 448,623).
- Pilot sample: 5 rows with `pilot_sample = Y`, each with a reason (far 4, heritage role 1, schema edges 2).
- Population: all 10 populated rows are `pop_type = secondary`, `pop_year = 2022`, `pop_source = S-hail-001`. One centre (As-Sulaymī) has no published figure and is not estimated.
- Sources: verified 2 (S-hail-003 OSM; S-hail-007 university site), secondary 5 (S-hail-001, 004, 005, 006, 008), unverified 1 (S-hail-002, GASTAT). Existing: S-018 verified, S-073 secondary.
- Validation: all 11 rows pass `RegionRow` with a local subclass that allows `pop_type = secondary` (`common/` untouched). Parquet and CSV agree on row count and ids. Parquet schema metadata: `governorates_gastat: 9`, `governorates_listed: 9`.
- Manifest: `uv run python -m common.manifest verify --manifest cities/ksa/sources.yaml --root .` → OK, 5 rows.
- Headers: `common.docver check` on the worktree path returns 0 files (see "Tooling issue" below); `check_file` on each new `.md` returns no error.
- Elapsed: about 10 minutes wall-clock (21:22 to 21:31 local, 30 Oct 2026), mostly web reads.

**Commands run:**
- `osmium extract` and `tags-filter` on `data/osm/gcc-states-latest.osm.pbf` (scratch in `/tmp/hail-scratch`, not committed)
- `uv run python -I` build and validation scripts (in `/tmp/hail-scratch/`, not committed; see "Not done")

**Schema and tooling deviations (flagged, not fixed in `common/`):**
- `RegionRow.pop_type` has no `secondary`; the pilot brief and `source-citation` need it. Register writes `secondary`; validation used a local subclass.
- `RegionRow` has no `threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `primary_to_find`, `terrain_basis`, `assumption_id`, `road_min_method`, `dist_method`, `notes`. These are pilot-only extra columns.
- `screening.region_sweep` (with its `validate` command) does not exist in this worktree. Validation was done by pydantic against `RegionRow`.
- **Tooling issue:** `common/docver.py:iter_md` skips every file whose path contains `.worktrees`, so `common.docver check docs` finds 0 files inside any worktree. Fix needed: match `.worktrees` relative to the root, not on absolute parts. Not changed here (`common/` is additive-only for track worktrees).

**Needs Opus judgement:**
1. As-Sulaymī centre population is absent from the 2,500+ table. Not estimated; needs a GASTAT locality figure.
2. Al-Ajfir (7,518, Baq'ā' governorate) is not registered: no OSM place node found in the pilot extract, and coordinates are required.
3. The 50,000 threshold is applied at settlement level; Al-Ḥā'īṭ (74,596) and Baq'ā' (56,362) are governorate totals only. Confirm.
4. The "near" test (< 25 km from an existing station) is unmet: no 5,000–50,000 town in Ḥā'il lies that close. Sample is far-biased.
5. Terrain is `mixed` by assumption (`A-screen-pilot-002`) for all rows except Ḥā'il city. Decide whether R1a runs a DEM classification.
6. OSM population tags conflict with the census figures for six towns (not used; see docs/regions/pilot-hail.md section 7).
7. Schema: add `secondary` to `pop_type`, and whether the pilot-only columns belong in `RegionRow`.

**Facts verified / secondary / unverified:** see the S-hail table above. The GASTAT count and every GASTAT-attributed population figure are secondary. The GACA airport role is from a search snippet; the UNESCO inscription is from a secondary listing (UNESCO returned 403).

**Not done (and why):**
- GASTAT primary list and locality table (DNS failure on the portal; no alternative primary reached).
- Road minutes (`road_min_*` null; pending R1a skims, per the brief).
- Committed-line distances: no committed alignment with coordinates in the repository. Landbridge, GCC railway and Riyadh Rail Link are announced; their station coordinates are unverified (S-061, S-062).
- The build and validation scripts are in `/tmp/hail-scratch/` and are not committed. Re-running needs them recreated or the R2 `screening.region_sweep` CLI.
- `docs/coverage.md` not updated (not owned by this track); it still reconciles to 150 rows (S-073) until GASTAT's primary is read.

PILOT_REGION_HAIL: done
