> **Document version:** prompts/FIX_LICENCE_CITE_FACTS.md v1.0 | 7 Nov 2026 | Author: Tariq (verbatim; header and a short coordinator addendum added) | Status: active

# FIX_LICENCE_CITE_FACTS — register only, after FIX_R9_COUNTS has stopped and been verified. One short run on main, Opus, USD 60 guard, verifier inside, then stop. No tag, no push, no remote, no R10, no film, no code or test changes unless a status-count test asserts the BLOCKER total you are correcting (then update that assertion to the measured value). This supersedes the unsent FIX_LICENCE_PRESS_FACTS prompt.

Tariq's decisions, 7 Nov 2026 AST (academic research practice):
1. Citing a published fact with its URL and access date is enough; no permission is needed when no text, table or image is reproduced. Subscriber/paywalled content remains unused.
2. Accessing a public page or dataset and creating study tables from it, with citation, is approved the same way. This includes transcribed or derived tables already in the docs.
3. Public citation of Claude (the orchestrator and coding assistant) is approved. Keep raw model ids out of the public register row unless they already appear there; name the tool, not a hidden mapping.
4. Public attribution of Nabrah is approved and will accompany published Nabrah audio. That is the owner answer to B9.

Apply (1) and (2) to these BLOCKER rows, recording approval (Tariq, 7 Nov 2026 AST) and using the same clearing method as the Google Chrome row closed on 4 Nov 2026:
Press and secondary fact pages: 117, 118, 119, 120, 121, 122, 123, 127, 132, 136, 141, 148, 149, 168, 188, 204, 221, 234, 235, 237, 263.
Statistical extracts and data tables: 7, 125, 183, 191, 193, 194, 195, 196, 262.
EPSG (203): CRS definitions read through PROJ/pyproj only; the dataset is not redistributed.
CC BY-SA fact tables: 133, 146, 147, 197, 236, 238 (cited facts and study tables only; do not add a new derived heritage database or map layer in this run).
Other citation rows: 201 (xlogit: citation of the unused candidate is approved; do not install it; leave the MIT vs GPL conflict unresolved and unused), 205 (Schittenhelm), 260 (CE Delft handbook).
Models named for credit: 1 (Claude: public citation approved; rename or word the public row so Claude may be credited), 153 (Nabrah: B9 answered as "attribute Nabrah"; do not change the written publication/broadcast clearance or the no-cloning rule).

OSM sidecars (246 and 290): do not leave the Produced Work vs Derivative Database question open. Record: OSM credit is required on every map; the committed alignment sidecars (cities/ksa/alignments/ and alignments-v2/) are released as ODbL share-alike derived databases. That answers B7 and should remove the BLOCKER grade if the release rule agrees; do not invent a new licence.

Do not lift the Transit Costs hard stop (189). It stays unused: no figure, table or benchmark from it. You may note that citing the excluded source (searched, not used) is approved. Do not regrade it as cleared for use.
Do not clear XTTS-v2 (94) for any commercial or public-release use. It stays out (CPML is non-commercial).

Regenerate docs/licences-blockers.md with `uv run python -m common.licence_blockers write` and update the BLOCKER count wherever status or the release note states 46. Expected remaining BLOCKER rows: 189 (Transit Costs, unused/hard stop) and 94 (XTTS-v2, non-commercial), unless the generator measures a different total — report the measured count, do not invent one.

Do not change the README body, credits prose, executive summaries, film/, R8, or the RJ study, except register/status/release-note count and wording required by the rows above. Do not create tag r9. Do not kill processes you did not start.

Save this prompt verbatim with a version header as prompts/FIX_LICENCE_CITE_FACTS.md. Verifier PASS, then stop.

Coordinator addendum (7 Nov 2026): FIX_R9_COUNTS stopped at 01:58 and was verified (PASS pass 2; main at 6c67b8f). Row numbers above are `docs/licences.csv` row numbers as `docs/licences-blockers.md` v1.1 and `docs/licences-release.md` §5 print them: confirm each row's item name before editing and list id → item in the status block; if a number does not match the group Tariq names it under, stop on that row and report rather than guess. Clearing method = the Chrome precedent: approval column "Tariq, 7 Nov 2026 AST (citation of published facts / study tables; FIX_LICENCE_CITE_FACTS)", status text updated, no licence field invented; `common.sources.release_status` decides the grade, so if a row stays BLOCKER after the approval text, say why instead of editing the rule to force it, and report it. Regenerate `docs/licences.md` (`common.licences sync`), `docs/licences-release.md`, `docs/licences-blockers.md`, `docs/credits.md`/`NOTICE` (`make credits`, generated prose only) and the report source/licence annexes only if a generator requires it; the Chrome-era test that allows only named rows to differ from tag r8 (`tests/test_fix_r8.py`) must be widened to exactly this run's row list, not disabled. Status block in `docs/status/main.md`, ending `FIX_LICENCE_CITE_FACTS: done` or `FIX_LICENCE_CITE_FACTS: blocked - <reason>`; verifier label `VERIFY_FIX_LICENCE_CITE_FACTS` (foreground; it checks every row in the list and that no row outside it changed, the measured BLOCKER total, 189 and 94 still BLOCKER, the OSM/ODbL wording, no code change beyond count assertions, no tag/remote).
