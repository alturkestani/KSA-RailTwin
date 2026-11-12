> **Document version:** docs/sources/cost-notes-opex.md v0.1 | 31 Oct 2026 | Author: cost-estimator (R1c task 4, topic `opex`) | Status: draft

# R1c task 4: opex, lifecycle and financing parameters

Rows: `cities/ksa/costs/cost_register.yaml` (38 rows: 13 sourced, 15 derived, 6 assumed, 4 unknown; validated against `CostItem`). Sources: `docs/sources/cost-opex.csv` (S-cost-opex-001 to -030), plus reused ids S-cp1-074/075/076/078/079 (sovereign rates, as in A-cba-003), S-cp1-087 (TAG asset lives), S-lb-021 (Haramain 450 km), S-lb-009 (Landbridge "seven-year" scheme) and S-al_baha-008 (Haramain opening). All values are in the source currency and price year. Arithmetic was run in Python on 2026-10-31. Figures are inputs to ranges, not forecasts.

## 1. Train operation cost per train-km
- **HSR, fully allocated (Amtrak Acela):** USD 93 per train-mile in FY2019 and USD 152 in FY2022, which is 57.79 and 94.45 USD per train-km (S-cost-opex-010; Eno analysis of Amtrak monthly reports, `secondary`). The two years are kept as separate rows so that price years are not mixed. Each row is one sourced figure, converted from miles to km, so low = central = high. **Flag:** this is the only single-point form in the file. Replace it with a range once the FRA Amtrak Performance Tracking appendices or Amtrak monthly reports are read.
- **Conventional intercity, fully allocated (Amtrak non-Acela):** FY2019: 36.04 / 44.12 / 53.44 USD per train-km. FY2022: 42.87 / 54.06 / 77.05 (S-cost-opex-010).
- **Conventional, operator train-operation cost (EC CBA Guide 2014 case study):** EUR 3.3 per train-km (short distance) and 3.95 (long distance) (S-cost-opex-006, `verified`). These are illustrative, country-specific values.
- **Freight:** JASPERS 2010 traction cost per train-km: electric 3.12, diesel 4.39 (EU15, without taxes) to 5.59 (with taxes) (S-cost-opex-009). The EC case uses 4.01 EUR per freight train-km (S-cost-opex-006). Freight cost **per tonne-km was not found**.
- **Conflict (kept, not averaged):** Amtrak's fully allocated cost per train-km (USD 36-94) is an order of magnitude above the EC operator figure (EUR 3.3-3.95; different currencies and years, not converted here). Analysis: the scope differs. Amtrak's figure includes stations, sales, overheads and, on the NEC, infrastructure. The EC figure is variable crew and vehicle cost only. Corridor costing must choose a scope and avoid double counting with the maintenance-of-way and rolling-stock rows.
- **Not found:** World Bank (2019) *China's High-Speed Rail Development*. Both the documents1 PDF and the OKR bitstream returned 404/403 on 2026-10-31, so it was not read. Renfe, SNCF and Eurostar filings were not reached within the budget. CHSRA 2024 O&M Cost Model Documentation: the PDF returned no text.

## 2. Energy
- **HSR, from the grid:** 11.90-19.45 kWh per train-km, simulated for 250-320 km/h trains on a 467 km Swedish new line. Central 16.31 is the Table 6 average at 320 km/h (S-cost-opex-011, KTH 2009, `verified`). **Caveat:** Swedish climate. No desert air-conditioning load is included, so a KSA value is likely higher (analysis, not quantified).
- **Conventional electric, measured at the pantograph:** 7.34 (3-car EMU), 10.09 (X2000-5) and 16.51 kWh per train-km (loco + 8 cars) (S-cost-opex-012). On the grid side, the X2000 uses 11.87-13.6 (S-cost-opex-013).
- **Secondary only (not used):** 21.4 kWh/km average for four Chinese 350 km/h types, and a ~43 kWh/km figure for a 16-car Shinkansen 500 (S-cost-opex-029, `unverified` popular media).
- **KSA electricity tariff:** under the 2026 rates, industrial is 20 halalas/kWh and commercial is 22 halalas/kWh up to 6,000 kWh/month and 32 above. From 1 Jan 2027 these become 23, 25 and 35 (MEED, 26 Oct 2026, S-cost-opex-014, `secondary`). The government tier is reported at 32 rising to 35 (S-cost-opex-015, `unverified`). The Saudi Energy tariff page returned "Rejected". Which tariff class applies to rail traction supply is unknown (A-cost-303), so the central value is the midpoint (derived).
- **KSA diesel:** SAR 1.79 per litre from 1 Jan 2026, up 7.8% (MEES, S-cost-opex-016, `secondary`). The Aramco price page returned 404. **Schema gap:** `CostItem` has no `SAR_per_litre` or `litre_per_train_km` unit, so the diesel price is not a register row. Diesel use per train-km is `unknown` (C-opex-conv-diesel-001). This matters because the SAR North and East passenger and freight fleets are diesel.

