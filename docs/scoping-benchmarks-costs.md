> **Document version:** docs/scoping-benchmarks-costs.md v0.1 | 30 Oct 2026 | Author: screening-analyst (PILOT_MERGE), from the benchmarks-researcher and cost-estimator reachability passes | Status: draft

# Scoping note: can the W5 benchmark metrics and the W3 KSA cost points be reached from open sources?

**A reachability map, not the dossier or the cost register.** It contains no cost, ridership or ratio figure. Where a figure exists it sits behind an `S-` id in `docs/sources/index.csv` or at the URL named; the R1b/R1c runs read it, grade it and register it. Access date for every URL: 30 Oct 2026. Pages were seen through search results; unless a line says "read", the page was not opened in full, so each needs a `source-citation` pass before use. Full working tables (gitignored): `logs/pilot_merge/scoping_benchmarks.md`, `logs/pilot_merge/scoping_costs.md`.

## 1. W5 benchmarks: cost/km, ridership vs forecast, farebox (yes / partly / no)

`yes` = an open primary or peer-reviewed source stating the metric, read; `partly` = primary located but not read, or secondary only, or some lines only; `no` = nothing reliable found. The brief names 11 countries; with Italy's Frecciarossa and Italo counted separately, that is the 12 named systems.

| system | cost/km | ridership vs forecast | farebox / op. ratio | best open lead |
|---|---|---|---|---|
| France (TGV/LGV) | partly | partly | partly | Cour des comptes, "La grande vitesse ferroviaire" (2014), ccomptes.fr: connection refused; press relay at banquedesterritoires.fr |
| Japan (Shinkansen) | partly | partly | partly | JR Central disclosures, global.jr-central.co.jp (PDFs unreadable by the fetch tool); Kyushu forecast vs actual only on Wikibooks (grade D) |
| Spain (AVE) | partly | no | partly | Tribunal de Cuentas audits, tcu.es (not opened); Renfe results via trenvista.net (trade press) |
| Germany (ICE) | partly | no | partly | Bundestag Drucksache 19/27544, dserver.bundestag.de (not opened); DB investor relations, ir.deutschebahn.com (segment level only) |
| China (CR HSR) | partly | partly | no | ITF/OECD, itf-oecd.org/sites/default/files/docs/wu-presentation.pdf (2013, dated); OECD assessment of China's HSR investments (not opened) |
| South Korea (KTX) | no | partly | no | Korean Railway Society proceedings 2005, koreascience.kr (early traffic below forecast); KORAIL open data, data.go.kr (ridership, no cost) |
| Italy: Frecciarossa | partly | no | partly | "An Early Evaluation of Italian High Speed Rail Projects", serena.atcult.it (academic, not opened); ART annual report, autorita-trasporti.it (not reached) |
| Italy: Italo (open access) | no (shares Frecciarossa's infrastructure) | no | partly | company results via press (affaritaliani.it); interested-party statements only |
| Morocco (Al Boraq) | partly | partly | partly | Railway Gazette, "Africa's first high-speed line covers its costs" (trade press, ONCF statement); totals conflict, no per-km |
| Turkey (YHT) | no | no | no | UIC e-news on TCDD (2010, outcome only); Sayıştay audit not found |
| UAE (Etihad Rail) | no | no | no | MEED and Gulf Business (press; forecasts conflict); passenger service opened mid-2026, too new |
| Egypt (HSR, under construction) | partly | no (not operating) | no (not operating) | egyptianstreets.com (2020 contract press); scope and financing changed since |
| Cautionary: California HSR | partly | partly (forecast revisions only) | no | Peer Review Group letter on the 2024 Business Plan, stran.senate.ca.gov; hsr.ca.gov returned an empty page |
| Cautionary: UK HS2 | partly | no | no (not operating) | DfT Phase 2 appendix, assets.publishing.service.gov.uk; NAO 2026 report (press relay only) |
| Cautionary (found): Taiwan HSR | no | partly | partly | worldtransitresearch.info record 1382; railjournal.com on the first operating profit |
| Cautionary (found): Brightline Florida | no | partly | partly | KBRA rating action vs the rating-case forecast, kbra.com |
| Cautionary (found): Portugal Porto–Lisbon | partly | no (not operating) | no (not operating) | forbespt.com (press); infrastructure manager and Tribunal de Contas to check |

Counts, all 17 rows: cost/km yes 0 / partly 11 / no 6; ridership vs forecast 0 / 8 / 9; farebox 0 / 9 / 8. Cross-cutting leads: European Court of Auditors special report 19/2018 on EU high-speed rail (official audit; English version not opened), Flyvbjerg, Skamris Holm and Buhl (2005) on ridership forecasts (peer-reviewed; journal paywalled). **Small-town evidence:** Shinkansen in-between municipalities: partly (CEPR working papers; direction mixed to negative); TGV peripheral stations ("gare des betteraves"): partly, qualitative only; AVE intermediate stops: partly (Universitat de Barcelona working paper and UPM accessibility studies; mixed).

## 2. W3 KSA cost data points (quality: primary / press / none)

| data point | quality | price year stated? | existing ids / best lead | main gap |
|---|---|---|---|---|
| Haramain HSR phase 1 civil works | press | no | S-007; railwaygazette.com "Spanish consortium wins Haramain high-speed rail contract" | award date and consortium differ across outlets; outturn unknown |
| Haramain phase 1 stations | press | no | meed.com (to confirm) | KAEC and airport stations not found; post-2019 fire rebuild unknown |
| Haramain phase 2 (Al-Shoula: track, systems, Talgo trains, O&M) | press | no | S-008, S-009 | award vs signing values differ; no capex/trains/O&M split |
| Haramain 2026 train order and O&M extension | press (primary reachable: Talgo CNMV notice, not opened) | no | S-011 (term); railjournal.com, railwaygazette.com | trains bundled with maintenance; the only HSR opex proxy is a lump sum |
| Haramain total programme | press | no | S-010 (unverified), S-lb-021, S-lb-016 | conflict C-004 open; land, O&M, IDC inclusion unknown |
| SAR North line total | press | no | S-023 (unverified), S-lb-023, S-lb-024 | excludes land; length basis conflicts (C-007) |
| SAR North packages, stations, rolling stock, operations | press | no | railway-technology.com, railwaygazette.com, meed.com (new) | package lengths not given, so no per-km yet |
| SAR North: Riyadh–Qurayyat passenger line and bauxite sections, separately | none | — | S-022 (length only) | no separate cost |
| SAR North phosphate-line doubling (2026) | press (MEED estimate) | no | meed.com (new) | section length to pin; the only recent upgrade-type point |
| SAR East line, original (1951) | none | — | — | none expected |
| SAR East doubling (Hofuf–Harad) and Stadler intercity trains | press (Stadler release reachable, not opened) | no | tradearabia.com, railjournal.com (new) | one phase only; trains bundled with maintenance |
| Riyadh Metro: three 2013 packages (BACS, FAST, ANM) and related contracts | press (Siemens datasheet and FCC annual report reachable, not opened) | no | meed.com, technicalreviewmiddleeast.com, bloomberg.com (new) | overlap between packages and rolling-stock/power/PMC awards |
| Riyadh Metro total programme | press | no | S-038, S-039 | conflict C-005 open; award vs outturn |
| Landbridge estimates (all statements in `docs/costs-landbridge.md`) | 7 press, 4 none | no | S-046 to S-063, S-lb-001 to S-lb-034 | no primary read; no price year; MEED Projects is paywalled (rule 12: approval needed) |
| GCC railway Saudi section; Jubail–Dammam; Makkah and Jeddah metros (announced) | press or none | no | S-029, S-030 (scope); meed.com, gulfnews.com | no Saudi-section estimate; metro plans stale |
| SAR company financials (opex, maintenance, staff) | none | — | — | SAR unlisted, wholly PIF-owned: no annual report found |
| Historical railway revenues 1999–2019 (GASTAT via KAPSARC) | primary | nominal by year | data.kapsarc.org (new) | revenue only, East line only; licence to check |

Counts over the 48 rows of the working table: primary 1, press 35, none 12. **No headline KSA capex point (Haramain, SAR North, SAR East, Riyadh Metro, Landbridge) has a primary source in hand**, though several primaries are public and reachable (CNMV notices, Stadler, Siemens and FCC filings, the SPA release on the 2018 Landbridge MoU, the Ministry of Transport post of 16 Nov 2022).

## 3. Gaps that shape R1b and R1c

1. **Primaries to open first** (public, no contact needed): Cour des comptes 2014, Tribunal de Cuentas, Bundesrechnungshof, Korea's Board of Audit and Inspection, Sayıştay, NAO 2026 (HS2), ECA 19/2018 (English); JR Central, DB, Renfe, Italo and THSRC filings (some need a different PDF extraction tool); for KSA, the CNMV, Stadler, Siemens and FCC documents above.
2. **Ex-post ridership against forecast** is nearly absent for conventional HSR in open sources; Japanese ex-post evaluations (MLIT) and ITF/UIC are the next leads.
3. **KSA opex, sand maintenance, terrain-specific capex** (escarpment and sabkha have no KSA data point), **land** and **financing terms**: no KSA source; W3 will lean on W5 benchmarks and registered assumptions, flagged as such.
4. **Price years**: no KSA source states one; the W3 index (A-cost-001) maps award dates to the 2025 price base as a registered assumption.
5. **Licences**: press pages, Wikibooks and preprints need a licence-register check before reuse; MEED Projects is proprietary (Tariq's approval needed before any use).
