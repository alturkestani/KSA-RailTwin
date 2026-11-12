> **Document version:** docs/status/r2-eastern.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_EASTERN) | Status: draft

# Status: r2-eastern (REGION_EASTERN)

## REGION_EASTERN (31 Oct 2026)

**Outputs:** `cities/ksa/regions/eastern.parquet` and `eastern.csv` (57 rows), `docs/regions/eastern.md`, `docs/assumptions-r2-eastern.md` (A-eastern-001 to 009), `docs/sources/r2-eastern.csv` (S-eastern-101 to 103), `screening/sweeps/eastern/build.py` (the builder; regenerates all three outputs from the R1a inputs).

**Counts**
- Governorates: `governorates_gastat` = 12 (GASTAT primary export, S-cp2-gastat-007); `governorates_listed` = 12; the 12 GASTAT governorate totals sum to 5,125,254 = the regional total. Discrepancy written both ways: Saudipedia Arabic lists 13 (Al-Bayda), not in the GASTAT list; Al-Bayda is an excluded row.
- Rows: 57 (12 governorate centres; 45 towns at or above 5,000 or other rows; 4 excluded).
- Towns at or above 10,000 (`tag_10k`): 29 = 28 official (GASTAT primary, verified) + 1 derived (AL THIYBIA, OSM tag, secondary). Grid rows at or above 10,000: 6, all uncorroborated, so `tag_10k = false`.
- Towns at or above 5,000 (`tag_5k`): 51.
- Economic roles: 27 role entries on 11 rows, each with a source (R1a economic nodes, plus two pilot search-extract roles: military).

**Facts, by status**
- *Verified:* the 34 official rows (population read from the primary GASTAT city export, S-cp2-gastat-008 / governorate export S-cp2-gastat-007); the governorate count (150-row GASTAT list); coordinates and osm ids (R1a universe, OSM ODbL).
- *Secondary:* 5 OSM-tag towns (`derived`, all dated, all at or above 5,000: AL THIYBIA, As Saffaniyah, Bani M'en, Mulayjah, Al Marah); the Saudipedia 13-governorate count (S-eastern-003); the military roles (S-eastern-001, S-eastern-009).
- *Unverified:* the 12 grid rows (WorldPop 2020, `pop_type: grid`); Al-Udayd and Al-Bayda centres (no sourced town figure); terrain class (not classified for any row).

**Measured**
- Distances: haversine to the nearest station and the metro reference node (R1a); OSRM car road minutes for every row with an R1a skim (all except the Al-Jubail (Al-Ahsa) row, which uses the pilot's haversine and has no road minutes).
- Validation: `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/eastern.parquet`: ok, 57 rows, 12 governorates, no warnings. Parquet and CSV agree (names and populations, same row order). The Markdown table has 57 rows.
- Lint: ruff check and format clean on `screening/sweeps/eastern/build.py` (E501 waived at file level for the prose writer).
- Docs: `common.docver.check_file` passes on `docs/regions/eastern.md` and `docs/assumptions-r2-eastern.md`.
- Manifest: no new raw data was downloaded, so `cities/ksa/sources.yaml` is unchanged.

**Geo-verify step (partial; record-only)**
- `screening.geo_verify.cli estimate --which no-pop --region eastern --seed 1` ran (log `logs/r2-eastern-geo-estimate.log`, gitignored). **It read the pilot register only:** the CLI globs `cities/ksa/regions/pilot-*.parquet` (`screening/geo_verify/cli.py:35`, not changed here: shared code). The pilot rows it evaluated map to this register as: Ras Tanura (estimate 22,923, range 7,013–39,756; record-only; the R2 row keeps 57,030), Al-Udayd (no footprint cluster), Al-Bayda (no footprint cluster). Neither estimator passes the back-test gate, so nothing was written to `population`.
- To re-run for R2: the CLI needs `REGISTERS` to include `eastern.parquet`, plus `data/ksa/geo` and `data/ksa/grids` present in the worktree (gitignored, not copied here) and `--backtest-dir` pointing at the back-test run. Coordinator decision needed on the CLI change.

**Decisions taken (all recorded in the assumptions file and in docs/regions/eastern.md §9)**
- Al-Hofuf row kept combined (430,105 + 299,501), as the crosswalk and pilot did (A-eastern-002).
- Duplicate and excluded nodes: KSA-ST-03116, KSA-ST-07366, KSA-ST-00817 (A-eastern-003).
- Undated OSM-tag population (Nuqayrah node, 5,000) not used (A-eastern-005).
- Al-Jubail (Al-Ahsa, 9,994): the primary figure with the pilot's coordinates (A-eastern-007).
- Rahimah (57,030 in the primary export) matched to the Ra's Tannurah row (crosswalk).

**Could not verify / not done**
- The 12 grid rows have no second method run, so none can enter `tag_10k`.
- Terrain class: null for every row (no R1a DEM class for Eastern towns; not guessed).
- Committed distances use unlocated GCC railway station positions (R1a flag): labelled committed, approximate.
- Opus items 1 to 11 in docs/regions/eastern.md §9 are open (Al-Bayda status, Al-Hofuf split, Rahimah, Al-Jubail location, OSM-tag towns, Thuqbah in the metro, military roles, terrain, Al-Udayd, roles schema).
- `common.docver check docs` reports 0 files in this worktree (the walker drops paths containing `.worktrees`, the bug the pilot noted in common/docver.py); each file was checked individually.
- Elapsed time: not measured.

REGION_EASTERN: done
