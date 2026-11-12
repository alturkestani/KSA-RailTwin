> **Document version:** docs/status/verify-R1d.md v1.1 | 31 Oct 2026 | Author: red-team-verifier | Status: verified

# Verification report: R1d (W6 funding/PPP + Saudi frame; W7 social review, equity method, survey design)

Worktree `.worktrees/r1d`, branch `r1d`, HEAD `55b69c7` (31 Oct 2026 11:13 +03). Verified 31 Oct 2026 11:00–11:25 +03 by the red-team-verifier (read-only; nothing fixed). Brief: `prompts/R1d.md` tasks 1–7 and its Acceptance section; rules `CLAUDE.md`, `prompts/_common.md`.

## 1. Commands (exit codes and timing)

| command | result | exit | wall |
|---|---|---|---|
| `uv run ruff check .` | All checks passed | 0 | 1 s |
| `uv run ruff format --check .` | 323 files already formatted | 0 | <1 s |
| `uv run pytest -q` | all green, 113 tests passed (ruff/pytest/docver/manifest = `make test`) | 0 | 6 s |
| `uv run python -m common.docver check docs prompts .claude film/script` | docver OK: 200 files | 0 | <1 s |
| `uv run python -m common.manifest verify` | manifest OK: 16 rows (data/ksa symlinks as expected) | 0 | <1 s |
| `uv run python -m funding.models validate` | OK: 14 options (6 families); sources resolve | 0 | <1 s |
| `uv run python -m funding.risk_matrix validate` | OK: template; 7 risks; 5 metrics | 0 | <1 s |
| `uv run python -m demand.survey design --config docs/survey/design.yaml --seed 1 --out /tmp/vr1d_a.csv` (×2) | 690 rows, D-error 0.00785495 both runs | 0 | ~3 s each |

Determinism: `cmp` of the two runs and of each against `docs/survey/choice_sets.csv` is byte-identical (SHA-256 `301f782b…f6b7` for all three). `meta.json` differs only in `code_version` (committed file says `cp1-3-g557f4bd-dirty`, regenerated says `cp1-9-g55b69c7`); seed, config hash, data hash, D-error and level balance identical.

