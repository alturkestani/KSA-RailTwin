> **Document version:** docs/status/verify-SOCIAL_CARDS.md v1.1 | 13 Nov 2026 | Author: red-team-verifier (`claude-fable-5-1`; v1.1 pass 2 after FIX_SOCIAL_CARDS) | Status: reviewed

# VERIFY_SOCIAL_CARDS

Audit of SOCIAL_CARDS (`prompts/SOCIAL_CARDS.md` v1.0, Tariq's brief + coordinator addendum). Repo `~/Documents/Projects/KSA-RailTwin`, main checkout, HEAD 4eef294 (run start cf504dc; builder commits c8a0bbe, 4eef294). Read-only: nothing was fixed, nothing rendered into the delivered folder, nothing pushed, nobody contacted.

## Commands run

| command | result |
|---|---|
| `make test` (= ruff check, ruff format --check, pytest -q, docver, manifest) | rc 0, 72 s wall; "All checks passed!", "833 files already formatted", pytest dots only (project config prints no tally), "docver OK: 425 files", "manifest OK: 388 rows". Log: `logs/verify-social-cards/make-test.log` |
| `uv run pytest -q tests/test_social_cards.py` | 15 passed (15 dots, 100 %), including `test_every_figure_traces` (local runs present) and `test_pngs_1080x1350` (volume present) |
| `uv run python -m film.cards check` | "film.cards check: ok"; word counts 19/16/23/24/25/25/23/25/20/17 |
| `git status --porcelain` | clean |
| `git remote -v` | empty |
| absolute home-path grep over `git ls-files` (the procedure's pattern; verify-* reports excluded) | empty |
| `git ls-files -z \| xargs -0 grep -l "git push"` restricted to scripts | empty |
| secrets grep (sk-…, AKIA…, api_key=…) over tracked files | empty |
| `git ls-files data runs movies film/renders film/audio` | only the pre-existing licensed GASTAT tables and READMEs under `data/`; nothing from this milestone |
| determinism: re-render card2-ar, card3-en, card4-ar to a temp folder (`cards.OUT`/`WORK` patched) and SHA-256 against the delivered PNGs | all three byte-identical (6 s) |

## Independent recomputation of every card figure

Recomputed with pandas/numpy from the cited files, not from `film.cards`.

| card | item | recomputed exact value | card value | cited file:line checked |
|---|---|---|---|---|
| 2 | committed lines (S1) cost | `np.percentile(draws.capex,[10,50,90])` = 48,039.2 / 101,508.0 / 468,494.6 SAR m over 10,000 draws | 102 · 48–468 | `runs/cba/CBA-S1-committed-programme/draws.parquet` col `capex`; `common/figures.py:1859-1862` is the same formula; `docs/policy-brief.md:39` = 101,508; `docs/report/sections/04-results.md:55-58` Figure 15 |
| 2 | connected network (S6-L6) cost | 122,532.0 / 227,213.0 / 860,035.3 | 227 · 123–860 | `runs/r6/l6/score/S6-L6.csv:2` (`capex_p10/p50/p90`); `docs/r6-l6-connected.md:70,95` |
| 2 | three stations (S6-L2) cost | 800.6 / 1,423.1 / 5,286.1 | 1.4 · 0.8–5.3 | `runs/r6/top5/top5.csv:3` (row S6-L2); `04-results.md:90` = 801 / 1,423 / 5,286 |
| 3 | three stations ratio | 5.961829 | 6 | `top5.csv:3` `bcr_p50_medium`; `film/storyboard/rounding-log.csv:3` (5.9618 → 6) |
| 3 | plus Al-Kharj spur (S6-L1) | 2.329272 | 2.3 | `top5.csv:2`; `rounding-log.csv:4` |
| 3 | committed lines | 0.3057226 | 0.3 | `results.json:3416` (`bcr.P50`, un_wpp_medium, 60 y, central rate; confirmed by `sim_main.cba_central()` selection); `rounding-log.csv:2` |
| 3 | Riyadh–Jeddah (five sketches) | 0.182, 0.221, 0.227, 0.228, 0.244 → all 0.2 | 0.2 | `runs/study/rj/score/score.csv:2-6`; `rounding-log.csv:6` |
| 3 | connected network | 0.060972 | 0.06 | `S6-L6.csv:2` `bcr_p50_medium`; `rounding-log.csv:10` (two decimals by the film's decision) |
| 4 | flight door to door | 191.0 min (60 + 101 + 30) | 3 h 11 min | `runs/study/rj/times-s1/air.json:6` `door_to_door_model_min`; `docs/rj-routes-study.md:204` "3:11" |
| 4 | fastest modelled train | min `d2d_p50_min` over 34 rows = 297.3 (RJ-A, hsr, 350, all-stop riyadh\|jeddah = non-stop) | 4 h 57 min | `times.csv:9`; `rj-routes-study.md:207` "4:57" |
| 4 | 350 km/h | `speed_class` of that row = 350 | 350 | `times.csv:9`; `film/script/lines.csv` m-04-03 |
| 5 | Claude runs | 93 rows with label ≠ PAID of 128 data rows (`cost-log.csv` lines 2–129 at cf504dc) | 93 | `git show cf504dc:docs/cost-log.csv`; definition `docs/spend-summary.md:10` |
| 5 | list price | sum `usd_list` of those rows = 1,324.87 | USD 1,325 | same |
| 5 | voices | 35 PAID rows, sum 7.09 | USD 7 | same; `spend-summary.md:29` says 7.06 / 33 calls (predates the last two TTS rows): difference listed in `social-cards.md` |
| 1 | map | 16 corridors of `runs/r6/l6/L6.layout.yaml`, drawn through `sim_main.corridor_geom` (routed alignments only); the `far5` cities | no figure | `film/cards.py:271-283`, `:448-472` |

All 19 rows of the trace table in `docs/publish/social-cards.md` were checked (100 %, no sampling; no external web sources are cited by this milestone, so no WebFetch spot-check applies). Every prompt-vs-file difference (100→102, 50→48, 120→123, 230→227, 94→93, 7.06→7.09) is listed in the "Where the files differ" table. Rounding rules stated in `social-cards.md` (ratios one decimal, 0.06 two decimals per `rounding-log.csv:10`; costs whole billions ≥ 10 bn, one decimal below; times to the minute) are applied consistently on all ten cards.

## Criteria

| # | criterion | result | evidence |
|---|---|---|---|
| 1 | every number traces; recomputed independently; rounding consistent with `rounding-log.csv`; prompt differences listed; PNG numbers = CSV | PASS | table above; all ten PNGs viewed: card 2 shows 102/48–468, 227/123–860, 1.4/0.8–5.3; card 3 shows 6, 2.3, 0.3, 0.2, 0.06; card 4 shows 3 h 11 min / 4 h 57 min and 350 km/h; card 5 shows 93, USD 1,325, USD 7, cf504dc, in both languages |
| 2 | no jargon on any card (incl. images) | PASS | independent regex over the CSV (NPV, BCR, P10/50/90, capex, present value, benefit-cost, صافي, القيمة الحالية, مئين, رأسمالي): no hits; images read: none visible; column headers are "middle / likely range" (الوسط / النطاق المرجّح) |
| 3 | body ≤ 25 words; footer; OSM attribution on all ten | PASS | independent count (tokens containing a letter) 19/16/23/24/25/25/23/25/20/17; footer "Independent simulation, not a government plan · github.com/alturkestani/KSA-RailTwin" / «محاكاة مستقلة، مو خطة حكومية · github.com/…» and "© OpenStreetMap contributors (ODbL) · Relief: … Copernicus WorldDEM-30 …" seen on all ten images (`film/cards.py:53-57`, `:387-393`) |
| 4 | ten PNGs, exactly 1080×1350, both languages | PASS | PIL: all ten `(1080, 1350)` RGB in `film/renders/out/social/cards/` (symlink to the external volume) |
| 5 | Arabic shaped, correct RTL order, ranges low–high, plain Saudi wording, `native_review = pending` recorded | PASS | zoomed crops of card 2 AR panel (48–468, 123–860, 0.8–5.3 read low–high; letters connected), card 4 AR panel (3 ساعات و11 دقيقة / 4 ساعات و57 دقيقة), card 1 AR legend, AR footer; wording «مو», «انسوّت», «الطيارة», «كيلو بالساعة», «ما يرجّع» = Saudi colloquial; `social-cards.md` "native_review = pending" paragraph present and the film's `lines.csv` `native_review` = pending on all 79 Arabic lines |
| 6 | card 1: modelled alignments only; legend = film classes; OSM + Copernicus credits | PASS | `film/cards.py:275` filters through `sim_main.corridor_geom` (routed GeoJSON; 2-point sketches never drawn); image shows curved routed lines through the Sarawat (Taif–Bisha–Abha–Jazan) and Tabuk–Sakaka; legend "existing / committed or under procurement / hypothetical (ours)" = `film/render.py:71-81` word for word (the prompt said "proposed"; the deviation is recorded in `social-cards.md` "Legend" and status decision 1; rule 5 favours the film's wording); credits present |
| 7 | synthetic-demand label on modelled cards; no advocacy; no company content; no model names; no absolute home paths | PASS | label on cards 1–4 (both languages, `R.FOOTER` wording); card 5 is a project fact and correctly carries none; titles say "in the model", card 1 note "A comparison, not a recommendation"; no "will …" phrasing; no company content; "Claude" appears on card 5 as Tariq's brief requires, no model ids (fable/opus/haiku) anywhere; home-path grep empty |
| 8 | `make test` green, nothing pushed, no remote | PASS | rc 0 (log above); `git remote -v` empty; `git status` clean |
| 9 | status block ends with a plain start-of-line `SOCIAL_CARDS: done` (Tariq: "Status ends 'SOCIAL_CARDS: done' or 'blocked - <reason>'"; addendum: "ending with a plain start-of-line `SOCIAL_CARDS: done` or `SOCIAL_CARDS: blocked - <reason>`") | **FAIL** | `grep -n "SOCIAL_CARDS: done\|SOCIAL_CARDS: blocked" docs/status/main.md docs/STATUS.md` → no match (rc 1). The block (`docs/status/main.md:1930-1963`) opens with "**Done.**" and ends with "- Cost row: added by the orchestrator from the run JSON." Every earlier block has the line (`main.md:1878` `PUBLISH_EXPORT: done`, `:1928` `FIX_EXPORT_NAMES: done`). The orchestrator greps for it (CLAUDE.md, Workflow) |

## Failures (exact evidence)

1. **Missing terminator line.** `docs/status/main.md` has no line matching `^SOCIAL_CARDS: (done|blocked)`. The brief and the addendum both make this the completion signal; the block as written would not be found by the orchestrator's grep. Severity: documentation only; no card content is affected.

## Observations (not FAILs)

- `docs/cost-log.csv` at HEAD 4eef294 has no SOCIAL_CARDS row (129 lines, last row FIX_EXPORT_NAMES). The block says the orchestrator appends it from the run JSON, which matches the precedent (5092df2 added the FIX_EXPORT_NAMES row after its verify). The row must exist before the milestone is closed.
- Card 5 names "Claude" (a product name, requested in the brief); the model-id mapping is not shown. Consistent with CLAUDE.md, which restricts model ids, not the orchestrator's name.
- The legend keeps the film's "hypothetical (ours)" where the prompt said "proposed"; recorded and justified (rule 5). Tariq may still prefer "proposed" on a social card; that is a wording choice, not a trace error.
- `docs/spend-summary.md:29` (7.06 / 33 calls) is stale against the cost log (7.09 / 35). The card uses the log and lists the difference; the summary itself is out of this milestone's scope.
- The external volume holds AppleDouble `._card*.png` sidecars beside the PNGs (ExFAT artefacts, 4 KB each, not tracked). Harmless; delete before sharing the folder.
- `social-cards.md` is `Status: draft`; it can move to `reviewed` once the terminator fix lands.

## Three most important fixes

1. Append the plain line `SOCIAL_CARDS: done` at the end of the `## SOCIAL_CARDS` block in `docs/status/main.md` (one-line docs commit; bump nothing else).
2. Orchestrator: append the SOCIAL_CARDS cost row to `docs/cost-log.md`/`.csv` before tagging the milestone done.
3. Optional, Tariq's call: decide whether the card 1 legend should read "proposed" (prompt wording) or "hypothetical (ours)" (film wording, currently on the cards); if changed, update `film/render.py` LEGEND users consistently or add a card-only override and re-render (re-render is deterministic, 6 s for three cards).

Spot-check sample: all 19 trace rows (100 %); no random seed needed.

VERDICT: FAIL
VERIFY_SOCIAL_CARDS: FAIL

## Pass 2 (FIX_SOCIAL_CARDS, 13 Nov 2026, HEAD f6358ed)

Full pass over the ten re-rendered cards after `prompts/FIX_SOCIAL_CARDS.md` (Tariq, 13 Nov 2026). Repo `~/Documents/Projects/KSA-RailTwin`, main checkout, HEAD f6358ed (builder commit f6358ed on 5c4c3f0; run start 8ccc6e9). Read-only: nothing fixed, nothing rendered into the delivered folder (the determinism re-render went to a temp folder), nothing pushed, nobody contacted, no paid calls, no process stopped.

### Commands run

| command | result |
|---|---|
| `make test` at f6358ed (ruff check, ruff format --check, pytest -q, docver, manifest) | rc 0, 72 s wall; "All checks passed!", "835 files already formatted", pytest dots only, "docver OK: 427 files", "manifest OK: 388 rows". Log: `logs/verify-social-cards/make-test-pass2.log` |
| `uv run pytest -q tests/test_social_cards.py` | 15 passed (15 dots, 100 %) |
| `git status --porcelain` before this report | clean; `git remote -v` empty |
| `git diff 8ccc6e9..f6358ed --stat` | five files: `docs/publish/social-cards.csv` (4 rows), `docs/publish/social-cards.md`, `docs/status/main.md` (header + appended block only; one hunk at 1982, one at 1), `film/cards.py` (+11 −1), `prompts/FIX_SOCIAL_CARDS.md` (new) |
| exact-string greps on the CSV | `^1,en,One connected network,` 1; `^1,ar,شبكة واحدة مترابطة,` 1; `للمقارنة، وليست توصية$` 1; `Flight = 3 h 11 min \| Fastest train = 4 h 57 min` 1; `الطيارة = 3 ساعات و11 دقيقة \| أسرع قطار = 4 ساعات و57 دقيقة` 1; residual `in the model`, `في النموذج`, `وحدة`: none (rc 1) |
| cost log: `git show cf504dc:docs/cost-log.csv` (129 lines) vs `head -129 docs/cost-log.csv` | byte-identical; the last row at cf504dc is `main-FIX_EXPORT_NAMES-try1` (line 129), which appears once in the live log; the live log has one extra row (`main-SOCIAL_CARDS-try1`, 8.26) |
| SHA-256 of the ten delivered PNGs (`film/renders/out/social/cards/`, volume) | all ten equal the table in the FIX_SOCIAL_CARDS status block (card1 en 279148bc…, ar 266c677b…, card4 en b6a37698…, ar 748eb346…, card2 ar b58166eb… etc.); PIL: all ten `(1080, 1350)` RGB; no `._` sidecars in the folder |
| determinism: all ten cards re-rendered with `cards.OUT`/`cards.WORK` patched to a temp folder, SHA-256 against the delivered files | all ten IDENTICAL (11 s); the delivered folder was not written |
| hygiene greps over `git ls-files` (home paths excluding verify reports; secrets; `git push` in scripts; model ids / company terms in the CSV, trace and `film/cards.py`; "will reduce/transform", "should build") | all empty (grep rc 1); `git ls-files data runs movies film/renders film/audio` shows only the pre-existing licensed GASTAT/pilgrim tables and READMEs |

### Independent recomputation (pandas/numpy from the cited files, not `film.cards`)

| card | item | recomputed | card | source |
|---|---|---|---|---|
| 2 | committed lines cost | 48,039.2 / 101,508.0 / 468,494.6 (10,000 draws, `capex` P10/50/90) | 102 · 48–468 | `runs/cba/CBA-S1-committed-programme/draws.parquet` |
| 2 | connected network cost | 122,532.0 / 227,213.0 / 860,035.3 | 227 · 123–860 | `runs/r6/l6/score/S6-L6.csv:2` |
| 2 | three stations cost | 800.6 / 1,423.1 / 5,286.1 | 1.4 · 0.8–5.3 | `runs/r6/top5/top5.csv` row S6-L2 |
| 3 | three stations / Al-Kharj spur / committed / Riyadh–Jeddah / connected | 5.961829 / 2.329272 / 0.3057226 / 0.182–0.244 (five sketches) / 0.060972 | 6 / 2.3 / 0.3 / 0.2 / 0.06 | `top5.csv`; `results.json:3416` (`bcr.P50`); `runs/study/rj/score/score.csv:2-6`; `S6-L6.csv:2`; rounding per `film/storyboard/rounding-log.csv` (m-08-01/02/03/08/19) |
| 4 | flight door to door | 191.0 min (60 + 101 + 30) | 3 h 11 min | `runs/study/rj/times-s1/air.json` `door_to_door_model_min`; `docs/rj-routes-study.md:204` |
| 4 | fastest train | min `d2d_p50_min` over 34 rows = 297.3 (RJ-A, hsr, 350, non-stop) | 4 h 57 min, 350 km/h | `times.csv:9`; `rj-routes-study.md:207` |
| 5 | Claude runs / list price / voices, rows up to `main-FIX_EXPORT_NAMES-try1` | 93 / 1,324.87 / 7.09 (35 PAID rows) | 93 / USD 1,325 / USD 7 | `docs/cost-log.csv` lines 2–129 = the log at cf504dc; with the live log (one more row) the totals would be 94 / 1,333.13 / 7.09, which the card does not show and must not |

All 19 trace rows of `docs/publish/social-cards.md` v1.1 checked (100 %); no external web source is cited, so no WebFetch spot-check applies. Independent word count (tokens containing a letter; `|` and `=` stripped): 16 / 14 / 23 / 24 / 25 / 25 / 20 / 23 / 20 / 17 = the builder's figures. Independent jargon regex (NPV, BCR, P10/50/80/90, capex, present value, benefit-cost, discount, صافي, القيمة الحالية, مئين, رأسمالي, خصم): no hits.

### Judgement on the `film/cards.py` change

`cost_totals()` now truncates the cost log at `AS_OF_LAST_RUN = "main-FIX_EXPORT_NAMES-try1"`. Verified: that id is the last row of `docs/cost-log.csv` at cf504dc, the 129 lines up to it are byte-identical to the file at cf504dc, and the id occurs once in the live log (the `assert` guards its absence). The change is the minimum needed to render at all: without it the render command refuses (card 5 would need 94 / USD 1,333) and `test_every_figure_traces` fails on main since 8ccc6e9. It makes the code match what card 5 says ("As of commit cf504dc") and is append-only-safe. Card numbers unchanged (93 / 1,325 / 7). In scope: a necessary enabling fix, not a wording, number, layout or source change to any card; ruff and tests pass. The matching trace-row edit in `social-cards.md` (card 5 cut-off) and the FIX section are the only non-wording edits to the trace doc; the other three edits are the Arabic-register line, the card 4 item name and the header. Nothing else in the trace changed.

### Criteria

| # | criterion | result | evidence |
|---|---|---|---|
| 1 | every number traces; recomputed independently; rounding per `rounding-log.csv`; PNG numbers = CSV | PASS | table above; all ten PNGs viewed: card 2 102/48–468, 227/123–860, 1.4/0.8–5.3; card 3 6, 2.3, 0.3, 0.2, 0.06; card 4 3 h 11 min / 4 h 57 min, 350 km/h; card 5 93, USD 1,325, USD 7, cf504dc; both languages |
| 2 | no jargon on any card (incl. images) | PASS | independent regex: no hits; nothing visible on the images; headers "middle / likely range" (الوسط / النطاق المرجّح) |
| 3 | body ≤ 25 words; footer; OSM credit on all ten | PASS | counts 16/14/23/24/25/25/20/23/20/17; footer "Independent simulation, not a government plan · github.com/alturkestani/KSA-RailTwin" / «محاكاة مستقلة، مو خطة حكومية · …» and "© OpenStreetMap contributors (ODbL) · Relief: … Copernicus WorldDEM-30 …" seen on all ten images |
| 4 | ten PNGs, exactly 1080×1350, both languages | PASS | PIL on the delivered folder: ten files, all (1080, 1350) RGB |
| 5 | Arabic shaped, RTL order correct, ranges low–high, plain Saudi wording, `native_review = pending` recorded | PASS | zoomed crops: card 1 AR title «شبكة واحدة مترابطة» (واحدة with the alif, letters connected), subtitle intact; card 4 AR «الطيارة 3 ساعات و11 دقيقة», «أسرع قطار 4 ساعات و57 دقيقة»; card 2 AR 48–468, 123–860, 0.8–5.3 read low–high; card 1 AR note «للمقارنة، وليست توصية»; legend «قائم / ملتزم به أو قيد الطرح / افتراضي (من الدراسة)»; `social-cards.md` "native_review = pending" paragraph present |
| 6 | card 1: routed alignments only; legend = film classes; OSM + Copernicus credits | PASS | `film/cards.py` unchanged in this respect (filters through `sim_main.corridor_geom`); image shows curved routed lines (Taif–Bisha–Abha–Jazan, Tabuk–Sakaka), no straight 2-point sketches; legend "existing / committed or under procurement / hypothetical (ours)" = `film/render.py:71-81`; credits present |
| 7 | synthetic label on modelled cards; no advocacy; no company content; no model ids; no absolute home paths | PASS | the label line "synthetic demand, uncalibrated: scenario comparison, not a forecast" / «طلب تركيبي غير مُعايَر: مقارنة سيناريوهات، ليست توقعاً» is on cards 1–4 in both languages (`foot_html(lang, True)` at `cards.py:481,503,541,580`; card 5 `False` at `:597`) and unchanged; "in the model" dropped from the card 1 and card 4 titles by Tariq's decision (prompt items 1 and 3), card 1 note "A comparison, not a recommendation" kept; no "will …" phrasing; no company terms; "Claude" on card 5 as the brief requires, no model ids; home-path grep empty |
| 8 | `make test` green, nothing pushed, no remote | PASS | rc 0 (log above); `git remote -v` empty; `git status` clean before this report |
| 9 | `docs/status/main.md` has plain start-of-line `SOCIAL_CARDS: done` at the end of the SOCIAL_CARDS block and `FIX_SOCIAL_CARDS: done` at the end of the FIX_SOCIAL_CARDS block | PASS | `grep -n "^SOCIAL_CARDS: done\|^FIX_SOCIAL_CARDS: done" docs/status/main.md` → `1984:SOCIAL_CARDS: done` (last line of the block, line 1985 blank, FIX block header at 1986) and `2032:FIX_SOCIAL_CARDS: done` (last line of the file, 2032 lines, newline-terminated) |

Additional checks requested for this pass: the CSV diff (`git diff 8ccc6e9..f6358ed -- docs/publish/social-cards.csv`) touches exactly rows 1 en, 1 ar, 4 en, 4 ar and only the five strings Tariq listed (also card 1 en title loses its quoting because the comma went); rows 2, 3 and 5 are unchanged. Before strings in the status block match the pre-edit CSV (verified on the diff's `-` lines). The status block's "changed / identical" column matches the earlier hashes quoted by the coordinator (card1 en was 7de1b0f9…, ar 58687e04…, card4 en e9ffbf2c…, ar e208404a…; card2 ar still b58166eb…).

### Observations (not FAILs)

- `docs/cost-log.csv` at f6358ed has no FIX_SOCIAL_CARDS row (last row SOCIAL_CARDS, 8.26). As with pass 1, the orchestrator appends it from the run JSON after this verify; the pin in `cards.py` means that row will not disturb card 5.
- `docs/STATUS.md` does not mention SOCIAL_CARDS or FIX_SOCIAL_CARDS; the track's status lives in `docs/status/main.md`, which is what the criterion names. The orchestrator may want a line in `docs/STATUS.md` when the cards are published.
- `docs/spend-summary.md:29` (7.06 / 33 calls) remains stale against the log (7.09 / 35); recorded in the trace; outside this milestone.
- `social-cards.md` is still `Status: draft`; it can move to `reviewed` with the next docs commit.
- The legend keeps "hypothetical (ours)" (film wording) rather than the prompt's "proposed"; Tariq's choice, unchanged by FIX_SOCIAL_CARDS, which did not ask for it.

### Three most important follow-ups

1. Orchestrator: append the FIX_SOCIAL_CARDS cost row to `docs/cost-log.md`/`.csv` (card 5 is unaffected by it).
2. Optional: set `docs/publish/social-cards.md` to `Status: reviewed` and bump its header in the next docs commit.
3. Optional, Tariq's call: legend wording "hypothetical (ours)" vs "proposed" (see pass 1 fix 3); if changed, re-render (deterministic, 11 s for all ten).

Spot-check sample: all 19 trace rows (100 %); no random seed needed.

VERDICT: PASS
VERIFY_SOCIAL_CARDS: PASS
