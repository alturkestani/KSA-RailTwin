> **Document version:** docs/cba.md v1.2 | 3 Nov 2026 | Author: INTEGRATE_R5 (register pointer repointed to docs/assumptions.md); R5 builder (economist) | Status: draft

# Cost–benefit analysis (W4, R5)

**Synthetic demand, uncalibrated: scenario comparison, not a forecast.** Every modelled figure is "in the model"; costs and benefits are P10/P50/P90 ranges over 10,000 Monte Carlo draws per case, never single points. Money: SAR million (tables: SAR bn) at 2025 prices, present value at 2026. Registers: parameters `cities/ksa/assumptions/cba_*.yaml`, assumptions `docs/assumptions.md` (A-cba-1xx/2xx/3xx), sources `docs/sources/r5-cba-a.csv`, `r5-cba-b.csv`, `r5-cost.csv`, `r5-hhr.csv`. Code: `economics/` (`cba.py`, `benefits.py`, `discounting.py`, `montecarlo.py`, `switching.py`, `distribution.py`, `demandruns.py`, `report.py`, `cli.py`).

**Reproduce:** `uv run python -m economics.cli cases && uv run python -m economics.cli inputs --workers 4 && uv run python -m economics.cli run-all --workers 4 && uv run python -m economics.cli summary && uv run python -m economics.cba report`. One case: `uv run python -m economics.cba run --case cities/ksa/cba/CBA-<id>.yaml --seed 1 --out runs/cba/CBA-<id>/`.

## 1. Standards used (edition actually read)

| standard | edition read | what R5 takes from it | source ids |
|---|---|---|---|
| HM Treasury, The Green Book | 2026 edition (updated 28 Oct 2026), PDF read | 60-year horizon for infrastructure (paras 6.11–6.12), residual value (8.32), costs of raising public funds not included (6.44) | S-cp1-088, S-cp1-089, S-r5-cba-019 |
| Green Book supplementary guidance: discounting | Oct 2026 | social rate schedule 3.00 % (years 1–30), 2.50 % (31–75), 2.25 % (76–125), central (A-cba-001, CP1 D1a) | S-cp1-060, S-cp1-061 |
| DfT TAG A1.1 Cost-Benefit Analysis | May 2026 (cover; file name "may-2025") | 60 years after opening, ≤ 100 years (2.3.3–2.3.5), residual value (2.3.10–2.3.11), asset lives (Table 2), market-price unit of account and (1 + t) (2.5.3); TAG 3.5/3.0/2.5 % schedule as a sensitivity | S-cp1-062, S-cp1-085, S-cp1-086, S-cp1-087, S-r5-cba-021 |
| DfT TAG Data Book | v2.03, May 2026 (xlsm, SHA-256 d5a24066…6108) | VoT Table A 1.3.1 (2023 prices and values), indirect tax correction 1.19, elasticity defaults, discount Table A 1.1.1 | S-cp1-063, S-cp1-092, S-cp1-093, S-cp1-094, S-r5-cba-007 |
| DfT TAG A1.3 User and Provider Impacts | May 2026 | rule of a half (2.1.6), VoT income elasticity 1.015 (4.5.1), reliability ratio 0.4 car (6.3.4), lateness 2.5× and ratio 1.4 for PT (6.5.3) | S-r5-cba-029, S-cp1-090, S-r5-cba-008, S-r5-cba-009 |
| DfT TAG A2.1 Wider Economic Impacts Appraisal | May 2026 (gov.uk updated 28 May 2026) | levels 1–3 and report-separately rule (Table 2), land value uplift only for dependent development (4.3.2–4.3.4), imperfect competition 13.4 % of business user benefits and labour supply 40 % of GDP change (Table 4) | S-r5-cba-030, S-r5-cba-016, S-r5-cba-018, S-r5-cba-017 |
| DfT TAG A2.4 Appraisal of Productivity Impacts | cover "November 2025"; gov.uk: updated 29 May 2025, minor correction 11 Dec 2025 (no 2026 edition found) | ATEM method (Eq. 1–4), ρ = 0.043 and α = 1.655 economy-wide (Table 2), sector values (Table C1), inter-city decay tests (5.1.2–5.1.3), ramp 0.5 → 1.0 over 10 years (4.2.2), growth with real GDP per capita (4.3.2), public sector indicative only (5.1.13) | S-r5-cba-011 to S-r5-cba-015 |
| DfT TAG A3 Environmental Impact Appraisal | gov.uk landing page: updated 28 May 2026; **content not read in this pass** (carbon and air-quality values belong to the environment parameters) | edition identified only | S-r5-cba-027 |
| DfT TAG A4.2 Distributional Impact Appraisal | gov.uk landing page: updated 30 May 2024; **content not read in this pass** | edition identified only; R5 reports a qualitative distributional note (nationality and income split of VoT, pilgrims) | S-r5-cba-026 |
| EC Guide to Cost-Benefit Analysis of Investment Projects | Dec 2014 (JASPERS/EIB host, secondary host) | 5 % / 3 % social rates (§2.8.1) as sensitivities (A-cba-002), fiscal corrections net of VAT and MCPF = 1 default (§2.8.2, fn 53) | S-cp1-067, S-cp1-068, S-r5-cba-020 |
| World Bank, Discounting Costs and Benefits in Economic Analysis of World Bank Projects | 9 May 2016 | growth-linked rate range; national rate table (A-cba-002) | S-cp1-069, S-cp1-070, S-cp1-071 |
| World Bank Transport Note TRN-15, Valuation of Time Savings | Jan 2005 | income elasticity 0.5–0.8; non-work fallback 0.3 × household income per head | S-cp1-095, S-cp1-096 |
| ADB Guidelines for the Economic Analysis of Projects | 2017 | 9 % minimum EIRR reference (sensitivity context only) | S-cp1-072 |

Not read in R5-a: World Bank TRN notes other than TRN-15 (e.g. on traffic forecasting or wider benefits), the ITF/OECD wider-benefit papers, the Green Book distributional weights annex. They are not used.

## 2. Saudi guidance

**None found, 3 Nov 2026.** No published Saudi government method for economic (social) cost-benefit appraisal of public projects (discount rate, value of time, appraisal period, shadow prices) was found (S-r5-cba-028, unverified "not found" record).

Searches tried on 3 Nov 2026 (web search; no government document returned): "Saudi Arabia cost-benefit analysis guidelines public investment projects Ministry of Economy and Planning OR Spending Efficiency OR NCP PPP value for money guideline"; "National Center for Privatization PPP guidelines value for money ncp.gov.sa PPP project lifecycle guide"; Arabic "دليل دراسات الجدوى الاقتصادية للمشاريع العامة تحليل التكلفة والعائد وزارة الاقتصاد والتخطيط OR هيئة كفاءة الإنفاق"; "PEFA Saudi Arabia 2023 assessment PI-11 public investment management economic analysis guidelines". Earlier passes: S-fund-056 (no NCP PPP manual or VfM method found), S-fund-029 (FY2026 pre-budget statement has no PPP commitments table).

What exists, and what it does not say:
- **NCP Privatisation Projects Manual (2018)**, known only through a law-firm briefing (S-r5-cba-025, secondary): the manual is mandatory for privatisation projects. Its First File asks for the "identification of the project's direct and indirect economic benefits". The Second File requires a qualitative value-for-money assessment and the Third File a quantitative one. The briefing gives no discount rate, value of time or CBA method. The manual itself was not read.
- **PSP Law Implementing Regulations** (as amended 31 Dec 2023, published 2 Feb 2024): the business case must analyse affordability and value for money (S-fund-053, S-fund-041, secondary). No appraisal parameters are given.
- Not checked directly in this pass: the publication pages of mep.gov.sa, expro.gov.sa (Spending Efficiency), mof.gov.sa and tga.gov.sa, and any IMF PIMA or Article IV text on Saudi public-investment appraisal. These are open items.

So R5 has no Saudi standard to depart from. It follows the UK (Green Book and TAG) as the named standard, with the EC and World Bank guides as cross-checks. A PPP/VfM test under the NCP manual would be a separate, financial exercise (W6, R7).

## 3. Departures from the standard

