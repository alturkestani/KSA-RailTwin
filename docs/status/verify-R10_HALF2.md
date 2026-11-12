> **Document version:** docs/status/verify-R10_HALF2.md v1.1 | 8 Nov 2026 | Author: red-team-verifier (`claude-fable-5-1`; v1.1: second pass after the builder's F1/F2 fixes at 62407e1) | Status: verified (verdict below)

# Verify R10_HALF2: half-2 production (narration, renders, subtitles, assembly), stop at CP9

Worktree `.worktrees/r10`, branch `r10`, HEAD 4a05318 (`r9-37-g4a05318`, clean). Read-only audit; nothing fixed, no `film.voice speak`, `render` or `assemble` run; `RAILTWIN_RUNS_ROOT` set to the main checkout's `runs/`. `.env` not read.

## 1. Commands run

| command | result |
|---|---|
| `make test` (ruff, ruff format, pytest, docver, manifest) | exit 0 in 40.5 s; "All checks passed!"; pytest 0 failures (quiet mode); `docver OK: 393 files`; `manifest OK: 388 rows` |
| `git diff 3a002a6 -- film/script/` | empty |
| `git diff 3a002a6 --stat` | 82 files, all under `film/`, `docs/film.md`, `docs/status/r10.md`, `docs/STATUS.md`, `docs/cost-log.*`, `prompts/R10.md`, `prompts/R10_HALF2.md`, `tests/test_film_*`, `scripts/film_*`, `cities/ksa/assumptions/film_voice.yaml`, `.gitignore` |
| `git check-ignore -v film/renders film/audio` | `.gitignore:11` / `:12` match; `git ls-files film/renders film/audio` empty |
| `uv run python -m film.rights check film/rights_log.csv` | PASS: 64 rows (candidate 31, rejected 14, test_only 6, used 13) |
| `uv run python -m film.subs check film/subs/` | PASS: 8 files, 792 cues, 538 warnings (all "reading speed < 12 cps") |
| `film.subs align-qa` ×4 | main-ar PASS 0 warn; main-en PASS 2 warn (m-02-04 0.124, m-06-04 0.108); trailer-ar PASS 1 (t-07 0.220); trailer-en PASS 1 (t-02 0.110) |
| `ffprobe` on the four MP4s | 880.933 / 817.133 / 88.533 / 84.500 s; H.264 1920×1080 30 fps; AAC 48 kHz mono (138–153 kb/s measured); one `mov_text` track tagged `ara`/`eng` |
| `ffmpeg loudnorm` measurement | main-ar: I −16.04 LUFS, TP −1.55 dBTP, LRA 4.0; trailer-en: −16.06 / −1.78 / 5.1 (both equal `film/assemble/loudness.csv`) |
| shot MP4 vs EDL durations (ffprobe over 140 shot files) | worst difference 0.000 s; EDL sums 817.13 / 880.93 / 84.5 / 88.53 s |
| secrets grep (sk-/sk_/hf_/AKIA/Bearer/key= patterns) and `grep -rn "/Users/[a-z]"` over `git ls-files` | both empty |
| `git worktree list` | 39 entries, all under `.worktrees/`; `/Volumes/Extreme_SSD/Projects/KSA-RailTwin/archive/worktrees/` empty |

## 2. Criteria

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1 | `make test` passes | PASS | §1; `/tmp/verify-r10h2/make-test.log`, `exit=0` |
| 2 | Gate real, called by every half-2 command, tested; symlinks and ignore rules; no media committed except `film/subs/qa` | PASS | `film/gate.py` `evaluate()` checks launch line (`LAUNCH_MARKER` present at `docs/status/r10.md:118`), `os.path.ismount`, both symlinks resolve inside `EXTERNAL_ROOT`, `RENDER_GATE_BYTES = 50 GiB`, `FLOOR_BYTES = 10 GB` on both volumes. `require()` called in `voice.py:282`, `render.py:958,976,979`, `assemble.py:208,221`, `subs.py:407`. `tests/test_film_gates.py`: 6 CLI closed-gate cases + 6 unit cases (launch, symlinks, 50 GiB, 10 GB both volumes, unmounted). `film/renders -> /Volumes/Extreme_SSD/Projects/KSA-RailTwin/renders`, `film/audio -> …/audio`; ignored; the only new binaries tracked are 24 PNGs under `film/subs/qa/` |
| 3a | `lines.csv` and scripts unchanged since 3a002a6; m-08-06 and FIX_CP8_NOTES wording intact | PASS | `git diff 3a002a6 -- film/script/` empty; `lines.csv:57,120` carry the FIX_CP8_NOTES m-08-06 text; `tests/test_film_real.py::test_fix_cp8_notes_wording` passes |
| 3b | `say.csv` changes only number forms, same values, both languages | PASS | 27 rows; `difflib` opcodes show only digit spans replaced. Checked by hand: 10,000 → عشرة آلاف / ten thousand; 32,175,224 → اثنين وثلاثين مليون ومية وخمسة وسبعين ألف وميتين وأربعة وعشرين; 93,693 → ثلاثة وتسعين ألف وستمية وثلاثة وتسعين; 109,007 → مية وتسعة آلاف وسبعة; 114.6 / 267.7 → مية وأربعة عشر فاصلة ستة / ميتين وسبعة وستين فاصلة سبعة; 1,250 → ألف وميتين وخمسين; 47,108; 4.25; 3.56; 0.18; 0.24; 61.9/91.4/16.2/14.8; all English number words correct. Note: m-08-07 (ar) inserts a comma «ستة، و» between the two numbers (pause only) |
| 3c | On-screen figures vs sources (13 shots) | PASS | see §3 |
| 3d | Footers, OSM, Copernicus on frames | PASS | manifests: `synthetic` on every modelled shot, `synthetic+not_official` on sh-01-03, 01-07, 04-02/03/06/07, 05-02/03, 06-03/04, 08-08/09/10/12, 01-51; OSM credit on all 33 map-bearing main shots; Copernicus on sh-01-04, 01-05, 01-07, 06-01, 06-03, 01-51, 06-51 (= rights-log list). Frames extracted from the delivered `main-en` MP4 at 63 s (sh-01-05: hillshade, OSM + Copernicus credit), 160 s (sh-02-06: OSM credit, six census figures), 680 s (sh-08-06: synthetic footer, basis caption), 755 s (sh-08-10: both labels, OSM credit) confirm the labels |
| 4 | Rights log complete and consistent; Nabrah caveat; no ClArTTS clone, no XTTS, no new account, no uncleared music; credits include Nabrah, Claude, KSA Rail Twin | **FAIL** | Register side is complete: 13 `used` rows cover Nabrah, Noto Naskh/Sans, Chrome, ffmpeg, OSM, alignment sidecars, Copernicus GLO-30, GASTAT, two LOC photographs, Whisper + mlx-whisper (QA only); Chatterbox V2 `test_only`, ElevenLabs `test_only`, ClArTTS clone and XTTS `rejected`, "Music: none chosen"; the Nabrah row records the paid-plan/trial caveat. Credits head lines name KSA Rail Twin, Nabrah and Claude (`render.py:665-667`, frame at 807 s / 872 s). **But the delivered credits card is wrong**: see F1 |
| 5 | Subtitles: check and align-qa pass; built from `lines.csv`; RTL QA screenshots from two players | **FAIL** | check/align-qa PASS (§1); every `main.ar.srt` block starts with U+200F; cue counts 177/184/19/16 match docs. **Chrome screenshots show no cue**: see F2 |
| 6 | Loudness −16 ±1 LUFS, ≤ −1.5 dBTP; one measured | PASS | `loudness.csv` final: −16.04/−1.55, −16.06/−1.77, −16.10/−1.84, −16.06/−1.78; my own loudnorm measurement of main-ar and trailer-en reproduces the table exactly |
| 7 | Durations match ffprobe; over-target runtime disclosed | PASS | 880.9 / 817.1 / 88.5 / 84.5 s and 58.9 / 56.8 / 6.5 / 6.0 MB match `docs/film.md` §1; §1 states both main cuts run over 12 minutes and lists options |
| 8 | Paid TTS logged, under USD 48; no key or home path tracked | PASS | `docs/cost-log.csv:79-90`: 11 Nabrah rows + 1 ElevenLabs row dated 2026-11-08, sum 0.12+0.00+0.08+0.07+0.74+0.45+0.46+0.01+0.01+0.00+0.07+0.03 = USD 2.04; `.md` has the same 12 rows; greps empty; no `.env` in the worktree |
| 9 | A-film-006..012 registered for every `film_voice.yaml` parameter | PASS | `film/assumptions-r10.md` v1.2 rows A-film-006 (roles), 007 (loudness incl. `aac_headroom_db`), 008 (gap 0.35), 009 (head 0.6), 010 (tail 0.8), 011 (USD/credit), 012 (CER thresholds); each YAML block carries `assumption:`. Note: A-film-012's 0.10/0.30 live as constants in `film/subs.py:192`, not in YAML |
| 10 | No worktree moved; failure reported honestly; native review pending; no reviewer contacted | PASS | 39 worktrees all on the internal disk; archive dir empty; `docs/status/r10.md:126` reports the `Cross-device link` rc 128 and the stop; `lines.csv`: 74 ar rows `pending`, 74 en rows `n/a`; `docs/film.md` §8 |
| 11 | Hard stops: no Transit Costs Project, no logos, no invented figures; frozen runs untouched | PASS | "Transit Costs" appears only in `film/script.py:71` (the validator's forbidden list); `shots.yaml:128` "No logo"; no logo asset in `film/render.py`; diffstat touches no `runs/`, `docs/report`, `docs/assumptions*`, `docs/licences*` or `cities/ksa/assumptions/*cba*` file |
| 12 | Claims in `docs/film.md` / status block | **FAIL** (see F1, F2) plus the minor errors in §4 | |

## 3. Spot-check of on-screen figures (13 shots; chosen by figure density, not random: no seed)

| shot | on-screen figure(s) | source checked | result |
|---|---|---|---|
| sh-01-04 | 11 tunnels, 32 bridges; Abha → Jeddah 1 h 15 min, expired schedule | `docs/sources/r10.csv` S-r10-014 (Arab News 2024-07-27: 11 tunnels; 32 bridges), S-r10-013 (1:15, validity to 2026-03-28) | PASS |
| sh-01-05 | 9.1 million visitors a year by 2030, Jan 2025 | S-r10-016 (Arab News 2025-01-27, Asir RDA CEO) | PASS |
| sh-02-06 | Taif 913k, Tabuk 624k, Khamis Mushait 601k, Abha 422k, Najran 422k, Jazan 201k, 150 governorates | `docs/coverage.md`: 913,374; 623,665; 601,305; 422,243; 421,902; 200,911; S-cp2-gastat-007 (150 governorates) | PASS |
| sh-02-08 | 26.10 of 35.93 million | `runs/r6/v3/national_reach.json`: S1 120 = 26,096,670; population_total_2025 = 35,927,621 | PASS |
| sh-03-01 | 32,175,224; 35.3 million mid-2024 | S-r10-023, S-r10-024 (GASTAT) | PASS |
| sh-05-04 | Dec 2025, 785 km, about 2 hours, announced | S-r10-028 (Arab News 2025-12-08) | PASS |
| sh-06-03 | 61.9 → 91.4 km, 16.2 tunnel, 14.8 viaduct | `runs/study/rj/legs-s1/legs.csv` RJ-B and RJ-C2 taif→wp-north: 61.85, 91.389, 16.2, 14.8 | PASS |
| sh-07-04 | 47,108 rows | `runs/r6/v3/results.tsv`: 47,108 data rows | PASS |
| sh-08-01 | NPV −337.6 / +11.6, middle −60.1 bn | `runs/cba/CBA-S1-committed-programme` via `docs/executive-summary.en.md:13`: −337,555 / −60,103 / 11,607 SAR m | PASS |
| sh-08-04 | 4.25 vs 3.56 million; −21.7 to −16.6 bn | `runs/r6/top5/top5.csv` L3: access_gain_120 4,246,882 vs 3,563,760; npv_p90cost −21,744.9 / −16,624.2 | PASS |
| sh-08-06 | 2.3–19.3; 0.6–7.4 bn | `results.json`: pv_user_time_cost P10 2313.14 / P90 19336.08; pv_safety 595.84 / 7444.50 | PASS |
| sh-08-07 | WEI 114.6–267.7 bn | `top5.csv` pv_wei_indicative_medium: 114,628 (L1), 142,741 (L2), 267,682 (L3) | PASS |
| sh-08-10 | 93,693; 109,007 | `runs/study/rj/score/replace-rj-c1/score.judge.json` access_gain_120 93693; `replace-rj-lb` 109007 | PASS |

Also checked: the render manifests (`film/assemble/renders-*.csv`) list `figures_not_found` empty on all 140 rows; the L1/L2 figures of sh-08-02/03 (0.8–5.3, 4.0–5.6; 6.2–41.3, −3.0/+1.6) match `top5.csv` capex_p10/p90 and npv_p90cost low/high.

## 4. Failures (exact evidence)

**F1 (criterion 4, 12): the delivered credits card is wrong and does not match the register or `docs/film.md`.** Frame extracted from `film/renders/out/ksa-rail-twin-main-en.mp4` at 807 s and from `…-main-ar.mp4` at 872 s (sh-08-14) shows, in both cuts:
- `Voice: Chatterbox Multilingual by Resemble AI (MIT)`: no Chatterbox audio is in any delivered file (`docs/film.md` §2; `film/voice/timing/*.csv` engine = nabrah on all 148 rows; rights log row `test_only`). The shot was rendered at 00:40 (en) / 00:49 (ar) on 8 Nov (`film/renders/main-en/frames/sh-08-14.O.html` mtime) while the rights log still carried Chatterbox as the fallback; the log was changed afterwards (fc5d2d4, 01:22) and sh-08-14 was not re-rendered before assembly. The current `credits_lines("en")` no longer emits that line, so the shipped MP4s and the code disagree.
- `attribute Nabrah on published audio (Tariq, 7 Nov 2026)` and `none for local use` are printed as credit lines: `render.py:683-688` prints the `attribution` column of every `used` row as the credit text and filters only the literal `none`/`n/a`. The first is an internal instruction with a person's name on a public-facing frame; the second is the ffmpeg row's "not required" note.
- Arabic card: `بُني باستخدام Claude ‏(Anthropic)` renders as `Anthropic)) Claude` and `‏(ODbL)؛` as `ODbL))` (bracket mirroring from the U+200F placed before the opening parenthesis: `render.py:676,678`).
- `docs/film.md` §6 ("Credits roll (sh-08-14): … and the attributions of the used rows") and the `render.py:638` docstring ("from docs/credits.md and film/rights_log.csv") do not describe the shipped frame; the code never reads `docs/credits.md` (the head lines are hard-coded).
Fix: make `credits_lines` emit a real attribution text (e.g. "Voices: Nabrah AI", "ffmpeg (LGPL)") instead of the raw `attribution` column, isolate LTR spans with `<bdi dir="ltr">`/U+200E instead of U+200F, re-render sh-08-14 for both languages, re-assemble both main cuts, re-measure loudness, and refresh sizes/SHA-256 in `docs/film.md` §1.

**F2 (criterion 5, 12): the "two players" RTL QA produced no Chrome rendering of any cue.** `film/subs/qa/*-cue001-chrome.png` are four byte-identical 4,250-byte files (MD5 cf347c3d…), each an all-black 1280×720 frame; `main-ar-cue008-chrome.png`, `main-ar-cue009-chrome.png`, `main-en-cue010-chrome.png`, `trailer-ar-cue003/005-chrome.png` show the video frame with no subtitle overlay, while the matching Firefox PNGs show the cue. `scripts/film_subs_qa.py:101-103` takes the Chrome screenshot with `--headless=new --virtual-time-budget=6000 --screenshot` and no wait for the `<track>` to load or the seek to complete. So the Blink column of the QA is empty, and `docs/film.md` §5 ("shown … in two players, Google Chrome (Blink) and Firefox (Gecko) … no reordering seen") and `docs/status/r10.md:136` ("RTL screenshots in Chrome and Firefox") overstate what was captured; the prompt's "RTL/bidi QA screenshots from two players" is met by one player only. Fix: make the Chrome capture wait for `track.readyState === 2` and the seek (or burn the VTT with ffmpeg/libass as the second renderer), regenerate the 12 Chrome PNGs, or else correct the two documents to say one player rendered cues.

## 5. Minor errors and notes (not blocking on their own; correct them)

1. `docs/status/r10.md:115` (first line of the R10_HALF2 block): "Paid TTS: USD 0 so far" while the block's results and the cost log say USD 2.04. The block header (`v1.4 | 7 Nov 2026 | … (in progress)`) also predates the 8 Nov content.
2. The closing lines `R10_HALF2: done` and, last, `R10: blocked - CP9 review required` are not yet in `docs/status/r10.md` at 4a05318 (`grep` empty). The prompt writes them after this verification; they must be appended, and `R10: done` must not be written.
3. `docs/film.md` §1: "AAC 48 kHz 192 kb/s" is the encoder request (`assemble.py:182` `-b:a 192k`); ffprobe reports 138–153 kb/s mono on the four files. Say "AAC 48 kHz mono, 192 kb/s requested (138–153 kb/s measured)".
4. `docs/cost-log.csv:84` note says "about 17,500 chars" before the HTTP 400; the logged rows sum to 1,440 + 945 + 845 + 9,016 + 5,458 = 17,704, and `docs/film.md` and the rights log say "about 17,700". Align to 17,700.
5. A-film-012 thresholds (0.10 / 0.30) are constants in `film/subs.py:192`, not in a YAML with `assumption:` (CLAUDE.md "no magic numbers in code"). Low priority.
6. Firefox QA frames show the subtitle cue overlapping the on-screen footer label at the bottom-left (e.g. `main-ar-cue008-firefox.png`, `trailer-ar-cue003-firefox.png`). Cosmetic; a `line:` position in the VTT or a lower footer would avoid it. For CP9.
7. Nabrah licence caveat (audio generated while the workspace looked like a free trial; S-nabrah-005 covers paid plans) is recorded consistently in the rights log, `docs/film.md` §2 and the status block, and no release is claimed. It stays an open item for Tariq, not a verifier FAIL.
8. The CP8 package's provisional voice roles were applied without a recorded CP9 decision (A-film-006, "pending native review"): correctly flagged as an assumption.

## 6. Three most important fixes

1. Re-render sh-08-14 (both languages) with corrected `credits_lines` (no Chatterbox line, real attribution texts, LTR isolation), re-assemble both main cuts, re-measure loudness, update `docs/film.md` §1 and §6 (F1).
2. Repair the Chrome subtitle capture (wait for the track and the seek) or substitute a second renderer that actually draws the cue; regenerate `film/subs/qa/*-chrome.png`; correct `docs/film.md` §5 and the status block (F2).
3. Correct the status-block paid-TTS line and header, the AAC bitrate wording, the 17,500 vs 17,700 note, then append `R10_HALF2: done` and `R10: blocked - CP9 review required` (§5 items 1–4).

First-pass verdict (8 Nov 2026, HEAD 4a05318): FAIL (F1, F2 open).

## 7. Second pass (8 Nov 2026, HEAD 62407e1 `fix(film): credits card from curated lines ...`, `git status --porcelain` clean)

Read-only again: no `film.voice speak`, `film.render`, `film.assemble` or `scripts/film_subs_qa.py` run; `.env` not read; `RAILTWIN_RUNS_ROOT=…/KSA-RailTwin/runs`. Scratch under `/tmp/verify-r10h2b/`.

### 7.1 Commands

| command | result |
|---|---|
| `make test` | exit 0 in 40.9 s; ruff + format clean; pytest 0 failures; `docver OK: 394 files` (393 + `scripts/film_subs_qa_chrome.mjs`'s companion docs); `manifest OK: 388 rows` (`/tmp/verify-r10h2b/make-test.log`) |
| `uv run python -m film.subs check film/subs/` | PASS: 8 files, 792 cues, 538 warnings (all "reading speed < 12 cps"); unchanged from the first pass |
| `film.subs align-qa` ×4 | main-ar PASS 0 warn; main-en PASS 2 warn (m-02-04 0.124, m-06-04 0.108); trailer-ar PASS 1 (t-07 0.220); trailer-en PASS 1 (t-02 0.110); identical to the first pass |
| `git diff 3a002a6 -- film/script/` | empty (0 bytes) |
| `git diff 3a002a6 --stat` | 84 files; every path under `film/`, `docs/film.md`, `docs/status/r10.md`, `docs/status/verify-R10_HALF2.md`, `docs/STATUS.md`, `docs/cost-log.*`, `prompts/R10.md`, `prompts/R10_HALF2.md`, `tests/test_film_*`, `scripts/film_*`, `cities/ksa/assumptions/film_voice.yaml`, `.gitignore` (filter for anything else: empty) |
| `git diff 4a05318 --stat` (the fix commit) | 33 files: `film/render.py` (+36/−23), `film/subs.py` (comment), `scripts/film_subs_qa.py`, new `scripts/film_subs_qa_chrome.mjs`, the 24 QA PNGs, `docs/film.md`, `docs/status/r10.md`, `docs/cost-log.*`, this file |
| `grep -rn "/Users/[a-z]" $(git ls-files)`; secrets grep; `grep "git push"` in `scripts/film_*` and `film/*.py` | all empty (the only secrets-pattern hits are `risk-allocation`/`risk_allocation` strings in funding files matching the `sk-` prefix: false positives) |

### 7.2 F1 (credits card): FIXED

| check | evidence |
|---|---|
| Frames from the delivered MP4s | `ffmpeg -ss 805` and `-ss 812` on `film/renders/out/ksa-rail-twin-main-en.mp4`, `-ss 870`/`-ss 877` on `…-main-ar.mp4` → `/tmp/verify-r10h2b/credits-{en,ar}-*.png`, viewed. Both cards show, in order: "KSA Rail Twin: a research film, not an official film of any ministry or company" / «التوأم الرقمي للسكك الحديدية في السعودية: فيلم بحثي…»; "Voices: Nabrah (public voices Daniah, Norah, Abdullah)" / «الأصوات: نبرة…»; "Built with Claude (Anthropic)" / «بُني باستخدام Claude (Anthropic)»; OSM (ODbL) + GASTAT; SAR/HHR, OAG, GACA; the two Copernicus lines; archival photographs (two LOC attributions, public domain); fonts (Noto Naskh Arabic, Noto Sans, SIL OFL 1.1); tools (Google Chrome, ffmpeg); pointer to `docs/credits.md` and `film/rights_log.csv` |
| No Chatterbox credit | not on either frame; `credits_lines("en"/"ar")` printed from the module: 11 lines each, none mentions Chatterbox; `credits_roll_html("ar").lower()` contains no "chatterbox"; `grep -i chatterbox film/render.py film/assemble/*.csv` empty |
| No raw register strings | the `attribution` column is no longer printed as a line: `render.py:669-677` selects `fonts` by `item`, `images` by `attribution` (the two photographers' credits, which are real attribution texts), `tools` by `item` with `used_in` containing render/encode. "attribute Nabrah on published audio (Tariq, 7 Nov 2026)" and "none for local use" are gone from both frames |
| Latin runs in Arabic not mirrored | Arabic frame: "Claude (Anthropic)", "© OpenStreetMap contributors (ODbL)", "(SIL OFL 1.1)", "(public domain)", "docs/credits.md و film/rights_log.csv" all read correctly with brackets on the right side; `ltr_isolate` now wraps 10 runs per card in `<bdi dir="ltr">` (regex extended with `_` for `rights_log`), and the U+200F marks before "(" are removed from the Arabic strings (`render.py:690-701`) |
| Docstring accurate | `render.py:638`: "The closing credits card (sh-08-14); text from credits_lines()."; `credits_lines` docstring (`:661-664`) says the full register is in `docs/credits.md` and `film/rights_log.csv` (named on the card), not read |
| Re-render before re-assembly | `film/renders/main-en/frames/sh-08-14.O.html` 01:38:13, `main-en/sh-08-14.mp4` 01:38:18, `main-ar/sh-08-14.mp4` 01:38:26; `out/ksa-rail-twin-main-ar.mp4` 02:01, `…-main-en.mp4` 02:02 (8 Nov) |
| `docs/film.md` §1 vs `shasum`/`ffprobe` | main-ar `4d49f0a74b15882a`, 880.933 s, 58,899,550 B (58.9 MB); main-en `c19a7828e6667e35`, 817.133 s, 56,796,006 B (56.8 MB); trailer-ar `139299499a75ac58`, 88.533 s; trailer-en `2879dce6002430b8`, 84.500 s: all four match §1 (trailers unchanged) |
| Loudness after re-assembly | `film/assemble/loudness.csv` final rows: −16.04/−1.55, −16.06/−1.77, −16.10/−1.84, −16.06/−1.78 LUFS/dBTP; my `ffmpeg loudnorm` measurement of the re-assembled `main-en`: Input Integrated −16.1 LUFS, True Peak −1.8 dBTP, LRA 4.3 LU (= the table's −16.06/−1.77/4.30 at one decimal); all within −16 ±1 and ≤ −1.5 dBTP |
| `docs/film.md` §6 | now describes the shipped card (fixed lines + register-derived fonts/images/tools), records the F1 history and the new SHA-256 values |

### 7.3 F2 (Chrome subtitle QA): FIXED

| check | evidence |
|---|---|
| Chrome PNGs distinct | `md5 -q film/subs/qa/*-chrome.png | sort -u | wc -l` = 12 (12 files); the four `cue001-chrome.png` grew from 4,250 B (black) to 60–303 KB; Firefox PNGs also 12 distinct |
| Each Chrome frame shows its cue | viewed `main-ar-cue001-chrome.png` («أربع رحلات. ما فيها ولا شخص حقيقي…», right-aligned, two lines), `main-ar-cue008-chrome.png` («في 2025 جا خط جدة–الرياض خامس…», digits in logical order, right-aligned), `main-en-cue001-chrome.png` ("Four journeys. No traveller here is a real person…"), `main-en-cue010-chrome.png` ("In 2025, Jeddah–Riyadh was fifth in OAG's top ten…"), `trailer-ar-cue003-chrome.png` («جدة–الرياض في 2025: حوالي 9.8 مليون مقعد طيران مجدول»), `trailer-ar-cue005-chrome.png` («الطائف، تبوك، أبها، نجران، جازان: ولا وحدة… 10 كيلو»), `trailer-en-cue001-chrome.png` ("A night train heading north…"). Firefox frames viewed for comparison: `main-ar-cue008-firefox.png`, `main-en-cue011-firefox.png`, `trailer-en-cue005-firefox.png`, each with the same cue text. No digit reordering seen |
| Script change | `scripts/film_subs_qa.py:101-109` `main_checkout()` resolves `git rev-parse --path-format=absolute --git-common-dir` and takes its parent; `shoot()` (`:114-123`) runs `node scripts/film_subs_qa_chrome.mjs <puppeteer-core dir> <chrome> <url> <png>` with puppeteer-core from `<main checkout>/web/node_modules/puppeteer-core`; clip now starts at the cue (`t0 = s`, comment explains the missing Range support); page script seeks to `a + 0.5` whether or not metadata is already loaded. `scripts/film_subs_qa_chrome.mjs` (23 lines) waits for `readyState >= 2 && !seeking && textTracks[0].activeCues.length > 0` (30 s timeout, 200 ms polling), then 500 ms, then 1280×720 screenshot. No absolute home path in either file (home-path grep empty); nothing leaves 127.0.0.1 |
| `film/subs/qa/report.json` | 24 PNG rows `exists: true`; both bidi-probe runs exit 0, "0 numeric runs, 0 wrong; 0 footnote markers, 0 wrong; 0 wrapped" |
| Documents | `docs/film.md` §5 names both players, the puppeteer wait, the first-pass failure and the cosmetic footer overlap; `docs/status/r10.md:136` says "Chrome (puppeteer-core, waits for the active cue) and Firefox … each showing its cue" |

### 7.4 Minor items from §5

| item | status | evidence |
|---|---|---|
| 1. "Paid TTS: USD 0 so far"; block header | fixed | `docs/status/r10.md:115`: "Paid TTS at launch: USD 0 … at the end of the run USD 2.04 list equivalent (below)"; header now `v1.5 | 8 Nov 2026 | … (v1.5: R10_HALF2 results, verifier, closing lines …)`. Line 3 of the file ("Paid TTS: USD 0 of the separate USD 60 cap") belongs to the half-1 (R10_LAUNCH) block and was true for that run; not an error |
| 2. Closing lines | pending by design | `grep -nE "^R10_HALF2: done|^R10: (done|blocked)" docs/status/r10.md` empty at 62407e1; the builder appends `R10_HALF2: done` and, last, `R10: blocked - CP9 review required` after this PASS. `R10: done` must not be written |
| 3. "192 kb/s" | fixed | `docs/film.md:19`: "AAC 48 kHz mono narration (192 kb/s requested; 138–153 kb/s measured)"; ffprobe today: 153,386 / 151,877 / 141,240 / 137,888 b/s |
| 4. "17,500 chars" | fixed | `docs/cost-log.csv:84` and `.md:91`: "about 17,700 chars ≈ 7,000 credits" |
| 5. A-film-012 pointer | fixed (comment only) | `film/subs.py:192`: `CER_WARN, CER_FAIL = 0.10, 0.30  # A-film-012 (film/assumptions-r10.md)`; the values stay constants in code rather than YAML, which I accept for a QA threshold (low priority, as before) |
| 6. Cue overlaps the footer label | open, cosmetic | still visible in e.g. `main-ar-cue008-chrome.png`, `main-en-cue010-chrome.png`; now disclosed in `docs/film.md` §5 for CP9 |
| 7, 8. Nabrah licence caveat; provisional voice roles | unchanged, correctly flagged | rights log, `docs/film.md` §2, A-film-006; CP9 items for Tariq |

### 7.5 Criteria re-scored

Criteria 4, 5 and 12 of §2 now PASS on the evidence in §7.2–7.4; criteria 1–3, 6–11 re-checked where the fix could touch them (make test, scripts unchanged, loudness, durations/SHA, cost log, hygiene) and still PASS. No criterion is open.

### 7.6 Remaining notes for CP9 (not blockers)

1. Both main cuts run over the 8–12 minute target (14:41 / 13:37), disclosed in `docs/film.md` §1 with options.
2. Nabrah audio was generated on trial credits; publishing it depends on the paid-plan terms (S-nabrah-005) and Tariq's decision.
3. Native Arabic review is pending on all 74 Arabic rows; nobody was contacted.
4. The subtitle cue box overlaps the bottom-left footer label in some players (cosmetic; `line:` position or lower footer).

VERDICT: PASS
