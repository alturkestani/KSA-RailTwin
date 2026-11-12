> **Document version:** screening/pilot_builders/README.md v1.0 | 31 Oct 2026 | Author: CP1_PREP builder | Status: draft

# Pilot builder scripts (recovered, archival)

Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

The 13 national-pilot region runs (30 Oct 2026) wrote their builder scripts to `/tmp` (and two into `cities/ksa/regions/`), so the pilot registers were not reproducible from the repository (`docs/plan.md` §9 Q24). CP1_PREP item 4 copied every script that still existed into this folder on 31 Oct 2026. Search: `find /tmp/ -maxdepth 3 -name '*.py' -newer PROJECT.md`, plus every `/tmp/...py` path named in the pilot status files and in the stream-json logs `logs/orch/pilot-*-try1.jsonl` (tool inputs).

Each file starts with a header: origin, last-modified time, role, the output files named in the code. Changes against the original: absolute home paths rewritten to repository-relative `./` (or `~`), `ruff format` applied, `# ruff: noqa` added (archival code, not linted). Logic unchanged. The `/tmp` copy is the **last** version on disk, which may differ from the version that produced the committed register if the pilot edited the file after its final run; the committed registers in `cities/ksa/regions/` (normalised by `screening/pilot_normalise.py`) remain the record.

These scripts called public services (Nominatim/Overpass, citypopulation.de) and are not run by the tests. New region sweeps keep their scripts under `screening/` in their worktree from the start (rule in `prompts/REGION_TEMPLATE.md`, `prompts/PILOT_REGION_TEMPLATE.md` and the `region-sweep` skill).