## 2. Criteria table

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | `make test` components, validators, generator determinism | PASS | table above; byte-identical CSV on seed 1 ×2 and vs committed file |
| 2 | Every W6 option present with sources (budget / PIF / SAR; public + private O&M; DBFOM availability and demand-risk; DBFM; vertical separation vs integrated; private concession; LVC station-area, betterment levy, tax increment) | PASS | `cities/ksa/funding/models.yaml` ids `fully_public_budget`, `fully_public_pif`, `fully_public_sar`, `public_with_private_om`, `ppp_dbfom_availability`, `ppp_dbfom_demand_risk`, `ppp_dbfm`, `vertical_separation_infra_public_ops_private`, `integrated_concession`, `private_concession`, `lvc_station_area_development`, `lvc_betterment_levy`, `lvc_tax_increment` (+1 hybrid); each with `sources:`; validator confirms every S-id resolves; `docs/funding.md` lines 24–39 table |
| 3 | Seven case studies, each with structure, who paid, demand risk, what happened, source + date, or "no reliable data found" | PASS | `docs/funding.md` §1–§7 (lines 50–257): Japan (S-fund-200…210), MTR (211…221), LISEA (222…235), ADIF/AVE (236…245), China (246…256), Al Boraq (257…260), Haramain (261…266); gaps written as "no reliable data found" (e.g. lines 57, 62, 132, 166, 219, 240); evidence grade per case; comparison table lines 259–271 |
| 4 | Saudi-frame items sourced or "unclear" with the precise question; no inferred legal position | PASS | `docs/funding.md` lines 274–349: PSP Law M/63 articles 1,4,7,8,10,11,20,28,34,41,44,45 (S-fund-001…011, MISA translation, verified by me: Art.1 "two or more", Art.7 "60 business days", Art.20 "not exceed 30 years"); NCP strategy (S-fund-030…032); PIF (S-fund-036…038, flagged secondary; official PDF 403); SAR (S-fund-033…035); Railway Law M/159 (S-fund-012…016, verified: "Authority: Transport General Authority", Art.32/33, "governing text is the Arabic text"); Landbridge (S-059, S-060, S-lb-*, S-049 unverified); 19-row item table, 3 clear / 16 unclear, each unclear row carries a question; `models.yaml` O&M paragraph says "whether such contracts are handled as PPPs under the Law in practice is unclear" rather than asserting |
| 5 | Risk-matrix rows (7) and columns public/private/shared + note; fiscal-exposure metrics (contingent liabilities, AP share of budget, VfM) with sources | PASS | `cities/ksa/funding/risk_matrix_template.yaml`: rows construction, demand, revenue, operations, financing, land, regulatory_force_majeure; `columns: [public, private, shared]`, `note` and `mechanism_options`, `precedents` per row; 5 metrics (`upfront_public_capex`, `availability_payments_share_of_budget`, `contingent_liabilities`, `net_fiscal_cost_horizon`, `value_for_money_psc`) each with `sources:` (PFRAM S-fund-021/023, IPSAS 32 S-fund-017, Green Book S-fund-024/025, EPEC S-fund-019, MoF S-fund-026, PSP Law S-fund-004/007); rendered in `docs/funding.md` lines 351–382 |
| 6 | 8 W7 topics with sourced evidence or explicit gap statement; equity method with data needs and availability; no advocacy; no unsourced cultural generalisation; sourced women's LFP trend table | PASS | `docs/social.md` §1–§8 (lines 24–202), each with Findings / Inference (ours, to test) / Gaps / evidence count; gap lines use "no Saudi evidence found; nearest evidence: …" (e.g. lines 39–40, 58–61, 102, 125–128, 143–144, 161–163, 179–181, 198–200); trend table lines 71–80 with per-row source and series-break notes (S-soc-001…009); tribal ties: "No statement on tribal ties is made" (line 125); Part B method lines 204–261 with data-availability column (table B1) and departures from TAG (B4); advocacy grep (will transform/should build/we recommend) empty; §6 explicitly "takes no position" |
| 7 | Survey exists as design files only; nothing fielded; Arabic reads natively; EN/AR figures identical | PASS | `docs/survey/` has design.md, design.yaml, instrument.en.md, instrument.ar.md, ethics-consent.md, analysis-plan.md + choice_sets.csv(.meta.json); every file opens with "designed, not fielded"; no form URL, account or respondent reference anywhere (grep); Arabic instrument: MSA, native phrasing (e.g. «فكّر في آخر رحلة قمت بها», «أفضّل عدم الإجابة», «قاعدة الارتكاز»), Arabic punctuation (، ؛ ؟ «») throughout, `dir="rtl"`, same question numbering (أ/ب/ج/د/هـ/و/ز); digit-by-digit script: numeric multisets of EN and AR identical (only tokenisation of trailing commas differs), S-/A-id sets identical; consent EN/AR figures 18/20/24/30 identical; `A-social-136` records that a native-speaker review is still a checkpoint item |
| 8 | Every prior in `mode_choice_priors.yaml` has `source:`/`assumption:` and the label; ids resolve | PASS | 27 entries: 25 `assumption: A-mode-0xx`/`A-cba-010`, 2 `source: S-soc-338`; every entry `status: "literature-based until survey results exist"` and file-level `label`; all A-mode-001…020 defined in `docs/assumptions-r1d.md`; A-cba-010, A-cost-001 in `docs/assumptions.md`; S-ids resolve (script: 0 undefined S-refs across all R1d deliverables) |
| 9 | Rule 1 spot check (seeded 10 %) and no number without S-/A-id | PASS | section 4 below: 24 rows, 0 fabricated or misquoted; one weak locator (S-fund-030) and one traceability gap (male 7.1 % Q4 2020) noted, neither a misquote; every figure in funding.md/social.md carries an id (manual read; the only bare numbers are our arithmetic labelled as such, e.g. social.md line 135) |
| 10 | Registers: assumptions-r1d complete; licences-r1d covers reused instruments/packages/datasets; unclear/share-alike flagged | PASS (with defects, see §3 B) | `docs/assumptions-r1d.md`: 92 rows (A-fund-001…011, A-mode-001…020, A-social-001…015, A-social-100…145); every A-id referenced in the deliverables is defined; `docs/licences-r1d.md/.csv` 12 rows: MoF (unclear), Green Book (OGL), PFRAM (unclear), GASTAT ×2 (commercial unclear), CCKP/CRU (unclear), UNESCO WHL (CC BY-SA, share-alike flagged, approval requested), TAG A4.2 (OGL), biogeme (MIT), apollo (GPL-2), xlogit (MIT vs GPL-3 conflict flagged, "do not use"), own generator (Apache-2.0) |
| 11 | Hygiene: no model names in facing docs; no content from the author's company; no absolute home paths; nothing under data/ or runs/; non-partisan; planned lines not styled existing | PASS | grep claude/opus/fable/haiku/sonnet/gpt over funding.md, social.md, survey/*, funding YAMLs, priors: empty; insurance grep: only pre-existing agent/prompt files on main; `/Users/` only in pre-existing main files (allowed by `tests/test_hygiene.py`), none in R1d files; `git ls-files data runs movies` = pre-existing `data/README.md`, `data/ksa/tables/*` (allowed); `git status --porcelain` clean; no `git push` in R1d files; Landbridge always "to be delivered / planned" (funding.md lines 316–320), social.md §8 "existing or announced corridors" |
| 12 | Status files and handoff: status block, `R1d: done` line, STATUS/cost-log rows | **FAIL** | `grep -nE "^R1d: (done|blocked)" docs/status/r1d.md` → NOT FOUND; `docs/status/r1d.md` (v0.1, 20 lines) ends at "Relaunched four subagents…" with no closing block (no case-study 7/7, Saudi-frame clear/unclear, social 8/8 counts, survey 6/6, elapsed); `docs/STATUS.md` line 15 still "R1a–R1d … not started"; `docs/cost-log.md` has no R1d row (STATUS/cost-log are coordinator-owned, noted for integration) |

