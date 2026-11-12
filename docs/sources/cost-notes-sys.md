> **Document version:** docs/sources/cost-notes-sys.md v0.1 | 31 Oct 2026 | Author: cost-estimator (R1c research subagent, topic `sys`) | Status: draft

# R1c task 3: bottom-up capex library, SYSTEMS part: research notes

Outputs: `docs/sources/cost-sys.csv` (S-cost-sys-001 to -040), `cities/ksa/costs/cost_register.yaml` (47 CostItem rows, validated against `common.schemas.CostItem`). Reused ids: S-lb-030 (EC/PwC 2018), S-009 (Talgo Haramain order), S-008 (phase II award date). Every figure was recorded as printed, in its source currency and price year. Nothing was converted. All per-unit divisions were run in Python on 31 Oct 2026.

Row status: 10 sourced, 27 derived, 2 assumed, 8 unknown.

Many rows have low = central = high. These are single published contracts. A range was used only where the source gives one. Spread across contracts lives in the cross-row comparison and the reference-class uplift. These rows are not invented bands.

## 1. Stations by class

| class | rows | finding |
|---|---|---|
| HSR terminal / major city (KSA) | C-station-hsr-terminal-ksa-001 | Haramain package 2 construction contracts, Feb 2011 (S-cost-sys-013): Makkah SAR 3.18 bn, Jeddah 2.90 bn, Madinah 1.56 bn. Row: low/median/high = 1,560 / 2,900 / 3,180 SAR m (2011). Excludes design, land, systems and permanent way. Outturn unknown. |
| HSR intermediate (KSA) | -002 | King Abdullah Economic City (Rabigh): SAR 1.75 bn (S-cost-sys-013). A signature station, so it sits at the high end of the intermediate class. |
| HSR intermediate (UK) | -003 | HS2 Interchange: design and build "up to" GBP 370 m (2022, S-cost-sys-015). This is a ceiling, not an outturn. |
| Conventional halt / small station | -004 | Reston + East Linton (Scotland): AFC GBP 37.8–38.2 m for two stations (S-cost-sys-014), so GBP 18.9–19.1 m per station (equal split). |
| KSA desert halt | -005 | **unknown**. No SAR North or East line station contract value was found. |

FTA and the CHSRA Basis of Estimate (2018/2022/2024) would give US station unit costs. The hsr.ca.gov PDFs returned a bot-challenge HTML page (HTTP 200, 212 bytes) on every attempt, so they were not read. HS2 Curzon Street (GBP 570 m) and Old Oak Common appear only in search snippets and were not used.

## 2. Depots

- HS2 Washwood Heath depot plus the Network Integrated Control Centre: about GBP 856 m (May 2026, S-cost-sys-016). It includes a national control centre and a test track, so it is an upper bound. **Conflict:** search snippets say the tender estimate was GBP 275 m (unverified). This looks like a threefold rise, not a contradiction. Both are kept, the GBP 275 m only in this note.
- Stadler Rendsburg (55 two-car battery MUs): about EUR 30 m (2023, S-cost-sys-017). This is the low bound for a light depot.
- Haramain depots: **unknown**. DB Cottbus ICE works: about EUR 1 bn appears only in a cio.de snippet (unverified). The federal government and DB pages that were read give no figure.

## 3. Rolling stock

Per trainset as derived, with bundling flagged:

| train | value | bundled? | row |
|---|---|---|---|
| Siemens ICE 3neo, 8 cars, 439 seats, 320 km/h | EUR 600 m / 17 = 35.29 m (2023) | no (train only) | -001 |
| Alstom TGV M (Avelia Horizon), up to 740 passengers | EUR 25 m per set (2018), excluding a EUR 190 m budget for options and services | no | -002 |
| Talgo 350 SRO, Haramain first fleet | EUR 1,257 m / 35 = 35.91 m; / 36 = 34.92 m (2011) | unclear (see conflict) | -003 |
| Talgo, Haramain +20 trains (2 power cars + 13 cars, 417 seats) | EUR 1,332 m / 20 = 66.6 m (CNMV figure via The Corner); GRR prints EUR 1.3 bn, giving 65.0 m (2026) | **yes**: manufacture + maintenance | -004 |
| CR400AF, 8 cars | CNY 297 m / 2 = 148.5 m (2021); check: CNY 3.1 bn / 21 eight-car equivalents = 147.6 m (2018) | not stated | -005 |
| Siemens Velaro Egypt | **unknown**: EUR 8.1 bn Siemens share bundles trains, systems and maintenance | yes | -006 |
| Stadler SAR intercity diesel-electric (about 175 m, about 320 passengers) | CHF 300 m / 10 = 30 m (2026 option); CHF 600 m / 20 = 30 m or / 10 = 60 m (2024) | **yes**: 10-year maintenance | -007 |
| CAF SAR North-South push-pull, 200 km/h | USD 147.4 m / 5 = 29.48 m (2012) | not stated | -008 |
| Stadler FLIRT H2 (Caltrans) | USD 80 m / 4 = 20.0 m (2023); USD 127 m / 6 = 21.17 m (2024) | not stated | -009, -010 |
| Alstom Coradia iLint (RMV) | EUR 500 m / 27 = 18.52 m; Alstom share 360 / 27 = 13.33 m (2019) | **yes**: H2 supply + 25-year maintenance | -011 |
| Stadler FLIRT Akku battery (NAH.SH) | EUR 600 m / 55 = 10.91 m (2019) | **yes**: 30-year maintenance | -012 |
| GE ES30ACi locomotive (Egypt) | USD 575 m / 100 = 5.75 m (2017) | **yes**: 15-year parts and support | -015 |
| European locomotive (implied) | EUR 0.3 m on-board unit ≈ 15 % of the locomotive, so about EUR 2.0 m (2017) | n/a | -016 |
| SAR SD70ACS | **unknown** (no value in 2009 or 2026 coverage) | | -017 |
| Siemens Mireo Plus H | **unknown** (Romania release gives no value) | yes (15-year maintenance) | -018 |

