> **Document version:** docs/funding.md v0.2 | 31 Oct 2026 | Author: funding-ppp-analyst A (R1d) (sections), funding-ppp-analyst B (case studies), R1d builder (integration) | Status: draft

# Funding, ownership and delivery models: options landscape (W6, R1d)

## Purpose and scope

This document answers "who pays, who owns, who operates and who carries which risk" as a **landscape of options**, not a recommendation. It is non-partisan (rule 9): entity names (PIF, SAR, NCP, TGA, concessionaires, contractors) are facts with sources, not endorsements. Per-corridor recommendations, filled risk matrices and fiscal exposure ranges (P10/P50/P90) are R7 outputs and depend on the W3 cost and W4 demand distributions; nothing here is a forecast.

- Machine-readable register: `cities/ksa/funding/models.yaml` (13 required options plus one hybrid; validated by `uv run python -m funding.models validate`).
- Risk matrix template: `cities/ksa/funding/risk_matrix_template.yaml` (validated by `uv run python -m funding.risk_matrix validate`).
- Sources: `docs/sources/r1d-fund.csv` (this track's rows) and existing Landbridge and Haramain rows in `docs/sources/index.csv`. Status of each source (verified / secondary / unverified) is in the CSV; unverified rows carry no figure into any model.
- Where the law or practice is not public, this document writes **unclear** and the precise question. No legal position is inferred.

Fiscal-treatment vocabulary used throughout:

- **IPSAS 32** (accrual accounting, grantor side): the grantor recognises the asset and a liability when it controls or regulates the services, the users and the price, and controls the residual interest (S-fund-017). It pays the operator either by payments (financial-liability model) or by granting a right to charge users (grant-of-a-right model) (S-fund-018).
- **Eurostat / ESA 2010** (statistics, via the EPEC guide): the PPP sits on the balance sheet of the economic owner, the party bearing most risks and rewards; if inconclusive, control decides; assessed at financial close (S-fund-019). The guide warns against an excessive focus on off-balance-sheet treatment (S-fund-020).
- **IMF / World Bank PFRAM 2.0**: estimates the timing and size of government payments, their deficit and debt effects, and contingent liabilities (debt guarantees, minimum revenue guarantees) under a worst case (S-fund-021); distinguishes government-funded, user-funded and combined PPPs (S-fund-022); notes that under IPSAS 32 most PPPs would be on balance sheet and that guarantees are contingent liabilities reported as memorandum items (S-fund-023).

## Delivery and funding options

Abbreviations: pub = public, priv = private, sh = shared, var = varies by contract. The allocation is the typical one described in the cited sources, not a proposal for any Saudi corridor. Definitions, fiscal treatment and "when it fits" for each option are in `models.yaml`.

| id | family | who pays | who owns / operates | typical term (years) | risk allocation (constr / demand / revenue / ops / fin / land / reg-FM) | sources |
|---|---|---|---|---|---|---|
| `fully_public_budget` | public | Taxpayers through the state budget; users through fares set by the state. | The state (ministry or state agency). / State agency or state-owned operator (O&M may be contracted out; see public_with_private_om). | no contract term; asset life and budget cycle apply | pub / pub / pub / pub / pub / pub / pub | S-007, S-008, S-fund-024, S-fund-025, S-fund-026, S-lb-021 |
| `fully_public_pif` | public | PIF (equity or shareholder loans), ultimately repaid from project revenues or written off against PIF returns; users through fares and freight tariffs. | PIF or a PIF-owned company. / A PIF-owned company or a contracted operator. | no contract term; investment horizon set by PIF; not published for rail | pub / pub / pub / var / pub / pub / pub | S-fund-023, S-fund-036, S-fund-038, S-lb-009, S-lb-012 |
| `fully_public_sar` | public | SAR from its funding (state budget transfers, PIF or borrowing; split not published) and from fares and freight tariffs. | SAR (ownership of SAR itself: secondary sources say PIF; see docs/funding.md). / SAR, directly or through contracted operators (for example Renfe on Haramain). | no concession term; D&B and O&M contract terms vary | var / pub / pub / var / pub / pub / pub | S-059, S-060, S-fund-033, S-fund-035, S-lb-001 |
| `public_with_private_om` | public_private | The asset owner pays an O&M fee; users pay fares to the owner (fare revenue not normally kept by the operator unless the contract says so). | State or state-owned company. / Private operator (or consortium). | Haramain O&M period reported to 2038 after extension; original term not confirmed (S-011 unverified) | pub / pub / pub / priv / pub / pub / sh | S-008, S-fund-001, S-fund-039 |
| `ppp_dbfom_availability` | ppp | The state through availability payments over the term (plus any construction-period contribution); users pay fares to the state. | State (asset typically reverts or is held by the grantor); SPV holds contractual rights. / Private SPV (operator subcontractor). | 20-30 (S-fund-045) | priv / pub / pub / priv / priv / pub / sh | S-fund-002, S-fund-004, S-fund-017, S-fund-019, S-fund-021, S-fund-043, S-fund-045 |
| `ppp_dbfom_demand_risk` | ppp | Users (fares or access charges passed through operators), with a public capital grant; any minimum revenue guarantee is a contingent public cost. | Grantor owns; concessionaire holds the right to operate and collect revenue. / Concessionaire (infrastructure) and/or train operators. | 30-50 (S-fund-046) | priv / priv / priv / priv / priv / pub / sh | S-fund-002, S-fund-018, S-fund-019, S-fund-023, S-fund-046, S-fund-047 |
| `ppp_dbfm` | ppp | The state or infrastructure manager through availability payments (loyers) after a construction-period contribution. | State or infrastructure manager. / Separate train operator; SPV maintains infrastructure. | 25-30 (S-fund-043) | priv / pub / pub / pub / priv / pub / sh | S-fund-002, S-fund-017, S-fund-019, S-fund-043, S-fund-044 |
| `vertical_separation_infra_public_ops_private` | public_private | State funds infrastructure; operators pay access charges; users pay fares to operators. | Public infrastructure owner or manager. / Licensed private (or public) train operators. | licence or path-allocation terms vary; no source for a typical term | pub / sh / sh / priv / pub / pub / sh | S-fund-015, S-fund-016, S-fund-051 |
| `integrated_concession` | ppp | Users through fares and freight tariffs; state through capital grants or guarantees if any. | Concessionaire during the term; reverts to the grantor at the end (BOT). / Concessionaire. | 30-50 (S-lb-012) | priv / priv / priv / priv / priv / sh / sh | S-fund-007, S-fund-013, S-fund-018, S-fund-023, S-lb-012, S-lb-017 |
| `private_concession` | private | Users and the company's investors; non-fare business revenue. | Private company (subject to the concession or licence). / Private company. | Japanese private-railway rights described as indefinite in the cited paper (S-fund-052); no Saudi precedent found | priv / priv / priv / priv / priv / var / sh | S-fund-012, S-fund-013, S-fund-017, S-fund-022, S-fund-052 |
| `lvc_station_area_development` | land_value_capture | Property buyers and tenants (through land and property value); the state forgoes land premium it could otherwise collect. | Rail company or developer holds development rights; land ownership per local law. / Rail company (railway) and developer (property). | varies with land tenure; no source for a typical term | var / var / sh / var / var / pub / sh | S-fund-014, S-fund-048, S-fund-052 |
| `lvc_betterment_levy` | land_value_capture | Property owners or businesses in the levy area. | The state or local authority (asset ownership unchanged). / Unchanged (any delivery model). | Crossrail BRS ran from April 2010 and continues in 2026-27 (S-fund-049); no typical term | pub / pub / sh / pub / pub / pub / pub | S-fund-049 |
| `lvc_tax_increment` | land_value_capture | Future taxpayers in the zone (the increment), developers through contributions. | The state or local authority. / Unchanged (any delivery model). | 25 (S-fund-050) | pub / pub / sh / pub / pub / pub / pub | S-fund-050 |
| `hybrid_public_dbfm_plus_station_lvc` (mix: fully_public_sar, ppp_dbfm, lvc_station_area_development) | hybrid | State (civil works and availability payments), users (fares to the state), property market (station-area value). | State company owns infrastructure; SPV holds a service contract; developers hold development rights. / State company or the SPV's operator, per package. | 20-30 (S-fund-045) | sh / pub / sh / var / sh / pub / sh | S-fund-023, S-fund-045, S-fund-048 |

Reading the table:

- The three fully public options differ in **who finances and reports** the cost (budget, PIF, SAR), not in who carries risk: in all three the state side keeps demand and financing risk. How PIF- or SAR-financed rail is reported in Saudi public accounts is **unclear** (see the Saudi-frame table).
- Availability PPPs (`ppp_dbfom_availability`, `ppp_dbfm`) transfer construction and whole-life maintenance risk but leave demand with the state and create long-term payment commitments; under IPSAS 32 they are usually on the government balance sheet (S-fund-017, S-fund-023).
- Demand-risk PPPs and concessions (`ppp_dbfom_demand_risk`, `integrated_concession`, `private_concession`) transfer ridership risk; the LGV SEA ex post review records taxpayer protection from overruns but also traffic below public-inquiry forecasts and a record per-km cost (S-fund-046, S-fund-047). The 2008 Landbridge 50-year BOT did not reach financial close (S-lb-012, S-lb-017; secondary).
- Land value capture options are **funding sources** that combine with any delivery model (Hong Kong Rail-plus-Property S-fund-048; Crossrail BRS S-fund-049; Northern Line Extension increment S-fund-050). Saudi legal instruments for them were not reviewed here (unclear; see table).

## Case studies

### 1. Japan: JNR break-up, JR East, and private railways with real estate (Tokyu)

**Structure.** In April 1987 the state-owned Japanese National Railways (JNR) was split into regional passenger companies (including JR East) and a freight company, while most of JNR's legacy debt was moved to a public JNR Settlement Corporation (S-fund-200, S-fund-201). The JR companies are vertically integrated (they own track and run trains) and operate as commercial companies. Tokyu Corporation is a privately owned railway that has developed residential, retail and commercial property along its lines since the Tama Den-en-toshi project began in 1955 (S-fund-208).

**Who paid (capex sources).**
- Legacy network and debt: at the reform, JNR's long-term debts and other liabilities were JPY 37.1 trillion (nominal, 1987) (S-fund-200). The Settlement Corporation took JPY 25.5 trillion (S-fund-201). The new JR companies took JPY 11.6 trillion, or JPY 14.5 trillion in practice once the Shinkansen lease fees taken on by JR East, JR West and JR Tokai are included (S-fund-202).
- The Settlement Corporation's repayment sources were JNR land and the stocks of the seven JR companies, estimated at JPY 11.8 trillion at the start of FY1987. The government's remaining share was calculated at JPY 13.8 trillion (S-fund-203). Between 1987 and 1995 it sold about 5,800 ha of land for JPY 4.6 trillion (S-fund-204). The first sale of JR East shares raised JPY 1.1 trillion for 2.5 million shares (S-fund-205). Land and share sales therefore made the former rail estate a direct source of debt repayment.
- Tokyu: the line-side development was financed by the company. The secondary source reports no government subsidy, in contrast with MTR's land arrangement (S-fund-208). Primary financing amounts: no reliable data found in the sources read.

**Who carried demand risk.** JR East and Tokyu carry ridership risk as commercial operators. COVID-19 showed the size of this exposure: JR East's average daily passengers were about 17.8 million on 1 Apr 2020 and about 12.4 million on 1 Apr 2021 (S-fund-210). The legacy-debt risk (whether land and share sales would cover the transferred debt) stayed with the state (S-fund-203).

**What happened.**
- The Settlement Corporation's asset sales covered only part of the debt it took on (S-fund-203, S-fund-204). How and when the remaining debt was finally settled is not covered by the sources read: no reliable data found here; the primary source to find is later MLIT white papers.
- Non-fare business is a material part of the profit mix. In 2019, real estate was 29% of Tokyu's segment profits and transportation 41% (S-fund-207, secondary). JR East's retail and services segment was 8% of profits and transportation 70% (S-fund-206, secondary).
- After COVID, JR East's FY2026 plan ("Move Up" 2027, published 2021) targeted consolidated operating income of JPY 450.0 bn (nominal, target), of which transportation JPY 252.0 bn, real estate and hotels JPY 113.0 bn, and retail and services JPY 57.0 bn (S-fund-209). These are targets, not outturns. FY2026 actuals: no reliable data found (the JR East IR site returned "Access Denied" on 2026-10-31).
- Hankyu and other private railways: no source was read in this pass, so they are not documented. They remain a gap.

**Lessons as evidence.**
- Separating legacy debt from the operating companies allowed commercial JR companies to start without the full debt load. The cost of that separation fell on the public sector, and land and share sales recovered only part of it (S-fund-200 to S-fund-205).
- Where a railway owns or controls the land around its stations and can develop it, property income can match or approach transport income (Tokyu: S-fund-207). Where it mainly runs in-station retail, the property share is smaller (JR East: S-fund-206). Both figures are secondary.
- Integrated commercial operators carry the full ridership shock (S-fund-210).

**Evidence grade.** B. The debt settlement comes from a primary government source (verified). The segment profit shares are secondary (a student research paper citing company filings). JR East's targets come from a JR East presentation (verified). Current financials and Hankyu are not covered.

### 2. Hong Kong: MTR "Rail plus Property" (R+P)

**Structure.** The MTR Corporation is a vertically integrated owner-operator. It was wholly government-owned until its listing in 2000 (S-fund-216). Under R+P, the Government grants the railway company property development rights at or above stations and depots. The company develops the sites, usually with private developers, and uses the proceeds to close the funding gap of rail lines that are otherwise financially non-viable (S-fund-216, S-fund-217). R+P financed the Kwun Tong, Tsuen Wan, Island, Airport Railway and Tseung Kwan O lines (S-fund-216).

**Who paid (capex sources).**
- The railway company arranges and pays the construction cost up front. It also pays operating and asset-replacement costs, and later the property development costs and the land premium (S-fund-217).
- The Government's contribution is the value of the development rights rather than cash. For two lines approved in 2011, an independent consultant estimated the costs and funding gaps as follows (S-fund-218), and the Government judged that the property "may barely bridge" those gaps:

| line | capital cost | funding gap | source |
|---|---|---|---|
| South Island Line (East) | HKD 12.4 bn (estimate, 2011–12) | HKD 9.9 bn | S-fund-218 |
| Kwun Tong Line Extension | HKD 5.3 bn (estimate, 2011–12) | HKD 3.3 bn | S-fund-218 |

- Not every line uses R+P. The West Island Line received a capital grant of HKD 12.7 bn (nominal) approved by LegCo. The XRL (Hong Kong section) and the Shatin to Central Link were built under a "concession approach", with construction funded by the Government through public works (S-fund-219).
- At the 2007 merger with KCRC, MTRCL paid KCRC HKD 4.91 bn (nominal) for the development rights over eight sites (S-fund-220).

**Who carried demand risk.** MTRCL carries ridership risk and property-market risk. Because flats can usually be sold only about ten-odd years after rail construction starts, the company also bears a long financing gap (S-fund-217). The Government describes R+P as sharing risks and benefits (S-fund-217).

**What happened.**
- In 2024 MTR reported (all HKD million, nominal; S-fund-211 to S-fund-214):

| item | 2024 | source |
|---|---|---|
| total revenue | 60,011 | S-fund-211 |
| profit from recurrent businesses | 7,210 | S-fund-212 |
| Hong Kong property development profit | 10,235 | S-fund-213 |
| net profit attributable to shareholders | 15,772 | S-fund-214 |

- MTR states that the 2024 net profit was "primarily" due to one-off property bookings from railway projects completed in earlier years (S-fund-214). Patronage on the Hong Kong network exceeded 1.9 billion in 2024, and MTR reports HKD 100 bn of investment already committed (S-fund-215).
- A secondary source puts real estate at 75% of MTR's profits in 2018 and transportation at 16% (S-fund-221).
- Renegotiations, bailouts or write-downs specific to R+P: none found in the sources read. The full MTR annual reports were not read in this pass.

**Lessons as evidence.**
- R+P works as a subsidy paid in land value instead of cash. Its size depends on property prices and on the planning parameters for the sites. The Government itself noted that rising development costs could leave the gap only barely bridged (S-fund-218).
- Property profit is lumpy and arrives with a long lag, so reported profits swing from year to year with booking cycles (S-fund-214, S-fund-217).
- In the same jurisdiction, the Government chose a cash capital grant or a public-works concession where station-area development rights were not suitable (S-fund-219).

**Evidence grade.** A– for the mechanism and the 2024 financials (government reply and company results, both verified). The 2018 profit share is secondary. Line-level outturn against the 2011 gap estimates is not covered.

### 3. France: SNCF Réseau and LGV concessions (SEA Tours–Bordeaux, LISEA)

**Structure.** France separates infrastructure from operations: SNCF Réseau (formerly RFF) is the infrastructure manager and train operators pay track-access tolls. The LGV Sud-Europe-Atlantique (SEA) is a 302 km new line between Tours and Bordeaux. In 2011 it was awarded as a concession to LISEA, a Vinci-led group, covering financing, design, construction, maintenance and renewal. In return, LISEA has the right to collect the track-access tolls on the line until 2061 (S-fund-222). The line opened in July 2017 and cut Paris–Bordeaux journeys by 51 minutes, with direct TGVs taking 2h03 (S-fund-222).

**Who paid (capex sources).**
- Total initial investment was EUR 8,176 M (2017 prices), or EUR 9.4 bn (2023 prices). This is EUR 7,151 M for the concession plus EUR 1,025 M of accompanying works by RFF (S-fund-224).
- The grantor contributed EUR 3.9 bn (2017 prices), which was 48% of the financing. Within that, the State subsidy was EUR 1.6 bn and local-authority subsidies EUR 1.2 bn, a cumulative subsidy of EUR 2.8 bn or 38%. IGEDD calls this significantly lower than for other high-speed lines (LGVs) of the period (S-fund-223).
- Private side, at 31 Dec 2017: equity of EUR 773 M (20%), of which a shareholder subordinated loan of EUR 765 M, and bank borrowings of EUR 3,029 M (80%) (S-fund-227). The State guaranteed 73% (EUR 2,217 M) of the senior debt. Lenders included the Caisse des dépôts (CDC) and the European Investment Bank (EIB), part guaranteed and part at project risk (S-fund-227).
- Equity holders: in 2018, Vinci Concessions 33%, CDC 25% and Meridiam 24%. In 2024, Vinci and Meridiam held 42% each and CDC 16% (S-fund-228).

**Who carried demand risk.** Mainly the concessionaire. LISEA carries cost-deviation risk, including maintenance and renewal until 2061. It also carries traffic risk "largely", especially in the first five years. From year five, a "redevance de bonne fortune" (contract Art. 26.2) shares revenue above forecast with the grantor (S-fund-226). LISEA also carried interest-rate risk on the unguaranteed debt and the design-build risks, including land release, works, interfaces and schedule (S-fund-226). A large share of the debt was nevertheless State-guaranteed until the refinancing (S-fund-227), so the State kept part of the credit risk.

**What happened.**
- *Cost.* The estimate rose from EUR 4,970 M (2004 prices) at the 2005 public inquiry to EUR 7,446 M (2017 prices) at the 2011 contract (S-fund-225), and the outturn total was EUR 8,176 M (2017 prices) (S-fund-224). IGEDD finds that the concession protected taxpayers from budget overruns and that risk transfer contributed to on-time delivery. It also finds that competitive tendering did not reduce the record per-km cost (S-fund-232).
- *Demand.* The public-inquiry forecasts were 19.4–20.6 million passengers a year on the SEA axis. SNCF Voyageurs carried 18.6 million in 2019. IGEDD attributes the overestimate mainly to overestimated diversion from air (S-fund-229).
- *Appraisal.* The socio-economic internal rate of return (IRR) was revised from 8% ex ante to 6% ex post, subject to traffic data and studies still to be redone (S-fund-230).
- *Refinancing.* In December 2018 LISEA refinanced EUR 2.2 bn of its 2011 bank debt. The new package is a EUR 1.3 bn loan over 27 years plus EUR 905 M of fixed-rate green-bond tranches over 30 and 35 years (S-fund-233).
- *Accounting.* The concession was described as deconsolidating for Maastricht debt as long as the concessionaire's revenues are mainly commercial (S-fund-231).
- *Network level.* The State took over EUR 35 bn of SNCF Réseau debt (S-fund-234). The reported 2020/2022 split of EUR 25 bn and EUR 10 bn is unverified (S-fund-235).
- LISEA's toll-revenue outturn against its base case: no reliable data found in the sources read.

**Lessons as evidence.**
- A demand-risk concession can deliver on time and cap the public budget commitment (S-fund-232). Even so, the State guaranteed 73% of the senior debt during construction (S-fund-227), so the risk transfer was partial on the financing side.
- Traffic forecasts on a line competing with air were optimistic (S-fund-229). The resulting revenue risk sits with the private party.
- Tendering did not lower unit construction cost on this line (S-fund-232).
- A concession can keep most of a line's cost off Maastricht debt. Network-wide, the infrastructure manager's debt still needed a large State takeover (S-fund-231, S-fund-234).

**Evidence grade.** A for LGV SEA: an independent ex-post review by the State's inspectorate (IGEDD, Sept 2025) plus the concessionaire shareholder's press release, both verified. B for the SNCF Réseau debt: only the total is verified. The Cour des comptes 2014 LGV report was not retrieved (the download failed), so it is not used.

### 4. Spain: ADIF / AVE (EU funds, AIReF ex-post CBA, CNMC liberalisation, ADIF debt)

**Structure.** The network is publicly built and owned and vertically separated. ADIF and ADIF Alta Velocidad (ADIF AV) are public business entities that own and manage the infrastructure, and operators pay track-access charges (S-fund-237, S-fund-244). Spain's high-speed rail (HSR) network was 3,086 km, the second longest in the world after China, with the lowest intensity of use among countries that have a significant HSR network (S-fund-236). Since January 2025, three operators run on the main HSR corridors: Renfe (AVE and AVLO), Ouigo and Iryo (S-fund-244).

**Who paid (capex sources).**
- More than EUR 55,888 M (2018 prices) was invested in HSR (S-fund-237):
  - EU funds paid EUR 14,086 M (25.2%).
  - Another EUR 15,858 M became debt of ADIF AV, whose deficit and debt do not count in the national accounts.
  - The remainder, by implication, came from the State budget and other public sources. AIReF's executive summary does not break this down.
- EU cohesion and ERDF funds for all Spanish transport infrastructure in 2000–2020 totalled EUR 57,641 M, which is 22% of that investment (S-fund-245).
- Average construction cost was EUR 14.7 M per km, or EUR 15.3 M per km including stations (S-fund-238).

**Who carried demand risk.** The public sector. Infrastructure costs are not recovered from users: AIReF finds that operation is profitable "without recovering the investment" (S-fund-242). Since liberalisation, train operators carry their own commercial risk. They moved from a combined EUR 133 M profit in 2019 to a EUR 99.5 M loss in 2024 (S-fund-244).

**What happened.**
- *Ex-post CBA (AIReF, 2020).* Socio-economic returns are "between nil and minimal" on all corridors, and social benefits do not cover the fixed construction costs. The North-East and South corridors are close to the minimum required return. The North and Levante corridors are notably worse because their demand is much lower (S-fund-239).
- *Usage and comparison with commuter rail.* HSR carried 30 million passengers in 2018, 4.8% of rail passengers, against 562.2 million on Cercanías. Cercanías received only EUR 3,600 M of investment over 1990–2018 (S-fund-241).
- *Remaining plan.* Completing the planned 8,740 km network (PITVI) would need at least EUR 73,000 M more (S-fund-240).
- *Liberalisation (CNMC, 2024 balance).*
  - Rail passengers reached 49 million, +42% against 2019.
  - HSR fares fell 33% on average, or 44% after inflation.
  - 4.8 million passengers shifted from air and road.
  - The net social benefit was EUR 503.9 M.
  - ADIF gained EUR 133.3 M net from higher access charges, while operators moved into losses and Renfe's share fell to 72% (S-fund-243, S-fund-244).
- *Current ADIF / ADIF AV debt stock.* No reliable data found in the sources read. The EUR 15,858 M figure is AIReF's 2018-price figure for the HSR debt (S-fund-237). ADIF annual accounts were not read.

**Lessons as evidence.**
- Large EU grants and an off-balance-sheet public entity made a long network fundable. AIReF's ex-post CBA nevertheless finds low returns where demand is thin (S-fund-237, S-fund-239).
- Opening an already built network to competing operators raised ridership and cut fares. The gains went to users and the infrastructure manager, while operators made losses in 2024 (S-fund-243, S-fund-244).
- Spending concentrated on HSR coincided with low investment in high-volume commuter rail (S-fund-241).

**Evidence grade.** A: the national fiscal council's ex-post review and the competition authority's balance, both verified on the publishers' sites. The current ADIF debt figure is a gap.

### 5. China: China Railway (CR/CRC, now China State Railway Group) and local-government JV financing

**Structure.** Since 2004, most major HSR projects have used the equity model, also called the "railway and local government cooperation" model (S-fund-247). Under it, a joint-venture (JV) company is formed between the central government, represented by China Railway Corporation (CRC), and the provincial government. Provinces often hold their stake through provincial railway investment companies (S-fund-246). Some JVs bring in minority third parties, for example Ping An Insurance in the Beijing–Shanghai HSR company (S-fund-247). Most JVs, apart from a few such as the Beijing–Shanghai company, are infrastructure-financing and contract-managing companies paid through access charges, "analogous to tolled expressway companies" (S-fund-253). Some later lines used PPP or private capital. Jinan–Qingdao was the first HSR line based on local-government capital, and Hangzhou–Taizhou the first financed more than 51% by private capital (S-fund-252).

**Who paid (capex sources).**
- *Financing structure.* JVs are typically 50% equity and 50% debt. Provinces often contribute their equity as land (S-fund-246). The debt comes mainly from domestic development banks such as China Development Bank, with very little from international banks (S-fund-247).
- *Total investment.* About CNY 2.5 trillion (US$370 bn, nominal) was invested from 2005 in the HSR network in service at end-2015 (S-fund-248). It was financed by:
  - equity from MOR/CRC and local governments;
  - JV bank loans;
  - the central budget;
  - construction bonds.

  Local governments also contributed land acquisition and resettlement, materials support and local tax relief (S-fund-248).
- *Unit cost.* Average construction cost was about CNY 139 M/km for 350 kph lines, CNY 114 M/km for 250 kph and CNY 104 M/km for 200 kph. That is at least 40% below European costs (S-fund-251).
- *Beijing–Shanghai SPV.* Equity and total cost figures (S-fund-254) are unverified and carry no figure here.

**Who carried demand risk.** Mostly the public sector through CRC's balance sheet. CRC finances its equity from its own balance sheet, which carried some CNY 4 trillion of long-term debt (S-fund-249). On weaker lines, the shareholding railway administrations absorb the infrastructure maintenance costs from their other operations (S-fund-252). Provincial governments carry risk through their equity and land contributions (S-fund-246).

**What happened.**
- *Financial viability depends on density.* Busy 350 kph lines, above 40 million passengers a year at about CNY 0.50 per passenger-km (pkm), cover operations, maintenance and debt service. Many lines with 10–15 million passengers a year, especially 250 kph lines at about CNY 0.28/pkm, barely cover operations and maintenance and cannot contribute to debt service for many years (S-fund-250). Only rarely do such lines cover even part of their debt service (S-fund-252).
- *Current figures not verified.* China State Railway Group's 2025 revenue, profit and debt ratio (S-fund-255) and the Beijing–Shanghai company's 2023 results (S-fund-256) are unverified leads. Neither carries a figure here.
- *World Bank options for weak lines.* The report discusses debt reprofiling, grouping lines, and station-area land development as remedies (World Bank 2019, ch.6; same source as S-fund-249). These are presented as the World Bank's options, not as outcomes.

**Lessons as evidence.**
- Co-investment by provinces, mainly as land, combined with state-bank debt delivered a very large network quickly at low unit cost (S-fund-246, S-fund-248, S-fund-251).
- Financial self-sufficiency depends on traffic density. Below roughly 40 million passengers a year, debt service falls back on the national railway's balance sheet (S-fund-249, S-fund-250, S-fund-252).

**Evidence grade.** A– for the mechanism and line economics (World Bank 2019, verified). C for current corporate financials (unverified). Not covered: a primary source for CSRG debt, the Beijing–Shanghai prospectus, and outturns of local-government PPP lines.

### 6. Morocco: Al Boraq (LGV Tanger–Kénitra) financing

**Structure.** The line is fully public and integrated. The State railway ONCF is the developer, infrastructure owner and operator. The project combines a new high-speed section of about 180 km between Tanger and Kénitra, where trains run at 320 km/h, with upgraded conventional track onward to Casablanca, where they run at 160 km/h. The whole route is about 350 km, and Casablanca–Tanger takes 2 hours instead of 5 (S-fund-258, secondary). It was inaugurated in November 2018 (S-fund-257, secondary).

**Who paid (capex sources).**
- Reported total cost: about MAD 23 bn (about EUR 2 bn, nominal), about 15% above the initial estimates (S-fund-257, secondary).
- Financing shares (S-fund-257, secondary):

| funder | share of financing |
|---|---|
| France, through various loans | 51% |
| Moroccan State | 28% |
| Arab funds (Saudi Arabia, Kuwait, UAE and others) | 21% |

- A more detailed split, totalling MAD 22.9 bn with the State/Fonds Hassan II, a French grant, French Treasury and AFD loans, and Saudi and Kuwaiti fund loans, is reported in the press but unverified (S-fund-259). It carries no figure here.
- The primary financing documents (ONCF, the Moroccan Ministry of Finance, the French Treasury, AFD and the Saudi Fund for Development) were not read: no reliable primary data found in this pass.

**Who carried demand risk.** ONCF and, through it, the Moroccan State. No private concession or demand-risk transfer was found in the sources read. The lenders are sovereign and development financiers, on concessional terms per the press (secondary), so the repayment obligation is public.

**What happened.**
- *Delay.* Delivery was originally planned for 2015 and slipped to 2018, attributed to expropriation and the complexity of the Franco-Moroccan partnership (S-fund-258, secondary).
- *Ridership.* ONCF expected 6 million passengers a year after three years (S-fund-258, secondary). Press reports 2024 ridership of over 5.5 million and revenue of MAD 780 M, but this is unverified (S-fund-260).
- An extension (Kénitra–Marrakech) is reported in the press, but its financing was not found: no reliable data found.

**Lessons as evidence.**
- A first HSR line in a middle-income country was financed mainly with bilateral export and development loans plus Gulf fund loans, with the State contributing just over a quarter (S-fund-257, secondary).
- Land expropriation was named as a cause of the three-year delay (S-fund-258, secondary).

**Evidence grade.** C. All figures are from Moroccan financial press. The primary sources (ONCF, ministries, lenders) remain to be found. Status: secondary or unverified.

### 7. Saudi Arabia: Haramain High Speed Railway contracts and consortium history

**Structure.** The line was publicly procured and is publicly owned, with design-build packages followed by an operations-and-maintenance (O&M) contract with a private and state-owned foreign consortium. The client was the Saudi Railways Organization (S-fund-261). The current contracting party is Saudi Arabia Railways (SAR) (S-fund-263). Two phases were procured:
- **Phase 1, civil works and stations.** Civil works Package 1 went to the Al Rajhi Alliance in February 2009: Mada Group, Bouygues, Al Arrab Contracting, Arup and China Railway Engineering Corp, for SAR 6.79 bn. Station contracts went out in February 2011: Saudi Bin Laden Group for Madinah (SAR 3.18 bn) and Makkah (SAR 1.56 bn), and Saudi Oger for Jeddah (SAR 2.9 bn) and KAEC (SAR 1.75 bn). Foster + Partners and Buro Happold did the station design. All values are nominal (S-fund-262, secondary).
- **Phase 2, systems, rolling stock and O&M.** On 26 Oct 2011 the AlShoula Consortium won a EUR 6.74 bn (nominal) contract. The consortium had two Saudi members (AlShoula, Al Rosan) and twelve Spanish ones, including ADIF, RENFE, Talgo, OHL, Indra, Ineco and Cobra. The scope was track, electrification, signalling and telecoms, 35 Talgo 350 trainsets with an option for 23 more, three years of construction and then 12 years of O&M on 444 km of double track (S-fund-261, secondary).

**Who paid (capex sources).** The Saudi State, through the then Saudi Railways Organization (S-fund-261, S-fund-262). The total contract value is reported at about US$9.4 bn (nominal) (S-fund-265, secondary). No private financing, project-finance debt or PPP structure was found in the sources read. The budget lines that funded the project and the final outturn cost: no reliable data found.

**Who carried demand risk.** The public owner. The Phase 2 contract is an EPC-plus-O&M service contract, not a concession, so ridership risk stays with the State (S-fund-261). How the O&M contractor is paid (fixed fee, availability or performance regime, any revenue share): unclear. The contract terms are not public; question: does any part of Renfe's remuneration depend on ridership or fares?

**What happened.**
- *Schedule.* Completion was originally slated for 2012. The line was inaugurated on 25 Sep 2018 and opened to the public on 11 Oct 2018 (S-fund-265, secondary).
- *Disruption.* The Jeddah Sulaymaniyah station was destroyed by fire on 29 Sep 2019 and resumed operation on 13 Jul 2021. Services were suspended for COVID from 20 Mar 2020 and resumed on 31 Mar 2021 (S-fund-265, secondary).
- *Ridership.* 6.97 million in 2023, against a design projection of 60 million a year (S-fund-265, secondary; primary to find).
- *Contract extension.* In February 2026 O&M by the Spanish consortium, with RENFE as operating partner, was extended to 2038 and described as EUR 2.8 bn across the consortium. SAR also ordered 20 new Talgo trainsets, adding EUR 1.3 bn to Talgo's order book, and extended Indra's systems O&M by at least five years for about EUR 130 M (S-fund-263, secondary). A EUR 1.5 bn value for Renfe's 2033–2038 extension is unverified (S-fund-264).
- *Disputes.* A settlement between Saudi Arabia and the contractor is reported (S-fund-266), but its terms are unverified. Cost overruns and claims by the consortium: no reliable data found in the sources read.
- *Institutions.* The 2021 merger of the Saudi Railways Organization with SAR is a lead from another track (see RESUME_LEADS) and is not sourced here.

**Lessons as evidence.**
- The Kingdom's only HSR was delivered with the State carrying cost and demand risk. Civil works and systems were split across separate contracts, and the schedule slipped about six years against the original 2012 target (S-fund-261, S-fund-262, S-fund-265).
- Operating capability was bought in through a long O&M contract with a foreign state operator and then extended (S-fund-261, S-fund-263).
- Reported 2023 ridership is about an eighth of the design projection (S-fund-265, secondary). This is the most relevant domestic evidence for demand-risk allocation, but it needs a primary source before any modelling use.

**Evidence grade.** C+. Contract scope and values come from trade press (Railway Gazette, secondary). Timeline and ridership come from Wikipedia citing press. No SAR, MoF or contractor primary filing was read. Gaps: total outturn cost, the O&M payment mechanism, the dispute settlement terms, and annual ridership from SAR or GASTAT.

### Comparison table

| case | delivery model | who paid (capex) | demand risk | outcome (evidence) | sources |
|---|---|---|---|---|---|
| Japan: JNR break-up, JR East, Tokyu | Privatised vertically integrated regional companies; legacy debt moved to a public settlement body; private railway with line-side real estate | State absorbed most legacy debt (JPY 25.5 trn of 37.1 trn, 1987); JR companies took JPY 11.6 trn (14.5 trn in practice); Tokyu self-financed property-led lines | Operators (commercial); legacy-debt shortfall on the State | Land and share sales covered part of the transferred debt; property is about 29% of Tokyu's profits (2019, secondary); JR East daily passengers fell from about 17.8 M to 12.4 M (2020–21) | S-fund-200 to S-fund-210 |
| Hong Kong: MTR R+P | Integrated owner-operator; government grants station-area development rights in place of cash | MTRCL funds construction; Government contributes development-rights value (e.g. SIL(E) gap HKD 9.9 bn); some lines by capital grant (WIL HKD 12.7 bn) or public-works concession | MTRCL (ridership plus property market, over a ten-plus-year lag) | 2024 net profit HKD 15,772 M, of which HK property development HKD 10,235 M; recurrent HKD 7,210 M | S-fund-211 to S-fund-221 |
| France: LGV SEA / LISEA | 50-year DBFM demand-risk concession (to 2061) in a vertically separated system | Grantor contribution EUR 3.9 bn (2017 prices, 48%); LISEA equity EUR 773 M plus debt EUR 3,029 M, 73% State-guaranteed; total EUR 8,176 M (2017 prices) | Concessionaire, largely (revenue sharing above forecast from year 5) | On time and within the public budget commitment; record per-km cost; 2019 traffic 18.6 M vs 19.4–20.6 M forecast; socio-economic IRR 6% vs 8% ex ante; 2018 refinancing | S-fund-222 to S-fund-235 |
| Spain: ADIF / AVE | Public build and ownership through an off-balance-sheet infrastructure entity; operators opened to competition | EUR 55,888 M (2018 prices): EU funds 25.2%, ADIF AV debt EUR 15,858 M, the rest public | Public (investment not recovered); operators carry commercial risk since liberalisation | Ex-post CBA returns nil to minimal; liberalisation: fares −33%, passengers +42%, operators lost EUR 99.5 M in 2024 | S-fund-236 to S-fund-245 |
| China: CR / CRC JV model | Central–provincial JVs (equity model), mostly access-charge infrastructure companies; some PPP or private lines | About CNY 2.5 trn (2005–15): CRC and provincial equity (land in kind), development-bank loans, budget, bonds; CRC long-term debt about CNY 4 trn | Public (CRC balance sheet, provinces) | Busy lines (>40 M passengers/yr) cover debt service; 10–15 M lines barely cover O&M | S-fund-246 to S-fund-256 |
| Morocco: Al Boraq | Fully public, integrated (ONCF) | About MAD 23 bn: France loans 51%, State 28%, Arab funds 21% (secondary) | ONCF / State | About 15% over initial estimates; three years late (2015 → 2018); 2024 ridership over 5.5 M (unverified) | S-fund-257 to S-fund-260 |
| Saudi Arabia: Haramain | Public design-build packages plus an EPC + O&M service contract (AlShoula consortium), O&M extended to 2038 | Saudi State: Phase 1 civil works SAR 6.79 bn plus stations; Phase 2 EUR 6.74 bn; total about US$9.4 bn (secondary) | Public | About six years late (2012 → 2018); 2023 ridership 6.97 M vs a 60 M design projection (secondary); O&M extended in 2026 | S-fund-261 to S-fund-266 |

All figures are nominal unless a price year is stated. The rows summarise the case sections above, and each figure carries the S-id given there.


## Saudi legal and institutional frame

Every statement below cites the instrument read and its status. Translations of Saudi laws are guidance; the Arabic text governs (the Railway Law translation says so explicitly, S-fund-012).

### Private Sector Participation (PSP) Law, Royal Decree M/63 (2021), and its Implementing Regulations

- **Definition of PPP.** A contract of 5 years or more in which the private party carries out two or more of design, build, manage, operate, maintain or finance; risks are allocated and the consideration is performance-based (Art. 1; S-fund-001, verified).
- **Scope.** Applies to ministries, government agencies and companies more than 50% government-owned set up to execute a PSP project (Art. 4; S-fund-010).
- **Term.** Up to 30 years including extensions, unless the relevant agency approves longer on the executive agency's recommendation (Art. 20; S-fund-002).
- **NCP referral.** Projects above a Council of Ministers value limit, or with a term of 5 years or more, are referred by the Ministry of Finance to the NCP for a preliminary privatisation-viability study within 60 business days (Art. 7; S-fund-003).
- **Ministry of Finance.** Ensures funds before tendering, secures allocations for government obligations on their due dates, approves additional obligations from amendment, suspension, extension or termination, and approves financial and credit support (Art. 8; S-fund-004). Support not stipulated in the contract needs a Council of Ministers resolution (Art. 10; S-fund-005).
- **Permits.** If a government agency fails to issue or delays a permit, CEDA instructs it on the executive agency's report, without prejudice to contractual risk allocation (Art. 11; S-fund-006).
- **Termination.** Unilateral termination for breach, bankruptcy, public interest or contract cases; the contract may define compensation, including lost revenues where there is no private-party breach (Art. 28; S-fund-007).
- **Disputes.** Arbitration and governing law may be agreed with the relevant agency's approval (Art. 34; S-fund-008). Unsolicited proposals are governed by the Implementing Regulations (Art. 41; S-fund-009).
- **Governance.** The Council of Ministers issues governing rules naming the relevant and executive agencies per project type (Art. 2); the NCP Board issues the Implementing Regulations and template contracts (Art. 44; S-fund-010). The law entered into force 120 days after publication (Art. 45; S-fund-011).
- **Implementing Regulations.** As amended by the NCP Board on 31 Dec 2023 and published 2 Feb 2024: minimum PPP value SAR 200 m measured over the project period, minimum SAR 50 m for asset-ownership transfer (S-fund-041, secondary). The 2022 text, per a law-firm summary, required a business case analysing affordability, value for money and contracting options, and allowed four procurement methods including unsolicited proposals (S-fund-053, secondary). The regulations' own text was not read (S-fund-042, unverified).

### NCP role and published guidance

- The National Privatization Strategy 2025 (NCP) sets 2030 ambitions of USD 64 bn private capital investment and USD 11.5 bn value for money from PPP transactions (S-fund-030); targets 18 sectors including public transport, with identified projects of USD 64 bn capex and USD 7.2 bn net government revenue (S-fund-031); reports about 90 contracts signed with total investment above USD 50 bn by end-2025 (S-fund-032). The document names no rail project.
- No NCP-published PPP manual, value-for-money method or standard rail contract was found in this pass (S-fund-056, unverified).

### Public Investment Fund (PIF)

- PIF Law issued by Royal Decree M/92 dated 12/8/1440H, in force 3 May 2019; objective (Art. 3, as quoted by a newspaper column) to invest its funds per best standards for returns serving the public interest; powers include establishing companies and special-purpose entities inside and outside the Kingdom; organisationally linked to CEDA (S-fund-036, secondary). Saudipedia states the board is chaired by the Crown Prince and Prime Minister (S-fund-038, secondary). The official PIF Law PDF returned HTTP 403 (S-fund-037, unverified).
- Role in rail as reported: PIF was assigned to finance the Landbridge in 2009 and took control in October 2011, appointing SAR (S-lb-012, MEED, secondary); MEED in 2023 described PIF as a fallback financier during the consortium talks (S-lb-009, secondary). Saudipedia states SAR is fully owned by PIF (S-fund-035, secondary).

### Saudi Arabia Railways (SAR)

- SAR's own history: established 2006; a Council of Ministers resolution of 16 Feb 2021 abolished the Saudi Railways Organization and assigned SAR its responsibilities from 1 Apr 2021; a 2016 decision that SAR owns intercity rail infrastructure and a 2019 decision that it owns all operational railway transport projects (S-fund-033, verified).
- Ownership and corporate form: SAR's site does not state its shareholder or legal form (S-fund-034); Saudipedia says fully owned by PIF (S-fund-035, secondary).
- Haramain operation: Renfe runs trains on behalf of SAR, extended to 2038 (S-fund-039, secondary); a reported EUR 1.5 bn value for 2033-2038 is unverified (S-fund-040).

### Transport General Authority (TGA) and the Railway Law, Royal Decree M/159 (2024)

- TGA is "the Authority" under the law; a concessionaire is a legal person entrusted by law to construct railways or provide railway services (Art. 1; S-fund-012, verified).
- Concession contracts are tendered upon TGA's approval, in accordance with relevant laws (Art. 32; S-fund-013). TGA may allow a concessionaire to use railway land and protection zones; the Regulations specify when existing assets may be transferred to a concessionaire (Art. 33; S-fund-014).
- Access: infrastructure managers grant usage rights on fair, transparent, non-discriminatory terms; TGA may restrict them without prejudice to economic benefits guaranteed under a concession (Art. 14; S-fund-015). TGA sets the usage-fee policy, approves use agreements and decides access disputes (Arts. 16-18; S-fund-016).
- Implementing Regulation: reported as approved by TGA Board resolution 4/2024/1/1 (19/12/1445H) (S-fund-054, unverified); text not read.

### Landbridge PPP history (sources secondary unless stated)

- 2007-2008: four prequalified consortiums bid for a BOT (S-lb-013); a preferred bidder named in April 2008 for a 50-year concession did not reach financial close (S-lb-017, Wikipedia).
- 2009-2011: the BOT was retendered; PIF assigned to finance (2009); the 2008 tender declared void; PIF took control in October 2011 and appointed SAR (S-lb-012).
- 2018-2023: SAR-CCECC memorandum reported in 2018 (S-lb-010); in January 2023 MEED reported the minister negotiating final cost and financing with an 11-company Chinese-led consortium (S-lb-009).
- 2026: MEED reports the PPP talks with the Chinese consortium did not succeed and the scheme "will now be delivered in several phases through a different procurement model", targeting 2034 (S-059); an Arabic report of a January 2026 TV interview with SAR's CEO is headlined that the Chinese alliance did not commit to local content, which stopped its continuation (S-lb-001). SAR tendered the 35 km Riyadh section (S-060). The ENR 2026 article returned HTTP 403 and is unverified (S-049).
- No official SAR, MoTLS or SPA statement on why the PPP talks ended was found; the reason above is as reported in the press.

### Published Saudi appraisal, budget and infrastructure-finance guidance

- FY2026 pre-budget statement (MoF): total expenditure SAR 1,313 bn budgeted for 2026, 1,350 bn (2027) and 1,419 bn (2028) estimated (S-fund-026); intention to expand alternative government financing through project finance, infrastructure finance and export credit agencies (S-fund-027); National Infrastructure Fund direct commitments of about SAR 8.6 bn (SAR 6.3 bn disbursed) on projects worth SAR 46.4 bn since 2022 (S-fund-028). No PPP commitment or contingent-liability table appears in the document (S-fund-029).
- No published Saudi appraisal manual (discount rate, VfM or PSC method) was found; the project's appraisal standard is set by the CP1 decisions recorded in `docs/STATUS.md`, with the UK Green Book PSC logic used here as the named reference (S-fund-024, S-fund-025).

### Saudi-frame items

| item | status | finding | precise open question | sources |
|---|---|---|---|---|
| PSP Law M/63: PPP definition, 30-year term, MoF duties, termination, arbitration | clear | Articles 1, 4, 7, 8, 10, 11, 20, 28, 34, 41, 44 read in the MISA English translation | Does the Arabic text differ from the translation on any of these articles? | S-fund-001, S-fund-002, S-fund-003, S-fund-004, S-fund-005, S-fund-006, S-fund-007, S-fund-008, S-fund-009, S-fund-010, S-fund-011 |
| PSP Implementing Regulations: thresholds and procedures | unclear | SAR 200 m PPP / SAR 50 m divestment thresholds and four procurement methods reported by secondary sources | What do the amended (2023/2024) Implementing Regulations say on procurement methods, unsolicited proposals, VfM study content and MoF fiscal approval? | S-fund-041, S-fund-053, S-fund-042 |
| Which agency is the "relevant agency" and "executive agency" for a rail PPP | unclear | Art. 2 leaves this to Council of Ministers governing rules; not read | For an intercity rail PPP, is the relevant agency MoTLS, TGA, SAR's board or another body, and is SAR (a state company) a contracting authority under Art. 4? | S-fund-010 |
| Council of Ministers value limit for NCP referral (Art. 7) | unclear | Limit set by Council of Ministers; value not found | What is the current Art. 7 referral threshold, and does it differ from the SAR 200 m PPP threshold? | S-fund-003 |
| NCP published PPP guidance (manuals, VfM, standard contracts) | unclear | National Privatization Strategy read; no manual found | Has NCP published PPP guidelines, a VfM/PSC method or standard contracts under Art. 44, and do they cover rail? | S-fund-030, S-fund-031, S-fund-032, S-fund-056 |
| PIF Law M/92: mandate and powers | unclear | Decree, objective and powers known only from a newspaper column and Saudipedia | What do Arts. 3-4 of the official PIF Law text say on investing in domestic infrastructure and on guarantees? | S-fund-036, S-fund-037, S-fund-038 |
| PIF's role in rail today | unclear | Historical role reported by MEED (2009-2011 finance and control; 2023 fallback) | Does PIF currently finance SAR's capex (equity, loans or guarantees), and is SAR in PIF's published portfolio? | S-lb-012, S-lb-009, S-fund-035 |
| SAR mandate (succession to SRO, 2021) | clear | SAR took over SRO's responsibilities from 1 Apr 2021 (SAR's own site) | none for the fact; the resolution text itself not read | S-fund-033 |
| SAR ownership and corporate form | unclear | SAR's site silent; Saudipedia says fully owned by PIF | Who are SAR's shareholders per its commercial registration or articles, and what is its legal form (joint stock or limited liability)? | S-fund-034, S-fund-035 |
| Fiscal reporting of SAR- or PIF-financed rail | unclear | Not stated in the FY2026 pre-budget statement | Are SAR's capex and debt consolidated in general-government statistics or the budget, and are any PPP payment commitments or guarantees disclosed? | S-fund-029, S-fund-026 |
| Railway Law M/159: TGA concession regime and access | clear | Arts. 1, 14, 16-18, 32, 33 read | none for the articles read | S-fund-012, S-fund-013, S-fund-014, S-fund-015, S-fund-016 |
| Railway Law Implementing Regulation (concession, asset-transfer and access-charge rules) | unclear | Board approval reported (1445H); text not read | Which cases allow transfer of existing assets to a concessionaire (Art. 33), and has TGA published a usage-fee (access-charge) policy under Art. 18? | S-fund-054, S-fund-055 |
| How PSP Law and Railway Law interact for a rail concession | unclear | Railway Law Art. 32 says "in accordance with relevant laws" | Does a rail concession tendered under Railway Law Art. 32 also follow PSP Law procedures (NCP study, MoF approval)? | S-fund-013, S-fund-003 |
| Multi-year O&M contracts under the PSP Law | unclear | An operate-and-maintain contract of 5+ years covers two of the six functions in the Art. 1 PPP definition | Are O&M-only rail contracts (such as Haramain's) treated as PPPs under the PSP Law, with NCP and MoF steps, or as ordinary government procurement? | S-fund-001, S-fund-039 |
| Haramain operating arrangements | unclear | Renfe operates for SAR to 2038 (press) | What is the contract form (O&M fee vs revenue share), value and risk allocation of the extended Haramain operating contract? | S-fund-039, S-fund-040, S-011 |
| Landbridge PPP talks and phased delivery | unclear | Talks ended; phased SAR delivery reported by MEED and Arabic press | Is there an official statement of why the PPP talks ended and of the procurement model for the phases? | S-059, S-lb-001, S-lb-009, S-060, S-049 |
| Saudi instruments for land value capture (development rights, levies, tax increment) | unclear | Not reviewed in this pass | Which Saudi instruments (for example municipal fees or the white-land fee) could legally be earmarked for rail, and can railway land under Railway Law Art. 33 be developed commercially? | S-fund-014 |
| National Infrastructure Fund role | unclear | Commitments SAR 8.6 bn on SAR 46.4 bn of projects (MoF) | Does the National Infrastructure Fund finance transport or rail projects, and on what terms? | S-fund-028 |
| Saudi appraisal guidance (discount rate, VfM, PSC) | unclear | None found published | Has MoF or NCP published a project-appraisal or PSC methodology? | S-fund-029, S-fund-056 |

## Risk-allocation matrix template

Template from `cities/ksa/funding/risk_matrix_template.yaml` (allocation cells deliberately empty; R7 fills one per corridor family and delivery model). Output of `uv run python -m funding.risk_matrix render`:

| risk | scope | public | private | shared | mechanism (options) | precedents |
|---|---|---|---|---|---|---|
| construction | cost overrun, schedule delay, geotechnical and ground conditions, sand and heat design, interfaces between civil, systems and rolling-stock packages |  |  |  | fixed-price design-and-build or DBFM/DBFOM with payment only from availability (private); target-cost or cost-sharing band with pain/gain share (shared); compensation event for unforeseen ground conditions above a defined baseline (shared); state-delivered works with optimism-bias contingency (public) | S-fund-046, S-fund-047, S-fund-043, S-fund-025 |
| demand | ridership and freight volume versus forecast; ramp-up; competing modes |  |  |  | availability payment, state keeps fare revenue (public); full demand risk to concessionaire via fares or access charges (private); minimum revenue guarantee and/or revenue sharing above a cap (cap-and-collar) (shared); revenue-sharing 'bonne fortune' clause above forecast (shared) | S-fund-045, S-fund-046, S-fund-023 |
| revenue | fare level and indexation, fare-setting authority, ancillary and non-fare revenue (retail, property), collection and leakage |  |  |  | state sets and keeps fares; operator paid a fee (public); concessionaire sets fares within a regulated cap (private); access-charge regime set by the regulator, collected by the infrastructure manager (shared); station-area development rights or levy income ring-fenced to the project (shared) | S-fund-016, S-fund-048, S-fund-049 |
| operations | operations and maintenance cost, availability and punctuality performance, asset condition at hand-back, lifecycle renewal |  |  |  | performance-based O&M contract with deductions (private); availability deductions and hand-back condition requirements in a DBFM/DBFOM (private); in-house operation by the state company (public) | S-fund-039, S-fund-044, S-fund-043 |
| financing | interest-rate and refinancing risk, availability of long-tenor debt, FX exposure on imported systems and foreign lenders, financial close |  |  |  | sovereign or PIF financing (public); project-finance debt raised by the SPV, rate fixed or hedged at financial close (private); refinancing-gain sharing clause (shared); MoF financial and credit support under PSP Law Arts. 8 and 10 (shared) | S-fund-004, S-fund-005, S-fund-027, S-lb-012 |
| land | land acquisition and expropriation, right-of-way, utilities relocation, protection zones, heritage and route-sensitivity constraints |  |  |  | state delivers land and utilities free of encumbrances before works (public); concessionaire acquires land within a capped budget (shared); compensation event for late land delivery (public) | S-fund-014, S-fund-006 |
| regulatory_force_majeure | change in law, permits, political decisions, termination for public interest, force majeure, disputes |  |  |  | change-in-law and public-interest termination compensation (public); force majeure relief with shared cost after a threshold (shared); arbitration with agreed governing law, subject to agency approval (shared) | S-fund-007, S-fund-008, S-fund-006 |

## Fiscal-exposure metric definitions (for R7)

All metrics are computed from W3 cost and W4 demand distributions and reported as ranges (P10/P50/P90), never points (rule 3). Inputs that are not sourced become assumptions in `docs/assumptions.md` (A-fund ids).

| metric id | definition | formula | unit | sources |
|---|---|---|---|---|
| `upfront_public_capex` | Public capital spending before and during construction (grants, contributions, state-delivered works), by year and PV | sum_t public_share_t x capex_t; PV with discount rate r | SAR bn real (stated price year) and PV | S-fund-021, S-fund-026 |
| `availability_payments_share_of_budget` | Annual availability or subsidy payments as a share of a stated budget line (total state expenditure from the MoF budget statement unless a narrower line is sourced) | AP_t / E_t; E_t from the FY2026 pre-budget statement for 2024-2028, then an A-fund growth assumption | % per year; peak and average | S-fund-026, S-fund-023, S-fund-004 |
| `contingent_liabilities` | Expected and worst-case value of guarantees, MRGs, termination compensation (incl. lost revenues, PSP Law Art. 28) and compensation events | EV = sum_k p_k L_k (Monte Carlo over W3/W4 draws); MRG_t = max(0, G_t - R_t) | SAR bn PV (expected, P90, worst case) | S-fund-021, S-fund-023, S-fund-007 |
| `net_fiscal_cost_horizon` | Net present fiscal cost over 30, 40 and 60 years | sum_t (Capex_pub + AP + E[CL] + OM_pub - Rev_pub)_t / (1+r)^t - RV_H / (1+r)^H | SAR bn PV at H = 30/40/60 | S-fund-021, S-fund-017 |
| `value_for_money_psc` | Public sector comparator vs PPP cost to the state, risk-adjusted | PV(PSC + retained and transferred risk + tax-neutrality adj.) - PV(PPP payments + retained risk + E[CL] + transaction costs) | SAR bn PV and % of PSC | S-fund-024, S-fund-025, S-fund-019, S-fund-030 |

Notes for R7:

- PFRAM's convention: availability payments are firm liabilities; guarantees are contingent liabilities reported as memorandum items, estimated under a worst case (S-fund-021, S-fund-023). R7 reports both the probability-weighted range and the worst case.
- The budget denominator is total state expenditure as published by MoF (S-fund-026); any narrower transport line needs its own source. Beyond 2028 the denominator is an assumption (A-fund-005).
- The risk-transfer value in the VfM test has no Saudi benchmark (unclear how NCP computes the VfM it targets, S-fund-030); it enters as an assumption (A-fund-007) with a wide range, and the VfM sign is reported across that range.
- Skill rule carried forward: a demand-risk PPP is not shown as a fit where the CBA P10 demand breaks BCR = 1 without saying so.
