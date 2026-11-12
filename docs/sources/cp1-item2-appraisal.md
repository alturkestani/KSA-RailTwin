> **Document version:** docs/sources/cp1-item2-appraisal.md v1.0 | 31 Oct 2026 | Author: rail-data-scout (CP1_PREP) | Status: draft

# CP1_PREP item 2: appraisal assumptions, primary-source check

Access date for every record: 2026-10-31 (Asia/Riyadh). Records are in `docs/sources/cp1-item2.csv` (S-cp1-060 to S-cp1-098; header identical to `docs/sources/index.csv`). Nothing outside the two output files was edited. Downloaded PDFs, spreadsheets and HTML are scratch copies in `/tmp/cp1item2/` and are not committed.

## Summary

| Assumption | Brief said | Finding on the primary source | Result |
|---|---|---|---|
| A-cba-001 social discount rate | Green Book 2022: 3.5% years 0-30, 3.0% years 31-75 | Current Green Book (updated 28 Oct 2026) gives 3.00% (1-30), 2.50% (31-75), 2.25% (76 on). DfT's May 2026 guidance still uses 3.5 / 3.0 / 2.5. The 2022 edition itself could not be retrieved. | CORRECTED (conflict; escalated) |
| A-cba-002 sensitivity 5% and 7% | EC guide section 2.8.8; 5% / 7% | The SDR box is in section 2.8.1, not 2.8.8. The EC guide gives 5% (Cohesion) and 3% (others); it has no 7%. 7% appears only in a World Bank 2016 note Annex II table (OECD 2007 data: Czech Republic 7%, US 3-7%) and within a 2-10% growth-linked range. No MDB transport source recommends 7%. | CONFIRMED for 5%; section corrected; 7% found only as a non-MDB reference (partly confirmed) |
| A-cba-003 commercial 6-8% | Sovereign sukuk/bond evidence | Dated 2026 evidence: Saudi USD sovereign 10-year and 30-year rates of about 4.9-5.9% (Jan 2026 coupons as printed), 10-year 5.598% and 5-year 5.257% (Sep 2026, secondary). Riyal yields not found. The 6-8% band is a premium above these, not supported by the evidence as a level. | Evidence FOUND (range is an assumption; real vs nominal basis unstated) |
| A-cba-004 horizons 30/40/60 and residual value | Green Book and DfT TAG A1.1 | 60 years is the standard for railways (GB 2026 para 6.11; TAG A1.1 para 2.3.3). Residual value is required only for finite lives under 60 years (TAG 2.3.10-2.3.11). No source gives 30 or 40 years as a rail standard. Two asset lives in the cba-appraisal skill (systems 20, rolling stock 30) have no TAG row. | CONFIRMED for 60 and residual rules; 30 and 40 not found as standards; asset lives partly unsourced |
| A-cba-010 value of time | TAG A1.3 table A1.3.1; elasticities 1.0 (work) and 0.8 (non-work) | Table A1.3.1 values confirmed (2023 prices, GBP). The income elasticity is 1.015 for both work and non-work (TAG A1.3 para 4.5.1). The data book defaults are 1.0 and 1.0. The 0.8 figure appears only in the World Bank TRN-15 range (0.5-0.8, UK and Netherlands, 2005). A data-book notice also says to uprate by a flat 1.5% a year. | CORRECTED (elasticity); table values CONFIRMED; transfer ratio computed |

---

## A-cba-001: social discount rate, central case

**Proposed value and range (for coordinator decision; see Escalation E1).** Central: the Green Book 2026 schedule, 3.00% (years 1-30), 2.50% (31-75), 2.25% (76 onward), all real. Reference case kept for comparison: the pre-October-2026 schedule, 3.5% (0-30), 3.0% (31-75), 2.5% (76 onward), which DfT still applies. Sensitivity bounds 5% and 7% are in A-cba-002.