| standard element | what the standard says | what R5 does | why |
|---|---|---|---|
| Value of time | TAG A1.3 / Data Book: national VoT from a national SP study (S-cp1-092) | Income-transfers the UK TAG 2023 values to KSA 2025 (A-cba-010). Central route: GBP ÷ UK PPP × (KSA/UK GDP per capita PPP)^e × KSA PPP. High end: the market-exchange route used by the mode-choice design VoT (A-mode-006). Low end: World Bank TRN-15 fallback (A-cba-101…106) | No Saudi VoT study found (S-soc-308). Choosing between the routes is a decision for Tariq (A-cba-106). Until he decides, behavioural VoT (mode choice) and appraisal VoT differ by about 1.9–2.0× (the high end ÷ the central value of A-cba-101…103: commute 95.47 ÷ 50.02 = 1.91, business 184.82 ÷ 93.58 = 1.97, non-work 43.58 ÷ 22.83 = 1.91). That inconsistency is stated, not resolved |
| VoT growth | TAG: VoT grows with GDP per head, elasticity 1.015 (A1.3 4.5.1). The Data Book notice gives a flat 1.5 %/yr (S-cp1-094) | Growth = IMF WEO Oct 2026 KSA per-capita growth (1.47 %, range 0.75–2.57) × elasticity 1.0 (range 0.5–1.015) (A-cba-107, A-cba-108) | Saudi growth path, not the UK's. The two TAG methods conflict; R5 uses the elasticity form |
| Demand | TAG: calibrated and validated demand model (M-units) | Synthetic, uncalibrated gravity and mode-choice demand (W8). Every output carries the label | No observed OD matrix or survey yet. Results are scenario comparisons, not forecasts (rule 3) |
| User benefit measure | TAG A1.3 2.1.6: rule of a half per mode / OD / purpose, on generalised cost (S-r5-cba-029) | Rule of a half on the composite generalised cost cost_min = −logsum / |b_ivt,car| (car in-vehicle minutes) per OD and purpose between the matched baseline and the scenario, valued at the appraisal VoT of the purpose (`economics/benefits.py`) | TAG's own rule, applied to the composite cost the mode-choice model gives. TAG 2.1.9 warns that it misstates large changes (new links); the composite also carries the logit taste-variation ("variety") term, so new rail options on long pairs give large minute savings per trip |
| Reliability | TAG A1.3 6.3–6.5: value SD of travel time (car 0.4) and lateness (PT 2.5×, 1.4) | Not monetised in the central case. Sensitivity only (A-cba-109…112) | No KSA intercity journey-time variability data. The TAG urban formula does not apply |
| Wider economic impacts | TAG A2.4: ATEM with UK sectoral ρ and α, LAD-level GDP per worker and sectoral employment (Wider Impacts Dataset) | Static clustering only. Economy-wide ρ 0.043 and α 1.655 on the 423 model zones (governorates, finer around metros). GC_ij = the logsum composite cost of business and commute trips (baseline trip weights in both runs), not TAG's trip-weighted average over modes: the average without mode constants falls when logit users switch for taste reasons, which would make agglomeration negative for every new line (tested in R5, see §7). Own-zone cost capped at 15 min (A-cba-307) because zones are governorate-sized. National GDP per worker (SAR 263,106, range 157,864–322,743). Imperfect competition 13.4 % of business user benefits. Labour supply not modelled. Reported separately (BCR with and without WEIs) (A-cba-130…142, A-cba-307) | No KSA sector-by-region employment or regional GDP. UK elasticities transferred untested. Hydrocarbon GDP inflates GDP per worker, hence the low variant. The UK tax wedge (labour supply 40 %) does not transfer |
| Discount rate | Green Book 2026: 3.00 / 2.50 / 2.25 % declining (S-cp1-060). EC Guide 2014: 5 % (Cohesion) or 3 % (S-cp1-067). World Bank: country-specific, growth-linked | Central: Green Book 2026 declining schedule (A-cba-001, CP1 D1a). Sensitivities: TAG 3.5/3.0/2.5 %, 5 %, 7 % (A-cba-002). FIRR on 6–8 % commercial (A-cba-003) | Approved by Tariq at CP1. The UK social time preference rate is not KSA-derived. The EC 5 % and the 7 % show the sensitivity |
| Appraisal period | Green Book / TAG: 60 years after opening (≤ 100) | 60 years central; 30 and 40 years as finite-life variants with residual value (A-cba-004) | The brief asks for 30/40/60. No standard gives 30 or 40 years for rail |
| Residual value | TAG A1.1 2.3.10–2.3.11, Green Book 8.32: residual value for finite periods | Straight-line remaining life by asset class at the horizon end: civil 100, track 40, systems 40, buildings 40, rolling stock 30 years (TAG A1.1 Table 2, S-cp1-087); renewable classes age ((h − 1) mod L) + 1 since their last costed renewal; S5 stations are not renewed inside the horizon (A-cba-126, A-cba-305) | A simple and transparent method. Civils (life > 60 years) carry a large residual at 30/40 years, so it is shown as a separate line |
| Price base and relative prices | TAG: market prices, real terms, relative price changes where evidenced (VoT, carbon, fuel) | SAR, 2025 prices (A-cost-001). No relative price changes except VoT growth and carbon-value growth | No KSA evidence on real construction-cost or fuel-price paths was found in this pass. Retail fuel prices are published monthly by Aramco (S-soc-316) |
| Indirect tax correction | TAG A1.1 2.5.3: convert factor-cost items (public costs) to market prices with (1 + t), t = 0.19 UK (S-r5-cba-021, S-r5-cba-007) | No (1 + t) on costs in the central case. Business VoT is put in market prices with t = 0.15 (KSA VAT, S-r5-cba-022; A-cba-124). The EC Guide's net-of-VAT rule (S-r5-cba-020) is noted | Whether the cost register's estimates include VAT is not established. The KSA average indirect tax rate is not published (15 % VAT is the standard rate; exempt and zero-rated supplies lower the average). A fuel excise beyond VAT was not found in this pass: retail fuel prices are set and published by Aramco (S-soc-316). Not confirmed against ZATCA |
| Fares | TAG: fares are transfers between users and operator in the social CBA; they enter generalised cost and the operator / public accounts | The same: fares enter generalised cost and revenue (FIRR, fiscal cost). They cancel in NPV (A-cba-120…122) | Standard treatment |
| Land value uplift | TAG A2.1 4.3: LVU only for dependent development; overlaps user benefits and WEIs (S-r5-cba-018) | Not added to benefits. Reported only as a capture potential (W6) | No double counting (cba-appraisal skill) |
| Decongestion | TAG A5.4: marginal external costs from VKT change (unit not read in this pass; the Data Book v2.03 carries MEC sheets A5.4.x) | Jeddah urban legs (15 km per trip end in a Jeddah metro zone, A-cba-308) belong to the TrafficTwin channel only; the R4 matched-control run (r4_hhr_jeddah_kaia vs baseline-weekday-f0.1-s1-ae764558-346893f2-a998e1, seed 1) found no measurable change and no R5 candidate is representable in TrafficTwin (no external demand), so the Jeddah stream is zero, a lower bound. Elsewhere VKT-based with the intercity marginal external cost (A-cba-220). Never both for one trip | TrafficTwin is read-only and single-seed (CP5 H7c) |
| Marginal cost of public funds | Green Book 6.44: not included (S-r5-cba-019). EC Guide fn 53: MCPF = 1 by default (S-r5-cba-020) | Not applied (MCPF = 1). 1.2 as a fiscal-cost sensitivity only (A-cba-123) | No Saudi MCPF estimate or guidance (S-r5-cba-028). Whether the UK tax-distortion logic transfers to the Saudi revenue mix was not examined in this pass |
| Optimism bias / reference class | Green Book and TAG: uplift costs for optimism bias | Capex enters uplifted and the construction duration is the uplifted R1c schedule draw (reference-class-forecasting skill, cities/ksa/costs/uplifts.yaml; the same draws as costs.rcf, same seed). Demand carries the reference-class ridership ratio (actual ÷ forecast, Flyvbjerg rail class, A-rcf-029) in every draw. The A-cba-116…119 duration rule is a cross-check only | The standard treatment; capex and schedule uplifts are not doubled. The ridership ratio is applied to a synthetic forecast, which is a further departure: its median (about 0.69) lowers every demand-driven benefit |
| Demand ramp-up | No TAG default found | 0.70 / 0.85 / 0.95 of mature demand in years 1–3 (A-cba-113…115). Opex not ramped (A-cba-125) | World Bank China (about 70 %) and ECA (6 m vs 9 m) evidence. Years 2–3 are assumed |
| Distributional and Vision 2030 | TAG A4.2: distributional appraisal (content not read) | A qualitative scorecard (`docs/cba-scorecard.md`, regional development, Vision 2030 alignment, visitor capacity), not monetised; `docs/distribution.md` follows TAG A4.2's share-of-benefits vs share-of-population comparison by region, with an unemployment-tercile proxy for income bands. VoT is not segmented by nationality or income | No source monetises these (rule 1). the A4.2 method is applied as set out in docs/social.md Part B (S-soc-051, verified in R1d); the unit was not re-read in R5 |
| Non-UK pilgrims and tourists | Not covered by TAG | Non-work VoT for all pilgrims and tourists (A-cba-104, A-cba-105) | No Umrah or tourism VoT found. The values of foreign visitors reflect origin-country incomes |
| Vehicle operating costs | TAG A1.3: fuel and non-fuel VOC in user benefits | The demand model's car cost is fuel only (A-mode-023), so fuel savings are inside the user benefit and the non-fuel resource saving (A-cba-222) is a separate stream on the change in car-km | Avoids double counting fuel |
| Freight | TAG / EC: freight user and external benefits | Not monetised (zero): no open freight OD exists (`freight.json`; A-cba-309); the cba_freight.yaml parameters are kept for when a corridor freight volume is sourced. Freight-carrying costs of the mixed lines remain in the costs, so mixed-line BCRs are lower bounds | Rule 1: no fabricated volumes |
| International visitors | Not covered by TAG | Foreign Umrah and Hajj visitors (demand.intl, fixed calibrated share A-intl-003) carry no generalised-cost model, so their user benefits and fares are not counted; capacity effects are scorecard-only (A-cba-310) | No behavioural model for them |
| S5 station additions | TAG: incremental costs | Capex = the new station item(s) only (trace P10/P50/P90, H10a spread) × the run's reference-class multipliers; opex 2 % (1–4 %) of station capex a year (A-cba-314, assumed); through-passenger delay is inside the demand runs (stop time in the rail graph) | No per-station opex item in the register |
| Construction start and PV year | TAG: discount to a common base year | Every case starts construction in 2027 and is discounted to 2026 (A-cba-301) | Cases compare on equal terms; a common delay shifts all alike |

## 4. What is appraised (cases)

`cities/ksa/cba/CBA-<id>.yaml` (schema `CbaCase`, generated by `economics.cli cases`): one case for every S2–S5 candidate of the regenerated set (CP5 H4a: 72 candidates; `logs/r5` and `docs/status/r5.md` give the before/after list), each against the matched baseline S1 (same zones, seed 1, population scenario, year and fitted constants; rule 6); the H8 two-station Jubail variant (`cities/ksa/cba/variants/`); and the committed-programme check S1 vs S0 (Landbridge, Riyadh Rail Link and the Saudi GCC section, costed with `costs.estimate` on their line YAMLs: `runs/costs/S1-*`). Every case names its cost run, demand inputs, population scenarios (UN WPP low, medium, high), horizons (30/40/60 years after opening) and rate cases (Green Book 2026 declining central; TAG declining; flat 5 %; flat 7 %; a `drawn` case with the Green Book schedule shifted by U[−0.5, +1.0] points, A-cba-304).

## 5. Benefit streams and the no-double-counting matrix

Demand inputs (`economics.demandruns`): for every case and every (population, year) group, the baseline and the scenario are run with `demand.gravity` (R4 network, R5 calibration `runs/r5/demand/calibration-r5-s1`) and reduced to the physical changes below (`runs/cba/inputs/<pop>-<year>/`). Years: 2025 (calibration point, shared), 2040, 2050, 2060; linear in between, flat after 2060 (A-cba-306). The matrix is generated from `economics.benefits.MATRIX`; `tests/test_economics_benefits.py` fails if a channel is counted twice or a stream counts a channel that another already contains.

<!-- BEGIN GENERATED MATRIX -->
| stream | channel it counts | channels it excludes | contains | in the totals as | method |
|---|---|---|---|---|---|
| user_time_cost | generalised_cost | fare_revenue, vehicle_operating_cost_nonfuel, land_value, agglomeration | fare_paid, vehicle_operating_cost_fuel, rail_air_on_time | core | rule of a half on the logsum composite cost per OD and purpose (TAG A1.3); contains fares and the car FUEL cost (perceived, A-mode-023) |
| vehicle_operating_cost_nonfuel | vehicle_operating_cost_nonfuel | generalised_cost | — | core | non-fuel car VOC (resource cost) x change in car vkm; the logsum's car cost is fuel only, so this channel is not in generalised_cost (TAG A1.3 non-fuel VOC) |
| reliability | travel_time_variability | generalised_cost | — | core | SENSITIVITY ONLY (zero in the central case, A-cba-109/112): car journey-time SD x reliability ratio x VoT, rule of a half, on car trips diverted to rail (TAG A1.3 sec. 6); the logsum carries an on-time term for rail and air only, so the car variability channel is not in generalised_cost |
| fare_revenue | fare_revenue | generalised_cost | — | cost_side | rail trips x model fare (cost_sar_rail); a transfer from users to the operator, netted from PVC (TAG A1.1 broad transport budget) |
| safety | road_crashes | generalised_cost | — | core | crash cost per car / bus vehicle-km x change in vehicle-km, rail train-km added |
| carbon | ghg_emissions | air_quality | — | core | emission factors x change in car / bus vkm, air pkm and rail train-km x carbon value |
| air_quality | local_pollutants | ghg_emissions | — | core | damage cost per vehicle-km (TAG A3 / EU Handbook, transferred) |
| decongestion_interurban | congestion_interurban_vkm | congestion_jeddah_traffictwin, generalised_cost | — | core | marginal external congestion cost x car vkm change outside the Jeddah metro urban legs (VKT-based) |
| decongestion_jeddah | congestion_jeddah_traffictwin | congestion_interurban_vkm | — | core | TrafficTwin matched-control runs (R4 run ids) for the Jeddah urban legs only; never VKT-valued as well |
| freight_shift | freight_road_to_rail | generalised_cost, road_crashes, ghg_emissions | — | core | NOT MONETISED (zero, A-cba-309): no open freight OD exists (demand freight.json); method if a corridor freight volume is sourced: tkm diverted x (road - rail cost + truck externalities, cba_freight.yaml); passenger time savings excluded |
| wei_agglomeration | agglomeration | generalised_cost, land_value | — | wei | TAG A2.4 effective density x elasticity x GDP per zone (reported separately) |
| wei_imperfect_competition | output_imperfect_competition | generalised_cost | — | wei | uplift on business user benefits (TAG A2.4, reported separately) |
| land_value_uplift | land_value | generalised_cost, agglomeration | — | capture_only | capture potential only, not added (it capitalises the time savings) |
| tourism_hajj_umrah_capacity | visitor_capacity | generalised_cost | — | scorecard | international visitors carry no generalised-cost model (demand.intl fixed share); capacity value not monetised unless sourced (none found): scorecard only |
| regional_development_vision2030 | regional_development | agglomeration, generalised_cost | — | scorecard | qualitative scorecard (docs/cba-scorecard.md), not monetised |
<!-- END GENERATED MATRIX -->

