> **Document version:** docs/dialect-recommendation.md v1.1 | 7 Nov 2026 | Author: R10 builder (v1.1: source and assumption paths, A-film-005); documentary-director (R10) | Status: draft (recommendation for Tariq, CP8)

# Arabic register for the documentary: recommendation

**This is a recommendation for Tariq, not a decision.** Nothing is rendered or recorded until Tariq approves the register, both scripts, the storyboard and the voice at CP8. A human native Saudi speaker reviews the Arabic script and audio before any release (section 5).

The film is a personal, independent research documentary about a feasibility study of a national Saudi rail network. It is not an official or ministry film, and it speaks for no entity. The register has to sound Saudi, be understood in every region, keep a documentary's dignity, and leave room for the hedges the study requires ("in the model", ranges, scenario rather than forecast).

Sources are in `docs/sources/r10.csv` (ids `S-r10-d01` to `S-r10-d14`, all pages opened on 7 Nov 2026). The register choice is recorded as assumption `A-film-005` in `film/assumptions-r10.md`. Statements marked *judgement* are the author's linguistic assessment, not sourced facts, and go to the native reviewer.

## 1. Options

| | Option | What it means here |
|---|---|---|
| a | **White Saudi register** (اللهجة البيضاء), Najdi-leaning, educated | Saudi colloquial grammar and pronunciation, without strongly local markers; common, educated vocabulary; no MSA case endings. Researchers describe an emerging Saudi koiné that Hijazi and Najdi speakers call the "white dialect", with Najdi as the strongest influence [S-r10-d12]. |
| b | **Hijazi** | The urban dialect of Jeddah, Makkah and Madinah, for the whole narration. |
| c | **Mix** | A white, Najdi-leaning narrator for the national story, with Hijazi voice(s) for western-region segments (the Hejaz Railway, the Haramain line, Jeddah). |
| d | **MSA** (فصحى) | Formal standard Arabic for the narration; considered here for contrast. |

## 2. Scores against the four W10 criteria

Scale: strong / good / fair / weak (*judgement*, with the evidence each rests on).

| Criterion | a. White Saudi | b. Hijazi | c. Mix | d. MSA |
|---|---|---|---|---|
| Intelligibility across all regions | **strong**: described as a "national colloquial" understood by all Saudis [S-r10-d10]; preferred by 85% of Saudi consumers surveyed for advertising, defined as understood in all regions [S-r10-d11] | good: widely heard in Saudi media [S-r10-d13], but heard as a regional voice outside the west (*judgement*) | good: each part is understood; switching adds no comprehension (*judgement*) | strong for comprehension, but not the "authentic Saudi dialect" the brief asks for |
| Fit with documentary tone | good: dignified if kept educated and free of slang (rules in section 4); risk: the same register is the advertising register [S-r10-d10, S-r10-d11], so it must not sound like a commercial (*judgement*) | good for western stories; reads as a western film for a national subject (*judgement*) | fair: region-by-region dialect switching can read as caricature, and the film has no recorded interviews that would justify it (no fabricated voices; rule 7, no survey or interview fielded) | fair: reads as official; government accounts were observed to hold to fusha [S-r10-d10], which this independent film should not imitate (*judgement*) |
| What Saudi documentaries use (section 3) | good: recent Saudi documentary series carry Saudi colloquial titles [S-r10-d06, S-r10-d07, S-r10-d09]; narration register not verified from text | fair: no Hijazi-narrated national documentary found today | fair: no example of this pattern found today | fair: at least one government documentary series has an MSA title [S-r10-d08]; narration register not verified |
| Availability of a good voice | **strong**: Nabrah's public voices Daniah, Norah and Abdullah are each labelled "Saudi" and tuned for Saudi and Gulf Arabic [S-r10-d01, S-r10-d02]; human Saudi narrators offer white and Najdi registers for documentary work [S-r10-d14] | weak for TTS: no Nabrah voice carries a Hijazi label [S-r10-d01, S-r10-d03]; a human narrator would be needed | weak: the Hijazi part has no verified TTS voice [S-r10-d01, S-r10-d03] | good: open models list Arabic without a dialect [S-r10-d05], and the earlier open test read vowelised MSA well (`docs/STATUS.md`, paid-model request 1) |
| **Overall** | **recommended** | second choice | not recommended for narration | narration: no; verbatim on-screen quotes: yes |

