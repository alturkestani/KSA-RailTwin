> **Document version:** docs/sources/cost-notes-ksa.md v1.0 | 31 Oct 2026 | Author: cost-estimator research subagent (R1c task 2, topic `ksa`) | Status: draft

# R1c task 2: KSA top-down cost data points: research notes

Outputs: `docs/sources/cost-ksa.csv` (S-cost-ksa-001 to -040), `cities/ksa/costs/cost_register.yaml` (49 rows: 17 sourced, 27 derived, 5 unknown; schema-validated). All figures are nominal, in the source currency, at the award or publication year. Nothing was converted except where a row's `derivation` applies the SAMA peg (S-lb-020, 3.75 SAR/USD, assumption A-cost-001). Quotes came through a page-extraction tool and must be byte-checked before they reach a report (`source-citation`). Text marked **analysis** is our reading, not a sourced fact. Arithmetic was run in Python on 31 Oct 2026.

Status convention: every press, trade-press and Wikipedia row is `secondary`, including pages read in full today. Snippet-only rows and HTTP 403 pages are `unverified`. No primary (SAR, MOT, RCRC, SPA, CNMV) document was read in this run.

## 1. Haramain HSR (layer `existing`)

| item | value | year | ids |
|---|---|---|---|
| (a) Phase 1 Package 1 civil works, Al Rajhi Alliance | SR 6.79 bn; RG gives the line as 444 km | award Feb/Mar 2009 | S-cost-ksa-001 (RG, 9 Feb 2009), S-cost-ksa-002 (Arab News, 5 Mar 2009 signing), S-007 |
| (b) Phase 1 Package 2 stations | Makkah 3.18, Madinah 1.56 (Saudi Bin Laden Group); Jeddah 2.90, KAEC 1.75 (Saudi Oger); sum SR 9.39 bn; KAIA station not contracted then | Feb 2011 | S-cost-ksa-003 |
| (c) Phase 2, Al Shoula (track, signalling and telecoms, electrification, OCC, 35 trains, 12-year O&M) | EUR 6.736 bn (Construction Index); EUR 6.74 bn = USD 9.4 bn (GCO); SR 30.8 bn = USD 8.2 bn at signing (Reuters byline) | Oct 2011 award, 14 Jan 2012 signing | S-cost-ksa-004, -005, -006, -007 |
| (d) programme total | SR 51.5 bn (two phases, Dec 2012 estimate); SR 63 bn incl. expropriation (SRO DG, Jun 2015); > SR 60 bn (Okaz, Sep 2018); SR 60 bn (Minister, Mar 2018; OBG 2019); ~SR 60 bn (Al-Madina 2019); outlier USD 7.87 bn (Railway Technology 2018) | 2012-2019 | S-lb-016, S-cost-ksa-008, -009, S-lb-021, S-lb-022, S-cost-ksa-010, -011 |
| (e) 2026 package | Talgo 20 trainsets, EUR 1.3 bn incl. maintenance of the whole 55-train fleet to 2033 (option 2038); Indra systems O&M about EUR 130 m for at least 5 years; EUR 2.8 bn across the consortium; Renfe operates to 2038; EUR 1,332 m (snippet only) | Feb 2026 | S-cost-ksa-012, -013, -014 |
| (f) ridership | early forecast "more than 3 million passengers annually" (Minister, Aug 2012; snippet, page 403); capacity 60 million/yr (acting PTA president, Sep 2018; project DG; Al-Madina 2019); outturn 6.97 million in 2023 (S-012); about 2,743 million pkm in 2025 (S-013) | | S-cost-ksa-016, -009, -015, -010, S-012, S-013 |

Per-km derived rows: Package 1 civil SR 14.99-15.29 m/km (444-453 km); all-in programme SR 132.45-140.25 m/km (SR 60 bn over 453 or 449.2 km; SR 63 bn incl. land over 449.2 km). This matches the "Haramain 35.3 USD m/km all-in" used in `docs/costs-landbridge.md` (132.45 / 3.75 = 35.3).

**Reconciliation of C-004 (cost part); evidence-based.** The "USD 9.4 bn total contract value" and the "Spanish source 6,736 million" on Wikipedia (S-010) are both the **Phase 2 Al Shoula contract**, not the programme total: GCO prints "€6.74-billion ($9.4 billion) contract for the second phase" (S-cost-ksa-005) and Construction Index prints "€6.736bn" for the same award (S-cost-ksa-004). The programme total is SR 60-63 bn. Components on record: 6.79 + 9.39 + 30.8 = SR 46.98 bn. The rest is the KAIA station, land (SR 63 bn includes expropriation), PM and variations (not itemised; analysis). Phase 2 bundles 12 years of O&M, so no published HHR figure is pure capex.

