> **Document version:** prompts/VERIFY_GREENBOOK.md v1.0 | 31 Oct 2026 | Author: coordinator | Status: active

# VERIFY_GREENBOOK — quote the Green Book 2026 discount-rate table verbatim (read-only, claude-fable-5-1)

Tariq's CP1 condition (31 Oct 2026): decision D1a (adopt the Green Book 2026 schedule 3.00 % years 1–30, 2.50 % years 31–75, 2.25 % from year 76 as the central social discount rate, A-cba-001) stands **only if** the verifier quotes the rate table verbatim from the fetched primary pages recorded as S-cp1-060 and S-cp1-061 in `docs/sources/index.csv`. Otherwise D1b applies (keep 3.5 / 3.0 / 2.5 % as central, the 2026 schedule as a sensitivity).

## You own
`docs/status/verify-greenbook.md` (new) and your block in `docs/status/main.md`. Nothing else. Do not edit the register, the plan or the pack.

## Procedure
1. Read rows S-cp1-060, S-cp1-061 and S-cp1-062 in `docs/sources/index.csv` (URL, title, locator, quote).
2. Fetch each URL with WebFetch (the gov.uk PDFs; if a PDF does not render, fetch the gov.uk landing page that links it and then the PDF through the page link; try `curl -sL <url> | pdftotext - -` if `pdftotext` exists, else `uv run python -c "import pypdf"` is NOT allowed — use `uv run --with pdfplumber python -c ...` or `--with pymupdf`). Record for each: HTTP status, bytes, the document title on its cover, publication month/year on the cover or in the metadata, and the access timestamp.
3. Locate the standard discount-rate table or paragraph (Green Book 2026 chapter on discounting; the supplementary discounting guidance's rate schedule table). **Quote it verbatim**, including the headings and footnotes about the years, inside a fenced block, with the page number. Do the same for TAG A1.1 (S-cp1-062) to show the DfT schedule still in force.
4. Compare the quoted figures digit by digit with the values in `docs/assumptions.md` row A-cba-001 and `docs/plan.md` §2 and `docs/cp1-decision-pack.md` D1. Any discrepancy is a FAIL.
5. Write `docs/status/verify-greenbook.md`: version header; the three fetch records; the verbatim quotes; the comparison table; `VERDICT: PASS` (table quoted verbatim and figures match) or `VERDICT: FAIL` with the reason (page unreachable, table not found, figures differ). Then append to `docs/status/main.md` a short block and the line `VERIFY_GREENBOOK: done`. Commit `verify(greenbook): <PASS|FAIL> — Green Book 2026 rate table`. No push.

## Rules
No real-world action. If a page cannot be fetched after two attempts, say so; do not quote from memory, do not paraphrase as a quote.
