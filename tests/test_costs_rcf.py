"""R1c: reference-class uplift sampling (fixture uplifts; values invented for tests)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from common.schemas import UpliftSpec, load_uplifts
from costs import rcf

REAL_UPLIFTS = Path(__file__).resolve().parents[1] / "cities" / "ksa" / "costs" / "uplifts.yaml"


def _u(**kw: object) -> UpliftSpec:
    base = {
        "id": "U-capex-rail-fixture",
        "applies_to": "capex",
        "line_type": "rail",
        "stage": "n/a",
        "distribution": "empirical",
        "params": {"percentiles": {50: 1.2, 80: 1.5, 90: 1.8}},
        "source": "S-fixture",
        "status": "sourced",
        "assumption_id": "A-rcf-fixture",
    }
    return UpliftSpec.model_validate({**base, **kw})


def test_empirical_reproduces_printed_percentiles() -> None:
    x = rcf.draw(_u(), np.random.default_rng(1), 200_000)
    assert np.percentile(x, 50) == pytest.approx(1.2, rel=0.01)
    assert np.percentile(x, 80) == pytest.approx(1.5, rel=0.01)
    assert np.percentile(x, 90) == pytest.approx(1.8, rel=0.01)
    assert np.percentile(x, 10) <= 1.2 and x.min() > 0


def test_lognormal_normal_triangular() -> None:
    g = np.random.default_rng(2)
    ln = rcf.draw(
        _u(distribution="lognormal", params={"median_ratio": 1.1, "p80_ratio": 1.4}), g, 200_000
    )
    assert np.percentile(ln, 50) == pytest.approx(1.1, rel=0.01)
    assert np.percentile(ln, 80) == pytest.approx(1.4, rel=0.01)
    nm = rcf.draw(
        _u(distribution="normal", params={"mean_ratio": 1.45, "sd": 0.38, "floor": 0.5}),
        g,
        50_000,
    )
    assert nm.min() >= 0.5
    tr = rcf.draw(
        _u(distribution="triangular", params={"low": 0.9, "mode": 1.0, "high": 1.6}), g, 1000
    )
    assert tr.min() >= 0.9 and tr.max() <= 1.6


def test_schema_rejects_bare_numbers() -> None:
    with pytest.raises(ValueError):
        _u(assumption_id=None)
    with pytest.raises(ValueError):
        _u(source="assumed")  # sourced needs an S- id
    with pytest.raises(ValueError):
        _u(distribution="normal", params={"mean_ratio": 1.4})


def test_select_precedence() -> None:
    ups = [
        _u(id="U-capex-all", line_type="all"),
        _u(id="U-capex-rail-obc", stage="outline_business_case"),
        _u(id="U-capex-hsr-obc", line_type="hsr", stage="outline_business_case"),
    ]
    assert rcf.select(ups, "capex", "hsr", "outline_business_case").id == "U-capex-hsr-obc"
    assert rcf.select(ups, "capex", "mixed", "outline_business_case").id == "U-capex-rail-obc"
    assert rcf.select(ups, "capex", "mixed", "strategic").id == "U-capex-all"
    with pytest.raises(KeyError):
        rcf.select(ups, "ridership", "hsr", "strategic")
    rid = _u(id="U-ridership-rail-fbc", applies_to="ridership", stage="full_business_case")
    sens = _u(id="U-capex-hsr-sens", line_type="hsr", stage="strategic", role="sensitivity")
    ups += [rid, sens]
    assert rcf.select(ups, "ridership", "hsr", "strategic").id == "U-ridership-rail-fbc"
    assert rcf.select(ups, "capex", "hsr", "strategic").id == "U-capex-all"  # sensitivity skipped
    assert rcf.select(ups, "capex", "hsr", "strategic", "U-capex-hsr-sens").id == "U-capex-hsr-sens"


def test_apply_is_deterministic() -> None:
    ups = [
        _u(),
        _u(
            id="U-schedule-fixture",
            applies_to="schedule",
            params={"percentiles": {50: 1.1, 90: 1.5}},
        ),
    ]
    base = {
        "line_type": "conventional_passenger",
        "stage": "strategic",
        "capex": {"low": 80, "central": 100, "high": 150},
        "schedule_years": {"low": 4, "central": 5, "high": 7},
    }
    a, da = rcf.apply(base, ups, seed=1, draws=2000)
    b, db = rcf.apply(base, ups, seed=1, draws=2000)
    c, _ = rcf.apply(base, ups, seed=2, draws=2000)
    assert a == b and da.equals(db)
    assert a["capex"]["uplifted"] != c["capex"]["uplifted"]
    q = a["capex"]["uplifted"]
    assert q["P10"] <= q["P50"] <= q["P80"] <= q["P90"]
    assert a["schedule"]["overrun_months"]["P50"] > 0


@pytest.mark.skipif(not REAL_UPLIFTS.exists(), reason="uplifts not built yet")
def test_real_uplifts_load_and_cover_three_kinds() -> None:
    ups = load_uplifts(REAL_UPLIFTS)
    kinds = {u.applies_to for u in ups}
    assert kinds == {"capex", "schedule", "ridership"}
    assert all(u.assumption_id.startswith("A-rcf-") for u in ups)
