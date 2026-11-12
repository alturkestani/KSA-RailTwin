"""R7 fiscal-exposure arithmetic on a fictional fixture basis (CBA-fixture-corridor numbers are
invented; never cite them). Runs in well under a second; needs no runs/ directory."""

from __future__ import annotations

import math

import numpy as np
import pytest

from funding import fiscal

POPS = fiscal.POPS


def fixture_basis(phase: int = 2030) -> fiscal.Basis:
    """FIXTURE: invented values shaped like a judge score.json (capex P90/P50 = 3)."""
    row = {
        "fiscal_cost_p50": 900.0,
        "pvc_p10": 500.0,
        "pvc_p50": 800.0,
        "pvc_p90": 2000.0,
        "pv_capex_p50": 700.0,
        "pv_opex_renewals_p50": 300.0,
        "pv_residual_p50": 100.0,
        "pv_fare_revenue_p50": 100.0,
        "bcr_p10": 0.8,
        "npv_at_p90_cost": -500.0,
    }
    rows = {(p, 60): dict(row) for p in POPS}
    return fiscal.Basis(
        entity="CBA-fixture-corridor",
        kind="corridor",
        score_path="tests/fixture",
        judge="fixture",
        capex={"p10": 500.0, "p50": 1000.0, "p90": 3000.0, "base_p50": 800.0},
        rows=rows,
        bcr_p10={p: 0.8 for p in POPS},
        npv_at_p90_cost={p: -500.0 for p in POPS},
        robust_npv=100.0,
        parts=[fiscal.Part("CBA-fixture-corridor", phase, 1, 1, 1, 1)],
    )


@pytest.fixture(scope="module")
def params():
    return fiscal.load_params()


@pytest.fixture(scope="module")
def st(params):
    return fiscal.settings(params)


def test_params_all_sourced_or_assumed(params):
    for k, v in params["params"].items():
        assert "id" in v and ({"source", "assumption"} & set(v)), k


def test_public_flows_capex_profile_and_annuities(st):
    b = fixture_basis()
    fl = fiscal.flows(b, st, "public", "un_wpp_low", 60, "p50")
    build = (fl.yrs >= 2027) & (fl.yrs <= 2029)
    assert np.allclose(fl.capex[build], 1000.0 / 3)
    assert fl.capex[~build].sum() == 0
    # level annual equivalents reproduce the 60-year PVs exactly
    assert fiscal.pv(fl.opex, st, fl.yrs) == pytest.approx(300.0)
    assert fiscal.pv(fl.fares, st, fl.yrs) == pytest.approx(100.0)
    total = fiscal.pv(fl.total(), st, fl.yrs)
    df = fiscal.dfs(st, int(fl.yrs[-1]))
    assert total == pytest.approx(sum(1000 / 3 * df[y - 2026] for y in (2027, 2028, 2029)) + 200)


def test_availability_payment_annuity(params):
    st = fiscal.settings(params, bid_contingency=0.25, public_contribution_availability=0.0)
    b = fixture_basis()
    fl = fiscal.flows(b, st, "availability", "un_wpp_low", 60, "p50")
    r = st.c["sovereign_real_rate"] + st.c["private_finance_premium"]
    kc = 800.0 * 1.25
    fin = sum(kc / 3 * (1 + r) ** k for k in (3, 2, 1))
    ann = fin * r / (1 - (1 + r) ** -30)
    o = fl.ap[fl.yrs == 2030][0] - ann
    assert o == pytest.approx(fl.opex[fl.yrs == 2060][0])  # pass-through, then public after term
    assert (fl.ap > 0).sum() == 30
    assert fl.capex.sum() == 0  # no public contribution in this case
    assert fl.txn.sum() == pytest.approx(st.c["transaction_cost"] * kc)
    # P50 capex (1000) is below the cushion kc * (1 + a): no contingent payment
    assert fl.contingent.sum() == 0
    f90 = fiscal.flows(b, st, "availability", "un_wpp_low", 60, "p90")
    assert f90.contingent.sum() == pytest.approx(3000 - kc * (1 + st.c["absorption_capacity"]))


def test_demand_concession_grant_and_mrg(st):
    b = fixture_basis()
    fl = fiscal.flows(b, st, "demand_concession", "un_wpp_low", 60, "p50")
    assert fl.grant.sum() > 0
    in_term = (fl.yrs >= 2030) & (fl.yrs <= 2059)
    assert fl.fares[in_term].sum() == 0 and fl.opex[in_term].sum() == 0  # private in the term
    # worst demand at the 'p90' slot: the ratio's P10 (0.25) against the 0.70 guarantee
    f90 = fiscal.flows(b, st, "demand_concession", "un_wpp_low", 60, "p90")
    f_annual = fl.fares[fl.yrs == 2061][0]
    mrg = st.c["mrg_level"] - 0.25
    overrun = 3000 - 800 * (1 + st.c["bid_contingency"]) * (1 + st.c["absorption_capacity"])
    assert f90.contingent[f90.yrs == 2031][0] == pytest.approx(mrg * f_annual)
    assert f90.contingent[f90.yrs == 2030][0] == pytest.approx(mrg * f_annual + overrun)


