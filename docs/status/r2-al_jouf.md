> **Document version:** docs/status/r2-al_jouf.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_AL_JOUF) | Status: draft

# Track `r2-al_jouf` — status

## REGION_AL_JOUF — full region sweep of Al-Jouf (الجوف), slug `al_jouf` — 31 Oct 2026

Built (worktree `r2-al_jouf`, branch `r2-al_jouf`, not pushed):
- `cities/ksa/regions/al_jouf.parquet` and `.csv`: **83 rows**, one per R1a settlement of the region, with the GASTAT primary population applied (CP2 P1a addendum 2). Header: `governorates_gastat = 4`, `governorates_listed = 4`.
- `screening/sweeps/al_jouf/build.py` (builds the register, deterministic, no random draws) and `report.py` (writes the Markdown table from the Parquet).
- `docs/regions/al_jouf.md` (generated table, counts, gaps, sources, Needs Opus judgement list; label "screening input, not a forecast").
- `docs/sources/r2-al_jouf.csv` (S-al_jouf-001 to -011; 001 to 009 copied from the pilot with `used_in` updated; -010 is the Ghata search log, -011 the filtered OSM extract).
- `docs/assumptions-r2-al_jouf.md` (A-al_jouf-001 to 007).
- `docs/licences-r2-al_jouf.md` and `.csv` (OSM ODbL, GASTAT use policy, WorldPop CC BY 4.0).
- Manifest: `al-jouf-osm-places-gcc` added to `cities/ksa/sources.yaml` (filtered place features, 7,082,323 bytes; gitignored under `data/ksa/al_jouf/raw/`).

Counts (from the register):
- Governorates: GASTAT **4** (primary export names: Sakaka, Al Qurayyat, Tubarjal, Dawamat Al Jandal) / listed **4**. Conflict flagged, not resolved: Wikipedia and Saudipedia say **3** (S-al_jouf-003, -004).
- Governorate centres with rows: **4**.
- Rows at or above 10,000 (`tag_10k`): **5** (all official, GASTAT primary, verified). Grid-only rows at or above 10,000, uncorroborated: **3** (`tag_10k` false, `screened` true, reason given).
- Rows at or above 5,000 (`tag_5k`): **21** (official 9, grid 12). **One official town is missing: Ghata (see Gaps).**
- Population basis: official 9 (`verified`); grid 74 (`unverified`, WorldPop 2020, `pop_corroboration` null for every row: no second method was run for any Al-Jouf grid row).
- Screened 21; excluded below 5,000 with no sourced economic role 62 (reason per row).
- Economic roles: 10 role entries on 4 towns (Sakaka: administrative, airport, university, industrial_city; Al Qurayyat: administrative, airport; Tubarjal: administrative; Dawamat Al Jandal: administrative, heritage, tourism). Every entry carries an S-id. Tubarjal has no sourced border-crossing role.
- Facts in the sources file: verified 3, secondary 6, unverified 2. GASTAT primary exports (S-cp2-gastat-007, -008) are `verified` in the index; S-cp2-gastat-005 (Census 2010) is used only for the 2010 check.

