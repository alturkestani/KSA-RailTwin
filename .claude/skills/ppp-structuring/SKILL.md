---
name: ppp-structuring
description: The W6 method for funding, ownership and delivery models: the option list, the risk-allocation matrix template, fiscal exposure metrics, the case-study template and the Saudi legal and institutional frame to cite. Use when recommending a delivery model per corridor family, building docs/funding.md or assessing fiscal exposure.
---
> **Document version:** skills/ppp-structuring/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Funding, ownership and delivery models

Output: `docs/funding.md` (landscape, case studies, Saudi frame), `cities/ksa/funding/models.yaml` (options), `cities/ksa/funding/risk_matrix_<corridor>.yaml`, and per-corridor recommendations in R7. Everything cited; where the law or practice is unclear, write "unclear" and the question.

## Options (`models.yaml`; one entry each, with `description`, `who_pays`, `who_owns`, `typical_term_years`, `examples: [S-xxx]`)
`fully_public_budget`, `fully_public_pif`, `fully_public_sar`, `public_with_private_om`, `ppp_dbfom_availability`, `ppp_dbfom_demand_risk`, `ppp_dbfm`, `vertical_separation_infra_public_ops_private`, `integrated_concession`, `private_concession`, `lvc_station_area_development`, `lvc_betterment_levy`, `lvc_tax_increment`, `hybrid_<name>` (document the mix).

## Risk-allocation matrix (one YAML per corridor family; rendered as a table)
| risk | public | private | shared | mechanism and reasoning (cite precedent S-xxx) |
|---|---|---|---|---|
| construction (cost, schedule, geotechnical, sand) | | | | |
| demand (ridership) | | | | |
| revenue (fares, ancillary) | | | | |
| operations and maintenance | | | | |
| financing (rates, refinancing, FX) | | | | |
| land acquisition and utilities | | | | |
| regulatory, political, force majeure | | | | |
Exactly one of public/private/shared is `x` per row; the mechanism names the contract clause type (availability payment, minimum revenue guarantee, cap-and-collar, pass-through, compensation event).

## Fiscal exposure metrics (computed by `uv run python -m funding.exposure --corridor <id> --model <option> --cba runs/cba/<id>/ --seed 1`)
Up-front public capex (P50/P80); annual availability or subsidy payments as a share of a stated budget line (source the budget figure); contingent liabilities (guarantees, termination payments) with a probability-weighted range; net fiscal cost over 30/40/60 years; the value-for-money logic (public-sector comparator vs PPP, with the risk-transfer value as an assumption `A-fund-nnn`).

## Case-study template (`docs/funding.md` section per case)
Name, country, years; what was built; model used; who carried which risk; financing structure and amounts (price year); outcome vs plan (cost, time, ridership, renegotiations); lessons for KSA; evidence grade; sources. Cases named in the brief: Japan rail + real estate (JR East; Tokyu and other private railways), Hong Kong MTR rail + property, France SNCF Réseau and LGV concessions (SEA Tours–Bordeaux, LISEA), Spain ADIF/AVE, China Railway and local-government financing, Morocco Al Boraq financing, Haramain contracts and consortium history.

## Saudi frame (cite the instrument and the date read)
Private Sector Participation Law and its regulations; National Center for Privatization (NCP) framework and manuals; PIF's mandate and transport holdings; SAR's mandate, ownership and the Haramain operating arrangements; the Landbridge PPP history (Chinese-consortium talks ended; SAR phased delivery); Transport General Authority and Ministry of Transport and Logistic Services roles; any rail regulator for access charges; public-debt and budget documents for the exposure ratios. Unclear points are listed as questions, not resolved by assumption.

## Rules that bite
- No advocacy: present options with evidence; recommendations are "best fit given X, Y" with the trade-offs.
- Risk allocation must match the corridor's demand uncertainty from the CBA switching values (demand-risk PPP is not recommended where the P10 demand breaks BCR = 1 without saying so).
- Entity names are facts, not endorsements; no logos; no contact with any entity (rule 7).
