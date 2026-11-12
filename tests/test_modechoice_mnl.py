"""MNL car/rail/air/bus on the six-zone fixture (invented test data; no network, < 5 s)."""

from __future__ import annotations

import json
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
import yaml

from modechoice.coefficients import (
    MODES,
    PRIORS_PATH,
    UTILITY_KEYS,
    apply_overrides,
    base_coefficients,
    corner,
    load_priors,
    load_r3,
)
from modechoice.mnl import PURPOSES, Settings, consumer_surplus_change_sar, shares
from modechoice.pairs import build_attributes
from modechoice.sweep import monotonicity, run_sweep, variants

PRIORS = load_priors()
R3 = load_r3()
SETTINGS = Settings.from_r3(R3, PRIORS)


def _fixture_od(fixtures) -> pd.DataFrame:
    """All ordered pairs of the six fixture zones x purposes; fixture road times from centroid
    distance (invented, test only); rail between zones holding a fixture-corridor station."""
    g = json.loads((fixtures / "zones.geojson").read_text(encoding="utf-8"))
    cents = {}
    for f in g["features"]:
        ring = np.asarray(f["geometry"]["coordinates"][0])
        cents[f["properties"]["zone_id"]] = ring[:-1].mean(axis=0)
    line = yaml.safe_load((fixtures / "corridor.yaml").read_text(encoding="utf-8"))
    st_zone = {}
    for s in line["stations"]:
        z = min(cents, key=lambda k: np.hypot(cents[k][0] - s["lon"], cents[k][1] - s["lat"]))
        st_zone[z] = s
    rows = []
    for o in cents:
        for d in cents:
            if o == d:
                continue
            km = float(np.hypot(*(cents[o] - cents[d])) * 111.0 * 1.3)  # fixture only
            for p in PURPOSES:
                r = {"o": o, "d": d, "purpose": p, "road_km": km}
                r.update(
                    avail_car=True,
                    ivt_min_car=km / 1.6,
                    cost_sar_car=km * 0.2,
                    avail_bus=True,
                    ivt_min_bus=km / 1.3,
                    access_min_bus=15,
                    egress_min_bus=15,
                    headway_min_bus=240,
                    cost_sar_bus=km * 0.2,
                )
                if o in st_zone and d in st_zone:
                    dk = abs(st_zone[o]["km_post"] - st_zone[d]["km_post"])
                    r.update(
                        avail_rail=True,
                        ivt_min_rail=dk / 2.0,
                        access_min_rail=20,
                        egress_min_rail=20,
                        headway_min_rail=60,
                        cost_sar_rail=dk * 0.3,
                        ontime_rail=95.0,
                    )
                else:
                    r.update(avail_rail=False)
                r.update(avail_air=False)
                rows.append(r)
    return pd.DataFrame(rows)


@pytest.fixture
def od(fixtures) -> pd.DataFrame:
    return _fixture_od(fixtures)


def test_loader_reads_every_prior_with_an_id() -> None:
    raw = yaml.safe_load(PRIORS_PATH.read_text(encoding="utf-8"))
    n_scalar = len(raw["asc"]) + len(raw["in_vehicle_time"]) + 4 + 5 + len(raw["auxiliary"])
    assert sum(1 for k in PRIORS if not k.startswith("vot.")) == n_scalar
    for k in UTILITY_KEYS:
        p = PRIORS[k]
        assert p.assumption and p.assumption.startswith("A-mode-"), k
        assert p.low <= p.value <= p.high, k
        assert p.status == "literature-based until survey results exist"
    assert PRIORS["ivt.rail"].value == raw["in_vehicle_time"]["rail"]["value"]


def test_shares_sum_to_one_and_unavailable_zero(od) -> None:
    res = shares(od, base_coefficients(PRIORS), SETTINGS)
    p = res[[f"share_{m}" for m in MODES]].to_numpy()
    assert np.allclose(p.sum(axis=1), 1.0)
    assert (res.loc[~res["avail_rail"], "share_rail"] == 0).all()
    assert (res["share_air"] == 0).all()
    assert res["logsum"].notna().all()


def test_only_one_available_gets_everything(od) -> None:
    one = od.copy()
    one["avail_bus"] = False
    one["avail_rail"] = False
    res = shares(one, base_coefficients(PRIORS), SETTINGS)
    assert np.allclose(res["share_car"], 1.0)
    none = one.copy()
    none["avail_car"] = False
    res = shares(none, base_coefficients(PRIORS), SETTINGS)
    assert np.allclose(res[[f"share_{m}" for m in MODES]].to_numpy(), 0.0)
    assert res["logsum"].isna().all() and not res["any_avail"].any()


def test_numerically_stable_for_huge_utilities(od) -> None:
    big = od.copy()
    big["ivt_min_car"] = 1e6
    res = shares(big, base_coefficients(PRIORS), SETTINGS)
    assert np.isfinite(res["share_car"]).all() and np.isfinite(res["logsum"]).all()