**Supporting ids:** S-cp1-060 (Green Book 2026, para 6.54), S-cp1-061 (supplementary guidance, paras 2.1, 3.7-3.8), S-cp1-062 (TAG A1.1 para 2.7.6), S-cp1-063 (TAG Data Book Table A 1.1.1), S-cp1-064 (Green Book 2022, unverified), S-cp1-065 (CRAN readme, secondary), S-cp1-066 (Freeman and Groom review, Table 1).

**What each source says**

- S-cp1-060, HM Treasury, The Green Book (2026), para 6.54 (printed p.40): "It is set at 3.00% in real terms for years 1 to 30 of an appraisal." Continues: "It is 2.50% for years 31 to 75, and then 2.25% for year 76 onwards." The gov.uk page gives the latest update as 28 Oct 2026, with the change note "Updated to reflect changes to the approach to discounting."
- S-cp1-061, HM Treasury, Green Book supplementary guidance: discounting (October 2026), para 3.8: "3.00% for years 1 to 30", "2.50% for years 31 to 75", "2.25% for years 76 to 125". Para 3.10: discounting "is not an analytically meaningful technique" for impacts after year 125. The 6.54 text says 2.25% from year 76 onward; the supplement caps that band at 125. Minor wording difference, flagged.
- S-cp1-062, DfT, TAG unit A1.1 (May 2026), para 2.7.6: "3.5% should be applied for years between the current year (the year the appraisal is taking place) and year 30 of an appraisal", then "3% for years 31 to 75" and "2.5% for year 76 onwards".
- S-cp1-063, DfT, TAG Data Book v2.03 (May 2026), sheet A1.1.1: standard rates 3.5% (0-30), 3.0% (31-75), 2.5% (76-125), 2.0% (126-200), 1.5% (201-300), 1.0% (301 and over). Its source note cites the Green Book supplementary guidance on discounting dated 2026-05-01, which is before the 28 Oct 2026 change.
- S-cp1-064, Green Book (2022), not retrieved. The attachment URL that a search returned (Green_Book_2022__updated_links_.pdf) now redirects to the 2026 PDF; its MD5 matches the 2026 file. The National Archives copy linked from gov.uk points to an unrelated planning document. The 3.5% / 3.0% figures for 2022 therefore rest on secondary statements only, and the brief's "Annex A6" locator is unverified.
- S-cp1-065, CRAN readme for the R package greenbook (secondary, cites "HMT Green Book 2022 Annex A6"): "stepping from 3.5 percent for the first 30 years down to 1.0 percent beyond year 300." This matches the DfT data book ladder but is not a primary source.
- S-cp1-066, Freeman and Groom, Green Book Discount Rate Review (30 June 2026), Table 1: standard projects 3.0% (0-30), 2.5% (31-75), 2.25% (76-125). The review states it is "not ... HM Treasury policy". Its figures match the October 2026 Green Book. Whether HM Treasury adopted the review in full is an inference from that match, not something a source states.

**Discrepancy with the brief (labelled):** The brief's rates (3.5% then 3.0%) are the schedule the 2026 Green Book replaced. On the sources read, the 2026 central case is 3.0% then 2.5% then 2.25%. Tariq approved 3.5% on 30 Oct 2026, two days after the 28 Oct update. Whether he saw the update is unknown. Escalated (E1). Per the rule against bending sources, the register should cite the 2026 text, not the 2022 text, unless he chooses otherwise.

**Status.** Central rate: corrected (source differs from brief). Reference schedule (3.5 / 3.0 / 2.5): verified as DfT's May 2026 practice; the 2022 edition itself: unverified.

---

## A-cba-002: sensitivity rates 5% and 7%

**Proposed sensitivity set (for coordinator).** 3.5% (superseded UK rate, kept as a sensitivity), 5% (EC Cohesion benchmark), 7% (upper reference from the World Bank 2016 Annex II table). ADB's 9% minimum EIRR (S-cp1-072) is a possible extra reference point, not a sensitivity; the ADB social-sector rate is 6%.

