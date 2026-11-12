"""R5 fix: the rail level of service reports the walk and fares the path choice used, so adding a
line never lowers an existing pair's rail utility through a free-in-the-search interchange walk
(explicit `connects_to` links are 0 km) or a faster-but-dearer path."""

from pathlib import Path

import pandas as pd
import pytest

from access import railgraph as rg

SKIMS = Path("runs/access/station-skims")
CAND = Path("cities/ksa/corridors/trunk_gap/S2-trunk_gap-riyadh-jeddah.yaml")


def test_weights_carry_fares() -> None:
    w = rg.weights(rg.load_cfg())
    assert w["fare"] > 0


@pytest.mark.skipif(not CAND.exists(), reason="corridor set not built")
def test_added_line_never_worsens_an_unchanged_path() -> None:
    try:
        od = pd.DataFrame({"o": ["G072-H001", "G091-H001"], "d": ["G089-H003", "G089-H003"]})
        b = rg.rail_los(od, "S1")
        s = rg.rail_los(od, "S1", candidate=CAND)
    except (FileNotFoundError, KeyError) as e:  # station skims are run outputs (gitignored)
        pytest.skip(f"station skims not available: {e}")
    same = b.rail_path == s.rail_path
    assert same.any()
    # transfer walk is booked under access (R4 convention), so compare access + egress
    ae_b = (b.access_min_rail + b.egress_min_rail)[same]
    ae_s = (s.access_min_rail + s.egress_min_rail)[same]
    assert (ae_s <= ae_b + 1e-9).all()
