> **Document version:** docs/status/r2-tabuk.md v1.0 | 31 Oct 2026 | Author: region-scout (REGION_TABUK) | Status: draft

# Track status: r2-tabuk (REGION_TABUK)

## REGION_TABUK: full region register for Tabuk, 31 Oct 2026

**Built:** `screening/sweeps/tabuk/build.py` (register) and `report.py` (Markdown, source list, counts); `cities/ksa/regions/tabuk.parquet` and `.csv` (119 rows); `docs/regions/tabuk.md`; `docs/sources/r2-tabuk.csv` (21 rows); `docs/assumptions-r2-tabuk.md` (A-tabuk-001 to -004).

**Measured:**
- Governorates: GASTAT **7** (primary TA1 export S-cp2-gastat-007, 150 governorates, Tabuk region membership via S-073) = listed **7** (one centre row each). Header `governorates_gastat: 7`, `governorates_listed: 7`.
- Rows **119** = every settlement the R1a universe holds for `tabuk`.
- ≥ 10,000 (`tag_10k`): **7**, all seven governorate centres, all `pop_type: official`, `pop_source_status: verified`, from S-cp2-gastat-008. Every primary ≥ 5,000 city of the Tabuk region is in the register.
- ≥ 5,000 (`tag_5k`): **10** = the seven centres, Halat Ammar (derived, OSM tag 5,293), Makna (grid 5,756), Al Kor (grid 5,353).
- Screened in: **11** (the 10 above plus Neom, grid 2,122, giga-project role). Excluded: **108**, each with `below 5,000 and no sourced economic role (A-screen-003)`.
- Rows without a population: **1** (قرية الجديد: OSM tag 4,000 with no year, so no `pop_year`; not used).
- Grid rows: **109**, all `pop_source_status: unverified`, none ≥ 10,000, none with `pop_corroboration` (no second method run; the 2010 city-growth method does not apply to villages).
- Economic roles: **7** rows, **14** entries, each with an S- source.
- Validation: `uv run python -m screening.region_sweep validate --strict cities/ksa/regions/tabuk.parquet` **ok** (119 rows, 7 governorates; header counts equal). Parquet and CSV agree (same name order). `ruff check` and `ruff format --check` clean on `screening/sweeps/tabuk/`. `common.docver check` OK on the Markdown and assumptions file.
- Facts by status (`docs/sources/r2-tabuk.csv`): primary 2, secondary 13, unverified 6.

**Decisions (recorded here, with reasons):**
1. **All 119 R1a settlements registered**, not only the ≥ 5k set. The pilot left the sub-5,000 places out and asked R2 to register them; excluded rows carry the reason, so no settlement disappears silently.
2. **Population precedence** official > derived > grid (A-screen-031). The seven centres use the primary city export, never the governorate totals (S-cp2-gastat-007). Bi'r Ibn Hirmas keeps its census figure 4,964 (S-tabuk-002, secondary) and the OSM tag 5,975 is not used.
3. **Halat Ammar** is a derived 5k row (A-tabuk-002): the OSM tag 5,293 is not in the census ≥ 5,000 city table. It is an open conflict (see Needs Opus judgement). The pilot's "governorate unresolved" is resolved to Tabuk by the R1a OSM governorate polygon (G147).
4. **Distances and road minutes** are the R1a skims, not recomputed. Committed distances are indicative (A-tabuk-004).
5. **Terrain by governorate** (A-tabuk-003), because no DEM class exists for this region in the R1a outputs. Replaces the pilot's A-screen-pilot-terrain-001.
6. **Governorate name spelling** follows the pilot: Taymā', Al-Bad', Haql (the S-073 list writes "Haqil").

**Deviations and limits:**
- The `red-team-verifier` was **not run**: REGION_TABUK's handoff (task 5) does not list it. Run it before the region is used in R2 screening.
- No DEM read; terrain is assumed by governorate (A-tabuk-003).
- Copied `citypop_admin.html` from the main checkout into the worktree's gitignored `data/ksa/pilot-qassim/raw/`: the GASTAT governorate join (`screening.gastat.governorates_2022`) reads it, and the worktree did not have it. No new dataset was downloaded, so no manifest row was added; every input (S-cp2-gastat-007/008, S-r1a-210, S-r1a-505, the R1a settlement and node files) is already registered.
- Python start took about 75 s on this machine under load; the elapsed time was not measured precisely.

**Needs Opus judgement** (also in `docs/regions/tabuk.md` §8):
1. Halat Ammar: census ≥ 5,000 list omits it; OSM tag 5,293. Drop or get the census locality figure.
2. Red Sea International Airport (nearest node: Hanak) and Red Sea Global: no settlement in the R1a universe, so the roles are attached to no row.
3. NEOM: the town figure 2,122 is a WorldPop grid value for a giga-project site; Port of NEOM has no location.
4. Terrain by governorate, not DEM.
5. Umluj's nearest metro is Madinah (tier 1, 245 km) by distance (A-screen-013); decide whether Tabuk's tier covers Umluj.
6. Committed distances are indicative (unlocated Landbridge stops).
7. Umluj has no sourced economic role.
8. Dhiba port (Duba): the Mawani name is unverified (S-r1a-209 not read).
9. Haql spelling: 'Haql' used; S-073 writes 'Haqil'.
10. Two primary ≥ 5,000 names with no Tabuk settlement (Halat Mahish 7,287; Alhalalih 5,120) are below 10,000 and do not appear in the R1a universe under those names; their region was not checked here (CP2 leftover: 69 primary cities unmatched nationally, `docs/network.md`).

REGION_TABUK: done
