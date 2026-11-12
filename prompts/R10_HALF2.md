> **Document version:** prompts/R10_HALF2.md v1.0 | 7 Nov 2026 | Author: Tariq (verbatim, including his coordinator addendum; header and a short pre-flight note added by the coordinator) | Status: active

# R10 half 2 — approved by Tariq on 7 Nov 2026 (AST). He connected a writable external volume at /Volumes/Extreme_SSD (about 931 GiB free), created /Volumes/Extreme_SSD/Projects, and asked to create /Volumes/Extreme_SSD/Projects/KSA-RailTwin and work on the movie there. He also said the Nabrah and ElevenLabs keys are in ~/Documents/Projects/KSA-RailTwin/.env, and that older worktrees not needed for the documentary may be moved onto the external drive. The written CP8 plan was already accepted at 3a002a6 (status closing line: "R10: CP8 plan accepted - half 2 not started (disk gate and explicit launch required)"). This prompt is the explicit half-2 launch.

Work from the existing r10 worktree on branch r10 at 3a002a6713b73ea5b6e4f1e8c7207479280870ba (or that commit plus later r10 film/half-2 work from this run). Expected describe: r9-28-g3a002a6. If HEAD has other unreviewed work that is not this run, stop and report. One run, Opus, verifier inside. STOP at CP9. Do not merge, do not fast-forward, do not push, do not tag, do not add a remote, do not create accounts, do not commit keys, do not contact anyone.

Follow prompts/R10.md Half 2 (items 7–11) and this file where they differ; this file wins. Do not change official published S1 / L1–L6 / R8 figures, runs/r6/top5/, runs/r7/, runs/cba/, licences, or the frozen trip rates.

COORDINATOR ADDENDUM (7 Nov 2026; applies on top of prompts/R10.md Half 2)

1. Runaway guard for this run: USD 200, not the default 60. The combined paid-TTS cap of USD 60 (alert at 48) is a separate limit and stands. Paid TTS used so far: USD 0. Write your own estimate in the first status line.

2. Launch mechanics: save this prompt verbatim with a version header as prompts/R10_HALF2.md on main (run_track.sh reads $ROOT/prompts/<LABEL>.md from the main checkout), and copy the same file into the r10 worktree. Start with `MODEL=claude-opus-5-5 RUN_GUARD_USD=200 ./run_track.sh r10 R10_HALF2` from ~/Documents/Projects/KSA-RailTwin. Do not use orchestrate.sh (it only knows r3–r9; that also means nothing can auto-start INTEGRATE_R10). Status file docs/status/r10.md. End signals: a line `R10_HALF2: done` (or `R10_HALF2: blocked - …` if you must stop short) and, when half-2 production finished, the last line exactly `R10: blocked - CP9 review required`. Do not write `R10: done`.

3. The git repo and r10 worktree stay on the internal disk. Do not copy or move the repo, .venv, main checkout, or the r10 worktree onto the external drive. Do not kill any process you did not start (a dashboard may already be on 8765; anything on port 8000 is not yours). Set RAILTWIN_RUNS_ROOT to the main checkout's runs directory so run: sources resolve.

KEYS (do this without printing any secret)

- Load environment variables from the main-checkout file ~/Documents/Projects/KSA-RailTwin/.env only. It is gitignored, mode 600, and contains NABRAH_API_KEY and ELEVENLABS_API_KEY. The r10 worktree has no .env of its own.
- Source it privately in the processes that call TTS (for example set -a; source that path; set +a, or python-dotenv). Never echo, log, commit, or write the values. Never copy .env onto the external drive, into status files, into prompts, or into the r10 worktree.
- Because the keys are present: use Nabrah public voices Daniah, Norah and Abdullah as the primary film voices, across both language cuts as in prompts/R10_LAUNCH.md (one guide, one history/existing network, one method and numbers). Attribute Nabrah on published audio (Tariq, 7 Nov 2026, FIX_LICENCE_CITE_FACTS).
- Paid A/B versus ElevenLabs versus open is already approved (31 Oct 2026) within the USD 60 combined cap, alert at USD 48. Do a sample A/B on representative lines, not a second full-film render in every engine, unless the remaining cap clearly allows it. Nabrah is the master track. Record cost after each paid call and stop paid TTS if you would pass USD 48 without a recorded note, or USD 60 at all.
- If a key is missing or a paid call fails, fall back to Chatterbox built-in and report the failure without exposing the key. NAMAA and Nabra-Saudi-82M remain allowed, not automatic replacements.
- Never use chatterbox-mtl-clartts or namaa-saudi-clartts, or any other clone of ClArTTS clip ch_02_arabic_tts_dataset_417. Coqui XTTS-v2 stays out. Do not create new vendor accounts.

OLDER WORKTREES (Tariq, 7 Nov 2026: move ones not needed for the documentary onto the external drive)

Narrow exception to prompts/_common.md: you may run `git worktree move` only as specified here. Do not `git worktree add`. Do not move or delete the main checkout or .worktrees/r10. Do not `git checkout`, merge, rebase, push or tag.

