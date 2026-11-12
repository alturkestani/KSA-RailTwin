> **Document version:** docs/status/r2-northern_borders.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_NORTHERN_BORDERS, R2) | Status: draft

# Track `r2-northern_borders`: status

## REGION_NORTHERN_BORDERS (Northern Borders, slug `northern_borders`)

**Outputs:** `cities/ksa/regions/northern_borders.parquet` and `.csv` (57 rows); `docs/regions/northern_borders.md`; `docs/assumptions-r2-northern_borders.md` (A-northern_borders-001…005); `docs/sources/r2-northern_borders.csv` (header only: no new source ids, all 19 cited ids resolve in `docs/sources/index.csv`); scripts in `screening/sweeps/northern_borders/` (`build.py`, `write_docs.py`).

**Counts (from the register, reproduced in the note):**

- Governorates: `governorates_gastat` 4, `governorates_listed` 4 (Arar, Rafha, Turayf, Al Uwayqilah; GASTAT TA1 primary, S-cp2-gastat-007). Their totals sum to 373,577, equal to the TA1 region total.
- Rows: 57 (every settlement in the R1a universe for the region). Screened 8; excluded 49, each with a reason.
- Population ≥ 10k tagged: 4 (Arar 199,247; Rafha 63,929; Turayf 61,395; Al-Uwayqilah 17,055; all primary, `verified`). Grid-only ≥ 10k not tagged: 2 (Linah 17,616; Badanah 10,670; uncorroborated, A-screen-032).
- Population ≥ 5k (`tag_5k`, sensitivity): 7 (the four above, Rawdat Habbas 5,620 primary, and Linah and Badanah as grid).
- Rows with a sourced economic role: 5 (Arar: airport, university, border post, industrial city; Rafha and Turayf: airport; Al-Uwayqilah, Arar, Rafha, Turayf: governorate seat; Hazm al Jalamid: mining).
- Facts status: 5 verified (GASTAT primary); 2 secondary (citypopulation.de, S-northern_borders-001: At Timyat, Ash Shu'bah); 27 grid gap-fills unverified (S-r1a-506).

**Decisions taken (recorded here, not in chat):**

1. Rows: all 57 R1a universe rows for this region, so nothing is silently dropped. Rows below 5k or with no figure are kept with `screened: false` and a reason. One Arabic-only duplicate (هجرة ابن بكر) is excluded as a duplicate of Ibn Bakr.
2. Population: GASTAT primary first, then the relayed secondary figure, then WorldPop as a gap-fill only. Grid rows are never corroborated in this sweep (no second method run; the buildings × occupancy estimator is record-only after its back-test, and the 2010-growth check has no entry for Linah or Badanah). A grid cell sum of zero is recorded as no population (Jadidat Arar).
3. Governorate totals are not used as populations (the centres carry the locality figure).
4. Distances follow R1a's definitions: `dist_existing_km` is to the passenger stations (A-r1a-008), road minutes from the OSRM car skim (S-r1a-809, free flow, uncalibrated). The alignment distance to any existing line (which includes the SAR North freight line, S-019) is shown in the note's changes table only; the schema has one existing-line field.
5. Terrain is assumed (A-northern_borders-001: `dunes` for Rafha, otherwise `flat_desert`). No DEM run in this sweep.
6. The stray characters in the universe name "`Ar`ar" are corrected to Arar (noted on the row). Al-Uwayqilah is written with its GASTAT spelling (name_en).
7. Economic roles attach to a town only when the R1a node names it (A-northern_borders-003). Waad Al-Shamal (MODON) and Al-Haditha (Jordan post) have no row and are referred to Opus.
8. Hazm al Jalamid: the R1a mining node sits on the mine polygon, about 30 km from the village point used for the row. Kept as in R1a and flagged. The freight line (S-019) is 14.2 km from the row, which matches the pilot.

**Facts verified / secondary / unverified:** verified: 5 (S-cp2-gastat-008 primary city figures; identical to the relayed S-cp2-gastat-001 for those five). Secondary: 2 (S-northern_borders-001). Unverified: 27 grid figures (S-r1a-506). Still not reached: the GASTAT locality table (portal unreachable on 30 Oct 2026, S-090), which is the primary for every place below 5,000.

**Checks run:**

- `screening.region_sweep validate --strict cities/ksa/regions/northern_borders.parquet`: ok, 57 rows, 4 governorates.
- CSV mirror and Markdown tables are generated from the Parquet (`write_docs.py`), so they agree.
- `ruff check` and `ruff format --check` on `screening/sweeps/northern_borders/`: clean. Long prose lines carry `# noqa: E501`, as in `scripts/register_gastat_tables.py`.
- `common.docver check docs`: OK, 101 files.
- Pytest (register, schema, source-id, pilot, network-zone and CP2 population-basis tests): 90 passed. Not run here: `test_costs_register.py` and `test_cp2_gastat_primary.py` need gitignored inputs (`data/ksa/costs/wb_NY.GDP.DEFL.ZS.json`, `runs/gastat/…`) that are absent from this worktree; they are outside this track.

**Open items for Opus (listed in `docs/regions/northern_borders.md`, "Needs Opus judgement"):** Linah and Badanah (grid against the ≥ 5k list); Jadidat Arar (2010 city 5,125, absent from 2022 list); Ash Shu'bah (secondary vs grid); Hazm al Jalamid point; Waad Al-Shamal and Al-Haditha nodes; the Arar border post; the SAR North passenger `existing` status (S-017); 69 unmatched primary cities with no region column (NB-plausible: Albadie Walqarfi 8,623, Aleuruq Alshamalia 5,783).

**Geo-verify step (mandatory): not run on the R2 rows.** `screening/geo_verify/cli.py` globs only `cities/ksa/regions/pilot-*.parquet` (`REGISTERS`), so `estimate --which no-pop --region northern_borders` would select pilot rows, not this register. Its footprint and raster inputs (`data/ksa/geo/…`) exist only in the main checkout. Fixing it needs a change outside this track's ownership (add `northern_borders.parquet` to `REGISTERS`, and a data path for the worktree), or a run from the main checkout. The pilot's geo-estimates for the same OSM objects are recorded in `docs/regions/pilot-northern_borders.md` (record-only; they never enter `population`).

**Elapsed:** about 15 minutes (16:15 to 16:30 Asia/Riyadh, approximate).

R2 region sweep, Northern Borders: the register, note, assumptions and scripts are complete and valid; the geo-verify step is the one mandatory step not run.

REGION_NORTHERN_BORDERS: blocked - geo-verify estimate (`--which no-pop`) not run on the R2 rows: `screening/geo_verify/cli.py` reads only `pilot-*.parquet` registers and its footprint and raster inputs exist only in the main checkout; needs a CLI change (or a run from the main checkout). Register, validation and all other outputs are complete.
