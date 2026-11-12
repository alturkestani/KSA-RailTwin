---
name: documentary-script
description: Writing the W10 bilingual documentary scripts: the eight-part narrative arc, one citation footnote per line, ranges not points, native Saudi-dialect writing rules and register choice, no fabricated quotes, the script file layout under film/script/ with a lines CSV, and the red-team check. Use for the Arabic and English cuts and both trailers.
---
> **Document version:** skills/documentary-script/SKILL.md v1.2 | 7 Nov 2026 | Author: coordinator (v1.2: R10 FIX_CP8_NOTES, Arabic label aligned to glossary term 4) | Status: active

# Documentary script

Two cuts (8–12 min each) and two trailers (60–90 s). The Arabic script is **written natively in Saudi dialect, not translated from the English**; the two cuts share facts and structure but may differ in phrasing. A human native Saudi speaker must review the Arabic script and audio before any release; Tariq approves both scripts at CP8 before any rendering.

## Narrative arc (PROJECT.md W10; every date and figure re-verified and cited)
1. History: the Hejaz Railway (opened to Madinah 1908, to verify) and its fate; Dammam–Riyadh (1951, to verify); SAR North line; Haramain HSR (2018, to verify); Riyadh Metro; Landbridge plans.
2. Today's gaps (from docs/coverage.md and the screening).
3. Global lessons: TGV, Shinkansen, AVE (from the W5 dossiers, with grades).
4. The simulated future network: maps and animations from the twin's own outputs (run ids on screen in the credits).
5. Economic benefits from the CBA: jobs, GDP, time savings, **always as ranges**.
6. Social benefits: small towns, commuting, women's mobility, family and Hajj/Umrah travel, emissions.
7. Honest risks and costs: overruns, fiscal exposure, what the model cannot say.
8. Closing vision tied to Vision 2030, framed as possibility, not promise.

## Files
`film/script/main.ar.md`, `film/script/main.en.md`, `film/script/trailer.ar.md`, `film/script/trailer.en.md`; `film/script/lines.csv` with columns `cut, lang, line_id, section, text, sources (S-xxx; A-xxx; run id), figure_values, on_screen_label, est_seconds, native_review (pending/approved by <initials> <date>)`; `film/script/dialect-recommendation.md`; `film/script/pronunciation.md` (place names with transliteration and stress). `uv run python -m film.script validate film/script/` checks that every line has a non-empty `sources`, that every numeric token in `text` appears in `figure_values`, and that every `S-xxx`/`A-xxx` exists.

## Writing rules
- One citation footnote per line (`[^S-xxx]`, `[^A-xxx]`, or `[^run:<id>]`); a line with no number still cites the document it rests on.
- Figures are spoken as ranges ("بين ١٢ و١٨ مليار ريال", "between 12 and 18 billion riyals"), never single points; model results say "في النموذج" / "in the model", never "سوف" / "will".
- No fabricated or paraphrased-as-real quotes; only verifiable published statements with the source read aloud or shown.
- Non-partisan: no entity is praised or blamed; options and evidence only; no logos.
- Every modelled scene carries the on-screen label "synthetic demand, uncalibrated" (Arabic, glossary term 4 in `docs/glossary.ar.md`: «طلب تركيبي غير مُعايَر»).
- The label and the credits name the sources, the run ids and the seed.

## Saudi-dialect writing rules
- Choose the register with the criteria in W10: intelligibility across regions, documentary tone, what Saudi broadcast documentaries use (cite 3+ examples with links), voice availability. Options: "white"/neutral educated Saudi close to Najdi; Hijazi; or a mix (Najdi narrator, Hijazi voices for western segments). Write the recommendation with reasons in `dialect-recommendation.md`.
- Write the lines as a Saudi narrator would speak them: dialect function words (مثلاً: «وش»، «ليه»، «كذا» only where the register allows), numbers spoken the Saudi way, no MSA case endings; keep technical terms in their common Saudi usage and give the English in parentheses in the lines CSV only.
- Place names with the local pronunciation (`pronunciation.md`); numbers written in words where TTS mispronounces digits (`voiceover-tts` finds out).
- Mark every line `native_review: pending` until a native speaker initials it.

## Red-team check
The `red-team-verifier` runs `film.script validate`, `common.sources bilingual-check` across the two cuts' `figure_values`, spot-checks 10 % of lines against their sources, and FAILs on any unlabelled model claim, single-point figure, unsourced quote, or advocacy.

**Model policy (Tariq, 31 Oct 2026):** a paid state-of-the-art model or API may be used for Saudi-dialect Arabic script and narration (R10) and for Arabic–English translation of final deliverables (R8) where it materially improves quality — only after the one-paragraph request in `docs/STATUS.md` is approved, with one open-vs-paid A/B sample shown first, every call logged with vendor and model, no personal or partner data sent, and no API keys in the repo (see `CLAUDE.md` "Model policy" and the `local-models` skill).
