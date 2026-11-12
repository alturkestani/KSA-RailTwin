> **Document version:** docs/sources/cost-notes-rcf.md v1.0 | 31 Oct 2026 | Author: cost-estimator (rcf subagent) | Status: draft

# R1c task 5: reference-class uplifts (topic `rcf`)

Outputs: `docs/sources/cost-rcf.csv` (S-cost-rcf-001 to -043), `cities/ksa/costs/uplifts.yaml` (30 entries, validated with `common.schemas.load_uplifts`; every empirical curve passes `costs.rcf.empirical_ppf`). Ratios = outcome / base estimate (capex, schedule) or actual / forecast (ridership). All figures below were read this session; "derived" means our arithmetic on read figures.

## 1. HM Treasury Green Book supplementary guidance (Mott MacDonald 2002)
- Table 1 (S-cost-rcf-001), upper / lower bounds, %: Standard civil engineering: works duration 20 / 1, capex 44 / 3. **Non-standard civil engineering: works duration 25 / 3, capex 66 / 6.** Standard buildings 4 / 1, 24 / 2; non-standard buildings 39 / 2, 51 / 4; equipment/development 54 / 10, 200 / 10; outsourcing (opex) 41 / 0.
- Rail category (S-cost-rcf-002, para 3.10): rail is named only under **non-standard civil engineering** ("e.g. innovative rail, road, utility projects, or upgrade and extension projects"); standard civil engineering lists "most new roads and some utility projects". The guidance does not place a non-innovative new rail line explicitly; para 3.6 calls a project non-standard if innovative, mostly unique, or of high complexity. Our classification of KSA lines as non-standard is an assumption (A-rcf-017).
- Method (S-cost-rcf-003): upper bound = average historic optimism bias at **outline business case**; start there and reduce only with evidenced mitigation; lower bound = target by contract award. No opex or benefit bounds (para 4.1). The Green Book 2026 (S-cost-rcf-004, para 6.80) still points to these generic values when a body has no own evidence, and names DfT's own guidance.
- Encoded as point uplifts (degenerate triangular): U-capex-nonstdcivil-obc 1.66, U-capex-nonstdcivil-award 1.06, U-schedule-nonstdcivil-obc 1.25, U-schedule-nonstdcivil-award 1.03. These are a method, not a distribution: sensitivity only.

## 2. DfT TAG A1.2 (May 2025) and A5.3 (Nov 2025)
- TAG A1.2 Table 7 (S-cost-rcf-005): Rail (metro, light rail, guided buses on tracks, line upgrades, high-speed rail) **56 % / 33 % / 30 %** at Stage 1 / 2 / 3 = SOBC / OBC / FBC (Table 6: railways = PACE 1 / 3 / 5). Rolling stock 61 / 38 / 35; stations and terminal buildings 70 / 48 / 44; fixed links 55 / 32 / 28; roads 46 / 23 / 20. Source: OGP (2020). The text calls the table "Table 8" in places (numbering slip in the source).
- TAG A5.3 Table 3 (S-cost-rcf-007) repeats 56 / 33 / 30 (new build rail), adds **rail opex OB 41 / 41 / 21 / 21 / 1 %** by PACE level 1-5, and footnote 7: a 120 % uplift at PACE 1 as a starting point for complex enhancement schemes that fail the Bowe recommendations.
- No opex uplift in A1.2 (S-cost-rcf-006); demand/benefit optimism via sensitivity tests.
- **Finding:** the TAG percentages are the **adjusted means** of the OGP curves, not P50 or P80: the DfT workbook's "Average" row for rail is 0.2968 / 0.3321 / 0.5607 (FBC / OBC / SOC) = 30 / 33 / 56 % (S-cost-rcf-008). The rail P50 is 19 % at every stage; P80 is 60 / 77 / 121 %.