Decisions taken (each recorded in `docs/assumptions-r2-al_jouf.md` or the region doc):
1. OSM `place` population tags are not used as 2022 figures (A-al_jouf-004). Two are dated 2010 and equal the Census 2010 list: Al-Hadithah al-Qadimah 6,979 and Al-Isawiyah 5,629. R1a's `derived` rows for these had carried the 2010 values as current population; the register uses the grid instead. Three undated OSM tags (2,800; 2,400; 2,400) are also not used.
2. A town absent from the GASTAT 2022 table of cities of 5,000+ is presumed below 5,000 in 2022 (A-al_jouf-003). Applied to grid rows only: Al-Hadithah (grid 11,301), Al-Isawiyah (grid 15,474), An-Nasifah and other grid towns. The grid figure is shown and flagged, never written as a GASTAT value. The brief's rule for untabulated towns (include as `grid`, say so) is applied literally, so these rows stay visible.
3. Ghata is not placed: no located source (see Gaps). No coordinates were invented.
4. Terrain class is null on every row (A-al_jouf-002): no DEM read, disk gate.
5. Geo-verify `estimate` was **not run**: it downloads building footprints and Sentinel-2 windows (`screening/geo_verify/cli.py`), which the R2 disk gate forbids. The pilot's record-only GEO_VERIFY estimates for its 8 rows are carried in the notes (not applied to `population`). The region-sweep skill's "mandatory from 31 Oct" step is therefore **not done**; this is a deviation from the skill, and needs Tariq's call.
6. Distances: `dist_existing_km` is haversine to the nearest existing station (checked for Sakaka: 51.03 km to `sar-north-passenger:al-jawf`); road minutes are R1a OSRM free flow (S-r1a-809). Committed nearest is the Landbridge `dawadmi` stop or the GCC railway Kuwait border proxy (both unlocated in R1a); no committed line is called existing.
7. Ghata-name collision: the R1a match gave "Ghata" to Al Ghat (Riyadh, KSA-ST-01141), so the Al-Jouf town never matched. The R1a universe should be corrected at the next integration (not changed here: R1a is read-only for this track).

Gaps and blockers:
- **Ghata** (GASTAT Census 2022 city, **6,653**, Al-Qurayyat governorate; S-cp2-gastat-008; membership S-al_jouf-002) has no coordinates in any source reachable here: the local GCC extract has no object named Ghata in Latin or الغطا spellings (exact-name `osmium tags-filter`), but it does hold a village غطي / Ghutti (node 1236744649, Al-Qurayyat) that may be the same place; citypopulation.de writes Ghata as غطى (candidate, not confirmed); Nominatim returned nothing (8 queries: 2 unbounded, 6 bounded to the Al-Jouf box); Wikidata has no Saudi entry; Overpass was at capacity (HTTP 502) and was not retried further; the 2010 list has no Ghata. The acceptance criterion "sensitivity rows ≥ 5 000 are tagged" therefore fails by one town. Options for Tariq: (a) a located source (GASTAT locality table, or the Ghata coordinates from a source he is content to cite); (b) accept the gap and record it in the R2 summary; (c) allow a single fetch of a page that lists Ghata's coordinates (terms not checked, so not done without approval).
- Governorate count 3 vs 4 (above; Needs Opus judgement 1).
- Geo-verify step not run (deviation 5).

Checks run:
- `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/al_jouf.parquet` (run as `.venv/bin/python -m ...`, since `uv run` was slow to start in this shell): `ok al_jouf.parquet: 83 rows, 4 governorates`.
- Parquet and CSV agree: 83 rows each, same `name_en` order; no null `osm_id` or `lat`/`lon`.
- `ruff check screening/sweeps/al_jouf`: all checks passed; `ruff format` applied.
- `common.docver check docs`: OK, 102 files (run in this worktree).
- `common.manifest verify`: this worktree reports 279 FAIL lines, all for gitignored data files that are absent from the worktree (for example `data/ksa/benchmarks/wb_PA.NUS.FCRF.json`, `data/ksa/hhr/...`, `data/ksa/geo/...`). None names an Al-Jouf file; the new `al-jouf-osm-places-gcc` row is not in the failure list. These failures pre-date this sweep.
- `pytest`: not run; this sweep adds no tests (the builder is a deterministic script checked by the strict validator).

Elapsed: about 35 minutes of wall time (session start not recorded; status written 16:31 +03).

REGION_AL_JOUF: blocked - Ghata (GASTAT Census 2022: 6,653, Al-Qurayyat) has no confirmed located source; candidate node 1236744649 (غطي / Ghutti) needs an identity judgement; the ≥ 5,000 completeness check fails by one town until then; the register otherwise validates (83 rows, 4 of 4 governorates); geo-verify was not run (disk gate)
