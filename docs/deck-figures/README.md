> **Document version:** docs/deck-figures/README.md v1.2 | 5 Nov 2026 | Author: report-writer (figures); FIX_R8 (v1.2: Arabic titles follow docs/glossary.ar.md, items 1 and 2) | Status: draft

# Deck-ready figures (R8 task 4)

16:9 (13.33 × 7.5 in, PNG at 150 dpi, plus SVG) versions of the 15 report figures, each with an English and an Arabic title. Built together with the report figures:

```
uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/
```

`figures.csv` columns: `file` (the PNG; the SVG has the same stem), `title_en`, `title_ar`, `source_run_ids`, `label` (the synthetic-demand label, the figure's provenance (judge v3 id and seed only where the figure is built from judge v3 runs), and where applicable the alignment limitation and the OSM credit, exactly as printed on the figure).

Arabic titles are written natively and short, use the preferred forms of `docs/glossary.ar.md` (checked by `tests/test_glossary_ar.py`), set in Noto Naskh Arabic with Noto Sans as fallback; matplotlib 3.11 shapes Arabic text itself (no reshaping library added). Digits are Western in both languages. Same labels, sources and rules as `docs/report/figures/README.md`. Nothing here has been shared: CP6 review comes first.