## 3. Flyvbjerg reference-class papers
- FHB 2002 JAPA (S-cost-rcf-022): rail cost escalation **mean 44.7 %, sd 38.4, n = 58** (constant prices; all 258 projects 27.6 %, sd 38.7). By region (S-cost-rcf-023): Europe 34.2 (sd 25.1, n 23), North America 40.8 (36.8, 19), other 64.6 (49.5, 16). Quartiles 24 / 43 / 60 % (Flyvbjerg 2007, S-cost-rcf-025); urban rail 33 / 44 / 60 (n 44); other rail (HSR + ordinary) 10 / 34 / 75 (n 14). HSR "tops the list" but the subdivision is not significant (2002 text).
- FHB 2005 JAPA (S-cost-rcf-024; arXiv copy is Draft 9.0, hence `secondary`): rail ridership **actual 51.4 % below forecast on average (sd 28.1, n = 25 excluding two outliers)**; **-39.5 % (sd 52.4, n = 27) including them**; 84 % of rail projects more than 20 % below forecast. Quartiles -70 / -54 / -25 (n 27; S-cost-rcf-026).
- Flyvbjerg 2006 PMJ (S-cost-rcf-027): rail uplift **40 % at the 50th percentile, 57 % at the 80th**, 68 % at a 10 % acceptable risk (90th).
- Flyvbjerg and COWI 2004 DfT guidance (S-cost-rcf-029): the full percentile table (50/60/70/80/90) was **not read** (SSRN 403; no file on vbn.aau.dk). What is verified: P50 40, P80 57, P90 68 (S-cost-rcf-027) and P95 80, n = 46 rail projects (Edinburgh Tram Inquiry report, S-cost-rcf-028). The 60th and 70th percentiles stay **unknown**; they are not filled in U-capex-rail2004-fbc.
- OGP 2020 for DfT (S-cost-rcf-015 to -021; workbook S-cost-rcf-008 to -014) supersedes 2004: rail cost n = 355, schedule n = 133, benefits n = 132, opex n = 49; HSR cost n = 23, schedule n = 11; rolling stock n = 20; buildings n = 149. Real terms, base cost excluding contingency, measured from each stage's approval.

## 4. Schedule
- OGP rail schedule (S-cost-rcf-009/-017): mean 28 / 33 / 31 % (FBC / OBC / SOBC); RCF50 20 %; RCF80 61 / 78 / 73 %; base = duration from stage approval to opening. HSR schedule n = 11: P50 37 %, P80 120 / 137 / 132 %.
- Green Book works duration, non-standard civil engineering: 25 % upper, 3 % lower (S-cost-rcf-001).
- FHB 2004 Transport Reviews (S-cost-rcf-030): no delay distribution; rail implementation phase averages 6.3 years (sd 3.3), and cost escalation rises 4.64 percentage points per year of implementation phase (all project types).
- ECA 19/2018 (S-cost-rcf-034): 8 of 30 audited HSR projects delayed at least one year; 5 of 10 lines delayed more than a decade; Milan-Venice 18 years. No duration base, so not convertible to a ratio.
- Light rail extensions (OGP Edinburgh, S-cost-rcf-031, n = 89): schedule P50 3 %, P80 35 %, P90 65 %, P95 82 % (check class only).
- Not searched this session (budget): Cantarelli et al. schedule papers, Love and Ahiaga-Dagbui.

## 5. Later and other reference classes
- ECA 19/2018 (S-cost-rcf-032/-033), **nominal** terms: aggregate overrun 44 % at project level, 78 % at line level; seven lines with estimates: 76.1, 622.1, 26.1, 28.1, 38.5, 26.3, 33.3 % (median 33.3 %, derived). Not an uplift entry: nominal, line-level, mixed scope.
- Flyvbjerg and Gardner 2023 appendix (S-cost-rcf-035): **unknown**; the appendix was not accessible; a blog figure seen in search results was not used.
- Cantarelli et al. 2012 (S-cost-rcf-043): literature table only (US rail 54 %, 61 %, 30 %; Korea 48 %); no HSR-specific Cantarelli class found in arXiv title search.
- NIC (2020) rail reference classes, cited by TAG A1.2 para 3.5.11 as disaggregated rail RCFs: not opened (search found the nic.org.uk page; a slide deck is described as proprietary). Primary to find.