## 3. Failures and defects with exact evidence

**A. FAIL: milestone handoff not written (task 7 of `prompts/R1d.md`; `_common.md` status rule).**
- `docs/status/r1d.md` has no end-of-milestone status block and no plain-text line `R1d: done` / `R1d: blocked - …`. The orchestrator greps for that line; as committed the milestone reads as unfinished. The brief lists the block's required contents (case studies 7/7, Saudi-frame items with status clear/unclear, social topics 8/8 with evidence counts, survey files 6/6, elapsed).
- No `milestone-handoff` entries: `docs/STATUS.md` milestone table still "not started" for R1d; no cost-log row. These two live outside the builder's ownership and belong to the integration run, but the track status block is the builder's.

**B. Defects (not individually failing, must be fixed before integration):**
1. Seven tracked deliverables point readers to untracked scratch files for the assumption register: `docs/funding.md:367` ("assumptions in `logs/r1d/assumptions-fund-A.md`"), `docs/social.md:5` (`logs/r1d/assumptions-social-A.md`), `docs/survey/design.md:18`, `docs/survey/ethics-consent.md:189`, `docs/survey/analysis-plan.md:352` (`logs/r1d/licences-social-B.csv`), `cities/ksa/assumptions/mode_choice_priors.yaml` header comment, and `docs/licences-r1d.md/.csv` rows 1 and 6 (`used_in`). `git ls-files logs` is empty, so these paths do not exist in the repository; the register is `docs/assumptions-r1d.md`.
2. `docs/sources/r1d-fund.csv` S-fund-030 (NCP strategy, USD 64 bn / 11.5 bn, used in funding.md lines 293 and 335) cites `https://www.ncp.gov.sa` (site root) with "PDF read from a downloaded copy": the figure is used but the URL does not locate the document.
3. `docs/sources/r1d-fund-cases.csv` S-fund-255 has an empty `url` (status unverified; carries no figure, so rule 1 is not breached, but the row format requires a URL).
4. `docs/social.md` table line 75: Saudi male unemployment 7.1 % (Q4 2020) is attributed to S-soc-009, whose `claim`/`quote` mention only the female 24.4 / 33.2 values; the Jadwa PDF could not be fetched (connection reset ×3), so this single cell is untraced to a quoted locator. Same pattern for male 5.4 / 4.3 / 4.6 / 4.3 (lines 76–79) under S-soc-002, whose claim lists only male Q4 2025; the locator (GASTAT Table 2-1) covers them, so it is a claim-text gap, not a source gap.
5. Survey design level balance (`choice_sets.csv.meta.json` `level_balance`): the middle levels of every linear time/cost attribute appear 0 times; air fare is SAR 180 in 26 of 27 tasks and car cost SAR 120 in 25 of 27. `design.md` section 5 discloses this as an open item, so it is not a rule breach, but the design as committed cannot identify air-fare sensitivity or non-linear time effects.
6. Cosmetic: `docs/funding.md` line 38 renders the tax-increment term as "25-25"; committed `choice_sets.csv.meta.json` `code_version` is "-dirty" (generated before the final commit).

