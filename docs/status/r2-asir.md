> **Document version:** docs/status/r2-asir.md v1.2 | 31 Oct 2026 | Author: region-scout (r2-asir, REGION_ASIR) | Status: draft

# Status: r2-asir (REGION_ASIR)

## REGION_ASIR block, 31 Oct 2026

- **Governorates:** GASTAT 18 (primary TA1 governorate table, Asir rows, S-cp2-gastat-007; the 18 rows sum to 2,024,285, the same as the region total in S-soc-339 and S-asir-001). Listed in the register: 18, one centre row each. OSM has 17 Asir polygons (G015 to G031); Al Amoah has none (C-r1a-20). The discrepancy with OSM is recorded in `docs/regions/asir.md`; the register follows GASTAT.
- **Rows:** 37 (18 centres, 19 other towns, of which 1 screened out). Rows at or above 10,000 (`tag_10k`): 13 (12 official, verified; 1 derived OSM tag). Rows at or above 5,000 (`tag_5k`): 32. Grid-only towns at or above 10,000 held out by the gate: 3 (Masloom, Al Harayr, King Faisal Military City; no corroborating method run).
- **Sources and roles:** 9 economic roles on 4 towns, each with an S- id (Abha 4, Bisha 2, Khamis Mushait 1, Rijal Almaa 2). Terrain assessed for 1 row (Abha, secondary); the rest are null (no DEM extract; disk gate).
- **Facts:** populations verified 14 (primary GASTAT), secondary 5 (2 citypopulation relays, 3 OSM tags), unverified 18 (WorldPop grid, S-asir-012). Every official figure from the primary table is asserted equal to the table value by the build script; a mismatch fails the build.
- **Corrections to the pilot (docs/status/pilot-asir.md):** the Balqarn centre (osm 11891866421) is in Makkah and is replaced by Sabt Al 'Alayah (containment, Balqarn polygon); the Al Harajah node in the Balqarn polygon is screened out; the Al Harjah seat (KSA-ST-01075) is set by containment; Tanumah carries the primary figure 12,442 (GASTAT spells it Tanawma).
- **Correction during verification (31 Oct 2026):** an earlier build set Tanumah to null, rejecting the R1a universe's 12,442 as Tathlith's Saudi count. The red-team verifier (first run, FAIL F1) found the primary city table row `Tanawma | 12,442`; the rejection was wrong. Fixed in `build_register.py`, `render_doc.py` and A-asir-003; rebuilt and re-validated.
- **Needs Opus judgement (not resolved; listed in `docs/regions/asir.md`):** Al Harjah seat; Al Amoah seat (no polygon); Balqarn seat population (OSM 200,000 rejected, WorldPop 7,594 used); Rijal Almaa seat (grid 288); three OSM-tag towns not in GASTAT's 5k table (Al Bashaer, Tabalah, Shawas); Bisha mining (exploration only); Khamis Mushait military (secondary); terrain for 36 rows; unsourced MODON Asir. The heading "Needs Opus judgement" follows `prompts/REGION_ASIR.md`; the verifier asked the coordinator to waive or rename it.
- **Assumptions:** A-asir-001 to A-asir-005 in `docs/assumptions-r2-asir.md` (method choices, all `assumed`); A-screen-001/002/031/032/033/037/039 and A-r1a-027 applied as registered.
- **Files:** `cities/ksa/regions/asir.parquet` (header keys `governorates_gastat` = 18, `governorates_listed` = 18), `cities/ksa/regions/asir.csv`, `docs/regions/asir.md`, `docs/assumptions-r2-asir.md`, `docs/sources/r2-asir.csv` (S-asir-001, 003 to 014; there is no S-asir-002), `screening/sweeps/asir/` (build_register.py, render_doc.py), `tests/test_region_asir.py`, `docs/status/verify-REGION_ASIR-run1.md` (first verifier run, FAIL F1 now fixed) and `docs/status/verify-REGION_ASIR.md` (second run, after the fix).
- **Datasets:** no new download. Inputs are the R1a settlement universe, the R1a economic nodes, the primary GASTAT exports already in `cities/ksa/sources.yaml`, and the OSM, WorldPop and GASTAT rows already registered. No licence file added (no new dataset or model).
- **Checks run (31 Oct 2026, after the Tanumah fix):**
  - `screening.region_sweep validate --strict cities/ksa/regions/asir.parquet`: ok, 37 rows, 18 governorates.
  - `ruff check` and `ruff format --check` on `screening/sweeps/asir/` and `tests/test_region_asir.py`: clean (file-level `# ruff: noqa: E501`, the repo's convention for prose-heavy builders).
  - `pytest tests/test_region_asir.py`: 3 passed.
  - `common.docver check docs/regions/asir.md docs/assumptions-r2-asir.md`: OK (2 files).
  - Full `pytest`: 2 failed, 3 errors, all `FileNotFoundError` on gitignored raw data missing from this worktree (`data/ksa/costs/wb_NY.GDP.DEFL.ZS.json`, `data/ksa/pilot-qassim/raw/citypop_admin.html`). Not caused by this track.
  - `common.manifest verify`: 279 FAIL lines, all `file missing` (the rows are gitignored raw data, for example the pilot-eastern nominatim files, that exist in the main checkout but not in this worktree, which holds only `data/ksa/tables/`). No row fails on a hash. Not caused by this track; the coordinator should run verify from the main checkout. An earlier note of four failures was a `tail -4` artefact.
- **Verification:** first red-team run (31 Oct 2026, read-only) returned FAIL on F1 (Tanumah, fixed above), F2 (status form: missing final line and elapsed figure; fixed in v1.2), F3 (the "Opus" heading, prescribed by the prompt; left as is), and F4 (uncommitted work, resolved by the commit after re-verification). Second run: `docs/status/verify-REGION_ASIR.md`.
- **Elapsed:** not measured (the run has no timer; the two verifier runs took about 6 and 6 minutes of wall time each).

REGION_ASIR: done