The LNVG "14 iLint for EUR 81 m" in the task brief was not found in any source read. Alstom's AMF-filed release (S-cost-sys-028) gives no value. Electrive gives a project total of more than EUR 93 m, including the trains, station and operation, with no split (S-cost-sys-029). Not used as a per-train price.

## 4. Signalling and telecom

- EC/PwC 2018 tier 3 (S-cost-sys-004; EUR 2016 PPP; per double-track-equivalent km). ETCS L2 signalling: conventional 0.3 ± 47 %, HSR 0.5 ± 17 %. Telecom: conventional 0.3 ± 47 %, HSR 0.19 ± 16 % (Fig. 7 prints 0.2). The sample **excludes radio-block centres and station signalling equipment**.
- ECA SR 13/2017 (S-cost-sys-001..003) covers whole national trackside programmes: Denmark 1.18, Netherlands 1.69, average 1.44 M EUR per km of line. New on-board unit about EUR 300,000. Retrofit EUR 395,000–570,000 (average 482,500); audited cases up to EUR 970,000.
- Spanish BOE 2010 guideline as cited by EC: HSR signalling 1–1.25 M EUR/km (S-cost-sys-005).
- GSM-R: 50–130 kEUR/km (ERA RSDI cited by EU-Rail WG2, S-cost-sys-012).
- FRMCS: **unknown**. France's EUR 120,000/km (2021) was seen in a snippet only (S-cost-sys-039, unverified).
- ETCS Level 3 / hybrid: **unknown**.

## 5. Electrification and power supply

- EC tier 3, OCS excluding substations (S-cost-sys-004): conventional 0.6 ± 45 %, HSR 0.6 ± 17 % M EUR per double-track-equivalent km (EUR 2016).
- Spanish BOE 2010 HSR electrification: 1.1–1.35 M EUR/km (S-cost-sys-005).
- UK RIA benchmark (S-cost-sys-006): simple GBP 0.75–1 m and complex GBP 1–1.5 m per **single** track km (2019). GWEP: GBP 2.8 m/stk (S-cost-sys-007).
- India (S-cost-sys-008, -009): Rs 12,134.50 crore for 13,675 route km (2018), so INR 8.87 m per route km or 7.34 m per track km. Rs 21,000 crore for 18,808 route km (2021), so INR 11.17 m per route km. These are kept as two rows and not merged across price years.
- Traction substations (S-cost-sys-011): Eje Atlántico 2x25 kV, EUR 42.7 m for 3 traction substations + 9 autotransformer centres (2010), so EUR 14.23 m per traction substation package.
- Grid connection (S-cost-sys-010): HS2 Phase 2a grid supply point GBP 92.5 m / c. 100 m / 160 m (three options, 2019). The same report gives a feeding distance of almost 100 km between feeder stations. That is a spacing parameter, and the schema has no unit for it, so it is recorded in the row notes.
- Etihad Rail (diesel, not electrified) and Haramain electrification: no separable figure found.

## 6. Alternatives (diesel, hybrid, hydrogen, battery)

- Hydrogen and battery vehicle premiums over diesel: no open source isolates them. RMV/BMVI says the state pays 40 % of the "additional vehicle costs" versus diesel but gives no size, so the premiums are **assumed** (A-cost-250, A-cost-251).
- Hydrogen refuelling station: **unknown**. Bremervörde capacity of 1,600 kg/day is verified (S-cost-sys-030). The EUR 10 m cost and the EUR 8.4 m / EUR 4.3 m grants appear only in snippets.
- The FCH JU/S2R 2019 hydrogen rail study PDF was 67 MB, over the brief's 50 MB limit. It was deleted from /tmp right after a text grep, and none of its content was used. A grep of the extracted text found no per-train or per-station capex table. Its four case-study annex reports ("Report 2/3", separate PDFs on rail-research.europa.eu) may hold TCO inputs. They are listed as primaries to find.
- Electric versus diesel infrastructure: electrification is costed by the rows in section 5. Battery MUs still need OCS islands for charging.

