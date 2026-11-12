> **Document version:** docs/status/pilot-al_baha.md v1.0 | 30 Oct 2026 | Author: region-scout (PILOT_REGION_AL_BAHA) | Status: draft

# Track `pilot-al_baha` — status

## PILOT_REGION_AL_BAHA — coarse pilot sweep, Al-Baha (الباحة), 30 Oct 2026

Start: about 21:57 (+03), first tool call. Stop: see the end of this block. Elapsed time: about 25 minutes of tool and research time, including the sources.

Rows written: **10** (one per governorate centre; `cities/ksa/regions/pilot-al_baha.parquet` and `.csv`, 39 columns, same row ids `AB-01`…`AB-10`).

Governorates: GASTAT official count **unknown** (`governorates_gastat: unknown`; the census portal did not resolve, `S-090`; the count is unverified, `S-072`). Listed: **10 rows** (citypopulation, S-al_baha-001) versus **9** governorates plus the capital (Wikipedia S-al_baha-005; Saudipedia snippet). Flagged, not resolved.

Towns ≥ 50k (settlement, `threshold_50k`): **1**, Al-Bāḥah city, 90,515 (S-al_baha-002). Baljurashī: governorate total 51,787 but town 35,985, so false; Needs Opus judgement.

Pilot sample (`pilot_sample: true`): **6** (Baljurashī, Al-Makhwāh, Al-Mandaq, Banī Ḥasan, Al-'Aqīq, Qilwah), each with a reason in `sample_reason`. The "near" stratum is empty: no town is within 25 km of any existing or committed station; all six are 213–253 km from Makkah Central.

Facts, by status (in `docs/sources/pilot-al_baha.csv`, 12 rows):
- verified: OSM place and station ids and coordinates (`S-al_baha-006`, `-007`); Kingdom index S-070 (13 regions).
- secondary: citypopulation.de populations (credits GASTAT, `S-al_baha-001`–`-003`); Wikipedia (Baljurashī coordinates, governorate list, Haramain opening, Sarawat range, Al-Aqiq airport); AJEL honey (`-011`); Saudipedia Banī Ḥasan (`-012`).
- unverified: the GASTAT governorate count; the word "escarpment" for terrain (not on the cited page; UNESCO returned 403); the Al-Qarā centre (no coordinate source); Baljurashī OSM place node (not found); the Al-Ḥajrah centre population (governorate total only).

Distances: great-circle (`A-screen-pilot-001`); road minutes empty (`pending R1a skims`). Committed-line distances empty (no station coordinates sourced).

Assumptions added (`docs/assumptions-pilot-al_baha.md`): A-screen-pilot-001 (haversine), -002 (station-only existing reference), -003 (region-level terrain), -004 (centre identification).

Schema validation: **fails**. `common/schemas.py` is additive-only for this track and was not edited. (1) `RegionRow.pop_type` has no `secondary` (10 populated rows; the brief's value). With `secondary` mapped to `official` for the check only, validation passes except for (2). (2) Al-Qarā has no coordinates: `lat`/`lon` are required. (3) The brief's extra fields (`threshold_50k`, `pilot_sample`, `sample_reason`, `nearest_metro_tier`, `road_min_method`, `notes`, `primary_to_find`) are not in `RegionRow`, which forbids extras; they are extra Parquet columns. `screening.region_sweep validate` does not exist in this worktree.

Parquet and CSV agree (10 rows, same `row_id`s, same column count, 6 pilot rows, 1 threshold_50k). Markdown table generated from the Parquet (10 rows). `common.docver check` on the new Markdown files by explicit path: OK (2 files). Note: `common.docver check docs` in this worktree reports 0 files because its path filter excludes any path containing `.worktrees`; so the directory form does not check this track.

Decisions (recorded, reason given):
- 2026-10-30: pop_type `secondary` kept in the data as the brief says; the schema decision is left to Opus (common/ is additive-only for this track).
- 2026-10-30: Al-Qarā kept as `screened: false` with NaN coordinates, not invented; the schema gap is reported rather than hidden.
- 2026-10-30: Governorate population used only for governorate totals; a centre gets a population only where a place-level figure is sourced.
- 2026-10-30: nearest existing = Makkah Central (in service; station-based); nearest metro = Taif or Abha by haversine, Makkah not nearest.

Needs Opus judgement (full list in `docs/regions/pilot-al_baha.md`): schema (pop_type, lat/lon, extra fields); GASTAT governorate count (10 vs 9+capital); Baljurashī 50k rule; Banī Ḥasan and Qilwah centre conflicts; Al-Ḥajrah centre tagged `place=village`; committed-line distances; terrain (DEM).

Could not verify: GASTAT governorate count; Al-Qarā coordinates; terrain per town (DEM not run); Baljurashī OSM place node.

Commit: `feat(screening): pilot sweep al_baha` on branch `pilot-al_baha` (no push).

PILOT_REGION_AL_BAHA: blocked - RegionRow rejects pop_type 'secondary' and requires coordinates (Al-Qarā has none); the register and docs are otherwise complete; the schema decision is for Opus (common/schemas.py is additive-only for this track).
