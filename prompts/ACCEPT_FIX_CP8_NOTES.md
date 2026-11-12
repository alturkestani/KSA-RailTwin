> **Document version:** prompts/ACCEPT_FIX_CP8_NOTES.md v1.0 | 7 Nov 2026 | Author: Tariq (verbatim; header and a short coordinator addendum added) | Status: active

# ACCEPT_FIX_CP8_NOTES — Tariq accepts FIX_CP8_NOTES on 7 Nov 2026 (AST) after independent coordinator review of e97eaba.

This accepts the notes-fix and the written CP8 plan below. It is NOT approval to start half 2, render, assemble, download models, call paid TTS, merge to main, fast-forward, push, tag, add a remote, or contact anyone.

Work on the existing branch r10 / worktree r10, from current HEAD e97eaba (or later only if it is this bookkeeping). One short run, Opus, USD 60 guard. Do not create a new worktree. Save this prompt as prompts/ACCEPT_FIX_CP8_NOTES.md with a version header.

RECORD
- FIX_CP8_NOTES is accepted with the notes below.
- Written CP8 plan accepted: scripts and storyboard as they now stand; dialect recommendation (educated white Saudi leaning Najdi for every narrator; MSA only for verbatim official quotes; Hijazi second choice); voice hierarchy (Nabrah public voices Daniah, Norah and Abdullah first, once Tariq sets the keys; Chatterbox built-in voice as the clean-licence fallback; NAMAA and Nabra-Saudi-82M allowed under MIT / Apache-2.0 even if the training corpus is unnamed; not automatic replacements).
- The Chatterbox clone from the ClArTTS reference clip ch_02_arabic_tts_dataset_417 (a real LibriVox reader) is NOT cleared. Do not use it. If the CP8 voice comparison table still marks that variant commercial-use Y, correct it to unresolved / not cleared without written consent. The no-cloning rule stands.
- Native review remains pending on every Arabic row. Contact no one.
- Half 2 remains unstarted. Disk gate still ≥ 50 GiB (about 23.3 GiB free). Do not render.
- Do not merge to main in this run. Integration waits for a separate ask. It will have to be a merge, not a fast-forward: main has three commits r10 lacks (ed419ce prompt; cda7a23 and a345f28 cost rows); merge-base is e9e0433.

NOTES TO RECORD (non-blocking; do not open a new study)
- Diffstat vs 6cec58f is 22 files, +705/−139 (not +704/−139).
- docver 389 files; manifest 388 rows (do not collapse both to 388).
- PNG-cache planning assumes the longest shot is 19.2 s and ignores the 20 s credits; correcting that is about 8.8 / 19.2 / 60.6 GB. Optional to note; do not render.
- English narration plus credits is 708.8 s (11:49). More than about 11.2 s of extra breathing room would pass 12 minutes; do not write that "any" breathing room would.
- S-r10-013 claim column still says "Jeddah to Abha nonstop block time" while the locator and card are Abha → Jeddah, valid to 28 March 2026. Optional register cleanup later; do not invent a forward-direction time.
- Arabic m-08-06 second clause elides a repeated «يقدّر»; meaning is clear; leave wording polish for the native reviewer.

Update docs/status/r10.md and docs/status/cp8-package.md. Closing line: R10: CP8 plan accepted - half 2 not started (disk gate and explicit launch required). Do not start INTEGRATE_R10.

Stop when the status files record the above, the ClArTTS comparison-table correction is done if it was still marked Y, and the tree is clean.

Coordinator addendum (7 Nov 2026): the launcher reads this file from the main checkout's `prompts/` (committed there as coordinator bookkeeping); copy it byte-identical into the worktree as `prompts/ACCEPT_FIX_CP8_NOTES.md` and commit it on `r10` first. The launcher ends the run on an `ACCEPT_FIX_CP8_NOTES: done` (or `ACCEPT_FIX_CP8_NOTES: blocked - <reason>`) line inside `docs/status/r10.md`: put it at the end of your ACCEPT_FIX_CP8_NOTES block, and make Tariq's new closing line `R10: CP8 plan accepted - half 2 not started (disk gate and explicit launch required)` the file's last line (replacing `R10: blocked - CP8 approval required`). If a test or checker asserts the old closing line, update that assertion to the new line; the half-2 gates (`film.gate`, and the exit-2 guards on `voice`, `render`, `assemble`) must stay closed — they key on an explicit half-2 launch record, never on this acceptance. Apply the ClArTTS correction wherever that variant is graded (the CP8 package §4 table, `film/voice/README.md`, `film/voice/scores.csv` if it carries the column, `film/rights_log.csv` and `film/licences-r10.csv`): commercial use "unresolved / not cleared without written consent", status rejected for use, same reason text in each. Record the six notes verbatim in the CP8 package (bump to v1.3) and correct the diffstat and docver/manifest figures where the status files state them. No verifier re-run is required for bookkeeping; run `make test` and docver, and state the counts. Do not kill any process you did not start (dashboard on 8765 and anything on 8000 are not yours; this run needs no server).