Physical quantities per OD and purpose: user benefit = ½ (T0 + T1)(C0 − C1) generalised minutes, valued at the purpose VoT growing with real GDP per head × elasticity; car-km change = Δ car trips × road-km ÷ occupancy (split into the Jeddah urban legs and the rest); bus-km and air passenger-km likewise; rail fare revenue = Σ trips × model fare. Emissions: car, bus and domestic-air factors, rail electricity at the KSA grid factor path (A-cba-212…214) on the case's train-km from its cost run. Safety, air quality and congestion: damage costs per vehicle-km. WEIs: TAG A2.4 effective density per zone, ΔWI = ρ × ΔED/ED × jobs × GDP per worker, with the A2.4 ramp (0.5 → 1.0 over 10 years); imperfect competition = 13.4 % of business user benefits.

## 6. Outputs, Monte Carlo, tornado and switching values

Per case (`runs/cba/<case>/`): `results.json` (PVB, PVC, NPV and BCR without and with WEIs, EIRR, FIRR, payback, fiscal cost to the state, PV of every stream, P10/P50/P90 per population scenario × horizon × rate case), `draws.parquet` (inputs and the 60-year NPV/BCR per draw), `tornado.csv/.png`, `switching_values.json`, `meta.json`. PVC = PV(capex + opex + renewals − residual value − fare revenue) (TAG broad transport budget); BCR = PVB ÷ PVC (∞ where fares exceed the costs); EIRR on benefits + fares − costs (+ residual value); FIRR on fares − costs (no terminal value); fiscal cost = PV(costs − fares) under fully public delivery (A-cba-312; delivery models are W6/R7).

Monte Carlo inputs (`economics.montecarlo`): capex (uplifted) and construction duration from the case's own R1c draws, shared with `costs.rcf` (same seed, same multipliers; checked in every run and in `tests/test_economics_montecarlo.py`); opex and renewals from the same `costs.estimate` draws; ridership actual ÷ forecast (Flyvbjerg rail reference class, `costs.rcf` ridership uplift, drawn after the capex and schedule streams so those stay identical); one VoT multiplier for every purpose; carbon, crash, air-quality, congestion and agglomeration multipliers; the discount-rate shift (drawn case). Correlations (A-cba-302): capex and duration as R1c draws them; ridership independent of costs; the VoT multiplier common to all purposes; externality multipliers independent.

Switching values (`economics.switching`): demand as a share of the modelled forecast for BCR = 1, the capex multiplier and the VoT multiplier for BCR = 1, and the constant real rate with NPV = 0, each on the deterministic central row (draw medians, multipliers 1, ridership ratio at its median, medium population, 60 years, Green Book 2026). Tornado: one-at-a-time P10/P90 swings of capex, duration, opex, ridership, VoT, carbon, crash and congestion values, the population scenario and the rate schedule.

## 7. Wider impacts: a method-sensitivity warning

In the model the agglomeration estimate is large relative to user benefits for some cases (BCR with WEIs far above the core BCR). Two reasons, found while building R5: (i) the logit composite cost falls by up to ln(1/s_car)/|b_ivt| minutes when a competitive rail option appears (the literature IVT coefficient makes the taste-variation term worth tens of minutes on intercity pairs), and (ii) the zones are governorate-sized, so the own-zone density term is small even with the 15-minute cap. Under TAG's own definition (trip-weighted average generalised cost over modes, without mode constants) the job-weighted effective density **fell** in a development test on three cases (the S1 programme, Jeddah–Yanbu trunk and the Al Jubayl station; scratch run, not retained), because logit users switch to rail for taste reasons at a higher average time-and-money cost. **The WEI figures are therefore indicative only; rankings use the BCR without WEIs, and the BCR with WEIs should not be used for decisions until a survey-based mode choice (W7) and finer zones exist.**

## 8. Parameters (generated from `cities/ksa/assumptions/cba_*.yaml`)

Every key is sourced or a registered assumption with a range (`economics.params` refuses one without). The value of time uses the PPP income transfer (A-cba-106, **decision pending for Tariq at the R5 checkpoint**); the market-exchange route is the high end of each range, which is also the route the mode-choice design VoT uses (A-mode-006), so behavioural and appraisal VoT differ by about 1.9–2.0× (the high end ÷ the central value of A-cba-101…103: commute 95.47 ÷ 50.02 = 1.91, business 184.82 ÷ 93.58 = 1.97, non-work 43.58 ÷ 22.83 = 1.91).