## 4. Spot-check sample (seed 20261031)

Method: all 238 rows of the four R1d source CSVs concatenated in sorted-filename order (`r1d-fund-cases.csv`, `r1d-fund.csv`, `r1d-soc-survey.csv`, `r1d-soc.csv`), `random.seed(20261031); random.sample(rows, 24)` (10.1 %). For each row: fetched the URL (WebFetch, or curl + pdftotext when WebFetch returned raw PDF bytes or a TLS error), confirmed value/quote, and confirmed the figure as used in the document.

| id | status | fetched | source confirms row | doc matches row |
|---|---|---|---|---|
| S-fund-012 | verified | MISA Railway-Law PDF (pdftotext) | "Authority: Transport General Authority"; "Concessionaire: A legal person who is entrusted by law…"; "The governing text is the Arabic text" | funding.md 276, 309 ✓ |
| S-fund-003 | verified | MISA PSP-Law PDF | Art. 7: "limit set by the Council of Ministers … five years or more … within 60 business days"; (also Art. 1 "two or more", Art. 20 "not exceed 30 years") | funding.md 280, 282–283 ✓ |
| S-fund-030 | verified | not retrievable from the cited URL (site root) | could not confirm from URL; quote present in row | funding.md 293 ✓ (locator weak, §3 B2) |
| S-fund-218 | verified | info.gov.hk (served the Chinese page) | 南港島線（東段）建造成本 124億元, 觀塘線延線 53億元; 資金差額 99億元 及 33億元 | funding.md 84–85 ✓ |
| S-fund-220 | verified | same page | 向九鐵公司支付了49億1,000萬元 (= HKD 4.91 bn) | funding.md 88 ✓ |
| S-fund-210 | verified | jttri.or.jp PDF | "Approx. 17,8 million（as of Apr 1, 2020）… 12,4 million（as of Apr 1, 2021）"; also S-fund-209 450.0/252.0/113.0/57.0 bn yen | funding.md 59, 64 ✓ |
| S-fund-253 | verified | World Bank PDF | "These HSR JVs are analogous to tolled expressway companies"; also Y 2.5 trn/US$370 bn, Y 4 trn debt, 139/114/104 M/km, 40 M pax, Y 0.50/0.28 | funding.md 177, 181, 188, 191, 194 ✓ |
| S-fund-240 | verified | AIReF PDF (curl -k) | "8.740 km … 5.654 km … inversión mínima de 73.000 millones"; also 55.888, 14.086 (25,2 %), 15.858, 14,7/15,3, 30 M (4,8 %), 562,2 M | funding.md 147–159 ✓ |
| S-fund-227 | verified | IGEDD PDF (curl) | "20% de capitaux propres (773 M€) et 80% d'emprunts bancaires (3 029 M€)… prêt subordonné 765 M€… garantie de l'État, couvrant 73% (2 217 M€)"; also 8 176 M€2017, 3,9 Mds€ (48 %), 19,4–20,6 vs 18,6 M | funding.md 118–127 ✓ |
| S-fund-261 | secondary | railwaygazette.com | €6·74bn, 26 Oct 2011, 2 Saudi + 12 Spanish, 35 Talgo 350 + option 23, 3-year construction, 12-year O&M, 444 km | funding.md 238 ✓ |
| S-fund-263 | secondary | railwaygazette.com | until 2038; €2·8bn across the consortium; 20 trainsets; €1·3bn; Indra ≥5 years ≈€130m; 11 Feb 2026 | funding.md 248 ✓ |
| S-fund-208 | secondary | u-tokyo PDF | "In 1955, the Tokyu Corporation … began"; "did not receive any subsidies from the government"; also 29 %/41 %, 8 %/70 %, 75 %/16 % (S-fund-206/207/221) | funding.md 52, 57, 63, 103 ✓ |
| S-fund-258 | secondary | fnh.ma | 350 km; 180 km at 320 km/h; 160 km/h; 2 h vs 5 h; 6 M after 3 years; 2015; also 23 Mds MAD, +15 %, 51/28/21 % (S-fund-257) | funding.md 206, 209–216, 224–225 ✓ |
| S-soc-010 | secondary | Jadwa 2024 PDF | "78 percent of unemployed women … maximum travel time of one hour or within their area of residence … compared to 53 percent of men"; transport/childcare attribution present | social.md 93–94 ✓ |
| S-soc-009 | secondary | Jadwa Q4-2020 PDF: connection reset ×3 | not fetched | social.md 75: 33.2 / 24.4 match the row; male 7.1 not in the row claim (§3 B4) |
| S-soc-338 | secondary | argaam.com | SAR 11,034 Saudi, SAR 3,933 expatriate, 18.2 M employed, Q2 2025 | priors yaml, assumptions A-mode-006 ✓ |
| S-soc-002 | verified | GASTAT Excel not fetched (SHA recorded in licences-r1d) | n/a | social.md table matches row values ✓ |
| S-soc-323 | verified | laws.boe.gov.sa (curl -k) | "مرسوم ملكي رقم (م/19) وتاريخ 1443/2/9هـ … قرار مجلس الوزراء رقم (98)" | ethics-consent.md 82 ✓ |
| S-soc-327 | verified | same page | "المادة الثامنة عشرة: على جهة التحكم إتلاف البيانات الشخصية فور انتهاء الغرض من جمعها…" | ethics-consent.md 97, 151 ✓ |
| S-soc-308 | unverified | not fetched (row says DNS failure) | n/a | no figure used (design.md 22 says "could not be read") ✓ |
| S-fund-055 | unverified | not fetched | n/a | funding.md 312 marks it unverified; no figure ✓ |
| S-fund-256 | unverified | not fetched | n/a | funding.md 195 "unverified leads … Neither carries a figure" ✓ |
| S-soc-014 | unverified | not fetched | n/a | social.md 91 "unverified: snippets only" ✓ |
| S-soc-050 | unverified | not fetched | n/a | social.md 191 reports the NGO figure as "unverified; NGO figures … neither is endorsed" ✓ |

