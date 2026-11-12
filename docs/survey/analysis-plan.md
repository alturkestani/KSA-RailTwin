> **Document version:** docs/survey/analysis-plan.md v0.1 | 31 Oct 2026 | Author: socio-culture-analyst B (R1d) | Status: draft

# Intercity stated-preference survey: analysis plan

**Designed, not fielded. No data exist.** Every coefficient used anywhere in the model stays **literature-based until survey results exist** (`cities/ksa/assumptions/mode_choice_priors.yaml`). Nothing in this plan is a result. It fixes, before any data are seen, how the data would be cleaned, modelled, weighted and used, so that the analysis cannot be tuned to a preferred answer.

Inputs: `docs/survey/design.yaml` (parameters, levels, coding), `docs/survey/choice_sets.csv` (27 design tasks in 3 blocks plus one dominance task per block), the instrument (`instrument.en.md`, `instrument.ar.md`), and the hypotheses H1–H8 (`design.md`, section 2).

| section | content |
|---|---|
| 1 | Data preparation and quality rules |
| 2 | Utility specification |
| 3 | Multinomial logit (MNL) |
| 4 | Mixed logit: panel, random parameters, error components |
| 5 | Segmentation and hypothesis tests |
| 6 | Weighting to GASTAT margins |
| 7 | Willingness to pay and value of time |
| 8 | Validation |
| 9 | How results replace the priors |
| 10 | Software and licences |
| 11 | Reporting rules and the R1d checks |

## 1. Data preparation and quality rules

Applied in this order. Every exclusion is counted and reported by region and language.

1. **Incomplete interviews** are discarded and never estimated (A-social-141).
2. **Attention check.** A respondent who does not choose "Disagree" at E10 is excluded from the main estimation and kept in a sensitivity run.
3. **Speeders.** A completion time below 40 % of the pilot median (A-social-129; range 30–50 %) excludes the respondent from the main estimation. The threshold is fixed after the pilot and before the main fieldwork.
4. **Dominance task.** A respondent who does not choose the dominant rail option in task 10 is excluded from the main estimation and kept in a sensitivity run (A-social-132). The dominance task itself is never used in estimation, because it carries almost no information on trade-offs. The failure share is reported; no expected share is assumed.
5. **Non-traders.** Respondents who choose the same alternative in all 9 design tasks are kept, because always choosing the car can be a real preference, and flagged. A sensitivity run without them is reported, with their share by region and by car access (F8).
6. **Self-reported non-attendance (D12).** Kept in the main model. A sensitivity model sets the attribute coefficient to zero for respondents who say they ignored that attribute (attribute non-attendance).
7. **Pivot check.** Shown times and costs are recomputed from the respondent's D (design.md, section 3) and compared with the logged screen values. Mismatches are corrected to the logged (shown) value, because the respondent chose on what was shown.

## 2. Utility specification

Car is the reference alternative. Parameter names are those of `design.yaml`:

- V_car = β_ivt_car · IVT_car + β_cost · COST_car
- V_rail = ASC_rail + β_ivt_rail · IVT_rail + β_access · ACC_rail + β_cost · FARE_rail + β_headway · HW_rail + β_on_time · OT_rail + β_comfort · BUSINESS + β_family_carriage · FAM + β_prayer · PRAY + β_luggage · LUG_rail + β_shaded_transfer · SHADE
- V_air = ASC_air + β_ivt_air · IVT_air + β_access · ACC_air + β_cost · FARE_air + β_headway · HW_air + β_on_time · OT_air + β_luggage · LUG_air
- V_bus = ASC_bus + β_ivt_bus · IVT_bus + β_access · ACC_bus + β_cost · FARE_bus + β_headway · HW_bus + β_comfort · VIP

Units as in `mode_choice_priors.yaml`: minutes, SAR, percentage points, and 0/1 dummies. That gives the 16 parameters of the design.

**Car cost and party size.** The car cost is per vehicle and fares are per person (instrument, D0). The main model uses the shown values. A sensitivity model divides the car cost by the party size (C3.7) to test whether respondents share it.

**Air availability.** Air enters a respondent's choice set only where the pair has scheduled flights (the screen did not show it otherwise). Availability is coded per task and handled in the likelihood.

**Trip length.** Because times and costs are scaled by D/400, a sensitivity model lets the time and cost coefficients vary with ln(D), to test whether the disutility per minute falls with trip length, as the international evidence suggests (S-soc-303).

## 3. Multinomial logit (MNL)

