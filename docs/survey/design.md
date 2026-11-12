> **Document version:** docs/survey/design.md v0.1 | 31 Oct 2026 | Author: socio-culture-analyst B (R1d) | Status: draft

# Intercity stated-preference survey: design (designed, not fielded)

**Status: designed, not fielded.** No respondent has been contacted, no form has been created online, no pilot has been run (PROJECT.md rule 7). Every coefficient used anywhere in the model stays **literature-based until survey results exist** (`cities/ksa/assumptions/mode_choice_priors.yaml`). This document describes a survey that a human fielding institution may run after Tariq's approval and after ethics approval (section 9).

Files in this package:

| file | content |
|---|---|
| `docs/survey/design.md` | this file: purpose, hypotheses, attributes and levels, experimental design, sample design, fielding prerequisites |
| `docs/survey/design.yaml` | machine-readable design configuration (alternatives, attributes, levels, priors, citations) |
| `docs/survey/choice_sets.csv` (+ `.meta.json`) | generated choice tasks, D-error, level balance, sample-size lower bounds |
| `docs/survey/instrument.en.md`, `docs/survey/instrument.ar.md` | the questionnaire in English and in Arabic |
| `docs/survey/ethics-consent.md` | consent text (English and Arabic), PDPL and research-ethics notes |
| `docs/survey/analysis-plan.md` | estimation, WTP and value-of-time derivation, weighting, how results replace the priors |

Sources: `docs/sources/r1d-soc-survey.csv` (S-soc-3xx). Assumptions: `docs/assumptions.md` (A-social-1xx, A-mode-0xx).

## 1. Purpose

The W8 mode-choice model needs Saudi values for how intercity travellers trade travel time, fare, access, frequency, reliability and service features against each other, and how this differs by trip purpose, income, sex, nationality and region. No published Saudi intercity coefficients were obtained in this track: the Riyadh–Dammam stated-preference study (S-soc-307) and the KAU intercity mode-choice paper (S-soc-308) could not be read, and the one Saudi stated-preference model read in part is urban (Riyadh car vs Metro, S-soc-304, secondary). The priors are therefore transferred from European and worldwide meta-analyses (S-soc-300, S-soc-302, S-soc-303) and US guidance (S-soc-337, secondary).

The survey would:
1. estimate Saudi intercity mode-choice coefficients (car, rail, air, bus) to replace the transferred priors;
2. derive values of travel time (VoT) and willingness to pay (WTP) for access time, frequency, reliability, comfort, women-only or family carriages, prayer facilities, luggage and shaded or air-conditioned transfers, by purpose, income band, sex and region;
3. test the hypotheses in section 2, several of which concern cultural and climatic features for which **no published Saudi estimate was found**; these are hypotheses to test, not findings;
4. record revealed intercity trips (last 12 months) by mode and purpose, including people who do not travel intercity, so the equity analysis can see who is left out.

The survey is independent and non-partisan: it does not promote any operator, line, agency or policy, and the scenarios name no real or planned line.

## 2. Hypotheses

Each hypothesis is stated so that the estimated model can reject it. None is a claim about Saudi travellers; the priors that encode them (A-mode-0xx) are design priors only.

