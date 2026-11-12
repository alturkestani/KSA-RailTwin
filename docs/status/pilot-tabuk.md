> **Document version:** docs/status/pilot-tabuk.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_TABUK) | Status: draft

# Track status: pilot-tabuk (PILOT_REGION_TABUK)

## PILOT_REGION_TABUK — 30 Oct 2026

**Result:** register written and validated (9 rows). Governorate count unresolved, flagged with both sources. Verifier not run (pilot, not a milestone; the coordinator decides whether a red-team pass is needed before R2).

### Measured
- Rows written: **9** (`cities/ksa/regions/pilot-tabuk.parquet` and `.csv`, identical ids). Seven governorate centres, Bi'r Ibn Hirmas (4,964; screened out, 5k-boundary check), Hala Ammar (governorate unresolved; screened out).
- Governorates: **GASTAT count not verified** (portal unreachable, S-072/S-090). Listed = **7** (6 governorates + the seat; S-tabuk-001, -003, -004). Wording count = 6 (+ seat). Hala Ammar may make 8. Flagged, not resolved.
- Towns ≥ 50,000: **1** (Tabuk city, 594,350; S-tabuk-002). Umluj's town figure is 46,229 (its governorate is 69,656).
- Sample: **5** rows with `pilot_sample: true` (Umluj, Duba, Tayma, Haql, Al-Bad'), each with a reason in `notes`. Near (<25 km) stratum empty for this region.
- Population checks: the seven governorate totals sum to 886,036, equal to the region total (S-tabuk-016).
- Acceptance gap (not met as written): the prompt requires `pop_source`, `pop_year` and `pop_type` on every row. Hala Ammar (`screened = false`) has none, because it has no census population. It is kept as an unresolved row so no unit is silently dropped. The other eight rows meet the rule.
- Sources: 21 rows in `docs/sources/pilot-tabuk.csv`. Primary 2 (OSM; UNESCO snippet). Secondary 13. Unverified 6 (one 404; three conflicting or snippet-only claims not used for values). GASTAT primary figures: none.
- Validation: `common.schemas.load_region_register` passes 9/9; Parquet and CSV both 9 rows with the same ids; the Markdown table is generated from the Parquet.
- Elapsed: about 11 min of wall-clock (system clock 21:22 to 21:33 on the worktree files; the research and build ran inside that window).

### Deviations from the prompt (decided, reason recorded)
1. **`screening/region_sweep` does not exist** in this worktree (`screening/` has only the R0 skeleton). The register is written by `cities/ksa/regions/pilot-tabuk_build.py` and validated against `common.schemas.RegionRow`. The `validate` command in the prompt is not available. Reason: the module is R2 work, outside this track's ownership.
2. **Schema field names:** the prompt's names (`dist_km_existing`, `terrain_class` values `sand_dunes` and `coastal_plain`) do not match `RegionRow`. The register uses the schema's names and values (`dist_existing_km`, `dunes`, `coastal`, `mixed`). Reason: `extra="forbid"` would reject the prompt's names.
3. **`common/schemas.py` changed (additive, coordinator to approve at integration):**
   - `pop_type` accepts `secondary` (the prompt's rule for secondary aggregators; without it the register could only say `official`, which is false here).
   - New optional fields with defaults, so existing rows still validate: `primary_to_find`, `threshold_50k`, `pilot_sample`, `nearest_metro_tier`, `distance_method`, `road_min_method`, `terrain_source`, `notes`.
   - Reason: the prompt requires `threshold_50k`, `pilot_sample` and the method on each distance. None of them has a column in `RegionRow`.
4. **Distances:** haversine to the nearest OSM rail vertex after 0.5 km densification (A-screen-pilot-001). Road minutes null (`pending R1a skims`), as the prompt asks.
5. **Terrain:** assumed by governorate (A-screen-pilot-terrain-001). No DEM read: no Copernicus or SRTM tile was downloaded (disk and download gate).
6. **Metro nodes pinned by OSM id** (not name): OSM `name` tags are mostly Arabic and the English forms sit in `alt_name`, so name matching failed for Taif.

### Assumptions added (`docs/assumptions-pilot-tabuk.md`)
- A-screen-pilot-001 (distance method), A-screen-pilot-terrain-001 (terrain classes), A-screen-pilot-002 (settlement population level). A-screen-001, -002 and -013 reused unchanged.

### Licences added (`docs/licences-pilot-tabuk.md` and `.csv`)
- OSM ODbL: share-alike question on a derived extract is open (flagged, not resolved).
- citypopulation.de, datasaudi, CruiseMapper and the UNESCO page: terms not read; facts only, flagged.

### Needs Opus judgement
1. **Governorate count** (6 / 7 / 8 incl. Hala Ammar). Confirm against GASTAT's own table before R2 (S-072 unresolved).
2. **Hala Ammar:** governorate or centre? No census population; row kept, screened false.
3. **NEOM rail layer.** "The Spine" and the Neom Connector are announced; a snippet reports the Neom Connector contract was ended (S-tabuk-018, unverified). The layer rule has no place for an announced, unprocured line. Options: `committed` only with procurement evidence, or left out until sourced. Not assigned here.
4. **Historic Hejaz line** (OSM `abandoned`/`disused`, within 2 km of Tabuk city): recorded in notes, not counted as existing. The Layer literal has `historical` but `RegionRow` has no field for it.
5. **Umluj's nearest metro is Madinah** (tier 1, 245 km), not Tabuk (381 km). Nearest-by-distance follows A-screen-013 as written. Confirm whether the Tabuk tier should cover Umluj.
6. **Population level** (A-screen-pilot-002): settlement, not governorate. Umluj does not clear 50k on its town figure (46,229); on the governorate figure (69,656) it would.
7. **Empty near stratum:** no 5k–50k town within 25 km of any existing line; no sourced committed line in the region.
8. **Terrain** needs a DEM pass in R1a (replaces A-screen-pilot-terrain-001).
9. **OSM share-alike** for any published derived extract (licence flag 1).

### Not done (named so the coordinator can decide)
- No GASTAT primary figure (portal unreachable on 2026-10-30).
- The Tabuk municipality page (S-tabuk-005) returned 404: its governorate list was not read.
- Settlements below 5,000 except Bi'r Ibn Hirmas are not registered (six census-listed places; the OSM ids for three of them were not matched). R2 should register them with OSM ids.
- Road skims, DEM terrain, Copernicus data: out of scope for the pilot and blocked by the disk gate.
- Verifier (`red-team-verifier`) not run: this is a pilot, not a milestone.

### Checks run
- **docver, a defect:** `uv run python -m common.docver check docs` reports `OK: 0 files` inside any worktree. `iter_md` skips every path containing `.worktrees`, and the worktree's own root contains that segment, so the walk returns nothing and the check passes vacuously. Not changed here (`common/docver.py` is shared code). Reported to the coordinator. Workaround used: the same `check_file` run on every `docs/**/*.md` file: 20 files, 0 problems.
- `ruff check` and `ruff format --check` on `common/schemas.py` and the builder: clean.
- `pytest -q`: all tests pass (after the `common/schemas.py` change).
- Register: `load_region_register` validates 9/9; Parquet and CSV agree; the docs table matches the Parquet row for row, except the Hala Ammar screened cell, which shows a short label (full text in `exclusion_reason`).

### Handoff
- Commit: `feat(screening): pilot sweep tabuk` on branch `pilot-tabuk`. Nothing pushed; no tag.

`PILOT_REGION_TABUK: done`
