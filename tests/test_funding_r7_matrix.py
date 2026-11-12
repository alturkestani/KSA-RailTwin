"""R7 risk matrices and recommendations: every CP7 corridor x candidate model and every programme
has a filled, valid matrix covering every risk row with exactly one column; the recommendations
file names a candidate model, alternatives and only resolvable sources (committed files only)."""

from __future__ import annotations

import yaml

from common import REPO_ROOT
from funding import inputs, recommend, risk_matrix
from funding.models import RISK_KEYS
from funding.sources import known_source_ids, unknown_ids

FUND = REPO_ROOT / "cities" / "ksa" / "funding"
PARAMS = yaml.safe_load((REPO_ROOT / "cities/ksa/assumptions/funding_r7.yaml").read_text())


def test_allocation_rules_cover_every_risk_once():
    for model, rules in PARAMS["allocation"].items():
        assert list(rules) == RISK_KEYS, model
        for r in rules.values():
            assert r["mark"] in risk_matrix.COLUMNS
            assert r["precedents"] and r["mechanism"] and r["why"]
    cited = [
        s
        for rules in PARAMS["allocation"].values()
        for r in rules.values()
        for s in r["precedents"]
    ]
    assert not unknown_ids(cited, known_source_ids())


def test_every_cp7_corridor_and_model_has_a_valid_matrix():
    known = known_source_ids()
    cors = inputs.corridor_phases()
    assert len(cors) == 5  # Al Jubayl, Dhahran, Duruma, Al-Kharj spur, Riyadh belt 225
    for cid in cors:
        fam = risk_matrix.FAMILY[cid.split("-")[0]]
        for model in PARAMS["candidates"][fam]:
            p = risk_matrix.matrix_path(cid, model)
            m = risk_matrix.load_matrix(p)
            assert not m.template and m.corridor == cid and m.delivery_model == model
            assert [r.risk for r in m.rows] == RISK_KEYS
            assert all(len(r.marks()) == 1 and r.mechanism and r.precedents for r in m.rows)
            assert not unknown_ids(m.cited(), known)
            assert m.evidence and "judge_sha256" in m.evidence
    for sid in inputs.LAYOUTS.values():
        ms = list(FUND.glob(f"risk_matrix_{sid}--*.yaml"))
        assert ms, sid
        for p in ms:
            assert risk_matrix.load_matrix(p).programme == sid


def test_recommendations_complete_and_checked():
    d = yaml.safe_load((FUND / "recommendations.yaml").read_text())
    assert not recommend.check(d)
    assert set(d["programmes"]) == set(inputs.LAYOUTS.values())
    assert set(d["corridors"]) == set(inputs.corridor_phases())
    for v in d["corridors"].values():
        fam = v["family"]
        assert v["recommended_model"] in PARAMS["candidates"][fam]
        assert set(v["alternatives_considered"]) == set(PARAMS["candidates"][fam]) - {
            v["recommended_model"]
        }
        assert "analyst's judgement" in v["judgement"]
        for m, o in v["options"].items():
            if m.startswith("_"):
                continue
            n = o["net_fiscal_cost_pv"]["60y"]
            assert n["p10"] <= n["p50"] <= n["p90"]
    for k, it in d["legal_items"].items():
        assert it["status"] in ("clear", "unclear"), k
        assert it.get("question") if it["status"] == "unclear" else it.get("text")
