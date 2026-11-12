> **Document version:** docs/status/r1c.md v1.1 | 31 Oct 2026 | Author: cost-estimator (R1c builder) | Status: draft

# Track r1c (W3 cost register v1)

## R1c: cost register v1, KSA data points, reference-class uplifts (31 Oct 2026)

Resumed session: tasks 1–7 were committed by the previous session (`c19c2c7` … `5fbfaca`); this session ran the handoff (task 8). Nothing was pushed; no one was contacted.

**Built**
- Schema and CLI: additive `CostItem` fields and `UpliftSpec` in `common/schemas.py`; `costs/register.py` (`validate`, `normalise --to SAR --price-year 2025`, `list`), `costs/index_build.py`, `costs/rcf.py`, `costs/estimate.py`, `costs/reconcile.py`, `costs/cli.py`.
- `cities/ksa/costs/cost_register.yaml`: **207 items: sourced 61, derived 114, assumed 13, unknown 19** (`uv run python -m costs.register validate` → OK).
- `cities/ksa/costs/index.yaml`: price and FX index from the manifest-registered World Bank WDI and Eurostat series (A-cost-001, -002, -009); price base 2025 SAR.
- `cities/ksa/costs/uplifts.yaml`: capex, schedule and ridership multipliers per line type and stage. Sources: UK DfT/OGP 2020 optimism-bias workbook and Green Book supplementary guidance on optimism bias (S-cost-rcf-008 and companions), Flyvbjerg et al. 2002–2007 reference-class papers (S-cost-rcf-010 and companions); every distribution carries a source id and an A-rcf id (`docs/sources/cost-rcf.csv`, `docs/costs.md` §7).
- KSA data points (`docs/costs.md` §4): Haramain HSR (2012 estimate, official outturn SR 60–63 bn, USD 7.87 bn outlier, per-km derivation, Phase 1 package contracts, 2026 consortium package), SAR North (2012 SR 20 bn, 2017 figure, packages), SAR East (doubling, renewal, Hofuf bypass, rolling stock), Riyadh Metro (USD 22.5 bn 2013 awards vs USD 25 bn 2024 outturn, conflict C-005 resolved as two vintages), Landbridge (SR 100 bn and USD 7 bn with scope, as in `docs/sources/conflicts.md`; `docs/costs-landbridge.md`). All KSA rows are `secondary`/`unverified` at source level: no SAR, MOT, RCRC or CNMV primary was readable. Haramain ridership vs forecast: the only forecast found is "> 3 m passengers a year" (2012, unverified snippet; no horizon year), against a 2023 outturn of 6.97 m (S-012, secondary); it cannot test the ridership reference class (`docs/costs.md` §4.1).
- Reconciliation (`docs/costs.md` §5.2, `costs/reconcile.py`): bottom-up vs top-down per line type; gaps > 30 % outside the top-down range are flagged and explained by scope or left open, never averaged.
- Registers: `docs/assumptions-r1c.md` (A-cost-*, A-rcf-*), `docs/licences-r1c.md` / `.csv` (10 rows).

**Fixture result** (README command, seed 1, `runs/costs/fixture/`, code version `cp1-9-g5fbfaca`; cost ranges, price year 2025, not a budget; synthetic demand, uncalibrated: scenario comparison, not a forecast): capex base P10 / P50 / P90 = SAR 7,458 / 9,461 / 12,657 m; uplifted (U-capex-rail-sobc) P50 11,295, P80 25,434 m; opex per year P10 / P50 / P90 = 462 / 531 / 617 m. Re-run with the same seed gives byte-identical `base.yaml`, `trace.csv` and `distribution.parquet`.

**Checks**: `make test` green (ruff, pytest, docver 198 files, manifest 20 rows). Verifier: see the closing note below.

**Could not verify**: primary KSA cost documents (all secondary); unit costs listed in `docs/costs.md` §10 (commuter at-grade per km, sand fencing, desert halt station, Haramain depots, conventional viaducts, FRMCS/ETCS L3, hydrogen refuelling, diesel per train-km, renewal cost share) are `unknown` or `assumed` with a reason.

### R1c closing note (builder)
- Verifier: `red-team-verifier` **PASS** on all 8 criteria at `440ebb2`; seeded spot-check (seed 20261031) 21/21 register rows reproduce from source; DfT/OGP workbook percentiles reproduced to 4 d.p.; determinism byte-exact. Report `docs/status/verify-R1c.md`.
- Fixed after the PASS (not re-audited): verifier fix 2 (`assumption_id: A-cost-303` on C-opex-power-tariff-001/-002, so `meta.json` lists it when they are used; the fixture does not use them, its outputs are unchanged); fix 3 (Haramain forecast wording above; `docs/costs.md` §4.1 Landbridge "exactly as" corrected to name the high = central departure).
- Open for R4 (verifier fix 1, not done here because it changes fixture numbers): five estimator defaults have zero base spread (substations, stations, depot, rolling stock; about 28 % of base P50 capex; `costs/config/estimate_map.yaml` lines 47–61). Disclosed in `docs/costs.md` §6. Give them a low/high from alternative register rows or an assumed spread with an A-cost id before real corridors are costed.
- Minor verifier observations left for the coordinator: S-cost-rcf-008 locator points to a gitignored log; A-rcf-029/-030 `assumed` vs uplifts `derived`; S-lb-030 prints ±17 % where the EC figure is ±16 % (register uses 16 %); 30-year renewals P10 = 0 is correct arithmetic but unexplained.
- Cost: this run's row is appended by `run_track.sh` when the run ends.

R1c: done