**Supporting ids:** S-cp1-067 (EC guide, benchmark, secondary host), S-cp1-068 (EC guide, no 7% found), S-cp1-069 (WB 2016 Annex II), S-cp1-070 (WB 2016 growth range), S-cp1-071 (WB 2016, 8-12%), S-cp1-072 (ADB 2017 para 194), S-cp1-073 (ADB 1987, wrong edition, not used).

**Section number correction.** The brief cites EC guide section 2.8.8. In the December 2014 guide, section 2.8.8 is "Evaluation of GHG emissions". The benchmark box is in section 2.8.1 "Introduction" (PDF p.57; the page header reads 55). Annex II, "The social discount rate", starts at about PDF p.303.

**What each source says**

- S-cp1-067, European Commission, Guide to Cost-Benefit Analysis of Investment Projects (December 2014), section 2.8.1: "the European Commission recommends that for the social discount rate 5 % is used for major projects in Cohesion countries and 3 % for the other Member States." Also: Member States may set a different benchmark if justified by "an economic growth forecast and other parameters". The guide's own scope is the 2014-2020 programming period.
- S-cp1-068, the same guide, full-text search: no 7% social discount rate found. The text does not give a 7% sensitivity for the SDR.
- S-cp1-069, World Bank, "Discounting Costs and Benefits in Economic Analysis of World Bank Projects" (9 May 2016), Annex II (PDF p.10): the table is adapted from OECD (2007) and gives "Czech Republic 7% 20-30", "United States 3-7%", "Australia 6-7%", "Denmark 6-7%", "Canada 5-10%", "United Kingdom 3.5% for 30 years, declining thereafter", "South Africa 8%", "Mexico 12%". It is not a World Bank rate. The note also says it "is not World Bank policy nor is it mandatory" (cover page).
- S-cp1-070, same note, PDF p.2: "per capita growth rates of 1%-5% yield discount rates of 2%-10%." A 3% per capita growth rate "translates into a 6% discount rate". This range includes 7%, but 7% is not a stated outcome.
- S-cp1-071, same note, PDF p.3: "Many authors favoring the descriptive approach generally suggest discount rates for developing countries in the 8-12% range." Presented as the views of "many authors", not a recommendation.
- S-cp1-072, Asian Development Bank, Guidelines for the Economic Analysis of Projects (2017), para 194 (printed p.53; PDF p.66): "ADB uses a discount rate of 9% as the minimum required EIRR to accept or reject a project." A "lower discount rate of 6% can be applied" for social-sector, poverty-targeting and environmental projects, with a stated rationale. No 7% rate.
- S-cp1-073, the adb.org link under "institutional-document/149712" is the 1987 Guidelines (Economics Office, August 1987), not the 2017 revision. Do not cite it for current ADB rates.

**Assessment.** 5% is confirmed as the EC benchmark (not as a transport recommendation). 7% has no MDB recommendation behind it. The only citable 7% is a national rate in an OECD-derived table, and the range 2-10% comes from a growth-linked rule. The brief's sentence "if no source gives 7%, say so" applies in part: no transport-appraisal source gives 7% as a rate. Some source (the WB table) does show 7%, but it is not an MDB transport benchmark.

**Status.** 5%: confirmed (EC benchmark; secondary host). 7%: found only as a reference value outside MDB transport guidance; partly confirmed. Section number 2.8.8: corrected to 2.8.1.

---

## A-cba-003: commercial / financial rate, 6-8% range

**Proposed value and range (for coordinator).** Keep 6-8% as the assumed range, labelled as a premium over sovereign evidence. The evidence supports a floor near the sovereign curve (about 4.9-5.9% nominal USD for 10- to 30-year paper in 2026, as printed or as reported) and does not on its own support 8%. Basis (real vs nominal) must be stated (Escalation E4).

