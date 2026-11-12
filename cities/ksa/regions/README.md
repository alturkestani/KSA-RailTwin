> **Document version:** cities/ksa/regions/README.md v1.0 | 31 Oct 2026 | Author: INTEGRATE_R2 | Status: active

# Region registers

`<region>.{parquet,csv}`: the 13 national R2 sweeps (`region-sweep` skill), merged by `./screening/run_r2.sh` into `cities/ksa/candidates.parquet`. Each passes `uv run python -m screening.region_sweep validate --strict`. The pilot registers (`pilot-<region>.*`, 30 Oct 2026) were archived to `archive/pilot/` at INTEGRATE_R2 (31 Oct 2026); see its README. Label: screening input, not a forecast.
