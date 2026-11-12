> **Document version:** prompts/STUDY_RJ_SCORE.md v1.0 | 6 Nov 2026 | Author: Tariq (verbatim; header and a short coordinator addendum added) | Status: active

# STUDY_RJ_SCORE — full-judge v3 scores for the five Riyadh–Jeddah study sketches as Landbridge replacements (one run on main, WT=0, claude-opus-5-5; then STOP)

STUDY_RJ_FAMILIES is accepted (HEAD at start should be 1c2d761 or later with only coordinator bookkeeping). Tariq, 6 Nov 2026: score the study. Then stop.

What to score. Five replacement packages, each one sketch instead of the committed Landbridge:

- S1* + RJ-A (speed-oriented HSR)
- S1* + RJ-B (via Taif, north-around)
- S1* + RJ-C1 (via Taif + gateway SW)
- S1* + RJ-C2 (via Taif + gateway NW)
- S1* + RJ-LB (the announced-stop chain, terrain-routed by us; like-for-like comparator)

S1* means S1 without the committed Landbridge: existing lines + Riyadh Rail Link + the Saudi GCC section. The committed Landbridge stays as it is in S1.yaml and in every published S1 / L1–L5 / R8 figure; you do not rewrite it. RJ-LB is the comparator for this run, not the public SR 100 bn / USD 7 bn figures (C-001) and not the S1 great-circle sketch.

Do not score:
- the existing scenarios/study/rj-*.yaml files as written (each is S1 plus the sketch drawn beside the Landbridge; that would be two Riyadh–Jeddah trunks);
- scenarios/study/all-families.yaml (overlapping inventory, not a programme);
- a stacked "S1 + sketch" sensitivity;
- any new alignment or re-route.

If the frozen adapter always injects S1's Landbridge and you cannot omit it except by editing judge/ or by changing how S1 or L1–L5 are scored, stop and write STUDY_RJ_SCORE: blocked - <reason> rather than stacking or patching the judge.

Rules (Tariq, verbatim in substance): no tag, no push, no R9/R10 (prompts/ and film/ untouched except this prompt if you save it), no licence status change, no paid model or API, no station moved, no new alignment, no interchange threshold changed, do not change the access model, do not write into runs/r6/top5/, do not fold this into the R8 report, summaries, policy brief, figure index or dashboard, do not change any published L1–L5 or S6-L6 number, do not merge the study's S-rj / A-rj rows into the main registers, and do not kill any process you did not start (the coordinator's dashboard on port 8765 and anything on port 8000 are not yours; this run needs no server). TrafficTwin read-only; foreground subagents only; runaway guard single run USD 60 (write your estimate in your first status line; five full-judge layouts, each on the order of two minutes locally). Judges stay frozen: supply inputs through the adapter exactly as R6 / S6_L6_SCORE did; judge hash d9fef643… checked before and after; never edit judge/. One commit per item; status block in docs/status/main.md; end with STUDY_RJ_SCORE: done or STUDY_RJ_SCORE: blocked - <reason>.

How to assemble each package
1. New replacement scenario files under scenarios/study/ (for example rj-a-replace.yaml). Do not turn the existing stacked rj-*.yaml files into scored programmes; leave their notes as "drawn beside, not instead; not scored".
2. Each replacement layout is S1* plus that one corridor, opened in 2030 (the first R6 investment phase) so the five are comparable. Note that the announced Landbridge target is 2034 (secondary). Electrified double-track, as the study already priced them (A-r4-cost-001/002). RJ-A/B/C1/C2 stay line_type hsr; RJ-LB stays mixed.
3. Point each corridor at the routed alignment in cities/ksa/alignments-study/<id>.geojson and the sidecar <id>.json. The study corridor YAML length_km values are the straight end-to-end distances (RJ-A 844.2, not the routed 887.2). Costing, running time and capex in the judge must use the routed length and structure shares from the sidecar, the same figures as docs/rj-routes-study.md §3 and §6. Add an alignment: key or a scoring-specific corridor file if the adapter needs it; do not silently cost the great-circle.
4. Implement Landbridge omission only inside a study scoring path (prefer study/rj.py), opt-in when a study replacement marker is present. Do not change optimise.layout's default "S1 + items" behaviour for R6. Add a test that S1 and a published top-5 layout still include the Landbridge and are byte-unchanged in their line lists.
5. Invoke the same full judge as S6_L6_SCORE: judge v3-variants (sha256 d9fef643…), seed 1, 10,000 draws, --all-cases (horizons × rate cases × the three population cases). Robust NPV = minimum over the population cases at P50 cost. Also report NPV at P90 cost, BCR P10/P50/P90, capex P10/P50/P90, 2050 rail trips and passenger-km, 120-min reach gain for the five metros (A-r6-007), national reach (reported only, A-r6-104), CO2, and HHR loads. There is no Landbridge line in these packages: do not pretend there is a landbridge_pax figure; report the load on the RJ sketch instead. Headline figures are incremental versus S1* (no Landbridge), not versus published S1. Do not put them in a table next to L1–L5 as if they were the same kind of increment (L1–L5 are extras on top of S1-with-Landbridge).
6. Output under runs/study/rj/score/<id>/ (score.json, score.judge.json, meta.json with the judge hash, seed, layout hash and git describe). A small map or scorecard each if cheap. Do not write into runs/r6/top5/ or runs/r6/l6/.