## Uplift entries proposed (headline ratios)
| id | n | P50 | P80 | note |
|---|---|---|---|---|
| U-capex-rail-sobc / -obc / -fbc | 355 | 1.19 | 2.2115 / 1.766 / 1.60 | default class (A-rcf-031) |
| U-capex-hsr-sobc / -obc / -fbc | 23 | 1.29 | 2.3535 / 1.908 / 1.742 | sensitivity |
| U-capex-rollingstock-* | 20 | 1.2993 | 2.2528 / 1.8073 / 1.6413 | combined-project split only |
| U-capex-buildings-* | 149 | 1.1333 | 2.451 / 2.0055 / 1.8395 | stations, split only |
| U-capex-rail2004-fbc | 46 | 1.40 | 1.57 | 2004 guidance; P60/P70 unknown |
| U-capex-railfhb-fbc / urbanrail / otherrail | 58 / 44 / 14 | 1.43 / 1.44 / 1.34 | quartiles only | FHB 2002 sample |
| U-capex-nonstdcivil-obc / -award | n/a | 1.66 / 1.06 point | | Green Book |
| U-capex-lrtext-fbc | 89 | 1.17 | 1.57 | urban extensions, check only |
| U-schedule-rail-sobc / -obc / -fbc | 133 | 1.20 | 1.73 / 1.78 / 1.61 | default |
| U-schedule-hsr-* | 11 | 1.37 | 2.32 / 2.37 / 2.20 | sensitivity |
| U-schedule-nonstdcivil-obc / -award | n/a | 1.25 / 1.03 point | | Green Book |
| U-schedule-lrtext-fbc | 89 | 1.03 | 1.35 | check only |
| U-ridership-rail-fbc | 132 | 0.70 | 0.3562 is reached by 80 % (q20) | derived relabel |
| U-ridership-railfhb-fbc | 27 | 0.46 | quartiles 0.30 / 0.75 | severe sensitivity |

## Conflicts (both kept, never averaged)
1. **Which statistic is "the uplift".** TAG 56 / 33 / 30 % are means; the OGP P50 is 19 % and P80 is 121 / 77 / 60 % for the same curves; Flyvbjerg 2004/2006 gives P50 40 % and P80 57 % from a different (older, n = 46) sample; the Green Book gives 66 % (non-standard civil, OBC upper bound = historic average). The P50/P80 budgets in `docs/reference-class.md` must name which curve they use.
2. **Stage baseline.** Flyvbjerg 2002/2004 measure from the decision to build (FBC); TAG then applied those uplifts at OBC (S-cost-rcf-028). OGP 2020 measures from each stage. U-capex-rail2004-fbc is labelled FBC for that reason.
3. **OGP 2020 Table 8 opex labels** (S-cost-rcf-019) print Rail mean 70 %, RCF80 185 %; Table 2 and the workbook give rail mean 1 % (RCF50 -10 %, RCF80 40 %) and roads 70 %. TAG A5.3 uses 1 % at FBC, consistent with Table 2. Table 8 appears mislabelled; flagged, not resolved by us.
4. **Ridership shortfall.** OGP rail benefits (n = 132, 1970-2011) mean -25 %, median -30 %; FHB 2005 (n = 27, 1969-1998) mean -39.5 % (incl. outliers) or -51.4 % (excl.); OGP UK rail (n = 14) mean -10 %. Different samples and eras.
5. **Schedule stage ordering.** OGP rail schedule P80 at SOBC (73 %) is below OBC (78 %) in both Table 6 and the workbook; kept as printed.
6. **Rail mean in the FHB sample.** Cantarelli et al. 2012 Table 1 prints 41 % (n 58) for Flyvbjerg et al. 2003a in the rail column; FHB 2002 gives 44.7 % for the same n. Possibly a different publication basis; not resolved.
7. **HSR vs pooled rail.** TAG A1.2 para 3.5.5 says risk within each category can be treated as statistically similar (OGP 2020), so HSR sits in "Rail"; the HSR-only curves (n = 23) are higher (P50 1.29 vs 1.19). Keep HSR as sensitivity.
8. **Nominal vs real.** ECA figures are nominal; OGP and Flyvbjerg are real. Not comparable without deflation.