- Destination: /Volumes/Extreme_SSD/Projects/KSA-RailTwin/archive/worktrees/<name> — keep this separate from renders/, audio/ and cache/.
- Keep on the internal disk: ~/Documents/Projects/KSA-RailTwin (main) and .worktrees/r10.
- Move these, which the documentary does not need (sizes as of 7 Nov 2026):
  - all 13 pilot-* worktrees (~529–535 MB each): pilot-al_baha, pilot-al_jouf, pilot-asir, pilot-eastern, pilot-hail, pilot-jazan, pilot-madinah, pilot-makkah, pilot-najran, pilot-northern_borders, pilot-qassim, pilot-riyadh, pilot-tabuk
  - r1a (~3.7 GB), r1b (~932 MB), r1c (~555 MB), r1d (~550 MB)
  - all 13 r2-* worktrees (~619–660 MB each): r2-al_baha, r2-al_jouf, r2-asir, r2-eastern, r2-hail, r2-jazan, r2-madinah, r2-makkah, r2-najran, r2-northern_borders, r2-qassim, r2-riyadh, r2-tabuk
  - r3 (~5.7 GB), r4 (~7.8 GB), r5 (~8.3 GB)
- Also move r6 (~9.3 GB), r6v3 (~10 GB), r7 (~6.0 GB) and r8 (~11 GB) only if that worktree is clean AND the film's run: citations already resolve from the main checkout's runs/ via RAILTWIN_RUNS_ROOT. If a tree is dirty, or is the only copy of a run the storyboard cites, leave it and report.
- Method: create the archive directory; for each candidate, check `git status --short` in that worktree; if dirty, skip and report; then from the main checkout run `git worktree move <old-path> <dest-path>`. After the batch, run `git worktree list` and record internal and external `df`. If a move fails, stop that tree and report; do not rm -rf it. Do not copy .env with any worktree. Leave the drive's "Install Security for …" installer files untouched.
- Do this after the film output folders exist and before large model downloads, so internal disk is freed first.

EXTERNAL OUTPUT (do this before unlocking any half-2 command)

The internal disk had about 26 GiB free and fails the ≥ 50 GiB render gate if renders land in the worktree. /Volumes/Extreme_SSD is ExFAT, writable, about 931 GiB free.

There is no FILM_ or RENDER_ environment variable and no --output flag that redirects bulky output. film/shots.py requires every shot output path to start with film/renders/. film/README.md documents film/audio/ and film/renders/ as gitignored half-2 outputs. So:

- Confirm /Volumes/Extreme_SSD is mounted and writable. If it is missing or read-only, stop and report.
- Create /Volumes/Extreme_SSD/Projects/KSA-RailTwin/{renders,audio,cache,models,assemble,tmp,archive/worktrees}. Projects already exists and is empty. Leave every other file on the drive untouched, including the installer files.
- Write a short README.txt in that folder stating it holds bulky film output and archived worktrees only; the git repo remains at ~/Documents/Projects/KSA-RailTwin.
- From the r10 worktree (APFS), create Unix symlinks. Do not create the symlinks on the ExFAT volume itself (ExFAT does not host Unix symlinks):
  - film/renders does not exist: point it at /Volumes/Extreme_SSD/Projects/KSA-RailTwin/renders
  - film/audio already exists (gitignored tests, about 22 MB). Copy it with rsync -a onto /Volumes/Extreme_SSD/Projects/KSA-RailTwin/audio/, verify the copy, then replace film/audio with a symlink to that external audio directory. Do not lose film/audio/tests.
- After the symlinks exist, run git check-ignore and git status. A symlink may not match a trailing-slash gitignore rule. If either symlink would be committed, update .gitignore so film/audio and film/renders are ignored without committing the symlink.
- Point model and Hugging Face caches for this run at /Volumes/Extreme_SSD/Projects/KSA-RailTwin/cache (HF_HOME, HUGGINGFACE_HUB_CACHE, TORCH_HOME as needed). Do not download multi-GB models onto the internal disk or into ~/.cache if you can redirect them.
- Leave /tmp/r10-voice in place (about 2.4 GB); do not delete it. New production audio goes under film/audio via the symlink.

DISK GATE (overrides the old "df -h ~" wording for this run)

- Before any model download, paid-TTS call, render or assemble: confirm the external volume is still mounted.
- The ≥ 50 GiB render gate applies to the output volume (/Volumes/Extreme_SSD), not to ~. It currently passes.
- Also check the internal disk that holds ~. Estimate the size of the next download or write. Stop that step if either volume would fall under 10 GB free.
- Record the df figures and the estimates.

GATE CODE

film/gate.py refuse() currently prints "R10 half 2 only: needs Tariq's recorded CP8 approval in docs/STATUS.md; nothing rendered" and exits 2 unconditionally. film.voice speak, film.render shot, film.render all, film.assemble all, film.assemble cut and film.subs build all call it.