| id | hypothesis | parameter(s) and test | prior used in the design | evidence so far |
|---|---|---|---|---|
| H1 | A women-only or family carriage raises the utility of rail, more for women respondents and for parties travelling with family | `family_carriage[1]` > 0; interaction with sex and party type (Q-C3.6) | 0.2 (A-mode-015) | no published WTP estimate found |
| H2 | A shaded or air-conditioned walk and transfer at stations raises rail utility, more when the scenario is framed in summer (June–August) than in winter | `shaded_transfer[1]` > 0; interaction with the season framing (A-social-128) | 0.25 (A-mode-018) | conflicting: not significant in the worldwide meta-analysis (S-soc-301); a large walk-time disutility in one Riyadh sample (S-soc-304, secondary) |
| H3 | The value of in-vehicle time rises with household income and is higher for business than for non-work trips | ratio `ivt_*`/`cost` by income band and purpose segment | car VoT 46 SAR/h (A-mode-006) | international evidence on purpose and distance effects (S-soc-303, S-soc-305, S-soc-337 secondary); no Saudi intercity estimate |
| H4 | A prayer area on board or at stations raises rail utility | `prayer[1]` > 0; heterogeneity in the mixed logit | 0.2 (A-mode-016) | no published estimate found |
| H5 | Reliability is valued: a higher on-time share raises utility, consistent with a late-time multiplier above 1 | `on_time` > 0; implied late-time multiplier vs 2.67 (S-soc-302) | 0.007 per percentage point (A-mode-009) | European inter-urban meta-analysis (S-soc-302) |
| H6 | Access and egress time weighs more than in-vehicle time | `access`/`ivt_rail` > 1 vs 1.87 (S-soc-302) and 1.70 (S-soc-300) | −0.017 per min (A-mode-007) | meta-analyses (S-soc-300, S-soc-302) |
| H7 | A large-suitcase allowance is valued more on pilgrimage and visiting-family trips than on business trips | `luggage[1]` by purpose segment | 0.2 (A-mode-017) | no published estimate found |
| H8 | Respondents without a driving licence or without a household car available for the trip have a higher rail constant | `asc_rail` interaction with licence and car access (Q-F7, Q-F8) | ASC −0.2 (A-mode-010) | constants are not transferable (S-soc-337, secondary) |

## 3. Choice context, alternatives and the pivot rule

- **Context.** The respondent's own most recent intercity trip (Q-C3) of 150 km or more one way (A-social-135) between their home governorate and a named destination. The scenario names the origin and destination, never a line name.
- **Alternatives (labelled, in display order).** Car (own or household), train (new intercity service), domestic flight, intercity coach. Car is the reference alternative (ASC 0). Air is shown only where the respondent's pair has scheduled flights; availability is handled in estimation (section 5 of the analysis plan).
- **Reference trip and pivot rule (A-social-100).** The levels in `design.yaml` describe a reference trip of 400 km road distance. For a respondent whose trip has road distance D (valid range 150–600 km; outside it the nearest band edge is used), the fielding team multiplies every time and cost level by D/400 and rounds times to 5 min and costs to SAR 5. Headway, on-time share and the yes/no features are not scaled. This pivots the design around the respondent's own trip, following the reference-alternative design literature (S-soc-311). The road distance D comes from the origin and destination the respondent names; it is not asked.

## 4. Attributes and levels

All levels are for the 400 km reference trip before pivoting. Arabic labels are those in `design.yaml` (`label_ar`, `level_labels_ar`) and are used verbatim in `instrument.ar.md`.

