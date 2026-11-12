> **Document version:** docs/status/pilot-eastern.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_EASTERN) | Status: draft

# Status: pilot-eastern track

## PILOT_REGION_EASTERN: Eastern Province coarse pilot sweep (30 Oct 2026)

**Run by:** the coordinator session on the `pilot-eastern` worktree, not a separate Haiku region-scout process (the prompt's model was not used for this run). Research and build, no real-world action (rule 7): nothing was sent, posted, signed up for or paid for.

**Rows written:** 22 in `cities/ksa/regions/pilot-eastern.parquet` and `.csv` (same rows, same order). Parquet metadata carries `governorates_gastat` and `governorates_listed`.

**Governorates:** GASTAT count **not verified** (`governorates_gastat: null`; S-072, S-090). `governorates_listed: 13` (12 census-credited, plus Al-Bayda flagged as conflicting). The 13-vs-12 discrepancy is flagged with both sources in `docs/regions/pilot-eastern.md` §1. Evidence for 12 census units: the 12 census governorate rows sum exactly to the regional total (5,125,254).

**Towns at or above 50,000:** 12 (E01–E12; Raḥīmah probably overlaps Ras Tanura, not summed).

**Pilot sample:** 5 rows with `pilot_sample: true` (E13 Abqaiq, E19 Al-Oyun, E20 Al-Jubail in Al-Ahsa, E21 Al-Qaisumah, E22 King Khalid Military City), each with its reason in `docs/regions/pilot-eastern.md` §5. Near-with-sourced-enum-role is not represented.

**Facts, by status**
- *Verified:* 13 regions (S-070); GASTAT portal unreachable on 30 Oct 2026 (S-090); the citypopulation.de Eastern page carries the GASTAT source line (S-eastern-001, page level); OSM object ids and coordinates (S-eastern-004, objects checked per row); the East line station list (S-025, existing).
- *Secondary:* every population (citypopulation.de, S-eastern-001), corroborated by Wikipedia (S-eastern-002, Dammam differs by 505 persons and Khafji uses a different row); the Eastern governorate count in Saudipedia Arabic (S-eastern-003); all economic roles (search extracts, S-eastern-005 to 012; UNESCO page returned 403 to a direct fetch, so S-eastern-006 is a search extract only).
- *Unverified:* the GASTAT governorate count; Ras Tanura's town population; Al-Udayd's location (OSM point near the Qatar border); the Al-Bayda centre; GCC railway alignment coordinates; the terrain class of every row.

**Measured**
- Distances: 22 rows computed with haversine to station points (`dist_existing_km`, A-screen-pilot-001/002) and to metro reference nodes (`dist_metro_km`, A-screen-pilot-003). Committed-line distances: 0 computed (no coordinates). Road minutes: 0 (pending R1a).
- Validation: every row built as `RegionRow` before writing and again after reading the Parquet back: **22/22 pass**. Parquet and CSV agree on names, governorates, coordinates and population for all 22 rows. The Markdown table (generated from the Parquet) has 22 rows in the same order. Every row with a population has `pop_source`, `pop_year`, `pop_type`. No committed distance is set. Only E18 is `screened = false`.
- Docs: the four new `.md` files pass `common.docver.check_file` individually (OK). `common.docver check docs` reports **0 files** in this worktree: its directory walk drops every path containing `.worktrees`, and this worktree's own path does (bug in shared `common/docver.py`, not fixed here because `common/` is additive-only; for the coordinator).
- Manifest: `common.manifest verify --manifest cities/ksa/sources.yaml --root .`: **OK, 9 rows** (five new raw extracts added under `data/ksa/regions-pilot/`, gitignored; SHA-256 recorded in the manifest).
- Elapsed time: not measured.

**Could not verify / not done**
- `uv run python -m screening.region_sweep validate`: **not run**. The module does not exist in this worktree (`screening/` is the R0 skeleton, owned by the screening track). Validation used `common/schemas.py:RegionRow` directly, as the brief allows.
- Overpass (rail alignments and place nodes) was unavailable (HTTP 502, server at capacity). The GCC PBF was not parsed (no OSM reader installed; adding one would change `pyproject.toml`).
- The GASTAT Census 2022 portal could not be reached.

## Schema findings (for Opus judgement; not changed in common/)
- `RegionRow.pop_type` allows only `official`, `derived`, `grid`. The brief's `secondary` was **not** added to the schema (shared file; the additive-only rule applies). The register uses `official` with the source row marked secondary.
- Brief field names differ from `RegionRow` (`dist_km_existing` vs `dist_existing_km`, etc.). The brief's extra fields (`threshold_50k`, `pilot_sample`, `notes`, `primary_to_find`, `road_min_method`, `nearest_metro_tier`) do not exist in `RegionRow`, which forbids extra fields. They are carried in `docs/regions/pilot-eastern.md`, not in the Parquet or CSV.
- `EconomicRoleName` has no energy role (Abqaiq oil processing; Ras Tanura refinery).
- The brief's `coastal_plain` terrain value is `coastal` in the schema. No terrain class was assigned (null), because no geography source consulted classifies these settlements.
- `RegionRow` has no `id` column; the id in the Markdown is the row order.

## Assumptions added
A-screen-pilot-001 (haversine), -002 (station points, not alignments), -003 (metro reference nodes), -004 (citypopulation.de census values, secondary), -005 (merged Hofuf place). Registered in `docs/assumptions-pilot-eastern.md` (approval pending CP1).

## Licences added
`docs/licences-pilot-eastern.md` and `.csv`: OpenStreetMap (ODbL, open, commercial allowed); citypopulation.de (**unclear**: terms not read; must not feed a redistributed dataset); Wikipedia (CC BY-SA 4.0, figures only); Saudipedia (**unclear**); search-extract press and staff pages (terms not checked).

## Needs Opus judgement (summary; full list in docs/regions/pilot-eastern.md §10)
1. Governorate count 12 or 13 (Al-Bayda). 2. `pop_type`: `secondary` in the schema or a GASTAT primary first. 3. Raḥīmah vs Ras Tanura. 4. Ras Tanura town population. 5. Al-Udayd location. 6. Al-Bayda centre. 7. Hofuf and Al-Mubarraz merged. 8. Jubail includes the industrial city. 9. King Khalid Military City as a settlement. 10. Energy role. 11. Schema field-name and extra-field gaps. 12. Metro inclusion (R2). 13. Dammam station node address. 14. GCC alignment coordinates. 15. Terrain (R1a DEM).

## Handoff
Files: `cities/ksa/regions/pilot-eastern.parquet`, `cities/ksa/regions/pilot-eastern.csv`, `docs/regions/pilot-eastern.md`, `docs/assumptions-pilot-eastern.md`, `docs/licences-pilot-eastern.md`, `docs/licences-pilot-eastern.csv`, `docs/sources/pilot-eastern.csv`, `docs/status/pilot-eastern.md`, `cities/ksa/sources.yaml` (5 rows appended, worktree copy only). Build script: not committed (in /tmp, one pass; the inputs are the OSM ids and coordinates in the register and the raw extracts in `data/ksa/regions-pilot/`).

PILOT_REGION_EASTERN: done
