> **Document version:** prompts/R1b.md v1.0 | 30 Oct 2026 | Author: coordinator | Status: active

# R1b — global benchmark dossiers (W5), worktree `r1b`

You are a Claude Code builder on `claude-opus-5-5` in worktree `r1b`. Owner: `benchmarks-researcher` (run it as a subagent per country on `claude-haiku-5-5` for collection, in batches of four; you do the synthesis). Skills: `benchmark-dossier`, `source-citation`, `assumptions-register`, `licence-register`, `milestone-handoff`. Research only (WebSearch/WebFetch, published reports, court-of-auditors reports, peer-reviewed literature); no downloads over 50 MB; disk gate applies to nothing you need here. No real-world action: never contact an operator or author.

## You own
`docs/benchmarks/` (one file per slug + `README.md`), `rail/benchmarks.py` (`summarise` command), `cities/ksa/benchmarks/metrics.csv` (the cross-country metric table, one row per system × metric × source), `docs/sources/*` (your `S-nnn` rows, prefix `S-bench-`), `docs/assumptions-r1b.md`, `docs/licences-r1b.{md,csv}`, `docs/status/r1b.md`, `tests/test_benchmarks.py`.

## Tasks
1. **One dossier per slug**, every one of them (rule 2: no silent omission): `france`, `japan`, `spain`, `germany`, `china`, `south_korea`, `italy`, `morocco`, `turkey`, `uae`, `egypt`, `cautionary` (California HSR, UK HS2, plus others you find with sources), `population_growth_peers`. Use the `benchmark-dossier` template sections in order. A metric with no reliable data is written as "no reliable data found (searched: <where>, <date>)", never estimated.
2. **Metrics per system** (each a row in `cities/ksa/benchmarks/metrics.csv` with `S-nnn`, price year, currency, evidence grade A–D): cost/km (as published and converted to a common price year via a documented index in `cities/ksa/costs/index.yaml` if R1c has created it, else your own `index-r1b.yaml` to be merged), ridership vs forecast (first years and mature), farebox recovery / operating ratio, population density and city-size thresholds used in planning, the distance band where rail won against air and car (test the commonly cited ~200–800 km band: cite the studies, do not assert it), station spacing, timetable and stopping patterns, cost and schedule overruns, delivery model (public, concession, PPP, vertical separation).
3. **Small-town evidence** section per dossier where relevant and a cross-cutting `docs/benchmarks/small-towns.md`: Shinkansen intermediate stations, TGV stations outside towns ("gares des betteraves"), AVE intermediate stops; summarise each empirical study with its method, sample and finding; say clearly where evidence is mixed or negative. Grade every study.
4. **Population-growth peers** (`population_growth_peers.md`): how countries with growing populations and good rail, and countries with shrinking ones, planned networks and housing around them (transit-oriented development, new towns, station-area policy); sources per claim.
5. **Cautionary class** (`cautionary.md`): capex, schedule and ridership outcomes vs plan, the stated causes in official reviews, and what each implies as a reference-class input (hand to R1c: write the candidate uplift observations into `cities/ksa/benchmarks/overruns.csv` with sources; do not set uplifts yourself).
6. **Summary table**: `uv run python -m rail.benchmarks summarise --metrics cities/ksa/benchmarks/metrics.csv --out docs/benchmarks/README.md` renders the cross-country table with grades and a "gaps" list; test on a three-row fixture.
7. **Docs and registers**: every number in every dossier carries `[^S-bench-xxx]`; `docs/licences-r1b.*` lists any dataset or report with reuse terms (e.g. a statistics office table) that the project might reproduce.
8. **Handoff** (`milestone-handoff`, docs variant plus `make test`): `red-team-verifier` (it spot-checks 10 % of metric rows against their URLs), commits per dossier, status block in `docs/status/r1b.md` (dossiers written 13/13, metric rows, grade distribution, "no reliable data" count, elapsed). End with `R1b: done` or `R1b: blocked - <reason>`.

## Acceptance (the verifier checks these)
- 13 dossier files exist, each with every template section filled or marked "no reliable data found".
- Every metric row has a source id, a price year, a currency and a grade; grade D rows are excluded from `README.md` totals and flagged.
- The 200–800 km claim is treated as a hypothesis with cited evidence for and against, not as a fact.
- Small-town evidence summarises at least one empirical study per system where such studies exist and states where it does not.
- No advocacy language; no figure without a source; the summary table is generated, not hand-typed.