Notes on voice availability:
- **Nabrah** (paid, approved for the A/B; publication and broadcast of the public voices on a paid plan confirmed in writing, `docs/licences.md`): every public voice is labelled simply "Saudi"; the pages name no Najdi, Hijazi or white sub-variety [S-r10-d01, S-r10-d02, S-r10-d03]. Whether the three voices sound Najdi-leaning or white has to be heard in the A/B, not read from the page.
- **ElevenLabs**: the Arabic page claims only that its TTS "can adapt to various regional Arabic accents" and names no Saudi variant [S-r10-d04]. Saudi-dialect quality is unknown until the A/B.
- **Open models** (rule 12, tested first): Chatterbox Multilingual lists Arabic among its languages, names no Arabic dialect and is MIT-licensed [S-r10-d05]. The brief's working expectation that open models lean towards MSA or Levantine Arabic is **not confirmed by the card**; it is a hypothesis for the A/B, scored on dialect authenticity by a native listener.
- **Human Saudi narrator**: fallback. One freelance listing offers Najdi, white and fusha registers for documentary work [S-r10-d14]; one listing is not a market rate, and `voice-audio` sources the cost and timeline range.

## 3. What Saudi documentaries use: verified examples and limits

Verified today: each title below exists as a Saudi documentary series on a named broadcaster or platform. **Not verified: the register of the narration.** None of the pages states the narration dialect, and no audio was downloaded or transcribed for this note. What can be said from the published text:

| Example | Broadcaster / platform | What the page confirms | Register evidence |
|---|---|---|---|
| Thmanyah, «ذا قال» (Tha Qal), 10-episode series presented by Khaled Oun; Thmanyah reports more than 250 documentary titles [S-r10-d06] | Al-Thaqafeyah channel and Shahid | The title "means 'he said' in the Saudi dialect" (press release) | Title in Saudi dialect (stated by the source); narration to confirm by listening |
| «من هالأرض», Government Communication Center, Ministry of Media, with the Saudi Tourism Authority, 2023, 10 episodes [S-r10-d07] | Saudi First Channel, Shahid, the Center's YouTube channel | Producer, year, platforms | Title uses the colloquial «هالـ» form (*judgement* from the published title); narration to confirm by listening |
| «ماذا يأكل السعوديون», same initiative, 2023 [S-r10-d08] | Shahid, the Center's YouTube channel, Saudi First Channel | Producer, year, platforms | Title in MSA; narration to confirm by listening |
| «حنا», presented by Ahmed Al Othman, first aired 21 May 2024 [S-r10-d09] | MBC Shahid | Docuseries, presenter, date | Title is the colloquial Saudi «حنا» ("we") (*judgement* from the published title); narration to confirm by listening |

Supporting evidence on the media landscape: a 2025 study of a long-running Saudi TV series found Najdi represented most, then Hijazi, with the Northern dialect largely neglected [S-r10-d13]. That is a comedy series, not a documentary; it is cited only for which Saudi dialects national audiences hear most.

**What this supports:** the same government documentary initiative used both a colloquial and an MSA title [S-r10-d07, S-r10-d08], and the largest Saudi documentary producer named a broadcast series in Saudi dialect [S-r10-d06]. Saudi colloquial is therefore in use in national documentary titling. **What it does not prove:** that the narration of these series is in the white register. Before CP8, Tariq or the native reviewer should listen to one episode of each and record the register in `film/script/review-log.md`; if the narration turns out to be MSA, the scores in section 2 change for criterion 3 only.

Searches that found nothing usable today: a Saudi-produced railway documentary; any page that explicitly describes a Saudi documentary as narrated in the white, Najdi or Hijazi dialect. Thmanyah's own site returned a bot checkpoint and was not read.

## 4. Recommendation

**Recommended (for Tariq to decide at CP8): option a, an educated white Saudi register, Najdi-leaning, used by every narrator in the Arabic cut and trailer. MSA appears only for verbatim on-screen quotations of official documents.**