| alternative | attribute (EN) | attribute (AR) | levels | unit | coding | parameter | prior | citation |
|---|---|---|---|---|---|---|---|---|
| car | Door-to-door driving time | مدة القيادة من الباب إلى الباب | 210 / 240 / 270 | min | linear | `ivt_car` | −0.010 | A-social-101, A-mode-001 |
| car | Fuel and parking cost for the car | تكلفة الوقود والمواقف للسيارة | 60 / 80 / 100 / 120 | SAR | linear | `cost` | −0.013 | A-social-102 (S-soc-316, S-soc-317), A-mode-005 |
| rail | Time on the train | مدة الرحلة على متن القطار | 90 / 150 / 210 | min | linear | `ivt_rail` | −0.009 | A-social-103, A-mode-002 |
| rail | Time to reach the station and from the station to your destination | مدة الوصول إلى المحطة ومن المحطة إلى وجهتك | 20 / 40 / 60 | min | linear | `access` | −0.017 | A-social-104, A-mode-007 |
| rail | Ticket price (one way, per person) | سعر التذكرة (ذهاب فقط، للشخص الواحد) | 60 / 100 / 140 / 180 | SAR | linear | `cost` | −0.013 | A-social-105 (S-soc-318, S-soc-321), A-mode-005 |
| rail | A train every | قطار كل | 30 / 60 / 120 | min | linear | `headway` | −0.004 | A-social-106, A-mode-008 |
| rail | Trips arriving on time | نسبة الرحلات التي تصل في موعدها | 80 / 95 | % | linear | `on_time` | 0.007 | A-social-107, A-mode-009 |
| rail | Class | الدرجة | Economy / Business | class | dummy | `comfort` | 0.4 | A-social-108, A-mode-014 |
| rail | Women-only or family carriage available | عربة مخصصة للنساء أو للعائلات | No / Yes | yes/no | dummy | `family_carriage` | 0.2 | A-social-109, A-mode-015 |
| rail | Prayer area on board or at the stations | مصلى في القطار أو في المحطات | No / Yes | yes/no | dummy | `prayer` | 0.2 | A-social-110, A-mode-016 |
| rail | Luggage included | الأمتعة المشمولة | Cabin bag only / Cabin bag + one large suitcase | allowance | dummy | `luggage` | 0.2 | A-social-111, A-mode-017 |
| rail | Shaded or air-conditioned walk and transfer at the stations | ممرات وانتقال مظللة أو مكيفة في المحطات | No / Yes | yes/no | dummy | `shaded_transfer` | 0.25 | A-social-112, A-mode-018 |
| air | Flight time | مدة الطيران | 55 / 70 / 85 | min | linear | `ivt_air` | −0.012 | A-social-113, A-mode-003 |
| air | Time to the airport, check-in and security, and from the airport to your destination | مدة الوصول إلى المطار وإجراءات السفر والتفتيش، ومن المطار إلى وجهتك | 60 / 90 / 120 | min | linear | `access` | −0.017 | A-social-114, A-mode-007 |
| air | Ticket price (one way, per person) | سعر التذكرة (ذهاب فقط، للشخص الواحد) | 180 / 260 / 340 / 420 | SAR | linear | `cost` | −0.013 | A-social-115 (S-soc-320, unverified), A-mode-005 |
| air | A flight every | رحلة كل | 60 / 120 / 240 | min | linear | `headway` | −0.004 | A-social-116, A-mode-008 |
| air | Flights arriving on time | نسبة الرحلات التي تصل في موعدها | 80 / 95 | % | linear | `on_time` | 0.007 | A-social-107, A-mode-009 |
| air | Luggage included | الأمتعة المشمولة | Cabin bag only / Cabin bag + one large suitcase | allowance | dummy | `luggage` | 0.2 | A-social-111, A-mode-017 |
| bus | Time on the coach | مدة الرحلة على متن الحافلة | 300 / 345 / 390 | min | linear | `ivt_bus` | −0.007 | A-social-117, A-mode-004 |
| bus | Time to reach the bus station and from the bus station to your destination | مدة الوصول إلى محطة الحافلات ومنها إلى وجهتك | 15 / 30 / 45 | min | linear | `access` | −0.017 | A-social-118, A-mode-007 |
| bus | Ticket price (one way, per person) | سعر التذكرة (ذهاب فقط، للشخص الواحد) | 60 / 80 / 100 / 120 | SAR | linear | `cost` | −0.013 | A-social-119 (S-soc-319), A-mode-005 |
| bus | A coach every | حافلة كل | 60 / 120 / 240 | min | linear | `headway` | −0.004 | A-social-116, A-mode-008 |
| bus | Class | الدرجة | Standard / VIP | class | dummy | `comfort` | 0.4 | A-social-108, A-mode-014 |

Alternative-specific constants: rail −0.2 (A-mode-010), air −0.2 (A-mode-011), bus −0.6 (A-mode-012). Cost, access, headway, on-time share, comfort and luggage are generic parameters (one value shared across the alternatives that carry them). The fare evidence behind the levels is mostly secondary or unverified (S-soc-318 to S-soc-321); the levels are deliberately wide because a wide level range improves design efficiency (S-soc-312), and each must be re-checked against a dated official fare sample before fielding (section 9).

Choices made about wording: the luggage levels avoid a kilogram figure that would need a source (A-social-111); "women-only or family carriage" is offered as a feature of a hypothetical service and makes no claim about current provision on any Saudi line (A-social-109).

## 5. Experimental design

