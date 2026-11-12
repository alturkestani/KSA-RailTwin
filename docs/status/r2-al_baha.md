> **Document version:** docs/status/r2-al_baha.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_AL_BAHA) | Status: draft

# Status, track r2-al_baha

## REGION_AL_BAHA (31 Oct 2026)

- Governorates: GASTAT `governorates_gastat: 10`, `governorates_listed: 10`. Counts reconciled: the ten primary-export names sum to the Al-Bahah region total 339,174 (S-r1a-502; citypopulation region table S-al_baha-112 agrees to the person).
- Rows: 16 (10 governorate centres; 5 at or above 10k; 12 at or above 5k). The 233 remaining Al-Bahah settlements (all below 5,000, all grid) stay in the R1a universe; scope rule A-al_baha-005.
- Population: 7 official rows (GASTAT Census 2022 TA1 city>=5,000 primary export, verified); 8 grid rows (WorldPop 2020, unverified, no second method, none at or above 10k). No derived or secondary figure in `population`.
- Economic roles: 13 role entries, all sourced: administrative x10 (S-al_baha-101/105); university and industrial_city for Al-Bahah (S-al_baha-110/107, S-al_baha-111); airport for Al-Aqiq (S-al_baha-108/107). Region-level tourism and honey (AJEL) not attached to a town.
- Terrain: region-level `escarpment_mountain` for all rows (A-al_baha-001; no DEM sampled).
- Facts: verified = GASTAT primary export values (S-al_baha-101/102); secondary = citypopulation cross-check, Wikipedia (Sarawat, Al-Aqiq airport), Saudipedia (Bani Hasan centres), AJEL; unverified = the eight grid rows and the Al-Qara centre location.
- Validation: `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/al_baha.parquet`: ok, 16 rows, 10 governorates. Builder `screening.sweeps.al_baha.build`; Markdown from `screening.sweeps.al_baha.docs`. `common.docver check docs`: OK.
- Deviations from the brief, stated for the coordinator:
  1. The geo-verify step (`screening.geo_verify.cli estimate --region al_baha`) was NOT run. Its estimator downloads Microsoft building-footprint tiles and imagery, which the R2 disk gate forbids here, and the worktree has no grids. The GEO_VERIFY back-test already fails both estimators at 30 %, so no value was lost; Al-Qara's centre remains an unlocated, flagged polygon point (A-al_baha-002).
  2. The red-team verifier was not run from this track. The region is an R2 input; the coordinator's R2 milestone check covers it.
  3. No licence-register rows were added: no new dataset was downloaded (GASTAT, OSM, WorldPop, OSRM and MODON entries are already registered).
  4. Elapsed time not measured.
- Needs Opus judgement: 10 items in `docs/regions/al_baha.md` (Al-Qara centre; airport host town Al-Aqiq vs R1a's Al-Bahah; Al-Hajrah and Ghamid seat populations unsourced; Bani Hasan centre conflict; Qilwah two nodes; committed distances to proxy stations; double-counting flags on Rahwat al Barr and Sayal; control-total flag; terrain; and the Al Harjah region question for the coverage audit).

REGION_AL_BAHA: done