| region | file | origin | last modified (+03) | role |
|---|---|---|---|---|
| al_baha | `al_baha_build.py` | `/tmp/alb/build.py` | 2026-10-30 22:03 | built the region register |
| al_baha | `al_baha_sources.py` | `/tmp/alb/sources.py` | 2026-10-30 22:04 | lookup helper (OSM/Nominatim or census-table extraction) |
| al_baha | `al_baha_docs.py` | `/tmp/alb/docs.py` | 2026-10-30 22:04 | wrote the region documents |
| al_baha | `al_baha_al_baha_dist.py` | `/tmp/al_baha_dist.py` | 2026-10-30 22:02 | distance calculations (printed, copied into the register) |
| al_jouf | `al_jouf_build.py` | `/tmp/aljouf_osm/build.py` | 2026-10-30 22:06 | built the region register |
| al_jouf | `al_jouf_calc.py` | `/tmp/aljouf_osm/calc.py` | 2026-10-30 22:05 | distance calculations (printed, copied into the register) |
| asir | `asir_build.py` | `/tmp/asir-scripts/build_pilot.py` | 2026-10-30 21:27 | built the region register |
| asir | `asir_extract_places.py` | `/tmp/asir-scripts/extract_places.py` | 2026-10-30 21:24 | lookup helper (OSM/Nominatim or census-table extraction) |
| asir | `asir_match_names.py` | `/tmp/asir-scripts/match_names.py` | 2026-10-30 21:24 | lookup helper (OSM/Nominatim or census-table extraction) |
| asir | `asir_gen_doc.py` | `/tmp/asir-scripts/gen_doc.py` | 2026-10-30 21:28 | wrote the region documents |
| eastern | `eastern_build.py` | `/tmp/pilot-eastern-src/build.py` | 2026-10-30 21:13 | built the region register |
| eastern | `eastern_nom.py` | `/tmp/pilot-eastern-src/nom.py` | 2026-10-30 21:08 | lookup helper (OSM/Nominatim or census-table extraction) |
| eastern | `eastern_md.py` | `/tmp/pilot-eastern-src/md.py` | 2026-10-30 21:13 | wrote the region documents |
| hail | `hail_build.py` | `/tmp/hail-scratch/build.py` | 2026-10-30 21:28 | built the region register |
| hail | `hail_tables.py` | `/tmp/hail-scratch/tables.py` | 2026-10-30 21:30 | lookup helper (OSM/Nominatim or census-table extraction) |
| hail | `hail_find.py` | `/tmp/hail-scratch/find.py` | 2026-10-30 21:24 | lookup helper (OSM/Nominatim or census-table extraction) |
| hail | `hail_match.py` | `/tmp/hail-scratch/match.py` | 2026-10-30 21:24 | lookup helper (OSM/Nominatim or census-table extraction) |
| hail | `hail_dist.py` | `/tmp/hail-scratch/dist.py` | 2026-10-30 21:24 | distance calculations (printed, copied into the register) |
| hail | `hail_d2.py` | `/tmp/hail-scratch/d2.py` | 2026-10-30 21:24 | distance calculations (printed, copied into the register) |
| hail | `hail_md.py` | `/tmp/hail-scratch/md.py` | 2026-10-30 21:29 | wrote the region documents |
| hail | `hail_validate.py` | `/tmp/hail-scratch/validate.py` | 2026-10-30 21:27 | validation only (no output files) |
| jazan | `jazan_build.py` | `/tmp/jz/build/build_pilot.py` | 2026-10-30 21:41 | built the region register |
| jazan | `jazan_write_pilot.py` | `/tmp/jz/build/write_pilot.py` | 2026-10-30 21:41 | lookup helper (OSM/Nominatim or census-table extraction) |
| jazan | `jazan_write_docs.py` | `/tmp/jz/build/write_docs.py` | 2026-10-30 21:43 | wrote the region documents |
| madinah | `madinah_build.py` | `/tmp/pilot_madinah/build.py` | 2026-10-30 21:10 | built the region register |
| madinah | `madinah_check.py` | `/tmp/pilot_madinah/check.py` | 2026-10-30 21:13 | validation only (no output files) |
| makkah | `makkah_build.py` | `/tmp/pilot_makkah/build.py` | 2026-10-30 21:12 | built the region register |
| makkah | `makkah_lookup.py` | `/tmp/pilot_makkah/lookup.py` | 2026-10-30 21:07 | lookup helper (OSM/Nominatim or census-table extraction) |
| najran | `najran_build.py` | `/tmp/najran_work/build.py` | 2026-10-30 22:02 | built the region register |
| najran | `najran_dist.py` | `/tmp/najran_work/dist.py` | 2026-10-30 21:58 | distance calculations (printed, copied into the register) |
| najran | `najran_calc.py` | `/tmp/najran_work/calc.py` | 2026-10-30 21:59 | distance calculations (printed, copied into the register) |
| najran | `najran_md.py` | `/tmp/najran_work/md.py` | 2026-10-30 22:02 | wrote the region documents |
| najran | `najran_validate.py` | `/tmp/najran_work/validate.py` | 2026-10-30 22:01 | validation only (no output files) |
| northern_borders | `northern_borders_build.py` | `/tmp/nbpilot/build_register.py` | 2026-10-30 21:43 | built the region register |
| northern_borders | `northern_borders_build_inputs.py` | `/tmp/nbpilot/build_inputs.py` | 2026-10-30 21:40 | built the region register |
| northern_borders | `northern_borders_write_docs.py` | `/tmp/nbpilot/write_docs.py` | 2026-10-30 21:44 | wrote the region documents |
| qassim | `qassim_build.py` | `/tmp/qassim_build/build.py` | 2026-10-30 21:31 | built the region register |
| qassim | `qassim_docs.py` | `/tmp/qassim_build/docs.py` | 2026-10-30 21:33 | wrote the region documents |
| qassim | `qassim_validate.py` | `/tmp/qassim_build/validate.py` | 2026-10-30 21:32 | validation only (no output files) |
| riyadh | `riyadh_build.py` | `cities/ksa/regions/build_pilot_riyadh.py` (still tracked there) | 2026-10-30 22:11 | built the region register |
| riyadh | `riyadh_osm_places.py` | `/tmp/rs/osm_places.py` | 2026-10-30 21:11 | lookup helper (OSM/Nominatim or census-table extraction) |
| riyadh | `riyadh_osm_places2.py` | `/tmp/rs/osm_places2.py` | 2026-10-30 21:14 | lookup helper (OSM/Nominatim or census-table extraction) |
| riyadh | `riyadh_osm_places3.py` | `/tmp/rs/osm_places3.py` | 2026-10-30 21:16 | lookup helper (OSM/Nominatim or census-table extraction) |
| tabuk | `tabuk_build.py` | `cities/ksa/regions/pilot-tabuk_build.py` (still tracked there) | 2026-10-30 22:11 | built the region register |

## Not recoverable

- Every `/tmp` script path named in the pilot status files and the stream-json logs was found (44 files, 13 of 13 regions). Nothing named is missing.
- Not recoverable as files: one-off `python -c` / heredoc commands typed directly in the pilot shells (they exist only inside the gitignored stream-json logs `logs/orch/pilot-*-try1.jsonl`). Where a pilot computed a value that way, the register row's `sources`/`notes` and `docs/regions/pilot-<region>.md` remain the only record.
- Not pilot builders, so not copied: PILOT_MERGE's inventory helpers (`/tmp/inv.py`, `inv2.py`, `inv3.py`, `cp.py`), the R0 and DATASCOUT_1H helpers (`/tmp/r0/lic.py`, `/tmp/datascout_D/mkcsv.py`).
