> **Document version:** prompts/LANDBRIDGE_RECONCILE.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# LANDBRIDGE_RECONCILE — reconcile the Landbridge cost figures (judgement run, main checkout, claude-fable-5-1)

Tariq asked (30 Oct 2026): "can you try to come up with the math?" This run reviews and completes the Landbridge entry that `DATASCOUT_1H` wrote in `docs/sources/conflicts.md`; it is a research and arithmetic task, not a modelling task. Use the `source-citation` skill for every figure and the `cost-register` skill's top-down table format for the per-km comparison.

## You own
`docs/sources/conflicts.md` (the Landbridge section only), `docs/costs-landbridge.md` (new), your `S-nnn` rows in `docs/sources/index.csv` (prefix `S-lb-`), `docs/status/main.md` (your block only).

## Tasks
1. Read the DATASCOUT_1H entry and its sources. Re-fetch the primary pages (MEED Jan and Jul 2026, ENR Jun 2026, meedprojects.com pid=114639, SAR press releases, SPA, Railway Gazette/International Railway Journal) and quote each cost statement with its date, currency and what it says the figure covers. Search for the original Arabic statements (SPA, Al-Eqtisadiah, Argaam, Asharq Business) — the SAR CEO's SR 100 bn quote likely exists in Arabic first.
2. **Arithmetic, shown step by step** (every input cited or labelled assumption):
   - FX: SAR/USD peg 3.75 (cite SAMA). SR 100 bn = USD 26.67 bn; USD 7 bn = SR 26.25 bn (26.25 % of SR 100 bn).
   - Lengths: the new Riyadh–Jeddah line (~900–950 km, two sources) and the whole programme ("more than 1,500 km of new track"); compute USD/km for each figure over each length (four cells) and compare with: Haramain HSR (cost and 453 km), SAR North line, Etihad Rail stage 2, Al Boraq, and the cost-per-km bands for mixed freight/passenger lines in flat terrain from the benchmark literature (each cited; ranges, not points). State which cells are plausible against those bands and which are not.
   - Hypotheses to test, each with evidence or "no evidence found": (a) USD 7 bn = phase 1 (e.g. the Jeddah–Riyadh section only, or civil works only); (b) USD 7 bn = one contract package or the private share of the former PPP; (c) SR 100 bn includes rolling stock, stations, land, financing or the full >1,500 km programme while USD 7 bn is track-only; (d) different price years or an earlier (2008–2011) estimate repeated by ENR; (e) a reporting error (e.g. SR 7 bn? USD 27 bn misread?).
3. Write `docs/costs-landbridge.md`: version header; the two headline figures with sources; the arithmetic table; the hypothesis table with evidence grades (benchmark-dossier A–D); your conclusion labelled "analysis" with a confidence (low/medium/high) and the **range** the cost register should carry for the Landbridge (low/central/high, price year, what it covers), status `derived` or `unresolved`; what would resolve it (a document to find, a figure to request — Tariq asks, never you). No advocacy, no single-point claims.
4. Update the conflicts entry to point to the new page. Handoff: `uv run python -m common.docver check docs`, commit `docs(costs): Landbridge cost reconciliation (analysis)`, status block, end with `LANDBRIDGE_RECONCILE: done` or `blocked - <reason>`.

## Acceptance
- Every number has an `S-lb-nnn` row or an explicit assumption; the arithmetic reproduces from the cited inputs.
- The output is a range with a stated scope and price year, or an honest `unresolved` with the next step.
- No contact with MEED, ENR, SAR or anyone (rule 7).
