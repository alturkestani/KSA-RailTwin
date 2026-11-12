> **Document version:** docs/status/verify-greenbook.md v1.0 | 31 Oct 2026 | Author: verifier (coordinator session, read-only) | Status: verified

# VERIFY_GREENBOOK — Green Book 2026 discount-rate schedule quoted verbatim from the primary pages

Purpose (prompt `prompts/VERIFY_GREENBOOK.md` v1.0): decision D1a (adopt the Green Book 2026 schedule 3.00 % years 1–30, 2.50 % years 31–75, 2.25 % from year 76 as the central social discount rate, A-cba-001) stands only if the rate table is quoted verbatim from the fetched primary pages recorded as S-cp1-060 and S-cp1-061 in `docs/sources/index.csv`, and the figures match the register, the plan and the decision pack digit by digit.

Method: each URL in the index rows was fetched with `curl -sL` on 31 Oct 2026 and the text extracted with `pdftotext -layout` (poppler, Homebrew). Page numbers below are the printed page numbers in each document's footer; the PDF page index is given where it differs. Nothing in the register, the plan or the pack was edited. No real-world action was taken beyond HTTP GET of public gov.uk pages.

## 1. Fetch records

| id | URL | HTTP | bytes | SHA-256 (first 16) | cover title | date on cover / in metadata | accessed (UTC) |
|---|---|---|---|---|---|---|---|
| S-cp1-060 | https://assets.publishing.service.gov.uk/media/6ae0ba897b7111c482d80a3b/The_Green_Book_2026.pdf | 200, `application/pdf` | 966,665 | `476b02b7fb13a7fe` | "THE GREEN BOOK / UK GOVERNMENT GUIDANCE ON APPRAISAL / 2026" (cover, p.1); PDF metadata Title "The Green Book – UK government guidance on appraisal", Author "HM Treasury"; 86 pages; ISBN 978-1-918417-12-8, PU3608 | cover: 2026 (© Crown copyright 2026); metadata CreationDate 21 Oct 2026, ModDate 26 Oct 2026; gov.uk landing page `dateModified` 2026-10-28T13:30:39Z with change note "Updated to reflect changes to the approach to discounting." | 2026-10-31T06:22:52Z |
| S-cp1-061 | https://assets.publishing.service.gov.uk/media/6ae0b34016428df537606216/Green_Book_supplementary_guidance_-_discounting.pdf | 200, `application/pdf` | 304,217 | `14909fc0c9e9d893` | "Discounting / Green Book supplementary guidance / October 2026" (cover, p.1); no Title field in the PDF metadata; 16 pages; Annex A table footed "Source: HM Treasury"; back page "HM Treasury contacts" | cover: October 2026; metadata CreationDate = ModDate 27 Oct 2026 | 2026-10-31T06:22:53Z |
| S-cp1-062 | https://assets.publishing.service.gov.uk/media/6a0da3794ea6d8f759662dc9/tag-unit-a1-1-cost-benefit-analysis-may-2025.pdf | 200, `application/pdf` | 697,915 | `aa5b7ffacc1093457` | "TAG Unit A1.1 / Cost-Benefit Analysis / May 2026 / Department for Transport" (cover, p.1); metadata Title "TAG unit A1.1 cost-benefit analysis", Author "Department for Transport"; 39 pages | cover: May 2026 (the file name says `may-2025`; the cover and metadata say May 2026, CreationDate 20 May 2026) | 2026-10-31T06:22:54Z |
| landing page | https://www.gov.uk/government/publications/the-green-book-appraisal-and-evaluation-in-central-government | 200 | 82,853 | – | GOV.UK publication page | `datePublished` 2013-04-18; `dateModified` 2026-10-28T13:30:39Z; most recent `<time>` entry "28 October 2026"; links the S-cp1-060 PDF by the same media id. The S-cp1-061 PDF is not linked from this page (its media id does not appear in the HTML); it was fetched directly and its cover identifies it as HM Treasury, October 2026. | 2026-10-31T06:24:25Z |

All three documents rendered as text on the first attempt; no fallback was needed.

## 2. Verbatim quotes

### 2.1 S-cp1-060 — The Green Book (2026), Chapter 6 "Shortlist appraisal", section "Discounting", paragraphs 6.52–6.55, printed page 40 (PDF page 46)

The 2026 Green Book states the schedule in prose; it has no rate table of its own and refers to the supplementary guidance for the derivation and the discount-factor table.

