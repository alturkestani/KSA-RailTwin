---
name: source-citation
description: The citation record every number, quote and factual claim in this repository must carry (URL, publisher, title, dates, page, quote, status), how to cite inline in Markdown with S-xxx footnotes and the docs/sources index, how to treat secondary aggregators, and the digit-by-digit bilingual check. Use whenever writing a figure or a fact into any document, register, script or report.
---
> **Document version:** skills/source-citation/SKILL.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# Source citation

Rule 1 of PROJECT.md: every figure is sourced or flagged as an assumption; a guess presented as fact is a verifier FAIL. This skill gives the mechanics.

## The citation record
Every source gets one entry in `docs/sources/index.csv` (and the human view `docs/sources/index.md`), id `S-<nnn>`:

| field | type | notes |
|---|---|---|
| id | `S-nnn` | unique, never reused |
| claim | text | what we take from it, one sentence |
| value | number or text | exactly as printed in the source |
| unit | text | km, SAR bn, passengers/yr, % ... (price year for money) |
| url | URL | the page or PDF actually read |
| publisher | text | GASTAT, SAR, MEED, Renfe, ... |
| title | text | document or page title |
| published | date | as stated; `unknown` if absent |
| accessed | date | the day it was read, Asia/Riyadh |
| locator | text | page, table, figure or section |
| quote | ≤25 words | verbatim, in quotation marks, original language |
| status | `verified` / `secondary` / `unverified` | see below |
| primary_to_find | text | required when status = secondary |
| used_in | paths | files that cite it |

- `verified`: read on the publisher's own site or document on the access date.
- `secondary`: taken from an aggregator (Wikipedia, citypopulation.de, press). Mark it, name the primary source to find in `primary_to_find`, and never let a secondary figure reach the report or the film without a verified replacement or an explicit "secondary" label.
- `unverified`: could not be read (paywall, WAF, dead link). It may be mentioned as unverified; it cannot feed a model or a narrated line.

## Inline citation
Markdown: `Haramain HSR is about 450 km long[^S-012].` with `[^S-012]: SAR/HHR, "Network", https://..., accessed 2026-10-31.` at the foot of the file, or the compact form `(S-012)` in tables. YAML: `source: S-012`. Code never embeds a figure; it reads YAML that carries `source:`.

CLI: `uv run python -m common.sources add --claim ... --value ... --url ... --publisher ... --title ... --published ... --locator ... --quote ... --status verified` appends and prints the id; `uv run python -m common.sources check <files>` finds `S-xxx` ids with no index row and numbers in tables with no citation or assumption id.

## Rules that bite
- Dates matter: SAR/HHR facts, fares, timetables and press figures carry the date sampled; a figure without a date is unverified.
- Conflicting figures (e.g. the Landbridge SR100 bn vs USD 7 bn) get two records and a `docs/sources/conflicts.md` entry; never pick one silently.
- Quotes: only verifiable published statements, verbatim, with the source. No paraphrase presented as a quote (rule 1 and W10 fact rule).
- Access date, not just publication date, on every record; re-verify grounding facts (PROJECT.md section 4) and record the new access date.
- Secondary aggregators must be replaced with the primary table where the brief says so (GASTAT census population).

## Digit-by-digit bilingual check
For every document that exists in Arabic and English (executive summary, film scripts, subtitles): extract every number from both versions with `uv run python -m common.sources bilingual-check <en.md> <ar.md>`; the tool normalises Arabic-Indic digits, thousands separators and decimal marks and prints any figure present in one version and not the other, or different. The `red-team-verifier` runs it; a mismatch is a FAIL.