Reasons:
1. **Intelligibility:** it is the register Saudis describe as understood in every region [S-r10-d10, S-r10-d11], and the emerging national koiné it rests on is closest to Najdi [S-r10-d12]. A national rail film should not sound like one city.
2. **Tone:** written to the rules below, it keeps the dignity of a documentary without the official distance of MSA, which suits an independent, non-partisan film [S-r10-d10].
3. **Practice:** Saudi documentary series use Saudi colloquial in their public titles [S-r10-d06, S-r10-d07, S-r10-d09]. The narration register of those series is still to confirm by listening (section 3).
4. **Voice:** the approved paid candidates are Saudi voices [S-r10-d01]; no verified Hijazi TTS voice exists for option b or c [S-r10-d01, S-r10-d03].
5. **Western segments:** the Hejaz Railway, Haramain and Jeddah stories are told in the same register. Hijazi colour comes from correct local pronunciation of place names (`film/script/pronunciation.md`) and, only if real, published Hijazi speech exists with rights, from that archive audio, credited and sourced. No Hijazi voice is invented for a "character".
6. **MSA** is used on screen only, for verbatim quotations of official documents (a Vision 2030 text, a decree, a published statement), with the source shown; the narrator introduces it in dialect («وهذا نص اللي نُشر:») and does not perform it.

**Three voices, both cuts (launch note).** The three Nabrah public voices can carry both language cuts in the same three roles, so neither language is the lesser version:

| Role | Covers | Proposed voice (provisional) |
|---|---|---|
| Guide | opening, transitions, social benefits, closing as possibility | Abdullah (male, Saudi) [S-r10-d01] |
| History and existing network | Hejaz Railway, Dammam–Riyadh, SAR North, Haramain, Riyadh Metro, Landbridge (as announced/planned) | Norah (female, Saudi) [S-r10-d01] |
| Method and numbers | global lessons, the model, CBA ranges, risks and costs | Daniah (female, Saudi) [S-r10-d01] |

The assignment is a placeholder until the A/B is heard. Open points: (i) the Nabrah pages claim Saudi and Gulf Arabic for these voices and list English for agents generally [S-r10-d01, S-r10-d02], but **English quality of these three voices is not verified**; the A/B includes one English paragraph per voice; (ii) all three must read the same register; if one sounds markedly Hijazi or Gulf in the A/B, it moves to a role with fewer lines or is replaced by another public voice.

Second choice: option b (Hijazi) if the A/B shows the Nabrah voices are Hijazi-leaning and Tariq prefers that colour; it would still follow the rules below, with Hijazi function words.

## 5. Writing rules for the Arabic script (white register)

### 5.1 Function words (*judgement*, for native review)

| Use | Avoid in narration | Why |
|---|---|---|
| «اللي» (relative) | «الذي/التي» except in on-screen MSA quotes | Saudi-wide |
| «كذا» (like this, so) | «هيك» (Levantine), «كده» (Egyptian) | Saudi-wide |
| «ليه» (why) | «ليش» if it sounds too local in the A/B; never «لماذا» in narration | common in Saudi speech |
| «مو» (not), sparingly, mainly in «سيناريو، مو توقّع» | «مش» (Egyptian/Levantine) | Saudi-wide; keeps the hedge short |
| «يعني», at most once per section, to explain | «يعني» as filler | dignity |
| «هالـ» (هالمدن، هالسؤال) | | Saudi-wide |
| «كيف»، «متى»، «وين» for questions | «وش» (strong Najdi marker), «إيش» (Hijazi marker) | keeps the register white |
| «اليوم»، «حالياً» | «الحين» (Najdi), «دحين» (Hijazi) | avoids a regional marker |
| «مثل» | «زي» | more formal, Saudi-wide |
| «كثير»، «جداً» | «مرّة» (very), «واجد» (eastern/Gulf) | avoids youth slang and regional markers |
| «يحتاج» | «يبي» (Najdi), «يبغى» (Hijazi) | avoids a regional marker |
| «نتكلم عن» | «نحكي عن» | «نحكي» reads Levantine/Hijazi |
| Omit the pronoun («رسمناها للدراسة») | choosing between «حنا» and «احنا» | both are regionally marked; the reviewer decides if one is needed |

