> **Document version:** prompts/BUILD_MOVIE.md v1.0 | 10 Nov 2026 | Author: Tariq (verbatim; header and a short coordinator addendum added) | Status: active

# BUILD_MOVIE (Tariq 10 Nov 2026; replaces the REBUILD_MAIN paste, which was never launched). Save as prompts/BUILD_MOVIE.md on main, then launch from the main checkout:
MODEL=claude-opus-5-5 RUN_GUARD_USD=200 RAILTWIN_RUNS_ROOT=~/Documents/Projects/KSA-RailTwin/runs ./run_track.sh r10 BUILD_MOVIE
Do not start a second run_track on r10 while one is live.

Goal: build the full documentary (main-en and main-ar, 59 shots each) in the accepted trailer style. The trailers are accepted as they are; do not touch or re-render them.
- Pictures: film/sim.py sim_map for every shot, one full-sentence caption per shot, legend and OSM/Copernicus credits on every frame. Treat the existing card-style main files as drafts; keep each one until its replacement exists (.new.mp4 then rename).
- English: ElevenLabs George (JBFqnCBsd6RMkjVDRZzb, eleven_multilingual_v2) for every English line.
- Arabic: Nabrah Daniah/Norah/Abdullah.
- One closing notice on each cut's last shot + credits only; no "in the model" / «في النموذج» / "uncalibrated" refrain elsewhere. m-08-06 stays byte-identical. Loudnorm -16 LUFS / -1.5 dBTP, two-pass, measured.

Arabic pronunciation (Tariq's priority):
1. Bare text has caused mispronunciation, e.g. «يكبر» read as «تكبُّر» (arrogance) instead of "growing".
2. First, rewrite ambiguous words in clear, plain Saudi Arabic where a clearer word exists. Tariq's example: «والبلد يكبر» -> «بلد يزداد فيه عدد السكان». Apply this to m-03-01 and m-03-08, and scan all 62 main Arabic lines for other words whose meaning changes with the vowels. Rewording must not change any digit, name, source or claim. Log every change before/after in film/storyboard/ar-rewords.csv and in the r10 status block.
3. Then write full tashkeel into speech_text for all 62 main Arabic lines (currently none have it). Leave nothing ambiguous unvocalised. The only allowed exceptions are digits and words proven to read worse when vocalised (مليون / مليار / مجدول); list each exception.
4. film.script validate must still prove speech_text strips back to text. Read back every Arabic line with ASR; flag any line with CER > 0.10 or any word that comes back with the wrong meaning; fix and re-synthesise only those lines. Report the list.
5. Changed rows get native_review = pending. Contact no one.

ElevenLabs: before any English synthesis, check the remaining characters. English main is about 9,608 characters and the free tier had about 8,950 left. If it cannot cover every English line, build the Arabic cut fully, synthesise no English, and stop with "BUILD_MOVIE: blocked - ElevenLabs quota / paid plan needed" and last line "R10: blocked - ElevenLabs paid plan needed before English narration". Never mix voices or fall back to Nabrah for English.

Spend: paid TTS (Nabrah + ElevenLabs) cap USD 60 combined, alert at USD 48; post the tally first and after every batch. Keys only from the main checkout's gitignored .env inside TTS processes; never print, log, copy or commit them. Disk gate: stop if either volume would go under 10 GB. No new paid model or API, no merge, tag, push or remote.

Done: "BUILD_MOVIE: done" as a plain start-of-line in docs/status/r10.md, last line "R10: blocked - CP9 review required". Report: commits, cost, paid-TTS total, both cut durations and loudness, the reworded lines, the tashkeel exceptions, and the read-back flags.

Coordinator addendum (10 Nov 2026): start from r10 HEAD bcbabe6 (FIX_HALF2_QUALITY done, tree clean); the launcher reads this file from the main checkout's `prompts/`, so copy it byte-identical into the worktree as `prompts/BUILD_MOVIE.md` and commit it on `r10` first. The main script and storyboard already carry the refrain edit from FIX_HALF2_QUALITY; main audio and picture do not. Paid TTS to date: USD 2.19 of 60 (Nabrah 2.19 list-equivalent; ElevenLabs 0, 1,050 of 10,000 free characters used as of 8 Nov) — re-measure before the first call. The main cuts on disk (`out/ksa-rail-twin-main-{ar,en}.mp4`, 8 Nov 02:01) are the rejected card versions: overwrite each only after its replacement exists. The ElevenLabs free-tier caveat (non-commercial only) stands and is recorded; it does not block this build. The ASR read-back for item 4 uses the open model already registered for read-back (no new download onto the internal disk; caches stay on the SSD). The ElevenLabs-quota stop in the prompt counts as a legitimate blocked end for the launcher (`BUILD_MOVIE: blocked - …`), not a failure. Verifier: red-team-verifier label VERIFY_BUILD_MOVIE in the foreground on the final cuts (every shot sim_map; every on-screen figure in a sentence and traceable; single closing notice; m-08-06 byte-identical; ar-rewords.csv changes alter no digit/name/claim; speech_text strips back; loudness measured; paid-TTS tally; trailers untouched by SHA-256 — en 07b52f6556115c01…, ar 21df620d1994ec75…). Update `docs/film.md` (bump) with the main-cut outputs. Do not kill any process you did not start (dashboard on 8765 and anything on 8000 are not yours).
