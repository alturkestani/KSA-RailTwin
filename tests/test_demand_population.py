"""demand.population (R3 task 2): projection preserves the national total exactly, shares sum to 1,
giga add-ons keep the total in reallocate mode, every number in the population YAMLs carries a
source or assumption id that resolves. Reads committed tables only; no network, no data/ files."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from common.labels import LABEL
from demand import population as P

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "zones.geojson"
SCENARIOS = sorted(P.SCEN_DIR.glob("*.yaml"))
PROJECTIONS = [
    "baseline",
    "un_wpp_low",
    "un_wpp_medium",
    "un_wpp_high",
    "un_wpp_constant_fertility",
    "un_wpp_zero_migration",
    "un_wpp_medium_gastat2024",
    "vision2030_policy",
]
YEARS = [2022, 2025, 2030, 2040, 2050, 2060]


@pytest.fixture(scope="module")
def base() -> pd.Series:
    return P.base_by_zone()


@pytest.fixture(scope="module")
def fixture_zones() -> pd.Series:
    d = json.loads(FIXTURE.read_text(encoding="utf-8"))
    s = pd.Series(
        {f["properties"]["zone_id"]: f["properties"]["population"] for f in d["features"]}
    )
    return s.astype("int64").sort_index()


def test_base_table_matches_census_and_zones(base: pd.Series) -> None:
    b = P.load_base()
    assert len(b) == 150 and b.zone_id.nunique() == 149
    assert int(b.pop_2022.sum()) == P.inputs()["census_2022_total"]["value"]
    gj = json.loads((ROOT / "cities/ksa/zones/governorates.geojson").read_text(encoding="utf-8"))
    assert set(base.index) == {f["properties"]["gov_id"] for f in gj["features"]}
    assert (b.saudi_2022 + b.non_saudi_2022 == b.pop_2022).all()


@pytest.mark.parametrize("sid", PROJECTIONS)
@pytest.mark.parametrize("method", ["constant_shares", "regional_trend"])
def test_project_preserves_national_total(base: pd.Series, sid: str, method: str) -> None:
    sc = P.load_scenario(sid)
    for y in YEARS:
        pop = P.project(base, sc, y, method)
        assert int(pop.sum()) == P.national_total(sc, y)
        assert (pop >= 0).all() and list(pop.index) == list(base.index)


@pytest.mark.parametrize("sid", PROJECTIONS)
def test_2022_reproduces_census_zones(base: pd.Series, sid: str) -> None:
    pop = P.project(base, P.load_scenario(sid), 2022)
    assert pop.equals(base.rename(pop.name))


def test_project_on_six_zone_fixture(fixture_zones: pd.Series) -> None:
    sc = {"id": "fixture", "national_totals": {"values": {2030: 39_999}}}
    pop = P.project(fixture_zones, sc, 2030)
    assert int(pop.sum()) == 39_999
    assert pop.equals(P.project(fixture_zones, sc, 2030))  # deterministic
    over = dict(sc, zone_overrides={"FZ5": {"values": {2030: 20_000}}})
    pop2 = P.project(fixture_zones, over, 2030)
    assert pop2["FZ5"] == 20_000 and int(pop2.sum()) == 39_999


@pytest.mark.parametrize("w", [0.0, 0.5, 1.0])
def test_shares_sum_to_one(base: pd.Series, w: float) -> None:
    for y in YEARS:
        for m in ("constant_shares", "regional_trend"):
            s = P.zone_shares(base, y, m, weight=w)
            assert s.sum() == pytest.approx(1.0, abs=1e-12)
            assert (s > 0).all()


def test_regional_trend_weight_zero_is_constant(base: pd.Series) -> None:
    a = P.zone_shares(base, 2050, "constant_shares")
    b = P.zone_shares(base, 2050, "regional_trend", weight=0.0)
    pd.testing.assert_series_equal(a, b, check_names=False)


def test_largest_remainder_exact() -> None:
    w = pd.Series([1.0, 1.0, 1.0], index=["a", "b", "c"])
    out = P.largest_remainder(w, 10)
    assert int(out.sum()) == 10 and sorted(out.tolist()) == [3, 3, 4]


def test_policy_override_hits_riyadh_target(base: pd.Series) -> None:
    sc = P.load_scenario("vision2030_policy")
    inp = P.inputs()["vision2030"]
    pop = P.project(base, sc, 2030)
    assert pop[inp["riyadh_target_2030"]["zone"]] == inp["riyadh_target_2030"]["value"]
    assert int(pop.sum()) == inp["national_target_2030"]["value"]


def test_wpp_ordering(base: pd.Series) -> None:
    lo, me, hi = (P.load_scenario(s) for s in ("un_wpp_low", "un_wpp_medium", "un_wpp_high"))
    for y in (2030, 2050, 2060):
        assert P.national_total(lo, y) < P.national_total(me, y) < P.national_total(hi, y)
    pi = me["prediction_intervals"]
    for y in P.PI_YEARS:
        vals = [pi[k][y] for k in ("lower_95", "lower_80", "median", "upper_80", "upper_95")]
        assert vals == sorted(vals)


@pytest.mark.parametrize("q", ["p10", "p50", "p90", "announced"])
def test_giga_reallocate_keeps_total(base: pd.Series, q: str) -> None:
    giga = P.load_scenario("gigaprojects")
    pop = P.project(base, P.load_scenario("un_wpp_medium"), 2040)
    inc = P.giga_increments(giga, 2040, q, base)
    out = P.apply_giga(pop, inc, "reallocate")
    assert int(out.sum()) == int(pop.sum())
    add = P.apply_giga(pop, inc, "additive")
    assert int(add.sum()) == int(pop.sum()) + int(round(inc.sum()))


def test_giga_quantiles_ordered_and_ramped(base: pd.Series) -> None:
    giga = P.load_scenario("gigaprojects")
    tot = {
        q: P.giga_increments(giga, 2040, q, base).sum() for q in ("p10", "p50", "p90", "announced")
    }
    assert tot["p10"] <= tot["p50"] <= tot["p90"] <= tot["announced"]
    assert P.giga_increments(giga, 2024, "announced", base).sum() == 0  # before the ramp start
    for p in giga["projects"]:
        d = p["delivered_share"]
        assert 0 <= d["p10"] <= d["p50"] <= d["p90"] <= 1
        assert p["zone"] is None or p["zone"] in base.index


def test_every_giga_node_listed() -> None:
    nodes = pd.read_csv(ROOT / "cities/ksa/zones/economic_nodes.csv")
    giga = {n.removeprefix("giga-") for n in nodes[nodes.role == "giga_project"].node_id}
    text = (P.SCEN_DIR / "gigaprojects.yaml").read_text(encoding="utf-8")
    listed = {
        "neom": "neom-the-line", "oxagon": "neom-oxagon", "trojena": "neom-trojena",
        "red-sea-global": "red-sea-global-the-red-sea", "roshn-sedra": "roshn-sedra",
    }  # fmt: skip
    for g in giga:
        assert f"id: {listed.get(g, g)}" in text, g


@pytest.mark.parametrize("path", SCENARIOS, ids=lambda p: p.name)
def test_scenario_yaml_header_label_kind(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# > **Document version:**")
    doc = P.read_yaml(path)
    assert doc["label"] == LABEL and doc["kind"]


def test_every_number_has_source_or_assumption() -> None:
    assert P.validate_all() == []


def test_uncovered_number_is_caught() -> None:
    doc = {"id": "x", "sources": ["S-r3-pop-001"], "block": {"values": {2030: 1}}}
    assert P.uncovered_numbers(doc) == [".block.values.2030"]
    doc["block"]["assumption"] = "A-pop-001"
    assert P.uncovered_numbers(doc) == []


@pytest.mark.parametrize(
    "rel",
    [
        "docs/population-scenarios.md",
        "cities/ksa/population/README.md",
    ],
)
def test_doc_ids_resolve(rel: str) -> None:
    known_s, known_a = P.known_ids()
    text = (ROOT / rel).read_text(encoding="utf-8")
    s_ids = {i for i in P.ID_S.findall(text) if not i.endswith("-")}
    a_ids = set(P.ID_A.findall(text))
    assert not sorted(s_ids - known_s), sorted(s_ids - known_s)
    assert not sorted(a_ids - known_a), sorted(a_ids - known_a)


def test_r3_register_rows_ids_resolve() -> None:
    """R3 rows merged into docs/assumptions.md at INTEGRATE_R3 (pop, demand, geo, mode)."""
    known_s, known_a = P.known_ids()
    rows = [
        line
        for line in (ROOT / "docs/assumptions.md").read_text(encoding="utf-8").splitlines()
        if line.startswith(("| A-pop-", "| A-demand-", "| A-geo-", "| A-mode-"))
    ]
    assert len(rows) >= 110
    text = "\n".join(rows)
    s_ids = {i for i in P.ID_S.findall(text) if not i.endswith("-")}
    a_ids = set(P.ID_A.findall(text))
    assert not sorted(s_ids - known_s), sorted(s_ids - known_s)
    assert not sorted(a_ids - known_a), sorted(a_ids - known_a)