No MSA case endings, no «سوف», no «إنّ … لـ» emphasis chains, no slang, no jokes, no regional stereotypes.

### 5.2 Numbers, ranges and percentages
- Every figure is a range, spoken «بين … و …» or «من … إلى …», with the middle value only as «والحالة الوسطى حوالي …». Never a single point for a cost or benefit.
- Percentages are spoken «بالمية» (pattern: «بين [أ] و[ب] بالمية»), not «في المئة». Large sums: «مليون»، «مليار ريال».
- Written form follows the Arabic glossary (`docs/glossary.ar.md`): Western digits, numeric runs and ranges inside left-to-right isolates. Where TTS misreads digits, the line is written in words; `voice-audio` finds out in the A/B.
- Arabic and English lines carry the same figures digit for digit (`figure_values` in `film/script/lines.csv`).

### 5.3 Model hedges
- Every simulated result: «في النموذج، …» at the start of the line. Never «سوف», «راح», «بيصير» or any promise.
- The scenario framing: «هذا سيناريو للمقارنة، مو توقّع.»
- The on-screen label uses the glossary term (`docs/glossary.ar.md`, term 4: «طلب تركيبي غير مُعايَر»), not «اصطناعي».
- The closing vision is a possibility: «ممكن»، «لو»، «احتمال»; never «بتصير» or «راح نشوف».

### 5.4 Technical terms
- «سكة الحديد» / «السكك الحديدية» for the network; «القطار السريع» for high-speed rail; «قطار الضواحي» for commuter rail (glossary term 14); «محطة»؛ «خط» (plural «خطوط»); «مسار» for an alignment; «شحن» for freight; «ركاب» for passengers.
- The three layers are always named: «قائم» (existing), «معلَن أو قيد الطرح» (committed/under procurement), «افتراضي رسمناه للدراسة» (hypothetical, ours). A planned line is never called «موجود».
- «تكلفة»، «منافع»، «تحليل التكلفة والمنفعة»، «مخاطر»، «تجاوز التكاليف» as in the executive summary; the executive summary is the terminology source, not a script to translate.
- Place names: local pronunciation, recorded in `film/script/pronunciation.md`.

### 5.5 Example lines (generic; no figures; register only)
1. «لو فيه قطار يربط هالمدن ببعض، كيف تتغيّر رحلة الناس اليومية؟»
2. «في النموذج، الرحلة بين المدينتين تقصر… بس هذا سيناريو للمقارنة، مو توقّع.»
3. «الأرقام هنا نطاق، مو رقم واحد: فيه حد أدنى، وحد أعلى، وحالة وسطى بينهم.»
4. «هذا الخط معلَن ومخطّط له، لكنه ما تشغّل إلى اليوم.»
5. «الخطوط اللي تشوفها بهاللون افتراضية، رسمناها للدراسة، مو مشاريع معتمدة.»
6. «وكل مشروع بهالحجم له تكلفة وله مخاطر، ولازم نتكلم عنها بوضوح.»
7. «التجارب برّا تعطينا دروس، اللي نجح منها واللي تعثّر.»
8. «كل رقم تسمعه له مصدر، والمصدر مكتوب على الشاشة.»
9. «هذي مو وعود… هذي احتمالات، والقرار في النهاية لأصحابه.»

## 6. Native review (required before release)
- A human native Saudi speaker reviews the Arabic script before any recording and the Arabic audio before any release: register, naturalness, place-name pronunciation, and any line that sounds regional, slangy or like an advertisement.
- **Tariq arranges the reviewer.** No agent contacts any narrator, broadcaster or reviewer (rule 7).
- The review is recorded in `film/script/review-log.md` (name withheld if preferred, date, changes). Until then every line in `film/script/lines.csv` stays `native_review: pending`, and the log stays empty; it is never filled in by an agent.
- The reviewer is also asked to listen to one episode of each series in section 3 and note its narration register.

## 7. Open questions for Tariq (CP8)
1. Register: option a (recommended) or b?
2. Voice roles: keep the provisional assignment, or decide after hearing the A/B?
3. Should the narrator's gender lead (guide) be male or female?
4. Who reviews the Arabic, and when?