```
Discounting
6.52 The Green Book recommends using discounting to compare social costs
and social benefits occurring over different time periods on a consistent basis.
Discounting enables profiles of benefits and costs stretching over many years to be
expressed in ‘present value’ terms.

6.53 Discounting is based on the concept of social time preference: people
generally prefer to receive benefits sooner and incur costs later. This means that
social costs and social benefits, which occur later in time, are given less weight than
costs or benefits that occur sooner.

6.54 The discount rate used in the Green Book is known as the social time
preference rate (STPR). It is set at 3.00% in real terms for years 1 to 30 of an appraisal.
It is 2.50% for years 31 to 75, and then 2.25% for year 76 onwards. Practitioners can
find more detail on the derivation of the STPR in the Green Book supplementary
guidance on discounting.

6.55 To adjust for discounting, practitioners should multiply social benefits and
social costs in future years by the discount factor corresponding to that year. The
Green Book supplementary guidance on discounting includes a table of pre-
calculated discount factors.
```

Consistency check inside the document: Table 8 on the same page ("Discounting and present values") shows discount factors 1.000, 0.9709, 0.9426, 0.9151, 0.8885, 0.8626 for years 0–5; 1/1.03 = 0.9709 and 1/1.03^5 = 0.8626 (computed), so the worked example uses 3.00 %.

### 2.2 S-cp1-061 — Green Book supplementary guidance: Discounting (October 2026)

Paragraph 2.1, printed page 7:

```
Derivation of the
discount rate
Introduction
2.1   The discount rate that is used in the Green Book is known
formally as the Social Time Preference Rate (STPR). The STPR is
currently set at 3.00% in real terms for the first 30 years of a proposal.
```

Paragraphs 3.7–3.10, printed page 12 (the rate schedule):

```
Proposals with time horizons beyond 30 years
3.7     The standard discount rate of 3.00% declines over time. This is
because there is uncertainty around the future values of the annual
growth rate of real per capita consumption (𝑔) and long-term real gilt
yields, both of which are used in informing the discount rate.
3.8   When conducting an appraisal, practitioners should use a
discount rate of:
•   3.00% for years 1 to 30

•   2.50% for years 31 to 75

•   2.25% for years 76 to 125
3.9   The Green Book discount rate profile is expressed in terms of
forward rates, not spot rates. For example, for an appraisal with a time
horizon ending in year 40, practitioners should use 3.00% as the
discount rate until year 30, then 2.50% from year 31 to year 40. They
should not use 2.50% as the discount rate in each year until year 40.
3.10 Many proposals have social costs and social benefits beyond 125
years. These should be taken into account in appraisal. However,
discounting is not an analytically meaningful technique for social costs
and social benefits that take place after year 125. Practitioners should
therefore use standard social cost-benefit analysis, and the relevant
discount rates, only for monetisable impacts that occur within the first
125 years of an appraisal. For social costs and social benefits that take
place after year 125, practitioners should consider alternative analytical
methods and discuss their approach with HM Treasury.
```

Annex A "Discount factors", printed pages 14–15 (the full table, as extracted; two-column layout preserved):

