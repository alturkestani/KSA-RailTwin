> **Document version:** docs/r6/judge-backtest.md v1.0 | 3 Nov 2026 | Author: R6 builder (optimizer) | Status: draft

# R6 judge back-test and the CP6 P5b judge change

**Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.** Copy of this file: `runs/r6/judge-backtest.md`. Rows: `runs/r6/judge-backtest-v1/backtest.csv` (270 rows). Hash records: `runs/r6/judge/<name>.hash.json`; summary `docs/r6/judge-hashes.md`.

## 1. Judge v1 (`judge/v1-r5`, tag `r5` = commit d5c43c6, 2,052 files, SHA-256 `f20091cfc4854dc6078a9b46c311bd10c04074027a2947062fe8c8e0d9354fd3`)

Command: `R6_JUDGE_ROOT=judge/v1-r5 .venv/bin/python optimise/backtest.py --ref-root . --out runs/r6/judge-backtest-v1` (seed 1, 10,000 draws). Pass rule: every compared figure within 1 % (relative).

| Test | What is compared | Reference (R5 output) | n | Passed | Max relative difference |
|---|---|---|---|---|---|
| A1 | S0, 2025 calibration point, trips by mode (car 244,606,605.7; rail 9,401,485.4; air 32,031,852.0; bus 3,662,666.7) | `runs/r5/demand/calibration-r5-s1/od/totals.json` | 4 | 4 | 0.0 |
| A2 | S1 vs S0 demand inputs, 17 quantities × 10 (population, year) groups | `runs/cba/inputs/<group>/scalars.parquet` | 170 | 170 | 0.0 |
| A3 | S1 committed programme vs S0: NPV, BCR, PVB, PVC at P10/P50/P90, 60 years, Green Book 2026, 3 population cases (e.g. medium NPV P50 SAR −60,103.2 m, BCR P50 0.306) | `runs/cba/CBA-S1-committed-programme/results.json` | 36 | 36 | 0.0 |
| B | Layout adapter (`optimise/layout.py`) with one corridor = the R5 case: `S3-branch_spur-al-kharj` | `runs/cba/CBA-S3-branch_spur-al-kharj/results.json` | 30 | 30 | 0.0 |
| B | same, `S5-station_addition-al-jubayl` (a station addition) | `runs/cba/CBA-S5-station_addition-al-jubayl/results.json` | 30 | 30 | 0.0 |

**Result: PASS (270/270, every figure identical).** One fix during the back-test: the adapter first used linear percentiles and missed by up to 2.5 % on a near-zero NPV; it now uses R5's own rule (`economics.cba.pct`: `method="nearest"`, NaN lowest), after which every figure is identical. The run that found it is superseded (`logs/r6/backtest-v1.log`, part B re-run in `logs/r6/backtest-v1-B.log`).

## 2. CP6 P5b: zone split, then the one judge change

- **Split** (`demand/zones.py` option `split_governorates`, `cities/ksa/assumptions/demand_zones.yaml` v0.2, A-r6-010): G033 Al-Ahsa → 55 hexagon zones, G034 Al Jubayl → 31, with the metro-hexagon method (A-demand-001/042/043) at 5 km flat-to-flat. Zones 423 → 507 (`runs/zones/meta.json`). Station zones after the split: Hufuf G033-H004, Al-Jarn G033-H053, Al-Oyun G033-H034, Al-Qarah G033-H016, Al-Umran G033-H013, Al Jubayl G034-H006, Jubail Industrial City G034-H005: every station addition now has a zone of its own. Road and station skims re-run (`runs/skims/r3-zones`, 257,049 pairs, 0 unreachable; `runs/skims/r4-stations`, 77 stations). The pre-split runs are kept under `runs/_superseded/R6-P5b/`.
- **Calibration after the split.** With the R5 constants held, S0 2025 changed: car +0.19 %, rail −4.2 %, air +0.35 %, bus −5.5 %; SAR East passengers −18.9 %, so the fitted target SAR East + North fell to −16.6 %, outside the ±15 % tolerance (A-demand-032) (`runs/r6/p5b/S0-2025-v1-r5.json` vs `S0-2025-v2-p5b-uncal-RETIRED.json`). **Decision D-r6-03:** re-run the R5 calibration method unchanged (`demand.calibrate run --network r4 --seed 1`, same targets and ranges) on the split zones: asc.rail −0.775 → **−0.580**, asc.air 1.192 → **1.204**, asc.bus −1.415 → **−1.343**, none at a bound, the three targets matched (deviation 0.0 %) (`runs/r6/demand/calibration-p5b-s1/calibration.json`, A-r6-011). Validation rows: intercity rail national −2.0 %, HHR −2.5 % (both within ±15 %), SAR East alone +39.3 % (outside, as before the split it was +43.3 %).
- **International segment (not in the judge's appraisal demand).** The H3a share (0.0286) was fitted so that resident + international HHR = 8,529,112 with the R5 constants. With the re-fit, resident HHR alone is 8,313,114, so a re-fit share would be ≈ 0.004, below its registered range [0.026, 0.470]. The international segment is not part of the CBA demand runs (international visitors carry no user benefits, CP6 P8a), so the judge is unaffected; the HHR loads reported by R6 are resident trips only. **Open for Tariq (R6 checkpoint).**
- **The judge hash changed once at this point.** A first post-split freeze (`v2-p5b-uncal`, commit db1427c, SHA-256 64fff0c8…) was retired before any search run when the calibration check above failed (it scored one test layout only; `judge/_retired-v2-p5b-uncal/`, `runs/r6/judge/v2-p5b-uncal-RETIRED.hash.json`, its library start in `runs/_superseded/R6-P5b/library-uncal/`). The search uses **only `judge/v2-p5b`** (commit 7606b43, 2,072 files, SHA-256 `2bdee7f587c53ba872cc5fd10a61475496daca76dddab6a1271c103644e592ea`). Code difference v1 → v2: `demand/zones.py` (split option), `economics/demandruns.py` (one line: the calibration file), `optimise/` (adapter, harness), and the post-split inputs; nothing in the appraisal or the demand equations.
- After the re-fit, S0 2025 under v2: car 243,276,946.0; rail 10,722,373.1; air 32,031,851.9; bus 3,662,666.7 (`runs/r6/p5b/S0-2025-v2-p5b.json`).
- **Affected S5 cases re-run** through judge v2: the four Al-Ahsa stations, both Jubail stations and the two-station variant are in the R6 library (`runs/r6/library/<id>/score.json`); the before/after table is in `docs/r6-topology.md` §4.
