> **Document version:** docs/status/verify-FIX_R8.md v1.1 | 5 Nov 2026 | Author: red-team-verifier (claude-fable-5-1; v1.1: pass 2 appended) | Status: verified

# VERIFY_FIX_R8: red-team verification of the R8-checkpoint fix pass

Scope: `prompts/FIX_R8.md` items 1–4 and 7–9 (items 5 and 6 are the coordinator's), checked against HEAD `576d883` on `main` (`git describe`: `r8-10-g576d883`), ten commits on top of tag `r8`. Read-only; nothing fixed. Commands were run from the main checkout on 5 Nov 2026 (about 02:00–02:15 Asia/Riyadh).

## Commands and exit codes

| command | result |
|---|---|
| `make setup && make test` (README command; log `logs/verify-fixr8-maketest.log`) | exit 0, 37.6 s wall: `ruff check` "All checks passed!", `ruff format --check` "671 files already formatted", pytest green, `docver OK: 339 files`, `manifest OK: 386 rows` |
| `uv run pytest -o addopts="" -q` | **724 passed**, 10 warnings, 33.8 s (matches the status block) |
| `uv run pytest -o addopts="" -q tests/test_glossary_ar.py tests/test_ar_render.py tests/test_fix_r8.py` | 59 passed (49 + 4 + 6, as claimed) |
| `uv run python -m common.sources bilingual-check docs/executive-summary.en.md docs/executive-summary.ar.md` | PASS: 258 = 258 |
| same check on the tag-`r8` texts (`git show refs/tags/r8:…` to `/tmp/r8tag/`) | PASS: 254 = 254 (the `common/sources.py` isolate change leaves text without isolates unchanged) |
| `uv run python -m common.report check` | PASS |
| `uv run python -m common.licences check` | 290 Markdown rows, 290 CSV rows, 0 differ |
| `uv run python -m common.ar_render bidi-probe docs/report/figures/executive-summary.ar.html` | 29 numeric runs, 0 wrong, exit 0 |
| `uv run python -m common.ar_render bidi-probe runs/fix-r8/ar-render/before/executive-summary.ar.html` | 35 numeric runs, 23 wrong, exit 1 (the 23 WRONG lines include `−2,958 / −724 / +1,631`, `801 / 1,423 / 5,286`, `3–10`, `±5`, `−894`) |
| `uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/` then `uv run python -m common.report build`, then `git status --porcelain` | both exit 0; working tree still clean (idempotent; figures and report are generator output, not hand-edited) |
| `uv run python -m common.ar_render html docs/executive-summary.ar.md /tmp/verify-ar.html` vs the committed HTML | identical modulo the font href (reproducible) |
| `git status --porcelain` | clean before and after the rebuilds |
| `git tag --contains refs/tags/r8` | only `r8` (no tag created after r8) |
| `git diff refs/tags/r8 --stat -- prompts/R9.md prompts/R10.md prompts/VERIFY_R9.md prompts/VERIFY_R10.md prompts/INTEGRATE_R9.md film/` | empty |
| `git diff refs/tags/r8 -- . \| grep -n '/Users/'` | one hit, `tests/test_ar_render.py` asserting that `"/Users/"` is absent from the committed HTML (not a path) |
| `git diff refs/tags/r8 -- . \| grep -i 'git push\|api_key\|secret\|token='` | empty |
| private-list `git grep -n -i` | only the two agent files that state the rule (no content) |

## Criteria

| # | criterion | PASS/FAIL | evidence |
|---|---|---|---|
| 1 | `make test` green; README command exits 0; 724 tests | PASS | table above; `logs/verify-fixr8-maketest.log` ends `EXIT=0` |
| 2 | Item 1: fig09 EN/AR title in spec, deck CSV, figures index, report caption; rebuilt through the generator; idempotent | PASS | `common/figures.py:1925–1926` (`Phasing (2030, 2050) and stage gates (2027, 2047)` / `المراحل (2030 و2050) وبوابات القرار (2027 و2047)`); `docs/deck-figures/figures.csv:10`; `docs/report/figures/figures-index.csv:10`; `docs/report/sections/07-phased-programme.md:12` and `docs/report/feasibility-report.md:666,744`; `docs/deck-figures/fig09-stage-gates.png` viewed: both titles printed; rebuild left `git status` clean |
| 3 | Items 2 and 3: every Arabic string of the prompt present character by character; glossary; rejected forms; test; bilingual check; unit on the spur figure | PASS | programmatic `in` test (`/tmp/verify_ar_strings.py`, 26 strings incl. the fig09 AR title): **all 25 summary/glossary strings match the raw file text; none needed isolate stripping** (the isolates sit around signed numbers and ranges, not inside any prompt string); fig09 AR matches `figures.csv` and `figures.py`; `docs/glossary.ar.md` v1.1 header, 28 terms with preferred and rejected forms and source (23 Tariq, 5 builder, marked), §typography; robust-NPV gloss exactly once at first use (count 1, bare term 5); rejected forms `أجور`, `مسح`, `المتفائلة`, `القيمة الحالية الصامدة`, `اصطناعي`, `فرع الخرج` absent from the summary, `figures.csv` and `figures.py`; `tests/test_glossary_ar.py` reads the summary, `SPECS` `title_ar`, `figures.csv` and every Arabic-bearing file under `web/src` and `api` (only `web/src/views/RegisterView.tsx:104` `الاسم`); EN `SAR 4,231 m` at `docs/executive-summary.en.md:32`, AR `4,231 مليون ريال` at `docs/executive-summary.ar.md:42`; English draft note kept at line 4, Arabic note at line 5; bilingual check 258 = 258 |
| 4 | Item 4: RTL render, PDF, committed HTML < 300 KB and no home path, two PNGs ≤ 1 MB, probes, glossary rule, isolate test, `sources.py` additive | PASS | `docs/report/figures/executive-summary.ar.html` 17,606 B, `<html lang="ar" dir="rtl">`, fonts `url('../../../common/fonts/NotoNaskhArabic-Regular.ttf')` etc., 0 `/Users/`; `runs/fix-r8/ar-render/executive-summary.ar.pdf` 142,941 B plus `before/` set; `ar-render-page1.png` 411,470 B (1350 × 1910) and `ar-render-table.png` 89,519 B (1254 × 425), both viewed: ranges read `−2,958 / −724 / +1,631` left to right with signs left of digits, `P10 / P50 / P90` in order, Arabic prose RTL; probes 0/29 after and 23/35 before; `docs/glossary.ar.md` §2 Typography states the rule, the before/after numbers and `RUN_PATTERN`; `tests/test_ar_render.py::test_every_numeric_run_of_the_ar_summary_is_isolated` (29 U+2066 and 29 U+2069 in the file); `common/sources.py` diff adds only U+2066–U+2069 to `_SIGN_OK_BEFORE`; tag-r8 texts still 254 = 254 |
| 5 | Item 7: `docs/plan.md` line 110 without model names; neutral report sentence; `common.report check` | PASS | `docs/plan.md:110` reads "Opus-class … Haiku-class … verifier runs"; `docs/report/sections/00-front-matter.md:11` and `feasibility-report.md:77` start "The study compares options for extending Saudi Arabia's rail network: which corridors, in what order, at what cost, with what long-term benefit, funded and owned by whom, and with what effect on people."; no "should build" left in the report; `common.report check` PASS. The run table at `plan.md:93–104` still says Opus / Haiku / Fable, which is outside the item (line 110 only) and covered by the CP3 7a exemption recorded at `docs/STATUS.md:114,120` |
| 6 | Item 8: blockers file complete; count independently recounted; grouped; HARD STOP with dependency list; no licence status changed | PASS | independent count: `sed -n '62,385p' docs/licences-release.md \| grep -c '\| \*\*BLOCKER\*\* \|'` = **46**; the 46 §5 row ids equal the 46 ids in `docs/licences-blockers.md` (1 7 94 117 … 290, same set); the "48" in the prompt is explained: `grep -c '**BLOCKER**'` over the whole release note gives 48 because the legend (line 11) and the §1 prose (line 31) also contain the string; the file states the count and the discrepancy (lines 7, 19); 8 groups in the required order (21 / 9 / 2 / 6 / 2 / 3 / 0 / 3 = 46); every row has register id, item, flag, terms text, used in, question (`test_licence_blockers_file_parses_and_matches_the_register` also checks non-empty questions); HARD STOP section at line 21 with the 16-hit dependency table. My own grep of `docs/` (minus status logs), `cities/ksa/benchmarks/` (0 hits) and 1,975 `runs/**/meta.json` (0 hits) reproduces the 16 hits; judgement: **no figure, table, benchmark or run draws on it**: `cities/ksa/costs/cost_register.yaml:1459–1475` row -034 has low/central/high null, `source: ''`, `status: unknown`, and `costs/config/estimate_map.yaml:10` maps commuter to the proxy C-line-type-conv-ec-base-006 (A-cost-013). Licence register: `docs/licences.csv` vs `refs/tags/r8` compared row by row on licence, open, commercial_use, status, approval: 0 differences; only the two `used_in` cells (markdown-it-py, Google Chrome) changed, as claimed |
| 7a | S1 negative NPV always "in the model" | PASS | re-grep (table below): every −337,555 / −60,103 occurrence sits in a sentence, table head or heading with "in the model" / `في النموذج`; the remaining `60,103` hits are AlUla's population (`annex-assumptions.md:445`, `annex-regions/madinah.md:18`); `figures.csv` has none; `سالباً` at AR :42–43 refers to S6-L1/S6-L3 at P90 cost, not S1 |
| 7b | Al-Kharj 4,231 always a layout difference, never an additive share; numbers confirmed | **FAIL** | the six `4,231` sentences are rewritten as differences (table below) and the arithmetic holds: `runs/r6/top5/top5.csv` `robust_npv` S6-L1 11,022.936 − S6-L2 6,791.610 = 4,231.33; `runs/r7/corridors/S3-branch_spur-al-kharj@2050/score.json` `robust_npv` 4,309.15 (standalone, so not a share). **But `docs/r6-topology.md:45` still reads "its value hangs on the Al-Kharj spur (SAR 4.2 bn of the 11.0 bn)"**: the same figure, rounded, presented as a share of the 11,023 in the very document the builder edited for this item (v1.4, line 80). The grep terms `4,231`/`4231` and the test regex `4,?231` do not catch the "4.2 bn" spelling, which is why it survived. Tariq's rule is "never as an additive share"; this is one |
| 7c | 120-minute reach always "door-to-door from the five metros"; national reach "reported only" | PASS | re-grep (table below): every reach sentence in the EN/AR summaries, brief, report sections and `figures-index.csv` carries the qualifier; national reach says "reported only" at `04-results.md:187`, `03-methods.md:97`, `r6-topology.md:38–39,144,152`; `40–120 road-km` hits (02:20, 04:205, 04:209) are the 30-minute lens, not the reach measure; fig08 y-axis now "…of the five metros" (`common/figures.py:1161`). Observation: `docs/r6-topology.md:99` table head "Reach gain 120 min" has no qualifier (internal R6 note; its §0.1 row 35 defines the measure) |
| 8 | R9/R10 untouched; no tag after r8; nothing pushed | PASS | empty diff on the R9/R10 prompts and `film/`; `git tag --contains refs/tags/r8` = `r8` only; no `git push` in the diff; `git status` clean |
| 9 | Headers bumped; one commit per item; no model names in public docs touched; no content from the author's company; no home paths | PASS | version bumps vs r8: STATUS v1.30→1.31, deck README v1.1→1.2, AR summary v0.3→0.7, EN summary v0.2→0.4, glossary new v1.1, blockers new v1.0, licences.md v1.9→1.10, plan v0.12→0.13, brief v0.2→0.3, r6-topology v1.3→1.4, report v1.0→1.3, figures README v1.2→1.3, sections 00/01/04 v1.0→1.1, 07 v1.0→1.2, status/main v1.14→1.15; `git log --oneline refs/tags/r8..HEAD`: items 1, 3, 2, 9, 4, 7, 8 each one commit, plus a register follow-up (d122b08) and the status commit; grep for opus/haiku/fable/claude- over the report, sections, brief, summaries, glossary and blockers file: only `licences-blockers.md:117` "Claude Code / [model ids: see docs/licences.md]" (redacted, as in the release table); no content from the author's company; no `/Users/` in tracked files |
| 10 | Non-partisan, "in the model", labels present | PASS | `common.report check` PASS; neutral front-matter sentence; the label line is on every modelled output seen (summaries, brief table, report tables, figures); no "should build"/"will" advocacy found in the touched documents |

## 9a re-grep (verifier)

| file:line | occurrence | "in the model" | verdict |
|---|---|---|---|
| docs/executive-summary.en.md:13 | −337,555 / −60,103 | same sentence ("In the model S1 itself…") | ok |
| docs/executive-summary.ar.md:19 | −337,555 / −60,103 | same sentence (`وفي النموذج يبلغ`) | ok |
| docs/policy-brief.md:33 | table row | table head line 31 "committed programme S1 vs S0, in the model" | ok |
| docs/report/sections/01-executive-summary.md:16 = report:121 | "does not pass in the model", −60,103 | same sentence | ok |
| docs/report/sections/04-results.md:25 = report:305 | gen:s1 row | head "NPV in the model, P10 / P50 / P90" and paragraph :18 "In the model, S1 against S0…" | ok |
| docs/report/annex-assumptions.md:445; annex-regions/madinah.md:18 | 60,103 | AlUla population | n/a |
| docs/executive-summary.ar.md:42, :43 | `سالباً` | S6-L1 / S6-L3 at P90 cost | n/a |
| docs/deck-figures/figures.csv | none | | |

## 9b re-grep (verifier)

| file:line | wording | verdict |
|---|---|---|
| docs/executive-summary.en.md:32 | "the difference between S6-L1 and the same layout without the spur is SAR 4,231 m of robust NPV; that layout is S6-L2" | ok |
| docs/executive-summary.ar.md:42 | `الفرق بين S6-L1 والمخطط نفسه دون الخط الفرعي إلى الخرج هو 4,231 مليون ريال من صافي القيمة الحالية الصامد؛ وذلك المخطط هو S6-L2` | ok |
| docs/policy-brief.md:61 | "the difference between S6-L1 and the same layout without the spur (S6-L2) is SAR 4,231 m of robust NPV" | ok |
| docs/report/sections/01-executive-summary.md:19 = report:124 | "The difference between S6-L1 and the same layout without the spur is SAR 4,231 m of robust NPV (S6-L1 − S6-L2, …)" | ok |
| docs/report/sections/04-results.md:99 = report:379 | "the difference between S6-L1 and the same layout without the spur (S6-L2) is SAR 4,231 m of robust NPV (11,023 against 6,792)" | ok |
| docs/r6-topology.md:80 | difference wording plus the 4,309 standalone score | ok |
| docs/glossary.ar.md:39 | term 27, the AR difference form | ok |
| **docs/r6-topology.md:45** | "its value hangs on the Al-Kharj spur (SAR 4.2 bn of the 11.0 bn)" | **additive share, unfixed** |
| SVG coordinate hits (`fig01`, `fig07`, `fig12`, `fig13`, `fig02 … translate(4231.7…)`) | path data | n/a |

## 9c re-grep (verifier)

Qualified: EN summary :33; AR summary :43 (`من الباب إلى الباب من المدن الخمس الكبرى`); brief :59 ("On the five-metro reach measure … within 120 minutes door to door"), :63 (×2), :65, :117; report 01:20, 01:21; 03:97 (national reach "reported column only"); 04:93, :100, :169, :171, :183, :187 ("reported only (a column outside the score, A-r6-104)"); 07:27; `figures-index.csv` fig08; `r6-topology.md` :17, :35, :38–39, :144, :152. Not the reach measure: 02:20, 04:205, 04:209 (`40–120 road-km`, 30-minute lens). Observation only: `r6-topology.md:99` column head "Reach gain 120 min".

## Failures (exact evidence)

1. **Item 9b, `docs/r6-topology.md:45`:** "L1: the highest robust NPV found by every engine, but its value hangs on the Al-Kharj spur (SAR 4.2 bn of the 11.0 bn) and it goes negative at P90 cost." The prompt's rule: the Al-Kharj figure "is always described as a difference between layouts (S6-L1 vs S6-L1 without the spur), never as an additive share". "4.2 bn of the 11.0 bn" is the 4,231 rounded to billions and framed as a part of the total. The builder's own test (`tests/test_fix_r8.py::test_al_kharj_4231_is_a_layout_difference`, regex `4,?231`) cannot see this spelling, and the file was edited for this item (v1.4) one paragraph further down (line 80), so the two sentences in the same document now contradict each other.

## Observations (not FAILs)

- `docs/r6-topology.md:99` ("Reach gain 120 min" column head) lacks the five-metro door-to-door qualifier that every deliverable now carries; the same file's §0.1 table (line 35) defines it. Worth aligning when line 45 is fixed.
- `docs/plan.md:93–104` run table still names Opus / Haiku / Fable; outside the item (line 110 only) and recorded as the CP3 7a exemption (`docs/STATUS.md:114,120`).
- `docs/cost-log.md` has no FIX_R8 row yet; the status block says the coordinator adds the measured row after the run (procedure step 12 is therefore pending on the coordinator, not the builder).
- The status block says the committed HTML is 17.6 KB, page1 411 KB, table 90 KB, 23/35 before, 0/29 after, 258 = 258, 724 tests, 46 blockers: all measured identically here.
- `docs/licences-blockers.md` "Fonts and media (0)" is correct: the Noto TTFs in `common/fonts/` are OFL-1.1 rows (`docs/licences.csv:270–271`) and grade OBLIGATIONS, not BLOCKER.

## Spot-check

Not applicable to this fix pass: no candidate, cost or benchmark register row was added or changed (the only register edits are two `used_in` cells of `docs/licences.csv`, verified above against tag r8). The one new quantitative claim (4,231 = 11,022.94 − 6,791.61; 4,309.15 standalone) was recomputed from `runs/r6/top5/top5.csv`, `runs/r6/top5/L1/score.json`, `L2/score.json` and `runs/r7/corridors/S3-branch_spur-al-kharj@2050/score.json`.

## Three most important fixes

1. Rewrite `docs/r6-topology.md:45` as a layout difference (for example "L1's robust NPV exceeds L2's by SAR 4,231 m, the difference between the two layouts, and the spur scored alone over S1 gives 4,309, so this is not a share") and bump the header to v1.5.
2. Extend `test_al_kharj_4231_is_a_layout_difference` (or its sentence regex) to the `4.2 bn` / `4.23 bn` spellings and to "of the 11" phrasing so the rule is enforced in every unit.
3. Add the five-metro door-to-door qualifier to the `r6-topology.md:99` column head (or a note under the table) so the internal note reads like the deliverables.

VERDICT: FAIL

---

# Pass 2 (VERIFY_FIX_R8, 5 Nov 2026, HEAD `bab5eda`, `git describe` = `r8-11-gbab5eda`, working tree clean)

Scope: re-verification of the one pass-1 FAIL (item 9b, `docs/r6-topology.md:45`) and a regression sweep of everything else since pass 1 (`576d883`). Read-only; nothing fixed. Pass 1 above is unchanged.

## Pass 2 commands

| command | result |
|---|---|
| `make test` (README command; log `logs/verify-fixr8-p2-maketest.log`) | `EXIT=0`, 36.2 s wall: ruff, format, pytest green, `docver OK: 340 files` (339 in pass 1 + this report, committed in bab5eda), `manifest OK: 386 rows` |
| `uv run pytest -o addopts="" -q` | **724 passed**, 10 warnings, 35.3 s (as expected) |
| `uv run pytest -o addopts="" -q tests/test_fix_r8.py tests/test_glossary_ar.py tests/test_ar_render.py` | 59 passed |
| `uv run python -m common.sources bilingual-check docs/executive-summary.en.md docs/executive-summary.ar.md` | PASS: 258 = 258 |
| `uv run python -m common.report check` | PASS |
| `uv run python -m common.docver check` | OK: 340 files |
| `uv run python -m common.manifest verify` | OK: 386 rows |
| `uv run python -m common.licences check` | 290 = 290, 0 differ |
| `git status --porcelain` | clean |
| `git tag --contains refs/tags/r8` | `r8` only |
| `git diff 576d883 bab5eda --stat` | 4 files: `docs/r6-topology.md` (+3/−3), `tests/test_fix_r8.py` (+4/−2), `docs/status/main.md` (+2/−1), `docs/status/verify-FIX_R8.md` (+99, this report) |
| `git diff 576d883 bab5eda --stat -- prompts film web api common cities docs/licences.csv docs/licences.md` | empty |
| `git diff refs/tags/r8 --stat -- prompts/R9.md prompts/R10.md prompts/VERIFY_R9.md prompts/VERIFY_R10.md prompts/INTEGRATE_R9.md film/` | empty |
| `docs/licences.csv` vs `refs/tags/r8`, row by row (290 rows each, none added or removed) | licence / open / commercial_use / status / approval: **0 differences**; only the two `used_in` cells (markdown-it-py, Google Chrome) differ, as in pass 1 |
| `git diff refs/tags/r8 -- . \| grep -E '^\+.*(/Users/\|git push\|api_key\|secret\|token=)'` | hits only inside this report's own pass-1 command table (quoting the grep) and the `tests/test_ar_render.py` assertion that `"/Users/"` is absent; no path, no push, no secret |

## Pass 2 checks

| # | check | PASS/FAIL | evidence |
|---|---|---|---|
| P2-1 | The pass-1 FAIL is closed: no spelling of the spur figure is framed as a share anywhere under `docs/` outside status logs | PASS | `grep -rn` over `docs/**/*.{md,csv,yaml,html}` (status logs and SVG path data excluded) for `4,231`, `4231`, `4.2 bn`, `4.23`, `4.2 billion`, "of the 11", "of its 11", "from the spur", "of which", `منه إلى الفرع`, `يعود`; every spur-related hit read in full: `docs/r6-topology.md:45` now "(the difference between S6-L1 and the same layout without the spur, L2, is SAR 4,231 m of robust NPV)"; `r6-topology.md:80`, `executive-summary.en.md:32`, `executive-summary.ar.md:42`, `report/figures/executive-summary.ar.html:88`, `policy-brief.md:61`, `report/sections/01-executive-summary.md:19` = `feasibility-report.md:124`, `report/sections/04-results.md:99` = `feasibility-report.md:379` all use the difference form; `glossary.ar.md:39` lists `يعود … منه إلى الفرع` only as the rejected form. `4\.2\d? ?(bn\|billion)` over all `docs/**/*.md`: **no hit**. Every other "of which"/`4.23`/`يعود`/`من أصل` hit is unrelated (source tables, A-cost-403 "14.2333", `network.md` track km, AR summary :61 "من أصل 16 بنداً" = the 16 legal items). `web/src`, `api`, `common`: no hit |
| P2-2 | The widened test would have caught the old line and passes now | PASS | `/tmp/verify-fixr8-p2/regex_probe.py` (same `_sentences` split, run with `python -I`) over `git show bab5eda^:docs/r6-topology.md`: **old regex 0 bad, new regex 1 bad** (the "Why each one is on the list" sentence); over HEAD: 0 bad under both. Synthetic probes: "SAR 4.2 bn of the 11.0 bn", "SAR 4.2 billion of its 11.0 bn", "about 4.23 bn of which", "SAR 4.2bn from the spur", "4,231 of its 11,023 is the spur" all FLAGGED; the HEAD difference sentence ok. `tests/test_fix_r8.py::test_al_kharj_4231_is_a_layout_difference` passes in the 724 |
| P2-3 | README command, pytest count, bilingual, report check, docver | PASS | commands table: `make test` exit 0; 724 passed; 258 = 258; report check PASS; docver OK 340 |
| P2-4 | Nothing else regressed since pass 1; R9/R10 prompts and `film/` untouched; no licence status changed vs tag r8; no tag, push, path or secret | PASS | the 576d883..bab5eda diff touches only `r6-topology.md`, `tests/test_fix_r8.py`, the FIX_R8 status block and this report (stat above); the R9/R10/film diff against `r8` is empty; licence status columns 0 differences; `git tag --contains r8` = `r8`; tree clean |
| P2-5 | Pass-1 observation on `docs/r6-topology.md:99` | PASS (closed) | line 99 now reads `Reach gain, 120 min door to door from the five metros`; the status block (`docs/status/main.md:588`) records it |
| P2-6 | Status block matches what was measured | PASS with two observations | `docs/status/main.md:586` row for :45 matches the diff; 724 tests, 258 = 258, 290 rows match. Observations: (a) the block says "docver 339 files": 340 now because this verifier report was committed after the block was written; (b) `docs/status/main.md` kept v1.15 across the bab5eda edit (CLAUDE.md asks a minor bump per substantive edit; docver check passes because it checks the header format). Both are expected to be settled by the builder's closing commit, which still has to add `FIX_R8: done` |

## Pass 2 observations (not FAILs, carried or new)

- `docs/cost-log.md` still has no FIX_R8 row (coordinator adds the measured row after the run, as the status block says).
- `docs/status/main.md` header v1.15 unchanged in bab5eda; the block's "docver 339 files" is now 340 (see P2-6).
- `docs/plan.md:93–104` run table still names Opus / Haiku / Fable (outside item 7; CP3 7a exemption, `docs/STATUS.md:114,120`), unchanged since pass 1.

## Pass 2 verdict

The single pass-1 failure (item 9b, `docs/r6-topology.md:45`) is closed with the layout-difference wording (r6-topology v1.5), the test now catches the `4.2 bn` / `4.2 billion` / "of the 11" / "of its 11" spellings (proved against the pre-fix file), the `:99` observation is closed, and nothing else moved since pass 1. All pass-1 PASS criteria still hold at `bab5eda`.

VERDICT: PASS
