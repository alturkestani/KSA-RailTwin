> **Document version:** docs/status/r2-hail.md v1.1 | 31 Oct 2026 | Author: region-scout (REGION_HAIL, track r2-hail) | Status: draft

# Track `r2-hail` — status

## REGION_HAIL — 31 Oct 2026

**Built:** the Ḥā'il register (`region-sweep` schema): `cities/ksa/regions/hail.parquet` and `.csv` (17 rows; header `governorates_gastat: 9`, `governorates_listed: 9`); the builder `screening/sweeps/hail/build_register.py` (explicit selection with an assertion; the population precedence applied by name against the relayed table); the generator `screening/sweeps/hail/write_doc.py` for `docs/regions/hail.md` (counts, tallies and table computed from the register); `docs/assumptions-r2-hail.md` (A-hail-001 to 003); `docs/sources/r2-hail.csv` (S-hail-009, a derived sum); `tests/test_hail_register.py` (7 tests).

**Measured:**
- Governorates: **9 GASTAT, 9 listed, reconciled.** The primary GASTAT governorate export (S-cp2-gastat-007) carries the nine working-list names; their sum, 746,406, equals the Ḥā'il region total (S-hail-001), re-read live on the citypopulation.de page on 31 Oct 2026.
- Rows: **17**: 9 governorate centres (2 below 5,000: Mawqaq 3,148 and Simīrā' 3,105, `screened: false`, kept for coverage), plus 8 non-centre towns at or above 5,000.
- Rows at ≥ 10,000 (`tag_10k`): **4** (Ḥā'il 448,623 verified; Baq'ā' 19,659 verified; Ash-Shanān 11,560 secondary; Al-Malwi 15,000 OSM tag, doubtful). Rows at ≥ 5,000 (`tag_5k`): **15**.
- Population sources: verified (GASTAT primary read) 8; secondary 4 (relayed or OSM tag); unverified grid 5 (all below 10,000, so the A-screen-031 gate does not bite).
- Economic roles, each sourced: **5** (Ḥā'il: administrative, airport, industrial city, university; Jubbah: heritage). Other towns say "none sourced" in notes.
- Universe: 650 R1a rows in Ḥā'il; 633 not written (422 hamlets, 209 villages, 2 towns), on the resolved figures. Largest excluded resolved population 4,688. The builder asserts that no excluded row has a resolved population at or above 5,000.
- Checks: `region_sweep validate --strict` ok (17 rows, 9 governorates); `common.docver check docs` OK (106 files, including the verifier archives); `common.manifest verify` OK (305 rows); `pytest` on the Hail, region-sweep and docver tests passes (full suite passed before the fix, exit 0); `ruff check` and `ruff format --check` clean on the new files.

**Verifier pass 1 — FAIL (fixed here).** The red-team verifier found that three towns were tagged at ≥ 5,000 on a grid or OSM figure while the relayed GASTAT table I cite carries lower figures for them: Al-Khuṭah 3,355 (was 9,636 grid), Al-Ḥalīfah as-Suflā 4,151 (was 8,990 grid), Al-Qā'id 2,913 (was 5,523 OSM tag). My notes said no GASTAT figure existed; that was wrong. The precedence rule (official > derived > grid) was not applied. The fix: the builder now matches every grid or OSM row by Arabic name against the relayed table before selection; the relayed figure then decides the 5k test. Six universe rows are replaced in this way (Al Hulayfah Assofla, Al Ruwda, Al Qa`id, Munifat al Qa`id, An Nisiyah, Al Khuttah); the doc lists them by name. I re-read the three figures on the live page myself before using them. The verifier's report is kept at `docs/status/verify-REGION_HAIL-pass1.md`. The `tag_5k` count moves from 18 to 15, as the verifier predicted.

**Decisions (recorded, with the reason):**
- **Selection (procedure):** every centre plus every settlement at ≥ 5,000 on the resolved population (relayed > primary > OSM tag > grid), so rule 2 is met for the figures that count.
- **Population precedence:** GASTAT primary city table (S-cp2-gastat-008) > relayed (S-hail-001, secondary) > OSM tag (S-hail-003, derived) > WorldPop grid (S-r1a-506, unverified). Matching is by (Arabic name, Arabic governorate), with tatweel removed and the universe's 'محافظة ' prefix stripped from governorates; a duplicate that a relayed match could hit is an error. The relayed transcription prints one name with a tatweel.
- **Ash-Shanān 11,560 stays on S-hail-001.** The crosswalk leaves the primary `Alshazalah` 11,560 unmatched (logged in notes and in the doc). Opus judgement.
- **Turubah = Turba 8,590 (Baq'ā').** The Makkah Turubah 28,279 is a different place; it is not used.
- **Al-Malwi (OSM tag 15,000, dated 1950) is kept at `tag_10k: true` as the procedure allows, and flagged** (A-hail-002). Without it the 10k count is 3. Opus judgement.
- **Terrain not measured (A-hail-001).** The pilot's blanket `mixed` is not carried.
- **Distances:** straight line (haversine) to the nearest existing or committed station; road minutes from the OSRM car profile (S-r1a-809, free flow, uncalibrated). For 4 committed rows the road skim targets a different Landbridge stop than the straight-line nearest; the notes name both.
- **English names:** five OSM places carry only an Arabic name; the English forms are our transliterations and are marked in notes.
- **Pilot GEO_VERIFY estimates** for Ash-Shanān, Mawqaq and Simīrā' are carried in notes as record-only values (back-test above the 30 % gate). None enters `population`.

**Verifier pass 2 — FAIL on F2, fixed here.** Pass 2 closed F1 (the three rows are gone; no other grid or OSM row at or above 5,000 is left unresolved against S-hail-001, checked independently). It found: (F2) the A-hail-002 row still named Al Qa'id as an OSM-tag row, and two note branches and the builder docstring described towns no longer in the register; and (W8) matching by name alone could collide across governorates (Al Ruwda in Ḥā'il and Arrwodhah in Al-Ḥā'īṭ share a name; no effect on this register, unsafe for other regions). Fixed: relayed matching is by (name, governorate) with the governorate prefix normalised, and a duplicate that a relayed match could hit raises an error; A-hail-002 and A-hail-003 rewritten to the 17-row register; dead branches and the docstring corrected. The register is unchanged (17 rows, 15 at 5k, 4 at 10k). Pass 2's report is at `docs/status/verify-REGION_HAIL.md` before pass 3 overwrites it.

**Incident, fixed:** while fixing the relayed-table match I appended a line to `data/ksa/hail/citypop_hail_census2022.csv` and then removed it. That file is a manifest-registered raw file, and my worktree's copy is a symlink into the main checkout, so the edit reached the main file and the revert also removed the file's original Al-Qā'id row (112 bytes short; the manifest failed). I restored the main file byte-for-byte from the pilot-hail worktree copy, whose SHA-256 and byte count match the manifest row (`citypop-hail-census2022`: 3405 bytes), and the manifest verifies again. The file's content is unchanged from the registered version.

**Could not do / deviations:**
- **Geo-verify estimate not re-run.** The WorldPop raster and footprint tiles are not in this worktree, and the prompt's disk gate forbids the grid and PBF downloads. Both estimators already fail the 30 % back-test, so their values are record-only anyway. The pilot estimates for the three relayed rows are carried; Al-Malwi and Al-Qā'id (OSM tags) have none, and Al-Qā'id is now below 5,000 on the relayed figure. This is the only step of the mandatory geo-verify list not done.
- **Manifest verify in this worktree needed local links.** The gitignored `data/ksa/` of this worktree held only `tables/` and `hail/`, so 62 manifest rows failed. I linked the missing directories (benchmarks, census, costs, geo, grids, hhr, northern_borders, osm, osrm, pilot-qassim, regions-pilot) and one pilot file from the main checkout. These are local symlinks in a gitignored folder, not tracked; the manifest verifies 305 rows.
- **No licence rows added.** No new dataset was downloaded; the inputs (GASTAT tables, WorldPop 2020, OSM, OSRM skims) are in `docs/licences.md`.
- **Not timed:** the elapsed time was not recorded.
- **Transcription gap (pilot file, not this track's):** the live page lists Al-Ḥafīr (Mawqaq area) at 3,243, which the pilot's transcription does not carry. Below 5,000, so no effect on this register; for the pilot and coverage audit.
- **Not committed yet.** The deliverables are uncommitted; the commit follows the verifier's PASS.

**Open for Opus judgement (also in `docs/regions/hail.md` section 7):** Al-Malwi (tag and governorate at 25.3 N); Ash-Shanān vs Alshazalah; the grid-only towns (5k sensitivity only); terrain class (no DEM); region-edge membership of Al-Ḥā'īṭ's southern villages; and whether Shuwaymis (the second rock-art component, Al-Ḥā'īṭ governorate) should carry a heritage role.

**Next:** commit (`feat(screening): region sweep hail`); then the Hail terrain pass (DEM) and the geo-verify re-run once the raster is available; the national coverage audit (150 primary governorate rows vs 152 in the working list).

**Verifier:** pass 1 FAIL (F1), pass 2 FAIL (F2, W8), pass 3 FAIL (status file only: replaced-row count and matching wording), pass 4 PASS (`docs/status/verify-REGION_HAIL.md`; earlier reports in `verify-REGION_HAIL-pass1/2/3.md`).

REGION_HAIL: done
