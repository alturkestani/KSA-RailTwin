"""Gravity and calibration tests on the 6-zone fixture (tests/fixtures/zones.geojson, invented).

No national data, no network: the fixture zones' populations and centroid distances drive the
doubly-constrained balancing, the origin-constrained branch, the PA->OD symmetrisation, the MNL
mode split and the calibration pass rule.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from demand import calibrate, gravity, supply
from modechoice.coefficients import base_coefficients
from modechoice.mnl import MODES, Settings, shares

FIXTURE = Path(__file__).parent / "fixtures" / "zones.geojson"


def fixture_zones() -> pd.DataFrame:
    g = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = []
    for f in g["features"]:
        ring = np.array(f["geometry"]["coordinates"][0])
        rows.append(
            {
                "zone_id": f["properties"]["zone_id"],
                "population": float(f["properties"]["population"]),
                "lon": ring[:, 0].mean(),
                "lat": ring[:, 1].mean(),
            }
        )
    return pd.DataFrame(rows)


def fixture_od(z: pd.DataFrame) -> pd.DataFrame:
    """All o != d pairs with straight-line km x 1.3 as road km at 80 km/h (test data only)."""
    rows = []
    for i, a in z.iterrows():
        for j, b in z.iterrows():
            if i == j:
                continue
            dlat = math.radians(b.lat - a.lat)
            dlon = math.radians(b.lon - a.lon) * math.cos(math.radians((a.lat + b.lat) / 2))
            km = 6371.0 * math.hypot(dlat, dlon) * 1.3 * 10  # stretched so pairs exceed 40 km
            rows.append(
                {
                    "o": a.zone_id,
                    "d": b.zone_id,
                    "oi": i,
                    "di": j,
                    "road_km": km,
                    "road_min": km / 80 * 60,
                }
            )
    return pd.DataFrame(rows)


def los(od: pd.DataFrame) -> pd.DataFrame:
    x = od.copy()
    x["avail_car"] = True
    x["ivt_min_car"] = x.road_min
    x["cost_sar_car"] = x.road_km * 0.218
    x["avail_bus"] = x.road_km >= 50
    x["ivt_min_bus"] = x.road_min * 1.15
    x["access_min_bus"] = 15.0
    x["egress_min_bus"] = 15.0
    x["headway_min_bus"] = 240.0
    x["cost_sar_bus"] = x.road_km * 0.2
    x["avail_rail"] = x.o.isin(["FZ1", "FZ2"]) & x.d.isin(["FZ1", "FZ2"])
    x["ivt_min_rail"] = x.road_min * 0.6
    x["access_min_rail"] = 20.0
    x["egress_min_rail"] = 20.0
    x["headway_min_rail"] = 60.0
    x["cost_sar_rail"] = x.road_km * 0.3
    x["ontime_rail"] = 95.0
    x["avail_air"] = False
    return x


GEN = {
    "impedance_priors": {
        "functional_form": {"value": {"leisure_vfr": "power", "commute": "exponential"}},
        "leisure_vfr": {"gamma": {"value": 1.9}},
        "commute": {"beta_per_min": {"value": 0.05}},
    }
}


def solve(purpose: str = "leisure_vfr") -> tuple[np.ndarray, np.ndarray, np.ndarray, int, float]:
    z = fixture_zones()
    od = los(fixture_od(z))
    x = od.assign(purpose=purpose)
    ms = shares(x, base_coefficients(), Settings.from_r3())
    c = np.maximum(-ms.logsum.to_numpy() / abs(base_coefficients().ivt["car"]), 1.0)
    f = gravity.impedance_matrix(
        len(z), od.oi.to_numpy(), od.di.to_numpy(), gravity.log_impedance(c, purpose, GEN)
    )
    o = 2.5 * z.population.to_numpy()
    d = z.population.to_numpy() * (o.sum() / z.population.sum())
    t, it, err = gravity.furness(o, d, f, 1e-4, 500)
    return t, o, d, it, err


def test_furness_row_and_column_sums_hold():
    t, o, d, it, err = solve()
    assert err < 1e-4 and it < 500
    np.testing.assert_allclose(t.sum(1), o, rtol=1e-4)
    np.testing.assert_allclose(t.sum(0), d, rtol=1e-4)
    assert np.all(np.diag(t) == 0)  # intrazonal pairs carry no trips


def test_exponential_does_not_underflow():
    c = np.array([2000.0, 2500.0, 3000.0])  # exp(-0.05 c) underflows to 0 without row scaling
    lf = gravity.log_impedance(c, "commute", GEN)
    f = gravity.impedance_matrix(3, np.array([0, 1, 2]), np.array([1, 2, 0]), lf)
    assert np.isclose(f.max(axis=1), 1.0).all()


def test_symmetrisation_keeps_totals_and_balances_directions():
    t, o, *_ = solve()
    s = 0.5 * (t + t.T)
    assert math.isclose(s.sum(), o.sum(), rel_tol=1e-9)
    np.testing.assert_allclose(s, s.T)


def test_gravity_is_deterministic_bit_for_bit():
    def run_bytes() -> str:
        t, *_ = solve()
        buf = io.BytesIO()
        pd.DataFrame(t.round(6)).to_parquet(buf, index=False)
        return hashlib.sha256(buf.getvalue()).hexdigest()

    assert run_bytes() == run_bytes()


def test_mode_shares_sum_to_one_and_unavailable_is_zero():
    z = fixture_zones()
    x = los(fixture_od(z)).assign(purpose="business")
    ms = shares(x, base_coefficients(), Settings.from_r3())
    total = ms[[f"share_{m}" for m in MODES]].sum(axis=1)
    np.testing.assert_allclose(total, 1.0)
    assert (ms.loc[~x.avail_rail, "share_rail"] == 0).all()
    assert (ms.share_air == 0).all()


def test_rail_share_rises_with_rail_constant():
    z = fixture_zones()
    x = los(fixture_od(z)).assign(purpose="leisure_vfr")
    lo = shares(x, gravity.coefficients({"asc.rail": -1.0}), Settings.from_r3())
    hi = shares(x, gravity.coefficients({"asc.rail": 0.5}), Settings.from_r3())
    on = x.avail_rail.to_numpy()
    assert (hi.share_rail.to_numpy()[on] > lo.share_rail.to_numpy()[on]).all()


def test_coefficients_refuse_out_of_range_unless_diagnostic():
    # A-mode-011 range is [-1.0, 1.5] since CP5 decision H2a (3 Nov 2026)
    with pytest.raises(ValueError):
        gravity.coefficients({"asc.air": 1.7})
    c = gravity.coefficients({"asc.air": 1.7}, unbounded=True)
    assert c.asc["air"] == 1.7
    with pytest.raises(KeyError):
        gravity.coefficients({"cost": -0.1}, unbounded=True)


def test_nearest_target_respects_the_access_cap():
    df = pd.DataFrame(
        {
            "zone_id": ["A", "A", "B"],
            "station_uid": ["s1", "s2", "s1"],
            "to_min": [30.0, 10.0, 200.0],
        }
    )
    near = supply._nearest(df, "zone_id", 90.0).set_index("zone_id")
    assert near.loc["A", "station_uid"] == "s2"
    assert "B" not in near.index


def test_calibration_pass_rule_and_geh():
    assert calibrate.geh(365.0, 365.0) == 0.0
    cal = {
        "tolerances": {"A_station": {"low_flow_exempt_below_departures_per_year": 100000}},
        "targets": [
            {
                "id": "t-in",
                "year": 2025,
                "mode": "rail",
                "measure": "passengers",
                "scope": "x",
                "value": 1000.0,
                "evidence_grade": "A",
                "usable": True,
                "tolerance": {"rel": 0.15},
            },
            {
                "id": "t-out",
                "year": 2025,
                "mode": "rail",
                "measure": "passengers",
                "scope": "x",
                "value": 1000.0,
                "evidence_grade": "A",
                "usable": True,
                "tolerance": {"rel": 0.15},
            },
            {
                "id": "t-c",
                "year": 2025,
                "mode": "bus",
                "measure": "passengers",
                "scope": "x",
                "value": 1000.0,
                "evidence_grade": "C",
                "usable": True,
                "tolerance": None,
            },
        ],
    }
    m = {"t-in": 1100.0, "t-out": 1300.0, "t-c": 1000.0, "_air_dep": {}, "_air_arr": {}}
    tab = calibrate.target_rows(cal, m, pd.DataFrame({"node_id": [], "iata": []})).set_index("id")
    assert tab.at["t-in", "status"].startswith("within tolerance")
    assert tab.at["t-out", "status"] == "outside tolerance"
    assert tab.at["t-c", "status"].startswith("available but unverified")
    assert "calibrated" not in set(tab.status)  # only fitted targets may be called calibrated