<!-- BEGIN GENERATED PARAMETERS -->
| key | value | low | high | unit | file | ids |
|---|---|---|---|---|---|---|
| access_distance_km | 30 | 20 | 50 | km straight-line to the nearest station | cba_programme.yaml | A-cba-313 |
| agglomeration_decay_alpha | 1.655 | 1.097 | 1.818 | distance-decay exponent on generalised cost | cba_wei.yaml | A-cba-131, S-r5-cba-011, S-r5-cba-012, S-r5-cba-013 |
| agglomeration_decay_alpha_business_intercity | 1.782 | 1.746 | 1.818 | distance-decay exponent, business purpose, inter-city test | cba_wei.yaml | A-cba-132, S-r5-cba-013, S-r5-cba-012 |
| agglomeration_elasticity | 0.043 | 0.021 | 0.083 | elasticity of productivity w.r.t. ATEM | cba_wei.yaml | A-cba-130, S-r5-cba-011, S-r5-cba-012 |
| agglomeration_ramp_year1 | 0.5 | 0.5 | 1 | share of full agglomeration benefit in opening year | cba_wei.yaml | A-cba-137, S-r5-cba-014 |
| agglomeration_ramp_years | 10 | 10 | 10 | years to full benefit | cba_wei.yaml | A-cba-138, S-r5-cba-014 |
| air_quality_cost_sar_per_bus_vkm | 0.8733 | 0.4366 | 1.3099 | SAR per bus vehicle-km | cba_externalities.yaml | A-cba-218, S-r5-cba-223 |
| air_quality_cost_sar_per_car_vkm | 0.0078 | 0.0063 | 0.0323 | SAR per car vehicle-km | cba_externalities.yaml | A-cba-217, S-r5-cba-201, S-r5-cba-223 |
| air_quality_cost_sar_per_train_km_diesel | 18.006 | 2.862 | 27.01 | SAR per diesel train-km | cba_externalities.yaml | A-cba-219, S-r5-cba-223, S-r5-cba-224 |
| bus_occupancy_intercity | 25 | 12.8 | 40 | passengers per bus (per vehicle-km) | cba_externalities.yaml | A-cba-202, S-r5-cba-202, S-r5-cba-219 |
| car_occupancy_intercity | 2 | 1.61 | 2.5 | persons per car (per vehicle-km) | cba_externalities.yaml | A-cba-201, S-r5-cba-202 |
| car_vehicle_operating_cost_sar_per_vkm | 0.503 | 0.3552 | 0.6592 | SAR per car vehicle-km (resource cost | cba_externalities.yaml | A-cba-222, S-soc-316, S-soc-317, S-r5-cba-207 |
| car_voc_fuel_sar_per_vkm | 0.218 | 0.1557 | 0.2913 | SAR per car vehicle-km | cba_externalities.yaml | A-cba-222, S-soc-316, S-soc-317 |
| car_voc_nonfuel_sar_per_vkm | 0.285 | 0.1995 | 0.368 | SAR per car vehicle-km | cba_externalities.yaml | A-cba-222, S-r5-cba-207 |
| carbon_value_2025 | 1858.9 | 929.4 | 2788.3 | SAR per tCO2e | cba_externalities.yaml | A-cba-205, S-r5-cba-204, S-r5-cba-205 |
| carbon_value_growth_real | 0.0151 | 0.0151 | 0.0151 | fraction per year (real) | cba_externalities.yaml | A-cba-206, S-r5-cba-204 |
| carbon_value_hlccp_2030_sar_per_tco2e | 362.6 | 241.8 | 483.5 | SAR per tCO2e (2030) | cba_externalities.yaml | A-cba-207, S-r5-cba-227 |
| carbon_value_sar_per_tco2e_2025 | 1858.9 | 929.4 | 2788.3 | SAR per tCO2e | cba_externalities.yaml | A-cba-205, S-r5-cba-204, S-r5-cba-205 |
| construction_start_year | 2027 | 2027 | 2032 | year | cba_programme.yaml | A-cba-301 |
| construction_years_base | 4 | 3 | 5 | years (fixed part of the duration rule) | cba_appraisal.yaml | A-cba-116, S-r5-cba-023, S-007, S-al_baha-008 |
| construction_years_max | 12 | 8 | 16 | years | cba_appraisal.yaml | A-cba-119, S-r5-cba-023 |
| construction_years_min | 4 | 3 | 5 | years | cba_appraisal.yaml | A-cba-118, S-r5-cba-023 |
| construction_years_per_100km | 1 | 0.5 | 2 | years per 100 route-km | cba_appraisal.yaml | A-cba-117, S-r5-cba-023, S-007, S-al_baha-008 |
| ef_air_kgco2e_per_pkm_domestic | 0.1355 | 0.1355 | 0.2628 | kg CO2e per passenger-km | cba_externalities.yaml | A-cba-210, S-r5-cba-210 |
| ef_bus_kgco2e_per_vkm | 0.6153 | 0.4923 | 0.7999 | kg CO2e per bus vehicle-km | cba_externalities.yaml | A-cba-209, S-r5-cba-208, S-r5-cba-209 |
| ef_car_kgco2e_per_vkm | 0.2354 | 0.1615 | 0.2942 | kg CO2e per car vehicle-km (tank-to-wheel) | cba_externalities.yaml | A-cba-208, S-r5-cba-209, S-soc-317 |
| ef_rail_diesel_kgco2e_per_train_km | 12.645 | 2.01 | 14.752 | kg CO2e per train-km (diesel passenger train) | cba_externalities.yaml | A-cba-216, S-cost-opex-012, S-r5-cba-209, S-r5-cba-224 |
| ef_rail_diesel_l_per_train_km | 4.751 | 4.157 | 5.543 | litres diesel per train-km | cba_externalities.yaml | A-cba-216, S-cost-opex-012, S-r5-cba-209 |
| ef_rail_electric_kwh_per_train_km_commuter | 7.34 | 4.97 | 8.31 | kWh per train-km | cba_externalities.yaml | A-cba-213, S-cost-opex-012, S-cost-opex-013 |
| ef_rail_electric_kwh_per_train_km_conventional | 10.09 | 7.34 | 16.51 | kWh per train-km (at pantograph) | cba_externalities.yaml | A-cba-212, S-cost-opex-012, S-cost-opex-013 |
| ef_rail_electric_kwh_per_train_km_hsr | 16.31 | 11.9 | 19.45 | kWh per train-km (from the grid) | cba_externalities.yaml | A-cba-211, S-cost-opex-011 |
| effective_density_cutoff_km | 0 | 0 | 0 | km (0 = no cut-off) | cba_wei.yaml | A-cba-133, S-r5-cba-011 |
| effective_density_cutoff_min | 0 | 0 | 200 | generalised minutes (0 = no cut-off) | cba_wei.yaml | A-cba-134, S-bench-de-025 |
| employment_national_total | 1.4837e+07 | 1.4837e+07 | 1.82e+07 | jobs (workplace-based), 2025 | cba_wei.yaml | A-cba-141, S-r3-cal-050, S-soc-338 |
| fare_sar_per_km_commuter | 0.1 | 0.067 | 0.2 | SAR per km (average trip) | cba_appraisal.yaml | A-cba-122, S-r5-cba-024 |
| fare_sar_per_km_conventional | 0.2 | 0.195 | 0.3 | SAR per track-km, economy, one way | cba_appraisal.yaml | A-cba-121, S-r1a-024, S-r1a-021, S-soc-319 |
| fare_sar_per_km_hsr | 0.405 | 0.356 | 0.558 | SAR per track-km, economy, one way | cba_appraisal.yaml | A-cba-120, S-soc-318, S-r1a-012, S-r4-rt-002 |
| freight_diversion_ramp_years | 5 | 3 | 8 | years to full diversion | cba_freight.yaml | A-cba-237 |
| freight_road_to_rail_diversion_share | 0.05 | 0 | 0.15 | share of corridor road tonne-km diverted to rail at full ramp | cba_freight.yaml | A-cba-237, S-r1a-037 |
| gdp_per_worker_growth | 1.47 | 0.75 | 2.57 | % per year, real | cba_wei.yaml | A-cba-136, S-r5-cba-015, S-r5-cba-005, S-r5-cba-006, S-r5-cba-001 |
| gdp_per_worker_sar | 263106 | 157864 | 322743 | SAR per worker per year | cba_wei.yaml | A-cba-135, S-r5-cba-004, S-soc-338, S-r3-cal-050 |
| imperfect_competition_uplift | 0.134 | 0.1 | 0.134 | share of business user benefits (incl. reliability) | cba_wei.yaml | A-cba-139, S-r5-cba-016, S-r5-cba-017 |
| indirect_tax_rate_ksa | 0.15 | 0.1 | 0.15 | average indirect tax rate t (proxy) | cba_appraisal.yaml | A-cba-124, S-r5-cba-022, S-r5-cba-021 |
| intrazonal_gc_cap_min | 15 | 10 | 25 | generalised minutes | cba_programme.yaml | A-cba-307 |
| intrazonal_speed_kmh | 30 | 20 | 40 | km/h | cba_programme.yaml | A-cba-307 |
| jeddah_urban_leg_km | 15 | 10 | 25 | km per trip end in the Jeddah metro | cba_programme.yaml | A-cba-308 |
| ksa_grid_kgco2e_per_kwh | 0.692 | 0.543 | 0.702 | kg CO2e per kWh generated | cba_externalities.yaml | A-cba-214, S-r5-cba-212, S-r5-cba-203 |
| labour_supply_uplift | 0 | 0 | 0 | share of GDP change (welfare) | cba_wei.yaml | A-cba-140, S-r5-cba-016 |
| marginal_cost_of_public_funds | 1 | 1 | 1.2 | multiplier on net public funds (MCPF) | cba_appraisal.yaml | A-cba-123, S-r5-cba-019, S-r5-cba-020 |
| marginal_external_congestion_cost_sar_per_car_vkm_intercity | 0.012 | 0.0032 | 0.4688 | SAR per car vehicle-km | cba_externalities.yaml | A-cba-220, S-r5-cba-201 |
| marginal_external_congestion_cost_sar_per_car_vkm_urban | 1.6501 | 0.1892 | 4.2277 | SAR per car vehicle-km | cba_externalities.yaml | A-cba-221, S-r5-cba-201 |
| opex_share_year1 | 1 | 0.85 | 1 | share of steady-state opex in the first year | cba_appraisal.yaml | A-cba-125 |
| public_sector_agglomeration_included | 0 | 0 | 1 | switch (0 = excluded from central, 1 = indicative variant) | cba_wei.yaml | A-cba-142, S-r5-cba-011 |
| pv_year | 2026 | 2026 | 2026 | year | cba_programme.yaml | A-cba-301 |
| rail_crash_cost_sar_per_train_km | 3.1789 | 1.0536 | 4.7684 | SAR per train-km (external accident cost) | cba_externalities.yaml | A-cba-204, S-r5-cba-222 |
| rail_crash_cost_sar_per_train_km_hsr | 1.0536 | 0.5268 | 3.1789 | SAR per train-km | cba_externalities.yaml | A-cba-204, S-r5-cba-222 |
| rail_freight_cost_sar_per_tkm | 0.0856 | 0.0201 | 0.1198 | SAR per tonne-km (SAR published tariff | cba_freight.yaml | A-cba-231, S-r5-cba-226, S-r1a-038 |
| rail_freight_kgco2e_per_tkm | 0.02583 | 0.0181 | 0.0336 | kg CO2e per tonne-km (diesel freight train) | cba_freight.yaml | A-cba-233, S-r5-cba-211, S-r5-cba-224 |
| rail_lateness_factor | 2.5 | 2 | 3 | value of 1 min average lateness / value of 1 min in-vehicle time (rail) | cba_appraisal.yaml | A-cba-110, S-r5-cba-009 |
| rail_reliability_ratio | 1.4 | 1 | 1.8 | value of SD of lateness / value of average lateness (PT) | cba_appraisal.yaml | A-cba-111, S-r5-cba-009 |
| rail_reliability_sd_share | 0.1 | 0.05 | 0.2 | SD of car journey time / mean journey time, intercity roads | cba_appraisal.yaml | A-cba-112 |
| ramp_up_year1 | 0.7 | 0.5 | 0.85 | share of mature demand, first full year of operation | cba_appraisal.yaml | A-cba-113, S-bench-cn-068, S-bench-fr-011 |
| ramp_up_year2 | 0.85 | 0.7 | 0.95 | share of mature demand, second year | cba_appraisal.yaml | A-cba-114 |
| ramp_up_year3 | 0.95 | 0.85 | 1 | share of mature demand, third year | cba_appraisal.yaml | A-cba-115 |
| rate_shift | 0 | -0.005 | 0.01 | absolute shift of every band of the Green Book 2026 schedule | cba_programme.yaml | A-cba-304 |
| real_gdp_per_capita_growth | 1.47 | 0.75 | 2.57 | % per year, real, KSA | cba_appraisal.yaml | A-cba-108, S-r5-cba-005, S-r5-cba-006, S-r5-cba-001 |
| reliability_ratio | 0.4 | 0.3 | 0.8 | value of 1 min SD of car journey time / value of 1 min of time | cba_appraisal.yaml | A-cba-109, S-r5-cba-008 |
| road_crash_cost_sar_per_bus_vkm | 0.3872 | 0.1901 | 1.1511 | SAR per bus vehicle-km | cba_externalities.yaml | A-cba-224, S-r5-cba-222 |
| road_crash_cost_sar_per_car_vkm | 0.1475 | 0.0724 | 0.4385 | SAR per car vehicle-km (average total casualty cost) | cba_externalities.yaml | A-cba-203, S-r5-cba-219, S-r5-cba-215, S-r5-cba-218, S-r5-cba-206, S-r5-cba-221, S-r5-cba-216, S-soc-317, S-r5-cba-220, S-r5-cba-222, S-r5-cba-201 |
| road_freight_cost_sar_per_tkm | 0.1466 | 0.0734 | 0.2562 | SAR per tonne-km (resource cost | cba_freight.yaml | A-cba-230, S-r5-cba-207, S-r5-cba-208, S-cost-opex-016, S-soc-338, S-r5-cba-211 |
| station_opex_share_of_capex | 0.02 | 0.01 | 0.04 | share of station base capex per year | cba_programme.yaml | A-cba-314 |
| truck_air_quality_cost_sar_per_tkm | 0.0463 | 0.0231 | 0.0694 | SAR per tonne-km | cba_freight.yaml | A-cba-235, S-r5-cba-223 |
| truck_congestion_cost_sar_per_tkm | 0.0244 | 0.0049 | 0.0487 | SAR per tonne-km | cba_freight.yaml | A-cba-236, S-r5-cba-225 |
| truck_crash_cost_sar_per_tkm | 0.0792 | 0.0266 | 0.1156 | SAR per tonne-km | cba_freight.yaml | A-cba-234, S-r5-cba-222, S-r5-cba-220 |
| truck_kgco2e_per_tkm | 0.07835 | 0.0603 | 0.19947 | kg CO2e per tonne-km | cba_freight.yaml | A-cba-232, S-r5-cba-211 |
| vot_business | 93.58 | 76.15 | 184.82 | SAR per person-hour (market price) | cba_appraisal.yaml | A-cba-102, S-cp1-092, S-r5-cba-007, S-cost-idx-002, S-r5-cba-001, S-r5-cba-002, S-cp1-097, S-cp1-098, S-cost-idx-003, S-r5-cba-022 |
| vot_commute | 50.02 | 46.81 | 95.47 | SAR per person-hour | cba_appraisal.yaml | A-cba-101, S-cp1-092, S-cost-idx-002, S-r5-cba-001, S-r5-cba-002, S-cp1-097, S-cp1-098, S-cost-idx-003, S-cp1-095 |
| vot_income_elasticity | 1 | 0.5 | 1.015 | elasticity of VoT to real GDP per capita (over time and cross-section) | cba_appraisal.yaml | A-cba-107, S-cp1-093, S-cp1-090, S-cp1-095, S-cp1-094 |
| vot_leisure_vfr | 22.83 | 12.46 | 43.58 | SAR per person-hour | cba_appraisal.yaml | A-cba-103, S-cp1-092, S-cost-idx-002, S-r5-cba-001, S-r5-cba-002, S-cp1-097, S-cp1-098, S-cost-idx-003, S-cp1-096, S-r5-cba-010, S-r5-cba-003 |
| vot_pilgrimage | 22.83 | 12.46 | 43.58 | SAR per person-hour | cba_appraisal.yaml | A-cba-105, S-cp1-092, S-r5-cba-002, S-cp1-096, S-r5-cba-010 |
| vot_tourism | 22.83 | 12.46 | 43.58 | SAR per person-hour | cba_appraisal.yaml | A-cba-104, S-cp1-092, S-r5-cba-002, S-cp1-096, S-r5-cba-010 |
<!-- END GENERATED PARAMETERS -->

## 9. Results (generated)

<!-- BEGIN GENERATED RESULTS (uv run python -m economics.cba report) -->
**synthetic demand, uncalibrated: scenario comparison, not a forecast.** Every figure below is a P10 / P50 / P90 range over the Monte Carlo draws (10,000 per case, seed 1), SAR bn at 2025 prices, present value at 2026, against the matched baseline (S1 for S2–S5; S0 for S1). In the model, these are scenario comparisons on synthetic, uncalibrated demand; they are not forecasts. Generated from `runs/cba/summary.parquet` by `uv run python -m economics.cba report`.

Ranking basis: UN WPP medium population scenario, 60-year horizon, Green Book 2026 declining social rate (A-cba-001). BCR without wider impacts ranks; the BCR with wider impacts (TAG A2.4) is shown beside it, never added to the core BCR. Demand switching value = share of the modelled forecast at which BCR = 1 (central inputs); capex switching value = multiplier on central uplifted capex at which BCR = 1.

#### S2 trunk gaps (23 cases)

| rank | case | BCR P10 / P50 / P90 | BCR with WEIs P10 / P50 / P90 | NPV SAR bn P10 / P50 / P90 | EIRR P10 / P50 / P90 | demand for BCR = 1 | capex × for BCR = 1 | run |
|---|---|---|---|---|---|---|---|---|
| 1 | S2-trunk_gap-riyadh-dammam-khobar-dhahran | 0.06 / 0.24 / 0.83 | 0.31 / 0.86 / 2.07 | -132.1 / -42.1 / -6.3 | -2.4 % / -0.6 % / 2.2 % | 190 % | 0.05 | `runs/cba/CBA-S2-trunk_gap-riyadh-dammam-khobar-dhahran` |
| 2 | S2-trunk_gap-riyadh-hafar-al-batin | 0.03 / 0.13 / 0.38 | 0.11 / 0.28 / 0.62 | -90.0 / -36.5 / -19.9 | -8.9 % / -4.0 % / -1.3 % | 365 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-riyadh-hafar-al-batin` |
| 3 | S2-trunk_gap-madinah-ha-il | 0.01 / 0.06 / 0.18 | 0.03 / 0.08 / 0.21 | -80.9 / -34.5 / -22.4 | -10.7 % / -5.9 % / -2.5 % | 701 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-madinah-ha-il` |
| 4 | S2-trunk_gap-riyadh-al-jubayl | 0.01 / 0.05 / 0.16 | 0.11 / 0.27 / 0.58 | -84.4 / -35.5 / -23.1 | -10.8 % / -5.9 % / -2.5 % | 701 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-riyadh-al-jubayl` |
| 5 | S2-trunk_gap-madinah-yanbu | 0.01 / 0.05 / 0.16 | 0.03 / 0.09 / 0.23 | -90.1 / -30.0 / -17.7 | -6.6 % / -3.6 % / -1.9 % | 914 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-madinah-yanbu` |
| 6 | S2-trunk_gap-jeddah-yanbu | 0.01 / 0.04 / 0.13 | 0.05 / 0.12 / 0.26 | -66.5 / -28.6 / -19.2 | -11.2 % / -6.5 % / -2.7 % | 938 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-jeddah-yanbu` |
| 7 | S2-trunk_gap-madinah-ar-rass | 0.01 / 0.04 / 0.13 | 0.04 / 0.11 / 0.24 | -91.8 / -39.2 / -26.3 | -11.3 % / -6.5 % / -2.7 % | 996 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-madinah-ar-rass` |
| 8 | S2-trunk_gap-riyadh-jeddah | -0.00 / 0.03 / 0.12 | 0.37 / 1.00 / 2.40 | -323.0 / -123.8 / -76.1 | -4.8 % / -2.7 % / -1.6 % | 895 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-riyadh-jeddah` |
| 9 | S2-trunk_gap-dammam-khobar-dhahran-al-kharj | 0.00 / 0.03 / 0.10 | 0.04 / 0.10 / 0.23 | -89.7 / -39.0 / -26.6 | -12.2 % / -7.1 % / -2.9 % | 1204 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-dammam-khobar-dhahran-al-kharj` |
| 10 | S2-trunk_gap-al-jubayl-hafar-al-batin | 0.00 / 0.03 / 0.09 | 0.03 / 0.08 / 0.17 | -81.3 / -35.6 / -24.5 | -12.1 % / -7.1 % / -2.9 % | 1257 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-al-jubayl-hafar-al-batin` |
| 11 | S2-trunk_gap-taif-bisha | 0.00 / 0.02 / 0.09 | 0.02 / 0.06 / 0.13 | -68.8 / -28.3 / -19.1 | -11.0 % / -6.4 % / -2.7 % | 1391 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-taif-bisha` |
| 12 | S2-trunk_gap-buraidah-hafar-al-batin | 0.00 / 0.02 / 0.08 | 0.03 / 0.07 / 0.16 | -81.5 / -32.7 / -22.0 | -11.7 % / -6.6 % / -2.6 % | 1571 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-buraidah-hafar-al-batin` |
| 13 | S2-trunk_gap-buraidah-ha-il | -0.00 / 0.02 / 0.07 | 0.03 / 0.09 / 0.20 | -58.3 / -25.4 / -17.6 | -12.3 % / -7.3 % / -2.9 % | 1629 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-buraidah-ha-il` |
| 14 | S2-trunk_gap-riyadh-bisha | -0.00 / 0.02 / 0.06 | 0.02 / 0.05 / 0.11 | -154.9 / -65.4 / -44.9 | -12.2 % / -7.1 % / -2.8 % | 1570 % | > 20.0 | `runs/cba/CBA-S2-trunk_gap-riyadh-bisha` |
| 15 | S2-trunk_gap-abha-khamis-mushait-bisha | -0.00 / 0.01 / 0.04 | 0.01 / 0.04 / 0.10 | -62.7 / -24.7 / -16.6 | -10.6 % / -6.1 % / -2.6 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-abha-khamis-mushait-bisha` |
| 16 | S2-trunk_gap-ar-rass-ha-il | -0.00 / 0.01 / 0.04 | 0.02 / 0.05 / 0.12 | -58.6 / -25.7 / -18.0 | -12.8 % / -7.7 % / -3.0 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-ar-rass-ha-il` |
| 17 | S2-trunk_gap-abha-khamis-mushait-najran | -0.00 / 0.01 / 0.04 | 0.01 / 0.04 / 0.11 | -115.8 / -39.4 / -24.6 | -7.9 % / -4.5 % / -2.1 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-abha-khamis-mushait-najran` |
| 18 | S2-trunk_gap-jazan-najran | -0.00 / 0.01 / 0.03 | 0.00 / 0.02 / 0.05 | -267.5 / -73.9 / -40.0 | -4.0 % / -2.6 % / -1.7 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-jazan-najran` |
| 19 | S2-trunk_gap-arar-hafar-al-batin | -0.01 / 0.01 / 0.03 | 0.00 / 0.02 / 0.05 | -113.0 / -50.8 / -36.0 | -13.6 % / -8.2 % / -3.1 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-arar-hafar-al-batin` |
| 20 | S2-trunk_gap-tabuk-sakaka | -0.01 / 0.00 / 0.03 | -0.00 / 0.01 / 0.04 | -95.2 / -42.1 / -29.8 | -13.4 % / -8.0 % / -3.1 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-tabuk-sakaka` |
| 21 | S2-trunk_gap-tabuk-yanbu | -0.01 / 0.00 / 0.02 | -0.00 / 0.01 / 0.03 | -155.4 / -62.2 / -42.3 | -11.5 % / -6.6 % / -2.7 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-tabuk-yanbu` |
| 22 | S2-trunk_gap-sakaka-ha-il | -0.01 / 0.00 / 0.02 | -0.00 / 0.01 / 0.03 | -100.0 / -38.9 / -26.3 | -12.6 % / -7.0 % / -2.7 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-sakaka-ha-il` |
| 23 | S2-trunk_gap-al-kharj-bisha | -0.02 / -0.01 / -0.00 | -0.02 / -0.00 / 0.00 | -152.6 / -70.2 / -50.5 | -14.9 % / -9.0 % / -3.3 % | > 20.0 | > 20.0 | `runs/cba/CBA-S2-trunk_gap-al-kharj-bisha` |

#### S3 branches and spurs (19 cases)

| rank | case | BCR P10 / P50 / P90 | BCR with WEIs P10 / P50 / P90 | NPV SAR bn P10 / P50 / P90 | EIRR P10 / P50 / P90 | demand for BCR = 1 | capex × for BCR = 1 | run |
|---|---|---|---|---|---|---|---|---|
| 1 | S3-branch_spur-al-kharj | 0.26 / 0.99 / 3.64 | 1.19 / 3.33 / 8.62 | -18.1 / -0.2 / 20.8 | -1.3 % / 2.7 % / 8.7 % | 66 % | 1.09 | `runs/cba/CBA-S3-branch_spur-al-kharj` |
| 2 | S3-branch_spur-al-jubayl | 0.16 / 0.55 / 1.62 | 2.10 / 5.59 / 12.75 | -18.3 / -4.5 / 5.0 | -2.5 % / 0.5 % / 5.2 % | 111 % | 0.32 | `runs/cba/CBA-S3-branch_spur-al-jubayl` |
| 3 | S3-branch_spur-duruma | 0.03 / 0.13 / 0.39 | 1.25 / 3.64 / 8.84 | -28.5 / -9.1 / -4.5 | -4.7 % / -2.3 % / -0.6 % | 427 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-duruma` |
| 4 | S3-branch_spur-ar-rass | 0.03 / 0.12 / 0.36 | 0.44 / 1.13 / 2.52 | -24.2 / -9.0 / -5.0 | -7.0 % / -3.5 % / -1.5 % | 471 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-ar-rass` |
| 5 | S3-branch_spur-at-ta-if | 0.03 / 0.12 / 0.37 | 0.29 / 0.90 / 2.18 | -79.8 / -22.9 / -10.6 | -3.7 % / -1.9 % / -0.5 % | 470 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-at-ta-if` |
| 6 | S3-branch_spur-sakaka | 0.02 / 0.09 / 0.26 | 0.09 / 0.25 / 0.53 | -18.2 / -6.7 / -4.0 | -6.9 % / -3.8 % / -1.9 % | 675 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-sakaka` |
| 7 | S3-branch_spur-yanbu-al-sina-iyah-yanbu-ind | 0.01 / 0.06 / 0.19 | 0.04 / 0.13 / 0.30 | -77.5 / -26.2 / -15.3 | -6.4 % / -3.5 % / -1.8 % | 770 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-yanbu-al-sina-iyah-yanbu-ind` |
| 8 | S3-branch_spur-badr-hunayn | 0.01 / 0.06 / 0.18 | 0.05 / 0.15 / 0.35 | -60.5 / -19.4 / -11.0 | -5.5 % / -3.1 % / -1.7 % | 841 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-badr-hunayn` |
| 9 | S3-branch_spur-hafar-al-batin | 0.00 / 0.03 / 0.10 | 0.03 / 0.08 / 0.18 | -52.9 / -22.6 / -15.3 | -11.0 % / -6.5 % / -2.8 % | 1175 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-hafar-al-batin` |
| 10 | S3-branch_spur-khaybar | 0.00 / 0.03 / 0.09 | 0.03 / 0.10 / 0.22 | -47.6 / -17.3 / -11.0 | -8.3 % / -4.8 % / -2.3 % | 1477 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-khaybar` |
| 11 | S3-branch_spur-rumah | 0.00 / 0.02 / 0.08 | 0.26 / 0.68 / 1.56 | -26.1 / -10.7 / -7.2 | -9.9 % / -6.0 % / -2.6 % | 1617 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-rumah` |
| 12 | S3-branch_spur-az-zulfi | -0.00 / 0.02 / 0.06 | 0.20 / 0.52 / 1.20 | -22.0 / -8.8 / -5.9 | -9.6 % / -5.9 % / -2.6 % | > 20.0 | > 20.0 | `runs/cba/CBA-S3-branch_spur-az-zulfi` |
| 13 | S3-branch_spur-bisha | -0.00 / 0.02 / 0.06 | 0.01 / 0.04 / 0.11 | -62.6 / -27.1 / -18.7 | -11.9 % / -7.1 % / -2.9 % | 1554 % | > 20.0 | `runs/cba/CBA-S3-branch_spur-bisha` |
| 14 | S3-branch_spur-arar | -0.00 / 0.01 / 0.06 | 0.01 / 0.03 / 0.08 | -44.0 / -18.7 / -12.9 | -11.6 % / -7.0 % / -2.9 % | > 20.0 | > 20.0 | `runs/cba/CBA-S3-branch_spur-arar` |
| 15 | S3-branch_spur-al-ula | -0.00 / 0.01 / 0.04 | 0.01 / 0.03 / 0.08 | -95.5 / -35.1 / -22.9 | -9.2 % / -5.3 % / -2.4 % | > 20.0 | > 20.0 | `runs/cba/CBA-S3-branch_spur-al-ula` |
| 16 | S3-branch_spur-rabigh | -0.00 / 0.01 / 0.04 | 0.02 / 0.06 / 0.14 | -16.0 / -6.3 / -4.2 | -8.8 % / -5.7 % / -2.5 % | > 20.0 | > 20.0 | `runs/cba/CBA-S3-branch_spur-rabigh` |
| 17 | S3-branch_spur-rafha | -0.01 / -0.00 / 0.01 | -0.01 / 0.00 / 0.02 | -65.8 / -27.3 / -18.9 | -12.8 % / -7.5 % / -2.9 % | > 20.0 | > 20.0 | `runs/cba/CBA-S3-branch_spur-rafha` |
| 18 | S3-branch_spur-hawtat-sudayr | -0.01 / -0.00 / 0.01 | 0.05 / 0.13 / 0.32 | -31.4 / -12.6 / -8.6 | -10.4 % / -6.4 % / -2.7 % | > 20.0 | > 20.0 | `runs/cba/CBA-S3-branch_spur-hawtat-sudayr` |
| 19 | S3-branch_spur-tayma | -0.02 / -0.01 / -0.00 | -0.02 / -0.01 / 0.00 | -63.8 / -26.5 / -18.4 | -12.9 % / -7.6 % / -2.9 % | > 20.0 | > 20.0 | `runs/cba/CBA-S3-branch_spur-tayma` |

#### S4 commuter belts (20 cases)

| rank | case | BCR P10 / P50 / P90 | BCR with WEIs P10 / P50 / P90 | NPV SAR bn P10 / P50 / P90 | EIRR P10 / P50 / P90 | demand for BCR = 1 | capex × for BCR = 1 | run |
|---|---|---|---|---|---|---|---|---|
| 1 | S4-commuter_belt-dammam-khobar-dhahran-315 | 0.11 / 0.38 / 1.00 | 1.98 / 4.29 / 8.87 | -24.3 / -11.3 / -0.1 | -15.0 % / -3.1 % / 2.8 % | 161 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-dammam-khobar-dhahran-315` |
| 2 | S4-commuter_belt-jazan-090 | 0.11 / 0.36 / 0.94 | 0.75 / 1.61 / 3.18 | -16.8 / -7.8 / -0.7 | -14.5 % / -3.3 % / 2.3 % | 170 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-jazan-090` |
| 3 | S4-commuter_belt-makkah-045 | 0.05 / 0.19 / 0.54 | 0.58 / 1.51 / 3.35 | -60.5 / -21.2 / -9.6 | -9.1 % / -3.2 % / -0.4 % | 309 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-makkah-045` |
| 4 | S4-commuter_belt-buraidah-180 | 0.05 / 0.17 / 0.46 | 0.81 / 1.74 / 3.54 | -23.1 / -12.3 / -7.0 | -22.6 % / -9.5 % / -2.6 % | 349 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-buraidah-180` |
| 5 | S4-commuter_belt-jazan-315 | 0.04 / 0.15 / 0.41 | 0.34 / 0.72 / 1.43 | -20.6 / -10.9 / -6.5 | -21.8 % / -9.4 % / -2.8 % | 370 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-jazan-315` |
| 6 | S4-commuter_belt-riyadh-225 | 0.03 / 0.13 / 0.36 | 2.88 / 6.88 / 15.19 | -34.8 / -16.0 / -9.6 | -17.3 % / -7.3 % / -2.4 % | 422 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-riyadh-225` |
| 7 | S4-commuter_belt-makkah-090 | 0.03 / 0.12 / 0.35 | 0.38 / 0.95 / 2.06 | -69.8 / -26.8 / -15.4 | -12.5 % / -5.1 % / -1.9 % | 436 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-makkah-090` |
| 8 | S4-commuter_belt-dammam-khobar-dhahran-180 | 0.00 / 0.05 / 0.16 | 0.18 / 0.40 / 0.80 | -49.5 / -28.7 / -20.7 | -31.4 % / -16.8 % / -5.4 % | 788 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-dammam-khobar-dhahran-180` |
| 9 | S4-commuter_belt-abha-khamis-mushait-135 | 0.01 / 0.04 / 0.15 | 0.05 / 0.17 / 0.38 | -121.6 / -38.3 / -22.3 | -8.1 % / -3.9 % / -2.0 % | 1027 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-abha-khamis-mushait-135` |
| 10 | S4-commuter_belt-riyadh-270 | 0.00 / 0.04 / 0.13 | 0.54 / 1.19 / 2.50 | -41.5 / -24.1 / -17.6 | -32.2 % / -17.5 % / -5.6 % | 950 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-riyadh-270` |
| 11 | S4-commuter_belt-riyadh-135 | 0.00 / 0.04 / 0.13 | 0.60 / 1.34 / 2.83 | -33.1 / -18.8 / -13.7 | -30.8 % / -16.8 % / -5.3 % | 996 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-riyadh-135` |
| 12 | S4-commuter_belt-madinah-225 | 0.00 / 0.04 / 0.13 | 0.03 / 0.09 / 0.20 | -71.4 / -31.5 / -21.8 | -20.0 % / -9.8 % / -3.3 % | 1076 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-madinah-225` |
| 13 | S4-commuter_belt-riyadh-090 | -0.00 / 0.04 / 0.12 | 0.71 / 1.59 / 3.40 | -28.2 / -15.7 / -11.5 | -29.5 % / -16.0 % / -5.1 % | 1071 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-riyadh-090` |
| 14 | S4-commuter_belt-madinah-045 | -0.00 / 0.03 / 0.09 | 0.05 / 0.12 / 0.25 | -35.9 / -21.2 / -15.9 | -34.6 % / -19.3 % / -6.1 % | 1364 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-madinah-045` |
| 15 | S4-commuter_belt-buraidah-090 | -0.01 / 0.01 / 0.06 | 0.21 / 0.48 / 1.01 | -34.9 / -19.6 / -14.7 | -34.0 % / -18.7 % / -5.7 % | 1802 % | > 20.0 | `runs/cba/CBA-S4-commuter_belt-buraidah-090` |
| 16 | S4-commuter_belt-abha-khamis-mushait-045 | -0.01 / 0.00 / 0.04 | 0.04 / 0.11 / 0.23 | -35.0 / -19.3 / -14.5 | -32.0 % / -17.7 % / -5.4 % | > 20.0 | > 20.0 | `runs/cba/CBA-S4-commuter_belt-abha-khamis-mushait-045` |
| 17 | S4-commuter_belt-jeddah-000 | -0.02 / 0.00 / 0.03 | 0.07 / 0.16 / 0.35 | -29.4 / -16.8 / -12.7 | -33.8 % / -19.2 % / -5.9 % | > 20.0 | > 20.0 | `runs/cba/CBA-S4-commuter_belt-jeddah-000` |
| 18 | S4-commuter_belt-riyadh-000 | -0.02 / 0.00 / 0.03 | 0.19 / 0.44 / 0.93 | -40.6 / -24.5 / -18.8 | -38.0 % / -21.7 % / -6.7 % | > 20.0 | > 20.0 | `runs/cba/CBA-S4-commuter_belt-riyadh-000` |
| 19 | S4-commuter_belt-makkah-315 | -0.02 / -0.00 / 0.02 | 0.03 / 0.08 / 0.18 | -40.2 / -22.4 / -17.0 | -33.1 % / -18.3 % / -5.5 % | > 20.0 | > 20.0 | `runs/cba/CBA-S4-commuter_belt-makkah-315` |
| 20 | S4-commuter_belt-jeddah-315 | -0.02 / -0.01 / 0.01 | 0.02 / 0.05 / 0.12 | -31.5 / -18.2 / -14.0 | -35.5 % / -20.3 % / -6.2 % | > 20.0 | > 20.0 | `runs/cba/CBA-S4-commuter_belt-jeddah-315` |

#### S5 station additions (11 cases)

| rank | case | BCR P10 / P50 / P90 | BCR with WEIs P10 / P50 / P90 | NPV SAR bn P10 / P50 / P90 | EIRR P10 / P50 / P90 | demand for BCR = 1 | capex × for BCR = 1 | run |
|---|---|---|---|---|---|---|---|---|
| 1 | S5-station_addition-al-jubayl | 3.47 / 45.12 / ∞ | 48.84 / 499.38 / ∞ | 1.6 / 6.0 / 14.4 | 7.6 % / 17.3 % / 32.8 % | 6 % | 15.29 | `runs/cba/CBA-S5-station_addition-al-jubayl` |
| 2 | S5-station_addition-al-jubayl-royal-commission | 2.40 / 20.31 / ∞ | 31.34 / 220.84 / ∞ | 1.0 / 4.2 / 10.4 | 6.1 % / 14.6 % / 28.3 % | 9 % | 11.13 | `runs/cba/CBA-S5-station_addition-al-jubayl-royal-commission` |
| 3 | S5-station_addition-jubail-two-stations | 1.50 / 7.74 / ∞ | 19.42 / 84.86 / ∞ | 0.7 / 5.2 / 13.6 | 4.3 % / 11.6 % / 23.1 % | 13 % | 7.39 | `runs/cba/CBA-S5-station_addition-jubail-two-stations` |
| 4 | S5-station_addition-dhahran | 1.06 / 3.58 / 9.27 | 11.96 / 32.73 / 74.14 | 0.0 / 1.8 / 5.0 | 3.0 % / 9.7 % / 19.7 % | 17 % | 5.43 | `runs/cba/CBA-S5-station_addition-dhahran` |
| 5 | S5-station_addition-duruma | 0.39 / 1.18 / 2.71 | 21.02 / 54.43 / 127.86 | -0.8 / 0.1 / 1.5 | -1.4 % / 3.7 % / 10.3 % | 52 % | 1.46 | `runs/cba/CBA-S5-station_addition-duruma` |
| 6 | S5-station_addition-az-zulfi | 0.03 / 0.12 / 0.35 | 0.74 / 2.18 / 5.25 | -1.6 / -0.5 / -0.3 | n/a / n/a / -2.6 % | 561 % | > 20.0 | `runs/cba/CBA-S5-station_addition-az-zulfi` |
| 7 | S5-station_addition-thuwal | -0.19 / -0.07 / -0.02 | -0.27 / -0.12 / -0.05 | -10.1 / -4.1 / -2.7 | n/a / n/a / n/a | > 20.0 | > 20.0 | `runs/cba/CBA-S5-station_addition-thuwal` |
| 8 | S5-station_addition-al-qarah | -1.44 / -0.58 / -0.18 | -4.21 / -2.05 / -0.78 | -2.4 / -1.2 / -0.7 | n/a / n/a / n/a | > 20.0 | > 20.0 | `runs/cba/CBA-S5-station_addition-al-qarah` |
| 9 | S5-station_addition-al-jarn | -1.44 / -0.58 / -0.18 | -4.21 / -2.05 / -0.78 | -2.4 / -1.2 / -0.7 | n/a / n/a / n/a | > 20.0 | > 20.0 | `runs/cba/CBA-S5-station_addition-al-jarn` |
| 10 | S5-station_addition-al-oyun | -1.44 / -0.58 / -0.18 | -4.21 / -2.05 / -0.78 | -2.4 / -1.2 / -0.7 | n/a / n/a / n/a | > 20.0 | > 20.0 | `runs/cba/CBA-S5-station_addition-al-oyun` |
| 11 | S5-station_addition-al-umran | -1.44 / -0.58 / -0.18 | -4.21 / -2.05 / -0.78 | -2.4 / -1.2 / -0.7 | n/a / n/a / n/a | > 20.0 | > 20.0 | `runs/cba/CBA-S5-station_addition-al-umran` |

#### S1 committed programme (vs S0) (1 cases)

| rank | case | BCR P10 / P50 / P90 | BCR with WEIs P10 / P50 / P90 | NPV SAR bn P10 / P50 / P90 | EIRR P10 / P50 / P90 | demand for BCR = 1 | capex × for BCR = 1 | run |
|---|---|---|---|---|---|---|---|---|
| 1 | S1-committed-programme | 0.07 / 0.31 / 1.26 | 0.25 / 0.98 / 2.97 | -337.6 / -60.1 / 11.6 | -1.4 % / 0.0 % / 3.4 % | 163 % | 0.26 | `runs/cba/CBA-S1-committed-programme` |

#### P50 BCR range across cases, by horizon, rate case and population scenario

Each cell: lowest and highest case P50 BCR (without WEIs) in the family, and the number of cases whose P50 BCR is at least 1. Ranges, not points.

| family | population | horizon | Green Book 2026 | TAG declining | 5 % | 7 % | drawn rate |
|---|---|---|---|---|---|---|---|
| trunk_gap | un_wpp_low | 30 | -0.01–0.15 (0/23) | -0.01–0.13 (0/23) | -0.01–0.10 (0/23) | -0.01–0.07 (0/23) | -0.01–0.14 (0/23) |
| trunk_gap | un_wpp_low | 40 | -0.01–0.16 (0/23) | -0.01–0.14 (0/23) | -0.01–0.10 (0/23) | -0.01–0.07 (0/23) | -0.01–0.15 (0/23) |
| trunk_gap | un_wpp_low | 60 | -0.01–0.22 (0/23) | -0.01–0.19 (0/23) | -0.01–0.12 (0/23) | -0.01–0.08 (0/23) | -0.01–0.20 (0/23) |
| trunk_gap | un_wpp_medium | 30 | -0.01–0.16 (0/23) | -0.01–0.15 (0/23) | -0.01–0.11 (0/23) | -0.01–0.07 (0/23) | -0.01–0.15 (0/23) |
| trunk_gap | un_wpp_medium | 40 | -0.01–0.17 (0/23) | -0.01–0.16 (0/23) | -0.01–0.11 (0/23) | -0.01–0.08 (0/23) | -0.01–0.16 (0/23) |
| trunk_gap | un_wpp_medium | 60 | -0.01–0.24 (0/23) | -0.01–0.21 (0/23) | -0.01–0.13 (0/23) | -0.01–0.08 (0/23) | -0.01–0.22 (0/23) |
| trunk_gap | un_wpp_high | 30 | -0.01–0.18 (0/23) | -0.01–0.16 (0/23) | -0.01–0.12 (0/23) | -0.01–0.08 (0/23) | -0.01–0.17 (0/23) |
| trunk_gap | un_wpp_high | 40 | -0.01–0.19 (0/23) | -0.01–0.17 (0/23) | -0.01–0.12 (0/23) | -0.01–0.08 (0/23) | -0.01–0.18 (0/23) |
| trunk_gap | un_wpp_high | 60 | -0.01–0.27 (0/23) | -0.01–0.23 (0/23) | -0.01–0.15 (0/23) | -0.01–0.09 (0/23) | -0.01–0.25 (0/23) |
| branch_spur | un_wpp_low | 30 | -0.01–0.65 (0/19) | -0.01–0.59 (0/19) | -0.01–0.45 (0/19) | -0.01–0.33 (0/19) | -0.01–0.62 (0/19) |
| branch_spur | un_wpp_low | 40 | -0.01–0.67 (0/19) | -0.01–0.61 (0/19) | -0.01–0.46 (0/19) | -0.01–0.34 (0/19) | -0.01–0.64 (0/19) |
| branch_spur | un_wpp_low | 60 | -0.01–0.89 (0/19) | -0.01–0.78 (0/19) | -0.01–0.54 (0/19) | -0.01–0.36 (0/19) | -0.01–0.83 (0/19) |
| branch_spur | un_wpp_medium | 30 | -0.01–0.71 (0/19) | -0.01–0.65 (0/19) | -0.01–0.49 (0/19) | -0.01–0.35 (0/19) | -0.01–0.67 (0/19) |
| branch_spur | un_wpp_medium | 40 | -0.01–0.74 (0/19) | -0.01–0.68 (0/19) | -0.01–0.50 (0/19) | -0.00–0.36 (0/19) | -0.01–0.70 (0/19) |
| branch_spur | un_wpp_medium | 60 | -0.01–0.99 (0/19) | -0.01–0.87 (0/19) | -0.01–0.59 (0/19) | -0.01–0.39 (0/19) | -0.01–0.92 (0/19) |
| branch_spur | un_wpp_high | 30 | -0.01–0.77 (0/19) | -0.01–0.70 (0/19) | -0.01–0.53 (0/19) | -0.01–0.38 (0/19) | -0.01–0.73 (0/19) |
| branch_spur | un_wpp_high | 40 | -0.01–0.81 (0/19) | -0.01–0.74 (0/19) | -0.01–0.55 (0/19) | -0.00–0.39 (0/19) | -0.01–0.77 (0/19) |
| branch_spur | un_wpp_high | 60 | -0.01–1.09 (1/19) | -0.01–0.96 (0/19) | -0.01–0.64 (0/19) | -0.00–0.43 (0/19) | -0.01–1.01 (1/19) |
| commuter_belt | un_wpp_low | 30 | -0.01–0.27 (0/20) | -0.01–0.25 (0/20) | -0.01–0.21 (0/20) | -0.01–0.17 (0/20) | -0.01–0.26 (0/20) |
| commuter_belt | un_wpp_low | 40 | -0.01–0.28 (0/20) | -0.01–0.26 (0/20) | -0.01–0.22 (0/20) | -0.01–0.17 (0/20) | -0.01–0.27 (0/20) |
| commuter_belt | un_wpp_low | 60 | -0.01–0.34 (0/20) | -0.01–0.32 (0/20) | -0.01–0.25 (0/20) | -0.01–0.18 (0/20) | -0.01–0.33 (0/20) |
| commuter_belt | un_wpp_medium | 30 | -0.01–0.29 (0/20) | -0.01–0.27 (0/20) | -0.01–0.23 (0/20) | -0.01–0.18 (0/20) | -0.01–0.28 (0/20) |
| commuter_belt | un_wpp_medium | 40 | -0.01–0.31 (0/20) | -0.01–0.29 (0/20) | -0.01–0.24 (0/20) | -0.01–0.19 (0/20) | -0.01–0.30 (0/20) |
| commuter_belt | un_wpp_medium | 60 | -0.01–0.38 (0/20) | -0.01–0.35 (0/20) | -0.01–0.27 (0/20) | -0.01–0.20 (0/20) | -0.01–0.36 (0/20) |
| commuter_belt | un_wpp_high | 30 | -0.01–0.31 (0/20) | -0.01–0.30 (0/20) | -0.01–0.25 (0/20) | -0.01–0.19 (0/20) | -0.01–0.30 (0/20) |
| commuter_belt | un_wpp_high | 40 | -0.01–0.34 (0/20) | -0.01–0.31 (0/20) | -0.01–0.26 (0/20) | -0.01–0.20 (0/20) | -0.01–0.32 (0/20) |
| commuter_belt | un_wpp_high | 60 | -0.01–0.42 (0/20) | -0.01–0.38 (0/20) | -0.01–0.29 (0/20) | -0.01–0.22 (0/20) | -0.01–0.40 (0/20) |
| station_addition | un_wpp_low | 30 | -0.39–14.15 (4/11) | -0.36–11.78 (4/11) | -0.28–7.29 (4/11) | -0.21–4.50 (4/11) | -0.37–12.76 (4/11) |
| station_addition | un_wpp_low | 40 | -0.43–17.72 (4/11) | -0.40–14.42 (4/11) | -0.30–8.40 (4/11) | -0.22–4.98 (4/11) | -0.41–15.92 (4/11) |
| station_addition | un_wpp_low | 60 | -0.54–31.86 (5/11) | -0.48–22.56 (5/11) | -0.35–10.44 (4/11) | -0.24–5.52 (4/11) | -0.51–26.06 (5/11) |
| station_addition | un_wpp_medium | 30 | -0.41–17.01 (4/11) | -0.38–13.82 (4/11) | -0.30–8.27 (4/11) | -0.22–4.98 (4/11) | -0.39–15.15 (4/11) |
| station_addition | un_wpp_medium | 40 | -0.46–22.16 (4/11) | -0.43–17.46 (4/11) | -0.33–9.69 (4/11) | -0.24–5.54 (4/11) | -0.44–19.50 (4/11) |
| station_addition | un_wpp_medium | 60 | -0.58–45.12 (5/11) | -0.52–29.58 (5/11) | -0.37–12.22 (4/11) | -0.26–6.18 (4/11) | -0.55–35.21 (5/11) |
| station_addition | un_wpp_high | 30 | -0.44–20.57 (4/11) | -0.41–16.32 (4/11) | -0.32–9.37 (4/11) | -0.24–5.49 (4/11) | -0.42–18.08 (4/11) |
| station_addition | un_wpp_high | 40 | -0.50–28.48 (5/11) | -0.46–21.45 (4/11) | -0.35–11.13 (4/11) | -0.25–6.15 (4/11) | -0.47–24.33 (4/11) |
| station_addition | un_wpp_high | 60 | -0.63–71.23 (5/11) | -0.56–40.16 (5/11) | -0.40–14.38 (4/11) | -0.28–6.93 (4/11) | -0.59–50.86 (5/11) |
| committed_programme | un_wpp_low | 30 | 0.19–0.19 (0/1) | 0.17–0.17 (0/1) | 0.12–0.12 (0/1) | 0.09–0.09 (0/1) | 0.18–0.18 (0/1) |
| committed_programme | un_wpp_low | 40 | 0.21–0.21 (0/1) | 0.19–0.19 (0/1) | 0.13–0.13 (0/1) | 0.09–0.09 (0/1) | 0.20–0.20 (0/1) |
| committed_programme | un_wpp_low | 60 | 0.28–0.28 (0/1) | 0.24–0.24 (0/1) | 0.15–0.15 (0/1) | 0.10–0.10 (0/1) | 0.25–0.25 (0/1) |
| committed_programme | un_wpp_medium | 30 | 0.21–0.21 (0/1) | 0.19–0.19 (0/1) | 0.13–0.13 (0/1) | 0.09–0.09 (0/1) | 0.20–0.20 (0/1) |
| committed_programme | un_wpp_medium | 40 | 0.23–0.23 (0/1) | 0.20–0.20 (0/1) | 0.14–0.14 (0/1) | 0.10–0.10 (0/1) | 0.22–0.22 (0/1) |
| committed_programme | un_wpp_medium | 60 | 0.31–0.31 (0/1) | 0.26–0.26 (0/1) | 0.17–0.17 (0/1) | 0.11–0.11 (0/1) | 0.28–0.28 (0/1) |
| committed_programme | un_wpp_high | 30 | 0.23–0.23 (0/1) | 0.20–0.20 (0/1) | 0.14–0.14 (0/1) | 0.10–0.10 (0/1) | 0.21–0.21 (0/1) |
| committed_programme | un_wpp_high | 40 | 0.25–0.25 (0/1) | 0.22–0.22 (0/1) | 0.16–0.16 (0/1) | 0.11–0.11 (0/1) | 0.24–0.24 (0/1) |
| committed_programme | un_wpp_high | 60 | 0.34–0.34 (0/1) | 0.29–0.29 (0/1) | 0.18–0.18 (0/1) | 0.11–0.11 (0/1) | 0.31–0.31 (0/1) |

#### Fiscal cost, FIRR and payback (same ranking basis)

| case | fiscal cost to the state SAR bn P10 / P50 / P90 | FIRR P10 / P50 / P90 | payback years after opening P10 / P50 / P90 | opening year P10 / P50 / P90 |
|---|---|---|---|---|
| S2-trunk_gap-riyadh-dammam-khobar-dhahran | 36.6 / 60.9 / 164.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,034 / 2,037 / 2,045 |
| S2-trunk_gap-riyadh-hafar-al-batin | 31.0 / 44.8 / 105.1 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-madinah-ha-il | 27.2 / 38.8 / 90.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-riyadh-al-jubayl | 27.5 / 39.5 / 93.6 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-madinah-yanbu | 21.3 / 33.9 / 99.1 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-jeddah-yanbu | 22.0 / 31.5 / 73.0 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-madinah-ar-rass | 30.2 / 43.1 / 100.7 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-riyadh-jeddah | 88.6 / 136.8 / 354.3 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,034 / 2,037 / 2,045 |
| S2-trunk_gap-dammam-khobar-dhahran-al-kharj | 29.6 / 42.2 / 97.9 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-al-jubayl-hafar-al-batin | 27.1 / 38.5 / 88.7 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-taif-bisha | 21.1 / 30.6 / 74.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-buraidah-hafar-al-batin | 24.0 / 35.2 / 88.4 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-buraidah-ha-il | 19.1 / 27.3 / 63.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-riyadh-bisha | 48.5 / 69.9 / 167.3 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-abha-khamis-mushait-bisha | 17.7 / 26.3 / 67.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-ar-rass-ha-il | 19.1 / 27.3 / 63.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-abha-khamis-mushait-najran | 26.4 / 42.2 / 124.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-jazan-najran | 43.0 / 79.7 / 288.3 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-arar-hafar-al-batin | 37.8 / 53.5 / 121.3 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-tabuk-sakaka | 31.2 / 44.4 / 102.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-tabuk-yanbu | 44.4 / 65.6 / 166.7 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-sakaka-ha-il | 27.4 / 40.8 / 107.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S2-trunk_gap-al-kharj-bisha | 51.5 / 72.5 / 162.4 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-al-kharj | 7.3 / 12.8 / 35.0 | n/a / n/a / n/a | 12 / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-al-jubayl | 7.1 / 10.8 / 28.2 | n/a / n/a / n/a | 28 / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-duruma | 7.1 / 11.3 / 32.6 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-ar-rass | 7.5 / 11.1 / 27.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-at-ta-if | 16.6 / 28.1 / 90.4 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-sakaka | 5.3 / 7.9 / 20.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-yanbu-al-sina-iyah-yanbu-ind | 18.9 / 29.9 / 85.7 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-badr-hunayn | 13.6 / 22.0 / 66.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-hafar-al-batin | 17.1 / 24.5 / 57.7 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-khaybar | 12.3 / 18.9 / 51.6 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-rumah | 7.9 / 11.6 / 28.4 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-az-zulfi | 6.4 / 9.5 / 23.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-bisha | 20.2 / 28.9 / 67.6 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-arar | 13.9 / 19.9 / 47.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-al-ula | 24.4 / 37.5 / 102.9 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-rabigh | 4.5 / 6.7 / 17.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-rafha | 19.7 / 28.6 / 70.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-hawtat-sudayr | 8.9 / 13.2 / 33.6 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S3-branch_spur-tayma | 18.8 / 27.5 / 67.9 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-dammam-khobar-dhahran-315 | 14.3 / 18.8 / 34.1 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-jazan-090 | 9.5 / 12.6 / 23.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-makkah-045 | 19.1 / 28.0 / 71.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-buraidah-180 | 11.9 / 15.6 / 27.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-jazan-315 | 10.2 / 13.5 / 24.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-riyadh-225 | 14.1 / 19.3 / 40.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-makkah-090 | 22.6 / 32.5 / 79.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-dammam-khobar-dhahran-180 | 24.0 / 31.4 / 54.3 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-abha-khamis-mushait-135 | 26.2 / 42.8 / 132.4 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-riyadh-270 | 19.9 / 26.0 / 45.1 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-riyadh-135 | 15.4 / 20.2 / 36.0 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-madinah-225 | 24.6 / 34.3 / 77.4 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-riyadh-090 | 12.9 / 16.9 / 30.6 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-madinah-045 | 17.2 / 22.5 / 38.5 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-buraidah-090 | 15.6 / 20.5 / 37.0 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-abha-khamis-mushait-045 | 15.1 / 19.9 / 36.9 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-jeddah-000 | 13.1 / 17.3 / 30.9 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-riyadh-000 | 19.4 / 25.1 / 42.6 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-makkah-315 | 17.4 / 23.0 / 42.2 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S4-commuter_belt-jeddah-315 | 14.1 / 18.5 / 33.0 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S5-station_addition-al-jubayl | -0.5 / 0.1 / 1.1 | -4.9 % / 1.7 % / 7.0 % | 1 / 3 / 15 | 2,032 / 2,036 / 2,043 |
| S5-station_addition-al-jubayl-royal-commission | -0.3 / 0.2 / 1.2 | -9.3 % / 0.8 % / 5.9 % | 1 / 5 / 21 | 2,032 / 2,036 / 2,043 |
| S5-station_addition-jubail-two-stations | -0.0 / 0.7 / 2.8 | n/a / -2.1 % / 2.9 % | 2 / 7 / 34 | 2,032 / 2,036 / 2,043 |
| S5-station_addition-dhahran | 0.4 / 0.6 / 1.8 | n/a / n/a / n/a | 3 / 10 / 54 | 2,032 / 2,036 / 2,043 |
| S5-station_addition-duruma | 0.5 / 0.8 / 1.9 | n/a / n/a / n/a | 9 / 43 / ∞ | 2,032 / 2,036 / 2,043 |
| S5-station_addition-az-zulfi | 0.4 / 0.6 / 1.7 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S5-station_addition-thuwal | 2.4 / 3.7 / 9.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,034 / 2,037 / 2,045 |
| S5-station_addition-al-qarah | 0.4 / 0.7 / 1.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S5-station_addition-al-jarn | 0.4 / 0.7 / 1.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S5-station_addition-al-oyun | 0.4 / 0.7 / 1.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S5-station_addition-al-umran | 0.4 / 0.7 / 1.8 | n/a / n/a / n/a | ∞ / ∞ / ∞ | 2,032 / 2,036 / 2,043 |
| S1-committed-programme | 45.0 / 98.4 / 412.4 | n/a / n/a / -4.7 % | 49 / ∞ / ∞ | 2,032 / 2,036 / 2,043 |

FIRR '< −50 %' means no internal rate of return in the search bracket (fares do not recover the costs); payback '∞' means the discounted net flow is still negative at the horizon end.
<!-- END GENERATED RESULTS -->

## 10. Jubail: one shared S5 station or two (CP5 decision H8)

Both options are costed with the same method (station item × the same run's reference-class multipliers; two stations = twice the item) and appraised against S1. **Zone caveat:** both stations lie in the same model zone (G034, Al Jubayl governorate; `runs/r5/s5-zone-check/zones.csv`), so the model cannot credit the second station with any access its own catchment gains; it sees only its cost and the extra stop time. The recommendation below is therefore "in the model, at governorate zone resolution"; a finer zoning of Jubail (R6 or later) is needed before it is treated as more than that.

<!-- BEGIN GENERATED JUBAIL -->
| option | BCR P10 / P50 / P90 | NPV SAR bn P10 / P50 / P90 | PV capex SAR bn P10 / P50 / P90 | EIRR P10 / P50 / P90 |
|---|---|---|---|---|
| one station: Al Jubayl | 3.47 / 45.12 / ∞ | 1.60 / 6.00 / 14.44 | 0.23 / 0.41 / 1.49 | 7.6 % / 17.3 % / 32.8 % |
| one station: Jubail Industrial City (Royal Commission) | 2.40 / 20.31 / ∞ | 0.95 / 4.21 / 10.35 | 0.23 / 0.41 / 1.49 | 6.1 % / 14.6 % / 28.3 % |
| two stations | 1.50 / 7.74 / ∞ | 0.71 / 5.20 / 13.64 | 0.46 / 0.81 / 2.98 | 4.3 % / 11.6 % / 23.1 % |

In the model (medium population, 60 years, Green Book 2026), NPV of two stations minus the better single station (S5-station_addition-al-jubayl), paired by draw: SAR bn -1.73 / -0.63 / -0.40 (P10 / P50 / P90; 100 % of draws negative). **Recommendation (in the model): one shared station**, because the second station lowers NPV in most draws and adds no reach.

Accessibility gain (in the model): population within each in-vehicle band of the Dammam–Khobar–Dhahran main station, S1 plus the option (`runs/r5/jubail-iso/`):

| option | 30 min | 45 min | 60 min | 90 min | 120 min |
|---|---|---|---|---|---|
| S1 (baseline) | 2,282,624 | 2,354,794 | 2,354,794 | 3,587,845 | 3,681,994 |
| Al Jubayl | 2,282,624 | 2,918,870 | 2,918,870 | 4,151,921 | 4,246,070 |
| Jubail Industrial City | 2,282,624 | 2,918,870 | 2,918,870 | 4,151,921 | 4,246,070 |
| two stations | 2,282,624 | 2,918,870 | 2,918,870 | 4,151,921 | 4,246,070 |
<!-- END GENERATED JUBAIL -->

## 11. Limits

- Demand is synthetic and uncalibrated beyond the 2025 totals marked `calibrated` in `docs/demand.md` §12; mode-choice coefficients are literature-based until the W7 survey is fielded. Results are scenario comparisons, not forecasts.
- Freight is not monetised (no open freight OD); mixed-line costs include freight-capable infrastructure, so those BCRs are lower bounds on the passenger case.
- International visitors carry no user benefits or fares in the CBA.
- Jeddah decongestion is zero (lower bound): no candidate is representable in the read-only TrafficTwin (CP5 H7c).
- WEIs are method-sensitive (§7).
- **Rail-graph fix in R5 (verify-R5 F3):** in the R4 rail graph an explicit `connects_to` interchange was free in the path search but billed as a geometric walk in the level of service, and fares were not part of the path choice. Adding a line could therefore lower the rail utility of existing pairs (e.g. Riyadh–Jeddah trunk: negative pilgrimage benefits). `access/railgraph.py` now reports the walk the search costed and includes fares (b_cost/b_ivt) in ride links (`tests/test_access_railgraph_r5.py`); every R5 run was repeated afterwards. After the fix, four belt/spur cases still lose fare revenue (fares in the path choice open cheaper paths on existing lines), and the non-S5 cases with a negative P50 BCR are driven by the added rail train-km (accident and grid-electricity costs) exceeding small road savings: a registered mechanism, not an artefact. Remaining pairs whose composite cost rises when a non-S5 line is added carry at most 0.05 % of trips (purpose-specific cost scaling; diagnostic `trips_cost_up` in `runs/cba/inputs/*/scalars.parquet`); for S5 the rise is the added stop.
- **S5 BCRs are ratios over a netted PVC.** PVC nets fare revenue and residual value from a small station capex, so it is near zero or negative in a large share of draws (BCR = ∞ there) and the BCR is fragile; read the S5 rows on NPV first.
- **Zone resolution of S5 station additions:** Al-Jarn, Al-Oyun, Al-Qarah and Al-Umran (Al-Ahsa oasis) lie in the same model zone as the existing Hufuf station (G033; `runs/r5/s5-zone-check/zones.csv`). The model therefore sees only the extra stop time for through passengers and the station's cost, not the access gain of the towns, and their four identical negative results are an artefact of zone size, not an appraisal of those stations. Both Jubail stations share zone G034 (§10).
- The HHR running-time gate stands at −12.2 % against the 29.0 min secondary reference, inside the accepted ±15 % until an official timetable exists (`docs/network-evaluation.md` §1, CP5 H1a).