## KSA check (cited data only; derived ratios are ours)
- **Haramain HSR schedule.** Civil works awarded Feb 2009, "expected to run for three years" from March 2009 (S-cost-rcf-036). "Opening had been envisaged for 2014 when the railway systems contract was signed in January 2012"; completion later moved from January 2017 to Q1 2018 (S-cost-rcf-037, S-cost-rcf-039). Public opening 11 Oct 2018 (S-al_baha-008, secondary). Derived: from the Jan 2012 systems contract, planned 1.9-3.0 years (opening any time in 2014) vs actual 6.7-6.8 years: **ratio 2.23-3.53**. The often-cited original "2012" opening is unverified (S-cost-rcf-042).
- **Haramain cost.** SR 51.5 bn "two phases" (Arab News, Dec 2012, S-lb-016) vs SR 60 bn (Minister, Mar 2018, S-lb-021): derived nominal ratio **1.165**; Al Jazeera 2018 "more than $16bn" (S-cost-rcf-041). The 2012 figure was stated after both main contracts were awarded, so it is not a decision-to-build base; the scope of both totals is unclear. Contract-level: SRO agreed an extra EUR 150 m towards systems-contract overruns on a EUR 6.7 bn contract (S-cost-rcf-038), about 2 % (derived), not a project overrun.
- **Riyadh Metro schedule.** Main contracts awarded 28 July 2013; "Due to be operational in 2019" (S-cost-rcf-040). Opened 1 Dec 2024 (lines 1, 4, 6; S-037), 15 Dec 2024 (S-035), 5 Jan 2025 (S-036). Derived: planned 5.4-6.4 years vs actual 11.3-11.4 years: **ratio 1.77-2.11**.
- **Riyadh Metro cost.** Contract packages USD 7.82 + 9.45 + 5.21 = 22.48 bn (2013, S-cost-rcf-040) vs USD 25 bn total project (RCRC CEO via Argaam, S-038) and USD 22.5 bn (S-039): derived nominal ratio **1.11**, but contract value vs whole-project scope, so not an overrun measure.
- **Fit to the global class.** Schedule: OGP rail FBC P50 1.20, P80 1.61, P90 2.112, P95 2.38. Riyadh Metro (1.77-2.11) sits around P80-P90; Haramain (2.23-3.53) sits at or beyond P90-P95. Both KSA projects are in the upper tail: the global class may understate KSA schedule risk. Cost: the KSA nominal ratios (1.11-1.17) are at or below the global rail P50 (1.19), but neither is measured against a decision-to-build base estimate in real terms, so they cannot confirm or reject the global cost class. Keep the global class for capex; run the schedule at P80 and P90 as the KSA sensitivity (A-rcf-039). Two projects are anecdotes, not a reference class.

## Unknowns and where searched
- Flyvbjerg and COWI 2004 full rail percentile table (P60, P70): SSRN abstract 2278346 (download 403), vbn.aau.dk record (no file), two web searches, arXiv title search.
- Mott MacDonald (2002) report itself: gov.uk search API (no result); the Green Book guidance is the verified carrier of Table 1.
- Flyvbjerg and Gardner 2023 Appendix A rail base rate: web search (catalogue record only).
- NIC 2020 rail RCF dataset: web search (page found, not opened).
- ATAP O2 optimism bias (Australia): fetch timed out.
- Haramain decision-to-build budget and Riyadh Metro budget at award (real terms): not found; MEED project pages behind paywall beyond the lead.