**Method.** A D-efficient labelled design for the multinomial logit (MNL) with fixed literature priors (S-soc-309, S-soc-310), built by our own coordinate-exchange code (`demand/survey.py`, Apache-2.0; no proprietary design software). The D-error is det(I⁻¹)^(1/K), with I the MNL Fisher information of the design at the priors and K the number of parameters. The search starts from 10 level-balanced random designs, runs coordinate-exchange sweeps (at most 30) and keeps the best; tasks are then split into blocks with the least correlation between block and attribute levels, and one dominance-check task is appended to each block.

Command (deterministic, rule 10):

```
uv run python -m demand.survey design --config docs/survey/design.yaml --seed 1 --out docs/survey/choice_sets.csv
```

**Size (A-social-120).** 27 design tasks in 3 blocks: 9 design tasks + 1 dominance task = 10 tasks per respondent, inside the 8–12 range of the survey-design skill. 16 parameters (3 ASCs, 4 mode-specific in-vehicle time, cost, access, headway, on-time share, comfort, family carriage, prayer, luggage, shaded transfer).

**Measured properties** (from `docs/survey/choice_sets.csv.meta.json`, seed 1):

| property | value |
|---|---|
| D-error of the chosen design | 0.00785495 |
| D-error across the 10 starts | 0.00785495 (best) to 0.00791422 (worst) |
| parameters | 16 |
| tasks per respondent | 10 (9 design + 1 dominance) |
| rows in `choice_sets.csv` | 690 (3 blocks × 10 tasks × 23 attribute cells) |

**Level balance** (number of the 27 design tasks showing each level, in level order; same file):

| attribute | counts | attribute | counts |
|---|---|---|---|
| car.ivt | 10 / 0 / 17 | air.ivt | 15 / 0 / 12 |
| car.cost | 2 / 0 / 0 / 25 | air.access | 19 / 0 / 8 |
| rail.ivt | 10 / 0 / 17 | air.cost | 26 / 1 / 0 / 0 |
| rail.access | 9 / 0 / 18 | air.headway | 21 / 0 / 6 |
| rail.cost | 7 / 0 / 1 / 19 | air.reliability | 13 / 14 |
| rail.headway | 9 / 0 / 18 | air.luggage | 13 / 14 |
| rail.reliability | 14 / 13 | bus.ivt | 15 / 0 / 12 |
| rail.comfort | 15 / 12 | bus.access | 23 / 0 / 4 |
| rail.family_carriage | 14 / 13 | bus.cost | 22 / 0 / 0 / 5 |
| rail.prayer | 13 / 14 | bus.headway | 16 / 0 / 11 |
| rail.luggage | 14 / 13 | bus.comfort | 12 / 15 |
| rail.shaded_transfer | 14 / 13 | | |

**Reading the balance, and an open issue.** The two-level features are well balanced. The linear-coded time and cost attributes are not: the D-efficient search pushes them to their extreme levels, a known property of D-efficient designs with linear coding, so the middle levels almost never appear (for example car cost is SAR 120 in 25 of 27 tasks, and air fare is SAR 180 in 26 of 27). Consequences: (a) the design cannot test non-linear time or cost effects; (b) air-fare variation within the design is small, so the generic cost coefficient is identified mainly from car, rail and bus; (c) respondents see repeated values, which the pilot must check for plausibility and fatigue. **Before fielding**, the fielding team should either accept this with the pilot's evidence, or regenerate with a minimum-appearances constraint per level (not implemented in `demand/survey.py` v0.1) and report the D-error loss. This is recorded as an open item, not resolved here.

**Dominance task.** In each block, task 10 shows rail at its best level on every attribute (by the sign of its prior) and every other alternative at its worst. A respondent who does not choose rail in that task is handled by the rule A-social-132 (analysis plan, section 3). The check uses rail as the dominant option in all blocks; the pilot should confirm that respondents do not read it as an advertisement.

**Design efficiency is conditional on the priors.** If the priors are wrong, the design loses efficiency but stays usable. After the pilot (section 9), the priors can be updated with the pilot's MNL estimates and the design regenerated (a standard two-stage practice; S-soc-309).

## 6. Sample-size justification