```
Annex A
Discount factors
        Discount   Discount               Discount   Discount
 Year                              Year
          rate      factor                  rate      factor
  0        –        1.0000          30     3.00%      0.4120
  1      3.00%      0.9709          31      2.50%     0.4019
  2      3.00%      0.9426          32      2.50%     0.3921
  3      3.00%       0.9151         33      2.50%     0.3826
  4      3.00%      0.8885          34      2.50%     0.3732
  5      3.00%      0.8626          35      2.50%     0.3641
  6      3.00%      0.8375          36      2.50%     0.3553
  7      3.00%       0.8131         37      2.50%     0.3466
  8      3.00%      0.7894          38      2.50%     0.3381
  9      3.00%      0.7664          39      2.50%     0.3299
  10     3.00%      0.7441          40      2.50%     0.3218
  11     3.00%      0.7224          41      2.50%     0.3140
  12     3.00%      0.7014          42      2.50%     0.3063
  13     3.00%      0.6810          43      2.50%     0.2989
  14     3.00%       0.6611         44      2.50%     0.2916
  15     3.00%      0.6419          45      2.50%     0.2845
  16     3.00%      0.6232          46      2.50%     0.2775
  17     3.00%      0.6050          47      2.50%     0.2708
  18     3.00%      0.5874          48      2.50%     0.2642
  19     3.00%      0.5703          49      2.50%     0.2577
  20     3.00%      0.5537          50      2.50%     0.2514
  21     3.00%      0.5375          51      2.50%     0.2453
  22     3.00%      0.5219          52      2.50%     0.2393
  23     3.00%      0.5067          53      2.50%     0.2335
  24     3.00%      0.4919          54      2.50%     0.2278
  25     3.00%      0.4776          55      2.50%     0.2222
  26     3.00%      0.4637          56      2.50%     0.2168
  27     3.00%      0.4502          57      2.50%      0.2115
  28     3.00%      0.4371          58      2.50%     0.2064
  29     3.00%      0.4243          59      2.50%     0.2013

            Discount   Discount               Discount   Discount
   Year                                Year
              rate      factor                  rate      factor
    60        2.50%     0.1964          93      2.25%     0.0909
    61        2.50%      0.1916         94      2.25%     0.0889
    62        2.50%     0.1869          95      2.25%     0.0869
    63        2.50%     0.1824          96      2.25%     0.0850
    64        2.50%     0.1779          97      2.25%     0.0831
    65        2.50%     0.1736          98      2.25%     0.0813
    66        2.50%     0.1694          99      2.25%     0.0795
    67        2.50%     0.1652         100      2.25%     0.0778
    68        2.50%      0.1612        101      2.25%     0.0760
    69        2.50%     0.1573         102      2.25%     0.0744
    70        2.50%     0.1534         103      2.25%     0.0727
    71        2.50%     0.1497         104      2.25%      0.0711
    72        2.50%     0.1460         105      2.25%     0.0696
    73        2.50%     0.1425         106      2.25%     0.0680
    74        2.50%     0.1390         107      2.25%     0.0665
    75        2.50%     0.1356         108      2.25%     0.0651
    76        2.25%     0.1326         109      2.25%     0.0636
    77        2.25%     0.1297         110      2.25%     0.0622
    78        2.25%     0.1269          111     2.25%     0.0609
    79        2.25%      0.1241         112     2.25%     0.0595
    80        2.25%      0.1213         113     2.25%     0.0582
    81        2.25%      0.1187        114      2.25%     0.0569
    82        2.25%      0.1161         115     2.25%     0.0557
    83        2.25%      0.1135         116     2.25%     0.0545
    84        2.25%      0.1110         117     2.25%     0.0533
    85        2.25%     0.1086         118      2.25%     0.0521
    86        2.25%     0.1062          119     2.25%     0.0509
    87        2.25%     0.1038         120      2.25%     0.0498
    88        2.25%      0.1016         121     2.25%     0.0487
    89        2.25%     0.0993         122      2.25%     0.0477
    90        2.25%     0.0971         123      2.25%     0.0466
    91        2.25%     0.0950         124      2.25%     0.0456
    92        2.25%     0.0929         125      2.25%     0.0446
Source: HM Treasury
```

Arithmetic check of the table's transition rows (computed 31 Oct 2026, 4 d.p.): 1.03^-30 = 0.4120 (year 30); × 1/1.025 = 0.4019 (year 31); year 75 = 0.1356; year 76 = 0.1356/1.0225 = 0.1326; year 125 = 0.0446. All five match the printed factors, so the table applies 3.00 % through year 30, 2.50 % for 31–75 and 2.25 % for 76–125 as forward rates.

### 2.3 S-cp1-062 — DfT TAG Unit A1.1 Cost-Benefit Analysis (May 2026), paragraphs 2.7.4–2.7.6, printed page 16 (PDF page 16)

```
2.7.4   Where PV is the present value; By is a monetary value (in real prices) received
        in year y; and Π(1+ri) is the product of 1 plus the discount rate for each year
        from the base year to the year y, when the value is received. The Green Book
        provides the discount rates which should be applied over different periods and
        these are given in the TAG Data Book:

        A1.1.1: Green Book Discount Rates

2.7.5   These rates should be applied from the current year, i.e. the year when the
        appraisal is undertaken, and not the scheme opening year. The discount rate is
        assumed to fall over very long periods because of uncertainty about the future.

2.7.6   As with adjusting for inflation, it is necessary to have a base year for discounting
        and the Department’s current base year is 2023. All streams of costs and
        benefits, interpolated and extrapolated over the whole appraisal period,
        presented in real prices and in the market-price unit of account, should be
        discounted back to this base year. The Green Book recommends that the
        following discount rates should be used:

        •   3.5% should be applied for years between the current year (the year the
            appraisal is taking place) and year 30 of an appraisal

        •   3% for years 31 to 75

        •   2.5% for year 76 onwards. This applies for all impacts, including for health
            impacts where the reduced 1.5% discount rate is applied for future years
            (see TAG units A3 and A4.1 for further details).
```

This is the May 2026 TAG text, published before the 28 Oct 2026 Green Book change. It shows the DfT schedule in force at the date of the TAG unit; whether DfT has since issued a revised unit was not checked here (out of scope of this prompt).

## 3. Digit-by-digit comparison