## 3. Maintenance of way, sand and rolling-stock maintenance
- **HSR:** EUR (2002) 12,919-71,650 per single-track km per year. The source gives about 30,000 for Belgium, France and Spain (S-cost-opex-001, Campos, de Rus and Barrón, WCTR 2007 paper, `verified`; the 2009 Transport Policy version is paywalled). Converted to double-track route-km with JASPERS's 1.67 factor (2.0 at the high end), this gives 21,575 / 50,100 / 143,300 (derived).
- **Conventional:** EUR (2002) 20,325-59,903 per single-track km, median 39,557 (S-cost-opex-002). EC CBA case: EUR 29,717 (business as usual) to 37,500 per track-km (S-cost-opex-005). JASPERS 2010 defaults: EUR 42,859-65,629 per km of double track, median 46,579 (S-cost-opex-008).
- **Sand:** no published cost was found for Haramain, SAR North/East, Etihad Rail, SNIM or Tazara. Searches: web (English, plus Arabic for SAR); the Glabeke et al. (2022) life-cycle cost paper on sand mitigation (polito.it, 403, not read); a Namibian thesis on the Aus-Lüderitz line (snippet only, no per-km figure); Rail Journal and IMechE coverage of Haramain (qualitative: slab track covered by sand). This gives assumption A-cost-302: +5% to +100% (central +25%) over flat maintenance of way, on the dune share only.
- **Rolling stock (HSR):** about EUR 1 m per trainset per year, about 2 EUR per km; range 1.4-4.0 EUR per train-km (2002) (S-cost-opex-003). Maintenance as a percentage of capex is `unknown`.

## 4. Staffing and Saudisation
- **Haramain headcount:** Renfe's Saudi branch had more than 1,300 direct workers in Jan 2023, "most of them Saudi" (S-cost-opex-021). A 2013 projection put the total at more than 3,000 employees, more than 70% Saudi (S-cost-opex-022, `unverified`). A 2018 official spoke of more than 2,000 jobs for Saudis (S-cost-opex-030). Over 450 km this gives 2.89-6.67 FTE per route-km (derived; the low end covers the operator only).
- **Saudisation share (A-cost-300):** 70-95%, central 88%. Evidence (all `unverified` snippets): SAR above 88% (Daleel, Nov 2024, S-cost-opex-023); SAR 89% in 2025 (Sabq, S-cost-opex-024); GASTAT rail passenger localization 86.29% in 2021 (Statista, S-cost-opex-027). The Nitaqat rules found are profession-based (engineering 30%, project management 70% from Feb 2027, per press); no rail-specific Nitaqat band was found.
- **Wages:** GASTAT Q2 2025 all-sector averages are SAR 11,034 a month for Saudis and SAR 3,933 for expatriates (S-cost-opex-025, `secondary`). Annual blended pay is 47,196-132,408, with a central of 122,183 at an 88% Saudi share (derived). No rail-specific wage was found. A-cost-301 adds the on-cost and skill multiplier.

## 5. Renewals and asset lives
- TAG A1.1 Table 2 (S-cp1-087, reused) gives these lives: track 14-40 years; electrification 30-40; signalling 10-50; telecoms 7-40; buildings 30-40; earthworks 100; bridges and tunnels up to 100. TAG A5.3 (2018) sets minimum rolling-stock lives of 30 years for DMUs and 35 for EMUs (S-cost-opex-026). The EC reference period for rail is 30 years (S-cost-opex-004). The project uses 60 years plus 30/40 variants (A-cba-004).
- **Renewal cost as a % of initial capex:** `unknown`. The EC Guide treats replacements as explicit cash flows; UIC LICB is not public. Suggested default for the coordinator to decide (not registered here): renew each asset class at 100% of its initial unit capex at end of life.

## 6. Financing
- **(a) Sovereign:** reused A-cba-003 evidence. NDMC 10-year 4.875% and 30-year 5.875% (Jan 2026); 10-year sukuk 5.598% (Sep 2026). Nothing newer was found.
- **(b) PIF:** 10-year USD sukuk in Jan 2026: USD 2 bn at 5.13%, about T+85 bp (S-cost-opex-019). Jan 2024 bonds: T+115 / 145 / 205 bp for 5 / 10 / 30 years (S-cost-opex-020). Both are `secondary`; PIF's own pages returned 403. No PIF green-bond coupon was read.
- **(c) Project-finance margin:** no open source for a GCC rail PPP was found. A-cost-304 sets 1.0-3.5 percentage points over SOFR. The PP11 IPP schedule of 250-350 bp (S-cost-opex-028) is an `unverified`, LIBOR-era snippet.
- **(d) Export credit:** OECD CIRR valid 15 Oct-14 Nov 2026: USD 5.73-5.99%, EUR 4.15-4.49% (S-cost-opex-017, `verified`). Saudi Arabia is OECD country risk category 2 (S-cost-opex-018, `verified`). The ECA premium itself is `unknown`.
- **(e) IDC:** the EC CBA Guide puts IDC in the financing plan, outside the economic CBA (worked example: EUR 4.8 m IDC funded by shareholders, loan at 4% real; S-cost-opex-007). IDC is a computed item: construction period (A-cost-305, 5-10 years, central 7) × drawdown profile (A-cost-306) × the rate from (a)-(d) for the financing structure in question.

