"""CP2_PREP item 1 addendum 2: primary GASTAT Census 2022 TA1 tables (screening.gastat).

Reads the two committed primary exports and the relayed DataPulse file (small tables under
data/ksa/tables/gastat/, committed with their README); the apply and control-total logic runs on
tiny in-test frames with fictional values.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from common import REPO_ROOT
from screening import gastat
from tests.localdata import needs_local

NATIONAL = 32_175_224  # S-cp2-gastat-007/008 Total rows (= TA9, S-cp2-gastat-003)


# --------------------------------------------------------------------------- readers
def test_primary_tables_sum_to_the_national_total() -> None:
    gov = gastat.read_gov_primary()
    cities, other = gastat.read_city_primary()
    assert len(gov) == 150 and int(gov.total.sum()) == NATIONAL
    assert len(cities) == 271 and other == 3_683_816
    assert int(cities.total.sum()) + other == NATIONAL
    assert (gov.saudi + gov.non_saudi == gov.total).all()


@pytest.mark.skipif(
    not (REPO_ROOT / gastat.CENSUS22).exists(),
    reason="relayed DataPulse table absent (public export drops it; docs/publish)",
)
def test_relayed_file_is_identical_to_the_primary_tables() -> None:
    gx, cx = gastat.primary_vs_relayed()
    assert len(gx) == 150 and gx.relayed_name.notna().all()
    assert (gx[["diff_total", "diff_saudi", "diff_non_saudi"]] == 0).all().all()
    rel = cx.dropna(subset=["relayed_name"])
    assert len(rel) == 60
    assert (rel[["diff_total", "diff_saudi", "diff_non_saudi"]] == 0).all().all()


# --------------------------------------------------------------------------- name keys
@pytest.mark.parametrize(
    ("a", "b"),
    [("Alkhubar", "Al Khubar"), ("Albahah", "Al-Bahah"), ("Alula", "Al `Ula")],
)
def test_key_light_drops_glued_article(a: str, b: str) -> None:
    assert gastat.key_light(a) == gastat.key_light(b)


@pytest.mark.parametrize(
    ("a", "b"),
    [("Bariduh", "Buraydah"), ("Jayzan", "Jazan"), ("Unayzah", "Onaizah"), ("Haqil", "Haql")],
)
def test_key_skeleton_joins_transliteration_variants(a: str, b: str) -> None:
    assert gastat.key_skeleton(a) == gastat.key_skeleton(b)


# --------------------------------------------------------------------------- matching (repo data)
# R9: the crosswalk reads a gitignored pilot capture (absent in a fresh clone); PUBLISH_PREP:
# and the relayed DataPulse table, which the public export drops
need_capture = needs_local(
    "data/ksa/pilot-qassim/raw/citypop_admin.html",
    "data/ksa/tables/gastat/census-2022-20260929.csv",
)


@pytest.fixture(scope="module")
def matches() -> pd.DataFrame:
    cw = gastat.load_crosswalk()
    univ = pd.read_parquet(gastat.UNIVERSE)
    c10 = gastat.cities2010_matched(univ, gastat.governorates_2022(cw), cw)
    return gastat.primary_city_targets(univ, c10, cw)


@need_capture
def test_no_settlement_claimed_twice_except_declared_combinations(matches: pd.DataFrame) -> None:
    m = matches.dropna(subset=["settlement_id"])
    dup = m[m.settlement_id.duplicated(keep=False)]
    assert dup.combined_with.notna().all()
    assert set(dup.city) == {"Alhufuf", "Almubriz"}


@need_capture
def test_crosswalk_and_guards(matches: pd.DataFrame) -> None:
    by = matches.set_index("city")
    assert by.loc["Alshaharin", "settlement_id"] == "KSA-ST-05310"
    assert pd.isna(by.loc["Aljabil", "settlement_id"])  # its figure sat on Ash Shaharin
    # A-screen-038: the skeleton bridge Alsafuh -> Safwa (ratio 0.10) is rejected
    assert pd.isna(by.loc["Alsafuh", "settlement_id"])
    assert "guard" in by.loc["Alsafuh", "reason"]
    assert by.loc["Safwa", "settlement_id"] == "KSA-ST-05170"
    assert matches.settlement_id.isna().sum() + matches.settlement_id.notna().sum() == 271


@need_capture
def test_bridged_matches_respect_the_growth_guard(matches: pd.DataFrame) -> None:
    lo, hi = gastat.GROWTH_GUARD
    b = matches[matches.tier.fillna("").str.startswith("2010")]
    assert len(b) > 0 and b.ratio_2022_2010.between(lo, hi).all()


# --------------------------------------------------------------------------- apply (fictional)
def _universe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "settlement_id": ["S1", "S2", "S3", "S4"],
            "name_en": ["Town A", "Town B", "Village C", "Hamlet D"],
            "region": ["r1", "r1", "r1", "r2"],
            "place": ["town", "town", "village", "hamlet"],
            "lat": [24.0, 24.5, 24.01, 20.0],
            "lon": [46.0, 46.5, 46.01, 42.0],
            "population": [8_000, 30_000, 900, 500],
            "grid_population": [8_000.0, 15_000.0, 900.0, 500.0],
            "pop_year": [2020, 2022, 2020, 2020],
            "pop_type": ["grid", "official", "grid", "grid"],
            "pop_source": ["wp", "S-x", "wp", "wp"],
            "pop_source_status": ["unverified", "secondary", "unverified", "unverified"],
            "pop_method": ["grid"] * 4,
            "pop_licence": ["CC BY"] * 4,
            "pop_quality": ["grid_estimate"] * 4,
            "pop_corroboration": [None] * 4,
            "pop_corroboration_value": [np.nan] * 4,
            "tag_10k": [False, True, False, False],
        }
    )


def test_apply_primary_universe_makes_rows_official_verified() -> None:
    vals = pd.DataFrame({"settlement_id": ["S1"], "primary": [12_000], "cities": ["Town A"]})
    u, log = gastat.apply_primary_universe(_universe(), vals)
    r = u.set_index("settlement_id").loc["S1"]
    assert (r.pop_type, r.pop_source_status, r.pop_source) == (
        "official",
        "verified",
        gastat.MID_CITY_PRIMARY,
    )
    assert r.population == 12_000 and bool(r.tag_10k)  # no corroboration needed
    assert r.population_basis == "official"
    assert log[0]["previous"] == 8_000 and log[0]["primary"] == 12_000


def test_control_total_flags_rows_in_regions_above_their_residual(monkeypatch) -> None:
    ta1 = pd.DataFrame({"region": gastat.REGION_ORDER, "population": [0] * 13})
    ta1.loc[ta1.region == "riyadh", "population"] = 13_000  # residual 1,000 after S1
    ta1.loc[ta1.region == "makkah", "population"] = 10_000
    monkeypatch.setattr(gastat, "read_ta1", lambda: ta1)
    u = _universe().replace({"r1": "riyadh", "r2": "makkah"})
    u.loc[u.settlement_id == "S2", "pop_type"] = "grid"  # 30,000 grid outside the matched city
    vals = pd.DataFrame({"settlement_id": ["S1"], "primary": [12_000], "cities": ["Town A"]})
    reg, flag, summary = gastat.control_total(u, vals, other=1_000)
    r = reg.set_index("region")
    assert r.loc["riyadh", "residual"] == 1_000 and bool(r.loc["riyadh", "exceeds"])
    assert not bool(r.loc["makkah", "exceeds"])  # 500 grid against a 10,000 residual
    f = flag.set_axis(u.settlement_id)
    assert "double counting" in f["S3"]  # 1.4 km from the matched town (radius 3 km)
    assert "over-count" in f["S2"]  # about 74 km away
    assert pd.isna(f["S4"])
    assert summary["grid_exceeds_other"] is True