**Conflicts kept, not averaged:**
- Phase 2: SR 30.8 bn (USD 8.2 bn) vs EUR 6.736 bn (USD 9.4 bn at the outlet's rate). The USD figures differ through currency conversion at different dates (analysis). Kept as two rows (SAR, EUR); the normaliser converts.
- USD 7.87 bn (Railway Technology, 2018): below the Phase 2 contract alone. Kept as its own row and flagged "do not use".
- Line length: 444 km (RG 2009), 449.2 + 3.75 km, 450 km, 453 km. The per-km rows carry the spread.
- Ridership: the 2012 forecast (> 3 m/yr) and the 60 m/yr capacity are different quantities. The 2023 outturn is 6.97 m (S-012, secondary), about 2.3x the early forecast and about 12 % of capacity (analysis). No published demand forecast with a horizon year was found. Ridership stays out of the cost register (CSV and these notes only).
- Talgo original order: Wikipedia's "1.257 billion" has no currency and no corroboration (S-009). The row is `unknown`; the trains sit inside the Phase 2 lump.

## 2. SAR North (North-South railway; layer `existing`)

| item | value | ids |
|---|---|---|
| civil works, three contracts (3 Apr 2007) | SR 2.3 bn / 576 km (Ras Azzawr-Az Zabirah); SR 1.9 bn / 440 km (Az Zabirah-Great Nafud); SR 2.8 bn / 818 km (An-Nafoud-Al Haditha/Jalamid/Basayta); stated total 7.1 bn and 1,765 km, but the parts sum to 7.0 bn and 1,834 km | S-cost-ksa-017 |
| stations, depot, maintenance buildings (Jan 2012) | 5 stations SR 1.57 bn; Na'ariyah depot SR 496 m; 15 track-maintenance facilities and 19 buildings SR 272 m; total SR 2.34 bn | S-cost-ksa-018 |
| CAF passenger trainsets (Mar 2012) | 5 diesel push-pull sets, supply and maintain, SR 533 m (RG) vs SR 553 m = USD 147.5 m (IRJ snippet); with 4 more sets for SRO, EUR 200 m together | S-cost-ksa-019, -020 |
| locomotives and wagons (Apr 2009) | 25 EMD SD70ACS (no value); 668 China South wagons, almost USD 100 m | S-cost-ksa-021 |
| 33 EMD locomotives (Sep 2026) | value not disclosed | S-cost-ksa-026 (snippet) |
| totals | USD 3.5 bn for 2,400 km (2010, S-lb-024); USD 5.33 bn excl. expropriation (Mar 2012, S-lb-023) = SR 19.99 bn at the peg, the same figure as SR 20 bn (Dec 2012, S-lb-016; Wikipedia S-023); USD 2.6 bn "built at" for 2,750 km (GCO, 1 Oct 2017) = SR 9.75 bn at the peg, the same figure as Saudipedia's SR 10 bn (undated) | S-cost-ksa-022, -023 |
| phosphate line doubling (2026) | section 1, about 100 km (AZ1/Nariyah to Ras Al-Khair), "estimated SR4bn-plus ($1.1bn)", awarded to Alomaier, 20 Aug 2026; section 2 (> 150 km) award being prepared, no value; MEED says this is the first of four packages | S-cost-ksa-024, -025 |

Per km: 2012 basis SR 7.27 m/km and 2017 basis SR 3.55-3.64 m/km (over 2,750 km, S-021). The 2007 civil contracts give SR 3.42-4.32 m/km by section, central 3.82. The phosphate doubling gives SR 40.0-41.25 m/km.

**C-007 update (open; narrowed).** The four published totals collapse to **two figures**: SR ~20 bn (2012 estimate, excl. land; SR 20 bn and USD 5.33 bn are the same number at the peg) and SR ~10 bn (2017 "built at"; USD 2.6 bn and SR 10 bn are the same number). USD 3.5 bn (2010) belongs to an earlier 2,400 km scope. **Analysis:** package values already on record (civil 7.0-7.1 + stations/depots 2.34 + CAF 0.53 + wagons ~0.37 at the peg) total about SR 10.3 bn before locomotives, track materials, signalling and land, so SR 10 bn is probably a narrower scope (civil works?) or an under-statement. The SR 20 bn estimate is more consistent with the package sum plus the unknown items. Both stay as rows.

**Other flags:**
- The phosphate-doubling contractor differs between reports: Alomaier (MEED, 20 Aug 2026, read) vs Al-Nasr (a Feb 2026 MEED item seen only as a snippet). The register uses the August report.
- **Analysis:** the 2026 doubling rate (SR ~40 m/km) is about 25x the 2014 Hofuf-Haradh doubling (SR 1.62 m/km). The scopes differ (hydrological structures, yard conversion near the coast) and the price bases are 12 years apart. Treat it as a scope-specific point, not a generic doubling rate.
- **Analysis:** the 440 km Nafud section has the highest civil rate (SR 4.32 m/km vs 3.42-3.99 elsewhere). This is weak evidence for a dunes premium, not a sourced premium.

## 3. SAR East (Riyadh-Dammam; layer `existing`, new works `committed`)

| item | value | ids |
|---|---|---|
| Hofuf bypass for 200 km/h (Apr 2011) | SR 659 m, length not stated | S-cost-ksa-030 |
| renewal of 78.4 km of freight line (CRCC, Aug 2014) | SR 123 m, 1.57 m/km | S-cost-ksa-031 |
| doubling of 241 km Hofuf-Haradh (Al Mobty, Aug 2014) | SR 391 m, 1.62 m/km | S-cost-ksa-031 |
| Talgo six 200 km/h diesel trainsets (Mar 2015) | > USD 200 m, 33.3 m per set (a floor) | S-cost-ksa-029 |
| Stadler 10 inter-city trainsets (Feb 2024) | SFr 600 m incl. 10-year maintenance and spares (60 m per set) | S-cost-ksa-027 |
| Stadler option, 10 more sets (Oct 2026) | CHF 300 m (30 m per set); existing maintenance extended | S-cost-ksa-028 |
| Dammam Second Industrial City link and yard | SR 500 m at selection (Jan 2026); award of 22.7 km single track (Jun 2026), no value | S-cost-ksa-032, -033 |
| Jubail-Dammam 115 km freight line (Terna, Sep 2013) | SAR 827 m (USD 220 m), 7.19 m/km | S-cost-ksa-034 |

No whole-line total for the East line was found. A search snippet gave "SR16.02 billion" for a CRCC phase-two freight contract over 91 km. It looks like a transcription error (16.02 bn over 91 km would be SR 176 m/km), was not read, and is not registered.

## 4. Riyadh Metro (reference only: urban metro, not a line type of this study)

- 2013 packages (DG Trésor, 28 Nov 2024, S-cost-ksa-035): BACS (Bechtel), lines 1-2, USD 9.45 bn; ANM (Ansaldo STS), line 3, USD 5.21 bn; FAST (FCC), lines 4-6, USD 7.82 bn. Sum USD 22.48 bn. Network: 176 km (60 km underground), 6 lines, 85 stations; awarded 28 Jul 2013. Package values verified against the three-way split; all three match the brief.
- Outturn: USD 25 bn and USD 166 m/km, attributed to the RCRC CEO (Argaam, Dec 2024, S-038). The ENR article "Global Consortia Complete Riyadh's New $25B Metro" exists (S-cost-ksa-036; HTTP 403, snippet only: "built the $25-billion electrified system").
- Land: SR 3 bn (USD 800 m) compensation budgeted for 35 locations (ADA president to Reuters, about Aug 2013, S-cost-ksa-037).

**C-005 (cost part) resolved as different vintages (evidence plus arithmetic):** USD 22.5 bn (S-039) = the sum of the three July 2013 awards (9.45 + 5.21 + 7.82 = 22.48). Al-Muraba's "84.4 bn riyals for the 2013 contracts" (snippet) = 22.48 × 3.75 = SR 84.3 bn. USD 25 bn is the 2024 outturn statement, +11 % nominal. Still open: USD 166 m/km implies 150.6 km, not 176 km. The length basis is unexplained.

## 5. Landbridge (layer `committed`)

The four rows from `docs/costs-landbridge.md` §4 were written as directed: the SR 100 bn programme row (low = central = high = 100,000, price year 2022 assumed, A-cost-100, status derived; the RCF uplift supplies the upside); two per-km rows, each a single point on one denominator (45.91 over 2,178 km; 66.67 over 1,500 km, an upper bound); the legacy SR 26-26.6 bn row (history only); and the Riyadh Rail Link `unknown` row. **New facts since 30 Oct 2026:** none. A search on 31 Oct 2026 found no Riyadh Rail Link award notice or value. The latest is MEED of 31 Aug 2026, "contract award nears" (S-047). A GDN Online item mentions an award without a value or date and was not used.

## 6. Other KSA data points

- **GCC railway, Saudi section (~672 km):** `unknown`. The only figure is "more than US$15bn" for the whole 2,186 km network (Construction Review, 12 May 2026, S-cost-ksa-038). Older snippets give USD 25 / 30 / 200 / 250 bn network figures; these were not read and their scope is unclear. No source apportions any of them to Saudi Arabia.
- **Riyadh Rail Link:** `unknown` (see §5).
- **Jeddah metro (planned):** USD 9.3 bn for 108 km, 3 lines, 46 stations (deputy mayor to Reuters; page undated, "14 years ago", so about 2012). Registered as reference only, layer `n/a` (announced/planned, never committed), price year 2012 assumed (A-cost-101).
- **Qiddiya high-speed rail (84 km):** in procurement. No project value was published (MEED snippets, S-cost-ksa-040). A "USD 404 m second phase" snippet is not clearly tied to this line, so it is not registered.
- **Makkah metro, Al-Ula tram, NEOM rail:** not searched individually within the lookup budget. No valued figure was seen incidentally. No rows (the brief limits unknown rows to the GCC section and the Riyadh Rail Link).

## Conflicts summary (for `docs/sources/conflicts.md`; coordinator to merge)

| conflict | figures | status |
|---|---|---|
| C-004 cost | USD 9.4 bn / EUR 6,736 m = Phase 2 contract; SR 60-63 bn = programme | **resolved with evidence** (S-cost-ksa-004, -005) |
| HHR Phase 2 currency | SR 30.8 bn (USD 8.2 bn) vs EUR 6.736 bn (USD 9.4 bn) | open: exchange-rate dates; two rows |
| HHR outlier | USD 7.87 bn (2018) | unexplained; flagged "do not use" |
| HHR length | 444 / 449.2 / 450 / 453 km | carried as a per-km spread |
| C-005 cost | USD 22.5 bn = 2013 award sum; USD 25 bn = 2024 outturn; 166 m/km implies 150.6 km | **resolved as vintages**; length basis of 166 m/km open |
| C-007 cost | SR 20 bn = USD 5.33 bn (2012, excl. land) vs SR 10 bn = USD 2.6 bn (2017); USD 3.5 bn (2010, 2,400 km) | narrowed to two figures; open |
| North-South 2007 civils | stated 7.1 bn / 1,765 km vs parts 7.0 bn / 1,834 km | internal inconsistency in the source; low = 7.0, central = 7.1 |
| CAF North trainsets | SR 533 m (RG) vs SR 553 m (IRJ snippet); EUR 200 m for 9 sets inconsistent with SR 533 m for 5 | open |
| Talgo 2026 | EUR 1.3 bn (RG, GRR) vs EUR 1,332 m (snippet) | rounding; range carried |
| phosphate contractor | Alomaier (Aug 2026) vs Al-Nasr (Feb 2026 snippet) | open (value unaffected) |

## Proposed assumption rows (block A-cost-100 to A-cost-149; used: 100, 101)

| id | parameter | value | unit | range | source or assumption | status | used in |
|---|---|---|---|---|---|---|---|
| A-cost-100 | Price year of the Landbridge SR 100 bn statement | 2022 | year (nominal SAR) | 2022-2026 (first stated Mar 2022; repeated Jan 2026 without re-basing) | assumption: no source states a price year; earliest official statement S-lb-002 (22 Mar 2022) taken as the base; reason: docs/costs-landbridge.md §4 "treat as 2022 nominal until re-based or confirmed" | assumed | cities/ksa/costs/cost_register.yaml: C-programme-landbridge-001, -per-km-2178-001, -per-km-1500-001 |
| A-cost-101 | Price year of the Jeddah metro USD 9.3 bn estimate | 2012 | year (nominal USD) | 2011-2013 | assumption: page undated ("14 years ago" on 31 Oct 2026); reason: no dated copy found | assumed | C-programme-jeddah-metro-planned-001 |

## Primaries to find (Tariq to request; this run contacted no one)

1. SRO/SAR award notices or SPA releases for HHR Package 1 (Mar 2009), Package 2 stations (Feb 2011) and Phase 2 (Oct 2011 / 14 Jan 2012), with the SAR value and scope of Phase 2 (capex vs 12-year O&M split).
2. Spanish Ministerio de Fomento / Adif release (Oct 2011) for EUR 6,736 m; Talgo annual report 2011-2012 (original train order value); Talgo and Indra CNMV notices (Feb 2026).
3. An official HHR outturn statement (SAR annual report or MOT) with what SR 60 bn includes (land, KAIA station, the post-2019 Jeddah station repair).
4. An HHR demand forecast with a horizon year (SRO feasibility study), to set against the 6.97 m outturn (2023) for the reference class.
5. SAR annual report or PIF disclosure reconciling the North-South SR 10 bn vs SR 20 bn; the EMD locomotive order values (2009, 2026).
6. RCRC statement of the Riyadh Metro outturn (USD 25 bn) with its length basis (166 m/km) and whether land is included; ENR full text (S-cost-ksa-036).
7. SAR award notices: Riyadh Rail Link; phosphate doubling sections 1-2 (contractor, value); Dammam Second Industrial City (award value).
8. GCC Railway Authority / SAR: Saudi-section estimate.
