> **Document version:** docs/status/verify-FIX_HALF2_QUALITY.md v1.1 | 8 Nov 2026 | Author: red-team-verifier (`claude-fable-5-1`) (v1.1: second pass on 18e4e3b, F1 closed; v1.0: first pass on 399de39) | Status: verified

# Verification: FIX_HALF2_QUALITY (branch `r10`, worktree `.worktrees/r10`)

Scope checked: commits 50c2937..399de39 on `r10` against base 76b43bd (`git diff 76b43bd --stat`: 63 files, +2,723/−989). Brief: `prompts/FIX_HALF2_QUALITY.md` v1.1 (Tariq's notes, ADD_FIX_HALF2_QUALITY, coordinator addenda). This run rebuilt the two trailers only; the main cuts were deliberately not rebuilt (allowed by item 7). Read only; nothing fixed. `RAILTWIN_RUNS_ROOT=$HOME/Documents/Projects/KSA-RailTwin/runs`. Media read through the `film/renders` symlink (external volume); frames extracted to `/tmp/verify-fixq/` only.

## 1. Commands (procedure 1 and 8)

| command | exit | result / timing |
|---|---|---|
| `uv run ruff check .` | 0 | `All checks passed!` |
| `uv run ruff format --check .` | 0 | `790 files already formatted` |
| `make test` (pytest + docver + manifest) | 0 | 41.0 s wall; `docver OK: 395 files`; `manifest OK: 388 rows`; pytest green (log `/tmp/verify-fixq/make-test.log`) |
| `uv run python -m common.docver check` | 0 | `docver OK: 395 files` |
| `uv run python -m common.manifest verify` | 0 | `manifest OK: 388 rows` |
| `uv run python -m film.script validate film/script/` | 0 | `PASS: 146 lines (main/ar 62, main/en 62, trailer/ar 11, trailer/en 11); 1 warning` (trailer/ar spoken estimate 58.3 s < 60 s; delivered length checked on the edit list) |
| `uv run python -m film.shots check film/storyboard/shots.yaml --lines film/script/lines.csv` | 0 | `PASS: 69 shots (main 685.5 s, trailer 60.0 s)` |
| `uv run python -m film.rights check film/rights_log.csv` | 0 | `PASS: 66 rows (candidate 31, rejected 14, test_only 6, used 15)` |
| `uv run python -m film.subs check film/subs` | 0 | `PASS: 8 file(s), 788 cues, 540 warning(s)` (reading-speed warnings only) |
| `uv run python -m film.subs align-qa --cut trailer --lang en` | 0 | `PASS (0 warning(s))` |
| `uv run python -m film.subs align-qa --cut trailer --lang ar` | 0 | `PASS (1 warning(s))`: `WARN t-07: read-back CER 0.171 > 0.1` |
| `git status --porcelain` | 0 | empty (clean at 399de39, `git describe` = `r9-45-g399de39`) |

## 2. Criteria

| # | criterion | verdict | evidence |
|---|---|---|---|
| 1a | Only the refrain was removed from `lines.csv`; no digit, name, range or claim changed | PASS | Script over `git show 76b43bd:film/script/lines.csv` vs HEAD: 33 text edits (ar+en), every one a deletion of "In the model, " / "in this model" / "an uncalibrated test" / «في النموذج،» / «وهذا اختبار غير معاير» / «في هالنموذج» / «اللي انحسبت في النموذج»→«اللي انحسبت», plus the permitted shortening of the closing lines m-08-11 and t-10; digit sequences identical on every edited line (`re.findall(r"\d+(?:[.,]\d+)?")` old == new); no other row text changed; only `est_seconds` and `on_screen_label` moved with them |
| 1b | m-06-07 removed entirely (it was the refrain) | PASS | removed keys: `('m-06-07','ar'), ('m-06-07','en')`; old text "Demand is synthetic: built from public data…" / «والطلب هنا تركيبي…»; `sh-06-07` removed from `shots.yaml` (`film/storyboard/refrain-edits.csv` row `sh-06-07,(shot),…,(shot removed with its line)`) |
| 1c | m-08-06 untouched | PASS | en/ar text byte-identical to 76b43bd ("users' travel time and cost savings … 2.3 to 19.3 billion riyals … safety benefit … 0.6 to 7.4 billion"); only its label went `synthetic`→`none`; `tests/test_film_quality.py::test_m_08_06_unchanged_by_the_refrain_edit` |
| 1d | `label` column kept as data, `none` where dropped | PASS | `on_screen_label` counts at HEAD: `none` 58, blank 73, `composite` 12, `quote` 3; 0 rows still `synthetic`/`synthetic+not_official` |
| 1e | `film/script/refrain-edits.csv` and before/after table in the status block | PASS | 60 data rows (`wc -l` 61); `docs/status/r10.md:157-195` table of every edited line (old → new, both languages) plus the label-only list; matches the diff |
| 1f | Subtitles follow the edited text | PASS | every trailer line (11 en, 11 ar) found verbatim in `film/subs/trailer.{en,ar}.srt` (cues re-joined; U+200F stripped); `film.subs check` PASS; `align-qa` PASS both languages |
| 2a | Single closing notice: only sh-08-54 and sh-08-14 carry `footer: synthetic` | PASS | `shots.yaml` footers != none: `sh-08-14 synthetic main`, `sh-08-54 synthetic trailer`; `check_closing_notice` in `film.shots check`; `renders-trailer-*.csv` footer column `none` on 10 shots, `synthetic` on sh-08-54 only |
| 2b | Arabic wording = glossary term 4 | PASS | `film/sim.py:540-543` `CLOSING_NOTICE["ar"] = R.FOOTER["ar"][0] + "."`; `film/render.py:692` credits `FOOTER["ar"][0] + "."`; closing frame (ar, 85.8 s) reads «طلب تركيبي غير مُعايَر: مقارنة سيناريوهات، ليست توقعاً.»; `test_closing_notice_wording_uses_glossary_term_4` |
| 2c | Visual: notice on the last frame, no stamp mid-trailer | PASS | frames `/tmp/verify-fixq/tr-en-end.png` (76.5 s) and `tr-ar-end.png` (85.8 s): title + notice + narration/data credits; mid frames at 12/21/30/38/45/55/62/66/69/73 s in both languages: no synthetic/uncalibrated stamp anywhere |
| 2d | Checker relaxations limited to film and film tests; diff scope | PASS (note) | `git diff 76b43bd --name-only` outside `film/`, `tests/test_film_*`, `docs/film.md`, `docs/status/r10.md`, `docs/status/cp8-package.md`, `cities/ksa/assumptions/film_voice.yaml`, `prompts/FIX_HALF2_QUALITY.md`: only `docs/cost-log.csv`, `docs/cost-log.md` (required by the model policy) and `tests/fixtures/film/shots.yaml` (film test fixture, 2 lines). PROJECT.md, R8 report, dashboard, studies untouched |
| 3a | `speech_text` on the Arabic trailer rows; stripping marks returns the accepted text or its say.csv override | PASS | 11 of 73 Arabic rows carry `speech_text` (all trailer rows), 0 English rows; `strip_tashkeel(speech_text) == strip_tashkeel(say or text)` for all 11 (t-05/t-06 differ from the raw text only by the shadda the accepted text itself carries); digits identical in order; `test_speech_text_only_adds_tashkeel`, `test_speech_text_check_catches_changes` |
| 3b | Approach registered | PASS | `film/assumptions-r10.md` A-film-014 (hand/LLM vocalisation, Saudi pronunciation, words that read worse keep the accepted spelling; native review pending); `film_voice.yaml` v1.2 |
| 3c | Subtitles unvocalised | PASS | `grep -c [ً-ْ] film/subs/trailer.ar.srt` = 3 lines, all from the accepted text's own shadda (قدّام, انسعّر, مجمّد); `native_review` values `{pending, n/a}` only |
| 4a | English trailer = ElevenLabs George on all 11 lines | PASS | `film/voice/timing/trailer-en.csv`: 11 rows `elevenlabs,George`; read-back CER 0.000-0.050 (`film/voice/readback/trailer-en.csv`) |
| 4b | Voice id / model / terms recorded; free-tier non-commercial caveat; no cloning | PASS | `film/rights_log.csv` row 66 (voice id JBFqnCBsd6RMkjVDRZzb, eleven_multilingual_v2, terms last updated 2026-10-09, read 2026-11-08, "non-commercial use only; regenerate on a paid plan"); `film/licences-r10.csv` row ("N on Free (§1(c)(i)); Y on paid plans"); `ab-fixq.csv` "premade voice"; WebFetch of https://elevenlabs.io/terms-of-use on 8 Nov 2026 confirms §1(c) free = non-commercial, paid = commercial, §4(c)(ii) user retains rights in Output, last updated 09 Oct 2026 |
| 4c | Arabic = Nabrah Abdullah/Norah/Daniah; no forbidden voices | PASS | `trailer-ar.csv`: 11 rows `nabrah` with Abdullah (t-01,02,04,05), Norah (t-03), Daniah (t-06..11); grep for clartts / namaa-saudi / chatterbox-mtl / Amal / Sultan over timing, assemble, shots.yaml, lines.csv: empty |
| 5a | Paid TTS tally | PASS | `docs/cost-log.csv` paid Nabrah rows (lines 79,81-90,92,93): 0.12+0.08+0.07+0.74+0.45+0.46+0.01+0.01+0.00+0.07+0.03+0.09+0.06 = USD 2.19; ElevenLabs rows (80, 91) 0.00; same rows in `cost-log.md:98-100`; status block and `docs/film.md` §0 say 2.19 / 0.00; cap 60, alert 48 not reached |
| 5b | No keys in tracked files | PASS | grep over `git ls-files` for `sk_…`, `xi-api-key`, `NABRAH…KEY`, `Bearer …`, `api_key=…`: empty; no `.env*` in the worktree |
| 6a | Trailer shots use `renderer: sim_map` | PASS | all 11 trailer shots in `shots.yaml` (`sh-01-51 … sh-08-54`) `renderer: sim_map`; `test_trailer_shots_use_the_sim_renderer` |
| 6b | Frames are moving-map/simulation pictures with full-sentence captions, credits, legend, RTL | PASS (cosmetic notes M4) | 13 frames per language read: relief basemap, drawn lines, trains/arcs, population dots, Taif escarpment, attempts cloud, NPV and fiscal bars; captions are full sentences with units and horizon ("Net present value at high cost: 4.0 to 5.6 billion SAR (2025 prices, 60 years)"); OSM and Copernicus credit lines on every frame; legend on map shots (existing / committed / hypothetical); Arabic captions right-aligned, numbers LTR inside RTL text |
| 6c | Every on-screen number traces; caption numbers in narration or `extra_figures` | PASS | `renders-trailer-{en,ar}.csv` `figures_not_found` empty on all 22 rows; `figures_traced` e.g. sh-01-52 `2025 9.8`, sh-03-51 `2024 35.3`, sh-07-51 `10,000`, sh-08-51 `4.0 5.6 2025 60`; `extra_figures` declared: sh-08-51 `['2025','60']`, sh-08-52 `['60']`; `film.shots check` PASS |
| 7a | ffprobe both trailers | PASS | en: h264 1920×1080 30/1, aac 48 kHz mono, mov_text, 77.600 s, 30,189,897 B, SHA-256 c36c1ce1b73b97f8…; ar: same codecs, 86.900 s, 33,276,508 B, db3db9c4857a1ad5…; both within 60-90 s; EDL sums 77.6 / 86.9 s |
| 7b | Loudness | PASS | `film/assemble/loudness.csv`: trailer en final −16.22 LUFS / −1.86 dBTP; ar −16.06 / −1.88 (target −16 / ≤ −1.5) |
| 8 | make test, validate, shots check, rights check | PASS | table in §1 |
| 9a | No home paths, no secrets, no tracked media | PASS | `grep "/Users/[a-z]"` over changed and over all tracked files: empty; `git ls-files data runs movies film/renders film/audio`: only the allowed READMEs and GASTAT tables |
| 9b | No model names in public-facing outputs beyond the approved credit | PASS | film scripts, lines.csv, subtitles, shots.yaml, sim.py: only the credits-roll line "Built with Claude (Anthropic)" (`render.py:680,694`, accepted storyboard sh-08-14); the trailer closing frame shows no model name |
| 9c | No content from the author's company, no advocacy | PASS | Private-list grep: only the prohibition sentences in CLAUDE.md, PROJECT.md, agent files and earlier verify reports; trailer wording "none is a recommendation to build", "a possibility, not a promise" |
| 9d | No push / merge / tag / remote | PASS | `git remote -v` empty; tags unchanged (last `r9`, `session1-pilot`); no `git push` in scripts |
| 10 | Determinism (procedure 3) | PASS | `sim.render_shot(sh-08-54, "en", 2.0, seed=7)` twice to `/tmp/verify-fixq/det{1,2}/`: `ffmpeg -f framemd5` digests identical (`aef2e69b290ab6a8c2690a4d05bbd367`), 591,379 B each, 60 frames |
| 11 | Registers for the run | PASS | A-film-013..015 in `film/assumptions-r10.md` v1.3; rights log rows 65-66 (sim.py renderer stack, ElevenLabs George); `film/licences-r10.csv` +2 rows; `film_voice.yaml` v1.2 with `source:`/`assumption:` on the new keys |
| 12a | Status block numbers match what was measured | PASS | 77.6 s / 86.9 s, −16.22/−1.86, −16.06/−1.88, 30.2 / 33.3 MB, hashes c36c1ce1… / db3db9c4…, USD 2.19, 11 lines George, all re-measured above |
| 12b | Milestone label line present; last line per item 7 | **FAIL** | `grep -n "QUALITY: " docs/status/r10.md` → no match: neither `R10_HALF2_QUALITY: done` nor `FIX_HALF2_QUALITY: done` (or `… blocked - …`) exists. Last line (`docs/status/r10.md:205`) is `R10: blocked - CP9 review required`, the variant item 7 reserves for "both language trailers and both language main cuts ready for review"; the block itself and `docs/film.md` §0 say the main cuts were not rebuilt and still are the rejected card versions, so the required last line is `R10: blocked - new trailers ready for Tariq (simulation pictures, ElevenLabs English, tashkeel Nabrah Arabic)`. The launcher's end signal is missing and the file's last line misstates the state |
| 12c | Cost log has a row for the run | PENDING | paid rows for the run present (cost-log.csv 91-93); no Claude-run row (`common.cost_log add`) yet: added by the coordinator after the run ends, as in earlier milestones; not counted as a FAIL |

## 3. Failures (exact evidence)

**F1 (blocking). Label lines and closing line of `docs/status/r10.md`.** The FIX_HALF2_QUALITY block (lines 147-205) ends with the "Disk" paragraph and `R10: blocked - CP9 review required`. Required by the brief: Tariq's `R10_HALF2_QUALITY: done`, then the coordinator's `FIX_HALF2_QUALITY: done`, then, because only the trailers were rebuilt, `R10: blocked - new trailers ready for Tariq (simulation pictures, ElevenLabs English, tashkeel Nabrah Arabic)` as the last line. Commands: `grep -n "^R10_HALF2_QUALITY:\|^FIX_HALF2_QUALITY:\|^R10:" docs/status/r10.md` → only `205:R10: blocked - CP9 review required`. The run_track launcher greps for the label line, so the milestone cannot be closed as it stands, and "CP9 review required" would send Tariq to main cuts that §0 of `docs/film.md` says "do not treat as final".

## 4. Minor findings (not blocking)

- **M1** `film/storyboard/storyboard.md` changed (46 insertions, 47 deletions: durations, section totals) but its header is still `v1.3 | 7 Nov 2026` (CLAUDE.md source-versioning rule 3: bump the minor on every substantive edit).
- **M2** `docs/film.md` keeps stale statements next to the new §0: line 5 "Every modelled result on screen carries 'synthetic demand, uncalibrated…'; Riyadh–Jeddah and extra-travel shots also carry 'not the official ranking'" (no longer true for the trailers); §1 table still lists the trailers at 88.5 s / 84.5 s, 6.5 / 6.0 MB, old hashes, with no "superseded by §0" marker; §4 "Footers … follow shots.yaml" describes the card renderer only.
- **M3** `docs/credits.md:168` (row 154) still says ElevenLabs "terms to read at R10 … Arabic … A/B candidate", while the credits card points viewers to `docs/credits.md`; the film registers (`film/rights_log.csv`, `film/licences-r10.csv`) are current. `docs/licences.csv` was not asked for in this run.
- **M4** Picture cosmetics seen in the frames: on sh-08-51 (t-08) the chart labels "4.0", "5.6 billion SAR" / «5.6 مليار ريال» and "break-even" / «التعادل» are on screen about 2-3 s before the chart panel and bar draw (en 55 s, ar 62 s), so they float over the map for a moment (the caption sentence below does carry the figures); on the Arabic sh-08-51 the «الظهران» label sits under the station glow at shot start (clear by 66 s); on the Arabic sh-07-51 the y-axis label «↑ صافي القيمة الحالية الصامد» touches the first attempt dots; the Arabic t-02 caption wraps inside «أو إيه جي» (OAG). Nothing clipped; all for Tariq's watch.
- **M5** `shots.yaml` sh-04-07 (main cut) `visual:` still reads "Tag: 'uncalibrated sensitivity'" (planning text, not `on_screen_text`); it will matter when the main cuts are rebuilt.
- **M6** `docs/STATUS.md` has no FIX_HALF2_QUALITY entry and `docs/cost-log.*` no Claude-run row yet (coordinator's files; see 12c).
- **M7** t-07 Arabic read-back CER 0.171 («عشرة آلاف» heard as «عشر آلاف»): reported by the builder; for the ear check.
- **M8** Native Saudi review of every Arabic row and of the tashkeel remains pending (expected; nobody contacted).

## 5. Spot-check sample (procedure 9)

Register: `film/rights_log.csv` (66 rows; the candidate, cost and benchmark registers were not touched by this run). `random.seed(20261108)`, `random.sample(range(66), 7)` → CSV lines 21, 26, 30, 37, 43, 59, 66 (10.6 %).

| line | item | register says | source checked (WebFetch, 8 Nov 2026) | result |
|---|---|---|---|---|
| 21 | mobarmg/OmniVoice-Najdi (rejected) | CC-BY-NC-4.0 | huggingface.co/mobarmg/OmniVoice-Najdi: tag `cc-by-nc-4.0` | consistent |
| 26 | IbrahimSalah/Arabic-TTS-Spark (rejected) | fair-noncommercial-research-license | model card tag "fair-noncommercial-research-license" | consistent |
| 30 | ElevenLabs Arabic voices (test_only) | Proprietary SaaS | elevenlabs.io/terms-of-use: §1(c) free non-commercial / paid commercial | consistent |
| 37 | Common Voice Arabic, Mozilla Data Collective (candidate) | CC0 (secondary: MDC page renders by script) | page returns "Loading dataset…" without licence text | consistent with the register's own note; licence not independently confirmed |
| 43 | Amiri (candidate) | SIL OFL 1.1 | github.com/aliftype/amiri OFL.txt: "SIL OPEN FONT LICENSE Version 1.1" | consistent |
| 59 | OpenFreeMap Positron (candidate) | MIT; attribution required | openfreemap.org: "The license of this project is MIT … Attribution is required" | consistent |
| 66 | ElevenLabs George (used) | Terms §1(c) free = non-commercial; §4(c)(ii) output rights; updated 2026-10-09 | elevenlabs.io/terms-of-use: §1(c) as stated; §4(c)(ii) "you retain all rights in and to your Output"; Last Updated 09 October 2026 | consistent |

No fabricated or misquoted figure found.

## 6. Three most important fixes

1. Append the label lines to `docs/status/r10.md` in the order the brief gives: `R10_HALF2_QUALITY: done`, `FIX_HALF2_QUALITY: done`, and replace the last line with `R10: blocked - new trailers ready for Tariq (simulation pictures, ElevenLabs English, tashkeel Nabrah Arabic)`; bump the file header (v1.6).
2. Bump `film/storyboard/storyboard.md` to v1.4 | 8 Nov 2026 and reconcile `docs/film.md` (line 5, §1 trailer rows marked superseded by §0, §4 footer sentence) so the document does not contradict itself.
3. Before the main-cut rebuild: fix the chart-label timing on sh-08-51 (labels after the panel) and the Arabic Dhahran label/glow order; update `docs/credits.md` row 154 (ElevenLabs terms read 8 Nov 2026, English narrator, non-commercial on the free tier); drop the "uncalibrated sensitivity" tag from sh-04-07's visual note.

First-pass verdict (399de39): FAIL on F1 only. Superseded by the second pass below.

## 7. Second pass (18e4e3b, 8 Nov 2026)

Narrow re-check after the builder's fix commit. The launcher named the fix commit `e3b01ab`; that revision does not exist in this worktree (`git rev-parse --verify e3b01ab` fails). The only commit after `399de39` on `r10` is `18e4e3b` ("fix(film): chart labels fade in with their panel; Arabic OAG kept on one line; verifier minor items; status end lines"), `git describe` = `r9-46-g18e4e3b`, working tree clean before and after the checks. `git diff 399de39 18e4e3b --stat`: 6 files (+145/−19): `docs/film.md`, `docs/status/r10.md`, `docs/status/verify-FIX_HALF2_QUALITY.md` (the first pass), `film/sim.py`, `film/storyboard/shots.yaml`, `film/storyboard/storyboard.md`. Read only; nothing fixed. Frames extracted to `/tmp/verify-fix-half2-pass2/` only.

| # | item | verdict | evidence |
|---|---|---|---|
| S1 | F1: `R10_HALF2_QUALITY: done` then `FIX_HALF2_QUALITY: done` as plain start-of-line text in `docs/status/r10.md` | PASS | `grep -n -E '^(R10_HALF2_QUALITY: done\|FIX_HALF2_QUALITY: done\|R10: )' docs/status/r10.md` → `209:R10_HALF2_QUALITY: done`, `211:FIX_HALF2_QUALITY: done`, `213:R10: blocked - …`; order as the brief requires |
| S2 | F1: last non-empty line is exactly `R10: blocked - new trailers ready for Tariq (simulation pictures, ElevenLabs English, tashkeel Nabrah Arabic)`; no other `R10: ` start-of-line closing line after it | PASS | `awk 'NF{last=$0} END{print last}'` piped to `cmp` against the required string: byte-exact match (trailing `\n` only); file is 213 lines, line 213 is that line; `grep -n '^R10: '` returns line 213 only (the old `R10: blocked - CP9 review required` is gone) |
| S3 | Post-pass code change limited to the label layer | PASS | `film/sim.py`: new `texts_html()` (chart/panel labels moved out of `overlay_html` into their own layer), `Scene.texts_at: float = 0.0`, composite `ta = min(oa, fr(f, texts_at, texts_at + 0.06))`; `sh-08-51` sets `texts_at=0.3`; sh-07-51 axis labels moved `py0 - 6` → `py0 - 34`. No other scene or renderer logic changed |
| S4 | `shots.yaml`: sh-01-52 Arabic NBSP; sh-04-07 visual | PASS | line 1278 `أو إيه جي.` carries 2 × U+00A0 (`od -c` shows `302 240` twice), so «أو إيه جي» cannot wrap; sh-04-07 `visual:` no longer contains "Tag: 'uncalibrated sensitivity'" (diff lines 617-618); `storyboard.md` table row regenerated accordingly |
| S5 | `storyboard.md` header bumped | PASS | line 1: `film/storyboard/storyboard.md v1.4 | 8 Nov 2026 | … (v1.4: FIX_HALF2_QUALITY, single closing notice, sim_map trailer shots, refrain dropped; …)` |
| S6 | `docs/film.md` final hashes = files on disk | PASS | `shasum -a 256 film/renders/out/ksa-rail-twin-trailer-{en,ar}.mp4` → en `07b52f6556115c01…`, ar `21df620d1994ec75…`; `docs/film.md:14-15` state `07b52f6556115c01` / `21df620d1994ec75`; `docs/status/r10.md` verifier paragraph states the same pair; file mtimes 03:23:39 / 03:23:47 (before the 03:25:05 commit) |
| S7 | Durations still 77.6 / 86.9 s | PASS | `ffprobe -show_entries format=duration`: `77.600000` (en), `86.900000` (ar); sizes 30,202,869 B (30.2 MB) and 33,276,888 B (33.3 MB), as in `docs/film.md` §0; EDL `edl-trailer-ar.csv` sums to 86.9 s |
| S8 | `film/assemble/renders-trailer-*.csv` `figures_not_found` empty | PASS | both files: 11 rows, column present, 0 non-empty values (`python3 -I` csv read) |
| S9 | Arabic trailer frame at ~54 s and at the sh-08-51 start: no floating chart labels before the panel | PASS | sh-08-51 starts at 59.533 s in the Arabic trailer (`edl-trailer-ar.csv`, `renders-trailer-ar.csv` cumulative), not 54 s; 53.5-59.5 s is sh-07-51. Frames read: 54.0 s (sh-07-51: Pareto panel, lifted axis label «↑ صافي القيمة الحالية الصامد» now above the panel edge, no overlap with the attempt dots), 59.7 s and 61.5 s (sh-08-51: map, stations, caption; no panel, no labels), 62.5 s (panel background fading in, no labels), 63.3 s (panel with «التعادل», «4.0», «5.6 مليار ريال»; bar not yet drawn), 64.5 s (bar growing), 67.0 s. Standalone `film/renders/trailer-ar/sh-08-51.mp4` (11.000 s, mtime 03:23:34) at 2.0 / 2.7 / 3.0 s: no labels; 3.6 s: labels on the panel. Matches the code: panel from fraction 0.25, labels 0.30-0.36, bar from 0.35 |
| S10 | `make test` | PASS | exit 0, 42.0 s wall: `ruff check` "All checks passed!", `ruff format --check` "791 files already formatted", pytest green (dots and `s` only, no `F`), `docver OK: 396 files`, `manifest OK: 388 rows`; log `/tmp/verify-fix-half2-pass2/make-test.log`; `git status --porcelain` empty afterwards |

Minor findings carried or new (not blocking):

- **M9 (new)** `docs/film.md` (header still `v1.2 | 8 Nov 2026`) and `docs/status/r10.md` (still `v1.5`) were edited substantively in 18e4e3b (final hashes, verifier paragraph, the three end lines) without a header bump; the first pass's fix 1 asked for r10.md v1.6. CLAUDE.md source-versioning rule 3. `docver check` passes because it checks presence, not the bump.
- **M3 (carried)** `docs/credits.md` row 154 (ElevenLabs described as an R10 A/B candidate) unchanged; the builder notes it feeds the R8 annexes and leaves it for integration. The film registers (`film/rights_log.csv` row 66, `film/licences-r10.csv`) are current.
- **M4 (part carried)** The Arabic «الظهران» label still sits under the station glow at shot start (frames 62.5 s and 63.3 s), clear later; cosmetic, for Tariq's watch. Labels on sh-08-51 now arrive with the panel and about 0.5 s before the bar begins, which is what the fix intended.
- **M6/12c (carried)** No Claude-run row for this run in `docs/cost-log.*` yet and no FIX_HALF2_QUALITY entry in `docs/STATUS.md`: coordinator's files, added after the run as in earlier milestones.
- **M7, M8 (carried)** t-07 Arabic read-back CER 0.171; native Saudi review of the Arabic rows and tashkeel pending.

F1 is closed. The three checks the launcher asked for pass, the post-pass changes are confined to the label layer, two storyboard rows, the storyboard header and the two status documents, and every stated hash, duration and count matches what was measured.

VERDICT: PASS
