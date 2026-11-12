> **Document version:** docs/status/pilot-northern_borders.md v1.0 | 30 Oct 2026 | Author: region-scout (pilot, track pilot-northern_borders) | Status: draft

# Status: pilot-northern_borders

## PILOT_REGION_NORTHERN_BORDERS (coarse pilot sweep, slug `northern_borders`)

**Outputs (owned files):** `cities/ksa/regions/pilot-northern_borders.parquet` and `.csv`, `docs/regions/pilot-northern_borders.md`, `docs/assumptions-pilot-northern_borders.md`, `docs/sources/pilot-northern_borders.csv` (12 rows, `S-northern_borders-001` to `-012`), this file.

| measure | result |
|---|---|
| Register rows | 8: four governorate centres (Arar, Rafha, Turaif, Al-Uwayqilah) and four others (Rawdat Habas, Talah at-Tamiat, Sha'bih Nasab, Hazm al-Jalamid) |
| Parquet vs CSV | 8 and 8 rows; names agree in order; 37 columns in the Parquet |
| Governorates (GASTAT) | `governorates_gastat: null`: **not verified**. The GASTAT primary table was unreachable (`portal.saudicensus.sa`: DNS failure, 30 Oct 2026; S-072, S-090). |
| Governorates (listed) | 4. Discrepancy flagged with both sources: S-002 (Saudipedia: "three governorates" plus capital Arar) vs S-001, S-003 and OSM (four units, Arar included). |
| Towns ≥ 50,000 | 3: Arar (199,247), Rafha (63,929), Turaif (61,395). Locality figures, secondary (S-northern_borders-001). |
| Towns 5,000–50,000 | 2: Al-Uwayqilah (17,055), Rawdat Habas (5,620) |
| Pilot sample | 5 rows with `pilot_sample: true` and a reason each. **Deviation:** only 2 are in the 5–50k band; the other 3 are below-band controls (3,770; 3,430; no population). The region has no further 5–50k towns in the secondary list. |
| Population sourcing | every populated row has `pop_source` (S-northern_borders-001), `pop_year` 2022 and `pop_type` `secondary`. No population is guessed; Hazm al-Jalamid is null. |
| Distances | haversine (A-screen-pilot-001) to the nearest OSM vertex of the named SAR North line, and to the nearest metro centre. Road minutes null, `road_min_method: pending R1a skims`. |
| Existing line | OSM ways named 'قطار الشمال' (main and branch). Nearest: Hazm al-Jalamid 14.2 km; Turaif 96.4; Arar 95.2; Al-Uwayqilah 215.3; Rafha 276.2; Rawdat Habas 302.2; Talah at-Tamiat 271.6; Sha'bih Nasab 326.6. |
| Committed line | none sourced for the region. The GCC railway Saudi section (Al-Khafji–Al-Batha) and Landbridge (Riyadh–Jeddah) do not reach it; committed distances are null. No committed row is labelled existing. |
| Economic roles | every role has a source id (mining: S-008, S-009; border crossing: S-006, S-007; airport: S-004; administrative: S-003) |
| Terrain | all `assumed` (A-screen-pilot-002); Rafha `dunes` by regional description (S-010), the rest `flat_desert` by default. No DEM pass. |
| Exclusions | Mazar'at Jaza' al-Yarman (2,545; no OSM object, so no coordinates); 52 other OSM place objects with no sourced population ≥ 2,500; Linah (OSM town node and village way, governorate unsourced). All listed in the md. |
| Facts verified / secondary / unverified | verified (primary): 0. secondary: all 12 pilot sources (aggregators, Wikipedia, MEED, Saudipedia, OSM). unverified: GASTAT governorate count and locality populations; branch in-service status; town-level terrain; Hazm population; citypopulation.de's own licence. |
| Elapsed time | not measured (no timer in this session) |

### Decisions taken (recorded with reasons)

1. **Schema.** `common/schemas.py:RegionRow` does not yet hold `pop_type: secondary`, `threshold_50k`, `pilot_sample`, `nearest_metro_tier`, `road_min_method` or `notes`, and it forbids extra fields. I did **not** edit `common/` (ownership rule: additive changes only, and this is outside my track). The rows were validated against a local subclass that allows the extra fields and adds `secondary` to `pop_type`; the base schema was not changed. **Coordinator decision needed:** add these fields to `RegionRow` before R2.
2. **Validator.** `screening.region_sweep` does not exist in this worktree, so the Parquet and CSV were written with pandas (the brief's fallback). The validation step is the subclass check above, not `validate`.
3. **Build script.** The script is a scratch file outside the repo, so it is not committed. R2 should move it to `screening/` so the pilot can be reproduced from its archived inputs.
4. **Raw OSM extracts.** Archived under `data/ksa/northern_borders/` (`osm_places_nb.json`, 21,341 bytes; `osm_rail_nb.json`, 236,790 bytes; gitignored). SHA-256 recorded in the sources CSV (S-northern_borders-005) and the md. **Not yet registered in `cities/ksa/sources.yaml`:** coordinator to add.
5. **Licence register.** `docs/licences-pilot-northern_borders.csv` not written (not in my owned list). Licences to register: OpenStreetMap (ODbL 1.0; attribution in the md; share-alike check before any release), citypopulation.de (licence unclear, treat as unclear), Wikipedia (CC BY-SA, facts only), MEED and Arab News (headline or summary only, no copying).
6. **Sample band.** Kept the 5–50k band where it exists and added below-band controls with reasons, instead of inventing towns. Flagged for Opus (md section "Needs Opus judgement", item 2).
7. **Terrain.** Assumed, not sourced at town level, with the assumption id. Flagged for the R1a DEM pass.

### Checks run

- `common.docver check` on the new `.md` files: **OK** (2 files passed when named explicitly). Note: `common.docver check docs` returned "0 files" from this worktree, so the directory form is not reliable here; the coordinator should recheck it in the main checkout.
- Parquet vs CSV: same 8 rows, same order, same 37 columns (Parquet); no population without `pop_source`; no distance without a nearest-line name; no committed row.
- Schema: all 8 rows validated against the subclass (see decision 1).
- Markdown table: generated from the same row list as the Parquet (single source).

### Needs Opus judgement (detail in `docs/regions/pilot-northern_borders.md`)

1. Governorate count: 3 + capital (S-002) or 4 (S-001, S-003, OSM). GASTAT's table decides.
2. Sample band: only 2 of 5 rows are in 5–50k. Accept the below-band controls, or relax the band for this region?
3. Terrain: all assumed; Rafha 'dunes' from a region-level description only.
4. Hazm al-Jalamid: unsourced population (null); unnamed OSM branch segments nearby (19 km): part of the phosphate line?
5. Committed layer: OSM 'construction' segments near 31.60 N, 38.99–39.00 E (ways 1408864679–81) look like a branch under construction, with no source. Not labelled committed.
6. Existing-line status of the Jouf–Qurayyat and phosphate branches, and the Al Haditha stop, which differs across sources.
7. Name variants: Turaif/Turayf; Talah at-Tamiat/At Timyat (a probable match, unconfirmed). Turaibil (Iraq–Jordan) is not Saudi and is not used.
8. Road minutes (pending R1a) and metro distances (straight-line; Tabuk and Buraidah are the nearest tier-2 centres for every row).

PILOT_REGION_NORTHERN_BORDERS: done
