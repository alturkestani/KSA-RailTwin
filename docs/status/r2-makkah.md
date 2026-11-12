> **Document version:** docs/status/r2-makkah.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_MAKKAH) | Status: draft

# Status: r2-makkah (track `r2-makkah`, milestone `REGION_MAKKAH`)

## REGION_MAKKAH: region sweep, Makkah (مكة المكرمة), 31 Oct 2026

**Outputs.** `cities/ksa/regions/makkah.parquet` and `.csv` (77 rows; header `governorates_gastat` = 17, `governorates_listed` = 17); `docs/regions/makkah.md` (generated table, exclusions, sources, Opus list); `docs/assumptions-r2-makkah.md` (A-makkah-001 to 010); `docs/sources/r2-makkah.csv` (S-makkah-008, 009; the pilot ids S-makkah-001 to 007 stay in `docs/sources/index.csv`); `docs/licences-r2-makkah.csv` and `.md`; `screening/sweeps/makkah/build.py` (the builder; run `build build --seed 1`); `tests/test_makkah_register.py`; raw `data/ksa/makkah/raw/nominatim-ardhiyat-2026-10-31.json` (gitignored; registered in `cities/ksa/sources.yaml`).

**Counts (measured).**
- Governorates: GASTAT **17** (S-cp2-gastat-007, joined by name to the S-073 list; the region sum 8,021,463 equals S-soc-339). Listed: **17**. They match. The primary table has no region column, so the count is a name join (A-makkah-008).
- Rows: **77**; governorate centres **17** (every governorate has a row; Al-Ardiyat's centre is the OSM boundary centroid, not a settlement).
- `tag_10k` true: **16** (15 official, all `verified` from S-cp2-gastat-008; 1 derived, Al Quoz from an OSM tag). `tag_5k` true: **68**.
- Official rows ≥ 10,000: 15 (the ≥ 10k test for these uses the primary figure only; no corroboration needed).
- Grid rows (WorldPop, `pop_type` grid, all `unverified`): 41; of these 36 are ≥ 5,000 and 12 are ≥ 10,000 with `tag_10k` held false (`grid-only population, uncorroborated`, A-screen-031/032). No Makkah grid row has a second method run: the one 2010-growth check (Dhahban) is superseded by its primary figure.
- Excluded or not screened: 8 rows (1 duplicate, 1 governorate centre without population, 1 OSM tag without a year, 5 towns below 5,000). Villages below 5,000 are not rows; they stay in `cities/ksa/zones/settlements.parquet`.
- Economic roles: **20** entries on **7** rows, each with an S- source (R1a `economic_nodes.csv` S-r1a-*; CP1 roles S-cp1-*; KAUST snippet S-makkah-003). Rows with no sourced role have an empty list, meaning not sourced, not "none".
- Terrain: not assessed (null everywhere; A-makkah-010).
- Road minutes: OSRM free-flow skims (S-r1a-809, uncalibrated) for every row the universe covers. The Al-Ardiyat centroid has none (`pending skims`).

**Facts: verified / secondary / unverified.**
- Verified: governorate count (by name join to the GASTAT primary table, S-cp2-gastat-007); the 15 official ≥ 10k populations and the official city 5k rows (S-cp2-gastat-008); OSM ids and coordinates (osm-gcc-2026-10-14); the Al-Ardiyat boundary (S-makkah-008).
- Secondary: 8 rows: 2 relayed official figures (S-makkah-001: Adham, the Census 2010 bridge attribution; Al Kamil, below the 5,000 city export) and 6 OSM-tag derived rows (S-makkah-009; years as tagged). Roles from snippets or governorate-level ties (S-makkah-003; S-cp1-104).
- Unverified: all 41 WorldPop grid rows (S-r1a-505; the grid is not GASTAT and is not corroborated); the Adham identity (A-makkah-003); the Al-Ardiyat seat town (not located).

**Decisions taken (recorded here).**
1. Adham (أضم): the relayed figure 9,022 is attributed to the Adham settlement (KSA-ST-01876) through the Census 2010 bridge in `screening/gastat_crosswalk.yaml`, not by a name match in the primary table. It replaces the universe's OSM tag 10,484 (official beats derived). Flagged for Opus (A-makkah-003).
2. KSA-ST-03308 (village, Al-Mahd node) is dropped: the universe carries Adham's 9,022 there through a pilot join, and the crosswalk leaves that figure unmatched (A-makkah-005). **Universe defect, for the coordinator:** `cities/ksa/zones/settlements.parquet` still holds the 9,022 on that node; fix it in the R1a/CP2 build, not here.
3. KSA-ST-00497 (Turabah node) is the same town as Turubah (relation 12429522, GASTAT 28,279): excluded as a duplicate with no population.
4. Al-Ardiyat: the governorate has no settlement row in the universe and no sourced seat town. The centre row uses the OSM boundary centroid (19.4348 N, 41.7021 E), excluded from the screen with the reason "seat town not located" (A-makkah-004).
5. Governorate names mapped from the universe spellings to the S-073 names (A-makkah-006).
6. Grid rows within 25 km of Makkah city are flagged in notes as possibly inside the official Makkah city figure (A-makkah-007). No value changed.
7. Rows where OSM gives a population but no year (one 5,000 tag) are not used: `pop_year` is required by the schema.
8. Distances: the R1a universe values (haversine to the located station, `dist_existing_km`, `dist_committed_km`, `dist_metro_km`), the OSRM minutes for road fields. Committed stations are unlocated, so `nearest_committed_station` is marked "site unlocated; approximate".
9. Governorate centres below 5,000 (Al Kamil) stay `screened` true with `tag_5k` false: the centre is kept, and the funnel decides.

**Open for Opus (full text in `docs/regions/makkah.md` section 6).** Adham identity; Al-Ardiyat seat; the grid rows near Makkah city (possible double count); 69 unmatched primary cities with no region (section 3 of the md); Thuwal and Al-Hawiyah governorate from snippets; KAEC giga-project and Rabigh port roles (governorate-level only); closely spaced grid rows (< 3 km apart, e.g. As Sayl as Saghir and Rayi' al-Dhiyab) that may be one locality (not merged); terrain.

**Checks run.**
- `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/makkah.parquet`: ok, 77 rows, 17 governorates (no warnings).
- `pytest tests/test_makkah_register.py`: 3 passed (strict validation; 15 official ≥ 10k rows present, no grid row passes; CSV mirror agrees).
- `ruff check` and `ruff format` on `screening/sweeps/` and `tests/test_makkah_register.py`: clean.
- `common.docver` `check_file` on the three Markdown files I own: pass. (The directory check `common.docver check docs` skips the worktree path: a known bug, see the pilot status.)
- `common.manifest verify` in this worktree: 279 FAIL, all "file missing" for gitignored data that exists only in the main checkout (`data/ksa/...` not present under the worktree). None concerns the R2 raw file, which is present and verifies. Not caused by this track; the coordinator should run `verify` from the main checkout.
- Full `pytest` (worktree): 5 errors or failures in 2 modules (`tests/test_costs_register.py`, `tests/test_cp2_gastat_primary.py`), all `FileNotFoundError` for gitignored raw files (`data/ksa/costs/...`, `data/ksa/pilot-qassim/raw/...`) that are not in this worktree. None concerns the R2 files; the R2 tests pass.

**Elapsed.** About 20 minutes wall clock (started about 16:15 +03, 31 Oct 2026), mostly reading the GASTAT outputs and the settlement universe.

10. Name candidates (verifier pass 1, F1): five unmatched primary cities carry a candidate on their row (Al Quoz: Alqawz 22,374; Ushayrah: Eshyrh 9,517; Ghran: Ghuran 6,803; Assel: Alsayl 6,064; Al 'Arfa: Aleurafa' 5,432). No value is changed: identity is open and the export has no region. Alqawz would replace the OSM tag 23,391 if confirmed; `tag_10k` stays true either way.

**Verifier.** Pass 1 (`docs/status/verify-REGION_MAKKAH.md`): FAIL on F1 (name candidates, decision 10) and F2 (the handoff: no status line, commit or cost row yet), plus three small items (literal `nan` cells in the Markdown table, a section 3 heading that contradicted the Adham row, the Al-Ardiyat caveat missing from the printed md). All fixed. Pass 2 (same file, "Pass 2"): PASS, no FAILs; both registers byte-identical on rebuild.

**Cost log.** No stream-json result file exists for this foreground run, so no row was added to `docs/cost-log.csv`.

REGION_MAKKAH: done
