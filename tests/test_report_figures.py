"""R8 figures (common.figures): every stem in both directories, deck index, labels in the SVGs.
R8_L6_PANEL: S6-L6 on fig08 (from runs/r6/l6/score, never top5), not on fig07, map fig16.

Runs in seconds on the files already built by
`uv run python -m common.figures build --out docs/report/figures/ --deck docs/deck-figures/`;
the byte-identical rebuild check renders one small figure into a temporary directory.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

from common import REPO_ROOT
from common.labels import ALIGNMENT_LIMITATION, LABEL
from tests.localdata import STUDY_RUNS, needs_local

REPORT = REPO_ROOT / "docs/report/figures"
DECK = REPO_ROOT / "docs/deck-figures"
RUNS = REPO_ROOT / "runs"

STEMS = [
    "fig01-national-map",
    "fig02-screening-funnel",
    "fig03-coverage-by-region",
    "fig04-bcr-bands-by-family",
    "fig05-programme-npv-ranges",
    "fig06-l1-p90-cost-risk",
    "fig07-pareto-front",
    "fig08-reach-tradeoff",
    "fig09-stage-gates",
    "fig10-fiscal-exposure",
    "fig11-vfm",
    "fig12-isochrones",
    "fig13-benchmark-cost-per-km",
    "fig14-tornado-switching",
    "fig15-capex-ranges",
    "fig16-l6-connected-map",
]
MAPS = {"fig01-national-map", "fig12-isochrones", "fig16-l6-connected-map"}
SCREENING = {"fig02-screening-funnel", "fig03-coverage-by-region"}
JUDGE = "judge v3 d9fef643… · seed 1"
OSM = "© OpenStreetMap contributors (ODbL)"

need_figs = pytest.mark.skipif(
    not (REPORT / "fig01-national-map.svg").exists(),
    reason="figures not built (uv run python -m common.figures build --out docs/report/figures/ "
    "--deck docs/deck-figures/)",
)
# R9: keyed on the study run metas, not on runs/ itself (`make demo` creates runs/demo in a clone);
# provenance() reads those metas (gitignored).
need_runs = needs_local(*STUDY_RUNS)
need_prov = need_runs


from common.figures import SPECS, provenance  # noqa: E402


def test_provenance_per_family() -> None:
    by = {s.stem: s.prov for s in SPECS}
    assert by["fig14-tornado-switching"] == ("r5_cba",)
    assert by["fig04-bcr-bands-by-family"] == ("r5_cba",)
    assert (
        "judge_v3" not in by["fig12-isochrones"]
        and "judge_v3" not in by["fig03-coverage-by-region"]
    )
    assert "judge_v3" in by["fig06-l1-p90-cost-risk"]


def test_clip_guard_detects_overflow() -> None:
    import matplotlib.pyplot as plt

    from common.figures import _fit_text, clipped_texts

    fig = plt.figure(figsize=(4, 2), dpi=72)
    fig.text(0.9, 0.5, "this text runs off the right edge of the canvas")
    assert clipped_texts(fig)
    plt.close(fig)
    fig = plt.figure(figsize=(4, 2), dpi=72)
    _fit_text(fig, 0.05, 0.5, "a long line " * 12, 8.0)
    assert not clipped_texts(fig)
    plt.close(fig)


def test_registry_matches_stems() -> None:
    from common.figures import STEMS as REGISTERED

    assert REGISTERED == STEMS


@need_figs
@pytest.mark.parametrize("stem", STEMS)
def test_both_dirs_both_formats(stem: str) -> None:
    for d in (REPORT, DECK):
        for ext in ("svg", "png"):
            f = d / f"{stem}.{ext}"
            assert f.exists() and f.stat().st_size > 1000, f


@need_figs
@need_prov
@pytest.mark.parametrize("stem", STEMS)
def test_svg_labels(stem: str) -> None:
    for d in (REPORT, DECK):
        text = (d / f"{stem}.svg").read_text(encoding="utf-8")
        assert LABEL in text
        spec = next(x for x in SPECS if x.stem == stem)
        assert provenance(spec) in text
        # the judge-v3 footer only on figures built from judge-v3 runs (verify-R8 fix 2)
        uses_v3 = bool({"judge_v3", "r7_funding", "l6_score"} & set(spec.prov))
        assert (JUDGE in text or "judge v3 d9fef643… scores" in text) == uses_v3, stem
        assert "<dc:date" not in text, "SVG carries a date: rebuilds would differ"
        if stem not in SCREENING:
            assert ALIGNMENT_LIMITATION in text
        if stem in MAPS:
            assert OSM in text
            for layer in ("existing", "committed / under procurement", "historical"):
                assert layer in text, (stem, layer)
            assert "hypothetical (ours)" in text


@need_figs
def test_no_v2_and_no_model_names() -> None:
    for d in (REPORT, DECK):
        for f in d.glob("fig*.svg"):
            text = f.read_text(encoding="utf-8").lower()
            assert "alignments-v2" not in text and "top5-v2" not in text and "r7-v2" not in text
            for bad in ("claude", "opus", "haiku", "fable"):
                assert bad not in text, (f.name, bad)


@need_figs
def test_l4_l5_only_with_tradeoff_caption() -> None:
    for stem in STEMS:
        text = (REPORT / f"{stem}.svg").read_text(encoding="utf-8")
        if "S6-L4" in text or "S6-L5" in text:
            assert stem in {"fig07-pareto-front", "fig08-reach-tradeoff"}, stem
            assert "trade-off illustration only: no recommendation" in text


@need_figs
def test_deck_csv() -> None:
    rows = list(csv.DictReader((DECK / "figures.csv").open(encoding="utf-8")))
    assert 12 <= len(rows) <= 20
    assert list(rows[0]) == ["file", "title_en", "title_ar", "source_run_ids", "label"]
    for r in rows:
        assert (DECK / r["file"]).exists()
        assert r["title_ar"] and any("؀" <= ch <= "ۿ" for ch in r["title_ar"])
        assert r["source_run_ids"] and LABEL in r["label"]


@need_figs
@need_prov
def test_index_csv() -> None:
    rows = list(csv.DictReader((REPORT / "figures-index.csv").open(encoding="utf-8")))
    assert [r["stem"] for r in rows] == STEMS
    assert list(rows[0]) == [
        "stem",
        "title_en",
        "caption",
        "sources",
        "provenance",
        "labels_present",
        "files",
    ]
    by = {s.stem: s for s in SPECS}
    for r in rows:
        assert r["caption"] == by[r["stem"]].caption and len(r["caption"]) > 40
        assert r["provenance"] == provenance(by[r["stem"]])
        assert r["sources"] and "synthetic" in r["labels_present"]
        text = (REPORT / f"{r['stem']}.svg").read_text(encoding="utf-8")
        for src in r["sources"].split("; "):
            assert src in text, (r["stem"], src)


@need_runs
@need_figs
def test_rebuild_is_byte_identical(tmp_path: Path) -> None:
    from common.figures import build_all

    stem = "fig15-capex-ranges"
    build_all(tmp_path, None, 1, None, only=[stem])
    for ext in ("svg", "png"):
        a = hashlib.sha256((tmp_path / f"{stem}.{ext}").read_bytes()).hexdigest()
        b = hashlib.sha256((REPORT / f"{stem}.{ext}").read_bytes()).hexdigest()
        assert a == b, ext


@need_runs
def test_l1_p90_cost_values_from_runs() -> None:
    """The decision-framing numbers fig06 shows come from the run file (prompts/R8.md)."""
    import json

    s = json.loads((RUNS / "r6/top5/L1/score.json").read_text(encoding="utf-8"))
    p90 = s["npv_at_p90_cost"]
    got = [round(p90[k]) for k in ("un_wpp_low", "un_wpp_medium", "un_wpp_high")]
    assert got == [-2958, -724, 1631]


# ------------------------------------------------------------------ R8_L6_PANEL (S6-L6)
L6_CSV = RUNS / "r6/l6/score/S6-L6.csv"
need_l6 = pytest.mark.skipif(not L6_CSV.exists(), reason="runs/r6/l6/score missing")


def test_l6_is_comparison_not_cp7_or_search() -> None:
    from common import figures as cf

    assert "S6-L6" not in cf.CP7 and "S6-L6" not in cf.ILLUSTRATION
    assert cf.COMPARISON == ["S6-L6"]
    assert "S6-L6" not in cf.ROLE  # not a CP7 programme role
    assert cf.L6_CSV.parts[:3] == ("runs", "r6", "l6") and "top5" not in str(cf.L6_CSV)
    by = {s.stem: s for s in SPECS}
    assert "l6_score" in by["fig08-reach-tradeoff"].prov
    assert "l6_score" not in by["fig07-pareto-front"].prov
    assert "not on the R6 front" in by["fig07-pareto-front"].caption
    cap = by["fig08-reach-tradeoff"].caption
    assert "S6-L6 is a connectivity comparison" in cap and "not a search-front point" in cap
    assert "reach trade-off illustrations from the search" in cap
    assert by["fig08-reach-tradeoff"].title_en == "Cost against reach: S6-L1 to S6-L6"
    m = by["fig16-l6-connected-map"]
    assert m.title_en == (
        "S6-L6: one connected rail system (comparison layout, not the recommended programme)"
    )
    assert "A-r4-acc-004" in m.caption


@need_runs
@need_l6
def test_l6_read_from_l6_score_not_top5() -> None:
    import pandas as pd

    from common import figures as cf

    t5 = pd.read_csv(RUNS / "r6/top5/top5.csv")
    assert "S6-L6" not in set(t5["layout"])
    assert len(t5) == 5
    front = pd.read_csv(RUNS / "r6/pareto_front.csv")
    r = cf.l6()
    assert not (
        (front["robust_npv"].round(1) == round(r["robust_npv"], 1))
        & (front["capex_p50"].round(1) == round(r["capex_p50"], 1))
    ).any(), "S6-L6 must not be an R6 front row"
    assert round(r["robust_npv"]) == -191660 and round(r["capex_p50"]) == 227213
    gain = r["national_reach_gain_120_reported_only"] / 1e6
    by = {s.stem: s for s in SPECS}
    assert f"+{gain:.2f} M" in by["fig08-reach-tradeoff"].caption


@need_figs
def test_l6_on_fig08_and_fig16_not_fig07() -> None:
    f8 = (REPORT / "fig08-reach-tradeoff.svg").read_text(encoding="utf-8")
    assert "S6-L6" in f8 and "runs/r6/l6/score/S6-L6.csv" in f8
    assert "comparison layout, not the recommended programme" in f8
    f7 = (REPORT / "fig07-pareto-front.svg").read_text(encoding="utf-8")
    assert "S6-L6" not in f7
    f16 = (REPORT / "fig16-l6-connected-map.svg").read_text(encoding="utf-8")
    assert "comparison layout, not the recommended programme" in f16
    assert "A-r4-acc-004" in f16 and "rail-graph interchanges" in f16
    rows = {r["stem"]: r for r in csv.DictReader((REPORT / "figures-index.csv").open())}
    assert "s6-l6-connected-map.png" in rows["fig16-l6-connected-map"]["sources"]
    assert "judge v3 d9fef643" in rows["fig16-l6-connected-map"]["provenance"]
    for s in (
        "fig01-national-map",
        "fig05-programme-npv-ranges",
        "fig06-l1-p90-cost-risk",
        "fig09-stage-gates",
        "fig10-fiscal-exposure",
        "fig11-vfm",
        "fig15-capex-ranges",
    ):
        assert "S6-L6" not in (REPORT / f"{s}.svg").read_text(encoding="utf-8"), s