## Conflicts
- Amtrak fully allocated vs EC operator cost per train-km: different scopes, both kept (see 1).
- Double-track maintenance factor: JASPERS uses 1.67 × single track; scaling by track-km gives 2.0. Both are used, one at each end of the derived range.
- HSR energy: KTH simulations (11.9-19.5) vs the popular-media China figure (21.4, unverified). Only KTH is registered.

## Proposed assumption rows (block A-cost-300 to A-cost-349)
| id | parameter | value | unit | range | source or assumption | status | used in |
|---|---|---|---|---|---|---|---|
| A-cost-300 | Saudi share of railway O&M workforce (Saudisation share) | 88 | % | 70-95 | Assumption. Evidence: SAR >88% (Nov 2024, S-cost-opex-023), 89% in 2025 (S-cost-opex-024), HHR 2013 target >70% (S-cost-opex-022), GASTAT rail passenger 86.29% in 2021 (S-cost-opex-027); all unverified snippets. Low = HHR target; high allows for Nitaqat tightening | assumed (approval pending) | C-opex-staff-saudisation-001, C-opex-staff-wage-001 |
| A-cost-301 | loaded-cost and rail-skill multiplier on the all-sector average wage | 150 | % of average wage | 120-200 | Assumption: no rail wage or loaded-cost source found; covers social insurance, allowances and a skill premium | assumed (approval pending) | C-opex-staff-oncost-001 |
| A-cost-302 | sand-maintenance uplift on maintenance of way, dune terrain | +25 | % over the flat base | +5 to +100 | Assumption: only qualitative evidence (sand covering slab track, jamming turnouts); no cost published for any desert railway found | assumed (approval pending) | C-opex-dunes-sand-maint-001 |
| A-cost-303 | electricity tariff class for rail traction supply | midpoint of industrial and commercial/government tiers | SAR/kWh | industrial (low) to the top commercial/government tier (high) | Assumption: the tariff class for SAR/HHR traction power was not found | assumed (approval pending) | C-opex-power-tariff-001, -002 |
| A-cost-304 | project-finance senior margin, Saudi rail PPP | 2.0 | percentage points over SOFR | 1.0-3.5 | Assumption: no open GCC rail PPP pricing; upper end informed by PP11 IPP 250-350 bp (S-cost-opex-028, unverified) | assumed (approval pending) | C-financing-pf-margin-001 |
| A-cost-305 | construction period for IDC | 7 | years | 5-10 | Assumption: Landbridge "seven-year" scheme (S-lb-009); Haramain opened Oct 2018 (S-al_baha-008); overruns handled by reference-class uplift | assumed (approval pending) | C-financing-construction-period-001 |
| A-cost-306 | capex drawdown profile: share drawn in the first half of construction | 40 | % | 30-50 | Assumption: back-loaded S-curve to uniform; no KSA drawdown data | assumed (approval pending) | C-financing-drawdown-001 |

## Unknowns (rows with status `unknown`) and where searched
- C-opex-conv-diesel-001: diesel use per train-km (plus the missing litre units in the schema).
- C-renewal-cost-share-001: renewal cost as a % of capex.
- C-opex-rs-maint-share-001: rolling-stock maintenance as a % of capex per year.
- C-financing-eca-premium-001: ECA premium for a Saudi borrower.
- Not registered (not found): World Bank China HSR O&M costs; freight cost per tonne-km; any sand-maintenance cost; a rail-specific Saudi wage; any PIF green-bond coupon.

## Primaries to find
1. Campos & de Rus (2009) Transport Policy 16(1):19-28, published version (the WCTR 2007 paper was used).
2. World Bank (2019) *China's High-Speed Rail Development* (CC BY 3.0 IGO): O&M chapters (403/404 today).
3. Amtrak Monthly Performance Reports (Sep 2019, Sep 2022, FY2025) or FRA APT appendices: cost per train-mile.
4. Saudi Energy (se.com.sa) official consumption-tariff schedule (2026 and 2027).
5. Aramco gasoline and diesel prices page (current diesel price).
6. SAR annual or sustainability report 2025: headcount, Saudisation %, fuel use (litres) and train-km.
7. PIF press releases and pricing supplements (Jan 2024 bonds, Jan 2026 sukuk; green bonds).
8. GASTAT Labour Market Statistics Q2 2025 wage table (by sector, if published).
9. Glabeke et al. (2022) life-cycle cost of sand mitigation measures (polito.it, 403 today).
10. A current Saudi or GCC PPP financing announcement with a margin over SOFR.