- Estimated first, on the cleaned sample, unweighted, by maximum likelihood, with robust (sandwich) standard errors clustered by respondent, because each respondent answers 9 tasks.
- Reported: coefficients, robust standard errors and t-ratios, log-likelihood at zero and at convergence, ρ² and adjusted ρ², AIC and BIC, numbers of respondents and of observations.
- Sign checks: time, access, headway and cost coefficients negative, on-time share positive. A wrong-signed coefficient is reported, not constrained away.
- The MNL also serves the pilot: the pilot's estimates update the priors, and the design may be regenerated before the main fieldwork (design.md, sections 5 and 9).

## 4. Mixed logit: panel, random parameters, error components

- **Panel.** Random parameters are drawn once per respondent and held fixed across that respondent's 9 tasks (panel specification), estimated by simulated maximum likelihood with Halton draws (S-soc-352).
- **Draws.** 500 Halton draws per respondent (A-social-134; range 200–2,000). Stability is checked by re-estimating with twice the draws and reporting the change in log-likelihood and in each coefficient.
- **Random parameters.**
  - Time, access and headway: negative lognormal (sign-constrained), one distribution per parameter.
  - Feature dummies (comfort, family carriage, prayer, luggage, shaded transfer): normal, so that some respondents may value a feature negatively; the estimated share below zero is reported.
  - Cost: **fixed** in the main model, so that the WTP ratios have finite moments. A WTP-space model, which estimates the WTP values directly, is the sensitivity run.
  - On-time share: fixed in the main model, normal in a sensitivity run.
- **Error components.** A shared normal error component on the three scheduled modes (rail, air, bus) captures their correlation; a second component on rail and bus only is tested. Only the standard deviations of the components are estimated; the ASCs carry the means.
- **Correlation.** A model with correlated random time parameters (Cholesky) is estimated if the uncorrelated model converges and the sample allows; it is a sensitivity run.
- **Selection.** Models are compared by BIC, and by likelihood-ratio tests where nested. The model that feeds the priors (section 9) is the one with the best BIC among those that pass the sign checks and the draw-stability check.

## 5. Segmentation and hypothesis tests

**Segments** (from the instrument): trip purpose (C3.4, grouped as commuting, business, visiting family or friends, Umrah or Hajj, tourism or leisure, other), household income band (F11, A-social-126; "prefer not to say" kept as its own group), sex (F1), nationality (F3), region (A3) and urban/non-urban stratum (A5), party type (C3.6), driving licence and car access (F7, F8), and season framing (A-social-128).

**Method.** Segment effects are estimated as interactions in the pooled model, not as separate models, unless a segment has at least 200 respondents (the subgroup rule, S-soc-314; design.md, section 6). Income enters the cost coefficient as β_cost · (income / mean income)^λ, with λ estimated: λ = 0 means no income effect, and λ < 0 means cost sensitivity falls as income rises, so the value of time rises with income. Band midpoints are used for income, with the open top band set at its lower bound in the main model and varied in a sensitivity run.

**What the sample supports** (design.md, section 7): national models with full segmentation; regional estimates of the main parameters; region × sex estimates of H1 only through pooled interactions.

| hypothesis | test (two-sided 5 % unless stated) |
|---|---|
| H1 family carriage | β_family_carriage > 0 (one-sided); interactions with sex and with the "with family" party types |
| H2 shaded transfer | β_shaded_transfer > 0 (one-sided); interaction with the summer framing |
| H3 value of time | VoT by income band and purpose; λ < 0 (one-sided); business VoT above non-work VoT |
| H4 prayer area | β_prayer > 0 (one-sided); standard deviation of the random coefficient |
| H5 reliability | β_on_time > 0; implied late-time multiplier (section 7) compared with 2.67 (S-soc-302) |
| H6 access weight | β_access / β_ivt_rail > 1; compared with 1.87 (S-soc-302) and 1.70 (S-soc-300) |
| H7 luggage | β_luggage by purpose (Umrah or Hajj and visiting family vs business) |
| H8 captivity | ASC_rail interactions with no licence and no car access |

Several tests are run, so the report gives both unadjusted and Holm-adjusted p-values across H1–H8. Attitudinal items E1–E9 are reported descriptively and may enter a hybrid choice model later; they are never used to explain away a choice result.

**Reporting language.** An unsupported hypothesis is reported as unsupported. Results describe the respondents' stated choices in the designed scenarios; they are not presented as facts about Saudi culture (rule 9).

## 6. Weighting to GASTAT margins

