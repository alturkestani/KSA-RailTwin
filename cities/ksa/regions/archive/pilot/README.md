> **Document version:** cities/ksa/regions/archive/pilot/README.md v1.0 | 31 Oct 2026 | Author: INTEGRATE_R2 | Status: active

# Archived pilot region registers (30 Oct 2026)

The 13 `pilot-<region>.{parquet,csv}` registers are the coarse pilot sweeps (PILOT_REGION_*, merged at PILOT_MERGE on 30 Oct 2026) and the two pilot build scripts. They were moved here from `cities/ksa/regions/` at INTEGRATE_R2 (31 Oct 2026, CP3 housekeeping, the coordinator's preference) because the national R2 registers (`cities/ksa/regions/<region>.parquet`, merged into `cities/ksa/candidates.parquet`) supersede them.

- They are samples (a subset of each region's governorates), so their headers cannot pass `uv run python -m screening.region_sweep validate --strict` (`governorates_gastat` is unknown or differs from the governorates listed). They still pass the non-strict check (`tests/test_region_sweep.py`).
- Code that reads them points here: `screening.geo_verify.cli` (default register glob), `screening.pilot_normalise`, `screening.cp1_fixes.apply`, `screening.gastat` (`--regions`), `screening/run_pilot_funnel.sh`, and the R2 sweep build scripts that take pilot notes or roles (`screening/sweeps/<region>/build.py`).
- Older documents (`docs/regions/pilot-*.md`, `docs/sources/*.csv` `used_in` columns, status files) cite the pre-archive path `cities/ksa/regions/pilot-<region>.*`; read it as this directory. The two build scripts (`build_pilot_riyadh.py`, `pilot-tabuk_build.py`) are kept as historical records and still name the old output paths.
- Data: OSM (ODbL 1.0, © OpenStreetMap contributors), GASTAT Census 2022 figures relayed or primary (credited per row in `sources`), WorldPop where marked `grid`. Licences: `docs/licences.md`. Label: screening input, not a forecast.