def _rail(od, coefs, settings=SETTINGS) -> np.ndarray:
    r = shares(od[od["avail_rail"]].reset_index(drop=True), coefs, settings)
    return r["share_rail"].to_numpy()


def test_monotonic_responses(od) -> None:
    base = _rail(od, base_coefficients(PRIORS))
    assert (_rail(od, corner(PRIORS, {"ivt.rail": "low"})) < base).all()  # more negative
    assert (_rail(od, corner(PRIORS, {"asc.rail": "high"})) > base).all()
    assert (_rail(od, corner(PRIORS, {"headway": "low"})) < base).all()
    assert (_rail(od, corner(PRIORS, {"access_egress": "low"})) < base).all()
    assert (_rail(od, corner(PRIORS, {"ivt.car": "low"})) > base).all()
    # cost more negative: rail share falls where rail is dearer than every other available mode
    sub = od[od["avail_rail"]].reset_index(drop=True)
    dear = (sub["cost_sar_rail"] > sub["cost_sar_car"] / SETTINGS.car_occupancy) & (
        sub["cost_sar_rail"] > sub["cost_sar_bus"]
    )
    low = _rail(od, corner(PRIORS, {"cost": "low"}))
    assert dear.any() and (low[dear] < base[dear]).all()
    # summer penalty on access/egress lowers rail
    assert (_rail(od, base_coefficients(PRIORS), replace(SETTINGS, season="summer")) < base).all()


def test_sweep_monotonicity_has_no_fail(od) -> None:
    m = monotonicity(od, PRIORS, SETTINGS)
    assert len(m) and (m["status"] != "FAIL").all()


def test_deterministic(od) -> None:
    a = shares(od, base_coefficients(PRIORS), SETTINGS)
    b = shares(od.copy(), base_coefficients(PRIORS), SETTINGS)
    pd.testing.assert_frame_equal(a, b)
    vs = variants(PRIORS, R3, SETTINGS)
    t = od.assign(pair_id=od["o"] + "-" + od["d"], pair_name="fx", scenario="FX")
    pd.testing.assert_frame_equal(run_sweep(t, vs), run_sweep(t, vs))


def test_logsum_rises_when_a_mode_improves(od) -> None:
    c = base_coefficients(PRIORS)
    a = shares(od, c, SETTINGS)
    better = od.copy()
    better["ivt_min_rail"] = better["ivt_min_rail"] * 0.8
    b = shares(better, c, SETTINGS)
    rail = od["avail_rail"].to_numpy()
    assert (b["logsum"].to_numpy()[rail] > a["logsum"].to_numpy()[rail]).all()
    assert np.allclose(b["logsum"].to_numpy()[~rail], a["logsum"].to_numpy()[~rail])
    cs = consumer_surplus_change_sar(a["logsum"], b["logsum"], a["b_cost_eff"])
    assert (cs[rail] > 0).all()


def test_purpose_scaling_business_less_fare_sensitive(od) -> None:
    res = shares(od, base_coefficients(PRIORS), SETTINGS)
    bc = res.groupby("purpose")["b_cost_eff"].first()
    assert bc["business"] > bc["commute"] > bc["leisure_vfr"]  # less negative
    assert bc["leisure_vfr"] == pytest.approx(PRIORS["cost"].value)


def test_apply_overrides_refuses_out_of_range() -> None:
    c = base_coefficients(PRIORS)
    c2 = apply_overrides(c, {"asc.rail": -0.5}, PRIORS)
    assert c2.asc["rail"] == -0.5 and c2.asc["car"] == 0.0
    with pytest.raises(ValueError):
        apply_overrides(c, {"asc.rail": 0.9}, PRIORS)
    with pytest.raises(KeyError):
        apply_overrides(c, {"asc.car": 0.1}, PRIORS)


def test_build_attributes_on_synthetic_skims() -> None:
    skims = pd.DataFrame(
        {
            "o": ["G138", "G038", "G138"],
            "d": ["G038", "G138", "G138"],
            "road_km": [400.0, 400.0, 0.0],
            "road_min": [240.0, 240.0, 0.0],
        }
    )
    points = {"G138": (46.7, 24.6), "G038": (50.1, 26.4)}
    spec = R3["representative_pairs"][0]["rail"]["S0"]
    od = pd.DataFrame({"o": ["G138"], "d": ["G038"], "purpose": ["leisure_vfr"]})
    t = build_attributes(od, R3, skims, points, "S0", {("G138", "G038"): spec})
    assert bool(t["avail_rail"].iloc[0]) and bool(t["avail_air"].iloc[0])
    assert t["cost_sar_rail"].iloc[0] == spec["fare_sar"]
    res = shares(t, base_coefficients(PRIORS), SETTINGS)
    assert res[[f"share_{m}" for m in MODES]].sum(axis=1).iloc[0] == pytest.approx(1.0)