**Supporting ids:** S-cp1-074 (NDMC, Jan 2026 USD issue), S-cp1-075 (NDMC, Sep 2026 trust certificates), S-cp1-076, S-cp1-077, S-cp1-078 (US Treasury curve, 1 Sep 2026, 12 Jan 2026, 30 Oct 2026), S-cp1-079 (Sep 2026 coupons, secondary), S-cp1-080 (T+70/T+80, unverified), S-cp1-081 (S&P A+), S-cp1-082 (Aug 2026 riyal sukuk, secondary), S-cp1-083 and S-cp1-084 (Jan 2026, unverified).

**What each source says**

- S-cp1-074, NDMC, Global Medium Term Note Issuance Program page (verified on ndmc.gov.sa). The 2026 USD issue table, column headed "Yield" as printed, lists "12/01/2036 4.875%" (2036 tranche) and "12/01/2056 5.875%" (2056 tranche); the 2029 and 2031 tranches are 4.125% and 4.375%. Total USD 11.5bn. The page shows dates as dd/mm/yyyy, so 12/01/2026 is read as 12 Jan 2026 (assumption; release date not shown on this page).
- S-cp1-075, NDMC news item 373929 (page date 01/09/2026, read as 1 Sep 2026): "for a 10 -year Sukuk maturing in 2036"; 5-year tranche maturing 2031 at USD 1.25bn; 10-year at USD 2bn; total USD 3.25bn; order book around USD 16.5bn. The release gives no profit rate or spread.
- S-cp1-079, The Halal Times (3 Sep 2026, secondary; cites Funds Global MENA, 2 Sep 2026): "The five-year tranche came at 70 basis points over US Treasuries, carrying a fixed coupon of 5.257%" and the 10-year "80 basis points over Treasuries, carrying a fixed 5.598% coupon". Needs the NDMC pricing supplement to become primary.
- S-cp1-076 to S-cp1-078, US Treasury daily par yield curve (verified, CSV). 1 Sep 2026: 5Y 4.55%, 10Y 4.79%. 12 Jan 2026: 10Y 4.19%, 30Y 4.83%. 30 Oct 2026: 10Y 4.94%, 30Y 5.31%.
- S-cp1-081, NDMC news item 715960: "S&P Global affirms the Kingdom of Saudi Arabia's credit rating at A+ with a stable outlook" (date not stated on the page).
- S-cp1-082, Arab News (19 Aug 2026, secondary): the domestic riyal sukuk, "SR9.52 billion ($2.54 billion)", five tranches maturing 2031 to 2041. No yield stated. No riyal yield was found on a primary page.
- S-cp1-080 and S-cp1-083, press summaries seen only as search snippets (AGBI returned HTTP 403; Arabian Business not opened): T+70 / T+80 (Sep 2026) and about 110bp / 140bp over Treasuries (Jan 2026, IFR; basis not stated). Unverified; not used for any figure.

**Derived checks (arithmetic run on the sourced values, not sourced figures).**

- Jan 2026 implied spreads over the 12 Jan Treasury curve: 10-year 4.875 minus 4.19 = about 69bp; 30-year 5.875 minus 4.83 = about 105bp. These are below the 110bp and 140bp reported via IFR (S-cp1-083; basis not stated in the snippet). The gap is not resolved here: the reported figures may be talk rather than final pricing, and the date reading may differ. Flagged, not averaged.
- Sep 2026 implied spreads over the 1 Sep curve: 5-year 5.257 minus 4.55 = about 71bp; 10-year 5.598 minus 4.79 = about 81bp. These match the reported T+70 and T+80, so the secondary pricing is internally consistent with the Treasury curve.
- Indicative current 10-year USD sovereign: 30 Oct 2026 Treasury 10Y 4.94% plus the Sep 2026 10-year spread of about 80bp gives about 5.7% (derived; not a quote).
- Premium of the 6-8% band over the sovereign points: 6% is 0.1-1.1 pp above the 2026 10- and 30-year coupons; 8% is 2.1-3.1 pp above them. The band's premium is an assumption, not an observed spread.