Extra (unsampled) check prompted by reading: S-fund-265 (Wikipedia, Haramain): 6.97 M (2023), US$9.4 bn, 25 Sep / 11 Oct 2018, 29 Sep 2019, 20 Mar 2020, 31 Mar 2021 confirmed; Wikipedia phrases 60 M/yr as "It was expected that the HHR will transport 60 million passengers a year", so funding.md's "design projection" (lines 247, 255) is a fair paraphrase; the 13 Jul 2021 reopening appears only in a reference title.

Result: 0 fabricated, 0 misquoted figures in the sample; 2 rows not fetchable (1 secondary, 1 Excel), 1 weak locator.

## 5. Three most important fixes

1. Write the R1d closing block in `docs/status/r1d.md` (case studies 7/7; Saudi-frame 3 clear / 16 unclear; social topics 8/8 with the evidence counts from social.md; survey files 6/6 + choice sets; elapsed) and end it with the plain-text line `R1d: done`; bump the header to v1.0. Integration then updates `docs/STATUS.md` and the cost log.
2. Replace every `logs/r1d/…` pointer in tracked deliverables (funding.md:367, social.md:5, survey/design.md:18, ethics-consent.md:189, analysis-plan.md:352, priors yaml header, licences-r1d rows 1 and 6) with `docs/assumptions-r1d.md` / `docs/licences-r1d.csv`.
3. Source hygiene: give S-fund-030 the document URL (or mark it secondary with the download provenance), add a URL to S-fund-255, and extend the S-soc-009 / S-soc-002 claim text to cover the male unemployment cells used in social.md lines 75–79. Carry the level-balance issue (design.md §5) into the status block as an open item for the fielding gate.

