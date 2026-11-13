> **Document version:** prompts/FIX_SOCIAL_CARDS.md v1.0 | 13 Nov 2026 | Author: Tariq (verbatim; header and a short coordinator addendum added) | Status: active

# FIX_SOCIAL_CARDS — Tariq approves FIX_SOCIAL_CARDS (13 Nov 2026 AST). Private main, no paid APIs, no push. Guard 15.

Text-only edits in docs/publish/social-cards.csv, then re-render the 10 cards in place:
1. Card 1 EN title: "One connected network" (drop ", in the model"). AR title: «شبكة واحدة مترابطة» (fix وحدة, drop «في النموذج»).
2. Card 1 AR note: «للمقارنة، وليست توصية».
3. Card 4 EN: "Fastest train = 4 h 57 min" (drop "in the model"); AR: «أسرع قطار = 4 ساعات و57 دقيقة».
4. Keep the one "synthetic demand, uncalibrated" line above the footer as is; no other wording, number, layout or source changes.
Update the social-cards.md trace only where text changed. Then run VERIFY_SOCIAL_CARDS as a full pass after the status line is written, so the recorded verdict covers criterion 9. Cost row as usual. Status ends "FIX_SOCIAL_CARDS: done" or "blocked - <reason>".

Coordinator addendum (13 Nov 2026): one short run on the MAIN checkout (`WT=0`; status block in `docs/status/main.md`); start from 8ccc6e9. Order: edit the CSV rows named above (the file that `film/social_cards` or its equivalent reads; if the text lives elsewhere, say where and edit that), re-render the ten PNGs in place on the external volume, re-run the existing card tests (jargon, word count), write the FIX_SOCIAL_CARDS status block with the before/after of each edited string and the new PNG SHA-256s, end it with the plain start-of-line `FIX_SOCIAL_CARDS: done`, commit, and only then run the red-team verifier with label VERIFY_SOCIAL_CARDS as a full pass over the ten re-rendered cards (all nine criteria, including the close line of the SOCIAL_CARDS block and of this one), appended as "pass 2" in `docs/status/verify-SOCIAL_CARDS.md` with a `VERIFY_SOCIAL_CARDS: PASS|FAIL` line; if it FAILs, change the status line to `FIX_SOCIAL_CARDS: blocked - <reason>` and stop. The eight unchanged cards' PNGs may differ byte-wise after the re-render only if the renderer is not deterministic — report which files changed and why; no number, layout or source changes. No paid calls; runaway guard USD 15. Contact no one; do not kill any process you did not start; no remote, no push.
