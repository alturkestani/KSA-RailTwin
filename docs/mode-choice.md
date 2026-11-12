> **Document version:** docs/mode-choice.md v0.2 | 31 Oct 2026 | Author: mode-choice-modeler (R3) | Status: draft

# Mode choice: intercity car, rail, air and bus (W8, R3)

> **Synthetic demand, uncalibrated: scenario comparison, not a forecast.**
> **Coefficients literature-based until survey results exist.** No coefficient is estimated from Saudi data; the W7 survey is designed, not fielded. Read every share below as a structured sensitivity of a literature-based model on a small table of representative pairs, not as a ridership estimate. Write "in the model, X", never "will".

## Commands

```
uv run python -m modechoice.cli pairs  --seed 1 --out runs/r3/modechoice/pairs-s1/
uv run python -m modechoice.cli shares --od runs/r3/modechoice/pairs-s1/pairs.parquet --seed 1 --out runs/r3/modechoice/shares-pairs-s1/
uv run python -m modechoice.cli sweep  --seed 1 --out runs/r3/modechoice/sweep/
uv run pytest tests/test_modechoice_mnl.py
```

Run ids (31 Oct 2026, seed 1, code `r2-int-dirty`): `runs/r3/modechoice/pairs-s1/`, `runs/r3/modechoice/shares-pairs-s1/` (shares + `shares_band.parquet`), `runs/r3/modechoice/sweep/` (config hash `b5a01c70…`, manifest hash `2e2e5e7b…`). Each `meta.json` lists the assumption ids the run used. Re-running the sweep reproduces every Parquet byte for byte (checked).

## Method

Generalised from TrafficTwin's binary car-vs-Loop logit (`docs/loop-mode-choice.md` in the read-only TrafficTwin checkout: one generalised-cost logit, one-at-a-time coefficient sweep plus a grid) to a multinomial logit over four modes. Car is the reference alternative (ASC 0). Code: `modechoice/mnl.py` (utility, shares, logsum), `modechoice/coefficients.py` (priors loader, sweep corners, calibration hook), `modechoice/pairs.py` (attribute builder), `modechoice/sweep.py`.

Utility per traveller and mode m:

```
V_m = ASC_m + b_ivt[m]·IVT_m + b_access·AE_m + b_headway·H_m + (b_cost / s_p)·C_m + b_ontime·(OT_m − 87.5)
P_m = exp(V_m − max V) / Σ_available exp(V_j − max V);   logsum = max V + ln Σ_available exp(V_j − max V)
```

- **IVT_m** in-vehicle minutes. Car: road skim minutes between the zone points (`runs/skims/national-governorates/skims.parquet`, OSRM car profile, free flow; car terminal time 0, A-mode-038). Rail: published or secondary journey times per pair (below); a hypothetical service (Landbridge) uses track km / (design speed × A-mode-036) + stops × 2 min (A-r1a-035). Air: block time 30 min + great-circle km / 12 km per min (A-mode-029). Bus: car skim × 1.15 (A-mode-033).
- **AE_m** access + egress minutes (A-mode-028: rail 20 + 20, air 60 + 30 including processing, bus 15 + 15; a zone without an airport adds the road skim to the host airport zone, Makkah → JED). **Summer first/last-mile penalty** (skill `isochrone-commute`): in the summer season AE_m × (1 + outdoor share_m × (multiplier − 1)), multiplier 1.5 (1.0 – 3.7, A-mode-026), outdoor share rail 0.3 / air 0.1 / bus 0.4 (A-mode-027). The default season is `other`; summer is a sweep variant.
- **H_m** headway, the minutes between departures, entered **as the headway itself, not headway/2**: the prior A-mode-008 is the inter-urban *headway* multiplier (0.46 × IVT, S-soc-302) and the SP design shows "a train every …" (docs/survey/design.yaml). A wait-time (headway/2) formulation would need the wait multiplier (1.76, S-soc-302) instead; it is not mixed in.
- **C_m** SAR per traveller. Car: fuel 2.18 SAR/L (S-soc-316) × km / 10 km/L (S-soc-317) + parking/tolls 0 (A-mode-024), divided by occupancy 2.0 (A-mode-022); perceived cost = fuel only (A-mode-023). Rail: published fares (below) or 0.30 SAR per track km for a line without one (A-mode-037). Air: 150 + 0.15 SAR per great-circle km (A-mode-030). Bus: 0.20 SAR per road km (A-mode-034, from SAPTCO fares S-soc-319).
- **OT_m** on-time share (rail and air only; car and bus have no term). HHR 97.8 % (S-014), East Train 96.1 %, North Train 94.3 % (S-r3-mode-001, GASTAT 2025), Landbridge 96.1 % proxy (A-mode-039), air 85 % (A-mode-032). Reference 87.5 = SP design midpoint (A-mode-025).
- **Availability** (A-mode-040): rail only where one line in the scenario has a station in both zones (no transfers in R3); air only where both zones map to different airports and the route is listed in `mode_choice_r3.yaml`; bus where road distance ≥ 50 km. Unavailable modes get utility −∞ and share 0; a row with nothing available gets shares 0 and logsum NaN.
- **Numerics**: vectorised NumPy over the OD table, max-subtracted exponentials (tested with 10⁶-minute utilities).

