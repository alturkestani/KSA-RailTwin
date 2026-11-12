> **Document version:** docs/publish/checklist.md v1.5 | 12 Nov 2026 | Author: FIX_EXPORT_NAMES (v1.5: private names moved to the gitignored list `.publish/private-names.txt`, R2 widened, §2, §7, §10); PUBLISH_EXPORT (v1.4: Tariq's answers Q1–Q9 applied, §8; figure inputs §9; export built, §10); PUBLISH_PREP (main; v1.1: TrafficTwin table 550 lines, scan-commit note on the §1 counts, VERIFY_PUBLISH_PREP pass 1); PUBLISH_PREP_URL (v1.2: repository URL, push variants (a)/(b) in §7; v1.3: verifier notes O1, O2) | Status: draft

# Public-release checklist (PUBLISH_PREP, 12 Nov 2026 AST)

**Update (PUBLISH_EXPORT, 12 Nov 2026): Tariq answered Q1–Q9 (§8). The answers are applied on `main`, and the public export was built at `~/Documents/Projects/KSA-RailTwin-public` (§10). Still nothing is pushed and no remote is added; the two push commands are in §10 as text.** The rest of this section and §1–§7 describe the PUBLISH_PREP run.

This run prepared the repository for a public GitHub release and stopped. **Nothing was pushed or published, no remote was added, and no export branch or folder was created.** `main` history was not rewritten: this run only added commits on top of a1d36aa, and tag `r10-final` still points to 92c5472. This file lists every finding and decision, the exact push steps (as text, for Tariq), and the open questions. It supersedes the R9 list in `docs/release-checklist.md` for anything that differs.

Findings are reported as file, commit, type and treatment. **No secret value, email address, phone number or home path is quoted here.**

## 1. Secrets and personal data (full history)

**Scope and counts.** The scan ran at 85afd41. The file counts in S8, S13 and S16 are as of that commit; this run's later files in `docs/publish/` add self-references (the verifier counted 24, 67 and 16 at 9e2975d). All refs (`git rev-list --all`: 689 commits, every track branch merged into `main`, including `r10`) and the 18 annotated tags. Tools: gitleaks 8.30.1 (already installed) and trufflehog 3.99.8 (installed with Homebrew in this run, run with `--no-verification` so that it made no network call). A third pass ran a regex scan over every blob reachable from any ref: home paths, volume paths, emails, phone numbers, street-address keywords, key and token shapes, `KEY=`/`TOKEN=` assignments, and private names. The `.env` file in the working tree was never opened.

| # | type | where (file) | commits | finding | treatment |
|---|---|---|---|---|---|
| S1 | credential shape (gitleaks generic-api-key) | `cities/ksa/alignments/` (5 files), `cities/ksa/alignments-v2/` (1 file) | 387ff0e, 6318367, 308efdc | `stations_key`: a 16-hex digest of a corridor's station list (`screening.corridors.stations_key`). **False positive** | keep; `.gitleaks.toml` (added) allowlists this line shape only. Re-scan with it: 0 findings |
| S2 | credential shape (trufflehog Refiner, 4 hits) | `docs/sources/index.csv`, `docs/sources/index.md`, `docs/report/annex-sources.md`, `docs/sources/r2-jazan.csv` | 48b088d, b30fdce, fb6b8fb | a UUID inside a public news-article URL. **False positive** | keep |
| S3 | credential shape (trufflehog SQLServer, 1 hit) | one GASTAT `.xlsx` under `data/ksa/tables/gastat/` | 9a877ec | bytes inside a binary spreadsheet. **False positive** | keep |
| S4 | API keys, tokens, `.env` values | none found | — | no key or token shapes; no `KEY=`/`TOKEN=`/`SECRET=`/`PASSWORD=` assignments with values; **no `.env*` file ever committed** (`git log --all` over `.env` paths is empty); `.env` and `.env.*` are gitignored | nothing to do |
| S5 | absolute home path | `docs/status/verify-CLOSE_R10.md`, `docs/status/verify-R10.md`, `docs/status/verify-REGION_HAIL-pass2.md`, `prompts/CLOSE_R10.md`, `prompts/R10_HALF2.md` | 1c6b395, 0ec2137; d1b9088, 96ec425; 0de90c5, 104f567; d8e2589, 1ef9ae3, fce616d; a4b2e31, 964e4a8 | **history only**. At HEAD no tracked file holds one (`tests/test_hygiene.py`). Two further regex hits (`verify-R6.md`, `verify-R6_V3.md`) are a literal `/Users/...` placeholder in prose | the squashed export (§7) leaves them behind |
| S6 | email address (third party, vendor) | `prompts/R9_LAUNCH.md` (2 addresses) | added 5edba39 | Tariq's verbatim prompt quoted two vendor addresses | **redacted on `main`** (bdfc214). Still in history until the squashed export |
| S7 | email address (third party, vendor) | `docs/licences.md` (1 address) | d703127, c013b49, f249b29 | history only; absent at HEAD | the squashed export leaves it behind |
| S8 | email address (institutional) | 23 published GASTAT and SPA PDFs or HTML under `data/ksa/tables/` | as committed | the publishers' own contact lines inside their documents | keep (part of the unmodified publications) |
| S9 | email-shaped strings | a parquet, a font, a PNG, a PDF and two spreadsheets | — | random bytes. **False positives** | keep |
| S10 | author identity | every commit (author and committer, 689 commits) and all 18 annotated tags | all | "author email on 689 commits" plus 18 tags; a single personal address | squashed export under a public or GitHub noreply address (§7); tags are not exported |
| S11 | phone numbers | `cities/ksa/zones/zones.geojson`, two `fig08` SVGs, `uv.lock`, two Noto fonts | — | digits inside coordinates, SVG paths, hashes and font binaries. **False positives**; no phone number found | keep |
| S12 | street addresses | none found | — | the keyword scan found no street address, P.O. box or postal code | nothing to do |
| S13 | private company name (rule 9) | 66 files at HEAD: the rule-9 sentence in `CLAUDE.md`, `PROJECT.md`, `prompts/_common.md`, 3 agent files, the `VERIFY_*` prompts and `prompts/R8.md`; a banned-word list in `tests/test_report_figures.py`; verifier reports | many | the name appears only in the prohibition itself and in checks that it is absent. No content | **redact in the export** (decision R2, §2). FIX_EXPORT_NAMES (12 Nov 2026): every such sentence and grep term on `main` rewritten without the name; R2 widened to the gitignored list |
| S14 | private project code names | 29 verifier reports in `docs/status/` (32 hits) | many | the code names appear as terms in the verifiers' grep patterns. No content | **redact in the export** (R2) |
| S15 | third-party person's name | 8 tracked files (`docs/sources/index.csv`/`.md`, `docs/report/annex-sources.md`, `docs/licences-release.md`, `docs/STATUS.md`, `docs/status/main.md`, `prompts/R9_LAUNCH.md`, `prompts/R10_LAUNCH.md`) | as committed | the vendor executive who confirmed the narration licence in writing, cited as the source of that confirmation | **replaced on `main` by company and role** ("the CEO of Nabrah.ai"; Tariq, 12 Nov 2026, Q4) in all 8 files; the confirmation stays cited as S-nabrah-005 |
| S16 | external-volume path | 15 tracked files at HEAD (film code defaults such as `film/gate.py` and `film/sim.py`, `docs/film.md`, R10 prompts and status) | — | the SSD mount point; not a home path and not personal. The film code reads it only as a default that `FILM_*` environment variables override | keep |

**Not in any tracked file:** gitignored local outputs such as `runs/r6/v3/national_reach.json` hold absolute paths. Neither `runs/` nor `logs/` ships.

## 2. What ships: keep, drop or redact

| item (tracked unless stated) | call | reason |
|---|---|---|
| code (`common/`, `rail/`, `network/`, `screening/`, `costs/`, `economics/`, `funding/`, `demand/`, `modechoice/`, `access/`, `coupling/`, `optimise/`, `study/`, `api/`, `web/`, `film/*.py`, `scripts/`), `tests/` and fixtures, `Makefile`, `pyproject.toml`, `uv.lock`, `.github/` | **keep** | the runnable study (Apache-2.0); the clean clone passes (§6) |
| registers and scenarios (`cities/ksa/`, `scenarios/`), including the alignment sidecars | **keep** | the study's inputs and outputs-as-registers. The alignment sidecars are ODbL share-alike derived databases (Tariq, 7 Nov 2026, B7) |
| study documents (`docs/report/`, `docs/policy-brief.md`, the executive summaries, research docs, registers, `docs/sources/`, `docs/deck-figures/`, `docs/report/figures/`) | **keep** | the product. Banners updated (§4). The dashboard screenshots carry the OSM and OpenFreeMap/OpenMapTiles credit on the image |
| `data/ksa/tables/`: 61 GASTAT publications and tables (PDF, xlsx, csv) plus READMEs and `sources.csv` | **keep** | GASTAT use policy: reuse including commercial use, with GASTAT acknowledged; modified tables marked as derived (`data/ksa/tables/README.md`) |
| `data/ksa/tables/pilgrims/gaca-19-million-air-passengers-hajj-1446.html`, `…/spa_N2326094_HHR_hajj1446.html` | **drop** (export only) | full copies of news pages whose terms were not captured. Cite by URL only (the 7 Nov citation-only rule). The figures stay cited in the registers |
| `data/ksa/tables/gastat/census-2022-20260929.csv`, `census-2022-dictionary.csv`, `population-region-20260928.csv`, `population-region-dictionary.csv` | **drop** (export only) | third-party (DataPulse) re-packagings of GASTAT tables whose own terms were never captured. They are superseded by the committed primary GASTAT TA1 exports and were a cross-check only. **Dropped; GASTAT cited directly (Tariq, 12 Nov 2026, Q5)** |
| `PROJECT.md`, `CLAUDE.md`, `.claude/agents/`, `.claude/skills/` | **redact** (export) | the brief and the method are the audit trail of an AI-built study, and the README links them. Redact the rule-9 company name (R2). The model-id mapping in `CLAUDE.md` and the agent files stays: you approved public citation of Claude (7 Nov 2026). **Published with R2 (Tariq, 12 Nov 2026, Q3).** |
| `prompts/` (108 files) | **redact** | your verbatim instructions per milestone (the audit trail). Vendor emails redacted on `main` (S6); company name redacted in the export (R2) |
| `docs/status/` (105 files: status blocks and verifier reports) | **redact** (export) | the independent verification record. Company name and code names redacted (R2); the SSD path is kept (S16) |
| `docs/cost-log.md`, `docs/cost-log.csv` | **keep** | transparency of compute use (list prices; the plan is a subscription) |
| `orchestrate.sh`, `run_track.sh` | **keep** | orchestration scripts (adapted from TrafficTwin, Apache-2.0). They never push |
| `logs/` including `logs/orch/` | **drop** (not tracked) | raw run transcripts with absolute paths and session detail; gitignored, so already out of the repository |
| audio, video, renders (`movies/`, `film/renders/`, `film/audio/`), model caches, `runs/` (about 5.0 GB), `judge/` copies (about 870 MB) | **out** (not tracked) | link to the published film; the full run archive goes to Zenodo (DOI placeholder in `reproduce.md`, Q8). Nabrah attribution goes with any published audio |
| `docs/publish/figure-inputs/` (106 run-output files, 21.6 MB, `SHA256SUMS`, README) | **keep** (new, Q8) | 106 files, 21.6 MB; the figure inputs: the part of `runs/` that `common.figures build` reads; list with sizes in §9 |
| `film/` scripts, storyboard, subtitles and subtitle QA screenshots | **keep** | text and QA evidence; no audio or video |
| `common/fonts/` (Noto Sans, Noto Naskh Arabic) | **keep** | SIL OFL 1.1; the OFL texts ship beside the fonts |
| `.env` (untracked) | **out** | gitignored; never read |

**Licence check of every committed dataset** (licence and openness register `docs/licences.csv`, 290 rows; blocker list `docs/licences-blockers.md`):

- OpenStreetMap-derived files (lines, stations, alignment sidecars, zones): ODbL 1.0. Credit "(c) OpenStreetMap contributors" appears on every map and in `NOTICE`, and derived databases stay ODbL.
- GASTAT tables: as above. Copernicus DEM, WorldPop, ESA WorldCover, UN WPP and Microsoft buildings feed derived tables only; the raw files are not committed. Their attribution is in `NOTICE` and `docs/credits.md`.
- **Cannot be redistributed or must stay out:** the two news-page copies and the four DataPulse relays above (drop); Transit Costs Project data (hard stop, unused, register row 189); Coqui XTTS-v2 (non-commercial, unused, row 94); Google Maps (visual checks only, nothing committed); the paid narration audio (not in the repository; publish only with the credit). The register still marks the citypopulation.de transcriptions as "licence unclear". They are population figures (facts), cited under the 7 Nov academic-practice decision, and no page content is reproduced.
- `docs/licences-blockers.md`: 2 BLOCKER rows (94, 189), both unused, unchanged by this run.

**Export redaction R2 (recommended; widened by FIX_EXPORT_NAMES, 12 Nov 2026).** In the export only, every term in the gitignored private-name list (`.publish/private-names.txt`, mode 600; 15 lines for 14 terms) is replaced: the author's company name becomes "the author's company", every other term becomes "[private name]". No tracked file names any term (a test checks this whenever the list is present), so the export normally has nothing to redact; R2 is the safety net. The command is in §7 and in `scripts/publish_export.sh`. The export dry run (§6) shows that the tests stay green after it.

## 3. TrafficTwin dependency

See [`traffictwin.md`](traffictwin.md) and [`traffictwin-references.csv`](traffictwin-references.csv): 553 referencing lines in 246 files (regenerated by PUBLISH_EXPORT after Q6 and its CHANGELOG and STATUS entries), each with its kind. The only run-time code path is the optional Jeddah coupling (`coupling/jeddah.py`), and its test skips without the checkout; the checkout path is now overridable by `TRAFFICTWIN`. The OSM extracts are public Geofabrik downloads. Nothing new was vendored (Q6: TrafficTwin stays private; it is an optional private companion, not required). The clean clone below ran with no TrafficTwin and no symlinks. This run wrote nothing to TrafficTwin and ran nothing there.

## 4. CP7 publication items cleared

- Policy brief and report front matter: the CP6 draft banner ("not for circulation") became a public-release banner: reviewed at CP6, prepared for release at CP7, an independent simulation on synthetic uncalibrated demand, not a government plan (1c6e9db).
- Executive summaries: public-use wording, plus **"native Saudi review of the Arabic text is still pending; where the two differ, the English text and the registers govern"**. Bilingual check 273 = 273 numeric tokens; RTL bidi probe 0 wrong at 900/480/360 px; the HTML render and page-1 shot were regenerated (1c6e9db, 32884cd). The film's Arabic rows keep `native_review = pending` (`docs/film.md` §8).
- `CODE_OF_CONDUCT.md`, `SECURITY.md`: PUBLISH_PREP left one grep-able contact placeholder; PUBLISH_EXPORT filled it with GitHub private vulnerability reporting (Q1, §8).
- CP6 closure: your R8-checkpoint review on 5 Nov 2026 and the R9 approval on 7 Nov 2026 were read as closing CP6. **Confirmed: CP6 is closed (Tariq, 12 Nov 2026, Q2).** The banners' wording ("reviewed at CP6, prepared for public release at CP7") stands.

## 5. README and companion files

`README.md` rewritten as a "Try it" page with: the disclaimer, a one-paragraph headline result sourced to the executive summary and the runs, quick start, expected demo output, skips explained, repository map, figure reproduction ([`reproduce.md`](reproduce.md)), credits (Claude; Nabrah on published audio; OSM, GASTAT, TrafficTwin), licence and citation. `CITATION.cff` is set to version "unreleased (prepared after tag r10-final)" and is valid per cffconvert (schema 1.2.0). `CONTRIBUTING.md` v1.1 covers fresh-clone behaviour and skips. `LICENSE` (Apache-2.0) and `NOTICE` are unchanged.

## 6. Proof that it runs clean

**Run A: README verbatim, clean environment (commit 85afd41, 12 Nov 2026; re-run as A2 on 76bb464 below).** `git clone` from the local path into a fresh folder under `$TMPDIR` (not under the repository and not on the SSD). Each command ran as `env -i PATH=<dir holding only uv>:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin HOME=<empty temp folder> bash -c '<command>'`. The empty `HOME` means there is no `.env`, no `RAILTWIN_RUNS_ROOT`, no uv or model cache, no TrafficTwin at its default path and no `data/` symlinks. Python 3.12 came from Homebrew; uv downloaded the locked packages (the only network use).

| step | command | exit | wall time |
|---|---|---|---|
| clone | `git clone <local path> KSA-RailTwin` | 0 | 2 s |
| setup | `make setup` | 0 | 28 s |
| test | `make test` (ruff check, ruff format check: 819 files, pytest, docver: 414 files, manifest `--allow-missing`: 388 rows) | 0 | 120 s |
| demo | `make demo` | 0 | 2 s |
| evidence (not a README step) | `uv run pytest -o addopts= -q -rs -p no:cacheprovider` (to print the counts that `-q -q` hides) | 0 | 44 s |

- **pytest: 920 passed, 154 skipped, 0 failed.** Every skip prints its reason: 140 need the gitignored run outputs (`runs/`), 6 need local OSM data under `data/`, 5 need a usable headless Chrome (it cannot start under an empty `HOME`; it is installed on this Mac), 2 need the film renders, and 1 needs the TrafficTwin checkout. **No test needs an API key, and none calls a paid API.**
- Demo output as in the README ("dashboard API: 7 endpoints answered (7 carry a label); web app not built"); outputs under `runs/demo/`.
- No model download: after the run, the temporary `HOME` held only the uv package cache and a matplotlib font cache.
- Two earlier preliminary runs found 6 failures: the Chrome-driven bidi tests, and a film test that read `runs/` without a skip marker. Fixed in 897bd30 (skip, not fail). The first export dry run then found 2 more: Chrome passed the about:blank check and then failed on the real page, and a GASTAT test read a dropped relay. Fixed in 76bb464 (the Chrome process error now skips; the relay tests skip when the file is absent).
**Run A2: README verbatim again, on the final code commit 76bb464** (same clean environment; run alongside B2, so the times include contention): clone 2 s, `make setup` 17 s, `make test` 146 s, `make demo` 2 s, all exit 0; **pytest 920 passed, 154 skipped, 0 failed**, with the same skip classes as Run A (140 `runs/`, 6 local data, 5 Chrome, 2 film renders, 1 TrafficTwin).

**Run B2: export dry run (Option B, §7) on 76bb464.** The §7 block ran verbatim with `EXPORT` set to a fresh `$TMPDIR` folder and a placeholder public email. It removed the 6 files in `export-exclude.txt` (1,884 → 1,878 files), applied redaction R2 (the residue check printed nothing) and made one squashed commit, and gitleaks on it found no leaks. A clean clone of that export, in the same clean environment: `make setup` 25 s, `make test` 136 s, `make demo` 2 s, all exit 0; **pytest 914 passed, 160 skipped, 0 failed**. The 6 extra skips are the relay test (file dropped) and run-scoped guards whose start commit is not in a squashed history ("start HEAD not in this clone"). No export branch or folder was created in the repository or at the §7 paths. The dry-run folder lived only under `$TMPDIR`.

All temporary clones and the dry-run export were deleted afterwards, from inside the temporary folder.

## 7. Push steps for Tariq (text only; nothing here was run on the real paths)

**PUBLISH_EXPORT:** the Option B block below now lives in `scripts/publish_export.sh` (same steps, plus logs, a text-files-only R2 and a fixed commit date). It was run on the real export path; see §10. The block below is kept as the PUBLISH_PREP record.

**Repository (Tariq, 12 Nov 2026):** `https://github.com/alturkestani/KSA-RailTwin`. This URL is in `README.md` (CI badge, clone command, licence section) and in `CITATION.cff` (`repository-code`, `url`). Nothing was checked online: this run made no call to GitHub, added no remote and pushed nothing. **If the rename from `-KSA-RailTwin` to `KSA-RailTwin` has not happened yet**, either rename it first on github.com (Settings → Repository name), or run the same commands below with `-KSA-RailTwin` in place of `KSA-RailTwin` in the URL and change the URL in `README.md` and `CITATION.cff` to match before the commit. **Visibility:** keep it private until the README, the Arabic files and CI render and pass on GitHub, then switch it to public.

Two variants. **Which one applies, from the §1 scan: variant (b).** History is not clean for publication: home paths (S5), third-party vendor emails (S6 redacted on `main` but still in history, S7) and the author's email on every commit and tag (S10) are in `main`'s history. None is a secret, but all of them would be published by a push of `main`. So **do not push `main` and do not push tags.**

**Variant (a): history clean → push `main` and the tags.** *Does not apply* (see above). It is here for completeness, in case you decide that S5, S6, S7 and S10 are acceptable to publish (they are in history only; HEAD is clean of them). Note that pushing `main` would also publish the §2 drop-list files and the private names that redaction R2 removes, because those changes exist only in the export:

```bash
# --- Variant (a): ONLY if you accept publishing main's full history (not recommended; the scan says (b)) ---
cd ~/Documents/Projects/KSA-RailTwin
git remote add origin https://github.com/alturkestani/KSA-RailTwin
git push -u origin main
git push origin --tags
```

**Variant (b): anything sensitive in history → push the clean public export, never `main`.** This applies. Create the export exactly as PUBLISH_PREP proposed, in the form you choose: **Option B (recommended): a separate export folder with one squashed commit**, or Option A: an orphan branch. Option B keeps the private repository and its history untouched; only the reviewed tree leaves the machine, and the S5, S6, S7 and S10 history items stay behind.

```bash
# --- Option B: separate export folder, one squashed commit (recommended) ---
# SRC = the private repository; EXPORT = a new folder (must not exist); COMMIT = what you publish.
SRC=${SRC:-~/Documents/Projects/KSA-RailTwin}
EXPORT=${EXPORT:-~/Documents/Projects/KSA-RailTwin-public}
COMMIT=${COMMIT:-$(git -C "$SRC" rev-parse main)}
test ! -e "$EXPORT" || { echo "$EXPORT exists; choose another folder" >&2; exit 1; }
mkdir -p "$EXPORT"
git -C "$SRC" archive --format=tar "$COMMIT" | tar -x -C "$EXPORT"
cd "$EXPORT"
# 1. Drop the files listed in docs/publish/export-exclude.txt (they stay on the private main).
grep -v '^#' docs/publish/export-exclude.txt | sed '/^$/d' | while read -r f; do rm -v -- "$f"; done
# 2-3. Redaction R2 and the residue check read the gitignored private-name list; no name is
#      written here. Use scripts/publish_export.sh, which does steps 1-5 (PRIVATE_NAMES points
#      to the list; default $SRC/.publish/private-names.txt), or build the pattern yourself:
NAMES="($(grep -v '^#' "$SRC/.publish/private-names.txt" | sed '/^$/d' | cut -f1 | sed 's/ /[ _-]?/g' | paste -sd'|' -))"
grep -rnIiE "$NAMES|/Users/[a-z]|/home/[a-z]|[A-Za-z0-9._%+-]@(nabrah|dscan)\.ai" . | head   # must print nothing after R2
# 4. One squashed commit under your public identity.
git init -q -b main
git config user.name "Tariq Alturkestani"
git config user.email "${PUBLIC_EMAIL:-<your public or GitHub noreply address>}"
git add -A
git commit -q -m "KSA Rail Twin: public release (squashed from private main $(git -C "$SRC" rev-parse --short "$COMMIT"))"
# 5. Secret scan of the export (expect: no leaks found).
gitleaks git --no-banner --redact=100 -c .gitleaks.toml .
```

Then check a fresh clone of the export, and push it:

```bash
cd "$(mktemp -d)" && git clone ~/Documents/Projects/KSA-RailTwin-public check && cd check
make setup && make test && make demo          # expect: all exit 0 (§6 timings)
cd ~/Documents/Projects/KSA-RailTwin-public
git remote add origin https://github.com/alturkestani/KSA-RailTwin            # after creating the repository on github.com
git push -u origin main                         # main of the EXPORT folder (one squashed commit), not the private main
```

Contact (Q1) and `CITATION.cff` `version` 1.0.0 / `date-released` 2026-11-12 (Q7) are set on `main` by PUBLISH_EXPORT, so the export carries them; `repository-code` and `url` were already set. Push no tags from the export (it has none) and never add this remote to the private repository.

**Option A (variant (b) as an orphan branch in the private repository).** This needs git ≥ 2.42 (2.52 here). It is riskier: the private history sits beside the public branch, the `git remote add` below writes the remote into the private repository's shared config (worktrees share it), and a mistaken `git push --all`, `--tags` or `git push origin main` would then publish the private history.

```bash
cd ~/Documents/Projects/KSA-RailTwin
git worktree add --orphan -b public ../KSA-RailTwin-public-wt
cd ../KSA-RailTwin-public-wt
git -C ~/Documents/Projects/KSA-RailTwin archive main | tar -x
# then steps 1-3 of Option B (drop list, redaction R2, residue check), then:
git add -A && git commit -m "KSA Rail Twin: public release"
git remote add origin https://github.com/alturkestani/KSA-RailTwin            # after creating the repository on github.com
git push origin public:main                     # push only this branch; never --all, never --tags, never main
```
## 8. Open questions for Tariq

1. **Q1 Contact:** which contact goes into `SECURITY.md` and `CODE_OF_CONDUCT.md` (`grep -n MAINTAINER-CONTACT *.md`)? GitHub's private vulnerability reporting is one option for security; a project email is another. **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** GitHub private vulnerability reporting (Security tab), no email. `SECURITY.md` v1.2 and `CODE_OF_CONDUCT.md` v1.2 now name it, with the form URL; the placeholder is gone. **Before pushing:** it works only once enabled on github.com (repository Settings → Code security → Private vulnerability reporting → Enable); see §7.
2. **Q2 CP6:** confirm that CP6 is closed (the banners now say "reviewed at CP6, prepared for public release at CP7"). **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** CP6 is closed. Recorded in §4 and in the `docs/STATUS.md` milestone table (R8 row); the banners are unchanged.
3. **Q3 Audit trail:** publish `CLAUDE.md`, `.claude/`, `prompts/`, `docs/status/` and the cost log (recommended, with redaction R2), or keep some of them out of the export? They name Claude model ids and include the run budgets. **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** publish `CLAUDE.md`, `.claude/`, `prompts/`, `docs/status/` and the cost log, with redaction R2. The §2 rows for them are "redact (export)" or "keep" and are unchanged; the export applies R2 to them (§7, §10).
4. **Q4 Third-party name (S15):** keep the vendor executive's name as the licence-evidence citation, or replace it with the company and role? **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** replace the name with company and role. Done on `main` in the 8 files of S15 (the two verbatim prompts get a header note); `git grep -i` for the surname now finds nothing. The report annex was rebuilt (`common.report build`; only the index hash line changed besides the row).
5. **Q5 DataPulse relays:** drop them as proposed, or keep them if you can confirm DataPulse's terms? **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** drop the relays and cite GASTAT directly. The four files stay in `export-exclude.txt`. On `main`: source row S-cp2-gastat-001 says "superseded for citation" and points to S-cp2-gastat-007/008/002/003 (identical values, C-gastat-001); A-jazan-003 and A-screen-035 now cite GASTAT (S-cp2-gastat-003, -007); the licence row status and `data/ksa/tables/gastat/README.md` note the drop; `index.md`, `licences.md` and the report annexes were regenerated. The region registers and the code keep the id S-cp2-gastat-001 as provenance (the values were read from the relay, identical to GASTAT); rewriting them would change committed study inputs.
6. **Q6 TrafficTwin:** will TrafficTwin Jeddah be public? The README, `NOTICE`, `CITATION.cff` and licence row 16 link `github.com/alturkestani/TrafficTwin`; if it stays private, that link will not resolve and the optional coupling cannot be reproduced. Vendoring its schema (Apache-2.0) is possible on your word. **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** TrafficTwin stays private for now. `README.md`, `CONTRIBUTING.md` v1.2, `NOTICE` (both TrafficTwin paragraphs) and `CITATION.cff` (reference entry: no URL; notes) now call it "the author's optional private companion project (not public; not required to run, test or reproduce this repository)" and no longer link it; licence rows 16, 156 and 287 keep the URL as provenance, labelled "private repository; optional companion; not public; not required". Nothing vendored. Verbatim records (`PROJECT.md`, `prompts/`, `docs/status/`) and the manifest rows keep the URL as written. Reference table regenerated (551 lines in 246 files).
7. **Q7 Release metadata:** version string (for example `1.0.0`) and release date for `CITATION.cff` (the repository URL is set: §7), and the public commit identity (name plus a public or GitHub noreply email). **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** version 1.0.0, date 2026-11-12 (`CITATION.cff`, cffconvert valid; `CHANGELOG.md` 1.0.0 section); public identity `Tariq Alturkestani <alturkestani@users.noreply.github.com>` for the squashed export commit. **Noreply form (not checked online):** GitHub accepts the plain `<username>@users.noreply.github.com` form only for accounts whose noreply address was set before mid-2017; newer accounts use `<ID>+<username>@users.noreply.github.com`, where `<ID>` is the numeric account id shown at github.com → Settings → Emails. The export uses the form Tariq gave. **Flag:** if GitHub shows the export commit as unlinked (no avatar, author not clickable) after the push, or rejects the push under email privacy, amend the export commit with the ID-prefixed form before (or instead of) the push, in one command (text only; replace `<ID>`): `GIT_COMMITTER_EMAIL="<ID>+alturkestani@users.noreply.github.com" git -C ~/Documents/Projects/KSA-RailTwin-public commit --amend --no-edit --author="Tariq Alturkestani <<ID>+alturkestani@users.noreply.github.com>"` (then push with `--force-with-lease` if it was already pushed; see §10).
8. **Q8 Run archive:** publish `runs/` (about 5.0 GB) and the judge copies (about 870 MB) for an exact figure rebuild (`reproduce.md`, level 2)? They would need splitting below GitHub's 2 GiB per-asset limit, or a data host such as Zenodo. A smaller subset (the figure inputs only) is another option. **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** ship only the figure inputs; Zenodo placeholder for the full `runs/` archive. The 106 files (21,647,100 bytes: the 105 the build reads plus the L1 `score.json` that fig06's numbers come from, §9; largest 11,093,472 bytes, well under GitHub's 50 MB warning and 100 MB limit) are committed under `docs/publish/figure-inputs/runs/…` (outside `runs/`, which rule 8 and `tests/test_hygiene.py` keep untracked), with `SHA256SUMS`, a README and licence register row 291. `reproduce.md` v1.1 has the new level 2 (figure inputs, exact) and level 3 (full archive on Zenodo: `10.5281/zenodo.[TO BE FILLED BY THE AUTHOR]`). List with sizes and the method in §9.
9. **Q9 Native review:** who does the native Saudi review of the Arabic summary and film, and does publication wait for it? Today it is disclosed as pending. **Answered (Tariq, 12 Nov 2026), applied by PUBLISH_EXPORT:** publish the code now with "native Saudi review pending"; the films wait for the review. Recorded as "code published; native Saudi review of the Arabic pending; films follow the review" in the README (release-status note under the disclaimer), `CITATION.cff` (message), `CHANGELOG.md` and `docs/film.md` v1.11 (new top section and §8). No reviewer was contacted; Tariq arranges the review.

## 9. Figure inputs shipped (Q8, PUBLISH_EXPORT, 12 Nov 2026)

"Figure inputs" = the files under the author's `runs/` that `uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/` (the command in `reproduce.md`) opens, lists or globs. Method: one build on the full `runs/` under a Python audit hook (open, listdir, scandir, glob, stat) plus wrappers on the parquet, CSV and GeoJSON readers gave 105 files. Plus `runs/r6/top5/L1/score.json` (64,957 bytes): the source of fig06's framing numbers, checked by `tests/test_report_figures.py`, which failed instead of skipping without it in the first clean-clone run (§10); 106 files, 21,647,100 bytes. Check: a fresh `git archive` tree with only those 105 files rebuilt all 33 report outputs and all 33 deck outputs byte-identical (`cmp`). Scan: no home or volume path, email address or private name in them. They are committed under `docs/publish/figure-inputs/`, paths mirroring `runs/` (README there; `SHA256SUMS`; licence register row 291, "KSA Rail Twin figure inputs"). By directory: `runs/cba` 80 files 20,933,823 bytes; `runs/r7` 3 files 355,491; `runs/r6` 11 files 242,558; `runs/access` 8 files 75,151; `runs/r2` 4 files 40,077. Everything else under `runs/` (about 5.0 GB) and `judge/` (about 870 MB) stays out: Zenodo, DOI to be filled by Tariq (`reproduce.md` level 3).

<details><summary>All 106 files with sizes</summary>

| file (under `docs/publish/figure-inputs/`) | bytes |
|---|---:|
| `runs/access/S0/jeddah/isochrone_door_to_door.geojson` | 11,339 |
| `runs/access/S0/reached.parquet` | 10,133 |
| `runs/access/S1/dammam/isochrone_door_to_door.geojson` | 2,581 |
| `runs/access/S1/jeddah/isochrone_door_to_door.geojson` | 15,208 |
| `runs/access/S1/meta.json` | 1,632 |
| `runs/access/S1/reached.parquet` | 10,337 |
| `runs/access/S5-station_addition-dhahran/dammam/isochrone_door_to_door.geojson` | 13,031 |
| `runs/access/S5-station_addition-dhahran/reached.parquet` | 10,890 |
| `runs/cba/CBA-S1-committed-programme/draws.parquet` | 11,093,472 |
| `runs/cba/CBA-S1-committed-programme/meta.json` | 3,467 |
| `runs/cba/CBA-S1-committed-programme/results.json` | 133,252 |
| `runs/cba/CBA-S1-committed-programme/switching_values.json` | 656 |
| `runs/cba/CBA-S1-committed-programme/tornado.csv` | 1,641 |
| `runs/cba/CBA-S2-trunk_gap-abha-khamis-mushait-bisha/results.json` | 133,452 |
| `runs/cba/CBA-S2-trunk_gap-abha-khamis-mushait-najran/results.json` | 133,551 |
| `runs/cba/CBA-S2-trunk_gap-al-jubayl-hafar-al-batin/results.json` | 133,158 |
| `runs/cba/CBA-S2-trunk_gap-al-kharj-bisha/results.json` | 133,646 |
| `runs/cba/CBA-S2-trunk_gap-ar-rass-ha-il/results.json` | 133,470 |
| `runs/cba/CBA-S2-trunk_gap-arar-hafar-al-batin/results.json` | 133,378 |
| `runs/cba/CBA-S2-trunk_gap-buraidah-ha-il/results.json` | 133,310 |
| `runs/cba/CBA-S2-trunk_gap-buraidah-hafar-al-batin/results.json` | 133,266 |
| `runs/cba/CBA-S2-trunk_gap-dammam-khobar-dhahran-al-kharj/results.json` | 133,223 |
| `runs/cba/CBA-S2-trunk_gap-jazan-najran/results.json` | 133,460 |
| `runs/cba/CBA-S2-trunk_gap-jeddah-yanbu/results.json` | 133,102 |
| `runs/cba/CBA-S2-trunk_gap-madinah-ar-rass/results.json` | 133,064 |
| `runs/cba/CBA-S2-trunk_gap-madinah-ha-il/results.json` | 132,994 |
| `runs/cba/CBA-S2-trunk_gap-madinah-yanbu/results.json` | 133,037 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-al-jubayl/results.json` | 133,063 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-bisha/results.json` | 133,436 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-dammam-khobar-dhahran/results.json` | 133,097 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-hafar-al-batin/results.json` | 132,891 |
| `runs/cba/CBA-S2-trunk_gap-riyadh-jeddah/results.json` | 132,988 |
| `runs/cba/CBA-S2-trunk_gap-sakaka-ha-il/results.json` | 133,684 |
| `runs/cba/CBA-S2-trunk_gap-tabuk-sakaka/results.json` | 133,510 |
| `runs/cba/CBA-S2-trunk_gap-tabuk-yanbu/results.json` | 133,707 |
| `runs/cba/CBA-S2-trunk_gap-taif-bisha/results.json` | 133,272 |
| `runs/cba/CBA-S3-branch_spur-al-jubayl/results.json` | 132,219 |
| `runs/cba/CBA-S3-branch_spur-al-kharj/results.json` | 132,264 |
| `runs/cba/CBA-S3-branch_spur-al-kharj/switching_values.json` | 653 |
| `runs/cba/CBA-S3-branch_spur-al-kharj/tornado.csv` | 1,622 |
| `runs/cba/CBA-S3-branch_spur-al-ula/results.json` | 133,378 |
| `runs/cba/CBA-S3-branch_spur-ar-rass/results.json` | 132,697 |
| `runs/cba/CBA-S3-branch_spur-arar/results.json` | 133,353 |
| `runs/cba/CBA-S3-branch_spur-at-ta-if/results.json` | 132,647 |
| `runs/cba/CBA-S3-branch_spur-az-zulfi/results.json` | 133,267 |
| `runs/cba/CBA-S3-branch_spur-badr-hunayn/results.json` | 132,954 |
| `runs/cba/CBA-S3-branch_spur-bisha/results.json` | 133,363 |
| `runs/cba/CBA-S3-branch_spur-duruma/results.json` | 132,624 |
| `runs/cba/CBA-S3-branch_spur-hafar-al-batin/results.json` | 133,216 |
| `runs/cba/CBA-S3-branch_spur-hawtat-sudayr/results.json` | 133,776 |
| `runs/cba/CBA-S3-branch_spur-khaybar/results.json` | 133,214 |
| `runs/cba/CBA-S3-branch_spur-rabigh/results.json` | 133,968 |
| `runs/cba/CBA-S3-branch_spur-rafha/results.json` | 133,783 |
| `runs/cba/CBA-S3-branch_spur-rumah/results.json` | 133,140 |
| `runs/cba/CBA-S3-branch_spur-sakaka/results.json` | 132,939 |
| `runs/cba/CBA-S3-branch_spur-tayma/results.json` | 134,142 |
| `runs/cba/CBA-S3-branch_spur-yanbu-al-sina-iyah-yanbu-ind/results.json` | 133,063 |
| `runs/cba/CBA-S4-commuter_belt-abha-khamis-mushait-045/results.json` | 133,303 |
| `runs/cba/CBA-S4-commuter_belt-abha-khamis-mushait-135/results.json` | 133,244 |
| `runs/cba/CBA-S4-commuter_belt-buraidah-090/results.json` | 133,002 |
| `runs/cba/CBA-S4-commuter_belt-buraidah-180/results.json` | 132,376 |
| `runs/cba/CBA-S4-commuter_belt-dammam-khobar-dhahran-180/results.json` | 132,818 |
| `runs/cba/CBA-S4-commuter_belt-dammam-khobar-dhahran-315/results.json` | 132,458 |
| `runs/cba/CBA-S4-commuter_belt-jazan-090/results.json` | 132,469 |
| `runs/cba/CBA-S4-commuter_belt-jazan-315/results.json` | 132,599 |
| `runs/cba/CBA-S4-commuter_belt-jeddah-000/results.json` | 133,438 |
| `runs/cba/CBA-S4-commuter_belt-jeddah-315/results.json` | 133,615 |
| `runs/cba/CBA-S4-commuter_belt-madinah-045/results.json` | 133,035 |
| `runs/cba/CBA-S4-commuter_belt-madinah-225/results.json` | 133,225 |
| `runs/cba/CBA-S4-commuter_belt-makkah-045/results.json` | 132,661 |
| `runs/cba/CBA-S4-commuter_belt-makkah-090/results.json` | 132,783 |
| `runs/cba/CBA-S4-commuter_belt-makkah-315/results.json` | 133,430 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-000/results.json` | 132,855 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-090/results.json` | 132,715 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-135/results.json` | 132,859 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-225/results.json` | 132,627 |
| `runs/cba/CBA-S4-commuter_belt-riyadh-270/results.json` | 132,910 |
| `runs/cba/CBA-S5-station_addition-al-jarn/results.json` | 131,373 |
| `runs/cba/CBA-S5-station_addition-al-jubayl-royal-commission/results.json` | 131,662 |
| `runs/cba/CBA-S5-station_addition-al-jubayl/results.json` | 131,693 |
| `runs/cba/CBA-S5-station_addition-al-oyun/results.json` | 131,349 |
| `runs/cba/CBA-S5-station_addition-al-qarah/results.json` | 131,393 |
| `runs/cba/CBA-S5-station_addition-al-umran/results.json` | 131,393 |
| `runs/cba/CBA-S5-station_addition-az-zulfi/results.json` | 130,901 |
| `runs/cba/CBA-S5-station_addition-dhahran/results.json` | 130,588 |
| `runs/cba/CBA-S5-station_addition-duruma/results.json` | 131,001 |
| `runs/cba/CBA-S5-station_addition-jubail-two-stations/results.json` | 131,626 |
| `runs/cba/CBA-S5-station_addition-thuwal/results.json` | 131,893 |
| `runs/r2/long-list/counts.json` | 893 |
| `runs/r2/score/meta.json` | 731 |
| `runs/r2/score/scores.parquet` | 34,044 |
| `runs/r2/score/summary.json` | 4,409 |
| `runs/r6/l6/meta.json` | 706 |
| `runs/r6/l6/score/S6-L6.csv` | 3,784 |
| `runs/r6/l6/score/meta.json` | 1,056 |
| `runs/r6/l6/search.json` | 161,163 |
| `runs/r6/pareto_front.csv` | 3,138 |
| `runs/r6/top5/L1.layout.yaml` | 268 |
| `runs/r6/top5/L1/meta.json` | 976 |
| `runs/r6/top5/L1/score.json` | 64,957 |
| `runs/r6/top5/L2.layout.yaml` | 224 |
| `runs/r6/top5/L3.layout.yaml` | 269 |
| `runs/r6/top5/top5.csv` | 6,017 |
| `runs/r7/fiscal/fiscal.json` | 333,726 |
| `runs/r7/fiscal/meta.json` | 719 |
| `runs/r7/vfm/vfm.json` | 21,046 |
| **total: 106 files** | **21,647,100** |
</details>


## 10. The public export (PUBLISH_EXPORT, 12 Nov 2026): how it was built, and the two push commands

**Built with** `scripts/publish_export.sh` (Option B; `SRC` = this repository, `EXPORT=~/Documents/Projects/KSA-RailTwin-public`, `PUBLIC_NAME="Tariq Alturkestani"`, `PUBLIC_EMAIL=alturkestani@users.noreply.github.com`, logs in `logs/publish-export/`, gitignored). The script:

1. refuses an existing folder, then extracts `git archive <source commit>` into it (a new standalone repository: `git init`, never a worktree or branch of this one);
2. removes the 7 files in `export-exclude.txt` (2 news pages, 4 DataPulse relays and, since FIX_EXPORT_NAMES, the prompt `prompts/FIX_EXPORT_NAMES.md`, which quotes the private-name list);
3. applies redaction R2 to **text files only** (`grep -I`; binaries, fonts, images and PDFs are never edited; a binary that contains a term stops the build and is listed in `logs/publish-export/skipped-binary.txt`), using every term of the gitignored list `.publish/private-names.txt` (case-insensitive, substring-wide; the replacement is the list's own TAB column, by default "[private name]");
4. runs the residue grep over text files, the text of every PDF (`pdftotext`) and the XML inside every xlsx/docx/pptx (must print nothing; the script stops otherwise), and after the commit a `git grep -i` of the commit;
5. makes one commit under the public identity, with a fixed date (2026-11-12 12:00 +03:00): no remote, no tag;
6. runs gitleaks with `.gitleaks.toml`.

FIX_EXPORT_NAMES (12 Nov 2026) moved every name out of the script, this checklist and every other tracked file, and rebuilt the export from scratch; the export's copies of the script and the checklist hold no name, not even in a pattern. The list itself stays only in the gitignored `.publish/private-names.txt` on this Mac.

**Before the push (Tariq):**
- On github.com, enable private vulnerability reporting (repository Settings → Code security → Private vulnerability reporting), so the Q1 contact works.
- Q7 noreply form: see §8 Q7. If GitHub shows the commit as unlinked, run the one amend command given there in the export folder.
- Q8: deposit the run archive on Zenodo and fill the DOI placeholder in `docs/publish/reproduce.md` (in the export folder, as a second commit, or on `main` and rebuild the export).
- Q9: the films stay unpublished until the native review.

**The two push commands (text only; not run; run them from the export folder, never from this repository):**

```bash
git -C ~/Documents/Projects/KSA-RailTwin-public remote add origin https://github.com/alturkestani/KSA-RailTwin
git -C ~/Documents/Projects/KSA-RailTwin-public push -u origin main
```

Push no tags (the export has none), and never add this remote to the private repository.
