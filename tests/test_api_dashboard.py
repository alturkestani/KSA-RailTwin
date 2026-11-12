"""Dashboard API (contract v1.0) on the tiny fixtures in tests/fixtures/api (seconds to run)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.contract import COMPARISON_CAPTION, JUDGE, TRADE_OFF_CAPTION
from api.main import create_app
from common.labels import ALIGNMENT_LIMITATION, LABEL

FIX = Path(__file__).parent / "fixtures" / "api"

MODELLED = [
    "/api/layers",
    "/api/layers/hypothetical",
    "/api/scenarios",
    "/api/cba",
    "/api/cba/CBA-S1-committed-programme",
    "/api/programmes",
    "/api/programmes/S6-L2",
    "/api/programmes/S6-L6",
    "/api/pareto",
    "/api/fiscal",
    "/api/vfm",
    "/api/difference?scenario=S6-L2",
    "/api/difference?scenario=S5-station_addition-dhahran",
]


@pytest.fixture(scope="module")
def client() -> TestClient:
    mp = pytest.MonkeyPatch()
    mp.setenv("RAILTWIN_DATA_ROOT", str(FIX))
    mp.setenv("RAILTWIN_RUNS_ROOT", str(FIX / "run_outputs"))
    mp.setenv("RAILTWIN_WEB_DIST", str(FIX / "no-dist"))
    yield TestClient(create_app())
    mp.undo()


def _ranges(obj: Any) -> list[dict[str, Any]]:
    """Every {'p10','p50','p90'} dict anywhere in a response."""
    found: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        if {"p10", "p50", "p90"} <= set(obj):
            found.append(obj)
        for v in obj.values():
            found += _ranges(v)
    elif isinstance(obj, list):
        for v in obj:
            found += _ranges(v)
    return found


def test_health_and_meta(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"
    m = client.get("/api/meta").json()
    assert m["label"] == LABEL
    assert m["alignment_limitation"] == ALIGNMENT_LIMITATION
    assert m["judge"]["sha256"] == JUDGE["sha256"]
    assert m["judge"]["sha256"].startswith("d9fef64384e2e25f")
    assert m["seed"] == 1
    assert m["osm_credit"] == "© OpenStreetMap contributors"
    assert set(m["layers"]) == {"existing", "committed", "hypothetical", "historical"}
    assert m["framing"]["S6-L2"]["role"] == "central case"
    assert m["framing"]["S6-L3"]["role"] == "reach alternative"
    assert "P90 cost risk" in m["framing"]["S6-L1"]["role"]


@pytest.mark.parametrize("url", MODELLED)
def test_both_labels_on_modelled_responses(client: TestClient, url: str) -> None:
    r = client.get(url)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["label"] == LABEL
    assert body["alignment_limitation"] == ALIGNMENT_LIMITATION


@pytest.mark.parametrize("url", MODELLED)
def test_ranges_are_ordered(client: TestClient, url: str) -> None:
    for r in _ranges(client.get(url).json()):
        vals = [r["p10"], r["p50"], r["p90"]]
        if None in vals:
            continue
        assert vals[0] <= vals[1] <= vals[2], r


def test_layers_keep_the_four_layers_apart(client: TestClient) -> None:
    body = client.get("/api/layers").json()
    assert body["osm_credit"] == "© OpenStreetMap contributors"
    layers = body["layers"]
    assert set(layers) == {"existing", "committed", "historical", "hypothetical"}
    for name, fc in layers.items():
        assert fc["features"], name
        assert {f["properties"]["layer"] for f in fc["features"]} == {name}
    names = {f["properties"]["layer_name"] for f in layers["committed"]["features"]}
    assert names == {"committed/under procurement"}
    for f in layers["committed"]["features"]:  # source and date travel to the legend note
        assert f["properties"]["source"] and "source_date" in f["properties"]
    hyp = layers["hypothetical"]["features"]
    kinds = {f["properties"]["kind"] for f in hyp}
    assert "routed" in kinds and "station_addition" in kinds
    assert client.get("/api/layers/nope").status_code == 404


def test_stations_and_regions(client: TestClient) -> None:
    st = client.get("/api/stations").json()
    assert st["features"] and all(f["properties"]["layer"] for f in st["features"])
    rg = client.get("/api/regions").json()
    assert rg["features"] and rg["osm_credit"]


def test_register_and_funnel(client: TestClient) -> None:
    reg = client.get("/api/register").json()
    stages = {r["stage"] for r in reg["rows"]}
    assert {"short_list", "long_list", "served", "not_long_listed"} <= stages
    short = client.get("/api/register?stage=short_list").json()
    assert short["count"] == 4 and all(r["stage"] == "short_list" for r in short["rows"])
    region = reg["rows"][0]["region"]
    by_region = client.get(f"/api/register?region={region}").json()["rows"]
    assert by_region and all(r["region"] == region for r in by_region)
    assert client.get("/api/register?stage=bad").status_code == 422
    fn = client.get("/api/funnel").json()
    counts = [s["count"] for s in fn["stages"]]
    assert counts[0] >= counts[1] >= counts[3]  # settlements >= long list >= short list
    assert fn["per_region"] and fn["corridors_by_family"]["station_addition"] == 3


def test_scenarios_s0_to_s6_and_trade_off_flags(client: TestClient) -> None:
    sc = {s["id"]: s for s in client.get("/api/scenarios").json()["scenarios"]}
    expected = {
        "S0",
        "S1",
        "S2",
        "S3",
        "S4",
        "S5",
        "S6-L1",
        "S6-L2",
        "S6-L3",
        "S6-L4",
        "S6-L5",
        "S6-L6",
    }
    assert set(sc) == expected
    for lay in ("S6-L4", "S6-L5"):
        assert sc[lay]["trade_off_only"] is True
        assert sc[lay]["caption"] == TRADE_OFF_CAPTION
    for lay in ("S6-L1", "S6-L2", "S6-L3"):
        assert sc[lay]["trade_off_only"] is False
        assert sc[lay]["baseline"] == "S1"
    l6 = sc["S6-L6"]
    assert l6["trade_off_only"] is True and l6["comparison_only"] is True
    assert l6["caption"] == COMPARISON_CAPTION != TRADE_OFF_CAPTION
    assert l6["source"] == "scenarios/S6-L6.yaml" and len(l6["candidates"]) == 16


def test_cba_ranges_and_central_row(client: TestClient) -> None:
    body = client.get("/api/cba").json()
    assert body["row"] == {
        "population": "un_wpp_medium",
        "horizon": 60,
        "rate_case": "greenbook_2026",
    }
    cases = {c["case"]: c for c in body["cases"]}
    s1 = cases["CBA-S1-committed-programme"]
    assert s1["baseline"] == "S0" and s1["seed"] == 1
    for c in cases.values():
        for m in ("npv", "bcr", "pvb", "pvc"):
            assert set(c["metrics"][m]) == {"p10", "p50", "p90"}
    assert cases["CBA-S5-station_addition-dhahran"]["baseline"] == "S1"
    fam = client.get("/api/cba?family=station_addition").json()["cases"]
    assert [c["family"] for c in fam] == ["station_addition"]
    assert client.get("/api/cba?population=x").status_code == 422
    assert client.get("/api/cba/CBA-nope").status_code == 404


def test_programmes_framing_and_l1_p90_note(client: TestClient) -> None:
    progs = {p["id"]: p for p in client.get("/api/programmes").json()["programmes"]}
    assert progs["S6-L2"]["role"] == "central case"
    l1 = progs["S6-L1"]
    assert l1["p90_cost_note"] == (
        "NPV at P90 cost −2,958 / −724 / +1,631 low/medium/high SAR m, runs/r6/top5/top5.csv"
    )
    assert round(l1["npv_at_p90_cost"]["low"]) == -2958
    assert round(l1["npv_at_p90_cost"]["medium"]) == -724
    assert round(l1["npv_at_p90_cost"]["high"]) == 1631
    for lay in ("S6-L4", "S6-L5"):
        assert progs[lay]["trade_off_only"] is True
        assert progs[lay]["caption"] == TRADE_OFF_CAPTION
    assert "p90_cost_note" not in progs["S6-L2"]
    assert client.get("/api/programmes/S6-L9").status_code == 404


def test_pareto_marks_l4_l5_trade_off_only(client: TestClient) -> None:
    body = client.get("/api/pareto").json()
    assert body["front"] and body["caption_trade_off"] == TRADE_OFF_CAPTION
    lay = {x["id"]: x for x in body["layouts"]}
    assert lay["S6-L4"]["trade_off_only"] and lay["S6-L5"]["trade_off_only"]
    assert not lay["S6-L2"]["trade_off_only"]
    for x in body["front"]:
        band = x["npv_band"]
        assert band["low"] <= band["medium"] <= band["high"]


def test_fiscal_and_vfm(client: TestClient) -> None:
    f = client.get("/api/fiscal").json()
    assert {p["entity"] for p in f["programmes"]} == {"S6-L1", "S6-L2", "S6-L3"}
    for p in f["programmes"]:
        assert p["judge_sha256"] == JUDGE["sha256"]
        assert all(m["net_fiscal_cost_60y"] for m in p["models"])
    assert f["baseline_s1"]["fiscal_cost_60y"]
    v = client.get("/api/vfm").json()
    for p in v["programmes"]:
        assert p["vfm"]["low"] <= p["vfm"]["central"] <= p["vfm"]["high"]


def test_difference_mode(client: TestClient) -> None:
    d = client.get("/api/difference?scenario=S6-L1").json()
    assert d["baseline"] == "S1"
    trips = d["rows"][0]
    assert trips["delta"] == pytest.approx(trips["scenario"] - trips["S1"])
    assert d["p90_cost_note"].startswith("NPV at P90 cost −2,958")
    assert "S3-branch_spur-al-kharj" in d["added_corridors"]
    cov = d["lines_2050_coverage"]
    assert cov["s1_lines_covered"] == ["hhr", "landbridge", "riyadh-rail-link"]
    assert "S3-branch_spur-al-kharj" in cov["s1_lines_not_covered"]
    assert "not written to any run file" in cov["why"]
    for line in d["lines_2050"]:
        assert (line["delta"] is None) == (line["line_id"] in cov["s1_lines_not_covered"])
    c = client.get("/api/difference?scenario=S5-station_addition-dhahran").json()
    assert c["scenario"] == "CBA-S5-station_addition-dhahran" and c["increments"]["npv"]
    for refused in ("S6-L4", "S6-L5", "S1", "S0"):
        assert client.get(f"/api/difference?scenario={refused}").status_code == 409
    assert client.get("/api/difference?scenario=S6-L4").json()["detail"].endswith(TRADE_OFF_CAPTION)
    # the S1 case has baseline S0, so it is not a difference against S1
    assert client.get("/api/difference?scenario=CBA-S1-committed-programme").status_code == 409


def test_no_model_names_or_will_in_responses(client: TestClient) -> None:
    for url in [*MODELLED, "/api/meta", "/api/funnel"]:
        text = client.get(url).text.lower()
        for bad in ("claude", "opus", "haiku", "fable", " will "):
            assert bad not in text, (url, bad)


# ---------------------------------------------------------------- R8_L6_PANEL (S6-L6)


def test_l6_framing_is_comparison_not_cp7() -> None:
    from api.contract import FRAMING, caption

    assert FRAMING["S6-L6"] == {
        "role": "comparison layout, not the recommended programme",
        "trade_off_only": True,
    }
    assert caption("S6-L6") == COMPARISON_CAPTION
    assert caption("S6-L4") == TRADE_OFF_CAPTION and caption("S6-L2") is None


def test_l6_served_from_l6_score_not_top5(client: TestClient) -> None:
    top5 = (FIX / "run_outputs/r6/top5/top5.csv").read_text(encoding="utf-8")
    assert "S6-L6" not in top5
    assert not list((FIX / "run_outputs/r6/top5").glob("L6*"))
    p = client.get("/api/programmes/S6-L6").json()
    assert p["source"] == ["runs/r6/l6/score/S6-L6.csv", "runs/r6/l6/score/score.json"]
    assert p["caption"] == COMPARISON_CAPTION and p["comparison_only"] is True
    assert round(p["robust_npv"]) == -191660
    assert round(p["metrics"]["capex"]["p50"]) == 227213
    assert len(p["corridors"]) == 16 and "p90_cost_note" not in p
    progs = {x["id"] for x in client.get("/api/programmes").json()["programmes"]}
    assert "S6-L6" in progs


def test_pareto_lists_l6_as_comparison_only(client: TestClient) -> None:
    body = client.get("/api/pareto").json()
    lay = {x["id"]: x for x in body["layouts"]}
    l6 = lay["S6-L6"]
    assert l6["trade_off_only"] and l6["comparison_only"] and l6["kind"] == "comparison"
    assert l6["caption"] == COMPARISON_CAPTION == body["caption_comparison"]
    assert lay["S6-L4"]["caption"] == TRADE_OFF_CAPTION and lay["S6-L4"]["kind"] == "search"
    assert "runs/r6/l6/score/S6-L6.csv" in body["source"]
    # not a front point
    assert not any(
        abs(x["robust_npv"] - l6["robust_npv"]) < 1 and abs(x["capex_p50"] - l6["capex"]["p50"]) < 1
        for x in body["front"]
    )


def test_difference_refuses_l6(client: TestClient) -> None:
    r = client.get("/api/difference?scenario=S6-L6")
    assert r.status_code == 409
    assert r.json()["detail"].endswith(COMPARISON_CAPTION)


def test_funnel_counts_five_search_layouts(client: TestClient) -> None:
    st = {s["stage"]: s for s in client.get("/api/funnel").json()["stages"]}
    s6 = st["optimised layouts (S6)"]
    assert s6["count"] == 5 and s6["source"] == "runs/r6/top5/top5.csv"


def test_l6_not_cp7_in_fiscal_and_meta(client: TestClient) -> None:
    f = client.get("/api/fiscal").json()
    assert "S6-L6" not in {p["entity"] for p in f["programmes"]}
    m = client.get("/api/meta").json()
    assert m["comparison_layouts"] == ["S6-L6"]
    assert m["comparison_caption"] == COMPARISON_CAPTION


def test_switcher_has_no_l6() -> None:
    import re

    cfg = (Path(__file__).parents[1] / "web/src/config.ts").read_text(encoding="utf-8")
    m = re.search(r"export const SWITCHER = \[(.*?)\] as const", cfg)
    assert m
    ids = re.findall(r'"([^"]+)"', m.group(1))
    assert ids == ["S0", "S1", "S2", "S3", "S4", "S5", "S6-L2", "S6-L1", "S6-L3"]