- **Why.** The sample is deliberately disproportionate: a floor of 200 completes per region, a proportional add-on, and a small-town oversample (design.md, section 7; A-social-122 to A-social-124). Unweighted national figures would over-represent small regions.
- **Margins.** Raking (iterative proportional fitting) to official GASTAT counts of residents aged 18 or over by: region × sex; region × nationality (Saudi / non-Saudi); age band (A-social-127) × sex nationally; urban/non-urban by region once GASTAT's locality classification is obtained. Only Census 2022 totals by region and nationality (all ages) were obtained in this track (S-soc-339, secondary); the 18+ margins and the urban/non-urban classification are **gaps** to fill before weighting (design.md, section 9, item 7).
- **Small-town oversample.** Weighted down to its governorate's population share inside the region before raking.
- **Trimming.** Weights are capped at 5 × the mean weight and re-raked (A-social-133; sensitivity at 3 and at 10). The Kish design effect and effective sample size are reported for each region.
- **Use of weights.** Descriptive results (trip rates, mode shares, attitudes) are weighted. Choice models are estimated unweighted in the main run, because the strata (region, sex, urban/non-urban) enter the model as explanatory variables; a weighted (pseudo-likelihood) run is reported as a sensitivity, and a material difference between the two is a sign of mis-specification to be reported. National values of time for appraisal are averaged over respondents with the weights (sample enumeration).

## 7. Willingness to pay and value of time

All values are ratios of estimated coefficients to the cost coefficient, in SAR of the survey year (stated in the report), one way, per person.

| quantity | formula | unit |
|---|---|---|
| Value of in-vehicle time, mode *m* | VoT_m = 60 · β_ivt_m / β_cost | SAR per hour |
| Value of access and egress time | 60 · β_access / β_cost | SAR per hour |
| Value of headway | 60 · β_headway / β_cost | SAR per hour of headway |
| Access-time multiplier | β_access / β_ivt_rail | ratio (compare 1.87, S-soc-302) |
| Headway multiplier | β_headway / β_ivt_rail | ratio (compare 0.46, S-soc-302) |
| WTP for one percentage point of on-time share | β_on_time / (−β_cost) | SAR per percentage point |
| Implied late-time multiplier | β_on_time / (−β_ivt_rail · 0.01 · 30) | ratio (30 = mean late delay told to respondents, A-mode-013; compare 2.67, S-soc-302) |
| WTP for a feature *k* (business class or VIP, family carriage, prayer area, large-suitcase allowance, shaded transfer) | β_k / (−β_cost) | SAR per trip |

Signs: with negative time and cost coefficients, the time ratios are positive; a feature with a positive coefficient has a positive WTP.

**Segments.** VoT and WTP are reported by purpose and income band (H3), and by sex, nationality and region where section 5 allows. With the income interaction, the cost coefficient of a respondent with income *y* is β_cost · (y / ȳ)^λ, so VoT_m(y) = 60 · β_ivt_m / (β_cost · (y / ȳ)^λ), which rises with income when λ < 0; the report gives VoT at each band midpoint.

**Uncertainty.**
- **Delta method** (S-soc-351): standard errors of each ratio from the robust covariance matrix, by the first-order expansion of the ratio.
- **Krinsky–Robb** (S-soc-350): 10,000 draws (A-social-134; range 5,000–20,000) from the multivariate normal of the estimates; the 10th, 50th and 90th percentiles of each ratio are reported as P10 / P50 / P90, as rule 3 requires for every cost and benefit. Draws with a cost coefficient of the wrong sign are counted and reported, not dropped silently.
- For the mixed logit, population WTP distributions come from the WTP-space model (section 4); the ratio of a random time coefficient to the fixed cost coefficient is reported with its mean, median and P10 / P90.

**Cross-checks** (not replacements): the survey VoT is compared with the transferred appraisal values A-cba-010 and the design value A-mode-006 (`mode_choice_priors.yaml`, `vot_cross_check`), and with the Saudi wage base used there (S-soc-338, secondary). A difference is reported and explained; neither value is silently preferred.

## 8. Validation

- **Hold-out respondents.** 20 % of respondents, drawn at random within region (A-social-145), are held out of estimation; the chosen model's predicted choice shares and log-likelihood on the hold-out are reported against the MNL and against a constants-only model.
- **Prior comparison.** Each estimate is placed against its prior and the prior range in `mode_choice_priors.yaml`. Estimates outside the prior range are flagged and discussed; they are not pulled back towards the prior.
- **Revealed trips.** The revealed mode shares of the respondents' last intercity trip (C3.3, weighted) are compared with the shares the model predicts for a no-rail scenario at typical levels. This is a plausibility check only: stated-preference constants are not used for forecasting (section 9).
- **Pilot.** The same pipeline runs on the pilot (30–50 respondents, A-social-125) to test the code and comprehension, not to produce estimates for use.