## Proposed assumption rows (A-rcf-001 to A-rcf-040; A-rcf-041 to -049 unused)
| id | parameter | value | unit | range | source or assumption | status | used in |
|---|---|---|---|---|---|---|---|
| A-rcf-001 | Reference class and stage for `U-capex-rail-sobc` (capex, rail, SOBC) | P50 1.19 / P80 2.2115 | ratio | P5 0.7085 to P95 4.1915 | S-cost-rcf-008, S-cost-rcf-016, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-002 | Reference class and stage for `U-capex-rail-obc` (capex, rail, OBC) | P50 1.19 / P80 1.766 | ratio | P5 0.7085 to P95 2.6188 | S-cost-rcf-008, S-cost-rcf-016, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-003 | Reference class and stage for `U-capex-rail-fbc` (capex, rail, FBC) | P50 1.19 / P80 1.6 | ratio | P5 0.8067 to P95 2.4269 | S-cost-rcf-008, S-cost-rcf-016, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-004 | Reference class and stage for `U-capex-hsr-sobc` (capex, hsr, SOBC) | P50 1.29 / P80 2.3535 | ratio | P5 0.9028 to P95 4.0486 | S-cost-rcf-010, S-cost-rcf-008 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-005 | Reference class and stage for `U-capex-hsr-obc` (capex, hsr, OBC) | P50 1.29 / P80 1.908 | ratio | P5 0.9028 to P95 2.4758 | S-cost-rcf-010, S-cost-rcf-008 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-006 | Reference class and stage for `U-capex-hsr-fbc` (capex, hsr, FBC) | P50 1.29 / P80 1.742 | ratio | P5 1.001 to P95 2.284 | S-cost-rcf-010, S-cost-rcf-008 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-007 | Reference class and stage for `U-capex-rollingstock-sobc` (capex, all, SOBC) | P50 1.2993 / P80 2.2528 | ratio | P5 0.5566 to P95 4.2859 | S-cost-rcf-011, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-008 | Reference class and stage for `U-capex-rollingstock-obc` (capex, all, OBC) | P50 1.2993 / P80 1.8073 | ratio | P5 0.5566 to P95 2.7132 | S-cost-rcf-011, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-009 | Reference class and stage for `U-capex-rollingstock-fbc` (capex, all, FBC) | P50 1.2993 / P80 1.6413 | ratio | P5 0.6549 to P95 2.5213 | S-cost-rcf-011, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-010 | Reference class and stage for `U-capex-buildings-sobc` (capex, all, SOBC) | P50 1.1333 / P80 2.451 | ratio | P5 0.7235 to P95 5.4763 | S-cost-rcf-012, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-011 | Reference class and stage for `U-capex-buildings-obc` (capex, all, OBC) | P50 1.1333 / P80 2.0055 | ratio | P5 0.7235 to P95 3.9036 | S-cost-rcf-012, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-012 | Reference class and stage for `U-capex-buildings-fbc` (capex, all, FBC) | P50 1.1333 / P80 1.8395 | ratio | P5 0.8217 to P95 3.7118 | S-cost-rcf-012, S-cost-rcf-005, S-cost-rcf-007 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-013 | Reference class and stage for `U-capex-rail2004-fbc` (capex, rail, FBC) | P50 1.4 / P80 1.57 | ratio | P50 1.4 to P95 1.8 | S-cost-rcf-027, S-cost-rcf-028, S-cost-rcf-029 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-014 | Reference class and stage for `U-capex-railfhb-fbc` (capex, rail, FBC) | P25 1.24 / P50 1.43 / P75 1.60 | ratio | P25 1.24 to P75 1.6 | S-cost-rcf-025, S-cost-rcf-022, S-cost-rcf-023 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-015 | Reference class and stage for `U-capex-urbanrail-fbc` (capex, rail, FBC) | P25 1.33 / P50 1.44 / P75 1.60 | ratio | P25 1.33 to P75 1.6 | S-cost-rcf-025 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-016 | Reference class and stage for `U-capex-otherrail-fbc` (capex, rail, FBC) | P25 1.10 / P50 1.34 / P75 1.75 | ratio | P25 1.1 to P75 1.75 | S-cost-rcf-025 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-017 | Reference class and stage for `U-capex-nonstdcivil-obc` (capex, rail, OBC) | 1.66 (point) | ratio | point uplift by method (no distribution in source) | S-cost-rcf-001, S-cost-rcf-002, S-cost-rcf-003, S-cost-rcf-004 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-018 | Reference class and stage for `U-capex-nonstdcivil-award` (capex, rail, FBC) | 1.06 (point) | ratio | point uplift by method (no distribution in source) | S-cost-rcf-001, S-cost-rcf-003 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-019 | Reference class and stage for `U-capex-lrtext-fbc` (capex, commuter, FBC) | P50 1.17 / P80 1.57 | ratio | P50 1.17 to P95 2.04 | S-cost-rcf-031 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-020 | Reference class and stage for `U-schedule-rail-sobc` (schedule, rail, SOBC) | P50 1.2 / P80 1.73 | ratio | P5 0.6279 to P95 2.53 | S-cost-rcf-009, S-cost-rcf-017, S-cost-rcf-021 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-021 | Reference class and stage for `U-schedule-rail-obc` (schedule, rail, OBC) | P50 1.2 / P80 1.78 | ratio | P5 0.6779 to P95 2.68 | S-cost-rcf-009, S-cost-rcf-017, S-cost-rcf-021 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-022 | Reference class and stage for `U-schedule-rail-fbc` (schedule, rail, FBC) | P50 1.2 / P80 1.61 | ratio | P5 0.6979 to P95 2.38 | S-cost-rcf-009, S-cost-rcf-017, S-cost-rcf-021 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-023 | Reference class and stage for `U-schedule-hsr-sobc` (schedule, hsr, SOBC) | P50 1.37 / P80 2.32 | ratio | P5 0.975 to P95 2.54 | S-cost-rcf-010, S-cost-rcf-009 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-024 | Reference class and stage for `U-schedule-hsr-obc` (schedule, hsr, OBC) | P50 1.37 / P80 2.37 | ratio | P5 1.025 to P95 2.69 | S-cost-rcf-010, S-cost-rcf-009 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-025 | Reference class and stage for `U-schedule-hsr-fbc` (schedule, hsr, FBC) | P50 1.37 / P80 2.2 | ratio | P5 1.045 to P95 2.39 | S-cost-rcf-010, S-cost-rcf-009 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-026 | Reference class and stage for `U-schedule-nonstdcivil-obc` (schedule, rail, OBC) | 1.25 (point) | ratio | point uplift by method (no distribution in source) | S-cost-rcf-001, S-cost-rcf-003 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-027 | Reference class and stage for `U-schedule-nonstdcivil-award` (schedule, rail, FBC) | 1.03 (point) | ratio | point uplift by method (no distribution in source) | S-cost-rcf-001 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-028 | Reference class and stage for `U-schedule-lrtext-fbc` (schedule, commuter, FBC) | P50 1.03 / P80 1.35 | ratio | P50 1.03 to P95 1.82 | S-cost-rcf-031 | proposed (sourced) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-029 | Reference class and stage for `U-ridership-rail-fbc` (ridership, rail, FBC) | P50 0.70 / P20 0.3562 (ratio reached by 80 % of projects) | ratio | P5 0.1865 to P95 1.6256 | S-cost-rcf-013, S-cost-rcf-018, S-cost-rcf-015 | proposed (derived) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-030 | Reference class and stage for `U-ridership-railfhb-fbc` (ridership, rail, FBC) | P25 0.30 / P50 0.46 / P75 0.75 | ratio | P25 0.3 to P75 0.75 | S-cost-rcf-026, S-cost-rcf-024 | proposed (derived) | cities/ksa/costs/uplifts.yaml; costs/rcf.py |
| A-rcf-031 | Default reference class for all KSA corridor families: OGP 2020 international rail (U-capex-rail-*, U-schedule-rail-*); HSR, 2004, FHB and Green Book entries as sensitivities | rail pooled (n 355 / 133) | choice | HSR sub-class; 2004 class; Green Book point | assumption (TAG A1.2 para 3.5.5 treats rail sub-types as one class, S-cost-rcf-005; OGP recommends international data where UK n < 20, S-cost-rcf-020) | proposed | cities/ksa/costs/uplifts.yaml; docs/reference-class.md |
| A-rcf-032 | Default appraisal stage for every KSA corridor at R1c-R6: strategic (SOBC) | SOBC | stage | OBC as sensitivity | assumption: our corridors are pre-feasibility hypotheses without design, the TAG Stage 1 / PACE 1 definition (S-cost-rcf-005, S-cost-rcf-007) | proposed | costs/rcf.py; docs/reference-class.md |
| A-rcf-033 | Uplifts multiply the real-terms base estimate excluding contingency and QRA; the register `contingency` category is not added on top in the uplifted case | base excl. contingency | rule | base + contingency shown separately as the bottom-up case | assumption from TAG A5.3 formula and OGP definition (S-cost-rcf-007, S-cost-rcf-021) | proposed | costs/rcf.py; docs/costs.md |
| A-rcf-034 | Combined-project split (rolling stock, stations with own classes) is used only as a sensitivity; the default applies the rail class to the whole capex | whole-project rail class | rule | split per TAG A1.2 para 3.5.16 | assumption (avoid stacking) | proposed | costs/rcf.py |
| A-rcf-035 | Ridership class applies to the W8 demand output only as a shortfall sensitivity, never as a forecast correction, while demand is "synthetic demand, uncalibrated: scenario comparison, not a forecast" | U-ridership-rail-fbc (P50 0.70) | ratio | U-ridership-railfhb-fbc (P50 0.46) | assumption; rule 3 | proposed | economics/ (CBA Monte Carlo) |
| A-rcf-036 | Tails beyond printed percentiles (quartile-only and 4-point classes) come from the code's lognormal fit to the printed points | lognormal fit | method | printed range only | assumption (costs/rcf.py docstring) | proposed | costs/rcf.py |
| A-rcf-037 | Schedule ratio multiplies the base duration from stage approval to opening (OGP definition), converted to months | ratio x base months | rule | n/a | assumption from S-cost-rcf-021 | proposed | costs/rcf.py; docs/reference-class.md |
| A-rcf-038 | Opex optimism bias: TAG A5.3 rail opex uplift 41 / 21 / 1 % (SOBC / OBC / FBC) as a sensitivity, not in the default case | 41 % (SOBC) | % of opex | 1-41 % | S-cost-rcf-007 (TAG A5.3 Table 3); OGP rail opex curve S-cost-rcf-014 | proposed | docs/costs.md (opex) |
| A-rcf-039 | KSA schedule sensitivity: report schedule at P80 and P90 of the rail class because Haramain and Riyadh Metro outcomes sit in the upper tail | P80 and P90 | percentile | P50-P95 | derived from the KSA check (S-cost-rcf-037, S-cost-rcf-040, S-035..S-037, S-al_baha-008) | proposed | docs/reference-class.md |
| A-rcf-040 | Capex, schedule and ridership multipliers are drawn independently unless the CBA skill decides otherwise | independent draws | rule | rank correlation as sensitivity | assumption (no source on joint distribution read) | proposed | costs/rcf.py; economics/ |

## Primaries to find
- Flyvbjerg, Glenting and Rønnest (COWI) 2004, Procedures for Dealing with Optimism Bias in Transport Planning: full rail percentile table.
- Mott MacDonald 2002, Review of Large Public Procurement in the UK.
- Published JAPA 2005 version of Flyvbjerg, Holm and Buhl (demand forecasts); published table numbering of FHB 2002.
- NIC 2020 Rail Needs Assessment reference class forecast and dataset.
- Flyvbjerg and Gardner 2023, Appendix A.
- SRO/SAR or MOT statement of the Haramain budget at the decision to build and planned opening date (the "2012" claim); RCRC/ADA award announcement for Riyadh Metro with the approved programme budget.
