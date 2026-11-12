> **Document version:** docs/glossary.ar.md v1.2 | 6 Nov 2026 | Author: FIX_R8 builder (from Tariq's R8-checkpoint review, 5 Nov 2026; v1.1: §typography, item 4); FIX_R8_RTL (v1.2: no-break rule, parentheses and footnote markers in isolates) | Status: draft

# Arabic glossary (مسرد المصطلحات العربية)

One preferred Arabic form per concept, used in every Arabic deliverable: `docs/executive-summary.ar.md`, the Arabic figure titles (`title_ar` in `common/figures.py`, written to `docs/deck-figures/figures.csv` by `uv run python -m common.figures build`), and any Arabic string in `web/` and `api/`. `docs/report/**` has no Arabic prose (only place names and the original titles of Arabic sources, which are quoted as published and are out of scope).

"Source" says where the form comes from: **Tariq** = verbatim from Tariq's R8-checkpoint review (`prompts/FIX_R8.md`, items 2 and 3); **builder** = proposed in FIX_R8 for consistency with Tariq's forms, pending his native review like the rest of the Arabic summary. Rejected forms must not appear in the Arabic deliverables; `tests/test_glossary_ar.py` checks both lists.

## 1. Terms

| # | English concept | Preferred Arabic form | Rejected forms | Source | Note |
|---|---|---|---|---|---|
| 1 | upside (case) | `الحالة الأعلى عائداً` | `الحالة المتفائلة` | Tariq | S6-L1. |
| 2 | committed (programme, lines) | `الملتزم به` | `الملتزم` without `به`/`بها` (e.g. `البرنامج الملتزم والخيارات`) | Tariq | The pronoun agrees with its noun: `البرنامج الملتزم به`, but `الخطوط الملتزم بها` (non-human plural). |
| 3 | robust NPV | `صافي القيمة الحالية الصامد (robust NPV)` on first use in each Arabic document, then `صافي القيمة الحالية الصامد` alone | `القيمة الحالية الصامدة` (adjective on the wrong noun); `المتين` | Tariq | Exactly one bracketed gloss per document. |
| 4 | synthetic, uncalibrated demand | `طلب تركيبي غير مُعايَر` | `طلب اصطناعي`, `اصطناعي` | Tariq | In the Arabic label line and wherever the summary says the demand is synthetic (`الطلب تركيبي`). |
| 5 | alignments (indicative least-cost sketches on 30 m terrain) | `ومسارات الخطوط مخططات تقريبية استرشادية بأقل تكلفة على نموذج تضاريس بدقة 30 م` | `رسوم استرشادية` | Tariq | Elsewhere `مسارات الخطوط` alone. |
| 6 | travel times (running times in the label) | `أزمنة الرحلة` | `أزمنة التشغيل` | Tariq | |
| 7 | judge v3 (the frozen appraisal model) | `نموذج التقييم judge v3` | `المُحكِّم`, `المحكم` | Tariq | |
| 8 | seed | `البذرة العشوائية` (e.g. `بالبذرة العشوائية 1`) | `البذرة` without `العشوائية` | Tariq | |
| 9 | availability PPP | `الشراكة بين القطاعين العام والخاص بنظام مدفوعات الإتاحة` | `دفعات الإتاحة`, `القائمة على الإتاحة`, `الشراكة مع القطاع الخاص` | Tariq | After the full form, `الشراكة` alone. |
| 10 | across every registered parameter range | `عبر جميع نطاقات المَعلَمات المسجَّلة` | `نطاق مسجَّل للمعاملات` | Tariq | |
| 11 | contingent liability | `التزام محتمل (طارئ)` | `التزام احتمالي` | Tariq | |
| 12 | the private partner's cushion | `هامش الحماية لدى الشريك الخاص` | `هامش الشريك الخاص` | Tariq | |
| 13 | net fiscal cost | `صافي التكلفة على المالية العامة` | `صافي التكلفة المالية` | Tariq | |
| 14 | commuter belt (Riyadh) | `حزام لقطارات الضواحي حول الرياض` | `الركاب اليوميين` | Tariq | |
| 15 | reach alternative (S6-L3) | `بديل التغطية الأوسع` | `بديل الوصول` | Tariq | |
| 16 | the Al-Kharj spur | `الخط الفرعي إلى الخرج` | `فرع الخرج` | Tariq | Full form on first mention and wherever Al-Kharj is named; later `الخط الفرعي` or `الفرع` alone. |
| 17 | ticket revenue (fares) | `إيرادات التذاكر` | `أجور`, `الأجور` | Tariq | |
| 18 | fare-setting authority | `الجهة التي تحدد تعرفة تذاكر الركاب` | `الجهة التي تحدد أجور الركاب` | Tariq | |
| 19 | GCC Railway | `سكة حديد دول مجلس التعاون الخليجي` | `مجلس التعاون` without `الخليجي` | Tariq | |
| 20 | screening | `الفرز` (e.g. `فرز جميع المناطق والمحافظات`) | `مسح` | Tariq | |
| 21 | within the host line's procurement | `ضمن عقد طرح الخط المضيف` | `مشتريات الخط المضيف` | Tariq | |
| 22 | wider economic impacts, freight and foreign visitors are outside the rankings | `أما الآثار الاقتصادية الأوسع والشحن والزوار من خارج المملكة فلا تدخل في ترتيب الخيارات.` | `القادمون من الخارج`, `خارج الترتيب` | Tariq | |
| 23 | draft note | `مسودة بانتظار مراجعة لغوية من متحدث أصلي (طارق)؛ لا تُستخدم خارج المستودع قبل اعتمادها.` | | Tariq | Kept next to the English note. |
| 24 | survey (fielded) | `استبيان ميداني` | `مسح ميداني` | builder | Avoids `مسح`, which term 20 reserves against screening. |
| 25 | reach (population within 120 minutes) | `التغطية` | `الوصول` for reach (`نطاقات الوصول` stays for isochrones, a different concept) | builder | Matches term 15; fig08 title. |
| 26 | 120-minute reach, door-to-door from the five metros | `في نطاق 120 دقيقة من الباب إلى الباب من المدن الخمس الكبرى` | `120 دقيقة` without `من المدن الخمس الكبرى` | Tariq (FIX_R8 item 9c form) | |
| 27 | the Al-Kharj difference (S6-L1 against the same layout without the spur) | `الفرق بين S6-L1 والمخطط نفسه دون الخط الفرعي إلى الخرج هو 4,231 مليون ريال` | `يعود … منه إلى الفرع` (an additive share) | builder (FIX_R8 item 9b) | A difference between layouts, never a share. |
| 28 | in the model | `في النموذج` | | builder (FIX_R8 item 9a) | Every S1 NPV sentence carries it. |

## 2. Typography (§typography)

**Rule: every numeric run in Arabic text sits inside a left-to-right isolate**, U+2066 LEFT-TO-RIGHT ISOLATE before it and U+2069 POP DIRECTIONAL ISOLATE after it (in HTML, `<bdi dir="ltr">` does the same). A numeric run is a signed number (`−894`, `+1,631`, `±5`), a range of numbers joined by ` / ` or `–` (`−2,958 / −724 / +1,631`, `801 / 1,423 / 5,286`, `3–10`) or a quantile label (`P10 / P50 / P90`). The pattern is `common.ar_render.RUN_PATTERN`; `common.ar_render.isolate_numeric_runs` applies it (idempotent; code spans and link targets are left alone). Unsigned single numbers (`2030`, `11,023`, `4.25`) need no isolate. Digits stay Western, as in the English summary and the figures.

**Why (FIX_R8 render check, 5 Nov 2026).** Rendered right to left (`dir="rtl"`, Noto Naskh Arabic, headless Chrome), the minus sign U+2212 has no strong direction, so in an RTL paragraph it was drawn on the right of its digits (`2,958−`), and the numbers of a ` / ` triple, and the two ends of a `3–10` range, were laid out right to left, so the P10 value of a range stood where the English reader expects P90. `common.ar_render bidi-probe` measures the on-screen x position of every character of every numeric run: before the isolates 23 of 35 runs were out of order; after, 0 of 29 (the six fewer runs are the English label lines, now rendered left to right as their own paragraphs). Inside an isolate each run keeps its logical left-to-right order, so every range reads P10 / P50 / P90 from left to right exactly as in the English summary and on the figures; the Arabic words around it still run right to left.

**Also.** The English label line and its Arabic rendering are separated by a bare `>` line so that Markdown keeps them as two paragraphs (one LTR, one RTL) instead of merging them into one mixed-direction paragraph. The version header line carries no Arabic word, so it renders left to right. `bidi-check`: `tests/test_ar_render.py` fails if any numeric run of `docs/executive-summary.ar.md` is outside an isolate, and (when Chrome is present) if the probe finds a run out of order.

**No line break inside a numeric run (FIX_R8_RTL, Tariq, 6 Nov 2026).** An isolate keeps a run's characters in order on each line, but when the run wraps, the RTL reader meets the fragment's trailing `/` or `(` first: `(/ P10` in §1, `/ −724 / −2,958` over `+1,631` in the S6-L1 table cell, and «التكاليف» dropped between parts of `P10 / P50 / P90` in the benefits-to-cost header. So:
- Inside a run, the spaces around ` / ` and around a spaced `–` are no-break spaces (U+00A0), and in the rendered HTML every isolate sits in `<span class="nr">` with `white-space: nowrap`. The run moves to the next line as one piece.
- A parenthetical that holds nothing but a run sits inside the isolate with its parentheses: `⁦(P10 / P50 / P90)⁩`, not `(⁦P10 / P50 / P90⁩)`.
- In a table header the Arabic words stay outside the isolate and only the label triple is inside, so «التكاليف» cannot split it.
- Every footnote reference in running text, `[^S-…]`, is its own isolate placed directly after the number, id or word it cites (`الكتاب الأخضر 2026⁦[^S-cp1-060]⁩`), so the year stays immediately after «الكتاب الأخضر» and the marker follows it, in any renderer. Footnote definitions (`[^S-…]:` at the start of a line) are left alone.

`isolate_numeric_runs` does all of this. It first removes existing LRI/PDI marks and then sets them again, so the result is canonical, and running it twice changes nothing. The no-break spaces are transparent to the bilingual check (`common.sources` treats U+00A0 like a space). `common.ar_render bidi-probe` measures the page at 900 px and at the narrow widths 480 and 360 px. A run that wraps counts as out of order, and a footnote marker must sit on its number's line, on the reading-order side. FIX_R8_RTL went from 8 / 14 / 15 failing runs to 0 / 0 / 0, with 0 of 5 markers misplaced at every width (`docs/status/main.md`).