## Conflicts (both kept, never averaged)

1. **ERTMS trackside:** EC tier 3 gives 0.3–0.5 M EUR/km (L2 works only, no RBC or station equipment, EUR 2016 PPP). ECA gives 1.18–1.69 M EUR/km (whole national programmes, price year not stated). The difference is scope, not error.
2. **HSR electrification:** EC gives 0.6 M EUR/km (excluding substations). BOE 2010 gives 1.1–1.35 M EUR/km (scope not stated, possibly including power supply; analysis).
3. **UK electrification:** the RIA benchmark of GBP 0.75–1.5 m/stk against the GWEP estimate of GBP 2.8 m/stk.
4. **Talgo Haramain first fleet:** EUR 1.257 bn for 35 trains (S-009) against EUR 1.6 bn for 35 trains plus 12 years of maintenance (S-cost-sys-040, snippet, unverified). If both are right, the 1.257 bn is the train-only part. Unconfirmed. Outlets also differ on fleet size, 35 or 36.
5. **Talgo 2026:** EUR 1.332 bn (CNMV figure via The Corner) against EUR 1.3 bn (GRR, rounded).
6. **Stadler SAR 2024:** it is unclear whether CHF 600 m includes the 10 option trains. The Railjournal snippet says yes. Swissinfo's 2026 CHF 300 m price for the 10 option trains is consistent with "yes".
7. **CAF SAR 2012:** USD 147.4 m (read) against SR 553 m (Railjournal snippet), SR 533 m (Railway Gazette snippet) and SR 53 m (MEED snippet, likely a typo).
8. **Haramain stations:** Makkah SAR 3.18 bn (Railway Gazette) against 3.2 bn or 3 bn (other outlets, snippets only); Madinah 1.56 bn against 1.6 bn.
9. **HS2 depot:** GBP 856 m awarded against the GBP 275 m tender estimate (snippet).

## Unknowns (where searched)

KSA desert halt station cost. Haramain depot cost. SAR SD70ACS price per unit. Siemens Velaro Egypt train-only price. Mireo Plus H price. Hydrogen refuelling station capex. FRMCS cost per km. ETCS Level 3 / hybrid cost per km. The `searched:` field of each unknown row lists the places searched.

## Proposed assumption rows (block A-cost-250 to A-cost-299; two used)

| id | parameter | value | unit | range | source or assumption | status | used in |
|---|---|---|---|---|---|---|---|
| A-cost-250 | Hydrogen fuel-cell MU capex premium over an equivalent diesel MU (vehicle only, excluding refuelling and H2 supply) | 30 | % | 15–60 | Assumption: no open source isolates the premium. RMV/BMVI (S-cost-sys-027) confirms a premium exists (the state pays 40 % of it) without sizing it. The wide range reflects that. | assumed | cities/ksa/costs/cost_register.yaml (C-rollingstock-h2-premium-013) |
| A-cost-251 | Battery-electric MU capex premium over an equivalent diesel MU (vehicle only, excluding charging OCS islands and battery replacement) | 25 | % | 10–50 | Assumption: no open source isolates the premium. NAH.SH and Stadler prices are bundled with 30-year maintenance. Battery performance at 50 °C ambient is an added uncertainty. | assumed | cities/ksa/costs/cost_register.yaml (C-rollingstock-battery-premium-014) |

## Primaries to find

- RIA *Electrification Cost Challenge* report (14 Mar 2019). The PDF is behind a bot challenge.
- CHSRA *Business Plan Capital Cost Basis of Estimate* (2018/2022/2024): station, maintenance-facility, trainset, OCS and traction power unit costs. Blocked by bot protection.
- Talgo CNMV filings: Feb 2026 (EUR 1.332 bn, 20 trains) and 2011 (Haramain phase II share and maintenance scope).
- Stadler media releases: SAR, Feb 2024 and Oct 2026 (does CHF 600 m include the option?).
- PIB release of 12 Sep 2018 (India electrification Cabinet decision). Rajya Sabha answer, Jul 2021.
- ERA Rail System Data Inventory (GSM-R 50–130 kEUR/km). The French COI report (FRMCS EUR 120,000/km).
- Boletín Oficial del Estado 2010 HSR cost guideline (cited by EC 2018).
- SRO/SAR award notices: Haramain station packages (2011), CAF (2012), PIF/EMD locomotives (2009), Progress Rail (2026).
- LNVG/Linde: Bremervörde hydrogen station capex and the LNVG contract value. Romania ARF award value (Mireo Plus H).
- FCH JU/S2R 2019 hydrogen rail study, case-study annex reports (Report 2, Report 3).