### Purpose treatment

The priors are not purpose-specific (A-mode-006 is the non-work inter-urban design VoT). Purposes commute, business, leisure_vfr, pilgrimage, tourism share the time coefficients; the cost coefficient is divided by the purpose VoT ratio to the A-cba-010 non-work value (A-mode-021): commute 82.6 / 37.7 = 2.19, business 134.3 / 37.7 = 3.56, the others 1.0 (no Saudi or Umrah VoT was found; S-soc-308 names Umrah as a distinct purpose but its coefficients were not obtained). Scaling money rather than time keeps the literature time sensitivities and reflects employer-paid business travel. Two alternatives run as sweep variants: `set:purpose_none` (one set for all purposes) and `set:purpose_ivt` (time coefficients × ratio). The method choice moves business shares a lot (table below), so it is a CP4 item, and the W7 survey's purpose segmentation replaces it.

| purpose | variant | JED-MED | JED-RUH (S1) | MAK-JED | MAK-MED | RUH-DMM | RUH-ELQ | RUH-HAS |
|---|---|---|---|---|---|---|---|---|
| business | base (cost scaling) | 40.5 | 12.5 | 24.9 | 38.2 | 11.5 | 6.4 | 7.2 |
| business | set:purpose_ivt | 66.3 | 0.1 | 4.1 | 45.0 | 0.5 | 0.0 | 0.1 |
| business | set:purpose_none | 25.4 | 11.2 | 19.6 | 20.4 | 10.0 | 4.9 | 6.0 |
| commute | base (cost scaling) | 37.2 | 12.4 | 23.5 | 33.6 | 11.4 | 6.1 | 7.1 |
| commute | set:purpose_ivt | 44.2 | 1.6 | 10.2 | 31.3 | 2.6 | 0.4 | 0.9 |
| commute | set:purpose_none | 25.4 | 11.2 | 19.6 | 20.4 | 10.0 | 4.9 | 6.0 |

Rail share in % of travellers on the pair in the model (`runs/r3/modechoice/sweep/sweep_long.parquet`).

## Coefficients and sources

All from `cities/ksa/assumptions/mode_choice_priors.yaml` (R1d, read-only; status "literature-based until survey results exist"; register rows A-mode-001…020 in `docs/assumptions.md`; sources in `docs/sources/r1d-soc-survey.csv`). Ranges are the swept ranges.