After the external output is in place and verified, replace the unconditional refuse with real checks: this half-2 launch is recorded; film/renders and film/audio resolve onto /Volumes/Extreme_SSD/Projects/KSA-RailTwin; the output volume has ≥ 50 GiB free; the next write would not take either volume under 10 GB; the drive is still mounted. Record a dated launch note in docs/status/r10.md and a short note in docs/STATUS.md (the original R10 text named that file). Do not open the commands before the symlinks exist. Update any tests that expected a permanent stub so they test the new checks. Do not treat acceptance text alone as permission to write media onto the internal disk.

VOICE

- One WAV per line; timing table; two-pass loudnorm to -16 LUFS integrated / -1.5 dBTP true peak; record measured values.
- Tempo/pause adjustments only as registered assumptions. Native review is still pending on all 74 Arabic rows: do not mark native_review done, and do not contact a reviewer. Produce draft narration from the accepted scripts; it can be replaced after review.

RENDERS, SUBTITLES AND ASSEMBLY (1080p)

Implement film.voice, film.render shot|all, film.assemble all|cut and film.subs build for real.

- Picture from the twin's own outputs: deck.gl or kepler.gl captures, Manim or Remotion (check Remotion's licence and record it), Blender optional. Open Arabic fonts. Archival imagery only when public domain or licensed and logged in film/rights_log.csv. Any AI-generated footage must be minimal and labelled on screen. Do not invent Saudi places, stations, trains, deserts or people. No SAR, PIF or other entity logos.
- Do not sign up to, pay for, or send study maps or any project data to Higgsfield, Seedance, Claude Motion, or any other new paid video API or footage generator. Claude has no video-generation model; do not treat Claude Motion as one. A new paid model or API needs Tariq's approval with a cost estimate before first use.
- OSM credit on every map; keep the Copernicus extra credits already on sh-01-05, sh-01-07 and sh-01-51; keep the synthetic / not-official footers as in the accepted storyboard.
- Render every shot at 1080p30. 4K only if the 1080p cuts and trailers are already done and time remains; do not start 4K if it risks leaving 1080p unfinished.
- Subtitles: SRT and VTT per language for both main cuts and both trailers from lines.csv (never retyped); RTL/bidi QA screenshots from two players into film/subs/qa/; film.subs check and align-qa pass.
- Assemble MP4 1080p for main AR, main EN, trailer AR and trailer EN; mov_text subtitle tracks; credits from docs/credits.md and film/rights_log.csv (Nabrah if used, plus Claude and KSA Rail Twin); the synthetic label on screen where modelled results appear; script PDFs with citations per language.
- Music bed only from CC/royalty-free tracks with licences checked (avoid NC/ND) and logged. If no cleared track can be obtained without a new paid account, ship without a music bed rather than using uncleared music. Do not scrape YouTube.

SCRIPTS AND FIGURES

Do not rewrite the accepted scripts or change their meaning. If measured audio length forces shot-duration updates, use the existing storyboard tools and tests so durations still match covered English lines. Do not change the wording of m-08-06 or the other FIX_CP8_NOTES corrections. Optional leftover notes (voice README double pipe, package §4 grouping both NAMAA voices, package §5 saying 49/13/2 vs rights-log 48/14/2, S-r10-013 claim column) may be fixed if you touch those files; do not start a separate study for them.

Every narrated number still traces to a sourced register row or scored output. Transit Costs Project hard stop stands. This is a research film, not a promo and not a ministry, SAR or PIF film. Extra-travel lines still need both labels ("synthetic demand, uncalibrated: scenario comparison, not a forecast" and "not the official ranking").

VERIFICATION AND STOP

- make test (including updated film tests for the new gate and the new commands).
- red-team-verifier audits the final script, the on-screen figures and the rights log.
- Write docs/film.md (it does not exist yet) with outputs (external paths and the worktree symlinks), durations, loudness, subtitle check results, rights-log completeness, disk figures, which voice engine was actually used, paid-TTS spend, which worktrees were moved, and native review status (still pending; no reviewer contacted).
- Update film/README.md so it documents the external output layout and the new gate checks.
- Status block in docs/status/r10.md pointing at those outputs.
- Then write `R10_HALF2: done` and, last, `R10: blocked - CP9 review required`. The coordinator writes `R10: done` only after recorded CP9 approval.

Save this prompt verbatim with a version header as prompts/R10_HALF2.md.

Coordinator pre-flight note (7 Nov 2026, before launch): r10 at 3a002a6 = r9-28-g3a002a6, clean; main at 78e765b, clean; no builder running; 39 worktrees listed; internal disk 26 GiB free; /Volumes/Extreme_SSD mounted (931 GiB free). The launcher does not source `.env` and the coordinator never reads it: the builder loads it as described under KEYS, inside its own TTS processes only. If a Finder or macOS "access files on a removable volume" prompt blocks the first read of /Volumes/Extreme_SSD, stop and report `R10_HALF2: blocked - removable-volume permission` rather than waiting on it or working around it. In the worktree copy of `prompts/R10.md`, add a one-line pointer to this file above the Half 2 list (bump to v1.2); the main checkout's `prompts/R10.md` is the coordinator's to update.
