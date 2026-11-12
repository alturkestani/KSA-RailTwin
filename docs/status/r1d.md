> **Document version:** docs/status/r1d.md v1.0 | 31 Oct 2026 | Author: R1d builder | Status: reviewed

# Track r1d: funding/PPP and Saudi frame (W6) + social, culture and survey design (W7)

## R1d (started 31 Oct 2026, 09:29 +03)

Plan: four subagents in parallel (funding-ppp-analyst ×2: options + Saudi frame / case studies; socio-culture-analyst ×2: literature review + equity method / survey design); the builder writes `funding/` and `demand/survey.py` code, tests and integration.

Decisions
- 31 Oct 2026: source rows live in track files `docs/sources/r1d-fund.csv` and `docs/sources/r1d-soc.csv` (same columns as `docs/sources/index.csv`); integration merges them into the index. Id ranges are split per subagent so no id is reused: S-fund-001…199 options and Saudi frame, S-fund-200…399 case studies; S-soc-001…299 literature review, S-soc-300…499 survey.
- 31 Oct 2026: assumption ids A-fund-001…099 (options/frame), A-fund-100…199 (cases), A-social-001…099 (review/equity), A-social-100…199 (survey), A-mode-001…099 (mode-choice priors).
- 31 Oct 2026: the survey design generator is own code on numpy (already a dependency): no new package, so nothing to add to the licence register beyond the method citation.

### Resume (31 Oct 2026, ~09:50 +03)
- The first session's subagents stopped before writing their outputs. Kept: `funding/` code and tests, `demand/survey.py` and tests, `docs/survey/design.yaml`, `cities/ksa/assumptions/mode_choice_priors.yaml`, `docs/sources/r1d-soc-survey.csv` (39 rows), `logs/r1d/assumptions-social-B.md`. Their raw downloads in /tmp are reused as reading copies; every figure still gets its own source row. Leads in `logs/r1d/RESUME_LEADS.md` (scratch).
- Generator check: `uv run python -m demand.survey design --config docs/survey/design.yaml --seed 1 --out docs/survey/choice_sets.csv` wrote 690 rows (3 blocks × 10 tasks incl. the dominance task), D-error 0.00785.
- Relaunched four subagents: funding A (options register, Saudi frame, risk-matrix template, fiscal metrics), funding B (seven case studies), social A (literature review + equity method), social B (survey documents).

### Integration and handoff (31 Oct 2026, 11:25 +03)
- The relaunched background subagents ended without writing or notifying (the same failure as the first session). Rerun 10:55 as foreground subagents that save each section as it is finished; all four completed.
- Integrated: case studies spliced into `docs/funding.md` (v0.2); assumption fragments merged into `docs/assumptions-r1d.md` (92 rows, no duplicate ids); licence fragments merged into `docs/licences-r1d.{md,csv}` (12 rows; MoF table and PFRAM licences `unclear`, UNESCO list CC BY-SA, xlogit PyPI-MIT vs GitHub-GPL conflict: all flagged for a check before release, none resolved silently). References to scratch fragments under `logs/r1d/` repointed to the tracked registers.
- Kept an S-estimate (Ngene eq. 7.9 lower bound) that the survey subagent added to `demand/survey.py`; added a test. The committed choice sets are unchanged (seed 1, byte-identical).
- Worktree data: `data/ksa/{hail,northern_borders,pilot-qassim,regions-pilot}` symlinked to the main checkout's gitignored pilot data so `manifest verify` can check the 12 pilot rows (nothing copied, nothing committed).
- Verifier pass 1 (`docs/status/verify-R1d.md`): 11/12 PASS; FAIL only on this missing block. Fixed alongside: the `logs/r1d/` references; S-fund-030 locator (document SHA-256 and corroborating press; exact NCP PDF URL still to find); S-soc-002/S-soc-009 extended to cover the male unemployment cells (re-read from the GASTAT Q4 2025 workbook Table 2-1 and the Jadwa Q4 2020 PDF). S-fund-255 stays unverified with no URL: it carries no figure.

