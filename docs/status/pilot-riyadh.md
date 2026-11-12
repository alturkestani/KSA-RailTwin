> **Document version:** docs/status/pilot-riyadh.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_RIYADH) | Status: draft

# Status: pilot-riyadh (PILOT_REGION_RIYADH)

## PILOT_REGION_RIYADH block (30 Oct 2026, 21:05 to 21:22 Asia/Riyadh, about 17 min wall time)

- **Rows written:** 25 (23 governorate centres + 2 non-centre sample towns). Files: `cities/ksa/regions/pilot-riyadh.parquet`, `pilot-riyadh.csv` (same 25 rows; identical content checked), `docs/regions/pilot-riyadh.md`.
- **Governorates:** GASTAT 23 (`governorates_gastat: 23`, **unverified against GASTAT**: `portal.saudicensus.sa` did not resolve, S-090) vs listed 23. Discrepancy flagged: English Wikipedia says 22 (regional capital not counted). Every governorate has a centre row (or a row marked not screened with a reason).
- **Towns ≥ 50,000 (`threshold_50k`):** 7, all governorate centres: Riyadh, Al-Kharj, Al-Majma'ah, Az-Zulfi, Ad-Dawadmi, Ad-Dir'iyah, Al-Muzahimiyah. All seven populations are **secondary** (citypopulation.de crediting GASTAT, or Wikipedia). None is a GASTAT primary.
- **Sample (5k–50k):** 4 rows with `pilot_sample = true` and a reason in `notes`: Rimah (far, with role), 'Afif (far, no role, unmapped OSM place), Al-Uyaynah and Al-Jubaylah (mid-distance, no role, non-centre). **Gap:** no near-rail (<25 km) small town, because the only one within 25 km of a proxy station is above 50k. Recorded, not hidden.
- **Screened:** 11 rows; not screened: 14 (13 centres with no sourced centre population, 1 centre unresolved). Each has `exclusion_reason`.
- **Facts (sources):** verified against a primary: SAR North and East place lists (S-018, S-025), the Riyadh Metro station count (S-034). Primary snippets only: UNESCO 1329 (S-riyadh-012), Diriyah Company (S-riyadh-013). Secondary: all citypopulation.de and Wikipedia figures (S-080, S-riyadh-001 to 009, 011, 014, 015), S-062, S-037, S-060, S-073. Unverified: GASTAT governorate count (S-072, S-090), GASTAT locality populations (none read). OSM coordinates (S-riyadh-010, ODbL): read 30 Oct 2026; some are relation centroids, flagged.
- **Elapsed:** about 17 min wall time (research and build).

### Method and deviations from the brief (decided by the builder; recorded here)

1. **Schema extended (additive, `common/schemas.py`).** `RegionRow` forbids extra fields and lacked the fields the brief names. Added, all optional with defaults: `osm_type`, `primary_to_find`, `threshold_50k`, `nearest_metro_tier`, `distance_method`, `road_min_method`, `terrain_source`, `pilot_sample`, `notes`. Widened `pop_type` to include `secondary` (the brief's rule). No existing field changed. Tests pass (see below). Coordinator: please review and merge into the main schema.
2. **`screening.region_sweep` does not exist** in this worktree (`screening/cli.py` is the R0 skeleton). The register was written with pandas against `common/schemas.py:RegionRow`, validated by `common.schemas.load_region_register` (25 of 25 rows pass). The `validate` command was not run.
3. **Build script in the repo:** `cities/ksa/regions/build_pilot_riyadh.py` generates the Parquet, CSV, and Markdown table from one row list. Run with `PYTHONPATH=. uv run python cities/ksa/regions/build_pilot_riyadh.py`. It is not a CLI; that is acceptable for the pilot.
4. **Distances:** great-circle (A-screen-pilot-001). Station and line locations are place-centre proxies (A-screen-pilot-004) because no `cities/ksa/lines/` file exists yet and the SAR/Landbridge lists give no coordinates. Road minutes are empty (pending R1a skims). Overpass returned 502 (busy) and was not retried successfully, so no OSM station geometry was used.
5. **Terrain:** Riyadh escarpment (S-riyadh-015, secondary); all others `flat_desert` assumed (A-screen-pilot-002). No DEM was read (disk gate and time).
6. **Layer discipline:** every planned line is labelled "announced/planned" or "committed". Landbridge is never called existing. The existing layer is SAR passenger only (North and East via place proxies). Freight (S-026) is not used.
7. **Assumptions:** A-screen-pilot-001 to 004, in `docs/assumptions-pilot-riyadh.md` (merge at integration).
8. **Sources:** `docs/sources/pilot-riyadh.csv` (S-riyadh-001 to 015). Existing S-nnn reused from `docs/sources/index.csv`.
9. **OSM usage:** Nominatim search (ODbL) with a non-commercial User-Agent, one request per second. No bulk download; no PBF; no data under `data/`.

### Needs Opus judgement (not guessed; recorded in `docs/regions/pilot-riyadh.md`)

1. Wadi ad-Dawasir centre population (governorate total 91,535 is not the centre figure).
2. Al-Aflaj centre identity (OSM place "Layla" presumed; Arabic name unsourced).
3. Al-Kharj and Az-Zulfi coordinates are governorate-centroid proxies; distances can be tens of km off.
4. Riyadh population: S-080 (6,924,566) vs Wikipedia 7,000,100 vs governorate 7,009,120. The index's S-080 is used.
5. Hotat Sudair branch campus not mapped to Hawtat Bani Tamim (unconfirmed naming).
6. Terrain beyond Riyadh (DEM check needed in R1a).

### Checks run

- `uv run ruff check common cities`: all checks passed. `uv run ruff format` applied to the new script and `common/schemas.py` (diff of `schemas.py` is additive only).
- `uv run pytest -q`: see the result line in the handoff message.
- `PYTHONPATH=. uv run python cities/ksa/regions/build_pilot_riyadh.py`: rows 25, validated 25, governorates 23, threshold_50k 7, pilot_sample 4.
- `python -m common.docver check docs`: **reports 0 files when run on a directory inside a git worktree** (`common/docver.py:iter_md` drops any path with `.worktrees` in its parts, and the worktree root contains it). Per-file check run on each new Markdown file instead; see the handoff. Coordinator: fix `iter_md` (filter relative to the root, not absolute parts).
- The brief's `screening.region_sweep validate` was not run (module absent; see deviation 2).

PILOT_REGION_RIYADH: done
