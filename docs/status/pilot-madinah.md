> **Document version:** docs/status/pilot-madinah.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_MADINAH) | Status: draft

# Track `pilot-madinah` — status

## PILOT_REGION_MADINAH — coarse pilot sweep of Al-Madinah (30 Oct 2026)

**Built:** `cities/ksa/regions/pilot-madinah.parquet` and `.csv` (9 rows, same ids), `docs/regions/pilot-madinah.md`, `docs/assumptions-pilot-madinah.md` (A-screen-pilot-001 to 005), `docs/sources/pilot-madinah.csv` (14 rows, S-madinah-001 to 015; 007 unused).

**Measured:**
- Rows written: 9 (8 governorate centres + Ath-Thamad). Excluded and explained in `docs/regions/pilot-madinah.md` section 5: Mazārī' Wādī al-'Uqūl (no OSM node), 12 places of 2.5k–4.5k (below 5k), and no centre row for Wādī al-Fara'.
- Governorates: `governorates_gastat` = **unverified** (GASTAT primary not reached; secondary reading is 9 rows = 8 governorates + capital). `governorates_listed` = **8 of 9** (Wādī al-Fara' has no row; flagged).
- Towns ≥ 50,000: 2 (Al-Madinah 1,411,599; Yanbu' al-Bahr 331,916, the census place includes Yanbu Industrial City).
- Sample of 5k–50k towns: 5 rows with `pilot_sample: true` and a reason in `notes` (Al-Ula, Badr, Khaybar, Mahd adh-Dhahab, Ath-Thamad). Near stratum (< 25 km) empty for this region.
- Population check: the 9 governorate rows of citypopulation.de sum to 2,137,983, which matches DataSaudi, Saudipedia and GLMM. Its region row (2,389,452) does not, flagged.
- Parquet and CSV: same 9 rows and ids (checked). Markdown register table vs Parquet: 0 mismatches (checked programmatically).
- Sources: 14 rows. Verified 1 (OSM, ODbL), secondary 11, unverified 2 (GASTAT portal; Landbridge page 404).
- Distances: haversine (A-screen-pilot-001). Nearest located existing station is the HHR Madinah station in all 9 rows (8.96–290 km). KAEC station not located, so this is provisional.
- `docver`: the directory form (`check docs`) reports "0 files" from inside this worktree (see Observations); run on explicit files it passes (see Handoff).
- Elapsed time: not measured.

**Decisions (recorded, not asked):**
- Field names follow `common/schemas.py:RegionRow` (`dist_existing_km`, `dist_committed_km`, `dist_metro_km`, `road_min_*`, `nearest_*`), not the prompt's `dist_km_*` names.
- Terrain classes follow the schema (`dunes`, `coastal`, `mixed`, `escarpment_mountain`, `flat_desert`, `sabkha`), not the prompt's `sand_dunes` and `coastal_plain`.
- Centre row = the place carrying the governorate's name (A-screen-pilot-003).
- Population for centres = census place rows (Yanbu' includes Yanbu Industrial City; A-screen-pilot-005).
- Nothing committed in Al-Madinah: no committed line is sourced (Landbridge page returned 404; search summary unverified). No row is labelled existing or committed in error.
- Empty economic roles mean "not recorded", not "no role" (Al-Henakiyah, Al-'Aīṣ, Ath-Thamad were not searched).
- No change to `common/` or the `screening` package (the prompt's `screening.region_sweep validate` does not exist in this worktree, so the register was validated by pydantic directly against `RegionRow`).

**Validation result:** each of the 9 rows fails `RegionRow` validation on one field only: `pop_type = 'secondary'` (allowed: `official`, `derived`, `grid`). Extra pilot columns (`threshold_50k`, `pilot_sample`, `nearest_metro_tier`, `primary_to_find`, `road_min_method`, `dist_method`, `notes`) are also rejected because the model forbids extra fields. These two schema points are why the milestone is blocked.

**Needs Opus judgement** (full list in `docs/regions/pilot-madinah.md` section 6):
1. `RegionRow.pop_type` has no `secondary` (add it to `common/schemas.py`, or relabel GASTAT-credited rows).
2. `RegionRow` forbids the pilot annotation columns (extra = forbid): add to the schema or move them to a sidecar.
3. Wādī al-Fara' governorate centre unnamed in the sources: no row.
4. Mazārī' Wādī al-'Uqūl (24,381): no OSM node found; cannot be placed.
5. Yanbu' population includes Yanbu Industrial City (331,916).
6. Badr: OSM way tagged `place=village`, census 30,494.
7. Governorate count: GASTAT primary unverified (9 vs 8 + capital).
8. Landbridge route through Madinah or Yanbu': unverified; no committed row.
9. KAEC station coordinates not located; existing-distance results depend on it.
10. Mahd adh-Dhahab distance from Madinah 167 vs 380 km (not used).

**Facts verified / secondary / unverified:** 1 / 11 / 2 (see `docs/sources/pilot-madinah.csv`). Secondary figures are GASTAT-credited aggregator data and search-summary reads; the pages behind most economic-role sources were not fetched in full (see the `locator` and `status` columns).

**Observations (outside this track; for the coordinator):**
- `common.docver` directory check: `iter_md` drops any `.md` whose absolute path contains `.worktrees`. From inside a worktree (this one), `docver check docs` therefore reports "0 files" and passes trivially. Explicit file paths work. Suggest matching `.worktrees` only relative to the repo root.
- `screening.region_sweep` does not exist in this worktree; the `region-sweep` skill's `validate` command is not available.
- The region-sweep skill's schema (`pop_type` set, `tag_*` names) and the prompt's field names differ from `RegionRow`. Decide which is canonical before R2 (13 region-scout sweeps).

**Handoff:**
- `uv run python -m common.docver check` on the explicit new `.md` files: passed (see the commit log entry for the run).
- `git add -A && git commit -m "feat(screening): pilot sweep madinah"`: done (see log).
- Cost-log row: `run_track.sh` logs the run; not done by this agent.

PILOT_REGION_MADINAH: blocked - RegionRow (common/schemas.py) rejects pop_type 'secondary' and the pilot annotation columns; needs an Opus schema decision (docs/regions/pilot-madinah.md section 6, items 1-2). The register, sources and assumptions are complete otherwise.