Measured
- `make test`: ruff clean, 113 tests passed, docver OK (201 files), manifest OK (16 rows). `funding.models validate`: 14 options (13 required + `hybrid_public_dbfm_plus_station_lvc`). `funding.risk_matrix validate`: template, 7 risks, 5 metrics.
- Survey generator: seed 1 → 690 rows, 3 blocks × 9 design tasks + 1 dominance task, D-error 0.00785495; two reruns byte-identical to `docs/survey/choice_sets.csv`.
- Source rows (verified / secondary / unverified): r1d-fund 56 (43/7/6); r1d-fund-cases 67 (49/10/8); r1d-soc 52 (26/12/14); r1d-soc-survey 63 (46/8/9).
- Case studies 7/7 (Japan B, MTR A–, France A, Spain A, China A–/C, Morocco C, Haramain C+ evidence grades).
- Saudi-frame items 19: 3 clear, 16 unclear with the precise question each (PSP Implementing Regulations and Railway Law regulation not read in primary text; PIF Law primary text blocked (403); SAR ownership and corporate form not stated on SAR's site; no NCP PPP/VfM manual, no Saudi appraisal guide, no budget contingent-liability disclosure; which agency signs a rail PPP and how PSP Law and Railway Law Art. 32 interact; no official reason for the end of the Landbridge PPP talks).
- Social topics 8/8 (evidence counts, v/s/u): commuting 8 (5/0/3); heat and first/last mile 6 (6/0/0); women's mobility and LFP 17 (10/4/3, trend table Q4 2018–Q4 2025 with the 2022, 2024 and 2025 series breaks); family, weekend, Eid, Hajj/Umrah 7 (4/2/1); remote/hybrid work 3 (0/1/2); housing and decentralisation 3 (1/1/1); regional jobs and Saudisation 4 (3/1/0); land, heritage, displacement 8 (1/3/4). Gaps written as "no Saudi evidence found; nearest evidence: …" (tribal ties: no evidence found, no claim made). Equity method: Part B, no results; income by region blocked (HIES 2023 PDF 404).
- Survey files 6/6: design.md, instrument.en.md, instrument.ar.md, ethics-consent.md, analysis-plan.md, choice_sets.csv (+ design.yaml, meta). Designed, not fielded; no form, no contact.
- Elapsed: 09:29 → 11:25 (about 2 h; two failed background launches included). Cost row: logged by the coordinator from the run's JSON (`common.cost_log add`); this builder has no result file of its own run.

Open items carried forward (not R1d blockers)
- Before fielding (CP for Tariq): native-speaker review of the Arabic instrument and consent (A-social-136); institutional ethics approval; the PDPL Implementing Regulation (S-soc-361 unverified) for consent and transfer details; whether a stated prayer-facility preference counts as sensitive data (ethics-consent Q2); level balance of the linear attributes (middle levels appear 0 times, air fare SAR 180 in 26/27 tasks, design.md §5): accept on pilot evidence or regenerate with a minimum-appearances constraint.
- For R7: primary texts of the PSP and Railway Law implementing regulations; PIF Law; SAR ownership; Haramain O&M contract form and value; Al Boraq lender split; the risk-transfer value (A-fund-007) has no Saudi benchmark.
- For integration: merge `docs/sources/r1d-*.csv` into `docs/sources/index.csv`, `docs/assumptions-r1d.md` into `docs/assumptions.md`, `docs/licences-r1d.*` into `docs/licences.*`; update `docs/STATUS.md` (coordinator-owned).

Verifier pass 2 (`docs/status/verify-R1d.md` v1.1, 31 Oct 2026): Verdict PASS. Afterwards S-fund-030 got the NCP PDF URL the verifier located (hash matched) and funding.md row `lvc_tax_increment` reads "25" instead of "25-25".

R1d: done
