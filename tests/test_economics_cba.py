"""R5: the appraisal engine on an invented context (fixture CBA case; every number is made up):
BCR identities, determinism and the switching-value solver."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from economics import cba, switching
from economics import params as prm

FIX = Path(__file__).parent / "fixtures"
COLS = {
    "user_min_commute": 2e6,
    "user_min_business": 2e6,
    "user_min_leisure_vfr": 4e6,
    "user_min_tourism": 1e6,
    "user_min_pilgrimage": 1e6,
    "car_trips_diverted": 1e5,
    "car_vkm_interurban": -2e7,
    "car_vkm_jeddah_urban": 0.0,
    "car_pkm_diverted_min": 1e7,
    "bus_vkm": -1e5,
    "air_pkm": -1e7,
    "rail_pkm": 3e7,
    "rail_trips": 2e5,
    "revenue_sar": 2e7,
    "trips_total": 1e8,
    "wei_job_weighted_dlnED": 50.0,
}


def ctx(scale: float = 1.0) -> cba.Context:
    case = cba.load_case(FIX / "cba_case.yaml")
    rows = [
        {"case": case.id, "population": "un_wpp_medium_gastat2024", "year": 2025}
        | {k: v * scale for k, v in COLS.items()},
        {"case": case.id, "population": "un_wpp_medium", "year": 2050}
        | {k: 1.2 * v * scale for k, v in COLS.items()},
    ]
    return cba.Context(
        case=case,
        p=prm.load(),
        scalars=pd.DataFrame(rows),
        cost={},
        class_share={"civil": 0.6, "track": 0.4},
        train_km_yr=1e5,
        electric=True,
        line_type="conventional_passenger",
    )


def draws(n: int = 3) -> pd.DataFrame:
    d = pd.DataFrame(
        {
            "draw": np.arange(n),
            "capex": np.linspace(800, 1200, n),
            "capex_base": np.full(n, 900.0),
            "capex_multiplier": np.linspace(800, 1200, n) / 900,
            "construction_years": np.full(n, 5.0),
            "opex": np.full(n, 20.0),
            "renewals_30y": np.full(n, 100.0),
            "renewals_40y": np.full(n, 150.0),
            "renewals_60y": np.full(n, 250.0),
            "ridership_ratio": np.ones(n),
        }
    )
    for c in ("vot_mult", "carbon_mult", "crash_mult", "aq_mult", "mec_mult", "wei_mult"):
        d[c] = 1.0
    d["rate_shift"] = 0.0
    return d


def test_bcr_npv_identities() -> None:
    r = cba.evaluate(ctx(), draws(), "un_wpp_medium", [60], ["greenbook_2026"])[
        (60, "greenbook_2026")
    ]
    assert np.allclose(r["npv"], r["pvb"] - r["pvc"])
    assert np.allclose(r["bcr"], r["pvb"] / r["pvc"])
    assert np.all(r["bcr_wei"] >= r["bcr"])  # WEIs only ever added in the separate BCR
    assert np.all(np.diff(r["npv"]) < 0)  # more capex, lower NPV
    assert np.allclose(r["opening_year"], 2027 + 5)


def test_demand_driven_streams_scale_with_demand() -> None:
    kw = {"detail": True}
    a = cba.evaluate(ctx(1.0), draws(1), "un_wpp_medium", [40], ["flat_5"], **kw)[(40, "flat_5")]
    b = cba.evaluate(ctx(2.0), draws(1), "un_wpp_medium", [40], ["flat_5"], **kw)[(40, "flat_5")]
    for k in ("pv_user_time_cost", "pv_fare_revenue", "pv_decongestion_interurban"):
        assert b[k][0] == pytest.approx(2 * a[k][0], rel=1e-9)
    assert a["pv_reliability"][0] == 0.0  # sensitivity only (A-cba-109/112)
    assert a["pv_freight_shift"][0] == 0.0  # not monetised (A-cba-309)


def test_switching_value_solver_converges() -> None:
    c = ctx()
    central = cba.central_row(draws(5))
    sv = switching.switching_values(c, central)
    k = sv["demand_share_of_model_forecast"]["value"]
    assert k is not None
    row = central.copy()
    row["ridership_ratio"] = k
    _, bcr = switching._npv_bcr(c, row)
    assert bcr == pytest.approx(1.0, abs=1e-6)
    r = sv["discount_rate_npv_zero"]["value"]
    if r is not None:
        npv, _ = switching._npv_bcr(c, central, rc=f"const:{r}")
        assert abs(npv) < 1e-3 * abs(switching._npv_bcr(c, central)[0]) + 1e-6


def test_residual_fraction() -> None:
    lives = {"civil": 100, "track": 40}
    assert cba.residual_fraction(60, {"civil": 1.0}, lives) == pytest.approx(0.4)
    assert cba.residual_fraction(40, {"track": 1.0}, lives) == pytest.approx(0.0)
    assert cba.residual_fraction(30, {"track": 1.0}, lives) == pytest.approx(0.25)


def test_fixture_case_validates() -> None:
    case = cba.load_case(FIX / "cba_case.yaml")
    assert case.baseline != case.scenario and case.population_scenarios == []