v1.0 verdict (superseded by section 6): FAIL

## 6. Re-verification (v1.1, 31 Oct 2026, HEAD `bf2c0ba`)

Re-verified 31 Oct 2026 11:26–11:40 +03 against HEAD `bf2c0ba` ("docs(r1d): verifier fixes … and handoff block"), read-only; nothing fixed. Scope: the six items the coordinator set ((a)–(f)) plus a fresh hygiene scan. `git status --porcelain` clean at start and end of the check (the only file I changed is this report).

### 6.1 Commands

| command | result | exit | wall |
|---|---|---|---|
| `make test` | ruff clean; 324 files already formatted; pytest **113 passed in 5.54 s**; `docver OK: 201 files`; `manifest OK: 16 rows` | 0 | 6.3 s |
| `uv run python -m funding.models validate` | OK: 14 options (6 families); sources resolve | 0 | <1 s |
| `uv run python -m funding.risk_matrix validate` | OK: template; 7 risks; 5 metrics | 0 | <1 s |
| `uv run python -m demand.survey design --config docs/survey/design.yaml --seed 1 --out /tmp/vr1d2/{a,b}.csv` | 690 rows, 3 blocks × 10 tasks, D-error 0.00785495 both runs | 0 | ~3 s each |

### 6.2 Items