| where | text found | matches source? |
|---|---|---|
| Green Book 2026 para 6.54 (S-cp1-060) | 3.00% years 1 to 30; 2.50% years 31 to 75; 2.25% year 76 onwards | source |
| Supplementary guidance para 3.8 (S-cp1-061) | 3.00% years 1 to 30; 2.50% years 31 to 75; 2.25% years 76 to 125 | source (125-year cap, para 3.10) |
| `docs/sources/index.csv` S-cp1-060: value, locator, quote | "3.00% (years 1-30); 2.50% (years 31-75); 2.25% (year 76 onwards)"; "Chapter 6 'Discounting', para 6.54 (printed p.40)"; quote "It is set at 3.00% in real terms for years 1 to 30 of an appraisal." | YES, value, page and quote exact |
| `docs/sources/index.csv` S-cp1-061: value, locator, quote | "3.00% (years 1-30); 2.50% (years 31-75); 2.25% (years 76-125)"; "paras 2.1, 3.7, 3.8, 3.9"; quote "3.00% for years 1 to 30" | YES, exact |
| `docs/sources/index.csv` S-cp1-062: value, locator, quote | "3.5% (current year to year 30); 3% (years 31-75); 2.5% (year 76 onwards)"; "para 2.7.6 (printed p.16)"; quote "3.5% should be applied for years between the current year" | YES, exact |
| `docs/assumptions.md` row A-cba-001, value column | "the Green Book now gives 3.00 % / 2.50 % / 2.25 %" | YES |
| `docs/assumptions.md` row A-cba-001, source column | "para 6.54: 3.00 % for years 1–30, 2.50 % for 31–75, 2.25 % from 76 (S-cp1-060, verified); supplementary guidance on discounting, Oct 2026, para 3.8 (S-cp1-061)" | YES |
| `docs/assumptions.md` row A-cba-001, approved (D1b) value | "3.5 % (years 0–30), 3.0 % (31–75), 2.5 % (76+)" vs TAG "current year ... and year 30 / 31 to 75 / 76 onwards" | YES (year 0 = the current year in TAG 2.7.5) |
| `docs/plan.md` §2 (line 51) | "3.00 % (years 1–30), 2.50 % (31–75), 2.25 % (76+) (para 6.54, S-cp1-060; supplementary guidance para 3.8, S-cp1-061)" | YES |
| `docs/plan.md` §9 row 3 (line 134) | "3.00/2.50/2.25 %" | YES |
| `docs/cp1-decision-pack.md` D1 (a) | "3.00 % for years 1–30, 2.50 % for 31–75, 2.25 % from 76 (S-cp1-060), with the TAG May 2026 schedule of 3.5 / 3.0 / 2.5 % as a sensitivity" | YES |
| `docs/cp1-decision-pack.md` D1 (b) | "3.5 / 3.0 % as central (DfT TAG still uses it, S-cp1-062), with 3.00 / 2.50 / 2.25 % as a sensitivity" | YES |

No discrepancy found.

## 4. Observations (not failures; for the coordinator and R5)

- O1. The main Green Book says "2.25% for year 76 onwards"; the supplementary guidance bounds the schedule at year 125 and says discounting is "not an analytically meaningful technique" after year 125 (para 3.10). The project's horizons (60 years central, 100 years maximum sensitivity, A-cba-004) sit inside the bound. When A-cba-001 is rewritten to one schedule after D1, write "2.25 % for years 76–125" and cite para 3.10 for anything beyond.
- O2. Para 3.9: the schedule is a profile of forward rates, not spot rates. The R5 appraisal code must apply 3.00 % to years 1–30 and then 2.50 % from year 31, never a single blended rate; the Annex A factors (quoted above) are the reference values for a unit test.
- O3. The supplementary guidance PDF is not linked from the Green Book landing page fetched here. Its cover (HM Treasury, October 2026) and metadata (27 Oct 2026) identify it; the gov.uk page that hosts it was not located in this run. The index row's published field ("gov.uk 'supplementary guidance updated' 28 Oct 2026") is the scout's record and was not re-confirmed from a page.
- O4. The TAG A1.1 file name says `may-2025`; its cover and metadata say May 2026. The index row already records "May 2026 (cover)". The cover carries an "OFFICIAL-SENSITIVE" marking although it is the public gov.uk download; recorded, no action.
- O5. TAG para 2.7.6 gives the DfT discounting base year (2023) and a reduced 1.5 % rate for health impacts expressed in utility values. Neither is used in A-cba-001; the health rate is a candidate for a later assumptions row if R5 monetises health impacts that way.

## 5. Verdict

Table quoted verbatim from both primary HM Treasury pages (S-cp1-060 para 6.54, S-cp1-061 paras 3.7–3.10 and Annex A); the DfT TAG schedule (S-cp1-062 para 2.7.6) quoted verbatim; every figure in the register row A-cba-001, plan §2 and §9, and decision pack D1 matches digit by digit.

VERDICT: PASS

Tariq's CP1 condition for D1a is met. The choice between D1a and D1b remains his at CP1; this report does not make it.