def test_lognormal_tail_matches_monte_carlo():
    k50, k90 = 1000.0, 3000.0
    mu, s = fiscal.lognormal_fit(k50, k90)
    x = np.random.default_rng(1).lognormal(mu, s, 400_000)
    assert np.quantile(x, 0.9) == pytest.approx(k90, rel=0.02)
    assert fiscal.ln_mean(k50, k90) == pytest.approx(x.mean(), rel=0.02)
    for cap in (800.0, 1500.0, 4000.0):
        assert fiscal.ln_excess(k50, k90, cap) == pytest.approx(
            np.maximum(0, x - cap).mean(), rel=0.03
        )


def test_expected_shortfall_reference_class():
    probs, vals = fiscal.ridership_ratio_table()
    assert vals[list(probs).index(0.5)] == pytest.approx(0.70)  # A-rcf-029 median
    assert fiscal.expected_shortfall(0.0, probs, vals) == 0
    e = fiscal.expected_shortfall(0.7, probs, vals)
    assert 0 < e < 0.7
    assert fiscal.shortfall_at(0.7, probs, vals, 0.1) == pytest.approx(0.45)


def test_budget_reference_deflated(st):
    yrs = np.array([2026, 2028, 2029])
    e = fiscal.budget_real(st, yrs)
    assert e[0] == pytest.approx(1313e3 / 1.0204)
    assert e[1] == pytest.approx(1419e3 / 1.0204**3)
    assert e[2] == pytest.approx(1419e3 * (1 + st.c["budget_growth_nominal"]) / 1.0204**4)


def test_exposure_ranges_ordered_and_complete(st):
    b = fixture_basis()
    for model, kind in (
        ("fully_public_sar", "public"),
        ("ppp_dbfom_availability", "availability"),
        ("ppp_dbfom_demand_risk", "demand_concession"),
        ("lvc_station_area_development", "public_plus_lvc"),
    ):
        ex = fiscal.exposure(b, st, model, kind)
        for p in POPS:
            r = ex["by_pop"][p]
            for h in fiscal.HORIZONS:
                n = r[f"net_fiscal_cost_{h}y"]
                assert n["p10"] <= n["p50"] <= n["p90"]
                assert math.isfinite(n["expected"])
            assert set(r) >= {
                "upfront_public_capex",
                "budget_share",
                "contingent_liabilities",
                "timing_p50_5y",
            }
        if kind.endswith("_lvc"):
            # break-even LVC value = the 60-year P50 net fiscal cost of the base model
            n60 = ex["by_pop"]["un_wpp_low"]["net_fiscal_cost_60y"]["p50"]
            assert ex["lvc_break_even_pv"] == n60
    # with every horizon in the score (a layout), the series is the judge's own fiscal cost
    full = fixture_basis()
    full.rows = {(p, h): dict(full.rows[(p, 60)]) for p in POPS for h in fiscal.HORIZONS}
    ex = fiscal.exposure(full, st, "fully_public_sar", "public")
    assert ex["by_pop"]["un_wpp_low"]["net_fiscal_cost_60y"]["p50"] == 900.0


def test_one_method_per_horizon_series(st):
    """verify-R7 F2: a score with only the 60-year row gets every horizon from the engine, so the
    series differs between horizons by exactly the PV of the extra operating years' net flows."""
    b = fixture_basis()
    ex = fiscal.exposure(b, st, "fully_public_sar", "public")["by_pop"]["un_wpp_low"]
    fl60 = fiscal.flows(b, st, "public", "un_wpp_low", 60, "p50")
    net = fl60.opex - fl60.fares
    df = fiscal.dfs(st, int(fl60.yrs[-1]))
    for h in (30, 40):
        extra = (fl60.yrs >= 2030 + h) & (fl60.yrs <= 2089)
        gap = float(np.dot(net[extra], df[extra]))
        n_h, n60 = ex[f"net_fiscal_cost_{h}y"]["p50"], ex["net_fiscal_cost_60y"]["p50"]
        assert n60 - n_h == pytest.approx(gap)
        assert n60 > n_h  # opex above fares in the fixture: a longer horizon costs more
