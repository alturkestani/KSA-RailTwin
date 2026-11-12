> **Document version:** tests/fixtures/api/README.md v1.1 | 6 Nov 2026 | Author: viz-engineer; R8_L6_PANEL (v1.1: S6-L6 fixtures) | Status: draft

# Dashboard-API fixtures (`tests/test_api_dashboard.py`)

Unlike the invented fixtures in `tests/fixtures/`, these are **trimmed copies of real registers and run outputs**, so the tests can check the binding framing values (for example the S6-L1 NPV at P90 cost). They are test inputs only: never cite them and never use them as inputs to a run. Rebuild from the repo with `uv run python tests/fixtures/api/make_fixtures.py` (values are copied, never edited; `MANIFEST.csv` lists every file and its size).

- `cities/ksa/lines/`, `cities/ksa/zones/regions.geojson`, `cities/ksa/alignments/`: a few features with decimated geometry. Derived from OpenStreetMap, (c) OpenStreetMap contributors, ODbL 1.0; the alignment copies carry the same open ODbL release question as `cities/ksa/alignments/`.
- `cities/ksa/corridors/`: five corridor YAMLs (the S6-L1..L3 corridors). `cities/ksa/candidates.parquet`: 12 register rows (4 short list, 3 long list, 2 served, 3 not long-listed); OSM ODbL and the sources named per row.
- `scenarios/`: copies of `scenarios/S0..S5.yaml` and `S6-L1..L6.yaml`.
- `run_outputs/` (mirrors `runs/`, which is gitignored at every depth): `r2` long-list counts, long-list and score rows for the 12 register rows; three CBA cases cut to the 60-year (three populations) and 30-year (medium) Green Book rows; `r6/top5/top5.csv`, `r6/pareto_front.csv`, layout YAMLs and `score.json` without the accessibility zone lists; `r6/l6/` (S6-L6, R8_L6_PANEL): `L6.layout.yaml`, `score/S6-L6.csv` and `score/score.json` trimmed the same way, kept in their own directory and never copied into the top-5 fixtures (S6-L6 is not a top-5 layout); `r7` fiscal (budget-share, contingent-liability and timing blocks dropped; one corridor) and VfM (one corridor).

Label: synthetic demand, uncalibrated: scenario comparison, not a forecast.
