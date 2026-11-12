> **Document version:** prompts/R9_LAUNCH.md v1.2 | 12 Nov 2026 | Author: Tariq (verbatim; header added by the coordinator); PUBLISH_PREP (v1.1: two third-party email addresses redacted, nothing else changed); PUBLISH_EXPORT (v1.2: the vendor executive's name replaced by company and role, Tariq's answer Q4; nothing else changed) | Status: active

# R9 — approved by Tariq, 7 Nov 2026 (AST). One run on main, Opus, USD 60 guard, verifier inside, then stop. No tag, no push, no remote, no Pages, no GitHub issue, no R10, no paid model (R9 does not need one). Save this prompt verbatim with a version header as prompts/R9_LAUNCH.md; leave the task list in prompts/R9.md intact and follow it.

Follow prompts/R9.md (release preparation). The author publishes; nothing here pushes or contacts anyone.

Coordinator addendum (7 Nov 2026):

1. Arabic executive summary. Tariq asked the coordinator to review docs/executive-summary.ar.md. The review (7 Nov 2026): the body is sound formal MSA; it follows docs/glossary.ar.md (including إيرادات التذاكر / تعرفة تذاكر الركاب, not أجور; صافي القيمة الحالية الصامد; طلب تركيبي غير مُعايَر; بديل التغطية الأوسع); the figures match docs/executive-summary.en.md digit for digit; the earlier RTL wrap issues were already fixed. Do not rewrite the body. Update only the draft/CP6 banners in both executive-summary.ar.md and executive-summary.en.md: record that the Arabic summary was reviewed on Tariq's request on 7 Nov 2026 and is signed off for internal use; drop "Draft for review at checkpoint CP6; not for circulation" and the matching Arabic CP6-only sentence, since CP6 has passed. Keep the synthetic/uncalibrated labels and "في النموذج" / "in the model". Change the status headers so they are no longer "draft, pending native review". Do not treat this as a public-release decision.

2. Nabrah licence row only. Nabrah.ai's CEO ([name replaced by company and role for publication], [email address redacted for publication], cc [email address redacted for publication]) confirmed in writing on 1 Nov 2026 at 09:38 AST that audio generated with Nabrah Studio public voices (including Daniah, Norah and Abdullah) on a paid plan may be used commercially, published publicly online (YouTube and social platforms), and screened or broadcast. Record that on the Nabrah TTS row: publication and broadcast cleared for those public voices on a paid plan; attribution still unanswered; training opt-out is Enterprise-only; no voice cloning of any real person without written consent. Do not clear any other blocker. Transit Costs Project remains a hard stop: do not use or cite it.

3. Do not start R10, do not write film/script, do not download TTS or render models. Disk free is about 28 GB (checked 7 Nov 2026); the R10 render gate is ≥ 50 GB.

4. STUDY_RJ_SCORE and the RJ study stay beside the study. Do not fold them into R8, top5, SWITCHER or the recommended programme. Credits and README may mention that a Riyadh–Jeddah routing study exists beside the main report, without publishing unscored claims as programme results.

5. Do not kill any process you did not start.

Verifier PASS, then stop with R9: done or R9: blocked - <reason>.

Coordinator notes (7 Nov 2026, added below Tariq's text): the run is launched with label `R9` on `main` (`WT=0`), so `prompts/R9.md` is the prompt body and this file is the approval and addendum it points to; R9.md task 5's "set the version and tag (`r9` by the coordinator)" is a checklist item for Tariq's release checklist, not an action in this run (no tag now); the Arabic banner edit keeps `docs/glossary.ar.md` typography (numeric runs isolated) and the bilingual check must still pass; the Nabrah row edit touches `docs/licences.csv`/`.md` and `docs/licences-release.md`/`docs/licences-blockers.md` only for that one row (status text and the written-confirmation source row with date and sender; no email content beyond that), every other BLOCKER row unchanged; the coordinator's dashboard on port 8765 and anything on port 8000 are not yours; the clean-clone check (task 6) clones locally under /tmp only.