| key | value | unit | range | assumption | sources (from the prior's note) |
|---|---|---|---|---|---|
| asc.rail | -0.2 | utility | -1 to 0.5 | A-mode-010 | S-soc-337 |
| asc.air | -0.2 | utility | -1 to 0.5 | A-mode-011 | as A-mode-010 |
| asc.bus | -0.6 | utility | -1.5 to 0 | A-mode-012 | S-soc-307, S-soc-308 |
| ivt.car | -0.01 | utility per min | -0.02 to -0.005 | A-mode-001 | S-soc-303, S-soc-304, S-soc-337 |
| ivt.rail | -0.009 | utility per min | -0.018 to -0.005 | A-mode-002 | S-soc-305 |
| ivt.air | -0.012 | utility per min | -0.024 to -0.006 | A-mode-003 | S-soc-306 |
| ivt.bus | -0.007 | utility per min | -0.014 to -0.004 | A-mode-004 | S-soc-306 |
| access_egress | -0.017 | utility per min | -0.03 to -0.01 | A-mode-007 | S-soc-300, S-soc-302 |
| headway | -0.004 | utility per min | -0.006 to -0.002 | A-mode-008 | S-soc-300, S-soc-302 |
| cost | -0.013 | utility per SAR | -0.03 to -0.007 | A-mode-005 | derived (A-mode-001, A-mode-006) |
| on_time | 0.007 | utility per percentage point | 0.002 to 0.015 | A-mode-009 | S-soc-302 |
| comfort_upper_class | 0.4 | utility | 0 to 1 | A-mode-014 | S-soc-305 |
| women_only_or_family_carriage | 0.2 | utility | -0.2 to 0.6 | A-mode-015 | - |
| prayer_facilities | 0.2 | utility | 0 to 0.5 | A-mode-016 | - |
| luggage_large_allowance | 0.2 | utility | 0 to 0.5 | A-mode-017 | - |
| heat_shaded_transfer | 0.25 | utility | 0 to 0.6 | A-mode-018 | S-soc-301, S-soc-304 |
| aux.late_arrival_mean_delay | 30 | min | 15 to 60 | A-mode-013 | - |

`cost` is derived: A-mode-001 ÷ (A-mode-006 / 60), with A-mode-006 cross-checked against A-cba-010 (S-soc-322, S-soc-303). The last six rows (comfort, women-only or family carriage, prayer facilities, luggage, shaded transfer, late-arrival delay) are loaded and registered but **not in the R3 utility**: no line YAML carries these attributes yet; the late-arrival delay is already folded into the on-time prior. Implied values of time (A-mode-019): car 46.2, rail 41.5, air 55.4, bus 32.3 SAR/h.

New R3 parameters (not coefficients) are in `cities/ksa/assumptions/mode_choice_r3.yaml`, registered A-mode-021…041 in `docs/assumptions.md`; new sources S-r3-mode-001…005 in `docs/sources/r3-mode.csv`.

## Representative pairs (inputs)

Zone ids from `cities/ksa/zones/governorates.geojson`; road km/min from the national governorate skims; rail from `mode_choice_r3.yaml` (`representative_pairs`) and the read-only line YAMLs. S0 = existing lines (scenarios/S0.yaml); S1 = S0 + committed (Landbridge, announced/planned, rule 5).

| pair | zones | road km / min | rail IVT min (range; source) | rail fare SAR (source) | rail headway min | air | bus |
|---|---|---|---|---|---|---|---|
| RUH-DMM, SAR East | G138–G038 | 416.5 / 241.2 | 215 (215–270; S-r1a-040 secondary, upper end S-r1a-041 unverified bound) | 90 (S-r1a-024) | 270 (180–480; A-mode-041) | RUH-DMM | yes |
| RUH-ELQ, SAR North (Buraydah) | G138–G114 | 356.9 / 203.9 | 148 (148–160; S-r3-mode-002 secondary) | 80 (S-r1a-022) | 540 (360–1080) | RUH-ELQ | yes |
| RUH-HAS, SAR North | G138–G050 | 623.7 / 364.0 | 272 (240–360; S-r3-mode-003 secondary) | 125 (S-r1a-021) | 540 (360–1080) | RUH-HAS | yes |
| MAK-JED, HHR | G091–G089 | 85.7 / 58.3 | 43 (28–43; S-cp2-503 verified 2018 timetable) | 43 (S-r1a-012 secondary) | 60 (30–120; S-r1a-011) | none (same airport) | yes |
| MAK-JED-28 (input variant of MAK-JED) | G091–G089 | 85.7 / 58.3 | 28 (S-cp2-504 secondary current listing) | 43 | 60 | none | yes |
| JED-MED, HHR | G089–G072 | 405.5 / 278.9 | 135 (100–140; A-mode-041) | 150 (S-soc-318 secondary) | 60 | JED-MED | yes |
| MAK-MED, HHR | G091–G072 | 435.6 / 289.1 | 175 (120–175; S-cp2-503) | 160 (150–195; A-mode-041) | 60 | JED-MED via JED | yes |
| JED-RUH, no rail in S0; Landbridge in S1 | G089–G138 | 954.1 / 631.7 | S1: 874.3 km / (250 km/h × 0.60) + 3 × 2 min = 355.7 (A-mode-036, hypothetical) | S1: 874.3 × 0.30 = 262.3 (A-mode-037) | 240 (120–480) | RUH-JED | yes |

**Haramain reality check.** HHR Makkah–Jeddah: 77 km in about 43 minutes, average about 107 km/h on a 300 km/h line (S-005, S-cp2-503); current secondary listings give 28–30 min (S-cp2-504; conflict C-r1a-22). This model does not compute rail times: it uses those published times as inputs (43 min base, 28 min as the MAK-JED-28 input variant). The only modelled rail time is the hypothetical Landbridge placeholder, whose 0.60 speed ratio (A-mode-036) sits above HHR's 0.36–0.54 on the 78 km hop and is a placeholder until R4's running-time model reproduces the HHR timetable within ±10 % (skill `isochrone-commute`). No competitiveness or 30-minute claim is made from it.

## Sweep

TrafficTwin pattern. 33 coefficient and settings variants: `base`; `oat:<key>:low|high` for each of the 11 utility coefficients at both ends of its registered range (22); four joint corners (`all_low`, `all_high`, `rail_favourable`, `rail_unfavourable`; the rail corners hold cost at base because on every representative pair rail is dearer than car per person and cheaper than air, so the cost coefficient has no fixed rail-favouring end); six settings (`summer`, `summer_high` multiplier 3.7, car occupancy 1.2 and 3.5, `purpose_none`, `purpose_ivt`). Plus 26 input variants `in:<input>:low|high` at base coefficients (rail IVT, fare and headway per pair range; Landbridge speed ratio; fuel price and economy; parking; air block time, fare and headway; bus IVT, fare and headway). 59 variants × 80 rows (8 pairs × 2 scenarios × 5 purposes) = 4,720 rows, `runs/r3/modechoice/sweep/`.

### Rail share on the representative pairs, leisure/VFR (% of travellers on the pair, in the model)

S0 for the existing-line pairs (identical in S1); JED-RUH under S1 (rail unavailable, share 0, in S0). Source: `runs/r3/modechoice/sweep/rail_share_leisure_vfr.csv`.

| variant | JED-MED | MAK-JED | MAK-JED-28 | MAK-MED | RUH-DMM | RUH-ELQ | RUH-HAS | JED-RUH (S1) |
|---|---|---|---|---|---|---|---|---|
| base | 25.4 | 19.6 | 21.9 | 20.4 | 10.1 | 4.9 | 6.0 | 11.2 |
| oat:asc.rail:low | 13.3 | 9.9 | 11.2 | 10.3 | 4.8 | 2.3 | 2.8 | 5.4 |
| oat:asc.rail:high | 40.7 | 33.0 | 36.0 | 34.0 | 18.4 | 9.5 | 11.4 | 20.2 |
| oat:asc.air:low | 26.5 | 19.6 | 21.9 | 20.8 | 10.4 | 5.0 | 6.3 | 17.1 |
| oat:asc.air:high | 23.8 | 19.6 | 21.9 | 19.7 | 9.4 | 4.8 | 5.6 | 6.8 |
| oat:asc.bus:low | 26.7 | 20.8 | 23.1 | 21.5 | 10.6 | 5.2 | 6.4 | 11.4 |
| oat:asc.bus:high | 23.9 | 18.3 | 20.4 | 19.0 | 9.3 | 4.5 | 5.6 | 10.9 |
| oat:ivt.car:low | 57.7 | 28.7 | 31.5 | 55.9 | 31.1 | 17.6 | 23.6 | 14.5 |
| oat:ivt.car:high | 9.1 | 15.8 | 17.7 | 6.4 | 3.7 | 2.0 | 1.2 | 1.8 |
| oat:ivt.rail:low | 9.2 | 14.2 | 17.8 | 5.0 | 1.6 | 1.4 | 0.5 | 0.5 |
| oat:ivt.rail:high | 36.9 | 22.5 | 23.8 | 34.0 | 20.9 | 8.6 | 16.0 | 34.3 |
| oat:ivt.air:low | 26.4 | 19.6 | 21.9 | 20.7 | 10.4 | 5.0 | 6.3 | 19.9 |
| oat:ivt.air:high | 24.7 | 19.6 | 21.9 | 20.1 | 9.8 | 4.9 | 5.7 | 7.4 |
| oat:ivt.bus:low | 27.4 | 20.3 | 22.6 | 22.2 | 10.9 | 5.4 | 6.6 | 11.6 |
| oat:ivt.bus:high | 22.5 | 19.2 | 21.4 | 17.7 | 9.0 | 4.5 | 4.9 | 8.9 |
| oat:access_egress:low | 18.4 | 13.1 | 14.7 | 14.1 | 6.7 | 3.1 | 4.0 | 13.0 |
| oat:access_egress:high | 29.0 | 23.9 | 26.5 | 23.5 | 12.0 | 6.2 | 7.2 | 9.3 |
| oat:headway:low | 24.4 | 18.5 | 20.6 | 19.3 | 6.4 | 1.8 | 2.3 | 7.6 |
| oat:headway:high | 26.1 | 20.5 | 22.8 | 21.1 | 15.2 | 12.4 | 14.5 | 16.0 |
| oat:cost:low | 6.2 | 12.3 | 13.8 | 4.0 | 5.6 | 2.7 | 2.8 | 2.7 |
| oat:cost:high | 35.5 | 22.9 | 25.4 | 31.5 | 11.3 | 5.9 | 7.0 | 12.4 |
| oat:on_time:low | 24.5 | 18.8 | 21.0 | 19.6 | 9.7 | 4.8 | 5.8 | 10.7 |
| oat:on_time:high | 27.1 | 21.0 | 23.3 | 21.8 | 10.7 | 5.2 | 6.3 | 12.0 |
| joint:all_low | 7.0 | 4.0 | 5.2 | 3.5 | 1.5 | 0.5 | 0.8 | 2.7 |
| joint:all_high | 37.2 | 40.3 | 42.1 | 35.3 | 25.3 | 20.3 | 19.6 | 21.8 |
| joint:rail_favourable | 94.6 | 63.1 | 64.9 | 94.9 | 91.7 | 84.1 | 95.8 | 92.8 |
| joint:rail_unfavourable | 0.7 | 2.8 | 3.6 | 0.3 | 0.1 | 0.1 | 0.0 | 0.0 |
| set:summer | 23.9 | 18.2 | 20.3 | 19.0 | 9.3 | 4.5 | 5.5 | 10.8 |
| set:summer_high | 17.6 | 12.9 | 14.5 | 13.7 | 6.5 | 3.1 | 3.8 | 8.9 |
| set:occupancy_low | 31.4 | 20.8 | 23.1 | 26.4 | 13.2 | 6.5 | 9.1 | 13.0 |
| set:occupancy_high | 21.8 | 18.9 | 21.1 | 16.9 | 8.3 | 4.1 | 4.5 | 9.5 |
| set:purpose_none | 25.4 | 19.6 | 21.9 | 20.4 | 10.1 | 4.9 | 6.0 | 11.2 |
| set:purpose_ivt | 25.4 | 19.6 | 21.9 | 20.4 | 10.1 | 4.9 | 6.0 | 11.2 |
| in:air_block:high | 25.8 | 19.6 | 21.9 | 20.5 | 10.2 | 5.0 | 6.1 | 13.3 |
| in:air_block:low | 25.1 | 19.6 | 21.9 | 20.3 | 9.9 | 4.9 | 5.9 | 9.6 |
| in:air_fare:high | 27.1 | 19.6 | 21.9 | 21.0 | 10.6 | 5.0 | 6.5 | 27.5 |
| in:air_fare:low | 22.4 | 19.6 | 21.9 | 19.1 | 8.8 | 4.8 | 4.8 | 2.8 |
| in:air_headway:high | 26.2 | 19.6 | 21.9 | 20.6 | 10.2 | 5.0 | 6.3 | 12.0 |
| in:air_headway:low | 25.0 | 19.6 | 21.9 | 20.2 | 10.0 | 4.9 | 5.7 | 10.8 |
| in:bus_fare:high | 26.0 | 19.8 | 22.0 | 20.9 | 10.3 | 5.1 | 6.2 | 11.4 |
| in:bus_fare:low | 25.4 | 19.6 | 21.8 | 20.3 | 10.0 | 4.9 | 6.0 | 11.2 |
| in:bus_headway:high | 27.3 | 21.3 | 23.6 | 22.1 | 10.9 | 5.4 | 6.6 | 11.5 |
| in:bus_headway:low | 23.5 | 17.9 | 20.0 | 18.6 | 9.2 | 4.5 | 5.5 | 10.8 |
| in:bus_ivt:high | 26.1 | 19.8 | 22.0 | 21.0 | 10.3 | 5.1 | 6.3 | 11.4 |
| in:bus_ivt:low | 25.0 | 19.6 | 21.8 | 20.0 | 9.9 | 4.9 | 5.9 | 11.0 |
| in:fuel_economy:high | 23.0 | 19.1 | 21.3 | 18.0 | 8.8 | 4.4 | 4.9 | 10.1 |
| in:fuel_economy:low | 27.7 | 20.1 | 22.3 | 22.6 | 11.2 | 5.5 | 7.1 | 12.0 |
| in:fuel_price:high | 26.1 | 19.8 | 22.0 | 21.0 | 10.3 | 5.1 | 6.3 | 11.4 |
| in:fuel_price:low | 25.4 | 19.6 | 21.9 | 20.4 | 10.1 | 4.9 | 6.0 | 11.2 |
| in:parking:high | 28.4 | 22.5 | 24.9 | 23.1 | 11.6 | 5.8 | 7.0 | 11.7 |
| in:parking:low | 25.4 | 19.6 | 21.9 | 20.4 | 10.1 | 4.9 | 6.0 | 11.2 |
| in:rail_fare:high | 25.4 | 19.6 | 21.9 | 14.0 | 10.1 | 4.9 | 6.0 | 3.7 |
| in:rail_fare:low | 25.4 | 19.6 | 21.9 | 22.6 | 10.1 | 4.9 | 6.0 | 28.2 |
| in:rail_headway:high | 21.2 | 16.1 | 18.0 | 16.8 | 4.6 | 0.6 | 0.7 | 4.6 |
| in:rail_headway:low | 27.8 | 21.6 | 24.0 | 22.4 | 13.8 | 9.6 | 11.6 | 16.9 |
| in:rail_ivt:high | 24.6 | 19.6 | 21.5 | 20.4 | 6.4 | 4.5 | 2.8 | 11.2 |
| in:rail_ivt:low | 31.9 | 21.9 | 21.9 | 29.6 | 10.1 | 4.9 | 7.9 | 11.2 |
| in:rail_speed:high | 25.4 | 19.6 | 21.9 | 20.4 | 10.1 | 4.9 | 6.0 | 21.7 |
| in:rail_speed:low | 25.4 | 19.6 | 21.9 | 20.4 | 10.1 | 4.9 | 6.0 | 4.2 |


Reading it: the base column ranks the pairs JED-MED > MAK-MED > MAK-JED > JED-RUH (S1) > RUH-DMM > RUH-HAS > RUH-ELQ. The levers that move rail most are the car and rail IVT coefficients, the rail ASC, the cost coefficient and (on the North pairs) the headway coefficient and the North headway input. The joint corners span almost the whole 0–100 % interval: the priors' ranges alone cannot bound a share until the survey or calibration narrows them. On the North pairs the headway term dominates because the North line runs about once a day per direction (S-r3-mode-003), far outside the 30–120 min headway levels the inter-urban headway multiplier was estimated on (S-soc-302): treat the North rail shares as the least reliable in the table.

### Sensitivity band (rail share %, min / median / max over all 59 variants; not a probability distribution)

`runs/r3/modechoice/sweep/band.parquet` (all purposes and modes). Three purposes shown; pilgrimage and tourism equal leisure/VFR by construction (A-mode-021).

| pair_id | scenario | purpose | rail_base | rail_min | rail_median | rail_max | car_base | air_base | bus_base |
|---|---|---|---|---|---|---|---|---|---|
| JED-MED | S0 | business | 40.5 | 1.6 | 40.5 | 94.9 | 35.2 | 17.6 | 6.7 |
| JED-MED | S0 | commute | 37.2 | 1.3 | 37.2 | 95.1 | 41.2 | 14.5 | 7.2 |
| JED-MED | S0 | leisure_vfr | 25.4 | 0.6 | 25.4 | 94.6 | 59.5 | 7.0 | 8.0 |
| JED-RUH | S1 | business | 12.5 | 0.0 | 12.5 | 91.9 | 5.8 | 79.8 | 1.8 |
| JED-RUH | S1 | commute | 12.4 | 0.0 | 12.4 | 92.1 | 8.4 | 77.0 | 2.2 |
| JED-RUH | S1 | leisure_vfr | 11.2 | 0.0 | 11.2 | 92.8 | 23.0 | 62.6 | 3.2 |
| MAK-JED | S0 | business | 24.9 | 3.8 | 24.9 | 70.0 | 66.0 | 0.0 | 9.1 |
| MAK-JED | S0 | commute | 23.5 | 3.5 | 23.5 | 68.4 | 67.4 | 0.0 | 9.1 |
| MAK-JED | S0 | leisure_vfr | 19.6 | 2.8 | 19.6 | 63.1 | 71.3 | 0.0 | 9.1 |
| MAK-MED | S0 | business | 38.2 | 0.9 | 38.2 | 96.0 | 44.1 | 9.2 | 8.5 |
| MAK-MED | S0 | commute | 33.6 | 0.7 | 33.6 | 95.9 | 50.2 | 7.4 | 8.8 |
| MAK-MED | S0 | leisure_vfr | 20.4 | 0.3 | 20.4 | 94.9 | 67.3 | 3.4 | 8.9 |
| RUH-DMM | S0 | business | 11.5 | 0.1 | 11.5 | 89.3 | 56.3 | 22.3 | 9.9 |
| RUH-DMM | S0 | commute | 11.4 | 0.1 | 11.4 | 90.4 | 61.8 | 16.8 | 10.0 |
| RUH-DMM | S0 | leisure_vfr | 10.0 | 0.1 | 10.0 | 91.7 | 74.4 | 6.4 | 9.2 |
| RUH-ELQ | S0 | business | 6.4 | 0.0 | 6.4 | 84.5 | 73.2 | 8.2 | 12.2 |
| RUH-ELQ | S0 | commute | 6.1 | 0.1 | 6.1 | 84.9 | 76.2 | 5.9 | 11.8 |
| RUH-ELQ | S0 | leisure_vfr | 4.9 | 0.0 | 4.9 | 84.1 | 82.8 | 2.1 | 10.2 |
| RUH-HAS | S0 | business | 7.2 | 0.0 | 7.2 | 91.6 | 53.6 | 28.0 | 11.2 |
| RUH-HAS | S0 | commute | 7.1 | 0.0 | 7.1 | 93.1 | 60.4 | 21.4 | 11.1 |
| RUH-HAS | S0 | leisure_vfr | 6.0 | 0.0 | 6.0 | 95.8 | 76.5 | 8.1 | 9.4 |


### Scenario comparison against the matched baseline

S1 vs S0 on the same zones, seed, skims and coefficients (rule 6), `runs/r3/modechoice/sweep/scenario_effect_S1_vs_S0.parquet`. Only JED-RUH changes (the other pairs' rail options are identical in both scenarios; checked: zero difference on every other row). In the model, the Landbridge placeholder service takes a rail share of 11.2 % of leisure/VFR travellers on JED-RUH at base (12.4 % commute, 12.5 % business); over the 59 variants the change runs from 0.0 to 92.8 points (median 11.2). At base, in the model, the air share on the pair falls from 70.4 % to 62.6 % and car from 25.9 % to 23.0 %. Logsum change at base, leisure/VFR: −6.319 → −6.200, i.e. about SAR 9.1 per traveller (Δlogsum / 0.013). That is a scenario comparison on an uncalibrated placeholder service, not a benefit estimate: W4 reads it only after CP4.

### Monotonicity checks

For every coefficient and every row with rail available (825 checks): the rail share at the coefficient's high end against its low end. Theory used: dP_rail/db = P_rail (x_rail − x̄) and dx̄/db = Var(x) ≥ 0, so the rail share rises then falls in b with at most one turning point; where the derivative has the same sign at both range ends the share is monotone across the range and the observed change must have that sign. Result (`monotonicity.parquet`): **799 pass, 0 FAIL, 26 "turning point in range"** (not testable as monotone: access/egress on JED-MED, MAK-MED, RUH-HAS, where air's longer access makes a heavier access weight help rail against air while hurting it against car; cost on RUH-DMM, RUH-HAS, JED-RUH, where rail sits between car-per-person and air in price; headway on JED-MED and MAK-MED, where rail's 60 min headway is shorter than air's and bus's). The named checks all hold on every rail row: rail share falls when the rail IVT coefficient is more negative, rises when the rail ASC rises, falls when the cost coefficient is more negative wherever rail is dearer than the share-weighted mean cost (here: on every pair rail is dearer than car per person), falls with a heavier access weight or a summer penalty where car is the main competitor, and rises when the car IVT coefficient is more negative. `tests/test_modechoice_mnl.py` repeats these checks on the six-zone fixture.

### Rank stability

Spearman ρ of the ordering of pairs by rail share, base vs each variant, per scenario and purpose (`rank_stability.parquet`; the MAK-JED-28 input variant excluded; 6 pairs in S0, 7 in S1).

| scenario | variant group | n | ρ min | ρ median | identical order |
|---|---|---|---|---|---|
| S0 | one at a time | 110 | 0.71 | 1.00 | 72 % |
| S0 | joint corners | 20 | 0.14 | 0.77 | 10 % |
| S0 | settings | 30 | 0.94 | 1.00 | 90 % |
| S0 | inputs | 130 | 0.94 | 1.00 | 88 % |
| S1 | one at a time | 110 | 0.64 | 1.00 | 55 % |
| S1 | joint corners | 20 | 0.18 | 0.77 | 0 % |
| S1 | settings | 30 | 0.96 | 1.00 | 73 % |
| S1 | inputs | 130 | 0.75 | 1.00 | 67 % |

The ordering is stable to single-coefficient and input changes (ρ ≥ 0.64) and to the settings; it is not stable to the joint rail-favourable/unfavourable corners (ρ down to 0.14), which compress every pair to near 0 % or near 100 %. The most frequent adjacent swaps: RUH-ELQ / RUH-HAS (54 variant-purpose cases), MAK-JED / MAK-MED (46), JED-MED / MAK-JED (44) and JED-RUH / RUH-DMM (41). The variants that most often push ρ below 0.8: the two rail joint corners, rail IVT at its low end, car IVT at its high end and cost at its low end.

## Outputs for economics (W4): logsum, no double counting

`shares` writes per OD row `logsum` and `b_cost_eff` (the cost coefficient used on that row, purpose-scaled). The user benefit per traveller is `consumer_surplus_change_sar(logsum_base, logsum_scenario, b_cost_eff)` = (LS_scn − LS_base) / −b_cost_eff, computed on the matched baseline (same OD, purpose, coefficients). That logsum change already contains the benefit to existing and to new (diverted) rail users; W4 must use it **or** the rule-of-a-half on generalised cost (GC = −V / −b_cost per mode, from the same utilities) for the same OD and purpose, never both, and must not add a separate time-saving item for diverted travellers on top. Induced demand (total trips responding to the logsum) is not in R3; it belongs to `demand/gravity.py` with a registered elasticity.

## The 30-minute commute lens: inputs R4 needs from this model

The isochrone work (skill `isochrone-commute`, R4) computes door-to-door times; to turn them into "in the model, X % of car trips shifted" it needs from here:

1. The utility function and coefficients: `modechoice.mnl.shares` with `base_coefficients()` and the sweep corners (`modechoice.sweep.variants`), purpose `commute` (cost scaling ratio 2.19, A-mode-021).
2. The generalised-time components with the same definitions: IVT; access + egress with the summer multiplier (A-mode-026) and outdoor shares (A-mode-027), replaced by R4's station access skims (the A-mode-028 defaults are placeholders); headway as headway (not headway/2) unless R4 switches to a wait formulation and the wait multiplier; fare per traveller; car cost per vehicle / occupancy (A-mode-022, A-mode-023).
3. Availability rule replacement: R4's rail graph decides rail availability and transfers (A-mode-040 is an R3 placeholder).
4. The running-time model (R4) must replace the hypothetical speed ratio A-mode-036 and reproduce HHR within ±10 % before any hypothetical line's share is reported.
5. The car side: the free-flow skim plus the AM-peak factor of the isochrone-commute skill (its id is not yet registered) for metro commutes; this model has no peak factor.

## Calibration hook (R3 `demand/calibrate.py`)

Only the ASCs may be adjusted, within their registered ranges (`calibration_hook` in `mode_choice_r3.yaml`; asc.rail and asc.air −1.0 to 0.5, asc.bus −1.5 to 0.0):

```python
from modechoice.coefficients import apply_overrides, base_coefficients, load_priors

priors = load_priors()
coefs = apply_overrides(base_coefficients(priors), {"asc.rail": -0.4, "asc.air": 0.1}, priors)
# ValueError if a value is outside the prior's range; KeyError for a non-coefficient key
```

The caller logs every adjustment; `apply_overrides` tags the overridden keys in `coefs.tags`. The coefficients' status flips to `calibrated` only through calibration against an observed total within the tolerance of `cities/ksa/assumptions/demand_calibration.yaml`, never globally.

## API (for `demand/gravity.py` and `demand/calibrate.py`)

- `modechoice.coefficients.load_priors(path=PRIORS_PATH) -> dict[str, Param]`; `load_r3(path=R3_PATH) -> dict`; `base_coefficients(priors=None) -> Coefficients`; `corner(priors, {key: "low"|"base"|"high"}) -> Coefficients`; `apply_overrides(coefs, overrides, priors=None) -> Coefficients`.
- `modechoice.mnl.Settings.from_r3(r3=None, priors=None, **overrides)`; `shares(od, coefs, settings=None) -> DataFrame` (adds `share_car|rail|air|bus`, `logsum`, `b_cost_eff`, `any_avail`); `utilities(od, coefs, settings) -> (V, b_cost_eff)`; `consumer_surplus_change_sar(ls_base, ls_scn, b_cost_eff)`.
- `modechoice.pairs.build_attributes(od, r3, skims, points, scenario, rail_specs=None, inputs=None) -> DataFrame` fills the per-mode columns for any `o, d, purpose` table from the skims (`load_skims()`), zone points (`load_points()`) and the R3 YAML. Without `rail_specs` rail is unavailable (R3 has no zone-to-station skims).
- `modechoice.sweep.variants(priors, r3, settings)`, `run_sweep(od, variants)`, `band(long)`, `monotonicity(od, priors, settings)`, `rank_stability(long)`, `scenario_effect(long, "S1", "S0")`.

Input columns: `o, d, purpose` and per mode `ivt_min_<m>, access_min_<m>, egress_min_<m>, headway_min_<m>, cost_sar_<m>` (car: per vehicle), `ontime_<m>` (NaN = no term), `avail_<m>`.

## Limits

- Every coefficient is a literature prior; the joint corners show the ranges are wide enough to make any rail share between about 0 % and 96 % possible on these pairs. Until calibration (ASCs only) and the survey, compare scenarios, do not read levels.
- Rail times and fares of the existing lines are published or secondary values sampled on 30–31 Oct 2026, not modelled; SAR prints no timetable (S-r1a-025, S-015). The Landbridge service is a placeholder.
- Air block times, fares, headways and route existence are assumptions: no open GACA city-pair table and no readable airline schedule (S-r1a-218; S-r3-mode-004/005 unverified).
- No transfers, no capacity constraint, no nests: the MNL has the IIA property (a new rail service draws from car, air and bus in proportion to their shares). A nested car-vs-public-modes test is the next step once calibration targets exist.
- No comfort, women-only or family carriage, prayer, luggage or shaded-transfer terms yet (their priors are registered; no line data carries them).