## 9. How results replace the priors

Until all of the steps below are complete and the verifier has signed off, every value in `cities/ksa/assumptions/mode_choice_priors.yaml` keeps the label **"literature-based until survey results exist"** and its assumption status `assumed`.

1. **Which values are replaced.** Time, access, headway, cost, on-time share and the feature coefficients take the estimates of the model selected in section 4, with P10 / P50 / P90 from section 7. Each entry gets `source:` pointing to the estimation run (`runs/` id, seed, data hash and code version, rule 10) and keeps the old value as `prior_value` and `prior_assumption`.
2. **ASCs are not taken from the survey.** Stated-preference constants are not transferable to forecasts (S-soc-337, secondary). The ASCs stay as priors and are recalibrated to observed mode shares in R3 (A-mode-010 to A-mode-012).
3. **Scale.** The stated-preference model's error scale differs from that of a revealed-preference model. Only ratios (values of time, multipliers, WTP) are transferred directly to W8; absolute coefficients are rescaled by the scale factor found in R3 calibration, and the method is recorded.
4. **Segments.** Where a segment value is estimated (purpose, income band, sex, region), the YAML gains a segment table; where a segment is too small (section 5), the pooled value is used and the file says so.
5. **Status labels.** Replaced values change from `assumed` to `estimated (survey, uncalibrated)` in `docs/assumptions.md`; after R3 calibration they change to `calibrated` (survey-design skill). The model outputs keep the rule-3 label until calibration says otherwise.
6. **Design rerun.** If the survey is fielded in waves, the new estimates become the priors of the next wave's design, and `choice_sets.csv` is regenerated with a new seed recorded in its `meta.json`.
7. **Verifier.** The red-team verifier checks that every replaced value traces to a `runs/` output and that no value was replaced without its range.

## 10. Software and licences

Open-source tools only (rule 12). None is installed yet; each is in `docs/licences.md` and will go into `docs/licences.md` when used.

| tool | version checked | licence | role | status |
|---|---|---|---|---|
| Biogeme (Python) | 3.3.5 | MIT (S-soc-334) | primary estimator: MNL, panel mixed logit with Halton draws, WTP space | planned |
| Apollo (R) | 0.3.9 | GPL-2 (S-soc-349) | independent cross-check of the selected model; called, not shipped | optional |
| xlogit (Python) | 0.2.7 | **unclear**: MIT on PyPI vs GPL-3.0 on GitHub (S-soc-335) | fast mixed logit | **not used** until the licence conflict is settled |
| `demand/survey.py` (own code) | 0.1 | Apache-2.0 | design generator; Krinsky–Robb and delta-method helpers to be added here | in repository |

Two estimators that agree on the selected model to within their standard errors are the reproducibility check; a disagreement is reported.

## 11. Reporting rules and the R1d checks

**Reporting rules.**
- Every report from this survey says "stated preference, designed scenarios"; until fielding, every document says "designed, not fielded".
- No table cell, segment estimate or map is published for fewer than 10 respondents (A-social-144).
- Every value carries a P10 / P50 / P90 range (rule 3); every model output that uses these values carries the rule-3 label.
- No quote from respondents is published (the instrument has no open text apart from "Other (please state)", which is coded and not quoted).

**R1d checks (31 Oct 2026; design only).**
- **Determinism.** `uv run python -m demand.survey design --config docs/survey/design.yaml --seed 1 --out /tmp/cs_check.csv` was run twice and compared with `docs/survey/choice_sets.csv` by SHA-256: all three files are identical (SHA-256 `301f782b92043f3b849ba09d62b8eeac5d924d157a1afae2fc67a5c9faa6f7b7`; 690 rows; D-error 0.00785495, as in `choice_sets.csv.meta.json`).
- **Bilingual figure check.** A one-off script compared every number and every S-/A-id in `instrument.en.md` and `instrument.ar.md`: no number appears in one version and not the other, and the two id sets are identical. There is no repository command for this check yet.
- **Ids.** Every S-id and A-id cited in `design.yaml`, `mode_choice_priors.yaml` and `docs/survey/*.md` was checked against `docs/sources/` and the assumption fragments (see the builder's status block).
