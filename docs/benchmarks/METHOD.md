> **Document version:** docs/benchmarks/METHOD.md v1.4 | 31 Oct 2026 | Author: R1b builder; price-year conversion by CP2_PREP | Status: draft

# W5 benchmark method: file layout, metric table, grades and price-year conversion

Binding for every R1b dossier. Template and grades: `.claude/skills/benchmark-dossier/SKILL.md`. Citation record: `.claude/skills/source-citation/SKILL.md`.

## Files per dossier slug
| file | content |
|---|---|
| `docs/benchmarks/<slug>.md` | the dossier, template sections 1–10 in order, then `## Escalations` (optional) and `## Sources` |
| `docs/sources/bench-<slug>.csv` | one citation record per source, same columns as `docs/sources/index.csv` |
| `cities/ksa/benchmarks/metrics-<slug>.csv` | the dossier's metric rows (merged by the builder into `metrics.csv`) |
| `cities/ksa/benchmarks/overruns-<slug>.csv` | candidate reference-class observations (cautionary and any dossier with an outturn-vs-estimate figure) |

Slugs and source-id codes: france `fr`, japan `jp`, spain `es`, germany `de`, china `cn`, south_korea `kr`, italy `it`, morocco `ma`, turkey `tr`, uae `ae`, egypt `eg`, cautionary `caut`, population_growth_peers `pop`, small-towns `st`, price index `idx`. Source ids: `S-bench-<code>-<nnn>` (e.g. `S-bench-fr-007`), never reused.

## Metric table columns (`metrics.csv`)
`row_id, slug, system, metric, scope, value, value_low, value_high, unit, currency, price_year, year_observed, source_id, grade, notes`

- `row_id`: `M-<code>-<nnn>`.
- `metric` (controlled list): `network_km`, `opening_year`, `cost_per_km`, `cost_total`, `ridership_annual`, `ridership_vs_forecast`, `farebox_recovery`, `operating_ratio`, `density_threshold`, `city_size_threshold`, `rail_share_by_distance`, `station_spacing_km`, `stopping_pattern`, `cost_overrun_pct`, `schedule_overrun_years`, `delivery_model`.
- `value`: as printed in the source (numeric where the metric is numeric; text for `delivery_model`, `stopping_pattern` and qualitative thresholds). `value_low`/`value_high` only when the source gives a range.
- Money: `unit` = `m/km` (millions of `currency` per route-km) or `m` (millions, totals); `currency` = ISO code as printed (EUR, JPY, USD, GBP, CNY, KRW, TRY, MAD, AED, EGP, TWD); `price_year` = the year the source states, or the year of the estimate/award with `notes: price year inferred from <...>`; `unknown` (with the reason in `notes`) when the source is undated or gives a span; never blank, never guessed. Rows with `unknown` are shown "not converted (price year unknown)". Gaps are not metric rows: a metric with no data is stated in the dossier, not written as an empty row.
- Non-money rows: `currency` = `n/a`, `price_year` = `n/a`; `year_observed` = the year the value describes.
- `ridership_vs_forecast` = outturn / forecast (ratio, unitless); scope says which forecast (at decision) and which outturn year.
- `cost_overrun_pct` = (outturn − baseline) / baseline × 100; scope names the baseline (decision to build, contract award, ...).
- `scope`: line or section, city pair, speed class, or "network".
- `grade`: A primary official (operator, ministry, statistics office, audit court); B peer-reviewed or audited study; C reputable secondary (ITF/OECD, UIC, World Bank, major press with named sources); D unverified (Wikipedia, blogs, unsourced press, search snippets not opened). Grade D rows are kept as "to verify" and excluded from the README totals.

## Overruns table columns (`overruns.csv`)
`obs_id, project, country, kind, baseline_desc, baseline_value, baseline_year, outturn_desc, outturn_value, outturn_year, unit, currency, price_basis, ratio, source_id, grade, notes`
`kind` = `capex` | `schedule` | `ridership`; `ratio` = outturn / baseline as computed from the two printed values (computed, not printed by the source, unless the source prints it; say which in `notes`). These are candidate observations for R1c (`reference-class-forecasting`); R1b sets no uplift.

## Evidence rules
1. A figure enters only if it was read on a page or document actually opened (WebFetch, or a PDF downloaded to `logs/r1b/pdf/<slug>/` and read with `pdftotext`). The citation record carries a verbatim quote of ≤ 25 words containing the figure.
2. A figure seen only in a search snippet: grade D, status `unverified`, "to verify".
3. Wikipedia and other aggregators: status `secondary`, grade D, `primary_to_find` named.
4. Paywalled papers: cite the abstract only (status `verified` for what the abstract says), say so.
5. A metric with nothing reliable: "no reliable data found (searched: <where>, <date>)". Never estimate.
6. Conflicting figures: both rows, and a line in the dossier's Gaps section; never pick silently.

## Price-year conversion (the single index, `cities/ksa/costs/index.yaml`)
Target: SAR, price year 2025 (A-cost-001). Since CP2 P2a (Tariq, 31 Oct 2026) the project has one price index, `cities/ksa/costs/index.yaml`, built by `uv run python -m costs.index_build` (A-cost-002); the R1b index `index-r1b.yaml` (A-bench-001, now superseded) was folded into it with its source rows S-bench-idx-001…003 and then deleted. Rule: SAR items are inflated with the Saudi CPI (S-cost-idx-001); foreign-currency figures are inflated with the source economy's GDP deflator (World Bank WDI NY.GDP.DEFL.ZS) to 2025 **before** conversion, then converted at the 2025 annual average official exchange rate (PA.NUS.FCRF) to USD and to SAR at the peg 3.75. EUR figures located in a euro-area economy (FRA, DEU, ESP, ITA, PRT) use that economy's deflator (factor ids `I-eur-<economy>-<year>-sar-2025`). Series exceptions (A-cost-307): EUR figures outside the euro area use the Eurostat EA20 deflator; AED uses the UAE CPI (WDI has no 2025 UAE deflator); TWD is not in WDI and is not converted. Sensitivity (factor ids ending `-cti`): convert at the price-year rate and the peg, then inflate with the Saudi CPI; it needs the Saudi CPI at the price year (from 2000). `rail.benchmarks summarise` prints both next to the nominal figure with the factor ids; where a factor is missing the cell says "not converted". Market exchange rates, not PPP, are used (the PPP argument of A-bench-001 still applies); cross-country cost comparisons remain indicative. The change against the former routes A/B is logged, value by value, in `normalisation-delta.md` (`uv run python -m rail.benchmarks delta --before <csv> --out docs/benchmarks/normalisation-delta.md`).

## Cost levels (`cost_levels.yaml`)
Each `cost_per_km` row is classified by the coordinator as `line`, `average`, `estimate`, `package`, `unbuilt` or `other` (definitions in the YAML header). Only `line` and `average` rows enter the per-dossier ranges in `README.md`; all rows stay listed in the cost table.
