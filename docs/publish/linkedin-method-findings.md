> **Document version:** docs/publish/linkedin-method-findings.md v1.1 | 13 Nov 2026 | Author: main builder (PUBLISH_PDF_POST; v1.1 FIX_PDF_CONNECTED: 56 pages, repository live, card 8 in the reply order, card 5 dropped from it) | Status: draft

# LinkedIn post draft: method and findings (English)

Draft for Tariq, to go out with the English film with Arabic subtitles (`renders/out/social/subs/main-en-subAR.mp4` on the external volume, `film/renders` symlink). Nothing has been posted. Tariq publishes (rule 7).

- Length: **1,937 characters** for the post body below (Python `len()` of the text between the fences, spaces and line breaks included; the first comment is excluded). Target 1,300–2,000.
- Hashtags: 3. Links: none in the body; they go in the first comment.
- Plain words: no NPV, BCR, P10/P50/P90, capex or present value. Checked with the cards' jargon list (`film.cards.jargon_hits`); `tests/test_linkedin_post.py` repeats the checks.
- Spend figures are **as of commit d58ef2a**, the start HEAD of the PUBLISH_PDF_POST run (its cost log equals ef50569's; d58ef2a only adds the prompt). This run cannot cost itself: its own row is added after it ends, so the post's figures stop before it.
- "Claude" is named as the tool, as on card 5; no model names (CLAUDE.md, model mapping).

## Post

```text
Thank you, Claude.

Over the past two weeks I ran an independent study of a question I care about: where could rail connect more of Saudi Arabia, and would it be worth building? Claude wrote the code and ran the analysis; I reviewed and decided at every checkpoint. As of commit d58ef2a it took 96 Claude runs, about USD 1,347 at list price (covered by my subscription, so a reference cost, not a bill), plus about USD 7 for the paid voices in the film.

How it worked, in plain words:
• Public, open data: OpenStreetMap, the 2022 census, open elevation data. All 150 governorates were screened.
• Every hypothetical line was routed over real terrain. Tested on three lines that already run, including the Haramain line between Makkah and Madinah: lengths came within 5%, paths 3 to 10 km off. Sketches, not designs.
• Costs are ranges that allow for overruns like past rail projects (a reference class of 355 rail projects).
• Travellers are simulated. In the study's words: synthetic demand, uncalibrated: scenario comparison, not a forecast.

What the model found (middle case, riyals back for every riyal spent):
• Three new stations on existing and committed lines: about 6.
• The committed lines: about 0.3.
• A direct Riyadh–Jeddah railway: about 0.2. Door to door, the flight (3 h 11 min) beats the fastest modelled train (4 h 57 min).
• One connected network reaching Tabuk, Abha, Najran and Jazan: 32.7 million people within two hours of a station instead of 26.1 million, for 123 to 860 billion riyals and about 0.06 back.
• Those riyals are benefits to people, not ticket income: no option pays for itself from fares.

What AI changes: one person can lay many options side by side, quickly and in the open. Here, 71 candidate corridors, each tested over 10,000 random draws, every figure sourced. People still decide; the machine only searched.

Film below. Report and code in the first comment.

#OpenData #Rail #SaudiArabia
```

## First comment

```text
Links:
• Report (PDF, 56 pages): https://github.com/alturkestani/KSA-RailTwin/blob/main/docs/report/feasibility-report.pdf
• Code, data sources and method notes (Apache-2.0): https://github.com/alturkestani/KSA-RailTwin
Independent simulation, not a government plan. Synthetic demand, uncalibrated: scenario comparison, not a forecast.
```

- The repository `https://github.com/alturkestani/KSA-RailTwin` is **live**: public, Apache-2.0, first commit 84ddeef (pushed by Tariq). The PDF link points to `docs/report/feasibility-report.pdf` in that repository, and it **resolves only after the public export is refreshed and pushed** (FIX_PDF_CONNECTED makes the refresh commit; Tariq pushes it). Until then, the PDF is on the external volume at `renders/out/social/feasibility-report.pdf` (`film/renders` symlink) for direct upload.
- The "56 pages" in the comment is the page count of the PDF built at e3c5e78, after the S6-L6 section was added (`pdfinfo`; `docs/status/main.md`, FIX_PDF_CONNECTED block). Rebuilding after a content change can change it: re-check before posting.

## Suggested order for the reply section

The film is the post. Under it: the first comment (links), then the cards as replies, one image each, in this order. English cards for the English post; the Arabic cards (`*-ar.png`, native_review = pending) are for an Arabic post or replies to Arabic comments.

| # | reply | file (`renders/out/social/cards/`) | one-line caption |
|---|---|---|---|
| 1 | first comment | (text above) | Links: the full report (PDF) and the open code. |
| 2 | card 6, method | `card6-method-en.png` | How the study worked, in five steps. |
| 3 | card 7, findings | `card7-findings-en.png` | The main findings, in riyals back for every riyal spent. |
| 4 | card 3, payback | `card3-payback-en.png` | All five options side by side, with the line at 1. |
| 5 | card 2, cost | `card2-cost-en.png` | What they cost to build, with ranges that allow for overruns. |
| 6 | card 4, Riyadh–Jeddah | `card4-riyadh-jeddah-en.png` | Why the plane still wins Riyadh–Jeddah door to door. |
| 7 | card 1, network | `card1-network-en.png` | The connected network the study drew, as a comparison. |
| 8 | card 8, connecting every region | `card8-connected-en.png` | The 16 links that join 18 cities, with their length, cost and riyals back. |

Card 5 (`card5-how-made-en.png`) is no longer in the suggested order (Tariq, 13 Nov 2026), because the post itself states the spend. The file stays. Card 5 counts the log as of commit cf504dc (93 runs, USD 1,325); the post counts it as of d58ef2a (96 runs, USD 1,347). Both say which commit they count to.

## Trace table (exact value → post value → file:line)

Rounding follows the film and the cards (`docs/publish/social-cards.md`, `film/storyboard/rounding-log.csv`). Study labels as in the cards' trace: S1 = committed lines, S6-L2 = three new stations, S6-L6 = connected network, RJ = the Riyadh–Jeddah side study.

| post text | exact value (study label) | post value | file:line |
|---|---|---|---|
| "commit d58ef2a" | start HEAD of this run | d58ef2a | `git log` (d58ef2a, prompt commit on ef50569) |
| "past two weeks" | first commit 30 Oct 2026 (b15788e); first cost-log row 2026-10-30; post drafted 13 Nov 2026 | two weeks | `git log --reverse`; `docs/cost-log.csv:2` |
| "96 Claude runs" | 96 rows whose `label` is not `PAID` (definition `docs/spend-summary.md:10`) | 96 | `docs/cost-log.csv` lines 2–132 at d58ef2a; `uv run python -m common.cost_log summary`, TOTAL row (`runs 96`) |
| "about USD 1,347 at list price" | USD 1,347.12, list price under a subscription (reference cost, not a charge) | USD 1,347 | same rows, column `usd_list`; summary TOTAL row (`USD 1347.12`) |
| "about USD 7 for the paid voices" | USD 7.09 over 35 `PAID` rows (ElevenLabs, Nabrah) | USD 7 | `docs/cost-log.csv` `PAID` rows; summary "PAID TOTAL" row (`calls 35 USD 7.09`); `docs/publish/social-cards.md:38` |
| "the 2022 census" / "All 150 governorates" | GASTAT Census 2022; 150 governorates screened | 2022; 150 | `film/script/lines.csv:85` (m-02-06); `docs/coverage.md` |
| "three lines that already run, including the Haramain line" | validation on HHR, SAR North passenger, SAR East passenger | three | `docs/alignments.md:65`; `film/script/lines.csv:109` (m-06-02) |
| "between Makkah and Madinah" | the Haramain line links Makkah, Jeddah and Madinah | words | `film/script/lines.csv:83` (m-02-04) |
| "lengths came within 5%" | length target ±5 % met on all three lines | 5% | `docs/alignments.md:67`; `film/script/lines.csv:109` (m-06-02) |
| "paths 3 to 10 km off" | mean offset HHR about 3.3 km, SAR North and SAR East about 9–10 km | 3 to 10 km | `docs/alignments.md:68`; `film/script/lines.csv:109` (m-06-02) |
| "355 rail projects" | reference class of 355 rail projects | 355 | `film/script/lines.csv:113` (m-06-06); `docs/publish/social-cards.md:26` |
| "Three new stations …: about 6" | 5.9618 (S6-L2, middle case, UN WPP medium, 60 years) | about 6 | `docs/publish/social-cards.md:27`; `film/storyboard/rounding-log.csv:3`; `film/script/lines.csv:120` (m-08-02) |
| "The committed lines: about 0.3" | 0.3057 (S1 vs today) | about 0.3 | `docs/publish/social-cards.md:29`; `film/storyboard/rounding-log.csv:2`; `film/script/lines.csv:119` (m-08-01) |
| "A direct Riyadh–Jeddah railway: about 0.2" | 0.182 to 0.244 over the five RJ sketches | about 0.2 | `docs/publish/social-cards.md:30`; `film/storyboard/rounding-log.csv:6`; `film/script/lines.csv:126` (m-08-08) |
| "the flight (3 h 11 min)" | 191.0 min door to door, city centre to city centre | 3 h 11 min | `runs/study/rj/times-s1/air.json:6`; `docs/publish/social-cards.md:33` |
| "the fastest modelled train (4 h 57 min)" | 297.3 min (RJ-A, 350 km/h, P50) | 4 h 57 min | `runs/study/rj/times-s1/times.csv:9`; `docs/publish/social-cards.md:34` |
| "reaching Tabuk, Abha, Najran and Jazan" | S6-L6 lines to Tabuk, Abha/Khamis Mushait, Najran and Jazan | names | `film/script/lines.csv:131` (m-08-16); `docs/publish/social-cards.md` card 1 row |
| "32.7 million people within two hours of a station instead of 26.1 million" | 32,739,046 (S6-L6) and 26,096,670 (S1), national reach at 120 minutes | 32.7 / 26.1 million | `film/storyboard/rounding-log.csv:8-9`; `film/script/lines.csv:132` (m-08-17) |
| "123 to 860 billion riyals" | 122,532.0 to 860,035.3 SAR m (S6-L6 cost to build, likely range) | 123 to 860 billion | `runs/r6/l6/score/S6-L6.csv:2` (`capex_p10`, `capex_p90`); `docs/publish/social-cards.md:24` |
| "about 0.06 back" | 0.06097 (S6-L6) | about 0.06 | `docs/publish/social-cards.md:31`; `film/storyboard/rounding-log.csv:10`; `film/script/lines.csv:134` (m-08-19) |
| "no option pays for itself from fares" | in the low population case, fares cover less than half of running and renewal costs on every CP7 layout | words | `film/script/lines.csv:123` (m-08-05); `docs/report/feasibility-report.md:130` |
| "71 candidate corridors" | 71 | 71 | `film/script/lines.csv:114` (m-07-01) |
| "10,000 random draws" | 10,000 | 10,000 | `film/script/lines.csv:115` (m-07-02) |
| "People still decide; the machine only searched." | "The machine searched; it did not decide." | words | `film/script/lines.csv:118` (m-07-05) |
| first comment "56 pages" | 56 (`pdfinfo` Pages) | 56 | `docs/report/feasibility-report.pdf` built at e3c5e78; `docs/status/main.md` (FIX_PDF_CONNECTED block) |

The "riyals back for every riyal spent" figures are middle-case values (P50 of the draws), as on card 3 and in the film; the ranges are in the report (§4) and in `docs/publish/social-cards.md`.

## Wording choices

- "Those riyals are benefits to people, not ticket income": the "riyals back" count economic benefits (time and cost savings, safety and the other appraised streams), not fares; fares are a separate test (report §1.3, §4.5).
- "Sketches, not designs" and "3 to 10 km off" keep the alignment caveat (report label) in the post.
- The project label is quoted word for word in the body and again in the first comment (rule 3).
