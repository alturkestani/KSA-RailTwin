"""FIX_R7 checks (R7-checkpoint fix pass, 4 Nov 2026): register, recommendations and labels. Reads
tracked files only; runs in well under a second."""

from __future__ import annotations

from common import REPO_ROOT


def _row(rid: str) -> list[str]:
    for line in (REPO_ROOT / "docs/assumptions.md").read_text(encoding="utf-8").splitlines():
        if line.startswith(f"| {rid} |"):
            return [c.strip() for c in line.strip().strip("|").split("|")]
    raise AssertionError(f"{rid} not in docs/assumptions.md")


def test_a_fund_003_is_derived_not_unset() -> None:
    row = _row("A-fund-003")
    assert "not set" not in row[2]
    assert row[2].startswith("derived")
    assert "A-fund-007/008/101/010" in row[2]
    assert row[6] == "derived"


def test_recommendations_basis_carries_series_method_and_judge_cross_check() -> None:
    import yaml

    d = yaml.safe_load(
        (REPO_ROOT / "cities/ksa/funding/recommendations.yaml").read_text(encoding="utf-8")
    )
    ents = {**d["corridors"], **d["programmes"]}
    assert len(ents) == 8
    for k, v in ents.items():
        b = v["basis"]
        assert b["fiscal_series_method"], k
        assert isinstance(b["judge_fiscal_cost_p50_60y"], (int, float)), k
        expect = "judge fiscal_cost" if k.startswith("S6-") else "cash-flow engine"
        assert b["fiscal_series_method"].startswith(expect), k


def test_availability_ppp_lists_fare_setting_authority() -> None:
    import yaml

    from funding.recommend import LEGAL_BY_MODEL

    assert "fare_setting_authority" in LEGAL_BY_MODEL["ppp_dbfom_availability"]
    d = yaml.safe_load(
        (REPO_ROOT / "cities/ksa/funding/recommendations.yaml").read_text(encoding="utf-8")
    )
    for k, v in {**d["corridors"], **d["programmes"]}.items():
        av = v["options"].get("ppp_dbfom_availability")
        if av:
            assert "fare_setting_authority" in av["legal_preconditions"], k


def test_numeric_tables_carry_heading_notes() -> None:
    """Every table with demand-based ranges or expected values in the two R7 documents has a
    heading note with the synthetic-demand label, and the PPP / A-fund-108 caveats where due."""
    from common.labels import LABEL

    for doc in ("docs/fiscal-exposure.md", "docs/delivery-models.md"):
        lines = (REPO_ROOT / doc).read_text(encoding="utf-8").splitlines()
        n = 0
        for i, ln in enumerate(lines):
            is_head = ln.startswith("| ") and i + 1 < len(lines) and lines[i + 1].startswith("|---")
            if not is_head or not any(k in ln for k in ("P10", "expected", "E[", "VfM", "2026")):
                continue
            n += 1
            prev = lines[i - 2] if i >= 2 else ""
            assert prev.startswith("*Table note: ") and LABEL in prev, (doc, ln[:60])
            if "expected" in ln or "E[" in ln:
                assert "A-fund-108" in prev and "1.69 × P50" in prev, (doc, ln[:60])
            if "model |" in ln or "option |" in ln or "E[availability PPP]" in ln:
                assert "P10 = P50 by construction" in prev, (doc, ln[:60])
        assert n >= 5, doc


def test_alignment_limitation_label() -> None:
    from common.labels import ALIGNMENT_LIMITATION, LABEL

    assert ALIGNMENT_LIMITATION == (
        "alignments are indicative least-cost sketches on 30 m terrain whose mean lateral offset "
        "from real lines was 3–10 km on three reference lines; lengths within ±5 %; costs and "
        "running times inherit that uncertainty"
    )
    assert ALIGNMENT_LIMITATION != LABEL
    doc = (REPO_ROOT / "docs/alignments.md").read_text(encoding="utf-8")
    assert ALIGNMENT_LIMITATION in doc


def _block(key: str) -> list[list[str]]:
    s = (REPO_ROOT / "docs/alignments.md").read_text(encoding="utf-8")
    a = s.index(f"<!-- gen:{key} -->")
    b = s.index(f"<!-- /gen:{key} -->")
    rows = [ln for ln in s[a:b].splitlines() if ln.startswith("| ")]
    return [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]


