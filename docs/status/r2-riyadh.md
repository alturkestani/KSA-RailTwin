> **Document version:** docs/status/r2-riyadh.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_RIYADH sweep) | Status: draft

# Status: r2-riyadh (REGION_RIYADH)

## REGION_RIYADH: Riyadh region sweep (W2), 31 Oct 2026

Built: `screening/sweeps/riyadh/build.py` (register builder) and `screening/sweeps/riyadh/doc.py` (document from the register, so prose and tables cannot drift); `cities/ksa/regions/riyadh.parquet` (header `governorates_gastat` = 23, `governorates_listed` = 23) and `riyadh.csv`; `docs/regions/riyadh.md`; `docs/assumptions-r2-riyadh.md` (A-riyadh-001 to 006); `docs/sources/r2-riyadh.csv` (S-riyadh-101, 102).

Measured:
- Governorates: 23 on the GASTAT list (S-073 names). Each name is found in the GASTAT TA1 primary governorate export (S-cp2-gastat-007); the 23 totals sum to 8,591,748, equal to the TA1 Riyadh region total (S-cp2-gastat-002). GASTAT's own count is not readable (S-090), so the sum check is the evidence. Listed in the register: 23.
- Rows: 1,096 settlements of the R1a Riyadh universe. Screened 60; excluded 1,036 (`below 5k and no economic role`).
- At or above 10,000 (`tag_10k`): 22. At or above 5,000 (`tag_5k`): 57.
- Grid-only rows at or above 10,000 that fail the 30 % gate: 3 (Al-Saih 138,604; Mugharrizat 19,214; Tharmada' 11,002), kept screened with the reason.
- Sourced economic roles: 30 entries on 14 rows (Riyadh city, Ad-Dir'iyah, Al-Kharj, Al-Majma'ah, Az-Zulfi, Duruma, Shaqra, Wadi ad-Dawasir and others).
- Pilot vs primary: no Riyadh row differs by more than 2 %.
- Validation: `python -m screening.region_sweep validate --strict cities/ksa/regions/riyadh.parquet` returns `ok`; `ruff check` and `ruff format` clean on `screening/sweeps/`; `common.docver check docs` OK (101 files).

Facts, by status:
- Verified: 36 official populations read on GASTAT's primary city table (S-cp2-gastat-008), of which 22 are at or above 10,000 (the whole base-case set); the governorate sum (S-riyadh-101).
- Secondary: Ar-Rayn seat 2,726 (S-cp1-017, relayed; `primary_to_find` = GASTAT locality table); 10 OSM population tags (`derived`, `secondary`), of which 6 are at or above 5,000.
- Unverified: 1,049 WorldPop 2020 grid rows (`pop_source_status: unverified`). Of these, 15 at or above 5,000 carry `primary_to_find`; grid rows never enter `population` as corrected values.

Decisions (recorded in `docs/assumptions-r2-riyadh.md`):
- Register scope is every R1a settlement of the region; excluded rows keep their reason (A-riyadh-001).
- Committed stops are unlocated proxies, so committed distances are to proxy points (A-riyadh-002).
- Terrain: `flat_desert` default (A-screen-pilot-002 [riyadh]) with `escarpment_mountain` for Ar-Riyadh (S-riyadh-015); no DEM class run (A-riyadh-003).
- Economic-node ties by name; the node-to-row distance is in `notes` (A-riyadh-004).
- Population follows CP2 P1a: the primary GASTAT city table first, then the relayed seat, then the OSM tag, then the gated grid. Al-Saih's 2010-growth second method (232,644) is 68 % from the grid value and fails the gate.
- Name spelling follows S-073 (`Rimah`); the GASTAT primary export and R1a use `Rumah` (governorate total 35,683).

Not done or open (none blocks the sweep; all listed in `docs/regions/riyadh.md` judgement list):
- GASTAT's locality table is not reachable (S-090, S-r1a-500): Al-Saih (138,604) and 14 other grid rows at or above 5,000 cannot be checked against an official figure.
- Three R1a economic nodes are excluded (Jeddah coordinates; a Shaqra tie 600 km away; a Hajj-coordinate source); Ma'aden Al-'Amar's role rests on search snippets (S-r1a-217).
- Riyadh Al-Khabra (31,203, GASTAT primary governorate) is outside the S-073 Riyadh list and outside the region total; not registered here.
- The `red-team-verifier` was not run: this sweep is not an R<n> milestone (VERIFY_R2 is the coordinator's); the sweep's own checks are the validator, ruff and docver.
- Repository tests: 5 tests fail in this worktree because gitignored raw files (`data/ksa/costs/wb_NY.GDP.DEFL.ZS.json`, `data/ksa/pilot-qassim/raw/citypop_admin.html`) exist only in the main checkout. They are unrelated to this sweep.
- Elapsed time: not timed.

REGION_RIYADH: done