Three published rules give lower bounds; the target (section 7) sits well above them so that segments and regions can be estimated.

1. **S-estimate (Ngene eq. 7.9; S-soc-313, S-soc-353).** N_k = (1.96 · se_k / β_k)², with se_k from the MNL covariance of one replicate of the full design at the priors; one replicate is answered by 3 respondents (one per block). Computed by the generator and stored in `docs/survey/choice_sets.csv.meta.json` (`s_estimate`). It is a lower bound that assumes the priors are true and choices independent (S-soc-353).

   | parameter | respondents (lower bound) | parameter | respondents (lower bound) |
   |---|---|---|---|
   | asc_air | 9,062.3 | family_carriage[1] | 189.7 |
   | asc_rail | 7,666.1 | luggage[1] | 88.5 |
   | asc_bus | 1,026.0 | ivt_air | 97.2 |
   | on_time | 308.5 | ivt_bus | 36.7 |
   | prayer[1] | 193.0 | ivt_car | 28.1 |
   | shaded_transfer[1] | 125.2 | comfort[1] | 26.0 |
   | headway | 12.5 | access | 9.0 |
   | ivt_rail | 8.8 | cost | 4.6 |

   The ASC bounds are large because their priors are close to zero; ASCs are not transferred and are recalibrated to observed shares in R3 (A-mode-010 to A-mode-012), so they are not the sizing criterion. Among the attribute parameters, the binding one is `on_time` (308.5 respondents); the feature parameters of H1 and H4 need about 190–193 respondents per segment in which they are to be estimated separately.
2. **CBC rules of thumb (S-soc-314).** At least 300 respondents overall and at least 200 per subgroup reported separately; and at least 500 appearances per level, n ≥ 500c/(t·a) with c = 4 (most levels of any attribute), t = 9 design tasks, a = 4 alternatives: n ≥ 2,000/36 = 55.6, so 56 respondents.
3. **Pretest (S-soc-315).** 30 participants is the published default for questionnaire pre-tests; the pilot here is 30–50 to cover both languages (A-social-125).

## 7. Sample design

**Target population (A-social-121).** Residents of Saudi Arabia aged 18 or over, Saudi and non-Saudi, in all 13 administrative regions (S-070). People with no intercity trip in the last 12 months are kept for the revealed-trip and attitudinal sections (they matter for the equity analysis) but skip the choice tasks.

**Strata.** Region (13) × urban/non-urban × sex = 52 hard cells, each with a minimum of 50 completes (A-social-122), so a floor of 200 per region, which meets the 200-per-subgroup rule (S-soc-314) and the H1/H4 S-estimate bounds (about 190–193) at the regional level only when sexes are pooled. Inside each region, soft quotas (±10 percentage points around the regional margin, A-social-131) for nationality (Saudi/non-Saudi), age band (A-social-127), driving licence and household car access, and household income band (A-social-126; optional question). The urban/non-urban split follows GASTAT's locality classification, which was **not obtained in this track** (gap).

**National target (A-social-123).** 4,000 completes: the 13 × 200 = 2,600 floor plus 1,400 allocated in proportion to Census 2022 regional population (A-social-130; total population used as a proxy for adults, S-soc-339, secondary; re-run on GASTAT 18+ counts before fielding). A small-town oversample of 30 completes per short-listed non-metro town, capped at 1,200 in total (A-social-124), comes on top, once R2 gives the short list (A-screen-006).

| # | region | Census 2022 population (S-soc-339, secondary) | share | proportional add-on (A-social-130) | target completes |
|---|---|---|---|---|---|
| 1 | Riyadh | 8,591,748 | 26.7 % | 374 | 574 |
| 2 | Makkah | 8,021,463 | 24.9 % | 349 | 549 |
| 3 | Eastern | 5,125,254 | 15.9 % | 223 | 423 |
| 4 | Madinah | 2,137,983 | 6.6 % | 93 | 293 |
| 5 | Asir | 2,024,285 | 6.3 % | 88 | 288 |
| 6 | Jazan | 1,404,997 | 4.4 % | 61 | 261 |
| 7 | Qassim | 1,336,179 | 4.2 % | 58 | 258 |
| 8 | Tabuk | 886,036 | 2.8 % | 39 | 239 |
| 9 | Hail | 746,406 | 2.3 % | 32 | 232 |
| 10 | Al Jawf | 595,822 | 1.9 % | 26 | 226 |
| 11 | Najran | 592,300 | 1.8 % | 26 | 226 |
| 12 | Northern Borders | 373,577 | 1.2 % | 16 | 216 |
| 13 | Al Bahah | 339,174 | 1.1 % | 15 | 215 |
| | **Total** | **32,175,224** | 100 % | **1,400** | **4,000** |

