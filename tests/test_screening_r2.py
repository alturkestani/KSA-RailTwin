"""R2: primary-city matching, control-total scaling, corridor generation, coverage reconciliation
and scenario validation, on small synthetic inputs (fictional towns) plus the tracked line layers.
Runs in a few seconds; no national run.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pandas as pd
import pytest
import yaml

from common.scenarios import check as check_scenarios
from screening import control_total, corridors, primary_match
from screening.coverage import reconcile
from screening.gastat import key_skeleton
from screening.merge import merge_frames

ROOT = Path(__file__).parents[1]
FIX = ROOT / "tests" / "fixtures" / "region_register.parquet"
WEIGHTS = ROOT / "cities" / "ksa" / "assumptions" / "screening_weights.yaml"


# --------------------------------------------------------------------------- primary matching
def test_arabic_skeleton_matches_ta1_spelling():
    assert primary_match.ar_skeleton("الكلابية") == key_skeleton("Alkalabiuh") == "klb"
    assert primary_match.ar_skeleton("العمران") == key_skeleton("Aleumran")
    # a final ح is a consonant, not the ة/ه ending: Abu Talh is not Albitaliuh
    assert primary_match.ar_skeleton("أبو طلح") != key_skeleton("Albitaliuh")
    assert primary_match.ar_norm("غطى") == primary_match.ar_norm("غطي")


def _reg():
    merged, _ = merge_frames([FIX])
    return merged


def _univ(reg: pd.DataFrame) -> pd.DataFrame:
    u = reg[["name_en", "name_ar", "region", "lat", "lon", "population", "pop_type"]].copy()
    u["settlement_id"] = [f"U{i}" for i in range(len(u))]
    u["osm_type"], u["osm_id"] = None, None
    u["grid_population"] = u.population
    return u


def _cities(rows: list[tuple[str, int]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["name", "total"]).assign(saudi=0, non_saudi=0)


def test_match_tiers_and_unmatched_listed():
    reg = _reg()
    univ = _univ(reg)
    reg.loc[reg.name_en == "Fixture Town 2", ["pop_source", "population"]] = [
        primary_match.PRIMARY_SRC,
        12000,
    ]
    cities = _cities([("Fixture Two Primary", 12000), ("Nowhere Farms", 8000)])
    t = primary_match.match(
        reg,
        univ,
        cities,
        pd.DataFrame(columns=["city", "settlement_id", "tier"]),
        relays=pd.DataFrame(),
        osm=None,
        decisions={},
    )
    got = dict(zip(t.city, t.status, strict=True))
    assert got == {"Fixture Two Primary": "matched", "Nowhere Farms": "unmatched"}
    assert t.loc[t.city == "Fixture Two Primary", "tier"].item() == "sweep"
    # an unmatched city is listed with its population and a reason (rule 2)
    um = t[t.status == "unmatched"].iloc[0]
    assert um.total == 8000 and um.reason


def test_apply_sums_declared_combination_and_sets_official():
    reg = _reg()
    key = reg.row_key.iloc[0]
    t = pd.DataFrame(
        {
            "city": ["A", "B"],
            "total": [30000, 20000],
            "tier": ["cp2", "cp2"],
            "row_key": [key, key],
            "settlement_id": [None, None],
            "status": ["matched", "matched"],
            "osm": [None, None],
        }
    )
    new, log = primary_match.apply(reg, t, _univ(reg))
    row = new[new.row_key == key].iloc[0]
    assert row.population == 50000 and row.pop_type == "official"
    assert row.pop_source_status == "verified" and bool(row.tag_10k)
    assert row.primary_city == "A + B" and len(log) == 1


# --------------------------------------------------------------------------- control total
def test_control_total_scales_down_only_and_keeps_raw():
    reg = _reg()
    reg["pop_type"] = ["official", "grid", "grid", "grid", None]
    reg.loc[reg.pop_type == "grid", "population"] = [12000, 7000, 3000]
    reg.loc[reg.pop_type == "grid", "pop_source_status"] = "unverified"
    t = pd.DataFrame({"grid_scale_factor": [0.5]}, index=["makkah"])
    new = control_total.apply(reg, t)
    g = new[new.pop_grid_raw.notna()]
    assert list(g.pop_grid_raw) == [12000, 7000, 3000]
    assert list(g.population) == [6000, 3500, 1500]
    assert g.grid_scaled.all() and (g.grid_scale_factor == 0.5).all()
    assert list(g.tag_5k) == [True, False, False]
    assert not g.tag_10k.any()  # the >= 10k gate is unchanged: grid rows stay uncorroborated
    same = control_total.apply(reg, pd.DataFrame({"grid_scale_factor": [1.0]}, index=["makkah"]))
    assert not same.grid_scaled.any()


# --------------------------------------------------------------------------- corridors
def _corridor_inputs(tmp_path: Path, rename: str | None = None) -> tuple[Path, Path, Path]:
    """Five fictional towns placed around the tracked Riyadh and Qassim stations."""
    reg = _reg()
    pts = [(24.64, 46.72), (26.33, 43.97), (24.15, 47.30), (25.20, 45.30), (23.00, 45.00)]
    reg["lat"], reg["lon"] = [p[0] for p in pts], [p[1] for p in pts]
    reg["population"] = [600000, 300000, 60000, 40000, 20000]
    reg["economic_roles"] = [[], [], [{"role": "port", "source": "fixture"}], [], []]
    if rename:
        reg.loc[2, "name_en"] = rename
    c = tmp_path / "cand.parquet"
    reg.to_parquet(c, index=False)
    sc = reg[["row_key"]].assign(rank=range(1, 6), score=0.5, short_list=True)
    s = tmp_path / "scores.parquet"
    sc.to_parquet(s, index=False)
    cfg = yaml.safe_load(WEIGHTS.read_text(encoding="utf-8"))
    cfg = copy.deepcopy(cfg)
    cfg["metros"] = [
        {"name": "Fixture Metro", "tier": 1, "anchors": [reg.row_key[0]]},
        {"name": "Fixture North", "tier": 2, "anchors": [reg.row_key[1]]},
    ]
    w = tmp_path / "weights.yaml"
    w.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
    return c, s, w


def _generate(tmp_path: Path, rename: str | None = None) -> dict[str, list[dict]]:
    c, s, w = _corridor_inputs(tmp_path, rename)
    ctx = corridors.Ctx(c, s, corridors.RULES, w, seed=1)
    return {
        "trunk_gap": corridors.trunk_gaps(ctx),
        "branch_spur": corridors.branches_spurs(ctx),
        "commuter_belt": corridors.commuter_belts(ctx),
        "station_addition": corridors.station_additions(ctx),
    }


def test_corridors_deterministic_hypothetical_and_traceable(tmp_path):
    a = _generate(tmp_path)
    b = _generate(tmp_path)
    assert a == b
    allc = [c for items in a.values() for c in items]
    assert allc, "the fixture should yield at least one corridor"
    for c in allc:
        corridors.CorridorSpec.model_validate(c)
        assert c["layer"] == "hypothetical" and c["status"] == "generated"
        assert c["rule_id"] and c["generated_from_ids"] and c["cost_status"].startswith("uncosted")
    assert a["commuter_belt"], "a town 40-120 km from the tier-1 metro makes a belt"


def test_corridors_come_from_the_register_not_a_town_list(tmp_path):
    base = _generate(tmp_path)
    renamed = _generate(tmp_path, rename="Renamed Fixture Port")
    ids = {c["id"] for items in renamed.values() for c in items}
    assert any("renamed-fixture-port" in i for i in ids)
    assert ids != {c["id"] for items in base.values() for c in items}


# --------------------------------------------------------------------------- coverage, scenarios
def _cov(n: int = 150) -> pd.DataFrame:
    regions = [f"r{i % 13}" for i in range(n)]
    return pd.DataFrame({"region": regions, "governorate_en": [f"G{i}" for i in range(n)],
                         "rows": 1})  # fmt: skip


def test_coverage_reconciles_and_a_missing_governorate_fails():
    assert reconcile(_cov(), []) == []
    assert reconcile(_cov(149), [])  # one governorate missing from the table
    t = _cov()
    t.loc[5, "rows"] = 0
    assert any("without rows" in e for e in reconcile(t, []))
    assert any("without a governorate" in e for e in reconcile(_cov(), ["x:node:1"]))


def test_committed_scenarios_validate():
    assert check_scenarios(ROOT / "scenarios") == []


def test_hypothetical_candidate_in_s1_fails(tmp_path):
    d = tmp_path / "scenarios"
    d.mkdir()
    for f in ("S0.yaml", "S1.yaml"):
        (d / f).write_text((ROOT / "scenarios" / f).read_text(encoding="utf-8"), encoding="utf-8")
    s1 = yaml.safe_load((d / "S1.yaml").read_text(encoding="utf-8"))
    s1["candidates"] = ["cities/ksa/corridors/x.yaml"]
    (d / "S1.yaml").write_text(yaml.safe_dump(s1, allow_unicode=True), encoding="utf-8")
    assert any("fixed baseline" in e for e in check_scenarios(d))


@pytest.mark.parametrize("fam", sorted(corridors.FAMILIES))
def test_scenario_files_list_only_generated_files(fam):
    sid = corridors.FAMILIES[fam][0]
    sc = yaml.safe_load((ROOT / "scenarios" / f"{sid}.yaml").read_text(encoding="utf-8"))
    for p in sc["candidates"]:
        line = yaml.safe_load((ROOT / p).read_text(encoding="utf-8"))
        assert line["family"] == fam and line["layer"] == "hypothetical"