What to write
7. A new "Full-judge score" section in docs/rj-routes-study.md (do not rewrite §§1–6 except to point at the new section). Include: the five-row score table; capex in the judge versus the study's §6 register table (they should match the routed sidecars; explain any difference); the via-Taif trade-off in NPV / reach / HHR load, not only in minutes and capex; the A-r4-acc-004 sentence (the judge still uses the access-model site overrides: Landbridge Jeddah with HHR Al-Sulaimaniyah, GCC Dammam with SAR Dammam — those are not rail-graph interchanges; say how the same Jeddah/Riyadh placeholders apply to the RJ terminals; do not change the access model); both labels plus the alignment limitation; and the quiet siting language already used (through track outside the Haram boundary; no passenger-group vignette). A score: block on each new replacement scenario file, matching score.json.
8. Keep every score labelled "study sketch, not the recommended programme" and "synthetic demand, uncalibrated: scenario comparison, not a forecast". No advocacy ("will transform"). No folding into R8.

Do not change: S1.yaml or the committed Landbridge geometry; HHR; interchange rules; the access model; runs/r6/top5/; runs/r6/l6/; runs/r7/; published L1–L5 or S6-L6 figures; docs/report/; summaries; policy brief; figure index; web/; api/; licences; film/; judge/; the main source/assumption registers; R9/R10.

Coordinator addendum (6 Nov 2026): the baseline S0 and the S1* reference run must come from the same frozen judge in the same invocation family (if the adapter needs an explicit S1* baseline run to compute the increment, write it to runs/study/rj/score/_s1-star/ and say so; never reuse a published S1 number as the S1* baseline); every omission of the Landbridge is logged in meta.json (`landbridge_omitted: true`, study marker name); the running-time inputs for the sketches come from the study sidecars and the same R4 model used in STUDY_RJ_FAMILIES §5 (no new timetable factor); the judge's own file is kept as score.judge.json as in S6_L6_SCORE.

Handoff
milestone-handoff: make test green (new tests: each replacement score file exists with the judge hash and seed 1; scenario score: blocks match score.json; each replacement graph omits landbridge and contains exactly one RJ sketch; costing used routed km not the straight 844 km; stacked scenarios/study/rj-*.yaml remain unscored; S1 / a published top-5 line list still includes landbridge; the study note has both labels, the alignment limitation, the A-r4-acc-004 sentence and no passenger-group vignette; runs/r6/top5/, R8 reader-facing files and licences untouched against HEAD at run start); docver; manifest verify (no downloads); red-team-verifier label VERIFY_STUDY_RJ_SCORE in the foreground (it checks the above, that the judge hash is unchanged, that landbridge was omitted only for these study packages, that no process was killed, and that every relied-on capex or time traces to a routed sidecar plus the frozen judge; fix FAILs and re-run until PASS); commits per item; status block with: the five-row score table, judge capex vs §6, the S1* definition, git diff --stat against the start HEAD as the untouched-areas evidence, test count, cost estimate; then STUDY_RJ_SCORE: done or STUDY_RJ_SCORE: blocked - <reason>. Then stop.