The Makkah and Madinah totals differ between aggregators (S-079); the allocation uses the GLMM row (S-soc-339) and moves by a few completes if the other figure is used. Because small regions are oversampled relative to their population, national estimates must be weighted (analysis plan, section 6).

What the sample supports: national models with full segmentation (purpose, income, sex, nationality); regional models for the main parameters (at least 200 per region); region × sex estimates of H1 only by pooling with interaction terms, since about 100 per region-sex cell is below the 189.7 lower bound for `family_carriage[1]`.

**Fielding modes (for the fielding institution to choose; none used here).** (a) An online panel with regional and demographic quotas; (b) intercept interviews at railway stations, airports and coach terminals, which reach current public-transport users but over-represent them; (c) household interviews, which reach people without internet access or without intercity travel. A mix is likely needed for non-metro regions. **No published Saudi survey cost was found**; costs must be quoted by the fielding institution and are not estimated here (rule 1).

**Coverage gaps to resolve before fielding.** The instrument exists in Arabic and English only; non-Saudi residents who read neither well (non-Saudis are 25.9 % of the Census 2022 population in Al Bahah and 48.3 % in Riyadh, the lowest and highest regional shares; derived from S-soc-339, secondary) would be under-covered. Translations into further languages, if wanted, need the same native-speaker review as the Arabic text.

## 8. What the survey does not ask

No names, national ID or Iqama numbers, phone numbers, exact addresses or GPS locations; no question on religious belief or practice, health or disability, tribe, or political views. The prayer-facility attribute is a feature of the service, not a question about the respondent; whether a stated preference for it counts as sensitive data under the PDPL is an open question recorded in `ethics-consent.md`. Accessibility needs of disabled travellers are therefore **not covered** by this instrument (gap: a separate, ethics-reviewed module would be needed).

## 9. Fielding prerequisites (for a future human team; none done)

Nothing below has been done. All are conditions before any respondent is contacted.

1. **Tariq's approval** to field (rule 7), recorded at a checkpoint.
2. **Fielding institution named**, acting as the data controller under the PDPL; it fills the placeholders in `ethics-consent.md` and adopts the privacy policy (S-soc-342).
3. **Ethics approval** by a local research-ethics committee registered under the Law of Ethics of Research on Living Creatures (S-soc-330, S-soc-346), or a documented decision by that committee that the study is out of the law's scope (unclear; see `ethics-consent.md`).
4. **Native-speaker review of the Arabic instrument** (survey-design skill; checkpoint item for Tariq) and a bilingual figure check (every number and every S-/A-id identical in `instrument.en.md` and `instrument.ar.md`; there is no repository command for this yet, the R1d check was a one-off script whose result is in `docs/survey/analysis-plan.md`, section 11).
5. **Level re-check**: a dated official fare sample for rail, air and coach and a car fuel-economy figure (replacing S-soc-317 secondary, S-soc-318 to S-soc-321 secondary/unverified), and a decision on the level-balance issue (section 5).
6. **Pilot** of 30–50 respondents in both languages (A-social-125, S-soc-315): comprehension of each attribute, timing (sets the speeder threshold A-social-129), dominance-task failure rate, and an MNL on the pilot to update the priors and regenerate the design if needed.
7. **Census margins** for weighting and allocation: GASTAT 18+ population by region, sex, nationality and age (S-090 unverified; S-soc-339 secondary).
8. **Data handling** set up in-Kingdom before the first interview (ethics-consent.md, section 4).
