"""CP2_PREP item 1 (P1a population rule; A-screen-031..033) on tiny in-test frames.

Precedence official > derived > grid, the 30 % corroboration band (0.30 passes, 0.3001 fails),
the RegionRow gate, the long-list gate, and the grid-ratio sensitivity flipping both ways.
All values are fictional fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from common.schemas import GRID_UNCORROBORATED, RegionRow, corroborates
from screening import funnel

FIX = Path(__file__).parent / "fixtures"


# --------------------------------------------------------------------------- band
@pytest.mark.parametrize(
    ("grid", "other", "ok"),
    [
        (10_000, 13_000, True),  # rel diff 0.30 exactly: passes
        (10_000, 7_000, True),  # 0.30 below: passes
        (10_000, 13_001, False),  # 0.3001: fails
        (10_000, 6_999, False),  # 0.3001 below: fails
        (10_000, None, False),  # no second method
        (0, 0, False),  # zero grid cannot be corroborated
    ],
)
def test_band_boundary(grid, other, ok):
    assert corroborates(grid, other) is ok


# --------------------------------------------------------------------------- RegionRow gate
def _row(**kw):
    base = {
        "name_ar": "بلدة اختبار",
        "name_en": "Fixture Town",
        "region": "makkah",
        "governorate": "Fixture",
        "governorate_ar": "محافظة اختبار",
        "is_governorate_centre": False,
        "lat": 21.0,
        "lon": 40.0,
        "population": 20_000,
        "pop_source": "fixture",
        "pop_year": 2020,
        "pop_type": "grid",
        "pop_source_status": "unverified",
        "tag_10k": False,
        "tag_5k": True,
        "screened": True,
        "exclusion_reason": GRID_UNCORROBORATED,
        "fixture": True,
    }
    base.update(kw)
    return base


def test_grid_uncorroborated_row_is_not_tagged():
    r = RegionRow.model_validate(_row())
    assert not r.tag_10k and r.exclusion_reason == GRID_UNCORROBORATED


def test_grid_corroborated_at_boundary_is_tagged():
    r = RegionRow.model_validate(
        _row(
            tag_10k=True,
            exclusion_reason=None,
            pop_corroboration="buildings_x_occupancy",
            pop_corroboration_value=14_000,  # 0.30 of 20,000
        )
    )
    assert r.tag_10k and r.pop_corroboration == "buildings_x_occupancy"


@pytest.mark.parametrize(
    "kw",
    [
        {"tag_10k": True, "exclusion_reason": None},  # uncorroborated grid may not be tagged
        {"exclusion_reason": None},  # gated row needs the reason text
        {"pop_source_status": "secondary"},  # grid must be unverified
        {  # 0.3001 outside the band: tag must stay false
            "tag_10k": True,
            "exclusion_reason": None,
            "pop_corroboration": "ghs_pop_sum",
            "pop_corroboration_value": 26_002,
        },
        {"pop_corroboration": "ghs_pop_sum"},  # method without its value
        {"pop_corroboration": "worldpop", "pop_corroboration_value": 20_000},  # not allowed
    ],
)
def test_grid_gate_rejects(kw):
    with pytest.raises(ValidationError):
        RegionRow.model_validate(_row(**kw))


def test_official_row_unaffected():
    r = RegionRow.model_validate(
        _row(
            pop_type="official",
            pop_source_status="secondary",
            primary_to_find="GASTAT table",
            tag_10k=True,
            exclusion_reason=None,
        )
    )
    assert r.tag_10k
    with pytest.raises(ValidationError):  # corroboration fields are for grid rows only
        RegionRow.model_validate(
            _row(
                pop_type="official",
                pop_source_status="verified",
                tag_10k=True,
                exclusion_reason=None,
                pop_corroboration="viirs_calibrated",
                pop_corroboration_value=20_000,
            )
        )


# --------------------------------------------------------------------------- resolver
def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "row_key": ["off", "der_ok", "der_bad", "grid_ok", "grid_no", "grid_small", "nopop"],
            "pop_type": ["official", "derived", "derived", "grid", "grid", "grid", None],
            "population": [12_000, 11_000, 30_000, 12_000, 25_000, 7_000, None],
            "grid_population": [3_000, 10_000, 10_000, 12_000, 25_000, 7_000, None],
            "pop_corroboration_value": [None, None, None, 15_600, None, 9_000, None],
        }
    )


def test_precedence_and_basis():
    pb = funnel.population_basis(_frame())
    assert pb["population_basis"].tolist() == [
        "official",  # official wins even though the grid disagrees
        "derived_corroborated",  # 11,000 vs grid 10,000: 0.10
        "derived_uncorroborated",  # 30,000 vs 10,000: reported, still counts (A-screen-031)
        "grid_corroborated",  # 15,600 vs 12,000: 0.30 exactly
        "grid_unverified",  # no second method
        "grid_corroborated",  # 9,000 vs 7,000: 0.286, but below 10k anyway
        "none",
    ]
    tags = funnel.tag_10k_rule(_frame()).tolist()
    assert tags == [True, True, True, True, False, False, False]


# --------------------------------------------------------------------------- sensitivity
def test_sensitivity_flips_both_ways():
    df = pd.DataFrame(
        {
            "settlement_id": ["up", "down", "raw_only"],
            "pop_type": ["grid", "grid", "grid"],
            "population": [9_000, 12_000, 8_000],
            # up: 9,000/0.64 = 14,062.5 vs 11,000 -> 0.218, passes (base: below 10k)
            # down: base 12,000 vs 13,000 -> 0.083 passes; sens 18,750 vs 13,000 -> 0.307 fails
            "pop_corroboration_value": [11_000, 13_000, None],
        }
    )
    f = funnel.grid_flips(df, 0.64, "settlement_id").set_index("settlement_id")
    assert f.loc["up", "flip_rule"] == "up"
    assert f.loc["down", "flip_rule"] == "down"
    assert f.loc["raw_only", "flip_rule"] == "" and f.loc["raw_only", "flip_raw"] == "up"
    assert f.loc["down", "flip_raw"] == ""  # already >= 10k raw


def test_base_case_unchanged_without_grid_rows():
    """Ratio 1 is the base case; official rows never move under any ratio."""
    df = _frame().iloc[:3]
    assert funnel.tag_10k_rule(df).tolist() == funnel.tag_10k_rule(df, ratio=0.64).tolist()
    assert funnel.grid_flips(df, 0.64, "row_key").empty


def test_long_list_gate_on_fixture_register():
    cfg = funnel.load_config(funnel.DEFAULT_WEIGHTS)
    reg = pd.read_parquet(FIX / "region_register.parquet")
    i = reg.index[reg["name_en"] == "Fixture Town 2"][0]  # 12,000; not a centre
    roles = reg["economic_roles"].tolist()
    roles[i] = []
    reg["economic_roles"] = roles
    base = funnel.long_list(reg, cfg, 10_000, 5_000)
    g = reg.copy()
    g.loc[i, "pop_type"] = "grid"
    gated = funnel.long_list(g, cfg, 10_000, 5_000)
    assert gated.loc[i, "population_basis"] == "grid_unverified"
    assert GRID_UNCORROBORATED in gated.loc[i, "long_list_reason"]
    assert bool(base.loc[i, "pass_threshold"]) and not bool(gated.loc[i, "pass_threshold"])
    assert bool(gated.loc[i, "pass_sensitivity"])  # the 5k sensitivity is not gated
    others = gated.index != i
    assert (gated.loc[others, "pass_threshold"] == base.loc[others, "pass_threshold"]).all()
    g.loc[i, "pop_corroboration_value"] = 9_000  # 0.25 of 12,000: corroborated
    ok = funnel.long_list(g, cfg, 10_000, 5_000)
    assert ok.loc[i, "population_basis"] == "grid_corroborated" and bool(
        ok.loc[i, "pass_threshold"]
    )


def test_cli_writes_flips_and_meta(tmp_path):
    reg = pd.read_parquet(FIX / "region_register.parquet")
    reg_p = tmp_path / "reg.parquet"
    reg.to_parquet(reg_p, index=False)
    uni = pd.DataFrame(
        {
            "settlement_id": ["a", "b"],
            "name_en": ["Fixture A", "Fixture B"],
            "pop_type": ["grid", "official"],
            "population": [7_000, 9_000],
        }
    )
    uni_p = tmp_path / "uni.parquet"
    uni.to_parquet(uni_p, index=False)
    out = tmp_path / "sens"
    res = CliRunner().invoke(
        funnel.app,
        [
            "sensitivity-grid",
            "--ratio",
            "0.64",
            "--seed",
            "1",
            "--register",
            str(reg_p),
            "--universe",
            str(uni_p),
            "--run-dir",
            str(out),
        ],
    )
    assert res.exit_code == 0, res.output
    flips = pd.read_csv(out / "flips.csv")
    assert flips["row_id"].tolist() == ["a"] and flips["flip_raw"].tolist() == ["up"]
    meta = json.loads((out / "meta.json").read_text())
    assert meta["seed"] == 1 and meta["report_only"] is True
    counts = json.loads((out / "counts.json").read_text())
    assert counts["universe"]["by_basis"]["grid_unverified"] == 1
    assert counts["universe"]["flip_raw_up"] == 1