def test_v2_validation_table_parses() -> None:
    import pandas as pd

    t = _block("4b-validation")
    head, body = t[0], t[1:]
    assert head[:5] == ["line", "weights", "routed km", "length error", "mean offset km"]
    assert len(body) == 9
    got = {(r[0], r[1]): float(r[4]) for r in body}
    # v1 is the frozen R4_ALIGN validation (docs/alignments.md §4)
    assert got[("hhr", "v1 (frozen)")] == 3.32
    assert got[("sar-north-passenger", "v1 (frozen)")] == 9.81
    assert got[("sar-east-passenger", "v1 (frozen)")] == 9.21
    for ln in ("hhr", "sar-north-passenger", "sar-east-passenger"):
        assert {w for (x, w) in got if x == ln} == {"v1 (frozen)", "v2 in-sample", "v2 held-out"}
    runs = {
        "v1 (frozen)": REPO_ROOT / "runs/align/validation-s1/validation.csv",
        "v2 in-sample": REPO_ROOT / "runs/align/validation-v2-s1/validation.csv",
        "v2 held-out": REPO_ROOT / "runs/align/validation-v2-loo-s1/validation.csv",
    }
    for w, p in runs.items():
        if p.exists():  # runs/ is gitignored: checked where the runs are present
            df = pd.read_csv(p).set_index("line")
            for ln in df.index:
                assert round(float(df.loc[ln, "mean_offset_km"]), 2) == got[(ln, w)]


def test_offset_causes_sum_to_mean_offset() -> None:
    t = _block("4a-causes")
    head, body = t[0], t[1:]
    total = body[-1]
    for j in range(1, len(head)):
        s = sum(float(r[j]) for r in body[:-1])
        assert abs(s - float(total[j].strip("*"))) < 0.02, head[j]


def test_v1_weights_frozen_and_v2_parallel() -> None:
    from network import align as al

    w1 = al.load_weights(None, REPO_ROOT)
    assert w1["frozen"] is True
    h1 = (REPO_ROOT / "cities/ksa/assumptions/align_weights.sha256").read_text().split()[0]
    assert al.weights_hash(w1) == h1
    assert h1.startswith("2b718ecb")
    assert "grade_deadband" not in w1["weights"] and "straightness" not in w1["weights"]
    p2 = REPO_ROOT / "cities/ksa/assumptions/align_weights_v2.yaml"
    w2 = al.load_weights(p2, REPO_ROOT)
    h2 = (REPO_ROOT / "cities/ksa/assumptions/align_weights_v2.sha256").read_text().split()[0]
    assert w2["frozen"] is True and w2["version"] == 2
    assert al.weights_hash(w2) == h2
    assert w2["weights"]["grade_deadband"]["assumption_id"] == "A-align-101"


def test_v2_terms_neutral_reproduce_v1_graph() -> None:
    import copy

    import numpy as np

    from network import align as al

    rng = np.random.default_rng(1)
    dem = (rng.random((12, 14)) * 30.0).astype(np.float32)
    g = al.Grid(1, 80_000, 40_000, dem, np.zeros(dem.shape, np.uint16))
    kl = al.Klass("mixed", 0.0125, 250.0, 4861.0, 151.7, 10.18)
    w = al.load_weights(None, REPO_ROOT)
    mask = np.ones(dem.shape, bool)
    pen = np.zeros(dem.shape)
    corr = np.zeros(dem.shape, bool)
    m1, _ = al.build_graph(g, mask, kl, w, pen, corr)
    w0 = copy.deepcopy(w)
    w0["weights"]["grade_deadband"] = {"value": 0.0}
    w0["weights"]["straightness"] = {"value": 0.0}
    m0, _ = al.build_graph(g, mask, kl, w0, pen, corr)
    assert (m1 != m0).nnz == 0
    a, b = (float(g.lat(0)), float(g.lon(0))), (float(g.lat(11)), float(g.lon(13)))
    assert al.straightness_penalty(g, a, b, w0) is None
    w0["weights"]["grade_deadband"] = {"value": 0.5}
    md, _ = al.build_graph(g, mask, kl, w0, pen, corr)
    assert md.sum() <= m1.sum()  # a dead-band never adds cost
    w0["weights"]["straightness"] = {"value": 0.2}
    sp = al.straightness_penalty(g, a, b, w0)
    assert sp is not None and sp.min() >= 0.0 and sp[0, 13] > sp[0, 0]
