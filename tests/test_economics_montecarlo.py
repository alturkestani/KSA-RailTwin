"""R5: Monte Carlo draws are deterministic and share costs.rcf's multipliers (same seed)."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from typer.testing import CliRunner

from costs import estimate
from economics import montecarlo as mc
from economics import params as prm

FIX = Path(__file__).parent / "fixtures"
REAL_REGISTER = Path("cities/ksa/costs/cost_register.yaml")


def test_lognormal_percentiles() -> None:
    rng = np.random.default_rng(1)
    x = mc.lognormal_from_p10_p90(rng, 10.0, 5.0, 20.0, 200_000)
    assert np.percentile(x, 10) == pytest.approx(0.5, rel=0.02)
    assert np.percentile(x, 90) == pytest.approx(2.0, rel=0.02)
    assert mc.lognormal_from_p10_p90(rng, 1.0, 1.0, 1.0, 3).tolist() == [1.0, 1.0, 1.0]


@pytest.fixture(scope="module")
def cost_run(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("cost") / "fixture"
    res = CliRunner().invoke(
        estimate.app,
        ["--corridor", str(FIX / "corridor.yaml"), "--seed", "1", "--draws", "500",
         "--out", str(out)],
    )  # fmt: skip
    assert res.exit_code == 0, res.output
    return out


@pytest.mark.skipif(not REAL_REGISTER.exists(), reason="register not built yet")
def test_shared_draws_equal_costs_rcf(cost_run: Path) -> None:
    rr = mc.ridership_draws(cost_run, FIX / "corridor.yaml", None, 1, 500, Path("/"))
    stored = pd.read_parquet(cost_run / "rcf" / "distribution.parquet")
    assert np.array_equal(rr.capex_multiplier.to_numpy(), stored.capex_multiplier.to_numpy())
    assert np.array_equal(rr.schedule_multiplier.to_numpy(), stored.schedule_multiplier.to_numpy())
    assert (rr.ridership_ratio > 0).all()


@pytest.mark.skipif(not REAL_REGISTER.exists(), reason="register not built yet")
def test_draws_deterministic(cost_run: Path) -> None:
    p = prm.load()
    a = mc.draw_inputs(cost_run, FIX / "corridor.yaml", None, p, 1, 500, Path("/"))
    b = mc.draw_inputs(cost_run, FIX / "corridor.yaml", None, p, 1, 500, Path("/"))
    pd.testing.assert_frame_equal(a, b)
    # another seed would not reproduce the cost run's multipliers: refused, never mixed
    with pytest.raises(RuntimeError, match="shared draws differ"):
        mc.draw_inputs(cost_run, FIX / "corridor.yaml", None, p, 2, 500, Path("/"))