**Discrepancy and gap.** The sources are nominal USD and sovereign. The appraisal is in real SAR (price base 2023 or 2025 per A-cost-001). The brief does not say whether 6-8% is real or nominal, and no riyal sovereign yield was found. Escalated (E4).

**Status.** Evidence: FOUND (two or three dated data points, as the brief asked; the Jan and Sep 2026 issues plus Treasury curve). The 6-8% range itself: assumed, unchanged; basis unresolved.

---

## A-cba-004: appraisal horizons (30 / 40 / 60 years) and residual value

**Proposed (for coordinator).** Central: 60-year appraisal after opening, the TAG and Green Book standard for railways. Finite-life variants of 30 and 40 years are scenario cases only and need residual value per TAG. Maximum 100 years (TAG design-life rule) as a sensitivity. Asset lives for residual value need a source per asset class (Escalation E5).

**Supporting ids:** S-cp1-085 (TAG A1.1 paras 2.3.3, 2.3.5), S-cp1-086 (TAG A1.1 paras 2.3.10-2.3.11), S-cp1-087 (TAG A1.1 Table 2), S-cp1-088 (Green Book 2026 paras 6.11-6.12), S-cp1-089 (Green Book 2026 para 8.32).

**What each source says**

- S-cp1-085, DfT TAG A1.1 (May 2026), para 2.3.3: the appraisal period covers "60 years from when the scheme opens". Para 2.3.5: "Whilst an appraisal period of 60 years is suitable for the majority of schemes", longer periods may be a sensitivity test, and "in all cases should be no more than 100 years".
- S-cp1-088, Green Book 2026, paras 6.11-6.12 (printed p.33): "60 years for infrastructure, such as roads, railways and new buildings"; "30 years for refurbishment of existing buildings"; "10 years as a standard measure for all other proposals". For periods beyond 60 years, "practitioners should discuss and agree a suitable appraisal period with HM Treasury". That is a UK rule.
- S-cp1-086, TAG A1.1 paras 2.3.10-2.3.11: "Residual asset values should be included in CBA of projects with finite lives of fewer than 60 years." Residual values "should not be included for projects with indefinite lives with an appraisal period ending 60 years or more after scheme opening".
- S-cp1-089, Green Book 2026, para 8.32: "An asset's residual value or liability at the end of the appraisal period should be included to reflect its opportunity cost."
- S-cp1-087, TAG A1.1 Table 2 (printed p.7), railway column as printed: track 14 to 40; electrification 30 to 40; signalling 10 to 50; telecommunications 7 to 40; earthworks 100; bridges and tunnels up to 100; buildings 30 to 40 (the table's column placement comes from text extraction and should be re-checked visually). The table's source note cites World Bank Transport Note TRN-18, "Projects with a Very Long Life".

**Discrepancies with the brief and the skill (labelled).**

- 30 and 40 years are not standard horizons in any source read. The Green Book's 30-year period applies to refurbishment of existing buildings, not railways. They can be scenario variants, not defaults.
- The cba-appraisal skill's example asset lives are civil 100, track 40, systems 20, rolling stock 30. Civil 100 and track 40 (top of the 14-40 range) match TAG. Systems 20 has no single TAG row (signalling 10-50, electrification 30-40, telecoms 7-40). Rolling stock 30 has no TAG row; the table covers infrastructure only. These two values are unsourced.
- Saudi guidance on horizons and residual value was not searched in this item.

**Status.** 60-year standard and residual-value rules: CONFIRMED. 30 and 40 years as rail standards: NOT FOUND. Systems and rolling-stock asset lives: NOT SOURCED (partly).

---

## A-cba-010: value of time transfer and income elasticity

**Proposed values (for coordinator).** Base values: DfT Table A1.3.1 (2023 prices, 2023 values, GBP): working person average GBP 25.23/h perceived cost (GBP 30.03/h market price); non-working commuting GBP 15.51/h; non-working other GBP 7.08/h. Elasticity for uprating: 1.015 (TAG A1.3 para 4.5.1) for both work and non-work, with the data book's flat 1.5% a year as an alternative to test (Escalation E6). Transfer to KSA: the World Bank TRN-15 method (non-working time 0.3 x household income per head where no local evidence exists) is the fallback; the income-elasticity range 0.5-0.8 from TRN-15 is a sensitivity on the transferred value.

**Supporting ids:** S-cp1-090 (TAG A1.3 para 4.5.1, elasticity 1.015), S-cp1-091 (TAG A1.3 para 4.3.2, GDP per capita elasticity of 1 for the 2010 conversion), S-cp1-092 (Data Book Table A 1.3.1), S-cp1-093 (Data Book Default Pars), S-cp1-094 (Data Book uprating notice), S-cp1-095 (TRN-15 elasticity 0.5-0.8), S-cp1-096 (TRN-15 Table 2 default), S-cp1-097 (WDI Saudi Arabia 2025), S-cp1-098 (WDI UK 2025).

**What each source says**

- S-cp1-090, DfT TAG A1.3 (May 2026), para 4.5.1: "Both the work and non-work values of time (excluding journeys by LGV or OGV) are assumed to increase with income over time with an elasticity of 1.015." Para 4.5.2: non-freight LGV "elasticity of 1.0".
- S-cp1-091, TAG A1.3 para 4.3.2: "The values have been converted to 2010 values and prices in line with the growth in income (with a GDP/capita elasticity of 1)" for the 2014/15 research values.
- S-cp1-092, TAG Data Book v2.03, sheet A1.3.1, Table A 1.3.1, "(£ per hour, 2023 prices, 2023 values)". Working person average (passenger only): perceived cost 25.23, market price 30.03. Non-working: commuting 15.51 (perceived = market), other 7.08. Rail passenger working time 38.22 perceived, 45.48 market. Indirect tax correction factor 1.19 noted.
- S-cp1-093, Data Book sheet "Default Pars", rows 24-25: "Elasticity of non-work-time value of time to GDP/head": work elasticity 1, non-work elasticity 1.
- S-cp1-094, Data Book notices (sheets A1.3.1 row 18 and "Annual Parameters" note 4, row 31): "should now be uprated by 1.5% each year from the appraisal year onwards". This is a flat real uprating, not an elasticity-to-GDP rule. The two methods conflict and the choice is not stated in the sources.
- S-cp1-095, World Bank Transport Note TRN-15, "Valuation of Time Savings" (January 2005), section on time trends (printed p.7 of 13): "Studies in the UK and Netherlands have indicated elasticities of VoT with respect to income of approximately 0.5 to 0.8." The same note says the value of non-work time "increases less than proportionally with income" (p.5).
- S-cp1-096, TRN-15 Table 2 (p.10 of 13): base approach for non-working time: "0.3 x Household income (per head)" for adults, 0.15 for children, walk/wait modifier 1.5 x in-vehicle time. Income-group values are recommended for pricing projects where travellers pay to save time (p.8).
- S-cp1-097 and S-cp1-098, World Bank WDI API (last updated 8 Oct 2026), NY.GDP.PCAP.PP.CD (current international $): Saudi Arabia 2025 = 73,783.56; United Kingdom 2025 = 64,606.50.

**Derived transfer ratio (not a sourced figure).** Saudi / UK GDP per capita PPP, 2025 = 1.142. Illustrative factor ratio^e: e = 0.5 gives 1.069; 0.8 gives 1.112; 1.0 gives 1.142; 1.015 gives 1.144. These show the sensitivity to the elasticity choice. They are not a transfer method: PPP-based GDP per capita is one choice, household income in local prices would be another, and the price bases (2023 GBP vs 2025 PPP) must be aligned before use.

**Discrepancies with the brief (labelled).**

- The brief's "1.0 for working time and 0.8 for non-working" is NOT the DfT figure. DfT gives 1.015 for both (TAG A1.3 para 4.5.1), and the data book defaults are 1.0 and 1.0. The 0.8 figure appears only as the top of TRN-15's 0.5-0.8 range for non-work time (UK and Netherlands, 2005). CORRECTED.
- The data book's 1.5% flat uprating notice conflicts with the elasticity approach in TAG A1.3. Escalated (E6).
- The table values are in 2023 prices; the brief asks for the price base. Recorded: GBP, 2023 prices, 2023 values.

**Status.** Table A1.3.1 values: CONFIRMED. Income elasticity: CORRECTED (1.015 work and non-work; data book 1 and 1; TRN-15 0.5-0.8 for non-work). Transfer by income: TRN-15 (WB) found; ITF and OECD sources not searched. WDI values: CONFIRMED (API, 2025).

---

## Escalations (for coordinator; not decided here)

- **E1 (A-cba-001, material).** The Green Book's central rate changed on 28 Oct 2026 to 3.00% / 2.50% / 2.25%. The register and Tariq's 30 Oct approval use 3.5% / 3.0% from the 2022 edition, which could not be retrieved. Decide the central case, whether the 2022 schedule stays as a reference case, and whether the register cites the 2026 text. Also check whether Tariq's approval was made knowing of the 28 Oct change.
- **E2 (A-cba-002, ID conflict).** The cba-appraisal skill's example assigns A-cba-002 to the commercial rate; the brief assigns A-cba-002 to the sensitivities and A-cba-003 to the commercial rate. Rows A-cba-002, -003, -004 and -010 are not in `docs/assumptions.md` (only A-cba-001 is). The register needs rows for each, and the skill example needs aligning.
- **E3 (A-cba-002, 7%).** No transport-appraisal source gives 7% as a recommended rate. Decide whether 7% stays as a sensitivity on the basis of the WB Annex II table (OECD 2007 data) and the 2-10% growth range, or whether the sensitivity set is 3.5 / 5 / 9%.
- **E4 (A-cba-003, basis).** The commercial 6-8% is not stated as real or nominal. The sovereign evidence is nominal USD. Decide the basis, and whether a SAR-denominated (riyal) rate should replace the USD evidence. No riyal sovereign yield was found on a primary source.
- **E5 (A-cba-004, asset lives).** Systems 20 and rolling stock 30 in the skill's residual-value example have no TAG row. Decide the source (manufacturer or operator data, or a project-specific assumption) before use. Also decide whether 30 and 40 years are scenarios or defaults.
- **E6 (A-cba-010, uprating).** TAG (elasticity 1.015), the data book defaults (1 and 1), the data book notice (flat 1.5% real), and TRN-15 (0.5-0.8 non-work, 2005) give different answers. Choose one method for the base case and state the price base (2023 GBP) and the transfer method for Saudi Arabia.
- **E7 (access).** The European Commission's own host of the 2014 guide returned 404/500 on 31 Oct 2026, so the text was read from the JASPERS (EIB) copy. The NDMC news pages returned 404 on direct requests, but the item pages (news-details/30151) were read. Halal Times and Arab News were read as secondary sources. AGBI (403) and Arabian Business (not opened) are snippets only and are unverified.

## Method notes

- Every quote was checked by machine against the text that was read (pdftotext output of the PDFs, the JSON from the WDI API, the CSV from the US Treasury, and the cached HTML). The check found no mismatches. Quotes marked secondary come from press pages, and the status says so.
- Status rule applied: verified = read on the publisher's own site or document on 2026-10-31; secondary = press, aggregator or a non-publisher copy, with `primary_to_find` filled; unverified = search snippet only or not retrievable.
- The brief's section and page references were checked against the sources. Where the brief and the source differ, the source is reported (the EC section, the Green Book rate, the elasticity).
- No real-world action was taken: no contact, sign-up or submission. All reads were public downloads or public APIs.
