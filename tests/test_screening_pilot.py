"""PILOT_MERGE: RegionRow pilot fields, screening.merge and screening.funnel on the fixtures.

Fixtures only (`tests/fixtures/region_register.parquet`, fictional towns); runs in well under 5 s.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pandas as pd
import pytest
import yaml
from pydantic import ValidationError

from common.schemas import RegionRow, load_region_register
from screening import funnel
from screening.coverage import norm_ar, norm_en
from screening.merge import merge_frames

FIX = Path(__file__).parent / "fixtures" / "region_register.parquet"
WEIGHTS = Path(__file__).parents[1] / "cities" / "ksa" / "assumptions" / "screening_weights.yaml"
# Sweep tolerance on the fixture: one-at-a-time +/- 25 % weight changes may move a candidate by at
# most this many rank places (the fixture has 4 long-list rows).
RANK_TOLERANCE = 1


def _row(**kw):
    base = {
        "name_ar": "بلدة اختبار",
        "name_en": "Fixture Town",
        "region": "makkah",
        "governorate": "Fixture",
        "governorate_ar": "محافظة اختبار",
        "is_governorate_centre": True,
        "lat": 21.0,
        "lon": 40.0,
        "population": 60000,
        "pop_source": "fixture",
        "pop_year": 2022,
        "pop_type": "official",
        "tag_10k": True,
        "tag_5k": True,
        "screened": True,
        "fixture": True,
    }
    base.update(kw)
    return base


# --------------------------------------------------------------------------- schema
def test_secondary_relay_is_official_with_status_and_primary():
    r = RegionRow.model_validate(
        _row(pop_source_status="secondary", primary_to_find="GASTAT table", threshold_50k=True)
    )
    assert r.pop_type == "official" and r.pop_source_status == "secondary"


@pytest.mark.parametrize(
    "kw",
    [
        {"pop_type": "secondary"},  # the pilots' value is not allowed (coordinator decision)
        {"pop_source_status": "secondary"},  # official + secondary needs primary_to_find
        {"threshold_50k": False},  # disagrees with population 60,000
        {"pilot_sample": True},  # needs the sampling reason in notes
        {"nearest_metro_tier": 4},
        {"osm_type": "area"},
        {"sample_reason": "x"},  # extra="forbid" still holds
    ],
)
def test_pilot_field_rules(kw):
    with pytest.raises(ValidationError):
        RegionRow.model_validate(_row(**kw))


def test_status_needs_population():
    kw = {"population": None, "pop_source": None, "pop_year": None, "pop_type": None}
    with pytest.raises(ValidationError):
        RegionRow.model_validate(
            _row(**kw, tag_10k=False, tag_5k=False, pop_source_status="unverified")
        )


def test_new_fields_optional_and_valid():
    r = RegionRow.model_validate(
        _row(
            threshold_50k=True,
            pilot_sample=True,
            notes="sample: far stratum",
            nearest_metro_tier=2,
            road_min_method="pending R1a skims",
            dist_method="haversine",
            osm_type="node",
        )
    )
    assert r.nearest_metro_tier == 2 and r.pilot_sample


# --------------------------------------------------------------------------- merge
def _split_fixture(tmp_path: Path) -> list[Path]:
    df = pd.read_parquet(FIX)
    a, b = tmp_path / "pilot-a.parquet", tmp_path / "pilot-b.parquet"
    df.iloc[:3].to_parquet(a, index=False)
    pd.concat([df.iloc[3:], df.iloc[[0]]]).to_parquet(b, index=False)  # row 0 duplicated
    return [a, b]


def test_merge_dedups_and_stages(tmp_path):
    merged, report = merge_frames(_split_fixture(tmp_path))
    n = len(load_region_register(FIX))
    assert len(merged) == n and report["rows_in"] == n + 1
    assert len(report["duplicates_dropped"]) == 1
    assert merged["row_key"].is_unique and set(merged["funnel_stage"]) == {"all"}
    assert sum(report["rows_per_region"].values()) == n


# --------------------------------------------------------------------------- funnel
def _fixture_cfg(merged: pd.DataFrame) -> dict:
    cfg = yaml.safe_load(WEIGHTS.read_text(encoding="utf-8"))
    cfg = copy.deepcopy(cfg)
    anchor = merged.loc[merged["name_en"] == "Fixture Town 1", "row_key"].item()
    cfg["metros"] = [{"name": "Fixture metro", "tier": 1, "anchors": [anchor]}]
    return cfg


def _run(tmp_path, seed=1, frac=0.25):
    merged, _ = merge_frames(_split_fixture(tmp_path))
    merged["dist_existing_km"] = [15.0, 40.0, 80.0, 120.0, 160.0]  # fixture geometry, fictional
    cfg = _fixture_cfg(merged)
    ll = funnel.long_list(merged, cfg, threshold=10_000, sensitivity=5_000)
    return ll, funnel.run_score(ll, merged, cfg, frac, seed)


def test_long_list_rules(tmp_path):
    ll, _ = _run(tmp_path)
    stage = dict(zip(ll["name_en"], ll["funnel_stage"], strict=True))
    # centres pass whatever their population (rule 2); a non-centre below 10k without a role and
    # excluded by the sweep does not
    assert stage["Fixture Town 3"] == "long" and stage["Fixture Town 5"] == "long"
    assert stage["Fixture Town 4"] == "all"
    assert ll.loc[ll["name_en"] == "Fixture Town 4", "pass_sensitivity"].item() is False


def test_funnel_deterministic(tmp_path):
    _, a = _run(tmp_path, seed=7)
    _, b = _run(tmp_path, seed=7)
    pd.testing.assert_frame_equal(a["table"], b["table"])
    pd.testing.assert_frame_equal(a["sweep"], b["sweep"])
    assert a["summary"] == b["summary"]


def test_sweep_changes_scores_not_order(tmp_path):
    _, res = _run(tmp_path)
    sweep, ranks = res["sweep"], res["ranks"]
    corners = [c for c in sweep.columns if c not in ("row_key", "base")]
    assert len(corners) == 10
    assert any(not sweep[c].equals(sweep["base"]) for c in corners)
    shift = ranks[corners].sub(ranks["base"], axis=0).abs().to_numpy().max()
    assert shift <= RANK_TOLERANCE
    assert 0.0 <= res["summary"]["top_report_stability"] <= 1.0


def test_weights_file_has_no_bare_numbers():
    cfg = yaml.safe_load(WEIGHTS.read_text(encoding="utf-8"))
    assert cfg["approval"] == "pending CP1"

    def walk(node, path=""):
        if isinstance(node, dict):
            if "value" in node:
                assert node.get("assumption_id") or node.get("source"), path
                return
            for k, v in node.items():
                if k == "metros":
                    continue
                walk(v, f"{path}.{k}")
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            raise AssertionError(f"bare number at {path}")

    walk(cfg)
    assert sum(cfg["criteria"][c]["weight"]["value"] for c in funnel.CRITERIA) == pytest.approx(1)


def test_name_normalisers():
    assert norm_ar("محافظة الأحساء") == norm_ar("الاحساء")
    assert norm_en("Al-Qaṭīf") == norm_en("Qatif")


# --------------------------------------------------------------------------- CP1_PREP item 1
def test_administrative_role_does_not_change_any_score(tmp_path):
    merged, _ = merge_frames(_split_fixture(tmp_path))
    merged["dist_existing_km"] = [15.0, 40.0, 80.0, 120.0, 160.0]
    cfg = _fixture_cfg(merged)
    adm = {"role": "administrative", "source": "fixture"}
    with_adm = merged.copy()
    with_adm["economic_roles"] = [[*list(r), adm] for r in merged["economic_roles"]]
    a = funnel.run_score(funnel.long_list(merged, cfg, 10_000, 5_000), merged, cfg, 0.25, 1)
    b = funnel.run_score(funnel.long_list(with_adm, cfg, 10_000, 5_000), with_adm, cfg, 0.25, 1)
    pd.testing.assert_series_equal(a["table"]["score"], b["table"]["score"])
    pd.testing.assert_frame_equal(a["sweep"], b["sweep"])
    assert a["table"]["c_economic_roles"].tolist() == b["table"]["c_economic_roles"].tolist()


def test_rail_gap_log_measure_saturates_at_cap():
    cap = 300.0
    d = pd.Series([0.0, 10.0, 150.0, 300.0, 450.0, 900.0, None])
    g = funnel.gap_measure(d, "log_capped", cap)
    assert g.iloc[0] == 0.0
    assert g.iloc[3] == pytest.approx(1.0) and g.iloc[4] == 1.0 and g.iloc[5] == 1.0
    assert g.iloc[1] < g.iloc[2] < g.iloc[3]
    assert pd.isna(g.iloc[6])
    lin = funnel.gap_measure(d, "linear", cap)
    assert lin.iloc[5] == 1.0 and lin.iloc[4] < 1.0  # the old measure keeps rising past the cap
    with pytest.raises(ValueError):
        funnel.gap_measure(d, "cubic", cap)


def test_duplicate_roles_count_once(tmp_path):
    cfg = yaml.safe_load(WEIGHTS.read_text(encoding="utf-8"))
    roles = [{"role": "port", "source": "a"}, {"role": "port", "source": "b"}]
    roles += [{"role": "administrative", "source": "c"}, {"role": "energy", "source": "d"}]
    assert funnel.scored_roles(roles, cfg) == {"port", "energy"}
