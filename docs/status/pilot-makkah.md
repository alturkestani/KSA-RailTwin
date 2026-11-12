> **Document version:** docs/status/pilot-makkah.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_MAKKAH) | Status: draft

# Status: pilot-makkah (track `pilot-makkah`, milestone `PILOT_REGION_MAKKAH`)

## PILOT_REGION_MAKKAH: pilot sweep, Makkah region (coarse) — 30 Oct 2026

**Outputs.** `cities/ksa/regions/pilot-makkah.parquet` and `.csv` (18 rows each, same OSM ids), `docs/regions/pilot-makkah.md`, `docs/assumptions-pilot-makkah.md` (A-screen-pilot-001 to 003), `docs/sources/pilot-makkah.csv` (S-makkah-001 to 007).

**Counts (measured).**
- Rows: 18 in the Parquet (validated with `common.schemas.load_region_register`: passes). 16 of them are governorate centres; 2 are non-centre settlements (Al-Ḥawiyah, Thuwal).
- Governorates: `governorates_gastat` **not found (null)**; `governorates_listed` **17** (S-073; S-makkah-001). Rows cover **16 of 17**. Al-Ardiyat is withheld (no coordinates; `RegionRow` requires lat/lon).
- Towns ≥ 50,000 (secondary): **6** (Makkah, Jiddah, Aṭ-Ṭa'if, Al-Ḥawiyah, Rābigh, Baḥrah). In the CSV `threshold_50k` only.
- Stratified sample: **5** rows with `pilot_sample: true` and a reason each (Al-Jumūm, Thuwal, Khulaīṣ, Al-Khurmah, Al-Qunfudhah).
- Coordinates: 12 from OSM place nodes, 6 from OSM boundary centroids (Makkah, Adam, Al-Līth, Al-Qunfudhah, Turubah, Rābigh; A-screen-pilot-003).
- Populations: 17 set, all **secondary** (citypopulation.de, credits GASTAT; S-makkah-001). 1 null (Maysān: OSM place with no census place row).
- Terrain: 0 assessed (null everywhere). Road minutes: none (R1a skims). Committed-line distances: none (no published coordinates).

**Facts: verified / secondary / unverified.**
- Verified: OSM ids and coordinates for the 18 rows (Nominatim, 30 Oct 2026; ODbL). HHR station positions (OSM nodes 10956967098, 2147398509, 7227897402).
- Secondary: all 17 populations (S-makkah-001; S-073 for the 17-governorate count). Thuwal's KAUST role (S-makkah-003, search snippet, not fetched). Thuwal in Jiddah Governorate (S-makkah-004, snippet).
- Unverified: GASTAT's own governorate count (S-072, S-090). Thuwal's governorate in the citypopulation list (not checked). Al-Ḥawiyah's governorate (OSM says Taif; not checked). Al-Jumūm as the Landbridge "Jumoum" stop (owner-identified S-063; no published location). No Al-Qunfudhah port role (S-makkah-007).
- Conflict: the citypopulation region row says 7,769,994, but its 17 governorate rows sum to 8,021,463 (= GLMM and Monshaat; S-079). The governorate rows are used; the conflict is noted, not resolved.

**Elapsed.** About 15 minutes wall clock (21:05 to 21:20, +03), mostly web lookups. Overpass returned 502 at capacity, so OSM was queried through Nominatim only.

**Decisions taken (recorded here, per the prompt's "decide and record").**
1. Parquet follows `common/schemas.py:RegionRow`, not the prompt's field names (`dist_existing_km` not `dist_km_existing`, etc.). Mapping in `docs/regions/pilot-makkah.md` section 6.
2. Secondary populations are null in the Parquet (`pop_type` cannot be `secondary`: see Opus item 1). They sit in the CSV (`population_secondary`) with `S-makkah-001`. No value is labelled official or derived.
3. Al-Ardiyat is withheld from both Parquet and CSV (parquet and CSV must agree), and listed as withheld in the Markdown.
4. The Jiddah distance uses the KAIA airport station (12.2 km); the Jeddah central station (Al-Sulaymaniyah) was not located, so the figure is overstated for the city.
5. `dist_existing_km` is distance to the nearest located HHR station, not to the alignment (A-screen-pilot-002).
6. `screening.region_sweep` does not exist in this worktree (`screening/cli.py` is the R0 skeleton). The Parquet was written with pandas against `RegionRow`. The build script is `/tmp/pilot_makkah/build.py`, not committed (no pilot-owned path; the coordinator can move it into `screening/` if wanted).

**Needs Opus judgement** (full text in `docs/regions/pilot-makkah.md` section 8).
1. **Schema gap:** `RegionRow.pop_type` has no `secondary` value, so the Parquet cannot carry population or tags. Recommendation: add `secondary` to the Literal in `common/schemas.py` (shared code; outside the additive-only rule, so not done here).
2. GASTAT governorate count unverified (secondary only: 17).
3. Al-Ardiyat: no coordinates; needs an OSM place node.
4. Thuwal and Al-Ḥawiyah governorate assignment.
5. Al-Jumūm committed-stop identity (owner-identified; not a layer until sourced).
6. Economic roles: only Thuwal has a sourced role; empty means "not assessed", not "none".
7. Terrain: DEM not read; `RegionRow.terrain_class` cannot record `assumed` with an assumption id.

**Other things found (not fixed: outside this track).**
- `common/docver.py` `iter_md` skips every file when the repo path contains `.worktrees` (its filter tests `".worktrees" in f.parts`, and the worktree's own path has that segment). `uv run python -m common.docver check docs` reports "0 files" in any worktree. Checked my files with `check_file` directly: both pass.
- Licence register: no rows written (`docs/licences-pilot-makkah.*` is not in this track's ownership list). Needed: OSM (ODbL, Nominatim and OSM data) and citypopulation.de (terms not checked).
- Overpass API (`overpass-api.de`) returned 502 at capacity; the local GCC PBF (`data/osm/gcc-states-latest.osm.pbf`, read-only symlink) was not read.

**Next (for the coordinator).** Decide Opus item 1 (the schema). Then R1a should: find GASTAT's primary tables, read the PBF for `place=*` and HHR stations, run road skims, and assign DEM terrain.

PILOT_REGION_MAKKAH: done