| item | verdict | evidence |
|---|---|---|
| (a) `make test` green | PASS | table 6.1; 113 tests (same count as v1.0 plus nothing broken by the fix commit, which touched only docs/CSV/YAML comments) |
| (b) handoff block in `docs/status/r1d.md` | PASS | file is v1.0 (header line 1); section "Integration and handoff (31 Oct 2026, 11:25 +03)" + "Measured" + "Open items carried forward". Required counts present and **all re-measured by me**: case studies 7/7 with evidence grades (funding.md §1–§7); Saudi-frame 19 items = 3 clear / 16 unclear (my count over funding.md lines 300–349: `| clear |` ×3, `| unclear |` ×16), each unclear with its question (listed in the block); social topics 8/8 with evidence counts 8 (5/0/3), 6 (6/0/0), 17 (10/4/3), 7 (4/2/1), 3 (0/1/2), 3 (1/1/1), 4 (3/1/0), 8 (1/3/4) = exactly the "Evidence count" lines at social.md 42, 63, 106, 130, 147, 165, 183, 202; survey files 6/6 (+ design.yaml, meta) = `ls docs/survey` (8 files); elapsed 09:29 → 11:25; source-row tallies 56 (43/7/6), 67 (49/10/8), 52 (26/12/14), 63 (46/8/9) = my `status` column counts of the four CSVs. Level balance is in the open items ("middle levels appear 0 times, air fare SAR 180 in 26/27 tasks, design.md §5: accept on pilot evidence or regenerate with a minimum-appearances constraint"). The plain line `R1d: done` is absent by design (appended by the builder after this PASS; milestone-handoff order); the block's content is complete. |
| (c) no `logs/r1d` references | PASS | `git grep -n "logs/r1d" -- docs cities ':!docs/status'` → empty (exit 1); repo-wide `git grep -n "logs/r1d" \| grep -v ^docs/status` → empty. Pointers now read `docs/assumptions-r1d.md` / `docs/licences-r1d.csv` (funding.md:367, social.md:5, survey/design.md:18, priors yaml line 6, licences-r1d rows, r1d-soc.csv S-soc-025/031/032 and r1d-soc-survey.csv S-soc-334/335/349 `used_in`). |
| (d) S-fund-030 and S-fund-255 | PASS | **S-fund-030** (`docs/sources/r1d-fund.csv` line 31) now records: locator "'Ambitions of the Strategy by 2030' (printed p. 9)", the copy read (title "National Privatization Strategy", created 2026-01-29, SHA-256 `234b2e82…f722d4`), corroboration (Zawya article URL for the USD 64 bn; Argaam 1876229 for the 29 Jan 2026 launch), `primary_to_find` = exact NCP PDF URL. My independent check: the NCP strategy page links `https://www.ncp.gov.sa/EN/NationalStrategy/Documents/National-Privatization-Strategy.pdf`; downloaded (2,308,161 bytes, 24 pp., CreationDate 29 Jan 2026 15:32 +03) and its SHA-256 is **identical** to the row's hash; pdftotext p. 9: "Ambitions of … $64 billion … $11.5 billion / Total value for money from PPP". Both figures confirmed against the primary document. Argaam (29/01/2026) confirms "launch of the National Privatization Strategy, approved by the Cabinet on Nov. 25, 2025" and "$64 billion"; the Zawya page is account-gated and shows only the USD 64 bn in the visible lead, so the row's "Both figures corroborated by Zawya" is only half-visible to a reader without an account (the primary PDF settles it). **S-fund-255** (`r1d-fund-cases.csv`): `url` still empty, `status` unverified, `locator` "not read"; funding.md:195 "China State Railway Group's 2025 revenue, profit and debt ratio (S-fund-255) … are unverified leads. Neither carries a figure here" — confirmed: the 1,298.7 / 4.34 / 62.5 values in the row appear nowhere in funding.md. Rule 1 holds. |
| (e) male unemployment cells covered | PASS | **S-soc-002** claim now ends "Saudi male, same table: Q4 2021 5.4; Q4 2022 4.3; Q4 2023 4.6; Q4 2024 4.3 (rounded from 5.366, 4.313, 4.600, 4.328 …)", value "… male 5.4; 4.3; 4.6; 4.3; 5.6". My re-read of `/tmp/r1dsoc/lms/lfs_q4_2025.xlsx` sheet `2-1` (`uv run --with openpyxl python -I`), column Saudi/Male, rows 2021 Q4 … 2025 Q4: **5.366, 4.313, 4.600, 4.328, 5.576**; Saudi/Female: 22.936, 15.675, 13.907, 11.854, 10.312 → social.md lines 76–80 (5.4/4.3/4.6/4.3/5.6; 22.9/15.7/13.9/11.9/10.3) all match. **S-soc-009** claim now includes "Saudi male unemployment 7.1 (Q3 2020: 7.9)", value "24.4; 33.2; male 7.1"; `pdftotext -layout /tmp/r1dsoc/jadwa/q42020.pdf` p. 1 side table: "Male 7.1 7.9 / Female 24.4 30.2 … Female 33.2 31.3" → social.md line 75 (33.2 / 24.4 / 7.1) matches. Semantic diff of `r1d-soc.csv` between `55b69c7` and `bf2c0ba`: only S-soc-002 and S-soc-009 (claim + value) and the three `used_in` repoints changed; the 106-line textual diff is CSV re-quoting; 52 rows, ids unique, no value changed elsewhere. |
| (f) nothing broken | PASS | id resolution over funding.md, social.md, both funding YAMLs, priors yaml, assumptions-r1d, licences-r1d, status/r1d, survey/*: 1,049 S-refs and 341 A-refs, **0 undefined**; 92 A-rows in assumptions-r1d.md; all four source CSVs have unique ids (56/67/52/63). docver OK 201 files; manifest OK 16 rows. Determinism: two fresh seed-1 runs and the committed `docs/survey/choice_sets.csv` share SHA-256 `301f782b92043f3b849ba09d62b8eeac5d924d157a1afae2fc67a5c9faa6f7b7`; `meta.json` identical after dropping `code_version` (regenerated `cp1-10-gbf2c0ba`, committed `cp1-3-g557f4bd-dirty`): seed, config hash, data hash, D-error, level balance and the S-estimate unchanged. Hygiene: `git status --porcelain` clean; no `/Users/` in any R1d-owned file; no claude/opus/fable/haiku/sonnet/gpt in funding.md, social.md, survey/*, funding YAMLs or priors; "insurance" matches only "Ping An Insurance" as a minority JV shareholder in the China case (funding.md:177, S-fund-247 World Bank), which is a sourced fact, not content from the author's company; `git ls-files data runs movies logs film/renders film/audio` = the pre-existing `data/README.md` and `data/ksa/tables/*` only; no secrets pattern; no `git push` outside prompts/agent files. |

### 6.3 Status of the v1.0 defects

| v1.0 item | now |
|---|---|
| A. FAIL: no handoff block | closed (item b) |
| B1. `logs/r1d/` pointers (7 places) | closed (item c) |
| B2. S-fund-030 locator | closed for rule 1 (figures verified against the primary PDF by hash); residual: `url` column is still the site root; the document URL is `https://www.ncp.gov.sa/EN/NationalStrategy/Documents/National-Privatization-Strategy.pdf` (found by me 31 Oct 2026; builder to record it at integration) |
| B3. S-fund-255 empty URL | accepted: unverified, no figure used, `primary_to_find` names the bond-market report; residual format gap only |
| B4. male cells S-soc-002/009 | closed (item e) |
| B5. level balance | carried into the status block's open items as required |
| B6. cosmetics ("25-25" at funding.md:38; "-dirty" code_version in the committed meta) | unchanged; cosmetic, not blocking |

Outside the builder's ownership, unchanged since v1.0 and left for the coordinator's integration run: `docs/STATUS.md` line 15 still lists R1a–R1d as "not started"; `docs/cost-log.md` has no R1d row (the status block says the coordinator logs it from the run's JSON).

### 6.4 Three items for integration (none blocks R1d)

1. Record the NCP PDF URL above in S-fund-030 `url` when the four `r1d-*.csv` files are merged into `docs/sources/index.csv`.
2. Append `R1d: done` to `docs/status/r1d.md`, then update `docs/STATUS.md` (R1d row) and add the cost-log row.
3. Keep the level-balance item on the fielding checkpoint list (regenerate with a minimum-appearances constraint or accept on pilot evidence) and the Arabic native-speaker review (A-social-136).

Verdict: PASS
