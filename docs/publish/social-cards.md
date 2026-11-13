> **Document version:** docs/publish/social-cards.md v1.3 | 13 Nov 2026 | Author: main builder (SOCIAL_CARDS; v1.1 FIX_SOCIAL_CARDS wording; v1.2 PUBLISH_PDF_POST cards 6 and 7; v1.3 FIX_PDF_CONNECTED card 8) | Status: draft

# Social cards: sources and rounding

Eight photo cards for social replies, each in English and Arabic: sixteen PNGs (cards 1–5 from SOCIAL_CARDS, cards 6 and 7 from PUBLISH_PDF_POST, card 8 from FIX_PDF_CONNECTED), 1080×1350, in `renders/out/social/cards/` on the external volume (`film/renders` symlink). They are not committed (rule 8).

- Command: `uv run python -m film.cards render` (all ten), `uv run python -m film.cards check` (jargon, word count, figures), `uv run python -m film.cards trace` (exact values).
- Card text: `docs/publish/social-cards.csv`, one row per card and language. The PNGs are drawn from it.
- Renderer: `film/cards.py`, a thin wrapper around the film's moving-map engine (`film/sim.py`, `film/sim_main.py`). It uses the same Copernicus night relief, line colours, dashes, glow, fonts (Noto Sans, Noto Naskh Arabic) and headless-Chrome text layer as the film's `sim_map` frames. It draws one still at 1080×1350. No new package, no model download, no paid call.
- Labels: cards 1–4 carry the project label "synthetic demand, uncalibrated: scenario comparison, not a forecast" (Arabic: the film's wording). Card 5 is a project fact, not a modelled output, so it has no label. Every card has the footer "Independent simulation, not a government plan · github.com/alturkestani/KSA-RailTwin" (Arabic: «محاكاة مستقلة، مو خطة حكومية» + the same URL). Every card also has the credit "© OpenStreetMap contributors (ODbL) · Relief: Copernicus WorldDEM-30 …", because every card's background is the relief map with the OSM-derived lines.
- Rule 3 on ranges: card 2 shows each cost as a middle value with its likely range. Card 3 shows only the middle value: Tariq asked for simple bars. Its title says "middle case", as the film does. The ranges are in the trace table below and in the report.

## Trace table (exact value → card value → file:line)

Rounding follows the film: ratios to one decimal, except 0.06, which has two decimals (`film/storyboard/rounding-log.csv:10`: one decimal would read 0.1). The film rounds the three-station ratio 5.96 to "about 6", so the card shows "6". Costs on the cards are in billion riyals: whole billions from 10 billion up, one decimal below that (the film used one decimal for the station costs, 0.8 to 5.3). Times are rounded to the minute.

"Likely range" on card 2 = the P10–P90 columns of the same files. The card has no percentile labels.

| card | item | exact value (file) | card value | file:line |
|---|---|---|---|---|
| 1 | connected network (S6-L6) | 16 corridors; lines drawn from routed (DEM least-cost) alignments | map only, no figure | `runs/r6/l6/L6.layout.yaml`; alignments via `film/sim_main.py` `corridor_geom` (`runs/align/corridors-*-s1/<id>/alignment.geojson`; 2-point straight sketches never drawn); `docs/r6-l6-connected.md:70` |
| 1 | the five cities | Tabuk, Jazan, Najran, Abha, Khamis Mushait (film's `far5`) | names on map | `film/sim_main.py` (sh-08-15..17 `far5`); `film/script/lines.csv` m-08-16 |
| 2 | committed lines (S1), cost to build | P10 / P50 / P90 = 48,039.2 / 101,508.0 / 468,494.6 SAR m (uplifted, undiscounted; percentiles of `capex` over the 10,000 draws) | 102 · 48–468 | `runs/cba/CBA-S1-committed-programme/draws.parquet` (column `capex`, computed as `common/figures.py:1859-1862` `s1_capex()`; report Figure 15, `docs/report/sections/04-results.md:55-58`); P50 also in `docs/policy-brief.md:39` (101,508) |
| 2 | connected network (S6-L6), cost to build | 122,532.0 / 227,213.0 / 860,035.3 SAR m | 227 · 123–860 | `runs/r6/l6/score/S6-L6.csv:2` (`capex_p10`, `capex_p50`, `capex_p90`); `docs/r6-l6-connected.md:95` |
| 2 | three new stations (S6-L2), cost to build | 800.6 / 1,423.1 / 5,286.1 SAR m | 1.4 · 0.8–5.3 | `runs/r6/top5/top5.csv:3` (`capex_p10/p50/p90`); `docs/report/sections/04-results.md:90` (801 / 1,423 / 5,286) |
| 2 | "Ranges allow for overruns like past rail projects" | reference-class uplift, one of 355 rail projects | words | `film/script/lines.csv` m-06-06 (A-rcf-001, A-rcf-004, A-cost-008); `docs/costs.md` §7 |
| 3 | three stations (S6-L2) | 5.9618 riyals back per riyal (middle case: P50 of the draws, UN WPP medium, 60 years) | 6 | `runs/r6/top5/top5.csv:3` (`bcr_p50_medium`); `film/storyboard/rounding-log.csv:3` |
| 3 | plus the Al-Kharj spur (S6-L1: the three stations + the spur) | 2.3293 | 2.3 | `runs/r6/top5/top5.csv:2`; `film/storyboard/rounding-log.csv:4` |
| 3 | committed lines (S1 vs today) | 0.3057 | 0.3 | `runs/cba/CBA-S1-committed-programme/results.json:3416` (`bcr.P50`, medium, 60 y, central rate); `film/storyboard/rounding-log.csv:2` |
| 3 | Riyadh–Jeddah (side study, five sketches) | 0.182 to 0.244 (all round to 0.2) | 0.2 | `runs/study/rj/score/score.csv:2-6` (`bcr_p50_medium`); `film/storyboard/rounding-log.csv:6`; `docs/rj-routes-study.md` §8a |
| 3 | connected network (S6-L6) | 0.06097 | 0.06 | `runs/r6/l6/score/S6-L6.csv:2` (`bcr_p50_medium`); `film/storyboard/rounding-log.csv:10` |
| 3 | the line at 1, "below 1 = doesn't pay back what it costs" | definition | 1 | `film/script/lines.csv` m-08-01 ("Below one, a line does not repay its cost") |
| 4 | flight, door to door (city centre to city centre) | 191.0 min (access 60 + block 101 + egress 30) | 3 h 11 min | `runs/study/rj/times-s1/air.json:6` (`door_to_door_model_min`); `docs/rj-routes-study.md:204` (3:11) |
| 4 | fastest train (card label "Fastest train"; the fastest modelled rail row: RJ-A, 350 km/h, non-stop), door to door | 297.3 min (P50) | 4 h 57 min | `runs/study/rj/times-s1/times.csv:9` (`d2d_p50_min`); `docs/rj-routes-study.md:207` (4:57) |
| 4 | 350 km/h | the speed class of that case | 350 | `runs/study/rj/times-s1/times.csv:9` (`speed_class`); `film/script/lines.csv` m-04-03 |
| 5 | Claude runs | 93 (rows of `docs/cost-log.csv` whose label is not `PAID`; the definition in `docs/spend-summary.md:10`) | 93 | `docs/cost-log.csv` lines 2–129 at cf504dc (the rows up to `main-FIX_EXPORT_NAMES-try1`; `film/cards.py` `AS_OF_LAST_RUN` stops there, so later rows do not change the card); `uv run python -m common.cost_log summary` TOTAL row at cf504dc |
| 5 | Claude, list price (subscription: reference cost, not a charge) | USD 1,324.87 | USD 1,325 | same rows, `usd_list`; summary TOTAL row |
| 5 | paid voices (TTS) | USD 7.09 over 35 calls | USD 7 | `docs/cost-log.csv` `PAID` rows; summary "PAID TOTAL" row |
| 5 | open code | Apache-2.0 | words | `LICENSE`; `CLAUDE.md` (Engineering rules) |
| 6 | "Open data" | public, licence-compatible data (OSM, GASTAT, open elevation data) | words | `docs/report/feasibility-report.md` §3.1; `docs/licences.md` |
| 6 | "Routes over real terrain" | least-cost routes on 30 m elevation data, tested on three lines in service | words | `film/script/lines.csv:108-109` (m-06-01, m-06-02); `docs/alignments.md:65-68` |
| 6 | "Costs with overrun ranges" | reference-class uplift, one of 355 rail projects (as card 2's note) | words | `film/script/lines.csv:113` (m-06-06); row card 2 above |
| 6 | "Simulated travellers" | synthetic demand, uncalibrated (the project label on the card) | words | `docs/report/feasibility-report.md` §3.3; `film/render.py` `FOOTER` |
| 6 | "Compare options" | every scenario against a matched baseline (rule 6) | words | `docs/report/feasibility-report.md` §0.3, §4 |
| 7 | three new stations (S6-L2) | 5.9618 (same value as card 3) | 6 | `runs/r6/top5/top5.csv:3` (`bcr_p50_medium`); `film/storyboard/rounding-log.csv:3` |
| 7 | committed lines (S1 vs today) | 0.3057 | 0.3 | `runs/cba/CBA-S1-committed-programme/results.json:3416` (`bcr.P50`); `film/storyboard/rounding-log.csv:2` |
| 7 | connected network (S6-L6) | 0.06097 | 0.06 | `runs/r6/l6/score/S6-L6.csv:2` (`bcr_p50_medium`); `film/storyboard/rounding-log.csv:10` |
| 7 | "Riyadh–Jeddah door to door: flight beats every modelled train" | air 191.0 min against the fastest rail row 297.3 min; air ahead in every rail case modelled | words (no figure) | `runs/study/rj/times-s1/air.json:6`; `runs/study/rj/times-s1/times.csv:9`; `film/script/lines.csv:98` (m-04-03); `docs/rj-routes-study.md` §5 |
| 8 | connected network (S6-L6), map | the 16 S6-L6 corridors, lines drawn from routed (DEM least-cost) alignments as on card 1; city labels: film places (`film/sim.py`) and, for Sakaka, Arar, Hafar Al-Batin, Yanbu and Bisha, the station points and `name_ar` of the S6-L6 corridor YAMLs | map, names | `runs/r6/l6/L6.layout.yaml`; `film/cards.py` `l6_geometry`, `l6_stations`; `cities/ksa/corridors/*/S2-trunk_gap-{tabuk-sakaka,al-jubayl-hafar-al-batin,jeddah-yanbu,taif-bisha}.yaml`, `cities/ksa/corridors/branch_spur/S3-branch_spur-arar.yaml` |
| 8 | "16 new links" | 16 corridors (14 lines + 2 station additions) | 16 | `runs/r6/l6/score/S6-L6.csv:2` (`corridors`); `docs/r6-l6-connected.md:95` |
| 8 | "join 18 cities" | 18 required cities, all on the rail graph (A-r6-132) | 18 | `cities/ksa/assumptions/r6_l6.yaml:28-45` (`required`); `docs/r6-l6-connected.md` §3 |
| 8 | new line | 3,241.87 route-km | 3,242 km | `runs/r6/l6/score/S6-L6.csv:2` (`new_route_km`); `docs/r6-l6-connected.md:95` (3,241.9) |
| 8 | cost to build, billion riyals | 122,532.0 / 227,213.0 / 860,035.3 SAR m (same values as card 2) | 227 · likely 123–860 | `runs/r6/l6/score/S6-L6.csv:2` (`capex_p10`, `capex_p50`, `capex_p90`); `docs/r6-l6-connected.md:95` |
| 8 | riyals back per riyal | 0.06097 (middle case, same value as cards 3 and 7) | 0.06 | `runs/r6/l6/score/S6-L6.csv:2` (`bcr_p50_medium`); `film/storyboard/rounding-log.csv:10` |

Card 4 uses the film's own figures in the sense of the film's door-to-door race (trailer shot sh-04-51, `film/sim.py` `air_over_rail()`): that race is scaled to exactly these two modelled times (air 191.0 against rail 297.3 minutes, the fastest rail row). The film's narration gives the result in words ("air stays ahead door to door in every rail case modelled, even non-stop at 350 kilometres an hour", m-04-03). It does not speak the minutes. The minutes are in `docs/rj-routes-study.md` §5.

## Where the files differ from the prompt's figures (the file wins)

| card | prompt | file | card shows |
|---|---|---|---|
| 2 | committed lines about 100 billion (50 to 470) | 101.5 (48.0 to 468.5) | 102 (48–468) |
| 2 | connected network about 230 billion (120 to 860) | 227.2 (122.5 to 860.0) | 227 (123–860) |
| 2 | three new stations about 1.4 billion | 1.42 (0.80 to 5.29) | 1.4 (0.8–5.3) |
| 3 | 6 / 2.3 / 0.3 / 0.2 / 0.06 | 5.96 / 2.33 / 0.31 / 0.18–0.24 / 0.061 | same as the prompt |
| 5 | 94 Claude runs | 93 at cf504dc (this run's own row is not yet in the log) | 93 |
| 5 | about USD 1,325 | 1,324.87 | USD 1,325 |
| 5 | about USD 7 in voices | 7.09 (cost log, 35 calls); `docs/spend-summary.md:29` says 7.06 over 33 calls. The summary was written before the last two `FIX_TRAILER_AR` TTS rows | USD 7 |

Card 5 states "As of commit cf504dc", the run's start HEAD. The cost log there is identical to 5092df2, the base the addendum names, because cf504dc only adds the prompt.

## Wording choices

- **Legend.** Card 1 uses the film's three legend classes word for word (`film/render.py` `LEGEND`): "existing", "committed or under procurement", "hypothetical (ours)". Tariq's prompt said "proposed". The film's word "hypothetical (ours)" is kept, so the layer names stay as rule 5 sets them and nothing reads as an official proposal.
- **Plain words.** No finance jargon: no NPV, BCR, P10/P50/P90, capex or present value, in English or Arabic. `tests/test_social_cards.py` checks this.
- **Word count.** At most 25 words of body per card, counting only whitespace tokens that contain a letter, so figures do not count. Footer, credits, the project label, legend and map labels are excluded.
- **Arabic register.** Plain Saudi Arabic, with the film's wording where the film has it: «كم ريال يرجع لكل ريال», «ما يرجّع تكلفته», «الخطوط الملتزم بها», «الشبكة المترابطة», «الحالة الوسطى», «للمقارنة، وليست توصية», «الطيارة», «كيلو بالساعة». Figures use Western digits, as in the film. Number ranges are LTR isolates, so "48–468" keeps its order inside a right-to-left line (checked on zoomed crops of the rendered PNGs).
- **native_review = pending.** The Arabic of these cards has had no native-speaker review. The film's Arabic is accepted, but its native review is also still pending (`film/script/lines.csv`, `native_review` column = `pending` on every Arabic line).

## Outputs

| file | size |
|---|---|
| card1-network-{en,ar}.png | 1080×1350 |
| card2-cost-{en,ar}.png | 1080×1350 |
| card3-payback-{en,ar}.png | 1080×1350 |
| card4-riyadh-jeddah-{en,ar}.png | 1080×1350 |
| card5-how-made-{en,ar}.png | 1080×1350 |
| card6-method-{en,ar}.png | 1080×1350 |
| card7-findings-{en,ar}.png | 1080×1350 |
| card8-connected-{en,ar}.png | 1080×1350 |

## FIX_SOCIAL_CARDS (Tariq, 13 Nov 2026)

Text edits only: card 1 title "One connected network" / «شبكة واحدة مترابطة» (", in the model" and «في النموذج» dropped; «وحدة» corrected to «واحدة»); card 1 Arabic note «للمقارنة، وليست توصية»; card 4 label "Fastest train" / «أسرع قطار» ("in the model" / «في النموذج» dropped). The one project label line above the footer ("synthetic demand, uncalibrated: scenario comparison, not a forecast") is unchanged and still on cards 1–4. No figure, layout or source changed.

Nothing was posted or pushed. Tariq publishes.

## PUBLISH_PDF_POST (Tariq, 13 Nov 2026): cards 6 and 7

Two reply cards in the same renderer, CSV, footer and credits: card 6 "How the study worked" (five steps joined by arrows, no figures) and card 7 "Main findings" (riyals back per riyal, middle case, for three options, plus the Riyadh–Jeddah door-to-door result in words). They match the post draft `docs/publish/linkedin-method-findings.md`. Both carry the project label, because they describe modelled results. Word counts (`film.cards check`): card 6 en 18, ar 18; card 7 en 24, ar 25. The checker expects no figure on card 6 and exactly 6, 0.3 and 0.06 on card 7 (`film/cards.py` `expected`). Arabic: native_review = pending, as for cards 1–5.

Only cards 6 and 7 were rendered (`film.cards render --card 6`, then `--card 7`). SHA-256 of the ten card 1–5 PNGs, measured before and after: identical, and equal to the FIX_SOCIAL_CARDS values (`docs/status/main.md`, FIX_SOCIAL_CARDS block).

| file | SHA-256 |
|---|---|
| card6-method-en.png | f50303f0710c6e298ff0050c75f651834b9c319077eaa440a67f994c455f3fc9 |
| card6-method-ar.png | c4939778d452318d1280315815e47912ae014201ec6d0854d6528e552c673b38 |
| card7-findings-en.png | b84f45dc73abafcca1f55f49a6e2fdf4a12daba0b054151f4f66c7ec28d08762 |
| card7-findings-ar.png | dbb9947f13bd058a51dde4b06013c5f03668d2c0d5e0933920a2c7b813d93760 |

Nothing was posted or pushed. Tariq publishes.

## FIX_PDF_CONNECTED (Tariq, 13 Nov 2026): card 8

Card 8 "Connecting every region" / «ربط كل المناطق», in the same renderer, CSV, footer, credits and project label: a route map of the 16 S6-L6 corridors with 16 city names (map labels; not counted as body words), and three figures under it: 3,242 km of new line, 227 billion riyals to build (likely 123–860), 0.06 riyals back per riyal. Subtitle "16 new links join 18 cities"; note "A comparison, not a recommendation" (as card 1). Word counts (`film.cards check`): en 25, ar 23. The checker expects exactly 3,242, 227, 123, 860, 0.06, 16 and 18 on card 8 (`film/cards.py` `expected`). Arabic: native_review = pending. The Arabic range «المرجّح 123–860» was checked on a zoomed crop: it reads low–high.

Only card 8 was rendered (`film.cards render --card 8`). SHA-256 of the fourteen card 1–7 PNGs, measured before and after: identical (`logs/fix-pdf-connected/cards1-7-before.sha256`, `shasum -c` 14 of 14 OK).

| file | SHA-256 |
|---|---|
| card8-connected-en.png | d4aff40ef7e098436c4fbced2e8339792495553786264ae5a8918f1259bf8151 |
| card8-connected-ar.png | f92b5cc10264a463bd63332c7fa6dfc8d0af13103a77c9af34d75395558d64ff |

Nothing was posted or pushed. Tariq publishes.
